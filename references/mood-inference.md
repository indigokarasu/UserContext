# Mood Inference

Mood is not one word. Multiple emotions can coexist across different life dimensions. The goal is to capture emotional context across all signals the system has access to within the allocated window, not summarize feelings into a single label.

## Data Sources

Mood is inferred by reading across all available signals within the window:

| Source | Tool | What it reveals |
|--------|------|-----------------|
| Session history | `session_search` (limit 10, not 5) | Tone, pacing, topics discussed, avoided topics |
| Calendar events | `mcp_google_workspace_get_events` | High-stakes events (interviews, deadlines, appointments, travel) |
| Email signals | `mcp_google_workspace_search_gmail_messages` | Outcomes (rejections, acceptances, confirmations), urgency patterns |
| Chronicle facts | `chronicle_ask_about` | Known stressors, life events, ongoing situations |

## Window

- **Primary window:** Last 7 days (not 3 sessions)
- **Extended context:** If a significant event is found (job interview, rejection, trip), broaden to 14 days using `session_search` with relevant date ranges

## Mood Dimensions

Mood is structured as a list of **active dimensions**, each with a short label and the signal that produced it. Do not collapse to one word.

Format:
```
**Mood:** [label] about [topic], [label2] about [topic2]
```

Examples:
```
**Mood:** dejected about job search, excited about upcoming trip, stressed about insurance lapse
**Mood:** focused on floorplan feedback, relaxed week overall
**Mood:** unknown (insufficient signal)
```

## Inference Rules

### 1. Scan broadly first

Run `session_search` with limit=10, no keyword filter (get overall activity pattern). Then search for known signal keywords:
- `session_search(query="interview OR rejected OR offer OR job")` if job context suspected
- `session_search(query="trip OR travel OR flight OR hotel")` if travel context suspected
- `session_search(query="medical OR appointment OR insurance OR Rx")` if health context suspected

### 2. Cross-reference with calendar

Look at calendar events for:
- Interview events, rejection/confirmation outcomes
- Medical appointments, prescription renewals
- Travel bookings, flight confirmations
- Deadline-driven meetings

### 3. Check email for outcomes

Search Gmail for recent outcomes:
- Job application responses
- Booking/travel confirmations or cancellations
- Bills, insurance notices, appointment reminders

### 4. Build dimensions

For each significant signal found, add one mood dimension. Order by emotional weight (strongest first).

| Signal type | Possible mood labels |
|-------------|---------------------|
| Job rejection / failed interview | dejected, frustrated, defeated, anxious |
| Job offer / accepted interview | excited, relieved, optimistic |
| Upcoming deadline | stressed, anxious, determined, focused |
| Travel planning / trip coming | excited, anticipatory, relaxed |
| Medical / insurance / coverage gap | worried, anxious, stressed |
| Calendar silence (no events) | unplanned, open, unstructured |
| Many rapid email threads | overwhelmed, busy, engaged |
| Few / no sessions | quiet, independent, unknown |
| Correcting me / repeating myself | frustrated, impatient |
| Playful / humorous interaction | relaxed, energized, creative |

### 5. Constraints

- **Max 3 dimensions.** Pick the 3 strongest signals. Do not list every minor fluctuation.
- **No false positives.** If you can't find concrete evidence, don't invent a dimension.
- **Preserve contradictions.** "Dejected about job, excited about trip" is valid and useful.
- **No hedging.** Don't say "seems like" or "might be." Present observed signals confidently.
- **If insufficient signal:** mood = "unknown"
- **Mood is not advice.** Don't suggest what to do about it. Just report what signals indicate.

## Output Examples

After interviewing for a role you've wanted for months and getting rejected:

```
**Mood:** dejected about job search
```

But also — if in the same week you booked a trip to Honolulu and have a health appointment coming up:

```
**Mood:** dejected about job search, excited about Honolulu trip, worried about coverage gap
```

Both are true. The assistant needs all three to be useful.
