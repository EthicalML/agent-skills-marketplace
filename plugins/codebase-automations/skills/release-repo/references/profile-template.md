# Release Repo Profile — bootstrap template

Generate a repo-local profile for the generic `release-repo` skill. The skill owns release policy: conformance scoring, setup gating, preflight, semantic release notes over a generated changelog, release creation, CI monitoring, artifact validation, and post-release reporting. The profile supplies repository data only.

Work only from repository contents. Do not invent facts. If a fact cannot be grounded in a file you read, write `unknown — fill in manually`. A repository with no release process is a valid outcome. Distinguish a greenfield versioned-release intent from a deliberately unversioned continuous-deployment model; only the former needs workflow scaffolding.

Return one Markdown document with exactly these eight sections:

## 1. Versioning & tagging

Document the tag format, current-version locations, test-tag or prerelease conventions, and next-development-version scheme. Cite repository files for every claim.

## 2. Release workflows & jobs

List existing release-related files under `.github/workflows/`, their triggers, every job a release executes, any reusable workflows they call, and the concrete test and lint commands that gate publication. Identify the release workflow filename the skill should monitor. If none exist for a repository that intends versioned releases, write exactly `none — release CI needs scaffolding`. For a deliberately unversioned repository, describe the continuous-deployment workflow instead.

## 3. Artifacts & validation

Provide a table with columns `Artifact | Class | Destination | Producing job | Validation command`. Give every released artifact its own row and its own concrete post-release command using `X.Y.Z` as the version placeholder; validate web destinations with a command such as `curl -sI`. Include downstream or syndicated repositories as ordinary rows. When no release exists, infer only artifact classes directly supported by repository contents and mark each row `proposed`.

Use these common class names when applicable: `container image`, `package`, `docs/pages`, `chart`, and `GitHub release`. Extra repository-specific classes are allowed. Never merge multiple artifacts into one validation command.

## 4. Release notes conventions

Document where release notes live and any required format or changelog-generation convention. If none exists, write exactly `none documented — skill default applies (Overview + Highlights + Generated changelog)`.

## 5. Post-release steps

Document version-bump pull requests, docs-rebuild remedies for deployment races, smoke-test procedures, cleanup, and additional publication. Cite the workflow or instruction file for each. Write `none documented` when appropriate.

## 6. Secrets & environments

List names, never values, of required secrets, environments, and trusted-publisher configurations. These are human-provisioned prerequisites. Write `none documented` if repository files name none, and flag external configuration as requiring human verification.

## 7. Repo-specific gotchas

Record release constraints from agent instructions and documentation, including ordering dependencies, known race conditions, environment quirks, and manual steps. Cite every item. Do not repeat generic skill policy.

### Accepted divergences

List intentional departures from recommended or optional contract requirements, including changes a human declined during setup, with the repository evidence and decision rationale for each. Record a deliberately unversioned continuous-deployment model here. Write `none` when there are no accepted divergences. Accepted divergences cannot waive required release-contract rows.

## 8. Confidence notes

Write one short paragraph identifying well-grounded and thin sections and what a human must verify before trusting the profile, especially repository settings, secrets, environments, and external registries.

Keep the profile under approximately 120 lines. Be concrete, concise, and repository-grounded.
