// The Now tab's two bands: the shared stage bar with every method's columns
// under it, and the next-move cards. Methods hand over data (Column, Move);
// this file draws it, so a third method is one more column.

import type { MethodId, SharedId } from '../types'
import { C, cut, doc, esc, inkOf, MONO, text, W, wrap } from './draw'
import type { Column, Move, Row, Section } from './method'
import { SHARED, sharedIndex, STAGE_MAP } from './stages'

export type Side = { id: MethodId; label: string; own: string | null; view: Column }

const TONE: Record<NonNullable<Section['tone']>, string> = { warn: C.orange, bad: C.red, good: C.green }

const LABEL_W = 60

// ---------- Stage bar ----------

const barSvg = (at: SharedId | null, sides: Side[]) => {
  const now = sharedIndex(at)
  const x0 = 16 + LABEL_W
  const gap = 4
  const sw = (W - 16 - x0 - gap * (SHARED.length - 1)) / SHARED.length
  let b = text(16, 34, 'h ink', 'You are here')
  SHARED.forEach((s, i) => {
    const x = x0 + i * (sw + gap)
    const isNow = i === now
    const isPast = now >= 0 && i < now
    b += `<rect x="${x}" y="${isNow ? 52 : 54}" width="${sw}" height="${isNow ? 12 : 8}" rx="4" fill="${isNow || isPast ? s.color : '#E5E5EA'}" fill-opacity="${isPast ? 0.4 : 1}"/>`
    if (isNow) b += `<path d="M${x + sw / 2 - 6} 41 h12 l-6 8 z" fill="${s.color}"/>`
  })
  let y = 84
  for (const side of sides) {
    b += `<text x="16" y="${y}" font-size="11.5" font-weight="700" class="ink">${esc(side.label)}</text>`
    let tallest = 1
    SHARED.forEach((s, i) => {
      const x = x0 + i * (sw + gap) + sw / 2
      const names = STAGE_MAP[side.id].filter(e => e.shared === s.id)
      tallest = Math.max(tallest, names.length)
      names.forEach((e, k) => {
        const isOwn = e.stage === side.own
        const tone = isOwn ? ` fill="${inkOf(s.color)}" font-weight="700"` : ' class="mut"'
        b += `<text x="${x}" y="${y + k * 13}" text-anchor="middle" font-size="${isOwn ? 11 : 10.5}"${tone}>${esc(e.name)}</text>`
      })
    })
    y += tallest * 13 + 10
  }
  return { svg: b, bottom: y - 6 }
}

// ---------- Columns ----------

const markSvg = (cx: number, cy: number, mark: Row['mark'], color: string) => {
  if (mark === 'done') return `<circle cx="${cx}" cy="${cy}" r="6.5" fill="${C.green}"/><path d="M${cx - 3.2} ${cy} l2.2 2.4 l4.4 -4.8" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>`
  if (mark === 'now') return `<circle cx="${cx}" cy="${cy}" r="6.5" fill="none" stroke="${color}" stroke-width="2.2"/><circle cx="${cx}" cy="${cy}" r="2.8" fill="${color}"/>`
  if (mark === 'skipped') return `<circle cx="${cx}" cy="${cy}" r="6.5" fill="#fff" stroke="${C.orange}" stroke-width="1.6" stroke-dasharray="2.5 2"/><text x="${cx}" y="${cy + 3.5}" text-anchor="middle" font-size="9" font-weight="800" fill="${inkOf(C.orange)}">!</text>`
  return `<circle cx="${cx}" cy="${cy}" r="6.5" fill="none" class="ln" stroke-width="1.6"/>`
}

// One column's content from its top; returns the drawing and where it ends.
const columnBody = (x: number, y: number, cw: number, side: Side, color: string) => {
  const v = side.view
  const chars = Math.floor((cw - 24) / 6.1)
  let b = ''
  b += `<text x="${x + 12}" y="${y + 22}" font-size="14" font-weight="700" class="ink">${esc(side.label)}</text>`
  const pill = cut(v.stage, 22)
  const pw = Math.round(pill.length * 6 + 16)
  b += `<rect x="${x + cw - 10 - pw}" y="${y + 9}" width="${pw}" height="20" rx="10" fill="${color}" fill-opacity=".14"/>`
  b += `<text x="${x + cw - 10 - pw / 2}" y="${y + 23}" text-anchor="middle" font-size="10.5" font-weight="700" fill="${inkOf(color)}">${esc(pill)}</text>`
  let ty = y + 46
  for (const line of wrap(v.title, chars - 2).slice(0, 2)) {
    b += `<text x="${x + 12}" y="${ty}" font-size="12" font-weight="600" class="ink">${esc(line)}</text>`
    ty += 15
  }
  ty += 6
  for (const r of v.rows) {
    b += markSvg(x + 20, ty, r.mark, color)
    const tone = r.mark === 'now' ? ' font-weight="700" class="ink"' : r.mark === 'todo' ? ' class="mut"' : r.mark === 'skipped' ? ` fill="${inkOf(C.orange)}"` : ' class="ink"'
    b += `<text x="${x + 33}" y="${ty + 4}" font-size="11.5"${tone}>${esc(cut(r.label, chars - 4))}</text>`
    ty += 18
    if (r.tag) {
      b += `<text x="${x + 33}" y="${ty}" font-size="9.5" font-family="${MONO}" class="mut">${esc(cut(r.tag, chars))}</text>`
      ty += 12
    }
  }
  for (const s of v.sections) {
    ty += 8
    const tone = s.tone ? TONE[s.tone] : C.gray
    b += `<text x="${x + 12}" y="${ty}" font-size="10" font-weight="700" fill="${inkOf(tone)}" letter-spacing=".03em">${esc(s.title.toUpperCase())}</text>`
    ty += 14
    for (const line of wrap(s.body, chars)) {
      b += `<text x="${x + 12}" y="${ty}" font-size="11"${s.tone === 'bad' ? ` fill="${inkOf(C.red)}"` : ' class="ink"'}>${esc(line)}</text>`
      ty += 14
    }
  }
  return { svg: b, bottom: ty }
}

const wouldBox = (x: number, y: number, cw: number, side: Side, color: string) => {
  const rows = wrap(side.view.would, Math.floor((cw - 28) / 5.9))
  const h = 26 + rows.length * 14 + 6
  let b = `<rect x="${x + 6}" y="${y}" width="${cw - 12}" height="${h}" rx="9" fill="${color}" fill-opacity=".12"/>`
  b += `<text x="${x + 14}" y="${y + 17}" font-size="9.5" font-weight="700" fill="${inkOf(color)}" letter-spacing=".03em">${esc(`WHAT ${side.label.toUpperCase()} WOULD DO NOW`)}</text>`
  rows.forEach((line, i) => {
    b += `<text x="${x + 14}" y="${y + 33 + i * 14}" font-size="11" class="ink">${esc(line)}</text>`
  })
  return { svg: b, h }
}

// The stage bar, then one column per method side by side, each ending in what
// that method would do now.
export const pairSvg = (at: SharedId | null, sides: Side[]) => {
  const bar = barSvg(at, sides)
  const color = SHARED[sharedIndex(at)]?.color ?? C.gray
  const gap = 12
  const cw = (W - 32 - gap * (sides.length - 1)) / sides.length
  const top = bar.bottom + 12
  const bodies = sides.map((s, i) => columnBody(16 + i * (cw + gap), top, cw, s, color))
  const boxTop = Math.max(...bodies.map(x => x.bottom)) + 10
  const boxes = sides.map((s, i) => wouldBox(16 + i * (cw + gap), boxTop, cw, s, color))
  const bottom = boxTop + Math.max(...boxes.map(x => x.h)) + 8
  let b = bar.svg
  sides.forEach((_, i) => {
    b += `<rect class="card" x="${16 + i * (cw + gap)}" y="${top}" width="${cw}" height="${bottom - top}" rx="12"/>`
  })
  b += bodies.map(x => x.svg).join('') + boxes.map(x => x.svg).join('')
  return doc(bottom + 12, b)
}

// ---------- Terminal ----------

export const barLines = (sides: Side[]) =>
  sides.map(side => {
    const cells = SHARED.map(s =>
      STAGE_MAP[side.id]
        .filter(e => e.shared === s.id)
        .map(e => (e.stage === side.own ? `[${e.name}]` : e.name))
        .join('/'),
    )
    return `${side.label.padEnd(7)}${cells.join(' · ')}`
  })

const MARK: Record<Row['mark'], string> = { done: '[x]', now: '[>]', todo: '[ ]', skipped: '[!]' }

export const columnMd = (side: Side) => {
  const v = side.view
  return [
    `**${side.label}** · ${v.stage}`,
    `_${v.title}_`,
    v.rows.map(r => `${MARK[r.mark]} ${r.label}${r.tag ? ` (${r.tag})` : ''}`).join('\n'),
    ...v.sections.map(s => `**${s.title}:** ${s.body}`),
    `**What ${side.label} would do now:** ${v.would}`,
  ]
    .filter(Boolean)
    .join('\n\n')
}

// ---------- Next move ----------

// The command a move runs: its leading slash command, or its whole text.
const commandOf = (text: string) => {
  const t = text.trim().toLowerCase()
  return /^\/\S+/.exec(t)?.[0] ?? t
}

export const agree = (a: Move, b: Move) => commandOf(a.text) !== '' && commandOf(a.text) === commandOf(b.text)

export type NextCard = { key: string; title: string; move: Move; ids: MethodId[] }

// One card per method, or one wide card when every method proposes the same command.
export const nextCards = (moves: { id: MethodId; label: string; move: Move }[]): NextCard[] => {
  const [first] = moves
  if (first && moves.length > 1 && moves.every(m => agree(m.move, first.move))) {
    return [{ key: 'both', title: 'Both agree', move: first.move, ids: moves.map(m => m.id) }]
  }
  return moves.map(m => ({ key: m.id, title: m.label, move: m.move, ids: [m.id] }))
}
