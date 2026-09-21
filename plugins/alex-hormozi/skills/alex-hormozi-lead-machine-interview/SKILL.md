---
name: alex-hormozi-lead-machine-interview
description: Run a structured 12-18 question interview about a user's business, then deliver a tailored lead-generation plan — which of the Core Four advertising methods to start with (warm outreach, content, cold outreach, paid ads), a lead-magnet recommendation, a one-page advertising plan with daily actions and volume, the next Lead Getter to add (referrals/employees/agencies/affiliates), and a scaling roadmap. Use this skill whenever the user wants to be guided/interviewed to figure out how to get more leads or customers, says things like "help me get more leads/customers," "interview me about my marketing," "what's the best way to advertise my business," "build me a customer-acquisition plan," or wants a personalized lead-gen recommendation rather than a generic explanation. Trigger it when the user wants a guided, question-driven path to a lead-generation plan even if they don't say "leads" or "interview."
---

# Lead Machine Interview

This skill interviews the user about their business, then delivers a **tailored lead-generation plan**: the right Core Four method to start with, a lead-magnet recommendation, a concrete one-page advertising plan with daily actions and volume, the next Lead Getter to add, and a scaling roadmap. The book's method is to pick **one** method and max it before adding more — so the deliverable focuses their effort, not scatters it.

**Read `references/lead-generation-playbook.md` before and during the process.** It is the canonical source for the engagement layer, the Core Four, the Lead Getters, More/Better/New, and the benchmarks. Ground the interview and the plan in it.

## How the interview works

Ask **12–18 questions** in **small batches (3–5 at a time)**, plain language, adapting follow-ups to answers. Acknowledge what you learn between batches. Skip anything already answered earlier in the conversation. If an interactive question/options tool is available, use it for the multiple-choice items (easier on mobile); ask open-ended items as prose.

### Question bank (cover these; starred are essential; pick/adapt 12–18)

**What & to whom**
1. ★ What do you sell, in a sentence or two?
2. ★ Who exactly is the ideal customer, and where do they congregate (lists, communities, platforms, places)?
3. ★ What do you charge, and is the sale quick/impulse or considered/expensive? (decides core-offer-direct vs lead-magnet-first)
4. Roughly what does it cost you to deliver one customer, and what's a customer worth over their lifetime? (LTGP)

**Resources & current state**
5. ★ Do you have more **time** or more **money** right now? (steers warm/content vs ads/cold)
6. ★ What are you doing today to get leads, and what's working / not?
7. How many leads/customers are you getting now, and how many do you want?
8. Do you have an audience or contact list of any kind (followers, past customers, email/phone contacts)?

**Engagement layer**
9. ★ Could you give away something free and genuinely valuable that solves a narrow problem and naturally leads to your paid offer? (lead-magnet candidate)
10. Is your core offer already strong (do people who hear it tend to buy), or does it need work? (offer vs leads problem)

**Lead Getters & capacity**
11. Do your customers refer others now? Is your product good enough that they would?
12. Do you have any employees, or is it just you? (can you delegate advertising yet?)
13. Are there other businesses whose audience is full of your ideal customers? (affiliate candidates)
14. Have you used agencies or paid help before — and is there a platform/method you want to learn?

**Constraints & goals**
15. ★ What's your #1 goal — more leads, cheaper leads, more reliable leads, or scaling an existing channel?
15b. ★ Constraint tree: are margins healthy, and do you have unused delivery capacity? If yes to both, the fix is usually ads/offer/sales - not a new product. What is the real bottleneck (leads, close rate, capacity, cash)?
15c. Are you advertising one proven winner, or spreading paid/affiliate across many SKUs? (Organic can show range; paid should pick a hero.)
16. How much time per day can you commit to advertising? (Rule of 100 vs Open to Goal)
17. Any legal/compliance sensitivities (claims, "free", SMS/cold-contact rules, regulated industry)?
18. What have you tried that flopped, or what's off-limits?

Fold in the starred essentials, choose a fitting set, and stop once you can plan responsibly (at least 12 unless the user cuts it short).

## Delivering the plan

Restate their situation in 2–3 sentences, then deliver:

**1) The starting method (one clear pick).** Which of the Core Four to start with and *why*, given their time-vs-money and where their customers congregate. Resist recommending all four — one, maxed.

**2) Lead magnet recommendation (or "advertise the core offer directly").** If a lead magnet fits, specify it: the narrow problem, the type (reveal/sample/one-step), the delivery (software/info/service/physical), and the CTA.

**3) The one-page advertising plan:**

```
### Daily advertising plan
- Who: you (for now)
- What: [core offer or named lead magnet]
- Where: [specific platform]
- To whom: [audience / list source]
- When: [time block — e.g., first 8 hours / morning block]
- Why: get [N] engaged leads
- How: [the specific Core Four actions]
- How much: 100/day (Rule of 100) or Open to Goal: [outcome]
- How many: [follow-up touches / retargets]
- How long: 100 days (or until the goal)
Expected: ~[benchmark] engaged leads → ~[N] customers
```

**4) The 30-day cash check.** Whether a customer repays CAC + fulfillment within 30 days (client-financed acquisition); if not, suggest the upsell that would make the machine self-fund — and point to the money-model skills for the full sequence.

**5) The next Lead Getter.** Which to add once the first method is reliable (referrals first for almost everyone — include the specific give + ask moves), and why, given their stage.

**6) Scaling roadmap.** More → Better → New, the constraint to watch, and roughly where they sit on the seven levels.

Close with the single first action to take today and a reminder that volume negates luck — the most common failure is doing a fraction of the required volume.

## Style & guardrails

- Conversational during the interview; concrete and numeric in the plan (real volume, cadence, benchmarks, literal wording).
- Name specific levers (the Core Four method, the lead-magnet type, the referral ask), not vague categories.
- Tie everything to **engaged-lead flow** and **LTGP:CAC**.
- Respect ethics (playbook §10): advertising works with volume; don't be sketchy; don't personalize failure; honor any compliance sensitivities they flagged (e.g., cold-contact / claims rules).
- If the real bottleneck is the offer, hand off to `alex-hormozi-grand-slam-offer-interview`; if it's monetization/sequencing, to `alex-hormozi-money-model-interview`. If the user wants to skip the interview, fall back to `alex-hormozi-lead-machine-architect` design mode.
