#!/usr/bin/env python3
"""Render a forest edge in Cycles on transparency, for the backdrop ring in the stills.
    python3 tools/render/forest.py   ->  kit/assets/trees/forest_<n>.png
"""
import bpy, math, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as SC
from mathutils import Vector
KIT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
out = os.path.join(KIT, 'assets', 'trees'); os.makedirs(out, exist_ok=True)
for n, seed in enumerate([31]):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.65, 0.85, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.55
    sd = bpy.data.lights.new('Sun', 'SUN'); sd.energy = 3.0; sd.angle = math.radians(2); sd.color = (1.0, 0.95, 0.88)
    so = bpy.data.objects.new('Sun', sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(58), 0, math.radians(-30))
    R = random.Random(seed)
    # a 420 ft strip of forest edge, deeper at the back, with understory in front
    SC.tree_line(seed, cen=Vector((0, 0, 0)), count=0)
    import scene
    for i in range(44):
        x = -210 + i * 9.6 + R.uniform(-3, 3); y = R.uniform(0, 70); h = R.uniform(50, 88)
        scene.TREE(R.choice(['hardwood', 'hardwood', 'conifer']), x, y, h, low=True)
    for i in range(48):
        scene.TREE('hardwood', -210 + i * 8.8 + R.uniform(-3, 3), R.uniform(-14, -4), R.uniform(14, 28), low=True)
    cd = bpy.data.cameras.new('C'); cd.type = 'ORTHO'; cd.ortho_scale = 420
    co = bpy.data.objects.new('C', cd); sc.collection.objects.link(co); sc.camera = co
    sc.render.resolution_x, sc.render.resolution_y = 4096, 1150
    co.location = (0, -500, 420 * 1150 / 4096 / 2 - 0.5); co.rotation_euler = (math.radians(90), 0, 0)
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 28; sc.cycles.use_denoising = True; sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'
    sc.render.filepath = os.path.join(out, f'forest_{n}.png'); bpy.ops.render.render(write_still=True)
    print('forest', n, flush=True)
