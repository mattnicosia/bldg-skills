#!/usr/bin/env python3
"""
massing_from_surfaces.py -- the Bid Presentation Kit's massing.json from a job's surface model.

  python3 -I scripts/massing_from_surfaces.py surfaces.json --out massing.json [--keep last_massing.json]

Reads surfaces.json, the file surface-model writes with
`sm.py export <job>/surface-model.json --what surfaces`, and writes the kit's massing
contract (kit/README.md, section "massing.json"):

  volumes   one per exterior outline per level. base is the level's elevation; top is base
            plus the exterior faces' height, or the level's story height, or the next level
            up. "el" is the exterior space key (sp_N). "surfaces" maps each face (N, E, S, W,
            N1, N2 ...) to its surface key (sk_N), so a build that splits a volume into face
            meshes can tag each one [el:sk_N] the way the kit's build_el pattern does.
  flats     one per roof plane, drawn at the plane's elevation in the roof material, "el" the
            roof space key and "surface" its TOP key. A space that sits outside the exterior
            outline on its level (a deck, a porch) is a flat too, at that level's elevation.
  spaces    interior footprints with their keys and face keys, for a later click layer. The
            kit ignores this list today.
  _phases   the phase list to paste into project.json, in build order.
  _notes    where each height came from, what was assumed, and what a person should check.

Phases follow the level: a level below grade is `foundation`, a level at or above grade is
`house`, a roof plane is `roof`. Elevation skins, windows, trees and site paving stay hand
steps; pass --keep with the job's last massing.json and they carry over, along with any
volume or flat that has no "el" (one a person added by hand).

The file is for a picture. It carries no areas and no lengths, and nothing in it is a
quantity. Stdlib only. Run with `python3 -I`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

CONF_ORDER = ["NOT_MEASURED", "LOW", "MEDIUM", "HIGH", "VERIFIED"]
DEFAULT_STORY_FT = 10.0
ROOF_LIFT_FT = 0.02        # a flat drawn a hair above the volume's top, so the two do not fight
MATCH_TOL_FT = 0.1         # two outlines are the same outline within this

PLATFORM_MATERIALS = [
    (("DECK", "PORCH", "TERRACE", "BALCONY"), "cedar"),
    (("POOL", "POND"), "water"),
    (("LAWN", "GARDEN"), "lawn"),
]


# ---------------------------------------------------------------------------
# small geometry
# ---------------------------------------------------------------------------
def rnd(v, places: int = 2):
    return None if v is None else round(float(v) + 0.0, places)


def rnd_pts(pts):
    return [[rnd(x), rnd(y)] for x, y in pts]


def point_in_polygon(x: float, y: float, poly) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                inside = not inside
    return inside


def centroid(pts) -> tuple[float, float]:
    """The area centroid (shoelace); the corner mean when the outline has no area."""
    a = cx = cy = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        a += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(a) < 1e-9:
        return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    return (cx / (3 * a), cy / (3 * a))


def outline_inside(inner, outer) -> bool:
    """True when the inner outline's centroid sits inside the outer outline.

    A room that abuts the exterior wall shares corners with the outline, so corners do not
    decide; the centroid does. A deck or porch outside the wall has its centroid outside."""
    if not inner or not outer:
        return False
    x, y = centroid(inner)
    return point_in_polygon(x, y, outer)


def same_outline(a, b, tol: float = MATCH_TOL_FT) -> bool:
    if not a or not b or len(a) != len(b):
        return False
    key = lambda p: (round(p[0] / tol), round(p[1] / tol))  # noqa: E731
    return sorted(map(key, a)) == sorted(map(key, b))


def min_conf(values) -> str | None:
    vals = [v for v in values if v in CONF_ORDER]
    return min(vals, key=CONF_ORDER.index) if vals else None


def cited(entry) -> tuple:
    """(value, source, confidence) from a cited value, or (None, None, None)."""
    if not isinstance(entry, dict):
        return (None, None, None)
    return (entry.get("value"), entry.get("source"), entry.get("confidence"))


# ---------------------------------------------------------------------------
# the build
# ---------------------------------------------------------------------------
def build(sx: dict, keep: dict | None = None, src_name: str = "surfaces.json") -> tuple[dict, list[str]]:
    levels = sx.get("levels") or {}
    spaces = sx.get("spaces") or []
    surfaces = sx.get("surfaces") or []
    notes: list[str] = []
    report: list[str] = []

    by_host: dict[str, list[dict]] = {}
    for s in surfaces:
        by_host.setdefault(s.get("host"), []).append(s)

    def level_elev(level: str):
        return cited((levels.get(level) or {}).get("elevationFt"))

    elev = {k: level_elev(k) for k in levels}
    ordered = sorted((k for k in elev if elev[k][0] is not None), key=lambda k: elev[k][0])

    def phase_for(level: str, base: float, kind: str) -> str:
        if kind == "roof" or level == "RF":
            return "roof"
        return "foundation" if base < 0 else "house"

    def face_key_map(host: str, kinds: tuple) -> dict:
        out = {}
        for s in by_host.get(host, []):
            if s.get("kind") in kinds and s.get("face"):
                out[s["face"]] = s["key"]
        return out

    # ---- volumes: one per exterior outline per level
    volumes = []
    vol_by_key: dict[str, dict] = {}
    for sp in spaces:
        if sp.get("kind") != "exterior" or not sp.get("outline"):
            continue
        level = sp["level"]
        base, base_src, base_conf = sp.get("elevationFt"), None, None
        if base is None:
            base, base_src, base_conf = elev.get(level, (None, None, None))
        else:
            _, base_src, base_conf = elev.get(level, (None, None, None))
        if base is None:
            base, base_src, base_conf = 0.0, "assumed: no level marker in the model", "LOW"
            notes.append(f"{sp['address']}: no elevation for {level}; drawn at grade. Mark LOW until a level marker is read.")

        faces = [s for s in by_host.get(sp["key"], []) if s.get("kind") == "exterior_face"]
        heights = [s.get("heightFt") for s in faces if s.get("heightFt") is not None]
        conf = min_conf(s.get("confidence") for s in faces) or "HIGH"
        if heights:
            height, h_src = max(heights), "the exterior faces' height"
        else:
            story, story_src, story_conf = cited((levels.get(level) or {}).get("storyFt"))
            if story is not None:
                height, h_src = story, f"{level} story height ({story_src})"
                conf = min_conf([conf, story_conf]) or conf
            elif level in ordered and ordered.index(level) + 1 < len(ordered):
                nxt = ordered[ordered.index(level) + 1]
                height, h_src = elev[nxt][0] - base, f"the next level up ({nxt} at {elev[nxt][0]} ft)"
                conf = min_conf([conf, elev[nxt][2]]) or conf
            else:
                height, h_src, conf = DEFAULT_STORY_FT, "assumed: nothing in the model gives this level a height", "LOW"
                notes.append(f"{sp['address']}: no face height, story height or next level; drawn {DEFAULT_STORY_FT} ft tall. LOW.")
        if height <= 0:
            notes.append(f"{sp['address']}: height came out {height} ft from {h_src}; drawn {DEFAULT_STORY_FT} ft tall instead. Check the level markers.")
            height, conf = DEFAULT_STORY_FT, "LOW"

        top = base + height
        phase = phase_for(level, base, "exterior")
        v = {
            "name": sp["address"],
            "el": sp["key"],
            "footprint": rnd_pts(sp["outline"]),
            "base": rnd(base),
            "top": rnd(top),
            "phase": phase,
            "material": "concrete" if phase == "foundation" else "paper",
            "roof": {"type": "flat"},
            "surfaces": face_key_map(sp["key"], ("exterior_face",)),
            "_confidence": conf,
        }
        if phase == "foundation":
            v["skin"] = False
            v["coping"] = False
        volumes.append(v)
        vol_by_key[sp["key"]] = v
        report.append(f"volume {sp['address']:10} {sp['key']:6} base {v['base']} ({base_src}, {base_conf}); top {v['top']}, height from {h_src} ({conf}); phase {phase}")

    if not volumes:
        notes.append("No exterior outline in the model. Nothing to draw; add the EXT walks to the readings first.")

    # ---- roof planes as flats
    flats = []
    for sp in spaces:
        if sp.get("kind") != "roof" or not sp.get("outline"):
            continue
        top_sf = next((s for s in by_host.get(sp["key"], []) if s.get("kind") == "roof"), None)
        y, y_src, y_conf = sp.get("elevationFt"), None, None
        if y is None:
            y, y_src, y_conf = elev.get(sp["level"], (None, None, None))
        else:
            _, y_src, y_conf = elev.get(sp["level"], (None, None, None))
        placed = f"{sp['level']} level ({y_src}, {y_conf})"
        # the roof plane covers the topmost volume with its outline
        matches = [v for v in volumes if same_outline(sp["outline"], [tuple(p) for p in v["footprint"]])]
        match = max(matches, key=lambda v: v["top"]) if matches else None
        if match is not None:
            if y is None or abs(match["top"] - y) > MATCH_TOL_FT:
                notes.append(
                    f"{sp['address']}: same outline as {match['name']}, whose top is {match['top']} ft, but the model puts it at "
                    f"{y} ft. Drawn on {match['name']}'s top. Check the roof's elevationFt in the readings against the sections.")
                y, placed = match["top"], f"the top of {match['name']} (outline match)"
        if y is None:
            y, placed = (volumes[-1]["top"] if volumes else DEFAULT_STORY_FT), "assumed: no roof elevation in the model"
            notes.append(f"{sp['address']}: no elevation; drawn at {y} ft. LOW.")
        f = {
            "name": sp["address"],
            "el": sp["key"],
            "polygon": rnd_pts(sp["outline"]),
            "y": rnd(y + ROOF_LIFT_FT),
            "material": "roof",
            "phase": "roof",
            "_confidence": min_conf([(top_sf or {}).get("confidence"), y_conf]) or "HIGH",
        }
        if top_sf:
            f["surface"] = top_sf["key"]
        flats.append(f)
        report.append(f"roof   {sp['address']:10} {sp['key']:6} at {f['y']} ft, placed from {placed}")

    # ---- interior spaces, and spaces outside the outline (decks, porches)
    ext_by_level: dict[str, list] = {}
    for sp in spaces:
        if sp.get("kind") == "exterior" and sp.get("outline"):
            ext_by_level.setdefault(sp["level"], []).append(sp["outline"])

    interior = []
    unplaced = []
    for sp in spaces:
        kind = sp.get("kind")
        if kind in ("exterior", "roof"):
            continue
        if not sp.get("outline"):
            unplaced.append({"key": sp["key"], "address": sp["address"], "name": sp.get("name"), "level": sp.get("level"), "kind": kind})
            continue
        level = sp["level"]
        base = sp.get("elevationFt")
        if base is None:
            base = elev.get(level, (0.0, None, None))[0]
        if base is None:
            base = 0.0
        inside = any(outline_inside(sp["outline"], ext) for ext in ext_by_level.get(level, []))
        face_keys = face_key_map(sp["key"], ("wall_face", "floor", "ceiling"))
        if inside:
            ceiling = sp.get("ceilingFt")
            interior.append({
                "key": sp["key"], "address": sp["address"], "name": sp.get("name"), "level": level,
                "footprint": rnd_pts(sp["outline"]), "base": rnd(base),
                "top": rnd(base + ceiling) if ceiling is not None else None,
                "phase": phase_for(level, base, kind), "surfaces": face_keys,
            })
            if ceiling is None:
                notes.append(f"{sp['address']}: no ceiling height; the click footprint has no top.")
        else:
            name = (sp.get("name") or sp["address"]).upper()
            material = next((m for words, m in PLATFORM_MATERIALS if any(w in name for w in words)), "paving")
            f = {
                "name": sp["address"], "el": sp["key"], "polygon": rnd_pts(sp["outline"]),
                "y": rnd(base + ROOF_LIFT_FT), "material": material, "phase": phase_for(level, base, kind),
                "_confidence": "HIGH",
            }
            if "FLR" in face_keys:
                f["surface"] = face_keys["FLR"]
            flats.append(f)
            report.append(f"flat   {sp['address']:10} {sp['key']:6} outside {level}'s outline; drawn at {f['y']} ft as {material}")

    if unplaced:
        notes.append(
            f"{len(unplaced)} host(s) have a key and no outline ({', '.join(u['address'] for u in unplaced)}). "
            "Add each by hand as a flat or volume if the picture needs it, and keep its key as \"el\".")

    # ---- carry the hand work over from the last massing.json
    kept_volumes, kept_flats = [], []
    out: dict = {"units": "ft"}
    if keep:
        for k in ("note", "elevations", "windows", "trees"):
            if k in keep:
                out[k] = keep[k]
        kept_volumes = [v for v in keep.get("volumes", []) if not v.get("el")]
        kept_flats = [f for f in keep.get("flats", []) if not f.get("el")]
        if kept_volumes or kept_flats or any(k in keep for k in ("elevations", "windows", "trees")):
            report.append(
                f"kept from the last massing.json: {len(kept_volumes)} hand volume(s), {len(kept_flats)} hand flat(s), "
                + ", ".join(k for k in ("elevations", "windows", "trees") if k in keep))

    out["volumes"] = volumes + kept_volumes
    out["flats"] = flats + kept_flats
    out.setdefault("trees", [])
    out["spaces"] = interior
    if unplaced:
        out["_unplaced"] = unplaced

    present = {v["phase"] for v in out["volumes"]} | {f.get("phase") for f in out["flats"] if f.get("phase")}
    order = ["foundation", "house", "roof", "envelope", "hardscape"]
    labels = {"foundation": "Foundation", "house": "House", "roof": "Roof", "envelope": "Envelope", "hardscape": "Hardscape"}
    phases = [{"id": p, "label": labels[p]} for p in order if p in present]
    phases += [{"id": p, "label": p.title()} for p in sorted(present) if p not in order]
    out["_phases"] = phases
    if "foundation" not in present:
        notes.append("No level below grade in the model, so there is no foundation phase. Add one by hand if the reveal should start below grade.")

    notes.append("Roofs are drawn flat. A gable, shed or hip is a hand edit to the volume's \"roof\" (kit README, massing.json).")
    notes.append("This file is for a picture. It carries no areas and no lengths; never pull a quantity from it.")
    out["_notes"] = notes
    out["_from"] = {"job": sx.get("job"), "rev": sx.get("rev"), "surfaces": src_name, "script": "drawings-to-massing/scripts/massing_from_surfaces.py"}
    return out, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="massing_from_surfaces.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("surfaces", help="surfaces.json from `sm.py export --what surfaces`")
    ap.add_argument("--out", required=True, help="where to write massing.json")
    ap.add_argument("--keep", help="the job's last massing.json; its skins, windows, trees and hand-added shapes carry over")
    ap.add_argument("--quiet", action="store_true", help="write the file and say nothing else")
    a = ap.parse_args(argv)

    with open(a.surfaces, encoding="utf-8") as f:
        sx = json.load(f)
    if "spaces" not in sx or "surfaces" not in sx:
        sys.exit(f"{a.surfaces} is not a surfaces export (no spaces or surfaces list). Run `sm.py export --what surfaces` first.")
    keep = None
    if a.keep:
        with open(a.keep, encoding="utf-8") as f:
            keep = json.load(f)

    out, report = build(sx, keep, os.path.basename(a.surfaces))
    tmp = a.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    os.replace(tmp, a.out)

    if not a.quiet:
        print(f"{out['_from']['job']} at {out['_from']['rev']}: {len(out['volumes'])} volumes, {len(out['flats'])} flats, {len(out['spaces'])} interior spaces")
        for line in report:
            print("  " + line)
        print("phases: " + ", ".join(p["id"] for p in out["_phases"]))
        print("check:")
        for n in out["_notes"]:
            print("  - " + n)
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
