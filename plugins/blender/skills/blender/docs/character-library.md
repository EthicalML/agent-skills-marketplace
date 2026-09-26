# Character libraries from supplied assets

## Inspect before importing

List archive members, reject absolute/traversing paths and symlinks, bound expanded size and compression ratios, verify CRCs, and record hashes. An allowlist of model/texture extensions catches obvious executable payloads but is not a malware guarantee. Inspect native files in a disposable Blender process with automatic script execution disabled. Inventory text blocks, driver expressions on objects and shape-key datablocks, constraints, packed images and missing resources. Read credit text and retain the original archive separately from derived previews.

## Pilot each rig family

Validate one representative of each artist/rig layout before parallelizing the rest. A weighted skeleton saves rigging work but does not establish motion compatibility. Separate model appearance, rig hierarchy, motion transfer, speech and browser integration into checks with visible evidence. Keep imported game props separate from anatomy: an extra boxing glove may be removable, while a similarly named palm-cupping bone can deform the actual hand.

Measure scale from the intended character after excluding props and control shapes. Inspect original mesh parenting, armature transforms and bind pose before applying transforms. A tested FBX had a skinned mesh with a bone child: the Blender importer reused its helper as an armature and attempted to add an Armature modifier to an armature. A narrowly scoped import repair also had to restore object parenting before preserving bind transforms. Do not generalize this repair to unrelated files or patch an installed importer globally.

Normalize heading and map anatomy explicitly. Transfer rotations with source-rest compensation, account for target bone axes, and preserve unmapped facial/accessory behavior deliberately. Some game ankle controls are root siblings rather than children of the knee. A direct FK bake can animate the torso while the feet stay fixed. Convert the derived rig to a coherent deformation hierarchy while retaining rest matrices; verify that a jump actually lifts the evaluated feet. Scale translation by corresponding anatomical heights, not an arbitrary root bone which may lie on the floor.

## Appearance and facial defaults

Recover supplied texture paths relative to the archive, pack resources, and record missing originals. A bounded material replacement is a replacement, not recovered artist artwork. Do not add subdivision indiscriminately to game meshes; it can change the silhouette and damage texture seams.

Inspect facial defaults visually. One native eyelid setup uses one for open and zero for closed. Missing pupil textures, eyelid coverage and a dependency cycle can look like a single missing-eye problem but need different repairs. Clear conflicting drivers only on channels the adapter takes ownership of. Reparent accessories or bake their constraints before removing the source control system; indiscriminately deleting constraints can leave a hat detached from the head.

Keep animated floating-point custom properties floating-point in every assignment, including zero: use `0.0`. A tested mouth Action stored fractional keys correctly, but a later assignment of integer zero changed the property type and the saved animation evaluated as closed. Reopen, sample the evaluated property and inspect the actual mouth at peak speech and silence. F-curve presence alone does not verify speech.

Calibrate neutral jaw and maximum speech separately for each character. A source smile or the target's open bind mouth may create a permanent gape. Native shape keys, a game jaw bone and a quadruped muzzle need separate adapters. Reusing audio/timing does not supply missing viseme geometry.

## Browser and validation

Use one prepared scene per character and explicit metadata mapping clip IDs to Actions, FPS and frame bounds. Append the reusable Actions explicitly, including inactive clips that are not scene dependencies; restore fake users and Action slots. A character selector can switch scenes while preserving the selected clip. Stop playback during scene changes, select the destination camera, and enable speech audio only for the talking clip. Verify every character/clip combination after saving and reopening.

Character-specific contact repair remains necessary. Review evaluated soles, gloves, face, clothing and accessories across both support phases, maximum gestures and loop boundaries. Attribute the lowest evaluated vertices to their object or skinning group: a low tail can masquerade as a sole-contact defect. Shorter tail chains may need their own modest traveling waves instead of proportional resampling of a long tail. Keep pelvis performance separate from local ankle correction. Analytic limb solvers should use actual child-joint positions; imported bone display tails and lengths may not point toward the next anatomical joint. Floor-clear keyframes do not certify subframe clearance, collision-free hands, foot locking or pleasing acting. Render and inspect the changes.

A quadruped requires its own gait and gesture semantics. A paw greeting can share a browser key with a human wave; its implementation must match the anatomy. Label a fast trot as a fast trot rather than claiming a gallop. Keep asset-specific recipes, source attribution, review images and limitations in the project; promote only demonstrated portable findings into this skill.

## Review-driven corrections

A neutral full-body render missed raised eyelid strips which were obvious in the user's closeup. Inspect modifier dependencies before removing apparently non-character objects: a helper without skinning can still be the target of a visible eyelid's Shrinkwrap modifier. Deleting the target left the modifier disconnected; exposing other construction surfaces compounded the defect. Restore the dependency in the normalized rig coordinates and keep construction surfaces out of beauty renders. Review front and profile, retaining intended eyelashes rather than simply hiding the whole eye region.

A lowest-vertex floor check does not detect hands entering a costume. Use evaluated glove vertices and torso/clothing surfaces, with explicit exclusion of the intended cuff/sleeve join. A nearest surface normal at a shorts hem or crotch can point down and toward the opposite side; forcing that normal into the horizontal plane can push the glove farther into the body. Apply anatomically constrained local arm corrections and inspect the worst offending pose. Preserve the arm's segment lengths, wrist presentation and matching loop endpoint; do not move the pelvis to fix a hand.

For vivid cartoon palettes, separate material colour from view transform, exposure and lights. A tested saturation/Standard-display pass clipped white detail until illumination was balanced. Region-specific hue and material adjustments were needed to match a green cap and brown vest without recolouring skin or gloves. Keep texture originals intact, inspect neutral and highlighted regions, and standardize the display/lighting treatment before assembling several characters into one shot. A per-scene palette preview is not automatic multi-character look matching.

Maintain an explicit selection manifest after user review. Removing a rejected character from the UI while leaving assembly driven by a directory glob can silently reintroduce it on the next rebuild. Keep prior checkpoints for reproduction and exclude retired variants from the current assembled scene and normal selector.

When a pose correction moves costume vertices as well as the arm, rebuild the collision BVH after each correction. A surface cached before the solve can falsely report clearance against the old garment shape. Audit the saved file independently and rerun only flagged clips; preserve unaffected animation channels with before/after hashes.
