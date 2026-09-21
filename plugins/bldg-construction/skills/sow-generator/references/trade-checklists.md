# Trade Checklists -- Primaries, Secondaries, and Ratio Placeholders

> ## READ THIS BEFORE USING ANY NUMBER BELOW
>
> **Every ratio in this file is an UNVERIFIED PLACEHOLDER.** These figures were converted
> from metric source material written for a different market (Australia / UK) and have
> never been checked against a single Montana Contracting or BLDG Estimating job.
>
> They are here so the *structure* of a derivation is available, not because the numbers
> are right. Rockland County NY labor, code, and means-and-methods do not match the market
> these came from.
>
> **Order of preference, every time:**
> 1. BLDG Estimating historical unit-cost / per-unit ratios — ask the user for them
> 2. A verified published source (RSMeans or equivalent) available in-session
> 3. These placeholders — **only** if neither exists, and **only** labeled
>    `ESTIMATED -- unverified ratio` in the output
>
> When a real BLDG figure replaces a placeholder, overwrite the placeholder here and mark
> it `VERIFIED (BLDG, <project>, <date>)`. That is how this file stops being borrowed and
> starts being an asset.

Imperial units throughout: `EA`, `SF`, `LF`, `CY`, `TON`, `lb`, `CFM`, `in`, `ft`.

For each trade: what AI counts or extracts directly (**PRIMARY**), what it derives with
arithmetic (**SECONDARY**), and the ratio for each derivation.

Both capping rules from `measurement-methods.md` apply to everything here:

- A secondary's confidence is capped at its source primary's confidence.
- A ratio that is an **assumption** (not read off the drawings) caps the result at MEDIUM
  even when the primary is HIGH.

Useful conversion: `concrete CY = area SF x thickness in / 12 / 27`.

---

## Concrete (CSI 03)

**Primaries**
- Slab area (SF) — explicit dimension extraction (plan dims) or schedule. Prefer a dimensioned outline over scaling.
- Footing/pier counts by type (P1, P2, F1...) — text-tag count, reconciled against the pier schedule.
- Footing dimensions per type — schedule extraction (footing/pier schedule) or explicit dimension on the detail.
- Column counts by type — text-tag count.
- Wall lengths (LF) — explicit dimension; scale only as a last resort.
- Slab/footing/wall thicknesses (in) — explicit dimension from section notes.

**Secondaries (derive)**
- Slab concrete CY = slab SF x thickness in / 12 / 27
- Footing concrete CY = (L ft x W ft x D ft) x count / 27, per type
- Column concrete CY = section area SF x height ft x count / 27
- Wall concrete CY = wall LF x height ft x thickness in / 12 / 27
- Rebar lb = concrete CY x reinforcement rate
- Formwork SF = exposed concrete face area (perimeter LF x height ft)

**Ratio placeholders — UNVERIFIED**
- Reinforcement rate: slabs 135-185 lb/CY; footings 150-220 lb/CY; columns 250-420 lb/CY; walls 170-250 lb/CY. **Always prefer the reinforcement schedule over any of these.**
- Concrete waste allowance: 3-5%. Carry it as its own line; never bake it silently into a primary.

---

## Structural Steel (CSI 05)

**Primaries**
- Member counts by mark (B1, C1...) — text-tag count.
- Member sizes/sections per mark — schedule extraction (steel schedule) or tag.
- Member lengths (LF) — explicit dimension; scale only as a last resort.
- Base plate / connection counts — text-tag count.

**Secondaries (derive)**
- Member weight lb = length LF x unit weight lb/ft (from the section designation) x count
- Total TON = sum of member weights / 2000
- Connection/bolt counts = members x connections-per-member

**Ratio placeholders — UNVERIFIED**
- Fabrication connection allowance: 7-12% added to net member tonnage.
- **Unit weight always comes from the steel section table. Never estimate a section weight** — this one is not a placeholder, it is a hard rule.

---

## Electrical (CSI 26)

**Primaries**
- Receptacle / outlet counts — text-tag count.
- Light fixture counts by type — text-tag count or luminaire schedule.
- Switch / sensor / data point counts — text-tag count.
- Panel / distribution board counts — text-tag count or panel schedule.
- Circuit counts — panel schedule extraction.

**Secondaries (derive)**
- Cable LF = point count x LF-per-point
- Conduit LF = cable LF x conduit-to-cable ratio (or count x run length)
- Termination count = (outlets + fixtures + switches) x 2
- Fitting count = conduit LF x fittings-per-LF

**Ratio placeholders — UNVERIFIED**
- Cable per general power point: 40-60 LF (default 50 LF). Per lighting point: 25-40 LF.
- Conduit-to-cable: ~0.7 LF conduit per LF of cable in conduit systems.
- Fittings: ~0.1 per LF of conduit (bends, couplers, connectors).

Counting points and applying an LF-per-point ratio is far more reliable than tracing
cable or conduit routes on a dense electrical plan. Default to the ratio method; scale a
run only when the user specifically asks.

**Note:** `electrical-estimator` is the skill for priced Division 26/27/28 work and has
its own tri-state rate tables. Use this section for quantities only; do not price from it.

---

## Mechanical / HVAC (CSI 23)

**Primaries**
- Diffuser / grille / register counts by type — text-tag count or air-device schedule.
- Equipment counts (RTU, FCU, exhaust fan, VAV) — text-tag count reconciled against the equipment schedule.
- Duct sizes (in) — explicit dimension from duct tags.
- Duct run lengths (LF) — explicit dimension only. **Do not scale.** Default to `NOT_MEASURED`.

**Secondaries (derive)**
- Duct surface SF (for insulation/sheet metal) = duct perimeter ft x length LF
- Duct weight lb = surface SF x gauge weight lb/SF
- Flex duct LF = diffuser count x flex-per-diffuser
- Refrigerant/condensate pipe LF = equipment count x pipe-per-unit

**Ratio placeholders — UNVERIFIED**
- Flex duct per diffuser: 6-13 LF.
- Insulation = ductwork surface SF x 1.0, plus 8% lap/waste.

Adjust for system mix rather than applying a generic ratio. A VRF-heavy system with many
small fan coils drives substantially more refrigerant piping per SF than an all-ducted RTU
system — say so in the output.

---

## Plumbing (CSI 22)

**Primaries**
- Fixture counts by type (WC, lav, shower, sink) — text-tag count or fixture schedule.
- Floor drain / floor waste counts — text-tag count.
- Water heater / pump counts — text-tag count or equipment schedule.
- Pipe sizes (in) — explicit dimension from pipe tags.
- Pipe run lengths (LF) — explicit dimension only. **Do not scale.** Default to `NOT_MEASURED`.

**Secondaries (derive)**
- Supply pipe LF = fixture count x supply-per-fixture
- Waste/vent pipe LF = fixture count x waste-per-fixture
- Fitting count = pipe LF x fittings-per-LF
- Insulation LF = hot/cold supply pipe LF (1:1)

**Ratio placeholders — UNVERIFIED**
- Supply pipe per fixture: 20-33 LF. Waste/vent per fixture: 16-26 LF.
- Pipe fittings: ~0.12 per LF.

---

## Adding a trade

Copy a section and replace the items. Keep the three blocks: **Primaries** (with the
preferred method), **Secondaries** (with the formula), **Ratio placeholders** (with a
source-of-truth reminder). The discipline is always the same:

> Maximize counts, dimensions, and schedules. Minimize scaled measurement. Derive
> everything else with transparent arithmetic that appears in the output.

---

## Provenance

Structure adapted from the `quantity-takeoff` skill, whose content derives from a published
method by Tim Fairley / Contractor OS.

**Kept:** the three-block per-trade format, the primary/secondary split, the
"points x ratio beats tracing routes" principle, and the extensibility instruction.

**Changed:** every unit and ratio converted metric to imperial; every converted figure
explicitly marked UNVERIFIED pending BLDG Estimating job history; `NOT_MEASURED` made the
default for linear duct and pipe runs; a pointer added to `electrical-estimator` for priced
electrical work.
