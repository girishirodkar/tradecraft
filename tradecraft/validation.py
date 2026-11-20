"""The validation check on a thesis draft. Deterministic code, run before the
user sees a draft (docs/on-demand-mode-design.md, "Validation check").

It runs in one place: as the Thesis agent's output check on the harness. A
draft that fails is returned once with the failed checks; if it fails again the
user is shown the draft with them.

`record` is what code knows when the Thesis agent runs:
  findings   {id: finding}   each with text, evidence_ids, bearing, grade,
                             primary_source, lead, family, analyst
  facts      {id: fact}      measured facts supplied to the agent (text, kind)
  evidence   {id: item}      the graded evidence store
  risk_flags [flag]
  horizon    {recommended_days, ...}
"""
from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation

from .agents import SEVERE_FLAGS, ThesisDraft
from .figures import ROWS

SOLID = {"moderate", "strong"}
SUPPORTS = {"bullish": "supports_bullish", "bearish": "supports_bearish"}
OPPOSITE = {"bullish": "supports_bearish", "bearish": "supports_bullish"}
_NOT_NUMBERS = re.compile(r"\b(10-K|10-Q|8-K|S&P 500|Form \d+)\b|\b[A-Z]+\d+\b", re.IGNORECASE)
_NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
# A price condition: "above" or "below" with a price beside it (a currency amount, or the words
# close, share price or stock price), or an unambiguous chart or price term. "Falls below consensus"
# is not one (operator ruling, 19 November 2026).
_SIDE = r"\b(above|below|under|over|through)\b"
_PRICE = r"(\$\s?\d|\b(close[sd]?|closing|share price|stock price)\b)"
_PRICE_LEVEL = re.compile(
    rf"({_SIDE}[^.;]{{0,25}}?{_PRICE}|{_PRICE}[^.;]{{0,25}}?{_SIDE}"
    r"|\bmoving average\b|\bsupport level\b|\bresistance level\b|\bstop[- ]loss\b"
    r"|\bshare price (falls|drops|declines|rises)\b|\bstock (falls|drops|declines|rises) \d)", re.IGNORECASE)
_PRICE_DERIVED = re.compile(
    r"\b(uptrend|downtrend|momentum|relative strength|moving average|support level|resistance|breakout|"
    r"overbought|oversold|chart pattern|technical(ly)? (strong|weak|picture|setup))\b", re.IGNORECASE)
ALWAYS_ALLOWED = {Decimal(d) for d, *_ in ROWS}          # the horizon lengths themselves


def numbers(text: str) -> set[Decimal]:
    out = set()
    for m in _NUMBER.finditer(_NOT_NUMBERS.sub(" ", text or "")):
        try:
            out.add(Decimal(m.group(0).replace(",", "")))
        except InvalidOperation:
            pass
    return out


def _is_fact(i: str) -> bool:
    return i.startswith("M")


def precedence(record: dict) -> dict:
    """The precedence rules, computed in code from the graded findings. Used to
    re-check the branch the agent selected, and shown in the reasoning view.

    A finding carries a direction only if it is one of the three bearing kinds
    ("lead"). Any one graded moderate or strong can start a view. Two such
    findings with opposite bearings are a conflict: no view. Primary source is
    one of the three grade checks and nothing more (operator decision, 18
    November 2026, replacing the earlier primary-source wording)."""
    f = record["findings"].values()
    lead = [x for x in f if x.get("lead") and x.get("grade") in SOLID]
    out = {}
    for view, bearing in SUPPORTS.items():
        out[view] = {"lead_support": [x["id"] for x in lead if x["bearing"] == bearing]}
    conflict = bool(out["bullish"]["lead_support"] and out["bearish"]["lead_support"])
    severe = [x["flag"] for x in record.get("risk_flags", []) if x["flag"] in SEVERE_FLAGS]
    for view in SUPPORTS:
        out[view]["meets"] = bool(out[view]["lead_support"]) and not conflict and not severe
    carrying = [x["id"] for x in f if x.get("lead")]
    reason = ("declined" if severe else "conflict" if conflict else
              None if any(out[v]["meets"] for v in SUPPORTS) else
              "nothing_carries_a_direction")       # only context, mixed or in-line results, or weak findings
    return {**out, "conflict": conflict, "severe_flags": severe, "carrying_a_direction": carrying,
            "no_view_reason": reason}


def check(draft: ThesisDraft, record: dict) -> list[str]:
    """Every failed check, as a plain sentence. An empty list means the draft passed."""
    findings, facts, evidence = record["findings"], record["facts"], record.get("evidence", {})
    errors: list[str] = []
    known = set(findings) | set(facts)

    # The three branches, and code's own reading of the precedence rules.
    views = sorted(b.view for b in draft.branches)
    if views != ["bearish", "bullish", "no_view"]:
        errors.append("Set out exactly three branches: bullish, bearish and no_view, one of each.")
    selected = [b for b in draft.branches if b.pruned_reason is None]
    if len(selected) != 1 or selected[0].view != draft.view:
        errors.append("Exactly one branch must be left unpruned, and it must be the view you selected; "
                      "every other branch needs a pruned_reason.")
    for b in draft.branches:
        bad = sorted({i for i in [*b.supporting, *b.opposing] if i not in findings})
        if bad:
            errors.append(f"The {b.view} branch cites ids that are not findings in the record: {', '.join(bad)}.")
    rules = precedence(record)

    if draft.view == "no_view":
        if not draft.no_view_kind or not (draft.no_view_reason or "").strip():
            errors.append("A no-view result needs no_view_kind and no_view_reason.")
        return errors

    view = draft.view
    if rules["severe_flags"]:
        errors.append(f"A severe risk flag was raised ({', '.join(rules['severe_flags'])}): "
                      "the result must be no_view, kind 'declined'.")
    if rules["conflict"]:
        errors.append("Findings graded moderate or strong carry both directions "
                      f"({', '.join(rules['bullish']['lead_support'])} against "
                      f"{', '.join(rules['bearish']['lead_support'])}): the result must be no_view.")
    lead_ok = [i for i in draft.supporting if i in rules[view]["lead_support"]]
    if not lead_ok:
        errors.append(f"A {view} view needs, under 'supporting', at least one finding that carries that direction, "
                      f"graded moderate or strong. Eligible: {', '.join(rules[view]['lead_support']) or 'none'}.")

    # Supporting and opposing evidence.
    bad = sorted({i for i in [*draft.supporting, *draft.opposing] if i not in findings})
    if bad:
        errors.append(f"'supporting' or 'opposing' cites ids that are not findings in the record: {', '.join(bad)}.")
    for i in draft.supporting:
        x = findings.get(i)
        if x is None:
            continue
        if x.get("description_only"):
            errors.append(f"{i} is price description and may not support a direction.")
        elif x["bearing"] != SUPPORTS[view]:
            errors.append(f"{i} is listed as supporting a {view} view but its bearing is '{x['bearing']}'.")
    missing = sorted(x["id"] for x in findings.values()
                     if x["bearing"] == OPPOSITE[view] and x.get("grade") in SOLID and x["id"] not in draft.opposing)
    if missing:
        errors.append(f"Opposing findings graded moderate or strong must be listed under 'opposing': {', '.join(missing)}.")

    # The screen text: cited, and every number traceable to what it cites.
    texts = []
    if draft.summary is None or draft.rationale is None:
        errors.append("A directional view needs a summary and the three parts of the rationale.")
    else:
        texts = [("summary", draft.summary), ("rationale.catalyst", draft.rationale.catalyst),
                 ("rationale.confirmation", draft.rationale.confirmation),
                 ("rationale.tempering", draft.rationale.tempering)]
    texts += [(f"horizon_reasons[{n}]", h) for n, h in enumerate(draft.horizon_reasons)]
    if not draft.horizon_reasons:
        errors.append("horizon_reasons is empty: explain the recommended horizon.")
    for name, t in texts:
        if not t.cites:
            errors.append(f"{name} cites nothing. Every sentence must rest on a finding or a measured fact.")
            continue
        unknown = sorted(i for i in t.cites if i not in known)
        if unknown:
            errors.append(f"{name} cites ids that are not in the record: {', '.join(unknown)}.")
        source = " ".join(_source_text(i, findings, facts, evidence) for i in t.cites if i in known)
        loose = sorted(numbers(t.text) - numbers(source) - ALWAYS_ALLOWED)
        if loose:
            errors.append(f"{name} contains numbers that are not in what it cites ({', '.join(str(n) for n in loose)}). "
                          "Use only numbers written in the cited findings or measured facts, or leave them out.")
        if name in ("summary", "rationale.catalyst", "rationale.confirmation"):
            m = _PRICE_DERIVED.search(t.text)
            if m:
                errors.append(f"{name} cites a price-derived measure ('{m.group(0)}') in support of the view. "
                              "Trend, momentum, relative strength and chart levels may not support a direction.")
            tech = [i for i in t.cites if findings.get(i, {}).get("description_only")]
            if tech:
                errors.append(f"{name} cites price description ({', '.join(tech)}) in support of the view.")

    # An earnings report inside the horizon must be flagged in the horizon reasons.
    for fid in record.get("horizon", {}).get("earnings_fact_ids_inside", []):
        if not any(fid in h.cites for h in draft.horizon_reasons):
            errors.append(f"An earnings report falls inside the recommended horizon ({fid}): "
                          "say so in horizon_reasons and cite it.")

    # Resolution rule and invalidation criteria.
    if not draft.resolution_criterion.strip():
        errors.append("resolution_criterion is missing.")
    covered = {f.finding_id for f in draft.falsifiers}
    uncovered = [i for i in draft.supporting if i in findings and i not in covered]
    if uncovered:
        errors.append(f"Each supporting finding needs an invalidation condition; none for: {', '.join(uncovered)}.")
    # These are the conditions the agent wrote. The fixed conditions written by code
    # (stage2.results_only_conditions) are added after this check and are exempt from it.
    for f in draft.falsifiers:
        if f.finding_id not in findings:
            errors.append(f"An invalidation condition names a finding that is not in the record: {f.finding_id}.")
        m = _PRICE_LEVEL.search(f.trigger)
        if m:
            errors.append(f"The invalidation condition for {f.finding_id} is a price condition ('{m.group(0).strip()}'). "
                          "Invalidation must be evidence-based: a price move does not falsify the view.")
    if draft.catalyst is None:
        errors.append("catalyst is missing: say whether the view depends on a dated event.")
    return errors


def _source_text(i: str, findings: dict, facts: dict, evidence: dict) -> str:
    if _is_fact(i) and i in facts:
        return facts[i]["text"]
    x = findings[i]
    body = " ".join(json.dumps(evidence[e].get("body"), default=str, ensure_ascii=False)
                    + " " + str(evidence[e].get("date") or "") for e in x.get("evidence_ids", []) if e in evidence)
    return f"{x['text']} {x.get('date') or ''} {body}"


def code_fields(draft: ThesisDraft, record: dict) -> dict:
    """What code adds to a draft: nothing here is the agent's to set."""
    findings = record["findings"]
    rules = precedence(record)
    if draft.view == "no_view":
        return {"precedence": rules, "no_view_reason_code": rules["no_view_reason"] or "agent_declined"}
    opposing_all = sorted(x["id"] for x in findings.values() if x["bearing"] == OPPOSITE[draft.view])
    solid_support = [findings[i] for i in draft.supporting if i in findings and findings[i].get("grade") in SOLID]
    families = sorted({x["family"] for x in solid_support if x.get("family")})
    # A view resting on the earnings result alone is marked weakly supported (decision, section 4).
    only_results = bool(solid_support) and all(x.get("kind") == "results_vs_estimates" for x in solid_support)
    return {
        "precedence": rules,
        "opposing_all": opposing_all,
        "contested": any(findings[i].get("grade") in SOLID for i in opposing_all),
        "evidence_families": families,
        "single_family": len(families) <= 1,
        "support": "weak" if only_results else "normal",
    }


def user_verdict(direction: str, chosen: list[str], findings: dict) -> dict:
    """How a thesis the user entered stands ("Take a view yourself", decision section 6).
    `chosen` are the ids of the findings relied on. A finding that carries the
    opposite direction stands against the thesis whether or not it was chosen."""
    relied = [{"evidence_id": i, "kind": "anchored" if findings[i]["bearing"] != "none" else "context"}
              for i in chosen if i in findings]
    matching = [i for i in chosen if i in findings and findings[i]["bearing"] == SUPPORTS[direction]]
    context = [r["evidence_id"] for r in relied if r["kind"] == "context"]
    against = sorted(x["id"] for x in findings.values() if x["bearing"] == OPPOSITE[direction])
    if not matching:
        verdict = "not_supported"
    elif context or against:
        verdict = "partly_supported"
    else:
        verdict = "well_supported"
    return {"verdict": verdict, "relied_on": relied, "matching": matching, "context_chosen": context,
            "opposing": against}
