"""Company data from Financial Modeling Prep (premium plan; config/data_sources.json).

Earnings dates and past results, ex-dividend dates, the current annual analyst
consensus, the company profile and company news. Every result names its source
and when it was retrieved. What FMP does not serve is reported as not available,
never guessed: there is no time of day for earnings and no revision history for
estimates.

Prices are deliberately left out of the profile: agents that draft or support a
view work from evidence, not from the quote.
"""
from __future__ import annotations

import datetime as dt

from .. import net
from ..storage import Store, now

BASE = "https://financialmodelingprep.com/stable/"


class NotServed(Exception):
    """FMP does not serve this for the symbol."""


def _get(path: str, store: Store | None, **params) -> list:
    try:
        data = net.get_json(BASE + path, params, source=f"fmp.{path}", store=store,
                            secret_param=("apikey", "FMP_API_KEY"))
    except net.FetchFailed as e:
        raise NotServed(f"FMP {path}: {str(e)[:160]}") from e
    if not isinstance(data, list):
        raise NotServed(f"FMP {path}: unexpected answer")
    return data


def _stamp(path: str) -> dict:
    return {"source": f"FMP /stable/{path}", "retrieved": now().isoformat(timespec="minutes")}


def profile(symbol: str, store: Store | None = None) -> dict:
    rows = _get("profile", store, symbol=symbol)
    if not rows:
        raise NotServed(f"FMP profile: nothing for {symbol}")
    p = rows[0]
    return {**_stamp("profile"), "symbol": symbol, "name": p.get("companyName"), "sector": p.get("sector"),
            "industry": p.get("industry"), "exchange": p.get("exchange"), "is_etf": bool(p.get("isEtf")),
            "is_fund": bool(p.get("isFund")), "is_adr": bool(p.get("isAdr")), "country": p.get("country"),
            "cik": p.get("cik"), "description": (p.get("description") or "")[:900]}


def earnings(symbol: str, store: Store | None = None, past: int = 8) -> dict:
    rows = _get("earnings", store, symbol=symbol)
    today = now().date().isoformat()
    future = sorted(r["date"] for r in rows if r.get("date") and r["date"] >= today and r.get("epsActual") is None)
    reported = sorted((r for r in rows if r.get("epsActual") is not None), key=lambda r: r["date"], reverse=True)

    def one(r):
        est, act = r.get("epsEstimated"), r.get("epsActual")
        surprise = round((act - est) / abs(est) * 100, 1) if est not in (None, 0) and act is not None else None
        return {"date": r["date"], "eps_actual": act, "eps_estimated": est, "eps_surprise_pct": surprise,
                "revenue_actual": r.get("revenueActual"), "revenue_estimated": r.get("revenueEstimated")}
    return {**_stamp("earnings"), "symbol": symbol,
            "next_report_date": future[0] if future else None,
            "next_report_time_of_day": "not available from this source; treat the report day as inside any window that contains it",
            "past_reports": [one(r) for r in reported[:past]]}


def dividends(symbol: str, store: Store | None = None) -> dict:
    rows = sorted(_get("dividends", store, symbol=symbol), key=lambda r: r.get("date") or "", reverse=True)
    today = now().date().isoformat()
    declared = sorted(r["date"] for r in rows if r.get("date") and r["date"] >= today)
    return {**_stamp("dividends"), "symbol": symbol, "pays_dividend": bool(rows),
            "next_ex_dividend_date": declared[0] if declared else None,
            "next_ex_dividend_note": None if declared else "no future ex-dividend date has been declared yet",
            "frequency": rows[0].get("frequency") if rows else None,
            "recent": [{"ex_date": r.get("date"), "dividend": r.get("dividend"), "payment_date": r.get("paymentDate")}
                       for r in rows[:4]]}


def analyst_estimates(symbol: str, store: Store | None = None) -> dict:
    rows = sorted(_get("analyst-estimates", store, symbol=symbol, period="annual"), key=lambda r: r["date"])
    year = now().date().year
    near = [r for r in rows if year - 1 <= dt.date.fromisoformat(r["date"]).year <= year + 2]
    return {**_stamp("analyst-estimates"), "symbol": symbol, "period": "annual",
            "revision_history": "not available from this source; this is the current consensus only",
            "fiscal_years": [{"fiscal_year_end": r["date"], "eps_avg": r.get("epsAvg"), "eps_low": r.get("epsLow"),
                              "eps_high": r.get("epsHigh"), "revenue_avg": r.get("revenueAvg"),
                              "analysts_eps": r.get("numAnalystsEps"), "analysts_revenue": r.get("numAnalystsRevenue")}
                             for r in near]}


def news(symbol: str, store: Store | None = None, limit: int = 10) -> dict:
    rows = _get("news/stock", store, symbols=symbol)
    rows = sorted(rows, key=lambda r: r.get("publishedDate") or "", reverse=True)[:max(1, min(limit, 20))]
    return {**_stamp("news/stock"), "symbol": symbol,
            "items": [{"published": r.get("publishedDate"), "publisher": r.get("publisher"), "title": r.get("title"),
                       "text": (r.get("text") or "")[:600], "url": r.get("url")} for r in rows]}
