# sow_data.json -- contract

Plain ASCII throughout (`ensure_ascii=True`). Everything the builder renders comes from
this file. The script holds no project content of its own.

```json
{
  "mode":            "quantified",
  "landlord_tenant": false,

  "project":      "JVL Academy",
  "address":      "17 Battery Place, New York, NY 10004",
  "date":         "2026-08-27",
  "prepared_by":  "BLDG Estimating",
  "job":          "260110",
  "client":       "Keystone Builders",

  "trades": [
    {
      "trade": "Drywall & Carpentry",
      "csi":   ["09 20 00", "09 29 00", "09 72 00"],
      "lines": [
        {
          "reference": "5/A-201",
          "scope":     "Type 2 -- Interior Stud Wall Partition -- 2 HR [UL #U419, STC 50-53]",
          "qty":       250.73,
          "unit":      "LF",
          "rate":      42.50,
          "responsibility": "Tenant",
          "bullets": [
            "(4 LAYERS) 3-5/8\" 20 GA. STUD @ 24\" O.C. (HEIGHT LMT. 14'-9\")",
            "(2) LAYERS 5/8\" FIRECODE TYPE 'X' G.W.B. BOTH SIDES, U.O.N.",
            "FILL CAVITY WITH SOUND ATTENUATION BATT INSULATION"
          ]
        },
        { "reference": "[UNVERIFIED]", "scope": "I/O Single HM & HW", "qty": 50, "unit": "EA" }
      ]
    }
  ],

  "notes": [
    { "type": "EXCLUSION",     "item": "Demolition",   "text": "..." },
    { "type": "CLARIFICATION", "item": "Paint colors", "text": "..." }
  ],
  "conflicts": [
    { "reference": "A-201, A-301",
      "text": "Floor Tile T-L-1 | Daltile Tuscan Brown (A-201) vs Continental Slate (A-301)" }
  ],
  "tbd_items": [
    { "reference": "A-401", "text": "Interior Wall Paint Color | TBD | Awaiting Owner Selection" }
  ],

  "markup_rows":   6,
  "markup_labels": ["General Conditions", "Insurance", "Fee"],

  "basis": [
    { "trade": "Painting", "csi": "09 91 00",
      "scope": "Prep And Paint New Gypsum Board Partitions",
      "qty": 25981.68, "unit": "SF",
      "basis": "(Types 1-6 1,604.73 LF x 2 faces) + single-face runs 38.25 LF = 3,247.71 LF x 8'-0\" typ ceiling ht per A-200.00" }
  ]
}
```

## The two modes

`mode` decides the grid, and it is the only switch that matters.

| | `"scope"` | `"quantified"` |
|---|---|---|
| Columns | Reference, Scope Item, [Resp.], gutter, Sub #1-4 | Reference, Scope Item, Qty, Unit Type, Unit Rate, Total, [Resp.], gutter, Sub #1-4 |
| Needs a takeoff | No | Yes |
| Markup ladder | None | SUBTOTAL, up to six compounding markup rows, TOTAL |
| Close-out | SUBTOTAL across the sub columns only | Full ladder on our Total and all four sub columns |
| Goes to | Subs, in a bid package, before anything is counted | The GC, to level bids against our own number |

**Scope mode carries no markup ladder on purpose.** There is no money of ours to mark up,
and the only free column would be Scope Item, which would put a percentage under a text
heading and mirror that mistake onto the SOV. This matches what the scope-only skill did
before the two were merged.

`landlord_tenant: true` adds a `Resp.` column in either mode. Fill
`lines[].responsibility` with `Landlord`, `Tenant` or `Both`. The classification rules are
in `references/landlord-tenant-rules.md`.

## Fields

| Field | Required | Notes |
|---|---|---|
`mode` | no | `scope` or `quantified`. Defaults to `quantified` |
`landlord_tenant` | no | Adds the Resp. column. Defaults to false |
`project` | yes | Sheet title, page header, notes-sheet title. NEVER `Untitled` |
`address`, `date`, `prepared_by`, `job`, `client` | no | Header block and page footer |
`trades[]` | yes | **Rendered in array order.** Sort before writing the file |
`trades[].trade` | yes | Uppercased in the header band. The unit a sub bids |
`trades[].csi` | no | Listed after the trade name |
`trades[].lines[].reference` | yes | `5/A-201`, or `A-400`, or comma-separated, or `[UNVERIFIED]`. Blank for auto-inserted boilerplate |
`trades[].lines[].scope` | yes | Begins with a directive. Bracket spec at the end |
`trades[].lines[].qty` | quantified only | `null` renders `--`, shades the row red, totals nothing |
`trades[].lines[].unit` | quantified only | Area work takes SF, never LF |
`trades[].lines[].rate` | no | Left blank when the pricing columns go out empty |
`trades[].lines[].responsibility` | landlord/tenant only | `Landlord`, `Tenant` or `Both` |
`trades[].lines[].bullets[]` | no | Verbatim drawing language. Column A only, never touches a sum |
`notes[]` | no | `type` is `EXCLUSION` or `CLARIFICATION`. Exclusions render red |
`conflicts[]` | no | Full-width block under the ladder. Never silently resolved |
`tbd_items[]` | no | Full-width block under the ladder |
`markup_rows` | no | Defaults to 6. Ignored in scope mode |
`markup_labels[]` | no | Fills the label column top-down. Unlabelled rows stay blank |
`basis[]` | no | The hidden Quantity Basis sheet. Omit it and the sheet is not created |

`conflicts[]` and `tbd_items[]` also accept bare strings, and the builder renders them with
an empty reference.

## Legacy shapes

`normalize()` accepts every shape this skill's data has taken, so an old `sow_data.json`
sitting in a job folder still builds:

- `trades[]` carrying `lines[]` (current)
- `trades[]` carrying `code` / `title` / `items[]` (the old Excel builder)
- `subdivisions[]` carrying `code` / `title` / `line_items[]` with `scope_item` (the old sample)
- `project` as a nested object rather than flat keys
- `notes` as `{"standard": [], "drawing_specific": []}`, plus the separate
  `standard_clarifications[]` and `drawing_specific_clarifications[]` arrays
- `tbd` as an alias for `tbd_items`

Write new data in the current shape. The others exist so nothing in a job folder rots.
