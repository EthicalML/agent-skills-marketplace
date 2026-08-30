---
name: release-repo
description: Release a repository end to end using a repository-local release profile. Use when asked to prepare or execute a semantic version release, monitor release CI, validate every published artifact, complete documented post-release work, or maintain historical GitHub release notes without pausing for input.
---

# Release Repo

Release a repository through profile bootstrap, preflight, semantic release notes, release creation, CI monitoring, artifact validation, and post-release cleanup. Run non-interactively within each phase. Release runs finish with the status table in Step 12.

The repo profile at `.github/release-profile.md` is repository data, not policy. It supplies version locations, workflows, artifacts, validation commands, and post-release procedures, but it cannot weaken the invariants in Step 13.

## Phase A — Establish release configuration

### Step 1 — Initialize and derive repository context

```bash
mkdir -p "$PWD/tmp" && touch "$PWD/tmp/null"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

Never hardcode the repository or default branch. Require authenticated repository access and a clean working tree before changing branches. Never discard unrelated work.

### Step 2 — Load or bootstrap the repo profile

Read `.github/release-profile.md` in full before inspecting release state. If it exists, continue to Step 3.

If it is missing, bootstrap it before any release work:

1. Read [references/profile-template.md](references/profile-template.md) in full.
2. Spawn one read-only subagent with that template. Ask it to inspect only repository files and return the complete eight-section profile; it must not edit files, run mutating commands, or use outside facts.
3. Save the returned draft at `$PWD/tmp/release-profile.md` and inspect it for unsupported claims. Use `unknown — fill in manually` wherever the repository does not ground a fact.
4. If profile section 2 identifies existing release CI, create `.github/release-profile.md` on a small agent-owned branch from the default branch, commit only that file, push it, and open a standalone PR for human review. Restore the default branch without deleting the temporary copy. Continue this run with the temporary profile without waiting for merge; this profile-only PR is not the setup PR gated below.
5. If profile section 2 says `none — release CI needs scaffolding`, copy [references/templates/release.yaml](references/templates/release.yaml) and [references/templates/create-tag.yaml](references/templates/create-tag.yaml) to `.github/workflows/` on one small agent-owned setup branch. Retain only optional artifact job blocks matching the proposed artifact classes in profile section 3, adjust `needs` lists to those retained jobs, fill only values grounded in repository files, and leave every human decision or provisioning gap marked `TODO(release-setup)`. Add `.github/release-profile.md`, commit the profile and both workflows together, push, and open one standalone setup PR for human review.
6. If publication is unavailable, report the local branch or patch state, but do not release.

Never mix bootstrap changes into another pull request. When scaffolding was required, never create a tag or release until the combined setup PR is merged and the merged release workflow contains no `TODO(release-setup)` marker. End such a run with `RESULT: setup-pending` and the setup PR or publication blocker.

### Step 3 — Enforce the setup gate

Before releasing from a profile already present on the default branch, verify that every workflow named in profile section 2 exists there and the release workflow contains no `TODO(release-setup)` marker. During a profile-only bootstrap with existing release CI, use the temporary profile and continue. During workflow scaffolding, require the combined setup PR to be merged before continuing.

If any condition fails, stop before version extraction and report `RESULT: setup-pending reason="<short phrase>"`. Do not ask whether to bypass this gate.

## Phase B — Validate the requested release

### Step 4 — Extract and validate the version

Extract the requested tag into `VERSION` and require the tag format documented in profile section 1. For the default `vX.Y.Z` convention:

```bash
VERSION=<tag from the request>
if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid release tag: $VERSION (expected vX.Y.Z)"
  exit 1
fi
VERSION_NUM=${VERSION#v}
```

Do not infer a missing version or silently normalize an invalid one. Apply documented prerelease or test-tag rules from the profile.

### Step 5 — Run preflight checks

Stop and report if any check fails:

1. Fetch the remote and confirm the current checkout is the clean default branch at `origin/$DEFAULT_BRANCH`. Do not switch branches when the working tree is dirty.
2. Confirm the expected CI suite on the latest default-branch commit completed successfully. Use structured `gh` output and the workflow or check names in profile section 2; zero observed checks is not green.
3. Confirm the tag is absent locally and remotely, and `gh release view "$VERSION" --repo "$REPO"` does not find an existing release.
Example repository checks:

```bash
git fetch origin --tags
git status --porcelain
git branch --show-current
git rev-parse HEAD
git rev-parse "origin/$DEFAULT_BRANCH"
gh run list --repo "$REPO" --branch "$DEFAULT_BRANCH" --limit 10 --json databaseId,workflowName,headSha,status,conclusion
git tag -l "$VERSION"
git ls-remote --exit-code --tags origin "refs/tags/$VERSION"
```

The `git ls-remote` command should return no matching ref; distinguish that expected absence from authentication or network failure.

## Phase C — Create the release

### Step 6 — Generate and review semantic release notes

Generate GitHub notes into the repository scratch directory:

```bash
GENERATED_NOTES="$PWD/tmp/generated-notes-${VERSION}.md"
RELEASE_NOTES="$PWD/tmp/release-notes-${VERSION}.md"
gh api "repos/$REPO/releases/generate-notes" \
  -f tag_name="$VERSION" \
  -f target_commitish="$DEFAULT_BRANCH" \
  --jq .body > "$GENERATED_NOTES"
```

Review the generated notes, commits since the previous release tag, merged pull requests, changed files, and any release-note conventions in profile section 4. Write `$RELEASE_NOTES` in this format:

```markdown
## Overview

One or two short paragraphs presenting the release as a coherent update and explaining why it matters.

## Highlights

- Group related changes by user-visible outcome or operational impact.
- State compatibility, migration, or validation notes when supported by the release contents.

## Generated changelog

<GitHub-generated notes preserved verbatim>
```

Preserve the generated changelog verbatim beneath its heading. Do not invent claims. If evidence is thin, say so plainly in the overview.

### Step 7 — Create the GitHub release

Create the release from the default branch using the reviewed notes:

```bash
gh release create "$VERSION" --repo "$REPO" --target "$DEFAULT_BRANCH" --title "$VERSION" --notes-file "$RELEASE_NOTES"
```

If the profile documents that the release workflow must be dispatched because the tag was created by `create-tag.yaml`, dispatch the release workflow explicitly at the tag:

```bash
gh workflow run release.yaml --repo "$REPO" --ref "$VERSION"
```

Never dispatch a ref-reading release workflow at a branch. Refs pushed with the built-in `GITHUB_TOKEN` do not trigger other workflows.

## Phase D — Monitor and validate

### Step 8 — Monitor every release job to a terminal state

Locate the run for this exact tag and release workflow. Poll structured job data until every job is terminal; do not stop when only the headline run is complete or after the first failure.

```bash
gh run list --repo "$REPO" --workflow=release.yaml --limit 10 --json databaseId,headBranch,headSha,status,conclusion
gh run view <run-id> --repo "$REPO" --json status,conclusion,jobs
```

Treat success, failure, cancelled, skipped, and timed out as terminal job outcomes. If a job fails, inspect `gh run view <run-id> --repo "$REPO" --log-failed`, diagnose the root cause, and apply only a safe repository-grounded remedy. Rerun only the affected workflow or failed jobs when supported. Continue monitoring the resulting run until all jobs are terminal.

### Step 9 — Validate every artifact from the profile

Profile section 3 is the complete artifact inventory. Execute each row's validation command independently with `X.Y.Z` or the profile's placeholder replaced by `VERSION_NUM`, and record command evidence and status. Do not substitute a generic check, merge artifact rows, or treat a successful producing job as artifact validation.

If a validation command needs unavailable credentials or infrastructure, mark that artifact `blocked`; never mark it passed. Include downstream publication as ordinary artifact rows when the profile defines it.

### Step 10 — Complete profile-driven post-release work

Perform only the procedures documented in profile section 5:

1. Find the release-generated next-development-version PR, verify its diff and checks, and merge it using the repository's documented merge convention. Use a merge commit when no convention is documented.
2. If documentation validation exposes a documented deployment race, run the profile's documented docs-rebuild remedy, wait for it to finish, and repeat the affected artifact validation commands.
3. Run the profile's documented smoke-test procedure when present and the required environment is available. Record unavailable infrastructure as `blocked`, not passed.
4. Complete any additional post-release publication listed in the artifact table and its producing workflow job.

## Phase E — Maintain or report

### Step 11 — Maintain historical release notes when requested

For a historical-notes-only request, load the profile and apply this procedure without creating a new release:

1. List releases in tag order with `gh release list --repo "$REPO" --limit 100`.
2. Inspect each body with `gh release view <tag> --repo "$REPO" --json body`.
3. Compare adjacent tags with `git log <previous>..<tag> --oneline` and inspect the merged pull requests or changed files needed to support a summary.
4. Rewrite each body to begin with `## Overview`, continue with outcome-grouped `## Highlights`, and preserve the prior generated notes verbatim under `## Generated changelog`.
5. Use `gh release edit <tag> --repo "$REPO" --notes-file <file>`. Retain assets and release metadata. If evidence is insufficient, state that limitation rather than inventing detail.

For a historical-notes-only run, report `Tag | Evidence reviewed | Status` and end with `RESULT: notes-updated reason="<short phrase>"`. Do not continue to the release artifact table.

### Step 12 — Report per-artifact status

Render one row for every artifact in profile section 3, followed by CI and applicable post-release rows:

| Artifact or step | Producing job | Validation | Status |
| --- | --- | --- | --- |
| `<profile artifact>` | `<profile job>` | `<command and concise evidence>` | `passed`, `failed`, or `blocked` |
| Release CI | all jobs | `<run URL; terminal job summary>` | `passed` or `failed` |
| Version-bump PR | `<profile job or n/a>` | `<PR URL or reason>` | `merged`, `left-open`, `failed`, or `n/a` |
| Smoke test | `<profile job or n/a>` | `<procedure result or reason>` | `passed`, `failed`, `blocked`, or `n/a` |

End with exactly one outcome line:

```text
RESULT: <released|failed|blocked|setup-pending> version=<VERSION> reason="<short phrase>"
```

Omit `version=<VERSION>` only when setup stopped before version extraction.

### Step 13 — Enforce invariants

The profile cannot weaken these invariants:

- Derive `REPO` and `DEFAULT_BRANCH` with `gh repo view`; never hardcode either.
- Load the merged repo profile or, when existing release CI allowed a profile-only bootstrap, the freshly generated temporary profile.
- Never create a tag or release while a workflow setup PR is unmerged or a release workflow contains `TODO(release-setup)`.
- Require a clean default branch, green expected CI, and an absent tag and release before creation.
- Preserve generated release notes verbatim beneath the semantic overview and highlights.
- Monitor every release job until terminal and validate every artifact with its own profile command.
- Treat missing checks, credentials, settings evidence, validation, or smoke-test infrastructure as blocked, never passed.
- Keep scratch files under the repository's `tmp/` directory, never the system temporary directory.
- Run non-interactively within a phase. The setup gate is a hard stop, not a question.

## Appendix — Transferable troubleshooting

Load only the item matching the observed failure:

- PyPI trusted publishing: the configured trusted-publisher workflow filename must exactly match the workflow filename, including `.yaml` versus `.yml`.
- Registry publication: verify the credential secret names documented in profile section 6 exist and are authorized for the target registry. Never print secret values.
- Chart or package release assets: the publish or packaging job must complete before the GitHub release-assembly job downloads and attaches its output.
- Helm upgrades: `--reuse-values` retains old image tags, so set every released image tag explicitly during an upgrade.
- Workflow chaining: refs pushed with the built-in `GITHUB_TOKEN` never trigger another workflow; dispatch the release workflow explicitly at the created tag.
