import { expect, test } from 'claude-code/testing'

import { all, COMPOSER, engine, md, PANE, POCOCK, settle, START } from './engine'

test('the strip follows the skills, Next step offers only what the flow allows, and /implement covers review', async ($, on) => {
  engine(on)
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  expect(await md(pane)).toContain('Nothing started yet')
  expect(await md(pane)).toContain('**Next step:** Grill your idea: `/grill-with-docs`')

  await $.skill.prompt({ skill: 'mattpocock-skills:grill-with-docs', text: 'x' })
  expect(await md(pane)).toContain('**[Grill]** → Spec')
  expect(await md(pane)).toContain('**Next step:** Write the spec: `/to-spec`')
  expect(await md(pane)).toContain('Keep grilling, spec and tickets in this one chat')

  await $.tool.call({ tool: 'Skill', skill: 'to-spec' })
  await $.command.run({ command: 'to-tickets', args: '', ...COMPOSER })
  expect(await md(pane)).toContain('**Next step:** Build the first ticket')
  expect(await md(pane)).toContain('Clear the chat before each ticket')

  await $.skill.prompt({ skill: 'implement', text: 'x' })
  const built = await md(pane)
  expect(built).toContain('✓Build → **[Review]**')
  expect(built).toContain('**Next step:** Open the pull request')
  // A step under way offers the shared quick replies, with /wait-what as the plain-words one.
  expect(await all(pane)).toContain('Show me the evidence')
  await settle()
})

test('skipping the grill shows why it matters, and a bug fix does not count as a skip', async ($, on) => {
  engine(on)
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  await $.skill.prompt({ skill: 'tdd', text: 'x' })
  expect(await md(pane)).toContain('**You skipped Grill.** Code built on a fuzzy idea gets rebuilt.')
  expect(await md(pane)).toContain('**Next step:** Review the change')

  await pane.press({ key: 'reset' })
  await $.skill.prompt({ skill: 'diagnosing-bugs', text: 'x' })
  expect(await md(pane)).not.toContain('You skipped')
  await settle()
})

test('a build request before any grilling gets a nudge card and a note for the model, and nothing is blocked', async ($, on) => {
  const { seen } = engine(on)
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await $.prompt.submit({ text: 'add a dark mode toggle to settings', wait: false, origin: { kind: 'composer' } })
  expect(seen.sent[0]).toBe('add a dark mode toggle to settings')
  expect(seen.context.join(' ')).toContain('suggesting they run /grill-with-docs first')
  expect(await all(pane)).toContain('Grill it first?')
  await pane.press({ key: 'nudge-go' })
  expect(seen.filled[0]).toBe('/grill-with-docs add a dark mode toggle to settings')

  await $.prompt.submit({ text: 'the login page crashes on submit', wait: false, origin: { kind: 'composer' } })
  expect(await all(pane)).toContain('Sounds like something is broken')

  await $.prompt.submit({ text: 'how does the login page work?', wait: false, origin: { kind: 'composer' } })
  expect(await all(pane)).not.toContain('Sounds like something is broken')

  await $.skill.prompt({ skill: 'grill-with-docs', text: 'x' })
  const before = seen.context.length
  await $.prompt.submit({ text: 'add the toggle now', wait: false, origin: { kind: 'composer' } })
  expect(seen.context.length).toBe(before)
  await settle()
})

test('Not this time turns the nudge off for the session', async ($, on) => {
  const { seen } = engine(on)
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await $.prompt.submit({ text: 'add a dark mode toggle to settings', wait: false, origin: { kind: 'composer' } })
  await pane.press({ key: 'nudge-off' })
  expect(await all(pane)).not.toContain('Grill it first?')
  const before = seen.context.length
  await $.prompt.submit({ text: 'add a light mode toggle too', wait: false, origin: { kind: 'composer' } })
  expect(seen.context.length).toBe(before)
  await settle()
})

test('the pstack method sends no beginner nudges', async ($, on) => {
  const { seen } = engine(on, { plugins: ['pstack@pstack-claude', ...POCOCK] })
  await $.session.start(START)
  await $.prompt.submit({ text: 'add a dark mode toggle to settings', wait: false, origin: { kind: 'composer' } })
  expect(seen.context).toEqual([])
  await settle()
})

test('the word exception alone is not a bug report', async ($, on) => {
  const { seen } = engine(on)
  await $.session.start(START)
  await $.prompt.submit({ text: 'yes add the exception line', wait: false, origin: { kind: 'composer' } })
  expect(seen.context.join(' ')).not.toContain('/diagnosing-bugs')
  await $.prompt.submit({ text: 'saving the form throws an exception', wait: false, origin: { kind: 'composer' } })
  expect(seen.context.join(' ')).toContain('/diagnosing-bugs')
  await settle()
})

test('without the skills installed, the Start tab shows how to install them and hides the skill buttons', async ($, on) => {
  engine(on, { plugins: [] })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  const text = await all(pane)
  expect(text).toContain("Matt Pocock's skills not installed")
  expect(text).toContain('claude plugin install matt-pocock@bldg-skills')
  expect(text).toContain('Catch me up')
  expect(text).not.toContain('I have an idea')
  await settle()
})

test('the official marketplace copy counts as installed but out of date, so the card points at the mirror', async ($, on) => {
  engine(on, { plugins: ['mattpocock-skills@claude-plugins-official'] })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  const text = await all(pane)
  expect(text).toContain('your copy is out of date')
  expect(text).toContain('claude plugin install matt-pocock@bldg-skills')
  expect(text).toContain('claude plugin uninstall mattpocock-skills')
  expect(text).toContain('I have an idea')
  await settle()
})

test('the mirror next to the official copy is not out of date', async ($, on) => {
  engine(on, { plugins: ['mattpocock-skills@claude-plugins-official', ...POCOCK] })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  expect(await all(pane)).not.toContain('out of date')
  await settle()
})

test('a repo that is not set up offers Set up this repo first', async ($, on) => {
  const { seen } = engine(on, { isSetUp: false })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'refresh' })
  expect(await all(pane)).toContain('This repo is not set up')
  await pane.press({ key: 'start-setup' })
  expect(seen.ran.at(-1)).toBe('/setup-matt-pocock-skills')
  expect(seen.sent).toEqual([])
  await settle()
})

test('the flow is saved per repo, so a new session picks up where the last one stopped', async ($, on) => {
  const { store } = engine(on, {
    store: { 'pocock:/Users/me/dev/app': { root: '/Users/me/dev/app', done: ['grill', 'spec', 'tickets'], current: 'tickets', last: 'to-tickets', isBugFix: false } },
  })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'tab-now' })
  expect(await md(pane)).toContain('**[Tickets]**')
  await $.skill.prompt({ skill: 'implement', text: 'x' })
  expect((store['pocock:/Users/me/dev/app'] as { current: string }).current).toBe('review')
  await settle()
})

test('a PR with failing checks offers Fix the checks, and a ready one offers only a review while the guard is on', async ($, on) => {
  const green = [{ status: 'COMPLETED', conclusion: 'SUCCESS' }]
  engine(on, {
    prs: [
      { number: 7, title: 'Login form', isDraft: false, statusCheckRollup: [{ status: 'COMPLETED', conclusion: 'FAILURE' }], mergeable: 'MERGEABLE' },
      { number: 8, title: 'Dark mode', isDraft: false, statusCheckRollup: green, mergeable: 'MERGEABLE', reviewDecision: '' },
    ],
  })
  await $.session.start(START)
  const pane = await $.ui.mount(PANE())
  await pane.press({ key: 'refresh' })
  const text = await all(pane)
  expect(text).toContain('PR #7 · checks failing')
  expect(text).toContain('Fix the checks')
  expect(text).toContain('PR #8 · ready to merge')
  expect(text).not.toContain('Merge it')
  await settle()
})

const BLOCKED = [
  ['git push --force origin feature/login', 'git push --force'],
  ['git -C /Users/me/dev/app push -f', 'git push --force'],
  ['git push origin +feature/login', 'git push --force'],
  ['git push origin main', 'git push to main'],
  ['git push origin HEAD:main', 'git push to main'],
  ['git push', 'git push to main'],
  ['cd /Users/me/dev/app && git reset --hard HEAD~1', 'git reset --hard'],
  ['git clean -fd', 'git clean -f'],
  ['git branch -D old-idea', 'git branch -D'],
  ['git checkout -- .', 'git checkout .'],
  ['git restore .', 'git restore .'],
  ['gh pr merge 5 --squash', 'gh pr merge'],
] as const

const ALLOWED = [
  'git push -u origin feature/login',
  'git push origin feature/login:feature/login',
  'git restore --staged .',
  'git branch -d merged-idea',
  'git checkout -b feature/signup',
  'git status && git log --oneline -5',
  'echo "never run git push origin main"',
  'gh pr create --fill',
]

test('the git guard blocks destructive commands and says why', async ($, on) => {
  engine(on)
  await $.session.start(START)
  for (const [command, what] of BLOCKED) {
    const ran = JSON.stringify(await $.tool.call({ tool: 'Bash', command }))
    expect(ran).toContain(`build-guide blocked ${what}`)
  }
  await settle()
})

test('the git guard lets a beginner push a feature branch and open a PR', async ($, on) => {
  engine(on)
  await $.session.start(START)
  for (const command of ALLOWED) {
    const ran = JSON.stringify(await $.tool.call({ tool: 'Bash', command }))
    expect(ran).not.toContain('build-guide blocked')
  }
  await settle()
})

test('the git guard is off when gitGuard is false', { options: { gitGuard: false } }, async ($, on) => {
  engine(on)
  await $.session.start(START)
  const ran = JSON.stringify(await $.tool.call({ tool: 'Bash', command: 'gh pr merge 5 --squash' }))
  expect(ran).not.toContain('build-guide blocked')
  await settle()
})
