# Context File Guide

Templates, question banks, and examples for generating the four core context files. Read this before starting the Context Files capability.

---

## File 1: about-me.md

### Template

```markdown
# About Me — [Name]

## Who I Am
[1-2 sentences: name, role, primary identity. E.g., "I'm Sarah Chen, a freelance brand strategist working with DTC founders."]

## Professional Background
[2-3 sentences: career history, credentials, what makes them credible. Include specific companies, years of experience, or domains of expertise.]

## What I Do Now
[For each active business/project, include:]
### [Business/Project Name]
- What it is and what it does
- Their specific role
- Key offerings or focus areas

## My Ideal Customer
[If applicable: who they serve, what those people need, key pain points]

## Tools I Use Daily
[Bulleted list of platforms, apps, and services they use regularly]

## What I Value
[3-5 core principles that drive their work and decision-making]
```

### Interview Questions — About Me

**Q1: Identity** (AskUserQuestion)
"In one sentence, how would you describe what you do?"
Options:
- Consultant / advisor
- Agency owner
- E-commerce / product business
- Creator / content business
- Freelancer / solopreneur
(Free text always available for custom answers)

**Q2: Businesses** (AskUserQuestion)
"What are all the businesses or projects you're actively working on right now? Which ones take up the most time?"
Options:
- Just one business
- Two businesses
- Multiple (3+)
- Let me list them
Follow up to understand each one: name, what it does, their role.

**Q3: Background** (AskUserQuestion)
"What's your professional background before this? What experience makes you credible in what you do?"
Options:
- Corporate career → went independent
- Always been entrepreneurial
- Specific industry expertise
- Let me explain
Get specifics: companies, years, domains.

**Q4: Tools** (AskUserQuestion, multiSelect)
"What tools and platforms do you use day-to-day?"
Options:
- Google Workspace (Drive, Gmail, Docs, Sheets)
- Slack / Discord / Teams
- Notion / Asana / Monday
- Social media platforms (X, LinkedIn, Instagram)
(Free text for additional tools)

**Q5: Customers** (AskUserQuestion — skip if not a business owner)
"Who do you serve? What does your ideal customer look like?"
Options:
- Other businesses (B2B)
- Consumers (B2C)
- Mix of both
- Not applicable (internal role)

---

## File 2: brand-voice.md

### Template — Single Voice

```markdown
# Brand Voice — [Name]

## Tone & Style
[2-3 sentences describing their communication style]

## Voice Characteristics
- [Characteristic 1: e.g., "Direct and to the point — no filler"]
- [Characteristic 2: e.g., "Warm but professional"]
- [Characteristic 3: e.g., "Uses specific examples and numbers"]

## Phrases & Language I Use
- [Examples of language that sounds like them]

## What to Avoid (Anti-Voice)
- [Language or styles that feel wrong]
- [Specific things Claude should never do when writing for them]

## Writing Rules
- [Specific formatting or structural preferences]
```

### Template — Multiple Voice Modes

```markdown
# Brand Voice — [Name]

[Name] operates in [N] distinct voice registers depending on audience and context. Identify which mode is appropriate based on the task.

---

## Voice Mode 1: [Name/Label]
Use this voice when: [contexts]
**Tone:** [description]
**Characteristics:** [bullet points]
**Example phrasings:** [real examples]
**What to avoid:** [anti-patterns]

---

## Voice Mode 2: [Name/Label]
Use this voice when: [contexts]
...

---

## Voice Selection Guide
| Context | Voice Mode |
|---------|-----------|
| [context] | [mode] |

## Universal Rules (All Modes)
- [Rules that apply regardless of voice mode]
```

### Interview Questions — Brand Voice

**Q1: Communication Style** (AskUserQuestion)
"How would you describe your tone when communicating professionally?"
Options:
- Direct and no-BS — get to the point, no padding
- Warm and encouraging — supportive, builds people up
- Academic / analytical — precise, evidence-based, thorough
- Casual and conversational — like talking to a friend

**Q2: Multiple Voices** (AskUserQuestion)
"Do you communicate differently depending on the audience?"
Options:
- Same voice everywhere
- Slightly different by context (e.g., more formal with clients)
- Very different voices (e.g., technical vs. non-technical audiences)
If multiple voices: interview each one separately using Q1 format, then ask which contexts each applies to.

**Q3: Anti-Voice** (AskUserQuestion, multiSelect)
"What kind of language or style makes you cringe? What should Claude NEVER sound like?"
Options:
- Buzzword corporate speak ("leverage synergies")
- Over-promising hype ("this will 10X your business overnight")
- Gatekeeping jargon (making things sound harder than they are)
- Generic AI-sounding content (bland, formulaic, obviously AI-written)

**Q4: Existing Materials** (AskUserQuestion)
"Do you have any existing brand materials, style guides, or writing samples?"
Options:
- Yes, in my connected platforms (search for them)
- Yes, I can upload them
- No, but I can describe my style
- Skip this — I'll refine later

If connected platforms have brand docs (found during pre-scan), reference them directly.

---

## File 3: working-style.md

### Template

```markdown
# Working Style — [Name]

## How I Work With Claude

### Planning & Execution
[How they prefer Claude to approach tasks — plan first, ask questions, just execute, etc.]

### Communication Preferences
[Verbosity, tone, preamble preferences, question-asking behavior]

### Output Defaults
[Default file formats by task type]

### Task Context
[What a typical day/week looks like — helps Claude understand priority and context]

## Things Claude Should Always Do
- [Positive behaviors they want reinforced]

## Things Claude Should Never Do
- [Behaviors to avoid — hard rules]

## Technical Context
[Their technical comfort level — so Claude calibrates explanations appropriately]
```

### Interview Questions — Working Style

**Q1: Task Approach** (AskUserQuestion)
"When Claude starts a task for you, what do you prefer?"
Options:
- Always ask clarifying questions first
- Just go for simple tasks, ask on complex ones
- Show me a plan first and let me approve
- Depends — I'll tell you each time

**Q2: Output Format** (AskUserQuestion)
"What file format should Claude default to for deliverables?"
Options:
- Markdown (.md) for most things
- Word docs (.docx) for professional documents
- Depends on the task type
- Ask me each time

**Q3: Verbosity** (AskUserQuestion)
"How detailed should Claude's responses be?"
Options:
- Concise and direct — get to the point
- Balanced — enough to understand, not over-explained
- Detailed — thorough explanations
- Match the complexity — short for simple, detailed for complex

**Q4: Rules** (AskUserQuestion, multiSelect)
"Any pet peeves or hard rules for how Claude should behave?"
Options:
- No fluff or filler — never pad responses
- Always show reasoning — explain the thinking
- Bias toward action — build it, don't just describe it
- Be opinionated — push back when there's a better way
(Free text for additional rules)

---

## Voice of Customer (`voc.md` or `voice-of-customer.md`)

The fourth core context file. Captures how your buyers actually talk so the agent can mirror their language in marketing, sales, content, and client-facing work. Without this, output trends generic and SaaS-sounding regardless of how detailed the brand voice file is.

### When to read it

The agent loads VOC at session start (Tier 1 in the prime skill). It uses VOC most heavily when:
- Writing marketing content, ads, or social posts
- Drafting sales messages, follow-ups, objection responses
- Building positioning statements, landing pages, offer copy
- Drafting client onboarding sequences or check-ins

### Sources

Real data, in priority order:
1. Sales call notes or full transcripts
2. Reviews and testimonials (raw, not edited for marketing)
3. Support tickets and customer emails
4. DMs and comments on social
5. "Best customer" descriptions you've written or said out loud
6. Founder memory — what you remember buyers saying. Always label these as assumption.

If no real data exists, fill the file with founder memory and add the header line `ASSUMPTION-BASED VOC - replace with real quotes`. Downstream skills treat this as a temporary placeholder.

### Interview questions

The cowork-onboarding skill walks through these as AskUserQuestion prompts:

1. Who is the buyer, in plain language?
2. What do they say right before they look for help?
3. What problem words do they repeat?
4. What outcome do they ask for in their words?
5. What do they fear if nothing changes?
6. What alternatives have they already tried?
7. What objections show up before buying?
8. What phrases do buyers use that you would not naturally write?
9. What jargon does your industry use that buyers do not use?
10. Paste 3 to 10 exact quotes if available.

### Template

````markdown
# Voice of Customer

## Buyer snapshot

[2-3 sentences naming the buyer in plain language. Role, context, what triggers them to look for help.]

## Exact buyer phrases
- "..." — source: [call/review/DM/founder memory]
- "..." — source: [...]

## Pain language

[Words and phrases buyers actually use to describe what's hurting. Verbatim.]

## Desired outcomes

[What buyers say they want — in their own words, not your features.]

## Trigger moments

[The moment buyers decide to look for help. What just happened.]

## Failed alternatives

[What they've tried that didn't work. Why it didn't work — in their words.]

## Objections / hesitations

[What they push back on before buying. The silent objection too — what stops them from saying yes.]

## Reuse these words

[A short list of buyer phrases the agent should weave into copy. Verbatim.]

## Avoid these words

[The jargon blacklist. Words your industry uses that buyers do not. Don't make the agent reach for these.]

## Evidence quality
- Direct quotes:  [count]
- Founder assumptions: [count]
- Last updated: YYYY-MM-DD
````

### Validation rules

Before declaring VOC complete, verify:

- **Minimum viable:** 5 exact buyer phrases, 3 pains, 3 outcomes, 2 objections.
- **Strong:** 20+ quotes from 3+ sources.
- Every quote has a source label.
- "Avoid these words" is non-empty (at least 3 entries) — the jargon blacklist is what prevents drift back to generic SaaS-speak.
- `Last updated:` field is present and ISO-formatted (YYYY-MM-DD).

### Refresh cadence

Every 90 days. The cowork-onboarding skill schedules this automatically when scheduled tasks are configured. Manual trigger: ask the agent to "refresh my VOC" — it will pull recent quotes from connected sources and merge into the file.

---

## Tips for Conducting the Interview

- **Ask 1-2 questions per AskUserQuestion call.** Don't dump all questions at once.
- **Use progressive disclosure.** Start broad, drill into detail based on answers.
- **Offer to pre-fill from connected data.** If Google Drive or Notion has relevant docs, use them.
- **Accept "skip" and "I'll refine later" gracefully.** Not everyone wants to answer everything upfront.
- **Use their exact words.** When they describe their style or preferences, use their language in the files, not paraphrased corporate speak.
- **Adapt formality.** If they're casual, be casual. If they're precise, be precise. Mirror the user.
