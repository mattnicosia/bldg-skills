import json, re, collections
from decimal import Decimal as D, ROUND_HALF_UP
import openpyxl
from openpyxl.styles import Font
C=lambda x: D(str(x)).quantize(D('0.01'), ROUND_HALF_UP)
rows=json.load(open('lines_final.json')); cj=json.load(open('codes.json')); NAMES=cj['names']; SC=cj['scope']
for r in rows: r['v']=D(r['v'])
FALL={'03.05.00':'03.30.00','04.05.00':'04.20.00','05.05.00':'05.50.00','31.05.00':'31.10.00','09.21.00':'09.29.00','09.22.00':'09.29.00','09.25.00':'09.29.00',
      '09.31.00':'09.30.00','06.41.00':'06.22.00','06.48.00':'06.11.00','10.22.00':'10.21.00'}
NAMES.update({'26.05.00':'Electrical, General','32.30.00':'Planting','01.31.00':'General Requirements','01.45.00':'Inspections','01.50.00':'General Conditions','01.74.00':'Container/Waste Removal','01.56.00':'Temporary Fencing','01.53.00':'Protection',
              '07.65.00':'Window Sill Pans and Flashing','31.23.00':'Soil Export and Utility Trenching'})
for r in rows:
    k=r['item'].strip().lower()
    c=SC.get(k)
    if c and c[:2]==r['code'][:2] and c in NAMES and r['code'] not in ('01.31.00','01.50.00'): r['code']=c
    r['code']=FALL.get(r['code'],r['code'])
    if r['item'].startswith('Spread Top Soil'): r['code']='31.22.00'
    if r['code']=='23.05.00':
        t=r['item'].lower()
        for keys,c in [(('bms','smoke detector'),'23.09.00'),(('geothermal','air separator','hydrokit'),'23.21.00'),(('radiant','manifold','unit heater','radiant pump'),'23.83.00'),
                       (('fan unit','exhaust fan, inline','f/i exhaust fan'),'23.34.00'),(('register','grille','louver'),'23.37.00'),(('hrv','heat recovery unit (hru)','erv unit'),'23.72.00'),
                       (('vrf','mini split','condenser','dehumidifier','wchp'),'23.81.00'),(('duct','dryer vent','plenum'),'23.31.00')]:
            if any(k in t for k in keys): r['code']=c; break
# ---- Rev 9: combined subdivisions (Matt, 10/30)
REMAP={'06.11.00':'06.10.00','26.09.23':'26.05.00','26.24.00':'26.05.00','26.27.26':'26.05.00','27.11.00':'26.05.00','26.56.00':'26.50.00'}
for r in rows:
    r['code']=REMAP.get(r['code'],r['code'])
    if r['item']=='F/I HSS6X4X3/8': r['item']='F/I HSS6X4X3/8 Steel Tube'
NAMES.update({'06.10.00':'Rough Carpentry and Framing','26.05.00':'Electrical','26.50.00':'Lighting Fixtures'})
# ---- Rev 9: one line per item. Same item within a subdivision (ignoring sizes in brackets and counts) is merged.
PROTECT=('I/O Windows','F/I Exterior Window Casing to Match Existing','Foundation - Foundation Walls (Elevator Pit Walls)','Cut Opening In Roof For Elevator Shaft',
         'F/I 2X8 Pressure Treated Deck Framing','F/I Deck Stairs','F/I New Pergola','F/I Geothermal','F/I Hydrokit','F/I Air Separator','Roofing Repair Allowance',
         'Patch Walls & Ceilings Behind MEP','F/I Honeywell BMS','F/I Radiant Tubing','F/I Manifolds For Radiant','F/I Heat Water Cooled','F/I 100 KW Diesel','F/I Elevator')
SIZE=re.compile(r"""^(?:W|C|HSS)?\d[\d\-/\.]*(?:"|')?(?:x\d[\d\-/\.]*(?:"|')?)+$|^\d[\d\-/\.]*(?:"|')$""", re.I)
def mkey(item):
    t=re.sub(r'^(?:Levels|Foundation) - ','',item.strip()); t=re.sub(r'\s*\([^()]*\)','',t)
    t=' '.join(w for w in t.split() if not SIZE.match(w))
    t=re.sub(r'\b(F/I|F/O|I/O) Column\b', r'\1 Steel Column', t)
    return re.sub(r'\s+',' ',t).strip()
grp=collections.OrderedDict()
for r in rows:
    k=(r['code'], r['item'] if r['item'].startswith(PROTECT) else mkey(r['item']).lower())
    grp.setdefault(k,[]).append(r)
merged=[]
for (code,_),rs in grp.items():
    if len(rs)==1: merged.append(rs[0]); continue
    items=[x['item'] for x in rs]
    if len(set(items))==1: name=items[0]
    else:
        common=[p_ for p_ in re.findall(r'\([^()]*\)',items[0]) if all(p_ in it for it in items)]
        name=(mkey(items[0])+' '+' '.join(common)).strip()
    units={x['unit'] for x in rs}
    q=sum(D(str(x['qty'] or 0)) for x in rs) if len(units)==1 else D(1)
    merged.append({**rs[0],'item':name,'qty':float(q),'unit':rs[0]['unit'] if len(units)==1 else 'LS','v':sum(x['v'] for x in rs)})
print('merged',len(rows),'->',len(merged)); rows=merged
miss=sorted({r['code'] for r in rows if r['code'] not in NAMES}); assert not miss, miss
direct=sum(r['v'] for r in rows)
fee=C(direct*D('0.06')); ins=C((direct+fee)*D('0.03')); base=direct+fee+ins
print('direct',direct,'fee',fee,'ins',ins,'base',base)
TRADE={'01':'GENERAL REQUIREMENTS','02':'EXISTING CONDITIONS','03':'CONCRETE','04':'MASONRY','05':'METALS','06':'WOOD, PLASTICS & COMPOSITES','07':'THERMAL & MOISTURE PROTECTION',
       '08':'OPENINGS','09':'FINISHES','10':'SPECIALTIES','11':'EQUIPMENT','12':'FURNISHINGS','14':'CONVEYING EQUIPMENT','21':'FIRE SUPPRESSION','22':'PLUMBING','23':'HVAC',
       '26':'ELECTRICAL','27':'COMMUNICATIONS','28':'FIRE ALARM','31':'EARTHWORK','32':'EXTERIOR IMPROVEMENTS','33':'UTILITIES'}
wb=openpyxl.Workbook(); ws=wb.active; ws.title='Estimate'
ws['A1']='E26044 The Inn at Kirkside'; ws['A2']='53865 State Highway 30, Roxbury, NY 12474'; ws['A3']='Budget, Rev 6, 10/30/2026'
ws['A4']='Markups: Fee 6% on direct cost, Insurance 3% on direct cost plus fee. Design Contingency (TBD) 0%. Sales tax excluded.'
ws.append([]); ws.append([]); ws.append([]); ws.append([])
ws.cell(9,1,'Code'); ws.cell(9,2,'Item'); ws.cell(9,3,'Qty'); ws.cell(9,4,'Unit'); ws.cell(9,5,'Unit Cost'); ws.cell(9,6,'Total')
rr=10; rows.sort(key=lambda r:(r['code'],))
bydiv=collections.OrderedDict()
for r in rows: bydiv.setdefault(r['code'][:2],[]).append(r)
for dv,rs in bydiv.items():
    ws.cell(rr,1,TRADE[dv]).font=Font(bold=True); rr+=1
    for r in rs:
        q=r['qty'] or 1
        ws.append([]) if False else None
        ws.cell(rr,1,r['code']); ws.cell(rr,2,r['item']); ws.cell(rr,3,float(r['qty'])); ws.cell(rr,4,r['unit']); ws.cell(rr,5,float(C(r['v']/D(str(q))))); ws.cell(rr,6,float(r['v'])); rr+=1
    ws.cell(rr,1,'TRADE TOTAL'); ws.cell(rr,6,float(sum(r['v'] for r in rs))); rr+=2
ws.cell(rr,1,'SUBTOTAL -- DIRECT COST'); ws.cell(rr,6,float(direct)); rr+=1
ws.cell(rr,1,'Design Contingency (TBD) 0%'); ws.cell(rr,6,0.0); rr+=1
ws.cell(rr,1,'Fee 6%'); ws.cell(rr,6,float(fee)); rr+=1
ws.cell(rr,1,'Insurance 3%'); ws.cell(rr,6,float(ins)); rr+=1
ws.cell(rr,1,'TOTAL -- BASE BID'); ws.cell(rr,6,float(base)); rr+=2
ALTS=[('ALTERNATE 1 -- Survey and Layout',[('Building and Foundation Stakeout, Including the Elevator Pit',1,'EA',3500),('Foundation As-Built Survey',1,'EA',2500),('Site Layout: Paving, Curbs, Utilities and Light Poles',3,'EA',2000),('Final As-Built Survey for the CO and Stormwater Closeout',1,'EA',4500)]),
      ('ALTERNATE 2 -- Condition Survey and Settlement Monitoring',[('Pre-Construction Condition Survey',1,'EA',3500),('Settlement Monitoring During Underpinning',8,'WK',750)]),
      ('ALTERNATE 3 -- Professional Final Cleaning',[('Professional Final Cleaning',15896,'SF',1.00)]),
      ('ALTERNATE 4 -- Window Cleaning',[('Window Cleaning',90,'EA',25)]),
      ('ALTERNATE 5 -- Drained Air Gap Behind the House Wrap',[('Spacer or Drainage Mat in Exterior Wall Stud Bays, Drainable WRB Sealed to Studs',5188,'SF',2.25)]),
      ('VE-1 -- Delete House Wrap at the Roof',[('Delete Henry WeatherSmart at the Roof, Foam Applied Direct to the Roof Deck',10000,'SF',-3.60)])]
# ---- Rev 8: value engineering. HVAC deducts use cost detail rates (the leveled HVAC lines carry the subcontract spread).
def lv(*keys, code=None): return sum(r['v'] for r in rows if (code is None or r['code'].startswith(code)) and any(k in r['item'] for k in keys))
spray=lv('Spray Foam', code='07.21'); lux=lv('Type H ','Type K ','Type P ','Type S ','Type T ', code='26.50')
van=lv('Custom Vanity', code='06.22'); seat=lv('Window Seat', code='06.22')
r2=lambda x: float(C(x))
ALTS+=[
 ('VE-2 -- VRF Manufacturer Controls in Lieu of a Full BMS',[('Delete Honeywell BMS',1,'LS',-200000),('VRF Manufacturer Central Controls, BACnet Integration of ERVs and Geothermal Pumps',1,'LS',60000)]),
 ('VE-3 -- Air-Source VRF in Lieu of the Geothermal Well Field',[('Delete Geothermal Wells, 16 at 495 Feet',16,'EA',-14000),('Delete Geothermal Pumps, Hydrokits and Air Separator',1,'LS',-41500),('Delete Water Cooled Heat Recovery Unit',1,'EA',-88300),('Delete Wiring of Geothermal Pumps',1,'LS',-2600),('Cold-Climate Air-Source Heat Recovery Condensers, Pads and Screening',1,'LS',125000),('Air-to-Water Heat Pump for the Radiant Floors and Unit Heaters',1,'LS',45000)]),
 ('VE-4 -- Radiant Floors at Baths, Conservatory and Vestibule Only',[('Delete Radiant Tubing, Keep 1,500 SF',8850,'SF',-9),('Reduce Radiant Manifolds',1,'LS',-15000)]),
 ('VE-5 -- Generator Sized to Key Loads',[('60 KW Standby Generator for Life Safety, Elevator, Refrigeration and Kitchen in Lieu of 100 KW',1,'LS',-75000)]),
 ('VE-6 -- Flash-and-Batt Insulation',[('2 Inch Closed Cell Spray Foam Plus Batt in Lieu of Full Depth Spray Foam',1,'LS',-r2(spray*D('0.35')))]),
 ('VE-7 -- Marvin Signature Elevate at Rear and Secondary Elevations',[('Signature Elevate in Lieu of Signature Ultimate, About 40 of 90 Windows',1,'LS',-r2(D('315717')*D(40)/D(90)*D('0.25')))]),
 ('VE-8 -- Equivalent Decorative Lighting',[('Equivalents for Fixture Types H, K, P, S and T, Signature Types F and J Kept',1,'LS',-r2(lux*D('0.5')))]),
 ('VE-9 -- Gravel at Overflow Parking',[('Gravel in Lieu of Full Depth Asphalt at Overflow Parking',9500,'SF',-6.50)]),
 ('VE-10 -- Concrete Pavers at Secondary Paths',[('Concrete Pavers in Lieu of Medina Stone at Secondary Paths',390,'SF',-64)]),
 ('VE-11 -- Semi-Custom Vanities and Simpler Window Seats',[('Semi-Custom Vanity Boxes with Custom Fronts',1,'LS',-r2(van*D('0.30'))),('Simplified Window Seats',1,'LS',-r2(seat*D('0.40')))]),
 ('VE-12 -- LULA Elevator',[('Limited Use Limited Application Elevator in Lieu of a Passenger Elevator',1,'LS',-45000)]),
]
altv={}
for h,ls in ALTS:
    ws.cell(rr,1,h).font=Font(bold=True); rr+=1; d=D(0)
    for it,q,u,rt in ls:
        v=C(D(str(q))*D(str(rt))); d+=v; ws.cell(rr,2,it); ws.cell(rr,3,q); ws.cell(rr,4,u); ws.cell(rr,5,rt); ws.cell(rr,6,float(v)); rr+=1
    f=C(d*D('0.06')); i=C((d+f)*D('0.03')); t=d+f+i
    ws.cell(rr,1,'Fee 6%'); ws.cell(rr,6,float(f)); rr+=1
    ws.cell(rr,1,'Insurance 3%'); ws.cell(rr,6,float(i)); rr+=1
    ws.cell(rr,1,'TOTAL'); ws.cell(rr,6,float(t)); rr+=2; altv[h]=(d,t)
sv=wb.create_sheet('SOV'); sv.append(['Schedule of Values, E26044 The Inn at Kirkside']); sv.append([]); sv.append(['CSI','Trade','Final Price'])
codes=collections.OrderedDict()
for r in rows: codes[r['code']]=codes.get(r['code'],D(0))+r['v']
for k,v in codes.items(): sv.append([k,NAMES[k],float(v)])
sv.append(['SUBTOTAL','',float(direct)]); sv.append(['Fee 6%','',float(fee)]); sv.append(['Insurance 3%','',float(ins)]); sv.append(['TOTAL','',float(base)])
nt=wb.create_sheet('Notes & Clarifications'); nt.append(['Notes & Clarifications']); nt.append([]); nt.append([]); nt.append(['#','Group','Note'])
NOTES=json.load(open('notes.json'))
for g,items in NOTES.items():
    for i,t in enumerate(items,1): nt.append([i,g,t])
wb.save('estimate.xlsx')
json.dump({'direct':str(direct),'fee':str(fee),'ins':str(ins),'base':str(base),'alts':{h:[str(a),str(b)] for h,(a,b) in altv.items()},'codes':{k:[NAMES[k],str(v)] for k,v in codes.items()}},open('figures_wb.json','w'),indent=1)
for h,(a,b) in altv.items(): print(h,a,b)
print(len(codes),'codes')
