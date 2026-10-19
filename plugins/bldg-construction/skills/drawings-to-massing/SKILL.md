---
name: drawings-to-massing
description: Turn 2D construction drawings (plans and elevations) into a massing.json 3D model for the Montana bid presentation kit, with the elevations projected onto the walls as skins. When the job has a surface model (surface-model.json), build the volumes from its export instead of re-reading the plans, so every volume carries its surface key.
---

# Drawings to Massing

Builds a light 3D model of a building from its drawings when there is no architect's model. The result is the `massing.json` the Bid Presentation Kit reads (see `kit/README.md`, section massing.json). It reads like a paper model: true footprint and heights, with the actual elevation drawings on the walls.

It works best on buildings made of boxes, gables, sheds and hips, which covers most houses and small commercial work. Curved or very complex forms come out simplified. Say so, and suggest asking the architect for the model.

The footprints and heights come from one of two places. If the job has `surface-model.json`
(the surface-model skill ran after drawing-index), they come from its export, and every volume
carries the key of the space it draws. If it does not, read them off the dimension strings by
hand, as the steps below say. Never do both: the surface model is the one source for a job
that has one.

## Tools

`scripts/massing_from_surfaces.py` (stdlib only, run with `python3 -I`): `surfaces.json` from the surface-model skill in, the kit's `massing.json` out. Volumes, roof flats and interior footprints each carry their surface-model key as `el`. `--keep` carries the hand work (skins, windows, trees, hand-added shapes) over from the last `massing.json`. The worked example is `examples/e26049/`.

`kit/tools/drawings.py` (needs poppler and Pillow):

- `index <set.pdf>`: every sheet with its number and what it holds (PLAN, ELEVATION, SECTION...).
- `page <set.pdf> <n> <out.png> [dpi]`: render a sheet. Use 40 to 60 dpi to look, 150 to 200 to crop.
- `crop <sheet.png> x0 y0 x1 y1 <out.jpg> --clean`: crop an elevation. `--clean` whitens the paper and darkens the lines.
- `scale <px> <feet>`: pixels per foot from a dimension you can read.

## Steps

1. **Index the set.** Find the floor plans, roof plan, exterior elevations and building sections. If the drawing-index skill has already run on the set, use its index instead.
2. **Look for the surface model.** If the job folder has `surface-model.json`, export it and build from it:
   ```bash
   python3 -I <surface-model>/scripts/sm.py export <job>/surface-model.json --what surfaces --out <job>/surfaces.json
   python3 -I scripts/massing_from_surfaces.py <job>/surfaces.json --out <project>/massing.json [--keep <project>/massing.json]
   ```
   The script writes one volume per exterior outline per level, one flat per roof plane, and
   an interior `spaces` list, each with `"el": "<key>"` (`sp_N` for a space, `sk_N` for a
   surface) so the kit can tag the mesh `[el:sk_12]` and a later click layer can find the
   pins on it. Phases follow the level: below grade is `foundation`, at or above grade is
   `house`, roof planes are `roof`. Paste the `_phases` list into `project.json`. Read the
   `_notes`: they say where each height came from, what was assumed, and which hosts have a
   key but no outline yet. `--keep` carries the skins, windows, trees and hand-added shapes
   over from the last build. Then skip steps 3 and 4 (footprints and heights are settled) and
   go on from step 5. A wall the model does not have is a reading to add to the surface model,
   not a volume to add here: the model is the one source.
   If there is no `surface-model.json`, continue with step 3.
3. **Footprints.** Read each mass from the dimensioned plans: main house, wings, garage, stair or entry volumes, upper-floor boxes, and cantilevers as their own volumes.
   - Coordinates are in feet: x east, y north, with one corner of the building at the origin.
   - Take dimensions from the dimension strings, never from scaling the image, unless no dimension exists. If you scale, compute pixels per foot from the longest dimension you can read, and note that the value was scaled.
4. **Heights.** Take finished floor, plate, parapet and ridge elevations from the elevation level markers or the sections. Grade is 0. Basement or exposed foundation goes below 0.
5. **Roofs.**
   From the surface model, every roof comes out flat. Change the volume's `roof` here for a gable, shed or hip read off the elevations.
   - `flat`: gets a thin coping automatically.
   - `gable`: `ridge` height and `axis` along the ridge.
   - `shed`: `ridge` and `high` side N/S/E/W.
   - `hip`.
   Gable, shed and hip roofs use the volume's bounding rectangle.
6. **Phases.** Tag every volume with the phase that builds it, in build order. Typical phases: `foundation`, `structure`, `modules` or `framing`, `envelope`, `hardscape`. These drive the scroll reveal and the schedule sync. From the surface model the phases are already set by level (`foundation`, `house`, `roof`); keep them, and give them their labels in `project.json`.
7. **Alternates.** A volume that only exists in an alternate (roof deck, solar array, pergola) gets `"alt": "<alternate number>"`. It appears when that alternate is switched on.
8. **Elevation skins.**
   - Render the elevation sheet at 150 dpi.
   - Crop each elevation from the building's left edge to its right edge, and from the lowest visible point to the highest. Do not crop at the title, dimension lines or level markers.
   - Save the crops as `drawings/elev_S.jpg`, `elev_N.jpg`, `elev_E.jpg` and `elev_W.jpg`.
   - Match each drawing to the compass face it shows. An "East Elevation" shows the east face.
   - Give the extents the crop covers: `x0`/`x1` in feet for S and N, `z0`/`z1` for E and W, `y0`/`y1` for bottom and top.
   - If a skin lands mirrored, swap the face or the extents.
9. **Context.** Add paving, drives and terraces as `flats`, and a few `trees` around the edges. Keep trees small: radius 7 to 10 ft for a house.
10. **Check.** Build the presentation and run `node tools/check.mjs <project> desktop`. Look at the hero, an aerial and the rear.
   - Window lines should land where the volumes break.
   - Upper boxes should sit on the right lower boxes.
   - Cantilevers should overhang.
   - Fix coordinates, not the camera.

## Accuracy

- State in the reply what each dimension came from: dimension strings, level markers, or scaled. From the surface model, repeat its `_notes` and the confidence it carried; the model's citations are the sources.
- List anything guessed, such as a wing with no dimensions or a roof height read off a section.
- The model is for a presentation, not a takeoff. Never pull quantities from it.
