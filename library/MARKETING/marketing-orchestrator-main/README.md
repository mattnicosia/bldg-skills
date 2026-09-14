# Marketing Orchestrator

> An AI-powered marketing skill for freelance and solo marketers. One entry point. Six specialist
> routes. Built to think, route, self-correct, and get better with every use.

Built by Bryan Engel / [Opti-Flow.AI](https://opti-flow.ai)

---

## What It Does

The Marketing Orchestrator is a Claude skill that handles every marketing task a solo marketer
needs — without switching tools, repeating context, or starting from scratch each session.

You describe what you need. It gathers just enough context, routes to the right specialist,
evaluates the output before you see it, and logs what happened so it can improve over time.

---

## Six Specialist Routes

| Route | What It Handles |
|---|---|
| **Brand Strategy and ICP** | Ideal customer profiles, positioning, messaging frameworks, brand voice guides — with downloadable Word doc output |
| **Ad Copy and Paid Media** | Google Ads, Meta Ads, LinkedIn Ads, landing page copy, A/B variants with platform-accurate character counts |
| **Content Creation** | Blog posts, LinkedIn posts, Instagram captions, email sequences, content calendars |
| **Repurpose** | Rebuilds one piece of content natively across multiple channels — not truncated, fully rewritten per platform |
| **Campaign Mode** | Architecture-first campaign planning — builds all deliverables in funnel sequence with a connecting thread and launch checklist |
| **GitHub Deploy** | Full setup walkthrough from account creation through ongoing push workflow — designed for non-developers |

---

## How It Gets Better Over Time

Every session is logged automatically in `references/revision-log.md`. The log captures intake
gaps, quality flags, and suggested improvements from real usage. Every third session, the skill
surfaces a reminder to run a revision pass. One command reads the log, finds the most repeated
pattern, proposes a specific fix, and updates the right sub-skill after your approval.

The skill also self-evaluates every output before delivery against a five-category rubric
(audience fit, clarity, voice, platform format, goal alignment) and silently fixes issues before
you see them. Every response ends with a quality check signal so you know it's working.

---

## Client Memory

Client context is saved to `references/client-profiles/` after the first session. Returning
clients are recognized automatically — intake questions already answered by the profile are
skipped. Profile data is updated at the end of every session when new information surfaces.

---

## File Structure

```
marketing-orchestrator/
├── SKILL.md                          ← Orchestrator: intake, routing, self-eval, revision loop
├── README.md                         ← This file
├── references/
│   ├── revision-log.md               ← Session log and version history
│   └── client-profiles/
│       └── README.md                 ← Profile template and instructions
└── sub-skills/
    ├── brand-strategy-icp/SKILL.md
    ├── ad-copy-paid-media/SKILL.md
    ├── content-creation/SKILL.md
    ├── repurpose/SKILL.md
    ├── campaign-mode/SKILL.md
    └── github-deploy/SKILL.md
```

---

## Installation

This skill is built for [Claude.ai](https://claude.ai) with the Skills feature enabled.

1. Download or clone this repository
2. Install the skill via the Claude Skills interface
3. Start any session with a marketing request — the orchestrator handles the rest

---

## Competition Entry

This skill was submitted to the Claude Skills Competition by Bryan Engel.

**Description:** The Marketing Orchestrator is a self-improving AI skill built for freelance
marketers who need a single intelligent system to handle every marketing task — from brand
strategy and ad copy to full campaign sequencing and content repurposing. It remembers your
clients, routes every request to the right specialist automatically, self-evaluates output
before you ever see it, and gets sharper with every use through a built-in revision loop.
Your work stays organized and version-controlled in GitHub from day one.

**Key benefits:**
- One skill, every marketing task — no context switching, no repeated setup
- Remembers clients and improves over time through a structured revision loop
- Work is organized and version-controlled in GitHub from the first session

---

## License

MIT License — free to use, adapt, and build on.
