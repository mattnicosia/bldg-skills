// The target strip: the session repo's target map at a glance, above every tab.
// The repo keeps targets/<product>.json and the check script writes
// ~/.claude/target-map/<product>.status.json; this file finds, parses and draws it.
// statusSvg, effect, ago and the dot are copied from matt-mods/target-map
// (hooks/register.tsx) so this public repo does not depend on a private one.

import type { Flag, Job, Road, Status, Target } from '../types'
import { C, cut, esc, inkOf, SANS, W, wrap } from './draw'

export const STATUS_DIR = '.claude/target-map'
export const SCRIPT = 'bin/target-map-status.mjs'
// The target-map mod as matt-mods installs it, which ships the check script.
export const TARGET_MAP_PLUGIN = 'target-map@matt-mods'
export const SCRIPT_UNKNOWN = '~/.claude/plugins/cache/matt-mods/target-map/<version>/bin/target-map-status.mjs'

// ---------- Which map: the per-repo lookup, copied from matt-mods/target-map (hooks/lookup.ts) ----------

// The product is the targets file's name. With several, the first by name.
export const pickTargets = (names: string[]) => {
  const files = names.filter(n => n.endsWith('.json')).sort()
  return { file: files[0] ?? null, others: files.slice(1) }
}

export const productOf = (file: string) => file.replace(/\.json$/, '')

// A product name for a repo with no targets file yet: "BLDG OS" is bldg-os.
export const slug = (name: string) =>
  name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'product'

export const startPrompt = (product: string) =>
  `Start a target map for this repo: ask me what finished means for this product and which tools or outcomes measure it, then write targets/${product}.json in the shape of BLDG OS's targets/bldg-os.json and run the target-map check.`

export const EMPTY = 'No target map for this project yet.'

const q = (s: string) => (/^[\w./~<>-]+$/.test(s) ? s : `"${s}"`)

export const commandFor = (script: string, root: string) => `node ${q(script)} --repo ${q(root)}`

export const missingText = (command: string) => `No target map status yet. Run ${command}`

export const severalText = (file: string, others: string[]) =>
  others.length ? `Several targets files: showing ${file}, not ${others.join(', ')}.` : ''

// The script's path in the plugin cache, from installed_plugins.json.
export const scriptFrom = (installed: string) => {
  try {
    const raw = JSON.parse(installed) as { plugins?: Record<string, { installPath?: string }[]> }
    const path = raw.plugins?.[TARGET_MAP_PLUGIN]?.[0]?.installPath
    return path ? `${path}/${SCRIPT}` : null
  } catch {
    return null
  }
}

export const parseStatus = (text: string, note = ''): Target => {
  try {
    const data = JSON.parse(text) as Status
    if (!Array.isArray(data.flags)) return { phase: 'bad', reason: 'it has no flags list' }
    return { phase: 'ok', data: { ...data, roads: data.roads ?? [], decisions: data.decisions ?? [] }, note }
  } catch (err) {
    return { phase: 'bad', reason: err instanceof Error ? err.message : String(err) }
  }
}

export const left = (f: Flag) => f.jobs.filter(j => j.state !== 'moved').length

// A flag with no jobs never says "0 left": it has nothing to count yet.
export const leftText = (f: Flag) => (f.jobs.length === 0 ? '' : left(f) === 0 ? 'all moved' : `${left(f)} left`)

const allJobs = (s: Status) => s.flags.flatMap(f => f.jobs)

export const stuckOf = (s: Status) => allJobs(s).filter(j => j.stuck)

// ---------- Does the work under way cross a job off? ----------

const STOP = new Set(['and', 'the', 'for', 'off', 'with', 'from', 'into', 'one', 'all', 'per', 'its', 'our', 'that', 'this', 'not', 'new'])

// Lowercase words of three letters or more, with a plural s dropped, so
// "Daily reports" meets "add-daily-report".
export const wordsOf = (s: string) =>
  s
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter(w => w.length >= 3 && !STOP.has(w))
    .map(w => (w.length > 3 && w.endsWith('s') && !w.endsWith('ss') ? w.slice(0, -1) : w))

// A job not yet moved matches when its id appears in the texts, or every word
// of its short name or its full name does. Texts are the current task, the
// playbook, the PR title and the branch.
export const crossesOff = (s: Status, texts: string[]): Job[] => {
  const said = texts.join(' ')
  const have = new Set(wordsOf(said))
  return allJobs(s).filter(j => {
    if (j.state === 'moved') return false
    if (new RegExp(`(^|[^a-z0-9])${j.id.replace(/[^\w]/g, '')}([^a-z0-9]|$)`, 'i').test(said)) return true
    return [j.short, j.name].some(label => {
      const need = wordsOf(label)
      return need.length > 0 && need.every(w => have.has(w))
    })
  })
}

const pillText = (jobs: Job[]) => `Crosses off ${jobs.map(j => `${j.id} ${j.short}`).join(', ')}`

const stuckText = (jobs: Job[]) => `Stuck: ${jobs.map(j => `${j.id} ${j.short}, since ${j.since}`).join('; ')}`

// ---------- The strip ----------

const DOT_X = 150
const DOT_STEP = 17

const dot = (x: number, y: number, j: Job, isMatched = false) => {
  const body =
    j.state === 'moved'
      ? `<circle cx="${x}" cy="${y}" r="5.5" fill="${C.green}"/>`
      : j.state === 'gray'
        ? `<circle cx="${x}" cy="${y}" r="5.5" fill="#fff" stroke="${C.gray}" stroke-width="1.5" stroke-dasharray="2 2"/>`
        : `<circle cx="${x}" cy="${y}" r="5.5" fill="#fff" stroke="${C.gray}" stroke-width="1.6"/>`
  const stuck = j.stuck ? `<circle cx="${x}" cy="${y}" r="8.5" fill="none" stroke="${C.red}" stroke-width="1.8"/>` : ''
  const match = isMatched ? `<circle cx="${x}" cy="${y}" r="8.5" fill="none" stroke="${C.indigo}" stroke-width="1.8"/>` : ''
  return `<g><title>${esc(`${j.id} ${j.name}`)}</title>${stuck}${match}${body}</g>`
}

const style = `<style>
svg{background:#F5F5F7}
.card{fill:#FFFFFF}.ink{fill:#1D1D1F}.mut{fill:#6E6E73}.ok{fill:${C.green}}
text{font-family:${SANS};letter-spacing:-.01em}
.h{font-size:20px;font-weight:700;letter-spacing:-.02em}.sub{font-size:12.5px}.lab{font-size:13.5px;font-weight:700}.sm{font-size:12px}.tiny{font-size:9.5px}
</style>`

const svgDoc = (h: number, body: string) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 ${W} ${h}" preserveAspectRatio="xMidYMin meet">
${style}
<rect width="${W}" height="${h}" fill="#F5F5F7"/>
${body}</svg>`

// One row per flag: its name, a dot per job and how many are left. A flag with
// no jobs shows its note. Under the rows, the stuck line and the crosses-off pill.
export const stripSvg = (s: Status, matched: Job[]) => {
  const ids = new Set(matched.map(j => j.id))
  const stuck = stuckOf(s)
  let b = ''
  let y = 14
  const top = y
  y += 22
  b += `<text x="28" y="${y}" font-size="11" font-weight="700" fill="${inkOf(C.indigo)}" letter-spacing=".04em">TARGET</text>`
  b += `<text x="82" y="${y}" class="sm ink" font-weight="600">${esc(cut(s.goal || s.product, 52))}</text>`
  y += 10
  for (const f of s.flags) {
    y += 22
    b += `<text x="28" y="${y + 4}" class="sm ink" font-weight="600">${esc(cut(f.name, 17))}</text>`
    if (f.jobs.length === 0) {
      b += `<text x="${DOT_X - 6}" y="${y + 4}" class="sm mut">${esc(cut(f.note ?? 'No jobs listed yet.', 44))}</text>`
      continue
    }
    const room = Math.floor((W - 28 - 70 - DOT_X) / DOT_STEP) + 1
    f.jobs.slice(0, room).forEach((j, i) => {
      b += dot(DOT_X + i * DOT_STEP, y, j, ids.has(j.id))
    })
    b += `<text x="${W - 28}" y="${y + 4}" text-anchor="end" class="sm ${left(f) === 0 ? 'ok' : 'ink'}" font-weight="700">${esc(leftText(f))}</text>`
  }
  y += 14
  if (stuck.length > 0) {
    y += 16
    b += `<circle cx="32" cy="${y - 4}" r="3.5" fill="${C.red}"/>`
    b += `<text x="42" y="${y}" class="sm" fill="${inkOf(C.red)}" font-weight="600">${esc(cut(stuckText(stuck), 62))}</text>`
    y += 8
  }
  if (matched.length > 0) {
    y += 8
    const label = cut(pillText(matched), 60)
    const w = Math.min(W - 56, Math.round(label.length * 6.4 + 24))
    b += `<rect x="28" y="${y}" width="${w}" height="24" rx="12" fill="${C.indigo}" fill-opacity=".13"/>`
    b += `<text x="40" y="${y + 16}" font-size="12" font-weight="700" fill="${inkOf(C.indigo)}">${esc(label)}</text>`
    y += 32
  }
  const card = `<rect x="16" y="${top}" width="${W - 32}" height="${y - top}" rx="12" class="card"/>`
  return svgDoc(y + 10, card + b)
}

const mark = (j: Job) => (j.state === 'moved' ? '●' : j.state === 'gray' ? '◌' : '○') + (j.stuck ? '!' : '')

// The strip as text lines, for the terminal.
export const stripLines = (s: Status, matched: Job[]) => [
  `Target: ${s.goal || s.product}`,
  ...s.flags.map(f => (f.jobs.length === 0 ? `${f.name}: ${f.note ?? 'no jobs listed yet'}` : `${f.name}  ${f.jobs.map(mark).join('')}  ${leftText(f)}`)),
  ...(stuckOf(s).length > 0 ? [stuckText(stuckOf(s))] : []),
  ...(matched.length > 0 ? [pillText(matched)] : []),
]

// ---------- The full map, copied from target-map ----------

const ids = (v: string[] | string | undefined): string[] => (Array.isArray(v) ? v : (v ?? '').split(/[\s,]+/).filter(Boolean))

export const ago = (iso: string, now: number) => {
  const t = Date.parse(iso)
  if (Number.isNaN(t)) return 'at an unknown time'
  const min = Math.max(0, Math.round((now - t) / 60000))
  if (min < 1) return 'just now'
  if (min < 60) return `${min} min ago`
  const hr = Math.round(min / 60)
  if (hr < 48) return `${hr} hour${hr === 1 ? '' : 's'} ago`
  return `${Math.round(hr / 24)} days ago`
}

// Before and after counts for one road: it takes off the jobs it crosses off
// that are not yet moved.
export const effect = (flags: Flag[], road: Road) => {
  const crossed = new Set(ids(road.crossesOff))
  return flags
    .filter(f => f.jobs.length > 0)
    .map(f => {
      const before = left(f)
      const after = before - f.jobs.filter(j => crossed.has(j.id) && j.state !== 'moved').length
      return { flag: f.name, before, after }
    })
}

const effectText = (flags: Flag[], road: Road) =>
  effect(flags, road)
    .map(x => (x.before === x.after ? `${x.flag} no change` : `${x.flag} ${x.before} → ${x.after}`))
    .join(', ')

const MAP = { green: C.green, red: C.red, gray: C.gray, ink: '#1D1D1F', ln: '#D2D2D7', blue: C.blue, purple: C.indigo }

const mapDot = (x: number, y: number, j: Job) => {
  const body =
    j.state === 'moved'
      ? `<circle cx="${x}" cy="${y}" r="7" fill="${MAP.green}"/>`
      : j.state === 'gray'
        ? `<circle cx="${x}" cy="${y}" r="7" fill="#fff" stroke="${MAP.gray}" stroke-width="1.8" stroke-dasharray="2.5 2.5"/>`
        : `<circle cx="${x}" cy="${y}" r="7" fill="#fff" stroke="${MAP.gray}" stroke-width="2"/>`
  const stuck = j.stuck ? `<circle cx="${x}" cy="${y}" r="11.5" fill="none" stroke="${MAP.red}" stroke-width="2.2"/>` : ''
  return `<g>${stuck}${body}</g>`
}

const dotX = (i: number, n: number) => (n <= 1 ? W / 2 : 40 + (i * (W - 80)) / (n - 1))

const jobLabel = (x: number, y: number, s: string, above: boolean) => {
  const rows = wrap(s, 14).slice(0, 2)
  const top = above ? y - 21 - (rows.length - 1) * 11 : y + 28
  return rows.map((r, i) => `<text x="${x}" y="${top + i * 11}" text-anchor="middle" class="tiny mut">${esc(r)}</text>`).join('')
}

// The whole map: every flag with its jobs, the roads under them, the stuck jobs
// and the decisions you own.
export const mapSvg = (s: Status, now: number) => {
  let y = 0
  let b = ''
  const goal = wrap(s.goal || s.product, 34)
  b += goal.map((g, i) => `<text x="16" y="${34 + i * 24}" class="h ink">${esc(g)}</text>`).join('')
  y = 34 + (goal.length - 1) * 24 + 20
  b += `<text x="16" y="${y}" class="sub mut">target set ${esc(s.targetSetOn)} · checked ${esc(ago(s.checkedAt, now))}</text>`
  y += 18

  let roadsBg = ''
  for (const f of s.flags) {
    const n = f.jobs.length
    const roads = s.roads.filter(r => f.jobs.some(j => j.id === r.from))
    const rowH = n === 0 ? 74 : 144
    b += `<rect x="12" y="${y}" width="${W - 24}" height="${rowH}" rx="12" class="card"/>`
    b += `<text x="26" y="${y + 26}" class="lab ink">${esc(f.name)}</text>`
    b +=
      n === 0
        ? `<text x="${W - 26}" y="${y + 26}" text-anchor="end" class="lab" fill="${MAP.gray}">add tools to start</text>`
        : `<text x="${W - 26}" y="${y + 26}" text-anchor="end" class="lab ${left(f) === 0 ? 'ok' : 'ink'}">${left(f)} job${left(f) === 1 ? '' : 's'} left</text>`
    if (n === 0) {
      b += wrap(f.note ?? 'No jobs listed yet.', 62)
        .slice(0, 2)
        .map((r, i) => `<text x="26" y="${y + 48 + i * 15}" class="sm mut">${esc(r)}</text>`)
        .join('')
    } else {
      const ly = y + 88
      b += `<line x1="${dotX(0, n)}" y1="${ly}" x2="${dotX(n - 1, n)}" y2="${ly}" stroke="${MAP.ln}" stroke-width="2"/>`
      f.jobs.forEach((j, i) => {
        const x = dotX(i, n)
        b += jobLabel(x, ly, `${j.id} ${j.short}`, i % 2 === 0)
        b += mapDot(x, ly, j)
      })
      // Roads leave from their dot, drawn dashed behind the boxes that follow.
      let off = 0
      roads.forEach(r => {
        const i = f.jobs.findIndex(j => j.id === r.from)
        const x = dotX(i, n)
        const stub = ids(r.crossesOff).length === 0
        if (stub) off += 24
        const boxTop = y + rowH + 14 + off
        off += 72
        const endY = stub ? boxTop - 22 : boxTop
        roadsBg += `<path d="M${x} ${ly + 12} V${endY}" fill="none" stroke="${MAP.purple}" stroke-width="2" stroke-dasharray="5 4"/>`
        if (stub) roadsBg += `<circle cx="${x}" cy="${endY}" r="3.5" fill="#fff" stroke="${MAP.red}" stroke-width="1.6"/>`
      })
    }
    y += rowH
    roads.forEach(r => {
      if (ids(r.crossesOff).length === 0) y += 24
      const crossed = ids(r.crossesOff)
      const unlocks = ids(r.unlocks)
      b += `<rect x="12" y="${y + 14}" width="${W - 24}" height="62" rx="10" fill="#fff" stroke="${MAP.purple}" stroke-width="1.6" stroke-dasharray="5 4"/>`
      b += `<text x="26" y="${y + 34}" class="lab" fill="${MAP.purple}">Road ${esc(r.id)}: ${esc(wrap(r.name, 42)[0] ?? '')}</text>`
      b += `<text x="26" y="${y + 51}" class="sm ink" ${crossed.length === 0 ? `fill="${MAP.red}"` : ''}>${crossed.length === 0 ? 'crosses off nothing' : `crosses off ${esc(crossed.join(', '))}`}, unlocks ${esc(unlocks.join(', ') || 'nothing')}</text>`
      b += `<text x="26" y="${y + 67}" class="sm mut">${esc(effectText(s.flags, r))}</text>`
      y += 72
    })
    y += 14
  }

  const stuck = stuckOf(s)
  const stuckRows = stuck.flatMap(j => wrap(`${j.id} ${j.name}, since ${j.since}`, 56))
  const sh = 14 + Math.max(1, stuckRows.length) * 16 + 8
  b += `<rect x="12" y="${y}" width="${W - 24}" height="${sh}" rx="10" fill="${MAP.red}" fill-opacity="${stuck.length ? '.1' : '0.04'}"/>`
  b += `<text x="26" y="${y + 20}" class="sm" font-weight="700" fill="${stuck.length ? MAP.red : MAP.gray}">STUCK</text>`
  b += stuck.length ? stuckRows.map((r, i) => `<text x="76" y="${y + 20 + i * 16}" class="sm ink">${esc(r)}</text>`).join('') : `<text x="76" y="${y + 20}" class="sm mut">nothing stuck</text>`
  y += sh + 14

  const dec = s.decisions.flatMap((d, i) => wrap(d, 56).map((r, k) => ({ r, first: k === 0, i })))
  const dh = 44 + Math.max(1, dec.length) * 16
  b += `<rect x="12" y="${y}" width="${W - 24}" height="${dh}" rx="12" class="card"/>`
  b += `<text x="26" y="${y + 24}" class="lab ink">Decisions you own</text>`
  b += dec.length
    ? dec.map((d, i) => `${d.first ? `<circle cx="32" cy="${y + 44 + i * 16}" r="2.5" fill="${MAP.blue}"/>` : ''}<text x="42" y="${y + 48 + i * 16}" class="sm ink">${esc(d.r)}</text>`).join('')
    : `<text x="26" y="${y + 48}" class="sm mut">none open</text>`
  y += dh + 16

  return svgDoc(y, roadsBg + b)
}

// The full map as text lines, for the terminal.
export const mapLines = (s: Status, now: number) => [
  s.goal,
  `target set ${s.targetSetOn} · checked ${ago(s.checkedAt, now)}`,
  ...s.flags.map(f => (f.jobs.length === 0 ? `${f.name}: ${f.note ?? 'add tools to start'}` : `${f.name}: ${leftText(f)}. ${f.jobs.map(j => `${mark(j)} ${j.id} ${j.short}`).join('  ')}`)),
  `STUCK ${stuckOf(s).map(j => `${j.id} since ${j.since}`).join('; ') || 'none'}`,
  ...s.roads.map(r => `Road ${r.id} ${r.name}: crosses off ${ids(r.crossesOff).join(', ') || 'nothing'}, unlocks ${ids(r.unlocks).join(', ') || 'nothing'}. ${effectText(s.flags, r)}`),
]
