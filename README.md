# The Institute's Agent Skills Marketplace

[![Validate](https://github.com/EthicalML/agent-skills-marketplace/actions/workflows/validate.yml/badge.svg)](https://github.com/EthicalML/agent-skills-marketplace/actions/workflows/validate.yml)

This repository is an open-source marketplace of portable agent skills and plugins maintained by [The Institute for Ethical AI & Machine Learning](https://ethical.institute). Its plugins install into both Claude Code and Copilot CLI and use the open SKILL.md convention.

## Catalogue

| Plugin | Skills | Description |
| --- | --- | --- |
| `dev-utilities` | `writing-skills`, `writing-agents-md`, `explain-code-walkthrough`, `standardize-agent-instructions` | Author reliable skills, keep agent instruction files short and followable, explain code changes, and align instruction files across agent tools. |
| `workflow-automations` | `site-capture`, `create-agent-harness`, `create-streamlit-app`, `verify-streamlit-app`, `new-project`, `rpi-research`, `rpi-adrs`, `rpi-plan`, `rpi-implement` | Run research-to-implementation projects with explicit gates, record scripted website walkthroughs, build skill-driven Python agents, and scaffold local Streamlit data apps with browser verification. |
| `codebase-automations` | `dependabot-fix`, `dependabot-fix-all`, `release-repo` | Diagnose and safely merge Dependabot pull requests, or assess release conformance and run profile-driven releases with artifact validation. |

## The RPI workflow

The `workflow-automations` plugin packages a research-to-implementation (RPI) workflow as five stage skills. The happy path:

1. `new-project <scope>` — records the request under `adr/<NNN>-<name>/` in your repo.
2. `rpi-research` — propose research areas, approve the gate, findings land from parallel investigations.
3. `rpi-adrs` — approve the ADR scope, then decide each design decision one by one from options with tradeoffs and a recommendation.
4. `rpi-plan` — approve a minimal plan of reviewable PRs with manual-first verification.
5. `rpi-implement` — PR by PR with your review between each, verification run eagerly, learnings captured as work progresses.

The files are the state: resume anytime in a fresh session and the skills work out the next step from what exists under `adr/<NNN>-<name>/`.

## Installation

The standard way to install is to point your AI assistant (Claude Code or Copilot CLI) at [INSTALL.md](INSTALL.md) — it is an assistant-driven install gate that checks prerequisites, registers the marketplace, and installs the selected plugins:

```text
Follow https://raw.githubusercontent.com/EthicalML/agent-skills-marketplace/master/INSTALL.md to install this marketplace
```

For a manual install, the underlying commands are:

```text
/plugin marketplace add EthicalML/agent-skills-marketplace          # Claude Code
/plugin install <plugin>@agent-skills-marketplace
```

```bash
copilot plugin marketplace add EthicalML/agent-skills-marketplace   # Copilot CLI
copilot plugin install <plugin>@agent-skills-marketplace
```

Replace `<plugin>` with `dev-utilities`, `workflow-automations`, or `codebase-automations`. INSTALL.md also covers follow-up installs, updates, and breaking-change recovery.

## Contributing

Contributions are welcome through pull requests. Read [CONTRIBUTING.md](CONTRIBUTING.md) and run `scripts/validate.sh` before submitting a change.

## License

This marketplace is available under the [Apache License 2.0](LICENSE).
