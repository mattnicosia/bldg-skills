// ---------- Shared ----------

export type MethodId = 'pstack' | 'pocock'

// 'start', 'now', or the id of one of the active method's guide pages.
export type Tab = string

// Plugin keys from installed_plugins.json, and the methods whose skills were
// copied into a skills folder instead of installed as a plugin.
export type Env = { isRead: boolean; plugins: string[]; copied: MethodId[] }

export type PrStage = 'conflict' | 'fail' | 'draft' | 'running' | 'changes' | 'checking' | 'ready'

export type PullRequest = { number: number; title: string; ci: 'fail' | 'pending' | 'pass' | 'none'; isDraft: boolean; stage: PrStage }

export type Repo = {
  isRead: boolean
  error: string | null
  name: string
  branch: string
  dirty: number
  stale: string[]
  worktrees: number
  prs: PullRequest[]
  // False only when the method names a setup file and the repo lacks it.
  isSetUp: boolean
}

export type Choice = { key: string; label: string; tier: string }

export type Decision = { question: string; options: Choice[]; pick: string; why: string } | null

export type Summary = { done: string; next: string; links: string[]; isWaiting: boolean } | null

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

export type PocockState = { flow: Flow; nudge: Nudge; isNudgeOff: boolean }

// ---------- pstack ----------

export type TaskStatus = 'pending' | 'in_progress' | 'completed'

export type Task = { id: string; subject: string; status: TaskStatus }

export type Advice = { what: string; move: string; isReady: boolean }

export type Power = { model: string; effort: string }

export type Seen = { commands: number; skills: number; tools: number; last: string[] }

export type Live = {
  playbook: string | null
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
      method: MethodId | null
      tab: Tab
      env: Env
      repo: Repo
      decision: Decision
      summary: Summary
      states: States
      seen: Seen
    }
  }
}
