# Stock motion and retargeting

A retargeting plugin is not a motion library. Acquire a motion clip separately, retaining its official source, stated usage permission, skeleton preset and frame rate. Follow any user download restrictions. A publicly linked Rokoko walk/run pack supplied FBX files on a Mixamo skeleton at 30 fps; no Studio application or cloud login was needed for this offline test.

## Inspect before mapping

Import the animated source and a second copy with animation disabled to inspect the actual rest transform. An FBX root can become the armature object instead of a hip bone. Deleting object animation as cleanup then discards hip movement. In one tested file, a new hip bone was added above the existing root children, object transforms were sampled, and the motion was converted relative to the nonanimated object transform. Preserve an unmodified import for comparison. Hide or remove imported reference meshes explicitly: hiding only an armature does not hide its children from rendering.

Map body bones explicitly, with rest orientation and scale compensation. Keep character-specific face, ears and tail separate. A human five-finger map should not silently replace a four-digit glove setup. Inspect reference-pose lead-in frames before declaring a walk loop.

## Blender 5 compatibility findings

Official Rokoko Studio Live 1.4.3 registered on Blender 5.2.2 but failed at bone detection because Action.fcurves no longer exists. A scoped test read F-curves from the assigned Action slot's channel bag. Assign the slot explicitly when assigning an Action; a copied Action reference alone may not evaluate.

Further failures appeared in legacy curve creation/merge and Bone.select. For one short clip, the project used slot-aware curve reads, PoseBone.select, and a single native nla.bake instead of the plugin's segmented legacy merge. The resulting body Action baked successfully on one stylized character. This is a local experiment, not a claim that the unmodified plugin supports Blender 5 or that long clips, login, streaming and all rig types have been tested. Keep these adaptations in an isolated process until broader validation warrants a maintained adapter.

## Acceptance gates

Reopen the output and verify the assigned Action slot, real bone movement, no leftover retarget constraints, and intended channel ownership. Render several phases, including both support legs and the loop boundary. Test evaluated shoe geometry against the floor; ankle height is not sole height. Per-frame root height correction can eliminate floor penetration but does not provide horizontal foot locking or solve all contact problems. Inspect subframes too. Match loop endpoints and review the transition: endpoint equality alone does not establish smooth velocity.

Use motion capture as a starting performance. Short limbs, oversized shoes and large gloves need contact and silhouette adjustments. Keep the untouched source motion and prior accepted character checkpoint, and label each delivered adaptation honestly.

## Expanding a downloaded pack

Do not assume one pack has one skeleton preset: a 15-clip batch contained both object-root Mixamo and bone-root unprefixed layouts. Test each layout before scaling out. Isolated workers with Action-only output libraries keep iteration small. Store per-clip ranges/FPS, preserve fake users and label full takes separately from seamless loops. Travel removal, forced upright posture and per-frame grounding alter the captured performance; document lost lean and running flight explicitly. A global floor offset can float a character when an outlier sets clearance. Test evaluated soles at fractional frames and render every clip: a successful bake can still be sideways or off-camera.

## Contact cleanup after user review

A broad batch passed sampled floor/midpoint checks yet failed playback review: a large shoe's toe roll drove the entire body upward through per-frame minimum-sole root correction, while human hand paths intersected an oversized head. Keep failed clips out of a normal preview browser and retain their source Actions for work; a larger dropdown is not a quality improvement.

Separate pelvis performance from foot placement. Detect or author support/swing phases, fit each ankle to evaluated sole geometry, and solve the limb with IK. A tested short-legged character used mocap upper-body rhythm with authored stance/swing paths and baked two-bone IK, bounded pelvis motion, modest heel/toe roll and running flight. This is a hybrid adaptation, not unchanged motion capture or general-purpose contact detection. In-place stance feet must move relative to the body; world-space locking requires matching root travel. Keep character-specific phase durations, stride lengths, wrist clearance targets and bone axes in the project until validated on another asset.

Partition left/right shoe geometry using skinning membership or known components, not vertex X sign: large shoes can cross the symmetry plane. Adjust each limb rather than raising the whole character from the lowest rotating point. Preserve scale and bone lengths, account for unreachable targets, and validate both support legs at half frames. The tested pair passed floor clearance, loop mesh equality and sampled glove/head signed-distance checks; those checks do not certify other collisions or endpoint velocity continuity. Visual review from front and side remains necessary.

Hand clearance needs actual retargeted mesh review. Wrist targets alone do not protect a large glove whose fingers point into the face. A tested correction adapted arm reach and damped wrist orientation toward a relaxed pose before baking; this was not a physics collision constraint. Do not claim a generic Limit Rotation switch solves mesh intersection.

Reapply fake users after appending Action-only libraries. In one saved-file test, an unused appended Action disappeared even though its source Action had a fake user. Reopening the complete browser and switching every entry caught the loss. Validate imports after save/reopen, not only immediately after append.
