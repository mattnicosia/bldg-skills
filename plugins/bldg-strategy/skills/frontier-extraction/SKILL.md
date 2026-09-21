---
name: frontier-extraction
description: Run a structured extraction protocol before a frontier AI model is repriced, deprecated, rate-limited, or pulled from a subscription plan. Converts temporary access to a top-tier model into permanent assets that cheaper models can execute against later. Trigger whenever the user says a model is "leaving," "getting repriced," "being deprecated," "last day with," "sunset," "moving to credits," "extract everything before it's gone," "frontier window," or wants to plan how to spend limited time with a superior model. Also trigger when a NEW frontier model launches with a limited promo window and the user wants an extraction plan for it. This is model-agnostic - it applies to any frontier model, any lab, any year. Do NOT answer these situations with a generic to-do list; run this protocol.
---

# Frontier Extraction Protocol

## Core principle

When a frontier model's access window closes, everything you extracted stays and everything you merely chatted about evaporates. The protocol's single sorting test:

**Can a cheaper model redo this tomorrow?**
- Yes → skip it. Do not spend frontier hours on it.
- No → it belongs in the extraction plan.

What passes the test is always the same category: artifacts that require frontier judgment to CREATE but only ordinary intelligence to USE. Standards. Roadmaps. Distilled knowledge. Self-firing skills. Recorded reasoning.

## Step 0: Situation intake (always do this first)

Before running any extraction move, establish the window:

1. **Which model, and what changes?** (repriced, deprecated, moved off plan, promo ends)
2. **How much time is left?** (hours, days, weeks)
3. **What are the usage limits?** Frontier models often burn plan limits faster than standard models and may have separate caps. Budget accordingly.
4. **What is the successor/fallback model?** Every extracted artifact will be written FOR that model to execute. Name it explicitly in prompts (e.g. "write this so [fallback model] can follow it").
5. **What does the user's current portfolio look like?** Pull from memory/context: active projects, repos, businesses, knowledge vault. Rank by locked-up value.

If time is short, run the moves in this order: **5, 4, 1, 2, 3.** Move 5 compounds passively while everything else runs. Move 4 runs unattended.

## The five moves

### Move 1: Plant the model's judgment in the workspace

The highest-value artifact is a written standard. An answer helps once; a standard upgrades every future answer from every future model.

For each project the user cares about, run in that project:

```
Read this entire project and how I work in it.

Then rewrite my CLAUDE.md as the operating manual a less capable model
([FALLBACK MODEL]) would need to work here at your level:

- the conventions I follow and the ones you'd add
- the mistakes a weaker model will make in this codebase, named,
  with the rule that prevents each
- the quality bar per deliverable, written as CHECKABLE criteria, not adjectives
- what to do when uncertain: exact escalation rules

Then propose the 3 skills that would save me the most hours, and write them in full.
```

Why checkable criteria matter: a cheaper model cannot invent a quality bar, but it applies a written one fine.

Adapt per user: if they use hooks, verifier subagents, memory files, or handoff docs (BRIEF.md etc.), have the frontier model rewrite ALL of that layer, not just CLAUDE.md.

### Move 2: The consultant audit

Point the frontier model's judgment at the business itself. Open a session with maximum context (projects, numbers, offers, workflows, time allocation) and run:

```
Act as the consultant I can't afford.

Audit everything: projects, offers, workflows, pricing, where my time goes.

Deliver a roadmap I can execute with [FALLBACK MODEL]:

- ranked moves, highest expected return first
- per move: why, the exact steps, what done looks like, and what a weaker
  model needs to be told to execute it
- the three things I should stop doing, with the reasoning written out in full
```

The deliverable rule: the REASONING gets written down while the model that can produce it is affordable. Later, the fallback model doesn't need to be brilliant. It needs to follow a brilliant document.

Save the output as a dated roadmap file the user can hand to future sessions.

### Move 3: The second brain run

Spend a slice of the window on research volume: deep research runs on the user's niche, competitors, customers' problems, and methods they've been meaning to study.

Then **atomize, never summarize**: mine every run into the user's knowledge vault (Obsidian or equivalent), one insight per note, notes linked to related notes. A hundred linked one-insight notes get retrieved and reused. A 40-page report gets stored and forgotten.

Note structure per insight:
- One claim or insight as the title
- 2-5 sentences of support
- Source
- Links to related notes
- Tags matching the vault's existing taxonomy

If the user has a vault MCP or file access, write the notes directly. Otherwise output them as a batch of individual markdown files.

### Move 4: Fire the goals (unattended hours)

The thing that actually stops being flat-rate is unattended endurance. Spend it on the 2-3 backlog items with the most locked-up value, not ten.

Use whatever long-horizon mechanism the current tooling offers (goal commands, loops, orchestrated subagent workflows). Structure every run with a finish-line condition:

```
/goal [concrete done-state], with [PROOF PASTED IN CHAT], and a
[CHANGE-NOTES FILE] documenting every change... or stop after [N] turns
and paste the failures.
```

Two safety rules, non-negotiable:
1. **Demand pasted proof in the finish line.** The judge only reads the conversation. It cannot run tests or open files. The condition asks for the green run pasted, never promised.
2. **Cap every run.** Turns or wall-clock, written into the condition. One uncapped unattended loop can burn thousands of dollars or an entire weekly limit overnight.

### Move 5: Install the reasoning recorder (do this FIRST if time is short)

Every hard problem the frontier model cracks, its approach evaporates when the session ends unless a recorder is installed. Create this skill in the user's workspace:

`.claude/skills/extract-approach/SKILL.md`:

```
---
name: extract-approach
description: After solving any non-trivial problem, document the reasoning
approach as a permanent learnings note before moving on.
---

After solving a non-trivial problem, write a learnings note to
learnings/YYYY-MM-DD-[slug].md containing:

- The problem in one sentence
- Why it was hard (what a naive approach misses)
- The approach that worked, as steps a less capable model could follow
- The generalizable rule extracted from this solve
- Files/context touched

Keep it under 40 lines. The rule line is mandatory.
```

Then wire it into CLAUDE.md so it fires without being asked:

```
## learning law
After every non-trivial solved problem, run the extract-approach skill
before moving on. A solution without its learnings note is unfinished work.
```

Then work the frontier model hard on the real backlog. Every solve leaves a note. The notes are the distillate: frontier reasoning sitting in the repo, readable by every model that comes after.

## Output of this skill

When this skill runs, produce for the user:

1. **A window budget**: time left, limits, what fraction goes to each move
2. **A ranked target list**: their specific projects/repos/businesses mapped to moves 1-4, ordered by locked-up value
3. **Ready-to-paste prompts** for each target, with [FALLBACK MODEL] and project names filled in from their actual context
4. **The extract-approach skill file** written out for their workspace
5. **A post-window checklist**: where every artifact lives and how future model sessions should consume it

## Recurrence

This situation repeats. The pattern: a frontier model appears, gets repriced, gets pulled, eventually retires. When the user mentions ANY new frontier window opening or closing, re-run this protocol with Step 0 updated. The protocol is the permanent asset; the model names are parameters.
