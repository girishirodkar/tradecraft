"""Stage 3: market and contracts. Deterministic code, no agents, no model call.

It takes the frozen thesis, opens the option chain, builds defined-risk
candidates by fixed rule, describes each on the same measures, sets aside those
over the cost cap and ranks the rest by the priority the user picked.

Design: docs/decisions/2026-11-17-stage-3-contract-selection.md (with the
operator's 22 build decisions of 19 November 2026) and docs/product-shell.md 6.3.

Rules this module keeps:
- Defined risk only. Every leg is a contract that passes the stage 1 criteria
  in force, leaving out the DTE criterion; no expiration under 7 DTE.
- Strikes come from the typical realized move for the days to expiration.
  Support and resistance (the 60-day closing high and low) place no strike and
  do not affect a filter or the ranking.
- Within a payoff shape the construction that costs less to trade is kept.
- Ranking is on the chosen priority alone. Nothing is ranked on how expensive
  its options appear, and the first-ranked candidate is the "best fit", never a
  recommendation to trade.
- Events are shown, not filtered.
"""
from __future__ import annotations

import bisect
import datetime as dt
import math
from functools import lru_cache

from . import figures, gate, net, settings, testfail
from .data import chain as chain_data
from .data import fmp, prices, session

VIEWS = ("bullish", "bearish", "range_bound")
PRIORITIES = ("match", "payoff", "cost")          # fit to thesis, reward-to-risk, lowest slippage
HORIZON_ROWS = figures.VIEW_ROWS                  # 7, 14, 30, 60, 90
BLEND_K = {days: k for days, _, _, k in figures.ROWS if k}      # 7: 900, 14: 570, 30: 380, 60: 290
POOLED_ONLY_BEYOND_DAYS = 60
MIN_ELIGIBLE_PER_EXPIRATION = gate.MIN_PASSING
POOR_MATCH_FACTOR = 2
CONDOR_WIDTHS = {"condor": 1.0, "condor_wide": 1.25}
LEVELS_DEFINITION = "60-day closing high and low (the last 60 daily closes), as stage 2 computes them"
INF = float("inf")


def config() -> dict:
    return settings.load_json("stage3.json")


def clean_params(given: dict | None) -> dict:
    """What the user may change on the stage 3 screen, held to what is allowed."""
    g = given or {}
    cap = config()["cost_cap_pct_of_max_loss"]
    out = {"priority": g.get("priority") if g.get("priority") in PRIORITIES else "match",
           "expiration": g.get("expiration") or None, "max_loss": None,
           "cost_cap_pct": float(cap["default"])}
    try:                                    # the on-screen control: 2% to 10%, in steps of 0.5
        if g.get("cost_cap_pct") is not None:
            out["cost_cap_pct"] = round(min(cap["max"], max(cap["min"], float(g["cost_cap_pct"]))) * 2) / 2
    except (TypeError, ValueError):
        pass
    try:
        if g.get("max_loss") is not None and float(g["max_loss"]) > 0:
            out["max_loss"] = float(g["max_loss"])
    except (TypeError, ValueError):
        pass
    return out


# ---- eligibility and expirations ---------------------------------------------------------

def eligible(chain: dict, gate_settings: dict | None) -> list[dict]:
    """Contracts that may form a leg, inside the gate's 7 to 180 DTE scope. The DTE
    criterion is left out. A leg of a spread or an iron condor needs a valid two-sided
    quote and must pass the open-interest, minimum-premium and strike-distance criteria;
    the bid-ask percentage criterion is not applied to each leg but to the structure,
    through the cost cap (operator decision, 19 November 2026). A single bought option
    must also pass the bid-ask criterion: those contracts carry `single_ok`."""
    s = gate.clean_settings(gate_settings)
    out = []
    for c in chain["contracts"]:
        if not (gate.DTE_SCOPE[0] <= c["dte"] <= gate.DTE_SCOPE[1]):
            continue
        c = dict(c)
        fails = gate._fails(c, s) - {"dte"}
        if not (fails - {"spread"}):
            c["mid"] = (c["bid"] + c["ask"]) / 2
            c["single_ok"] = not fails
            c["spread_pct"] = round(c["_spread_pct"], 1)
            c["spread_setting_pct"] = s["max_spread_pct"]
            out.append(c)
    return out


def trading_days(start: dt.date, end: dt.date) -> int:
    """NYSE sessions after `start`, up to and including `end`."""
    holidays = session.calendar()["holidays"]
    n, d = 0, start
    while d < end:
        d += dt.timedelta(days=1)
        n += d.weekday() < 5 and d.isoformat() not in holidays
    return n


SESSIONS_BEFORE_HORIZON = 3


def expiration_options(ok: list[dict], thesis_days: int, chosen: str | None = None,
                       as_of: dt.date | None = None) -> list[dict]:
    """One expiration for each horizon row that has an eligible one: the eligible
    expiration nearest the horizon date, among those on or after it or up to three
    trading sessions before it (operator decision, 19 November 2026). A tie goes to
    the one on or after. Horizons leading to the same expiration are merged."""
    count: dict[tuple[int, str], int] = {}
    for c in ok:
        count[(c["dte"], c["expiration"])] = count.get((c["dte"], c["expiration"]), 0) + 1
    usable = sorted(k for k, n in count.items() if n >= MIN_ELIGIBLE_PER_EXPIRATION)
    served: dict[str, dict] = {}
    for days in HORIZON_ROWS:
        def allowed(dte: int, exp: str) -> bool:
            if dte >= days:
                return True
            if as_of is None:
                return False
            return trading_days(dt.date.fromisoformat(exp), as_of + dt.timedelta(days=days)) <= SESSIONS_BEFORE_HORIZON
        near = [(abs(dte - days), dte < days, dte, exp) for dte, exp in usable if allowed(dte, exp)]
        pick = min(near)[2:] if near else None
        if pick:
            o = served.setdefault(pick[1], {"expiration": pick[1], "dte": pick[0], "horizons_served": []})
            o["horizons_served"].append(days)
    out = sorted(served.values(), key=lambda o: o["dte"])
    default = next((o["expiration"] for o in out if thesis_days in o["horizons_served"]), None)
    selected = chosen if chosen in served else default
    for o in out:
        # The horizon the card is read against: the thesis horizon where it is served, else the longest served.
        o["serves_days"] = thesis_days if thesis_days in o["horizons_served"] else max(o["horizons_served"])
        o["days_beyond"] = o["dte"] - o["serves_days"]
        o["poor_match"] = o["dte"] > POOR_MATCH_FACTOR * o["serves_days"]
        o["from_thesis"] = o["expiration"] == default
        o["selected"] = o["expiration"] == selected
    return out


# ---- candidates ----------------------------------------------------------------------------

def _nearest(strikes, target: float) -> float:
    return min(strikes, key=lambda k: (abs(k - target), k))          # a tie goes to the lower strike


def _leg(action: str, c: dict) -> dict:
    return {"action": action, "type": c["type"], "strike": c["strike"], "occ": c.get("occ"),
            "bid": c["bid"], "ask": c["ask"], "mid": round(c["mid"], 4), "open_interest": c["open_interest"],
            "iv": c.get("iv"), "delta": c.get("delta"), "theta": c.get("theta"), "vega": c.get("vega"),
            "spread_pct": c.get("spread_pct"), "spread_setting_pct": c.get("spread_setting_pct"),
            "spread_above_setting": c.get("single_ok") is False}


def _k(x: float) -> str:
    return f"{x:g}"


def _vertical(direction: str, kind: str, lo: dict, hi: dict) -> tuple[str, list[dict]]:
    """A two-strike spread. Both constructions have the same payoff at the same strikes."""
    a, b = _k(lo["strike"]), _k(hi["strike"])
    if direction == "bullish":
        name = "Bull call spread (debit)" if kind == "call" else "Bull put spread (credit)"
        legs = [_leg("buy", lo), _leg("sell", hi)]
    else:
        name = "Bear put spread (debit)" if kind == "put" else "Bear call spread (credit)"
        legs = [_leg("buy", hi), _leg("sell", lo)]
    if "credit" in name:
        legs.reverse()                                  # the leg sold is listed first
    return f"{name}, {a} / {b}", legs


def build_candidates(view: str, spot: float, move_pct: float, calls: dict, puts: dict) -> tuple[list[dict], list[dict]]:
    """(built, not built). `calls` and `puts` map strike to an eligible contract of one expiration.
    Each built entry holds one or two constructions of one payoff shape."""
    built, not_built = [], []
    grid = {"call": calls, "put": puts}
    union = sorted(set(calls) | set(puts))
    f = move_pct / 100.0

    def missing(shape, label, reason):
        not_built.append({"id": shape, "name": label, "reason": reason})

    if view in ("bullish", "bearish"):
        up = view == "bullish"
        for shape in ("hold", "move"):
            side = 1 if (up == (shape == "move")) else -1       # where the second strike sits
            label = ("Bull" if up else "Bear") + " spread " + ("above" if side > 0 else "below") + " spot"
            if not union:
                missing(shape, label, "no eligible contracts at your criteria")
                continue
            anchor = _nearest(union, spot)
            target = spot * (1 + side * f)
            found = {}
            for kind in ("call", "put"):
                beyond = [k for k in grid[kind] if (k - anchor) * side > 0] if anchor in grid[kind] else []
                if beyond:
                    found[kind] = _nearest(beyond, target)
            if not found:
                missing(shape, label, f"no eligible strike {'above' if side > 0 else 'below'} the strike nearest spot, "
                                      f"{_k(anchor)}")
                continue
            # Where the two constructions land on different far strikes: the pair nearest the
            # target; on a tie, the one that costs less to trade (operator decision, 19 November 2026).
            def cost(kind):
                lo_, hi_ = sorted((anchor, found[kind]))
                return sum((grid[kind][k]["ask"] - grid[kind][k]["bid"]) / 2 for k in (lo_, hi_))
            best = min(found, key=lambda kind: (abs(found[kind] - target), cost(kind), kind))
            second = found[best]
            lo, hi = sorted((anchor, second))
            cons = []
            for kind in ("call", "put"):
                if found.get(kind) == second:
                    name, legs = _vertical(view, kind, grid[kind][lo], grid[kind][hi])
                    cons.append({"name": name, "legs": legs})
            built.append({"id": shape, "shape": shape, "constructions": cons, "anchor": anchor, "second": second,
                          "second_target": round(target, 2), "one_construction_only": len(cons) == 1})
        kind = "call" if up else "put"
        label = "Long " + kind
        singles = {k: c for k, c in grid[kind].items() if c.get("single_ok", True)}   # keeps the bid-ask criterion
        if singles:
            c = singles[_nearest(singles, spot)]
            built.append({"id": "single", "shape": "single",
                          "constructions": [{"name": f"{label}, {_k(c['strike'])}", "legs": [_leg("buy", c)]}]})
        else:
            missing("single", label, "no eligible contracts at your criteria")
    elif view == "range_bound":
        for shape, width in CONDOR_WIDTHS.items():
            label = "Iron condor" if width == 1.0 else "Wider iron condor"
            below_spot = [k for k in puts if k < spot]
            above_spot = [k for k in calls if k > spot]
            if not below_spot or not above_spot:
                missing(shape, label, "no eligible contracts at your criteria")
                continue
            sp, sc = _nearest(below_spot, spot * (1 - width * f)), _nearest(above_spot, spot * (1 + width * f))
            lp, lc = [k for k in puts if k < sp], [k for k in calls if k > sc]
            if not lp or not lc:
                missing(shape, label, "no eligible strike beyond a short strike")
                continue
            lp, lc = max(lp), min(lc)
            legs = [_leg("buy", puts[lp]), _leg("sell", puts[sp]), _leg("sell", calls[sc]), _leg("buy", calls[lc])]
            built.append({"id": shape, "shape": shape, "constructions": [
                {"name": f"{label}, {_k(lp)} / {_k(sp)} / {_k(sc)} / {_k(lc)}", "legs": legs}]})
        if len(built) == 2 and built[0]["constructions"][0]["name"].split(", ")[1] == \
                built[1]["constructions"][0]["name"].split(", ")[1]:
            built.pop()                                    # the wider one landed on the same strikes
            missing("condor_wide", "Wider iron condor", "the eligible strikes give the same condor as the usual range")
    return built, not_built


# ---- payoff --------------------------------------------------------------------------------

def payoff(legs: list[dict], s: float) -> float:
    """Profit or loss per share at expiration, entered at mid. Intrinsic value only."""
    x = 0.0
    for l in legs:
        sign = 1 if l["action"] == "buy" else -1
        x += sign * ((max(s - l["strike"], 0) if l["type"] == "call" else max(l["strike"] - s, 0)) - l["mid"])
    return x


def payoff_shape(legs: list[dict]) -> dict:
    """Net premium, max loss, max profit, breakevens and the prices at which it profits."""
    strikes = sorted({l["strike"] for l in legs})
    top = strikes[-1] * 4 + 1000
    knots = [0.0] + strikes + [top]
    ys = [payoff(legs, k) for k in knots]
    slope_up = ys[-1] - payoff(legs, top - 1)              # per $1 beyond the last strike
    bes = []
    for (a, ya), (b, yb) in zip(zip(knots, ys), zip(knots[1:], ys[1:])):
        if (ya < 0 < yb) or (ya > 0 > yb):
            bes.append(a + (b - a) * (0 - ya) / (yb - ya))
    edges = [0.0] + bes + [INF]
    profit = []
    for a, b in zip(edges, edges[1:]):
        mid = (a + min(b, top)) / 2 if b != INF else max(a, strikes[-1]) + 1
        if payoff(legs, mid) > 0:
            profit.append((a, b))
    net = sum((1 if l["action"] == "buy" else -1) * l["mid"] for l in legs)
    return {"net": net, "max_loss": -min(ys), "max_profit": None if slope_up > 1e-9 else max(ys),
            "breakevens": bes, "profit_intervals": profit}


# ---- the two history-based figures -------------------------------------------------------

def _moves(closes: list[float], h: int) -> list[float]:
    return sorted(closes[t + h] / closes[t] - 1.0 for t in range(len(closes) - h))


def _share(sorted_xs: list[float], intervals: list[tuple[float, float]]) -> float | None:
    if not sorted_xs:
        return None
    n = sum(bisect.bisect_left(sorted_xs, b) - bisect.bisect_right(sorted_xs, a) for a, b in intervals if b > a)
    return 100.0 * n / len(sorted_xs)


def _clip(intervals, lo, hi):
    return [(max(a, lo), min(b, hi)) for a, b in intervals if min(b, hi) > max(a, lo)]


@lru_cache(maxsize=1)
def _pool_series() -> tuple[tuple[str, tuple[float, ...]], ...]:
    """The single stocks of label_out/prices with five years of history (the stage 2 pool)."""
    out = []
    for p in sorted(net.readable("label_out/prices").glob("*.json")):
        if p.stem in figures.NOT_SINGLE_STOCKS:
            continue
        try:
            series = [c for _, c in prices._parse(p.read_bytes())]
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if len(series) >= figures.MIN_YEARS * figures.TRADING_DAYS:
            out.append((p.stem, tuple(figures._lookback(series))))
    return tuple(out)


@lru_cache(maxsize=8)
def pool_scaled_moves(h: int) -> tuple[tuple[float, ...], ...]:
    """Per pool stock: its past h-day moves, each divided by that stock's typical move, sorted."""
    out = []
    for _, closes in _pool_series():
        m = _moves(list(closes), h)
        t = figures.typical_move(list(closes), h)
        if m and t:
            out.append(tuple(x / (t / 100.0) for x in m))
    return tuple(out)


def blend_weight(symbol: str, dte: int, closes: list[float], h: int) -> tuple[float, str]:
    """Own weight n / (n + k), with the k of the stage 2 row nearest the DTE (the shorter
    row when midway); pooled only beyond 60 days or under five years of history; funds unblended."""
    if symbol.upper() in figures.OWN_HISTORY:
        return 1.0, "own history"
    if (len(closes) - 1) / figures.TRADING_DAYS < figures.MIN_YEARS:
        return 0.0, "pool average (under five years of history)"
    if dte > POOLED_ONLY_BEYOND_DAYS:
        return 0.0, "pool average"
    row = min(BLEND_K, key=lambda d: (abs(d - dte), d))
    n = (len(closes) - 1) / h
    return n / (n + BLEND_K[row]), "blended"


class History:
    """Past moves over the trading days to expiration, for one underlying and its pool."""

    def __init__(self, symbol: str, closes: list[float], dte: int, h: int, pool=None):
        self.closes = figures._lookback(closes)
        self.h, self.dte = h, dte
        self.own = _moves(self.closes, h)
        self.move_pct = figures.typical_move(self.closes, h)
        self.weight, self.basis = blend_weight(symbol, dte, self.closes, h)
        self.pool = (pool if pool is not None else pool_scaled_moves(h)) if self.weight < 1.0 else ()
        if self.weight < 1.0 and not self.pool:
            self.weight, self.basis = 1.0, "own history (pool average not available)"
        self.n_independent = (len(self.closes) - 1) / h if h else 0

    def figure(self, intervals_px, spot: float, within: tuple[float, float] = (-INF, INF)) -> dict:
        """Share of past periods in which the price would have finished inside `intervals_px`
        (profit, before slippage), among periods whose move lay in `within` (as a return)."""
        f = (self.move_pct or 0) / 100.0
        ret = [(a / spot - 1.0, (b / spot - 1.0) if b != INF else INF) for a, b in intervals_px]
        own_n = _share(self.own, [within])
        own = _share(self.own, _clip(ret, *within))
        own = None if not own_n else 100.0 * own / own_n
        pooled = None
        if self.pool and f > 0:
            z = [(a / f, b / f) for a, b in ret]
            zw = (within[0] / f, within[1] / f)
            shares = []
            for xs in self.pool:
                base = _share(xs, [zw])
                if base:
                    shares.append(100.0 * _share(xs, _clip(z, *zw)) / base)
            pooled = sum(shares) / len(shares) if shares else None
        if pooled is None:
            main = own
        elif own is None:
            main = pooled
        else:
            main = self.weight * own + (1 - self.weight) * pooled
        se = None
        if own is not None and self.n_independent > 0:
            se = 100.0 * math.sqrt(max(own / 100 * (1 - own / 100), 0) / self.n_independent)
        r = lambda x: None if x is None else round(x, 1)      # noqa: E731
        return {"pct": r(main), "own_pct": r(own), "pooled_pct": r(pooled), "own_weight": round(self.weight, 2),
                "basis": self.basis if pooled is not None else "own history", "uncertainty_pts": r(se)}


# ---- market-implied figures --------------------------------------------------------------

def _cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def atm_iv(ok_exp: list[dict], spot: float) -> float | None:
    """Mean implied volatility of the call and the put nearest spot."""
    ivs = []
    for kind in ("call", "put"):
        xs = [c for c in ok_exp if c["type"] == kind and c.get("iv")]
        if xs:
            ivs.append(min(xs, key=lambda c: (abs(c["strike"] - spot), c["strike"]))["iv"])
    return sum(ivs) / len(ivs) if ivs else None


def implied_pop(profit_intervals, spot: float, dte: int, ok_exp: list[dict]) -> dict:
    """Approximate. Risk-neutral, rate zero, lognormal: the chance of finishing inside the
    profit region, reading each breakeven with the implied volatility of the eligible
    contract nearest it on its side (calls above spot, puts below); at-the-money mean otherwise."""
    atm = atm_iv(ok_exp, spot)
    t = dte / 365.0
    used = []

    def above(b: float) -> float | None:          # chance of finishing above b
        if b <= 0:
            return 1.0
        if b == INF:
            return 0.0
        kind = "call" if b >= spot else "put"
        xs = [c for c in ok_exp if c["type"] == kind and c.get("iv")]
        iv, src = (min(xs, key=lambda c: (abs(c["strike"] - b), c["strike"]))["iv"], "nearest the breakeven") \
            if xs else (atm, "at the money")
        if not iv or t <= 0:
            return None
        used.append({"breakeven": round(b, 2), "iv": iv, "from": src})
        return _cdf((math.log(spot / b) - iv * iv * t / 2) / (iv * math.sqrt(t)))

    total = 0.0
    for a, b in profit_intervals:
        pa, pb = above(a), above(b)
        if pa is None or pb is None:
            return {"pct": None, "method": "not available: no implied volatility for this expiration"}
        total += pa - pb
    return {"pct": round(100 * total, 1), "iv_used": used,
            "method": "approximate: risk-neutral, rate zero, lognormal"}


def implied_move_pct(ok_exp: list[dict], spot: float, dte: int) -> float | None:
    iv = atm_iv(ok_exp, spot)
    return None if not iv else round(100 * iv * math.sqrt(dte / 365.0), 1)


# ---- describing, filtering, ranking --------------------------------------------------------

def _usd(x: float) -> str:
    return f"${x:,.2f}"


def describe(con: dict, entry: dict, ctx: dict) -> dict:
    """One construction on every measure. Dollar figures are for one contract (100 shares)."""
    legs, spot, view = con["legs"], ctx["spot"], ctx["view"]
    hist: History = ctx["history"]
    p = payoff_shape(legs)
    f = (hist.move_pct or 0) / 100.0
    max_loss = round(p["max_loss"] * 100, 2)
    slip = round(sum((l["ask"] - l["bid"]) / 2 for l in legs) * 100, 2)
    within = {"bullish": (0.0, INF), "bearish": (-INF, 0.0), "range_bound": (-f, f)}[view]
    ref = {"bullish": spot * (1 + f), "bearish": spot * (1 - f), "range_bound": spot}[view]
    at_move = payoff(legs, ref) * 100

    def greek(name: str, scale: float):
        if any(l.get(name) is None for l in legs):
            return None
        return round(sum((1 if l["action"] == "buy" else -1) * l[name] for l in legs) * scale, 2)

    shorts = [l for l in legs if l["action"] == "sell"]
    exp = dt.date.fromisoformat(ctx["expiration"])
    ev = ctx["events"]

    def before_exp(e):
        return bool(e.get("date")) and dt.date.fromisoformat(e["date"]) <= exp
    bes = [round(b, 2) for b in p["breakevens"]]
    lv = ctx["levels"]
    levels = None
    if lv and bes:
        levels = {"definition": LEVELS_DEFINITION, "support": lv["low"], "resistance": lv["high"],
                  "break_even_vs_support": ["above" if b > lv["low"] else "below" for b in bes],
                  "break_even_vs_resistance": ["above" if b > lv["high"] else "below" for b in bes]}
    return {
        "id": entry["id"], "shape": entry["shape"], "structure": con["name"].split(",")[0], "name": con["name"],
        "legs": legs, "expiry": ctx["expiration"], "dte": ctx["dte"],
        "net_price": round(p["net"] * 100, 2), "credit": p["net"] < 0,
        "max_loss": max_loss, "max_gain": None if p["max_profit"] is None else round(p["max_profit"] * 100, 2),
        "break_even": bes,
        "pays_when_view_right": hist.figure(p["profit_intervals"], spot, within),
        "base_rate_profit": hist.figure(p["profit_intervals"], spot),
        "implied_profit": implied_pop(p["profit_intervals"], spot, ctx["dte"], ctx["ok_exp"]),
        "cost": {"dollars": slip, "pct_of_risk": round(100 * slip / max_loss, 2) if max_loss > 0 else None,
                 "pct_of_price": round(100 * slip / abs(p["net"] * 100), 2) if abs(p["net"]) > 1e-9 else None},
        "greeks": {"delta": greek("delta", 1), "theta": greek("theta", 100), "vega": greek("vega", 100)},
        "payoff_at_one_move": {"spot_at": round(ref, 2), "dollars": round(at_move, 2),
                               "per_dollar_at_risk": round(at_move / max_loss, 2) if max_loss > 0 else None,
                               "keeps_growing": p["max_profit"] is None},
        "checks": {"earnings_before_expiration": before_exp(ev["earnings"]),
                   "ex_dividend_before_expiration_short_leg": bool(shorts) and before_exp(ev["ex_dividend"]),
                   "has_short_leg": bool(shorts),
                   "short_leg_in_the_money": any((l["type"] == "call" and l["strike"] < spot) or
                                                 (l["type"] == "put" and l["strike"] > spot) for l in shorts),
                   "min_leg_open_interest": min(l["open_interest"] for l in legs)},
        "levels": levels,
        "strikes": {"anchor": entry.get("anchor"), "second": entry.get("second"),
                    "second_target": entry.get("second_target"),
                    "second_distance_pct": None if entry.get("second") is None
                    else round(abs(entry["second"] / spot - 1) * 100, 1),
                    "typical_move_pct": hist.move_pct and round(hist.move_pct, 1)},
        "points": _chart_points(legs, ctx),
    }


def _chart_points(legs, ctx) -> list[list[float]]:
    lo, hi = ctx["chart"]
    ks = sorted({lo, hi} | {l["strike"] for l in legs if lo < l["strike"] < hi})
    return [[round(k, 4), round(payoff(legs, k), 4)] for k in ks]


def _sentences(c: dict, ctx: dict) -> None:
    """The fixed sentences of a row, built from the candidate's own figures."""
    view, be = ctx["view"], c["break_even"]
    b = _usd(be[0]) if be else "not available"
    if c["shape"] in ("condor", "condor_wide"):
        c["need"] = f"Needs spot to stay between the {_usd(be[0])} and {_usd(be[-1])} breakevens." if len(be) == 2 \
            else "Needs spot to stay inside the short strikes."
    else:
        side = "above" if view == "bullish" else "below"
        c["need"] = {"hold": f"Needs spot to hold {side} the {b} breakeven.",
                     "move": f"Needs spot {side} the {b} breakeven.",
                     "single": f"Single leg. Needs spot {side} the {b} breakeven."}[c["shape"]]
        if c["shape"] == "single":
            k, spot = c["legs"][0]["strike"], ctx["spot"]
            d = round(abs(k / spot - 1) * 100, 1)
            c["strike_distance_pct"] = d
            c["need"] += (f" The strike, {_k(k)}, is {d:g}% {'above' if k > spot else 'below'} spot."
                          if d >= 0.05 else f" The strike, {_k(k)}, is at spot.")
    s = c["strikes"]
    if s["second"] is not None and s["typical_move_pct"] and abs(s["second_distance_pct"] - s["typical_move_pct"]) >= 1.0:
        c["need"] += (f" The far strike is {s['second_distance_pct']:g}% from spot; one typical move is "
                      f"{s['typical_move_pct']:g}%.")
    m = c["payoff_at_one_move"]
    how = {"bullish": f"if spot rises one typical move, to {_usd(m['spot_at'])}",
           "bearish": f"if spot falls one typical move, to {_usd(m['spot_at'])}",
           "range_bound": f"if spot finishes where it is now, at {_usd(m['spot_at'])}"}[view]
    ratio = m["per_dollar_at_risk"]
    c["reward_sentence"] = (f"${ratio:.2f} per $1 at risk {how}." if ratio is not None and ratio >= 0
                            else f"a loss of ${abs(ratio or 0):.2f} per $1 at risk {how}.")
    if m["keeps_growing"]:
        c["reward_sentence"] += " Profit keeps growing beyond that."
    lv = c["levels"]
    if lv:
        parts = []
        for i, x in enumerate(be):
            parts.append(f"The breakeven, {_usd(x)}, is {lv['break_even_vs_support'][i]} the 60-day low, "
                         f"{_usd(lv['support'])}, and {lv['break_even_vs_resistance'][i]} the 60-day high, "
                         f"{_usd(lv['resistance'])}.")
        c["levels_sentence"] = " ".join(parts)


def _why(c: dict, priority: str, cands: list[dict]) -> str:
    if priority == "match" and c["pays_when_view_right"]["pct"] == 100.0:
        return "profitable in every historical period in which the thesis held"
    if priority == "cost":
        return "lowest slippage as a share of max loss"
    return "ranked first on the chosen ranking"


def rank(cands: list[dict], priority: str) -> list[dict]:
    """Order by the chosen priority alone. Ties: lower slippage, then fewer legs."""
    def key(c):
        if priority == "match":
            first = -(c["pays_when_view_right"]["pct"] if c["pays_when_view_right"]["pct"] is not None else -1)
        elif priority == "payoff":
            r = c["payoff_at_one_move"]["per_dollar_at_risk"]
            first = -(r if r is not None else -INF)
        else:
            first = c["cost"]["pct_of_risk"] if c["cost"]["pct_of_risk"] is not None else INF
        return (first, c["cost"]["dollars"], len(c["legs"]))
    out = sorted(cands, key=key)
    for i, c in enumerate(out):
        c["rank"] = i + 1
    return out


def select(chain: dict, thesis: dict, closes: list[float], gate_settings: dict | None, params: dict | None,
           events: dict, pool=None) -> dict:
    """Stage 3 on one chain. `thesis` needs view, horizon_days and origin; `events` is
    {"earnings": {...}, "ex_dividend": {...}}, each with a date or a status."""
    p = clean_params(params)
    symbol, spot, view = chain["symbol"], chain["spot"], thesis["view"]
    as_of = dt.date.fromisoformat(chain["as_of"][:10])
    ok = eligible(chain, gate_settings)
    options = expiration_options(ok, thesis["horizon_days"], p["expiration"], as_of)
    chosen = next((o for o in options if o["selected"]), None)
    recent = closes[-60:]
    levels = {"definition": LEVELS_DEFINITION, "high": round(max(recent), 2), "low": round(min(recent), 2)} \
        if recent else None
    out = {"symbol": symbol, "source": chain["source"], "as_of": chain["as_of"],
           "provisional": chain["source"] == "snapshot", "spot": spot, "view": view,
           "thesis_origin": thesis.get("origin"), "thesis_horizon_days": thesis["horizon_days"],
           "expiry_options": options, "expiry_chosen": chosen and chosen["expiration"], "horizon_amendment": None,
           "priority": p["priority"], "events": events, "levels": levels,
           "filters": {"liquidity": {"settings": gate.clean_settings(gate_settings), "dte_criterion": "left out",
                                     "bid_ask_criterion": "per leg for a single option; for a spread or an iron "
                                                          "condor, judged on the structure through the cost cap",
                                     "min_dte": gate.DTE_SCOPE[0], "strike_distance": gate.STRIKE_DEFINITION},
                       "cost_cap_pct": p["cost_cap_pct"], "cost_cap_default_pct": float(config()["cost_cap_pct_of_max_loss"]["default"]),
                       "events": "shown, not filtered"},
           "max_loss_for_trade": p["max_loss"], "eligible_contracts": len(ok),
           "candidates": [], "filtered_out": [], "not_built": [], "best_fit_id": None,
           "labels": {"pays_when_view_right": "before slippage", "base_rate_profit": "before slippage",
                      "implied_profit": "approximate"}}
    if chosen is None:
        why = ("no eligible contracts at your criteria" if not options else
               f"no eligible expiration serves the {thesis['horizon_days']}-day horizon; another may be chosen")
        return {**out, "outcome": "no_candidates", "message": f"No candidate built: {why}."}
    if not chosen["from_thesis"]:
        out["horizon_amendment"] = {"from_days": thesis["horizon_days"], "to_days": max(chosen["horizons_served"]),
                                    "expiration": chosen["expiration"]}
    dte = chosen["dte"]
    h = trading_days(as_of, dt.date.fromisoformat(chosen["expiration"]))
    hist = History(symbol, closes, dte, h, pool)
    ok_exp = [c for c in ok if c["expiration"] == chosen["expiration"]]
    out.update({"dte": dte, "trading_days": h, "typical_move_pct": hist.move_pct and round(hist.move_pct, 1),
                "implied_move_pct": implied_move_pct(ok_exp, spot, dte),
                "history": {"basis": hist.basis, "own_weight": round(hist.weight, 2),
                            "pool_names": len(hist.pool), "windows": len(hist.own)}})
    if not hist.move_pct:
        return {**out, "outcome": "no_candidates",
                "message": "No candidate built: the typical realized move could not be measured for this period."}
    calls = {c["strike"]: c for c in ok_exp if c["type"] == "call"}
    puts = {c["strike"]: c for c in ok_exp if c["type"] == "put"}
    built, not_built = build_candidates(view, spot, hist.move_pct, calls, puts)
    f = hist.move_pct / 100.0
    ks = [l["strike"] for e in built for con in e["constructions"] for l in con["legs"]]
    half = max([1.8 * f] + [abs(k / spot - 1) * 1.25 for k in ks])
    ctx = {"spot": spot, "view": view, "history": hist, "expiration": chosen["expiration"], "dte": dte,
           "ok_exp": ok_exp, "events": events, "levels": levels,
           "chart": (round(spot * (1 - half), 2), round(spot * (1 + half), 2))}
    out["chart"] = {"low": ctx["chart"][0], "high": ctx["chart"][1],
                    "move_low": round(spot * (1 - f), 2), "move_high": round(spot * (1 + f), 2)}
    kept, filtered = [], []
    for e in built:
        versions = sorted((describe(con, e, ctx) for con in e["constructions"]),
                          key=lambda c: (c["cost"]["dollars"], len(c["legs"])))
        c = versions[0]                                 # the construction that costs less to trade
        if len(versions) > 1:
            o = versions[1]
            c["other_construction"] = {"structure": o["structure"], "name": o["name"], "cost": o["cost"],
                                       "available": True}
        elif e.get("one_construction_only"):
            c["other_construction"] = {"available": False, "reason": "not available at these strikes"}
        else:
            c["other_construction"] = None
        _sentences(c, ctx)
        pct = c["cost"]["pct_of_risk"]
        if pct is None or pct > p["cost_cap_pct"]:
            c["removed_reason"] = (f"Est. slippage is {pct:g}% of max loss, above the {p['cost_cap_pct']:g}% cost cap."
                                   if pct is not None else "Max loss could not be computed.")
            c["removed_by"] = "cost_cap"
            filtered.append(c)
        else:
            c["removed_reason"] = None
            kept.append(c)
    kept = rank(kept, p["priority"])
    for c in kept:
        c["best_fit_reason"] = _why(c, p["priority"], kept) if c["rank"] == 1 else None
    out.update({"candidates": kept, "filtered_out": filtered,
                "not_built": [{**n, "reason": n["reason"]} for n in not_built],
                "best_fit_id": kept[0]["id"] if kept else None})
    if kept:
        return {**out, "outcome": "ok"}
    if not built:
        return {**out, "outcome": "no_candidates",
                "message": "No candidate built: no eligible contracts at your criteria."}
    return {**out, "outcome": "no_candidates",
            "message": "Every candidate was filtered out." if not not_built
            else "No candidate is left: each was filtered out or could not be built."}


# ---- the workflow step ---------------------------------------------------------------------

_CHAINS: dict[str, tuple[int, dict]] = {}     # request id -> (fetch number, chain): reused on re-rank and expiration switch


def frozen_thesis(state: dict) -> dict:
    """What stage 3 reads of the frozen thesis: the view, the horizon and whose it is."""
    mine = state.get("user_thesis")
    t = state.get("thesis") or {}
    if mine:
        return {"view": mine["view"], "horizon_days": mine["primary_horizon_days"], "origin": "user"}
    view = state.get("view")
    days = t.get("primary_horizon_days") or t.get("recommended_horizon_days")
    if view == "range_bound":
        days = ((state.get("range_rule") or {}).get("horizon") or {}).get("recommended_days") or days
    return {"view": view, "horizon_days": days, "origin": "system"}


def events_for(state: dict, ctx) -> dict:
    """The next earnings date (from stage 2's record) and the next ex-dividend date."""
    symbol = state["symbol"].upper()
    fig = state.get("figures") or {}
    fund = symbol in figures.OWN_HISTORY
    e = next((x for x in fig.get("events") or [] if x.get("kind") == "earnings"), None)
    if e:
        earnings = {"date": e["date"], "status": "scheduled"}
    elif fund:
        earnings = {"date": None, "status": "not applicable"}
    else:
        earnings = {"date": None, "status": "not available"}
    try:
        d = fmp.dividends(symbol, ctx.store)
        if d.get("next_ex_dividend_date"):
            ex = {"date": d["next_ex_dividend_date"], "status": "declared"}
        else:
            ex = {"date": None, "status": "none declared"}
    except Exception:  # noqa: BLE001 - not served, or the source failed: shown as not available
        ex = {"date": None, "status": "not available"}
    return {"earnings": earnings, "ex_dividend": ex}


def contracts_step(state, ctx) -> dict:
    symbol = state["symbol"]
    thesis = frozen_thesis(state)
    market = session.status()
    fetch_no = state.get("chain_fetch") or 0
    cached = _CHAINS.get(ctx.request_id)
    if cached and cached[0] == fetch_no:
        data = cached[1]
    else:
        if testfail.take("option_chain_fail_once", ctx.request_id):      # developer-only, off by default
            return {"outcome": "source_failed", "symbol": symbol, "market": market, "candidates": [],
                    "failed_source": "Cboe delayed quotes (live option chain)", "test_failure": True,
                    "message": "The live option chain could not be retrieved: a test failure, made by the "
                               "developer switch option_chain_fail_once."}
        # Order of preference (operator decision, 20 November 2026): Cboe, Tradier (both inside
        # chain_data.live), then the latest daily snapshot. No source failure is shown while one
        # of the three answers; the screen names the source that did.
        live_failed = None
        try:
            if market["open"]:
                try:
                    data = chain_data.live(symbol, ctx.store)
                except chain_data.ChainUnavailable as e:
                    live_failed = str(e)
                    data = chain_data.snapshot(symbol)
            else:
                data = chain_data.snapshot(symbol)
        except chain_data.ChainUnavailable as e:
            if market["open"]:
                return {"outcome": "source_failed", "symbol": symbol, "market": market, "candidates": [],
                        "failed_source": "the live option chain (Cboe, then Tradier) and the daily snapshot",
                        "message": f"No option data could be retrieved. Live: {live_failed}. Snapshot: {e}."}
            return {"outcome": "market_closed", "symbol": symbol, "market": market, "candidates": [],
                    "message": "Contracts cannot be chosen until the market opens."}
        data["live_failed"] = live_failed
        _CHAINS.clear()
        _CHAINS[ctx.request_id] = (fetch_no, data)
    if thesis["view"] not in VIEWS or not thesis["horizon_days"]:
        return {"outcome": "no_candidates", "symbol": symbol, "market": market, "candidates": [],
                "message": "No candidate built: the frozen thesis carries no view or no horizon."}
    try:
        closes = [c for _, c in prices.closes(figures.HISTORY_OF.get(symbol.upper(), symbol), ctx.store)["closes"]]
    except prices.PricesUnavailable as e:
        return {"outcome": "source_failed", "symbol": symbol, "market": market, "candidates": [],
                "failed_source": "price history", "message": f"The price history could not be retrieved: {e}."}
    gate_settings = (state.get("gate") or {}).get("settings") or state.get("gate_settings")
    out = select(data, thesis, closes, gate_settings, state.get("contracts_params"), events_for(state, ctx))
    out["market"] = market
    out["live_failed"] = data.get("live_failed")          # why the snapshot was used although the market is open
    out["provider"], out["delay"], out["provider_fell_back"] = data.get("provider"), data.get("delay"), data.get("fell_back")
    out["gate_overridden"] = (state.get("gate_decision") or {}).get("action") == "override"
    return out
