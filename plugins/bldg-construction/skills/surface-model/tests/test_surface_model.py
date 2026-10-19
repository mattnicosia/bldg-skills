"""
Tests for the six gaps found on the Yaun Road job (LA-2851). Stdlib only:

  python3 -I -m unittest discover -s plugins/bldg-construction/skills/surface-model/tests
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
MASSING = os.path.join(HERE, "..", "..", "drawings-to-massing", "scripts", "massing_from_surfaces.py")
sys.path.insert(0, SCRIPTS)

import build as B  # noqa: E402
import export as X  # noqa: E402
import pins as P  # noqa: E402
import report as R  # noqa: E402
import revise as V  # noqa: E402
import sm  # noqa: E402
import store as S  # noqa: E402

PERSON = {"kind": "person", "id": "matt"}


def room(handle, x, y_top, w, h, name=None, level="L1", **extra):
    e = {"level": level, "handle": handle, "name": name or handle, "anchor": [x, y_top], "edges": [
        {"heading": "E", "length": w, "source": "A-101"}, {"heading": "S", "length": h, "source": "A-101"},
        {"heading": "W", "length": w, "source": "A-101"}, {"heading": "N", "length": h, "source": "A-101"}]}
    e.update(extra)
    return e


def readings(spaces, roofs=(), rev="R1", level_el=0):
    return {"job": "T1", "revision": {"id": rev}, "wallTolFt": 1.0,
            "levels": [{"id": "L1", "elevationFt": {"value": level_el, "source": "A-301"}, "ceilingFt": {"value": 9, "source": "A-301"}},
                       {"id": "RF", "elevationFt": {"value": 20, "source": "A-301"}}],
            "spaces": list(spaces), "roofs": list(roofs)}


def model_at(r1, accept_pairs=False):
    m = S.new_model("T1")
    res = B.first_build(m, r1, "R1", PERSON if accept_pairs else None)
    assert res["ok"], res
    return m


def reissue(m, r2, rev="R2", accept_all=True, pairs=True):
    prop = V.propose(m, r2, rev)
    assert prop["ok"], prop.get("holds")
    res = V.accept(m, prop, PERSON, accept_all, PERSON if pairs else None)
    assert res["ok"], res
    return prop, res


def run_cli(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = sm.main(list(argv))
    return code, buf.getvalue()


class MergeProposal(unittest.TestCase):
    def test_laundry_folding_into_a_bigger_mud_room_is_one_merge(self):
        m = model_at(readings([room("MUD-ROOM", 0, 10, 10, 10), room("LAUNDRY", 10, 10, 5, 10)]))
        r2 = readings([room("MUD-ROOM", 0, 10, 15, 10)], rev="R2")
        prop = V.propose(m, r2, "R2")
        kinds = sorted(e["kind"] for e in prop["events"])
        self.assertEqual(kinds, ["merge"])
        merge = prop["events"][0]
        self.assertEqual(sorted(merge["addresses"]), ["L1/LAUNDRY", "L1/MUD-ROOM"])
        self.assertEqual(merge["decision"], "needs_person")

    def test_accept_retires_both_and_keeps_the_pins(self):
        m = model_at(readings([room("MUD-ROOM", 0, 10, 10, 10), room("LAUNDRY", 10, 10, 5, 10)]))
        P.pin(m, "L1/LAUNDRY", "note", "n1", PERSON)
        _, res = reissue(m, readings([room("MUD-ROOM", 0, 10, 15, 10)], rev="R2"))
        spaces = lambda kind: [e for e in m["lineage"] if e["kind"] == kind and str(e["from"]).startswith(("sp", "['sp"))]  # noqa: E731
        self.assertEqual(len(spaces("merge")), 1)
        self.assertEqual(len(spaces("retire")), 0)
        self.assertEqual(len(m["pins"]), 1)
        self.assertEqual(P.status(m, m["pins"][0], "R2")["status"], "merged")

    def test_a_plain_carry_stays_a_carry(self):
        m = model_at(readings([room("MUD-ROOM", 0, 10, 10, 10)]))
        prop = V.propose(m, readings([room("MUD-ROOM", 0, 10, 10.2, 10)], rev="R2"), "R2")
        self.assertEqual([e["kind"] for e in prop["events"]], ["carry"])


class PinCommands(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "m.json")
        m = model_at(readings([room("KITCHEN", 0, 10, 10, 10), room("PANTRY", 10, 10, 5, 10)]))
        P.pin(m, "L1/KITCHEN/FLR", "estimate", "09 64 00", PERSON)
        S.save(m, self.path)

    def pin(self):
        return S.load(self.path)["pins"][0]

    def test_accept(self):
        run_cli("pin-accept", self.path, "pin_1", "--by", "matt")
        p = self.pin()
        self.assertEqual(p["state"], "accepted")
        self.assertEqual(p["acceptedBy"], PERSON)
        self.assertIn("acceptedAt", p)

    def test_move_writes_every_field_and_touches_reports_moved(self):
        run_cli("pin-move", self.path, "pin_1", "--to", "L1/PANTRY/FLR", "--by", "matt")
        p = self.pin()
        self.assertEqual((p["state"], p["movedTo"], p["movedBy"], p["movedRev"]), ("moved", "L1/PANTRY/FLR", PERSON, "R1"))
        self.assertIn("movedAt", p)
        m = S.load(self.path)
        key = S.key_for_address(m, "L1/KITCHEN/FLR", "R1")
        self.assertEqual(P.what_touches(m, key, "R1")[0]["status"]["status"], "moved")
        pantry = S.key_for_address(m, "L1/PANTRY/FLR", "R1")
        self.assertEqual(len(P.what_touches(m, pantry, "R1")), 1)
        self.assertEqual(P.review_queue(m, "R1"), [])

    def test_withdraw_leaves_review(self):
        run_cli("pin-withdraw", self.path, "pin_1", "--by", "matt")
        m = S.load(self.path)
        self.assertEqual(m["pins"][0]["state"], "withdrawn")
        self.assertEqual(P.status(m, m["pins"][0], "R1")["status"], "withdrawn")

    def test_unknown_pin_and_bad_target_refuse(self):
        with self.assertRaises(SystemExit):
            run_cli("pin-accept", self.path, "pin_9", "--by", "matt")
        with self.assertRaises(SystemExit):
            run_cli("pin-move", self.path, "pin_1", "--to", "L1/NOPE/FLR", "--by", "matt")


class RenamedSpace(unittest.TestCase):
    def test_same_outline_new_name_goes_to_review(self):
        m = model_at(readings([room("BATH-B", 0, 10, 8, 8, name="BATH"), room("DEN", 30, 10, 8, 8)], level_el=0))
        P.pin(m, "L1/BATH-B/FLR", "estimate", "09 30 00", PERSON)
        reissue(m, readings([room("KITCHEN-B", 0, 10, 8, 8, name="KITCHEN"), room("DEN", 30, 10, 8, 8)], rev="R2"))
        p = m["pins"][0]
        st = P.status(m, p, "R2")
        self.assertEqual(st["status"], "renamed")
        self.assertEqual(len(P.review_queue(m, "R2")), 1)
        self.assertIn("renamed BATH to KITCHEN", R.revision_report(m, "R2"))

    def test_a_renumber_alone_is_not_flagged(self):
        m = model_at(readings([room("X", 0, 10, 8, 8, name="BATH", number="101"), room("DEN", 30, 10, 8, 8)]))
        P.pin(m, "L1/101/FLR", "estimate", "09 30 00", PERSON)
        reissue(m, readings([room("X", 0, 10, 8, 8, name="BATH", number="201"), room("DEN", 30, 10, 8, 8)], rev="R2"))
        self.assertEqual(P.status(m, m["pins"][0], "R2")["status"], "readdressed")
        self.assertEqual(P.review_queue(m, "R2"), [])

    def test_accepting_at_the_new_revision_clears_the_flag(self):
        m = model_at(readings([room("BATH-B", 0, 10, 8, 8, name="BATH"), room("DEN", 30, 10, 8, 8)]))
        P.pin(m, "L1/BATH-B/FLR", "estimate", "09 30 00", PERSON)
        reissue(m, readings([room("KITCHEN-B", 0, 10, 8, 8, name="KITCHEN"), room("DEN", 30, 10, 8, 8)], rev="R2"))
        P.decide(m, "pin_1", "accept", PERSON)
        self.assertEqual(P.review_queue(m, "R2"), [])


class PairReject(unittest.TestCase):
    def two_rooms(self):
        return readings([room("A", 0, 10, 10, 10), room("B", 10.5, 10, 10, 10)])

    def test_reject_drops_adjacency_retires_the_wall_and_survives_a_reissue(self):
        m = model_at(self.two_rooms(), accept_pairs=True)
        a, b = S.key_for_address(m, "L1/A/E", "R1"), S.key_for_address(m, "L1/B/W", "R1")
        self.assertTrue(m["surfaces"][a]["wall"])
        wall = m["surfaces"][a]["wall"]
        res = B.reject_pair(m, "R1", "L1/A/E", "L1/B/W", PERSON, "no wall, open plan")
        self.assertEqual(res["adjacencyDropped"], 2)
        rows = {s["surface"]: s for s in m["surfaceRevs"] if s["rev"] == "R1"}
        self.assertEqual(rows[a]["adjacency"], [])
        self.assertEqual(rows[b]["adjacency"], [])
        self.assertIsNone(m["surfaces"][a]["wall"])
        self.assertEqual(m["walls"][wall]["retiredIn"], "R1")
        _, r = reissue(m, self.two_rooms() | {"revision": {"id": "R2"}})
        self.assertEqual(r["pairsAccepted"], 0)
        rows2 = {s["surface"]: s for s in m["surfaceRevs"] if s["rev"] == "R2"}
        self.assertEqual(rows2[a]["adjacency"], [])

    def test_cli(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "m.json")
        S.save(model_at(self.two_rooms(), accept_pairs=True), path)
        code, text = run_cli("pair-reject", path, "L1/A/E", "L1/B/W", "--by", "matt")
        self.assertEqual(code, 0)
        self.assertEqual(len(S.load(path)["rejectedPairs"]), 1)


class SpaceFactChanges(unittest.TestCase):
    def roof(self, **kw):
        return {"level": "RF", "handle": "MAIN", "anchor": [0, 10], "edges": room("x", 0, 10, 10, 10)["edges"], **kw}

    def test_elevation_spot_and_pitch_changes_are_listed(self):
        r1 = readings([room("GARAGE", 0, 10, 10, 10, elevationFt={"value": -0.5, "source": "A-301"}),
                       room("BASEMENT", 20, 10, 10, 10, elevationFt={"value": -9.333, "source": "A-301"})],
                      roofs=[self.roof(spotFt={"value": 24, "source": "A-201"}, pitch={"value": "6:12", "source": "A-201"})])
        m = model_at(r1)
        r2 = readings([room("GARAGE", 0, 10, 10, 10, elevationFt={"value": 2.0, "source": "A-301"}),
                       room("BASEMENT", 20, 10, 10, 10, elevationFt={"value": -10.667, "source": "A-301"})],
                      roofs=[self.roof(spotFt={"value": 26.5, "source": "A-201"}, pitch={"value": "8:12", "source": "A-201"})], rev="R2")
        reissue(m, r2)
        cl = R.change_list(m, "R1", "R2")
        got = {(r["address"], r["field"]): (r["before"], r["after"], r["delta"]) for r in cl["spaces"]}
        self.assertEqual(got[("L1/GARAGE", "elevationFt")], (-0.5, 2.0, 2.5))
        self.assertEqual(got[("L1/BASEMENT", "elevationFt")], (-9.333, -10.667, -1.334))
        self.assertEqual(got[("RF/MAIN", "spotFt")], (24, 26.5, 2.5))
        self.assertEqual(got[("RF/MAIN", "pitch")], ("6:12", "8:12", None))
        md = R.change_list_md(m, cl)
        self.assertIn("L1/GARAGE | elevation | -0.5 ft | 2 ft | +2.5 ft", md)
        self.assertEqual(cl["totals"]["spaceFacts"], 4)

    def test_unchanged_facts_are_not_listed(self):
        r1 = readings([room("GARAGE", 0, 10, 10, 10, elevationFt={"value": -0.5, "source": "A-301"})])
        m = model_at(r1)
        reissue(m, readings([room("GARAGE", 0, 10, 10, 10, elevationFt={"value": -0.5, "source": "A-301"})], rev="R2"))
        self.assertEqual(R.change_list(m, "R1", "R2")["spaces"], [])


class RoofExport(unittest.TestCase):
    def setUp(self):
        ext = {"level": "L1", "anchor": [0, 10], "edges": room("x", 0, 10, 10, 10)["edges"], "heightFt": {"value": 9, "source": "A-301"}}
        roof = {"level": "RF", "handle": "MAIN", "anchor": [0, 10], "edges": ext["edges"], "elevationFt": {"value": 9, "source": "A-301"},
                "spotFt": {"value": 15, "source": "A-201"}, "pitch": {"value": "6:12", "source": "A-201"}}
        r = readings([], roofs=[roof])
        r["exterior"] = [ext]
        self.m = model_at(r)

    def test_roofs_export_carries_pitch_and_spot(self):
        out = X.roofs_export(self.m, "R1")
        self.assertEqual(len(out["roofs"]), 1)
        roof = out["roofs"][0]
        self.assertEqual((roof["pitch"], roof["spotFt"], roof["pitchSource"]), ("6:12", 15, "A-201"))
        d = tempfile.mkdtemp()
        path, dest = os.path.join(d, "m.json"), os.path.join(d, "roofs.json")
        S.save(self.m, path)
        self.assertEqual(run_cli("export", path, "--what", "roofs", "--out", dest)[0], 0)
        self.assertEqual(json.load(open(dest))["roofs"][0]["spotFt"], 15)

    def test_massing_keeps_pitch_and_height(self):
        spec = importlib.util.spec_from_file_location("massing_from_surfaces", MASSING)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out, _ = mod.build(X.surfaces_export(self.m, "R1"))
        flat = out["flats"][0]
        self.assertEqual((flat["pitch"], flat["spotFt"]), ("6:12", 15))
        roof = out["volumes"][0]["roof"]
        self.assertEqual((roof["type"], roof["pitch"], roof["riseFt"]), ("flat", "6:12", 6.0))

    def test_a_roof_without_either_stays_as_before(self):
        r = readings([], roofs=[{"level": "RF", "handle": "MAIN", "anchor": [0, 10], "edges": room("x", 0, 10, 10, 10)["edges"]}])
        spec = importlib.util.spec_from_file_location("massing_from_surfaces", MASSING)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out, _ = mod.build(X.surfaces_export(model_at(r), "R1"))
        self.assertNotIn("pitch", out["flats"][0])


if __name__ == "__main__":
    unittest.main()
