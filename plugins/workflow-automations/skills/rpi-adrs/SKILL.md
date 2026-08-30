---
name: rpi-adrs
description: Scope and create RPI architecture decision records through explicit user decision walks. Use after rpi-research and before rpi-plan.
---

# Create RPI ADRs

Work only inside the selected `adr/<NNN>-<name>/`. The files are the workflow state. Keep the design proportionate: prefer one short ADR unless the change has genuinely separable large parts.

## 1. Resume from the files

Read the initial request, approved research gate, findings, existing ADR files, and relevant code. Summarize the current position and offer the next unfinished step. If the user does not choose it, stop. If the user has just invoked this skill and the stage has no files yet, that invocation is the choice: proceed directly to the next step without asking again.

Treat `adrs/proposed-adrs.md` as approved only when it says `Status: approved`. All gates and decision walks run in the main session, never in subagents.

## 2. Propose ADR scope only

Write `adrs/proposed-adrs.md` with `Status: proposed`. List which ADRs will exist, what each covers, and the decisions each maps. Do not include options, tradeoffs, recommendations, or decisions in this gate document.

If several approaches need evidence, propose parallel spikes before the decision walk and document their results. Do not assume a path.

Commit the scope document alone with a comprehensive conventional commit. Present it for approval or edits and stop.

## 3. Record approval

After explicit approval in the main session, change the gate to `Status: approved` and commit that change. Do not collapse scope approval and decision-making into one review.

## 4. Walk decisions one by one

For each mapped decision, in order:

1. Present the decision and the evidence that constrains it.
2. Present every viable option with concrete pros and cons.
3. Recommend one option and explain why.
4. Ask the user to accept it or override it, then stop until they decide.
5. Record the chosen option and its tradeoffs in the ADR before moving to the next decision.

Never decide several items in a batch. If the evidence is insufficient, return to an approved spike instead of guessing.

## 5. Finish each ADR

Write each approved record as `adrs/adr_<NNNN>_<slug>.md`. Show the intended API, SDK, CLI, configuration, or user workflow with examples before explaining its internals. State expected behavior, decisions, alternatives and tradeoffs, consequences, and caveats.

Create or update `adrs/usage-cheatsheet.md` with only the short commands or examples users need. Commit each ADR and the cheatsheet separately with comprehensive conventional commits as they land.

## 6. Stop at the handover

Present the approved scope gate, completed ADRs, and a caveats summary of anything that could be misread. Include the cheatsheet and commits. State that design is complete, offer to start `rpi-plan`, and stop. Never begin planning silently.
