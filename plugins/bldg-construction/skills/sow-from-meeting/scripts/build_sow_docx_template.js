/**
 * sow-from-meeting :: build_sow_docx_template.js
 *
 * Starting template for turning a meeting-transcript-derived scope of work into a
 * polished Word document. Copy this file, replace the placeholder content in the
 * `sections:` array near the bottom with the project's actual scope items, and run.
 *
 * Requires the `docx` npm package (preinstalled in the Cowork sandbox).
 * Run with: node build_sow_docx_template.js
 *
 * After building, ALWAYS render to PDF and visually check pages before delivering
 * (see the docx skill's SKILL.md for the soffice.py / pdftoppm verification steps).
 */

const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  BorderStyle, ShadingType, Header, Footer, PageNumber, PageBreak,
} = require("docx");
const fs = require("fs");

// ---- Palette (matches sow-generator's visual language) ----
const CHARCOAL = "3A3A3A";
const MEDGRAY = "7A7A7A";
const LIGHTGRAY = "E8E8E8";
const BLACK = "000000";
const FLAG_RED = "8B0000";

// ---- Helpers ----

function divHeading(code, title) {
  return new Paragraph({
    spacing: { before: 320, after: 100 },
    border: { bottom: { color: BLACK, space: 2, style: BorderStyle.SINGLE, size: 10 } },
    children: [
      new TextRun({ text: `DIVISION ${code} `, bold: true, size: 26, color: BLACK }),
      new TextRun({ text: title.toUpperCase(), bold: true, size: 26, color: BLACK }),
    ],
  });
}

function subHeading(code, title) {
  return new Paragraph({
    spacing: { before: 200, after: 80 },
    shading: { type: ShadingType.CLEAR, fill: MEDGRAY },
    children: [new TextRun({ text: `${code} — ${title}`, bold: true, size: 22, color: "FFFFFF" })],
  });
}

/**
 * A single scope line item.
 * @param {string} text  - the directive-language scope description
 * @param {string|null} ref - source citation, e.g. "Sheet A-100.00" or "Per Meeting, 08/06/26"
 * @param {string|null} tag - "TBD", "ALLOWANCE", "ALTERNATE", "UNVERIFIED", or null
 */
function item(text, ref, tag) {
  const runs = [];
  if (tag) runs.push(new TextRun({ text: `[${tag}] `, bold: true, size: 19, color: FLAG_RED }));
  runs.push(new TextRun({ text, size: 20, color: BLACK }));
  if (ref) runs.push(new TextRun({ text: `  (${ref})`, italics: true, size: 17, color: "555555" }));
  return new Paragraph({ bullet: { level: 0 }, spacing: { after: 60 }, children: runs });
}

function noteBlock(text) {
  return new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text, italics: true, size: 19, color: "555555" })] });
}

function bodyPara(text) {
  return new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text, size: 20 })] });
}

function sectionHeader(text) {
  return new Paragraph({
    spacing: { before: 400, after: 120 },
    shading: { type: ShadingType.CLEAR, fill: CHARCOAL },
    children: [new TextRun({ text, bold: true, size: 28, color: "FFFFFF" })],
  });
}

// =====================================================================
// PROJECT-SPECIFIC CONTENT — replace everything below with real content
// =====================================================================

const PROJECT = {
  name: "PROJECT NAME",
  address: "Project Address",
  preparedBy: "Preparer Name, Montana Contracting Corp.",
  datePrepared: "Month DD, YYYY",
  preparedFor: "Owner Name(s)",
  basisOfScope: "Meeting transcript, [date] ([attendees]); [drawing set reference, if any].",
  purpose: "Describe the actual purpose of this document here — e.g. supporting a bank appraisal, an internal budget conversation, a design-development milestone — and state plainly that it is a preliminary/schematic-level scope, not an issued-CD bid scope.",
};

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 }, // US Letter
        margin: { top: 1000, bottom: 1000, left: 1080, right: 1080 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: `${PROJECT.name} — Preliminary Scope of Work`, size: 16, color: "777777" })],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Confidential — Montana Contracting Corp.   |   Page ", size: 16, color: "777777" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "777777" }),
            new TextRun({ text: " of ", size: 16, color: "777777" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: "777777" }),
          ],
        })],
      }),
    },
    children: [
      // COVER
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: PROJECT.name.toUpperCase(), bold: true, size: 44 })] }),
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Preliminary Scope of Work", size: 28, color: "444444" })] }),
      new Paragraph({
        spacing: { after: 300 },
        border: { bottom: { color: BLACK, space: 4, style: BorderStyle.SINGLE, size: 12 } },
        children: [new TextRun({ text: PROJECT.address, size: 22, color: "444444" })],
      }),
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Prepared By: ", bold: true, size: 20 }), new TextRun({ text: PROJECT.preparedBy, size: 20 })] }),
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Date Prepared: ", bold: true, size: 20 }), new TextRun({ text: PROJECT.datePrepared, size: 20 })] }),
      new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Prepared For: ", bold: true, size: 20 }), new TextRun({ text: PROJECT.preparedFor, size: 20 })] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Basis of Scope: ", bold: true, size: 20 }), new TextRun({ text: PROJECT.basisOfScope, size: 20 })] }),
      new Paragraph({
        spacing: { after: 100 }, shading: { type: ShadingType.CLEAR, fill: LIGHTGRAY },
        children: [new TextRun({ text: "PURPOSE & LIMITATIONS: ", bold: true, size: 19 }), new TextRun({ text: PROJECT.purpose, size: 19 })],
      }),
      new Paragraph({ spacing: { before: 200, after: 60 }, children: [new TextRun({ text: "Directive Legend", bold: true, size: 19 })] }),
      noteBlock("F/I = Furnish and Install   |   F/O = Furnish Only   |   I/O = Install Only   |   Remove = Demolition   |   Provide = Services / Non-Material Work"),

      new Paragraph({ children: [new PageBreak()] }),

      sectionHeader("SCOPE OF WORK BY CSI MASTERFORMAT DIVISION"),

      // EXAMPLE DIVISION — duplicate this pattern per division/subdivision actually needed
      divHeading("02", "Existing Conditions"),
      subHeading("02 41 00", "Demolition"),
      item("Example: Remove Existing [Item] at [Location]", "Sheet [X]; or Per Meeting, [date]"),
      // ... add every real scope line here, grouped by division/subdivision ...

      new Paragraph({ children: [new PageBreak()] }),

      sectionHeader("FF&E / OWNER-FURNISHED EXCLUSIONS"),
      bodyPara("State the owner's own definition of the FF&E boundary if they gave one, then list every excluded item."),
      item("Example: [FF&E item]", "Per Meeting, [date]"),

      sectionHeader("ALLOWANCES & BUDGET ASSUMPTIONS"),
      bodyPara("Every $ figure actually discussed in the meeting, with its source — these are placeholders, not firm bids."),
      item("Example: [Trade] allowance of $[X] — [basis, e.g. owner's own quote, GC ballpark]", null),

      sectionHeader("ALTERNATES / STRIKE ITEMS"),
      bodyPara("Items the owner wants priced independently so they can be added/removed without redrawing."),
      item("Example: [Item] — base case vs. alternate", "Per Meeting, [date]"),

      sectionHeader("OPEN ITEMS / CLARIFICATIONS NEEDED"),
      item("Example: [Pending engineer confirmation / unmade decision / unengaged subcontractor]", null),

      new Paragraph({ spacing: { before: 400 }, children: [new TextRun({ text: "— End of Preliminary Scope of Work —", italics: true, size: 18, color: "777777" })] }),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("./SOW_output.docx", buffer);
  console.log("done");
});
