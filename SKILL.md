---
name: ocas-usercontext
description: >
  Generates the compressed `## Daily Context` block in the owner's USER.md:
  an evidence-grounded snapshot of mood, location, week theme, and
  yesterday/today/tomorrow bullets, inferred from calendar, session history,
  and email outcomes. Use when the daily context block needs refreshing, when
  the daily cron has failed, or when the owner asks for a status snapshot.
  Keywords: daily context, user snapshot, mood inference, USER.md update,
  personal briefing. NOT for weather (use ocas-vesper), long-term planning,
  or advice.
license: MIT
source: https://github.com/indigokarasu/ocas-usercontext
metadata:
  author: Indigo Karasu (indigokarasu)
  version: 2.0.0
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

Keep one block of USER.md — `## Daily Context` — fresh every morning so that
every session that day opens with an accurate read of what is happening in the
owner's life. USER.md loads into **every** session, so this block is the
highest-leverage and most-read text the agent maintains. Two failure modes are
equally bad: **stale** (yesterday's events shown as today's) and **fabricated**
(a mood or fact invented from thin signal). This skill optimizes against both.

## Honest data model

Be clear about what is *extracted* vs what is *inferred*, because they have
different failure modes and the previous version conflated them:

| Field | Kind | Source of truth |
|-------|------|-----------------|
| Yesterday/Today/Tomorrow bullets | **Extracted** | Calendar events. Report what is scheduled. Do not editorialize. |
| Location | **Extracted** | Calendar event geography + memory of known travel. Default `unknown`. |
| Week theme | **Summarized** | The week's calendar shape in one line. |
| Mood | **Inferred** | Session *tone* and email *outcomes* — NOT the calendar. See below. |

The single most common defect in this skill's history is **inferring mood from
the calendar** ("tea reservation" → "anticipation for tea"). A reservation is
an event, not a feeling. Mood comes from how the owner *interacted* and what
*outcomes* landed, never from restating the schedule. If session and email
signal is thin, the correct mood is `quiet (low signal)`, not an invented one.

## Output format

Written into `~/.hermes/profiles/indigo/memories/USER.md` as exactly this block:

```markdown
## Daily Context

> Refreshed daily at 7am PT by `ocas-usercontext` cron. Do not manually edit; regenerate instead.

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

- Total block **under 300 words**. It costs context on every session.
- Bullets: up to 3 per day, **max 12 words each**.
- Mood: 1-3 dimensions, each as `[label] about [topic]`; or `quiet (low signal)`.
- Week: one line, max 10 words.
- Empty calendar day → `No scheduled events`. Never fabricate an event.
- No weather, no advice, no system/meta narration, **no em dashes** (Telegram mangles them; use commas/periods).

## Tools on THIS box (verified)

The previous version named tools that do not exist here. Use only these:

| Need | Tool that actually works | Notes |
|------|--------------------------|-------|
| Calendar events | google-workspace calendar tool (`get_events` / `list_events`) | Per-day pulls for yesterday/today/tomorrow. The reliable backbone. |
| Session tone/topics | `session_search` | limit 10, broad first then keyword. Primary mood signal. |
| Email outcomes | google-workspace gmail search | Rejections, confirmations, deadlines. Secondary mood signal. |
| Known travel / standing context | `memory` (search) | Replaces the dead `chronicle_ask_about`. Read-only here. |
| Yesterday's snapshot (trajectory) | read USER.md `## Daily Context` | Already on disk. Enables continuity. |

`chronicle_ask_about` is **not available** on this box (chronicle runs in
fallback). Do not call it. Use `memory` search for standing context, and if it
returns nothing, degrade — do not block the run.

See `references/data-sources.md` for the full mapping and degradation behavior.

## Generation workflow

- [ ] **Step 0 — Read yesterday's snapshot.** Open USER.md, read the existing
      `## Daily Context`. Note prior mood + location. This is the trajectory
      baseline for Step 4. (If absent, this is a first run; skip the comparison.)
- [ ] **Step 1 — Build the Signal Ledger.** Gather, do not yet interpret:
      - Calendar: three pulls (yesterday, today, tomorrow). Record title + time + location.
      - Sessions: `session_search` limit 10, no keyword, for overall tone/topics.
      - Email: search for recent outcomes (rejection/offer/confirm/deadline/bill).
      - Memory: `memory` search for active travel or standing situations.
      Write each signal as one line with its source. Thin ledger is fine and honest.
- [ ] **Step 2 — Extract day bullets.** For each day, list calendar events as
      bullets (title + time). Empty → `No scheduled events`. No editorializing.
- [ ] **Step 3 — Determine location.** City from today's calendar geography or a
      memory travel signal. No signal → `unknown`. Never guess from home base.
- [ ] **Step 4 — Infer mood (the hard part).** Read `references/mood-inference.md`
      in full. Build 1-3 dimensions, **each citing a concrete ledger signal**.
      Mood comes from session tone + email outcomes, never from the calendar.
      Then apply trajectory (Step 0): mark a dimension `still` if it persists from
      yesterday, `now`/`shifted` if it changed. Thin ledger → `quiet (low signal)`.
- [ ] **Step 5 — Write the week theme.** One line, max 10 words, from the week's
      calendar shape (travel / deadline-heavy / meeting-heavy / quiet / project push).
- [ ] **Step 6 — Patch USER.md.** Replace ONLY the `## Daily Context` block (from
      that heading to the next `##` or EOF). Use the `file`/patch tool with an exact
      match; never touch identity, preferences, or any other section.
- [ ] **Step 7 — Validate (do not skip).** Run `references/validation.md` checklist:
      word count < 300, no em dashes, dates correct, mood cites evidence or says
      low-signal, patch landed, other sections untouched. Re-compress if over budget.
- [ ] **Step 8 — Deliver.** Send the snapshot to the owner via Telegram (origin
      channel). If delivery fails, the block is already on disk; log and move on.

## Schedule and runtime wiring

| Job | Schedule | Action |
|-----|----------|--------|
| `daily-user-context` (`53920c89f796`) | `0 7 * * *` (07:00 PT — box is America/Los_Angeles) | Generate + patch USER.md + deliver |

**Critical:** the cron job carries an inlined prompt; it does not auto-read this
SKILL.md. When you change the workflow or format here, you MUST sync the change
into the cron prompt in `~/.hermes/profiles/indigo/cron/jobs.json` (job
`53920c89f796`) or the change will not take effect. The cron prompt is the
runtime source of truth; this skill is the design source of truth. Keep them in
lockstep. See `references/constraints.md` for the divergence rationale.

## Target file

`~/.hermes/profiles/indigo/memories/USER.md` — the `## Daily Context` block only.
The file lives under `memories/`, not at the profile root.

## When NOT to use

- Weather → `ocas-vesper`.
- Long-term planning / goal tracking → `ocas-mentor` / `ocas-tasks`.
- Advice or recommendations — this reports state, it does not prescribe.
- "How do I feel about X?" — this infers mood from signals; it does not ask.
- A full briefing with weather and priorities → `ocas-vesper`.

## Gotchas and error handling

| Failure | Response |
|---------|----------|
| Calendar pull fails for a day | `No available calendar data` for that day; continue. |
| `session_search` empty | No tone bullets; mood leans on email, else `quiet (low signal)`. |
| `memory` search empty | Location may be `unknown`; do not block. |
| `chronicle_ask_about` referenced anywhere | Ignore it; the tool is dead on this box. |
| Patch can't find `## Daily Context` | First run: append the block after the last `##`. |
| Patch fuzzy-matches wrong section | Read raw USER.md, use an exact `old_string`. |
| USER.md missing | Create it with the Daily Context block as first content. |
| Telegram delivery fails | Block is already written; log, retry next run. |
| Output exceeds 300 words | Re-compress: bullets to 8 words, mood to 1 dimension, week to 5 words. |
| All sources fail at once | Minimal honest snapshot: mood `unknown`, location `unknown`, `No available data` per day. Still run; never skip. |

## Initialization (first run)

1. Verify USER.md exists at `~/.hermes/profiles/indigo/memories/USER.md`.
2. Add a `## Daily Context` block with a placeholder snapshot.
3. Confirm cron `53920c89f796` exists (`0 7 * * *`, deliver origin); if not, register it.
4. Confirm the cron prompt matches this skill's workflow and format.
5. Log to journal.
