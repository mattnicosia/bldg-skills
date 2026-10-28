#!/usr/bin/env python3
"""Architectural model renders in Cycles: white clay, soft light, true shadows, on a plain ground.
For axonometrics, exploded assemblies and construction stages.

    python3 tools/render/clay.py <project_dir> <out.png> --phases foundation,barn,wing,details
          [--explode foundation:0,barn:18,wing:18,details:34] [--az 220 --el 30] [--ortho 120] [--size 1600x1000] [--samples 48]
"""
import bpy, math, os, sys
from mathutils import Vector
A = sys.argv
opt = lambda k, d=None: A[A.index(k) + 1] if k in A else d
proj, outp = os.path.abspath(A[1]), os.path.abspath(A[2])
PH = opt('--phases', 'foundation,barn,wing,details').split(',')
EXP = {k: float(v) for k, v in (x.split(':') for x in opt('--explode', '').split(',') if x)}
AZ, EL, ORTHO = float(opt('--az', 220)), float(opt('--el', 30)), float(opt('--ortho', 0))
W, H = map(int, opt('--size', '1600x1000').split('x')); SPP = int(opt('--samples', 48))
BG = tuple(float(v) for v in opt('--bg', '0.925,0.918,0.902').split(','))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.join(proj, opt('--glb', 'model.glb')))
def phase_of(o):
    while o is not None:
        if '[phase:' in o.name: return o.name.split('[phase:')[1].split(']')[0]
        o = o.parent
roots = {o.name.split('[phase:')[1].split(']')[0]: o for o in bpy.data.objects if '[phase:' in o.name}
for k, o in roots.items():
    if k not in PH:
        for c in [o] + list(o.children_recursive): c.hide_render = True
    o.location.z += EXP.get(k, 0)
HIDE = set(x for x in opt('--hide-mats', '').split(',') if x)
for o in bpy.data.objects:
    if o.type == 'MESH' and any(m and m.name.split('.')[0] in HIDE for m in o.data.materials): o.hide_render = True
# clay palette: white model, a few true material hints
CLAY = {'siding': (0.80, 0.79, 0.77), 'trim': (0.84, 0.83, 0.81), 'roof': (0.62, 0.63, 0.64), 'flashing': (0.66, 0.67, 0.68), 'soffit': (0.80, 0.79, 0.77),
        'frame': (0.30, 0.30, 0.30), 'concrete': (0.56, 0.55, 0.53), 'footing': (0.47, 0.46, 0.44), 'slab': (0.66, 0.65, 0.62), 'gravel': (0.40, 0.38, 0.35),
        'lumber': (0.70, 0.58, 0.42), 'deck': (0.55, 0.40, 0.29), 'membrane': (0.25, 0.25, 0.25), 'steel': (0.2, 0.2, 0.2), 'stainless': (0.7, 0.7, 0.72)}
for m in bpy.data.materials:
    if not m.node_tree: continue
    b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not b: continue
    key = m.name.split('.')[0]
    if key.startswith('glass'):
        b.inputs['Base Color'].default_value = (0.78, 0.86, 0.9, 1); b.inputs['Transmission Weight'].default_value = 0.85; b.inputs['Roughness'].default_value = 0.05; b.inputs['Metallic'].default_value = 0
        continue
    c = CLAY.get(key, (0.8, 0.79, 0.77))
    b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Metallic'].default_value = 0.15 if key in ('roof', 'flashing', 'stainless') else 0
    b.inputs['Roughness'].default_value = 0.55 if key in ('roof', 'flashing') else 0.8
# priced elements (meshes named "... [el:<name>]" by M.el in the model builder):
#   --highlight bifolds,deck   paint those Montana blue      --hide-els wingroof   leave those out
#   --ghost-els cutwall        draw those as faint glass, to see the room behind them
def el_of(o):
    return o.name.split('[el:')[1].split(']')[0] if '[el:' in o.name else None
HL = set(x for x in opt('--highlight', '').split(',') if x); HID = set(x for x in opt('--hide-els', '').split(',') if x)
GH = set(x for x in opt('--ghost-els', '').split(',') if x)
def flat(name, rgb, emit=0.0, alpha=1.0, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = 0
    if emit: b.inputs['Emission Color'].default_value = (*rgb, 1); b.inputs['Emission Strength'].default_value = emit
    if alpha < 1: b.inputs['Alpha'].default_value = alpha
    return m
blue = tuple(float(v) for v in opt('--blue', '0.0,0.0212,0.604').split(','))   # #0028CC in linear
m_hl = flat('HL', blue, emit=float(opt('--blue-emit', 0.25)), rough=0.5); m_gh = flat('GH', (0.9, 0.9, 0.9), alpha=float(opt('--ghost-alpha', 0.14)), rough=0.3)
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    e = el_of(o)
    if e is None: continue
    if e in HID: o.hide_render = True; continue
    if e in HL or e in GH:
        mm = m_hl if e in HL else m_gh
        for i in range(len(o.data.materials)): o.data.materials[i] = mm
        if e in GH: o.visible_shadow = False
# bounds of what is shown
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.type != 'MESH' or (o.hide_render and '--frame-all' not in A): continue   # --frame-all: same camera for every stage of a sequence
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, p)); mx = Vector(map(max, mx, p))
cen = (mn + mx) / 2
# ground: a shadow catcher under the lowest part, composited onto the paper color afterwards
gz = float(opt('--grade')) if opt('--grade') else mn.z - 0.02   # --grade 0 puts the ground at grade and hides what is below it
bpy.ops.mesh.primitive_plane_add(size=2000, location=(cen.x, cen.y, gz)); g = bpy.context.object; g.is_shadow_catcher = True
# light: soft sky plus a low sun from the south west
w = bpy.data.worlds.new('W'); sc.world = w
try: w.use_nodes = True
except Exception: pass
bgn = w.node_tree.nodes['Background']; bgn.inputs['Color'].default_value = (0.95, 0.95, 0.96, 1); bgn.inputs['Strength'].default_value = 0.9
sd = bpy.data.lights.new('Sun', 'SUN'); sd.energy = 2.6; sd.angle = math.radians(6); sd.color = (1.0, 0.96, 0.9)
so = bpy.data.objects.new('Sun', sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(48), 0, math.radians(-(225 + 180)))
# camera: axonometric (orthographic) unless --ortho 0
cd = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam); sc.camera = cam
a, e = math.radians(AZ), math.radians(EL)
d = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))   # AZ: compass bearing from the model to the camera
look = cen.copy(); look.z = mn.z + (mx.z - mn.z) * float(opt('--look', 0.45))
cam.location = look + d * 400; cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
if ORTHO: cd.type = 'ORTHO'; cd.ortho_scale = ORTHO
else: cd.lens = float(opt('--lens', 120))
cd.clip_end = 3000
cd.shift_x = float(opt('--sx', 0)); cd.shift_y = float(opt('--sy', 0))
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SPP; sc.cycles.use_denoising = True
if opt('--points'):   # --points "name:x,y,z;..." in model feet: write their pixel positions beside the image, for callouts
    import json
    from bpy_extras.object_utils import world_to_camera_view
    sc.render.resolution_x, sc.render.resolution_y = W, H; bpy.context.view_layer.update()
    pts = {}
    for item in opt('--points').split(';'):
        nm, xyz = item.split(':'); v = world_to_camera_view(sc, cam, Vector([float(t) for t in xyz.split(',')]))
        pts[nm] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
    json.dump(pts, open(outp + '.points.json', 'w'), indent=1); print('points', pts)
sc.render.film_transparent = True; sc.render.resolution_x, sc.render.resolution_y = W, H
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium Contrast'
except Exception: pass
tmp = outp + '.rgba.png'; sc.render.filepath = tmp; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True)
from PIL import Image
im = Image.open(tmp).convert('RGBA'); bg = Image.new('RGBA', im.size, tuple(int(v * 255) for v in BG) + (255,))
(im.save(outp) if '--rgba' in A else Image.alpha_composite(bg, im).convert('RGB').save(outp, quality=92)); os.remove(tmp)
print('wrote', outp)
