#!/usr/bin/python3
"""Compatibility stdin/stdout profile bridge to users; no LDAP or fake profiles."""
import json
import sys
from users_client import profile


def main():
    for line in sys.stdin:
        uid = line.strip()
        try:
            value = profile(uid)
        except Exception:
            print("users profile unavailable", file=sys.stderr)
            value = {"c5_access": False, "unavailable": True}
        print(json.dumps([uid, value]), flush=True)


if __name__ == "__main__":
    main()
