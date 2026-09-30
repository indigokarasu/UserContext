#!/usr/bin/env python3
"""Recent Gmail outcome scan for ocas-usercontext cron runs.

Lists metadata (From/Subject/Date) for messages in the last 48h on the primary
account. Run with the Hermes venv python.

Usage:
  <hermes-venv>/bin/python _uemail_run.py [--hours 48] [--max 30] [--help]

Options:
  -h, --help     Show this help message and exit 0 without touching Gmail.
  --hours N       Lookback window in hours (default 48). How far back OUTCOME
                  signal reaches; mood weight is the same whatever you set.
  --max N         Cap on messages listed (default 30, output shows first 20).

Exit codes:
  0  Scan completed, OR the run degraded honestly (JSON carries a "DEGRADED"
     key). Same rule as the calendar helper: degradation is this skill's normal
     no-signal path, not a failure, so read the JSON rather than the code.
  2  Usage error.

I/O:
  stdout  {"count": N, "messages": [{"from","subject","date"}, ...]},
          or {"DEGRADED": "<reason>"} when auth or the query failed.
  stderr  nothing on the happy path.

Privacy: this returns real sender addresses and subjects into the agent's
context. It is deliberately metadata-only (no bodies) — do not paste any of it
into USER.md; cite mood evidence by channel only (see SKILL.md Gotchas).
"""
import sys

# D9: help guard FIRST, before every import and side effect. Without this,
# `--help` ran a live authenticated Gmail scan at module scope: 30 messages
# pulled and printed in ~8s, and again in ~15s for -h.
if "--help" in sys.argv or "-h" in sys.argv:
    print((__doc__ or "<no docstring>").strip())
    sys.exit(0)

import argparse
import os
import json
from datetime import datetime, timezone, timedelta


def main():
    ap = argparse.ArgumentParser(
        description="Recent Gmail outcome scan (OUTCOME signal) for "
                    "ocas-usercontext. Metadata only: no message bodies.")
    ap.add_argument("--hours", type=int, default=48,
                    help="lookback window in hours (default: 48)")
    ap.add_argument("--max", type=int, default=30,
                    help="max messages to list (default: 30)")
    args = ap.parse_args()

    # Defer the auth import so a missing dep is a degraded run, not a traceback.
    sys.path.insert(0, os.path.expanduser('~/.hermes/profiles/indigo/scripts'))
    try:
        from google_auth_mcp import get_gmail_service
        from _ucenv import get as envget
        svc = get_gmail_service(account=envget('OCAS_OPERATOR_EMAIL'))
    except Exception as e:
        print(json.dumps({"DEGRADED": str(e)}))
        return 0

    now = datetime.now(timezone.utc)
    since = int((now - timedelta(hours=args.hours)).timestamp())
    try:
        r = svc.users().messages().list(
            userId='me', q=f'after:{since//1000}', maxResults=args.max).execute()
    except Exception as e:
        print(json.dumps({"DEGRADED": str(e)}))
        return 0

    msgs = r.get('messages', [])
    rows = []
    for m in msgs:
        try:
            msg = svc.users().messages().get(
                userId='me', id=m['id'], format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']).execute()
        except Exception:
            continue
        hdrs = {h['name']: h['value']
                for h in msg.get('payload', {}).get('headers', [])}
        rows.append({"from": hdrs.get('From', ''),
                     "subject": hdrs.get('Subject', ''),
                     "date": hdrs.get('Date', '')})

    print(json.dumps({"count": len(rows), "messages": rows[:20]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
