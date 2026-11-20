"""Stage 2's measured figures. Deterministic code, no agents, no option data.

For six fixed horizons, from daily split-adjusted closes
(docs/on-demand-mode-design.md, step 2A, "Measured figures"):

- Base rate: the share of past windows of the horizon's length that closed
  above their starting close. Lookback up to 20 years, minimum 5.
  Single stocks, 7- to 60-day rows: blended with the average of all single
  stocks, own weight n / (n + k). 90- and 180-day rows: the average alone.
  Funds and indices: their own history, unblended. XSP uses SPX's history.
- Typical realized move (the design's "usual range"): the band either side of
  the starting close that held 68% of past moves of that length. Not adjusted
  for the volatility state.
- Volatility state: 20-day realised volatility against its one-year median.
  Quiet below 80%, active above 120%, otherwise normal.
- Trend: the close against a simple moving average. Description only.
- Risk reference: how often a daily close reached one typical move away from
  the start, on each side. Information only.

The definitions of the volatility state and the moving averages are those of
scripts/analysis/label_frequency.py (which is not modified). Nothing here
scores an outcome or tunes a parameter.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import statistics

from . import net, settings
from .data import prices

# (calendar days, trading days, moving-average days, blending constant k or None)
ROWS = [(7, 5, 20, 900), (14, 10, 50, 570), (30, 21, 100, 380), (60, 42, 200, 290),
        (90, 63, 200, None), (180, 126, 200, None)]
VIEW_ROWS = [7, 14, 30, 60, 90]          # the 180-day row is context only
LOOKBACK_YEARS = 20
MIN_YEARS = 5
TRADING_DAYS = 252
VOL_WINDOW = 20
VOL_MEDIAN_WINDOW = 252
QUIET, ACTIVE = 0.8, 1.2
BAND = 0.68
# Names in label_out/prices that are funds or indices, not single stocks.
NOT_SINGLE_STOCKS = {"DIA", "IWM", "QQQ", "SPY", "TLT", "XLE", "XLF", "XLK", "_SPX", "_XSP"}
OWN_HISTORY = {"SPY", "SPX", "XSP", "QQQ", "IWM", "TLT", "DIA"}       # always unblended
HISTORY_OF = {"XSP": "SPX"}
POOL_FILE = "pool_base_rates.json"
DEFINITION = {
    "base_rate": "share of past windows closing above their starting close; split-adjusted closes",
    "lookback_years": LOOKBACK_YEARS, "min_years": MIN_YEARS,
    "blend": "own weight n/(n+k), n = years x 252 / trading days in the row; "
             "k = 900, 570, 380, 290 for 7, 14, 30, 60 days; 90 and 180 days use the pool average",
    "typical_move": "68th percentile of the absolute move over the horizon; not adjusted for volatility state",
    "volatility_state": "20-day realised volatility / its 252-day median; quiet < 0.8, active > 1.2",
    "trend": "close against a simple moving average of 20, 50, 100, 200, 200, 200 days by row; description only",
    "uncertainty": "one standard error of the own base rate, counting independent windows only",
}


class FiguresUnavailable(Exception):
    pass


def _lookback(closes: list[float]) -> list[float]:
    return closes[-(LOOKBACK_YEARS * TRADING_DAYS + 1):]


def base_rate(closes: list[float], h: int) -> tuple[float, int] | None:
    """(percent of windows that closed higher, number of windows)."""
    n = len(closes) - h
    if n <= 0:
        return None
    up = sum(1 for t in range(n) if closes[t + h] > closes[t])
    return 100.0 * up / n, n


def typical_move(closes: list[float], h: int) -> float | None:
    moves = sorted(abs(closes[t + h] / closes[t] - 1.0) for t in range(len(closes) - h))
    if not moves:
        return None
    return 100.0 * moves[min(len(moves) - 1, math.ceil(BAND * len(moves)) - 1)]


def crossed(closes: list[float], h: int, move_pct: float) -> tuple[float, float]:
    """Share of windows in which a daily close reached one typical move below,
    and above, the starting close at any point in the window."""
    n = len(closes) - h
    lo = hi = 0
    f = move_pct / 100.0
    for t in range(n):
        window = closes[t + 1:t + h + 1]
        lo += min(window) <= closes[t] * (1 - f)
        hi += max(window) >= closes[t] * (1 + f)
    return 100.0 * lo / n, 100.0 * hi / n


def volatility_state(closes: list[float]) -> dict:
    """Today's state, by the fixed definition."""
    if len(closes) < VOL_WINDOW + VOL_MEDIAN_WINDOW:
        return {"state": None, "ratio": None, "note": "not enough price history"}
    lr = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    rv = [statistics.pstdev(lr[i - VOL_WINDOW:i]) for i in range(len(lr) - VOL_MEDIAN_WINDOW + 1, len(lr) + 1)]
    med = statistics.median(rv)
    if med <= 0:
        return {"state": None, "ratio": None, "note": "no price movement in the past year"}
    r = rv[-1] / med
    return {"state": "quiet" if r < QUIET else "active" if r > ACTIVE else "normal", "ratio": round(r, 2)}


def trend(closes: list[float], sma_days: int) -> str | None:
    if len(closes) < sma_days:
        return None
    return "above" if closes[-1] > sum(closes[-sma_days:]) / sma_days else "below"


# ---- the pool: the average of all single stocks ----------------------------------------

def compute_pool() -> dict:
    """Average own base rate of the single stocks in label_out/prices, per row."""
    folder = net.readable("label_out/prices")
    rates: dict[int, list[float]] = {days: [] for days, *_ in ROWS}
    names = []
    for p in sorted(folder.glob("*.json")):
        if p.stem in NOT_SINGLE_STOCKS:
            continue
        try:
            series = [c for _, c in prices._parse(p.read_bytes())]
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        if len(series) < MIN_YEARS * TRADING_DAYS:
            continue
        series = _lookback(series)
        names.append(p.stem)
        for days, h, _, _ in ROWS:
            br = base_rate(series, h)
            if br:
                rates[days].append(br[0])
    if not names:
        raise FiguresUnavailable("no single-stock price histories in label_out/prices")
    return {"names": len(names), "source": "label_out/prices",
            "computed": dt.date.today().isoformat(),
            "base_rate_pct": {str(d): round(statistics.mean(v), 2) for d, v in rates.items() if v}}


def pool() -> dict:
    """The pool averages, computed once and kept in data/."""
    path = settings.data_dir() / POOL_FILE
    if path.exists():
        return json.loads(path.read_text())
    out = compute_pool()
    path.write_text(json.dumps(out, indent=1))
    return out


# ---- the six rows ----------------------------------------------------------------------

def measure(symbol: str, series: list[tuple[dt.date, float]], pool_rates: dict | None = None) -> dict:
    """All measured figures for one underlying. `series` is (date, close), oldest first."""
    symbol = symbol.upper()
    if len(series) < 2:
        raise FiguresUnavailable(f"no price history for {symbol}")
    closes = _lookback([c for _, c in series])
    years = (len(closes) - 1) / TRADING_DAYS
    single = symbol not in OWN_HISTORY
    short = years < MIN_YEARS
    pooled = (pool_rates or {}).get("base_rate_pct", {}) if single else {}
    rows = []
    for days, h, sma_days, k in ROWS:
        br = base_rate(closes, h)
        own = br[0] if br else None
        n_indep = (len(closes) - 1) / h
        pool_rate = pooled.get(str(days))
        if not single:
            main, basis, weight = own, "own history", 1.0
        elif pool_rate is None:
            main, basis, weight = (None if short else own), "own history (pool average not available)", 1.0
        elif short or k is None or own is None:
            main, weight = pool_rate, 0.0
            basis = "pool average (under five years of history)" if short else "pool average"
        else:
            weight = n_indep / (n_indep + k)
            main, basis = weight * own + (1 - weight) * pool_rate, "blended"
        move = typical_move(closes, h)
        below, above = crossed(closes, h, move) if move else (None, None)
        se = 100.0 * math.sqrt(own / 100 * (1 - own / 100) / n_indep) if own is not None and n_indep > 0 else None
        rnd = lambda x, p=1: None if x is None else round(x, p)   # noqa: E731
        rows.append({
            "days": days, "trading_days": h, "context_only": days not in VIEW_ROWS,
            "base_rate_pct": rnd(main), "base_rate_basis": basis,
            "own_base_rate_pct": rnd(own), "pool_base_rate_pct": rnd(pool_rate), "own_weight": rnd(weight, 2),
            "base_rate_uncertainty_pts": rnd(se), "independent_windows": int(n_indep),
            "typical_move_pct": rnd(move),
            "crossed_below_pct": rnd(below), "crossed_above_pct": rnd(above),
            "trend": trend(closes, sma_days), "trend_sma_days": sma_days,
        })
    return {
        "symbol": symbol, "reference_close": round(closes[-1], 2), "reference_date": series[-1][0].isoformat(),
        "years_of_history": round(years, 1), "short_history": short, "single_stock": single,
        "volatility": volatility_state(closes), "horizons": rows,
        "pool": {k: pool_rates.get(k) for k in ("names", "source", "computed")} if pooled else None,
        "definition": DEFINITION,
    }


def for_symbol(symbol: str, store=None) -> dict:
    """Fetch the price history and measure. The source is named in the result."""
    try:
        data = prices.closes(HISTORY_OF.get(symbol.upper(), symbol), store)
    except prices.PricesUnavailable as e:
        raise FiguresUnavailable(str(e)) from e
    single = symbol.upper() not in OWN_HISTORY
    out = measure(symbol, data["closes"], pool() if single else None)
    out["price_source"] = data["source"]
    out["price_source_stale"] = data["stale"]
    if symbol.upper() in HISTORY_OF:
        out["history_of"] = HISTORY_OF[symbol.upper()]
    return out
