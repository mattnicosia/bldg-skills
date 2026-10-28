# Montana Bid Presentation Kit v1.13

v1.13 (E260050 Cooper Barn and Pool House, whole property, 2026-10-22):
- How We Work: "Your Team" (the three principals, one support line) replaces the 1 Site Superintendent / 1 Project Manager /
  3 Principals block. Matt: the headcount block is "not my vibe". Class `yteam` (an older `.team` rule exists).
- The Proposal PDF button stays in the nav at every width. Under 600px it is a compact "PDF" pill (Matt could not find it in the
  narrow Claude side panel).
- Two buildings on one page: see `example_e260050/README.md` (three workbooks, `bld` on steps, stacked element lists, badges
  numbered per building, sub-cent line extensions rounded once at display).
- `tools/glb/parts.js`: `casing()` with `sill: false` no longer adds a second jamb on the first (it rendered black); `glazedUnit()`
  head and sill sit between the jambs so frame faces never overlap at the corners.
- `tools/render/diorama.py`: `--target x,y,z` aims the camera at a point for close probes (x east, y north, z up). Element tags can
  carry several names joined by `+` (`win+west`): hidden or ghosted if any tag is listed, blue if any tag is highlighted, so a
  cutaway lifts a whole wall while its windows still light up in their own frame.
- Black faces come from any two faces in one plane, facing the same way or opposite: overlapping casings on ganged units (one
  casing plus a mullion board), a trim box whose top meets a hole jamb, corner pilasters on two walls whose caps reach the same
  plane (step one wall 1/8 inch in height and depth), a pilaster shaft and its cap sharing a top. Probe with `--target` and a small
  `--ortho` before the long render.

v1.12 and v1.11 (E26049 1004 Old Albany Post Rd, Matt's review, 2026-10-17):
- Montana OS: the survey-theme section labels and the mono type are gone (Matt is dropping that theme from OS). `--mono` maps to
  the page font.
- Section 01 title: "Project Details".
- Allowances: a ranked ledger with a bar per allowance (`.aled`), then the per-SF rates in one navy strip (`.arate`). No empty cells.
- Selections: Exterior and Interior pills; Requested reads in Montana blue.
- Signature element frames: the edge fade touches only the soft shadow, so the land block corners stay crisp.
- Optional wall assembly panel on a step (`.wallx`, `s.wall`): the exterior wall as priced, inside to out.

Approach rebuilt (E26049 v1.10, Matt 2026-10-17: "the Montana OS section is bland", make the section stop being the weakest part):
- Removed: Unreasonable Hospitality, Radical Transparency, Our Values and the stats row (1984, 3, NY + NJ + FL). The footer keeps
  Since 1984 and NY + NJ + FL.
- How We Work: the title, then one statement in large type ("Every superintendent is a finish carpenter by trade."), then the team
  as numbers: 1 Site Superintendent, 1 Project Manager, 3 Principals, each with three short lines (`TIERS`, JOB: the architect and the
  long-lead item), then the principals' portraits.
- Montana OS: light panel with outline OS letters top right (the BLDG OS treatment, drawn as SVG polygons in `OS_LETTERS`), section
  labels with a square bullet in mono caps, and "This Job in Montana OS": an app frame with a navy bar (M mark, Montana OS, the
  project) and tiles built from the job's own numbers (base budget, line items, schedule weeks, selections when the job has them).
  The six features are numbered rows. Who It Serves stays.
- Walk Your Plans now sits above the pre-construction card.

Pre-construction without ranges, Walk Your Plans, FL (E26049 v1.9, Matt 2026-10-17):
- No plus-or-minus range anywhere a client reads. "±25 to 30% today" next to their budget reads as "the number could be 30% low".
  Each pre-con phase now says what it locks (budget and scope, selections, trade bids, GMP). The funnel keeps its shape, one tick per
  phase at its column center, never labelled with a percentage. The reserve percentages are gone from the phase columns too.
- Walk Your Plans: Montana now includes one full-scale plan session at Walk Your Plans New York (Port Chester). Every build carries a
  black screen after the pre-construction card: kicker Walk Your Plans, "Walk the house before it's built.", the session on Montana, a
  Book the Session button (email to the decisions address) and a link to walkyourplansnewyork.com. Image: the job's own floor plan as
  light linework on a dark floor, `python3 tools/wyp/plan_floor.py <plan.pdf> <job>/wyp/wyp_plan.jpg --crop .. --erase ..` (the
  E26049 arguments are in the file). JOB: name the job's real rooms in the copy (`WYP_TEXT`). Pre-con Phase 02 lists the plan walk.
- Licensed and operating: NY + NJ + FL (stats, footer, classic book footer).
- Fix: the pre-con card stayed two columns on phones (an unscoped rule after the 900px query). It stacks now.

Proposal PDF (E26049 v1.8, asked for by Matt on 2026-10-17): put the job's one proposal PDF in `<project>/proposal/` and the build ships it
in `assets/` under its own name and adds a Proposal PDF button at the top right of the nav (outline pill, white over the photo, navy on
the white nav) and in the phone menu. No PDF, no button; two PDFs stop the build. On Netlify it is a plain download link. Inside a
claude.ai artifact a plain link cannot save a file, so `app.js` hands the PDF to the `downloads` capability: publish the preview with
`capabilities: {"downloads": true}` and the PDF in `files`. Check: `web/pdf_check.mjs` (desktop, laptop, tablet, phone menu, the saved
file's size, and the artifact path with a stand-in `window.claude`).

Selections (E26049 v1.7, card design approved by Matt on 2026-10-17): every website build can carry a Selections section. One card
per element, opened from a numbered point on a model render. Four pills switch the view: Outside, Inside, Site, List. The card has two
modes. Options mode shows tiles; picking one shows the change for that element and the new total, and the render or site plan changes
with it (a roof option swaps in a second render, a driveway option repaints the drive). Rate mode is for allowances priced per unit
(SF, LF) or as a lump sum: a dial sets the rate, with marks for the value engineering items that match a rate. Prices are never typed.
An option names its workbook item (`"ref": "ALT 11"` or `"VE-2"`), a rate is `sum(row qty) x factor x 1.15`, and the build stops if a
mark does not tie to its item to the cent. The Alternates switches and the cards share one set of requests, saved on the reader's
device. Send to Montana posts them through a Netlify form (fallback: an email to the decisions address), and nothing changes in the
budget until Montana confirms in writing. See "Selections" below and `example_e26049/selections.json`.

v1.5 (E26049 1004 Old Albany Post Rd, Oct 2026): the kit ships inside the generate-proposal-mcc-living-01 skill as plain files (plugins cannot
contain zip files), so no job folder is needed.
`example_e26049/` is a second worked example of the website format: a flat-roof modern house with a cantilevered box, green roofs and a
screened porch, priced from a Claude takeoff workbook. Its `web/build.py` adds what the Cooper Barn build did not need: line items found by
their words instead of fixed rows (`find_rows`), the TOTAL -- BASE BID row found on the sheet, every alternate and value engineering total
parsed from the workbook, a Value Engineering list under the Alternates (deducts that join the running total), a schedule of any length from
`schedule.json` milestones, and a client wording pass on line items (`ITEM_FIX`, drawing references and estimator notes removed).
Shared fixes: logos and fonts load from `assets/` (the reference build pointed at a session folder), `figures.py` reads the project folder,
`app.js` formats negative figures and takes the project name from the page data, `diorama.py` honors `model.palette` for frame, flashing,
deck, concrete and membrane, and both renderers know `sedum` (green roof trays) and `stone`.

Motion hygiene (E26049 v1.6, glitch still seen live on a Mac at standard density after v1.5): the frame rate was fine (240 fps, no
long tasks); the glitch was what the motion did to fine detail. Rules now in `app.js` and `style.css`:
- Scroll-driven transforms move in whole device pixels (`snap()`), never scale a photo or a model frame. Thin battens moved by a
  fraction of a pixel, or scaled a little each frame, shimmer on a 1x screen. No slow zoom on the entry photo, no scroll zoom on the
  dusk photo, no per-photo parallax inside the gallery, no drift or scale on the model frame.
- Nothing animates a layout property: the scroll cue and the nav underline move by transform, the nav keeps one height in both
  states, and the solid nav is opaque white with no backdrop blur.
- Every per-frame write goes through `put()`, which skips unchanged values, so nothing repaints when it has not changed.
- Elements whose opacity changes every frame (`.hero__shade`, the model frames) sit on their own layer (`will-change: opacity`).
- `warm()` decodes background photos only while the reader is not scrolling; decoding during the first scroll starved the raster
  threads (18 dropped frames in a trace, 0 after).
Measure with a trace on the `netlify/` build, never `site/`: `site/index.html` has no doctype (the Artifact adds it), so a local
browser opens it in quirks mode and Lenis cannot scroll it, which makes any headless scroll test silently test nothing.

Text on Windows (E26049 v1.5, still glitching live after v1.3): Chrome on Windows draws text with ClearType only when it is fully
opaque and not animating; any opacity below 1 or a running transform flips it to grayscale and back, which reads as the words
glitching. The lede now darkens by color, never opacity; the hero title words and `.hero__inner` stay on their own layers
(`will-change`); body paragraphs reveal as one block (`data-r="up"`) instead of word by word. Headless Linux checks cannot see this;
judge it on a Windows machine.

MasterFormat view (E26049 v1.4): one row per SOV cost code from the workbook's SOV sheet, same names as the PDF proposal, never
by two-digit division. `build.py` also writes `web/proposal_lists.json` for generate-proposal-mcc.

First impression (E26049 v1.3, seen live on Netlify): the page painted the hero and title, then the blue loader flashed over them,
because the `m` class came from app.js at the end of the body. `build.py` now sets it in the head, preloads the hero photo, paints a
tiny blurred copy under it, waits for the photo to decode before lifting the loader, inlines Lenis (no CDN) and decodes the remaining
photos in the background. The lede words have no CSS opacity transition (scroll drives them every frame; a transition on top flickers).

Model hygiene from the E26049 render review. Two faces that sit exactly on each other render as black zippers in Cycles. Keep board walls
on `corners: true` with `cornerWidth` larger than the wall depth (0.7 for the default 0.6) and give `trim` the siding color so corners
read clean. On narrow piers, drop `cornerWidth` to 0.3 so the two corner boards on a 1' face never overlap. Stop walls 0.12' under the roof membrane, set roof framing 0.7' inside the walls, end east-west coping and fascia pieces
0.01' short and set north-south pieces 0.01' higher, offset overlapping footings, set deck skirts back from pier faces, and never let two
trays or slabs overlap at the same top. Put the stair in its own phase so it never pokes through a roof in an early stage. For an
all-elements frame where elements sit inside a volume, hide that volume's walls, roof and floor and ghost a plain wall shell with no
battens, built in its own `xray` phase (`--phases ...,xray --hide-els boxshell,roof1u,boxsiding --ghost-els boxghost --ghost-alpha 0.18
--samples 48`). Ghosted board-and-batten walls render as static. `hero.py` drops the `xray` phase (`model.render.heroes.hide_phases`).
`render_model.sh` passes per-frame options before the shared ones, so a frame can override `--samples`. In white clay the deck is now
clay too, so the blue reads. Keep the north glass base a light concrete band with a thin dark sill, not a tall black band. Match stair
direction and landings to the plan. Check site features (patios, terraces) against the plan, not only the renders.
Run every frame set past a fresh-context reviewer against the architect's renders before the client sees it. Chain the dusk script after
the frames in one background command (`nohup bash -c "bash web/render_model.sh; bash web/after_frames.sh"`): a separate loop that waits
for ALLDONE can read the previous run's file and start Blender early.


v1.4 (Cooper Barn v5, Oct 2026): the website format in `web/`, now the default client presentation (Project, Design, Budget, Schedule, Approach, optional Pre-Construction). `tools/render/diorama.py` renders the building on a block of land with excavation pits, in color or white clay with priced elements in Montana blue. Lenis vendored for local checks. The classic format below (`build.py`, `template/`) is kept for the Decision List.

v1.3 (Cooper Barn, Oct 2026): photographic hero frames (`tools/render/hero.py`) with real grown trees (EZ-Tree, vendored), dappled light, grass, cloud sky, finished materials and a lit interior; graded with `post.py`. v1.2: detailed model builder from drawings, Cycles stills as the default visual, phone stills, one still per phase on build stops, the landscape setting for live 3D, and the schedule on its own page. v1.1 added the Decision List.

A scroll presentation for a bid: the model builds as you scroll, then the budget, the alternates,
the schedule, pre-construction, the principals and a closing note, with a Detailed Budget behind
a button. One project folder in, one self-contained HTML page out.

## Folder layout

```
kit/
  build.py              project folder -> out/presentation.html, out/local.html, out/netlify/, zip
  lib/estimate.py       reads the house estimate workbook (SOV, markups, alternates, notes)
  template/             style.css, body.html, page.js (stops, money, book, schedule), world.js (3D)
  assets/               fonts, Montana logos, principal portraits
  tools/drawings.py     index a drawing set, render a sheet, crop and clean an elevation
  tools/glb/parts.js    parts for a detailed model from drawings (walls with battens, glazing, bifolds, standing seam, trim)
  tools/make_glb.mjs    <project>/model/build.js -> <project>/model.glb (headless browser export)
  tools/render/         Cycles (pip install bpy): hero.py photographic hero frames, post.py grade, ez.py trees,
                        stills.py renders every stop, clay.py white model views, bake.py bakes light (experimental)
  tools/make_trees.mjs  grows the tree set with vendor/ez-tree -> assets/trees/ez_trees.glb (oak, ash, pine, brush)
  vendor/ez-tree/       EZ-Tree (MIT); assets/leaves and assets/bark hold its photographic textures (CC0 bark)
  tools/pose.mjs        render the live model from exact camera poses, chrome hidden, for review
  tools/schedule.py     simple activity CSV -> schedule.json
  tools/check.mjs       screenshots of every stop, desktop and phone, plus page errors
  tools/sheet.py        contact sheet of the screenshots
  example/              Eun/Yu Residence built from drawings (massing + elevation skins)
  web/                  website format (default): reference build, page source, render script and checks. See web/README.md
  tools/render/diorama.py  building on a land block, color or white clay with blue elements, one fixed camera
  tools/sel/             Selections: selbuild.py (resolve, assets, data, section, sheet), swatches.py (procedural material swatches),
                        survey.py (a faded site plan backdrop from the survey)
  vendor/lenis/         Lenis smooth scroll (MIT), for local checks
```

Setup once per machine or session: `npm i` in the kit folder (three 0.186.1, playwright-core),
`pip install openpyxl pillow`, and `poppler-utils` for the drawing tools.

## A project folder

```
<project>/
  project.json          everything below
  estimate.xlsx         the house workbook from generate-estimate-workbook (or "budget" inline)
  schedule.json         optional; from a real schedule, or tools/schedule.py
  massing.json          when model.mode is "massing"
  model.glb             when model.mode is "glb"
  drawings/             cropped elevations for the massing skins
  img/                  renders, poster, extra portraits (embedded at build time)
```

Build: `python3 build.py <project>`. Check: `node tools/check.mjs <project> both`, then
`python3 tools/sheet.py <project> desktop` and look at every frame.

## The visual bar

Every frame must match or beat the architect's best rendering. The default for client pages is Cycles stills
(`images` mode with `"renders": true`): build `model/build.js`, `node tools/make_glb.mjs <project>`, then
`python3 tools/render/stills.py <project>`. The paper massing is for internal studies only.
The schedule has its own page (`"schedule_model": true` puts the live model back above the chart).

### Hero frames (the bar for the cover and the big moments)

`python3 tools/render/hero.py <project> --draft --size 960x540` to tune, then
`nohup python3 tools/render/hero.py <project> --size 1920x1080 --samples 128 &` (about 30 to 45 min a frame on 2 cores),
then `python3 tools/render/post.py <project>/hero/hero_<id>.png`. Everything is set in `model.render.heroes`:

- `shots`: `{id, pos, look, lens, dusk}` in Blender feet (x east, y north, z up). The camera stays level and frames
  with lens shift, so verticals stay plumb. Match the architect's best rendering for one shot (same side, eye level, long lens).
- Light: `sun_az` (compass bearing of the sun), `sun_el`, `sun_energy` about 3.5, `sky` about 0.055. Keep the sky dim:
  at 0.2 the sky out-lights the sun on the walls and everything goes flat.
- Woods: `clearing` (ellipse around the building), `forest.open` (bearings left open toward the cameras and the sun),
  `forest.gaps` (`[from, to, kmin]` where the woods stand back, so sky shows behind the roof), `stands` for named trees
  that frame a shot. Trees between the sun and the building put the whole wall in shade: check with `--probe`,
  which prints a sun map of the roof, wall and lawn. For dappled light on the roof use a shadow-only tree,
  `["oak", x, y, h, {"z": 31, "shadow_only": true}]`, raised so it shades the roof and leaves the walls in sun.
- Interior: give walls `inner: 'gyp'` in `boardBatten`, model the fit-out on its own `interior` phase, and list
  `interior_lights` for dusk. The glass passes sunlight (shadow rays see clear glass), so rooms read by day.
- Shade walls go black on dark siding: give a three-quarter shot a soft `fill` (`{"az": 110, "el": 18, "energy": 0.45}`,
  skylight colored, not seen in reflections). Colors come from `model.palette`; sample them from the architect's
  rendering in sunlight, not from the drawing notes.
- Lawn: `grass_box` at about 18 blades/sf, plus `grass_near` boxes at about 90 for the ground close to a camera,
  scoped to their shots. Blades are 2 segment ribbons; 3 segments ran out of memory at 1.5M blades.
- Get a fresh reviewer to compare every frame with the architect's rendering and the drawing before delivery.
  Check window lites, door heads and colors against the drawing yourself.
- `--set key=value` overrides one value for a test run, `--border x0,y0,x1,y1` renders a crop at full quality.

## The three model sources

| mode | when | what to provide |
|---|---|---|
| `glb` | the architect sends a model (SketchUp, Revit, Rhino, ArchiCAD) | export `.glb`, under 25 MB. Name groups with `[phase:house]`, `[alt:5]`, `[context]`, or map names in `model.phaseNodes` / `model.altNodes` / `model.contextNodes` (wildcards allowed) |
| `massing` | drawings only | footprints from the plans, heights from the elevations or sections, and optionally the elevations themselves as skins |
| `images` | the default for client pages | Cycles stills from `tools/render/stills.py` (`"renders": true`, `"fit": "cover"`): one per stop, one per phase on build stops, phone frames swap in under 760 px. Or the architect's renders in `images` / `images_phone` |

### massing.json

Plan coordinates in feet: x east, y north, grade at 0. Read them off the dimensioned plans.

```json
{
  "volumes": [
    { "name": "Main House", "footprint": [[0,0],[60,0],[60,32],[0,32]], "base": 0, "top": 22,
      "phase": "house", "material": "paper", "roof": { "type": "flat" } },
    { "name": "Garage", "footprint": [[60,0],[84,0],[84,24],[60,24]], "base": 0, "top": 12,
      "phase": "house", "roof": { "type": "gable", "ridge": 20, "axis": "x" }, "roofMaterial": "roof" },
    { "name": "Roof Deck", "footprint": [[10,8],[40,8],[40,28],[10,28]], "base": 22, "top": 25.5, "alt": "5", "skin": false, "material": "cedar" }
  ],
  "elevations": {
    "S": { "image": "drawings/elev_S.jpg", "x0": 0, "x1": 84, "y0": -2, "y1": 25.5 },
    "N": { "image": "drawings/elev_N.jpg" }
  },
  "windows": [ { "volume": "Main House", "face": "S", "along": [8, 20], "height": [3, 10] } ],
  "flats": [ { "polygon": [[-10,-30],[40,-30],[40,-2],[-10,-2]], "material": "paving", "phase": "hardscape" } ],
  "trees": [[-20, 40, 9], [100, -10, 8]]
}
```

- `roof.type`: `flat` (default, gets a thin coping), `gable` (`ridge` height, `axis` x or y), `shed` (`ridge`, `high` N/S/E/W), `hip`.
- Materials: `paper` (default), `dark_siding`, `light_siding`, `wood`, `cedar`, `concrete`, `stucco`, `white`, `roof`, `steel`, `stone`, `brick`, `glass`, `green`, `lawn`, `paving`, `asphalt`, `water`, or any `#hex`.
- Elevation skins: each elevation is projected onto every wall that faces that way. Crop it edge to edge of the building and from the lowest visible point to the highest (`tools/drawings.py crop ... --clean`), then give the matching extents: `x0`/`x1` (S and N faces, feet east) or `z0`/`z1` (E and W faces), `y0`/`y1` (feet, grade 0). Omit them and the model's bounding box is used.
- `windows` are for volumes without a skin.

## project.json

| key | meaning |
|---|---|
| `title` | page title, two to four words |
| `project` | `name`, `address`, `job` (E26040), `chip` (Budget Proposal) |
| `estimate` / `budget` | the workbook path, or `{trades:[{code,trade,value}], markups:[{label,rate}], alternates:[...]}` |
| `trade_names` | rename workbook trades for the client (`"Plumbing & Gas": "Plumbing and Gas"`) |
| `groups` | `[{name, scope, trades:[...], color?}]`. Every trade must land in one group, or the build stops. Omit to group by CSI division |
| `alternates` | per id: `title`, `note`, `featured` (shown on the Alternates stop), `hide` |
| `alt_note`, `allowances`, `keys`, `precon`, `next_step`, `team`, `book_lede`, `book_stat` | Detailed Budget content. `team` defaults to Joe, Matt and Chris |
| `include_clarifications` | true adds the workbook clarifications to the Detailed Budget |
| `schedule` | path to schedule.json |
| `model` | `mode`, `file`, `front_deg` (0 = front faces south), `zoom`, `rotateY`, `scale`, `images`, `fit` |
| `phases` | `[{id, label, sched?}]` in build order. `sched` names a schedule row, so the model rises in calendar time on the schedule stop |
| `labels` | override `book`, `keys`, `key`, `design`, `ours` |
| `stops` | the walk, below |

### Stops

Every stop takes `name` (the tick label), `view`, `side` (`l` or `r`), `w` (scroll length), `dusk`.

| type | fields |
|---|---|
| `hero` | `tag`, `h1` (lines), `lede`, `facts` ([["7","modules"], ...]) |
| `story` | `tag`, `h2`, `body` (paragraphs), `line` ({b, t}), `keys` ([{key, design, ours}]), `fine`, `show` (last phase shown), `tint` (phases tinted Montana blue) |
| `build` | as story, plus `reveal`: the phases that rise across the stop |
| `schedule` | `tag`, `h2`, `lede`, `moves` |
| `budget` | `tag` |
| `alternates` | `h2`, `lede`, `button` |
| `precon` | `tag`, `h2`, `body` (steps come from `precon`) |
| `job` | `tag`, `h2` (lines), `duties` ([[role, text], ...]) |
| `principals` | `tag`, `h2` (lines) |
| `thanks` | `tag`, `h2`, `body`, `next` |
| `html` | `html`: raw markup for a one-off stop |

Views are computed from the model: `hero`, `front`, `rear`, `left`, `right`, `aerial`, `aerial-rear`,
`top`, `low`, `corner-left`, `corner-right`, `detail`, or an exact `{pos:[x,y,z], look:[x,y,z], fov}`.

## Decision List

On by default. A header button opens a list of every alternate (Include, Not Now, Discuss) and every
`decision` milestone in schedule.json (Confirmed, Open), each with a note, a who-and-when stamp, a
running working total and an activity log. "Email This List" works everywhere.

- Shared saving needs the Artifact runtime: publish with
  `capabilities: {"db": {}, "user": {"scopes": ["profile"]}}`. Answers live in the artifact's
  database (`decisions/<item>`, `log/<auto>`) and every viewer sees them live. Read them back with
  the ArtifactData tool.
- People outside Montana can save only if invited by email as Editor while the artifact is not
  also shared by public link. Everyone else sees it read-only.
- On Netlify or a saved file, answers last for the visit and go to Montana by email.
- project.json: `"decisions": {"enabled": true, "email": "...", "placeholder": "...", "lede": "..."}`.

## Rules the build enforces

- The base budget ties to the workbook's TOTAL BASE BID to the dollar, and every trade sits in a group.
- Copy: no em or en dashes, semicolons, exclamation points or questions; none of the banned words from the
  web voice; no "X, not Y". `"allow_lint": true` lets a draft through.
- Page under 15 MB (the Artifact limit is 16 MB). A GLB over 25 MB is refused.

## Publish

- Artifact: publish `out/presentation.html` with the Artifact tool (same `file_path` each time keeps the URL).
- Netlify: drag `out/<JOB>_Presentation_Netlify.zip` onto the site's Deploys tab. It carries noindex and robots.txt.
- Save the zip and a note of the artifact URL to the job's `04 Deliverables` folder.

## Selections

`<project>/selections.json` turns the section on. No file, no section, no nav link; the send sheet still ships so the Alternates
switches can be sent. `web/build.py` calls `tools/sel/selbuild.py` (resolve after the workbook is read, assets after the hero photos,
data into the page data, section before the allowances). The schema is in the docstring at the top of `selbuild.py`.

Views. `out` and `in` are model renders from one fixed camera, made by `example_e26049/web/render_selections.sh` with
`tools/render/diorama.py` (`--rgba --block`, inside view lifts the roof and the box with `--hide-els`). A view can swap its image for
an option (`"swap": {"epdm": "sel/out_epdm.png"}`, a second model variant made with `tools/make_glb.mjs`). `site` is the survey,
faded with `tools/sel/survey.py`, with the driveway centerline traced in the cropped image's pixels; an option marked `"section": true`
paints only the stretch between `section.from` and `section.to` (fractions of the path length). Points are percent of the view.

Images. `sw:<name>` uses a swatch from `tools/sel/swatches.py <job>/sel`, `crop:hero:x0,y0,x1,y1` crops the hero photo, `crop:<stem>:...`
crops a render, and an empty value shows a labelled placeholder. Swatches are drawn, not supplier photos: replace any of them with a
real photo of the same name when there is one.

Requests. Stored in `localStorage` under `mcc-sel-<job>`. A switch in Alternates that matches a card option or a rate mark moves that
card (`refmap`), so the two never disagree. Options for one element are exclusive (one driveway surface at a time).

Netlify, once per site: Forms > Enable form detection, then deploy the zip again (detection reads the page at deploy, so the deploy
before it does not count). Then Forms > Submission notifications > add an email notification for the form named `selections`.
The hidden form in the page is what Netlify detects. A send that fails
(the Artifact preview, a local file, detection off) opens an email to the decisions address with the same list.

Check: `example_e26049/web/selections_check.mjs` runs every view and both card modes at 1440, 1180 and 390 wide, the totals to the cent,
the Alternates link, the form post, the email fallback and reload persistence. Copy it and change the figures for a new job.

