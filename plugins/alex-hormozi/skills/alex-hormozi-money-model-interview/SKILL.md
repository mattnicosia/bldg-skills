---
name: alex-hormozi-money-model-interview
description: Run a structured 12-18 question interview about a user's business, then deliver three tailored "money models" — complete offer sequences (attraction → upsell → downsell → continuity) engineered to maximize cash collected per customer within 30 days. Use this skill whenever the user wants to be guided/interviewed to figure out how to monetize or price their business, product, app, course, agency, SaaS, or service; says things like "help me figure out my pricing," "interview me about my business," "what's the best way to make money from X," "build me a monetization plan," "design my offers," or wants a personalized recommendation rather than a generic explanation. Trigger it when the user wants a guided, question-driven path to a monetization strategy even if they don't say "money model" or "interview."
---

# Money Model Interview

This skill interviews the user about their business and then delivers **three tailored money models** — complete, sequenced offer stacks designed to recoup customer-acquisition cost within ~30 days.

**Read `references/offer-playbook.md` before and during this process.** It is the canonical source for every offer type, the rules, and the pricing heuristics you'll apply when designing the recommendations. Ground the entire interview and every recommendation in it.

## How the interview works

Ask **12–18 questions**, delivered in **small batches (3–5 at a time)**, not all at once and not one-by-one. Use plain language. After each batch, briefly acknowledge what you learned, then continue. Adapt follow-ups to their answers — if something is unclear or a big opportunity appears, probe it. Skip questions already answered earlier in the conversation.

If interactive selection UI is available (e.g., a question/options tool), you may use it for the multiple-choice items to make answering easier on mobile; otherwise just ask in prose. Open-ended items ("what do you sell?") are always asked as prose.

### The question bank

Cover these areas. Pick/adapt 12–18 total; the starred ones are essential.

**What they sell & to whom**
1. ★ What do you sell, in one or two sentences?
2. ★ Who's the ideal customer, and what's the painful problem you solve for them?
3. Is it a one-time purchase or naturally recurring/ongoing?
4. Do customers go through a "hyper-buying" moment (new baby, wedding, new business, new hobby, getting fit) when they buy?

**Money & unit economics**
5. ★ What's your current main price (and is it one-time or recurring)?
6. ★ Roughly what does it cost you to *acquire* one customer (ad spend, sales effort)?
7. Roughly what does it cost you to *deliver/service* one customer?
8. ★ How long does it currently take to make your acquisition cost back? (days / months / never tracked)
9. What's your current refund/chargeback/cancellation rate, roughly?

**What they already have to offer**
10. ★ Besides the main thing, what *else* could you sell them next — more of it, a better version, or something complementary? (List anything, even rough ideas.)
11. Do you have anything you could give away as a high-value bonus that costs you little (past content, onboarding, a tool, community access)?
12. Can customers get a clear, measurable *result* you could attach a goal or guarantee to?

**Sales motion & constraints**
13. How do customers buy — self-serve online, a sales call, in person, an app?
14. ★ Do you currently make any offer *after* the first sale (an upsell), and any offer when someone says *no* (a downsell)? If so, what?
15. How tight is your cash right now — do you need cash up front fast, or can you afford to wait for profit? (This decides how aggressively to front-load.)
16. Are there legal/regulatory sensitivities (e.g., around "free," giveaways, health, finance)?

**Goals**
17. ★ What's the #1 goal: more customers, more profit per customer, faster cash, or more recurring revenue?
18. Is there anything you've tried that flopped, or anything off-limits?

Don't robotically ask all 18 — choose the set that fits, fold in the starred essentials, and stop once you have enough to design responsibly (always at least 12 unless the user cuts it short).

## Delivering the recommendation

After the interview, restate their situation in 2–3 sentences (so they know you understood), then deliver **three complete tailored money models**. Three is the right number: it gives a real strategic choice (the book teaches building *one* model, perfected one stage at a time — so present three, then tell them which to build first).

Frame the three as distinct strategies, each a full stage-1→stage-3 sequence with specific named offers, numbers, and customer-facing wording:

- **Model 1 — Cash-Max (front-load):** maximizes cash collected in the first 30 days. Favor it when cash is tight. Lean on aggressive attraction + anchor/classic upsells + bulk-prepaid continuity.
- **Model 2 — Balanced:** strong 30-day profit while building durable recurring revenue. The default recommendation for most.
- **Model 3 — Volume/Continuity-Max:** maximizes number of customers and long-term recurring revenue, accepting lower upfront cash. Favor it when they can afford to wait and want a subscription base.

For **each** model, lay it out as:

```
### Model [N]: [Strategy name]
Best if: [the condition under which this is their best choice]

- Stage 1 — Attraction: [named offer] — [entry price] — "[what the customer hears]"  (why it fits: ...)
- Stage 2 — Upsell: [named offer] — [price] — "[the line]"  (solves the next problem: ...)
- Stage 2 — Downsell (the no path): [named offer + the fallback rungs with numbers]
- Stage 3 — Continuity: [named offer] — [price set via the pricing heuristics] — then a bulk prepaid upsell rolling into month-to-month.

30-day math: [cash collected per customer in 30 days vs. cost to get + service; does it clear the good-model bar / how far from the $100M bar].
```

Then close with:
- **My recommendation:** which of the three to build *first*, and why, given their #1 goal and cash position.
- **First move:** the single offer to implement first and make reliable before adding anything else (reinforce one-offer-at-a-time, raise-prices-in-stages, simple-scales-fancy-fails).

## Style & guardrails

- Conversational and encouraging during the interview; concrete and numeric in the recommendation. Always name the *specific* offer from the playbook, not just a category.
- Tailor every offer to *their* business — translate canonical offers when needed (e.g., a "win your money back" analog for SaaS) and say so.
- Tie everything back to **cash collected within 30 days**, the metric the framework optimizes.
- Respect the ethics rails (playbook §8): refunds on request, no hard-selling weak products, obey law especially around "free"/giveaways, transparency, deliver what you sell, never the same thing for less. If they flagged regulatory sensitivities, steer away from risky structures and say why.
- If the user wants to skip the interview and just get models, fall back to the `alex-hormozi-money-model-architect` skill's design mode with whatever context you have.
