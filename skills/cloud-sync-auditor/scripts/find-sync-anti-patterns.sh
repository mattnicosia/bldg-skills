#!/usr/bin/env bash
# Quick scanner for common cloud-sync / data-loss anti-patterns.
# Usage: ./find-sync-anti-patterns.sh [path-to-src]
# Requires: rg (ripgrep)

set -euo pipefail

ROOT="${1:-.}"

echo "=== Cloud Sync Anti-Pattern Scanner ==="
echo "Root: $ROOT"
echo

echo "--- 1. Client-side timestamps / LWW without version ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  'updated_at\s*[:=]\s*(Date\.now|new Date|now\(\)|timestamp)' \
  "$ROOT" || true
echo

echo "--- 2. Potential incomplete dirty flag handling ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(dirty|isDirty|needsSync|pendingSync|needs_sync)\s*[:=]' \
  "$ROOT" || true
echo

echo "--- 3. Soft / hard deletes ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(softDelete|soft_delete|deleted_at|is_deleted|tombstone|hardDelete|hard_delete)' \
  "$ROOT" || true
echo

echo "--- 4. Realtime channels (check for unsubscribe) ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(\.channel\(|postgres_changes|realtime|supabase\.channel)' \
  "$ROOT" || true
echo

echo "--- 5. IndexedDB / idb usage ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(indexedDB|idb|openDB|transaction\(|objectStore)' \
  "$ROOT" || true
echo

echo "--- 6. Upserts / updates that may be partial ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(\.upsert\(|\.update\(|Object\.assign|\.\.\.\s*\w+Partial)' \
  "$ROOT" || true
echo

echo "--- 7. Multi-tab coordination (or lack) ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(BroadcastChannel|navigator\.locks|SharedWorker|multi.?tab|leader.?election)' \
  "$ROOT" || true
echo

echo "--- 8. Potential fire-and-forget / unawaited ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(void\s+\w+\(|\.then\(|catch\(\s*\(\)\s*=>\s*\{\s*\}\s*\))' \
  "$ROOT" || true
echo

echo "--- 9. Dedup / one-active patterns ---"
rg -n --type-add 'web:*.{ts,tsx,js,jsx}' -t web \
  '(dedup|one.?active|is_active|active.?estimate|unique.*project)' \
  "$ROOT" || true
echo

echo "=== Scan complete. Review hits manually for context. ==="
