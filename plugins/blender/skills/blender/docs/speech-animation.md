# Build talking from speech and mouth poses

Use this workflow when a jaw oscillator or silent gesture does not meet the speech requirement. Treat audio timing, facial deformation and expressive performance as separate work. Rhubarb CLI timing and a jaw/cheek pose bank have been tested on one short utterance; broader speech quality remains unvalidated.

## 1. Audit and approve mouth poses first

Inspect existing bones, shape keys, rest/supplied expression and mouth interior. Keep eye-opening controls separate from a neutral mouth: REST can change both in an imported rig. Name the missing poses and test them as held front/profile/oblique closeups before scheduling an audio-driven render.

Start with a compact bank covering neutral, closed lips, open/wide/rounded/puckered vowels and useful lip/tongue contacts. Use bones where their deformation is adequate; add scoped shape keys where it is not. Preserve character identity, lip closure and surrounding features. A jaw bone alone does not provide speech articulation; a shape-key bank is also not mandatory if a bone rig can make the approved poses.

## 2. Select a timing backend after the pose bank passes

[Rhubarb](https://github.com/DanielSWolf/rhubarb-lip-sync) offers timed cartoon-mouth cues and JSON output from audio, with optional dialogue text. A small adapter could drive approved 3D poses from those cues; it does not build the poses. Version 1.14.0 ran locally on a Mac and produced cues for one short stylized-character benchmark. The [Rhubarb Lip Sync NG add-on](https://github.com/Premik/blender_rhubarb_lipsync_ng) offers capture, bone/shape-key Action mapping and NLA baking as a Blender UI alternative; its compatibility with the tested Blender 5.2 session has not been verified.

[Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/stable/user_guide/index.html) is an alternative when audio/transcript phone alignment is needed. It still requires a mapping from phones to the character's poses.

[NVIDIA Audio2Face-3D](https://docs.nvidia.com/nim/digital-human/a2f-3d/latest/) is a more involved facial-coefficient route. Its [official SDK](https://github.com/NVIDIA/Audio2Face-3D-SDK) has NVIDIA/CUDA requirements, and the output still needs a suitable target rig. Check deployment and mapping before choosing it; do not imply it is an installed local Mac capability.

## 3. Convert cues into editable facial animation

Keep audio, transcript, cue times and the character-specific control mapping together. Validate cue order, labels and duration before mutation. Convert timestamps to fractional frames with explicit FPS/start offsets. Keep jaw, lip and tongue controls distinguishable.

[JALI research](https://www.dgp.toronto.edu/~karan/jali/) motivates separate jaw/lip motion and contextual blending. As a proposed implementation, preserve brief closures while blending neighboring mouth poses and settling during pauses; do not apply indiscriminate smoothing that removes consonants. This does not claim a JALI implementation.

Bake a separate facial Action. Keep head movement, blinks, expression and hand gestures separately controlled, and remove conflicting placeholder jaw channels from the composed performance. Use [animation libraries](animation-library.md) for Action ownership and NLA composition.

## 4. Validate with sound and record the scope

Review at least one short sentence with closures, distinct vowels and silence; inspect transitions and profile views for penetration or lost identity. Test another phrase before calling the mapping reusable. Log what was authored, inferred, aligned, reviewed and still untested. A convincing silent gesture is not lip-sync, and correct timing cannot fix poor mouth shapes.

The tested character had facial bones but no shape keys. A small jaw oscillator was applied on top of a supplied open smile, so it never reached closure. An absolute closed-jaw pose fixed that while preserving the eye expression. Inspect supplied pose offsets before deciding that new facial geometry is necessary.

One three-second audio benchmark now drives a separate facial Action from 12 Rhubarb cues. Front/oblique pose reviews and reopened-file cue-center checks verified closure, opening, silence, channel ownership and aligned sound placement. Cheek-driven E/F narrowing remains an approximation: true puckering, teeth/lip contact, tongue articulation, another phrase and user playback acceptance remain pending. No automatic facial-rig generation is implied.

For short cues, retain fractional frames and test the cue center. Rounding a closure check to a nearby integer can sample its transition instead. Keep the audio origin and cue-to-frame origin identical, and remove the placeholder jaw curves before evaluating the composed Action. Inspect closure in the final NLA stack; correct standalone facial keys can still blend against an open base pose.
