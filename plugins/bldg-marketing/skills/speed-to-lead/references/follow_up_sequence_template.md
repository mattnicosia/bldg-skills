# Follow-Up Sequence Template

5-touch cadence: Day 0, Day 1, Day 3, Day 7, Day 14. Each touch has a distinct job. Don't blur them.

The sequence runs only if Day 0 has been sent and the prospect has not responded or booked. The instant they reply or book, **stop the sequence** — manual mode takes over.

---

## File output format

Save the full sequence to `SALES/follow-up-sequence.md` using this structure:

```markdown
# Follow-Up Sequence: [Prospect Name] - [Company]

Day 0 sent: [date + channel]
Primary CTA: [from config]
Status: [Awaiting reply / Replied / Booked / Closed]

---

## Day 1 ([calendar date]) - Bump

[draft]

---

## Day 3 ([calendar date]) - Proof / Value share

[draft]

---

## Day 7 ([calendar date]) - No-oriented check-in

[draft]

---

## Day 14 ([calendar date]) - Close loop

[draft]
```

---

## Day 1: Short bump

**Job:** Resurface the inquiry. Acknowledge that inboxes are noisy. Same CTA, low friction.

**Length:** 1–3 sentences. Anything longer is overplaying it.

**Voice:** Casual, peer-level. Sounds like a quick check-in, not a sales nudge.

**Template:**
```
Bumping this in case my note got buried.

Same offer — [one-sentence summary of the CTA from Day 0]. Want me to send a couple times, or want to grab one off the calendar?

[BOOKING_LINK]

- [First Name]
```

**Variants:**
- If they asked a question on Day 0 that you answered: "Just making sure my reply landed — happy to keep going on [topic]."
- If Day 0 included a specific time offer: "Still got [day/time] open if it works for you."

**Don't:**
- Apologize for "bothering" them.
- Add new proof or new framing — that's Day 3's job.
- Switch CTAs.

---

## Day 3: Proof / Value share

**Job:** Re-engage with one specific, useful thing tied to the need they articulated on Day 0. The asset does the work; the message just hands it over.

**Length:** 4–8 sentences. Slightly longer than Day 1 because there's an asset to frame.

**Voice:** Generous, not promotional. Sounds like "thought of you, here's something useful."

**Template:**
```
One more thought on [their specific situation from Day 0].

[One sentence that ties their situation to the asset.] Here's a [case study / framework / short Loom / specific result] from a [similar client/context]: [link or paraphrase].

[One sentence on why it matters for their specific case.]

If the call still makes sense, here's the link: [BOOKING_LINK]. Otherwise no worries.

- [First Name]
```

**Asset rules:**
- Pull only from `references/config.md` approved proof bank or approved resources.
- Match the asset to their stated need. Don't send a sales-focused case study to someone asking about ops.
- If no approved asset maps to their need, **skip Day 3 entirely** — better to keep cadence light than to send weak material.

**Don't:**
- Send a generic "here's our case studies page."
- Pivot to a different offer.
- Manufacture urgency.

---

## Day 7: No-oriented check-in

**Job:** Give them a permission-to-close off-ramp. This is the highest-converting touch in the sequence — counterintuitively, framing as "is this still a fit?" or "is the timing wrong?" earns more replies than "still interested?"

**Length:** 2–4 sentences. Short, low-pressure.

**Voice:** Genuinely curious, not passive-aggressive. The vibe is "I want to know whether to keep this thread open, not pressure you."

**Template (pick one):**

Variant A — "Is this still on the radar?"
```
Wanted to check in one more time.

Is [their specific goal/situation] still on your radar, or did the timing shift?

Totally fine either way — just trying to figure out whether to keep this thread open.

- [First Name]
```

Variant B — "Have you given up on this?"
```
Last note on this one.

Have you given up on [their specific goal], or is it just that this isn't the right moment?

If the timing's off, all good — and if it's still on the table, [BOOKING_LINK].

- [First Name]
```

Variant C — "Should I close the loop?"
```
Hey [name], one more time.

Should I close the loop on this, or is it still something you're working through?

If it's the latter, here's the link: [BOOKING_LINK]. If not, no worries — appreciate the original note.

- [First Name]
```

**Why this works:**
- Permission-to-close framing flips the power dynamic. The prospect either says "no, still interested" (which re-engages them) or "yes, close it" (which gives you data and frees the slot).
- "Is this still a fit?" and "did the timing shift?" trigger replies because they sound like real questions, not sales nudges.
- The off-ramp removes guilt, which is what kills late-sequence replies.

**Don't:**
- Use guilt language ("I'm surprised I haven't heard back," "thought I'd hear from you by now").
- Manufacture urgency ("closing my calendar Friday").
- Re-pitch the offer. The Day 7 is not about the offer; it's about whether to continue the thread.

---

## Day 14: Close loop

**Job:** Final touch. Polite, no guilt, leaves the door open. After this, archive the lead (or move to a long-term nurture list if config specifies).

**Length:** 2–4 sentences.

**Voice:** Friendly, definitive. No follow-up implied.

**Template:**
```
Closing the loop on this one.

If timing changes down the line, my door's open — just reply to any of these threads or grab a slot: [BOOKING_LINK].

Appreciate the original note. Good luck with [their specific goal/situation].

- [First Name]
```

**Variants:**
- If they're a referral or someone you want to keep warm: add one sentence — "I'll add you to my [newsletter/list] so you've got something useful landing once a week — feel free to unsubscribe anytime: [NEWSLETTER_LINK]." (Only if `config.md` has this pre-approved.)
- If they hit a hard disqualifier mid-sequence: skip the Day 14 and send a polite redirect instead.

**Don't:**
- Sign off with passive-aggression ("I guess this isn't a priority").
- Demand a final answer.
- Promise to follow up again later.

---

## Stop conditions

The sequence pauses immediately on any of these signals:
- Prospect replies (any reply, even "not interested" — manual mode takes over)
- Prospect books on the calendar
- Prospect unsubscribes (if email)
- Hard escalate signal triggered (anger, legal, refund) → route to human immediately
- The user manually stops the thread

When the sequence stops, update `SALES/lead-record.md` status field accordingly.

---

## Common failure modes

- **Same message four times.** Each touch has a distinct job. If Day 1 and Day 3 read interchangeably, redo Day 3.
- **Switching CTAs mid-sequence.** Default is same CTA across all touches. Switching reads as confusion.
- **Skipping Day 7.** Day 7 is the conversion touch. Skipping it because "it feels passive-aggressive" is a misread — it's the most polite touch in the sequence.
- **Adding scarcity that isn't real.** "Closing my calendar Friday" only works if the calendar actually closes Friday. Faking it kills trust.
- **Generic Day 3 asset.** Sending a "here's our whole case studies page" link is lazy. Pick one specific thing tied to their need or skip Day 3.
- **Continuing after a reply.** The sequence is for non-responders. Once they reply, kill the queue.
