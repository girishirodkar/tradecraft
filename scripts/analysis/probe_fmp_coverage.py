#!/usr/bin/env python3
"""
How much of the universe does the free Financial Modeling Prep key cover?

The first probe (probe_fmp.py, 18 November 2026) tested one company and found:
earnings dates are served, with no time of day; analyst estimates are served as a
current snapshot; company news is refused on the free plan; and one symbol (DUK)
was refused for price history as "not available under your current subscription".
So the free plan limits which symbols it serves. This script counts that.

For every symbol in universe.txt it asks for the earnings dates. For a sample it
also asks for dividends and analyst estimates. It prints a summary and writes the
detail to test_out/fmp_coverage_<stamp>.json. The key is never printed or saved.

Run from the project root:
    python3 scripts/analysis/probe_fmp_coverage.py
    python3 scripts/analysis/probe_fmp_coverage.py --limit 10     # first ten symbols only

The free plan refuses the "limit" parameter and the quarterly period, so neither
is sent (found 18 November 2026: a first run with limit=12 was refused for every
symbol). It makes about 150 requests. It stops early if the provider says the daily
limit has been reached.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_fmp as P                                    # noqa: E402  (same folder)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE = 20                                              # symbols also asked for dividends and estimates
PAUSE = 0.25                                             # seconds between requests


def symbols(limit: int | None) -> list[str]:
    out = []
    for line in open(os.path.join(ROOT, "universe.txt")):
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out[:limit] if limit else out


def refused(d: dict) -> str | None:
    """A short reason when the provider declined, else None."""
    if d.get("status") == 200 and "note" not in d:
        return None
    return f"{d.get('status')}: {(d.get('note') or '')[:90]}"


def earnings(sym: str, key: str, today: str) -> dict:
    d = P.describe(P.call("/stable/earnings", {"symbol": sym}, key))
    r = {"refused": refused(d)}
    rows = d.get("_rows") or []
    future = sorted(x["date"] for x in rows if x.get("date") and x["date"] >= today)
    past = [x for x in rows if x.get("date") and x["date"] < today]
    r["rows"] = len(rows)
    r["next_date"] = future[0] if future else None
    r["past_with_actual"] = sum(1 for x in past if x.get("epsActual") is not None)
    r["fields"] = d.get("fields")
    return r


def simple(path: str, params: dict, key: str) -> dict:
    d = P.describe(P.call(path, params, key))
    return {"refused": refused(d), "rows": d.get("rows"), "fields": d.get("fields"), "sample": d.get("sample")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--only", default=None, help="comma-separated symbols to ask for, instead of the whole universe")
    a = ap.parse_args()
    key = P.load_key()
    if not key:
        print("No FMP_API_KEY in the environment or in .env"); return 1
    today = dt.date.today().isoformat()
    syms = [x.strip() for x in a.only.split(",") if x.strip()] if a.only else symbols(a.limit)
    res: dict[str, dict] = {}
    stopped = None
    for i, s in enumerate(syms):
        e = earnings(s, key, today)
        res[s] = {"earnings": e}
        if e["refused"] and e["refused"].startswith("429"):
            stopped = f"daily limit reached at {s} ({i} symbols done)"; break
        time.sleep(PAUSE)
        if i < SAMPLE and not e["refused"]:
            res[s]["dividends"] = simple("/stable/dividends", {"symbol": s}, key); time.sleep(PAUSE)
            res[s]["estimates"] = simple("/stable/analyst-estimates", {"symbol": s, "period": "annual"}, key); time.sleep(PAUSE)
        if (i + 1) % 20 == 0:
            print(f"  {i + 1} of {len(syms)} symbols...")

    done = [s for s in res]
    served = [s for s in done if not res[s]["earnings"]["refused"]]
    with_next = [s for s in served if res[s]["earnings"]["next_date"]]
    declined = [s for s in done if res[s]["earnings"]["refused"]]
    print()
    print(f"symbols asked            {len(done)} of {len(syms)}")
    print(f"earnings served          {len(served)}")
    print(f"  with a future date     {len(with_next)}")
    print(f"earnings refused         {len(declined)}")
    if declined:
        print("  refused: " + " ".join(declined[:60]))
        print("  first reason: " + str(res[declined[0]]["earnings"]["refused"]))
    for name in ("dividends", "estimates"):
        tried = [s for s in done if name in res[s]]
        ok = [s for s in tried if not res[s][name]["refused"] and (res[s][name]["rows"] or 0) > 0]
        print(f"{name:<24} served for {len(ok)} of {len(tried)} sampled")
        if ok:
            print(f"  fields: {res[ok[0]][name]['fields']}")
            print(f"  sample: {json.dumps(res[ok[0]][name]['sample'])[:300]}")
        elif tried:
            print(f"  first reason: {res[tried[0]][name]['refused']}")
    if with_next:
        nxt = sorted((res[s]["earnings"]["next_date"], s) for s in with_next)[:8]
        print("next earnings dates: " + ", ".join(f"{s} {d}" for d, s in nxt))
    if stopped:
        print("STOPPED: " + stopped)

    os.makedirs(os.path.join(ROOT, "test_out"), exist_ok=True)
    out = os.path.join(ROOT, "test_out", f"fmp_coverage_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out, "w") as f:
        json.dump({"run_at": dt.datetime.now().isoformat(timespec="seconds"), "stopped": stopped, "symbols": res}, f, indent=1, default=str)
    print(f"\ndetail: {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
