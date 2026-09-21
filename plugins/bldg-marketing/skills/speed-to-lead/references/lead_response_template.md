# Day 0 First Response Template

The Day 0 response is the highest-leverage touch in the entire sequence. It either earns the next conversation or quietly loses it. The five required elements below are non-negotiable.

---

## Required structure (in order)

### 1. Fast acknowledgment (first 1 sentence)

Open by acknowledging the inquiry. No "Hope you're well." No "Thanks for reaching out!" (corporate). The opener should sound like a human who actually read the message.

Good:
- "Got your note about [specific topic they mentioned]."
- "Saw your message — [their specific situation] is exactly the kind of thing I work on most weeks."
- "Quick reply because [specific reason from their inquiry]."

Bad:
- "Thanks so much for reaching out!"
- "I hope this email finds you well."
- "Hi [Name], I appreciate your interest in our services."

### 2. Specific personalization (1–2 sentences)

Quote a phrase from their inquiry verbatim or reference a specific detail. This proves you read it and aren't running a template.

Format: `You mentioned [verbatim quote / specific detail]. [Brief reaction or expansion that shows you understood the actual problem.]`

If they didn't give specifics, name the implicit situation: `Sounds like you're at the point where [specific scenario their inquiry implies].`

### 3. Relevant proof (1–2 sentences, optional but recommended)

Pull **one** approved proof element from `references/config.md`. One — not two, not a list. Just the most relevant single point.

Format: `For context: [client/context]: [specific result or quote].`

If no proof in the bank maps cleanly to their need, **skip this element entirely.** Better to skip than to force a weak proof.

### 4. Tactical empathy (1–2 sentences, only if concern is visible)

If their inquiry shows hesitation, confusion, or a specific worry, name it back without minimizing it. Use Voss-style labels: "Sounds like..." or "It seems like..." rather than "I know how you feel."

Examples:
- "Sounds like the part that's tripping you up is figuring out where to start without burning a month on tools that won't stick."
- "It seems like you've already burned time on [X] and you're not looking for another solution that takes 6 weeks to set up."

Skip this element if the inquiry shows no hesitation. Forcing empathy when none is needed sounds like sales theater.

### 5. One clear CTA (final 1–2 sentences)

Exactly one. The primary CTA from `references/config.md`. Never a menu.

Default format: `Easiest next step: [primary CTA verbatim + booking link]. Want me to send a couple times that work for me, or do you prefer to grab one off the calendar?`

Or for a single-link CTA: `[Primary CTA verbatim]: [link]. Grab whatever works.`

**Bad** (multi-CTA — always wrong):
- "You can book a call, reply with questions, or check out our website."
- "Let me know if you want to chat, or if you'd prefer I send some materials first."

### Sign-off

Per `references/config.md`. Example: `- [First Name]`

---

## Length targets

- Cold inbound, simple inquiry: 80–120 words
- Cool inbound, some context: 120–180 words
- Warm/referred inbound, complex inquiry: up to 250 words

Anything over 250 words is too long for a Day 0. Cut.

---

## Tone constraints

Pull from `references/config.md` `tone` section. Common defaults the user might choose:
- Warm but direct. Peer-level, not vendor-level.
- No corporate filler ("touch base," "circle back," "leverage," "synergy").
- No exclamation marks unless something is actually exciting.
- No emoji unless the inquiry used emoji.
- Contractions OK. Sentence fragments OK if they punch.
- Don't hedge ("I think this might possibly..."). Direct or skip the sentence.

If config defines different tone constraints, follow config — these are just common starting points.

---

## Worked example

**Inquiry (raw):**
> "Hi - found your site through a referral. We're a 12-person agency and we're drowning in client context that lives in 4 different tools. Curious if you do consulting or if this is something I can DIY. Budget would be flexible if the ROI is there."

**Assumed config values for this example:**
- Approved proof: "9-person client engagement: consolidated context across tools in 11 days, eliminated repeat internal questions"
- Pricing: "engagements start at $X — flagged for user to fill in"
- Risk reversal: "free 20-minute fit call, no pitch"
- CTA: "Book a 20-min fit call: [BOOKING_LINK]"
- Sign-off: `- [First Name]`

**Day 0 response draft:**

```
Got your note about the context-across-tools problem.

You said you're drowning in client context across 4 tools — that's the exact bottleneck I worked on with a 9-person engagement earlier this year; we got their per-client context dialed into a single layer in 11 days and their account managers stopped pinging founders for context.

DIY is doable if you've got someone internal who'll own the buildout. If not, consulting works.

Easiest next step: book a 20-min fit call so I can see your stack and tell you which path actually fits. [BOOKING_LINK]

- [First Name]
```

**Why it works:**
- Acknowledgment: first 6 words.
- Personalization: verbatim quote ("drowning in client context across 4 tools").
- Proof: one specific result (anonymized, named timeline, named outcome).
- Tactical empathy: implicit — answers the DIY-vs-consulting question they actually asked.
- One CTA: book the call. Single link. No menu.
- Length: ~100 words. Within Day 0 range.

---

## Common failure modes

- **Generic personalization.** "Loved your message" or "Great question" is not personalization. Quote them or skip.
- **Two CTAs.** "Book a call OR reply with questions" cuts conversion. Pick one.
- **Invented proof.** If the proof bank doesn't have a clean match, don't fabricate one. Skip the proof step.
- **Long preamble.** Anything before the acknowledgment is wasted words.
- **Asking for too much.** Day 0 asks for the next step, not the deal. Save the qualifying questions for after they book or for the Maybe-bucket variant.
- **Tone mismatch.** If their inquiry is casual, don't reply formal. If their inquiry is formal, don't reply with "yo."

---

## Maybe-bucket variant

When a lead is classified Maybe (Step 2), replace the CTA with one specific qualifying question instead of a booking link. Example:

```
Got your note about [topic].

Before I send a calendar link — quick question: [one specific qualifying question that determines fit, e.g. "how many people on your team would be using this?" or "what's your timeline on starting?"].

That answer changes whether the right next step is a quick call or just a pointer to a resource.

- [First Name]
```

The qualifying question replaces the booking CTA. Once they answer, re-classify and draft a new touch.
