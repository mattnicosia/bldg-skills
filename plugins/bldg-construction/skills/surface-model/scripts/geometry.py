"""
geometry.py -- feet, walks, polygons.

Everything the model knows about shape comes from dimension strings a person read off
the drawings (or a prefill drafted from the text layer and then confirmed). This module
turns an ordered list of edges into points, checks the walk closes, computes areas, and
measures how much two outlines overlap. Nothing here reads a PDF or scales an image.
"""
from __future__ import annotations

import math
import re
from typing import Iterable, Sequence

# heading of travel (clockwise walk) -> outward normal of the face on the right
NORMAL_FOR_HEADING = {"E": "N", "S": "E", "W": "S", "N": "W"}
VEC = {"E": (1.0, 0.0), "S": (0.0, -1.0), "W": (-1.0, 0.0), "N": (0.0, 1.0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

_DIM_RE = re.compile(
    r"""^\s*(?:(?P<ft>\d+(?:\.\d+)?)\s*'?\s*)?        # feet (optional)
         (?:-\s*)?
         (?:(?P<inch>\d+(?:\.\d+)?)\s*
            (?:\s+(?P<num>\d+)\s*/\s*(?P<den>\d+))?\s*"?)?\s*$""",
    re.X,
)


def parse_feet(value) -> float:
    """'33'-0"' -> 33.0; '15'-6"' -> 15.5; '10'-4 1/2"' -> 10.375; 22 -> 22.0; '22.5' -> 22.5."""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace("’", "'").replace("”", '"').replace("″", '"').replace("′", "'")
    if re.match(r"^\d+(\.\d+)?$", s):
        return float(s)
    m = _DIM_RE.match(s)
    if not m or (m.group("ft") is None and m.group("inch") is None):
        raise ValueError(f"cannot read a length from {value!r}")
    ft = float(m.group("ft") or 0)
    inch = float(m.group("inch") or 0)
    if m.group("num"):
        inch += float(m.group("num")) / float(m.group("den"))
    if "'" not in s and '"' in s and m.group("ft") and m.group("inch") is None:
        # a bare inches string like 6"
        return ft / 12.0
    return ft + inch / 12.0


def feet_text(v: float) -> str:
    """33.5 -> 33'-6"."""
    ft = int(math.floor(v + 1e-9))
    inch = (v - ft) * 12
    if abs(inch - round(inch)) < 1e-6:
        return f"{ft}'-{int(round(inch))}\""
    return f"{ft}'-{inch:.2f}\""


def walk(anchor: Sequence[float], edges: Iterable[dict]) -> dict:
    """
    Walk edges clockwise from the anchor (the north-west corner).

    Each edge: {"heading": "E"|"S"|"W"|"N", "length": <feet or dimension string>, ...}.
    Consecutive edges with the same heading are one straight run and become one face.

    Returns {"points": [[x,y],...], "faces": [...], "closureErrorIn": float, "closed": bool}
    where each face carries heading, normal, lengthFt, parts (the strings it was summed
    from), start and end points.
    """
    x, y = float(anchor[0]), float(anchor[1])
    pts = [[x, y]]
    faces: list[dict] = []
    for e in edges:
        h = str(e["heading"]).upper()
        if h not in VEC:
            raise ValueError(f"edge heading {h!r} is not N, E, S or W")
        length = parse_feet(e["length"])
        dx, dy = VEC[h]
        part = {"text": str(e["length"]), "lengthFt": length, "source": e.get("source"),
                "confidence": e.get("confidence", "HIGH" if e.get("source") else "LOW")}
        if faces and faces[-1]["heading"] == h:
            f = faces[-1]
            f["lengthFt"] += length
            f["parts"].append(part)
        else:
            faces.append({"heading": h, "normal": NORMAL_FOR_HEADING[h], "lengthFt": length,
                          "parts": [part], "start": [x, y]})
        x, y = x + dx * length, y + dy * length
        faces[-1]["end"] = [x, y]
        pts.append([x, y])
    err_ft = math.hypot(x - pts[0][0], y - pts[0][1])
    closed = err_ft * 12 <= 1.0
    # A closed walk's last point repeats the first; drop it for polygon work.
    poly = pts[:-1] if closed and len(pts) > 1 else pts
    return {"points": poly, "faces": faces, "closureErrorIn": round(err_ft * 12, 3), "closed": closed}


def assign_ordinals(faces: list[dict]) -> None:
    """N1, N2 when a space has two faces that point the same way; in walk order."""
    counts: dict[str, int] = {}
    for f in faces:
        counts[f["normal"]] = counts.get(f["normal"], 0) + 1
    seen: dict[str, int] = {}
    for f in faces:
        n = f["normal"]
        if counts[n] > 1:
            seen[n] = seen.get(n, 0) + 1
            f["ordinal"] = seen[n]
            f["face"] = f"{n}{seen[n]}"
        else:
            f["ordinal"] = None
            f["face"] = n


def area(points: Sequence[Sequence[float]]) -> float:
    """Shoelace, absolute, square feet."""
    if len(points) < 3:
        return 0.0
    s = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def bbox(points: Sequence[Sequence[float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def point_in_polygon(x: float, y: float, poly: Sequence[Sequence[float]]) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xcross = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xcross:
                inside = not inside
        j = i
    return inside


def overlap_area(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]], cell: float = 0.25) -> float:
    """Area shared by two outlines, by counting cells. Good to a few square inches."""
    if len(a) < 3 or len(b) < 3:
        return 0.0
    ax0, ay0, ax1, ay1 = bbox(a)
    bx0, by0, bx1, by1 = bbox(b)
    x0, y0, x1, y1 = max(ax0, bx0), max(ay0, by0), min(ax1, bx1), min(ay1, by1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    nx = max(1, int(math.ceil((x1 - x0) / cell)))
    ny = max(1, int(math.ceil((y1 - y0) / cell)))
    hits = 0
    for i in range(nx):
        cx = x0 + (i + 0.5) * cell
        for j in range(ny):
            cy = y0 + (j + 0.5) * cell
            if point_in_polygon(cx, cy, a) and point_in_polygon(cx, cy, b):
                hits += 1
    return hits * cell * cell


def same_outline(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]], tol_ft: float = 0.05) -> bool:
    if len(a) != len(b):
        return False
    return all(abs(p[0] - q[0]) <= tol_ft and abs(p[1] - q[1]) <= tol_ft for p, q in zip(a, b))


# ---------------------------------------------------------------------------
# Faces as line segments: collinear overlap tests for adjacency and revision matching
# ---------------------------------------------------------------------------
def _axis(face: dict) -> str:
    return "x" if face["normal"] in ("N", "S") else "y"


def face_line(face: dict) -> tuple[float, float, float]:
    """(position across, start along, end along) for an axis-aligned face."""
    (x1, y1), (x2, y2) = face["start"], face["end"]
    if _axis(face) == "x":
        return y1, min(x1, x2), max(x1, x2)
    return x1, min(y1, y2), max(y1, y2)


def along_overlap(f1: dict, f2: dict) -> tuple[float, float] | None:
    """The shared span along two parallel faces, or None."""
    if _axis(f1) != _axis(f2):
        return None
    _, a0, a1 = face_line(f1)
    _, b0, b1 = face_line(f2)
    lo, hi = max(a0, b0), min(a1, b1)
    if hi - lo <= 0.25:
        return None
    return lo, hi


def back_to_back(f1: dict, f2: dict, f2_is_exterior: bool, wall_tol_ft: float) -> tuple[float, float] | None:
    """
    Are these two faces the two sides of one wall?

    f1 is an interior face. Its wall sits just beyond it in the direction of its normal.
    f2 is either an interior face whose normal points the other way, or an exterior face
    whose normal points the same way (the outside of the same wall).
    Returns the shared span along the wall, or None.
    """
    if _axis(f1) != _axis(f2):
        return None
    n1 = f1["normal"]
    if f2_is_exterior:
        if f2["normal"] != n1:
            return None
    elif f2["normal"] != OPPOSITE[n1]:
        return None
    p1, _, _ = face_line(f1)
    p2, _, _ = face_line(f2)
    sign = 1.0 if n1 in ("N", "E") else -1.0
    gap = (p2 - p1) * sign
    if gap <= 0 or gap > wall_tol_ft:
        return None
    return along_overlap(f1, f2)


def face_span_from_left(face: dict, lo: float, hi: float) -> tuple[float, float]:
    """
    Express an absolute span along the face as feet from the left end, standing in
    the space and facing the wall. Facing N, left is west (low x). Facing S, left is
    east (high x). Facing E, left is north (high y). Facing W, left is south (low y).
    """
    _, a0, a1 = face_line(face)
    n = face["normal"]
    if n in ("N", "W"):
        return round(lo - a0, 3), round(hi - a0, 3)
    return round(a1 - hi, 3), round(a1 - lo, 3)
