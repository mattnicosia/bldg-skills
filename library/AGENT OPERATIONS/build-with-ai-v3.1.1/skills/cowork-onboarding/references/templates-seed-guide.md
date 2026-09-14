# Templates Seed Guide

Starter template catalog and structures for seeding the TEMPLATES/ folder during onboarding. Read this before offering template seeding in the Completion section.

---

## When to Seed Templates

Template seeding happens during the Completion section of onboarding, after the user has completed their setup. Only offer if:

1. TEMPLATES/ folder exists and is empty
2. The user completed Full Setup (or has a workspace with TEMPLATES/)
3. The user agrees when asked via AskUserQuestion

Never seed if templates already exist (check `ls TEMPLATES/` first). Never force templates — always let the user pick which ones to install.

## Template Catalog by Role

Map the user's role (captured during the context file interview or Quickstart) to recommended starter templates:

| Role | Templates to Offer |
|------|--------------------|
| Consultant/Advisor | `client-proposal.md`, `meeting-notes.md`, `project-brief.md` |
| Agency Owner | `client-brief.md`, `campaign-report.md`, `content-calendar.md` |
| E-commerce/Product | `product-listing.md`, `email-campaign.md`, `competitor-analysis.md` |
| Content Creator | `article-outline.md`, `social-post.md`, `newsletter-issue.md` |
| Freelancer/Solopreneur | `project-proposal.md`, `invoice-cover.md`, `weekly-review.md` |
| General/Other | `meeting-notes.md`, `project-brief.md`, `weekly-review.md` |

## Template Structures

Each template should be minimal but useful — section headers with brief guidance comments and placeholder text.

### meeting-notes.md
```markdown
# Meeting Notes — [Meeting Name]

**Date:** [Date]
**Attendees:** [Names]
**Purpose:** [1-sentence meeting objective]

## Key Discussion Points
- [Topic 1]: [Summary]
- [Topic 2]: [Summary]

## Decisions Made
- [Decision]: [Owner] — [Deadline if applicable]

## Action Items
- [ ] [Task] — [Owner] — [Due date]
- [ ] [Task] — [Owner] — [Due date]

## Follow-Up
[Next meeting date, any prep needed, or next steps]
```

### project-brief.md
```markdown
# Project Brief — [Project Name]

## Overview
[2-3 sentences: what this project is and why it matters]

## Objectives
- [Primary goal]
- [Secondary goal]

## Scope
**In scope:** [What's included]
**Out of scope:** [What's explicitly excluded]

## Key Stakeholders
- [Name] — [Role/responsibility]

## Timeline
- **Start:** [Date]
- **Key milestones:** [List]
- **Deadline:** [Date]

## Success Criteria
[How we'll know this project is done and done well]

## Reference Materials
[Links or file paths to relevant docs, research, past work]
```

### client-proposal.md
```markdown
# Proposal — [Client Name]

**Prepared by:** [Your name]
**Date:** [Date]

## The Challenge
[2-3 sentences describing the client's problem or opportunity]

## Proposed Solution
[What you'll do, at a high level]

## Approach
1. [Phase/Step 1] — [Brief description]
2. [Phase/Step 2] — [Brief description]
3. [Phase/Step 3] — [Brief description]

## Deliverables
- [Deliverable 1]
- [Deliverable 2]

## Timeline
[Expected duration, key milestones]

## Investment
[Pricing structure — fixed, hourly, retainer, etc.]

## Why Us
[1-2 sentences on what makes you the right fit]

## Next Steps
[Clear call to action — what happens if they say yes]
```

### client-brief.md
```markdown
# Client Brief — [Client Name]

## Client Overview
**Business:** [What they do]
**Industry:** [Sector]
**Size:** [Team size, revenue range if known]
**Website:** [URL]

## Project Context
[Why they're engaging you — what triggered this work]

## Objectives
- [What they want to achieve]

## Target Audience
[Who the work is for — their customers, users, stakeholders]

## Brand Guidelines
[Key brand rules, tone, visual direction — or link to brand docs]

## Constraints
- **Budget:** [If known]
- **Timeline:** [Deadlines]
- **Technical:** [Platform requirements, integrations, etc.]

## Key Contacts
- [Name] — [Role] — [Email/phone]
```

### campaign-report.md
```markdown
# Campaign Report — [Campaign Name]

**Period:** [Start date] — [End date]
**Prepared by:** [Your name]

## Campaign Overview
[1-2 sentences: what was the campaign and what was it trying to achieve]

## Results Summary
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| [Metric 1] | [Target] | [Actual] | [On track / Above / Below] |
| [Metric 2] | [Target] | [Actual] | [On track / Above / Below] |

## What Worked
- [Insight 1]
- [Insight 2]

## What Didn't Work
- [Issue 1 — and what to do differently]

## Recommendations
- [Next step 1]
- [Next step 2]
```

### content-calendar.md
```markdown
# Content Calendar — Week of [Date]

## Monday
- **Platform:** [LinkedIn / X / Instagram / etc.]
- **Topic:** [Subject]
- **Format:** [Post / Article / Carousel / Video]
- **Status:** [ ] Draft  [ ] Review  [ ] Scheduled  [ ] Published

## Tuesday
[Same structure]

## Wednesday
[Same structure]

## Thursday
[Same structure]

## Friday
[Same structure]

## Notes
[Themes for the week, any tie-ins to events or launches]
```

### product-listing.md
```markdown
# Product Listing — [Product Name]

## Title
[Optimized product title — include key search terms]

## Bullet Points
1. [Key benefit — lead with the outcome, not the feature]
2. [Key benefit]
3. [Key benefit]
4. [Key benefit]
5. [Key benefit]

## Description
[2-3 paragraphs: what it is, who it's for, why it's better]

## Search Terms
[Backend keywords — comma-separated]

## Images Needed
- Hero shot: [Description]
- Lifestyle: [Description]
- Detail: [Description]
- Infographic: [Description]

## Pricing
**Price:** [Amount]
**Competitor range:** [Low] — [High]
```

### email-campaign.md
```markdown
# Email Campaign — [Campaign Name]

**Goal:** [What this campaign achieves]
**Audience:** [Who receives it]
**Trigger:** [What starts the sequence — sign-up, purchase, date, etc.]

## Email 1: [Subject Line]
**Send:** [Timing — immediately, day 1, etc.]
**Purpose:** [What this email does]
**Body outline:**
- [Opening hook]
- [Main content]
- [CTA]

## Email 2: [Subject Line]
**Send:** [Timing]
**Purpose:** [What this email does]
**Body outline:**
- [Opening hook]
- [Main content]
- [CTA]

## Email 3: [Subject Line]
[Same structure]
```

### competitor-analysis.md
```markdown
# Competitor Analysis — [Your Product/Service]

**Date:** [Date]
**Analyst:** [Your name]

## Competitors Reviewed
1. [Competitor 1]
2. [Competitor 2]
3. [Competitor 3]

## Comparison Matrix
| Feature | Us | [Comp 1] | [Comp 2] | [Comp 3] |
|---------|-----|----------|----------|----------|
| [Feature 1] | [Status] | [Status] | [Status] | [Status] |
| [Feature 2] | [Status] | [Status] | [Status] | [Status] |
| **Price** | [Price] | [Price] | [Price] | [Price] |

## Key Insights
- [What competitors do well that we don't]
- [Where we have an advantage]
- [Gaps in the market nobody's filling]

## Recommendations
- [Action item based on findings]
```

### article-outline.md
```markdown
# Article Outline — [Working Title]

**Target audience:** [Who this is for]
**Goal:** [What the reader should think/feel/do after reading]
**Target length:** [Word count]
**Platform:** [Blog / LinkedIn / X / Newsletter]

## Hook
[Opening line or angle that grabs attention]

## Main Argument
[1-2 sentences: the core thesis]

## Section 1: [Heading]
- [Key point]
- [Supporting evidence or example]

## Section 2: [Heading]
- [Key point]
- [Supporting evidence or example]

## Section 3: [Heading]
- [Key point]
- [Supporting evidence or example]

## Conclusion / CTA
[What you want the reader to do next]

## SEO Notes (if applicable)
**Primary keyword:** [Keyword]
**Secondary keywords:** [Keywords]
```

### social-post.md
```markdown
# Social Post — [Platform]

**Date:** [Date]
**Topic:** [Subject]

## Hook (first line)
[The line that stops the scroll]

## Body
[Main content — value, story, or insight]

## CTA
[What you want the reader to do]

## Hashtags / Tags
[If applicable]

## Visual Direction
[Image, carousel, or video description if needed]
```

### newsletter-issue.md
```markdown
# Newsletter — [Issue Title]

**Issue #:** [Number]
**Send date:** [Date]
**Subject line:** [Subject]
**Preview text:** [First line visible in inbox]

## Intro
[Personal opening — 2-3 sentences connecting to the reader]

## Main Content
### [Section 1 Heading]
[Content]

### [Section 2 Heading]
[Content]

## Quick Hits / Links
- [Resource 1]: [Why it matters]
- [Resource 2]: [Why it matters]

## CTA
[One clear ask — reply, click, share, etc.]

## Sign-off
[Personal closing]
```

### project-proposal.md
```markdown
# Project Proposal — [Project Name]

**Prepared for:** [Client/self]
**Date:** [Date]

## Problem
[What problem are we solving? Why now?]

## Proposed Solution
[High-level approach in 2-3 sentences]

## Scope of Work
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

## Timeline
| Phase | Duration | Deliverable |
|-------|----------|-------------|
| [Phase 1] | [Duration] | [What's delivered] |
| [Phase 2] | [Duration] | [What's delivered] |

## Investment
[Cost breakdown]

## Next Steps
[What happens if approved]
```

### weekly-review.md
```markdown
# Weekly Review — Week of [Date]

## Wins
- [What went well this week]

## Completed
- [x] [Task completed]
- [x] [Task completed]

## In Progress
- [ ] [Task still underway] — [Status/blockers]

## Pushed / Deprioritized
- [ ] [Task that got bumped] — [Why]

## Next Week's Priorities
1. [Top priority]
2. [Second priority]
3. [Third priority]

## Notes
[Anything else worth remembering — insights, ideas, follow-ups]
```

### invoice-cover.md
```markdown
# Invoice Cover — [Client Name]

**Invoice #:** [Number]
**Date:** [Date]
**Period:** [Service period]

## Summary of Work
[Brief description of what was delivered during this billing period]

## Line Items
| Description | Hours/Units | Rate | Total |
|-------------|-------------|------|-------|
| [Service 1] | [Amount] | [Rate] | [Total] |
| [Service 2] | [Amount] | [Rate] | [Total] |
| **Total** | | | **[Grand total]** |

## Payment Terms
[Due date, payment methods, late fee policy if any]

## Notes
[Any additional context — upcoming work, changes to scope, etc.]
```

## CONTEXT/ Auto-Seeded Templates

Separate from the TEMPLATES/ catalog above, the cowork-onboarding skill also auto-seeds certain files into `CONTEXT/` when they are missing at the end of onboarding. These are not user-pick — they are required for downstream skills to function and are seeded automatically.

### voc.md (Voice of Customer)

**Seed when:** No `voc.md` exists in CONTEXT/ at the end of onboarding.
**Seed contents:** The empty VOC template with the `ASSUMPTION-BASED VOC - replace with real quotes` header. Operator fills in real buyer language as it accumulates.
**Why seed it empty:** The agent needs the file to exist for prime to load it. Empty-with-header is better than missing — the staleness reporting flags it on every session start, prompting the operator to fill it in.

## Seeding Rules

1. **Only offer templates for TEMPLATES/ if the folder exists**
2. **Never seed if templates already exist** — check `ls TEMPLATES/` first
3. **Present the list and let the user pick** which ones to install via AskUserQuestion (multiSelect)
4. **Always explain:** "These are starter templates. Claude uses them as structural patterns — studying the format before creating similar content. You can edit them, add your own, or delete any that don't fit."
5. **Use the naming convention:** `template_content-type.md` or just the descriptive name as shown above
6. **Match to role:** Only present templates relevant to the user's stated role/business type
