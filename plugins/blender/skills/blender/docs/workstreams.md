# Reconstruction and animation workstreams

Use this list to select bounded implementation work. Read [polish](../references/asset-polish.md) for the overall procedure and [quality review](quality-review.md) for acceptance. Status applies to the tested scope only; no row implies arbitrary character automation.

| Workstream | Current evidence | Next bounded output | Acceptance gate |
| --- | --- | --- | --- |
| Reference review | Fixed review views implemented; read-only tight bounds and normalized rig-anchor helper tested on one asset and transformed/sparse fixtures | Reusable named landmark and defect register | Reject wrong anatomy even when topology/export succeeds |
| Regional audit | Topology/component checks implemented for gloves; counts alone missed visual failure | Expected-boundary metadata and regional evidence views | Distinguish deliberate openings, accidental bridges, and style defects |
| Regional surface reconstruction | Regional remesh and radial-fit candidates rejected; controlled surface prototype built and visually reviewed, facial/deformation quality still limited | Preserve useful reference volumes while rebuilding damaged surfaces | Fixed front/oblique/profile/rear views improve without losing silhouette or facial structure |
| Controlled cage and loop construction | Project loft/sweep and annular quad-bridge helpers tested; shared topology passes but facial likeness rejected | Measured semantic curve correspondence and constrained fit of new topology | Stable subdivision and expression tests; no copied source cracks |
| Hands | Wrist-relative thumb/web and cuff revisions validated visually for an open glove; 192-frame sampled head-clearance check passed; finger articulation remains pending | Broader reference-style review and finger articulation when required | Visual comparison plus intended pose tests |
| Materials/detail transfer | Rest-space simple palette validated; sophisticated UV/bake transfer not benchmarked | Regional UV/material boundaries and a small selective bake | No cross-part leakage, seams, or baked reconstruction damage |
| Facial controls | Eye-bone squash exported; absolute jaw closure and cheek narrowing visually reviewed on one source rig | Sculpted lip rounding/contact poses and proper eyelids | No penetration or loss of volume through intermediate shapes |
| Speech timing | Rhubarb 1.14.0 cues baked into a separate facial Action for one short utterance; saved-file closure/audio/channel checks pass | Another phrase, better E/F poses and playback acceptance | Closed pauses/consonants, recognizable vowels, aligned sound and no conflicting jaw curves |
| Deformation | Limited explicit nine-bone performance validated; imported 91-bone asset preserved with three static perturbations reviewed | Broader joint/finger stress poses and local corrective shapes | Acceptable volume and contact beyond the original wave |
| Visual regression | Controlled views and inspection rejected a numerically valid but pointed muzzle; general metrics pending | Fixed-camera silhouette/landmark comparisons with visual decisions | Reject a visibly worse candidate that passes numerical checks |
| Delivery | Animated export, sampled roundtrip, and complete video checks validated for one short | Local facial/finger regression after topology changes | Reimport preserves the new approved deformation, not just bounds |
| Optional assisted tools | Artist workflows and add-on documentation researched | Small version-pinned comparison against native methods | Demonstrated quality/time benefit; no assumed headless API or compatibility |

## Update a status

Record the test asset class, failure it detects, settings, evidence, and remaining limits. Update this table and the project learning log together. For an experiment still running, do not mark its method validated. If rejected, retain the failure and choose a materially different intervention rather than polishing the rejected result.

Promote project helpers into the skill only after they handle a real case and a meaningful failure-sensitive check. Candidate utilities include fixed review rendering, regional mesh audit, constrained fitting, loop-patch construction, attribute transfer, and deformation comparison. These names describe needed functions; they are not current client API endpoints.
