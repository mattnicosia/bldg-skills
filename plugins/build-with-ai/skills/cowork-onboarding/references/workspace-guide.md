# Workspace Folder Structure Guide

How to set up an organized workspace folder that makes Cowork sessions consistently productive. Read this before running the Build Your Workspace capability.

---

## Why Structure Matters

Cowork has real read/write access to whatever folder you share. A clean folder structure means:
- Claude reads the right context before every task
- Outputs land in a predictable place
- If something goes wrong, damage is contained to one folder
- You can point Claude at a project subfolder instead of explaining everything from scratch

## Recommended Folder Architecture

```
[USER'S FOLDER NAME]/
├── CONTEXT/                      ← Who you are + how you work
│   ├── about-me.md
│   ├── brand-voice.md
│   ├── working-style.md
│   └── voc.md
├── PROJECTS/                     ← Active work, one subfolder per project
│   ├── client-x/
│   │   ├── brief.md
│   │   ├── reference-deck.pptx
│   │   └── notes.md
│   └── product-launch/
│       ├── timeline.md
│       └── assets/
├── TEMPLATES/                    ← Proven structures to reuse as patterns
│   ├── proposal-template.docx
│   ├── weekly-report-template.md
│   └── email-sequence-template.md
└── OUTPUTS/                      ← Where Claude delivers finished work
    ├── client-x/
    └── product-launch/
```

## Folder Roles

| Folder | Purpose | Default Access |
|--------|---------|----------------|
| `CONTEXT/` | Identity, voice, working preferences, and voice of customer — the four context files from onboarding | Read only |
| `PROJECTS/` | Active briefs, drafts, and reference material organized by project | Read only |
| `TEMPLATES/` | Finished work so good you want to reuse the structure (not the content) | Read only |
| `OUTPUTS/` | Everything Claude creates goes here, organized by project | Read and write |

### Why CONTEXT Instead of ABOUT ME

Onboarding generates four context files (about-me.md, brand-voice.md, working-style.md, voc.md), so a single "ABOUT ME" folder undersells what's there. CONTEXT signals that this folder contains everything Claude needs to understand you — identity, voice, workflow preferences, and voice of customer.

The four context files:
- about-me.md — Who you are, your business, your role, and what you're working on.
- brand-voice.md — How you sound. Tone, vocabulary, sentence rhythm, and what to avoid.
- working-style.md — How you work. Preferences for pacing, format, decisions, and feedback.
- voc.md — Voice of Customer. Buyer language, pain phrases, desired outcomes, jargon blacklist. Loaded for marketing, sales, content, and client-facing work.

## Permission Models

During onboarding, users choose how Claude interacts with their workspace folders. This choice feeds into Global Instructions and the security review.

| Model | CONTEXT/ | PROJECTS/ | TEMPLATES/ | OUTPUTS/ |
|-------|----------|-----------|------------|----------|
| Read-only (default) | Read | Read | Read | Read/Write |
| Read/write with confirmation | Read/Write (confirm) | Read/Write (confirm) | Read/Write (confirm) | Read/Write |
| Full read/write | Read/Write | Read/Write | Read/Write | Read/Write |

### Read-only (Recommended for safety)

Claude reads CONTEXT/, PROJECTS/, and TEMPLATES/ but never modifies them. Only the user adds or updates files there. OUTPUTS/ is the only writable folder.

Best for: Most users. Keeps source material safe. The user manually maintains their workspace.

### Read/write with confirmation

Claude can update files in CONTEXT/, PROJECTS/, and TEMPLATES/ but always asks before modifying. Good if you want Claude to help maintain your workspace — for example, updating context files when information changes or adding project notes.

Best for: Users who want Claude to actively help maintain their workspace.

### Full read/write (Advanced)

Claude can freely read and write all folders. No confirmation needed. Best for power users who want maximum automation and trust their setup.

Best for: Technical users who understand the implications. The security review (Capability 6) flags this as medium-risk if selected.

## Read/Write Rules

These rules get baked into the user's Global Instructions so Claude follows them automatically. The rules vary by permission model:

**Read-only (default):**
- Claude reads CONTEXT/, PROJECTS/, TEMPLATES/ before every task
- Claude never creates, modifies, or deletes files in these folders
- Only the user adds or updates files there
- All Claude-generated work lands in OUTPUTS/

**Read/write with confirmation:**
- Claude reads all folders before every task
- Claude can suggest updates to any folder but always shows the diff first
- The user approves or rejects each change before it's saved
- New deliverables still default to OUTPUTS/

**Full read/write:**
- Claude reads and writes all folders freely
- New deliverables still default to OUTPUTS/ unless context dictates otherwise
- Claude creates project subfolders as needed

## Naming Convention

All files Claude creates follow this pattern:

```
project_content-type_v1.ext
```

**Content types:** Newsletter, LinkedIn-Post, Brief, Deck, Report, Email, Analysis, Outline, Script, Proposal

**Examples:**
- `client-x_proposal_v1.docx`
- `product-launch_email-sequence_v1.md`
- `weekly_newsletter_v2.md`
- `competitor_analysis_v1.xlsx`

**Version rule:** If a file with the same name exists, increment the version number. `v1` → `v2` → `v3`.

## Minimal Variant (Quickstart)

For users who want to get running fast, start with just two folders:

```
[USER'S FOLDER NAME]/
├── CONTEXT/
│   └── about-me.md
└── OUTPUTS/
```

Add PROJECTS/ and TEMPLATES/ later when you need them. The structure scales — you're not locked in.

## Setting Up the Workspace — Onboarding Flow

### What to say to the user

When proposing the folder structure:

> "Let's set up your workspace folder. This is the folder you'll point Claude to every time you start a Cowork session. Think of it like setting up a desk for a new employee — organized, intentional, with clear rules about where things go."

For the permission model:

> "Now let's decide how Claude interacts with these folders. The safest option is read-only — Claude reads your context but never touches it. If you want Claude to help maintain your files, we can enable write access with confirmation. And for power users, there's full read/write."

### AskUserQuestion: Structure Preference

Ask with AskUserQuestion:
"How structured do you want your workspace?"

Options:
- **Full structure (Recommended)** — CONTEXT, PROJECTS, TEMPLATES, OUTPUTS — organized for serious daily use
- **Minimal** — CONTEXT + OUTPUTS — get running fast, expand later
- **Custom** — describe what you want

### AskUserQuestion: Permission Model

Ask with AskUserQuestion (only during Capability 0 — Build Your Workspace):
"How should Claude handle your workspace folders?"

Options:
- **Read-only source folders (Recommended for safety)** — Claude reads CONTEXT/, PROJECTS/, TEMPLATES/ but never modifies them. You manually maintain these folders.
- **Read/write with confirmation** — Claude can update files in CONTEXT/, PROJECTS/, TEMPLATES/ but always asks before modifying. Good if you want Claude to help maintain your workspace.
- **Full read/write (Advanced)** — Claude can freely read and write all folders. Best for power users who want maximum automation.

### Creating the folders

Use bash `mkdir -p` to create the folder structure inside the user's selected folder. Don't create example files in PROJECTS or TEMPLATES — those stay empty until the user adds their own material.

For CONTEXT/, create the folder but don't add files yet — the Context Files capability (Capability 2) handles that.

### When Workspace Already Exists

If the user already has a folder with context files in the root:
1. Acknowledge what exists — don't suggest starting over
2. Offer to reorganize: "I can see you already have context files here. Want me to organize them into the CONTEXT/PROJECTS/TEMPLATES/OUTPUTS structure, or leave them as-is?"
3. If they decline restructuring, adapt — save outputs to an OUTPUTS/ subfolder but leave everything else where it is
4. Update global instructions to reference actual file locations either way

### Workspace + Global Instructions Integration

When generating Global Instructions (Capability 3), include folder protocol based on the workspace structure and permission model that was set up. The global-instructions-guide.md has the template variants for each permission model.
