---
name: drawings-to-massing
description: Turn 2D construction drawings (plans and elevations) into a massing.json 3D model for the Montana bid presentation kit, with the elevations projected onto the walls as skins.
---

# Drawings to Massing

Builds a light 3D model of a building from its drawings when there is no architect's model. The result is the `massing.json` the Bid Presentation Kit reads (see `kit/README.md`, section massing.json). It reads like a paper model: true footprint and heights, with the actual elevation drawings on the walls.

It works best on buildings made of boxes, gables, sheds and hips, which covers most houses and small commercial work. Curved or very complex forms come out simplified. Say so, and suggest asking the architect for the model.

## Tools

`kit/tools/drawings.py` (needs poppler and Pillow):

- `index <set.pdf>`: every sheet with its number and what it holds (PLAN, ELEVATION, SECTION...).
- `page <set.pdf> <n> <out.png> [dpi]`: render a sheet. Use 40 to 60 dpi to look, 150 to 200 to crop.
- `crop <sheet.png> x0 y0 x1 y1 <out.jpg> --clean`: crop an elevation. `--clean` whitens the paper and darkens the lines.
- `scale <px> <feet>`: pixels per foot from a dimension you can read.

## Steps

1. **Index the set.** Find the floor plans, roof plan, exterior elevations and building sections. If the drawing-index skill has already run on the set, use its index instead.
2. **Footprints.** Read each mass from the dimensioned plans: main house, wings, garage, stair or entry volumes, upper-floor boxes, and cantilevers as their own volumes.
   - Coordinates are in feet: x east, y north, with one corner of the building at the origin.
   - Take dimensions from the dimension strings, never from scaling the image, unless no dimension exists. If you scale, compute pixels per foot from the longest dimension you can read, and note that the value was scaled.
3. **Heights.** Take finished floor, plate, parapet and ridge elevations from the elevation level markers or the sections. Grade is 0. Basement or exposed foundation goes below 0.
4. **Roofs.**
   - `flat`: gets a thin coping automatically.
   - `gable`: `ridge` height and `axis` along the ridge.
   - `shed`: `ridge` and `high` side N/S/E/W.
   - `hip`.
   Gable, shed and hip roofs use the volume's bounding rectangle.
5. **Phases.** Tag every volume with the phase that builds it, in build order. Typical phases: `foundation`, `structure`, `modules` or `framing`, `envelope`, `hardscape`. These drive the scroll reveal and the schedule sync.
6. **Alternates.** A volume that only exists in an alternate (roof deck, solar array, pergola) gets `"alt": "<alternate number>"`. It appears when that alternate is switched on.
7. **Elevation skins.**
   - Render the elevation sheet at 150 dpi.
   - Crop each elevation from the building's left edge to its right edge, and from the lowest visible point to the highest. Do not crop at the title, dimension lines or level markers.
   - Save the crops as `drawings/elev_S.jpg`, `elev_N.jpg`, `elev_E.jpg` and `elev_W.jpg`.
   - Match each drawing to the compass face it shows. An "East Elevation" shows the east face.
   - Give the extents the crop covers: `x0`/`x1` in feet for S and N, `z0`/`z1` for E and W, `y0`/`y1` for bottom and top.
   - If a skin lands mirrored, swap the face or the extents.
8. **Context.** Add paving, drives and terraces as `flats`, and a few `trees` around the edges. Keep trees small: radius 7 to 10 ft for a house.
9. **Check.** Build the presentation and run `node tools/check.mjs <project> desktop`. Look at the hero, an aerial and the rear.
   - Window lines should land where the volumes break.
   - Upper boxes should sit on the right lower boxes.
   - Cantilevers should overhang.
   - Fix coordinates, not the camera.

## Accuracy

- State in the reply what each dimension came from: dimension strings, level markers, or scaled.
- List anything guessed, such as a wing with no dimensions or a roof height read off a section.
- The model is for a presentation, not a takeoff. Never pull quantities from it.
