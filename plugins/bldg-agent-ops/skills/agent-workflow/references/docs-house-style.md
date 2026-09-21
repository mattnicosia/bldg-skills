# Greppable docs house style

## Why

Agents find the right doc by grepping. The first content block must be enough to accept or reject the file without reading the whole thing.

## Required header (first 7 lines after the H1)

Immediately under `# Title`, include seven dense lines (bullets or labeled lines):

1. **Purpose**  -  one sentence, outcome-level
2. **Owner**  -  person or persona (e.g. security-review persona, Matt, Kron)
3. **Status**  -  draft | active | deprecated + date
4. **When to update**  -  what code/docs events force a rewrite
5. **Canonical paths**  -  code or config this document owns
6. **Traps**  -  the one or two gotchas that burn sessions
7. **Related**  -  AGENTS.md route keys or sibling docs

Example:

```markdown
# SMS Intake Agent

- Purpose: Drive multi-turn smoke-damage SMS intake to a structured lead.
- Owner: Capture lead-ops persona
- Status: active (2026-07-12)
- When to update: prompt changes, required fields change, Twilio handler contract changes
- Canonical paths: `supabase/functions/sms-handler/` · `web/lib/leads.ts`
- Traps: MMS size limits; status transitions capturing → new are strict
- Related: AGENTS.md "intake brain" · BRIEF.md §3 · docs/DATA-MODEL.md
```

## Body rules

- Short sections. Prefer tables for inventories.
- Link commands that agents can run copy-paste.
- No em-dashes or en-dashes in public-facing copy. Hyphens, periods, colons OK.
- Mark deprecated docs at the top of the header with a redirect path.
