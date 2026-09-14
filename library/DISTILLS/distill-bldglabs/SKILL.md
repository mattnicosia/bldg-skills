---
name: distill-bldglabs
description: "Distill content for BLDG Labs strategy."
---

# Distill BLDG Labs

Wrapper for `distill-strategy` preset to the BLDG Labs domain.

## Parameters (preset)

- **VAULT_PATH:** `/Users/mattnicosia/matt-vault-v2`
- **INTAKE_LOG:** `07 Sources/BLDG Labs Strategy Intake.md`
- **STRATEGY_NOTES:** `02 Concepts/BLDG Labs Strategy Notes.md`
- **DOMAIN_LABEL:** BLDG Labs
- **STRATEGIC_LENS:** What's strategically actionable for BLDG Labs (AI for contractors: BLDG Capture, BLDG Arrival, AI employees/managed seats, NOVATerra, BLDG OS, BLDG 4D, Vision CRM, BLDG Access) — positioning, pricing, GTM, competitive landscape, product sequencing, model economics (e.g. Grok 4.5 vs Fable), AI/construction tech trends, or CI on construction software (Outbuild, Contractor OS, etc.).
- **THREAD_SECTIONS:** Positioning/ICP, Pricing/packaging, GTM/distribution, Competitive landscape, New offering ideas, Product sequencing, Content/marketing strategy, Contradictions/open tensions
- **OFFER_ASSESSMENT:** `02 Concepts/BLDG Labs Offer Assessment.md` — the decision engine for which candidate offers to build next. Check after each distillation to see if new signal changes any scores or priorities.
- **PRODUCT_PORTFOLIO:** `references/bldg-labs-product-portfolio.md` — authoritative description of every BLDG Labs product/service and its current state. Load this before scoring any product for monetization or build priority. Incorrect product understanding (e.g. confusing BLDG Capture with a lead gen widget, or listing Datalab as a BLDG Labs product) invalidates every recommendation that follows.

## Scoring methodology — two axes, not one

When Matt asks for product rankings, score on two separate axes. Never combine into a single score:

1. **Immediate recurring revenue** (1-100): How fast can this generate real recurring dollars with minimal new build? Weighs speed-to-dollar and current product readiness.
2. **Big-picture potential** (1-100): Can this scale to tens/hundreds of millions without Matt's time as the bottleneck? Weighs TAM, software scalability, and defensibility.

Present as two separate lists, not one combined ranking. Combined scores obscure the trade-off between "this makes money next week" and "this makes $100M in five years."

## Current-state verification (critical pitfall)

Before scoring any product for monetization:
- Load `references/bldg-labs-product-portfolio.md` to verify what each product actually is and its current state.
- A product that is buggy, losing data, or has zero paid users belongs at the BOTTOM of both lists — regardless of theoretical strategic fit.
- If NOVATERRA is buggy: "stabilize first, monetize last." Do not score it based on what it could become.
- If Matt says "X is not ready" or "X is buggy," remove it from monetization consideration. Don't re-rank it hoping for a different result.

## Execution

Load the general engine skill (`distill-strategy`) and apply the parameters above. All distillation logic lives in the engine — this file only sets domain-specific config.

**Content byproduct:** every successful distill must run step 5 in `distill-strategy` (emit 0–2 rows into `05 Operating/Content Seeds.md`). Prefer content pillars Shift / Edge / Build for Labs signals. Amber Hourly Pulse (`deliver: slack:C0BFTQHEUQ1`) mines that queue. Prefer construction/ops/offer angles — not meta posts about how AMBER works, unless the distill is explicitly about contractor content ops.

## Reference files

- `references/bldg-labs-product-portfolio.md` — authoritative description of every BLDG Labs product/service and its current state. Load before scoring any product. Includes Arrival (not SiteWork) and AI employee seats.
- `references/degraded-sources-research.md` — fallback research when branded web tools are unavailable. Prefer raw HTTP via terminal/execute_code; for papers use Crossref / Semantic Scholar / arXiv APIs. Do not encode transient tooling outages as permanent constraints.
- AI-employee productization (roles, pricing, autonomy gates, character) → class skill `bldg-ai-employees`.
