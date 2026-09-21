# O+D Proposal Visual System

Use this reference for every O+D proposal. It converts the brand into fixed print rules so separate runs produce the same document.

## Design aim

The document should feel precise, restrained, and construction-led. Navy carries identity and hierarchy. White space separates ideas. Type weight, size, and alignment guide the scan. Decoration does not.

Each page must answer three questions in a quick scan:

1. Which project and section is this?
2. What information matters most on this page?
3. Where does the reader look next?

## Color roles

Use one brand accent and a neutral ink scale:

| Role | Value | Use |
|---|---:|---|
| Brand | `#1a1a2e` | Titles, section bars, rules, total row, cover footer |
| Primary ink | `#222222` | Body copy and table text |
| Secondary ink | `#5f5f63` | Notes, address, metadata |
| Tertiary ink | `#76767b` | Eyebrows and page labels at 8 pt or larger |
| Hairline | `#dedee3` | Rules and row dividers |
| Soft surface | `#f4f4f7` | Subtotals, metadata rails, alternate note |
| Paper | `#ffffff` | Page background |

Use navy for identity, totals, and section orientation. Do not use it to decorate empty space. Keep normal body copy in primary ink. Use white type on navy only at 8 pt or larger with semibold weight.

For screen previews, normal text must meet a 4.5:1 contrast ratio. Large text and heavy display totals must meet 3:1. Print a grayscale test when the proposal depends on a shaded row. Labels, borders, or weight must still carry the distinction.

## Type system

Use `Arial, Helvetica, sans-serif` to match O+D source material. Do not add another family unless an approved O+D proposal proves that it belongs in the brand.

| Role | Size | Weight | Line height | Tracking | Use |
|---|---:|---:|---:|---:|---|
| Cover title | 26 pt | 700 | 1.02 | -0.02em | `Proposal` on the letter |
| Money hero | 24 pt | 700 | 1.00 | -0.015em | Cover total only |
| Page title | 15 pt | 700 | 1.12 | -0.01em | Main title on interior pages |
| Section title | 10.5 pt | 700 | 1.20 | 0 | Scope and alternate section names |
| Body | 9.25 pt | 400 | 1.45 | 0 | Paragraphs and list text |
| Table | 8.5 pt | 400 | 1.30 | 0 | Schedule rows |
| Small | 8.25 pt | 400 | 1.35 | 0 | Address and secondary metadata |
| Label | 7.5 pt | 700 | 1.20 | 0.10em | Uppercase eyebrows and column labels |
| Footer | 7.25 pt | 400 | 1.20 | 0.04em | Page number and project footer |

Apply `font-variant-numeric: tabular-nums` to every price, percentage, date, page number, and CSI code. Right-align money and percentages. Keep codes left-aligned. Do not letter-space lowercase body text.

### Pairing rules

- Pair the 26 pt cover title with 9.25 pt body. The large scale change gives the cover one focal point.
- Pair the 15 pt page title with 7.5 pt uppercase metadata. The label orients the reader while the title names the page.
- Pair 10.5 pt section titles with 9.25 pt body. Use weight and spacing for local hierarchy.
- Pair 8.5 pt table rows with 7.5 pt semibold column labels. Do not shrink a dense table below 8.5 pt. Split it instead.
- Do not set two adjacent roles within 1 pt of each other unless weight or case makes their function clear.
- Do not use more than three weights on one page. Use 400, 600, and 700.

Keep body lines between 45 and 78 characters when the layout permits. Use `text-wrap: balance` for short titles and `text-wrap: pretty` for body text where Chromium supports them.

## Spacing scale

Use a 4 pt base scale: `4, 8, 12, 16, 24, 32, 48 pt`.

- 4 pt separates a label from its value.
- 8 pt separates parts of the same item.
- 12 pt separates adjacent items in one section.
- 16 pt separates a heading from its first content block.
- 24 pt separates distinct sections.
- 32 or 48 pt creates the cover's main pauses.

Do not add off-scale spacing to make a single page fit. Repaginate or tighten the whole role consistently.

## Page grid

Use US Letter at 8.5 by 11 inches. Use `box-sizing: border-box` on every element.

| Zone | Measure |
|---|---:|
| Left and right page padding | 0.62 in |
| Top page padding | 0.52 in |
| Bottom page padding | 0.58 in |
| Interior running header | 0.68 in |
| Gap after running header | 0.24 in |
| Interior footer zone | 0.30 in |
| Cover website footer | 0.38 in |
| Safe content buffer above footer | 0.18 in |

Use an eight-column content grid with seven 0.14 inch gutters when a page needs columns. Most body content should span all eight columns. Use five columns for the main title or table and three columns for project metadata.

Align the logo, page title, table left edge, section bars, and footer text to the same page grid. A one-pixel drift is visible in a printed set.

## Page hierarchy

### Proposal letter

- Set the logo at the upper left within a 0.72 inch high brand zone. Keep its native aspect ratio.
- Place the firm address at upper right in the Small role. Use flush-right alignment and no more than four lines.
- Put the date and recipient block below the brand zone with 24 pt between groups.
- Set `Re:` as a 7.5 pt uppercase label with the project name in 10.5 pt semibold on the next line.
- Keep `Proposal` left-aligned. Do not center the cover title.
- Put the offer sentence above the price. Put a small uppercase `TOTAL ESTIMATE` label 4 pt above the Money hero.
- Set the total as navy text on white. Do not place it in a rounded card, gradient, or shadowed box.
- Use a 24 pt pause before attachments and the closing. Keep the signature and acceptance areas on the same baseline grid.
- Reserve the bottom 0.76 inch for the full-width navy website footer and its safe gap.

### Running header and footer

- Use the logo or O+D wordmark at the upper left. Use the project name and current section at the upper right.
- Keep the header visually quiet. Use a 0.75 pt navy rule below it.
- Put the project name at lower left and `Page N of N` at lower right in the Footer role.
- Use a light gray top rule on the interior footer. The cover uses the navy website band and no page number.

### Schedule of Values

- Use a two-part title row. The page title spans five grid columns. Status, contact, and date use three columns and the Small role.
- Use `Description / Total / % of Total` widths of `60% / 24% / 16%`.
- Use a 0.32 inch header row with navy fill, white Label text, and 8 pt horizontal padding.
- Use a minimum 0.28 inch body row. Use 7 pt vertical and 8 pt horizontal padding.
- Use horizontal hairlines only. Do not box every cell.
- Keep descriptions left-aligned. Right-align all prices and percentages. Align digits on the right edge.
- Use Soft surface for the direct-cost subtotal. Use white rows for General Conditions and Insurance.
- Use navy fill and white 10.5 pt bold type for Total Estimate. Give this row at least 0.36 inch height.
- Place Alternates 24 pt below the total. Use one navy section bar, then a soft note panel if the client supplied an explanatory note.
- Keep a table header with at least two body rows. Repeat the header on later pages.

### Qualifications, clarifications, and exclusions

- Use a 0.34 inch number rail and a hanging text column.
- Set the number in 8.25 pt bold navy. Set the item text in the Body role.
- Set a supplied label in bold, followed by a colon and the explanation in regular weight.
- Use 8 pt between related items and 12 pt after long items.
- Keep at least two items on a continuation page when content permits.

### Scope of Work

- Use a navy section bar no taller than 0.32 inch. Set the two-digit local number in a fixed 0.44 inch rail and the title in the remaining width.
- Use the section title role in white. Keep the label to one line when possible.
- Start the section content 12 pt below the bar.
- Use an 0.18 inch hanging indent for work items. Use a short navy rule or a plain bullet, not a long dash as decoration.
- Use hairline dividers only when a section has three or more work rows.
- Set qualifying notes in Secondary ink and italic. Give the note a soft surface only when it could be mistaken for scope.
- Keep a section bar with its intro and at least two work rows. If that group does not fit, move it to the next page.

## Advanced document checks

Apply these checks to the rendered pages, not only the source CSS:

- **First-impression check:** The cover should communicate the firm, project, document type, and proposed total within three seconds.
- **Eye-path check:** The cover scan should move from logo to project to title to price to offer details.
- **Squint check:** Blur or zoom out to 25%. Titles, section starts, and totals should remain clear.
- **Page-area check:** Each visual area should have one clear purpose. Remove any area that cannot be named in two seconds.
- **Density check:** Pages should feel full but calm. Do not solve sparse pages with larger logos, thick bars, or more decoration.
- **Consistency check:** The same role must keep the same size, weight, color, and spacing on every page.
- **Table check:** A reader should trace one row from description to amount without losing place.
- **Print check:** Fine rules, small type, and gray text must survive a grayscale office printer.
- **AI-pattern check:** Reject decorative cards, gradients, icons in circles, centered-everything layouts, large rounded corners, colored side borders, stock art, and generic sales language.

## Allowed adjustments

Change the fixed system only when content cannot fit after measured pagination or when an approved O+D reference proves a different brand rule. Make the smallest system-wide change. Record it in the source HTML or working notes. Never change a single item in isolation to force a page break.
