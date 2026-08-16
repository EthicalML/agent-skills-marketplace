# Installation runbook

This runbook is addressed to the AI assistant carrying out an installation. Confirm the selected runtime and plugins, execute only the relevant commands, and report each result clearly.

## 0. Check runtime prerequisites

Require `git` and `gh` for the guided clone and repository workflow. Additional runtimes are plugin-specific:

- Install Node.js 20 or later and Playwright only when `site-capture` is selected; its `capture.mjs` script needs them.
- Install Python 3 and pip only when the `agent-harness` template will actually be run.
- `dev-utilities` has no additional runtime dependency.

Do not print secrets. Phase 1 has no secrets to collect: none of the plugins requires an access token or MCP server to install.

## 1. Choose plugins

Default to all three plugins unless the user narrows the selection:

- `dev-utilities`
- `site-capture`
- `agent-harness`

State plainly that installation itself needs no tokens and no MCP servers.

## 2. Clone or update the marketplace

Use the runtime-neutral location `~/.config/agent-skills/marketplace`:

```bash
mkdir -p ~/.config/agent-skills
gh repo clone EthicalML/agent-skills-marketplace ~/.config/agent-skills/marketplace
```

If the clone already exists, update it without rewriting local work:

```bash
git -C ~/.config/agent-skills/marketplace pull --ff-only
```

## 3. Register and install

For Claude Code, run these slash commands in Claude Code:

```text
/plugin marketplace add EthicalML/agent-skills-marketplace
/plugin install dev-utilities@agent-skills-marketplace
/plugin install site-capture@agent-skills-marketplace
/plugin install agent-harness@agent-skills-marketplace
```

For Copilot CLI, run:

```bash
copilot plugin marketplace add EthicalML/agent-skills-marketplace
copilot plugin install dev-utilities@agent-skills-marketplace
copilot plugin install site-capture@agent-skills-marketplace
copilot plugin install agent-harness@agent-skills-marketplace
```

Run only the install commands for the selected plugins.

## 4. Confirm installation

Start a new session and confirm that the selected skills appear in the runtime's available skills. Trigger one with a small representative request if practical.

## 5. Add plugins and apply updates

For a later plugin, refresh marketplace metadata, install the plugin, and start a new session. For an existing plugin, pull the marketplace clone, refresh marketplace metadata, run the runtime's plugin update command, then start a new session. Where supported, `/reload-plugins --force` can replace the new-session step.

Use `scripts/check-plugin-freshness.sh <plugin-name> [installed-plugin-dir]` from the clone when a quick source-versus-installed check is useful.

## Failure handling

Stop at the first failed prerequisite or command, preserve the exact non-secret error output, and report which runtime, plugin, and step failed. Do not retry authentication by requesting or printing credentials; installation requires none. If a command is unavailable, confirm the runtime version and its plugin support before changing the repository.
