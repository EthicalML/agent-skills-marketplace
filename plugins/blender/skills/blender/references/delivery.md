# Validate and deliver

1. Run `B.validate(collection=..., mesh=True)` where geometry matters. It checks base meshes, not evaluated modifiers. Interpret non-manifold counts according to whether the object should be watertight. Inspect dimensions, scale, normals, UVs, modifier state, animation, and material nodes according to the deliverable. Missing resource checks cover file images and linked libraries; UDIM tiles, sequences, simulation caches, fonts, and compositor resources need task-specific checks.

2. Save the final .blend using `B.save(path, pack=True)` when a portable file is required. Packing does not guarantee every external cache or linked library is embedded. Preserve required adjacent resources and record their relative locations. Don't overwrite the original file unless requested.

3. Export intended objects with `B.export_scene(path, object_names=[...])`. Choose GLB for a self-contained interchange asset, or the requested format. For rigged or shape-key assets, consider apply_modifiers=False and verify deformation after reimport. Arbitrary Blender shader graphs do not fully survive GLB; visual equivalence needs checking, not assuming.

4. Call `B.verify_file(path, output_dir)` and poll the returned job. It opens a .blend or imports a GLB/FBX in an isolated Blender process, writes a report, and fails on empty scene content or missing resources. Read its report; compare the resulting object types/counts and bounds with the intended selection. For rigs and animation, add a script that verifies the actual channels/deformation and sample frames; basic reimport does not prove them.

5. Inspect a final render and any additional angles/frames needed to assess the brief. Deliver the files plus a concise account of what was checked and what remains unverified. Keep build scripts if reproducibility is part of the task. Do not include credentials or private user paths in public benchmark reports.
