---
name: gpt-image2-prompter
description: "Produce on-brand, paste-ready GPT Image 2 prompts for ChatGPT. Two modes: `infographic` for designed, data-forward graphics (charts, stat cards, comparison tables); `lifestyle` for photorealistic product-in-context imagery. Loads a reusable brand profile (colors, typography, vibe, do/don't, reference images) and composes a tightly engineered prompt plus size, quality, and attachment list. Use when the user asks for a GPT Image 2 prompt, an on-brand image brief, a ChatGPT image plan, a product lifestyle shot, a stat/benefits infographic, an Amazon listing image plan, or says things like 'make an infographic', 'lifestyle image', 'image prompt', or 'brand image brief'. Orchestrates cleanly with the product-research-amazon skill: given a research markdown, outputs a batch plan of one hero lifestyle plus 3\u20135 infographic prompts mapped to the biggest VoC, competitor-gap, feature, and seasonal signals."
license: MIT
metadata:
  author: jsnsdirect
  version: "1.0.0"
  adapted_from: "gpt-image2-gen v0.3.0 (Claude Code skill)"
---

# gpt-image2-prompter

Turn a brief plus a brand profile into a tightly engineered GPT Image 2 prompt that you paste into ChatGPT. Two modes: `infographic` and `lifestyle`. Reusable brand profile compounds over time. Pairs with the `product-research-amazon` skill to turn a research document into a batch image plan.

## When to use this skill

Use when the user asks you to:

- Generate a GPT Image 2 / ChatGPT image prompt
- Create an infographic prompt (bar chart, stat card, comparison table, process flow, quote card)
- Create a lifestyle / product-in-context / hero / flat-lay / UGC image prompt
- Build an on-brand image brief from a marketing deck, research doc, or product page
- Produce a batch image plan for an Amazon listing, landing page, or campaign
- Capture / create a brand profile (colors, typography, vibe, do/don't) for reuse

Do NOT use for generating the image directly in-thread — this skill produces paste-ready prompts for ChatGPT's GPT Image 2. For in-thread image generation use the `media` skill.

## Operating model

This skill runs entirely inside the conversation. There is no CLI, no browser automation, no external script execution. The flow is:

1. Resolve or create a brand profile (a YAML file in `brands/<slug>.yaml` inside the workspace).
2. Compose a prompt from the brand profile + the user's brief + the mode template.
3. Print a copy-paste block the user pastes into ChatGPT (operator mode).
4. When the user reports the generated image back (uploaded or linked), critique it against the rubric and optionally propose one surgical refinement prompt.

Every successful run saves `brief.md`, `prompt.md`, and `metadata.json` to `outputs/<YYYY-MM-DD>_<mode>_<brand>_<slug>/` in the workspace, and appends one line to `outputs/.invocations.jsonl`. Never delete anything. On filename collision auto-version with `_v2`, `_v3`.

## Decision tree

Parse the user's request, then walk this tree. Load only the references you need.

1. **Is the user asking to create or edit a brand profile?** (e.g. "set up my brand", "new brand profile", "update colors for X")
   → Run the **brand profile wizard** (see "Brand profile wizard" below). Stop after writing the YAML and suggesting the next command.

2. **Is the user asking for a batch image plan from an Amazon research document or marketing deck?**
   → Load `references/orchestration-with-product-research.md` and follow the batch-planner flow. Produces one lifestyle hero + 3–5 infographics as separate paste-ready blocks.

3. **Is it a single image request?** Determine the mode:
   - Charts, stat cards, comparison tables, process flows, quote cards, explainer diagrams → `infographic`
   - Products in scenes, hands holding product, flat lays, editorial heroes, UGC-feel shots → `lifestyle`
   - Unclear → ask one clarifying question, then continue.

4. **Is the brief <3 meaningful words or vague?** → ask exactly one clarifying question, then continue.

5. **Is a brand slug referenced?** (e.g. "--brand=acme" or "for my Luma brand")
   - Yes → read `brands/<slug>.yaml` from workspace. Missing → offer: "No brand `<slug>` found. Want me to run the wizard, or should I proceed with generic brand defaults?"
   - No → proceed with generic defaults (no brand lock) and note that clearly in the output.

6. **Load the mode reference**:
   - `infographic` → `references/infographic-prompting.md`
   - `lifestyle` → `references/lifestyle-prompting.md`

7. **Compose the prompt** using the mode's slot template + the brief + injected brand fields (colors, typography, logo, do/don't, vibe, refs).

8. **Resolve size**: explicit user request > `brand.defaults.<mode>_size` > mode default.

9. **Resolve quality**: explicit user request > `brand.defaults.quality` > mode default.

10. **Resolve refs**: user-provided refs + standing brand refs (`product_hero` for lifestyle, `style_anchor` for infographic, plus `logo` when relevant for infographic). Attach by numeric index (`Image 1`, `Image 2`…) and reference them in the CONSTRAINTS slot.

11. **Save artifacts** to `outputs/<YYYY-MM-DD>_<mode>_<brand>_<slug>/`:
    - `brief.md` — the original brief
    - `prompt.md` — the composed prompt
    - `metadata.json` — slots, settings, refs, critique placeholder

12. **Print the operator copy-paste block** (see `references/operator-mode.md` for exact format). The user pastes it into ChatGPT, generates, and returns the image.

13. **When the user returns the image** (shares a file or a link, or pastes it): read it, run the critique per `references/critique-rubric.md`, print scored results, and if it fails offer exactly one refinement prompt (one-shot — never recurse). Update `metadata.json` with the critique block.

14. **Report**: output directory, critique score, any refinement offered.

## Brand profile wizard

Brand profiles live at `brands/<slug>.yaml` in the workspace. The wizard runs entirely in-thread.

**Schema reference**: `references/brand-profile-schema.md`. Load it before writing YAML so field names and validation rules are correct.

**Input classification**:

| Input                                          | Handling                                                                                           |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| No argument / vague description                | Q&A: walk through required fields (`name`, `slug`, `brand_type`) one at a time, then offer optionals |
| Quoted description ("calm premium candle co")  | Extract what you can, then Q&A for gaps                                                            |
| Local `.txt` / `.md` / `.docx` in workspace    | `read` the file, extract fields, Q&A for gaps                                                      |
| Local `.pdf` in workspace                      | `read` the PDF (vision enabled), extract fields including color swatches and typography, Q&A for gaps |
| `http(s)://…` URL                              | Use `fetch_url` with an extraction prompt; Q&A for gaps                                            |
| Marketing deck PDF from prior product research | Extract brand-relevant fields only (colors, tone, audience); do not copy product copy verbatim     |

**Extraction prompt pattern** — when reading a PDF / site / doc, ask the model for exactly these fields in this order: `name`, `slug` (kebab-case guess from filename/title), `brand_type` (product | service | personal | media), `colors.primary/secondary/accent` as hex, `typography.display/body`, `logo.path` only if a file is provided, `tagline`, `audience`, `vibe` (3–6 adjectives), `do` (3–6 items), `don't` (3–6 items). Convert Pantone/RGB to hex. Never invent — if a field isn't in the source, leave it out.

**Validation** (enforce before writing):

- `slug` is lowercase-kebab-case and matches filename stem
- `brand_type` is one of: `product`, `service`, `personal`, `media`
- Hex colors match `^#[0-9A-Fa-f]{6}$`
- `defaults.*_size` matches `^\d+x\d+$`
- `defaults.quality` is one of: `low`, `medium`, `high`
- Required fields present: `name`, `slug`, `brand_type`, `schema_version: 1`

**Write flow**:

1. Preview the composed YAML to the user. Include a short "Notes" block (what was extracted automatically, what was guessed, what's missing).
2. Ask about missing required fields one at a time.
3. On confirmation, `write` to `brands/<slug>.yaml` in the workspace.
4. Tell the user: "Done. Try: generate an infographic for `<slug>` with brief `"..."`" — keep it natural, do not hardcode a slash-command pattern.

A starting-point template lives at `examples/brand.template.yaml`. A fully populated example lives at `examples/brands/luma-candle-co.yaml`.

## Mode defaults

| Mode          | Default size | Default quality | Primary use                              |
| ------------- | ------------ | --------------- | ---------------------------------------- |
| `infographic` | 1536x1024    | high            | Charts, stat cards, tables, process flows |
| `lifestyle`   | 1024x1536    | medium          | Product-in-context, editorial, UGC       |

Override precedence for both size and quality: explicit user request > brand defaults > mode default. Never exceed 2560x1440.

## Prompt-engineering discipline (non-negotiable)

These rules come from OpenAI's GPT Image 2 prompting guide. Apply them to every generated prompt.

**For infographics** — detailed guidance in `references/infographic-prompting.md`:

1. Wrap every literal string that must render in double quotes.
2. Specify typography (font, weight, size, color, placement) for every label.
3. Spell brand names letter-by-letter on first appearance.
4. Add `render verbatim, do not paraphrase` in the CONSTRAINTS slot.
5. Add `appears once` to every single-instance string (kills duplicate-headline failures).

**For lifestyle** — detailed guidance in `references/lifestyle-prompting.md`:

1. The literal word `photorealistic` must be in the STYLE slot.
2. Use photography language (named lens, film stock, f-stop, DoF), not art-direction language.
3. Add texture cues (pores, weave, patina, dust motes) — biggest lever against "looks AI".
4. When reference images are attached, spell out the preserve list (`color, shape, label text, label typography, proportions, finish`) in every prompt AND every refinement.
5. Default CONSTRAINTS for lifestyle must include: `no text, no labels, no writing anywhere in the frame, except the product's own label as shown in Image 1`.

## Output contract

Every successful invocation writes to `outputs/<YYYY-MM-DD>_<mode>_<brand-slug>_<kebab-brief>/`:

```
outputs/2026-04-24_infographic_luma-candle-co_q3-revenue/
├── brief.md         # original brief
├── prompt.md        # composed prompt (paste-ready)
└── metadata.json    # slots, settings, refs, critique
```

Plus one line appended to `outputs/.invocations.jsonl` with timestamp, mode, brand, brief, output_dir.

When the user returns a generated image, save it as `generated.png` in the same output dir and update `metadata.json.critique`.

## Operator copy-paste block

After composing, print the block per `references/operator-mode.md` — header, attachments (absolute workspace paths, or instruct the user to attach their own local files), fenced prompt, settings line, save target, "then reply 'done' (or paste the image back)", footer.

## Critique loop

When the user returns the image, load `references/critique-rubric.md` and score across six dimensions (text legibility, brand color adherence, subject fidelity, composition & hierarchy, mode realism, ref-lock). N/A dimensions drop out. Pass criteria: all applicable dimensions ≥ 2 AND no 0s.

On fail, produce exactly ONE refinement prompt that:

1. Starts with "Regenerate the same <mode>."
2. Re-states the full preservation list.
3. Makes exactly one surgical change.
4. References attached images by index.
5. Is concrete, not vague.

Refinement is one-shot. If it still fails, hand the loop back to the user — do not recurse.

## Orchestrating with `product-research-amazon`

When the user has run `product-research-amazon` (or hands you its output markdown) and asks for image assets, load `references/orchestration-with-product-research.md`. The batch planner reads the research doc, extracts the ICP, top VoC insight, biggest competitor review gap, hero feature, and seasonal signal, and outputs:

- **1 lifestyle hero** — ICP using the product in its highest-intent context
- **3–5 infographics** covering: top benefit/stat, competitor-gap callout, feature explainer, comparison/before-vs-after, seasonal/use-case hook

Each comes with a fully-composed paste-ready block using the same brand profile. The user pastes them into ChatGPT one at a time (or in parallel tabs).

Important: the orchestration never re-reads the raw marketing deck; it only reads the research markdown that `product-research-amazon` produced. That keeps the main thread cheap and the image briefs grounded in researched signals, not raw source material.

## Fail-safe rules

- **Brand YAML invalid** → print field-level errors, do not write, do not generate.
- **Vague brief** → one clarifying question, then continue.
- **ToS-risk content** (copyright characters, real public figures without permission, explicit content) → soft block with explanation. If the user confirms they have rights/permission, proceed and log the confirmation in `metadata.json.user_acknowledgement`.
- **Collision in outputs/** → auto-version `_v2`, `_v3`. Never overwrite.
- **User returns an image that doesn't match the prompt size/mode** → note the mismatch in critique, score accordingly, still save.

## Scope

This skill only touches, inside the workspace:

- `outputs/` — writes (never deletes)
- `brands/` — reads (writes only during the wizard)
- `refs/` — reads (user-provided reference images)

Never modifies or reads anywhere else on disk.

## References (loaded on demand)

- `references/infographic-prompting.md` — load when mode=infographic
- `references/lifestyle-prompting.md` — load when mode=lifestyle
- `references/brand-profile-schema.md` — load during wizard or on validation errors
- `references/operator-mode.md` — load before printing the copy-paste block
- `references/critique-rubric.md` — load when scoring a returned image
- `references/orchestration-with-product-research.md` — load when building a batch plan from a product research markdown

## Examples

- `examples/brand.template.yaml` — starting point for new brand profiles
- `examples/brands/luma-candle-co.yaml` — fully populated product brand
- `examples/infographic-brief-walkthrough.md` — brief → injected slots → composed prompt → expected output → pass critique → alt fail + refinement
- `examples/lifestyle-brief-walkthrough.md` — same shape, lifestyle mode
