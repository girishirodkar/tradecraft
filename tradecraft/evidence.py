"""The evidence store and the grades (docs/on-demand-mode-design.md, step 2A).

What an agent fetches through a data tool is stored here by code, item by item,
with its source and date, and the tool's result is handed back carrying each
item's id (E1, E2, ...). Agents cite those ids; they never write the evidence
themselves, so "every claim cites stored evidence" can be checked in code.

Grades are set in code from three checks, so agents do not grade their own work:
  primary source   a company filing, an earnings release or official data, not a
                   report about them. A data provider's copy of reported figures
                   is not a primary source (operator decision, 18 November 2026).
  recent           dated within the last 30 days, or since the latest earnings report.
  specific         concerns this company (or, for an index, the index itself).
All three: strong. Two: moderate. One or none: weak. A finding takes the grade
of its best cited item (operator decision, 18 November 2026).

A grade says how reliable an item is. It is not a score, is never summed and
changes no figure.
"""
from __future__ import annotations

import datetime as dt

from .data import edgar
from .storage import Store, now

FUNDAMENTALS, NEWS, MACRO = "fundamentals and expectations", "news and events", "sector and macro"
# The design's input numbers (step 2A) and the evidence family each belongs to.
FAMILY_OF_INPUT = {1: FUNDAMENTALS, 2: FUNDAMENTALS, 4: FUNDAMENTALS, 3: NEWS, 5: NEWS, 7: MACRO, 8: MACRO}
RECENT_DAYS = 30
ORDER = {"strong": 3, "moderate": 2, "weak": 1}
# Roles from "Safeguards on the inputs": only "evidence" may support a direction.
EVIDENCE, GUARD, RISK_CONTEXT, DESCRIPTION = "evidence", "guard", "risk context", "description only"


def _item(key: str, *, kind: str, input_no: int | None, source: str, date: str | None, primary: bool,
          specific: bool, title: str, body, role: str = EVIDENCE, family: str | None = None) -> dict:
    return {"key": key, "kind": kind, "input": input_no,
            "family": family if family is not None else FAMILY_OF_INPUT.get(input_no),
            "role": role, "source": source, "date": date[:10] if date else None,
            "primary_source": primary, "specific": specific, "title": title, "body": body}


def _save(store: Store, request_id: str | None, item: dict) -> str:
    key = item.pop("key")
    item["retrieved"] = now().isoformat(timespec="minutes")
    return store.add_evidence(request_id, key, item)


# ---- turning a tool's result into stored items -----------------------------------------

def _filing_meta(symbol: str, accession: str, store: Store) -> dict:
    try:
        for f in edgar.list_filings(symbol, store, limit=40)["filings"]:
            if f["accession"] == accession:
                return f
    except Exception:  # noqa: BLE001 - the item is still stored, without its filing date
        pass
    return {}


def capture(tool: str, args: dict, result: dict, store: Store, request_id: str | None) -> dict:
    """Store the items in one tool result and return the result with their ids."""
    sym = str(args.get("symbol") or result.get("symbol") or "").upper()
    src = result.get("source") or tool
    today = now().date().isoformat()
    save = lambda **kw: _save(store, request_id, _item(**kw))   # noqa: E731

    if tool == "get_company_news":
        items = []
        for n in result.get("items", []):
            eid = save(key=f"news|{sym}|{n.get('url') or n.get('title')}", kind="company news", input_no=3,
                       source=f"{n.get('publisher') or 'news'} (via {src})", date=n.get("published"),
                       primary=False, specific=True, title=n.get("title") or "", body=n)
            items.append({"evidence_id": eid, **n})
        return {**result, "items": items}

    if tool == "get_earnings":
        out = dict(result)
        out["next_report_evidence_id"] = save(
            key=f"earnings_next|{sym}|{today}", kind="next earnings date", input_no=5, source=src, date=today,
            primary=False, specific=True, role=GUARD,
            title=f"Next earnings report: {result.get('next_report_date') or 'not scheduled'}",
            body={k: result.get(k) for k in ("next_report_date", "next_report_time_of_day")})
        past = []
        for r in result.get("past_reports", []):
            eid = save(key=f"earnings_report|{sym}|{r['date']}", kind="reported earnings (provider's figures)",
                       input_no=2, source=src, date=r["date"], primary=False, specific=True,
                       title=f"Earnings reported {r['date']}", body=r)
            past.append({"evidence_id": eid, **r})
        out["past_reports"] = past
        return out

    if tool == "get_analyst_estimates":
        return {"evidence_id": save(
            key=f"estimates|{sym}|{today}", kind="analyst consensus", input_no=4, source=src, date=today,
            primary=False, specific=True, title="Current annual analyst consensus", body=result), **result}

    if tool == "get_dividends":
        return {"evidence_id": save(
            key=f"dividends|{sym}|{today}", kind="dividend dates", input_no=5, source=src, date=today,
            primary=False, specific=True, role=GUARD, title="Ex-dividend dates", body=result), **result}

    if tool == "get_company_profile":
        return {"evidence_id": save(
            key=f"profile|{sym}", kind="company profile", input_no=None, family=FUNDAMENTALS, source=src,
            date=None, primary=False, specific=True, role=DESCRIPTION,
            title=f"Profile of {result.get('name') or sym}", body=result), **result}

    if tool == "read_filing_section":
        acc = str(args.get("accession") or result.get("accession"))
        meta = _filing_meta(sym, acc, store)
        form = meta.get("form") or "filing"
        release = any(i.get("item") == "2.02" for i in (meta.get("items") or []))
        section = result.get("section") or "whole document"
        doc = args.get("document") or ""
        eid = save(
            key=f"filing|{sym}|{acc}|{doc}|{section}|{result.get('part', 1)}",
            kind="earnings release (8-K)" if release else f"company filing ({form})",
            input_no=2 if release else 1, source=f"SEC EDGAR, {form} filed {meta.get('filed') or 'date unknown'}",
            date=meta.get("filed"), primary=True, specific=True,
            title=f"{form} {doc}, {section}" + (f", part {result.get('part')}" if result.get("parts", 1) > 1 else ""),
            body={"accession": acc, "document": doc, "section": section, "part": result.get("part"),
                  "text": result.get("text")})
        # The id goes first: a long section shortened by the harness must still carry it.
        return {"evidence_id": eid, "filed": meta.get("filed"), "form": meta.get("form"), **result}

    if tool == "get_macro_calendar":
        return {"evidence_id": save(
            key=f"macro_calendar|{today}|{args.get('days_ahead', 180)}", kind="macro calendar", input_no=8,
            source="Federal Reserve; FRED release calendar", date=today, primary=True, specific=False,
            role=GUARD, title="Scheduled FOMC decisions and data releases", body=result), **result}

    return result            # list_filings, list_filing_sections: indexes, not evidence


def add_computed(store: Store, request_id: str | None, name: str, body: dict, symbol: str) -> str:
    """Store a set of numbers computed in code, so findings can cite it."""
    today = now().date().isoformat()
    spec = {
        "earnings_reactions": dict(kind="past earnings reactions", input_no=6, family=FUNDAMENTALS, role=GUARD,
                                   specific=True, title="Price reaction to past earnings reports"),
        "sector_context": dict(kind="sector context", input_no=7, role=EVIDENCE, specific=False,
                               title="The stock against its sector fund and SPY"),
        "market_regime": dict(kind="market regime", input_no=9, family=MACRO, role=RISK_CONTEXT, specific=False,
                              title="SPY trend and VIX"),
        "technical": dict(kind="price description", input_no=10, family="", role=DESCRIPTION, specific=True,
                          title="Trend, momentum, levels and relative strength"),
    }[name]
    return _save(store, request_id, _item(key=f"{name}|{symbol}|{today}", source="computed in code from daily closes",
                                          date=today, primary=False, body=body, **spec))


# ---- grades ----------------------------------------------------------------------------

def checks(item: dict, today: dt.date, latest_report: str | None) -> dict:
    recent = False
    if item.get("date"):
        try:
            d = dt.date.fromisoformat(item["date"][:10])
            recent = (today - d).days <= RECENT_DAYS or (bool(latest_report) and item["date"][:10] >= latest_report[:10])
        except ValueError:
            pass
    return {"primary_source": bool(item.get("primary_source")), "recent": recent,
            "specific": bool(item.get("specific"))}


def grade_of(c: dict) -> str:
    return {3: "strong", 2: "moderate"}.get(sum(bool(v) for v in c.values()), "weak")


def graded(store: Store, request_id: str | None, latest_report: str | None = None,
           today: dt.date | None = None) -> dict[str, dict]:
    """Every stored item of the request with its three checks and its grade, by id.
    `latest_report` defaults to the newest reported-earnings item in the store."""
    items = store.evidence(request_id)
    if latest_report is None:
        dates = [i["date"] for i in items if i["kind"].startswith("reported earnings") and i.get("date")]
        latest_report = max(dates) if dates else None
    today = today or now().date()
    out = {}
    for i in items:
        c = checks(i, today, latest_report)
        out[i["id"]] = {**i, "checks": c, "grade": grade_of(c)}
    return out


def finding_grade(cited: list[str], items: dict[str, dict]) -> tuple[str | None, list[str]]:
    """The grade of a finding: that of its best cited item. Ids that are not in
    the store are returned so the caller can reject the finding."""
    unknown = [e for e in cited if e not in items]
    grades = [items[e]["grade"] for e in cited if e in items]
    return (max(grades, key=ORDER.get) if grades else None), unknown


def capturing(tool: str, fn):
    """Wrap a data tool so that what it returns is stored as evidence."""
    def run(ctx, **kw):
        result = fn(ctx, **kw)
        return capture(tool, kw, result, ctx.store, ctx.request_id) if isinstance(result, dict) else result
    return run
