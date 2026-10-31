# Website format (kit v1.10)

The default client presentation since E260050 The Cooper Barn (v5.2, approved by Matt on 2026-10-16).
`build.py` here is that job's build, kept whole as the reference. Copy the folder to `<project>/web/`
and change the blocks marked `# JOB`. Everything else (layout, motion, budget views, schedule, approach,
pre-construction) is shared and should not need edits.

```
<work>/kit/                    this kit (or set MCC_KIT)
<work>/<project>/              project.json, schedule.json, estimate.xlsx, hero/, model_el.glb
<work>/<project>/web/          this folder
    render_model.sh            Cycles frames: color build steps on a land block, white elements in Montana blue
    build.py                   -> site/ (Artifact page), netlify/ (full document, noindex), <JOB>_Presentation_Netlify_v#.zip, figures.json
    figures.py                 prints direct, overhead and profit and base to the cent
    src/app.js, src/style.css  the page
    shoot.mjs                  screenshots at every scroll point, desktop and phone
    interact.mjs               pre-con open and close, budget pills and rows, alternates math, schedule weeks, stage figures
    fitcheck.mjs               copy against the model and the rail at 8 window sizes
    markers.mjs                the four element marker styles side by side
    precon_card.mjs            budget totals, line detail, the pre-con card opening into the full view
<work>/<project>/proposal/<one>.pdf  optional: the Proposal PDF button, top right (pdf_check.mjs checks it)
<work>/<project>/selections.json   optional: the Selections section (see the kit README, Selections). Example in example_e26049/
```

Run order: `bash render_model.sh` (background, about 100 s a frame), with selections also `bash render_selections.sh`,
`python3 -I build.py`, then the four checks (and `selections_check.mjs` when the job has selections, `pdf_check.mjs` when it has a proposal PDF).
Test on `netlify/`, never `site/` (no doctype there, so a local browser opens it in quirks mode and nothing scrolls).
Marker styles switch with `#mk-dot`, `#mk-leader` or `#mk-badge` on the page URL. Brackets are the default.


kit v1.16: `tools/scope/wording.py` (client wording and directives, merge keys) is imported by `build.py`. Optional sections are switched in project.json `"sections"`. The build also writes `scope_lines.json` and `proposal_lists.json` for the PDF proposal.
