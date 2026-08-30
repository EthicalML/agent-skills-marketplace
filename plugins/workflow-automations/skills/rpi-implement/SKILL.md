---
name: rpi-implement
description: Execute an approved RPI plan pull request by pull request with eager verification, user review gates, and implementation learnings. Use after rpi-plan.
---

# Implement an RPI plan

Work only from the approved files in `adr/<NNN>-<name>/`. The files are the workflow state. Keep the implementation proportionate and preserve the planned review boundaries.

## 1. Resume from the files

At every fresh start, read the approved plan, phase documents, ADRs, usage cheatsheet, existing learning files, Git history, and worktree state. Map completed commits and pull requests to the plan, summarize the current position, offer the next unfinished step, and stop until the user chooses it.

Do not infer approval from conversation history alone. Gates and user review stay in the main session, never in subagents.

## 2. Implement the next pull request

Confirm its scope and acceptance signals from the plan. Parallelize independent bounded work when it reduces elapsed time, but keep dependent changes ordered and reconcile all results in the main session.

Make the smallest coherent changes. Use comprehensive, reviewable conventional commits for each logical change. Keep every workflow document inside the effort folder and commit each landed document separately.

If implementation exposes multiple viable paths, stop and propose parallel spikes. Document observed results and ask the user to choose; do not silently depart from the ADRs or plan.

## 3. Verify eagerly

Run the phase's manual-first loop as each piece lands:

1. Confirm the target repository's `tmp/` directory is ignored and keep quick scripts there.
2. Exercise the real multi-step workflow, inspect the output, and hand it to the user early.
3. Run the scripted smoke gate once the manual behavior stabilizes.
4. Run opted-in end-to-end checks, including `verify-streamlit-app` for UI-heavy work or a kind cluster for Kubernetes work.

Use the plan's time threshold and concurrency cap for slow verification. Never replace a real workflow check with a trivial input-equals-output test.

## 4. Capture learnings while working

As soon as a durable lesson appears, write `implement/learnings/L<n>-<topic>.md`. Record what broke, the observed evidence, what the documentation or plan got wrong, the fix or decision, and what a future harness should assert. Do not reconstruct learnings at the end.

Keep `adrs/usage-cheatsheet.md` aligned with behavior that has actually been verified. Commit every learning document and cheatsheet update separately with comprehensive conventional commits as they land.

## 5. Stop for review between pull requests

Present the current PR's changes, commits, verification evidence, learnings, caveats, and the approved `plan/proposed-plan.md`. Ask the user to review. Do not start the next PR until they approve and explicitly choose to continue.

After the final PR, present the same evidence against every plan phase and stop. Ask whether to close the effort or plan follow-up work; do not perform release or cleanup work silently.
