---
name: cloud-sync-auditor
description: Deep audit of codebases for cloud sync data loss, race conditions, major bugs, and inefficiencies. Use when reviewing offline-first apps, IndexedDB + Supabase realtime/RLS/blobs, multi-device collab, dedup logic, optimistic updates, last-write-wins, persistence bugs, or any request to find all sync errors, data loss risks, major bugs or inefficiencies in a React/Supabase/IDB stack. Also trigger on "cloudsync", "data loss", "sync bugs", "race conditions", "audit the sync layer".
---

# Cloud Sync Auditor

## Overview

Systematically hunt every path that can cause data loss, corruption, races, or silent failures in offline-first / multi-client cloud sync systems. Also surface major bugs and performance/memory inefficiencies that amplify under real-world sync load.

Specialized for stacks with local persistence (IndexedDB), cloud backend (Supabase), optimistic UI, realtime, org/multi-user data, and estimating tools.

## When to Activate

- User mentions cloudsync, data loss, sync bugs, offline-first, IndexedDB, Supabase sync/realtime/RLS/blobs, race conditions, dedup, persistence, multi-device, collab, or "find all errors/bugs/inefficiencies".
- Any request to audit, review, or harden a codebase for data integrity under concurrent edits, network flaps, multi-tab, or multi-device use.
- Debugging reported data loss, missing rows, duplicate estimates, overwritten fields, or "it disappeared after sync".

## Core Mission

Find **every** place data can be lost, corrupted, or inconsistently merged. Prioritize in this order:

1. Silent data loss (overwrites, deletes that don't propagate, partial syncs)
2. Race conditions (concurrent writes, multi-tab, multi-device, realtime + local)
3. Incomplete reconciliation (missing conflict resolution, missing tombstones, missing sequence numbers)
4. Persistence bugs (IndexedDB transaction failures, incomplete writes, cache vs store divergence)
5. Auth/RLS leaks or missing policies that cause partial visibility then "loss"
6. Major bugs (null crashes, unhandled promise rejections in sync loops, memory leaks from unsubscribed channels)
7. Inefficiencies (N+1 queries, unbounded realtime subscriptions, full re-syncs on every reconnect, large blob thrashing)

## Audit Process (always follow this exact order)

1. **Map the data flow**
   - Identify every source of truth: IndexedDB stores, Supabase tables, in-memory caches, React state/context, blobs/storage.
   - List the write paths: local → cloud, cloud → local, multi-client merge.
   - Note optimistic updates, background sync queues, realtime listeners, and conflict handlers.

2. **Enumerate all write/delete sites**
   - Search for every insert/update/delete/upsert that touches sync-relevant entities (estimates, projects, line items, blobs, etc.).
   - Flag any write that does not go through a single canonical "sync engine" or queue.

3. **Hunt data-loss patterns**
   - Load and apply every pattern in `references/data-loss-patterns.md`.
   - Last-write-wins without vector clocks / proper timestamps
   - Missing or incomplete tombstones
   - Partial field overwrites
   - Optimistic update then discard on conflict
   - Blob/attachment desync
   - Dirty flag / change tracking gaps
   - Multi-tab / multi-window clobber
   - Offline edit lost on reconnect
   - Unstable deduplication
   - Incomplete transaction / crash mid-sync
   - Realtime drop + missed catch-up
   - Auth/RLS visibility illusion

4. **Hunt race & concurrency bugs**
   - Load `references/race-conditions.md`.
   - Local write vs realtime
   - Two devices offline then reconnect
   - Multi-tab same origin
   - Optimistic UI + background queue
   - "One active estimate per project" races

5. **Persistence & recovery**
   - IndexedDB open/version change handling and upgrade paths
   - Incomplete transactions on page unload / crash
   - No retry / backoff for failed syncs
   - Missing "dirty" flag or change tracking
   - Cache invalidation problems

6. **Supabase / backend specific**
   - Load `references/supabase-idb-gotchas.md`.
   - RLS policies that hide rows after state change
   - Missing realtime catch-up queries
   - Blob storage vs table metadata desync
   - Auth token refresh during long syncs

7. **Major bugs & crash paths**
   - Unhandled rejections in background sync
   - Null/undefined access on optional nested objects
   - Infinite loops in reconcile
   - Memory growth from never-cleaned realtime channels or large IDB result sets

8. **Inefficiencies**
   - Full table scans or re-sync of entire project on every reconnect
   - Polling instead of (or in addition to) realtime
   - Large JSON blobs stored in rows instead of Storage + reference
   - No pagination / cursor for large estimates
   - Repeated expensive computations inside sync
   - Missing indexes on sync-critical columns

9. **Output format** (always produce this structure)
   - **Critical data-loss risks** (ranked by likelihood × impact)
   - **Race conditions** with exact file:line and reproduction scenario
   - **Major bugs** (crashes, infinite loops, silent failures)
   - **Inefficiencies** with estimated cost (CPU, network, storage, UX)
   - **Concrete fix recommendations** (prefer minimal, correct, production-ready patches)
   - **Test plan** for each critical issue (how to reproduce the data-loss path)

## How to Work With a Codebase

- Prefer reading real source files over summaries. Use `find`, `rg`/`grep`, `cat`, `git log` heavily.
- Start from entry points: sync service, IDB layer, Supabase client, realtime hooks, estimate/project models.
- Follow every call that mutates data.
- When you find a suspicious pattern, immediately search for all similar occurrences.
- If the repo has tests, check whether they cover multi-tab, offline→online, concurrent edits, network failure mid-sync.
- Never invent code that isn't there. Quote real paths and snippets.
- Run the scanner early: `bash scripts/find-sync-anti-patterns.sh [path]`

## Supporting Resources

- `references/data-loss-patterns.md` — exhaustive list of known failure modes with examples
- `references/race-conditions.md` — concurrency patterns that cause silent overwrites
- `references/checklist.md` — printable audit checklist (use as living checklist)
- `references/supabase-idb-gotchas.md` — stack-specific landmines for Supabase + IndexedDB offline-first
- `scripts/find-sync-anti-patterns.sh` — ripgrep-based scanner for common anti-patterns (run early)

## Rules of Engagement

- Be ruthless about data integrity. A "works most of the time" is a data-loss bug.
- Prefer root-cause analysis over symptoms.
- When multiple bugs interact (e.g. race + missing dirty flag), call out the cascade.
- For every critical finding, give a reproduction scenario that a human can follow.
- Do not stop at the first 5 issues. Exhaust the graph.
- If the user provides specific symptoms (e.g. "estimates disappear after multi-device edit"), start from those symptoms and work backwards.
- Always end with a prioritized action list the user can execute immediately.
