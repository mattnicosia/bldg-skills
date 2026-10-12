// The build guide pane. Everything a method needs done (a read, a write, a
// model call, a toast) happens here: the engine follows `$` only into functions
// of this file, so the methods stay data and pure functions.
//
// Every method hears every signal and keeps its own state. When one method's
// own move changes the shared stage, the others move to match (stages.ts), and
// that counts as one move. No method toasts or adds a note to a prompt: its
// advice shows in its own column on the Now tab.

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Decision, Env, MethodId, SharedId, Stage, States, Summary, Target } from '../types'
import { fit } from './draw'
import { guardBlock } from './guard'
import { during, skillsOf, type Act, type AnyMethod, type Card, type Out } from './method'
import { detect, isMethod, methodOf, METHODS } from './methods'
import { barLines, columnMd, nextCards, pairSvg, type Side } from './pair'
import { NO_REPO, openWork, prsOf, staleOf, startSvg, treesOf } from './repo'
import { ownOf, sharedOf, SHARED } from './stages'
import { crossesOff, mapLines, mapSvg, MISSING, parseStatus, STATUS_FILE, stripLines, stripSvg } from './target'
import { ASK, decidePrompt, decisionSvg, linksIn, looksLikeChoice, parseDecision, parseSummary } from './turn'

const PANE = 'build-guide'
const TITLE = 'Build guide'
// The method the person last picked in the Guide tab, kept across sessions.
const PICKED = 'method'

const method = atom({ plugin: 'build-guide', key: 'method' } as const, null as MethodId | null)
const tab = atom({ plugin: 'build-guide', key: 'tab' } as const, 'start')
const env = atom({ plugin: 'build-guide', key: 'env' } as const, { isRead: false, plugins: [], copied: [] } as Env)
const repo = atom({ plugin: 'build-guide', key: 'repo' } as const, NO_REPO)
const summary = atom({ plugin: 'build-guide', key: 'summary' } as const, null as Summary)
const decision = atom({ plugin: 'build-guide', key: 'decision' } as const, null as Decision)
const states = atom({ plugin: 'build-guide', key: 'states' } as const, {} as States)
const stage = atom({ plugin: 'build-guide', key: 'stage' } as const, { at: null, by: null, moves: 0 } as Stage)
const target = atom({ plugin: 'build-guide', key: 'target' } as const, { phase: 'unread' } as Target)
const isTargetOpen = atom({ plugin: 'build-guide', key: 'isTargetOpen' } as const, false)

const picked = async ($: EngineInterface) => methodOf(await read($, method))

const stateIn = (all: States, m: AnyMethod): unknown => (all as Record<string, unknown>)[m.id] ?? m.empty

type Moved = { by: MethodId; at: SharedId }

// Runs a reducer on each method's state (or only one's), keeps the results, moves
// the other methods when one changed the shared stage, and does the work asked for.
async function step($: EngineInterface, reduce: (m: AnyMethod, s: unknown) => Out<unknown> | undefined, only?: AnyMethod) {
  const outs = new Map<MethodId, Out<unknown>>()
  const event: { moved: Moved | null } = { moved: null }
  const all = await update($, states, a => {
    outs.clear()
    event.moved = null
    const next: Record<string, unknown> = { ...a }
    for (const m of only ? [only] : METHODS) {
      const was = stateIn(next as States, m)
      const out = reduce(m, was)
      if (!out) continue
      outs.set(m.id, out)
      next[m.id] = out.s
      const before = sharedOf(m.id, m.stageOf(was))
      const after = sharedOf(m.id, m.stageOf(out.s))
      if (!event.moved && after !== null && after !== before) event.moved = { by: m.id, at: after }
    }
    const moved = event.moved
    if (moved) {
      for (const o of METHODS) {
        const s = stateIn(next as States, o)
        const own = ownOf(o.id, moved.at)
        if (o.id !== moved.by && own && sharedOf(o.id, o.stageOf(s)) !== moved.at) next[o.id] = o.moveTo(s, own)
      }
    }
    return next as States
  })
  const moved = event.moved
  if (moved) await update($, stage, s => ({ at: moved.at, by: moved.by, moves: s.moves + 1 }))
  if (outs.size > 0) await save($, all)
  for (const [id, out] of outs) {
    const m = methodOf(id)
    const path = out.read
    if (path && m.hooks.file) {
      let content: string | null = null
      try {
        content = String(await $.fs.read(path))
      } catch {
        content = null
      }
      await step($, (x, s) => x.hooks.file?.(s, path, content), m)
    }
    const ask = out.ask
    if (ask && m.hooks.answer) void advise($, m, ask)
  }
  return outs
}

// One Haiku call per step: the method's own question, and a line from every
// method on what it would have the person do now.
async function advise($: EngineInterface, m: AnyMethod, ask: { key: string; prompt: string }) {
  const all = await read($, states)
  const prompt =
    `${ask.prompt}\n\nThen write one line for each method below. Start the line with the method name and a colon, ` +
    'and say in under 18 plain words what that method would have the user do now. No dashes, no markdown.\n' +
    METHODS.map(x => `${x.label}: ${x.brief(stateIn(all, x))}`).join('\n')
  let said: string | null = null
  try {
    const r = await $.model.complete({ model: 'haiku', prompt, timeoutMs: 20000 })
    said = r.isAnswered ? r.text : null
  } catch {
    said = null
  }
  await step($, (x, s) => ({ s: x.hooks.answer?.(s, ask.key, said) ?? s }), m)
}

async function save($: EngineInterface, all: States) {
  for (const m of METHODS) {
    const keep = m.persist
    const root = keep?.rootOf(stateIn(all, m))
    if (keep && root) await $.store.set(`${m.id}:${root}`, keep.save(stateIn(all, m)))
  }
}

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
async function mainCheckout($: EngineInterface) {
  const common = await git($, ['rev-parse', '--path-format=absolute', '--git-common-dir'])
  return common === null ? null : common.replace(/\/\.git\/?$/, '')
}

// Reads the repo once per press, never while drawing, so the pane stays still.
async function readRepo($: EngineInterface) {
  const setupFile = (await picked($)).setup?.file
  const top = await git($, ['rev-parse', '--show-toplevel'])
  if (top === null) {
    await update($, repo, () => ({ ...NO_REPO, isRead: true, error: 'This session is not in a git repo.' }))
    return
  }
  const branch = (await git($, ['rev-parse', '--abbrev-ref', 'HEAD'])) ?? '?'
  const status = (await git($, ['status', '--porcelain'])) ?? ''
  const base = ((await git($, ['symbolic-ref', '--short', 'refs/remotes/origin/HEAD'])) ?? 'origin/main').replace(/^origin\//, '')
  const merged = (await git($, ['branch', '--merged', base, '--format=%(refname:short)'])) ?? ''
  const heads = (await git($, ['for-each-ref', '--format=%(refname:short)|%(committerdate:unix)', 'refs/heads'])) ?? ''
  const trees = treesOf((await git($, ['worktree', 'list', '--porcelain'])) ?? '')
  const others = trees.filter((t, i) => i > 0 && t.path && t.path !== top)
  const stale = staleOf(heads, merged, trees, base, Date.now() / 1000)
  let prs: ReturnType<typeof prsOf> = []
  let error: string | null = null
  try {
    const r = await $.process.run(['gh', 'pr', 'list', '--author', '@me', '--state', 'open', '--limit', '8', '--json', 'number,title,headRefName,isDraft,statusCheckRollup,mergeable,reviewDecision'], { timeoutMs: 15000 })
    if (r.exitCode === 0) prs = prsOf(r.stdout)
    else error = 'Could not read pull requests with gh.'
  } catch {
    error = 'Could not read pull requests with gh.'
  }
  const isSetUp = setupFile ? await $.fs.exists(`${top}/${setupFile}`).catch(() => true) : true
  const name = ((await mainCheckout($)) ?? top).split('/').pop() ?? top
  await update($, repo, () => ({ isRead: true, error, name, branch, dirty: status ? status.split('\n').length : 0, stale, worktrees: others.length, prs, isSetUp }))
}

async function readEnv($: EngineInterface) {
  const home = (await $.env.get('HOME')) ?? ''
  let plugins: string[] = []
  try {
    const raw = JSON.parse(String(await $.fs.read(`${home}/.claude/plugins/installed_plugins.json`))) as { plugins?: Record<string, unknown> }
    plugins = Object.keys(raw.plugins ?? {})
  } catch {
    plugins = []
  }
  // skills.sh copies skill files into the user's or the project's skills folder instead of a plugin.
  const copied: MethodId[] = []
  for (const m of METHODS) {
    const has =
      (await $.fs.exists(`${home}/.claude/skills/${m.requires.skill}/SKILL.md`).catch(() => false)) ||
      (await $.fs.exists(`.claude/skills/${m.requires.skill}/SKILL.md`).catch(() => false))
    if (has) copied.push(m.id)
  }
  const value: Env = { isRead: true, plugins, copied }
  await update($, env, () => value)
  return value
}

// The BLDG OS target map, read at the start, on /mod-guide, after each turn and on a press.
async function readTarget($: EngineInterface) {
  const home = (await $.env.get('HOME')) ?? ''
  let text: string | null = null
  try {
    text = String(await $.fs.read(`${home}/${STATUS_FILE}`))
  } catch {
    text = null
  }
  await update($, target, () => (text === null ? { phase: 'missing' } : parseStatus(text)))
}

// A method that keeps progress per repo loads it once its state names no repo:
// at the start, and after /clear starts the session's state over. The shared
// stage then takes the loaded position, and the other methods follow it; a
// load is not a move.
async function loadSaved($: EngineInterface) {
  for (const m of METHODS) {
    const keep = m.persist
    if (!keep || keep.rootOf(stateIn(await read($, states), m))) continue
    const root = (await mainCheckout($)) ?? (await $.session.cwd())
    const saved = await $.store.get(`${m.id}:${root}`)
    await update($, states, a => ({ ...a, [m.id]: keep.load(stateIn(a, m), saved, root) }))
  }
  if ((await read($, stage)).at !== null) return
  const all = await read($, states)
  const from = METHODS.find(m => sharedOf(m.id, m.stageOf(stateIn(all, m))) !== null)
  const at = from ? sharedOf(from.id, from.stageOf(stateIn(all, from))) : null
  if (!from || !at) return
  await update($, states, a => {
    const next: Record<string, unknown> = { ...a }
    for (const o of METHODS) {
      const own = ownOf(o.id, at)
      if (o.id !== from.id && own) next[o.id] = o.moveTo(stateIn(a, o), own)
    }
    return next as States
  })
  await update($, stage, s => ({ ...s, at, by: from.id }))
}

async function startOver($: EngineInterface) {
  const all = await update($, states, a => Object.fromEntries(METHODS.map(m => [m.id, m.reset(stateIn(a, m))])) as States)
  await update($, stage, s => ({ ...s, at: null, by: null }))
  await save($, all)
}

const registered = new Set<string>()

async function registerTools($: EngineInterface) {
  for (const m of METHODS) {
    for (const t of m.tools ?? []) {
      if (registered.has(t.name)) continue
      registered.add(t.name)
      await $.tool.register({ name: t.name, description: t.description, inputSchema: t.inputSchema as never })
    }
  }
}

// Makes `id` the method the Guide and Start tabs show.
async function pick($: EngineInterface, id: MethodId) {
  const m = methodOf(id)
  await $.store.set(PICKED, m.id)
  await update($, method, () => m.id)
  // A guide page of the old method becomes the new method's first page.
  await update($, tab, t => (t === 'start' || t === 'now' || m.guide.some(g => g.id === t) ? t : (m.guide[0]?.id ?? 'start')))
  void readRepo($)
}

// The engine refuses a submitted prompt that starts with a slash, so a slash
// command runs as a command and anything else goes in as the user's message.
function send($: EngineInterface, text: string) {
  const slash = /^\/(\S+)\s*([\s\S]*)$/.exec(text)
  return slash ? $.command.run({ command: slash[1] ?? '', args: slash[2] ?? '' }) : $.prompt.submit({ text, asUser: true })
}

function press($: EngineInterface, a: Act) {
  return a.isSend ? send($, a.text ?? '') : $.prompt.fill({ text: a.text ?? '' })
}

function installCard(m: AnyMethod, e: Env): Card | null {
  const status = skillsOf(m, e)
  if (status === 'ok') return null
  const isOld = status === 'outdated'
  return {
    key: 'install',
    title: isOld ? `${m.requires.name}: your copy is out of date` : `${m.requires.name} not installed`,
    body: `${isOld ? `${m.requires.outdatedNote ?? ''} ` : `The buttons here run ${m.requires.name}, so install it first. `}Run this in a terminal, then start a new session:`,
    color: '#E5342C',
    code: m.requires.install,
    note: isOld ? (m.requires.removeOld ? `Then remove the old copy with: ${m.requires.removeOld}` : undefined) : 'Or pick another method in the Guide tab.',
    acts: [],
  }
}

// The plain-words reply of the first method whose skills are installed.
const explainOf = (e: Env) => (METHODS.find(m => skillsOf(m, e) !== 'missing') ?? METHODS[0]!).explain

// Every pressable element of the pane's last drawing, by key, so a focus that
// lands on one can run it.
const pressable = new Map<string, () => void>()
const ranOnFocus = new Map<string, number>()
let hasKeys = false

function collect(node: unknown) {
  if (Array.isArray(node)) return node.forEach(collect)
  if (!node || typeof node !== 'object') return
  const el = node as { key?: unknown; props?: { onPress?: unknown; children?: unknown } }
  if (typeof el.key === 'string' && typeof el.props?.onPress === 'function') {
    const run = el.props.onPress as (arg?: unknown) => void
    pressable.set(el.key, () => run({}))
  }
  collect(el.props?.children)
}

export const register: Register = (on, options) => {
  // With the guard off nothing stops a merge, so the pane may offer one.
  const isGuarded = (options as { gitGuard?: boolean }).gitGuard !== false

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'mod-guide',
      description: "Open the build guide: pstack and Matt Pocock's flow side by side, under the BLDG OS target map. Add pstack or pocock to pick the one the Guide tab shows.",
    })
    const found = await readEnv($)
    const saved = await $.store.get(PICKED)
    await update($, method, m => m ?? (isMethod(saved) ? saved : detect(found)))
    await registerTools($)
    await loadSaved($)
    await readTarget($)
    // Opens on its own at session start, so the Start tab is the first thing seen.
    void $.ui.open({ id: PANE, title: TITLE, focus: true })
    void readRepo($)

    return next(e)
  })

  on('command.run', { command: 'mod-guide' }, async ($, e) => {
    const asked = e.args.trim().toLowerCase()
    if (isMethod(asked)) await pick($, asked)
    else await readEnv($)
    await readTarget($)
    const all = await read($, states)
    const isBusy = METHODS.some(m => m.isBusy(stateIn(all, m)))
    await update($, tab, t => (isBusy && t === 'start' ? 'now' : t))
    await $.ui.open({ id: PANE, title: TITLE })
    void readRepo($)

    return { text: isMethod(asked) ? `Build guide opened. The Guide tab shows ${asked}.` : 'Build guide opened.' }
  })

  on('command.run', async ($, e, next) => {
    const outs = await step($, (m, s) => m.hooks.command?.(s, e.command, e.args))
    const args = [...outs.values()].map(o => (o as { args?: string }).args).find(a => a !== undefined && a !== e.args) ?? e.args
    const result = await next(args === e.args ? e : { ...e, args })
    if (e.command === 'clear') await loadSaved($)
    return result
  })

  on('skill.prompt', async ($, e, next) => {
    const result = await next(e)
    const outs = await step($, (m, s) => m.hooks.skill?.(s, e.skill, result.text))
    const said = [...outs.values()].map(o => (o as { text?: string }).text).find(t => t !== undefined && t !== result.text) ?? result.text
    return said === result.text ? result : { ...result, text: said }
  })

  // The methods' own tools, served whatever the Guide tab shows.
  for (const m of METHODS) {
    for (const t of m.tools ?? []) {
      on('tool.call', { tool: `mcp__build-guide__${t.name}` }, async ($, e) => {
        const outs = await step($, (_x, s) => t.run(s, e as unknown as Record<string, unknown>), m)
        return { result: (outs.get(m.id) as { result?: string } | undefined)?.result ?? '' }
      })
    }
  }

  on('tool.call', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId) return result
    const said = (result as { text?: unknown }).text
    await step($, (m, s) => m.hooks.tool?.(s, e.tool, e as unknown as Record<string, unknown>, typeof said === 'string' ? said : ''))
    return result
  })

  // Runs before the call, for subagents too, so a blocked command never starts.
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    if (!isGuarded) return next(e)
    const found = await guardBlock(e.command, async () => (await git($, ['rev-parse', '--abbrev-ref', 'HEAD'])) ?? '')
    if (!found) return next(e)
    $.ui.toast(`Build guide: blocked ${found.what}.`)
    return { deny: `build-guide blocked ${found.what}. ${found.why} If it is really needed, ask the person who reviews your work to run it, and tell the user so in plain words.` }
  })

  on('turn.step', async function* ($, e, next) {
    if ((e as { agentId?: string }).agentId === undefined) {
      const effort = e.effort === undefined ? '' : String(e.effort)
      await step($, (m, s) => {
        const change = m.hooks.step
        return change ? { s: change(s, e.model, effort) } : undefined
      })
    }

    return yield* next(e)
  })

  // Anything the person sends answers or replaces the open decision. The
  // methods see the prompt; none of them changes it.
  on('prompt.submit', async ($, e, next) => {
    await update($, decision, () => null)
    await update($, summary, s => (s ? { ...s, isWaiting: false } : s))
    const isPerson = e.origin.kind === 'composer' || e.origin.kind === 'bridge'
    const setup = await read($, env)
    await step($, (m, s) => m.hooks.prompt?.(s, e.text, isPerson, skillsOf(m, setup) !== 'missing'))
    return next(e)
  })

  // The desktop spends the first click on an unfocused pane on focus, so a
  // button needs two clicks. When a main turn ends the pane asks for the
  // keyboard; the surface refuses while text is typed.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if ((e as { agentId?: string }).agentId !== undefined) return result
    void $.ui.open({ id: PANE, title: TITLE, focus: true })
    await loadSaved($)
    await readTarget($)
    const answer = e.answer.trim()
    if (e.isAborted || !answer) {
      await update($, decision, () => null)
      return result
    }
    // A short reply is its own summary, so it costs no model call.
    if (answer.length < 280 && !looksLikeChoice(answer)) {
      await update($, decision, () => null)
      await update($, summary, () => ({ done: answer, next: '', links: linksIn(answer), isWaiting: false }))
      return result
    }
    void (async () => {
      const ask = await $.model.complete({ model: 'haiku', prompt: decidePrompt(METHODS, answer), timeoutMs: 20000 })
      const found = ask.isAnswered && looksLikeChoice(answer) ? parseDecision(ask.text) : null
      const said = ask.isAnswered ? parseSummary(ask.text, answer) : null
      await update($, decision, () => found)
      await update($, summary, () => (said ? { ...said, isWaiting: said.isWaiting || found !== null } : null))
      if (found) $.ui.toast('Build guide: Claude is asking you to choose. The pane has a button for each option.')
      else if (said?.isWaiting) $.ui.toast('Build guide: Claude is waiting on you. The pane says what for.')
    })()
    return result
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const pm = await picked($)
    const all = await read($, states)
    const current = await read($, tab)
    const setup = await read($, env)
    const r = await read($, repo)
    const ui = $.ui.resolve(e)
    const { Box, Button, Markdown, Text, Code } = ui
    const isDesktop = e.surface !== 'terminal' && 'Svg' in ui
    // Drawn only where the surface has Svg; elsewhere the caller draws text.
    const picture = (key: string, source: string, alt: string) => {
      if (!('Svg' in ui)) return <Text key={key}>{alt}</Text>
      const { Svg } = ui
      return <Svg key={key} source={source} alt={alt} {...fit(source, e.props.bodyColumns)} />
    }

    const button = (a: Act, isPrimary = a.isPrimary === true) => (
      <Button
        key={a.key}
        label={a.label}
        variant={isPrimary ? 'primary' : 'secondary'}
        onPress={() => {
          void press($, a)
        }}
      />
    )
    const row = (acts: Act[]) => (
      <Box flexDirection="row" flexWrap="wrap" gap={1}>
        {acts.map(a => button(a))}
      </Box>
    )
    const lines = (key: string, rows: string[], color?: string) => (
      <Box key={key} flexDirection="column">
        {rows.map((t, i) => (
          <Text key={`${key}-${i}`} color={color}>
            {t}
          </Text>
        ))}
      </Box>
    )

    // ---------- Band 1: the target strip ----------

    const map = await read($, target)
    const isOpen = await read($, isTargetOpen)
    const pr = r.prs.find(p => p.branch !== '' && p.branch === r.branch)
    const work = [...METHODS.flatMap(m => m.focus?.(stateIn(all, m)) ?? []), pr?.title ?? '', r.branch].filter(Boolean)
    const toggle = (
      <Box key="target-row" flexDirection="row" gap={1}>
        <Button
          key="target-toggle"
          label={isOpen ? 'Hide the full map' : 'Show the full map'}
          plain
          onPress={() => {
            void readTarget($)
            void update($, isTargetOpen, o => !o)
          }}
        />
      </Box>
    )
    const strip = (() => {
      if (map.phase === 'unread') return null
      if (map.phase === 'missing') return <Text key="target">{MISSING}</Text>
      if (map.phase === 'bad') return <Text key="target">{`The target map file could not be read: ${map.reason}.`}</Text>
      const s = map.data
      const matched = crossesOff(s, work)
      const alt = `${s.goal}: ${s.flags.map(f => `${f.name} ${f.jobs.length ? `${f.jobs.filter(j => j.state !== 'moved').length} left` : (f.note ?? '')}`).join(', ')}`
      return (
        <Box key="target" flexDirection="column">
          {isDesktop
            ? picture(isOpen ? 'target-map' : 'target-strip', isOpen ? mapSvg(s, Date.now()) : stripSvg(s, matched), alt)
            : lines('target-lines', isOpen ? mapLines(s, Date.now()) : stripLines(s, matched))}
          {toggle}
        </Box>
      )
    })()

    const go = (id: string) => () => {
      void update($, tab, () => id)
      if (id === 'start') void readRepo($)
    }
    const page = pm.guide.find(g => g.id === current)
    const top: { id: string; label: string; key: string; isOn: boolean }[] = [
      { id: 'start', label: 'Start', key: 'tab-start', isOn: current === 'start' },
      { id: 'now', label: 'Now', key: 'tab-now', isOn: current === 'now' },
      { id: page ? current : (pm.guide[0]?.id ?? 'start'), label: 'Guide', key: 'tab-guide', isOn: page !== undefined },
    ]
    const nav = (
      <Box flexDirection="row" flexWrap="wrap" gap={1}>
        {top.map(t => (
          <Button key={t.key} label={t.label} variant={t.isOn ? 'primary' : 'secondary'} onPress={go(t.id)} />
        ))}
      </Box>
    )

    const drawCard = (c: Card, extra?: JSX.Element) => (
      <Box key={c.key} flexDirection="column" gap={1} borderStyle="round" borderColor={c.color} paddingX={1}>
        <Text bold color={c.color}>
          {c.title}
        </Text>
        <Text>{c.body}</Text>
        {c.code ? <Code source={c.code} /> : null}
        {c.note ? <Text dimColor>{c.note}</Text> : null}
        {c.acts.length > 0 ? row(c.acts) : null}
        {extra ?? null}
      </Box>
    )

    const open = await read($, decision)
    const said = await read($, summary)
    const explain = explainOf(setup)
    // A waiting turn with no options read from it still gets one-press answers.
    const fallback: Act[] = [
      { key: 'reply-yes', label: 'Yes, go ahead', text: 'yes, go ahead', isSend: true, isPrimary: true },
      { key: 'reply-no', label: 'Not yet', text: 'no, hold off for now', isSend: true },
      { ...explain, key: 'reply-plain' },
    ]
    const summaryCard =
      said === null ? null : (
        <Box key="summary" flexDirection="column" borderStyle="round" borderColor={said.isWaiting ? '#F56300' : '#D2D2D7'} paddingX={1}>
          <Text bold color={said.isWaiting ? '#F56300' : undefined}>
            {said.isWaiting ? 'Needs you' : 'Last turn'}
          </Text>
          <Markdown text={[said.done, said.next ? `**Next:** ${said.next}` : '', said.links.map(l => `[PR #${l.split('/').pop()}](${l})`).join(' · ')].filter(Boolean).join('\n\n')} />
          {said.isWaiting && open === null ? row(fallback) : null}
        </Box>
      )

    const choose = (key: string, label: string) => (
      <Button
        key={`choose-${key}`}
        label={label}
        variant={key === open?.pick ? 'primary' : 'secondary'}
        onPress={() => {
          void $.prompt.submit({ text: key, asUser: true })
        }}
      />
    )
    const decisionCard =
      open === null ? null : isDesktop ? (
        <Box key="decision" flexDirection="column" gap={1}>
          {picture('decision-svg', decisionSvg(open, ASK), `${ASK.title}: ${open.question}`)}
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {open.options.map(o => choose(o.key, o.key === open.pick ? `★ ${o.key}` : o.key))}
          </Box>
        </Box>
      ) : (
        <Box key="decision" flexDirection="column" gap={1} borderStyle="round" paddingX={1}>
          <Text bold>
            {ASK.title}: {open.question}
          </Text>
          {open.pick ? (
            <Text>
              {ASK.pick}: {open.options.find(o => o.key === open.pick)?.label ?? open.pick}. {open.why}
            </Text>
          ) : open.why ? (
            <Text dimColor>{open.why}</Text>
          ) : null}
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {open.options.map(o => choose(o.key, `${o.key} · ${o.label}${o.tier ? ` (${o.tier})` : ''}`))}
          </Box>
        </Box>
      )

    const tree = await (async () => {
      if (current === 'start') {
        const install = installCard(pm, setup)
        const isMissing = skillsOf(pm, setup) === 'missing'
        const needsSetup = pm.setup !== undefined && r.isRead && !r.isSetUp && install === null
        const usable = pm.starts.filter(a => !a.needs || setup.plugins.some(k => k.startsWith(a.needs!)))
        const starts = isMissing ? pm.plainStarts : needsSetup && pm.setup ? [{ ...pm.setup.act, isPrimary: true }, ...usable.map(a => ({ ...a, isPrimary: false }))] : usable
        const rows = openWork(r, pm, !isGuarded)
        return (
          <Box flexDirection="column" gap={1}>
            {nav}
            {strip}
            {install
              ? drawCard(
                  install,
                  <Box flexDirection="row" gap={1}>
                    <Button key="check-again" label="Check again" onPress={() => readEnv($)} />
                  </Box>,
                )
              : null}
            {summaryCard}
            {decisionCard}
            {isDesktop && r.isRead && r.name ? (
              picture('dashboard', startSvg(r), `${r.name} on ${r.branch}: ${r.prs.length} open PRs, ${r.dirty} uncommitted files, ${r.stale.length} stale branches, ${r.worktrees} other worktrees`)
            ) : (
              <Text bold>{r.isRead ? (r.name ? `${r.name} · ${r.branch}` : 'No repo') : 'Reading the repo…'}</Text>
            )}
            {r.error ? <Text dimColor>{r.error}</Text> : null}
            {rows.length > 0 ? <Text bold>Open work</Text> : null}
            {rows.map(w => (
              <Box key={w.key} flexDirection="row" flexWrap="wrap" gap={1} alignItems="center">
                <Text>{w.label}</Text>
                {w.acts.map(a => button(a))}
              </Box>
            ))}
            <Text bold>Start something</Text>
            {needsSetup && pm.setup ? <Text color="#E5342C">{pm.setup.warn}</Text> : null}
            {row(starts)}
            <Text dimColor>{`${pm.startNote} These are ${pm.label}'s starts; the Guide tab picks the method.`}</Text>
            <Box flexDirection="row" gap={1}>
              <Button key="refresh" label="Refresh" onPress={() => readRepo($)} />
            </Box>
          </Box>
        )
      }

      if (current === 'now') {
        const at = (await read($, stage)).at
        const shared = at ?? METHODS.map(m => sharedOf(m.id, m.stageOf(stateIn(all, m)))).find(x => x !== null) ?? null
        // Haiku's lines for the running step, from whichever method asked for them.
        const would: Record<string, string> = Object.assign({}, ...METHODS.map(m => m.would?.(stateIn(all, m)) ?? {}))
        const sides: Side[] = METHODS.map(m => {
          const s = stateIn(all, m)
          return { id: m.id, label: m.label, own: m.stageOf(s), view: m.column(s, would[m.id]) }
        })
        const where = SHARED.find(x => x.id === shared)?.name ?? 'not started'
        const pair = isDesktop ? (
          picture('now', pairSvg(shared, sides), `Stage: ${where}. ${sides.map(x => `${x.label}: ${x.view.stage}. ${x.view.would}`).join(' ')}`)
        ) : (
          <Box key="now" flexDirection="column" gap={1}>
            {lines('bar', barLines(sides))}
            <Box flexDirection="row" gap={1}>
              {sides.map(x => (
                <Box key={`col-${x.id}`} flexDirection="column" width={`${Math.floor(100 / sides.length)}%`}>
                  <Markdown text={columnMd(x)} />
                </Box>
              ))}
            </Box>
          </Box>
        )

        // ---------- Band 3: next move ----------
        const cards = nextCards(METHODS.map(m => ({ id: m.id, label: m.label, move: m.next(stateIn(all, m)) })))
        const moveCards = (
          <Box key="next" flexDirection="row" flexWrap="wrap" gap={1}>
            {cards.map(c => {
              const missing = c.ids.map(methodOf).filter(m => skillsOf(m, setup) === 'missing')
              return (
                <Box key={`next-card-${c.key}`} flexDirection="column" borderStyle="round" borderColor="#1DA851" paddingX={1} flexGrow={1} width={cards.length > 1 ? '48%' : '100%'}>
                  <Text bold color="#137A3A">
                    {c.title}
                  </Text>
                  <Text bold>{c.move.label}</Text>
                  <Code source={c.move.text.trim() || ' '} />
                  {c.move.why ? <Text dimColor>{c.move.why}</Text> : null}
                  {missing.length > 0 ? (
                    <Box flexDirection="column">
                      <Text color="#E5342C">{`${missing.map(m => m.requires.name).join(' and ')} not installed. Run:`}</Text>
                      <Code source={missing.map(m => m.requires.install).join('\n')} />
                    </Box>
                  ) : (
                    button({ key: `next-${c.key}`, label: 'Put in prompt', text: c.move.text, isPrimary: true })
                  )}
                </Box>
              )
            })}
          </Box>
        )
        // A finished task list outranks a flow position: its next moves replace the quick replies.
        const phases = METHODS.map(m => m.phase(stateIn(all, m)))
        const isDone = phases.includes('done')
        const replies = isDone ? METHODS.filter((_, i) => phases[i] === 'done').flatMap(m => m.after) : phases.includes('running') ? during(explain) : []
        const owned = map.phase === 'ok' ? map.data.decisions : []
        return (
          <Box flexDirection="column" gap={1}>
            {nav}
            {strip}
            {pair}
            <Text bold>Next move</Text>
            {moveCards}
            {summaryCard}
            {decisionCard}
            {replies.length > 0 ? <Text dimColor>{isDone ? 'Steps done. Pick what comes next.' : 'These send at once and wait their turn.'}</Text> : null}
            {replies.length > 0 ? row(replies) : null}
            {owned.length > 0 ? <Text bold>Decisions you own</Text> : null}
            {owned.length > 0 ? lines('owned', owned.map(d => `• ${d.length > 110 ? `${d.slice(0, 109).trimEnd()}…` : d}`)) : null}
            <Box flexDirection="row" gap={1}>
              <Button key="reset" label="Start over" onPress={() => startOver($)} />
            </Box>
          </Box>
        )
      }

      const picker = (
        <Box flexDirection="row" flexWrap="wrap" gap={1} alignItems="center">
          <Text dimColor>Method</Text>
          {METHODS.map(x => (
            <Button
              key={`pick-${x.id}`}
              label={x.label}
              variant={x.id === pm.id ? 'primary' : 'secondary'}
              onPress={() => {
                void pick($, x.id)
              }}
            />
          ))}
        </Box>
      )
      const pages = (
        <Box flexDirection="row" flexWrap="wrap" gap={1}>
          {pm.guide.map(g => (
            <Button key={`tab-${g.id}`} label={g.id === current ? `• ${g.label}` : g.label} plain onPress={go(g.id)} />
          ))}
        </Box>
      )
      const shown = page ?? pm.guide[0]
      if (!shown) return <Box flexDirection="column">{nav}</Box>
      const drawing = isDesktop && shown.svg ? picture(`guide-${shown.id}`, shown.svg, shown.alt) : <Markdown text={shown.md} />
      return (
        <Box flexDirection="column" gap={1}>
          {nav}
          {strip}
          {picker}
          {pages}
          {shown.recipes ? null : drawing}
          {shown.note ? <Text dimColor>{shown.note}</Text> : null}
          {(shown.rows ?? []).map((x, i) => (
            <Box key={`row-${i}`} flexDirection="row" flexWrap="wrap" gap={1} alignItems="center">
              {x.label ? <Text bold>{x.label}</Text> : null}
              {x.acts.map(a => button(a))}
            </Box>
          ))}
          {shown.recipes ? <Text bold>Recipes: press one to put it in your prompt</Text> : null}
          {(shown.recipes ?? []).map(x => (
            <Box key={`recipe-${x.title}`} flexDirection="column">
              <Text bold>{x.title}</Text>
              <Code source={x.prompt} />
              {button({ key: `use-${x.title}`, label: 'Put in prompt', text: x.prompt })}
            </Box>
          ))}
          {shown.recipes ? drawing : null}
        </Box>
      )
    })()
    pressable.clear()
    collect(tree)
    hasKeys = e.props.isFocused
    return tree
  })

  // The desktop spends the first click on a pane that lacks the keyboard on
  // giving it the keyboard, so the press never arrives. That click still moves
  // the focus ring onto the button, so run the button from there, and drop the
  // press if one follows.
  on('ui.focus', { requestId: PANE }, async ($, e, next) => {
    const moved = await next(e)
    const run = e.element ? pressable.get(e.element) : undefined
    if (!hasKeys && e.origin.kind === 'person' && e.element && run && !moved.deny) {
      ranOnFocus.set(e.element, Date.now())
      run()
    }
    return moved
  })

  on('ui.press', { requestId: PANE }, async ($, e, next) => {
    const at = ranOnFocus.get(e.element)
    if (at !== undefined && Date.now() - at < 1500) {
      ranOnFocus.delete(e.element)
      return { element: e.element }
    }
    return next(e)
  })
}
