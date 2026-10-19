"""
address.py -- the surface address grammar.

An address names a place on a job the way a PM says it: level, host, face, and
sometimes the assembly tag and a span along the face.

    L2/204/N          the north face of room 204 on level 2
    L2/204/N/W3       the W3 part of that face
    L2/204/N @6-12    six to twelve feet along it, from the left as you face it
    L2/204/FLR        its floor
    L2/CORR-1/S       an unnumbered corridor, south face
    L1/EXT/N          the building's north exterior face on level 1
    RF/MAIN/TOP       the main roof plane
    SITE/DRIVE        a site host with no faces
    L2/204+205        the wall core two rooms share (input only)
    L*/*/*/W3         a selector: every W3 face on the job

The parser also reads Matt's long form ("L2 / Rm 204 / North wall / W3") and writes
the canonical short form. `speak()` turns an address into words. Nothing here touches
a store; it is pure text.

Direction is the face's outward normal under project north, rounded to N, E, S or W.
An ordinal (N1, N2) appears only when a space has two faces that point the same way.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

LEVEL_RE = re.compile(r"^(L\d+[A-Z]?|B\d+|RF|MEZZ|SITE|\*|L\*|B\*)$", re.I)
DIRS = ("N", "E", "S", "W")
FACE_WORDS = {"FLR": "floor", "CLG": "ceiling", "TOP": "top"}
LONG_DIR = {"NORTH": "N", "EAST": "E", "SOUTH": "S", "WEST": "W"}


class AddressError(ValueError):
    pass


@dataclass
class Address:
    level: str
    host: str                      # "204", "CORR-1", "EXT", "DRIVE", "*"
    face: Optional[str] = None     # "N", "N2", "FLR", "CLG", "CLG2", "TOP", "*"
    assembly: Optional[str] = None # "W3"
    opposite: Optional[str] = None # input-only disambiguator, never stored
    span: Optional[tuple] = None   # (from_ft, to_ft)
    point: Optional[tuple] = None  # (along_ft, up_ft)
    core: Optional[tuple] = None   # ("204", "205") for a wall core
    raw: str = field(default="", repr=False)

    # -- derived -------------------------------------------------------------
    @property
    def is_selector(self) -> bool:
        parts = [self.level, self.host, self.face or "", self.assembly or ""]
        return any("*" in p for p in parts)

    @property
    def direction(self) -> Optional[str]:
        if self.face and self.face[0] in DIRS:
            return self.face[0]
        return None

    @property
    def ordinal(self) -> Optional[int]:
        if self.face and self.face[0] in DIRS and len(self.face) > 1 and self.face[1:].isdigit():
            return int(self.face[1:])
        return None

    def canonical(self) -> str:
        """The stored form. Drops :opposite, keeps assembly and locator."""
        if self.core:
            s = f"{self.level}/{self.core[0]}+{self.core[1]}"
            if self.assembly:
                s += f"/{self.assembly}"
            return s
        s = f"{self.level}/{self.host}"
        if self.face:
            s += f"/{self.face}"
        if self.assembly:
            s += f"/{self.assembly}"
        if self.span:
            s += f" @{_ft(self.span[0])}-{_ft(self.span[1])}"
        elif self.point:
            s += f" @{_ft(self.point[0])}+{_ft(self.point[1])}"
        return s

    def surface_key_text(self) -> str:
        """The part that names a surface: level/host/face. No locator, no assembly."""
        s = f"{self.level}/{self.host}"
        if self.face:
            s += f"/{self.face}"
        return s


def _ft(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
_LOCATOR_RE = re.compile(r"@\s*([\d.]+)\s*(?:-\s*([\d.]+)|\+\s*([\d.]+))?\s*$")


def parse(text: str) -> Address:
    """Read the canonical form, the long form, or a selector."""
    raw = text.strip()
    if not raw:
        raise AddressError("empty address")
    t = raw

    span = point = None
    m = _LOCATOR_RE.search(t)
    if m:
        a = float(m.group(1))
        if m.group(2) is not None:
            span = (a, float(m.group(2)))
        elif m.group(3) is not None:
            point = (a, float(m.group(3)))
        else:
            point = (a, 0.0)
        t = t[: m.start()].strip()

    parts = [p.strip() for p in t.split("/")]
    parts = [_normalize_part(p) for p in parts if p != ""]
    if not parts:
        raise AddressError(f"no segments in {raw!r}")

    level = parts[0].upper()
    if not LEVEL_RE.match(level):
        raise AddressError(f"{level!r} is not a level (L1, B1, RF, MEZZ, SITE, or *)")

    if len(parts) < 2:
        raise AddressError(f"{raw!r} names a level only; add the host")

    host = parts[1].upper()
    core = None
    if "+" in host and "*" not in host:
        a, b = host.split("+", 1)
        core = (a.strip(), b.strip())
        host = core[0]

    face = assembly = opposite = None
    if len(parts) >= 3 and not core:
        face = parts[2].upper()
        if ":" in face:
            face, opposite = face.split(":", 1)
        face = _normalize_face(face)
    elif len(parts) >= 3 and core:
        assembly = parts[2].upper()
    if len(parts) >= 4 and not core:
        assembly = parts[3].upper()
    if len(parts) > 4:
        raise AddressError(f"{raw!r} has too many segments")

    if face and face not in ("*",):
        _check_face(face, raw)

    return Address(level=level, host=host, face=face, assembly=assembly, opposite=opposite,
                   span=span, point=point, core=core, raw=raw)


def _normalize_part(p: str) -> str:
    """Long form to short: 'Rm 204' -> '204', 'North wall' -> 'N', 'Level 2' -> 'L2'."""
    s = p.strip()
    u = s.upper()
    m = re.match(r"^(?:LEVEL|LVL|FLOOR)\s*(\d+)$", u)
    if m:
        return f"L{m.group(1)}"
    m = re.match(r"^(?:BASEMENT|CELLAR)\s*(\d*)$", u)
    if m:
        return f"B{m.group(1) or 1}"
    if u in ("ROOF",):
        return "RF"
    m = re.match(r"^(?:RM|ROOM)\s*\.?\s*([A-Z0-9-]+)$", u)
    if m:
        return m.group(1)
    m = re.match(r"^(NORTH|EAST|SOUTH|WEST)\s*(?:WALL|FACE)?\s*(\d*)$", u)
    if m:
        return LONG_DIR[m.group(1)] + m.group(2)
    if u in ("FLOOR",):
        return "FLR"
    if u in ("CEILING", "CLG."):
        return "CLG"
    if u in ("EXTERIOR", "EXT."):
        return "EXT"
    return s


def _normalize_face(face: str) -> str:
    f = face.strip().upper()
    if f in ("FLOOR",):
        return "FLR"
    if f in ("CEILING",):
        return "CLG"
    return f


def _check_face(face: str, raw: str) -> None:
    if face in ("FLR", "TOP"):
        return
    if re.match(r"^CLG\d*$", face):
        return
    if re.match(r"^[NESW]\d*$", face):
        return
    if "*" in face:
        return
    raise AddressError(f"{face!r} in {raw!r} is not a face (N, E, S, W, N2, FLR, CLG, CLG2, TOP)")


# ---------------------------------------------------------------------------
# Matching a selector against a canonical surface address
# ---------------------------------------------------------------------------
def _seg_match(pattern: str, value: str) -> bool:
    if pattern == "*":
        return True
    if "*" not in pattern:
        return pattern.upper() == value.upper()
    rx = "^" + re.escape(pattern.upper()).replace(r"\*", ".*") + "$"
    return re.match(rx, value.upper()) is not None


def _list_match(pattern: str, value: str) -> bool:
    """A segment may hold a comma list: 'N,E,S,W'."""
    return any(_seg_match(p.strip(), value) for p in pattern.split(","))


def matches(selector: Address, surface_address: str, assembly_tags: Optional[list] = None) -> bool:
    """Does this selector pick the surface with this canonical address?"""
    target = parse(surface_address)
    if not _list_match(selector.level, target.level):
        return False
    if not _list_match(selector.host, target.host):
        return False
    if selector.face is None:
        # "L2/204" picks the space; it matches every face of it only when asked as L2/204/*
        return target.face is None
    if not _list_match(selector.face, target.face or ""):
        return False
    if selector.assembly:
        tags = [t.upper() for t in (assembly_tags or [])]
        if not any(_seg_match(selector.assembly, t) for t in tags):
            return False
    return True


# ---------------------------------------------------------------------------
# Speaking
# ---------------------------------------------------------------------------
def speak(text: str) -> str:
    a = parse(text)
    words = []
    if a.level == "SITE":
        words.append("Site")
    elif a.level == "RF":
        words.append("Roof")
    elif a.level.startswith("L"):
        words.append(f"Level {a.level[1:]}")
    elif a.level.startswith("B"):
        words.append(f"Basement {a.level[1:]}" if a.level != "B1" else "Basement")
    else:
        words.append(a.level)

    if a.core:
        words.append(f"the wall between {_host_words(a.core[0])} and {_host_words(a.core[1])}")
    else:
        words.append(_host_words(a.host))
        if a.face:
            words.append(_face_words(a.face))
    if a.assembly:
        words.append(f"the {a.assembly} part")
    if a.span:
        words.append(f"{_ft(a.span[0])} to {_ft(a.span[1])} feet from the left")
    elif a.point:
        words.append(f"{_ft(a.point[0])} feet along and {_ft(a.point[1])} feet up")
    return ", ".join(words)


def _host_words(h: str) -> str:
    if "*" in h:
        return "any space" if h == "*" else f"spaces {h}"
    if h == "EXT":
        return "exterior"
    if h.isdigit() or re.match(r"^\d+[A-Z]$", h):
        return f"Room {h}"
    m = re.match(r"^([A-Z]+)-(\d+)$", h)
    if m:
        return f"{m.group(1).title()} {m.group(2)}"
    return h.title()


def _face_words(f: str) -> str:
    if "*" in f:
        return "any face" if f == "*" else f"faces {f}"
    if f in FACE_WORDS:
        return FACE_WORDS[f]
    if f.startswith("CLG"):
        return f"ceiling {f[3:]}" if f[3:] else "ceiling"
    d = {"N": "north", "E": "east", "S": "south", "W": "west"}[f[0]]
    n = f[1:]
    return f"{d} wall {n}".strip() if n else f"{d} wall"


if __name__ == "__main__":  # a tiny self-check
    for t in ["L2/204/N", "L2 / Rm 204 / North wall / W3", "L2/204/N @6-12", "L2/CORR-1/S",
              "L1/EXT/N", "RF/MAIN/TOP", "SITE/DRIVE", "L2/204+205", "L*/*/*/W3", "L2/210/N:CORR-1"]:
        a = parse(t)
        print(f"{t:36} -> {a.canonical():22} selector={a.is_selector!s:5} | {speak(a.canonical())}")
