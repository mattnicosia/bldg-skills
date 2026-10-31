---
name: say-it-once
description: Find and fix product screens that say the same thing too many times. Scan mode ranks the screens of a running app or codebase where a fact repeats, a sentence restates a chip, a button only switches a view, or a rare action takes a prime spot. Fix mode takes one screen through a ledger, a ladder of mockup options and a build checklist. Trigger on say it once, declutter, too much text, simplify this screen, header too tall, too many rows, find simplification opportunities, or a request to make an app screen faster to read.
license: MIT
metadata:
  type: workflow
  version: "1.0"
---

# Say It Once

A working screen should state each fact once, in the spot where the user acts on it. Most clutter in a mature app is one fact said two or three times, plus sentences that explain what a chip or button already says.

The model case is VERIDEX LA-3529. A bid package header took five rows to say that the package was out to bid, its date had passed, and it still took bids. It now says that in two rows with no sentences. The worked example is in `references/patterns.md`.

This skill works on app screens: dashboards, records, lists, headers and forms people use every day. For a weak landing page, use `level-up-design` instead.

## Pick a mode

- **Scan**: the user wants opportunities across an app. Go to Scan.
- **Fix**: the user names one screen, or approves a finding from Scan. Go to Fix.

## Scan

1. **List the daily screens.** Read the router or nav and list each screen with how often people open it. Ask the user, or infer it from the nav order and the product's job. Rank the most-used screens first, because a row saved on a daily screen beats ten rows saved on a settings page.
2. **Capture each screen.** Run the app and capture each screen at desktop width and 390 by 844, with realistic data. Pull the visible text with the browser's page-text tool and pipe it through `scripts/repeat_scan.py`. It reports sentences, sentences and lines that repeat, phrases that repeat inside lines, and years, long time zone names and times. Measure the pixel offset of the first piece of work at both widths. With no running app, read the component source, but treat what it finds as leads to confirm on the rendered screen.
3. **Tag every element** against the patterns in `references/patterns.md`. A finding names the pattern, the exact text or control, where else that fact already shows, and the rows or words it costs.
4. **Rank** by screen use times rows saved. Put risky fixes last: a finding that touches a warning, a legal note or a required fact needs a destination, not a deletion.

Done when every daily screen has a line in `SAY-IT-ONCE.md`: its use rank, rows above the first actionable item, words in its chrome, and each finding with its pattern. The top three findings each carry a one-sentence fix. Offer to run Fix on the first one.

## Fix

1. **Ledger.** List every element in the area, top to bottom, with what it is: a fact, an action, navigation or an explanation. Next to each fact, name every other place on the screen that states it. Count rows and words before the user reaches the work.
2. **Write the one sentence.** Say in one sentence what the area has to tell the user, such as "this package is out to bid, its date passed 14 days ago, and it still takes bids." Each element either carries part of that sentence, is an action the user takes here often, or has to go somewhere else.
3. **Give every removed element a destination** from the table in `references/patterns.md`: already said elsewhere, moved beside the action it qualifies, into an overflow menu, onto a hover with an accessible label, or onto the screen where it matters. A required fact keeps a visible home. Check the project's rules for facts that must show, such as a deadline's time zone.
4. **Mock a ladder.** Build one HTML page with three or four options, from the smallest change (A) to the boldest (D). Open with the current state and one sentence naming the repetition. Under each option, list exactly what it removes and where each piece goes. Recommend one. Use the real component styles if you can, and sample data marked as sample.
5. **List the states before building.** The mockup shows one sample record. Write down every state the real data can be in (draft, open, overdue, closed, cancelled, sealed, empty, loading, failed, long names, phone width) and say what the chosen option shows in each. Any difference from the mockup goes on the departure list.
6. **Build to the guardrails** in `references/guardrails.md`.

Done when the chosen option is built, every item on the guardrail list has a test or a browser check, the before and after counts are in the PR, and the PR lists every departure from the mockup for the owner to rule on.

## Measure

Report these before and after for each fixed area, so the change is a number and not a taste call:

- Rows above the first actionable item
- Words in the area, not counting the user's own data
- Facts stated more than once
- Full sentences
- Buttons that only switch a view or scroll

LA-3529 went from 5 rows to 2, from 2 sentences to none, and from 2 view-switch buttons to none. Its status and released date each went from two mentions to one.
