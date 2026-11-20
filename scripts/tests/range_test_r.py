#!/usr/bin/env python3
"""
range_test_r.py -- Test R, spec R-1. FROZEN 16 November 2026. Do not edit and re-run.

Pre-registered in docs/proposals/2026-11-16-move-forecast-backbone.md, section 8.
One run. No variants. A failure is recorded and stands. This is trial 4 of ~12
under spec section 11; the run appends one line to vrp_out/TRIALS.log.

QUESTION
  On data the rule has not seen, does scaling the usual range for the
  volatility state predict the actual range better than the usual range alone?

DEFINITIONS (all fixed before the run)
  data            daily closes (split-adjusted) from label_out/prices, last 20
                  years; names with under 8 years of history are excluded
  rows            7d = 5 trading days, 14d = 10, 30d = 21  (decisive)
                  60d = 42, 90d = 63                        (reported only)
  windows         non-overlapping, per name, starting after a 1,260-day warm-up
  usual range U   68th percentile of |h-day return| over every rolling window
                  of that name that had fully ended by the start date
  state           20-day realised volatility / its 252-day median at the start
                  date: quiet < 0.8, active > 1.2, otherwise normal
  normalised move z = |actual h-day return| / U
  multiplier      for scoring year Y and state s: the 68th percentile of z over
                  all names' windows in state s that ENDED before 1 January Y
  forecasts       naive  q = 1        (the usual range)
                  scaled q = multiplier of the start-date state
  scoring period  windows starting on or after 1 January 2014
  error           quantile (pinball) loss at 0.68 on the z scale:
                  0.68*max(z-q,0) + 0.32*max(q-z,0)
  test statistic  d = loss(naive) - loss(scaled), averaged across names within
                  each calendar month of the start date; t-statistic of the
                  monthly means with a Newey-West (Bartlett, 3 lags) variance
  hit rate        share of windows with z <= q, by state

PASS (all three decisive rows)
  mean d > 0 with t > 2, AND the scaled hit rate is within 3 points of 68%
  in each of the three states.
FAIL otherwise: the state adjustment is dropped and the stage reports the
  usual range only.

Usage:  python3 range_test_r.py            (the one run)
        python3 range_test_r.py --selftest (synthetic, no files written)
"""
from __future__ import annotations

import argparse
import bisect
import datetime as dt
import json
import math
import random
import sys
from pathlib import Path

import label_frequency as L

SPEC_VERSION = "R-1"
SPEC_FROZEN_ON = "2026-11-16"
TAU = 0.68
ROWS = [("7d", 5, True), ("14d", 10, True), ("30d", 21, True), ("60d", 42, False), ("90d", 63, False)]
WARMUP = 1260
MIN_YEARS = 8
SCORE_FROM = dt.date(2014, 1, 1)
STATES = ("quiet", "normal", "active")
NW_LAGS = 3
HIT_TOL = 3.0
T_MIN = 2.0


def pct68(sorted_v: list[float]) -> float:
    return sorted_v[int(TAU * len(sorted_v))]


def loss(q: float, z: float) -> float:
    return TAU * max(z - q, 0.0) + (1 - TAU) * max(q - z, 0.0)


def records_for(dates: list[dt.date], closes: list[float], h: int) -> list[tuple]:
    """(start_date, end_date, state, z) for non-overlapping windows after warm-up."""
    n = len(closes)
    vs = L.vol_state(closes)
    absr = [abs(closes[s + h] / closes[s] - 1.0) for s in range(n - h)]
    hist: list[float] = []
    nxt = 0                                  # next rolling-window start not yet in hist
    out = []
    t = WARMUP
    while t + h < n:
        while nxt <= t - h:                  # windows that ended at or before t
            bisect.insort(hist, absr[nxt]); nxt += 1
        if vs[t] is not None and len(hist) >= 500:
            u = pct68(hist)
            if u > 0:
                out.append((dates[t], dates[t + h], vs[t], absr[t] / u))
        t += h
    return out


def nw_t(x: list[float], lags: int = NW_LAGS) -> tuple[float, float]:
    n = len(x)
    m = sum(x) / n
    e = [v - m for v in x]
    var = sum(v * v for v in e) / n
    for k in range(1, lags + 1):
        cov = sum(e[i] * e[i - k] for i in range(k, n)) / n
        var += 2 * (1 - k / (lags + 1)) * cov
    se = math.sqrt(max(var, 1e-300) / n)
    return m, m / se


def evaluate(recs: list[tuple]) -> dict:
    recs = sorted(recs, key=lambda r: r[1])                 # by end date
    years = sorted({r[0].year for r in recs if r[0] >= SCORE_FROM})
    mult: dict[int, dict[str, float]] = {}
    for y in years:
        cut = dt.date(y, 1, 1)
        mult[y] = {}
        for s in STATES:
            v = sorted(r[3] for r in recs if r[1] < cut and r[2] == s)
            mult[y][s] = pct68(v) if len(v) >= 200 else float("nan")
    by_month: dict[tuple[int, int], list[float]] = {}
    hits = {k: {s: [0, 0] for s in STATES} for k in ("naive", "scaled")}
    ln = ls = 0.0
    n = 0
    for start, _end, s, z in recs:
        if start < SCORE_FROM:
            continue
        q = mult[start.year][s]
        if q != q:                                           # nan: not enough history
            continue
        a, b = loss(1.0, z), loss(q, z)
        ln += a; ls += b; n += 1
        by_month.setdefault((start.year, start.month), []).append(a - b)
        hits["naive"][s][0] += 1; hits["naive"][s][1] += z <= 1.0
        hits["scaled"][s][0] += 1; hits["scaled"][s][1] += z <= q
    monthly = [sum(v) / len(v) for _, v in sorted(by_month.items())]
    mean_d, t = nw_t(monthly) if len(monthly) > NW_LAGS + 2 else (float("nan"), float("nan"))
    rate = lambda k, s: 100.0 * hits[k][s][1] / hits[k][s][0] if hits[k][s][0] else float("nan")  # noqa: E731
    res = {
        "windows_scored": n, "months": len(monthly),
        "loss_naive": ln / n if n else None, "loss_scaled": ls / n if n else None,
        "improvement_pct": 100.0 * (ln - ls) / ln if n and ln else None,
        "mean_monthly_d": mean_d, "t_stat": t,
        "hit_naive": {s: rate("naive", s) for s in STATES},
        "hit_scaled": {s: rate("scaled", s) for s in STATES},
        "n_by_state": {s: hits["scaled"][s][0] for s in STATES},
        "multiplier_last_year": mult[years[-1]] if years else {},
        "multiplier_first_year": mult[years[0]] if years else {},
    }
    res["error_ok"] = bool(mean_d == mean_d and mean_d > 0 and t > T_MIN)
    res["hits_ok"] = all(abs(res["hit_scaled"][s] - 100 * TAU) <= HIT_TOL for s in STATES)
    res["row_pass"] = res["error_ok"] and res["hits_ok"]
    return res


def run(series: dict[str, tuple[list[dt.date], list[float]]]) -> dict:
    out = {}
    for label, h, _dec in ROWS:
        recs = []
        for dates, closes in series.values():
            recs.extend(records_for(dates, closes, h))
        out[label] = evaluate(recs)
    out["PASS"] = all(out[l]["row_pass"] for l, _h, dec in ROWS if dec)
    return out


def show(res: dict) -> None:
    print("row   decisive  windows  months  loss naive  loss scaled  improve   t     "
          "hit rate scaled q/n/a      hit rate naive q/n/a     row")
    for label, _h, dec in ROWS:
        r = res[label]
        hs = "/".join(f"{r['hit_scaled'][s]:.1f}" for s in STATES)
        hn = "/".join(f"{r['hit_naive'][s]:.1f}" for s in STATES)
        print(f"{label:5s} {'yes' if dec else 'no ':8s} {r['windows_scored']:7d}  {r['months']:5d}   "
              f"{r['loss_naive']:.4f}      {r['loss_scaled']:.4f}     {r['improvement_pct']:+5.1f}%  {r['t_stat']:+6.2f}   "
              f"{hs:22s}   {hn:22s}  {'pass' if r['row_pass'] else 'FAIL'}"
              f"{'' if r['row_pass'] else ' (' + ', '.join(x for x, ok in (('error', r['error_ok']), ('hit rate', r['hits_ok'])) if not ok) + ')'}")
    print("multipliers (quiet/normal/active), last scoring year:")
    for label, *_ in ROWS:
        m = res[label]["multiplier_last_year"]
        print(f"  {label:5s} " + " / ".join(f"{m[s]:.2f}" for s in STATES))
    print(f"\nTEST R ({SPEC_VERSION}): {'PASS' if res['PASS'] else 'FAIL'}")


def selftest() -> int:
    random.seed(11)
    d0 = dt.date(2006, 11, 20)
    dates = [d0 + dt.timedelta(days=int(i * 365.25 / 252)) for i in range(5040)]

    def make(clustered: bool) -> dict:
        ser = {}
        for k in range(40):
            x, sig = [100.0], 0.015
            for i in range(5039):
                if clustered and i % 120 == 0:
                    sig = random.choice([0.007, 0.012, 0.02, 0.03])
                x.append(x[-1] * math.exp(random.gauss(0.0, sig)))
            ser[f"S{k}"] = (dates, x)
        return ser
    a = run(make(True)); b = run(make(False))
    show(a); print(); show(b)
    ok = (a["30d"]["error_ok"] and a["7d"]["error_ok"] and a["7d"]["improvement_pct"] > 2
          and abs(b["7d"]["improvement_pct"]) < 1.0 and not b["PASS"]
          and abs(loss(1.0, 2.0) - 0.68) < 1e-12 and abs(loss(1.0, 0.0) - 0.32) < 1e-12)
    print("\nselftest", "PASSED" if ok else "FAILED",
          "(clustered volatility must improve; constant volatility must not pass)")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    here = Path(__file__).resolve().parent
    cache = here / "label_out" / "prices"
    names = [l.strip() for l in (here / "universe.txt").read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    cutoff = dt.date.today() - dt.timedelta(days=int(365.25 * 20))
    series, skipped = {}, []
    for n in names:
        if not (cache / f"{n}.json").exists():
            skipped.append((n, "no cached prices")); continue
        ser = [(d, c) for d, c in L.fetch_closes(n, cache, False) if d >= cutoff]
        yrs = (ser[-1][0] - ser[0][0]).days / 365.25 if ser else 0
        if yrs < MIN_YEARS:
            skipped.append((n, f"{yrs:.1f} years")); continue
        series[n] = ([d for d, _ in ser], [c for _, c in ser])
    print(f"Test R, spec {SPEC_VERSION}, frozen {SPEC_FROZEN_ON}")
    print(f"names used: {len(series)}; skipped: {', '.join(f'{n} ({w})' for n, w in skipped) or 'none'}\n")
    if len(series) < 50:
        print("FATAL: fewer than 50 names with cached prices. Run label_frequency.py first."); return 2
    res = run(series)
    show(res)
    out = here / "vrp_out"
    out.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    rf = out / f"range_test_r_{stamp}.json"
    rf.write_text(json.dumps({"spec_version": SPEC_VERSION, "frozen_on": SPEC_FROZEN_ON,
                              "names": sorted(series), "skipped": skipped, "result": res}, indent=1))
    line = {"run_at": dt.datetime.now().isoformat(timespec="seconds"), "test": "R",
            "spec_version": SPEC_VERSION, "names": len(series),
            "config": {"tau": TAU, "rows_decisive": [l for l, _h, d in ROWS if d], "warmup_days": WARMUP,
                       "score_from": str(SCORE_FROM), "nw_lags": NW_LAGS, "hit_tolerance": HIT_TOL},
            "improvement_pct": {l: res[l]["improvement_pct"] for l, *_ in ROWS},
            "t_stat": {l: res[l]["t_stat"] for l, *_ in ROWS},
            "hit_scaled": {l: res[l]["hit_scaled"] for l, *_ in ROWS},
            "reading": "PASS" if res["PASS"] else "FAIL", "result_file": rf.name}
    with (out / "TRIALS.log").open("a") as f:
        f.write(json.dumps(line) + "\n")
    print(f"wrote {rf}\nappended one trial to {out}/TRIALS.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
