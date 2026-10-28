#!/bin/bash
# after render_model.sh: refresh the marker points, then render the dusk frames. Chain it:  nohup bash -c "bash web/render_model.sh; bash web/after_frames.sh" > /dev/null 2>&1 &
WEB=$(cd "$(dirname "$0")" && pwd); P=$(dirname "$WEB"); K=${MCC_KIT:-$(dirname "$P")/kit}; mkdir -p $P/web/draft $P/hero
while ! grep -q ALLDONE $P/web/model/done.txt 2>/dev/null; do sleep 20; done
cd $K
PTS=$(grep '^PTS=' $P/web/render_model.sh | sed 's/^PTS=//; s/"//g')
python3 tools/render/diorama.py $P $P/web/draft/pts.png --glb model_el.glb --az 320 --el 30 --ortho 104 --size 1600x1200 --samples 1 --rgba --block -24,-13,62,46,10.5 --phases foundation,floor1,porch,upper,upperwalls,roof,interior,stair,site --color --points "$PTS" > $P/web/draft/pts.log 2>&1
cp $P/web/draft/pts.png.points.json $P/web/model/c3_exterior.png.points.json
python3 tools/render/hero.py $P --only dusk --size 1600x900 > $P/hero/dusk.log 2>&1
python3 tools/render/hero.py $P --only dusk_p > $P/hero/dusk_p.log 2>&1
echo HERODONE >> $P/hero/dusk.log
