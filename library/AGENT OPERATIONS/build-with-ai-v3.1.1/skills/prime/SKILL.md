---
name: prime
description: >
  Load all core context files to prime Claude for a work session.
  Use this skill whenever the user says 'prime', 'load context',
  'read your files', 'get up to speed', 'load your instructions',
  'refresh context', 'start fresh', or at the beginning of any
  session where Claude needs full context about the user's identity,
  brand voice, working style, and project standards. Also trigger
  when someone says 'remember who I am', 'load everything', or
  'context check'.
---

# Prime - Context Loader

Load core context files so Claude has full working knowledge for the session. Uses a tiered system — Tier 1 always loads, Tier 2 and Tier 3 load based on the session type.

## Tier 1: Core Identity (always load)

Read ALL of these in parallel. No task starts without these loaded.

Check both the folder root and CONTEXT/ subfolder for each file. Use whichever location exists.

1. `about-me.md` — Identity, businesses, tools, values
2. `brand-voice.md` — Voice modes, tone, anti-voice, selection guide
3. `working-style.md` — Planning flow, output formats, communication preferences, do/don't rules
4. `voc.md` — Buyer language, pain phrases, desired outcomes, objections, jargon blacklist. Accept `voice-of-customer.md` as an alias filename — load whichever exists.
5. `STANDARDS.md` — Folder structure, naming conventions, config patterns (if exists)
6. `global-instructions.md` — Folder protocol, naming conventions, security rules (check root and `reference/` subfolder)

### VOC Staleness Check

When `voc.md` (or `voice-of-customer.md`) loads, parse the `Last updated:` field from the Evidence quality section.

- If the field is present and the date is older than 90 days, emit one informational line in the status report: `VOC last updated YYYY-MM-DD (>90 days). Consider running the 90-day refresh.`
- If the field is missing or unparseable, treat as ">90 days" and emit the same nudge.
- Never block the session. The check is informational only.

The 90-day cadence aligns with the scheduled VOC refresh recommended by the cowork-onboarding skill.

## Tier 2: Content Pipeline (load for content sessions)

Load these when the user mentions content, writing, articles, social media, or publishing. Also load if the command is `/prime content` or `/prime x`.

Scan for content pipeline files in common locations:
- `twitter/` or `x/` or `content/` directories
- Pipeline rules, quality contracts, voice examples, article structures
- Any `PIPELINE-RULES.md`, `QUALITY-CONTRACT.md`, or similar files

If content pipeline files exist, load them. If not, skip silently.

## Tier 3: Project Context (load on demand)

Scan `PROJECTS/` and list active project folders. If the user specifies a project (e.g., `/prime [project-name]`), read that project's top-level .md files:

- `PROJECTS/{project}/*-project-instructions.md`
- `PROJECTS/{project}/*-brand-voice.md`
- Any other .md files at the project root

List all discovered project folders in the status report so the user knows what's available.

## How to Interpret the Command

| Command | What loads |
|---------|-----------|
| `/prime` | Tier 1 only |
| `/prime content` or `/prime x` | Tier 1 + Tier 2 |
| `/prime [project-name]` | Tier 1 + Tier 3 for that project |
| `/prime all` | Tier 1 + Tier 2 + Tier 3 (all projects scanned, instruction files loaded) |
| `/prime content [project-name]` | Tier 1 + Tier 2 + Tier 3 for specified project |

If the user just says "prime" with no modifier, load Tier 1. Fast and general.

## Execution Rules

- Read files in parallel wherever possible. Speed matters.
- Don't dump file contents into the chat. Load into working memory, not the conversation.
- If a file doesn't exist, skip it silently.
- If any Tier 1 file is missing, flag it and offer to create it via the onboarding skill: "Missing [file]. Want me to run onboarding to set it up?"
- If `voc.md` is missing specifically, the nudge wording is: "No VOC file found — run cowork-onboarding to capture buyer language. The agent will fall back on brand voice alone for now, but VOC is what makes marketing and sales sound like the buyer."

## Status Report

After loading, output a tight status report:

```
Primed. Loaded:
- about-me.md — [brief summary of what's in it]
- brand-voice.md — [voice modes found]
- working-style.md — [key preferences]
- voc.md — [count of buyer phrases / pain language / objections; emit staleness line if >90 days]
- [additional Tier 1 files found]

Content pipeline: [loaded / not requested / not found]
Project context: [project name loaded / not requested]

Active projects: [list discovered project folders, or "none found"]

Ready to work.
```

No fluff. No re-reading contents. Confirm what loaded and signal ready.
