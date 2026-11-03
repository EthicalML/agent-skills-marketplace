# Blender 5.x API notes

Verified on Blender 5.2 LTS, headless. Each line is a change or trap that cost a failed render.

## Rendering and colour

- The EEVEE engine identifier is `BLENDER_EEVEE`. `BLENDER_EEVEE_NEXT` no longer exists.
- Set `view_settings.view_transform = 'AgX'` before setting `look`; look names are `'AgX - Punchy'`, `'AgX - Medium High Contrast'`, and so on.
- AgX pushes very bright emission towards white. For a saturated glow, keep emission strength moderate (roughly 2–20) and use a deeply saturated colour ramp, then let bloom carry the brightness.
- `Material.use_nodes` and `World.use_nodes` print a deprecation warning but are still required. Ignore the warning.

## Lighting and reflections (EEVEE)

- A shader on the world `Volume` socket blocks all world lighting and reflections. Put haze in a volume object (a large cube with Principled Volume) that encloses the camera.
- EEVEE traces reflections in screen space. Emissive objects hidden from the camera (`visible_camera = False`) do not appear in reflections. To give metals something to reflect, light them from the world.
- For a dark backdrop with a bright reflection environment, mix two world backgrounds with Light Path `Is Camera Ray`: dark for camera rays, a studio gradient or HDRI for everything else. This works only once the world `Volume` socket is empty.
- A light inside an emissive sphere is shadowed by it. Set `visible_shadow = False` on the emitter.

## Compositor

- The compositor is a node group, not `scene.node_tree`: create `bpy.data.node_groups.new(name, 'CompositorNodeTree')`, add an `Image` output to its interface, assign it to `scene.compositing_node_group`, and link the result into a `NodeGroupOutput`.
- Glare settings are input sockets, not properties: `inputs["Type"].default_value = 'Bloom'`, plus `Threshold`, `Strength`, `Size`, `Quality`. `glare_type` no longer exists.
- Lens Distortion takes `Distortion` and `Dispersion` as inputs.

## Animation

- Set `bpy.context.preferences.edit.keyframe_new_interpolation_type` (`'LINEAR'`, `'BEZIER'`) before `keyframe_insert`. Do not edit interpolation through `action.fcurves`: actions are slotted and that path is gone.
- Python-expression drivers do not run in background mode without auto-exec. Use keyframes, or Geometry Nodes `Scene Time` for procedural motion.
- Animate a node value with `node.inputs["W"].keyframe_insert("default_value", frame=f)`.

## Nodes

- `ShaderNodeMix` has typed sockets addressed by index: Factor `0`; A/B float `2`/`3`, vector `4`/`5`, colour `6`/`7`. Outputs: float `0`, vector `1`, colour `2`. Set `data_type` first.
- Geometry Nodes groups need an explicit interface: `ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')`. `GeometryNodeInputSceneTime` outputs `Seconds` and `Frame`.
- World `Texture Coordinate > Generated` is the view direction, so its Z runs from -1 (down) to 1 (up).

## Meshes

- `mesh.shade_smooth()` replaces the old operator. A Bevel modifier with `harden_normals = True` gives clean highlights without auto-smooth.
- Build geometry with `bmesh` from parameters (profiles, counts, radii) rather than editing primitives through operators; it needs no context and stays exact.

## When an identifier is unknown

Print it from the live build rather than guessing: `[s.name for s in node.inputs]`, `[p.identifier for p in bpy.types.X.bl_rna.properties]`, or an enum's `bl_rna.properties[name].enum_items`. Add a line here if it was a trap.
