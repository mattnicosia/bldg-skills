# Build With AI

**Version:** 3.1.1
**Author:** Return My Time

Complete AI workspace setup, readiness assessment, and session priming for business owners using Claude Cowork. Three skills working together to take you from zero to operational with AI.

---

## What's Inside

### 1. Cowork Onboarding (`build-with-ai:cowork-onboarding`)

Interactive setup workflow that walks you through configuring your entire Claude Cowork workspace. Covers workspace structure, four context files (about-me, brand-voice, working-style, voice-of-customer), global instructions, connectors, skills, scheduled tasks, and security review.

**Two paths:**
- **Quickstart (~15 min):** Get productive fast with the essentials — about-me context file, a few connectors, and your first prompt.
- **Full Setup (~45-60 min):** Complete configuration across all seven capabilities with template seeding and self-assessment option.

**Trigger phrases:** "set up Cowork," "onboard me," "configure my setup," "help me get started"

### 2. Self-Assessment (`build-with-ai:self-assessment`)

AI readiness assessment built on the Three Outcomes methodology (Effectiveness, Efficiency, Quality). Identifies the highest-ROI AI opportunities in your business through a guided interview, then recommends specific Cowork skills to act on the findings.

**Tiers:**
- Quick Scan (~5 min): 8-10 questions
- Standard (~10 min): 15-20 questions with industry depth
- Deep Dive (~15 min): 25-30 questions, most thorough

**Produces:** Impact-Effort Matrix, Skills Recommendations, and a Skill Blueprint for your first custom skill.

**Trigger phrases:** "assess my business," "AI readiness check," "self-assessment," "where should I use AI," "audit my workflows"

**Prerequisite:** Onboarding must be completed first (context files must exist).

### 3. Prime (`build-with-ai:prime`)

Session context loader that reads your context files at the start of each work session so Claude knows who you are, your brand voice, and how you like to work.

**Tiered loading:**
- Tier 1 (always): about-me, brand-voice, working-style, voc (or voice-of-customer)
- Tier 2 (if present): content-specific context files
- Tier 3 (if present): project-specific context files

**Trigger phrases:** "prime," "load context," "read your files," "get up to speed"

---

## How the Skills Work Together

This plugin follows the **AOA framework** (Audit, Optimize, Automate):

1. **Onboarding** sets up your workspace and context files
2. **Prime** loads that context at the start of each session
3. **Self-Assessment** audits your workflows and identifies where AI has the biggest impact
4. The assessment outputs a **Skill Blueprint** you can use with the `skill-creator` to build your first custom skill (Optimize)
5. Scheduled tasks put your skills on autopilot (Automate)

---

## Installation

Two paths, in order of preference.

**1. From Cowork (primary).** In a Cowork session, type:

> Install the Build With AI plugin

Cowork resolves the plugin from this repository. Once installed, the `cowork-onboarding` skill walks you through the rest of setup.

**2. Manual upload (fallback).** If the in-session install isn't available to you:

1. Download `buildwithai-plugin-vX.Y.Z.zip` from the [Releases page](https://github.com/ReturnMyTime/buildwithai-plugin/releases).
2. In Cowork's left sidebar: **Customize → Plugins → "+" → Upload**.
3. Select the ZIP. The plugin installs and `cowork-onboarding` becomes available.

After installation by either path, kick things off with: "set up Cowork" or "onboard me".

---

## Reference Files

Each skill includes reference files that provide domain knowledge:

**Onboarding references:**
- `workspace-guide.md` — Folder structure and permission models
- `context-file-guide.md` — Writing effective context files
- `global-instructions-guide.md` — CLAUDE.md configuration
- `connectors-guide.md` — Tool connections and integrations
- `skills-guide.md` — Discovering and using skills
- `scheduled-tasks-guide.md` — Automation and maintenance tasks
- `security-guide.md` — Security review and best practices
- `use-cases-guide.md` — Getting started examples
- `templates-seed-guide.md` — Starter template catalog

**Self-assessment references:**
- `question-bank.md` — 195-question bank across 18 industries
- `scoring-guide.md` — Impact-Effort scoring methodology
- `report-template.md` — Assessment report output format

---

## Version History

- **3.1.1** — Compliance release. Removes schema-rejecting fields (`displayName` in `plugin.json`; `version:` in skill frontmatter), trims `cowork-onboarding`'s description under the 1024-char cap, and adds `scripts/validate.sh` so the same regression can't ship again.
- **3.1.0** — Adds Voice of Customer as the fourth core context file. Onboarding captures buyer language with a 10-question interview and writes `CONTEXT/voc.md`. Prime loads VOC in Tier 1 with 90-day staleness reporting. Self-assessment requires context before running and produces an expanded Skill Blueprint (Buyback Rate, Define-Outcome rubric, validation plan, two-week measurement plan). Reference guides updated for the four-file model.
- **3.0.0** — Major overhaul. Renamed from `cowork-onboarding` to `build-with-ai`. Added self-assessment skill, prime skill, template seeding, permission models, drift detection, live plugin discovery, and two-stage entry point routing.
- **2.2.0** — Previous release as `cowork-onboarding`.

## Validation

Before publishing, `scripts/validate.sh` checks:

- `.claude-plugin/plugin.json` parses, declares a kebab-case `name`, and uses only fields in the published Claude plugin schema.
- Every `skills/*/SKILL.md` has YAML frontmatter with exactly `name` and `description`, a kebab-case name matching its parent directory, and a description ≤1024 characters with no XML tags.
- `.claude-plugin/` contains nothing other than `plugin.json`.

Run it directly with `./scripts/validate.sh` (exits non-zero on first violation). `scripts/release.sh` calls it before building the zip, so a tree that would be rejected by Cowork can't be packaged.

## Releases

To cut a new release once a version is tagged:

```bash
./scripts/release.sh v3.2.0   # replace with the tag you just pushed
```

The script verifies the tag, confirms `.claude-plugin/plugin.json` matches the version, builds `buildwithai-plugin-vX.Y.Z.zip` from the tagged ref via `git archive`, extracts the matching `CHANGELOG.md` section as the release body, and publishes via `gh release create` (or refreshes the asset if the release already exists).

Requires the `gh` CLI authenticated against `ReturnMyTime`. The generated ZIP is left in the repo root so it can be uploaded to Skool directly.
