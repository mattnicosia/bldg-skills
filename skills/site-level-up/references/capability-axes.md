# Capability axes

Score models on these axes. Do not collapse them into one rank.

## Axes that matter for sites

| Axis | What "up" looks like on a site | What "down" looks like |
|---|---|---|
| Hierarchy | One thing owns the first second; scale contrast is decisive | Even, polite, card-grid default |
| Type | Distinct pairing, optical size, real scale | Inter/system defaults, display type too big or too timid |
| Color and material | Restraint, presence, surfaces with weight | Soft gradients, glass slop, muddy midtones |
| Motion | Few moves that change hierarchy; correct scroll; reduced-motion | Carnival animation, broken scrub, layout jank |
| Page coherence | Multi-section site stays on-system | Hero is sharp, footer looks like another product |
| Vision self-check | Model looks at the page and fixes hierarchy/contrast | Ships code that does not match the brief |
| Constraint respect | Holds a design system and a ban-list | Ignores "no pills / no Inter / no teal" |
| Copy and tone | Specific, short, product-true | Generic SaaS adjectives |
| Interaction / states | Hover, focus, empty, error feel native | Pretty static mock |
| 3D / shaders | Intentional, performant, on-brief | Cheap WebGL demo bolted on |
| A11y and contrast | AA where it matters, real focus | Pretty and unusable |
| Front-end correctness | Semantic, stable, 60fps enough | Looks good in a screenshot, breaks on scroll |

## Evidence ranking

Use this order. Say which tier you used.

1. **First party** — this user's previous pages from each model
2. **Task-matched evals** — Design Arena, frontend vibe benches, motion/vision checks
3. **Nearby one-shots** — public pages in the same genre
4. **Composite model rank** — intelligence/coding leaderboards
5. **Launch blog** — ignore unless it names a test you can inspect

Tier 4–5 cannot unlock a rewrite by themselves.

## Common mismatch patterns

- New model wins coding agents, loses design taste → keep the look, use it for implementation only
- New model wins vision, same type → add a visual QA pass, do not swap fonts
- New model wins long context, weaker motion → let it hold the whole page system, do not add more animation
- New model is cheaper and "close enough" → maybe demote cost, do not restyle

## When evidence conflicts

Prefer the axis that would hurt the current site if you are wrong.

If hierarchy is already strong, do not gamble it on an unproven model.
If hierarchy is weak and the model is up on hierarchy, that is the bet.
