// What a method is. A method is data and pure functions over its own state; the
// pane (register.tsx) does every read, write, call and toast for it. The engine
// follows `$` only into functions of the file that holds the hooks, so nothing
// here touches `$`.

import type { Env, MethodId, PullRequest } from '../types'

// A button. It puts `text` in the prompt, or sends it at once when `isSend`
// (a slash command runs as a command).
export type Act = {
  key: string
  label: string
  text?: string
  isSend?: boolean
  isPrimary?: boolean
  // A plugin key prefix the button calls; the button hides when it is not installed.
  needs?: string
}

// A bordered card: the install warning.
export type Card = { key: string; title: string; body: string; color: string; code?: string; note?: string; acts: Act[] }

export type GuidePage = {
  id: string
  label: string
  // Drawn on the desktop; `md` stands in for it in the terminal.
  svg?: string
  alt: string
  md: string
  // Buttons under the picture, one row each, with an optional label in front.
  note?: string
  rows?: { label?: string; acts: Act[] }[]
  recipes?: { title: string; prompt: string }[]
}

// One method's column on the Now tab, as data; pair.ts draws it.
export type Row = { label: string; mark: 'done' | 'now' | 'todo' | 'skipped'; tag?: string }
export type Section = { title: string; body: string; tone?: 'warn' | 'bad' | 'good' }
export type Column = {
  // The method's own stage, as it names it: "Build", "Step 4 of 7 · Build".
  stage: string
  title: string
  rows: Row[]
  sections: Section[]
  // What the method would have the person do now: Haiku's line, else the stage's own text.
  would: string
}

// The one thing the method would do next, and the prompt that does it.
export type Move = { label: string; text: string; why: string }

// The state a reducer hands back, and the work it asks the pane to do. A method
// never toasts or adds a note to a prompt: its advice shows in its own column.
export type Out<S> = {
  s: S
  // Read this file, then hand it to `hooks.file`.
  read?: string
  // Ask Haiku this, then hand the answer to `hooks.answer` with the key. The pane
  // adds every method's position and asks for one line per method.
  ask?: { key: string; prompt: string }
}

// Where the method's skills come from, so the pane can say when they are missing.
export type Requires = {
  name: string
  // Prefixes of installed_plugins.json keys that count as installed.
  plugins: string[]
  // A skill whose SKILL.md in a skills folder also counts, for copies made without a plugin.
  skill: string
  // A plugin key that is installed but too old to use, when it is the only copy.
  outdated?: string
  outdatedNote?: string
  install: string
  removeOld?: string
}

export type Method<S> = {
  id: MethodId
  label: string
  requires: Requires
  // Put in front of a work prompt the shared code writes, such as the clean-up one.
  lead: string
  starts: Act[]
  // The starts that still work when the method's skills are missing.
  plainStarts: Act[]
  startNote: string
  // A file the repo must have before the method's skills work, and the button that makes it.
  setup?: { file: string; act: Act; warn: string }
  prActs: (pr: PullRequest, canMerge: boolean) => Act[]
  // The reply that says the last message again in plain words.
  explain: Act
  // Quick replies once every step is done.
  after: Act[]
  // How the after-turn reader is told what this method favors.
  decide: { who: string; favors: string }
  guide: GuidePage[]

  empty: S
  // Progress kept per repo in the store, so a new session in the repo picks it up.
  persist?: { rootOf: (s: S) => string; save: (s: S) => unknown; load: (s: S, saved: unknown, root: string) => S }

  // Its own stage now (an entry of its STAGE_MAP list), and the state moved to
  // another of its stages when the other method moves.
  stageOf: (s: S) => string | null
  moveTo: (s: S, stage: string) => S
  // Where it is, in one line, for the Haiku prompt.
  brief: (s: S) => string
  // Haiku's lines for the running step, by method id, once they came back.
  would?: (s: S) => Record<string, string> | undefined
  // Words naming the work under way, for matching it to a target map job.
  focus?: (s: S) => string[]
  column: (s: S, would: string | undefined) => Column
  next: (s: S) => Move
  phase: (s: S) => 'idle' | 'running' | 'done'
  reset: (s: S) => S
  isBusy: (s: S) => boolean
  hooks: {
    // A slash command the person ran; returns the args to pass on.
    command?: (s: S, command: string, args: string) => Out<S> & { args: string }
    // A skill's text as the model will read it; returns the text to pass on.
    skill?: (s: S, skill: string, text: string) => Out<S> & { text: string }
    // A main-agent tool call that finished.
    tool?: (s: S, tool: string, args: Record<string, unknown>, output: string) => Out<S>
    // A model step of the main agent: the model and effort it ran on.
    step?: (s: S, model: string, effort: string) => S
    // A prompt about to be sent. It changes the method's own state and nothing else.
    prompt?: (s: S, text: string, isPerson: boolean, hasSkills: boolean) => Out<S>
    file?: (s: S, path: string, content: string | null) => Out<S>
    answer?: (s: S, key: string, text: string | null) => S
  }
  // Tools the model can call, served as mcp__build-guide__<name>.
  tools?: { name: string; description: string; inputSchema: Record<string, unknown>; run: (s: S, args: Record<string, unknown>) => Out<S> & { result: string } }[]
}

// Fills the prompt: the person reads it, adds what it asks for, and presses Enter.
export const fill = (key: string, label: string, text: string): Act => ({ key, label, text })
// Sends at once.
export const say = (key: string, label: string, text: string): Act => ({ key, label, text, isSend: true })

// Whether the method's skills are installed, and new enough.
export const skillsOf = (m: AnyMethod, e: Env): 'ok' | 'missing' | 'outdated' => {
  if (!e.isRead) return 'ok'
  const found = e.plugins.filter(k => m.requires.plugins.some(p => k.startsWith(p)))
  const isCopied = e.copied.includes(m.id)
  if (!isCopied && found.length === 0) return 'missing'
  if (!isCopied && m.requires.outdated && found.every(k => k === m.requires.outdated)) return 'outdated'
  return 'ok'
}

// Merging cannot be undone, so the button fills the prompt and the check comes first.
export const mergeAct = (n: number): Act =>
  fill(
    `merge-${n}`,
    'Merge it',
    `merge pr #${n}. first run gh pr view ${n} --json commits,files and confirm every commit and file is mine and belongs to this change; if any is not, stop and tell me. confirm the checks are green, it merges cleanly and it does what its ticket asked. then merge it the way this repo merges (look at recent merged PRs) and delete the branch. tell me what you merged.`,
  )

// Quick replies while work is running. They send at once and wait their turn.
// `explain` is the plain-words reply of a method whose skills are installed.
export const during = (explain: Act): Act[] => [
  say('q-continue', 'Continue', 'continue'),
  say('q-evidence', 'Show me the evidence', 'show me the evidence for what you just did: the real command, output or screenshot.'),
  { ...explain, key: 'q-plain' },
  say('q-stop', 'Stop and explain', "stop after this step. tell me where you are, what's left, and anything you need from me."),
]

// A method whatever its state, for the list the pane draws.
export type AnyMethod = Method<any>
