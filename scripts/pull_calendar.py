#!/usr/bin/env python3
"""DEPRECATED shim: use scripts/_ucal_run.py instead.

This file was a near-duplicate of _ucal_run.py and has been retired. It is kept
as a forwarding shim so any external caller importing or shelling out to
`pull_calendar.py` keeps working. It is NOT a second implementation.

Why it was retired (2026-09-30 10khr critique):
  1. D9 hazard. It had no argument handling at all, so `--help` performed a
     real authenticated 6-query Google Calendar pull and printed the owner's
     events. Probing a script for usage must never touch a live account.
  2. DST correctness. It hardcoded `timezone(timedelta(hours=-7))` (PDT) and so
     mis-filed every event by an hour between November and March. Its own
     reference (references/cron-calendar-access.md) warns: "Use the correct
     offset for the TARGET date, not today's date" — which this file did not
     do. _ucal_run.py resolves the zone via zoneinfo instead.
  3. Duplication. Two copies of the same query/dedup logic meant a fix to one
     silently did not apply to the other, which is how the DST defect survived.

It now delegates everything — flags, output, exit codes — to _ucal_run.py, so
the two paths cannot diverge again.

Usage:
  <hermes-venv>/bin/python pull_calendar.py [--help]     (delegates)
  <hermes-venv>/bin/python _ucal_run.py [--help]         (canonical)
"""
import sys

# D9: help guard before the delegation, so --help is answered without an import
# of google_auth_mcp and without any network call.
if "--help" in sys.argv or "-h" in sys.argv:
    print((__doc__ or "<no docstring>").strip())
    sys.exit(0)

import os
import runpy

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ucal_run.py")

if not os.path.exists(TARGET):
    print(f"DEGRADED: canonical helper missing at {TARGET}", file=sys.stderr)
    sys.exit(2)

# DeprecationWarning is suppressed by default outside __main__ (PEP 565), so a
# caller shelled out to this file would never learn it is retired. Print to
# stderr explicitly instead of relying on warnings.warn.
print(
    "WARNING: pull_calendar.py is deprecated and now delegates to "
    "_ucal_run.py. Update any caller that still names it.",
    file=sys.stderr)

# Preserve the caller's argv shape: _ucal_run.py reads sys.argv for --help only.
sys.argv = [TARGET] + sys.argv[1:]

runpy.run_path(TARGET, run_name="__main__")
