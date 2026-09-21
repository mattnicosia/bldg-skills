---
name: site-level-up
description: Level up a landing page or product site. Trigger on site level-up, poorly designed UI, no wow, unrecognizable improvement, landing page wow, model-aware redesign, or selective upgrade based on model strengths. Rescue mode when the current page fails the two-second test.
license: MIT
metadata:
  type: workflow
  version: "1.1"
---

# Site Level Up

Two modes. Pick one in the first 20 lines of the run. Do not mix them.

| Mode | When | Job |
|---|---|---|
| **protect** | Page already has presence, brand, or a signature moment | Capability delta. Change only weak axes. Hold the rest. |
| **rescue** | User says poorly designed, no pop, no wow, unrecognizable improvement, or the two-second test fails on 3+ axes | Visible redesign of primary surfaces. Hold only IA, auth, and named brand tokens. |

If the user does not name a mode, infer it from the audit. A page that fails the two-second test is **rescue**. A page a sharp visitor would already pause on is **protect**.

Default after a failed run is **rescue**. The last version of this skill over-protected weak pages and shipped polish that nobody could see. That is a failed run.

## Mission

Protect mode

1. Build a capability delta vs the incumbent.
2. Change only site-weak AND model-up axes.
3. Hold what already works.

Rescue mode

1. Still write a short delta so you do not spend the page on an axis the model is bad at.
2. Then treat hierarchy, type scale, material, and one signature moment as mandatory work.
3. The pass fails unless a glance at before/after is obvious without reading the commit message.

## Inputs

Ask once if missing:

- Site URL and/or source path
- Mode if the user already knows (protect / rescue)
- Challenger model
- Incumbent model if known
- Product job
- Hard constraints (tokens, stack, no new deps)

Unknown incumbent does **not** mean hold everything. In rescue it means hold only constraints the user named.

## Process

### 0. Classify the page (mandatory)

Load `references/wow-protocol.md`. Answer the six audit questions. Count fails.

- 0–1 fails → protect
- 2 fails → ask, default protect if the user already likes the look
- 3+ fails → rescue
- User said "no visual improvement" / "unrecognizable" / "poorly designed" → rescue, skip the debate

Write the mode at the top of AUDIT.md.

### 1. Capability delta

Load `references/capability-axes.md` and `references/delta-template.md`.

Protect: a change still needs challenger **up** on that axis.

Rescue: hierarchy, type, color/material, and one signature moment are in the allow list unless the challenger is explicitly **down** on that axis. Unproven is allowed here. Same is allowed here. Only **down** blocks it.

Do not spend rescue budget on 3D/shaders or a motion system if those axes are down or unproven. Put presence into layout, type, and material instead.

### 2. Plan

Protect cap: 3 moves.

Rescue cap: 5 moves, and they must include all of

1. Extreme hierarchy on the one thing that matters (scale jump the current page does not have)
2. Type that is not the system default and not "slightly larger Inter"
3. Material / depth / presence so surfaces are not flat cards
4. One product-specific signature moment
5. Designed states for the primary CTA (hover, focus, loading, error)

If a planned move would not be visible in a 1200px screenshot from 5 feet, cut it. Spacing tweaks, token comments, and "subtle motion" are not rescue work.

### 3. Execute

Report pack first unless the user already said implement:

```text
DELTA.md
AUDIT.md          # includes mode + two-second verdict
PLAN.md
HOLD.md
BEFORE.md         # 6-line description of the current first screen
```

On implement, change PLAN.md items only. Then fill `AFTER.md` with the same 6 lines. If BEFORE and AFTER could describe the same screenshot, the run failed. Do another pass on hierarchy and the signature moment. Do not declare done.

## Visual acceptance (both modes, harder in rescue)

The run is not done when the code is prettier. It is done when:

- A sharp user sees a different page in two seconds
- One element owns the viewport
- There is a signature moment they could describe later
- Motion, if any, changed hierarchy rather than decorating an even layout

Failed acceptance language the agent is not allowed to use as success: polished, refined, cleaned up, tightened spacing, more consistent, slightly more premium, modernized.

## Anti-patterns

- Running protect logic on a page the user already called bad
- Shipping spacing and radius changes as a level-up
- Adding motion on an even layout
- Holding an ugly default because incumbent is unknown
- Declaring success without a before/after glance test
- New brand on a page that already has a working system (protect only)

## Invocation

Rescue (weak UI, or last run did nothing visible):

```text
Load site-level-up in rescue mode.

Site: [url or path]
The current UI is poorly designed. The last pass was not visible.
Do not protect the current look.
Implement the rescue allow list.
Success means a glance at before and after is obvious.
```

Protect (page already has presence):

```text
Load site-level-up in protect mode.

Site: [url or path]
Incumbent: [model]
Challenger: [model]
Hold the current system. Only touch weak axes.
```
