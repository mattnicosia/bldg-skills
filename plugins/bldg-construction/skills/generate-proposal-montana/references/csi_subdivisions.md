# Common CSI MasterFormat subdivisions

Reference for assigning subdivision codes to raw scope/cost line items. This is not
exhaustive — it covers the trades that come up most often in the small-to-mid-size
renovation work (bathrooms, kitchens, offices, schools) this skill is typically used
for. If a line item doesn't fit anything here, look up the correct MasterFormat
subdivision rather than guessing at a division-level code — the whole point of the
boss's revision was specificity, so a wrong-but-specific-looking code is worse than
taking a moment to get it right.

## Division 01 — General Requirements
- `01 50 00` Temporary Facilities and Controls
- `01 56 00` Temporary Barriers and Enclosures (protection of existing surfaces/areas)
- `01 74 19` Construction Waste Management (dumpsters, debris removal, if tracked separately from demo)

## Division 02 — Existing Conditions
- `02 41 00` Demolition
- `02 41 19` Selective Demolition (demo within an occupied/active building)

## Division 03 — Concrete
- `03 30 00` Cast-in-Place Concrete
- `03 35 00` Concrete Finishing

## Division 06 — Wood, Plastics, and Composites
- `06 11 00` Wood Framing
- `06 20 00` Finish Carpentry
- `06 40 00` Architectural Woodwork (custom millwork, cabinetry)

## Division 07 — Thermal and Moisture Protection
- `07 14 00` Fluid-Applied Waterproofing (shower pans, wet-area waterproofing)
- `07 21 00` Thermal Insulation
- `07 92 00` Joint Sealants (caulking)

## Division 08 — Openings
- `08 11 00` Metal Doors and Frames
- `08 14 00` Wood Doors
- `08 71 00` Door Hardware

## Division 09 — Finishes
- `09 21 16` Gypsum Board Assemblies (framing + board as one system)
- `09 29 00` Gypsum Board (board/drywall material and install only)
- `09 30 13` Ceramic Tiling
- `09 51 00` Acoustical Ceilings
- `09 65 00` Resilient Flooring (VCT, LVT, sheet vinyl)
- `09 68 00` Carpeting
- `09 91 00` Painting

## Division 10 — Specialties
- `10 14 00` Signage
- `10 21 00` Toilet Compartments (partitions)
- `10 26 00` Wall and Corner Guards
- `10 28 00` Toilet, Bath, and Laundry Accessories
- `10 44 00` Fire Extinguishers, Cabinets, and Accessories

## Division 11 — Equipment
- `11 30 00` Residential Equipment (appliances)

## Division 12 — Furnishings
- `12 24 00` Window Shades
- `12 36 00` Countertops
- `12 93 00` Site Furnishings

## Division 21 — Fire Suppression
- `21 13 00` Fire-Suppression Sprinkler Systems

## Division 22 — Plumbing
- `22 10 00` Plumbing Piping (rough-in, supply/waste lines)
- `22 40 00` Plumbing Fixtures (sinks, toilets, showers, drains — supply and install)

## Division 23 — HVAC
- `23 05 00` Common Work Results for HVAC
- `23 82 00` Convection Heating and Cooling Units (baseboard, unit heaters)

## Division 26 — Electrical
- `26 05 00` Common Work Results for Electrical
- `26 27 26` Wiring Devices (switches, receptacles)
- `26 51 00` Interior Lighting

## Division 32 — Exterior Improvements
- `32 12 16` Asphalt Paving
- `32 92 00` Turf and Grasses (landscaping)

## Notes on judgment calls

- **Waterproofing tied to tile work** (shower pan mud jobs, wall waterproofing behind tile): use `07 14 00` as its own line, or fold it into `09 30 13` Ceramic Tiling if the user's cost breakdown doesn't separate it — either is defensible, just be consistent within one proposal.
- **Rough-in vs. fixture cost combined**: if a single price covers both rough-in plumbing and fixture supply/install (common in small-project pricing), it's fine to code the whole thing `22 40 00` Plumbing Fixtures rather than splitting out a `22 10 00` line with no real cost behind it.
- **Protection/temporary items**: general jobsite protection (floor protection, dust barriers) is `01 56 00`; don't confuse this with `01 74 19` waste management (dumpsters/debris hauling), which is a separate cost center even though both are "General Requirements."
