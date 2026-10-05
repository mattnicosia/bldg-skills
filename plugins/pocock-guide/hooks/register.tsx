import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Choice, Decision, Env, Flow, Nudge, PullRequest, Repo, StepId, Summary, Tab } from '../types'

const PANE = 'pocock-guide'
const TITLE = 'Pocock flow'

const tab = atom({ plugin: 'pocock-guide', key: 'tab' } as const, 'start' as Tab)
const EMPTY_FLOW: Flow = { root: '', done: [], current: null, last: '', isBugFix: false }
const flow = atom({ plugin: 'pocock-guide', key: 'flow' } as const, EMPTY_FLOW)
const nudge = atom({ plugin: 'pocock-guide', key: 'nudge' } as const, null as Nudge)
const env = atom({ plugin: 'pocock-guide', key: 'env' } as const, { isRead: false, hasSkills: true, isOutdated: false, hasPstackGuide: false } as Env)
const summary = atom({ plugin: 'pocock-guide', key: 'summary' } as const, null as Summary)
const decision = atom({ plugin: 'pocock-guide', key: 'decision' } as const, null as Decision)

const NO_REPO: Repo = { isRead: false, error: null, name: '', branch: '', dirty: 0, stale: [], worktrees: 0, prs: [], isSetUp: true }
const repo = atom({ plugin: 'pocock-guide', key: 'repo' } as const, NO_REPO)

const W = 460
const SANS = `-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Helvetica,Arial,sans-serif`
const MONO = `ui-monospace,'SF Mono',Menlo,Consolas,monospace`

// Apple's light palette: one vivid fill per step that carries white bold text,
// and a deeper ink of each for text on a tint.
const C = {
  grill: '#0071E3',
  spec: '#5E5CE6',
  tickets: '#AF52DE',
  build: '#F56300',
  review: '#1DA851',
  pr: '#0A9BC1',
  retro: '#E8335F',
  gray: '#8E8E93',
  red: '#E5342C',
  slate: '#48484A',
}

const INK: Record<string, string> = {
  [C.grill]: '#0058B0',
  [C.spec]: '#3F3DB8',
  [C.tickets]: '#8133A8',
  [C.build]: '#B54700',
  [C.review]: '#137A3A',
  [C.pr]: '#06708C',
  [C.retro]: '#B8163F',
  [C.gray]: '#5B5B60',
  [C.red]: '#B3261E',
  [C.slate]: '#1D1D1F',
}

// ---------- The flow ----------

type Step = { id: StepId; name: string; color: string; cmd: string; what: string; you: string; why: string }

const STEPS: Step[] = [
  {
    id: 'grill',
    name: 'Grill',
    color: C.grill,
    cmd: '/grill-with-docs',
    what: 'Claude asks you questions about the idea, one round at a time, until it has no gaps.',
    you: 'Answer each question. Say "I don\'t know" when you don\'t, and Claude will look it up.',
    why: 'Code built on a fuzzy idea gets rebuilt. Ten minutes of questions first is the cheapest fix there is.',
  },
  {
    id: 'spec',
    name: 'Spec',
    color: C.spec,
    cmd: '/to-spec',
    what: 'Claude turns the grilling into one written plan and files it on the issue tracker.',
    you: 'Read it. Ask for changes now, while they cost nothing.',
    why: 'Without a written plan, each new chat starts from a guess about what you meant.',
  },
  {
    id: 'tickets',
    name: 'Tickets',
    color: C.tickets,
    cmd: '/to-tickets',
    what: 'Claude cuts the spec into small tickets. Each one works end to end and says which tickets go first.',
    you: 'Check the order makes sense, and that each ticket is small enough for one chat.',
    why: 'A big job in one chat runs out of room. Small tickets each get a fresh, sharp chat.',
  },
  {
    id: 'build',
    name: 'Build',
    color: C.build,
    cmd: '/implement',
    what: 'Claude builds it test-first: a test that fails, then the code that makes it pass.',
    you: 'Watch the tests go red, then green. Clear the chat before each new ticket.',
    why: 'A test written first proves the code does the job, now and after every later change.',
  },
  {
    id: 'review',
    name: 'Review',
    color: C.review,
    cmd: '/code-review',
    what: 'Two reviewers check the change: does it follow the repo\'s rules, and does it do what was asked.',
    you: 'Read both lists. Ask Claude to fix the ones that matter.',
    why: 'Mistakes are cheap to fix before a pull request and expensive after it ships.',
  },
  {
    id: 'pr',
    name: 'PR',
    color: C.pr,
    cmd: '/pr',
    what: 'Claude opens a pull request with a picture of the change and proof that it works.',
    you: 'Read it, then share the link with whoever reviews your work.',
    why: 'A pull request is how someone else checks the work before it joins the main code.',
  },
  {
    id: 'retro',
    name: 'Retro',
    color: C.retro,
    cmd: '/retro',
    what: 'Claude looks back at the session and suggests changes to the setup, so the next build goes better.',
    you: 'Pick which suggestions to keep. Run it before you clear the chat.',
    why: 'Each retro turns a mistake into a check or a rule, so it does not happen twice.',
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

const advance = (f: Flow, name: string, step: StepId): Flow => {
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

// Buttons that only talk send at once. Buttons that start work fill the prompt,
// so Enter is the go.
type Move = { key: string; label: string; text: string; isSend: boolean; why: string }

const NEXT_TICKET: Move = {
  key: 'move-next-ticket',
  label: 'Build the next ticket',
  text: '/implement ',
  isSend: false,
  why: 'Clear the chat first, then add the ticket number after /implement.',
}
const CLEAR: Move = { key: 'move-clear', label: 'Clear the chat', text: '/clear', isSend: false, why: 'Empties the chat so the next ticket starts fresh.' }

// Next step only offers what the flow allows from where you are.
const nextFor = (f: Flow): { main: Move; others: Move[] } => {
  const hasTickets = f.done.includes('tickets')
  switch (f.current) {
    case null:
      return {
        main: { key: 'move-grill', label: 'Grill your idea', text: '/grill-with-docs ', isSend: false, why: 'Type your idea after the command in your own words. Rough is fine.' },
        others: [{ key: 'move-bug', label: 'Something is broken instead', text: '/diagnosing-bugs ', isSend: false, why: '' }],
      }
    case 'grill':
      return {
        main: { key: 'move-spec', label: 'Write the spec', text: '/to-spec', isSend: false, why: 'Do this in the same chat, so the spec builds on the whole grilling.' },
        others: [
          { key: 'move-small', label: 'Small job? Build it here', text: '/implement what we just agreed', isSend: false, why: '' },
          { key: 'move-prototype', label: 'Need to see it run first?', text: '/handoff I want to answer this with a throwaway prototype: <the question>', isSend: false, why: '' },
        ],
      }
    case 'spec':
      return {
        main: { key: 'move-tickets', label: 'Cut it into tickets', text: '/to-tickets', isSend: false, why: 'Stay in this chat. Clear it only after the tickets exist.' },
        others: [],
      }
    case 'tickets':
      return {
        main: { key: 'move-build', label: 'Build the first ticket', text: '/implement ', isSend: false, why: 'Clear the chat first. Then add the first ticket after /implement.' },
        others: [CLEAR, { key: 'move-all', label: 'Build every ticket in one run', text: '/implement-spec', isSend: false, why: '' }],
      }
    case 'build':
      return {
        main: { key: 'move-review', label: 'Review the change', text: '/code-review since main', isSend: false, why: 'Two reviewers read the diff before anyone else sees it.' },
        others: [],
      }
    case 'review':
      return {
        main: { key: 'move-pr', label: 'Open the pull request', text: 'open a pull request for this branch. use /pr to write the body.', isSend: false, why: 'It shows the change and the proof that it works.' },
        others: hasTickets ? [CLEAR, NEXT_TICKET] : [],
      }
    case 'pr':
      return {
        main: { key: 'move-retro', label: 'Look back with a retro', text: '/retro', isSend: false, why: 'Run it now, before you clear the chat, so it can see the whole session.' },
        others: hasTickets ? [CLEAR, NEXT_TICKET] : [],
      }
    case 'retro':
      return {
        main: { key: 'move-again', label: 'Start the next idea', text: '/grill-with-docs ', isSend: false, why: 'The path starts over at Grill.' },
        others: hasTickets ? [CLEAR, NEXT_TICKET] : [],
      }
  }
}

const hintFor = (f: Flow) => {
  if (f.current === 'grill' || f.current === 'spec') {
    return 'Keep grilling, spec and tickets in this one chat. Do not clear or compact until the tickets exist.'
  }
  if (f.current === 'tickets' || (f.done.includes('tickets') && f.current !== null)) {
    return 'Clear the chat before each ticket. The ticket holds everything Claude needs.'
  }
  return ''
}

// ---------- Drawing helpers ----------

type Item = { label: string; tip: string }

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

const wrap = (s: string, max: number) => {
  const out: string[] = []
  let line = ''
  for (const word of s.split(' ')) {
    if (line && line.length + word.length + 1 > max) {
      out.push(line)
      line = word
    } else {
      line = line ? `${line} ${word}` : word
    }
  }
  if (line) out.push(line)
  return out
}

const cut = (s: string, max: number) => (s.length > max ? `${s.slice(0, max - 1).trimEnd()}…` : s)

const text = (x: number, y: number, cls: string, s: string, extra = '') =>
  `<text x="${x}" y="${y}" class="${cls}"${extra}>${esc(s)}</text>`

const lines = (x: number, y: number, cls: string, rows: string[], step: number, extra = '') =>
  rows.map((row, i) => text(x, y + i * step, cls, row, extra)).join('')

const chipW = (label: string) => Math.round(label.length * 12.5 * 0.6 + 20)

const chip = (x: number, y: number, it: Item, color: string) => {
  const w = chipW(it.label)
  return `<g class="chip"><title>${esc(it.tip)}</title><rect x="${x}" y="${y}" width="${w}" height="24" rx="12" fill="${color}" fill-opacity=".13"/><text x="${x + w / 2}" y="${y + 16.5}" text-anchor="middle" fill="${INK[color] ?? color}" font-size="12.5" font-weight="600" font-family="${MONO}">${esc(it.label)}</text></g>`
}

const flowChips = (x0: number, y0: number, maxX: number, items: Item[], color: string) => {
  let x = x0
  let y = y0
  let svg = ''
  for (const it of items) {
    const w = chipW(it.label)
    if (x > x0 && x + w > maxX) {
      x = x0
      y += 30
    }
    svg += chip(x, y, it, color)
    x += w + 6
  }
  return { svg, bottom: y + 24 }
}

const down = (cx: number, y: number) => `<path class="ar" d="M${cx - 6} ${y} l6 7 l6 -7z"/>`

const check = (cx: number, cy: number) =>
  `<path d="M${cx - 4.5} ${cy} l3 3.2 l6 -6.5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>`

const doc = (h: number, body: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 ${W} ${h}" preserveAspectRatio="xMidYMin meet">
<style>
svg{background:#F5F5F7}
.bg{fill:#F5F5F7}.card{fill:#FFFFFF;filter:url(#lift)}.ink{fill:#1D1D1F}.mut{fill:#6E6E73}.ln{stroke:#D2D2D7}.ar{fill:#AEAEB2}
text{font-family:${SANS};letter-spacing:-.01em}
.h{font-size:20px;font-weight:700;letter-spacing:-.02em}.sub{font-size:12.5px}.lab{font-size:13px;font-weight:700}.body{font-size:12.5px}.sm{font-size:11.5px}.mono{font-family:${MONO}}
.chip:hover rect{fill-opacity:.24}
</style>
<defs><filter id="lift" x="-10%" y="-10%" width="120%" height="140%"><feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-color="#000" flood-opacity=".07"/><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity=".05"/></filter></defs>
<rect class="bg" width="${W}" height="${h}"/>
${body}</svg>`

// A white card with a colored title and wrapped body lines; returns its height.
const noteCard = (y: number, title: string, body: string, color: string) => {
  const rows = wrap(body, 60)
  const h = 34 + rows.length * 16 + 8
  const svg =
    `<rect x="16" y="${y}" width="${W - 32}" height="${h}" rx="10" fill="${color}" fill-opacity=".1" stroke="${color}" stroke-opacity=".45"/>` +
    `<text x="30" y="${y + 22}" font-size="13" font-weight="700" fill="${INK[color] ?? color}">${esc(title)}</text>` +
    lines(30, y + 42, 'body ink', rows, 16)
  return { svg, h }
}

// ---------- Now: where you are on the path ----------

const nowSvg = (f: Flow) => {
  let b = ''
  const at = f.current ? ORDER.indexOf(f.current) : -1
  const skipped = skippedOf(f)
  b += text(20, 34, 'h ink', 'You are here')
  b += text(W - 20, 34, 'sm mut', at >= 0 ? `step ${at + 1} of 7` : 'not started', ' text-anchor="end"')
  const x0 = 34
  const gap = (W - 2 * x0) / (STEPS.length - 1)
  const cy = 76
  b += `<line class="ln" stroke-width="2" x1="${x0}" x2="${W - x0}" y1="${cy}" y2="${cy}"/>`
  STEPS.forEach((s, i) => {
    const x = x0 + i * gap
    const isNow = i === at
    const isDone = f.done.includes(s.id) && !isNow
    const isSkipped = skipped.includes(s.id)
    if (isNow) {
      b += `<circle cx="${x}" cy="${cy}" r="19" fill="${s.color}" fill-opacity=".2"/>`
      b += `<circle cx="${x}" cy="${cy}" r="14" fill="${s.color}"/>`
      b += `<text x="${x}" y="${cy + 4.5}" text-anchor="middle" fill="#fff" font-size="12.5" font-weight="700">${i + 1}</text>`
    } else if (isSkipped) {
      b += `<circle cx="${x}" cy="${cy}" r="11" fill="#fff" stroke="${C.build}" stroke-width="2" stroke-dasharray="3 2.5"/>`
      b += `<text x="${x}" y="${cy + 4.5}" text-anchor="middle" fill="${INK[C.build]}" font-size="13" font-weight="800">!</text>`
    } else if (isDone) {
      b += `<circle cx="${x}" cy="${cy}" r="11" fill="${s.color}"/>${check(x, cy)}`
    } else {
      b += `<circle cx="${x}" cy="${cy}" r="10" fill="#E5E5EA"/>`
      b += `<text x="${x}" y="${cy + 4}" text-anchor="middle" font-size="11" font-weight="600" class="mut">${i + 1}</text>`
    }
    const tone = isNow ? ` fill="${INK[s.color]}" font-weight="700"` : isSkipped ? ` fill="${INK[C.build]}" font-weight="600"` : ' class="mut"'
    b += `<text x="${x}" y="${cy + 36}" text-anchor="middle" font-size="11.5"${tone}>${s.name}</text>`
  })
  let y = 132
  if (f.current) {
    const s = stepOf(f.current)
    const what = wrap(s.what, 56)
    const you = wrap(s.you, 56)
    const h = 106 + (what.length + you.length) * 16
    b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${h}" rx="12"/>`
    b += `<rect x="16" y="${y + 14}" width="4" height="22" rx="2" fill="${s.color}"/>`
    b += text(30, y + 31, 'ink', s.name, ' font-size="17" font-weight="700"')
    b += chip(W - 28 - chipW(s.cmd), y + 13, { label: s.cmd, tip: `The skill for the ${s.name} step` }, s.color)
    let ty = y + 58
    b += `<text x="30" y="${ty}" font-size="11" font-weight="700" fill="${INK[s.color]}" letter-spacing=".04em">WHAT IT IS</text>`
    b += lines(30, ty + 17, 'body ink', what, 16)
    ty += 17 + what.length * 16 + 10
    b += `<text x="30" y="${ty}" font-size="11" font-weight="700" fill="${INK[s.color]}" letter-spacing=".04em">WHAT YOU DO</text>`
    b += lines(30, ty + 17, 'body ink', you, 16)
    y += h + 12
  } else {
    const card = noteCard(y, 'Every job starts with an idea', 'Press Next step and type your idea in plain words. Claude will ask you questions until it is clear, then you build it step by step.', C.grill)
    b += card.svg
    y += card.h + 12
  }
  for (const id of skipped) {
    const s = stepOf(id)
    const card = noteCard(y, `You skipped ${s.name}`, s.why, C.build)
    b += card.svg
    y += card.h + 12
  }
  const hint = hintFor(f)
  if (hint) {
    const card = noteCard(y, 'Keep the chat clean', hint, C.grill)
    b += card.svg
    y += card.h + 12
  }
  const next = nextFor(f)
  const why = next.main.why ? wrap(next.main.why, 50) : []
  const h = 82 + why.length * 16
  b += `<rect x="16" y="${y}" width="${W - 32}" height="${h}" rx="12" fill="${C.review}" fill-opacity=".13" stroke="${C.review}" stroke-opacity=".5"/>`
  b += `<circle cx="48" cy="${y + 38}" r="20" fill="${C.review}"/><path d="M38 ${y + 38} h16 m-6 -7 l7 7 l-7 7" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`
  b += `<text x="80" y="${y + 26}" font-size="11.5" font-weight="700" fill="${INK[C.review]}" letter-spacing=".04em">NEXT STEP</text>`
  b += text(80, y + 47, 'ink', cut(next.main.label, 36), ' font-size="17" font-weight="700"')
  b += `<text x="80" y="${y + 67}" font-size="12.5" font-family="${MONO}" class="ink">${esc(cut(next.main.text.trim(), 44))}</text>`
  b += lines(80, y + 86, 'sm mut', why, 16)
  y += h + 8
  return { source: doc(y + 8, b), next }
}

const nowMd = (f: Flow) => {
  const skipped = skippedOf(f)
  const strip = STEPS.map(s =>
    s.id === f.current ? `**[${s.name}]**` : skipped.includes(s.id) ? `!${s.name}` : f.done.includes(s.id) ? `✓${s.name}` : s.name,
  ).join(' → ')
  const s = f.current ? stepOf(f.current) : null
  const next = nextFor(f)
  return [
    '### You are here',
    strip,
    s ? `**${s.name}** (\`${s.cmd}\`)\n\nWhat it is: ${s.what}\n\nWhat you do: ${s.you}` : 'Nothing started yet. Every job starts with an idea.',
    ...skipped.map(id => `**You skipped ${stepOf(id).name}.** ${stepOf(id).why}`),
    hintFor(f) ? `_${hintFor(f)}_` : '',
    `**Next step:** ${next.main.label}: \`${next.main.text.trim()}\`${next.main.why ? `\n\n${next.main.why}` : ''}`,
  ]
    .filter(Boolean)
    .join('\n\n')
}

// ---------- Guide: the main flow ----------

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
    svg += chip(W - 28 - chipW(s.cmd), y + 10, { label: s.cmd, tip: s.what }, s.color)
    svg += lines(62, y + 48, 'body mut', what, 16)
    return { svg, h }
  }
  const side = (title: string, body: string, color: string) => {
    const rows = wrap(body, 60)
    const h = 26 + rows.length * 15 + 8
    const svg =
      `<rect x="44" y="${y}" width="${W - 60}" height="${h}" rx="9" fill="${color}" fill-opacity=".08" stroke="${color}" stroke-opacity=".5" stroke-dasharray="4 3"/>` +
      `<text x="58" y="${y + 18}" font-size="12" font-weight="700" fill="${INK[color] ?? color}">${esc(title)}</text>` +
      lines(58, y + 35, 'sm ink', rows, 15)
    return { svg, h }
  }
  const band = (label: string, color: string) => {
    b += `<rect x="16" y="${y}" width="${W - 32}" height="26" rx="13" fill="${color}" fill-opacity=".14"/>`
    b += `<text x="${W / 2}" y="${y + 17.5}" text-anchor="middle" font-size="12" font-weight="700" fill="${INK[color] ?? color}">${esc(label)}</text>`
    y += 26 + 10
  }
  band('Steps 1 to 3: one chat, no clearing', C.grill)
  STEPS.forEach((s, i) => {
    if (i === 3) band('Clear the chat before each ticket', C.tickets)
    const c = card(s, i)
    b += c.svg
    y += c.h + 6
    if (s.id === 'grill') {
      b += down(W / 2, y)
      y += 12
      const d = side('Stuck on a question only running code can answer?', '/handoff out, /prototype a throwaway answer in a new chat, then /handoff back what you learned.', C.grill)
      b += d.svg
      y += d.h + 6
      const small = side('Small job that fits in one chat?', 'Skip spec and tickets. Run /implement right after grilling.', C.build)
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

// ---------- Guide: other ways in ----------

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

// ---------- Guide: skills for any time ----------

const ANYTIME: { name: string; color: string; items: Item[] }[] = [
  {
    name: 'Think it through',
    color: C.grill,
    items: [
      { label: '/grill-me', tip: 'The same interview as /grill-with-docs, for a plan with no repo. It saves nothing.' },
      { label: '/research', tip: 'A background agent reads the sources and leaves a cited notes file in the repo.' },
      { label: '/to-questionnaire', tip: 'Writes questions for someone else to answer, when the gap is in their head.' },
    ],
  },
  {
    name: 'Learn and ask',
    color: C.spec,
    items: [
      { label: '/wait-what', tip: 'That last message did not land. Claude says it again, in plain words.' },
      { label: '/teach', tip: 'Learn a concept over several sessions, in this folder.' },
    ],
  },
  {
    name: 'Words and shape',
    color: C.tickets,
    items: [
      { label: '/domain-modeling', tip: 'Sort out a fuzzy word, or record a hard-to-undo decision.' },
      { label: '/codebase-design', tip: 'Shape a part of the code: a lot of work behind a small, simple surface.' },
    ],
  },
  {
    name: 'Steps only you can do',
    color: C.build,
    items: [{ label: '/wizard', tip: 'A script that walks you through keys, dashboards and secrets, and saves each value.' }],
  },
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
    const f = flowChips(20, y + 10, W - 16, g.items, g.color)
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
    b += `<text x="71" y="${ry + 19.5}" text-anchor="middle" font-size="12" font-weight="700" font-family="${MONO}" class="ink">${esc(k)}</text>`
    b += text(126, ry + 19.5, 'body ink', v)
  })
  y += BETWEEN.length * 34 + 10
  return doc(y + 18, b)
}

// ---------- Guide: words you will hear ----------

const WORDS: [string, string][] = [
  ['Grilling', 'Claude asks you questions, one round at a time, until the idea has no gaps. Facts are Claude\'s job. Decisions are yours.'],
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
    b += text(40, y + 25, 'lab', word, ` fill="${INK[color]}" font-size="13.5"`)
    b += lines(40, y + 44, 'body ink', rows, 16)
    y += h + 8
  })
  return doc(y + 10, b)
}

const GUIDE: { id: Tab; label: string; svg: string; alt: string; md: string }[] = [
  {
    id: 'flow',
    label: 'Main path',
    svg: flowSvg(),
    alt: 'The seven steps from idea to shipped, with the skill for each',
    md: `### From idea to shipped\n\n${STEPS.map((s, i) => `${i + 1}. **${s.name}** \`${s.cmd}\`: ${s.what}`).join('\n')}\n\nKeep steps 1 to 3 in one chat. Clear the chat before each ticket.`,
  },
  {
    id: 'ramps',
    label: 'Other ways in',
    svg: rampsSvg(),
    alt: 'Starting points that join the main path partway',
    md: `### Other ways in\n\n${RAMPS.map(r => `- **${r.when}**: \`${r.cmd}\`. ${r.what} Joins at ${stepOf(r.joins).name}.`).join('\n')}\n\nBefore your first build in a repo, run \`/setup-matt-pocock-skills\`.`,
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

// The desktop draws an Svg in a frame it cannot size from the markup, so pass
// the pixel size: the pane's width, guessed at 8px a cell.
const fit = (source: string, columns: number) => {
  const width = Math.round(Math.min(Math.max(columns * 8, 300), 1100))
  const h = Number(/viewBox="0 0 \d+ ([\d.]+)"/.exec(source)?.[1] ?? 600)
  return { width, height: Math.round((h * width) / W) }
}

// ---------- Is the setup there? ----------

const SKILL_PLUGINS = ['mattpocock-skills@', 'matt-pocock@']
// The official marketplace pins a commit from before v1.3.1, so the mirror is the one to install.
const OUTDATED = 'mattpocock-skills@claude-plugins-official'
const INSTALL = 'claude plugin marketplace add mattnicosia/bldg-skills && claude plugin install matt-pocock@bldg-skills'

async function readEnv($: EngineInterface) {
  const home = (await $.env.get('HOME')) ?? ''
  let keys: string[] = []
  try {
    const raw = JSON.parse(String(await $.fs.read(`${home}/.claude/plugins/installed_plugins.json`))) as { plugins?: Record<string, unknown> }
    keys = Object.keys(raw.plugins ?? {})
  } catch {
    keys = []
  }
  // skills.sh copies the skill files into the user's or the project's skills folder instead of a plugin.
  const isCopied =
    (await $.fs.exists(`${home}/.claude/skills/grill-with-docs/SKILL.md`).catch(() => false)) ||
    (await $.fs.exists('.claude/skills/grill-with-docs/SKILL.md').catch(() => false))
  const found = keys.filter(k => SKILL_PLUGINS.some(p => k.startsWith(p)))
  const value: Env = {
    isRead: true,
    hasSkills: isCopied || found.length > 0,
    isOutdated: !isCopied && found.length > 0 && found.every(k => k === OUTDATED),
    hasPstackGuide: keys.some(k => k.startsWith('pstack-guide@')),
  }
  await update($, env, () => value)
  return value
}

// ---------- Start tab: the repo at a glance ----------

const STALE_DAYS = 14

const git = async ($: EngineInterface, args: string[]) => {
  try {
    const r = await $.process.run(['git', ...args], { timeoutMs: 10000 })
    return r.exitCode === 0 ? r.stdout.trim() : null
  } catch {
    return null
  }
}

// In a worktree, --show-toplevel names the worktree folder; the shared git dir
// sits inside the main checkout, which carries the repo's name.
const mainCheckout = async ($: EngineInterface) => {
  const common = await git($, ['rev-parse', '--path-format=absolute', '--git-common-dir'])
  return common === null ? null : common.replace(/\/\.git\/?$/, '')
}

const ciOf = (checks: { status?: string; conclusion?: string; state?: string }[]): PullRequest['ci'] => {
  if (checks.length === 0) return 'none'
  const bad = new Set(['FAILURE', 'ERROR', 'TIMED_OUT', 'CANCELLED', 'ACTION_REQUIRED'])
  if (checks.some(c => bad.has(c.conclusion ?? '') || bad.has(c.state ?? ''))) return 'fail'
  if (checks.some(c => (c.status && c.status !== 'COMPLETED') || c.state === 'PENDING')) return 'pending'
  return 'pass'
}

// Reads the repo once per press, never while drawing, so the pane stays still.
async function readRepo($: EngineInterface) {
  const top = await git($, ['rev-parse', '--show-toplevel'])
  if (top === null) {
    await update($, repo, () => ({ ...NO_REPO, isRead: true, error: 'This session is not in a git repo.' }))
    return
  }
  const branch = (await git($, ['rev-parse', '--abbrev-ref', 'HEAD'])) ?? '?'
  const status = (await git($, ['status', '--porcelain'])) ?? ''
  const base = ((await git($, ['symbolic-ref', '--short', 'refs/remotes/origin/HEAD'])) ?? 'origin/main').replace(/^origin\//, '')
  const merged = new Set(((await git($, ['branch', '--merged', base, '--format=%(refname:short)'])) ?? '').split('\n').filter(Boolean))
  const heads = ((await git($, ['for-each-ref', '--format=%(refname:short)|%(committerdate:unix)', 'refs/heads'])) ?? '').split('\n').filter(Boolean)
  // A worktree entry is a `worktree <path>` line, then `branch refs/heads/<name>`.
  const trees = ((await git($, ['worktree', 'list', '--porcelain'])) ?? '').split('\n\n').map(entry => ({
    path: /^worktree (.+)$/m.exec(entry)?.[1] ?? '',
    branch: /^branch refs\/heads\/(.+)$/m.exec(entry)?.[1] ?? '',
  }))
  // A branch checked out in any worktree is someone's live work, never stale.
  const inUse = new Set(trees.map(t => t.branch).filter(Boolean))
  const others = trees.filter((t, i) => i > 0 && t.path && t.path !== top)
  const cutoff = Date.now() / 1000 - STALE_DAYS * 86400
  const stale = heads
    .map(line => {
      const [name = '', when = '0'] = line.split('|')
      return { name, when: Number(when) }
    })
    .filter(h => h.name !== base && !inUse.has(h.name) && (merged.has(h.name) || h.when < cutoff))
    .map(h => h.name)
  let prs: PullRequest[] = []
  let error: string | null = null
  try {
    const r = await $.process.run(['gh', 'pr', 'list', '--author', '@me', '--state', 'open', '--limit', '8', '--json', 'number,title,isDraft,statusCheckRollup'], { timeoutMs: 15000 })
    if (r.exitCode === 0) {
      prs = (JSON.parse(r.stdout) as { number: number; title: string; isDraft: boolean; statusCheckRollup: { status?: string; conclusion?: string; state?: string }[] }[]).map(p => ({
        number: p.number,
        title: p.title,
        isDraft: p.isDraft,
        ci: ciOf(p.statusCheckRollup ?? []),
      }))
    } else error = 'Could not read pull requests with gh.'
  } catch {
    error = 'Could not read pull requests with gh.'
  }
  // /setup-matt-pocock-skills always writes this file.
  const isSetUp = await $.fs.exists(`${top}/docs/agents/issue-tracker.md`).catch(() => true)
  const name = ((await mainCheckout($)) ?? top).split('/').pop() ?? top
  await update($, repo, () => ({ isRead: true, error, name, branch, dirty: status ? status.split('\n').length : 0, stale, worktrees: others.length, prs, isSetUp }))
}

const startSvg = (r: Repo) => {
  const failing = r.prs.filter(p => p.ci === 'fail').length
  const running = r.prs.filter(p => p.ci === 'pending').length
  const tiles: { n: number; label: string; note: string; color: string }[] = [
    {
      n: r.prs.length,
      label: r.prs.length === 1 ? 'Open PR' : 'Open PRs',
      note: r.prs.length === 0 ? 'none open' : failing ? `${failing} failing` : running ? `${running} running` : 'all green',
      color: r.prs.length === 0 ? C.gray : failing ? C.red : running ? C.build : C.review,
    },
    { n: r.dirty, label: 'Uncommitted', note: r.dirty ? 'files changed' : 'clean', color: r.dirty ? C.build : C.review },
    { n: r.stale.length, label: 'Stale', note: r.stale.length ? 'branches' : 'none', color: r.stale.length ? C.build : C.review },
    { n: r.worktrees, label: 'Worktrees', note: r.worktrees ? 'others open' : 'just this one', color: r.worktrees ? C.grill : C.gray },
  ]
  const isClean = r.prs.length === 0 && r.dirty === 0 && r.stale.length === 0 && r.worktrees === 0
  let b = ''
  b += text(20, 36, 'h ink', cut(r.name || 'No repo', 26))
  const bw = Math.min(r.branch.length * 7 + 24, 210)
  b += `<rect x="${W - 20 - bw}" y="18" width="${bw}" height="24" rx="12" fill="${C.slate}" fill-opacity=".08"/>`
  b += `<text x="${W - 32}" y="34.5" text-anchor="end" font-size="12" font-family="${MONO}" class="mut">${esc(cut(r.branch, 27))}</text>`
  b += text(20, 58, 'sub mut', isClean ? 'Nothing open. You can start something new.' : 'Finish what is open before starting something new.')
  const tw = (W - 32 - 3 * 8) / 4
  tiles.forEach((t, i) => {
    const x = 16 + i * (tw + 8)
    b += `<rect class="card" x="${x}" y="74" width="${tw}" height="92" rx="12"/>`
    b += `<rect x="${x + 14}" y="86" width="22" height="4" rx="2" fill="${t.color}"/>`
    b += `<text x="${x + 14}" y="118" font-size="32" font-weight="700" fill="${t.n ? (INK[t.color] ?? t.color) : '#AEAEB2'}" letter-spacing="-.02em">${t.n}</text>`
    b += `<text x="${x + 14}" y="140" font-size="12" font-weight="600" class="ink">${esc(t.label)}</text>`
    b += `<circle cx="${x + 18}" cy="154" r="3.5" fill="${t.color}"/>`
    b += `<text x="${x + 26}" y="158" font-size="11" class="mut">${esc(t.note)}</text>`
  })
  return doc(184, b)
}

type Act = { key: string; label: string; text: string; isSend: boolean }

const prActs = (pr: PullRequest): Act[] =>
  pr.ci === 'fail'
    ? [{ key: `fix-${pr.number}`, label: 'Fix the checks', isSend: false, text: `pull request #${pr.number} has failing checks. tell me why in plain words, then fix them test-first. don't merge.` }]
    : [{ key: `review-${pr.number}`, label: 'Review it', isSend: false, text: `/code-review pull request #${pr.number} against its base branch` }]

const SETUP: Act = { key: 'start-setup', label: 'Set up this repo', isSend: true, text: '/setup-matt-pocock-skills' }

const CATCH_UP: Act = {
  key: 'start-catchup',
  label: 'Catch me up',
  isSend: true,
  text: "catch me up in plain words for a beginner: what this repo does, what was built recently, any open branches or pull requests, and which step of the flow (grill, spec, tickets, build, review, PR, retro) the work is at. keep it short. end with a multiple-choice question of what to do next, with finishing open work first.",
}

const STARTS: Act[] = [
  { key: 'start-idea', label: 'I have an idea', isSend: false, text: '/grill-with-docs ' },
  { key: 'start-bug', label: 'Something is broken', isSend: false, text: '/diagnosing-bugs ' },
  {
    key: 'start-ticket',
    label: 'Pick up a ticket',
    isSend: true,
    text: "list this repo's open tickets that are ready for an agent, using the issue tracker named in docs/agents/issue-tracker.md, and ask me to pick one with a multiple-choice question. when I pick, run /implement on it.",
  },
  CATCH_UP,
]

// ---------- Guard rail: grill before building ----------

const BUILD_ASK = /\b(build|add|implement|make|create|change|refactor|rewrite|update|wire up|hook up|code|feature|new (page|screen|button|endpoint|component))\b/i
const BUG_ASK = /\b(bug|broken|error|crash(es|ed|ing)?|fails?|failing|doesn'?t work|not working|exception|stack trace)\b/i
const QUESTION = /^(how|what|why|where|when|who|which|is|are|does|can you explain|explain|tell me)\b/i

const nudgeFor = (prompt: string, f: Flow): Nudge => {
  const said = prompt.trim()
  if (!said || said.startsWith('/') || QUESTION.test(said)) return null
  // Only before the path starts, or once the last job ran its retro.
  if (f.current !== null && f.current !== 'retro') return null
  if (BUG_ASK.test(said)) return { text: said, kind: 'bug' }
  if (BUILD_ASK.test(said)) return { text: said, kind: 'grill' }
  return null
}

const NUDGE_NOTE: Record<NonNullable<Nudge>['kind'], string> = {
  grill:
    '(pocock-guide: the person is new and follows Matt Pocock\'s flow: grill, spec, tickets, build test-first, review, PR, retro. ' +
    'They asked for a code change before any grilling. Start your reply with one plain sentence suggesting they run /grill-with-docs first, and why. ' +
    'Then do what they asked. If the change is large, ask whether to grill first before you write code.)',
  bug:
    '(pocock-guide: the person is new and follows Matt Pocock\'s flow. They described something broken. ' +
    'Start your reply with one plain sentence suggesting /diagnosing-bugs, which finds a command that shows the bug failing before it fixes anything. ' +
    'Then help with what they asked, and reproduce the bug before you change code.)',
}

// ---------- Decision card and turn summary ----------

const looksLikeChoice = (answer: string) => {
  const tail = answer.slice(-1500)
  const listed = (tail.match(/^\s*(?:\*\*)?([A-H]|[1-9])[.):](?:\*\*)?\s+\S/gm) ?? []).length
  return listed >= 2 || /\?\s*$/.test(answer.trim()) || /\b(reply with|which (one|option)|should I|do you want|want me to|pick one|say the word)\b/i.test(tail)
}

const DECIDE_PROMPT = (answer: string) =>
  'A beginner is working with an AI coding agent through Matt Pocock\'s flow: grill the idea, write a spec, cut tickets, build test-first, review, open a PR, run a retro. ' +
  'The agent just finished a turn. Summarize it in short everyday words for the beginner, and if it ends by asking them to make a choice, extract it. ' +
  'The flow favors: grill before building, a spec and tickets for anything bigger than one chat, a failing test before the fix, review before a PR, and finishing open work before starting new work.\n\n' +
  'Reply with JSON only, no prose, in this shape:\n' +
  '{"done":"<what this turn did or found, one or two plain sentences>","next":"<what the beginner should do next, one sentence>","isWaiting":<true if the agent stopped and needs the person to answer or act>,"isChoice":true,"question":"<one short line>","options":[{"key":"<what the person would type, e.g. B or yes>","label":"<3 to 6 words>"}],"pick":"<key the flow favors>","why":"<one plain sentence>"}\n' +
  'For a yes or no question use keys "yes" and "no". At most 6 options. If the turn does not ask for a choice, set isChoice false and leave out question, options, pick and why.\n\n' +
  `The turn's final reply:\n${answer.slice(-6000)}`

const PR_LINK = /https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/pull\/\d+/g

const jsonOf = (s: string) => JSON.parse(s.slice(s.indexOf('{'), s.lastIndexOf('}') + 1)) as Record<string, unknown>

const parseSummary = (said: string, answer: string): Summary => {
  const links = [...new Set(answer.match(PR_LINK) ?? [])].slice(0, 4)
  try {
    const raw = jsonOf(said)
    if (!raw.done) return null
    return { done: String(raw.done), next: String(raw.next ?? ''), links, isWaiting: raw.isWaiting === true }
  } catch {
    return null
  }
}

const parseDecision = (said: string): Decision => {
  try {
    const raw = jsonOf(said)
    const options: Choice[] = ((raw.options ?? []) as Partial<Choice>[])
      .filter(o => o.key && o.label)
      .slice(0, 6)
      .map(o => ({ key: String(o.key), label: String(o.label) }))
    if (!raw.isChoice || options.length === 0) return null
    const pick = options.some(o => o.key === raw.pick) ? String(raw.pick) : ''
    return { question: String(raw.question ?? 'Your call'), options, pick, why: String(raw.why ?? '') }
  } catch {
    return null
  }
}

const decisionSvg = (d: NonNullable<Decision>) => {
  let b = ''
  b += `<circle cx="26" cy="27" r="5" fill="${C.build}"/>`
  b += `<text x="38" y="31" font-size="12" font-weight="700" fill="${INK[C.build]}" letter-spacing=".04em">CLAUDE IS ASKING YOU</text>`
  const q = wrap(d.question, 44).slice(0, 2)
  b += lines(20, 56, 'ink', q, 22, ' font-size="18" font-weight="700" letter-spacing="-.02em"')
  let y = 56 + q.length * 22 - 4
  for (const o of d.options) {
    const isPick = o.key === d.pick
    const h = 46
    b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${h}" rx="12"${isPick ? ` stroke="${C.grill}" stroke-width="2"` : ''}/>`
    b += `<circle cx="40" cy="${y + h / 2}" r="13" fill="${isPick ? C.grill : '#E5E5EA'}"/>`
    b += `<text x="40" y="${y + h / 2 + 4.5}" text-anchor="middle" font-size="12.5" font-weight="700" fill="${isPick ? '#fff' : '#1D1D1F'}">${esc(cut(o.key, 3))}</text>`
    b += `<text x="62" y="${y + h / 2 + (isPick ? -1 : 4.5)}" font-size="13.5" font-weight="${isPick ? 700 : 500}" class="ink">${esc(cut(o.label, 40))}</text>`
    if (isPick) b += `<text x="62" y="${y + h / 2 + 14}" font-size="10.5" font-weight="700" fill="${INK[C.grill]}">★ what the flow suggests</text>`
    y += h + 8
  }
  if (d.why) {
    y += 8
    const why = wrap(d.why, 62).slice(0, 3)
    b += lines(20, y, 'body mut', why, 17)
    y += why.length * 17
  }
  return doc(y + 10, b)
}

// ---------- Flow progress, kept per repo ----------

const flowKey = (root: string) => `flow:${root}`

// The flow belongs to the repo, not the chat, so a cleared chat or a new session
// in the same repo picks up where the last one stopped.
async function loadFlow($: EngineInterface) {
  const root = (await mainCheckout($)) ?? (await $.session.cwd())
  const saved = (await $.store.get(flowKey(root))) as Flow | undefined
  const value: Flow = saved && Array.isArray(saved.done) ? { ...EMPTY_FLOW, ...saved, root } : { ...EMPTY_FLOW, root }
  await update($, flow, () => value)
}

async function setFlow($: EngineInterface, fn: (f: Flow) => Flow) {
  const next = await update($, flow, fn)
  if (next.root) await $.store.set(flowKey(next.root), next)
}

async function useSkill($: EngineInterface, raw: string) {
  const name = raw.split(':').pop() ?? raw
  const step = SKILL_STEP[name]
  if (!step) return
  const now = await read($, flow)
  if (now.last === name && now.current === (REVIEWS_ITSELF.has(name) ? 'review' : step)) return
  await setFlow($, f => advance(f, name, step))
  await update($, nudge, () => null)
}

export const register: Register = on => {
  // The pane opens on its own only where pstack-guide does not, so Matt's own
  // sessions keep pstack-guide. /mod-pocock opens it anywhere.
  let isActive = false
  let isNudgeOff = false

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'mod-pocock',
      description: "Open a guide that walks you through Matt Pocock's flow, step by step",
    })
    const found = await readEnv($)
    await loadFlow($)
    isActive = !found.hasPstackGuide
    if (isActive) void $.ui.open({ id: PANE, title: TITLE, focus: true })
    void readRepo($)

    return next(e)
  })

  on('command.run', { command: 'mod-pocock' }, async $ => {
    isActive = true
    const f = await read($, flow)
    await update($, tab, t => (f.current && t === 'start' ? 'now' : t))
    await readEnv($)
    await $.ui.open({ id: PANE, title: TITLE })
    void readRepo($)

    return { text: 'Pocock flow pane opened.' }
  })

  on('command.run', async ($, e, next) => {
    await useSkill($, e.command)
    const result = await next(e)
    // /clear may start the session state over; the repo's saved flow brings it back.
    if (e.command === 'clear' && !(await read($, flow)).root) await loadFlow($)
    return result
  })

  on('skill.prompt', async ($, e, next) => {
    await useSkill($, e.skill)
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId) return result
    const args = e as unknown as Record<string, unknown>
    if (e.tool === 'Skill' && typeof args.skill === 'string') await useSkill($, args.skill)
    if (e.tool === 'Bash' && typeof args.command === 'string' && /\bgh pr create\b/.test(args.command)) {
      await setFlow($, f => advance(f, 'gh pr create', 'pr'))
    }
    return result
  })

  // A prompt that asks for code before any grilling gets a card in the pane and a
  // note for the model. Nothing is blocked.
  on('prompt.submit', async ($, e, next) => {
    await update($, decision, () => null)
    await update($, summary, s => (s ? { ...s, isWaiting: false } : s))
    const isPerson = e.origin.kind === 'composer' || e.origin.kind === 'bridge'
    const found = isPerson && !isNudgeOff && (await read($, env)).hasSkills ? nudgeFor(e.text, await read($, flow)) : null
    await update($, nudge, () => found)
    if (!found) return next(e)
    $.ui.toast(found.kind === 'bug' ? 'Pocock flow: try /diagnosing-bugs. The pane has a button.' : 'Pocock flow: grill it first? The pane has a button.')
    return next({ ...e, context: [...(e.context ?? []), NUDGE_NOTE[found.kind]] })
  })

  // The desktop spends the first click on an unfocused pane on focus, so a
  // button needs two clicks. When a main turn ends the pane asks for the keyboard.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if ((e as { agentId?: string }).agentId !== undefined) return result
    if (isActive) void $.ui.open({ id: PANE, title: TITLE, focus: true })
    if (!(await read($, flow)).root) await loadFlow($)
    const answer = e.answer.trim()
    if (e.isAborted || !answer) {
      await update($, decision, () => null)
      return result
    }
    // A short reply is its own summary, so it costs no model call.
    if (answer.length < 280 && !looksLikeChoice(answer)) {
      await update($, decision, () => null)
      await update($, summary, () => ({ done: answer, next: '', links: [...new Set(answer.match(PR_LINK) ?? [])], isWaiting: false }))
      return result
    }
    void (async () => {
      const ask = await $.model.complete({ model: 'haiku', prompt: DECIDE_PROMPT(answer), timeoutMs: 20000 })
      const found = ask.isAnswered && looksLikeChoice(answer) ? parseDecision(ask.text) : null
      const said = ask.isAnswered ? parseSummary(ask.text, answer) : null
      await update($, decision, () => found)
      await update($, summary, () => (said ? { ...said, isWaiting: said.isWaiting || found !== null } : null))
      if (found) $.ui.toast('Pocock flow: Claude is asking you to choose. The pane has a button for each option.')
      else if (said?.isWaiting) $.ui.toast('Pocock flow: Claude is waiting on you. The pane says what for.')
    })()
    return result
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const current = await read($, tab)
    const f = await read($, flow)
    const setup = await read($, env)
    const { Box, Button, Markdown, Text, Code } = $.ui.resolve(e)
    const isDesktop = e.surface !== 'terminal'

    const guide = GUIDE.find(g => g.id === current)
    const go = (id: Tab) => () => {
      void update($, tab, () => id)
      if (id === 'start') void readRepo($)
    }
    const top: { id: Tab; label: string; key: string; isOn: boolean }[] = [
      { id: 'start', label: 'Start', key: 'tab-start', isOn: current === 'start' },
      { id: 'now', label: 'Now', key: 'tab-now', isOn: current === 'now' },
      { id: guide ? current : 'flow', label: 'Guide', key: 'tab-guide', isOn: guide !== undefined },
    ]
    const nav = (
      <Box flexDirection="column" gap={1}>
        <Box flexDirection="row" flexWrap="wrap" gap={1}>
          {top.map(t => (
            <Button key={t.key} label={t.label} variant={t.isOn ? 'primary' : 'secondary'} onPress={go(t.id)} />
          ))}
        </Box>
        {guide ? (
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {GUIDE.map(g => (
              <Button key={`tab-${g.id}`} label={g.id === current ? `• ${g.label}` : g.label} plain onPress={go(g.id)} />
            ))}
          </Box>
        ) : null}
      </Box>
    )

    const act = (a: Act | Move, variant: 'primary' | 'secondary' = 'secondary') => (
      <Button
        key={a.key}
        label={a.label}
        variant={variant}
        onPress={() => {
          if (!a.isSend) return void $.prompt.fill({ text: a.text })
          // The engine refuses a submitted prompt that starts with a slash, so a
          // slash command runs as a command.
          const slash = /^\/(\S+)\s*([\s\S]*)$/.exec(a.text)
          void (slash ? $.command.run({ command: slash[1] ?? '', args: slash[2] ?? '' }) : $.prompt.submit({ text: a.text, asUser: true }))
        }}
      />
    )

    const asked = await read($, nudge)
    const nudgeCard =
      asked === null ? null : (
        <Box key="nudge" flexDirection="column" gap={1} borderStyle="round" borderColor="#F56300" paddingX={1}>
          <Text bold color="#F56300">
            {asked.kind === 'bug' ? 'Sounds like something is broken' : 'Grill it first?'}
          </Text>
          <Text>
            {asked.kind === 'bug'
              ? '/diagnosing-bugs finds a command that shows the bug failing, then fixes it with a test. Claude will still help with what you asked.'
              : 'You asked for code before any grilling. A few minutes of questions now saves a rebuild later. Claude will still do what you asked.'}
          </Text>
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            <Button
              key="nudge-go"
              label={asked.kind === 'bug' ? 'Diagnose it' : 'Grill it first'}
              variant="primary"
              onPress={() => {
                void $.prompt.fill({ text: `${asked.kind === 'bug' ? '/diagnosing-bugs' : '/grill-with-docs'} ${asked.text}` })
              }}
            />
            <Button
              key="nudge-off"
              label="Not this time"
              onPress={() => {
                isNudgeOff = true
                void update($, nudge, () => null)
              }}
            />
          </Box>
        </Box>
      )

    const said = await read($, summary)
    const summaryCard =
      said === null ? null : (
        <Box key="summary" flexDirection="column" borderStyle="round" borderColor={said.isWaiting ? '#F56300' : '#D2D2D7'} paddingX={1}>
          <Text bold color={said.isWaiting ? '#F56300' : undefined}>
            {said.isWaiting ? 'Needs you' : 'Last turn'}
          </Text>
          <Markdown
            text={[said.done, said.next ? `**Next:** ${said.next}` : '', said.links.map(l => `[PR #${l.split('/').pop()}](${l})`).join(' · ')]
              .filter(Boolean)
              .join('\n\n')}
          />
        </Box>
      )

    const open = await read($, decision)
    const choose = (o: Choice, label: string) => (
      <Button
        key={`choose-${o.key}`}
        label={label}
        variant={o.key === open?.pick ? 'primary' : 'secondary'}
        onPress={() => {
          void $.prompt.submit({ text: o.key, asUser: true })
        }}
      />
    )
    const decisionCard =
      open === null ? null : isDesktop ? (
        <Box key="decision" flexDirection="column" gap={1}>
          {(() => {
            const { Svg } = $.ui.resolve(e)
            const source = decisionSvg(open)
            return <Svg source={source} alt={`Claude is asking: ${open.question}`} {...fit(source, e.props.bodyColumns)} />
          })()}
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {open.options.map(o => choose(o, o.key === open.pick ? `★ ${o.key}` : o.key))}
          </Box>
        </Box>
      ) : (
        <Box key="decision" flexDirection="column" gap={1} borderStyle="round" paddingX={1}>
          <Text bold>Claude is asking: {open.question}</Text>
          {open.why ? <Text dimColor>{open.why}</Text> : null}
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {open.options.map(o => choose(o, `${o.key} · ${o.label}`))}
          </Box>
        </Box>
      )

    const installCard = setup.hasSkills && !setup.isOutdated ? null : (
      <Box key="install" flexDirection="column" gap={1} borderStyle="round" borderColor="#E5342C" paddingX={1}>
        <Text bold color="#E5342C">
          {setup.hasSkills ? "Your copy of Matt Pocock's skills is out of date" : "Matt Pocock's skills are not installed"}
        </Text>
        <Text>
          {setup.hasSkills
            ? 'The copy from the official marketplace is older than v1.3.1 and has no /implement-spec, /pr or /retro, which later steps need. Run this in a terminal, then start a new session:'
            : 'The buttons here run his skills, so install them first. Run this in a terminal, then start a new session:'}
        </Text>
        <Code source={INSTALL} />
        {setup.hasSkills ? <Text dimColor>Then remove the old copy with: claude plugin uninstall mattpocock-skills</Text> : null}
        <Box flexDirection="row" gap={1}>
          <Button key="check-again" label="Check again" onPress={() => readEnv($)} />
        </Box>
      </Box>
    )

    if (current === 'start') {
      const r = await read($, repo)
      const ciText = { fail: 'checks failing', pending: 'checks running', pass: 'checks green', none: 'no checks' } as const
      const rows: { key: string; label: string; acts: Act[] }[] = [
        ...r.prs.map(pr => ({
          key: `pr-${pr.number}`,
          label: `PR #${pr.number}${pr.isDraft ? ' (draft)' : ''} · ${ciText[pr.ci]} · ${cut(pr.title, 48)}`,
          acts: prActs(pr),
        })),
        ...(r.dirty > 0
          ? [{
              key: 'dirty',
              label: `${r.dirty} uncommitted ${r.dirty === 1 ? 'file' : 'files'} on ${r.branch}`,
              acts: [{ key: 'look-dirty', label: 'Look at them', isSend: false, text: "show me the uncommitted changes in this repo in plain words: what they are, and whether they look like mine or another session's. don't change anything." }],
            }]
          : []),
        ...(r.stale.length > 0 || r.worktrees > 0
          ? [{
              key: 'stale',
              label: [
                r.stale.length > 0 ? `${r.stale.length} stale ${r.stale.length === 1 ? 'branch' : 'branches'}` : '',
                r.worktrees > 0 ? `${r.worktrees} other ${r.worktrees === 1 ? 'worktree' : 'worktrees'} (someone may be working in ${r.worktrees === 1 ? 'it' : 'them'})` : '',
              ].filter(Boolean).join(', '),
              acts: [{ key: 'clean-up', label: 'Clean up', isSend: false, text: "list the stale branches, worktrees and open pull requests in this repo and give each a keep, merge or delete call with a reason, in plain words. don't delete, close, merge, push or switch branches until I say yes." }],
            }]
          : []),
      ]
      const starts = setup.hasSkills ? (r.isSetUp ? STARTS : [SETUP, ...STARTS]) : [CATCH_UP]
      return (
        <Box flexDirection="column" gap={1}>
          {nav}
          {installCard}
          {nudgeCard}
          {summaryCard}
          {decisionCard}
          {isDesktop && r.isRead && r.name ? (
            (() => {
              const { Svg } = $.ui.resolve(e)
              const source = startSvg(r)
              return <Svg key="dashboard" source={source} alt={`${r.name} on ${r.branch}: ${r.prs.length} open PRs, ${r.dirty} uncommitted files, ${r.stale.length} stale branches, ${r.worktrees} other worktrees`} {...fit(source, e.props.bodyColumns)} />
            })()
          ) : (
            <Text bold>{r.isRead ? (r.name ? `${r.name} · ${r.branch}` : 'No repo') : 'Reading the repo…'}</Text>
          )}
          {r.error ? <Text dimColor>{r.error}</Text> : null}
          {rows.length > 0 ? <Text bold>Open work</Text> : null}
          {rows.map(row => (
            <Box key={row.key} flexDirection="row" flexWrap="wrap" gap={1} alignItems="center">
              <Text>{row.label}</Text>
              {row.acts.map(a => act(a))}
            </Box>
          ))}
          <Text bold>Start something</Text>
          {setup.hasSkills && !r.isSetUp ? <Text color="#E5342C">This repo is not set up for the skills yet. Press Set up this repo once, first.</Text> : null}
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {starts.map((a, i) => act(a, i === 0 ? 'primary' : 'secondary'))}
          </Box>
          <Text dimColor>Idea and broken fill your prompt: type what you mean after the command, then press Enter. The others send at once.</Text>
          <Box flexDirection="row" gap={1}>
            <Button key="refresh" label="Refresh" onPress={() => readRepo($)} />
          </Box>
        </Box>
      )
    }

    if (current === 'now') {
      const view = nowSvg(f)
      const actions = (
        <Box flexDirection="column" gap={1}>
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {act({ ...view.next.main, key: 'next-step', label: `Next step: ${view.next.main.label}` }, 'primary')}
            {view.next.others.map(m => act(m))}
          </Box>
          <Text dimColor>Next step fills your prompt. Read it, add what it asks for, then press Enter.</Text>
          <Box flexDirection="row" gap={1}>
            <Button key="reset" label="Start over" onPress={() => setFlow($, x => ({ ...EMPTY_FLOW, root: x.root }))} />
          </Box>
        </Box>
      )
      return (
        <Box flexDirection="column" gap={1}>
          {nav}
          {nudgeCard}
          {summaryCard}
          {decisionCard}
          {isDesktop ? (
            (() => {
              const { Svg } = $.ui.resolve(e)
              return <Svg key="now" source={view.source} alt="Where you are on the path from idea to shipped, and the next step" {...fit(view.source, e.props.bodyColumns)} />
            })()
          ) : (
            <Markdown text={nowMd(f)} />
          )}
          {actions}
        </Box>
      )
    }

    const page = guide ?? GUIDE[0]!
    return (
      <Box flexDirection="column" gap={1}>
        {nav}
        {isDesktop ? (
          (() => {
            const { Svg } = $.ui.resolve(e)
            return <Svg key={`guide-${page.id}`} source={page.svg} alt={page.alt} {...fit(page.svg, e.props.bodyColumns)} />
          })()
        ) : (
          <Markdown text={page.md} />
        )}
        {page.id === 'flow' ? (
          <Box flexDirection="column" gap={1}>
            <Text dimColor>Press a step to put its command in your prompt.</Text>
            <Box flexDirection="row" flexWrap="wrap" gap={1}>
              {STEPS.map((s, i) => act({ key: `cmd-${s.id}`, label: `${i + 1} ${s.name}`, text: `${s.cmd} `, isSend: false }))}
            </Box>
          </Box>
        ) : null}
        {page.id === 'ramps' ? (
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {RAMPS.map(r => act({ key: `ramp-${r.cmd}`, label: r.when, text: `${r.cmd} `, isSend: false }))}
          </Box>
        ) : null}
      </Box>
    )
  })
}
