# Pricing Logic

How to derive defensible numbers for a NYC sketch-stage budgetary estimate.

## The pricing structure

Every line item is bottom-up. There are no top-down $/SF guesses — those are only used as sanity checks at the end.

```
Trade subtotal (sum of all CSI line items)
+ Design Contingency (sketch)    12%   <- ALWAYS directly below subtotal, above other markups
+ General Conditions overhead    7%
+ Fee (GC profit)                5%
+ Insurance (GL + builder's risk) 3%
= TOTAL ESTIMATE
```

**Presentation convention:** contingency is always shown FIRST, directly below the Sub-Total (Direct Cost) line and above GC / Fee / Insurance. The math is unaffected (markups are parallel), but the row order is fixed — keep it this way in the cost-totals tabs and any add-alternate tab.

Markups are parallel (each applied as a % of trade subtotal), not sequential. So a $2.0M trade subtotal × 1.27 = $2.54M total. The 27% all-in markup is the standard for NYC open-shop work at sketch stage.

## Why these specific markups

- **GC 7%** — covers site supervision, project management, dumpsters, hoisting, daily clean, temp toilets. Most of this is also captured in Division 01 line items, but the 7% covers home-office allocation.
- **Fee 5%** — GC's profit. For private fast-track work in NYC this is the going rate. For union jobs or institutional clients it's 6–8%.
- **Insurance 3%** — GL + builder's risk allocation. Bond premium is excluded (private work, no bond required).
- **Contingency 12%** — sketch-level. At DD it drops to 8%, at CD to 5%, at GMP to 3%.

## How to scale from a benchmark

When pricing a new project, start with a known comparable. The MacDougal Street Restaurant estimate is the working template (2,138 SF FOH, 6-month build, mid-tier ~$1.9M / high-end ~$2.5M). Scale by SF ratio and adjust for scope differences.

**SF-scalable items** (multiply by new_SF / template_SF):
- Demolition
- Concrete floor patching
- Drywall, ceilings, flooring, painting
- Sprinkler heads/drops
- HVAC distribution
- Electric branch wiring
- Fire alarm device count
- Audio/visual rough-in
- Bathroom finishes within bath allowance

**SF-independent items** (keep flat or scale loosely):
- General Requirements (scales with months, not SF) — figure $30–35K/month for full-time GC supervision + tools + dumpsters
- Bar millwork (driven by LF, typically 22 LF custom bar regardless of restaurant size)
- Bathroom allowance (fixed per bath; default $85K, range $75–115K)
- Kitchen scope (fixed when "stays minimal")
- Cellar refresh (lump sum)
- Eliason door, water heater, grease interceptor (count-based)

## The Paolo benchmark (168 Bleeker St)

| Line | $ | $/SF (2,000 SF) | % |
|---|---|---|---|
| Div 01 General Reqs | $192,220 | $96 | 13.7% |
| Div 02 Demolition | $16,000 | $8 | 1.1% |
| Div 06 Millwork | $125,902 | $63 | 9.0% |
| Div 08 Doors / Glass | $23,526 | $12 | 1.7% |
| Div 09 Finishes (DW/Acoustic/Tile/Floor/Paint) | $198,686 | $99 | 14.2% |
| Div 10 Specialties | $21,658 | $11 | 1.5% |
| Div 11 Kitchen Equipment | $116,981 | $58 | 8.4% |
| Div 21 Sprinkler | $30,696 | $15 | 2.2% |
| Div 22 Plumbing + Fixtures | $101,400 | $51 | 7.3% |
| Div 23 HVAC | $172,500 | $86 | 12.3% |
| Div 26 Electric + Lighting | $164,112 | $82 | 11.7% |
| Div 27 Comms | $11,500 | $6 | 0.8% |
| Div 28 Fire Alarm + Security | $34,016 | $17 | 2.4% |
| **Direct Cost** | **$1,209,196** | **$605** | **86.4%** |
| GC | $84,644 | $42 | 6.1% |
| Fee | $64,692 | $32 | 4.6% |
| Insurance | $40,756 | $20 | 2.9% |
| **TOTAL** | **$1,399,287** | **$700** | **100%** |

This is a NEW 2,000 SF mid-tier West Village restaurant with full new kitchen equipment, FF&E (tables/chairs), full new HVAC (heat pumps), 6-month build, completed 2026.

**To compare a renovation against Paolo**, strip:
- Kitchen equipment (~$58/SF if equipment stays)
- FF&E (~$10–20/SF if loose furniture excluded)
- Some HVAC (~$30/SF if reusing existing equipment)

That gives a "renovation-only equivalent" of ~$600/SF for mid-tier comparable work.

## Tier A vs Tier B — what changes

Going from mid-tier to high-end roughly doubles certain trade lines while leaving others flat:

| Line | Mid-tier multiplier | High-end multiplier |
|---|---|---|
| Millwork | 1.0× | 1.3× (premium hardwoods, stone, brass) |
| Tile & Stone | 1.0× | 1.8× (imported tile, natural stone) |
| Flooring | 1.0× | 1.5× (wide-plank specialty / stone) |
| Painting | 1.0× | 1.85× (Venetian plaster, specialty finishes) |
| Acoustic ceilings | 1.0× | 1.7× (custom acoustic + wood plank) |
| Lighting fixtures (allowance) | $40–55K | $80–110K (designer + statement) |
| Bath allowance | $85K/bath | $115K/bath (premium fixtures) |
| Doors/hardware | 1.0× | 1.5× (solid hardwood, premium hw) |
| Misc metals | 1.0× | 1.5× (blackened steel, brass) |
| HVAC | 1.0× | 1.15× (linear slot diffusers) |
| Electric | 1.0× | 1.20× (more circuits for lighting/AV) |
| General Reqs | 1.0× | 1.05× (slightly longer build) |
| Demolition | 1.0× | 1.10× (more careful, more salvage) |
| Everything else | 1.0× | 1.0× |

These are starting ratios. Adjust if the user has specific premium scope (e.g., a chef's-table fireplace built-in adds Tier B but not Tier A).

## Sanity-check thresholds

Before delivering, a NYC restaurant gut should land in one of these ranges per SF of FOH:

| Tier | $/SF FOH (renovation, kitchen stays) |
|---|---|
| Casual / fast-casual | $400–550 |
| Mid-tier upscale | $600–900 |
| High-end signature | $900–1,400 |

If your number is outside these, recheck. Most likely causes:
- SF is wrong (don't scale from drawings — ask)
- Bathroom allowance double-counted or missing
- General Requirements not scaled for actual schedule duration
- Tier B premiums applied to Tier A by mistake

The $/SF metric is high for small projects because fixed costs (super, dumpsters, bath allowance) don't shrink with the room. A 1,500 SF FOH at $1,200/SF is normal; a 5,000 SF FOH at $1,200/SF is not.

## Why two tiers, not one

The architect asked "what would this cost?" The honest answer is "depends on finish level." Presenting one number invites pushback ("why so expensive?"). Presenting two tiers educates the architect and gives them a tool — they can take Tier B to the owner if the budget supports it, or scope down to Tier A if it doesn't. It also frames the negotiation around finish quality rather than dollars.

## Why HVAC as add-alternate, not base

HVAC is the most uncertain line at sketch stage. The existing equipment might be 5 years old (reuse fine) or 25 years old (replace, with rigging headaches). Showing it both ways — reuse as base, full replace as add-alt — lets the architect/owner decide after a mechanical site survey without re-pricing the whole estimate. The +$285–365K spread is shown explicitly so the owner sees the real cost of the decision.
