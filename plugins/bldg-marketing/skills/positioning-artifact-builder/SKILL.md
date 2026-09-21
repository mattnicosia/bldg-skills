---
name: positioning-artifact-builder
description: "Interviews the user into a one-page positioning artifact and converts Voice-of-Customer (VOC) into a specific ICP, buyer Jobs-To-Be-Done (JTBD), an ownable idea, supporting subclaims, and explicit angle boundaries. Use whenever the user says 'build my positioning', 'positioning artifact', 'help me position my offer', 'ownable idea', 'POV doc', 'turn VOC into positioning', 'I need a positioning doc', 'sharpen my positioning', 'what's my angle', 'who do I serve', 'help me figure out what to say', 'distill my VOC', 'run the positioning workflow', '/positioning', or pastes a VOC dump and wants positioning out of it. Also trigger when the user is clearly working on messaging foundations (landing page, sales page, email sequence, pitch) and lacks a documented ICP, JTBD, or ownable idea. Requires CONTEXT/voc.md. Output is saved to CONTEXT/positioning.md and becomes the upstream source-of-truth for all downstream content."
---

# Positioning Artifact Builder

A guided interview that turns raw Voice-of-Customer (VOC) plus the user's own founder POV into a one-page positioning artifact: a specific ICP paragraph, a buyer-language JTBD, an ownable idea (scored against six criteria), three supporting subclaims, and an explicit avoid list.

The artifact is upstream of everything else. Once it exists at `CONTEXT/positioning.md`, every other content skill (newsletter, landing page, podcast, ads) can pull from it instead of reinventing the angle each time.

---

## What this skill produces

A single markdown file at `CONTEXT/positioning.md` containing:

1. **ICP** — a specific paragraph describing the best-fit buyer (not a category like "small business owners")
2. **Buyer JTBD** — written in the buyer's own language, pulled from VOC where possible
3. **Ownable Idea** — one sentence, scored against six criteria
4. **Three Supporting Subclaims** — proof points that hold the ownable idea up
5. **Five+ VOC phrases** — verbatim pulls preserved as raw material for downstream copy
6. **Angle Boundaries & Avoid List** — what this positioning is NOT, and who it is NOT for

---

## Prerequisites

Before starting the interview, check for these files in order:

1. **REQUIRED**: `CONTEXT/voc.md` — Voice-of-Customer raw material. If missing, stop and tell the user:
   > "I need `CONTEXT/voc.md` before I can build positioning. That file is the raw material — verbatim phrases from real buyers (sales calls, support tickets, reviews, DMs, survey responses). Without it, the ownable idea won't be grounded in buyer language and the artifact will be generic. Can you put one together and come back? Even a rough dump of 20-30 quotes is enough to start."

2. **PREFERRED**: `CONTEXT/about-me.md` — the user's identity, POV, and history. If missing, note it and proceed, but probe harder during the interview for founder POV.

3. **PREFERRED**: An offer or service description (in chat, in a file, or pasted). Ask if not present.

4. **PREFERRED**: At least one real customer/problem example. Ask if not present.

---

## Workflow

Execute in order. Pause where explicitly noted.

### Step 1: Read the VOC first

Before asking any questions, fully read `CONTEXT/voc.md`. This is non-negotiable. The whole point of this artifact is that it is grounded in real buyer language, not in the user's projection of what buyers think. Reading VOC first means:

- Interview questions land sharper because you can echo back actual buyer phrases
- The JTBD draft is in buyer words from the start, not paraphrased
- The ownable idea candidates are tested against what buyers actually say

Also read `CONTEXT/about-me.md` if it exists, plus any offer/service description.

While reading VOC, internally collect:
- 8-12 candidate phrases for pain
- 8-12 candidate phrases for desired outcome
- Recurring objections, misunderstandings, and "what they already tried"
- Any phrase a buyer used that surprised you (these are often the gold)

### Step 2: Run the interview

Ask the questions one at a time, in this order. Do not batch them. After each answer, briefly reflect what you heard back so the user can correct course before the next question.

If the user has already answered a question elsewhere in the conversation (or in `about-me.md`), skip it and confirm: "I'm reading from your about-me that [X]. Still true?"

**Q1.** Who do you serve when the work goes best? Picture one real client. What do they do, what stage are they at, what makes them a fit?

**Q2.** What do they hire you to make easier, faster, safer, or more profitable? Use their words if you have them.

**Q3.** What have they already tried? What's on their graveyard of failed attempts before you?

**Q4.** What do they misunderstand about solving this problem? Where is the market wrong?

**Q5.** What do competitors say that you disagree with? Name names if you can.

**Q6.** What do you believe that your market needs to hear, even if it costs you some customers?

**Q7.** From the VOC, which phrase best captures the pain? (Offer 3-5 candidate phrases from VOC for the user to pick from or override.)

**Q8.** From the VOC, which phrase best captures the desired outcome? (Same: offer 3-5 candidates.)

**Q9.** What proof shows your POV is true? Results, stories, named clients, case studies, screenshots, before/afters.

**Q10.** Who should you explicitly NOT write for? Who would be a bad-fit customer, even if they had money?

### Step 3: Draft the ICP paragraph

Write the ICP as a paragraph, not a bullet list. The goal is specificity. If a generic phrase like "small business owners" or "founders" or "marketers" could replace your ICP without losing meaning, you have not gone deep enough.

A good ICP paragraph names:
- Stage/size (revenue, headcount, lifecycle)
- Role/title of the buyer
- The specific situation they are currently in
- What they are actively trying to fix or build
- What disqualifies someone from this ICP

**Bad:** "Small business owners who want to grow."
**Good:** "Service-based business owners doing $500K to $5M, usually past the scrappy founder-led sales stage, who have a working offer but a team that's still bottlenecked on the founder for delivery, sales, or hiring decisions. They've tried at least one productivity system or CRM and bounced off it. They are not coaches selling coaching to coaches, and not pre-revenue."

### Step 4: Draft the JTBD in buyer words

The JTBD must sound like the buyer talking, not the seller. Pull from VOC where possible. If you find yourself writing "they want to optimize their funnel" but the VOC says "I just want to stop getting ghosted by leads", use the VOC phrasing.

JTBD format: "When [situation], I want to [motivation], so I can [desired outcome]."

Anchor each piece in a real VOC phrase if you can.

### Step 5: Generate 3 to 5 ownable idea candidates

An ownable idea is the one-sentence claim that this brand/founder owns. It is what makes someone forward your work and say "this person gets it". It is NOT a tagline. It is NOT a feature list. It is a position.

Generate 3 to 5 candidates. Each should be one sentence. Vary the angle:
- One that attacks a common misunderstanding from Q4
- One that disagrees with a competitor from Q5
- One that crystallizes the founder POV from Q6
- One that names the real underlying problem the buyer doesn't yet have words for
- One that reframes the category itself

### Step 6: Score each candidate against the six criteria

For every candidate, score True / Different / Useful / Defensible / Memorable / Yours as Pass or Fail. Show the user the table.

| Criterion | Question to ask |
|---|---|
| **True** | Can the founder defend this with evidence, story, or pattern? |
| **Different** | Would competitors actively disagree, or is this table stakes? |
| **Useful** | Does it change what the buyer does next? Does it solve something? |
| **Defensible** | Can the founder hold this position over 12 months without flinching? |
| **Memorable** | Could a buyer paraphrase it back a week later? |
| **Yours** | Is this rooted in the founder's actual lived experience, not a borrowed frame? |

A candidate must pass at least **5 of 6**, and **Different** and **Useful** are non-negotiable — if either fails, the candidate is out, regardless of the other scores. Different without Useful is a hot take. Useful without Different is a commodity.

### Step 7: Pick the strongest candidate (or let the user choose)

If one candidate clearly dominates on the scoring rubric, recommend it and explain why. If two or three are close, present them side-by-side and let the user pick. Do not pick for them in a tie — the founder has to be the one who'll defend it for 12 months.

### Step 8: Write three supporting subclaims

Subclaims are the load-bearing arguments that hold the ownable idea up. If someone challenges the ownable idea, the subclaims are what you point to. Each subclaim should:

- Be a complete sentence
- Be tied to proof (a result, a story, a named client, a pattern across customers)
- Be specific enough that it could not be lifted onto a competitor's site without rewriting

### Step 9: Write the avoid list and angle boundaries

Pull from Q10 plus anything that surfaced in the interview. The avoid list should include:

- Audiences to NOT write for
- Topics or angles that are off-brand
- Tone shifts to avoid (e.g., "no academic theory framing, no MBA jargon")
- Specific phrases or clichés that disqualify a piece of content from being on-brand

This list is what makes the positioning enforceable downstream. Without it, the ownable idea drifts within a quarter.

### Step 10: Save the artifact

Write the full artifact to `CONTEXT/positioning.md` using the template below.

### Step 11: Recommend the sanity check

After saving, tell the user:

> "Before this goes into anything customer-facing, run the ownable idea past one real best-fit buyer. Not 'do you like it' — read it to them and ask 'does this sound like you, and would it stop you mid-scroll?' If they shrug, the idea isn't ownable yet. If they say 'wait, say that again' — you have it."

---

## Output template

Save to `CONTEXT/positioning.md` using this exact structure:

```markdown
# Positioning Artifact

_Last updated: [DATE]_

## ICP

[One specific paragraph. Names stage, role, situation, what they're trying to fix, what disqualifies someone.]

## Buyer JTBD

When [situation], I want to [motivation], so I can [outcome].

Pulled from VOC: "[verbatim buyer phrase that anchors this JTBD]"

## Ownable Idea

[One sentence.]

### Scored against six criteria

- True: [Pass/Fail] — [one-line rationale]
- Different: [Pass/Fail] — [one-line rationale]
- Useful: [Pass/Fail] — [one-line rationale]
- Defensible: [Pass/Fail] — [one-line rationale]
- Memorable: [Pass/Fail] — [one-line rationale]
- Yours: [Pass/Fail] — [one-line rationale]

## Supporting Subclaims

1. [Subclaim one — tied to proof.]
2. [Subclaim two — tied to proof.]
3. [Subclaim three — tied to proof.]

## VOC Phrases (raw material for downstream copy)

- "[verbatim phrase 1]"
- "[verbatim phrase 2]"
- "[verbatim phrase 3]"
- "[verbatim phrase 4]"
- "[verbatim phrase 5]"
(Add more if rich.)

## Founder POV / Why I Believe This

[2-4 sentences of the founder's underlying belief, lifted from the interview. This is what makes the ownable idea "Yours".]

## Proof

- [Result/story 1]
- [Result/story 2]
- [Result/story 3]

## Angle Boundaries & Avoid List

**Do NOT write for:**
- [Audience to exclude 1]
- [Audience to exclude 2]

**Do NOT use these angles or framings:**
- [Off-brand angle/topic 1]
- [Off-brand angle/topic 2]
- [Cliché or phrase to avoid]

**Tone guardrails:**
- [Tone shift to avoid]
```

---

## Validation gate

Before declaring the artifact done, verify all of the following. If any fail, fix and re-check.

- [ ] **Audience is specific.** "Small business owners", "founders", "marketers", "creators" alone are disqualifying. The ICP names stage, role, situation, and what disqualifies someone.
- [ ] **JTBD sounds like buyer language.** If the JTBD could appear in a competitor's marketing deck without changes, rewrite it using a real VOC phrase.
- [ ] **Ownable idea is exactly one sentence.** Not two. Not a compound sentence held together with semicolons.
- [ ] **Ownable idea passed at least 5 of 6 criteria**, AND passed both **Different** and **Useful**. If either failed, the idea is rejected — go back to Step 5.
- [ ] **Exactly three supporting subclaims**, each tied to proof.
- [ ] **At least 5 VOC phrases included verbatim.** Not paraphrased.
- [ ] **Avoid list is present and specific.** "Avoid being too salesy" doesn't count. Name audiences, angles, phrases.

---

## Notes on running this skill well

**Don't over-direct.** The founder's POV has to come out of the founder's mouth. If you find yourself feeding them words on Q4, Q5, Q6, slow down — let them struggle for a beat. The thing they say when they're searching is usually the ownable idea.

**VOC trumps founder opinion.** When the founder's intuition conflicts with what VOC says, default to VOC. The founder is often pattern-matching off the loudest 10% of customers; VOC reveals the median.

**The ownable idea is a stance, not a feature.** "We help X do Y faster" is not ownable — anyone can say it. "Most X are solving Y wrong because Z" is ownable. Push toward the second shape.

**Avoid list does most of the long-term work.** People underrate it. The ownable idea sets direction; the avoid list prevents drift. Spend real time on Step 9.

**This artifact is meant to be revisited.** Tell the user that positioning isn't one-and-done — re-run this every 6-12 months, or anytime they pivot the offer, change the ICP, or notice that their best content is hitting differently than it used to.
