"""Daily closing prices, for the measured figures (which are computed in code).

Source: Yahoo's chart endpoint, as the existing analysis scripts use. Closes are
split-adjusted, not dividend-adjusted. Fetched through the allowlist and cached
for the day. If the fetch fails, the copy in label_out/prices/ (written by
scripts/analysis/label_frequency.py) is read instead and marked as such.
"""
from __future__ import annotations

import datetime as dt
import json

from .. import net
from ..storage import Store

YAHOO = "https://query{host}.finance.yahoo.com/v8/finance/chart/{sym}"
INDEX = {"SPX": "^SPX", "XSP": "^XSP"}


class PricesUnavailable(Exception):
    pass


def yahoo_symbol(symbol: str) -> str:
    s = symbol.upper()
    return INDEX.get(s, s.replace(".", "-"))


def _parse(blob: bytes) -> list[tuple[dt.date, float]]:
    res = json.loads(blob)["chart"]["result"][0]
    out = []
    for t, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]):
        if c is not None and c > 0:
            out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).date(), float(c)))
    return out


def closes(symbol: str, store: Store | None = None) -> dict:
    """{"symbol", "source", "closes": [(date, close), ...]} oldest first."""
    last = None
    for host in (1, 2):
        try:
            blob = net.get(YAHOO.format(host=host, sym=yahoo_symbol(symbol)),
                           {"period1": 0, "period2": 9999999999, "interval": "1d"},
                           source="yahoo.chart", store=store)
            return {"symbol": symbol.upper(), "source": "Yahoo chart endpoint", "stale": False, "closes": _parse(blob)}
        except (net.FetchFailed, KeyError, IndexError, TypeError, ValueError) as e:
            last = e
    name = "_" + symbol.upper() if symbol.upper() in INDEX else symbol.upper()
    try:
        p = net.readable(f"label_out/prices/{name}.json")
        if p.exists():
            return {"symbol": symbol.upper(), "source": "local copy in label_out/prices", "stale": True,
                    "closes": _parse(p.read_bytes())}
    except (net.NotAllowed, KeyError, IndexError, TypeError, ValueError):
        pass
    raise PricesUnavailable(f"price history for {symbol.upper()}: {str(last)[:160]}")
