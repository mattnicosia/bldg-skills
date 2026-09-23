"""
export_pdf.py -- Cross-platform xlsx -> branded PDF. Replaces export_pdf.ps1.

The Windows original drove Excel COM: it set each sheet's PageSetup, dropped the O+D
logo into the left print header via `LeftHeaderPicture` + the `&G` placeholder (which
makes Excel repeat it on every printed page), then called ExportAsFixedFormat.

None of that exists off Windows, and **openpyxl cannot write header/footer images** --
there is no `LeftHeaderPicture` equivalent. So the work is split:

  1. LibreOffice headless converts xlsx -> PDF. It honors the page setup written by
     build_estimate.py (portrait, letter, fit-to-1-page-wide, margins), so pagination
     and column fitting match what Excel produced.
  2. PyMuPDF stamps the logo, the right-header title/address block, and the footer
     (date | company | Page N of M) onto EVERY page afterwards.

Step 2 is what replaces `&G`, and it is more predictable than Excel's header renderer --
exact point positioning instead of Excel's internal header layout.

Verified against the known-good Windows output for 260093 (620 W 52nd Rock Removal v4):
same page count, same portrait letter geometry, logo present on every page.

Usage:
    python export_pdf.py --xlsx <in.xlsx> --out <out.pdf> \
        --logo ../assets/OD_logo.png \
        --title "Estimate: 260105 620 West 52nd Street" \
        --address "620-622 West 52nd Street, New York, NY 10019" \
        --date "07/29/2026"

    # footer company line defaults to O+D Builders; override with --footer

Requires: PyMuPDF (fitz), LibreOffice (`soffice` on PATH, or /Applications/LibreOffice.app)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import fitz  # PyMuPDF
import openpyxl
from openpyxl.worksheet.properties import PageSetupProperties

DEFAULT_FOOTER = ("O+D Builders | 152 West 25th St. Suite 801, "
                  "New York, NY 10001 | (212) 929-8320")

# Geometry in points (1/72"). Matches the Windows original's header/footer margins:
# header 0.3", top margin 1.0", bottom 0.75", footer 0.3", left/right 0.7".
LOGO_X, LOGO_Y = 50.0, 22.0
LOGO_W, LOGO_H = 145.0, 54.0      # same as $ps.LeftHeaderPicture Width/Height
RIGHT_MARGIN = 50.0
FOOTER_Y = 756.0                  # ~0.5" up from an 11" page bottom
TITLE_SIZE, ADDR_SIZE, FOOT_SIZE = 11.0, 10.0, 8.5
GRAY = (0.35, 0.35, 0.35)
BLACK = (0.0, 0.0, 0.0)


def normalize_page_setup(xlsx_in, xlsx_out, include_hidden=False):
    """Write explicit page setup so LibreOffice paginates the way Excel did.

    THIS STEP IS LOAD-BEARING, do not skip it. Excel stores `fitToWidth` as absent
    when you set FitToPagesWide via COM, and often leaves a stale `scale` alongside
    `fitToPage=True`. Excel ignores the stale scale; LibreOffice honors it and
    over-shrinks, squeezing a two-page tab onto one page and **clipping the right-hand
    money columns off the sheet entirely**.

    Measured on 260093 v4 before this fix: 6 pages instead of 10, and 27 of 37 dollar
    figures silently missing from the PDF. No error, no `###` markers -- just absent
    numbers on a cost document. Explicitly setting fitToWidth=1 / fitToHeight=0 and
    clearing `scale` restores Excel's pagination.
    """
    wb = openpyxl.load_workbook(xlsx_in)   # keep formulas + their cached values

    # A hidden sheet is silently omitted from the PDF by LibreOffice AND by Excel.
    # On 260093 v4 the Takeoff tab was hidden, so the deliverable lost an entire
    # section (2 pages, including the site-area and tonnage quantities) with no error.
    # Never let that pass unannounced.
    hidden = [ws.title for ws in wb.worksheets if ws.sheet_state != "visible"]
    if hidden:
        if include_hidden:
            for ws in wb.worksheets:
                ws.sheet_state = "visible"
            print(f"  --include-hidden: un-hiding {len(hidden)} sheet(s) for this "
                  f"export only: {', '.join(hidden)}")
        else:
            print(f"  WARNING: {len(hidden)} sheet(s) are HIDDEN and will NOT appear "
                  f"in the PDF: {', '.join(hidden)}")
            print("           If they belong in the deliverable, re-run with "
                  "--include-hidden.")

    for ws in wb.worksheets:
        ps = ws.page_setup
        ps.orientation = "portrait"
        ps.paperSize = "1"                 # letter
        ps.fitToWidth = 1                  # the "Fit All Columns on One Page" preset
        ps.fitToHeight = 0                 # as many pages tall as needed
        ps.scale = None                    # MUST clear -- conflicts with fitToPage
        if ws.sheet_properties.pageSetUpPr is None:
            ws.sheet_properties.pageSetUpPr = PageSetupProperties()
        ws.sheet_properties.pageSetUpPr.fitToPage = True

        m = ws.page_margins
        m.left = m.right = 0.7
        m.top = 1.25                       # logo occupies 0.3"-1.06"; keep sheet
                                           # content clear of it (1.0" overlapped the
                                           # workbook's own O+D BUILDERS band)
        m.bottom = 0.75                    # room for the stamped footer
        m.header = m.footer = 0.3

        ws.print_options.horizontalCentered = True
        ws.print_options.verticalCentered = False

        # Clear any header/footer already stored in the workbook. If this xlsx was
        # previously exported on Windows, export_pdf.ps1 wrote Excel header/footer
        # strings into it. LibreOffice renders those too, so we would get TWO stacked
        # header blocks plus a literal `_x000a_` where Excel encoded its newline.
        # Our stamps are the single source of branding.
        for hf in (ws.oddHeader, ws.oddFooter, ws.evenHeader, ws.evenFooter,
                   ws.firstHeader, ws.firstFooter):
            for part in (hf.left, hf.center, hf.right):
                part.text = None
    wb.save(xlsx_out)
    return xlsx_out


def find_soffice():
    for cand in ("soffice", "libreoffice"):
        p = shutil.which(cand)
        if p:
            return p
    mac = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.exists(mac):
        return mac
    return None


def xlsx_to_pdf(soffice, xlsx, workdir):
    """Convert with an isolated LibreOffice profile so a running GUI copy can't block us."""
    profile = os.path.join(workdir, "lo_profile")
    cmd = [
        soffice, "--headless", "--norestore", "--invisible",
        f"-env:UserInstallation=file://{profile}",
        "--convert-to", "pdf:calc_pdf_Export",
        "--outdir", workdir, xlsx,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    produced = os.path.join(
        workdir, os.path.splitext(os.path.basename(xlsx))[0] + ".pdf")
    if not os.path.exists(produced):
        raise SystemExit(
            "ERROR: LibreOffice produced no PDF.\n"
            f"  cmd: {' '.join(cmd)}\n"
            f"  stdout: {res.stdout.strip()}\n"
            f"  stderr: {res.stderr.strip()}\n"
            "  If a LibreOffice GUI window is open, close it and retry."
        )
    return produced


def fit_text(page, rect, text, fontname, fontsize, color, align, label, fontfile=None):
    """insert_textbox that cannot fail silently.

    PyMuPDF's insert_textbox returns a NEGATIVE number when the text does not fit the
    rect -- and renders NOTHING. No exception. The first version of this script lost the
    entire right-header block on every page that way: a 51-character title at 11pt bold
    needs ~311pt and the box was 256pt, so the header simply never appeared and the PDF
    looked plausible. Shrink until it fits, and shout if it still does not.
    """
    size = fontsize
    while size >= 5.5:
        kw = {"fontfile": fontfile} if fontfile else {}
        if page.insert_textbox(rect, text, fontname=fontname, fontsize=size,
                               color=color, align=align, **kw) >= 0:
            return size
        size -= 0.5
    print(f"  WARNING: '{label}' did not fit its box on page {page.number + 1} "
          f"even at 5.5pt -- it is NOT rendered. Shorten the text or widen the box.")
    return None


def stamp(pdf_in, pdf_out, logo, title, address, footer, date_str,
          font_regular=None, font_bold=None):
    doc = fitz.open(pdf_in)
    n = len(doc)
    have_logo = bool(logo) and os.path.exists(logo)

    logo_xref = 0
    for i, page in enumerate(doc, start=1):
        pw = page.rect.width
        right_edge = pw - RIGHT_MARGIN

        if have_logo:
            rect = fitz.Rect(LOGO_X, LOGO_Y, LOGO_X + LOGO_W, LOGO_Y + LOGO_H)
            # Embed the bitmap once, then reference the same XObject on every page.
            # Passing filename= each time re-embeds it per page, bloating the file and
            # listing N copies in each page's resources.
            if logo_xref:
                page.insert_image(rect, xref=logo_xref)
            else:
                page.insert_image(rect, filename=logo, keep_proportion=True)
                imgs = page.get_images(full=True)
                if imgs:
                    logo_xref = imgs[0][0]

        # Right header block: bold title over italic address, right-aligned.
        # Box starts just right of the logo so long project titles have room.
        hdr_left = LOGO_X + LOGO_W + 12
        # Embed the brand font when supplied; fall back to base-14 Helvetica otherwise.
        nb, fb = ("ttcpb", font_bold) if font_bold else ("hebo", None)
        nr, fr = ("ttcpr", font_regular) if font_regular else ("heit", None)
        nl, flr = ("ttcpr", font_regular) if font_regular else ("helv", None)
        if title:
            fit_text(page, fitz.Rect(hdr_left, LOGO_Y + 2, right_edge, LOGO_Y + 26),
                     title, nb, TITLE_SIZE, BLACK,
                     fitz.TEXT_ALIGN_RIGHT, "title", fontfile=fb)
        if address:
            fit_text(page, fitz.Rect(hdr_left, LOGO_Y + 27, right_edge, LOGO_Y + 48),
                     address, nr, ADDR_SIZE, GRAY,
                     fitz.TEXT_ALIGN_RIGHT, "address", fontfile=fr)

        # Footer on TWO lines. The company line is ~95 characters; sharing one line
        # with the date and page number left it too narrow and it wrapped mid-address.
        # Line 1: date (left) | Page N of M (right). Line 2: company, full width.
        if date_str:
            fit_text(page, fitz.Rect(LOGO_X, FOOTER_Y, LOGO_X + 150, FOOTER_Y + 13),
                     date_str, nl, FOOT_SIZE, GRAY,
                     fitz.TEXT_ALIGN_LEFT, "footer date", fontfile=flr)
        fit_text(page, fitz.Rect(right_edge - 150, FOOTER_Y, right_edge, FOOTER_Y + 13),
                 f"Page {i} of {n}", nl, FOOT_SIZE, GRAY,
                 fitz.TEXT_ALIGN_RIGHT, "page number", fontfile=flr)
        if footer:
            fit_text(page, fitz.Rect(LOGO_X, FOOTER_Y + 13, right_edge, FOOTER_Y + 28),
                     footer, nl, FOOT_SIZE, GRAY,
                     fitz.TEXT_ALIGN_CENTER, "footer company", fontfile=flr)

    doc.save(pdf_out, garbage=4, deflate=True)
    doc.close()
    return n


def main():
    ap = argparse.ArgumentParser(description="xlsx -> branded PDF (cross-platform)")
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--logo", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--address", default="")
    ap.add_argument("--footer", default=DEFAULT_FOOTER)
    ap.add_argument("--date", dest="date_str", default="")
    ap.add_argument("--font-regular", default="",
                    help="Path to a .ttf/.otf used for the stamped address and footer.")
    ap.add_argument("--font-bold", default="",
                    help="Path to a .ttf/.otf used for the stamped title.")
    ap.add_argument("--include-hidden", action="store_true",
                    help="Un-hide hidden sheets for this export only. "
                         "The deliverable xlsx is never modified.")
    args = ap.parse_args()

    if not os.path.exists(args.xlsx):
        raise SystemExit(f"ERROR: xlsx not found: {args.xlsx}")

    soffice = find_soffice()
    if not soffice:
        raise SystemExit(
            "ERROR: LibreOffice not found. Install with `brew install --cask libreoffice`, "
            "or run the Windows export_pdf.ps1 path instead."
        )

    if args.logo and not os.path.exists(args.logo):
        print(f"WARNING: logo not found at {args.logo} -- PDF will have no logo.")

    # Unlike Excel COM on Windows, writing into a Dropbox path works fine here. The
    # temp dir is for LibreOffice's own scratch, not a Dropbox workaround.
    with tempfile.TemporaryDirectory() as workdir:
        # Normalize into a temp copy -- never modify the deliverable xlsx the GC edits.
        staged = normalize_page_setup(
            os.path.abspath(args.xlsx), os.path.join(workdir, "staged.xlsx"),
            include_hidden=args.include_hidden)
        raw = xlsx_to_pdf(soffice, staged, workdir)
        for lbl, fp in (("--font-regular", args.font_regular), ("--font-bold", args.font_bold)):
            if fp and not os.path.exists(fp):
                raise SystemExit(f"ERROR: {lbl} not found: {fp}")
        pages = stamp(raw, args.out, args.logo, args.title, args.address,
                      args.footer, args.date_str,
                      font_regular=args.font_regular or None,
                      font_bold=args.font_bold or None)

    size = os.path.getsize(args.out)
    print(f"PDF created: {args.out} ({pages} pages, {size:,} bytes)")
    if not (10 <= pages <= 18):
        print(f"  NOTE: {pages} pages is outside the expected 10-18 range for this "
              f"deliverable -- check for a blank tab or a runaway print area.")


if __name__ == "__main__":
    main()
