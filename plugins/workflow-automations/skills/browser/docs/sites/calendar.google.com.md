# calendar.google.com

Last verified: 2026-09-26

## Prefer instead

- A Google Calendar API integration (an MCP server, CLI or skill), when available, reads and changes Calendar with attendees, RSVPs and rooms as structured data. Use the browser only when none is installed or the user asks for what the web view shows.

## Durable facts

- A given day opens directly at `https://calendar.google.com/calendar/u/0/r/day/YYYY/M/D`, for example `.../r/day/2026/9/28`.
- Each event is a button whose accessible name holds the whole event: `"<start> to <end>, <title>, <organiser or owner>, <RSVP status>, <location or No location>, <date>"`. Tasks read `"task: <title>, Not completed, <date>, <time>"`. So `pwb labels "\d(am|pm) to "` returns the day's agenda without a snapshot.

## Traps

- The page text is mostly the month grid and navigation; `pwb text` is the wrong rung here. Go to `pwb labels`.
- A weekend day often has no events, so an empty result is not a failure. Check the date in the page title before retrying.
