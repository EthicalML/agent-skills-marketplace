# INSTALL.md — guided install gate

> **For the AI assistant reading this file:** follow these steps exactly. This is a *pre-install gate* and the standard way to install from this marketplace. Do not install anything until the prerequisites for a selected plugin pass. Never print or persist secret values (this marketplace currently requires none — say so if asked).
>
> **Runtime:** Steps 3–5 are written for **Copilot CLI**. If you are running under **Claude Code**, do Steps 0–2 and 6–7 the same way, and use the [Claude Code](#claude-code-use-in-place-of-steps-35) section in place of Steps 3–5.

## Path convention

The per-user path in these docs — the marketplace clone — lives under a runtime-neutral home:

- `~/.config/agent-skills/marketplace` — the marketplace clone

Runtime-internal paths (e.g. `~/.copilot/installed-plugins/`, `~/.claude/plugins/cache/`) are written literally and are not affected.

## Step 0 — Runtime prerequisites

Check what is present before anything else:

```sh
command -v git && git --version     # git (Step 1 clone, freshness checks)
command -v gh && gh --version       # gh (clone auth)
```

Plugin-specific runtimes — check only for the plugins in scope:

- `site-capture`: Node.js 20+ (`command -v node && node -v`); the skill guides the Playwright install on first use.
- `agent-harness`: Python 3 with pip (`command -v python3`), needed only when the harness template will actually be run.
- `dev-utilities`: no additional runtime.

If a required runtime is missing, guide the user to install it (or skip that plugin), then continue.

## Step 1 — Ask which plugins to install

Install the **default set** unless the user opts out. Confirm the list with them (they may deselect any), but do not require them to pick from scratch.

**Default set:**

- `dev-utilities` — skill authoring (`writing-skills`), code-change walkthroughs (`explain-code-walkthrough`), and cross-harness instruction-file standardization (`standardize-agent-instructions`)
- `site-capture` — scripted browser capture of a website as video or GIF
- `agent-harness` — build a skill-driven Python agent (`create-agent-harness`) against any OpenAI-compatible endpoint

No plugin in this marketplace requires an access token or an MCP server. There is nothing to create, store, or validate credential-wise — state that plainly and move on.

## Step 2 — Get the marketplace repo (before installing)

Clone the marketplace repo. Follow-up installs and updates (Steps 6–7) operate on this same clone, and the freshness helper runs from it. By convention:

```sh
mkdir -p ~/.config/agent-skills
gh repo clone EthicalML/agent-skills-marketplace ~/.config/agent-skills/marketplace
```

If the clone already exists, make sure it is current before continuing (a stale clone is the most common reason a newly added plugin is invisible at install time):

```sh
git -C ~/.config/agent-skills/marketplace pull --ff-only
```

## Claude Code (use in place of Steps 3–5)

1. Register the marketplace (once):
   ```
   /plugin marketplace add EthicalML/agent-skills-marketplace
   ```
2. Install each selected plugin:
   ```
   /plugin install <plugin>@agent-skills-marketplace
   ```
   The marketplace name (`agent-skills-marketplace`) comes from `.claude-plugin/marketplace.json`.
3. Confirm per Step 5: the skills appear in a new session.

## Step 3 — Register the marketplace (once)

```sh
copilot plugin marketplace add EthicalML/agent-skills-marketplace
```

## Step 4 — Install each selected plugin

```sh
copilot plugin install <plugin>@agent-skills-marketplace
```

Run once per selected plugin.

## Step 5 — Confirm

```sh
copilot plugin list      # installed plugins
```

In a new session, the installed skills should appear in the available-skills list. Trigger one with a small representative request if practical (e.g. ask for a walkthrough of the latest commit to exercise `explain-code-walkthrough`).

## Step 6 — Follow-up install (adding one more plugin later)

When the marketplace is already registered and you only want to add another plugin, do **not** repeat the whole flow — but the marketplace metadata does not refresh itself, so a newly added plugin stays invisible until you refresh it:

1. **Update the source** so the new plugin is visible: `git -C ~/.config/agent-skills/marketplace pull --ff-only` (nothing to pull if the marketplace was registered from the GitHub URL).
2. **Refresh the marketplace metadata** (required — the plugin is "not found" until you do):
   - Claude Code: `claude plugin marketplace update agent-skills-marketplace`
   - Copilot CLI: `copilot plugin marketplace update agent-skills-marketplace`
3. **Install** it (Step 4, or the Claude Code section).
4. **Activate it.** A newly installed plugin loads only in a **new session**, or after `/reload-plugins --force` in the current one — a plain `/reload-plugins` only *stages* it.

## Step 7 — Updating installed plugins (including breaking changes)

Routine updates are safe and should be the first move whenever a skill asks you to refresh:

1. **Update the source** (same as Step 6).
2. **Refresh the marketplace metadata** (same as Step 6).
3. **Update the plugin(s)**: `copilot plugin update <plugin>@agent-skills-marketplace`, or `copilot plugin update --all` (Claude Code: `claude plugin update <plugin>@agent-skills-marketplace`).
4. **Activate**: new session, or `/reload-plugins --force`.

To check quickly whether a refresh is needed at all, run the freshness helper from the clone: `scripts/check-plugin-freshness.sh <plugin-name> [installed-plugin-dir]` — it prints `UP-TO-DATE` or `STALE` lines with the exact remediation.

**If an update fails with an unknown plugin or skill name, do not stop — assume a breaking change (e.g. a plugin rename) and recover:**

1. Refresh the marketplace metadata (above), then read `.claude-plugin/marketplace.json` in the clone to see what the marketplace offers now.
2. Find the migration note: breaking changes are always merged with the `breaking-change` label, and the PR body carries a **Migration** section (what broke, old name → new name, exact commands):
   ```sh
   gh pr list --repo EthicalML/agent-skills-marketplace --label breaking-change --state merged --limit 10
   gh pr view <number> --repo EthicalML/agent-skills-marketplace
   ```
3. Apply the migration: typically uninstall the old name, install the new one, plus whatever extra steps the note lists.
4. Verify with Step 5, then continue with the task that triggered the update.

## Contributing

The runtime install itself only fetches a **read-only cache** (Claude Code: `~/.claude/plugins/cache/`; Copilot CLI: `~/.copilot/installed-plugins/`) — overwritten on every plugin update, so never edit it. To contribute upstream, work in the Step 2 clone and follow [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Failure handling (summary)

- Missing runtime for a plugin → guide the install or skip that plugin, keep going with the others.
- Newly added plugin "not found" on install → refresh the marketplace metadata (Step 6), then retry.
- Installed plugin "not found" on **update** → likely a breaking change (rename/removal); follow the recovery path in Step 7.
- A skill installed but not appearing → confirm you are in a **new session** (or ran `/reload-plugins --force`), then check the installed cache exists for that plugin.
- Never claim a credential is needed — this marketplace requires none; if a tool asks for one, something else is wrong and should be reported, not worked around.
