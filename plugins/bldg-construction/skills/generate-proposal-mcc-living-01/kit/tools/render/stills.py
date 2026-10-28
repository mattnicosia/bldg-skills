#!/usr/bin/env python3
"""Render the presentation's stills in Cycles, one per stop (several for build stops, one per phase),
for model.mode "images". Desktop 16:9 and phone portrait, framed like the live views.

    python3 tools/render/stills.py <project_dir> [--only hero0,build2] [--samples 32] [--phone-only|--desktop-only] [--draft]

Reads project.json (stops, phases, model.render) and <project>/model.glb. Writes <project>/img/r_<stop>_<n>_{d,p}.jpg
and <project>/renders.json, which build.py turns into the image list and each stop's still indices.
"""
import bpy, math, os, sys, json, time
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as SC

A = sys.argv
proj = os.path.abspath(A[1]); P = json.load(open(os.path.join(proj, 'project.json')))
opt = lambda k, d=None: A[A.index(k) + 1] if k in A else d
ONLY = set(opt('--only', '').split(',')) - {''}
SPP = int(opt('--samples', 32)); DRAFT = '--draft' in A
RC = P.get('model', {}).get('render', {})
PRESET = {   # same table as template/world.js: distance in model sizes, azimuth from the front, elevation, vertical fov, look height
  'hero': [1.55, 28, 9, 34, 0.35], 'front': [1.7, 0, 6, 32, 0.4], 'rear': [1.7, 180, 10, 32, 0.4], 'left': [1.7, -90, 8, 32, 0.4], 'right': [1.7, 90, 8, 32, 0.4],
  'aerial': [1.85, 38, 34, 32, 0.2], 'aerial-rear': [1.85, 215, 34, 32, 0.2], 'top': [2.3, 10, 78, 32, 0], 'low': [1.25, -24, 4, 38, 0.5],
  'corner-left': [1.55, -42, 16, 32, 0.35], 'corner-right': [1.55, 48, 16, 32, 0.35], 'detail': [0.9, 30, 12, 36, 0.45]}
SIDE = {'hero': 'l', 'budget': 'l', 'alternates': 'r', 'schedule': 'r', 'precon': 'l', 'job': 'r', 'principals': 'r', 'thanks': 'r'}

t0 = time.time()
sc = SC.build(os.path.join(proj, 'model.glb'), sun_az=RC.get('sun_az', 215), sun_el=RC.get('sun_el', 32), trees=False)
# phases from the glTF node names
def phase_of(o):
    while o is not None:
        if '[phase:' in o.name: return o.name.split('[phase:')[1].split(']')[0]
        o = o.parent
    return None
B = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'Lawn']
PH = {o.name: phase_of(o) for o in B}
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
for o in B:
    for c in o.bound_box:
        p = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, p)); mx = Vector(map(max, mx, p))
size = mx - mn; S = max(size.x, size.y, size.z * 1.6); CEN = (mn + mx) / 2
print('model', [round(v, 1) for v in mn], [round(v, 1) for v in mx], 'S', round(S, 1), flush=True)
# a forest edge all round (Cycles-rendered strips on cards facing the barn), and a few full trees closer in
TD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'trees')
strips = [os.path.join(TD, f) for f in sorted(os.listdir(TD)) if f.startswith('forest_') and f.endswith('.png')] if os.path.isdir(TD) else []
def _fill_base(f):   # the bottom of the forest edge falls into shade, so no lawn shows between trunks
    mark = f + '.filled'
    if os.path.exists(mark) and os.path.getmtime(mark) >= os.path.getmtime(f): return
    from PIL import Image
    import numpy as np
    im = np.array(Image.open(f)).astype(np.float32); H = im.shape[0]; band = int(H * 0.12)
    for i in range(band):
        y = H - 1 - i; t = 1 - i / band; a = im[y, :, 3] / 255.0; na = np.maximum(a, np.clip(t * 1.4, 0, 1))
        w = (na - a) / np.maximum(na, 1e-6); im[y, :, :3] = im[y, :, :3] * (1 - w[:, None]) + np.array([18, 28, 12], np.float32) * w[:, None]; im[y, :, 3] = na * 255
    Image.fromarray(im.astype(np.uint8)).save(f); open(mark, 'w').write('1')
for f in strips: _fill_base(f)
if strips:
    import random as _r
    RR = _r.Random(RC.get('tree_seed', 7))
    mats = []
    for f in strips:
        m = bpy.data.materials.new('Forest'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(f); tx.extension = 'CLIP'
        em = nt.nodes.new('ShaderNodeEmission'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx_ = nt.nodes.new('ShaderNodeMixShader'); o_ = nt.nodes.new('ShaderNodeOutputMaterial')
        em.inputs['Strength'].default_value = RC.get('forest_light', 0.95)
        nt.links.new(tx.outputs['Color'], em.inputs['Color']); nt.links.new(tx.outputs['Alpha'], mx_.inputs['Fac'])
        nt.links.new(tr.outputs[0], mx_.inputs[1]); nt.links.new(em.outputs[0], mx_.inputs[2]); nt.links.new(mx_.outputs[0], o_.inputs['Surface'])
        mats.append(m)
    for k in range(RC.get('forest_cards', 14)):
        ang = k / RC.get('forest_cards', 14) * 2 * math.pi + RR.uniform(-0.1, 0.1); rad = S * RR.uniform(3.6, 4.6); sc_ = RR.uniform(0.85, 1.1)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(CEN.x + math.cos(ang) * rad, CEN.y + math.sin(ang) * rad, 0))
        c = bpy.context.object; c.scale = (420 * sc_, 1, 1); c.rotation_euler = (math.radians(90), 0, ang + math.pi / 2)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        h = 420 * sc_ * 1150 / 4096
        for v in c.data.vertices: v.co.z = (v.co.z + 0.5 * (1 if v.co.z > 0 else -1) * 0) 
        # plane is 1 unit tall before scaling: set its height to the strip's aspect, foot on the lawn
        for v in c.data.vertices: v.co.z = h if v.co.z > 0 else -0.5
        c.data.materials.append(mats[k % len(mats)]); c.visible_shadow = False
    SC.tree_line(RC.get('tree_seed', 7), cen=CEN, count=RC.get('trees', 10), rmin=S * 2.3, rmax=S * 3.1, around=(0.15, 0.85))
else:
    SC.tree_line(RC.get('tree_seed', 7), cen=CEN, count=RC.get('trees', 110), rmin=S * 2.5, rmax=S * 5.5, around=(0, 2.0))
# glass reads as dark glazing by day and a warm interior at dusk
glass = [m for m in bpy.data.materials if m.name.startswith('glass')]
for m in glass:   # real glass, so the bifolds read as glazing with the room behind them
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (0.92, 0.95, 0.95, 1); b.inputs['Metallic'].default_value = 0; b.inputs['Roughness'].default_value = 0.02
    b.inputs['IOR'].default_value = 1.5; b.inputs['Transmission Weight'].default_value = RC.get('glass_transmission', 0.55)
    b.inputs['Base Color'].default_value = (0.32, 0.36, 0.36, 1)   # dark tinted glazing that still shows the room
# warm interior light for the dusk frames
lamps = []
for (x, y, z, e) in RC.get('interior_lights', [[CEN.x - 12, CEN.y, 8, 2600], [CEN.x + 2, CEN.y, 8, 1800], [CEN.x + 20, CEN.y, 6.5, 1100]]):
    ld = bpy.data.lights.new('In', 'POINT'); ld.energy = e; ld.color = (1.0, 0.72, 0.45); ld.shadow_soft_size = 3
    lo = bpy.data.objects.new('In', ld); lo.location = (x, y, z); sc.collection.objects.link(lo); lamps.append(lo)
    try: lo.visible_camera = False; lo.visible_glossy = False; lo.visible_transmission = False
    except Exception: pass
def set_dusk(on):
    w = sc.world.node_tree.nodes
    sky = next(n for n in w if n.type == 'TEX_SKY'); sky.sun_elevation = math.radians(RC.get('dusk_el', 5) if on else RC.get('sun_el', 32))
    sun = bpy.data.objects['Sun']; sun.data.energy = 0.5 if on else 3.2; sun.data.color = (1.0, 0.62, 0.38) if on else (1.0, 0.86, 0.72)
    sun.rotation_euler = (math.radians(90 - (RC.get('dusk_el', 5) if on else RC.get('sun_el', 32))), 0, sun.rotation_euler.z)
    w['Background'].inputs['Strength'].default_value = RC.get('dusk_sky', 0.16) if on else 0.18
    for lo in lamps: lo.hide_render = not on
FRONT = Vector((0, -1, 0)); RIGHT = Vector((-1, 0, 0))   # world.js: the front faces south, three z -> Blender -y
zoom = RC.get('zoom', P.get('model', {}).get('zoom', 1.0))
cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.sensor_fit = 'VERTICAL'
def frame(view, sx, sy, phone):
    d, az, el, fov, lh = PRESET.get(view, PRESET['hero']) if isinstance(view, str) else view
    a, e = math.radians(az), math.radians(el)
    dirv = (FRONT * math.cos(a) + RIGHT * math.sin(a)) * math.cos(e) + Vector((0, 0, math.sin(e)))
    dist = d * S / math.tan(math.radians(fov) / 2) * (0.42 / zoom)
    look = CEN.copy(); look.z = mn.z + size.z * lh
    W, H = sc.render.resolution_x, sc.render.resolution_y; asp = W / H
    if phone: dist *= RC.get('phone_dist', 1.1)   # stay inside the tree line: widen the lens instead of backing off
    cam.location = look + dirv * dist
    cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()
    if phone:
        cd.sensor_fit = 'HORIZONTAL'; cd.angle_x = math.radians(RC.get('phone_hfov', 40)); cd.shift_x = 0; cd.shift_y = -RC.get('phone_up', 0.24) * H / max(W, H)
    else:
        cd.sensor_fit = 'VERTICAL'; cd.angle_y = math.radians(fov); cd.shift_x = -sx; cd.shift_y = sy * H / W
# the shot list: every stop, and for build stops one frame per revealed phase
phases = [p['id'] for p in P.get('phases', [])]
shots = []
for i, s in enumerate(P['stops']):
    sid = s.get('id') or s['type'] + str(i)
    if s['type'] == 'schedule': continue
    if s['type'] == 'hero' and RC.get('hero_view'): s = {**s, 'view': RC['hero_view']}
    side = s.get('side') or SIDE.get(s['type'], 'l')
    off = RC.get('side_shift', 0.2)   # stills sit under the copy panels, so the building moves further aside than in live 3D
    sx = -off if side == 'r' else RC.get('hero_sx', 0.27) if s['type'] == 'hero' else off
    sy = RC.get('hero_sy', 0.2) if s['type'] == 'hero' else 0
    dusk = any(x.get('dusk') for x in P['stops'][:i + 1])
    if s['type'] == 'build' and s.get('reveal'):
        last = phases.index(s['reveal'][-1]); first = phases.index(s['reveal'][0])
        for k in range(first - 1 if first > 0 else first, last + 1):
            shots.append((sid, len([x for x in shots if x[0] == sid]), s.get('view', 'hero'), set(phases[:k + 1]), sx, sy, dusk))
    else:
        vis = set(phases[:phases.index(s['show']) + 1]) if s.get('show') else set(phases)
        shots.append((sid, 0, s.get('view', 'hero'), vis, sx, sy, dusk))
img_dir = os.path.join(proj, 'img'); os.makedirs(img_dir, exist_ok=True)
sc.cycles.samples = SPP if not DRAFT else 12
out = json.load(open(os.path.join(proj, 'renders.json'))) if os.path.exists(os.path.join(proj, 'renders.json')) else {}
modes = [m for m in ('d', 'p') if not ('--phone-only' in A and m == 'd') and not ('--desktop-only' in A and m == 'p')]
cur_dusk = None
for sid, n, view, vis, sx, sy, dusk in shots:
    if ONLY and sid not in ONLY: continue
    if dusk != cur_dusk: set_dusk(dusk); cur_dusk = dusk
    for o in B: o.hide_render = PH[o.name] not in vis and PH[o.name] is not None
    for m in modes:
        sc.render.resolution_x, sc.render.resolution_y = ((1600, 900) if m == 'd' else (720, 1400)) if not DRAFT else ((800, 450) if m == 'd' else (360, 700))
        frame(view, sx, sy, m == 'p')
        f = f'r_{sid}_{n}_{m}.jpg'; sc.render.filepath = os.path.join(img_dir, f)
        sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
        ts = time.time(); bpy.ops.render.render(write_still=True)
        out.setdefault(sid, {}).setdefault(m, {})[str(n)] = f
        print(f'{f} {time.time() - ts:.0f}s', flush=True)
json.dump(out, open(os.path.join(proj, 'renders.json'), 'w'), indent=1)
print(f'done in {time.time() - t0:.0f}s')
