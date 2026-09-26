# Iteration

Keep construction scripts in the user's project so the result can be reproduced. Accept task parameters through `PARAMS`, name task-owned collections and objects consistently, and update those objects rather than deleting unrelated work. After changing dependencies call `bpy.context.view_layer.update()` before reading evaluated dimensions. Use explicit collection links and context overrides where operators require a particular scene, area, mode, or selection.

A new `bpy.data.scenes.new(...)` scene may have no world or camera. Create and assign both explicitly before configuring lighting or rendering.

Inspect geometry from useful angles. Camera previews show composition and occlusion; additional cameras expose hidden joins or intersections. For cameras and lights, aim with a tracking quaternion:

```python
from mathutils import Vector

obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
```

For material and lighting decisions:

```python
job = B.render_preview(
    "/absolute/project/tmp/previews", camera="ProductCamera", resolution=768
)
# Save this result locally: job['job_dir'] and job['image'] are needed later.
progress = job_status(job["job_dir"])
# Only after state == 'succeeded', open job['image'] with the host image viewer.
```

The preview retains the scene's render engine and color management. Cycles defaults to 32 samples in this helper; increase only when noise obscures the decision. The helper changes preview resolution in the snapshot, not the live scene. Render filenames are unique per iteration. Viewport images use B.screenshot; final lighting needs an actual render.

Make criticism concrete: clipped silhouette, unreadable focal point, floating contact, distracting reflection, missing texture, harsh shadow, wrong proportion. Change the relevant geometry, camera, material, or light, then compare the next image. An agent should not claim it inspected a preview unless it actually opened the image.

For animation, inspect representative start, middle, end and contact/transition frames. Use `render_preview(frame=...)` for those checks, then a background script for the full sequence. Inspect animation channels via object_info and live API lookup: Blender 5 uses action slots/layers rather than assuming legacy action.fcurves.

A saved checkpoint is the recovery mechanism for partially applied scripts. To restore one in the GUI, use explicit `bpy.ops.wm.open_mainfile(filepath=...)` only when discarding changes since that checkpoint is intended. Reconnect and inspect after a file load. Prefer inspecting checkpoints in background Blender when recovery is not needed.
