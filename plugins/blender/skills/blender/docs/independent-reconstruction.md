# Build independently against a 3D reference

Use this workflow when adapting the source mesh would not meet the goal of constructing reusable assets. A finished adapted asset is useful evidence of the quality target, but does not prove independent construction. Treat a complete character as a sequence of regional shape, topology, material, and deformation gates.

## 1. Define what is being rebuilt

Record whether the output reuses source geometry, retopologizes the source surface, or builds new geometry from authored landmarks and parameters. Do not describe all three as from scratch. For a regional prototype, explicitly state which surrounding meshes remain from the earlier model. Reusing a generic surface-building function is compatible with independently generated geometry; reusing the reference mesh is adaptation.

Choose a bounded high-value region and name its missing structure. A muzzle with an incorrect mouth cut-out needs upper/lower lip, mouth corners, and cheek volume; moving its existing vertices forward may only exaggerate the wrong construction. Preserve the earlier candidate as a regression case.

## 2. Establish comparable reference state

Use [asset spikes](asset-spikes.md) to prepare a pose-aware inspection derivative. Align expression as well as body pose. Closed-mouth and open-mouth versions of the same character are not corresponding shape targets.

Inside Blender, use [reference_snapshot.py](../scripts/reference_snapshot.py) as `snapshot(model_meshes, rigs)` for read-only tight evaluated bounds and bone endpoints. Supply the model objects explicitly; exclude the floor and unrelated props. The result records frame, pose/rest mode, uniform height scale and grounded origin. Orient the model separately: normalization does not rotate it, align expressions, or infer anatomy. Bone endpoints are rig anchors, not surface landmarks.

The helper was tested on one rigged asset, a translated/scaled instance, a rotated sparse-mesh fixture, and invalid selections. This validates measurement mechanics, not universal landmark correspondence. Keep measurements and the assumed coordinate frame beside each preset.

## 3. Separate construction code from character design

Keep generic surface operations in a Python module and character-specific dimensions, semantic points, profiles and attachment rules in data. Name the controls by what they shape: nose contact, upper lip, mouth corner, lower lip, cheek peak, boundary. Prefer a small explicit surface/cage to a generator with dozens of opaque world-coordinate constants.

Inspect base and evaluated mesh counts separately. In one reference, a 250-vertex base head had better facial organization than a roughly 65,000-vertex remeshed candidate. This is a reason to test a small editable control mesh, not a universal vertex-count target.

Construct a region whose topology represents its openings and boundaries. Lofts and curve sweeps are possible building blocks, but intersecting closed pieces do not automatically form a continuous facial surface. If a prototype looks like assembled parts, solve the region boundary and mouth integration before adding more detail or samples. Smooth shading does not remove an assembly seam.

Keep visibility ownership explicit: identify which old surfaces are replaced and which remain. Review both the new region and its attachment to the surrounding face. A local object may be manifold while the assembled face intersects or shows duplicate borders.

## 4. Validate code reuse separately from visual quality

Build two meaningfully different parameter presets with the same generator and inspect both. Check finite coordinates, expected topology, parameter rejection, and that the code does not read the target mesh when claiming independently constructed geometry. This demonstrates parameter reuse only.

Then assess likeness with fixed front, profile and oblique cameras, including clay and material views when boundaries may conceal shape. Require improvement in all relevant views without damaged surrounding features. Preserve rejected candidates and the precise defect. Reopen the saved file before trusting object transforms or attribute preservation.

A second preset is not a second-character benchmark. Before claiming broader automation, run a genuinely different reference through landmark definition, construction, review and correction. Record where human/agent decisions were needed. Character families with different anatomy may require different topology templates and controls.

## 5. Expand only after regional acceptance

Promote useful geometry primitives and measurement tools at their tested scope. Keep asset-specific fitting constants in the project. If two local attempts fail, change the representation or boundary strategy instead of merely increasing resolution. Once shape and integration pass, validate UV/material behavior, articulation and facial expressions. A static region does not establish a reusable animation rig or a complete from-scratch asset.

## Observed continuous-patch limit

A subsequent annular mouth-to-cheek patch replaced intersecting volumes with shared topology and a closed rear/cavity surface. The static head had 1,346 control vertices, 672 frontal quads, one connected component and zero non-manifold edges; exact-boundary and invalid-input checks passed for the ring-bridge helper. Front/profile/oblique review still rejected wedge-like muzzle depth, jaw projection and corner pinching. This establishes a construction primitive, not solved likeness.

For the next attempt, measure corresponding target surface landmarks and curves instead of continuing to guess coordinates. Fitting newly authored topology to those measurements is reference-fitted reconstruction; it does not require copying the target polygon layout. Keep that claim distinct from making an asset without a 3D reference. An image-only task needs its own reconstruction and hidden-surface assumptions.
