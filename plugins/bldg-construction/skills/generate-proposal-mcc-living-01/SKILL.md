---
name: generate-proposal-mcc-living-01
description: Build a Montana Contracting presentation in website format, a scroll page with the project, the design (the building rising on its land, signature elements priced in Montana blue), the budget (Elements and MasterFormat views, allowances, alternates, notes and clarifications), selections (one card per element on Exterior, Interior, Site and List views, with requests the owner or architect sends to Montana), the schedule, how we work and an optional pre-construction view, from the estimate workbook and drawings or a 3D model.
---

# Generate Proposal MCC Living 01

The client-facing presentation Montana sends with a budget or bid. One page in website format, built to the bar of lusion.co/about: one idea per screen, giant type, scroll-linked motion, numbers as the design object, rounded corners and a friendly UI. The PDF proposal is a separate deliverable (generate-proposal-montana). This page goes alongside it.

The reference job is E260050 The Cooper Barn, v5.2, which Matt approved on 2026-10-16 ("It's literally perfect"). Its build is in the kit at `kit/web/`. Start every new job from it.

Call it a "presentation". Lead with Montana Contracting. Never show or mention NOVATERRA or any internal tool.

## Before anything else: ask Matt which sections go in

At the start of every job, before building, ask with the AskUserQuestion tool (one call, two questions). Save the answers in `project.json` as `"sections"` and `"renovation"`; `build.py` reads them (kit v1.16).

1. **"Which optional sections go in this presentation?"** (`multiSelect: true`). Options, in this order:
   - Pre-Construction (Recommended): the black card after How We Work and the full-screen view it opens. Key `precon`.
   - Your Team (Recommended): the three principals under How We Work. Key `your_team`.
   - Selections: one card per element with options and rates (needs `selections.json`). Key `selections`.
   - Walk Your Plans: the full-scale plan session offer, after How We Work, plus its Phase 02 pre-con bullet. Key `walk_your_plans`.
   - Montana OS: the operating system panel under How We Work (numbers-only tiles, feature names only). Key `montana_os`.
   Defaults when Matt skips the question: Pre-Construction and Your Team on, Selections on only when `selections.json` exists, Walk Your Plans and Montana OS off.
2. **"Is this a new building or a renovation of an existing one?"** New build (the building rises on the site) or Renovation (opens on the existing building; see 02 / Design). Pick the recommended answer from the drawings (demolition sheets and "existing to remain" mean renovation).

```json
"sections": {"precon": true, "your_team": true, "selections": false, "walk_your_plans": false, "montana_os": false},
"renovation": true
```

## The page

The flow is project, design, budget, selections, schedule, approach. Every section has a numbered kicker and a plain title. Details for each section, and the code behind it, are in `references/website-format.md`. Read it before building.

1. **Entry.** The best hero render, full screen, with no effect over it. Pills for Budget Presentation, the town and the building type, the project name as the title, and the architect and address as the eyebrow. A loader where the M assembles from its three pieces.
2. **01 / Project.** Title "Project Details". A facts column (Location, Type, Architect, Budget, Schedule) beside a one-paragraph project description (40 to 80 words), written in the Project description voice below.
3. **Gallery.** The day and dusk renders on a pinned horizontal track.
4. **02 / Design.** One pinned model and one fixed camera on a block of land (lawn, topsoil, subsoil).
   - **New build:** "Site and Foundation" shows the excavation, then the backfill, then the next step, so the foundation never disappears. Its figure is all site work and concrete with the markups.
   - **Renovation (kit v1.16, E26044 The Inn at Kirkside):** never show the site empty and the building rising. The rail reads Existing Building, New Work, Complete, Signature Elements. Existing Building is the building as it stands, in white clay, carrying the base budget figure (render it with the new foundations hidden: `--hide-els foundation`). New Work holds Site and Foundation (the existing building in clay, new foundations and pits in blue) and Additions (each addition in blue, no figure). Then Complete in color. Never call it "The House".
   - The Site and Foundation figure leaves out any line already inside a signature element (name the element rows in `EL_ROWS`; the build skips them), so nothing is counted twice.
   - Build steps (Workshop, Lounge, Exterior for the Cooper Barn) are in color.
   - "Signature Elements" are in white clay with each element in Montana blue, one per screen with its price. The marker is brackets by default. Dot, leader and badge are kept as options (`#mk-dot`, `#mk-leader`, `#mk-badge`).
   - The last step lists the elements plus "Building, Site and Systems" so the list totals the base budget.
5. **03 / Budget.** The base as a rolling figure, a stacked bar by group and two pills, Elements and MasterFormat.
   - Each row opens to its line items with no line pricing and no unit rates.
   - **MasterFormat = the Schedule of Values.** One row per cost code exactly as the workbook's SOV sheet lists it (`01 00 00 General Requirements`, `02 41 00 Waste Removal`, ... `34 71 00 Guide Rail`), at direct cost, with the same plain names the PDF proposal uses (`SOV_NAMES` in `build.py`, e.g. Base Courses (RCA Driveway) reads Gravel Driveway). Never group by two-digit division. `build.py` dies if a line's code is missing from the SOV sheet or a row differs from the workbook by a cent. See `kit/example_e26049/web/build.py`.
   - `build.py` writes `web/proposal_lists.json` (allowances, alternates, value engineering) so the PDF proposal (generate-proposal-mcc) carries the same items, names and figures.
   - Below the rows: Direct Cost in bold, then each markup on its own line (`"markups"` in project.json, e.g. `[["Design Contingency (TBD)", 0], ["Fee", 0.06], ["Insurance", 0.03]]`; default Overhead and Profit 15%), then Base Budget. Each markup compounds on everything above it: insurance sits under fee and is figured on direct plus fee. Never combine two markups on one line ("Fee and Insurance").
   - Row percentages are shares of direct cost, so they add to 100%. A line under 0.05% reads "<0.1%".
   - Selections (when the job has `selections.json`, see Selections below), then Allowances (a ranked ledger, largest first, with bars and the total, then the per square foot rates in their own strip), then Alternates (switches and a running total, Requested and If Montana Confirms, a Send to Montana button, no lede), then Notes and Clarifications (Basis of Budget, Clarifications, Exclusions) as three closed groups that show their count.
6. **04 / Schedule.** A side panel with the total weeks, a live week counter and the phases filling as the cursor passes. A pinned chart that ends exactly on the last week. No "Preliminary" note.
7. **05 / Approach.** Title "How We Work", then "Every superintendent is a finish carpenter by trade." in large type with no paragraph under it, then "Your Team": the three principals with the line "Three principals stay on this project from the first walkthrough to the final punch list. You are never handed off." and their portraits (class `yteam`, never `team`). No team-as-numbers block (Matt dropped the 1 Superintendent, 1 PM, 3 Principals tiers 2026-10-21). Montana OS only when Matt picks it at the start (off by default), no values list, no principles, no stats row.
8. **Pre-Construction (optional, on by default).** A black card, "See Our Pre-Construction Process", after How We Work. Walk Your Plans (optional, off by default) sits between How We Work and this card when Matt picks it. The card opens a full-screen view that grows out of the card. The view is the latest pre-con proposal with everything project-specific removed. There is no pre-construction button in the nav, the menu or the close.
9. **Thank you.** The dusk render with "Thank you for the opportunity to partner with you on this project."
10. **Contact.** Navy and very minimal: the kicker Contact, a Call button and the contact block. No sentence (Matt, 2026-10-30).

**Proposal PDF.** When the PDF proposal exists (generate-proposal-mcc), put it alone in `<project>/proposal/`. The build adds a Proposal PDF button at the top right of the nav at every width (a compact pill under 600px, so it never hides in a narrow panel) and in the phone menu. Publish the preview with `capabilities: {"downloads": true}` and the PDF in `files`, because a plain link cannot save a file inside an artifact. Run `pdf_check.mjs`.

The M logo goes in the loader, the navy Contact screen (tone on tone), the pre-con card and view, and the favicon. Never next to the wordmark. Dark panels are true black (#000), not navy.

## The visual bar

The architect's renderings are the minimum. Every frame must look at least as good as the best rendering the architect provided: real materials, the real details (canopies, brackets, cupola, gutters, flues), daylight with soft shadows and a believable setting.

- Collect every rendering first and save the best one as `ref/reference.jpg`.
- Hero and gallery frames come from `tools/render/hero.py`: eye level, real grown trees, dappled light, grass, a cloud sky and a lit interior. Tune with `--draft` and `--probe` before the long render.
- Design frames come from `tools/render/diorama.py`, driven by `web/render_model.sh`: the building on a land block with boolean excavation pits, `--color` for build steps, white clay with `--highlight` for elements, `--ghost-els` and `--hide-els` for cutaways, `--points` for marker anchors.
- Before publishing, a fresh-context reviewer (Agent tool) compares the frames with the reference on materials, detail, proportion, light, setting and artifacts. Fix until it says they match or beat it. Expect two or three passes: zoom into corners, wall tops, roof edges and pier bases, and check site features and the stair against the plan. If they cannot reach the bar in the time available, say so plainly before publishing.

## The kit

All code lives in the Bid Presentation Kit. Do not rebuild it from scratch.

- The kit ships with this skill as plain files in `kit/` in this skill's base directory (`kit/README.md` first). Never ask Matt for it and never reach into another job's folder for it. Plugins cannot contain zip files, so never zip the kit inside the skill.
- To get it into the session: copy this skill's `kit/` folder into the working directory as `kit/`, run `npm i` in it, run `pip install openpyxl pillow numpy bpy --break-system-packages`, and make sure `pdftoppm` is available.
- Layout: `<work>/kit/` and `<work>/<project>/` side by side. Copy `kit/web/` to `<project>/web/`. `kit/web/README.md` lists every file.
- If you improve the kit during a job, bump the version in `kit/README.md`, replace the files in this skill's `kit/` folder (no `node_modules`, no zips) and ship it as a plugin update. Say what changed.
- `kit/example_e26049/` is the second worked example (1004 Old Albany Post Rd): a modern house from a Claude takeoff workbook, with a Value Engineering list under the Alternates (`ve` in project.json, deducts that join the running total), line items found by their words, a schedule from `schedule.json` milestones and a client wording pass on line items. Start from it when the workbook carries VE items or the rows are not the Cooper Barn layout.

Kit v1.16 (E26044 The Inn at Kirkside, 2026-10-30): optional sections asked at the start (Pre-Construction, Your Team, Selections, Walk Your Plans, Montana OS), the renovation sequence, the markup ladder (each markup its own compounding line), percentages of direct cost, no double counting in Site and Foundation, directives on every scope item (`tools/scope/wording.py`), schedule and allowance checks, the PDF hand-off `scope_lines.json`, and check scripts that skip optional sections. Kit v1.15 (2026-10-30) removed the Next Step sentence and took Montana OS off by default. Kit v1.14 (2026-10-30) is the light-reading pass: Walk Your Plans removed and about 40% fewer words (README). Kit v1.13 (E260050 Cooper Barn and Pool House, 2026-10-21) added "Your Team" in place of the team tiers, the Proposal PDF pill at every width, the Project Details title, the allowance ledger and rate strip, Netlify publishing (step 7) and the third example `kit/example_e260050/`: two buildings plus shared General Requirements from three workbooks, Barn and Pool House filters on the elements and budget, a pool house model with a cutaway stair. Its render fixes: duplicate casing jambs and glazed-unit head and sill overlaps removed in `tools/glb/parts.js`, `--target x,y,z` and multi-tag elements (`a+b`) in `diorama.py`. Kit v1.12 and v1.11 (E26049) brought the v1.12 CSS, the Montana OS panel without survey-theme labels, Exterior and Interior selection pills and the edge fade only on transparent frames. Kit v1.10 (E26049) rebuilt Approach (team as numbers, Montana OS as a product with the job's numbers, values and stats removed) and moved Walk Your Plans above Pre-Construction. Kit v1.9 (E26049) took every plus-or-minus range out of the pre-con content, added Walk Your Plans and FL. Kit v1.8 (E26049) added the Proposal PDF button. Kit v1.7 (E26049) added Selections (`tools/sel/`, below). Kit v1.6 (E26049) set the motion rules below after the live hero and Project glitch. Kit v1.5 (E26049) bundled the kit into this skill, added the second example, the Value Engineering list, `sedum` and `stone` materials in the renderers and palette colors for frames and flashing in the diorama, and moved logos and fonts to `assets/`. It also records the model hygiene rules from the E26049 render reviews (README, "Model hygiene"): two faces that sit exactly on each other render as black zippers, so walls, framing, coping, trays and footings never share a face; the stair gets its own phase; an all-elements frame with elements inside a volume ghosts a plain `xray` shell that `hero.py` drops; patios, stairs and porch walls are checked against the plan, not only the renders. Kit v1.4 (Cooper Barn v5) added the website format (`web/`), `tools/render/diorama.py`, the element-tagged model pattern (`tools/glb/example_cooper_barn_el.js`) and vendored Lenis for local checks. Kit v1.3 added the hero frames. The classic format (`kit/build.py`, `template/`) is kept for the Decision List.

## Order of work

1. **Gather first.** The final estimate workbook in the house format (Estimate sheet, SOV with Final Price, markups, Alternates block, Notes & Clarifications). The schedule, real or Matt's dates, never invented. The drawings. Any 3D model from the architect. Every rendering. If the estimate is not final, the presentation is not final. Say so.
2. **Build the model.** Write `<project>/model/build_el.js` from `tools/glb/example_cooper_barn_el.js`. Tag each signature element and each cutaway wall with `M.el` so it becomes its own mesh. Then, from `kit/`, `node tools/make_glb.mjs <project> <project>/model_el.glb <project>/model/build_el.js`. List what was read off the drawings and what was assumed.
3. **Render the frames.** Set the camera, the land block, the pits, the element points and the frame list in `web/render_model.sh`, then run it in the background with `nohup` and watch `web/model/done.txt` for ALLDONE. One Blender at a time, about 100 seconds a frame at 1600x1200 and 24 samples on two cores.
4. **Write the job blocks** in `web/build.py` (marked `# JOB`). Line names go through `tools/scope/wording.py` (every item opens with a directive: Furnish and Install, Furnish Only, Install Only, Provide, Remove, Repair, Patch, Paint, Wire...; no estimator tags, no TBD); add this estimate's own fixes in `JOB_FIX`. Product names that contain a banned word go in `"allow_words"` (e.g. "Signature Elevate"). Blocks: element rows, allowance rows, milestones, the project description, the design steps, Basis of Budget, Clarifications, Exclusions, the team and the zip name. Write the copy with the montana-web-voice skill and the rules below.
5. **Build:** `python3 -I build.py` in `web/`. It stops if the base does not tie to the TOTAL BASE BID row, if a row moved, if a note fragment is not in the Notes sheet, if a dollar figure lacks cents, or if the copy breaks the house rules. Fix the cause.
   With selections: write `<project>/selections.json` from the example, render the views with `web/render_selections.sh` after the model frames, and make the swatches with `tools/sel/swatches.py <project>/sel`.
6. **Check.** Run `shoot.mjs`, `interact.mjs`, `fitcheck.mjs`, `markers.mjs` and `precon_card.mjs`, each with a screenshot folder outside `site/` and `netlify/` (they refuse one inside). Set `CHROME` to the Chromium in `/opt/pw-browsers/*/chrome-linux*/chrome` when the default path is missing. Look at every screenshot, desktop and phone. Then send a fresh-context checker (Agent tool) the visible copy, `figures.json` and the workbook, to verify every figure, scope claim and copy rule. Fix what it finds that the estimate supports.
7. **Publish.**
   - Publish `web/site/index.html` with the Artifact tool, with `root` set to `web/site` and every asset in `files`. Publish to a private preview first. Change the live link only when Matt says go.
   - Save the zip to the job's `04 Deliverables` as `<JOB>_Presentation_Netlify_v#.zip`, using the next version number. It carries noindex.
   - **Build the PDF proposal first** (generate-proposal-mcc, from `web/proposal_lists.json` and `web/scope_lines.json`) and put it in `<project>/proposal/`, so the first deploy already has the Proposal PDF button.
   - **Netlify (Matt's account).** Create the site with `POST /api/v1/sites` `{"name": "montana-<shortname>"}` when it does not exist. The cloud shell can reach api.netlify.com too (E26044 deployed from it). Site name `montana-<shortname>.netlify.app` (short: `montana-cooper`). Keep a copy of the zip on Matt's Mac at `~/Sites/montana-presentations/<shortname>/<Name>_Presentation_v#.zip`. Deploy from the Mac shell (device_bash) with the REST API: `POST https://api.netlify.com/api/v1/sites/<site_id>/deploys` with `Content-Type: application/zip` and the zip as the body, then poll the deploy until `state` is `ready`. netlify-cli fails behind the proxy (407), so use curl. The token lives only in `~/.nf_token` in that shell. If it is missing or expired, start an OAuth ticket (`POST /api/v1/oauth/tickets?client_id=d6f37de6614df7ae58664cfca524744d73807a377f5ee71f1a254f78412e3750`), give Matt the link `https://app.netlify.com/authorize?response_type=ticket&ticket=<id>` to approve in his browser, then exchange the ticket for the token. Never ask Matt for a token or password and never type one into a page. `*.netlify.app` cannot be fetched from either shell, so verify through the API (deploy state, file count).
   - **Cover email.** Every publish reply includes the cover email draft, written in Matt's voice guide (`/Users/mattnicosia/matt-vault-v2/03 Self/Writing Voice.md`). Subject `Montana Budget - <Project Name>`. The link near the top, no figures in the body, no "Here is our", no "reach out" hedges. Close on thanks for the opportunity and an offer to review on Zoom or in person. Signature: Matt Nicosia, Chief Operating Officer.
   - Record the links, the final numbers and the open items in the Claude project doc for the job.

## Copy rules from Matt

- Never put a plus-or-minus range or an accuracy percentage where a client reads it. Next to their budget, "±25 to 30%" reads as "your number could be 30% low" (Matt, E26049). Say what each phase locks instead, and show certainty by shape, not numbers.

- No em dashes or en dashes anywhere. No "X, not Y". No questions, exclamation points or semicolons. Title Case for every label that is not a sentence.
- Titles are plain: "Project Details", "Design", "Signature Elements", "Budget", "Allowances", "Alternates", "Notes and Clarifications", "Schedule", "How We Work", "See Our Pre-Construction Process". Offer Matt options when a title is new, and say which one you put in.
- Lines Matt rejected as AI writing: "Every design move, priced.", "The Design Moves", "On Site", "Supervision on Site. Management in the Office.", "Carpenters run our sites." Avoid anything like them.
- Never put risk in front of the client. Never show where the documents disagree. Never take credit for the design team's measures.
- Coordination with other contractors reads as partnership and a clean handoff. Avoid contract-boundary lines.
- Every claim must match the estimate notes. If a scope is excluded, the copy cannot say it is carried.
- Keep reading light (Matt, 2026-10-30: "simplify and minimize our proposal ... specifically the amount of reading"). One idea per screen, short lines, numbers as the design object. No lede paragraphs under titles, no body paragraphs on design steps, captions of 14 words or fewer, notes folded. When a line explains what a number already shows, cut the line. The PDF carries the long text.
- Principals are Joe Montana (Founder and CEO), Matt Nicosia (COO) and Chris Lange (Director of Construction). Show each person once. Confirm titles if anything changed.

## Project description voice (Montana Contracting)

Use this voice for the project description in the presentation: the Project section right after the entry, and any other paragraph that describes the building.

### Inputs to collect first
Ask for these if they're missing. Never invent a fact, number, brand or name.
- Project name, town and state
- Building type and size (square feet, units, acres, stories)
- Scope: ground-up, conversion, buildout, phased work around an operating business
- Named materials, products and systems (brands where known)
- What was hard: site, schedule, structure, occupied building, tight lot
- Architect, if any
- Who uses the building and how

### Structure
In the presentation (kit v1.14): one paragraph, 40 to 80 words: the site and the brief, then the one fact about the build that matters most. The three-paragraph structure below is for montanacontracting.com.

On the website: three paragraphs, 1 to 4 sentences each, about 90 to 220 words in total.
1. **The site and the brief.** What it is, where it is, what it had to do. The first sentence must stand alone as a search snippet: under about 155 characters, and naming the building type and the town.
2. **The build.** Materials, massing, systems and the hard part, with real numbers and product names.
3. **The building as designed.** The interior, how it will be used, the result. End on a plain, quiet line, not a sales line.

### Rules
- Lead with the building, not the company. When the company appears, say "we" / "our team" or "Montana Contracting". Never "I".
- Name the material and the brand: "Marvin Contemporary Windows", "Warmboard radiant heating", "rift white oak", "helical piles". Don't write "high-end finishes" or "premium materials".
- Use real numbers as numerals: 4,900 square feet, 12 to 18 feet, 26,000 square feet, three weeks.
- A short fragment opener is fine when the brief is the story: "Three weeks, start to finish." / "Two homes, one family, one site."
- Leave construction terms as they are (MEP, GMP, schematic design). Don't explain them.
- Name the architect when there is one.
- Never use em dashes or en dashes. Use periods, commas or colons.
- Banned: "proud to share", "excited", "grateful", thank-you lines, "stunning", "breathtaking", "dream home", "state-of-the-art" (unless quoting a spec), "nestled", "seamless", "elevate", "transform".
- Banned patterns: "not X, but Y" contrasts, stacked negations ("No X. No Y."), any sentence that explains why something matters.
- Don't describe the photos ("the photography follows..."). Describe the building.
- Don't claim anything the inputs don't support. If a paragraph has no facts to work from, ask for them. Don't pad.

### Examples (approved, live on montanacontracting.com)

**Palisades Mod Ranch**
A 4,900-square-foot ranch in Palisades, New York, designed around two principles: open space and natural light. Fourteen-foot Marvin Contemporary Windows and Wasco skylights pull daylight deep into the plan, while ceiling heights shift from 12 to 18 feet to define each zone without walls.

The exterior is a composition of materials. Clear cedar and ipe siding sit alongside Cembonit fiber cement panels and natural stone veneer, all capped by a black standing-seam metal roof. The material palette feels grounded and modern at once, aging into the wooded Palisades site rather than fighting it.

Inside, every system was chosen for precision and comfort. Warmboard radiant heating runs underfoot. Three Stuv wood-burning fireplaces anchor the main living spaces. Liberamente kitchen cabinetry, a RadioRa lighting control system, and a fully-finished basement complete a home built to perform as well as it looks.

**Dunkin' New City**
Three weeks, start to finish. Dunkin' needed a full interior rebuild of an operating store in New City, and the schedule left no room for a slow start or a second mobilization.

We ran the job with our own crews. Every one of our superintendents came up as a carpenter first, so the people running the schedule are the same people who can pick up a tool and close a gap in it. A three-week interior turn depends on a crew that can move from demo to rough-in to finish without waiting on outside labor to catch up.

The result is a full rebuild behind the same four walls. New counters, new digital menu boards, a full espresso and cold brew bar, dark tile and black ceiling throughout, and the branded wall signage that anchors the dining room. The store reopened on schedule, finished to the same standard as a ground-up build.

**Rivers Bend Farm**
A 50 by 60 foot, two-story barn built as an event space on a private 100-acre compound in the Catskills. The barn shares the land with a main house, a cottage, a single-family cabin and a regenerative organic farm.

The ground floor holds the events. Upstairs is fully finished as a bridal suite and living space, so a wedding party can get ready, stay the night and step down into the celebration without leaving the building.

The compound is private and remote. The West Kill runs through the property, past a pond and an open lawn, and the farm works the land around the barn.

### Check before handing off
- Three paragraphs, in the order above
- First sentence works on its own as a search snippet
- Every number, brand and name came from the inputs
- No em dashes, en dashes, banned words or banned patterns

## Numbers

- Every figure comes from the Estimate sheet line items, summed with Python Decimal to the cent. Every dollar figure on the page shows cents ($1,739.00).
- The SOV Final Price column rounds each trade, so it can differ from the line items by a few cents. Use the line items and tell Matt the difference.
- Group and division percentages are shares of direct cost. Each markup shows once, on its own line, under Direct Cost.
- Signature element figures are their line items with the markup ladder (`mk()` in `build.py`). The element rows are checked by name at build, so a moved row stops the build, and the build prints each element's lines: read them, a stray line (shower glass inside Conservatory Glass on E26044) is a wrong figure.
- When a leveled subcontract feeds an element (HVAC spread over a geothermal field), hold the real lines at their values in the workbook (see generate-estimate-workbook) so the element is not inflated by the spread.
- Allowances follow the Notes sheet list, carried before overhead and profit. Alternates show the workbook's Final Price, with markups.
- Basis of Budget, Clarifications and Exclusions come from the Notes & Clarifications sheet.
- Check the General Requirements staffing in the workbook against the schedule length. Tell Matt if they differ.

## Selections

Approved by Matt on 2026-10-17 ("love it"). Every new bid gets it from the start. The code is `kit/tools/sel/selbuild.py`, the worked example is `kit/example_e26049/` (`selections.json`, `web/render_selections.sh`, `web/selections_check.mjs`, `model/build_el_epdm.js`), and the schema is at the top of `selbuild.py`.

- **One card, two modes.** Options mode for a material or product choice: tiles, the change for that element, the new total, and the view changes with the pick. Rate mode for an allowance priced per SF, LF or as a lump sum: a dial sets the rate, with marks where a value engineering item matches a rate. Matt does not want a side-by-side compare and does not want packages.
- **Four pills.** Exterior and Interior are model renders from one fixed camera (Interior lifts the roof off). Site is the survey, faded with `tools/sel/survey.py`, with the driveway drawn and painted in the chosen surface, never a photo of grass labelled driveway. List replaces a separate selections schedule.
- **Numbered points** on the views open the card. Same numbers as the list.
- **Prices are never typed.** Options name the workbook item (`ALT 11`, `VE-2`); rates are `sum(row qty) x factor x 1.15`; lump sums are the cost codes' total, per dollar 1.15. The build stops if a mark with a ref does not tie to the cent.
- **Requests, not changes.** A pick is Requested and changes nothing until Montana confirms in writing. Requests are saved on the reader's device and shared with the Alternates switches (one store, `refmap`). Send to Montana posts a Netlify form named `selections` with the list, the change and the total; if that fails it opens an email to the decisions address. Confirmed picks become the next workbook version and the next revision of the proposal.
- **Assets.** Swatches from `tools/sel/swatches.py` are drawn, not supplier photos; replace them with real photos when there are some. A choice that changes the building (a roof membrane) gets a model variant and a second render through `swap`.
- **Netlify, once per site.** Tell Matt: Forms > Enable form detection, deploy the zip again, then Forms > Submission notifications > add an email notification for the `selections` form.
- **Check** with `selections_check.mjs` (copy it and change the figures): every view and both modes at 1440, 1180 and 390 wide, totals to the cent, the Alternates link, the form post, the email fallback, reload persistence.

## Decision List

The Decision List (Include, Not Now, Discuss on every alternate, with notes and a log) is in the classic format only (`kit/build.py`, kit v1.1). The website format does not carry it. If Matt wants it on a job, build that job in the classic format or port it, and publish with `capabilities: {"db": {}, "user": {"scopes": ["profile"]}}`.

## Phones

The website format is built for phones: the model frame sits above the copy, the step rail scrolls to the current step, the schedule unpins and plays as the chart scrolls past, the team sits in one row and the line detail drops to one column. `shoot.mjs` and `fitcheck.mjs` cover 390x844 and 375x667. If Matt reports a slow phone, ask which phone and whether the problem is the load or the scroll.

## Motion on a real screen

Matt judges the page live on Netlify in Chrome on a Mac at standard density, the first time he scrolls. Smooth frame rates are not enough: motion that is fine on a Retina screen shimmers on a 1x screen. Keep the kit rules (README, "Motion hygiene"): scroll-driven transforms in whole device pixels and never a scale on a photo or model frame, no layout property animated, unchanged values never rewritten, background decoding paused while the reader scrolls. Any new scroll effect follows them. Test scroll in a headless browser only against the `netlify/` build, which has a doctype; `site/` opens in quirks mode and does not scroll.

## Done means

- The preview artifact is published and Matt has a card for it. The live link changes only on his go.
- The Netlify zip is saved in 04 Deliverables with the next version number, deployed to `montana-<shortname>.netlify.app` and the deploy reads `ready`.
- The reply carries the cover email draft with the `Montana Budget - <Project Name>` subject.
- The budget ties to the TOTAL BASE BID row to the cent, and the reply says so.
- The frames passed the side-by-side review against the architect's rendering, and the copy and figures passed the fresh-context check.
- Every screenshot was looked at, desktop and phone.
- With a proposal PDF: the button downloads it on Netlify and in the preview, and `pdf_check.mjs` passes.
- With selections: `selections_check.mjs` passes and Matt has been told the one-time Netlify form setup.
- The reply lists open items only: unconfirmed titles, unpriced alternates, a schedule assumption, a rounding difference.

## Session gotchas

- Run one Blender render at a time. Two at once run out of memory.
- Never stop a background render with `pkill -f` on a pattern that also appears in your own command. Save the PID and kill that PID.
- In Blender scripts, set `display_percentage = 0` on particle systems, and keep leaf instances moderate.
- Odometer digit strips overflow their boxes, so `scrollHeight` overstates a block's height. Measure the content box instead.
- An author `display` rule beats the `hidden` attribute. Keep `[hidden] { display: none !important; }` at the top of the CSS.
- Watch for class names that collide with section names (a `.pc` percentage cell picked up the pre-con overlay styles).
- When a clip-path starts from a measured rect, turn the transition off, set the start state, force a reflow, then turn it back on. Otherwise it animates from the old state.
- Word masks clip with `clip-path`, not `overflow: hidden`, or the last letter of a word gets cut.
- The schedule span is the total weeks. A finish date that counts its own day lands a fraction past the last week, so clamp it.
- If WebFetch cannot reach a page, do not fetch it any other way. Ask Matt.
- Write job-folder files back (log, run state, CLAUDE.md) from a new path under the outputs folder, then check the size on the device. Reusing an outputs path once committed an older synced copy over the current file (E26049, 2026-10-17).
