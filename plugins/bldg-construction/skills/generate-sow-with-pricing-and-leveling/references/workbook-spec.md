# sow_pricing_data.json -- contract

Plain ASCII throughout (`ensure_ascii=True`). Everything the builder renders comes from
this file; the script holds no project content of its own.

```json
{
  "project":      "JVL Academy",
  "address":      "17 Battery Place, New York, NY 10004",
  "date":         "2026-08-27",
  "prepared_by":  "BLDG Estimating",
  "job":          "260110",
  "client":       "Keystone Builders",

  "trades": [
    {
      "trade": "Drywall & Carpentry",
      "csi":   ["06.11.00", "09.29.00", "09.72.00"],
      "lines": [
        {
          "scope":   "Type 2 -- Interior Stud Wall Partition -- 2 HR [UL #U419, STC 50-53]",
          "qty":     250.73,
          "unit":    "LF",
          "bullets": [
            "(4 LAYERS) 3-5/8\" 20 GA. STUD @ 24\" O.C. (HEIGHT LMT. 14'-9\")",
            "(2) LAYERS 5/8\" FIRECODE TYPE 'X' G.W.B. BOTH SIDES, U.O.N.",
            "FILL CAVITY WITH SOUND ATTENUATION BATT INSULATION"
          ]
        },
        { "scope": "I/O Single HM & HW", "qty": 50, "unit": "EA" }
      ]
    }
  ],

  "notes": [
    { "type": "EXCLUSION",     "item": "Demolition", "text": "..." },
    { "type": "CLARIFICATION", "item": "Paint colors", "text": "..." }
  ],

  "markup_rows":   6,
  "markup_labels": ["General Conditions", "Insurance", "Fee"],

  "basis": [
    { "trade": "Painting", "csi": "09.91.00",
      "scope": "Prep And Paint New Gypsum Board Partitions",
      "qty": 25981.68, "unit": "SF",
      "basis": "(Types 1-6 1,604.73 LF x 2 faces) + single-face runs 38.25 LF = 3,247.71 LF x 8'-0\" typ ceiling ht per A-200.00" }
  ]
}
```

## Fields

| Field | Required | Notes |
|---|---|---|
`project` | yes | Sheet title, page header, notes-sheet title |
`address`, `date`, `prepared_by`, `job`, `client` | no | Header block and page footer |
`trades[]` | yes | **Rendered in array order.** Sort before writing the file |
`trades[].trade` | yes | Uppercased in the header band |
`trades[].csi` | no | Listed after the trade name |
`trades[].lines[]` | yes | Rendered in array order |
`lines[].scope` | yes | The line item. Directive-led (`F/I`, `F/O`, `I/O`, `Remove`, `Provide`) |
`lines[].qty` | yes | Number, or `null` for a line requiring a plan count |
`lines[].unit` | yes | EA / SF / LF / CY / TON / LS |
`lines[].bullets` | no | Build-up detail. Bolds the parent line. Verbatim drawing language |
`notes[]` | no | `type` is `EXCLUSION` (red) or `CLARIFICATION` (light gray) |
`markup_rows` | no | Count of blank markup lines below SUBTOTAL. Default 6 |
`markup_labels` | no | Pre-fills the first N markup labels; percentages are always left blank for the user |
`basis[]` | no | Hidden Quantity Basis sheet. Omit entirely and the sheet is not created |

## Behaviour to rely on

- `qty: null` renders `--`, shades the row red, and contributes to no total.
- `bullets` render as indented italic sub-rows in column A only. They never carry a
  quantity or price and so cannot affect a sum.
- The Total column formula guards on `ISNUMBER`, so a null-quantity row computes blank
  rather than zero.
- Each sub column's TRADE TOTAL sums from the lump-sum row down through the last line.
- Row heights are computed from text length. Do not pass heights.
- Markups compound on the running total and are driven by one percent per row, shared
  across our total and all four sub columns. Empty percent renders blank, not zero.
- The SOV sheet is generated from the trade blocks. It needs no input of its own.
- `Quantity Basis` ships hidden. Hidden is not removed -- delete the sheet if the content
  must not travel.

## Before you build

- Scan every line for a linear unit on area work (paint, wall covering, tile, brick, wall
  patching, flooring). Fix at the data layer, not in the workbook.
- Confirm counted items against their own schedule and record any disagreement as a note.
- Confirm no `null` quantity is silently expected to price.
