export type Tab = 'start' | 'now' | 'flow' | 'ramps' | 'more' | 'words'

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

// isOutdated: the only copy is the official marketplace's, which predates v1.3.1 and lacks /implement-spec, /pr and /retro.
export type Env = { isRead: boolean; hasSkills: boolean; isOutdated: boolean; hasPstackGuide: boolean }

export type PullRequest = { number: number; title: string; ci: 'fail' | 'pending' | 'pass' | 'none'; isDraft: boolean }

export type Repo = {
  isRead: boolean
  error: string | null
  name: string
  branch: string
  dirty: number
  stale: string[]
  worktrees: number
  prs: PullRequest[]
  isSetUp: boolean
}

export type Choice = { key: string; label: string }

export type Decision = { question: string; options: Choice[]; pick: string; why: string } | null

export type Summary = { done: string; next: string; links: string[]; isWaiting: boolean } | null

declare module 'claude-code' {
  interface PluginState {
    'pocock-guide': {
      tab: Tab
      flow: Flow
      nudge: Nudge
      env: Env
      repo: Repo
      decision: Decision
      summary: Summary
    }
  }
}
