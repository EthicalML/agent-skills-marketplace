# Portable learnings from actual Blender runs

Keep private assets and logs in the project. This log records reusable findings; it is not a substitute for the actual before/after evidence. New research belongs in the relevant workflow until tested.

| ID | Observation and evidence scope | Correction or next action | Regression check |
| --- | --- | --- | --- |
| L01 | A primitive character passed rendering and interaction checks but failed the requested sculpted likeness | Classify primitive assembly as a blockout; use reference comparison and a suitable modeling/reconstruction method | Neutral silhouette and facial-volume comparison before detailing |
| L02 | Independent single-image candidates differed; an angled source invented an extra ear and the selected front source invented rear facial relief | Review every candidate from multiple views; record inferred hidden surfaces | Front, profile, oblique, and rear review; never label unrelated screenshots calibrated multiview |
| L03 | Recalculating normals reduced striped shading while thousands of invalid edges remained | Separate normals repair from topology repair; inspect imported custom normals and sharp flags | Same-lighting render plus connectivity report |
| L04 | More reconstruction resolution increased detail and polygon count without yielding clean deformation topology | Retain high resolution only when it improves a named shape defect; plan a clean base when required | Compare likeness and topology independently |
| L05 | Aggressive decimation opened large tears; blanket remeshing degraded regions in earlier trials | Operate on a copy, compare locally, and reject degradation rather than applying cleanup globally | Same-view before/after and neighboring-region inspection |
| L06 | Broad removal of damaged arms/hands also cut shorts and inner shoes | Constrain deletion to the part; inspect oblique views before accepting it | Adjacent clothing and foot silhouettes remain intact |
| L07 | A glove had zero non-manifold edges but fused fingertips and an accidental handle | Widen gaps, reduce finger radii, and use a finer local remesh; assess components and intended genus | View every finger gap and audit topology; style remains a separate gate |
| L08 | Rest-space vertex colors followed the rig; coarse face coloring amplified rough appearance | Store a named point color attribute for a simple palette; use controlled UV/material boundaries for finer work | Boundary position and stability in rest and bent poses |
| L09 | An eye-squash gesture worked in Blender but object-scale channels were absent from a skinned GLB clip | Use a supported joint or morph animation path; verify the actual closed-eye state after reimport | A nonempty clip or channel count alone is insufficient |
| L10 | Nonuniform arm scale with disabled hand scale inheritance changed the exported glove | In the tested export copy, bake evaluated joint matrices into independent joints; retain the editable hierarchy in the blend | Sampled evaluated world-space geometry matches after reimport |
| L11 | Scene export defaults split coordinated actions; required curves could be omitted | Inspect export grouping, disable scene object splitting when a single clip is required, convert needed curves in the isolated export copy | Clip count, included parts, and synchronized motion |
| L12 | A data-library blend opened to an empty startup scene | Save a normal project with the intended active scene and reopen it separately | Default scene, camera, and visible asset exist on reopen |
| L13 | GUI GPU preferences did not establish worker device choice; first render included large shader compilation cost | Configure devices in the worker and time a second frame | Engine/device/sample report and actual frame timings |
| L14 | Interpolated contact drifted despite correct authored keys | Sample the contact interval; constrain or bake the corrected path | World-space contact error throughout the interval |
| L15 | Complete renders and successful exports did not establish polished character quality | Add explicit likeness, surface, joint, and eyelid gates; document residual damage | [Quality review](quality-review.md) passes for the actual deliverable |
| L16 | Native modifier/operator availability was verified in a factory scene, but no automatic retopology result followed from that probe | Label this API-probed; implement and benchmark modeling methods separately | A real regional benchmark, not discovery of an operator name |

| L17 | Head-only remeshing yielded zero non-manifold edges but severe visible perforations | Reject the candidate; do not equate manifold edges with intended volume | Fixed-view renders plus expected topology, not a single count |
| L18 | Radial reference sampling closed the surface but copied broad lumps and could not represent the mouth well | Use an approved proxy/authored surface; represent undercuts separately | Profile/rear inspection and landmark comparison, not ray-hit coverage |
| L19 | Clamped per-vertex colors made jagged boundaries on an otherwise smooth head | Interpolate a signed region field before shader thresholding; bake/transfer for portable export | Native closeup and separate exported-material check |
| L20 | A saved trial lacked a previously created but unused material | Get-or-create required named resources and initialize them explicitly | Reopen in a fresh process before depending on a resource |

| L21 | A consolidated rebuild inherited portrait render settings from the source, unlike the square trial previews | Set every review camera and render property explicitly; inspect output dimensions | Identical dimensions, framing, pose, and exposure across baseline/candidates |

## Follow the applicable procedure

For L01–L08, read [reconstruction](../references/reconstruction.md), then [polish](../references/asset-polish.md) when a clean rebuild is required. For L09–L14, read [animation](../references/animation.md), [jobs](../references/jobs.md), or [delivery](../references/delivery.md) according to the failing stage. New local surface trials and their limitations belong in [regional surface experiments](regional-surfaces.md).

Do not erase failed approaches when a later version succeeds. Record the conditions under which a method failed; a regional method succeeding does not retroactively prove that a whole-character application was safe.
