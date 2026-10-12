import { expect, test } from 'claude-code/testing'

import { nextCards } from '../hooks/pair'
import { ownOf, sharedOf, STAGE_MAP } from '../hooks/stages'
import { crossesOff, MISSING } from '../hooks/target'
import { all, col, engine, PANE, POCOCK, PSTACK, settle, START } from './engine'
import { fixture } from './fixture'

const BOTH = [...PSTACK, ...POCOCK]

test('one TaskUpdate moves both columns, and counts as one move', async ($, on) => {
  const { stages } = engine(on, { plugins: BOTH })
  await $.session.start(START)
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Write the failing test' })
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  expect(await col(pane, 'pstack')).toContain('**pstack** · Not started')
  expect(await col(pane, 'pocock')).toContain('**pocock** · Not started')

  await $.tool.call({ tool: 'TaskUpdate', taskId: '1', status: 'in_progress' })
  await settle()
  expect(await col(pane, 'pstack')).toContain('**pstack** · Build')
  expect(await col(pane, 'pocock')).toContain('**pocock** · Step 4 of 7 · Build')
  expect(await all(pane)).toContain('pocock Grill · Spec/Tickets · [Build] · Review · PR · Retro')
  expect(stages).toEqual([{ at: 'build', by: 'pstack', moves: 1 }])
})

test('the stage map: each pocock step sits under one pstack stage, and a step inside the same stage is not a move', async ($, on) => {
  expect(STAGE_MAP.pocock.map(e => `${e.stage}>${e.shared}`)).toEqual(['grill>understand', 'spec>design', 'tickets>design', 'build>build', 'review>verify', 'pr>ship', 'retro>overnight'])
  expect(sharedOf('pocock', 'tickets')).toBe('design')
  expect(ownOf('pocock', 'design')).toBe('spec')
  expect(ownOf('pstack', 'verify')).toBe('verify')

  const { stages } = engine(on, { plugins: BOTH })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  await $.skill.prompt({ skill: 'to-spec', text: 'x' })
  expect(await col(pane, 'pstack')).toContain('**pstack** · Design')
  await $.skill.prompt({ skill: 'to-tickets', text: 'x' })
  expect(await col(pane, 'pocock')).toContain('Step 3 of 7 · Tickets')
  expect(stages.map(s => s.moves)).toEqual([1])

  await $.skill.prompt({ skill: 'code-review', text: 'x' })
  expect(await col(pane, 'pstack')).toContain('**pstack** · Verify')
  expect(stages.at(-1)).toEqual({ at: 'verify', by: 'pocock', moves: 2 })
  await settle()
})

test('one Haiku call gives each column its own line on what it would do now', async ($, on) => {
  const { seen } = engine(on, { plugins: BOTH })
  await $.session.start(START)
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Write the failing test' })
  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'in_progress' })
  await settle()
  expect(seen.asked.length).toBe(1)
  expect(seen.asked[0]).toContain('pocock: step Build (/implement)')
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  expect(await col(pane, 'pstack')).toContain('**What pstack would do now:** Nothing yet. Check it names the forwarded link risk.')
  expect(await col(pane, 'pocock')).toContain('**What pocock would do now:** Watch the failing test go green before review.')

  const desktop = await $.ui.mount(PANE('desktop') as never)
  await (desktop as any).press({ key: 'tab-now' })
  const svg = await all(desktop as never)
  expect(svg).toContain('WHAT PSTACK WOULD DO NOW')
  expect(svg).toContain('WHAT POCOCK WOULD DO NOW')
  await settle()
})

test('without Haiku, each column falls back to its stage text', async ($, on) => {
  engine(on, { plugins: BOTH, model: '' })
  await $.session.start(START)
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Write the failing test' })
  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'in_progress' })
  await settle()
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  expect(await col(pane, 'pstack')).toContain('**What pstack would do now:** Follow the playbook: a repro or failing test first')
  expect(await col(pane, 'pocock')).toContain('**What pocock would do now:** Watch the test fail, then pass.')
})

test('no prompt nudge fires from either method on the Now tab', async ($, on) => {
  const { seen } = engine(on, { plugins: BOTH })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  await $.prompt.submit({ text: 'add a dark mode toggle to settings', wait: false, origin: { kind: 'composer' } })
  expect(seen.context).toEqual([])
  expect(seen.toasts).toEqual([])
  expect(seen.sent).toEqual(['add a dark mode toggle to settings'])
  expect(await col(pane, 'pocock')).toContain('Grill it first?')
  expect(await col(pane, 'pstack')).not.toContain('Grill it first?')
  await settle()
})

test('next move: one card per method, each filling the prompt without sending', async ($, on) => {
  const { seen } = engine(on, { plugins: BOTH })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  const text = await all(pane)
  expect(text).toContain('"key":"next-pstack"')
  expect(text).toContain('"key":"next-pocock"')
  expect(text).not.toContain('Both agree')
  await pane.press({ key: 'next-pstack' })
  await pane.press({ key: 'next-pocock' })
  expect(seen.filled).toEqual(['/poteto-mode <goal>. <how you will know it is done>.', '/grill-with-docs '])
  expect(seen.sent).toEqual([])
  expect(seen.ran).toEqual([])
  await settle()
})

test('next move: when both methods propose the same command, one wide card says Both agree', () => {
  const cards = nextCards([
    { id: 'pstack', label: 'pstack', move: { label: 'Build ticket 12', text: '/implement 12', why: '' } },
    { id: 'pocock', label: 'pocock', move: { label: 'Build the next ticket', text: '/implement ', why: '' } },
  ])
  expect(cards.length).toBe(1)
  expect(cards[0]?.title).toBe('Both agree')
  expect(cards[0]?.ids).toEqual(['pstack', 'pocock'])

  const split = nextCards([
    { id: 'pstack', label: 'pstack', move: { label: 'Check it', text: '/blast-radius', why: '' } },
    { id: 'pocock', label: 'pocock', move: { label: 'Review it', text: '/code-review since main', why: '' } },
  ])
  expect(split.map(c => c.title)).toEqual(['pstack', 'pocock'])
})

test('the target strip reads the status file: one row per flag, its note for a flag with no jobs, never 0 left, and the stuck line', async ($, on) => {
  engine(on, { plugins: BOTH, target: fixture })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  const text = await all(pane)
  expect(text).toContain('Target: Acme runs on one platform alone')
  expect(text).toContain('PM tool off  ○●○◌○○○!○○  8 left')
  expect(text).toContain('Accounting off  ●○○○○◌○○  7 left')
  expect(text).toContain('Other tools off: No other tools are on the map yet.')
  expect(text).not.toContain('0 left')
  expect(text).toContain('Stuck: P7 project key, since 2026-06-12')
  // The Start tab keeps its starts under the strip.
  expect(text).toContain('Assess the project')

  const desktop = await $.ui.mount(PANE('desktop') as never)
  const svg = await all(desktop as never)
  expect(svg).toContain('TARGET')
  expect(svg).toContain('8 left')
  expect(svg).toContain('No other tools are on the map yet.')
  await settle()
})

test('pressing the strip opens the full map in place, and again closes it', async ($, on) => {
  engine(on, { plugins: BOTH, target: fixture })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'target-toggle' })
  const open = await all(pane)
  expect(open).toContain('Road A One project key: crosses off P7, unlocks P9. PM tool off 8 → 7, Accounting off no change')
  expect(open).toContain('Hide the full map')
  await pane.press({ key: 'target-toggle' })
  expect(await all(pane)).not.toContain('Road A One project key')

  const desktop = await $.ui.mount(PANE('desktop') as never)
  await (desktop as any).press({ key: 'target-toggle' })
  expect(await all(desktop as never)).toContain('Decisions you own')
  await settle()
})

test('a missing status file is one line', async ($, on) => {
  engine(on, { plugins: BOTH })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  const text = await all(pane)
  expect(MISSING).toBe('No target map yet. Run node scripts/target-map-status.mjs in BLDG OS.')
  expect(text).toContain(MISSING)
  expect(text).not.toContain('target-toggle')
  await settle()
})

test('work that matches a map job shows a crosses-off pill, and the decisions you own sit under the next move', async ($, on) => {
  engine(on, { plugins: BOTH, target: fixture })
  await $.session.start(START)
  await $.tool.call({ tool: 'mcp__build-guide__task_create', subject: 'Add daily reports to the field app' })
  await $.tool.call({ tool: 'mcp__build-guide__task_update', taskId: '1', status: 'in_progress' })
  await settle()
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  const text = await all(pane)
  expect(text).toContain('Crosses off P3 daily reports')
  expect(text).toContain('Decisions you own')
  expect(text).toContain('Option A or B for the project key')
  await settle()
})

test('the crosses-off matcher: a job id or every word of a job name, never a job already moved', () => {
  expect(crossesOff(fixture, ['mattnicosia/p7-one-key']).map(j => j.id)).toEqual(['P7'])
  expect(crossesOff(fixture, ['Move AP bills into BLDG OS']).map(j => j.id)).toEqual(['Q2'])
  expect(crossesOff(fixture, ['Wire up RFIs']).map(j => j.id)).toEqual([])
  expect(crossesOff(fixture, ['P10 is not P1x']).map(j => j.id)).toEqual([])
  expect(crossesOff(fixture, ['Tidy the README']).map(j => j.id)).toEqual([])
})
