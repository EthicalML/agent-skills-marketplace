---
name: writing-skills
description: Write or revise a SKILL.md so it reads as executable instructions rather than prose. Use whenever asked to create a new skill, restructure an existing one, or turn documentation into a workflow. Applies to plugin skills, personal skills in ~/.claude/skills, and any file that tells an agent how to do a task.
---

# Writing a skill

A skill is a procedure an agent follows. When writing it, write it as if you were going to write code, but in English. Make sure you are exact and deterministic where the answer is fixed, and leave room for judgement where it is not. Use both scripts and judgement based steps, where they make sense.

The below are (ironically) not steps, but principles. Follow these closely when creating or revising a skill.

## 0. Keep it simple

The most important step. Radical simplicity. Do not overcomplicate.

Simple does not mean incomplete. It means simple.

Making things complicated is easy. Finding simple solutions for complex problems (or even simple problems) is hard. And this is what we need to do.

The default skills created are usually overengineered. In this case the most important principle is, don't overengineer, don't overcomplicate. Keep it simple, and add complexity as it's required, not earlier, but also not later.

## 1. Write the steps

The skill should read like a deterministic recipe. If it's not in a step, other than the outline, it likely shouldn't be there - or should be inside a step.

Leverage optional steps; especially on progressive disclosure, and particularly when these read files, documentation that is only conditionally relevant. No files linked 'for reference' either they are relevant or not.

Handle errors next to the thing that fails: "If the error says an asset cannot be cropped, pick a different asset. Do not widen the crop."

Do not put errors in a troubleshooting section at the end. Nobody reads it until they are already lost.

## 2. Use scripts or judgement as required

If a sequence of steps resemble a script, write a script instead: e.g. authenticate, call the API, validate, build.

When judgement is necessary, leverage the agent. Let the agent decide when the step needs reading a source, choosing between valid options, writing content, or judging whether the output is good. Give it the rule it must follow, not the answer.

Sometimes too much is delegated into a script, which loses the point of being a skill (write a script instead!); other times too many tokens are used and too much time spent for something that could be a simple script. Find the sweet spot.

## 3. Keep in SKILL.md only what every run needs

Context is king, and we need to reverse context-engineer to identify the optimal context for this job.

SKILL.md loads every time. It holds the steps, their conditions, and their commands.

Move something to another file only if some runs need it and others do not, or if it's needed only based on specific conditions. Then read it from the step that needs it.

For branching into different workflow steps, consider separating into a different workflow-<file>.md if it's extensive enough and has enough references; however keep it simple if not extensive.

For references into `docs.md` or other resources, use progressive disclosure; sometimes this has to be read from the outset, other times only after a conditional.

Also, don't restate what a type or schema already says; if it needs restating make it more clear in the source of truth or in the reference to it.

## 4. Verification as a step

Make sure that also proportionate verification is in place.

Where relevant this can involve scripts and utilities that help ensure the input used is correct.

However it could also be gating steps such as ensuring that the requirements are in place.

Do not overengineer on verification unless it's needed, as this can add significant overhead; leverage progressive disclosure where possible.

## 5. Verification of the SKILL.md itself

You can verify the quality of the skill itself by running a blind subagent with it; do not give instructions like "judge this skill.md", but ask it to execute an action with it.

Then review the token consumption, the time spent, and the transcript to understand where it got stuck, where it re-read files too many times, and where things fell apart.

A handful of these runs improve the quality of the skill more than any agentic passes could. Especially when running them in cheaper sonnet models.

## 6. Add a human feedback loop when useful

Optionally add a final step that tells the agent to:

1. Retrospect on retries, manual fixes, unexpected failures, and reusable knowledge from the run.
2. Send fixes of a couple of lines upstream as a pull request.
3. Put anything bigger into one issue per session, with runtime context, the exact command, the error, and reproduction steps.

Recommend this for skills whose users cannot judge defects themselves. It costs a little context on every run, so make it a judgement call for each skill.
