# github.com

Last verified: 2026-09-26

## Prefer instead

- `gh` covers almost everything: issues, PRs, checks, releases, search. `gh api notifications` returns the notifications inbox as JSON, which the web page otherwise only shows as a 45 KB snapshot.
- With several `gh` accounts logged in, the API answers for the active one. For another account, prefix the command with `GH_TOKEN=$(gh auth token --user <login>)`.

## Durable facts

- The browser is only worth it for what the API does not expose, such as the notification inbox exactly as the user has it filtered on the web.
