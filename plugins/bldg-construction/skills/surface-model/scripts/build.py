"""
build.py -- turn one revision's readings into spaces, walls and surfaces.

Input: a readings file (see references/readings-format.md). A person wrote it from the
dimension strings on the plans, or confirmed a draft that prefill.py made from the text
layer. Every length carries its sheet. Nothing is measured off an image.

For the first revision this mints every key. For a later revision, revise.py calls
`candidates()` here and decides lineage before anything is minted.
"""
from __future__ import annotations

import geometry as G
from store import mint

KINDS = {"space": "wall_face", "exterior": "exterior_face", "roof": "roof"}


def cited(v, default_conf="HIGH"):
    """Accept {"value":..,"source":..} or a bare number with no source (LOW)."""
    if v is None:
        return None
    if isinstance(v, dict):
        d = {"value": v.get("value"), "source": v.get("source"),
             "confidence": v.get("confidence") or (default_conf if v.get("source") else "LOW")}
        if v.get("confirmedBy"):
            d["confirmedBy"] = v["confirmedBy"]
        return d
    return {"value": v, "source": None, "confidence": "LOW"}


def unmeasured(reason: str) -> dict:
    return {"confidence": "NOT_MEASURED", "reason": reason}


def host_handle(entry: dict, taken: set[str]) -> str:
    """Printed number first. Otherwise the plan's word plus an ordinal, minted once."""
    if entry.get("number"):
        return str(entry["number"]).upper()
    if entry.get("handle"):
        return str(entry["handle"]).upper()
    word = (entry.get("name") or "SPACE").upper().split()[0]
    n = 1
    while f"{word}-{n}" in taken:
        n += 1
    return f"{word}-{n}"


# ---------------------------------------------------------------------------
# candidates: geometry for every entry in the readings, no keys yet
# ---------------------------------------------------------------------------
def candidates(readings: dict) -> dict:
    """
    Returns {"levels": {...}, "spaces": [cand...], "problems": [...]}. Each cand holds
    kind, level, handle, address, name, number, outline (points, faces, closed,
    closureErrorIn), areaSf, ceilingFt or heightFt, runs, finishes, phase.
    """
    problems: list[str] = []
    levels = {lv["id"].upper(): lv for lv in readings.get("levels", [])}
    cands: list[dict] = []
    taken_per_level: dict[str, set[str]] = {}

    def add(kind: str, entry: dict, level: str):
        if entry.get("draft"):
            problems.append(f"{level}/{entry.get('handle') or entry.get('number') or entry.get('name')} is still a draft; confirm it first")
            return
        taken = taken_per_level.setdefault(level, set())
        handle = "EXT" if kind == "exterior" else host_handle(entry, taken)
        if handle in taken:
            problems.append(f"{level}/{handle} appears twice in the readings")
        taken.add(handle)
        c = {
            "kind": kind, "level": level, "handle": handle, "address": f"{level}/{handle}",
            "name": cited(entry.get("name")) if entry.get("name") else None,
            "number": cited(entry.get("number")) if entry.get("number") else None,
            "phase": entry.get("phase", "new"),
            "runs": entry.get("runs", []), "finishes": entry.get("finishes", {}),
            "mepTags": entry.get("mepTags", []),
            "confirmedBy": entry.get("confirmedBy"),
            "outline": None, "areaSf": None,
        }
        edges = entry.get("edges")
        if edges:
            w = None
            try:
                w = G.walk(entry.get("anchor", [0, 0]), edges)
            except ValueError as e:
                problems.append(f"{c['address']}: {e}")
            if w:
                G.assign_ordinals(w["faces"])
                c["outline"] = w
                c["anchor"] = entry.get("anchor", [0, 0])
                c["anchorSource"] = entry.get("anchorSource")
                if w["closed"]:
                    c["areaSf"] = round(G.area(w["points"]), 2)
                else:
                    problems.append(f"{c['address']}: the walk misses its start by "
                                    f"{w['closureErrorIn']} in; name the edge that is wrong")
        lv = levels.get(level, {})
        c["elevationFt"] = cited(entry.get("elevationFt")) if entry.get("elevationFt") else None
        if kind == "exterior":
            c["heightFt"] = cited(entry.get("heightFt")) or (cited(lv.get("storyFt")) if lv.get("storyFt") else None)
        elif kind == "roof":
            c["spotFt"] = cited(entry.get("spotFt")) if entry.get("spotFt") is not None else None
            c["pitch"] = cited(entry.get("pitch")) if entry.get("pitch") is not None else None
        elif kind == "space":
            c["ceilingFt"] = cited(entry.get("ceilingFt")) or (cited(lv.get("ceilingFt")) if lv.get("ceilingFt") else None)
        cands.append(c)

    for e in readings.get("spaces", []):
        add("space", e, e["level"].upper())
    for e in readings.get("exterior", []):
        add("exterior", e, e["level"].upper())
    for e in readings.get("roofs", []):
        add("roof", e, (e.get("level") or "RF").upper())
    for e in readings.get("hosts", []):
        add("host", e, (e.get("level") or "SITE").upper())
    return {"levels": levels, "spaces": cands, "problems": problems}


_RANK = {"VERIFIED": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "NOT_MEASURED": 4}


def weakest(confs) -> str:
    return max(confs, key=lambda c: _RANK.get(c, 3))


def surface_rows_for(cand: dict) -> list[dict]:
    """The surfaces a candidate implies, as rows without keys."""
    rows: list[dict] = []
    lvl, host, kind = cand["level"], cand["handle"], cand["kind"]
    if kind == "host":
        return rows
    w = cand["outline"]
    if kind == "roof":
        rows.append({"face": "TOP", "kind": "roof", "areaSf": cand["areaSf"], "lengthFt": None,
                     "heightFt": None, "seg": None, "poly": w["points"] if w else None,
                     "address": f"{lvl}/{host}/TOP", "runs": [], "finish": None})
        return rows
    if w:
        h = cand.get("heightFt") if kind == "exterior" else cand.get("ceilingFt")
        for f in w["faces"]:
            parts = f["parts"]
            sources = sorted({p["source"] for p in parts if p.get("source")})
            length = {"value": round(f["lengthFt"], 4), "source": ", ".join(sources) or None,
                      "confidence": weakest(p["confidence"] for p in parts) if sources else "LOW"}
            height = h if h else unmeasured("no ceiling height on the RCP, schedule or section")
            area = None
            if height.get("confidence") != "NOT_MEASURED" and height.get("value") is not None:
                area = round(f["lengthFt"] * float(height["value"]), 2)
            rows.append({"face": f["face"], "direction": f["normal"], "ordinal": f["ordinal"],
                         "kind": KINDS[kind], "lengthFt": length, "heightFt": height, "areaSf": area,
                         "seg": [f["start"], f["end"]], "poly": None, "parts": parts,
                         "address": f"{lvl}/{host}/{f['face']}",
                         "runs": [r for r in cand.get("runs", []) if str(r.get("face", "")).upper() == f["face"]],
                         "finish": cited(cand.get("finishes", {}).get(f["face"]))})
    if kind == "space":
        for fc, k in (("FLR", "floor"), ("CLG", "ceiling")):
            rows.append({"face": fc, "kind": k, "areaSf": cand["areaSf"], "lengthFt": None,
                         "heightFt": cand.get("ceilingFt") if fc == "CLG" else None,
                         "seg": None, "poly": w["points"] if w else None, "runs": [],
                         "address": f"{lvl}/{host}/{fc}", "finish": cited(cand.get("finishes", {}).get(fc))})
    return rows


# ---------------------------------------------------------------------------
# adjacency: which faces are the two sides of one wall
# ---------------------------------------------------------------------------
def propose_pairs(cands: list[dict], wall_tol_ft: float) -> list[dict]:
    """Back-to-back faces on one level. Each proposal names both faces and the span."""
    out = []
    by_level: dict[str, list[tuple[dict, dict]]] = {}
    for c in cands:
        if not c.get("outline"):
            continue
        for f in c["outline"]["faces"]:
            by_level.setdefault(c["level"], []).append((c, f))
    for level, faces in by_level.items():
        for i, (ca, fa) in enumerate(faces):
            if ca["kind"] != "space":
                continue
            for j, (cb, fb) in enumerate(faces):
                if ca is cb or cb["kind"] not in ("space", "exterior"):
                    continue
                if cb["kind"] == "space" and j < i:
                    continue  # each interior pair once
                span = G.back_to_back(fa, fb, cb["kind"] == "exterior", wall_tol_ft)
                if not span:
                    continue
                out.append({"level": level,
                            "a": f"{ca['address']}/{fa['face']}", "b": f"{cb['address']}/{fb['face']}",
                            "spanA": G.face_span_from_left(fa, *span), "spanB": G.face_span_from_left(fb, *span),
                            "lengthFt": round(span[1] - span[0], 3)})
    return out


# ---------------------------------------------------------------------------
# rows
# ---------------------------------------------------------------------------
def space_rev_row(sk: str, rev: str, c: dict) -> dict:
    w = c.get("outline")
    return {
        "space": sk, "rev": rev, "address": c["address"], "level": c["level"], "kind": c["kind"],
        "printedNumber": c.get("number"), "name": c.get("name"),
        "outline": None if not w else {
            "anchor": c.get("anchor"), "anchorSource": c.get("anchorSource"),
            "points": w["points"], "closed": w["closed"], "closureErrorIn": w["closureErrorIn"],
            "edges": [{"heading": f["heading"], "lengthFt": round(f["lengthFt"], 4), "parts": f["parts"]} for f in w["faces"]]},
        "areaSf": c.get("areaSf"), "ceilingFt": c.get("ceilingFt"), "heightFt": c.get("heightFt"),
        "elevationFt": c.get("elevationFt"), "spotFt": c.get("spotFt"), "pitch": c.get("pitch"),
        "phase": c.get("phase", "new"), "mepTags": c.get("mepTags", []), "confirmedBy": c.get("confirmedBy"),
    }


def surface_rev_row(k: str, rev: str, host_key: str, r: dict) -> dict:
    return {
        "surface": k, "rev": rev, "address": r["address"], "host": host_key, "kind": r["kind"],
        "face": r["face"], "direction": r.get("direction"), "ordinal": r.get("ordinal"),
        "adjacency": [], "lengthFt": r.get("lengthFt"), "heightFt": r.get("heightFt"), "areaSf": r.get("areaSf"),
        "runs": r.get("runs", []), "finish": r.get("finish"), "phase": "new",
        "seg": r.get("seg"), "poly": r.get("poly"), "confirmedBy": None,
    }


def revision_entry(readings: dict, rev: str, levels: dict) -> dict:
    meta = readings.get("revision", {})
    return {"id": rev, "label": meta.get("label"), "date": meta.get("date"), "sheets": meta.get("sheets", []),
            "levels": {k: {"elevationFt": cited(v.get("elevationFt")),
                           "storyFt": cited(v.get("storyFt")) if v.get("storyFt") else None,
                           "ceilingFt": cited(v.get("ceilingFt")) if v.get("ceilingFt") else None}
                       for k, v in levels.items()}}


# ---------------------------------------------------------------------------
# first build: mint everything
# ---------------------------------------------------------------------------
def first_build(model: dict, readings: dict, rev: str, accept_pairs_by: dict | None) -> dict:
    cand = candidates(readings)
    if cand["problems"]:
        return {"ok": False, "problems": cand["problems"]}
    if model["revisions"]:
        return {"ok": False, "problems": ["the model already has a revision; use `revise`"]}
    model["north"] = readings.get("north")
    model["wallTolFt"] = readings.get("wallTolFt", model.get("wallTolFt", 1.0))
    model["revisions"].append(revision_entry(readings, rev, cand["levels"]))
    for c in cand["spaces"]:
        sk = mint(model, "sp", rev, kind=c["kind"])
        model["spaceRevs"].append(space_rev_row(sk, rev, c))
        for r in surface_rows_for(c):
            k = mint(model, "sk", rev, kind=r["kind"], host=sk, wall=None)
            model["surfaceRevs"].append(surface_rev_row(k, rev, sk, r))
    pairs = propose_pairs(cand["spaces"], model["wallTolFt"])
    result = {"ok": True, "rev": rev, "spaces": len(cand["spaces"]),
              "surfaces": sum(1 for s in model["surfaceRevs"] if s["rev"] == rev),
              "pairsProposed": len(pairs), "pairs": pairs, "pairsAccepted": 0}
    if accept_pairs_by:
        result["pairsAccepted"] = accept_pairs(model, rev, pairs, accept_pairs_by)
    return result


def accept_pairs(model: dict, rev: str, pairs: list[dict], by: dict) -> int:
    """Confirmed pairs create wall cores and fill adjacency on both faces."""
    from store import address_map
    amap = address_map(model, rev)
    rows = {s["surface"]: s for s in model["surfaceRevs"] if s["rev"] == rev}
    rejected = {frozenset(r["keys"]) for r in model.get("rejectedPairs", [])}
    n = 0
    for p in pairs:
        ka, kb = amap.get(p["a"]), amap.get(p["b"])
        if not ka or not kb or ka not in rows or kb not in rows:
            continue
        if frozenset((ka, kb)) in rejected:
            continue
        wk = model["surfaces"][ka].get("wall") or model["surfaces"][kb].get("wall") or mint(model, "wk", rev)
        model["surfaces"][ka]["wall"] = wk
        model["surfaces"][kb]["wall"] = wk
        rows[ka]["adjacency"].append({"opposite": rows[kb]["host"], "surface": kb, "fromFt": p["spanA"][0], "toFt": p["spanA"][1], "confirmedBy": by})
        rows[kb]["adjacency"].append({"opposite": rows[ka]["host"], "surface": ka, "fromFt": p["spanB"][0], "toFt": p["spanB"][1], "confirmedBy": by})
        n += 1
    return n


def reject_pair(model: dict, rev: str, addr_a: str, addr_b: str, by: dict, reason: str | None = None) -> dict:
    """
    A person says two faces are not the two sides of one wall. The pair is dropped from the
    adjacency of both faces at this revision and stays rejected: later accepts skip it. A wall
    core that no face points at any more is retired (keys are never deleted).
    """
    from store import address_map, now, retire
    amap = address_map(model, rev)
    ka, kb = amap.get(addr_a), amap.get(addr_b)
    if not ka or not kb or not ka.startswith("sk") or not kb.startswith("sk"):
        raise SystemExit(f"{addr_a} and {addr_b} must both be surfaces live at {rev}")
    rejected = model.setdefault("rejectedPairs", [])
    if not any(frozenset(r["keys"]) == frozenset((ka, kb)) for r in rejected):
        rejected.append({"keys": [ka, kb], "addresses": [addr_a, addr_b], "rev": rev, "by": by, "at": now(), "reason": reason})
    dropped = 0
    for row in model["surfaceRevs"]:
        if row["rev"] != rev:
            continue
        other = kb if row["surface"] == ka else ka if row["surface"] == kb else None
        if other is None:
            continue
        keep = [a for a in row["adjacency"] if a["surface"] != other]
        dropped += len(row["adjacency"]) - len(keep)
        row["adjacency"] = keep
    for k in (ka, kb):
        wk = model["surfaces"][k].get("wall")
        still = [r for r in model["surfaceRevs"] if r["rev"] == rev and r["surface"] == k and r["adjacency"]]
        if wk and not still:
            model["surfaces"][k]["wall"] = None
    live_walls = {s.get("wall") for s in model["surfaces"].values() if s.get("wall")}
    for wk, row in model["walls"].items():
        if row["retiredIn"] is None and wk not in live_walls:
            retire(model, wk, rev)
    return {"keys": [ka, kb], "adjacencyDropped": dropped}
