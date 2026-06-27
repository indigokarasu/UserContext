# Data Sources

This skill consumes *capability roles*, not fixed tools. Each field draws from one
or more roles; each role resolves to whatever concrete tool a given setup exposes,
discovered at runtime. Any role may be absent — the skill degrades, it does not
abort. Read alongside `mood-inference.md`.

## Roles → fields

| Field | Role(s) | What the role provides | If the role is absent |
|-------|---------|------------------------|------------------------|
| Day bullets | CALENDAR | Per-day events: title, time, location | `No scheduled events` (empty) / `No available calendar data` (error) / `No calendar source` (role absent). Never fabricate. |
| Mood: tone | SESSIONS | Interaction tone, topics, frustration, playfulness | No tone dimension; fall back to EMAIL, else `quiet (low signal)`. |
| Mood: outcomes | EMAIL | Rejections, offers, confirmations, deadlines, bills | No outcome dimension. |
| Location | CALENDAR + MEMORY | Current city, active travel | `unknown`. Do not assume home base. |
| Standing context | MEMORY | Active travel, ongoing situations (for interpretation only) | Skip; do not block. |
| Trajectory | (USER.md itself) | Yesterday's mood + location for continuity | First run: skip the comparison. |

## Discovery (Step 0)

At the start of each run, enumerate the tools available in the current setup and
map them to roles. Examples of how a role may be filled, by setup:

- **CALENDAR:** a google-workspace calendar tool, a CalDAV bridge, an MCP calendar
  server, or nothing.
- **SESSIONS:** `session_search` or any conversation-history search.
- **EMAIL:** a google-workspace gmail tool, an IMAP bridge, an MCP mail server, or
  nothing.
- **MEMORY:** a `memory` search tool, a context engine such as chronicle, a notes
  store, or nothing.

Confirm a tool exists before calling it. Do not assume a tool name from one setup
is present in another. If a context engine (e.g. chronicle) is installed but
running in a degraded/fallback mode where its query tool does not resolve, treat
MEMORY as absent for that run rather than erroring.

## Degradation principle

Calendar is the *preferred* backbone for day bullets, but it is not required. The
run produces a valid snapshot from whatever is present:

- Rich setup (all four roles): full snapshot.
- Sessions only: empty/absent day bullets, mood from session tone, location `unknown`.
- Nothing available: minimal honest snapshot (mood `unknown`, `No available data`).

An honest thin snapshot always beats a fabricated rich one. The run must never
abort because a source was empty or a role was absent.
