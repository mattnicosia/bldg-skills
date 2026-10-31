# Website format, section by section

Reference build: `kit/web/` (E260050 The Cooper Barn, v5.2). This file says what each section does and where it lives in the code, so a new job changes content and leaves the system alone.

## Build outputs

`python3 -I build.py` in `<project>/web/` writes:

- `site/index.html` plus `site/assets/`: the Artifact page. No doctype or skeleton, because the Artifact tool adds it.
- `netlify/index.html` plus assets and `robots.txt`: a full document with `noindex, nofollow`.
- `<JOB>_Presentation_Netlify_v#.zip` from `netlify/`.
- `figures.json`: every figure the page shows, for the fresh-context check.

Fonts (TT Commons Pro) are inlined as base64. Lenis 1.1.13 loads from jsdelivr. The page data (base, frame size, marker points and boxes, elements, alternates, schedule span and weeks) is a JSON block that `app.js` reads.

## Entry and loader

- The M assembles from its three polygons (`M_PIECES`, viewBox 0 0 773 652). The loader waits for fonts and the hero image, at least about 1.1 s, at most 3.4 s.
- The hero is the photo with a slow parallax and nothing over it. Matt turned down the WebGL effect.
- The nav goes solid on scroll, clear over the dusk image and navy over the Next Step. Links: Project, Design, Budget, Schedule, Approach. No buttons on the right except the phone menu.

## 01 / Project

- Facts column with a blue rule: Location, Type, Architect, Budget, Schedule.
- The lede is the whole project description (one paragraph, 40 to 80 words), lit word by word on scroll.
- The build lints the description: one paragraph, the first sentence is 155 characters or fewer, and the total is 40 to 80 words.

## Gallery

Pinned horizontal track on desktop, a swipe row on phones. Captions name the view (South Elevation, Southeast, Southeast at Dusk).

## 02 / Design (the stage)

- One frame, sized with container queries (`--fa` is the frame aspect from the crop). Frames are webp, cropped to the union of all frames' alpha with margins.
- Steps crossfade. A step can name a `via` frame that shows during the first part of its scroll (Site and Foundation uses the backfill frame), so the next build step never pops.
- Each element step sets the marker. Brackets use each element's blue-pixel box (`BB`, found from the white frames at build). Dot and leader use the projected point (`--points` from diorama.py). Badge shows the element number. On the final step numbered badges show on every element, pushed apart if they would overlap at the current size.
- The step rail sits under the model. On mid widths it moves to the model column, and on phones it scrolls to the current step.
- Kit v1.14: a step is a title, a figure and one caption line (14 words or fewer). No body paragraph.
- Titles use word masks with `clip-path`, and the odometer digits clip with `clip-path: inset(0 -.3em)`, so no letter or digit is cut.

## 03 / Budget

- Rolling base figure, a caption (Base Budget with Overhead and Profit, Direct Cost, 15% Overhead and Profit), the stacked bar and the two pills. The bar re-animates when the view changes. Hovering a row lights its segment, and the Overhead and Profit line under Direct Cost lights the grey one.
- Elements view: the project groups from project.json, by trade, with overrides by row where a trade's item belongs elsewhere (the cupola and weathervane sit in Building Envelope). MasterFormat view: divisions from the line codes.
- Rows open to their line items in two columns, codes shown in the MasterFormat view. No dollar figure per line, and unit rates are stripped from item names ("($600.00 Allowance)" reads "(Allowance)"). Estimator tags like "(Per Week)" are removed.
- Allowances: a ranked ledger (`aled`), largest first, each row a name, a bar and the figure, then the total, then the per square foot material rates in their own strip (`arate`). Money strings parse with `_num`.
- Selections (kit v1.7, when `<project>/selections.json` exists): sits between the budget rows and the Allowances, with its own nav link.
  Pills for Exterior, Interior, Site and List over one stage; numbered points open one sticky card beside it (below it on a phone).
  Options mode: tiles with a swatch or crop, the element change, the new total, a Request button; the render swaps or the site drive
  repaints with the pick. Rate mode: the carried rate, a dial between min and max with marks for matching value engineering items,
  the change and the new total. A bar under the stage shows Requested, If Montana Confirms and Send to Montana. List view is the
  schedule of every element: what the budget carries, the request and the change.
- Alternates: switches, a running total in cents (Requested), If Montana Confirms, and Send to Montana. The switches and the
  Selections cards are one set of requests saved on the device. The send sheet takes name, email, role and a note, posts the
  Netlify form `selections`, and falls back to an email to the decisions address.
- Notes and Clarifications: three closed groups (Basis of Budget, Clarifications, Exclusions), each showing its count and opening to the numbered list. Each fragment is checked against the Notes sheet at build. The full notes also live in the PDF.
- Kit v1.14: no hint under the budget pills, no lede under Alternates, no device line under Send to Montana.

## 04 / Schedule

- Phases come from schedule.json rows mapped to six phases with a blue ramp. Milestones are in weeks from mobilization, never calendar dates.
- Side panel: the total weeks, the headline, the live week odometer with the current phase name, and the phase list, each with a line that fills while the cursor is in it.
- The chart pins only if it fits the screen (measured from the grid, not `scrollHeight`). Row height scales with the screen height. If it does not fit, the cursor plays as the chart scrolls past.
- The cursor carries a "Week N" pill that slides from left aligned to right aligned so it never leaves the chart. The chart span equals the total weeks, so the cursor ends on the last milestone line.

## 05 / Approach

- Kit v1.13. Title How We Work, one statement in large type, then the `yteam` block: kicker Your Team, the line "Three principals stay on this project from the first walkthrough to the final punch list. You are never handed off." and the principals' portraits with name and title. The old `TIERS` numerals (1, 1, 3) are gone.
- Kit v1.14: no lede under the big statement. Montana OS on a light panel (`--off`): outline OS letters top right (`OS_LETTERS`, stroke only, navy at 20%), plain headings for This Job in Montana OS, What It Tracks and Who It Serves (the survey-theme `osx__st` mono labels and square bullets were removed in v1.11 to match the software). The app frame has a navy bar (M mark, Montana OS boxed, the project, "Opens at Award") and 2 by 2 tiles from the job's own numbers, the base budget tile in navy, ghost numerals 01 to 04. Features are numbered rows, names only (kit v1.14). Tiles show numbers only. Who It Serves is removed.
- No values list, no principles, no stats row.

## Pre-Construction

- The card: black, rounded 28px, the M watermark, "See Our Pre-Construction Process", "Four phases. One Guaranteed Maximum Price.", a See the Process button and the price band narrowing across the phases. The whole card is the button (Enter and Space work).
- On click the full view's clip-path starts at the card's rect and grows to the screen, so the card becomes the view's black header. Escape or Close shrinks it back.
- The view: the hero ("Know the number before you build.") with no lede, the phases, what each phase delivers (three bullets each), the promises (Walk-Away Guarantee, Unused Reserve Comes Back to You, One Rate) in one short line each, then the contact block. No section paragraphs and no principles (kit v1.14). Nothing project-specific.

- Kit v1.9: no ranges. Columns are Phase, name, Locks In (budget and scope, selections, trade bids, one GMP) and timing. The funnel has one tick per phase at its column center and no percentage labels. The card labels read Budget Set, Selections, Trade Bids, GMP.

## Thank you and Next Step

- The dusk render with a slow zoom and "Thank you for the opportunity to partner with you on this project."
- Navy Next Step with the M tone on tone, the working session line naming the architect and the owner, a Call button and Phone, Address, Email.

## Checks

| Script | What it checks |
|---|---|
| `shoot.mjs <out> both` | Screenshots at every scroll point, desktop 1440x900 and phone 390x844, plus page errors and sideways scroll |
| `interact.mjs <out>` | Pre-con open and close, MasterFormat view and row count, a row opening, alternates math, schedule weeks, every stage step's title and figure |
| `fitcheck.mjs <out>` | Copy against the model, the rail and the screen edges at 8 window sizes |
| `markers.mjs <out>` | The four marker styles on two elements, and the numbered badges on a phone |
| `precon_card.mjs <out>` | The totals block, line detail in both views, the card opening into the view, the OS panel, the dusk line and the close |
| `pdf_check.mjs <out>` | The Proposal PDF button: top right at 1440, 1200 and 900, clear of the section links, navy on the white nav, in the phone menu, the downloaded file's name and size, and the artifact path through the downloads capability |
| `selections_check.mjs <out>` | Selections: every view and both card modes at three widths, totals to the cent, the Alternates link, the form post, the email fallback, reload persistence (example in `kit/example_e26049/web/`) |
