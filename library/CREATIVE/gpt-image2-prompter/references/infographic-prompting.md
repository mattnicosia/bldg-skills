# Infographic Prompting

## Overview

Infographic prompting — designed-feel, data-forward, text-legible images.

## When to use this mode

Use `infographic` mode for images whose job is to communicate structured information, not set a mood. Pick it for:

- Bar, line, and pie charts
- Comparison tables (Before vs After, Plan A vs Plan B)
- Stat cards (single headline number plus supporting copy)
- Process flows and step diagrams (3-, 5-, 7-step sequences)
- Quote cards with attribution
- Explainer diagrams (labeled parts, annotated screenshots, concept maps)

If the brief asks for a person, place, or product in a scene, switch to `lifestyle` mode instead.

## Prompt template

Fill every slot. The ordering — background → subject → data → labels → constraints — is load-bearing: it matches how GPT Image 2 parses the prompt.

```
BACKGROUND: <canvas color or gradient, margins, overall grid feel>
SUBJECT:    <the single visual idea — "a vertical bar chart", "a 5-step horizontal flow", "a stat card">
DATA:       <the exact numbers, categories, or step names that must appear>
LABELS:     <every literal string that must render, in quotes, with typography direction>
CONSTRAINTS: <brand colors as #HEX, fonts, do/don't list, "no photorealism", "appears once" markers>
```

What goes in each slot:

- **BACKGROUND** — sets the stage first so the model locks composition before drawing content. One or two sentences: canvas color, optional subtle grid, whitespace margin size.
- **SUBJECT** — one short noun phrase naming the structure. Avoid layering multiple structures in a single image.
- **DATA** — the ground-truth values. Spell out numbers (`$1.2M`, `92%`, `Step 1 of 5`). If a value must be exact, repeat it.
- **LABELS** — every string that must render, wrapped in double quotes. Call out placement and typography per label.
- **CONSTRAINTS** — brand lock-down and negative guidance. This is where you block photorealism, enforce hex colors, and reinforce spelling.

## Default settings

- `quality="high"` — always, for any infographic. Lower quality garbles small text.
- Size: `1536x1024` (landscape) by default. Dashboards, comparison tables, and process flows all breathe better in landscape.
- Size: `1024x1536` (portrait) only when the brief explicitly calls for a social post (Instagram feed, Pinterest, LinkedIn image card).
- Size: `1024x1024` for square social (Instagram grid, X card) when requested.
- Never exceed `2560x1440` QHD.
- State intended use in the prompt itself ("designed for a LinkedIn feed post at 1200x627"). This nudges composition.

## Text-rendering discipline

Five rules, applied to every infographic prompt. These come straight from the OpenAI GPT Image prompting guide and are non-negotiable for this mode.

1. **Wrap literal text in double quotes or write in ALL CAPS.** The model treats quoted strings and ALL CAPS tokens as verbatim rendering targets.
2. **Specify typography for every visible string.** Font family, weight, color, and placement — e.g., `"Q3 Revenue" in Inter Bold 48pt, #0E3A5F, top-left, 64px from edge`.
3. **Spell brand names letter-by-letter the first time they appear.** `"A-C-M-E"` then `"ACME"`. This prevents the model from hallucinating letterforms.
4. **Demand verbatim rendering explicitly.** Add `render this text verbatim, do not paraphrase` in the CONSTRAINTS slot.
5. **State "appears once" for any single-instance string.** Otherwise the model will duplicate headlines and labels across the canvas.

## Brand-slot injection pattern

Brand profile YAML values flow into prompt slots using literal substitution. Given a brand with:

```yaml
brand:
  colors:
    primary: "#0E3A5F"
    accent: "#E8B04B"
    neutral: "#F5F2EC"
  typography:
    display: "Playfair Display"
    body: "Inter"
  logo: "assets/brand/acme-logo-dark.svg"
  do:
    - "generous whitespace"
    - "left-aligned headlines"
  dont:
    - "drop shadows"
    - "gradients on type"
```

The slots compose as:

- **BACKGROUND** gets `brand.colors.neutral`:
  `Canvas: solid #F5F2EC with 96px margins on all sides.`
- **LABELS** gets `brand.typography.display` and `brand.typography.body`:
  `Headline in Playfair Display 56pt bold, #0E3A5F. Body in Inter Regular 18pt, #0E3A5F at 80% opacity.`
- **CONSTRAINTS** gets `brand.colors.primary`, `brand.colors.accent`, `brand.do`, `brand.dont`, and `brand.logo`:
  `Primary color #0E3A5F. Accent color #E8B04B used only for the hero value. Generous whitespace. Left-aligned headlines. No drop shadows. No gradients on type. Place the ACME wordmark logo (provided as reference image) in the bottom-left at 120px width.`

Rule: **the logo always enters the prompt as a reference image, never as a description.** Describing a logo causes the model to invent one.

## Five worked examples

### 1. Bar chart — "Q3 revenue by product line"

Brief: Four product lines, vertical bar chart, brand ACME, landscape for a board deck.

```
BACKGROUND: Solid #F5F2EC canvas, 1536x1024, 96px margins. Subtle horizontal
gridlines at 20% opacity in #0E3A5F.
SUBJECT: A clean vertical bar chart with four bars of varying height, left-aligned
on the canvas, occupying the right two-thirds of the composition.
DATA: Four bars labeled "Core" $1.2M, "Pro" $2.8M, "Enterprise" $4.1M,
"Add-ons" $0.6M. Y-axis ticks at $0, $1M, $2M, $3M, $4M, $5M.
LABELS: Headline "Q3 Revenue by Product Line" top-left in Playfair Display
56pt bold, #0E3A5F, appears once. Subhead "Fiscal Year 2026" directly below
in Inter Regular 20pt, #0E3A5F at 60% opacity. Each bar labeled above with
its dollar value in Inter Semibold 18pt, #0E3A5F. X-axis category labels
in Inter Regular 16pt.
CONSTRAINTS: Bars filled #0E3A5F, highlight the "Enterprise" bar in #E8B04B.
Render all text verbatim, do not paraphrase. No drop shadows, no gradients,
no 3D effects, no photorealism. Pure flat vector infographic. Designed for
a board deck slide.
```

Why this works: one subject, exact numbers quoted, accent color reserved for the single hero bar, photorealism explicitly blocked.

### 2. Process flow — "5-step user onboarding"

Brief: Horizontal 5-step flow, pill-shaped nodes with arrows, social landscape.

```
BACKGROUND: Solid #F5F2EC canvas, 1536x1024, 80px margins. No grid.
SUBJECT: A horizontal 5-step process flow. Five pill-shaped nodes evenly
spaced across the middle of the canvas, connected by thin arrows pointing
left to right.
DATA: Step 1 "Sign up", Step 2 "Verify email", Step 3 "Pick a plan",
Step 4 "Invite team", Step 5 "Ship first project". Numbered 1 through 5.
LABELS: Headline "How onboarding works" top-left in Playfair Display 48pt
bold, #0E3A5F, appears once. Each pill contains its step number in Inter
Bold 32pt, #FFFFFF, centered, and the step label below the pill in Inter
Semibold 18pt, #0E3A5F. Arrow connectors in #0E3A5F at 60% opacity.
CONSTRAINTS: Pills filled #0E3A5F. Step 5 pill filled #E8B04B to signal
completion. Generous whitespace between nodes. Render the five step labels
verbatim. No drop shadows, no photorealism, no human figures, no icons
inside pills — numbers only. Flat vector infographic.
```

Why this works: the step strings are quoted and explicitly verbatim; the model knows exactly five nodes, not "around five".

### 3. Stat card — "Customer satisfaction — 92%"

Brief: Single hero number for a social post, portrait orientation.

```
BACKGROUND: Solid #0E3A5F canvas, 1024x1536, 120px margins. No grid, no
pattern.
SUBJECT: A single stat card centered vertically. One oversized percentage
number, a short headline above it, a supporting line below it.
DATA: The number is exactly "92%". One decimal point of precision is wrong —
render "92%" and nothing else for the hero figure.
LABELS: Kicker "CUSTOMER SATISFACTION" centered top, Inter Bold 20pt,
#E8B04B, letter-spacing 0.15em, appears once. Hero number "92%" centered
middle, Playfair Display 280pt bold, #F5F2EC, appears once. Supporting
line "Q1 2026 survey · 1,248 respondents" centered below hero, Inter
Regular 18pt, #F5F2EC at 70% opacity, appears once.
CONSTRAINTS: Render "92%" exactly once, centered, no duplicate watermark
copies. Render "CUSTOMER SATISFACTION" in all caps, verbatim. No drop
shadows, no gradients, no photorealism, no background imagery. Pure
typography on solid #0E3A5F. Designed for Instagram feed.
```

Why this works: "appears once" on every string kills the classic duplicate-headline failure mode; the hero number is isolated so the model can render it sharply.

### 4. Comparison table — "Before vs After"

Brief: Two-column comparison, four rows, landscape.

```
BACKGROUND: Solid #F5F2EC canvas, 1536x1024, 96px margins. A single thin
vertical divider at 50% width, #0E3A5F at 30% opacity.
SUBJECT: A two-column comparison table. Left column header "BEFORE", right
column header "AFTER". Four rows of paired statements beneath the headers.
DATA:
Row 1: "Manual spreadsheets" vs "Automated reports"
Row 2: "Weekly close" vs "Daily close"
Row 3: "4 analysts" vs "1 analyst + AI"
Row 4: "$42k monthly cost" vs "$11k monthly cost"
LABELS: Headline "Before vs After" top-center in Playfair Display 56pt
bold, #0E3A5F, appears once. Column headers "BEFORE" and "AFTER" in Inter
Bold 28pt, letter-spacing 0.12em, each appears once. Row text in Inter
Regular 22pt, #0E3A5F. Left column text at 60% opacity, right column at
100% opacity.
CONSTRAINTS: Render all eight row strings verbatim, in the order given.
Right column labels get a small #E8B04B checkmark bullet, left column gets
a neutral dash. No drop shadows, no photorealism, no icons beyond the
bullets. Flat vector infographic.
```

Why this works: row strings are quoted in pairs so the model preserves alignment; opacity difference carries the "before = faded, after = vivid" semantic without extra color.

### 5. Quote card — "A short quote with attribution"

Brief: Pull quote with attribution line, square social.

```
BACKGROUND: Solid #F5F2EC canvas, 1024x1024, 96px margins. A single
oversized decorative opening quotation mark glyph top-left at 40% opacity
in #E8B04B, 360pt, purely decorative.
SUBJECT: A single pull quote, left-aligned, occupying the middle two-thirds
of the canvas, with a small attribution block below it.
DATA: Quote text: "The best infographic is the one your reader finishes."
Attribution: "— Dana Reyes, Head of Content, ACME".
LABELS: Quote in Playfair Display 44pt regular italic, #0E3A5F, line-height
1.25, left-aligned, appears once. Attribution below in Inter Semibold 18pt,
#0E3A5F at 70% opacity, appears once.
CONSTRAINTS: Render the quote verbatim including the period. Render the
attribution verbatim including the em dash and comma. Spell "A-C-M-E"
then render "ACME". No drop shadows, no photorealism, no portrait photo,
no additional decorative marks beyond the one opening quotation glyph.
Flat vector infographic.
```

Why this works: decorative glyph is scoped to one placement and color, preventing stray marks; brand name is spelled letter-by-letter so the letterforms stay correct.

## Critique anchors

When critiquing a generated infographic against the six rubric dimensions, these are the concrete bars to clear.

- **Text legibility** — sharp at 50% zoom, no garbling, no dropped letters, no invented words. Every label spells exactly what the prompt specified. Kerning is even and no letter pairs collide.
- **Brand color adherence** — hex values match within perceptual tolerance. The primary, accent, and neutral are each used in the roles the CONSTRAINTS slot assigned. No off-brand hues have leaked in from the model's prior.
- **Subject fidelity** — the image contains exactly the structure named in SUBJECT (one chart, one table, one flow). Count matches: if the brief said five steps, there are five steps, not four or six. Numbers in DATA render verbatim.
- **Composition** — clear visual hierarchy. Headline reads first, hero value second, supporting detail third. Generous margins, one idea per region, no overlap between bars/cells/nodes.
- **Mode realism** — reads as a designed graphic, not a photo of a graphic. No paper texture, no camera glare, no perspective warp, no film grain. Flat vector feel.
- **Ref-lock** — when a logo or style reference was attached, the output's logo is pixel-faithful and the style reference's color and layout language are carried through. No invented logo forms.

## Common failure modes & fixes

- **Garbled text** — the classic failure: "Q3 Rvenuu" instead of "Q3 Revenue". Fix: repeat the label in ALL CAPS in the LABELS slot, add `appears once`, and add `render verbatim, do not paraphrase` in CONSTRAINTS. Regenerate.
- **Off-brand color** — bars render teal instead of `#0E3A5F`. Fix: reinforce the hex in CONSTRAINTS with role assignment — `Primary color #0E3A5F for bars. Accent #E8B04B used only for the highlight bar. Do not introduce any other colors.` If the drift persists, remove mood words like "modern" or "vibrant" that pull in unbranded palettes.
- **Crowded layout** — labels collide, bars touch, margins vanish. Fix: add `generous whitespace, one idea per section, 80px minimum gap between elements` to CONSTRAINTS. Reduce the number of DATA items before blaming the model.
- **Accidental photorealism** — the image looks like a photo of a printed chart on a desk. Fix: audit the prompt for any photography language ("shot on", "lighting", "photograph", "realistic", "lifelike", "depth of field") and remove it. Add `flat vector infographic, no photorealism, no texture, no camera effects, no lighting simulation` to CONSTRAINTS.
- **Unintended figures or faces** — a stock-photo person appears next to the chart. Fix: add `no people, no faces, no hands, pure typography and data only` to CONSTRAINTS. For quote cards specifically, add `no portrait photo of the speaker`.
- **Duplicated headline** — the headline renders twice, once at the top and once as a watermark. Fix: append `appears once` to every label in LABELS and add `no watermarks, no duplicate text anywhere on the canvas` to CONSTRAINTS.
- **Invented logo** — a made-up wordmark appears where the real logo should be. Fix: never describe the logo in text. Always attach it as a reference image and reference it as `the provided logo reference`. Add `do not generate or invent any logo or wordmark` to CONSTRAINTS.
