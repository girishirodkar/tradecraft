#!/usr/bin/env python3
"""
Test B — did WRITING index options still pay after May 2012, at real prices?

Test A showed the surface-wide variance premium is intact but gross and
untradeable. This test uses Cboe's BXM (buy-write) and PUT (put-write) indices,
which are built from actually transacted S&P 500 option prices, in the two
structures factor-spec.md §5c marks as supported.

THE SPECIFICATION IS FROZEN. Declared 15 November 2026, before the first run
(factor-spec.md §11).

  Returns        NON-OVERLAPPING calendar-month returns, month-end to month-end
  Benchmark      S&P 500 TOTAL RETURN. BXM and PUT are total-return indices;
                 comparing them with the price index would plant a ~1.5-2%/yr
                 dividend bias, the same size as the effect. If no total-return
                 series can be fetched the script STOPS. It never falls back
                 to the price index.
  Risk-free      13-week T-bill yield at window start, accrued over the window.
                 Required: with beta near 0.6, omitting it biases alpha by
                 0.4 x rf, up to ~2%/yr, and differently in each period.
  Measurement    OLS of strategy excess return on market excess return, per
                 period. Alpha, annualised, is the measurement. It removes the
                 average equity exposure, so a bull market cannot make a
                 premium look absent and a bear market cannot make it look
                 present.
  Break date     2012-05-01, from Dew-Becker & Giglio, not chosen here
  Periods        pre-2001 / 2001-2012 / post-2012 / full sample
  Both indices   BXM and PUT are BOTH reported. Neither is picked afterwards.
  Forbidden      another break date, another benchmark, adding factors,
                 dropping 2008 or 2020, winsorising, daily or overlapping data

PRE-REGISTERED READING of the post-2012 alphas:
  both positive, at least one with |t| > 2 ... the tradeable premium survived
  both positive, neither significant ......... survived as a point estimate;
                                               size against costs decides
  mixed signs ................................ unresolved
  both zero or negative ...................... it did not survive in tradeable
                                               form; defined-risk only

KNOWN LIMITS, stated before the result:
  1. A covered call is a CONCAVE payoff, and CAPM alpha is biased UPWARD for
     concave payoffs. A small positive alpha is weaker evidence than it looks.
  2. The regression removes AVERAGE equity exposure. The option's delta moves
     through the month; that timing component stays in the residual as noise.
  3. BXM and PUT write one-month at-the-money options once a month. Mode 1's
     42-90 DTE out-of-the-money programme is a different implementation.
  4. Index prices are institutional executions with no commission.

Usage:
  python3 vrp_test_b.py --selftest
  python3 vrp_test_b.py --probe
  python3 vrp_test_b.py
"""

from __future__ import annotations

import argparse
import bisect
import datetime as dt
import json
import math
import os
import random
import statistics as st
import sys

from vrp_test_a import (_get, _parse_csv_close, _parse_yahoo, month_ends,
                        MIN_ROWS, BREAK_DATE, EARLY_BREAK)

SPEC_VERSION = "B-1"
SPEC_FROZEN_ON = "2026-11-15"

_CBOE = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{}_History.csv"
_YF = ("https://query{host}.finance.yahoo.com/v8/finance/chart/{sym}"
       "?period1=0&period2=9999999999&interval=1d")

SOURCES = {
    "BXM": [("cboe", _CBOE.format("BXM")),
            ("yahoo1", _YF.format(host=1, sym="%5EBXM")),
            ("yahoo2", _YF.format(host=2, sym="%5EBXM"))],
    "PUT": [("cboe", _CBOE.format("PUT")),
            ("yahoo1", _YF.format(host=1, sym="%5EPUT")),
            ("yahoo2", _YF.format(host=2, sym="%5EPUT"))],
    # Total return ONLY. No price-index entry belongs in this list.
    "SPTR": [("yahoo1", _YF.format(host=1, sym="%5ESP500TR")),
             ("yahoo2", _YF.format(host=2, sym="%5ESP500TR")),
             ("cboe", _CBOE.format("SPTR"))],
    # 13-week T-bill yield, percent, annualised.
    "RF": [("yahoo1", _YF.format(host=1, sym="%5EIRX")),
           ("yahoo2", _YF.format(host=2, sym="%5EIRX"))],
}


def _fetch_one(label: str, url: str) -> dict:
    blob = _get(url)
    return _parse_yahoo(blob) if label.startswith("yahoo") else _parse_csv_close(blob)


def fetch(name: str) -> tuple[dict, str, list[str]]:
    notes = []
    for label, url in SOURCES[name]:
        try:
            s = _fetch_one(label, url)
            if len(s) < MIN_ROWS:
                notes.append(f"{name}/{label}: only {len(s)} rows, rejected")
                continue
            notes.append(f"{name}/{label}: {len(s)} rows, accepted")
            return s, label, notes
        except Exception as e:
            notes.append(f"{name}/{label}: {type(e).__name__}: {str(e)[:80]}")
    extra = ("\nThe benchmark must be TOTAL RETURN. Do not add the price index "
             "to make this run.") if name == "SPTR" else ""
    raise SystemExit(f"FATAL: no usable {name} series.\n  " + "\n  ".join(notes) + extra)


def probe() -> int:
    print(f"Probing sources. Usable means >= {MIN_ROWS} rows.\n")
    for name in SOURCES:
        print(f"{name}:")
        for label, url in SOURCES[name]:
            try:
                s = _fetch_one(label, url)
                v = "USABLE" if len(s) >= MIN_ROWS else "TOO SHORT"
                print(f"   {label:8s} {len(s):>6} rows  {min(s)} to {max(s)}  {v}")
            except Exception as e:
                print(f"   {label:8s}   ---   {type(e).__name__}: {str(e)[:80]}")
        print()
    return 0


# ---------------------------------------------------------------------------

def build_returns(bxm, put, sptr, rf) -> list[dict]:
    common = sorted(set(bxm) & set(put) & set(sptr))
    if len(common) < MIN_ROWS:
        raise SystemExit(f"FATAL: only {len(common)} dates common to BXM, PUT and SPTR")
    rf_dates = sorted(rf)
    me = month_ends(common)
    out = []
    for a, b in zip(me, me[1:]):
        i = bisect.bisect_right(rf_dates, a) - 1
        if i < 0 or (a - rf_dates[i]).days > 10:
            continue                      # no T-bill quote near the window start
        r_f = rf[rf_dates[i]] / 100.0 * (b - a).days / 360.0
        out.append({
            "start": a.isoformat(), "end": b.isoformat(), "rf": r_f,
            "mkt_x": sptr[b] / sptr[a] - 1 - r_f,
            "bxm_x": bxm[b] / bxm[a] - 1 - r_f,
            "put_x": put[b] / put[a] - 1 - r_f,
        })
    return out


def ols(y: list[float], x: list[float]) -> dict:
    n = len(y)
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((v - mx) ** 2 for v in x)
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx
    alpha = my - beta * mx
    ssr = sum((b - alpha - beta * a) ** 2 for a, b in zip(x, y))
    s2 = ssr / (n - 2)
    se_a = math.sqrt(s2 * (1.0 / n + mx * mx / sxx))
    return {"n": n, "alpha_m": alpha, "beta": beta, "se_alpha_m": se_a,
            "t_alpha": alpha / se_a if se_a else float("nan")}


def summarise(rows: list[dict], label: str) -> dict:
    if len(rows) < 24:
        return {"period": label, "n": len(rows), "note": "too few observations"}
    x = [r["mkt_x"] for r in rows]
    out = {"period": label, "n": len(rows),
           "first": rows[0]["start"], "last": rows[-1]["end"]}
    for key in ("bxm", "put"):
        y = [r[f"{key}_x"] for r in rows]
        o = ols(y, x)
        out[key] = {
            "alpha_pct_per_year": 1200 * o["alpha_m"],
            "ci95_pct_per_year": [1200 * (o["alpha_m"] - 1.96 * o["se_alpha_m"]),
                                  1200 * (o["alpha_m"] + 1.96 * o["se_alpha_m"])],
            "t_alpha": o["t_alpha"], "beta": o["beta"],
            "min_detectable_alpha_pct_per_year": 1200 * 2 * o["se_alpha_m"],
            # descriptive only — NOT the measurement
            "excess_return_pct_per_year": 1200 * st.mean(y),
            "vol_pct_per_year": 100 * st.stdev(y) * math.sqrt(12),
            "worst_month_pct": 100 * min(y),
        }
    out["market"] = {"excess_return_pct_per_year": 1200 * st.mean(x),
                     "vol_pct_per_year": 100 * st.stdev(x) * math.sqrt(12),
                     "worst_month_pct": 100 * min(x)}
    return out


def reading(post: dict) -> str:
    a, b = post["bxm"], post["put"]
    pos = [v["alpha_pct_per_year"] > 0 for v in (a, b)]
    sig = [abs(v["t_alpha"]) > 2 and v["alpha_pct_per_year"] > 0 for v in (a, b)]
    if all(pos) and any(sig):
        return "SURVIVED: both alphas positive, at least one significant."
    if all(pos):
        return ("SURVIVED AS A POINT ESTIMATE: both positive, neither significant. "
                "Size against costs decides.")
    if any(pos):
        return "UNRESOLVED: the two indices disagree in sign."
    return ("DID NOT SURVIVE in tradeable form: both alphas zero or negative. "
            "Defined-risk only.")


# ---------------------------------------------------------------------------

def selftest() -> int:
    rng = random.Random(20261115)
    print("Self-test: strategy = rf + 0.6 x market excess + planted alpha + noise")
    print("  planted alpha: +3.6%/yr before the break, 0.0%/yr after\n")
    bxm, put, sptr, rf = {}, {}, {}, {}
    lb = lp = lm = 100.0
    d = dt.date(1988, 1, 1)
    while d <= dt.date(2026, 10, 31):
        if d.weekday() < 5:
            y = 4.0 if d < BREAK_DATE else 1.5          # T-bill yield, percent
            rfd = y / 100 / 252
            m = rng.gauss(0.06 / 252, 0.16 / math.sqrt(252))
            a = (0.036 if d < BREAK_DATE else 0.0) / 252
            lm *= 1 + rfd + m
            lb *= 1 + rfd + 0.6 * m + a + rng.gauss(0, 0.002)
            lp *= 1 + rfd + 0.55 * m + a + rng.gauss(0, 0.002)
            sptr[d], bxm[d], put[d], rf[d] = lm, lb, lp, y
        d += dt.timedelta(days=1)
    rows = build_returns(bxm, put, sptr, rf)
    cut = BREAK_DATE.isoformat()
    pre = summarise([r for r in rows if r["start"] < cut], "pre")
    post = summarise([r for r in rows if r["start"] >= cut], "post")
    ok = True
    for s, target in ((pre, 3.6), (post, 0.0)):
        for k, bt in (("bxm", 0.6), ("put", 0.55)):
            v = s[k]
            good = (abs(v["alpha_pct_per_year"] - target) < 2.2 * v["min_detectable_alpha_pct_per_year"] / 2
                    and abs(v["beta"] - bt) < 0.05)
            ok &= good
            print(f"  {s['period']:4s} {k.upper()}  alpha {v['alpha_pct_per_year']:+5.2f}%/yr "
                  f"(planted {target:+.1f})  beta {v['beta']:.3f} (planted {bt})  "
                  f"{'PASS' if good else 'FAIL'}")
    o = ols([1 + 2 * v for v in (0.1, -0.2, 0.3, 0.05)], [0.1, -0.2, 0.3, 0.05])
    good = abs(o["alpha_m"] - 1) < 1e-9 and abs(o["beta"] - 2) < 1e-9
    ok &= good
    print(f"  OLS on an exact line: alpha {o['alpha_m']:.6f}, beta {o['beta']:.6f}  "
          f"{'PASS' if good else 'FAIL'}")
    print("\n" + ("SELF-TEST PASSED" if ok else "SELF-TEST FAILED — do not trust real output."))
    return 0 if ok else 1


def fmt(s: dict) -> str:
    if s.get("note"):
        return f"  {s['period']:12s} {s['note']}\n"
    lines = [f"  {s['period']:12s} n={s['n']:4d}  {s['first']} to {s['last']}"]
    for k in ("bxm", "put"):
        v = s[k]
        lines.append(
            f"      {k.upper()}  alpha {v['alpha_pct_per_year']:+6.2f}%/yr  "
            f"CI [{v['ci95_pct_per_year'][0]:+.2f}, {v['ci95_pct_per_year'][1]:+.2f}]  "
            f"t={v['t_alpha']:+.2f}  beta {v['beta']:.2f}  "
            f"(detectable > {v['min_detectable_alpha_pct_per_year']:.2f}%/yr)")
    m = s["market"]
    lines.append("      descriptive only, not the measurement:")
    for k, v in (("BXM", s["bxm"]), ("PUT", s["put"]), ("S&P TR", m)):
        lines.append(f"        {k:6s} excess {v['excess_return_pct_per_year']:+6.2f}%/yr  "
                     f"vol {v['vol_pct_per_year']:5.2f}%  worst month {v['worst_month_pct']:+6.2f}%")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--out", default="./vrp_out")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.probe:
        return probe()

    print(f"Test B — did writing index options pay?  spec {SPEC_VERSION}, "
          f"frozen {SPEC_FROZEN_ON}\n")
    data, used, notes = {}, {}, []
    for name in ("BXM", "PUT", "SPTR", "RF"):
        data[name], used[name], n = fetch(name)
        notes += n
        print(f"  {name:4s} from {used[name]}: {len(data[name])} days, "
              f"{min(data[name])} to {max(data[name])}")
    rows = build_returns(data["BXM"], data["PUT"], data["SPTR"], data["RF"])
    print(f"\n{len(rows)} non-overlapping monthly returns "
          f"({rows[0]['start']} to {rows[-1]['end']})\n")
    print("Alpha is the return left after removing average equity exposure.")
    print("Positive alpha means writing the options added return.\n")

    e, c = EARLY_BREAK.isoformat(), BREAK_DATE.isoformat()
    periods = [("pre-2001", [r for r in rows if r["start"] < e]),
               ("2001-2012", [r for r in rows if e <= r["start"] < c]),
               ("post-2012", [r for r in rows if r["start"] >= c]),
               ("full sample", rows)]
    summaries = [summarise(r, lbl) for lbl, r in periods]
    for s in summaries:
        print(fmt(s))
    post = next(s for s in summaries if s["period"] == "post-2012")
    verdict = reading(post)
    print("PRE-REGISTERED READING (declared 15 Nov 2026, before the first run):")
    print(f"  => {verdict}")
    print("  Remember: CAPM alpha is biased UPWARD for a concave payoff.\n")

    os.makedirs(args.out, exist_ok=True)
    now = dt.datetime.now()
    payload = {"spec_version": SPEC_VERSION, "spec_frozen_on": SPEC_FROZEN_ON,
               "run_at": now.isoformat(timespec="seconds"), "sources": used,
               "source_notes": notes, "n_observations": len(rows),
               "summaries": summaries, "reading": verdict, "returns": rows}
    res = os.path.join(args.out, f"vrp_test_b_{now.strftime('%Y%m%d_%H%M%S')}.json")
    with open(res, "w") as f:
        json.dump(payload, f, indent=2)
    with open(os.path.join(args.out, "TRIALS.log"), "a") as f:
        f.write(json.dumps({
            "run_at": payload["run_at"], "test": "B", "spec_version": SPEC_VERSION,
            "sources": used, "n": len(rows),
            "post2012_bxm_alpha_pct_yr": post["bxm"]["alpha_pct_per_year"],
            "post2012_put_alpha_pct_yr": post["put"]["alpha_pct_per_year"],
            "reading": verdict, "result_file": os.path.basename(res)}) + "\n")
    print(f"wrote {res}\nappended one trial to {args.out}/TRIALS.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
