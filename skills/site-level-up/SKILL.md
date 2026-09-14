---
name: site-level-up
description: Level up a landing page or product site when a new frontier model ships. Trigger on site level-up, new model site pass, landing page wow, model-aware redesign, or selective UI upgrade based on model strengths not blanket restyle.
license: MIT
metadata:
  type: workflow
  version: "1.0"
---

# Site Level Up

Upgrade an existing site using a new model only on axes where that model is actually better. Do not restyle the whole site because a flagship shipped.

This is not `project-level-up`. That skill audits a full app. This skill is for a site or a primary marketing/app-entry surface.

## Mission

1. Build a capability delta between the incumbent model (what last touched this site) and the challenger (the new model).
2. Audit the live site for wow gaps.
3. Change only the intersection — site is weak AND challenger is stronger on that axis.
4. Protect axes where the incumbent or the current site already wins.

Default mode is report-only. Do not rewrite until the user names axes or pages.

## Inputs

Ask once if missing, then proceed with stated assumptions:

- Site URL and/or source path
- Challenger model name
- Incumbent model if known (what built or last revised this site)
- Product job in one sentence
- Hard constraints (brand tokens, stack, no new deps, etc.)

## Process

### 1. Capability delta (mandatory before any design work)

Load `references/capability-axes.md`.

For each axis score the challenger vs the incumbent as **up / same / down / unproven**.

Evidence, in order of weight:

1. The user's own last output from each model on this product
2. Design/frontend arenas and motion/vision evals, not overall IQ leaderboards
3. Reproducible public one-shots on similar sites
4. Vendor launch posts (lowest weight — treat as ads)

Rules:

- An overall "better model" score is not a license to touch type, motion, or layout.
- **Unproven** means do not bet the page. A small isolated probe is allowed. A rewrite is not.
- **Down** means keep the current treatment. Say so out loud.
- Write the delta card before proposing a single visual change.

Template is in `references/delta-template.md`.

### 2. Site audit

Load `references/wow-protocol.md`.

Score the current site on the same axes. Mark each as hold / gap / broken.

Hold = already strong. Do not "improve" it just to use the new model.

### 3. Intersection plan

A change is allowed only when:

- site axis = gap or broken
- challenger axis = up
- the move has a verify step

Everything else goes on the hold list or the probe list.

Cap the plan. Three high-leverage moves beat twelve taste edits.

### 4. Execute or report

Report pack:

```text
DELTA.md          # axis table + evidence
AUDIT.md          # current site, hold vs gap
PLAN.md           # allowed moves only
HOLD.md           # what we will not touch and why
```

If the user says implement, change only PLAN.md items. After building, self-check against HOLD.md so a new-model weakness did not regress a previous strength.

## How to talk about models

Name axes, not vibes.

Bad: "Fable 5.1 is better so redo the landing page."

Good: "Fable 5.1 is up on hierarchy and vision self-check, same on type, down or unproven on WebGL. We will push the hero hierarchy and add a vision pass. We will not rebuild the 3D canvas."

## Anti-patterns

- Blanket restyle on a model drop
- Using composite leaderboard rank as a design brief
- Adding motion because the new model likes animation
- Touching brand tokens that already work
- Throwing away a strong incumbent page to "see what the new model does"
- Implementing unproven axes at full page scale

## Invocation

```text
Load site-level-up.

Site: [url or path]
Incumbent model: [what last built this]
Challenger model: [new model]
Product job: [one sentence]
Do not write code yet.

Build the capability delta first. Only plan moves where the site is weak and the new model is actually up.
```
