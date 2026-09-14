# Trade-Specific Scope Splitting Rules

Detailed examples of how to apply trade splitting rules. These rules override what may be shown on drawings. Examples are organized by subdivision where the line item belongs.

## MEP Demolition (ALL MEP trades: Electrical, HVAC, Sprinkler, Plumbing, Fire Alarm)

Universal split: the MEP sub PROVIDES disconnection, safe-off, and drain-down (where applicable to the equipment); the DEMOLITION sub REMOVES and hauls off-site. In an MEP SOW use the `Provide` directive -- NEVER `Remove` for equipment the demo sub hauls. The `Remove` directive lives in the demolition/architectural SOW.

**HVAC/Mechanical (23 00 00 — HVAC), HVAC Sub Scope:**
```
Provide Disconnection, Drain-Down, and Safe-Off of Existing AHU-1 [Refrigerant Recovery; Physical Removal and Haul-Off by Demolition Subcontractor]
```

**Sprinkler (21 13 00), Sprinkler Sub Scope:**
```
Provide Drain-Down, Disconnection, and Safe-Off of Existing Sprinkler Piping and Heads [Cap at Disconnection; Physical Removal and Haul-Off by Demolition Subcontractor]
```

**Plumbing (22 00 00 — Plumbing), Plumbing Sub Scope:**
```
Provide Disconnection, Drain-Down, and Safe-Off of Existing Boiler / Water Heater / Fixtures [Cap Supply/Waste/Vent/Gas; Physical Removal and Haul-Off by Demolition Subcontractor]
```

**Electrical (26 00 00 — Electric), Electrical Sub Scope (always include for renovations):**
```
Provide Disconnection and Safe-Off of Existing Devices, Wiring, and Equipment [De-Energize at Source; Bypass/Continuity for Circuits to Remain; Physical Removal and Haul-Off by Demolition Subcontractor]
Provide Temporary Power and Lighting [Per Project Requirements]
```

**Fire Alarm (28 31 00), Fire Alarm Sub Scope:**
```
Provide Disconnection and Safe-Off of Existing Fire Alarm Devices and Wiring [Maintain Code-Required Coverage During Construction; Physical Removal and Haul-Off by Demolition Subcontractor]
```

**Demolition Sub (02 41 16 / 02 41 19 — Demolition SOW):**
```
Remove and Haul Off-Site Existing [MEP Equipment/Piping/Ductwork/Devices] [After Disconnection, Drain-Down, and Safe-Off by the Respective MEP Sub]
```
Adjust per equipment: omit drain-down if nothing to drain; omit refrigerant recovery if no refrigerant.

## Doors, Frames, and Hardware

**08 11 13 — Hollow Metal Doors and Frames:**
```
F/O D-1 Hollow Metal Frame [Steelcraft 16ga Painted]
```

**08 14 00 — Wood Doors:**
```
F/O D-1 Solid Core Wood Door [Marshfield Cherry Veneer Stain Grade]
```

**08 71 00 — Door Hardware:**
```
F/O D-1 Hardware Set [Schlage L Series Lever Set Satin Chrome]
```

**06 20 00 — Finish Carpentry:**
```
I/O D-1 Door Installation [Including Frame and Hardware Furnished By Others]
```

## Bathroom and Toilet Accessories

**10 28 13 — Toilet Accessories:**
```
F/O Toilet Paper Holder [Bobrick B-685 Stainless Steel]
F/O Grab Bar 36" [Bobrick B-6806.99x36 Stainless Steel]
F/O Soap Dispenser [Bobrick B-2111 Surface Mount]
```

**06 20 00 — Finish Carpentry:**
```
I/O Bathroom Accessories Installation [All Accessories Furnished By Others]
```

## Plumbing Fixtures (F/O Triggering Rough-In Pairing)

**22 40 00 — Plumbing Fixtures** (Furnish Side):
```
F/O P-1 Lavatory [Kohler K-2210 White]
F/O P-2 Water Closet [American Standard 215AA Champion 4 White]
```

**22 11 00 — Facility Water Distribution** (Install Side, paired):
```
I/O P-1 Lavatory Rough-In [Per Plumbing Drawings]
I/O P-2 Water Closet Rough-In [Per Plumbing Drawings]
```

## Owner-Supplied Materials

When drawings or specs note "Owner-Supplied" or "OFCI":

**Appropriate Trade Subdivision:**
```
I/O Owner-Supplied Refrigerator [Per Owner Selection]
Provide Acceptance and Coordination of Owner-Supplied Refrigerator Delivery
Provide Storage and Protection of Owner-Supplied Refrigerator Until Installation
```

## Auto-Inserted Shop Drawings

Always include "Provide Shop Drawings" in these subdivisions even if drawings don't call it out:

**05 50 00 / 05 73 00 — Architectural Metal:**
```
Provide Shop Drawings [Architectural Metal Assemblies]
```

**06 41 00 — Architectural Wood Casework (Millwork):**
```
Provide Shop Drawings [Custom Millwork and Casework]
```

**23 05 00 — Common Work Results for HVAC:**
```
Provide Shop Drawings [Ductwork Layout and Equipment]
```

**21 13 00 — Fire-Suppression Sprinkler Systems:**
```
Provide Shop Drawings [Sprinkler Layout per NFPA 13]
Provide Hydrostatic Testing
Provide Permits
Provide Inspections
Provide Signoff
```

## Capture-All Items (Per Subdivision)

Include in EVERY subdivision section:
```
Provide All Required Permits and Inspections Per Local Code
Provide Cleanup of Own Work into Centralized Container Provided by GC
Provide All Testing Required Per Drawing Specifications, Local Code Requirements, and Industry Standards
```

## Coordination Items

Include in scope where coordination genuinely required:
```
Coordinate with Electrical Sub for Outlet Locations Prior to Drywall Closure
Coordinate with HVAC Sub for Ceiling Penetrations Prior to Ceiling Installation
Coordinate with Plumbing Sub for Wall Chase Locations Prior to Framing
Coordinate with Owner for Equipment Delivery Schedule
```

## Existing Conditions Protection

Place at the BOTTOM of the relevant trade scope section, not in the Notes:
```
Provide Protection of Existing Adjacent Finishes
Provide Protection of Existing Floor Finishes During Work
Provide Protection of Existing Equipment to Remain
```
