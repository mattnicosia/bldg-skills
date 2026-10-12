// After a main turn: a summary of what it did, and a decision card when it ends
// by asking the person to choose.

import type { Choice, Decision, Summary } from '../types'
import { C, cut, doc, esc, inkOf, lines, MONO, W, wrap } from './draw'
import type { AnyMethod } from './method'

// Cheap gate before any model call: the reply's tail asks something, or lists
// lettered or numbered options.
export const looksLikeChoice = (answer: string) => {
  const tail = answer.slice(-1500)
  const listed = (tail.match(/^\s*(?:\*\*)?([A-H]|[1-9])[.):](?:\*\*)?\s+\S/gm) ?? []).length
  return (
    listed >= 2 ||
    /\?\s*$/.test(answer.trim()) ||
    /\b(reply with|which (one|option)|should I|do you want|want me to|pick one|say the word|say yes|when you say|confirm|go ahead|let me know|tell me (which|if|when))\b/i.test(tail)
  )
}

export const decidePrompt = (m: AnyMethod, answer: string) =>
  `An agent working through ${m.decide.who} finished a turn. Summarize it in short everyday words for the user, and if it ends by asking the user to make a choice, extract it. ` +
  `The method favors: ${m.decide.favors}\n\n` +
  'Reply with JSON only, no prose, in this shape:\n' +
  '{"done":"<what this turn did or found, one or two plain sentences>","next":"<what happens next or what the user should do, one sentence>","isWaiting":<true if the agent stopped and needs the user to answer or act>,"isChoice":true,"question":"<one short line>","options":[{"key":"<what the user would type, e.g. B or yes>","label":"<3 to 6 words>","tier":"<model and effort if the reply gave one, else empty>"}],"pick":"<key the method favors>","why":"<one plain sentence>"}\n' +
  'A request to confirm before acting ("when you say yes I will...", "shall I go ahead") is a yes or no choice: use keys "yes" and "no", and add a third option when the reply names one. For a yes or no question use keys "yes" and "no". At most 6 options. If the turn does not ask for a choice, set isChoice false and leave out question, options, pick and why.\n\n' +
  `The turn's final reply:\n${answer.slice(-6000)}`

export const PR_LINK = /https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/pull\/\d+/g

export const linksIn = (answer: string) => [...new Set(answer.match(PR_LINK) ?? [])].slice(0, 4)

const jsonOf = (s: string) => JSON.parse(s.slice(s.indexOf('{'), s.lastIndexOf('}') + 1)) as Record<string, unknown>

export const parseSummary = (said: string, answer: string): Summary => {
  try {
    const raw = jsonOf(said)
    if (!raw.done) return null
    return { done: String(raw.done), next: String(raw.next ?? ''), links: linksIn(answer), isWaiting: raw.isWaiting === true }
  } catch {
    return null
  }
}

export const parseDecision = (said: string): Decision => {
  try {
    const raw = jsonOf(said)
    const options: Choice[] = ((raw.options ?? []) as Partial<Choice>[])
      .filter(o => o.key && o.label)
      .slice(0, 6)
      .map(o => ({ key: String(o.key), label: String(o.label), tier: String(o.tier ?? '') }))
    if (!raw.isChoice || options.length === 0) return null
    const pick = options.some(o => o.key === raw.pick) ? String(raw.pick) : ''
    return { question: String(raw.question ?? 'Your call'), options, pick, why: String(raw.why ?? '') }
  } catch {
    return null
  }
}

const tierColor = (tier: string) =>
  /fable/i.test(tier) ? C.indigo : /opus/i.test(tier) ? C.blue : /haiku/i.test(tier) ? C.gray : /sonnet/i.test(tier) ? C.green : C.slate

// The decision card as a picture: one tile per option, the method's pick outlined.
export const decisionSvg = (d: NonNullable<Decision>, m: AnyMethod) => {
  let b = ''
  b += `<circle cx="26" cy="27" r="5" fill="${C.orange}"/>`
  b += `<text x="38" y="31" font-size="12" font-weight="700" fill="${inkOf(C.orange)}" letter-spacing=".04em">${esc(m.ask.title.toUpperCase())}</text>`
  const q = wrap(d.question, 44).slice(0, 2)
  b += lines(20, 56, 'ink', q, 22, ' font-size="18" font-weight="700" letter-spacing="-.02em"')
  let y = 56 + q.length * 22 - 4
  for (const o of d.options) {
    const isPick = o.key === d.pick
    const h = 46
    b += `<rect class="card" x="16" y="${y}" width="${W - 32}" height="${h}" rx="12"${isPick ? ` stroke="${C.blue}" stroke-width="2"` : ''}/>`
    b += `<circle cx="40" cy="${y + h / 2}" r="13" fill="${isPick ? C.blue : '#E5E5EA'}"/>`
    b += `<text x="40" y="${y + h / 2 + 4.5}" text-anchor="middle" font-size="12.5" font-weight="700" fill="${isPick ? '#fff' : '#1D1D1F'}">${esc(cut(o.key, 3))}</text>`
    b += `<text x="62" y="${y + h / 2 + (isPick ? -1 : 4.5)}" font-size="13.5" font-weight="${isPick ? 700 : 500}" class="ink">${esc(cut(o.label, o.tier ? 34 : 40))}</text>`
    if (isPick) b += `<text x="62" y="${y + h / 2 + 14}" font-size="10.5" font-weight="700" fill="${inkOf(C.blue)}">★ ${esc(m.ask.pick)}</text>`
    if (o.tier) {
      const t = cut(o.tier, 18)
      const tw = Math.round(t.length * 6.2 + 16)
      const c = tierColor(o.tier)
      b += `<rect x="${W - 28 - tw}" y="${y + h / 2 - 10}" width="${tw}" height="20" rx="10" fill="${c}" fill-opacity=".13"/>`
      b += `<text x="${W - 28 - tw / 2}" y="${y + h / 2 + 4}" text-anchor="middle" font-size="10.5" font-weight="600" font-family="${MONO}" fill="${inkOf(c)}">${esc(t)}</text>`
    }
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
