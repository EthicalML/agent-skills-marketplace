---
name: rpi-plan
description: Turn approved RPI decisions into a gated, reviewable implementation and verification plan. Use after rpi-adrs and before rpi-implement.
---

# Plan an RPI implementation

Work only inside the selected `adr/<NNN>-<name>/`. The files are the workflow state. Keep phases, pull requests, and documents as few and short as the change allows.

## 1. Resume from the files

Read the initial request, research findings, approved ADRs, usage cheatsheet, and existing plan files. Summarize the current position and offer the next unfinished step. If the user does not choose it, stop. If the user has just invoked this skill and the stage has no files yet, that invocation is the choice: proceed directly to the next step without asking again.

Treat `plan/proposed-plan.md` as approved only when it says `Status: approved`. Gates run in the main session, never in subagents.

## 2. Propose the plan

Write `plan/proposed-plan.md` with `Status: proposed` and:

- the minimum ordered phases and dependencies;
- the minimum pull-request split that leaves every PR independently reviewable;
- comprehensive, reviewable conventional commits within each PR;
- exact acceptance signals and a verification section;
- unresolved forks, each assigned an approved parallel spike rather than an assumed answer.

For every phase, name its intended `plan/P<n>-<name>.md`, changed areas, verification, and user review point. A small change may need one phase and one PR.

Commit the gate document alone with a comprehensive conventional commit. Present it for approval or edits and stop.

## 3. Plan verification manual-first

Make verification eager and part of each phase:

1. Check that the target repository's `tmp/` directory is ignored by Git; add `/tmp/` to its `.gitignore` if needed.
2. Use quick scripts under the target repository's `tmp/` directory to exercise real behavior repeatedly. Never assume it works: run it, inspect the result, and hand it to the user early.
3. Once the manual loop stabilizes, add a scripted smoke gate built from what it found.
4. Add opt-in end-to-end checks only where warranted. For UI-heavy work, use `verify-streamlit-app` for Playwright visual checks. For Kubernetes work, validate on a kind cluster.

Tests must exercise meaningful multi-step workflows. Do not add input-equals-output checks such as `1+1=2` unless that behavior is itself the requirement.

For verification likely to exceed a stated time threshold, plan parallel execution with an explicit concurrency cap and reason. Keep the default sequential when parallelism adds no value.

## 4. Record approval and phase plans

After explicit approval, change the gate to `Status: approved` and commit that change. Write the approved phase details to `plan/P<n>-<name>.md`, keeping each below code-review cost. Include concrete files, steps, manual handoff, smoke gate, conditional end-to-end checks, and review boundary.

Update `adrs/usage-cheatsheet.md` with verified planned usage. Commit every phase document and the cheatsheet separately with comprehensive conventional commits as they land.

## 5. Stop at the handover

Present the approved proposal, phase documents, verification sequence, review boundaries, cheatsheet, and commits. State that planning is complete, offer to start `rpi-implement`, and stop. Never begin implementation silently.
