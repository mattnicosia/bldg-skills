# Critique Rubric

## Overview

Six-dimension rubric for scoring a generated image and, if needed, producing one concrete refinement prompt.

Critique runs AFTER the skill successfully reads the generated PNG natively (multimodal). It scores the image against the brief and brand profile, writes results to `metadata.json.critique`, and — if the image fails — proposes exactly one surgical refinement prompt. Refinement is one-shot: the refined image is scored and saved, but the loop never recurses.

Critique is not a taste test. It catches defects (misspelled labels, off-brand colors, missing subjects, hierarchy collapse). Subjective preferences ("I'd prefer a bolder font") are out of scope — those are handled by the user iterating manually.

## Six dimensions table

| Dimension | What it checks | Applies to |
|---|---|---|
| Text legibility | Any text in image is readable, spelled correctly, no garbling | infographic (critical), lifestyle (only if text present) |
| Brand color adherence | Colors in image match `brand.colors.primary/secondary/accent` within tolerance | both, if brand provided |
| Subject fidelity | Main subject from brief is unambiguously present and correct | both |
| Composition & hierarchy | Framing and hierarchy match mode (data-first infographic, subject-first lifestyle) | both |
| Mode realism | Infographic: looks designed, not sketchy. Lifestyle: photoreal, not CGI unless asked | both |
| Ref-lock | If refs attached, image respects them (product identity, style cues) | both, only if refs present |

Max raw score: 18 (6 dimensions × 3). N/A dimensions drop out of both numerator and denominator, so the displayed max adjusts (e.g. a lifestyle image with no text and no refs scores out of 12).

## Per-dimension scoring guide

### Text legibility

- 3 = sharp at 50% zoom, all labels exactly verbatim vs brief, correct spelling throughout, consistent font across elements
- 2 = readable with minor kerning, spacing, or tracking issues; spelling correct; no garbled glyphs
- 1 = at least one unreadable, misspelled, or garbled label; or one word hallucinated that wasn't in the brief
- 0 = most text unreadable, multiple severe garbles, or headline-level text wrong
- N/A = mode is lifestyle and no text appears intentionally in the image

Note: if the brief specified exact copy ("chart title reads 'Q3 REVENUE'"), ANY deviation is at most a 1. Verbatim match is non-negotiable for headlines, axis labels, and callouts. Small decorative text (watermarks, faint background type) is judged loosely — a blurry background word doesn't sink the score unless the brief called it out. What sinks the score: a hero headline with a fused glyph, a mislabeled axis, a button with a typo, or any copy the user will read first.

### Brand color adherence

- 3 = primary, secondary, and accent all present and on-hex (within ~5% lightness/saturation tolerance); no off-brand hues dominate
- 2 = brand colors present but one is shifted (e.g. cream drifted to beige, navy to royal blue); no jarring off-brand colors
- 1 = at least one brand color missing or replaced with a clearly wrong hue; or an off-brand color dominates the composition
- 0 = palette bears no resemblance to brand profile; feels like a generic stock image
- N/A = no `brand.colors` provided in profile

Tolerance guidance: hex values don't need to be pixel-exact (diffusion won't deliver that), but the perceptual family must match. Navy #1B2A4E and #1F3050 pass. Navy vs teal fails. For accent colors with small footprints (a single accent line, a small badge), tolerance is tighter — the accent is often the only place that color appears and drift is immediately visible.

### Subject fidelity

- 3 = the exact subject from the brief is unambiguously present, correctly proportioned, and correctly contextualized
- 2 = subject present but with minor issues (wrong quantity, slightly off pose, missing one labeled element)
- 1 = subject partially wrong (wrong product variant, wrong data shape in chart, swapped labels)
- 0 = subject missing, replaced with a hallucination, or fundamentally incorrect (e.g. brief said bar chart, got pie chart)
- N/A = never; every image has a subject

### Composition & hierarchy

- 3 = hierarchy matches mode exactly — infographic reads data-first with clear primary/secondary/tertiary levels; lifestyle reads subject-first with supporting context
- 2 = hierarchy works but one element is over/under-weighted (legend cramped, CTA dwarfed, subject slightly off-center when centering was specified)
- 1 = hierarchy confused — eye doesn't know where to land first; multiple elements compete for primary slot
- 0 = no hierarchy; composition is chaotic, off-balance, or cuts off important elements
- N/A = never; composition always applies

### Mode realism

- 3 = infographic looks like a designer made it in Figma (clean vectors, intentional type, grid-aligned); lifestyle looks like a real photograph (believable lighting, DOF, materials)
- 2 = mostly on-mode with minor tells (slight AI texture, one over-rendered element, minor DALL-E-fingerprint in gradient)
- 1 = visible mode mismatch — infographic feels sketchy/painterly, or lifestyle feels CGI/video-game
- 0 = completely wrong register — infographic is an oil painting, or lifestyle is obviously synthetic plastic
- N/A = user explicitly requested a non-default register (e.g. "illustrated infographic" or "stylized 3D render")

### Ref-lock

- 3 = product identity preserved exactly (label, colors, shape, proportions); style cues from ref images honored
- 2 = product mostly right with minor drift (label text slightly different, slight color shift, proportions 90% accurate)
- 1 = product recognizable but with clear changes (wrong label, wrong cap color, missing feature)
- 0 = product replaced or fundamentally re-imagined; refs clearly ignored
- N/A = no reference images attached to the brief

## Pass criteria

- All applicable dimensions ≥ 2 AND no 0s → **pass**
- Any 0 → **always propose refinement** (critical failure, regardless of total)
- Any 1 → **propose refinement** (even if total score is otherwise high)
- All 2s and 3s → **pass**

Passing score depends on applicable max. For a full 6-dimension image (18 max), passing is typically 12+ with no 0s and no 1s. For a reduced 4-dimension image (12 max), it's 8+. But the threshold is the per-dimension floor, not the total — a 16/18 with a single 1 still fails and refines.

Why the floor rule matters: a misspelled headline is not rescued by three dimensions of 3. Summed scores hide critical defects. The per-dimension floor guarantees that any critical-path failure surfaces a refinement offer, regardless of how strong the rest of the image is.

## User-facing output format

### Pass template

```
Critique: 15/18 (pass)

✓ Text legibility (3) — labels sharp, correct spelling
✓ Brand colors (3) — navy + cream present, no off-brand hues
✓ Subject fidelity (3) — Q3 revenue bars correctly labeled
△ Composition (2) — hierarchy ok, legend slightly cramped
✓ Mode realism (3) — designed infographic feel
✓ Ref-lock (2) — logo present, slightly different proportions

No refinement needed. Saved to outputs/2026-04-22_infographic_acme_q3-revenue/
```

### Fail template

```
Critique: 10/18 (fail)

✗ Text legibility (1) — "Q3 RVENEU" misspelled in chart title
△ Brand colors (2) — primary navy ok, but cream replaced with beige
✓ Subject fidelity (3) — bar chart with correct Q3 data
△ Composition (2) — hierarchy ok, legend slightly cramped
✓ Mode realism (3) — designed infographic feel
N/A Ref-lock — no references attached

Proposed refinement (single surgical change, preserves everything else):

┌─ refinement prompt ─────────────────────────────────────┐
│ Regenerate the same infographic. Preserve: layout,      │
│ all bar data, axes, legend position, chart style,       │
│ photography style. Change ONLY: fix the title text to   │
│ read exactly "Q3 REVENUE" (no other words), and use     │
│ the cream color #F5E6D3 (not beige) for the background.│
└─────────────────────────────────────────────────────────┘

Run refinement? (y/n)
```

Symbol key: ✓ = 3, △ = 2, ✗ = 0 or 1, N/A = not applicable. Scores in parens are the raw 0–3 value.

## Refinement discipline

Every refinement prompt MUST follow these five rules. They exist because refinement recurses drift if loose — the model reinterprets everything each pass.

1. **Start with `"Regenerate the same <mode>."`** — anchors the model to the prior output as the reference point.
2. **Explicitly re-state the preservation list every time.** Drift compounds. If you don't name what to keep, the model will redecide it. Include: layout, data/subject, style, colors not being changed, typography, framing.
3. **Exactly one surgical change** (or one tight cluster of related fixes like two spelling errors in the same title, or two colors in the same palette). Never combine unrelated fixes — that's two refinements, not one, and the model will do neither well.
4. **Reference attached images by index if relevant** ("Keep product from Image 1 identical", "Match the lighting from Image 2"). The model sees images by ordinal, not by description.
5. **Concrete, not vague.** "Fix spelling of 'revenue' → 'REVENUE'" not "make the text better". "Use cream #F5E6D3" not "use the right cream". Every refinement names the failure mode and the target state.

Anti-patterns to avoid in refinement prompts:

- "Improve the text" — too vague, model will redo the whole layout
- "Make it more on-brand" — no target state, drift guaranteed
- "Fix the issues" — doesn't name which issues
- Combining unrelated fixes (spelling + composition + color) in one pass — split into separate refinements or pick the most critical and ship the rest as a note to the user
- Omitting the preservation list on the assumption the model will "just keep what works" — it won't

## Refinement examples

### Example 1 — Spelling fix (text legibility failure)

**Failure:** chart title reads "Q3 RVENEU" instead of "Q3 REVENUE". Score: Text legibility = 1.

**Refinement prompt:**

```
Regenerate the same infographic. Preserve: bar chart data,
axis labels, legend, color palette (navy + cream), typography,
overall layout, and grid alignment. Change ONLY the chart title
text: it must read exactly "Q3 REVENUE" (all caps, two words,
no other characters). Do not add, remove, or rephrase any
other text anywhere in the image.
```

### Example 2 — Brand color correction (brand adherence failure)

**Failure:** brief specified cream #F5E6D3 background; image rendered with beige #E8D4B8. Score: Brand colors = 2, but user wants exact brand match.

**Refinement prompt:**

```
Regenerate the same infographic. Preserve: all text verbatim,
chart data, bar colors (navy #1B2A4E), legend position, layout,
and typography. Change ONLY the background color: use cream
#F5E6D3 (a warm off-white with a slight yellow undertone).
Do not shift any other color in the palette.
```

### Example 3 — Composition tweak (hierarchy failure)

**Failure:** lifestyle image of product on kitchen counter; product is tiny in frame, kitchen dominates. Score: Composition = 1.

**Refinement prompt:**

```
Regenerate the same lifestyle photograph. Preserve: product
from Image 1 identical (label, cap, shape), kitchen setting,
morning light, countertop material, styling props. Change
ONLY the framing: the product must fill roughly 40% of the
frame height and be centered in the lower-middle third.
Keep all other elements in their current positions relative
to the product.
```

### Example 4 — Ref-lock drift (ref-lock failure)

**Failure:** product label reads "ACEM" instead of "ACME" (model hallucinated the logo). Score: Ref-lock = 1, Text legibility = 1.

**Refinement prompt:**

```
Regenerate the same lifestyle photograph. Preserve: setting,
lighting, composition, color grade, props, and framing.
Change ONLY the product label: it must read exactly "ACME"
(four letters, all caps) matching the reference in Image 1.
Do not alter product shape, cap color, or any other visual
element on or around the bottle.
```

This example shows a tight cluster: two dimensions both failed because of the same root cause (hallucinated logo text). One refinement fixes both.

## Escape hatch

The `--accept` flag skips critique entirely.

- Skill reads the image (to confirm the file is valid) but does not score it
- The image is saved to the output directory as normal
- `metadata.json.critique` is written as `{"skipped": true}`
- No refinement is offered

Use when: user has already eyeballed the image and wants to move on, or when running in a batch/automated context where the loop can't pause for interactive y/n.

Invocation: any skill command that produces an image accepts `--accept` as a trailing flag.

Why this exists: critique is cheap but not free — it burns a multimodal read and a few seconds of the user's attention. When the user knows they want the image regardless (quick iteration, exploratory drafts, scripted batch runs), skipping critique keeps the loop tight. The metadata still records that critique was skipped so later sessions know the image wasn't validated.

Do NOT default to `--accept`. Critique catches defects that the user's eye will miss (especially spelling errors in dense infographics). Skip only with intent.

## When to skip refinement even on fail

Occasionally critique will flag a defect that isn't worth a refinement pass. The skill should still offer refinement (the user decides), but these cases inform how the user answers the y/n prompt:

- **The defect is in decorative background text** that no reader will ever parse. Burn a token only if the text is in the hero region.
- **The brief was under-specified** and the "defect" is actually the model's reasonable interpretation of ambiguous input. Better fix: rewrite the brief and regenerate from scratch rather than refine.
- **Multiple critical defects compound.** If three dimensions score 1 or 0, refinement can only surgically fix one cluster. Better to regenerate with a tighter brief.
- **The refinement prompt itself would exceed one surgical change.** If you find yourself writing "also fix X, also fix Y, also fix Z" — stop. That's a regenerate, not a refine.

The skill does not make this decision; it always offers refinement on fail. The guidance above is for the user answering y/n.

## What critique does NOT do

- **Does not rank against other generations.** Each image is scored in isolation against the brief. Comparative judgement ("which of these three is best?") is a separate workflow.
- **Does not offer subjective creative alternatives.** "What if we tried a brighter palette?" or "Have you considered a different angle?" are out of scope. Critique catches defects, not taste.
- **Does not block saving.** The image is always saved to the output directory. Critique is metadata — it informs the user and gates the refinement offer, but it never deletes or withholds the generated file.
- **Does not re-critique the refinement.** The refined image is scored once and saved, but there is no second refinement offer. If the refinement still fails, the user iterates manually with a fresh brief. One-shot by design: prevents runaway loops and forces the user back into the loop when surgical refinement isn't enough.
- **Does not second-guess the brief.** If the brief said "use purple" and the image used purple, that's a 3 on brand colors even if purple was a bad choice. Brief correctness is upstream of critique.

## Metadata writeback

Every critique result persists to `metadata.json` under the `critique` key. Schema:

```json
{
  "critique": {
    "score": 15,
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
    "notes": "Strong pass. Minor: legend slightly cramped, logo proportions slightly off.",
    "refined_from": null
  }
}
```

Field definitions:

- `score` — sum of applicable dimension scores (N/A dimensions excluded)
- `max` — applicable max (18 minus 3 per N/A dimension)
- `passed` — boolean per the pass criteria above
- `dimensions` — dict of dimension key → integer score (0–3) or `"N/A"`
- `notes` — brief human-readable summary (1–2 sentences), same content shown in the user-facing output
- `refined_from` — null for first-generation images; path to the previous image in the output dir if this is a refinement result

When `--accept` is used, the critique block is simply `{"skipped": true}` — no other fields.

For refinement outputs, a new metadata.json is written in the refinement's own subdirectory, and `refined_from` points back to the original. The original's metadata.json is not modified.

Downstream tooling reads `metadata.json.critique` for:

- filtering batch outputs by `passed: true`
- aggregating dimension scores across a session to spot weak spots in briefs or brand profiles
- skipping already-refined images (those with non-null `refined_from`) when the user asks "show me first-pass results only"

Keep the schema stable. Additive fields are fine; renames or removals break downstream consumers.
