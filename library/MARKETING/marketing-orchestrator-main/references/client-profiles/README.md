# Client Profiles

Each client gets a saved profile file named `[client-slug].md` (e.g., `acme-plumbing.md`).

The orchestrator checks this directory at the start of every session. If a matching profile
exists, it loads it silently and skips intake questions already answered by the profile.

---

## Profile Template

When saving a new client profile, use this structure:

```markdown
# [Client Name]

## Business
- Industry: 
- What they sell / do: 
- Website (if known): 
- Key differentiator: 

## Target Audience
- Primary ICP: (role, company size, pain point)
- Secondary ICP (if any): 

## Brand Voice
- Tone attributes: (e.g., direct, warm, expert)
- Words / phrases to use: 
- Words / phrases to avoid: 
- Example copy they love: 

## Goals
- Primary marketing goal: (awareness / leads / conversion / retention)
- Active campaigns or channels: 

## History
- Deliverables produced (date, type, notes):
```

---

## How to Save a Profile

After completing any intake, the orchestrator automatically offers to save the profile:
"Want me to save [Client Name]'s profile so you don't have to repeat this next time?"

If yes, save the file here as `[client-slug].md`.

## How to Update a Profile

At the end of any session, if new information surfaced (new ICP, new campaign, updated voice),
append it to the relevant section and add a note under History.
