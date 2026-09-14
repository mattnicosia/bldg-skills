# Multi-Agent Debate — pressure-testing technique

A reusable pattern for stress-testing business models, product concepts, or strategic
decisions. Spawn 3 subagents in parallel with opposing roles, then synthesize the debate.

## When to use

- Pressure-testing a business model before committing resources
- Iterating a concept toward a target score (e.g., "get to 90")
- Finding blind spots that a single analyst would miss
- The founder says "pressure test this" or "I need to be sure"

## The three roles

| Role | Assignment | What they produce |
|---|---|---|
| **Defender** | Defend the concept against any attack | Strongest possible defense, addresses all identified concerns head-on, score 1-100 |
| **Attacker** | Destroy the concept | Ruthless attack on every assumption, every broken number, every fantasy. Score 1-100 |
| **Blind-spot hunter** | Find what neither will see | Unquestioned assumptions, risks not listed, structural market problems, the biggest unstated bet. Score 1-100 |

## Execution

1. Write a comprehensive brief covering: the concept, the model, the founder, economics, known concerns, and the case for the model.
2. Spawn 3 subagents via `delegate_task` with `tasks=[]` (batch mode). Each gets the full brief + their role assignment.
3. All three run in parallel. Synthesize when they finish.
4. Identify: where they agree, where they disagree, what the attacker found that the defender couldn't dismiss, what the blind-spot hunter found that neither saw.
5. Iterate the model to address the strongest critiques. Re-score.
6. Repeat if the new score still doesn't clear the target.

## Example: BLDG Verify pressure test (2026-07-15)

- Defender score: 82
- Attacker score: 28
- Blind-spot hunter score: 31

Average: 47. The concept at 90 was too fragile. The attacker found the conflict of
interest (Matt's estimating firm competes with estimators being tested). The blind-spot
hunter found the biggest unstated bet: the assessment doesn't need to be valid, just
look credible. Both forced changes that pushed the model from 72 to 95.

## Pitfall

The subagent model inherits from the parent. For maximum rigor, use the strongest
available model (Claude Sonnet 4.6 via Anthropic API direct call if Claude Code is
unavailable). DeepSeek v4 is adequate for the debate structure but less sharp on
domain-specific blind spots.
