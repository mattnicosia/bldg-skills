---
name: generate-proposal-mcc-living-01
description: Build a Montana Contracting living proposal, a scroll presentation where the model builds as you scroll, plus the budget, alternates, schedule, pre-construction, principals and a Detailed Budget, from the estimate workbook and drawings or a 3D model.
---

# Generate Proposal MCC Living 01

The client-facing living proposal Montana sends with a budget or bid. One page. A model of the house builds as the reader scrolls, then the number, the alternates, the schedule, pre-construction, how we run the job, the principals and a thank-you, with a Detailed Budget behind a button. The first one was job E26040, a modular residence for an architect-led client. The PDF proposal is a separate deliverable (generate-proposal-mcc). This page goes alongside it.

Call it a "presentation". The budget view is the "Detailed Budget". Options are "Alternates". Lead with Montana Contracting. Never show or mention NOVATERRA or any internal tool.

## The kit

All code lives in the Bid Presentation Kit. Do not rebuild it from scratch.

- Master copy: `MCC\Estimating\Misc. Templates\Bid Presentation Kit\` on the Montana shared drive.
- If that folder is not there yet, the latest zip is in the E26040 job folder under `05 Claude Cowork\` (v1.1 adds the Decision List). Ask Matt to move it to Misc. Templates once.
- To get it into the session:
  1. Stage the zip from the linked computer, or ask Matt to attach it.
  2. Unzip it into the working directory.
  3. Run `npm i` in `kit/`.
  4. Run `pip install openpyxl pillow --break-system-packages`.
  5. Make sure `pdftoppm` (poppler) is available; the drawing tools need it.
- `kit/README.md` is the reference for every field in project.json and massing.json. Read it before writing either.
- `kit/example/` is a complete project (massing built from drawings). Copy it as the starting point for a new job.

If you improve the kit during a job (a fix, a new stop type), bump the version, rezip it and save it back to Misc. Templates. Say what changed.

## Order of work

1. **Gather first.** Before any build, collect:
   - The final estimate workbook in the house format: SOV with Final Price, markups, Alternates block, Notes & Clarifications. If the estimate is not final, the presentation is not final. Say so.
   - The schedule: a real one (CPM, P6, the working-schedule workbook) or Matt's dates. Never invent durations. `tools/schedule.py` turns an activity CSV into schedule.json.
   - The drawings: plans, elevations, sections, finish schedule.
   - Any 3D model. Ask the architect for it. A SketchUp, Revit or Rhino export to .glb saves the most time.
   - The architect's requested pricing format, if any. One architect asked for Site Work, Foundation, House, Garage, Decks, Hardscape. Use it for `groups`.
2. **Pick the model source** (README, "The three model sources"):
   - **Architect model available:** use `glb`. Tag groups with `[phase:...]` and `[alt:N]`, or map node names in `model.phaseNodes` and `model.altNodes`.
   - **Drawings only:** use `massing` and the drawings-to-massing skill. Elevation skins make it read like a paper model of the real house.
   - **Neither, or no time:** use `images`, with renders (`"fit": "cover"`) or drawings.
3. **Write project.json.** Copy `kit/example/project.json` and replace everything.
   - Map phases to schedule rows (`"sched"`) so the model rises in calendar time on the schedule stop.
   - Mark which alternates to feature on the Alternates stop, and say on each whether it shows on the model.
4. **Write the copy** with the montana-web-voice skill. The rules below are Matt's and override defaults.
5. **Build:** `python3 build.py <project>`.
   - It stops if the base does not tie to the workbook to the dollar, if a trade is not in a group, or if copy breaks the house rules.
   - Fix the cause. Do not set `allow_lint` on a final.
6. **Check:** run `node tools/check.mjs <project> both`, then `python3 tools/sheet.py <project> desktop` and `phone`.
   - Open both sheets and look at every frame.
   - Headlines fit.
   - The model is framed beside the copy, not under it.
   - Phases rise in order.
   - The schedule chart reads.
   - The numbers match the workbook.
   - Fix the camera with `view` presets or exact poses.
7. **Publish:**
   - Publish `out/presentation.html` with the Artifact tool, with `capabilities: {"db": {}, "user": {"scopes": ["profile"]}}` so the Decision List saves for everyone on the link. The same file path keeps the URL. After the first publish, list the `decisions` and `log` collections with ArtifactData once to confirm the store answers.
   - Save `out/<JOB>_Presentation_Netlify.zip` to the job's `04 Deliverables` as `<JOB>_Presentation_Netlify_v#.zip`, using the next version number. Matt drags it onto Netlify. It carries noindex.
   - Record the artifact URL, the final numbers and the open questions in the Claude project doc for the job.

## Decision List

On by default (kit v1.1). A header button opens every alternate (Include, Not Now, Discuss) and every `decision` milestone in schedule.json (Confirmed, Open), each with a note, who answered and when, a working total, and an activity log. It turns the presentation into the start of pre-construction.

- **Where it saves:** shared saving works only in the claude.ai artifact. On Netlify or in a saved copy, answers last for the visit, and the email button sends the list to Montana.
- **Sharing:** tell Matt how to share it. People outside Montana can save answers only if he invites them by email as Editor, and only while the artifact is not also shared by public link. Editors can also republish the page, so he should invite only the people who should answer.
- **Selections:** put the selection deadlines in schedule.json as a `decision` row with dated milestones, so they appear as Selections.
- **Before the working session:** read the answers back with ArtifactData (`decisions`, `log`) and summarize them for Matt: what was included, what is under discussion, and the notes.
- **Schedule impact:** do not add a schedule impact to an alternate unless Matt gives its duration.

## Copy rules from Matt

- No em dashes anywhere. No "X, not Y". No questions, exclamation points or semicolons. Title Case for every label that is not a sentence.
- Headlines are plain titles or flat facts. Use the stop names that worked: "Project History", "Site Conditions", "Modular Scope", "Building Envelope & Exterior Finishes", "Finishes", "Preliminary Schedule", "Pre-Construction", "How We Run the Job", "The Principals".
- The opening headline credits the architect and is something the owner and architect both feel good reading (for example "Designed by <Architect>. Ready to build."). Offer Matt five options and say which one you put in.
- Never put risk in front of the client. Use "Key to Success" and "Our Approach". When the design already handles it, add "In the Design" and credit the engineer or architect. Never take credit for the design team's measures.
- Coordination with other contractors (slope repair, abatement, utility) reads as partnership and a clean handoff. Avoid contract-boundary lines such as "in our budget, below the line is theirs" or "not in our price".
- Never show where the documents disagree. It makes the architect look bad.
- Pre-Construction: "We find solutions that hold the design intent, the quality and the excitement that started the project." Mention the proprietary cost database. Do not show another client's numbers; they confuse the reader.
- Keep reading light: one idea per screen, short lines, numbers as the design object.
- Every claim must match the estimate notes. If winter protection, dewatering, rock or deeper fill are excluded, the copy cannot say they are carried.
- Principals are Joe Montana (Founder and CEO), Matt Nicosia (COO) and Chris Lange (Director of Construction). Show each person once. Confirm titles if anything changed.

## Numbers

- The Budget stop shows the base in millions, the groups as strata and the markups as one line.
- The Detailed Budget shows direct cost by trade, then the markups compounding in order. Markup rates come from the workbook. Never hand-type them.
- Alternates show the workbook's Final Price, with markups. A blank price shows "Not Priced". Deducts show negative.
- Exclusions and By Owner come straight from the Notes & Clarifications sheet. Clarifications go in only if Matt wants them (`include_clarifications`).
- Check the General Requirements duration in the workbook against the schedule length. Tell Matt if they differ.

## Phones

The kit already handles phones: it stops redrawing at rest, ignores address-bar resizes and drops quality on slow devices. If Matt reports a slow phone, ask which phone and whether the problem is the load or the scroll. The usual levers, in order:

1. Lower `zoom`.
2. Cut trees.
3. Simplify the GLB.
4. Switch the job to `images`.

## Done means

- The artifact is published with the db and user capabilities, and Matt has a card for it.
- The Netlify zip is saved in 04 Deliverables.
- The budget ties to the workbook to the dollar, and the reply says so.
- Both contact sheets were looked at.
- The reply lists open items only: unconfirmed titles, unpriced alternates, a schedule assumption.
