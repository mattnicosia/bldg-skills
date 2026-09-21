#!/usr/bin/env python3
"""Fill template.html with proposal data + embedded brand fonts.

Usage: python3 build_proposal.py data.json out.html

data.json keys:
  proposal_no, date_long, project_name, project_location,
  client_contact, client_company, client_addr1, client_addr2,
  signer_name, signer_title, duration, duration_sentence,
  subtotal, tax_label, tax, total,
  scope_items: [str, ...],
  notes: [str, ...]          # optional -> "02 / Clarifications & Exclusions"

  sov: {                     # optional -> adds a 3rd page, "03 / Schedule of Values"
    "has_phases": bool,
    "groups": [
      {
        "csi": "26 00 00",
        "title": "Electrical",
        "items": [
          {"desc": "...", "phase": "Phase 1", "amount": 12345.00}
          # "phase" omitted/ignored if has_phases is false
        ]
      }, ...
    ],
    "total": 123456.00        # must equal client-facing subtotal
  }
"""
import base64, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def money(v):
    if isinstance(v, str):
        return v
    return "${:,.2f}".format(v)

def build_sov_page(sov, proposal_no, project_name):
    if not sov or not sov.get("groups"):
        return ""

    has_phases = bool(sov.get("has_phases"))
    groups_html = []
    for g in sov["groups"]:
        rows = []
        for it in g["items"]:
            phase_html = f'<span class="phase">{it["phase"]}</span>' if has_phases and it.get("phase") else ""
            rows.append(
                f'<div class="sov-row"><span class="desc">{it["desc"]}</span>'
                f'{phase_html}<span class="amt">{money(it["amount"])}</span></div>'
            )
        group_subtotal = sum(it["amount"] for it in g["items"])
        groups_html.append(
            f'<div class="sov-group">'
            f'<div class="sov-group-head"><span>{g["csi"]} &nbsp;·&nbsp; {g["title"]}</span>'
            f'<span>{money(group_subtotal)}</span></div>'
            + "\n".join(rows) +
            f'</div>'
        )

    return f"""
<!-- ============================== PAGE 3 — SCHEDULE OF VALUES ============================== -->
<div class="sheet">
  <div class="runhead">
    <div class="wordmark">MONTANA <span>/</span> CONTRACTING</div>
    <div class="meta">{proposal_no} · {project_name}</div>
  </div>

  <div class="sec">
    <div class="sec-head"><span class="idx">03 /</span><h2>Schedule of Values</h2></div>
    {''.join(groups_html)}
    <div class="sov-total"><span>Total</span><span>{money(sov["total"])}</span></div>
  </div>

  <div class="foot">
    <span>Since 1984 &nbsp;·&nbsp; NY + NJ</span>
    <span class="pg">03</span>
  </div>
</div>
"""

def main():
    data = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    tpl = open(os.path.join(ROOT, "template.html")).read()

    # Fonts: inline from assets/ if the template still carries the tokens
    # (a fonts-embedded template copy has them baked in already).
    if "{{FONT_REGULAR_B64}}" in tpl:
        tpl = tpl.replace("{{FONT_REGULAR_B64}}", b64(os.path.join(ROOT, "assets/TTCommonsPro-Regular.woff2")))
    if "{{FONT_BOLD_B64}}" in tpl:
        tpl = tpl.replace("{{FONT_BOLD_B64}}",    b64(os.path.join(ROOT, "assets/TTCommonsPro-Bold.woff2")))

    scope = "\n".join(
        f'<div class="scope-item"><span class="n">{i:02d}</span><span>{s}</span></div>'
        for i, s in enumerate(data["scope_items"], 1))
    tpl = tpl.replace("{{SCOPE_ITEMS}}", scope)

    notes = data.get("notes") or []
    if notes:
        body = "\n".join(
            f'<div class="scope-item"><span class="n">{i:02d}</span><span>{n}</span></div>'
            for i, n in enumerate(notes, 1))
        sec = ('<div class="sec" style="margin-top:40px;">'
               '<div class="sec-head"><span class="idx">02 /</span>'
               '<h2>Clarifications &amp; Exclusions</h2></div>'
               f'<div class="notes-list">{body}</div></div>')
    else:
        sec = ""
    tpl = tpl.replace("{{NOTES_SECTION}}", sec)

    tpl = tpl.replace("{{SOV_PAGE}}", build_sov_page(
        data.get("sov"), data["proposal_no"], data["project_name"]))

    simple = {
        "PROPOSAL_NO": data["proposal_no"], "DATE_LONG": data["date_long"],
        "PROJECT_NAME": data["project_name"], "PROJECT_LOCATION": data["project_location"],
        "CLIENT_CONTACT": data["client_contact"], "CLIENT_COMPANY": data["client_company"],
        "CLIENT_ADDR1": data["client_addr1"], "CLIENT_ADDR2": data["client_addr2"],
        "SIGNER_NAME": data["signer_name"], "SIGNER_TITLE": data["signer_title"],
        "DURATION": data["duration"], "DURATION_SENTENCE": data["duration_sentence"],
        "SUBTOTAL": money(data["subtotal"]), "TAX_LABEL": data["tax_label"],
        "TAX": money(data["tax"]), "TOTAL": money(data["total"]),
    }
    for k, v in simple.items():
        tpl = tpl.replace("{{%s}}" % k, str(v))

    open(out, "w").write(tpl)
    print(f"Built {out}")

if __name__ == "__main__":
    main()
