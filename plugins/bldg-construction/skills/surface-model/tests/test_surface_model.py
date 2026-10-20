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
import geometry as G  # noqa: E402
import export as X  # noqa: E402
import openings as O  # noqa: E402
import pins as P  # noqa: E402
import prefill as F  # noqa: E402
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


class PrefillSplitDimensions(unittest.TestCase):
    """Revit prints one dimension as several words; prefill must read it as one string."""

    def line(self, text):
        return {"x": 10.0, "y": 20.0, "text": text}

    def test_split_and_whole_strings_read_the_same(self):
        got = F.join_dims([self.line("11' - 0 1/2\""), self.line("39' - 6\""), self.line("33'-0\""),
                           self.line("10'-4 1/2\""), self.line("12' 7\"")])
        self.assertEqual([d["text"] for d in got], ["11'-0 1/2\"", "39'-6\"", "33'-0\"", "10'-4 1/2\"", "12'-7\""])
        self.assertEqual([G.parse_feet(d["text"]) for d in got], [11 + 0.5 / 12, 39.5, 33.0, 10 + 4.5 / 12, 12 + 7 / 12])

    def test_two_strings_on_one_line_and_other_words_are_kept_apart(self):
        got = F.join_dims([self.line("14' - 8 1/2\" 12' - 7\""), self.line("SEE A401 6' - 0\" CLR")])
        self.assertEqual([d["text"] for d in got], ["14'-8 1/2\"", "12'-7\"", "6'-0\""])

    def test_level_marker_zero_is_not_a_length(self):
        self.assertEqual(F.join_dims([self.line("0' - 0\"")]), [])


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

    def test_a_merged_room_that_rose_is_listed(self):
        # Yaun Road REV 02: the laundry folds into the mud room, and the floor rises to +2'-0".
        m = model_at(readings([room("MUD-ROOM", 0, 10, 10, 10), room("LAUNDRY", 10, 10, 5, 10)]))
        reissue(m, readings([room("MUD-ROOM", 0, 10, 15, 10, elevationFt={"value": 2.0, "source": "A101.5"})], rev="R2"))
        cl = R.change_list(m, "R1", "R2")
        got = [(r["address"], r["was"], r["field"], r["before"], r["after"], r["delta"]) for r in cl["spaces"]]
        self.assertEqual(got, [("L1/MUD-ROOM", "L1/LAUNDRY, L1/MUD-ROOM", "elevationFt", 0, 2.0, 2.0)])
        self.assertIn("L1/MUD-ROOM | elevation | 0 ft | 2 ft | +2 ft", R.change_list_md(m, cl))

    def test_a_split_room_that_dropped_is_listed_once_per_part(self):
        m = model_at(readings([room("GARAGE", 0, 10, 20, 10)]))
        reissue(m, readings([room("GARAGE", 0, 10, 12, 10),
                             room("SHOP", 12, 10, 8, 10, elevationFt={"value": -0.5, "source": "A-301"})], rev="R2"))
        got = [(r["address"], r["was"], r["before"], r["after"]) for r in R.change_list(m, "R1", "R2")["spaces"]]
        self.assertEqual(got, [("L1/SHOP", "L1/GARAGE", 0, -0.5)])

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



class LineageExport(unittest.TestCase):
    def test_a_split_and_a_merge_both_reach_surfaces_json(self):
        m = model_at(readings([room("GARAGE", 0, 10, 20, 10), room("MUD-ROOM", 30, 10, 10, 10), room("LAUNDRY", 40, 10, 5, 10)]))
        keys = {r["address"]: r["space"] for r in S.live_spaces(m, "R1")}
        reissue(m, readings([room("GARAGE", 0, 10, 12, 10), room("SHOP", 12, 10, 8, 10), room("MUD-ROOM", 30, 10, 15, 10)], rev="R2"))
        d = tempfile.mkdtemp()
        path, dest = os.path.join(d, "m.json"), os.path.join(d, "surfaces.json")
        S.save(m, path)
        self.assertEqual(run_cli("export", path, "--what", "surfaces", "--out", dest)[0], 0)
        out = json.load(open(dest))
        self.assertEqual(out["lineage"], m["lineage"])
        split = [e for e in out["lineage"] if e["kind"] == "split" and e["from"] == keys["L1/GARAGE"]]
        merge = [e for e in out["lineage"] if e["kind"] == "merge" and sorted(e["from"]) == sorted([keys["L1/MUD-ROOM"], keys["L1/LAUNDRY"]])]
        self.assertEqual(len(split), 1)
        self.assertEqual(len(merge), 1)
        self.assertEqual((split[0]["rev"], len(split[0]["to"]), merge[0]["rev"]), ("R2", 2, "R2"))
        self.assertTrue(set(split[0]["to"]) <= {r["key"] for r in out["spaces"]})
        self.assertIn(merge[0]["to"], {r["key"] for r in out["spaces"]})

    def test_an_earlier_revision_leaves_out_later_events(self):
        m = model_at(readings([room("GARAGE", 0, 10, 20, 10)]))
        reissue(m, readings([room("GARAGE", 0, 10, 12, 10), room("SHOP", 12, 10, 8, 10)], rev="R2"))
        self.assertEqual(X.surfaces_export(m, "R1")["lineage"], [])

    def test_a_model_saved_before_lineage_still_exports(self):
        m = model_at(readings([room("GARAGE", 0, 10, 20, 10)]))
        del m["lineage"]
        self.assertEqual(X.surfaces_export(m, "R1")["lineage"], [])

    def test_a_file_without_lineage_still_builds_massing(self):
        spec = importlib.util.spec_from_file_location("massing_from_surfaces", MASSING)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        old = X.surfaces_export(model_at(readings([room("GARAGE", 0, 10, 20, 10)])), "R1")
        del old["lineage"]
        mod.build(old)


class ChangesExport(unittest.TestCase):
    def test_each_revision_exports_the_change_list_from_the_one_before(self):
        m = model_at(readings([room("GARAGE", 0, 10, 20, 10)]))
        reissue(m, readings([room("GARAGE", 0, 10, 12, 10), room("SHOP", 12, 10, 8, 10)], rev="R2"))
        self.assertIsNone(X.surfaces_export(m, "R1")["changes"])
        changes = X.surfaces_export(m, "R2")["changes"]
        self.assertEqual(changes, R.change_list(m, "R1", "R2"))
        self.assertTrue(changes["surfaces"])



def opening(face, tag, c, w, kind="window", host="EXT", sill=3, head=8, level="L1", **extra):
    return {"level": level, "host": host, "face": face, "kind": kind, "tag": {"value": tag, "source": "A-101"},
            "centerFt": {"value": c, "source": "A-101", "confidence": "LOW", "reason": "center from the plan tag"},
            "widthFt": {"value": w, "source": "A-200"}, "sillFt": {"value": sill, "source": "A-200"},
            "headFt": {"value": head, "source": "A-200"}, **extra}


def house(ops, rev="R1", rooms=None, roofs=(), **extra):
    r = readings(rooms if rooms is not None else [room("LIVING", 0, 20, 30, 20)], roofs=roofs, rev=rev)
    r["exterior"] = [{"level": "L1", "anchor": [0, 20], "edges": room("x", 0, 20, 30, 20)["edges"],
                      "heightFt": {"value": 10, "source": "A-301"}}]
    r["openings"] = ops
    r.update(extra)
    return r


class OpeningBuild(unittest.TestCase):
    def test_each_opening_gets_a_key_in_its_face(self):
        m = model_at(house([opening("N", "W01", 10, 5), opening("S", "102", 15, 3, kind="door", sill=0)]))
        ops = {o["address"]: o for o in S.live_openings(m, "R1")}
        self.assertEqual(sorted(ops), ["L1/EXT/N/W01@10", "L1/EXT/S/102@15"])
        north = S.key_for_address(m, "L1/EXT/N", "R1")
        self.assertEqual(ops["L1/EXT/N/W01@10"]["surface"], north)
        self.assertEqual(ops["L1/EXT/N/W01@10"]["opening"], "op_1")
        self.assertEqual(ops["L1/EXT/N/W01@10"]["at"], [10.0, 20.0])
        self.assertEqual(ops["L1/EXT/S/102@15"]["at"], [15.0, 0.0])

    def test_an_interior_door_sits_in_a_room_face(self):
        m = model_at(house([opening("E", "101", 10, 3, kind="door", host="LIVING", sill=0)]))
        self.assertEqual(S.live_openings(m, "R1")[0]["surface"], S.key_for_address(m, "L1/LIVING/E", "R1"))

    def test_an_opening_that_does_not_fit_its_face_is_refused(self):
        for bad in (opening("N", "W01", 28, 5), opening("N", "W01", 2, 5), opening("E", "W01", 10, 21)):
            res = B.first_build(S.new_model("T1"), house([bad]), "R1", None)
            self.assertFalse(res["ok"])
            self.assertIn("does not fit", res["problems"][0])

    def test_an_unknown_face_or_kind_is_refused(self):
        res = B.first_build(S.new_model("T1"), house([opening("N2", "W01", 10, 5)]), "R1", None)
        self.assertIn("no such face", res["problems"][0])
        res = B.first_build(S.new_model("T1"), house([opening("N", "W01", 10, 5, kind="skylight")]), "R1", None)
        self.assertIn("is not one of", res["problems"][0])


class OpeningReissue(unittest.TestCase):
    def setUp(self):
        self.m = model_at(house([opening("N", "W01", 10, 5), opening("N", "W01", 20, 5), opening("E", "W02", 10, 4),
                                 opening("S", "102", 15, 3, kind="door", sill=0)]))

    def reissue(self, ops, **kw):
        return reissue(self.m, house(ops, rev="R2", **kw))

    def test_carry_resize_remove_and_add(self):
        _, res = self.reissue([opening("N", "W01", 10.4, 5), opening("E", "W02", 10, 5),
                               opening("S", "102", 15, 3, kind="door", sill=0),
                               opening("W", "115", 10, 10, kind="slider", sill=0, leaves=2)])
        self.assertEqual(res["openings"], {"carried": 3, "retired": 1, "minted": 1})
        live = {o["address"]: o["opening"] for o in S.live_openings(self.m, "R2")}
        self.assertEqual(live["L1/EXT/N/W01@10.4"], "op_1")
        self.assertEqual(live["L1/EXT/E/W02@10"], "op_3")
        self.assertEqual(live["L1/EXT/W/115@10"], "op_5")
        self.assertEqual(self.m["openings"]["op_2"]["retiredIn"], "R2")
        ev = [e for e in self.m["lineage"] if e["from"].startswith("op_")]
        self.assertEqual(sorted(e["from"] for e in ev), ["op_1", "op_2", "op_3", "op_4"])
        rows = {(r["change"], r["kind"]): r for r in R.change_list(self.m, "R1", "R2")["surfaces"] if r["subject"] == "opening"}
        self.assertEqual(sorted(rows), [("added", "slider"), ("changed", "window"), ("removed", "window")])
        self.assertEqual((rows[("changed", "window")]["lengthBefore"], rows[("changed", "window")]["lengthAfter"]), (4, 5))
        self.assertEqual(rows[("changed", "window")]["note"], "resized: width")
        self.assertEqual(R.change_list(self.m, "R1", "R2")["totals"]["openings"], {"added": 1, "removed": 1, "resized": 1})

    def test_a_move_past_a_foot_or_a_new_tag_retires_and_mints(self):
        _, res = self.reissue([opening("N", "W01", 11.5, 5), opening("N", "W09", 20, 5), opening("E", "W02", 10, 4),
                               opening("S", "102", 15, 3, kind="door", sill=0)])
        self.assertEqual(res["openings"], {"carried": 2, "retired": 2, "minted": 2})

    def test_a_sill_change_is_a_resize(self):
        self.reissue([opening("N", "W01", 10, 5), opening("N", "W01", 20, 5, sill=2), opening("E", "W02", 10, 4),
                      opening("S", "102", 15, 3, kind="door", sill=0)])
        rows = [r for r in R.change_list(self.m, "R1", "R2")["surfaces"] if r["subject"] == "opening"]
        self.assertEqual([(r["change"], r["note"], r["sillBefore"], r["sillAfter"]) for r in rows],
                         [("changed", "resized: sill", 3, 2)])

    def test_an_opening_follows_its_face_into_a_split_room(self):
        m = model_at(house([opening("N", "101", 25, 3, kind="door", host="GARAGE", sill=0)],
                           rooms=[room("GARAGE", 0, 20, 30, 20)]))
        reissue(m, house([opening("N", "101", 7, 3, kind="door", host="SHOP", sill=0)], rev="R2",
                         rooms=[room("GARAGE", 0, 20, 18, 20), room("SHOP", 18, 20, 12, 20)]))
        live = S.live_openings(m, "R2")
        self.assertEqual([o["opening"] for o in live], ["op_1"])
        self.assertEqual(live[0]["surface"], S.key_for_address(m, "L1/SHOP/N", "R2"))
        self.assertEqual(live[0]["address"], "L1/SHOP/N/101@7")


class HouseExport(unittest.TestCase):
    def roof(self, **kw):
        return {"level": "RF", "handle": "MAIN-S", "anchor": [0, 10], "edges": room("x", 0, 10, 30, 10)["edges"],
                "spotFt": {"value": 20, "source": "A-201"}, "pitch": {"value": "12/12", "source": "A-201"}, **kw}

    def export(self, **kw):
        return X.surfaces_export(model_at(house([opening("N", "W01", 10, 5, unit={"value": "Andersen 400", "source": "A-200"})], **kw)), "R1")

    def test_openings_follow_the_contract(self):
        op = self.export()["openings"][0]
        self.assertEqual(sorted(op), sorted(["key", "address", "wasAddress", "surface", "wall", "level", "kind", "tag",
                                             "centerFt", "widthFt", "sillFt", "headFt", "leaves", "unit"]))
        self.assertEqual((op["key"], op["address"], op["kind"], op["leaves"]), ("op_1", "L1/EXT/N/W01@10", "window", 1))
        self.assertEqual(op["centerFt"], {"value": 10, "source": "A-101", "confidence": "LOW", "reason": "center from the plan tag"})

    def test_roof_downslope_eave_finish_materials_and_grade(self):
        out = self.export(roofs=[self.roof(downslope={"value": "S", "source": "A-201"}, finish={"value": "RF-1", "source": "A-002"})],
                          materials={"RF-1": {"label": "Standing seam", "kind": "standing_seam", "source": "A-002"}},
                          site={"gradeFt": {"value": -0.67, "source": "A-301", "confidence": "MEDIUM"}})
        roof = next(s for s in out["spaces"] if s["kind"] == "roof")
        self.assertEqual(roof["downslope"], {"value": "S", "source": "A-201", "confidence": "HIGH"})
        self.assertEqual(roof["finish"], "RF-1")
        self.assertEqual((roof["eaveFt"]["value"], roof["eaveFt"]["confidence"]), (10.0, "LOW"))
        self.assertIn("derived", roof["eaveFt"]["reason"])
        self.assertEqual(out["materials"]["RF-1"]["kind"], "standing_seam")
        self.assertEqual(out["site"]["gradeFt"]["value"], -0.67)

    def test_a_grade_the_set_does_not_give_is_not_measured_with_its_reason(self):
        out = self.export(site={"gradeFt": {"confidence": "NOT_MEASURED", "reason": "no grade printed"}})
        self.assertEqual(out["site"]["gradeFt"], {"confidence": "NOT_MEASURED", "reason": "no grade printed"})

    def test_absent_fields_stay_absent(self):
        out = self.export(roofs=[self.roof()])
        roof = next(s for s in out["spaces"] if s["kind"] == "roof")
        self.assertFalse({"downslope", "eaveFt", "finish"} & set(roof))
        self.assertEqual((out["materials"], out["site"]), ({}, {}))
        m = model_at(readings([room("GARAGE", 0, 10, 20, 10)]))
        del m["openings"], m["openingRevs"]
        self.assertEqual(X.surfaces_export(m, "R1")["openings"], [])

    def test_a_star_finish_covers_every_wall_face(self):
        out = X.surfaces_export(model_at(house([])), "R1")
        self.assertEqual({s["finish"] for s in out["surfaces"] if s["kind"] == "exterior_face"}, {None})
        r = house([])
        r["exterior"][0]["finishes"] = {"*": {"value": "SID-1", "source": "A-002"}, "N": {"value": "STO-1", "source": "A-002"}}
        faces = {s["face"]: s["finish"] for s in X.surfaces_export(model_at(r), "R1")["surfaces"] if s["kind"] == "exterior_face"}
        self.assertEqual(faces, {"N": "STO-1", "E": "SID-1", "S": "SID-1", "W": "SID-1"})

    def test_pitch_ratio(self):
        self.assertEqual([X.pitch_ratio(p) for p in ("12/12", "3/12", "6:12", "1/4/12", "flat")],
                         [1.0, 0.25, 0.5, 0.25 / 12, None])


class WorkedExample(unittest.TestCase):
    def test_the_e26049_reissue_adds_removes_and_resizes_an_opening(self):
        ex = os.path.join(HERE, "..", "examples", "e26049")
        def load(name):
            with open(os.path.join(ex, name), encoding="utf-8") as f:
                return json.load(f)
        m = S.new_model("E26049")
        B.first_build(m, load("readings_rev1.json"), "SD-1", PERSON)
        reissue(m, load("readings_rev2.json"), rev="DD-1")
        cl = R.change_list(m, "SD-1", "DD-1")
        self.assertEqual(cl["totals"]["openings"], {"added": 1, "removed": 1, "resized": 1})
        self.assertEqual(len(X.surfaces_export(m, "DD-1")["openings"]), 5)


if __name__ == "__main__":
    unittest.main()
