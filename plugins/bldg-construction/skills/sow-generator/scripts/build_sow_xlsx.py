#!/usr/bin/env python3
"""Build the SOW workbook, in either output mode.

usage: build_sow_xlsx.py <data.json> <out.xlsx>

One builder, two modes, set by `"mode"` in the data file:

  "scope"       Reference | Scope Item | [Resp.] | gutter | Sub #1..#4
                Zero quantities, zero pricing. What goes out in a bid package
                before anything has been counted.

  "quantified"  Reference | Scope Item | Qty | Unit | Unit Rate | Total
                | [Resp.] | gutter | Sub #1..#4
                Our number and four sub numbers reconciling on the same row.

`"landlord_tenant": true` adds the Resp. column in either mode.

These were two skills until they were merged. One builder is the point: the grid,
the borders, the formulas and the close-out ladder are exactly what drifted last
time, and there is now one copy of each.

See references/workbook-spec.md for the data contract.
A null qty renders "--", shades the row red, and is excluded from every total.
"""
import json, math, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import FormulaRule

W = "FFFFFFFF"; BLACK = "FF000000"; CHAR = "FF3A3A3A"; MED = "FF7A7A7A"
LT = "FFE8E8E8"; VLT = "FFF5F5F5"; RED = "FFFFD6D6"; GREEN = "FFD6F0D6"
FONT = "Calibri"; CUR = '$#,##0.00'
HAIR = Side("thin", color="FFB0B0B0")
MEDS = Side("medium", color=CHAR)
BLKS = Side("medium", color=BLACK)


def columns(mode, lt):
    """The grid, derived from the mode. Nothing downstream hardcodes a column letter."""
    cols = [("ref", "Reference", 16),
            ("scope", "Scope Item", 76 if mode == "scope" else 52)]
    if mode == "quantified":
        cols += [("qty", "Qty", 10), ("unit", "Unit Type", 11),
                 ("rate", "Unit Rate", 13), ("total", "Total", 14)]
    if lt:
        cols += [("resp", "Resp.", 12)]
    cols += [("gut", "", 2.5)]
    cols += [("sub%d" % i, "Sub #%d" % i, 15) for i in (1, 2, 3, 4)]
    return cols


def ch(spec, mn=22, lp=13):
    """Row height that fits wrapped text. NEVER write a flat height -- it kills auto-fit."""
    n = max([1] + [math.ceil(len(str(t)) / c) for t, c in spec if t])
    return max(mn, n * lp)


def paint(ws, r1, c1, r2, c2, edge, inner=HAIR):
    """Border EVERY cell in the range. Excel draws a merged range's edges from all of its
    constituent cells, so bordering only the anchor leaves the box three-quarters open."""
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            cur = ws.cell(r, c).border
            ws.cell(r, c).border = Border(
                left=edge if c == c1 else (inner or cur.left),
                right=edge if c == c2 else (inner or cur.right),
                top=edge if r == r1 else (inner or cur.top),
                bottom=edge if r == r2 else (inner or cur.bottom))


def erow(ws, r, c1, c2, top=None, bottom=None):
    for c in range(c1, c2 + 1):
        b = ws.cell(r, c).border
        ws.cell(r, c).border = Border(left=b.left, right=b.right,
                                      top=top or b.top, bottom=bottom or b.bottom)


def ecol(ws, r1, r2, c, l=None, rt=None):
    for r in range(r1, r2 + 1):
        b = ws.cell(r, c).border
        ws.cell(r, c).border = Border(left=l or b.left, right=rt or b.right,
                                      top=b.top, bottom=b.bottom)


def fill(ws, r, cols, color):
    for c in cols:
        ws.cell(r, c).fill = PatternFill("solid", fgColor=color)


def _text(v):
    """Conflicts and TBD arrived as bare strings in one shape and as dicts in another."""
    if isinstance(v, dict):
        return v.get("reference", ""), v.get("text", "")
    return "", str(v)


def normalize(d):
    """Accept every shape this skill's data has taken, so an old sow_data.json in a job
    folder still builds instead of erroring two years from now.

    Three have existed: `trades[]` with `lines[]` (current), `trades[]` with `items[]`
    (the old Excel builder), and `subdivisions[]` with `line_items[]` (the old sample).
    The header block has been both a nested `project` object and flat keys."""
    p = d.get("project")
    if isinstance(p, dict):
        d["address"] = d.get("address") or p.get("address", "")
        d["date"] = d.get("date") or p.get("date_prepared", "") or p.get("date", "")
        d["prepared_by"] = d.get("prepared_by") or p.get("prepared_by", "")
        d["job"] = d.get("job") or p.get("job", "")
        d["client"] = d.get("client") or p.get("client", "")
        d["project"] = p.get("name", "")
    d.setdefault("project", d.get("project_name", ""))
    d.setdefault("address", d.get("project_address", ""))
    d.setdefault("date", d.get("date_prepared", ""))

    src = d.get("subdivisions") if "subdivisions" in d else None
    if src is None and d.get("trades") and "lines" not in (d["trades"][0] or {}):
        src = d["trades"]
    if src is not None:
        d["trades"] = [{
            "trade": s.get("title", "") or s.get("trade", ""),
            "csi": s.get("csi") or ([s["code"]] if s.get("code") else []),
            "lines": [{"reference": li.get("reference", ""),
                       "scope": li.get("scope_item", "") or li.get("scope", ""),
                       "qty": li.get("qty"), "unit": li.get("unit", ""),
                       "rate": li.get("rate"),
                       "responsibility": li.get("responsibility", ""),
                       "bullets": li.get("bullets") or []}
                      for li in (s.get("line_items") or s.get("items") or [])]
        } for s in src]

    notes = d.get("notes")
    flat = []
    if isinstance(notes, dict):           # {"standard":[...], "drawing_specific":[...]}
        for t in notes.get("standard") or []:
            flat.append({"type": "CLARIFICATION", "item": "Standard", "text": t})
        for t in notes.get("drawing_specific") or []:
            ref, txt = _text(t)
            flat.append({"type": "CLARIFICATION", "item": ref or "Drawing", "text": txt})
    elif isinstance(notes, list):
        flat = list(notes)
    for t in d.get("standard_clarifications") or []:
        flat.append({"type": "CLARIFICATION", "item": "Standard", "text": t})
    for c in d.get("drawing_specific_clarifications") or []:
        ref, txt = _text(c)
        flat.append({"type": "CLARIFICATION", "item": ref or "Drawing", "text": txt})
    d["notes"] = flat
    d["tbd_items"] = d.get("tbd_items") or d.get("tbd") or []
    d["conflicts"] = d.get("conflicts") or []
    return d


def section(ws, r, width_chars, LAST, title, rows, color, M):
    """A full-width block under the ladder: Conflicts, then TBD Items.

    These were named outputs of the scope-only skill and they are the reason a
    contradiction in the drawings reaches a person instead of being silently resolved.
    They travel into both modes unchanged."""
    if not rows:
        return r
    ws.row_dimensions[r].height = 7
    r += 1
    c = ws.cell(r, 1, title)
    c.font = Font(FONT, 12, bold=True, color=W)
    c.alignment = Alignment("left", "center")
    fill(ws, r, range(1, LAST + 1), CHAR)
    ws.row_dimensions[r].height = 20
    M.append((r, 1, r, LAST))
    head = r
    r += 1
    for item in rows:
        ref, txt = _text(item)
        a = ws.cell(r, 1, ref)
        a.font = Font(FONT, 9, color=CHAR)
        a.alignment = Alignment("left", "top", wrap_text=True)
        b = ws.cell(r, 2, txt)
        b.font = Font(FONT, 10)
        b.alignment = Alignment("left", "top", wrap_text=True)
        fill(ws, r, range(1, LAST + 1), color)
        M.append((r, 2, r, LAST))
        ws.row_dimensions[r].height = ch([(txt, width_chars)], mn=20, lp=12)
        r += 1
    paint(ws, head, 1, r - 1, LAST, MEDS, inner=HAIR)
    return r


def build(d, out):
    d = normalize(d)
    mode = d.get("mode", "quantified")
    if mode not in ("scope", "quantified"):
        sys.exit("mode must be 'scope' or 'quantified', got %r" % mode)
    lt = bool(d.get("landlord_tenant"))
    cols = columns(mode, lt)
    X = {k: i + 1 for i, (k, _, _) in enumerate(cols)}
    LAST = len(cols)
    GUT = X["gut"]
    SUBS = [X["sub%d" % i] for i in (1, 2, 3, 4)]
    LEFT = list(range(1, GUT))                 # our side of the gutter
    BOTH = LEFT + SUBS
    priced = mode == "quantified"
    MONEY = ([X["total"]] if priced else []) + SUBS
    SCOPE_W = cols[X["scope"] - 1][2]
    TAIL_W = sum(w for _, _, w in cols[1:GUT - 1]) or SCOPE_W

    wb = Workbook()
    ws = wb.active
    ws.title = "Scope of Work"
    for i, (_, _, w) in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for c in [GUT] + SUBS:
        L = get_column_letter(c)
        ws.column_dimensions[L].outline_level = 1
        ws.column_dimensions[L].hidden = False
    M = []   # merges applied AFTER borders, never before

    ws.cell(1, 1, d["project"]).font = Font(FONT, 18, bold=True)
    ws.row_dimensions[1].height = 28
    M.append((1, 1, 1, LAST))
    ws.cell(2, 1, d.get("address", "")).font = Font(FONT, 11)
    M.append((2, 1, 2, LAST))
    ws.cell(3, 1, "Date: %s" % d.get("date", "")).font = Font(FONT, 10)
    M.append((3, 1, 3, 1))
    ws.cell(3, 2, "Prepared By: %s   |   Job %s   |   Client: %s" % (
        d.get("prepared_by", ""), d.get("job", ""), d.get("client", ""))).font = Font(FONT, 10)
    M.append((3, 2, 3, LAST))
    ws.row_dimensions[4].height = 5

    legend = ("F/I = Furnish and Install  |  F/O = Furnish Only  |  I/O = Install Only  |  "
              "Remove = Demolition  |  Provide = Services")
    if priced:
        legend += "  |  LS = Lump Sum"
    if lt:
        legend += "  |  Resp. = Landlord / Tenant / Both"
    x = ws.cell(5, 1, legend)
    x.font = Font(FONT, 9, italic=True, color=CHAR)
    fill(ws, 5, range(1, LAST + 1), VLT)
    ws.row_dimensions[5].height = 16
    M.append((5, 1, 5, LAST))

    if priced:
        banner = ("Lines shown without a quantity require a plan count and are not included "
                  "in any total. See Notes & Clarifications.")
        bfill = RED
    else:
        banner = ("This scope carries no quantities and no pricing. Subcontractor columns "
                  "are for bid entry.")
        bfill = VLT
    x = ws.cell(6, 1, banner)
    x.font = Font(FONT, 9, bold=True, color=CHAR)
    fill(ws, 6, range(1, LAST + 1), bfill)
    ws.row_dimensions[6].height = 18
    M.append((6, 1, 6, LAST))
    erow(ws, 5, 1, LAST, top=MEDS)
    erow(ws, 6, 1, LAST, bottom=MEDS)    # rules only, no verticals
    ws.row_dimensions[7].height = 7

    HDR = 8
    for col, (_, title, _) in enumerate(cols, 1):
        c = ws.cell(HDR, col, title)
        c.font = Font(FONT, 11, bold=True, color=W)
        c.fill = PatternFill("solid", fgColor=CHAR)
        c.alignment = Alignment("left" if col <= 2 else "center", "center")
    ws.row_dimensions[HDR].height = 22
    paint(ws, HDR, 1, HDR, LAST, BLKS, inner=Side("thin", color=CHAR))
    ws.freeze_panes = "A%d" % (HDR + 1)

    r = HDR + 1
    trade_rows = []
    for tr in d["trades"]:
        ws.row_dimensions[r].height = 7
        r += 1
        h1, h2 = r, r + 1
        csi = ", ".join(tr.get("csi", []))
        c = ws.cell(h1, 1, "%s%s" % (tr["trade"].upper(), ("  --  CSI " + csi) if csi else ""))
        c.font = Font(FONT, 11, bold=True, color=W)
        c.alignment = Alignment("left", "center")
        for rr in (h1, h2):
            fill(ws, rr, LEFT, MED)
        M.append((h1, 1, h2, GUT - 1))
        for i, col in enumerate(SUBS, 1):
            a = ws.cell(h1, col, "Sub #%d" % i)
            a.font = Font(FONT, 10, bold=True)
            a.fill = PatternFill("solid", fgColor=LT)
            a.alignment = Alignment("center", "center")
            b = ws.cell(h2, col)
            b.number_format = CUR
            b.fill = PatternFill("solid", fgColor=VLT)
            b.alignment = Alignment("center", "center")
        ws.row_dimensions[h1].height = 19
        ws.row_dimensions[h2].height = 19

        r = h2 + 1
        first = r
        band = 0
        for ln in tr["lines"]:
            q = ln.get("qty") if priced else None
            bullets = ln.get("bullets") or []
            fg = (RED if (priced and q is None) else (VLT if band % 2 else None))
            band += 1
            ref = ws.cell(r, X["ref"], ln.get("reference", ""))
            ref.font = Font(FONT, 9, color=CHAR)
            ref.alignment = Alignment("left", "center", wrap_text=True)
            s = ws.cell(r, X["scope"], ln["scope"])
            s.font = Font(FONT, 10, bold=bool(bullets))
            s.alignment = Alignment("left", "center", wrap_text=True)
            if priced:
                qa = ws.cell(r, X["qty"], q if q is not None else "--")
                if q is not None:
                    qa.number_format = '#,##0.00'
                qa.alignment = Alignment("right", "center")
                qa.font = Font(FONT, 10, bold=True)
                u = ws.cell(r, X["unit"], ln.get("unit", ""))
                u.alignment = Alignment("center", "center")
                u.font = Font(FONT, 10)
                ur = ws.cell(r, X["rate"], ln.get("rate"))
                ur.number_format = CUR
                ur.alignment = Alignment("right", "center")
                QL = get_column_letter(X["qty"]); RL = get_column_letter(X["rate"])
                tot = ws.cell(r, X["total"],
                              '=IF(AND(ISNUMBER($%s%d),ISNUMBER($%s%d)),$%s%d*$%s%d,"")'
                              % (QL, r, RL, r, QL, r, RL, r))
                tot.number_format = CUR
                tot.font = Font(FONT, 10, bold=True)
                tot.alignment = Alignment("right", "center")
            if lt:
                rp = ws.cell(r, X["resp"], ln.get("responsibility", ""))
                rp.font = Font(FONT, 9, bold=True)
                rp.alignment = Alignment("center", "center")
            for col in SUBS:
                p = ws.cell(r, col)
                p.number_format = CUR
                p.alignment = Alignment("right", "center")
            if fg:
                fill(ws, r, BOTH, fg)
            ws.row_dimensions[r].height = ch([(ln["scope"], SCOPE_W)])
            r += 1
            for b in bullets:
                bc = ws.cell(r, X["scope"], "- " + b)
                bc.font = Font(FONT, 9, italic=True, color=CHAR)
                bc.alignment = Alignment("left", "center", wrap_text=True, indent=2)
                ws.row_dimensions[r].height = ch([(b, SCOPE_W - 6)], mn=14, lp=11)
                r += 1

        last = r - 1
        tot_r = r
        LADDER_END = X["unit"] if priced else GUT - 1
        c = ws.cell(tot_r, 1, "TRADE TOTAL")
        c.font = Font(FONT, 10, bold=True)
        c.alignment = Alignment("left", "center")
        M.append((tot_r, 1, tot_r, LADDER_END))
        if priced:
            TL = get_column_letter(X["total"])
            te = ws.cell(tot_r, X["total"],
                         '=IF(SUM(%s%d:%s%d)=0,"-",SUM(%s%d:%s%d))'
                         % (TL, first, TL, last, TL, first, TL, last))
            te.number_format = CUR
            te.font = Font(FONT, 10, bold=True)
            te.alignment = Alignment("right", "center")
        for col in SUBS:
            L = get_column_letter(col)
            # sums from the LUMP-SUM row down, so lump-sum and itemised bidders both roll up
            p = ws.cell(tot_r, col, '=IF(SUM(%s%d:%s%d)=0,"-",SUM(%s%d:%s%d))'
                        % (L, h2, L, last, L, h2, L, last))
            p.number_format = CUR
            p.font = Font(FONT, 10, bold=True)
            p.alignment = Alignment("right", "center")
        fill(ws, tot_r, BOTH, LT)
        ws.row_dimensions[tot_r].height = 19
        paint(ws, h1, 1, tot_r, LAST, MEDS, inner=HAIR)
        erow(ws, h2, 1, LAST, bottom=MEDS)
        erow(ws, tot_r, 1, LAST, top=MEDS)
        ecol(ws, h1, tot_r, GUT, l=MEDS, rt=MEDS)
        ecol(ws, h1, tot_r, GUT + 1, l=MEDS)
        trade_rows.append((tr["trade"], csi, tot_r))
        r = tot_r + 1

    # ---- SUBTOTAL / markup ladder / TOTAL ----
    LADDER_END = X["unit"] if priced else GUT - 1
    ws.row_dimensions[r].height = 7
    r += 1
    r_sub = r
    c = ws.cell(r_sub, 1, "SUBTOTAL")
    c.font = Font(FONT, 11, bold=True)
    c.alignment = Alignment("left", "center")
    M.append((r_sub, 1, r_sub, LADDER_END))
    for col in MONEY:
        L = get_column_letter(col)
        ref = "+".join("%s%d" % (L, tr) for _, _, tr in trade_rows) or "0"
        cc = ws.cell(r_sub, col, "=%s" % ref)
        cc.number_format = CUR
        cc.font = Font(FONT, 11, bold=True)
        cc.alignment = Alignment("right", "center")
    fill(ws, r_sub, BOTH, LT)
    ws.row_dimensions[r_sub].height = 20
    r += 1

    # THE LADDER IS PRICED-MODE ONLY. In scope mode there is no money of ours to mark
    # up, and the only column free to hold a percentage is Scope Item -- which would put
    # a markup rate under a text heading and mirror that mistake onto the SOV. A
    # scope-only document going out to subs carries no markup at all, which is what the
    # scope-only skill did before the merge. SUBTOTAL across the sub columns stays, so
    # the estimator can still level.
    PCT = X["rate"] if priced else None
    PL = get_column_letter(PCT) if PCT else None
    r_m1 = r
    n_mk = int(d.get("markup_rows", 6)) if priced else 0
    labels = d.get("markup_labels") or []
    for i in range(n_mk):
        rr = r_m1 + i
        lb = ws.cell(rr, 1, labels[i] if i < len(labels) else None)
        lb.font = Font(FONT, 10)
        lb.alignment = Alignment("left", "center")
        lb.fill = PatternFill("solid", fgColor=VLT)
        if PCT > 1:
            M.append((rr, 1, rr, PCT - 1))
        pc = ws.cell(rr, PCT)
        pc.number_format = '0.00%'
        pc.alignment = Alignment("right", "center")
        pc.font = Font(FONT, 10, bold=True)
        pc.fill = PatternFill("solid", fgColor=VLT)
        for col in MONEY:
            L = get_column_letter(col)
            base = ("%s%d" % (L, r_sub) if i == 0 else
                    "%s%d+SUM(%s%d:%s%d)" % (L, r_sub, L, r_m1, L, rr - 1))
            cc = ws.cell(rr, col, '=IF($%s%d="","",ROUND((%s)*$%s%d,2))' % (PL, rr, base, PL, rr))
            cc.number_format = CUR
            cc.alignment = Alignment("right", "center")
        ws.row_dimensions[rr].height = 18
    r = r_m1 + n_mk
    r_tot = r if n_mk else r_sub
    if n_mk:
        c = ws.cell(r_tot, 1, "TOTAL")
        c.font = Font(FONT, 12, bold=True)
        c.alignment = Alignment("left", "center")
        M.append((r_tot, 1, r_tot, LADDER_END))
        for col in MONEY:
            L = get_column_letter(col)
            cc = ws.cell(r_tot, col, '=ROUND(%s%d+SUM(%s%d:%s%d),2)'
                         % (L, r_sub, L, r_m1, L, r_m1 + n_mk - 1))
            cc.number_format = CUR
            cc.font = Font(FONT, 12, bold=True)
            cc.alignment = Alignment("right", "center")
        fill(ws, r_tot, BOTH, LT)
        ws.row_dimensions[r_tot].height = 24
    paint(ws, r_sub, 1, r_tot, LAST, MEDS, inner=HAIR)
    erow(ws, r_sub, 1, LAST, bottom=MEDS)
    erow(ws, r_tot, 1, LAST, top=MEDS)
    ecol(ws, r_sub, r_tot, GUT, l=MEDS, rt=MEDS)
    ecol(ws, r_sub, r_tot, GUT + 1, l=MEDS)
    r = r_tot + 1

    # Conflicts and TBD: never silently resolved, always on the face of the document.
    r = section(ws, r, TAIL_W, LAST, "CONFLICTS", d["conflicts"], RED, M)
    r = section(ws, r, TAIL_W, LAST, "TBD ITEMS", d["tbd_items"], VLT, M)

    for m in M:
        ws.merge_cells(start_row=m[0], start_column=m[1], end_row=m[2], end_column=m[3])
    ws.print_area = "A1:%s%d" % (get_column_letter(LAST), r - 1)
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    ws.print_title_rows = "1:%d" % HDR
    ws.oddHeader.left.text = "%s -- Scope of Work" % d["project"]
    ws.oddHeader.right.text = "Page &P of &N"
    ws.oddFooter.center.text = d.get("prepared_by", "")
    ws.oddFooter.right.text = d.get("date", "")
    ws.sheet_properties.outlinePr.summaryRight = False
    ws.sheet_view.showGridLines = False

    # ---- SOV: trade roll-up, our total against the sub bids, low bid highlighted ----
    sv = wb.create_sheet("SOV")
    heads = ["Trade", "CSI"] + (["Our Total"] if priced else []) + \
            ["Sub #1", "Sub #2", "Sub #3", "Sub #4", "Low Bid", "Low Bidder"] + \
            (["Low Bid vs Ours"] if priced else [])
    NS = len(heads)
    SW = [30, 24] + [15] * (NS - 3) + [16]
    for i, w in enumerate(SW, 1):
        sv.column_dimensions[get_column_letter(i)].width = w
    NSL = get_column_letter(NS)
    C_OURS = 3 if priced else None
    C_SUB1 = 4 if priced else 3
    C_SUB4 = C_SUB1 + 3
    C_LOW = C_SUB4 + 1
    C_WHO = C_LOW + 1
    C_DELTA = C_WHO + 1 if priced else None
    S1 = get_column_letter(C_SUB1); S4 = get_column_letter(C_SUB4)
    LOWL = get_column_letter(C_LOW)

    sv.cell(1, 1, "%s -- Schedule of Values" % d["project"]).font = Font(FONT, 16, bold=True)
    sv.row_dimensions[1].height = 24
    sv.merge_cells("A1:%s1" % NSL)
    x = sv.cell(2, 1, "Job %s  |  %s  |  %s  |  %s" % (d.get("job", ""), d.get("address", ""),
                                                       d.get("prepared_by", ""), d.get("date", "")))
    x.font = Font(FONT, 10, italic=True)
    fill(sv, 2, range(1, NS + 1), VLT)
    sv.row_dimensions[2].height = 18
    sv.merge_cells("A2:%s2" % NSL)
    x = sv.cell(3, 1, "Sub columns are linked to the Scope of Work sheet. Markup percentages "
                      "are entered once on Scope of Work and mirrored here. The low bid in "
                      "each row is highlighted.")
    x.font = Font(FONT, 9, italic=True, color=CHAR)
    sv.merge_cells("A3:%s3" % NSL)
    fill(sv, 3, range(1, NS + 1), VLT)
    sv.row_dimensions[3].height = 16
    erow(sv, 2, 1, NS, top=MEDS)
    erow(sv, 3, 1, NS, bottom=MEDS)
    shr = 5
    for col, t in enumerate(heads, 1):
        c = sv.cell(shr, col, t)
        c.font = Font(FONT, 11, bold=True, color=W)
        c.fill = PatternFill("solid", fgColor=CHAR)
        c.alignment = Alignment("left" if col <= 2 else "center", "center")
    sv.row_dimensions[shr].height = 22
    paint(sv, shr, 1, shr, NS, BLKS, inner=Side("thin", color=CHAR))
    sv.freeze_panes = "A%d" % (shr + 1)

    rr = shr + 1
    first_sov = rr
    for name, csi, tr_row in trade_rows:
        sv.cell(rr, 1, name).font = Font(FONT, 10, bold=True)
        sv.cell(rr, 1).alignment = Alignment("left", "center", wrap_text=True)
        sv.cell(rr, 2, csi).font = Font(FONT, 9, color=CHAR)
        sv.cell(rr, 2).alignment = Alignment("left", "center", wrap_text=True)
        if priced:
            c = sv.cell(rr, C_OURS, "='Scope of Work'!%s%d"
                        % (get_column_letter(X["total"]), tr_row))
            c.number_format = CUR
            c.font = Font(FONT, 10, bold=True)
        for i, col in enumerate(SUBS):
            L = get_column_letter(col)
            c = sv.cell(rr, C_SUB1 + i,
                        "=IF('Scope of Work'!%s%d=\"-\",\"\",'Scope of Work'!%s%d)"
                        % (L, tr_row, L, tr_row))
            c.number_format = CUR
        lo = sv.cell(rr, C_LOW, '=IF(COUNT(%s%d:%s%d)=0,"",MIN(%s%d:%s%d))'
                     % (S1, rr, S4, rr, S1, rr, S4, rr))
        lo.number_format = CUR
        lo.font = Font(FONT, 10, bold=True)
        sv.cell(rr, C_WHO, '=IF(%s%d="","",INDEX($%s$%d:$%s$%d,MATCH(%s%d,%s%d:%s%d,0)))'
                % (LOWL, rr, S1, shr, S4, shr, LOWL, rr, S1, rr, S4, rr))
        if priced:
            OL = get_column_letter(C_OURS)
            dl = sv.cell(rr, C_DELTA, '=IF(OR(%s%d="",N(%s%d)=0),"",%s%d-%s%d)'
                         % (LOWL, rr, OL, rr, LOWL, rr, OL, rr))
            dl.number_format = CUR
        for col in range(3, NS + 1):
            sv.cell(rr, col).alignment = Alignment("center" if col == C_WHO else "right", "center")
        sv.row_dimensions[rr].height = ch([(name, 30), (csi, 24)], mn=20, lp=13)
        rr += 1
    last_sov = rr - 1
    sv.conditional_formatting.add(
        "%s%d:%s%d" % (S1, first_sov, S4, last_sov),
        FormulaRule(formula=['AND(ISNUMBER(%s%d),COUNT($%s%d:$%s%d)>0,%s%d=MIN($%s%d:$%s%d))'
                             % (S1, first_sov, S1, first_sov, S4, first_sov,
                                S1, first_sov, S1, first_sov, S4, first_sov)],
                    fill=PatternFill("solid", fgColor=GREEN), font=Font(bold=True)))

    SUM_END = C_LOW
    s_sub = rr
    c = sv.cell(s_sub, 1, "SUBTOTAL")
    c.font = Font(FONT, 11, bold=True)
    sv.merge_cells(start_row=s_sub, start_column=1, end_row=s_sub, end_column=2)
    for col in range(3, SUM_END + 1):
        L = get_column_letter(col)
        cc = sv.cell(s_sub, col, '=IF(SUM(%s%d:%s%d)=0,"",SUM(%s%d:%s%d))'
                     % (L, first_sov, L, last_sov, L, first_sov, L, last_sov))
        cc.number_format = CUR
        cc.font = Font(FONT, 11, bold=True)
        cc.alignment = Alignment("right", "center")
    fill(sv, s_sub, range(1, NS + 1), LT)
    sv.row_dimensions[s_sub].height = 20

    s_m1 = s_sub + 1
    for i in range(n_mk):
        rw = s_m1 + i
        sv.cell(rw, 1, "=IF('Scope of Work'!A%d=\"\",\"\",'Scope of Work'!A%d)"
                % (r_m1 + i, r_m1 + i)).font = Font(FONT, 10)
        c = sv.cell(rw, 2, "=IF('Scope of Work'!%s%d=\"\",\"\",'Scope of Work'!%s%d)"
                    % (PL, r_m1 + i, PL, r_m1 + i))
        c.number_format = '0.00%'
        c.alignment = Alignment("right", "center")
        c.font = Font(FONT, 10, bold=True)
        for col in range(3, SUM_END + 1):
            L = get_column_letter(col)
            base = ("%s%d" % (L, s_sub) if i == 0 else
                    "%s%d+SUM(%s%d:%s%d)" % (L, s_sub, L, s_m1, L, rw - 1))
            cc = sv.cell(rw, col, '=IF(OR($B%d="",N(%s%d)=0),"",ROUND((%s)*$B%d,2))'
                         % (rw, L, s_sub, base, rw))
            cc.number_format = CUR
            cc.alignment = Alignment("right", "center")
        fill(sv, rw, range(1, NS + 1), VLT)
        sv.row_dimensions[rw].height = 18
    s_tot = s_m1 + n_mk if n_mk else s_sub
    if n_mk:
        c = sv.cell(s_tot, 1, "TOTAL")
        c.font = Font(FONT, 12, bold=True)
        sv.merge_cells(start_row=s_tot, start_column=1, end_row=s_tot, end_column=2)
        for col in range(3, SUM_END + 1):
            L = get_column_letter(col)
            cc = sv.cell(s_tot, col, '=IF(N(%s%d)=0,"",ROUND(%s%d+SUM(%s%d:%s%d),2))'
                         % (L, s_sub, L, s_sub, L, s_m1, L, s_m1 + n_mk - 1))
            cc.number_format = CUR
            cc.font = Font(FONT, 12, bold=True)
            cc.alignment = Alignment("right", "center")
        fill(sv, s_tot, range(1, NS + 1), LT)
        sv.row_dimensions[s_tot].height = 24
    paint(sv, first_sov, 1, s_tot, NS, MEDS, inner=HAIR)
    erow(sv, last_sov, 1, NS, bottom=MEDS)
    erow(sv, s_tot, 1, NS, top=MEDS)
    sv.page_setup.orientation = "landscape"
    sv.page_setup.fitToWidth = 1
    sv.page_setup.fitToHeight = 0
    sv.sheet_properties.pageSetUpPr.fitToPage = True
    sv.print_title_rows = "1:%d" % shr
    sv.sheet_view.showGridLines = False

    # ---- Notes & Clarifications (client-facing) ----
    n = wb.create_sheet("Notes & Clarifications")
    for col, w in zip("ABC", [16, 34, 104]):
        n.column_dimensions[col].width = w
    n.cell(1, 1, "%s -- Notes & Clarifications" % d["project"]).font = Font(FONT, 16, bold=True)
    n.row_dimensions[1].height = 24
    n.merge_cells("A1:C1")
    x = n.cell(2, 1, "Job %s  |  %s  |  %s  |  %s" % (d.get("job", ""), d.get("address", ""),
                                                      d.get("prepared_by", ""), d.get("date", "")))
    x.font = Font(FONT, 10, italic=True)
    fill(n, 2, range(1, 4), VLT)
    n.row_dimensions[2].height = 18
    n.merge_cells("A2:C2")
    erow(n, 2, 1, 3, top=MEDS, bottom=MEDS)
    hr = 4
    for col, t in enumerate(["Type", "Item", "Clarification"], 1):
        c = n.cell(hr, col, t)
        c.font = Font(FONT, 11, bold=True, color=W)
        c.fill = PatternFill("solid", fgColor=CHAR)
        c.alignment = Alignment("left", "center")
    n.row_dimensions[hr].height = 20
    paint(n, hr, 1, hr, 3, BLKS, inner=Side("thin", color=CHAR))
    n.freeze_panes = "A5"
    rr = hr + 1
    for nt in d["notes"]:
        for col, v in enumerate([nt.get("type", ""), nt.get("item", ""), nt.get("text", "")], 1):
            c = n.cell(rr, col, v)
            c.font = Font(FONT, 10, bold=(col == 1))
            c.alignment = Alignment("left", "top", wrap_text=True)
            c.fill = PatternFill("solid", fgColor=(RED if nt.get("type") == "EXCLUSION" else VLT))
        n.row_dimensions[rr].height = ch([(nt.get("item", ""), 34), (nt.get("text", ""), 104)],
                                         mn=26, lp=13)
        rr += 1
    if rr > hr + 1:
        paint(n, hr + 1, 1, rr - 1, 3, MEDS, inner=HAIR)
    n.page_setup.orientation = "landscape"
    n.page_setup.fitToWidth = 1
    n.page_setup.fitToHeight = 0
    n.sheet_properties.pageSetUpPr.fitToPage = True
    n.print_title_rows = "1:%d" % hr
    n.sheet_view.showGridLines = False

    # ---- Quantity Basis (internal, hidden -- hidden is not removed; say so on handover) ----
    basis = d.get("basis") or []
    if basis:
        h = wb.create_sheet("Quantity Basis")
        for col, w in zip("ABCDEF", [22, 10, 54, 12, 8, 70]):
            h.column_dimensions[col].width = w
        h.cell(1, 1, "Internal -- quantity basis by line").font = Font(FONT, 14, bold=True)
        h.merge_cells("A1:F1")
        hr2 = 3
        for col, t in enumerate(["Trade", "CSI", "Scope Item", "Qty", "Unit", "Basis"], 1):
            c = h.cell(hr2, col, t)
            c.font = Font(FONT, 11, bold=True, color=W)
            c.fill = PatternFill("solid", fgColor=CHAR)
        h.row_dimensions[hr2].height = 20
        h.freeze_panes = "A4"
        rr = hr2 + 1
        for b in basis:
            q = b.get("qty")
            for col, v in enumerate([b.get("trade", ""), b.get("csi", ""), b.get("scope", ""),
                                     (q if q is not None else "--"), b.get("unit", ""),
                                     b.get("basis", "")], 1):
                c = h.cell(rr, col, v)
                c.font = Font(FONT, 10)
                c.alignment = Alignment("left", "top", wrap_text=True)
                c.fill = PatternFill("solid", fgColor=(RED if q is None else VLT))
            h.row_dimensions[rr].height = ch([(b.get("scope", ""), 54), (b.get("basis", ""), 70)],
                                             mn=24, lp=13)
            rr += 1
        paint(h, hr2, 1, rr - 1, 6, MEDS, inner=HAIR)
        h.sheet_view.showGridLines = False
        h.sheet_state = "hidden"

    wb.save(out)
    nl = sum(len(t["lines"]) for t in d["trades"])
    nq = sum(1 for t in d["trades"] for l in t["lines"] if l.get("qty") is None) if priced else 0
    nu = sum(1 for t in d["trades"] for l in t["lines"]
             if str(l.get("reference", "")).strip().upper() == "[UNVERIFIED]")
    print("wrote %s | mode %s%s | trades %d | lines %d | no-quantity %d | unverified %d | "
          "conflicts %d | tbd %d | notes %d"
          % (out, mode, " +landlord/tenant" if lt else "", len(d["trades"]), nl, nq, nu,
             len(d["conflicts"]), len(d["tbd_items"]), len(d["notes"])))


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
