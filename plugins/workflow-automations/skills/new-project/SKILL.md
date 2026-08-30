---
name: new-project
description: Start an RPI research-to-implementation effort by recording the request and creating its numbered documentation folder. Use when beginning a project or feature that should follow the RPI workflow.
---

# Start an RPI project

The files under `adr/<NNN>-<name>/` are the workflow state. Keep every document short, plain, and useful. Use less structure for small changes, but keep the stage gates and explicit handovers.

## 1. Check for an existing effort

Inspect `adr/` in the target repository before creating anything. If an effort already matches the request, inspect which files exist, summarize the current position, offer the next unfinished step, and stop. Do not create a duplicate.

## 2. Capture the scope

Ask only for missing information needed to state:

- the problem and desired outcome;
- users and important workflows;
- requirements, constraints, and explicit exclusions;
- known acceptance signals and unresolved questions.

Do not invent choices. If multiple viable paths are already apparent, record them as questions for research or parallel spikes.

## 3. Create the effort folder

Choose the next free three-digit number under `adr/` and a short kebab-case name. Use this stage layout as it becomes needed:

```text
adr/<NNN>-<name>/
  research/
    proposed-research.md
    research-findings-<n>-<name>.md
    research-ref-<n>-<m>-<name>.md
  adrs/
    000-initial-request.md
    proposed-adrs.md
    adr_<NNNN>_<slug>.md
    usage-cheatsheet.md
  plan/
    proposed-plan.md
    P<n>-<name>.md
  implement/
    learnings/
      L<n>-<topic>.md
```

Create only the directories needed now; later skills add their own files.

## 4. Write and commit the initial request

Write `adrs/000-initial-request.md` with a concise normalized scope, acceptance signals, open questions, and a final `Verbatim request` section containing the user's request unchanged. Keep private or sensitive material out of documents intended for a public repository.

Show `adrs/000-initial-request.md` to the user, incorporate any corrections, and then commit this document alone with a comprehensive conventional commit, such as `docs(rpi): capture initial request for <name>`.

## 5. Stop at the handover

Present the initial-request document, its path, and its commit. State that project setup is complete, offer to start `rpi-research`, and stop. Never begin research silently.
