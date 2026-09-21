---
name: content-matrix
description: Build the weekly content matrix — pull from positioning, VOC, and the latest Signal Stack brief, score raw ideas against buyer pain and business priority, select the 3–5 strongest, and hand each one off to the content-draft skill as a ready-to-draft brief. Use this skill whenever the user says "plan this week's content," "weekly content plan," "build the content matrix," "what should I post this week," "content matrix," "/content-matrix," "/matrix," "/weekly-plan," or any request to decide what to publish across hub + spoke channels over the next 7 days. Also trigger when the user dumps a Signal Stack brief, a list of buyer phrases, or recent performance notes and wants a publication plan out of it — even if they don't say "matrix." If they're asking what to write or which ideas to draft this week, that's this skill. This is a PLANNING skill, not a drafting skill — it produces briefs, not finished posts, and explicitly hands those briefs to the content-draft skill for actual drafting.
---

# Content Matrix

A weekly planning skill for operators who tie distribution to buyer conversations, not vanity metrics. It turns positioning + VOC + signals into a scored shortlist of ideas, then ships each pick as a brief that the content-draft skill can pick up and draft.

## What this skill is for

The job is to answer one question every Monday: **"Given my positioning, my buyers' current language, what's happening in the market this week, and what conversations I'm trying to start — what 3 to 5 things should I publish, where, and why?"**

Everything else (drafting, hooks, copy) belongs to the content-draft skill downstream. This skill stops at the brief.

## What this skill is NOT

- Not a drafting skill. It does not write finished posts. It generates briefs.
- Not a calendar tool. It plans one week at a time, tied to a specific business priority.
- Not vanity-driven. It tracks buyer conversations, DMs, calls, qualified leads, and objections — not likes.
- Not channel-agnostic. The user has to commit to a hub channel and 1–3 spokes; otherwise the plan is decorative.

## Hard rules

1. **No draft prose.** This skill produces planning artifacts and briefs only. If the user asks for a "draft" inside this flow, tell them the next step is to run the content-draft skill on the brief they want to draft first.
2. **Every selected brief carries the fields content-draft consumes.** That handoff is the whole point of the skill. See "Brief schema" below.
3. **Positioning pillars come from `CONTEXT/positioning.md`.** Don't invent pillars. If the file lacks pillars, stop and route the user to the positioning-artifact-builder skill.
4. **At least 3 pillars must appear across the selected briefs.** Single-pillar weeks starve the other angles; the matrix exists to keep distribution balanced.
5. **At least 12 raw ideas before scoring.** Premature shortlists are how operators end up posting the same idea five different ways.

## Prerequisites

Before starting, check that these files exist and are loaded. Where they live depends on the user's setup:

- **Required:** `CONTEXT/voc.md` — buyer phrases, objections, repeat language
- **Required:** `CONTEXT/positioning.md` — ICP, JTBD, ownable idea, pillars, angle boundaries
- **Strongly preferred:** the latest Signal Stack brief (this week's market intel) — usually `CONTEXT/signal-stack/YYYY-MM-DD.md` or similar
- **Preferred:** prior performance log — `MARKETING/performance-log.md` or a Google Sheet — to see what created buyer conversations last week
- **Required from the user (verbal is fine):** the active hub channel and 1–3 spokes for the week

If a `CONTEXT/` directory isn't visible:

- If the `request_cowork_directory` tool is available, use it to ask the user to connect the workspace.
- Otherwise, ask the user for the absolute path to their workspace, or paste the contents of voc.md and positioning.md into chat.

If `voc.md` or `positioning.md` is missing or empty, do not proceed. Tell the user which file is missing and recommend running the positioning-artifact-builder skill first. The whole matrix depends on having an ownable idea and real buyer language — without those, you'll score generic ideas against vague pain and produce a generic plan.

## Inputs

Collect these from the interview (or pull them from inputs the user has already given):

- Week / date range (default: the next 7 days starting from today)
- Business priority this week (e.g., "fill the May 22 webinar," "warm up 10 accounts for the AI Audit offer")
- Offer or conversation the content should support
- Hub channel (e.g., LinkedIn, X, podcast, newsletter)
- Spoke channels (1–3)
- Publishing capacity — how many drafts the user can realistically review and ship
- Recent performance notes — what created conversations last week
- 10 target accounts/buyers to engage manually during the week
- Anything timely (proof, events, launches, customer wins) the week should ride

## Interview

Default to walking through all 10 questions. They take ~5 minutes and they are the entire input to the scoring step.

If the user pushes back ("just give me a plan"), do a Quick mode with questions 1, 2, 3, 6, 7 only — but tell them the matrix will lean on inferred answers for the rest, and ask them to confirm those inferences before scoring.

1. What is the business priority this week?
2. What offer or conversation should content support?
3. What did the latest Signal Stack brief surface? (If you have it in context, summarize the top 2–3 signals back to the user instead of asking blind.)
4. What buyer phrases or problems showed up recently? (DMs, calls, replies, lost-deal post-mortems, support tickets.)
5. Which 3 to 5 pillars should we pull from? (Default to all pillars in positioning.md unless the user wants to focus.)
6. What's the hub this week and which spokes are active?
7. How many drafts can you realistically review this week? (This sets the shortlist size — 3 minimum, 5 maximum.)
8. What posts created buyer conversations last week? (Direct reply, DM, booked call, qualified lead, objection raised — not likes.)
9. Anything timely we should ride — proof, customer wins, events, launches, news cycle?
10. Who are 10 target accounts or named buyers to engage manually this week?

Show your inferences for any answer the user skipped or punted on, before moving to scoring. The scoring step lives or dies on the buyer pain being specific and named — generic answers produce a generic week.

## Workflow

1. **Read context.** Load `CONTEXT/voc.md` and `CONTEXT/positioning.md`. If `CONTEXT/signal-stack/` exists, read the most recent file. If `MARKETING/performance-log.md` exists, read the last 14 days.
2. **Run the interview** (above).
3. **Build a pillar × format matrix.** Rows = positioning pillars. Columns = the formats available across hub + spokes (e.g., long-form LinkedIn, X article, X quote tweet, podcast episode, newsletter, video). The matrix is a thinking tool — every cell is a potential idea slot.
4. **Generate raw ideas — minimum 12.** For each pillar, brainstorm idea seeds tied to specific buyer pain (use VOC phrases verbatim) and the business priority. Don't filter yet. Stretch into formats the user uses but defaults away from — that's where most operators leak distribution.
5. **Score each idea on the 5-criterion rubric** (1–5 each, total 25):

    | Criterion | What it means | Why it matters |
    |---|---|---|
    | Buyer pain strength | Does it hit a named, repeated pain in VOC? | Generic pain → generic post. |
    | Ownable idea fit | Does it reinforce the positioning's ownable idea / a named pillar? | Off-pillar posts confuse the brand. |
    | Angle clarity | Is the angle (POV, story, framework, teardown, list, contrarian, lesson) crisp enough to write a hook for? | Fuzzy angle → drafting stalls. |
    | Proof availability | Do we have a story, screenshot, data point, or example ready? | No proof → "tips" content nobody saves. |
    | Business relevance | Does this directly serve the week's business priority / offer? | Off-priority content is decorative. |

6. **Select the top 3 to 5 by score**, with two override rules:
    - At least 3 distinct pillars must be represented across the picks.
    - At least one pick must directly tee up the offer / CTA from the business priority.

7. **Convert each selected idea into a brief** using the schema below. Each brief is the handoff artifact — the user (or Claude) runs the content-draft skill on it to produce the actual draft.

8. **Build the hub/spoke distribution plan.** For each brief, name the hub channel, the spoke repurposes, and the order they ship in. Group the week into "publishing days" so the user sees the full cadence.

9. **Build the engagement loop.** List the 10 target accounts/buyers and the manual action against each (comment on a recent post, send a thoughtful DM tied to the content theme, voice memo, reply to a post they made about a buyer pain). This is the half of distribution most operators skip.

10. **Save the matrix to `MARKETING/content-matrix.md`.** If the file already exists for an earlier week, append below a `---` divider with the new week's date header — don't overwrite history. Performance tracking compounds when you can look back.

## Brief schema (the content-draft handoff)

Each selected brief must include every field below. The fields marked **[content-draft input]** are consumed verbatim by the content-draft skill — don't drop them or rename them, or the handoff breaks.

```
### Brief [N]: [short working title]

- **Pillar:** [from positioning.md]
- **Buyer pain:** "[VOC phrase, in buyer's words]" [content-draft input]
- **Topic / source signal:** [the signal or topic this brief is built on] [content-draft input]
- **Platform / format:** [LinkedIn long-form / X article / podcast / newsletter / etc.] [content-draft input]
- **Target pillar:** [the positioning pillar this reinforces] [content-draft input]
- **Angle:** [POV / story / framework / teardown / list / contrarian / lesson learned] [content-draft input]
- **Promise to reader:** [what they'll believe or do after reading]
- **Proof / story / example:** [the specific receipt — customer name, screenshot, data point, lived experience] [content-draft input]
- **CTA:** [DM me, comment a word, book a call, reply to email — or "none"] [content-draft input]
- **Length / tone constraints:** [short punchy / mid / long-form deep dive; tone if non-default] [content-draft input]
- **Business relevance:** [which offer or conversation it supports]
- **Score:** [X/25, with the 5 sub-scores]
- **Next step:** Run `/content-draft` on this brief.
```

The "Next step" line is intentional — it tells the user (and any agent reading the matrix later) exactly how to move this brief into drafting.

## Output structure

Save to `MARKETING/content-matrix.md`. Use this exact structure so the file stays scannable across weeks:

```
# Content Matrix — Week of [YYYY-MM-DD]

## Business priority
[one line]

## Offer / conversation supported
[one line]

## Hub + spokes
- Hub: [channel]
- Spokes: [channel, channel, channel]

## Pillars in play this week
- [pillar 1]
- [pillar 2]
- [pillar 3+]

## Signals driving this week's plan
[bullets from the Signal Stack brief or the user's input]

## Pillar × format matrix
[markdown table or bulleted matrix — pillars as rows, formats as columns, idea seeds in cells]

## Raw idea pool (minimum 12)
1. [idea] — pillar: [X], pain: "[VOC phrase]"
2. ...

## Scored shortlist
[ranked table: rank | working title | pillar | format | score (X/25)]

## Selected briefs (handoff to content-draft)
[brief 1, brief 2, ... using the brief schema above]

## Hub/spoke distribution schedule
| Day | Channel | Asset | Brief # | Notes |
|---|---|---|---|---|
| Mon | LinkedIn (hub) | long-form post | Brief 1 | — |
| Mon | X (spoke) | repurpose | Brief 1 | thread version |
| Tue | Newsletter (hub) | edition | Brief 2 | — |
| ...

## Engagement loop (10 target accounts)
| Account / buyer | Channel | Action | Tied to | Done? |
|---|---|---|---|---|
| [name] | LinkedIn | thoughtful comment on their last post | Brief 1 | ☐ |
| ...

## Tracking — buyer conversation metrics
For the week, track these (not likes):
- Direct replies to content
- DMs initiated by buyers
- Calls booked
- Qualified leads
- Objections raised (and which content surfaced them)
- Customer / prospect quotes captured (feed back into voc.md)

## Notes for next week
[what to test, what to retire, what to amplify]
```

## Validation checklist

Before handing the file back, verify all of the following. If any item fails, fix it before saving.

- At least 3 pillars from `positioning.md` appear across the selected briefs.
- At least 12 raw ideas were generated before scoring.
- 3 to 5 selected briefs in the final shortlist.
- Every selected brief includes: buyer pain (in VOC words), angle, proof or example, and CTA.
- Every selected brief carries every content-draft input field intact.
- The matrix includes a hub/spoke distribution schedule with specific days/channels.
- The matrix includes an engagement loop with 10 named target accounts.
- The tracking section names buyer-conversation metrics — not likes, follows, or impressions in isolation.
- A line on each brief explicitly tells the user to run `/content-draft` to move to drafting.

## Why this design

The reason this skill stops at briefs (instead of producing finished drafts) is that content quality collapses when planning and drafting are mashed together. Planning needs cold, scoring-driven thinking — what reaches the right buyer, what reinforces the ownable idea, what the offer needs this week. Drafting needs warm, voice-driven thinking — the right hook, the right rhythm, the right proof. Different modes. The matrix protects the planning mode by forcing scoring before prose, then ships briefs that are dense enough for the drafting skill to do its job without re-doing the planning.

The 5-criterion rubric exists to keep operators from over-indexing on "what would feel fun to write" (which is angle clarity only). A high-fun idea with no proof and no business relevance is a vanity post. The rubric makes that trade-off explicit.

The engagement loop is in here on purpose. Most "content plans" stop at publishing and wonder why nothing converts. For B2B operators doing $500K–$5M, the conversation that closes the deal usually starts in DMs or comments triggered by a post, not the post itself. Naming 10 accounts upfront and tying manual outreach to the week's themes is what turns content into pipeline.

## Anti-patterns to avoid

- **Skipping the raw idea pool.** If the model jumps straight to "here are 5 ideas," the user gets a recency-biased shortlist. Always generate 12+ first.
- **Generic buyer pain.** "Founders are overwhelmed" is not a VOC phrase. Pull verbatim from voc.md.
- **Single-pillar weeks.** Easy to do when one pillar feels hot. The matrix exists to keep the brand whole.
- **Vanity metrics.** If the tracking section drifts toward likes/impressions, the whole skill has failed its purpose.
- **Inventing pillars.** Pillars come from positioning.md. If the user wants new ones, send them to positioning-artifact-builder first.
- **Brief without proof.** A brief that says "TBD" under proof is not ready to hand off. Either find the proof or drop the brief and pick the next-highest scorer.
