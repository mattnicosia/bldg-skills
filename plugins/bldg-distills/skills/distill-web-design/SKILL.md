---
description: Distill websites into a compounding web design tactics bank (required
  fonts + motion extraction), then design and Hermes-build sites by client job/category
  physics. Use on a URL (study), client brief (design), Arrival demos, or full implement.
  Entry skill for Matt's web design mastery.
metadata:
  version: 1.1.0
  hermes:
    related_skills:
    - bldg-web-design-tactics
    - fable-website-build
    - web-clone
    - bldg-impeccable
    - bldg-design-eng
    - distill-strategy
    tags:
    - distill
    - web-design
    - tactics
    - fonts
    - motion
    - clients
    - arrival
name: distill-web-design
---

# Distill Web Design

Primary entry for turning reference sites into durable design skill, then **shipping new sites** tuned to the client job (plumbing shop, private school, contractor SaaS, etc.).

This is the umbrella Matt invokes by habit ("distill this site", "design for X"). It loads specialist skills; it does not reimplement impeccable/clone engines.

## Parameters (preset)

- **VAULT_PATH:** `/Users/mattnicosia/matt-vault-v2`
- **HUB:** `07 Sources/Web Design Tactics.md`
- **INTAKE_LOG:** `07 Sources/Web Design Intake.md`
- **BANK_ROOT:** `/Users/mattnicosia/projects/website-clones/_tactics`
- **CLONES_ROOT:** `/Users/mattnicosia/projects/website-clones`
- **CAPTURE_SCRIPT:** `$BANK_ROOT/scripts/site-capture.mjs`
- **DOMAIN_LABEL:** Web Design
- **LENS (study):** Reusable craft moves + **required fonts + motion schemas** (SOURCE/PARTIAL/GUESS) + free-stack reproduce plan.
- **LENS (design):** Category physics + banked tactics for this job code; never clone last reference wholesale.

## Load order

1. This skill
2. `bldg-web-design-tactics` (bank protocol — always)
3. Escalations:
   - **Always prefer** light `site-capture.mjs` on study when Playwright is available
   - `web-clone` when Matt wants DNA/template/full recon or fidelity is L4+
   - `bldg-impeccable` + `bldg-design-eng` before/while production UI

## Modes

### Mode A · Study (URL)

1. **Run capture** (do not skip without stating why):
   ```bash
   node "$BANK_ROOT/scripts/site-capture.mjs" --url "<url>" --slug "<slug>"
   ```
   Reads: `$BANK_ROOT/captures/<slug>/capture.json` (+ screenshots).
2. Fetch HTML (curl) if capture html-only or further DOM copy needed.
3. Classify: category + job code (CALL/FORM/BOOK/ENROLL/BUY/TRIAL/TRUST/MULTI).
4. Fill `sites/<slug>.md` using **SITE_TEMPLATE.md**.  
   **Hard fail if fonts: or motion: yaml blocks missing.**
5. Walk taxonomy categories → tactics. Dedupe via INDEX.
6. For each new motion behavior, prefer linking a `recipes/` free rebuild.
7. Check ANTI_PATTERNS.md — log steal carefully if source uses slop/gimmicks that still work.
8. Vault intake row; report formats below.
9. Optional: escalate web-clone if craft L4+ and Matt wants eng depth.

### Mode B · Design (client brief)

1. Design Spec (job code first).
2. **Extract real metrics from existing copy.** When designing for a real client (not a fictional demo), mine their current site, About page, or owner interviews for accurate numbers. Never guess years-in-business, project counts, or revenue figures. Wrong numbers under a redesign destroy trust faster than no numbers at all. The Montana session used "10+ years" until the real "Since 1984" was found in the hero JS — that gap is a credibility hole. When in doubt, leave the metric out until confirmed.
3. Load **CATEGORIES.md** for that category physics seed.
4. Load INDEX + relevant T-### + recipes.
5. Output tactic stack (5–12) + skips + IA + page plans + risk.
6. Approval unless just ship → Mode C.

Category mismatch check: if seed stack pulls lifestyle-housing defaults onto trade, stop and fix.

### Default execution surface (2026-07-15)

**Fable via Claude Code is the primary quality build path.** For any Arrival preview, client site, or build where Matt expects $20k-grade output, use the protocol in `fable-website-build` (load that skill, then launch Claude Code with `--model fable`). Lead with vision and atmosphere, not T-IDs and section lists. The Smith Cooling session (2026-07-12) proved this: 4 rounds of manual/Delegated builds produced $3k templates, and one Fable prompt produced a cinematic $20k site with air-mass gradients, film grain, glassmorphism gauge, and gradient text.

**Design-before-build rule:** Never launch Fable builds without agreed design direction. On 2026-07-15, Matt stopped a BLDG Vision launch mid-flight to refine the aesthetic via reference imagery first. The correct sequence: D2 audit → define aesthetic direction with concrete references → get explicit approval → write vision-first prompt → launch. Skipping to launch produces $3k templates. The direction IS the value.

**When Matt asks for design references, provide URLs, not technique descriptions.** On 2026-07-15, suggestions like "use T-022 from Wembi" were rejected with "I DON'T LIKE ANY OF THE TECHNIQUES OR REFERENCES YOU PROVIDED — I need to see references with links." Always lead with real site URLs + Playwright screenshots before distilling techniques from them. If web extract is down, use curl + Playwright capture + x_search to find real live URLs.

**Hermes / Kron** for fast fixes (copy changes, photo swaps, single-element patches). For full rebuilds or when Matt says a site looks like a template, escalate to Fable immediately — do not attempt a manual rebuild from memory.

### Mode C · Build

1. Apply stack; cite T-IDs in config comments.
2. Fonts: use **reproduce.free_stack** from site DNA / brand rules — never unlicensed faces from harvest.
3. Motion: free recipes + free GSAP only; no Club redistribution.
4. **Default deploy path:** `npx vercel --yes --prod` from the build folder. Vercel preview URL becomes the live review surface for Matt. Use for all static builds — contractor demos, Arrival skins, client previews. The alias stays stable across re-deploys.
5. **Build-then-iterate:** after first deploy, expect Matt to review and request changes. Patch, redeploy, report the same URL. Do not treat the first deploy as final. The Montana session went through 10+ deploy rounds before settling.
6. Visual loop: Playwright screenshots 1440/768/390 for QA; Matt also views the live URL. For motion verification, use Playwright video recording → ffmpeg frames → vision analysis (see `references/motion-implementation-pitfalls.md`).
7. Arrival demos: edit `~/dev/bldg-labs` (`demo-configs`, `app/arrival/lab/...`).

**Two-track parallel build (Montana session, 2026-07-12):** When stuck on motion/polish after 5+ deploy rounds, or when Matt expresses disappointment with incremental progress, launch Claude Code as a parallel wild-card track. Give it the same assets folder and constraints, ask for total creative freedom, let it run autonomously for 15-25 minutes with three iteration passes. Deploy its output to a separate Vercel URL. Then compare the two versions side-by-side and merge the best of both. The manual build keeps the framework; the autonomous build brings the spark. **Always launch 3 variants in parallel with different creative directions** — Matt expects at least three to compare. See `references/autonomous-fable-builds.md` for the full prompt template, deploy pattern, and verification steps.

**Hero cinema rule (Montana correction):** do not stack a long body paragraph + CTA over a video/photo hero on premium GC, architecture, or lifestyle brands. The hero is the proof — type should be minimal: one thin editorial line at bottom, or a short claim + single CTA. Dense hero text reads marketing brochure, not award-winning firm. Push body copy to a separate manifesto bridge band below the hero (dark brand color, centered, one paragraph max).

**Motion implementation rule (Montana correction):** when Matt asks for scroll-driven motion (parallax, fades, counters, pin-reveal), ship actual JavaScript — not CSS-only approximations. CSS transition and @keyframes are for component-level micro-interactions. Scroll-driven narrative motion requires IntersectionObserver, scroll event handlers, and direct style manipulation in JS. CSS-only iteration after a request for motion reads as stalling. See `references/motion-implementation-pitfalls.md`.
6. Visual loop: Playwright screenshots 1440/768/390 for QA; Matt also views the live URL.
7. Arrival demos: edit `~/dev/bldg-labs` (`demo-configs`, `app/arrival/lab/...`).
6. Visual loop: Playwright screenshots 1440/768/390 for QA; Matt also views the live URL. For motion verification, use Playwright video recording → ffmpeg frames → vision analysis (see `references/motion-implementation-pitfalls.md`).
7. Arrival demos: edit `~/dev/bldg-labs` (`demo-configs`, `app/arrival/lab/...`).

### Mode D · Critique only

**D1 · Critique a reference site (no bank write)** — score + pattern notes after optional light fetch. No bank write. Use when Matt says "rate this" and you haven't already distilled the URL.

**D2 · Audit an existing client site against the bank (diagnostic mode)** — trigger: "rate my site", "audit montanacontracting.com", "tell me what to improve".

1. Fetch the site (HTML minimum; Playwright if available). If site blocks Playwright (403/timeout), fall back to HTML + CSS deep dive — do not stall.
2. Classify category + job code (trade CALL, professional-services TRUST, etc.)
3. Walk the bank's taxonomy dimensions against what the site actually delivers.
4. Score 1-100 using bank-weighted craft standards — weighted by category physics for the site's job code.
5. Pull the top 3 measurable improvements, each cited with T-IDs and measurable outcomes.
6. Report score first, then the three fixes with T-ID citations.

This mode uses the bank as a diagnostic lens, not an extraction target. Do NOT create a sites/ card or mint new T-IDs. If Matt escalates from D2 to Mode B ("design package"), switch modes and produce a full tactic stack, IA, fonts/motion/color plans, and build path. Write design packages to `06 Projects/` in the vault. the URL.

   **D2 · Audit an existing client site against the bank (diagnostic mode)** — trigger: "rate my site", "audit montanacontracting.com", "tell me what to improve".

   1. Fetch the site (HTML minimum; Playwright if available). If site blocks Playwright (403/timeout), fall back to HTML + CSS deep dive — do not stall.
   2. Classify category + job code (trade CALL, professional-services TRUST, etc.)
   3. Walk the bank's taxonomy dimensions against what the site actually delivers.
   4. Score 1-100 using bank-weighted craft standards — weighted by category physics for the site's job code.
   5. Pull the top 3 measurable improvements, each cited with T-IDs and measurable outcomes.
   6. Report score first, then the three fixes with T-ID citations.

   This mode uses the bank as a diagnostic lens, not an extraction target. Do NOT create a sites/ card or mint new T-IDs. If Matt escalates from D2 to Mode B ("design package"), switch modes and produce a full tactic stack, IA, fonts/motion/color plans, and build path. Write design packages to `06 Projects/` in the vault.

## Required study completeness checklist

- [ ] capture.json or explicit blocker
- [ ] fonts yaml (roles + license + free_stack)
- [ ] motion yaml (libs + behaviors[] + free_stack_plan + club_or_paid)
- [ ] primary CTA pattern
- [ ] masterclass axes
- [ ] anti-fits
- [ ] INDEX updated if new T-IDs

## Report formats

### Study
```markdown
## <site> · distill
**Job / code:** …
**Category:** …
**Masterclass:** …
### Fonts (evidence)
- display/body — reproduce free_stack …
### Motion (evidence)
- intensity · libs · free_stack_plan
### New tactics
- T-0xx …
### Reinforced
### Recipes linked
### Steal carefully
```

### Design
```markdown
## Design package · <client>
**Job code:** CALL|…
**Category physics:** trade|…
### Tactic stack
### Skips (with why)
### Fonts plan
### Motion plan (free stack)
### Sitemap / home scroll
### Build next
```

## Intake bootstrap

If missing, create vault intake with columns:

| Date | Site | URL | Job | Category | Masterclass | New IDs | Fonts | Motion | Notes |

## End-state Matt wants

Brief → category physics → tactic stack with fonts+motion plans → Hermes build → Playwright-visible QA → bank compounds.

## Support files

- `references/pipeline-and-pitfalls.md` — re-distill rules, capture honesty, Desktop slash limits, Hermes-first, legal floors
- `references/report-templates.md` — tight study/design report shapes
- `references/site-audit-mode.md` — D2 diagnostic mode: scoring dimensions, T-ID-as-lens, top-3 format
- `references/montana-build-session.md` — complete build session case study: D2→B→C pipeline, press iteration, hero cinema rule, font licensing, category blending
- `references/tresmares-borrow-analysis.md` — scroll-motion techniques borrowable for premium sites
- `references/hover-overlay-pattern.md` — fixed overlay for project previews. Row-expand pushes layout and causes scroll jump. Overlay with pointer-events:none (even when active) avoids infinite flicker loop (Playwright log: \"intercepts pointer events\"). Overlay HTML must exist BEFORE script tags.
- `references/motion-implementation-pitfalls.md` — CSS-only trap, counter animation bug, video verification, Vimeo headless fix, bidirectional IO toggle, press logo scaling trap
- `references/photo-swap-workflow.md` — replacing WordPress banner headers with real project photos. Copy from Downloads, sequential rename, PROJECTS array update, featured card update, deploy.
- `references/scroll-video-verification.md` — Playwright video → ffmpeg frames → vision analysis technique
- `references/interview-for-content.md` — when to interview Matt for real copy instead of generating AI filler. Core values, approach, owner voice, project descriptions.
- `references/press-logo-sourcing.md` — finding and preparing publication logos for press sections. Wikipedia, Condé Nast CDN, SVG approximation. Sizing and color rules.
- `references/autonomous-fable-builds.md` — Claude Code autonomous build: prompt template, multi-variant parallel launches, deploy pattern, verification
- `references/color-extraction-from-logos.md` — extracting hex colors from client's existing logo via vision_analyze (or Pillow fallback). Use when building Arrival previews for clients who have a logo but no documented brand palette.
- `references/subcontractor-pitch-pipeline.md` — D2 audit → Arrival preview build → Vercel deploy → before/after pitch asset for selling Arrival to subs Matt knows. Simplified pipeline with Smith Cooling case study (2026-07-12).
- `references/editorial-design-acceleration.md` — what to do when Matt says a built site looks like a "$3k template": editorial design push, massive type, asymmetric layout, single-accent discipline, photo as art. Smith Cooling case study progression (v1-v5, 2026-07-12).
- `references/arrival-offer.md` — Arrival pricing: one price ($200/mo), no upsells, no ladder. Old machinery deferred.
- `references/arrival-preview-build.md` — Concrete build pipeline: extract real data → single-page HTML with Arrival design rules → Vercel deploy → Playwright QA. Smith Cooling case study included.
- `references/fable-targeted-edits.md` — using Claude Code for in-place targeted edits (not full rebuilds) when Matt has a numbered change list. Prompt template, verification steps, pitfalls.

## Use cases

### Subcontractor pitch pipeline (simplified, 2026-07-12)
When Matt has a personal relationship with a sub whose website is weak: run D2 audit, extract real data, **delegate the build to a subagent with full bank context** (isolated context space for all T-IDs + Arrival presets + real client data), deploy to Vercel, QA with Playwright. Do not build manually from working memory — the quality delta is the difference between "functional" and "remarkable." The offer is one price: $200/mo. No upsells, no annual, no ladder. See `references/subcontractor-pitch-pipeline.md` and `references/arrival-preview-build.md`.

### Bank study (reference URL)
Standard Mode A: capture → classify → site card → mint tactics → INDEX → intake. This compounds the bank. Use when Matt sends a reference URL he admires.

### Client design/build
Mode B → Mode C for a real client with a real brief. Category physics first, bank tactics second. Skip lifestyle-housing defaults on trade jobs. Premium GC uses blend physics.

## Pitfalls (embed)

- **Re-distill known URL:** reinforce T-IDs + refresh capture; do not rebootstrap the whole bank.
- **Desktop:** `/reload-skills` not in Desktop slash palette; skill id is `distill-web-design`, not "distill website".
- **Capture intensity** can over-rank when Club/canvas merely load; verify behavior class before calling L5 theatre required for rebuild.
- **Category autopilot is forbidden:** housing tactics off on trade CALL jobs. **Premium GC blends trade + professional-services physics** — do not score or design a $10M GC against pure roofing standards (Montana session).
- **Visual proof for Matt:** Playwright screenshots in-chat; do not claim we cannot ship Arrival because Hermes lacks Claude-native browser (compensated loop).
- **Capture screenshots may show loader states, not final content:** sites with animated loaders (SVG intro, WebGL preloader, page transitions) can produce screenshots that show the loader instead of the rendered page. The Vectr session (2026-07-15) captured the loader ellipse at 1440px. Verification: after capture, check that screenshot H1 text matches capture.json's h1 field. If screenshots are loader-only, note it as PARTIAL evidence and proceed with HTML+CSS analysis — do not re-run capture expecting a different result (Playwright fires `load` + short wait, not animation-complete detection). The HTML+CSS from curl had full page content, so the study could proceed.
- **Site blocks Playwright (403/timeout):** do not stall. Fall back to HTML-only fetch + CSS deep dive. The HTML + CSS + inline styles alone yield fonts, colors, copy, section structure, and stack signals — enough for a full study or audit without Playwright (Montana session).
- **Metrics must be real:** never guess years-in-business, project counts, or revenue figures for a real client. Wrong numbers under a redesign destroy trust faster than no numbers. When in doubt, leave the metric out until confirmed. The Montana session used "10+ years" until the real "Since 1984" was found in the hero JS.
- **CSS-only iteration reads as stalling:** when Matt asks for scroll-driven motion from a reference site (Tresmares, etc.), ship JS — not font/spacing/padding CSS tweaks. If stuck after 3+ deploys without satisfying the motion request, escalate to autonomous Claude Code build (see `references/autonomous-fable-builds.md`). Do not keep deploying incremental CSS changes.
- **Lenis kills IntersectionObserver:** observe individual `[data-reveal]` elements directly, use forgiving thresholds, add a 4-second unconditional fallback timer.
- **Vimeo blocks headless Chrome:** use `domcontentloaded` not `networkidle`. Hide iframe temporarily for content QA.
- **Press logos + CSS filter inversion = white rectangles:** on dark backgrounds, let full-color PNGs render naturally. Do not use `brightness(0) invert(1)` on brand logos.
- **Counters with text prefixes need separate spans:** animate only `.count-number`, keep `.count-prefix` static.
- **AI-generated placeholder copy reads fake:** when Matt asks to replace content on one of his own sites, interview him instead of generating replacement copy. See `references/interview-for-content.md`.
- **Em-dash absolute ban, no exceptions ever:** `&mdash;`, `&ndash;`, `\u2014`, `\u2013` are prohibited in ALL rendered copy on ALL BLDG/Arrival/Montana/client sites. Code comments exempt. The Montana session (2026-07-13) escalated this from a brand law to a hard operational rule after em-dashes survived multiple fix rounds. After every deploy, grep the output for these characters and kill any found before reporting done. Applies to site copy, meta descriptions, OG tags, alt text, footer copyright lines, and press card labels. Use hyphens or middots instead.
- **Content guardrails from the Montana interview (2026-07-13):** never call architects/clients "demanding" as people -- projects can be demanding, people are not. Avoid cliche hero lines like "work others call impossible." Never insert casual lines ("we build with people we like") unless Matt says them directly in an interview. When Matt asks to remove owner-led narrative, remove ALL traces: stat blocks, manifesto paragraphs, footer tags, meta descriptions.
- **Logo unification rule:** when Matt says the logo lettering isn't unified (one line bold and one line light), make both lines the same weight and both all-caps. Don't try a "subtle" weight difference -- make them identical.
- **Marquee removal:** if Matt says to remove a scrolling project-name bar, remove the entire element: HTML, CSS, and JS. The Montana session marquee survived multiple fix rounds because only the content was updated, not the element itself.
- **Removing HTML elements with JS references kills the entire site:** when you delete an HTML element that JavaScript references by ID (e.g., a progress bar `<div id="prog">`), the JS throws `Cannot read properties of null` on the first `element.style` call, bricking ALL JavaScript — reveals, counters, nav, parallax. Every section renders black. After removing any element, grep the full JS for its ID/class and clean up every reference. The Montana session (2026-07-13) lost 3 deploy rounds to this bug after removing the progress bar and spotlight.
- **Be resourceful — scrape before you ask:** when Matt says "get it from my website," exhaust all automated approaches before asking him to send files. WordPress sites with hotlink protection can be scraped by using Playwright's `page.evaluate` with `fetch()` → blob — the browser's own network stack bypasses referrer checks that block curl. See `references/scraping-hotlink-protected-sites.md`.
- **Higgsfield rasters fail for geometric UI elements:** when Matt asks for abstract shapes, section dividers, or geometric line art for websites, do not use Higgsfield — the PNGs have pixelation and white backgrounds. Use inline SVGs instead (vector-perfect, CSS-colorable, zero artifacts).
- **Hover overlay pointer-events flicker:** when building a fixed overlay for project previews, the `.preview-overlay.active` state must NOT set `pointer-events: auto`. Doing so blocks the mouse from reaching the `.pitem` element, which fires `mouseleave`, which deactivates the overlay, which restores pointer-events, which re-fires `mouseenter` — infinite flicker loop. Playwright log confirms with: `\"intercepts pointer events\"`. The overlay stays `pointer-events: none` at all times; dismissal is via a click handler on the overlay itself. See `references/hover-overlay-pattern.md`.
- **Self-verify before delivery, always:** never tell Matt a site is ready based on Playwright data alone. Take full-page screenshots at every section break, verify all content renders, run the banned-term grep, and confirm zero JS errors. The Montana session (2026-07-13) shipped a broken site because Playwright data showed 40/40 reveals visible while the real browser was black. Data-only verification is not verification. Use the video recording → ffmpeg frames → vision analysis pipeline from `references/scroll-video-verification.md` when Matt is available to review, and Playwright screenshots + content extraction when verifying autonomously.
**Manual patching death spiral — fire rebuild at 3 deploys:** after 3+ rounds of manual HTML/CSS patches without satisfying Matt's feedback, do NOT deploy a 4th patch. Stop, fire Claude Code for a clean rebuild with ALL accumulated feedback. The Montana session (2026-07-13) proved: (a) manual patches compound errors — missing closing tags, deleted elements with dangling JS references, broken section nesting; (b) the symptom is Matt saying "this is riddled with issues" while Playwright says it's fine; (c) after removing ANY HTML element, grep the full JS for ID/class references — dangling references brick ALL JavaScript. The trigger to fire rebuild: Matt expresses frustration, OR the same fix is requested across 2+ rounds, OR you say "Playwright says it's fine" — any of these means patch mode has failed.

- **Fable output still needs 10+ manual patches:** Claude Code's autonomous build produces the creative direction and motion, but it will miss specifics — wrong project names, stale content, incorrect press logos, missing sections. After deploying the Fable output, expect a fast iteration round of patching: content replacement (approach, manifesto, core values), project lineup fixes, press logo additions, removing unwanted UI elements (progress bars), and adjusting hero typography. The Fable build is the spark — manual patching is the polish.
- **Manual build vs delegated build — the quality delta is real:** when building an Arrival preview for a subcontractor (or any site requiring full bank tactics), delegate the build to a subagent with the complete bank context (all T-IDs, Arrival presets, Haven/Montana/Tresmares learnings, real client data, design requirements). A manual build from working memory produces functional but forgettable output (~21KB). A delegated build with isolated context space produces remarkable output (~45KB, 1,375 lines). The Smith Cooling session (2026-07-12) established this: v2 manual was "not up to snuff," v3 delegated was "the Apple version of an HVAC website — absolutely a $20,000+ asset." Delegation is not optional for Arrival previews — it is the quality gate.
- **Italic text banned in all client-facing sites:** force `em, i, cite, address { font-style: normal }` in the CSS reset. Never use italic for emphasis. Matt explicitly prefers weight and size for hierarchy. The Smith Cooling session (2026-07-12) confirmed this.
- **Photos must display at natural aspect ratio:** never force `aspect-ratio: 1/1` on client photos. The Smith Cooling session had the family photo cropped to a square, making it look resized and awkward. Let photos breathe with their natural dimensions. Use an offset background panel or generous padding instead of cropping.
- **WordPress header banners are not project photos:** when scraping a WordPress site for project images, the 1500x510 header crops are banner crops for page headers, not suitable for project previews or galleries. They render as thin strips (3:1 ratio) that look broken when expanded. Use real project photography from the media library instead, or ask Matt for actual photos.
- **Editorial escalation trigger:** when Matt says a built site looks like a basic template, do not add more features or sections. Push toward editorial design: massive type (up to 10.5rem), asymmetric layout offsets, single-accent discipline, typography-as-image. See `references/editorial-design-acceleration.md`.

- **Premium sci-fi = subtraction, not addition (2026-07-15):** animated particles, data rain, glowing CSS beams, and pulsing effects read as AI slop in dark cinematic designs. The BLDG Vision V1 build had all of these and was rejected as "obvious AI and amateur." The reference sites that nail premium sci-fi (Drift: drift-co0.pages.dev, VAST: vastspace.com) share a common principle: subtract everything until only the essential remains, then make that essential feel inevitable. One volumetric beam. Monochromatic depth. Real photography. Atmospheric gradients without animation loops. No particles. No glow. This applies to all dark/sci-fi/immersive designs — when in doubt, remove the effect.

### Montana-specific founder preferences (2026-07-13)

Defaults consolidated from the Montana build session:
- **Deploy every round immediately** — Vercel alias, no approval gate on incremental fixes.
- **No revenue numbers ever.** Replace with years, project count, service area, or ownership signals.
- **Press logos unmissable** — start at 200px minimum for portrait-orientation logos (Vogue, NYT). When Matt says "still too small," triple the size, not add 20%. Sizing progression from the session: 44 → 64 → 80 → 120 → 200 → 240 → 360 → 420px.
- **Hero is cinema** — video or hero photo, thin editorial claim at bottom, no body text on hero. Body copy → manifesto bridge band (dark brand color, centered, one paragraph max).
- **Premium GC = blend category** — trade (phone, local, owner voice) + professional-services (monochrome, editorial type, press proof).
- **TT Commons Pro approved for Montana** — Regular 400 + Bold 600 from Dropbox BLDG/FONTS/. Both logo lines same weight, all-caps.
- **Recommend premium fonts freely** — Matt will license them if they earn their place.
- **Two-track parallel builds** — when stuck on motion/polish, launch Claude Code autonomously as wild-card. Build 3 variants with different creative directions. Compare and merge.
- **Scrape first, ask second** — WordPress sites with hotlink protection can be scraped via Playwright `page.evaluate` with `fetch()` → blob.
- **Press section goes above the video** — Recognition/As Seen In sits between the hero and the feature video section. This builds trust before the portfolio scroll.
- **Project detail pages via hash routing** — use a JavaScript PROJECTS array with inline hash-based navigation (#project-slug). Full-screen detail view with hero image, gallery lightbox, and back button. All projects shareable and linkable. Fable handles the design; Kron handles the data extraction from the existing WordPress site.
