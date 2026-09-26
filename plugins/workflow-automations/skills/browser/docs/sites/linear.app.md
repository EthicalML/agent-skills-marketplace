# linear.app

Last verified: 2026-09-26

## Prefer instead

- The Linear MCP server, when installed, answer issue, project and inbox questions without the browser.

## Durable facts

- Routes are `https://linear.app/<workspace>/...`. Opening `https://linear.app/` redirects into the user's workspace, so read the workspace slug from the final URL instead of guessing it.
- Useful routes: `/<workspace>/inbox`, `/<workspace>/my-issues/assigned` (also `created`, `subscribed`, `activity`).
- Linear is a client-rendered app: the page title and sidebar arrive first, and the main list arrives a few seconds later behind a "Loading…" placeholder.

## Traps

- A read straight after navigation returns only the sidebar and "Loading…", and generic page-text tools report the page as empty. Use `pwb text main` after `pwb open` has settled; if it still shows "Loading…", run `pwb wait` and read once more.
- An empty *My issues* page says "No issues assigned to you"; that is an answer, not a rendering failure.
