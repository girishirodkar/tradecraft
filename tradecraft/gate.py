"""Stage 1: the liquidity gate. Deterministic code, no agents.

A contract passes when it meets all five criteria. The gate excludes; it never
ranks or penalises. Its result carries counts and bid-ask spreads only: no
spot price and no premiums, so pricing cannot anchor the thesis.

Definitions (docs/product-shell.md 6.1, docs/decisions/2026-11-15-liquidity-controls.md):
- Bid-ask spread: (ask - bid) / mid, as a percentage.
- Strike distance: the plain percentage |strike / spot - 1|. (The daily census
  uses a log measure, so counts can differ by a few contracts at the boundary.)
- Invalid quote: no bid, no ask, or bid above ask. Always fails; no setting
  can pass it and it cannot be overridden.
- Contracts considered: 7 to 180 days to expiration, the adjustable range.
- The underlying passes when at least two contracts pass.
"""
from __future__ import annotations

import statistics

DEFAULTS = {"max_spread_pct": 5.0, "min_open_interest": 100, "dte_min": 42, "dte_max": 90,
            "max_strike_distance_pct": 10.0, "min_premium": 0.20}
OI_STEPS = [10, 25, 50, 100, 250, 500, 1000]
RANGES = {"max_spread_pct": (2.0, 10.0), "min_open_interest": (10, 1000), "dte_min": (7, 180),
          "dte_max": (7, 180), "max_strike_distance_pct": (5.0, 30.0), "min_premium": (0.05, 1.00)}
BUCKETS = [(7, 21), (22, 41), (42, 90), (91, 180)]
DTE_SCOPE = (7, 180)
MIN_PASSING = 2
REASONS = ["spread", "open_interest", "dte", "strike", "premium", "invalid_quote"]   # the tile order
STRIKE_DEFINITION = "plain percentage: |strike / spot - 1|"


def clean_settings(given: dict | None) -> dict:
    """Defaults, overlaid with the user's values, held inside each control's range."""
    s = dict(DEFAULTS)
    for k, v in (given or {}).items():
        if k not in DEFAULTS or v is None:
            continue
        lo, hi = RANGES[k]
        s[k] = type(DEFAULTS[k])(min(hi, max(lo, float(v))))
    s["max_spread_pct"] = round(s["max_spread_pct"] * 2) / 2                 # slider step 0.5
    s["min_open_interest"] = min(OI_STEPS, key=lambda x: abs(x - s["min_open_interest"]))
    s["max_strike_distance_pct"] = float(round(s["max_strike_distance_pct"]))
    s["min_premium"] = round(round(s["min_premium"] / 0.05) * 0.05, 2)
    s["dte_min"], s["dte_max"] = sorted((int(s["dte_min"]), int(s["dte_max"])))
    return s


def _fails(c: dict, s: dict) -> set[str]:
    f: set[str] = set()
    bid, ask = c.get("bid"), c.get("ask")
    valid = bid is not None and ask is not None and bid > 0 and ask > 0 and bid <= ask
    if not valid:
        f.add("invalid_quote")
    else:
        mid = (bid + ask) / 2
        c["_spread_pct"] = round((ask - bid) / mid * 100, 6)      # rounded so a value at the limit passes
        if c["_spread_pct"] > s["max_spread_pct"]:
            f.add("spread")
        if round(mid, 6) < s["min_premium"]:
            f.add("premium")
    if (c.get("open_interest") or 0) < s["min_open_interest"]:
        f.add("open_interest")
    if not (s["dte_min"] <= c["dte"] <= s["dte_max"]):
        f.add("dte")
    if round(abs(c["strike"] / c["spot"] - 1) * 100, 6) > s["max_strike_distance_pct"]:
        f.add("strike")
    return f


def screen(chain: dict, settings: dict | None = None) -> dict:
    s = clean_settings(settings)
    scope = [dict(c) for c in chain["contracts"] if DTE_SCOPE[0] <= c["dte"] <= DTE_SCOPE[1]]
    fails = [_fails(c, s) for c in scope]
    passing = [c for c, f in zip(scope, fails) if not f]

    buckets = []
    for lo, hi in BUCKETS:
        n = sum(1 for c, f in zip(scope, fails) if lo <= c["dte"] <= hi and not (f - {"dte"}))
        buckets.append({"from": lo, "to": hi, "passing_other_four": n,
                        "highlighted": not (hi < s["dte_min"] or lo > s["dte_max"])})
    exact = any(b["from"] == s["dte_min"] and b["to"] == s["dte_max"] for b in buckets)

    screened = {}
    for r in REASONS:
        entry = {"count": sum(1 for f in fails if r in f)}
        if r != "invalid_quote":
            entry["alone"] = sum(1 for f in fails if f == {r})
        screened[r] = entry

    spreads = sorted(c["_spread_pct"] for c in passing)
    valid_quotes = sum(1 for f in fails if "invalid_quote" not in f)
    return {
        "status": "pass" if len(passing) >= MIN_PASSING else "fail",
        "passing": len(passing),
        "considered": len(scope),
        "screened_out": len(scope) - len(passing),
        "min_passing": MIN_PASSING,
        "settings": s,
        "changed": [k for k in DEFAULTS if s[k] != DEFAULTS[k]],
        "buckets": buckets,
        "dte_matches_one_bucket": exact,
        "spread": ({"median": round(statistics.median(spreads), 1), "tightest": round(spreads[0], 1),
                    "widest": round(spreads[-1], 1)} if spreads else None),
        "screened_out_by_reason": screened,
        "override_allowed": valid_quotes > 0,      # with no valid quote there is nothing to carry forward
        "strike_distance": STRIKE_DEFINITION,
        "dte_scope": list(DTE_SCOPE),
    }
