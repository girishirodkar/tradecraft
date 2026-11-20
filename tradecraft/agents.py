"""Stage 2's five agents. Each is one `AgentConfig` on the shared harness.

- Evidence Retriever: a ReAct loop over the data tools. It fetches; code stores
  what it fetches and sets the grades. It draws no conclusion.
- Fundamental Analyst, Regime Assessor, Technical Analyst: one output class
  (`AnalystFindings`) and one builder, three configurations.
- Thesis agent: a Tree of Thought in one pass. Three branches (bullish, bearish,
  no view), each tested against the precedence rules, pruned with a reason, the
  remainder selected. No tools. It never receives an option price, an implied
  volatility or a market-implied probability, and it states no probability.

Contracts: docs/agent-architecture.md, section 3. Guardrails by agent:
docs/build-plan.md, section 5.
"""
from __future__ import annotations

import re
from typing import Callable, Literal

from pydantic import BaseModel, Field

from .harness import AgentConfig, no_probability, no_trading_advice

Bearing = Literal["supports_bullish", "supports_bearish", "none"]
COMPANY_FLAGS = ["going_concern_or_liquidity_warning", "announced_merger_or_takeover_target",
                 "pending_binary_event", "dilution", "guidance_reduction", "material_litigation_or_regulatory_action"]
SECTOR_FLAGS = ["sector_wide_move"]
SEVERE_FLAGS = {"going_concern_or_liquidity_warning", "announced_merger_or_takeover_target"}
FALSIFIER_TYPES = ["guidance_change", "new_filing", "estimate_revision", "earnings_result",
                   "dated_event_outcome", "macro_release", "volatility_state", "unscheduled_announcement", "other"]
# What earns a finding its bearing (docs/decisions/2026-11-18-stage-2-anchored-bearings.md).
# The event list: the bearing of each kind is fixed here, never chosen by the analyst.
EVENT_BEARING = {
    "share_offering_or_shelf_registration": "supports_bearish",
    "guidance_lowered_outside_an_earnings_report": "supports_bearish",
    "new_material_litigation_or_regulatory_action": "supports_bearish",
    "material_impairment": "supports_bearish",
    "exit_or_disposal_costs": "supports_bearish",
    "non_reliance_on_earlier_statements": "supports_bearish",
    "ceo_or_cfo_departure_unplanned_or_no_permanent_successor": "supports_bearish",
    "guidance_raised_outside_an_earnings_report": "supports_bullish",
    # Events whose direction cannot be read from the event alone: reported, shown as context.
    "planned_succession_with_successor_named": "none",
    "material_agreement": "none",
    "acquisition_by_the_company": "none",
    "buyback": "none",
    "dividend_change": "none",
}
# Why a context finding has no direction. Code sets every reason it can know; the
# Fundamental Analyst chooses only between no_estimate and commentary. The model
# writes none of these sentences (decision of 18 November 2026, section 5).
CONTEXT_SENTENCE = {
    "in_line": "In line with estimates",
    "mixed": "Mixed: one measure above, one below",
    "no_quarterly_consensus": "No quarterly consensus available",
    "event_no_direction": "Direction cannot be read from the event alone",
    "not_recent": "Too old to count as new",
    "price_description": "Price behaviour is description only",
    "no_macro_expectation": "No expected figure to compare with",
    "no_estimate": "No estimate to compare with",
    "commentary": "Commentary, not a comparison",
    "other": "No stated comparison",
    # Guidance, set in code (operator decision, 19 November 2026).
    "measure_no_direction": "Direction cannot be read from this measure",
    "worded_guidance": "Stated in words, not figures",
    "reaffirmed": "Reaffirmed: unchanged from earlier guidance",
    "guidance_mixed": "Mixed: the range narrowed or moved both ways",
    "not_comparable": "Measure, period or basis does not match",
}
RECENT_DAYS = 30
BEARING_KINDS = ("results_vs_estimates", "guidance_change", "new_event")
BANNED_CHART_TERMS = re.compile(r"\b(candlestick|doji|hammer pattern|fibonacci|elliott wave|head and shoulders)\b", re.I)


def _named(name: str, fn: Callable) -> Callable:
    fn.__name__ = name
    return fn


# ---- Evidence Retriever ----------------------------------------------------------------

class Fetched(BaseModel):
    what: str = Field(description="What was fetched, in a few words. No conclusion.")
    evidence_ids: list[str] = Field(description="The evidence ids the tool results carried, e.g. E3.")


class Unavailable(BaseModel):
    input: str
    reason: str


class RetrieverIndex(BaseModel):
    fetched: list[Fetched]
    unavailable: list[Unavailable] = []


RETRIEVER = """You are the Evidence Retriever of a research system. You collect the evidence that later
analysts will read about one underlying. You fetch; you do not interpret. Draw no conclusion, state no view
and no probability, and do not say whether anything is good or bad for the stock.

Work in a loop: say in one short line what you will fetch and why, call the tools, read what came back, then
decide what to fetch next. Ask for several tools in one step when they do not depend on each other.

For a company, collect:
1. the company profile;
2. the earnings calendar and past reports;
3. the list of recent filings; then the most recent earnings release (an 8-K with item 2.02: list its
   documents and read the release exhibit, not the cover page) and, if tool calls remain, the management
   discussion section of the most recent 10-Q or 10-K;
4. the current analyst consensus;
5. recent company news;
6. the macro calendar for the next 90 days;
7. dividend dates.
For a fund or an index there are no company filings: collect the profile, the macro calendar and news.

If a source refuses, returns nothing or fails, do not stop: try the sensible fallback once (for example another
filing or another document of the same filing), and if that also fails record the input under "unavailable"
with the reason and carry on. Results that hold evidence carry evidence ids (evidence_id); in your answer list
what you fetched with those ids, exactly as given, including every filing section you read. Do not invent an id.
The list of filings and the list of a filing's sections are indexes, not evidence: they carry no id, so leave
them out of your answer and do not report them as unavailable. Keep the answer short: a few words per entry."""


def retriever(known_ids: Callable[[], set[str]]) -> AgentConfig:
    def ids_exist(answer: RetrieverIndex) -> list[str]:
        known = known_ids()
        bad = sorted({e for f in answer.fetched for e in f.evidence_ids if e not in known})
        return [f"These evidence ids are not in the evidence store: {', '.join(bad)}. "
                "List only ids that a tool result carried."] if bad else []
    return AgentConfig(
        name="evidence_retriever", role="evidence_retriever.company", instructions=RETRIEVER,
        output_model=RetrieverIndex, effort="low",
        tools=["get_company_profile", "get_earnings", "get_dividends", "get_analyst_estimates", "get_company_news",
               "list_filings", "list_filing_sections", "read_filing_section", "get_macro_calendar"],
        output_guards=[_named("evidence_ids_exist", ids_exist), no_probability])


# ---- the three analysts: one class, three configurations --------------------------------

class GuidedFigures(BaseModel):
    """One side of a guidance comparison, extracted from the evidence. Nothing here is a judgement."""
    measure: str = Field(description="What is guided, as the evidence names it, e.g. 'EPS', 'revenue', 'operating margin'.")
    period: str = Field(description="The period it covers, as the company names it, e.g. 'fiscal 2026'.")
    basis: str = Field(default="not stated", description="The basis, e.g. 'adjusted' or 'reported'; 'not stated' if the evidence does not say.")
    low: str | None = Field(default=None, description="The low end, or the single figure, quoted with its unit, e.g. '$4.10' or '+2.5%'.")
    high: str | None = Field(default=None, description="The high end of a range, quoted with its unit. Leave empty for a single figure.")


class Guidance(BaseModel):
    now: GuidedFigures = Field(description="The new guidance.")
    before: GuidedFigures | None = Field(default=None, description=(
        "What it is compared with: the consensus figure, or the company's earlier guidance. Empty if there is neither."))
    compared_with: Literal["earlier_guidance", "consensus"] | None = None
    passage: str | None = Field(default=None, description=(
        "If the guidance is stated in words with no figures to extract, the passage, quoted from the evidence."))


class Finding(BaseModel):
    finding: str = Field(description="One factual finding, in one or two sentences.")
    evidence_ids: list[str] = Field(min_length=1, description="The stored evidence it rests on, e.g. ['E3'].")
    kind: Literal["guidance_change", "new_event", "context"] = "context"
    bearing: Bearing = "none"
    guidance: Guidance | None = Field(default=None, description="Required for a guidance_change.")
    event_kind: str | None = Field(default=None, description="Required for a new_event: a kind from the event list.")
    context_reason: Literal["no_estimate", "commentary"] | None = Field(default=None, description=(
        "For a context finding: no_estimate if it is a figure with no estimate to compare it with, "
        "commentary if it is management or press commentary."))
    standing_disclosure: bool = Field(default=False, description=(
        "True if this is a standing disclosure and not something new: a long-standing risk factor, ongoing "
        "litigation, or anything repeated from earlier filings."))


class RiskFlag(BaseModel):
    flag: str
    evidence_ids: list[str] = Field(min_length=1)
    event_date: str | None = Field(default=None, description="YYYY-MM-DD if the flag concerns a dated event.")
    note: str = ""


class Level(BaseModel):
    label: str
    level: float


class AnalystFindings(BaseModel):
    findings: list[Finding] = []
    risk_flags: list[RiskFlag] = []
    # Regime Assessor only
    regime: Literal["ok", "hostile", "unknown"] | None = None
    # Technical Analyst only
    price_description: str | None = None
    timeframes: dict[str, str] | None = None
    levels: list[Level] = []


COMMON = """Rules for every finding:
- It is a fact found in the evidence, not an opinion. Cite the evidence ids it rests on (evidence_ids),
  exactly as given. Do not invent an id and do not use anything you remember that is not in the evidence.
- You do not form the overall view; a later step does, by fixed rules.
- State no probability, no price target, no score and no advice."""

FUNDAMENTAL = """You are the Fundamental Analyst of a research system. You read the stored evidence about one
company (filings, the earnings release, the analyst consensus, company news, past earnings reactions) and
extract findings.

Work in a loop. Read the evidence you are given. Where a finding needs more than you have (for example the
guidance paragraph of the earnings release, or an 8-K reporting an event), fetch that one filing section with
the tools, then stop when you have what you need. Do not read a filing whole.

Report at most eight findings, the most material first, whichever way they read. Every finding has a kind.
A finding carries a direction ONLY when the evidence states the comparison that gives it one:

1. kind "guidance_change": one finding per guided measure. You extract the figures; you do not say whether
   the guidance is good or bad, raised or lowered, above or below. Code compares the figures and sets the
   direction. Leave bearing as "none". Fill in "guidance":
   - now: the new guidance: measure, period, basis (for example adjusted or reported), and the low and high
     figures quoted from the evidence with their units. For a single figure give low only.
   - before: what it is compared with, extracted the same way. If the evidence gives an analyst consensus figure
     for the same measure and the same period, use that consensus (compared_with "consensus", the figure in low)
     and nothing else. Only if there is no such consensus figure, use THE COMPANY'S OWN EARLIER GUIDANCE FOR THE
     SAME PERIOD (compared_with "earlier_guidance"). If there is neither, leave before empty. Only annual
     consensus is available, so a quarterly outlook can be compared only with earlier guidance for that quarter.
   - Name the period the same way on both sides when they cover the same fiscal period.
   - If the guidance is stated in words with no figures to extract (for example "high-teens growth"), leave the
     figures empty and quote the passage in "passage".
   Never report the same guided measure twice, and never put two measures in one finding.
2. kind "new_event": a discrete event on this list that is recent: dated within the last 30 days, or since the
   latest earnings report. Cite the dated evidence for it (the 8-K or the item reporting it). Give event_kind.
   Its direction is fixed by the list, so leave bearing as "none"; code sets it.
   - share_offering_or_shelf_registration
   - guidance_lowered_outside_an_earnings_report
   - new_material_litigation_or_regulatory_action (a new 8-K or a newly added risk factor; a law firm's notice
     soliciting plaintiffs does not count)
   - material_impairment, exit_or_disposal_costs, non_reliance_on_earlier_statements (8-K items 2.06, 2.05, 4.02)
   - ceo_or_cfo_departure_unplanned_or_no_permanent_successor (the chief executive or chief financial officer
     leaves and the departure is unplanned or no permanent successor is named; a planned succession with the
     successor named is context)
   - guidance_raised_outside_an_earnings_report
   These events are also reported as new_event, and have no direction (it cannot be read from the event alone):
   - planned_succession_with_successor_named, material_agreement, acquisition_by_the_company, buyback,
     dividend_change
3. kind "context": everything else, with bearing "none". Segment detail, margins, cash flow, capital
   expenditure, inventory, year-over-year changes with no estimate beside them, management commentary, and
   news that reports opinion or price action are all context. Context is valuable and is shown to the user; it
   does not point up or down. For each context finding set context_reason: "no_estimate" for a figure that has
   no estimate to compare it with, "commentary" for management or press commentary.

Do NOT report the latest results against estimates (EPS and revenue against consensus): code builds that
finding from the two numbers. You may report detail of the results as context.
Do not report who is buying or selling the stock, institutional holdings, option activity or chart signals:
they are not findings.

Standing disclosures: a long-standing risk factor, ongoing litigation, or anything else a filing repeats from
earlier filings is not news. If you report one, set standing_disclosure to true; it is context.
""" + COMMON + """

Risk flags: raise a flag only if it is on this list and the evidence shows it, citing that evidence.
- going_concern_or_liquidity_warning: stated in the latest annual or quarterly report.
- announced_merger_or_takeover_target: the company is the target of an announced transaction.
- pending_binary_event: a dated court ruling, regulatory decision or shareholder vote (give event_date).
- dilution: a share offering or shelf registration filed in the last 90 days.
- guidance_reduction: guidance lowered at the latest report.
- material_litigation_or_regulatory_action: a new 8-K or a newly added risk factor, not standing disclosure.
If something matters and no flag fits, report it as a finding. Do not invent a flag.

Leave regime, price_description, timeframes and levels empty."""

REGIME = """You are the Regime Assessor of a research system. You are given numbers computed in code: how the
stock, its sector fund and the market (SPY) have moved, SPY's trend, and the VIX level and term structure; and
the calendar of scheduled FOMC decisions and data releases. You may fetch the macro calendar if it is missing.

Report at most five findings about the sector and macro backdrop: what the sector fund and the market have
done and the level of market risk. Every finding is context: kind "context", bearing "none"; never use kind
"new_event" or "guidance_change". A sector fund's move is price action, so nothing here points up or down.
Do NOT report scheduled FOMC decisions or data releases as findings: code already puts them on the calendar and
raises the flags for them. Do not say what the backdrop means for the stock.
Set regime to ok, hostile or unknown from the market numbers; "unknown" is a valid answer.
""" + COMMON + """

Risk flag: raise sector_wide_move only if the stock's recent move matches its sector fund's with no
company-specific outperformance, citing the sector evidence. No other flag is yours to raise.

Leave price_description, timeframes and levels empty."""

TECHNICAL = """You are the Technical Analyst of a research system. You are given numbers computed in code from
daily closing prices: where the close stands against its 50-day, 30-week and 10-month averages, the percentage
change over 1, 3 and 12 months, the highest and lowest close of the last 52 weeks and 60 trading days, and the
3-month change against the sector fund and SPY.

Describe the price behaviour in plain words:
- price_description: two or three sentences.
- timeframes: one sentence each for "daily", "weekly" and "monthly", side by side. Do not count how many
  agree and do not combine them.
- levels: the levels you were given, each with a short label. Use only numbers you were given; never compute,
  estimate or round a level yourself.

Your output is description. It is not evidence for a direction, so do not say the stock is likely to rise or
fall, give no signal, no target and no probability, and do not mention candlesticks, Fibonacci or Elliott wave.
Leave findings, risk_flags and regime empty."""


def is_recent(date: str | None, latest_report: str | None) -> bool:
    """The grades' "recent" test, reused for a new event (operator decision, 19 November 2026)."""
    from . import evidence
    from .storage import now
    return evidence.checks({"date": date}, now().date(), latest_report)["recent"]


def rejected_signal(text: str) -> str | None:
    """The name of the rejected signal a text matches (config/rejected_signals.json), if any."""
    from . import settings
    for sig in settings.load_json("rejected_signals.json")["signals"]:
        for pat in sig["patterns"]:
            if re.search(pat, text, re.IGNORECASE):
                return sig["name"]
    return None


def analyst(name: str, known_ids: Callable[[], set[str]], given_numbers: Callable[[], set[float]] | None = None,
            evidence_facts: Callable[[], dict] | None = None) -> AgentConfig:
    """One of the three analysts. `known_ids` is the evidence store's ids for the
    request; `given_numbers` (Technical Analyst) the numbers it was handed."""
    allowed_flags = {"fundamental_analyst": COMPANY_FLAGS, "regime_assessor": SECTOR_FLAGS}.get(name, [])

    def cites_stored_evidence(a: AnalystFindings) -> list[str]:
        known = known_ids()
        bad = sorted({e for x in [*a.findings, *a.risk_flags] for e in x.evidence_ids if e not in known})
        return [f"These evidence ids are not in the evidence store: {', '.join(bad)}. "
                "Cite only ids you were given."] if bad else []

    def bearing_standard(a: AnalystFindings) -> list[str]:
        """Context carries no bearing; a guidance change must give figures or quote the passage
        (code sets its bearing); a new event must be on the list; a rejected signal cannot carry a direction.
        (An event that is not recent is not refused: code reports it as context, "too old
        to count as new".)"""
        errors = []
        facts = evidence_facts() if evidence_facts else {}
        latest = facts.get("latest_report")
        dates = facts.get("dates", {})
        for f in a.findings:
            label = f"'{f.finding[:60]}...'"
            # Only a finding offered as carrying a direction is tested against the rejected signals.
            # Description (context, the Regime Assessor's and the Technical Analyst's output, a
            # trend against a moving average) is exempt: the design allows description.
            # A defined event is never refused as a rejected signal (operator ruling, 19 November 2026):
            # its kind is checked against the event list instead. That leaves a guidance change.
            hit = rejected_signal(f.finding) if f.kind == "guidance_change" else None
            if hit:
                errors.append(f"{label} rests on a rejected signal ({hit}). It cannot carry a direction: "
                              "report it as context or remove it.")
            if f.kind == "context" and f.bearing != "none":
                errors.append(f"{label} is context, so its bearing must be 'none'. A direction needs a stated "
                              "comparison: a guidance change with both figures, or an event on the list.")
            if f.kind == "guidance_change" and not (f.guidance and (
                    (f.guidance.now.low or "").strip() or (f.guidance.passage or "").strip())):
                errors.append(f"{label} is a guidance change but gives no figures (guidance.now.low) and quotes "
                              "no passage (guidance.passage). Extract the figures, quote the passage, or report "
                              "it as context.")
            if f.kind == "new_event":
                if f.event_kind not in EVENT_BEARING:
                    errors.append(f"{label} names an event kind that is not on the list ({f.event_kind}). "
                                  "Use a kind from the list, or report it as context.")
        # One guidance figure yields one finding.
        seen: dict[tuple, int] = {}
        for f in a.findings:
            if f.kind == "guidance_change" and f.guidance:
                key = (f.guidance.now.measure.strip().lower(), f.guidance.now.period.strip().lower())
                seen[key] = seen.get(key, 0) + 1
        for (measure, period), n in seen.items():
            if n > 1:
                errors.append(f"The guidance for {measure}, {period} appears in {n} findings. One guidance figure "
                              "yields one finding: compare it with consensus if a consensus figure exists for "
                              "that period, otherwise with the company's earlier guidance.")
        return errors

    def flags_on_the_list(a: AnalystFindings) -> list[str]:
        bad = sorted({f.flag for f in a.risk_flags if f.flag not in allowed_flags})
        return [f"These risk flags are not on your list: {', '.join(bad)}. "
                f"Allowed: {', '.join(allowed_flags) or 'none'}."] if bad else []

    def description_only(a: AnalystFindings) -> list[str]:
        errors = []
        if a.findings or a.risk_flags:
            errors.append("The Technical Analyst reports no findings and no risk flags: its output is description.")
        if not a.price_description or set(a.timeframes or {}) != {"daily", "weekly", "monthly"}:
            errors.append("Give price_description and one sentence each for daily, weekly and monthly.")
        given = given_numbers() if given_numbers else set()
        made_up = [x.level for x in a.levels if not any(abs(x.level - g) < 0.005 for g in given)]
        if made_up:
            errors.append(f"These levels were not among the numbers you were given: {made_up}. "
                          "Use only the given levels; never compute one.")
        text = " ".join([a.price_description or "", *(a.timeframes or {}).values()])
        m = BANNED_CHART_TERMS.search(text)
        if m:
            errors.append(f"The description may not mention '{m.group(0)}'.")
        return errors

    spec = {
        "fundamental_analyst": dict(instructions=FUNDAMENTAL,
                                    tools=["list_filings", "list_filing_sections", "read_filing_section"],
                                    guards=[cites_stored_evidence, flags_on_the_list, bearing_standard]),
        # The bearing standard (event kinds, guidance figures) is the Fundamental Analyst's alone. Every
        # Regime Assessor finding is context, set in code (operator ruling, 19 November 2026).
        "regime_assessor": dict(instructions=REGIME, tools=["get_macro_calendar"],
                                guards=[cites_stored_evidence, flags_on_the_list]),
        "technical_analyst": dict(instructions=TECHNICAL, tools=[], guards=[description_only]),
    }[name]
    return AgentConfig(name=name, role=f"{name}.thesis_drafting", instructions=spec["instructions"],
                       output_model=AnalystFindings, tools=spec["tools"], effort="low",
                       output_guards=[_named(g.__name__, g) for g in spec["guards"]]
                       + [no_probability, no_trading_advice])


# ---- Thesis agent ----------------------------------------------------------------------

class Cited(BaseModel):
    text: str
    cites: list[str] = Field(description="Ids of the findings (F1, R2) or measured facts (M3) this rests on.")


class Branch(BaseModel):
    view: Literal["bullish", "bearish", "no_view"]
    supporting: list[str] = Field(description="Finding ids for this branch.")
    opposing: list[str] = Field(description="Finding ids against this branch.")
    meets_precedence: bool
    pruned_reason: str | None = Field(default=None, description="Why the branch was pruned; null for the selected one.")


class Rationale(BaseModel):
    catalyst: Cited
    confirmation: Cited
    tempering: Cited


class Falsifier(BaseModel):
    finding_id: str
    type: Literal["guidance_change", "new_filing", "estimate_revision", "earnings_result", "dated_event_outcome",
                  "macro_release", "volatility_state", "unscheduled_announcement", "other"]
    trigger: str = Field(description="The observable evidence that would reverse the finding. Never a price level.")
    reverses: str = Field(description="What it reverses, e.g. 'Reverses the catalyst'.")
    action: str = Field(description="What the reader should then do, phrased affirmatively.")


class Catalyst(BaseModel):
    dated: bool
    date: str | None = None
    finding_id: str | None = None
    note: str = ""


class ThesisDraft(BaseModel):
    branches: list[Branch] = Field(min_length=3, max_length=3)
    view: Literal["bullish", "bearish", "no_view"]
    no_view_kind: Literal["nothing_found", "declined", "insufficient_data"] | None = None
    no_view_reason: str | None = None
    basis: str = ""
    summary: Cited | None = None
    rationale: Rationale | None = None
    horizon_reasons: list[Cited] = []
    resolution_criterion: str = ""
    falsifiers: list[Falsifier] = []
    supporting: list[str] = []
    opposing: list[str] = []
    catalyst: Catalyst | None = None


THESIS = """You are the Thesis agent of a research system. You are given the findings about one underlying,
each with an id, its kind, its bearing and a grade set by code (strong, moderate, weak); and measured facts
computed in code, each with an id (M1, M2, ...). You draft a researched view, or decline to. You have no tools.

A finding carries a direction only if its bearing is supports_bullish or supports_bearish. Only three kinds
can: results against estimates (set by code from the two numbers), a guidance change, and a new event on a
fixed list. Every other finding is context, with bearing "none": it may be quoted, and it cannot start,
support or cancel a view. Sector and macro findings are always context.

Reason as a tree with exactly three branches: bullish, bearish and no_view. For each branch list the finding
ids for it and against it, test it against the precedence rules, and either keep it or prune it with the reason.
Then select the one branch that remains. Do this once; do not argue the branches against each other.

Precedence rules:
1. A directional branch needs at least one finding that carries its direction, graded moderate or strong.
   One is enough, including the earnings result alone.
2. Conflict: if findings graded moderate or strong carry both directions, prune both directional branches and
   select no_view. You do not choose between them.
3. A weak finding carrying the other direction does not prune the branch: list it under "opposing".
4. Context never supports, opposes or cancels a branch. Do not list context under supporting or opposing.
5. A severe risk flag (going concern, announced takeover target) means no_view, kind "declined".
6. Price description, trend, momentum, relative strength and chart levels never support a direction.
no_view is a proper result, not a failure. Kinds: nothing_found (the findings conflict, or nothing carries a
direction), declined (a severe flag), insufficient_data (too little evidence was available). For no_view, say
in no_view_reason which it is, naming the findings on each side.

If you select bullish or bearish, also write:
- summary: one sentence giving the view and its main reason.
- rationale.catalyst and rationale.confirmation: the findings that carry the direction and the comparison each
  rests on. If the view rests on the earnings result alone, write the result in "catalyst" (it is the basis)
  and say in "confirmation" what is missing: no change in guidance and no defined event.
- rationale.tempering: the thesis's own weak points: evidence resting on one report, how long ago the report
  was and any move in the price since (use the measured facts), and context that reads the other way.
- horizon_reasons: three or four sentences on the recommended horizon you are given: why it fits the evidence,
  why the shorter and the longer row fit less well, and which known events fall inside it. The horizon is set
  by rule; you explain it, you do not choose it. If an earnings report falls inside it, say so and cite its fact.
- resolution_criterion: bullish = the close at the horizon is above the reference close; bearish = below it.
- falsifiers: for every finding under "supporting", the evidence that would reverse it. Each has a type from the
  list. NEVER a price level, a moving average or a chart level: a price move does not falsify the view.
- supporting: the ids of the findings that carry the view's direction. opposing: weak findings that carry the
  other direction, or empty.
- catalyst: whether the view depends on a dated event still to come, and its date.
- basis: two or three sentences for the record.
If you select no_view, give no_view_kind and no_view_reason and leave those fields empty.

Rules on the text:
- Every text with "cites" must cite the ids of the findings or measured facts it rests on. Use nothing else:
  not your memory, not general knowledge about the company. Put the ids in "cites" only: never write an id
  such as F2 or M7 inside the text itself, which is shown to the user.
- Every number you write must appear in a finding or measured fact you cite, written the same way. Do not
  calculate, convert or round a number. If you need a number you were not given, leave it out.
- State no probability, chance, odds or confidence, no price target, no score and no trading advice."""


def thesis(content_check: Callable[[ThesisDraft], list[str]]) -> AgentConfig:
    """The Thesis agent. `content_check` is the validation check against the
    record (tradecraft/validation.py). It runs here, on the harness, and nowhere
    else, so a draft is returned at most once in total."""
    return AgentConfig(name="thesis", role="thesis.draft", instructions=THESIS, output_model=ThesisDraft,
                       tools=[], effort="medium",
                       output_guards=[no_probability, no_trading_advice, _named("validation_check", content_check)])
