// pstack: say the goal and how to check it, and /poteto-mode picks the playbook.

import type { Advice, Live, Power, PullRequest, SharedId, Task } from '../../types'
import { C, chip, chips, chipW, cut, doc, down, esc, labelOf, lines, MONO, text, W, wrap, type Item } from '../draw'
import { fill, mergeAct, say, type Act, type Column, type GuidePage, type Method, type Out, type Row, type Section } from '../method'
import { SHARED } from '../stages'

const EMPTY_LIVE: Live = { playbook: null, stage: null, advice: {}, power: { model: '', effort: '' }, steps: [], tasks: [], skills: [], prOpened: false, prMerged: false }

// ---------- Map ----------

const STAGES: { name: string; color: string; items: Item[] }[] = [
  {
    name: 'Understand',
    color: C.blue,
    items: [
      { label: '/how', tip: 'How the code works today: runtime flow, key types, the non-obvious parts.' },
      { label: '/why', tip: 'Why it is shaped this way. Digs through git, issues, docs and chat, and cites everything.' },
      { label: '/teach', tip: 'Runs /how and /why and turns them into one plain explanation.' },
      { label: '/recall', tip: 'Catches you up on your own recent work on a topic.' },
    ],
  },
  {
    name: 'Design',
    color: C.indigo,
    items: [
      { label: '/architect', tip: 'Settles types and boundaries before any code, starting from how callers use it.' },
      { label: '/arena', tip: 'Several agents try the same brief. A judge scores them; the best base gets the best parts grafted in.' },
      { label: '/swarm', tip: 'One worker per slice or check, then one PASS / ISSUES / BLOCKED report.' },
      { label: '/interrogate', tip: 'Other models try to break it. Findings sorted into Act on, Consider, Noted, Dismissed.' },
    ],
  },
  {
    name: 'Build',
    color: C.orange,
    items: [
      { label: 'Bug fix', kind: 'play', tip: 'Reproduce first, trace to the cause, then fix and rerun.' },
      { label: 'Feature', kind: 'play', tip: 'Name the data shape first, then build, then prove it.' },
      { label: 'Refactor', kind: 'play', tip: 'Record current behavior, move the structure, prove nothing changed.' },
      { label: 'Perf', kind: 'play', tip: 'Profile, fix the measured cause, show before and after.' },
      { label: '/tdd', tip: 'Smallest failing test first, then the fix, then rerun.' },
      { label: '/unslop', tip: 'Strips filler from the diff, PR text and commit messages.' },
      { label: '/no-comments', tip: 'A fresh reviewer that did not write the code deletes needless comments.' },
    ],
  },
  {
    name: 'Verify',
    color: C.green,
    items: [
      { label: '/blast-radius', tip: 'What else this change could break, proved by running code.' },
      { label: '/create-verification-skill', tip: 'Writes a skill that lets any agent launch and drive your app.' },
      { label: '/maintain-verification-skill', tip: 'Audits that skill against the app and fixes drift.' },
    ],
  },
  {
    name: 'Ship',
    color: C.teal,
    items: [
      { label: 'Open a PR', kind: 'play', tip: 'Small ordered commits from a worktree, cleaned diff, evidence in the description.' },
      { label: 'Babysit', kind: 'play', tip: 'Gets a PR green: conflicts, then review threads, then CI. Never merges.' },
      { label: 'Shipping', kind: 'play', tip: 'Verifies each PR live, then lands only the verified run from the bottom.' },
    ],
  },
  {
    name: 'Overnight',
    color: C.pink,
    items: [
      { label: '/figure-it-out', tip: 'Designs the phases for big or unattended work and keeps a decision log.' },
      { label: '/loop', tip: 'Claude Code’s wake-up loop. Re-checks the finish condition until it passes.' },
      { label: '/show-me-your-work', tip: 'The decision log you audit in the morning.' },
      { label: 'Autopilot', kind: 'play', tip: 'Runs a queue of PRs. Full merges them; Stack leaves one verified stack for you.' },
    ],
  },
]

const ANYTIME: Item[] = [
  { label: '/bro', tip: 'Restates the last reply in plain words.' },
  { label: '/reflect', tip: 'Reviews this chat and turns lessons into edits to skills.' },
  { label: '/automate-me', tip: 'Captures how you work into your own -mode skill.' },
  { label: '/setup-pstack', tip: 'Picks which models each role uses.' },
]

const mapSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'pstack in one picture')
  b += text(20, 54, 'sub mut', 'Say the goal and how to check it. It picks the playbook.')
  b += `<rect class="card" x="16" y="68" width="${W - 32}" height="60" rx="10"/>`
  b += `<text x="30" y="93" font-size="13.5" font-weight="700" font-family="${MONO}"><tspan class="ink">/poteto-mode</tspan><tspan fill="${C.blue}"> &lt;goal&gt;.</tspan><tspan fill="${C.green}"> &lt;how to check&gt;.</tspan></text>`
  b += text(30, 115, 'sm mut', 'e.g. "users get two emails after a retry. repro first, then fix and verify."')
  let y = 148
  STAGES.forEach((stage, i) => {
    const f = chips(126, y + 6, W - 16, stage.items, stage.color)
    const h = f.bottom - y + 6
    if (i > 0) b += down(65, y - 11)
    b += `<rect x="16" y="${y}" width="98" height="${h}" rx="8" fill="${stage.color}"/>`
    b += `<text x="65" y="${y + h / 2 + 4.5}" text-anchor="middle" fill="#fff" class="lab">${stage.name}</text>`
    b += `<rect class="card" x="120" y="${y}" width="${W - 136}" height="${h}" rx="8"/>`
    b += f.svg
    y += h + 14
  })
  b += text(20, y + 14, 'lab mut', 'Anytime')
  const any = chips(126, y, W - 16, ANYTIME, C.gray)
  y = any.bottom + 22
  b += any.svg
  b += `<line class="ln" x1="16" x2="${W - 16}" y1="${y}" y2="${y}"/>`
  y += 22
  b += chip(20, y - 16, { label: '/name', tip: 'A command you type.' }, C.slate)
  b += text(84, y, 'sm mut', 'you type it')
  b += chip(170, y - 16, { label: 'Playbook', kind: 'play', tip: 'A playbook.' }, C.slate)
  b += text(270, y, 'sm mut', 'poteto-mode picks it')
  y += 26
  b += text(20, y, 'sm mut', 'Hover any chip to see what it does.')
  return doc(y + 18, b)
}

// ---------- Router ----------

const ROUTES: { name: string; color: string; say: string[] }[] = [
  { name: 'Investigation', color: C.blue, say: ['"how does X work?"', '"don\'t change code yet."'] },
  { name: 'Bug fix', color: C.red, say: ['"X breaks after Y."', '"repro first, then fix."'] },
  { name: 'Feature', color: C.orange, say: ['"add a --json flag."', '"text output stays the same."'] },
  { name: 'Refactor', color: C.indigo, say: ['"move parsing to one module."', '"zero behavior change."'] },
  { name: 'Perf', color: C.teal, say: ['"startup takes 1.8s."', '"show before and after."'] },
  { name: 'figure-it-out', color: C.pink, say: ['"migrate every caller."', '"I\'m stepping away."'] },
]

const MORE: Item[] = [
  { label: 'Hillclimb', kind: 'play', tip: 'Push one number toward a target, one hypothesis at a time.' },
  { label: 'Runtime forensics', kind: 'play', tip: 'Diagnose a live symptom.' },
  { label: 'Trace forensics', kind: 'play', tip: 'Read a captured trace or profile.' },
  { label: 'Prototype', kind: 'play', tip: 'A throwaway build to answer a question.' },
  { label: 'Visual parity', kind: 'play', tip: 'Make a screen match a reference.' },
  { label: 'Authoring a skill', kind: 'play', tip: 'Write or change a SKILL.md with validation and review.' },
  { label: 'Eval', kind: 'play', tip: 'Measure a skill against test cases.' },
  { label: 'Autonomous run', kind: 'play', tip: 'Keep going alone until the finish condition passes.' },
  { label: 'Opening a PR', kind: 'play', tip: 'Small ordered commits, cleaned diff, evidence.' },
  { label: 'Babysit', kind: 'play', tip: 'Drive a PR to green. Never merges.' },
  { label: 'Shipping', kind: 'play', tip: 'Verify each PR, land the verified run.' },
  { label: 'Autopilot full', kind: 'play', tip: 'A queue of independent PRs, merged by morning.' },
  { label: 'Autopilot stack', kind: 'play', tip: 'A verified stack you land yourself.' },
  { label: 'Orchestrate', kind: 'play', tip: 'A multi-day program run by a coordinator that never writes code.' },
  { label: 'Session pickup', kind: 'play', tip: 'Take over a branch someone left mid-flight.' },
  { label: 'Pause safely', kind: 'play', tip: 'Stop in a state someone can resume.' },
  { label: 'Multi-phase plan', kind: 'play', tip: 'Break a large change into checked phases.' },
  { label: 'Worktree cleanup', kind: 'play', tip: 'Prune worktrees the evidence says are safe.' },
]

const PHRASES: Item[] = [
  { label: '"new task"', kind: 'name', tip: 'Re-match a playbook instead of continuing the last one.' },
  { label: '"don\'t change code yet"', kind: 'name', tip: 'Pins the job to Investigation: read and report only.' },
  { label: '"repro first"', kind: 'name', tip: 'It must reproduce the bug before touching code.' },
  { label: '"show me the evidence"', kind: 'name', tip: 'The reply must carry the real commands and output.' },
  { label: '"fresh worktree"', kind: 'name', tip: 'Keeps parallel agents out of each other’s files.' },
  { label: '"continue"', kind: 'name', tip: 'The mode is sticky. One word keeps the playbook going.' },
  { label: '"I\'m going to bed"', kind: 'name', tip: 'Stops asking questions and keeps working.' },
]

const routeSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'How your words pick a playbook')
  b += text(20, 54, 'sub mut', 'Never list skills in your prompt. The playbook orders them.')
  const cx = W / 2
  b += `<rect class="card" x="${cx - 90}" y="70" width="180" height="32" rx="16"/>`
  b += text(cx, 91, 'lab ink', 'Your prompt', ' text-anchor="middle"')
  b += down(cx, 108)
  b += `<rect x="${cx - 90}" y="120" width="180" height="34" rx="17" fill="${C.slate}" stroke="${C.indigo}" stroke-width="2"/>`
  b += `<text x="${cx}" y="142" text-anchor="middle" fill="#fff" font-size="14" font-weight="700" font-family="${MONO}">/poteto-mode</text>`
  b += text(cx + 98, 134, 'sm mut', 'reads the 21')
  b += text(cx + 98, 148, 'sm mut', 'principles first')
  b += down(cx, 160)
  const cw = (W - 32 - 12) / 2
  let y = 174
  ROUTES.forEach((r, i) => {
    const x = 16 + (i % 2) * (cw + 12)
    const top = y + Math.floor(i / 2) * 78
    b += `<rect class="card" x="${x}" y="${top}" width="${cw}" height="68" rx="9"/>`
    b += `<path d="M${x} ${top + 9} a9 9 0 0 1 9 -9 h${cw - 18} a9 9 0 0 1 9 9 v17 h-${cw} z" fill="${r.color}"/>`
    b += `<text x="${x + 12}" y="${top + 18}" fill="#fff" class="lab">${esc(r.name)}</text>`
    b += lines(x + 12, top + 43, 'body ink', r.say, 17, ' font-style="italic"')
  })
  y += 3 * 78
  b += down(cx, y)
  y += 12
  b += `<rect x="16" y="${y}" width="${W - 32}" height="34" rx="9" fill="${C.green}"/>`
  b += `<text x="${cx}" y="${y + 22}" text-anchor="middle" fill="#fff" class="lab">Verify and report, with the evidence</text>`
  y += 62
  b += text(20, y, 'lab ink', '18 more playbooks it can pick')
  const more = chips(20, y + 10, W - 16, MORE, C.gray)
  b += more.svg
  y = more.bottom + 30
  b += text(20, y, 'lab ink', 'Words that steer it')
  const steer = chips(20, y + 10, W - 16, PHRASES, C.blue)
  b += steer.svg
  return doc(steer.bottom + 20, b)
}

// ---------- Design ----------

const RUNGS: { level: number; when: string; use: string[]; note?: string }[] = [
  { level: 5, when: 'Contested design that is costly to reverse', use: ['/architect', '/interrogate'] },
  { level: 4, when: 'Crosses functions or moves ownership', use: ['/architect'], note: 'brings /arena with it' },
  { level: 3, when: 'One decision: a name, a format, an algorithm', use: ['/arena'] },
  { level: 2, when: 'A small finished change you are unsure of', use: ['/interrogate'] },
  { level: 1, when: 'Most changes', use: [], note: 'nothing extra' },
]

const box = (x: number, y: number, w: number, label: string, color: string) =>
  `<rect x="${x}" y="${y}" width="${w}" height="24" rx="6" fill="${color}"/><text x="${x + w / 2}" y="${y + 16}" text-anchor="middle" fill="#fff" font-size="11.5" font-weight="600">${esc(label)}</text>`

const designSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'How much design does it need?')
  b += text(20, 54, 'sub mut', 'Climb only as high as the risk. poteto-mode climbs on its own.')
  let y = 72
  b += text(20, y + 8, 'sm mut', 'more scrutiny ↑')
  y += 18
  for (const r of RUNGS) {
    b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="54" rx="9"/>`
    for (let i = 0; i < 5; i++) {
      b += `<rect x="${28 + i * 9}" y="${y + 34 - i * 5}" width="6" height="${8 + i * 5}" rx="1.5" fill="${i < r.level ? C.indigo : '#E5E5EA'}"/>`
    }
    b += lines(84, y + 23, 'body ink', wrap(r.when, 30), 16)
    let cy = y + (r.use.length > 1 ? 3 : 15)
    for (const u of r.use) {
      b += chip(W - 28 - chipW({ label: u, tip: '' }), cy, { label: u, tip: u }, C.indigo)
      cy += 25
    }
    if (r.note) b += text(W - 28, y + (r.use.length ? 48 : 31), 'sm mut', r.note, ' text-anchor="end"')
    y += 60
  }
  y += 18
  const pw = (W - 32 - 12) / 2
  const panel = (x: number, title: string, sub: string) =>
    `<rect class="card" x="${x}" y="${y}" width="${pw}" height="196" rx="10"/>` +
    `<text x="${x + 12}" y="${y + 22}" font-size="13.5" font-weight="700" font-family="${MONO}" class="ink">${esc(title)}</text>` +
    text(x + 12, y + 39, 'sm mut', sub)
  const ax = 16
  b += panel(ax, '/arena', 'one brief, many tries')
  b += box(ax + pw / 2 - 40, y + 52, 80, 'one brief', C.slate)
  for (let i = 0; i < 3; i++) {
    const bx = ax + 14 + i * ((pw - 28 - 48) / 2)
    b += `<line class="ln" stroke-width="1.5" x1="${ax + pw / 2}" y1="${y + 76}" x2="${bx + 24}" y2="${y + 92}"/>`
    b += box(bx, y + 92, 48, `try ${'ABC'[i]}`, C.indigo)
    b += `<line class="ln" stroke-width="1.5" x1="${bx + 24}" y1="${y + 116}" x2="${ax + pw / 2}" y2="${y + 132}"/>`
  }
  b += box(ax + pw / 2 - 40, y + 132, 80, 'judge', C.gray)
  b += down(ax + pw / 2, y + 160)
  b += box(ax + 14, y + 168, pw - 28, 'best base + best parts', C.green)
  const sx = 16 + pw + 12
  b += panel(sx, '/swarm', 'split the work, one report')
  for (let i = 0; i < 3; i++) {
    const bx = sx + 14 + i * ((pw - 28 - 52) / 2)
    b += box(bx, y + 52, 52, `slice ${i + 1}`, C.teal)
    b += down(bx + 26, y + 82)
    b += box(bx, y + 92, 52, 'check', C.gray)
    b += `<line class="ln" stroke-width="1.5" x1="${bx + 26}" y1="${y + 116}" x2="${sx + pw / 2}" y2="${y + 132}"/>`
  }
  b += box(sx + pw / 2 - 50, y + 132, 100, 'one report', C.slate)
  const tags: [string, string][] = [['PASS', C.green], ['ISSUES', C.orange], ['BLOCKED', C.red]]
  let tx = sx + 14
  for (const [label, color] of tags) {
    const w = label.length * 7 + 14
    b += box(tx, y + 168, w, label, color)
    tx += w + 6
  }
  y += 196 + 28
  b += text(20, y, 'lab ink', '/interrogate sorts every finding')
  b += text(20, y + 17, 'sm mut', 'It applies nothing on its own. Read the dismissals too.')
  const buckets: [string, string][] = [['Act on', C.red], ['Consider', C.orange], ['Noted', C.gray], ['Dismissed', C.slate]]
  const bw = (W - 32 - 18) / 4
  buckets.forEach(([label, color], i) => {
    b += `<rect x="${16 + i * (bw + 6)}" y="${y + 28}" width="${bw}" height="34" rx="8" fill="${color}"/>`
    b += `<text x="${16 + i * (bw + 6) + bw / 2}" y="${y + 50}" text-anchor="middle" fill="#fff" class="lab">${label}</text>`
  })
  return doc(y + 80, b)
}

// ---------- Overnight ----------

const CONTRACT: [string, string][] = [
  ['Goal', 'migrate every caller to the new parser'],
  ['Done means', 'zero old callers, all fixtures pass'],
  ['Fresh worktree', 'keeps it off your other work'],
  ['Permission', 'commit freely; no merge, deploy or post'],
  ['Escape hatch', '"if truly stuck, stop and write up why"'],
]

const LOOP = ['Check the finish line', 'Smallest change', 'Verify for real', 'Keep or discard', 'Log one decision']

const BIG: Item[] = [
  { label: 'Autopilot full', kind: 'play', tip: 'Independent PRs merged by morning. A fresh verifier clears every merge.' },
  { label: 'Autopilot stack', kind: 'play', tip: 'One verified stack. Nothing merges; you land it.' },
  { label: 'Orchestrate', kind: 'play', tip: 'A multi-day program. A coordinator runs subagents and never writes code.' },
]

const overnightSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'Leave it running overnight')
  b += text(20, 54, 'sub mut', 'Five lines make it safe to walk away.')
  let y = 70
  b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${CONTRACT.length * 32 + 14}" rx="10"/>`
  CONTRACT.forEach(([k, v], i) => {
    const ry = y + 14 + i * 32
    b += `<circle cx="38" cy="${ry + 11}" r="11" fill="${C.pink}"/>`
    b += `<text x="38" y="${ry + 15.5}" text-anchor="middle" fill="#fff" font-size="12" font-weight="700">${i + 1}</text>`
    b += text(58, ry + 15.5, 'lab ink', k)
    b += text(166, ry + 15.5, 'body mut', v)
  })
  y += CONTRACT.length * 32 + 14 + 30
  b += text(20, y, 'lab ink', 'What it does all night')
  const cx = W / 2
  const cy = y + 150
  const r = 118
  b += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${C.pink}" stroke-width="2.5" stroke-opacity=".55"/>`
  const angle = (i: number) => -90 + i * 72
  for (let i = 0; i < LOOP.length; i++) {
    const mid = ((angle(i) + 36) * Math.PI) / 180
    const px = cx + r * Math.cos(mid)
    const py = cy + r * Math.sin(mid)
    b += `<path d="M-6,-6 L6,0 L-6,6z" fill="${C.pink}" transform="translate(${px.toFixed(1)} ${py.toFixed(1)}) rotate(${(angle(i) + 36 + 90).toFixed(1)})"/>`
  }
  LOOP.forEach((label, i) => {
    const a = (angle(i) * Math.PI) / 180
    const px = cx + r * Math.cos(a)
    const py = cy + r * Math.sin(a)
    const w = label.length * 7 + 22
    b += `<rect x="${(px - w / 2).toFixed(1)}" y="${(py - 14).toFixed(1)}" width="${w}" height="28" rx="14" fill="${i === 3 ? C.slate : C.pink}"/>`
    b += `<text x="${px.toFixed(1)}" y="${(py + 4.5).toFixed(1)}" text-anchor="middle" fill="#fff" font-size="12" font-weight="700">${esc(label)}</text>`
  })
  b += `<text x="${cx}" y="${cy - 4}" text-anchor="middle" fill="${C.pink}" font-size="16" font-weight="700" font-family="${MONO}">/loop</text>`
  b += text(cx, cy + 15, 'sm mut', 'until "done" is true', ' text-anchor="middle"')
  y = cy + r + 40
  b += `<rect x="16" y="${y}" width="${W - 32}" height="52" rx="10" fill="${C.red}" fill-opacity=".12" stroke="${C.red}" stroke-opacity=".5"/>`
  b += text(30, y + 21, 'lab ink', '"Work on this for 4 hours" is not a finish line.')
  b += text(30, y + 39, 'body mut', 'Give it a check that can pass or fail.')
  y += 76
  b += text(20, y, 'lab ink', 'Next morning')
  b += chip(20, y + 12, { label: '/show-me-your-work catch me up', tip: 'Summarizes the night from the decision log. A second model reviews it first.' }, C.pink)
  b += text(20, y + 58, 'body ink', 'Read its Attention section first,')
  b += text(20, y + 75, 'body ink', 'then only the log rows it points at.')
  y += 106
  b += text(20, y, 'lab ink', 'A whole queue instead of one task?')
  const big = chips(20, y + 10, W - 16, BIG, C.pink)
  b += big.svg
  return doc(big.bottom + 20, b)
}

// ---------- Principles ----------

const GROUPS: { name: string; color: string; items: Item[] }[] = [
  {
    name: 'How much to build',
    color: C.blue,
    items: [
      { label: 'Laziness protocol', kind: 'name', tip: 'Prefer deletion and the smallest change that solves it.' },
      { label: 'Foundational thinking', kind: 'name', tip: 'Choose the core data structures before writing logic.' },
      { label: 'Redesign from first principles', kind: 'name', tip: 'Fit a new requirement in as if it had been there from day one.' },
      { label: 'Subtract before you add', kind: 'name', tip: 'Remove dead weight before building on top of it.' },
      { label: 'Minimize reader load', kind: 'name', tip: 'Collapse layers and hidden state a reader must hold in their head.' },
      { label: 'Outcome-oriented execution', kind: 'name', tip: 'Go straight to the target design; skip throwaway in-between states.' },
      { label: 'Experience first', kind: 'name', tip: 'Choose the user’s result over what is easy to build.' },
      { label: 'Exhaust the design space', kind: 'name', tip: 'With no precedent, build two or three competing prototypes.' },
      { label: 'Build the lever', kind: 'name', tip: 'Write the script that does or proves the work, so anyone can rerun it.' },
    ],
  },
  {
    name: 'Where state and rules live',
    color: C.indigo,
    items: [
      { label: 'Model the domain', kind: 'name', tip: 'Put a repeated rule in one structure, not scattered ifs.' },
      { label: 'Boundary discipline', kind: 'name', tip: 'Validate at the edge, then trust internal types.' },
      { label: 'Type system discipline', kind: 'name', tip: 'Make illegal states impossible to write.' },
      { label: 'Make operations idempotent', kind: 'name', tip: 'Running it twice ends in the same state as once.' },
      { label: 'Migrate callers, then delete legacy', kind: 'name', tip: 'Move every caller and delete the old API in one wave.' },
      { label: 'Separate before serializing', kind: 'name', tip: 'Remove the sharing before adding locks.' },
    ],
  },
  {
    name: 'What counts as proof',
    color: C.green,
    items: [
      { label: 'Prove it works', kind: 'name', tip: 'Check the real app or output, not a green build.' },
      { label: 'Fix root causes', kind: 'name', tip: 'Reproduce and trace to the cause before changing code.' },
      { label: 'Sequence verifiable units', kind: 'name', tip: 'Finish each small step with a check before the next.' },
    ],
  },
  {
    name: 'Parallel work',
    color: C.teal,
    items: [
      { label: 'Guard the context window', kind: 'name', tip: 'Send bulk reading to subagents; keep findings in the main chat.' },
      { label: 'Never block on the human', kind: 'name', tip: 'Do the reversible work, then show the result.' },
    ],
  },
  { name: 'Meta', color: C.pink, items: [{ label: 'Encode lessons in structure', kind: 'name', tip: 'Advice you gave twice becomes a lint, check or script.' }] },
]

const principlesSvg = () => {
  let b = ''
  b += text(20, 34, 'h ink', 'Principles are names you say')
  b += text(20, 54, 'sub mut', 'Mid-task, say the name to steer it. Hover for the rule.')
  b += `<rect class="card" x="16" y="68" width="${W - 32}" height="34" rx="10"/>`
  b += `<text x="30" y="90" font-size="13" font-family="${MONO}" class="ink">"apply prove it works. show me the real output."</text>`
  let y = 130
  for (const g of GROUPS) {
    b += `<rect x="20" y="${y - 11}" width="4" height="14" rx="2" fill="${g.color}"/>`
    b += text(30, y, 'lab ink', `${g.name}  ·  ${g.items.length}`)
    const f = chips(20, y + 10, W - 16, g.items, g.color)
    b += f.svg
    y = f.bottom + 32
  }
  b += lines(20, y - 6, 'body mut', wrap('Each reply names the principle it applied and the decision it changed. A name with no decision behind it was name-dropped.', 62), 17)
  return doc(y + 34, b)
}

// ---------- Recipes ----------

// The session's own model writes these plans, since it can read the repo and
// the ticket. The mod only hands it the prompt.
const PLAN_OVERNIGHT =
  "/poteto-mode plan an overnight run for <ticket>. don't start it. read the ticket and the repo, find the real commands that prove it's done, and write the overnight prompt: goal, done means, fresh worktree, permissions, escape hatch, and \"open a PR but do not merge, deploy, or post\". then list anything that would stop it overnight: permission prompts, missing tests, the Mac sleeping. wait for my go."
const PLAN_TASK = "/poteto-mode help me write the prompt for: <rough goal in your words>. read the repo, find how we'd prove it works, give me the prompt. don't start."
const OVERNIGHT_RUN =
  "/poteto-mode im going to bed. <goal> in a fresh worktree off main. done means <checks that pass or fail>. keep a decision log. don't ask me before committing. open a PR when done, but do not merge, deploy, or post anything. /loop until done. if you're truly stuck after a few hours, stop and write up why."

const RECIPES: { title: string; prompt: string }[] = [
  { title: 'Plan an overnight run', prompt: PLAN_OVERNIGHT },
  { title: 'Plan any task', prompt: PLAN_TASK },
  { title: 'Fix a bug', prompt: '/poteto-mode <symptom>. repro first. if there is a cheap test path, /tdd it. then fix and verify.' },
  { title: 'Add a feature', prompt: '/poteto-mode add <behavior>. <what must not change> stays the same. show me the evidence.' },
  { title: 'Understand code', prompt: 'use /how to understand <area>. then use /why to find out why it changed recently.' },
  { title: 'Second opinion on a plan', prompt: 'ask /arena for a second opinion on this thread and our approach' },
  { title: 'Skeptical review', prompt: "/interrogate the whole branch, skeptically. don't change anything yet. no nitpicks unless it's a real bug." },
  { title: 'Open a PR', prompt: '/poteto-mode open the pr. small ordered commits, evidence in the description.' },
  { title: 'Get a PR green', prompt: '/poteto-mode babysit this pr. get it green.' },
  { title: 'Overnight run', prompt: OVERNIGHT_RUN },
  { title: 'Morning audit', prompt: '/show-me-your-work catch me up on what you did last night' },
  { title: 'Catch me up', prompt: '/recall catch me up on <topic>' },
  { title: 'Say it plainly', prompt: '/bro' },
]

const PITFALLS: [string, string][] = [
  ['"use /how, then /architect, then /arena"', 'State the goal. The playbook orders the steps.'],
  ['"make it better"', 'Give a check that can pass or fail.'],
  ['"the build passed, so it works"', 'Show the real command, flow or output.'],
  ['Two agents in one worktree', 'One worktree per attempt.'],
  ['/arena to cover many slices', '/swarm for slices. /arena for one brief.'],
  ['Accepting every review comment', 'Let /interrogate sort and dismiss with reasons.'],
]

const pitfallsSvg = () => {
  let b = ''
  b += text(20, 30, 'h ink', 'Mistakes everyone makes once')
  const cw = (W - 32 - 10) / 2
  b += text(28, 56, 'lab', 'Instead of', ` fill="${C.red}"`)
  b += text(16 + cw + 22, 56, 'lab', 'Do this', ` fill="${C.green}"`)
  let y = 66
  for (const [bad, good] of PITFALLS) {
    const left = wrap(bad, 30)
    const right = wrap(good, 30)
    const h = Math.max(left.length, right.length) * 16 + 18
    b += `<rect x="16" y="${y}" width="${cw}" height="${h}" rx="8" fill="${C.red}" fill-opacity=".1"/>`
    b += `<rect x="${16 + cw + 10}" y="${y}" width="${cw}" height="${h}" rx="8" fill="${C.green}" fill-opacity=".12"/>`
    b += lines(28, y + 22, 'body ink', left, 16)
    b += lines(16 + cw + 22, y + 22, 'body ink', right, 16)
    y += h + 8
  }
  return doc(y + 10, b)
}

// ---------- You are here ----------

const PLAYBOOK_STAGE: Record<string, number> = {
  investigation: 0,
  'runtime-forensics': 0,
  'trace-forensics': 0,
  'session-pickup': 0,
  prototype: 1,
  'multi-phase-plan': 1,
  'bug-fix': 2,
  feature: 2,
  refactoring: 2,
  'perf-issue': 2,
  hillclimb: 2,
  'visual-parity': 2,
  'authoring-a-skill': 2,
  eval: 3,
  'opening-a-pr': 4,
  babysit: 4,
  shipping: 4,
  'worktree-cleanup': 4,
  'pause-safely': 5,
  'autonomous-run': 5,
  'autopilot-full': 5,
  'autopilot-stack': 5,
  orchestrate: 5,
}

const SKILL_STAGE: Record<string, number> = {
  how: 0,
  why: 0,
  teach: 0,
  recall: 0,
  architect: 1,
  arena: 1,
  swarm: 1,
  interrogate: 1,
  tdd: 2,
  unslop: 2,
  'no-comments': 2,
  'blast-radius': 3,
  'create-verification-skill': 3,
  'maintain-verification-skill': 3,
  'figure-it-out': 5,
  'show-me-your-work': 5,
}

const TRACKED = new Set([...Object.keys(SKILL_STAGE), 'poteto-mode', 'bro', 'reflect', 'automate-me'])
const BUILD = new Set(['bug-fix', 'feature', 'refactoring', 'perf-issue', 'hillclimb', 'visual-parity', 'authoring-a-skill'])
const FINDINGS = new Set(['investigation', 'runtime-forensics', 'trace-forensics'])
const LONG_RUNS = new Set(['autonomous-run', 'autopilot-full', 'autopilot-stack', 'orchestrate', 'figure-it-out'])

const playbookName = (slug: string) => (slug.charAt(0).toUpperCase() + slug.slice(1).replace(/-/g, ' ')).replace(/\bpr\b/, 'PR')

const parseSteps = (md: string) =>
  md
    .split('\n')
    .map(line => /^\d+\.\s+(.*)$/.exec(line)?.[1])
    .filter((s): s is string => Boolean(s))
    .map(s => s.replace(/[*`]/g, '').split(/(?<=[a-z)])[.;:]\s/)[0] ?? s)
    .map(s => cut(s.split(' ').slice(0, 8).join(' '), 48))

const stageAt = (n: number | undefined): SharedId | null => (n === undefined ? null : (SHARED[n]?.id ?? null))

// A step that starts moves the stage when its words name one. Matched in order,
// so "Reproduce the duplicate write" is reading, not building.
const TASK_STAGE: [RegExp, SharedId][] = [
  [/\b(open (the|a) pr|pull request|push|land|babysit|ship it)\b/i, 'ship'],
  [/\b(verify|review|prove|blast[- ]radius|interrogate|audit|evidence)\b/i, 'verify'],
  [/\b(design|architect|spec|plan|decide|ticket|tickets)\b/i, 'design'],
  [/\b(read|explore|map|trace|investigate|reproduce|repro|understand|recall|find)\b/i, 'understand'],
  [/\b(implement|build|fix|write|add|refactor|code|test)\b/i, 'build'],
]

export const taskStage = (subject: string): SharedId | null => TASK_STAGE.find(([re]) => re.test(subject))?.[1] ?? null

type Next = { label: string; prompt: string; why: string }

const nextMove = (l: Live): { now: Next; then: string[] } => {
  const open = l.tasks.filter(t => t.status !== 'completed')
  const pb = l.playbook ?? ''
  const used = new Set(l.skills)
  if (!l.playbook && l.tasks.length === 0 && l.skills.length === 0) {
    return {
      now: { label: 'Start with a goal and a check', prompt: '/poteto-mode <goal>. <how you will know it is done>.', why: 'poteto-mode picks the playbook from your words.' },
      then: ['It reads the principles', 'then lists the playbook steps'],
    }
  }
  const current = open.find(t => t.status === 'in_progress') ?? open[0]
  if (current) {
    return { now: { label: 'Let it keep going', prompt: 'continue', why: `It is on: ${current.subject}` }, then: open.filter(t => t !== current).slice(0, 2).map(t => t.subject) }
  }
  if (l.prMerged || pb === 'shipping') {
    return { now: { label: 'Start the next task', prompt: '/poteto-mode new task. <goal>. <how to check>.', why: 'Say "new task" so it picks a fresh playbook.' }, then: [] }
  }
  if (pb === 'babysit') {
    return { now: { label: 'Land it', prompt: '/poteto-mode land the stack.', why: 'Babysit stops at green. Shipping verifies each PR, then lands it.' }, then: ['Start the next task'] }
  }
  if (l.prOpened || pb === 'opening-a-pr') {
    return { now: { label: 'Get the PR green', prompt: '/poteto-mode babysit this pr. get it green.', why: 'It works through conflicts, review threads and CI. It never merges.' }, then: ['Land it'] }
  }
  if (FINDINGS.has(pb)) {
    return { now: { label: 'Act on what it found', prompt: '/poteto-mode new task. fix <what it found>. repro first, then fix and verify.', why: 'An investigation only reports. The fix is a new task.' }, then: ['Open the PR'] }
  }
  if (LONG_RUNS.has(pb) || used.has('figure-it-out')) {
    return { now: { label: 'Audit the run', prompt: '/show-me-your-work catch me up on what you did', why: 'Read its Attention section first.' }, then: ['Open the PR'] }
  }
  if (BUILD.has(pb) && !used.has('blast-radius')) {
    return { now: { label: 'Check what else it could break', prompt: '/blast-radius', why: 'It proves the one fact the change is safe because of.' }, then: ['Open the PR', 'Get it green'] }
  }
  if (BUILD.has(pb)) {
    return { now: { label: 'Open the PR', prompt: '/poteto-mode open the pr. small ordered commits, evidence in the description.', why: 'It cleans the diff and puts the evidence in the description.' }, then: ['Get it green', 'Land it'] }
  }
  return { now: { label: 'Review it skeptically', prompt: "/interrogate the whole branch, skeptically. don't change anything yet.", why: 'Other models try to break it before it ships.' }, then: ['Open the PR'] }
}

// ---------- Step advice ----------

type Family = 'Haiku' | 'Sonnet' | 'Opus' | 'Fable'
type Effort = 'Low' | 'Medium' | 'High'
type Tier = { model: Family; effort: Effort; why: string }

// Matched in order against a step's words. The roles follow pstack's model
// roles: medium is the default, high is for judgment, design and hard bugs,
// low is for mechanical edits.
const TIER_RULES: [RegExp, Tier][] = [
  [/\b(rename|sweep|bump|typo|format|lint|move files?|delete dead)\b/i, { model: 'Haiku', effort: 'Low', why: 'a mechanical edit' }],
  [/\b(spec|write[- ]?up|write the spec|describe|summar|pr description|docs?|explain|reply|rule on|for your ruling)\b/i, { model: 'Fable', effort: 'High', why: 'judgment and prose' }],
  [/\b(decide|decision|choose|weigh|trade-?offs?|polic(y|ies)|authori[sz]|permission|security|sealed|custody|provenance)\b/i, { model: 'Fable', effort: 'High', why: 'a call that is costly to unwind' }],
  [/\b(architect|design|root cause|cause|binary-?search|concurren|race|algorithm|schema|data shape)\b/i, { model: 'Opus', effort: 'High', why: 'design or a hard bug' }],
  [/\b(read|explore|map|trace|investigate|find|list|inventory|gather|look|check|audit|recall)\b/i, { model: 'Sonnet', effort: 'Medium', why: 'reading and mapping' }],
]
const DEFAULT_TIER: Tier = { model: 'Sonnet', effort: 'Medium', why: 'routine build work' }

const tierFor = (subject: string): Tier => TIER_RULES.find(([re]) => re.test(subject))?.[1] ?? DEFAULT_TIER

const FAMILY_RANK: Record<Family, number> = { Haiku: 1, Sonnet: 2, Opus: 3, Fable: 3 }
const EFFORT_RANK: Record<string, number> = { low: 1, medium: 2, high: 3, xhigh: 4, max: 5 }

const familyOf = (model: string): Family | null => {
  const m = model.toLowerCase()
  if (m.includes('fable')) return 'Fable'
  if (m.includes('opus')) return 'Opus'
  if (m.includes('sonnet')) return 'Sonnet'
  if (m.includes('haiku')) return 'Haiku'
  return null
}

const capital = (s: string) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s)

type Fit = { kind: 'under' | 'over' | 'match' | 'unknown'; text: string }

const powerFit = (need: Tier, power: Power): Fit => {
  const family = familyOf(power.model)
  const effort = EFFORT_RANK[power.effort.toLowerCase()]
  if (!family || effort === undefined) return { kind: 'unknown', text: `Needs ${need.model} · ${need.effort}. The session's model shows after its next step.` }
  const now = `${family} · ${capital(power.effort)}`
  const needEffort = EFFORT_RANK[need.effort.toLowerCase()] ?? 2
  const wrongFamily = need.model === 'Fable' && family !== 'Fable'
  if (wrongFamily || FAMILY_RANK[family] < FAMILY_RANK[need.model] || effort < needEffort) {
    return { kind: 'under', text: `Needs ${need.model} · ${need.effort} for ${need.why}. This session is on ${now}. Switch now if this step matters.` }
  }
  if (FAMILY_RANK[family] > FAMILY_RANK[need.model] || effort > needEffort) {
    return { kind: 'over', text: `${need.model} · ${need.effort} is enough for ${need.why}. This session is on ${now}, which costs more.` }
  }
  return { kind: 'match', text: `${now} fits ${need.why}.` }
}

const ADVICE_PROMPT = (l: Live, step: string) =>
  'You coach the user, who runs AI coding agents but does not write code. ' +
  'An agent is working through a pstack playbook, a checklist it follows step by step. ' +
  'Write about the step it is on now.\n' +
  'Line 1 starts with "WHAT:" and says in plain words what the agent is doing in this step and why it matters.\n' +
  'Each line is one sentence under 22 words. Use short everyday words. No dashes, no markdown, no lists.\n\n' +
  `Playbook: ${l.playbook ? playbookName(l.playbook) : 'none named'}\n` +
  `All steps:\n${l.tasks.map(t => `- ${t.subject}`).join('\n')}\n` +
  `Step now: ${step}`

// WHAT is the step; every other "name: line" is one method's line.
export const parseAdvice = (said: string): Advice | null => {
  const what = /WHAT:\s*(.+)/i.exec(said)?.[1]?.trim()
  if (!what) return null
  const would: Record<string, string> = {}
  for (const line of said.split('\n')) {
    const found = /^[\s*-]*([a-z][\w-]*)\s*:\s*(.+)$/i.exec(line)
    const name = found?.[1]?.toLowerCase()
    if (found && name && name !== 'what' && name !== 'move') would[name] = (found[2] ?? '').trim()
  }
  return { what, would, isReady: true }
}

const norm = (l: Live): Live => ({ ...EMPTY_LIVE, ...l, stage: l.stage ?? null, advice: l.advice ?? {}, power: l.power ?? EMPTY_LIVE.power })

// A step the agent is under-powered for turns the next move into a switch.
const moveFor = (l: Live) => {
  const running = l.tasks.find(t => t.status === 'in_progress')
  const need = running ? tierFor(running.subject) : null
  const base = nextMove(l)
  if (need && powerFit(need, l.power).kind === 'under') {
    return { now: { label: `Switch to ${need.model} · ${need.effort}`, prompt: 'continue', why: 'Stop it if this step matters, pick the model in the selector, then say continue.' }, then: base.then }
  }
  return base
}

// What pstack would do at each stage when Haiku has not said, or cannot.
const WOULD: Record<SharedId, string> = {
  understand: 'Map how the code works with /how and /why before changing anything.',
  design: 'Settle the types and boundaries with /architect, and /arena for one hard call.',
  build: 'Follow the playbook: a repro or failing test first, then the smallest fix.',
  verify: 'Prove it on the real app or output, and run /blast-radius on the change.',
  ship: 'Open small ordered commits as a PR with the evidence, and babysit it green.',
  overnight: 'Give it a finish line it can check, then audit the night with /show-me-your-work.',
}
const WOULD_IDLE = 'Say the goal and how to check it to /poteto-mode, and let it pick the playbook.'

const running = (l: Live) => l.tasks.find(t => t.status === 'in_progress')

const column = (raw: Live, would: string | undefined): Column => {
  const l = norm(raw)
  const stage = SHARED.find(x => x.id === l.stage)
  const rows: Row[] =
    l.tasks.length > 0
      ? l.tasks.slice(0, 10).map(t => {
          const need = tierFor(t.subject)
          return { label: t.subject, mark: t.status === 'completed' ? 'done' : t.status === 'in_progress' ? 'now' : 'todo', tag: `${need.model} · ${need.effort}` }
        })
      : l.steps.slice(0, 10).map(x => ({ label: x, mark: 'todo' as const }))
  const sections: Section[] = []
  const task = running(l)
  if (task) {
    const advice = l.advice[task.id]
    sections.push({ title: "What's happening", body: advice?.what ?? 'Working out advice for this step…' })
    const fit = powerFit(tierFor(task.subject), l.power)
    sections.push({ title: 'Power', body: fit.text, tone: fit.kind === 'under' ? 'bad' : fit.kind === 'match' ? 'good' : undefined })
  } else if (rows.length === 0) {
    sections.push({ title: 'Nothing running yet', body: l.playbook ? 'Waiting for its task list.' : 'Start a task with /poteto-mode and this fills in.' })
  }
  const finished = l.tasks.filter(t => t.status === 'completed').length
  return {
    stage: stage?.name ?? 'Not started',
    title: l.playbook ? `${playbookName(l.playbook)} playbook` : l.tasks.length ? `Task list · ${finished} of ${l.tasks.length} done` : 'No playbook yet',
    rows,
    sections,
    would: would ?? (l.stage ? WOULD[l.stage] : WOULD_IDLE),
  }
}

const brief = (raw: Live) => {
  const l = norm(raw)
  const task = running(l)
  return `stage ${l.stage ?? 'not started'}${l.playbook ? `, ${playbookName(l.playbook)} playbook` : ''}${task ? `, step "${task.subject}"` : ''}`
}

// ---------- Guide pages ----------

const GUIDE: GuidePage[] = [
  {
    id: 'map',
    label: 'Map',
    svg: mapSvg(),
    alt: 'pstack stages from understand to overnight, with the commands for each',
    md: `### pstack in one picture\n\n\`/poteto-mode <goal>. <how to check>.\`\n\n${STAGES.map(s => `**${s.name}:** ${s.items.map(labelOf).join(', ')}`).join('\n\n')}\n\n**Anytime:** ${ANYTIME.map(labelOf).join(', ')}`,
    note: 'Press a command to put it in your prompt, then add what it is for.',
    rows: [...STAGES, { name: 'Anytime', color: C.gray, items: ANYTIME }]
      .map(st => ({ label: st.name, acts: st.items.filter(it => it.label.startsWith('/')).map(it => fill(`cmd-${it.label}`, it.label, `${it.label} `)) }))
      .filter(r => r.acts.length > 0),
  },
  {
    id: 'route',
    label: 'Router',
    svg: routeSvg(),
    alt: 'How poteto-mode routes a prompt to a playbook',
    md: `### How your words pick a playbook\n\n${ROUTES.map(r => `- **${r.name}**: ${r.say.join(' ')}`).join('\n')}\n\nThen: verify and report, with the evidence.\n\n**Words that steer:** ${PHRASES.map(p => p.label).join(', ')}`,
  },
  {
    id: 'design',
    label: 'Design',
    svg: designSvg(),
    alt: 'A ladder of how much design work a change needs',
    md: `### How much design does it need?\n\n${RUNGS.map(r => `- ${r.when}: ${r.use.join(' then ') || r.note}`).join('\n')}\n\n/arena tries one brief many ways. /swarm splits the work and returns one report.`,
  },
  {
    id: 'overnight',
    label: 'Overnight',
    svg: overnightSvg(),
    alt: 'The overnight contract and the loop it runs',
    md: `### Leave it running overnight\n\n${CONTRACT.map(([k, v], i) => `${i + 1}. **${k}**: ${v}`).join('\n')}\n\nLoop: ${LOOP.join(' → ')}\n\nNext morning: \`/show-me-your-work catch me up\`, read Attention first.`,
    rows: [{ acts: [{ ...fill('plan-overnight', "Plan tonight's run", PLAN_OVERNIGHT), isPrimary: true }, fill('overnight-run', 'Start a run', OVERNIGHT_RUN)] }],
  },
  {
    id: 'principles',
    label: 'Principles',
    svg: principlesSvg(),
    alt: 'The 21 pstack principles in five groups',
    md: `### Principles are names you say\n\n${GROUPS.map(g => `**${g.name}:** ${g.items.map(i => i.label).join(', ')}`).join('\n\n')}`,
  },
  {
    id: 'recipes',
    label: 'Recipes',
    svg: pitfallsSvg(),
    alt: 'Common pstack mistakes and what to do instead',
    md: `### Mistakes everyone makes once\n\n${PITFALLS.map(([bad, good]) => `- Instead of ${bad}: ${good}`).join('\n')}`,
    recipes: RECIPES,
  },
]

// ---------- Start ----------

const PLAN_ANY =
  'ask me what I want to do with a multiple-choice question of likely next jobs in this repo, plus an other option. then write the /poteto-mode prompt with a finish line we can check, show it to me, and wait for my go.'

const STARTS: Act[] = [
  say(
    'start-recall',
    'Catch me up',
    '/recall catch me up on my recent work in this repo: open branches and PRs, the last few sessions, and what I was about to build next. keep it short. end with a multiple-choice question of what to continue, with finishing open work first.',
  ),
  say(
    'start-assess',
    'Assess the project',
    "/poteto-mode assess this whole project, read only. say in plain words what it does and what state it is in: open work, tests, known bugs, open tickets, and the weakest parts of the code. then rank the 5 moves that would take it furthest for the least work, in this order of priority: data loss and correctness bugs first, then finishing open work, then AI model routing, then architecture that will fight the next year, then UX friction, then new features. within a tier, favor the most value for the least work, each with how we would check it worked and the model and effort it needs. finishing open work counts as a move. end with a multiple-choice question of which to take on. don't change anything.",
  ),
  say(
    'start-ticket',
    'Pick a ticket',
    "list this repo's open ready-for-agent tickets and ask me to pick one with a multiple-choice question. when I pick, start /poteto-mode implement <that ticket>, with the ticket's acceptance check as done means. open a PR when done, don't merge.",
  ),
  {
    ...say(
      'start-levelup',
      'Level up (new model)',
      "run the bldg-house:project-level-up skill on this repo. a new frontier model is out: use the model this session runs on unless I name another. don't write any files; give me the review pack and the ranked patch queue, then ask which to take on with a multiple-choice question.",
    ),
    needs: 'bldg-house@',
  },
  say(
    'start-bug',
    'Fix a bug',
    "I want to fix a bug. ask me what's broken with a multiple-choice question built from recent errors, failing tests and open issues you can find, plus an other option. then start /poteto-mode on it: repro first, then fix and verify.",
  ),
  say('start-understand', 'Explain part of the app', 'ask me which part of this repo I want to understand, as a multiple-choice question of its main areas. then use /teach on it, in plain words.'),
  say('start-any', 'Plan any task', PLAN_ANY),
  say(
    'start-night',
    'Plan tonight',
    "plan an overnight run. first ask me which ticket, as a multiple-choice question of this repo's ready-for-agent tickets. then read it and the repo, find the real commands that prove it's done, and write the overnight prompt: goal, done means, fresh worktree, permissions, escape hatch, and \"open a PR but do not merge, deploy, or post\". list anything that would stop it overnight. wait for my go.",
  ),
]

const PLAIN_CATCH_UP = say(
  'start-catchup',
  'Catch me up',
  'catch me up in plain words: what this repo does, what was built recently, and any open branches or pull requests. keep it short. end with a multiple-choice question of what to do next, with finishing open work first.',
)

const review = (n: number) => fill(`review-${n}`, 'Review it', `/interrogate pr #${n}, skeptically. don't change anything yet. no nitpicks unless it's a real bug.`)

// Every button here fills the prompt: they start work, so pressing Enter is the go-ahead.
const prActs = (pr: PullRequest, canMerge: boolean): Act[] => {
  const n = pr.number
  switch (pr.stage) {
    case 'conflict':
      return [fill(`conflict-${n}`, 'Fix the conflict', `/poteto-mode pr #${n} conflicts with main. in its own worktree, rebase it onto main, resolve the conflict, run the checks and push. don't merge.`)]
    case 'fail':
      return [fill(`green-${n}`, 'Get it green', `/poteto-mode babysit pr #${n}. get it green. don't merge.`)]
    case 'draft':
      return [
        fill(`ready-${n}`, 'Finish the draft', `pr #${n} is a draft. check it against its ticket and show me what is left. if nothing is, show me the evidence and mark it ready for review with gh pr ready. don't merge.`),
        review(n),
      ]
    case 'changes':
      return [fill(`changes-${n}`, 'Answer the review', `/poteto-mode pr #${n} has review comments asking for changes. read them, fix what is right, reply to what is not, push. don't merge.`)]
    case 'ready':
      return canMerge ? [mergeAct(n), review(n)] : [review(n)]
    default:
      return [review(n)]
  }
}

const AFTER: Act[] = [
  fill('q-blast', 'Check what else breaks', '/blast-radius'),
  fill('q-review', 'Skeptical review', "/interrogate the whole branch, skeptically. don't change anything yet. no nitpicks unless it's a real bug."),
  fill('q-pr', 'Open the PR', '/poteto-mode open the pr. small ordered commits, evidence in the description. put Fixes <ticket> in the body.'),
  say('q-new', 'New task', PLAN_ANY),
]

// ---------- Following the run ----------

const TASK_CREATE = 'mcp__build-guide__task_create'
const TASK_UPDATE = 'mcp__build-guide__task_update'

// Desktop sessions have no TaskCreate or TaskUpdate, so poteto-mode keeps its
// list in reply text and the tracker sees nothing. This note points it at the
// mod's own task tools, which the tracker serves and records.
const TASK_NOTE =
  '\n\n(build-guide: if TaskCreate and TaskUpdate are not available in this session, use ' +
  `${TASK_CREATE} and ${TASK_UPDATE} as the task list instead, with the same subject, taskId and status fields. ` +
  `If they are not listed, load them with ToolSearch select:${TASK_CREATE},${TASK_UPDATE}.)`

const PLAYBOOK_PATH = /(\/[^\s'"]*poteto-mode\/playbooks\/([a-z-]+)\.md)/

const isPoteto = (name: string) => /(^|:)poteto-mode$/.test(name)
const nameOf = (raw: string) => raw.split(':').pop() ?? raw

// Set when a typed /poteto-mode already carried the note, so the skill text
// that follows does not repeat it.
let isNoted = false

// A skill moves the stage only when no playbook names one: the playbook leads.
const useSkill = (l: Live, raw: string): Live => {
  const name = nameOf(raw)
  if (!TRACKED.has(name) || l.skills.at(-1) === name) return l
  const isLed = l.playbook !== null && l.playbook in PLAYBOOK_STAGE
  const stage = isLed ? l.stage : (stageAt(SKILL_STAGE[name]) ?? l.stage)
  return { ...l, stage, skills: [...l.skills.filter(s => s !== name), name].slice(-8) }
}

// The first playbook a run opens is the main one. Playbooks it opens later (Feature
// ends by reading Opening a PR) only take over once every task is done.
const opensPlaybook = (l: Live, slug: string) => {
  if (l.playbook === slug) return false
  const isDone = l.tasks.length > 0 && l.tasks.every(t => t.status === 'completed')
  return !l.playbook || isDone
}

const addTask = (l: Live, subject: string, id?: string): Live => {
  const isFresh = l.tasks.length > 0 && l.tasks.every(t => t.status === 'completed')
  const tasks = isFresh ? [] : l.tasks
  return { ...l, tasks: [...tasks, { id: id ?? String(tasks.length + 1), subject, status: 'pending' as const }] }
}

// A step that starts moves the stage its words name, and gets advice from Haiku, once.
const updateTask = (l: Live, id: string, status: unknown, subject: string | undefined): Out<Live> => {
  const started = status === 'in_progress' ? l.tasks.find(t => t.id === id) : undefined
  const next: Live = {
    ...l,
    stage: started ? (taskStage(subject ?? started.subject) ?? l.stage) : l.stage,
    tasks: l.tasks
      .filter(t => !(t.id === id && status === 'deleted'))
      .map((t): Task => (t.id !== id ? t : { ...t, subject: subject ?? t.subject, status: status === 'in_progress' || status === 'completed' || status === 'pending' ? status : t.status })),
  }
  const task = next.tasks.find(t => t.id === id)
  if (status !== 'in_progress' || !task || next.advice[id]) return { s: next }
  return { s: next, ask: { key: id, prompt: ADVICE_PROMPT(next, task.subject) } }
}

const explain = say('q-plain', 'Say it plainly', '/bro')

export const pstack: Method<Live> = {
  id: 'pstack',
  label: 'pstack',
  requires: {
    name: 'pstack',
    plugins: ['pstack@'],
    skill: 'poteto-mode',
    install: 'claude plugin marketplace add lifeofladi/pstack-claude && claude plugin install pstack@pstack-claude',
  },
  lead: '/poteto-mode ',
  starts: STARTS,
  plainStarts: [PLAIN_CATCH_UP],
  startNote: 'Start buttons send at once and ask you to pick. Open-work buttons fill your prompt, so press Enter to send.',
  prActs,
  explain,
  after: AFTER,
  decide: {
    who: 'the pstack method',
    favors: 'finish open work before starting new work, reproduce before fixing, the smallest change that can be verified, proof over claims, and the cheapest model tier that does the job.',
  },
  guide: GUIDE,

  empty: EMPTY_LIVE,

  stageOf: raw => norm(raw).stage,
  moveTo: (raw, stage) => ({ ...norm(raw), stage: SHARED.find(x => x.id === stage)?.id ?? norm(raw).stage }),
  brief,
  would: raw => {
    const l = norm(raw)
    const task = running(l)
    return task ? l.advice[task.id]?.would : undefined
  },
  focus: raw => {
    const l = norm(raw)
    const task = running(l) ?? l.tasks.at(-1)
    return [task?.subject ?? '', l.playbook ? playbookName(l.playbook) : ''].filter(Boolean)
  },
  column,
  next: raw => {
    const next = moveFor(norm(raw)).now
    return { label: next.label, text: next.prompt, why: next.why }
  },
  phase: raw => {
    const l = norm(raw)
    return l.tasks.length === 0 ? 'idle' : l.tasks.every(t => t.status === 'completed') ? 'done' : 'running'
  },
  reset: raw => ({ ...EMPTY_LIVE, power: norm(raw).power }),
  isBusy: l => norm(l).tasks.some(t => t.status !== 'completed'),

  hooks: {
    command: (raw, command, args) => {
      const l = useSkill(norm(raw), command)
      if (!isPoteto(command)) return { s: l, args }
      isNoted = true
      return { s: { ...l, playbook: null, steps: [] }, args: args + TASK_NOTE }
    },
    skill: (raw, skill, said) => {
      const l = useSkill(norm(raw), skill)
      if (!isPoteto(skill)) return { s: l, text: said }
      const wasNoted = isNoted
      isNoted = false
      return { s: l, text: wasNoted ? said : said + TASK_NOTE }
    },
    tool: (raw, tool, args, output) => {
      let l = norm(raw)
      const path =
        tool === 'Read' && typeof args.file_path === 'string' ? args.file_path : tool === 'Bash' && typeof args.command === 'string' ? PLAYBOOK_PATH.exec(args.command)?.[1] : undefined
      const slug = path ? PLAYBOOK_PATH.exec(path)?.[2] : undefined
      const read = path && slug && opensPlaybook(l, slug) ? path : undefined
      if (tool === 'Skill' && typeof args.skill === 'string') l = useSkill(l, args.skill)
      if (tool === 'TaskCreate' && typeof args.subject === 'string') l = addTask(l, args.subject, /#(\d+)/.exec(output)?.[1])
      if (tool === 'TodoWrite' && Array.isArray(args.todos)) {
        const todos = args.todos as { content?: unknown; status?: unknown }[]
        l = {
          ...l,
          tasks: todos.map((t, i): Task => ({ id: String(i + 1), subject: String(t.content ?? ''), status: t.status === 'completed' || t.status === 'in_progress' ? t.status : 'pending' })),
        }
      }
      if (tool === 'Bash' && typeof args.command === 'string') {
        if (/\bgh pr create\b/.test(args.command)) l = { ...l, prOpened: true, stage: 'ship' }
        if (/\bgh pr merge\b/.test(args.command)) l = { ...l, prMerged: true, stage: 'ship' }
      }
      if (tool === 'TaskUpdate' && args.taskId !== undefined) {
        return { ...updateTask(l, String(args.taskId), args.status, typeof args.subject === 'string' ? args.subject : undefined), read }
      }
      return { s: l, read }
    },
    file: (raw, path, content) => {
      const l = norm(raw)
      const slug = PLAYBOOK_PATH.exec(path)?.[2]
      if (!slug || !opensPlaybook(l, slug)) return { s: l }
      return { s: { ...l, playbook: slug, stage: stageAt(PLAYBOOK_STAGE[slug]) ?? l.stage, steps: content === null ? [] : parseSteps(content) } }
    },
    answer: (raw, id, said) => {
      const l = norm(raw)
      const advice = (said === null ? null : parseAdvice(said)) ?? { what: 'No advice came back for this step.', would: {}, isReady: false }
      return { ...l, advice: { ...l.advice, [id]: advice } }
    },
    step: (raw, model, effort) => {
      const l = norm(raw)
      return l.power.model === model && l.power.effort === effort ? raw : { ...l, power: { model, effort } }
    },
  },

  tools: [
    {
      name: 'task_create',
      description: 'Adds one step to the task list. Use it in place of TaskCreate when TaskCreate is not available. Returns the new task id.',
      inputSchema: { type: 'object', properties: { subject: { type: 'string' }, description: { type: 'string' } }, required: ['subject'] },
      run: (raw, args) => {
        const l = norm(raw)
        const subject = String(args.subject ?? '')
        const isFresh = l.tasks.length > 0 && l.tasks.every(t => t.status === 'completed')
        const id = String((isFresh ? 0 : l.tasks.length) + 1)
        return { s: addTask(l, subject, id), result: `Task #${id} created: ${subject}` }
      },
    },
    {
      name: 'task_update',
      description: 'Moves a task to in_progress, completed or deleted, or renames it. Use it in place of TaskUpdate when TaskUpdate is not available.',
      inputSchema: {
        type: 'object',
        properties: { taskId: { type: 'string' }, status: { type: 'string', enum: ['pending', 'in_progress', 'completed', 'deleted'] }, subject: { type: 'string' } },
        required: ['taskId'],
      },
      run: (raw, args) => {
        const l = norm(raw)
        const id = String(args.taskId ?? '')
        if (!l.tasks.some(t => t.id === id)) return { s: l, result: `No task #${id}. Create it with ${TASK_CREATE} first.` }
        return { ...updateTask(l, id, args.status, typeof args.subject === 'string' ? args.subject : undefined), result: `Task #${id} updated.` }
      },
    },
  ],
}
