# Use Cases & First Prompt Guide

Role-based example sessions, the one-prompt template, and AskUserQuestion teaching. Read this before running the "Your First Prompt" graduation step.

---

## The One-Prompt Template

This is the prompt pattern users should adopt for the majority of their Cowork tasks. It works because it combines three things: a clear task, folder context, and Claude asking the user questions before executing.

```
I want to [TASK] for [SUCCESS CRITERIA]. First, explore my folder.
Then, ask me questions using the AskUserQuestion tool.
I want to refine the approach with you before you execute.
```

### Why it works

- **"Explore my folder"** — Claude reads the context files, checks PROJECTS/ for relevant material, and reviews TEMPLATES/ for structural patterns before doing anything.
- **"Ask me questions using AskUserQuestion"** — Instead of the user writing a perfect prompt, Claude generates a clickable form asking the right questions. The user clicks answers in under a minute.
- **"Refine before you execute"** — Claude shows a plan. The user approves, tweaks, or redirects. Then Claude executes — creating real files in the OUTPUTS/ folder.

### Adapting the template

The template is flexible. Users can add specifics:

- **With a project reference:** "I want to write a follow-up email for the client-x project. Check PROJECTS/client-x/ for context. Ask me questions first."
- **With a template reference:** "I want to create a proposal using my proposal template in TEMPLATES/. Ask me questions first."
- **Quick version (for simple tasks):** "Draft a LinkedIn post about [topic]. Check my context files for voice, then go."

## What is AskUserQuestion?

AskUserQuestion is a built-in Cowork tool that generates interactive forms — clickable buttons, multi-select options, and ranking choices — right in the conversation.

### Why it matters

Traditional AI tools trained users to write longer, more detailed prompts. Cowork flips this: instead of the user explaining everything upfront, Claude asks the right questions. The user clicks through a form in 30-60 seconds, and Claude has everything it needs.

### How to trigger it

Users just include "use the AskUserQuestion tool" or "ask me questions first" in their prompt. Claude generates the form automatically.

### What it looks like in practice

User types: "I want to write my next newsletter. Ask me questions first."

Claude generates a form:
- "What's the topic?" [option A] [option B] [option C] [type your own]
- "Who's the audience?" [existing subscribers] [new readers] [both]
- "What tone?" [educational] [opinionated] [story-driven]
- "Target length?" [short: 500 words] [medium: 1000 words] [long: 2000+]

User clicks answers → Claude writes the newsletter.

## Use Cases by Role

### Content Creator: Writing a Newsletter

**What's in the folder:**
- CONTEXT/about-me.md, brand-voice.md, voc.md, working-style.md
- PROJECTS/newsletter/past-issues/ (3-4 top-performing past newsletters)
- TEMPLATES/newsletter-template.md (structure of a proven issue)

**The prompt:**
```
I want to write my next newsletter on [topic] for my subscriber list.
First, explore my folder — check my past issues and newsletter template.
Then, ask me questions using the AskUserQuestion tool.
I want to refine the approach with you before you execute.
```

**What happens:**
1. Claude reads `CONTEXT/about-me.md` and `CONTEXT/brand-voice.md` for voice and audience
2. Claude reads `CONTEXT/voc.md` to mirror buyer language and pull "Reuse these words" phrases
3. Claude reviews past newsletters for tone, structure, length patterns
4. Claude studies the newsletter template for structural patterns
5. Claude generates a form: topic angle, audience segment, tone, length, any specific points to hit
6. User clicks answers
7. Claude produces an outline for review
8. User approves or adjusts
9. Claude writes the full draft (using at least two phrases from VOC's "Reuse these words" list) and saves to `OUTPUTS/newsletter/` with a "Draft for human review" status header

---

### Content Creator: Drafting a LinkedIn Post

**What's in the folder:**
- CONTEXT/about-me.md, brand-voice.md, voc.md
- (optional) PROJECTS/linkedin/past-posts/ for tone reference

**The prompt:**
```
I want to draft a LinkedIn post about [topic] for [audience]. First, explore my folder.
Then, ask me questions using the AskUserQuestion tool.
I want to refine the approach with you before you execute.
```

**What happens:**
1. Claude reads `CONTEXT/about-me.md` to understand who you are and what you do
2. Claude reads `CONTEXT/brand-voice.md` to match your tone
3. Claude reads `CONTEXT/voc.md` to mirror buyer language and avoid your industry's jargon
4. Claude asks 3-5 clarifying questions via AskUserQuestion (audience cut, hook angle, CTA)
5. Claude drafts the post with at least two phrases from your VOC's "Reuse these words" section
6. Claude saves to `OUTPUTS/linkedin-[YYYY-MM-DD]-[topic].md` with a "Draft for human review" status header

---

### Consultant: Client Deliverable

**What's in the folder:**
- CONTEXT/ (all four files)
- PROJECTS/client-x/brief.md (the client's project brief)
- PROJECTS/client-x/notes.md (call notes or background)
- TEMPLATES/strategy-deck-template.pptx (proven deck structure)

**The prompt:**
```
A client just sent a brief for a 2026 strategy. The brief is in
PROJECTS/client-x/. Read the brief, my deliverable template, and
my past examples. Create a first draft as a .docx.
Ask me questions first using AskUserQuestion.
```

**What happens:**
1. Claude reads the brief and cross-references with the template
2. Claude asks smart questions the user didn't think of — "Should this include a timeline or just recommendations?" "Do you want competitor examples or keep it internal?"
3. User clicks answers
4. Claude creates a .docx file in OUTPUTS/client-x/

---

### Sales: Responding to a Sales Objection

**What's in the folder:**
- CONTEXT/about-me.md, brand-voice.md, voc.md
- (optional) PROJECTS/sales/approved-claims.md (guarantees, pricing, refund terms)

**The prompt:**
```
I just got this objection from a prospect: "[paste the objection]".
Draft a response that addresses it without discounting. First, explore my folder.
```

**What happens:**
1. Claude reads `CONTEXT/voc.md` to find how your buyers naturally describe similar concerns. Pulls the closest matching pain language and reuse-phrases.
2. Claude reads `CONTEXT/brand-voice.md` to match your tone (warm, direct, etc.).
3. Claude drafts a response that acknowledges the objection in the buyer's language, reframes with approved proof, and ends with a single clear next step.
4. Claude flags any approved-only claims (guarantees, pricing, refund terms) for your review before sending.
5. Claude saves to `OUTPUTS/sales-response-[YYYY-MM-DD].md` with a "Draft for human review" status header.

---

### E-Commerce Seller: Listing Optimization

**What's in the folder:**
- CONTEXT/ (all four files)
- PROJECTS/product-launch/listing-data.xlsx (current listing performance)
- PROJECTS/product-launch/competitor-screenshots/ (reference images)

**The prompt:**
```
I want to optimize my Amazon product listing for [ASIN/product].
Check PROJECTS/product-launch/ for my current data.
Ask me questions first using AskUserQuestion.
```

**What happens:**
1. Claude reviews the listing data and competitor references
2. Claude asks: target keywords, main differentiator, price point, audience
3. User clicks answers
4. Claude produces optimized title, bullets, and description saved to OUTPUTS/

---

### General Business: Weekly Planning

**What's in the folder:**
- CONTEXT/ (all four files)
- No project-specific files needed — this pulls from connected tools

**The prompt:**
```
Help me plan my week. Check my calendar, email, and any
connected task tools. Then ask me questions about priorities
using AskUserQuestion before creating the plan.
```

**What happens:**
1. Claude checks Google Calendar for upcoming meetings
2. Claude checks Gmail for anything needing a response
3. Claude checks connected task tools for overdue items
4. Claude asks: "What's your #1 priority this week?" "Any deadlines I should know about?" "Anything you want to block time for?"
5. User clicks answers
6. Claude creates a weekly plan saved to OUTPUTS/

---

### Research & Competitive Analysis

**What's in the folder:**
- CONTEXT/ (all four files)
- PROJECTS/research/competitor-articles/ (3-5 competitor articles or reports)

**The prompt:**
```
I uploaded 4 competitor articles into PROJECTS/research/.
Read all of them. Create a comparison table: what each covered,
what they missed, and where I can say something new.
Ask me questions first.
```

**What happens:**
1. Claude reads all competitor materials
2. Claude asks: "What's your unique angle?" "Which audience are you targeting?" "What format — table, brief, or full report?"
3. User clicks answers
4. Claude produces the analysis in OUTPUTS/research/

## Power User Tip: Text Replacement

For users who use the one-prompt template frequently, suggest setting up a text replacement shortcut on their computer:

**Mac:** System Settings → Keyboard → Text Replacements → Add:
- Replace: `/prompt`
- With: `I want to [TASK] for [SUCCESS CRITERIA]. First, explore my folder. Then, ask me questions using the AskUserQuestion tool. I want to refine the approach with you before you execute.`

**Windows:** Settings → Time & Language → Typing → Advanced keyboard settings → Personal dictionary, or use a text expander app like Espanso or AutoHotkey.

Then every Cowork session starts with typing `/prompt` and filling in the blanks.

## Teaching AskUserQuestion During Onboarding

### When to introduce it

**First mention — after completing the Working Style interview (Capability 2, Step 3):**

> "By the way — those clickable forms I've been using to ask you questions? That's a tool called AskUserQuestion. You can tell Claude to use it in your own prompts. Just add 'Start by using AskUserQuestion' to any task and Claude will generate a form to clarify your needs before executing. It's the single biggest quality-of-life upgrade in Cowork."

**Full explanation — during "Your First Prompt" graduation step:**

Walk through the one-prompt template, explain each piece, and run a real task together so the user experiences the AskUserQuestion flow from the other side — as the person giving instructions, not the person answering questions.

### What to emphasize

- You don't need to write long prompts anymore
- Claude asks YOU the right questions
- The output quality jumps because Claude has the context it needs before starting
- This pattern works for 80% of tasks — only the task description changes
