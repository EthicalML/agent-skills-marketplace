# Build and repair stylized hands and gloves

Read this workflow when a hand looks wrong, even if its mesh is manifold. It covers a tested open cartoon glove and rigid wave. It does not establish realistic anatomy, arbitrary finger articulation, or a general-purpose hand generator.

## 1. Define the pose and the defect

Inspect the reference hand separately from the character. Record finger count, palm outline, thumb direction, thumb–index web, fingertip lengths, cuff placement, and whether the palm or back faces the viewer. Distinguish a relaxed hand from an open wave: rotating one static glove does not automatically reproduce the other gesture.

Capture rest, intended action, back, palm, side/oblique, and full-character views. Name the defect precisely. In the tested repair, the thumb ran back toward the wrist along the hand's longitudinal axis. Rotating the hand into the wave put the thumb below the palm. The earlier manifold and finger-gap checks had not detected this anatomical/pose error.

## 2. Establish a hand-relative frame

Define a wrist point W, a unit direction D toward the fingers, a perpendicular across-palm direction A toward the thumb side, and a surface-normal direction N. Construct local points as `W + u*A + v*D + w*N`. Record handedness and which side is the palm. Mirror deliberately and recalculate face winding when needed.

Express the palm, finger bases, thumb root, thumb tip, and cuff in this frame. Check the root and tip longitudinal coordinates before posing. A thumb whose tip is near the wrist coordinate while its root is farther toward the fingers may be curling backward; determine whether that is intentional for the reference pose. Do not fix a misplaced thumb by changing only global Z or rotating its visible tip.

Keep these parameters task-specific. A tested cartoon glove's dimensions are not universal anatomical ratios. Compare the constructed silhouette to the intended reference, especially after changing the wrist orientation.

## 3. Build the palm and digits as connected forms

Start with a rounded palm with deliberate width, length, and thickness. Attach the fingers at a coherent base arc, with reference-appropriate lengths and slight spread. Use shorter, rounded fingertips when that matches the style. Avoid three identical parallel rods unless the design actually calls for them.

Attach the thumb to the side of the palm through a broad transition. Shape the thumb–index web and the thumb mound together; inspect both the palm and the back. Keep the thumb distinct from a fourth parallel finger. In the tested iteration, moving its root distally improved the attachment, but an overly long raised thumb then needed shortening and more lateral spread to remain visually distinct.

For a scripted volumetric prototype, use a palm volume, controlled digit centerlines, rounded tips, and a separate thumb curve. Join/remesh only the task-owned parts. Keep intentional gaps several voxels wide; inspect again after smoothing. This creates a static surface, not articulation loops. For fingers that must curl independently, build suitable joint topology and a finger rig before claiming fist or grasp support.

## 4. Construct the wrist and cuff as a real join

The glove sleeve should meet or overlap the cuff's inner edge. Check the bent wrist from both sides. A tapered ellipsoid can narrow too much at the cuff and expose a dark gap; extending it behind the wrist can produce protruding white fragments during a bend.

A tested correction used a short constant-radius sleeve at the cuff, tapering farther inside the palm. Its far cap must be inside the palm volume, not visible as a ledge across the glove. Match the cuff plane to the wrist/finger direction and keep its thickness proportionate. A torus placed near a wrist is not, by itself, proof of a sealed join.

## 5. Place surface details after the shape passes

Keep glove seams on the intended back surface, with their points attached to the surface and bound to the same hand motion. Inspect the opposite side to ensure the lines do not protrude through. Do not use decorative seams to distract from an incorrect thumb or palm.

Check that remeshing, smoothing, or mirroring preserved the material, outward normals, and intended gaps. Re-run these checks after every topology-changing operation.

## 6. Revisit the pose after replacing geometry

Test the new hand in the actual action. In the observed repair, retaining the old wrist rotation hid the improved thumb and one finger behind the head. Adjusting the wave orientation and arm reach exposed the thumb and restored clearance. A hand-only closeup was not enough to identify this problem.

Keep left/right handedness consistent and inspect both gloves. If nonuniform arm scale is used, check hand scale inheritance and export behavior through the [animation workflow](../references/animation.md). Do not silently stretch the glove to gain reach. Preserve the editable rig and document any pose changes made alongside the anatomy correction.

## 7. Separate topology, shape, and motion evidence

For an intended closed, connected glove, audit connected components, non-manifold edges, and expected Euler characteristic. Then inspect every intended digit gap, the thumb web, palm thickness, fingertip proportions, and cuff join. A single connected genus-zero surface can still have a badly placed thumb.

Sample the whole action for head/prop clearance and inspect intermediate frames. A nearest-surface distance or nearest-normal sign test on sampled vertices can flag likely intersections, but it is not exhaustive collision proof. State the sampling density and assumptions, especially when using a rigid-bone transform instead of evaluated skinning.

Keep the review camera large enough to contain all digits. If a candidate no longer fits the original crop, render both baseline and candidate again with the same wider framing; do not judge a clipped finger as missing geometry.

Only test fists, pinches, or grasps if the model actually has the required articulation. Otherwise report the supported scope as an open glove with rigid wrist motion.

## 8. Save the accepted iteration and its learnings

Keep a variant register with geometry settings, root/tip landmarks, pose changes, views, topology report, decision, and remaining defects. Save the accepted scene separately from the source. Reopen it before rendering the full sequence. Inspect encoded video samples after complete frame/stream/decode validation.

Add portable failures to [the learning log](learning-log.md) and update [workstreams](workstreams.md). Keep project-specific assets and code outside the public skill. Promote a helper only after it succeeds on more than its construction assumptions; documentation of a hand-relative frame is not an implemented universal hand tool.
