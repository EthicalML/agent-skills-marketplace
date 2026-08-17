# The Institute's Agent Skills Marketplace

[![Validate](https://github.com/EthicalML/agent-skills-marketplace/actions/workflows/validate.yml/badge.svg)](https://github.com/EthicalML/agent-skills-marketplace/actions/workflows/validate.yml)

This repository is an open-source marketplace of portable agent skills and plugins maintained by [The Institute for Ethical AI & Machine Learning](https://ethical.institute). Its plugins install into both Claude Code and Copilot CLI and use the open SKILL.md convention.

## Catalogue

| Plugin | Skills | Description |
| --- | --- | --- |
| `dev-utilities` | `writing-skills`, `writing-agents-md`, `explain-code-walkthrough`, `standardize-agent-instructions` | Author reliable skills, keep agent instruction files short and followable, explain code changes, and align instruction files across agent tools. |
| `site-capture` | `site-capture` | Record scripted website walkthroughs as video or GIF. |
| `agent-harness` | `create-agent-harness` | Build a skill-driven Python agent against an OpenAI-compatible endpoint. |

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

Replace `<plugin>` with `dev-utilities`, `site-capture`, or `agent-harness`. INSTALL.md also covers follow-up installs, updates, and breaking-change recovery.

## Contributing

Contributions are welcome through pull requests. Read [CONTRIBUTING.md](CONTRIBUTING.md) and run `scripts/validate.sh` before submitting a change.

## License

This marketplace is available under the [MIT License](LICENSE).
