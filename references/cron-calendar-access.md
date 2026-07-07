# Cron-Mode Calendar Access (Google Workspace)

When `ocas-usercontext` runs as a cron job and the SCHEDULE source is Google
Calendar, OAuth tokens can expire between runs (cron has no user present to
re-authenticate). This reference documents the fallback pattern for reliable
calendar reads in cron mode.

## The Problem

The primary account (`jared.zimmerman@gmail.com`) may return `400 Bad Request`
or `invalid_grant` on token refresh. Cron cannot prompt for re-auth, so the run
would produce `No available calendar data` for all three days.

## The Fallback

The agent's own account (`mx.indigo.karasu@gmail.com`) has been granted calendar
sharing permissions on Jared's calendars. It can serve as a complete fallback:
when the primary account's token is dead, the indigo account can still read both
the primary and family calendars.

## Fallback Order

1. Try `jared.zimmerman@gmail.com` — works when token is valid.
2. On `400`/`invalid_grant`, try `mx.indigo.karasu@gmail.com` — works when the
   indigo token is valid AND has calendar sharing permissions.
3. If both fail, log `degraded: oauth_stale` and report honestly.

## Working Calendar IDs

| Calendar | ID |
|----------|-----|
| Jared (primary) | `jared.zimmerman@gmail.com` |
| Family | `family08350553536598846140@group.calendar.google.com` |

## Cron-Compatible Python Pattern

`execute_code` is blocked in cron mode. Use `write_file` + `terminal` instead:

```python
import sys
sys.path.insert(0, '/root/.hermes/scripts')
from google_auth_mcp import get_service

calendars_to_query = ['jared.zimmerman@gmail.com']
accounts_to_try = ['jared.zimmerman@gmail.com', 'mx.indigo.karasu@gmail.com']

calendar = None
working_account = None

for account in accounts_to_try:
    try:
        cal = get_service('calendar', 'v3',
            ['https://www.googleapis.com/auth/calendar.readonly'],
            account=account)
        cal.calendarList().list(maxResults=1).execute()
        calendar = cal
        working_account = account
        break
    except Exception as e:
        continue

if calendar is None:
    # Both accounts dead — degrade honestly
    print("DEGRADED: Both OAuth tokens invalid")
else:
    for cal_id in calendars_to_query:
        result = calendar.events().list(
            calendarId=cal_id,
            timeMin=time_min,  # RFC3339 with correct DST offset
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
            showDeleted=False
        ).execute()
        events = result.get('items', [])
        # ... process events ...
```

## Timezone Handling

Always convert event start times to local timezone before displaying. The
Calendar API returns times in the event's own timezone (often UTC with `Z`
suffix). Naive parsing shows UTC as if local.

```python
from datetime import datetime, timezone, timedelta
PDT = timezone(timedelta(hours=-7))  # Use PST (-8) in winter

raw = ev['start']['dateTime']
if raw.endswith('Z'):
    dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
else:
    dt = datetime.fromisoformat(raw)
local_dt = dt.astimezone(PDT)
time_str = local_dt.strftime('%H:%M')
```

All-day events have `start.date` (no `dateTime`) — detect with
`'date' in ev['start']` and label as "all day".

## Deduplication

The same event may appear on multiple calendars (e.g., a doctor's appointment
showing on both the primary and a shared calendar). Deduplicate by matching
`summary` + `start.dateTime` + `location`. Keep one copy.

## DST Offset

Use the correct offset for the **target date**, not today's date:
- PDT (Mar–Nov): `-07:00`
- PST (Nov–Mar): `-08:00`

## See Also

- `ocas-sands/references/direct_calendar_access.md` — full Sands calendar
  reference (multi-account fallback, Composio fallback, cron patterns).
- `ocas-sands/references/credential-files.md` — OAuth credential storage layout.
