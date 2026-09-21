# Evals

Run on BEFORE and AFTER. Report both numbers. Thresholds are the pass bar for AFTER.

## Primary eval: monday.com Night, Agents screen

The anchor for every run is `monday-night.md`, measured off the Agents screen of monday.com in Night theme. It is used in two of the evals below and it is the one that decides "good", not just "not broken".

| Eval | What it is | AFTER threshold |
|------|-----------|-----------------|
| Token diff | The AFTER page's measured colours, type, spacing and structure against the tables in `monday-night.md` | Every `hard` rule passes. `soft` misses are listed in the scorecard. |
| Judge anchor | The Agents screen screenshot fed to the blind judge as the "3" reference | AFTER wins 3/3 against BEFORE, and the judge's axis scores for AFTER are within 1 of the anchor on axes 2, 4, 5 and 6 |

The board view in the same theme is not an anchor and must not be screenshotted as one.

## Automated (run these every time)

| Eval | Tool | What it catches | AFTER threshold |
|------|------|-----------------|-----------------|
| Lighthouse | `npx lighthouse <url> --output json` | Perf, a11y, best practices, SEO | A11y 95+, Perf 85+ (mobile) |
| axe-core | `npx @axe-core/cli <url>` | Contrast, missing labels, ARIA | 0 serious/critical violations |
| Visual diff | Playwright screenshots + `pixelmatch` | Proves the change is real, not cosmetic | 40%+ pixels changed above the fold |
| Contrast ratio | axe contrast rule | Unreadable text | All text WCAG AA |

The visual diff is the key one for "drastic." If less than 40% of the above-the-fold pixels changed, the rebuild was a restyle. Go bolder.

## Vision-model judge (the one that actually measures design)

Automated tools catch errors, not taste. For taste, use a blind pairwise judge:

1. Give a vision model the BEFORE and AFTER screenshots in random order, labeled A and B only.
2. Ask it to score each on the 10 axes in design-bar.md and pick which it would click the CTA on.
3. Run 3 times with order swapped. AFTER must win 3/3.

Blind + order-swapped is what makes this real. An unblinded judge just agrees with whoever built it.

## Human 5-second test (the gold standard, optional)

Show the AFTER hero to someone who has never seen it for 5 seconds. Ask: what is it, who is it for, what would you click? Two out of three people should nail all three. Use UsabilityHub/Lyssna, or just text a screenshot to 3 people in the buyer's world.

## Where to calibrate the judge

Do NOT use general model leaderboards to judge design. Use these as reference for what "good" looks like:
- Design Arena and WebDev Arena (LMArena): human preference on generated UIs, the closest public signal to real taste
- The monday.com Agents screen in Night theme first, then your own 2-3 reference sites from the inputs: feed their screenshots to the judge as the "3" anchor so it scores against your bar, not a generic one
