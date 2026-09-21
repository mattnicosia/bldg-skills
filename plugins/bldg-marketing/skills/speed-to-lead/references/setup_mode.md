# Mode 0: First-Time Setup (Speed-to-Lead)

Conversational walkthrough that captures everything the drafting workflow needs. Output: `references/config.md` + `references/lead-routing-rules.md`. Run this once. Re-run anytime offer, proof, pricing, or cadence changes.

---

## How to run it

Ask the 10 questions below **one at a time**, in order. Wait for an answer before moving to the next. Don't batch them. If the user skips or says "use a sensible default," use the suggested default and note it in the config so they can see what was assumed.

Tone: peer-level, fast, no preamble. This is a 10-minute task, not a workshop.

---

## The 10 questions

### Q1. Where do new leads arrive?

> "Where do new leads come in? List every channel I should be watching — email, LinkedIn DM, website form, Calendly inbound, podcast contact form, referrals, SMS, anything. I'll route from each one differently."

Capture: list of channels. For each, note whether it gets the same treatment or a different one (e.g. LinkedIn DMs get a shorter response than email).

Default if skipped: email, LinkedIn DM, website form.

---

### Q2. Target first response SLA — 5 min, 15 min, 1 hour?

> "What's your target speed-to-lead? 5 minutes (you want to win on speed alone), 15 minutes (premium-but-not-instant), or 1 hour (considered/quality-first)? This sets how aggressive the Day 0 draft is."

Capture: SLA target in minutes. Note that the skill never auto-sends regardless of SLA — SLA is a target the user hits manually after approval.

Default if skipped: 15 minutes.

---

### Q3. Main action for qualified leads?

> "When a qualified lead lands, what's the single primary CTA? Book a call on your calendar? Reply to a screening question? Fill a short form? Jump to a Loom? Pick one — the whole sequence revolves around it."

Capture: the primary CTA verbatim, plus the URL (booking link, form URL, Loom, etc.).

Default if skipped: "Book a 20-minute call: [BOOKING_LINK]".

---

### Q4. Which leads should be disqualified or routed?

> "Who shouldn't get the standard response? Give me the signals that say 'spam/vendor,' 'not ICP,' 'urgent existing client,' or 'angry/legal — escalate to me.' I'll turn these into routing rules."

Capture: explicit lists of signals per bucket. Examples:
- Spam/vendor signals: generic "we offer SEO/dev services," mass cold pitch, no personalization, bulk apollo-style sender
- Not-ICP signals: company size below or above threshold, geography, industry mismatch, pricing tier mismatch
- Urgent existing client signals: known client name in `clients.md` (if it exists), refund/billing/support keywords
- Escalate-to-human signals: anger, legal, refund, threat, regulator mention

This output populates `references/lead-routing-rules.md`.

---

### Q5. What proof can be used in a first response?

> "Give me your approved proof bank. Specific case studies, named clients I can name, specific metrics ('saved 14 hours/week,' '$87K in 90 days,' etc.), testimonials I can paraphrase. If it's not in this list, I won't use it in any draft."

Capture: bulleted proof bank. Each item formatted as: `[client/context]: [specific result or quote]`. Mark any item that can NOT be named publicly with `[anonymized]`.

If the user doesn't have a formal proof bank yet, suggest 3–5 specific results from their recent client work and ask them to confirm which are OK to cite. Never invent proof.

---

### Q6. What guarantee/pilot/audit/risk reversal is approved?

> "What risk reversal can I offer in writing without escalating to you? Money-back guarantee, free pilot, free audit, satisfaction promise — give me the exact language. If I want to offer something stronger to close a specific lead, I'll flag it for your call instead of writing it."

Capture: the exact language the user is willing to put in writing. If they have multiple tiers (e.g. "free audit" for cold leads, "30-day money-back" for paid offers), capture each with a rule for when each applies.

Default if skipped: "no risk reversal language pre-approved — flag to the user when needed."

---

### Q7. What pricing can be mentioned without approval?

> "What pricing can the draft state without your sign-off? Public list prices? Tiered ranges ('$X to $Y depending on scope')? Or nothing — every price gets flagged to you? Also: what discounts, if any, are pre-approved (e.g. annual prepay = 10% off)?"

Capture:
- Prices mentionable without approval (verbatim)
- Discounts mentionable without approval (rule + amount)
- Prices/discounts NOT mentionable — these get flagged to the user instead of written into drafts

Default if skipped: no pricing in drafts; route to call to discuss pricing.

---

### Q8. What tone should responses use?

> "What's the tone? Warm-but-direct? Peer-level? Formal? Casual-but-not-flippant? Give me 2–3 examples of how you'd open a response in your voice so I can mirror it."

Capture:
- Tone descriptors (3–5 adjectives)
- 2–3 verbatim opening lines the user would write themselves
- Sign-off (e.g. "- [First Name]")
- Voice DON'Ts (e.g. "no 'hope this finds you well,'" "no corporate hedging," "no exclamation marks unless something is actually exciting")

If a brand-voice skill or voice profile already exists in the user's setup, pull from there as the baseline and have them confirm/adjust.

---

### Q9. What follow-up cadence should run?

> "What's the follow-up cadence? Default is Day 0 first response, Day 1 bump, Day 3 proof share, Day 7 no-oriented check-in, Day 14 close-loop. Want to change any of the intervals, kill any of the touches, or extend past Day 14?"

Capture:
- Confirmed intervals (in days from Day 0)
- Any touches the user wants to kill or add
- Whether to rotate CTAs across the sequence or keep the same one (default: same)
- What "close loop" looks like (default: friendly archive note)

---

### Q10. Where should lead record and tasks be saved?

> "Where does the lead record live? Local file (`SALES/lead-record.md`), Notion database (paste the database ID or URL), Airtable, HubSpot, Pipedrive, Google Sheet, or just Gmail label? Also — where do follow-up tasks go: Notion, Asana, Things, calendar reminders, or your manual workflow?"

Capture:
- `crm_destination`: name + (URL or database ID) + field mapping if non-standard
- `task_destination`: where Day 1/3/7/14 reminders go
- If MCP is connected for the destination (Notion, Gmail, etc.), note it — the skill can offer to write directly after approval

Default if skipped: `SALES/lead-record.md` (local) + calendar reminders for follow-up dates.

---

## Output: `references/config.md`

After all 10 questions are answered, write `references/config.md` with this structure:

```markdown
# Speed-to-Lead Config

Last updated: [date]

## Lead sources
- [list from Q1]

## SLA target
- First response within: [Q2] minutes

## Primary CTA
- [Q3 verbatim] → [URL]

## Routing rules
See references/lead-routing-rules.md

## Approved proof bank
- [each Q5 proof item]

## Approved risk reversal
- [Q6 exact language]
- Escalate to user for: [any stronger guarantees]

## Pricing rules
- Mentionable without approval: [Q7]
- NOT mentionable without approval: [Q7]
- Pre-approved discounts: [Q7]

## Tone
- Descriptors: [Q8 adjectives]
- Opening examples: [Q8 verbatim openers]
- Sign-off: [Q8 sign-off]
- Voice DON'Ts: [Q8 don'ts]

## Cadence
- Day 0: [confirmed]
- Day 1: [confirmed or modified]
- Day 3: [confirmed or modified]
- Day 7: [confirmed or modified]
- Day 14: [confirmed or modified]
- CTA strategy across sequence: [same / rotate]

## CRM destination
- Where: [Q10]
- MCP connected: [yes/no, which one]
- Field mapping: [if non-standard]

## Task destination
- Where: [Q10]
```

## Output: `references/lead-routing-rules.md`

After Q4 is answered, write this file with explicit, scannable rules:

```markdown
# Lead Routing Rules

## Qualified (drafts standard response, Day 0–14 sequence)
Signals:
- [list]

## Maybe (drafts response with one qualifying question instead of CTA)
Signals:
- [list]

## Unqualified (polite decline/redirect, no sequence)
Signals:
- [list]

## Spam/vendor (archive, no reply unless overridden)
Signals:
- [list]

## Urgent existing client (route to human immediately, do not draft)
Signals:
- [list of client names from clients.md if it exists]
- Keywords: refund, billing, broken, support, urgent

## Hard escalate to human (always, no auto-draft)
Signals:
- Anger keywords: angry, frustrated, disappointed, terrible, worst, lawsuit
- Legal keywords: lawyer, attorney, breach, legal, sue
- Refund keywords: refund, money back, charge back, chargeback
- Regulator/compliance keywords: FTC, FCC, GDPR, complaint filed
```

---

## Confirmation step

After both files are written, print:

```
Setup complete. Speed-to-lead is configured.

Files written:
- references/config.md
- references/lead-routing-rules.md

Try it: paste a real past inquiry and say "speed to lead" — the workflow will draft a Day 0 response and a Day 1/3/7/14 sequence.

If anything changes (offer, pricing, proof, cadence), re-run Mode 0 or hand-edit references/config.md.
```
