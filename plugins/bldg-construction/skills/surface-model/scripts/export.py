"""
export.py -- what other skills and BLDG OS read.

  roofs.json      the roof planes alone: elevation, spot height, pitch, outline.
  surfaces.json   every live space and surface at a revision, with keys, addresses,
                  level elevations, outlines and face segments in plan feet. The
                  proposal kit's click layer and the OS Model tab read this. The key is
                  the tag to put on the mesh (`[el:sk_12]`). `lineage` holds every
                  carry, split, merge and retire up to that revision, each with its
                  `rev`, so a reader can tell what happened to a pinned key.
                  `changes` is report.change_list from the revision before to this
                  one, or null for the first revision.
The kit's massing.json is written from this file by
drawings-to-massing/scripts/massing_from_surfaces.py, the one massing writer.

Nothing here holds a quantity the model did not read off a sheet.
"""
from __future__ import annotations

from report import change_list
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
                       "spotFt": (s.get("spotFt") or {}).get("value"), "pitch": (s.get("pitch") or {}).get("value"),
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
            "spaces": spaces, "surfaces": surfaces, "lineage": lineage_export(model, rev),
            "changes": changes_export(model, rev)}


def changes_export(model: dict, rev: str) -> dict | None:
    """The change list from the revision before `rev`, or None when `rev` is the first."""
    i = rev_index(model, rev)
    return change_list(model, model["revisions"][i - 1]["id"], rev) if i else None


def lineage_export(model: dict, rev: str) -> list[dict]:
    """Every lineage event at or before `rev`, in the shapes model-schema.md gives.

    A model saved before lineage existed has no `lineage` key and exports an empty list."""
    upto = rev_index(model, rev)
    return [dict(e) for e in model.get("lineage", []) if rev_index(model, e["rev"]) <= upto]


def roofs_export(model: dict, rev: str) -> dict:
    """Roof planes only: elevation, spot height and pitch with their sources, and the outline."""
    out = []
    for s in surfaces_export(model, rev)["spaces"]:
        if s["kind"] != "roof":
            continue
        row = next(r for r in live_spaces(model, rev) if r["space"] == s["key"])
        out.append({**{k: s[k] for k in ("key", "address", "level", "elevationFt", "elevationSource", "spotFt", "pitch", "outline", "areaSf", "wasAddress")},
                    "spotSource": (row.get("spotFt") or {}).get("source"), "pitchSource": (row.get("pitch") or {}).get("source")})
    return {"job": model["job"], "rev": rev, "roofs": out}


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
