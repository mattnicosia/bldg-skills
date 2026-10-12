// The stage map: each method's own stages, in order, and the shared stage each
// one sits under. The shared stages are pstack's six. A new method adds its
// entries here and its object in methods/.

import type { MethodId, SharedId } from '../types'
import { C } from './draw'

export const SHARED: { id: SharedId; name: string; color: string }[] = [
  { id: 'understand', name: 'Understand', color: C.blue },
  { id: 'design', name: 'Design', color: C.indigo },
  { id: 'build', name: 'Build', color: C.orange },
  { id: 'verify', name: 'Verify', color: C.green },
  { id: 'ship', name: 'Ship', color: C.teal },
  { id: 'overnight', name: 'Overnight', color: C.pink },
]

export const STAGE_MAP: Record<MethodId, { stage: string; name: string; shared: SharedId }[]> = {
  pstack: SHARED.map(s => ({ stage: s.id, name: s.name, shared: s.id })),
  pocock: [
    { stage: 'grill', name: 'Grill', shared: 'understand' },
    { stage: 'spec', name: 'Spec', shared: 'design' },
    { stage: 'tickets', name: 'Tickets', shared: 'design' },
    { stage: 'build', name: 'Build', shared: 'build' },
    { stage: 'review', name: 'Review', shared: 'verify' },
    { stage: 'pr', name: 'PR', shared: 'ship' },
    { stage: 'retro', name: 'Retro', shared: 'overnight' },
  ],
}

export const sharedOf = (m: MethodId, stage: string | null): SharedId | null => (stage === null ? null : (STAGE_MAP[m].find(e => e.stage === stage)?.shared ?? null))

// The method's first own stage under a shared one: entering Design moves pocock to Spec.
export const ownOf = (m: MethodId, shared: SharedId): string | null => STAGE_MAP[m].find(e => e.shared === shared)?.stage ?? null

export const sharedIndex = (id: SharedId | null) => SHARED.findIndex(s => s.id === id)
