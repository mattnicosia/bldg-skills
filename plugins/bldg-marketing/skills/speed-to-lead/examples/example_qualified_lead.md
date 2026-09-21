# Worked Example: Qualified Lead, End-to-End

This is what a full Mode 1 run looks like. Use it as a reference when the workflow gets ambiguous.

The example below assumes a fictional fractional operations consultant named **Jordan Reyes** who helps 10–50 person creative agencies fix tool sprawl. All names, businesses, dates, and proof points are fictional and used only to illustrate the workflow shape.

---

## Assumed config values for this example

- Owner / sign-off: `Jordan Reyes` / `- Jordan`
- Primary CTA: "Book a 20-min fit call: https://example.com/jordan/intro"
- Approved proof: "9-person agency engagement (anonymized): consolidated client context across 4 tools in 11 days, account managers stopped pinging founders for context"
- Pricing: "engagements start at $7,500 for a 30-day implementation"
- Risk reversal: "Free 20-min fit call, no pitch"
- Tone: warm, direct, peer-level, no corporate filler, no exclamation marks

---

## Input (what gets pasted)

```
New lead came in — handle it:

From: Maya Patel <maya@kestrelagency.example>
Channel: Website contact form
Received: [date] 09:12 ET

Body:
Hey - found you through a referral. I run a 14-person creative agency
and we're hemorrhaging time because our account managers keep
re-asking founders the same questions about brand guidelines, voice,
past projects, etc. Everything lives in Drive + Notion + Slack + a few
old emails. We've tried two AI tools and they didn't stick.

What does engaging with you look like? Budget is flexible if we can get
this dialed in this quarter.

Maya
Founder/CEO, Kestrel Agency
```

---

## Workflow output (printed in chat)

### Classification

**Qualified.** Signals: 14-person agency (in stated ICP range), specific operational pain named (account managers re-asking founders for client context), stated quarter timeline, explicit budget flexibility, and direct ask for next step ("what does engaging look like"). Two-strike signal: she's already tried two AI tools that didn't stick, which means she's qualified AND wary — the draft should address that explicitly.

### Need (in her language)

She's "hemorrhaging time" because account managers "keep re-asking founders the same questions" about client context. Wants to "get this dialed in this quarter." Already burned by two AI tools that "didn't stick."

### First response draft (Day 0)

```
Got your note about Kestrel.

You said your account managers keep re-asking founders the same
questions because client context is spread across Drive, Notion,
Slack, and old emails. That's the exact bottleneck I worked on with
a 9-person agency earlier this year — we got their per-client context
into a single layer in 11 days and the account managers stopped
pinging founders entirely.

The reason most AI tools don't stick: they get bolted on top of the
mess instead of replacing the mess. The fix is mostly architecture,
not new tools.

Engagements look like a 30-day implementation, $7,500 starting, scope
depending on team size and tool sprawl. Free 20-min fit call first so
I can see your stack and tell you whether this is actually the right
move.

Easiest next step: grab a slot. https://example.com/jordan/intro

- Jordan
```

**Word count:** 168 words. Within Day 0 range for warm/qualified.

**Element check:**
- Acknowledgment ("Got your note about Kestrel."): yes, first 5 words
- Personalization (quoted "keep re-asking founders the same questions"): yes
- Proof (anonymized 9-person agency, 11-day implementation, specific outcome): yes, from approved bank
- Tactical empathy (addresses the "two AI tools that didn't stick" worry without naming it as a problem): yes
- One CTA (book the fit call): yes, single link, no menu
- Pricing (starts-at range, pulled from approved pricing rules): yes, no custom quote invented
- Sign-off (matches config): yes

### Follow-up sequence preview

| Touch | Date | Job | First line |
|---|---|---|---|
| Day 1 | [+1 day] | Bump | "Bumping this in case my note got buried." |
| Day 3 | [+3 days] | Proof | "One more thought on the account-managers-pinging-founders problem." |
| Day 7 | [+7 days] | No-oriented check-in | "Is getting Kestrel's client context dialed in this quarter still on your radar?" |
| Day 14 | [+14 days] | Close loop | "Closing the loop on this one." |

Full drafts saved to `SALES/follow-up-sequence.md`.

### Lead record summary

- Prospect: Maya Patel, Founder/CEO, Kestrel Agency
- Source: Website contact form, [timestamp]
- Classification: Qualified
- Status: Awaiting approval
- Next action: Send Day 0 response
- Owner: Jordan Reyes
- Notes: She's burned by two prior AI tools that didn't stick. Lead with architecture-not-tools framing in the call.

Full record saved to `SALES/lead-record.md`.

### Missing info warnings

- Annual revenue not stated — inferred as small-mid agency range based on team size (14 people, creative agency). Not used in pricing.
- Specific tools beyond Drive/Notion/Slack not named — will probe on the fit call.

### Files written

- `SALES/lead-response.md`
- `SALES/follow-up-sequence.md`
- `SALES/lead-record.md`

### Approval prompt

> Want me to send/save anything? Reply: **approve send** (just Day 0), **approve all** (Day 0 + queue sequence), **edit** (tell me what to change), or **hold** (don't send anything).

---

## Failure modes this example avoids

- Generic opener ("Hope this email finds you well.") — replaced with verbatim acknowledgment.
- Made-up proof — every claim is in the approved proof bank.
- Custom pricing — uses the approved starts-at range, doesn't quote her a custom number.
- Two CTAs ("book a call OR reply with questions") — single CTA, single link.
- Ignoring the "two AI tools didn't stick" signal — explicitly addressed without naming her past tools.
- Fake scarcity ("only 2 slots this week") — none.
- Auto-sending — output ends with explicit approval prompt.

---

## What this looks like across the sequence

### Day 1 bump (sample)

```
Bumping this in case my note got buried.

Same offer — 20-min fit call to see Kestrel's stack and tell you
whether the implementation sprint is actually the right move.

https://example.com/jordan/intro

- Jordan
```

### Day 3 proof/value share (sample)

```
One more thought on the account-managers-pinging-founders problem.

Most agencies I work with assume they need a new tool to fix client
context — what actually works is replacing the layer underneath,
not adding another tool on top.

The 9-person agency I mentioned had the same Drive + Notion + Slack
sprawl. Eleven days to single-layer it. Their account managers
stopped pinging founders entirely.

If the fit call still makes sense, here's the link:
https://example.com/jordan/intro

- Jordan
```

### Day 7 no-oriented check-in (sample)

```
Wanted to check in one more time.

Is getting Kestrel's client context dialed in this quarter still
on your radar, or did the timing shift?

Totally fine either way — just trying to figure out whether to keep
this thread open.

- Jordan
```

### Day 14 close loop (sample)

```
Closing the loop on this one.

If timing changes down the line, my door's open — grab a slot
whenever it makes sense: https://example.com/jordan/intro

Appreciate the original note. Good luck getting Kestrel's context
layer dialed in.

- Jordan
```
