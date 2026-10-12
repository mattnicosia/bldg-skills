import type { On } from 'claude-code'

export const PANE = (surface: 'terminal' | 'desktop' = 'terminal') =>
  ({
    plugin: 'build-guide',
    surface,
    component: 'Pane',
    requestId: 'build-guide',
    props: { title: 'Build guide', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 40 }, view: {} },
  }) as const

export const START = { cwd: '/Users/me/dev/app', surface: 'terminal', isInteractive: true } as const
export const COMPOSER = { origin: { kind: 'composer' }, presentation: { isFullscreen: true, columns: 120 } } as const
export const USAGE = { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 }

const RUN = (stdout: string, exitCode = 0) => ({ value: { exitCode, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } })

export const PSTACK = ['pstack@pstack-claude']
export const POCOCK = ['matt-pocock@bldg-skills']

type Setup = {
  plugins?: string[]
  isSetUp?: boolean
  store?: Record<string, unknown>
  git?: Record<string, string>
  prs?: unknown[]
  // What Haiku answers.
  model?: string
  // The target map status file, or null when there is none.
  target?: unknown
  // The files in the repo's targets/ folder.
  targets?: string[]
  // What the target-map check script exits with.
  scriptExit?: number
}

const now = () => Math.floor(Date.now() / 1000)

// Stands in for the engine: a repo at /Users/me/dev/app on main, the given
// plugins installed, and a store that keeps what the mod writes.
export const engine = (on: On, setup: Setup = {}) => {
  const store: Record<string, unknown> = { ...setup.store }
  const seen = { opened: 0, filled: [] as string[], sent: [] as string[], ran: [] as string[], args: [] as string[], context: [] as string[], tools: [] as string[], toasts: [] as string[], asked: [] as string[] }
  const plugins = setup.plugins ?? POCOCK
  const git: Record<string, string> = {
    'rev-parse --show-toplevel': '/Users/me/dev/app',
    'rev-parse --abbrev-ref HEAD': 'main',
    'status --porcelain': '',
    'symbolic-ref --short refs/remotes/origin/HEAD': 'origin/main',
    'branch --merged main --format=%(refname:short)': 'main',
    'for-each-ref --format=%(refname:short)|%(committerdate:unix) refs/heads': `main|${now()}`,
    'rev-parse --path-format=absolute --git-common-dir': '/Users/me/dev/app/.git',
    'worktree list --porcelain': 'worktree /Users/me/dev/app\nbranch refs/heads/main',
    ...setup.git,
  }
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  on('session.cwd', async () => ({ value: '/Users/me/dev/app' }))
  on('env.get', async (_$, e) => ({ value: e.name === 'HOME' ? '/Users/me' : undefined }))
  const targets = setup.targets ?? ['bldg-os.json']
  const product = (targets.filter(t => t.endsWith('.json')).sort()[0] ?? '').replace(/\.json$/, '')
  on('fs.list', async (_$, e) => {
    if (e.path !== '/Users/me/dev/app/targets' || targets.length === 0) throw new Error('ENOENT')
    return { value: targets.map(name => ({ name, kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false })) }
  })
  on('fs.read', async (_$, e) => {
    if (e.path.endsWith('installed_plugins.json')) {
      const all: Record<string, unknown> = Object.fromEntries(plugins.map(p => [p, []]))
      all['target-map@matt-mods'] = [{ installPath: '/Users/me/.claude/plugins/cache/matt-mods/target-map/0.2.0' }]
      return { value: JSON.stringify({ version: 2, plugins: all }) }
    }
    if (e.path === `/Users/me/.claude/target-map/${product}.status.json`) {
      if (setup.target === undefined || setup.target === null) throw new Error('ENOENT')
      return { value: JSON.stringify(setup.target) }
    }
    return { value: '1. Reproduce it yourself on the matching surface.\n2. Binary-search the cause. More words.\n' }
  })
  on('fs.exists', async (_$, e) => ({ value: e.path.endsWith('docs/agents/issue-tracker.md') ? setup.isSetUp !== false : false }))
  on('store.get', async (_$, e) => ({ value: store[e.key] }))
  on('store.set', async (_$, e) => {
    store[e.key] = e.value
    return { value: undefined }
  })
  on('process.run', async (_$, e) => {
    const [cmd, ...rest] = e.argv
    if (cmd === 'gh') return RUN(JSON.stringify(setup.prs ?? []))
    if (cmd === 'node') {
      seen.ran.push(e.argv.join(' '))
      return RUN('', setup.scriptExit ?? 0)
    }
    const key = rest.join(' ')
    return key in git ? RUN(git[key] ?? '') : RUN('', 1)
  })
  on('command.register', async (_$, e) => ({ value: { command: e.name } }))
  on('tool.register', async (_$, e) => {
    seen.tools.push(e.name)
    return { value: { tool: `mcp__build-guide__${e.name}` } }
  })
  on('ui.open', async () => {
    seen.opened += 1
    return { value: { isPlaced: true as const } }
  })
  on('ui.toast', async (_$, e) => {
    seen.toasts.push(e.text)
    return { value: undefined }
  })
  let created = 6
  on('tool.call', async (_$, e) => {
    if (e.tool === 'TaskCreate') return { result: {}, text: `Task #${(created += 1)} created successfully` }
    return { result: {}, text: 'ok' }
  })
  on('command.run', async (_$, e) => {
    seen.ran.push(`/${e.command} ${e.args}`.trim())
    seen.args.push(e.args)
    return { text: 'ran' }
  })
  on('skill.prompt', async (_$, e) => ({ text: e.text }))
  on('prompt.fill', async (_$, e) => {
    seen.filled.push(e.text)
    return { isFilled: true }
  })
  on('prompt.submit', async (_$, e) => {
    seen.sent.push(e.text)
    seen.context.push(...(e.context ?? []))
    return { text: e.text, context: e.context }
  })
  on('model.complete', async (_$, e) => {
    seen.asked.push(e.prompt)
    // An empty model answer stands for a session with no Haiku.
    if (setup.model === '') return { value: { isAnswered: false as const, reason: 'empty-reply' as const, usage: USAGE } }
    return {
      value: {
        isAnswered: true as const,
        text: setup.model ?? 'WHAT: It decides who may send a price.\npstack: Nothing yet. Check it names the forwarded link risk.\npocock: Watch the failing test go green before review.',
        usage: USAGE,
      },
    }
  })
  on('turn.complete', async (_$, e) => ({ text: e.answer }))
  // Every value the mod writes to its shared stage, in order.
  const stages: { at: string | null; moves: number }[] = []
  on('state.set', async (_$, e, next) => {
    if (e.key === 'stage') stages.push(e.value as { at: string | null; moves: number })
    return next(e)
  })
  return { store, seen, stages }
}

// The test runner has timers; the hooks module's type library does not name them.
declare const setTimeout: (done: () => void, ms: number) => unknown

// Lets work the mod left running (a Haiku call) settle.
export const settle = async () => {
  for (let i = 0; i < 200; i++) await Promise.resolve()
  await new Promise<void>(done => setTimeout(done, 30))
}

export const md = async (pane: { find: (q: { type: 'Markdown' }) => Promise<{ text: string } | undefined> }) => (await pane.find({ type: 'Markdown' }))?.text ?? ''

export const all = async (pane: { find: (q: { type: 'Box' }) => Promise<unknown> }) => JSON.stringify(await pane.find({ type: 'Box' }))

// One method's column on the Now tab, as the terminal draws it.
export const col = async (pane: { find: (q: { key: string }) => Promise<unknown> }, id: string) => JSON.stringify(await pane.find({ key: `col-${id}` }))
