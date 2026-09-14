# BLDG Skills

Private-capable skill library for Grok, Claude Code, and any agent that loads [agentskills.io](https://agentskills.io) `SKILL.md` packages.

This repo is the source of truth. Machines install from it. Do not treat `~/.grok/skills` or `~/.claude/skills` as the canonical copy.

## Layout

```text
bldg-skills/
  README.md
  install.sh                 # install curated flat skills from skills/
  scripts/validate-skill.sh
  .github/workflows/validate-skills.yml
  skills/                    # curated, installable via ./install.sh
    project-level-up/        # full app audit on a model drop
    site-level-up/           # site/landing pass gated by model strengths
    cloud-sync-auditor/      # sync / data-loss
  library/                   # full Dropbox SKILLS mirror by category
    AGENT OPERATIONS/
    CODING/
    CONSTRUCTION/
    CREATIVE/
    DISTILLS/
    DOCUMENTS/
    MAKER SCHOOL/
    MARKETING/
    SEO/
    SOCIAL/
    STRATEGY/
    WEBSITE DESIGN/
    _ADMIN/
    _ARCHIVE/
    _INBOX/
    _SHARED/
```

- `skills/` — curated flat skills. Each folder is one skill; directory name must match `name:` in `SKILL.md`. `./install.sh` only installs from here.
- `library/` — faithful mirror of Dropbox `BLDG/SKILLS` by category (199 `SKILL.md` files across 16 top-level category folders). Not mass-linked by install.sh yet.

## Install on a machine

```bash
git clone git@github.com:mattnicosia/bldg-skills.git
cd bldg-skills
./install.sh --link
```

`--link` symlinks each skill into the local agent dirs so edits in the git repo are live.

```bash
./install.sh            # copy instead of symlink
./install.sh --list     # show skills in this repo
./install.sh --only project-level-up
```

Default destinations (created if missing):

- `~/.grok/skills` — Grok / xAI
- `/home/workdir/.grok/skills` — Grok cloud sessions
- `~/.claude/skills` — Claude Code, if that folder exists or `--claude` is passed

Grok can also pull a single skill after the repo is public or you have a token:

```bash
# from a Grok session with skill-installer loaded
install-skill.sh --repo mattnicosia/bldg-skills --path skills/project-level-up
```

## Add a skill

```bash
# from this repo
bash scripts/validate-skill.sh skills/your-skill-name
git add skills/your-skill-name
git commit -m "Add your-skill-name"
git push
./install.sh --link --only your-skill-name
```

Move an existing local skill in with:

```bash
cp -R ~/.grok/skills/cloud-sync-auditor ./skills/cloud-sync-auditor
bash scripts/validate-skill.sh skills/cloud-sync-auditor
```

## Skills

- `project-level-up` — full app audit on a model drop (code, routing, UI, UX).
- `site-level-up` — landing/product site only. Builds a capability delta first. Changes only axes where the new model is actually up and the current page is weak.
- `cloud-sync-auditor` — IndexedDB / Supabase / realtime data-loss review.

Say the skill name in a new agent session. Do not paste the file.

## Remote

Canonical repo: [github.com/mattnicosia/bldg-skills](https://github.com/mattnicosia/bldg-skills)

Keep it **private** unless a skill contains zero product internals. `references/novaterra.md` is product-specific.

```bash
git remote add origin git@github.com:mattnicosia/bldg-skills.git
git branch -M main
git push -u origin main
```

## Rules

- One skill = one directory = one `SKILL.md`
- `description` is an unquoted YAML scalar. No `: `, no `<`, no `>`
- Validate before push
- Update `skills/project-level-up/references/model-registry.md` on every model drop, before running audits
