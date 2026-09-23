#!/usr/bin/env python3
"""Recent Gmail outcome scan for ocas-usercontext cron runs.

Lists metadata (From/Subject/Date) for messages in the last 48h on the primary
account. Run with the Hermes venv python.
"""
import sys
import json
from datetime import datetime, timezone, timedelta

sys.path.insert(0, '~/.hermes/profiles/indigo/scripts')
from google_auth_mcp import get_gmail_service

try:
    svc = get_gmail_service(account='<operator-email>')
except Exception as e:
    print(json.dumps({"DEGRADED": str(e)}))
    sys.exit(0)

now = datetime.now(timezone.utc)
since = int((now - timedelta(hours=48)).timestamp())
try:
    r = svc.users().messages().list(userId='me', q=f'after:{since//1000}', maxResults=30).execute()
except Exception as e:
    print(json.dumps({"DEGRADED": str(e)}))
    sys.exit(0)

msgs = r.get('messages', [])
rows = []
for m in msgs:
    try:
        msg = svc.users().messages().get(userId='me', id=m['id'], format='metadata',
                                         metadataHeaders=['From', 'Subject', 'Date']).execute()
    except Exception:
        continue
    hdrs = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
    rows.append({"from": hdrs.get('From', ''), "subject": hdrs.get('Subject', ''), "date": hdrs.get('Date', '')})

print(json.dumps({"count": len(rows), "messages": rows[:20]}, indent=2))
