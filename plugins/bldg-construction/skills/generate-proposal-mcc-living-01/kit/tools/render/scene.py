# Cycles scene for the Cooper Barn: the GLB from the kit, a physical sky, a lawn and a tree line.
import bpy, math, random, sys, os, mathutils
TREE = None
from mathutils import Vector

def build(glb, sun_az=215, sun_el=32, trees=True, seed=7):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=glb)
    # world: physical sky
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    sky = nt.nodes.new('ShaderNodeTexSky')
    try: sky.sky_type = 'MULTIPLE_SCATTERING'
    except Exception:
        try: sky.sky_type = 'NISHITA'
        except Exception: pass
    sky.sun_elevation = math.radians(sun_el); sky.sun_rotation = math.radians(sun_az)
    try: sky.air_density = 1.0; sky.aerosol_density = 1.6
    except Exception: pass
    bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.18
    try: sky.sun_disc = False
    except Exception: pass
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(sky.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
    # sun lamp along the same direction
    sd = bpy.data.lights.new('Sun', 'SUN'); sd.energy = 3.2; sd.angle = math.radians(1.2); sd.color = (1.0, 0.86, 0.72)
    so = bpy.data.objects.new('Sun', sd); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(90 - sun_el), 0, math.radians(-(sun_az + 180)))   # sun_az: compass bearing of the sun
    # lawn
    bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, -0.02)); g = bpy.context.object; g.name = 'Lawn'
    m = bpy.data.materials.new('Lawn'); m.use_nodes = True; n = m.node_tree.nodes; L = m.node_tree.links
    bsdf = n['Principled BSDF']; bsdf.inputs['Roughness'].default_value = 0.95
    tc = n.new('ShaderNodeTexCoord'); nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.08; nz.inputs['Detail'].default_value = 6
    nz2 = n.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 3.0; nz2.inputs['Detail'].default_value = 8
    ramp = n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (0.085, 0.115, 0.035, 1); ramp.color_ramp.elements[1].color = (0.19, 0.22, 0.075, 1)
    mix = n.new('ShaderNodeMix'); mix.data_type = 'FLOAT'; mix.inputs['Factor'].default_value = 0.35
    L.new(tc.outputs['Object'], nz.inputs['Vector']); L.new(tc.outputs['Object'], nz2.inputs['Vector'])
    L.new(nz.outputs['Fac'], mix.inputs[2]); L.new(nz2.outputs['Fac'], mix.inputs[3]); L.new(mix.outputs[0], ramp.inputs['Fac']); L.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bump = n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.4; L.new(nz2.outputs['Fac'], bump.inputs['Height']); L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    g.data.materials.append(m)
    if trees: tree_line(seed)
    # render settings
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.use_denoising = True
    try: sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    return sc

def card_mat(name, img, tint=(1, 1, 1, 1)):
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree.nodes; L = m.node_tree.links
    b = n['Principled BSDF']; b.inputs['Roughness'].default_value = 0.75
    t = n.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(img)
    hsv = n.new('ShaderNodeHueSaturation'); hsv.inputs['Value'].default_value = tint[0]
    L.new(t.outputs['Color'], hsv.inputs['Color']); L.new(hsv.outputs['Color'], b.inputs['Base Color']); L.new(t.outputs['Alpha'], b.inputs['Alpha'])
    try: b.inputs['Subsurface Weight'].default_value = 0.0
    except Exception: pass
    try:
        tr = b.inputs.get('Transmission Weight')
    except Exception: pass
    m.blend_method = 'HASHED' if hasattr(m, 'blend_method') else None
    return m

def card(name, mat, size):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, -500)); c = bpy.context.object; c.name = name
    c.data.materials.append(mat); return c

def tree_line(seed, cen=None, count=70, rmin=75, rmax=190, around=(-0.15, 1.15), kinds=None):
    R = random.Random(seed)
    D = os.path.dirname(os.path.abspath(__file__))
    cards = [card('LeafA', card_mat('LeafA', os.path.join(D, 'leaf_a.png')), 4.4), card('LeafB', card_mat('LeafB', os.path.join(D, 'leaf_b.png'), (0.8,)), 4.4)]
    ncard = card('Needle', card_mat('Needle', os.path.join(D, 'needle.png')), 4.0)
    coll = bpy.data.collections.new('LeafCards'); bpy.context.scene.collection.children.link(coll)
    for c in cards: 
        for u in c.users_collection: u.objects.unlink(c)
        coll.objects.link(c)
    shell = bpy.data.materials.new('Shell'); shell.use_nodes = True; shell.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.012, 0.022, 0.006, 1); shell.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1.0
    shell2 = bpy.data.materials.new('Shell2'); shell2.use_nodes = True; shell2.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.01, 0.02, 0.01, 1)
    bark = bpy.data.materials.new('Bark'); bark.use_nodes = True; bark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.05, 0.04, 0.032, 1)
    if cen is None:
        objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name not in ('Lawn',) and not o.name.startswith(('Leaf', 'Needle'))]
        mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
        for o in objs:
            for c in o.bound_box:
                p = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, p)); mx = Vector(map(max, mx, p))
        cen = (mn + mx) / 2
    def scatter(obj, inst, n, size):
        ps = obj.modifiers.new('p', 'PARTICLE_SYSTEM').particle_system; st = ps.settings
        st.type = 'HAIR'; st.count = n; st.use_advanced_hair = True; st.render_type = 'OBJECT'; st.instance_object = inst
        st.particle_size = size; st.size_random = 0.5; st.display_percentage = 0; st.use_rotations = True; st.rotation_mode = 'NOR'; st.phase_factor_random = 2.0; st.rotation_factor_random = 0.6
        st.hair_length = 1; st.emit_from = 'FACE'; obj.show_instancer_for_render = obj.data.materials[0].name == 'Shell'; st.use_emit_random = True; ps.seed = R.randint(0, 10000)
    def hardwood(x, y, h):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=h * 0.016, depth=h * 0.62, location=(x, y, h * 0.31)); bpy.context.object.data.materials.append(bark)
        for k in range(R.randint(6, 10)):
            r = h * R.uniform(0.12, 0.19); a = R.uniform(0, 6.28); d = h * R.uniform(0, 0.17)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(x + math.cos(a) * d, y + math.sin(a) * d, h * R.uniform(0.52, 0.86)))
            s = bpy.context.object; s.data.materials.append(shell); s.scale = (0.82, 0.82, 0.82)
            md = s.modifiers.new('d', 'DISPLACE'); tx = bpy.data.textures.new('c%d' % R.randint(0, 10**9), 'CLOUDS'); tx.noise_scale = r * 0.4; md.texture = tx; md.strength = r * 0.3
            scatter(s, R.choice(cards), int(320 * (r / 8) ** 2), R.uniform(0.9, 1.3))
    def conifer(x, y, h):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=h * 0.013, depth=h * 0.85, location=(x, y, h * 0.42)); bpy.context.object.data.materials.append(bark)
        bpy.ops.mesh.primitive_cone_add(vertices=14, radius1=h * 0.17, depth=h * 0.82, location=(x, y, h * 0.55))
        c = bpy.context.object; c.data.materials.append(shell2)
        c.scale = (0.85, 0.85, 1.0)
        scatter(c, cards[1], int(900 * (h / 60) ** 2), 0.75)
    global TREE
    def TREE(kind, x, y, h, low=False):
        if kind == 'conifer': return conifer(x, y, h)
        if not low: return hardwood(x, y, h)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=h * 0.016, depth=h * 0.5, location=(x, y, h * 0.25)); bpy.context.object.data.materials.append(bark)
        for k in range(R.randint(9, 14)):
            r = h * R.uniform(0.13, 0.21); a = R.uniform(0, 6.28); d = h * R.uniform(0, 0.2)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(x + math.cos(a) * d, y + math.sin(a) * d, h * R.uniform(0.3, 0.86)))
            s = bpy.context.object; s.data.materials.append(shell); s.scale = (0.82, 0.82, 0.82)
            scatter(s, R.choice(cards), int(320 * (r / 8) ** 2), R.uniform(0.9, 1.3))
    for i in range(count):
        ang = R.uniform(*around) * math.pi; dist = R.uniform(rmin, rmax)
        x, y = cen.x + math.cos(ang) * dist * 1.25, cen.y + math.sin(ang) * dist
        h = R.uniform(48, 82) * (1 + 0.25 * (dist - rmin) / max(1, rmax - rmin))
        k = kinds or ('conifer' if R.random() < 0.4 else 'hardwood')
        (conifer if k == 'conifer' else hardwood)(x, y, h)

def camera(sc, pos, look, lens=50):
    cd = bpy.data.cameras.new('Cam'); cd.lens = lens; co = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(co)
    co.location = pos
    d = Vector(look) - Vector(pos); co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co; return co

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
