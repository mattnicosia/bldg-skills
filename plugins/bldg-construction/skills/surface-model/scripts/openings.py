"""
openings.py -- windows, doors, sliders and garage doors in the faces that hold them.

An opening sits in one face. The readings name that face the way the address does
(level, host, face), and give the tag, the center along the face, the width, the sill
and the head, each with its sheet. The center runs from the face's first point, `seg[0]`,
which is the left end as you stand inside facing the wall. Sill and head are feet above
the floor of the opening's level.

An opening gets an `op_` key on first sight. On a reissue it carries when the new reading
sits in a face the old face carried, split or merged into, has the same tag, and its
center lies within one foot of the old one in plan. Otherwise the old key retires and a
new one is minted. The change list reports an opening that was added, removed, or
resized (a width, sill or head change).
"""
from __future__ import annotations

import math

from store import live_openings, mint, opening_at, retire, rev_index

KINDS = ("window", "door", "slider", "garage")
CARRY_FT = 1.0
FIT_TOL_FT = 0.01


def _val(v):
    return v.get("value") if isinstance(v, dict) else v


def _ft(v: float) -> str:
    v = round(float(v), 1)
    return str(int(v)) if v.is_integer() else f"{v:g}"


def read(readings: dict, cands: list[dict], cited) -> tuple[list[dict], list[str]]:
    """Each reading checked against the face it names. An opening whose center and width
    do not fit inside that face is a refusal, as is a face that does not exist."""
    faces = {}
    for c in cands:
        for f in (c.get("outline") or {}).get("faces", []):
            faces[f"{c['level']}/{c['handle']}/{f['face']}"] = f
    out, problems = [], []
    for e in readings.get("openings", []):
        level, host, face = str(e.get("level", "")).upper(), str(e.get("host", "")).upper(), str(e.get("face", "")).upper()
        where = f"{level}/{host}/{face}"
        tag = cited(e.get("tag")) if e.get("tag") is not None else None
        name = f"opening {_val(tag) or '?'} on {where}"
        if e.get("kind") not in KINDS:
            problems.append(f"{name}: kind {e.get('kind')!r} is not one of {', '.join(KINDS)}")
            continue
        if tag is None or not _val(tag):
            problems.append(f"{name}: no tag")
            continue
        f = faces.get(where)
        if f is None:
            problems.append(f"{name}: no such face in the readings")
            continue
        center, width = cited(e.get("centerFt")), cited(e.get("widthFt"))
        if _val(center) is None or _val(width) is None:
            problems.append(f"{name}: center and width are both needed to place it")
            continue
        c, w, length = float(_val(center)), float(_val(width)), f["lengthFt"]
        if c - w / 2 < -FIT_TOL_FT or c + w / 2 > length + FIT_TOL_FT:
            problems.append(f"{name}: {w:g} ft wide at {c:g} ft does not fit in the {length:.3f} ft face")
            continue
        (x0, y0), (x1, y1) = f["start"], f["end"]
        out.append({"level": level, "host": host, "face": face, "faceAddress": where, "kind": e["kind"],
                    "tag": tag, "centerFt": center, "widthFt": width,
                    "sillFt": cited(e.get("sillFt")) if e.get("sillFt") is not None else None,
                    "headFt": cited(e.get("headFt")) if e.get("headFt") is not None else None,
                    "leaves": int(e.get("leaves", 1)),
                    "unit": cited(e.get("unit")) if e.get("unit") is not None else None,
                    "at": [round(x0 + (x1 - x0) * c / length, 4), round(y0 + (y1 - y0) * c / length, 4)]})
    return out, problems


def address(o: dict) -> str:
    return f"{o['faceAddress']}/{_val(o['tag'])}@{_ft(_val(o['centerFt']))}"


def _row(key: str, rev: str, surface: str, o: dict) -> dict:
    return {"opening": key, "rev": rev, "address": address(o), "surface": surface, "level": o["level"],
            "kind": o["kind"], "tag": o["tag"], "centerFt": o["centerFt"], "widthFt": o["widthFt"],
            "sillFt": o["sillFt"], "headFt": o["headFt"], "leaves": o["leaves"], "unit": o["unit"], "at": o["at"]}


def mint_all(model: dict, rev: str, ops: list[dict], amap: dict[str, str]) -> int:
    """First revision: every opening gets a key in its face."""
    for o in ops:
        k = mint(model, "op", rev, kind=o["kind"])
        model.setdefault("openingRevs", []).append(_row(k, rev, amap[o["faceAddress"]], o))
    return len(ops)


def _successors(lineage: list[dict]) -> dict[str, set[str]]:
    succ: dict[str, set[str]] = {}
    for e in lineage:
        if e["kind"] == "retire":
            continue
        froms = e["from"] if isinstance(e["from"], list) else [e["from"]]
        tos = e["to"] if isinstance(e["to"], list) else [e["to"]]
        for f in froms:
            succ.setdefault(f, set()).update(tos)
    return succ


def carry(model: dict, prev: str, rev: str, ops: list[dict], amap: dict[str, str],
          lineage: list[dict], by: dict) -> dict:
    """A reissue. Faces have their lineage already; each old opening carries into a reading
    on a successor face with the same tag within a foot, or retires. The rest are minted."""
    succ = _successors(lineage)
    old = live_openings(model, prev)
    free = list(range(len(ops)))
    events: list[dict] = []
    for o in old:
        hosts = succ.get(o["surface"], set())
        best = None
        for i in free:
            n = ops[i]
            if amap.get(n["faceAddress"]) not in hosts or _val(n["tag"]) != _val(o["tag"]):
                continue
            d = math.dist(n["at"], o["at"])
            if d <= CARRY_FT and (best is None or d < best[1]):
                best = (i, d)
        if best is None:
            retire(model, o["opening"], rev)
            events.append({"kind": "retire", "from": o["opening"], "rev": rev, "by": by,
                           "reason": f"{o['address']}: no {_val(o['tag'])} within {CARRY_FT:g} ft on the same face in {rev}"})
            continue
        n = ops[best[0]]
        free.remove(best[0])
        row = _row(o["opening"], rev, amap[n["faceAddress"]], n)
        model["openingRevs"].append(row)
        events.append({"kind": "carry", "from": o["opening"], "to": o["opening"], "rev": rev, "by": by,
                       "readdressed": row["address"] != o["address"], "moved": best[1] > 0.005})
    minted = 0
    for i in free:
        k = mint(model, "op", rev, kind=ops[i]["kind"])
        model["openingRevs"].append(_row(k, rev, amap[ops[i]["faceAddress"]], ops[i]))
        minted += 1
    seen: dict[str, int] = {}
    for e in events:
        seen[e["from"]] = seen.get(e["from"], 0) + 1
    missing = [o["opening"] for o in old if seen.get(o["opening"]) != 1]
    if missing:
        raise SystemExit(f"openings not in exactly one event: {missing}; refusing")
    lineage.extend(events)
    return {"carried": sum(1 for e in events if e["kind"] == "carry"),
            "retired": sum(1 for e in events if e["kind"] == "retire"), "minted": minted}


def exported(c: dict | None) -> dict | None:
    """A cited value in the export shape: a NOT_MEASURED value is its confidence and reason."""
    if not c or c.get("confidence") != "NOT_MEASURED":
        return c
    return {"confidence": "NOT_MEASURED", "reason": c.get("reason") or c.get("source") or "not given on the set"}


def export_rows(model: dict, rev: str, was) -> list[dict]:
    out = []
    for o in live_openings(model, rev):
        row = {"key": o["opening"], "address": o["address"], "wasAddress": was(model, o["opening"], rev),
               "surface": o["surface"], "wall": model["surfaces"][o["surface"]].get("wall"),
               "level": o["level"], "kind": o["kind"], "leaves": o["leaves"],
               **{f: exported(o[f]) for f in ("tag", "centerFt", "widthFt", "sillFt", "headFt")}}
        if o.get("unit"):
            row["unit"] = exported(o["unit"])
        out.append(row)
    return out


SIZE = (("widthFt", "width"), ("sillFt", "sill"), ("headFt", "head"))


def change_rows(model: dict, rev_a: str, rev_b: str) -> list[dict]:
    """Openings added, removed or resized between two revisions, in the change-row shape.
    Length is the width; area is width times sill-to-head height."""
    ia, ib = rev_index(model, rev_a), rev_index(model, rev_b)
    rows = []
    for k, meta in model.get("openings", {}).items():
        minted = rev_index(model, meta["mintedIn"])
        gone = rev_index(model, meta["retiredIn"]) if meta["retiredIn"] else None
        b = opening_at(model, k, rev_a) if minted <= ia and (gone is None or gone > ia) else None
        a = opening_at(model, k, rev_b) if minted <= ib and (gone is None or gone > ib) else None
        if not b and not a:
            continue
        if b and a:
            changed = [label for f, label in SIZE if _val(b.get(f)) != _val(a.get(f))]
            if not changed:
                continue
            change, note = "changed", "resized: " + ", ".join(changed)
        else:
            change, note = ("added" if a else "removed"), None
        rows.append({"subject": "opening", "keys": [k], "kind": (a or b)["kind"],
                     "before": b["address"] if b else None, "after": a["address"] if a else None,
                     "lengthBefore": _num(b, "widthFt"), "lengthAfter": _num(a, "widthFt"),
                     "areaBefore": _area(b), "areaAfter": _area(a),
                     "deltaLengthFt": _delta(_num(b, "widthFt"), _num(a, "widthFt")),
                     "deltaAreaSf": _delta(_area(b), _area(a)),
                     "sillBefore": _num(b, "sillFt"), "sillAfter": _num(a, "sillFt"),
                     "headBefore": _num(b, "headFt"), "headAfter": _num(a, "headFt"),
                     "sources": sorted({(r.get(f) or {}).get("source") for r in (b, a) if r for f, _ in SIZE} - {None}),
                     "change": change, "note": note})
    order = {"changed": 0, "removed": 1, "added": 2}
    rows.sort(key=lambda r: (order[r["change"]], r["before"] or r["after"]))
    return rows


def _num(r, f):
    return None if not r else _val(r.get(f))


def _area(r):
    if not r:
        return None
    w, s, h = _num(r, "widthFt"), _num(r, "sillFt"), _num(r, "headFt")
    return None if None in (w, s, h) else round(w * (h - s), 2)


def _delta(a, b):
    return None if a is None and b is None else round((b or 0) - (a or 0), 3)
