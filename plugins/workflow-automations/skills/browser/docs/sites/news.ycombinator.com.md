# news.ycombinator.com

Last verified: 2026-09-26

## Prefer instead

- Hacker News has two public, unauthenticated APIs; use them for anything that does not need the user's own account view.
  - Firebase, for live lists and items: `curl -s https://hacker-news.firebaseio.com/v0/topstories.json` returns story ids; `/v0/item/<id>.json` returns one story or comment.
  - Algolia, for search: `curl -s 'https://hn.algolia.com/api/v1/search?query=<terms>&tags=story'`.
