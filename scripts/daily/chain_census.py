#!/usr/bin/env python3
"""
chain_census.py — options chain liquidity census + point-in-time snapshot logger.

Two jobs, one pass over the data:

  1. CENSUS  How many optionable names actually clear a tradeable liquidity gate?
             Research puts this at ~250 (range 150-400, pessimistic 100-150) but no
             published absolute-threshold census exists. This measures it for real.

  2. SNAPSHOT  Write the raw quoted chain to disk, point-in-time. Chains cannot be
             reconstructed from a pricing model later, so every night not logged is
             permanently lost. The census is a by-product of doing this anyway.

Design decisions that come straight out of the research, and should not be
"simplified" later without re-reading it:

  * Spread is measured as a % of premium ON THE SPECIFIC CONTRACT, never a
    per-name average. Liquidity varies enormously across a single chain.
  * The gate EXCLUDES; it does not penalise. Gross returns are HIGHER in illiquid
    terciles (23.9% vs 18.0%) while net returns go +8.2% -> -0.8%. Any ranking on
    gross richness selects for contracts whose edge dies in execution.
  * Raw bid/ask are stored verbatim. ~38% of raw OPRA trades appear to print inside
    the BBO from sequencing errors, biased to flatter the trader, so downstream
    analysis needs the untouched quote.
  * DTE band defaults to 42-90. Options >90 DTE are insignificant or negative at
    25% costs; <42 DTE spreads widen sharply (0DTE ~8.7-9.5% of premium vs ~2%).
  * "Has weeklys" is recorded as a free exchange-curated liquidity certification.
  * Quote pathologies (crossed, locked, one-sided, zero-bid) are flagged, not fixed.
    A mid computed from a one-sided quote is fiction.

Usage:
    # verify the logic with no token and no network
    python3 scripts/daily/chain_census.py --synthetic --out ./census_out

    # real run (Tradier Lite account token; free, personal use is the default term)
    export TRADIER_TOKEN=...
    python3 scripts/daily/chain_census.py --universe universe.txt --out ./census_out

    # nightly snapshot cron: same call, --snapshot-only skips census aggregation
    python3 scripts/daily/chain_census.py --universe universe.txt --out ./snapshots --snapshot-only

universe.txt is one ticker per line. To build a starting universe see
build_universe_hint() at the bottom.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import http.client
import json
import math
import os
import random
import subprocess
import sys
import time
from dataclasses import dataclass, asdict, field
from typing import Iterable, Iterator

import urllib.error
import urllib.parse
import urllib.request


# ----------------------------------------------------------------------------
# Gate configuration. These are the thresholds from the factor spec.
# ----------------------------------------------------------------------------

@dataclass
class GateConfig:
    # Spread as a fraction of premium (mid). 0.05 = 5%.
    max_spread_pct: float = 0.05
    # Absolute floors. A tight spread on a contract nobody holds is not liquidity.
    min_open_interest: int = 100
    min_volume: int = 0          # daily volume is noisy; OI is the better floor
    # Maturity band in calendar days.
    min_dte: int = 42
    max_dte: int = 90
    # What the SNAPSHOT keeps, as distinct from what the gate passes. Since
    # 15 Nov 2026 the expiry band is an adjustable control in on-demand mode
    # (7-180 days) and very short-dated contracts can be named by the operator,
    # so the archive keeps 0-180 days. Contracts outside min_dte..max_dte are
    # stored with the reason dte_out_of_band; they are not dropped. Snapshots
    # before 16 Nov 2026 hold 42-90 days only, and that cannot be backfilled.
    store_min_dte: int = 0
    store_max_dte: int = 180
    # Moneyness band, |log(K/S)|. 0.10 ~= +/-10%.
    max_abs_log_moneyness: float = 0.10
    # Reject quotes below this premium outright: tick granularity makes the
    # spread-% metric meaningless on very cheap contracts.
    min_mid_price: float = 0.20

    def as_dict(self) -> dict:
        return asdict(self)


# ----------------------------------------------------------------------------
# Per-contract record. This is what gets written to the snapshot.
# ----------------------------------------------------------------------------

@dataclass
class ContractRecord:
    asof: str
    symbol: str
    occ_symbol: str
    expiration: str
    strike: float
    option_type: str
    spot: float

    # Raw quote, stored verbatim. Do not clean these in place.
    bid: float | None
    ask: float | None
    bid_size: int | None
    ask_size: int | None
    last: float | None
    volume: int | None
    open_interest: int | None

    # Derived
    mid: float | None = None
    spread_abs: float | None = None
    spread_pct: float | None = None
    dte: int | None = None
    log_moneyness: float | None = None

    # Quality flags, not corrections
    flags: str = ""

    # Gate outcome
    gate_pass: bool = False
    gate_reasons: str = ""

    # Provenance: which feed, and the feed's own timestamp for the quote batch.
    source: str = ""
    source_ts: str = ""

    # The vendor's own implied volatility, Greeks and theoretical value, stored
    # verbatim from 16 Nov 2026. These are the feed's model outputs, not
    # measurements: keep them for convenience and for a delta-based strike
    # control, and recompute from bid/ask where it matters. Appended as the
    # LAST columns so older snapshot readers are unaffected. Empty in snapshots
    # before 16 Nov 2026 and for sources that do not supply them.
    iv: float | None = None
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    rho: float | None = None
    theo: float | None = None


def _f(x) -> float | None:
    try:
        if x is None:
            return None
        v = float(x)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def _i(x) -> int | None:
    try:
        return None if x is None else int(x)
    except (TypeError, ValueError):
        return None


def derive(rec: ContractRecord, asof_date: dt.date) -> ContractRecord:
    """Compute derived fields and flag quote pathologies. Never mutates bid/ask."""
    flags: list[str] = []
    bid, ask = rec.bid, rec.ask

    if bid is None or ask is None:
        flags.append("missing_quote")
    else:
        if bid <= 0 and ask <= 0:
            flags.append("no_quote")
        elif bid <= 0:
            flags.append("zero_bid")       # one-sided: mid is fiction
        elif ask <= 0:
            flags.append("zero_ask")
        elif bid > ask:
            flags.append("crossed")
        elif bid == ask:
            flags.append("locked")

        # Only compute a mid from a genuine two-sided quote.
        if bid > 0 and ask > 0 and ask >= bid:
            rec.mid = (bid + ask) / 2.0
            rec.spread_abs = ask - bid
            if rec.mid > 0:
                rec.spread_pct = rec.spread_abs / rec.mid

    try:
        exp = dt.date.fromisoformat(rec.expiration)
        rec.dte = (exp - asof_date).days
    except ValueError:
        flags.append("bad_expiration")

    if rec.spot and rec.spot > 0 and rec.strike > 0:
        rec.log_moneyness = math.log(rec.strike / rec.spot)

    if rec.open_interest is None:
        flags.append("missing_oi")

    # Adjusted / alternate-deliverable roots (e.g. "B1SPY", "AAPL1") quote a
    # different contract than the standard one. Keep them in the snapshot, but
    # flag them so the gate does not count them as the name's liquidity.
    root = occ_root(rec.occ_symbol)
    if root and root not in standard_roots(rec.symbol):
        flags.append("nonstandard_root")

    rec.flags = "|".join(flags)
    return rec


def apply_gate(rec: ContractRecord, cfg: GateConfig) -> ContractRecord:
    """
    Exclusionary gate. A contract either qualifies or it is not scored at all.
    Reasons are recorded so the census can report WHY names fail, which is the
    interesting part.
    """
    reasons: list[str] = []

    if rec.flags and any(f in rec.flags for f in
                         ("missing_quote", "no_quote", "zero_bid", "zero_ask",
                          "crossed", "bad_expiration")):
        reasons.append("bad_quote")

    if "nonstandard_root" in rec.flags:
        reasons.append("nonstandard_root")

    if rec.mid is None:
        reasons.append("no_mid")
    elif rec.mid < cfg.min_mid_price:
        reasons.append("premium_too_low")

    if rec.spread_pct is None:
        reasons.append("no_spread")
    elif rec.spread_pct > cfg.max_spread_pct:
        reasons.append("spread_too_wide")

    oi = rec.open_interest or 0
    if oi < cfg.min_open_interest:
        reasons.append("oi_too_low")

    vol = rec.volume or 0
    if cfg.min_volume and vol < cfg.min_volume:
        reasons.append("volume_too_low")

    if rec.dte is None:
        reasons.append("no_dte")
    elif not (cfg.min_dte <= rec.dte <= cfg.max_dte):
        reasons.append("dte_out_of_band")

    if rec.log_moneyness is None:
        reasons.append("no_moneyness")
    elif abs(rec.log_moneyness) > cfg.max_abs_log_moneyness:
        reasons.append("moneyness_out_of_band")

    rec.gate_pass = not reasons
    rec.gate_reasons = "|".join(reasons)
    return rec


# ----------------------------------------------------------------------------
# OCC symbol helpers (shared by all providers)
# ----------------------------------------------------------------------------

# Index chains list PM-settled / weekly series under a second root. These are
# standard contracts, not adjusted ones.
INDEX_ALT_ROOTS = {
    "SPX": {"SPXW"}, "NDX": {"NDXP"}, "RUT": {"RUTW"}, "VIX": {"VIXW"},
    "XSP": set(), "DJX": set(), "OEX": set(), "XEO": set(),
}


def standard_roots(symbol: str) -> set[str]:
    base = symbol.lstrip("_").replace(".", "").replace("/", "").upper()
    return {base} | INDEX_ALT_ROOTS.get(base, set())


def occ_root(occ: str) -> str:
    """OCC symbol = ROOT + YYMMDD + C/P + strike*1000 (8 digits)."""
    occ = (occ or "").replace(" ", "")
    return occ[:-15] if len(occ) > 15 else ""


def parse_occ(occ: str) -> tuple[str, str, str, float] | None:
    """-> (root, expiration ISO, 'call'|'put', strike), or None if malformed."""
    occ = (occ or "").replace(" ", "")
    if len(occ) <= 15:
        return None
    tail = occ[-15:]
    yymmdd, cp, k = tail[:6], tail[6], tail[7:]
    if not (yymmdd.isdigit() and k.isdigit() and cp in "CP"):
        return None
    try:
        exp = dt.date(2000 + int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:6]))
    except ValueError:
        return None
    return occ[:-15], exp.isoformat(), "call" if cp == "C" else "put", int(k) / 1000.0


# ----------------------------------------------------------------------------
# Data source: Cboe free delayed quotes. Public JSON, no auth, ~15 min delay.
# One request returns the whole chain plus the underlying quote. Response shape
# verified 2026-11-11:
#   {"timestamp": "...", "symbol": "...",
#    "data": {"current_price": .., "options": [
#       {"option": OCC, "bid", "ask", "bid_size", "ask_size", "open_interest",
#        "volume", "last_trade_price", "iv", greeks..., ...}]}}
# All numerics arrive as floats. Index chains need a leading underscore (_SPX).
# cdn.cboe.com 307-redirects to cdn-api.cboe.com; urllib follows it.
# ----------------------------------------------------------------------------

CBOE_BASE = "https://cdn.cboe.com/api/global/delayed_quotes/options"


def fetch_chain_cboe(symbol: str) -> dict:
    """
    urllib first; on a truncated or undecodable body, fall back to the system
    curl (ships with macOS). Observed 2026-11-11: macOS system python 3.9 /
    LibreSSL 2.8.3 consistently got IncompleteRead on Cboe's chunked HTTP/1.1
    responses (through a local proxy) while curl received the full body.
    A body that still fails to parse raises: never use a partial chain.
    """
    url = f"{CBOE_BASE}/{urllib.parse.quote(symbol)}.json"
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "chain-census/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError:
        raise                                   # 403 = unknown symbol; don't retry
    except (http.client.IncompleteRead, json.JSONDecodeError, OSError):
        pass
    out = subprocess.run(
        ["curl", "-sSfL", "--max-time", "60", "-A", "chain-census/1.0", url],
        capture_output=True, check=True,
    ).stdout
    return json.loads(out.decode("utf-8"))


def records_for_symbol_cboe(symbol: str, cfg: GateConfig,
                            asof: dt.datetime) -> Iterator[ContractRecord]:
    asof_date = asof.date()
    payload = fetch_chain_cboe(symbol)
    d = payload.get("data") or {}
    spot = _f(d.get("current_price")) or _f(d.get("close"))
    if not spot:
        return
    source_ts = str(payload.get("timestamp") or "")

    for o in d.get("options") or []:
        parsed = parse_occ(o.get("option"))
        if parsed is None:
            continue
        _root, exp, opt_type, strike = parsed
        # Same in-band filter as the Tradier path, so the two sources produce
        # comparable snapshots and census failure counts.
        dte = (dt.date.fromisoformat(exp) - asof_date).days
        if not (cfg.store_min_dte <= dte <= cfg.store_max_dte):
            continue
        rec = ContractRecord(
            asof=asof.isoformat(timespec="seconds"),
            symbol=symbol,
            occ_symbol=o.get("option") or "",
            expiration=exp,
            strike=strike,
            option_type=opt_type,
            spot=spot,
            bid=_f(o.get("bid")),
            ask=_f(o.get("ask")),
            bid_size=_i(_f(o.get("bid_size"))),
            ask_size=_i(_f(o.get("ask_size"))),
            last=_f(o.get("last_trade_price")),
            volume=_i(_f(o.get("volume"))),
            open_interest=_i(_f(o.get("open_interest"))),
            source="cboe",
            source_ts=source_ts,
            iv=_f(o.get("iv")),
            delta=_f(o.get("delta")),
            gamma=_f(o.get("gamma")),
            theta=_f(o.get("theta")),
            vega=_f(o.get("vega")),
            rho=_f(o.get("rho")),
            theo=_f(o.get("theo")),
        )
        yield apply_gate(derive(rec, asof_date), cfg)


# ----------------------------------------------------------------------------
# Data source: Tradier. Kept as the fallback (needs TRADIER_TOKEN).
# ----------------------------------------------------------------------------

TRADIER_BASE = "https://api.tradier.com/v1"


def tradier_get(path: str, params: dict, token: str) -> dict:
    """Stdlib-only GET so this runs on a bare system python3 with no pip install."""
    url = f"{TRADIER_BASE}{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "chain-census/1.0",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_spot(symbol: str, token: str) -> float | None:
    d = tradier_get("/markets/quotes", {"symbols": symbol}, token)
    q = (d.get("quotes") or {}).get("quote")
    if isinstance(q, list):
        q = q[0] if q else None
    if not q:
        return None
    return _f(q.get("last")) or _f(q.get("close"))


def fetch_expirations(symbol: str, token: str) -> list[str]:
    d = tradier_get(
        "/markets/options/expirations",
        {"symbol": symbol, "includeAllRoots": "true", "strikes": "false"},
        token,
    )
    exps = (d.get("expirations") or {}).get("date") or []
    return [exps] if isinstance(exps, str) else list(exps)


def fetch_chain(symbol: str, expiration: str, token: str) -> list[dict]:
    d = tradier_get(
        "/markets/options/chains",
        {"symbol": symbol, "expiration": expiration, "greeks": "false"},
        token,
    )
    opts = (d.get("options") or {}).get("option") or []
    return [opts] if isinstance(opts, dict) else list(opts)


def records_for_symbol(symbol: str, token: str, cfg: GateConfig,
                       asof: dt.datetime) -> Iterator[ContractRecord]:
    asof_date = asof.date()
    spot = fetch_spot(symbol, token)
    if not spot:
        return

    exps = fetch_expirations(symbol, token)
    # Only pull expirations that could land in the band. Each chain call costs a
    # request, and the whole point is to stay inside a free tier's rate limit.
    wanted = []
    for e in exps:
        try:
            d = dt.date.fromisoformat(e)
        except ValueError:
            continue
        dte = (d - asof_date).days
        if cfg.store_min_dte <= dte <= cfg.store_max_dte:
            wanted.append(e)

    for e in wanted:
        for o in fetch_chain(symbol, e, token):
            rec = ContractRecord(
                asof=asof.isoformat(timespec="seconds"),
                symbol=symbol,
                occ_symbol=o.get("symbol") or "",
                expiration=o.get("expiration_date") or e,
                strike=_f(o.get("strike")) or 0.0,
                option_type=o.get("option_type") or "",
                spot=spot,
                bid=_f(o.get("bid")),
                ask=_f(o.get("ask")),
                bid_size=_i(o.get("bidsize")),
                ask_size=_i(o.get("asksize")),
                last=_f(o.get("last")),
                volume=_i(o.get("volume")),
                open_interest=_i(o.get("open_interest")),
                source="tradier",
            )
            yield apply_gate(derive(rec, asof_date), cfg)


# ----------------------------------------------------------------------------
# Synthetic mode: verifies the gate logic with no token and no network.
# Calibrated so the pass rate lands in a plausible range, NOT to predict reality.
# ----------------------------------------------------------------------------

def synthetic_records(symbol: str, tier: str, cfg: GateConfig,
                      asof: dt.datetime, rng: random.Random) -> list[ContractRecord]:
    asof_date = asof.date()
    spot = rng.uniform(20, 600)

    # Liquidity tier drives spread and OI. Loosely mirrors the observed market:
    # a handful of mega-liquid names, a few hundred decent ones, a long tail.
    params = {
        "mega":  dict(spread_frac=(0.003, 0.012), oi=(5_000, 150_000)),
        "good":  dict(spread_frac=(0.015, 0.055), oi=(200, 8_000)),
        "thin":  dict(spread_frac=(0.06, 0.35),  oi=(0, 300)),
        "dead":  dict(spread_frac=(0.25, 1.20),  oi=(0, 40)),
    }[tier]

    out: list[ContractRecord] = []
    for weeks_out in (5, 7, 9, 11, 13):
        exp = asof_date + dt.timedelta(days=weeks_out * 7)
        for k_mult in (0.85, 0.92, 0.97, 1.0, 1.03, 1.08, 1.15):
            strike = round(spot * k_mult, 1)
            for opt_type in ("call", "put"):
                # crude premium proxy: intrinsic + time value
                intrinsic = max(0.0, (spot - strike) if opt_type == "call"
                                else (strike - spot))
                tv = spot * 0.02 * math.sqrt(weeks_out / 52.0) * rng.uniform(0.6, 1.5)
                mid = max(0.01, intrinsic + tv)

                sf = rng.uniform(*params["spread_frac"])
                half = max(0.005, mid * sf / 2.0)
                bid = max(0.0, round(mid - half, 2))
                ask = round(mid + half, 2)

                oi = int(rng.uniform(*params["oi"]))
                vol = int(oi * rng.uniform(0, 0.4))

                # inject the pathologies the gate must survive
                roll = rng.random()
                if roll < 0.02:
                    bid = 0.0                      # one-sided
                elif roll < 0.03:
                    bid, ask = ask, bid            # crossed
                elif roll < 0.04:
                    ask = bid                      # locked

                rec = ContractRecord(
                    asof=asof.isoformat(timespec="seconds"),
                    symbol=symbol,
                    occ_symbol=f"{symbol}{exp:%y%m%d}{opt_type[0].upper()}{int(strike*1000):08d}",
                    expiration=exp.isoformat(),
                    strike=strike,
                    option_type=opt_type,
                    spot=round(spot, 2),
                    bid=bid, ask=ask,
                    bid_size=int(rng.uniform(1, 200)),
                    ask_size=int(rng.uniform(1, 200)),
                    last=round(mid, 2),
                    volume=vol,
                    open_interest=oi,
                )
                out.append(apply_gate(derive(rec, asof_date), cfg))
    return out


def synthetic_universe(n: int, rng: random.Random) -> list[tuple[str, str]]:
    """(symbol, tier) pairs with a roughly market-shaped liquidity distribution."""
    tiers = (["mega"] * max(1, int(n * 0.01))
             + ["good"] * int(n * 0.10)
             + ["thin"] * int(n * 0.30))
    tiers += ["dead"] * (n - len(tiers))
    rng.shuffle(tiers)
    return [(f"SYN{i:04d}", t) for i, t in enumerate(tiers)]


# ----------------------------------------------------------------------------
# Census aggregation
# ----------------------------------------------------------------------------

@dataclass
class SymbolSummary:
    symbol: str
    spot: float | None = None
    contracts_seen: int = 0
    contracts_in_band: int = 0        # right DTE + moneyness, before liquidity
    contracts_passed: int = 0
    best_spread_pct: float | None = None
    median_spread_pct_in_band: float | None = None
    max_oi_in_band: int = 0
    has_weeklys: bool = False
    passes: bool = False
    top_failure: str = ""
    failure_counts: dict = field(default_factory=dict)


def summarise(symbol: str, recs: list[ContractRecord]) -> SymbolSummary:
    s = SymbolSummary(symbol=symbol)
    if not recs:
        return s
    s.spot = recs[0].spot
    s.contracts_seen = len(recs)

    # "has weeklys": any expiration that is not a third Friday
    exps = {r.expiration for r in recs if r.expiration}
    for e in exps:
        try:
            d = dt.date.fromisoformat(e)
        except ValueError:
            continue
        third_friday = d.weekday() == 4 and 15 <= d.day <= 21
        if not third_friday:
            s.has_weeklys = True
            break

    in_band_spreads: list[float] = []
    fail: dict[str, int] = {}

    for r in recs:
        structural = {"dte_out_of_band", "moneyness_out_of_band", "no_dte",
                      "no_moneyness"}
        rs = set(r.gate_reasons.split("|")) - {""}
        if not (rs & structural):
            s.contracts_in_band += 1
            if r.spread_pct is not None:
                in_band_spreads.append(r.spread_pct)
            s.max_oi_in_band = max(s.max_oi_in_band, r.open_interest or 0)

        if r.gate_pass:
            s.contracts_passed += 1
        else:
            for reason in rs:
                fail[reason] = fail.get(reason, 0) + 1

        if r.spread_pct is not None:
            s.best_spread_pct = (r.spread_pct if s.best_spread_pct is None
                                 else min(s.best_spread_pct, r.spread_pct))

    if in_band_spreads:
        in_band_spreads.sort()
        mid = len(in_band_spreads) // 2
        s.median_spread_pct_in_band = (
            in_band_spreads[mid] if len(in_band_spreads) % 2
            else (in_band_spreads[mid - 1] + in_band_spreads[mid]) / 2.0
        )

    s.failure_counts = fail
    # A name qualifies if it has at least a couple of tradeable contracts, not one
    # lucky strike. One qualifying contract is not a tradeable name.
    s.passes = s.contracts_passed >= 2
    if fail:
        s.top_failure = max(fail.items(), key=lambda kv: kv[1])[0]
    return s


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------

SNAPSHOT_FIELDS = list(ContractRecord.__annotations__.keys())


def write_snapshot(path: str, recs: Iterable[ContractRecord]) -> int:
    n = 0
    with gzip.open(path, "wt", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=SNAPSHOT_FIELDS)
        w.writeheader()
        for r in recs:
            w.writerow(asdict(r))
            n += 1
    return n


def write_census(path: str, summaries: list[SymbolSummary], cfg: GateConfig,
                 asof: dt.datetime, extra: dict | None = None) -> dict:
    passing = [s for s in summaries if s.passes]
    agg_fail: dict[str, int] = {}
    for s in summaries:
        if not s.passes and s.top_failure:
            agg_fail[s.top_failure] = agg_fail.get(s.top_failure, 0) + 1

    report = {
        "asof": asof.isoformat(timespec="seconds"),
        **(extra or {}),
        "gate": cfg.as_dict(),
        "universe_size": len(summaries),
        "names_passing": len(passing),
        "pass_rate": round(len(passing) / len(summaries), 4) if summaries else 0.0,
        "names_with_weeklys": sum(1 for s in summaries if s.has_weeklys),
        "total_contracts_seen": sum(s.contracts_seen for s in summaries),
        "total_contracts_passing": sum(s.contracts_passed for s in summaries),
        "top_blocking_reason_by_name": dict(
            sorted(agg_fail.items(), key=lambda kv: -kv[1])
        ),
        "passing_names": sorted(s.symbol for s in passing),
    }
    with open(path, "w") as fh:
        json.dump(report, fh, indent=2)

    with open(path.replace(".json", "_by_symbol.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["symbol", "spot", "contracts_seen", "contracts_in_band",
                    "contracts_passed", "best_spread_pct",
                    "median_spread_pct_in_band", "max_oi_in_band",
                    "has_weeklys", "passes", "top_failure"])
        for s in sorted(summaries, key=lambda x: (-x.contracts_passed, x.symbol)):
            w.writerow([s.symbol, s.spot, s.contracts_seen, s.contracts_in_band,
                        s.contracts_passed,
                        None if s.best_spread_pct is None else round(s.best_spread_pct, 5),
                        None if s.median_spread_pct_in_band is None
                        else round(s.median_spread_pct_in_band, 5),
                        s.max_oi_in_band, s.has_weeklys, s.passes, s.top_failure])
    return report


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def us_session(now: dt.datetime | None = None) -> str:
    """
    'regular' if inside 09:30-16:00 America/New_York on a weekday, else
    'outside_regular_hours'. Holidays are not checked.

    Why it matters: after the close, delayed feeds show quotes that market makers
    have widened or left stale. Observed 2026-11-11 ~23:38 ET: QQQ ATM 44-DTE call
    25.61/27.35 (6.6%), AAPL ATM 10.80/12.35 (13%); intraday these are cents wide.
    A census or snapshot taken then measures after-hours quoting, not liquidity.
    """
    from zoneinfo import ZoneInfo
    et = (now or dt.datetime.now(dt.timezone.utc)).astimezone(ZoneInfo("America/New_York"))
    open_, close = et.replace(hour=9, minute=30, second=0), et.replace(hour=16, minute=0, second=0)
    return "regular" if et.weekday() < 5 and open_ <= et < close else "outside_regular_hours"


def build_universe_hint() -> str:
    return (
        "Starting universes, cheapest first:\n"
        "  * Tradier /markets/options/lookup gives all optionable underlyings.\n"
        "  * Cboe publishes a listed-symbol directory.\n"
        "  * S&P 500 + Nasdaq 100 + Russell 1000 constituents is a decent proxy\n"
        "    for the top of the distribution and is where the gate actually binds.\n"
        "The research says the gate binds INSIDE the S&P 500, so starting with a\n"
        "broad-index constituent list costs little and loses little.\n"
    )


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--universe", help="file with one ticker per line")
    p.add_argument("--out", default="./census_out")
    p.add_argument("--synthetic", action="store_true",
                   help="run on generated chains; no token or network needed")
    p.add_argument("--synthetic-n", type=int, default=600)
    p.add_argument("--source", choices=("cboe", "tradier"), default="cboe",
                   help="cboe: free delayed quotes, no key (default); "
                        "tradier: needs TRADIER_TOKEN")
    p.add_argument("--snapshot-only", action="store_true",
                   help="write the snapshot, skip census aggregation")
    p.add_argument("--max-spread-pct", type=float, default=0.05)
    p.add_argument("--min-oi", type=int, default=100)
    p.add_argument("--min-dte", type=int, default=42)
    p.add_argument("--max-dte", type=int, default=90)
    p.add_argument("--store-min-dte", type=int, default=0,
                   help="shortest expiry kept in the snapshot (days)")
    p.add_argument("--store-max-dte", type=int, default=180,
                   help="longest expiry kept in the snapshot (days)")
    p.add_argument("--sleep", type=float, default=0.3,
                   help="seconds between symbols; respect the free-tier rate limit")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args(argv)

    cfg = GateConfig(
        max_spread_pct=args.max_spread_pct,
        min_open_interest=args.min_oi,
        min_dte=args.min_dte,
        max_dte=args.max_dte,
        store_min_dte=min(args.store_min_dte, args.min_dte),
        store_max_dte=max(args.store_max_dte, args.max_dte),
    )

    os.makedirs(args.out, exist_ok=True)
    asof = dt.datetime.now()
    stamp = asof.strftime("%Y%m%d_%H%M%S")
    snap_path = os.path.join(args.out, f"chain_snapshot_{stamp}.csv.gz")

    all_recs: list[ContractRecord] = []
    summaries: list[SymbolSummary] = []

    if args.synthetic:
        rng = random.Random(args.seed)
        uni = synthetic_universe(args.synthetic_n, rng)
        print(f"synthetic mode: {len(uni)} names", file=sys.stderr)
        for sym, tier in uni:
            recs = synthetic_records(sym, tier, cfg, asof, rng)
            all_recs.extend(recs)
            summaries.append(summarise(sym, recs))
    else:
        token = os.environ.get("TRADIER_TOKEN")
        if args.source == "tradier" and not token:
            print("TRADIER_TOKEN not set. Use --source cboe (no key needed),\n"
                  "--synthetic to verify the logic, or export a Tradier Lite token.\n\n"
                  + build_universe_hint(), file=sys.stderr)
            return 2
        if not args.universe:
            print("--universe required for a real run.\n\n" + build_universe_hint(),
                  file=sys.stderr)
            return 2
        with open(args.universe) as fh:
            syms = [ln.strip().upper() for ln in fh if ln.strip()
                    and not ln.startswith("#")]
        session = us_session()
        if session != "regular":
            print("WARNING: outside US regular hours (09:30-16:00 ET). Post-close\n"
                  "quotes are widened/stale; spread-% will badly overstate cost.\n"
                  "Run the census during the session (ideally 11:00-15:45 ET).",
                  file=sys.stderr)
        print(f"real run ({args.source}): {len(syms)} names", file=sys.stderr)
        for i, sym in enumerate(syms, 1):
            try:
                if args.source == "cboe":
                    recs = list(records_for_symbol_cboe(sym, cfg, asof))
                else:
                    recs = list(records_for_symbol(sym, token, cfg, asof))
            except Exception as e:                      # noqa: BLE001
                print(f"  {sym}: FAILED {type(e).__name__}: {e}", file=sys.stderr)
                recs = []
            all_recs.extend(recs)
            summaries.append(summarise(sym, recs))
            if i % 25 == 0:
                print(f"  {i}/{len(syms)}", file=sys.stderr)
            time.sleep(args.sleep)

    n = write_snapshot(snap_path, all_recs)
    print(f"snapshot: {n} contract rows -> {snap_path}", file=sys.stderr)

    if args.snapshot_only:
        return 0

    census_path = os.path.join(args.out, f"census_{stamp}.json")
    report = write_census(census_path, summaries, cfg, asof,
                          extra={"source": "synthetic" if args.synthetic else args.source,
                                 "session": "synthetic" if args.synthetic else us_session()})

    print("\n" + "=" * 62)
    print("LIQUIDITY CENSUS")
    print("=" * 62)
    print(f"  gate: spread <= {cfg.max_spread_pct:.1%} of premium, "
          f"OI >= {cfg.min_open_interest}, "
          f"DTE {cfg.min_dte}-{cfg.max_dte}, "
          f"|log(K/S)| <= {cfg.max_abs_log_moneyness}")
    print(f"  universe examined          {report['universe_size']:>8,}")
    print(f"  names clearing the gate    {report['names_passing']:>8,}   "
          f"({report['pass_rate']:.1%})")
    print(f"  names with weeklys         {report['names_with_weeklys']:>8,}")
    print(f"  contract rows seen         {report['total_contracts_seen']:>8,}")
    print(f"  contract rows passing      {report['total_contracts_passing']:>8,}")
    print("\n  top blocking reason, counted by name:")
    for k, v in list(report["top_blocking_reason_by_name"].items())[:8]:
        print(f"    {k:<24} {v:>6,}")
    print(f"\n  report:   {census_path}")
    print(f"  by-symbol {census_path.replace('.json', '_by_symbol.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
