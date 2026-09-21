# Self-Assessment Question Bank

Master question bank for the AI Readiness Self-Assessment, aligned to the Three Outcomes methodology. Every question maps to one or more outcomes: **Effectiveness** (revenue), **Efficiency** (time saved), **Quality** (customer experience).

---

## How to Use This Bank

**Tags:** `[E]` = Effectiveness, `[F]` = Efficiency, `[Q]` = Quality

**Tier control** (set in Step 0):

| Tier | Universal (A1+A2) | Outcome-Specific (A3-A5) | Industry (B) | Closing |
|------|-------------------|--------------------------|--------------|---------|
| Quick Scan | 3-4 questions | 2 from primary outcome | Skip | 1-2 |
| Standard | 3-4 questions | 3-4 primary + 2-3 secondary | 3-4 from matched | 1-2 |
| Deep Dive | 3-4 questions | All primary + 3-4 secondary | 5-7 from matched | 1-2 |
| Custom | All | All until user stops | All until user stops | 1-2 |

**Question selection priority:** For each section, prefer questions that (1) surface actionable pain points with time estimates, (2) match the user's business type from context files, (3) are most likely to reveal quick wins.

**Delivery format:** Use AskUserQuestion for each. Convert open-ended questions to multiple-choice where possible. Always allow a free-text option for nuance.

**Skip logic:** If a question is already answered in context files (about-me.md, working-style.md), skip it and note why: "I can see from your about-me that [detail], so I'll skip this one."

---

## Section A: Universal Questions

### A1: Outcome Prioritization

Ask 1-2 of these to anchor the assessment to their primary desired outcome.

**Q1** `[E] [F] [Q]`
"If AI could deliver just one result for your business in the next 90 days, which would matter most: making more money, getting hours back, or delivering a better experience to your clients?"

> Anchors the entire assessment to their primary desired outcome. Listen for which bucket they gravitate toward.

AskUserQuestion version:
```
"If AI could deliver one result in the next 90 days, which matters most?"
Options:
- Making more money (Effectiveness)
- Getting hours back in my week (Efficiency)
- Delivering a better experience to my clients (Quality)
- Honestly, all three — help me prioritize
```

**Q2** `[E] [F] [Q]`
"When you think about what's holding your business back right now, is it more about not having enough revenue coming in, not having enough time to do everything, or not being able to serve clients the way you want to?"

> Reveals their current constraint and frames AI as a solution to that specific problem.

**Q3** `[E] [F] [Q]`
"If you could wave a magic wand and fix one thing about how your business operates, what would it be?"

> Open-ended discovery that often reveals their true priority among the three outcomes. Use free-text input.

### A2: AI Literacy & Baseline

**Q4** `[F]`
"On a scale from 'I never touch AI' to 'I use AI all day, every day,' where would you rate your current AI usage?"

> Establishes baseline AI literacy and comfort level. Affects recommendation complexity.

AskUserQuestion version:
```
"How would you describe your current AI usage?"
Options:
- I rarely or never use AI tools
- I dabble — ChatGPT here and there
- I use AI daily for specific tasks
- AI is woven into most of my workflows
- I'm building custom automations and agents
```

---

### A3: Effectiveness Discovery (Revenue)

Ask these when the user's primary outcome is Effectiveness, or as secondary questions for other outcomes.

**Q5** `[E]`
"How do new leads currently come in, and what happens in the first 24-48 hours after someone raises their hand?"

> Surfaces speed-to-lead issues. Faster response = higher conversion = more revenue.

**Q6** `[E]`
"How do you currently track leads, conversations, and follow-ups? How many potential deals slip through the cracks each month?"

> Exposes CRM underuse and missed revenue from lost follow-ups.

**Q7** `[E]`
"What does your sales process look like from first contact to closed deal? Where do prospects drop off?"

> Identifies conversion bottlenecks that AI can address to increase close rates.

**Q8** `[E]`
"How are you currently generating demand or attracting new business? What's working and what isn't?"

> Reveals marketing and lead generation opportunities for AI-assisted content and outreach.

**Q9** `[E]`
"What percentage of your revenue comes from repeat clients vs. new clients? How do you nurture past clients?"

> Lifetime value and retention opportunities. Often easier wins than new acquisition.

---

### A4: Efficiency Discovery (Hours Saved)

Ask these when the user's primary outcome is Efficiency, or as secondary questions for other outcomes.

**Q10** `[F]`
"Walk me through a typical workday from start to finish. Where does most of your time actually go?"

> Reveals the full workflow, time sinks, and context switching. Foundation for time-saving recommendations.

**Q11** `[F]`
"Which tasks feel repetitive, manual, or mentally draining — the things you wish you didn't have to do anymore?"

> Direct automation targets. These are your quick wins for returning hours.

**Q12** `[F]`
"When you look at your week, what are the top 2-3 activities that consume the most energy but don't directly drive revenue?"

> Identifies low-leverage work that AI can automate or eliminate.

**Q13** `[F]`
"If you could reliably get 5-10 hours back every week, where would you want that time to come from?"

> Anchors ROI expectations and prioritizes which time leaks matter most to them.

**Q14** `[F]`
"Do you find yourself rewriting the same emails, DMs, or messages over and over again?"

> Flags opportunities for templating, AI drafts, or canned responses. Often 2-5 hours/week.

**Q15** `[F]`
"Do you take notes during calls or meetings? What happens to those notes afterward?"

> Entry point for transcription, summaries, and structured data extraction.

**Q16** `[F]`
"Which tools or software do you currently use that feel underutilized or disconnected from each other?"

> Integration and consolidation opportunities. Disconnected tools waste time.

---

### A5: Quality Discovery (Customer Experience)

Ask these when the user's primary outcome is Quality, or as secondary questions for other outcomes.

**Q17** `[Q]`
"How would your clients rate their experience working with you on a scale of 1-10? What would make it a 10?"

> Directly assesses current quality baseline and identifies specific improvement opportunities.

**Q18** `[Q]`
"What parts of your business feel inconsistent, undocumented, or dependent on you personally?"

> Inconsistency hurts client experience. SOPs and AI agents can standardize quality.

**Q19** `[Q]`
"Are there any processes that break down when you're busy, traveling, or away from the business?"

> Identifies fragile workflows that impact client experience during peak times.

**Q20** `[Q]`
"How quickly do clients typically get responses from you? Are there times when response time suffers?"

> Response time is a key driver of NPS. AI can ensure consistent, fast communication.

**Q21** `[Q]`
"What do clients complain about most? What questions do they ask over and over?"

> Reveals friction points in the client experience and FAQ automation opportunities.

**Q22** `[Q]`
"How do you currently collect and act on client feedback?"

> Shows if there's a feedback loop. AI can automate collection and surface insights.

**Q23** `[Q]`
"After the main service is delivered, what follow-up happens — reviews, check-ins, additional value?"

> Post-delivery experience often determines NPS and referrals.

---

## Section B: Industry-Specific Questions

Select the subsection matching the user's industry. If industry was not detected from context files, ask using AskUserQuestion before entering this section.

### Hospitality & Event Venues

Use for wedding venues, event spaces, Airbnb/vacation rental hosts, and hospitality businesses.

**Q24** `[F]` "Walk me through what happens from the first inquiry to the event day itself."
> Surfaces booking, coordination, and handoff workflows.

**Q25** `[Q] [F]` "How do you currently communicate details, timelines, rules, and expectations to clients before their event?"
> Opportunities for automated guides, FAQs, and client portals.

**Q26** `[F]` "What does coordination look like with vendors, planners, or outside partners?"
> Workflow orchestration and communication automation.

**Q27** `[Q]` "How do you handle guest communication related to on-site lodging — check-in, rules, directions, FAQs?"
> High-leverage automation + AI messaging. Directly impacts guest experience.

**Q28** `[E] [Q]` "After an event is over, what follow-up happens — reviews, feedback, referrals, or re-marketing?"
> Reputation management impacts future bookings. Referrals drive revenue.

**Q29** `[E]` "How do you manage seasonal demand fluctuations — pricing changes, staffing, promotional pushes?"
> Dynamic pricing and seasonal campaigns affect revenue optimization.

**Q30** `[E] [Q]` "What does your booking and deposit collection process look like from first contact to confirmation?"
> Payment workflow impacts both conversion (revenue) and client experience.

**Q31** `[E]` "How quickly do you respond to new inquiries? What happens if you're busy with an event?"
> Speed-to-lead for bookings. Delayed responses lose revenue.

---

### Insurance Agencies

Use for insurance agents in commercial lines, personal lines, farm, self-storage, or specialty markets.

**Q32** `[F] [Q]` "Walk me through how you create policy summaries, coverage explanations, and marketing content for clients."
> Explaining complex coverage simply is a time sink. Also impacts client understanding.

**Q33** `[F] [Q]` "For commercial clients: Do you need to quickly research industry-specific risks, compile loss control recommendations, or generate tailored coverage checklists?"
> AI can instantly generate industry risk profiles. Saves research time and improves proposal quality.

**Q34** `[Q]` "What questions do personal lines clients (home, auto, umbrella) ask you over and over again?"
> FAQ automation improves response time and client experience.

**Q35** `[Q]` "What questions do commercial lines clients ask repeatedly about their business coverage?"
> Automated FAQ responses and AI-powered coverage explainers.

**Q36** `[F]` "How much time do you spend researching carrier appetites, coverage comparisons, or underwriting guidelines?"
> Manual research across carrier portals is a huge time drain.

**Q37** `[F]` "What parts of your policy servicing process involve the most paperwork or back-and-forth?"
> Certificate requests, endorsements, claims documentation — automation goldmine.

**Q38** `[F] [Q]` "How do you handle scheduling — client reviews, renewal meetings, claims calls, inspections?"
> Manual scheduling wastes hours. Also impacts client convenience.

**Q39** `[E]` "How do new prospects find you, and what's your process for quoting and winning new business?"
> Lead generation and conversion process affects revenue growth.

**Q40** `[E] [Q]` "How do you stay in touch with clients between renewals to strengthen the relationship?"
> Retention affects lifetime value. Proactive touch improves NPS.

---

### Real Estate / Property Management

Use for residential and commercial agents, brokers, teams, and property managers.

**Q41** `[F]` "Walk me through how you create listing descriptions, marketing copy, and social content."
> Content creation is often the biggest time sink for agents.

**Q42** `[F] [Q]` "For listing photos: Do you need to remove clutter, improve lighting, or virtually stage empty rooms?"
> AI photo tools save editing time and improve listing quality.

**Q43** `[Q]` "What questions do buyers or sellers ask you over and over again?"
> Perfect for templated responses and AI chatbots.

**Q44** `[F] [E]` "Since so much happens in the car, do you lose ideas or tasks because you can't capture them safely?"
> Agents lose leads and tasks while driving. Voice capture saves time and deals.

**Q45** `[F]` "How much time do you spend researching neighborhood stats, school ratings, or local news?"
> Agents need to look like local experts instantly.

**Q46** `[F]` "What parts of your transaction process involve the most paperwork or back-and-forth?"
> Contract prep, contingencies, deadlines — automation goldmine.

**Q47** `[F] [Q]` "How do you handle scheduling — showings, consultations, inspections?"
> Manual scheduling wastes hours and frustrates clients.

**Q48** `[Q]` "For property management: How do you handle tenant communications — maintenance, renewals, reminders?"
> High-volume communication affects tenant satisfaction.

**Q49** `[E]` "How do you track and follow up with past clients for referrals or repeat business?"
> Referrals are the lifeblood of real estate revenue.

**Q50** `[E]` "What's your lead response time? How many leads go cold because you couldn't respond fast enough?"
> Speed-to-lead directly impacts conversion and revenue.

---

### Financial Services / Accounting

Use for accountants, bookkeepers, financial planners, tax preparers, and wealth advisors.

**Q51** `[F]` "Walk me through a typical client engagement from onboarding to deliverable."
> Surfaces the full service workflow and handoff points.

**Q52** `[F] [Q]` "How do you currently collect documents and information from clients — especially during tax season?"
> Document collection is a massive bottleneck. Also frustrates clients.

**Q53** `[F]` "What recurring reports or deliverables do you produce on a regular cadence?"
> Templated report generation and automated data pulls.

**Q54** `[F] [Q]` "How much time do you spend chasing clients for missing documents, signatures, or approvals?"
> Follow-up automation frees hours and improves client experience.

**Q55** `[F]` "How do you stay current with changing tax laws, regulations, or compliance requirements?"
> AI-powered research keeps you current without hours of reading.

**Q56** `[Q]` "What does client communication look like between major milestones — are clients left in the dark?"
> Proactive communication drives NPS. Clients hate silence.

**Q57** `[F]` "How do you handle scheduling for client meetings, especially during peak seasons?"
> Calendar automation during busy season is critical.

**Q58** `[F]` "What parts of your process still involve manual data entry between systems?"
> Data integration and automated reconciliation opportunities.

**Q59** `[E]` "How do clients find you? What's your process for converting prospects to paying clients?"
> Lead generation and sales process affects revenue growth.

**Q60** `[E]` "What services do you turn away because they're not profitable or too time-intensive?"
> AI might make previously unprofitable services viable.

---

### Legal Services

Use for solo attorneys, small law firms, paralegals, and legal consultants.

**Q61** `[F]` "Walk me through what happens from first client inquiry to engagement letter."
> Surfaces intake, conflict checks, and onboarding workflows.

**Q62** `[F] [Q]` "How do you currently handle client intake and initial consultations?"
> Intake form automation and pre-consultation questionnaires.

**Q63** `[F]` "What document types do you draft most frequently? How much is repetitive or template-based?"
> Document automation and AI-assisted drafting opportunities.

**Q64** `[F] [Q]` "How do you track deadlines, court dates, and statute of limitations across active matters?"
> Deadline management. Missing deadlines has severe consequences.

**Q65** `[F]` "How much time do you spend on legal research for each matter?"
> AI-powered legal research can dramatically reduce research time.

**Q66** `[E] [F]` "What does your billing and time-tracking process look like? Where does time slip through?"
> Time capture automation directly affects revenue captured.

**Q67** `[Q] [F]` "How do you communicate case updates to clients? Do clients frequently ask for status updates?"
> Client portal and automated updates improve experience and reduce interruptions.

**Q68** `[F]` "What parts of document review or contract analysis feel most tedious?"
> AI-assisted review, redlining, and clause extraction.

**Q69** `[E]` "How do new clients find you? What's your conversion rate from consultation to engagement?"
> Lead generation and conversion affects revenue.

---

### Healthcare / Medical Practices

Use for private practices, dental offices, therapy practices, chiropractors, and wellness providers.

**Q70** `[F]` "Walk me through what happens from new patient contact to first appointment."
> Surfaces intake, scheduling, and onboarding workflows.

**Q71** `[F] [E]` "How do you handle appointment scheduling, reminders, and no-show follow-ups?"
> Scheduling automation is often the highest-ROI quick win. No-shows hurt revenue.

**Q72** `[F] [Q]` "What does your patient intake process look like? How much is still paper-based?"
> Digital intake saves staff time and improves patient experience.

**Q73** `[Q]` "How do you handle after-visit summaries, care instructions, or follow-up communications?"
> Templated communications improve outcomes and patient satisfaction.

**Q74** `[F]` "What recurring administrative tasks take up the most staff time — verification, billing, authorizations?"
> Administrative automation frees clinical staff for patient care.

**Q75** `[E]` "How do patients currently find and choose your practice?"
> Patient acquisition affects revenue growth.

**Q76** `[Q]` "How do you collect and respond to patient reviews and feedback?"
> Reputation management and NPS improvement.

**Q77** `[F] [Q]` "What documentation or charting tasks feel most time-consuming for providers?"
> AI-assisted documentation frees providers for more patient time.

**Q78** `[E]` "What's your patient retention rate? How do you keep patients engaged between visits?"
> Retention affects lifetime value and practice revenue.

---

### Coaches & Consultants

Use for business coaches, executive coaches, life coaches, consultants, and speakers.

**Q79** `[F]` "Walk me through what happens before, during, and after a 1:1 coaching call."
> Unlocks call prep, summaries, action items, and follow-up automation.

**Q80** `[F] [Q]` "After a coaching call ends, how do insights, homework, or next steps get documented and delivered?"
> High-leverage automation zone. Also improves client accountability.

**Q81** `[F]` "How do you currently prepare for public speaking engagements or workshops?"
> Content reuse, outline generation, and slide drafting opportunities.

**Q82** `[Q]` "What does onboarding a new client or running a coaching orientation look like?"
> Templated workflows and checklists for consistent experience.

**Q83** `[E]` "How are you turning your coaching calls, talks, or ideas into LinkedIn content?"
> Content repurposing drives thought leadership and lead generation.

**Q84** `[Q]` "How do you track client progress, goals, and accountability between sessions?"
> Tracking improves outcomes and demonstrates value to clients.

**Q85** `[E]` "What does your discovery call or sales process look like for converting prospects?"
> Sales process optimization affects revenue.

**Q86** `[E] [Q]` "What percentage of your clients renew or continue working with you? How do you drive retention?"
> Retention directly affects revenue and indicates quality.

**Q87** `[E]` "How are you deciding what to post on LinkedIn or other social platforms?"
> Content strategy and ideation for visibility and lead generation.

---

### Marketing / Creative Agencies

Use for marketing agencies, branding firms, social media managers, graphic designers, and creative studios.

**Q88** `[F]` "Walk me through a typical client project from kickoff to delivery. Where are the bottlenecks?"
> Surfaces project management, approval, and delivery workflows.

**Q89** `[F] [Q]` "How do you handle client briefs, revisions, and approval workflows?"
> Collaboration and feedback loop automation.

**Q90** `[F]` "What does your content creation process look like from ideation to publishing?"
> Content pipeline and production workflow opportunities.

**Q91** `[F]` "How much time does your team spend on repetitive creative tasks — resizing, reformatting, variations?"
> AI-assisted creative production and batch processing.

**Q92** `[F] [Q]` "How do you report on campaign performance to clients? How much time does reporting take?"
> Automated reporting saves hours and improves client transparency.

**Q93** `[Q]` "What does your client communication cadence look like? Do clients frequently ask for updates?"
> Proactive communication improves client experience.

**Q94** `[F]` "How do you handle research — competitor analysis, audience research, trend identification?"
> AI-powered research and insights generation.

**Q95** `[F] [E]` "What parts of your proposal or pitch process feel most time-consuming?"
> Proposal templating affects win rate and efficiency.

**Q96** `[E] [Q]` "How do you measure and demonstrate ROI to clients? What results do clients care most about?"
> Demonstrating value improves retention and referrals.

---

### Executive Coaches

Use for executive coaches, leadership development professionals, and C-suite advisors.

**Q97** `[F]` "Walk me through how you prepare for a coaching session with a C-level executive."
> Executive coaching requires significant prep — company context, challenges, goals.

**Q98** `[Q]` "How do you capture and track leadership development goals and progress across engagements?"
> Longitudinal tracking and pattern recognition demonstrates value.

**Q99** `[F]` "Do you produce written deliverables — 360 feedback summaries, coaching reports, development plans?"
> AI-assisted report generation and synthesis.

**Q100** `[F] [Q]` "How do you manage stakeholder communication — HR contacts, sponsors, boards needing updates?"
> Multi-stakeholder communication automation.

**Q101** `[F]` "What does your process look like for designing custom leadership workshops or offsites?"
> Workshop design, materials creation, and facilitation prep.

**Q102** `[E]` "How are you building your pipeline? Referrals, speaking engagements, or content?"
> Business development and thought leadership for revenue growth.

**Q103** `[F] [Q]` "How do you stay current on leadership research and industry trends relevant to clients?"
> AI-powered research curation keeps you sharp without hours of reading.

**Q104** `[E] [Q]` "What outcomes do your executive clients typically achieve? How do you measure and communicate that?"
> Demonstrating results drives referrals and premium pricing.

---

### Business Consultants

Use for management consultants, strategy consultants, operations consultants, and advisory firms.

**Q105** `[F]` "Walk me through a typical engagement from proposal to final deliverable. Where do you spend the most time?"
> Surfaces the full engagement workflow and time-intensive phases.

**Q106** `[F]` "How do you conduct client research — market analysis, competitive landscape, benchmarking?"
> AI-powered research can dramatically reduce analysis time.

**Q107** `[F]` "What does deliverable creation look like? How much time goes into decks, reports, recommendations?"
> Document and presentation automation opportunities.

**Q108** `[F]` "How do you capture and organize insights from client interviews, workshops, or discovery?"
> Transcription, summarization, and structured data extraction.

**Q109** `[F]` "What recurring frameworks, templates, or methodologies do you apply across engagements?"
> Template libraries and AI-assisted framework application.

**Q110** `[F] [Q]` "How do you manage multiple client engagements without things falling through the cracks?"
> Project management and multi-client workflow automation.

**Q111** `[F] [E]` "How do you handle the proposal and scoping process? How much time does each proposal take?"
> Proposal templating affects win rate and time investment.

**Q112** `[E]` "What does follow-up look like after an engagement — do you nurture past clients?"
> Repeat business and referrals from past clients.

**Q113** `[Q]` "How do clients measure your impact? What metrics matter most to them?"
> Understanding client success metrics improves delivery quality.

---

### Freelancers / Contractors

Use for independent freelancers, contractors, and gig-based professionals across industries.

**Q114** `[E]` "Walk me through how you find and land new clients. What does your sales process look like?"
> Lead generation, outreach, and proposal automation.

**Q115** `[F]` "How do you scope projects, send proposals, and handle contracts?"
> Proposal templating, contract generation, and e-signature workflows.

**Q116** `[E] [F]` "What does your invoicing and payment collection look like? Do you chase payments?"
> Automated invoicing and payment reminders affect cash flow.

**Q117** `[F]` "How do you manage time across multiple clients? What falls through the cracks?"
> Project management and time-tracking automation.

**Q118** `[F]` "What repetitive deliverables do you create that follow a similar structure?"
> Template-based delivery and AI-assisted production.

**Q119** `[F] [Q]` "How do you handle client communication — updates, revisions, feedback loops?"
> Communication workflow affects efficiency and client experience.

**Q120** `[E] [F]` "Are you doing your own marketing and content creation? How much time does that take?"
> Content automation for personal brand and lead generation.

**Q121** `[F]` "What administrative tasks — bookkeeping, taxes, expenses — eat into billable hours?"
> Back-office automation for solo operators.

**Q122** `[E] [Q]` "What do clients say about working with you? How do you collect and use testimonials?"
> Social proof drives new business. Reviews indicate quality.

---

### Virtual Assistants

Use for virtual assistants, online business managers, and remote support professionals.

**Q123** `[F]` "Walk me through a typical day managing your clients. How many are you juggling?"
> Reveals multi-client workflow challenges and context-switching costs.

**Q124** `[F]` "What types of tasks do your clients most frequently delegate to you?"
> Identifies which delegated tasks are most automatable.

**Q125** `[F]` "How do you handle communication across multiple clients — different tools, platforms, preferences?"
> Multi-platform communication consolidation.

**Q126** `[F]` "What repetitive tasks do you do for clients that follow the same steps every time?"
> Direct automation targets that free up capacity for higher-value work.

**Q127** `[F]` "How do you manage your own business operations — invoicing, scheduling, onboarding?"
> VA business operations automation.

**Q128** `[E]` "Are there tasks clients ask for that you turn down because they're too time-intensive?"
> AI tools may enable VAs to offer services that were previously not viable.

**Q129** `[F]` "How do you stay organized across different client systems, logins, and workflows?"
> Tool consolidation and workflow management automation.

**Q130** `[F] [Q]` "What does your client reporting or status update process look like?"
> Automated reporting demonstrates value and saves time.

**Q131** `[Q]` "How do your clients rate your service? What makes you stand out from other VAs?"
> Understanding quality differentiators and client satisfaction.

---

### E-commerce / Retail

Use for online store owners, DTC brands, Etsy/Amazon sellers, and retailers with online presence.

**Q132** `[F]` "Walk me through how a product goes from idea to listed-for-sale. Where are the bottlenecks?"
> Surfaces product listing, photography, copywriting, and catalog management.

**Q133** `[F]` "How do you write product descriptions, titles, and marketing copy? How long per product?"
> AI-assisted copywriting can dramatically speed up catalog creation.

**Q134** `[F]` "What does your inventory management look like? Tracking stock across multiple channels?"
> Inventory automation and multi-channel sync opportunities.

**Q135** `[Q] [F]` "How do you handle customer service — order status, returns, product questions?"
> AI chatbots and support automation improve experience and save time.

**Q136** `[E]` "What does your email marketing look like — campaigns, abandoned cart, post-purchase?"
> Email automation drives revenue recovery and repeat purchases.

**Q137** `[F] [Q]` "How are you handling product photography and visual assets?"
> AI-powered photo editing and lifestyle image generation.

**Q138** `[F]` "What parts of order fulfillment are still manual?"
> Shipping, tracking, and fulfillment automation.

**Q139** `[E]` "How do you analyze sales data and make pricing or promotion decisions?"
> AI-powered analytics and trend identification for revenue optimization.

**Q140** `[E]` "What's your customer retention rate? How do you turn first-time buyers into repeat customers?"
> Retention and lifetime value optimization.

**Q141** `[Q]` "How do customers rate their experience? What drives reviews and referrals?"
> Customer experience and NPS improvement opportunities.

---

### Home Services

Use for cleaning companies, landscaping, pest control, HVAC, plumbing, and home service businesses.

**Q142** `[F]` "Walk me through what happens from first customer call to job completion. Where does time get wasted?"
> Surfaces the full service delivery workflow.

**Q143** `[F]` "How do you handle estimates and quotes? How much time does each one take?"
> Automated quoting and estimate generation.

**Q144** `[F]` "What does your scheduling and dispatch process look like? Mostly manual?"
> Scheduling and route optimization automation.

**Q145** `[Q]` "How do you handle customer communication — confirmations, reminders, follow-ups?"
> Automated messaging improves experience and reduces no-shows.

**Q146** `[E] [Q]` "What does your review collection process look like after a job is completed?"
> Automated review requests drive reputation and new business.

**Q147** `[E]` "How do you currently market your services — Google, social media, referrals?"
> Local SEO and content automation for lead generation.

**Q148** `[F]` "What recurring paperwork or documentation is required for each job?"
> Digital forms and compliance documentation automation.

**Q149** `[E]` "How do you handle seasonal fluctuations in demand?"
> Seasonal marketing automation and capacity planning.

**Q150** `[E]` "How quickly do you respond to new inquiries? What's your conversion rate?"
> Speed-to-lead and conversion optimization affect revenue.

**Q151** `[Q]` "What do customers say about your service? What makes them refer you to others?"
> Understanding quality drivers and referral triggers.

---

### Trades / Contractors

Use for general contractors, electricians, plumbers, builders, and specialty trade businesses.

**Q152** `[F]` "Walk me through a typical project from first contact to final payment. Where are the time drains?"
> Surfaces the full project lifecycle and administrative bottlenecks.

**Q153** `[F]` "How do you create estimates, bids, and proposals? How long does each take?"
> Estimating and proposal automation — often the biggest time sink.

**Q154** `[F]` "What does project documentation look like — change orders, progress photos, inspections?"
> Digital documentation and automated record-keeping.

**Q155** `[F] [Q]` "How do you manage communication with clients, subcontractors, and suppliers?"
> Multi-party communication and coordination automation.

**Q156** `[E] [F]` "What does your invoicing process look like? Progress billing or milestone payments?"
> Invoicing automation and payment tracking affect cash flow.

**Q157** `[F]` "How do you find and vet subcontractors or suppliers for new projects?"
> Vendor management and sourcing automation.

**Q158** `[F]` "Since so much happens on job sites, how do you capture tasks and notes in the field?"
> Mobile capture and field-to-office workflow automation.

**Q159** `[F]` "How do you handle permit applications, compliance documentation, and code requirements?"
> Regulatory compliance and documentation automation.

**Q160** `[E]` "How do clients find you? What's your close rate from estimate to signed contract?"
> Lead generation and conversion optimization.

**Q161** `[Q]` "How do clients rate their experience working with you? What drives referrals?"
> Quality indicators and referral optimization.

---

### Content Creators

Use for YouTubers, podcasters, bloggers, social media creators, and influencers.

**Q162** `[F]` "Walk me through your content creation process from idea to published. Where are the bottlenecks?"
> Surfaces the full production pipeline and time-intensive steps.

**Q163** `[F]` "How do you currently come up with content ideas? System or ad hoc?"
> Content ideation and editorial calendar automation.

**Q164** `[F]` "What does your editing and post-production process look like? Time per piece?"
> AI-assisted editing, captioning, and production automation.

**Q165** `[E] [F]` "How are you repurposing content across platforms — turning videos into clips, posts, blogs?"
> Content repurposing pipelines maximize reach from single efforts.

**Q166** `[Q]` "How do you handle audience engagement — comments, DMs, community management?"
> Community management and response automation.

**Q167** `[E]` "What does your monetization workflow look like — sponsorships, affiliates, products?"
> Revenue management and sponsor communication automation.

**Q168** `[E]` "How do you track performance and decide what content to create next?"
> Analytics automation and AI-powered content strategy.

**Q169** `[F]` "What behind-the-scenes tasks — thumbnails, SEO, show notes — take too much time?"
> Production support task automation.

**Q170** `[Q]` "How engaged is your audience? What's your relationship like with your community?"
> Audience quality and engagement indicators.

---

### Course Creators

Use for online educators, course builders, membership site owners, and digital product creators.

**Q171** `[F]` "Walk me through creating a new course or module from scratch. Where does the most time go?"
> Surfaces the full course development workflow.

**Q172** `[F]` "How do you structure, script, and outline your course content?"
> AI-assisted curriculum design and content outlining.

**Q173** `[F]` "What does your video production and editing workflow look like for course content?"
> Production automation and AI-assisted editing.

**Q174** `[Q]` "How do you handle student onboarding, orientation, and the first-week experience?"
> Automated onboarding for consistent student experience.

**Q175** `[Q]` "What does student support look like — questions, community, coaching calls?"
> Support automation and community management tools.

**Q176** `[Q]` "How do you gather and use student feedback to improve courses?"
> Automated surveys and feedback loops improve quality.

**Q177** `[E] [F]` "What does your launch process look like? How much time goes into each launch?"
> Launch automation — email sequences, webinars, countdown pages.

**Q178** `[F]` "How do you handle ongoing course updates and content maintenance?"
> Content refresh workflows and version management.

**Q179** `[F]` "What's your process for creating supplementary materials — worksheets, templates, quizzes?"
> AI-assisted resource creation and template generation.

**Q180** `[Q]` "What are your completion rates and student outcomes? How do you measure success?"
> Student success metrics indicate course quality.

**Q181** `[E]` "What percentage of students buy additional products or refer others?"
> Lifetime value and referral metrics affect revenue.

---

### SaaS Founders

Use for early-stage SaaS founders, bootstrapped software companies, and micro-SaaS operators.

**Q182** `[F]` "Walk me through your typical week. How do you split time between product, sales, marketing, ops?"
> Reveals time allocation and where AI can free up founder bandwidth.

**Q183** `[Q] [E]` "How do you handle customer onboarding and activation?"
> Onboarding automation affects retention and lifetime value.

**Q184** `[Q] [F]` "What does your customer support process look like? Still handling most personally?"
> Support automation, knowledge bases, and AI chatbot opportunities.

**Q185** `[Q]` "How do you gather and prioritize customer feedback and feature requests?"
> Feedback collection and prioritization automation.

**Q186** `[E]` "What does your content marketing and demand generation look like?"
> Content automation for SEO, social, and thought leadership.

**Q187** `[E]` "How do you handle sales — demos, follow-ups, proposals, closing?"
> Sales process automation and CRM optimization.

**Q188** `[F]` "What recurring operational tasks — billing, reporting, metrics — take founder time?"
> Operational automation and dashboard generation.

**Q189** `[E]` "How do you stay on top of competitor movements and market trends?"
> AI-powered competitive intelligence and market monitoring.

**Q190** `[Q]` "What does your user communication cadence look like — updates, newsletters, in-app?"
> User communication automation and lifecycle messaging.

**Q191** `[E] [Q]` "What's your churn rate? How do you identify and save at-risk customers?"
> Churn reduction directly impacts revenue and indicates quality issues.

**Q192** `[E]` "What metrics do you track most closely? How do you make data-driven decisions?"
> Analytics automation and AI-powered insights.

---

## Closing: Anchoring to Outcomes

Always end the assessment with 1-2 of these. They confirm priority and establish success criteria.

**Q193** `[E] [F] [Q]`
"Based on everything we've discussed, which of these three would have the biggest impact on your business: making more money, getting hours back, or improving your client experience?"

> Confirms priority outcome for final recommendations. May have shifted from initial answer.

AskUserQuestion version:
```
"Based on everything we've discussed, which would have the biggest impact right now?"
Options:
- Making more money
- Getting hours back
- Improving client experience
- [Dynamically generated option based on their #1 stated pain point]
```

**Q194** `[E] [F] [Q]`
"If we could solve just one of the problems we've identified today, which one would make the biggest difference?"

> Prioritizes the single highest-impact opportunity for the quick win recommendation.

**Q195** `[E] [F] [Q]`
"What would success look like 90 days from now? How would you know this assessment was worth it?"

> Establishes measurable success criteria tied to their desired outcome. Use free-text input.

---

## Industry Detection

If the user's industry is not known from context files, use this AskUserQuestion to determine which Section B subsection to use:

```
"What best describes your business?"
Options:
- Hospitality / Events / Venues → Q24-31
- Insurance → Q32-40
- Real Estate / Property Management → Q41-50
- Financial Services / Accounting → Q51-60
- Legal Services → Q61-69
- Healthcare / Medical → Q70-78
- Coaching / Consulting → Q79-87
- Marketing / Creative Agency → Q88-96
- Executive Coaching → Q97-104
- Business Consulting → Q105-113
- Freelancer / Independent Contractor → Q114-122
- Virtual Assistant / Online Business Manager → Q123-131
- E-commerce / Retail → Q132-141
- Home Services → Q142-151
- Trades / Contracting → Q152-161
- Content Creation (YouTube, podcast, blog) → Q162-170
- Course Creation / Online Education → Q171-181
- SaaS / Software → Q182-192
- Other — I'll describe it
```

For "Other," use the universal questions only and lean on free-text responses to identify pain points.
