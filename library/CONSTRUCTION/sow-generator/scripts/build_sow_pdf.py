"""
build_sow_pdf.py — Editorial Scope of Work PDF Generator

Generates a polished, typeset PDF from the same sow_data.json structure.
Black/gray/white only. Helvetica/Helvetica-Bold for typography.

Layout:
- Cover page with massive editorial title
- Table of contents
- Scope of work organized by subdivision (heavy black band headers)
- Appendix: notes, conflicts, TBD, QA report

Usage:
    python build_sow_pdf.py <sow_data.json> <output_path.pdf>
"""

import json
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Flowable
)
from reportlab.pdfgen import canvas


# Color palette (strict black/gray/white)
COLOR_BLACK = HexColor("#000000")
COLOR_DARK = HexColor("#1A1A1A")
COLOR_CHARCOAL = HexColor("#3A3A3A")
COLOR_MEDIUM = HexColor("#7A7A7A")
COLOR_LIGHT = HexColor("#D8D8D8")
COLOR_WHISPER = HexColor("#F2F2F2")
COLOR_WHITE = HexColor("#FFFFFF")


# Page geometry
PAGE_WIDTH, PAGE_HEIGHT = letter
LEFT_MARGIN = 0.75 * inch
RIGHT_MARGIN = 0.75 * inch
TOP_MARGIN = 0.85 * inch
BOTTOM_MARGIN = 0.85 * inch
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


# ============================================================
# STYLES
# ============================================================
def _styles():
    return {
        "doc_label": ParagraphStyle(
            "doc_label",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=COLOR_MEDIUM,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Helvetica-Bold",
            fontSize=42,
            leading=48,
            textColor=COLOR_BLACK,
            spaceAfter=12,
            alignment=TA_LEFT,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=COLOR_CHARCOAL,
            alignment=TA_LEFT,
        ),
        "control_label": ParagraphStyle(
            "control_label",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=COLOR_MEDIUM,
            alignment=TA_LEFT,
        ),
        "control_value": ParagraphStyle(
            "control_value",
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=COLOR_BLACK,
            alignment=TA_LEFT,
        ),
        "section_label": ParagraphStyle(
            "section_label",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=COLOR_MEDIUM,
            alignment=TA_LEFT,
        ),
        "page_title": ParagraphStyle(
            "page_title",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=COLOR_BLACK,
            alignment=TA_LEFT,
        ),
        "subdivision_code": ParagraphStyle(
            "subdivision_code",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=COLOR_WHITE,
            alignment=TA_LEFT,
        ),
        "subdivision_title": ParagraphStyle(
            "subdivision_title",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=COLOR_WHITE,
            alignment=TA_LEFT,
        ),
        "item_num": ParagraphStyle(
            "item_num",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=COLOR_MEDIUM,
            alignment=TA_LEFT,
        ),
        "item_ref": ParagraphStyle(
            "item_ref",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=COLOR_CHARCOAL,
            alignment=TA_LEFT,
        ),
        "item_ref_unverified": ParagraphStyle(
            "item_ref_unverified",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=COLOR_BLACK,
            alignment=TA_LEFT,
        ),
        "item_scope": ParagraphStyle(
            "item_scope",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=COLOR_BLACK,
            alignment=TA_LEFT,
        ),
        "legend": ParagraphStyle(
            "legend",
            fontName="Helvetica-Oblique",
            fontSize=8,
            leading=11,
            textColor=COLOR_MEDIUM,
            alignment=TA_LEFT,
        ),
        "appendix_section": ParagraphStyle(
            "appendix_section",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=COLOR_BLACK,
            spaceBefore=24,
            spaceAfter=8,
            alignment=TA_LEFT,
        ),
        "appendix_subhead": ParagraphStyle(
            "appendix_subhead",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=COLOR_MEDIUM,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        "appendix_body": ParagraphStyle(
            "appendix_body",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=COLOR_BLACK,
            alignment=TA_LEFT,
        ),
        "toc_code": ParagraphStyle(
            "toc_code",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=COLOR_BLACK,
        ),
        "toc_title": ParagraphStyle(
            "toc_title",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=COLOR_BLACK,
        ),
        "toc_page": ParagraphStyle(
            "toc_page",
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            textColor=COLOR_MEDIUM,
            alignment=TA_RIGHT,
        ),
    }


# ============================================================
# CUSTOM FLOWABLES
# ============================================================
class HeavyBand(Flowable):
    """A thick black horizontal band used as a divider."""

    def __init__(self, width, thickness=3):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness

    def wrap(self, available_width, available_height):
        return self.width, self.thickness

    def draw(self):
        self.canv.setFillColor(COLOR_BLACK)
        self.canv.rect(0, 0, self.width, self.thickness, fill=1, stroke=0)


class ThinRule(Flowable):
    def __init__(self, width, color=COLOR_LIGHT, thickness=0.5):
        Flowable.__init__(self)
        self.width = width
        self.color = color
        self.thickness = thickness

    def wrap(self, available_width, available_height):
        return self.width, self.thickness

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)


# ============================================================
# PAGE TEMPLATES (header / footer)
# ============================================================
class CoverPage:
    """Used to suppress header/footer on cover page."""
    pass


def _make_page_decorator(sow_data):
    """Returns a function that draws header/footer on each page (except cover)."""
    project_name = sow_data.get("project_name", "")
    date_prepared = sow_data.get("date_prepared", "")

    def _decorate(canv, doc):
        canv.saveState()

        # Skip cover page
        if doc.page == 1:
            canv.restoreState()
            return

        # Header: project name (left) | page number (right)
        canv.setFont("Helvetica-Oblique", 8)
        canv.setFillColor(COLOR_MEDIUM)
        canv.drawString(LEFT_MARGIN, PAGE_HEIGHT - 0.5 * inch, project_name)
        canv.drawRightString(
            PAGE_WIDTH - RIGHT_MARGIN,
            PAGE_HEIGHT - 0.5 * inch,
            f"{doc.page}",
        )

        # Header thin rule
        canv.setStrokeColor(COLOR_LIGHT)
        canv.setLineWidth(0.5)
        canv.line(
            LEFT_MARGIN, PAGE_HEIGHT - 0.55 * inch,
            PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - 0.55 * inch,
        )

        # Footer: confidential (center) | date (right)
        canv.setFont("Helvetica", 8)
        canv.setFillColor(COLOR_MEDIUM)
        canv.drawCentredString(
            PAGE_WIDTH / 2, 0.5 * inch,
            f"Confidential - {sow_data.get('prepared_by', '[Prepared By Not Specified]')}",
        )
        canv.drawRightString(
            PAGE_WIDTH - RIGHT_MARGIN, 0.5 * inch,
            date_prepared,
        )

        # Footer thin rule
        canv.line(
            LEFT_MARGIN, 0.65 * inch,
            PAGE_WIDTH - RIGHT_MARGIN, 0.65 * inch,
        )

        canv.restoreState()

    return _decorate


# ============================================================
# COVER PAGE
# ============================================================
def _build_cover(story, sow_data, styles):
    project_name = sow_data.get("project_name", "Project Name")
    project_address = sow_data.get("project_address", "")
    date_prepared = sow_data.get("date_prepared", datetime.now().strftime("%B %d, %Y"))
    prepared_by = sow_data.get("prepared_by", "[Prepared By Not Specified]")
    revision = sow_data.get("revision", "1.0")
    status = sow_data.get("status", "FOR PRICING")

    # Top spacing
    story.append(Spacer(1, 1.0 * inch))

    # Document type label
    story.append(Paragraph("SCOPE OF WORK", styles["doc_label"]))
    story.append(Spacer(1, 0.05 * inch))
    story.append(HeavyBand(CONTENT_WIDTH, thickness=4))
    story.append(Spacer(1, 0.6 * inch))

    # Massive editorial title
    story.append(Paragraph(project_name, styles["cover_title"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(project_address, styles["cover_subtitle"]))

    # Big whitespace before document control
    story.append(Spacer(1, 3.5 * inch))

    # Bottom heavy band
    story.append(HeavyBand(CONTENT_WIDTH, thickness=4))
    story.append(Spacer(1, 0.25 * inch))

    # Document control as a table
    control_data = [
        [Paragraph("PREPARED BY", styles["control_label"]),
         Paragraph(prepared_by, styles["control_value"])],
        [Paragraph("DATE", styles["control_label"]),
         Paragraph(date_prepared, styles["control_value"])],
        [Paragraph("REVISION", styles["control_label"]),
         Paragraph(revision, styles["control_value"])],
        [Paragraph("STATUS", styles["control_label"]),
         Paragraph(status, styles["control_value"])],
    ]
    control_table = Table(control_data, colWidths=[1.5 * inch, CONTENT_WIDTH - 1.5 * inch])
    control_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(control_table)

    story.append(PageBreak())


# ============================================================
# TABLE OF CONTENTS
# ============================================================
def _build_toc(story, sow_data, styles):
    story.append(Paragraph("CONTENTS", styles["doc_label"]))
    story.append(Spacer(1, 0.05 * inch))
    story.append(HeavyBand(CONTENT_WIDTH, thickness=4))
    story.append(Spacer(1, 0.4 * inch))

    # Build TOC table
    rows = []

    # Header row
    rows.append([
        Paragraph("CODE", styles["section_label"]),
        Paragraph("SUBDIVISION", styles["section_label"]),
        Paragraph("SHEET", ParagraphStyle(
            "right_label", parent=styles["section_label"], alignment=TA_RIGHT
        )),
    ])

    for subdiv in sow_data.get("subdivisions", []):
        rows.append([
            Paragraph(subdiv.get("code", ""), styles["toc_code"]),
            Paragraph(subdiv.get("title", ""), styles["toc_title"]),
            Paragraph("Scope", styles["toc_page"]),
        ])

    appendix_sections = ["Notes and Clarifications", "Conflicts", "TBD Items", "QA Report"]
    rows.append(["", "", ""])
    for section_name in appendix_sections:
        rows.append([
            "",
            Paragraph(section_name, styles["toc_title"]),
            Paragraph("Appendix", styles["toc_page"]),
        ])

    col_widths = [1.5 * inch, CONTENT_WIDTH - 2.3 * inch, 0.8 * inch]
    toc_table = Table(rows, colWidths=col_widths, repeatRows=1)

    table_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 1, COLOR_BLACK),
    ]
    # Whisper grey rule under each subdivision row
    for i in range(1, len(rows)):
        if rows[i][0] != "" or rows[i][1] != "":
            table_style.append(("LINEBELOW", (0, i), (-1, i), 0.4, COLOR_WHISPER))

    # Heavy band before appendix block
    appendix_start = len(rows) - len(appendix_sections) - 1
    if appendix_start > 0:
        table_style.append(("LINEABOVE", (0, appendix_start + 1), (-1, appendix_start + 1), 1, COLOR_BLACK))

    toc_table.setStyle(TableStyle(table_style))
    story.append(toc_table)
    story.append(PageBreak())


# ============================================================
# SCOPE OF WORK BODY
# ============================================================
def _build_sow_body(story, sow_data, styles):
    project_name = sow_data.get("project_name", "")
    project_address = sow_data.get("project_address", "")

    # Page header — section label
    story.append(Paragraph("SCOPE OF WORK", styles["doc_label"]))
    story.append(Spacer(1, 0.05 * inch))
    story.append(HeavyBand(CONTENT_WIDTH, thickness=4))
    story.append(Spacer(1, 0.25 * inch))

    # Project name (smaller reminder)
    story.append(Paragraph(project_name, styles["page_title"]))
    story.append(Paragraph(project_address, ParagraphStyle(
        "addr_sub", parent=styles["legend"], fontSize=9, italic=False, textColor=COLOR_MEDIUM
    )))
    story.append(Spacer(1, 0.2 * inch))

    # Directive legend
    legend_text = "F/I  Furnish & Install  ·  F/O  Furnish Only  ·  I/O  Install Only  ·  Remove  Demolition  ·  Provide  Services / Shop Drawings"
    legend_table = Table(
        [[Paragraph(legend_text, styles["legend"])]],
        colWidths=[CONTENT_WIDTH],
    )
    legend_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, COLOR_LIGHT),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, COLOR_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 0.25 * inch))

    # Column headers
    col_widths = [0.6 * inch, 1.3 * inch, CONTENT_WIDTH - 1.9 * inch]

    header_row = [
        Paragraph("ITEM", styles["section_label"]),
        Paragraph("REFERENCE", styles["section_label"]),
        Paragraph("SCOPE", styles["section_label"]),
    ]
    header_table = Table([header_row], colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 1, COLOR_BLACK),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.1 * inch))

    # Each subdivision
    for subdiv_idx, subdiv in enumerate(sow_data.get("subdivisions", [])):
        _build_subdivision(story, subdiv, subdiv_idx, styles, col_widths)


def _build_subdivision(story, subdiv, subdiv_idx, styles, col_widths):
    code = subdiv.get("code", "")
    title = subdiv.get("title", "").upper()

    # Heavy black subdivision header band
    header_data = [[
        Paragraph(code, styles["subdivision_code"]),
        Paragraph(title, styles["subdivision_title"]),
    ]]
    header_widths = [1.3 * inch, sum(col_widths) - 1.3 * inch]
    header_table = Table(header_data, colWidths=header_widths)
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_BLACK),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Line items table
    item_rows = []
    for item_idx, item in enumerate(subdiv.get("line_items", [])):
        ref = item.get("reference", "[UNVERIFIED]")
        scope = item.get("scope_item", "")
        seq = f"{subdiv_idx + 1:02d}.{item_idx + 1:02d}"

        ref_style = styles["item_ref_unverified"] if ref.strip() == "[UNVERIFIED]" else styles["item_ref"]

        item_rows.append([
            Paragraph(seq, styles["item_num"]),
            Paragraph(ref, ref_style),
            Paragraph(scope, styles["item_scope"]),
        ])

    if not item_rows:
        return

    item_table = Table(item_rows, colWidths=col_widths)
    item_table_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(len(item_rows)):
        item_table_style.append(("LINEBELOW", (0, i), (-1, i), 0.4, COLOR_WHISPER))

    item_table.setStyle(TableStyle(item_table_style))

    # Keep header + first 2 items together so subdivision doesn't orphan
    keep_block = KeepTogether([header_table, Spacer(1, 0.05 * inch), item_table])
    story.append(keep_block)
    story.append(Spacer(1, 0.2 * inch))


# ============================================================
# APPENDIX
# ============================================================
def _build_appendix(story, sow_data, styles):
    story.append(PageBreak())

    story.append(Paragraph("APPENDIX", styles["doc_label"]))
    story.append(Spacer(1, 0.05 * inch))
    story.append(HeavyBand(CONTENT_WIDTH, thickness=4))
    story.append(Spacer(1, 0.25 * inch))

    # ===== Notes and Clarifications =====
    _appendix_section_header(story, "NOTES AND CLARIFICATIONS", styles)

    story.append(Paragraph("Standard", styles["appendix_subhead"]))
    standard_clar = sow_data.get("standard_clarifications", [])
    _build_appendix_list(story, standard_clar, styles)

    drawing_clar = sow_data.get("drawing_specific_clarifications", [])
    if drawing_clar:
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph("Drawing-Specific", styles["appendix_subhead"]))
        _build_appendix_ref_list(story, drawing_clar, styles)

    # ===== Conflicts =====
    _appendix_section_header(story, "CONFLICTS", styles)
    conflicts = sow_data.get("conflicts", [])
    if conflicts:
        _build_appendix_ref_list(story, conflicts, styles)
    else:
        story.append(Paragraph("None identified.", ParagraphStyle(
            "none", parent=styles["appendix_body"], fontName="Helvetica-Oblique",
            textColor=COLOR_MEDIUM,
        )))

    # ===== TBD Items =====
    _appendix_section_header(story, "TBD ITEMS - RFI REQUIRED", styles)
    tbd_items = sow_data.get("tbd_items", [])
    if tbd_items:
        _build_appendix_ref_list(story, tbd_items, styles)
    else:
        story.append(Paragraph("None identified.", ParagraphStyle(
            "none", parent=styles["appendix_body"], fontName="Helvetica-Oblique",
            textColor=COLOR_MEDIUM,
        )))

    # ===== QA Report =====
    _appendix_section_header(story, "QA REPORT", styles)
    qa = sow_data.get("qa_report", {})

    metrics = [
        ("Total Line Items", qa.get("total_line_items", 0)),
        ("Subdivisions Used", qa.get("subdivisions_used", 0)),
        ("Items with [UNVERIFIED] Citations", qa.get("unverified_count", 0)),
        ("Items with [Not Specified] Specs", qa.get("not_specified_count", 0)),
        ("Conflicts Detected", len(conflicts)),
        ("TBD Items Flagged", len(tbd_items)),
        ("Trade Splits Applied", qa.get("trade_splits_applied", 0)),
        ("Auto-Inserted Line Items", qa.get("auto_inserted_count", 0)),
    ]
    qa_rows = []
    for label, value in metrics:
        qa_rows.append([
            Paragraph(label, styles["appendix_subhead"]),
            Paragraph(
                str(value),
                ParagraphStyle("v", parent=styles["appendix_body"], fontName="Helvetica-Bold")
            ),
        ])

    qa_table = Table(qa_rows, colWidths=[CONTENT_WIDTH * 0.65, CONTENT_WIDTH * 0.35])
    qa_table_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(len(qa_rows)):
        qa_table_style.append(("LINEBELOW", (0, i), (-1, i), 0.4, COLOR_WHISPER))
    qa_table.setStyle(TableStyle(qa_table_style))
    story.append(qa_table)

    qa_notes = qa.get("notes", [])
    if qa_notes:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("QA NOTES", styles["appendix_subhead"]))
        for note in qa_notes:
            story.append(Paragraph(f"&bull;  {note}", styles["appendix_body"]))
            story.append(Spacer(1, 0.05 * inch))


def _appendix_section_header(story, title, styles):
    story.append(Spacer(1, 0.15 * inch))
    story.append(HeavyBand(CONTENT_WIDTH, thickness=3))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(title, styles["appendix_section"]))
    story.append(ThinRule(CONTENT_WIDTH))
    story.append(Spacer(1, 0.15 * inch))


def _build_appendix_list(story, items, styles):
    rows = [[Paragraph(item, styles["appendix_body"])] for item in items]
    if not rows:
        return
    table = Table(rows, colWidths=[CONTENT_WIDTH])
    table_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(len(rows)):
        table_style.append(("LINEBELOW", (0, i), (-1, i), 0.4, COLOR_WHISPER))
    table.setStyle(TableStyle(table_style))
    story.append(table)


def _build_appendix_ref_list(story, items, styles):
    rows = []
    for item in items:
        rows.append([
            Paragraph(item.get("reference", ""), styles["item_ref"]),
            Paragraph(item.get("text", ""), styles["appendix_body"]),
        ])
    if not rows:
        return
    table = Table(rows, colWidths=[1.5 * inch, CONTENT_WIDTH - 1.5 * inch])
    table_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(len(rows)):
        table_style.append(("LINEBELOW", (0, i), (-1, i), 0.4, COLOR_WHISPER))
    table.setStyle(TableStyle(table_style))
    story.append(table)


# ============================================================
# MAIN ENTRY
# ============================================================
def build_sow_pdf(sow_data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title=sow_data.get("project_name", "Scope of Work"),
        author=sow_data.get("prepared_by", "[Prepared By Not Specified]"),
    )

    styles = _styles()
    story = []

    _build_cover(story, sow_data, styles)
    _build_toc(story, sow_data, styles)
    _build_sow_body(story, sow_data, styles)
    _build_appendix(story, sow_data, styles)

    page_decorator = _make_page_decorator(sow_data)
    doc.build(story, onFirstPage=page_decorator, onLaterPages=page_decorator)

    return output_path


def filter_by_responsibility(sow_data: dict, responsibility: str) -> dict:
    """
    Return a copy of sow_data filtered to items matching the given responsibility.

    responsibility: "Landlord" | "Tenant" | "All"
      - "Landlord" -> keep items tagged Landlord or Both
      - "Tenant"   -> keep items tagged Tenant or Both
      - "All"      -> no filtering (returns sow_data unchanged)

    Items without a `responsibility` field are kept in all outputs (for back-compat
    with non-split SOWs). Empty subdivisions are dropped from the filtered copy.

    Also stamps the project name so the output shows "LANDLORD SOW" or "TENANT SOW".
    """
    if responsibility == "All":
        return sow_data

    if responsibility not in ("Landlord", "Tenant"):
        raise ValueError(f"responsibility must be 'Landlord', 'Tenant', or 'All' -- got {responsibility!r}")

    import copy
    filtered = copy.deepcopy(sow_data)

    keep_tags = {responsibility, "Both"}
    new_subs = []
    for sub in filtered.get("subdivisions", []):
        items = sub.get("line_items", [])
        kept = [
            i for i in items
            if i.get("responsibility") is None or i.get("responsibility") in keep_tags
        ]
        if kept:
            sub["line_items"] = kept
            new_subs.append(sub)
    filtered["subdivisions"] = new_subs

    suffix = f" - {responsibility.upper()} SOW"
    if not filtered.get("project_name", "").endswith(suffix):
        filtered["project_name"] = filtered.get("project_name", "") + suffix

    return filtered


if __name__ == "__main__":
    args = sys.argv[1:]
    responsibility = "All"
    if "--responsibility" in args:
        idx = args.index("--responsibility")
        responsibility = args[idx + 1]
        del args[idx:idx + 2]

    if len(args) < 2:
        print("Usage: python build_sow_pdf.py <sow_data.json> <output_path.pdf> "
              "[--responsibility Landlord|Tenant|All]")
        sys.exit(1)

    with open(args[0], "r") as f:
        sow_data = json.load(f)

    sow_data = filter_by_responsibility(sow_data, responsibility)
    saved = build_sow_pdf(sow_data, args[1])
    print(f"SOW PDF saved: {saved} (responsibility filter: {responsibility})")
