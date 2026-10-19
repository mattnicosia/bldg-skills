"""
revise.py -- a new drawing issue against the model.

drawing-index's own revision workflow runs first (sheet diff, superseded sheets,
index_revisions.md). Then this compares the previous revision's spaces with the new
readings and returns a lineage proposal. Nothing in it is a fact until a person accepts
it. Matching goes by outline overlap on the same level first and by printed number
second, never the other way, because a renumber makes number matching pair the wrong
rooms.

Two invariants gate every revision, and a failure refuses the whole revision:
  1. every key live at the previous revision appears in exactly one lineage event;
  2. the pin count after accept equals the pin count before.
"""
from __future__ import annotations

import geometry as G
from build import (accept_pairs, candidates, propose_pairs, revision_entry,
                   space_rev_row, surface_rev_row, surface_rows_for)
from store import (current_rev, live_spaces, live_surfaces, mint, retire, space_at,
                   surface_at)

SAME_MIN = 0.90       # shared / larger area: the same footprint
CHILD_INSIDE = 0.60   # a new space mostly inside one old space is its child
MOVE_TOL_FT = 0.05


# ---------------------------------------------------------------------------
# propose
# ---------------------------------------------------------------------------
def propose(model: dict, readings: dict, rev: str) -> dict:
    prev = current_rev(model)
    if prev is None:
        return {"ok": False, "problems": ["the model has no revision yet; use `build`"]}
    cand = candidates(readings)
    if cand["problems"]:
        return {"ok": False, "problems": cand["problems"]}

    old = live_spaces(model, prev)
    new = cand["spaces"]
    events: list[dict] = []
    holds: list[str] = []
    used_new: set[int] = set()
    used_old: set[str] = set()

    def shared(o: dict, n: dict) -> float:
        if o["level"] != n["level"] or not o.get("outline") or not n.get("outline"):
            return 0.0
        if o["kind"] != n["kind"] and not ({o["kind"], n["kind"]} <= {"space", "host"}):
            return 0.0
        return G.overlap_area(o["outline"]["points"], n["outline"]["points"])

    with_outline = [o for o in old if o.get("outline")]
    table: dict[str, dict[int, float]] = {}
    for o in with_outline:
        vals = {i: shared(o, n) for i, n in enumerate(new)}
        table[o["space"]] = {i: v for i, v in vals.items() if v > 0}

    # A. one old, one new, nearly the same footprint: a carry
    for o in with_outline:
        best = None
        for i, sh in table[o["space"]].items():
            if i in used_new:
                continue
            score = sh / max(o["areaSf"] or 1e-9, new[i]["areaSf"] or 1e-9)
            if score >= SAME_MIN and (best is None or score > best[1]):
                best = (i, score)
        if best:
            events.append(_carry(o["space"], best[0], o, new[best[0]], auto=True))
            used_new.add(best[0]); used_old.add(o["space"])

    # B. one old covered by several new: a split (or a carry when one child remains)
    for o in with_outline:
        if o["space"] in used_old:
            continue
        kids = [i for i, sh in table[o["space"]].items() if i not in used_new and sh / max(new[i]["areaSf"] or 1e-9, 1e-9) >= CHILD_INSIDE]
        cover = sum(table[o["space"]][i] for i in kids) / max(o["areaSf"] or 1e-9, 1e-9)
        if len(kids) >= 2 and cover >= CHILD_INSIDE:
            events.append({"kind": "split", "from": o["space"], "address": o["address"],
                           "to": [new[i]["address"] for i in kids], "toIdx": kids,
                           "note": f"{o['address']} became {', '.join(new[i]['address'] for i in kids)}",
                           "decision": "needs_person"})
            used_new.update(kids); used_old.add(o["space"])
        elif len(kids) == 1 and cover >= CHILD_INSIDE:
            events.append(_carry(o["space"], kids[0], o, new[kids[0]], auto=False))
            used_new.add(kids[0]); used_old.add(o["space"])

    # C. several old inside one new: a merge
    for i, n in enumerate(new):
        if i in used_new or not n.get("outline"):
            continue
        parents = [o for o in with_outline if o["space"] not in used_old and i in table[o["space"]]
                   and table[o["space"]][i] / max(o["areaSf"] or 1e-9, 1e-9) >= CHILD_INSIDE]
        if len(parents) >= 2:
            cover = sum(table[o["space"]][i] for o in parents) / max(n["areaSf"] or 1e-9, 1e-9)
            if cover >= CHILD_INSIDE:
                events.append({"kind": "merge", "from": [o["space"] for o in parents], "addresses": [o["address"] for o in parents],
                               "to": n["address"], "toIdx": i,
                               "note": f"{', '.join(o['address'] for o in parents)} became {n['address']}",
                               "decision": "needs_person"})
                used_new.add(i); used_old.update(o["space"] for o in parents)

    # D. spaces with no outline (hosts, labels) match by address on the same level
    by_addr = {n["address"]: i for i, n in enumerate(new)}
    for o in old:
        if o["space"] in used_old:
            continue
        if not o.get("outline"):
            i = by_addr.get(o["address"])
            if i is not None and i not in used_new and ({o["kind"], new[i]["kind"]} <= {"space", "host"} or o["kind"] == new[i]["kind"]):
                events.append(_carry(o["space"], i, o, new[i], auto=True))
                used_new.add(i); used_old.add(o["space"])
                continue
            events.append({"kind": "retire", "from": o["space"], "address": o["address"],
                           "reason": f"{o['address']} is not in the new readings", "decision": "needs_person"})
            used_old.add(o["space"])
            continue
        # an outlined space nothing matched
        i = by_addr.get(o["address"])
        if i is not None and i not in used_new:
            if not new[i].get("outline"):
                # the new set lists it without dimensions: it carries, its faces lose their outline
                events.append(_carry(o["space"], i, o, new[i], auto=False))
                used_new.add(i); used_old.add(o["space"])
                continue
            holds.append(f"{o['address']} keeps its name but moved too far to match; decide by hand")
        events.append({"kind": "retire", "from": o["space"], "address": o["address"],
                       "reason": f"nothing on {o['level']} overlaps {o['address']}", "decision": "needs_person"})
        used_old.add(o["space"])

    for i, n in enumerate(new):
        if i not in used_new:
            events.append({"kind": "new", "address": n["address"], "toIdx": i, "decision": "auto"})

    # renumber guard: more than half the printed numbers on a level changed
    for level in {o["level"] for o in old}:
        carried = [e for e in events if e["kind"] == "carry" and e.get("level") == level]
        if carried and sum(1 for e in carried if e["readdressed"]) > len(carried) / 2:
            holds.append(f"more than half of {level} is readdressed; confirm the level match before accepting")

    # invariant 1
    seen: dict[str, int] = {}
    for e in events:
        for k in ([e["from"]] if isinstance(e.get("from"), str) else e.get("from", [])):
            seen[k] = seen.get(k, 0) + 1
    missing = [o["space"] for o in old if seen.get(o["space"], 0) != 1]
    if missing:
        holds.append(f"keys not in exactly one event: {missing}")

    return {"ok": not holds, "prev": prev, "rev": rev, "events": events, "holds": holds,
            "needsPerson": [e for e in events if e.get("decision") == "needs_person"],
            "_cand": cand, "_readings": readings}


def _carry(key: str, i: int, o: dict, n: dict, auto: bool) -> dict:
    moved = False
    if o.get("outline") and n.get("outline"):
        moved = not G.same_outline(o["outline"]["points"], n["outline"]["points"], MOVE_TOL_FT)
    elif bool(o.get("outline")) != bool(n.get("outline")):
        moved = True
    return {"kind": "carry", "from": key, "toIdx": i, "address": o["address"], "to": n["address"], "level": o["level"],
            "readdressed": o["address"] != n["address"], "moved": moved,
            "decision": "auto" if auto else "needs_person"}




# ---------------------------------------------------------------------------
# accept
# ---------------------------------------------------------------------------
def accept(model: dict, proposal: dict, by: dict, accept_all: bool, accept_pairs_by: dict | None) -> dict:
    """
    Apply the proposal. Carries apply on their own. Splits, merges and retires apply
    only with accept_all (or decisions listed in proposal["decisions"] as event indexes).
    """
    if not proposal.get("ok"):
        return {"ok": False, "problems": proposal.get("holds") or proposal.get("problems")}
    prev, rev = proposal["prev"], proposal["rev"]
    decided = set(proposal.get("decisions", []))
    pending = [i for i, e in enumerate(proposal["events"]) if e.get("decision") == "needs_person" and i not in decided]
    if pending and not accept_all:
        return {"ok": False, "problems": [f"{len(pending)} events need a person: " + "; ".join(
            f"[{i}] {proposal['events'][i]['kind']} {proposal['events'][i].get('address') or proposal['events'][i].get('addresses')}" for i in pending)]}

    pins_before = len(model["pins"])
    cand = proposal["_cand"]
    new = cand["spaces"]
    model["revisions"].append(revision_entry(proposal["_readings"], rev, cand["levels"]))
    lineage: list[dict] = []
    new_keys: dict[int, str] = {}

    def write_space(key: str, i: int):
        model["spaceRevs"].append(space_rev_row(key, rev, new[i]))

    for e in proposal["events"]:
        if e["kind"] == "carry":
            i = e["toIdx"]
            model["spaces"][e["from"]]["kind"] = new[i]["kind"]
            write_space(e["from"], i)
            lineage.append({"kind": "carry", "from": e["from"], "to": e["from"], "rev": rev, "by": by,
                            "readdressed": e["readdressed"], "moved": e["moved"]})
            new_keys[i] = e["from"]
            _carry_faces(model, prev, rev, e["from"], new[i], by, lineage)
        elif e["kind"] == "new":
            i = e["toIdx"]
            k = mint(model, "sp", rev, kind=new[i]["kind"])
            write_space(k, i)
            new_keys[i] = k
            for r in surface_rows_for(new[i]):
                sk = mint(model, "sk", rev, kind=r["kind"], host=k, wall=None)
                model["surfaceRevs"].append(surface_rev_row(sk, rev, k, r))
        elif e["kind"] == "split":
            kids = []
            for i in e["toIdx"]:
                k = mint(model, "sp", rev, kind=new[i]["kind"])
                write_space(k, i)
                kids.append(k)
                new_keys[i] = k
            lineage.append({"kind": "split", "from": e["from"], "to": kids, "rev": rev, "by": by, "note": e["note"]})
            retire(model, e["from"], rev)
            _split_faces(model, prev, rev, e["from"], [(new[i], k) for i, k in zip(e["toIdx"], kids)], by, lineage)
        elif e["kind"] == "merge":
            i = e["toIdx"]
            k = mint(model, "sp", rev, kind=new[i]["kind"])
            write_space(k, i)
            new_keys[i] = k
            lineage.append({"kind": "merge", "from": e["from"], "to": k, "rev": rev, "by": by, "note": e["note"]})
            for p in e["from"]:
                retire(model, p, rev)
            _merge_faces(model, prev, rev, e["from"], new[i], k, by, lineage)
        elif e["kind"] == "retire":
            retire(model, e["from"], rev)
            lineage.append({"kind": "retire", "from": e["from"], "rev": rev, "by": by, "reason": e["reason"]})
            for s in live_surfaces(model, prev):
                if s["host"] == e["from"]:
                    retire(model, s["surface"], rev)
                    lineage.append({"kind": "retire", "from": s["surface"], "rev": rev, "by": by, "reason": e["reason"]})

    model["lineage"].extend(lineage)
    pairs = propose_pairs(new, model["wallTolFt"])
    accepted = accept_pairs(model, rev, pairs, accept_pairs_by) if accept_pairs_by else 0
    if len(model["pins"]) != pins_before:
        raise SystemExit("pin count changed during accept; refusing")
    return {"ok": True, "rev": rev, "lineage": len(lineage), "pairsProposed": len(pairs), "pairsAccepted": accepted,
            "counts": {k: sum(1 for l in lineage if l["kind"] == k) for k in ("carry", "split", "merge", "retire")}}


# ---------------------------------------------------------------------------
# faces under each space event
# ---------------------------------------------------------------------------
def _old_faces(model: dict, prev: str, host: str) -> list[dict]:
    return [s for s in live_surfaces(model, prev) if s["host"] == host]


def _carry_faces(model, prev, rev, host, n, by, lineage):
    """Same space: match faces by face name (N, N2, FLR...). Extra old faces retire, new ones mint."""
    old = {s["face"]: s for s in _old_faces(model, prev, host)}
    rows = {r["face"]: r for r in surface_rows_for(n)}
    for face, r in rows.items():
        if face in old:
            k = old[face]["surface"]
            row = surface_rev_row(k, rev, host, r)
            row["adjacency"] = []
            model["surfaceRevs"].append(row)
            moved = old[face].get("seg") != r.get("seg") or old[face].get("poly") != r.get("poly")
            lineage.append({"kind": "carry", "from": k, "to": k, "rev": rev, "by": by,
                            "readdressed": old[face]["address"] != r["address"], "moved": bool(moved)})
        else:
            k = mint(model, "sk", rev, kind=r["kind"], host=host, wall=None)
            model["surfaceRevs"].append(surface_rev_row(k, rev, host, r))
    for face, s in old.items():
        if face not in rows:
            retire(model, s["surface"], rev)
            lineage.append({"kind": "retire", "from": s["surface"], "rev": rev, "by": by,
                            "reason": f"{s['address']} has no counterpart in {rev}"})


def _split_faces(model, prev, rev, host, kids, by, lineage):
    """An old face that two children share splits; one wholly inside a child carries readdressed."""
    old = _old_faces(model, prev, host)
    claimed: dict[str, list[str]] = {s["surface"]: [] for s in old}
    for n, k in kids:
        for r in surface_rows_for(n):
            match = _collinear_old(old, r)
            sk = mint(model, "sk", rev, kind=r["kind"], host=k, wall=None)
            model["surfaceRevs"].append(surface_rev_row(sk, rev, k, r))
            if match:
                claimed[match["surface"]].append(sk)
    for s in old:
        kids_of = claimed[s["surface"]]
        retire(model, s["surface"], rev)
        if len(kids_of) == 1:
            lineage.append({"kind": "carry", "from": s["surface"], "to": kids_of[0], "rev": rev, "by": by, "readdressed": True, "moved": False})
        elif len(kids_of) > 1:
            lineage.append({"kind": "split", "from": s["surface"], "to": kids_of, "rev": rev, "by": by, "note": "the cut line crosses this face"})
        else:
            lineage.append({"kind": "retire", "from": s["surface"], "rev": rev, "by": by, "reason": "no child face lies on it"})


def _merge_faces(model, prev, rev, parents, n, k, by, lineage):
    """New outer faces that two old collinear faces covered are merges; removed partition faces retire."""
    old = [s for p in parents for s in _old_faces(model, prev, p)]
    covered: set[str] = set()
    for r in surface_rows_for(n):
        sk = mint(model, "sk", rev, kind=r["kind"], host=k, wall=None)
        model["surfaceRevs"].append(surface_rev_row(sk, rev, k, r))
        ms = _collinear_old_all(old, r)
        for m in ms:
            covered.add(m["surface"])
        if len(ms) == 1:
            lineage.append({"kind": "carry", "from": ms[0]["surface"], "to": sk, "rev": rev, "by": by, "readdressed": True, "moved": True})
        elif len(ms) > 1:
            lineage.append({"kind": "merge", "from": [m["surface"] for m in ms], "to": sk, "rev": rev, "by": by, "note": "collinear faces joined"})
    for s in old:
        retire(model, s["surface"], rev)
        if s["surface"] not in covered:
            lineage.append({"kind": "retire", "from": s["surface"], "rev": rev, "by": by, "reason": "partition removed"})


def _collinear_old(old: list[dict], r: dict) -> dict | None:
    ms = _collinear_old_all(old, r)
    return ms[0] if ms else None


def _collinear_old_all(old: list[dict], r: dict) -> list[dict]:
    out = []
    if r.get("seg") is None:
        for s in old:
            if s["face"] == r["face"] and s.get("seg") is None:
                out.append(s)
        return out
    rf = {"normal": r["direction"], "start": r["seg"][0], "end": r["seg"][1]}
    for s in old:
        if s.get("seg") is None or s.get("direction") != r["direction"]:
            continue
        of = {"normal": s["direction"], "start": s["seg"][0], "end": s["seg"][1]}
        p1, _, _ = G.face_line(rf)
        p2, _, _ = G.face_line(of)
        if abs(p1 - p2) > 0.1:
            continue
        if G.along_overlap(rf, of):
            out.append(s)
    return out
