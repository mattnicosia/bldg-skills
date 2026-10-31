#!/bin/bash
# E26044 The Inn at Kirkside: model frames. One Blender at a time.
WEB=$(cd "$(dirname "$0")" && pwd); PROJ=$(dirname "$WEB"); KIT=${MCC_KIT:-$(dirname "$PROJ")/kit}
O=$WEB/model; mkdir -p "$O"; rm -f "$O/done.txt"
cd "$KIT"
COM="--glb model_el.glb --az 200 --el 34 --ortho 200 --size 1600x1200 --samples 24 --rgba --block -5,-152,172,-5,12"
ALL="--phases foundation,house,new,site"
PTS="windows:68,-97,16;glass:46,-80,18;elevator:48,-62,37;deck:50,-128,2;terrace:99,-112,10;geo:143,-74,0.3"
r() { n=$1; shift; t0=$(date +%s); python3 tools/render/diorama.py "$PROJ" "$O/$n.png" $COM "$@" > "$O/$n.log" 2>&1; echo "$n $(( $(date +%s) - t0 ))s" >> "$O/done.txt"; }
r c2_complete --color $ALL --points "$PTS"
r c0_site --phases foundation,house --highlight foundation --pit "40,-68,-15,56,-56,1.6"
r c1_today --phases foundation,house --hide-els foundation
r c3_add --phases foundation,house,new --highlight glass,elevator
r w1_windows $ALL --highlight windows
r w2_glass $ALL --highlight glass
r w3_elevator $ALL --highlight elevator
r w4_deck $ALL --highlight deck
r w5_terrace $ALL --highlight terrace
r w6_geo $ALL --highlight geo --pit "121,-97,-10.5,166,-52,1"
r w7_all $ALL --highlight windows,glass,elevator,deck,terrace,geo
echo ALLDONE >> "$O/done.txt"
