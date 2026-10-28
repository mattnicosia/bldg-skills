#!/bin/bash
# Selections views: Outside (green roof, and the EPDM variant), Inside (roof and box lifted off). One Blender at a time, about 3 minutes a frame.
#   bash web/render_selections.sh     then rebuild. Outputs go to <job>/sel/.
WEB=$(cd "$(dirname "$0")" && pwd); PROJ=$(dirname "$WEB"); KIT=${MCC_KIT:-$(dirname "$PROJ")/kit}; O=$PROJ/sel; mkdir -p "$O"
cd "$KIT"
# JOB: camera from the northwest, the land block, the EPDM model variant (model/build_el_epdm.js, made with tools/make_glb.mjs)
COM="--az 320 --rgba --block -24,-13,62,46,10.5 --sx 0.03 --size 2000x1250 --samples 32 --color"
ALL="--phases foundation,floor1,porch,upper,upperwalls,roof,interior,stair,site"
python3 tools/render/diorama.py "$PROJ" "$O/out_green.png" --glb model_el.glb $ALL --el 30 --ortho 100 --sy 0.08 $COM > "$O/out_green.log" 2>&1
python3 tools/render/diorama.py "$PROJ" "$O/out_epdm.png" --glb model_el_epdm.glb $ALL --el 30 --ortho 100 --sy 0.08 $COM > "$O/out_epdm.log" 2>&1
python3 tools/render/diorama.py "$PROJ" "$O/inside.png" --glb model_el.glb --phases foundation,floor1,porch,interior,stair,site --hide-els roof1,roof1u,lamps --el 52 --ortho 100 --sy 0.06 $COM > "$O/inside.log" 2>&1
echo SELDONE > "$O/done.txt"
