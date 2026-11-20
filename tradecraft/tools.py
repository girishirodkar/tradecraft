"""The data tools agents may be given, registered on the harness.

Each agent's configuration names the few it may call; the harness refuses the
rest. No tool here returns an option price, an implied volatility or a stock
quote, and none can place an order or change a setting.

Text written outside the system (news, filings, company descriptions) comes
from tools marked `untrusted`: the harness wraps it as data before a model
sees it.

What a tool returns is also written to the evidence store (tradecraft/evidence.py)
and comes back carrying evidence ids, which the agents cite.
"""
from __future__ import annotations

from dataclasses import replace

from . import evidence, testfail
from .data import directory, edgar, fmp, macro
from .harness import Tool, ToolContext, ToolRegistry, ToolUnavailable

SYMBOL = {"type": "string", "description": "A listed ticker symbol, for example NVDA."}


def _symbol(ctx: ToolContext, symbol: str) -> str:
    s = (symbol or "").strip().upper()
    if not directory.is_listed(s, ctx.store):
        raise ToolUnavailable(f"'{symbol}' is not a listed symbol")
    return s


def _section_chars(ctx: ToolContext) -> int:
    """How much of a filing section one call returns: within the per-document limit
    and small enough that the harness does not shorten the result (a shortened
    part would hide text the agent believes it has read)."""
    t = ctx.limits["text"]
    return min(ctx.max_document_chars(), t["max_tool_result_tokens"] * t["chars_per_token_estimate"] - 2_500)


def _wrap(fn, *errors):
    """Turn a source's own 'cannot supply this' into ToolUnavailable (not retried)."""
    def run(ctx: ToolContext, **kw):
        try:
            return fn(ctx, **kw)
        except errors as e:
            raise ToolUnavailable(str(e)) from e
    return run


def _obj(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


def _fail_once(name: str, fn):
    """Developer-only (tradecraft/testfail.py), off by default: the first call to the named
    tool in a request fails, so the harness's one retry of a failing tool can be seen."""
    def run(ctx: ToolContext, **kw):
        if name == testfail.tool() and testfail.take("stage2_source_fail_once", ctx.request_id):
            raise testfail.TestFailure(f"a test failure, made by the developer switch stage2_source_fail_once "
                                       f"on the first call to {name}")
        return fn(ctx, **kw)
    return run


def build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    # Everything a tool returns is stored as evidence, item by item, and handed back with its ids.
    add = lambda t: reg.register(replace(t, fn=_fail_once(t.name, evidence.capturing(t.name, t.fn))))   # noqa: E731

    add(Tool("get_company_profile",
             "Name, sector, industry and a short business description for one company or fund. No prices.",
             _obj({"symbol": SYMBOL}, ["symbol"]),
             _wrap(lambda ctx, symbol: fmp.profile(_symbol(ctx, symbol), ctx.store), fmp.NotServed),
             untrusted=True, source="FMP company profile"))

    add(Tool("get_earnings",
             "The next earnings report date (no time of day is available) and the last eight reports with "
             "actual and estimated EPS and revenue.",
             _obj({"symbol": SYMBOL}, ["symbol"]),
             _wrap(lambda ctx, symbol: fmp.earnings(_symbol(ctx, symbol), ctx.store), fmp.NotServed)))

    add(Tool("get_dividends",
             "The next declared ex-dividend date, if any, and recent dividends.",
             _obj({"symbol": SYMBOL}, ["symbol"]),
             _wrap(lambda ctx, symbol: fmp.dividends(_symbol(ctx, symbol), ctx.store), fmp.NotServed)))

    add(Tool("get_analyst_estimates",
             "The current annual analyst consensus (EPS and revenue) by fiscal year. Current figures only: "
             "no revision history is available.",
             _obj({"symbol": SYMBOL}, ["symbol"]),
             _wrap(lambda ctx, symbol: fmp.analyst_estimates(_symbol(ctx, symbol), ctx.store), fmp.NotServed)))

    add(Tool("get_company_news",
             "Recent news items about one company: date, publisher, headline and a short excerpt.",
             _obj({"symbol": SYMBOL, "limit": {"type": "integer", "minimum": 1, "maximum": 20}}, ["symbol"]),
             _wrap(lambda ctx, symbol, limit=10: fmp.news(_symbol(ctx, symbol), ctx.store, limit), fmp.NotServed),
             untrusted=True, source="FMP company news"))

    add(Tool("list_filings",
             "The company's most recent 10-K, 10-Q and 8-K filings with filing dates and accession numbers. "
             "For an 8-K, the item numbers say what it reports (2.02 is an earnings release).",
             _obj({"symbol": SYMBOL}, ["symbol"]),
             _wrap(lambda ctx, symbol: edgar.list_filings(_symbol(ctx, symbol), ctx.store), edgar.FilingUnavailable)))

    add(Tool("list_filing_sections",
             "What one filing contains: the Items of a 10-K or 10-Q, or the documents of an 8-K (cover page "
             "and exhibits such as the earnings release), each with its approximate size. Call this before "
             "reading, then read only the sections you need.",
             _obj({"symbol": SYMBOL, "accession": {"type": "string", "description": "From list_filings."}},
                  ["symbol", "accession"]),
             _wrap(lambda ctx, symbol, accession: edgar.list_sections(_symbol(ctx, symbol), accession, ctx.store),
                   edgar.FilingUnavailable)))

    add(Tool("read_filing_section",
             "The text of one section of a filing, as named by list_filing_sections. Long sections come in "
             "parts; ask for a later part only if you need it.",
             _obj({"symbol": SYMBOL, "accession": {"type": "string"},
                   "document": {"type": "string", "description": "The document name from list_filing_sections."},
                   "section": {"type": "string", "description": "For example 'Item 2', or 'whole document'."},
                   "part": {"type": "integer", "minimum": 1}},
                  ["symbol", "accession", "document"]),
             _wrap(lambda ctx, symbol, accession, document, section="whole document", part=1:
                   edgar.read_section(_symbol(ctx, symbol), accession, document, section, part, ctx.store,
                                      max_chars=_section_chars(ctx)),
                   edgar.FilingUnavailable),
             untrusted=True, source="SEC EDGAR filing"))

    add(Tool("get_macro_calendar",
             "Scheduled FOMC decision dates (Federal Reserve) and scheduled dates of major data releases "
             "(CPI, Employment Situation, GDP, Personal Income and Outlays; from FRED) in the coming months. "
             "Release dates are published only a few weeks ahead; the result says how far they reach.",
             _obj({"days_ahead": {"type": "integer", "minimum": 1, "maximum": 365}}, []),
             _wrap(lambda ctx, days_ahead=180: macro.calendar(ctx.store, days_ahead), macro.MacroUnavailable)))

    return reg


TOOL_NAMES = ["get_company_profile", "get_earnings", "get_dividends", "get_analyst_estimates",
              "get_company_news", "list_filings", "list_filing_sections", "read_filing_section",
              "get_macro_calendar"]
