# EthicalML Agent Skills Marketplace

[![Validate](https://github.com/EthicalML/agent-skills-marketplace/actions/workflows/validate.yml/badge.svg)](https://github.com/EthicalML/agent-skills-marketplace/actions/workflows/validate.yml)

This repository is an open-source marketplace of portable agent skills and plugins maintained by [The Institute for Ethical AI & Machine Learning](https://ethical.institute). Its plugins install into both Claude Code and Copilot CLI and use the open SKILL.md convention.

## Catalogue

| Plugin | Skills | Description |
| --- | --- | --- |
| `dev-utilities` | `writing-skills`, `explain-code-walkthrough`, `standardize-agent-instructions` | Author reliable skills, explain code changes, and align instruction files across agent tools. |
| `site-capture` | `site-capture` | Record scripted website walkthroughs as video or GIF. |
| `agent-harness` | `create-agent-harness` | Build a skill-driven Python agent against an OpenAI-compatible endpoint. |

## Quickstart

Claude Code:

```text
/plugin marketplace add EthicalML/agent-skills-marketplace
/plugin install <plugin>@agent-skills-marketplace
```

Copilot CLI:

```bash
copilot plugin marketplace add EthicalML/agent-skills-marketplace
copilot plugin install <plugin>@agent-skills-marketplace
```

Replace `<plugin>` with `dev-utilities`, `site-capture`, or `agent-harness`. See [INSTALL.md](INSTALL.md) for the guided installation and update flow.

## Contributing

Contributions are welcome through pull requests. Read [CONTRIBUTING.md](CONTRIBUTING.md) and run `scripts/validate.sh` before submitting a change.

## License

This marketplace is available under the [MIT License](LICENSE).
