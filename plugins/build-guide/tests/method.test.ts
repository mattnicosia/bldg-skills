import { expect, test } from 'claude-code/testing'

import { all, COMPOSER, engine, PANE, POCOCK, PSTACK, settle, START } from './engine'

test('the Guide tab picks the method it shows, the Start tab follows the pick, and the pick is remembered', async ($, on) => {
  const { store, seen } = engine(on, { plugins: [...PSTACK, ...POCOCK] })
  await $.session.start(START)
  expect(seen.opened).toBe(1)
  expect(seen.tools).toEqual(['task_create', 'task_update'])
  const pane = await $.ui.mount(PANE())
  const start = await all(pane)
  expect(start).toContain('Assess the project')
  // No method switch above the tabs any more.
  expect(start).not.toContain('"key":"pick-pocock"')

  await pane.press({ key: 'tab-guide' })
  const guide = await all(pane)
  expect(guide).toContain('Router')
  expect(guide).toContain('"key":"pick-pstack"')

  await pane.press({ key: 'pick-pocock' })
  expect(store.method).toBe('pocock')
  const text = await all(pane)
  expect(text).toContain('Main path')
  expect(text).not.toContain('Router')
  await pane.press({ key: 'tab-start' })
  const after = await all(pane)
  expect(after).toContain('I have an idea')
  expect(after).toContain("These are pocock's starts")
  await settle()
})

test('a session starts on pocock where pstack is not installed', async ($, on) => {
  engine(on, { plugins: POCOCK })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  const text = await all(pane)
  expect(text).toContain('I have an idea')
  expect(text).not.toContain('Assess the project')
  await settle()
})

test('a method picked in an earlier session wins over the one detected', async ($, on) => {
  engine(on, { plugins: [...PSTACK, ...POCOCK], store: { method: 'pocock' } })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  expect(await all(pane)).toContain('I have an idea')
  await settle()
})

test('/mod-guide with a method name sets the Guide tab picker', async ($, on) => {
  const { store } = engine(on, { plugins: [...PSTACK, ...POCOCK] })
  await $.session.start(START)
  const said = await $.command.run({ command: 'mod-guide', args: 'pocock', ...COMPOSER })
  expect(said.text).toBe('Build guide opened. The Guide tab shows pocock.')
  expect(store.method).toBe('pocock')
  await settle()
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: a decision card speaks for both methods, and a press sends the key`, async ($, on) => {
    const { seen } = engine(on, {
      plugins: [...PSTACK, ...POCOCK],
      model:
        '{"done":"Wrote the spec.","next":"Pick one.","isWaiting":true,"isChoice":true,"question":"Which ticket first?","options":[{"key":"A","label":"Version changes on refresh","tier":"Opus 5.5 - High"},{"key":"B","label":"Huge number blanks totals","tier":""}],"pick":"B","why":"One keystroke wipes every total."}',
    })
    await $.session.start(START)
    const answer = 'A. The version changes by itself.\nB. A very large number blanks every total.\n\nReply with a letter.'
    await $.turn.complete({ answer, durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as never)
    await settle()
    expect(seen.asked.at(-1)).toContain('the pstack method and Matt Pocock')
    const pane = await $.ui.mount(PANE(surface) as never)
    await (pane as any).press({ key: 'tab-now' })
    const text = await all(pane as never)
    if (surface === 'desktop') {
      expect(text).toContain('DECISION WAITING')
      expect(text).toContain('★ suggested pick')
      expect(text).toContain('Opus 5.5 - High')
    } else {
      expect(text).toContain('Decision waiting: Which ticket first?')
      expect(text).toContain('suggested pick: Huge number blanks totals')
    }
    await (pane as any).press({ key: 'choose-B' })
    expect(seen.sent.at(-1)).toBe('B')
    await settle()
  })
}

test('a finished turn leaves a summary with PR links, and a waiting one offers a plain-words reply', async ($, on) => {
  const { seen } = engine(on, {
    plugins: [...PSTACK, ...POCOCK],
    model: '{"done":"Opened the PR for the deploy 404 fixes.","next":"Review the PR, then say merge.","isWaiting":true,"isChoice":false}',
  })
  await $.session.start(START)
  const answer = `I opened https://github.com/acme/app/pull/91 with the four commits for tickets 05 and 11. ${'Detail. '.repeat(40)}Review it and tell me when to merge.`
  await $.turn.complete({ answer, durationMs: 1, isAborted: false, turnId: 't2', reason: 'answer' } as never)
  await settle()
  const pane = await $.ui.mount(PANE('desktop') as never)
  const text = await all(pane as never)
  expect(text).toContain('Needs you')
  expect(text).toContain('Opened the PR for the deploy 404 fixes.')
  expect(text).toContain('[PR #91](https://github.com/acme/app/pull/91)')
  expect(text).toContain('Yes, go ahead')
  await (pane as any).press({ key: 'reply-plain' })
  expect(seen.ran.at(-1)).toBe('/bro')

  await $.prompt.submit({ text: 'looks good' } as never)
  expect(await all(pane as never)).toContain('Last turn')
  await settle()
})

test('with only pocock installed, the plain-words reply is /wait-what', async ($, on) => {
  const { seen } = engine(on, { plugins: POCOCK, model: '{"done":"Asked a question.","next":"Answer it.","isWaiting":true,"isChoice":false}' })
  await $.session.start(START)
  await $.turn.complete({ answer: `${'Detail. '.repeat(40)}Do you want me to go on?`, durationMs: 1, isAborted: false, turnId: 't4', reason: 'answer' } as never)
  await settle()
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'reply-plain' })
  expect(seen.ran.at(-1)).toBe('/wait-what')
  await settle()
})

test('a short reply is its own summary', async ($, on) => {
  engine(on, { plugins: PSTACK })
  await $.session.start(START)
  await $.turn.complete({ answer: 'Done. The test passes now.', durationMs: 1, isAborted: false, turnId: 't3', reason: 'answer' } as never)
  await settle()
  const pane = await $.ui.mount(PANE())
  expect(await all(pane)).toContain('Done. The test passes now.')
  await settle()
})
