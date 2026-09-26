# Reusable Actions and layered animation

Use this workflow when creating several named motions or combining them on one rig. Follow [animation](../references/animation.md) for contact, preview and delivery checks. One tested stylized rig supports the workflow; bone names and motion axes remain asset-specific.

## 1. Define ownership and timing

List each clip's duration, loop/one-shot behavior and keyed bones. Use full-body Actions for idle, locomotion and jumps; use restricted channels for overlays such as a wave, nod or speaking gesture. Do not key every bone into an overlay: its neutral leg keys can replace the underlying walk. Gesture-only clips require a full-body base pose/Action.

Distinguish procedural jaw motion from speech synchronization. Label an unaligned clip as silent talking/gesturing. Actual lip-sync needs audio timing and appropriate facial controls; do not imply a jaw oscillator encodes phonemes.

## 2. Bake and retain the Actions

Preserve the source and author on a separate rig copy. Reset pose transforms and update evaluation before constructing each frame. Save one cycle with a matching endpoint rather than baking many identical repeats. Give every Action a stable descriptive name and retain it with a fake user when it might have no current assignment. Key only the bones/channels in the ownership list.

In Blender versions with layered Actions, inspect Action slots and explicitly associate the strip with the intended slot. A saved Action's existence alone does not prove it evaluates on the intended rig. Reopen and inspect its actual F-curves and bone paths.

## 3. Compose the demonstration

Use [scripts/nla.py](../scripts/nla.py) inside Blender: `add_strip(track, action, start, source_start, source_end, repeat=1, blend_in=0, blend_out=0, slot=None)`. The helper creates a REPLACE strip with NOTHING extrapolation, validates ranges/blends, rejects same-track overlap, and requires a slot when the Action has several. It does not infer bone masks or solve pose compatibility.

Put a full-body base below masked gesture tracks. Repeat the loop with NLA repetition. Give one-shots stable entry/exit poses and inspect any blends. Use a separate track for intentional overlap; weight and strip order still determine the result. Clear the active Action before evaluating the composed NLA demo so it does not unexpectedly override strips. Mark the timeline with readable clip names.

## 4. Test the composition after reopening

Check retained Action count, slot association and source ranges. Inspect overlay F-curves for unintended root/leg channels. At a representative layered frame, mute the overlay and compare lower-body matrices: a wave should not disturb the gait. Inspect geometry too; a correct mask can still move the glove through the head.

Sample foot clearance across the demo, including half-frames around takeoff, landing and blend boundaries. Compare evaluated geometry at cycle endpoints. These checks are local regression tests, not exhaustive collision certification or world-space foot locking. Review anticipations, peaks, landings and overlay silhouettes from rendered images.

In the tested library, a raised glove overlapped the ear in the first preview. Widening the shoulder/forearm pose and adjusting wrist roll improved readability. Numerical reach checks alone did not catch that silhouette problem. A talking gesture remained explicitly silent, and a one-cycle walk repeated through NLA rather than duplicated keys.

## 5. Save the tools at their tested scope

Keep bone names, axes, gait parameters and gesture recipes in the project until tested on another rig. The generic strip helper was exercised on a saved six-Action library and with overlap, reversed range, zero repetition and excessive blend rejection. No automatic retargeting or speech-sync capability is implied. Record timings, masks, previews and limitations in the project; refresh this workflow only with demonstrated findings.

For user-rejected talking or audio-synchronized speech, follow [speech animation](speech-animation.md). For a side-to-side wave, derive the rotation axis from the palm plane and distinguish it from wrist flexion. Finger-root/wrist landmarks identified the useful axis on one rig; a covariance estimate over a small weighted vertex subset did not. Verify the arm holds still during the wave phase and inspect both hand-rotation extremes.

Approve the intended palm/back facing separately from the wrist rotation axis. A mathematically correct side-to-side wave can still show the glove back to the audience. Check the held pose and both swing extremes after setting the hand roll.

## 6. Give viewers a clip browser

When a viewer needs to compare prepared clips, provide a small viewport sidebar with named selections and Previous/Next/Play controls. A selection describes the full preview configuration: base and overlay Actions, explicit slots, frame range, frame rate, sound start/mute state and secondary-motion layers. Switching only the active Action fails for gesture overlays and leaves speech audio or mismatched timing behind. Keep this UI project-specific until another rig validates its assumptions.

Own a dedicated preview rig or file. Rebuilding its NLA tracks is appropriate there but destroys custom arrangements on that rig, so preserve the original scene and state that ownership clearly. Clear the active Action, restore an accepted baseline for unkeyed pose channels, then compose the clip. Removing tracks alone leaves previously evaluated channels behind; resetting all bones to identity can also break a rig whose intended resting face differs from identity. Store the baseline as a reproducible project input, not a temporary inspection artifact.

Validate every selection after saving and reopening: range/fps, slot assignment, evaluated motion, sound mute/start, silent facial handles and selecting the same clip again after a different clip. A seven-clip library verified that locomotion → Talk → locomotion restores identical evaluated bone matrices; pose reset and sound timing are part of browsing. A user-installed add-on can persist the panel without relying on embedded Python auto-execution; the currently baked animation remains playable without the panel. Scaling secondary-motion cycles to clip duration closes seams but changes motion speed, which should be documented rather than mistaken for preserved timing.
