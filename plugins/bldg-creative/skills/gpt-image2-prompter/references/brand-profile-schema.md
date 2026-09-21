# Brand Profile Schema

Brand profiles live at `brands/<slug>.yaml` in the workspace. They compound over time: the more fields you fill in, the more tailored every generated prompt becomes. One profile, many images, consistent brand.

## Minimum viable profile

Four fields:

```yaml
name: "Acme Candle Co"
slug: "acme"
brand_type: "product"
schema_version: 1
```

Save as `brands/acme.yaml`. Generate with brand slug `acme`. That's it — everything else is optional but adds lock-in.

## Complete profile (all fields)

See `examples/brands/luma-candle-co.yaml` for a fully populated example.

```yaml
# ── REQUIRED ────────────────────────────────────────────────
name: "Luma Candle Co"         # display name used in prompts
slug: "luma-candle-co"         # lowercase-kebab; MUST match filename stem
brand_type: "product"          # product | service | personal | media
schema_version: 1              # always 1 for v1.x

# ── VISUAL IDENTITY ─────────────────────────────────────────
colors:
  primary:   "#0E3A5F"         # hex #RRGGBB only
  secondary: "#F5E6D3"
  accent:    "#D4A574"         # optional third color

typography:
  display: "Playfair Display"  # headline font; blank → "serif"
  body:    "Inter"             # body font; blank → "sans-serif"

logo:
  path: "./logo.png"           # workspace-relative path; "" to skip
  usage: "bottom-right, small, subtle"

# ── VOICE & POSITIONING (drive prompt tone) ─────────────────
tagline: "Slow-burning luxury for mindful mornings"
audience: "women 30-55, wellness-oriented"
vibe: ["calm", "premium", "tactile", "warm-minimal"]  # 3–6 adjectives

# ── VISUAL DO / DON'T ───────────────────────────────────────
do:
  - "natural daylight, soft shadows"
  - "real bathroom, bedroom, or living-room contexts"
  - "single product hero"
dont:                          # YAML-safe key (NOT "don't" with apostrophe)
  - "no neon colors"
  - "no cluttered scenes"
  - "no cartoonish illustration"

# ── STANDING REFERENCE IMAGES (auto-attached when relevant) ──
refs:
  product_hero: "./luma-candle-hero.png"   # auto-attached in lifestyle mode
  style_anchor: "./luma-aesthetic.png"     # auto-attached in infographic mode
  # additional named refs can be attached on-demand by the user

# ── PER-BRAND DEFAULTS (override mode defaults) ─────────────
defaults:
  infographic_size: "1536x1024"
  lifestyle_size:   "1024x1536"
  quality:          "high"     # low | medium | high
```

Note: use `dont` (no apostrophe) as the YAML key. Some YAML parsers trip on the apostrophe; stay safe and use the plain key.

## Field-by-field reference

### Required

| Field            | Type   | Notes                                                           |
| ---------------- | ------ | --------------------------------------------------------------- |
| `name`           | string | Display name used in prompts                                    |
| `slug`           | string | Lowercase-kebab; MUST match filename stem                       |
| `brand_type`     | enum   | `product` \| `service` \| `personal` \| `media`                 |
| `schema_version` | int    | Always `1` for v1.x of this skill                               |

### Visual identity

- `colors.primary` / `colors.secondary` / `colors.accent` — hex strings like `"#0E3A5F"`. Injected into infographic prompts as background + accents and into lifestyle prompts as palette guidance (carried by natural materials, never splashed on as paint).
- `typography.display` / `typography.body` — font family names. Used in infographic prompts for headline/body discipline.
- `logo.path` — workspace-relative (or absolute) path to the logo image. When present, auto-attached to infographic prompts as a reference image and referenced by numeric index in the CONSTRAINTS slot. **Never describe a logo in text** — describing it makes the model invent one.
- `logo.usage` — natural-language placement rule (e.g., "bottom-right, small, subtle").

### Voice & positioning

- `tagline` — one-line positioning statement. Flows into corner copy on infographics and atmosphere cues in lifestyle.
- `audience` — who the image is for. Informs mood, framing, and photoreal register.
- `vibe` — 3–6 adjectives like `["calm", "premium", "tactile"]`. Heavy-lifted in lifestyle mode; informs both SCENE atmosphere and STYLE register.

### Visual do / don't

- `do` / `dont` — short imperative strings. Appended directly to the CONSTRAINTS slot. Keep items to 3–6 per list; more and the prompt gets noisy.
- Lifestyle-only items (e.g., "natural daylight") are filtered out of infographic prompts. Infographic-only items (e.g., "flat vector") are filtered out of lifestyle prompts.

### Standing reference images

- `refs.product_hero` — auto-attached to **lifestyle** prompts as `Image 1`. This is the single biggest quality lever for product work. Locks color, shape, label text, label typography, proportions, and finish.
- `refs.style_anchor` — auto-attached to **infographic** prompts as `Image 1`. Keeps a series visually consistent across dozens of infographics (same grid discipline, color temperature, type hierarchy).
- Additional keys under `refs` are available for on-demand attachment when the user asks.

### Per-brand defaults

- `defaults.infographic_size` / `defaults.lifestyle_size` — `"WxH"` format like `"1536x1024"`.
- `defaults.quality` — `low` | `medium` | `high`.

## Validation rules

Enforce before writing any brand YAML:

- Required fields present with correct types.
- `slug` matches `^[a-z][a-z0-9-]*$` and matches the filename stem.
- `brand_type` is in the allowed enum.
- Hex colors match `^#[0-9A-Fa-f]{6}$`.
- `defaults.infographic_size` / `defaults.lifestyle_size` match `^\d+x\d+$`.
- `defaults.quality` is one of `low | medium | high`.
- Missing file paths (logo, refs) → warning, not error.
- Unknown top-level keys → warning (forward-compat).

Warnings print during the preview step; they don't block generation. Hard errors do — fix or re-ask before writing.

## Setup paths

Four ways to create a brand profile, all produce the same artifact at `brands/<slug>.yaml`:

1. **In-chat Q&A** (default) — walk through the schema one field at a time. Required first, optionals after.
2. **Extraction from a source** — paste a description, a file, or a URL. The skill extracts what it can, then fills gaps via Q&A.

   | Source                                   | Handling                                                                                |
   | ---------------------------------------- | --------------------------------------------------------------------------------------- |
   | Quoted description                       | Extract in-thread                                                                       |
   | `.txt` / `.md` / `.docx` in workspace    | `read` the file, extract                                                                |
   | `.pdf` in workspace                      | `read` the PDF (vision — look at swatches, type, layouts, logo treatment)               |
   | `http(s)://` URL                         | `fetch_url` with an extraction prompt                                                   |
   | Google Doc / Google Sheet                | Use the Google Docs / Sheets connector if authenticated; otherwise `fetch_url` fallback |
   | A product-research-amazon output doc     | Extract only brand-relevant fields (tone, audience, vibe); do not copy product copy     |

3. **Copy the template** — start from `examples/brand.template.yaml`, edit the values, save.
4. **Paste a full YAML** — if the user already has a complete brand YAML, validate it and write directly.

## Troubleshooting

- **"Colors don't show up in the generated image"** → Colors are guidance, not constraints. For exact adherence use infographic mode with `quality=high` and include the hex directly in the brief. Lifestyle mode carries color via natural materials (marble, brass, linen) — it won't paint walls a hex.
- **"Logo is the wrong size"** → Tune `logo.usage` with specific width like "bottom-right corner, approximately 8% of image width". Never describe the logo visually.
- **"Product identity drifts between generations"** → Add `refs.product_hero`. Ref-lock is the biggest quality lever. Without it, the product will drift on color, label text, and proportions.
- **"I want to update the schema later"** → Bump `schema_version`. Old YAMLs keep working until an explicit deprecation. Brand YAMLs are yours — they live in the workspace, not in the skill directory.
