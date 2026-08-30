# Release Conformance Scorecard — assessment template

Assess how a repository conforms to the generic release contract. Produce a scorecard a human can use to decide what must change before the automated release skill may create a release.

Work only from repository contents. Do not invent facts. Every scorecard row must cite repository file paths. When a status depends on GitHub settings, provisioned secrets, external registries, or anything else outside repository files, use `unknown`; never guess. If an existing release profile records an accepted divergence, retain it as a profile fact and do not propose it again. Accepted divergences cannot waive required rows.

## The release contract

Assess the repository against exactly these requirements:

| ID | Requirement | Level |
| --- | --- | --- |
| R1 | A release workflow triggers on semver tag push (`vX.Y.Z`-style) and has a validate job that parses and checks the version from the ref | required |
| R2 | The release workflow supports `workflow_dispatch` runnable against a tag ref for sessions that cannot push tags, or a companion tag-creation dispatch workflow exists | recommended |
| R3 | Tests gate all publication jobs: publish jobs depend on a test job | required |
| R4 | Every published artifact has a producing job in the release workflow | required |
| R5 | Every published artifact has a concrete post-release validation command or URL from repository documentation or a direct derivation such as `docker pull` or `pip install` | required |
| R6 | The GitHub release or assembly job requires its asset-producing jobs to succeed; it cannot assemble a release over failed publishes | required |
| R7 | A version-bump mechanism exists, as a job or documented procedure, that moves the repository to the next development version after release | recommended |
| R8 | Version locations are enumerable: files carrying the version are identifiable and consistent with one another | required |
| R9 | Secrets and environments referenced by release workflows are named and documented in the repository | recommended |
| R10 | Release-notes conventions exist, or the skill default of Overview, Highlights, and a preserved generated changelog applies without conflict | recommended |
| R11 | No release-workflow job references artifacts, images, or directories that do not exist in the repository | required |
| R12 | A test-tag or rehearsal path exists, such as an excluded tag range that triggers a docs-only run | optional |

## Output format

Produce exactly these four sections:

### 1. Scorecard

Return one row per requirement:

| ID | Status | Evidence | Proposed change |
| --- | --- | --- | --- |

Status is one of `pass`, `partial`, `missing`, `divergent` (the repository contradicts the contract), `unknown` (repository files cannot determine the status), or `n/a` (the requirement or artifact class does not apply; explain why). Evidence must cite file paths, including for `unknown` and absence findings. Proposed change is one concrete sentence and is empty for `pass` or `n/a`. For `divergent`, state what the repository does instead and whether conformance would change behavior. Do not repeat a recorded accepted divergence as a proposed change.

### 2. Verdict

Choose exactly one verdict:

- `conformant`: all required rows pass and no unresolved drift warrants a repository change.
- `conformant-with-drift`: all required rows pass, but unresolved divergences or unknowns warrant a repository change or human verification.
- `partial`: at least one required row is partial, missing, divergent, or unknown; list those row IDs.
- `greenfield`: no release CI exists and the repository intends versioned releases.
- `not-applicable`: the repository is deliberately unversioned and continuously deployed from its default branch, with no version fields or release tags.

Write one short paragraph justifying the verdict and naming the single highest-impact change, except that `not-applicable` names the decisive evidence instead. A continuous-deployment workflow mapped honestly onto the contract, such as deployment gated on a successful build corresponding to R3 and R6, is evidence for `not-applicable`, not partial conformance. Do not use `not-applicable` merely because release files are missing; use `greenfield` unless repository evidence shows the deliberate unversioned model.

### 3. Proposed change set

Give an ordered list of concrete repository changes a setup PR would make. Tag each item `[required]`, `[recommended]`, or `[optional]` and name the files it would touch. For `greenfield`, specify which template artifact classes to retain and prune. Put actions that require a human outside the repository, such as provisioning secrets, configuring trusted publishers, or enabling Pages, in a separate `Human provisioning` sublist. Use an empty list when no changes are proposed.

### 4. Deliberate-divergence candidates

List behavior that appears intentional and should become a recorded profile fact rather than a change. Include the evidence path and rationale. Do not repeat divergences already accepted in the profile. Use an empty list when there are no candidates.

Keep the complete output under approximately 100 lines. Be concrete and avoid generic advice.
