// The build guide pane. Everything a method needs done (a read, a write, a
// model call, a toast) happens here: the engine follows `$` only into functions
// of this file, so the methods stay data and pure functions.

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Decision, Env, MethodId, Seen, States, Summary } from '../types'
import { fit } from './draw'
import { guardBlock } from './guard'
import { during, skillsOf, type Act, type AnyMethod, type Card, type Out } from './method'
import { detect, isMethod, methodOf, METHODS } from './methods'
import { NO_REPO, openWork, prsOf, staleOf, startSvg, treesOf } from './repo'
import { decidePrompt, decisionSvg, linksIn, looksLikeChoice, parseDecision, parseSummary } from './turn'

const PANE = 'build-guide'
const TITLE = 'Build guide'
// The method the person last picked, kept across sessions.
const PICKED = 'method'

const method = atom({ plugin: 'build-guide', key: 'method' } as const, null as MethodId | null)
const tab = atom({ plugin: 'build-guide', key: 'tab' } as const, 'start')
const env = atom({ plugin: 'build-guide', key: 'env' } as const, { isRead: false, plugins: [], copied: [] } as Env)
const repo = atom({ plugin: 'build-guide', key: 'repo' } as const, NO_REPO)
const summary = atom({ plugin: 'build-guide', key: 'summary' } as const, null as Summary)
const decision = atom({ plugin: 'build-guide', key: 'decision' } as const, null as Decision)
const states = atom({ plugin: 'build-guide', key: 'states' } as const, {} as States)
// The tally changes on every tool call, so it lives apart from the methods'
// states: only the terminal text reads it, and the desktop picture does not redraw for it.
const seen = atom({ plugin: 'build-guide', key: 'seen' } as const, { commands: 0, skills: 0, tools: 0, last: [] } as Seen)

const active = async ($: EngineInterface) => methodOf(await read($, method))

const stateIn = (all: States, m: AnyMethod): unknown => (all as Record<string, unknown>)[m.id] ?? m.empty

// Runs a method's reducer on its state, keeps the result, and does the work it asks for.
async function step($: EngineInterface, m: AnyMethod, reduce: (s: unknown) => Out<unknown> | undefined) {
  let out: Out<unknown> | undefined
  const all = await update($, states, a => {
    out = reduce(stateIn(a, m))
    return out ? { ...a, [m.id]: out.s } : a
  })
  if (!out) return out
  if (m.persist) {
    const root = m.persist.rootOf(stateIn(all, m))
    if (root) await $.store.set(`${m.id}:${root}`, m.persist.save(stateIn(all, m)))
  }
  if (out.toast) $.ui.toast(out.toast)
  const path = out.read
  if (path && m.hooks.file) {
    let content: string | null = null
    try {
      content = String(await $.fs.read(path))
    } catch {
      content = null
    }
    await step($, m, s => m.hooks.file?.(s, path, content))
  }
  const ask = out.ask
  if (ask && m.hooks.answer) {
    void (async () => {
      const said = await $.model.complete({ model: 'haiku', prompt: ask.prompt, timeoutMs: 20000 })
      await step($, m, s => ({ s: m.hooks.answer?.(s, ask.key, said.isAnswered ? said.text : null) ?? s }))
    })()
  }
  return out
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
  const setupFile = (await active($)).setup?.file
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
    const r = await $.process.run(['gh', 'pr', 'list', '--author', '@me', '--state', 'open', '--limit', '8', '--json', 'number,title,isDraft,statusCheckRollup,mergeable,reviewDecision'], { timeoutMs: 15000 })
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

// A method that keeps progress per repo loads it once its state names no repo:
// at the start, and after /clear starts the session's state over.
async function loadSaved($: EngineInterface, m: AnyMethod) {
  const keep = m.persist
  if (!keep || keep.rootOf(stateIn(await read($, states), m))) return
  const root = (await mainCheckout($)) ?? (await $.session.cwd())
  const saved = await $.store.get(`${m.id}:${root}`)
  await update($, states, a => ({ ...a, [m.id]: keep.load(stateIn(a, m), saved, root) }))
}

const registered = new Set<string>()

// Makes `id` the active method: its tab, its saved progress and its tools.
async function enter($: EngineInterface, id: MethodId) {
  const m = methodOf(id)
  await update($, method, () => m.id)
  // A guide page of the old method becomes the new method's first page.
  await update($, tab, t => (t === 'start' || t === 'now' || m.guide.some(g => g.id === t) ? t : (m.guide[0]?.id ?? 'start')))
  await loadSaved($, m)
  for (const t of m.tools ?? []) {
    if (registered.has(t.name)) continue
    registered.add(t.name)
    await $.tool.register({ name: t.name, description: t.description, inputSchema: t.inputSchema as never })
  }
}

async function pick($: EngineInterface, id: MethodId) {
  await $.store.set(PICKED, id)
  await enter($, id)
  void readRepo($)
}

function tally($: EngineInterface, kind: keyof Omit<Seen, 'last'>, label: string) {
  return update($, seen, s => ({ ...s, [kind]: s[kind] + 1, last: [...s.last, label].slice(-4) }))
}

// The engine refuses a submitted prompt that starts with a slash, so a slash
// command runs as a command and anything else goes in as the user's message.
function send($: EngineInterface, text: string) {
  const slash = /^\/(\S+)\s*([\s\S]*)$/.exec(text)
  return slash ? $.command.run({ command: slash[1] ?? '', args: slash[2] ?? '' }) : $.prompt.submit({ text, asUser: true })
}

async function press($: EngineInterface, a: Act) {
  const change = a.apply
  if (change) return step($, await active($), s => ({ s: change(s) }))
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
    note: isOld ? (m.requires.removeOld ? `Then remove the old copy with: ${m.requires.removeOld}` : undefined) : 'Or pick another method above.',
    acts: [],
  }
}

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
      description: "Open the build guide for pstack or Matt Pocock's flow. Add pstack or pocock to switch.",
    })
    const found = await readEnv($)
    const saved = await $.store.get(PICKED)
    await enter($, (await read($, method)) ?? (isMethod(saved) ? saved : detect(found)))
    // Opens on its own at session start, so the Start tab is the first thing seen.
    void $.ui.open({ id: PANE, title: TITLE, focus: true })
    void readRepo($)

    return next(e)
  })

  on('command.run', { command: 'mod-guide' }, async ($, e) => {
    const asked = e.args.trim().toLowerCase()
    if (isMethod(asked)) await pick($, asked)
    else await readEnv($)
    const m = await active($)
    const isBusy = m.isBusy(stateIn(await read($, states), m))
    await update($, tab, t => (isBusy && t === 'start' ? 'now' : t))
    await $.ui.open({ id: PANE, title: TITLE })
    void readRepo($)

    return { text: `Build guide opened on ${m.label}.` }
  })

  on('command.run', async ($, e, next) => {
    const m = await active($)
    await tally($, m.knows(e.command) ? 'skills' : 'commands', `/${e.command}`)
    const out = await step($, m, s => m.hooks.command?.(s, e.command, e.args))
    const args = (out as { args?: string } | undefined)?.args ?? e.args
    const result = await next(args === e.args ? e : { ...e, args })
    if (e.command === 'clear') await loadSaved($, m)
    return result
  })

  on('skill.prompt', async ($, e, next) => {
    const m = await active($)
    await tally($, 'skills', e.skill)
    const result = await next(e)
    const out = await step($, m, s => m.hooks.skill?.(s, e.skill, result.text))
    const said = (out as { text?: string } | undefined)?.text ?? result.text
    return said === result.text ? result : { ...result, text: said }
  })

  // The methods' own tools, served whichever method is active.
  for (const m of METHODS) {
    for (const t of m.tools ?? []) {
      on('tool.call', { tool: `mcp__build-guide__${t.name}` }, async ($, e) => {
        const out = await step($, m, s => t.run(s, e as unknown as Record<string, unknown>))
        return { result: (out as { result?: string } | undefined)?.result ?? '' }
      })
    }
  }

  on('tool.call', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId) return result
    const m = await active($)
    await tally($, 'tools', e.tool.split('__').pop() ?? e.tool)
    const said = (result as { text?: unknown }).text
    await step($, m, s => m.hooks.tool?.(s, e.tool, e as unknown as Record<string, unknown>, typeof said === 'string' ? said : ''))
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
      const m = await active($)
      const effort = e.effort === undefined ? '' : String(e.effort)
      const change = m.hooks.step
      if (change) await step($, m, s => ({ s: change(s, e.model, effort) }))
    }

    return yield* next(e)
  })

  // Anything the person sends answers or replaces the open decision.
  on('prompt.submit', async ($, e, next) => {
    await update($, decision, () => null)
    await update($, summary, s => (s ? { ...s, isWaiting: false } : s))
    const m = await active($)
    const isPerson = e.origin.kind === 'composer' || e.origin.kind === 'bridge'
    const hasSkills = skillsOf(m, await read($, env)) !== 'missing'
    const out = await step($, m, s => m.hooks.prompt?.(s, e.text, isPerson, hasSkills))
    const note = (out as { note?: string } | undefined)?.note
    return next(note ? { ...e, context: [...(e.context ?? []), note] } : e)
  })

  // The desktop spends the first click on an unfocused pane on focus, so a
  // button needs two clicks. When a main turn ends the pane asks for the
  // keyboard; the surface refuses while text is typed.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if ((e as { agentId?: string }).agentId !== undefined) return result
    void $.ui.open({ id: PANE, title: TITLE, focus: true })
    const m = await active($)
    await loadSaved($, m)
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
      const ask = await $.model.complete({ model: 'haiku', prompt: decidePrompt(m, answer), timeoutMs: 20000 })
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
    const m = await active($)
    const s = stateIn(await read($, states), m)
    const current = await read($, tab)
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

    const page = m.guide.find(g => g.id === current)
    const go = (id: string) => () => {
      void update($, tab, () => id)
      if (id === 'start') void readRepo($)
    }
    const top: { id: string; label: string; key: string; isOn: boolean }[] = [
      { id: 'start', label: 'Start', key: 'tab-start', isOn: current === 'start' },
      { id: 'now', label: 'Now', key: 'tab-now', isOn: current === 'now' },
      { id: page ? current : (m.guide[0]?.id ?? 'start'), label: 'Guide', key: 'tab-guide', isOn: page !== undefined },
    ]
    const nav = (
      <Box flexDirection="column" gap={1}>
        <Box flexDirection="row" flexWrap="wrap" gap={1} alignItems="center">
          <Text dimColor>Method</Text>
          {METHODS.map(x => (
            <Button
              key={`method-${x.id}`}
              label={x.label}
              variant={x.id === m.id ? 'primary' : 'secondary'}
              onPress={() => {
                void pick($, x.id)
              }}
            />
          ))}
        </Box>
        <Box flexDirection="row" flexWrap="wrap" gap={1}>
          {top.map(t => (
            <Button key={t.key} label={t.label} variant={t.isOn ? 'primary' : 'secondary'} onPress={go(t.id)} />
          ))}
        </Box>
        {page ? (
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {m.guide.map(g => (
              <Button key={`tab-${g.id}`} label={g.id === current ? `• ${g.label}` : g.label} plain onPress={go(g.id)} />
            ))}
          </Box>
        ) : null}
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
    const cards = m.cards?.(s) ?? []

    const open = await read($, decision)
    const said = await read($, summary)
    // A waiting turn with no options read from it still gets one-press answers.
    const fallback: Act[] = [
      { key: 'reply-yes', label: 'Yes, go ahead', text: 'yes, go ahead', isSend: true, isPrimary: true },
      { key: 'reply-no', label: 'Not yet', text: 'no, hold off for now', isSend: true },
      { ...m.explain, key: 'reply-plain' },
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
          {picture('decision-svg', decisionSvg(open, m), `${m.ask.title}: ${open.question}`)}
          <Box flexDirection="row" flexWrap="wrap" gap={1}>
            {open.options.map(o => choose(o.key, o.key === open.pick ? `★ ${o.key}` : o.key))}
          </Box>
        </Box>
      ) : (
        <Box key="decision" flexDirection="column" gap={1} borderStyle="round" paddingX={1}>
          <Text bold>
            {m.ask.title}: {open.question}
          </Text>
          {open.pick ? (
            <Text>
              {m.ask.pick}: {open.options.find(o => o.key === open.pick)?.label ?? open.pick}. {open.why}
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
        const r = await read($, repo)
        const setup = await read($, env)
        const install = installCard(m, setup)
        const isMissing = skillsOf(m, setup) === 'missing'
        const needsSetup = m.setup !== undefined && r.isRead && !r.isSetUp && install === null
        const starts = isMissing ? m.plainStarts : needsSetup && m.setup ? [{ ...m.setup.act, isPrimary: true }, ...m.starts.map(a => ({ ...a, isPrimary: false }))] : m.starts
        const rows = openWork(r, m, !isGuarded)
        return (
          <Box flexDirection="column" gap={1}>
            {nav}
            {install
              ? drawCard(
                  install,
                  <Box flexDirection="row" gap={1}>
                    <Button key="check-again" label="Check again" onPress={() => readEnv($)} />
                  </Box>,
                )
              : null}
            {cards.map(c => drawCard(c))}
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
            {needsSetup && m.setup ? <Text color="#E5342C">{m.setup.warn}</Text> : null}
            {row(starts)}
            <Text dimColor>{m.startNote}</Text>
            <Box flexDirection="row" gap={1}>
              <Button key="refresh" label="Refresh" onPress={() => readRepo($)} />
            </Box>
          </Box>
        )
      }

      if (current === 'now') {
        const view = m.now(s, await read($, seen))
        const replies = view.phase === 'running' ? during(m.explain) : view.phase === 'done' ? m.after : []
        return (
          <Box flexDirection="column" gap={1}>
            {nav}
            {cards.map(c => drawCard(c))}
            {summaryCard}
            {decisionCard}
            {isDesktop ? picture('now', view.svg, view.alt) : <Markdown text={view.md} />}
            {row([view.next, ...view.others])}
            {view.note ? <Text dimColor>{view.note}</Text> : null}
            {replies.length > 0 ? <Text dimColor>{view.phase === 'done' ? 'Steps done. Pick what comes next.' : 'These send at once and wait their turn.'}</Text> : null}
            {replies.length > 0 ? row(replies) : null}
            <Box flexDirection="row" gap={1}>
              {button(view.reset)}
            </Box>
          </Box>
        )
      }

      const shown = page ?? m.guide[0]
      if (!shown) return <Box flexDirection="column">{nav}</Box>
      const drawing = isDesktop && shown.svg ? picture(`guide-${shown.id}`, shown.svg, shown.alt) : <Markdown text={shown.md} />
      return (
        <Box flexDirection="column" gap={1}>
          {nav}
          {shown.recipes ? null : drawing}
          {shown.note ? <Text dimColor>{shown.note}</Text> : null}
          {(shown.rows ?? []).map((r, i) => (
            <Box key={`row-${i}`} flexDirection="row" flexWrap="wrap" gap={1} alignItems="center">
              {r.label ? <Text bold>{r.label}</Text> : null}
              {r.acts.map(a => button(a))}
            </Box>
          ))}
          {shown.recipes ? <Text bold>Recipes: press one to put it in your prompt</Text> : null}
          {(shown.recipes ?? []).map(r => (
            <Box key={`recipe-${r.title}`} flexDirection="column">
              <Text bold>{r.title}</Text>
              <Code source={r.prompt} />
              {button({ key: `use-${r.title}`, label: 'Put in prompt', text: r.prompt })}
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
