# Cloud Sync Auditor — Claude Skill

Deep, systematic auditor for cloud sync data loss, race conditions, major bugs, and inefficiencies.

Built for offline-first React + Supabase + IndexedDB stacks (especially construction estimating tools like NOVATerra).

## Installation (Claude Code / Claude Cowork / Claude.ai)

### Option 1 — Claude Code (recommended)
```bash
# From your home directory or project
mkdir -p ~/.claude/skills
unzip cloud-sync-auditor-claude-skill.zip -d ~/.claude/skills/
# or copy the folder:
# cp -r cloud-sync-auditor ~/.claude/skills/
```

Then restart Claude Code or start a new session. The skill will auto-trigger on relevant requests, or you can invoke it with:

```
/cloud-sync-auditor
```

or just say:
- "Run the cloud sync auditor"
- "Find all data loss risks and race conditions in the sync layer"
- "Audit for cloudsync bugs"

### Option 2 — Claude Projects / Claude.ai custom skills
Upload the entire `cloud-sync-auditor` folder (or the zip) as a skill/project knowledge, or paste the SKILL.md content into a Project custom instruction and attach the references.

### Option 3 — Manual
Just keep the folder somewhere and tell Claude: "Use the cloud-sync-auditor skill from this path: ..."

## What's Included
- `SKILL.md` — main instructions + progressive disclosure
- `references/` — deep knowledge (data-loss patterns, races, checklist, Supabase+IDB gotchas)
- `scripts/find-sync-anti-patterns.sh` — quick rg scanner (run it first)

## Best Model + Effort
- **Claude Opus 4.8 (or latest Opus) at High or Max / xhigh / Ultra Code effort**
- This skill was designed to pair perfectly with high-effort reasoning on distributed systems.

Happy hunting. No more silent data loss.
