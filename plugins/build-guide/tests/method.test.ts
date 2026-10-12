import { expect, test } from 'claude-code/testing'

import { all, COMPOSER, engine, PANE, POCOCK, PSTACK, settle, START } from './engine'

test('a session starts on pstack where pstack is installed, and the switch moves to pocock and remembers it', async ($, on) => {
  const { store, seen } = engine(on, { plugins: [...PSTACK, ...POCOCK] })
  await $.session.start(START)
  expect(seen.opened).toBe(1)
  expect(seen.tools).toEqual(['task_create', 'task_update'])
  const pane = await $.ui.mount(PANE())
  expect(await all(pane)).toContain('Assess the project')
  await pane.press({ key: 'tab-guide' })
  expect(await all(pane)).toContain('Router')

  await pane.press({ key: 'method-pocock' })
  expect(store.method).toBe('pocock')
  const text = await all(pane)
  expect(text).toContain('Main path')
  expect(text).not.toContain('Router')
  await pane.press({ key: 'tab-start' })
  expect(await all(pane)).toContain('I have an idea')
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

test('/mod-guide with a method name switches to it', async ($, on) => {
  const { store } = engine(on, { plugins: [...PSTACK, ...POCOCK] })
  await $.session.start(START)
  const said = await $.command.run({ command: 'mod-guide', args: 'pocock', ...COMPOSER })
  expect(said.text).toBe('Build guide opened on pocock.')
  expect(store.method).toBe('pocock')
  await settle()
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: each method draws its own decision card, and a press sends the key`, async ($, on) => {
    const { seen } = engine(on, {
      plugins: [...PSTACK, ...POCOCK],
      model:
        '{"done":"Wrote the spec.","next":"Pick one.","isWaiting":true,"isChoice":true,"question":"Which ticket first?","options":[{"key":"A","label":"Version changes on refresh","tier":"Opus 5.5 - High"},{"key":"B","label":"Huge number blanks totals","tier":""}],"pick":"B","why":"One keystroke wipes every total."}',
    })
    await $.session.start(START)
    const answer = 'A. The version changes by itself.\nB. A very large number blanks every total.\n\nReply with a letter.'
    await $.turn.complete({ answer, durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as never)
    await settle()
    const pane = await $.ui.mount(PANE(surface) as never)
    const pstack = await all(pane as never)
    if (surface === 'desktop') {
      expect(pstack).toContain('DECISION WAITING')
      expect(pstack).toContain('★ pstack pick')
      expect(pstack).toContain('Opus 5.5 - High')
    } else {
      expect(pstack).toContain('Decision waiting: Which ticket first?')
      expect(pstack).toContain('pstack pick: Huge number blanks totals')
    }

    await (pane as any).press({ key: 'method-pocock' })
    const pocock = await all(pane as never)
    expect(pocock).toContain(surface === 'desktop' ? 'CLAUDE IS ASKING YOU' : 'Claude is asking you: Which ticket first?')
    expect(pocock).toContain(surface === 'desktop' ? '★ what the flow suggests' : 'what the flow suggests: Huge number blanks totals')
    await (pane as any).press({ key: 'choose-B' })
    expect(seen.sent.at(-1)).toBe('B')
    await settle()
  })
}

test('a finished turn leaves a summary with PR links, and a waiting one offers the method’s own plain-words reply', async ($, on) => {
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

  await (pane as any).press({ key: 'method-pocock' })
  await (pane as any).press({ key: 'reply-plain' })
  expect(seen.ran.at(-1)).toBe('/wait-what')

  await $.prompt.submit({ text: 'looks good' } as never)
  expect(await all(pane as never)).toContain('Last turn')
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
