# Data Sources

What each field draws from, the tool that actually exists on this box, and how
to degrade when a source is empty or down. Read alongside `mood-inference.md`.

| Field | Tool (verified on this box) | Provides | If empty / fails |
|-------|------------------------------|----------|-------------------|
| Day bullets | google-workspace calendar (`get_events`/`list_events`), one pull per day | Yesterday/today/tomorrow events: title, time, location | `No scheduled events` (empty) or `No available calendar data` (error). Never fabricate. |
| Mood: tone | `session_search` (limit 10) | Interaction tone, topics, frustration, playfulness | No tone dimension; fall back to email, else `quiet (low signal)`. |
| Mood: outcomes | google-workspace gmail search | Rejections, offers, confirmations, deadlines, bills | No outcome dimension. |
| Location | calendar geography + `memory` search | Current city, active travel | `unknown`. Do not assume home base. |
| Standing context | `memory` search | Active travel, ongoing situations (interpretation only) | Skip; do not block. |
| Trajectory | read USER.md `## Daily Context` | Yesterday's mood + location for continuity | First run: skip the comparison. |

## Dead / unavailable here — do NOT call

- `chronicle_ask_about` — chronicle runs in fallback on this box; the tool does
  not resolve. The previous skill version called it as a primary source, so it
  was silently a no-op. Use `memory` search for standing context instead.

## Degradation principle

Every source is optional except the calendar backbone. A thin run still produces
a valid snapshot: real events where the calendar had them, `quiet (low signal)`
for mood, `unknown` for location. The run must never abort because a source was
empty. An honest thin snapshot beats a fabricated rich one.
