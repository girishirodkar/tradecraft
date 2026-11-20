#!/usr/bin/env python3
"""
label_frequency.py -- how often would stage 2 produce a view?

Counts how often a row of the thesis ladder clears the view margin, using the
definitions in docs/on-demand-mode-design.md (step 2A) as of 16 November 2026.

It measures LABEL FREQUENCY only. It does not test whether a label is right,
computes no returns to a strategy, and tunes nothing. It therefore spends no
trial under spec section 11. Do not extend it to score outcomes.

What is computed, per underlying and per horizon, from daily closes:
  direction
    base rate          share of rolling windows that closed above their start
    trend state        close above / below a simple moving average
                       (20, 50, 100, 200, 200, 200 days for the six rows)
    trend difference   conditional rate minus base rate, limited to
                       +/-5 points (7-60 day rows) or +/-3 (90, 180)
  move size
    typical move       one standard deviation of horizon-length returns
    range base rate    share of windows closing within one typical move
    volatility state   20-day realised vol / its 252-day median:
                       quiet < 0.8, active > 1.2, otherwise normal
    range difference   conditional rate minus base rate, same limits

Labels (rows 7-90 days; the 180-day row is context only):
  bullish      departure >= +4 and figure > 50
  bearish      departure <= -4 and figure < 50
  range-bound  no directional label and range difference >= +4
Estimate revisions cannot be measured from prices, so every directional count
is given twice: revisions flat (lower bound) and revisions agreeing with the
trend (upper bound: +/-1 on 7 and 14 days, +/-2 on 30, 60, 90). Earnings dates
are not known here, so the range-bound count ignores the no-event condition
and is an upper bound.

Conditional rates use the whole history of each name, so "across history"
figures answer "on what share of past days would this row have carried a
label", not "what would the system have said at the time".

Usage:
  python3 scripts/analysis/label_frequency.py              # fetch (cached) and report
  python3 scripts/analysis/label_frequency.py --selftest   # synthetic check, no network
  python3 scripts/analysis/label_frequency.py --refresh    # ignore the price cache
Stdlib only. Prices are cached in label_out/prices/.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import random
import statistics
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SPEC = "label-frequency-1 (design of 2026-11-16)"

# (label, trading days, SMA period, trend/range limit, revision increment)
ROWS = [
    ("7d", 5, 20, 5.0, 1.0),
    ("14d", 10, 50, 5.0, 1.0),
    ("30d", 21, 100, 5.0, 2.0),
    ("60d", 42, 200, 5.0, 2.0),
    ("90d", 63, 200, 3.0, 2.0),
    ("180d", 126, 200, 3.0, 0.0),
]
VIEW_ROWS = {"7d", "14d", "30d", "60d", "90d"}   # 180d is context only
MARGIN = 4.0
LOOKBACK_YEARS = 20
MIN_YEARS = 5
VOL_WINDOW = 20
VOL_MEDIAN_WINDOW = 252
QUIET, ACTIVE = 0.8, 1.2

UA = {"User-Agent": "Mozilla/5.0 (label-frequency/1.0)",
      "Accept": "application/json,*/*"}
YF = ("https://query{host}.finance.yahoo.com/v8/finance/chart/{sym}"
      "?period1=0&period2=9999999999&interval=1d")


# ---------------------------------------------------------------- data

def yahoo_symbol(name: str) -> str:
    if name.startswith("_"):
        return "^" + name[1:]
    return name.replace(".", "-")


def fetch_closes(name: str, cache: Path, refresh: bool) -> list[tuple[dt.date, float]]:
    f = cache / f"{name}.json"
    if f.exists() and not refresh:
        blob = f.read_bytes()
    else:
        blob, err = None, None
        for host in (1, 2):
            url = YF.format(host=host, sym=urllib.parse.quote(yahoo_symbol(name)))
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=60) as r:
                    blob = r.read()
                break
            except Exception as e:           # noqa: BLE001
                err = e
                time.sleep(1.0)
        if blob is None:
            raise RuntimeError(f"fetch failed: {err}")
        f.write_bytes(blob)
        time.sleep(0.4)
    res = json.loads(blob)["chart"]["result"][0]
    ts = res["timestamp"]
    cl = res["indicators"]["quote"][0]["close"]   # split-adjusted, not dividend-adjusted
    out = []
    for t, c in zip(ts, cl):
        if c is None or c <= 0:
            continue
        out.append((dt.datetime.fromtimestamp(t, dt.timezone.utc).date(), float(c)))
    return out


# ---------------------------------------------------------------- maths

def sma(x: list[float], n: int) -> list[float | None]:
    out: list[float | None] = [None] * len(x)
    s = 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def vol_state(x: list[float]) -> list[str | None]:
    """quiet / normal / active per day, or None while the windows fill."""
    n = len(x)
    lr = [0.0] + [math.log(x[i] / x[i - 1]) for i in range(1, n)]
    rv: list[float | None] = [None] * n
    s = s2 = 0.0
    for i in range(1, n):
        s += lr[i]; s2 += lr[i] ** 2
        if i > VOL_WINDOW:
            s -= lr[i - VOL_WINDOW]; s2 -= lr[i - VOL_WINDOW] ** 2
        if i >= VOL_WINDOW:
            var = max(s2 / VOL_WINDOW - (s / VOL_WINDOW) ** 2, 0.0)
            rv[i] = math.sqrt(var)
    out: list[str | None] = [None] * n
    for i in range(n):
        j0 = i - VOL_MEDIAN_WINDOW + 1
        if j0 < VOL_WINDOW or rv[i] is None:
            continue
        med = statistics.median(rv[j0:i + 1])      # includes today; fixed definition
        if med <= 0:
            continue
        r = rv[i] / med
        out[i] = "quiet" if r < QUIET else "active" if r > ACTIVE else "normal"
    return out


def clip(v: float, lim: float) -> float:
    return max(-lim, min(lim, v))


def analyse(closes: list[float]) -> dict:
    """All per-row statistics for one underlying."""
    n = len(closes)
    vs = vol_state(closes)
    res = {}
    for label, h, sma_n, lim, inc in ROWS:
        ma = sma(closes, sma_n)
        up_all = up_n = 0
        cnt = {"up": [0, 0], "down": [0, 0]}                 # [windows, closed higher]
        rets, states_v = [], []
        day_state = {"up": 0, "down": 0}
        for t in range(n - h):
            if ma[t] is None or vs[t] is None:
                continue
            st = "up" if closes[t] > ma[t] else "down"
            hi = closes[t + h] > closes[t]
            up_n += 1; up_all += hi
            cnt[st][0] += 1; cnt[st][1] += hi
            day_state[st] += 1
            rets.append(closes[t + h] / closes[t] - 1.0)
            states_v.append(vs[t])
        if up_n < 250:
            continue
        base = 100.0 * up_all / up_n
        diff = {}
        for st in ("up", "down"):
            w, k = cnt[st]
            diff[st] = clip(100.0 * k / w - base, lim) if w >= 50 else 0.0
        sigma = statistics.pstdev(rets)
        inside = [abs(r) <= sigma for r in rets]
        rbase = 100.0 * sum(inside) / len(inside)
        rdiff, vshare = {}, {}
        for st in ("quiet", "normal", "active"):
            idx = [i for i, s in enumerate(states_v) if s == st]
            vshare[st] = len(idx) / len(states_v)
            rdiff[st] = (clip(100.0 * sum(inside[i] for i in idx) / len(idx) - rbase, lim)
                         if len(idx) >= 50 else 0.0)
        t_now = n - 1
        res[label] = {
            "windows": up_n, "base": base, "diff": diff,
            "share_up": day_state["up"] / up_n,
            "sigma_pct": 100.0 * sigma, "rbase": rbase, "rdiff": rdiff, "vshare": vshare,
            "now_trend": ("up" if closes[t_now] > ma[t_now] else "down") if ma[t_now] else None,
            "now_vol": vs[t_now], "inc": inc,
        }
    return res


def direction_label(base: float, d: float) -> str | None:
    fig = base + d
    if d >= MARGIN and fig > 50:
        return "bullish"
    if d <= -MARGIN and fig < 50:
        return "bearish"
    return None


def row_label(r: dict, trend: str, vol: str, revisions_agree: bool) -> str | None:
    d = r["diff"][trend]
    if revisions_agree and r["inc"]:
        d += r["inc"] if d > 0 else -r["inc"] if d < 0 else 0.0
    lab = direction_label(r["base"], d)
    if lab:
        return lab
    if r["rdiff"][vol] >= MARGIN:
        return "range-bound"
    return None


# ---------------------------------------------------------------- report

def pct(x: float) -> str:
    return f"{100 * x:5.1f}%"


def quantiles(v: list[float]) -> str:
    v = sorted(v)
    q = lambda p: v[min(len(v) - 1, int(p * (len(v) - 1) + 0.5))]   # noqa: E731
    return f"{q(.1):5.1f} {q(.25):5.1f} {q(.5):5.1f} {q(.75):5.1f} {q(.9):5.1f}"


def report(results: dict[str, dict], out_dir: Path, stamp: str) -> None:
    names = sorted(results)
    print(f"\n{SPEC}\nunderlyings analysed: {len(names)}\n")

    print("1. Size of the trend difference, in points (after limits), across underlyings")
    print("   row    state   p10   p25   p50   p75   p90   share of days in state")
    for label, *_ in ROWS:
        for st in ("up", "down"):
            v = [results[n][label]["diff"][st] for n in names if label in results[n]]
            sh = statistics.mean(
                (results[n][label]["share_up"] if st == "up" else 1 - results[n][label]["share_up"])
                for n in names if label in results[n])
            print(f"   {label:5s}  {st:5s} {quantiles(v)}   {pct(sh)}")

    print("\n2. Size of the range difference, in points (after limits), across underlyings")
    print("   row    state    p10   p25   p50   p75   p90   share of days in state")
    for label, *_ in ROWS:
        for st in ("quiet", "normal", "active"):
            v = [results[n][label]["rdiff"][st] for n in names if label in results[n]]
            sh = statistics.mean(results[n][label]["vshare"][st] for n in names if label in results[n])
            print(f"   {label:5s}  {st:6s} {quantiles(v)}   {pct(sh)}")

    print("\n3. Share of underlying-days on which a row would carry a label, across history")
    print("   (direction: revisions flat -> revisions agreeing; range-bound ignores earnings dates)")
    print("   row    bullish            bearish            range-bound")
    hist_any = {False: [], True: []}
    for label, *_ in ROWS:
        acc = {(lab, ra): [] for lab in ("bullish", "bearish", "range-bound") for ra in (False, True)}
        for n in names:
            r = results[n].get(label)
            if not r:
                continue
            for ra in (False, True):
                tot = {"bullish": 0.0, "bearish": 0.0, "range-bound": 0.0}
                for tr, ptr in (("up", r["share_up"]), ("down", 1 - r["share_up"])):
                    for vo, pvo in r["vshare"].items():      # states treated as independent
                        lab = row_label(r, tr, vo, ra)
                        if lab:
                            tot[lab] += ptr * pvo
                for lab in tot:
                    acc[(lab, ra)].append(tot[lab])
        m = lambda k: statistics.mean(acc[k]) if acc[k] else 0.0      # noqa: E731
        tag = "" if label in VIEW_ROWS else "   (context only)"
        print(f"   {label:5s}  {pct(m(('bullish', False)))} -> {pct(m(('bullish', True)))}"
              f"   {pct(m(('bearish', False)))} -> {pct(m(('bearish', True)))}"
              f"   {pct(m(('range-bound', False)))}{tag}")

    # any view on rows 7-90d, across history (states independent across rows is NOT assumed:
    # computed from today's-state style enumeration per name using the 30d row's vol share)
    print("\n4. Today: underlyings with a view on at least one row (7 to 90 days)")
    rows_csv = []
    counts = {False: {"dir": 0, "range": 0, "any": 0}, True: {"dir": 0, "range": 0, "any": 0}}
    per_row_today = {lab: {False: 0, True: 0, "range": 0} for lab, *_ in ROWS}
    for n in names:
        labs = {False: {}, True: {}}
        for label, *_ in ROWS:
            r = results[n].get(label)
            if not r or r["now_trend"] is None or r["now_vol"] is None:
                continue
            for ra in (False, True):
                labs[ra][label] = row_label(r, r["now_trend"], r["now_vol"], ra)
            rows_csv.append([n, label, r["windows"], f"{r['base']:.1f}", r["now_trend"],
                             f"{r['diff']['up']:.1f}", f"{r['diff']['down']:.1f}",
                             f"{r['sigma_pct']:.1f}", f"{r['rbase']:.1f}", r["now_vol"],
                             f"{r['rdiff']['quiet']:.1f}", f"{r['rdiff']['normal']:.1f}",
                             f"{r['rdiff']['active']:.1f}",
                             labs[False][label] or "no view", labs[True][label] or "no view"])
            if labs[False][label] in ("bullish", "bearish"):
                per_row_today[label][False] += 1
            if labs[True][label] in ("bullish", "bearish"):
                per_row_today[label][True] += 1
            if labs[False][label] == "range-bound":
                per_row_today[label]["range"] += 1
        for ra in (False, True):
            v = [labs[ra].get(l) for l in VIEW_ROWS]
            d = any(x in ("bullish", "bearish") for x in v)
            g = any(x == "range-bound" for x in v)
            counts[ra]["dir"] += d; counts[ra]["range"] += g; counts[ra]["any"] += (d or g)
    N = len(names)
    for ra, txt in ((False, "revisions flat     "), (True, "revisions agreeing ")):
        c = counts[ra]
        print(f"   {txt}: directional {c['dir']:3d} ({pct(c['dir'] / N)})   "
              f"range-bound {c['range']:3d} ({pct(c['range'] / N)})   "
              f"any view {c['any']:3d} ({pct(c['any'] / N)})   no view {N - c['any']:3d} ({pct(1 - c['any'] / N)})")
    print("\n   by row, today:  directional (flat -> agreeing)   range-bound")
    for label, *_ in ROWS:
        p = per_row_today[label]
        print(f"   {label:5s}           {p[False]:3d} -> {p[True]:3d}                    {p['range']:3d}")

    out_dir.mkdir(exist_ok=True)
    f = out_dir / f"label_frequency_{stamp}.csv"
    with f.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "row", "windows", "base_rate", "trend_now", "diff_up", "diff_down",
                    "typical_move_pct", "range_base", "vol_now", "rdiff_quiet", "rdiff_normal",
                    "rdiff_active", "label_revisions_flat", "label_revisions_agree"])
        w.writerows(rows_csv)
    print(f"\nwrote {f}")


# ---------------------------------------------------------------- main

def selftest() -> int:
    random.seed(7)
    x = [100.0]
    for _ in range(6000):
        x.append(x[-1] * math.exp(random.gauss(0.0, 0.015)))
    r = analyse(x)
    ok = True
    for label, *_ in ROWS:
        a = r[label]
        # driftless walk: base near 50 (wide tolerance on overlapping long windows),
        # range base near 68, no real trend or volatility effect
        tol = 4 if label in ("7d", "14d", "30d") else 12
        checks = [abs(a["base"] - 50) < tol, 60 < a["rbase"] < 76,
                  abs(a["vshare"]["quiet"] + a["vshare"]["normal"] + a["vshare"]["active"] - 1) < 1e-9]
        print(label, f"base {a['base']:.1f} rbase {a['rbase']:.1f} diff_up {a['diff']['up']:+.1f} "
                     f"rdiff_quiet {a['rdiff']['quiet']:+.1f} quiet {a['vshare']['quiet']:.2f}",
              "ok" if all(checks) else "FAIL")
        ok &= all(checks)
    # volatility clustering must show up as a positive quiet-state range difference
    y, sig = [100.0], 0.01
    for i in range(6000):
        if i % 250 == 0:
            sig = random.choice([0.006, 0.012, 0.024])
        y.append(y[-1] * math.exp(random.gauss(0.0, sig)))
    q = analyse(y)["30d"]["rdiff"]
    print("clustered vol, 30d: quiet", f"{q['quiet']:+.1f}", "active", f"{q['active']:+.1f}",
          "ok" if q["quiet"] > 1 and q["active"] < 0 else "FAIL")
    ok &= q["quiet"] > 1 and q["active"] < 0
    assert direction_label(53, 4) == "bullish" and direction_label(53, -4) == "bearish"
    assert direction_label(57, -5) is None and direction_label(53, 3.9) is None
    print("selftest", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--universe", default="universe.txt")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    here = Path(__file__).resolve().parents[2]      # project root; this file is in scripts/analysis/
    out_dir = here / "label_out"
    cache = out_dir / "prices"
    cache.mkdir(parents=True, exist_ok=True)
    names = [l.strip() for l in (here / a.universe).read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    cutoff = dt.date.today() - dt.timedelta(days=int(365.25 * LOOKBACK_YEARS))
    results, skipped = {}, []
    for i, n in enumerate(names, 1):
        try:
            series = [(d, c) for d, c in fetch_closes(n, cache, a.refresh) if d >= cutoff]
        except Exception as e:                    # noqa: BLE001
            skipped.append((n, str(e)[:80])); continue
        years = (series[-1][0] - series[0][0]).days / 365.25 if series else 0
        if years < MIN_YEARS:
            skipped.append((n, f"history {years:.1f} years, minimum {MIN_YEARS}")); continue
        res = analyse([c for _, c in series])
        if "30d" not in res:
            skipped.append((n, "too few windows")); continue
        results[n] = res
        print(f"\r{i}/{len(names)} {n:6s} {years:4.1f}y", end="", file=sys.stderr)
    print(file=sys.stderr)
    if skipped:
        print("skipped:")
        for n, why in skipped:
            print(f"  {n}: {why}")
    if not results:
        print("FATAL: no underlying could be analysed"); return 2
    report(results, out_dir, dt.datetime.now().strftime("%Y%m%d_%H%M%S"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
