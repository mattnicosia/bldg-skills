"""E260050 whole-property proposal PDF data, from the presentation build (same figures, same lists)."""
import json, re, sys, html
from decimal import Decimal as D
sys.argv = ['build.py']
src = open('/home/claude/pres/cooper/web/build.py').read()
cut = src.index('# ================================================================ assets')
g = {'__name__': 'x'}
exec(compile(src[:cut].replace("HERE = os.path.dirname(os.path.abspath(__file__))", "HERE = '/home/claude/pres/cooper/web'"), 'b', 'exec'), g)
C, BASE, DIRECT, OP = g['C'], g['BASE'], g['DIRECT'], g['OP']
esc = lambda s: html.escape(s, quote=True)
PL = json.load(open('/home/claude/pres/cooper/web/proposal_lists.json'))

scope = [
 # shared
 "Provide one superintendent and one project manager for both buildings on one 26 week duration, with general labor, temporary toilet, temporary power, protection and final cleaning.",
 "Protect the existing pool, stone terrace and retaining wall throughout construction.",
 # barn
 "The Barn: Excavate for 4 foot frost walls and the full-height mechanical space under the lounge wing. Furnish and install 12x24 footings, parged 10 inch foundation walls, 4 inch reinforced slabs on 15 mil Stego wrap and 6 inch gravel, 2 inch XPS below grade, foundation waterproofing and a footing drain to daylight.",
 "The Barn: Furnish and install 2x6 exterior walls at a 15 foot plate, a 9:12 main roof, the tapered lounge wing roof, engineered floor framing over the mechanical space and at the mezzanine, LVL headers at the bifolds, ZIP wall and roof sheathing, and three exposed beams in the workshop.",
 "The Barn: Furnish and install canopies over the bifold doors on heavy timber brackets, a glazed cupola with a copper horse weathervane, and a Cumaru roof deck on a drainage mat over pitched EPDM with metal coping, scuppers and a guardrail.",
 "The Barn: Furnish and install high temperature ice and water shield over the whole roof, galvalume standing seam roofing, 6 inch gutters and 4 inch leaders.",
 "The Barn: Furnish and install Hardie board and batten siding on a ZIP rain screen, Hardie trim and soffits, spray foam insulation at the walls and roof, and a blower door test.",
 "The Barn: Furnish and install four Marvin custom exterior bifold doors with transoms, 10 feet by 11 feet 8 inches, eleven Marvin double-hung windows, the swing door to the roof deck, and the U-0.27 glass package.",
 "The Barn: Furnish and install 5/8 inch gypsum board at Level 4 finish, a white oak stair to the mezzanine, a box stair to the mechanical space, railings and guardrails, painted wainscot and reclaimed beams at the lounge, interior doors, trim and closet interiors.",
 "The Barn: Furnish and install workshop workbenches and desk areas, a custom front bar with a copper bar top, back bar cabinets with a stone counter, a powder room vanity and bath accessories, wide plank wood flooring, powder room tile, painting and staining, and a Hearthstone Bari wood stove with a Class A flue.",
 "The Barn: Furnish and install plumbing with a hot water heater, the toilet, lav and bar sink, a new 500 gallon underground propane tank and piping, two zone ducted heat pumps, an ERV, and electrical with a 200A subpanel, a feeder from the house, an upgrade to the house electric service, dedicated 240V circuits for the owner's shop equipment, lighting, low voltage and smoke and CO detection.",
 "The Barn: Furnish and install water and electric runs from the house, a sanitary line to the existing septic, silt fence, a construction entrance, and rough and finish grading around the building.",
 # pool house
 "The Pool House: Demolish and remove the existing pool house pavilion, roof and slab, and disconnect and cap its utilities.",
 "The Pool House: Excavate and furnish and install 24x12 footings, 10 inch frost walls 48 inches deep with the east and north walls carried up against the grade, a 4 inch reinforced slab on a vapor barrier, R-10 rigid and 6 inch gravel, Rubber-R-Wall waterproofing with a drainage mat, footing and roof drains to daylight, and a passive radon vent.",
 "The Pool House: Furnish and install 2x6 exterior walls, 2x12 roof framing at 11:12, TJI floor framing, an LVL ridge beam, LVL headers, a steel moment frame at the south bifold wall, and the north entry canopy on brackets.",
 "The Pool House: Furnish and install a cedar shingle roof to match the main house on a Cedar Breather mat, copper drip edge, head flashing, sill pans and the north canopy roof, and 6 inch half-round copper gutters with 4 inch downspouts.",
 "The Pool House: Furnish and install 6 inch smooth Hardie lap siding over R-5 rigid insulation and housewrap, mitered Claymark Solid Gold casings, corner boards, pilasters, belt, frieze and soffits with built-up cornice returns, spray foam insulation at the walls and roof, closed cell spray foam inside the frost walls, and a blower door test.",
 "The Pool House: Furnish and install Marvin Ultimate bifold doors 2 and 3, the bifold window over the outside bar counter, the Marvin Ultimate entry door, the Reeb Select storage door pair, and 30 Marvin Ultimate clad windows with tempered glass where required and the U-0.27 glass package.",
 "The Pool House: Furnish and install gypsum board at Level 4 finish, base, crown and casings, interior doors and hardware, a split-run white oak stair with a wood guardrail, painted inset Shaker bar and vanity cabinets with stone countertops, a 3 inch stone counter outside the bar window, and built-in storage shelving.",
 "The Pool House: Furnish and install the stone floor to match the pool terrace, white oak flooring at the second floor, shower tile with a frameless glass door, bath accessories, interior and exterior painting, and four undercounter appliances.",
 "The Pool House: Furnish and install plumbing with a hot water heater, the outdoor shower, a multi-zone cold climate heat pump with four ductless heads, an ERV, and electrical with a 125A subpanel, a feeder from the house, 27 recessed fixtures, smoke and CO detection, and a 14 kW propane standby generator fed from the Barn tank.",
 "The Pool House: Furnish and install Sonos audio, Lutron lighting control and 26 Lutron motorized shades with low voltage pre-wire.",
 "The Pool House: Furnish and install water and electric runs from the house, a sanitary line to the existing septic, the generator gas run from the Barn tank, 2 inch bluestone treads and landing with stone veneer at the north entry steps and the west exterior stair, silt fence, and rough and finish grading around the building.",
]

notes = [
 "All work performed in a professional and workman-like manner, licensed as required by law.",
 "All work fully covered with compensation and liability insurances.",
 "Pricing includes all supervision, labor, materials and equipment required to complete the scope above.",
 "Pricing is valid for 30 days.",
 "All work to be performed during normal working hours. Overtime is not included.",
 "Permits and fees are not included.",
"Sales tax on materials is carried in the pricing. No sales tax is added to the contract amount. It is assumed a capital improvement certificate will be provided to Montana Contracting Corp. prior to the start of construction.",
] + g['BASIS'] + g['CLAR'] + [e.replace('Landscaping, topsoil, seed,', 'Landscaping, lawn restoration, topsoil, seed,') for e in g['EXCL']] + [
 "Allowances, Alternates and Unit Price Allowances are listed in their own sections of this proposal.",
]
notes = [n.replace('Alternate 5', 'Alternate 5 of this proposal') if 'Alternate 5' in n else n for n in notes]

sov = [{'code': d['n'], 'description': f"{d['b'].replace('The ', '')}, {d['name']}" if d['b'] != 'Barn and Pool House' else d['name'], 'amount': float(d['v'])} for d in g['DIVS']]
num = lambda s: float(D(s.replace('$', '').replace(',', '').split(' ')[0]))
allow = []
for a in PL['allowances']:
    allow.append({'name': a['label'], 'basis': a['basis'], 'amount': num(a['v']) if 'per' not in a['v'] else a['v']})
alts = [{'name': re.sub(r'^\d+\. ', '', a['title']).replace(', Per Day', ''), 'basis': a['note'], 'amount': float(a['v']), 'unit': 'per day' if a['id'] == '5' else ''} for a in PL['alternates']]

data = {
 'proposal_no': 'E260050-01', 'date_long': 'October 22, 2026',
 'project_name': 'The Cooper Barn and Pool House', 'project_location': '194 Titicus Road, North Salem, New York',
 'client_contact': 'Erika DaSilva, Project Manager', 'client_company': 'Crisp Architects',
 'client_addr1': '16 Washington Avenue', 'client_addr2': 'Millbrook, NY 12545',
 'signer_name': 'Matt Nicosia', 'signer_title': 'COO',
 'subtotal': float(BASE), 'tax_label': 'Sales Tax (Excluded)', 'tax': 0.0, 'total': float(BASE),
 'scope_items': [esc(s) for s in scope], 'notes': [esc(n) for n in notes],
 'sov': sov, 'sov_markups': [{'label': 'Overhead and Profit (15%)', 'amount': float(OP)}],
 'allowances': allow, 'alternates': alts,
 'allowances_note': 'Carried in the Subtotal, before overhead and profit.',
 'alternates_note': 'Priced with overhead and profit. Not included in the Subtotal.',
}
assert abs(sum(s['amount'] for s in sov) + float(OP) - float(BASE)) < 0.005
txt = re.sub(r'&[#\w]+;', '', json.dumps(data))
for ch in ('—', '–', ';'):
    assert ch not in txt, ch
json.dump(data, open('data.json', 'w'), indent=1)
print('ok', len(sov), 'sov rows', len(allow), 'allowances', BASE)
