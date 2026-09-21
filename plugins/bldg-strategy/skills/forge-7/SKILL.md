---
name: forge-7-website-builder
description: FORGE-7 website-building system. Nine levels from brief to adversarial review. The ladder that shipped TOTAL STATION on bldglabs.ai. Trigger on "forge", "forge-7", "level up this page", "redesign", "make this page beautiful", "new landing page".
---

# FORGE-7 Website Builder

The ladder that took bldglabs.ai from a clean-but-conventional dark site to TOTAL
STATION. Levels compound; never skip below your target. For a quick page touch-up,
run L1 + L7 + L9. For a from-scratch or "wow" brief, run all nine. Grade the target
against the ladder FIRST, then climb only the missing rungs.

The one-line diagnosis of bad AI websites: the model was asked like a chatbot
("make it nice") instead of being given references, extraction blueprints, evidence,
and laws. Every level below removes one class of that failure.

## L1 · BRIEF (never grab-and-go)

Pin the subject, the audience, and the page's SINGLE job (the one action a visitor
should take) before any design thought. Name the success metric. At BLDG Labs the
audience is contractors and founders, practical people, not tech people; the job is
almost always one of: book the assessment, run the scorer, submit the idea, call.

## L2 · REFERENCES (show, don't tell)

Collect 3-5 visual references before designing. Sources that consistently pay off:
godly.website, land-book.com, awwwards.com, dribbble.com, mobbin.com. For each
reference, write ONE sentence naming exactly what to take from it (a spacing rhythm,
a hero structure, a motion feel) — never "make it like this" wholesale. If the user
supplies screenshots or URLs, those outrank found references.

## L3 · DESIGN SKILLS (load the piano)

Before writing UI code, load the design skills available in the session:
`frontend-design` (distinctive direction, anti-slop calibration, signature element
discipline) and `ui-motion-design` (house easing set, numbers-not-adjectives,
tokens-before-components). Honor this repo's CLAUDE.md brand rules absolutely: one
green #b6ff00, TT Octosquares + TT Commons locked, no em/en dashes, estimating-AI
rule. Tokens before components; forbid one-off values.

## L4 · ASSETS (give the artist tools)

Plan imagery and video deliberately. Generated assets (image models, video models,
connected via MCP when available) are legitimate for atmosphere and product
renders, but at BLDG Labs they must never fake receipts: no invented jobsite
photos, no fake testimonials, no stock-photo energy. Real product screenshots
outrank generated art. Whatever ships gets optimized: correct rendered dimensions,
WebP/AVIF, lazy below the fold, poster frames on video. An unoptimized 500KB
decoration is a defect, not an asset.

## L5 · COMPONENT SNAPPING (steal the fireplace, repaint it)

Proven interaction patterns can be lifted from component libraries (21st.dev,
Magic UI, CodePen, shadcn/ui) instead of reinvented. HARD RULE: every borrowed
component is re-tokened to the house system (colors, fonts, radii, easings,
durations) before it ships. A component that still looks like its source library
is franken-UI and does not ship. Borrow mechanics, never skins.

## L6 · EVIDENCE (a Ferrari needs an engine)

Beautiful pages that do not convert are failures. Before finalizing structure,
research the niche: find winners and losers among comparable pages (WebSearch /
WebFetch; Firecrawl MCP if connected), extract what the winners share (section
order, CTA copy and placement, proof placement, form length), and write it as a
checklist the build must satisfy. House conversion laws, non-negotiable:
- The primary CTA is visible in the landing viewport and repeated at the end.
- Money copy, prices, and contact info are NEVER dimmed, animated, or gated.
- Two clicks maximum from any scroll depth to the conversion action.
- Every claim is true and specific; a real number beats an adjective.

## L7 · DESIGN EXTRACTION (talk to the architect)

Never build from vibes. Extract a written blueprint FIRST, from either (a) a
reference site the user loves, or (b) the house system itself when extending an
existing property. The blueprint names: palette (exact hexes), type roles and
scale, spacing rhythm, radius/shadow vocabulary, motion vocabulary (named
primitives with curves and durations), copy voice, and the signature element.
For bldglabs.ai the blueprint already exists: the TOTAL STATION system (memory:
total-station-homepage; CSS layer at the bottom of app/globals.css; engine in
components/instrument/Instrument.tsx). Its reusable static vocabulary (.readout,
.plate, .plate-seal, .calibration-note, .keycap, .status-dot, spec-plate layout,
instrument-log copy voice) works on ANY page without arming the engine. Extend
it; do not invent a second language.

## L8 · CONCEPT COMPETITION (house level)

For from-scratch or wow-moment briefs: generate 3-4 complete creative directions
under deliberately different lenses, then judge them with a panel holding
different stakes (a taste judge allergic to cliche, a customer judge who scores
trust and conversion, a staff engineer who scores 60fps buildability). Ship the
winner plus grafts from the losers. Use the Workflow tool for the fan-out when
available. One signature element per page; spend boldness in exactly one place.
Calibration: near-black + single neon accent is itself an AI default; when the
palette is locked, distinctiveness must come from the governing concept and
motion system, not the colors.

## L9 · ADVERSARIAL REVIEW + LAWS (house level)

Nothing ships on first draft. Run a multi-lens review (engine correctness,
CSS/perf, brand/copy including a literal dash scan, a11y including composited
contrast of any dimmed state, conversion UX at 375px and 1440px) and
adversarially verify every finding before fixing (skeptic agents told to refute;
only confirmed findings get fixed). Then verify live in the preview browser at
mobile and desktop, run tsc + lint + production build, and screenshot proof.
Structural laws every BLDG page obeys:
- Static-first: the server DOM is the complete, converting page; motion systems
  are progressive enhancement gated on JS + prefers-reduced-motion.
- True data only: any readout, stat, or badge reports something real.
- Idle law: when the user is not interacting, at most one element moves.
- Degradation is designed, not hoped for: reduced-motion, no-JS, and low-end
  paths are explicit deliverables.

## Running the ladder

1. Grade the target page L1-L9 (one line per level: pass / missing).
2. Climb the missing rungs in order; L6 and L7 can run in parallel (Workflow).
3. Implement, then L9 always runs last, no exceptions.
4. Deliverables: the shipped page, the graded ladder, and proof screenshots.
