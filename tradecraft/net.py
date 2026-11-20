"""The only way application code reaches the network or the file system.

- Network: hosts outside config/limits.json "reach.network_domains" are refused.
- Rate limits per host (SEC 5 a second, FMP 700 a minute): requests wait; none
  is dropped.
- Cache: responses are kept per source, per request, per calendar day, so a
  repeated run does not refetch.
- Files: reads only under "reach.read_roots", writes only under "reach.write_roots".

Secrets (the FMP key) are added here and never appear in a cache key, a trace
or an error message.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import deque
from pathlib import Path
from urllib.parse import urlencode, urlparse

import httpx

from . import settings
from .storage import Store


class NotAllowed(Exception):
    """A host or path outside the allowlist."""


class FetchFailed(Exception):
    """The source refused or did not answer."""


# ---- network allowlist and rate limits ----------------------------------------------

def check_host(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    allowed = settings.limits()["reach"]["network_domains"]
    if host not in allowed:
        raise NotAllowed(f"network access to {host or url!r} is not on the allowlist")
    return host


class _Limiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._hits: dict[str, deque] = {}

    def wait(self, host: str) -> float:
        rule = settings.limits()["outside_services"]["rate_limits"].get(host)
        if not rule:
            return 0.0
        n, window = (rule["per_second"], 1.0) if "per_second" in rule else (rule["per_minute"], 60.0)
        waited = 0.0
        while True:
            with self._lock:
                q = self._hits.setdefault(host, deque())
                t = time.monotonic()
                while q and t - q[0] >= window:
                    q.popleft()
                if len(q) < n:
                    q.append(t)
                    return waited
                pause = window - (t - q[0]) + 0.01
            time.sleep(pause)
            waited += pause


_limiter = _Limiter()
_client: httpx.Client | None = None


def _http() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(timeout=30, follow_redirects=False)
    return _client


def _headers_for(host: str) -> dict:
    h = {"Accept-Encoding": "gzip, deflate"}
    if host.endswith("sec.gov"):
        ua = settings.secret("SEC_USER_AGENT")
        if not ua:
            raise FetchFailed("SEC_USER_AGENT is not set in .env")
        h["User-Agent"] = ua
    else:
        h["User-Agent"] = "Tradecraft research tool"
    return h


def get(url: str, params: dict | None = None, *, source: str, store: Store | None = None,
        secret_param: tuple[str, str] | None = None, use_cache: bool = True,
        retries: int = 2) -> bytes:
    """GET a URL through the allowlist, the rate limiter and the daily cache.

    `secret_param` = (query name, secret name), e.g. ("apikey", "FMP_API_KEY"):
    added to the request only, never to the cache key or any message.
    """
    host = check_host(url)
    params = dict(params or {})
    key = hashlib.sha256(f"{source}|{url}|{urlencode(sorted(params.items()))}".encode()).hexdigest()
    store = store or Store()
    if use_cache:
        hit = store.cache_get(key)
        if hit is not None:
            return hit
    send = dict(params)
    if secret_param:
        val = settings.secret(secret_param[1])
        if not val:
            raise FetchFailed(f"{secret_param[1]} is not set in .env")
        send[secret_param[0]] = val
    last = ""
    for attempt in range(1 + retries):
        _limiter.wait(host)
        try:
            r = _http().get(url, params=send, headers=_headers_for(host))
            for _ in range(3):             # follow a redirect only to a host on the allowlist
                if r.status_code not in (301, 302, 303, 307, 308) or "location" not in r.headers:
                    break
                target = str(r.url.join(r.headers["location"]))
                hop = check_host(target)   # raises NotAllowed for any other host
                _limiter.wait(hop)
                r = _http().get(target, headers=_headers_for(hop))
        except httpx.HTTPError as e:
            last = f"{type(e).__name__}"
            time.sleep(0.5 * (2 ** attempt))
            continue
        if r.status_code == 200:
            body = r.content
            if use_cache:
                store.cache_put(key, source, body)
            return body
        last = f"HTTP {r.status_code}: {settings.redact(r.text[:200])}"
        if r.status_code in (429,) or r.status_code >= 500:
            time.sleep(0.5 * (2 ** attempt))
            continue
        break  # 4xx other than 429: the source refused; do not retry
    raise FetchFailed(f"{source}: {last}")


def get_json(url: str, params: dict | None = None, **kw) -> object:
    return json.loads(get(url, params, **kw))


# ---- file allowlist -----------------------------------------------------------------

def _inside(path: Path, roots: list[str]) -> bool:
    p = path.resolve()
    for r in roots:
        root = (settings.ROOT / r).resolve()
        if p == root or root in p.parents:
            return True
    return False


def readable(path: str | Path) -> Path:
    p = Path(path) if Path(path).is_absolute() else settings.ROOT / path
    if not _inside(p, settings.limits()["reach"]["read_roots"]):
        raise NotAllowed(f"reading {path} is outside the file allowlist")
    return p


def writable(path: str | Path) -> Path:
    p = Path(path) if Path(path).is_absolute() else settings.ROOT / path
    if not _inside(p, settings.limits()["reach"]["write_roots"]):
        raise NotAllowed(f"writing {path} is outside the file allowlist")
    return p
