---
name: signal-stack-builder
description: "Build a personalized market intelligence stack: interview, classify trustworthy sources by category, produce a weekly brief template, generate /schedule prompts. Outputs to INTELLIGENCE/."
---

# Signal Stack Builder

This skill interviews the user, builds a personalized market intelligence stack, produces a weekly brief template, and generates copy-paste `/schedule` prompts the user runs themselves to automate weekly briefs and monthly source verification.

## Hard rules

Bake these into every step:

- **Never publish or send anything externally.** Outputs are for the Operator's internal review only.
- **Never schedule a task programmatically.** Cowork has no public scheduling API. The skill produces copy-paste `/schedule` prompts; the user runs `/schedule` themselves.
- **Always read VOC before drafting source recommendations.** A signal stack drafted without VOC will be generic and miss buyer venues. If `CONTEXT/voc.md` is missing, stop and tell the user to complete `buildwithai-plugin` v3.1.0 onboarding first.
- **Outputs go to `INTELLIGENCE/` only.** Never `OUTPUTS/`, never `PROJECTS/`. Create `INTELLIGENCE/` at the workspace root if it doesn't exist.
- **If validation fails, surface explicitly.** Don't silently save a stack that doesn't meet the bar — tell the user what's missing and offer to expand.

## Workflow

### Step 1 — Read context

Load these files. If any are missing, handle as below:

- `CONTEXT/about-me.md` — required. If missing, ask the user to run `buildwithai-plugin` onboarding.
- `CONTEXT/voc.md` — required. If missing, **stop and tell the user**: "Voice of Customer is required for source classification. Run the VOC capture in `buildwithai-plugin` v3.1.0+ onboarding, then re-run this skill."
- `CONTEXT/working-style.md` — preferred. Note any mentioned formatting preferences (bullet style, brief length).

### Step 2 — Interview

Ask these 10 questions, one at a time. Wait for the user's answer before moving on. Take their answers verbatim — paraphrasing strips signal.

1. What market or category should we watch?
2. Who are the 5 to 10 competitors or substitutes?
3. Where do your buyers complain, ask questions, or compare options?
4. What events would change your marketing or sales priorities?
5. Which signals matter most: customer pain, competitor moves, market news, creator content, buyer objections, pricing changes? (Pick top 2–3.)
6. What sources are trustworthy enough to act on?
7. How often should the brief run? (Default: weekly.)
8. What should count as a high-priority signal?
9. Where should the weekly brief be saved? (Default: `INTELLIGENCE/weekly-briefs/YYYY-MM-DD.md`.)
10. Who reviews the brief?

### Step 3 — Classify sources

Read `references/signal-source-rubric.md` (relative to this SKILL.md). Use the four categories defined there:

1. Customer / audience
2. Competitor
3. Market / category
4. Internal sales / customer feedback

Map every source the user mentioned in steps 2 + 6 + 8 to exactly one category. If a source doesn't fit any category, it's noise — drop it and tell the user why.

### Step 4 — Build the source list

For each source, capture:

- URL or search query
- Category
- One-sentence "why this exists" (must tie to a downstream decision type — see the rubric's decision-type catalog)
- Check cadence (daily / weekly / bi-weekly / monthly)
- Quick accessibility check: does the URL resolve? Does it return content from the last 30 days?

If a source fails the accessibility check at this step, ask the user before including it.

### Step 5 — Define signal types and high-priority rubric

Surface the user's answers from interview Q5 (signal types) and Q8 (high-priority criteria). State them explicitly in the artifact you're about to produce — these become the rubric the scheduled task uses each week.

### Step 6 — Generate `INTELLIGENCE/signal-stack.md`

Create the `INTELLIGENCE/` folder at the workspace root if it doesn't exist. Then write `INTELLIGENCE/signal-stack.md` with this structure:

- Header: Operator name, market focus, reviewer
- Source list grouped by the four categories — each source shows URL, why, cadence
- Signal types section
- High-priority rubric section
- Review cadence + reviewer

Match the structure of `examples/example-signal-stack.md` (read that example before drafting).

### Step 7 — Generate `INTELLIGENCE/weekly-brief-template.md`

Read `references/weekly-brief-template.md`. Personalize per the rules in that file (substitute the user's market, signal types, reviewer name). Save the personalized version to `INTELLIGENCE/weekly-brief-template.md`.

Validate: the personalized template MUST include the "This week's three decisions" section verbatim. If your personalization step drops it, restore it before saving.

### Step 8 — Output `/schedule` prompts to chat

Read `references/scheduled-task-guide.md`. Output the two `/schedule` prompts to the chat — verbatim — as instructions for the user to run themselves in Cowork.

Format:

> Two scheduled tasks to set up. Open Cowork, type `/schedule`, and paste each prompt below.
>
> **Prompt 1 — Weekly brief:**
> ```
> [paste from scheduled-task-guide.md prompt 1]
> ```
> Confirm cadence: weekly, Monday 8am local.
>
> **Prompt 2 — Monthly source verification:**
> ```
> [paste from scheduled-task-guide.md prompt 2]
> ```
> Confirm cadence: monthly, first Monday at 9am.
>
> Caveats: Cowork must be open and your laptop awake when tasks fire. See `references/scheduled-task-guide.md` in this skill's install for full details.

### Step 9 — Validation pass

Verify the artifacts you produced:

- [ ] `INTELLIGENCE/signal-stack.md` covers ≥3 source categories
- [ ] `INTELLIGENCE/signal-stack.md` lists ≥10 sources
- [ ] Every source has a "why" tied to a decision type
- [ ] `INTELLIGENCE/weekly-brief-template.md` includes the "This week's three decisions" section
- [ ] `INTELLIGENCE/` folder exists at the workspace root

If any check fails, surface to the user explicitly. Do not say "done" until all check.

### Step 10 — Done

Tell the user:

> Your signal stack is built at `INTELLIGENCE/signal-stack.md`. Your personalized weekly brief template is at `INTELLIGENCE/weekly-brief-template.md`. The two `/schedule` prompts above are your next step — run them in Cowork to start automated weekly briefs and monthly source verification.
>
> Module 1 Lesson 4 of the course walks through reviewing the stack and scheduling — pick up there for the rest of the prereq flow.

## Examples

When drafting outputs in steps 6 and 7, read these examples first:

- `examples/example-signal-stack.md` — sample stack for a fictional B2B SaaS business showing all 4 categories populated, 15 sources, validation status.
- `examples/example-weekly-brief.md` — sample brief showing the "three decisions" forcing function in action.

LLMs anchor better to concrete examples than abstract templates — read them.
