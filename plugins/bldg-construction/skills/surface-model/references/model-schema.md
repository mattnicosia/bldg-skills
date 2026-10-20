# surface-model.json

One file per job, beside drawing-index's `index.json`. Version `1.0`.

```json
{
 "schema_version": "1.0",
 "job": "E26049",
 "north": {"source": "A-101 north arrow", "confirmedBy": null},
 "wallTolFt": 1.0,
 "revisions":   [ {"id": "SD-1", "label": "...", "date": "...", "sheets": [...], "levels": {...}} ],
 "spaces":      { "sp_1": {"key": "sp_1", "job": "E26049", "mintedIn": "SD-1", "retiredIn": null, "kind": "space"} },
 "walls":       { "wk_1": {"key": "wk_1", "job": "E26049", "mintedIn": "SD-1", "retiredIn": null} },
 "surfaces":    { "sk_1": {"key": "sk_1", "job": "E26049", "mintedIn": "SD-1", "retiredIn": null, "kind": "wall_face", "host": "sp_1", "wall": "wk_1"} },
 "openings":    { "op_1": {"key": "op_1", "job": "E26049", "mintedIn": "SD-1", "retiredIn": null, "kind": "window"} },
 "spaceRevs":   [ ... ],
 "surfaceRevs": [ ... ],
 "openingRevs": [ ... ],
 "lineage":     [ ... ],
 "pins":        [ ... ],
 "counters":    {"sp": 20, "wk": 9, "sk": 52, "op": 5, "pin": 6}
}
```

## Identity

Four things carry identity: a space (`sp_`), a wall core (`wk_`), a surface (`sk_`) and
an opening (`op_`), which is a window, door, slider or garage door in one face.
A key is minted once, never reused, never deleted. Retiring sets `retiredIn`. A space
is a room, a corridor, a deck, the building's exterior outline on a level (`EXT`), a
roof plane, or a host with no faces (a site element, a room the set has not laid out).
Two faces that are the two sides of one wall share a wall core.

## Facts per revision

`spaceRevs` and `surfaceRevs` hold one row per key per revision in which that key's
facts changed. The latest row at or before a revision is the truth at that revision.

A `spaceRevs` row: `space`, `rev`, `address`, `level`, `kind`, `printedNumber`, `name`,
`outline` (anchor, points, closed, closureErrorIn, edges with their printed parts),
`areaSf`, `ceilingFt`, `heightFt`, `elevationFt` (a roof plane's own; null means the
level's), `spotFt`, `pitch`, `downslope` and `finish` (roof planes), `phase`, `mepTags`,
`confirmedBy`.

An `openingRevs` row: `opening`, `rev`, `address` (`L1/EXT/N1/W01@43.1`, the face's
address, the tag and the center), `surface` (the face it sits in at that revision),
`level`, `kind`, `tag`, `centerFt` (from the face's `seg[0]`), `widthFt`, `sillFt` and
`headFt` (above the level's floor), `leaves`, `unit`, and `at`, the center as a plan
point, which a reissue uses to match it.

A revision entry also holds `materials`, the finish legend from its readings, and `site`
(`gradeFt`).

A `surfaceRevs` row: `surface`, `rev`, `address`, `host`, `kind` (`wall_face`,
`exterior_face`, `floor`, `ceiling`, `roof`), `face`, `direction`, `ordinal`,
`adjacency` (opposite space, its surface, the span in feet from the left),
`lengthFt`, `heightFt`, `areaSf`, `runs`, `finish`, `phase`, `seg` (the face's two
endpoints in plan feet), `poly` (for floors, ceilings and roofs).

Every measured value is cited: `{"value": 33.0, "source": "A-101", "confidence": "HIGH"}`.
A value the set does not give is `{"confidence": "NOT_MEASURED", "reason": "..."}`.
Area is null when either factor is not measured.

## Lineage

Append-only. The only way a key's meaning changes.

| kind | fields |
|---|---|
| `carry` | `from`, `to` (the same key, or a new key when a face carried under a split or merged host), `rev`, `by`, `readdressed`, `moved` |
| `split` | `from`, `to[]`, `rev`, `by`, `note` |
| `merge` | `from[]`, `to`, `rev`, `by`, `note` |
| `retire` | `from`, `rev`, `by`, `reason` |

Two invariants gate a revision: every key live before it appears in exactly one event,
and the pin count does not change. Openings count: an opening carries (same key) when the
new reading sits in a face its old face carried, split or merged into, has the same tag
and a center within 1 ft in plan. Otherwise it retires and the new reading is minted with
no event, the same way a new surface is.

## Pins

Append-only. A pin links something outside the model to a key.

```json
{"id": "pin_2", "target": {"kind": "surface", "key": "sk_3", "span": [2, 4]},
 "source": {"system": "estimate", "ref": "08 54 00"}, "label": "Unilux glass wall",
 "pinnedAt": "SD-1", "addressSnapshot": "L1/GREAT/N", "by": {"kind": "person", "id": "matt"},
 "state": "proposed", "evidence": [], "at": "2026-10-19T12:00:00+00:00"}
```

Targets: `surface` (with an optional `span` or `point`), `wall`, `space`, or `set`
(a selector such as `L1/*/FLR` and the member keys at pin time). Systems: `estimate`,
`proest`, `procore_rfi`, `procore_co`, `sow`, `selection`, `allowance`,
`field_figure`, `note`. Agents propose; people accept, withdraw or move (`state`). The
`pin-accept`, `pin-withdraw` and `pin-move` commands write the fields:

| state | fields written |
|---|---|
| `accepted` | `acceptedBy`, `acceptedAt`, `acceptedRev` |
| `withdrawn` | `withdrawnBy`, `withdrawnAt`, `withdrawnRev` |
| `moved` | `movedTo` (an address), `movedBy`, `movedAt`, `movedRev` |

Pin status is never stored. `pins.py status` derives it from the lineage at a revision:
`exact`, `readdressed`, `renamed` (the space kept its outline and changed name; a person
confirms), `forked`, `merged`, `retired`, `span_invalid`, `set_drift`, and for a person's
decision `moved` or `withdrawn`. `review` lists everything except `exact`, `readdressed`,
`moved` and `withdrawn`.

## Rejected wall pairs

`rejectedPairs` holds `{keys, addresses, rev, by, at, reason}` for each pair a person
rejected with `pair-reject`. Later accepts skip those pairs. A wall core no face points at
any more is retired.

## Exports

`sm.py export --what roofs` writes the roof planes alone: elevation, `spotFt`, `pitch`,
their sources and the outline. `sm.py export --what surfaces` writes every live space and surface at a revision with
its key, address, coordinates, elevation and cited sizes. The proposal kit's click layer
and the BLDG OS Model tab read that file; the key is the mesh tag. The Bid Presentation
Kit's `massing.json` is written from it by
`drawings-to-massing/scripts/massing_from_surfaces.py`. Neither file is a takeoff.

`surfaces.json` has the top-level keys `job`, `rev`, `north`, `levels`, `spaces`,
`surfaces`, `lineage`, `changes`, `openings`, `materials` and `site`. Each space and surface row carries `wasAddress`, the address it
had before its last readdress. `lineage` lists every event at or before the exported
revision in the order `accept` wrote them, in the shapes the Lineage table above gives,
and each event's `rev` names the revision that produced it. BLDG OS reads it to show
whether a pinned wall or room was split, merged or retired. A file written before this
field existed has no `lineage` key; readers treat that the same as an empty list.

`changes` holds `report.change_list` from the revision before the exported one to the
exported one: `from`, `to`, `surfaces`, `events`, `spaces` and `totals`, the same object
`sm.py changes` writes. Each row in `surfaces` has a `subject`, `surface` or `opening`.
An opening row is an opening added, removed or resized (width, sill or head), with the
width as its length, width times sill-to-head as its area, and `sillBefore`, `sillAfter`,
`headBefore`, `headAfter`. `totals.openings` counts them.

`openings` lists every live opening: `key`, `address`, `wasAddress`, `surface`, `wall`
(the face's wall core), `level`, `kind`, `tag`, `centerFt`, `widthFt`, `sillFt`, `headFt`,
`leaves` and, when read, `unit`, each a cited value. `materials` is the revision's finish
legend, and every `finish` on a surface or roof plane is a key into it. `site` holds
`gradeFt` when the readings give it. A roof plane's row adds `downslope` (cited), `eaveFt`
(derived, LOW: the spot height less the pitch times the run across the plane to its
downslope edge) and `finish`. A file written before these fields existed lacks them;
readers treat each as absent. It is null when the exported revision is the first. A file
written before this field existed has no `changes` key; readers treat that as null.
