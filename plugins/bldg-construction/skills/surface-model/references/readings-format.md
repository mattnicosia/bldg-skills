# Readings format

One readings file per drawing issue. A person writes it from the dimension strings on
the plans, or confirms a draft `prefill.py` made from the text layer. `build.py` and
`revise.py` read it. Every length names its sheet. No length is measured off an image.

```json
{
 "job": "E26049",
 "revision": {"id": "SD-1", "label": "Schematic Design set", "date": "2026-09-12", "sheets": ["A-101", "A-301"]},
 "north": {"source": "A-101 north arrow", "confirmedBy": {"kind": "person", "id": "matt"}},
 "wallTolFt": 1.0,
 "levels": [
  {"id": "L1", "elevationFt": {"value": 0, "source": "A-301 level marker"},
   "ceilingFt": {"value": 11.6, "source": "A-301 section"}, "storyFt": {"value": 13.2, "source": "A-301 section"}}
 ],
 "exterior": [ { "level": "L1", "anchor": [0, 32.17], "edges": [ ... ], "heightFt": {...} } ],
 "spaces":   [ { "level": "L1", "number": "101", "name": "GREAT ROOM", "anchor": [0.5, 31.67], "edges": [ ... ] } ],
 "roofs":    [ { "level": "RF", "handle": "MAIN", "anchor": [0, 32.17], "edges": [ ... ] } ],
 "hosts":    [ { "level": "SITE", "handle": "DRIVE", "name": "DRIVEWAY", "source": "C-101" } ]
}
```

## Coordinates

Plan feet. x runs east, y runs north, under project north. One corner of the building
is the origin. `anchor` is the north-west corner of the outline, where the walk starts.
Anchors come from the grid offsets or the dimension strings; say which in
`anchorSource`. An anchor you placed by eye is marked that way and stays LOW until a
person confirms it.

## An outline is a walk

`edges` runs clockwise from the north-west corner. Each edge has a `heading` (the
direction you walk: E, S, W or N), a `length` (a dimension string as printed, `33'-0"`,
`15'-6"`, `10'-4 1/2"`, or a number in feet), and a `source` (the sheet, and the detail
where it helps). Consecutive edges with the same heading are partial dimensions along
one straight side; they become one face whose length is their sum.

The walk must return to the anchor within one inch. If it does not, the build refuses
the space and names the gap. Fix the edge, never the tolerance.

Each edge becomes one face. Walking clockwise, the outside is on your right, so an
edge walked east is the north face, south is the east face, west is the south face,
north is the west face. A space with two faces that point the same way (an L) gets N1
and N2 in walk order.

## Heights

`levels[].elevationFt` from the level markers on the sections. `levels[].ceilingFt` is
the default ceiling height for spaces on that level; a space can carry its own
`ceilingFt` from the RCP or the finish schedule. `levels[].storyFt` or an exterior's
`heightFt` sets exterior face height. A space with no height anywhere gets
`NOT_MEASURED` and its faces carry a length and no area.

## Spaces, exterior, roofs, hosts

| Block | What it is | Gets |
|---|---|---|
| `spaces` | a room, corridor, shaft, deck | wall faces, FLR, CLG |
| `exterior` | the building outline on a level, host `EXT` | exterior faces |
| `roofs` | a roof plane, level `RF` | one TOP surface |
| `hosts` | a thing with no faces: a site element, a room the set has not laid out yet | a space key only, so pins can land on it |

A host that gets an outline in a later issue carries its key; the faces are minted then.

## Naming

`number` is the printed room number when the set has one. Otherwise `handle` is the
plan's word (`GREAT`, `CORR-1`). Leave both out and the build mints the name's first
word plus an ordinal (`BATH-1`), once, and never frees it.

## Runs and finishes

```json
"runs": [{"face": "N", "assembly": {"value": "W3", "source": "A-101"}, "from": 0, "to": 12}],
"finishes": {"N": {"value": "PT-1", "source": "A-601"}, "FLR": {"value": "WD-1", "source": "A-601"}}
```

Feet along a face run from the left end as you stand in the space facing the wall.
Both are stored as printed and never normalized.

## Cited values

Any value may be `{"value": 11.6, "source": "A-301", "confidence": "HIGH"}`. Confidence
defaults to HIGH when a source is given and LOW when it is not. A printed room size on
an SD plan is MEDIUM. A string a human measured in a takeoff tool is VERIFIED.

## Drafts

`prefill.py` writes entries with `"draft": true`, headings of `?`, and the dimension
strings printed nearest each room tag. The build refuses a draft. A person orders the
edges, sets the headings, fixes the anchor and removes the flag.
