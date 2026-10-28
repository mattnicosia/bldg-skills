#!/bin/bash
# Pool House sequence: on its block of land, one camera. Build stages in color, priced elements in white with Montana blue.
cd /home/claude/pres/kit
O=../ph3d/frames
COM="--glb model_el.glb --az 215 --el 30 --ortho 88 --size 1600x1200 --samples 24 --rgba --block -10,-8,26,44,8"
ALL="--phases site,foundation,first,second,roof,interior,details"
CUT="--hide-els cutwall,west"
PIT="-0.6,-0.6,-5.3,16.6,35.6,1"
PTS="bifold:8,-0.4,4.2;win:8,-0.3,14.6;roof:4,19,23.6;trim:-0.5,-0.5,9.7;stair:2.3,29.5,7.6;bar:6.4,13.1,3.4"
r() { n=$1; shift; t0=$(date +%s); python3 tools/render/diorama.py ../ph3d $O/$n.png $COM "$@" > $O/$n.log 2>&1; echo "$n $(( $(date +%s) - t0 ))s" >> $O/done.txt; }
r p_c3_exterior --color $ALL --points "$PTS"
r p_c0_site --color --phases site,foundation --hide-mats slab,gravel,lumber --pit "$PIT"
r p_c0b_backfill --color --phases site,foundation
r p_c1_first --color --phases site,foundation,first
r p_c2_second --color --phases site,foundation,first,second
r p_w1_bifold $ALL --highlight bifold
r p_w2_win $ALL --highlight win
r p_w3_roof $ALL --highlight roof
r p_w4_trim $ALL --highlight trim
r p_w5_stair $ALL --highlight stair --hide-els cutwall,west,floor2
r p_w6_bar $ALL --highlight bar $CUT
r p_w7_all $ALL --highlight bifold,win,roof,trim,stair,bar
echo ALLDONE >> $O/done.txt
