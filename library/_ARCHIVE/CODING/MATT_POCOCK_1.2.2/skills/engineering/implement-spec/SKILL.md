---
name: implement-spec
description: Implement an entire spec's worth of tickets concurrently as a single PR, by treating the tickets as a task graph and running the frontier — every ticket whose blockers are done — in parallel implementer subagents, each in its own git worktree. Use when the user wants to implement a whole spec or ticket set (not just one ticket), says "implement this spec", "build out these tickets", "run the implementation", or points at output from /to-tickets or /wayfinder and wants it built end to end. For a single ticket or a small piece of work, use /implement instead — this skill is for the multi-ticket, maximum-concurrency case.
disable-model-invocation: true
---

# Implement Spec

Take a spec and its tickets — a **task graph** with blocking edges, not a checklist — and land the whole thing as a single PR, running as many unblocked tickets in parallel as the graph allows.

This assumes an environment with background tasks and subagents (Claude Code). If you're in a chat-only environment without those, fall back to `/implement` and work the frontier one ticket at a time yourself instead of spawning subagents.

The issue tracker should have been provided to you — run `/setup-matt-pocock-skills` if not. This skill consumes tickets in the shape `/to-tickets` or `/wayfinder` produce: each ticket declares what it's **blocked by**, and the **frontier** is every ticket whose blockers are all closed/checked.

Communication to and from subagents should be sparse. Point at the spec, the ticket, research notes, and prior commits rather than restating their contents — subagents should read the pointers, not receive a summary of them.

## Steps

### 1. Read the graph

Read the spec and every ticket. Don't just skim titles — understand the full blocking structure so you know the frontier now and can predict how it opens up as tickets close.

### 2. Explore (optional)

If the tickets need codebase or external-doc context that isn't already captured, run an **exploration subagent** first. It should write its findings as markdown to a scratch location outside the repo (e.g. `.scratch/<feature-slug>/research/`) that every future subagent can read, so implementer subagents spend their context on implementation, not rediscovery.

### 3. Open the branch and draft PR

Create a feature branch and a draft PR. Reference the spec and every ticket in the PR body so the PR is the thing that closes them all.

### 4. Work the frontier

For every ticket currently in the frontier (unblocked, not done, unclaimed):

- Launch an **implementer subagent** in its own git worktree, on its own branch cut from the PR branch.
- Point it at the spec, its ticket, and the research notes from step 2 — don't re-explain them.
- Tell it to use `/tdd` where the ticket has pre-agreed seams, same as `/implement` would.
- Run these in the background, in parallel, for maximum concurrency.

### 5. Merge as tickets land

When an implementer subagent finishes, hand its branch to a **merger subagent** to merge into the PR branch. Resolve conflicts there, not in the implementer's worktree.

Each merge can change the frontier — check for newly-unblocked tickets and immediately kick off implementer subagents for them. Keep the pipeline full: don't wait for every in-flight ticket to land before starting the next batch.

Update ticket status (close it / check it off, per whichever tracker `/setup-matt-pocock-skills` configured) as each merges, so the frontier calculation stays accurate for anyone else watching the graph.

### 6. Wide refactors

If a ticket is a wide refactor (expand–contract, per `/to-tickets`), respect its batch sequencing — its batches are still separate tickets in the graph, but don't parallelize batches that share the same blast radius even if the graph doesn't force an edge between them. Green is only promised at the integrate-and-verify ticket.

### 7. Review and fix

Once the graph is fully closed, run `/code-review` on the PR branch against the branch point. Fix everything it raises in a single implementer subagent — don't fan this back out across the graph.

### 8. Finish

Mark the PR ready for review. Clean up every implementer subagent's worktree.
