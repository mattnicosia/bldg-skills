// The repo at a glance: parsing what git and gh print, and drawing it. The
// pane runs the commands.

import type { PrStage, PullRequest, Repo } from '../types'
import { C, cut, doc, esc, inkOf, MONO, text, W } from './draw'
import { fill, type Act, type AnyMethod } from './method'

export const NO_REPO: Repo = { isRead: false, error: null, name: '', branch: '', dirty: 0, stale: [], worktrees: 0, prs: [], isSetUp: true }

const STALE_DAYS = 14

const ciOf = (checks: { status?: string; conclusion?: string; state?: string }[]): PullRequest['ci'] => {
  if (checks.length === 0) return 'none'
  const bad = new Set(['FAILURE', 'ERROR', 'TIMED_OUT', 'CANCELLED', 'ACTION_REQUIRED'])
  if (checks.some(c => bad.has(c.conclusion ?? '') || bad.has(c.state ?? ''))) return 'fail'
  if (checks.some(c => (c.status && c.status !== 'COMPLETED') || c.state === 'PENDING')) return 'pending'
  return 'pass'
}

// Green checks are one of several gates. A PR is ready to merge only when it is
// out of draft, merges cleanly with main, has passing checks and has no review
// asking for changes. GitHub reports mergeable as UNKNOWN until it has worked
// it out, so that waits rather than counting as clean.
const stageOf = (ci: PullRequest['ci'], isDraft: boolean, mergeable?: string, review?: string): PrStage => {
  if (mergeable === 'CONFLICTING') return 'conflict'
  if (ci === 'fail') return 'fail'
  if (isDraft) return 'draft'
  if (ci === 'pending') return 'running'
  if (review === 'CHANGES_REQUESTED') return 'changes'
  if (mergeable !== 'MERGEABLE') return 'checking'
  return 'ready'
}

export const STAGE_TEXT: Record<PrStage, string> = {
  conflict: 'conflicts with main',
  fail: 'checks failing',
  draft: 'draft',
  running: 'checks running',
  changes: 'changes requested',
  checking: 'GitHub still checking',
  ready: 'ready to merge',
}

// A worktree entry is a `worktree <path>` line, then `branch refs/heads/<name>`.
export const treesOf = (porcelain: string) =>
  porcelain.split('\n\n').map(entry => ({
    path: /^worktree (.+)$/m.exec(entry)?.[1] ?? '',
    branch: /^branch refs\/heads\/(.+)$/m.exec(entry)?.[1] ?? '',
  }))

// Branches merged into the base, or untouched for two weeks. A branch checked
// out in any worktree is someone's live work, never stale.
export const staleOf = (heads: string, merged: string, trees: { branch: string }[], base: string, nowSec: number) => {
  const done = new Set(merged.split('\n').filter(Boolean))
  const inUse = new Set(trees.map(t => t.branch).filter(Boolean))
  const cutoff = nowSec - STALE_DAYS * 86400
  return heads
    .split('\n')
    .filter(Boolean)
    .map(line => {
      const [name = '', when = '0'] = line.split('|')
      return { name, when: Number(when) }
    })
    .filter(h => h.name !== base && !inUse.has(h.name) && (done.has(h.name) || h.when < cutoff))
    .map(h => h.name)
}

export const prsOf = (json: string): PullRequest[] => {
  type Raw = { number: number; title: string; isDraft: boolean; statusCheckRollup?: { status?: string; conclusion?: string; state?: string }[]; mergeable?: string; reviewDecision?: string }
  return (JSON.parse(json) as Raw[]).map(p => {
    const ci = ciOf(p.statusCheckRollup ?? [])
    return { number: p.number, title: p.title, isDraft: p.isDraft, ci, stage: stageOf(ci, p.isDraft, p.mergeable, p.reviewDecision) }
  })
}

// The Start tab's header: the repo at a glance, one tile per kind of open work.
export const startSvg = (r: Repo) => {
  const blocked = r.prs.filter(p => p.stage === 'fail' || p.stage === 'conflict').length
  const ready = r.prs.filter(p => p.stage === 'ready').length
  const running = r.prs.filter(p => p.ci === 'pending').length
  const tiles: { n: number; label: string; note: string; color: string }[] = [
    {
      n: r.prs.length,
      label: r.prs.length === 1 ? 'Open PR' : 'Open PRs',
      note: r.prs.length === 0 ? 'none open' : blocked ? `${blocked} blocked` : ready ? `${ready} ready to merge` : running ? `${running} running` : 'in progress',
      color: r.prs.length === 0 ? C.gray : blocked ? C.red : running ? C.orange : C.green,
    },
    { n: r.dirty, label: 'Uncommitted', note: r.dirty ? 'files changed' : 'clean', color: r.dirty ? C.orange : C.green },
    { n: r.stale.length, label: 'Stale', note: r.stale.length ? 'branches' : 'none', color: r.stale.length ? C.orange : C.green },
    { n: r.worktrees, label: 'Worktrees', note: r.worktrees ? 'others open' : 'just this one', color: r.worktrees ? C.blue : C.gray },
  ]
  const isClean = r.prs.length === 0 && r.dirty === 0 && r.stale.length === 0 && r.worktrees === 0
  let b = ''
  b += text(20, 36, 'h ink', cut(r.name || 'No repo', 26))
  const bw = Math.min(r.branch.length * 7 + 24, 210)
  b += `<rect x="${W - 20 - bw}" y="18" width="${bw}" height="24" rx="12" fill="${C.slate}" fill-opacity=".08"/>`
  b += `<text x="${W - 32}" y="34.5" text-anchor="end" font-size="12" font-family="${MONO}" class="mut">${esc(cut(r.branch, 27))}</text>`
  b += text(20, 58, 'sub mut', isClean ? 'Nothing open. You can start something new.' : 'Finish what is open before starting something new.')
  const tw = (W - 32 - 3 * 8) / 4
  tiles.forEach((t, i) => {
    const x = 16 + i * (tw + 8)
    b += `<rect class="card" x="${x}" y="74" width="${tw}" height="92" rx="12"/>`
    b += `<rect x="${x + 14}" y="86" width="22" height="4" rx="2" fill="${t.color}"/>`
    b += `<text x="${x + 14}" y="118" font-size="32" font-weight="700" fill="${t.n ? inkOf(t.color) : '#AEAEB2'}" letter-spacing="-.02em">${t.n}</text>`
    b += `<text x="${x + 14}" y="140" font-size="12" font-weight="600" class="ink">${esc(t.label)}</text>`
    b += `<circle cx="${x + 18}" cy="154" r="3.5" fill="${t.color}"/>`
    b += `<text x="${x + 26}" y="158" font-size="11" class="mut">${esc(t.note)}</text>`
  })
  return doc(184, b)
}

// One row per piece of open work, each with the buttons that move it on.
export const openWork = (r: Repo, m: AnyMethod, canMerge: boolean): { key: string; label: string; acts: Act[] }[] => [
  ...r.prs.map(pr => ({
    key: `pr-${pr.number}`,
    label: `PR #${pr.number} · ${STAGE_TEXT[pr.stage]} · ${cut(pr.title, 48)}`,
    acts: m.prActs(pr, canMerge),
  })),
  ...(r.dirty > 0
    ? [{
        key: 'dirty',
        label: `${r.dirty} uncommitted ${r.dirty === 1 ? 'file' : 'files'} on ${r.branch}`,
        acts: [fill('look-dirty', 'Look at them', "show me the uncommitted changes in this repo in plain words: what they are, and whether they look like mine or another session's. don't change anything.")],
      }]
    : []),
  ...(r.stale.length > 0 || r.worktrees > 0
    ? [{
        key: 'stale',
        label: [
          r.stale.length > 0 ? `${r.stale.length} stale ${r.stale.length === 1 ? 'branch' : 'branches'}` : '',
          r.worktrees > 0 ? `${r.worktrees} other ${r.worktrees === 1 ? 'worktree' : 'worktrees'} (another session may be in ${r.worktrees === 1 ? 'it' : 'them'})` : '',
        ].filter(Boolean).join(', '),
        acts: [fill('clean-up', 'Clean up', `${m.lead}list the stale branches, worktrees and open pull requests in this repo and give each a keep, merge or delete call with a reason, in plain words. don't delete, close, merge, push or switch branches until I say yes.`)],
      }]
    : []),
]
