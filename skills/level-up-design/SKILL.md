---
name: level-up-design
description: Tear down and rebuild a landing page or product site that is already weak, scored against an absolute design bar (not a model comparison). Trigger on site rebuild, this page is bad, redesign this page, fix my landing page, make this site not look AI-generated, page teardown, or when site-level-up returned nothing useful on a page the user already dislikes. Default mode is BUILD, not report.
license: MIT
metadata:
  type: workflow
  version: "1.0"
---

# Level Up Design

For pages that are already bad. The goal is a before/after a stranger can tell apart in 3 seconds. If the rebuild is not obviously different at a glance, the skill failed.

Sister skill: `site-level-up` protects pages that already work. This skill has no protection gate. The page does not work. Treat the existing design as a draft, not an asset.

## Hard rule

**Default mode is build.** Report-only output is a failure unless the user explicitly asks for report-only. The deliverable is a rendered new page plus side-by-side screenshots.

## Inputs

Ask once, then proceed on stated assumptions:

- URL or source path
- Product job in one sentence (who is this for, what should they do)
- The one action the page must drive (book call, sign up, buy)
- Hard constraints: logo, stack, anything legally locked. Everything else is negotiable, including color and fonts.
- Reference sites: the primary anchor is always `references/monday-night.md`, the monday.com Agents screen in Night theme. The wider set is `references/taste-profile.md`. Only ask if the user wants a different set for this run.

## Process

### 1. Capture the BEFORE (mandatory)

Screenshot the current page at 1440px desktop and 390px mobile, full page. Save as `before-desktop.png`, `before-mobile.png`. No screenshots, no rebuild. You must be able to see what you are fixing.

Run the automated evals in `references/evals.md` on the before page and record the numbers. This is the baseline.

Screenshot the primary anchor too: the monday.com Agents screen in Night theme at 1440px, saved as `anchor-monday-night.png`. It goes to the vision judge beside BEFORE and AFTER, and it is what the token diff in `references/monday-night.md` compares against. If monday is not reachable, say so in the scorecard and fall back to the token tables in that file.

### 2. Teardown against the absolute bar

Load `references/design-bar.md`. Score each of the 10 axes 0 to 3 using the rubric there. This is page-vs-standard. Never page-vs-model.

Then name the crimes. Every score of 0 or 1 gets a one-line verdict in the form:
`[axis] [what is wrong] [where on the page] [why it costs conversions]`

Vague verdicts are banned. "Typography could be improved" is not a verdict. "H1 and body both 16px/400, so the eye has no entry point above the fold" is.

### 3. Pick a direction before touching pixels

Load `references/direction.md`, `references/taste-profile.md` and `references/monday-night.md`. Use the taste profile's page-type rule to pick the camp. Commit to ONE named visual direction for the page with a one-paragraph rationale tied to the product job and buyer. Write the token set (type scale, 5-color palette with roles, spacing scale, radius, one motion rule) before any layout.

No direction = generic output. This step is what separates a rebuild from a restyle.

### 4. Rebuild the structure, then the skin

Order matters:

1. **Message.** Rewrite the hero headline, subhead, and CTA so a stranger knows what it is, who it is for, and what to do in 5 seconds. Bad copy in a beautiful layout still loses.
2. **Structure.** Re-sequence sections to match how the buyer decides (problem, proof, offer, action). Cut any section that does not move them toward the one action.
3. **Hierarchy.** One dominant element per viewport. Size and weight contrast of at least 2x between H1 and body.
4. **Skin.** Apply the tokens from step 3.
5. **Detail.** Hover, focus, press states, spacing rhythm, image treatment.

Minimum change floor: the rebuild must move at least 3 axes from 0-1 to 2-3. If it cannot, the direction is too timid. Go back to step 3 and pick a bolder one.

### 5. Vision self-check loop (mandatory)

Screenshot the AFTER at both widths. Look at before and after side by side. Answer in writing:

- Could a stranger tell these apart in 3 seconds? If no, you failed. Rebuild the hero.
- Does anything look like a default template (centered hero, gradient blob, 3 identical feature cards, generic stock icons)? Remove it.
- Re-score all 10 axes. Re-run the automated evals.
- Run the token diff against `references/monday-night.md`. Every `hard` rule must pass. List each `soft` rule that does not.

Loop until every axis is 2+ and the automated evals are at or above the thresholds in `references/evals.md`. Cap at 3 loops, then report what is still short.

### 6. Deliver

```
before-desktop.png / before-mobile.png
after-desktop.png  / after-mobile.png
anchor-monday-night.png
SCORECARD.md   # 10 axes before -> after, eval numbers before -> after, token diff hard/soft results
DIRECTION.md   # chosen direction + tokens
CRIMES.md      # every verdict and how it was fixed
<the rebuilt page source>
```

Lead the summary with the side-by-side, not prose.

## Anti-patterns

- Returning a report when the user wanted a better page
- Keeping the old layout and only swapping colors and fonts
- Designing before writing the tokens
- Beautiful page, same weak headline
- AI-default look: purple-blue gradients, glassmorphism cards, centered everything, emoji bullets, "Unlock the power of"
- Adding motion to hide a weak hierarchy
- Stopping after one pass without the vision self-check
