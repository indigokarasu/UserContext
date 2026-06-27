---
name: ocas-usercontext
description: >
  Maintains a compressed `## Daily Context` block in the owner's USER.md:
  an evidence-grounded snapshot of mood, location, week theme, and
  yesterday/today/tomorrow bullets, inferred from whatever signal sources the
  setup exposes (calendar, session history, email, long-term memory). Use when
  the daily context block needs refreshing, when its scheduled job has failed,
  or when the owner asks for a status snapshot. Keywords: daily context, user
  snapshot, mood inference, USER.md update, personal briefing. NOT for weather,
  long-term planning, or advice.
license: MIT
source: https://github.com/indigokarasu/ocas-usercontext
metadata:
  author: Indigo Karasu (indigokarasu)
  version: 3.0.0
  hermes:
    tags: [context, daily, cron]
    category: infrastructure
includes:
  - references/**
triggers:
  - /usercontext
  - /daily-context
---

# User Daily Context

## Purpose

Keep one block of USER.md — `## Daily Context` — fresh every morning so every
session that day opens with an accurate read of what is happening in the owner's
life. USER.md loads into **every** session, so this block is the highest-leverage
and most-read text the agent maintains. Two failure modes are equally bad:
**stale** (yesterday's events shown as today's) and **fabricated** (a mood or
fact invented from thin signal). This skill optimizes against both.

It is designed to be **portable**: it adapts to whatever signal sources and tools
a given Hermes setup exposes, rather than assuming a fixed toolset. It runs well
in a rich setup (calendar + email + sessions + memory) and degrades honestly in a
bare one (sessions only, or even nothing).

## Honest data model

Be clear about what is *extracted* vs *inferred* — they have different failure
modes and conflating them is this skill's classic defect:

| Field | Kind | Drawn from |
|-------|------|-----------|
| Yesterday/Today/Tomorrow bullets | **Extracted** | Calendar capability. Report what is scheduled; do not editorialize. |
| Location | **Extracted** | Calendar geography + memory of known travel. Default `unknown`. |
| Week theme | **Summarized** | The week's calendar shape in one line. |
| Mood | **Inferred** | Session *tone* and email *outcomes* — NOT the calendar. |

The most common defect in this skill's history is **inferring mood from the
calendar** ("tea reservation" → "anticipation for tea"). A scheduled event is not
a feeling. Mood comes from how the owner *interacted* and what *outcomes* landed.
If session and email signal is thin, the correct mood is `quiet (low signal)`, not
an invention.

## Capabilities (discover, don't assume)

This skill needs four *capability roles*. Which concrete tool fills each role
varies by setup, and any role may be **absent**. At the start of every run,
discover what is available (e.g. list tools / check the toolset) and map them:

| Role | What it provides | Typical tools (setup-dependent) | If absent |
|------|------------------|---------------------------------|-----------|
| **CALENDAR** | Events per day (title, time, location) | google-workspace calendar, CalDAV, an MCP calendar tool | No day bullets from calendar; lean on sessions/memory; bullets may be `No calendar source`. |
| **SESSIONS** | Recent interaction tone & topics | `session_search` or equivalent history search | No tone signal; mood leans on email, else `quiet (low signal)`. |
| **EMAIL** | Recent outcomes (rejections, confirms, deadlines) | google-workspace gmail, IMAP, an MCP mail tool | No outcome signal for mood. |
| **MEMORY** | Standing context (travel, ongoing situations) | `memory` search, a context engine (e.g. chronicle), notes store | Location may be `unknown`; no standing-context interpretation. |

Rules for portability:

- **Probe, then proceed.** Resolve each role to a concrete available tool. Record
  which roles are present. Never call a tool you have not confirmed exists.
- **Every role is optional.** A run with only SESSIONS still produces a valid (if
  sparse) snapshot. A run with nothing produces an honest `unknown` snapshot. The
  run must never abort because a role is missing.
- **Do not hardcode tool names in your reasoning.** Names like `chronicle_ask_about`
  or `mcp_google_workspace_get_events` exist in some setups and not others;
  treat them as candidates for a role, confirmed by discovery, not as givens.

See `references/data-sources.md` for the role→signal mapping and degradation matrix.

## Where things live (resolve at runtime)

Paths are **profile-relative**, never hardcoded to one machine:

- **Profile root:** the active Hermes profile directory. Resolve from
  `$HERMES_HOME` if set; otherwise it is the directory this skill is installed
  under (the parent of `skills/`).
- **Target file:** `<profile>/memories/USER.md`. (Note: under `memories/`, not the
  profile root.) If `memories/USER.md` does not exist, check the profile root for a
  `USER.md`; if neither exists, create `<profile>/memories/USER.md`.
- **Timezone:** resolve the host timezone at runtime (e.g. `timedatectl` / system
  clock). Date math for yesterday/today/tomorrow uses the host's local day, never
  an assumed zone.

## Output format

The `## Daily Context` block, written into USER.md exactly as:

```markdown
## Daily Context

> Refreshed daily by the `ocas-usercontext` job. Do not manually edit; regenerate instead.

### Snapshot (YYYY-MM-DD)
**Mood:** [1-3 evidence-backed dimensions, or `quiet (low signal)`]
**Location:** [city, or `unknown`]
**Week:** [one line, max 10 words]

### Yesterday (YYYY-MM-DD)
- [event, max 12 words]

### Today (YYYY-MM-DD)
- [event, max 12 words]

### Tomorrow (YYYY-MM-DD)
- [event, max 12 words]
```

### Compression rules

- Total block **under 300 words** (configurable; see Configuration). It costs context on every session.
- Bullets: up to 3 per day, **max 12 words each**.
- Mood: 1-3 dimensions, each `[label] about [topic]`; or `quiet (low signal)`.
- Week: one line, max 10 words.
- Empty calendar day → `No scheduled events`. Never fabricate an event.
- No weather, no advice, no system/meta narration, **no em dashes** (chat renderers mangle them; use commas/periods).

## Generation workflow

- [ ] **Step 0 — Resolve environment.** Profile root, USER.md path, host timezone.
      Discover available tools and map them to the CALENDAR / SESSIONS / EMAIL /
      MEMORY roles. Note which roles are present.
- [ ] **Step 1 — Read yesterday's snapshot.** Read the existing `## Daily Context`.
      Note prior mood + location: the trajectory baseline for Step 5. (Absent =
      first run; skip the comparison.)
- [ ] **Step 2 — Build the Signal Ledger.** Gather, do not yet interpret, from each
      present role: calendar (3 day pulls), sessions (broad tone scan), email
      (recent outcomes), memory (active travel / standing situations). Write each
      signal as one line tagged with its role. A thin ledger is fine and honest.
- [ ] **Step 3 — Extract day bullets.** Per day, list calendar events (title + time)
      as bullets. Empty → `No scheduled events`. No editorializing.
- [ ] **Step 4 — Determine location.** City from today's calendar geography or a
      memory travel signal. No signal → `unknown`. Never guess from home base.
- [ ] **Step 5 — Infer mood.** Read `references/mood-inference.md` in full. Build
      1-3 dimensions, **each citing a concrete ledger signal** (session tone or
      email outcome, never the calendar). Apply trajectory vs Step 1: `still` if it
      persists, `now`/`shifted` if changed, drop vanished moods. Thin ledger →
      `quiet (low signal)`.
- [ ] **Step 6 — Write the week theme.** One line, max 10 words, from the week's
      calendar shape (travel / deadline-heavy / meeting-heavy / quiet / project push).
- [ ] **Step 7 — Patch USER.md.** Replace ONLY the `## Daily Context` block (from
      that heading to the next `##` or EOF). Use an exact match; never touch
      identity, preferences, or any other section.
- [ ] **Step 8 — Validate, then act on delivery (do not skip).** Run the
      `references/validation.md` checklist. Then honor the configured `deliver`
      setting (default `local` = silent, write-only). See Configuration.

## Configuration

The skill ships with safe defaults; an installer or owner can override them. On a
Hermes box these live on the scheduled job (see `references/install.md`); the
skill should read intent from the job/config rather than hardcoding it.

| Knob | Default | Meaning |
|------|---------|---------|
| `deliver` | `local` (silent, write-only) | Where the snapshot goes after the patch. `local` = USER.md only. A chat target (e.g. `origin`, `telegram`) also pushes a copy. Most owners want `local`: USER.md already reaches the agent via session load, so a daily chat push is redundant. |
| `schedule` | once daily, morning, host TZ | When the job runs. |
| `word_budget` | 300 | Max words in the block. |
| `weather_skill` | none | If the setup has a dedicated weather/briefing skill (e.g. `ocas-vesper`), this skill still emits no weather; that skill owns it. Purely informational — no hard dependency. |

## Runtime wiring (Hermes cron)

If run by a cron whose prompt is **inlined** (the common Hermes pattern), the cron
does not auto-read this SKILL.md. Then this skill is the **design** source of truth
and the cron prompt is the **runtime** source of truth; a change in one not
mirrored in the other is a silent divergence. When you change the workflow, format,
or config here, mirror the essentials into the cron prompt. See
`references/install.md` for how to instantiate the job on any box, and
`references/constraints.md` for the divergence rationale.

## When NOT to use

- Weather → a dedicated weather/briefing skill if the setup has one.
- Long-term planning / goal tracking → a planning skill.
- Advice or recommendations — this reports state, it does not prescribe.
- "How do I feel about X?" — this infers mood from signals; it does not ask.
- A full briefing with weather and priorities → a briefing skill.

## Gotchas and error handling

| Failure | Response |
|---------|----------|
| A capability role has no available tool | Proceed without it (see degradation matrix); never abort. |
| Calendar pull fails for a day | `No available calendar data` for that day; continue. |
| Session search empty | No tone bullets; mood leans on email, else `quiet (low signal)`. |
| Memory search empty | Location may be `unknown`; do not block. |
| A named tool from another setup doesn't resolve here | Skip it; it is a candidate, not a requirement. |
| Patch can't find `## Daily Context` | First run: append the block after the last `##`. |
| Patch fuzzy-matches wrong section | Read raw USER.md, use an exact `old_string`. |
| USER.md missing | Create `<profile>/memories/USER.md` with the block as first content. |
| Configured delivery fails | Block is already written; log, retry next run. |
| Output exceeds the word budget | Re-compress: bullets to 8 words, mood to 1 dimension, week to 5 words. |
| All sources fail at once | Minimal honest snapshot: mood `unknown`, location `unknown`, `No available data` per day. Still run; never skip. |

## Initialization (first run on a new setup)

1. Resolve the profile root and host timezone (Step 0).
2. Verify / create `<profile>/memories/USER.md`.
3. Add a `## Daily Context` block with a placeholder snapshot.
4. Discover available tools; record which capability roles are present.
5. Register or confirm the scheduled job with the chosen `deliver`, `schedule`,
   and `word_budget` (see `references/install.md`).
6. If the job uses an inlined prompt, ensure it matches this skill's workflow.
7. Log to journal.
