"""Scene template (Blender 5.x). Copy into the project, keep the helpers, replace SUBJECT.

Build-only: bl.py handles saving, preview overrides, and rendering.
"""
import bpy, bmesh, math, sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FPS, FRAMES = 24, 240
TAU = math.tau

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.frame_start, scene.frame_end, scene.render.fps = 1, FRAMES, FPS
prefs = bpy.context.preferences.edit
prefs.keyframe_new_interpolation_type = 'LINEAR'   # set before inserting keys; 'BEZIER' for camera moves


# ---------------------------------------------------------------- helpers
def link(obj, parent=None):
    scene.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj

def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.location, e.rotation_euler = loc, rot
    return link(e, parent)

def mesh_obj(name, build, mat=None, loc=(0, 0, 0), parent=None, smooth=True):
    """build(bm) fills a bmesh; returns the linked object."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
    if smooth:
        me.shade_smooth()
    if mat:
        me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    return link(o, parent)

def bevel(obj, width, segments=2):
    b = obj.modifiers.new("bevel", 'BEVEL')
    b.width, b.segments, b.limit_method, b.harden_normals = width, segments, 'ANGLE', True
    return obj

def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    return m, nt, nt.nodes.new("ShaderNodeOutputMaterial")

def node(nt, kind, **inputs):
    """Inputs by socket name; keys starting with '_' set node properties (e.g. _operation='MULTIPLY')."""
    n = nt.nodes.new(kind)
    for k, v in inputs.items():
        if k.startswith("_"):
            setattr(n, k[1:], v)
        else:
            n.inputs[k].default_value = v
    return n

def ramp(nt, stops):
    r = nt.nodes.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    while len(els) < len(stops):
        els.new(0.5)
    for el, (pos, col) in zip(els, stops):
        el.position, el.color = pos, (*col, 1) if len(col) == 3 else col
    return r

def metal(name, color, rough=0.2, grime=0.4):
    """Metal with noise-varied roughness and AO-darkened crevices. Reads as metal only if the world gives it something to reflect."""
    m, nt, out = new_mat(name)
    p = node(nt, "ShaderNodeBsdfPrincipled", Metallic=1.0)
    tc = node(nt, "ShaderNodeTexCoord")
    noise = node(nt, "ShaderNodeTexNoise", Scale=18.0, Detail=8.0)
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    ao = node(nt, "ShaderNodeAmbientOcclusion", Distance=0.05)
    dirt = node(nt, "ShaderNodeMath", _operation='MULTIPLY')
    nt.links.new(ao.outputs["AO"], dirt.inputs[0])
    blot = node(nt, "ShaderNodeMapRange", **{"To Min": 1 - grime, "To Max": 1.0})
    nt.links.new(noise.outputs["Fac"], blot.inputs["Value"]); nt.links.new(blot.outputs["Result"], dirt.inputs[1])
    col = ramp(nt, [(0.35, tuple(c * 0.3 for c in color)), (0.75, color)])
    nt.links.new(dirt.outputs[0], col.inputs["Fac"]); nt.links.new(col.outputs["Color"], p.inputs["Base Color"])
    rr = node(nt, "ShaderNodeMapRange", **{"To Min": rough * 0.6, "To Max": rough * 1.6})
    nt.links.new(noise.outputs["Fac"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    return m

def emission(name, color, strength):
    m, nt, out = new_mat(name)
    e = node(nt, "ShaderNodeEmission", Color=(*color, 1), Strength=strength)
    nt.links.new(e.outputs[0], out.inputs["Surface"])
    return m

def spin(obj, rate_turns, phase=0.0, axis=2):
    """Constant rotation: rate_turns full turns over the shot. Keyframes, not drivers (drivers need auto-exec)."""
    obj.rotation_euler[axis] = phase
    obj.keyframe_insert("rotation_euler", index=axis, frame=scene.frame_start)
    obj.rotation_euler[axis] = phase + rate_turns * TAU
    obj.keyframe_insert("rotation_euler", index=axis, frame=scene.frame_end)

def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

def spot(name, loc, target, watts, color=(1, 1, 1), cone_deg=35, blend=0.5, radius=0.1):
    d = bpy.data.lights.new(name, 'SPOT')
    d.energy, d.color, d.spot_size, d.spot_blend, d.shadow_soft_size = watts, color, math.radians(cone_deg), blend, radius
    o = link(bpy.data.objects.new(name, d)); o.location = loc; aim(o, target)
    return o

# ---------------------------------------------------------------- SUBJECT (replace)
brass = metal("Brass", (0.95, 0.64, 0.25))
plinth = bevel(mesh_obj("Plinth", lambda bm: bmesh.ops.create_cone(
    bm, cap_ends=True, segments=96, radius1=1.2, radius2=1.2, depth=0.3), metal("Gunmetal", (0.12, 0.12, 0.13), 0.35),
    (0, 0, 0.15)), 0.02)
orb = mesh_obj("Orb", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=48, radius=0.5), brass, (0, 0, 0.9))
spin(orb, 0.5)

floor_mat, nt, out = new_mat("Floor")
fp = node(nt, "ShaderNodeBsdfPrincipled", **{"Base Color": (0.01, 0.01, 0.012, 1), "Roughness": 0.25})
nt.links.new(fp.outputs[0], out.inputs["Surface"])
floor = mesh_obj("Floor", lambda bm: bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=200), floor_mat, smooth=False)


# ---------------------------------------------------------------- world, haze, lights
world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
wn = world.node_tree
# Camera sees a dark backdrop; reflections and lighting see a studio (bright top, warm and cool bands).
# This is what makes metal read as metal in a dark scene.
bg = wn.nodes["Background"]
dark = wn.nodes.new("ShaderNodeBackground"); dark.inputs["Color"].default_value = (0.006, 0.008, 0.014, 1)
tc = wn.nodes.new("ShaderNodeTexCoord")
sep = wn.nodes.new("ShaderNodeSeparateXYZ"); wn.links.new(tc.outputs["Generated"], sep.inputs[0])
studio = ramp(wn, [(0.45, (0.0, 0.0, 0.0)), (0.62, (0.25, 0.2, 0.16)), (0.66, (2.5, 2.2, 1.9)), (0.7, (0.2, 0.18, 0.16)),
                   (0.9, (0.6, 0.65, 0.8)), (1.0, (1.5, 1.5, 1.6))])
zn = wn.nodes.new("ShaderNodeMath"); zn.operation = 'MULTIPLY_ADD'
zn.inputs[1].default_value, zn.inputs[2].default_value = 0.5, 0.5   # z in [-1,1] -> [0,1]
wn.links.new(sep.outputs["Z"], zn.inputs[0]); wn.links.new(zn.outputs[0], studio.inputs["Fac"])
wn.links.new(studio.outputs["Color"], bg.inputs["Color"])
lp = wn.nodes.new("ShaderNodeLightPath")
mix = wn.nodes.new("ShaderNodeMixShader")
wn.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
wn.links.new(bg.outputs[0], mix.inputs[1]); wn.links.new(dark.outputs[0], mix.inputs[2])
wn.links.new(mix.outputs[0], wn.nodes["World Output"].inputs["Surface"])
# Haze lives in a volume object, never the world Volume socket: a world volume blocks all world lighting in EEVEE.
HAZE = 0.006                      # density; above ~0.01 washes the frame out; 0 disables
if HAZE:
    haze_mat, nt, out = new_mat("Haze")
    hv = node(nt, "ShaderNodeVolumePrincipled", Density=HAZE, Anisotropy=0.5)
    nt.links.new(hv.outputs[0], out.inputs["Volume"])
    haze = mesh_obj("Haze", lambda bm: bmesh.ops.create_cube(bm, size=1.0), haze_mat, (0, 0, 10), smooth=False)
    haze.scale = (80, 80, 20.6)   # must enclose the camera and everything it sees, or its edges show

spot("Key", (-4, 3, 7), (0, 0, 0.6), 6000, (1.0, 0.85, 0.65), 25, 0.5, 0.05)
spot("Rim", (5, -4, 4), (0, 0, 1.0), 3500, (0.5, 0.7, 1.0), 35, 0.6, 0.3)


# ---------------------------------------------------------------- camera: keyed shots, tracked target, DOF
cam_data = bpy.data.cameras.new("Cam")
cam_data.dof.use_dof = True
cam = link(bpy.data.objects.new("Camera", cam_data)); scene.camera = cam
target = empty("CamTarget")
cam_data.dof.focus_object = target
tr = cam.constraints.new('TRACK_TO'); tr.target = target; tr.track_axis, tr.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
SHOTS = [  # frame, camera location, look-at, lens mm, f-stop
    (1,      (3.0, -3.5, 1.4), (0, 0, 0.9), 50, 2.0),
    (FRAMES, (-2.5, -4.0, 2.2), (0, 0, 0.8), 35, 3.5),
]
prefs.keyframe_new_interpolation_type = 'BEZIER'
for f, cl, tl, lens, fstop in SHOTS:
    cam.location = cl; cam.keyframe_insert("location", frame=f)
    target.location = tl; target.keyframe_insert("location", frame=f)
    cam_data.lens = lens; cam_data.keyframe_insert("lens", frame=f)
    cam_data.dof.aperture_fstop = fstop; cam_data.dof.keyframe_insert("aperture_fstop", frame=f)
prefs.keyframe_new_interpolation_type = 'LINEAR'


# ---------------------------------------------------------------- render + colour
r = scene.render
r.engine = 'BLENDER_EEVEE'
r.resolution_x, r.resolution_y = 1920, 1080
r.use_motion_blur, r.motion_blur_shutter = True, 0.4
ee = scene.eevee
ee.taa_render_samples = 64
ee.use_raytracing = True
ee.use_fast_gi = True
ee.use_shadows = True
ee.volumetric_tile_size = '4'
ee.use_volumetric_shadows = True
vs = scene.view_settings
vs.view_transform = 'AgX'
vs.look = 'AgX - Punchy'
vs.exposure = 0.0

# compositor (5.x): a node group assigned to the scene, ending in a Group Output
comp = bpy.data.node_groups.new("Comp", 'CompositorNodeTree')
comp.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
scene.compositing_node_group = comp
rl = comp.nodes.new("CompositorNodeRLayers")
glare = comp.nodes.new("CompositorNodeGlare")
glare.inputs["Type"].default_value = 'Bloom'
glare.inputs["Threshold"].default_value = 1.2
glare.inputs["Strength"].default_value = 0.5
go = comp.nodes.new("NodeGroupOutput")
comp.links.new(rl.outputs["Image"], glare.inputs["Image"])
comp.links.new(glare.outputs["Image"], go.inputs[0])
