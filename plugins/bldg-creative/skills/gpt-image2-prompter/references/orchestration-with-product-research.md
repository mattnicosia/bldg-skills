# Orchestrating with `product-research-amazon`

This reference explains how to turn the output of the `product-research-amazon` skill into a batch of paste-ready GPT Image 2 prompts. Load it when the user has a product research markdown in the workspace and asks for image assets, a listing image plan, or says something like "make the images for this research" / "give me the creative plan".

## What `product-research-amazon` produces

The `product-research-amazon` skill produces a single unified markdown document covering:

- **ICP (Ideal Customer Profile)** — who buys, demographics, context of use
- **Voice of Customer (VoC)** — the exact language buyers use, pain points, aspirations, recurring phrases from reviews and forums
- **Competitor review gaps** — what the top competitors do poorly (most common 1–3 star review themes) that this product can differentiate against
- **Amazon keyword signals** — search terms with intent, modifiers, long-tail clusters
- **OEM compatibility / technical fit** — vehicles, models, specs the product is compatible with (if applicable)
- **Seasonal signals** — when demand spikes, what contexts drive purchase at different times of year
- **Answers to the question template** supplied as input

## Inputs the batch planner needs

Before composing image prompts, confirm:

1. **Path to the research markdown** in the workspace (e.g. `/home/user/workspace/research/motul-300v-listing-research.md`).
2. **Brand slug** — a `brands/<slug>.yaml` profile. If none exists, offer to run the brand wizard first using the research doc as a source (it usually surfaces enough tone, audience, and vibe cues). Do NOT block on this — a generic brand profile is fine for a first pass; flag it in the output.
3. **The product hero image** — ideally already at `refs/<slug>-hero.png` and referenced in `brand.refs.product_hero`. Without it, lifestyle prompts still work but drift more. Ask the user to add one if missing.
4. **Destination surface** — Amazon listing, landing page, campaign, or social? The planner biases size + framing based on this. Amazon main image is square 1:1 white background; Amazon A+ content and secondary images are usually landscape 1500x750 or 1000x1000; social is portrait 4:5.

## Extraction pattern

Read the research markdown. From it, pull:

- **ICP sentence**: one sentence — who, what context, what they want.
- **Top VoC insight**: the single most-repeated benefit or pain buyers articulate. Stat if one exists (e.g., "73% of 5-star reviews mention `quiet burn`").
- **Top competitor gap**: the single most common 1–3 star complaint about the top competitor, phrased as a benefit the subject product delivers.
- **Hero feature**: the product's strongest differentiator — one phrase, ideally tied to a number or a spec.
- **Comparison angle**: the before/after, with/without, or A vs B framing that best lands for this buyer.
- **Seasonal / use-case hook**: when or where the buyer is most likely in-market. Use only if the research surfaces it clearly.
- **Exact buyer phrases**: 3–5 verbatim strings from VoC that can render as quoted labels in infographics.

If the research doc doesn't name one of these clearly, skip that infographic rather than inventing. A tight 3-asset plan beats a padded 5-asset plan with fabricated claims.

## The default batch plan

Unless the user asks for a different mix, produce:

| # | Mode        | Purpose                       | Source signal from research              |
| - | ----------- | ----------------------------- | ---------------------------------------- |
| 1 | lifestyle   | Hero — ICP in primary context | ICP + hero feature                       |
| 2 | infographic | Top benefit stat card         | Top VoC insight (with stat if available) |
| 3 | infographic | Competitor-gap comparison     | Top competitor gap (before vs after)     |
| 4 | infographic | Feature explainer / callouts  | Hero feature + 2–3 supporting specs      |
| 5 | infographic | Seasonal / use-case hook      | Seasonal signal (SKIP if not clear)      |

Total: 4–5 assets. Skip any infographic whose source signal isn't clearly present in the research — do not fabricate.

## Output format for the batch plan

Before printing the copy-paste blocks, first print a short **plan summary**:

```
## Batch image plan

Source research: <path>
Brand: <slug>
Destination: <Amazon listing | landing page | campaign | social>

Plan:
  1. LIFESTYLE — "<one-line brief>"           (1024x1536 portrait, quality: high)
  2. INFOGRAPHIC — "<one-line brief>"          (1024x1024 square, quality: high)
  3. INFOGRAPHIC — "<one-line brief>"          (1536x1024 landscape, quality: high)
  4. INFOGRAPHIC — "<one-line brief>"          (1536x1024 landscape, quality: high)
  5. (skipped — no clear seasonal signal in the research)

Signals used:
  - ICP: <sentence>
  - Top VoC: "<verbatim phrase>" — appears in <N> reviews
  - Competitor gap: "<phrase>"
  - Hero feature: <phrase with spec>
  - Exact buyer quotes available: "<q1>", "<q2>", "<q3>"

Proceeding to generate individual paste-ready blocks...
```

Then, for each item in the plan, print a **full operator copy-paste block** per `references/operator-mode.md`. Number them clearly. The user can paste them into ChatGPT one at a time or open parallel tabs.

Save artifacts for each asset to its own output directory:

```
outputs/2026-04-24_lifestyle_motul-300v_hero/
outputs/2026-04-24_infographic_motul-300v_top-voc-stat/
outputs/2026-04-24_infographic_motul-300v_vs-competitor/
outputs/2026-04-24_infographic_motul-300v_feature-callouts/
```

Append one line per asset to `outputs/.invocations.jsonl` with a shared `batch_id` (timestamp) so the user can query "all assets from this batch".

## Amazon-specific sizing biases

When the destination is an Amazon listing, bias toward:

- **Main image (slot 1)**: lifestyle is NOT valid for the Amazon main image per TOS — main must be the product on pure white, no props, no text overlays. If the user asked for a main-image prompt, generate a clean white-background product shot (technically `lifestyle` mode with specific constraints, see below) and flag it as Amazon-TOS-compliant.
- **Secondary images (slots 2–6)**: lifestyle in-context for slots 2–3, infographics for slots 4–6 is the common pattern.
- **A+ content**: landscape 1464x600 or 970x300 for modules; use infographic mode with destination stated in the prompt.

For the Amazon main image:

```
SCENE: Pure white seamless background, no environment.
SUBJECT: <product>, centered, no props, no hands, 85% frame-fill.
CAMERA: 50mm, straight-on, perfectly level, no perspective distortion.
LIGHTING: Soft even studio lighting, no hard shadows under the product.
STYLE: Photorealistic, sharp focus throughout, catalog-grade.
CONSTRAINTS: Image 1 is the product reference. Preserve the product exactly.
No text, no overlays, no shadows cast onto background. Background is pure
#FFFFFF white, no gradient, no tint. Amazon main-image compliant.
Generate at 2000x2000 square.
```

## Example — composed batch for a hypothetical oil product

Say the research is about a high-performance motor oil. A typical batch:

1. **Lifestyle hero** — "Garage at dawn, enthusiast owner pouring the oil into a clean engine bay, soft tungsten overhead, one-bottle hero, shallow DoF on the label" (portrait 1024x1536).
2. **Infographic stat card** — "92% of owners report `smoother shifts` after one oil change" with the verbatim phrase in quotes, Playfair display headline, brand colors (square 1024x1024 for Instagram grid).
3. **Infographic before/after** — "Before vs After" two-column comparison card using competitor-gap phrases on the left and this product's delivery on the right (landscape 1536x1024 for A+ content).
4. **Infographic feature callouts** — exploded diagram of the bottle with 3 labeled spec callouts (viscosity, API rating, formulation) (landscape 1536x1024).
5. **Skipped** — research doesn't surface a strong seasonal angle for this product.

Each block is independent and paste-ready. The user paces their ChatGPT quota as they like.

## Don't-do list

- **Don't** fabricate stats or quotes. If the research doc doesn't name a number, the infographic doesn't carry one. A vague "many customers say" is worse than silence.
- **Don't** repeat the same VoC phrase across multiple infographics. Each infographic carries one signal. Repetition burns the asset's punch.
- **Don't** invent OEM compatibility claims. If the research doc lists "fits models X, Y, Z", the image can show X/Y/Z verbatim. No extrapolation.
- **Don't** mix lifestyle and infographic constraints. Each asset is purely one mode. A "lifestyle image with text callouts" is really an infographic with a photoreal background — score it as infographic and lean hard on text discipline.
- **Don't** skip ref-lock on lifestyle. Every lifestyle asset attaches `brand.refs.product_hero` as Image 1 and restates the preserve list. Drift across a 5-asset batch is the single biggest failure mode if ref-lock is loose.

## Handoff back to the user

After printing all blocks, close with:

```
That's <N> paste-ready blocks. Paste each into ChatGPT one at a time (or
open parallel tabs for batch speed). When you have the generated PNGs,
upload them back here or save to the output paths I listed and reply
"done with #<N>" — I'll critique each and propose refinements if any miss
the bar.
```

This keeps the critique loop clean per-asset and lets the user tackle the batch in whatever order works for their ChatGPT session.
