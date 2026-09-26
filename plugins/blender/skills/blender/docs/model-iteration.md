# Fast model iteration

Use this workflow while geometry is still changing or the user wants model review. Rendering a full sequence after each small edit wastes time and delays the useful feedback.

## Keep the loop local

1. Preserve a checkpoint and record the visible defect. Select a static pose and fixed front/oblique review cameras. Keep rig overlays out of beauty or shape comparisons.
2. Edit the affected mesh or modifier parameters only. Preserve source geometry and earlier candidates. Inspect the live scene again before applying a background candidate so user edits are not overwritten.
3. Use a viewport or clay closeup first. Render a small still only when material, relief, or surface intersections need it. Re-render only views affected by the change. In a tested case, three 600px, eight-sample stills plus edits/save took about 37 seconds inside Blender; a two-view refinement took about 26 seconds. These are observations on one asset/device, not guaranteed budgets.
4. Open each image and state whether the specific defect improved. Check a second angle so flattening or smoothing does not conceal a new problem.
5. Save the selected model, check changed topology and resource dependencies, and expose it in the live review workspace while preserving prior scenes. Full motion validation and video encoding are separate later work after model acceptance.

Cancel task-owned obsolete renders when the user changes scope. Keep completed evidence, but do not spend more time encoding a video the user has deferred. Distinguish elapsed build/render time from startup, research, and agent inspection time.

## Diagnose surface defects correctly

Smooth shading changes interpolated normals; it cannot remove ridges in the actual silhouette or joined volumes. For volumetric gloves, inspect the thumb/palm/wrist transition, then compare additional mesh smoothing and limited subdivision. Excessive smoothing shrinks fingers, weakens the thumb web, and changes cuff fit. Review those landmarks again. Subdivision is not production retopology.

Reseat attached detail strokes after changing the surface. Move whole cross-section rings or use a suitable surface attachment; projecting every vertex onto one surface can collapse a tube's thickness. Keep the decorative detail separate from the glove's watertightness claim.

## Reduce protruding cartoon eyes deliberately

First distinguish thick separate eyeballs from the intended shallow cartoon eye treatment. In one static prototype, projecting eye whites, pupils, and catchlights onto the face with small layered relief removed the detached dome appearance. Check the front, oblique profile, layer intersections, silhouette, and material response. Keep offset magnitudes proportional to the model, not copied as universal dimensions.

This bounded method does not create anatomical eye sockets or eyelids. An old eye-squash action may be incompatible with the new surface. Preserve the source, remove or disable incompatible animation only in the candidate, and report that animation is deferred. A static visual pass does not prove blinking or eye motion works.

## Use external models as evidence

Record author, model URL, license, and whether you examined a thumbnail, interactive viewer, or downloaded mesh. Public previews support silhouette observations; they do not establish topology, rig quality, or file contents. Prefer sources with clear asset licenses, preserve attribution, and follow [asset access](../references/assets.md) for actual imports. Never describe a located download as a successfully inspected source model.

## Repair the whole visible region

1. For torn shoulders, rear fragments, or cracked shoes, inventory object bounds and surface ownership before editing. A legacy mesh can contain several body regions beneath newer replacement parts. Inspect rear and side views; a front-only pass can miss folded shells and duplicate appendages.
2. If damage is widespread, replace the affected region with clean geometry instead of transferring its cracks onto a new surface. For a continuous stylized shoulder, connect the torso and arm surfaces and inspect the axilla; separate overlapping joint spheres retain visible seams even when each part is smooth. Keep garment/cuff boundaries deliberate.
3. Confirm replacement ownership using exact object identities and scene membership. A prefix ending in a dot can match numbered duplicates while missing the original unsuffixed object. Check counts of intended appendages and inspect the rear after replacement.
4. Review the new silhouette as well as smoothness. Joined shorts volumes can create bulbous hems; rounded shoe volumes need intentional toe, heel, ankle, and sole shapes. A crack-free sphere is not automatically a convincing shoe. Preserve the earlier candidate and change only the defective construction parameters.
5. Save before preview rendering. If a small still stalls, inspect evaluation before lowering samples. In an observed case, large polygon caps on cut shorts made subdivision stencil construction very slow; omitting unnecessary subdivision on the dense shorts restored the review loop. For reusable low-resolution geometry, design suitable cap topology instead.
6. Reopen the result and inspect evaluated topology against each region's intended boundaries. Keep static validation separate from weight/deformation validation: newly connected shoulders with provisional weights have not passed the old animation merely because the neutral pose looks better.
