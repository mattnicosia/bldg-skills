# Persona Simulation — Lightweight Adversarial Review

When the full 26-agent adversarial workflow is impossible (degraded conditions —
no web search, model can't spawn subagents, tool restrictions), persona simulation
is the fallback. It is weaker than the full protocol but stronger than a single
judge scoring alone.

## When to use

- Web search unavailable, subagent spawning blocked
- Quick pressure test before committing to a full adversarial run
- Evaluating how a known audience would receive the concept (name, pitch, demo)

## How to run

1. **Pick 2-3 personas** who would have strong, distinct reactions to the concept.
   - Industry evaluators (e.g. "This Week in AI" hosts, Product Hunt reviewers)
   - The target ICP (the actual buyer, speaking in their own words)
   - A skeptical competitor (someone who'd benefit from the concept failing)

2. **For each persona, simulate their full reaction.** Not a score, a VOICE.
   - What would they notice first? What would confuse them?
   - What would they praise? What would they dismiss?
   - What question would they ask that the founder hasn't answered yet?
   - Would they use the product? Would they tell someone about it?

3. **Extract the blind spots.** After all personas have spoken:
   - What did ALL of them flag? (highest priority fix)
   - What did one catch that the others missed? (blind spot you wouldn't have found alone)
   - What did none of them question that SHOULD be questioned? (the shared assumption)

4. **Apply findings to the concept.** Adjust the pitch, name, scope, or demo based on
   what the personas surfaced. This is the output — not a score, but actionable changes.

## What this does NOT replace

- Live web search for competitor discovery (no persona can substitute for ground truth)
- Full adversarial scoring (personas are subjective impressions, not dimension-level scoring)
- Legal/trademark review (personas can flag obvious collisions, not legal risk)

## Session precedent

2026-07-16 FLEET-1 session: Web search and X search were both dead while scoring
a BLDG self-assessment. Persona simulation of "This Week in AI" hosts (Andrew and Corey)
surfaced three blind spots: (1) the maintenance risk of adapter drift matching the
Printing Press pizza demo problem, (2) the "is this a feature or a product" question
that forced the subscription model to shift from migration to continuous sync, and
(3) the name-level critique that killed STARPORT and led to FLEET-1. The follow-up
pressure-test with the same personas (critical eye mode) then surfaced the demo-gap
problem: a sci-fi name on a migration script feels like overreach, requiring the
product to match the name's ambition.
