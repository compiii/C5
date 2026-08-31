"""Read-only users API client. No LDAP dependency, no offline identity fallback."""
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import time
import urllib.parse
import urllib.request


def profile(uid):
    if not re.fullmatch(r"(?:[a-z][a-z0-9._-]{2,63}|[0-9]{1,64})", uid):
        raise ValueError("Invalid uid")
    base = os.environ.get("C5_USERS_URL", "")
    url = urllib.parse.urlsplit(base)
    if (url.scheme != "http" or url.hostname != "127.0.0.1" or not url.port or
            url.username or url.password or url.query or url.fragment or
            url.path != "/users/internal/c5/profiles"):
        raise ValueError("C5_USERS_URL must be the loopback users API")
    path = Path(os.environ["C5_USERS_TOKEN_FILE"])
    if not path.is_absolute():
        raise ValueError("Absolute secret path required")
    with path.open() as stream:
        mode = os.fstat(stream.fileno()).st_mode
        if not stat.S_ISREG(mode) or mode & 0o037:
            raise ValueError("Private secret required")
        token = stream.read(8193).strip()
    if not 32 <= len(token) <= 8192 or any(c.isspace() for c in token):
        raise ValueError("Invalid API secret")
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(base + "/" + uid, headers={"Authorization": "Bearer " + token})
    with opener.open(request, timeout=5) as response:
        value = json.loads(response.read(16385))
    if (value.get("schema") != 1 or value.get("uid") != uid or
            type(value.get("c5_access")) is not bool or
            type(value.get("auth_version")) is not int or
            any(not isinstance(value.get(k), str) for k in ("fn", "sn", "mail"))):
        raise ValueError("Invalid users API response")
    value["time"] = int(time.time())
    return value


def client_address(peer, headers):
    """Only the loopback reverse proxy may supply a single client address."""
    address = ipaddress.ip_address(peer)
    forwarded = headers.get("x-forwarded-for", "")
    if address.is_loopback and forwarded:
        return str(ipaddress.ip_address(forwarded))
    return str(address)


def valid_ticket(ticket):
    return bool(re.fullmatch(r"ST-[A-Za-z0-9_-]{16,200}", ticket))
