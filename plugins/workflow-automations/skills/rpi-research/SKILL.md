---
name: rpi-research
description: Research an RPI project through an approved scope, parallel investigations, retained references, findings, and optional spikes. Use after new-project and before rpi-adrs.
---

# Research an RPI project

Work only inside the selected `adr/<NNN>-<name>/`. The files are the workflow state. Keep documents short and plain; scale the number of research areas to the change.

## 1. Resume from the files

Read `adrs/000-initial-request.md`, then inspect `research/` and relevant repository code. Summarize what exists and offer the next unfinished step. If the user does not choose it, stop. If the user has just invoked this skill and the stage has no files yet, that invocation is the choice: proceed directly to the next step without asking again.

Treat a gate as approved only when its file says `Status: approved`. Gates run in the main session, never in a subagent.

## 2. Propose the research scope

Identify the few questions that materially reduce uncertainty. Prefer external evidence for ecosystem behavior, standards, and prior art, with targeted internal codebase research for integration constraints.

Write `research/proposed-research.md` with `Status: proposed`. For each area, state the question, why it matters, likely sources, and intended finding file. If multiple paths are viable, propose parallel spikes that exercise them instead of assuming one works.

Commit this gate document alone with a comprehensive conventional commit. Present it to the user for approval or edits and stop.

## 3. Record approval

After explicit approval in the main session, change the gate to `Status: approved` and commit that change. Do not start investigations before approval.

## 4. Run the investigations

Fan approved independent areas out to parallel subagents. Give each a bounded question and exact output paths; keep gate decisions in the main session. A small effort may use one investigation and one findings document.

For area `<n>`, write:

- `research/research-findings-<n>-<name>.md`: distilled evidence, implications, uncertainties, and recommendations that remain useful after research;
- `research/research-ref-<n>-<m>-<name>.md`: source metadata and the full text that may lawfully be retained, one file per source or captured artifact. Clearly distinguish quotation from analysis.

Review every landed document for relevance, accuracy, plain language, and sensitive content. Commit each document separately with a comprehensive conventional commit as it lands. If research reveals a real fork, propose and run approved parallel spikes, document their setup and observed results, and do not choose a path without evidence.

## 5. Stop at the handover

Present the approved `proposed-research.md`, the findings and references produced, spike results, remaining uncertainties, and commits. State that research is complete, offer to start `rpi-adrs`, and stop. Never begin ADR work silently.
