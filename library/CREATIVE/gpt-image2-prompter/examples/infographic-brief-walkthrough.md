# Infographic Brief — End-to-End Walkthrough

This is a realistic, paste-ready walkthrough of generating a single infographic using the `luma-candle-co` brand profile. It shows the brief, the exact invocation, how brand YAML fields flow into the prompt slots, the composed 5-slot prompt, the settings, the expected output, a passing critique result, and an alternate failure + one-shot refinement.

## The brief

"Q3 2025 revenue by product line, with totals: Pillars $1.8M, Tapers $0.9M, Votives $0.6M, Accessories $0.3M."

Destination: board deck slide, landscape.

## Invocation

The user asks in chat:

> Make me an infographic for Q3 2025 revenue by product line using the Luma brand: Pillars $1.8M, Tapers $0.9M, Votives $0.6M, Accessories $0.3M. For a board deck slide, landscape.

The skill identifies `mode=infographic`, `brand=luma-candle-co`, no explicit size/quality/refs — all three pulled from the brand's `defaults` block and `refs` block.

## Brand slots injected

The skill reads `brands/luma-candle-co.yaml` from the workspace and substitutes fields into the 5-slot template. Each transformation below shows the YAML field on the left and the literal prompt text it becomes on the right.

### colors.primary → CONSTRAINTS (bar fill, headline, axis)

```
# YAML
colors:
  primary: "#0E3A5F"
```
→
```
# Prompt
Bars filled #0E3A5F. Headline and axis labels in #0E3A5F.
```

### colors.secondary → BACKGROUND (canvas)

```
# YAML
colors:
  secondary: "#F5E6D3"
```
→
```
# Prompt
Solid #F5E6D3 canvas, 1536x1024, 96px margins.
```

### colors.accent → CONSTRAINTS (hero bar highlight)

```
# YAML
colors:
  accent: "#D4A574"
```
→
```
# Prompt
Highlight the "Pillars" bar in #D4A574. Accent color used only for the hero bar.
```

### typography.display → LABELS (headline)

```
# YAML
typography:
  display: "Playfair Display"
```
→
```
# Prompt
Headline "Q3 2025 Revenue by Product Line" in Playfair Display 56pt bold.
```

### typography.body → LABELS (subhead, axis, value labels)

```
# YAML
typography:
  body: "Inter"
```
→
```
# Prompt
Subhead in Inter Regular 20pt. Value labels in Inter Semibold 18pt. Axis category labels in Inter Regular 16pt.
```

### logo.path + logo.usage → CONSTRAINTS (placement) + auto-attached as Image 2

```
# YAML
logo:
  path: "./logo.png"
  usage: "bottom-right, small, subtle"
```
→
```
# Prompt
Place the Luma Candle Co wordmark from the provided logo reference (Image 2) in the bottom-right at 120px width, subtle, low contrast.
```

Note: the logo never enters the prompt as a textual description — it enters as a reference image and is referenced by index.

### do → CONSTRAINTS (positive guidance)

```
# YAML
do:
  - "natural daylight, soft shadows"
  - "real bathroom, bedroom, or living-room contexts"
  - "single product hero"
```
→
```
# Prompt
(Note: these brand "do" entries are lifestyle-oriented and skip injection for infographic mode. Infographic-relevant "do" items flow through; lifestyle-only ones are filtered.)
```

### don't → CONSTRAINTS (negative guidance)

```
# YAML
don't:
  - "no neon colors"
  - "no cluttered scenes"
  - "no cartoonish illustration"
```
→
```
# Prompt
No neon colors. No cluttered scenes. No cartoonish illustration.
```

### refs.style_anchor → auto-attached as Image 1

```
# YAML
refs:
  style_anchor: "./luma-aesthetic.png"
```
→
```
# Prompt (CONSTRAINTS)
Image 1 is the Luma style anchor. Match its color temperature, grid discipline, and type hierarchy.
```

## Composed prompt

Here is the full 5-slot prompt that the skill composes and sends to GPT Image 2. Paste-ready:

```
BACKGROUND: Solid #F5E6D3 canvas, 1536x1024, 96px margins. Subtle
horizontal gridlines at 15% opacity in #0E3A5F. Clean, uncluttered stage.

SUBJECT: A clean vertical bar chart with four bars of varying height,
left-aligned on the canvas, occupying the right two-thirds of the
composition. Single chart, no secondary visualizations.

DATA: Four bars labeled "Pillars" $1.8M, "Tapers" $0.9M, "Votives"
$0.6M, "Accessories" $0.3M. Bars sorted descending by value. Y-axis
ticks at $0, $0.5M, $1.0M, $1.5M, $2.0M. Totals render exactly as
written: $1.8M, $0.9M, $0.6M, $0.3M — do not round, do not paraphrase.

LABELS: Headline "Q3 2025 Revenue by Product Line" top-left in
Playfair Display 56pt bold, #0E3A5F, appears once. Subhead "Luma
Candle Co · Fiscal Q3 2025" directly below in Inter Regular 20pt,
#0E3A5F at 60% opacity, appears once. Each bar labeled directly
above its top edge with its dollar value in Inter Semibold 18pt,
#0E3A5F — "$1.8M", "$0.9M", "$0.6M", "$0.3M", each appears once
in the position corresponding to its bar. X-axis category labels
"Pillars", "Tapers", "Votives", "Accessories" in Inter Regular 16pt,
#0E3A5F, directly below each bar.

CONSTRAINTS: Bars filled #0E3A5F. Highlight the "Pillars" bar in
#D4A574 as the hero value; accent color used only for that single
bar. No other colors in the palette. Render all text verbatim, do
not paraphrase, do not abbreviate — especially the dollar totals.
No drop shadows, no gradients, no 3D effects, no photorealism,
no texture, no camera effects. Pure flat vector infographic.
Generous whitespace, one idea per region, 80px minimum gap between
elements. No neon colors. No cluttered scenes. No cartoonish
illustration. Place the Luma Candle Co wordmark from the provided
logo reference (Image 2) in the bottom-right at 120px width, subtle,
low contrast — do not invent or redraw the wordmark. Image 1 is the
Luma style anchor — match its color temperature, grid discipline,
and type hierarchy. Designed for a board deck slide at 1536x1024.
```

## Settings

- **Size:** `1536x1024` (from `defaults.infographic_size`)
- **Quality:** `high` (from `defaults.quality`)
- **Refs attached (in order):**
  - Image 1: `examples/refs/luma-aesthetic.png` (auto-attached from `refs.style_anchor`)
  - Image 2: `examples/refs/logo.png` (auto-attached from `logo.path`)

## Expected output (placeholder)

A landscape 1536x1024 PNG on a warm cream canvas (#F5E6D3). Four vertical bars in deep navy (#0E3A5F) align along the right two-thirds of the frame, sorted descending: the tallest "Pillars" bar rendered in the warm tan accent (#D4A574) reads $1.8M at its top; the three shorter navy bars read $0.9M (Tapers), $0.6M (Votives), $0.3M (Accessories). A Playfair Display headline "Q3 2025 Revenue by Product Line" sits in the top-left at 56pt, with a small Inter Regular subhead "Luma Candle Co · Fiscal Q3 2025" beneath it at 60% opacity. Faint horizontal gridlines break the background at even $0.5M increments. The Luma Candle Co wordmark appears in the bottom-right corner at about 120px wide, deliberately muted. No shadows, no gradients, no 3D — a flat designed graphic suitable for a board deck.

## Critique result (pass example)

```
Critique: 16/18 (pass)

✓ Text legibility (3) — all four dollar totals render verbatim,
  headline and subhead crisp at 50% zoom, Inter vs Playfair hierarchy clean
✓ Brand colors (3) — #F5E6D3 canvas, #0E3A5F bars, #D4A574 on the hero
  bar, no off-brand drift
✓ Subject fidelity (3) — four bars present, sorted descending, values
  match the brief exactly
△ Composition (2) — hierarchy is correct but the subhead sits slightly
  tight under the headline; baseline spacing could breathe more
✓ Mode realism (3) — flat vector, no gradients, no texture — reads as
  a designer's Figma output
✓ Ref-lock (2) — logo preserved from Image 2 but rendered ~15% larger
  than requested; style anchor color temperature carried through

No refinement needed. Saved to outputs/2026-04-22_infographic_luma-candle-co_q3-revenue/
```

## Alt scenario (fail + refinement)

On a different seed, the first-pass output renders the "Pillars" value label as "$1.bM" instead of "$1.8M" — the `8` glyph fused into a lowercase `b`. Everything else passes.

```
Critique: 15/18 (fail)

✗ Text legibility (1) — "Pillars" value label reads "$1.bM" instead
  of "$1.8M" — the digit 8 rendered as a lowercase b. The other three
  totals ($0.9M, $0.6M, $0.3M) are correct.
✓ Brand colors (3) — palette clean, accent reserved for hero bar
✓ Subject fidelity (3) — four bars, correct categories, sorted descending
✓ Composition (3) — hierarchy reads headline → hero bar → supporting
  bars → axis, margins breathe
✓ Mode realism (3) — flat vector, no photorealism
△ Ref-lock (2) — logo slightly larger than specified, acceptable

Proposed refinement (single surgical change, preserves everything else):

┌─ refinement prompt ─────────────────────────────────────────────┐
│ Regenerate the same infographic. Preserve: the four bars and    │
│ their descending order, all three other value labels exactly    │
│ ($0.9M for Tapers, $0.6M for Votives, $0.3M for Accessories),   │
│ the headline "Q3 2025 Revenue by Product Line", the subhead     │
│ "Luma Candle Co · Fiscal Q3 2025", axis ticks at $0, $0.5M,     │
│ $1.0M, $1.5M, $2.0M, the #F5E6D3 canvas, the #0E3A5F bar fill,  │
│ the #D4A574 accent on the Pillars bar, Playfair Display headline│
│ typography, Inter body typography, the logo placement in the    │
│ bottom-right from Image 2, and the overall layout.              │
│                                                                 │
│ Change ONLY the "Pillars" value label: it must read exactly     │
│ "$1.8M" — a dollar sign, the digit 1, a period, the digit 8,    │
│ then the capital letter M. Do not render the 8 as a b. Spell    │
│ one-point-eight-M. Render this label verbatim, appears once,    │
│ above the Pillars bar in Inter Semibold 18pt #0E3A5F.           │
└─────────────────────────────────────────────────────────────────┘

Run refinement? (y/n)
```

Why the refinement follows the discipline rules from `references/critique-rubric.md`:

1. Starts with "Regenerate the same infographic." — anchors to the prior output.
2. Re-states the full preservation list, not just the bits that changed.
3. Makes exactly one surgical change: the single glyph fix.
4. References Image 2 by index for the logo.
5. Names the failure mode ("8 rendered as b") and the target state ("a dollar sign, the digit 1, a period, the digit 8, then the capital letter M") concretely.

## Metadata sidecar

`outputs/2026-04-22_infographic_luma-candle-co_q3-revenue/metadata.json` after a passing first run:

```json
{
  "skill_version": "0.1.0",
  "timestamp": "2026-04-22T10:34:17-05:00",
  "mode": "infographic",
  "brand": {
    "slug": "luma-candle-co",
    "schema_version": 1
  },
  "brief": "Q3 2025 revenue by product line, with totals: Pillars $1.8M, Tapers $0.9M, Votives $0.6M, Accessories $0.3M.",
  "prompt_slots": {
    "background": "Solid #F5E6D3 canvas, 1536x1024, 96px margins. Subtle horizontal gridlines at 15% opacity in #0E3A5F.",
    "subject": "A clean vertical bar chart with four bars of varying height, left-aligned on the canvas, occupying the right two-thirds of the composition.",
    "data": "Four bars labeled Pillars $1.8M, Tapers $0.9M, Votives $0.6M, Accessories $0.3M.",
    "labels": "Headline in Playfair Display 56pt bold #0E3A5F. Subhead in Inter Regular 20pt. Value labels in Inter Semibold 18pt.",
    "constraints": "Bars filled #0E3A5F, Pillars highlighted #D4A574. Flat vector, no photorealism. Logo from Image 2 bottom-right 120px."
  },
  "settings": {
    "size": "1536x1024",
    "quality": "high"
  },
  "refs_attached": [
    {"index": 1, "role": "style_anchor", "path": "examples/refs/luma-aesthetic.png"},
    {"index": 2, "role": "logo", "path": "examples/refs/logo.png"}
  ],
  "output": {
    "filename": "image.png",
    "bytes": 418203,
    "width": 1536,
    "height": 1024
  },
  "critique": {
    "score": 16,
    "max": 18,
    "passed": true,
    "dimensions": {
      "text_legibility": 3,
      "brand_colors": 3,
      "subject_fidelity": 3,
      "composition": 2,
      "mode_realism": 3,
      "ref_lock": 2
    },
    "notes": "Strong pass. Minor: subhead baseline a touch tight, logo ~15% larger than requested.",
    "refined_from": null
  }
}
```

For the failed-then-refined branch, a second directory `outputs/2026-04-22_infographic_luma-candle-co_q3-revenue-refined/metadata.json` is written with `critique.refined_from` set to the path of the original `image.png`.
