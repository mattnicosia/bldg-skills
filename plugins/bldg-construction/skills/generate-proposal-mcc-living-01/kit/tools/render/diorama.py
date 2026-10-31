#!/usr/bin/env python3
"""Site model renders in Cycles: the building standing on a block of land cut to show the soil, in white (clay)
or in finished colors. One fixed camera for a whole sequence, so build stages and highlighted elements crossfade.

    python3 tools/render/diorama.py <project_dir> <out.png> --glb model_el.glb --phases foundation,barn,wing,interior,details
        [--color] [--block x0,y0,x1,y1,depth] [--pit "x0,y0,z0,x1,y1,z1;..."] [--hide-mats lumber,slab]
        [--highlight bifolds] [--hide-els wingroof,deck] [--ghost-els cutwall]
        [--az 150 --el 32 --ortho 100 --look 0.4] [--size 1600x1200] [--samples 24] [--rgba] [--points "name:x,y,z;..."]

Coordinates are Blender feet (x east, y north, z up, grade at z 0). The block is always part of the framing, so
every frame of a sequence shares one camera. --pit boxes are dug out of the block (an excavation).
"""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector
A = sys.argv
opt = lambda k, d=None: A[A.index(k) + 1] if k in A else d
proj, outp = os.path.abspath(A[1]), os.path.abspath(A[2])
P = json.load(open(os.path.join(proj, 'project.json')))
PH = opt('--phases', 'foundation,barn,wing,interior,details').split(',')
AZ, EL, ORTHO = float(opt('--az', 150)), float(opt('--el', 32)), float(opt('--ortho', 100))
W, H = map(int, opt('--size', '1600x1200').split('x')); SPP = int(opt('--samples', 24))
COLOR = '--color' in A

def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1,)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.join(proj, opt('--glb', 'model.glb')))
BLD = [o for o in bpy.data.objects if o.type == 'MESH']
roots = {o.name.split('[phase:')[1].split(']')[0]: o for o in bpy.data.objects if '[phase:' in o.name}
for k, o in roots.items():
    if k not in PH:
        for c in [o] + list(o.children_recursive): c.hide_render = True
HIDE = set(x for x in opt('--hide-mats', '').split(',') if x)
for o in BLD:
    if any(m and m.name.split('.')[0] in HIDE for m in o.data.materials): o.hide_render = True

# ------------------------------------------------------------------ materials
def tree_of(m):
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); return nt, nt.nodes, nt.links
def coords(n, L, scale=(1, 1, 1)):
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = scale
    L.new(tc.outputs['Object'], mp.inputs['Vector']); return mp.outputs['Vector']
def noise(n, L, vec, scale, detail=4, rough=0.5):
    t = n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value = scale; t.inputs['Detail'].default_value = detail; t.inputs['Roughness'].default_value = rough
    L.new(vec, t.inputs['Vector']); return t.outputs['Fac']
def vary(n, L, color, fac, amt):
    mr = n.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1 - amt; mr.inputs['To Max'].default_value = 1 + amt
    L.new(fac, mr.inputs['Value'])
    mul = n.new('ShaderNodeVectorMath'); mul.operation = 'SCALE'; mul.inputs[0].default_value = color[:3]
    L.new(mr.outputs['Result'], mul.inputs['Scale']); return mul.outputs['Vector']
def surface(m, color, rough=0.6, metal=0.0, cvar=0.0, cscale=0.5, bump=0.0, bscale=4.0, grain=None, coat=0.0):
    nt, n, L = tree_of(m)
    out = n.new('ShaderNodeOutputMaterial'); b = n.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if coat: b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = 0.08
    v = coords(n, L)
    if grain:
        vg = coords(n, L, {'x': (0.15, 3, 3), 'y': (3, 0.15, 3), 'z': (3, 3, 0.15)}[grain])
        wv = n.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 2.2; wv.inputs['Distortion'].default_value = 6; L.new(vg, wv.inputs['Vector'])
        L.new(vary(n, L, color, wv.outputs['Fac'], 0.18), b.inputs['Base Color'])
    elif cvar: L.new(vary(n, L, color, noise(n, L, v, cscale, 6, 0.6), cvar), b.inputs['Base Color'])
    else: b.inputs['Base Color'].default_value = color
    if bump:
        bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.02
        L.new(noise(n, L, v, bscale, 8, 0.55), bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    L.new(b.outputs[0], out.inputs['Surface']); return b
def glass(m):
    nt, n, L = tree_of(m)
    out = n.new('ShaderNodeOutputMaterial'); b = n.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (0.80, 0.85, 0.84, 1); b.inputs['Roughness'].default_value = 0.0
    b.inputs['IOR'].default_value = 1.5; b.inputs['Transmission Weight'].default_value = 1.0
    lp = n.new('ShaderNodeLightPath'); tp = n.new('ShaderNodeBsdfTransparent'); mx_ = n.new('ShaderNodeMixShader')
    L.new(lp.outputs['Is Shadow Ray'], mx_.inputs['Fac']); L.new(b.outputs[0], mx_.inputs[1]); L.new(tp.outputs[0], mx_.inputs[2])
    L.new(mx_.outputs[0], out.inputs['Surface'])
PAL = P.get('model', {}).get('palette', {})
col = lambda k, d: lin(PAL.get(k, d))
RECIPE = {   # finished colors, as the hero renders
    'siding': lambda m: surface(m, col('siding', '#605a53'), 0.6, cvar=0.05, cscale=0.35),
    'trim': lambda m: surface(m, col('trim', '#5a534b'), 0.55, cvar=0.04),
    'soffit': lambda m: surface(m, col('soffit', '#4a423b'), 0.7),
    'frame': lambda m: surface(m, col('frame', '#3a3129'), 0.42),
    'roof': lambda m: surface(m, col('roof', '#aeaba4'), float(PAL.get('roof_rough', 0.42)), metal=float(PAL.get('roof_metal', 0.38)), cvar=0.04, cscale=0.25),   # v1.15: palette roof (asphalt shingle on E26044)
    'flashing': lambda m: surface(m, col('flashing', '#7f7f7c'), 0.46, metal=0.7),
    'concrete': lambda m: surface(m, col('concrete', '#a8a59d'), 0.92, cvar=0.08, cscale=1.2, bump=0.25, bscale=6),
    'footing': lambda m: surface(m, lin('#8c8981'), 0.95, cvar=0.06, cscale=1.4),
    'slab': lambda m: surface(m, lin('#9f9b93'), 0.32, cvar=0.08, cscale=0.25),
    'gravel': lambda m: surface(m, lin('#8f8a80'), 1.0, cvar=0.35, cscale=40, bump=0.6, bscale=60),
    'lumber': lambda m: surface(m, lin('#b89a72'), 0.85, grain='x'),
    'deck': lambda m: surface(m, col('deck', '#6e4630'), 0.6, grain='y'),
    'membrane': lambda m: surface(m, col('membrane', '#2a2a2a'), 0.9),
    'sedum': lambda m: surface(m, col('sedum', '#6f7f43'), 1.0, cvar=0.28, cscale=6, bump=0.5, bscale=30),   # green roof trays (v1.5)
    'stone': lambda m: surface(m, col('stone', '#9b968c'), 0.85, cvar=0.10, cscale=1.5, bump=0.15, bscale=5),
    'steel': lambda m: surface(m, lin('#1e1e1e'), 0.45, metal=0.6),
    'stainless': lambda m: surface(m, lin('#cfd1d3'), 0.2, metal=1.0),
    'gyp': lambda m: surface(m, lin('#e9e6df'), 0.9),
    'timber': lambda m: surface(m, lin('#7a5a3e'), 0.7, grain='x'),
    'walnut': lambda m: surface(m, lin('#4a3326'), 0.45, grain='x', coat=0.3),
    'plank': lambda m: surface(m, lin('#9c7652'), 0.5, grain='x', coat=0.2),
    'machine': lambda m: surface(m, lin('#5c6066'), 0.42, metal=0.3),
    'copper': lambda m: surface(m, (0.86, 0.48, 0.30, 1), 0.26, metal=1.0),
    'fabric': lambda m: surface(m, lin('#3d4249'), 1.0),
    'lamp': lambda m: surface(m, lin('#efe7d6'), 0.6),
    'glass': glass,
}
CLAY = {'siding': (0.80, 0.79, 0.77), 'trim': (0.84, 0.83, 0.81), 'roof': (0.62, 0.63, 0.64), 'flashing': (0.66, 0.67, 0.68), 'soffit': (0.80, 0.79, 0.77),
        'frame': (0.30, 0.30, 0.30), 'concrete': (0.56, 0.55, 0.53), 'footing': (0.47, 0.46, 0.44), 'slab': (0.66, 0.65, 0.62), 'gravel': (0.40, 0.38, 0.35),
        'lumber': (0.70, 0.58, 0.42), 'deck': (0.78, 0.76, 0.73), 'membrane': (0.45, 0.45, 0.45), 'sedum': (0.74, 0.74, 0.72), 'stone': (0.72, 0.71, 0.69), 'steel': (0.2, 0.2, 0.2), 'stainless': (0.7, 0.7, 0.72)}
for m in list(bpy.data.materials):
    key = m.name.split('.')[0]
    if COLOR:
        if key in RECIPE: RECIPE[key](m)
        continue
    if not m.node_tree: continue
    b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not b: continue
    if key.startswith('glass'):
        b.inputs['Base Color'].default_value = (0.78, 0.86, 0.9, 1); b.inputs['Transmission Weight'].default_value = 0.85; b.inputs['Roughness'].default_value = 0.05; b.inputs['Metallic'].default_value = 0
        continue
    c = CLAY.get(key, (0.8, 0.79, 0.77))
    b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Metallic'].default_value = 0.15 if key in ('roof', 'flashing', 'stainless') else 0
    b.inputs['Roughness'].default_value = 0.55 if key in ('roof', 'flashing') else 0.8

# ------------------------------------------------------------------ priced elements: blue, hidden or ghosted
def el_of(o): return o.name.split('[el:')[1].split(']')[0] if '[el:' in o.name else None
HL = set(x for x in opt('--highlight', '').split(',') if x); HID = set(x for x in opt('--hide-els', '').split(',') if x)
GH = set(x for x in opt('--ghost-els', '').split(',') if x)
def flat(name, rgb, emit=0.0, alpha=1.0, rough=0.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb[:3], 1); b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (*rgb[:3], 1); b.inputs['Emission Strength'].default_value = emit
    if alpha < 1: b.inputs['Alpha'].default_value = alpha
    return m
m_hl = flat('HL', (0.0, 0.0212, 0.604), emit=0.25, rough=0.5); m_gh = flat('GH', (0.9, 0.9, 0.9), alpha=float(opt('--ghost-alpha', 0.14)), rough=0.3)
for o in BLD:   # a part can carry several tags, 'win+west': hidden or ghosted if any tag says so, blue if any tag is highlighted
    e = el_of(o)
    if e is None: continue
    tags = set(e.split('+'))
    if tags & HID: o.hide_render = True; continue
    if tags & HL or tags & GH:
        hl = bool(tags & HL)
        for i in range(len(o.data.materials)): o.data.materials[i] = m_hl if hl else m_gh
        if not hl: o.visible_shadow = False

# ------------------------------------------------------------------ the block of land: lawn, topsoil, subsoil, dug out where --pit says
def box(name, x0, y0, z0, x1, y1, z1, mat=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    o.scale = (x1 - x0, y1 - y0, z1 - z0); o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    if mat: me.materials.append(mat)
    return o
bx0, by0, bx1, by1, depth = [float(v) for v in opt('--block', '-10,-11,66,41,11').split(',')]
def landmat(name, color, white, cvar=0.0, cscale=0.5, bump=0.0, bscale=4):
    m = bpy.data.materials.new(name)
    surface(m, lin(color) if COLOR else (*white, 1), 0.95, cvar=cvar if COLOR else 0.0, cscale=cscale, bump=bump if COLOR else 0.0, bscale=bscale)
    return m
m_lawn = landmat('lawn', '#6c8448', (0.86, 0.865, 0.84), cvar=0.18, cscale=3, bump=0.3, bscale=40)
m_top = landmat('topsoil', '#4d3b2c', (0.74, 0.73, 0.71), cvar=0.15, cscale=2)
m_sub = landmat('subsoil', '#8b7155', (0.80, 0.79, 0.77), cvar=0.12, cscale=1.2, bump=0.2, bscale=8)
LAND = [box('lawn', bx0, by0, -0.3, bx1, by1, 0.0, m_lawn), box('topsoil', bx0, by0, -1.5, bx1, by1, -0.3, m_top), box('subsoil', bx0, by0, -depth, bx1, by1, -1.5, m_sub)]
pits = [tuple(float(v) for v in p.split(',')) for p in opt('--pit', '').split(';') if p]
for k, (x0, y0, z0, x1, y1, z1) in enumerate(pits):
    cut = box(f'pit{k}', x0, y0, z0, x1, y1, z1); cut.hide_render = True; cut.display_type = 'WIRE'
    for o in LAND:
        md = o.modifiers.new(f'pit{k}', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut
        try: md.solver = 'EXACT'
        except Exception: pass

# ------------------------------------------------------------------ framing: building plus block, the same for every frame
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
bpy.context.view_layer.update()
for o in BLD + LAND:
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, p)); mx = Vector(map(max, mx, p))
cen = (mn + mx) / 2
bpy.ops.mesh.primitive_plane_add(size=2000, location=(cen.x, cen.y, -depth - 0.02)); g = bpy.context.object; g.is_shadow_catcher = True
w = bpy.data.worlds.new('W'); sc.world = w
try: w.use_nodes = True
except Exception: pass
bgn = w.node_tree.nodes['Background']; bgn.inputs['Color'].default_value = (0.95, 0.95, 0.96, 1); bgn.inputs['Strength'].default_value = float(opt('--sky', 0.9))
sd = bpy.data.lights.new('Sun', 'SUN'); sd.energy = float(opt('--sun', 2.6)); sd.angle = math.radians(6); sd.color = (1.0, 0.96, 0.9)
so = bpy.data.objects.new('Sun', sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(48), 0, math.radians(-(225 + 180)))
cd = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam); sc.camera = cam
a, e = math.radians(AZ), math.radians(EL)
d = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
look = cen.copy(); look.z = mn.z + (mx.z - mn.z) * float(opt('--look', 0.42))
if opt('--target'): look = Vector([float(t) for t in opt('--target').split(',')])   # probe: aim at a point (x east, y north, z up)
cam.location = look + d * 400; cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
cd.type = 'ORTHO'; cd.ortho_scale = ORTHO; cd.clip_end = 3000
cd.shift_x = float(opt('--sx', 0)); cd.shift_y = float(opt('--sy', 0))
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SPP; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = W, H
if opt('--points'):
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update(); pts = {}
    for item in opt('--points').split(';'):
        nm, xyz = item.split(':'); v = world_to_camera_view(sc, cam, Vector([float(t) for t in xyz.split(',')]))
        pts[nm] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
    json.dump(pts, open(outp + '.points.json', 'w'), indent=1); print('points', pts)
sc.render.film_transparent = True
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium Contrast'
except Exception: pass
tmp = outp + '.rgba.png'; sc.render.filepath = tmp; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True)
from PIL import Image
im = Image.open(tmp).convert('RGBA')
if '--rgba' in A: im.save(outp)
else:
    bg = Image.new('RGBA', im.size, (244, 245, 248, 255)); Image.alpha_composite(bg, im).convert('RGB').save(outp, quality=92)
os.remove(tmp); print('wrote', outp)
