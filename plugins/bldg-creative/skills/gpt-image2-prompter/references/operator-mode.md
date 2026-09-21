# Operator Mode

This skill's only execution path. The skill does the engineering work (brief → optimized prompt → size/quality/refs/attachments) and prints a copy-paste block. The user takes it to ChatGPT, generates the image, and returns it.

## The copy-paste block format

After composing the prompt, print this block **verbatim** in the chat. Do not editorialize around it — the user needs to copy cleanly into ChatGPT.

```
────── COPY-PASTE BLOCK ──────
Open ChatGPT → new chat → ask "create an image".

Attach these files:
  • <absolute workspace path or instruction for the user to attach their own file>

Prompt:
┌──────────────────────────────────────────────────────────
│ <composed prompt, full multi-line, wrapped to ~80 cols>
└──────────────────────────────────────────────────────────

Settings: <WxH> <orientation>, quality: <low|medium|high>

Download the result and save to:
  <absolute path under workspace outputs/...>

Then reply "done" (or upload the image here / paste the link).
─────────────────────────────────
```

## Attachment rules

Reference images attach to ChatGPT by upload. List them in order — that order determines the `Image 1`, `Image 2` indices the prompt references.

- **Files in the workspace** (e.g. `refs/luma-candle-hero.png`) → print the absolute workspace path. Also offer to `share_file` it back to the user so they can download it and re-upload to ChatGPT.
- **Files on the user's machine** (never uploaded to this thread) → print a placeholder path the user recognizes, e.g. `<your product hero image — same one in Image 1 slot>`, and remind them the prompt references it as `Image 1`.
- **No attachments** → print `(no attachments)` on the attachments line.

Standing refs from the brand profile (`product_hero`, `style_anchor`, `logo`) are listed in the attachment block automatically. If those files aren't present in the workspace, note it and ask the user to provide them before pasting into ChatGPT — ref-lock language in the prompt assumes the references are attached.

## Settings line

- **Size**: `WxH orientation` — e.g., `1536x1024 landscape`, `1024x1536 portrait`, `1024x1024 square`.
- **Quality**: one of `low`, `medium`, `high`. Infographics default `high` (small text garbles at lower quality). Lifestyle default `medium`.

Repeat the size inside the prompt itself (usually in CONSTRAINTS) — not just on the settings line. GPT Image 2 sometimes ignores the size parameter; a literal `Generate at 1024x1536 portrait.` line in the prompt is a belt-and-suspenders fix.

## Save target

Always give an absolute path under the workspace: `outputs/<YYYY-MM-DD>_<mode>_<brand-slug>_<kebab-brief>/generated.png`. When the user downloads from ChatGPT and uploads back into this thread, save it to that exact path using `write` (or have them save it and `read` the uploaded file, then move it).

## Resume protocol

When the user replies `done` (or uploads an image / shares a link):

1. **File returned** → read the image with the vision-enabled `read` tool.
2. **Corrupt / wrong file type** → ask: "The file doesn't look like a valid PNG. Please re-download from ChatGPT and try again."
3. **Wrong size/aspect** → note in critique, still save, still score.
4. Proceed to critique per `references/critique-rubric.md`.

If the user replies something other than `done` / image / link, treat it as feedback and ask: "Do you want to pause, retry with a tweaked prompt, or skip critique?"

## Example

```
────── COPY-PASTE BLOCK ──────
Open ChatGPT → new chat → ask "create an image".

Attach these files:
  • /home/user/workspace/refs/luma-candle-hero.png
  • /home/user/workspace/refs/luma-logo.png

Prompt:
┌──────────────────────────────────────────────────────────
│ SCENE: A sun-washed marble bathroom shelf in a pre-war
│ apartment on a weekday morning. Pale Carrara marble with
│ soft grey veining, white subway tile behind, a folded
│ linen towel and small face-oil bottle softly defocused.
│
│ SUBJECT: A single Luma pillar candle placed slightly
│ left of center on the marble shelf, unlit, label facing
│ camera, occupying ~40% of frame height. No second candle,
│ no hand in frame.
│
│ CAMERA: 50mm lens, medium shot, eye-level at candle mid-
│ height, shallow DoF at f/2.5. Candle tack-sharp; marble
│ softly defocused; tile fully blurred.
│
│ LIGHTING: Soft diffuse morning light from a north-facing
│ window camera-left at 30° above horizon, ~5200K. Long
│ soft shadow drifts to camera-right along the shelf.
│
│ STYLE: Photorealistic, Kodak Portra 400, subtle film
│ grain, visible marble veining, linen weave, brass patina.
│ Slow-burning luxury for mindful mornings — unhurried,
│ considered, quiet.
│
│ CONSTRAINTS: Image 1 is the product reference. Preserve
│ the candle from Image 1 exactly — color, shape, label
│ text, label typography, proportions, finish. Allow only
│ environment, lighting, and props to change. No neon, no
│ clutter, no cartoonish illustration. No text, no labels,
│ no writing anywhere in the frame except the candle's own
│ label as shown in Image 1. Generate at 1024x1536 portrait,
│ for an Instagram feed post at 4:5.
└──────────────────────────────────────────────────────────

Settings: 1024x1536 portrait, quality: high

Download the result and save to:
  /home/user/workspace/outputs/2026-04-24_lifestyle_luma-candle-co_marble-shelf/generated.png

Then reply "done" (or upload the image here / paste the link).
─────────────────────────────────
```

## What operator mode does NOT do

- Does not open the browser for you.
- Does not click anything in ChatGPT for you.
- Does not track ChatGPT quota — if you hit the quota banner, the skill has no visibility; wait out the window or upgrade the plan.
- Does not generate images in-thread. For that, use the `media` skill instead.
