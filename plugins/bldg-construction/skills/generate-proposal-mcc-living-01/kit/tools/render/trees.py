#!/usr/bin/env python3
"""Render tree impostors for the landscape setting: each tree in Cycles on transparency, lit from
the left, saved to kit/assets/trees/tree_<n>.webp with its height in trees.json.

    python3 tools/render/trees.py [count=8]
"""
import bpy, math, os, sys, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as SC
from mathutils import Vector

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
KIT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
out = os.path.join(KIT, 'assets', 'trees'); os.makedirs(out, exist_ok=True)
meta = []
for i in range(N):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.68, 0.85, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    sd = bpy.data.lights.new('Sun', 'SUN'); sd.energy = 3.2; sd.angle = math.radians(2); sd.color = (1.0, 0.95, 0.88)
    so = bpy.data.objects.new('Sun', sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(-35))
    R = random.Random(100 + i)
    conifer = i % 3 == 2
    SC.tree_line(100 + i, cen=Vector((0, 0, 0)), count=1, rmin=0.0001, rmax=0.0002, around=(0, 0.0001), kinds=('conifer' if conifer else 'hardwood'))
    # frame it
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith(('Leaf', 'Needle')): continue
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, p)); mx = Vector(map(max, mx, p))
    h = mx.z * 1.04; wdt = max(mx.x - mn.x, mx.y - mn.y) * 1.25
    cd = bpy.data.cameras.new('C'); cd.type = 'ORTHO'; cd.ortho_scale = max(h, wdt)
    co = bpy.data.objects.new('C', cd); sc.collection.objects.link(co); sc.camera = co
    co.location = ((mn.x + mx.x) / 2, -400, h / 2); co.rotation_euler = (math.radians(90), 0, 0)
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    asp = wdt / h if wdt < h else 1
    sc.render.resolution_y = 768; sc.render.resolution_x = int(768 * min(1, wdt / h)) if wdt < h else 768
    try: sc.view_settings.view_transform = 'Standard'
    except Exception: pass
    png = os.path.join(out, f'tree_{i}.png'); sc.render.filepath = png
    bpy.ops.render.render(write_still=True)
    from PIL import Image
    im = Image.open(png); wp = png[:-4] + '.webp'; im.save(wp, 'WEBP', quality=82); os.remove(png)
    meta.append({'file': os.path.basename(wp), 'h': round(max(h, wdt) if wdt >= h else h, 1), 'w': round(min(wdt, h) if wdt < h else wdt, 1), 'conifer': conifer})
    print('tree', i, meta[-1], flush=True)
json.dump(meta, open(os.path.join(out, 'trees.json'), 'w'), indent=1)
