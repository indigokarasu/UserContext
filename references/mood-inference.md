# Mood Inference

This is the only field in the snapshot that is genuinely *inferred*. Get it
right or leave it empty. A fabricated mood is worse than `quiet (low signal)`,
because the agent makes decisions about how to talk to the owner based on it.

## The one rule that matters most

**Mood is read from how the owner interacted and what outcomes landed. It is
NEVER read from the calendar.**

A reservation, a meeting, a flight on the calendar tells you the *schedule*, not
the *feeling*. The historical failure of this skill was laundering calendar
events into emotions ("tea reservation" → "anticipation for tea";
"dinner booked" → "content"). Stop. Those are events; they belong in the day
bullets, not in mood. Mood evidence comes from two places only:

1. **Session tone** (`session_search`) — pacing, topics raised, topics avoided,
   frustration, playfulness, repetition, what the owner kept returning to.
2. **Email outcomes** (gmail search) — a rejection, an offer, a confirmation, a
   cancellation, a bill, a deadline. Outcomes carry emotional weight; calendar
   entries do not.

Memory (`memory` search) supplies *standing context* that colors interpretation
(a known job transition, a recent loss, ongoing travel) but is not itself
same-day mood evidence. Use it to interpret signals, not to manufacture them.

## Output shape

```
**Mood:** [label] about [topic], [label2] about [topic2]
```

- 1 to 3 dimensions, strongest first, **each backed by a concrete signal**.
- Contradictions are valid and valuable: `dejected about job search, excited about Honolulu trip` can both be true in one week. Preserve them; do not average them into "mixed."
- No hedging words ("seems", "might"). State the observed signal plainly.
- If you cannot point to a concrete signal for a dimension, the dimension does not exist.
- Thin or no signal → `quiet (low signal)`. This is a correct, common answer. It is not a failure.

(Note: this supersedes any older "one word only" instruction. Mood is 1-3
evidence-backed dimensions, never collapsed to a single mandated word.)

## The Signal Ledger (do this before writing mood)

Before composing the mood line, write an internal ledger — one line per signal,
each tagged with its source. You are not allowed to assert a mood dimension that
does not trace to a ledger line. Example:

```
[session]  Repeated frustration about the gateway OOMing; returned to it 3x
[session]  Playful tangent about a side project late in the day
[email]    Rejection from <employer> re: senior role
[email]    Confirmation: flight to Honolulu booked
[memory]   Standing: job transition in progress (interpret job signals through this)
[trajectory] Yesterday's mood was "dejected about job search" -> persists
```

A thin ledger:

```
[session]  One short logistics session, neutral tone
[email]    Nothing notable
[memory]   No active travel or standing event surfaced
```

→ yields `quiet (low signal)`. That is the honest answer; write it.

## Inference procedure

### 1. Scan sessions broadly, then targeted

- `session_search` limit 10, **no keyword** first — read the overall tone and
  what dominated.
- Then targeted only if the broad scan hints at it (do not fish for drama):
  - job: `session_search("interview OR rejected OR offer OR job OR resume")`
  - travel: `session_search("trip OR flight OR hotel OR Honolulu")`
  - health/admin: `session_search("medical OR appointment OR insurance OR Rx")`
- The targeted searches confirm or size a signal the broad scan already raised.
  Do not invent a dimension from a targeted search that the broad scan and email
  did not corroborate.

### 2. Read email for outcomes (not subjects)

An outcome is something that resolved or is due: a rejection, an acceptance, a
confirmation, a cancellation, a bill, a hard deadline. A newsletter is not an
outcome. Weight outcomes by how much they change the owner's situation.

### 3. Apply standing context from memory

`memory` search for active travel and standing situations. Use it to *interpret*
(a curt job-related session reads differently mid-transition) — never to assert
a same-day mood with no same-day signal.

### 4. Build 1-3 dimensions

| Signal observed in ledger | Candidate labels |
|---------------------------|------------------|
| Job rejection / failed interview (session or email) | dejected, frustrated, defeated, anxious |
| Job offer / advanced stage | excited, relieved, optimistic |
| Hard deadline approaching (email/session, not just a calendar block) | stressed, determined, focused |
| Trip confirmed / actively planned | excited, anticipatory |
| Health/insurance/coverage outcome | worried, anxious |
| Many rapid email threads + busy sessions | overwhelmed, engaged |
| Few/short neutral sessions, no outcomes | quiet (low signal) |
| Owner correcting me / repeating himself | frustrated, impatient |
| Playful/humorous session tone | relaxed, energized, creative |

Order by emotional weight. Cap at 3. No false positives.

### 5. Apply trajectory (the continuity layer)

Compare to yesterday's snapshot (read in Step 0 of the workflow):

- Dimension present yesterday and today → prefix `still`: `still dejected about job search`.
- New today → prefix `now` or leave plain: `now relieved about the offer`.
- Yesterday's dimension gone, no replacement signal → drop it silently; do not
  carry a stale mood forward, and do not assert it "lifted" without a signal.

Trajectory is what makes a *daily* tracker more than a daily *snapshot*. A third
consecutive low day reads very differently from a one-off, and the agent should
know which it is.

## Sensitivity

Standing context in memory may include difficult, long-running facts (a
bereavement, a strained relationship, a health matter). Handle with restraint:
do not surface a sensitive standing fact as "mood" unless a same-day signal
genuinely raised it, and even then label the *signal*, not the underlying fact.
The snapshot is read by the agent in every session; it should inform tone, not
broadcast private weight without cause.

## Worked examples

Rich week:
```
**Mood:** still dejected about job search, excited about Honolulu trip, worried about coverage gap
```
(job rejection in email + persists from yesterday; flight confirmation; insurance notice — three real ledger signals.)

Quiet day:
```
**Mood:** quiet (low signal)
```
(one neutral logistics session, no outcomes — honest, correct, not a failure.)

Shift day:
```
**Mood:** now relieved about the offer
```
(yesterday "anxious about interview"; today an acceptance email landed — trajectory captured.)
