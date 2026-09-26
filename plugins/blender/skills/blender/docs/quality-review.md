# Quality review for reconstructed characters

Run these gates before declaring a reconstructed asset polished. Technical checks and visual review answer different questions.

## 1. Fix the comparison conditions

Save the baseline and use the same camera transforms, orthographic scale or focal length, framing, light setup, exposure, resolution, and pose for every candidate. Record the settings. Capture front, oblique, profile, rear, and local detail views; use neutral clay to separate geometry from material appearance. Review final materials separately. An image with a changed camera is not a controlled before/after comparison.

Confirm what the source views actually show. If screenshots are uncalibrated or inconsistent, record the uncertainty rather than optimizing a false multiview match. Hidden anatomy needs an explicit design choice.

## 2. Inspect primary shape and style

Compare silhouette, head-to-body proportions, muzzle depth, ear shape/thickness, eye placement, mouth corners, glove palm/thumb/finger proportions, shoes, and exposed joins. Clean topology does not establish these qualities. A previously repaired glove was manifold and had separated digits but still needed a style/proportion review.

Reject a smooth but less recognizable candidate. Record whether an improvement is local, view-dependent, or consistent across the whole review set. Do not use attractive lighting to conceal a failed neutral view.

## 3. Audit regional surfaces

Inspect shading normals independently of mesh connectivity. Report boundary edges, non-manifold edges, components, and expected openings by region. A closed glove and an intentionally open clothing shell have different requirements. Euler characteristic 2 supports a closed, connected genus-zero glove but does not prove correct fingers or silhouette.

Look for fused digits, accidental bridges, interior duplicates, missing lips, surface pits, false rear relief, and cuts extending into neighboring clothes or shoes. Inspect oblique and rear views after localized deletion or replacement. A whole-object bounding box cannot detect most of these defects.

## 4. Audit deformation and appearance

For intended actions, render rest, maximum bend, contact, closed-eye, and intermediate frames. Check eyelid contact, eye penetration, mouth thickness, joint volume, feet, and hand/object contact. Squashing an eye mesh is not a finished eyelid. Finite transforms only establish numerical sanity.

Verify that material boundaries remain attached during deformation, and that transfer/baking did not copy reconstruction cracks or cross onto an adjacent part. Compare a neutral material and a final material render where surface noise and painted boundaries are difficult to distinguish.

## 5. Check the delivered representation

Reopen the blend or reimport the actual export in a separate process. Check intended scene, meshes, resources, colors, skin, clip grouping, and relevant motion. Compare evaluated geometry at selected poses. World-space bounds are useful for gross motion but can miss local eyelid or fingertip damage; inspect closeups too.

For video, verify the complete expected frame sequence, encoded stream dimensions/FPS/duration/frame count, and full-file decode. Open sampled frames from the encoded video. Do not describe that as watching the entire video in real time.

## 6. Record the decision

Write one of: reject, keep for a named limited use, or pass for the stated deliverable. List remaining defects and untested behaviors. Keep evidence paths and settings beside the decision. Passing a limited wave does not certify a general-purpose facial or finger rig. Use [workstreams](workstreams.md) to select the next unresolved capability.
