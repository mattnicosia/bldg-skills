# Supabase + IndexedDB Offline-First Gotchas

## IndexedDB
- Version upgrades that change objectStore schemas without careful migration drop data.
- Transactions are auto-committed; long-running work that includes network will abort if you try to keep the transaction open.
- Multi-tab: the "versionchange" event can fire and block other tabs. Always handle `blocked` and `versionchange`.
- Large blobs in IDB can hit quota or become very slow; prefer storing only metadata + use Cache API or OPFS for files.
- `idb` library (or raw) – always use explicit transactions for multi-put/delete that must be atomic.

## Supabase Realtime
- `postgres_changes` does not replay missed events. On reconnect you MUST do a catch-up query using `updated_at > last_seen` or a sequence column.
- Filters on realtime are client-side; heavy filters still receive everything then discard.
- Channel leaks: every `.channel()` that is not `.unsubscribe()` will keep the WebSocket open and accumulate.
- Auth: when the JWT refreshes, existing channels may need re-subscribe or they silently stop receiving.

## Supabase Storage + Table Metadata
- Upload succeeds → write path to table fails = orphaned file (cost + ghost).
- Table row written with path → upload fails = dangling reference (broken image).
- Always do upload first (or use a temp path + rename), then write the row, and have a cleanup job for orphans.
- Signed URLs expire; never store long-lived signed URLs in IDB.

## RLS + Soft Deletes
- Common bug: RLS policy has `deleted_at IS NULL` so soft-deleted rows disappear from SELECT. Client interprets missing row as "remote deleted it" and hard-deletes local copy → permanent loss if the soft-delete was temporary or a mistake.
- Better: RLS allows seeing soft-deleted rows for a grace period, or use a separate tombstone table that is always visible to the org.

## Optimistic + Realtime + IDB
- The classic triple race:
  1. Local optimistic write to IDB + React state
  2. Realtime arrives for same row (from another client)
  3. Your own push arrives late
- Without a version / vector clock / "pending local version" the last one to land wins arbitrarily.

## "One Active Estimate per Project" Pattern
- Extremely common in estimating tools. Easy to get races where two actives appear or the wrong one is deleted.
- Server-side unique partial index (`WHERE is_active = true`) + client retry is safer than pure client enforcement.
- When promoting a new estimate to active, use a transaction or a Postgres function that demotes the old one atomically.

## Common Anti-Patterns Found in Real Codebases
- `await supabase.from('x').upsert(localRow)` without first checking if localRow is still the latest dirty version.
- Clearing the entire IDB store on logout instead of soft-clearing only the current org.
- Using `Date.now()` as version instead of a server-generated `updated_at` or a proper sequence.
- Storing full estimate JSON (thousands of line items) as a single JSONB column and re-uploading the whole thing on every change.
- No dead-letter queue; after 3 failed pushes the item is just dropped.
