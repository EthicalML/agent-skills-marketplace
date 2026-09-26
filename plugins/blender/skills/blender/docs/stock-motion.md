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
