# Repository instructions for agents

- Marketplace metadata lives in `.claude-plugin/marketplace.json`; each plugin lives under `plugins/<plugin>/` with its manifest in `.claude-plugin/plugin.json` and skills under `skills/<skill>/`.
- Run `scripts/validate.sh` before preparing any pull request.
- Keep all content suitable for a public EthicalML repository. Never include private organization names, internal hostnames, workspace identifiers, access tokens, or other non-public references.
- Do not hard-wrap Markdown prose.
- Use a sober, professional tone with essentially no emojis.
- Keep changes simple and avoid unnecessary dependencies or abstractions.
