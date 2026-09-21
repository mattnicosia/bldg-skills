# Data Loss Patterns in Cloud Sync Systems

## 1. Last-Write-Wins Without Proper Timestamps / Vectors
- Using `updated_at = now()` on client without server-authoritative clock or version column.
- Two devices edit offline; the one that reconnects second wins even if its edit is older.
- **Detection**: Search for `updated_at`, `last_modified`, upserts that set timestamps client-side without `GREATEST` or version check.

## 2. Missing or Incomplete Tombstones
- Soft delete locally (`deleted_at = now()`) but hard delete on server, or vice versa.
- Delete propagates to one client but not others because no tombstone table or `is_deleted` flag is synced.
- **Detection**: Look for `delete`, `soft_delete`, `trash`, and check if a `deleted_at` or separate `tombstones` table is written and read on every pull.

## 3. Partial Field Overwrites
- PATCH / upsert that sends only changed fields but server or local merge replaces entire row with partial object.
- JSONB merge that drops keys not present in the new payload.
- **Detection**: Search for `Object.assign`, `...spread`, `update({ ...partial })`, Supabase `.update()` without selecting existing first.

## 4. Optimistic Update Then Discard on Conflict
- UI shows local change, then on conflict the entire local change is dropped instead of 3-way merge.
- No "conflict" UI or automatic CRDT-style merge for line items / quantities.
- **Detection**: Look for conflict handlers that simply `return serverVersion` or `setState(server)`.

## 5. Blob / Attachment Desync
- File uploaded to Supabase Storage but the row that holds the path/URL is never written (or written then rolled back).
- Local blob written to IDB, path stored, but upload fails and path is left dangling.
- **Detection**: Search for `storage.from`, `upload`, `createSignedUrl` and the subsequent DB write. Check transaction boundaries.

## 6. Dirty Flag / Change Tracking Gaps
- Entity is edited but `dirty = true` / `needs_sync` is never set (or cleared too early).
- After partial sync, dirty is cleared even though some related entities failed.
- **Detection**: Grep for `dirty`, `isDirty`, `needsSync`, `pending`, `queue`. Trace every mutation site.

## 7. Multi-Tab / Multi-Window Clobber
- Two tabs open same project; both write; last tab to close wins (or IndexedDB transaction order is non-deterministic).
- No BroadcastChannel / SharedWorker / leader election.
- **Detection**: Search for `localStorage`, `BroadcastChannel`, `navigator.locks`, or absence of any multi-tab coordination.

## 8. Offline Edit Lost on Reconnect
- Local version has higher sequence but server has newer wall-clock; server wins and local is discarded without merge.
- No client-side "pending changes" that survive a full re-sync.
- **Detection**: Look at reconnect / onAuthStateChange / online event handlers. Do they call a full `pull()` that overwrites without merge?

## 9. Deduplication That Drops Valid Data
- Dedup key based on unstable hash (e.g. includes random UUID or order-dependent fields).
- "One active estimate per project" enforced by deleting the other instead of merging or archiving.
- **Detection**: Search for `dedup`, `unique`, `one active`, racey ID generation (`crypto.randomUUID` without coordination).

## 10. Incomplete Transaction / Crash Mid-Sync
- Multi-statement IDB transaction that is not atomic with the network call.
- Page unload aborts the transaction; partial state is left.
- **Detection**: Look for `idb.transaction`, `await db.put`, then network call outside the same try/finally. Check for `beforeunload` / `visibilitychange` handlers that flush.

## 11. Realtime Drop + Missed Catch-up
- Realtime channel disconnects; on reconnect only new messages arrive, historical missed events are never pulled.
- No "last sequence" or "since" parameter on re-subscribe.
- **Detection**: Supabase `.channel().on('postgres_changes')` without a subsequent full or delta sync on `SUBSCRIBED` / reconnect.

## 12. Auth / RLS Visibility Illusion
- User loses access (RLS) to a row; client treats missing row as "deleted by someone else" and hard-deletes local copy.
- Or inverse: row is soft-deleted on server but still visible because RLS allows it, then later disappears.
- **Detection**: Check RLS policies for soft-delete filters, and client code that does `if (!row) deleteLocal(id)`.
