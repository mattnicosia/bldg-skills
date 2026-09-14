#!/usr/bin/env python3
"""Fill template.html with proposal data + embedded brand fonts.

Usage: python3 build_proposal.py data.json out.html
data.json keys:
  proposal_no, date_long, project_name, project_location,
  client_contact, client_company, client_addr1, client_addr2,
  signer_name, signer_title, duration, duration_sentence,
  subtotal, tax_label, tax, total,
  scope_items: [str, ...],
  notes: [str, ...]          # optional -> "03 / Clarifications & Exclusions"
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
