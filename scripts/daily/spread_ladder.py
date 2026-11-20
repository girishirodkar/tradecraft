#!/usr/bin/env python3
"""
Spread ladder — how many contracts and names are tradeable at each bid-ask
threshold, computed from a daily snapshot.

The snapshot already stores the raw bid and ask of every contract in the DTE
band, so this needs no new data and can be run on any past snapshot. It exists
so the bid-ask threshold can be chosen from measured counts instead of by
assertion (on-demand design, step 1).

Reported BY EXPIRY, never pooled: a pooled figure is dominated by thinly traded
weekly expiries (factor-spec.md §0a).

For each (symbol, expiration) and each threshold T it counts:
  quoted_le_T   contracts with a two-sided quote on a standard root and
                spread <= T. Nothing else applied.
  gated_le_T    the same, AND every other gate criterion as recorded in the
                snapshot (open interest, minimum premium, moneyness band).
                The expiry band is NOT applied: every stored expiry is shown.
The second column changes if the other criteria change; the first does not.

A snapshot taken outside regular hours is not usable for this. The 12 Nov 2026
file is one of those.

Usage:
  python3 scripts/daily/spread_ladder.py                       # newest snapshot
  python3 scripts/daily/spread_ladder.py snapshots/<file>.csv.gz
"""
from __future__ import annotations

import collections
import csv
import glob
import gzip
import os
import sys

THRESHOLDS = [2, 5, 7, 10, 12, 15, 17, 20, 25, 30]      # percent of premium
MIN_CONTRACTS_PER_NAME = 2
# The project root, two levels above scripts/daily/. Anchoring here means the
# script finds snapshots/ and ladder_out/ whatever directory it is run from.
# OPTIONS_EXPLORER_ROOT overrides it (used for testing).
ROOT = os.environ.get("OPTIONS_EXPLORER_ROOT") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "ladder_out")


def main() -> int:
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        files = sorted(glob.glob(os.path.join(ROOT, "snapshots", "chain_snapshot_*.csv.gz")))
        if not files:
            print("no snapshots found"); return 1
        path = files[-1]

    cell = collections.defaultdict(lambda: {"n": 0, "two_sided": 0, "dte": "",
                                            "q": [0] * len(THRESHOLDS),
                                            "g": [0] * len(THRESHOLDS)})
    asof = ""
    with gzip.open(path, "rt") as h:
        for r in csv.DictReader(h):
            asof = asof or r["asof"]
            c = cell[(r["symbol"], r["expiration"])]
            c["n"] += 1
            c["dte"] = r["dte"]
            reasons = set(x for x in (r["gate_reasons"] or "").split("|") if x)
            if reasons & {"bad_quote", "no_mid", "no_spread", "nonstandard_root"}:
                continue
            try:
                sp = 100.0 * float(r["spread_pct"])
            except (TypeError, ValueError):
                continue
            c["two_sided"] += 1
            # The expiry band is a scope control now, and this table is by
            # expiry anyway, so being outside 42-90 days is not a failure here.
            other_ok = not (reasons - {"spread_too_wide", "dte_out_of_band"})
            for i, t in enumerate(THRESHOLDS):
                if sp <= t:
                    c["q"][i] += 1
                    if other_ok:
                        c["g"][i] += 1

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = os.path.basename(path).replace("chain_snapshot_", "").replace(".csv.gz", "")
    out = os.path.join(OUT_DIR, f"spread_ladder_{stamp}.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["asof", "symbol", "expiration", "dte", "contracts", "two_sided"]
                   + [f"quoted_le_{t}" for t in THRESHOLDS]
                   + [f"gated_le_{t}" for t in THRESHOLDS])
        for (sym, exp), c in sorted(cell.items()):
            w.writerow([asof, sym, exp, c["dte"], c["n"], c["two_sided"]] + c["q"] + c["g"])

    # Names summary, per expiry. A name counts at T if it has >= 2 gated contracts.
    exps = sorted({e for _, e in cell})
    syms = sorted({s for s, _ in cell})
    print(f"Spread ladder from {path}\n  as of {asof}   {len(syms)} names\n")
    print(f"Names with >= {MIN_CONTRACTS_PER_NAME} contracts passing every other "
          f"criterion, by bid-ask threshold:\n")
    print("  expiry      dte  " + "".join(f"{'<=' + str(t) + '%':>7}" for t in THRESHOLDS))
    for e in exps:
        dte = next(c["dte"] for (s, x), c in cell.items() if x == e)
        row = [sum(1 for s in syms if cell.get((s, e)) and cell[(s, e)]["g"][i] >= MIN_CONTRACTS_PER_NAME)
               for i in range(len(THRESHOLDS))]
        print(f"  {e}  {dte:>3}  " + "".join(f"{v:>7}" for v in row))
    best = [sum(1 for s in syms if any(cell.get((s, e)) and cell[(s, e)]["g"][i] >= MIN_CONTRACTS_PER_NAME
                                       for e in exps)) for i in range(len(THRESHOLDS))]
    print(f"  {'any one expiry':<16} " + "".join(f"{v:>7}" for v in best))

    print("\nContracts passing every other criterion, by bid-ask threshold:\n")
    print("  expiry      dte  " + "".join(f"{'<=' + str(t) + '%':>7}" for t in THRESHOLDS))
    for e in exps:
        dte = next(c["dte"] for (s, x), c in cell.items() if x == e)
        row = [sum(c["g"][i] for (s, x), c in cell.items() if x == e) for i in range(len(THRESHOLDS))]
        print(f"  {e}  {dte:>3}  " + "".join(f"{v:>7}" for v in row))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
