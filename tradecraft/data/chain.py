"""Option chains: live from Cboe, then Tradier, or the daily snapshot.

Order of preference (operator decision, 20 November 2026): Cboe, Tradier, snapshot.
`live` tries Cboe and, if it fails, Tradier, and says which one answered; the
stages fall back to the snapshot when `live` fails.

Live: Cboe's free delayed quotes (15 minutes delayed), one request per symbol.
Tradier (TRADIER_TOKEN in .env): one request per expiration, expirations up to
TRADIER_MAX_DTE days out, real-time quotes on a brokerage token.
Snapshot: the latest file written by the daily job in snapshots/, which this
module only reads. The OCC-symbol parsing and the list of standard roots are
reused from scripts/daily/chain_census.py, which is imported unchanged.

A contract here is a plain dict: expiration, dte, strike, type, bid, ask,
open_interest, spot. Raw bid and ask are kept as the feed gave them. Each also
carries the feed's iv, delta, theta and vega where it gives them (None where
not): vendor model outputs, per share, used by stage 3 only. Stage 1's result
never includes them.
"""
from __future__ import annotations

import csv
import datetime as dt
import gzip
import importlib.util
import json
from functools import lru_cache
from zoneinfo import ZoneInfo

from .. import net, settings
from ..storage import Store

ET = ZoneInfo("America/New_York")
PT = ZoneInfo("America/Los_Angeles")
CBOE = "https://cdn.cboe.com/api/global/delayed_quotes/options/{symbol}.json"
TRADIER = "https://api.tradier.com/v1/markets/"
TRADIER_MAX_DTE = 190                     # the snapshot holds 0 to 180 days; no stage reads further out
INDEX_SYMBOLS = {"SPX", "XSP"}            # Cboe and the snapshot name these _SPX, _XSP


class ChainUnavailable(Exception):
    """No usable chain from this source."""


@lru_cache(maxsize=1)
def _census():
    """scripts/daily/chain_census.py, loaded read-only for its parsing helpers."""
    path = settings.ROOT / "scripts" / "daily" / "chain_census.py"
    spec = importlib.util.spec_from_file_location("chain_census", path)
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules["chain_census"] = mod      # its dataclasses need the module registered
    spec.loader.exec_module(mod)
    return mod


def feed_symbol(symbol: str) -> str:
    s = symbol.upper()
    return "_" + s if s in INDEX_SYMBOLS else s


def _num(x):
    try:
        return float(x) if x not in (None, "") else None
    except (TypeError, ValueError):
        return None


GREEKS = ("iv", "delta", "theta", "vega")


def _contract(occ: str, feed: str, asof: dt.date, bid, ask, oi, spot, extra: dict | None = None) -> dict | None:
    cc = _census()
    parsed = cc.parse_occ(occ)
    if parsed is None:
        return None
    root, exp, kind, strike = parsed
    if root not in cc.standard_roots(feed):
        return None                         # adjusted or alternate-deliverable series: not this name's liquidity
    return {"occ": occ, "expiration": exp, "dte": (dt.date.fromisoformat(exp) - asof).days,
            "strike": strike, "type": kind, "bid": _num(bid), "ask": _num(ask),
            "open_interest": int(_num(oi) or 0), "spot": spot,
            **{k: _num((extra or {}).get(k)) for k in GREEKS}}


def live(symbol: str, store: Store | None = None) -> dict:
    """The live chain: Cboe first, Tradier if Cboe fails. Not cached: a screen is of this
    moment. The result names its `provider` and, after a fall back, why (`fell_back`)."""
    try:
        return live_cboe(symbol, store)
    except ChainUnavailable as first:
        try:
            data = live_tradier(symbol, store)
        except ChainUnavailable as second:
            raise ChainUnavailable(f"{first}; {second}") from second
        data["fell_back"] = str(first)
        return data


def live_tradier(symbol: str, store: Store | None = None) -> dict:
    """The live chain from Tradier: the expirations, then one request for each."""
    if not settings.secret("TRADIER_TOKEN"):
        raise ChainUnavailable("Tradier: TRADIER_TOKEN is not set in .env")
    sym, feed = symbol.upper(), feed_symbol(symbol)
    now_et = dt.datetime.now(ET)

    def ask(path: str, **params):
        return json.loads(net.get(TRADIER + path, params, source="tradier.chain", store=store,
                                  bearer="TRADIER_TOKEN", use_cache=False))
    try:
        quote = ((ask("quotes", symbols=sym).get("quotes") or {}).get("quote")) or {}
        if isinstance(quote, list):
            quote = quote[0] if quote else {}
        spot = _num(quote.get("last")) or _num(quote.get("close"))
        if not spot:
            raise ChainUnavailable("Tradier: no price for the underlying")
        dates = ((ask("options/expirations", symbol=sym).get("expirations") or {}).get("date")) or []
        dates = [dates] if isinstance(dates, str) else dates
        wanted = [d for d in dates if 0 <= (dt.date.fromisoformat(d) - now_et.date()).days <= TRADIER_MAX_DTE]

        def one(exp: str) -> list[dict]:
            found = ((ask("options/chains", symbol=sym, expiration=exp, greeks="true").get("options") or {})
                     .get("option")) or []
            return [found] if isinstance(found, dict) else found
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as pool:
            quotes = [o for part in pool.map(one, wanted) for o in part]
    except net.FetchFailed as e:
        raise ChainUnavailable(f"Tradier: {e}") from e
    rows = []
    for o in quotes:
        g = o.get("greeks") or {}
        extra = {"iv": g.get("mid_iv"), "delta": g.get("delta"), "theta": g.get("theta"), "vega": g.get("vega")}
        c = _contract(o.get("symbol") or "", feed, now_et.date(), o.get("bid"), o.get("ask"),
                      o.get("open_interest"), spot, extra)
        if c:
            rows.append(c)
    if not rows:
        raise ChainUnavailable("Tradier: no option contracts listed")
    return {"symbol": sym, "source": "live", "provider": "Tradier", "delay": "real-time",
            "as_of": now_et.isoformat(timespec="minutes"), "feed_timestamp": "", "spot": spot, "contracts": rows}


def live_cboe(symbol: str, store: Store | None = None) -> dict:
    """The live (delayed) chain from Cboe."""
    feed = feed_symbol(symbol)
    try:
        payload = json.loads(net.get(CBOE.format(symbol=feed), source="cboe.chain", store=store,
                                     use_cache=False))
    except net.FetchFailed as e:
        raise ChainUnavailable(f"Cboe delayed quotes: {e}") from e
    d = payload.get("data") or {}
    spot = _num(d.get("current_price")) or _num(d.get("close"))
    if not spot:
        raise ChainUnavailable("Cboe delayed quotes: no price for the underlying")
    now_et = dt.datetime.now(ET)
    rows = [c for o in d.get("options") or []
            if (c := _contract(o.get("option") or "", feed, now_et.date(), o.get("bid"), o.get("ask"),
                               o.get("open_interest"), spot, o))]
    if not rows:
        raise ChainUnavailable("Cboe delayed quotes: no option contracts listed")
    return {"symbol": symbol.upper(), "source": "live", "provider": "Cboe", "delay": "15-minute delayed",
            "as_of": now_et.isoformat(timespec="minutes"),
            "feed_timestamp": str(payload.get("timestamp") or ""), "spot": spot, "contracts": rows}


def latest_snapshot_path():
    files = sorted((settings.ROOT / "snapshots").glob("chain_snapshot_*.csv.gz"))
    return files[-1] if files else None


def snapshot_info() -> dict | None:
    """Date and time of the latest snapshot, for Home's status chip."""
    p = latest_snapshot_path()
    if p is None:
        return None
    stamp = dt.datetime.strptime(p.name[len("chain_snapshot_"):-len(".csv.gz")], "%Y%m%d_%H%M%S")
    taken = stamp.replace(tzinfo=PT).astimezone(ET)
    return {"file": p.name, "taken_et": taken.isoformat(timespec="minutes")}


def snapshot(symbol: str) -> dict:
    """The symbol's chain from the latest daily snapshot (read-only)."""
    p = latest_snapshot_path()
    if p is None:
        raise ChainUnavailable("no daily snapshot found")
    feed = feed_symbol(symbol)
    rows, spot, asof = [], None, None
    with gzip.open(net.readable(p), "rt") as f:
        for r in csv.DictReader(f):
            if r["symbol"] != feed:
                continue
            asof = asof or dt.datetime.fromisoformat(r["asof"]).replace(tzinfo=PT)
            spot = spot or _num(r["spot"])
            c = _contract(r["occ_symbol"], feed, asof.date(), r["bid"], r["ask"], r["open_interest"], spot, r)
            if c:
                rows.append(c)
    if not rows:
        raise ChainUnavailable(f"{symbol.upper()} is not in the daily snapshot")
    return {"symbol": symbol.upper(), "source": "snapshot",
            "as_of": asof.astimezone(ET).isoformat(timespec="minutes"), "file": p.name,
            "spot": spot, "contracts": rows}
