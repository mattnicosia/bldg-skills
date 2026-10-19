# e26049: massing.json from the surface model

1004 Old Albany Post Road at DD-1, built from the surface-model skill's worked example
(`../../../surface-model/examples/e26049/surfaces.json`), not from the plans. To remake it:

```bash
python3 -I scripts/massing_from_surfaces.py ../surface-model/examples/e26049/surfaces.json --out examples/e26049/massing.json
```

What came out:

| Shape | Key | From |
|---|---|---|
| `L1/EXT` volume, 0 to 13.2 ft | `sp_8`, faces `sk_43` to `sk_46` | L1 level marker (A-301, HIGH); the exterior faces' height (MEDIUM) |
| `L2/EXT` volume, 12.4 to 24.0 ft | `sp_9`, faces `sk_47` to `sk_50` | L2 level marker (A-301, MEDIUM); the exterior faces' height (MEDIUM) |
| `RF/MAIN` roof flat at 13.2 ft | `sp_10`, surface `sk_51` | drawn on `L1/EXT`'s top, see below |
| `RF/BOX` roof flat at 24.0 ft | `sp_11`, surface `sk_52` | the RF level marker (A-301, MEDIUM) |
| `L1/DECK` cedar flat at grade | `sp_7`, floor `sk_41` | its outline sits outside `L1/EXT` |
| seven interior footprints in `spaces` | `sp_1` ... | the rooms' outlines and ceiling heights |

The notes in the file say what to check. The one that matters: the model puts both roof
planes on the single `RF` level at 24.0 ft, and `RF/MAIN` has the first floor's outline, so
the script drew it on `L1/EXT`'s top at 13.2 ft and said so. The address grammar has one roof
level, so a lower roof plane has no elevation of its own in the model yet. Eight hosts have
keys and no outline (three second-floor rooms the set has not laid out, five site elements);
the picture needs none of them, and each keeps its key for the day it gets a shape.

No skins, trees or site paving: those are hand steps 8 and 9 in the skill. Nothing in this
file is a quantity.
