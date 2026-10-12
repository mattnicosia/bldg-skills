// Drawing helpers every method's pictures share. Each picture is one SVG string,
// 460 wide, in Apple's light palette.

export const W = 460
export const SANS = `-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Helvetica,Arial,sans-serif`
export const MONO = `ui-monospace,'SF Mono',Menlo,Consolas,monospace`

// One vivid fill per hue that carries white bold text, and a deeper ink of each
// for text on a tint. Methods name their steps after these hues.
export const C = {
  blue: '#0071E3',
  indigo: '#5E5CE6',
  purple: '#AF52DE',
  orange: '#F56300',
  green: '#1DA851',
  teal: '#0A9BC1',
  pink: '#E8335F',
  gray: '#8E8E93',
  red: '#E5342C',
  slate: '#48484A',
}

export const INK: Record<string, string> = {
  [C.blue]: '#0058B0',
  [C.indigo]: '#3F3DB8',
  [C.purple]: '#8133A8',
  [C.orange]: '#B54700',
  [C.green]: '#137A3A',
  [C.teal]: '#06708C',
  [C.pink]: '#B8163F',
  [C.gray]: '#5B5B60',
  [C.red]: '#B3261E',
  [C.slate]: '#1D1D1F',
}

export const inkOf = (color: string) => INK[color] ?? color

// A chip is a command you type (mono), a playbook (▸, sans) or a name you say (sans).
export type Item = { label: string; tip: string; kind?: 'cmd' | 'play' | 'name' }

export const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

export const wrap = (s: string, max: number) => {
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

export const cut = (s: string, max: number) => (s.length > max ? `${s.slice(0, max - 1).trimEnd()}…` : s)

export const text = (x: number, y: number, cls: string, s: string, extra = '') => `<text x="${x}" y="${y}" class="${cls}"${extra}>${esc(s)}</text>`

export const lines = (x: number, y: number, cls: string, rows: string[], step: number, extra = '') =>
  rows.map((row, i) => text(x, y + i * step, cls, row, extra)).join('')

const chipLabel = (it: Item) => (it.kind === 'play' ? `▸ ${it.label}` : it.label)
const isMono = (it: Item) => !it.kind || it.kind === 'cmd'

export const labelOf = chipLabel

export const chipW = (it: Item) => Math.round(chipLabel(it).length * 12.5 * (isMono(it) ? 0.6 : 0.56) + 20)

export const chip = (x: number, y: number, it: Item, color: string) => {
  const w = chipW(it)
  const font = isMono(it) ? ` font-family="${MONO}"` : ''
  return `<g class="chip"><title>${esc(it.tip)}</title><rect x="${x}" y="${y}" width="${w}" height="24" rx="12" fill="${color}" fill-opacity=".13"/><text x="${x + w / 2}" y="${y + 16.5}" text-anchor="middle" fill="${inkOf(color)}" font-size="12.5" font-weight="600"${font}>${esc(chipLabel(it))}</text></g>`
}

// Chips laid left to right, wrapping at maxX.
export const chips = (x0: number, y0: number, maxX: number, items: Item[], color: string) => {
  let x = x0
  let y = y0
  let svg = ''
  for (const it of items) {
    const w = chipW(it)
    if (x > x0 && x + w > maxX) {
      x = x0
      y += 30
    }
    svg += chip(x, y, it, color)
    x += w + 6
  }
  return { svg, bottom: y + 24 }
}

export const down = (cx: number, y: number) => `<path class="ar" d="M${cx - 6} ${y} l6 7 l6 -7z"/>`

export const doc = (h: number, body: string) => `<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 ${W} ${h}" preserveAspectRatio="xMidYMin meet">
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

// A tinted card with a colored title and wrapped body lines; returns its height.
export const noteCard = (y: number, title: string, body: string, color: string) => {
  const rows = wrap(body, 60)
  const h = 34 + rows.length * 16 + 8
  const svg =
    `<rect x="16" y="${y}" width="${W - 32}" height="${h}" rx="10" fill="${color}" fill-opacity=".1" stroke="${color}" stroke-opacity=".45"/>` +
    `<text x="30" y="${y + 22}" font-size="13" font-weight="700" fill="${inkOf(color)}">${esc(title)}</text>` +
    lines(30, y + 42, 'body ink', rows, 16)
  return { svg, h }
}

// The desktop draws an Svg in a frame it cannot size from the markup, so pass
// the pixel size: the pane's width, guessed at 8px a cell.
export const fit = (source: string, columns: number) => {
  const width = Math.round(Math.min(Math.max(columns * 8, 300), 1100))
  const h = Number(/viewBox="0 0 \d+ ([\d.]+)"/.exec(source)?.[1] ?? 600)
  return { width, height: Math.round((h * width) / W) }
}
