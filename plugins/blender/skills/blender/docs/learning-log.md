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

| L22 | A closed glove's thumb pointed toward the wrist in hand-relative coordinates, so the wave put it below the palm | Construct root, web, mound, and tip in a wrist/palm frame | Compare longitudinal thumb direction, back/palm views, and the actual wave |
| L23 | Improved hand geometry was hidden behind the head by the old wrist orientation | Revisit pose angle and reach after geometry changes | Full-character and intermediate-frame clearance checks |
| L24 | Rounded wrist ends exposed a cuff gap; a sleeve cap created a ridge in the palm | Match sleeve radius to cuff and place the far cap inside the palm volume | Bent-wrist closeups from both sides |
| L25 | Raising the thumb too far made it resemble another long finger | Shorten it and adjust lateral spread while preserving the web | Reference-style silhouette and thumb/index distinction, not tip height alone |

| L26 | Full animation rendering delayed feedback on local model defects | Use static, targeted closeups and defer sequence rendering until modeling is accepted | Record affected views and per-pass timing |
| L27 | Smooth shading left ridges where glove volumes joined | Change surface geometry and review smoothing/subdivision with shape landmarks | Thumb web, finger size, cuff fit, front and oblique views |
| L28 | Separate thick eye ellipsoids looked detached from the face | Test shallow face-following layers for a static cartoon treatment | Oblique relief/intersection checks; do not claim eyelid or blink support |

| L29 | Front-focused review missed torn rear shells and overlapping shoulder pieces | Inventory regional ownership; replace damaged legacy surfaces and review rear/side | No residual flaps; intended continuous shoulder and appendage counts |
| L30 | A replacement left the original unsuffixed tail because its name filter only matched dotted duplicates | Match exact owned objects and verify scene membership | Count intended appendages and inspect the rear |
| L31 | Subdivision of dense cut-surface caps stalled a small preview | Profile geometry evaluation; omit unnecessary subdivision or rebuild cap topology | Save first and compare build/evaluation timing |

| L32 | A downloadable model listing still required authenticated acquisition | Separate preview discovery, download, import, and mesh inspection states | Actual local source file and attribution before claiming geometry comparison |
| L33 | Appended parts scattered when reparented using stale world transforms | Update dependency graph after linking and before matrix capture | Inspect full imported model and reopen the saved comparison |
| L34 | Cleaner surfaces changed shoe proportions relative to an older checkpoint | Review fixed orthographic profiles and named landmarks independently of smoothness | Recorded transforms, pose caveats, and visual comparison |
| L35 | Git-ignored binary models would leave progress without an editable remote backup | Publish versioned checkpoints with hashes and restore instructions | Verify uploaded asset sizes/digests and preserve rebuild inputs |

| L36 | An asset download contained a nested archive; unrelated source image paths obscured real dependencies | Inspect archive levels and pack material-used textures | Source hash, safe extraction, material appearance review |
| L37 | Rest mode occluded pupils although the supplied pose rendered correctly | Preserve supplied pose and label rest-derived measurements | Compare original appearance before interpreting rest geometry |
| L38 | Rotated local-box corners overstated ear dimensions and caused an undersized fit | Measure evaluated world-space vertices for quantitative fitting | Compare tight extents and rendered silhouette |
| L39 | Matching head/ear extents still left an incorrect muzzle and shoe silhouette | Treat dimensions, anatomy, appearance, and rigging as separate gates | Keep incomplete static trials separate from accepted assets |

| L40 | Rest-mode eyelids covered pupils in a supplied rig; moving pupil geometry would have treated the wrong cause | Inspect occluding parts; preserve facial pose while resetting only the intended body transforms | Face render and eye-region ray hits before and after reset |
| L41 | A neutral-looking model did not establish complete rig readiness | Preserve mesh/UV/weight fingerprints; restore snapshots between bounded bone tests | Fresh-file reopen plus explicitly limited static pose evidence |
| L42 | A compact-support muzzle edit preserved pins and topology but made the profile pointed | Reject it for likeness; use explicit lip, cheek, and mouth-corner structure next | Identical baseline/candidate profile cameras plus fresh coordinate comparison |

| L43 | Blender exited zero after a script traceback | Require a completion report and inspect the log before trusting artifacts | Fresh artifact validation rather than process exit code alone |

For L40–L43, follow [bounded asset spikes](asset-spikes.md). Pose-transform snapshots do not capture animation, constraints, or rest data.

| L44 | A rig's bone anchors were useful for measurements but did not locate facial surface landmarks | Export pose-aware normalized bounds/anchors; label their meaning and align expression separately | Transformed-instance and sparse rotated-mesh measurement checks |
| L45 | A second shape preset reused construction code but did not establish quality on another character | Separate generator, per-character parameters, and cross-character benchmark | Treat parameter reuse and target likeness as separate results |
| L46 | Voxel union made a facial assembly connected/manifold while cheek and lip shapes stayed wrong | Replace the surface representation with explicit mouth/cheek boundary layout | Profile and oblique review can reject a one-component watertight head |
| L47 | An old facial color boundary put black patches on newly enlarged cheek volume | Re-author or transfer the material-region field after topology/volume changes | Review clay geometry separately from material boundaries; report regenerated attributes |

| L48 | Shared mouth/cheek topology removed assembly seams but still yielded a wedge muzzle and pinched corners | Measure target surface correspondences and fit new topology; stop guessing curve coordinates | Exact boundary/helper checks plus independent multiview likeness review |

For L44–L48, follow [independent reconstruction](independent-reconstruction.md). Complete independent likeness has not been demonstrated by these regional trials.

| L49 | Procedural pose generation reset bone bases then read stale matrices, accumulating root offsets and unreachable leg targets | Update the dependency graph between reset and matrix reads | Reopened cycle endpoint equality, leg reach and per-frame shoe-floor checks |

For L49, follow [animation](../references/animation.md). In-place contact checks do not establish world-space foot locking.

## Follow the applicable procedure

For L01–L08, read [reconstruction](../references/reconstruction.md), then [polish](../references/asset-polish.md) when a clean rebuild is required. For L09–L14, read [animation](../references/animation.md), [jobs](../references/jobs.md), or [delivery](../references/delivery.md) according to the failing stage. New local surface trials and their limitations belong in [regional surface experiments](regional-surfaces.md).

Do not erase failed approaches when a later version succeeds. Record the conditions under which a method failed; a regional method succeeding does not retroactively prove that a whole-character application was safe.

For L22–L25, follow [hands and gloves](hands.md); the observed benchmark covers an open glove and rigid wave, not independent finger articulation.

For L26–L28, follow [fast model iteration](model-iteration.md).

For L29–L31, use the regional repair steps in [fast model iteration](model-iteration.md).

For L32–L35, follow [reference-model comparison](reference-comparison.md).

For L36–L39, read the external-blend findings in [reference comparison](reference-comparison.md).
