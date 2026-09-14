# Scoring & Analysis Guide

Methodology for scoring pain points, building the Impact-Effort Matrix, mapping to the Three Outcomes, and generating Skills Recommendations after the self-assessment interview.

---

## Pain Point Extraction

After the interview, synthesize all responses into a structured pain point list. Each pain point is a discrete, actionable finding — not a vague theme.

**Extraction rules:**

1. Use the user's exact language when naming pain points. If they said "I spend hours chasing invoices," the pain point is "Chasing invoices" — not "Accounts receivable follow-up optimization."
2. Extract 5-15 pain points depending on interview depth:
   - Quick Scan: 5-8 pain points
   - Standard: 8-12 pain points
   - Deep Dive: 10-15 pain points
   - Custom: As many as the data supports
3. Each pain point should be specific enough to act on. "Marketing is hard" is too vague. "Writing product descriptions takes 45 min each" is actionable.
4. If the user mentioned time estimates, capture them. If not, estimate based on industry norms and note the estimate is approximate.

---

## Impact Scoring (1-10)

Score each pain point's potential impact if solved with AI:

| Score | Criteria | Examples |
|-------|----------|---------|
| **9-10** | Critical to revenue OR saves 5+ hours/week OR directly affects customer retention | Lost leads from slow response, manual invoice chasing losing $X/month, clients leaving due to poor follow-up |
| **7-8** | Significant impact OR saves 3-5 hours/week OR measurably improves client experience | Content creation bottleneck limiting growth, repetitive proposal writing, inconsistent onboarding |
| **5-6** | Moderate impact OR saves 1-3 hours/week OR noticeable quality improvement | Manual scheduling, redundant email drafting, basic reporting tasks |
| **3-4** | Minor convenience OR saves under 1 hour/week | Formatting documents, organizing files, minor research tasks |
| **1-2** | Negligible — nice to have but minimal business impact | Aesthetic preferences, occasional tasks that happen rarely |

**Scoring heuristics:**

- If the pain point touches revenue directly (leads, conversions, retention), start at 7 and adjust up or down
- If the user described it with emotional language ("drives me crazy," "I dread this"), bump +1
- If it affects their clients directly, bump +1
- If it only affects the user internally with no client-facing impact, cap at 6 unless time savings are substantial

---

## Effort Scoring (1-10)

Score the effort required to solve this pain point with AI tools and Cowork skills:

| Score | Criteria | Examples |
|-------|----------|---------|
| **1-2** | Plug-and-play. Under 30 minutes. Use an existing tool or skill as-is | Transcription with Fathom, email drafts with Claude, scheduling with Calendly |
| **3-4** | Some setup. 1-2 hours. May need a prompt template or simple skill | Custom email templates, content repurposing workflow, meeting prep checklist |
| **5-6** | Moderate learning curve. Half-day. Requires building a skill or connecting tools | CRM integration, multi-step content pipeline, automated reporting |
| **7-8** | Significant effort. Multiple days. Custom development or complex integrations | Voice agent deployment, multi-system workflow automation, custom dashboard |
| **9-10** | Major project. Weeks of work. Custom development, API integrations, or platform changes | Full CRM rebuild, custom software, enterprise-grade automation |

**Effort heuristics:**

- If an existing Cowork skill addresses it, effort is 1-3
- If it requires building a new skill, effort is 3-5
- If it requires connecting external APIs or tools, effort is 5-7
- If it requires custom software development, effort is 7-10
- Always consider the user's AI literacy score (Q4) — lower literacy = higher effort for the same task

---

## Quadrant Assignment

Plot each pain point on the Impact-Effort Matrix:

```
                    HIGH IMPACT
                        |
     Major Projects     |     Quick Wins
     (Impact 7-10,      |     (Impact 7-10,
      Effort 7-10)      |      Effort 1-6)
                        |
   ─────────────────────┼─────────────────────
                        |
     Thankless Tasks    |     Fill-Ins
     (Impact 1-6,       |     (Impact 1-6,
      Effort 7-10)      |      Effort 1-6)
                        |
                    LOW IMPACT
```

**Quadrant definitions:**

- **Quick Wins** (top-right): High impact, low effort. Do these first. These are the assessment's primary recommendations.
- **Major Projects** (top-left): High impact, high effort. Worth doing but plan carefully. Good candidates for phased implementation.
- **Fill-Ins** (bottom-right): Low impact, low effort. Do these when you have spare time or as learning exercises.
- **Thankless Tasks** (bottom-left): Low impact, high effort. Avoid these. Not worth the investment.

**Priority order for recommendations:** Quick Wins > Major Projects > Fill-Ins > Thankless Tasks (never recommend)

---

## Three Outcomes Mapping

Assign each pain point to one or more outcomes. Use the question tags from the question bank as a starting point, then refine based on the user's actual response.

| Outcome | Tag | What to Look For |
|---------|-----|-----------------|
| **Effectiveness** | `[E]` | Revenue, leads, conversions, pricing, retention, lifetime value, marketing, sales pipeline |
| **Efficiency** | `[F]` | Time saved, hours recovered, automation, templates, eliminated steps, reduced manual work |
| **Quality** | `[Q]` | Client experience, consistency, response time, NPS, reviews, follow-up, onboarding |

**Aggregation:**

After mapping, produce a Three Outcomes Summary:

- **Efficiency:** Total estimated hours recoverable per week across all efficiency pain points
- **Effectiveness:** Number of revenue opportunities identified + estimated impact range
- **Quality:** Number of client experience improvement areas identified

---

## Skills Recommendation Algorithm

After scoring and mapping, cross-reference findings against available Cowork skills.

### Step 1: Gather Available Skills

Read the `available_skills` list from the current session context. This includes both installed skills (from plugins) and skills that could be installed.

### Step 2: Match Pain Points to Skills

For each Quick Win pain point (in priority order):

1. Extract keywords from the pain point description
2. Match against skill names, descriptions, and trigger phrases
3. Score match confidence:
   - **Strong match:** Skill description directly addresses the pain point (e.g., pain point is "writing LinkedIn posts" and skill is `linkedin-content`)
   - **Partial match:** Skill addresses a related capability (e.g., pain point is "repurposing content" and skill is `content-engine`)
   - **No match:** No available skill addresses this pain point

### Step 3: Build Recommendations

For each recommended skill (maximum 5):

```
skill_name: [fully qualified name, e.g., returnmytime:email-marketing]
pain_point_addressed: [which assessment finding it solves]
why_it_helps: [concrete explanation using the user's own words]
starter_prompt: [a ready-to-use first prompt for the skill]
installed: [true/false — already installed vs. needs installation]
```

### Recommendation Rules

- Maximum 5 skill recommendations (don't overwhelm)
- Only recommend skills with clear evidence from the interview — never speculative
- Never recommend `self-assessment` or `cowork-onboarding` (meta-recursive)
- Prioritize already-installed skills (zero friction) over available-but-not-installed
- If no skills match, say so honestly and suggest exploring the plugin marketplace
- For pain points with no skill match, flag them as candidates for custom skill creation (feeds into the Skill Blueprint in Step 6)

---

## Edge Cases

**User says "all three" for primary outcome:**
Weight all three equally in scoring. Ask the closing anchor question (Q193) to determine final priority for the report.

**Very few pain points extracted:**
If fewer than 5 pain points surface, the interview was too short or too high-level. For Quick Scan, this is acceptable. For Standard or Deep Dive, consider asking 1-2 follow-up questions to dig deeper.

**All pain points cluster in one quadrant:**
This is normal — it means the user's challenges are concentrated. Note the pattern in the report and explain what it means.

**User's AI literacy is very low (Q4 = level 1-2):**
Increase all effort scores by 1-2 points to account for learning curve. Weight Quick Wins even more heavily — the user needs early wins to build confidence.

**User's AI literacy is very high (Q4 = level 4-5):**
Decrease effort scores by 1 point for tool-based solutions. They can handle more complex recommendations. Consider recommending Major Projects alongside Quick Wins.
