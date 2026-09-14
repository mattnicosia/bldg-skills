---
name: cowork-onboarding
description: >
  Interactive onboarding workflow for setting up Claude Cowork. Walks
  business owners through building a workspace, connecting tools,
  creating personalized context files (about-me, brand-voice,
  working-style, voice-of-customer), setting global instructions,
  installing skills, creating scheduled tasks, running an optional
  security review, and learning the daily workflow pattern. Includes
  a Quickstart path for users who want to get productive in 15 minutes.
  Use this skill whenever someone says "set up Cowork," "onboard me,"
  "configure my setup," "help me get started," "personalize Claude,"
  "create my context files," "connect my tools," "build with AI,"
  "BWA setup," or any request about initial Cowork configuration. Also
  triggers on "how do I set up Cowork" or "I just installed Claude
  Desktop." Works for first-time setup and returning users who want to
  improve any part of their existing configuration.
---

# Cowork Onboarding

An interactive, interview-driven onboarding workflow that sets up Claude Cowork for any business owner. This skill adapts to whoever is using it — no assumptions about industry, role, or technical level.

## Before Starting

Read the appropriate reference file before executing each capability:
- Capability 0 (Build Workspace): `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/workspace-guide.md`
- Capability 1 (Connect Tools): `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/connectors-guide.md`
- Capability 2 (Context Files): `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/context-file-guide.md`
- Capability 3 (Global Instructions): `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/global-instructions-guide.md`
- Capability 4 (Install Skills): `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/skills-guide.md`
- Capability 5 (Scheduled Tasks): `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/scheduled-tasks-guide.md`
- Capability 6 (Security Review): `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/security-guide.md`
- Your First Prompt: `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/use-cases-guide.md`

## Entry Point

When this skill is invoked:

### Step 1: Check Existing Setup

Scan for what's already configured:
- Look for context files (about-me.md, brand-voice.md, working-style.md) in the selected folder — check both root and CONTEXT/ subfolder
- Check for workspace folder structure (CONTEXT/, PROJECTS/, TEMPLATES/, OUTPUTS/ subfolders)
- Check if any connectors are active by testing a known connector (e.g., Google Drive search)
- Note which skills/plugins are already installed from the available_skills list
- Check if any scheduled tasks exist via `list_scheduled_tasks`
- Check if a security posture document exists (security-posture.md in CONTEXT/ or root)

### Step 2: Check for Working Folder

If no folder is selected, explain to the user:

"Before we get started, I'd recommend selecting a folder for this session. This is where I'll save your context files and set up your workspace so everything persists across sessions. You can name it anything you like -- `ClaudeContext`, `AI-Setup`, your business name, whatever makes sense to you. Just pick a dedicated folder that you'll select at the start of each Cowork session."

Use `request_cowork_directory` to prompt the user to select a folder. Remember the folder name they chose and use it in all subsequent references during this onboarding session (never hardcode "ClaudeContext"). If they want to proceed without one, that's fine -- save files to the outputs directory and let them know they'll need to move the files manually.

### Step 3: Route the Session

Detect whether this is a first-time or returning user (based on context file existence). Present the appropriate menu.

**First-time users** (no context files found):

Use AskUserQuestion:
```
"What brings you here today?"

Options:
- I'm brand new -- set everything up (Full Setup ~45 min)
- I want to get productive fast (Quickstart ~15 min)
- I need help with something specific
```

Self-Assessment is intentionally excluded here — it requires context files to work well, so onboarding must come first.

**Route based on selection:**

- **"I'm brand new"** → Full Setup flow (Capabilities 0 → 1 → 2 → 3 → 4 → 5, offer Capability 6, offer Self-Assessment, Your First Prompt, Completion)
- **"Get productive fast"** → Quickstart flow (unchanged)
- **"Help with something specific"** → Free text. Claude uses the input to route to the most relevant capability or offers general help.

**Returning users** (context files and/or workspace already exist):

Use AskUserQuestion:
```
"Welcome back! I can see you've already set up [list what exists].
What would you like to do?"

Options:
- Run a full refresh -- re-interview and update everything
- Update specific sections (pick which ones)
- Run a self-assessment -- find where AI can help your business most
- I need help with something specific
```

Self-Assessment appears here because returning users have already completed onboarding and have context files in place.

**"Full refresh"** → Re-run all capabilities in update mode — reading existing files first and presenting current values as defaults.

**"Run a self-assessment"** → Invoke `build-with-ai:self-assessment`. Context files are guaranteed to exist since they're a returning user.

**"Update specific sections"** → Present multiSelect capability picker with visual indicators of what's currently configured:

```
"What would you like to work on?"

Options (multiSelect enabled):
- [x] Workspace folder structure (configured)
- [x] Tool connections -- [N] connected (update)
- [x] Context files -- [N] files found (update)
- [x] Global instructions (update)
- [ ] Skills & plugins (review)
- [x] Scheduled tasks -- [N] active (update)
- [ ] Security review (not yet run -- recommended)
- [ ] Template seeding (TEMPLATES/ is empty)
- [ ] Self-assessment (run AI readiness analysis)
```

Checked items mean "exists." The user selects which ones to run. Claude executes them in logical order (workspace first, then tools, then context files, etc.) regardless of selection order.

After each capability completes, Claude checks if more are queued and transitions: "Done with [capability]. Next up: [next capability]. Ready to continue?"

**"Help with something specific"** → Route based on free text input.

### Step 4: What to Expect (show once, after menu selection)

Before diving into the chosen path, briefly set expectations. Keep this to 3-4 sentences — not a wall of text. Use natural language, not a bulleted list:

"A few things worth knowing before we start: Cowork sessions use more capacity than regular chat, so on the Pro plan you'll want to use it for your most important work. Cowork is still evolving — always review outputs before sending to clients or publishing. And it only runs in the desktop app, so keep it open when you're working. Quick questions are still better in regular Chat — Cowork is built for multi-step tasks."

---

## Quickstart Path (~15 minutes)

A streamlined path to get users productive fast. Covers the essentials and teaches the daily workflow pattern. Users can return for the full setup anytime.

### Quickstart Step 1: Build Minimal Workspace

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/workspace-guide.md` for the minimal variant.

1. If a folder is selected, create the minimal structure:
   ```
   CONTEXT/
   OUTPUTS/
   ```
   Use `mkdir -p` to create both folders.

2. Explain briefly: "CONTEXT is where your identity files live — Claude reads these before every task. OUTPUTS is where Claude delivers everything it creates. Simple, clean, expandable later."

### Quickstart Step 2: Quick About-Me Interview

Condensed version — 3 questions max using AskUserQuestion:

1. **Identity + Business:** "In one or two sentences, what do you do and what's the business you're building?"
   Options: Consultant/advisor, Agency owner, E-commerce/product, Creator/content, Freelancer/solopreneur, or free text.

2. **Tools:** "What tools do you use every day?" (multiSelect)
   Options: Google Workspace, Slack/Discord, Notion/Asana, Social media platforms, or free text.

3. **Working style:** "How should Claude work with you?"
   Options: Ask questions before every task, Just go for simple tasks — ask on complex ones, Show me a plan first, Match my energy — short for simple and detailed for complex.

### Quickstart Step 3: Generate About-Me File

Generate `about-me.md` using the template from the context file guide but with only the sections covered (identity, tools, working preferences). Save to `CONTEXT/about-me.md`.

Present the file and offer to refine.

### Quickstart Step 4: Generate Minimal Global Instructions

Generate a condensed version of Global Instructions covering only:
- Who I Am (2-3 sentences)
- How I Work (3-4 bullets from their working style answer)
- Output Defaults (infer from their role)
- Rules (2-3 rules from their preferences)
- Folder Protocol (minimal version — just CONTEXT/ and OUTPUTS/)

Use the structure from the global instructions guide but skip Voice/Tone and Key Context sections — those come with the full setup.

Present the draft for review. Provide setup instructions for pasting into Settings → Cowork → Global Instructions.

Save as `global-instructions.md` in the folder root for reference.

### Quickstart Step 5: Your First Prompt

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/use-cases-guide.md` for the template and teaching approach.

1. **Introduce AskUserQuestion:**
   "Here's the feature that's going to change how you use Cowork. Instead of writing the perfect prompt, you tell Claude to ask YOU the right questions. Claude generates a clickable form, you click through in under a minute, and the output quality jumps because Claude has exactly the context it needs."

2. **Present the one-prompt template:**
   ```
   I want to [TASK] for [SUCCESS CRITERIA]. First, explore my folder.
   Then, ask me questions using the AskUserQuestion tool.
   I want to refine the approach with you before you execute.
   ```

3. **Suggest a first task based on their role** (from the identity question):
   - Consultant/advisor: "Want to try it? Let's draft an outline for a client deliverable."
   - Agency owner: "Want to try it? Let's create a project brief for one of your current clients."
   - E-commerce/product: "Want to try it? Let's write a product description or listing."
   - Creator/content: "Want to try it? Let's draft your next social media post or article."
   - Freelancer: "Want to try it? Let's tackle something on your to-do list this week."
   - General: "Want to try it? Pick something you need to get done this week and let's run it through the template."

4. **If they say yes,** walk them through the task using the template. Let them experience the full AskUserQuestion → plan → execute flow firsthand.

5. **After the task,** bridge to ongoing usage:
   "That pattern — task + folder + AskUserQuestion — works for about 80% of what you'll do in Cowork. Only the task description changes. The more you add to your folder over time, the less prompting you need."

6. **Optional power tip:** Mention the text replacement shortcut from the use-cases guide for frequent users.

### Quickstart Step 6: Show What's Next

Highlight what the Full Setup adds beyond what Quickstart covered:

"You're set up and productive. When you're ready to go deeper, you can re-run this onboarding to add:
- **Brand voice file** — teaches Claude exactly how you write and communicate
- **Working style file** — detailed preferences for how Claude approaches tasks
- **Tool connections** — link Gmail, Google Drive, Slack, and more so Claude can access your data directly
- **Skills & plugins** — specialized capabilities for your specific role
- **Scheduled tasks** — recurring automations that run while you work on other things
- **Security review** — audit your setup for common security gaps and generate protective rules

Just say 'run onboarding' anytime to pick up where you left off."

Then proceed to the Completion section.

---

## Capability 0: Build Your Workspace

**Goal:** Set up an organized folder structure with clear read/write rules so every Cowork session starts from a clean, predictable foundation.

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/workspace-guide.md` before executing this capability.

### Flow

1. **Check if folder is selected.** If not, use `request_cowork_directory` to prompt selection.

2. **Check for existing structure.** Look for CONTEXT/, PROJECTS/, TEMPLATES/, OUTPUTS/ subfolders. If they exist, acknowledge them and skip to step 5.

3. **Check for existing context files in root.** If about-me.md, brand-voice.md, or working-style.md exist in the folder root (not in a CONTEXT/ subfolder), offer to reorganize: "I can see you already have context files here. Want me to organize them into a CONTEXT/PROJECTS/TEMPLATES/OUTPUTS structure, or leave them where they are?"

4. **Ask structure preference.** Use AskUserQuestion:
   "How structured do you want your workspace?"
   - **Full structure (Recommended)** — CONTEXT, PROJECTS, TEMPLATES, OUTPUTS — organized for serious daily use
   - **Minimal** — CONTEXT + OUTPUTS — get running fast, expand later
   - **Custom** — let me describe what I want

5. **Create the folder structure.** Use bash `mkdir -p` to create the chosen folders inside the selected directory. Don't create example files in PROJECTS or TEMPLATES — those stay empty until the user adds their own material.

6. **Set folder permissions.** Use AskUserQuestion:

   ```
   "How should Claude handle your workspace folders?"

   Options:
   - Read-only source folders (Recommended for safety)
     Claude reads CONTEXT/, PROJECTS/, TEMPLATES/ but never modifies them.
     You manually maintain these folders.

   - Read/write with confirmation
     Claude can update files in CONTEXT/, PROJECTS/, TEMPLATES/ but always
     asks before modifying. Good if you want Claude to help maintain your
     workspace.

   - Full read/write (Advanced)
     Claude can freely read and write all folders. Best for power users
     who want maximum automation.
   ```

   Store the user's choice. This feeds into:
   - The Folder Protocol section of Global Instructions (Capability 3)
   - The workspace-guide reference
   - The security review's global instructions audit (Capability 6)

7. **Explain the rules** based on their permission choice:
   - Read-only: "CONTEXT, PROJECTS, and TEMPLATES are read-only — I read them for context but never touch them. Only you add or update files there. OUTPUTS is where I deliver everything I create."
   - Read/write with confirmation: "I can update files in any folder, but I'll always show you what I'm changing and ask before saving. OUTPUTS is still where all new work goes."
   - Full read/write: "I have full access to all folders. I'll create and update files wherever makes sense. OUTPUTS is still the default for new deliverables."

8. **If doing Full Setup:** transition to Capability 1 (Connect Your Tools). Note that context files will be saved to CONTEXT/ when we get to Capability 2.

---

## Capability 1: Connect Your Tools

**Why this comes first:** Connecting platforms like Google Drive, Notion, or Slack before building context files means Claude can search the user's existing documents during the interview. This produces richer, more accurate context files with less typing from the user.

### Flow

1. **Ask what tools they use daily.** Use AskUserQuestion with common options:
   - Google Workspace (Drive, Gmail, Calendar)
   - Slack
   - Notion
   - Asana / Monday / Linear
   - Figma
   - Other (let them type)

   Allow multiple selections.

2. **Search for connectors.** For each tool mentioned, use `search_mcp_registry` with relevant keywords to check if a connector exists.

3. **Present available connectors.** For each match, use `suggest_connectors` with the connector's UUID to show the user a connect button. Briefly explain what each connector enables (e.g., "Connecting Google Drive lets me search your documents, read files, and pull context without you needing to copy-paste anything.").

4. **Handle tools without connectors.** Note them and suggest alternatives where possible. Be honest: "There's no direct connector for Calendly right now, but if you sync Calendly to Google Calendar, I can access your schedule through the Google Calendar connector."

5. **Verify connections.** After connecting, suggest a quick test for each. For example:
   - Google Drive: "Let me search your Drive for a recent document to make sure the connection works."
   - Slack: "Let me pull your recent messages to verify."

6. **Note what's connected.** Track which platforms are now available — this directly feeds into Capability 2's pre-scan step and Capability 6's security audit.

---

## Capability 2: Context Files

**Goal:** Interview the user and generate four markdown files that give Claude persistent context about who they are, how they communicate, and how they work.

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/context-file-guide.md` before starting this capability for templates and the full question bank.

### Sub-Routing for Returning Users

If any context files already exist (about-me.md, brand-voice.md, working-style.md, or voc.md), present a sub-menu using AskUserQuestion:

"I can see you already have context files. What would you like to do?"
- **Update About Me** — Re-interview and regenerate just your about-me.md
- **Update Brand Voice** — Re-interview and regenerate just your brand-voice.md
- **Update Working Style** — Re-interview and regenerate just your working-style.md
- **Update Voice of Customer** — Re-interview and regenerate just your voc.md
- **Regenerate All Four** — Full re-interview, update everything

If they pick a specific file, jump directly to the corresponding interview step (Step 1, 2, or 3) and regenerate only that file. Read the existing file first and present current content as defaults the user can keep or change.

If they pick "Regenerate All Four," run the full flow below.

If no context files exist, skip this sub-menu and run the full flow.

### Flow

#### Step 0: Pre-scan Connected Platforms

If any connectors are active (especially Google Drive or Notion), search for existing materials that could inform the context files:
- Brand voice guides, style guides, tone documents
- About pages, bios, company descriptions
- SOPs, workflows, process documents
- ICP documents, customer personas

Search using queries like: `name contains 'brand' or name contains 'voice' or name contains 'style guide' or name contains 'about'`

If materials are found, present them: "I found these documents in your connected platforms that might help us build your context files faster: [list]. Want me to use these as a starting point?"

If the user agrees, read the materials and use them to pre-fill information. The interview then becomes a refinement/confirmation step rather than starting from blank.

#### Step 1: About Me Interview

Use AskUserQuestion for each question. Adapt follow-ups based on answers. The reference file has the full question bank, but the core questions are:

1. **Identity:** "In one sentence, how would you describe what you do?" Offer options based on common business types (consultant, agency owner, e-commerce, creator, freelancer, etc.) plus a free-text option.

2. **Businesses/Projects:** "What are all the businesses or projects you're actively working on right now?" Ask which ones take the most time.

3. **Background:** "What's your professional background? What experience makes you credible in what you do?"

4. **Tools:** "What tools and platforms do you use day-to-day?" Offer common categories (communication, project management, docs, automation, etc.).

5. **Customers (optional):** "Who do you serve? What does your ideal customer look like?" Skip if not relevant (e.g., they're an internal employee, not a business owner).

#### Step 2: Brand Voice Interview

1. **Communication style:** "How would you describe your tone when communicating professionally?" Offer a spectrum: direct/no-BS, warm/encouraging, academic/analytical, casual/conversational.

2. **Multiple voices:** "Do you communicate differently depending on the audience?" If yes, interview each voice mode separately (e.g., technical vs. client-facing).

3. **Anti-voice:** "What kind of language or communication style do you hate? What should Claude never sound like when writing for you?"

4. **Existing materials:** If connected platforms had brand docs, reference them here. If the brand-voice plugin is installed, offer to run guideline generation for a deeper analysis. Otherwise, ask if they have any writing samples they're proud of.

#### Step 3: Working Style Interview

1. **Task approach:** "When Claude starts a task for you, what do you prefer?" Options: always ask clarifying questions first, just go for simple tasks, show me a plan first, depends on the task.

2. **Output format:** "What file format should Claude default to for deliverables?" Options: markdown, Word docs, depends on the task, ask each time.

3. **Verbosity:** "How detailed should Claude's responses be?" Options: concise and direct, balanced, detailed, match to complexity.

4. **Rules:** "Any specific pet peeves or hard rules for how Claude should behave?" Options: no fluff/filler, always show reasoning, bias toward action, let me type my own.

#### Step 3.5: Teach AskUserQuestion (inline moment)

After completing the Working Style interview, introduce the concept:

"By the way — those clickable forms I've been using to ask you questions? That's a tool called AskUserQuestion. You can tell Claude to use it in your own prompts. Just add 'Start by using AskUserQuestion' to any task and Claude will generate a form to clarify your needs before executing. It's the single biggest quality-of-life upgrade in Cowork — we'll practice it together at the end of the setup."

#### Step 4: Voice of Customer Interview

Why this exists: marketing, sales, content, and client-facing work all need to sound like the buyer, not like generic SaaS marketing. Voice of Customer (VOC) captures the exact words your buyers use so the agent can mirror them.

Use AskUserQuestion. Adapt follow-ups based on answers. The full template lives in the context file guide. Core questions:

1. **Buyer in plain language:** "Who is the buyer, in plain language?"
2. **Pre-help moment:** "What do they say right before they look for help?"
3. **Pain words:** "What problem words do they repeat?"
4. **Outcome words:** "What outcome do they ask for in their words?"
5. **Fears:** "What do they fear if nothing changes?"
6. **Failed alternatives:** "What alternatives have they already tried?"
7. **Objections:** "What objections show up before buying?"
8. **Buyer-only phrases:** "What phrases do buyers use that you would not naturally write?"
9. **Avoid-jargon:** "What jargon does your industry use that buyers do not use?"
10. **Direct quotes:** "Paste 3 to 10 exact quotes if available."

**Sources to offer in the prompt:** best-customer descriptions, sales call notes/transcripts, reviews/testimonials, support tickets, DMs/comments, founder memory (must be labeled as assumption when used).

**Validation rules** (the skill checks these before declaring VOC complete):
- Minimum viable: 5 exact buyer phrases, 3 pains, 3 outcomes, 2 objections.
- Strong: 20+ quotes from 3+ sources.
- Every quote must have a source label (e.g., "— source: review", "— source: founder memory").
- Includes a jargon blacklist (the "Avoid these words" section).

**If the user has no real customer data**, write the file with a header line: `ASSUMPTION-BASED VOC - replace with real quotes`. The blueprint and downstream skills treat assumption-only VOC as a temporary placeholder.

#### Step 5: Generate Files

Generate four files using the templates from the context file guide:
- `about-me.md` — structured overview of identity, background, businesses, tools, customers
- `brand-voice.md` — tone, voice modes, anti-voice, language preferences
- `working-style.md` — task approach, output defaults, verbosity, rules
- `voc.md` — buyer language, pain phrases, desired outcomes, objections, jargon blacklist

**File save location:**
- If workspace structure exists (CONTEXT/ subfolder): save to `CONTEXT/`
- If no workspace structure: save to the selected folder root
- If no folder selected: save to outputs and instruct the user to move them

Present links to all four files and offer to refine any section.

---

## Capability 3: Global Instructions

**Goal:** Distill the context files into a condensed document optimized for the Global Instructions field in Settings > Cowork.

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/global-instructions-guide.md` for the format template and word budget.

### Sub-Routing for Returning Users

If `global-instructions.md` already exists, present a sub-menu using AskUserQuestion:

"You already have global instructions. What would you like to do?"
- **Regenerate from context files** — Rebuild the full document from your current about-me, brand-voice, and working-style files
- **Add/update security rules** — Add or replace the Security Rules section only (runs the security interview if needed)
- **Add/update folder protocol** — Add or replace the Folder Protocol and Naming Convention sections based on current workspace structure
- **Start fresh** — Full regeneration with interview

If they pick a targeted update, read the existing `global-instructions.md`, modify only the relevant section(s), and present the updated version for approval.

If no global instructions exist, skip this sub-menu and run the full flow.

### Flow

1. **Check prerequisites.** If no context files exist yet, suggest running Capability 2 first. If the user wants to skip ahead, interview them for the basics inline.

2. **Read context files** from the selected folder (check both CONTEXT/ subfolder and root).

3. **Generate condensed instructions** under ~800 words, structured as:
   - Who I am (2-3 sentences)
   - How I work (task approach, communication preferences)
   - Output defaults (format by task type)
   - Voice/tone (key characteristics, voice modes if applicable)
   - Key business context (businesses, customers, frameworks)
   - Rules (always do / never do)
   - Security rules (if Capability 6 has been completed — include the user's chosen security rules)
   - Folder Protocol (if workspace structure exists — include read/write rules based on the user's permission model choice from Capability 0, and before-every-task checklist)
   - Naming Convention (if workspace structure exists — include the `project_content-type_v1.ext` pattern)

   **Permission model variants for the Folder Protocol section:**

   Read-only (default):
   ```
   ### Read-only — never create, edit, or delete anything here:
   - `CONTEXT/` — My identity, voice, and working rules. Read before every task.
   - `TEMPLATES/` — Proven structures to reuse as patterns.
   - `PROJECTS/` — My briefs, references, and finished work by project.

   ### Write folder — the only place you deliver work:
   - `OUTPUTS/` — Everything you create goes here.
   ```

   Read/write with confirmation:
   ```
   ### Folders you can read and update (with confirmation):
   - `CONTEXT/` — My identity, voice, and working rules. Read before every task.
     You may suggest updates but always show me the diff before saving.
   - `PROJECTS/` — Briefs, references, and finished work by project.
   - `TEMPLATES/` — Proven structures to reuse as patterns.

   ### Write folder — deliver all new work here:
   - `OUTPUTS/` — Everything you create goes here.
   ```

   Full read/write:
   ```
   ### All folders are readable and writable:
   - `CONTEXT/` — My identity, voice, and working rules. Read before every task.
   - `PROJECTS/` — Briefs, references, and finished work by project.
   - `TEMPLATES/` — Proven structures to reuse as patterns.
   - `OUTPUTS/` — Default destination for new deliverables.
   ```

4. **Present the draft.** Let the user review and request changes.

5. **Provide setup instructions:**
   "To activate these, open the Claude desktop app → Settings → Cowork → click 'Edit' next to Global Instructions → paste the contents → save. These will load automatically at the start of every Cowork session, even before you select a folder."

Save the global instructions as `global-instructions.md` alongside the context files for reference.

---

## Capability 4: Install Skills

**Goal:** Help the user discover and install relevant skills and plugins for their specific role and needs.

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/skills-guide.md` for the recommendation matrix.

### Flow

1. **Understand their role.** If context files exist, use them. Otherwise, ask: "What kind of work do you do most often?" Offer categories: content creation, sales/outreach, data analysis, project management, document creation, research, etc.

2. **Check available skills.** Review the `available_skills` list in the current session. Present what's already installed and what it does.

3. **Live plugin discovery.** For each of the user's stated needs and role keywords, run `search_plugins` to get the current marketplace inventory. Compare results against the static recommendation matrix in the skills guide reference.

   - If search_plugins returns results NOT in the static matrix, present them as "Recently added" or "New since last update"
   - If the static matrix recommends something search_plugins can't find, note it may have been renamed or removed
   - Always prioritize live search results over static recommendations when there's a conflict

4. **Cross-reference installed skills.** Check the available_skills list against both live results and static recommendations. Highlight what's already installed, what's recommended but not installed, and what's new.

5. **Help install.** For plugins, use `suggest_plugin_install`. For skills already available, show the slash commands they add and suggest a first prompt to try.

6. **Note gaps.** If the user describes a workflow need that no existing skill covers, note it: "There's no existing skill for that yet, but you could create a custom one using the skill-creator if you'd like."

---

## Capability 5: Scheduled Tasks

**Goal:** Help the user identify recurring tasks and set them up as automated scheduled tasks.

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/scheduled-tasks-guide.md` for common patterns and prompt templates.

### Sub-Routing for Returning Users

Check for existing scheduled tasks using `list_scheduled_tasks`. If any exist, present a sub-menu using AskUserQuestion:

"You already have scheduled tasks set up. What would you like to do?"
- **Add a new task** — Interview for a new recurring pattern and create it
- **Review existing tasks** — List all current tasks with their schedules and status, offer to modify or pause any
- **Remove a task** — Show current tasks and let you pick one to disable or delete
- **Start fresh** — Full interview for recurring patterns

If they pick "Add a new task," skip directly to the proposal step (Step 3 in the full flow) — interview for the new pattern only, then propose and create.

If they pick "Review existing tasks," list all tasks with `list_scheduled_tasks`, present each with its schedule, enabled status, and last run time. For each, offer: keep as-is, modify the prompt, change the schedule, or pause/disable.

If they pick "Remove a task," list all tasks and let the user select which to disable. Use `update_scheduled_task` with `enabled: false` to pause.

If no scheduled tasks exist, skip this sub-menu and run the full flow.

### Flow

1. **Interview for recurring patterns.** Use AskUserQuestion:
   - "What do you do every morning when you start work?" (inbox check, news scan, task review)
   - "Are there any weekly tasks you repeat?" (reports, summaries, content scheduling, check-ins)
   - "Any monthly or periodic tasks?" (reviews, audits, cleanups)
   - "Do you have any skills or workflows you want to run on a schedule? For example, a content skill that drafts posts every Monday, or a reporting skill that summarizes your week every Friday."

2. **Check existing tasks.** Use `list_scheduled_tasks` to see what's already configured. Present them if any exist.

3. **Propose tasks.** For each identified pattern, propose a scheduled task with:
   - Clear description of what it does
   - Suggested schedule in plain language ("Every weekday at 8 AM")
   - The full self-contained prompt the task would execute
   - Which connected tools it would leverage

4. **Always propose three quarterly maintenance tasks:**

   **a. Context review.** Every 3 months, Claude reads your context files (about-me, brand-voice, working-style), asks what's changed, and updates anything that's drifted.

   **b. VOC refresh.** Every 3 months, Claude pulls 10 fresh buyer quotes from the last 90 days of calls, tickets, and reviews, then merges them into `voc.md` so the file stays current with how your buyers actually talk this quarter.

   **c. Security review.** Every 3 months, re-run the security audit to catch stale connectors, new permissions, or scheduled tasks that have grown beyond their original risk envelope.

   Present all three. Let the user approve, modify, or skip each. Don't bundle them into one — they have different cadences and different content.

5. **Get approval.** Present each proposed task and let the user approve, modify, or skip. Do not create any task without explicit approval.

6. **Create approved tasks.** Use `create_scheduled_task` for each approved task with the appropriate cron expression and prompt. Remember: cron expressions are in the user's local timezone.

7. **Explain management.** Tell the user how to view, pause, update, or delete tasks in future sessions.

---

## Capability 6: Security Review (Optional)

**Goal:** Audit the user's current Cowork configuration for common security gaps and generate a security posture document with actionable recommendations. This capability is optional but recommended — especially for users who have connected tools or set up scheduled tasks.

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/security-guide.md` before executing this capability for the full audit checklist, risk classifications, and templates.

### When This Runs

- **Full Setup path:** Offered after Capability 5 (Scheduled Tasks), before Self-Assessment offer and "Your First Prompt." Present it as: "Before we wrap up, want to run a quick security check on everything we just set up? It takes about 5 minutes and helps make sure your setup is locked down the way you want."
- **Standalone:** Available from the welcome menu as "Security Review."
- **Returning users:** If the user has completed setup but never run a security review (no security-posture.md found), suggest it when they re-run onboarding.

### Sub-Routing for Returning Users

If `security-posture.md` already exists, present a sub-menu using AskUserQuestion:

"You already have a security review on file. What would you like to do?"
- **Full review** — Run the complete audit again from scratch
- **Audit connected tools** — Just re-check what your connectors can access (useful after connecting new tools)
- **Audit workspace folder** — Just re-scan for sensitive files (useful after reorganizing your folder)
- **Audit scheduled tasks** — Just re-classify your tasks by risk level (useful after adding new tasks)
- **Update security rules** — Re-interview for your security preferences and regenerate the rules section

If they pick a targeted audit:
- Run only that audit step (Step 2, 3, 5, or the interview from Step 1)
- Read the existing `security-posture.md` and update only the relevant section
- Present the changes and save the updated document
- Offer to update Global Instructions if the security rules changed

If no security posture document exists, skip this sub-menu and run the full flow.

### Flow

#### Step 1: Interview — Establish Preferences

Use AskUserQuestion for 2-3 questions to understand the user's security posture. See the security guide for the full question bank. The core questions:

1. **Data Sensitivity:** "What kind of data does Claude have access to through your connected tools and workspace folder?"
   Options: Mostly business content, Some sensitive data, Highly sensitive, Not sure — help me figure it out

2. **Automated Action Comfort:** "How cautious do you want Claude to be with actions that affect the outside world (sending emails, creating calendar events, publishing content)?"
   Options: Ask before any external action (Recommended), Ask on sensitive actions only, I trust the setup — just flag major risks

3. **Document Trust:** "How often does Claude process documents from people outside your organization?"
   Options: Rarely, Sometimes, Frequently, Not sure

#### Step 2: Audit Connected Tools

List all active connectors detected during the session. For each one, document:
- What it can read (data types)
- What it can write, send, or modify
- Risk notes (if any)

Present this as a simple table. Flag any connectors with write/send access the user may not have considered.

#### Step 3: Audit Workspace Folder

Scan the selected folder for potentially sensitive files. Use bash to search for common patterns:
- `.env` files, files containing "password", "secret", "token", "api_key"
- Private keys (`.pem`, `.key`, `.p12`)
- Financial documents in unexpected locations
- VOC files containing personally identifying customer data (names, emails, phone numbers in direct quotes) — flag as moderate-sensitivity content that should not be uploaded to public LLM contexts. The skill should warn but not refuse.

Also check folder scope:
- Is the folder too broad (home directory, entire Documents folder)?
- Are there more than 1000 files (suggesting scope creep)?

Report findings.

#### Step 4: Audit Global Instructions

If global instructions exist, review them for:
- Overly permissive rules (e.g., "never ask permission," "execute immediately")
- Missing guardrails (no file restrictions, no output review requirement)
- If the user chose "Full read/write" in Capability 0, flag this as a medium-risk configuration and recommend "Read/write with confirmation" if they're not sure they need full access

Report findings with specific recommendations.

#### Step 5: Audit Scheduled Tasks

Use `list_scheduled_tasks` to review each active task. Classify each by risk level using the criteria from the security guide:
- **Low:** Read-only tasks, local file creation
- **Medium:** Shared file creation, non-working-hours execution
- **High:** Sending messages, modifying calendars, publishing content, financial tool interaction

Present the classification. For high-risk tasks, confirm the user is comfortable.

#### Step 6: Prompt Injection Awareness

Deliver the plain-language prompt injection explanation from the security guide. Adapt the emphasis based on the Document Trust answer.

Teach the three rules:
1. If Claude does something you didn't ask for, stop the task
2. Be cautious with documents from untrusted sources
3. Review any output before it gets sent to someone else

#### Step 7: Generate Security Posture Document

Generate `security-posture.md` using the template from the security guide.

**File save location:**
- If workspace structure exists (CONTEXT/ subfolder): save to `CONTEXT/`
- If no workspace structure: save to the selected folder root
- If no folder selected: save to outputs and instruct the user to move them

#### Step 8: Offer Global Instructions Integration

"Want me to add these security rules to your Global Instructions? That way they'll load automatically every session and Claude will follow them without you needing to remind it."

If yes, read the current `global-instructions.md`, add the Security Rules section, present the updated version for approval, and save.

---

## Self-Assessment Offer (Full Setup path only)

After Capability 6 (Security Review) and before Your First Prompt, offer the self-assessment:

"Before we wrap up with your first prompt, want to run a quick self-assessment? It'll identify the highest-ROI AI opportunities in your business and recommend specific skills to act on the findings. Takes about 10 minutes."

If they accept, invoke `build-with-ai:self-assessment` with the Standard tier pre-selected (since they just did a full setup and are ready for depth).

If they decline, proceed to Your First Prompt.

---

## Your First Prompt (Graduation Step)

**Goal:** Teach the user the daily workflow pattern and walk them through their first real task. This runs at the end of Full Setup or as Step 5 of Quickstart.

Read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/use-cases-guide.md` for the template, use cases, and teaching approach.

### Flow

1. **Introduce the concept:**
   "You're all set up. Now here's the one thing that will change how you actually use Cowork day-to-day. Instead of writing long, detailed prompts, you give Claude a short task and tell it to ask YOU the right questions. Claude generates a clickable form, you click through in under a minute, and the output is dramatically better because Claude has the context it needs before starting."

2. **Present the one-prompt template:**
   ```
   I want to [TASK] for [SUCCESS CRITERIA]. First, explore my folder.
   Then, ask me questions using the AskUserQuestion tool.
   I want to refine the approach with you before you execute.
   ```

3. **Explain each piece:**
   - "Explore my folder" — Claude reads your context files, checks PROJECTS/ for relevant material, reviews TEMPLATES/ for patterns
   - "Ask me questions" — Claude generates a form instead of guessing what you want
   - "Refine before you execute" — Claude shows a plan, you approve, then it creates real files

4. **Suggest a first task based on their role** (captured during context file interviews or Quickstart):
   - Content Creator: "Want to try it? Let's draft your next social media post or article."
   - Consultant/Agency: "Want to try it? Let's create an outline for a client deliverable."
   - E-Commerce: "Want to try it? Let's write a product description or optimize a listing."
   - General: "Want to try it? Pick something you need to get done this week and let's run it through the template."

5. **If they accept,** walk them through the full cycle: they write the prompt using the template → Claude asks questions → they click answers → Claude shows a plan → they approve → Claude executes and saves to OUTPUTS/.

6. **After the task, bridge to ongoing usage:**
   "That pattern works for about 80% of what you'll do in Cowork. Only the task description changes. The more you add to your folder over time — project briefs, templates, past work — the less prompting you need and the better the output gets."

7. **Optional power tip:** "If you use this prompt a lot, you can set up a text replacement on your computer. On Mac, go to System Settings → Keyboard → Text Replacements. Add `/prompt` as the shortcut and paste the template as the replacement. Then every Cowork session starts with typing `/prompt` and filling in the blanks."

---

## Completion

After completing any capability (or the full setup), do the following:

### Generate Onboarding Checklist

Create a checklist showing what's been configured and what's still available. Save as `onboarding-checklist.md` in the selected folder (or outputs). Use this format:

```markdown
# Cowork Onboarding Checklist

## Completed
- [x] Workspace folder structure set up
- [x] Connected tools: [list connected platforms]
- [x] Context files: about-me.md, brand-voice.md, working-style.md, voc.md
- [x] Global instructions: generated and ready to paste
- [x] Skills installed: [list]
- [x] Scheduled tasks: [list]
- [x] Security review: audit completed, posture document saved
- [x] First prompt template learned
...

## Still Available
- [ ] Build workspace — set up your folder structure with read/write rules
- [ ] Install skills — discover specialized capabilities for your role
- [ ] Scheduled tasks — set up recurring automations
- [ ] Security review — audit connected tools, workspace, and scheduled tasks for risks
- [ ] Self-assessment — find where AI can help your business most
...

## Your Daily Workflow
Start every Cowork session by:
1. Opening the Claude desktop app and clicking Cowork
2. Selecting your workspace folder
3. Choosing Opus 4.6 + Extended Thinking
4. Using this prompt template for any task:

I want to [TASK] for [SUCCESS CRITERIA]. First, explore my folder.
Then, ask me questions using the AskUserQuestion tool.
I want to refine the approach with you before you execute.

## Tips
- Select your workspace folder at the start of every Cowork session
- Add project briefs and reference material to PROJECTS/ as you work
- Save deliverables you're proud of as templates in TEMPLATES/
- Refine your context files over time — the more detail, the better the output
- Re-run the security review when you connect new tools or add scheduled tasks that send messages
- You can re-run this onboarding anytime to update any section
```

### Quickstart-Specific Completion

If the user chose Quickstart, add a "What's Next" section to the checklist highlighting what Full Setup adds:

```markdown
## What Full Setup Adds
- [ ] Brand voice file — teaches Claude exactly how you write
- [ ] Voice of customer file — captures buyer language so marketing and sales sound like your buyers, not generic SaaS
- [ ] Working style file — detailed preferences for task approach
- [ ] Tool connections — link Gmail, Drive, Slack for direct access
- [ ] Full workspace — PROJECTS/ and TEMPLATES/ folders
- [ ] Skills & plugins — specialized capabilities for your role
- [ ] Scheduled tasks — recurring automations
- [ ] Security review — audit your setup for common security gaps
- [ ] Self-assessment — find where AI can help your business most

Run this onboarding again anytime to add any of these.
```

### Seed Templates (if applicable)

If the user completed a Full Setup (or has a workspace with TEMPLATES/):

1. Check if TEMPLATES/ exists and is empty
2. If empty, read `@${CLAUDE_PLUGIN_ROOT}/skills/cowork-onboarding/references/templates-seed-guide.md`
3. Determine the user's role from context files or interview answers
4. Present relevant templates via AskUserQuestion (multiSelect):
   "Want me to add some starter templates to your TEMPLATES/ folder? Claude uses these as structural patterns when creating similar content. Pick the ones that match your workflow:"
   [Role-appropriate template options]
5. Create selected templates in TEMPLATES/
6. Briefly explain how to use them: "When you ask Claude to write a proposal, it'll check TEMPLATES/ first and use the structure as a pattern. You can customize these anytime."

If TEMPLATES/ already has files, skip this step entirely.

If TEMPLATES/ doesn't exist but the user might benefit: "Want me to add a TEMPLATES/ folder so I can seed it with starter templates for your role?"

### Remind About Re-entry

Let the user know: "You can come back to any of these capabilities anytime by running this skill again and selecting the one you want."

## Behavioral Guidelines

- **Use AskUserQuestion for every interview step.** Multiple-choice options reduce friction. Always allow free-text input for nuance.
- **Adapt to technical level.** If the user uses technical language, match it. If they don't, keep everything in plain language.
- **Don't overwhelm.** Ask 1-2 questions at a time max. Never dump a wall of questions.
- **Be opinionated but flexible.** Suggest good defaults but defer to the user's preferences.
- **Show progress.** After each major step, briefly confirm what was accomplished before moving on.
- **Save files incrementally.** Don't wait until the end to save everything. Generate and save each file as it's completed.
- **Respect existing work.** If context files or configurations already exist, don't overwrite them — offer to update or enhance instead.
- **Save to the right location.** If workspace structure exists, save context files to CONTEXT/ and outputs to OUTPUTS/. If no workspace, save to folder root. If no folder, save to outputs with instructions to move.
- **Teach as you go.** The AskUserQuestion mention after Working Style (Step 3.5) and the Your First Prompt graduation step are educational moments — don't skip them even if the user seems advanced.
- **Security review is optional but recommended.** Never force the security review. Frame it as "this takes 5 minutes and gives you peace of mind" rather than implying the user is at risk.
- **Drift detection in Global Instructions.** When generating or updating Global Instructions, include this bullet under "Before every task": "If you notice information in the conversation that contradicts what's in CONTEXT/ files (e.g., I mention a new business, a tool I've stopped using, or a changed preference), flag it: 'I noticed you mentioned [X] but your about-me.md says [Y]. Want me to update it?'"
