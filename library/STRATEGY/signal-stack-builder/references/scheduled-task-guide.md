# Scheduled Task Guide

Two copy-paste-ready `/schedule` prompts. Run each once in Cowork. The skill outputs both as instructions to you at the end of the workflow (step 8).

> **Important:** Cowork has no public scheduling API. The `/schedule` slash command is a built-in Anthropic skill that takes natural language and creates the scheduled task internally. You — the user — invoke `/schedule` yourself; this skill does NOT call it programmatically.

## Prompt 1 — Weekly intelligence brief

Open Cowork. Type `/schedule`. When prompted, paste this verbatim:

```
Every Monday at 8am, run a weekly intelligence brief.

Read `INTELLIGENCE/signal-stack.md` to know which sources to monitor and what counts as a high-priority signal.

Read `INTELLIGENCE/weekly-brief-template.md` for the format the brief must follow.

For each source in the stack, surface this week's most decision-relevant signals. Apply the high-priority rubric to flag what matters most. Generate 3–5 customer signals, 1–3 competitor moves, 0–3 market shifts, and an internal pulse synthesis.

The brief MUST include a "This week's three decisions" section with three concrete decisions, owners, and the signal bullets that drove each. If you cannot fill in three decisions honestly, note that and explain why.

Save the completed brief to `INTELLIGENCE/weekly-briefs/YYYY-MM-DD.md` using today's date.

After saving, post a one-line summary to chat: "Weekly brief saved at INTELLIGENCE/weekly-briefs/<date>.md — top decision: <first decision>."

Do NOT publish, send, or share the brief externally. Output is for review only.
```

Confirm cadence as **weekly** when Cowork's `/schedule` modal asks. Pick **Monday at 8am local time**.

## Prompt 2 — Monthly source verification

Open Cowork. Type `/schedule`. When prompted, paste this verbatim:

```
On the first Monday of each month at 9am, verify my signal stack sources.

Read `INTELLIGENCE/signal-stack.md` to get the full list of sources.

Read the verification checklist at the path your skill installation provides (look for `verification-checklist.md` inside the signal-stack-builder skill's references folder).

For each source, run all 5 per-source checks (URL resolves, recent content, same publisher, quality unchanged, still distinct). For the stack as a whole, run the 5 stack-level checks (4-category coverage, dead sources, new VOC venues, silent competitor sources, total source count ≤25).

Append one row per source to `INTELLIGENCE/source-verification-log.md` using the table format from the checklist. Append a stack-level summary row after the per-source rows.

Surface any sources you marked "remove", "replace", or "pause" in a one-line summary to chat: "Source verification done — N sources kept, M removed, K paused. See INTELLIGENCE/source-verification-log.md."

Do NOT modify `INTELLIGENCE/signal-stack.md` automatically. Surface what would change so I can review and update the stack manually.
```

Confirm cadence as **monthly** (Cowork supports cron-style "first Monday of each month" via the `/schedule` skill's natural-language parser).

## Cowork scheduling caveats (read once)

These come from official Anthropic docs (snapshot 2026-05-06):

- **Desktop must be open and laptop must be awake.** "Scheduled tasks only run while your computer is awake and the Claude Desktop app is open." Skipped runs auto-execute when the app reopens.
- **Fresh session, no memory.** "Each scheduled task runs in a fresh session with no conversation history — prompts must be fully self-contained." That's why the prompts above are explicit about what to read and where to save.
- **Windows tool-injection bug.** Known issue ([anthropics/claude-code#29022](https://github.com/anthropics/claude-code/issues/29022)) where `create_scheduled_task` isn't always injected into the Cowork session on Windows. If `/schedule` doesn't see the tool, restart Cowork and try again.
- **No cloud execution for Cowork.** Routines (Claude Code only, launched April 2026) run cloud-side; Cowork scheduled tasks remain device-local. Plan around this — don't expect briefs to fire when your laptop is closed.

## Editing scheduled tasks

After the tasks are scheduled, manage them via the **Scheduled** sidebar entry in Claude Desktop:

- Pause a task without deleting it (handy when traveling)
- Edit the prompt (e.g., to point at a renamed file or new template)
- Change the cadence
- View execution history

## Troubleshooting

- **Brief comes back empty or thin.** Re-run `signal-stack-builder` (the skill that generated this stack) to refresh sources, or check `INTELLIGENCE/source-verification-log.md` for failing sources.
- **Tone of brief is off.** Update `CONTEXT/voc.md` with fresh customer language, then let the next scheduled brief pick up the change. The brief reads VOC indirectly through the source rubric.
- **Brief saves but post-summary doesn't appear in chat.** Check the Scheduled sidebar's execution history for that run — there may be a runtime error visible there.
- **Wrong day/time.** Edit the scheduled task in the Scheduled sidebar; the natural-language cadence is editable.
