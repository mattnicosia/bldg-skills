/**
 * Violante & Sons proposal builder.
 * Usage: node build_proposal.js config.json
 *
 * config.json shape — see ../reference/config.example.json
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, VerticalAlign,
  ImageRun, Footer, TabStopType, TableLayoutType,
} = require("docx");

const configPath = process.argv[2];
if (!configPath) {
  console.error("Usage: node build_proposal.js <config.json>");
  process.exit(1);
}
const cfg = JSON.parse(fs.readFileSync(configPath, "utf8"));
const ASSETS = path.join(__dirname, "..", "assets");

const DXA_PAGE_W = 12240, DXA_PAGE_H = 15840, MARGIN = 1080;
const CONTENT_W = DXA_PAGE_W - MARGIN * 2; // 10080

// ---- Brand constants, sampled directly from real Violante & Sons proposals. Do not guess new values. ----
const NAVY_BAR = "24309E";
const TEXT = "333333";
const HEAD_DARK = "1A1A1A";
const LIGHT_SHADE = "F7F7F7";
const TOTAL_SHADE = "E9F3FF";
const RULE = "D9D9D9";
const FONT = "Arial";

const logoData = fs.readFileSync(path.join(ASSETS, "violante_logo.png"));
const rightAddr = ["Violante & Sons", "8 Kimberly Court", "Lake Grove, NY, 11755", "(516) 404-2772"];

function noBorder() {
  const b = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  return { top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b };
}

function headerTable(rightLines) {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [2200, CONTENT_W - 2200],
    borders: noBorder(),
    layout: TableLayoutType.FIXED,
    rows: [new TableRow({ children: [
      new TableCell({
        width: { size: 2200, type: WidthType.DXA }, borders: noBorder(), verticalAlign: VerticalAlign.TOP,
        children: [new Paragraph({ children: [new ImageRun({ data: logoData, type: "png", transformation: { width: 120, height: 128 } })] })],
      }),
      new TableCell({
        width: { size: CONTENT_W - 2200, type: WidthType.DXA }, borders: noBorder(), verticalAlign: VerticalAlign.TOP,
        children: rightLines.map((t) => new Paragraph({
          alignment: AlignmentType.RIGHT, spacing: { after: 0 },
          children: [new TextRun({ text: t, size: 18, font: FONT, color: TEXT })],
        })),
      }),
    ] })],
  });
}

function rule() {
  return new Paragraph({ spacing: { before: 120, after: 220 }, border: { bottom: { color: RULE, space: 4, style: BorderStyle.SINGLE, size: 6 } }, children: [] });
}
// Vertical rhythm: content-heavy pages (Scope of Work + Clarifications + Acceptance
// stacked on one page) were reading top-crammed with dead white space at the bottom
// because every spacing value below was tight (~140-160 twips / 7-8pt) regardless of
// how much content shared the page. These are deliberately looser so multi-section
// pages distribute evenly instead of bunching at the top. Don't shrink these back
// down without checking a rendered page first.
function p(text, opts = {}) {
  return new Paragraph({ spacing: { after: opts.after ?? 170 }, children: [new TextRun({ text, size: opts.size ?? 19, font: FONT, color: opts.color ?? TEXT, bold: !!opts.bold })] });
}
function h2(text, opts = {}) {
  return new Paragraph({ spacing: { before: opts.before ?? 260, after: 180 }, children: [new TextRun({ text, bold: true, size: 24, font: FONT, color: HEAD_DARK })] });
}
function bullet(text) {
  return new Paragraph({ spacing: { after: 90 }, indent: { left: 500 }, children: [new TextRun({ text: "•  " + text, size: 19, font: FONT, color: TEXT })] });
}
function numbered(n, text) {
  return new Paragraph({ spacing: { after: 170 }, indent: { left: 500, hanging: 260 }, children: [
    new TextRun({ text: `${n}. `, size: 19, font: FONT, color: TEXT }), new TextRun({ text, size: 19, font: FONT, color: TEXT }),
  ] });
}
function bottomBar() {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], borders: noBorder(), layout: TableLayoutType.FIXED,
    rows: [new TableRow({ children: [new TableCell({
      width: { size: CONTENT_W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: NAVY_BAR }, borders: noBorder(),
      margins: { top: 260, bottom: 260 }, children: [new Paragraph({ children: [new TextRun({ text: "", size: 2 })] })],
    })] })],
  });
}

// ---------- SOV / estimate-totals table (optional page) ----------
const colW = [4800, 2000, 1600, 1680];
function cell(text, { bold = false, color = TEXT, shade = null, width, align = AlignmentType.LEFT, size = 18 } = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, shading: shade ? { type: ShadingType.CLEAR, fill: shade } : undefined,
    verticalAlign: VerticalAlign.CENTER, margins: { top: 90, bottom: 90, left: 110, right: 110 },
    borders: { top: { style: BorderStyle.SINGLE, size: 4, color: RULE }, bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE }, left: { style: BorderStyle.SINGLE, size: 4, color: RULE }, right: { style: BorderStyle.SINGLE, size: 4, color: RULE } },
    children: [new Paragraph({ alignment: align, children: [new TextRun({ text, bold, color, size, font: FONT })] })],
  });
}
function buildSovTable(rows, totalLabel, totalPrice) {
  const trows = [new TableRow({ children: [
    cell("Description", { bold: true, width: colW[0] }), cell("Total Estimate", { bold: true, width: colW[1], align: AlignmentType.RIGHT }),
    cell("Job %", { bold: true, width: colW[2], align: AlignmentType.RIGHT }), cell("Cost/Unit", { bold: true, width: colW[3] }),
  ] })];
  for (const r of rows) {
    if (r.group) {
      trows.push(new TableRow({ children: [cell(r.group, { bold: true, width: colW[0], shade: LIGHT_SHADE }), cell("", { width: colW[1], shade: LIGHT_SHADE }), cell("", { width: colW[2], shade: LIGHT_SHADE }), cell("", { width: colW[3], shade: LIGHT_SHADE })] }));
    } else {
      trows.push(new TableRow({ children: [cell(r.desc, { width: colW[0] }), cell(r.total, { width: colW[1], align: AlignmentType.RIGHT }), cell(r.pct, { width: colW[2], align: AlignmentType.RIGHT }), cell("", { width: colW[3] })] }));
    }
  }
  trows.push(new TableRow({ children: [
    cell(totalLabel, { bold: true, width: colW[0], shade: TOTAL_SHADE }), cell(totalPrice, { bold: true, width: colW[1], align: AlignmentType.RIGHT, shade: TOTAL_SHADE }),
    cell("100%", { bold: true, width: colW[2], align: AlignmentType.RIGHT, shade: TOTAL_SHADE }), cell("", { width: colW[3], shade: TOTAL_SHADE }),
  ] }));
  return new Table({ width: { size: colW.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: colW, layout: TableLayoutType.FIXED, rows: trows });
}

// ============ Assemble pages ============
const page1 = [
  headerTable(rightAddr),
  rule(),
  new Paragraph({ spacing: { after: 260 }, tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }], children: [
    new TextRun({ text: cfg.date, size: 19, font: FONT, color: TEXT }),
    new TextRun({ text: `\tEstimate: ${cfg.estimateNumber || "[ESTIMATE #]"}`, size: 19, font: FONT, color: TEXT }),
  ] }),
  ...[cfg.client.name + (cfg.client.title ? `, ${cfg.client.title}` : ""), cfg.client.company, ...cfg.client.address].map((line, i, arr) =>
    p(line, { after: i === arr.length - 1 ? 260 : 0 })),
  p(`Re: ${cfg.projectRef}`, { bold: true, after: 260 }),
  ...cfg.introParagraphs.map((t) => p(t)),
  p("The services provided under this proposal include, but are not limited to:"),
  ...cfg.serviceBullets.map(bullet),
  p("All materials and workmanship shall be provided in accordance with applicable codes, industry standards, and good construction practices. Any and all deviations or substitutions will be communicated and approved through the proper channels before proceeding.", { after: 500 }),
  h2("Proposal Amount"),
  p("The total sum for the complete performance of the scope of work described herein is:"),
  p(cfg.totalPrice, { bold: true, size: 30, color: HEAD_DARK, after: 500 }),
];

// Cover page (page 1) is always included — that's the standing default.
const pages = [page1];

// --- Schedule of Values / Estimate Totals page: only if includeSOV is true ---
if (cfg.includeSOV && cfg.sov) {
  pages.push([
    headerTable(["Status: Active Estimates", "Contact:", `Date: ${cfg.date}`]),
    rule(),
    new Paragraph({ spacing: { after: 220 }, tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }], children: [
      new TextRun({ text: `Estimate: ${cfg.estimateNumber || "[ESTIMATE #]"}  ${cfg.projectRef}`, bold: true, size: 21, font: FONT, color: HEAD_DARK }),
      new TextRun({ text: "\tEstimate Totals", bold: true, size: 21, font: FONT, color: HEAD_DARK }),
    ] }),
    buildSovTable(cfg.sov.rows, "Total Estimate", cfg.totalPrice),
  ]);
}

// --- Scope of Work: only if includeScopeOfWork is true. Placement (own page vs.
// sharing the page with Clarifications) is a judgment call, not auto-detected —
// set cfg.scopeOfWorkOwnPage explicitly. Rule of thumb: a couple of short sentences
// share the page with Clarifications; anything that runs long, covers multiple
// phases/trades, or needs its own subheadings gets its own page. ---
const wantScope = !!(cfg.includeScopeOfWork && cfg.scopeOfWork && cfg.scopeOfWork.length);
const wantClarifications = !!(cfg.includeClarifications && cfg.exclusions && cfg.exclusions.length);

// A heading directly under the header rule needs a smaller "before" (the rule already
// reads as a break); a heading following another section's content needs the bigger
// gap so sections read as distinct blocks instead of running together. `firstOnPage`
// tracks this per page so whichever block leads gets the tight gap and the rest don't.
function scopeBlock(firstOnPage) { return [h2("Scope of Work", { before: firstOnPage ? 160 : 340 }), ...cfg.scopeOfWork.map((t) => p(t))]; }
function clarificationsBlock(firstOnPage) {
  return [h2("Clarifications and Exclusions", { before: firstOnPage ? 160 : 340 }), ...cfg.exclusions.map((t, i) => numbered(i + 1, t))];
}
function acceptanceBlock(firstOnPage) {
  return [
    h2("Acceptance", { before: firstOnPage ? 160 : 340 }),
    p("To proceed with the scope of work outlined above, please sign below and return an executed copy of this proposal. Upon acceptance, we will coordinate with the project team to schedule the work in alignment with the project timeline and other critical path activities.", { after: 400 }),
    p(cfg.client.name, { after: 0 }),
    p(cfg.client.company, { after: 320 }),
    p("Signature: ______________________________________", { after: 240 }),
    p("Name: __________________________________________", { after: 240 }),
    p("Title: ___________________________________________", { after: 240 }),
    p("Date: ___________________________________________", { after: 120 }),
  ];
}

if (wantScope && cfg.scopeOfWorkOwnPage) {
  // Scope of Work gets its own page; Clarifications + Acceptance follow on the next.
  pages.push([headerTable(rightAddr), rule(), ...scopeBlock(true)]);
  pages.push([headerTable(rightAddr), rule(), ...(wantClarifications ? clarificationsBlock(true) : []), ...acceptanceBlock(!wantClarifications)]);
} else {
  // Scope of Work (if any) shares a page with Clarifications + Acceptance.
  let placedFirst = false;
  const parts = [];
  if (wantScope) { parts.push(...scopeBlock(!placedFirst)); placedFirst = true; }
  if (wantClarifications) { parts.push(...clarificationsBlock(!placedFirst)); placedFirst = true; }
  parts.push(...acceptanceBlock(!placedFirst));
  pages.push([headerTable(rightAddr), rule(), ...parts]);
}

// The lever that actually keeps body text off the footer bar is the `footer`
// distance (how far the footer sits from the page's bottom edge) — NOT the `bottom`
// body margin. LibreOffice bounds text wrap against the footer's occupied region,
// so a bigger `bottom` margin alone does nothing (confirmed by pixel-measuring a
// render: increasing bottom from 900→1350 didn't move the gap at all). Pushing
// `footer` out to 1440 (1in) is what actually creates clearance. Don't "simplify"
// this back to only setting `bottom` without re-measuring a rendered page.
const pageProps = { page: { size: { width: DXA_PAGE_W, height: DXA_PAGE_H }, margin: { top: MARGIN, bottom: 900, left: MARGIN, right: MARGIN, footer: 1000 } } };
const footer = () => new Footer({ children: [bottomBar()] });

const doc = new Document({
  sections: pages.map((children) => ({ properties: pageProps, footers: { default: footer() }, children })),
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(cfg.outputName, buf);
  console.log("written:", cfg.outputName);
});
