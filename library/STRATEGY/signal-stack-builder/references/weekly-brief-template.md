# Weekly Brief — Template

This is the template the skill personalizes for the user's market when it generates `INTELLIGENCE/weekly-brief-template.md`. The personalized version is what scheduled `/schedule` tasks fill in each week.

The skill reads this file at workflow step 7 to produce the personalized version.

## Template structure (markdown to fill in)

```markdown
# Weekly Brief — {{YYYY-MM-DD}}

**Market focus:** {{user's market/category}}
**Week-over-week delta:** {{count of new high-priority signals vs. last week}}
**Brief reviewer:** {{user's named reviewer from interview Q10}}

## Customer signals

- **{{source name}}** — [link]({{url}})
  - Summary: {{one-line summary of what was said/posted}}
  - So what: {{decision implication — feeds into Marketing/Sales/Operations}}

- (3–5 bullets total in a typical week)

## Competitor moves

- **{{competitor}} — {{move type}}** — [link]({{url}})
  - Summary: {{what they shipped/changed/announced}}
  - So what: {{competitive response considerations}}

- (1–3 bullets per typical week)

## Market shifts

- **{{event}}** — [link]({{url}})
  - Summary: {{regulatory / category / economic shift}}
  - So what: {{which system this affects + how}}

- (0–3 bullets per typical week)

## Internal pulse

Summary of this week's first-party signal: {{theme synthesis from sales calls, support tickets, churn interviews, etc.}}

- {{theme 1}}: {{what's new vs. last week}}
- {{theme 2}}: {{...}}

## This week's three decisions

A brief without decisions is a newsletter. Force three concrete decisions you (or your team) will act on this week:

1. **{{decision}}** — {{owner}} — driven by signals: {{which bullets above}}
2. **{{decision}}** — {{owner}} — driven by signals: {{...}}
3. **{{decision}}** — {{owner}} — driven by signals: {{...}}

If you can't fill in three, the brief is too thin or you're already on top of the signal. Note which.

## Source health flags

Any sources that returned empty, errored, or felt off this week. Feeds the monthly verification pass.

- {{source}}: {{flag}} ({{action}})
- (often empty in a healthy week)

---

**Stack reference:** [INTELLIGENCE/signal-stack.md](../signal-stack.md)
**Next brief:** {{YYYY-MM-DD + 7}}
```

## Personalization rules (applied by the skill at step 7)

When the skill personalizes this template into `INTELLIGENCE/weekly-brief-template.md`, it should:

1. Replace `{{user's market/category}}` with the user's answer to interview Q1.
2. Replace `{{user's named reviewer}}` with interview Q10.
3. Reorder the four signal sections (customer signals / competitor moves / market shifts / internal pulse) to match the user's signal-priority answer from interview Q5 (most-important first).
4. Drop sections the user said they don't care about. If interview Q5 didn't include "market news" as a priority, the personalized template can omit "Market shifts" entirely.
5. Inline a one-line note at the top of each section indicating the user's signal types and high-priority rubric for that section (helps future-fired scheduled tasks know what to filter for).

## Validation rule

The skill's validation pass (workflow step 9) requires the personalized template to include the **"This week's three decisions"** section verbatim. If the personalization step drops it, validation fails and the skill must restore it.

This is the forcing function — without it, the brief is information without decisions.
