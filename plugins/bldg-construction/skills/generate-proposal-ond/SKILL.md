---
name: generate-proposal-od-builders
description: "Generate or revise an O+D Builders construction proposal PDF with the firm's branded letterhead, measured pagination, clear price hierarchy, and fixed print design system. Use for O+D proposal letters, Schedules of Values, alternates, qualifications, clarifications, exclusions, and CSI-style scopes of work."
---

# O+D Builders Proposal Generator

Create a client-ready proposal PDF for O+D Builders. Preserve the black square logo, navy brand color, business terms, and page order while using the fixed typography, spacing, page grid, and table rules in this skill.

The legal entity is **DNP Builders LLC d/b/a O+D Builders**. Use the full legal name in the first formal proposal sentence and the signature block. Use **O+D** or **O+D Builders** in running headers, footers, and later references.

## 1. Gather the missing inputs

Use any supplied proposal, scope, estimate, or client record before asking questions. Ask only for fields that remain missing:

- Client contact, company, address, project name, project address, and proposal date.
- Signer name. Use the source proposal's signer when present. Do not guess a person.
- A priced Schedule of Values or a target total that must be reconciled.
- General Conditions percentage and Insurance percentage. The usual starting values are 5% and 2.5%, but confirm them against the source or with the user.
- Alternates, with a price or unit rate for each one.
- Qualifications, clarifications, and exclusions. Reuse approved client text when supplied and change only the requested items.
- Scope sections. Each section needs a two-digit local number, a short title, and any intro, work items, and notes.

Do not invent scope, quantities, prices, owners, project facts, or legal terms.

## 2. Load the print system and brand assets

Read [references/visual-system.md](references/visual-system.md) before building or revising any proposal. It defines the type roles, pairings, spacing scale, margins, page zones, tables, and review checks.

Start from [assets/proposal-print.css](assets/proposal-print.css). Copy it beside the proposal HTML or embed it in the HTML. Change a token only when a verified O+D reference requires it. Do not add one-off font sizes, colors, margins, padding, shadows, or rounded cards.

Use the real O+D logo. If the skill has no approved logo asset, extract it from a supplied O+D PDF with PyMuPDF:

```python
import fitz

doc = fitz.open("reference.pdf")
page = doc[0]
image = page.get_images(full=True)[0]
asset = doc.extract_image(image[0])
open(f"logo.{asset['ext']}", "wb").write(asset["image"])
```

Embed the logo as a data URI so the HTML and PDF do not depend on a local path. Do not redraw, trace, recolor, stretch, or crop it.

## 3. Reconcile the pricing

Use this default calculation only when it matches the source proposal:

```text
Sub-Total (Direct Cost) = sum of CSI line items
General Conditions      = GC% x Sub-Total
Insurance               = Insurance% x (Sub-Total + General Conditions)
Total Estimate          = Sub-Total + General Conditions + Insurance
```

Check that the source line items, percentages, and total reconcile before rendering. If the source uses another method, reproduce the source method and state the difference to the user.

When the user asks to rescale a Schedule of Values to a target total, calculate `k = target_total / current_total`. Multiply each line item and markup amount by `k`, use `ROUND_HALF_UP`, and reconcile the rounded rows back to the target. Apply any rounding residual to the largest direct-cost row and record that adjustment in the working notes. Keep CSI rows in numeric order.

## 4. Build the page sequence

Use these page types. Follow their detailed layout rules in the visual-system reference.

1. **Proposal letter.** Show the logo, firm address, date, client block, project line, proposal title, formal offer sentence, total, attachments, closing, signer, and acceptance lines. Use the full-width navy website footer on this page only.
2. **Schedule of Values.** Use the running header, project metadata, title, line-item table, direct-cost subtotal, General Conditions, Insurance, Total Estimate, and alternates.
3. **Qualifications, Clarifications & Exclusions.** Use one numbered stream with hanging numbers and bold labels when labels exist.
4. **Scope of Work.** Use two-digit local section numbers, section titles, work items, and optional notes. Scope section numbers and CSI cost codes are separate systems.

Keep each section's job clear. Do not add cover cards, decorative icons, gradients, photos, slogans, or generic sales copy. The proposal should read as an O+D business document, not a web landing page.

## 5. Paginate from measured content

Build one HTML document with `@page { size: letter; margin: 0; }`. Each physical page is one `.page` element. Use the CSS asset for the fixed page size and padding.

For each page type with variable content, run a measure, pack, and assemble pass:

1. **Measure.** Render all repeatable blocks without page splitting in Chromium. Measure each block and the space between `#content-start` and the footer zone.
2. **Pack.** Add blocks in source order until the next block would cross the safe content boundary. Keep a heading with at least its first paragraph or two list rows. Keep a table header with at least two body rows. Do not leave one list item on a final page when balanced packing can avoid it.
3. **Assemble.** Build the final page groups with running headers, project labels, and page numbers.

Do not use guessed units per item. Do not set `overflow: hidden` to conceal overrun. Do not hand-patch the PDF after rendering.

Render with Playwright Chromium:

```js
await page.pdf({
  format: "Letter",
  printBackground: true,
  margin: { top: "0in", right: "0in", bottom: "0in", left: "0in" }
});
```

## 6. Verify every page

Run all checks before delivery:

- Confirm each `.page` is at most 11 inches tall and the PDF page count matches the assembled page count.
- Render every PDF page to an image at 144 dpi or higher and inspect every page.
- Confirm the proposal letter total, Schedule of Values total, percentages, and alternates match the approved worksheet.
- Confirm all money and percentage columns use tabular figures and align on the right edge.
- Confirm body text, labels, notes, headings, and totals use only the defined type roles.
- Confirm text contrast meets the thresholds in the visual-system reference and that no key meaning depends on navy alone.
- Confirm no clipped text, broken rows, stretched logo, double-escaped ampersand, isolated heading, sparse final list page, or footer collision appears.
- Run a squint check on each page. The page title, current section, and primary price or action must remain clear when detail blurs.

If any check fails, revise the HTML, repaginate, render again, and inspect the full PDF again.

## 7. Deliver

Name the file `<Client or Project> Proposal - O+D Builders.pdf`. Deliver the PDF and keep the approved input data, HTML, CSS, and rendered page images together so a later revision can use the same source.
