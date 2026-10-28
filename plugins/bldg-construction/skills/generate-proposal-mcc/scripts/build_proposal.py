#!/usr/bin/env python3
"""Fill template.html with proposal data + embedded brand fonts.

Usage: python3 build_proposal.py data.json out.html

data.json keys:
  proposal_no, date_long, project_name, project_location,
  client_contact, client_company, client_addr1, client_addr2,
  signer_name, signer_title,
  subtotal, tax_label, tax, total,
  scope_items:  [str, ...]       # HTML-escaped strings
  notes:        [str, ...]       # optional -> "Clarifications & Exclusions"
  sov:          [ {code, description, amount, phase?}, ... ]   # DIRECT costs
  sov_markups:  [ {label, amount}, ... ]   # GC / Fee / Insurance, shown on the SOV
  allowances:   [ {name, basis?, amount}, ... ]          # optional -> "Allowances" (amount: number or text like "$15.00 per SF")
  allowances_note: str                                   # optional line under the allowance total
  alternates:   [ {name, basis?, amount, unit?}, ... ]   # optional -> "Alternates" (adds, not in the total)
  value_engineering: [ {name, basis?, amount}, ... ]     # optional -> "Value Engineering" (deducts, amount positive)

Sheet order is fixed: cover, Scope of Work, Schedule of Values, Allowances,
Alternates, Value Engineering (each only if present), then Clarifications &
Exclusions LAST. The M mark (assets/mc_m_2026.png) sits top right on the cover. Content flows onto continuation sheets when a
page fills, so the fixed-height sheets never silently clip.
"""
import base64, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---- page geometry (px @96dpi), mirrors template.html ----
BODY_H      = 841      # interior sheet height after the running header
SEC_HEAD_H  = 54       # .sec margin-top + h2 + margin-bottom
ROW_PAD     = 27       # scope row padding + border
LINE_H      = 21       # 14px * 1.5
SCOPE_CPL   = 95       # chars per line in a scope/notes row
NOTE_CPL    = 96       # chars per line in the sov reconciliation note
SOV_ROW_PAD = 23       # sov row padding + border
SOV_HEAD_H  = 30       # sov column header row
SOV_SUB_H   = 43       # direct-work subtotal row
SOV_MK_H    = 40       # one markup row
SOV_GRAND_H = 63       # big blue grand-total block
MIN_ROWS_AFTER_HEAD = 3

SOV_NOTE = ("This Schedule of Values reconciles to the Subtotal shown on the cover.")


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def money(v):
    return v if isinstance(v, str) else "${:,.2f}".format(v)


def wrapped(text, cpl):
    """Estimated rendered line count for a string at `cpl` chars per line."""
    plain = re.sub(r"<[^>]+>", "", text)
    plain = (plain.replace("&amp;", "&").replace("&nbsp;", " ")
                  .replace("&quot;", '"').replace("&#39;", "'"))
    return max(1, -(-len(plain) // cpl))


def sheet(inner, page_no, proposal_no, project_name):
    return f"""<div class="sheet">
  <div class="runhead">
    <div class="wordmark">MONTANA <span>/</span> CONTRACTING</div>
    <div class="meta">{proposal_no} · {project_name}</div>
  </div>
{inner}
  <div class="foot">
    <span>Since 1984 &nbsp;·&nbsp; NY + NJ</span>
    <span class="pg">{page_no:02d}</span>
  </div>
</div>"""


def paginate(title, rows, tail_h=0):
    """Greedy page-fill for one section. Returns [[row_html, ...], ...].

    `tail_h` is extra height that must ride with the final row (the SOV totals
    block). A heading is never left with fewer than MIN_ROWS_AFTER_HEAD rows.
    """
    pages, cur, used, i = [], [], SEC_HEAD_H, 0
    while i < len(rows):
        h = rows[i][1] + (tail_h if i == len(rows) - 1 else 0)
        if used + h > BODY_H and cur:
            pages.append(cur)
            cur, used = [], SEC_HEAD_H
            h = rows[i][1] + (tail_h if i == len(rows) - 1 else 0)
        cur.append(rows[i][0])
        used += h
        i += 1
    if cur:
        pages.append(cur)
    # never strand a heading with too few rows on the page it opens
    if len(pages) > 1 and len(pages[-1]) < MIN_ROWS_AFTER_HEAD and len(pages[-2]) > MIN_ROWS_AFTER_HEAD:
        while len(pages[-1]) < MIN_ROWS_AFTER_HEAD and len(pages[-2]) > MIN_ROWS_AFTER_HEAD:
            pages[-1].insert(0, pages[-2].pop())
    return pages


def render_section(title, rows, cont=False, wrap_notes=False, tail=""):
    body = [f'<div class="sec">\n<div class="sec-head">'
            f'<h2>{title}{" (continued)" if cont else ""}</h2></div>']
    if wrap_notes:
        body.append('<div class="notes-list">')
    body.extend(rows)
    if wrap_notes:
        body.append("</div>")
    if tail:
        body.append(tail)
    body.append("</div>")
    return "\n".join(body)


def numbered(items):
    out = []
    for n, s in enumerate(items, 1):
        out.append((f'<div class="scope-item"><span class="n">{n:02d}</span>'
                    f'<span>{s}</span></div>',
                    ROW_PAD + LINE_H * wrapped(s, SCOPE_CPL)))
    return out


def main():
    data = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    tpl = open(os.path.join(ROOT, "template.html")).read()

    for token, asset in (("{{FONT_REGULAR_B64}}", "TTCommonsPro-Regular.woff2"),
                         ("{{FONT_BOLD_B64}}", "TTCommonsPro-Bold.woff2"),
                         ("{{MARK_B64}}", "mc_m_2026.png")):
        if token in tpl:
            tpl = tpl.replace(token, b64(os.path.join(ROOT, "assets", asset)))

    pno, pname = data["proposal_no"], data["project_name"]
    bodies = []          # interior sheet bodies, in final print order

    # ---------- 1. Scope of Work ----------
    for i, pg in enumerate(paginate("Scope of Work", numbered(data["scope_items"]))):
        bodies.append(render_section("Scope of Work", pg, cont=(i > 0)))

    # ---------- 2. Schedule of Values (optional) ----------
    sov = data.get("sov")
    markups = data.get("sov_markups") or []
    if sov:
        has_phase = any(r.get("phase") for r in sov)
        cpl = 44 if has_phase else 61
        ph_head = '<span class="c-phase">Phase</span>' if has_phase else ""
        col_head = ('<div class="sov-head"><span class="c-code">CSI</span>'
                    f'{ph_head}<span class="c-desc">Description</span>'
                    '<span class="c-amt">Amount</span></div>')
        rows = []
        for r in sov:
            ph = f'<span class="c-phase">{r.get("phase","")}</span>' if has_phase else ""
            rows.append((
                f'<div class="sov-row"><span class="c-code">{r["code"]}</span>{ph}'
                f'<span class="c-desc">{r["description"]}</span>'
                f'<span class="c-amt">{money(r["amount"])}</span></div>',
                SOV_ROW_PAD + LINE_H * wrapped(r["description"], cpl)))
        rows[0] = (col_head + "\n" + rows[0][0], rows[0][1] + SOV_HEAD_H)

        direct = sum(r["amount"] for r in sov)
        tail = [f'<div class="sov-sub"><span class="k">Schedule of Values Subtotal</span>'
                f'<span class="v">{money(direct)}</span></div>']
        for m in markups:
            tail.append(f'<div class="sov-mk"><span class="k">{m["label"]}</span>'
                        f'<span class="v">{money(m["amount"])}</span></div>')
        tail.append('<div class="sov-total"><span class="k">Subtotal</span>'
                    f'<span class="v">{money(data["subtotal"])}</span></div>')
        tail_h = SOV_SUB_H + SOV_MK_H * len(markups) + SOV_GRAND_H

        sov_pages = paginate("Schedule of Values", rows, tail_h=tail_h)
        for i, pg in enumerate(sov_pages):
            bodies.append(render_section(
                "Schedule of Values", pg, cont=(i > 0),
                tail="\n".join(tail) if i == len(sov_pages) - 1 else ""))

    # ---------- 3-5. Allowances, Alternates, Value Engineering (each optional, own section) ----------
    def priced(title, items, sign="", unit_key="unit", total=None, total_label="", note=""):
        rows = []
        for n, it in enumerate(items, 1):
            amt = it["amount"]
            a = amt if isinstance(amt, str) else sign + money(amt)
            if it.get(unit_key): a += f" {it[unit_key]}"
            basis = f' <em>{it["basis"]}</em>' if it.get("basis") else ""
            d = f'<b>{it["name"]}</b>{basis}'
            rows.append((f'<div class="pl-row"><span class="n">{n:02d}</span><span class="d">{d}</span>'
                         f'<span class="a">{a}</span></div>',
                         SOV_ROW_PAD + LINE_H * wrapped(it["name"] + " " + it.get("basis", ""), 82)))
        tail = []
        if total is not None:
            tail.append(f'<div class="pl-total"><span>{total_label}</span><span class="v">{sign}{money(total)}</span></div>')
        if note:
            tail.append(f'<p class="sov-note">{note}</p>')
        tail_h = (SOV_SUB_H if total is not None else 0) + (LINE_H * wrapped(note, NOTE_CPL) + 14 if note else 0)
        pages = paginate(title, rows, tail_h=tail_h)
        for i, pg in enumerate(pages):
            bodies.append(render_section(title, pg, cont=(i > 0), tail="\n".join(tail) if i == len(pages) - 1 else ""))

    al = data.get("allowances") or []
    lump = [x for x in al if not isinstance(x["amount"], str)]      # dollar allowances, totaled
    unit = [x for x in al if isinstance(x["amount"], str)]          # unit-price allowances ("$15.00 per SF"), listed after
    if lump:
        priced("Allowances", lump, total=sum(x["amount"] for x in lump), total_label="Allowances Total",
               note=data.get("allowances_note", "Allowances are included in the Subtotal. Final selections are reconciled against each allowance."))
    if unit:
        priced("Unit Price Allowances", unit, note=data.get("unit_allowances_note", "Unit price allowances set the material rate carried in the Subtotal."))
    alt = data.get("alternates") or []
    if alt:
        priced("Alternates", alt, sign="", note=data.get("alternates_note", "Alternates are not included in the Subtotal. Each is added to the contract when accepted."))
    ve = data.get("value_engineering") or []
    if ve:
        priced("Value Engineering", ve, sign="-", note=data.get("ve_note", "Value engineering options are not included in the Subtotal. Each is deducted from the contract when accepted."))

    # ---------- 6. Clarifications & Exclusions — ALWAYS LAST ----------
    notes = data.get("notes") or []
    if notes:
        title = "Clarifications &amp; Exclusions"
        for i, pg in enumerate(paginate(title, numbered(notes))):
            bodies.append(render_section(title, pg, cont=(i > 0), wrap_notes=True))

    tpl = tpl.replace("{{INTERIOR_BODY}}", bodies[0])
    tpl = tpl.replace("{{SOV_SECTION}}", "\n\n".join(
        sheet(b, i, pno, pname) for i, b in enumerate(bodies[1:], start=3)))

    simple = {
        "PROPOSAL_NO": pno, "DATE_LONG": data["date_long"],
        "PROJECT_NAME": pname, "PROJECT_LOCATION": data["project_location"],
        "CLIENT_CONTACT": data["client_contact"], "CLIENT_COMPANY": data["client_company"],
        "CLIENT_ADDR1": data["client_addr1"], "CLIENT_ADDR2": data["client_addr2"],
        "SIGNER_NAME": data["signer_name"], "SIGNER_TITLE": data["signer_title"],
        "SUBTOTAL": money(data["subtotal"]), "TAX_LABEL": data["tax_label"],
        "TAX": money(data["tax"]), "TOTAL": money(data["total"]),
    }
    for k, v in simple.items():
        tpl = tpl.replace("{{%s}}" % k, str(v))

    open(out, "w").write(tpl)
    print(f"Built {out}  ({len(bodies) + 1} sheets)")

    if sov:
        direct = sum(r["amount"] for r in sov)
        stack = direct + sum(m["amount"] for m in markups)
        ok = abs(stack - data["subtotal"]) < 0.005
        print(f"SOV reconciliation: direct {money(direct)} + markups "
              f"{money(stack - direct)} = {money(stack)} vs Subtotal "
              f"{money(data['subtotal'])} " + ("OK" if ok else "!! MISMATCH"))


if __name__ == "__main__":
    main()
