# Dependabot Fix Repo Profile — bootstrap template

Generate `.github/dependabot-fix-profile.md` for the repository. Work only from repository files such as dependency manifests, `.github/dependabot.yml`, workflows, build files, documentation, and agent instructions. Do not use outside knowledge or invent facts. Write `unknown — fill in manually` when evidence is absent. Keep the profile under approximately 120 lines and cite a repository path for every factual claim.

Use exactly these eight sections:

## 1. Ecosystems & directories

From `.github/dependabot.yml`, list every package ecosystem, directory, schedule, and grouping strategy, including group names. Say when that file is absent. Also identify dependency manifests in directories not covered by Dependabot.

## 2. Build & test commands per directory

For every Dependabot-covered directory, list dependency installation, unit test, lint, and build commands when applicable. Ground each command in a build file, package script, workflow, or agent instruction and cite that source. Add a verification marker to every test and lint command: `verified` when its bootstrap smoke-test succeeds, or `unverified — <reason>` when it fails or cannot run.

## 3. Risk ordering (easy → hard)

Order ecosystems and directories for batch processing from lowest to highest risk. Give a short evidence-based reason for each position; prefer CI-only changes before runtime libraries and broad user-facing frameworks.

## 4. Hold-for-human policy

List concrete packages by ecosystem whose major versions must never be auto-merged even with green CI. Use this for broad frameworks or surfaces whose regressions may evade automated tests. If repository evidence supports no entries, write `none documented`; the skill's default UI-framework-major hold still applies until a human reviews this profile.

## 5. Merge policy

Record the repository's merge method convention and any additional auto-merge conditions, citing contribution guidance, agent instructions, or repository configuration. If no convention is documented, write `merge commit (skill default)`. State that this profile cannot weaken the skill's merge-safety invariants: zero checks is not green; `mergeStateStatus` must be `CLEAN`; hold-for-human majors are never auto-merged; restricted sessions never push to `dependabot/**`; and merge commits are used unless this section documents a different repository convention.

## 6. CI checks & known flakes

List the check names expected on Dependabot pull requests and relevant workflow path filters, derived from `.github/workflows/*`. List rerun-once candidates only when a repository file documents them; otherwise write `none documented`.

## 7. Repo-specific gotchas

Summarize dependency-update constraints from `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and `.github/instructions/*`, when present. Include required code generation, toolchain alignment, branch conventions, local services, integration environments, and documentation duties. Cite every item.

## 8. Confidence notes

In one short paragraph, distinguish well-grounded sections from thin or unknown sections and state what a human should verify before relying on the profile.
