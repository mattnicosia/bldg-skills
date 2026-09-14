# AI Readiness Self-Assessment

**Date:** 2026-06-30
**Name:** Matt Nicosia
**Business:** BLDG Estimating (construction estimating service + general contracting, NYC metro)
**Industry:** Trades / Contracting (estimating)
**Assessment tier:** Standard (focused)

---

## Your Priority Outcome

Your primary focus is **Efficiency (getting hours back)**.

You named one specific bleak, plainly: the manual relay between getting an estimate request and having a bid package ready. Right now that's "a lot of manual steps" across four systems, and when you're busy "the estimate sits in my inbox." You want a one-click path through that workflow. That is the assessment.

---

## Executive Summary

I identified seven pain points inside one workflow: estimate intake to bid package. Three are Quick Wins you can automate now because they live on systems you already control (your Dropbox folder, the sow-generator skill you already built, and your Gmail). Two are Major Projects because ProEst and BuildingConnected are web apps with no direct connector and need browser automation. Conservatively, automating just the buildable chunk recovers 3 to 5 hours per week and kills the "sits in my inbox" delay. The single most impactful move: build one Estimate Intake skill that chains inbox to Dropbox to SOW automatically, then bolt the two web-app steps on after.

---

## Three Outcomes Overview

### Effectiveness (Revenue)

Not your focus today, but worth flagging: every hour an estimate sits in your inbox is throughput you can't bill, and slow intake is the first thing clients feel. Faster, more consistent intake lets you take on more bids without adding hours. Indirect revenue upside, real.

**Opportunities identified:** 1 (throughput / faster turnaround)
**Estimated revenue impact:** To be quantified (more bids handled per week)

### Efficiency (Time Saved)

This is the whole game. The intake-to-bid-package chain is pure manual setup work: creating Dropbox folders, re-entering project data into ProEst, running the SOW, then assembling the bid package in BuildingConnected. Most of it is low-value clicking that does not need your brain, just your time.

**Estimated hours recoverable:** 3 to 5 hours/week (buildable chunk) — more with full orchestration
**Top time sinks identified:** (1) Dropbox project setup, (2) ProEst project creation, (3) BuildingConnected bid package assembly

### Quality (Customer Experience)

Indirect but present. The "estimate sits in my inbox" failure mode is a quality gap: requests stall when you're slammed, and the intake experience is inconsistent. A standardized, automated intake means every project gets set up the same way, every time, regardless of how busy you are.

**Improvement areas identified:** 2
**Key quality gaps:** (1) intake stalls under load, (2) inconsistent project setup

---

## Impact-Effort Matrix

### Quick Wins (Do First)

High impact, low effort — your immediate priorities. All three live on systems you already control.

| # | Pain Point | Impact | Effort | Outcome | Est. Time Saved |
|---|-----------|--------|--------|---------|----------------|
| 1 | "The estimate sits in my inbox" — no instant trigger or acknowledgment when a request arrives | 7 | 3 | F | 1–2 hrs/wk + faster starts |
| 2 | Dropbox project folders built by hand every time | 7 | 2 | F | ~1 hr/wk |
| 3 | sow-generator runs as a manual, disconnected step instead of being chained into intake | 7 | 2 | F | ~1 hr/wk |

### Major Projects (Plan Carefully)

High impact, high effort — worth doing, but these need browser automation because there's no direct connector.

| # | Pain Point | Impact | Effort | Outcome | Notes |
|---|-----------|--------|--------|---------|-------|
| 1 | Re-entering project data into ProEst by hand | 7 | 7 | F | Web app, no MCP. Browser automation works but is more fragile and needs your login session. Phase 2. |
| 2 | Assembling bid packages and inviting subs in BuildingConnected | 8 | 8 | F/E | Highest-value step (sub coverage drives your bids) but also the most complex to automate. Phase 3, approval-gated. |
| 3 | The full "one-click" end-to-end orchestration you described | 9 | 8 | F | The dream. Built by stacking the Quick Wins first, then adding the two web steps. Don't build this in one shot. |

### Fill-Ins (When You Have Time)

Low impact, low effort — good for momentum.

| # | Pain Point | Impact | Effort | Outcome |
|---|-----------|--------|--------|---------|
| 1 | Folder names and file conventions vary project to project | 4 | 2 | F/Q |

*Thankless Tasks (low impact, high effort) are deliberately excluded — not worth your time.*

---

## Skills Recommendations

### SOW Generator
**Skill:** `anthropic-skills:sow-generator`
**Addresses:** Quick Win #3
**Why it helps:** You already built this and it's the engine for step 4 of your workflow. The win isn't the skill itself, it's chaining it so it fires automatically once a project is scaffolded, instead of you invoking it by hand.
**Status:** Already installed

**Try this first:**
> Run sow-generator on the drawings in my latest Dropbox project folder and save the SOW into that same folder.

### Speed to Lead
**Skill:** `anthropic-skills:speed-to-lead`
**Addresses:** Quick Win #1
**Why it helps:** Directly targets the "sits in my inbox" failure. It drafts a fast, human-approved first response to an inbound request so the client hears back immediately while you (or the intake skill) set up the project behind the scenes.
**Status:** Available

**Try this first:**
> New estimate request came in — draft me a same-day acknowledgment to the client and tell me what I need to kick off the project.

### Schedule
**Skill:** `anthropic-skills:schedule`
**Addresses:** Quick Win #1 (the Automate step)
**Why it helps:** Once your intake skill exists, schedule lets it run on its own — check Gmail for new estimate requests every morning and pre-stage the project before you've finished coffee. This is what makes intake stop depending on you noticing the email.
**Status:** Available

**Try this first:**
> Every weekday at 7am, check my inbox for new estimate requests and set up any new ones using my estimate intake workflow.

### Skill Creator
**Skill:** `anthropic-skills:skill-creator`
**Addresses:** Quick Wins #1–3 (bundled)
**Why it helps:** This is how you build the custom Estimate Intake skill in the blueprint below — the one that chains inbox to Dropbox to SOW into a single command.
**Status:** Available

**Try this first:**
> Use the blueprint in my self-assessment to build my estimate-intake skill.

---

## Your First Skill Blueprint

This is the bridge from assessment (Audit) to action (Optimize → Automate).

**Pain point:** The manual relay from "estimate request hits my inbox" to a set-up project — Dropbox folders, SOW, and the start of a bid package — done by hand across four systems.
**Outcome type:** Efficiency
**Estimated impact:** 3 to 5 hours/week recovered, plus the death of the "sits in my inbox" delay

### What this skill would do

Takes a new estimate request and automatically scaffolds the project: builds the standard Dropbox folder structure, drops in the plans and specs, runs sow-generator to produce the SOW, and stages the next steps for ProEst and BuildingConnected — pausing for your approval before anything goes out to subs.

### When you'd use it

**Trigger phrases:** "new estimate intake", "set up this estimate", "intake this bid", "kick off [project name]", "new bid came in"

### What it needs from you

The client request (forwarded email or pasted text), the project and client name, the trade scope, and the drawings/specs (attached or a path). Everything else it derives or asks for once.

### How it works (high-level steps)

1. Parse the estimate request — pull out client, project name, due date, scope, and attachments.
2. Scaffold the standard Dropbox project folder structure and drop the plans and specs into it.
3. Run sow-generator on the drawings to produce the SOW Excel file, saved into the project folder.
4. Prepare the ProEst project setup (Phase 2: via browser automation, or output a ready-to-paste setup sheet until then).
5. Stage the BuildingConnected bid package and suggested sub invites (Phase 3) — and stop for your approval before sending anything.

### What it produces

A fully set-up project: populated Dropbox folders, a finished SOW Excel file, a ProEst project (or setup sheet), and a draft BuildingConnected bid package — plus a one-line status of what's done and what needs your click.

### Buyback Rate (delegation threshold)

Your Buyback Rate is **Annual Revenue ÷ 2,000 ÷ 4**. Any task at or below that hourly rate is a candidate to delegate to an agent.

**Calculation for you (using the $175K midpoint of your $100K–$250K band):**
- Annual revenue: ~$175,000
- ÷ 2,000 (annual working hours) → **$87.50/hour** cost-of-time
- ÷ 4 (the buyback factor) → **~$22/hour** delegation threshold

Clicking folders into existence and re-typing project data into ProEst is well below $22/hour of value. It's a textbook delegation candidate — the cost of building this skill is recouped fast.

### Define-Outcome rubric

- **Desired outcome:** A new estimate request goes from inbox to a fully staged project — folders, SOW, and a drafted bid package — with one command and one approval click.
- **Quality bar (one measurable):** Every project folder follows the exact standard structure and the SOW passes sow-generator's QA with zero hallucinated line items. Nothing reaches a sub without your approval.
- **Coaching loop:** First two weeks, spot-check 100% of intakes. Once folder structure and SOW are reliably correct, drop to spot-checking 1 in 3. A wrong folder, a hallucinated line item, or anything auto-sent to a sub triggers a course correction.

### Validation plan

- **Three real inputs:** Three actual past estimate requests — ideally one clean one with full drawings, one with a messy/partial scope, and one from a repeat client.
- **Edge cases to test:** (1) a request with no drawings attached, (2) an oversized plan set that strains sow-generator.
- **Brand/VOC check:** Any sub-facing or client-facing copy (the acknowledgment, the bid invite) must use your builder-to-builder voice — blunt, no corporate buzzwords. If it drifts, add a brand-voice read step before generation. Note: you don't currently have a saved `voc.md`/`brand-voice.md` file, so capturing one would make this sharper.

### Two-week measurement plan

Capture the baseline BEFORE turning the skill on:
- **Time today:** ~45–90 min of setup per project
- **Cost today:** ~$65–130 per project (at $87.50/hr)
- **Error rate today:** Occasional missed folder or delayed start when slammed

After two weeks:
- **Time with agent:** ~10 min review per project
- **Cost with agent:** Token cost + your review time
- **Error rate with agent:** Track wrong folders / SOW issues
- **Verdict:** Keep, refine, or kill

### Ready-to-use skill-creator prompt

Invoke `skill-creator` and paste this:

> I want to create a skill called estimate-intake that takes a new BLDG Estimating request and stages the whole project automatically.
> It should trigger when I say "new estimate intake", "set up this estimate", "intake this bid", or "kick off [project name]".
> The skill should: (1) parse the estimate request for client, project, due date, scope, and attachments; (2) scaffold my standard Dropbox project folder structure and drop in the plans/specs; (3) run my sow-generator skill on the drawings and save the SOW into the project folder; (4) prepare the ProEst project setup; (5) stage the BuildingConnected bid package and suggested sub invites, pausing for my approval before sending anything to subs.
> It should output a set-up project (Dropbox folders, SOW Excel, ProEst setup, draft bid package) plus a one-line status of what's done and what needs my click.
> Build it in phases: the Dropbox + SOW chain first (those work today via filesystem and my existing skill), then add the ProEst and BuildingConnected steps via browser automation.
> Here's the full context: see self-assessment-2026-06-30.md.

---

## What's Next: The AOA Path

### Audit (Complete)
Seven pain points, three Quick Wins, primary focus Efficiency. This report is your roadmap.

### Optimize (Next Step)
Take the blueprint above into `skill-creator` and design the estimate-intake skill. Build the Dropbox + SOW chain first — it works today with no browser automation and proves the value fast.

### Automate (Final Step)
Once the skill is reliable, use `schedule` to have it check your inbox every morning and pre-stage new estimates. The "sits in my inbox" problem disappears, and you get 3 to 5 hours a week back.

**Your recommended first action:** Run `skill-creator` with the blueprint above and build Phase 1 (inbox → Dropbox → SOW). We can do that in the next message if you want.

---

*Generated by the Build With AI self-assessment skill on 2026-06-30.*
*Framework: AOA (Audit → Optimize → Automate) by Return My Time.*
