#!/bin/bash
# Model sequence for the website format: the building on a block of land, one fixed camera.
# Build stages in color, priced elements in white clay with Montana blue. One Blender at a time (about 100 s a frame on 2 cores).
# Run in the background with the dusk chained after:  nohup bash -c "bash web/render_model.sh; bash web/after_frames.sh" > /dev/null 2>&1 &   then watch web/model/done.txt for ALLDONE. Per-frame options come first, so a frame can override --samples.
# JOB: E26049 1004 Old Albany Post Rd. Camera from the northwest (the Blejer SD-12 side), the crawl space pit, the element points.
WEB=$(cd "$(dirname "$0")" && pwd); PROJ=$(dirname "$WEB"); KIT=${MCC_KIT:-$(dirname "$PROJ")/kit}
O=$WEB/model; mkdir -p "$O"; rm -f "$O/done.txt"
cd "$KIT"
COM="--glb model_el.glb --az 320 --el 30 --ortho 104 --size 1600x1200 --samples 24 --rgba --block -24,-13,62,46,10.5"
ALL="--phases foundation,floor1,porch,upper,upperwalls,roof,interior,stair,site"
PIT="-1.6,-8,-5.6,58,36,1"
PTS="windows:27,32.2,7;cantilever:24.3,38,12.8;greenroof:-6,24,13.6;siding:45,32.6,12.4;stair:24,-5.6,8;porch:-8.5,21.5,2.2"
r() { n=$1; shift; t0=$(date +%s); python3 tools/render/diorama.py "$PROJ" "$O/$n.png" "$@" $COM > "$O/$n.log" 2>&1; echo "$n $(( $(date +%s) - t0 ))s" >> "$O/done.txt"; }
r c3_exterior --color $ALL --points "$PTS"
r c0_site --color --phases foundation --hide-mats lumber,slab,gravel,subfloor --pit "$PIT"
r c0b_backfill --color --phases foundation --hide-mats slab
r c1_first --color --phases foundation,floor1,porch,interior
r c2_upper --color --phases foundation,floor1,porch,interior,stair,upper,upperwalls
r w1_windows $ALL --highlight windows
r w2_cantilever --phases foundation,floor1,porch,upper,roof,interior,site --hide-els boxshell --highlight cantilever
r w3_greenroof $ALL --highlight greenroof
r w4_siding $ALL --highlight siding,boxsiding
r w5_stair --phases foundation,floor1,porch,interior,stair,site --hide-els roof1,roof1u,lamps,partitions --highlight stair
r w6_porch $ALL --highlight porch
r w7_all --phases foundation,floor1,porch,upper,upperwalls,roof,interior,stair,site,xray --hide-els boxshell,roof1u,boxsiding --ghost-els boxghost --ghost-alpha 0.18 --samples 48 --highlight windows,cantilever,greenroof,stair,porch   # box as a plain x-ray shell, roof and floor off, so the steel and stair read; siding left white
echo ALLDONE >> "$O/done.txt"
