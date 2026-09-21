# Skills & Plugins Guide

How skills and plugins work, recommendation matrix by role, and first-use prompts. Read this before running the Install Skills capability.

---

## What Skills Are

Skills are specialized instruction sets that make Claude an expert at specific tasks. When a skill triggers, Claude reads its instructions and follows them — producing higher-quality, more structured output than a generic prompt would.

Skills are organized into plugins (bundles of skills, commands, and connectors for a specific role or function).

## How to Discover Skills

Three discovery methods — use all three during Capability 4:

1. **Check what's already installed.** The `available_skills` list in the session shows all skills the user currently has. Review it and explain what each does.

2. **Live plugin search (primary).** Use `search_plugins` with keywords matching the user's role and needs. This searches the plugin marketplace for installable bundles. **Always prioritize live search results over the static matrix below** — the marketplace changes faster than this reference file.

3. **Static recommendation matrix (secondary).** Use the matrix below as a starting point. Cross-reference against live search results:
   - If search_plugins returns results NOT in the matrix, present them as "Recently added" or "New since last update"
   - If the matrix recommends something search_plugins can't find, note it may have been renamed or removed

## Recommendation Matrix — Last Updated: 2026-03-11

> This matrix is a starting point. Capability 4 always runs live plugin discovery alongside these static recommendations. If you're maintaining this plugin, update this matrix when major new plugins ship or existing ones change significantly.

### Content Creators / Marketers
| Need | Recommended Skill | What It Does |
|------|-------------------|-------------|
| Brand voice | brand-voice | Extract or build consistent brand voice profiles |
| LinkedIn posts | linkedin-content | Data-backed frameworks for posts, carousels, comments, connections, follow-ups |
| X/Twitter articles | x-content | Article structures, headline patterns, cross-platform repurposing |
| Podcast/YouTube | podcast-youtube | Complete workflows: research, pitching, titles, thumbnails, promos, orchestration |
| Email campaigns | email-marketing | Email sequence frameworks and templates |
| Direct response | direct-response | Landing pages, sales copy, hook formulas |
| Content engine | content-engine | Repurpose across all platforms systematically |
| AI creative | ai-creative | Creative copy, storytelling frameworks |
| SEO content | seo-content | Blog posts optimized for search + ranking |

### Podcast Hosts & YouTube Creators
| Need | Recommended Skill | What It Does |
|------|-------------------|-------------|
| Guest research + pitching | podcast-youtube | Research, pitch, score, and rank potential guests |
| Episode titles | podcast-youtube | Research-backed title patterns with scoring (A-J templates) |
| Thumbnail briefs | podcast-youtube | AI-prompt-ready thumbnail formulas for ThumbnailMaker.ai |
| Promo emails | podcast-youtube | Email templates for promoting new episodes |
| Guest outreach | podcast-youtube | Email, X, LinkedIn templates (all generalized) |
| Production workflow | podcast-youtube | Full orchestration: who → when → what skill to run |
| Content mining | podcast-youtube | Extract X articles, LinkedIn posts, newsletters from transcripts |
| Brand voice | brand-voice | Ensure all intro scripts, descriptions match your tone |

### E-Commerce / Amazon Sellers
| Need | Recommended Skill | What It Does |
|------|-------------------|-------------|
| Product content | brand-voice | Consistent voice across listings and descriptions |
| Social selling | linkedin-content | Create carousel content for product launches |
| Email marketing | email-marketing | Customer nurture sequences, promotional campaigns |

### Consultants / Agencies
| Need | Recommended Skill | What It Does |
|------|-------------------|-------------|
| Client brand voice | brand-voice | Build voice profiles for client brands |
| Content strategy | content-engine | Multi-platform content calendars and repurposing |
| Client emails | email-marketing | Sequence templates for nurture, sales, onboarding |
| Case studies | linkedin-content | LinkedIn-optimized case study posts and carousels |

### Technical Builders
| Need | Recommended Skill | What It Does |
|------|-------------------|-------------|
| Personal brand | brand-voice | Create voice profile for your thought leadership |
| Technical writing | x-content | Turn complex concepts into articles |
| Product launch | podcast-youtube | Guest research to get interviews for product/launch |
| Community building | linkedin-content | Build network through comments and connections |

### General Business / Operations
| Need | Recommended Skill | What It Does |
|------|-------------------|-------------|
| Consistent communication | brand-voice | Foundation for all content across channels |
| Email marketing | email-marketing | Marketing, sales, and operational sequences |
| Scheduling | (native Cowork) | Create recurring automated tasks |

## Recommended Skill Installation Order

**Phase 1 (Foundation — Install First):**
1. brand-voice — Creates the voice all other skills reference
2. build-with-ai — Completes your setup (you already have this)

**Phase 2 (Content Creation — Install Based on Your Channels):**
- LinkedIn creator? → linkedin-content
- X/Twitter writer? → x-content
- Podcast/YouTube producer? → podcast-youtube
- Email marketer? → email-marketing
- Blog writer? → seo-content
- Sales/landing pages? → direct-response

**Phase 3 (Enhancement — Build on Foundation):**
- All channels? → content-engine (repurposing engine)
- Creative/storytelling? → ai-creative
- Multiple content types? → Install Phase 2 skills as needed

## Anthropic Official Plugins

These are the major plugin categories Anthropic has shipped. Search for them using `search_plugins`:

- **Productivity** — task management, calendars, daily workflows
- **Marketing** — content drafting, campaign planning, brand voice
- **Sales** — account research, call prep, outreach, battlecards
- **Finance** — financial modeling, analysis, reporting
- **Data Analysis** — SQL, dashboards, dataset exploration
- **Legal** — contract review, research, drafting
- **Product Management** — specs, roadmaps, user stories
- **Customer Support** — ticket handling, response drafting
- **Enterprise Search** — search across connected tools
- **Biology Research** — scientific literature and data

## First-Use Prompts

After installing a skill, suggest one of these so the user can see it in action:

| Skill | First Prompt to Try |
|-------|-------------------|
| pptx | "Create a 5-slide presentation about [their business] for [their audience]." |
| docx | "Write a one-page [proposal/report/memo] about [relevant topic]." |
| xlsx | "Create a spreadsheet that tracks [something relevant to their business]." |
| Brand Voice | "Run /brand-voice:discover-brand to find my existing brand materials." |
| Skill Creator | "I want to create a skill that helps me [their described workflow]." |
| Schedule | "Help me set up a morning briefing task that runs every weekday at 8 AM." |

## Tips for the Onboarding Flow

- **Don't overwhelm with options.** Recommend 2-3 skills max based on their stated needs. They can discover more later.
- **Show concrete value.** For each recommendation, give a specific example of how it helps their business — not abstract feature descriptions.
- **Document-creation skills are universal.** Almost everyone benefits from pptx, docx, xlsx, and pdf. Suggest these as a baseline if nothing else is relevant.
- **Note unmet needs.** If the user describes a workflow need that no existing skill covers, acknowledge it and suggest the Skill Creator for building a custom one.
- **Explain slash commands.** After installing, tell the user they can type "/" in any Cowork chat to see available commands from their installed skills.
- **Live search trumps static.** If search_plugins returns something not in the matrix above, trust the live results.
