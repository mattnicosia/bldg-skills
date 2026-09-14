# Example: signal-stack.md for Acme Forecasting

> This is a sample output for a fictional B2B SaaS business: **Acme Forecasting** — vertical CFO software for small-mid construction firms ($5–50M revenue). The skill reads this example at workflow step 6 to anchor on what a finished stack looks like.

**Operator:** Sam Lee, Founder/CEO
**Market focus:** Small-mid construction firms ($5–50M revenue) needing CFO-level forecasting without a full-time CFO
**Reviewer:** Sam (founder), weekly review every Monday morning

## Source list

### Customer / audience (5 sources)

- **r/contractor** — https://reddit.com/r/contractor
  - Why: Where construction firm owners discuss financial pain, software choices, and growing past the spreadsheet phase.
  - Cadence: weekly skim
- **r/Construction-management** — https://reddit.com/r/Construction-management
  - Why: PM-level discussions surface upstream demand for CFO-level visibility.
  - Cadence: weekly skim
- **Construction Dive — comments section** — https://www.constructiondive.com
  - Why: Industry executive readers comment on news with operational context. Comments > articles.
  - Cadence: weekly
- **G2 — Construction Accounting category** — https://g2.com/categories/construction-accounting
  - Why: Buyer language in negative reviews of competitors. The "what didn't work" is gold.
  - Cadence: bi-weekly
- **The Contractor's Compass (Substack)** — https://contractorscompass.substack.com
  - Why: Practitioner-written, focused on financial ops for sub-$50M GCs. Best signal-to-noise in the category.
  - Cadence: weekly (issue drops Tuesdays)

### Competitor (4 sources)

- **Foundation Software changelog** — https://foundationsoftware.com/release-notes
  - Why: Largest competitor in our SMB tier. Their feature shipping rate and target use cases reveal market priorities.
  - Cadence: bi-weekly
- **Sage 100 Contractor pricing page (snapshot diff)** — https://sage.com/products/sage-100-contractor
  - Why: Pricing page changes signal positioning shifts. Use Visualping or similar to diff weekly.
  - Cadence: weekly diff alerts
- **CMiC LinkedIn employee posts** — https://linkedin.com/company/cmic
  - Why: Their senior PMs and product leaders post about customer wins and roadmap themes. Higher signal than corporate posts.
  - Cadence: weekly
- **JobTread G2 page** — https://g2.com/products/jobtread/reviews
  - Why: Adjacent player attacking the SMB construction segment from a different angle. Their reviews surface what SMBs care about that we may be missing.
  - Cadence: bi-weekly

### Market / category (3 sources)

- **Construction Dive — daily newsletter** — https://constructiondive.com/newsletter
  - Why: Macro signal on construction sector economics — affects buyer budgets directly.
  - Cadence: daily skim, weekly synthesis
- **Bureau of Labor Statistics — Construction sector employment** — https://bls.gov/iag/tgs/iag23.htm
  - Why: Leading indicator of buyer demand cycles. Quarterly drops change account-level forecasts.
  - Cadence: monthly check, quarterly deep-read
- **AGC of America industry surveys** — https://agc.org/learn/research-economics
  - Why: Industry trade association produces forward-looking surveys our buyers act on. We act on them too.
  - Cadence: monthly when new releases drop

### Internal sales / customer feedback (3 sources)

- **Sales call transcripts (last 30 days)** — Gong export
  - Why: Top objections this week are top objections in marketing copy next week.
  - Cadence: weekly synthesis (cron-pulled from Gong each Monday morning)
- **Support ticket tag synthesis** — Intercom + Zendesk
  - Why: Themes that surface 3+ times in a week become onboarding playbook updates.
  - Cadence: weekly grouping
- **Churn interview notes** — Notion database
  - Why: Single highest-signal source. We do exit interviews for every >$5K ACV churn. Read every one.
  - Cadence: as-they-happen

## Signal types

The skill flags signals across these types (per interview Q5):

- **Customer pain shifts** — new vocabulary in how buyers describe the problem (e.g., shifting from "cash flow forecasting" to "real-time cost-to-complete")
- **Competitor pricing/feature moves** — pricing page changes, new modules, repositioning
- **Regulatory/market changes** — sector employment shifts, tax law changes affecting construction firms, public-project funding moves
- **Internal sales objection patterns** — objection clusters that show up 3+ times in a week
- **Buyer venue shifts** — when our buyers start showing up in venues we don't watch yet (read VOC monthly to catch this)

## High-priority rubric

A signal is high-priority if it triggers any of these:

1. **Indicates a buyer is about to evaluate alternatives in the next 30 days.** (e.g., a contractor on r/contractor asking "what's everyone using for cost-to-complete?")
2. **Suggests a competitor pricing/positioning shift we should respond to.**
3. **Reveals a sales objection now appearing in 3+ calls in a single week.**
4. **Surfaces a buyer venue we're not currently monitoring.** (Adds it to next month's verification pass.)
5. **Forecasts a sector economic shift that will affect 50%+ of our pipeline within 60 days.**

Anything else is interesting but doesn't drive a decision this week — note it, don't escalate it.

## Review cadence + reviewer

- **Weekly brief:** every Monday 8am local, reviewed by Sam before standup at 9am
- **Monthly verification:** first Monday of each month, reviewed by Sam alongside the weekly brief
- **Stack revision:** quarterly (or triggered by any verification pass that flags 3+ stale sources)

## Validation status

- ✅ 4 source categories present (customer/audience, competitor, market/category, internal)
- ✅ 15 total sources (above the 10-source minimum)
- ✅ Every source has a "why" tied to a specific decision type
- ✅ High-priority rubric defined
- ✅ Review cadence + reviewer named
- ✅ Weekly brief template includes "three decisions" section (see `INTELLIGENCE/weekly-brief-template.md`)
