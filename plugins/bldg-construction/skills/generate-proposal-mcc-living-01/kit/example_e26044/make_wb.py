import json, re
from decimal import Decimal as D, ROUND_HALF_UP
C=lambda x: D(str(x)).quantize(D('0.01'), ROUND_HALF_UP)
rows=json.load(open('cd_lines.json'))
for r in rows: r['v']=C(r['total']); r['locked']=False
def find(code=None, item=None, qty=None, n=1):
    out=[r for r in rows if (code is None or r['code']==code) and (item is None or r['item'].startswith(item)) and (qty is None or abs(r['qty']-qty)<0.01)]
    assert len(out)==n, (code,item,qty,len(out)); return out
def setv(r, qty=None, unit=None, rate=None, v=None):
    if qty is not None: r['qty']=qty
    if unit is not None: r['unit']=unit
    if rate is not None: r['rate']=rate
    r['v']=C(v if v is not None else D(str(r['qty']))*D(str(r['rate']))); r['locked']=True
def add(code,item,qty,unit,rate,v=None):
    r={'code':code,'item':item,'qty':qty,'unit':unit,'rate':rate,'v':C(v if v is not None else D(str(qty))*D(str(rate))),'locked':True}; rows.append(r); return r
# ---- reclassifications made in the proposal
for r in find('09.29.00','F/I Henry Weathersmart',n=2): r['code']='07.27.00'
for r in rows:
    if r['code']=='09.29.00' and r['item'].startswith('I/O ') and any(k in r['item'] for k in ('Grab Bar','TP Holder','Towel','Mirror')): r['code']='10.28.00'
find('31.05.00','F/I Medina Stone Slab')[0]['code']='32.14.00'
find('31.05.00','F/I Gravel Path')[0]['code']='32.15.00'
find('32.05.00','F/I Gravel Path')[0]['code']='32.15.00'
find('31.05.00','F/I Handicap Parking Sign')[0]['code']='32.17.00'
find('31.05.00','F/I Light Pole Base')[0]['code']='26.56.00'
# ---- Division 01 replaced (Rev 3-5)
rows=[r for r in rows if not r['code'].startswith('01.')]
GR=[('Project Manager (60% of Duration)',36,'WK',3200),('Superintendent, Full Duration',60,'WK',3200),('General Laborer, As Needed',180,'DAY',300)]
for it,q,u,rt in GR: add('01.31.00',it,q,u,rt)
GC=[('Field Office Trailer',14,'MO',450),('Field Office Delivery & Pickup',1,'EA',1200),('Site Internet & Phone',14,'MO',150),('Field Office Furniture, Printer & Supplies',1,'EA',1500),
    ('Storage Container',14,'MO',200),('Storage Container Delivery & Pickup',1,'EA',600),('Temporary Toilets (2 Units)',28,'MO',250),
    ('Small Tools & Consumables',1,'EA',5000),('Safety: PPE, First Aid, Signage, Temporary Extinguishers',1,'EA',3500),('Drawings, Printing & Document Control',1,'EA',2500)]
for it,q,u,rt in GC: add('01.50.00',it,q,u,rt)
add('01.74.00','Container/Waste Removal, 30 YD',24,'EA',950)
add('01.56.00','Temporary Fence, Install & Remove',600,'LF',12)
for it,q,u,rt in [('Floor Protection (Ram Board)',12000,'SF',0.60),('Protect Existing Stairs, Railings, Hearth & Finishes to Remain',1,'EA',3500),('Dust Partitions (ZipWall)',1,'EA',2500)]: add('01.53.00',it,q,u,rt)
add('01.45.00','Inspections: Stormwater, Weekly',60,'EA',200)
add('31.25.00','Stabilized Construction Entrance',1,'EA',3500)
add('31.25.00','Storm Drain Inlet Protection & Concrete Washout',1,'EA',2500)
# ---- Rev 1
add('31.23.00','Export Surplus Topsoil (Stripped Less Re-Spread)',585,'CY',40)
add('31.23.00','Export Foundation Spoil',188,'CY',40)
add('31.23.00','Export Paving Box-Out Below Topsoil Strip',528,'CY',40)
add('31.23.00','Utility Trench, Sanitary Sewer',213.92,'LF',20)
add('09.91.00','Paint New 5/8" GWB at Existing Walls',10266.25,'SF',1.30)
setv(find('05.12.00','F/I C10X30 Steel Beam')[0],qty=1258.8,unit='LB',rate=5)
setv(find('05.12.00','F/I HSS4x4x1/4 Steel Beam')[0],qty=153.60,unit='LB',rate=5)
setv(find('05.12.00','F/I HSS6X4X3/8',qty=2)[0],qty=447.4,unit='LB',rate=5)
for it in ('F/I HSS4x4x1/4 Column','F/I HSS4x4x5/16 Column','F/I HSS4x4x3/8 Column'):
    r=find('05.12.00',it)[0]; setv(r,unit='LB',rate=5)
add('26.05.00','Roof Melt: 240V/30A Circuits with Ground-Fault Breakers',5,'EA',1500)
add('26.05.00','Roof Melt Contactor Panel',1,'EA',1500)
add('26.05.00','Wire Roof Melt Snow/Ice Sensor & Controller',1,'EA',1000)
for r in [x for x in rows if x['code']=='12.36.00']:
    r['item']=r['item'].replace('$65/SF','$75/SF'); setv(r,rate=140)
add('12.36.00','F/I Bar Countertop ($75/SF Material Allowance)',113.74,'SF',140)
setv(find('08.81.00','F/I 3/8" Tempered Shower Glass')[0],qty=9)
acc={'TP Holder':16,'Towel Bar':9,'Towel Holder':9,'Bath Vanity Mirror':11,'ADA Grab Bar':9}
for r in rows:
    if r['code']=='10.28.00':
        for k,q in acc.items():
            if k in r['item']: setv(r,qty=q)
for it,q,fo,io in [('Soap Dispenser',6,150,100),('Paper Towel Dispenser',2,250,100),('Sanitary Napkin Disposal',4,100,50),('Baby Changing Station',1,600,250)]:
    add('10.28.00','F/O '+it,q,'EA',fo); add('10.28.00','I/O '+it,q,'EA',io)
# ---- Rev 2
rows.remove(find('32.12.00','F/I Asphalt Paving 3" Binder')[0])
setv(find('06.10.00','F/I 2X8 Pressure Treated Deck Framing')[0],rate=22)
setv(find('03.35.00','FF-06: Grind & Seal')[0],rate=6)
setv(find('04.05.00','Mortar')[0],rate=1.50)
setv(find('06.10.00','I/O Windows')[0],rate=600)
add('07.65.00','Sill Pans & Flashing at Replaced Windows',90,'EA',150)
add('07.46.00','F/I Exterior Window Casing to Match Existing',1275.43,'LF',26)
setv(find('06.43.00','F/I Stairs & Railing')[0],rate=1800)
for r in rows:
    if r['item'].startswith(('Roofing Repair Allowance','Patch Walls & Ceilings Behind MEP')): r['locked']=True
# ---- Rev 8: hold the BMS at $200,000 and the geothermal well field at the cost detail; the HVAC spread goes to the other lines
setv(find('23.05.00','F/I Honeywell BMS System')[0],rate=200000)
for k in ('F/I Geothermal Wells','F/I Geothermal Pump','F/I Hydrokit','F/I Air Separator'):
    r=find('23.05.00',k)[0]; r['locked']=True
# ---- tie each division to the final schedule of values (Rev 6)
T={'01':'448900.00','02':'236638','03':'175763.62','04':'55402.75','05':'124559.91','06':'1107660.32','07':'392239.18','08':'794767','09':'684052.07',
   '10':'31785','11':'71750','12':'39630.65','14':'120000','21':'102969','22':'531436','23':'2100000','26':'1035000','31':'342731.40','32':'423714.04','33':'3423'}
dv=lambda r: '26' if r['code'][:2] in ('26','27','28') else r['code'][:2]
LEV={'06','07','09','22','23','26'}
for k,t in T.items():
    t=D(t); rs=[r for r in rows if dv(r)==k]; s=sum(r['v'] for r in rs); diff=t-s
    if k in LEV:
        free=[r for r in rs if not r['locked']]; fs=sum(r['v'] for r in free); f=(fs+diff)/fs
        for r in free: r['v']=C(r['v']*f)
        rem=t-sum(r['v'] for r in rs); max(free,key=lambda r:r['v'])['v']+=rem
        print(k,'leveled x',round(float(f),4))
    else:
        if abs(diff)>D('20'): print('MISMATCH',k,s,t,diff)
        if diff: max(rs,key=lambda r:r['v'])['v']+=diff; print(k,'adjusted',diff)
    assert sum(r['v'] for r in rs)==t,(k)
d=sum(r['v'] for r in rows); print('direct',d, len(rows))
json.dump([{**r,'v':str(r['v'])} for r in rows],open('lines_final.json','w'),indent=0)
