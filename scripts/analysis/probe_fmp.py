#!/usr/bin/env python3
"""
Probe of Financial Modeling Prep's FREE tier, before paying for anything.

Stage 2 (thesis) needs research data. This script answers four questions about
one candidate provider, using about 20 of the free tier's 250 calls a day:

  1. Does the earnings calendar give the TIME OF DAY of each announcement
     (before the open / after the close)? Stage 3 and Mode 2 both need it.
  2. How many years of daily prices does this key actually return?
  3. Do its index closes agree with Cboe's own published SPX closes?
  4. Which of news, company profile and analyst estimates answer on this plan?

The endpoint paths could not be confirmed from the session that wrote this
file, so each question tries the current ("stable") path and the older ("v3")
one and reports what each returned. A refusal is a finding, not a failure:
the message usually names the plan that would be needed.

Setup: get a free key at financialmodelingprep.com, then put this line in
~/options-explorer/.env (that file is ignored by git):

    FMP_API_KEY=your_key_here

Run:      python3 scripts/analysis/probe_fmp.py
No key:   python3 scripts/analysis/probe_fmp.py --selftest

The key is never printed and never written to the output file.
Results go to test_out/fmp_probe_<stamp>.json.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://financialmodelingprep.com"
SYMBOLS = ["AAPL", "SPY", "DUK"]          # mega-cap, ETF, quieter utility
TIME_WORDS = {"bmo", "amc", "dmh", "before market open", "after market close",
              "pre-market", "post-market", "premarket", "postmarket"}


def load_key() -> str | None:
    k = os.environ.get("FMP_API_KEY")
    if k:
        return k.strip()
    # .env is at the project root, two levels above scripts/analysis/.
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = os.path.join(root, ".env")
    if os.path.exists(env):
        for line in open(env):
            if line.strip().startswith("FMP_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def call(path: str, params: dict, key: str) -> dict:
    q = dict(params); q["apikey"] = key
    url = f"{BASE}{path}?{urllib.parse.urlencode(q)}"
    out = {"path": path, "params": params}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "options-explorer-probe/1.0"})
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read().decode("utf-8", "replace")
            out["status"] = r.status
    except urllib.error.HTTPError as e:
        out["status"] = e.code
        body = e.read().decode("utf-8", "replace")
    except Exception as e:                                   # network, timeout
        out["status"] = None
        out["error"] = f"{type(e).__name__}: {e}"
        return out
    try:
        out["data"] = json.loads(body)
    except json.JSONDecodeError:
        out["text"] = body[:300]
    return out


def describe(res: dict) -> dict:
    """Shape of a response: rows, field names, and any refusal message."""
    d = {"path": res["path"], "status": res.get("status")}
    if "error" in res:
        d["note"] = res["error"]; return d
    data = res.get("data")
    if isinstance(data, dict):
        msg = data.get("Error Message") or data.get("message") or data.get("error")
        if msg:
            d["note"] = str(msg)[:220]; return d
        inner = data.get("historical") if isinstance(data.get("historical"), list) else None
        if inner is not None:
            data = inner
        else:
            d["rows"] = 1; d["fields"] = sorted(data.keys())[:40]; d["sample"] = data; return d
    if isinstance(data, list):
        d["rows"] = len(data)
        if data and isinstance(data[0], dict):
            d["fields"] = sorted(data[0].keys())
            d["sample"] = data[0]
        d["_rows"] = data
        return d
    d["note"] = (res.get("text") or "unrecognised response")[:220]
    return d


def time_of_day_evidence(rows: list) -> dict:
    """Is there a field saying before-open or after-close, and how often is it filled?"""
    if not rows or not isinstance(rows[0], dict):
        return {"field": None}
    best = {"field": None, "filled": 0, "values": []}
    for k in rows[0].keys():
        vals = [str(r.get(k, "")).strip().lower() for r in rows if isinstance(r, dict)]
        hits = [v for v in vals if v in TIME_WORDS]
        named = "time" in k.lower() and "update" not in k.lower()
        if hits or named:
            filled = sum(1 for v in vals if v not in ("", "none", "null", "--"))
            if hits or filled > best["filled"]:
                best = {"field": k, "filled": filled, "of": len(vals),
                        "values": sorted(set(vals))[:8], "recognised": len(hits)}
    return best


def price_depth(rows: list) -> dict:
    dates = sorted(r["date"][:10] for r in rows if isinstance(r, dict) and r.get("date"))
    if not dates:
        return {}
    y = (dt.date.fromisoformat(dates[-1]) - dt.date.fromisoformat(dates[0])).days / 365.25
    return {"first": dates[0], "last": dates[-1], "rows": len(dates), "years": round(y, 1)}


def cboe_check(fmp_rows: list) -> dict:
    """Compare FMP's S&P 500 closes with Cboe's own SPX history, last 250 days."""
    try:
        # vrp_test_a.py moved to scripts/tests/ on 18 November 2026. Importing its
        # two fetch helpers does not run the frozen test.
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
        from vrp_test_a import _get, _parse_csv_close
        cb = _parse_csv_close(_get("https://cdn.cboe.com/api/global/us_indices/daily_prices/SPX_History.csv"))
    except Exception as e:
        return {"note": f"Cboe history unavailable: {type(e).__name__}"}
    f = {dt.date.fromisoformat(r["date"][:10]): float(r["close"]) for r in fmp_rows
         if isinstance(r, dict) and r.get("date") and r.get("close") is not None}
    common = sorted(set(f) & set(cb))[-250:]
    if len(common) < 50:
        return {"note": f"only {len(common)} overlapping days"}
    diffs = [abs(f[d] - cb[d]) / cb[d] * 100 for d in common]
    worst = max(range(len(common)), key=lambda i: diffs[i])
    return {"days_compared": len(common), "max_diff_pct": round(max(diffs), 4),
            "days_over_0.05pct": sum(1 for x in diffs if x > 0.05),
            "worst_day": common[worst].isoformat()}


def first_working(results: list[dict]) -> dict | None:
    for r in results:
        if r.get("status") == 200 and r.get("rows"):
            return r
    return None


def show(label: str, results: list[dict]) -> None:
    print(f"\n{label}")
    for r in results:
        if r.get("rows"):
            print(f"   {r['path']:<46} {r['status']}  {r['rows']} rows")
        else:
            print(f"   {r['path']:<46} {r.get('status')}  {r.get('note', 'no rows')}")


def selftest() -> int:
    rows = [{"symbol": "AAPL", "date": "2026-10-29", "time": "amc", "epsEstimated": 1.7},
            {"symbol": "JPM", "date": "2026-10-13", "time": "bmo", "epsEstimated": 4.9},
            {"symbol": "XYZ", "date": "2026-11-05", "time": "", "epsEstimated": None}]
    t = time_of_day_evidence(rows)
    none = time_of_day_evidence([{"symbol": "AAPL", "date": "2026-10-29", "lastUpdated": "2026-10-01"}])
    p = price_depth([{"date": "1996-01-02", "close": 1}, {"date": "2026-11-13", "close": 2}])
    d = describe({"path": "/x", "status": 402, "data": {"Error Message": "Premium endpoint"}})
    ok = (t["field"] == "time" and t["recognised"] == 2 and t["filled"] == 2
          and none["field"] is None and p["years"] == 30.9 and d["note"] == "Premium endpoint")
    print("time-of-day detection:", t)
    print("no time field        :", none)
    print("price depth          :", p)
    print("refusal message      :", d["note"])
    print("SELF-TEST PASSED" if ok else "SELF-TEST FAILED")
    return 0 if ok else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    key = load_key()
    if not key:
        print("No FMP_API_KEY found. Add it to ~/options-explorer/.env (see the top of this file).")
        return 1
    today = dt.date.today()
    report = {"run_at": dt.datetime.now().isoformat(timespec="seconds"), "provider": "FMP", "findings": {}}

    # 1. earnings calendar and time of day
    win = {"from": (today - dt.timedelta(days=30)).isoformat(), "to": (today + dt.timedelta(days=45)).isoformat()}
    cal = [describe(call("/stable/earnings-calendar", win, key)),
           describe(call("/api/v3/earning_calendar", win, key))]
    per = [describe(call("/stable/earnings", {"symbol": "AAPL"}, key)),
           describe(call("/api/v3/historical/earning_calendar/AAPL", {}, key))]
    show("1. Earnings calendar (market-wide, then AAPL only)", cal + per)
    w = first_working(cal) or first_working(per)
    tod = time_of_day_evidence(w["_rows"]) if w else {"field": None}
    if w:
        print(f"   fields: {', '.join(w['fields'])}")
    if tod.get("field"):
        print(f"   TIME OF DAY: field '{tod['field']}', filled on {tod['filled']} of {tod['of']} rows, "
              f"values {tod['values']}")
    else:
        print("   TIME OF DAY: no before-open / after-close field found on this plan")
    report["findings"]["earnings_time_of_day"] = tod

    # 2. price history depth
    print("\n2. Daily price history")
    depth = {}
    for s in SYMBOLS:
        res = [describe(call("/stable/historical-price-eod/full", {"symbol": s, "from": "1980-01-01"}, key)),
               describe(call(f"/api/v3/historical-price-full/{s}", {"from": "1980-01-01"}, key))]
        w2 = first_working(res)
        depth[s] = price_depth(w2["_rows"]) if w2 else {"note": res[0].get("note") or res[1].get("note")}
        d = depth[s]
        print(f"   {s:5s} " + (f"{d['first']} to {d['last']}  {d['rows']} rows  {d['years']} years"
                                 if d.get("rows") else f"unavailable: {d.get('note')}"))
    report["findings"]["price_depth"] = depth

    # 3. agreement with Cboe on the index
    print("\n3. S&P 500 closes against Cboe's published SPX history")
    idx = [describe(call("/stable/historical-price-eod/full", {"symbol": "^GSPC", "from": "2025-06-01"}, key)),
           describe(call("/api/v3/historical-price-full/%5EGSPC", {"from": "2025-06-01"}, key))]
    wi = first_working(idx)
    chk = cboe_check(wi["_rows"]) if wi else {"note": idx[0].get("note") or "index history unavailable on this plan"}
    print("   " + (f"{chk['days_compared']} days compared, largest difference {chk['max_diff_pct']}%, "
                   f"{chk['days_over_0.05pct']} days differ by more than 0.05%"
                   if chk.get("days_compared") else chk.get("note")))
    report["findings"]["cboe_agreement"] = chk

    # 4. the rest
    other = {
        "Company profile and sector": [("/stable/profile", {"symbol": "AAPL"}), ("/api/v3/profile/AAPL", {})],
        "Company news": [("/stable/news/stock", {"symbols": "AAPL", "limit": 5}), ("/api/v3/stock_news", {"tickers": "AAPL", "limit": 5})],
        "Analyst estimates": [("/stable/analyst-estimates", {"symbol": "AAPL", "period": "annual", "limit": 2}),
                              ("/api/v3/analyst-estimates/AAPL", {"limit": 2})],
    }
    report["findings"]["other"] = {}
    for label, cands in other.items():
        res = [describe(call(p, q, key)) for p, q in cands]
        show("4. " + label, res)
        w3 = first_working(res)
        if w3:
            print(f"   fields: {', '.join(w3['fields'][:18])}")
        report["findings"]["other"][label] = [{k: v for k, v in r.items() if k != "_rows"} for r in res]

    os.makedirs("test_out", exist_ok=True)
    out = os.path.join("test_out", f"fmp_probe_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    report["findings"]["earnings_endpoints"] = [{k: v for k, v in r.items() if k != "_rows"} for r in cal + per]
    with open(out, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
