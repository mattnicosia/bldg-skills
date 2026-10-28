#!/usr/bin/env python3
"""Photographic hero frames in Cycles: eye level, level camera with lens shift (verticals stay vertical),
real trees around a clearing, dappled light from trees out of frame, a grass lawn, a cloud sky,
finished materials and a lit interior seen through the glass.

    python3 tools/render/hero.py <project_dir> [--only front,se,dusk] [--size 1920x1080] [--samples 160]
          [--draft] [--out <dir>] [--no-grass] [--seed 7]

Shots, sun and tree stands come from project.json model.render.heroes (see the README); coordinates are
Blender feet (x east, y north, z up) with the building as modeled. Writes <out>/hero_<id>.png (raw)
and hero_<id>.jpg (graded).
"""
import bpy, math, os, sys, json, time, random
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ez

A = sys.argv
opt = lambda k, d=None: A[A.index(k) + 1] if k in A else d
proj = os.path.abspath(A[1]); P = json.load(open(os.path.join(proj, 'project.json')))
HC = P.get('model', {}).get('render', {}).get('heroes', {})
for kv in [A[i + 1] for i, x in enumerate(A) if x == '--set']:   # --set sky=0.05 overrides a heroes value for this run
    k_, v_ = kv.split('='); HC[k_] = json.loads(v_)
ONLY = set(opt('--only', '').split(',')) - {''}
W, H = map(int, opt('--size', '1920x1080').split('x'))
DRAFT = '--draft' in A
SPP = int(opt('--samples', 24 if DRAFT else 160))
OUT = os.path.abspath(opt('--out', os.path.join(proj, 'hero')))
SEED = int(opt('--seed', HC.get('seed', 7)))
os.makedirs(OUT, exist_ok=True)
t0 = time.time()

def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1,)

# ------------------------------------------------------------------ scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=os.path.join(proj, 'model.glb'))
HIDE_PH = set(HC.get('hide_phases', ['xray']))   # model phases kept out of photographic frames (x-ray shells made for diagram frames)
def _ph(o):
    while o is not None:
        if '[phase:' in o.name: return o.name.split('[phase:')[1].split(']')[0]
        o = o.parent
for o in [o for o in bpy.data.objects if o.type == 'MESH' and _ph(o) in HIDE_PH]: bpy.data.objects.remove(o, do_unlink=True)
BLD = [o for o in bpy.data.objects if o.type == 'MESH']
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
for o in BLD:
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, p)); mx = Vector(map(max, mx, p))
CEN = (mn + mx) / 2
print('building', [round(v, 1) for v in mn], [round(v, 1) for v in mx], flush=True)

# ------------------------------------------------------------------ materials
def tree_of(m):
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    return nt, nt.nodes, nt.links

def coords(n, L, scale=(1, 1, 1)):
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = scale
    L.new(tc.outputs['Object'], mp.inputs['Vector']); return mp.outputs['Vector']

def noise(n, L, vec, scale, detail=4, rough=0.5):
    t = n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value = scale; t.inputs['Detail'].default_value = detail; t.inputs['Roughness'].default_value = rough
    L.new(vec, t.inputs['Vector']); return t.outputs['Fac']

def vary(n, L, color, fac, amt):
    """color scaled by 1 +/- amt following fac"""
    mr = n.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1 - amt; mr.inputs['To Max'].default_value = 1 + amt
    L.new(fac, mr.inputs['Value'])
    mul = n.new('ShaderNodeVectorMath'); mul.operation = 'SCALE'; mul.inputs[0].default_value = color[:3]
    L.new(mr.outputs['Result'], mul.inputs['Scale']); return mul.outputs['Vector']

def surface(m, color, rough=0.6, metal=0.0, spec=0.5, cvar=0.0, cscale=0.5, bump=0.0, bscale=4.0, bmap=(1, 1, 1), rvar=0.0, coat=0.0, grain=None):
    nt, n, L = tree_of(m)
    out = n.new('ShaderNodeOutputMaterial'); b = n.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    try: b.inputs['Specular IOR Level'].default_value = spec
    except Exception: pass
    if coat:
        b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = 0.08
    v = coords(n, L)
    if grain:   # wood: stretched wave grain along an axis
        sc_ = {'x': (0.15, 3, 3), 'y': (3, 0.15, 3), 'z': (3, 3, 0.15)}[grain]
        vg = coords(n, L, sc_)
        wv = n.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 2.2; wv.inputs['Distortion'].default_value = 6; wv.inputs['Detail'].default_value = 3
        L.new(vg, wv.inputs['Vector'])
        L.new(vary(n, L, color, wv.outputs['Fac'], 0.18), b.inputs['Base Color'])
    elif cvar:
        L.new(vary(n, L, color, noise(n, L, v, cscale, 6, 0.6), cvar), b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = color
    if rvar:
        mr = n.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = rough - rvar; mr.inputs['To Max'].default_value = rough + rvar
        L.new(noise(n, L, v, cscale * 1.7, 5), mr.inputs['Value']); L.new(mr.outputs['Result'], b.inputs['Roughness'])
    if bump:
        bv = coords(n, L, bmap)
        bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.02
        L.new(noise(n, L, bv, bscale, 8, 0.55), bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    L.new(b.outputs[0], out.inputs['Surface'])
    return b

def glass(m):
    nt, n, L = tree_of(m)
    out = n.new('ShaderNodeOutputMaterial'); b = n.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = tuple(HC.get('glass_tint', (0.80, 0.85, 0.84))) + (1,); b.inputs['Roughness'].default_value = 0.0
    b.inputs['IOR'].default_value = 1.5; b.inputs['Transmission Weight'].default_value = HC.get('glass_transmission', 1.0)
    # sunlight passes the glass into the room (shadow rays see clear glass), so the interior is lit by day
    lp = n.new('ShaderNodeLightPath'); tp = n.new('ShaderNodeBsdfTransparent'); mxs = n.new('ShaderNodeMixShader')
    L.new(lp.outputs['Is Shadow Ray'], mxs.inputs['Fac']); L.new(b.outputs[0], mxs.inputs[1]); L.new(tp.outputs[0], mxs.inputs[2])
    L.new(mxs.outputs[0], out.inputs['Surface'])

LAMPS = []
def lamp(m):
    nt, n, L = tree_of(m)
    out = n.new('ShaderNodeOutputMaterial'); e = n.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (1.0, 0.72, 0.42, 1); e.inputs['Strength'].default_value = 0.0
    d = n.new('ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value = (0.9, 0.85, 0.75, 1)
    ad = n.new('ShaderNodeAddShader'); L.new(e.outputs[0], ad.inputs[0]); L.new(d.outputs[0], ad.inputs[1]); L.new(ad.outputs[0], out.inputs['Surface'])
    LAMPS.append(e)

PAL = P.get('model', {}).get('palette', {})
def col(k, d): return lin(PAL.get(k, d))
RECIPE = {
    'siding':   lambda m: surface(m, col('siding', '#605a53'), 0.6, spec=0.45, cvar=0.05, cscale=0.35, bump=0.06, bscale=9, bmap=(1, 1, 0.12), rvar=0.08),
    'trim':     lambda m: surface(m, col('trim', '#5a534b'), 0.55, spec=0.45, cvar=0.04, cscale=0.4, bump=0.03, bscale=8, rvar=0.06),
    'soffit':   lambda m: surface(m, col('soffit', '#4a423b'), 0.7, cvar=0.04),
    'frame':    lambda m: surface(m, col('frame', '#3a3129'), 0.42, spec=0.5, cvar=0.03),
    'roof':     lambda m: surface(m, col('roof_finish', '#aeaba4'), HC.get('roof_rough', 0.42), metal=HC.get('roof_metal', 0.38), cvar=0.04, cscale=0.25, bump=0.12, bscale=1.6, bmap=(1.0, 0.08, 0.08), rvar=0.1),
    'flashing': lambda m: surface(m, col('flashing', '#7f7f7c'), 0.46, metal=0.7, rvar=0.06),
    'concrete': lambda m: surface(m, col('concrete', '#a8a59d'), 0.92, cvar=0.08, cscale=1.2, bump=0.25, bscale=6),
    'footing':  lambda m: surface(m, col('footing', '#7f7c76'), 0.95),
    'slab':     lambda m: surface(m, col('slab', '#9f9b93'), 0.28, cvar=0.1, cscale=0.25, rvar=0.08, coat=0.0),
    'deck':     lambda m: surface(m, col('deck', '#6e4630'), 0.6, grain='y'),
    'membrane': lambda m: surface(m, col('membrane', '#2a2a2a'), 0.9),
    'sedum':    lambda m: surface(m, col('sedum', '#6f7f43'), 1.0, cvar=0.28, cscale=6, bump=0.5, bscale=30),   # green roof trays (v1.5)
    'stone':    lambda m: surface(m, col('stone', '#9b968c'), 0.85, cvar=0.10, cscale=1.5, bump=0.15, bscale=5),
    'steel':    lambda m: surface(m, col('steel', '#1e1e1e'), 0.45, metal=0.6),
    'stainless': lambda m: surface(m, col('stainless', '#cfd1d3'), 0.2, metal=1.0, rvar=0.05),
    'gyp':      lambda m: surface(m, col('gyp', '#e9e6df'), 0.9, cvar=0.02),
    'timber':   lambda m: surface(m, col('timber', '#7a5a3e'), 0.7, grain='x'),
    'walnut':   lambda m: surface(m, col('walnut', '#4a3326'), 0.45, grain='x', coat=0.3),
    'plank':    lambda m: surface(m, col('plank', '#9c7652'), 0.5, grain='x', coat=0.2),
    'machine':  lambda m: surface(m, col('machine', '#5c6066'), 0.42, metal=0.3),
    'copper':   lambda m: surface(m, (0.86, 0.48, 0.30, 1), 0.26, metal=1.0, rvar=0.08, cvar=0.08),
    'fabric':   lambda m: surface(m, col('fabric', '#3d4249'), 1.0, spec=0.2, cvar=0.04, cscale=8),
    'lumber':   lambda m: surface(m, col('lumber', '#b89a72'), 0.85),
    'gravel':   lambda m: surface(m, col('gravel', '#8a857c'), 1.0),
    'glass':    glass,
    'lamp':     lamp,
}
for m in list(bpy.data.materials):
    k = m.name.split('.')[0]
    if k in RECIPE: RECIPE[k](m)
for o in BLD:   # the GLB comes in flat shaded per face already; keep hard edges
    o.visible_shadow = True

# ------------------------------------------------------------------ world: physical sky with a cloud layer for the camera
SUN_AZ, SUN_EL = HC.get('sun_az', 235), HC.get('sun_el', 26)
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
nt = w.node_tree; n = nt.nodes; L = nt.links; n.clear()
sky = n.new('ShaderNodeTexSky')
for t in ('MULTIPLE_SCATTERING', 'NISHITA'):
    try: sky.sky_type = t; break
    except Exception: pass
sky.sun_disc = False
try: sky.air_density = HC.get('air', 1.0); sky.aerosol_density = HC.get('haze', 1.0)
except Exception: pass
bg = n.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = HC.get('sky', 0.2)
L.new(sky.outputs[0], bg.inputs[0])
# clouds: a noise field on a plane overhead, read along the view direction, thinning to the horizon
tc = n.new('ShaderNodeTexCoord'); sep = n.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
dz = n.new('ShaderNodeMath'); dz.operation = 'MAXIMUM'; dz.inputs[1].default_value = 0.02; L.new(sep.outputs['Z'], dz.inputs[0])
px = n.new('ShaderNodeMath'); px.operation = 'DIVIDE'; L.new(sep.outputs['X'], px.inputs[0]); L.new(dz.outputs[0], px.inputs[1])
py = n.new('ShaderNodeMath'); py.operation = 'DIVIDE'; L.new(sep.outputs['Y'], py.inputs[0]); L.new(dz.outputs[0], py.inputs[1])
cv = n.new('ShaderNodeCombineXYZ'); L.new(px.outputs[0], cv.inputs['X']); L.new(py.outputs[0], cv.inputs['Y']); cv.inputs['Z'].default_value = HC.get('cloud_seed', 3.7)
cn = n.new('ShaderNodeTexNoise'); cn.noise_dimensions = '3D'; cn.inputs['Scale'].default_value = HC.get('cloud_scale', 0.55); cn.inputs['Detail'].default_value = 9; cn.inputs['Roughness'].default_value = 0.62
L.new(cv.outputs[0], cn.inputs['Vector'])
cr = n.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value = HC.get('cloud_cover', 0.56); cr.inputs['From Max'].default_value = HC.get('cloud_cover', 0.56) + 0.2
L.new(cn.outputs['Fac'], cr.inputs['Value'])
hz = n.new('ShaderNodeMapRange'); hz.inputs['From Min'].default_value = 0.03; hz.inputs['From Max'].default_value = 0.35; L.new(sep.outputs['Z'], hz.inputs['Value'])
cm = n.new('ShaderNodeMath'); cm.operation = 'MULTIPLY'; L.new(cr.outputs['Result'], cm.inputs[0]); L.new(hz.outputs['Result'], cm.inputs[1])
cm2 = n.new('ShaderNodeMath'); cm2.operation = 'MULTIPLY'; cm2.inputs[1].default_value = HC.get('cloud_opacity', 0.85); L.new(cm.outputs[0], cm2.inputs[0])
cbg = n.new('ShaderNodeBackground'); cbg.inputs['Color'].default_value = (1.0, 0.97, 0.93, 1); cbg.inputs['Strength'].default_value = HC.get('cloud_light', 0.95)
mxc = n.new('ShaderNodeMixShader'); L.new(cm2.outputs[0], mxc.inputs['Fac']); L.new(bg.outputs[0], mxc.inputs[1]); L.new(cbg.outputs[0], mxc.inputs[2])
lp = n.new('ShaderNodeLightPath'); mxw = n.new('ShaderNodeMixShader')
L.new(lp.outputs['Is Camera Ray'], mxw.inputs['Fac']); L.new(bg.outputs[0], mxw.inputs[1]); L.new(mxc.outputs[0], mxw.inputs[2])
wo = n.new('ShaderNodeOutputWorld'); L.new(mxw.outputs[0], wo.inputs['Surface'])
CLOUD_LIGHT = cbg
sd = bpy.data.lights.new('Sun', 'SUN'); sd.angle = math.radians(0.9)
SUN = bpy.data.objects.new('Sun', sd); sc.collection.objects.link(SUN)
fd = bpy.data.lights.new('Fill', 'SUN'); fd.energy = 0.0; fd.angle = math.radians(40); fd.color = (0.85, 0.9, 1.0)
FILL = bpy.data.objects.new('Fill', fd); sc.collection.objects.link(FILL)
FILL.visible_glossy = False; FILL.visible_transmission = False
def set_fill(f):   # soft skylight-colored fill from the camera side: shade walls keep their siding, as a bounce card would
    f = f or {}
    fd.energy = f.get('energy', 0.0)
    FILL.rotation_euler = (math.radians(90 - f.get('el', 20)), 0, math.radians(-(f.get('az', 120) + 180)))
def set_sun(az, el, energy, color):
    sky.sun_elevation = math.radians(el); sky.sun_rotation = math.radians(az)
    SUN.rotation_euler = (math.radians(90 - el), 0, math.radians(-(az + 180)))
    sd.energy = energy; sd.color = color

# ------------------------------------------------------------------ ground: lawn near the building, forest floor under the trees
def haze_mix(n, L, shader, out, near=90, far=650, amt=None, color=(0.62, 0.70, 0.80)):
    """aerial perspective for camera rays: blend toward the sky color with distance"""
    amt = HC.get('haze_amt', 0.38) if amt is None else amt
    cdn = n.new('ShaderNodeCameraData'); mr = n.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = near; mr.inputs['From Max'].default_value = far; mr.inputs['To Max'].default_value = amt
    HAZE_MR.append(mr)
    L.new(cdn.outputs['View Distance'], mr.inputs['Value'])
    lpn = n.new('ShaderNodeLightPath'); mul = n.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    L.new(mr.outputs['Result'], mul.inputs[0]); L.new(lpn.outputs['Is Camera Ray'], mul.inputs[1])
    em = n.new('ShaderNodeEmission'); em.inputs['Color'].default_value = color + (1,); em.inputs['Strength'].default_value = HAZE_STRENGTH
    HAZE.append(em)
    ms = n.new('ShaderNodeMixShader'); L.new(mul.outputs[0], ms.inputs['Fac']); L.new(shader, ms.inputs[1]); L.new(em.outputs[0], ms.inputs[2]); L.new(ms.outputs[0], out)
HAZE = []; HAZE_MR = []; HAZE_STRENGTH = HC.get('haze_light', 0.55)

bpy.ops.mesh.primitive_plane_add(size=4000, location=(CEN.x, CEN.y, 0)); G = bpy.context.object; G.name = 'Ground'
gm = bpy.data.materials.new('Ground'); nt_, n, L = tree_of(gm)
out = n.new('ShaderNodeOutputMaterial'); b = n.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.92
try: b.inputs['Specular IOR Level'].default_value = 0.3
except Exception: pass
v = coords(n, L)
n1 = noise(n, L, v, 0.025, 5); n2 = noise(n, L, v, 0.25, 8); n3 = noise(n, L, v, 2.5, 8)
mixa = n.new('ShaderNodeMix'); mixa.data_type = 'FLOAT'; mixa.inputs['Factor'].default_value = 0.4; L.new(n1, mixa.inputs['A']); L.new(n2, mixa.inputs['B'])
mixb = n.new('ShaderNodeMix'); mixb.data_type = 'FLOAT'; mixb.inputs['Factor'].default_value = 0.25; L.new(mixa.outputs['Result'], mixb.inputs['A']); L.new(n3, mixb.inputs['B'])
lawn = n.new('ShaderNodeValToRGB'); lawn.color_ramp.elements[0].color = (0.05, 0.08, 0.022, 1); lawn.color_ramp.elements[1].color = (0.13, 0.17, 0.05, 1)
lw = lawn.color_ramp.elements.new(0.9); lw.color = (0.2, 0.19, 0.08, 1)
lawn.color_ramp.elements[0].position = 0.36; lawn.color_ramp.elements[1].position = 0.64
L.new(mixb.outputs['Result'], lawn.inputs['Fac'])
# forest floor beyond the clearing: distance outside the clearing ellipse, broken up with noise
CL = HC.get('clearing', {'cx': CEN.x, 'cy': CEN.y, 'rx': 120, 'ry': 70})
tcg = n.new('ShaderNodeTexCoord'); sepg = n.new('ShaderNodeSeparateXYZ'); L.new(tcg.outputs['Object'], sepg.inputs[0])
def axis(comp, c, r):
    s = n.new('ShaderNodeMath'); s.operation = 'SUBTRACT'; s.inputs[1].default_value = c - (CEN.x if comp == 'X' else CEN.y); L.new(sepg.outputs[comp], s.inputs[0])
    if comp == 'Y':   # the lawn runs on toward the cameras: only the far side of the clearing turns to woods floor
        s2 = n.new('ShaderNodeMath'); s2.operation = 'MAXIMUM'; s2.inputs[1].default_value = 0.0; L.new(s.outputs[0], s2.inputs[0]); s = s2
    d = n.new('ShaderNodeMath'); d.operation = 'DIVIDE'; d.inputs[1].default_value = r; L.new(s.outputs[0], d.inputs[0])
    q = n.new('ShaderNodeMath'); q.operation = 'POWER'; q.inputs[1].default_value = 2; L.new(d.outputs[0], q.inputs[0]); return q.outputs[0]
ad = n.new('ShaderNodeMath'); ad.operation = 'ADD'; L.new(axis('X', CL['cx'], CL['rx']), ad.inputs[0]); L.new(axis('Y', CL['cy'], CL['ry']), ad.inputs[1])
jit = n.new('ShaderNodeMath'); jit.operation = 'MULTIPLY_ADD'; L.new(noise(n, L, v, 0.06, 4), jit.inputs[0]); jit.inputs[1].default_value = 0.6; L.new(ad.outputs[0], jit.inputs[2])
edge = n.new('ShaderNodeMapRange'); edge.inputs['From Min'].default_value = 1.15; edge.inputs['From Max'].default_value = 1.55; L.new(jit.outputs[0], edge.inputs['Value'])
floor = n.new('ShaderNodeValToRGB'); floor.color_ramp.elements[0].color = (0.035, 0.03, 0.018, 1); floor.color_ramp.elements[1].color = (0.075, 0.07, 0.035, 1)
L.new(n3, floor.inputs['Fac'])
gmix = n.new('ShaderNodeMix'); gmix.data_type = 'RGBA'; L.new(edge.outputs['Result'], gmix.inputs['Factor']); L.new(lawn.outputs['Color'], gmix.inputs['A']); L.new(floor.outputs['Color'], gmix.inputs['B'])
L.new(gmix.outputs['Result'], b.inputs['Base Color'])
bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; L.new(n3, bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
haze_mix(n, L, b.outputs[0], out.inputs['Surface'])
G.data.materials.append(gm)

# grass: hair blades on the lawn around the building, denser in front of the near cameras
def blade_mat():
    hm = bpy.data.materials.new('Blades'); nt_, n, L = tree_of(hm)
    out = n.new('ShaderNodeOutputMaterial'); b = n.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.55
    try: b.inputs['Specular IOR Level'].default_value = 0.35
    except Exception: pass
    hi = n.new('ShaderNodeHairInfo'); rmp = n.new('ShaderNodeValToRGB')
    rmp.color_ramp.elements[0].color = (0.06, 0.10, 0.025, 1); rmp.color_ramp.elements[1].color = (0.15, 0.20, 0.055, 1)
    e3 = rmp.color_ramp.elements.new(0.92); e3.color = (0.22, 0.22, 0.09, 1)
    L.new(hi.outputs['Random'], rmp.inputs['Fac'])
    # blades darken a little toward the root, where they shade each other
    gr = n.new('ShaderNodeMapRange'); gr.inputs['To Min'].default_value = 0.6; L.new(hi.outputs['Intercept'], gr.inputs['Value'])
    mulc = n.new('ShaderNodeVectorMath'); mulc.operation = 'SCALE'; L.new(rmp.outputs['Color'], mulc.inputs[0]); L.new(gr.outputs['Result'], mulc.inputs['Scale'])
    L.new(mulc.outputs['Vector'], b.inputs['Base Color'])
    tr = n.new('ShaderNodeBsdfTranslucent'); L.new(rmp.outputs['Color'], tr.inputs['Color'])
    ms = n.new('ShaderNodeMixShader'); ms.inputs['Fac'].default_value = 0.3; L.new(b.outputs[0], ms.inputs[1]); L.new(tr.outputs[0], ms.inputs[2])
    haze_mix(n, L, ms.outputs[0], out.inputs['Surface'])
    return hm
def grass_patch(box, density, name):
    import bmesh
    gx0, gy0, gx1, gy1 = box
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=60, size=1, location=((gx0 + gx1) / 2, (gy0 + gy1) / 2, 0.0))
    GR = bpy.context.object; GR.name = name; GR.scale = (gx1 - gx0, gy1 - gy0, 1)
    bpy.ops.object.transform_apply(scale=True)
    bm = bmesh.new(); bm.from_mesh(GR.data)
    kill = [f for f in bm.faces if all(mn.x - 0.5 < (GR.matrix_world @ v_.co).x < mx.x + 0.5 and mn.y - 0.5 < (GR.matrix_world @ v_.co).y < mx.y + 0.5 for v_ in f.verts)]
    bmesh.ops.delete(bm, geom=kill, context='FACES'); bm.to_mesh(GR.data); bm.free()
    area = sum(p.area for p in GR.data.polygons)
    GR.data.materials.append(BLADES)
    ps = GR.modifiers.new('grass', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
    gl = HC.get('grass_len', 0.3)   # blade length in feet: Blender grows hair to 4 x the normal velocity here
    st.type = 'HAIR'; st.count = int(area * density); st.hair_length = gl
    st.length_random = 0.6; st.use_advanced_hair = True; st.normal_factor = gl / 4; st.factor_random = gl / 12; st.brownian_factor = 0.0
    st.hair_step = 2; st.display_step = 1; st.render_step = 1; st.emit_from = 'FACE'   # 2 segments a blade: 3 steps blew 8 GB with 1.5M blades; st.use_emit_random = True; st.display_percentage = 0
    st.root_radius = 1.0; st.tip_radius = 0.0; st.radius_scale = HC.get('blade_radius', 0.01); st.material_slot = 'Blades'
    ps.seed = SEED + len(name)
    GR.show_instancer_for_render = False
    print(f'grass {name}: {st.count:,} blades over {area:,.0f} sf', flush=True)
    return GR
NEAR = []
if '--no-grass' not in A and HC.get('grass', True):
    BLADES = blade_mat()
    grass_patch(HC.get('grass_box', [mn.x - 60, mn.y - 110, mx.x + 90, mx.y + 30]), HC.get('grass_density', 18) * (0.3 if DRAFT else 1), 'Grass')
    for i, nb in enumerate(HC.get('grass_near', [])):   # [x0, y0, x1, y1, density, [shot ids]]: the lawn close to a camera
        NEAR.append((grass_patch(nb[:4], nb[4] * (0.2 if DRAFT else 1), f'GrassNear{i}'), nb[5] if len(nb) > 5 else None))

# ------------------------------------------------------------------ trees
R = random.Random(SEED)
LIB = ez.load()
for m in bpy.data.materials:   # haze on the trees too, on the leaf itself and not on the cut-out part of the card
    if m.name.startswith(('ezleaf_', 'ezbark_')):
        n, L = m.node_tree.nodes, m.node_tree.links
        o_ = next(x for x in n if x.type == 'OUTPUT_MATERIAL'); top = o_.inputs['Surface'].links[0].from_node
        cut = top if m.name.startswith('ezleaf_') and top.type == 'MIX_SHADER' else None
        target = cut.inputs[2] if cut else o_.inputs['Surface']
        haze_mix(n, L, target.links[0].from_socket, target)
KIND = {'oak': ez.names(LIB, 'Oak'), 'ash': ez.names(LIB, 'Ash'), 'pine': ez.names(LIB, 'Pine'), 'bush': ez.names(LIB, 'Bush')}
def pick(mix):
    r = R.random(); acc = 0
    for k, p in mix.items():
        acc += p
        if r <= acc: return k
    return list(mix)[-1]
placed = []
def plant(kind, x, y, h):
    nm = R.choice(KIND[kind]); placed.append((x, y)); return ez.place(LIB, nm, x, y, h, R=R)
STANDS = HC.get('stands') or []
for s in STANDS:   # explicit trees: [kind, x, y, height, {z, shadow_only}]
    o_ = s[4] if len(s) > 4 else {}
    if o_.get('shadow_only'):   # a gobo: a tree that only casts shade, raised so it dapples the roof and leaves the walls in sun
        root = ez.place(LIB, R.choice(KIND[s[0]]), s[1], s[2], s[3], R=R); root.location.z += o_.get('z', 0)
        for c in root.children:
            c.visible_camera = False; c.visible_glossy = False; c.visible_transmission = False; c.visible_diffuse = False; c.visible_volume_scatter = False
            if c.name.startswith('bark'): c.visible_shadow = False   # leaves only: a floating trunk would print a stripe on the wall
    else: plant(s[0], s[1], s[2], s[3])
# the woods around the clearing: rings of trees outside the clearing ellipse, open on the camera side
F = HC.get('forest', {})
open_from, open_to = F.get('open', [200, 340])     # bearings (deg, 0 = north, clockwise) left open toward the cameras
mix = F.get('mix', {'oak': 0.4, 'ash': 0.3, 'pine': 0.3})
n_tr = F.get('count', 150 if not DRAFT else 70)
tries = 0
GAPS = F.get('gaps', [])   # [from, to, kmin]: bearings where the woods stand back, so sky shows behind the roof
def in_gap(ang, k):
    for g0, g1, kmin in GAPS:
        inside = (g0 <= ang <= g1) if g0 <= g1 else (ang >= g0 or ang <= g1)
        if inside and k < kmin: return True
    return False
while n_tr > 0 and tries < 20000:
    tries += 1
    ang = R.uniform(0, 360)
    if open_from <= ang <= open_to: continue
    k = R.uniform(1.12, F.get('depth', 2.6))
    if in_gap(ang, k): continue
    a = math.radians(ang)
    x = CL['cx'] + math.sin(a) * CL['rx'] * k; y = CL['cy'] + math.cos(a) * CL['ry'] * k
    if any((x - px) ** 2 + (y - py) ** 2 < F.get('spacing', 17) ** 2 for px, py in placed): continue
    kind = pick(mix)
    h = (R.uniform(62, 92) if kind != 'pine' else R.uniform(58, 84)) * (1 + 0.15 * (k - 1.1))
    plant(kind, x, y, h); n_tr -= 1
# a lower, farther band inside the gaps, so the horizon closes without trees rising behind the roof
for g0, g1, kmin in GAPS:
    for i in range(F.get('far', 45) if not DRAFT else 40):
        span = (g1 - g0) % 360; ang = (g0 + R.uniform(0, span)) % 360; k = R.uniform(kmin + 0.2, kmin + 1.8)
        a = math.radians(ang); x = CL['cx'] + math.sin(a) * CL['rx'] * k; y = CL['cy'] + math.cos(a) * CL['ry'] * k
        kind = pick(mix); plant(kind, x, y, R.uniform(*F.get('far_h', [34, 52])))
        for j in range(2):   # brush in front of each far tree closes the view under the canopies
            a2 = a + R.uniform(-0.05, 0.05); k2 = k - R.uniform(0.05, 0.35)
            plant('bush', CL['cx'] + math.sin(a2) * CL['rx'] * k2, CL['cy'] + math.cos(a2) * CL['ry'] * k2, R.uniform(10, 18))
# understory along the edge, so the trunks stand in brush and not on a bare lawn
for i in range(F.get('brush', 170) if not DRAFT else 80):
    ang = R.uniform(0, 360)
    if open_from + 5 <= ang <= open_to - 5: continue
    a = math.radians(ang); k = R.uniform(1.0, 1.35)
    if in_gap(ang, k): continue
    plant('bush', CL['cx'] + math.sin(a) * CL['rx'] * k, CL['cy'] + math.cos(a) * CL['ry'] * k, R.uniform(*F.get('brush_h', [9, 20])))
print(f'trees: {len(placed)} placed', flush=True)

# ------------------------------------------------------------------ interior light for dusk
LIGHTS = []
for (x, y, z, e) in HC.get('interior_lights', []):
    ld = bpy.data.lights.new('In', 'POINT'); ld.energy = e; ld.color = (1.0, 0.70, 0.42); ld.shadow_soft_size = 2.5
    lo = bpy.data.objects.new('In', ld); lo.location = (x, y, z); sc.collection.objects.link(lo); LIGHTS.append(lo)
    lo.visible_camera = False; lo.visible_glossy = False; lo.visible_transmission = False

# ------------------------------------------------------------------ render settings
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = SPP; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02 if DRAFT else 0.008
sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.cycles.max_bounces = 10; sc.cycles.diffuse_bounces = 4; sc.cycles.glossy_bounces = 4; sc.cycles.transmission_bounces = 8; sc.cycles.transparent_max_bounces = 24
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.cycles.blur_glossy = 1.0
try: sc.cycles_curves.shape = 'RIBBONS'   # flat blades: a third of the memory of round curves
except Exception: pass
try: sc.cycles.light_tree = True
except Exception: pass
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = HC.get('look', 'AgX - Medium High Contrast')
sc.view_settings.exposure = HC.get('exposure', 0.0)
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.resolution_percentage = 100
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '16'
if opt('--border'):   # --border x0,y0,x1,y1 (0..1 from bottom left): render only that region, for close checks
    bx = [float(v) for v in opt('--border').split(',')]
    sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_min_y, sc.render.border_max_x, sc.render.border_max_y = bx

cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36
def shoot(s):
    pos = Vector(s['pos']); look = Vector(s['look'])
    d = look - pos; yaw = math.atan2(d.y, d.x)
    # level camera: pitch 0, aim by yaw only; framing height comes from lens shift so verticals stay plumb
    cam.location = pos; cam.rotation_euler = (math.radians(90), 0, yaw - math.pi / 2)
    W_, H_ = s.get('size', [W, H])
    if DRAFT and s.get('size'): W_, H_ = int(W_ * 0.4), int(H_ * 0.4)
    sc.render.resolution_x, sc.render.resolution_y = W_, H_
    cd.sensor_fit = 'VERTICAL' if H_ > W_ else 'HORIZONTAL'   # portrait (phone) frames: lens and shift work on the height
    cd.sensor_height = 36 if H_ > W_ else 24
    if s.get('samples') and not DRAFT: sc.cycles.samples = s['samples']
    cd.lens = s.get('lens', 50); hd = math.hypot(d.x, d.y)
    fov_w = 2 * math.tan(math.atan(18 / cd.lens))   # frame width per unit distance
    cd.shift_y = s.get('shift_y', (look.z - pos.z) / hd / fov_w)
    cd.shift_x = s.get('shift_x', 0)
    for mr in HAZE_MR:   # haze starts past the building, so a long lens from far off does not wash out the trees
        mr.inputs['From Min'].default_value = hd + 40; mr.inputs['From Max'].default_value = hd + 600
    if s.get('dof'):
        cd.dof.use_dof = True; cd.dof.focus_distance = hd; cd.dof.aperture_fstop = s['dof']
    else: cd.dof.use_dof = False

SHOTS = HC.get('shots', []) + HC.get('page_shots', [])   # page_shots: frames for the presentation stops, run with --only
if '--probe' in A:   # what shades a point: cast toward the sun from sample points and report the first hit
    set_sun(SUN_AZ, SUN_EL, 3, (1, 1, 1)); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); to_sun = -(SUN.matrix_world.to_3x3() @ Vector((0, 0, -1)))
    rows = [('roof y12', [(x, 12, 15.5 + 0.75 * 12) for x in range(1, 40, 2)]), ('roof y5 ', [(x, 5, 15.5 + 0.75 * 5) for x in range(1, 40, 2)]),
            ('wall z11', [(x, -0.3, 11) for x in range(1, 40, 2)]), ('wall z5 ', [(x, -0.3, 5) for x in range(1, 40, 2)]), ('lawn -20', [(x, -20, 0.2) for x in range(-20, 100, 6)]), ('lawn -45', [(x, -45, 0.2) for x in range(-20, 100, 6)])]
    for pt in [(70, -45, 0.2), (60, -55, 0.2), (40, -50, 0.2)]:
        hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, Vector(pt), to_sun)
        print('probe hit', pt, ob.name if hit else '-', ob.parent.name if hit and ob.parent else '', [round(v, 1) for v in loc] if hit else '', flush=True)
    for label, pts in rows:
        line = ''
        for pt in pts:
            hit, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, Vector(pt), to_sun)
            line += ('#' if 'leaves' in ob.name else 'T' if 'bark' in ob.name else 'b') if hit else '.'
        print('probe', label, line, flush=True)
    sys.exit(0)
for s in SHOTS:
    if ONLY and s['id'] not in ONLY: continue
    if not ONLY and s.get('page'): continue
    dusk = s.get('dusk', False)
    if dusk:
        set_sun(s.get('sun_az', SUN_AZ), s.get('sun_el', 2.5), s.get('sun_energy', 0.35), (1.0, 0.55, 0.32))
        bg.inputs['Strength'].default_value = s.get('sky', 0.09); CLOUD_LIGHT.inputs['Strength'].default_value = s.get('cloud_light', 0.12)
        CLOUD_LIGHT.inputs['Color'].default_value = (1.0, 0.62, 0.42, 1)
        for e in LAMPS: e.inputs['Strength'].default_value = s.get('lamp', 60)
        for e in HAZE: e.inputs['Strength'].default_value = s.get('haze_light', 0.08)
        for lo in LIGHTS: lo.hide_render = False
    else:
        set_sun(s.get('sun_az', SUN_AZ), s.get('sun_el', SUN_EL), s.get('sun_energy', HC.get('sun_energy', 3.4)), tuple(HC.get('sun_color', (1.0, 0.87, 0.72))))
        bg.inputs['Strength'].default_value = s.get('sky', HC.get('sky', 0.2)); CLOUD_LIGHT.inputs['Strength'].default_value = s.get('cloud_light', HC.get('cloud_light', 0.95))
        CLOUD_LIGHT.inputs['Color'].default_value = (1.0, 0.97, 0.93, 1)
        for e in LAMPS: e.inputs['Strength'].default_value = 0.0
        for e in HAZE: e.inputs['Strength'].default_value = HAZE_STRENGTH
        for lo in LIGHTS: lo.hide_render = True
    sc.view_settings.exposure = s.get('exposure', HC.get('exposure', 0.0))
    set_fill(s.get('fill'))
    for g_, ids in NEAR: g_.hide_render = bool(ids) and s['id'] not in ids
    shoot(s)
    f = os.path.join(OUT, s.get('out', f"hero_{s['id']}.png")); sc.render.filepath = f
    ts = time.time(); bpy.ops.render.render(write_still=True)
    print(f"{f} {time.time() - ts:.0f}s", flush=True)
print(f'done in {time.time() - t0:.0f}s', flush=True)
