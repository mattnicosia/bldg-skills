---
name: ui-motion-design-kvnkld
description: A UI motion and interaction design skill for adding premium motion design and micro-interaction polish to web interfaces, so they read as designed by a human with taste instead of generic or AI-generated. Covers a house easing set, design tokens, physics-based drag, magnetic snap points, blur-in entrances, layered-light shadows, tactile press states, grid-row reveals, FLIP transitions, reduced-motion accessibility, and state-driven component design. Use whenever building or refining frontend components (buttons, sliders, modals, cards, tooltips, dropdowns, expand/collapse, drag handles) or any time the user wants a UI to feel polished, premium, tactile, weighty, springy, like iOS or a real app, better designed, or less AI-generated. Trigger even when the user only says make it feel nicer, add some polish, improve the design, or the animations feel cheap, not just on explicit motion-design requests. Originally distilled from the UI motion design principles shared by @kvnkld.
---

# UI Motion Design

> Distilled from the UI motion design principles shared by **@kvnkld** on X. Credit for the taste and the original numbers is his; this skill just makes them reusable.

The gap between "an LLM built this" and "a person with taste built this" is almost never the layout. It is the motion: how things start, speed up, settle, press, and reveal. This skill encodes the specific values and patterns that close that gap. The judgment behind the numbers is taste; the numbers themselves are reusable.

The whole skill in one line: **give numbers, never adjectives.** "Smooth" is meaningless and unbuildable. A specific curve at 280ms is buildable.

## Step 0: Lay the foundation first

Before building a single component, load the design tokens in `assets/tokens.css`. Polish reads as consistency, and consistency comes from a shared vocabulary that every state, hover, and dark-mode variant pulls from. With tokens in place the UI stops inventing one-off 13px radii and random 0.3s timings.

Forbid one-off values: "Use only these tokens, no ad-hoc numbers." That single instruction kills most of the generic look. When working in Figma, build Figma variables that mirror these token names 1:1 so design and build is a translation, not a reinvention.

The token file already includes the house easing set, radius/duration scales, two layered shadow presets, the tactile press default, and a reduced-motion block. Read it before applying any rule below.

## The ten rules

Each rule is a lever. Apply the ones the current component needs; you rarely need all ten at once. Concrete code for the heavier ones lives in `references/recipes.md`.

**1. Easing is everything; the default ease is banned.** Never use `ease` or `ease-in-out`. Use `--ease-smooth` for almost everything, `--ease-spring` for anything that pops in with a tiny overshoot (badges, toasts), `--ease-out` for decorative entrances. When prompting, give the exact curve, never the word "smooth."

**2. Define tokens before components.** See Step 0. This is the highest-leverage move in the skill.

**3. Draggable things use real physics, not timed slides.** Velocity tracking smoothed over recent frames, momentum that coasts to rest on release, and soft boundaries that stretch and spring back at the edge. For values that can't ride a fixed duration (counters, live numbers), drive them with a spring tuned for stiffness/bounce/weight. See recipes 4 and 6.

**4. Snap points are free haptics.** As a handle nears a meaningful value, magnetize to it. The detail that sells it is a two-zone system: a tight pull-in zone to catch, a larger release zone to break free, so once snapped the user has to mean it to leave. Pulse the label on catch. See recipe 5.

**5. Entrances blur in; they never just fade.** Combine three things: opacity 0 to 1, translateY 6px to 0, and `blur(2px)` to `blur(0)`, around 280ms on `--ease-smooth`. The clearing blur makes content focus into place instead of flicking on. Tooltips use the same recipe at 4px and `--duration-fast`. See recipe 1.

**6. One shadow is a sticker; real depth is layered light.** Use `--shadow-card` and `--shadow-elevated`. Three things make them read as real: a hairline ring replaces the border (the edge is defined by light, not a 1px stroke), opacities stay tiny (2% to 8%), and several blurs stack at different sizes (a tight contact shadow plus a wide soft ambient). Animate the whole stack on hover, not a single blur.

**7. Make everything tactile; press should be felt.** Every interactive element scales to 0.98 on `:active` (the token file wires this up). 0.98, not 0.9, so it reads as a firm press, not a collapse. Buttons, swatches, tabs, footer rows, all of them. Pair with hover shifts and blur-lift tooltips.

**8. Reveal height the right way.** Animate `grid-template-rows: 0fr` to `1fr`, never a `max-height` hack, which is jittery and times wrong. For an element moving between containers, use FLIP (First, Last, Invert, Play): two position measurements that look impossibly smooth. See recipes 2 and 3.

**9. Respect performance and accessibility, or it is not polished.** Honor `prefers-reduced-motion` everywhere (the token file does this globally; animations collapse to instant, decorative loops stop). For 60fps, favor the cheap properties (transform, opacity) over heavy ones (shadow stacks, height reveals) on long lists and large surfaces. Spend the heavy effects in small, deliberate moments.

**10. State-driven design is the actual job.** A component is not a picture; it is a system of states: idle / hover / pressed / loading / disabled / success. The crucial insight: you discover the states you need by building, not by speccing. The Figma frame always looks complete; then you drag the thing and feel the holes ("this needs a working state," "the number should roll, not swap," "the icon should cross-fade between play and pause"). Build the states you know as variants, then expect the build to surface two or three more. That is where the polish actually lives. See recipe 7 for working-state micro-interactions (shimmer, digit roll, icon cross-fade).

## How to prompt for this (when guiding a model or yourself)

- **Numbers, not adjectives.** A specific curve at a specific duration is buildable; "smooth" is not.
- **Lead with the tokens.** Paste the token block first and forbid one-off values.
- **Think in states, then list them.** The model builds exactly the states you name and no more, so name them.
- **Isolate when iterating.** "Now only tune the shadow stack." "Now only the entrance." One variable at a time reaches polish without thrashing.
- **Describe the feeling plus a reference.** "Should feel like an iOS sheet: weighty, slightly springy, settles fast." Reference-anchored requests land far better than abstract ones.
- **On Figma handoff, name every property to copy.** Point at the current selection and list exactly what to read off it: padding, gaps, tokens, colors, corner radius, type sizes and weights. Never assume the handoff carries it all over on its own.

## The part the model does not supply

The model is the hands; the eye is yours. It will build a flawless spring or card-flight faster than anyone by hand, but it did not decide the press should be 98% not 95%, that the entrance needed a 2px blur, or that the release zone should be bigger than the pull-in zone. Those calls come from feel. When a value in this skill seems almost right for the case at hand, trust the discomfort and nudge it. A curve 0.02 off feels subtly wrong even when you can't name why, and naming why is the job.

## Files in this skill
- `assets/tokens.css`: drop-in foundation: easing set, radius/duration scales, two shadow presets, tactile press, reduced-motion. Load first.
- `references/recipes.md`: full code for the heavier patterns: blur entrance, grid-row reveal, FLIP, drag physics, two-zone snapping, value springs, and working-state micro-interactions.
