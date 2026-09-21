---
name: keystone-7
description: KEYSTONE-7 idea scoring instrument. Five kill gates, seven weighted dimensions, Resonance timing modifier, Fragility multiplier, and Disruptor Lens. The ruler that powers /idea-score on bldglabs.ai. Trigger on "keystone", "keystone-7", "gauntlet", "rate this idea", "generate ideas", "find opportunities".
---

# KEYSTONE-7

BLDG-tuned idea scoring instrument. Same soul as the live `/idea-score` scorer on
bldglabs.ai: the idea is here to be tested, not validated. Kill first. Never inflate. An
honest empty result beats a flattering full one.

Scores from this skill and scores from the two live web surfaces are the same ruler and
should agree; if you change a number here, change `docs/keystone-7-spec.md` and
`lib/keystone.ts`'s `KS7` export too (the code wins if they ever disagree).

## Disruptor Lens (before gates, before scoring)

Before any dimension is scored, ask one question that changes how Propagation and
Ignition are evaluated:

**Is this product going AROUND middlemen to end users, or selling TO middlemen?**

What a disruptor does: Elon didn't sell better batteries to automakers. He built cars
people wanted so badly that the industry had to follow. Jobs didn't sell a better MP3
player to Best Buy. He built an iPod+iTunes experience that made every other music
device feel broken. Neither sold TO the industry. They went AROUND the industry —
straight to the end user — and let the end user pull the industry toward them.

The answer determines the scoring lens:

**If DISRUPTOR (goes around middlemen to end users):**
- Propagation: Can the end user experience the product in under 60 seconds and share it
  without explanation? Does the artifact manufacture attention? Score 8-10 if the
  product is self-distributing; 5-7 if it spreads with light facilitation; 1-4 if it
  requires a sales call for anyone to experience it. The end user IS the distribution.
- Ignition: Can the founder ignite end-user adoption directly (content, demos, free
  access), or does ignition require signing middlemen first? Score 8-10 if the founder
  can light a match and end users see it immediately; 5-7 if ignition requires seeding
  both sides; 1-4 if an end user cannot touch the product until a middleman approves it.

**If REFORMER (sells TO middlemen):**
- Propagation: Can the middleman experience the product and immediately see how it makes
  them more competitive? Does the product sell itself in a middleman's hands? Score 8-10
  if the middleman becomes the evangelist (one closed middleman opens five more); 5-7 if
  middlemen adopt after seeing peers; 1-4 if each middleman requires a separate sale.
- Ignition: Can a single middleman's adoption cascade to others (network effect within
  the industry), or does each middleman require a separate, linear sale? Score 8-10 if
  the ecosystem pulls the product through middlemen; 5-7 if warm intros accelerate
  adoption; 1-4 if growth is strictly one-at-a-time sales.

**If HYBRID (goes to end users, revenue from middlemen):**
- Propagation: Score through the end-user DISRUPTOR lens — the end user drives
  distribution. Revenue source is irrelevant to the propagation question.
- Ignition: Score the harder side. If end users and middlemen must both exist for
  ignition to work, score the side that's harder to acquire. If the product works
  single-player for end users (they get value without middlemen present), score through
  the DISRUPTOR lens.

This changes nothing about the dimensions, weights, or gates. It sharpens the questions
you ask when scoring two dimensions. A disruptor can still score 2 on Propagation if the
artifact isn't shareable. A reformer can still score 9 if middlemen evangelize.

Record the lens classification (DISRUPTOR / REFORMER / HYBRID) in the output header.

## Run Mode (choose before scoring)

KEYSTONE-7 has two run modes. The DEFAULT is Standard (single judge). The REQUIRED
mode for any self-assessment is Adversarial. Getting this wrong is the most common
failure mode: a single judge, unaided by live search, will overrate a concept its own
author is attached to.

### Standard mode (default)

One judge. Fast. Appropriate for: scoring third-party ideas, quick triage, generate
runs where the concept is brand-new and the judge has no attachment to it.

Rules:
- Read the asset profile. Score every gate and dimension from evidence.
- The normal pitfall: assuming "no competitor" without checking. If any gate or
  dimension hinges on "nobody else is doing this," you MUST run a live web search
  before scoring. Model memory is stale. Do not trust it for competitor claims.

### Adversarial mode (REQUIRED for self-assessments)

The instrument scoring itself, or Matt scoring his own concept. Flattery risk is
maximal. Resist it structurally, not by intention.

Mandatory rules when the concept being scored is BLDG's own:

1. **Live web search is non-negotiable.** Before scoring Incumbent Immunity, Timing,
   or Propagation, run real-time searches for competitors, clones, and adjacent
   products. Model cutoff knowledge is worthless for "is this already done?" gates.
   If search is unavailable, mark Sources as DEGRADED and score Incumbent Immunity
   one point lower than evidence alone suggests, as a penalty for the blind spot.

2. **Adversarial multi-agent workflow.** See `references/adversarial-workflow.md`.
   Spawn independent agents: researchers for competitor discovery, gate skeptics
   instructed to FAIL their assigned gate, two judges per dimension (take the
   LOWER), a resonance judge, a fragility judge, a devil's advocate, and a
   monetization strategist. One judge will flatter. Twenty-six won't.

3. **Take the lower of two judges per dimension.** The scoring discipline that
   prevents inflation. If two judges disagree, the lower score stands. Do not
   average. Do not let an agent do the final multiplication — compute raw,
   effective compression, fragility, and display final deterministically in the
   main loop.

4. **Check git for same-day ruler edits.** If `lib/keystone.ts`, `docs/keystone-7-spec.md`,
   or this skill were edited on the same day as the scoring run, disclose it in the
   output header. Note whether the verdict survives without the edit. The instrument's
   credibility depends on the ruler not being loosened the day it grades the ruler's
   maker. (2026-07-16 precedent: the fragility recalibration and display multiplier
   were shipped the same day as the self-assessment. The verdict survived even the
   loosened rules, which strengthened the honesty claim.)

5. **Honor gate logic.** Any gate FAIL zeroes the final. Report both the gate-verdict
   (which may be zero) and the shadow score (all dimensions scored as if the gate
   passed) for diagnostic altitude. Zero survivors is a valid result.

The adversarial workflow is documented in `references/adversarial-workflow.md`.
The older 3-role debate (`references/debate-technique.md`) is still valid for
non-self-assessment pressure tests but is less rigorous.

## Five Kill Gates (binary, evidence-required, fail any = stop)

1. **Dollar Arrow** — Can someone reach for money without being sold?
2. **Timing Window** — Is now the right time? Evidence required to claim warm/hot.
3. **Incumbent Immunity** — Can incumbents copy this in under 90 days?
4. **Witnessable Proof** — Can you prove it works in under 60 seconds?
5. **Cold-Start Viability** — Can you get the first users without a platform?

## Seven Dimensions (each 0-10, weighted)

| Dimension | Weight |
|-----------|--------|
| Timing & Substrate | 18 |
| Capture | 18 |
| Propagation | 15 |
| Compression | 14 |
| Entrenchment | 10 |
| Ignition & Distribution | 14 |
| Founder-Market Fit | 11 | Scoring tip: credit "incumbent constraint" — when incumbents cannot make the same bet because of architecture, cannibalization risk, or institutional inertia, the founders' willingness to make that bet is itself an unfair advantage. |

**Resonance modifier:** Before weighting, multiply Compression by 0.8 (dormant) / 1.0
(neutral, default) / 1.25 (warm) / 1.5 (hot) based on cited, ~90-day-recent evidence.
Cap effective Compression at 10.

**Fragility multiplier:** Applied to the final weighted score. Only idea-specific
weaknesses: two-sided cold start, regulatory gray zone, 90-day incumbent copyability,
platform dependence, single-channel dependence, fresh-unproven mechanic. BANNED as
fragilities: "solo founder," "no audience yet," "limited budget" — those are founder
constants, not idea fragilities. If the worst weakness is founder-constant, the
multiplier is 1.0. Every fragility line must name WHICH idea-specific weakness drove the
multiplier.

Recalibrated 2026-07-16: a designed, plausible mitigation — even unproven — qualifies
as minor (0.9). Serious (0.75) is reserved for weaknesses where NO mitigation has been
designed. The Cursor test proved that founding concepts with designed mitigations
should not be penalized at the old "serious" default.

## Asset Profile

Read `docs/asset-profile.md` before any run. If missing or stale, say so and fix it
first. Never invent assets.

## Verdict Bands (final, post-fragility)

Recalibrated 2026-07-16 against real founding concepts (Stripe 87→97, iPhone 85→95, ChatGPT 85→95, Google 84→94, Lovable 82→91). A 1.12× display multiplier maps internal scores to a human-intuitive 0-100 scale.

- **91+** — Build now (once-a-decade idea)
- **80-90** — Strong. Build the evidence engine
- **69-79** — Real but missing an engine
- **<69** — Kill or reframe

## Output Format

Header: Classification (DISRUPTOR / REFORMER / HYBRID), Sources (full or degraded), any
degradation notes.

Then: Gates block (each gate: PASS/FAIL with evidence), then score block (all seven
dimensions with named Resonance band and evidence, total, fragility line naming the
specific weakness and multiplier, final score, verdict band).

Zero survivors is a valid, reportable result. Never inflate to fill slots.

## Scoring pitfalls (2026-07-16 FLEET-1 session)

- **Web search unavailable = DEGRADED scoring, not an excuse to skip.** When web search is down (Firecrawl not configured, X rate-limited, credits exhausted), mark Sources as DEGRADED and score Incumbent Immunity one point lower than evidence alone suggests. Do NOT skip the gate or assume "no search = no competitors." The degraded penalty is structural protection against self-assessment inflation.
- **Self-assessment without adversarial mode is invalid.** A single judge scoring its own concept will overrate. Never score BLDG's own ideas in Standard mode. If adversarial agents can't be spawned (model limitations, tool restrictions), use persona simulation (see `references/persona-simulation.md`) as a lightweight alternative. If even that is impossible, say so AND score one full band lower as a penalty.
- **Don't let a single dimension rescue a product with structural flaws.** A 10/10 Founder-Market Fit doesn't compensate for 4/10 Entrenchment. Flag when one dimension is pulling the weighted average above where the weakest dimension belongs.
- **Rescore after spec or architecture changes.** The first FLEET-1 score (concept only) and the second FLEET-1 score (734-line spec) produced the same verdict band (90), but the Entrenchment dimension moved from 8→9 because the spec design made entrenchment structural (fidelity report, adapter pinning, shared-file ownership markers). A major architecture, spec, or design iteration can shift dimension scores even when the concept hasn't changed. After a Fable-level spec or significant technical design, rescore — don't assume the old score still holds. The spec IS the product's first real form.

## Reference files

- `references/calibration-method.md` — How to calibrate KEYSTONE-7 against real founding concepts, with the current calibration set
- `references/calibration.md` — Calibration tests against known outcomes
- `references/debate-technique.md` — 3-role debate pattern for non-self-assessment pressure tests
- `references/adversarial-workflow.md` — Full 26-agent adversarial protocol, REQUIRED for all self-assessments
- `references/persona-simulation.md` — Lightweight adversarial fallback when full agent spawning is impossible (degraded conditions); simulate known evaluator personas to surface blind spots
- `references/public-surface.md` — Architecture of the /idea-score public scorer, shareable URLs, OG image generation, DB schema, and Dossier funnel integration at bldglabs.ai
