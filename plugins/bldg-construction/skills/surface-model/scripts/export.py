"""
export.py -- what other skills and BLDG OS read.

  surfaces.json   every live space and surface at a revision, with keys, addresses,
                  level elevations, outlines and face segments in plan feet. The
                  proposal kit's click layer and the OS Model tab read this. The key is
                  the tag to put on the mesh (`[el:sk_12]`).
The kit's massing.json is written from this file by
drawings-to-massing/scripts/massing_from_surfaces.py, the one massing writer.

Nothing here holds a quantity the model did not read off a sheet.
"""
from __future__ import annotations

from store import live_spaces, live_surfaces, rev_index


def level_elevation(model: dict, rev: str, level: str):
    r = model["revisions"][rev_index(model, rev)]
    lv = (r.get("levels") or {}).get(level) or {}
    el = lv.get("elevationFt") or {}
    return el.get("value")


def surfaces_export(model: dict, rev: str) -> dict:
    spaces = []
    for s in live_spaces(model, rev):
        spaces.append({"key": s["space"], "address": s["address"], "level": s["level"], "kind": s["kind"],
                       "name": (s.get("name") or {}).get("value"), "number": (s.get("printedNumber") or {}).get("value"),
                       "elevationFt": ((s.get("elevationFt") or {}).get("value")
                                       if (s.get("elevationFt") or {}).get("value") is not None
                                       else level_elevation(model, rev, s["level"])),
                       "elevationSource": (s.get("elevationFt") or {}).get("source") or f"{s['level']} level marker",
                       "outline": (s.get("outline") or {}).get("points"), "areaSf": s.get("areaSf"),
                       "ceilingFt": (s.get("ceilingFt") or {}).get("value"), "phase": s.get("phase"),
                       "wasAddress": _was(model, s["space"], rev)})
    surfaces = []
    for s in live_surfaces(model, rev):
        surfaces.append({"key": s["surface"], "address": s["address"], "host": s["host"], "kind": s["kind"],
                         "face": s["face"], "direction": s.get("direction"), "ordinal": s.get("ordinal"),
                         "wall": model["surfaces"][s["surface"]].get("wall"),
                         "lengthFt": (s.get("lengthFt") or {}).get("value"),
                         "heightFt": (s.get("heightFt") or {}).get("value"),
                         "areaSf": s.get("areaSf"), "seg": s.get("seg"), "poly": s.get("poly"),
                         "confidence": _conf(s), "runs": s.get("runs", []), "finish": (s.get("finish") or {}).get("value"),
                         "adjacency": s.get("adjacency", []), "wasAddress": _was(model, s["surface"], rev)})
    return {"job": model["job"], "rev": rev, "north": model.get("north"),
            "levels": model["revisions"][rev_index(model, rev)].get("levels", {}),
            "spaces": spaces, "surfaces": surfaces}


def _conf(s: dict) -> str:
    vals = [(s.get("lengthFt") or {}).get("confidence"), (s.get("heightFt") or {}).get("confidence")]
    vals = [v for v in vals if v]
    order = ["NOT_MEASURED", "LOW", "MEDIUM", "HIGH", "VERIFIED"]
    return min(vals, key=order.index) if vals else "HIGH"


def _was(model: dict, key: str, rev: str) -> str | None:
    """The address this key had before the last readdress, for the card's 'was' line."""
    table, field = ("spaceRevs", "space") if key.startswith("sp") else ("surfaceRevs", "surface")
    rows = sorted((r for r in model[table] if r[field] == key), key=lambda r: rev_index(model, r["rev"]))
    rows = [r for r in rows if rev_index(model, r["rev"]) <= rev_index(model, rev)]
    if len(rows) >= 2 and rows[-1]["address"] != rows[-2]["address"]:
        return f"{rows[-2]['address']} ({rows[-2]['rev']})"
    return None
