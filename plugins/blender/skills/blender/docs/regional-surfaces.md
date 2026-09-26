# Regional surface experiments

Use this workflow when a reconstructed region has useful proportions but contains cracks, thin sheets, false relief, or dense surface noise. This records tested experiments on one stylized head; it does not establish automatic retopology or reference-quality facial anatomy.

## 1. Preserve the source and establish comparison views

Keep the raw mesh, latest working asset, and candidate scripts separate. Load the saved source in an isolated Blender process. Use rest pose when extracting geometry from a rigged source. Set render resolution, scale percentage, samples, and color management explicitly; a consolidated builder can inherit different settings from the original source than from an intermediate trial. Confirm dimensions from the images. Define fixed front, oblique, profile, and rear cameras with identical framing and lights for all candidates. Render before editing, then render each candidate with the same settings. Add clay views to separate form from material boundaries.

Restrict edits to the intended region and inspect the adjoining neck, clothing, and accessories. A cut plane that seems safe from the front can leave a floating fragment or remove adjacent anatomy. Do not overwrite the current GUI project during trials.

## 2. Reject a failed volume interpretation

A tested head-only voxel remesh used 0.010 scene-unit voxels followed by Smooth factor 0.7 for 12 iterations. It produced 316,600 vertices, 318,378 faces, and zero non-manifold edges in about six seconds for the geometry stage. The rendered face and ears were nevertheless severely perforated. The input's thin/inconsistent surface structure was not converted into the intended solid form. This is an observed failure with a likely volume-interpretation cause, not proof that every regional remesh fails.

Do not tune render settings to hide this outcome. Reject the candidate. A manifold mesh can contain many unwanted holes/handles and disconnected closed pieces. Zero non-manifold edges is not a visual or anatomical acceptance criterion.

## 3. Test bounded reference sampling when the form permits it

A second experiment sampled radial rays around a head center, built an ordered latitude/longitude surface, and filtered the sampled distances with a median pass and local relaxation. It used 24,384 rays; about 83.4% passed the region and distance filters. Misses used an explicit ellipsoid fallback. Clean parametric ears replaced the damaged ones.

The resulting continuous head removed perforations but retained low-frequency lumps, weakened the nose, and represented the mouth badly in profile. It was kept as experiment evidence and rejected as the final head. The ray hit fraction measures coverage, not likeness.

If trying this method:

1. Choose a center, finite ray interval, allowed region, and permitted distance range. Record rejected hits and fallback use. Rays from outside toward the center must not silently sample an ear, opposite surface, or nearby limb.
2. Build explicit, periodic mesh connectivity. Handle poles and the wrap seam deliberately; incorrect pole radius or unfiltered seam neighborhoods can create spikes.
3. Remove isolated distance outliers before smoothing. Keep approved primary volumes and material boundaries as separate constraints.
4. Review all required views before adding detail. A single radius per direction only models a star-shaped surface; undercuts, overlapping lips, and mouth interiors may require another representation.
5. Reject projection that copies the very defect being repaired. Use a clean proxy or deliberately authored surface where the raw source cannot provide trustworthy correspondence.

This is a fitting experiment, not a facial loop generator. It should not be promoted into an automatic reconstruction utility based on one smooth front render.

## 4. Use an authored surface when projection is the wrong objective

A subsequent prototype replaced the radial distances with a controlled ellipsoidal head surface and explicit front-volume adjustments, retaining the approximate working proportions. Separate smooth ears and nose removed damaged source geometry. The base head had 48,898 vertices, 49,152 faces, zero non-manifold edges, and Euler characteristic 2. Its renders were much cleaner, but design fidelity still required review and the first smile was primarily painted rather than recessed.

The important distinction is that this surface is an authored interpretation. It is not recovered ground-truth anatomy and is not automatic retopology of the reference. Keep a visible record of any silhouette/proportion change. Use the source as a guide without treating distance to its defects as the optimization objective.

For a readable mouth, test a real recessed volume separately from the color mask. A closed cutting volume and a controlled Boolean can provide a static prototype cavity, but Boolean output does not provide expression-friendly lip loops. Inspect the rim, interior, tongue, and side view. Plan dedicated facial topology before advertising reusable expressions.

## 5. Separate material sampling from geometric quality

Thresholded per-vertex colors can create stair-step boundaries even on a smooth surface. One project refinement stores an unthresholded signed region field as a point-domain FLOAT attribute, then applies a Color Ramp after shader interpolation. This lets the color boundary cross a face instead of being constrained to already clamped vertex colors.

Keep that distinction explicit when delivering: arbitrary Blender attribute/shader graphs are not automatically portable to glTF. Bake or transfer an export-compatible representation and reimport it before claiming material equivalence. A native blend prototype can retain the editable field shader while the portable material work remains pending.

Do not assume an unused material created in an earlier script survives a save/reopen. A trial failed with a missing material name because the material had no users. Resolve required named resources with get-or-create and set their properties explicitly in the isolated process; use a fake user only when deliberate persistence is needed.

## 6. Integrate only the accepted scope

Before appending a prototype to the working session, reopen the saved candidate and confirm scene, required resources, named objects, and relevant pose behavior. Audit the evaluated region as well as the base mesh after destructive modifiers. Inspect closeups; finite transforms and object bounds cannot establish lip or eyelid quality.

Retain the existing body, rig, and earlier scenes unless their replacement is part of the approved scope. Label the result as a cleaner surface prototype if eyelids, reference likeness, facial loops, portable materials, or body polish are unfinished. Save the experiment decisions and remaining work in the project and update [workstreams](workstreams.md) only to the level actually tested.
