# BLDG Labs Product Portfolio

What each product/service ACTUALLY is and its current state. Updated when Matt corrects understanding.

## Live / Active

### AI Opportunity Assessment
- **What it is:** The paid front-door product. A workflow-level review of where custom AI returns the most time and money across a contractor's operation, scored by payback and sequenced into a build plan. This is paid diagnosis and prioritization, NOT implementation discovery (that comes after a workflow is chosen, as phase one of the build).
- **Price:** $1,500 fixed, credited toward the first build.
- **Codebase:** live landing page at `app/assessment/` (bldglabs.ai/assessment); profile-driven PDF generator at `scripts/assessment/` (render.mjs engine, blocks.mjs opportunity menu, per-prospect profiles). Sample reports at `public/assessment-sample*.pdf` (GC tier + two sub tiers).
- **Funnel:** demo or direct outreach → $1,500 Assessment → pick one workflow → scoped build → retainer/seat.
- **Current state:** Built. Live. Downloadable samples. Transcript-to-profile workflow documented in `scripts/assessment/README.md`.
- **Brand law:** estimating is assist-only (setup, cost-library, assembly, pricing, proposals). Takeoff stays with the human estimator. Scheduling leads recommendations.

### BLDG Capture
- **What it is:** Speed-to-lead automation for roofers. Missed call → SMS within seconds → AI intake (qualify, photos, satellite scope) → priced lead to the roofer. Plumbing spin-off planned.
- **Codebase:** `/Users/mattnicosia/dev/BLDG Capture` — Supabase/Twilio/Claude/Next.js. SMS, voice, roofintel, multi-tenant dashboard, live demo, proposals, Stripe, CRM stubs, CGO agent (LangGraph + Slack approval).
- **Gaps to complete offer:** public landing/signup, trial, tiered proposals, e-sign + deposit, scorecard, confidence gating on heuristic roofs, pricing memory, finish CGO pipeline, dash UX.
- **Current state:** Built. Running. Live users. No revenue yet.
- **Revenue model:** Solo ~$397/mo, Standard ~$500/mo, Storm ~$749/mo + setup.
- **NOT:** A "lead gen widget" for GCs.

### BLDG Arrival (was working name: SiteWork / construction web)
- **What it is:** Productized websites for old-school GCs with weak/zero online presence. AI-built, construction-specific, section of bldglabs.ai.
- **Name:** **Arrival** locked 2026-07. Noun. Unmodified real word. Family: VANTAGE, KEYSTONE, CADENCE, VISION, CAPTURE, ARRIVAL.
- **Best money model:** Core ~$200/mo or ~$2,000/year prepay; optional Pro/menu later.
- **Ship first:** Core reliable (site + host + changes + reporting). AIOS-style pipeline: intake → Claude/Grok brain → image gen when available → HTML site → deploy.
- **Current state:** Offer designed. Name locked. Full multi-tenant product not shipped yet.

## Candidate / Planned offers

### AI Employees (managed seats) — skill: `bldg-ai-employees`
Sell the **role** ("Estimating Coordinator", "Project Engineer"), not "buy software."

| Role | Price target | Job to be done | Notes |
|---|---|---|---|
| Estimating Coordinator | ~$1,500/mo | Bid invites, sub chase, bid tab, cost-library *proposals*, digests | NOT takeoffs. Sub outbound: draft → daily approve first 14 days |
| Project Engineer | ~$2,000/mo | Submittals, RFIs, doc control, minutes, daily reports, closeout support | Broad market; high human PE churn |
| Bundle | ~$3,500/mo | Both seats | Optional ~$1,500 / 14-day pilot |

**Model economics signal (2026-07):** Grok 4.5 ~1/10 Fable cost, 10–15× faster. Tools are not the moat. Domain + Capture/Arrival + phone network are.

**Brand law:** AI assists estimate SETUP, cost library structure, assembly, pricing, proposals only. Takeoff stays human.

## Stabilize first / monetize last

### NOVATERRA
- Estimating assist product. Buggy / data-loss history. Zero paid users posture: **stabilize first, monetize last.** Do not rank high on immediate revenue until state changes.

## Not BLDG Labs products
- Confirm before inventing or scoring side tools as core portfolio lines.
