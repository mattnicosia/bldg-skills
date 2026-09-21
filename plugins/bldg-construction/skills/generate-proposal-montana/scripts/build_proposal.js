#!/usr/bin/env node
/**
 * Build a Montana Contracting Corp. proposal PDF-ready .docx from a data.json.
 *
 * Usage: node build_proposal.js data.json output.docx
 *
 * See ../SKILL.md and ../example_data.json for the full field reference.
 */
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  BorderStyle, Table, TableRow, TableCell, WidthType, ShadingType,
  ImageRun, VerticalAlign, Header, Footer, PageBreak,
} = require("docx");
const fs = require("fs");
const path = require("path");

const SKILL_ROOT = path.dirname(__dirname);
const FONT = "Open Sans";
const SZ = 20; // 10pt (docx-js sizes are in half-points)
const TEXT = "222222";
const NAVY = "0B4F8C";

const [, , dataPath, outPath] = process.argv;
if (!dataPath || !outPath) {
  console.error("Usage: node build_proposal.js data.json output.docx");
  process.exit(1);
}
const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));

// ---------- required fields / defaults ----------
const D = Object.assign({
  signer_name: "Joseph Montana",
  signer_title: "President",
  logo_path: path.join(SKILL_ROOT, "assets", "logo.png"),
  gc_pct: 0,
  fee_pct: 0,
  insurance_pct: 0,
  tax_amount: null,
  tax_pct: null,
  tax_label: "Sales Tax",
}, data);

for (const req of ["date_long", "client_contact", "client_company", "client_addr1", "client_addr2", "project_name", "scope_items", "clarifications", "sov_items"]) {
  if (D[req] === undefined) {
    console.error(`Missing required field in data.json: ${req}`);
    process.exit(1);
  }
}

const logo = fs.readFileSync(D.logo_path);

// ---------- cascading pricing math ----------
// General Conditions, Fee, and Insurance each apply to the RUNNING subtotal,
// not all three to the same flat direct-cost base. This compounding order
// (GC -> Fee -> Insurance, each added before the next percentage is taken)
// is what matches how Montana Contracting's estimators actually build these
// numbers -- verified against real approved figures. Do not flatten this to
// three parallel percentages of the same base; it will not match.
const sovSubtotal = round2(D.sov_items.reduce((s, i) => s + i.amount, 0));
let running = sovSubtotal;
const gcAmount = round2(running * D.gc_pct);
running = round2(running + gcAmount);
const feeAmount = round2(running * D.fee_pct);
running = round2(running + feeAmount);
const insuranceAmount = round2(running * D.insurance_pct);
running = round2(running + insuranceAmount);
const pricingSubtotal = running;

let taxAmount;
if (D.tax_amount !== null) {
  taxAmount = round2(D.tax_amount);
} else if (D.tax_pct !== null) {
  taxAmount = round2(pricingSubtotal * D.tax_pct);
} else {
  taxAmount = 0;
}
const total = round2(pricingSubtotal + taxAmount);

function round2(v) { return Math.round((v + Number.EPSILON) * 100) / 100; }
function money(v) { return "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

if (D.expected_total !== undefined && Math.abs(D.expected_total - total) > 0.01) {
  console.error(`WARNING: computed total ${money(total)} does not match data.expected_total ${money(D.expected_total)}. Check sov_items / gc_pct / fee_pct / insurance_pct / tax before sending this to the client.`);
}

// ---------- shared helpers ----------
const noBorders = {
  top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
  left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
  insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
};
const gridBorders = {
  top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
  bottom: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
  left: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
  right: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "E4E6EA" },
  insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "E4E6EA" },
};

function T(text, opts) {
  opts = opts || {};
  return new TextRun({ text, font: FONT, size: SZ, color: TEXT, bold: !!opts.bold, italics: !!opts.italics });
}
function P(children, opts) {
  opts = opts || {};
  return new Paragraph({ children: Array.isArray(children) ? children : [children], alignment: opts.align, spacing: opts.spacing || { after: 0 }, indent: opts.indent });
}
function pageHeaderRow(rightLabel) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: noBorders,
    rows: [new TableRow({
      children: [
        new TableCell({ width: { size: 60, type: WidthType.PERCENTAGE }, children: [new Paragraph({ children: [new TextRun({ text: `Project: ${D.project_name}`, font: FONT, bold: true, size: SZ, color: TEXT })] })] }),
        new TableCell({ width: { size: 40, type: WidthType.PERCENTAGE }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: rightLabel, font: FONT, bold: true, size: SZ, color: TEXT })] })] }),
      ],
    })],
  });
}

// ---------- running header / footer (repeat on every page) ----------
const header = new Header({
  children: [
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      borders: noBorders,
      rows: [new TableRow({
        children: [
          new TableCell({
            width: { size: 50, type: WidthType.PERCENTAGE },
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({ children: [new ImageRun({ data: logo, transformation: { width: 106, height: 75 }, type: "png" })] })],
          }),
          new TableCell({
            width: { size: 50, type: WidthType.PERCENTAGE },
            verticalAlign: VerticalAlign.CENTER,
            children: [
              new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 0 }, children: [T("Montana Contracting Corp.")] }),
              new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 0 }, children: [T("173 North Route 9W")] }),
              new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 0 }, children: [T("Congers, NY, 10920")] }),
              new Paragraph({ alignment: AlignmentType.RIGHT, children: [T("(845) 398-1778")] }),
            ],
          }),
        ],
      })],
    }),
    new Paragraph({ border: { bottom: { color: "CCCCCC", space: 6, style: BorderStyle.SINGLE, size: 4 } }, spacing: { after: 0 }, children: [new TextRun({ text: "" })] }),
  ],
});

const footer = new Footer({
  children: [
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      borders: noBorders,
      rows: [new TableRow({
        children: [new TableCell({
          width: { size: 100, type: WidthType.PERCENTAGE },
          shading: { type: ShadingType.CLEAR, fill: NAVY },
          margins: { top: 120, bottom: 120, left: 200, right: 200 },
          children: [
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: "www.montanacontracting.com", font: FONT, bold: true, size: SZ, color: "FFFFFF" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Powered by ProEst", font: FONT, size: SZ - 2, color: "D9E4F5" })] }),
          ],
        })],
      })],
    }),
  ],
});

// ---------- PAGE 1: Proposal letter ----------
const page1 = [
  P(T(`Date: ${D.date_long}`), { spacing: { after: 200 } }),
  P(T(D.client_contact), { spacing: { after: 0 } }),
  P(T(D.client_company), { spacing: { after: 0 } }),
  P(T(D.client_addr1), { spacing: { after: 0 } }),
  P(T(D.client_addr2), { spacing: { after: 200 } }),
  P(T(`Re: ${D.project_name}`, { bold: true }), { spacing: { after: 200 } }),
  P(new TextRun({ text: "Proposal", font: FONT, size: SZ + 4, color: TEXT, bold: true }), { align: AlignmentType.CENTER, spacing: { after: 200 } }),
  P([
    T("Montana Contracting Corp. will furnish all necessary supervision, labor, materials and equipment to build the above-referenced project for the sum of: "),
    T(money(total), { bold: true }),
  ], { spacing: { after: 200 } }),
  P(T("Attachments:", { bold: true }), { spacing: { after: 0 } }),
  P(T("Scope of Work"), { spacing: { after: 0 } }),
  P(T("Clarifications & Exclusions"), { spacing: { after: 0 } }),
  P(T("Schedule of Values"), { spacing: { after: 200 } }),
  P(T("All work will be done in a professional and workman-like manner, licensed as required by law. All work to be fully covered with compensation and liability insurances."), { spacing: { after: 200 } }),
  P(T("Thank you for the opportunity."), { spacing: { after: 200 } }),
  P(T("Very truly yours,"), { spacing: { after: 40 } }),
  P(T(D.signer_name), { spacing: { after: 0 } }),
  P(T("Montana Contracting Corp."), { spacing: { after: 260 } }),
  P(T("Accepted By: __________________________________"), { spacing: { after: 100 } }),
  P(T("Date of Acceptance: _____________________________")),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------- PAGE 2: Scope of Work ----------
const page2 = [
  pageHeaderRow("Scope of Work"),
  new Paragraph({ text: "", spacing: { after: 200 } }),
  ...D.scope_items.map(item => P([T(item.label + " — ", { bold: true }), T(item.description)], { spacing: { after: 160 } })),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------- PAGE 3: Clarifications & Exclusions ----------
const page3 = [
  P(T("Clarifications & Exclusions:", { bold: true }), { spacing: { after: 240 } }),
  ...D.clarifications.map((n, i) => P(T(`${i + 1}. ${n}`), { spacing: { after: 120 }, indent: { left: 360 } })),
  new Paragraph({ children: [new PageBreak()] }),
];

// ---------- PAGE 4: Schedule of Values (by CSI subdivision) + Pricing Summary ----------
function sovDataRow(code, desc, amount) {
  return new TableRow({
    children: [
      new TableCell({ width: { size: 18, type: WidthType.PERCENTAGE }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: code, font: FONT, size: SZ, color: TEXT })] })] }),
      new TableCell({ width: { size: 52, type: WidthType.PERCENTAGE }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: desc, font: FONT, size: SZ, color: TEXT })] })] }),
      new TableCell({ width: { size: 30, type: WidthType.PERCENTAGE }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: money(amount), font: FONT, size: SZ, color: TEXT })] })] }),
    ],
  });
}
function sovSubtotalRow(label, amount) {
  return new TableRow({
    children: [
      new TableCell({ columnSpan: 2, shading: { type: ShadingType.CLEAR, fill: "E4E9F5" }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: label, font: FONT, bold: true, size: SZ, color: TEXT })] })] }),
      new TableCell({ shading: { type: ShadingType.CLEAR, fill: "E4E9F5" }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: money(amount), font: FONT, bold: true, size: SZ, color: TEXT })] })] }),
    ],
  });
}
const sovHeadRow = new TableRow({
  children: [
    new TableCell({ width: { size: 18, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.CLEAR, fill: "101418" }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: "CSI Subdivision", font: FONT, bold: true, size: SZ, color: "FFFFFF" })] })] }),
    new TableCell({ width: { size: 52, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.CLEAR, fill: "101418" }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: "Description", font: FONT, bold: true, size: SZ, color: "FFFFFF" })] })] }),
    new TableCell({ width: { size: 30, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.CLEAR, fill: "101418" }, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Amount", font: FONT, bold: true, size: SZ, color: "FFFFFF" })] })] }),
  ],
});
const sovItemsSorted = [...D.sov_items].sort((a, b) => a.code.localeCompare(b.code));
const sovRows = [sovHeadRow, ...sovItemsSorted.map(i => sovDataRow(i.code, i.description, i.amount))];
sovRows.push(sovSubtotalRow("Subtotal", sovSubtotal));

const sovTable = new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, columnWidths: [1700, 4900, 2400], borders: gridBorders, rows: sovRows });

function pricingRow(label, amount, opts) {
  opts = opts || {};
  const cellProps = opts.shade ? { shading: { type: ShadingType.CLEAR, fill: opts.shade } } : {};
  return new TableRow({
    children: [
      new TableCell({ width: { size: 70, type: WidthType.PERCENTAGE }, ...cellProps, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: label, font: FONT, bold: !!opts.bold, size: SZ, color: TEXT })] })] }),
      new TableCell({ width: { size: 30, type: WidthType.PERCENTAGE }, ...cellProps, margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: money(amount), font: FONT, bold: !!opts.bold, size: SZ, color: TEXT })] })] }),
    ],
  });
}
const pricingRows = [
  pricingRow("Subtotal (Schedule of Values)", sovSubtotal, { shade: "E4E9F5", bold: true }),
];
if (D.gc_pct) pricingRows.push(pricingRow(`General Conditions (${(D.gc_pct * 100).toFixed(1).replace(/\.0$/, "")}%)`, gcAmount));
if (D.fee_pct) pricingRows.push(pricingRow(`Fee (${(D.fee_pct * 100).toFixed(1).replace(/\.0$/, "")}%)`, feeAmount));
if (D.insurance_pct) pricingRows.push(pricingRow(`Insurance (${(D.insurance_pct * 100).toFixed(1).replace(/\.0$/, "")}%)`, insuranceAmount));
pricingRows.push(pricingRow("Subtotal", pricingSubtotal, { shade: "E4E9F5", bold: true }));
pricingRows.push(pricingRow(D.tax_label, taxAmount));
pricingRows.push(pricingRow("TOTAL", total, { shade: "C9D6EE", bold: true }));

const pricingTable = new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, columnWidths: [7000, 2000], borders: gridBorders, rows: pricingRows });

const page4 = [
  pageHeaderRow("Schedule of Values — by CSI MasterFormat Subdivision"),
  new Paragraph({ text: "", spacing: { after: 160 } }),
  sovTable,
  new Paragraph({ text: "", spacing: { after: 240 } }),
  P(T("Pricing Summary", { bold: true }), { spacing: { after: 120 } }),
  pricingTable,
];

// ---------- assemble ----------
const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1400, bottom: 1100, left: 900, right: 900 } } },
    headers: { default: header },
    footers: { default: footer },
    children: [...page1, ...page2, ...page3, ...page4],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outPath, buf);
  console.log(`Built ${outPath}`);
  console.log(`Schedule of Values subtotal: ${money(sovSubtotal)}`);
  if (D.gc_pct) console.log(`General Conditions (${D.gc_pct * 100}%): ${money(gcAmount)}`);
  if (D.fee_pct) console.log(`Fee (${D.fee_pct * 100}%): ${money(feeAmount)}`);
  if (D.insurance_pct) console.log(`Insurance (${D.insurance_pct * 100}%): ${money(insuranceAmount)}`);
  console.log(`Pricing subtotal: ${money(pricingSubtotal)}`);
  console.log(`${D.tax_label}: ${money(taxAmount)}`);
  console.log(`TOTAL: ${money(total)}`);
});
