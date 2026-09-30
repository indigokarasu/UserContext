"""Identity/config keys for ocas-usercontext scripts.

Values live in the profile .env (outside this repo on purpose — this repo is
public). Scripts read keys here instead of hardcoding operator identity.

This is an importable LIBRARY module, not an entry point: importing it has no
side effects (the .env is only opened when get() is called). It still honors
--help, because the D9 audit probes every executable in scripts/ and a
zero-output exit 0 reads as a missing guard rather than a library.

Usage:
  python _ucenv.py KEY [KEY ...]   print the resolved value of each key
  python _ucenv.py --help          this message

Prints the empty string for an unset key. Values are secrets-adjacent: this
CLI exists for debugging only, do not pipe its output into logs or context.
"""
import os
import sys

# D9: help guard before the ENV_FILE global is even needed.
if "--help" in sys.argv or "-h" in sys.argv:
    print((__doc__ or "<no docstring>").strip())
    sys.exit(0)

ENV_FILE = os.path.expanduser("~/.hermes/profiles/indigo/.env")


def get(key, default=""):
    """Return key from the environment, else from the profile .env."""
    val = os.environ.get(key)
    if val:
        return val
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(key + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    return default


if __name__ == "__main__":
    for k in sys.argv[1:]:
        print(get(k))
