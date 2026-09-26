# Blender workflow checks

Run the ordinary socket/job tests with `python3 -m unittest discover -s plugins/blender/tests -p 'test_*.py'`; the marketplace validator includes them. They do not need Blender or credentials. They cover chunked Unicode responses, reported errors, ambiguous timeout/connection outcomes without write retries, script entrypoints/parameters, successful/failed jobs, and graceful/forced cancellation.

Run `blender --background --threads 2 --python-exit-code 1 --python plugins/blender/tests/runtime_checks.py` for Blender-specific regression checks. This starts a separate process and creates files only under repository tmp. It verifies pagination, selected-object GLB export from Edit Mode, active/selection/mode restoration, exclusion of unrelated scenes from exported GLB JSON, material inspection, and reopening a copied blend with relative textures. It requires Blender and is intentionally outside hosted CI.

## Independent skill exercise: product lamp

Tested with GPT-6 Luna against Blender 5.2.2 LTS on macOS. The agent received the skill path and a brief for a teal articulated desk lamp, two rendered views, a saved blend, and a lamp-only GLB. It had to preserve the user's existing scene and could not edit the skill or publish reports externally.

The run used 45 tool calls and five image inspections over approximately ten minutes. The transcript shows an actual visual revision: the first hero image concealed the illuminated opening; the agent changed the shade orientation and inspected the revised render. Mesh validation found 96 boundary edges and the agent closed the unintended opening before delivery.

The benchmark also exposed a helper defect: selected-object glTF export included unrelated scene nodes because Blender defaults use_active_scene to false. The helper now explicitly enables it, and a regression test inspects the GLB JSON for isolation. After the fix, the exported file contained exactly the 21 lamp mesh nodes; isolated reimport matched that count. The saved blend reopened with 27 scene objects, both final 1400×1400 renders were inspected, and the original three-object scene remained intact.

Two instruction improvements came from failed agent attempts: keep external client code separate from code importing bpy, and create a world explicitly for a new scene. The transcript also showed simultaneous final renders slowing the workstation; background jobs now default to four threads and the skill recommends sequential heavy jobs.

Local benchmark artifacts, tool transcripts (without image payloads), token counters, and run reports stay under ignored tmp/bench. Token counters include repeated cached context and are not a measure of unique context or model cost. No private scene data or machine-specific paths are included in this repository report.

## Independent skill exercise: asset and animation

A fresh GPT-6 Luna agent used the finished skill for a ceramic mug on a pedestal. It searched Poly Haven, inspected two HDRI previews, imported the free 1k studio_wizja_03 HDRI, and packed it into the saved project. It animated a full turn over frames 1–24 and rendered three final 512px frames sequentially. The transcript contains 38 tool calls over approximately nine minutes; the parent also inspected all three final images.

Visual inspection caught an incorrect parent offset that left the first mug floating. The agent fixed the pivot and height and rerendered all three frames. Two build-script errors and a save-path typo were also corrected; this run found no additional client defect. These were actual failed attempts, not a clean first-pass result.

Separate Blender processes reopened the packed blend, confirmed the HDRI and 0/180/360-degree keyframes, and reimported a four-object mug-only GLB with animation channels. A further import check sampled the handle's world position at frames 1, 6, 12, and 24: it moved around the pivot, reached the opposite side, and returned within 0.001 units. Both existing scenes retained their exact object-name lists compared with the prebuild checkpoint. This comparison establishes scene membership preservation, not a byte-for-byte audit of every property.

## Real Blender cancellation

A saved-file job running a deliberate wait in a separate Blender process was cancelled through cancel_job. Its terminal state was cancelled and its exit code was -15; the interactive listener remained available. The subprocess unit suite separately verifies forced termination of an unresponsive child.

## Advanced exercise: character interaction and video

An 18-second workshop short exercises 228 objects, hierarchical character animation, four camera segments, a grasping hand, a robot-controlled lever, a rolling ball, a spring paddle, a bell, and confetti. It uses a packed CC0 Poly Haven HDRI, generated narration, original synthesized music/effects, and reusable character/prop libraries. The source scene and previous benchmark scenes remain separate from the delivery project.

The first previews exposed a reversed shoulder rotation and a robot hand that did not reach the lever. Corrected poses follow their targets in world space. A numerical check then exposed a small ball-to-ramp gap and interpolation drift between corrected keys; baking the contact interval removed it. The full 432-frame verification checks finite transforms and camera cuts. Maximum measured errors are below 0.000001 scene units for the mouse grasp, robot lever contact, the ball's checked ramp interval, and the ball-to-clapper impact.

A packaging check caught the distinction between a Blender data library and an ordinary project: the library opened to an empty startup scene. A separate process selected the intended scene and saved a normal project, and another reopen verified the default scene, packed lighting, and soundtrack. GPU profiling also showed why a second sample matters: first-use Metal shader compilation took about 102 seconds, while subsequent 720p/24-sample frames took approximately three seconds. The first glTF exports also split each object action into separate clips; scene-mode export with object splitting disabled preserves coordinated motion in a single clip per asset. Required curves are converted in the isolated export process. These findings are captured in the conditional animation workflow reference.

The final 720p/24 fps video contains all 432 frames, AAC audio, and captions. Full-file decoding and stream metadata checks passed; sampled frames from the encoded MP4 were inspected. The successful render took 1,128 seconds, averaging 2.61 seconds per frame. The three GLB assets reimported as 45, 26, and 28 objects respectively, with one coordinated animation clip each. A separate reconstruction from the included scene scripts also passed the contact and camera checks.

## Reference reconstruction and visual quality

The character short above passed technical checks, but its primitive character construction did not meet the requested sculpted reference quality. Treat it as a workflow/blockout benchmark, not proof of production character modeling. That distinction is now explicit in the skill.

A subsequent local experiment used two supplied reference images independently with TRELLIS.2 through the MLX runtime documented in references/local-image-to-3d.md. It generated two 512 candidates and a 1024 cascade refinement on an M1 Max with 32 GB. Neutral front, three-quarter, side, back, and face views were inspected. The angled input invented an additional ear and damaged facial geometry and was rejected. The front input captured substantially better reference proportions and facial volume than the primitive assembly, but invented facial structure on the unseen rear head.

The raw 512 mesh had 683,105 vertices and 1,374,528 triangles. Recalculating face winding reduced inconsistent manifold edges from 373,959 to 3,284 and removed most striped shading; 20,297 non-manifold edges remained. A voxel-remesh cleanup worsened the head and one shoe and was rejected. Imported custom normals and sharp-edge flags also required attention during neutral review.

The 1024 candidate took approximately 16 minutes versus four minutes for one 512 candidate. It improved mouth and shoe forms but retained invented rear geometry and surface defects. Its 5,523,350 triangles did not imply cleaner topology: after normals repair, 141,760 non-manifold edges remained. The selected result is a static reconstruction study, explicitly not approved for production animation. Its GLB reimport preserved mesh counts and approximately four-unit height; a five-second, 60-frame turntable exposes all sides. No deformation rig or facial controls were created.

These observed failures motivated the reference comparison, candidate rejection, repair comparison, and animation-readiness gates. Private inputs and generated character assets remain outside version control. Broader reusable mesh-audit and deformation tests are tracked in issue #18.

## Local hand replacement, color, and limited animation

A follow-up retained the dense reconstruction and replaced both damaged gloves with joined, remeshed palm/finger/thumb volumes, separate cuffs, and seams. Each glove has 74,842 vertices, one connected component, zero non-manifold edges, and Euler characteristic 2. Earlier versions passed the edge check but had fused fingertips; closeup inspection and the topology check together caught that failure. Broad trimming and decimation damaged adjacent clothing and shoes and were rejected.

Rest-space vertex colors and separate colored parts support a nine-bone wave, two blinks, and bow over 192 frames at 24 fps. All frame transforms are finite. This is a limited performance, with visible inherited face/body surface defects; it does not establish full-body retopology or arbitrary deformation readiness.

A GLB with one skin and one clip initially omitted object-scale eye blinks. Eye-bone animation retained those channels. A subsequent reimport exposed hand deformation from nonuniform parent scaling with disabled scale inheritance. Baking evaluated joint matrices into independent joints in the isolated export copy fixed it. Rest, closed-eye, maximum-wave, bow, and final-frame comparisons of evaluated world-space mesh bounds agree within 0.000001 scene units. The editable blend retains its original joint hierarchy. Private source images and generated assets remain outside this repository.

## Reconstruction polish research and availability probe

A follow-up review identified remaining surface, likeness, joint, and eyelid gaps despite successful hand topology and export checks. The conditional asset-polish reference now captures regional rebuilding, controlled cage fitting, loop/patch design, detail and material transfer, deformation, visual regression, and portable delivery as separate workstreams. Artist-authored Blender Studio and CG Cookie articles, Blender manuals, and RetopoFlow documentation inform the methods; proposed programmatic translations are labeled as proposals.

An isolated Blender 5.2.2 factory-scene probe constructed Mirror, Subdivision, Shrinkwrap, Smooth, Laplacian Smooth, Corrective Smooth, Multires, Data Transfer, Lattice, Mesh Deform, Surface Deform, and Geometry Nodes modifiers. It found the QuadriFlow, voxel remesh, bake, Multires Reshape, and UV unwrap operator schemas, constructed shape keys, and imported BVH/KD-tree types. This establishes API availability only. It does not validate automatic retopology, selective projection, facial rig quality, a third-party add-on, or autonomous production polish. Those require the regional asset benchmarks described in the workflow.

## Regional head surface benchmark and documentation routing

A bounded head experiment compared matching front, oblique, profile, and rear views. Head-only voxel remeshing produced zero non-manifold edges but severe visible perforations and was rejected. A filtered radial shell used 24,384 samples with about 83.4% accepted hits; it closed the surface but retained broad lumps and weakened facial/profile features, so it was rejected as the final candidate too.

An authored controlled surface with separate smooth ears/nose produced cleaner views. A further refinement introduced a recessed smile, corrected an inherited jaw/neck fragment, and interpolated a signed material-region field before shader thresholding to remove stepped color boundaries. The resulting head has 50,014 vertices, zero non-manifold edges, and Euler characteristic 2. It remains a surface prototype: reference likeness, facial loops, proper eyelids, body polish, and portable shader baking are not established. A consolidated project builder recreates the prototype from the preserved source without depending on rejected trials.

The skill now routes complex tasks through docs/index.md, with a learning log, regional experiment procedure, quality gates, and workstream statuses. Existing reference paths remain valid. Project-specific assets, scripts, and private evidence remain outside the public repository.

## Thumb, cuff, and action-pose iteration

A later review exposed a missed criterion: the earlier closed glove's thumb pointed back toward the wrist along the longitudinal hand axis. Rotating it into the wave put the thumb below the palm. Four variants rebuilt the palm/digits in a wrist-relative frame, raised the side-mounted thumb root, shortened and spread the thumb, sealed the cuff, and corrected a sleeve-cap ridge. The new geometry also required a revised wrist angle and reach to keep the thumb visible beside the head. Matching back/palm/oblique and whole-character views were inspected.

The selected right/left gloves have 39,546 and 39,544 vertices respectively, each with one component, zero non-manifold edges, and Euler characteristic 2. Finite rig transforms passed across 192 frames. A nearest-surface/normal diagnostic sampled 501 vertices per glove per frame against the closed head, flagged no suspected penetration, and measured a minimum sampled separation of approximately 0.0427 scene units. This is not exhaustive collision proof. The benchmark remains a rigid open glove and wrist action, not an articulated fist/grasp rig. The new docs/hands.md procedure separates anatomy/style, topology, cuff joins, and action-pose checks.

## Scope of confidence

This checks a representative iterative modeling/render/export workflow, not every Blender feature or every upstream service. Paid model-generation APIs and credentialed asset libraries require separate acceptance tests with authorized accounts. File-reimport success is not proof of visual equivalence, rig deformation, or simulation-cache portability; those require task-specific evidence.
