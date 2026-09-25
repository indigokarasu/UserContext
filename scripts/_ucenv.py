"""Identity/config keys for ocas-usercontext scripts.

Values live in the profile .env (outside this repo on purpose — this repo is
public). Scripts read keys here instead of hardcoding operator identity.
"""
import os

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
