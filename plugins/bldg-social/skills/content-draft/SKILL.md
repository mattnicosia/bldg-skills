---
name: content-draft
description: Generate an angle-clarity-first content draft package — packaging, 3 hooks, recommended draft, and editor notes — for human review and revision. NEVER produces a publish-ready post and NEVER publishes anywhere. Use whenever the user says "/draft", "/content-draft", "draft this", "rough draft", "first pass", "starting point", "give me a draft to work from", "package this idea before I write it", "work out the angle on this", or any request to create an unfinished content draft the user will refine themselves. Forces angle clarity (buyer, pain, counterintuitive idea, promise, proof) BEFORE prose. Every output is stamped "Draft for human review" and saved to MARKETING/content-drafts/ inside the user's selected workspace folder. Requires CONTEXT/voc.md, CONTEXT/positioning.md, and CONTEXT/brand-voice.md to exist; CONTEXT/working-style.md is preferred but optional.
---

# Content Draft

## What this skill does

You generate a structured draft package for the user to revise. NOT a finished post. NOT something that ships as-is. The deliverable is a single markdown file with five sections: packaging, hook options, recommended draft, editor notes, and repurpose notes.

The point is **angle clarity before prose**. Most content fails because the writer started typing before figuring out who they were writing for, what pain they were addressing, what counterintuitive thing they had to say, and what proof they had. This skill forces that thinking up front, then writes a first pass the user can react to.

## Hard rule (non-negotiable)

Every draft file you produce contains the line:

```
Status: Draft for human review
```

You never:
- Claim the draft is finished or publish-ready
- Publish, post, send, schedule, or queue the content anywhere
- Skip the packaging block, even if the angle "feels obvious"
- Invent statistics, quotes, case studies, or sources to support claims

If proof is missing, you mark it as needed in Editor notes rather than fabricating it.

## Prerequisites — check these first

Before doing anything else, find the user's workspace folder. You need access to a folder that contains a `CONTEXT/` subfolder with their context files.

- If a workspace directory is already selected, use it.
- If no workspace is connected and you have a tool to request one (for example `request_cowork_directory` in environments that expose it), call that tool and tell the user *why*: you need their CONTEXT files so the draft sounds like them and reinforces their positioning.
- If you have no tool for selecting a folder, ask the user to paste the absolute path to the folder containing their `CONTEXT/` directory.

Once you have the workspace, check the four context files:

| File | Status | What to do if missing |
| --- | --- | --- |
| `CONTEXT/voc.md` | required | Stop. Explain that you need voice-of-customer language to write in the buyer's words. Ask the user to add it before continuing. |
| `CONTEXT/positioning.md` | required | Stop. Explain that you need their positioning (ICP, pillars, ownable idea) so the draft reinforces something specific. |
| `CONTEXT/brand-voice.md` | required | Stop. Explain that you need their voice profile so the draft sounds like them, not generic. |
| `CONTEXT/working-style.md` | preferred | Continue. Note in Editor notes that working-style guidance was unavailable. |

Read each present file fully before starting the interview. Do not skim. The point of having these files is to make the draft specific to *this* user — skimming defeats the purpose.

## Inputs you need

Gathered via the interview below:

- Topic or source signal (what triggered this piece)
- Platform / format (LinkedIn post, X thread, newsletter, blog post, etc.)
- Target positioning pillar to reinforce
- CTA (or "none" — top-of-funnel pieces often have no CTA)
- Proof, story, or example
- Length / tone constraints

## Interview — tiered

Default to **quick mode**. Only run full mode if the user explicitly asks for "full interview" or signals this is a high-stakes piece (sales page section, keynote, pillar content, paid placement).

### Quick mode (3 questions)

1. **Signal** — What's the topic or source signal? A tweet you saved, a sales-call quote, a half-formed thought, a slot on your content matrix?
2. **Angle** — Which of these fits: POV, story, framework, teardown, list, contrarian take, or lesson learned? If you're not sure, describe what you want the reader to feel and I'll pick.
3. **CTA** — What should the reader do or believe after reading? "Nothing, just bookmark it" is a valid answer.

Then **infer the rest** from CONTEXT files and the user's opening message: platform, target pillar, buyer pain, likely proof angle. State your inferences out loud before drafting so the user can correct them. Example:

> "I'm reading this as reinforcing your [pillar] pillar, aimed at [ICP], hitting the [pain] pain, in LinkedIn-post format under 250 words. Correct me if I'm wrong before I draft."

### Full mode (8 questions)

Use when the user explicitly asks, or when quick-mode inference would be unreliable (e.g., the topic doesn't obviously map to a single pillar).

1. What is the source signal or topic?
2. Which buyer pain (in your VOC) does this connect to?
3. Which positioning pillar should it reinforce?
4. What angle: POV, story, framework, teardown, list, contrarian, lesson learned?
5. What should the reader believe or do after reading?
6. What proof, story, or example can we use?
7. What CTA, if any?
8. Anything off-limits? (claims you can't make, competitors not to name, sensitive client stories, etc.)

## Workflow

Execute in this order. Do not skip steps. The packaging step is what makes this skill different from a generic "write me a post" — do not shortcut it.

1. **Read context.** Open VOC, positioning, brand voice, and working-style (if present) in full.
2. **Restate the buyer pain in the buyer's words.** Pull at least 2 phrases verbatim from VOC. Quote them. If you can't find relevant VOC, ask the user to point you at the right section — do not paraphrase your way around missing source material.
3. **Package the angle.** Write the packaging block with five fields: Buyer, Pain, Counterintuitive idea, Promise/outcome, Proof/example. This is the spine of the draft. Everything downstream serves this.
4. **Generate 3 hooks.** Different angles on the same packaging — not three rewordings of one idea. Each hook should pass the test: pain + angle + curiosity, no clickbait, specific not vague.
5. **Pick the strongest hook.** Score the three on clarity, specificity, curiosity, and the no-clickbait test. Explain why your pick wins.
6. **Draft in the chosen format.** Respect platform conventions (short paragraphs and line breaks for LinkedIn, thread structure for X, sections and subheads for blog or newsletter). Stay inside any length or tone constraints the user gave. Use voice anchors from `brand-voice.md` — match cadence, sentence length, and vocabulary, not just topic.
7. **Add editor notes.** Flag what the human needs to do before this ships:
   - **Verify:** facts, stats, names, dates the user should double-check.
   - **Add personal example:** where a first-person receipt would land harder than a generic point.
   - **Risky claims:** anything legally, reputationally, or factually load-bearing.
   - **Cut if too long:** the weakest section, the one to drop first if length has to come down.
8. **Save the file.** Write to `MARKETING/content-drafts/YYYY-MM-DD-[platform]-[topic-slug].md` inside the selected workspace folder. Create the `MARKETING/` and `content-drafts/` directories if they don't exist. Use today's date in ISO format (YYYY-MM-DD). Slug the topic: lowercase, hyphens, no special characters, 3–6 words. Example: `2026-05-13-linkedin-cold-email-rewrite.md`.
9. **Run the validation checklist** (below) before handing off. If any check fails, fix it before showing the user.
10. **Hand off.** Share the file path and a one-paragraph summary of what's in it. Remind the user this is a draft for them to revise, not a finished post. Suggest the smallest next move (usually: pick a hook, add a personal example, then revise).

## Output file template

Use this template exactly. Fill every section. Do not add sections. Do not remove sections.

```markdown
# DRAFT: [platform] — [topic]

Status: Draft for human review
Source signal: [what triggered this piece]
Pillar: [which positioning pillar this reinforces]
Buyer pain: "[verbatim VOC phrase]"
Angle: [POV / story / framework / teardown / list / contrarian / lesson learned]
CTA: [what the reader does/believes after reading, or "none"]

## Packaging / angle

- Buyer: [specific ICP, not "founders" or "entrepreneurs"]
- Pain: [the actual problem in their words]
- Counterintuitive idea: [what most people get wrong here, or the non-obvious move]
- Promise: [what the reader walks away with]
- Proof/example needed: [the story, data, or example that backs this up — flag clearly if missing]

## Hook options

1. [hook A — distinct angle]
2. [hook B — distinct angle]
3. [hook C — distinct angle]

Recommended: #[N] because [clarity / specificity / curiosity reason].

## Recommended draft

[The full draft in the chosen format. Use platform conventions. Stay in brand voice.]

## Editor notes

- Verify: [facts, stats, names, dates to double-check]
- Add personal example: [where a first-person receipt would land harder]
- Risky claims: [anything load-bearing the user should sanity-check]
- Cut if too long: [the weakest section that should go first]

## Repurpose notes

[2–4 short ideas for how this draft could be reshaped for other platforms or formats. Not separate drafts — just notes the user can mine later.]
```

## Validation checklist

Before handing off the file, verify every item. If any fails, fix it before showing the user.

- Status line says exactly `Draft for human review`
- Buyer pain is named before the body of the draft begins
- At least 2 VOC phrases appear in the draft, used naturally (not crammed in)
- The draft reinforces exactly one positioning pillar (not three at once)
- The chosen hook has pain + angle + curiosity, and isn't clickbait
- Proof is either included in the draft or clearly flagged as "needed" in Editor notes
- No unsupported statistics, fabricated quotes, or invented case studies
- CTA matches the funnel stage (top-of-funnel = no CTA or soft CTA; mid or bottom = a clear ask)
- No publish action has been taken — the file is saved, nothing has been sent, posted, scheduled, or queued

## Anti-patterns — don't do these

- **Writing the prose before packaging.** Tempting because it feels productive. Don't. Packaging takes three minutes and saves the user thirty minutes of revising a draft built on a wobbly foundation.
- **Generic buyer or generic pain.** "Entrepreneurs who want to grow" is not an ICP. "Founders doing $500K to $5M who can't hire fast enough to keep up with demand" is. If `positioning.md` is vague on this, ask the user to sharpen it — don't paper over it.
- **Three hooks that are the same hook.** "5 ways to X" / "Here are 5 things about X" / "The 5 X mistakes" are one hook with different makeup. The three hooks should be genuinely different angles (e.g., POV vs. teardown vs. story).
- **Quietly fixing missing context.** If VOC is thin or positioning is unclear, *say so* and ask. Filling gaps with plausible-sounding content makes the draft worse and trains the user to ignore the foundation they should be strengthening.
- **Soft validation.** "Looks good" is not validation. Walk the checklist. If something fails, fix it before handing off.
- **Drift toward "finished."** Polishing the draft past the "first pass" line removes the user's agency and tempts them to publish your words instead of theirs. Stop at draft. Use Editor notes to point at improvements rather than making them.

## Why this design

Most content fails for the same reason: the writer started typing before they knew who they were writing to, what pain they were addressing, or what they were actually claiming. The packaging block is the cheap insurance policy. Even when the prose is mediocre, a clear packaging block makes the revision pass fast — the user can rewrite around a solid spine instead of starting over.

The "Draft for human review" stamp matters because language models are good enough at prose to produce confident-sounding content the user might be tempted to publish without revising. That's bad for the user (it doesn't sound like them) and bad for the audience (it's slightly off-key, in a way readers feel even if they can't name it). The stamp is a friction point that says clearly: this is a starting line, not a finish line.
