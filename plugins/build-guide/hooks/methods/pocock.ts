// Matt Pocock's flow: grill, spec, tickets, build, review, PR, retro.

import type { Flow, Nudge, PocockState, PullRequest, StepId } from '../../types'
import { C, chip, chips, chipW, doc, down, esc, inkOf, lines, noteCard, text, W, wrap, type Item } from '../draw'
import { fill, mergeAct, say, type Act, type Column, type GuidePage, type Method, type Move, type Out, type Section } from '../method'

const EMPTY_FLOW: Flow = { root: '', done: [], current: null, last: '', isBugFix: false }
const EMPTY: PocockState = { flow: EMPTY_FLOW, nudge: null }

// `now` is what the flow would have you do while on the step, when Haiku has not said.
type Step = { id: StepId; name: string; color: string; cmd: string; what: string; you: string; why: string; now: string }

const STEPS: Step[] = [
  {
    id: 'grill',
    name: 'Grill',
    color: C.blue,
    cmd: '/grill-with-docs',
    what: 'Claude asks you questions about the idea, one round at a time, until it has no gaps.',
    you: 'Answer each question. Say "I don\'t know" when you don\'t, and Claude will look it up.',
    why: 'Code built on a fuzzy idea gets rebuilt. Ten minutes of questions first is the cheapest fix there is.',
    now: "Keep answering Claude's questions until the idea has no gaps left.",
  },
  {
    id: 'spec',
    name: 'Spec',
    color: C.indigo,
    cmd: '/to-spec',
    what: 'Claude turns the grilling into one written plan and files it on the issue tracker.',
    you: 'Read it. Ask for changes now, while they cost nothing.',
    why: 'Without a written plan, each new chat starts from a guess about what you meant.',
    now: "Read the spec on the tracker and ask for changes before any code exists.",
  },
  {
    id: 'tickets',
    name: 'Tickets',
    color: C.purple,
    cmd: '/to-tickets',
    what: 'Claude cuts the spec into small tickets. Each one works end to end and says which tickets go first.',
    you: 'Check the order makes sense, and that each ticket is small enough for one chat.',
    why: 'A big job in one chat runs out of room. Small tickets each get a fresh, sharp chat.',
    now: "Check the tickets are small and in order, then clear the chat for the first one.",
  },
  {
    id: 'build',
    name: 'Build',
    color: C.orange,
    cmd: '/implement',
    what: 'Claude builds it test-first: a test that fails, then the code that makes it pass.',
    you: 'Watch the tests go red, then green. Clear the chat before each new ticket.',
    why: 'A test written first proves the code does the job, now and after every later change.',
    now: "Watch the test fail, then pass. Stay on this one ticket.",
  },
  {
    id: 'review',
    name: 'Review',
    color: C.green,
    cmd: '/code-review',
    what: "Two reviewers check the change: does it follow the repo's rules, and does it do what was asked.",
    you: 'Read both lists. Ask Claude to fix the ones that matter.',
    why: 'Mistakes are cheap to fix before a pull request and expensive after it ships.',
    now: "Read both review lists and have Claude fix the findings that matter.",
  },
  {
    id: 'pr',
    name: 'PR',
    color: C.teal,
    cmd: '/pr',
    what: 'Claude opens a pull request with a picture of the change and proof that it works.',
    you: 'Read it, then share the link with whoever reviews your work.',
    why: 'A pull request is how someone else checks the work before it joins the main code.',
    now: "Read the pull request, then send the link to whoever reviews your work.",
  },
  {
    id: 'retro',
    name: 'Retro',
    color: C.pink,
    cmd: '/retro',
    what: 'Claude looks back at the session and suggests changes to the setup, so the next build goes better.',
    you: 'Pick which suggestions to keep. Run it before you clear the chat.',
    why: 'Each retro turns a mistake into a check or a rule, so it does not happen twice.',
    now: "Keep the setup changes worth keeping, then start the next idea.",
  },
]

const ORDER: StepId[] = STEPS.map(s => s.id)
const stepOf = (id: StepId) => STEPS.find(s => s.id === id) ?? STEPS[0]!

const SKILL_STEP: Record<string, StepId> = {
  'grill-with-docs': 'grill',
  'grill-me': 'grill',
  grilling: 'grill',
  'domain-modeling': 'grill',
  prototype: 'grill',
  wayfinder: 'grill',
  'to-spec': 'spec',
  'to-tickets': 'tickets',
  triage: 'tickets',
  implement: 'build',
  'implement-spec': 'build',
  tdd: 'build',
  'diagnosing-bugs': 'build',
  'code-review': 'review',
  pr: 'pr',
  retro: 'retro',
}

// /implement and /implement-spec run /code-review themselves, so they finish two steps.
const REVIEWS_ITSELF = new Set(['implement', 'implement-spec'])

export const advance = (f: Flow, name: string, step: StepId): Flow => {
  const isFresh = step === 'grill' && (f.current === 'pr' || f.current === 'retro')
  const base = isFresh ? { ...f, done: [], isBugFix: false } : f
  const reached: StepId[] = REVIEWS_ITSELF.has(name) ? [step, 'review'] : [step]
  const done = ORDER.filter(s => base.done.includes(s) || reached.includes(s))
  return { ...base, done, current: reached.at(-1) ?? step, last: name, isBugFix: base.isBugFix || name === 'diagnosing-bugs' }
}

// A step left out on the way to where you are. Spec and tickets are optional for a
// small job, and a bug fix starts at Build, so only these two count.
const skippedOf = (f: Flow): StepId[] => {
  if (!f.current) return []
  const at = ORDER.indexOf(f.current)
  const out: StepId[] = []
  if (!f.isBugFix && at >= ORDER.indexOf('build') && !f.done.includes('grill')) out.push('grill')
  if (at >= ORDER.indexOf('pr') && f.done.includes('build') && !f.done.includes('review')) out.push('review')
  return out
}

type FlowMove = Act & { why: string }

const NEXT_TICKET: FlowMove = { key: 'move-next-ticket', label: 'Build the next ticket', text: '/implement ', why: 'Clear the chat first, then add the ticket number after /implement.' }
const CLEAR: FlowMove = { key: 'move-clear', label: 'Clear the chat', text: '/clear', why: 'Empties the chat so the next ticket starts fresh.' }

// Next step only offers what the flow allows from where you are. Each fills the
// prompt, so Enter is the go.
const nextFor = (f: Flow): { main: FlowMove; others: FlowMove[] } => {
  const hasTickets = f.done.includes('tickets')
  switch (f.current) {
    case null:
      return {
        main: { key: 'move-grill', label: 'Grill your idea', text: '/grill-with-docs ', why: 'Type your idea after the command in your own words. Rough is fine.' },
        others: [{ key: 'move-bug', label: 'Something is broken instead', text: '/diagnosing-bugs ', why: '' }],
      }
    case 'grill':
      return {
        main: { key: 'move-spec', label: 'Write the spec', text: '/to-spec', why: 'Do this in the same chat, so the spec builds on the whole grilling.' },
        others: [
          { key: 'move-small', label: 'Small job? Build it here', text: '/implement what we just agreed', why: '' },
          { key: 'move-prototype', label: 'Need to see it run first?', text: '/handoff I want to answer this with a throwaway prototype: <the question>', why: '' },
        ],
      }
    case 'spec':
      return { main: { key: 'move-tickets', label: 'Cut it into tickets', text: '/to-tickets', why: 'Stay in this chat. Clear it only after the tickets exist.' }, others: [] }
    case 'tickets':
      return {
        main: { key: 'move-build', label: 'Build the first ticket', text: '/implement ', why: 'Clear the chat first. Then add the first ticket after /implement.' },
        others: [CLEAR, { key: 'move-all', label: 'Build every ticket in one run', text: '/implement-spec', why: '' }],
      }
    case 'build':
      return { main: { key: 'move-review', label: 'Review the change', text: '/code-review since main', why: 'Two reviewers read the diff before anyone else sees it.' }, others: [] }
    case 'review':
      return {
        main: { key: 'move-pr', label: 'Open the pull request', text: 'open a pull request for this branch. use /pr to write the body.', why: 'It shows the change and the proof that it works.' },
        others: hasTickets ? [CLEAR, NEXT_TICKET] : [],
      }
    case 'pr':
      return { main: { key: 'move-retro', label: 'Look back with a retro', text: '/retro', why: 'Run it now, before you clear the chat, so it can see the whole session.' }, others: hasTickets ? [CLEAR, NEXT_TICKET] : [] }
    case 'retro':
      return { main: { key: 'move-again', label: 'Start the next idea', text: '/grill-with-docs ', why: 'The path starts over at Grill.' }, others: hasTickets ? [CLEAR, NEXT_TICKET] : [] }
  }
}

const hintFor = (f: Flow) => {
  if (f.current === 'grill' || f.current === 'spec') return 'Keep grilling, spec and tickets in this one chat. Do not clear or compact until the tickets exist.'
  if (f.current === 'tickets' || (f.done.includes('tickets') && f.current !== null)) return 'Clear the chat before each ticket. The ticket holds everything Claude needs.'
  return ''
}

// ---------- Now: where you are on the path ----------

const NUDGE_TEXT: Record<NonNullable<Nudge>['kind'], Section> = {
  grill: { title: 'Grill it first?', body: 'You asked for code before any grilling. A few minutes of questions now saves a rebuild later.', tone: 'warn' },
  bug: { title: 'Sounds like something is broken', body: '/diagnosing-bugs finds a command that shows the bug failing, then fixes it with a test.', tone: 'warn' },
}

const column = (s: PocockState, would: string | undefined): Column => {
  const f = s.flow
  const at = f.current ? ORDER.indexOf(f.current) : -1
  const skipped = skippedOf(f)
  const step = f.current ? stepOf(f.current) : null
  const sections: Section[] = []
  if (s.nudge) sections.push(NUDGE_TEXT[s.nudge.kind])
  if (step) sections.push({ title: 'What it is', body: step.what }, { title: 'What you do', body: step.you })
  else sections.push({ title: 'Every job starts with an idea', body: 'Grill it in plain words. Claude asks questions until it is clear, then you build it step by step.' })
  for (const id of skipped) sections.push({ title: `You skipped ${stepOf(id).name}`, body: stepOf(id).why, tone: 'warn' })
  const hint = hintFor(f)
  if (hint) sections.push({ title: 'Keep the chat clean', body: hint })
  return {
    stage: step ? `Step ${at + 1} of 7 · ${step.name}` : 'Not started',
    title: step ? `${step.name} · ${step.cmd}` : 'No step yet',
    rows: STEPS.map(x => ({
      label: x.name,
      mark: x.id === f.current ? 'now' : skipped.includes(x.id) ? 'skipped' : f.done.includes(x.id) ? 'done' : 'todo',
      tag: x.id === f.current ? x.cmd : undefined,
    })),
    sections,
    would: would ?? step?.now ?? 'Grill the idea with /grill-with-docs before any code is written.',
  }
}

const nextOf = (s: PocockState): Move => {
  // A request for code before any grilling makes grilling it the next move.
  if (s.nudge) {
    const cmd = s.nudge.kind === 'bug' ? '/diagnosing-bugs' : '/grill-with-docs'
    return { label: s.nudge.kind === 'bug' ? 'Diagnose it first' : 'Grill it first', text: `${cmd} ${s.nudge.text}`, why: NUDGE_TEXT[s.nudge.kind].body }
  }
  const next = nextFor(s.flow).main
  return { label: next.label, text: next.text ?? '', why: next.why }
}

// ---------- Guide pages ----------

const flowSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'From idea to shipped')
  b += text(20, 54, 'sub mut', 'Seven steps, in order. Each one has a skill you run.')
  let y = 72
  const card = (s: Step, i: number) => {
    const what = wrap(s.what, 56)
    const h = 40 + what.length * 16 + 6
    let svg = `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${h}" rx="10"/>`
    svg += `<circle cx="40" cy="${y + 22}" r="13" fill="${s.color}"/>`
    svg += `<text x="40" y="${y + 26.5}" text-anchor="middle" fill="#fff" font-size="12.5" font-weight="700">${i + 1}</text>`
    svg += text(62, y + 27, 'lab ink', s.name, ' font-size="14.5"')
    svg += chip(W - 28 - chipW({ label: s.cmd, tip: '' }), y + 10, { label: s.cmd, tip: s.what }, s.color)
    svg += lines(62, y + 48, 'body mut', what, 16)
    return { svg, h }
  }
  const side = (title: string, body: string, color: string) => {
    const rows = wrap(body, 60)
    const h = 26 + rows.length * 15 + 8
    const svg =
      `<rect x="44" y="${y}" width="${W - 60}" height="${h}" rx="9" fill="${color}" fill-opacity=".08" stroke="${color}" stroke-opacity=".5" stroke-dasharray="4 3"/>` +
      `<text x="58" y="${y + 18}" font-size="12" font-weight="700" fill="${inkOf(color)}">${esc(title)}</text>` +
      lines(58, y + 35, 'sm ink', rows, 15)
    return { svg, h }
  }
  const band = (label: string, color: string) => {
    b += `<rect x="16" y="${y}" width="${W - 32}" height="26" rx="13" fill="${color}" fill-opacity=".14"/>`
    b += `<text x="${W / 2}" y="${y + 17.5}" text-anchor="middle" font-size="12" font-weight="700" fill="${inkOf(color)}">${esc(label)}</text>`
    y += 26 + 10
  }
  band('Steps 1 to 3: one chat, no clearing', C.blue)
  STEPS.forEach((s, i) => {
    if (i === 3) band('Clear the chat before each ticket', C.purple)
    const c = card(s, i)
    b += c.svg
    y += c.h + 6
    if (s.id === 'grill') {
      b += down(W / 2, y)
      y += 12
      const d = side('Stuck on a question only running code can answer?', '/handoff out, /prototype a throwaway answer in a new chat, then /handoff back what you learned.', C.blue)
      b += d.svg
      y += d.h + 6
      const small = side('Small job that fits in one chat?', 'Skip spec and tickets. Run /implement right after grilling.', C.orange)
      b += small.svg
      y += small.h + 6
    }
    if (i < STEPS.length - 1) {
      b += down(W / 2, y)
      y += 14
    }
  })
  y += 14
  b += text(20, y, 'sm mut', 'Hover a command to see what it does.')
  return doc(y + 16, b)
}

const RAMPS: { when: string; cmd: string; what: string; joins: StepId }[] = [
  { when: 'Something is broken', cmd: '/diagnosing-bugs', what: 'Finds a command that shows the bug failing, then fixes it with a test.', joins: 'build' },
  { when: 'Bugs and requests piling up', cmd: '/triage', what: 'Sorts issues other people filed into clear tickets an agent can take.', joins: 'tickets' },
  { when: 'A huge project, too big to see', cmd: '/wayfinder', what: 'Maps the big decisions as tickets and settles them one by one.', joins: 'spec' },
  { when: 'The code is getting messy', cmd: '/improve-codebase-architecture', what: 'Finds parts of the code worth reshaping. Picking one gives you an idea.', joins: 'grill' },
]

const rampsSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'Other ways in')
  b += text(20, 54, 'sub mut', 'Not every job starts with an idea. These join the path partway.')
  let y = 72
  for (const r of RAMPS) {
    const s = stepOf(r.joins)
    const what = wrap(r.what, 58)
    const h = 74 + what.length * 16
    b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${h}" rx="10"/>`
    b += text(30, y + 24, 'lab ink', r.when, ' font-size="14.5"')
    b += chip(30, y + 34, { label: r.cmd, tip: r.what }, C.slate)
    b += lines(30, y + 76, 'body mut', what, 16)
    const label = `joins at ${s.name}`
    const lw = label.length * 6.6 + 22
    b += `<rect x="${W - 28 - lw}" y="${y + 10}" width="${lw}" height="22" rx="11" fill="${s.color}"/>`
    b += `<text x="${W - 28 - lw / 2}" y="${y + 25}" text-anchor="middle" fill="#fff" font-size="11.5" font-weight="700">${esc(label)}</text>`
    y += h + 10
  }
  y += 8
  const pre = noteCard(y, 'Before your first build in a repo', 'Run /setup-matt-pocock-skills once. It tells the other skills where tickets live and where to write the glossary.', C.red)
  b += pre.svg
  y += pre.h
  return doc(y + 16, b)
}

const ANYTIME: { name: string; color: string; items: Item[] }[] = [
  {
    name: 'Think it through',
    color: C.blue,
    items: [
      { label: '/grill-me', tip: 'The same interview as /grill-with-docs, for a plan with no repo. It saves nothing.' },
      { label: '/research', tip: 'A background agent reads the sources and leaves a cited notes file in the repo.' },
      { label: '/to-questionnaire', tip: 'Writes questions for someone else to answer, when the gap is in their head.' },
    ],
  },
  {
    name: 'Learn and ask',
    color: C.indigo,
    items: [
      { label: '/wait-what', tip: 'That last message did not land. Claude says it again, in plain words.' },
      { label: '/teach', tip: 'Learn a concept over several sessions, in this folder.' },
    ],
  },
  {
    name: 'Words and shape',
    color: C.purple,
    items: [
      { label: '/domain-modeling', tip: 'Sort out a fuzzy word, or record a hard-to-undo decision.' },
      { label: '/codebase-design', tip: 'Shape a part of the code: a lot of work behind a small, simple surface.' },
    ],
  },
  { name: 'Steps only you can do', color: C.orange, items: [{ label: '/wizard', tip: 'A script that walks you through keys, dashboards and secrets, and saves each value.' }] },
]

const BETWEEN: [string, string][] = [
  ['Continue', 'Stay in this chat. The safe first choice.'],
  ['/clear', 'Empty the chat when nothing in it matters next.'],
  ['/handoff', 'Write a file for a new folder, tool or person.'],
  ['Subagent', 'Send one small job to its own chat.'],
  ['/compact', 'Squeeze the chat when it gets long.'],
]

const moreSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'Skills for any time')
  b += text(20, 54, 'sub mut', 'Off the path. Use them whenever they help.')
  let y = 84
  for (const g of ANYTIME) {
    b += `<rect x="20" y="${y - 11}" width="4" height="14" rx="2" fill="${g.color}"/>`
    b += text(30, y, 'lab ink', g.name)
    const f = chips(20, y + 10, W - 16, g.items, g.color)
    b += f.svg
    y = f.bottom + 30
  }
  b += text(20, y, 'lab ink', 'Between two steps, pick one')
  b += text(20, y + 17, 'sm mut', 'Try them top to bottom. Stop at the first that fits.')
  y += 30
  b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${BETWEEN.length * 34 + 10}" rx="10"/>`
  BETWEEN.forEach(([k, v], i) => {
    const ry = y + 10 + i * 34
    b += `<rect x="28" y="${ry + 4}" width="86" height="22" rx="11" fill="${C.slate}" fill-opacity=".1"/>`
    b += `<text x="71" y="${ry + 19.5}" text-anchor="middle" font-size="12" font-weight="700" class="ink mono">${esc(k)}</text>`
    b += text(126, ry + 19.5, 'body ink', v)
  })
  y += BETWEEN.length * 34 + 10
  return doc(y + 18, b)
}

const WORDS: [string, string][] = [
  ['Grilling', "Claude asks you questions, one round at a time, until the idea has no gaps. Facts are Claude's job. Decisions are yours."],
  ['Spec', 'One written plan for the whole job, made from the grilling.'],
  ['Ticket', 'One small piece of the spec, small enough to build in one chat.'],
  ['Tracer bullet', 'A ticket that cuts a thin slice through every layer, from screen to data, so something works end to end early.'],
  ['Blocking edge', 'A note on a ticket that says which tickets must finish first.'],
  ['Red-green', 'Write a test that fails (red), then the code that makes it pass (green). One small slice at a time.'],
  ['Deep module', 'A part of the code that does a lot of work behind a small, simple surface.'],
  ['Context window', 'Everything Claude can see in this chat. /clear empties it.'],
  ['Smart zone', 'The first part of a chat, about 150k tokens, where Claude still thinks sharply. Past it, answers get worse.'],
  ['GLOSSARY.md', 'The file where grilling writes down the words you agreed on.'],
  ['ADR', 'A short note that records a decision that is hard to undo, and why it was made.'],
  ['Pull request', 'A request to add your branch to the main code, with proof it works, for someone to review.'],
]

const wordsSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'Words you will hear')
  b += text(20, 54, 'sub mut', 'Lost in a reply? Type /wait-what and Claude says it again.')
  let y = 70
  WORDS.forEach(([word, meaning], i) => {
    const rows = wrap(meaning, 60)
    const h = 36 + rows.length * 16
    const color = STEPS[i % STEPS.length]!.color
    b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${h}" rx="10"/>`
    b += `<rect x="28" y="${y + 13}" width="4" height="15" rx="2" fill="${color}"/>`
    b += text(40, y + 25, 'lab', word, ` fill="${inkOf(color)}" font-size="13.5"`)
    b += lines(40, y + 44, 'body ink', rows, 16)
    y += h + 8
  })
  return doc(y + 10, b)
}

const GUIDE: GuidePage[] = [
  {
    id: 'flow',
    label: 'Main path',
    svg: flowSvg(),
    alt: 'The seven steps from idea to shipped, with the skill for each',
    md: `### From idea to shipped\n\n${STEPS.map((s, i) => `${i + 1}. **${s.name}** \`${s.cmd}\`: ${s.what}`).join('\n')}\n\nKeep steps 1 to 3 in one chat. Clear the chat before each ticket.`,
    note: 'Press a step to put its command in your prompt.',
    rows: [{ acts: STEPS.map((s, i) => fill(`cmd-${s.id}`, `${i + 1} ${s.name}`, `${s.cmd} `)) }],
  },
  {
    id: 'ramps',
    label: 'Other ways in',
    svg: rampsSvg(),
    alt: 'Starting points that join the main path partway',
    md: `### Other ways in\n\n${RAMPS.map(r => `- **${r.when}**: \`${r.cmd}\`. ${r.what} Joins at ${stepOf(r.joins).name}.`).join('\n')}\n\nBefore your first build in a repo, run \`/setup-matt-pocock-skills\`.`,
    rows: [{ acts: RAMPS.map(r => fill(`ramp-${r.cmd}`, r.when, `${r.cmd} `)) }],
  },
  {
    id: 'more',
    label: 'Any time',
    svg: moreSvg(),
    alt: 'Skills you can use at any point, and what to do between steps',
    md: `### Skills for any time\n\n${ANYTIME.map(g => `**${g.name}:** ${g.items.map(i => `\`${i.label}\``).join(', ')}`).join('\n\n')}\n\n**Between two steps:** ${BETWEEN.map(([k, v]) => `${k} (${v})`).join(' ')}`,
  },
  {
    id: 'words',
    label: 'Words',
    svg: wordsSvg(),
    alt: 'Plain meanings for the words the skills use',
    md: `### Words you will hear\n\n${WORDS.map(([w, m]) => `- **${w}**: ${m}`).join('\n')}`,
  },
]

// ---------- Start ----------

const SETUP = say('start-setup', 'Set up this repo', '/setup-matt-pocock-skills')

const CATCH_UP = say(
  'start-catchup',
  'Catch me up',
  'catch me up in plain words for a beginner: what this repo does, what was built recently, any open branches or pull requests, and which step of the flow (grill, spec, tickets, build, review, PR, retro) the work is at. keep it short. end with a multiple-choice question of what to do next, with finishing open work first.',
)

const STARTS: Act[] = [
  { ...fill('start-idea', 'I have an idea', '/grill-with-docs '), isPrimary: true },
  fill('start-bug', 'Something is broken', '/diagnosing-bugs '),
  say(
    'start-ticket',
    'Pick up a ticket',
    "list this repo's open ready-for-agent tickets, using the issue tracker named in docs/agents/issue-tracker.md, and ask me to pick one with a multiple-choice question. when I pick, run /implement on it.",
  ),
  CATCH_UP,
]

const prActs = (pr: PullRequest, canMerge: boolean): Act[] => {
  const n = pr.number
  const review = fill(`review-${n}`, 'Review it', `/code-review pull request #${n} against its base branch`)
  switch (pr.stage) {
    case 'conflict':
      return [fill(`conflict-${n}`, 'Fix the conflict', `pull request #${n} conflicts with main. in its own worktree, rebase it onto main, resolve the conflict in plain words as you go, run the tests and push. don't merge.`)]
    case 'fail':
      return [fill(`fix-${n}`, 'Fix the checks', `pull request #${n} has failing checks. tell me why in plain words, then fix them test-first. don't merge.`)]
    case 'changes':
      return [fill(`changes-${n}`, 'Answer the review', `pull request #${n} has review comments asking for changes. read them, fix what is right test-first, reply to what is not, and push. don't merge.`)]
    case 'ready':
      return canMerge ? [mergeAct(n), review] : [review]
    default:
      return [review]
  }
}

// ---------- Grill before building ----------
// Shown in this method's column as advice. Nothing is blocked or sent.

const BUILD_ASK = /\b(build|add|implement|make|create|change|refactor|rewrite|update|wire up|hook up|code|feature|new (page|screen|button|endpoint|component))\b/i
const BUG_ASK = /\b(bug|broken|error|crash(es|ed|ing)?|fails?|failing|doesn'?t work|not working|uncaught exception|(throws?|threw|raises?|raised) (an? )?exception|exception (is |was )?(thrown|raised)|stack trace)\b/i
const QUESTION = /^(how|what|why|where|when|who|which|is|are|does|can you explain|explain|tell me)\b/i

export const nudgeFor = (prompt: string, f: Flow): Nudge => {
  const said = prompt.trim()
  if (!said || said.startsWith('/') || QUESTION.test(said)) return null
  // Only before the path starts, or once the last job ran its retro.
  if (f.current !== null && f.current !== 'retro') return null
  if (BUG_ASK.test(said)) return { text: said, kind: 'bug' }
  if (BUILD_ASK.test(said)) return { text: said, kind: 'grill' }
  return null
}

// ---------- Following the flow ----------

const nameOf = (raw: string) => raw.split(':').pop() ?? raw

// A skill of the flow moves it, and answers any open nudge.
const useSkill = (s: PocockState, raw: string): PocockState => {
  const name = nameOf(raw)
  const step = SKILL_STEP[name]
  if (!step) return s
  if (s.flow.last === name && s.flow.current === (REVIEWS_ITSELF.has(name) ? 'review' : step)) return s
  return { ...s, flow: advance(s.flow, name, step), nudge: null }
}

const explain = say('q-plain', 'Say it plainly', '/wait-what')

export const pocock: Method<PocockState> = {
  id: 'pocock',
  label: 'pocock',
  requires: {
    name: "Matt Pocock's skills",
    plugins: ['mattpocock-skills@', 'matt-pocock@'],
    skill: 'grill-with-docs',
    // The official marketplace pins a commit from before v1.3.1, so the mirror is the one to install.
    outdated: 'mattpocock-skills@claude-plugins-official',
    outdatedNote: 'The copy from the official marketplace is older than v1.3.1 and has no /implement-spec, /pr or /retro, which later steps need.',
    install: 'claude plugin marketplace add mattnicosia/bldg-skills && claude plugin install matt-pocock@bldg-skills',
    removeOld: 'claude plugin uninstall mattpocock-skills',
  },
  lead: '',
  starts: STARTS,
  plainStarts: [CATCH_UP],
  startNote: 'Idea and broken fill your prompt: type what you mean after the command, then press Enter. The others send at once.',
  setup: { file: 'docs/agents/issue-tracker.md', act: SETUP, warn: 'This repo is not set up for the skills yet. Press Set up this repo once, first.' },
  prActs,
  explain,
  after: [],
  decide: {
    who: "Matt Pocock's flow (grill the idea, write a spec, cut tickets, build test-first, review, open a PR, run a retro) with a beginner",
    favors: 'grill before building, a spec and tickets for anything bigger than one chat, a failing test before the fix, review before a PR, and finishing open work before starting new work.',
  },
  guide: GUIDE,

  empty: EMPTY,
  // The flow belongs to the repo, not the chat, so a cleared chat or a new
  // session in the same repo picks up where the last one stopped.
  persist: {
    rootOf: s => s.flow.root,
    save: s => s.flow,
    load: (s, saved, root) => {
      const f = saved as Flow | undefined
      return { ...s, flow: f && Array.isArray(f.done) ? { ...EMPTY_FLOW, ...f, root } : { ...EMPTY_FLOW, root } }
    },
  },

  stageOf: s => s.flow.current,
  moveTo: (s, stage) => {
    const step = ORDER.find(x => x === stage)
    return step ? { ...s, flow: { ...advance(s.flow, '', step), last: s.flow.last }, nudge: null } : s
  },
  brief: s => (s.flow.current ? `step ${stepOf(s.flow.current).name} (${stepOf(s.flow.current).cmd})` : 'not started, no idea grilled yet'),
  column,
  next: nextOf,
  phase: s => (s.flow.current !== null && s.flow.current !== 'retro' ? 'running' : 'idle'),
  reset: s => ({ ...s, flow: { ...EMPTY_FLOW, root: s.flow.root }, nudge: null }),
  isBusy: s => s.flow.current !== null,

  hooks: {
    command: (s, command, args) => ({ s: useSkill(s, command), args }),
    skill: (s, skill, text) => ({ s: useSkill(s, skill), text }),
    tool: (s, tool, args): Out<PocockState> => {
      let next = s
      if (tool === 'Skill' && typeof args.skill === 'string') next = useSkill(next, args.skill)
      if (tool === 'Bash' && typeof args.command === 'string' && /\bgh pr create\b/.test(args.command)) next = { ...next, flow: advance(next.flow, 'gh pr create', 'pr') }
      return { s: next }
    },
    // A request for code before any grilling shows in this column and nowhere else.
    prompt: (s, said, isPerson, hasSkills) => {
      const found = isPerson && hasSkills ? nudgeFor(said, s.flow) : null
      return { s: found ? { ...s, nudge: found } : s.nudge === null ? s : { ...s, nudge: null } }
    },
  },
}
