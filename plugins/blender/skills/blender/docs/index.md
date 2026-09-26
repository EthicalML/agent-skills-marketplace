# Blender workflow and learning index

Use this index when a task needs more than connection setup or a simple scene edit. Read only the rows relevant to the current problem. The documents distinguish methods observed in a real run from researched or proposed capabilities; a workflow description is not evidence that an automatic modeling utility exists.

| Task or symptom | Read next | Evidence level |
| --- | --- | --- |
| Reconstruct likeness from images | [Image reconstruction](../references/reconstruction.md), then [local Apple Silicon generation](../references/local-image-to-3d.md) when using that backend | Tested local candidates; hidden surfaces and deformation remain separate checks |
| Recognizable asset, poor finish | [Polish workflow](../references/asset-polish.md), then [regional surface experiments](regional-surfaces.md) | Research plus bounded regional trials; not automatic production retopology |
| Repair thumb placement, finger proportions, or cuff joins | [Hands and gloves](hands.md), then [quality review](quality-review.md) | Open-glove and rigid-wave iterations; finger articulation remains separate |
| Decide which quality check is missing | [Quality review](quality-review.md) | Failures observed in reconstruction, glove repair, and export runs |
| Understand failures and avoid repeating them | [Learning log](learning-log.md) | Observed outcomes, limits, and links to the applicable procedure |
| Select the next capability to implement | [Workstreams](workstreams.md) | Explicit implementation and validation status |
| Rig interaction, blinks, contacts, or portable animation | [Animation workflow](../references/animation.md) and the animation/export rows in [Learning log](learning-log.md) | Limited performance and reimport benchmarks; not a full facial rig |
| Render, bake, or run expensive validation | [Background jobs](../references/jobs.md), then [iteration](../references/iteration.md) | Tested separate-process jobs and comparable previews |
| Package an editable project or export | [Delivery](../references/delivery.md) | Reopen/reimport and video verification; appearance still requires inspection |
| Invoke Blender capabilities from Python | [Python API](../references/python-api.md); inspect live RNA for version-specific operators | Implemented client, not a high-level character modeling API |

## Capture a learning during work

1. Keep private reference images, project paths, logs, and before/after evidence in the user's project. Name the defect, attempted intervention, result, and decision; include an artifact path and settings.
2. Classify the result as observed, researched, API-probed, implemented, or validated on this asset. A successful command or clean topology count is not a visual pass.
3. Add portable findings to the learning log with the cause or suspected cause, recovery, and the check that would catch a recurrence. Label a suspected cause as a hypothesis.
4. Put reusable steps in the relevant workflow document. Link from this index and from the conditional step in SKILL.md; avoid copying the same procedure into several files.
5. Update workstream status only when the stated evidence exists. Keep rejected trials and remaining limits visible. Run repository validation before publishing changes and refresh the installed skill after an update.

Existing reference paths remain valid; this index organizes them rather than moving files that installed workflows may already use.
