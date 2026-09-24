#!/usr/bin/env python3
"""Waited runner for the sanctioned Chronicle write path under DB contention.

When a usercontext cron run records a durable outcome (via the dispatch
`chronicle_record.py` script), chronicle.db may be under heavy multi-writer
load (every active session writes fold/compression events). The store's
start-up busy bound (INIT_BUSY_TIMEOUT_MS = 5s) then fails fast by design,
expecting callers to retry — but a one-shot cron caller has no retry loop.
This runner raises the start-up bound in-process (default 120s) and then
executes chronicle_record.py UNCHANGED, so the sanctioned writer can
out-wait the contention. Status 2026-09-23: plain attempts failed for
minutes; the first extended attempt succeeded immediately.

Usage:
  python _urecord_run.py --signals /path/to/signals.json [--init-ms 120000]
Run with the Hermes venv python.
"""
import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
PROFILE = HERE.parents[3]  # <profile>/skills/ocas-usercontext/scripts/_urecord_run.py
DISPATCH_SCRIPT = PROFILE / "skills" / "ocas-dispatch" / "scripts" / "chronicle_record.py"
CHRONICLE_PLUGIN = Path(os.environ.get("CHRONICLE_PLUGIN", "~/.hermes/plugins/chronicle"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--signals", required=True, help="validated JSON signal file")
    ap.add_argument("--init-ms", type=int, default=120000,
                    help="start-up busy timeout override in ms (default 120000)")
    args = ap.parse_args()

    if not DISPATCH_SCRIPT.exists():
        print(f"DEGRADED: {DISPATCH_SCRIPT} not found", file=sys.stderr)
        sys.exit(2)

    sys.path.insert(0, str(CHRONICLE_PLUGIN))
    import engine.store as store_mod

    store_mod.INIT_BUSY_TIMEOUT_MS = max(store_mod.INIT_BUSY_TIMEOUT_MS, args.init_ms)

    import runpy
    sys.argv = ["chronicle_record.py", "--signals", args.signals]
    runpy.run_path(str(DISPATCH_SCRIPT), run_name="__main__")


if __name__ == "__main__":
    main()