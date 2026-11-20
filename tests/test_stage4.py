"""Stage 4: both checklists, the question, retrieval, the Critic and readiness.

No network and no model: the Retriever and the Critic run on a scripted model,
and the research index is a small fixed set of passages searched by keyword.
"""
import copy
import datetime as dt
import json
import re
import threading
import time

import pytest

from tradecraft import research, settings, stage4, testfail
from tradecraft.data import prices, session
from tradecraft.harness import ScriptedModel
from tradecraft.storage import now
from tradecraft.workflow import StepFailed, Workflow
from tradecraft.workflow.state import HIDDEN_FROM_SCREEN, StepContext

TODAY = now().date()


def day(n):
    return (TODAY + dt.timedelta(days=n)).isoformat()


EXP = day(32)
FAMILY = "fundamentals and expectations"


def finding(i, bearing="supports_bullish", grade="moderate", date=None, family=FAMILY, analyst="fundamental_analyst", **kw):
    return {"id": i, "text": kw.pop("text", f"Finding {i}."), "bearing": bearing, "grade": grade, "ungraded": False,
            "date": date or day(-10), "family": family, "analyst": analyst, "source": "test",
            "checks": {"primary_source": grade == "strong", "recent": True, "specific": True}, **kw}


def candidate(**kw):
    c = {"id": "hold", "name": "Bull put spread (credit), 95 / 100", "structure": "Bull put spread (credit)",
         "expiry": EXP, "dte": 32, "credit": True, "net_price": -170.0, "max_loss": 330.0, "max_gain": 170.0,
         "break_even": [98.3], "pays_when_view_right": {"pct": 100.0, "basis": "blended"},
         "base_rate_profit": {"pct": 62.0, "uncertainty_pts": 3.0}, "implied_profit": {"pct": 60.0},
         "cost": {"dollars": 6.0, "pct_of_risk": 1.8},
         "payoff_at_one_move": {"per_dollar_at_risk": 0.52},
         "checks": {"has_short_leg": True, "short_leg_in_the_money": False,
                    "ex_dividend_before_expiration_short_leg": False},
         "legs": [{"action": "sell", "type": "put", "strike": 100.0, "occ": "A", "open_interest": 500},
                  {"action": "buy", "type": "put", "strike": 95.0, "occ": "B", "open_interest": 800}]}
    c.update(kw)
    return c


def make_state(**kw):
    findings = {"F1": finding("F1", text="EPS $2.05 against $1.99 expected. Results above estimates."),
                "F2": finding("F2", grade="strong", text="Clearly, full-year EPS guidance was raised to $4.10 to $4.30."),
                "F3": finding("F3", bearing="none", text="Free cash flow fell year over year."),
                "R1": finding("R1", bearing="none", analyst="regime_assessor", family="sector and macro",
                              text="The sector fund rose 2% over one month.")}
    cand = candidate()
    other = candidate(id="single", name="Long call, 100", structure="Long call", credit=False,
                      cost={"dollars": 4.0, "pct_of_risk": 1.1}, pays_when_view_right={"pct": 63.0})
    state = {
        "request_id": "req_s4", "symbol": "NVDA", "view": "bullish",
        "gate": {"status": "pass", "provisional": False}, "gate_decision": {"action": "continue"},
        "figures": {"events": [{"kind": "fomc", "label": "FOMC decision", "date": day(22)},
                               {"kind": "earnings", "label": "earnings report", "date": day(60)},
                               {"kind": "data_release", "label": "Consumer Price Index", "date": day(12)}],
                    "measured": {"reference_close": 100.0, "reference_date": day(-1),
                                 "volatility": {"state": "normal", "ratio": 1.0},
                                 "horizons": [{"days": 30, "base_rate_pct": 56.0, "base_rate_basis": "blended",
                                               "base_rate_uncertainty_pts": 3.0, "typical_move_pct": 5.0}]}},
        "findings": {"fundamental_analyst": {"status": "ok"}, "regime_assessor": {"status": "ok"}},
        "thesis": {"view": "bullish", "basis": "I am certain the raise settles it. THE-ORIGINAL-WORDING.",
                   "supporting": ["F1", "F2"], "opposing": [], "findings": findings, "primary_horizon_days": 30,
                   "recommended_horizon_days": 30, "catalyst": {"dated": False, "date": None}, "risk_flags": [],
                   "inputs_unavailable": ["estimate revision history (no source)"],
                   "falsifiers": [{"finding_id": "F1", "type": "earnings_result", "trigger": "The next result misses"},
                                  {"finding_id": "F2", "type": "guidance_change", "trigger": "Guidance is cut"}]},
        "thesis_decision": {"action": "accept", "at": time.time()},
        "contracts": {"spot": 100.0, "as_of": "now", "provisional": False, "typical_move_pct": 5.2,
                      "implied_move_pct": 5.5, "filters": {"cost_cap_pct": 5.0}, "candidates": [cand, other],
                      "expiry_options": [{"expiration": EXP, "dte": 32, "serves_days": 30, "poor_match": False}],
                      "events": {"earnings": {"date": day(60)}, "ex_dividend": {"date": None, "status": "none declared"}}},
        "selection": {"id": "hold", "candidate": cand, "best_fit_id": "hold", "priority": "match",
                      "contracts_proposed": 1, "horizon_amendment": None},
    }
    state.update(kw)
    return state


def user_state(direction="bullish", relied=("F1", "F3"), verdict="partly_supported"):
    s = make_state(view=direction)
    s["thesis"] = {**s["thesis"], "no_view": True, "supporting": [], "falsifiers": []}
    s["user_thesis"] = {"thesis_origin": "user", "view": direction, "primary_horizon_days": 30,
                        "recommended_horizon_days": 30, "verdict": verdict, "opposing": [],
                        "relied_on": [{"evidence_id": i, "kind": "context" if i in ("F3", "R1") else "anchored"}
                                      for i in relied],
                        "falsifiers": [{"type": "guidance_change", "trigger": "Guidance is changed against the view",
                                        "finding_id": None}],
                        "entered_after_no_view": {"kind": "nothing_found", "reason_code": "conflict"}}
    return s


FRESH = {"market_open": True, "spot": 100.5, "as_of": "t", "legs": {"A": 3.0, "B": 1.3}, "reason": None}
CLOSED = {"market_open": False, "spot": None, "as_of": None, "legs": None, "reason": "the market is closed"}


def run(state, fresh=FRESH, vol=None, records=()):
    out = stage4.run_checklists(stage4.Case(state), fresh, vol, list(records))
    return {x["id"]: x for x in out["thesis"] + out["contract"]}, out


def res(state, cid, **kw):
    return run(state, **kw)[0][cid]


# ---- the two checklists -------------------------------------------------------------------

def test_twenty_three_checks_each_with_one_of_four_results():
    by, out = run(make_state())
    assert [x["id"] for x in out["thesis"]] == [f"T{i}" for i in range(1, 13)]
    assert [x["id"] for x in out["contract"]] == [f"C{i}" for i in range(1, 12)]
    assert {x["result"] for x in by.values()} <= {"passed", "flagged", "not_applicable", "not_checked"}
    assert all(x["detail"] and x["name"] for x in by.values())


def test_no_check_passes_for_want_of_data():
    s = make_state()
    s["figures"] = {"events": [], "measured": {"horizons": [], "volatility": {"state": None}}}
    s["contracts"] = {"candidates": [], "events": {"ex_dividend": {"status": "not available"}}}
    for k in ("pays_when_view_right", "base_rate_profit", "implied_profit", "cost"):
        s["selection"]["candidate"][k] = {}
    s["selection"]["candidate"]["legs"][0]["open_interest"] = None
    by, _ = run(s, fresh=CLOSED)
    for cid in ("T5", "T11", "T12", "C1", "C2", "C3", "C4", "C5", "C6", "C8", "C9", "C11"):
        assert by[cid]["result"] == "not_checked", cid
    assert by["T6"]["result"] == "not_checked"                       # no date served, no calendar read


def test_t1_reads_the_basis_and_the_cited_findings_only():
    s = make_state()
    assert res(s, "T1")["result"] == "passed"
    s["thesis"]["findings"]["F1"]["text"] = "The stock broke out above its 50-day moving average."
    t1 = res(s, "T1")
    assert t1["result"] == "flagged" and t1["data"]["matches"][0]["where"] == "finding F1"
    s = make_state()
    s["thesis"]["findings"]["F3"]["text"] = "Momentum is strong."          # context, not cited: not read
    assert res(s, "T1")["result"] == "passed"


def test_the_two_tightened_patterns_no_longer_match_ordinary_wording():
    pats = [p for g in settings.load_json("rejected_signals.json")["signals"] for p in g["patterns"]]
    hit = lambda t: any(re.search(p, t, re.I) for p in pats)   # noqa: E731
    assert not hit("Bearish over 30 days, because results came in below estimates.")
    assert not hit("Revenue was $67.80B against $61.82B expected.")
    assert hit("SPY closed below its 200-day average.") and hit("a 61.8% retracement")


def test_t2_same_family_same_day_counts_once_and_no_support_is_flagged():
    t2 = res(make_state(), "T2")
    assert t2["result"] == "flagged" and t2["data"]["kind"] == "single_finding"
    s = make_state()
    s["thesis"]["findings"]["F2"]["date"] = day(-3)
    assert res(s, "T2")["data"]["kind"] == "single_family"
    s["thesis"]["findings"]["F2"]["family"] = "news and events"
    assert res(s, "T2")["result"] == "passed"
    u = user_state(relied=("F3",))
    assert res(u, "T2")["data"]["kind"] == "none" and res(u, "T3")["result"] == "flagged"


def test_t3_moderate_at_best_and_weak_cited():
    assert res(make_state(), "T3")["result"] == "passed"
    s = make_state()
    s["thesis"]["supporting"] = ["F1"]
    t3 = res(s, "T3")
    assert t3["result"] == "flagged" and t3["data"]["kind"] == ["moderate_at_best"]
    assert t3["data"]["findings"]["F1"]["tests_failed"] == ["primary source"]


def test_t4_opposition_is_any_finding_carrying_the_other_direction():
    assert res(make_state(), "T4")["result"] == "passed"
    s = make_state()
    s["thesis"]["findings"]["F9"] = finding("F9", bearing="supports_bearish", grade="weak")
    t4 = res(s, "T4")
    assert t4["result"] == "passed" and t4["note"]
    s["thesis"]["findings"]["F9"]["grade"] = "strong"
    assert res(s, "T4")["result"] == "flagged"
    s = make_state()
    del s["thesis"]["findings"]["R1"]
    assert res(s, "T4")["result"] == "not_checked"


def test_t5_plain_threshold_at_fifty_and_the_horizon_in_force():
    assert res(make_state(), "T5")["result"] == "passed"
    s = make_state(view="bearish")
    t5 = res(s, "T5")
    assert t5["result"] == "flagged" and t5["data"]["rate_pct"] == 44.0
    s = make_state()
    s["selection"]["horizon_amendment"] = {"from_days": 30, "to_days": 60, "expiration": EXP}
    assert res(s, "T5")["result"] == "not_checked"                  # no 60-day row in this record


def test_t6_window_runs_to_the_expiration_and_lines_keep_their_own_result():
    t6 = res(make_state(), "T6")
    lines = {l["name"]: l["result"] for l in t6["lines"]}
    assert t6["result"] == "flagged" and "day 22" in t6["detail"]
    assert lines == {"Earnings date": "passed", "Dated ruling or vote": "passed", "FOMC decision": "flagged",
                     "Inflation and employment releases": "not_applicable", "Heavy earnings period": "not_applicable",
                     "Dated catalyst": "not_applicable"}
    s = make_state()
    s["figures"]["events"][1]["date"] = day(20)                      # earnings before the expiration
    assert {l["name"]: l["result"] for l in res(s, "T6")["lines"]}["Earnings date"] == "flagged"
    s["figures"]["events"] = [e for e in s["figures"]["events"] if e["kind"] != "earnings"]
    assert {l["name"]: l["result"] for l in res(s, "T6")["lines"]}["Earnings date"] == "not_checked"
    s = make_state()
    s["thesis"]["catalyst"] = {"dated": True, "date": day(40)}       # after the expiration
    assert {l["name"]: l["result"] for l in res(s, "T6")["lines"]}["Dated catalyst"] == "flagged"


def test_t6_index_lines():
    s = make_state(symbol="SPY")
    s["figures"]["events"] = [{"kind": "data_release", "label": "Consumer Price Index", "date": day(12)}]
    lines = {l["name"]: l["result"] for l in res(s, "T6")["lines"]}
    assert lines["Earnings date"] == "not_applicable" and lines["Heavy earnings period"] == "not_checked"
    assert lines["Inflation and employment releases"] == "flagged"
    s["figures"]["events"][0]["label"] = "Gross Domestic Product"    # listed dates end before the expiration
    assert {l["name"]: l["result"] for l in res(s, "T6")["lines"]}["Inflation and employment releases"] == "not_checked"


def test_t7_flags_a_note_and_a_severe_flag_overridden():
    assert res(make_state(), "T7")["result"] == "passed"
    s = make_state()
    s["thesis"]["risk_flags"] = [{"flag": "sector_wide_move"}]
    assert res(s, "T7")["note"] and res(s, "T7")["result"] == "passed"
    s["thesis"]["risk_flags"].append({"flag": "dilution"})
    assert res(s, "T7")["result"] == "flagged"
    u = user_state()
    u["thesis"]["risk_flags"] = [{"flag": "going_concern_or_liquidity_warning"}]
    assert res(u, "T7")["data"]["severe_overridden"] is True


def test_t8_stays_flagged_while_nothing_monitors_and_maps_each_type():
    t8 = res(make_state(), "T8")
    assert t8["result"] == "flagged" and t8["data"]["kind"] == ["not_monitored"]
    s = make_state()
    s["thesis"]["falsifiers"] = [{"finding_id": "F1", "type": "estimate_revision", "trigger": "x"}]
    t8 = res(s, "T8")
    assert set(t8["data"]["kind"]) == {"cannot_be_monitored", "no_condition", "not_monitored"}
    assert t8["data"]["findings_without_a_condition"] == ["F2"]
    assert "no_condition" not in res(user_state(), "T8")["data"]["kind"]     # left out for a user thesis


def test_t9_origin_and_the_verdict_for_a_thesis_the_user_entered():
    assert res(make_state(), "T9")["result"] == "passed"
    t9 = res(user_state(), "T9")
    assert t9["result"] == "flagged" and t9["data"]["kind"] == ["entered_after_no_view", "not_fully_supported"]
    assert t9["data"]["counts"] == {"carrying_the_direction": 1, "context": 1, "standing_against": 0}
    assert res(user_state(relied=("F1",), verdict="well_supported"), "T9")["data"]["kind"] == ["entered_after_no_view"]


def test_t10_overrides_provisional_data_and_missing_inputs_as_a_note():
    t10 = res(make_state(), "T10")
    assert t10["result"] == "passed" and t10["note"] and t10["data"]["inputs_unavailable"]
    s = make_state(gate_decision={"action": "override", "rationale": "thin name"})
    s["selection"]["horizon_amendment"] = {"from_days": 30, "to_days": 30, "expiration": EXP}
    s["contracts"]["provisional"] = True
    rec = [{"decision": "update", "payload": {"changed": {"max_loss": {"from": 300.0, "to": 500.0}}}}]
    whats = [i["what"] for i in res(s, "T10", records=rec)["data"]["items"]]
    assert whats == ["Liquidity gate overridden", "Horizon amended by switching expiration",
                     "Max loss raised after the candidates were shown", "Provisional data"]


def test_t11_move_in_typical_moves_stale_and_no_price():
    assert res(make_state(), "T11")["result"] == "passed"
    t = res(make_state(), "T11", fresh={**FRESH, "spot": 103.0})
    assert t["result"] == "flagged" and t["data"]["kind"] == "moved_with" and t["data"]["typical_moves"] == 0.6
    assert res(make_state(view="bearish"), "T11", fresh={**FRESH, "spot": 103.0})["data"]["kind"] == "moved_against"
    assert res(make_state(), "T11", fresh=CLOSED)["result"] == "not_checked"
    old = make_state(thesis_decision={"at": time.time() - 9 * 86400})
    assert res(old, "T11")["data"]["kind"] == "stale"


def test_t12_and_c2_read_the_volatility_state():
    by, _ = run(make_state(), vol={"state": "active", "ratio": 1.4})
    assert by["T12"]["result"] == "flagged" and by["C2"]["result"] == "flagged"     # active and short premium
    by, _ = run(make_state(), vol={"state": "quiet", "ratio": 0.7})
    assert by["T12"]["result"] == "passed" and by["T12"]["note"] and by["C2"]["result"] == "passed"
    s = make_state(view="range_bound")
    assert res(s, "T12", vol={"state": "active", "ratio": 1.4})["data"]["kind"] == "invalidation_met"


def test_contract_checks():
    by, _ = run(make_state())
    assert by["C1"]["result"] == "passed" and by["C7"]["result"] == "flagged" and by["C10"]["result"] == "passed"
    assert by["C3"]["result"] == by["C4"]["result"] == by["C5"]["result"] == by["C6"]["result"] == "passed"
    assert by["C8"]["result"] == "passed" and by["C9"]["result"] == "passed"
    s = make_state()
    c = s["selection"]["candidate"]
    c.update({"pays_when_view_right": {"pct": 71.0}, "base_rate_profit": {"pct": 55.0, "uncertainty_pts": 3.0},
              "cost": {"dollars": 14.0, "pct_of_risk": 4.2}})
    c["checks"]["short_leg_in_the_money"] = True
    s["contracts"].update({"implied_move_pct": 7.0})
    s["contracts"]["expiry_options"][0]["poor_match"] = True
    s["selection"].update({"best_fit_id": "single", "contracts_proposed": 60})
    by, _ = run(s)
    for cid in ("C1", "C3", "C4", "C5", "C6", "C8", "C9", "C10"):
        assert by[cid]["result"] == "flagged", cid
    assert by["C6"]["data"]["flag_at_pct"] == 4.0


def test_c6_uses_the_cost_cap_in_force():
    s = make_state()
    s["selection"]["candidate"]["cost"] = {"dollars": 14.0, "pct_of_risk": 4.2}
    s["contracts"]["filters"]["cost_cap_pct"] = 10.0
    assert res(s, "C6")["result"] == "passed"


def test_c8_european_no_short_leg_and_no_dividend_date():
    assert res(make_state(symbol="SPX"), "C8")["result"] == "not_applicable"
    s = make_state()
    s["selection"]["candidate"]["checks"]["has_short_leg"] = False
    assert res(s, "C8")["result"] == "not_applicable"
    s = make_state()
    s["contracts"]["events"]["ex_dividend"] = {"date": None, "status": "not available"}
    assert res(s, "C8")["result"] == "not_checked"


def test_c11_compares_the_fresh_net_price_with_the_selection():
    assert res(make_state(), "C11")["result"] == "passed"                   # 3.00 - 1.30 = 1.70, unchanged
    c11 = res(make_state(), "C11", fresh={**FRESH, "legs": {"A": 3.4, "B": 1.3}})
    assert c11["result"] == "flagged" and c11["data"]["moved_dollars"] == 40.0
    assert res(make_state(), "C11", fresh=CLOSED)["result"] == "not_checked"
    assert res(make_state(), "C11", fresh={**FRESH, "legs": {"A": 3.0}})["result"] == "not_checked"


def test_fresh_quotes_never_stop_the_stage(store, monkeypatch):
    ctx = StepContext(store=store, request_id="r", cancel=threading.Event(), deadline=float("inf"))
    monkeypatch.setattr(session, "status", lambda when=None: {"open": False})
    assert stage4.fresh_quotes(make_state(), ctx)["reason"] == "the market is closed"
    monkeypatch.setattr(session, "status", lambda when=None: {"open": True})
    from tradecraft.data import chain

    def down(symbol, store=None):
        raise chain.ChainUnavailable("down")
    monkeypatch.setattr(chain, "live", down)
    assert "could not be retrieved" in stage4.fresh_quotes(make_state(), ctx)["reason"]
    monkeypatch.setattr(chain, "live", lambda symbol, store=None: {"spot": 101.0, "as_of": "t", "contracts": [
        {"occ": "A", "bid": 2.9, "ask": 3.1}, {"occ": "B", "bid": 0.0, "ask": 1.4}, {"occ": "Z", "bid": 1, "ask": 2}]})
    f = stage4.fresh_quotes(make_state(), ctx)
    assert f["spot"] == 101.0 and f["legs"] == {"A": 3.0}                    # B has no two-sided quote


# ---- the question --------------------------------------------------------------------------

def test_the_question_is_a_fixed_template_without_the_wording_or_the_author():
    q = stage4.restate(stage4.Case(make_state()))
    assert q["question"] == "Do the following support a close above the reference price for NVDA at 30 days?"
    assert [c["evidence_id"] for c in q["claims"]] == ["F1", "F2"]
    assert q["claims"][1]["text"].startswith("Full-year EPS guidance")       # "Clearly," is stripped
    u = stage4.restate(stage4.Case(user_state(direction="bearish")))
    assert "below the reference price" in u["question"] and [c["evidence_id"] for c in u["claims"]] == ["F1", "F3"]
    assert "user" not in json.dumps(u).lower() and "your" not in json.dumps(u).lower()


# ---- the research index and retrieval ---------------------------------------------------------

DOC = """# Research Strand 99

## 1. Earnings

**CLAIM:** Stocks drift higher after earnings beat estimates.
**EVIDENCE STRENGTH:** Strong (for the historical effect)
**Numbers:** Post-earnings announcement drift was large before 2005 across many stocks and decades of data.

**CLAIM:** The drift after earnings beats has disappeared in liquid stocks.
**EVIDENCE STRENGTH:** Moderate
**Numbers:** In liquid names after 2005 the earnings drift is near zero and is already priced within days.

## 2. Premium selling

Selling option premium on single stocks earned no return after trading costs in the sample studied here at all.
"""


def fixed_index():
    passages = [{**p, "id": f"R99-{i:03d}"} for i, p in enumerate(research.split_document("research-99-x.md", DOC), 1)]
    return research.KeywordIndex(passages)


def test_passages_keep_source_section_and_the_reports_own_grade():
    ps = research.split_document("research-99-x.md", DOC)
    assert [p["grade"] for p in ps] == ["Strong (for the historical effect)", "Moderate", "ungraded"]
    assert ps[0]["section"] == "1. Earnings" and ps[2]["section"] == "2. Premium selling"
    assert all(p["source"] == "research-99-x.md" for p in ps)


def ctx_for(store, replies, index="fixed"):
    extras = {"model": ScriptedModel(replies)}
    if index is not None:
        extras["research_index"] = fixed_index() if index == "fixed" else index
    return StepContext(store=store, request_id="req_s4", cancel=threading.Event(), deadline=float("inf"), extras=extras)


def search(topic, a, b):
    return {"name": "search_research", "input": {"topic_id": topic, "supports_query": a, "opposes_query": b}}


def staged(**kw):
    s = make_state(**kw)
    by, lists = run(s)
    s["checklists"] = lists
    s["question"] = stage4.restate(stage4.Case(s))
    return s


def test_retrieval_searches_each_topic_both_ways_and_keeps_what_the_agent_sorted(store, monkeypatch):
    monkeypatch.setattr(research, "config", lambda: {**settings.load_json("stage4.json")["retrieval"],
                                                     "relevance_bar": {"keyword": 0.3, "chromadb": 0.45}})
    answer = {"topics": [{"topic_id": "TP1", "supporting": ["R99-001"], "opposing": ["R99-002"]},
                         {"topic_id": "TP2", "supporting": [], "opposing": []},
                         {"topic_id": "TPS", "supporting": [], "opposing": ["R99-003"]}]}
    ctx = ctx_for(store, [
        {"tool_uses": [search("TP1", "stocks drift higher after earnings beat estimates", "earnings drift disappeared liquid stocks priced"),
                       search("TP2", "zzz qqq", "xxx yyy"),
                       search("TPS", "selling option premium earns return", "selling option premium no return after trading costs")]},
        {"tool_uses": [search("TP2", "www vvv", "uuu ttt")]},
        {"text": json.dumps(answer)}])
    out = stage4.passages_step(staged(), ctx)
    t = {x["id"]: x for x in out["topics"]}
    assert out["method"] == "keyword" and out["retrieved"]
    assert t["TP1"]["for"] == ["P1"] and t["TP1"]["against"] == ["P2"] and t["TPS"]["against"] == ["P3"]
    assert t["TP2"]["nothing_found"] and len(t["TP2"]["searches"]) == 2          # reworded once, then nothing found
    p1 = out["passages"]["P1"]
    assert p1["source"] == "research-99-x.md" and p1["section"] == "1. Earnings" and p1["grade"].startswith("Strong")


def test_retriever_may_cite_only_passages_a_search_returned(store):
    bad = {"topics": [{"topic_id": "TP1", "supporting": ["R99-777"], "opposing": []}]}
    ctx = ctx_for(store, [{"text": json.dumps(bad)}, {"text": json.dumps(bad)}])
    out = stage4.passages_step(staged(), ctx)
    assert not out["retrieved"] and "did not finish" in out["reason"]             # the Critic runs without passages
    assert all(t["nothing_found"] for t in out["topics"])


def test_a_third_search_of_one_topic_is_refused():
    seen, log = {}, {}
    tool = stage4.search_tool(fixed_index(), seen, log, ["TP1"])
    for _ in range(2):
        tool.fn(None, topic_id="TP1", supports_query="zzz", opposes_query="yyy")
    assert "refused" in tool.fn(None, topic_id="TP1", supports_query="earnings", opposes_query="earnings")
    assert "error" in tool.fn(None, topic_id="TP9", supports_query="a", opposes_query="b")


def test_no_index_means_no_passages_and_says_so(store, monkeypatch):
    monkeypatch.setattr(research, "open_index", lambda: (None, "the research index is not available"))
    out = stage4.passages_step(staged(), ctx_for(store, [], index=None))
    assert out["method"] == "none" and not out["retrieved"] and out["passages"] == {}


# ---- the Critic ------------------------------------------------------------------------------

def critique(**kw):
    c = {"depends_on": {"claim_id": "CL2", "why": "Without the raise only the result is left."},
         "case_for": "Guidance was raised and the quarter beat estimates.",
         "case_against": "Both supports come from one report and an FOMC decision falls inside the window.",
         "priced_in": [{"claim_id": "CL2", "reading": "No figure was given."}],
         "loss_paths": [{"title": "A close below the breakeven", "text": "The spread loses below 98.30.", "grounds": ["C7"]},
                        {"title": "The FOMC decision", "text": "A market-wide move.", "grounds": ["T6"]}],
         "missing": [{"ref": "U1", "why_it_matters": "Revisions would show whether estimates followed."}],
         "dispositions": [{"claim_id": "CL1", "standing": "holds", "reason": "As recorded."},
                          {"claim_id": "CL2", "standing": "holds_in_a_narrower_form", "reason": "One report."}],
         "objections": [{"title": "One catalyst", "text": "Both findings are one report.", "grounds": ["T2", "CL1", "CL2"]}]}
    c.update(kw)
    return c


@pytest.fixture
def no_prices(monkeypatch):
    def down(*a, **k):
        raise prices.PricesUnavailable("test")
    monkeypatch.setattr(prices, "closes", down)


def known_for(state):
    return stage4.critic_brief(stage4.Case(state), state, stage4.priced_in_figures(
        stage4.Case(state), state["question"], None))[1]["known"]


def test_the_critic_is_not_shown_the_wording_the_basis_or_the_author(no_prices):
    s = staged()
    s["passages"] = stage4.no_passages("test")
    task, extra = stage4.critic_brief(stage4.Case(s), s, stage4.priced_in_figures(stage4.Case(s), s["question"], None))
    assert "THE-ORIGINAL-WORDING" not in task and "Origin and edits" not in task and '"T9"' not in task
    assert "T9" not in extra["known"]["checks"] and "T8" in extra["known"]["checks"]
    assert "No research passages were retrieved" in task
    u = user_state()
    u["checklists"] = run(u)[1]
    u["question"] = stage4.restate(stage4.Case(u))
    u["passages"] = stage4.no_passages("test")
    task, _ = stage4.critic_brief(stage4.Case(u), u, stage4.priced_in_figures(stage4.Case(u), u["question"], None))
    assert "entered after no view" not in task.lower() and "your thesis" not in task.lower()


@pytest.mark.parametrize("change,rule", [
    ({"dispositions": [{"claim_id": "CL1", "standing": "holds", "reason": "x"}]}, "Every claim needs a standing"),
    ({"case_against": ""}, "The case against is missing"),
    ({"case_for": "word " * 91}, "the limit is 90"),
    ({"objections": [{"title": "t", "text": "x", "grounds": ["T2"]}] * 6}, "At most 5 objections"),
    ({"objections": [{"title": "t", "text": "x", "grounds": []}]}, "cites no grounds"),
    ({"objections": [{"title": "t", "text": "x", "grounds": ["T9"]}]}, "grounds that do not exist"),
    ({"objections": [{"title": "t", "text": "x", "grounds": ["P7"]}]}, "grounds that do not exist"),
    ({"loss_paths": [{"title": "a", "text": "b", "grounds": ["C7"]}]}, "Give 2 or 3 ways"),
    ({"missing": [{"ref": "U9", "why_it_matters": "x"}]}, "only inputs recorded as unavailable"),
    ({"depends_on": {"claim_id": "CL7", "why": "x"}}, "claim ids do not exist"),
])
def test_output_check_rules(change, rule, no_prices):
    s = staged()
    s["passages"] = stage4.no_passages("test")
    errors = stage4.output_check(stage4.Critique(**critique(**change)), known_for(s))
    assert any(rule in e for e in errors), errors
    assert stage4.output_check(stage4.Critique(**critique()), known_for(s)) == []


@pytest.mark.parametrize("text", ["On balance, the trade is attractive.", "You should wait for a pullback.",
                                  "I would recommend a smaller size.", "Confidence: 7/10.", "My verdict is mixed."])
def test_no_verdict_score_or_advice(text):
    assert stage4.no_verdict(stage4.Critique(**critique(case_for=text)))
    assert stage4.no_verdict(stage4.Critique(**critique())) == []
    quoting = critique(case_against="That has happened in 38% of past 32-day periods.")
    assert stage4.no_verdict(stage4.Critique(**quoting)) == []


def critic_ctx(store, replies):
    return ctx_for(store, replies)


def with_passages():
    s = staged()
    s["passages"] = stage4.no_passages("test")
    return s


def test_critic_passes_and_records_its_model_and_the_standing_counts(store, no_prices):
    out = stage4.critic_step(with_passages(), critic_ctx(store, [{"text": json.dumps(critique())}]))
    assert out["check"] == {"ok": True, "failed_checks": [], "returned_once": False, "in_harness": True}
    assert out["model"] == "claude-opus-5-5" and out["same_family_as_thesis_agent"] is True
    assert out["standing_counts"] == {"holds": 1, "holds_in_a_narrower_form": 1, "does_not_hold": 0}
    assert out["priced_in_figures"]["CL1"]["pct"] is None                     # no price history: no figure, no guess


def test_critic_is_returned_once_in_total_then_rejected(store, no_prices):
    bad = critique(case_against="")
    model_replies = [{"text": json.dumps(bad)}, {"text": json.dumps(bad)}, {"text": json.dumps(critique())}]
    ctx = critic_ctx(store, model_replies)
    out = stage4.critic_step(with_passages(), ctx)
    assert out["rejected"] and out["check"]["ok"] is False and out["check"]["in_harness"]
    assert "The case against is missing." in out["check"]["failed_checks"]
    assert len(ctx.extras["model"].requests) == 2                              # one return, never a second
    good = critic_ctx(store, [{"text": json.dumps(bad)}, {"text": json.dumps(critique())}])
    assert stage4.critic_step(with_passages(), good)["check"] == {
        "ok": True, "failed_checks": [], "returned_once": True, "in_harness": True}


def test_an_unreadable_answer_twice_stops_the_stage_and_is_not_a_rejection(store, no_prices):
    with pytest.raises(StepFailed) as e:
        stage4.critic_step(with_passages(), critic_ctx(store, [{"text": "not json"}, {"text": "still not"}]))
    assert e.value.cause == "agent_failed" and e.value.agent == "critic"


def test_the_critic_switch_is_off_and_fires_once(store, monkeypatch, no_prices):
    assert testfail.read()["critic_fail_once"] is False and testfail.active() == []
    monkeypatch.setattr(testfail, "read", lambda: {"critic_fail_once": True})
    testfail._used.clear()
    ctx = critic_ctx(store, [{"text": json.dumps(critique())}])
    with pytest.raises(StepFailed) as e:
        stage4.critic_step(with_passages(), ctx)
    assert "critic_fail_once" in e.value.message and testfail.active() == ["critic_fail_once"]
    assert stage4.critic_step(with_passages(), ctx)["check"]["ok"]            # the retry runs the Critic


# ---- readiness ---------------------------------------------------------------------------------

def ready(state, **kw):
    state["checklists"] = run(state, **kw)[1]
    return stage4.readiness(state)


def test_readiness_is_set_by_code_from_validity_not_from_the_number_of_flags():
    r = ready(make_state())
    assert r["label"] == "Ready" and r["state"] == "ready_with_items" and r["items"] == 4
    assert r["headline"] == "No blocking conditions. 4 items for your judgement."
    assert r["sentence"] == ("The thesis is from this session and the contract's price has not moved by more than "
                             "its slippage.")
    r = ready(make_state(), fresh=CLOSED)
    assert r["label"] == "Ready" and "could not be checked: the market is closed" in r["sentence"]
    r = ready(make_state(), fresh={**FRESH, "legs": {"A": 3.4, "B": 1.3}})
    assert r["label"] == "Not ready" and r["conditions"][0]["check"] == "C11"
    assert "Return to contracts" in r["sentence"] and r["headline"] == "1 blocking condition."
    r = ready(make_state(thesis_decision={"at": time.time() - 9 * 86400}))
    assert r["label"] == "Not ready" and "Start a new analysis to redraft the thesis." in r["sentence"]
    s = make_state(critic_unavailable={"kind": "rejected", "reason": "The Critic's output was rejected by the output check: x."})
    assert ready(s)["label"] == "Not ready"


# ---- through the workflow ------------------------------------------------------------------------

def through(store, monkeypatch, replies, **extras):
    base = make_state()
    monkeypatch.setattr(session, "status", lambda when=None: {"open": False})

    def down(*a, **k):
        raise prices.PricesUnavailable("test")
    monkeypatch.setattr(prices, "closes", down)
    testfail._used.clear()
    steps = {**stage4.STEPS, "figures": lambda s, c: base["figures"], "thesis": lambda s, c: copy.deepcopy(base["thesis"]),
             "contracts": lambda s, c: {**copy.deepcopy(base["contracts"]), "outcome": "ok", "best_fit_id": "hold",
                                        "priority": "match", "expiry_chosen": EXP}}
    model = ScriptedModel(replies)
    w = Workflow(store, steps=steps, extras={"model": model, "research_index": fixed_index(), **extras})
    v = w.start("NVDA")
    rid = v["request_id"]
    w.resume(rid, "continue")
    w.resume(rid, "accept")
    return w, rid, w.resume(rid, "continue", selection={"id": "hold", "contracts": 1}), model


RETRIEVED = {"text": json.dumps({"topics": [{"topic_id": "TP1"}, {"topic_id": "TP2"}, {"topic_id": "TPS"}]})}


def test_stage_4_end_to_end_records_everything_the_design_lists(store, monkeypatch):
    w, rid, v, _ = through(store, monkeypatch, [RETRIEVED, {"text": json.dumps(critique())}])
    assert v["pause"]["pause"] == "challenge"
    s = v["state"]
    assert s["readiness"]["label"] == "Ready" and s["critic"]["objections"][0]["grounds"] == ["T2", "CL1", "CL2"]
    rec = [r for r in store.records(rid) if r["decision"] == "challenge"][0]["payload"]
    assert len(rec["checklists"]["thesis"]) == 12 and len(rec["checklists"]["contract"]) == 11
    assert rec["question"]["question"].startswith("Do the following support a close above")
    assert rec["passages"]["method"] == "keyword" and all(t["nothing_found"] for t in rec["passages"]["topics"])
    assert rec["critic_model"] == "claude-opus-5-5" and rec["critic_output_check"]["ok"] and rec["readiness"]["label"] == "Ready"
    assert [p["label"] for p in v["progress"]] == ["Evidence Retriever", "Critic", "Output check"]
    assert {p["status"] for p in v["progress"]} == {"done"}
    v = w.resume(rid, "proceed")
    last = [r for r in store.records(rid) if r["decision"] == "challenge_proceed"][0]
    assert v["done"] and last["payload"]["proceeded_past_not_ready"] is False


def test_a_rejected_critic_output_is_stored_never_shown_and_proceeding_is_marked(store, monkeypatch):
    bad = {"text": json.dumps(critique(objections=[{"title": "t", "text": "x", "grounds": []}]))}
    w, rid, v, model = through(store, monkeypatch, [RETRIEVED, bad, bad, {"text": json.dumps(critique())}])
    s = v["state"]
    assert v["pause"]["pause"] == "challenge" and s["critic"] is None and s["readiness"]["label"] == "Not ready"
    assert s["critic_unavailable"]["reason"] == ("The Critic's output was rejected by the output check: Objection 1 "
                                                 "cites no grounds.. It was returned once and failed again.") \
        or "Objection 1 cites no grounds" in s["critic_unavailable"]["reason"]
    assert len(model.requests) == 3                                           # retriever, critic, the one return
    assert "critic_rejected" in HIDDEN_FROM_SCREEN
    rec = [r for r in store.records(rid) if r["decision"] == "challenge"][0]["payload"]
    assert rec["critic_rejected"]["output"]["output"]["objections"][0]["grounds"] == []
    w.resume(rid, "proceed")
    last = [r for r in store.records(rid) if r["decision"] == "challenge_proceed"][0]
    assert last["payload"]["proceeded_past_not_ready"] is True


def test_a_critic_failure_stops_the_stage_and_checklists_only_is_not_ready(store, monkeypatch):
    w, rid, v, _ = through(store, monkeypatch, [RETRIEVED, {"text": "not json"}, {"text": "no"}])
    assert v["pause"]["pause"] == "stage4_stopped"
    assert v["pause"]["actions"] == ["retry", "checklists_only", "return", "stop"]
    v = w.resume(rid, "checklists_only")
    s = v["state"]
    assert v["pause"]["pause"] == "challenge" and s["critic"] is None and s["readiness"]["label"] == "Not ready"
    assert len(s["checklists"]["thesis"]) == 12 and "The Critic's output is not available" in s["readiness"]["sentence"]


def test_no_passages_and_the_critic_still_runs(store, monkeypatch):
    w, rid, v, model = through(store, monkeypatch, [{"text": json.dumps(critique())}], no_passages="replay: no passages")
    s = v["state"]
    assert v["pause"]["pause"] == "challenge" and s["passages"]["retrieved"] is False and s["critic"]["case_for"]
    assert "No research passages were retrieved" in model.requests[0]["messages"][0]["content"]


# ---- the index is brought up to date when the app starts ------------------------------------------

def test_ensure_current_rebuilds_a_stale_index_and_never_downloads_or_stops_the_app(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(research, "model_present", lambda: True)
    monkeypatch.setattr(research, "build", lambda: calls.append(1) or {"built": True, "passages": 3, "corpus": "x"})
    research._OPENED.update(index="old", note=None)
    out = research.ensure_current()
    assert out["built"] and out["method"] == "chromadb" and calls == [1] and research._OPENED == {}
    assert "Research index: rebuilt, chromadb, 3 passages." in capsys.readouterr().out
    monkeypatch.setattr(research, "model_present", lambda: False)        # a fresh clone: no download at start
    out = research.ensure_current()
    assert out["method"] == "keyword" and calls == [1] and "tradecraft.research build" in out["note"]

    def broken():
        raise RuntimeError("no disk")
    monkeypatch.setattr(research, "model_present", lambda: True)
    monkeypatch.setattr(research, "build", broken)
    assert research.ensure_current()["method"] == "keyword"


def test_creating_an_app_in_tests_does_not_build_the_index(monkeypatch):
    from tradecraft.web import app as web
    import inspect
    assert "ensure_current" not in inspect.getsource(web.create_app)


# ---- the recorded demo's bundle must hold no secret ------------------------------------------------

def test_the_bundle_scan_finds_a_secret_a_home_path_and_an_email(tmp_path, monkeypatch):
    import gzip
    from pathlib import Path
    from tradecraft import demo
    MAIL, HOME = "someone@" + "private-mail.org", "/Us" + "ers/somebody/project"   # not literal: the scan reads this file too
    monkeypatch.setattr(settings, "_env", lambda: {"FMP_API_KEY": "abc123secretvalue",
                                                   "SEC_USER_AGENT": "Some Name " + MAIL})
    (tmp_path / "ok.json").write_text('{"source": "SEC EDGAR", "contact": "webmaster@sec.gov"}')
    assert demo.scan(tmp_path) == []
    (tmp_path / "a.json").write_text('{"url": "https://x/?apikey=abc123secretvalue"}')
    with gzip.open(tmp_path / "b.csv.gz", "wt") as f:
        f.write("path\n" + HOME + "\n")
    (tmp_path / "c.md").write_text("Write to " + MAIL)
    found = " | ".join(demo.scan(tmp_path))
    assert "a.json: holds the value of FMP_API_KEY" in found and "b.csv.gz: holds a home-folder path" in found
    assert "c.md: holds the contact address from SEC_USER_AGENT" in found
    assert "abc123secretvalue" not in found and "someone@" not in found       # the values are never printed
