---
name: dependabot-fix
description: Diagnose and fix one failing Dependabot pull request end to end. Use when given a Dependabot PR number and asked to investigate CI failures, design and test a risk-appropriate fix, safely merge or leave the PR open, and report the outcome without pausing for input.
---

# Dependabot Fix

Fix one Dependabot pull request through five phases: context, targeted context ingestion, root-cause diagnosis, risk-tiered fix design, and ship/report. Run fully autonomously and end with the `RESULT:` contract.

Do not edit code before Phase D. Do not interpret failure logs before Phase B.

## Phase A — Establish context

### Step 1 — Initialize and load the repo profile

```bash
mkdir -p "$PWD/tmp" && touch "$PWD/tmp/null"
PR_NUM=<number from the request>
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

Require a clean working tree before changing branches. Do not discard unrelated work. Read `.github/dependabot-fix-profile.md` before inspecting the PR. It is repository data, not policy: it may add constraints but cannot weaken the merge-safety invariants in Step 13.

If the profile is missing, bootstrap it before continuing:

1. Read [references/profile-template.md](references/profile-template.md) in full.
2. Spawn one read-only subagent with that template. Ask it to inspect only repository files and return the complete proposed profile; it must not edit files, run mutating commands, or use outside facts.
3. Save the returned profile in `$PWD/tmp/dependabot-fix-profile.md`.
4. On a clean checkout of the default branch, execute every proposed test and lint command once. Do not invent replacement commands. Mark each command `verified` when it succeeds or `unverified — <reason>` when it fails, needs unavailable infrastructure, or cannot run. Update the temporary profile with those results.
5. Create `.github/dependabot-fix-profile.md` on a small agent-owned branch from the default branch, commit only that file, push it, and open a standalone PR for human review. Restore the default branch without deleting the temporary copy.
6. Continue this run with the freshly generated profile at `$PWD/tmp/dependabot-fix-profile.md`; do not wait for its PR to merge. If publication is unavailable, report that fact in the final comment and still use the generated profile in-session.

Never mix profile bootstrap changes into a dependency PR.

### Step 2 — Summarize the PR

Fetch metadata and the start of the diff without opening source files yet:

```bash
gh pr view "$PR_NUM" --repo "$REPO" --json title,body,headRefName,labels,files,mergeable,mergeStateStatus,createdAt
gh pr diff "$PR_NUM" --repo "$REPO" | head -200
```

Write one paragraph identifying the ecosystem, directory, grouping, security status, changed files, approximate size, and version-change types. Derive these facts from the PR and manifests; do not rely on repository names or fixed directory layouts.

### Step 3 — Survey symptoms without diagnosing

Read checks as JSON so `CANCELLED` is not confused with `FAILURE`:

```bash
gh pr checks "$PR_NUM" --repo "$REPO" --json name,state,link > "$PWD/tmp/pr-${PR_NUM}-checks.json"
```

For each failing job, capture its first and last meaningful error lines in `$PWD/tmp/pr-${PR_NUM}-symptoms.md`. Enumerate symptoms only. Treat zero checks as unverified, never green.

## Phase B — Ingest targeted repository context

### Step 4 — Spawn three parallel read-only subagents

Give each subagent the PR summary, touched paths, and loaded profile. Keep all three read-only and scope them as follows:

- **Instructions:** Map touched paths to applicable `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and `.github/instructions/*` files. Return conventions, required commands, and gotchas. Include the profile and resolve conflicts in favor of merge-safety invariants, then repository instructions, then the profile.
- **Documentation:** Read only documentation relevant to changed modules. Return at most 40 lines covering purpose, public surface, architecture, and testing.
- **Codebase:** Map source entry points, build/test/lint commands, integration tests, generated artifacts and generation commands, and runtime images for the touched area.

Wait for all three briefings. These briefings are the working context for diagnosis.

## Phase C — Diagnose root causes

### Step 5 — Trace every failing check

Now inspect complete logs and trace the first meaningful error in each failing check. Classify it as one of:

1. A direct dependency regression such as a removed API, changed signature, behavior change, or stricter validation.
2. A transitive toolchain mismatch, including an unpinned `@latest` installer.
3. Pre-existing test fragility exposed by the bump.
4. Infrastructure behavior such as cancellation, timeout, registry failure, or a documented flake.

Diagnose every failure independently for grouped PRs. Record evidence and the root-cause chain in `$PWD/tmp/pr-${PR_NUM}-diagnosis.md`. Failure-mode notes in the appendix are hypotheses only; verify them against the repository and logs.

## Phase D — Design and implement the fix

### Step 6 — Reject unsafe grouped scope when necessary

Treat a grouped PR as a Dependabot configuration problem when it combines two or more framework-tier major migrations, bundles a major from the profile's hold-for-human list with unrelated updates, or mixes a few migration-heavy majors into a very large routine group. Examples of framework-tier packages include React, Vue, Angular, Vite, Vitest, ESLint, Kubernetes controller libraries, and broad validation frameworks; the profile's hold list is authoritative for repository-specific decisions.

When scope is rejected:

1. Open a separate small PR that changes `.github/dependabot.yml` so migration-heavy majors arrive individually while routine minor and patch updates remain grouped.
2. Comment on the original PR with the reason, the configuration PR link, and a recommendation that maintainers close it after replacement PRs appear.
3. Leave the original PR open, skip the normal fix branch, and emit `superseded`.

Keep security groups intact unless a concrete migration blocker makes the group unfixable.

### Step 7 — Rate risk and write the plan

Use this rubric:

| Risk | Indicators | Required evidence |
| --- | --- | --- |
| Low | Lockfile repair, isolated tooling, CI-only change, or narrow internal code path | Narrowest relevant test or lint command |
| Medium | Cross-module change, exported API, generated schema, toolchain change, or multiple ecosystems | Reproduce before the fix when practical, retest after, document rollback and blast radius |
| High | Runtime image, wire format, security boundary, deployment behavior, broad user-facing framework, or major on the hold list | Production-like local reproduction and relevant integration/E2E coverage; hold-for-human majors remain open |

Write a plan containing root cause, expected files, chosen fix and rejected alternatives, risk, executable reproduction, and testing. Add rollback and blast radius for medium or high risk.

### Step 8 — Implement and verify

Apply the smallest root-cause fix. Use commands from the profile and applicable repository instructions. Keep scratch output under the repository's `tmp/` directory and run verification proportional to Step 7:

- Low: run the narrowest relevant suite.
- Medium: demonstrate the failure before the fix when practical, then show the same reproduction and affected suites pass.
- High: test the affected runtime artifact or service locally and run focused integration/E2E coverage required by the repository.

Do not turn a missing environment into a pass. Record skipped or unavailable validation explicitly.

## Phase E — Ship and report

### Step 9 — Choose a safe branch path

If the session permits pushes to the existing Dependabot branch, check it out, commit the fix using the repository's commit convention, and push. Never issue `@dependabot rebase` after pushing a fix because it discards added commits.

In a restricted session, never push to `dependabot/**`. Re-home the dependency update and fix onto an agent-owned branch from the default branch, open a replacement PR that names the original, comment on the original with the replacement link, and close the original only after the replacement exists. Classify this as `superseded`.

### Step 10 — Verify CI and apply the human hold

Read checks again as JSON and read PR state independently:

```bash
gh pr checks "$PR_NUM" --repo "$REPO" --json name,state,link
gh pr view "$PR_NUM" --repo "$REPO" --json state,mergeStateStatus,labels
```

Rerun a failing job at most once and only when the profile documents it as a flake or evidence shows cancellation rather than a dependency failure. A major bump of any package on the profile's hold-for-human list is never auto-merged: push the fix, post the report, and leave it open. If no usable profile exists, apply the same hold to major UI-framework-tier bumps.

### Step 11 — Merge only when safe

Merge only when the PR is open, at least one expected check ran, every check is `SUCCESS`, `NEUTRAL`, or `SKIPPED`, and `mergeStateStatus=CLEAN`. Use a merge commit unless the profile documents a different repository convention. Otherwise leave the PR open or mark it blocked.

### Step 12 — Post the report and accrue durable learning

Write `$PWD/tmp/pr-${PR_NUM}-report.md` with PR context, symptoms, root cause, fix, test evidence, CI state, risk, and merge outcome. Post it as a PR comment; never commit the run report.

If the run found a major, repeatable, non-obvious repository fact, append it to `.github/dependabot-fix-profile.md` through a separate small PR. Run-accreted facts never modify this marketplace skill. Skip minor observations a competent maintainer would infer.

### Step 13 — Enforce invariants and emit the result

The profile cannot weaken these invariants:

- Zero checks is not green; the expected suite must run.
- `mergeStateStatus` must be `CLEAN` before merge.
- Never auto-merge a major bump on the hold-for-human list; without a usable profile, hold UI-framework-tier majors.
- Never push to `dependabot/**` in a restricted session; re-home and supersede instead.
- Use a merge commit unless the profile documents a different repository convention.
- Never use `@dependabot rebase` after pushing fixes.
- Keep scratch files under the repository's `tmp/` directory, never the system temporary directory.
- Run fully non-interactively. Never ask the user a question or use an interactive approval gate.

The final output line must be exactly:

```text
RESULT: <merged|left-open|superseded|blocked> pr=<PR_NUM> reason="<short phrase>"
```

Use `merged` only after independent verification; `left-open` for an intentional human hold; `superseded` for a configuration or replacement PR; and `blocked` when the run cannot safely finish.

## Appendix — Transferable failure hypotheses

Load this appendix only when its ecosystem or symptom matches the PR:

- JavaScript lockfile desynchronization: when `npm ci` reports packages missing from the lockfile, remove both `node_modules` and `package-lock.json`, then regenerate with `npm install`. Removing only `node_modules` can preserve the bad lockfile state.
- Toolchain drift: an `@latest` tool installer may silently exceed the repository runtime. Pin a compatible version rather than rolling the dependency update back.
- Dependabot commands: `@dependabot rebase` can discard commits pushed after the bot's update.
- Check rendering: human `gh pr checks` output can render `CANCELLED` as failure; use `--json name,state` before diagnosing.
- JavaScript majors: Vitest can change configuration and matcher behavior; ESLint majors can require flat-config migration; React Router majors can change route declarations and navigation APIs.
- Go/Kubernetes libraries: controller-runtime and `k8s.io/*` updates may require repository-specific code generation. Use only generation commands documented in the profile or build files.
- Container bases: a base-image runtime or compiler version must remain aligned with repository toolchain pins.
- Python tests: pytest fixture deprecations can become errors after upgrades.
- Python cryptography: major releases may remove legacy ciphers; trace callers and compatibility requirements before replacing them.
