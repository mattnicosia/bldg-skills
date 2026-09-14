# BLDG Skills

Private-capable skill library for Grok, Claude Code, and any agent that loads [agentskills.io](https://agentskills.io) `SKILL.md` packages.

This repo is the source of truth. Machines install from it. Do not treat `~/.grok/skills` or `~/.claude/skills` as the canonical copy.

## Layout

```text
bldg-skills/
  README.md
  install.sh                 # copy or symlink skills onto this machine
  scripts/validate-skill.sh
  .github/workflows/validate-skills.yml
  skills/
    project-level-up/        # first skill
      SKILL.md
      scripts/
      references/
```

Each folder under `skills/` is one skill. Directory name must match `name:` in `SKILL.md`.

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

## First skill

`project-level-up` — run this when a new frontier model ships. It audits one repo for stale model IDs, code leverage, UI/UX wow gaps, and capabilities the new model unlocks. It writes a review pack. It does not rewrite the product until you approve the patch queue.

## Create the GitHub repo (once)

```bash
cd bldg-skills
git remote add origin git@github.com:mattnicosia/bldg-skills.git
git branch -M main
git push -u origin main
```

If the empty repo is not created yet:

```bash
# GitHub CLI
gh repo create bldg-skills --private --source=. --remote=origin --push

# or GitHub UI: New repository → bldg-skills → private → then push
```

Keep it **private** unless a skill contains zero product internals. `references/novaterra.md` is product-specific.

## Rules

- One skill = one directory = one `SKILL.md`
- `description` is an unquoted YAML scalar. No `: `, no `<`, no `>`
- Validate before push
- Update `skills/project-level-up/references/model-registry.md` on every model drop, before running audits
