# Learnings log — create-agent-harness

Append-only. Each entry records the date, what was learned, and the evidence. Promote anything that changes the procedure into SKILL.md; this file records why a decision was made rather than duplicating the procedure.

## 2026-08-16 — Harness validated end-to-end; missing skill loads were a trace bug

- **Deferred skill loading works as designed** through an OpenAI-compatible endpoint, including description-based activation: with the skill never named in the prompt, the model called `load_capability` first and received the complete SKILL.md body. This held across named, unmentioned, and explicit prompt variants.
- **The false bug:** early validation filtered message parts by the exact class name `ToolCallPart`. pydantic-ai surfaces skill loads as typed subclasses, so the filter silently dropped them. Wire-level traces showed the capability catalogue in the system prompt and `load_capability` in the tool calls. Filter with `isinstance`, and use a fact available only in the skill body as a cheap ground-truth probe.
- **Marketplace skills run unmodified** when their plugin-level dependencies are copied with them. If a skill resolves paths outside its own directory, preserve that surrounding layout.
- **A one-sentence run-mode preamble** was sufficient to adapt an interactive skill to a headless run. The skill itself did not need rewriting.
- Model observations: a smaller model completed the workflow; a larger reasoning model used cleaner tool ordering and handled sensitive fields more deliberately.

## 2026-08-16 — Why a Python-native harness fits scheduled Python workloads

- **Claude-oriented SDKs:** skills can work headlessly, but an endpoint that only implements OpenAI chat completions may require a protocol proxy and extra runtime bootstrap.
- **Node-based harnesses:** portable and capable, but add a subprocess and runtime boundary when the scheduled environment is already Python-native.
- **Serving-oriented agent frameworks:** useful for deployed online agents, but often heavier than a scheduled job that needs a bounded agent loop.
- Decisive property: a Python-native harness can call in-process data and platform APIs directly while keeping skills portable through the agentskills.io SKILL.md standard.

## 2026-08-15 — Backend facts the harness relies on

- OpenAI-compatible endpoints can support full tool calling, but model availability, authentication, and exact base paths are provider-specific and must be verified against the selected backend.
- Databricks Foundation Model APIs are an OpenAI-compatible option. Local runs can use a CLI OAuth token; scheduled jobs can use an execution-context token where supported.
- Scheduled environments should use narrow tools and explicit dependency installation. Upload the complete `skills/` tree beside the job artifact so deferred loading can find it.
