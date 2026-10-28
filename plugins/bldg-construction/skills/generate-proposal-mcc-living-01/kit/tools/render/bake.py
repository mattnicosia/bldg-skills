#!/usr/bin/env python3
"""Bake Cycles lighting into the building model, so the realtime page looks like a rendering.

    python3 tools/render/bake.py <project_dir> [--density 16] [--samples 96] [--sun-az 215 --sun-el 32]

Reads <project>/model.glb (from tools/make_glb.mjs or the architect's export), lights it with a
physical sky and sun over a lawn, bakes every mesh's full lighting (direct, bounce, sky shadowing,
reflections) into its own texture, and writes <project>/model_baked.glb. The page shows those
textures unlit (model.baked: true), with the sun's shadow on the lawn still live.
Needs Blender as a module: pip install bpy (Python 3.13 wheel).
"""
import bpy, bmesh, math, os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene as SC

def arg(k, d):
    a = sys.argv
    return type(d)(a[a.index(k) + 1]) if k in a else d

proj = os.path.abspath(sys.argv[1])
DENS, SPP = arg('--density', 16.0), arg('--samples', 96)
AZ, EL, K = arg('--sun-az', 215.0), arg('--sun-el', 32.0), arg('--scale', 0.5)   # K: bake at K x light, the page multiplies back
t0 = time.time()
sc = SC.build(os.path.join(proj, 'model.glb'), sun_az=AZ, sun_el=EL, trees=False)
# scale the light so bright faces stay under 1.0 in an 8 bit texture
for o in bpy.data.objects:
    if o.type == 'LIGHT': o.data.energy *= K
bg = sc.world.node_tree.nodes.get('Background'); bg.inputs['Strength'].default_value *= K
sc.cycles.samples = SPP
sc.render.bake.margin = 6
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'Lawn']
out_dir = os.path.join(proj, 'bake'); os.makedirs(out_dir, exist_ok=True)
total = 0
for o in meshes:
    me = o.data
    area = sum(p.area for p in me.polygons) * (o.matrix_world.median_scale ** 2)
    side = math.sqrt(area) * DENS * 1.35
    size = int(min(4096, max(256, 2 ** round(math.log2(max(side, 1))))))
    total += size * size
    # one material per object, so each can bake into its own image
    for i, m in enumerate(me.materials): me.materials[i] = m.copy()
    while len(me.uv_layers): me.uv_layers.remove(me.uv_layers[0])
    uv = me.uv_layers.new(name='bake'); me.uv_layers.active = uv
    bpy.context.view_layer.objects.active = o
    for x in bpy.context.view_layer.objects: x.select_set(x == o)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=4.0 / size, area_weight=0.0, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(rotate=True, margin=4.0 / size)
    bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new('bake_' + o.name.replace(' ', '_'), size, size, alpha=False)
    for m in me.materials:
        nt = m.node_tree; n = nt.nodes.new('ShaderNodeTexImage'); n.image = img; n.name = 'BAKE'; nt.nodes.active = n
    o['bake_image'] = img.name
    print(f'{o.name}: {area:.0f} sf -> {size}px', flush=True)
print(f'bake atlas total {total / 1e6:.1f} Mpx', flush=True)
for x in bpy.context.view_layer.objects: x.select_set(x in meshes)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.bake(type='COMBINED', margin=6, use_clear=True)
print(f'baked in {time.time() - t0:.0f}s', flush=True)
# light denoise of each map, then wire the map in as the base color for export
for o in meshes:
    img = bpy.data.images[o['bake_image']]
    path = os.path.join(out_dir, img.name + '.png'); img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    for m in o.data.materials:
        nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        tex = nt.nodes['BAKE']; nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
try:
    from PIL import Image, ImageFilter
    for f in os.listdir(out_dir):
        if f.endswith('.png'):
            p = os.path.join(out_dir, f); im = Image.open(p).convert('RGB'); im.filter(ImageFilter.GaussianBlur(0.6)).save(p)
    for img in bpy.data.images:
        if img.name.startswith('bake_'): img.reload()
except Exception as e: print('denoise skipped', e)
bpy.data.objects.remove(bpy.data.objects['Lawn'])
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA'): bpy.data.objects.remove(o)
outp = os.path.join(proj, 'model_baked.glb')
bpy.ops.export_scene.gltf(filepath=outp, export_format='GLB', export_image_format='JPEG', export_jpeg_quality=86, export_yup=True, export_apply=True)
json.dump({'scale': K, 'sun_az': AZ, 'sun_el': EL, 'density': DENS, 'samples': SPP}, open(os.path.join(proj, 'bake', 'bake.json'), 'w'))
print(f'wrote {outp} {os.path.getsize(outp) / 1e6:.1f} MB in {time.time() - t0:.0f}s')
