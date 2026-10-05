import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'pocock-guide',
  surface: 'terminal',
  component: 'Pane',
  requestId: 'pocock-guide',
  props: { title: 'Pocock flow', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 40 }, view: {} },
} as const
const USAGE = { input_tokens: 1, output_tokens: 1, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 }
const RUN = (stdout: string, exitCode = 0) => ({ value: { exitCode, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } })
const START = { cwd: '/Users/me/dev/app', surface: 'terminal', isInteractive: true } as const

type Setup = { plugins?: string[]; isSetUp?: boolean; saved?: Record<string, unknown> }

// Stands in for the engine: a repo at /Users/me/dev/app, the given plugins
// installed, and a store that keeps what the mod writes.
const engine = (on: On, setup: Setup = {}) => {
  const store: Record<string, unknown> = { ...setup.saved }
  const seen = { opened: 0, filled: [] as string[], sent: [] as string[], ran: [] as string[], context: [] as string[] }
  const plugins = setup.plugins ?? ['matt-pocock@bldg-skills']
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  on('session.cwd', async () => ({ value: '/Users/me/dev/app' }))
  on('env.get', async () => ({ value: '/Users/me' }))
  on('fs.read', async () => ({ value: JSON.stringify({ version: 2, plugins: Object.fromEntries(plugins.map(p => [p, []])) }) }))
  on('fs.exists', async (_$, e) => ({ value: e.path.endsWith('docs/agents/issue-tracker.md') ? setup.isSetUp !== false : false }))
  on('store.get', async (_$, e) => ({ value: store[e.key] }))
  on('store.set', async (_$, e) => {
    store[e.key] = e.value
    return { value: undefined }
  })
  on('process.run', async (_$, e) => {
    const [cmd, ...rest] = e.argv
    if (cmd === 'gh') return RUN('[]')
    const out: Record<string, string> = {
      'rev-parse --show-toplevel': '/Users/me/dev/app',
      'rev-parse --abbrev-ref HEAD': 'main',
      'rev-parse --path-format=absolute --git-common-dir': '/Users/me/dev/app/.git',
      'worktree list --porcelain': 'worktree /Users/me/dev/app\nbranch refs/heads/main',
    }
    const key = rest.join(' ')
    return key in out ? RUN(out[key] ?? '') : RUN('', 1)
  })
  on('command.register', async (_$, e) => ({ value: { command: e.name } }))
  on('ui.open', async () => {
    seen.opened += 1
    return { value: { isPlaced: true as const } }
  })
  on('ui.toast', async () => ({ value: undefined }))
  on('tool.call', async () => ({ result: {}, text: 'ok' }))
  on('command.run', async (_$, e) => {
    seen.ran.push(`/${e.command} ${e.args}`.trim())
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
  return { store, seen }
}

const md = async (pane: { find: (q: { type: 'Markdown' }) => Promise<{ text: string } | undefined> }) => (await pane.find({ type: 'Markdown' }))?.text ?? ''

test('the strip follows the skills, Next step offers only what the flow allows, and /implement covers review', async ($, on) => {
  engine(on)
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  await pane.press({ key: 'tab-now' })
  expect(await md(pane)).toContain('Nothing started yet')
  expect(await md(pane)).toContain('**Next step:** Grill your idea: `/grill-with-docs`')

  await $.skill.prompt({ skill: 'mattpocock-skills:grill-with-docs', text: 'x' })
  expect(await md(pane)).toContain('**[Grill]** → Spec')
  expect(await md(pane)).toContain('**Next step:** Write the spec: `/to-spec`')
  expect(await md(pane)).toContain('Keep grilling, spec and tickets in this one chat')

  await $.tool.call({ tool: 'Skill', skill: 'to-spec' })
  await $.command.run({ command: 'to-tickets', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: true, columns: 120 } })
  expect(await md(pane)).toContain('**Next step:** Build the first ticket')
  expect(await md(pane)).toContain('Clear the chat before each ticket')

  await $.skill.prompt({ skill: 'implement', text: 'x' })
  const built = await md(pane)
  expect(built).toContain('✓Build → **[Review]**')
  expect(built).toContain('**Next step:** Open the pull request')
})

test('skipping the grill shows why it matters, and a bug fix does not count as a skip', async ($, on) => {
  engine(on)
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  await pane.press({ key: 'tab-now' })
  await $.skill.prompt({ skill: 'tdd', text: 'x' })
  expect(await md(pane)).toContain('**You skipped Grill.** Code built on a fuzzy idea gets rebuilt.')
  expect(await md(pane)).toContain('**Next step:** Review the change')

  await pane.press({ key: 'reset' })
  await $.skill.prompt({ skill: 'diagnosing-bugs', text: 'x' })
  expect(await md(pane)).not.toContain('You skipped')
})

test('a build request before any grilling gets a nudge card and a note for the model, and nothing is blocked', async ($, on) => {
  const { seen } = engine(on)
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  await $.prompt.submit({ text: 'add a dark mode toggle to settings', wait: false, origin: { kind: 'composer' } })
  expect(seen.sent[0]).toBe('add a dark mode toggle to settings')
  expect(seen.context.join(' ')).toContain('suggesting they run /grill-with-docs first')
  const text = JSON.stringify(await pane.find({ type: 'Box' }))
  expect(text).toContain('Grill it first?')
  await pane.press({ key: 'nudge-go' })
  expect(seen.filled[0]).toBe('/grill-with-docs add a dark mode toggle to settings')

  await $.prompt.submit({ text: 'the login page crashes on submit', wait: false, origin: { kind: 'composer' } })
  expect(JSON.stringify(await pane.find({ type: 'Box' }))).toContain('Sounds like something is broken')

  await $.prompt.submit({ text: 'how does the login page work?', wait: false, origin: { kind: 'composer' } })
  expect(JSON.stringify(await pane.find({ type: 'Box' }))).not.toContain('Sounds like something is broken')

  await $.skill.prompt({ skill: 'grill-with-docs', text: 'x' })
  const before = seen.context.length
  await $.prompt.submit({ text: 'add the toggle now', wait: false, origin: { kind: 'composer' } })
  expect(seen.context.length).toBe(before)
})

test('without the skills installed, the Start tab shows how to install them and hides the skill buttons', async ($, on) => {
  engine(on, { plugins: [] })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  const text = JSON.stringify(await pane.find({ type: 'Box' }))
  expect(text).toContain("Matt Pocock's skills are not installed")
  expect(text).toContain('claude plugin install matt-pocock@bldg-skills')
  expect(text).toContain('Catch me up')
  expect(text).not.toContain('I have an idea')
})

test('the official marketplace copy counts as installed but out of date, so the card points at the mirror', async ($, on) => {
  engine(on, { plugins: ['mattpocock-skills@claude-plugins-official'] })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  const text = JSON.stringify(await pane.find({ type: 'Box' }))
  expect(text).toContain('is out of date')
  expect(text).toContain('claude plugin install matt-pocock@bldg-skills')
  expect(text).toContain('I have an idea')
})

test('the mirror next to the official copy is not out of date', async ($, on) => {
  engine(on, { plugins: ['mattpocock-skills@claude-plugins-official', 'matt-pocock@bldg-skills'] })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  expect(JSON.stringify(await pane.find({ type: 'Box' }))).not.toContain('out of date')
})

test('a repo that is not set up offers Set up this repo first', async ($, on) => {
  const { seen } = engine(on, { isSetUp: false })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  await pane.press({ key: 'refresh' })
  expect(JSON.stringify(await pane.find({ type: 'Box' }))).toContain('This repo is not set up')
  await pane.press({ key: 'start-setup' })
  expect(seen.ran.at(-1)).toBe('/setup-matt-pocock-skills')
  expect(seen.sent).toEqual([])
})

test('the pane opens on its own only where pstack-guide is not installed', async ($, on) => {
  const { seen } = engine(on, { plugins: ['matt-pocock@bldg-skills', 'pstack-guide@matt-mods'] })
  await $.session.start(START)
  expect(seen.opened).toBe(0)
  await $.command.run({ command: 'mod-pocock', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: true, columns: 120 } })
  expect(seen.opened).toBe(1)
  const pane = await $.ui.mount(PANE)
  await pane.press({ key: 'refresh' })
})

test('the flow is saved per repo, so a new session picks up where the last one stopped', async ($, on) => {
  const { store } = engine(on, { saved: { 'flow:/Users/me/dev/app': { root: '/Users/me/dev/app', done: ['grill', 'spec', 'tickets'], current: 'tickets', last: 'to-tickets', isBugFix: false } } })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE)
  await pane.press({ key: 'tab-now' })
  expect(await md(pane)).toContain('**[Tickets]**')
  await $.skill.prompt({ skill: 'implement', text: 'x' })
  expect((store['flow:/Users/me/dev/app'] as { current: string }).current).toBe('review')
})

test('a turn that ends with a choice draws the decision card with a button per option', async ($, on) => {
  const { seen } = engine(on)
  on('model.complete', async () => ({
    value: {
      isAnswered: true,
      text: '{"done":"Wrote the spec.","next":"Pick how to build it.","isWaiting":true,"isChoice":true,"question":"How should we build it?","options":[{"key":"A","label":"One ticket at a time"},{"key":"B","label":"All tickets in one run"}],"pick":"A","why":"You are new, so one ticket at a time is easier to follow."}',
      usage: USAGE,
    },
  }))
  on('turn.complete', async (_$, e) => ({ text: e.answer }))
  await $.session.start(START)
  await $.turn.complete({ answer: 'A. One ticket at a time.\nB. All of them at once.\n\nReply with a letter.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as never)
  for (let i = 0; i < 20; i++) await Promise.resolve()
  const pane = await $.ui.mount({ ...PANE, surface: 'desktop' } as never)
  const text = JSON.stringify(await pane.find({ type: 'Box' }))
  expect(text).toContain('CLAUDE IS ASKING YOU')
  expect(text).toContain('One ticket at a time')
  expect(text).toContain('★ what the flow suggests')
  await (pane as any).press({ key: 'choose-A' })
  expect(seen.sent.at(-1)).toBe('A')
})
