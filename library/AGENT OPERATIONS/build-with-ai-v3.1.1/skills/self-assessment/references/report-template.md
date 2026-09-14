# Self-Assessment Report Template

Output format specification for the AI Readiness Self-Assessment report. Claude generates this report as a markdown file after completing the interview and scoring.

---

## File Naming & Location

**Filename:** `self-assessment-YYYY-MM-DD.md`

**Save location (in order of preference):**
1. `OUTPUTS/` folder if it exists in the workspace
2. Workspace root if no OUTPUTS/ folder
3. Session outputs directory if no workspace folder is selected

---

## Report Structure

Generate the report using the following template. Replace all `[bracketed content]` with actual findings. Remove any sections that don't apply (e.g., skip Industry-Specific Findings for Quick Scan).

```markdown
# AI Readiness Self-Assessment

**Date:** [YYYY-MM-DD]
**Name:** [User's name from context files]
**Business:** [Business name/description from context files]
**Industry:** [Detected or stated industry]
**Assessment tier:** [Quick Scan / Standard / Deep Dive / Custom]

---

## Your Priority Outcome

Based on our conversation, your primary focus is **[Effectiveness / Efficiency / Quality]**.

[1-2 sentences summarizing why this outcome matters most to them, using their own words from the interview. Reference their specific situation.]

---

## Executive Summary

[3-5 sentences summarizing the key findings. Include:
- Total number of pain points identified
- Number of Quick Wins found
- Estimated total hours recoverable per week (Efficiency)
- Number of revenue opportunities identified (Effectiveness)
- Number of quality improvement areas (Quality)
- The single most impactful opportunity]

---

## Three Outcomes Overview

### Effectiveness (Revenue)
[Summary of revenue-related findings. Include specific opportunities identified, estimated impact where possible.]

**Opportunities identified:** [count]
**Estimated revenue impact:** [range or "to be quantified"]

### Efficiency (Time Saved)
[Summary of time-related findings. Include specific workflows that can be automated and time estimates.]

**Estimated hours recoverable:** [X] hours/week
**Top time sinks identified:** [list the top 3]

### Quality (Customer Experience)
[Summary of quality-related findings. Include specific client experience improvements identified.]

**Improvement areas identified:** [count]
**Key quality gaps:** [list the top 3]

---

## Impact-Effort Matrix

### Quick Wins (Do First)
High impact, low effort — these are your immediate priorities.

| # | Pain Point | Impact | Effort | Outcome | Est. Time Saved |
|---|-----------|--------|--------|---------|----------------|
| 1 | [Pain point in user's words] | [1-10] | [1-10] | [E/F/Q] | [X hrs/wk] |
| 2 | [Pain point] | [score] | [score] | [tag] | [estimate] |
| 3 | [Pain point] | [score] | [score] | [tag] | [estimate] |

### Major Projects (Plan Carefully)
High impact, high effort — worth doing but requires planning.

| # | Pain Point | Impact | Effort | Outcome | Notes |
|---|-----------|--------|--------|---------|-------|
| 1 | [Pain point] | [score] | [score] | [tag] | [Why it's worth the effort] |

### Fill-Ins (When You Have Time)
Low impact, low effort — good for building momentum.

| # | Pain Point | Impact | Effort | Outcome |
|---|-----------|--------|--------|---------|
| 1 | [Pain point] | [score] | [score] | [tag] |

[Note: Thankless Tasks (low impact, high effort) are deliberately excluded — they're not worth your time.]

---

## Skills Recommendations

Based on your assessment findings, here are the Cowork skills that can address your top pain points:

[For each recommended skill (0-5 max):]

### [Skill Display Name]
**Skill:** `[fully qualified skill name]`
**Addresses:** [Which pain point from the matrix]
**Why it helps:** [Concrete explanation tied to their specific workflow, using their words]
**Status:** [Already installed / Available to install]

**Try this first:**
> [Ready-to-use starter prompt for the skill]

[If no skills match:]

None of your currently available skills directly address these opportunities. You might explore the plugin marketplace for [category] tools, or build a custom skill using the blueprint below.

---

## Your First Skill Blueprint

This is the bridge from assessment (Audit) to action (Optimize → Automate). The blueprint below describes a custom skill designed for your #1 opportunity.

**Pain point:** [The #1 Quick Win from the assessment]
**Outcome type:** [Effectiveness / Efficiency / Quality]
**Estimated impact:** [hours saved per week or revenue impact]

### What this skill would do
[1-2 sentence description of the automation]

### When you'd use it
**Trigger phrases:** [natural language triggers — what the user would say to invoke it]

### What it needs from you
[Inputs: files, information, context the skill requires from the user]

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
To build this skill, invoke the `skill-creator` skill and paste the following:

> I want to create a skill called [name] that [description].
> It should trigger when I say [triggers].
> The skill should [step-by-step workflow].
> It should output [deliverable format].
> Here's the full context from my self-assessment: [reference to assessment file]

---

## What's Next: The AOA Path

This assessment is the **Audit** step of the AOA framework. Here's your path forward:

### Audit (Complete)
You've identified [X] pain points, [Y] Quick Wins, and your primary focus is [outcome]. This report is your roadmap.

### Optimize (Next Step)
Take the Skill Blueprint above and use the `skill-creator` to design your first custom skill. This is where you turn findings into a plan.

### Automate (Final Step)
Once the skill is built and tested, use scheduled tasks to put it on autopilot. Your [pain point] gets handled automatically, and you get [impact] back.

**Your recommended first action:** [Specific, concrete next step — e.g., "Run the skill-creator with the blueprint above to build your [skill name] skill."]

---

*Generated by the Build With AI self-assessment skill on [date].*
*Framework: AOA (Audit → Optimize → Automate) by Return My Time.*
```

---

## Generation Instructions

### Tone
- Warm, direct, actionable. This is not a clinical audit — it's a practical roadmap.
- Use the user's own words when describing their pain points. Don't abstract or corporate-ify them.
- Be encouraging about Quick Wins — they should feel motivated to act.
- Be honest about Major Projects — don't minimize the effort required.

### Content Rules
- Every recommendation must tie to a specific interview response. No generic advice.
- Time estimates should be conservative. Better to under-promise.
- The Skill Blueprint should always be generated, even if existing skills cover some wins. Building a custom skill is part of the learning journey.
- The "What's Next" section should always end with one specific, concrete action step.

### Formatting Rules
- Use tables for the Impact-Effort Matrix — they're scannable.
- Keep the Executive Summary under 5 sentences.
- The Skill Blueprint section should be copy-pasteable into the skill-creator.
- Include the AOA framework positioning throughout — this assessment is the Audit step.

### Conditional Sections
- **Quick Scan:** Skip Industry-Specific Findings section. Shorter Executive Summary. May have fewer than 3 Quick Wins.
- **Standard:** Include all sections. 3-5 Quick Wins expected.
- **Deep Dive:** Include all sections. 5+ Quick Wins expected. Add a "Detailed Findings" subsection under each Three Outcomes category with expanded analysis.
- **Custom:** Follow the Standard format but adjust scope based on actual interview depth.
