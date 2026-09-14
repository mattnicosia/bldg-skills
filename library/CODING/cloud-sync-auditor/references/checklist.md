# Cloud Sync Audit Checklist

Use this as a living checklist while reviewing a codebase. Mark each item.

## Architecture Mapping
- [ ] All sources of truth identified (IDB stores, Supabase tables, Storage buckets, in-memory)
- [ ] Write paths diagrammed (local-first? cloud-first? hybrid?)
- [ ] Single sync engine / queue exists (or multiple uncoordinated writers)
- [ ] Conflict resolution strategy documented and implemented (LWW, CRDT, OT, manual, none)

## Data Loss Vectors
- [ ] Every mutation sets a dirty / version / updated_at correctly
- [ ] Deletes produce tombstones that are synced both ways
- [ ] Partial updates never drop fields
- [ ] Blobs have atomic reference + upload (or compensating transaction)
- [ ] Offline edits survive full re-pull on reconnect
- [ ] Multi-tab coordination present (BroadcastChannel / locks / leader)
- [ ] Deduplication keys are stable and collision-resistant
- [ ] No "if not found, delete local" without checking soft-delete or RLS

## Concurrency & Races
- [ ] Sync loop is re-entrant safe (mutex or queue)
- [ ] Realtime + local write has version or sequence guard
- [ ] Critical multi-row updates use IDB transactions
- [ ] "One active X per Y" invariants are enforced with proper locking or unique constraints + retry
- [ ] Unawaited promises or fire-and-forget mutations are flagged

## Persistence Reliability
- [ ] IndexedDB upgrade paths never drop data (or have migration + backup)
- [ ] Transactions have proper abort / cleanup on error
- [ ] beforeunload / visibilitychange flushes pending work
- [ ] Failed sync items stay in queue with backoff + max retries + dead-letter
- [ ] No silent drop of queue on auth change or page reload

## Backend / Supabase Specific
- [ ] RLS policies do not create "disappearing rows" that look like deletes
- [ ] Realtime subscriptions re-establish with catch-up query (since last sequence)
- [ ] Storage paths and table metadata stay in sync (or have cleanup job)
- [ ] Auth refresh does not kill in-flight syncs
- [ ] Server has conflict columns or triggers for last-write-wins if used

## Major Bugs
- [ ] No unhandled promise rejections in sync paths
- [ ] No null/undefined crashes on optional nested objects during merge
- [ ] No infinite reconcile loops
- [ ] Realtime channels are always unsubscribed on unmount / logout
- [ ] Large result sets are paginated / cursor-based

## Inefficiencies
- [ ] No full re-sync of entire project/org on every reconnect
- [ ] Realtime used instead of (or in addition to) polling
- [ ] Blobs not stored as large JSONB columns
- [ ] Indexes exist on (org_id, project_id, updated_at, dirty, deleted_at)
- [ ] Sync does not recompute expensive hashes / validations on every run
- [ ] Memory: no unbounded growth of channels, listeners, or cached full tables

## Test Coverage
- [ ] Multi-device concurrent edit tests exist
- [ ] Offline → online transition tests
- [ ] Multi-tab tests
- [ ] Network failure mid-sync tests
- [ ] Crash / reload mid-write tests
- [ ] RLS change / permission revocation tests
