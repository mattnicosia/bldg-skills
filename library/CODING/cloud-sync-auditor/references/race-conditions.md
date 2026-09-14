# Race Conditions That Cause Silent Data Loss

## Classic Multi-Writer Races

### 1. Local write vs Realtime update
```
Tab A: read → mutate → write local + push
Realtime: receives remote update for same row → overwrites local before push finishes
```
**Fix pattern**: version check or "if my local version > remote, ignore and re-push".

### 2. Two devices offline edit, then both reconnect
Without vector clocks or CRDTs the second reconnect overwrites the first.

### 3. Multi-tab same origin
IndexedDB is shared but transactions from different tabs can interleave. No automatic serialisation across tabs for complex multi-row updates.

### 4. Optimistic UI + background sync queue
UI commits, queue is async; if user navigates away or another mutation arrives before queue flushes, state diverges.

### 5. "One active estimate" invariant
```
// pseudo
const existing = await getActive(projectId)
if (existing) await delete(existing)
await insert(newOne)
```
Between the get and the delete another tab can insert, violating the invariant or causing double-delete.

## Detection Heuristics

- Any `await getX(); await mutateY()` without a transaction or version compare.
- Realtime listener that does `setState(payload.new)` without checking local dirty or version.
- Sync loop that is not guarded by a mutex / "isSyncing" flag + queue.
- Use of `Date.now()` or client-generated UUIDs as sole conflict resolver.
- Absence of `SELECT ... FOR UPDATE` (or equivalent optimistic lock) on critical rows.
- React state updates that are not derived from a single source of truth (multiple useState that both write to IDB).

## Reproduction Recipes (always include in findings)

1. Open two browsers / two devices, both offline, edit same field, go online in different order.
2. Open two tabs, both edit, hard-refresh one while the other is mid-sync.
3. Throttle network to 3G, trigger sync, then immediately edit again.
4. Kill the tab mid-transaction (DevTools → Application → clear storage mid-write).
5. Simulate Supabase realtime disconnect (DevTools offline + re-online) while local queue has pending items.
