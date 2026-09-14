# Scheduled Tasks Guide

Common patterns, prompt templates, and cron reference for setting up recurring automations. Read this before running the Scheduled Tasks capability.

---

## What Scheduled Tasks Do

Scheduled tasks run automatically on a recurring schedule (or on-demand). Each task is a self-contained prompt that Claude executes in a fresh session — no conversation history, no prior context. This means the prompt must include everything Claude needs to complete the task.

Tasks are created with the `create_scheduled_task` tool and managed with `list_scheduled_tasks` and `update_scheduled_task`.

**Important:** The Claude Desktop app must be open for scheduled tasks to run. If the app is closed, tasks won't execute until it's reopened.

## Cron Expression Quick Reference

Cron expressions use 5 fields: `minute hour dayOfMonth month dayOfWeek`

All times are in the **user's local timezone** — do NOT convert to UTC.

| Schedule | Cron Expression |
|----------|----------------|
| Every day at 8:00 AM | `0 8 * * *` |
| Every day at 9:00 AM | `0 9 * * *` |
| Weekdays at 8:00 AM | `0 8 * * 1-5` |
| Weekdays at 9:00 AM | `0 9 * * 1-5` |
| Every Monday at 8:00 AM | `0 8 * * 1` |
| Every Friday at 4:00 PM | `0 16 * * 5` |
| Every Sunday at 6:00 PM | `0 18 * * 0` |
| First of every month at 9:00 AM | `0 9 1 * *` |
| First Monday of every quarter | `0 9 1 1,4,7,10 *` |
| Every 2 hours during work hours | `0 9,11,13,15,17 * * 1-5` |

Day of week: 0=Sunday, 1=Monday, ..., 6=Saturday

## Common Task Patterns by Role

### Universal — Works for Everyone

**Morning Briefing**
```
taskId: morning-briefing
description: Daily summary of what needs attention today
schedule: Weekdays at 8 AM (0 8 * * 1-5)
prompt: |
  Check all connected platforms and give me a morning briefing:
  1. Check my calendar for today's meetings and prep notes
  2. Check my email for anything urgent or requiring a response
  3. Check my task manager for items due today or overdue
  4. Summarize everything in a concise briefing organized by urgency
  Save the briefing as a markdown file called morning-briefing-[today's date].md
```

**Weekly Review**
```
taskId: weekly-review
description: End-of-week summary of accomplishments and next week prep
schedule: Fridays at 4 PM (0 16 * * 5)
prompt: |
  Generate a weekly review:
  1. Check my calendar for this week's meetings and summarize key events
  2. Check my task manager for tasks completed this week
  3. Identify any tasks that are overdue or were pushed
  4. List priorities for next week based on upcoming deadlines
  Save as weekly-review-[date].md
```

### Content Creators / Marketers

**Content Calendar Check**
```
taskId: content-calendar
description: Weekly content planning reminder with platform-specific ideas
schedule: Sundays at 6 PM (0 18 * * 0)
prompt: |
  Help me plan next week's content:
  1. Review what I posted this past week (check connected social platforms if available)
  2. Suggest 5 content ideas for next week based on trending topics in my niche
  3. For each idea, suggest which platform it's best suited for
  4. Create a simple content calendar for the week
  Save as content-plan-[date].md
```

### E-Commerce / Amazon Sellers

**Inventory Check**
```
taskId: inventory-check
description: Weekly inventory and listing health review
schedule: Mondays at 9 AM (0 9 * * 1)
prompt: |
  Run a weekly Amazon business check:
  1. Review any shared inventory reports or spreadsheets in my connected Drive
  2. Flag any products that might need attention (low stock, declining performance)
  3. Suggest 3 action items for this week to improve listings or operations
  Save as amazon-weekly-[date].md
```

### Consultants / Agencies

**Client Follow-Up Digest**
```
taskId: client-followup
description: Daily check for client communications needing response
schedule: Weekdays at 9 AM (0 9 * * 1-5)
prompt: |
  Check my connected communication platforms (email, Slack, etc.) for:
  1. Client messages that need a response
  2. Action items mentioned in recent conversations
  3. Upcoming client meetings that need prep
  Organize by client and urgency. Save as client-followup-[date].md
```

**Monthly Client Report Prep**
```
taskId: monthly-report-prep
description: Monthly reminder to prepare client deliverables
schedule: Last weekday of the month (0 9 28 * *)
prompt: |
  It's time to prep monthly client reports. Help me:
  1. List all active clients from my recent documents and communications
  2. For each client, summarize key activities this month
  3. Create a template report outline I can fill in with specific metrics
  Save as monthly-report-template-[date].md
```

## Maintenance — Keep Your Setup Current

### Context File Review

```
taskId: context-review
description: Quarterly reminder to review and refresh context files
schedule: First Monday of every quarter (0 9 1 1,4,7,10 *)
prompt: |
  It's time to review my Cowork context files. Please:
  1. Read all files in my CONTEXT/ folder
  2. For each file, summarize what it currently says
  3. Ask me if anything has changed since the last review:
     - New businesses, projects, or roles?
     - Changed tools or platforms?
     - Updated brand voice or communication style?
     - New working preferences or rules?
  4. If I report changes, update the relevant file(s)
  5. After updating, check if Global Instructions need
     to be regenerated to match
  Save a brief review log as context-review-[date].md
```

### VOC Refresh (Every 90 days)

**What it does:** Reads the existing `CONTEXT/voc.md`, pulls 10-20 fresh buyer quotes from the last 90 days of connected sources (calls, tickets, reviews, DMs), categorizes them into the existing VOC sections, and merges into the file. Updates `Last updated:`.

**Why 90 days:** Your buyer's language shifts faster than you think. Words that landed in Q1 ("burnout", "overwhelmed") may have been replaced by Q3 ("can't keep up", "drowning"). The agent's marketing and sales output is only as fresh as the Voice of Customer data underneath it.

```
taskId: voc-refresh
description: Quarterly refresh of Voice of Customer file with fresh buyer quotes
schedule: First Monday of every quarter at 9 AM (0 9 1 1,4,7,10 *)
prompt: |
  Refresh my VOC file. Read CONTEXT/voc.md to see what's already there.
  Then pull 10-20 fresh buyer quotes from the last 90 days from my
  connected sources (Gmail, Drive, etc.). Categorize each quote into
  the right VOC section (pain language, desired outcomes, objections,
  etc.). Merge into voc.md without duplicating. Update Last updated.
  Show me the diff before saving.
```

### Plugin Ecosystem Check

```
taskId: plugin-check
description: Monthly check for new plugins relevant to your workflow
schedule: First Monday of every month (0 9 1 * 1)
prompt: |
  Check for new Cowork plugins and skills relevant to my work:
  1. Read my CONTEXT/about-me.md to understand my role and needs
  2. Search the plugin marketplace for keywords matching my
     business, role, and daily activities
  3. Compare results against my currently installed skills
  4. If there are relevant new plugins I don't have, summarize
     what they do and why they might help
  5. Save findings as plugin-check-[date].md
  Only flag genuinely relevant additions -- not everything new.
```

## Skill Scheduling — Put Your Skills on Autopilot

Once you've built and validated a custom skill, you can schedule it to run automatically. This is the true delegation moment — the skill runs without you.

**Example: Schedule a custom skill**
```
taskId: [skill-name]-auto
description: Automated run of [skill name]
schedule: [appropriate cron expression]
prompt: |
  Run my [skill name] skill. Here's the context:
  - Read my CONTEXT/ files for identity and voice
  - Check PROJECTS/[relevant project] for current state
  - Execute the skill workflow
  - Save output to OUTPUTS/[project]/
  - Summarize what was produced
```

**Example: Weekly content drafting skill**
```
taskId: linkedin-drafts-auto
description: Draft 3 LinkedIn posts every Monday morning
schedule: Mondays at 7 AM (0 7 * * 1)
prompt: |
  Run my LinkedIn content skill to draft 3 posts for this week:
  - Read CONTEXT/ for my voice and audience
  - Check PROJECTS/content/ for recent topics and what I've already posted
  - Draft 3 LinkedIn posts using different frameworks (story, insight, contrarian)
  - Save all drafts to OUTPUTS/content/linkedin-drafts-[date].md
  - Include a one-line summary of each draft's hook and angle
```

**Tips:**
- Start with a manual run to verify the skill works as expected
- Schedule conservatively at first (weekly, not daily)
- For skills that send messages or publish content, use "draft only" mode in the schedule until you trust the output
- Review scheduled skill outputs periodically
- The prompt must be fully self-contained — include all context the skill needs since scheduled tasks run in fresh sessions

## Writing Effective Task Prompts

### Rules for Self-Contained Prompts

Every scheduled task prompt must be fully self-contained because it runs in a fresh session with no conversation history.

**Include:**
- Clear objective statement (what to accomplish)
- Specific steps to execute
- Which connected platforms to check
- Where to save output (file name and format)
- Success criteria (what "done" looks like)

**Never include:**
- References to "this conversation" or "what we discussed"
- Assumptions about prior context
- Vague instructions like "check the usual places"

### Template

```
[Clear 1-sentence objective]

Steps:
1. [Specific action with named tool/platform]
2. [Specific action]
3. [Specific action]

Output:
- Format: [markdown/docx/etc.]
- Filename: [name-pattern-with-date.md]
- Save to: [location]
```

## Tips for the Onboarding Flow

- **Start with one task.** Don't overwhelm with 5 scheduled tasks on day one. One well-configured morning briefing is more valuable than five half-baked automations.
- **Match to connected tools.** Only suggest tasks that leverage platforms the user has actually connected. A morning briefing that checks Slack is useless if Slack isn't connected.
- **Use plain language for scheduling.** Say "every weekday at 8 AM" and handle the cron expression behind the scenes. Most users don't need to know what `0 8 * * 1-5` means.
- **Get explicit approval.** Always present the full task prompt and schedule before creating. Use AskUserQuestion with the proposed task details.
- **Explain the constraint.** Mention that the Claude Desktop app needs to be open for scheduled tasks to run.
- **Always propose the context review task.** This keeps the user's setup accurate over time. Frame it as low-effort: "Every 3 months, Claude checks your context files and asks if anything changed."
- **Ask about skill scheduling.** During the interview, include: "Do you have any skills or workflows you want to run on a schedule?" This plants the seed for the autopilot pattern.
