import json, html
from decimal import Decimal as D
W='/home/claude/work/E26044/'
sc=json.load(open(W+'web/scope_lines.json')); pl=json.load(open(W+'web/proposal_lists.json'))
notes=json.load(open(W+'notes.json')); P=json.load(open(W+'project.json'))
esc=lambda s: html.escape(s, quote=True)
items=[]
for dv in sc['divs']:
    code=dv['n'].replace(' ','.')
    ls=list(sc['lines'][code])
    ls=[l[len(dv['name'])+2:] if l.startswith(dv['name']+': ') else l for l in ls]
    if len(ls)==1 and ls[0].rstrip('.').lower()==dv['name'].lower(): items.append(esc(dv['name']+'.')); continue
    n=-(-len(ls)//18); per=-(-len(ls)//n)
    for j,k in enumerate(range(0,len(ls),per)):
        head=dv['name']+(' (continued)' if j else '')
        items.append(esc(f"{head}: "+'; '.join(ls[k:k+per])+'.'))
house=["All work performed in a professional and workman-like manner, licensed as required by law.",
 "All work fully covered with compensation and liability insurances.",
 "Pricing includes all supervision, labor, materials and equipment required to complete the scope above.",
 "Pricing is valid for 30 days.",
 "All work to be performed during normal working hours. Overtime is not included.",
 "Permits and fees are not included."]
nl=house+["Basis of budget: "+b for b in notes['Basis of Budget']]+[c for c in notes['Clarifications'] if not c.startswith(('Material allowances','A $10,000.00'))]+["Excluded: "+e for e in notes['Exclusions']]
nl.append("Allowances, alternates and value engineering items are listed in their own sections.")
direct=sum(D(d['v']) for d in sc['divs']); assert direct==D('8822421.94')
money=lambda s: D(s.replace('$','').replace(',',''))
data={
 "proposal_no":"E26044","date_long":"October 30, 2026",
 "project_name":"The Inn at Kirkside","project_location":"53865 State Highway 30, Roxbury, New York",
 "client_contact":"M-ARK Project, Inc.","client_company":"The Inn at Kirkside","client_addr1":"53865 State Highway 30","client_addr2":"Roxbury, NY 12474",
 "signer_name":"Matt Nicosia","signer_title":"Chief Operating Officer",
 "subtotal":9632320.28,"tax_label":"Sales Tax (Excluded)","tax":0.0,"total":9632320.28,
 "scope_items":items,"notes":[esc(n) for n in nl],
 "sov":[{"code":d['n'],"description":esc(d['name']),"amount":float(d['v'])} for d in sc['divs']],
 "sov_markups":[{"label":"Design Contingency (0%)","amount":0.0},{"label":"Fee (6%)","amount":529345.32},{"label":"Insurance (3%)","amount":280553.02}],
 "allowances":[{"name":esc(a['label']),"basis":esc(a['basis']),"amount":(a['v'] if 'per' in a['v'] else float(money(a['v'])))} for a in pl['allowances']],
 "alternates":[{"name":esc(a['title'].split('. ',1)[1]),"basis":esc(a['note']),"amount":float(a['v']),"unit":""} for a in pl['alternates']],
 "value_engineering":[{"name":esc(P['ve'][str(i+1)]['title'].split('. ',1)[1]),"basis":esc(P['ve'][str(i+1)]['note']),"amount":-float(v['v'])} for i,v in enumerate(pl['ve'])],
}
json.dump(data,open('data.json','w'),indent=1)
print(len(items),'scope rows',len(nl),'notes')
