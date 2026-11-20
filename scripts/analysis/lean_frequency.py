#!/usr/bin/env python3
"""
lean_frequency.py -- how often would the "lean" alternative produce a label?

The alternative under test (16 November 2026): trend no longer moves the
probability; analyst estimate revisions alone may produce a weak directional
label, "leans bullish" or "leans bearish", at a 2-point margin.

  revision state   change in the consensus EPS estimate for the current fiscal
                   year over the last 30 days: up > +2%, down < -2%, else flat
  increment        +/-1 on the 7- and 14-day rows (below the 2-point margin, so
                   never a label), +/-2 on the 30-, 60- and 90-day rows
  leans bullish    revisions up, on a 30/60/90-day row (figure = base rate + 2)
  leans bearish    revisions down AND base rate - 2 is under 50%

This counts LABEL FREQUENCY for today only. It scores no outcomes and tunes
nothing, so it spends no trial under spec section 11. Do not extend it to
score outcomes.

Data: base rates from the price cache written by label_frequency.py; today's
consensus and its value 30 days ago from Yahoo's earningsTrend module (a
snapshot: there is no history, so nothing "across history" can be reported).
ETFs and indices have no earnings estimates and can never carry a lean.

Usage:
  python3 scripts/analysis/lean_frequency.py              # fetch revisions (cached), report
  python3 scripts/analysis/lean_frequency.py --no-fetch   # price-only part: is a bearish lean reachable?
  python3 scripts/analysis/lean_frequency.py --refresh    # refetch revisions
  python3 scripts/analysis/lean_frequency.py --selftest
The report is printed and also written to label_out/lean_frequency_<stamp>.txt
"""
from __future__ import annotations

import argparse
import datetime as dt
import http.cookiejar
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import label_frequency as L

SPEC = "lean-frequency-1 (alternative of 2026-11-16)"
THRESHOLD = 2.0           # percent change in consensus over 30 days
LEAN_ROWS = ("30d", "60d", "90d")
INC = 2.0
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


# ---------------------------------------------------------------- revisions

class Yahoo:
    """
    Yahoo session. Two transports: Python's urllib, and the system curl binary.
    Yahoo answers HTTP 429 to the crumb request from some non-browser clients,
    so if urllib cannot get a crumb the session is retried through curl.
    """

    def __init__(self, transport: str = "urllib") -> None:
        self.transport = transport
        self.jar = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.op.addheaders = [("User-Agent", BROWSER_UA), ("Accept", "*/*")]
        self.jar_file = Path(tempfile.gettempdir()) / f"lean_yahoo_{os.getpid()}.cookies"
        self.crumb: str | None = None

    def _get(self, url: str) -> bytes:
        if self.transport == "urllib":
            with self.op.open(url, timeout=30) as r:
                return r.read()
        out = subprocess.run(
            ["curl", "-sS", "-L", "--compressed", "-m", "30", "-A", BROWSER_UA,
             "-H", "Accept: */*", "-b", str(self.jar_file), "-c", str(self.jar_file),
             "-w", "\n%{http_code}", url],
            capture_output=True, timeout=45)
        if out.returncode != 0:
            raise RuntimeError(f"curl exit {out.returncode}: {out.stderr.decode()[:80]}")
        body, _, code = out.stdout.rpartition(b"\n")
        code_i = int(code or b"0")
        if code_i >= 400:
            raise urllib.error.HTTPError(url, code_i, f"HTTP {code_i}", None, None)
        return body

    def login(self) -> None:
        for u in ("https://fc.yahoo.com", "https://finance.yahoo.com"):
            try:
                self._get(u)
            except urllib.error.HTTPError:
                pass                      # fc.yahoo.com answers 404 but sets the cookie
            except Exception:             # noqa: BLE001
                continue
        last = None
        for attempt in range(2):
            for host in (1, 2):
                try:
                    c = self._get(f"https://query{host}.finance.yahoo.com/v1/test/getcrumb").decode().strip()
                    if c and "<" not in c and len(c) < 40:
                        self.crumb = c
                        return
                    last = f"unexpected crumb reply: {c[:60]!r}"
                except Exception as e:        # noqa: BLE001
                    last = e
            time.sleep(4)
        raise RuntimeError(f"[{self.transport}] could not obtain a session crumb ({last})")

    def earnings_trend(self, sym: str) -> bytes:
        q = urllib.parse.quote(sym)
        url = (f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{q}"
               f"?modules=earningsTrend&crumb={urllib.parse.quote(self.crumb or '')}")
        return self._get(url)


def open_session() -> "Yahoo":
    errs = []
    for tr in ("urllib", "curl"):
        y = Yahoo(tr)
        try:
            y.login()
            print(f"session opened via {tr}", file=sys.stderr)
            return y
        except Exception as e:            # noqa: BLE001
            errs.append(str(e)[:140])
    raise RuntimeError(" | ".join(errs))


def parse_revision(blob: bytes) -> tuple[float | None, str]:
    """Percent change in the current-fiscal-year consensus over 30 days, and a note."""
    try:
        res = json.loads(blob)["quoteSummary"]["result"]
    except Exception:                     # noqa: BLE001
        return None, "unreadable reply"
    if not res:
        return None, "no estimates"
    trend = (res[0].get("earningsTrend") or {}).get("trend") or []
    for period in ("0y", "+1y"):
        for t in trend:
            if t.get("period") != period:
                continue
            et = t.get("epsTrend") or {}
            cur = (et.get("current") or {}).get("raw")
            ago = (et.get("30daysAgo") or {}).get("raw")
            if cur is None or ago is None:
                continue
            if abs(ago) < 0.10:
                return None, f"consensus too close to zero ({ago})"
            return 100.0 * (cur - ago) / abs(ago), period
    return None, "no estimates"


def state_of(chg: float | None) -> str:
    if chg is None:
        return "none"
    return "up" if chg > THRESHOLD else "down" if chg < -THRESHOLD else "flat"


# ---------------------------------------------------------------- report

def base_rates(here: Path) -> dict[str, dict[str, float]]:
    cache = here / "label_out" / "prices"
    names = [l.strip() for l in (here / "universe.txt").read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    cutoff = dt.date.today() - dt.timedelta(days=int(365.25 * L.LOOKBACK_YEARS))
    out = {}
    for n in names:
        if not (cache / f"{n}.json").exists():
            continue
        ser = [(d, c) for d, c in L.fetch_closes(n, cache, False) if d >= cutoff]
        if not ser or (ser[-1][0] - ser[0][0]).days / 365.25 < L.MIN_YEARS:
            continue
        res = L.analyse([c for _, c in ser])
        if "30d" in res:
            out[n] = {r: res[r]["base"] for r in LEAN_ROWS if r in res}
    return out


def lean_for(base: float, st: str) -> str | None:
    if st == "up":
        return "leans bullish"                       # base + 2 is always above 50 here
    if st == "down" and base - INC < 50.0:
        return "leans bearish"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    here = Path(__file__).resolve().parents[2]      # project root; this file is in scripts/analysis/
    out_dir = here / "label_out"
    lines: list[str] = []

    def say(s: str = "") -> None:
        print(s); lines.append(s)

    bases = base_rates(here)
    if not bases:
        print("FATAL: no price cache. Run label_frequency.py first."); return 2
    N = len(bases)
    say(f"{SPEC}\nrun {dt.datetime.now():%Y-%m-%d %H:%M}   underlyings with base rates: {N}\n")
    say("1. Is a bearish lean reachable? (needs base rate - 2 under 50%)")
    say("   row    base rate p10 / median / p90     names where reachable")
    for r in LEAN_ROWS:
        v = sorted(b[r] for b in bases.values() if r in b)
        k = sum(x - INC < 50.0 for x in v)
        say(f"   {r:5s}  {v[len(v)//10]:5.1f} / {statistics.median(v):5.1f} / {v[9*len(v)//10]:5.1f}"
            f"            {k:3d} of {len(v)} ({100*k/len(v):.0f}%)")
    if a.no_fetch:
        return 0

    rcache = out_dir / "revisions"
    rcache.mkdir(parents=True, exist_ok=True)
    y: Yahoo | None = None
    rev: dict[str, tuple[float | None, str]] = {}
    failed = []
    for i, n in enumerate(sorted(bases), 1):
        f = rcache / f"{n}.json"
        if f.exists() and not a.refresh:
            blob = f.read_bytes()
        else:
            try:
                if y is None:
                    y = open_session()
                blob = y.earnings_trend(L.yahoo_symbol(n))
                f.write_bytes(blob)
                time.sleep(0.4)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    rev[n] = (None, "no estimates"); continue
                failed.append((n, f"HTTP {e.code}")); continue
            except Exception as e:        # noqa: BLE001
                failed.append((n, str(e)[:300]))
                if y is None or y.crumb is None:
                    break                 # no session: every further call would fail the same way
                continue
        rev[n] = parse_revision(blob)
        print(f"\r{i}/{N} {n:6s}", end="", file=sys.stderr)
    print(file=sys.stderr)
    if failed:
        say("\nfetch failures:")
        for n, why in failed[:12]:
            say(f"  {n}: {why}")
        if len(failed) > 12:
            say(f"  ... and {len(failed) - 12} more")
    if not any(c is not None for c, _ in rev.values()):
        say("\nFATAL: no revision data could be read. Nothing to count.");
        _write(out_dir, lines); return 2

    states = {n: state_of(c) for n, (c, _) in rev.items()}
    cnt = {s: sum(v == s for v in states.values()) for s in ("up", "down", "flat", "none")}
    M = len(rev)
    with_est = M - cnt["none"]
    say(f"\n2. Revision state today ({M} underlyings read, {with_est} with estimates)")
    say(f"   up {cnt['up']}   down {cnt['down']}   flat {cnt['flat']}   no estimates {cnt['none']}")
    chg = sorted(c for c, _ in rev.values() if c is not None)
    if chg:
        q = lambda p: chg[min(len(chg) - 1, int(p * (len(chg) - 1) + 0.5))]      # noqa: E731
        say(f"   30-day change in consensus, %: p10 {q(.1):+.1f}  p25 {q(.25):+.1f}  median {q(.5):+.1f}"
            f"  p75 {q(.75):+.1f}  p90 {q(.9):+.1f}")

    say("\n3. Leans today, by row")
    say("   row    leans bullish   leans bearish   revisions down but not under 50%")
    any_lean = {"leans bullish": set(), "leans bearish": set()}
    blocked_all = set()
    for r in LEAN_ROWS:
        b = be = bl = 0
        for n, st in states.items():
            if r not in bases[n]:
                continue
            lab = lean_for(bases[n][r], st)
            if lab == "leans bullish":
                b += 1; any_lean[lab].add(n)
            elif lab == "leans bearish":
                be += 1; any_lean[lab].add(n)
            elif st == "down":
                bl += 1; blocked_all.add(n)
        say(f"   {r:5s}  {b:3d}             {be:3d}             {bl:3d}")
    nb, nbe = len(any_lean["leans bullish"]), len(any_lean["leans bearish"])
    tot = len(any_lean["leans bullish"] | any_lean["leans bearish"])
    say(f"\n4. Underlyings with a lean on at least one row: {tot} of {M} ({100*tot/M:.0f}%)")
    say(f"   leans bullish {nb} ({100*nb/M:.0f}%)   leans bearish {nbe} ({100*nbe/M:.0f}%)   no lean {M-tot} ({100*(M-tot)/M:.0f}%)")
    say(f"   if the under-50% condition were dropped, leans bearish would be {cnt['down']} ({100*cnt['down']/M:.0f}%)")

    say("\n5. Per underlying (30-day change in consensus %, state, base rate 30d, lean on 30d)")
    for n in sorted(rev):
        c, note = rev[n]
        b30 = bases[n].get("30d")
        lab = lean_for(b30, states[n]) if b30 is not None else None
        cs = f"{c:+6.1f}" if c is not None else "   n/a"
        say(f"   {n:6s} {cs}  {states[n]:5s} {b30:5.1f}  {lab or '-'}{'' if c is not None else '  (' + note + ')'}")
    _write(out_dir, lines)
    return 0


def _write(out_dir: Path, lines: list[str]) -> None:
    f = out_dir / f"lean_frequency_{dt.datetime.now():%Y%m%d_%H%M%S}.txt"
    f.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {f}")


def selftest() -> int:
    def blob(cur, ago, period="0y"):
        return json.dumps({"quoteSummary": {"result": [{"earningsTrend": {"trend": [
            {"period": "0q", "epsTrend": {"current": {"raw": 1.0}, "30daysAgo": {"raw": 1.0}}},
            {"period": period, "epsTrend": {"current": {"raw": cur}, "30daysAgo": {"raw": ago}}},
        ]}}], "error": None}}).encode()
    c, p = parse_revision(blob(10.5, 10.0)); assert abs(c - 5.0) < 1e-9 and p == "0y"
    assert state_of(c) == "up" and state_of(-2.5) == "down" and state_of(1.9) == "flat" and state_of(None) == "none"
    c, _ = parse_revision(blob(-1.2, -1.0)); assert abs(c + 20.0) < 1e-9          # loss widening is 'down'
    assert parse_revision(blob(0.05, 0.02))[0] is None                             # near-zero base
    assert parse_revision(b'{"quoteSummary":{"result":null,"error":{}}}') == (None, "no estimates")
    assert parse_revision(blob(3.0, 2.0, "+1y"))[1] == "+1y"
    assert lean_for(53.0, "up") == "leans bullish" and lean_for(53.0, "down") is None
    assert lean_for(51.5, "down") == "leans bearish" and lean_for(51.5, "flat") is None
    print("selftest PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
