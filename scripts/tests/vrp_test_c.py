#!/usr/bin/env python3
"""
Test C — did OUT-OF-THE-MONEY and DEFINED-RISK index writing pay after May 2012?

Test A: the surface-wide variance premium is intact (gross).
Test B: one-month AT-THE-MONEY writing earned no alpha after 2012.
Neither covers what Mode 1 actually proposes: out-of-the-money writing, and the
defined-risk structures that Test B's reading left as the only permitted branch.

THE SPECIFICATION IS FROZEN. Declared 15 November 2026, before the first run.
This is trial 3 against the factor-spec.md §11 budget.

  Indices        BXY   Cboe S&P 500 2% OTM BuyWrite
                 BXMD  Cboe S&P 500 30-Delta BuyWrite
                 CNDR  Cboe S&P 500 Iron Condor
                 All three are reported. None is dropped or added afterwards.
  Method         Identical to Test B: monthly CAPM alpha against the S&P 500
                 TOTAL RETURN index, net of the 13-week T-bill.
  Sample         Each index uses its own common dates with the benchmark.
                 A window needs >= 15 common trading days (this also removes
                 the partial final month that Test B let through).
  Break date     2012-05-01. Only the post-2012 alpha feeds the reading.
  Forbidden      as Test B, plus: swapping in another Cboe index after seeing
                 the result.

PRE-REGISTERED READING of the post-2012 alphas:

  OTM overwriting (BXY and BXMD together)
    both positive, at least one |t| > 2 .. restored to the Mode 1 menu
    both positive, neither significant ... point estimate only; stays
                                           "de-risking only"
    anything else ........................ no alpha out of the money either
    either index unavailable ............. INCOMPLETE, no change to the spec

  Defined-risk short premium (CNDR)
    positive, |t| > 2 .................... evidenced edge
    positive, not significant ............ permitted as a structure, with NO
                                           edge claim
    zero or negative ..................... no evidenced edge; Mode 1 has no
                                           supported premium-harvesting leg

MULTIPLE COMPARISONS, stated before the result: three indices each have a ~2.5%
chance of a spurious t > +2. That is why the overwriting branch needs BOTH
indices positive, and why a lone significant CNDR should be read as roughly a
1-in-13 event under no skill across this test, not 1-in-40.

LIMITS: CAPM alpha is biased upward for concave payoffs (BXY, BXMD). An iron
condor's risk is not equity beta at all, so a near-zero beta does not mean low
risk: look at its worst month. These are monthly 1-month programmes, still not
Mode 1's 42-90 DTE.

Usage:  --selftest | --probe | (no flag: run)
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

from vrp_test_a import month_ends, MIN_ROWS, BREAK_DATE
from vrp_test_b import _fetch_one, ols, _CBOE, _YF, SOURCES as B_SOURCES

SPEC_VERSION = "C-1"
SPEC_FROZEN_ON = "2026-11-15"
MIN_DAYS = 15
INDICES = ("BXY", "BXMD", "CNDR")

SOURCES = {k: [("cboe", _CBOE.format(k)),
               ("yahoo1", _YF.format(host=1, sym="%5E" + k)),
               ("yahoo2", _YF.format(host=2, sym="%5E" + k))] for k in INDICES}
SOURCES["SPTR"] = B_SOURCES["SPTR"]
SOURCES["RF"] = B_SOURCES["RF"]


def fetch(name: str):
    notes = []
    for label, url in SOURCES[name]:
        try:
            s = _fetch_one(label, url)
            if len(s) < MIN_ROWS:
                notes.append(f"{name}/{label}: only {len(s)} rows, rejected")
                continue
            return s, label, notes
        except Exception as e:
            notes.append(f"{name}/{label}: {type(e).__name__}: {str(e)[:70]}")
    return None, None, notes


def probe() -> int:
    for name in SOURCES:
        print(f"{name}:")
        for label, url in SOURCES[name]:
            try:
                s = _fetch_one(label, url)
                v = "USABLE" if len(s) >= MIN_ROWS else "TOO SHORT"
                print(f"   {label:8s} {len(s):>6} rows  {min(s)} to {max(s)}  {v}")
            except Exception as e:
                print(f"   {label:8s}   ---   {type(e).__name__}: {str(e)[:70]}")
        print()
    return 0


def monthly(idx: dict, sptr: dict, rf: dict) -> list[dict]:
    common = sorted(set(idx) & set(sptr))
    pos = {d: i for i, d in enumerate(common)}
    rf_dates = sorted(rf)
    out = []
    me = month_ends(common)
    for a, b in zip(me, me[1:]):
        if pos[b] - pos[a] < MIN_DAYS:
            continue
        i = bisect.bisect_right(rf_dates, a) - 1
        if i < 0 or (a - rf_dates[i]).days > 10:
            continue
        r_f = rf[rf_dates[i]] / 100.0 * (b - a).days / 360.0
        out.append({"start": a.isoformat(), "end": b.isoformat(),
                    "mkt_x": sptr[b] / sptr[a] - 1 - r_f,
                    "idx_x": idx[b] / idx[a] - 1 - r_f})
    return out


def measure(rows: list[dict]) -> dict | None:
    if len(rows) < 24:
        return None
    x = [r["mkt_x"] for r in rows]
    y = [r["idx_x"] for r in rows]
    o = ols(y, x)
    return {"n": len(rows), "first": rows[0]["start"], "last": rows[-1]["end"],
            "alpha_pct_per_year": 1200 * o["alpha_m"],
            "ci95": [1200 * (o["alpha_m"] - 1.96 * o["se_alpha_m"]),
                     1200 * (o["alpha_m"] + 1.96 * o["se_alpha_m"])],
            "t_alpha": o["t_alpha"], "beta": o["beta"],
            "detectable_pct_per_year": 2400 * o["se_alpha_m"],
            "excess_pct_per_year": 1200 * st.mean(y),
            "vol_pct_per_year": 100 * st.stdev(y) * math.sqrt(12),
            "worst_month_pct": 100 * min(y),
            "mkt_excess_pct_per_year": 1200 * st.mean(x)}


def read_overwrite(bxy, bxmd) -> str:
    if bxy is None or bxmd is None:
        return "INCOMPLETE: an index was unavailable. No change to the spec."
    a = (bxy["alpha_pct_per_year"], bxmd["alpha_pct_per_year"])
    sig = any(m["alpha_pct_per_year"] > 0 and m["t_alpha"] > 2 for m in (bxy, bxmd))
    if all(v > 0 for v in a) and sig:
        return "RESTORED to the Mode 1 menu: both positive, at least one significant."
    if all(v > 0 for v in a):
        return "POINT ESTIMATE ONLY: both positive, neither significant. Stays de-risking only."
    return "NO ALPHA out of the money either."


def read_condor(c) -> str:
    if c is None:
        return "INCOMPLETE: CNDR unavailable. No change to the spec."
    if c["alpha_pct_per_year"] > 0 and c["t_alpha"] > 2:
        return "EVIDENCED EDGE (read as ~1-in-13 under no skill, see header)."
    if c["alpha_pct_per_year"] > 0:
        return "PERMITTED AS A STRUCTURE, with no edge claim."
    return "NO EVIDENCED EDGE. Mode 1 has no supported premium-harvesting leg."


def selftest() -> int:
    rng = random.Random(7)
    idx, sptr, rf = {}, {}, {}
    li = lm = 100.0
    d = dt.date(2004, 1, 1)
    while d <= dt.date(2026, 11, 13):
        if d.weekday() < 5:
            m = rng.gauss(0.06 / 252, 0.16 / math.sqrt(252))
            lm *= 1 + 0.02 / 252 + m
            li *= 1 + 0.02 / 252 + 0.3 * m + 0.03 / 252 + rng.gauss(0, 0.001)
            sptr[d], idx[d], rf[d] = lm, li, 2.0
        d += dt.timedelta(days=1)
    rows = monthly(idx, sptr, rf)
    m = measure(rows)
    ok = (abs(m["alpha_pct_per_year"] - 3.0) < m["detectable_pct_per_year"]
          and abs(m["beta"] - 0.3) < 0.04
          and rows[-1]["end"] == "2026-10-30")           # partial November dropped
    print(f"  planted alpha +3.0%/yr, beta 0.30 -> got {m['alpha_pct_per_year']:+.2f}%/yr, "
          f"beta {m['beta']:.3f}; last window ends {rows[-1]['end']}")
    print("SELF-TEST PASSED" if ok else "SELF-TEST FAILED")
    return 0 if ok else 1


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

    print(f"Test C — OTM and defined-risk index writing.  spec {SPEC_VERSION}, "
          f"frozen {SPEC_FROZEN_ON}\n")
    sptr, s_src, n1 = fetch("SPTR")
    rf, r_src, n2 = fetch("RF")
    if sptr is None or rf is None:
        raise SystemExit("FATAL: benchmark or risk-free series unavailable.\n  "
                         + "\n  ".join(n1 + n2))
    cut = BREAK_DATE.isoformat()
    results, used, notes = {}, {"SPTR": s_src, "RF": r_src}, n1 + n2
    for k in INDICES:
        series, src, n = fetch(k)
        notes += n
        used[k] = src
        if series is None:
            results[k] = {"post": None, "pre": None}
            print(f"  {k:5s} UNAVAILABLE")
            for line in n:
                print(f"         {line}")
            print()
            continue
        rows = monthly(series, sptr, rf)
        post = measure([r for r in rows if r["start"] >= cut])
        pre = measure([r for r in rows if r["start"] < cut])
        results[k] = {"post": post, "pre": pre}
        print(f"  {k:5s} from {src}: {len(series)} days, {min(series)} to {max(series)}")
        for lbl, m in (("pre-2012 ", pre), ("POST-2012", post)):
            if m is None:
                print(f"      {lbl}  too few observations")
                continue
            print(f"      {lbl}  n={m['n']:3d}  alpha {m['alpha_pct_per_year']:+6.2f}%/yr  "
                  f"CI [{m['ci95'][0]:+.2f}, {m['ci95'][1]:+.2f}]  t={m['t_alpha']:+.2f}  "
                  f"beta {m['beta']:.2f}  (detectable > {m['detectable_pct_per_year']:.2f})")
            print(f"                 excess {m['excess_pct_per_year']:+.2f}%/yr  "
                  f"vol {m['vol_pct_per_year']:.2f}%  worst month {m['worst_month_pct']:+.2f}%  "
                  f"[market excess {m['mkt_excess_pct_per_year']:+.2f}%/yr]")
        print()

    r1 = read_overwrite(results["BXY"]["post"], results["BXMD"]["post"])
    r2 = read_condor(results["CNDR"]["post"])
    print("PRE-REGISTERED READING (declared 15 Nov 2026, before the first run):")
    print(f"  OTM overwriting (BXY + BXMD): {r1}")
    print(f"  Defined-risk (CNDR):          {r2}\n")

    os.makedirs(args.out, exist_ok=True)
    now = dt.datetime.now()
    res = os.path.join(args.out, f"vrp_test_c_{now.strftime('%Y%m%d_%H%M%S')}.json")
    with open(res, "w") as f:
        json.dump({"spec_version": SPEC_VERSION, "run_at": now.isoformat(timespec="seconds"),
                   "sources": used, "source_notes": notes, "results": results,
                   "reading_overwrite": r1, "reading_condor": r2}, f, indent=2)
    with open(os.path.join(args.out, "TRIALS.log"), "a") as f:
        f.write(json.dumps({"run_at": now.isoformat(timespec="seconds"), "test": "C",
                            "spec_version": SPEC_VERSION, "sources": used,
                            "post2012_alpha_pct_yr": {k: (v["post"] or {}).get("alpha_pct_per_year")
                                                      for k, v in results.items()},
                            "reading_overwrite": r1, "reading_condor": r2,
                            "result_file": os.path.basename(res)}) + "\n")
    print(f"wrote {res}\nappended one trial to {args.out}/TRIALS.log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
