"""Stage 2 as workflow steps: measured figures, evidence, the three analysts,
the Thesis agent with its validation check, and the range-bound rule.

Each step is `step(state, ctx) -> dict`. Agent steps call the harness; an agent
that does not finish becomes `StepFailed`, never a "no view". Nothing here
reads an option price: the horizon rule uses counts of eligible contracts only.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
from functools import lru_cache

from . import agents, context, evidence, figures, horizon, tools, validation
from .data import chain, fmp, macro
from .harness import AgentResult, AnthropicModel, run_agent, wrap_untrusted
from .storage import next_daily_reset, now
from .workflow.state import StepFailed, findings_for_thesis

EQUITY_INDICES = {"SPY", "SPX", "XSP", "QQQ", "IWM", "DIA"}
FUNDS = EQUITY_INDICES | {"TLT"}
DIGEST_ITEM_CHARS = {"company filing": 14_000, "earnings release": 14_000}
DIGEST_TOTAL_CHARS = 110_000
NOT_SERVED = ["estimate revision history (no source)", "the time of day of the next earnings report (no source)",
              "quarterly consensus (only annual consensus is available)", "macro expectations: no source"]


# ---- shared helpers --------------------------------------------------------------------

@lru_cache(maxsize=1)
def _default_model():
    return AnthropicModel()


@lru_cache(maxsize=1)
def _default_registry():
    return tools.build_registry()


def _model(ctx):
    return ctx.extras.get("model") or _default_model()


def _registry(ctx):
    return ctx.extras.get("registry") or _default_registry()


def require_ok(r: AgentResult) -> AgentResult:
    """An agent run that did not finish becomes a stage stop with a plain message."""
    if r.ok:
        return r
    if r.status == "timed_out":
        raise StepFailed("timed_out", r.message, agent=r.agent)
    if r.status == "spend_limit":
        daily = "daily" in r.message
        raise StepFailed("spend_limit", r.message, agent=r.agent, scope="day" if daily else "request",
                         resets_at=next_daily_reset().isoformat(timespec="minutes") if daily else None)
    raise StepFailed("agent_failed", r.message, agent=r.agent)     # also "cancelled": the graph checks Stop


def _run(cfg, task: str, ctx) -> AgentResult:
    return run_agent(cfg, task, model=_model(ctx), registry=_registry(ctx), store=ctx.store,
                     request_id=ctx.request_id, cancel=ctx.cancel)


def _run_info(r: AgentResult) -> dict:
    return {"run_id": r.run_id, "status": r.status, "model_calls": r.model_calls, "tool_calls": r.tool_calls,
            "cost_usd": round(r.cost_usd, 4), "returned_once": r.returned, "config": r.config_fingerprint}


def _known_ids(ctx):
    return lambda: {i["id"] for i in ctx.store.evidence(ctx.request_id)}


def _evidence_facts(state, ctx):
    """For the analysts' output check: each item's date and the latest earnings report."""
    return lambda: {"latest_report": (state.get("figures") or {}).get("latest_earnings_report"),
                    "dates": {i["id"]: i.get("date") for i in ctx.store.evidence(ctx.request_id)}}


def _days(n: int) -> str:
    return f"{n} day" if abs(n) == 1 else f"{n} days"


def _today() -> dt.date:
    return now().date()


def _slim(item: dict) -> dict:
    return {k: v for k, v in item.items() if k != "body"}


# ---- figures ---------------------------------------------------------------------------

def collect_events(symbol: str, ctx, today: dt.date) -> tuple[list[dict], list[dict], str | None]:
    """Dated events ahead, from the earnings calendar and the macro calendar.
    Returns (events, unavailable inputs, date of the latest earnings report)."""
    events, unavailable, latest = [], [], None
    if symbol not in FUNDS:
        try:
            e = evidence.capture("get_earnings", {"symbol": symbol}, fmp.earnings(symbol, ctx.store),
                                 ctx.store, ctx.request_id)
            if e.get("next_report_date"):
                events.append({"kind": "earnings", "label": "earnings report", "date": e["next_report_date"],
                               "evidence_id": e["next_report_evidence_id"],
                               "note": "time of day not available; the report day counts as inside"})
            latest = e["past_reports"][0]["date"] if e.get("past_reports") else None
        except fmp.NotServed as x:
            unavailable.append({"input": "earnings dates", "reason": str(x)})
    try:
        m = evidence.capture("get_macro_calendar", {"days_ahead": 200}, macro.calendar(ctx.store, 200),
                             ctx.store, ctx.request_id)
        if isinstance(m.get("fomc_decisions"), list):
            events += [{"kind": "fomc", "label": "FOMC decision", "date": d["date"], "evidence_id": m["evidence_id"]}
                       for d in m["fomc_decisions"]]
        else:
            unavailable.append({"input": "FOMC decision dates", "reason": str(m.get("fomc_decisions"))})
        if isinstance(m.get("data_releases"), list):
            events += [{"kind": "data_release", "label": d["release"], "date": d["date"],
                        "evidence_id": m["evidence_id"]} for d in m["data_releases"]]
        else:
            unavailable.append({"input": "data release dates", "reason": str(m.get("data_releases"))})
    except macro.MacroUnavailable as x:
        unavailable.append({"input": "macro calendar", "reason": str(x)})
    return sorted(events, key=lambda e: e["date"]), unavailable, latest


def figures_step(state, ctx) -> dict:
    symbol = state["symbol"]
    try:
        measured = figures.for_symbol(symbol, ctx.store)
    except figures.FiguresUnavailable as e:
        raise StepFailed("error", f"The measured figures could not be computed: {e}.") from e
    today = _today()
    events, unavailable, latest = collect_events(symbol, ctx, today)
    eligible, chain_source = None, None
    gate = state.get("gate") or {}
    if gate.get("status") != "not_checked":
        try:
            data = chain.live(symbol, ctx.store) if gate.get("source") == "live" else chain.snapshot(symbol)
            eligible = horizon.eligible_counts(data, (gate.get("settings") or state.get("gate_settings")))
            chain_source = data["source"]
        except chain.ChainUnavailable as e:
            unavailable.append({"input": "option contract counts for the horizon rule", "reason": str(e)})
    for row in measured["horizons"]:
        row["events_inside"] = horizon.events_inside(events, today, row["days"])
    return {"measured": measured, "events": events, "latest_earnings_report": latest, "today": today.isoformat(),
            "eligible_contracts": eligible, "eligible_source": chain_source, "unavailable": unavailable}


# ---- Evidence Retriever ----------------------------------------------------------------

def retriever_step(state, ctx) -> dict:
    symbol = state["symbol"]
    kind = "a fund or index" if symbol in FUNDS else "a company"
    r = require_ok(_run(agents.retriever(_known_ids(ctx)),
                        f"Collect the evidence on {symbol}, which is {kind}. Today is {_today().isoformat()}.", ctx))
    out = r.output.model_dump()
    out["unavailable"] += [{"input": f"{u['tool']} {json.dumps(u['input'])}", "reason": u["reason"]}
                           for u in r.unavailable_inputs]
    return {**out, "run": _run_info(r), "items_stored": len(ctx.store.evidence(ctx.request_id))}


# ---- computed inputs and grades --------------------------------------------------------

def grades_step(state, ctx) -> dict:
    """Compute the numbers the analysts are handed (stored as evidence so that
    findings can cite them), then grade every stored item by the three checks."""
    symbol, store, rid = state["symbol"], ctx.store, ctx.request_id
    unavailable = []
    series = context.fetch(figures.HISTORY_OF.get(symbol, symbol), store)
    if series is None:
        raise StepFailed("error", f"Price history for {symbol} could not be fetched.")
    market = context.fetch("SPY", store)
    sector_name = next((i["body"].get("sector") for i in store.evidence(rid) if i["kind"] == "company profile"), None)
    if sector_name is None and symbol not in FUNDS:
        try:
            sector_name = evidence.capture("get_company_profile", {"symbol": symbol}, fmp.profile(symbol, store),
                                           store, rid).get("sector")
        except fmp.NotServed as e:
            unavailable.append({"input": "company profile (sector)", "reason": str(e)})
    fund = context.sector_fund(sector_name)
    fund_series = context.fetch(fund, store) if fund else None
    computed = {}
    tech = context.technical(series, fund_series, market, fund)
    computed["technical"] = evidence.add_computed(store, rid, "technical", tech, symbol)
    sector = context.sector_context(symbol, sector_name, series, fund_series, market)
    if sector["available"]:
        computed["sector_context"] = evidence.add_computed(store, rid, "sector_context", sector, symbol)
    elif symbol not in FUNDS:
        unavailable.append({"input": "sector context", "reason": sector["reason"]})
    regime = context.market_regime(market, context.fetch("^VIX", store), context.fetch("^VIX3M", store))
    computed["market_regime"] = evidence.add_computed(store, rid, "market_regime", regime, symbol)
    unavailable += [{"input": f"market regime: {k}", "reason": "could not be fetched"}
                    for k in ("SPY", "VIX") if regime[k] == "not available"]
    reports = [i["date"] for i in store.evidence(rid) if i["kind"].startswith("reported earnings") and i.get("date")]
    if reports:
        computed["earnings_reactions"] = evidence.add_computed(
            store, rid, "earnings_reactions", {"definition": "close before the report day to the close after it",
                                               "reactions": context.earnings_reactions(series, sorted(reports, reverse=True))},
            symbol)
    latest = (state.get("figures") or {}).get("latest_earnings_report")
    graded = evidence.graded(store, rid, latest)
    return {"items": {i: _slim(x) for i, x in graded.items()}, "computed": computed, "unavailable": unavailable,
            "counts": {g: sum(1 for x in graded.values() if x["grade"] == g) for g in ("strong", "moderate", "weak")}}


def _graded(state, ctx) -> dict:
    return evidence.graded(ctx.store, ctx.request_id, (state.get("figures") or {}).get("latest_earnings_report"))


def _digest(items: list[dict]) -> str:
    """Stored evidence as handed to an analyst: each item with its id, source, date and grade."""
    parts, used = [], 0
    for x in items:
        cap = next((n for k, n in DIGEST_ITEM_CHARS.items() if x["kind"].startswith(k)), 3_000)
        body = json.dumps(x["body"], default=str, ensure_ascii=False)
        if len(body) > cap:
            body = body[:cap] + " [shortened]"
        text = (f"[{x['id']}] {x['kind']} | role: {x['role']} | {x['source']} | dated {x.get('date') or 'undated'} | "
                f"grade {x['grade']} | {x['title']}\n{body}")
        if used + len(text) > DIGEST_TOTAL_CHARS:
            parts.append(f"[{x['id']}] {x['kind']} | {x['title']} (not shown here: the digest is full)")
            continue
        used += len(text)
        parts.append(text)
    return "\n\n".join(parts)


# ---- the three analysts ----------------------------------------------------------------

def _money(x: float) -> str:
    for unit, size in (("B", 1e9), ("M", 1e6)):
        if abs(x) >= size:
            return f"${x / size:.2f}{unit}"
    return f"${x:,.0f}"


def results_finding(store, request_id: str | None) -> tuple[dict | None, str | None]:
    """The results-against-estimates finding, built in code from the two numbers of
    the latest report. Returns (finding, what was unavailable). The model sets
    neither its text nor its bearing. It cites the data provider's figures, so
    it always grades moderate (recent and specific, not a primary source)."""
    reports = [i for i in store.evidence(request_id) if i["kind"].startswith("reported earnings") and i.get("date")]
    if not reports:
        return None, "results against estimates (no reported earnings in the evidence)"
    item = max(reports, key=lambda i: i["date"])
    b = item["body"]
    tol = settings_stage2()["results_tolerance_pct"]
    sides, parts = [], []
    for name, act, est, fmt in (("EPS", b.get("eps_actual"), b.get("eps_estimated"), lambda v: f"${v:.2f}"),
                                ("revenue", b.get("revenue_actual"), b.get("revenue_estimated"), _money)):
        if act is None or est in (None, 0):
            return None, f"results against estimates ({name} estimate not available for the report of {item['date']})"
        diff = (act - est) / abs(est) * 100
        sides.append("above" if diff > tol else "below" if diff < -tol else "in line")
        parts.append((name, fmt(act), fmt(est), round(diff, 1)))
    if "above" in sides and "below" not in sides:
        bearing, how = "supports_bullish", "above estimates"
    elif "below" in sides and "above" not in sides:
        bearing, how = "supports_bearish", "below estimates"
    elif "above" in sides:
        bearing, how = "none", "mixed against estimates"
    else:
        bearing, how = "none", "in line with estimates"
    (n1, a1, e1, d1), (n2, a2, e2, d2) = parts
    text = (f"{n1} {a1} against {e1} expected ({d1:+.1f}%); {n2} {a2} against {e2} expected ({d2:+.1f}%). "
            f"Results {how}, reported {item['date']}.")
    reason = None if bearing != "none" else "mixed" if "mixed" in how else "in_line"
    return {"id": "F1", "text": text, "evidence_ids": [item["id"]], "kind": "results_vs_estimates",
            "bearing": bearing, "set_by": "code", "standing_disclosure": False, "context_reason": reason,
            "context_sentence": agents.CONTEXT_SENTENCE.get(reason),
            "comparison": {"eps": sides[0], "revenue": sides[1], "tolerance_pct": tol,
                           "eps_diff_pct": d1, "revenue_diff_pct": d2}}, None


_UNIT = {"trillion": 1e12, "billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "mm": 1e6, "m": 1e6,
         "thousand": 1e3, "k": 1e3}
_FIGURE = re.compile(r"(?<![\w.,])(-)?\$?\s?(\d[\d,]*(?:\.\d+)?)\s*(trillion|billion|million|thousand|bn|mm|[bmk])?(?![\w])",
                     re.IGNORECASE)
_NOT_FIGURES = re.compile(r"\([^)]*\)|\b\d{4}-\d{2}-\d{2}\b|\b(fy|fiscal(\s+year)?)\s?\d{2,4}\b|(?<![$\d.,])\b(19|20)\d{2}\b(?![.,]\d)",
                          re.IGNORECASE)


def quoted_figures(text: str) -> list[float]:
    """The figures in a quoted guidance or consensus string, in plain units. A unit
    written once after a range ("$62.0 to $64.0 billion") applies to both ends.
    Text in brackets, dates and fiscal years are not figures."""
    found = [(float(m.group(2).replace(",", "")) * (-1 if m.group(1) else 1), (m.group(3) or "").lower())
             for m in _FIGURE.finditer(_NOT_FIGURES.sub(" ", text or ""))]
    if found and found[-1][1] and not any(u for _, u in found[:-1]):
        found = [(v, found[-1][1]) for v, _ in found]
    return [v * _UNIT.get(u, 1) for v, u in found]


def guidance_vs_consensus(now: str, before: str, tolerance_pct: float) -> dict:
    """Guidance against consensus, set in code from the two quoted figures (operator
    ruling, 19 November 2026). A guided range that contains the consensus figure is
    in line; a range wholly above it is above, wholly below it is below. A single
    guided figure within the tolerance of consensus is in line."""
    g, c = quoted_figures(now), quoted_figures(before)
    if not g or len(set(c)) != 1 or c[0] == 0:
        return {"result": "unreadable", "set_by": "code"}
    lo, hi, cons = min(g), max(g), c[0]
    # The two may be quoted in different units ("$80,000" in millions against "$81,433 million").
    mid = (lo + hi) / 2
    scale = next((1000.0 ** k for k in (0, 1, -1, 2, -2, 3, -3) if cons and 0.5 <= mid * 1000.0 ** k / cons <= 2), None)
    if scale is None:
        return {"result": "unreadable", "set_by": "code"}
    lo, hi = lo * scale, hi * scale
    if lo < hi:
        result = "in_line" if lo <= cons <= hi else "above" if lo > cons else "below"
    else:
        diff = (lo - cons) / abs(cons) * 100
        result = "in_line" if abs(diff) <= tolerance_pct else "above" if diff > 0 else "below"
    return {"result": result, "guided_low": lo, "guided_high": hi, "consensus": cons, "range": lo < hi,
            "tolerance_pct": tolerance_pct, "set_by": "code"}


_VS_CONSENSUS = {"above": "supports_bullish", "below": "supports_bearish"}

# ---- every guidance bearing is set in code (operator decision, 19 November 2026) ----------
# Only these measures can carry a bearing. Anything else that is guided (capital expenditure,
# costs, tax rate, share count, cash flow, a segment's revenue) is context.
_MEASURE = {"eps": "eps", "earnings per share": "eps", "revenue": "revenue", "revenues": "revenue", "sales": "revenue",
            "operating income": "operating income", "operating profit": "operating income",
            "operating margin": "operating margin"}
_FILLER = re.compile(r"\([^)]*\)|\b(adjusted|non gaap|gaap|core|underlying|diluted|basic|reported|as reported|full year|"
                     r"fiscal year|fiscal|annual|total|net|consolidated|company|constant currency|cc|organic|comparable|"
                     r"estimated|and|the|of|in|fy ?\d{2,4}|(19|20)\d{2})\b", re.IGNORECASE)
_BASIS = [("adjusted", r"adjusted|non[- ]?gaap|core|underlying"), ("reported", r"\bgaap\b|reported")]
_BULLISH, _BEARISH = {"raised", "above"}, {"lowered", "below"}
GUIDANCE_REASON = {"in_line": "in_line", "reaffirmed": "reaffirmed", "mixed": "guidance_mixed", "worded": "worded_guidance",
                   "measure_no_direction": "measure_no_direction", "not_comparable": "not_comparable",
                   "nothing_to_compare": "other", "unreadable": "other"}


def measure_key(measure: str) -> tuple[str, bool] | None:
    """(measure, whether it is a growth rate) if it is one of the measures that can carry a
    bearing: EPS, revenue or net sales, operating income or operating margin. Otherwise None."""
    text = re.sub(r"[-_/,]", " ", (measure or "").lower())
    growth = bool(re.search(r"\bgrowth\b", text))
    name = " ".join(_FILLER.sub(" ", re.sub(r"\bgrowth\b", " ", text)).split())
    return (_MEASURE[name], growth) if name in _MEASURE else None


def _period_key(period: str):
    text = (period or "").lower()
    year = re.search(r"\b(?:fy ?)?((?:19|20)\d{2})\b", text) or re.search(r"\bfy ?(\d{2})\b", text)
    q = re.search(r"\bq([1-4])\b", text) or re.search(r"\b(first|second|third|fourth)[- ]quarter\b", text)
    quarter = q and {"first": "1", "second": "2", "third": "3", "fourth": "4"}.get(q.group(1), q.group(1))
    if not year:
        return " ".join(text.split())
    y = year.group(1)
    return ("20" + y if len(y) == 2 else y, quarter)


def _basis_key(basis: str) -> str:
    text = (basis or "").lower()
    kinds = [name for name, pat in _BASIS if re.search(pat, text)]
    out = kinds[0] if len(kinds) == 1 else " ".join(text.split())
    return out + (" constant currency" if re.search(r"constant currency|\bcc\b", text) else "")


def _side(x: dict | None) -> tuple[str, list[float], bool]:
    x = x or {}
    text = " to ".join(t.strip() for t in (x.get("low"), x.get("high")) if t and t.strip())
    return text, quoted_figures(text), bool(re.search(r"%|\bpercent\b", text, re.IGNORECASE))


def guidance_comparison(g: dict | None, tolerance_pct: float) -> dict:
    """What a guidance finding amounts to, set in code from the extracted figures. The
    analyst classifies nothing. Against earlier guidance: raised when both ends are at or
    above the earlier ones and at least one is higher; lowered for the reverse; unchanged
    is reaffirmed; narrowed or moved both ways is mixed. Against consensus: a range that
    contains it is in line, wholly above is above, wholly below is below, and a single
    figure within the tolerance is in line."""
    g = g or {}
    now, before, vs = g.get("now") or {}, g.get("before"), g.get("compared_with")
    out = {"set_by": "code", "compared_with": vs}
    key = measure_key(now.get("measure"))
    if key is None:
        return {**out, "result": "measure_no_direction"}
    now_text, now_figs, now_pct = _side(now)
    if not now_figs:
        return {**out, "result": "worded", "passage": g.get("passage")}
    if not before or vs not in ("earlier_guidance", "consensus"):
        return {**out, "result": "nothing_to_compare"}
    b_text, b_figs, b_pct = _side(before)
    if not b_figs:
        return {**out, "result": "worded", "passage": g.get("passage")}
    matches = {"measure": measure_key(before.get("measure")) == key,
               "period": _period_key(before.get("period")) == _period_key(now.get("period")),
               # The data provider does not state the basis of its consensus figures.
               "basis": vs == "consensus" or _basis_key(before.get("basis")) == _basis_key(now.get("basis")),
               "unit": now_pct == b_pct}
    out["matches"] = matches
    if not all(matches.values()):
        return {**out, "result": "not_comparable"}
    if vs == "consensus":
        return {**out, **guidance_vs_consensus(now_text, b_text, tolerance_pct)}
    lo, hi, blo, bhi = min(now_figs), max(now_figs), min(b_figs), max(b_figs)
    # The two sides may be quoted in different units ("$9B" against "$7,500 million"): bring them to the
    # nearest power of a thousand. Percentages are never rescaled.
    ratio = (lo + hi) / (blo + bhi) if (blo + bhi) else 0
    scale = 1.0 if now_pct or ratio <= 0 else 1000.0 ** -round(math.log(ratio, 1000))
    lo, hi = lo * scale, hi * scale
    tiny = 1e-9 * max(abs(blo), abs(bhi), 1e-12)
    d_lo, d_hi = lo - blo, hi - bhi
    up, down = (d_lo > tiny, d_hi > tiny), (d_lo < -tiny, d_hi < -tiny)
    result = ("reaffirmed" if not any(up) and not any(down) else "raised" if not any(down) else
              "lowered" if not any(up) else "mixed")
    return {**out, "result": result, "guided_low": lo, "guided_high": hi, "earlier_low": blo, "earlier_high": bhi}


def settings_stage2() -> dict:
    from . import settings
    return settings.load_json("stage2.json")


PRICE_KINDS = {"past earnings reactions", "price description", "sector context", "market regime"}
_QUARTERLY = re.compile(
    r"\b(q[1-4]|quarter(ly)?|first-quarter|second-quarter|third-quarter|fourth-quarter)\b.{0,80}\b(outlook|guidance|guides?|guided)\b"
    r"|\b(outlook|guidance)\b.{0,80}\b(q[1-4]|quarter)\b", re.IGNORECASE)


def context_reason(f: dict, kind: str, prefix: str, items: dict, latest: str | None) -> str:
    """Why a context finding has no direction. Code sets every reason it can know;
    the analyst's own choice (no_estimate or commentary) is used only for the rest."""
    cited = [items[e] for e in f["evidence_ids"] if e in items]
    if kind == "new_event":
        if agents.EVENT_BEARING.get(f.get("event_kind")) == "none":
            return "event_no_direction"
        return "not_recent"                       # on the list, but it failed the recent test
    if kind == "guidance_change":
        g = f.get("guidance") or {}
        vs = (f.get("comparison") or {}).get("result")
        if vs == "nothing_to_compare" and _QUARTERLY.search(f"{(g.get('now') or {}).get('period', '')} guidance"):
            return "no_quarterly_consensus"
        return GUIDANCE_REASON.get(vs, "other")
    if cited and all(x["kind"] == "macro calendar" for x in cited):
        return "no_macro_expectation"
    if prefix in ("R", "T") or (cited and all(x["kind"] in PRICE_KINDS for x in cited)):
        return "price_description"
    if _QUARTERLY.search(f["finding"]):
        return "no_quarterly_consensus"
    return f.get("context_reason") or "other"


def _analyst_output(r: AgentResult, prefix: str, first: int = 1, items: dict | None = None,
                    latest: str | None = None) -> dict:
    """An analyst's answer as stored. Code, not the analyst, has the last word on
    each bearing: an event takes the bearing of its kind on the list and must be
    recent; a standing disclosure and every sector or macro finding carry none.
    Every finding without a direction gets the reason, from a fixed list."""
    out = r.output.model_dump()
    items = items or {}
    findings, dropped = [], 0
    if prefix == "R":
        # A scheduled macro release goes to the calendar and the risk flags, not to findings.
        kept = [f for f in out["findings"] if not (
            f["evidence_ids"] and all(items.get(e, {}).get("kind") == "macro calendar" for e in f["evidence_ids"]))]
        dropped, out["findings"] = len(out["findings"]) - len(kept), kept
    for n, f in enumerate(out["findings"], first):
        kind, bearing = f.get("kind") or "context", f["bearing"]
        g = f.get("guidance") or {}
        if prefix == "R" or f.get("standing_disclosure"):
            bearing = "none"
        elif kind == "guidance_change":
            # Set in code from the extracted figures; the analyst classifies nothing.
            f["comparison"] = guidance_comparison(g, settings_stage2()["guidance_tolerance_pct"])
            res = f["comparison"]["result"]
            bearing = "supports_bullish" if res in _BULLISH else "supports_bearish" if res in _BEARISH else "none"
        elif kind == "new_event":
            bearing = agents.EVENT_BEARING.get(f.get("event_kind"), "none")
            if bearing != "none" and items and not any(
                    agents.is_recent(items[e].get("date"), latest) for e in f["evidence_ids"] if e in items):
                bearing = "none"                  # not new: reported as context, "too old to count as new"
        elif kind == "context":
            bearing = "none"
        reason = None
        if bearing == "none":
            reason = context_reason(f, "context" if prefix == "R" or f.get("standing_disclosure") else kind,
                                    prefix, items, latest)
            kind = "context"
        findings.append({"id": f"{prefix}{n}", "text": f["finding"], "evidence_ids": f["evidence_ids"],
                         "kind": kind, "bearing": bearing, "guidance": f.get("guidance"),
                         "event_kind": f.get("event_kind"),
                         **({"comparison": f["comparison"]} if f.get("comparison") else {}),
                         "context_reason": reason, "context_sentence": agents.CONTEXT_SENTENCE.get(reason),
                         "standing_disclosure": bool(f.get("standing_disclosure")), "set_by": "analyst",
                         **({"bearing_as_reported": f["bearing"]} if f["bearing"] != bearing else {})})
    out["findings"] = findings
    if dropped:
        out["calendar_findings_dropped"] = dropped
    return {**out, "run": _run_info(r),
            "unavailable": [{"input": f"{u['tool']} {json.dumps(u['input'])}", "reason": u["reason"]}
                            for u in r.unavailable_inputs]}


def fundamental_step(state, ctx) -> dict:
    symbol = state["symbol"]
    items = [x for x in _graded(state, ctx).values() if x["kind"] not in ("market regime", "price description",
                                                                         "sector context", "macro calendar")]
    task = (f"The underlying is {symbol}. Today is {_today().isoformat()}. The stored evidence follows; "
            "each item starts with its evidence id in square brackets.\n\n"
            + wrap_untrusted(_digest(items), "the evidence store"))
    r = require_ok(_run(agents.analyst("fundamental_analyst", _known_ids(ctx), evidence_facts=_evidence_facts(state, ctx)), task, ctx))
    # The results-against-estimates finding is built in code and comes first.
    results, missing = results_finding(ctx.store, ctx.request_id)
    out = _analyst_output(r, "F", first=2 if results else 1, items=_graded(state, ctx),
                          latest=(state.get("figures") or {}).get("latest_earnings_report"))
    if results:
        out["findings"].insert(0, results)
    if missing:
        out["unavailable"].append({"input": missing, "reason": "not served by the data provider"})
    return out


def regime_step(state, ctx) -> dict:
    symbol = state["symbol"]
    items = [x for x in _graded(state, ctx).values() if x["kind"] in ("market regime", "sector context", "macro calendar")]
    kind = ("an equity index fund: macro and policy findings are lead evidence" if symbol in EQUITY_INDICES
            else "a single stock: your findings qualify a view and cannot start one")
    task = (f"The underlying is {symbol}, {kind}. Today is {_today().isoformat()}. "
            "The evidence follows; each item starts with its evidence id in square brackets.\n\n"
            + wrap_untrusted(_digest(items), "computed figures and the macro calendar"))
    r = require_ok(_run(agents.analyst("regime_assessor", _known_ids(ctx), evidence_facts=_evidence_facts(state, ctx)), task, ctx))
    return _analyst_output(r, "R", items=_graded(state, ctx))


def _floats(obj) -> set[float]:
    if isinstance(obj, bool):
        return set()
    if isinstance(obj, (int, float)):
        return {float(obj)}
    if isinstance(obj, dict):
        return set().union(*[_floats(v) for v in obj.values()]) if obj else set()
    if isinstance(obj, list):
        return set().union(*[_floats(v) for v in obj]) if obj else set()
    return set()


def technical_step(state, ctx) -> dict:
    symbol = state["symbol"]
    item = next((x for x in ctx.store.evidence(ctx.request_id) if x["kind"] == "price description"), None)
    if item is None:
        raise StepFailed("error", "The price figures for the Technical Analyst were not computed.")
    body = item["body"]
    task = (f"The underlying is {symbol}. These figures were computed in code from daily closes "
            f"(evidence id {item['id']}):\n{json.dumps(body, indent=1)}")
    r = require_ok(_run(agents.analyst("technical_analyst", _known_ids(ctx), lambda: _floats(body["levels"]) | {float(body["last_close"])}), task, ctx))
    return {**_analyst_output(r, "T"), "evidence_id": item["id"], "figures": body}


# ---- Thesis agent ----------------------------------------------------------------------

def _best(cited: list[str], items: dict) -> dict | None:
    found = [items[e] for e in cited if e in items]
    return max(found, key=lambda x: (evidence.ORDER[x["grade"]], x["primary_source"], x.get("date") or "")) if found else None


def enrich_findings(state, items: dict) -> dict:
    """Every analyst finding with what code attaches: grade, checks, source, date,
    family, whether it is from a primary source and whether it is lead evidence."""
    symbol = state["symbol"]
    out = {}
    for analyst in ("fundamental_analyst", "regime_assessor"):
        o = ((state.get("findings") or {}).get(analyst) or {}).get("output") or {}
        for f in o.get("findings", []):
            best = _best(f["evidence_ids"], items)
            cited = [items[e] for e in f["evidence_ids"] if e in items]
            # A finding carries a direction ("lead") only as one of the three bearing kinds.
            lead = (analyst == "fundamental_analyst" and f.get("kind") in agents.BEARING_KINDS
                    and f["bearing"] != "none" and symbol not in FUNDS)
            out[f["id"]] = {**f, "analyst": analyst, "grade": best["grade"] if best else "weak",
                            "ungraded": best is None, "checks": best["checks"] if best else None,
                            "primary_source": bool(best and best["primary_source"]),
                            "family": best["family"] if best else None, "source": best["source"] if best else None,
                            "date": best.get("date") if best else None, "lead": lead}
    return out


def _risk_flags(state, rec: dict, today: dt.date) -> list[dict]:
    flags = []
    for analyst in ("fundamental_analyst", "regime_assessor"):
        o = ((state.get("findings") or {}).get(analyst) or {}).get("output") or {}
        flags += [{**f, "raised_by": analyst} for f in o.get("risk_flags", [])]
    days = rec.get("recommended_days")
    if days and days <= 14:
        for e in horizon.events_inside((state.get("figures") or {}).get("events", []), today, days):
            if e["kind"] == "fomc":
                flags.append({"flag": "fed_decision_inside_a_short_horizon", "evidence_ids": [e["evidence_id"]],
                              "event_date": e["date"], "note": "", "raised_by": "code"})
    return flags


def build_facts(state, rec: dict, findings: dict, series, today: dt.date) -> dict:
    """The measured facts handed to the Thesis agent, each with an id it can cite.
    Code computes every number and every day count; the agent calculates nothing."""
    fig = state["figures"]
    m = fig["measured"]
    facts, n = {}, 0

    def add(kind: str, text: str, **extra) -> str:
        nonlocal n
        n += 1
        facts[f"M{n}"] = {"id": f"M{n}", "kind": kind, "text": text, **extra}
        return f"M{n}"
    days = rec.get("recommended_days")
    status = {r["days"]: r for r in rec["rows"]}
    for row in m["horizons"]:
        if row["context_only"]:
            continue
        s = status.get(row["days"], {})
        add("row", f"{row['days']}-day row: base rate of a higher close {row['base_rate_pct']}% "
                   f"({row['base_rate_basis']}); typical realized move plus or minus {row['typical_move_pct']}%. "
                   f"Horizon rule: {s.get('status', 'not a candidate')}.", days=row["days"])
    if days:
        end = today + dt.timedelta(days=days)
        add("horizon", f"Recommended horizon: {days} days, ending {end.isoformat()}. It is set by a fixed rule: "
                       "the candidate row nearest 30 days that has eligible contracts and does not span an earnings "
                       "report or a flagged binary event." + (f" Warning: {rec['warning']}" if rec.get("warning") else ""))
    latest = fig.get("latest_earnings_report")
    if latest:
        ago = (today - dt.date.fromisoformat(latest[:10])).days
        add("latest_report", f"The latest earnings report was on {latest[:10]}, {_days(ago)} ago.", days_ago=ago)
    vol = m["volatility"]
    add("volatility", f"Volatility state: {vol['state'] or 'not available'}"
        + (f" (20-day realised volatility is {vol['ratio']} times its one-year median)." if vol.get("ratio") else "."))
    earnings_inside = []
    for e in fig["events"]:
        d = dt.date.fromisoformat(e["date"])
        day = (d - today).days
        if 0 <= day <= 100:
            inside = " It falls inside the recommended horizon." if days and day <= days else \
                     " It falls after the recommended horizon." if days else ""
            fid = add("event", f"{e['label'][0].upper() + e['label'][1:]} on {e['date']}, {_days(day)} from today."
                               + inside + (" " + e["note"][0].upper() + e["note"][1:] + "." if e.get("note") else ""),
                      event=e["kind"], date=e["date"], day=day)
            if e["kind"] == "earnings" and days and day <= days:
                earnings_inside.append(fid)
    if not any(e["kind"] == "earnings" for e in fig["events"]) and state["symbol"] not in FUNDS:
        add("event", "The date of the next earnings report is not available.")
    seen = set()
    for f in findings.values():
        if f.get("date") and f["date"] not in seen and f["bearing"] != "none":
            seen.add(f["date"])
            mv = context.move_since(series, f["date"]) if series else None
            if mv is not None:
                add("price_move_since", f"Since the close before {f['date']} (the date of the evidence behind {f['id']}) "
                                        f"the closing price has changed by {mv:+.1f}%.", date=f["date"], move_pct=mv)
    add("unavailable", "Inputs that were not available: " + "; ".join(
        NOT_SERVED + [u["input"] for u in _all_unavailable(state)]) + ".")
    return {"facts": facts, "earnings_fact_ids_inside": earnings_inside}


def _all_unavailable(state) -> list[dict]:
    out = []
    for key in ("figures", "evidence", "grades"):
        out += (state.get(key) or {}).get("unavailable", [])
    for a in (state.get("findings") or {}).values():
        out += (a.get("output") or {}).get("unavailable", [])
    seen, uniq = set(), []
    for u in out:
        if u["input"] not in seen:
            seen.add(u["input"])
            uniq.append(u)
    return uniq


def thesis_step(state, ctx) -> dict:
    symbol, today = state["symbol"], _today()
    fig = state["figures"]
    items = _graded(state, ctx)
    findings = enrich_findings(state, items)
    # The horizon is recommended by rule before the agent runs; it explains it, it does not choose it.
    pre_flags = _risk_flags(state, {}, today)
    span = [e for e in fig["events"] if e["kind"] == "earnings"] + \
           [{"kind": "binary_event", "label": "flagged binary event", "date": f["event_date"]}
            for f in pre_flags if f["flag"] == "pending_binary_event" and f.get("event_date")]
    rec = horizon.recommend(today, span, fig.get("eligible_contracts"))
    flags = _risk_flags(state, rec, today)
    series = context.fetch(figures.HISTORY_OF.get(symbol, symbol), ctx.store)
    built = build_facts(state, rec, findings, series, today)
    record = {"findings": findings, "facts": built["facts"], "evidence": items, "risk_flags": flags,
              "horizon": {**rec, "earnings_fact_ids_inside": built["earnings_fact_ids_inside"]}}

    for_agent = {a: {"status": "ok", "output": [
        {k: f.get(k) for k in ("id", "text", "kind", "bearing", "grade", "guidance", "comparison", "event_kind",
                               "family", "source", "date")}
        for f in findings.values() if f["analyst"] == a]} for a in ("fundamental_analyst", "regime_assessor")}
    tech = ((state.get("findings") or {}).get("technical_analyst") or {}).get("output") or {}
    kind = ("an equity index fund" if symbol in EQUITY_INDICES else "a fund" if symbol in FUNDS else "a single stock")
    task = "\n\n".join([
        f"The underlying is {symbol}, {kind}. Today is {today.isoformat()}.",
        "FINDINGS (kind, bearing and grade as checked or set by code):\n" + findings_for_thesis(for_agent),
        "RISK FLAGS RAISED: " + (json.dumps([{k: f[k] for k in ("flag", "event_date", "note")} for f in flags])
                                 if flags else "none"),
        "MEASURED FACTS (computed in code; cite by id):\n" + "\n".join(f"{i}: {f['text']}" for i, f in built["facts"].items()),
        "PRICE DESCRIPTION (description only; it has no id and may not be cited or used to support a direction):\n"
        + wrap_untrusted(json.dumps({k: tech.get(k) for k in ("price_description", "timeframes")}, ensure_ascii=False),
                         "the Technical Analyst"),
    ])
    cfg = agents.thesis(lambda draft: validation.check(draft, record))
    r = _run(cfg, task, ctx)
    if r.ok:
        draft, failed = r.output, []
    elif r.status == "failed_validation" and r.rejected_output is not None:
        draft, failed = r.rejected_output, r.errors      # shown to the user with the failed checks
    else:
        raise _failure(r)
    d = draft.model_dump()
    days = rec.get("recommended_days")
    row = next((x for x in fig["measured"]["horizons"] if x["days"] == days), None)
    common = {
        "branches": d["branches"], "findings": findings, "facts": built["facts"], "risk_flags": flags,
        "horizon": rec, "recommended_horizon_days": days, "primary_horizon_days": days,
        "inputs_unavailable": NOT_SERVED + [u["input"] for u in _all_unavailable(state)],
        "technical": {k: tech.get(k) for k in ("price_description", "timeframes", "levels")},
        "validation": {"ok": not failed, "failed_checks": failed, "returned_once": r.returned, "in_harness": True},
        "view_origin": "agents", "thesis_origin": "system", "system_draft": d, "run": _run_info(r),
        "report_dates": report_dates(fig, today),
        "horizon_reasons_code": horizon_reasons(rec, today, fig["events"]),
        **validation.code_fields(draft, record),
    }
    if common.get("support") == "weak" and fig.get("latest_earnings_report"):
        ago = (today - dt.date.fromisoformat(fig["latest_earnings_report"][:10])).days
        common["support_note"] = f"This view rests on the earnings result alone, reported {_days(ago)} ago."
    if draft.view == "no_view":
        out = {"no_view": True, "kind": draft.no_view_kind, "reason": draft.no_view_reason, **common}
        out["no_view_text"] = no_view_text(symbol, out["no_view_reason_code"], draft.no_view_kind, findings, flags,
                                           [u["input"] for u in _all_unavailable(state)], draft.no_view_reason)
        # "Take a view yourself" needs at least one evidence item to rely on.
        out["own_view_allowed"] = bool(findings)
        out["own_view_options"] = own_view_options(state, out)
        return out
    up = row["base_rate_pct"] if row else None
    base = None if up is None else (up if draft.view == "bullish" else round(100 - up, 1))
    move = row["typical_move_pct"] if row else None
    ref = fig["measured"]["reference_close"]
    against = -1 if draft.view == "bullish" else 1
    falsifiers = [{**f, "set_by": "agent"} for f in d["falsifiers"]]
    if common.get("support") == "weak":
        # Set in code from a fixed set; what the agent wrote is added and never stands alone.
        basis = next((i for i in d["supporting"] if findings.get(i, {}).get("kind") == "results_vs_estimates"), None)
        falsifiers = results_only_conditions(draft.view, basis, common["report_dates"]) + falsifiers
    return {
        "view": draft.view, "basis": d["basis"], "summary": d["summary"], "rationale": d["rationale"],
        "horizon_reasons": d["horizon_reasons"], "resolution_criterion": d["resolution_criterion"],
        "falsifiers": falsifiers, "supporting": d["supporting"], "opposing": d["opposing"],
        "catalyst": d["catalyst"], "view_base_rate_pct": base, "view_probability_pct": None,
        "runs_against_base_rate": base is not None and base < 50,
        "risk_reference": None if row is None or move is None else {
            "level": round(ref * (1 + against * move / 100), 2), "usual_ranges_away": 1,
            "side": "below" if against < 0 else "above",
            "crossed_pct": row["crossed_below_pct"] if against < 0 else row["crossed_above_pct"]},
        **common,
    }


def _list(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def horizon_reasons(rec: dict, today: dt.date, events: list[dict]) -> list[str]:
    """Why the row is recommended, built in code from the rule that chose it
    (operator decision, 19 November 2026): which rows had eligible contracts,
    which were set aside and why, that the recommended row is the one nearest 30
    days of those left, and any known event inside it."""
    rows, pick = rec["rows"], rec.get("recommended_days")
    out = []
    if rec.get("provisional"):
        out.append("Option data was not available, so rows were not checked for eligible contracts. "
                   "The recommendation is provisional.")
    else:
        have = [f"{r['days']}-day" for r in rows if r["has_contracts"]]
        lack = [f"{r['days']}-day" for r in rows if not r["has_contracts"]]
        if have:
            out.append(f"Rows with eligible contracts: {_list(have)}.")
        if lack:
            out.append(f"No eligible contracts: the {_list(lack)} row{'s' if len(lack) > 1 else ''}.")
    for r in rows:
        if r["has_contracts"] and r["spans"] and r["status"] == "spans an event":
            what = _list([f"{e.get('label') or e['kind']} on {e['date']}" for e in r["spans"]])
            out.append(f"The {r['days']}-day row was set aside: it spans the {what}.")
    if pick is None:
        out.append("No row has eligible contracts, so no horizon is recommended.")
        return out
    out.append(f"The {pick}-day row is the one nearest 30 days of those left.")
    if rec.get("warning"):
        out.append(f"Warning: {rec['warning']} No row was set aside.")
    inside = horizon.events_inside(events, today, pick)
    if inside:
        out.append("Known events inside it: " + "; ".join(
            f"{e['label']} on {e['date']} (day {e['day']})" for e in inside) + ".")
    else:
        out.append("No known event falls inside it.")
    return out


FLAG_NAME = {
    "going_concern_or_liquidity_warning": "a going-concern or liquidity warning",
    "announced_merger_or_takeover_target": "an announced takeover of the company",
}


def no_view_text(symbol: str, code: str, kind: str | None, findings: dict, flags: list[dict],
                 unavailable: list[str], reason: str | None) -> dict:
    """The headline and the sentences under it for a no view. Fixed wording set in
    code (operator decision, 19 November 2026); the model writes none of it."""
    if code == "conflict":
        up = [f["text"] for f in findings.values() if f.get("lead") and f["bearing"] == "supports_bullish"]
        down = [f["text"] for f in findings.values() if f.get("lead") and f["bearing"] == "supports_bearish"]
        return {"case": "conflict", "headline": "The evidence that carries a direction points both ways",
                "sentences": ["Pointing higher: " + " ".join(up), "Pointing lower: " + " ".join(down),
                              "The system does not choose between two solid findings that disagree."]}
    if code == "declined":
        names = _list([FLAG_NAME.get(f["flag"], f["flag"].replace("_", " ")) for f in flags
                       if f["flag"] in agents.SEVERE_FLAGS])
        return {"case": "declined", "headline": "The system declined to take a view",
                "sentences": [f"A severe flag was raised: {names}.",
                              "A stock in this position trades on that outcome, not on its results."],
                "override_note": "This is an override. The flag stays attached to your thesis and is recorded."}
    if code == "nothing_carries_a_direction" and kind != "insufficient_data":
        n = len(findings)
        s = [f"The system found {n} fact{'' if n == 1 else 's'} about {symbol}. "
             "None comes with a comparison that gives it a direction."]
        res = next((f for f in findings.values() if f.get("kind") == "results_vs_estimates"
                    or f.get("context_reason") in ("in_line", "mixed")), None)
        if res and res.get("context_reason") == "in_line":
            s.append("The latest results were in line with estimates.")
        elif res and res.get("context_reason") == "mixed":
            s.append("The latest results were mixed against estimates: one measure above, one below.")
        return {"case": "nothing", "headline": "Nothing found carries a direction", "sentences": s}
    if kind == "insufficient_data":
        return {"case": "insufficient", "headline": "Not enough data to form a view",
                "sentences": ["Missing: " + "; ".join(unavailable) + "." if unavailable else
                              "Too little evidence was available."]}
    # The agent returned no view although the rules would have allowed one. It may decline.
    return {"case": "agent_declined", "headline": None, "sentences": [reason or ""]}


def report_dates(fig: dict, today: dt.date) -> dict:
    """The age of the latest earnings report and the date of the next one, shown
    prominently on the brief (operator ruling, 19 November 2026)."""
    latest = fig.get("latest_earnings_report")
    nxt = next((e["date"] for e in fig.get("events", []) if e["kind"] == "earnings"), None)
    out = {"latest_report": latest[:10] if latest else None, "latest_report_days_ago": None,
           "next_report": nxt, "next_report_days_from_today": None}
    if latest:
        out["latest_report_days_ago"] = (today - dt.date.fromisoformat(latest[:10])).days
    if nxt:
        out["next_report_days_from_today"] = (dt.date.fromisoformat(nxt[:10]) - today).days
    return out


def results_only_conditions(view: str, finding_id: str | None, dates: dict) -> list[dict]:
    """The fixed invalidation conditions for a view that rests on the earnings
    result alone (operator ruling, 19 November 2026): guidance changed against
    the view; a defined event against the view; and the next earnings result
    going against it, when its date is known."""
    bull = view == "bullish"
    out = [
        {"finding_id": finding_id, "type": "guidance_change", "set_by": "code",
         "trigger": "Guidance is cut" if bull else "Guidance is raised",
         "reverses": "A new finding against the view", "action": "Treat the thesis as no longer holding."},
        {"finding_id": finding_id, "type": "new_filing", "set_by": "code",
         "trigger": ("A defined event against the view is reported: a share offering, new material litigation or "
                     "regulatory action, an impairment, exit costs, non-reliance on earlier statements, or the "
                     "unplanned departure of the chief executive or chief financial officer" if bull else
                     "The company raises guidance outside an earnings report"),
         "reverses": "A new finding against the view", "action": "Treat the thesis as no longer holding."},
    ]
    if dates.get("next_report"):
        out.insert(0, {"finding_id": finding_id, "type": "earnings_result", "set_by": "code",
                       "trigger": (f"The next earnings result, due {dates['next_report']}, "
                                   + ("misses consensus" if bull else "beats consensus")),
                       "reverses": "Reverses the basis", "action": "Treat the thesis as no longer holding."})
    return out


def _failure(r: AgentResult) -> StepFailed:
    try:
        require_ok(r)
    except StepFailed as e:
        return e
    return StepFailed("agent_failed", r.message, agent=r.agent)


def validate_step(state, ctx) -> dict:
    """The check itself ran on the harness, as the Thesis agent's output check
    (one return in total). This step reports its result to the workflow."""
    return dict(state["thesis"]["validation"])


# ---- the range-bound rule --------------------------------------------------------------

def range_rule_step(state, ctx) -> dict:
    symbol, today = state["symbol"], _today()
    t = state.get("thesis") or {}
    fig = state["figures"]
    view = None if t.get("no_view") else t.get("view")
    events, unchecked = [], []
    for e in fig["events"]:
        if e["kind"] in ("earnings", "fomc"):
            events.append(e)
        elif e["kind"] == "data_release" and symbol in FUNDS and \
                e["label"] in ("Consumer Price Index", "Employment Situation"):
            events.append({**e, "max_row_days": 7})
    events += [{"kind": "binary_event", "label": f["flag"], "date": f["event_date"]}
               for f in t.get("risk_flags", []) if f.get("event_date") and f["flag"] == "pending_binary_event"]
    if symbol in EQUITY_INDICES:
        unchecked.append("heavy earnings period (no source for the holdings' report dates)")
    if symbol not in FUNDS and not any(e["kind"] == "earnings" for e in fig["events"]):
        unchecked.append("the next earnings date")
    out = horizon.range_bound(view, fig["measured"]["volatility"]["state"], today, events, unchecked)
    if out["range_bound"]:
        out["horizon"] = horizon.recommend(today, [], fig.get("eligible_contracts"), range_bound=True)
    return out


# ---- "Take a view yourself" ------------------------------------------------------------

# Conditions the system can name for a thesis the user enters. Two apply to every thesis;
# an event on the brief adds the condition that would reverse it, for a view that rests on it.
GENERAL_CONDITIONS = [
    {"id": "earnings_result", "type": "earnings_result", "text": "The next earnings result goes against the view"},
    {"id": "guidance_change", "type": "guidance_change", "text": "Guidance is changed against the view"},
]
EVENT_REVERSAL = {
    "ceo_or_cfo_departure_unplanned_or_no_permanent_successor":
        ("new_filing", "A permanent chief executive or chief financial officer is named"),
    "share_offering_or_shelf_registration": ("new_filing", "The offering is withdrawn"),
    "new_material_litigation_or_regulatory_action": ("dated_event_outcome", "The action is dismissed or settled"),
}


def nameable_conditions(findings: dict, direction: str) -> list[dict]:
    out = [dict(c) for c in GENERAL_CONDITIONS]
    for f in findings.values():
        rev = EVENT_REVERSAL.get(f.get("event_kind") or "")
        if rev and f["bearing"] == validation.SUPPORTS[direction]:
            out.append({"id": f"reverses_{f['id']}", "type": rev[0], "text": rev[1], "finding_id": f["id"],
                        "note": f"For a {direction} view resting on this event"})
    return out


def own_view_options(state, thesis: dict) -> dict:
    """What the "Take a view yourself" screen offers: the rows of the measured
    table, the evidence on the brief, and the conditions the system can name."""
    rows = [r["days"] for r in state["figures"]["measured"]["horizons"] if not r["context_only"]]
    return {"horizons": rows, "recommended_days": thesis.get("recommended_horizon_days"),
            "evidence": [{"id": f["id"], "text": f["text"], "bearing": f["bearing"],
                          "kind": "anchored" if f["bearing"] != "none" else "context"}
                         for f in thesis["findings"].values()],
            "conditions": {d: nameable_conditions(thesis["findings"], d) for d in ("bullish", "bearish")}}


def user_thesis_step(state, ctx) -> dict:
    """The thesis the user enters after a no view (decision of 18 November 2026,
    section 6). Raises ValueError with a plain message when the entry is not
    complete; the verdict is computed in code and blocks nothing."""
    t, entry = state["thesis"], state.get("user_input") or {}
    findings = t["findings"]
    direction = entry.get("direction")
    if direction not in ("bullish", "bearish"):
        raise ValueError("Choose a direction: bullish or bearish.")
    opts = own_view_options(state, t)
    days = entry.get("horizon_days") or opts["recommended_days"]
    if days not in opts["horizons"]:
        raise ValueError("Choose a horizon from the measured table.")
    chosen = [i for i in (entry.get("relied_on") or []) if i in findings]
    if not chosen:
        raise ValueError("Choose at least one item you are relying on.")
    offered = {c["id"]: c for c in opts["conditions"][direction]}
    conditions = [offered[c] for c in (entry.get("conditions") or []) if c in offered]
    if not conditions:
        raise ValueError("Choose at least one condition that would prove you wrong.")
    v = validation.user_verdict(direction, chosen, findings)
    row = next((x for x in state["figures"]["measured"]["horizons"] if x["days"] == days), {})
    up = row.get("base_rate_pct")
    return {
        "thesis_origin": "user", "view": direction, "view_origin": "user",
        "primary_horizon_days": days, "recommended_horizon_days": opts["recommended_days"],
        "relied_on": v["relied_on"], "opposing": v["opposing"], "verdict": v["verdict"],
        "falsifiers": [{"type": c["type"], "trigger": c["text"], "finding_id": c.get("finding_id")} for c in conditions],
        "resolution_criterion": ("The close at the horizon is above the reference close." if direction == "bullish"
                                 else "The close at the horizon is below the reference close."),
        "view_base_rate_pct": None if up is None else (up if direction == "bullish" else round(100 - up, 1)),
        "view_probability_pct": None,
        "entered_after_no_view": {"kind": t.get("kind"), "reason_code": t.get("no_view_reason_code"),
                                  "reason": t.get("reason")},
    }


STEPS = {"user_thesis": user_thesis_step, "figures": figures_step, "retriever": retriever_step, "grades": grades_step,
         "fundamental_analyst": fundamental_step, "regime_assessor": regime_step,
         "technical_analyst": technical_step, "thesis": thesis_step, "validate": validate_step,
         "range_rule": range_rule_step}
