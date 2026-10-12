# BLDG Skills

Matt Nicosia's skill library, published as a Claude Code **plugin marketplace**.

This repo is the source of truth. Do not treat `~/.claude/skills` as the canonical copy.

## Install

```bash
claude plugin marketplace add mattnicosia/bldg-skills
claude plugin install bldg-construction@bldg-skills
```

Install any plugin from the table below by name. A plugin is the install unit: one
command brings in every skill inside it, and `claude plugin update` keeps it current.
Nothing is copied into a second location, so nothing drifts.

## Plugins

| Plugin | Skills | Whose | What it is |
|---|---|---|---|
| [`alex-hormozi`](plugins/alex-hormozi) | 8 | Alex Hormozi | Skills built on Alex Hormozi's frameworks: grand slam offers, lead magnets, lead machines and money models, with their interview companions. Mirror maintained by Matt Nicosia. |
| [`bldg-agent-ops`](plugins/bldg-agent-ops) | 2 |  | Running agents: session worksheets and workflow scaffolding. |
| [`bldg-coding`](plugins/bldg-coding) | 7 |  | Coding skills: review, debugging, architecture and the caveman pass. |
| [`bldg-construction`](plugins/bldg-construction) | 17 |  | Construction estimating: drawing indexing, scope of work generation in Excel and PDF, bid leveling, proposals and job folder setup. |
| [`bldg-creative`](plugins/bldg-creative) | 2 |  | Creative work: image prompting, voice, and the gauntlet loop. |
| [`bldg-distills`](plugins/bldg-distills) | 12 |  | Distilled one-page methods pulled out of longer sources. |
| [`bldg-documents`](plugins/bldg-documents) | 1 |  | Document generation and release. |
| [`bldg-house`](plugins/bldg-house) | 4 |  | House build skills: project and site level-ups, page teardowns, and the cloud sync auditor. |
| [`bldg-maker-school`](plugins/bldg-maker-school) | 46 |  | The Maker School library: growth, offers, funnels, outreach and operating skills. |
| [`bldg-marketing`](plugins/bldg-marketing) | 25 |  | Marketing: funnels, positioning, SEO, ads, content and speed to lead. |
| [`bldg-social`](plugins/bldg-social) | 4 |  | Social: posting, scheduling and the scroll-stop technique. |
| [`bldg-strategy`](plugins/bldg-strategy) | 7 |  | Strategy: idea scoring, prediction, competitive work and planning. |
| [`bldg-website-design`](plugins/bldg-website-design) | 9 |  | Website design and build: frontend design, motion, cloning and upgrades. |
| [`corey-ganim`](plugins/corey-ganim) | 3 | Corey Ganim | Corey Ganim's Build With AI set, v3.1.1, from Return My Time. Claude Cowork workspace onboarding, an AI readiness self-assessment on the Audit-Optimize-Automate framework, and a session context loader. The self-assessment is the paid, community-only version. |
| [`matt-pocock`](plugins/matt-pocock) | 37 | Matt Pocock | Matt Pocock's skill collection, mirrored at 1.3.1. TypeScript, testing, code review and the productivity set. Mirror maintained by Matt Nicosia; upstream docs in upstream/. |
| [`build-guide`](plugins/build-guide) | mod |  | A side pane for building with Claude. A strip at the top shows the BLDG OS target map (jobs left under each flag, stuck jobs, and a pill when your current work crosses a job off); press it for the full map. The Now tab shows pstack and Matt Pocock's flow side by side on the same work: one stage bar, a column per method with its steps and what it would do now, and a next-move card per method with a button that fills your prompt. Neither method toasts or adds notes to your prompts. Start shows the repo's open PRs, uncommitted files, stale branches and worktrees, each with a button, plus one-press starts for the method picked in the Guide tab. After each turn a card says what Claude did, and when Claude asks you to choose, a card puts a button on each option. Pocock's flow also needs `matt-pocock`, the v1.3.1 mirror above. It stops Claude from running destructive git (pushing to main, force pushing, `reset --hard`, `clean -f`, `branch -D`, `checkout .`, `restore .`, `gh pr merge`); turn that off with the `gitGuard` option on a reviewer's machine. Open it with `/mod-guide`, or `/mod-guide pocock` to pick the method the Guide tab shows. |

`pocock-guide` is now `build-guide`. Install the new one and remove the old one:

```bash
claude plugin install build-guide@bldg-skills
claude plugin uninstall pocock-guide
```

The plugins with a name in the **Whose** column are other people's work, mirrored here
and named after their author so it is obvious at a glance whose thinking you are running.
Each keeps its own plugin so it can be refreshed as a unit, and whatever upstream docs
came with it live in that plugin's `upstream/` folder.

`corey-ganim` is the paid, community version of Build With AI 3.1.1 from Return My Time.
Its upstream repo no longer resolves publicly, so this mirror may be the only reachable copy.

## Other tools

Plugins are a Claude Code mechanism. For Codex, Cursor or anything else that reads a
`SKILL.md` folder, `install.sh` is the bridge:

```bash
./install.sh --list                 # every skill, as <plugin>/<skill>
./install.sh --library --link       # symlink them all into the local agent skill dirs
```

Use `--link`, not the default copy. A copy drifts from the repo; a symlink cannot.

## Layout

```text
bldg-skills/
  .claude-plugin/marketplace.json   # the marketplace: every plugin, its path and category
  plugins/<plugin>/
    .claude-plugin/plugin.json      # name, description, version
    skills/<skill>/SKILL.md         # the skills themselves
    archive/                        # non-skill files that came with the category
  library/_ARCHIVE/                 # retired skills, deliberately not published
  install.sh
```

## Notes

- **Ratio figures in `plugins/bldg-construction/skills/sow-generator/references/trade-checklists.md`
  are unverified placeholders**, converted from metric source material written for another
  market. Replace them with BLDG Estimating job history and mark them `VERIFIED`. Until
  then any output using them must be labeled `ESTIMATED -- unverified ratio`.
- `library/_ARCHIVE` holds retired skills and is not part of any plugin.
