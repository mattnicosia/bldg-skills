# Example E260050: the Cooper Barn and Pool House, whole property (kit v1.13, 2026-10-22)

Two buildings on one page, from three workbooks: the Barn, the Pool House and the Shared General Requirements
(one superintendent and one PM for both, on one 26 week schedule). Live at montana-cooper.netlify.app.

- `web/build.py`: `BOOKS` loads the three workbooks with row offsets (barn 0, pool house 100000, shared 200000) so row keys stay
  unique. Each book's base ties to its own TOTAL -- BASE BID row; the page base is their sum. Line extensions are kept as the workbook
  holds them (`X()`, Qty x Rate can run past the cent) and figures round once at display, so a book with sub-cent rates still ties.
- Elements and design steps carry `bld` ('barn' or 'ph'). `app.js` filters the element list (`.elist[data-b]`, stacked in `.elists`),
  the numbered badges and the marker numbering (`s.no`) by building. Frames: `b_*` and `p_*`, one frame size (the larger building's
  crop) with the smaller building centred in it.
- Six rail steps: the rail sits under the model column above 1180px (CSS in `build.py`).
- MasterFormat = each workbook's SOV, row for row, with the building as the row's scope line.
- Alternates numbered across the property (`ALT_SRC` maps page number to workbook and alternate).
- `model/build_el_pool_house.js`: the pool house from Crisp SK4 A1.1/A1.2, element tags, `win+west` style multi-tags so the cutaway
  frames lift the whole west wall (`--hide-els cutwall,west`), `floor2` for the second floor in the stair cutaway.
- `proposal_pdf/make_data.py`: the generate-proposal-mcc data.json from the same figures (SOV at direct cost, O&P 15%, allowances and
  alternates from `web/proposal_lists.json`).
