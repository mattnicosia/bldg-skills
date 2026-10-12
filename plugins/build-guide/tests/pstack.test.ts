import { expect, test } from 'claude-code/testing'

import { all, COMPOSER, engine, md, PANE, PSTACK, settle, START } from './engine'

const PLAYBOOK = '/plugins/pstack/skills/poteto-mode/playbooks/bug-fix.md'
const now = () => Math.floor(Date.now() / 1000)

test('follows TaskCreate, advises on the running step and names the next move', async ($, on) => {
  engine(on, { plugins: PSTACK })
  await $.session.start(START)
  await $.tool.call({ tool: 'Read', file_path: PLAYBOOK })
  await $.tool.call({ tool: 'TaskCreate', subject: 'Reproduce the duplicate write', description: 'x' })
  await $.tool.call({ tool: 'TaskCreate', subject: 'Decide what the invite token allows', description: 'x' })
  await $.tool.call({ tool: 'TaskUpdate', taskId: '7', status: 'completed' })
  await $.tool.call({ tool: 'TaskUpdate', taskId: '8', status: 'in_progress' })
  await $.skill.prompt({ skill: 'pstack:how', text: 'x' })
  await settle()

  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  const text = await md(pane)
  expect(text).toContain('Bug fix playbook')
  expect(text).toContain('[x] Reproduce the duplicate write (Sonnet · Medium)')
  expect(text).toContain('[>] Decide what the invite token allows (Fable · High)')
  expect(text).toContain("What's happening: It decides who may send a price.")
  expect(text).toContain('Power: Needs Fable · High')

  await $.tool.call({ tool: 'TaskUpdate', taskId: '8', status: 'completed' })
  expect(await md(pane)).toContain('/blast-radius')
  await settle()
})

test('a desktop session: typed /poteto-mode, the mod task tools and a playbook read through Bash', async ($, on) => {
  const { seen } = engine(on, { plugins: PSTACK })
  await $.session.start(START)
  await $.command.run({ command: 'pstack:poteto-mode', args: 'spec the no-account bid response', ...COMPOSER })
  expect(seen.args[0]).toContain('spec the no-account bid response')
  expect(seen.args[0]).toContain('mcp__build-guide__task_create')

  await $.tool.call({ tool: 'Bash', command: `cat ${PLAYBOOK}; echo done` })
  const made = await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Read the shipped code' })
  expect(made.result).toBe('Task #1 created: Read the shipped code')
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Write the spec' })
  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'in_progress' })
  const missing = await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '9', status: 'completed' })
  expect(missing.result).toContain('No task #9')
  await settle()

  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  const text = await md(pane)
  expect(text).toContain('Bug fix playbook')
  expect(text).toContain('[>] Read the shipped code (Sonnet · Medium)')
  expect(text).toContain('[ ] Write the spec (Fable · High)')
  await settle()
})

test('the skill text of /poteto-mode carries the task-tool note once', async ($, on) => {
  engine(on, { plugins: PSTACK })
  await $.session.start(START)
  const said = await $.skill.prompt({ skill: 'pstack:poteto-mode', text: 'the skill' })
  expect(said.text).toContain('mcp__build-guide__task_update')
  await settle()
})

test('a follow-on playbook read mid-run keeps the main playbook, and /poteto-mode counts as a skill', async ($, on) => {
  engine(on, { plugins: PSTACK })
  await $.session.start(START)
  await $.command.run({ command: 'pstack:poteto-mode', args: 'implement ticket 25', ...COMPOSER })
  await $.tool.call({ tool: 'Read', file_path: '/plugins/pstack/skills/poteto-mode/playbooks/feature.md' })
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Map the estimate store' })
  await $.tool.call({ tool: 'Read', file_path: '/plugins/pstack/skills/poteto-mode/playbooks/opening-a-pr.md' })

  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  const text = await md(pane)
  expect(text).toContain('Feature playbook')
  expect(text).not.toContain('Opening a PR playbook')
  expect(text).toContain('Seen: 0 commands, 1 skills')

  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'completed' })
  await $.tool.call({ tool: 'Read', file_path: '/plugins/pstack/skills/poteto-mode/playbooks/opening-a-pr.md' })
  expect(await md(pane)).toContain('Opening a PR playbook')
  await settle()
})

test('the Overnight tab puts a planning prompt in the composer', async ($, on) => {
  const { seen } = engine(on, { plugins: PSTACK })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE('desktop') as never)
  await (pane as any).press({ key: 'tab-guide' })
  await (pane as any).press({ key: 'tab-overnight' })
  await (pane as any).press({ key: 'plan-overnight' })
  expect(seen.filled[0]).toContain('plan an overnight run for <ticket>')
  expect(seen.filled[0]).toContain('do not merge, deploy, or post')
  await settle()
})

test('the Start tab lists open work from git and gh, and a start button sends at once', async ($, on) => {
  const at = now()
  const { seen } = engine(on, {
    plugins: PSTACK,
    git: {
      'rev-parse --show-toplevel': '/Users/me/dev/acme/.claude/worktrees/me',
      'rev-parse --abbrev-ref HEAD': 'mine',
      'status --porcelain': ' M a.ts\n?? b.ts',
      'branch --merged main --format=%(refname:short)': 'main\nold-fix\nbusy',
      'for-each-ref --format=%(refname:short)|%(committerdate:unix) refs/heads': `main|${at}\nold-fix|${at}\nbusy|${at}\nmine|${at}`,
      'rev-parse --path-format=absolute --git-common-dir': '/Users/me/dev/acme/.git',
      'worktree list --porcelain':
        'worktree /Users/me/dev/acme\nbranch refs/heads/main\n\nworktree /Users/me/dev/acme/.claude/worktrees/x\nbranch refs/heads/busy\n\nworktree /Users/me/dev/acme/.claude/worktrees/me\nbranch refs/heads/mine',
    },
    prs: [{ number: 41, title: 'Estimate store reload', isDraft: false, statusCheckRollup: [{ status: 'COMPLETED', conclusion: 'FAILURE' }] }],
  })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'refresh' })
  const text = await all(pane)
  expect(text).toContain('acme · mine')
  expect(text).toContain('PR #41 · checks failing')
  expect(text).toContain('2 uncommitted files on mine')
  expect(text).toContain('1 stale branch, 1 other worktree')
  expect(text).not.toContain('2 stale')
  expect(text).toContain('Get it green')

  await pane.press({ key: 'start-ticket' })
  expect(seen.sent[0]).toContain('ready-for-agent')
  await pane.press({ key: 'clean-up' })
  expect(seen.filled.at(-1)).toMatch(/^\/poteto-mode list the stale branches/)
  await settle()
})

test('quick replies send during a run and switch to next moves when every step is done', async ($, on) => {
  const { seen } = engine(on, { plugins: PSTACK })
  await $.session.start(START)
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Write the failing test' })
  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'in_progress' })
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  await pane.press({ key: 'q-evidence' })
  expect(seen.sent[0]).toContain('show me the evidence')

  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'completed' })
  const after = await all(pane)
  expect(after).toContain('Check what else breaks')
  expect(after).not.toContain('Show me the evidence')
  await settle()
})

test('buttons whose text starts with a slash run the command instead of submitting it', async ($, on) => {
  const { seen } = engine(on, { plugins: PSTACK })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'start-recall' })
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Write the failing test' })
  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'in_progress' })
  await pane.press({ key: 'tab-now' })
  await pane.press({ key: 'q-plain' })
  expect(seen.ran.some(r => r.startsWith('/recall'))).toBe(true)
  expect(seen.ran).toContain('/bro')
  expect(seen.sent.some(x => x.startsWith('/'))).toBe(false)
  await settle()
})

const green = [{ status: 'COMPLETED', conclusion: 'SUCCESS' }]
const STAGED = [
  { number: 279, title: 'Bids on Home', isDraft: true, statusCheckRollup: green, mergeable: 'CONFLICTING', reviewDecision: '' },
  { number: 280, title: 'Draft work', isDraft: true, statusCheckRollup: green, mergeable: 'MERGEABLE', reviewDecision: '' },
  { number: 281, title: 'Done work', isDraft: false, statusCheckRollup: green, mergeable: 'MERGEABLE', reviewDecision: '' },
  { number: 282, title: 'Still checking', isDraft: false, statusCheckRollup: green, mergeable: 'UNKNOWN', reviewDecision: '' },
]

test('green checks alone are not ready: each PR gets its stage, and a ready one offers Merge it when the guard is off', { options: { gitGuard: false } }, async ($, on) => {
  const { seen } = engine(on, { plugins: PSTACK, prs: STAGED })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'refresh' })
  const text = await all(pane)
  expect(text).toContain('PR #279 · conflicts with main')
  expect(text).toContain('PR #280 · draft')
  expect(text).toContain('PR #281 · ready to merge')
  expect(text).toContain('PR #282 · GitHub still checking')
  expect(text).toContain('Fix the conflict')
  expect(text).toContain('Finish the draft')
  expect((text.match(/"label":"Merge it"/g) ?? []).length).toBe(1)
  await pane.press({ key: 'merge-281' })
  expect(seen.filled[0]).toContain('gh pr view 281 --json commits,files')
  await settle()
})

test('with the git guard on, a ready PR offers no Merge it, since the guard would block it', async ($, on) => {
  engine(on, { plugins: PSTACK, prs: STAGED })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'refresh' })
  expect(await all(pane)).not.toContain('"label":"Merge it"')
  await settle()
})

test('the model a step needs is checked against the one the session runs on', async ($, on) => {
  engine(on, { plugins: PSTACK })
  await $.session.start(START)
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Rename the helper' })
  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'in_progress' })
  await settle()
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  expect(await md(pane)).toContain("Needs Haiku · Low. The session's model shows after its next step.")
  await settle()
})
