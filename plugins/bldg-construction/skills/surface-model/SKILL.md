---
name: surface-model
description: Gives every room, wall face, floor, ceiling, roof plane and site element on a job a permanent address and key, built from the dimension strings on the drawings, so estimate lines, selections, allowances, RFIs and change orders can pin to the place they touch and survive a drawing reissue. Use after drawing-index has indexed a set and before drawings-to-massing, generate-proposal-mcc-living-01, a change order from an addendum, or any task that needs "which wall" to mean one thing. Trigger on "build the surface model", "address the rooms", "pin this line to the wall", "what changed in the addendum", "draft the change order from the new set", or when a downstream skill needs surface-model.json and it does not exist.
---

# Surface Model

A job is a set of surfaces. This skill gives each one a key that never changes and an
address a PM would say out loud, reads its size from the dimension strings on the plans,
and keeps a log of what each drawing reissue did to it. Everything else on the job
(an estimate line, a selection, an allowance, an RFI, a change order, a field figure)
pins to a key, so "the great room's north wall" means the same wall on the proposal
page, in the estimate, on the addendum and on the change order.

It sits between drawing-index and everything that draws or prices the building.

```
drawing-index ──► index.json, md/<sheet>.md
        │
        ▼
surface-model ──► surface-model.json       keys, addresses, cited sizes, lineage, pins
        │           surfaces.json          what the proposal kit and BLDG OS draw
        │           (massing.json          written from surfaces.json by drawings-to-massing)
        │           changes_<a>_<b>.md     the scope list a change order starts from
        ▼
drawings-to-massing, generate-proposal-mcc-living-01, BLDG OS Model tab
```

## What it refuses to do

- It never measures off an image. A length comes from a printed dimension string with
  its sheet, or it is `NOT_MEASURED`. drawing-index's rule 7 holds here.
- It never prices anything. The change list says what grew, shrank, appeared or went,
  in feet and square feet. A rate comes from a pinned estimate line when the job has
  one; otherwise the line says needs pricing.
- It never deletes a key. A removed wall is retired and drawn as a ghost. A pin on it
  says so.
- It never decides a split, a merge or a retire on its own. Those wait for a person.

## The address

`level / host / face [/ assembly] [@span]`. `L2/204/N` is the north face of room 204.
`L1/EXT/N` is the building's north exterior face on level 1. `L1/GREAT/FLR` is the
great room floor. `RF/MAIN/TOP` is the main roof plane. `SITE/DRIVE` is the driveway,
a host with no faces. `L*/*/FLR` is a selector that picks every floor. The full
grammar, the rules behind it and worked examples are in `references/address-grammar.md`.
`scripts/address.py` reads the short form, Matt's long form ("L2 / Rm 204 / North wall / W3")
and speaks any of them back in words.

## Order of work

1. **drawing-index first.** The set is split and indexed. For a reissue, its revision
   workflow has run and `index_revisions.md` names the changed sheets.
2. **Write the readings.** One file per issue, format in `references/readings-format.md`.
   For each level: the elevation from the level markers. For each room, the exterior
   outline and each roof plane: the dimension strings in order, clockwise from the
   north-west corner, each with its sheet. On a vector sheet, draft it:
   ```bash
   python3 -I scripts/prefill.py drawings/sheets/A-101.pdf --level L1 --sheet A-101 --out readings.draft.json
   ```
   then order the edges, set the headings, fix the anchors and remove the draft flags.
   On a scanned sheet, read the strings off the scan. Two to three minutes a room.
   List what was read and what was assumed, and mark assumed values LOW.
3. **Build the first revision.**
   ```bash
   python3 -I scripts/sm.py init <job>/surface-model.json --job E26049
   python3 -I scripts/sm.py build <job>/surface-model.json readings_rev1.json --rev SD-1
   ```
   The build refuses a room whose walk does not close within an inch and names the gap.
   It prints the wall pairs it proposes (which faces are the two sides of one wall).
   Show the list to a person and rerun with `--accept-pairs <who>` once they confirm.
4. **Pin what touches the building.** Estimate lines by selector, selections and
   allowances by target, RFIs and COs by the surface they name:
   ```bash
   python3 -I scripts/sm.py pin <job>/surface-model.json "L1/*/FLR" --system estimate --ref "09 64 00" --by matt --label "Wood flooring"
   python3 -I scripts/sm.py pin <job>/surface-model.json "L1/GREAT/N" --system selection --ref "SEL-02" --by matt --label "Unilux or North American glass"
   ```
   An agent that proposes a pin from an RFI's text passes `--by agent:connie` and
   `--state proposed`; a person accepts it later.
5. **A reissue.** Write the new readings, then:
   ```bash
   python3 -I scripts/sm.py propose <job>/surface-model.json readings_rev2.json --rev DD-1 --out proposal.json
   ```
   Read the proposal: carries apply on their own; splits, merges and retires are listed
   with the pins they would touch. Accept with `--all` or `--decide 2,4` after a person
   decides:
   ```bash
   python3 -I scripts/sm.py accept <job>/surface-model.json proposal.json --by matt --all --accept-pairs matt
   python3 -I scripts/sm.py review <job>/surface-model.json
   ```
   The review lists every pin that is no longer exact: forked (the room split, pick a
   child), merged, retired, renamed (same outline, new room name), span past the new wall
   end, or a selector whose members changed. A room folding into a larger one shows as one
   merge, not a carry plus a retire. Settle a pin with a command, never by editing the JSON:
   ```bash
   python3 -I scripts/sm.py pin-accept   <job>/surface-model.json pin_3 --by matt
   python3 -I scripts/sm.py pin-move     <job>/surface-model.json pin_3 --to "L1/KITCHEN-B" --by matt
   python3 -I scripts/sm.py pin-withdraw <job>/surface-model.json pin_3 --by matt
   ```
   A wall pair the model proposed or accepted where the plan has no wall is rejected with
   `sm.py pair-reject <job>/surface-model.json "L1/A/E" "L1/B/W" --by matt`. It stays rejected
   on later issues.
6. **The change list.** The scope list a change order starts from:
   ```bash
   python3 -I scripts/sm.py changes <job>/surface-model.json --from SD-1 --to DD-1 --md changes.md
   ```
   One row per surface that changed, plus a table of spaces whose elevation, roof spot
   height or pitch changed, with before, after, delta, and a price only where
   a pinned estimate line carries a rate (`--rates rates.json`, `{"estimate:09 64 00": {"rate": 27.22, "unit": "SF"}}`).
7. **Export for the people who draw it.**
   ```bash
   python3 -I scripts/sm.py export <job>/surface-model.json --what surfaces --out surfaces.json
   ```
   `surfaces.json` carries every key with its address, outline or segment, elevation
   and cited sizes; the proposal kit tags each mesh with the key and the OS Model tab
   draws from it. Its `lineage` array lists every carry, split, merge and retire up to
   that revision, so the OS can say what happened to a pinned wall or room. Its `changes`
   field holds the change list from the revision before, in the shape `report.py` gives
   it, or null for the first revision. `--what roofs` writes the roof planes alone (elevation, spot height,
   pitch). The kit's `massing.json` comes from that file through
   `drawings-to-massing/scripts/massing_from_surfaces.py`, the one massing writer.

## Rules

1. ALWAYS take lengths from dimension strings with a sheet; NEVER from the image.
2. ALWAYS walk clockwise from the north-west corner; a walk that does not close is a refusal, not a warning.
3. NEVER reuse a key. A room that merges gets a new key; the old ones retire.
4. NEVER accept a split, merge or retire without a person's decision. Carries apply on their own.
5. ALWAYS run `review` after `accept` and put every non-exact pin in front of a person.
6. NEVER price in this skill. The change list carries feet and square feet; rates come from pins.
7. ALWAYS mark an assumed height, anchor or length LOW and say so in the reply.
8. ALWAYS keep `surface-model.json` beside `index.json` as a permanent project deliverable.

## Scripts

| Script | Purpose |
|---|---|
`sm.py` | The command line: init, build, propose, accept, resolve, pin, pin-accept, pin-withdraw, pin-move, pair-reject, touches, review, changes, export, report, speak, summary. |
`address.py` | The grammar: parse, canonical form, selector match, speak. |
`geometry.py` | Dimension strings to feet, the clockwise walk, closure, area, overlap, back-to-back faces. |
`build.py` | Readings to spaces, surfaces and wall pair proposals; mints keys on the first revision. |
`revise.py` | A new issue against the model: match by outline, propose lineage, accept with invariants. |
`pins.py` | Pins, resolve a selector, pin status at a revision, what touches a key, the review queue. |
`report.py` | The proposal report, the revision report, the change list. |
`export.py` | surfaces.json. |
`prefill.py` | Draft readings from a vector sheet's text layer (needs PyMuPDF). |

Stdlib only, except prefill. Run every script with `python3 -I`.

## Worked example

`examples/e26049/` holds 1004 Old Albany Post Road at SD-1 and a made-up DD-1 addendum
(the bedroom splits into a bedroom and a study, the great room grows two feet, the
mechanical room goes, the primary suite gets its first outline). Room sizes are the
printed SD sizes and anchors are approximated, both marked. Run it end to end:

```bash
cd examples/e26049 && sm() { python3 -I ../../scripts/sm.py "$@"; }
rm -f surface-model.json && sm init surface-model.json --job E26049
sm build surface-model.json readings_rev1.json --rev SD-1 --accept-pairs matt
sm pin surface-model.json "L1/*/FLR" --system estimate --ref "09 64 00" --by matt --label "Wood flooring"
sm pin surface-model.json "L1/BEDROOM" --system procore_rfi --ref "RFI-031" --by agent:connie --label "Outlet height"
sm propose surface-model.json readings_rev2.json --rev DD-1 --out proposal.json
sm accept surface-model.json proposal.json --by matt --all --accept-pairs matt
sm review surface-model.json
sm changes surface-model.json --from SD-1 --to DD-1
```

The review shows the flooring set drifted (two floors added, two gone), the RFI forked
(pick the bedroom or the study) and nothing else. The change list shows the bedroom's
north wall as one row, 16 ft to 15.5 ft across the two rooms it became, the new partition's
two faces as added, the great room's glass wall as 33 ft to 35 ft, the mechanical room
removed, and the primary suite measured for the first time.

## Where this goes next

The job folder's `surface-model.json` is the one source. drawings-to-massing reads
`surfaces.json` instead of re-reading dimensions (done: its `massing_from_surfaces.py`). The proposal kit tags each mesh with
the surface key and draws the click layer from the same file. BLDG OS reads the file for
its Model tab and never computes its own copy. The design note in `~/dev/BLDG OS` holds
the data model this file follows and the accuracy test it must pass before any
model-derived area goes in front of an estimate; `references/` carries the parts of it
a collaborator needs.
