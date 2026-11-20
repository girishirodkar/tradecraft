#!/usr/bin/env python3
"""
Test A — is there still an index variance risk premium after May 2012?

THE SPECIFICATION IS FROZEN. It was declared before the first run, on
15 November 2026, to satisfy factor-spec.md §11: every configuration tried must
be logged from the first commit, because ~12 trials on 60 monthly observations
exhausts the zero-skill Sharpe budget and the count cannot be reconstructed
later.

  Estimator      close-to-close realised variance, no mean adjustment,
                 annualised by 252/n
  Implied        VIX close at window start, squared, annualised variance
  Windows        NON-OVERLAPPING, month-end to month-end
  Break date     2012-05-01, taken from Dew-Becker & Giglio, not chosen here
  Periods        pre-2001 / 2001-2012 / post-2012  (pre-2001 is reported only
                 to sit beside the paper's table; the decision is post-2012)
  Minimum        a month needs >= 15 trading days or it is dropped
  Statistics     mean, sd, plain t (windows are independent), 95% CI
  Forbidden      a second break date, a different vol estimator, a different
                 window length, overlapping windows with Newey-West, dropping
                 2008 or 2020, winsorising

Changing anything above means this is a new trial. Log it; do not edit silently.

SIGN CONVENTION, stated because this literature is full of sign errors:
  VRP = implied variance - realised variance.
  VRP > 0  =>  options were expensive  =>  selling premium paid.
  This is the OPPOSITE sign to the straddle Sharpe in Dew-Becker & Giglio,
  where NEGATIVE meant profitable to sell. Their -0.74 pre-2001 corresponds to
  a POSITIVE premium here.

WHAT THIS TEST CANNOT DO:
  VIX^2 - RV is the VARIANCE SWAP premium, which integrates across strikes.
  A straddle return does not. Related object, not the same one.
  Power is limited: see the minimum-detectable-Sharpe line in the output.
  A failure to reject zero is NOT evidence the premium is zero.

Usage:
  python3 vrp_test_a.py --selftest        # verify the arithmetic, no network
  python3 vrp_test_a.py --probe           # what does each data source return?
  python3 vrp_test_a.py                   # fetch and run
  python3 vrp_test_a.py --out ./vrp_out
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import math
import os
import random
import statistics as st
import sys
import urllib.error
import urllib.parse
import urllib.request

SPEC_VERSION = "A-1"
SPEC_FROZEN_ON = "2026-11-15"
BREAK_DATE = dt.date(2012, 5, 1)
EARLY_BREAK = dt.date(2001, 1, 1)
MIN_DAYS_IN_MONTH = 15
TRADING_DAYS_PER_YEAR = 252

UA = {"User-Agent": "vrp-test-a/1.0", "Accept": "text/csv,application/json,*/*"}


# ---------------------------------------------------------------------------
# Data sources. Tried in order; the first that returns a usable series wins.
# None of these could be reached from the cloud session that wrote this file,
# so the source that actually works is recorded in the output, not assumed.
# ---------------------------------------------------------------------------

# Observed 15 Nov 2026 on the operator's Mac:
#   cboe VIX_History.csv .......... WORKS (9,316 rows, 1990-01-02 onward)
#   cboe SPX_History.csv .......... WORKS, but the schema is DATE,SPX — one
#                                   value column named after the symbol, not
#                                   CLOSE. Parser handles both now.
#                                   Preferred for BOTH legs: same vendor means
#                                   the same trading-day calendar, rather than
#                                   splicing Cboe VIX against Yahoo SPX.
#                                   This choice was made from the probe, before
#                                   any result was computed.
#   stooq ......................... serves a JavaScript bot-challenge page.
#                                   Unusable from a stdlib fetcher; kept last
#                                   only so the probe reports it consistently.
#   yahoo ?range=max .............. IGNORED. Returned 169 rows (~8 months).
#                                   Use period1/period2 epochs instead; range=
#                                   is not reliable on this endpoint.
# A short series is REJECTED rather than used: running this test on 8 months
# of data would produce a number, and that number would be meaningless.

_YF = ("https://query{host}.finance.yahoo.com/v8/finance/chart/{sym}"
       "?period1=0&period2=9999999999&interval=1d")

SOURCES = {
    "VIX": [
        ("cboe", "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"),
        ("yahoo1", _YF.format(host=1, sym="%5EVIX")),
        ("yahoo2", _YF.format(host=2, sym="%5EVIX")),
        ("stooq", "https://stooq.com/q/d/l/?s=%5Evix&i=d"),
    ],
    "SPX": [
        ("cboe", "https://cdn.cboe.com/api/global/us_indices/daily_prices/SPX_History.csv"),
        ("yahoo1", _YF.format(host=1, sym="%5EGSPC")),
        ("yahoo2", _YF.format(host=2, sym="%5EGSPC")),
        # SPY is a documented fallback, not an equivalent: it is total-return,
        # so four ex-dividend gaps a year inflate close-to-close realised
        # variance by roughly 0.3% relative. That biases VRP DOWNWARD, i.e.
        # against finding a premium, so it is the safe direction to be wrong in.
        # The output records which source was used; if it says spy, say so.
        ("yahoo1_spy", _YF.format(host=1, sym="SPY")),
        ("stooq", "https://stooq.com/q/d/l/?s=%5Espx&i=d"),
    ],
}

# 1990-2026 is ~9,000 trading days. Anything under this is a truncated
# response, not a short history, and must not be used.
MIN_ROWS = 2000


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _parse_csv_close(blob: bytes) -> dict[dt.date, float]:
    """
    Accept any CSV with a date-ish first column and one value column.

    Cboe is not consistent between series. Observed 15 Nov 2026:
      VIX_History.csv -> DATE,OPEN,HIGH,LOW,CLOSE
      SPX_History.csv -> DATE,SPX          <- one column, named after the symbol
    So: prefer an explicit CLOSE-like column; failing that, if the file has
    exactly two columns, the second one is the level.
    """
    text = blob.decode("utf-8-sig", errors="replace")
    rdr = csv.reader(io.StringIO(text))
    rows = [r for r in rdr if r and any(c.strip() for c in r)]
    if not rows:
        raise ValueError("empty csv")
    header = [c.strip().upper() for c in rows[0]]
    ci = next((i for i, c in enumerate(header)
               if c in ("CLOSE", "ADJ CLOSE", "CLOSE/LAST")), None)
    if ci is None and len(header) == 2:
        ci = 1
    if ci is None:
        raise ValueError(f"no CLOSE column and not a two-column file: {header}")
    out: dict[dt.date, float] = {}
    for r in rows[1:]:
        if len(r) <= ci:
            continue
        d = _parse_date(r[0].strip())
        if d is None:
            continue
        try:
            v = float(r[ci].strip().replace(",", ""))
        except ValueError:
            continue
        if v > 0:
            out[d] = v
    return out


def _parse_date(s: str) -> dt.date | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_yahoo(blob: bytes) -> dict[dt.date, float]:
    d = json.loads(blob.decode("utf-8"))
    res = d["chart"]["result"][0]
    ts = res["timestamp"]
    closes = res["indicators"]["quote"][0]["close"]
    out: dict[dt.date, float] = {}
    for t, c in zip(ts, closes):
        if c is None:
            continue
        out[dt.datetime.utcfromtimestamp(t).date()] = float(c)
    return out


def fetch_series(name: str) -> tuple[dict[dt.date, float], str, list[str]]:
    notes = []
    for label, url in SOURCES[name]:
        try:
            blob = _get(url)
            series = (_parse_yahoo(blob) if label.startswith("yahoo")
                      else _parse_csv_close(blob))
            if len(series) < MIN_ROWS:
                notes.append(f"{label}: only {len(series)} rows, need >={MIN_ROWS} "
                             f"for a 1990-2026 sample — truncated response, rejected")
                continue
            notes.append(f"{label}: {len(series)} rows, accepted")
            return series, label, notes
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError,
                KeyError, json.JSONDecodeError, OSError) as e:
            notes.append(f"{label}: {type(e).__name__}: {e}")
    raise SystemExit(
        f"FATAL: no source returned a usable {name} series.\n  "
        + "\n  ".join(notes)
        + "\n\nAll three were unreachable from the cloud session that wrote this\n"
          "script. If they are unreachable here too, the endpoints have moved:\n"
          "find a free daily close series and add it to SOURCES."
    )


# ---------------------------------------------------------------------------
# The measurement
# ---------------------------------------------------------------------------

def month_ends(dates: list[dt.date]) -> list[dt.date]:
    last: dict[tuple[int, int], dt.date] = {}
    for d in dates:
        last[(d.year, d.month)] = d          # dates arrive sorted
    return [last[k] for k in sorted(last)]


def realised_variance(closes: list[float]) -> float:
    """Annualised close-to-close realised variance. No mean adjustment."""
    if len(closes) < 2:
        return float("nan")
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    return TRADING_DAYS_PER_YEAR * sum(r * r for r in rets) / len(rets)


def build_observations(spx: dict[dt.date, float], vix: dict[dt.date, float]) -> list[dict]:
    common = sorted(set(spx) & set(vix))
    if len(common) < 500:
        raise SystemExit(f"FATAL: only {len(common)} overlapping dates between SPX and VIX")
    me = month_ends(common)
    idx = {d: i for i, d in enumerate(common)}
    obs = []
    for a, b in zip(me, me[1:]):
        window = common[idx[a]: idx[b] + 1]          # inclusive both ends
        n_rets = len(window) - 1
        if n_rets < MIN_DAYS_IN_MONTH:
            continue
        iv = (vix[a] / 100.0) ** 2
        rv = realised_variance([spx[d] for d in window])
        obs.append({
            "start": a.isoformat(), "end": b.isoformat(), "n_returns": n_rets,
            "vix": round(vix[a], 4),
            "implied_var": iv, "realised_var": rv, "vrp_var": iv - rv,
            "implied_vol_pts": 100 * math.sqrt(iv),
            "realised_vol_pts": 100 * math.sqrt(rv),
            "vrp_vol_pts": 100 * (math.sqrt(iv) - math.sqrt(rv)),
        })
    return obs


def summarise(obs: list[dict], label: str) -> dict:
    if len(obs) < 3:
        return {"period": label, "n": len(obs), "note": "too few observations"}
    x = [o["vrp_var"] for o in obs]
    v = [o["vrp_vol_pts"] for o in obs]
    n = len(x)
    mean, sd = st.mean(x), st.stdev(x)
    se = sd / math.sqrt(n)
    t = mean / se if se else float("nan")
    # Monthly observations -> annualise the ratio by sqrt(12). This is the
    # Sharpe of a short-variance position whose P&L is VRP, and it is NOT the
    # paper's straddle Sharpe: different instrument, and opposite sign.
    sharpe_ann = (mean / sd) * math.sqrt(12) if sd else float("nan")
    mds = 2.0 / math.sqrt(n / 12.0)          # Sharpe detectable at |t| ~ 2
    return {
        "period": label,
        "n": n,
        "first": obs[0]["start"], "last": obs[-1]["end"],
        "mean_vrp_variance": mean,
        "sd_vrp_variance": sd,
        "t_stat": t,
        "ci95_variance": [mean - 1.96 * se, mean + 1.96 * se],
        "mean_vrp_vol_points": st.mean(v),
        "median_vrp_vol_points": st.median(v),
        "share_months_positive": sum(1 for y in x if y > 0) / n,
        "short_variance_sharpe_annualised": sharpe_ann,
        "min_detectable_sharpe_at_t2": mds,
        "worst_month_vrp_vol_points": min(v),
    }


# ---------------------------------------------------------------------------
# Self-test: verify the arithmetic against data with a premium put in by hand.
# ---------------------------------------------------------------------------

def selftest() -> int:
    rng = random.Random(20261115)
    print("Self-test: generating 40 years of daily data with a KNOWN premium.")
    print("  pre-2012 : implied vol set 3.0 vol points above realised")
    print("  post-2012: implied vol set 0.0 vol points above realised\n")

    spx: dict[dt.date, float] = {}
    vix: dict[dt.date, float] = {}
    px = 300.0
    d = dt.date(1986, 1, 1)
    end = dt.date(2026, 10, 31)
    # true realised vol, slowly varying so months differ
    while d <= end:
        if d.weekday() < 5:
            true_vol = 0.13 + 0.05 * math.sin(d.toordinal() / 400.0)
            px *= math.exp(rng.gauss(0.0, true_vol / math.sqrt(252)))
            spx[d] = px
            premium_pts = 3.0 if d < BREAK_DATE else 0.0
            vix[d] = 100 * true_vol + premium_pts
        d += dt.timedelta(days=1)

    obs = build_observations(spx, vix)
    pre = summarise([o for o in obs if o["start"] < BREAK_DATE.isoformat()], "pre-break")
    post = summarise([o for o in obs if o["start"] >= BREAK_DATE.isoformat()], "post-break")

    ok = True
    for s, target, tol in ((pre, 3.0, 0.6), (post, 0.0, 0.6)):
        got = s["mean_vrp_vol_points"]
        good = abs(got - target) < tol
        ok &= good
        print(f"  {s['period']:10s} n={s['n']:4d}  "
              f"mean VRP {got:+.2f} vol pts (planted {target:+.1f})  "
              f"{'PASS' if good else 'FAIL'}")

    print(f"\n  sign check: pre-break t = {pre['t_stat']:+.2f} "
          f"(must be positive — premium present)  "
          f"{'PASS' if pre['t_stat'] > 0 else 'FAIL'}")
    ok &= pre["t_stat"] > 0

    # Realised variance against a closed-form case.
    flat = [100.0 * math.exp(0.01 * i) for i in range(253)]
    rv = realised_variance(flat)
    good = abs(rv - 252 * 0.0001) < 1e-9
    ok &= good
    print(f"  RV on a constant-return path: {rv:.6f}, expected {252*0.0001:.6f}  "
          f"{'PASS' if good else 'FAIL'}")

    print("\n" + ("SELF-TEST PASSED — the estimator recovers a planted premium."
                  if ok else "SELF-TEST FAILED — do not trust real output."))
    return 0 if ok else 1


# ---------------------------------------------------------------------------

def probe() -> int:
    """Diagnose every source without running the test. One command, no guessing."""
    print("Probing data sources. A source is usable only if it returns "
          f">={MIN_ROWS} rows.\n")
    worst = 0
    for name in ("VIX", "SPX"):
        print(f"{name}:")
        for label, url in SOURCES[name]:
            try:
                blob = _get(url)
                series = (_parse_yahoo(blob) if label.startswith("yahoo")
                          else _parse_csv_close(blob))
                n = len(series)
                verdict = "USABLE" if n >= MIN_ROWS else f"TOO SHORT (need {MIN_ROWS})"
                print(f"   {label:12s} {n:>6} rows  {min(series)} to {max(series)}  {verdict}")
            except Exception as e:
                msg = str(e).replace("\n", " ")[:90]
                print(f"   {label:12s}   ---   {type(e).__name__}: {msg}")
        print()
    return worst


def fmt(s: dict) -> str:
    if s.get("note"):
        return f"  {s['period']:14s} {s['note']}\n"
    return (
        f"  {s['period']:14s} n={s['n']:4d}  {s['first']} to {s['last']}\n"
        f"      mean VRP        {s['mean_vrp_vol_points']:+7.3f} vol points   "
        f"(median {s['median_vrp_vol_points']:+.3f})\n"
        f"      in variance     {s['mean_vrp_variance']:+.6f}   "
        f"95% CI [{s['ci95_variance'][0]:+.6f}, {s['ci95_variance'][1]:+.6f}]\n"
        f"      t-statistic     {s['t_stat']:+7.2f}"
        f"{'   (|t|>2)' if abs(s['t_stat']) > 2 else '   (not significant)'}\n"
        f"      months positive {100*s['share_months_positive']:5.1f}%\n"
        f"      short-var Sharpe{s['short_variance_sharpe_annualised']:+7.2f} annualised; "
        f"this sample can only detect |Sharpe| > {s['min_detectable_sharpe_at_t2']:.2f}\n"
        f"      worst month     {s['worst_month_vrp_vol_points']:+7.2f} vol points\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="verify the arithmetic on planted data; no network")
    ap.add_argument("--probe", action="store_true",
                    help="report what each data source returns, then stop")
    ap.add_argument("--out", default="./vrp_out")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.probe:
        return probe()

    print(f"Test A — index variance risk premium.  spec {SPEC_VERSION}, "
          f"frozen {SPEC_FROZEN_ON}\n")

    vix, vix_src, vix_notes = fetch_series("VIX")
    spx, spx_src, spx_notes = fetch_series("SPX")
    for n in vix_notes + spx_notes:
        print(f"  source note: {n}")
    print(f"  VIX from {vix_src}: {len(vix)} days, {min(vix)} to {max(vix)}")
    print(f"  SPX from {spx_src}: {len(spx)} days, {min(spx)} to {max(spx)}\n")

    obs = build_observations(spx, vix)
    periods = [
        ("pre-2001", [o for o in obs if o["start"] < EARLY_BREAK.isoformat()]),
        ("2001-2012", [o for o in obs if EARLY_BREAK.isoformat() <= o["start"] < BREAK_DATE.isoformat()]),
        ("post-2012", [o for o in obs if o["start"] >= BREAK_DATE.isoformat()]),
        ("full sample", obs),
    ]
    summaries = [summarise(o, lbl) for lbl, o in periods]

    print(f"{len(obs)} non-overlapping monthly observations "
          f"({obs[0]['start']} to {obs[-1]['end']})\n")
    print("VRP > 0 means options were expensive, i.e. selling premium paid.")
    print("This is the OPPOSITE sign to Dew-Becker & Giglio's straddle Sharpe.\n")
    for s in summaries:
        print(fmt(s))

    post = next(s for s in summaries if s["period"] == "post-2012")
    pre = next(s for s in summaries if s["period"] == "2001-2012")
    gate = (post.get("mean_vrp_variance", 0) > 0
            and pre.get("mean_vrp_variance", 1) > 0
            and post["mean_vrp_variance"] >= 0.5 * pre["mean_vrp_variance"])
    print("PRE-REGISTERED GATE (declared 15 Nov 2026, before the first run):")
    print("  Run Test B only if post-2012 mean VRP is positive AND at least")
    print("  half the 2001-2012 value.")
    print(f"  => {'CLEARED: Test B is justified.' if gate else 'NOT CLEARED: do not run Test B. Defined-risk structures only.'}\n")

    os.makedirs(args.out, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "spec_version": SPEC_VERSION, "spec_frozen_on": SPEC_FROZEN_ON,
        "run_at": dt.datetime.now().isoformat(timespec="seconds"),
        "sources": {"vix": vix_src, "spx": spx_src},
        "source_notes": vix_notes + spx_notes,
        "config": {
            "break_date": BREAK_DATE.isoformat(), "early_break": EARLY_BREAK.isoformat(),
            "min_days_in_month": MIN_DAYS_IN_MONTH,
            "trading_days_per_year": TRADING_DAYS_PER_YEAR,
            "estimator": "close-to-close RV, no mean adjustment",
            "windows": "non-overlapping month-end to month-end",
        },
        "n_observations": len(obs),
        "summaries": summaries,
        "gate_cleared": gate,
        "observations": obs,
    }
    res = os.path.join(args.out, f"vrp_test_a_{stamp}.json")
    with open(res, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    # §11: the trial count cannot be reconstructed later. Append-only.
    trials = os.path.join(args.out, "TRIALS.log")
    with open(trials, "a") as f:
        f.write(json.dumps({
            "run_at": payload["run_at"], "test": "A", "spec_version": SPEC_VERSION,
            "config": payload["config"], "n": len(obs),
            "post2012_mean_vrp_vol_points": post.get("mean_vrp_vol_points"),
            "post2012_t": post.get("t_stat"), "gate_cleared": gate,
            "result_file": os.path.basename(res),
        }) + "\n")

    print(f"wrote {res}")
    print(f"appended one trial to {trials}  (§11: never delete this file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
