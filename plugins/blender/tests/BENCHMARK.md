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

## Scope of confidence

This checks a representative iterative modeling/render/export workflow, not every Blender feature or every upstream service. Paid model-generation APIs and credentialed asset libraries require separate acceptance tests with authorized accounts. File-reimport success is not proof of visual equivalence, rig deformation, or simulation-cache portability; those require task-specific evidence.
