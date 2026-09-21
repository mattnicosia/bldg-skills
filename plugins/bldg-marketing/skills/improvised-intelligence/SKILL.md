---
name: improvised-intelligence
description: "Full-stack client acquisition and delivery engine. Combines competitive research, brand strategy, personalized sales pitches, operational agent architecture, and self-improving workflow capture into one unified system. Use when: prospecting a new client ('pitch [company]', 'run [business] through the system'), onboarding a client ('build brand book for [client]', 'onboard [company]'), setting up AI operations ('build agent system', 'create my boardroom', 'set up my AI team'), or when any multi-phase client workflow completes and should be captured as a repeatable process. Also triggers on: 'improvised intelligence', 'full client pipeline', 'prospect to operations', 'S.O.U.L. system', 'brand book', 'agent architecture', 'boardroom protocol', or 'capture this workflow'. This is the mega-skill — if a task touches client acquisition, brand building, operational AI, or workflow systematization, start here."
---

# Improvised Intelligence

A unified engine that takes a business from cold prospect to fully operationalized client — with self-improving workflow capture at every stage. Built by Blues Prince Media.

## System Overview

This skill orchestrates four interconnected phases:

```
PROSPECT → PITCH → BRAND → OPERATE → [CAPTURE]
   ↓          ↓        ↓         ↓          ↓
 Research   S.O.U.L.  Brand    Agent     Workflow
 & Recon    Pitch     Book     System    Spotter
            System    Builder  (Calvin)  (Meta)
```

**Phase 1: PROSPECT** — Competitive intelligence and market research on a target business
**Phase 2: PITCH** — Personalized S.O.U.L. pitch with 5 deliverables that close the deal
**Phase 3: BRAND** — 8-phase guided brand book creation that becomes the strategy foundation
**Phase 4: OPERATE** — Deploy an AI agent team (Calvin Boardroom Protocol) to run ongoing operations
**Phase 5: CAPTURE** — Detect repeatable patterns and auto-generate new skills from completed work

Each phase can run independently or chain together. The skill detects which phase is needed based on context.

---

## Phase Detection

Read the user's request and match to the appropriate entry point:

| User Says | Phase | Action |
|-----------|-------|--------|
| "Pitch [company]" / "Run [X] through the system" | PROSPECT → PITCH | Start with research, build full pitch |
| "Create a brand book for [client]" | BRAND | Jump to guided discovery |
| "Build me an agent system" / "Set up my boardroom" | OPERATE | Jump to Calvin architecture |
| "Onboard [client]" / "Full pipeline for [company]" | ALL | Run Phases 1-4 sequentially |
| *(auto-detected at conversation end)* | CAPTURE | Evaluate workflow for skill creation |

If the request is ambiguous, ask one clarifying question:
> "Are we prospecting, onboarding, or building operations?"

---

## Phase 1: PROSPECT — Competitive Intelligence

**Goal:** Build a complete dossier on the target business before creating any pitch materials.

### Step 1: Business Recon
Search for and document:
- Business name, location, years operating
- Google Business rating + review count
- Website quality assessment (load speed, mobile, SEO basics)
- Social media presence (platforms, follower counts, posting frequency)
- Service offerings and visible pricing
- Unique positioning signals (women-owned, family-run, awards, certifications)

### Step 2: Competitive Landscape
- Identify 3-5 direct competitors in their market
- Document competitor positioning, pricing, review counts
- Find the gaps — what competitors do vs. what this business does differently
- Identify the prospect's "unclaimed lane"

### Step 3: Search Landscape
- Research what customers search when looking for this service
- Estimate monthly search volumes for 5-10 key terms
- Identify who currently ranks for these terms
- Map the visibility gap between experience quality and online presence

### Step 4: Pain Point Mapping
- If a conversation happened, note specific pain points mentioned
- Cross-reference with common industry pain points:
  - Slow season anxiety
  - Inconsistent bookings/leads
  - Time spent on marketing vs. core work
  - Wanting customers to come to them (not chasing)
  - Online presence doesn't match in-person quality

### Output: Prospect Dossier
Save all findings as structured data. This feeds directly into Phase 2.

---

## Phase 2: PITCH — S.O.U.L. System

**Goal:** Create a personalized, research-backed pitch that positions Blues Prince Media as the obvious choice.

> Read `references/soul-pitch-details.md` for full landing page templates, Loom scripts, and PDF specifications.

### The S.O.U.L. Framework

| Letter | Pillar | In Practice |
|--------|--------|-------------|
| **S** | Strategy | Reverse engineer the ideal customer — who, what, where |
| **O** | Optimization | Show up where customers search — Google, social, everywhere |
| **U** | Unique Edge | Name what makes them different. Make it the reason customers choose them |
| **L** | Leverage | Build systems — content that works while they sleep |

### Deliverable Checklist

Create all five:

- [ ] **90-Day Content Calendar PDF** — Month-by-month posting plan with platform-specific schedules, content themes tied to business goals, specific post ideas with hooks, hashtag strategy, and optimal posting times for their industry
- [ ] **Brand Positioning Worksheet PDF** — Discovery questions across 5 sections (Business, Ideal Customer, Brand Voice, Practical Info, Open-Ended). Closeable with: "Once I have this + access to your photo/video files, I can start immediately."
- [ ] **Market Snapshot & Analysis PDF** — Header stats (rating, reviews, years), What You've Built, The Visibility Gap, What Customers Search, Competitive Edge, Bottom Line
- [ ] **Personalized Landing Page** — 7-section structure: Hero (pain point headline), S.O.U.L. System intro, Research findings, Competitive edge, Free resources, CTA, Questionnaire. See `references/soul-pitch-details.md` for section-by-section copy templates.
- [ ] **Loom Script** — Sub-2-minute video script with 7-beat structure: warm greeting → curiosity gap → callback → the gift → light insight → value framing → soft CTA. Three tone variants available: warm lead (met in person), referral, cold outreach.

### Loom Script Embedded Commands

Weave these phrases naturally into the script:
- "I want you to take a look at..."
- "When you see it laid out..."
- "When you're ready..."

### PDF Generation

Use ReportLab with this color palette:
```python
NAVY = '#1a365d'
CORAL = '#e85a4f'
TEAL = '#319795'
LIGHT_GRAY = '#f7f7f7'
DARK_TEXT = '#2d3748'
```

All PDFs include footer: `Blues Prince Media • dennison@bluesprincemedia.com • bluesprincemedia.com`

---

## Phase 3: BRAND — Brand Book Builder

**Goal:** Walk the client through an 8-phase guided discovery process that produces a complete brand identity system.

> Read `references/brand-book-details.md` for discovery questions, example output (ShadeScapes), and quality checks.

### Critical Rule: Lock Incrementally

**Do NOT skip phases. Do NOT assume answers.** Each phase must be confirmed by the client before moving to the next. This is a consultative process, not a template fill.

### The 8 Phases

**Phase 3.1: Discovery**
Ask conversationally (not all at once). Cover:
- Business fundamentals (what, how long, differentiator, what they're NOT)
- Customer understanding (avatar types, emotional state, transformation)
- Aspirational positioning (admired brands, brand-as-person, target feeling)

**Phase 3.2: Mission Statement**
Formula: `[Company] [action verb] [what they offer] that [key benefits] — [outcome/impact]`
- Draft 2-3 versions → present → refine → lock
- Quality: internal-facing, purpose-driven, timeless

**Phase 3.3: Brand Promise**
A paragraph answering: "What can customers COUNT on every time?"
- Opens with commitment → describes experience → states quality → closes with outcome
- Quality: customer-facing, specific, deliverable, accountable

**Phase 3.4: Tagline System**
Develop 2-4 taglines:

| Type | Purpose |
|------|---------|
| Primary | Universal, all audiences |
| Emotional | Feeling-based, lifestyle |
| Authority | Category ownership |
| Seasonal/Campaign | Time-limited pushes |

Generate 5-10 per category → test against positioning → present top 3 → lock.

**Phase 3.5: Voice & Tone**
- Create voice equation: `[Aspirational brand] + [key modifier] = [This brand]`
- Define 5 core voice attributes with practical meaning
- Compile word banks: excellence words (10-15), sophistication words (10-15), brand-specific phrases (5-10)

**Phase 3.6: Vocabulary Rules**
"Never Say / Say Instead" table based on:
- Industry commodity language to avoid
- Elevated alternatives that reinforce positioning
- Client-specific preferences from discovery

**Phase 3.7: Avatar Phrase Banks**
For each customer type: name it → identify 3-5 emotional drivers → research their language → build phrase banks:
- Headlines & hooks (7-15)
- Body copy language (5-10)
- Pain points addressed (table format)
- Avatar-specific taglines (2-4)
- Product descriptors (2-3)
- CTAs (3-5)

**Phase 3.8: Compile & Deliver**
Generate final deliverables:
1. **Brand Book PDF** — mission, promise, taglines, voice/tone, vocabulary, avatar phrase banks, quick reference
2. **Avatar Phrase Banks PDF** — standalone marketing reference
3. **Interactive Dashboard** (optional React artifact) — tabbed interface for client to explore their brand system

Use PDF skill with brand colors (navy #1a365d, gold #b8860b default, or client brand colors).

---

## Phase 4: OPERATE — Calvin Boardroom Protocol

**Goal:** Deploy a two-layer AI agent system that runs ongoing operations for the client's business.

> Read `references/calvin-architecture.md` for the full SOP, agent templates, and memory architecture.

### Architecture Overview

```
┌─────────────────────────────────────┐
│        🏛️ THE BOARDROOM              │
│  Strategy layer (never client-facing)│
│                                      │
│  Chief of Staff  •  CTO  •  CMO     │
│  CFO  •  CCO  •  COO                │
└──────────────┬───────────────────────┘
        DELEGATE ↓ ↑ ESCALATE
┌──────────────┴───────────────────────┐
│        🏢 THE DEPARTMENTS             │
│  Operations layer (client-facing)    │
│                                      │
│  One agent per business vertical     │
│  No lateral communication            │
│  Escalate through Boardroom          │
└──────────────────────────────────────┘
```

### Setup Workflow

**Step 1: Define Verticals**
- List client's business units/verticals (max 8 departments recommended)
- Name each department agent
- Define scope and out-of-scope for each

**Step 2: Configure Boardroom**
Six executive agents using this template structure:
```
Agent Name | Role | Responsibilities | Decision Authority
```
Standard roster: Chief of Staff, CTO, CMO, CFO, CCO, COO

**Step 3: Build Agent Contexts**
For each agent, generate a system prompt using layer-appropriate templates:

*Boardroom template essentials:*
- Layer declaration (BOARDROOM / Executive)
- 3-5 specific responsibilities
- Full peer roster
- Department roster for delegation
- Protocol tags: CONSULT, ROUTE, SPAWN, LEARN
- Decision authority (autonomous vs. confirm with CEO)

*Department template essentials:*
- Layer declaration (DEPARTMENT / Operational)
- Business key and scope
- Escalation map to specific Boardroom agents
- Rules: no lateral communication, escalate cross-vertical to Chief of Staff

**Step 4: Memory Architecture**
Configure the Second Brain:
- Rules (always loaded, `master` key cascades to all agents)
- Facts (capped at 20 per call, sorted by recency)
- Vertical Memory (last 15 interactions per channel)
- Sensitive information protocol: never auto-learn financials, legal, health, tax details

**Step 5: Communication Rules**
- Boardroom ↔ Boardroom: ✅ (lateral consultation)
- Boardroom → Department: ✅ (delegation)
- Department → Boardroom: ✅ (escalation)
- Department → Department: ❌ (must route through Boardroom)

**Step 6: System Channels**
- `#coo-review` — COO posts reflective review recommendations for approval
- `#routing-log` — Audit trail of all cross-layer traffic

### COO Reflective Review

The COO agent has a meta-function: periodic system-wide performance review analyzing knowledge gaps, routing issues, contradictory facts, cross-vertical traffic patterns, and successful patterns. All recommendations require CEO approval before deployment.

---

## Phase 5: CAPTURE — Workflow Spotter

**Goal:** After completing any phase (or any complex conversation), detect repeatable patterns and offer to create new skills.

### Auto-Detection Triggers

Evaluate for skill-worthiness when ANY occur:
- 10+ back-and-forth exchanges on a single project
- 5+ tool calls in service of one outcome
- 3+ file outputs created
- Research → Analysis → Creation → Delivery arc completed
- User says "we should do this again" or "for next time"

### Detection Checklist

```
□ Was this more than simple Q&A?
□ Did it involve 3+ distinct phases?
□ Were reusable artifacts created?
□ Would the user likely do something similar again?
□ Could 50%+ of this work be systematized?
□ Did I figure things out future-Claude shouldn't rediscover?
```

If 3+ checked → suggest skill creation.

### Suggestion Format

```
---
**Workflow Pattern Detected**

We just completed a [WORKFLOW TYPE] workflow:
[PHASE 1] → [PHASE 2] → [PHASE 3] → [PHASE 4]

This looks repeatable. Want me to capture it as a skill?

**Suggested skill:** `[skill-name]`
**Would include:** [key components]
**Triggers:** "[phrase 1]," "[phrase 2]," "[phrase 3]"

I can build it now (5 min) or save for later.
---
```

### Known High-Value Patterns

| Pattern | Skill Name | Revenue Impact |
|---------|-----------|----------------|
| Client acquisition pipeline | `client-accelerator` | $5K+ per engagement |
| Podcast production | `podcast-workflow` | $5K/mo retainer |
| Voice AI assistant setup | `voice-agent-builder` | Productizable service |
| n8n automation build | `n8n-blueprints` | Productizable IP |
| Content batch production | `content-engine` | Brand building |
| Due diligence research | `due-diligence` | Risk mitigation |

### Skill Creation Workflow (When User Says Yes)

1. Confirm scope
2. Create folder structure: `skill-name/SKILL.md` + `references/` + `assets/`
3. Write SKILL.md with pushy description (combat under-triggering)
4. Extract reusable components (prompts → assets, tables → references, processes → SKILL.md)
5. Package and present

---

## Brand Voice (All Outputs)

All client-facing content follows Blues Prince Media voice:
- Confident but not arrogant
- Strategic, not just tactical
- "Scale without losing your soul"
- Sales-minded, not just content-focused
- Warm and human, not corporate
- Never state years of experience directly — build authority through stories
- Official title: "Dennison Blackett / Blues Prince CEO / Creative Futurist"
- All content includes `#bluesprincemedia` in hashtag sets
- Hooks provided by Dennison are used exactly as written — never modified

## LinkedIn Content Rules

When any output targets LinkedIn:
- Standard posts: 3,000 characters max (verify with `wc -c`)
- No markdown rendering — use plain text, line breaks, emojis sparingly
- Strong hook in first 2 lines (before "see more" fold)
- 3-6 hashtags at end, always include #bluesprincemedia
- Dennison's voice: punchy, contrarian, challenges starving artist narrative

---

## Output Quality Standards

Before delivering ANY output from any phase:

1. **Specificity check** — Does it reference the actual business, not generic placeholders?
2. **Research-backed** — Are claims supported by data found during recon?
3. **Actionable** — Does every section end with a clear next step?
4. **Brand-aligned** — Does it sound like Blues Prince Media, not generic consulting?
5. **Completeness** — Does it include all checklist items for that phase?

---

## Reference Files

Load these as needed based on active phase:

| File | When to Load | Contains |
|------|-------------|----------|
| `references/soul-pitch-details.md` | Phase 2 (PITCH) | Landing page section templates, Loom script templates (3 variants), PDF structure specs |
| `references/brand-book-details.md` | Phase 3 (BRAND) | Discovery questions, ShadeScapes example, avatar phrase bank format |
| `references/calvin-architecture.md` | Phase 4 (OPERATE) | Full agent SOP, context templates, memory architecture, troubleshooting |
| `references/workflow-patterns.md` | Phase 5 (CAPTURE) | Known BPM workflow patterns, skill template, detection priority matrix |
