---
name: speed-to-lead
description: >
  End-to-end inbound lead response workflow for any business. Intakes a raw
  inquiry, classifies fit (qualified, maybe, unqualified, spam/vendor, urgent
  existing client), drafts a human-approved first response, builds a
  Day 0/1/3/7/14 follow-up sequence, and writes a CRM-ready lead record.
  Draft-first by default. Never auto-sends. Use whenever the user says
  'speed to lead', 'new lead came in', 'lead came in', 'respond to this lead',
  'inbound inquiry', 'first response to this lead', 'draft a lead response',
  'build a follow-up sequence', 'lead nurture', or pastes a raw inquiry from
  email, LinkedIn, website form, DM, etc. and wants a first reply plus
  follow-up cadence. Also triggers on 'route this lead',
  'should I take this lead', 'qualify this lead'.
---

# Speed-to-Lead Skill

End-to-end inbound lead workflow. Goal: hit your first-response SLA with a high-quality, personalized, approved draft. Never leak a lead.

> **First time using this skill?** Say "Set up the speed-to-lead skill" and Mode 0 walks you through a 10-question interview that captures your offer, proof, risk reversal, pricing rules, tone, cadence, CRM destination, and routing rules. The skill needs this config before it can draft anything.

---

## Setup state check

Before running any mode that drafts a response, verify:

- `references/config.md` exists in the skill folder (your saved offer, proof bank, risk reversal language, pricing rules, tone, cadence, CRM destination, routing rules).

If `references/config.md` is missing when Modes 1/2/3 are invoked, stop and offer to run Mode 0 first. Do not draft anything without the config — drafting blind risks inventing pricing/availability/guarantees, which violates the guardrails.

---

## Modes

### Mode 0: First-time setup
Trigger phrases: "set up the speed-to-lead skill", "configure speed to lead", "first time using this", "run the speed-to-lead setup"
→ Read `references/setup_mode.md` and follow it. Produces `references/config.md` and `references/lead-routing-rules.md`.

### Mode 1: Process a new lead (end-to-end)
Trigger phrases: "new lead came in", "speed to lead", "respond to this lead", "inbound inquiry", "process this lead", or paste a raw inquiry with intent to reply
→ Run the full workflow below (Steps 1–8). Produces three per-lead files in `SALES/`:
- `SALES/lead-response.md` — Day 0 first response draft
- `SALES/follow-up-sequence.md` — Day 1/3/7/14 drafts
- `SALES/lead-record.md` — CRM-ready row

### Mode 2: Just draft the first response
Trigger phrases: "draft a first response", "first reply to this lead", "just the first response"
→ Run Steps 1–4 only. Produces `SALES/lead-response.md`.

### Mode 3: Just build the follow-up sequence
Trigger phrases: "build a follow-up sequence", "lead nurture", "lead cadence", "follow-up drafts for this lead"
→ Run Steps 1–3 and Step 5 only. Produces `SALES/follow-up-sequence.md`.

### Mode 4: Routing/qualification check only
Trigger phrases: "route this lead", "should I take this lead", "qualify this lead", "is this lead worth my time"
→ Run Steps 1–2 only. Returns a routing decision with rationale. Does not draft.

---

## Workflow (Mode 1, full pipeline)

Execute in order. Pause only where noted for approval.

### Step 1: Intake raw inquiry and metadata

Confirm or extract from the conversation:
- Prospect name, company, role, contact (email/LinkedIn/phone)
- Raw inquiry (full message body, verbatim)
- Source channel (email, LinkedIn DM, website form, referral, DM, etc.)
- Timestamp (when did it arrive — drives SLA countdown)
- Product/service interest (if stated)
- Urgency/timeline (if stated)
- Known budget or company size (if stated)
- Prior notes (any history with this person)
- Desired CTA (if the user already has one in mind; otherwise default to the offer's primary CTA from config)

If any **critical** field is missing (raw inquiry text, source, name or contact), ask one targeted question to get it. Do not invent metadata. Missing-but-not-critical fields go into the "Missing info" warning in Step 7.

### Step 2: Classify fit

Read `references/lead-routing-rules.md`. Apply the rules to classify the lead into exactly one bucket:

- **Qualified** — matches ICP signals, has budget/authority/intent/timing fit, primary action is to book the calendar/next step CTA
- **Maybe** — partial fit; needs one qualifying question before booking
- **Unqualified** — clear ICP mismatch, but a real human; politely redirect or decline
- **Spam/vendor** — obvious vendor pitch, mass outreach, irrelevant solicitation; archive, no reply by default
- **Urgent existing client** — known client with an active issue; route to human immediately, do not draft a sales-style response

State the classification in the output with a 1–2 sentence rationale tied to specific signals in the inquiry. If unsure between two buckets, choose the more conservative one and flag it for human review.

**Hard routing overrides** (always send to human, never auto-draft):
- Anger, complaint, refund request, legal language ("breach," "lawyer," "refund," "demand"), or support issue
- Mentions of regulated/sensitive topics outside the offer scope
- Anything tagged "urgent existing client"

### Step 3: Extract need in prospect language

Write a 1–2 sentence summary of what the prospect actually said they want, using **their words** wherever possible. Quote 1–3 short phrases verbatim. This summary becomes the personalization anchor for Step 4.

### Step 4: Draft first response (Day 0)

Follow `references/lead_response_template.md`. The draft must include all five elements:

1. **Fast acknowledgment** — opens by acknowledging the inquiry within the first sentence. No "Hope you're well." No throat-clearing.
2. **Specific personalization** — references a verbatim detail from their inquiry (a phrase, a number, a stated goal, a tool they mentioned). Generic openers fail.
3. **Relevant proof** — pulls one approved proof element from `references/config.md` (case-study line, named result, named client, metric). **Only approved proof — never invent.**
4. **Tactical empathy if concern is visible** — if the inquiry shows hesitation, confusion, or a specific worry, name it back ("Sounds like the part that's tripping you up is X — that's the same thing most [type of buyer] hit.") Skip if no concern is visible.
5. **One clear CTA** — exactly one. Default is the booking link from config. Never a menu. Never two CTAs.

**Constraints:**
- Word count: 80–180 words for cold/cool leads; can stretch to 250 for warm/referred leads with complex inquiries.
- Tone: matches `tone` field in config.
- No invented availability, pricing, delivery promises, guarantees, or results.
- Only pricing/discounts/guarantees from config's "approved without escalation" list.
- If a discount, custom price, or non-standard guarantee feels needed: flag it, do not include it, and tell the user "this one needs your call on pricing/guarantee before sending."
- Sign-off matches config's `sign_off` field.

### Step 5: Create follow-up sequence

Build a 5-touch cadence in `references/follow_up_sequence_template.md` format. Default cadence (override if config specifies different intervals):

- **Day 0** — first response (already drafted in Step 4; reference it, don't re-draft)
- **Day 1** — short bump. 1–3 sentences. Re-surface the inquiry. Same CTA. "Bumping this in case my note got buried — still happy to [CTA] this week."
- **Day 3** — proof/value share. Drop one piece of approved value: a relevant case study line, a short framework, a useful resource (only if approved in config), or a specific result that mirrors their stated need. 4–8 sentences. Same CTA.
- **Day 7** — no-oriented check-in. Frame as a low-pressure off-ramp: "Is this still on your radar, or did the timing shift?" or "Totally fine if this isn't a priority right now — just want to know whether to keep this thread open." Permission-to-close framing. Same CTA, softer.
- **Day 14** — close loop. Final touch. Polite, no guilt. "Closing the loop on this — if the timing changes, my door's open. [link]." Archive the lead after this if no reply.

**Sequence rules:**
- Each touch references something specific from the prior inquiry, not generic.
- Same primary CTA across all 5 touches unless config says to rotate.
- No fake scarcity ("only 2 spots left this month") unless it's literally true and pre-approved.
- No guilt tactics ("I'm surprised I haven't heard back").
- All dates are calendar dates calculated from the Day 0 timestamp captured in Step 1. Show actual dates next to each touch.

### Step 6: Save/update CRM record

Build the lead record in `references/lead_record_template.md` format. Default fields:

- Prospect: name, company, role, contact
- Source: channel, timestamp, referrer (if any)
- Classification (from Step 2) and rationale
- Need (from Step 3, in prospect's language)
- Offer: which product/service interest
- Status: New / First-response-drafted / Awaiting-approval / Sent / Replied / Booked / Disqualified / Closed-loop
- Next action + due date (tied to sequence)
- Owner (default per config)
- Notes (anything that affects how to follow up: tone preference, hesitation signal, budget hint)

Save to `SALES/lead-record.md`. If the config's `crm_destination` field specifies an external CRM (HubSpot, Notion, Airtable, Pipedrive, etc.), **also format the record as a one-liner row** matching that CRM's field structure and include it in the file under a "CRM row" heading so it can be pasted directly.

If the user has connected the relevant MCP (Notion, Gmail, etc.), offer to write the row directly after approval. Never write to the CRM before Step 7 approval.

### Step 7: Show rationale and missing-info warnings

Print to chat, in this order:

1. **Classification** (one line) + rationale (1–2 sentences)
2. **Need summary** (1–2 sentences in prospect's words)
3. **First response draft** (the full Day 0 response, ready to copy)
4. **Follow-up sequence preview** (just touch headers + first line of each — full drafts are in the file)
5. **Lead record summary** (prospect, classification, next action + date)
6. **Missing info warnings** — any required-but-absent field, any signal that the draft is making a soft assumption, any item that needs the user's call before sending
7. **Files written** — links to all SALES/ files created

### Step 8: Require approval before send

End the chat output with this exact line:

> "Want me to send/save anything? Reply: approve send (just Day 0), approve all (Day 0 + queue sequence), edit (tell me what to change), or hold (don't send anything)."

**Never send before explicit approval.** Even with approval, only act on tools you have access to:
- If Gmail MCP is connected: offer to create a draft (not send).
- If a CRM MCP is connected: offer to write the lead record row.
- If neither: deliver the files and let the user paste manually.

After approval, log the send action (timestamp, channel) into `SALES/lead-record.md` and update status to Sent.

---

## Validation checklist (run before printing output)

```
□ Step 1: Raw inquiry, source, timestamp, name, contact present (or flagged missing)
□ Step 2: Classification stated with rationale tied to specific signals
□ Step 2: Hard routing overrides checked (anger/legal/refund/support → human)
□ Step 3: Need summary uses prospect's verbatim words
□ Step 4: First response references a specific inquiry detail (quote a phrase)
□ Step 4: Exactly one primary CTA in first response
□ Step 4: Proof/metric/guarantee pulled from config.md, not invented
□ Step 4: No unapproved discount, custom price, delivery promise, or guarantee
□ Step 4: Tone matches config
□ Step 5: Day 0/1/3/7/14 all drafted with actual calendar dates
□ Step 5: Same primary CTA across sequence (unless config rotates)
□ Step 5: No fake scarcity, no guilt tactics
□ Step 6: Lead record saved with all default fields
□ Step 7: Missing info warnings explicit, not buried
□ Step 8: Approval prompt shown; nothing sent or written to external CRM yet
```

If any item fails, fix before printing. Do not print partial output.

---

## Guardrails (always on)

- **Draft-first by default.** Nothing sends without explicit approval.
- **Never invent availability, pricing, delivery promises, results, or guarantees.** Pull from config; if absent, flag it.
- **Route angry/legal/refund/support issues to human.** Do not draft a sales reply over a complaint.
- **No fake scarcity, no guilt tactics, no manipulative urgency.**
- **No discounts not pre-approved in config.**
- **No claims about results that aren't in the approved proof bank.**
- **If the inquiry is ambiguous, ask one clarifying question before drafting — don't guess at intent.**

---

## File map

| Path | Purpose |
|---|---|
| `SKILL.md` | This file. Workflow and modes. |
| `references/setup_mode.md` | Mode 0 conversational walkthrough (the 10 questions) |
| `references/config.md` | Generated by Mode 0. Your offer/proof/pricing/tone/cadence/CRM/routing. Source-of-truth for all drafts. |
| `references/lead-routing-rules.md` | Generated by Mode 0. Classification rules + hard overrides. |
| `references/lead_response_template.md` | Day 0 first-response anatomy |
| `references/follow_up_sequence_template.md` | Day 1/3/7/14 touch templates |
| `references/lead_record_template.md` | CRM row schema + default fields |
| `references/config.md.example` | Sample populated config (placeholders) — hand-edit instead of running Mode 0 |
| `references/lead-routing-rules.md.example` | Sample routing rules (placeholders) |
| `examples/example_qualified_lead.md` | Worked example end-to-end |

---

## Example trigger phrases

- "New lead came in — [paste inquiry]"
- "Speed to lead"
- "Respond to this inquiry: [paste]"
- "Draft a first reply to this lead"
- "Build a follow-up sequence for this lead"
- "Should I take this lead? [paste]"
- "Inbound inquiry — handle this"

---

## Notes

- **One CTA rule is non-negotiable.** Two CTAs cuts response rate. If you're tempted to add a second, you're hedging — pick one.
- **Personalization must be a verbatim quote or specific detail.** "Loved your inquiry" doesn't count. "You mentioned you're stuck on [exact phrase]" counts.
- **The Day 7 no-oriented check-in is the highest-leverage touch.** Permission-to-close framing consistently outperforms "just bumping this" on the 7-day touch. Don't skip it.
- **Config drift = bad drafts.** If your offer, pricing, proof, or guarantee changes, re-run Mode 0 (or hand-edit `references/config.md`) before drafting more leads.
