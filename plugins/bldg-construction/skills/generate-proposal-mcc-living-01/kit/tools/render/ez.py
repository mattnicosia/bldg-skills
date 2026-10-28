# EZ-Tree trees for the Cycles scenes: load the GLB from tools/make_trees.mjs, put photographic
# bark and leaf textures on, and place linked copies (cheap instances) at a height in feet.
import bpy, os, math, random
from mathutils import Vector

KIT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
A = os.path.join(KIT, 'assets')

def _img(p, data=False):
    im = bpy.data.images.load(p, check_existing=True)
    if data: im.colorspace_settings.name = 'Non-Color'
    return im

def leaf_mat(kind, hue=0.0, val=1.0, sat=1.0):
    m = bpy.data.materials.new('ezleaf_' + kind); m.use_nodes = True
    n = m.node_tree.nodes; L = m.node_tree.links; n.clear()
    out = n.new('ShaderNodeOutputMaterial')
    tx = n.new('ShaderNodeTexImage'); tx.image = _img(os.path.join(A, 'leaves', kind + '.png')); tx.interpolation = 'Cubic'
    # per tree variation: hue and value drift so a stand of the same tree does not read as copies
    oi = n.new('ShaderNodeObjectInfo')
    mr = n.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = -0.035; mr.inputs['To Max'].default_value = 0.035
    L.new(oi.outputs['Random'], mr.inputs['Value'])
    add = n.new('ShaderNodeMath'); add.operation = 'ADD'; add.inputs[1].default_value = 0.5 + hue
    L.new(mr.outputs['Result'], add.inputs[0])
    hs = n.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = sat; hs.inputs['Value'].default_value = val
    L.new(add.outputs[0], hs.inputs['Hue']); L.new(tx.outputs['Color'], hs.inputs['Color'])
    b = n.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.55
    try: b.inputs['Specular IOR Level'].default_value = 0.35
    except Exception: pass
    L.new(hs.outputs['Color'], b.inputs['Base Color'])
    tr = n.new('ShaderNodeBsdfTranslucent')
    tc = n.new('ShaderNodeMix'); tc.data_type = 'RGBA'; tc.blend_type = 'MULTIPLY'; tc.inputs['Factor'].default_value = 1.0
    tc.inputs['B'].default_value = (0.9, 1.0, 0.45, 1)
    L.new(hs.outputs['Color'], tc.inputs['A']); L.new(tc.outputs['Result'], tr.inputs['Color'])
    mx = n.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = 0.32
    L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    tp = n.new('ShaderNodeBsdfTransparent')
    cut = n.new('ShaderNodeMath'); cut.operation = 'GREATER_THAN'; cut.inputs[1].default_value = 0.45
    L.new(tx.outputs['Alpha'], cut.inputs[0])
    mx2 = n.new('ShaderNodeMixShader')
    L.new(cut.outputs[0], mx2.inputs['Fac']); L.new(tp.outputs[0], mx2.inputs[1]); L.new(mx.outputs[0], mx2.inputs[2])
    L.new(mx2.outputs[0], out.inputs['Surface'])
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m

def bark_mat(kind):
    m = bpy.data.materials.new('ezbark_' + kind); m.use_nodes = True
    n = m.node_tree.nodes; L = m.node_tree.links
    b = n['Principled BSDF']; b.inputs['Roughness'].default_value = 0.9
    c = n.new('ShaderNodeTexImage'); c.image = _img(os.path.join(A, 'bark', kind + '_c.jpg'))
    nm = n.new('ShaderNodeTexImage'); nm.image = _img(os.path.join(A, 'bark', kind + '_n.jpg'), True)
    hs = n.new('ShaderNodeHueSaturation'); hs.inputs['Value'].default_value = 0.7
    L.new(c.outputs['Color'], hs.inputs['Color']); L.new(hs.outputs['Color'], b.inputs['Base Color'])
    nmap = n.new('ShaderNodeNormalMap'); nmap.inputs['Strength'].default_value = 1.2
    L.new(nm.outputs['Color'], nmap.inputs['Color']); L.new(nmap.outputs['Normal'], b.inputs['Normal'])
    return m

LEAF_TUNE = {'oak': (0.0, 0.78, 0.95), 'ash': (0.0, 0.85, 0.9), 'pine': (0.0, 0.72, 0.9), 'aspen': (0.11, 0.62, 0.75)}

def load(glb=None):
    """Import the tree GLB into a hidden collection. Returns {name: (object, height)} for the tree roots."""
    glb = glb or os.path.join(A, 'trees', 'ez_trees.glb')
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    new = [o for o in bpy.data.objects if o not in before]
    lib = bpy.data.collections.new('EZLib'); bpy.context.scene.collection.children.link(lib)
    lib.hide_render = True; lib.hide_viewport = True
    mats = {}
    out = {}
    for o in new:
        for c in o.users_collection: c.objects.unlink(o)
        lib.objects.link(o)
        if o.type == 'MESH':
            for i, s in enumerate(o.material_slots):
                nm = s.material.name.split('.')[0] if s.material else ''
                if nm.startswith('leaf_'):
                    k = nm[5:]
                    if nm not in mats: mats[nm] = leaf_mat(k, *LEAF_TUNE.get(k, (0, 0.8, 0.9)))
                elif nm.startswith('bark_'):
                    k = nm[5:] if os.path.exists(os.path.join(A, 'bark', nm[5:] + '_c.jpg')) else 'oak'
                    if nm not in mats: mats[nm] = bark_mat(k)
                if nm in mats: o.material_slots[i].material = mats[nm]
    for o in new:
        if o.name.startswith('tree|'):
            pts = []
            for ch in o.children_recursive:
                if ch.type == 'MESH': pts += [ch.matrix_world @ Vector(c) for c in ch.bound_box]
            h = max(p.z for p in pts) - min(p.z for p in pts) if pts else 1
            out[o.name] = (o, h)
    return out

def place(lib, name, x, y, h, rot=None, R=random):
    """A linked copy of tree `name`, scaled to `h` feet, at (x, y). Shares mesh data, so it costs no memory."""
    src, h0 = lib[name]
    root = bpy.data.objects.new(name.split('|')[1] + '_inst', None)
    bpy.context.scene.collection.objects.link(root)
    for ch in src.children:
        c = ch.copy(); c.data = ch.data
        bpy.context.scene.collection.objects.link(c); c.parent = root
        c.matrix_parent_inverse = src.matrix_world.inverted()
    s = h / h0
    root.scale = (s, s, s); root.location = (x, y, 0)
    root.rotation_euler = (0, 0, rot if rot is not None else R.uniform(0, 6.283))
    return root

def names(lib, kind):
    return [k for k in lib if k.split('|')[1].startswith(kind)]
