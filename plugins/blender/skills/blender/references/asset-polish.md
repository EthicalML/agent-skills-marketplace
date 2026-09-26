# Polish a reconstructed character

Use this procedure when a reconstruction is recognizable but does not meet the requested surface, likeness, or animation quality. Read it before scheduling another full animation render. These are researched methods and proposed automation paths, not a claim that the skill already implements automatic character retopology. Research checked on 2026-09-26; probe the installed Blender API before using version-specific settings.

## 1. Define and record the quality gate

Separate three deliverables: a polished static asset, an asset that survives the requested performance, and a reusable production character. Name which one is required. Preserve the raw reconstruction and the latest working scene. Create a project defect register with region, reference view, visible problem, likely cause, next intervention, acceptance evidence, and status. Keep observed findings separate from hypotheses and researched methods.

Render fixed front, oblique, profile, rear, and closeup views in neutral clay, with wireframe and final-material comparisons. Use identical framing, lighting, exposure, and subdivision settings across revisions. Check primary volumes before detail. Review the full silhouette, muzzle depth, eye placement, mouth corners, ear thickness, hand proportions, shoe shape, shoulder joins, and hidden surfaces. A smooth render can still have the wrong design. The artist workflow in [Pierrick Picaut's character breakdown](https://blog.cgcookie.com/posts/workflow-tips-from-pierrick-picaut-creating-a-stylized-blender-character/) prioritizes proportions before detail and loops around articulating regions; our automation proposal is a landmark and fixed-view review gate before surface refinement.

Record camera assumptions: unrelated screenshots may use different perspective, poses, and even models. Do not average incompatible views or fit their pixel coordinates as if calibrated. Mark inferred rear anatomy as a design decision, not recovered evidence.

For tested failure cases and the bounded regional procedure, read [regional surface experiments](../docs/regional-surfaces.md). Use [quality review](../docs/quality-review.md) to distinguish a smooth prototype from a reference-matched, deformable character.

## 2. Choose repair, replacement, or another reconstruction per region

Classify defects before selecting tools:

| Defect | First intervention | Reject the candidate when |
| --- | --- | --- |
| Shading stripes with plausible shape | Inspect winding, custom normals, sharp edges, duplicates | Neutral geometry remains cracked or the silhouette changes |
| Small isolated noise on a sound surface | Masked relaxation or low-resolution cage deformation | Creases soften, volume collapses, or landmarks drift |
| Widespread cracks, paper-thin shells, invented relief | Rebuild a clean surface using the original only as a guide | Projection reproduces the defects |
| Wrong anatomy or silhouette | Fit or rebuild primary forms; reconsider source views | Higher resolution only sharpens the wrong form |
| Fused digits or accidental bridges | Replace the affected region and inspect each intended gap | A topology count passes but the anatomy is still wrong |
| Bad joint deformation | Correct topology and weights, then corrective shapes if needed | Smoothing only conceals collapse in one pose |

Keep a stop rule: after two local variants fail to improve a named defect without damaging adjacent regions, switch method rather than accumulating patches. This is a workflow heuristic, not a measured optimal retry count. Budget by region and preserve the best candidate.

Do not infer that a generation backend promises animation topology. [TRELLIS.2's own repository](https://github.com/microsoft/TRELLIS.2) explicitly supports open and non-manifold structures and distinguishes geometry from material generation. Its published CUDA timings and hardware requirements do not establish performance or feature parity for an Apple Silicon port.

## 3. Establish a clean, controllable base

Keep the useful likeness and proportions, not necessarily the generated triangles. Choose a fitted base mesh, manually designed loop patches constructed through Python, or clean parametric surfaces for simple regions. Use separate meshes at intentional clothing/accessory boundaries. Avoid arbitrary overlaps at exposed shoulders, mouth corners, and wrists. Symmetry can establish a baseline; preserve intentional asymmetry after the baseline passes.

For scripts, represent important contours as named curves or ordered landmark samples. Construct ring/strip meshes with explicit connectivity, bridge compatible loops, and use Mirror/Subdivision for controlled surfaces. A smooth sphere assembly remains a blockout unless the transitions and silhouette match the design. The agent must choose the topology layout; BMesh is an implementation mechanism, not an anatomy solver.

For a face, plan eye and mouth loops, eyelid thickness, mouth interior, expression range, and the placement of poles before filling remaining patches. [Blender Studio's live-retopology breakdown](https://studio.blender.org/blog/live-retopology-at-bcon22/) maps edge flow, creases, articulation, expression bounds, and landmarks before filling topology. Translate that into named loop sets and deformation requirements; do not treat an all-quad count as the acceptance test.

## 4. Fit and relax without copying the damage

Fit the clean cage to approved primary forms, using a clean proxy when the raw reconstruction is noisy. Constrain fitting to the intended part. Start with broad shape changes through cage/lattice controls, then smaller adjustments. For Shrinkwrap, explicitly select method, direction, offset, maximum distance where available, and affected vertex group. Inspect projection misses and wrong-surface hits around thin lips, fingers, and overlapping clothes. [The Shrinkwrap manual](https://docs.blender.org/manual/en/4.2/modeling/modifiers/deform/shrinkwrap.html) documents the projection choices; none identifies anatomical correspondence for the agent.

Pin landmarks, boundaries, and crease loops while relaxing filler vertices. A proposed Python implementation alternates masked neighbor relaxation with bounded projection through `mathutils.bvhtree.BVHTree`; accept a move only if it respects the region and displacement limit. Use staged snapshots and inspect drift. [Blender Studio's pinning/relaxing article](https://studio.blender.org/blog/retopology-modifiers-pinning-relaxing/) demonstrates selective pins and automatic filler distribution, but also documents prototype issues and unstable live relaxation. Its downloadable node tools are an optional experiment, not an installed dependency or a verified headless API.

## 5. Evaluate remeshing as a candidate, not a final rigging decision

Try QuadriFlow only on an appropriate isolated copy, with recorded target density and symmetry settings; compare against a deliberately constructed cage. Curvature-following quads do not establish the mouth/eyelid loops or joint behavior this character needs. Voxel remeshing can help join volumes but can close gaps or discard attributes. Check data preservation and anatomy after every topology-changing step. See the [Blender retopology manual](https://docs.blender.org/manual/en/3.0/modeling/meshes/retopology.html) for the distinction between volume remeshing and quad remeshing; use runtime inspection for current operator arguments.

For optional assisted tooling, [RetopoFlow Contours](https://docs.retopoflow.com/v4/contours.html) describes contour loops for tubular forms with walking, distance-field, and raycast methods; [PolyStrips](https://docs.retopoflow.com/v3/polystrips.html) describes spline-guided strips. These suggest programmable cross-section and curve-strip builders. Check the installed release, license, and exposed operators before integration. Modal mouse tools are not automatically callable as a stable batch API. Do not install a commercial dependency or claim compatibility based only on a tutorial.

## 6. Recover intentional detail and materials

After the base shape passes, add controlled detail with Multires or selective projection. Keep lower levels editable and restrict transfer to approved regions. [Multires documentation](https://docs.blender.org/manual/en/4.4/modeling/modifiers/generate/multiresolution.html) describes reprojection and requires matching topology/vertex indices for Reshape; an arbitrary new cage and raw reconstruction do not meet that requirement. Never transfer the original cracks simply to preserve apparent detail.

Create UVs or deliberate rest-space color boundaries on the new surface. Check seams, stretching, texel consistency, and boundary placement in neutral light. [Data Transfer](https://docs.blender.org/manual/en/4.3/modeling/modifiers/modify/data_transfer.html) can move supported attributes between meshes, but mapping errors remain possible between nearby parts. Transfer weights as an initial estimate only; normalize and test them.

If using high-to-low baking, specify source/target selection, active UV/image nodes, cage or ray distance, margins, and tangent-space conventions. Run a small regional bake first and inspect misses, seams, and contamination. [Cycles baking documentation](https://docs.blender.org/manual/de/4.5/render/cycles/baking.html) explains selected-to-active projection and cage control. A normal map does not repair silhouette, holes, or deformation. For a clean stylized character, intentionally omitting reconstructed surface noise can be the correct decision.

## 7. Build deformation and facial controls on stable topology

Test elbow, shoulder, wrist, knee, and neck poses on the new base before polishing motion. Sample intermediate poses, not only keys. Use explicit masks/weights and review volume and contact. [Corrective Smooth](https://docs.blender.org/manual/id/4.0/modeling/modifiers/deform/corrective_smooth.html) can reduce deformation distortion, with rest-state and binding requirements; it does not create missing joint loops.

For proper blinks, build eyelids that follow the eye surface and meet without penetration. Squashing an eyeball mesh is a prototype gesture, not a finished eyelid solution. Create smile, mouth-open, and blink shapes with stable vertex correspondence; use pose-driven correctives where a particular bend needs adjustment. Export drivers/modifiers only through supported baked animation or deformation representations and verify the result. Keep independent finger controls as a separate requirement from a waving rigid glove.

## 8. Validate quality and portability separately

Keep topology checks, appearance checks, and deformation checks separate. Count boundary/non-manifold edges and connected components only against expected regional topology. Euler characteristic is useful for an intended closed glove, not a universal rule for an open mouth or clothing shell. Use candidate self-intersection/proximity reports to guide visual inspection; a BVH overlap query alone is not a complete self-intersection proof.

At a fixed reference camera, silhouette overlap and normalized landmark error can detect regression. Use two-sided sampled surface distance to approved clean geometry where meaningful; closeness to a defective raw mesh is not a quality objective. Set tolerances from the deliverable scale and approved reference, not invented universal thresholds. Keep artist/agent visual judgment explicit.

Render neutral and final-material views, a turntable, and a short stress-pose clip before the complete performance. Reimport the deliverable and compare evaluated vertex positions or world-space bounds at rest, maximum bends, closed eyes, and contact frames. Bounds can miss local finger or eyelid defects, so retain closeup checks. Verify clip grouping, colors, resources, frame rate, and complete video decoding through the existing animation workflow.

## 9. Track implementation workstreams honestly

Keep a project table with dependency, status, artifact, acceptance gate, next experiment, and measured runtime. Use statuses `observed`, `researched`, `API-probed`, `implemented`, and `validated on this asset`; do not promote a workstream because its documentation exists.

| Workstream | Concrete output to implement | First meaningful acceptance test |
| --- | --- | --- |
| Reference and defect review | Fixed review cameras, regional defect register, normalized landmarks | Expose a known silhouette and rear-surface defect without changing framing |
| Regional audit | Mesh/attribute report with named regions and isolated candidates | Detect a fused-digit fixture and an intentional open boundary without conflating them |
| Cage fitting and selective relaxation | Named pins, region masks, bounded projection, before/after renders | Clean one cheek/ear while preserving approved silhouette and nearby mouth |
| Loop and patch construction | Explicit eye/mouth loops and bridged quad strips | Subdivide and perform blink/mouth-open without collapse |
| UV/material/detail transfer | Seam plan, color map, small bake, mapping report | No cross-part contamination or reintroduced surface cracks |
| Deformation and facial controls | Weight audit, stress poses, eyelid/pose corrective shapes | Continuous closure and acceptable joint volumes through intermediate frames |
| Visual regression | Comparable views, mask/landmark metrics, recorded visual decision | Reject a technically valid but visibly worse candidate |
| Portable delivery | Baked export plus reimport geometry/animation comparisons | Preserve the approved motion, materials, and local facial details |

Implement small project functions first. Promote them into skill utilities only after real use and a failure-sensitive test. The live Python connection already exposes Blender execution; changing the transport does not supply these modeling decisions. Reuse the existing background job and validation infrastructure instead of adding another task framework.

## 10. Record the next bounded experiment

Select the highest-visibility unresolved region, normally the face, and compare at most a few materially different methods under identical views. Record elapsed work and outcome. If the clean head prototype passes, expand to torso/feet, then transfer materials and rebuild deformation. If it fails, record whether correspondence, topology design, or visual judgment was responsible before estimating the remaining project. Do not promise production quality from an unbenchmarked automatic retopology path.
