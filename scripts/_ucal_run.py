#!/usr/bin/env python3
"""3-day calendar pull for ocas-usercontext cron runs.

Computes yesterday/today/tomorrow windows from the host clock (NEVER hardcoded
dates), tries the operator's account then the agent fallback account, queries the
primary + family calendars, dedupes by summary+start+location, and prints JSON:
{"yesterday": [...], "today": [...], "tomorrow": [...]}

Run with the Hermes venv python, e.g.:
  <hermes-venv>/bin/python <this file>
"""
import sys
import os
import json
from datetime import datetime, timedelta

# Make google_auth_mcp importable on this box (profile scripts, then shared).
for p in ('~/.hermes/profiles/indigo/scripts', '~/.hermes/scripts'):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo('America/Los_Angeles')
except Exception:
    from datetime import timezone
    TZ = timezone(timedelta(hours=-7))

from google_auth_mcp import get_service

CALENDARS = [
    '<operator-email>',  # Primary
    '<family-calendar-id>',  # Family
]

ACCOUNTS = [
    '<operator-email>',
    'mx.indigo.karasu@gmail.com',
]


def get_calendar_service():
    """Try each account until one works (cron has no user to re-auth)."""
    for account in ACCOUNTS:
        try:
            cal = get_service('calendar', 'v3',
                ['https://www.googleapis.com/auth/calendar.readonly'],
                account=account)
            cal.calendarList().list(maxResults=1).execute()
            print(f"Using account: {account}", file=sys.stderr)
            return cal
        except Exception as e:
            print(f"Account {account} failed: {e}", file=sys.stderr)
    return None


def parse_event_time(ev):
    """Return (time_str, local_date) in host TZ, or (None, None)."""
    start = ev.get('start', {})
    if 'dateTime' in start:
        raw = start['dateTime']
        if raw.endswith('Z'):
            dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(raw)
        local = dt.astimezone(TZ)
        return local.strftime('%H:%M'), local.date()
    elif 'date' in start:
        return 'all day', datetime.fromisoformat(start['date']).date()
    return None, None


def pull_events_for_date(calendar, target_date):
    time_min = datetime.combine(target_date, datetime.min.time(), tzinfo=TZ).isoformat()
    time_max = datetime.combine(target_date + timedelta(days=1), datetime.min.time(), tzinfo=TZ).isoformat()
    all_events = []
    seen = set()  # dedup: (summary, raw start, location) across calendars
    for cal_id in CALENDARS:
        try:
            result = calendar.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
                showDeleted=False
            ).execute()
        except Exception as e:
            print(f"Error querying calendar {cal_id}: {e}", file=sys.stderr)
            continue
        for ev in result.get('items', []):
            time_str, ev_date = parse_event_time(ev)
            if time_str is None or ev_date != target_date:
                continue
            summary = ev.get('summary', '(no title)')
            location = ev.get('location', '')
            start_dt = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date', ''))
            key = (summary, start_dt, location)
            if key in seen:
                continue
            seen.add(key)
            if location:
                all_events.append(f"{summary}, {time_str}, {location}")
            else:
                all_events.append(f"{summary}, {time_str}")
    return all_events


def main():
    today = datetime.now(TZ).date()
    calendar = get_calendar_service()
    if calendar is None:
        print(json.dumps({
            "yesterday": ["No available calendar data"],
            "today": ["No available calendar data"],
            "tomorrow": ["No available calendar data"],
            "degraded": "oauth_stale"
        }))
        return

    result = {
        'yesterday': pull_events_for_date(calendar, today - timedelta(days=1)),
        'today': pull_events_for_date(calendar, today),
        'tomorrow': pull_events_for_date(calendar, today + timedelta(days=1)),
    }
    for day in list(result):
        if not result[day]:
            result[day] = ["No scheduled events"]
    print(json.dumps(result))


if __name__ == '__main__':
    main()
