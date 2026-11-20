"""Stage 4: the challenge.

Two checklists in code (twelve checks on the thesis, eleven on the contract),
the thesis restated as a question by a fixed template, retrieval from the
project's research only, the Critic's nine tasks with its output checked in
code, and a readiness line set by code. It advises and never blocks.

Design: docs/on-demand-mode-design.md, "Stage 4 redesigned";
docs/decisions/2026-11-17-stage-4-challenge.md (with the operator's decisions
for the build, 19 November 2026); docs/product-shell.md 6.4 and 6.5.

Rules this module keeps:
- Every check returns passed, flagged, not_applicable or not_checked. A check
  never reports "passed" for want of data.
- Nothing here changes the thesis, the contract or a figure. Flags are not
  counted into a rating.
- The Critic is not shown the original wording, the written basis or who wrote
  the thesis; thesis check 9 (origin and edits) is withheld from it.
- The Critic's output check runs on the harness, as its output check, and
  nowhere else: one return in total.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import time
from typing import Literal

from pydantic import BaseModel, Field

from . import figures, research, settings, stage2, stage3, testfail, validation
from .agents import SEVERE_FLAGS, _named
from .data import chain as chain_data
from .data import prices, session
from .harness import AgentConfig, Tool, ToolRegistry, no_probability, wrap_untrusted
from .storage import now
from .workflow.state import StepFailed

PASSED, FLAGGED, NA, NC = "passed", "flagged", "not_applicable", "not_checked"
SOLID = validation.SOLID
ORDER = {"strong": 3, "moderate": 2, "weak": 1}
GRADE_TESTS = {"primary_source": "primary source", "recent": "recent", "specific": "specific"}
FLAG_LABEL = {
    "going_concern_or_liquidity_warning": "going-concern or liquidity warning",
    "announced_merger_or_takeover_target": "announced takeover of the company",
    "pending_binary_event": "pending dated ruling, decision or vote", "dilution": "share offering or shelf registration",
    "guidance_reduction": "guidance lowered at the latest report",
    "material_litigation_or_regulatory_action": "new material litigation or regulatory action",
    "sector_wide_move": "sector-wide move", "fed_decision_inside_a_short_horizon": "FOMC decision inside a short horizon",
}

# Thesis check 8: where each kind of invalidation condition could be watched today.
WATCH = {
    "guidance_change": ("could", "the company's filings"),
    "new_filing": ("could", "the company's filings"),
    "estimate_revision": ("cannot", None),
    "earnings_result": ("could", "the earnings release, once it is filed"),
    "dated_event_outcome": ("partly", "the company's filings (news is not watched)"),
    "macro_release": ("could", "the macro calendar"),
    "volatility_state": ("could", "price history"),
    "unscheduled_announcement": ("partly", "the company's filings (news is not watched)"),
    "other": ("cannot", None),
}
CONFIDENCE_WORDS = re.compile(
    r"\b(clearly|obviously|certainly|certain|undoubtedly|definitely|surely|easily|without (a )?doubt|"
    r"no doubt|guaranteed|unquestionably|plainly|evidently)\b,?\s*", re.IGNORECASE)
CHECK_NAMES = {
    "T1": "Rejected signal", "T2": "Concentrated evidence", "T3": "Strength of evidence",
    "T4": "Contested evidence", "T5": "Against the base rate", "T6": "Event risk inside the holding period",
    "T7": "Risk flags", "T8": "Invalidation not monitored", "T9": "Origin and edits",
    "T10": "Earlier overrides and gaps", "T11": "Price moved since the freeze", "T12": "Volatility regime",
    "C1": "Can lose with the thesis correct", "C2": "Volatility regime vs. strategy", "C3": "Expiration mismatch",
    "C4": "POP gap, historical vs. implied", "C5": "Implied move above typical move", "C6": "Slippage high",
    "C7": "Short-premium strategy", "C8": "Early assignment", "C9": "Order size",
    "C10": "Top-ranked candidate passed over", "C11": "Price moved since selection",
}


def config() -> dict:
    return settings.load_json("stage4.json")


def _usd(x: float) -> str:
    return f"${x:,.2f}"


def _day(d: str | dt.date) -> str:
    d = dt.date.fromisoformat(d[:10]) if isinstance(d, str) else d
    return f"{d.day} {d:%B}"


def _n(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def check(cid: str, result: str, detail: str, *, note: bool = False, lines: list[dict] | None = None, **data) -> dict:
    return {"id": cid, "name": CHECK_NAMES[cid], "result": result, "note": note, "detail": detail,
            "lines": lines or [], "data": data}


def line(name: str, result: str, detail: str, **data) -> dict:
    return {"name": name, "result": result, "detail": detail, **data}


def _overall(lines: list[dict]) -> str:
    """A check made of lines: flagged if any line is; could not be checked if none
    is flagged and any could not be checked; not applicable if none applies."""
    rs = {l["result"] for l in lines}
    return FLAGGED if FLAGGED in rs else NC if NC in rs else PASSED if PASSED in rs else NA


# ---- what stage 4 reads of the earlier stages ----------------------------------------------

class Case:
    """The request as stage 4 reads it. Nothing here is written back."""

    def __init__(self, state: dict, today: dt.date | None = None):
        self.state = state
        self.symbol = state["symbol"].upper()
        self.today = today or now().date()
        self.thesis = state.get("thesis") or {}
        self.mine = state.get("user_thesis")
        self.origin = "user" if self.mine else "system"
        self.view = state.get("view")
        self.fig = state.get("figures") or {}
        self.measured = self.fig.get("measured") or {}
        self.findings: dict = self.thesis.get("findings") or {}
        self.selection = state.get("selection") or {}
        self.cand = self.selection.get("candidate") or {}
        self.contracts = state.get("contracts") or {}
        frozen = stage3.frozen_thesis(state)["horizon_days"]
        amended = self.selection.get("horizon_amendment") or {}
        self.frozen_days = frozen
        self.days = amended.get("to_days") or frozen          # the horizon in force
        self.amended = bool(amended)
        self.row = next((r for r in self.measured.get("horizons") or [] if r["days"] == self.days), None)
        self.fund = self.symbol in stage2.FUNDS
        self.index = self.symbol in stage2.EQUITY_INDICES

    @property
    def directional(self) -> bool:
        return self.view in ("bullish", "bearish")

    def supporting(self) -> list[dict]:
        """The findings the thesis rests on that carry its direction."""
        if not self.directional:
            return []
        want = validation.SUPPORTS[self.view]
        if self.mine:
            ids = [r["evidence_id"] for r in self.mine.get("relied_on") or []]
        else:
            ids = self.thesis.get("supporting") or []
        return [self.findings[i] for i in ids if i in self.findings and self.findings[i].get("bearing") == want]

    def relied_on(self) -> list[dict]:
        """What the thesis cites: the supporting findings, and for a thesis the user
        entered every finding relied on, context included."""
        if self.mine:
            return [self.findings[r["evidence_id"]] for r in self.mine.get("relied_on") or []
                    if r["evidence_id"] in self.findings]
        return self.supporting()

    def opposing(self) -> list[dict]:
        """Any finding that carries the opposite direction (operator decision, 19 November 2026)."""
        if not self.directional:
            return []
        want = validation.OPPOSITE[self.view]
        return [f for f in self.findings.values() if f.get("bearing") == want]

    def falsifiers(self) -> list[dict]:
        return (self.mine or self.thesis).get("falsifiers") or []

    def events(self, kind: str) -> list[dict]:
        return [e for e in self.fig.get("events") or [] if e.get("kind") == kind]


def _grade(f: dict) -> str:
    return f.get("grade") or "weak"


# ---- step 1: the thesis checklist -----------------------------------------------------------

def t1_rejected_signal(c: Case) -> dict:
    texts = []
    if not c.mine and c.thesis.get("basis"):
        texts.append(("the written basis", c.thesis["basis"]))
    texts += [(f"finding {f['id']}", f.get("text") or f.get("finding") or "") for f in c.relied_on()]
    hits = []
    for sig in settings.load_json("rejected_signals.json")["signals"]:
        for pat in sig["patterns"]:
            for where, text in texts:
                m = re.search(pat, text, re.IGNORECASE)
                if m and not any(h["signal"] == sig["name"] and h["where"] == where for h in hits):
                    hits.append({"signal": sig["name"], "signal_id": sig["id"], "phrase": m.group(0), "where": where,
                                 "reason": sig["reason"]})
    if not texts:
        return check("T1", NC, "The thesis cites no finding to test.")
    if hits:
        h = hits[0]
        more = f" And {_n(len(hits) - 1, 'more match')}." if len(hits) > 1 else ""
        return check("T1", FLAGGED, f"“{h['phrase']}” in {h['where']} matches {h['signal']}.{more}", matches=hits)
    return check("T1", PASSED, f"No rejected signal in {_n(len(texts), 'text')} tested.", matches=[])


def _counted(c: Case) -> tuple[list[dict], dict[str, int]]:
    """Supporting findings graded moderate or strong; the same family on the same day counts once."""
    seen, out, fam = set(), [], {}
    for f in c.supporting():
        if _grade(f) not in SOLID:
            continue
        key = (f.get("family"), f.get("date"))
        if config()["thesis_checks"]["same_day_same_family_counts_once"] and f.get("date") and key in seen:
            continue
        seen.add(key)
        out.append(f)
        fam[f.get("family") or "no family"] = fam.get(f.get("family") or "no family", 0) + 1
    return out, fam


def t2_concentrated(c: Case) -> dict:
    if not c.directional:
        return check("T2", NA, "No directional view.")
    counted, fam = _counted(c)
    data = {"counted": [f["id"] for f in counted], "by_family": fam,
            "supporting": [f["id"] for f in c.supporting()]}
    if not c.supporting():
        return check("T2", FLAGGED, "No finding carries this direction.", kind="none", **data)
    if not counted:
        return check("T2", FLAGGED, "No supporting finding is graded moderate or strong.", kind="none_solid", **data)
    if len(counted) == 1:
        return check("T2", FLAGGED, f"One finding, {counted[0]['id']}. The thesis rests on it alone.", kind="single_finding", **data)
    if len(fam) == 1:
        return check("T2", FLAGGED, f"{_n(len(counted), 'finding').capitalize()}, one evidence family.", kind="single_family", **data)
    return check("T2", PASSED, f"{_n(len(counted), 'finding').capitalize()} from {len(fam)} evidence families.", **data)


def t3_strength(c: Case) -> dict:
    if not c.directional:
        return check("T3", NA, "No directional view.")
    sup = c.supporting()
    if not sup:
        return check("T3", FLAGGED, "No finding carries this direction.", kind=["none"], best=None)
    best = max(sup, key=lambda f: ORDER[_grade(f)])
    weak = [f for f in sup if _grade(f) == "weak"]
    kinds, failed = [], {}
    if _grade(best) != "strong":
        kinds.append("moderate_at_best")
    if weak:
        kinds.append("weak_cited")
    for f in sup:
        if _grade(f) != "strong":
            tests = [GRADE_TESTS[k] for k, ok in (f.get("checks") or {}).items() if k in GRADE_TESTS and not ok]
            failed[f["id"]] = {"grade": "ungraded, treated as weak" if f.get("ungraded") else _grade(f),
                               "tests_failed": tests}
    if not kinds:
        return check("T3", PASSED, "At least one supporting finding is graded strong; none is weak.", best="strong")
    parts = []
    if "moderate_at_best" in kinds:
        b = failed.get(best["id"], {})
        why = f" Grade test not met: {', '.join(b.get('tests_failed') or [])}." if b.get("tests_failed") else ""
        parts.append(f"The best supporting finding is graded {_grade(best)}.{why}")
    if weak:
        parts.append(f"A weak finding is cited as support ({', '.join(f['id'] for f in weak)}).")
    return check("T3", FLAGGED, " ".join(parts), kind=kinds, best=_grade(best), findings=failed)


def t4_contested(c: Case) -> dict:
    if not c.directional:
        return check("T4", NA, "No directional view.")
    opp = c.opposing()
    sup = c.supporting()
    data = {"opposing": [{"id": f["id"], "grade": _grade(f), "source": f.get("source"), "text": f.get("text")} for f in opp],
            "best_for": max((_grade(f) for f in sup), key=ORDER.get, default=None),
            "best_against": max((_grade(f) for f in opp), key=ORDER.get, default=None)}
    solid = [f for f in opp if _grade(f) in SOLID]
    if solid:
        return check("T4", FLAGGED, f"{_n(len(solid), 'finding').capitalize()} graded moderate or strong "
                                   f"{'carries' if len(solid) == 1 else 'carry'} the opposite direction "
                                   f"({', '.join(f['id'] for f in solid)}). Best for: {data['best_for'] or 'none'}; "
                                   f"best against: {data['best_against']}.", **data)
    if opp:
        return check("T4", PASSED, f"{_n(len(opp), 'finding').capitalize()} against, graded weak "
                                  f"({', '.join(f['id'] for f in opp)}).", note=True, **data)
    backdrop = any(f.get("analyst") == "regime_assessor" for f in c.findings.values())
    if not backdrop:
        return check("T4", NC, "No sector or macro evidence was retrieved.", **data)
    return check("T4", PASSED, "No finding carries the opposite direction.", **data)


def t5_base_rate(c: Case) -> dict:
    if not c.directional:
        return check("T5", NA, "Not a directional view.")
    up = (c.row or {}).get("base_rate_pct")
    if up is None:
        return check("T5", NC, f"No base rate for the {c.days}-day row.")
    rate = up if c.view == "bullish" else round(100 - up, 1)
    unc = c.row.get("base_rate_uncertainty_pts")
    how = "higher" if c.view == "bullish" else "lower"
    text = (f"{c.symbol} closed {how} in {rate:g}% of past {c.days}-day periods"
            + (f", plus or minus {unc:g} points" if unc is not None else "") + f" ({c.row['base_rate_basis']})."
            + (" The horizon was amended in stage 3." if c.amended else ""))
    data = {"rate_pct": rate, "uncertainty_pts": unc, "horizon_days": c.days, "basis": c.row["base_rate_basis"],
            "horizon_amended": c.amended}
    limit = config()["thesis_checks"]["base_rate_threshold_pct"]
    return check("T5", FLAGGED if rate < limit else PASSED, text, **data)


def _inside(c: Case, date: str) -> tuple[bool, int, str]:
    """(inside the window, day number from today, which side of the horizon)."""
    d = dt.date.fromisoformat(date[:10])
    n = (d - c.today).days
    exp = dt.date.fromisoformat(c.cand["expiry"])
    return c.today <= d <= exp, n, "inside the horizon" if n <= (c.days or 0) else "after the horizon"


def t6_events(c: Case) -> dict:
    if not c.cand.get("expiry"):
        return check("T6", NC, "No expiration to measure the window against.")
    exp = dt.date.fromisoformat(c.cand["expiry"])
    lines = []
    # Earnings: stage 3's own test (on or before the expiration), so the stages cannot disagree.
    if c.fund:
        lines.append(line("Earnings date", NA, "A fund has no earnings report."))
    else:
        e = next(iter(c.events("earnings")), None)
        if not e:
            lines.append(line("Earnings date", NC, "No date is served for the next earnings report."))
        else:
            inside, n, side = _inside(c, e["date"])
            lines.append(line("Earnings date", FLAGGED if inside else PASSED,
                              f"Earnings report on {_day(e['date'])}, day {n}, {side}." if inside else
                              f"Next earnings report {_day(e['date'])}, after the expiration.", date=e["date"], day=n))
    # A dated ruling, regulatory decision or vote, from the stage 2 risk flags.
    if c.fund:
        lines.append(line("Dated ruling or vote", NA, "Applies to single stocks."))
    else:
        dated = [f for f in c.thesis.get("risk_flags") or []
                 if f.get("flag") == "pending_binary_event" and f.get("event_date")]
        inside = [(f, *_inside(c, f["event_date"])) for f in dated]
        hit = [x for x in inside if x[1]]
        if hit:
            f, _, n, side = hit[0]
            lines.append(line("Dated ruling or vote", FLAGGED, f"A flagged event on {_day(f['event_date'])}, day {n}, {side}.",
                              date=f["event_date"], day=n))
        else:
            lines.append(line("Dated ruling or vote", PASSED, "No dated ruling, decision or vote was flagged inside the window."))
    # FOMC decision: every instrument.
    fomc = c.events("fomc")
    calendar_read = bool(fomc or c.events("data_release"))
    hit = [(e, *_inside(c, e["date"])) for e in fomc]
    hit = [x for x in hit if x[1]]
    if hit:
        e, _, n, side = hit[0]
        lines.append(line("FOMC decision", FLAGGED, f"FOMC decision, day {n} ({_day(e['date'])}), {side}.", date=e["date"], day=n))
    elif calendar_read:
        lines.append(line("FOMC decision", PASSED, "No FOMC decision before the expiration."))
    else:
        lines.append(line("FOMC decision", NC, "The macro calendar could not be read."))
    # Inflation and employment releases: index instruments. FRED lists dates only a few weeks ahead.
    if not c.fund:
        lines.append(line("Inflation and employment releases", NA, "Applies to index instruments."))
    else:
        rel = [e for e in c.events("data_release") if e.get("label") in ("Consumer Price Index", "Employment Situation")]
        hit = [(e, *_inside(c, e["date"])) for e in rel]
        hit = [x for x in hit if x[1]]
        last = max((e["date"] for e in c.events("data_release")), default=None)
        if hit:
            names = "; ".join(f"{e['label']}, day {n}" for e, _, n, _ in hit[:3])
            lines.append(line("Inflation and employment releases", FLAGGED, names + ".", dates=[e["date"] for e, *_ in hit]))
        elif last is None or dt.date.fromisoformat(last) < exp:
            lines.append(line("Inflation and employment releases", NC,
                              "Release dates are published only to " + (_day(last) if last else "an unknown date")
                              + "; the expiration is later."))
        else:
            lines.append(line("Inflation and employment releases", PASSED, "None before the expiration."))
    # Heavy earnings period: no source.
    lines.append(line("Heavy earnings period", NC, "No source for the holdings' report dates.") if c.index
                 else line("Heavy earnings period", NA, "Applies to equity indices."))
    # The thesis's own dated catalyst.
    cat = None if c.mine else c.thesis.get("catalyst")
    if cat and cat.get("dated") and cat.get("date"):
        inside, n, side = _inside(c, cat["date"])
        after = dt.date.fromisoformat(cat["date"][:10]) > exp
        lines.append(line("Dated catalyst", FLAGGED if after else PASSED,
                          f"The thesis depends on an event on {_day(cat['date'])}, after the expiration." if after
                          else f"The catalyst, {_day(cat['date'])}, falls before the expiration.", date=cat["date"]))
    else:
        lines.append(line("Dated catalyst", NA, "The thesis does not depend on a dated event still to come."))
    result = _overall(lines)
    flagged = [l for l in lines if l["result"] == FLAGGED]
    unchecked = [l for l in lines if l["result"] == NC]
    detail = (" ".join(l["detail"] for l in flagged) if flagged else
              " ".join(f"{l['name']}: {l['detail']}" for l in unchecked) if unchecked else
              f"No known event between today and the expiration, {_day(exp)}.")
    return check("T6", result, detail, lines=lines, window={"from": c.today.isoformat(), "to": exp.isoformat(),
                                                           "horizon_days": c.days})


def t7_risk_flags(c: Case) -> dict:
    flags = c.thesis.get("risk_flags") or []
    rows = [{"flag": f["flag"], "name": FLAG_LABEL.get(f["flag"], f["flag"].replace("_", " ")),
             "event_date": f.get("event_date"), "raised_by": f.get("raised_by"), "evidence_ids": f.get("evidence_ids"),
             "note": f.get("note") or "", "see_check_6": bool(f.get("event_date"))} for f in flags]
    severe = [f for f in rows if f["flag"] in SEVERE_FLAGS]
    names = ", ".join(r["name"] for r in rows)
    if severe and c.mine:
        return check("T7", FLAGGED, f"A severe risk flag was raised ({severe[0]['name']}) and the request went on.",
                     kind="severe", severe_overridden=True, flags=rows)
    real = [r for r in rows if r["flag"] != "sector_wide_move"]
    if real:
        timing = " The timing is in the event check." if any(r["see_check_6"] for r in real) else ""
        return check("T7", FLAGGED, f"{_n(len(real), 'risk flag').capitalize()} raised in the thesis stage: "
                                   f"{', '.join(r['name'] for r in real)}.{timing}", kind="flag", flags=rows)
    if rows:
        return check("T7", PASSED, f"A note only: {names}.", note=True, flags=rows)
    read = any((c.state.get("findings") or {}).get(a, {}).get("status") == "ok"
               for a in ("fundamental_analyst", "regime_assessor")) or bool(c.findings)
    if not read:
        return check("T7", NC, "The filings and the calendar could not be read.", flags=[])
    return check("T7", PASSED, "No risk flag was raised.", flags=[])


def t8_invalidation(c: Case) -> dict:
    conds = []
    for f in c.falsifiers():
        status, source = WATCH.get(f.get("type") or "other", WATCH["other"])
        conds.append({"trigger": f.get("trigger"), "type": f.get("type") or "other", "finding_id": f.get("finding_id"),
                      "source": source, "status": {"could": "could be monitored", "partly": "could be monitored in part",
                                                   "cannot": "cannot be monitored"}[status],
                      "where_to_look": source or "no data source"})
    kinds = []
    if any(x["status"] == "cannot be monitored" for x in conds):
        kinds.append("cannot_be_monitored")
    covered = {x["finding_id"] for x in conds}
    bare = [] if c.mine else [f["id"] for f in c.supporting() if f["id"] not in covered]
    if not conds or bare:
        kinds.append("no_condition")
    monitor = config()["thesis_checks"]["monitor_built"]
    if not monitor:
        kinds.append("not_monitored")
    if not kinds:
        return check("T8", PASSED, "Every condition has a data source and is monitored.", conditions=conds)
    if not conds:
        text = "The thesis states no invalidation condition."
    else:
        places = sorted({x["source"] for x in conds if x["source"]})
        cannot = sum(x["status"] == "cannot be monitored" for x in conds)
        text = (f"{_n(len(conds), 'condition').capitalize()}; nothing monitors "
                f"{'it' if len(conds) == 1 else 'them'} for you."
                + (f" {cannot} of them {'has' if cannot == 1 else 'have'} no data source." if cannot else "")
                + (f" Watch for yourself: {places[0]}." if places else "")
                + (f" No condition for {', '.join(bare)}." if bare else ""))
    return check("T8", FLAGGED, text, kind=kinds, conditions=conds, findings_without_a_condition=bare)


VERDICT_WORDS = {"not_supported": "not supported", "partly_supported": "partly supported",
                 "well_supported": "well supported"}


def t9_origin(c: Case) -> dict:
    """Shown to the user and kept in the record. Withheld from the Critic."""
    if not c.mine:
        return check("T9", PASSED, "Drafted by the system and accepted unchanged.", origin="system", edits=[])
    m = c.mine
    relied = m.get("relied_on") or []
    counts = {"carrying_the_direction": len(c.supporting()),
              "context": sum(r.get("kind") == "context" for r in relied),
              "standing_against": len(m.get("opposing") or [])}
    why = (m.get("entered_after_no_view") or {})
    reason = {"conflict": "the evidence that carries a direction pointed both ways",
              "nothing_carries_a_direction": "nothing carried a direction",
              "declined": "the system declined to form a view"}.get(
        why.get("reason_code") or "", "the system returned no view")
    verdict = m.get("verdict")
    kinds = ["entered_after_no_view"] + (["not_fully_supported"] if verdict != "well_supported" else [])
    text = (f"Your thesis, entered after no view ({reason}). It is {VERDICT_WORDS.get(verdict, verdict)}: "
            f"{counts['carrying_the_direction']} of the {_n(len(relied), 'item')} relied on "
            f"{'carries' if counts['carrying_the_direction'] == 1 else 'carry'} its direction"
            + (f", and {counts['standing_against']} {'stands' if counts['standing_against'] == 1 else 'stand'} "
               "against it." if counts["standing_against"] else "."))
    return check("T9", FLAGGED, text, origin="user", kind=kinds, verdict=verdict, counts=counts,
                 no_view_reason=why)


def t10_overrides(c: Case, records: list[dict]) -> dict:
    items = []
    g = c.state.get("gate_decision") or {}
    if g.get("action") == "override":
        items.append({"stage": 1, "what": "Liquidity gate overridden", "proposed": "FAIL at the criteria in force",
                      "chosen": "Override and continue", "reason": g.get("rationale")})
    if c.mine and c.mine.get("recommended_horizon_days") and \
            c.mine.get("primary_horizon_days") != c.mine.get("recommended_horizon_days"):
        items.append({"stage": 2, "what": "Recommended horizon not taken",
                      "proposed": f"{c.mine['recommended_horizon_days']} days",
                      "chosen": f"{c.mine['primary_horizon_days']} days", "reason": None})
    a = c.selection.get("horizon_amendment")
    if a:
        items.append({"stage": 3, "what": "Horizon amended by switching expiration",
                      "proposed": f"{a['from_days']} days", "chosen": f"{a['to_days']} days ({_day(a['expiration'])})",
                      "reason": None})
    raised = None
    for r in records:
        ch = ((r.get("payload") or {}).get("changed") or {}).get("max_loss") if r.get("decision") == "update" else None
        if ch and ch.get("from") is not None and ch.get("to") is not None and ch["to"] > ch["from"]:
            raised = ch
    if raised:
        items.append({"stage": 3, "what": "Max loss raised after the candidates were shown",
                      "proposed": _usd(raised["from"]), "chosen": _usd(raised["to"]), "reason": None})
    gate = c.state.get("gate") or {}
    prov = [name for name, on in (("the liquidity screen", gate.get("provisional")),
                                  ("the contracts", c.contracts.get("provisional"))) if on]
    if prov:
        items.append({"stage": 1 if gate.get("provisional") else 3, "what": "Provisional data",
                      "proposed": "live quotes", "chosen": f"the latest snapshot, for {' and '.join(prov)}",
                      "reason": "market closed, or live quotes unavailable"})
    missing = c.thesis.get("inputs_unavailable") or []
    as_flag = config()["thesis_checks"]["unavailable_inputs_are_a_flag"]
    if items or (missing and as_flag):
        text = "; ".join(i["what"] for i in items) + "." if items else f"{_n(len(missing), 'input')} unavailable."
        return check("T10", FLAGGED, text, items=items, inputs_unavailable=missing)
    if missing:
        return check("T10", PASSED, f"No override. {_n(len(missing), 'input').capitalize()} not available when the "
                                   f"view was formed: {'; '.join(missing)}.", note=True, items=[], inputs_unavailable=missing)
    return check("T10", PASSED, "No override, no provisional data, no missing input.", items=[], inputs_unavailable=[])


def _frozen_at(c: Case) -> dt.datetime | None:
    at = (c.state.get("thesis_decision") or {}).get("at")
    return dt.datetime.fromtimestamp(at, now().tzinfo) if at else None


def t11_price_moved(c: Case, fresh: dict) -> dict:
    cfg = config()["thesis_checks"]
    ref, move = c.measured.get("reference_close"), (c.row or {}).get("typical_move_pct")
    frozen = _frozen_at(c)
    age = stage3.trading_days(frozen.date(), c.today) if frozen else None
    stale = age is not None and age > cfg["stale_after_sessions"]
    data = {"reference_close": ref, "reference_date": c.measured.get("reference_date"),
            "current": fresh.get("spot"), "current_as_of": fresh.get("as_of"), "typical_move_pct": move,
            "horizon_days": c.days, "sessions_since_freeze": age, "stale": stale}
    if stale:
        return check("T11", FLAGGED, f"The thesis was frozen {_n(age, 'trading session')} ago.", kind="stale", **data)
    if not fresh.get("spot") or not ref or not move:
        return check("T11", NC, "No current price: " + (fresh.get("reason") or "the reference close or the typical "
                                                       "move is missing") + ".", **data)
    pct = round((fresh["spot"] / ref - 1) * 100, 2)
    ranges = round(abs(pct) / move, 2)
    data.update({"move_pct": pct, "typical_moves": ranges})
    if c.view == "range_bound":
        rel = "either way"
    else:
        with_view = (pct > 0) == (c.view == "bullish")
        rel = "with the thesis" if with_view else "against the thesis"
    data["direction"] = rel
    text = (f"Spot {_usd(fresh['spot'])} against a reference close of {_usd(ref)}: {pct:+.1f}%, "
            f"{ranges:g} of a typical realized move for {c.days} days")
    if ranges >= cfg["price_move_usual_ranges"]:
        return check("T11", FLAGGED, text + (f", {rel}." if rel != "either way" else "."),
                     kind="moved_with" if rel == "with the thesis" else "moved_against" if rel == "against the thesis"
                     else "moved", **data)
    return check("T11", PASSED, text + ". The thesis is from this session or the last.", **data)


VOL_OBSERVED = {"active": "After an active state the close stayed inside the typical realized move in 59 to 62% of "
                          "periods, against the 68% it is built for (observed 16 November 2026, not a tested rule).",
                "quiet": "In a quiet state moves have tended to be smaller.", "normal": ""}


def t12_volatility(c: Case, vol_now: dict | None) -> dict:
    frozen = c.measured.get("volatility") or {}
    vol = vol_now or frozen
    state = vol.get("state")
    data = {"state": state, "ratio": vol.get("ratio"), "state_at_freeze": frozen.get("state"),
            "changed_since_freeze": bool(vol_now) and vol_now.get("state") != frozen.get("state"),
            "remeasured": bool(vol_now), "observed": VOL_OBSERVED.get(state or "", "")}
    if not state:
        return check("T12", NC, "Under one year of price history.", **data)
    level = f"Recent volatility is {vol['ratio']:g} times its one-year typical level." if vol.get("ratio") else ""
    if c.view == "range_bound":
        if state == "active":
            return check("T12", FLAGGED, f"The state is now active: the range-bound thesis's invalidation condition is met. {level}",
                         kind="invalidation_met", **data)
        if state == "normal":
            return check("T12", FLAGGED, f"The state is no longer quiet. {level}", kind="no_longer_quiet", **data)
        return check("T12", PASSED, f"Quiet, as the range-bound thesis needs. {level}", **data)
    if state == "active":
        return check("T12", FLAGGED, f"Active. {level} {VOL_OBSERVED['active']} Stage 3 places every strike by that move.",
                     kind="active", **data)
    if state == "quiet":
        return check("T12", PASSED, f"Quiet. {level} {VOL_OBSERVED['quiet']}", note=True, **data)
    return check("T12", PASSED, f"Normal. {level}".strip(), **data)


# ---- step 2: the contract checklist ---------------------------------------------------------

def c1_can_lose(c: Case) -> dict:
    p = (c.cand.get("pays_when_view_right") or {}).get("pct")
    if p is None:
        return check("C1", NC, "The figure could not be computed.")
    bes, spot, move = c.cand.get("break_even") or [], c.contracts.get("spot"), c.contracts.get("typical_move_pct")
    data = {"pays_when_view_right_pct": p, "break_even": bes, "basis": (c.cand.get("pays_when_view_right") or {}).get("basis")}
    if p >= 100:
        return check("C1", PASSED, "Profitable in every historical period in which the thesis held.", **data)
    need = ""
    if bes and spot:
        be = bes[0] if c.view != "bearish" else bes[-1]
        pct = (be / spot - 1) * 100
        data.update({"move_needed_pct": round(pct, 2), "move_needed_typical_moves": round(abs(pct) / move, 2) if move else None})
        side = "between the breakevens" if len(bes) == 2 else f"{'above' if c.view == 'bullish' else 'below'} {_usd(be)}"
        need = f"Needs spot {side}. "
    held = {"bullish": "with a higher close", "bearish": "with a lower close"}.get(c.view, "that stayed inside the typical move")
    return check("C1", FLAGGED, f"{need}Profitable in {p:g}% of periods {held}, before slippage.", **data)


def c2_vol_vs_strategy(c: Case, t12: dict, c1: dict) -> dict:
    state = t12["data"].get("state")
    if not state:
        return check("C2", NC, "No volatility state.")
    if state == "active" and c.cand.get("credit"):
        return check("C2", FLAGGED, "Active volatility and a short-premium strategy: larger moves hurt a premium seller.", state=state)
    if state == "quiet" and c1["result"] == FLAGGED:
        return check("C2", FLAGGED, "Quiet volatility and a strategy that needs a move.", state=state)
    return check("C2", PASSED, f"Volatility is {state}; nothing in the strategy conflicts with it.", state=state)


def c3_expiration(c: Case) -> dict:
    o = next((x for x in c.contracts.get("expiry_options") or [] if x.get("expiration") == c.cand.get("expiry")), None)
    if o is None:
        return check("C3", NC, "The expiration's match to the horizon is not in the record.")
    data = {"dte": o["dte"], "horizon_days": o["serves_days"], "poor_match": o["poor_match"]}
    if o["poor_match"]:
        return check("C3", FLAGGED, f"{o['dte']} DTE against a {o['serves_days']}-day horizon: more than twice as far. "
                                   "Figures assume holding to expiration.", **data)
    return check("C3", PASSED, f"{o['dte']} DTE against a {o['serves_days']}-day horizon.", **data)


def c4_pop_gap(c: Case) -> dict:
    b, i = c.cand.get("base_rate_profit") or {}, c.cand.get("implied_profit") or {}
    base, unc, imp = b.get("pct"), b.get("uncertainty_pts"), i.get("pct")
    data = {"base_rate_profit_pct": base, "uncertainty_pts": unc, "implied_profit_pct": imp}
    if imp is None:
        return check("C4", NC, "No implied volatility for this expiration.", **data)
    if base is None or unc is None:
        return check("C4", NC, "The historical figure or its uncertainty is not available.", **data)
    text = f"POP {base:g}% on the historical base rate (plus or minus {unc:g}) against {imp:g}% market-implied."
    if base < imp - unc:
        return check("C4", FLAGGED, text + " History is below the market by more than its own margin of error.", **data)
    return check("C4", PASSED, text, **data)


def c5_implied_move(c: Case) -> dict:
    imp, typ = c.contracts.get("implied_move_pct"), c.contracts.get("typical_move_pct")
    limit = config()["contract_checks"]["implied_move_ratio"]
    if not imp or not typ:
        return check("C5", NC, "No implied move for this expiration." if not imp else "No typical realized move.")
    ratio = round(imp / typ, 2)
    text = f"Implied move {imp:g}% against a typical realized move of {typ:g}%: {ratio:g} times."
    return check("C5", FLAGGED if ratio >= limit else PASSED,
                 text + (" The market may be pricing an event." if ratio >= limit else ""),
                 implied_move_pct=imp, typical_move_pct=typ, ratio=ratio, threshold=limit, provisional_threshold=True)


def c6_slippage(c: Case) -> dict:
    cost = c.cand.get("cost") or {}
    cap = ((c.contracts.get("filters") or {}).get("cost_cap_pct"))
    share = config()["contract_checks"]["cost_share_of_cap"]
    pct = cost.get("pct_of_risk")
    if pct is None or cap is None:
        return check("C6", NC, "The slippage or the cost cap is not in the record.")
    others = [x for x in c.contracts.get("candidates") or [] if (x.get("cost") or {}).get("pct_of_risk") is not None]
    cheapest = min(others, key=lambda x: x["cost"]["pct_of_risk"], default=None)
    data = {"dollars": cost.get("dollars"), "pct_of_max_loss": pct, "cost_cap_pct": cap, "flag_at_pct": round(share * cap, 2),
            "cheapest": cheapest and {"id": cheapest["id"], "pct_of_max_loss": cheapest["cost"]["pct_of_risk"]}}
    text = f"Est. slippage {_usd(cost.get('dollars') or 0)}, {pct:g}% of max loss, against a {cap:g}% cost cap."
    if pct >= share * cap:
        return check("C6", FLAGGED, text + " Closing before expiration costs about the same again.", **data)
    return check("C6", PASSED, text, **data)


def c7_short_premium(c: Case) -> dict:
    if not c.cand.get("credit"):
        return check("C7", PASSED, "The strategy pays premium; it does not collect it.", credit=False)
    credit, loss = -c.cand.get("net_price", 0), c.cand.get("max_loss") or 0
    q = max(int(c.selection.get("contracts_proposed") or 1), 1)
    context = ("The project's tests found no excess return from rule-based index premium selling after May 2012."
               if c.fund else "A single-name premium is not harvestable at retail trading cost.")
    return check("C7", FLAGGED, f"Net credit {_usd(credit * q)} vs. max loss {_usd(loss * q)}. {context}",
                 credit=True, credit_dollars=round(credit * q, 2), max_loss_dollars=round(loss * q, 2),
                 max_loss_multiple=round(loss / credit, 2) if credit > 0 else None)


def c8_assignment(c: Case) -> dict:
    inst = settings.load_json("instruments.json")
    spec = {**inst["default"], **(inst["instruments"].get(c.symbol) or {})}
    ch = c.cand.get("checks") or {}
    if not spec.get("early_assignment_possible"):
        return check("C8", NA, "European exercise, cash-settled: no early assignment.", exercise=spec.get("exercise"))
    if not ch.get("has_short_leg"):
        return check("C8", NA, "No short leg.", exercise=spec.get("exercise"))
    lines = [line("Short leg in the money", FLAGGED if ch.get("short_leg_in_the_money") else PASSED,
                  "A short leg is in the money at entry." if ch.get("short_leg_in_the_money")
                  else "No short leg is in the money at entry.")]
    ex = (c.contracts.get("events") or {}).get("ex_dividend") or {}
    if ex.get("status") == "not available":
        lines.append(line("Ex-dividend date", NC, "No ex-dividend date is served for this symbol."))
    elif ex.get("date") and ch.get("ex_dividend_before_expiration_short_leg"):
        lines.append(line("Ex-dividend date", FLAGGED, f"Ex-dividend {_day(ex['date'])}, before the expiration, with a short leg.",
                          date=ex["date"]))
    else:
        lines.append(line("Ex-dividend date", PASSED, "No declared ex-dividend date before the expiration."
                          if not ex.get("date") else f"Ex-dividend {_day(ex['date'])}, after the expiration."))
    result = _overall(lines)
    pick = [l for l in lines if l["result"] == result]
    return check("C8", result, " ".join(l["detail"] for l in pick), lines=lines, exercise=spec.get("exercise"))


def c9_order_size(c: Case) -> dict:
    q = max(int(c.selection.get("contracts_proposed") or 1), 1)
    limit = config()["contract_checks"]["order_share_of_open_interest_pct"]
    legs = c.cand.get("legs") or []
    if not legs or any(l.get("open_interest") is None for l in legs):
        return check("C9", NC, "Open interest is missing for a leg.", contracts=q)
    worst = min(legs, key=lambda l: l["open_interest"])
    share = round(100 * q / worst["open_interest"], 1) if worst["open_interest"] else None
    data = {"contracts": q, "min_open_interest": worst["open_interest"], "share_pct": share, "limit_pct": limit}
    text = f"{_n(q, 'contract').capitalize()} against open interest of {worst['open_interest']:,} on the thinnest leg"
    if share is None or share > limit:
        return check("C9", FLAGGED, text + f": above {limit}%.", **data)
    return check("C9", PASSED, text + (f": {share:g}%." if share >= 0.1 else ": under 0.1%."), **data)


PRIORITY_NAME = {"match": "fit to thesis", "payoff": "reward-to-risk", "cost": "lowest slippage"}


def _measure(x: dict, priority: str) -> str:
    if priority == "payoff":
        r = (x.get("payoff_at_one_move") or {}).get("per_dollar_at_risk")
        return "not available" if r is None else f"${r:.2f} per $1 at risk"
    if priority == "cost":
        p = (x.get("cost") or {}).get("pct_of_risk")
        return "not available" if p is None else f"slippage {p:g}% of max loss"
    p = (x.get("pays_when_view_right") or {}).get("pct")
    return "not available" if p is None else f"profitable in {p:g}% of periods in which the thesis held"


def c10_passed_over(c: Case) -> dict:
    chosen, best, pr = c.selection.get("id"), c.selection.get("best_fit_id"), c.selection.get("priority") or "match"
    by_id = {x["id"]: x for x in c.contracts.get("candidates") or []}
    data = {"chosen_id": chosen, "best_fit_id": best, "priority": pr}
    if chosen != best:
        a, b = by_id.get(chosen, c.cand), by_id.get(best)
        cmp_ = f" Selected: {_measure(a, pr)}. Best fit: {_measure(b, pr)}." if b else ""
        return check("C10", FLAGGED, f"You selected a candidate other than the best fit on {PRIORITY_NAME[pr]}.{cmp_}", **data)
    if pr != "match":
        return check("C10", PASSED, f"The best fit was selected, ranked by {PRIORITY_NAME[pr]}, not by the default.",
                     note=True, **data)
    return check("C10", PASSED, "The best fit on the default ranking was selected.", **data)


def c11_price_moved(c: Case, fresh: dict) -> dict:
    was, slip = c.cand.get("net_price"), (c.cand.get("cost") or {}).get("dollars")
    data = {"net_price_at_selection": was, "slippage_dollars": slip, "selection_quotes_as_of": c.contracts.get("as_of"),
            "fresh_as_of": fresh.get("as_of")}
    if fresh.get("legs") is None or was is None or slip is None:
        return check("C11", NC, (fresh.get("reason") or "the selected legs were not found in the fresh quotes").capitalize()
                     + ". The figures are from " + ("the last session." if not fresh.get("market_open") else "the selection."), **data)
    net = 0.0
    for l in c.cand["legs"]:
        q = fresh["legs"].get(l["occ"])
        if q is None:
            return check("C11", NC, "A selected leg has no two-sided quote now.", **data)
        net += (1 if l["action"] == "buy" else -1) * q
    net = round(net * 100, 2)
    moved = round(abs(net - was), 2)
    data.update({"net_price_now": net, "moved_dollars": moved})
    word = "credit" if c.cand.get("credit") else "debit"
    text = (f"Net {word} {_usd(abs(was))} at selection, {_usd(abs(net))} now: moved {_usd(moved)}, "
            f"against est. slippage of {_usd(slip)}.")
    if moved > slip:
        return check("C11", FLAGGED, text + " The figures the selection rested on are out of date.", **data)
    return check("C11", PASSED, text, **data)


# ---- the fresh quotes (operator decision, 19 November 2026) ------------------------------

def fresh_quotes(state: dict, ctx) -> dict:
    """One fetch of the option chain when stage 4 starts: the current price for thesis
    check 11 and the selected legs' mids for contract check C11. It does not replace
    the chain stage 3 holds. A failure here is "could not be checked", never a stop."""
    market = session.status()
    sel = state.get("selection") or {}
    out = {"market_open": bool(market.get("open")), "spot": None, "legs": None, "as_of": None, "reason": None}
    if not market.get("open"):
        return {**out, "reason": "the market is closed"}
    if (state.get("contracts") or {}).get("provisional"):
        return {**out, "reason": "the selection was made on the snapshot, not on live quotes"}
    try:
        data = chain_data.live(state["symbol"], ctx.store)
    except chain_data.ChainUnavailable as e:
        return {**out, "reason": f"the live option chain could not be retrieved ({e})"}
    want = {l.get("occ") for l in (sel.get("candidate") or {}).get("legs") or []}
    legs = {}
    for c in data["contracts"]:
        if c["occ"] in want and c.get("bid") is not None and c.get("ask") is not None and c["ask"] >= c["bid"] > 0:
            legs[c["occ"]] = (c["bid"] + c["ask"]) / 2
    return {**out, "spot": data["spot"], "legs": legs, "as_of": data["as_of"]}


def _vol_now(c: Case, ctx) -> dict | None:
    try:
        series = prices.closes(figures.HISTORY_OF.get(c.symbol, c.symbol), ctx.store)["closes"]
        return figures.volatility_state(figures._lookback([x for _, x in series]))
    except Exception:  # noqa: BLE001 - not re-measured: the state at the freeze is used and said to be
        return None


def run_checklists(c: Case, fresh: dict, vol_now: dict | None, records: list[dict]) -> dict:
    t12 = t12_volatility(c, vol_now)
    c1 = c1_can_lose(c)
    thesis = [t1_rejected_signal(c), t2_concentrated(c), t3_strength(c), t4_contested(c), t5_base_rate(c),
              t6_events(c), t7_risk_flags(c), t8_invalidation(c), t9_origin(c), t10_overrides(c, records),
              t11_price_moved(c, fresh), t12]
    contract = [c1, c2_vol_vs_strategy(c, t12, c1), c3_expiration(c), c4_pop_gap(c), c5_implied_move(c),
                c6_slippage(c), c7_short_premium(c), c8_assignment(c), c9_order_size(c), c10_passed_over(c),
                c11_price_moved(c, fresh)]
    return {"thesis": thesis, "contract": contract, "horizon_days": c.days, "horizon_amended": c.amended,
            "fresh_quotes": {k: fresh.get(k) for k in ("market_open", "spot", "as_of", "reason")},
            "counts": {"thesis": counts(thesis), "contract": counts(contract)}, "at": now().isoformat(timespec="seconds")}


def counts(checks: list[dict]) -> dict:
    return {r: sum(x["result"] == r for x in checks) for r in (FLAGGED, NC, NA, PASSED)}


def checklists_step(state, ctx) -> dict:
    c = Case(state)
    records = ctx.store.records(ctx.request_id) + ctx.store.pending(ctx.request_id)
    return run_checklists(c, fresh_quotes(state, ctx), _vol_now(c, ctx), records)


# ---- step 3: the thesis restated as a question -----------------------------------------------

def _plain(text: str) -> str:
    t = CONFIDENCE_WORDS.sub("", text or "").strip()
    return t[:1].upper() + t[1:] if t else t


def restate(c: Case) -> dict:
    """A fixed template; no model. It never uses the written basis or the user's wording,
    and it does not say who wrote the thesis."""
    where = {"bullish": "above", "bearish": "below", "range_bound": "within the typical realized move of"}[c.view]
    claims = [{"id": f"CL{i}", "n": i, "text": _plain(f.get("text") or f.get("finding") or ""), "evidence_id": f["id"]}
              for i, f in enumerate(c.relied_on(), 1)]
    return {"question": f"Do the following support a close {where} the reference price for {c.symbol} at {c.days} days?",
            "direction": c.view, "horizon_days": c.days, "claims": claims}


def question_step(state, ctx) -> dict:
    return restate(Case(state))


# ---- step 4: retrieval from the research corpus ----------------------------------------------

class TopicResult(BaseModel):
    topic_id: str
    supporting: list[str] = Field(default=[], description="Passage ids that bear on the topic and say the reasoning has worked.")
    opposing: list[str] = Field(default=[], description="Passage ids that bear on the topic and say it has not worked.")


class RetrievalAnswer(BaseModel):
    topics: list[TopicResult]


RETRIEVER_RESEARCH = """You are the Evidence Retriever of a research system, searching the project's own research
corpus. You are given a list of topics. Each is a kind of reasoning behind a trade (for example "results above
estimates as a reason for a higher price") or a type of option strategy. For each topic you find what the research
says about whether that kind of reasoning has worked, on both sides.

For each topic, call search_research once with two queries:
- supports_query: worded as the finding that the reasoning HAS worked (for example "stocks rise in the weeks after
  earnings beat estimates; post-earnings announcement drift").
- opposes_query: worded as the finding that it has NOT worked (for example "post-earnings drift has disappeared in
  liquid stocks; an earnings beat is already priced in").
Word each query about the kind of reasoning in general. Leave out the company's name, the ticker and its figures:
the corpus is research about methods and markets, not about this company.

If a search returns nothing for a topic, reword both queries once and call search_research again for that topic.
After the second attempt, report the topic with empty lists. Do not search a topic a third time.

Then read the passages returned. For each topic, list under "supporting" the ids of passages that clearly bear on
the topic and say the reasoning has worked, and under "opposing" those that clearly bear on it and say it has not,
or that it fails after costs. Leave out a passage that is only loosely related: nothing is better than something
loosely related. At most three ids a side, the most relevant first. A passage goes on one side only.

Draw no conclusion. Do not say which side is stronger, state no view on the trade, and add no fact of your own.
Use only passage ids that a search returned. Answer with every topic you were given, by its topic_id."""


def retriever_research(seen: dict[str, dict], topic_ids: list[str]) -> AgentConfig:
    def passages_exist(a: RetrievalAnswer) -> list[str]:
        errors = []
        bad = sorted({p for t in a.topics for p in t.supporting + t.opposing if p not in seen})
        if bad:
            errors.append(f"These passage ids were not returned by a search: {', '.join(bad)}. Use only ids you were given.")
        unknown = sorted({t.topic_id for t in a.topics} - set(topic_ids))
        if unknown:
            errors.append(f"These topic ids are not on your list: {', '.join(unknown)}.")
        both = sorted({p for t in a.topics for p in set(t.supporting) & set(t.opposing)})
        if both:
            errors.append(f"A passage goes on one side only: {', '.join(both)}.")
        return errors
    return AgentConfig(name="evidence_retriever", role="evidence_retriever.research", instructions=RETRIEVER_RESEARCH,
                       output_model=RetrievalAnswer, effort="low", tools=["search_research"],
                       output_guards=[_named("passages_exist", passages_exist), no_probability])


def search_tool(index, seen: dict[str, dict], log: dict[str, list], topic_ids: list[str]) -> Tool:
    """The one tool of the stage 4 Retriever: both searches for one topic in one call.
    Code applies the relevance bar, and allows each topic one reworded retry."""
    cfg = research.config()
    bar = index.bar()

    def run(ctx, topic_id: str, supports_query: str, opposes_query: str):
        if topic_id not in topic_ids:
            return {"error": f"'{topic_id}' is not one of your topics: {', '.join(topic_ids)}."}
        tries = log.setdefault(topic_id, [])
        if len(tries) >= 2:
            return {"topic_id": topic_id, "refused": "This topic has been searched and reworded once already. "
                                                     "Report it with empty lists."}
        found = {}
        for side, q in (("supports", supports_query), ("opposes", opposes_query)):
            hits = [h for h in index.search(q, cfg["results_per_search"]) if h["score"] >= bar]
            for h in hits:
                seen.setdefault(h["id"], {k: h[k] for k in ("id", "source", "section", "grade", "text")})
                seen[h["id"]].setdefault("topics", set()).add(topic_id)
                best = seen[h["id"]].setdefault("score", {})
                best[topic_id] = max(best.get(topic_id, 0), h["score"])
            found[side] = [{"id": h["id"], "source": h["source"], "section": h["section"], "evidence_grade": h["grade"],
                            "text": h["text"][:cfg["passage_chars_for_agents"]]} for h in hits]
        tries.append({"supports_query": supports_query, "opposes_query": opposes_query,
                      "returned": sorted({p["id"] for v in found.values() for p in v})})
        out = {"topic_id": topic_id, "returned_for_supports_query": found["supports"],
               "returned_for_opposes_query": found["opposes"]}
        if not found["supports"] and not found["opposes"]:
            out["note"] = ("Nothing passed the relevance bar. Reword both queries once and search this topic again."
                           if len(tries) == 1 else "Nothing passed the relevance bar after rewording. Report nothing found.")
        return out

    props = {"topic_id": {"type": "string"},
             "supports_query": {"type": "string", "description": "The finding that this kind of reasoning has worked."},
             "opposes_query": {"type": "string", "description": "The finding that it has not worked."}}
    return Tool("search_research", "Search the project's research corpus for one topic, both ways. Returns the passages "
                "that pass the relevance bar for each query, each with an id, its source report, section and evidence grade.",
                {"type": "object", "properties": props, "required": list(props), "additionalProperties": False},
                run, untrusted=True, source="the project's research corpus")


STRUCTURE_TOPIC = {
    True: "{name}: a short-premium (net credit) option strategy with defined risk on {kind}, held to expiration; "
          "whether selling option premium earns a return after trading costs",
    False: "{name}: buying options (a net debit, defined risk) on {kind} to express a directional view; whether "
           "bought options pay after trading costs and time decay",
}


def topics_for(c: Case, question: dict) -> list[dict]:
    limit = research.config()["max_topics"]
    out = [{"id": f"TP{cl['n']}", "kind": "claim", "claim_id": cl["id"], "text": cl["text"]}
           for cl in question["claims"][:limit - 1]]
    kind = "an index fund" if c.fund else "a single stock"
    name = c.cand.get("structure") or "The selected strategy"
    out.append({"id": "TPS", "kind": "structure", "claim_id": None,
                "text": STRUCTURE_TOPIC[bool(c.cand.get("credit"))].format(name=name, kind=kind)})
    return out


SAVED_DIR = "stage4-saved"


def saved_path(state: dict):
    """Where a live run's two agent outputs are kept for the development replay app
    (operator decision, 19 November 2026): one file per symbol and selected candidate."""
    cand = ((state.get("selection") or {}).get("id")) or "none"
    return settings.data_dir() / SAVED_DIR / f"{state['symbol'].upper()}.{cand}.json"


def _save(state: dict, ctx, key: str, out: dict) -> None:
    if "model" in ctx.extras:                    # a scripted model (tests, replay): nothing to keep
        return
    try:
        p = saved_path(state)
        p.parent.mkdir(exist_ok=True)
        kept = json.loads(p.read_text()) if p.exists() else {}
        kept[key] = out
        kept["saved_at"] = now().isoformat(timespec="seconds")
        p.write_text(json.dumps(kept, default=str, indent=1))
    except OSError:
        pass


def _index(ctx):
    if "research_index" in ctx.extras:
        return ctx.extras["research_index"], None
    return research.open_index()


def no_passages(reason: str, method: str | None = None, topics: list[dict] | None = None, **extra) -> dict:
    return {"method": method or "none", "retrieved": False, "reason": reason,
            "topics": [{**t, "for": [], "against": [], "nothing_found": True, "searches": []} for t in topics or []],
            "passages": {}, **extra}


def passages_step(state, ctx) -> dict:
    """Step 4. If the index or the Retriever fails, the Critic runs on the checklists and
    the thesis record alone and the screen says so (operator decision, 19 November 2026)."""
    c = Case(state)
    question = state.get("question") or restate(c)
    topics = topics_for(c, question)
    if ctx.extras.get("no_passages"):                       # the replay app's switch
        return no_passages(ctx.extras["no_passages"], topics=topics)
    index, note = _index(ctx)
    if index is None:
        return no_passages(note or "the research index is not available", topics=topics)
    seen: dict[str, dict] = {}
    log: dict[str, list] = {}
    ids = [t["id"] for t in topics]
    reg = ToolRegistry()
    reg.register(search_tool(index, seen, log, ids))
    task = ("TOPICS:\n" + "\n".join(f"- {t['id']} ({t['kind']}): {t['text']}" for t in topics)
            + "\n\nSearch each topic both ways, then answer with every topic.")
    from .harness import run_agent
    r = run_agent(retriever_research(seen, ids), task, model=stage2._model(ctx), registry=reg, store=ctx.store,
                  request_id=ctx.request_id, cancel=ctx.cancel)
    info = stage2._run_info(r)
    if r.status == "cancelled":
        raise StepFailed("agent_failed", r.message, agent="evidence_retriever")
    if not r.ok:
        return no_passages(f"the Evidence Retriever did not finish ({r.message})", method=index.method,
                           topics=topics, run=info, index_note=note)
    cap = research.config()["passages_per_side"]
    by_topic = {t.topic_id: t for t in r.output.topics}
    used, out_topics = {}, []
    for t in topics:
        a = by_topic.get(t["id"])
        sides = {"for": (a.supporting if a else [])[:cap], "against": (a.opposing if a else [])[:cap]}
        for pid in sides["for"] + sides["against"]:
            used[pid] = seen[pid]
        out_topics.append({**t, **sides, "nothing_found": not (sides["for"] or sides["against"]),
                           "searches": log.get(t["id"], [])})
    refs = {pid: f"P{i}" for i, pid in enumerate(used, 1)}
    passages = {refs[pid]: {"ref": refs[pid], "passage_id": pid, "source": p["source"], "section": p["section"],
                            "grade": p["grade"], "text": p["text"]} for pid, p in used.items()}
    for t in out_topics:
        t["for"] = [refs[p] for p in t["for"]]
        t["against"] = [refs[p] for p in t["against"]]
    out = {"method": index.method, "retrieved": bool(passages), "index_note": note,
           "reason": None if passages else "nothing in the research passed the relevance bar",
           "relevance_bar": index.bar(), "topics": out_topics, "passages": passages, "run": info}
    _save(state, ctx, "passages", out)
    return out


# ---- step 5: the Critic --------------------------------------------------------------------

Standing = Literal["holds", "holds_in_a_narrower_form", "does_not_hold"]


class DependsOn(BaseModel):
    claim_id: str
    why: str


class Reworded(BaseModel):
    claim_id: str
    signal_id: str = Field(description="The id of the entry on the rejected-signal list.")
    note: str


class Clash(BaseModel):
    claim_ids: list[str] = Field(min_length=2)
    note: str


class Linked(BaseModel):
    checks: list[str] = Field(min_length=2, description="Check ids that are one problem, e.g. ['T2', 'T3'].")
    note: str


class PricedIn(BaseModel):
    claim_id: str
    reading: str


class LossPath(BaseModel):
    title: str = Field(description="A few words naming the path to a loss.")
    text: str = Field(description="One or two sentences.")
    grounds: list[str] = Field(description="A check id or a finding id.")


class Missing(BaseModel):
    ref: str = Field(description="The id of the unavailable input, e.g. U2.")
    why_it_matters: str


class Disposition(BaseModel):
    claim_id: str
    standing: Standing
    reason: str


class Objection(BaseModel):
    title: str = Field(description="The objection in one short sentence.")
    text: str = Field(description="One or two sentences.")
    grounds: list[str] = Field(description="What it rests on: check ids, claim ids, passage ids, finding ids.")


class Critique(BaseModel):
    depends_on: DependsOn | None = None
    rejected_signals_in_other_words: list[Reworded] = []
    claims_that_do_not_fit: list[Clash] = []
    checks_that_are_one_problem: list[Linked] = []
    case_for: str
    priced_in: list[PricedIn] = []
    case_against: str
    loss_paths: list[LossPath]
    missing: list[Missing] = []
    dispositions: list[Disposition]
    objections: list[Objection] = []


CRITIC = """You are the Critic of a research system. You are given a question about one underlying, the claims
behind it, recorded evidence, the results of two fixed-rule checklists (one on the thesis, one on the selected
option strategy), and passages from the project's own research. You examine the question from both sides.
You have no tools and you do no research of your own.

Ids go only in the fields made for them (grounds, claim_id, checks, ref). Never write an id such as F2, T3 or P1
inside a sentence: every sentence is shown to a reader who does not see the ids.

Everything you are given has an id: claims (CL1, CL2), findings (F1, R2), thesis checks (T1 to T12), contract
checks (C1 to C11), passages (P1, P2), priced-in figures (one per claim), unavailable inputs (U1, U2), and the
entries of the rejected-signal list. Cite by id. Use nothing else: not your memory and not general knowledge
about the company.

Do these nine tasks, once, in one pass:
1. depends_on: the one claim whose removal would leave nothing, and why.
2. rejected_signals_in_other_words: a claim that rests on a signal on the rejected-signal list but describes it
   in other words. Cite the claim and the list entry. Leave empty if there is none.
3. claims_that_do_not_fit: claims that contradict each other. Leave empty if there is none.
4. checks_that_are_one_problem: flagged checks, from either checklist, that are the same problem seen twice.
5. case_for: the strongest case for the outcome in the question. Required.
6. priced_in: for each claim you named in task 1 (and any other the question leans on), read the priced-in figure
   you were given: the price move since the finding became public, in percent and in typical realized moves. Say
   what the figure shows. Interpret the figure; do not guess where none is given.
7. case_against: the strongest case for the opposite outcome or for no move. Build it only from the recorded
   opposing findings, the base rate, the flagged checks and the passages. Required, and no longer than case_for's
   limit.
8. loss_paths: two or three specific ways the selected strategy loses money. Each cites a check or a finding.
9. missing: evidence that would be expected and is absent. You may name only items on the list of unavailable
   inputs, by id. Do not invent a gap.

Then:
- dispositions: for EVERY claim, exactly one standing: holds, holds_in_a_narrower_form, or does_not_hold, with
  the reason. Skip no claim.
- objections: at most {max_objections}, the most serious first. Every objection cites its grounds: a check, a claim,
  a passage or a finding. An objection with no grounds is not allowed. If the checks are clean and nothing stands
  against the question, give few objections or none: you may concede.

Hard limits:
- case_for and case_against: at most {case_words} words each, plain prose, no ids inside the text. The limit is
  checked by counting words, so aim for about {case_aim} words each to stay under it.
- Give NO verdict, score, rating or confidence figure, and NO advice on whether to trade, enter, size, wait or
  avoid. Do not say the trade is good, bad, attractive or worth taking. You describe; the reader decides.
- State no probability of your own. You may quote a percentage you were given, with what it measures.
- Write for a reader who trades options: plain sentences, no jargon beyond the terms you were given."""


def critic_config(known: dict, content_check) -> AgentConfig:
    c = config()["critic"]
    return AgentConfig(name="critic", role="critic.challenge",
                       instructions=CRITIC.format(max_objections=c["max_objections"], case_words=c["case_max_words"],
                                                  case_aim=int(c["case_max_words"] * 0.8)),
                       output_model=Critique, tools=[], effort="medium",
                       output_guards=[_named("output_check", content_check), _named("no_verdict_or_advice", no_verdict)])


_VERDICT = re.compile(
    r"\b(you should|i (would|'d) (recommend|suggest|advise)|we recommend|i recommend|my recommendation|recommended trade|"
    r"(do not|don't|should not|shouldn't) (take|enter|place|make|put on) (the|this) (trade|position)|"
    r"(take|skip|avoid|pass on|stay out of|go ahead with|proceed with) (the|this) (trade|position)|"
    r"worth (taking|trading|the risk)|not worth (taking|trading|the risk)|(strong )?(buy|sell) (rating|signal)|"
    r"(overall|on balance|in sum|net)[, ]+(the|this) (trade|thesis|setup) (is|looks|seems) (good|bad|sound|unsound|"
    r"attractive|unattractive|weak|strong|favou?rable|unfavou?rable)|"
    r"verdict|(confidence|conviction)( level| score)?( is|:| of)? ?(high|low|medium|\d)|\b\d{1,2} ?/ ?10\b|out of (10|ten)|"
    r"score of \d|rating of \d|i am \d{1,3}% (sure|confident))", re.IGNORECASE)


def no_verdict(answer: Critique) -> list[str]:
    from .harness.guards import _strings
    out = []
    for path, text in _strings(answer):
        m = _VERDICT.search(text)
        if m:
            out.append(f"No verdict, score or trading advice: {path} says '{m.group(0)}'.")
    return out[:3]


def _words(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def output_check(a: Critique, known: dict) -> list[str]:
    """The code check on the Critic's output, before the user sees it. Each failure is
    one short sentence naming the rule."""
    cfg = config()["critic"]
    claims, checks_, everything = known["claims"], known["checks"], known["all"]
    errors = []

    def bad(ids, allowed):
        return sorted({i for i in ids if i not in allowed})

    seen = [d.claim_id for d in a.dispositions]
    missing = [c for c in claims if c not in seen]
    if missing:
        errors.append(f"Every claim needs a standing: none given for {', '.join(missing)}.")
    if len(seen) != len(set(seen)) or bad(seen, claims):
        errors.append("Each claim gets exactly one standing, and only claims on the list.")
    for name, text in (("The case for", a.case_for), ("The case against", a.case_against)):
        if not (text or "").strip():
            errors.append(f"{name} is missing.")
        elif _words(text) > cfg["case_max_words"]:
            errors.append(f"{name} is {_words(text)} words; the limit is {cfg['case_max_words']}.")
    if len(a.objections) > cfg["max_objections"]:
        errors.append(f"At most {cfg['max_objections']} objections; {len(a.objections)} were given.")
    for i, o in enumerate(a.objections, 1):
        if not o.grounds:
            errors.append(f"Objection {i} cites no grounds.")
        elif bad(o.grounds, everything):
            errors.append(f"Objection {i} cites grounds that do not exist: {', '.join(bad(o.grounds, everything))}.")
    lo, hi = cfg["loss_paths"]
    if not lo <= len(a.loss_paths) <= hi:
        errors.append(f"Give {lo} or {hi} ways the trade loses; {len(a.loss_paths)} were given.")
    for i, p in enumerate(a.loss_paths, 1):
        allowed = checks_ | known["findings"]
        if not p.grounds or bad(p.grounds, allowed):
            errors.append(f"Loss path {i} must cite a check or a finding that exists.")
    if bad([m.ref for m in a.missing], known["unavailable"]):
        errors.append("What is missing may name only inputs recorded as unavailable.")
    cited = ([a.depends_on.claim_id] if a.depends_on else []) + [p.claim_id for p in a.priced_in] \
        + [r.claim_id for r in a.rejected_signals_in_other_words] + [i for x in a.claims_that_do_not_fit for i in x.claim_ids]
    if bad(cited, claims):
        errors.append(f"These claim ids do not exist: {', '.join(bad(cited, claims))}.")
    if claims and a.depends_on is None:
        errors.append("Name the claim the thesis depends on.")
    if bad([r.signal_id for r in a.rejected_signals_in_other_words], known["signals"]):
        errors.append("A rejected signal must be cited by its id on the list.")
    if bad([i for x in a.checks_that_are_one_problem for i in x.checks], checks_):
        errors.append("Checks read together must be cited by ids that exist.")
    return errors


def priced_in_figures(c: Case, question: dict, series) -> dict:
    """Code supplies the price move since each claim's finding became public, in percent
    and in typical realized moves (`evidence[].price_move_since`). Computed here; stage 2
    records the percentage for the findings that carry a direction."""
    from . import context
    move = (c.row or {}).get("typical_move_pct")
    out = {}
    for cl in question["claims"]:
        f = c.findings.get(cl["evidence_id"]) or {}
        pct = context.move_since(series, f.get("date")) if series and f.get("date") else None
        out[cl["id"]] = {"claim_id": cl["id"], "finding_id": f.get("id"), "since": f.get("date"),
                         "pct": None if pct is None else round(pct, 1),
                         "typical_moves": None if pct is None or not move else round(abs(pct) / move, 2),
                         "typical_move_pct": move, "horizon_days": c.days}
    return out


def _for_critic(checks: list[dict]) -> list[dict]:
    """The checklist results as the Critic receives them. Check 9 is withheld: it says
    who wrote the thesis (operator decision, 19 November 2026)."""
    out = []
    for x in checks:
        if x["id"] == "T9":
            continue
        detail = x["detail"]
        if x["id"] == "T7" and x["data"].get("severe_overridden"):
            detail = "A severe risk flag was raised."
        out.append({"id": x["id"], "check": x["name"], "result": x["result"].replace("_", " "),
                    **({"passed_with_a_note": True} if x["note"] else {}), "detail": detail,
                    **({"lines": [{"name": l["name"], "result": l["result"].replace("_", " "), "detail": l["detail"]}
                                  for l in x["lines"] if l["result"] != NA]} if x["lines"] else {})})
    return out


def critic_brief(c: Case, state: dict, priced: dict) -> tuple[str, dict]:
    """What the Critic is given, and the ids it may cite."""
    q, lists, pas = state["question"], state["checklists"], state.get("passages") or {}
    claims = q["claims"]
    relied = {cl["evidence_id"] for cl in claims}

    def slim(f):
        return {"id": f["id"], "text": f.get("text"), "bearing": f.get("bearing"), "grade": f.get("grade"),
                "date": f.get("date"), "family": f.get("family"), "source": f.get("source")}
    opposing = [slim(f) for f in c.opposing()]
    context_ = [slim(f) for f in c.findings.values() if f["id"] not in relied and f.get("bearing") == "none"][:12]
    unavailable = {f"U{i}": u for i, u in enumerate(c.thesis.get("inputs_unavailable") or [], 1)}
    signals = [{"id": s["id"], "name": s["name"], "reason": s["reason"]}
               for s in settings.load_json("rejected_signals.json")["signals"]]
    cand = c.cand
    qty = max(int(c.selection.get("contracts_proposed") or 1), 1)
    contract = {"strategy": cand.get("name"), "expiration": cand.get("expiry"), "dte": cand.get("dte"),
                "contracts": qty, "spot": c.contracts.get("spot"),
                "legs": [{k: l.get(k) for k in ("action", "type", "strike")} for l in cand.get("legs") or []],
                "net_price_per_contract": cand.get("net_price"), "collects_premium": cand.get("credit"),
                "max_loss_per_contract": cand.get("max_loss"), "max_profit_per_contract": cand.get("max_gain"),
                "breakeven": cand.get("break_even"),
                "profitable_if_thesis_holds_pct": (cand.get("pays_when_view_right") or {}).get("pct"),
                "pop_historical_base_rate_pct": (cand.get("base_rate_profit") or {}).get("pct"),
                "pop_market_implied_pct": (cand.get("implied_profit") or {}).get("pct"),
                "est_slippage": cand.get("cost"), "typical_realized_move_pct": c.contracts.get("typical_move_pct"),
                "implied_move_pct": c.contracts.get("implied_move_pct")}
    passages = [{"id": p["ref"], "source": p["source"], "section": p["section"], "evidence_grade": p["grade"],
                 "text": p["text"][:research.config()["passage_chars_for_agents"] * 2]} for p in (pas.get("passages") or {}).values()]
    topics = [{"topic": t["text"], "for": t["for"], "against": t["against"]} for t in pas.get("topics") or []]
    parts = [
        f"QUESTION: {q['question']}",
        "CLAIMS (each with the finding it rests on, that finding's grade set by code, and the priced-in figure):\n"
        + wrap_untrusted(json.dumps([{**{k: cl[k] for k in ("id", "text")}, "finding": cl["evidence_id"],
                                      "grade": (c.findings.get(cl["evidence_id"]) or {}).get("grade"),
                                      "date": (c.findings.get(cl["evidence_id"]) or {}).get("date"),
                                      "carries_a_direction": (c.findings.get(cl["evidence_id"]) or {}).get("bearing") != "none",
                                      "priced_in": {k: priced[cl["id"]][k] for k in ("since", "pct", "typical_moves")}}
                                     for cl in claims], ensure_ascii=False), "the thesis record"),
        "RECORDED FINDINGS THAT CARRY THE OPPOSITE DIRECTION:\n"
        + (wrap_untrusted(json.dumps(opposing, ensure_ascii=False), "the thesis record") if opposing else "none"),
        "OTHER RECORDED FINDINGS (context: they carry no direction):\n"
        + (wrap_untrusted(json.dumps(context_, ensure_ascii=False), "the thesis record") if context_ else "none"),
        "THESIS CHECKS (fixed rules, set by code):\n" + json.dumps(_for_critic(lists["thesis"]), ensure_ascii=False),
        "CONTRACT CHECKS (fixed rules, set by code):\n" + json.dumps(_for_critic(lists["contract"]), ensure_ascii=False),
        "THE SELECTED STRATEGY (figures set by code; dollar figures are for one contract):\n" + json.dumps(contract),
        "INPUTS RECORDED AS UNAVAILABLE:\n" + (json.dumps(unavailable, ensure_ascii=False) if unavailable else "none"),
        "REJECTED-SIGNAL LIST:\n" + json.dumps(signals, ensure_ascii=False),
        "RESEARCH PASSAGES (from the project's own research; each topic was searched both ways):\n"
        + (wrap_untrusted(json.dumps({"passages": passages, "by_topic": topics}, ensure_ascii=False),
                          "the project's research corpus") if passages
           else "No research passages were retrieved. Work from the record and the checklists alone."),
    ]
    check_ids = {x["id"] for x in lists["thesis"] + lists["contract"] if x["id"] != "T9"}
    known = {"claims": [cl["id"] for cl in claims], "checks": check_ids,
             "findings": set(c.findings), "unavailable": set(unavailable), "signals": {s["id"] for s in signals},
             "passages": {p["id"] for p in passages}}
    known["all"] = set(known["claims"]) | check_ids | known["findings"] | known["passages"] | known["unavailable"]
    return "\n\n".join(parts), {"known": known, "unavailable": unavailable}


def _model_family(model_id: str) -> str:
    return "Claude" if model_id.startswith("claude") else model_id.split("-")[0]


def critic_step(state, ctx) -> dict:
    """Step 5. The output check runs here, on the harness, and nowhere else (one return in
    total). A readable answer that fails twice is returned as rejected; anything else that
    does not finish stops the stage."""
    if testfail.take("critic_fail_once", ctx.request_id):          # developer-only, off by default
        raise StepFailed("agent_failed", "The Critic could not complete: a test failure, made by the developer "
                                         "switch critic_fail_once.", agent="critic")
    from . import context
    c = Case(state)
    series = context.fetch(figures.HISTORY_OF.get(c.symbol, c.symbol), ctx.store)
    priced = priced_in_figures(c, state["question"], series)
    task, extra = critic_brief(c, state, priced)
    known = extra["known"]
    cfg = critic_config(known, lambda a: output_check(a, known))
    from .harness import run_agent
    r = run_agent(cfg, task, model=stage2._model(ctx), registry=ToolRegistry(), store=ctx.store,
                  request_id=ctx.request_id, cancel=ctx.cancel)
    thesis_model = settings.models()["agents"]["thesis"]["model"]
    meta = {"run": stage2._run_info(r), "model": cfg.model_id(), "model_family": _model_family(cfg.model_id()),
            "same_family_as_thesis_agent": _model_family(cfg.model_id()) == _model_family(thesis_model),
            "priced_in_figures": priced, "unavailable": extra["unavailable"]}
    if r.ok:
        out = r.output.model_dump()
        tally = {s: sum(d["standing"] == s for d in out["dispositions"])
                 for s in ("holds", "holds_in_a_narrower_form", "does_not_hold")}
        done = {**out, **meta, "standing_counts": tally,
                "check": {"ok": True, "failed_checks": [], "returned_once": r.returned, "in_harness": True}}
        _save(state, ctx, "critic", done)
        return done
    if r.status == "failed_validation" and r.rejected_output is not None:
        return {"rejected": True, "output": r.rejected_output.model_dump(), **meta,
                "check": {"ok": False, "failed_checks": r.errors[:3], "returned_once": True, "in_harness": True}}
    raise stage2._failure(r)


def critic_check_step(state, ctx) -> dict:
    """The check itself ran on the harness, as the Critic's output check. This step
    reports its result to the workflow."""
    return dict(state["critic"]["check"])


# ---- the readiness line ---------------------------------------------------------------------

def readiness(state: dict) -> dict:
    """Set by code. It is about whether the inputs are still valid, not about merit;
    flags are not counted into a rating; it never blocks."""
    lists = state.get("checklists") or {"thesis": [], "contract": []}
    by = {x["id"]: x for x in lists["thesis"] + lists["contract"]}
    t11, t12, c11 = by.get("T11", {}), by.get("T12", {}), by.get("C11", {})
    conditions = []
    if (t11.get("data") or {}).get("stale"):
        conditions.append({"check": "T11", "text": "The thesis was frozen more than one trading session ago.",
                           "remedy": "Start a new analysis to redraft the thesis."})
    if c11.get("result") == FLAGGED:
        conditions.append({"check": "C11", "text": "The strategy's price has moved by more than its slippage since you selected it.",
                           "remedy": "Return to contracts to select on current quotes."})
    if (t12.get("data") or {}).get("kind") == "invalidation_met":
        conditions.append({"check": "T12", "text": "Volatility is now active, which meets the range-bound thesis's "
                                                   "invalidation condition.",
                           "remedy": "Start a new analysis to redraft the thesis."})
    un = state.get("critic_unavailable")
    if un:
        conditions.append({"check": None, "text": un["reason"] if un.get("kind") == "rejected" else
                           "The Critic's output is not available: " + un["reason"],
                           "remedy": "The challenge rests on the fixed-rule checks alone."})
    items = sum(x["result"] in (FLAGGED, NC) for x in by.values())
    if conditions:
        n = len(conditions)
        return {"label": "Not ready", "state": "not_ready", "conditions": conditions, "items": items,
                "headline": f"{n} blocking condition{'s' if n > 1 else ''}.",
                "sentence": " ".join(f"{x['text']} {x['remedy']}" for x in conditions)}
    fresh = lists.get("fresh_quotes") or {}
    age = "The thesis is from this session" if (t11.get("data") or {}).get("sessions_since_freeze") == 0 \
        else "The thesis is from the last session" if t11 else "The thesis's age is not in the record"
    if c11.get("result") == PASSED:
        sentence = f"{age} and the contract's price has not moved by more than its slippage."
    else:
        why = fresh.get("reason") or "the selected legs have no fresh quote"
        sentence = f"{age}. Whether the contract's price has moved since selection could not be checked: {why}."
    headline = "No blocking conditions." + (f" {_n(items, 'item')} for your judgement." if items else "")
    return {"label": "Ready", "state": "ready_with_items" if items else "ready", "conditions": [], "items": items,
            "headline": headline, "sentence": sentence}


def readiness_step(state, ctx) -> dict:
    return readiness(state)


STEPS = {"checklists": checklists_step, "question": question_step, "passages": passages_step,
         "critic": critic_step, "critic_check": critic_check_step, "readiness": readiness_step}
