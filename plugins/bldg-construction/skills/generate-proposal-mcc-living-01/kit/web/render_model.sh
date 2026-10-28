#!/bin/bash
# Model sequence for the website format: the building on a block of land, one fixed camera.
# Build stages in color, priced elements in white clay with Montana blue. One Blender at a time (about 100 s a frame on 2 cores).
# Run in the background:  nohup bash web/render_model.sh > /dev/null 2>&1 &   then watch web/model/done.txt for ALLDONE.
# JOB: the camera, the land block, the excavation pits, the element points and the frame list below are Cooper Barn values.
WEB=$(cd "$(dirname "$0")" && pwd); PROJ=$(dirname "$WEB"); KIT=${MCC_KIT:-$(dirname "$PROJ")/kit}
O=$WEB/model; mkdir -p "$O"; rm -f "$O/done.txt"
cd "$KIT"
COM="--glb model_el.glb --az 150 --el 32 --ortho 104 --size 1600x1200 --samples 24 --rgba --block -9,-6,62,36,10.5"
ALL="--phases foundation,barn,wing,interior,details"
CUT="--hide-els wingroof,deck --ghost-els cutwall"
PIT="-3,-3,-4.7,43,33,1;40,-1,-9.7,59,31,1"
PTS="bifolds:20,0,6;deck:47.7,15.7,11;bar:47.6,24,2.5;canopy:20,-1.5,13.6;cupola:20,15,28;stove:56.75,15,13"
r() { n=$1; shift; t0=$(date +%s); python3 tools/render/diorama.py "$PROJ" "$O/$n.png" $COM "$@" > "$O/$n.log" 2>&1; echo "$n $(( $(date +%s) - t0 ))s" >> "$O/done.txt"; }
r c3_exterior --color $ALL --points "$PTS"
r c0_site --color --phases foundation --hide-mats lumber,slab,gravel --pit "$PIT"
r c0b_backfill --color --phases foundation --hide-mats slab
r c1_workshop --color --phases foundation,barn
r c2_lounge --color --phases foundation,barn,wing,interior $CUT
r w1_bifolds $ALL --highlight bifolds
r w2_deck $ALL --highlight deck
r w3_bar $ALL --highlight bar $CUT
r w4_canopy $ALL --highlight canopy
r w5_cupola $ALL --highlight cupola
r w6_stove $ALL --highlight stove $CUT
r w7_all $ALL --highlight bifolds,deck,bar,canopy,cupola,stove
echo ALLDONE >> "$O/done.txt"
