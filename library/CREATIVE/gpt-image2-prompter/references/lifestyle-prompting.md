# Lifestyle Prompting

## Overview

Lifestyle prompting — photorealistic, subject-forward, in-context imagery.

## When to use this mode

Use `lifestyle` mode whenever the job of the image is to make a viewer feel the product in the real world, not communicate structured data. Pick it for:

- Product-in-context shots (hand holding the product, product on a surface it belongs on)
- Environmental hero shots (a single product anchored in a well-styled room)
- Flat lays (top-down arrangement of the product with complementary props)
- UGC-feel content (iPhone-grade snapshots, natural framing, slight imperfection)
- Editorial (magazine-scale full-bleed compositions with deliberate negative space)

If the brief is a chart, table, stat card, process flow, or any text-heavy explainer, switch to `infographic` mode instead.

## Prompt template

Fill every slot. The ordering — scene → subject → camera → lighting → style → constraints — is load-bearing: it tells GPT Image 2 to lock the world before it renders the thing, which is how a photographer works on set.

```
SCENE:       <location, time of day, atmosphere>
SUBJECT:     <one sentence; product/person/scene; explicit scale>
CAMERA:      <lens, framing, angle, DoF — e.g. "35mm, medium close-up, shallow DoF, eye-level">
LIGHTING:    <"golden hour", "soft diffuse north window", "high-contrast late afternoon">
STYLE:       <must include the literal word "photorealistic"; film stock/grain cues optional>
CONSTRAINTS: <brand do/don't, ref-lock preservation language if refs present>
```

What goes in each slot:

- **SCENE** — anchors the model in a physical location and time. One or two sentences: room, surface, weather, era. Concrete beats abstract: "a sun-washed bathroom shelf in a 1920s pre-war apartment" beats "a nice bathroom".
- **SUBJECT** — one sentence naming the hero and its scale relative to the frame. Name the product, name the hand or person if present, and state size cues ("a 9oz candle held in the subject's right hand").
- **CAMERA** — the photography fingerprint. Always name a lens (35mm, 50mm, 85mm), framing (wide, medium, medium close-up, close-up, macro), angle (eye-level, low, high, top-down), and depth of field.
- **LIGHTING** — one named lighting scheme. "Golden hour through a west-facing window", "soft diffuse north window on an overcast morning", "hard single-source morning sun at 30 degrees".
- **STYLE** — must contain the literal word `photorealistic`. Optionally a film stock cue (Portra 400, Cinestill 800T), a grain descriptor, or a reference photographer's visual register.
- **CONSTRAINTS** — brand do/don't, negative guidance, and ref-lock preservation. This is where you forbid text when none is wanted, forbid unrelated props, and lock the product identity from reference images.

## Default settings

- `quality="medium"` default for lifestyle. High quality rarely pays off on photoreal scenes and slows iteration.
- Size: `1024x1536` portrait by default — the social-first default (Instagram feed, Pinterest, LinkedIn, TikTok thumbnail, Reels cover).
- Size: `1536x1024` landscape when the brief is editorial, a hero banner, or a website above-the-fold.
- Size: `1024x1024` square only when the destination is Instagram grid or an ad slot that demands it.
- Escalate `quality="high"` only when a particular output will be printed, blown up past 4x on screen, or used for a client pitch.
- State the destination in the prompt ("shot for an Instagram feed post at 4:5") — it nudges framing and negative space.

## Photorealism activation rules

These rules come straight from OpenAI's GPT Image prompting guide for photoreal scenes. Apply them verbatim to every lifestyle prompt.

1. **Include the literal word `photorealistic` in the STYLE slot.** Omit it and the model drifts toward illustrated or CGI registers.
2. **Use photography language, not art-direction language.** Name a lens (`35mm`, `50mm`, `85mm`), a film stock (`Kodak Portra 400`, `Cinestill 800T`), a grain amount (`subtle film grain`), and a depth of field (`shallow DoF, f/2.0`).
3. **Avoid words that imply studio polish unless you want glossy.** Words like `commercial`, `pristine`, `polished`, `product shot`, `e-commerce` push the output toward CGI-lit catalog renders. Drop them unless that is the target.
4. **Include real-world texture cues.** Name the surfaces the camera will see: `pores visible on the skin`, `wrinkles on the linen napkin`, `weathered brass hardware`, `fabric weave on the knit throw`, `dust motes in the light beam`. Texture language is the single biggest lever against "it looks AI".
5. **Add slight imperfection for UGC and editorial.** `slight motion blur on the hand`, `a single hair strand out of place`, `uneven fingerprint on the glass`. Perfection reads as fake.

## Ref-lock pattern

Brand profiles can supply standing reference images under `brand.refs`. The most important one is `brand.refs.product_hero` — the canonical product photo. When present, the skill auto-attaches it as Image 1 to every generation call in lifestyle mode.

The prompt must then address the reference explicitly, because GPT Image 2 only locks to references when told to. Use this exact preservation phrasing in the CONSTRAINTS slot:

```
Image 1 is the product reference. Preserve the candle from Image 1 exactly —
color, shape, label text, label typography, proportions, and finish. Allow
only the environment, lighting, and any hands or supporting props to change.
Do not restyle, recolor, or redesign the product in any way.
```

Mechanics:

- Reference images are numbered. The first attached ref is `Image 1`, the second is `Image 2`, and so on. Always refer to them by index inside the prompt.
- Spell the preservation list out: `color, shape, label text, label typography, proportions, finish`. Vagueness ("keep the product the same") loses on iteration 3 of 5.
- **Repeat the preserve list on every iteration.** Drift compounds across edits — each round forgets a little more. Restate preservation in full every time.
- Explicitly name what is allowed to change: `Allow only the environment, lighting, hand placement, and supporting props to change.` Models treat the unmentioned as fair game.
- For virtual try-on style shots with a person from `brand.refs.model_hero`: `Preserve the model's face, body shape, pose, hair, and expression exactly from Image 2. Only the held product and background may change.`

Ref-lock is the single biggest quality lever on brand work. A mediocre prompt with tight ref-lock beats a brilliant prompt without it.

## Text handling in lifestyle

Lifestyle images rarely need rendered text. If any unintended text appears — on a sign, a book spine, a packaging label the prompt didn't ask for — the critique rubric scores `Text legibility = 1` because the image broke its mode.

- Default CONSTRAINTS for lifestyle should include: `no text, no labels, no writing, no signage, no typography anywhere in the frame, except the product's own label as shown in Image 1`.
- The product's own label is the single exception and is governed by ref-lock: it must match Image 1 character-for-character, not be invented.
- When text IS intentional — a chalkboard sign in a café scene, a magazine cover in a flat lay — follow the text-rendering discipline from `references/infographic-prompting.md`: wrap the literal string in double quotes, specify typography, spell brand names letter-by-letter, demand verbatim rendering, and mark it `appears once`.

## Five worked examples

Each example assumes a brand profile with:

```yaml
brand:
  vibe: ["calm", "premium"]
  colors:
    primary: "#0E3A5F"
    accent: "#E8B04B"
    neutral: "#F5F2EC"
  do:
    - "natural light"
    - "negative space"
    - "matte finishes"
  dont:
    - "neon"
    - "clutter"
    - "stock-photo cliches"
  refs:
    product_hero: "./candle-hero.png"
```

### 1. Product-in-hand — "woman holding Acme candle on a bathroom shelf"

Brief: UGC-leaning product-in-context shot for a social post, portrait.

```
SCENE: A sun-washed bathroom shelf in a 1920s pre-war apartment on a weekday
morning. Clean white subway tile behind the shelf, a small glass bottle of
face oil and a folded linen hand towel beside the subject.
SUBJECT: A woman's right hand, mid-30s, holding a 9oz Acme candle at chest
height in front of the shelf, the candle occupying roughly 30% of the frame.
CAMERA: 35mm lens, medium close-up, eye-level, shallow DoF at f/2.2. The
candle label is in sharp focus, the tile behind softly defocused.
LIGHTING: Soft diffuse morning light from a north-facing window camera-left.
No harsh highlights. Gentle shadow on the right side of the candle.
STYLE: Photorealistic, shot on Kodak Portra 400, subtle film grain, natural
skin tone with visible pores and faint wrist veins, matte finish overall.
CONSTRAINTS: Image 1 is the product reference. Preserve the candle from
Image 1 exactly — color, shape, label text, label typography, proportions,
and finish. Allow only the environment, hand, and lighting to change. Calm
and premium vibe, natural light, negative space, matte finishes. No neon,
no clutter, no stock-photo cliches. No text, no labels, no writing anywhere
except the candle's own label as shown in Image 1.
```

Why this works: ref-lock is explicit and enumerated; the hand is framed at a specific percentage so the model knows the scale; film stock and pore cues push hard against CGI register.

### 2. Environmental hero — "candle on a nightstand, morning light"

Brief: Quiet editorial hero for a website above-the-fold, landscape.

```
SCENE: A minimalist bedroom nightstand in a Scandinavian apartment just
after sunrise. A linen-bound book, a small ceramic water carafe, and a
folded pair of reading glasses rest on the nightstand's pale oak surface.
Out-of-focus bed linen in cream tones fills the background.
SUBJECT: A single 9oz Acme candle centered on the nightstand, roughly 40%
of the frame height, unlit, label facing the camera.
CAMERA: 50mm lens, medium shot, slight low angle (12 degrees below eye
level), shallow DoF at f/2.8. Candle sharply in focus, nightstand edge
softly defocused, background fully blurred.
LIGHTING: Golden hour morning sun from camera-right through a sheer curtain,
casting a soft warm wash and a long, gentle shadow of the candle onto the
oak surface. Color temperature around 3200K.
STYLE: Photorealistic, shot on Cinestill 800T, subtle grain, weathered oak
grain visible, visible dust motes in the light beam.
CONSTRAINTS: Image 1 is the product reference. Preserve the candle from
Image 1 exactly — color, shape, label text, label typography, proportions,
and finish. Allow only the room, props, and lighting to change. Calm and
premium vibe, natural light, negative space, matte finishes. No neon, no
clutter, no stock-photo cliches. No text, no labels, no writing anywhere
except the candle's own label as shown in Image 1. Designed for a website
hero banner at 1536x1024.
```

Why this works: the shadow is directed explicitly, the background is prescribed as out-of-focus so the model does not over-compose, and dust motes in the beam is a high-leverage photoreal cue.

### 3. Flat lay — "candle, matches, and linen napkin on marble"

Brief: Top-down flat lay for a Pinterest pin, portrait.

```
SCENE: A white Carrara marble countertop seen from directly above. The
marble shows gentle grey veining and faint natural imperfections.
SUBJECT: A flat lay composition: the 9oz Acme candle positioned slightly
left of center, a pale-cream linen napkin loosely folded to the right, a
small brass matchbox and three spilled wooden matches in the bottom-left,
a single sprig of dried lavender top-right. Candle occupies roughly 25%
of the frame.
CAMERA: 50mm lens, top-down / flat lay / bird's-eye, perfectly perpendicular
to the surface, moderate DoF at f/4.0 so all props are in acceptable focus.
LIGHTING: Soft diffuse overhead window light, slightly stronger from
camera-top, casting gentle soft-edged shadows to the bottom of each prop.
STYLE: Photorealistic, shot on Kodak Portra 400, subtle grain, visible
marble veining, visible linen weave on the napkin, faint brass patina on
the matchbox.
CONSTRAINTS: Image 1 is the product reference. Preserve the candle from
Image 1 exactly — color, shape, label text, label typography, proportions,
and finish. Allow only the surface, props, and lighting to change. Calm
and premium vibe, natural light, negative space, matte finishes. Off-white
neutral palette only (#F5F2EC family); no neon, no clutter, no stock-photo
cliches. No text, no labels, no writing anywhere except the candle's own
label as shown in Image 1.
```

Why this works: each prop has a named position so the composition doesn't collapse into a pile; surface texture (marble, linen weave, brass patina) is called out per prop so nothing reads as CGI.

### 4. UGC feel — "iPhone-shot candle on a reading chair"

Brief: Organic-looking social post, portrait, meant to feel not-directed.

```
SCENE: An amber-toned reading corner on a rainy Sunday afternoon. A worn
forest-green velvet reading chair sits beside a stack of three paperbacks
on the floor. Soft rain is visible on the window behind.
SUBJECT: The 9oz Acme candle placed on the seat cushion of the chair,
slightly off-center, roughly 20% of the frame, a knit throw blanket
crumpled to one side of it.
CAMERA: iPhone-style framing, approximately 26mm equivalent wide, medium
shot, slightly handheld angle tilted 3 degrees right, moderate DoF.
LIGHTING: Low-contrast overcast afternoon light from the window camera-
left, warm lamp glow spilling from camera-right at 2700K.
STYLE: Photorealistic, looks like an iPhone 15 photo, no film grain, faint
sensor noise in shadows, slight motion softness, natural color science
(not HDR-crushed), a single hair strand on the velvet cushion, uneven
fingerprint on the glass of the candle.
CONSTRAINTS: Image 1 is the product reference. Preserve the candle from
Image 1 exactly — color, shape, label text, label typography, proportions,
and finish. Allow only the room, chair, throw, and lighting to change.
Calm and premium vibe but deliberately un-styled; feels spontaneous. No
neon, no stock-photo cliches, no obvious staging. No text, no labels, no
writing anywhere except the candle's own label as shown in Image 1.
```

Why this works: UGC needs explicit imperfection — the stray hair and fingerprint cues break the "too perfect" tell; specifying iPhone framing and banning HDR crush keeps the color science honest.

### 5. Editorial — "full-bleed candle in a luxury spa vignette"

Brief: Magazine-register full-bleed hero for a brand campaign, portrait.

```
SCENE: A dimly-lit luxury spa treatment room at dusk. A black stone massage
slab, white terry towels folded in a neat stack, eucalyptus branches lying
beside the candle, pale smoke drifting through the frame.
SUBJECT: The 9oz Acme candle, lit, centered, flame visible, candle occupies
roughly 45% of the frame height, oriented slightly three-quarters to reveal
the label while showing the flame profile.
CAMERA: 85mm lens, close-up hero shot, eye-level at candle height, very
shallow DoF at f/1.8. The candle label and flame are tack-sharp, the stone
slab and towels defocused into soft tonal blocks.
LIGHTING: Single hard key light from camera-right at 45 degrees above,
color temperature 2800K, carving a high-contrast chiaroscuro shadow along
the left side of the candle. Faint warm flame glow on the underside of
drifting smoke.
STYLE: Photorealistic, editorial magazine register, shot on Kodak Portra
800 pushed one stop, fine grain, visible wax sheen, visible eucalyptus leaf
veins, subtle smoke turbulence, deep velvety blacks in the shadows.
CONSTRAINTS: Image 1 is the product reference. Preserve the candle from
Image 1 exactly — color, shape, label text, label typography, proportions,
and finish. Allow only the room, stone slab, towels, eucalyptus, smoke, and
lighting to change. Calm and premium vibe, restrained palette, generous
negative space on the left third of the frame for campaign headline
placement. No neon, no clutter, no stock-photo cliches. No text, no labels,
no writing anywhere except the candle's own label as shown in Image 1.
Designed for a full-bleed portrait hero at 1024x1536.
```

Why this works: named single key light at a specific angle gives the model one directional source to solve instead of averaging; leaving negative space on a named side of the frame makes the output usable as a headline plate.

## Critique anchors

When critiquing a generated lifestyle image against the six rubric dimensions, these are the concrete bars to clear.

- **Text legibility** — N/A when no text was intended. If any unintended text appears (signs, labels, packaging copy the prompt did not request), score this dimension `1` regardless of the rest of the image — the image broke its mode. The only legitimate text is the product's own label, and it must match Image 1 character-for-character.
- **Brand color adherence** — the scene's dominant palette aligns with `brand.colors` and the vibe list. No neon, no clashing saturated hues, no off-brand warm/cool cast. The accent color appears naturally (a brass handle, a ribbon, a warm light source) rather than being splashed on.
- **Subject fidelity** — the hero named in SUBJECT is the hero in the image, at roughly the scale specified. Not buried, not duplicated, not miniaturized. Scale cues from the prompt are respected ("30% of the frame" holds within reasonable tolerance).
- **Composition** — rule-of-thirds or center framing is deliberate; the eye lands on the hero first; negative space is where the prompt asked for it; props are spaced, not piled; the horizon or surface is level unless the prompt asked for a tilt.
- **Mode realism** — the image reads as a photograph, not as 3D render, illustration, or AI pastiche. Skin has pores, fabric has weave, metal has micro-scratches, light falls off with a plausible curve. No plastic-sheen faces, no impossibly clean highlights on every surface, no uncanny symmetry.
- **Ref-lock** — when `brand.refs.product_hero` was attached, the product in the output matches Image 1 on color, shape, proportions, label text, and label typography. No invented label copy, no restyled silhouette, no color drift toward the scene's palette.

## Common failure modes & fixes

- **CGI-looking output** — skin is too smooth, highlights are too clean, everything has a product-render sheen. Fix: remove any word in the prompt that implies studio polish (`commercial`, `pristine`, `polished`, `e-commerce`, `product shot`). Add real-world texture cues to STYLE: `Kodak Portra 400, subtle film grain, visible skin pores, visible fabric weave, faint imperfection on the glass`. Add a named lens and a specific f-stop.
- **Product drift** — across iterations the candle color shifts, the label type changes, proportions warp. Fix: add or expand the ref-lock block in CONSTRAINTS, enumerating the preserve list explicitly — `color, shape, label text, label typography, proportions, and finish` — and repeat that full list on every iteration. Drift happens because preservation instructions decay across edits; restating them resets the lock.
- **Unwanted text in the frame** — spurious signs, made-up book spines, a fake packaging label. Fix: add to CONSTRAINTS: `no text, no labels, no writing, no signage, no typography anywhere in the frame, except the product's own label as shown in Image 1`. This single sentence resolves the majority of stray-text cases.
- **Wrong aspect ratio** — the model renders square when you wanted portrait, or vice versa. Fix: state the size literally inside the prompt, not just in the API call. Append `Generate at 1024x1536 portrait.` or `Generate at 1536x1024 landscape.` as the final line of the prompt. Also state the destination use ("designed for an Instagram feed post at 4:5") — that nudges framing.
- **Face or identity drift** — when a person from `brand.refs.model_hero` is locked, their face morphs, their expression changes, or their body shape shifts. Fix: add the strict preservation clause — `Preserve the model's face, body shape, pose, hair, and expression exactly from Image 2. Only the held product, the outfit as described, and the background may change. Do not restyle, re-age, or otherwise alter the person.` Repeat on every iteration.
- **Over-staged scene** — props pile up, the image looks like a catalog page instead of a moment. Fix: reduce the prop count in SCENE to three items max, add `negative space on the [top/left/right]`, add `one hero, supporting props recede in focus`, and explicitly forbid `no clutter, no stock-photo cliches, no over-styling`.
- **Flat or muddy lighting** — scene looks evenly grey, no direction, no depth. Fix: replace vague lighting ("nice light", "natural") with a named scheme and a direction — `Soft diffuse north-window light from camera-left at 30 degrees, casting a gentle shadow to the bottom-right`. Name a color temperature in Kelvin when the mood depends on it.
