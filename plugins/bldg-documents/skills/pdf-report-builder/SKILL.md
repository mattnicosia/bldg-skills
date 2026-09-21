---
name: pdf-report-builder
description: Build a polished, on-brand HTML report and export it to a pixel-accurate PDF via headless Chrome, with every page verified for split content before delivery. Use this whenever the user asks for a PDF report, printable report, assessment report, credential/scorecard PDF, invoice, proposal, or any "export this to PDF" / "give me a PDF" request -- especially when the output needs to match a specific product's or company's real fonts and colors (not generic placeholder styling), or the user has been burned before by content getting cut off or split awkwardly across page breaks. Also use when asked to "make it a PDF" after building an HTML report earlier in the conversation.
---

# Building a report that survives being printed

A report that looks perfect on screen and then chops a sentence in half the moment it becomes a PDF is a real, recurring failure mode -- not an edge case. HTML has no concept of a page; a PDF forces one. Anything you don't explicitly protect from splitting WILL split eventually, and it usually looks fine in a quick skim (a card that's 90% visible, a sentence that trails off) which is exactly why it slips through casual review. This skill exists because that happened on a real report, got "fixed" once (cards only), and still had a sentence sliced in half across a page boundary the next time -- because plain paragraph text wasn't covered. Don't repeat that: cover *everything* that reads as one unit, prose included, from the first draft.

## Step 1: Get the real brand, don't invent one

If this report represents a specific company or product, go find its actual design system before writing a single line of CSS:
- Look for an existing design-system doc, `DESIGN.md`, theme constants file, or a component that already renders something similar (a credential card, an existing report page, an admin dashboard).
- Read the ACTUAL rendered component source (not just a constants file that might be stale/unused -- grep for who actually imports it) to get real hex colors, real font-family strings, and real layout patterns.
- Check for self-hosted font files (`public/fonts/*.woff2` or similar). If one is small (well under 500KB), embed it as a base64 `@font-face` data URI so the PDF is self-contained and pixel-accurate without depending on the font being installed wherever it's opened. For fonts loaded via Google Fonts `@import` in the live product, just reuse that same `@import` -- match what's actually live, don't substitute a similar-looking system font.
- If nothing brand-specific exists, ask the user for their palette/fonts rather than guessing -- a generic template that "looks fine" is a worse outcome than a plain report, because it reads as an attempt at branding that missed.

## Step 2: Write the HTML so page breaks have something to grab onto

The single most important rule, and the one that's easy to skip: **every paragraph and list item must be a real `<p>` or `<li>` element, never plain text joined with `<br><br>`.** A `break-inside: avoid` rule has no effect on a blob of text with manual line breaks -- the browser is free to split anywhere inside it, including mid-word. Structure first, CSS second.

Bake this CSS in from the start (adapt the selector list to your actual class names, but keep the categories):

```css
/* Real margins, not a bare `margin: 0`. Every physical page needs breathing
   room, especially at the top -- edge-to-edge content reads as cramped even
   though it's technically "full bleed." If the page background is a color
   (not white), set it via `@page { background }` directly -- see the note
   below the CSS block before you reach for anything fancier. */
@page { margin: 36px 0 0 0; background: #1B1B1B; } /* swap the color for your theme's page bg */

/* Nothing that reads as one unit should ever split across a page boundary. */
.card, .callout, .table-row-unit, table tr,
p, li, blockquote, .keep-together {
  break-inside: avoid;
  page-break-inside: avoid; /* older engines */
}

/* A heading should never be the last line on a page, orphaned from its content. */
h1, h2, h3 {
  break-after: avoid;
  page-break-after: avoid;
}

/* A long table MAY span pages; its individual rows may not. */
table { break-inside: auto; }
table tr { break-inside: avoid; }
```

**On margins and page background:** a non-zero `@page` margin needs its own background set via `@page { background: ... }` -- do this directly, don't reach for a `position: fixed` full-viewport div as a "repeat this element on every printed page" trick. That trick is real and used elsewhere for print headers/footers, but for a *background* specifically it gets clipped to the content area in Chrome's headless print engine and leaves the margin blank/white instead -- easy to try, looks like it should work, and doesn't. `@page { background }` alone is the reliable fix; confirmed by testing both side by side on a real report.

**The top-of-page gap must be IDENTICAL on every page, and getting this wrong is subtle.** `@page margin` sets a baseline, but whatever element the browser's natural reflow happens to place first on a given page ADDS its own leading space on top of that margin -- and different element types carry different amounts: a heading might have a divider border + padding-top, a callout might have its own top margin, a plain paragraph usually has neither. The result is that every page looks like it has a "different margin," when really the `@page` margin was fine all along and the inconsistency is coming from ordinary element spacing colliding with wherever the page happens to break. This is NOT something a background-color check or a text-boundary check will catch -- both can report "clean" while the gap size still varies wildly page to page. The fix: in `@media print`, zero the `margin-top`/`padding-top`/`border-top` on every element class that could plausibly land at the top of a page (section wrappers, headings, callouts, quote blocks -- audit anything with its own top spacing), so `@page` margin is the ONLY source of top-of-page spacing anywhere in the document. Screen viewing is unaffected since this only fires under print media.

Run `render_and_verify.py` with `--bg <R,G,B>` matching your report's actual background color -- it now measures the top gap on every page and flags anything that varies by more than a few points (a few tenths of a point is just font-glyph-metric noise from different starting characters and is fine; anything bigger is the bug above). This check is not optional -- it's what actually catches the "every page has a different margin" failure mode, which is easy to miss by eye across 7 separate page images and very obvious to a user flipping through the actual PDF.

A quote followed by its own explanatory paragraph (or any two elements that only make sense read together) should be wrapped in one shared container with `break-inside: avoid` -- protecting each element separately still lets the break land *between* them.

## Step 3: Render with headless Chrome, not LibreOffice

LibreOffice's HTML rendering doesn't reliably support flexbox/grid, CSS custom properties, `backdrop-filter`, or embedded web fonts -- all things a real branded report is likely to use. Headless Chrome uses the actual rendering engine most users' browsers use, so what you see is what they'll get:

```bash
python3 scripts/render_and_verify.py <input.html> <output.pdf> --bg 27,27,27
```

`--bg` should match your report's real background color (`255,255,255` if you don't pass it, i.e. white) -- it's used both for the page-boundary text check context and, critically, for the top-of-page gap measurement (Step 4). This bundled script finds a local Chrome/Chromium binary, runs the headless print-to-pdf command, then verifies the result. Run it directly rather than re-deriving the Chrome flags by hand each time. If no Chrome/Chromium is available, tell the user rather than silently falling back to a lower-fidelity renderer.

## Step 4: Verify every page -- don't eyeball one and assume the rest are fine

This is the step that's easy to shortcut and is genuinely worth the extra minute, because it catches two DIFFERENT failure modes that neither looks like the other:

1. **Split content.** `render_and_verify.py` extracts the text of every page to check each boundary between consecutive pages. A split card is obvious in a screenshot; a split *sentence* usually isn't -- "...standing" cutting to "in for the live..." on the next page reads like a normal new sentence unless you actually read the words across the boundary. The script's heuristic flags anything suspicious, but read the flagged boundaries yourself rather than trusting a pass/fail -- and spot-check a couple of the "ok" boundaries too.
2. **Inconsistent top-of-page spacing.** The script also measures the top gap on every page in points and flags any spread beyond glyph-metric noise. A page that "looks fine" on its own can still be part of a set where every page has a visibly different gap -- something a single-page glance will never catch, but a user flipping through the real PDF notices immediately.

Also render every page to a PNG and actually open a few (first/last and anything with a table or long text block) -- the script does this automatically. Only hand the PDF over after both checks report clean (or after you've manually confirmed every flagged item is actually fine).

## Step 5: Clean up

Delete intermediate HTML versions, verification PNGs, and test renders from the scratch/output directory once the final PDF is confirmed good -- don't leave a pile of `report-v2.html`, `report-v3.html`, `verify-page-4.png` clutter behind.
