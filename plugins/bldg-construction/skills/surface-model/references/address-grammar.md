# The address grammar

An address names a place on a job the way a PM says it. It is also a query: it resolves
against one revision to zero, one or many keys. The canonical form is short, uppercase,
slash separated. The parser (`scripts/address.py`) also reads Matt's long form and
plain words, and `speak()` turns any address back into words.

```ebnf
address    = level "/" host "/" face [ "/" assembly ] [ locator ] ;
level      = "L" token | "B" token | "RF" | "MEZZ" | "SITE" ;   (* as the level markers print *)
host       = space | "EXT" ;
space      = printed-number | label [ "-" ordinal ] ;         (* 204, 204A, CORR-1, STOR-2, GREAT, DRIVE *)
face       = wall-face | "FLR" | "CLG" [ ordinal ] | "TOP" ;  (* CLG2 is a soffit; TOP is a roof plane *)
wall-face  = direction [ ordinal ] [ ":" opposite ] ;
direction  = "N" | "E" | "S" | "W" ;                          (* outward normal, project north *)
opposite   = space | "EXT" ;                                  (* input-only disambiguator *)
assembly   = tag ;                                            (* W3, GL-1, PT-1, as printed *)
locator    = "@" feet "-" feet | "@" feet "+" feet ;          (* span along the face; point along and up *)

core       = level "/" space "+" ( space | "EXT" ) ;          (* the wall two faces share *)
selector   = address with "*" in any segment, or a comma list in one ;   (* legal in a query, never stored *)
```

## Rules the grammar does not say on its own

- **Direction** is the face's outward normal under project north, rounded to the nearest
  of four points. Project north is set once per job from the plan's north arrow and
  confirmed by a person. Walking an outline clockwise from the north-west corner, the
  outside is on the right, so an edge walked east is the north face.
- **A face is one straight run** of the outline, from one corner to the next. A corridor's
  north wall is one face no matter how many rooms sit across the hall, and it stays one
  face when one of those rooms splits. Which neighbour sits behind which part of it is an
  attribute (`adjacency`), not a name.
- **An ordinal** (`N1`, `N2`) appears only when a space has two faces that point the same
  way. It is assigned once, in clockwise walk order from the north-west corner, and never
  reassigned.
- **`:opposite`** is accepted on input to pick between two same-direction faces by what is
  on the other side (`L2/204/N:CORR-1`). It is never part of the stored name.
- **An unnumbered space** gets the plan's own word, or the word plus an ordinal minted once
  at first sight (`BATH-1`). Deleting `STOR-1` never frees the number.
- **Assembly** narrows to the run of one wall type along a face. `L2/204/N/W3` and
  `L2/204/N` name the same face when W3 runs its full length. The runs are attributes of
  one face; the surface count never depends on the tag legend.
- **A locator** narrows to a span or a point on one face. Feet run from the left end as
  you stand in the space facing the wall. A locator lives on the pin, not on the surface.
- **`EXT`** is the building's outline on a level. Its faces are exterior faces; each shares
  a wall core with the interior faces behind it.
- **`RF`** holds roof planes. Each is a host with one `TOP` surface and its own elevation.
- **`SITE`** holds site elements. They are hosts with no faces and no geometry; they exist
  so a pin can land on them.
- **Level may be omitted** when typing or speaking if the room number is unique on the
  job. The canonical form always carries it.

## Worked examples

| Case | Address | Resolves to |
|---|---|---|
| Rectangular room, north face | `L2/204/N` | one surface key |
| Wall shared by 204 and 205, the face in 204 | `L2/204/N` | one key, whose wall core is `wk_7` |
| The same wall, the face in 205 | `L2/205/S` | a different key, same core `wk_7` |
| The shared wall itself (an RFI about its rating) | `L2/204+205` | `wk_7`; a click on either face shows it |
| L-shaped 210, two north faces | `L2/210/N1`, `L2/210/N2` | two keys, ordinals in walk order |
| The same two faces, picked by neighbour | `L2/210/N:CORR-1`, `L2/210/N:208` | the same two keys |
| Exterior face, north, level 1 | `L1/EXT/N` | one key; its core is shared with the faces behind it |
| Ceiling and floor of 204 | `L2/204/CLG`, `L2/204/FLR` | one key each |
| Unnumbered corridor, south face | `L2/CORR-1/S` | one key |
| The W5 part of a wall | `L2/CORR-1/N/W5` | the same key as `L2/CORR-1/N`, span filled in |
| A penetration 6 ft along, 8 ft up | `L2/204/N @6+8` | the same key with a point |
| The main roof plane | `RF/MAIN/TOP` | one key |
| The driveway | `SITE/DRIVE` | one space key, no faces |
| All L2 corridor wall faces | `L2/CORR-*/N,E,S,W` | many keys; the snapshot is stored on the pin |
| Every floor on level 1 | `L1/*/FLR` | many keys |
| Every W3 face on the job | `L*/*/*/W3` | many keys |
| After the floor is renumbered | `L3/304/N` | the same key `L2/204/N` had; the card shows "was L2/204/N (Rev 2)" |
| Matt's long form | `L2 / Rm 204 / North wall / W3` | the parser reads it and writes `L2/204/N/W3` |

The spoken form is generated, never stored: `L2/204/N/W5 @12-18` reads "Level 2, Room 204,
north wall, the W5 part, 12 to 18 feet from the left".
