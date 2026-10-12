// ---------- Shared ----------

export type MethodId = 'pstack' | 'pocock'

// The stages every method maps onto: pstack's six. The stage bar draws these.
export type SharedId = 'understand' | 'design' | 'build' | 'verify' | 'ship' | 'overnight'

// Where the work is on the shared stage bar, the method whose own move put it
// there, and how many stage changes the session has seen. One change is one
// move, however many methods it moves.
export type Stage = { at: SharedId | null; by: MethodId | null; moves: number }

// 'start', 'now', or the id of one of the picked method's guide pages.
export type Tab = string

// Plugin keys from installed_plugins.json, and the methods whose skills were
// copied into a skills folder instead of installed as a plugin.
export type Env = { isRead: boolean; plugins: string[]; copied: MethodId[] }

export type PrStage = 'conflict' | 'fail' | 'draft' | 'running' | 'changes' | 'checking' | 'ready'

export type PullRequest = { number: number; title: string; branch: string; ci: 'fail' | 'pending' | 'pass' | 'none'; isDraft: boolean; stage: PrStage }

export type Repo = {
  isRead: boolean
  error: string | null
  name: string
  branch: string
  dirty: number
  stale: string[]
  worktrees: number
  prs: PullRequest[]
  // False only when a method names a setup file and the repo lacks it.
  isSetUp: boolean
}

export type Choice = { key: string; label: string; tier: string }

export type Decision = { question: string; options: Choice[]; pick: string; why: string } | null

export type Summary = { done: string; next: string; links: string[]; isWaiting: boolean } | null

// ---------- Target map ----------
// The shape the target-map mod's bin/target-map-status.mjs writes.

export type JobState = 'moved' | 'not_yet' | 'gray'

export type Job = {
  id: string
  name: string
  short: string
  state: JobState
  stuck: boolean
  since: string
  evidence: string
  needs: string
  source: string
  proofKind: string
  zeroSince?: string
}

export type Flag = { id: string; name: string; note?: string; jobs: Job[] }

export type Road = { id: string; name: string; from: string; crossesOff: string[] | string; unlocks: string[] | string; source: string }

export type Status = { product: string; goal: string; targetSetOn: string; checkedAt: string; flags: Flag[]; roads: Road[]; decisions: string[] }

// none: the repo has no targets file; ask fills the prompt to start one.
// missing: a targets file but no status file; command writes it.
// note: says which file shows when the repo has several.
export type Target =
  | { phase: 'unread' }
  | { phase: 'none'; ask: string }
  | { phase: 'missing'; command: string }
  | { phase: 'bad'; reason: string }
  | { phase: 'ok'; data: Status; note: string }

// ---------- pocock ----------

export type StepId = 'grill' | 'spec' | 'tickets' | 'build' | 'review' | 'pr' | 'retro'

export type Flow = {
  // The repo this progress belongs to, so a new session in it picks up where the last one stopped.
  root: string
  done: StepId[]
  current: StepId | null
  // The skill that last moved the flow, without its plugin prefix.
  last: string
  isBugFix: boolean
}

export type Nudge = { text: string; kind: 'grill' | 'bug' } | null

export type PocockState = { flow: Flow; nudge: Nudge }

// ---------- pstack ----------

export type TaskStatus = 'pending' | 'in_progress' | 'completed'

export type Task = { id: string; subject: string; status: TaskStatus }

// What Haiku said about one step: what is happening, and one line per method
// on what that method would have the person do now, by method id.
export type Advice = { what: string; would: Record<string, string>; isReady: boolean }

export type Power = { model: string; effort: string }


export type Live = {
  playbook: string | null
  // The shared stage pstack is on: set by its own playbook, skills and tasks,
  // or moved there when the other method moved.
  stage: SharedId | null
  advice: Record<string, Advice>
  power: Power
  steps: string[]
  tasks: Task[]
  skills: string[]
  prOpened: boolean
  prMerged: boolean
}

// Each method's own state, under its id. A method not used yet has none.
export type States = { pocock?: PocockState; pstack?: Live }

declare module 'claude-code' {
  interface PluginState {
    'build-guide': {
      // The method the Guide tab shows. The Start and Now tabs show every method.
      method: MethodId | null
      tab: Tab
      env: Env
      repo: Repo
      decision: Decision
      summary: Summary
      states: States
      stage: Stage
      target: Target
      isTargetOpen: boolean
    }
  }
}
