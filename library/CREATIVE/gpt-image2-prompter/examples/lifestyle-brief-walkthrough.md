# Lifestyle Brief — End-to-End Walkthrough

This is a realistic, paste-ready walkthrough of generating a single lifestyle photograph using the `luma-candle-co` brand profile. It shows the brief, the exact invocation, how brand YAML fields flow into the prompt slots, the composed 6-slot prompt, the settings, the expected output, a passing critique result, and an alternate failure + one-shot refinement.

## The brief

"Luma pillar candle on a marble bathroom shelf, soft morning light, single subject, wellness aesthetic."

Destination: Instagram feed post, portrait 4:5.

## Invocation

The user asks in chat:

> Lifestyle shot of the Luma pillar candle on a marble bathroom shelf, soft morning light, single subject, wellness aesthetic. For an Instagram feed post.

The skill identifies `mode=lifestyle`, `brand=luma-candle-co`, no explicit size/quality/refs — all three pulled from the brand's `defaults` block, and `refs.product_hero` is auto-attached as Image 1.

## Brand slots injected

The skill reads `brands/luma-candle-co.yaml` from the workspace and substitutes fields into the 6-slot template. Each transformation below shows the YAML field on the left and the literal prompt text it becomes on the right.

### vibe → SCENE + STYLE (atmosphere cues)

```
# YAML
vibe: ["calm", "premium", "tactile", "warm-minimal"]
```
→
```
# Prompt (SCENE atmosphere)
A calm, warm-minimal wellness setting on a weekday morning.

# Prompt (STYLE register)
Premium register, tactile surfaces emphasized.
```

### audience → SCENE (contextual framing)

```
# YAML
audience: "women 30-55, wellness-oriented"
```
→
```
# Prompt (SCENE)
The space reads as belonging to a 30-55 wellness-oriented woman — deliberate, curated, unhurried.
```

### tagline → STYLE (mood anchor)

```
# YAML
tagline: "Slow-burning luxury for mindful mornings"
```
→
```
# Prompt (STYLE)
Mood anchor: slow-burning luxury for mindful mornings — unhurried, considered, quiet.
```

### colors.secondary + colors.accent → STYLE (palette guidance)

```
# YAML
colors:
  secondary: "#F5E6D3"
  accent:    "#D4A574"
```
→
```
# Prompt (STYLE)
Dominant palette: warm cream (#F5E6D3) and soft tan (#D4A574) carried
by natural materials — pale marble veining, brass hardware, linen —
never splashed on as paint.
```

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
# Prompt (CONSTRAINTS)
Natural daylight with soft shadows. Real bathroom context. Single
product hero — do not duplicate the candle.
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
# Prompt (CONSTRAINTS)
No neon colors. No cluttered scenes. No cartoonish illustration.
```

### refs.product_hero → auto-attached as Image 1 + ref-lock CONSTRAINTS

```
# YAML
refs:
  product_hero: "./luma-candle-hero.png"
```
→
```
# Prompt (CONSTRAINTS — ref-lock block)
Image 1 is the product reference. Preserve the candle from Image 1
exactly — color, shape, label text, label typography, proportions,
and finish. Allow only the environment, lighting, and supporting
props to change. Do not restyle, recolor, or redesign the product
in any way.
```

## Composed prompt

Here is the full 6-slot prompt that the skill composes and sends to GPT Image 2. Paste-ready:

```
SCENE: A sun-washed marble bathroom shelf in a quiet pre-war apartment
on a weekday morning, roughly 8am. Pale Carrara marble with soft grey
veining forms the shelf surface. White subway tile behind. A folded
pale-cream linen hand towel sits to one side and a small clear glass
bottle of face oil with a brass dropper cap sits further back, softly
defocused. The space reads as belonging to a 30-55 wellness-oriented
woman — deliberate, curated, unhurried. Calm, warm-minimal wellness
atmosphere.

SUBJECT: A single Luma pillar candle placed on the marble shelf,
slightly left of center, unlit, label facing camera. The candle
occupies roughly 40% of the frame height. No second candle. No hand
in frame.

CAMERA: 50mm lens, medium shot, eye-level at candle mid-height,
shallow DoF at f/2.5. Candle label and wax surface tack-sharp; the
marble veining beside it softly defocused; the tile behind fully
blurred into a neutral tonal block.

LIGHTING: Soft diffuse morning light from a north-facing window
camera-left at 30 degrees above horizon, around 5200K. A gentle
warm wash falls across the marble to the right of the candle; a
long soft-edged shadow drifts to camera-right along the shelf.
No harsh highlights on the glass. No direct sun hitting the label.

STYLE: Photorealistic, shot on Kodak Portra 400, subtle film grain,
natural color science. Premium register with tactile surfaces
emphasized — visible marble veining, linen weave on the towel,
faint brass patina on the face-oil dropper, a single dust mote
drifting in the light beam. Mood anchor: slow-burning luxury for
mindful mornings — unhurried, considered, quiet. Dominant palette:
warm cream (#F5E6D3) and soft tan (#D4A574) carried by the marble,
linen, and brass — never splashed on as paint.

CONSTRAINTS: Image 1 is the product reference. Preserve the candle
from Image 1 exactly — color, shape, label text, label typography,
proportions, and finish. Allow only the environment, lighting, and
supporting props to change. Do not restyle, recolor, or redesign
the product in any way. Natural daylight with soft shadows. Real
bathroom context. Single product hero — do not duplicate the candle.
No neon colors. No cluttered scenes. No cartoonish illustration.
No text, no labels, no writing, no signage, no typography anywhere
in the frame, except the candle's own label as shown in Image 1.
Generate at 1024x1536 portrait, designed for an Instagram feed
post at 4:5.
```

## Settings

- **Size:** `1024x1536` portrait (from `defaults.lifestyle_size`)
- **Quality:** `high` (from `defaults.quality`)
- **Refs attached (in order):**
  - Image 1: `examples/refs/luma-candle-hero.png` (auto-attached from `refs.product_hero`)

Note: `refs.style_anchor` is NOT auto-attached in lifestyle mode — it is an infographic-mode standing ref. The logo is also not auto-attached in lifestyle mode because the candle already carries the brand on its label via ref-lock.

## Expected output (placeholder)

A portrait 1024x1536 PNG. A single Luma pillar candle, unlit, centered slightly left on a pale Carrara marble shelf with soft grey veining. The candle's label faces the camera, matching Image 1 character-for-character in its wordmark, its tan-on-cream color block, and its proportions. Warm diffuse morning light rakes in from the upper-left, casting a long soft shadow across the marble to the right of the candle. Out of focus behind: white subway tile, a folded pale-cream linen hand towel, and a clear glass face-oil bottle with a brass dropper. The marble veining and linen weave are visible but not overstated. A single dust mote floats in the light beam. The overall tone is warm cream with a soft tan underlayer — calm, premium, tactile. No other text appears anywhere in the frame; the candle's label is the only typography present, and it matches Image 1. The image reads as a Kodak Portra 400 photograph, not a render.

## Critique result (pass example)

```
Critique: 16/18 (pass)

N/A Text legibility — no intentional text; the candle label matches
  Image 1 character-for-character (enforced under ref-lock)
✓ Brand colors (3) — warm cream marble, tan accents through brass
  and candle label, no off-brand hues
✓ Subject fidelity (3) — single Luma pillar candle, ~40% frame height,
  label facing camera, unlit
△ Composition (2) — candle is slightly-left-of-center as specified,
  but the face-oil bottle in the background is a touch more prominent
  than "softly defocused" suggests
✓ Mode realism (3) — reads as Portra 400, visible marble veining,
  linen weave, faint brass patina — no CGI sheen
△ Ref-lock (2) — candle color, shape, proportions, and label all match
  Image 1; one of the label's corner curves is rendered ~5% tighter
  than the reference

No refinement needed. Saved to outputs/2026-04-22_lifestyle_luma-candle-co_marble-shelf/
```

Text legibility is scored N/A — no intentional text appears, and the candle's own label is governed by ref-lock (see `references/lifestyle-prompting.md` on text handling). The applicable max drops from 18 to 15; 13 of 15 is a comfortable pass under the per-dimension floor rule.

## Alt scenario (fail + refinement)

On a different seed, the first-pass output shifts the candle's proportions — the pillar renders about 20% narrower than Image 1 and the label wraps more tightly around the circumference than the reference. Environment and lighting are otherwise excellent.

```
Critique: 12/15 (fail)

N/A Text legibility — no intentional text
✓ Brand colors (3) — palette clean, accent in brass and label
△ Subject fidelity (2) — single candle present at correct framing,
  but the pillar proportions drifted narrower than the brief implied
✓ Composition (3) — slightly-left-of-center, props recede correctly,
  negative space on the top third
✓ Mode realism (3) — convincing photograph, tactile surfaces
✗ Ref-lock (1) — candle proportions narrowed ~20% vs Image 1;
  label wraps tighter around the candle than in the reference,
  making the wordmark compress. Color and finish match.

Proposed refinement (single surgical change, preserves everything else):

┌─ refinement prompt ─────────────────────────────────────────────┐
│ Regenerate the same lifestyle photograph. Preserve: the marble  │
│ bathroom shelf environment, the white subway tile background,   │
│ the folded pale-cream linen hand towel, the clear glass face-oil│
│ bottle with brass dropper, the soft diffuse morning light from  │
│ camera-left at 30 degrees, the Kodak Portra 400 register with   │
│ subtle grain, the dust mote in the light beam, the overall warm │
│ cream and soft tan palette, the candle's slightly-left-of-center│
│ placement, the ~40% frame height scale, and the unlit state.    │
│                                                                 │
│ Change ONLY the candle itself: re-lock the candle to Image 1    │
│ exactly — preserve color, shape, label text, label typography,  │
│ proportions, and finish. In particular, the pillar diameter and │
│ the label's horizontal wrap around the candle must match Image 1│
│ precisely; do not narrow the pillar, do not compress the label. │
│ The candle in the refined image must be visually indistinguishable│
│ from Image 1 except for the environment and lighting around it. │
└─────────────────────────────────────────────────────────────────┘

Run refinement? (y/n)
```

Why the refinement follows the discipline rules from `references/critique-rubric.md`:

1. Starts with "Regenerate the same lifestyle photograph." — anchors to the prior output.
2. Re-states the full preservation list — environment, props, light direction, film stock, grain, dust mote, palette, composition, scale, unlit state — because drift compounds and anything unnamed gets redecided.
3. Makes exactly one surgical change: re-lock the candle to Image 1.
4. References Image 1 by index, not by description.
5. Names the failure mode (pillar narrowed, label compressed) and the target state (match Image 1 exactly on diameter and label wrap) concretely.

Note: this is the classic "drift on iteration 3 of 5" failure mode described in `references/lifestyle-prompting.md`. The fix is not a new prompt structure — it is restating the full preserve list in the refinement, which the model will otherwise decay on each edit.

## Metadata sidecar

`outputs/2026-04-22_lifestyle_luma-candle-co_marble-shelf/metadata.json` after a passing first run:

```json
{
  "skill_version": "0.1.0",
  "timestamp": "2026-04-22T08:12:44-05:00",
  "mode": "lifestyle",
  "brand": {
    "slug": "luma-candle-co",
    "schema_version": 1
  },
  "brief": "Luma pillar candle on a marble bathroom shelf, soft morning light, single subject, wellness aesthetic.",
  "prompt_slots": {
    "scene": "Sun-washed marble bathroom shelf, pre-war apartment, weekday 8am. Carrara marble, subway tile, linen towel, face-oil bottle softly defocused.",
    "subject": "Single Luma pillar candle, slightly-left-of-center, unlit, label facing camera, ~40% frame height.",
    "camera": "50mm, medium shot, eye-level at candle mid-height, shallow DoF at f/2.5.",
    "lighting": "Soft diffuse morning light from a north-facing window camera-left at 30 degrees, ~5200K. Long soft shadow to camera-right.",
    "style": "Photorealistic, Kodak Portra 400, subtle grain. Marble veining, linen weave, brass patina, single dust mote.",
    "constraints": "Ref-lock to Image 1 (color, shape, label text, label typography, proportions, finish). No text except candle label. Single hero, no duplicates."
  },
  "settings": {
    "size": "1024x1536",
    "quality": "high"
  },
  "refs_attached": [
    {"index": 1, "role": "product_hero", "path": "examples/refs/luma-candle-hero.png"}
  ],
  "output": {
    "filename": "image.png",
    "bytes": 612488,
    "width": 1024,
    "height": 1536
  },
  "critique": {
    "score": 13,
    "max": 15,
    "passed": true,
    "dimensions": {
      "text_legibility": "N/A",
      "brand_colors": 3,
      "subject_fidelity": 3,
      "composition": 2,
      "mode_realism": 3,
      "ref_lock": 2
    },
    "notes": "Comfortable pass. Minor: face-oil bottle slightly too prominent; label corner curve ~5% tighter than reference.",
    "refined_from": null
  }
}
```

For the failed-then-refined branch, a second directory `outputs/2026-04-22_lifestyle_luma-candle-co_marble-shelf-refined/metadata.json` is written with `critique.refined_from` set to the path of the original `image.png` and the candle re-locked to Image 1.
