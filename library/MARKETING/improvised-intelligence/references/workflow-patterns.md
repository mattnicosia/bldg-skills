# Workflow Patterns — Detection & Capture Reference

## Table of Contents
1. Detection Priority Matrix (line 7)
2. Known High-Value Patterns (line 20)
3. Skill Template (line 135)
4. Description Writing Guide (line 175)

---

## 1. Detection Priority Matrix

When multiple patterns detected, prioritize by:

| Priority | Criteria | Weight |
|----------|----------|--------|
| 1 | **Revenue impact** — Will this make/save money? | Highest |
| 2 | **Frequency** — Weekly > Monthly > Occasional | High |
| 3 | **Delegation potential** — Could this be handed off? | Medium |
| 4 | **Complexity** — More steps = more value in systematizing | Medium |

**DO suggest skills for:** workflows done weekly+, high-value deliverables, multi-tool integrations, 5+ step processes, anything delegatable.

**DON'T suggest skills for:** one-off research, simple Q&A, highly variable creative work, processes still being figured out (revisit after 3rd iteration).

---

## 2. Known High-Value Patterns

### Client Accelerator
**Frequency:** Per new consulting client | **Value:** $5K+ per engagement

Phases: Research client → Create strategy/assets → Build infrastructure (voice AI, landing page, automations) → Package deliverables → Handoff documentation

**Triggers:** "New consulting client," "Onboard [client name]," "Build out [client]'s system"

---

### Podcast Production
**Frequency:** Weekly | **Value:** $5K/mo retainer

Phases: Guest prep/research → Record → Show notes → Audiogram clips → Social distribution → Newsletter content

**Triggers:** "New episode," "Show notes for [episode]," "Podcast guest prep"

---

### Voice Agent Builder
**Frequency:** Per client project | **Value:** Productizable service

Phases: Discovery (needs, phone setup) → Platform comparison → Prompt engineering → Integration (Twilio, calendar, CRM) → Testing → Handoff

**Triggers:** "Set up voice assistant," "AI receptionist," "Retell," "Vapi," "Phone automation"

---

### Wedding Lead Capture
**Frequency:** Per inquiry | **Value:** $1,500-8,000 per booking

Phases: Lead intake (Knot, WeddingWire, referral) → Qualification → Availability check → Quote generation → Follow-up sequence → Contract/Booking

**Triggers:** "Wedding inquiry," "New lead from [source]," "Quote for [date]"

---

### Pitch/Proposal Builder
**Frequency:** Per opportunity | **Value:** Deal-closing asset

Phases: Research prospect → Define scope → Build deck/one-pager → Pricing → Case studies → Follow-up sequence

**Triggers:** "Create proposal for [client]," "Pitch deck," "Quote for [project]"

---

### n8n Automation Build
**Frequency:** Per client project | **Value:** Productizable IP

Phases: Requirements → Workflow architecture → Build in n8n → Test with sample data → Error handling → Documentation → Handoff

**Triggers:** "Build automation for [process]," "n8n workflow," "Automate [task]"

---

### Content Batch Production
**Frequency:** Weekly/Monthly | **Value:** Brand building

Phases: Content pillars/themes → Batch ideation (10-30 posts) → Copy generation → Visual creation (Canva/AI) → Scheduling → Hashtag sets

**Triggers:** "Batch Instagram content," "Create posts for [brand]," "Social content for the month"

---

### Due Diligence Research
**Frequency:** Per opportunity | **Value:** Risk mitigation

Phases: Initial research (web, LinkedIn, public records) → Business model analysis → Red flag identification → Competitive landscape → Summary/recommendation

**Triggers:** "Research [company/person]," "Due diligence on [opportunity]," "Vet this"

---

### Creator Accelerator
**Frequency:** Per creator client | **Value:** High-ticket consulting

Phases: Content capture (transcription, organization) → Structure/architecture → Assessment (publisher, market) → Platform research → Infrastructure (landing page, lead capture, voice AI) → Go-to-market assets

**Triggers:** "Turn notes into a book," "Build author platform," "Creator wants to productize"

---

### Brand-to-Workflow Mapping

| Brand | Primary Workflows |
|-------|-------------------|
| Sax By Dennison | Wedding leads, booking, performance prep |
| Blues Prince Media | Client accelerator, voice agent, automations |
| Ella Gant | Product development, beta onboarding |
| Personal | Due diligence, content, pitch building |

---

## 3. Skill Template

### Folder Structure
```
skill-name/
├── SKILL.md              ← Required: Main instructions
├── scripts/              ← Optional: Executable code
├── references/           ← Optional: Deep documentation
└── assets/               ← Optional: Templates, prompts, files
```

### SKILL.md Skeleton
```markdown
---
name: [skill-name]
description: [What it does]. [When to use — be specific]. Use when [trigger 1], [trigger 2], or [trigger 3].
---

# [Skill Name]

[One sentence overview]

## When to Use
- [Trigger phrase 1]
- [Trigger phrase 2]
- [Context that activates]

## Workflow

### Phase 1: [Name]
[Steps]

### Phase 2: [Name]
[Steps]

## Output Checklist
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

## Quality Checks
- [ ] [Check 1]
- [ ] [Check 2]
```

### Component Extraction Guide

| Created During Convo | Destination | Example |
|---------------------|-------------|---------|
| Prompts for external tools | `assets/` | `retell-prompt-template.md` |
| Pricing/comparison tables | `references/` | `voice-ai-pricing.md` |
| Frameworks/methodologies | `references/` | `nlp-quote-mapping.md` |
| Step-by-step processes | `SKILL.md` | Main workflow section |
| Reusable templates | `assets/` | `assessment-template.md` |
| Scripts/code | `scripts/` | `generate_pdf.py` |

---

## 4. Description Writing Guide

The description is the ONLY thing Claude sees before loading the skill. Make it count.

**Include:**
- What the skill does (capability)
- When to use it (triggers)
- Specific phrases that should activate it
- Be "pushy" — combat Claude's tendency to under-trigger

**Good example:**
```
Build complete voice AI assistants for businesses. Handles pricing comparison,
platform selection, prompt engineering, and integration setup. Use when user
mentions "voice assistant," "AI receptionist," "Retell," "Vapi," or "phone automation."
```

**Bad example:**
```
Helps with voice stuff.
```

### Trigger Phrase Generation (5-10 per skill)

1. Direct request: "Create a [thing]"
2. Problem statement: "I need to [outcome]"
3. Tool mention: "Help me with [tool name]"
4. Context mention: "I have a client who..."
5. Process request: "Walk me through [workflow]"
6. Handoff language: "Set up [system] for me"

### Testing Before Package

1. **Trigger test:** Would the description catch the right requests?
2. **Completeness test:** Does SKILL.md cover the full workflow?
3. **Reusability test:** Works for similar-but-different cases?
4. **Asset test:** All referenced files present?
5. **Clarity test:** Could another Claude instance follow this?
