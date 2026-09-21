---
name: self-assessment
description: >
  Interactive AI readiness self-assessment using Return My Time's
  Three Outcomes methodology. Identifies the highest-ROI AI opportunities
  in your business through a guided interview, then recommends relevant
  Cowork skills to act on the findings. Produces an Impact-Effort Matrix,
  Skills Recommendations, and a Skill Blueprint for your first custom skill.
  Requires onboarding to be completed first (context files must exist).
  Use when someone says "assess my business," "AI readiness check,"
  "self-assessment," "where should I use AI," "audit my workflows,"
  "find my quick wins," or any request to identify where AI can save time,
  make money, or improve customer experience. Supports timed interview
  lengths: 5-minute quick scan, 10-minute standard, 15-minute deep dive,
  or custom.
---

# AI Readiness Self-Assessment

An interactive, interview-driven assessment that identifies the highest-ROI opportunities for AI in your business. Built on the Three Outcomes methodology: Effectiveness (revenue), Efficiency (time saved), Quality (customer experience).

This assessment is the **Audit** step of the AOA (Audit → Optimize → Automate) framework. Its output feeds directly into skill creation (Optimize) and skill scheduling (Automate).

## Before Starting

Read the reference files before executing:
- Question bank: `@${CLAUDE_PLUGIN_ROOT}/skills/self-assessment/references/question-bank.md`
- Scoring methodology: `@${CLAUDE_PLUGIN_ROOT}/skills/self-assessment/references/scoring-guide.md`
- Report template: `@${CLAUDE_PLUGIN_ROOT}/skills/self-assessment/references/report-template.md`

## Prerequisite: Onboarding Must Be Complete

Before running the self-assessment, verify that context files exist (at minimum `about-me.md` in CONTEXT/ or root). VOC (`voc.md` or `voice-of-customer.md`) is also strongly recommended — the assessment uses it to ground recommendations in buyer language. If `about-me.md` is missing, refuse to proceed. If `voc.md` is missing, warn and continue.

If no context files are found:

"The self-assessment works best when I already know about you and your business. Let's run through onboarding first — even the 15-minute Quickstart will give me the context I need. Then we'll come back to the assessment."

Invoke `build-with-ai:cowork-onboarding` and return to self-assessment after completion.

If `about-me.md` exists but `voc.md` does not, emit this warning before starting the interview: "Note: I don't see a VOC file. The assessment will work, but recommendations won't be grounded in your buyer's exact language. After the assessment, consider running cowork-onboarding to capture VOC — it makes downstream skills (especially marketing and sales) substantially more useful."

If context files exist, read them before starting the interview. This allows Claude to:
- Skip questions already answered in context files (e.g., skip industry detection if about-me.md specifies it)
- Personalize question framing based on known business details
- Pre-populate the assessment with known tool stack and workflow information

## Interview Flow

### Step 0: Setup & Time Selection

Use AskUserQuestion:

```
"How deep do you want to go?"

Options:
- Quick Scan (~5 min) -- 8-10 questions covering the essentials.
  Good for a fast pulse check.
- Standard Assessment (~10 min) -- 15-20 questions with industry-specific
  depth. Recommended for actionable results.
- Deep Dive (~15 min) -- 25-30 questions covering all three outcomes
  plus your industry. Most thorough analysis.
- Custom -- I'll set my own pace. Ask me questions until I say stop.
```

Store the selection. This controls which question tiers get asked.

### Step 1: Universal Questions (All Tiers)

**Always asked (A1 + A2 from question bank):**

1. Outcome Prioritization (Q1-3 from bank — pick the best one based on context, or ask 2 of 3)
2. AI Literacy baseline (Q4)

**Question delivery:** Use AskUserQuestion for each. Map the bank's open-ended questions to multiple-choice options where possible. For example:

Bank Q1: "If AI could deliver just one result for your business in the next 90 days, which would matter most?"

AskUserQuestion version:
```
"If AI could deliver one result in the next 90 days, which matters most?"
Options:
- Making more money (Effectiveness)
- Getting hours back in my week (Efficiency)
- Delivering a better experience to my clients (Quality)
- Honestly, all three -- help me prioritize
```

### Step 2: Outcome-Specific Questions (Standard + Deep Dive)

Based on their Q1 answer (primary outcome), pull questions from the matching A3/A4/A5 section:

| Primary Outcome | Question Bank Section | Quick Scan | Standard | Deep Dive |
|----------------|----------------------|------------|----------|-----------|
| Effectiveness | A3 (Q5-9) | 2 questions | 3 questions | All 5 |
| Efficiency | A4 (Q10-16) | 2 questions | 4 questions | All 7 |
| Quality | A5 (Q17-23) | 2 questions | 3 questions | All 7 |

For Standard and Deep Dive, also ask 2-3 questions from the secondary outcome sections (the ones they didn't pick as primary).

**Question selection logic:** For each section, prioritize questions that:
1. Surface the most actionable pain points (questions tagged with time estimates)
2. Match the user's business type (if known from context files)
3. Are most likely to reveal quick wins

### Step 3: Industry-Specific Questions (Standard + Deep Dive Only)

**Industry detection:** Use AskUserQuestion if not already known from context files:

```
"What best describes your business?"
Options:
- Hospitality / Events / Venues
- Insurance
- Real Estate / Property Management
- Financial Services / Accounting
- Legal Services
- Healthcare / Medical
- Coaching / Consulting
- Marketing / Creative Agency
- Content Creation (YouTube, podcast, blog)
- Course Creation / Online Education
- SaaS / Software
- E-commerce / Retail
- Home Services (cleaning, landscaping, HVAC)
- Trades / Contracting
- Virtual Assistant / Online Business Manager
- Freelancer / Independent Contractor
- Other -- I'll describe it
```

Map the selection to the corresponding Section B subsection in the question bank.

| Tier | Industry Questions Asked |
|------|------------------------|
| Quick Scan | 0 (skip industry section) |
| Standard | 3-4 from matched industry |
| Deep Dive | 5-7 from matched industry |
| Custom | Keep asking until user says stop |

### Step 3.5: Buyback Rate Anchor (Standard + Deep Dive)

Before the closing anchor, ask one revenue question to support Buyback Rate calculation in the Blueprint:

```
"What's your approximate annual revenue? This anchors the delegation threshold in your Skill Blueprint."

Options:
- Under $100K
- $100K-$250K
- $250K-$500K
- $500K-$1M
- $1M-$5M
- $5M+
- Skip this — calculate threshold from a generic revenue band
```

Use the midpoint of the chosen band for the Buyback Rate math. If the user skips, default to $250K (a reasonable solo-operator midpoint) and note the assumption in the Blueprint.

### Step 4: Closing Anchor (All Tiers)

Always end with 1-2 questions from the Closing section (Q193-195):

```
"Based on everything we've discussed, which of these would have
the biggest impact on your business right now?"
Options:
- Making more money
- Getting hours back
- Improving client experience
- [Their primary pain point from earlier -- dynamically generated]
```

And:

```
"What would success look like 90 days from now?"
[Free text]
```

## Scoring & Analysis

### Pain Point Extraction

After the interview, Claude synthesizes all responses into a structured pain point list. For each pain point:

1. **Score Impact (1-10)** using the scoring guide:
   - 9-10: Critical to revenue OR saves 5+ hours/week
   - 7-8: Significant impact OR saves 3-5 hours/week
   - 5-6: Moderate impact OR saves 1-3 hours/week
   - 3-4: Minor inconvenience
   - 1-2: Negligible

2. **Score Effort (1-10):**
   - 1-2: Plug-and-play, under 30 minutes
   - 3-4: Some setup, 1-2 hours
   - 5-6: Moderate learning curve, half-day
   - 7-8: Significant learning, multiple days
   - 9-10: Major project, custom development

3. **Assign Quadrant:**
   - Quick Wins: Impact 7-10 AND Effort 1-6
   - Major Projects: Impact 7-10 AND Effort 7-10
   - Fill-Ins: Impact 1-6 AND Effort 1-6
   - Thankless Tasks: Impact 1-6 AND Effort 7-10

4. **Map Outcome Type:** Effectiveness / Efficiency / Quality

### Three Outcomes Summary

Aggregate by outcome:
- Total hours recoverable (Efficiency)
- Revenue opportunities identified (Effectiveness)
- Quality improvement areas (Quality)

## Step 5: Skills Recommendations

After scoring pain points and building the Impact-Effort Matrix, cross-reference the findings against the user's installed and available Cowork skills.

**Process:**

1. Read the `available_skills` list from the current session
2. For each Quick Win pain point, check if an existing skill addresses it:
   - Match pain point keywords against skill descriptions
   - Prioritize skills that are already installed (zero friction)
   - Then recommend available-but-not-installed skills
3. For each recommended skill, provide:
   - `skill_name` — fully qualified (e.g., `returnmytime:email-marketing`)
   - `pain_point_addressed` — which assessment finding it solves
   - `why_it_helps` — concrete explanation tied to their stated workflows
   - `starter_prompt` — a ready-to-use first prompt for the skill
   - `installed` — boolean (already installed vs. needs installation)

**Rules:**
- Recommend 0-5 skills maximum (don't overwhelm)
- Only recommend skills with clear evidence from the interview
- Never recommend `self-assessment` or `cowork-onboarding` (meta-recursive)
- If no skills match, say so honestly: "None of your currently available skills directly address these opportunities. You might explore the plugin marketplace for [category]."

## Step 6: Skill Blueprint Generation

After Skills Recommendations, generate a blueprint for the user's first custom skill. This is the critical handoff artifact that bridges the self-assessment (Audit) to skill creation (Optimize → Automate) in the AOA framework.

**Logic:**

1. Identify the #1 Quick Win that either has no existing skill match OR represents the user's most impactful automation opportunity
2. Generate a structured Skill Blueprint for that pain point
3. Always generate at least one blueprint, even if existing skills cover some wins — the user should build a skill as part of the learning process

**Blueprint format:**

```markdown
## Your First Skill Blueprint

**Pain point:** [The #1 Quick Win from the assessment]
**Outcome type:** [Effectiveness / Efficiency / Quality]
**Estimated impact:** [hours saved or revenue impact]

### What this skill would do
[1-2 sentence description of the automation]

### When you'd use it
Trigger phrases: [natural language triggers for the skill]

### What it needs from you
[Inputs: files, information, context the skill requires]

### How it works (high-level steps)
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]
5. [Step 5]

### What it produces
[Output: what the skill delivers — files, reports, messages, etc.]

### Buyback Rate (delegation threshold)

Your Buyback Rate is **Annual Revenue ÷ 2,000 ÷ 4**. Any task at or below that hourly rate is a candidate to delegate to an agent.

**Calculation for you:**
- Annual revenue: $[ASK OR PULL FROM about-me.md]
- Divide by 2,000 (annual working hours) → $[X]/hour cost-of-time
- Divide by 4 (the buyback factor) → $[Y]/hour delegation threshold

Tasks taking less than $[Y]/hour of value are the cleanest delegation candidates because the cost of building and maintaining the skill is recouped fast.

### Define-Outcome rubric

Before building, write down the answers to all three:

- **Desired outcome:** [What does success look like in one sentence?]
- **Quality bar (one measurable):** [The single quality check that decides "this output is acceptable" — e.g., "every recommendation cites the call timestamp it came from."]
- **Coaching loop:** [How will you validate the agent over the first two weeks? Spot-check sample size, frequency, what triggers a course correction.]

### Validation plan

Before you flip the agent on, queue these:

- **Three real inputs:** [List three actual past examples of this task — real client emails, real meeting transcripts, real briefs. The skill must produce acceptable output on all three.]
- **Edge cases to test:** [Two scenarios where the skill is most likely to fail — empty input, oversized input, mixed-language input, etc.]
- **Brand/VOC check:** [Confirm the output uses VOC language and brand voice. If not, the skill needs a CONTEXT/voc.md and CONTEXT/brand-voice.md read step before generation.]

### Two-week measurement plan

Capture the baseline BEFORE turning the agent on:

- **Time today:** [How long this task takes you currently — minutes or hours]
- **Cost today:** [Hourly rate × time, or other cost basis]
- **Error rate today:** [What goes wrong now and how often]

After two weeks of running the agent:

- **Time with agent:** [Including review time]
- **Cost with agent:** [Token costs + your review time]
- **Error rate with agent:** [What goes wrong and how often]
- **Verdict:** [Keep, refine, or kill]

This is the artifact you bring to a 90-day review of the skill — without baseline numbers, you can't tell if the skill is actually winning.

### Ready-to-use skill-creator prompt
To build this skill, run the skill-creator and paste the following:

> I want to create a skill called [name] that [description].
> It should trigger when I say [triggers].
> The skill should [step-by-step workflow].
> It should output [deliverable format].
> Here's the full context from my self-assessment: [reference to assessment file]
```

This blueprint becomes the input to the skill-creator skill. The Optimize step (plan mode) and Automate step (build/validate) use this artifact as the starting point.

## Step 7: Generate Report

Read `@${CLAUDE_PLUGIN_ROOT}/skills/self-assessment/references/report-template.md` for the full template. Generate `self-assessment-[date].md` in the workspace.

**File save location:**
- If OUTPUTS/ exists: save to `OUTPUTS/self-assessment-[date].md`
- If no OUTPUTS/: save to selected folder root
- If no folder selected: save to outputs directory

## Integration with Onboarding

The self-assessment **requires onboarding to be completed first** (context files must exist). It cannot run as a pre-onboarding standalone. This is enforced by the prerequisite check at the top of the skill.

**Integration points:**

1. **Post-onboarding offer (Full Setup path)**: After Capability 6 (Security Review) and before Your First Prompt, the onboarding skill offers the self-assessment: "Want to find out where AI can have the biggest impact on your business? This takes about 10 minutes and maps your workflows to the highest-ROI opportunities — plus recommends specific skills to act on the findings."

2. **Returning user menu option**: Self-Assessment appears in the returning user menu since they've already completed onboarding.

3. **Standalone invocation**: Users can invoke `build-with-ai:self-assessment` directly anytime after onboarding. The prerequisite check catches cases where context files are missing and redirects to onboarding.

## Behavioral Guidelines

- **Use AskUserQuestion for every question.** Multiple-choice options reduce friction. Always allow free-text for nuance.
- **Personalize from context files.** Reference the user's business, tools, and role by name — don't make them repeat what's already known.
- **Skip what's known.** If context files already answer a question, skip it and note why: "I can see from your about-me that you're in e-commerce, so I'll skip the industry question."
- **Be conversational, not clinical.** This is a self-assessment, not a doctor's visit. Keep it warm and actionable.
- **Don't overwhelm.** 1-2 questions per AskUserQuestion call. Never dump a wall of questions.
- **Show empathy for pain points.** When they describe frustrating workflows, acknowledge it before moving on.
- **Ground recommendations in their words.** Use the user's exact language when referencing pain points — not abstracted versions.
- **AOA framing throughout.** Remind the user where they are in the framework: this is the Audit step. Next comes Optimize (planning the skill), then Automate (building and scheduling it).
