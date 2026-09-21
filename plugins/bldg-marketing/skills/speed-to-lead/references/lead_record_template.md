# Lead Record Template

Schema for `SALES/lead-record.md` and the CRM row that gets written to the destination in `references/config.md`.

---

## Default fields (always populated)

| Field | Source | Notes |
|---|---|---|
| Prospect name | Step 1 intake | Required |
| Company | Step 1 intake | Required if known |
| Role | Step 1 intake | Optional |
| Contact (email/LinkedIn/phone) | Step 1 intake | Required — at least one |
| Source channel | Step 1 intake | Required (email, LinkedIn DM, website form, referral, etc.) |
| Source timestamp | Step 1 intake | Required — drives SLA + sequence dates |
| Referrer (if any) | Step 1 intake | Optional |
| Product/service interest | Step 1 intake or inferred | If inferred, mark as `[inferred]` |
| Urgency/timeline | Step 1 intake | Optional |
| Known budget/size | Step 1 intake | Optional, do not invent |
| Prior notes | Step 1 intake | Any history with this person |
| Classification | Step 2 | Qualified / Maybe / Unqualified / Spam-Vendor / Urgent-Existing-Client |
| Classification rationale | Step 2 | 1–2 sentence rationale tied to signals |
| Need summary | Step 3 | Prospect's language, verbatim phrases where possible |
| Desired CTA | From config or Step 1 | The primary CTA being used |
| Status | Workflow state | New / First-response-drafted / Awaiting-approval / Sent / Replied / Booked / Disqualified / Closed-loop |
| Next action | Sequence | "Send Day 1 bump" / "Send Day 3 proof" / etc. |
| Next action due date | Sequence | Calendar date |
| Owner | From config | Who owns the lead |
| Notes | Free text | Tone preference, hesitation signals, budget hints, anything that affects follow-up |
| Created | Auto | Timestamp the record was created |
| Last updated | Auto | Timestamp of last status change |

---

## File format: `SALES/lead-record.md`

```markdown
# Lead Record: [Prospect Name] - [Company]

**Created:** [YYYY-MM-DD HH:MM]
**Last updated:** [YYYY-MM-DD HH:MM]
**Status:** [New / First-response-drafted / Awaiting-approval / Sent / Replied / Booked / Disqualified / Closed-loop]
**Owner:** [from config]

## Prospect
- Name: [name]
- Company: [company]
- Role: [role]
- Contact: [email / LinkedIn / phone]

## Source
- Channel: [email / LinkedIn DM / website form / referral / etc.]
- Timestamp: [YYYY-MM-DD HH:MM TZ]
- Referrer: [name if any, else "—"]

## Inquiry
- Product/service interest: [from inquiry or inferred — mark inferred]
- Urgency/timeline: [from inquiry, or "not stated"]
- Known budget/size: [from inquiry, or "not stated"]
- Prior notes: [any history]

### Raw inquiry
> [verbatim raw inquiry, indented as a quote]

## Classification
- Bucket: [Qualified / Maybe / Unqualified / Spam-Vendor / Urgent-Existing-Client]
- Rationale: [1–2 sentences tied to specific signals]

## Need (in prospect's language)
[1–2 sentence summary with verbatim phrases quoted]

## CTA
- Primary CTA: [verbatim]
- Link/path: [URL]

## Sequence schedule
- Day 0 ([date]): [Sent / Drafted / Pending approval]
- Day 1 ([date]): [Pending]
- Day 3 ([date]): [Pending]
- Day 7 ([date]): [Pending]
- Day 14 ([date]): [Pending]

## Notes
- [tone preference, hesitation signals, budget hints, anything else]

## Audit log
- [YYYY-MM-DD HH:MM] Record created
- [YYYY-MM-DD HH:MM] Day 0 drafted
- [YYYY-MM-DD HH:MM] Day 0 sent via [channel]
- [add entries as state changes]

---

## CRM row (for paste into external destination)

[If config.crm_destination is set to an external CRM, format the row here in that CRM's field structure. See the CRM-specific formats below.]
```

---

## CRM-specific row formats

If `references/config.md` specifies one of these destinations, also format a row in the matching layout below and include it under the `## CRM row` heading in `SALES/lead-record.md`.

### Notion database row (markdown table)

```markdown
| Name | Company | Email | Source | Classification | Status | Next action | Due date | Owner |
|---|---|---|---|---|---|---|---|---|
| [name] | [company] | [email] | [source] | [bucket] | [status] | [next action] | [date] | [owner] |
```

If Notion MCP is connected, after approval the skill can write this row directly to the configured database. Pull database ID from `references/config.md`.

### Airtable row (CSV)

```csv
Name,Company,Email,Source,Classification,Status,Next action,Due date,Owner
"[name]","[company]","[email]","[source]","[bucket]","[status]","[next action]","[date]","[owner]"
```

### HubSpot contact note (plain text)

```
Contact: [name] ([email]) at [company]
Source: [source] on [timestamp]
Classification: [bucket] — [rationale]
Need: [need summary]
Status: [status]
Next action: [next action] on [date]
```

### Pipedrive deal note

```
Deal title: [company] - [product/service interest]
Person: [name] ([email])
Source: [source] / [timestamp]
Stage: [maps to status]
Note: [classification + rationale + need summary]
Next activity: [next action] / [date]
```

### Google Sheet row (CSV)

```csv
Date,Name,Company,Email,Source,Classification,Status,Next action,Due date,Owner,Notes
"[date]","[name]","[company]","[email]","[source]","[bucket]","[status]","[next action]","[due]","[owner]","[notes]"
```

### Gmail label (no CRM row, just labels)

If `crm_destination = gmail_labels`, apply the following labels to the original inquiry thread:
- `Leads/[Classification]` (e.g. `Leads/Qualified`)
- `Leads/[Status]` (e.g. `Leads/Awaiting-approval`)
- `Leads/Source/[Channel]` (e.g. `Leads/Source/LinkedIn`)

Skill does not auto-apply labels; offer to do so after approval if Gmail MCP is connected.

---

## Status state machine

Allowed transitions:

```
New
 → First-response-drafted
 → Awaiting-approval
 → Sent
   → Replied → [manual mode]
   → Booked → [manual mode]
   → [no response] → Day 1 sent → Day 3 sent → Day 7 sent → Day 14 sent → Closed-loop
 → Disqualified (from any state if hard override triggers)
```

When status changes, append an entry to the audit log with timestamp.

---

## Sensitive fields

Never write to the record:
- Full credit card / payment details
- Anything the prospect marked confidential
- Salary or PII the prospect didn't volunteer

If the raw inquiry contains any of the above, quote only what's relevant and redact the rest with `[redacted by speed-to-lead]`.
