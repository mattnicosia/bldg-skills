# Signal Source Rubric

This rubric tells the skill — and the Operator running it — how to evaluate a candidate signal source. The rubric defines four source categories, lists example source types per category, sets the trust criteria every source must meet, calls out anti-patterns to reject, and forces a "why this source exists" justification for every entry.

The skill reads this file at workflow step 3 (source categorization) before drafting the user's source list.

## The four source categories

Every source belongs to exactly one of these four categories. If a source doesn't fit, drop it — the categories are designed to cover the full intelligence surface, and a source that fits none of them is probably noise.

### 1. Customer / audience

**Definition:** Where your buyers go to talk about the problem you solve. Their words, their venues, their tone — not vendor marketing about them.

**Example source types:**

- Subreddits where buyers compare options (e.g., r/<vertical> + r/<job-title>)
- Review sites with categorical search (G2, Capterra, TrustRadius, ProductHunt) — read the negative reviews
- Forum threads tagged with the problem space (Stack Overflow, IndieHackers, Hacker News)
- X/Twitter accounts of practitioners and operators in your category — NOT vendors
- Substack newsletters written by people doing the job your buyer does
- LinkedIn posts from people in the buyer's title (search "<title>" + relevant keywords)

### 2. Competitor

**Definition:** What your competitors are shipping, charging, hiring for, and signaling. Movement matters more than marketing.

**Example source types:**

- Their public changelog or release notes page
- Their LinkedIn employee posts (especially product/eng/sales hires posting about their work)
- Pricing page snapshots over time (using a service that diffs page changes)
- Their G2/Capterra page — read both the praise and the criticism
- Their job postings (signal of where they're investing — "Senior PM, Outbound" tells you they're going outbound)
- Their conference talks and webinar recordings
- Their funding announcements and investor letters (where available)

### 3. Market / category

**Definition:** The shifts in your buyer's world that change priorities. Regulations, tech trends, economic conditions, category-defining events.

**Example source types:**

- Analyst reports (selectively — Gartner, Forrester, IDC, vertical-specific firms; favor those with data, not opinion)
- Industry-specific newsletters with editorial filter (NOT aggregators)
- Regulatory filings if relevant (SEC for public companies in your space, agency rulings)
- Conference talks (especially the ones that don't make it into mainstream coverage)
- Podcasts focused on your category (find the 1–2 with the most thoughtful host, skip the rest)
- Government data sources (BLS, Census, sector-specific agencies)

### 4. Internal sales / customer feedback

**Definition:** Your own first-party signal. The richest, most underused source for most operators.

**Example source types:**

- Support ticket synthesis (group by theme weekly, surface emerging patterns)
- Sales call transcripts (key objections)
- Churn interviews (the highest-signal source most teams ignore)
- NPS comments and verbatims
- Win/loss analyses (what closed vs. didn't, and why)
- Customer onboarding feedback in the first 30 days

## Trust criteria

Every source must pass these four bars before it goes in your stack:

1. **Specificity.** Does it discuss your specific problem space, not "AI" or "tech" generally? A source that publishes 10 articles a week on every topic is rarely useful.
2. **Recency.** Frequency of updates. A blog updated once a year is a reference doc, not a signal source. Daily/weekly cadence preferred.
3. **Signal-to-noise.** High-quality posts as a fraction of total posts. A subreddit with 1,000 daily posts but 5 worth reading is fine if you can filter; a subreddit with 5 daily posts and 5 worth reading is better.
4. **Decision-relevance.** Does reading this source actually change a decision? If you can't name a decision your last 3 reads of this source informed, drop it.

## Anti-patterns — reject these

- **Vague generalist newsletters.** "AI weekly" / "Tech digest" / "Founder insights" — too broad to inform your specific decisions.
- **Social aggregators with no editorial filter.** Aggregators that re-post everything in a topic produce volume without quality. Skip.
- **Vendor blogs from your category.** They're marketing, not signal. Read once for positioning research; don't weekly-monitor.
- **Sources that produce volume without specificity.** A weekly "100 things in AI this week" newsletter is harder to act on than a focused 5-item rundown.
- **Generic LinkedIn thought leadership.** Most LinkedIn posts in your category will be hot takes from people without the data. Filter aggressively.

## "Why this source exists" — required for every source

Every source in the stack must have a one-sentence justification that ties it to a downstream decision. Format:

> "<source>: monitored to inform <decision-type> in <system>."

Examples:

- "r/construction-tech: monitored to inform marketing content angles in Marketing System."
- "Acme Competitor's pricing page: monitored to inform pricing/packaging decisions in Sales System."
- "BLS construction sector report: monitored to inform capacity planning in Operations System."
- "Internal churn interview synthesis: monitored to inform retention skill iteration in Operations System."

If you can't write a sentence in this format for a source, the source doesn't belong in the stack.

## Decision-type catalog (what downstream decisions feed into)

To make the "why" sentence concrete, here are the decision types each system produces:

- **Marketing System** — content angles, positioning shifts, distribution channel changes
- **Sales System** — objection responses, proposal language, follow-up timing
- **Operations System** — process improvements, capacity decisions, automation targets
- **Finance System** — pricing changes, margin focus, allocation shifts
- **Intelligence System (recursive)** — new source candidates surfaced by existing sources

A signal that doesn't feed any of these decision types isn't a signal. It's news.
