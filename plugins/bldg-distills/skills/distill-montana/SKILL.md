---
name: distill-montana
description: "Distill content for Montana Contracting Corp strategy. Load when Matt sends a video, article, or take relevant to his general contracting business."
---

# Distill Montana Contracting

Wrapper for `distill-strategy` preset to the Montana Contracting domain.

## Parameters (preset)

- **VAULT_PATH:** `/Users/mattnicosia/matt-vault-v2`
- **INTAKE_LOG:** `05 Operating/Montana Strategy Intake.md`
- **STRATEGY_NOTES:** `05 Operating/Montana Strategy Notes.md`
- **DOMAIN_LABEL:** Montana Contracting
- **STRATEGIC_LENS:** What's actionable for Montana Contracting Corp — a ~$10M general contractor in Rockland County, NY, now covering both commercial and residential projects (Montana Home Builders projects are completing under MCC). Focus on: estimating and preconstruction process improvements, project management and field operations for both commercial and residential jobs, subcontractor and trade partner management, business development and client relationships, safety and compliance, construction industry trends (material costs, labor market, regulatory changes in NY/NYC metro), technology adoption for GCs, residential construction specifics (client communication, design-build coordination, homeowner expectations), and anything that helps win more profitable work or run existing jobs better. Pay attention to Matt's role (owner/oversight, not day-to-day PM) and anything estimator-relevant that Steve Catalanotto or Pete Kola could use.
- **THREAD_SECTIONS:** Estimating & preconstruction, Project management & field ops, Subcontractor & vendor management, Business development, Residential projects, Safety & compliance, Industry trends & market conditions, Technology & tools for GCs, Contradictions/open tensions

## Execution

Load the general engine skill (`distill-strategy`) and apply the parameters above. All distillation logic lives in the engine — this file only sets domain-specific config.

## First-run note

The intake log and strategy notes files (`Montana Strategy Intake.md`, `Montana Strategy Notes.md`) may not exist yet. If missing, create them from scratch using the Kron equivalents (`Kron Strategy Intake.md`, `Kron Strategy Notes.md`) as format templates. The intake log uses pipe-delimited markdown with columns: Date | Creator/Author | Title | URL | Type | Takeaway | Tags. The strategy notes file uses `### Thread name` sections with `- Current thinking:` bullet points and a `## Contradictions / open tensions` catch-all.

## Reference material

- `references/residential-experience-plays.md` — Battle-tested concrete plays for making homebuilding projects talkable. Survived Matt's pressure test. Load this when synthesizing residential experience ideas or when the conversation turns to "how do we make them talk about us."
