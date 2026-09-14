# Landlord vs. Tenant Scope-Splitting Rules

Used when the skill is invoked in `landlord_tenant_split` mode. Every SOW line item must be tagged with a `responsibility` field: `"Landlord"`, `"Tenant"`, or `"Both"`.

## Classification Priority (highest to lowest)

When determining responsibility for a line item, apply these sources in order. The first source that addresses the item wins.

1. **Explicit assignment in a Landlord SOW (LL SOW) document** — if the narrative says "Landlord shall provide X" or "Tenant shall provide X," that determines the classification. This always wins over drawings.

2. **Explicit drawing callout** — if a drawing note says "By Tenant," "By Owner," "By Landlord," "N.I.C." (Not In Contract), "By Others," etc., that classification applies.

3. **Industry-convention defaults** (below) — used only when neither source above addresses the item.

If a Landlord SOW document and drawings explicitly conflict (e.g., LL SOW says Landlord, drawing says By Tenant), tag the item with the LL SOW classification but flag the conflict in the reconciliation report. The LL SOW typically prevails because it is the contractual document.

## Industry-Convention Defaults

### Default Landlord Scope (base building / shell prep)

**Structural:**
- All structural framing, columns, beams, slabs
- Floor openings for new stairs, elevators, shafts
- Slab cutting, shoring, patching
- New elevator shaft, pit, sump
- New stairs and stair enclosures (rated partitions, treads, risers, landings)
- Roof openings, curbs, flashings for base building equipment

**Architectural (base building only):**
- Building envelope (exterior walls, windows, roof)
- Common-area finishes, doors, ceilings, lighting (corridors, lobbies, stairs, restrooms outside tenant space)
- Rated demising partitions between tenant spaces (typically furnished by Landlord, ready to receive tenant finishes)
- Code-required signage in common areas

**Mechanical (HVAC) — capacity to tenant POC:**
- Primary HVAC distribution to tenant point-of-connection (POC)
- Rooftop units (RTUs), chillers, boilers serving multiple tenants
- Main ductwork mains and risers up to tenant connection
- Common-area HVAC (corridors, restrooms outside tenant space)
- Capped/valved stubs at the tenant POC
- Existing RTU rebalance/repair when retained for tenant use
- Combo fire/smoke dampers at rated demising partitions
- Tenant-area ventilation if required by code and provided by base building

**Plumbing — capacity to tenant POC:**
- Domestic water main with tenant submeter
- Sanitary and vent risers and below-slab mains
- Capped waste/vent stubs above slab at future tenant fixture locations
- Floor drains in common areas, mechanical rooms, elevator pits
- Elevator sump pump and discharge piping
- RPZ backflow preventer, booster pumps serving multiple tenants
- Existing water heater / hot water service if base-building-supplied

**Electrical — capacity to tenant POC:**
- Service entrance, main switchgear, distribution panels
- Tenant-dedicated panel and feeder to tenant POC (panel only, no branch circuits)
- Tenant submeter
- Common-area lighting and devices
- Emergency power feeders to tenant POC (panel only)
- Generator, ATS, transformers serving multiple tenants
- Empty conduits and draglines for future tenant data, FA, security at tenant POC
- Disconnects for base building equipment

**Life Safety:**
- Base-building fire alarm system (FACP, common-area devices, risers)
- Empty conduit/dragline for future tenant FACP at demising point
- Sprinkler standpipe/riser, floor control valve assemblies (CAPPED) at tenant POC
- Temporary sprinkler protection during construction
- Base-building code-required signage (exit, fire hose cabinet, FACP location)

**Common-Area Misc:**
- Demolition of prior base-building-supplied items
- Patching, firestopping at base-building penetrations and rated walls

### Default Tenant Scope (fit-out)

**Architectural:**
- All interior partitions inside the tenant demise
- All interior doors, frames, and hardware (except code-required base-building doors)
- All interior finishes: paint, wallcovering, flooring, ceilings, base, tile
- All millwork, casework, countertops, appliances within tenant space
- Tenant signage (rooms, branding, ADA wayfinding inside tenant space)
- Toilet accessories (grab bars, dispensers, mirrors) in tenant restrooms
- Window treatments

**Mechanical (HVAC) — downstream of tenant POC:**
- Branch ductwork from tenant POC to diffusers/grilles
- Diffusers, registers, grilles
- VAV boxes serving the tenant space
- Tenant-side controls, thermostats, sensors
- Exhaust fans serving tenant-only spaces (e.g., tenant restroom exhaust, kitchen exhaust)
- Acoustical lining and tenant-area insulation
- T&B (testing and balancing) of tenant-side air

**Plumbing — downstream of tenant POC:**
- All plumbing fixtures (water closets, lavatories, sinks, drinking fountains, mop sinks)
- Fixture supply piping from tenant POC to fixture
- Fixture waste/vent piping from fixture to cap above slab
- Water hammer arrestors, mixing valves, trap primers serving tenant fixtures
- Tenant-specific water heaters, instant hot units
- Coffee makers, ice makers, dishwashers, refrigerator water supply

**Electrical — downstream of tenant POC:**
- All branch circuits, conduits, wire downstream of tenant panel
- All wiring devices (receptacles, switches, dimmers)
- All lighting fixtures and lighting controls in tenant space
- All exit signs/emergency lights inside tenant demise
- Tenant FACP head end, all tenant-side FA devices (smoke detectors, horn/strobes, pull stations, duct detectors)
- All tenant data/telecom outlets, cabling, equipment
- All tenant security (card readers, cameras, DPS, electric strikes)
- All tenant AV systems

**Special Systems:**
- Tenant-only signage
- Tenant-specific specialty equipment (kitchen equipment, lab benches, etc.)

### "Both" Classification (coordination items appearing in both SOWs)

Some items legitimately belong in both packages because both parties have a piece of the work. Examples:

- **Firestopping at penetrations** — Landlord firestops their penetrations, Tenant firestops theirs
- **Cutting and patching** — each trade patches its own work
- **Coordination meetings, schedule coordination** — both parties participate
- **Field verification of existing conditions** — both parties verify
- **Temporary protection of existing work** — applies on both sides of the demise
- **Hoisting/freight elevator access** — typically coordinated by GC across both packages

When tagging an item as "Both," include a sub-classification noting which portion is each party's responsibility (e.g., `"Both - Landlord patches base building penetrations; Tenant patches tenant penetrations"`).

## Edge Cases / Common Gotchas

- **Existing tenant equipment being reused by new tenant (e.g., VRF unit to remain)** — typically Landlord protects during construction, Tenant pays to re-commission and integrate
- **Sprinkler heads in tenant space** — Landlord provides standpipe/riser/control valves; Tenant provides branch piping, heads, and FDNY signoff
- **Toilet rooms inside tenant space** — fixtures, partitions, accessories = Tenant; rough-ins (if base-building-provided) = Landlord
- **Elevator with tenant call buttons** — elevator equipment = Landlord; tenant-side card reader integration = Tenant
- **Demolition** — if the LL SOW assigns demolition to Landlord, all of it is Landlord. If split, base-building items go to LL and tenant-area items to Tenant.

## Conflicts to Always Flag

If you encounter any of these, flag in the reconciliation report rather than silently choosing one:

- LL SOW says Landlord but drawings say "By Tenant" (or vice versa)
- LL SOW assigns Landlord scope to perform work that drawings show as future tenant fit-out only
- Same scope item appears in both the LL SOW narrative and a tenant fit-out plan with no boundary noted
- LL SOW silent on an item that's clearly tenant fit-out but Landlord drawings show it
- An item is described in the LL SOW but is not on the drawings (missing from design intent)

## Output Format

When the skill runs in `landlord_tenant_split` mode, each line item in `sow_data.json` gets a `responsibility` field:

```json
{
  "reference": "P-200",
  "scope_item": "F/I New 4\" Waste Stub-Ups to Future Water Closets [...]",
  "responsibility": "Landlord",
  "responsibility_source": "P-200 drawing note + LL SOW Section 3.2"
}
```

The `responsibility_source` field is required and must cite either the LL SOW document section, the drawing reference, or the industry-convention rule applied.
