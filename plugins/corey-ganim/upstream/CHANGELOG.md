# Changelog

All notable changes to this plugin are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project adheres to semantic versioning.

## [3.1.1] — 2026-05-08

### Fixed
- Removed `displayName` from `.claude-plugin/plugin.json`. The field is not in the published Claude plugin schema and Cowork's AJV-strict validator rejects unrecognized top-level keys, surfacing as `Plugin validation failed` on upload.
- Removed `version:` from `SKILL.md` frontmatter in `cowork-onboarding`, `self-assessment`, and `prime`. The Anthropic skill schema only allows `name` and `description` keys.
- Trimmed `cowork-onboarding`'s description from 1050 to ~950 characters to fit the 1024-character limit. All primary trigger phrases preserved.

### Added
- `scripts/validate.sh` — pre-release linter that enforces both schemas (`plugin.json` field allowlist; `SKILL.md` frontmatter rules including 1024-char description cap, kebab-case names, no XML tags). Wired into `scripts/release.sh` so a non-compliant tree cannot be packaged.
- Standard metadata fields in `plugin.json`: `$schema`, `homepage`, `repository`, `license`.

### Changed
- `scripts/release.sh` zip prefix is now `build-with-ai-vX.Y.Z/` (matching the plugin's `name`) instead of `buildwithai-plugin/`.

## [3.1.0] — 2026-05-06

### Added
- Voice of Customer (VOC) capture in `cowork-onboarding`: interview branch with 10 questions, output template, source taxonomy, and validation rules. Writes `CONTEXT/voc.md` (or `CONTEXT/voice-of-customer.md`).
- 90-day VOC refresh recommended in scheduled-tasks setup, alongside existing security review and onboarding delta cadence.
- VOC tier-1 load and staleness reporting in `prime`. Reads `voc.md` (or `voice-of-customer.md` alias). Emits a refresh nudge when `Last updated:` is older than 90 days.
- Skill Blueprint fields in `self-assessment` output: Buyback Rate (Annual Revenue ÷ 2,000 ÷ 4), Define-Outcome rubric, validation plan, two-week measurement plan.
- Context-existence guard at `self-assessment` entry. Refuses to run if `CONTEXT/about-me.md` is missing.
- VOC sections in references: `context-file-guide`, `global-instructions-guide`, `workspace-guide`, `use-cases-guide`, `templates-seed-guide`, `scheduled-tasks-guide`.
- `CHANGELOG.md` (this file).
- `.gitignore` covering `.DS_Store`, `node_modules/`, `.env`, log files.

### Changed
- Four-context-file model replaces the three-file model throughout the plugin and all reference guides.
- Plugin description and keywords updated to mention VOC.

## [3.0.0] — 2026-03-11

Major overhaul. Renamed from `cowork-onboarding` to `build-with-ai`. Added self-assessment skill, prime skill, template seeding, permission models, drift detection, live plugin discovery, and two-stage entry point routing.
