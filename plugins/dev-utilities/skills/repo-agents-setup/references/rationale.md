# Rationale & research — SSOT-in-.github layout (verified 2026-08-15)

Read this only when the user asks for the reasoning behind the layout.

## Who reads what (doc-verified)

- **Claude Code** reads `CLAUDE.md` only — it does NOT auto-load `AGENTS.md` (no setting/env var enables it; nested AGENTS.md not discovered either). Docs quote: "Claude Code reads CLAUDE.md, not AGENTS.md. If your repository already uses AGENTS.md for other coding agents, create a CLAUDE.md that imports it." A **symlinked CLAUDE.md is officially documented**: `ln -s AGENTS.md CLAUDE.md` (any target works; on native non-WSL2 Windows use the `@file` import instead). Source: https://code.claude.com/docs/en/memory.md
- **Claude Code glob scoping**: `.claude/rules/*.md` with `paths:` list frontmatter is the only glob mechanism. Lazy-loaded when Claude touches matching files; brace expansion supported; rules without `paths:` load at startup. `@path` imports are documented for CLAUDE.md only — NOT for rules files (that's why rules are symlinks, not import stubs).
- **GitHub Copilot**: reads `.github/copilot-instructions.md` (all surfaces), `.github/instructions/*.instructions.md` with `applyTo:` glob frontmatter (path-scoped), and — coding agent only — `AGENTS.md` (root + nested), `CLAUDE.md`, `GEMINI.md`. Sources: https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot , https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/
- **Codex / Cursor / Gemini CLI etc.**: `AGENTS.md` is the emerging cross-harness standard for the global file. No cross-harness standard exists for glob-scoped instructions.

## Why .github is the SSOT (symlink direction)

Git stores a symlink as a blob whose content is the target path string. Anything reading blobs via the Git API (GitHub server-side features, notably Copilot code review) must explicitly resolve symlinks — and whether it does is UNDOCUMENTED (open question: https://github.com/github/awesome-copilot/discussions/456 ; VS Code bug when copilot-instructions.md is a symlink: https://github.com/microsoft/vscode/issues/265063 ). Checkout-based harnesses (Claude Code, coding agents, CLIs, IDEs on mac/linux) resolve symlinks via the filesystem, guaranteed.

So: put **real files where the fragile/undocumented readers look** (`.github/…`), and **symlinks where support is documented or filesystem-guaranteed** (CLAUDE.md, AGENTS.md, `.claude/rules/*`).

## Dual frontmatter

One shared file body needs both keys because Copilot reads `applyTo:` (single glob string, `{a,b}` braces for multi-path) and Claude reads `paths:` (YAML list). Each harness ignores the other's key — standard frontmatter behavior, not vendor-documented, but verified in practice. Keep the globs identical in both keys.

## FAQ

**Why not AGENTS.md as the default/SSOT?** AGENTS.md is the broadest *global-file* standard (Codex, Cursor, Gemini CLI, Copilot coding agent), but two facts disqualify it as the SSOT here: (1) Claude Code does not read it at all — it would still need a CLAUDE.md symlink/import, so AGENTS.md-as-SSOT buys no simplification; (2) the standard has no glob-scoped companion, while both Copilot (`applyTo`) and Claude (`paths`) key their path-scoped mechanisms off files that live elsewhere. Since `.github/copilot-instructions.md` + `.github/instructions/` are the only locations read by the harnesses that *cannot* be assumed to resolve symlinks (GitHub server-side), the real files must live there anyway — making `.github` the SSOT and AGENTS.md the symlink is the only direction that works for every reader.

**Why not CLAUDE.md as the SSOT?** Symmetric argument: Copilot's server-side features read `.github/copilot-instructions.md` via the Git API where symlink resolution is undocumented, while Claude Code always works on a real checkout and officially documents reading a *symlinked* CLAUDE.md. Put the real file where the fragile reader looks.

**What does a committed symlink actually look like?** Git stores it as mode `120000` with the target path as the blob content. On the GitHub web UI (and to API blob readers) it therefore *displays* as a one-line path — that is expected, not a broken file. On `git clone`/checkout on macOS/Linux it materializes as a real filesystem symlink (`core.symlinks=true` is the default), so every checkout-based harness reads the target content transparently. Verify with `git ls-files -s CLAUDE.md` → `120000 ...`.

**Gitignore pitfall:** many repos gitignore `CLAUDE.md` (it's often local-only). That makes `git add -A` skip the new symlink *silently* — the layout then ships without its Claude entry point. Always `git check-ignore -v` the symlink names and remove matching ignore rules.

**Reference convention:** with real file + symlinks coexisting, prose references get ambiguous ("read CLAUDE.md" vs "read copilot-instructions.md"). Settle on always referencing the real `.github` paths; symlink names appear only when describing the layout.

**Windows contributors?** Only relevant for native (non-WSL2) Windows checkouts, where symlinks need Developer Mode/admin — there, fall back to a real CLAUDE.md containing just `@.github/copilot-instructions.md`. WSL2 handles symlinks like Linux; no change needed.

## Rejected alternatives

- **AGENTS.md as SSOT / per-directory AGENTS.md for Claude**: Claude doesn't read AGENTS.md at all; nested AGENTS.md gives only directory (not glob) scoping and only for some harnesses.
- **`.claude/rules` stubs that `@`-import the .github files**: imports are not documented for rules files.
- **Duplicated content kept in sync**: drift risk, no upside over symlinks for checkout-based readers.
