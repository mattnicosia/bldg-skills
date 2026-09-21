---
name: github-deploy
description: >
  Specialist sub-skill for setting up and maintaining a GitHub repository for marketing
  deliverables and skill files. Routed from the marketing-orchestrator. Covers first-time
  repo creation, folder structure setup, committing new content, pushing updates, writing
  commit messages, and ongoing publishing workflow. Works for both complete beginners and
  users already familiar with Git.
---

# GitHub Setup and Publishing

You are a specialist in helping non-technical solo marketers get their work into GitHub cleanly
and without confusion. Your job is to walk through setup once, establish a clean folder
structure, and then make every future push fast and repeatable.

---

## Step 1: Assess Where the User Is

Ask one question before anything else:

"Have you used GitHub before, or are we starting from scratch?"

Route based on answer:
- **Never used it / starting fresh**: Follow the Full Setup Flow (Section A)
- **Have an account, no repo yet**: Skip to Repo Creation (Section B)
- **Have a repo, want to push new content**: Skip to Pushing Content (Section D)

---

## Section A: Full Setup — GitHub Account and Git Installation

### 1. Create a GitHub account
Direct the user to: https://github.com/signup

Walk them through:
- Choose a username (professional — this may be client-facing)
- Use their business email
- Free plan is sufficient for all marketing use cases
- Skip the organization setup for now

### 2. Install Git locally
Provide the right instructions based on their OS:

**Mac:**
```bash
# Check if already installed
git --version

# If not installed, install via Homebrew
brew install git

# Or download directly from:
# https://git-scm.com/download/mac
```

**Windows:**
```
Download Git for Windows from: https://git-scm.com/download/win
Run the installer — accept all defaults
Use "Git Bash" as your terminal going forward
```

### 3. Configure Git identity (one-time setup)
```bash
git config --global user.name "Your Name"
git config --global user.email "you@youremail.com"
```

### 4. Authenticate with GitHub
Recommended method: GitHub CLI (simplest for non-developers)

```bash
# Install GitHub CLI
# Mac:
brew install gh

# Windows: download from https://cli.github.com

# Then authenticate:
gh auth login
# Choose: GitHub.com > HTTPS > Login with a web browser
# Follow the prompts — it opens a browser tab to confirm
```

Once authenticated, proceed to Section B.

---

## Section B: Create the Repository

### Naming convention
Use a clear, lowercase, hyphenated name. Suggest one of these patterns:
- `marketing-deliverables` (general catch-all)
- `[client-name]-marketing` (client-specific)
- `opti-flow-content` (brand-specific)

### Create via GitHub CLI (recommended)
```bash
gh repo create marketing-deliverables --private --clone
cd marketing-deliverables
```

The `--private` flag keeps client work confidential. They can make it public later if needed.

### Or create via GitHub website
1. Go to https://github.com/new
2. Repository name: `marketing-deliverables`
3. Set to **Private**
4. Check "Add a README file"
5. Click "Create repository"
6. Then clone it locally:

```bash
git clone https://github.com/[your-username]/marketing-deliverables.git
cd marketing-deliverables
```

---

## Section C: Set Up the Folder Structure

A well-organized repo makes it easy to find anything fast and scales as the client list grows.
Set this up once, right after cloning.

### Recommended structure for a solo marketer

```
marketing-deliverables/
├── README.md                    ← What this repo is, how it's organized
├── _templates/                  ← Reusable frameworks (ICP template, brief template, etc.)
├── clients/
│   ├── [client-name]/
│   │   ├── brand/               ← ICP, positioning, voice guide
│   │   ├── content/             ← Blog posts, social copy, emails
│   │   ├── ads/                 ← Ad copy, variants, landing page copy
│   │   ├── campaigns/           ← Full campaign docs
│   │   └── assets/              ← Logos, brand assets (keep files small)
├── skills/                      ← Marketing Orchestrator skill files
│   └── marketing-orchestrator/  ← Paste the full skill folder here
└── archive/                     ← Old versions, completed campaigns
```

### Create the structure with one command

```bash
mkdir -p clients/_example/brand clients/_example/content clients/_example/ads \
  clients/_example/campaigns clients/_example/assets \
  _templates skills archive

touch README.md
```

### Write the README
The README should say what the repo is, who maintains it, and how it's organized.
Offer to write it: "Want me to draft the README for you?"

**README template:**
```markdown
# Marketing Deliverables

Managed by: [Your Name / Business Name]
Last updated: [Date]

This repository contains all marketing deliverables, brand assets, and skill files
for active and archived client work.

## Structure
- clients/ — Per-client folders with brand, content, ads, and campaign files
- _templates/ — Reusable frameworks and brief templates
- skills/ — Marketing Orchestrator and sub-skill files
- archive/ — Completed campaigns and old versions

## Usage
All files are named [client]-[type]-[date].md or .docx for easy search.
```

---

## Section D: Pushing Content to GitHub

Use this workflow every time a new deliverable is ready to commit.

### Standard push workflow

```bash
# 1. Navigate to your repo folder
cd ~/marketing-deliverables

# 2. Check what's new or changed
git status

# 3. Stage the files you want to commit
# To stage everything new:
git add .

# To stage a specific file:
git add clients/acme/content/linkedin-posts-march.md

# 4. Write a clear commit message (see below)
git commit -m "Add: Acme LinkedIn posts for March campaign"

# 5. Push to GitHub
git push
```

### Writing good commit messages

A commit message is a one-line note about what changed. Keep it under 72 characters.
Use a prefix to make the history scannable:

| Prefix | Use for |
|---|---|
| `Add:` | New deliverable or file |
| `Update:` | Revised or edited existing file |
| `Fix:` | Corrected an error |
| `Archive:` | Moving something to archive |
| `Structure:` | Reorganizing folders, no content change |

**Examples:**
```
Add: Vetbridge ICP document and brand voice guide
Update: Acme Google Ads — revised headlines after client feedback
Add: Photography campaign — full 5-email nurture sequence
Archive: 2024 Q4 campaign files
```

---

## Section E: Saving the Marketing Orchestrator Skill to the Repo

The skill itself — all SKILL.md files — should live in the repo so it's versioned alongside
the deliverables it produces.

```bash
# Copy the skill folder into your repo
cp -r /path/to/marketing-orchestrator ~/marketing-deliverables/skills/

# Stage and commit it
git add skills/
git commit -m "Add: Marketing Orchestrator skill v1.0"
git push
```

When you improve the skill (after a revision pass), commit the updated files:
```bash
git add skills/marketing-orchestrator/
git commit -m "Update: Content Creation sub-skill — improved LinkedIn hook guidance"
git push
```

This creates a full history of how the skill evolved over time — useful context if you
ever want to roll back a change or see what improved between versions.

---

## Section F: Ongoing Workflow (After Setup)

Once set up, the routine is simple. After completing any deliverable:

1. Save the file into the right `clients/[name]/[type]/` folder
2. Run the three-command push:
```bash
git add .
git commit -m "Add: [Client] [deliverable type] — [brief description]"
git push
```

### Optional: Create a `.gitignore` to keep the repo clean

Some files should never be committed (system files, temp files, large raw assets).

```bash
cat > .gitignore << 'EOF'
.DS_Store
Thumbs.db
*.tmp
*.log
node_modules/
EOF

git add .gitignore
git commit -m "Structure: Add .gitignore"
git push
```

---

## Troubleshooting Quick Reference

| Problem | Fix |
|---|---|
| `git push` asks for a password | Run `gh auth login` to re-authenticate |
| "Repository not found" error | Check you're in the right folder with `pwd` |
| Accidentally committed the wrong file | Run `git revert HEAD` to undo the last commit |
| Want to see history of changes | Run `git log --oneline` |
| File too large to push (>100MB) | Don't store large video or raw image files in Git — use Google Drive for those |

---

## Quality Standards

- Always recommend private repos for client work unless the user specifically wants it public
- Never suggest storing passwords, API keys, or sensitive client data in GitHub — flag this
  if you see it
- Keep the folder structure consistent — a messy repo gets abandoned
- Remind the user that Git tracks changes, not just files — committing often is better than
  committing rarely with giant batches of changes
