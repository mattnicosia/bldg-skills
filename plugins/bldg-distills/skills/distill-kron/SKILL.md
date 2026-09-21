---
name: distill-kron
description: "Distill content for Kron's own improvement — skills to build, patterns to adopt, capabilities to add."
---

# Distill Kron

Wrapper for `distill-strategy` preset for Kron's own self-improvement.

## Parameters (preset)

- **VAULT_PATH:** `/Users/mattnicosia/matt-vault-v2`
- **INTAKE_LOG:** `05 Operating/Kron Strategy Intake.md`
- **STRATEGY_NOTES:** `05 Operating/Kron Strategy Notes.md`
- **DOMAIN_LABEL:** Kron (Chief of Staff)
- **STRATEGIC_LENS:** What should Kron adopt, build, or change to be a better Chief of Staff? Focus on: new Hermes features or capabilities Kron isn't using yet, agent architecture patterns (memory systems, multi-agent coordination, skill design), tooling improvements (new CLIs, MCPs, APIs worth wiring up), workflow patterns other advanced agents use, operational improvements (how Kron manages context, delegates, reports), autonomy gains (things Kron currently asks about but could handle alone), and anything that would make Kron more useful to Matt across ALL his domains (not just BLDG Labs — construction, family, personal, health, finance). The output of this skill is not just vault notes — it's concrete actions: new skills to create, config changes, cron jobs to set up, or behavioral changes to adopt immediately.
- **THREAD_SECTIONS:** New capabilities to add, Agent architecture & patterns, Tooling & integrations, Autonomy improvements, Context & memory management, Multi-agent coordination, Pitfalls & lessons from other builders

## Post-distillation actions (different from other wrappers)

After logging and updating strategy notes, Kron must also:

1. **Flag any immediately actionable improvement** — if the content describes a capability Kron could adopt right now (a new tool, a config change, a skill idea), propose it directly to Matt in the reply. Don't just file it.
2. **Offer to build** — if the content suggests a new skill, cron job, or integration Kron should have, offer to create it. The default answer is "yes, build it" unless Matt says otherwise.
3. **Self-audit** — check whether Kron already has the described capability. If the video says "your agent should be able to X" and Kron can already do X, say so and don't create duplicate work. If Kron can't do X, flag the gap.

## Execution

Load the general engine skill (`distill-strategy`) and apply the parameters above. Then run the post-distillation actions.
