# Compare adaptation with independent reconstruction

Use this workflow when a real reference mesh becomes available and the task could either reuse it or reconstruct its appearance. Keep the source and accepted model unchanged. These methods were exercised on one rigged stylized character and one static authored reconstruction; they are not a general character-fitting system.

## 1. Give each route a bounded task

Run adaptation and reconstruction in separate directories and background Blender processes. Disable source-file script auto-execution, cap render threads, and avoid concurrent writes to the GUI scene. Record the source, attribution, pose, chosen region, expected improvement, and output paths. Use a few static closeups before any animation render.

For adaptation, preserve mesh coordinates, topology, UVs, weights, material assignments, and bind/rest data. For reconstruction, identify pinned regions and attachments before changing geometry. Do not copy target geometry while describing the result as independently reconstructed.

## 2. Inspect pose dependencies before neutralizing an imported rig

Compare the supplied pose with rest mode. If eyes disappear, inspect eyelids and occlusion before moving pupils or rebuilding surfaces. In the tested asset, rest-mode eyelids covered the pupils; the supplied facial pose held them open. Rays toward the eye region hit eyelids in rest mode and pupils after the facial pose was retained. This finding explains that asset, not every missing-eye symptom.

Use [scripts/pose.py](../scripts/pose.py) inside Blender for `snapshot_pose(armature)`, `restore_pose(armature, snapshot)`, and `reset_except(armature, snapshot, preserve)`. These helpers snapshot each pose bone's `matrix_basis`. Inspect actions, NLA tracks, drivers, and constraints before changing the pose; these can overwrite or alter direct transforms. On a rig without those dependencies, reset only the intended body/head pose transforms and preserve explicitly selected facial descendant transforms. Keep `pose_position = 'POSE'`; do not apply a pose as rest merely to inspect proportions. Update the dependency graph and render the face before continuing.

Treat a matrix-basis snapshot as a pose-transform snapshot only. It does not capture animation, constraints, drivers, rest data, or object transforms. Restore it between tests. Explicitly validate bone names before mutation; a semantic facial-bone list is asset-specific, not a universal naming rule.

## 3. Review adaptation without overstating rig readiness

Inspect front, rear, profile, and three-quarter views. Apply a few named, bounded static bone perturbations, restoring the snapshot between them. Inspect shoulder, wrist, and eyelid behavior separately. Finite coordinates and a successful restore do not establish collision-free motion or expression coverage.

Save and reopen in a new process. Compare source/candidate fingerprints of raw mesh coordinates, topology, UVs, vertex weights, and material-slot assignments. Record fingerprint scope: matching assignments does not prove material node graphs unchanged. Verify images and rig dependencies separately. The tested adaptation preserved 15 meshes and 91 bones; only limited static perturbations were reviewed, not production animation or export.

## 4. Evaluate a bounded reconstruction edit

Use a compact-support displacement field or explicit control cage with known zero-influence regions. Record maximum displacement, pin masks, attachment behavior, and parameters. Transform world-space displacements correctly into local coordinates; rigid nose or eye attachments may need separate treatment.

Reopen the output and compare actual coordinates with the baseline. Check pinned-region movement, untouched objects, topology, attributes, and finite values. Render baseline and candidate with identical cameras and framing. If reference framing is normalized separately, label it as qualitative comparison rather than pixel correspondence.

Reject a candidate whose profile or anatomy is worse even if every numerical check passes. In the tested muzzle edit, increased depth preserved topology and pins but produced a pointed, duck-like profile. It demonstrated bounded editing, not improved likeness. A useful next intervention needs cheek, upper/lower lip, and mouth-corner structure, not simply more displacement.

## 5. Save findings at their tested scope

Keep source, candidate, before/after evidence, scripts, timings, rejected variants, and remaining gaps in the project. Retain useful pose and regional-edit helpers as project utilities first. Promote general helpers only after they handle a real case and a failure-sensitive check; keep character-specific names and coordinates out of portable defaults.

Low-resolution static CPU renders in this experiment took under one second to roughly three seconds per image; the regional mesh edit took under one second. These are measured local results, not timing guarantees. Fast image feedback made the incorrect profile cheap to reject.

Require an explicit completion report and inspect failures in the log. One tested Blender process returned exit code zero after a Python traceback; process success alone did not establish script completion.
