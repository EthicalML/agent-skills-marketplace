# Site notes — index and admission bar

Site notes make extraction cheaper on sites where a model would otherwise waste turns. They are an index of hard-won facts, not a scraping library: small, durable, and only what a run could not cheaply discover. `pwb open` finds the right file by domain on its own, so nothing here needs to be read during a normal run. Read this file only when adding to or correcting a note.

## Sites

| Site | What its note covers |
|---|---|
| [github.com](./sites/github.com.md) | Prefer `gh`; the notifications inbox has an API |
| [linear.app](./sites/linear.app.md) | Content renders after load; the stable URL routes |
| [calendar.google.com](./sites/calendar.google.com.md) | Prefer a Calendar API integration; events live in button labels; the day URL |
| [news.ycombinator.com](./sites/news.ycombinator.com.md) | Prefer the public APIs |

## Admission bar

A line goes into a site note only when **both** tests pass:

1. **Not cheap to rediscover.** If one `pwb text`, `pwb find` or `pwb snapshot` on the page would show it, it stays out. The model reads pages well; the note is for what costs retries.
2. **Durable.** It describes how the site behaves, its URL routes, its accessible names, or a better route (API, CLI, skill) — things that survive a front-end redesign.

Always out, whatever it saved on one run:

- CSS classes, element ids, DOM paths, element refs (`e21`), layout positions, or any `eval` selector. These change with every redesign and look authoritative until they silently fail.
- Anything not seen on a live run. Nothing goes in from memory.
- Anything true of every site (waiting for late rendering, snapshot size, safety). That belongs in `SKILL.md` or `pwb.py`, not in a site note.
- One-off results: what a page said today is a result, not a learning.

A site with nothing that passes gets no file. A single *Prefer instead* line is a complete, valid note.

## Note schema

`docs/sites/<domain>.md`, named by the host without `www.` (`calendar.google.com.md`, not `google.com.md`, when the app lives on a subdomain). ≤60 lines; over that, the note has stopped being a note — cut it. In this order, leaving out empty sections:

1. `# <domain>` and a `Last verified: YYYY-MM-DD` line.
2. `## Prefer instead` — the API, CLI or skill that answers most questions better, with the one command that shows it works.
3. `## Durable facts` — URL routes, rendering behaviour, what the accessible names contain.
4. `## Traps` — what went wrong on a live run, and what to do instead.

## Keeping notes true

- When a note is wrong on a live run, fix or delete the line and update `Last verified`. A wrong note is worse than no note.
- When a note has not been verified for about six months, re-check it on the next run that uses it before relying on it.
- Tell the user what you added or removed; notes ship with the plugin, so changes go through a pull request on this repository like any other edit.
