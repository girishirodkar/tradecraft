"""Numbers computed in code and handed to the analysts, who describe them and
compute nothing (docs/on-demand-mode-design.md, step 2A; operator decisions of
18 November 2026 for the definitions).

- Technical inputs (10 to 12): trend, momentum, levels, relative strength.
  Description only: none supports a direction or moves a figure.
- Sector context (7) and market regime (9), for the Regime Assessor.
- Past earnings reactions (6) and the move since a dated item.

All from daily closes. No option price and no implied volatility of the
underlying is used; VIX is index-level only.
"""
from __future__ import annotations

import datetime as dt

from . import settings
from .data import prices

Series = list[tuple[dt.date, float]]
MOMENTUM = [("1 month", 21), ("3 months", 63), ("12 months", 252)]


def _pct(a: float, b: float) -> float:
    return round((a / b - 1.0) * 100, 1)


def change(series: Series, trading_days: int) -> float | None:
    if len(series) <= trading_days:
        return None
    return _pct(series[-1][1], series[-1 - trading_days][1])


def _last_per(series: Series, key) -> list[float]:
    out: dict = {}
    for d, c in series:
        out[key(d)] = c
    return list(out.values())


def _vs_average(values: list[float], n: int) -> dict | None:
    if len(values) < n:
        return None
    avg = sum(values[-n:]) / n
    return {"close": "above" if values[-1] > avg else "below", "distance_pct": _pct(values[-1], avg)}


def _extreme(series: Series, n: int) -> dict:
    window = series[-n:]
    hi = max(window, key=lambda x: x[1])
    lo = min(window, key=lambda x: x[1])
    last = series[-1][1]
    return {"high_close": round(hi[1], 2), "high_date": hi[0].isoformat(), "below_high_pct": _pct(last, hi[1]),
            "low_close": round(lo[1], 2), "low_date": lo[0].isoformat(), "above_low_pct": _pct(last, lo[1])}


def technical(series: Series, sector: Series | None = None, market: Series | None = None,
              sector_fund: str | None = None) -> dict:
    """Inputs 10 to 12, for the Technical Analyst."""
    daily = [c for _, c in series]
    weekly = _last_per(series, lambda d: d.isocalendar()[:2])
    monthly = _last_per(series, lambda d: (d.year, d.month))
    three_months = change(series, 63)

    def relative(other: Series | None):
        o = change(other, 63) if other else None
        return None if o is None or three_months is None else round(three_months - o, 1)
    return {
        "as_of": series[-1][0].isoformat(), "last_close": round(daily[-1], 2),
        "trend": {"daily": {"average": "50-day", **(_vs_average(daily, 50) or {"close": None})},
                  "weekly": {"average": "30-week", **(_vs_average(weekly, 30) or {"close": None})},
                  "monthly": {"average": "10-month", **(_vs_average(monthly, 10) or {"close": None})}},
        "momentum_pct": {name: change(series, n) for name, n in MOMENTUM},
        "levels": {"52 weeks": _extreme(series, 252), "60 trading days": _extreme(series, 60)},
        "relative_strength_3_months_pts": {"against_sector_fund": relative(sector), "sector_fund": sector_fund,
                                           "against_SPY": relative(market)},
        "role": "description only: not evidence for a direction, sets no strike, exit or invalidation condition",
    }


def sector_fund(sector_name: str | None) -> str | None:
    funds = settings.load_json("data_sources.json")["sources"]["sector_context"]["sector_funds"]
    return funds.get(sector_name or "")


def sector_context(symbol: str, sector_name: str | None, series: Series, fund_series: Series | None,
                   market: Series | None) -> dict:
    """Input 7. Changes of the stock, its sector fund and SPY over the same periods."""
    fund = sector_fund(sector_name)
    if fund is None or not fund_series:
        return {"available": False, "sector": sector_name,
                "reason": "no sector fund is mapped to this sector" if fund is None
                else f"price history for {fund} could not be fetched"}
    out = {"available": True, "sector": sector_name, "sector_fund": fund, "as_of": series[-1][0].isoformat(),
           "change_pct": {}}
    for name, n in MOMENTUM:
        out["change_pct"][name] = {symbol: change(series, n), fund: change(fund_series, n),
                                   "SPY": change(market, n) if market else None}
    return out


def market_regime(market: Series | None, vix: Series | None, vix3m: Series | None) -> dict:
    """Input 9. SPY's trend and the VIX level and term structure. Risk context,
    never support for a direction."""
    out: dict = {"role": "risk context: not an entry signal and not support for a direction"}
    if market:
        closes = [c for _, c in market]
        out["SPY"] = {"as_of": market[-1][0].isoformat(), "against_200_day_average": _vs_average(closes, 200),
                      "change_pct": {name: change(market, n) for name, n in MOMENTUM}}
    else:
        out["SPY"] = "not available"
    if vix:
        year = sorted(c for _, c in vix[-252:])
        out["VIX"] = {"as_of": vix[-1][0].isoformat(), "level": round(vix[-1][1], 1),
                      "one_year_median": round(year[len(year) // 2], 1),
                      "one_year_low": round(year[0], 1), "one_year_high": round(year[-1], 1)}
        if vix3m and vix3m[-1][0] == vix[-1][0]:
            ratio = vix[-1][1] / vix3m[-1][1]
            out["VIX"]["three_month_level"] = round(vix3m[-1][1], 1)
            out["VIX"]["term_structure"] = ("near-term above three-month (inverted)" if ratio > 1
                                            else "near-term below three-month (normal)")
        else:
            out["VIX"]["term_structure"] = "not available"
    else:
        out["VIX"] = "not available"
    return out


def _index_on_or_after(series: Series, day: dt.date) -> int | None:
    for i, (d, _) in enumerate(series):
        if d >= day:
            return i
    return None


def earnings_reactions(series: Series, report_dates: list[str]) -> list[dict]:
    """Input 6. The time of day of a report is not available, so the reaction is
    measured across two sessions: from the close before the report day to the
    close after it. That spans a report before the open or after the close."""
    out = []
    for text in report_dates:
        try:
            day = dt.date.fromisoformat(text[:10])
        except ValueError:
            continue
        i = _index_on_or_after(series, day)
        if i is None or i == 0 or i + 1 >= len(series):
            out.append({"report_date": text[:10], "move_pct": None, "note": "prices not available around this date"})
            continue
        out.append({"report_date": text[:10], "move_pct": _pct(series[i + 1][1], series[i - 1][1]),
                    "from_close": series[i - 1][0].isoformat(), "to_close": series[i + 1][0].isoformat()})
    return out


def move_since(series: Series, date_text: str | None) -> float | None:
    """Percentage change from the last close before a dated item to the latest
    close (`evidence[].price_move_since`)."""
    try:
        day = dt.date.fromisoformat(str(date_text)[:10])
    except ValueError:
        return None
    i = _index_on_or_after(series, day)
    if i is None or i == 0:
        return None
    return _pct(series[-1][1], series[i - 1][1])


def fetch(symbol: str, store=None) -> Series | None:
    """A price history, or None when it cannot be fetched ("not available")."""
    try:
        return prices.closes(symbol, store)["closes"]
    except prices.PricesUnavailable:
        return None
