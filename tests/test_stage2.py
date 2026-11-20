"""Stage 2's agents, the validation check and the steps, on a scripted model. No network."""
import datetime as dt
import json
import threading

import pytest

from tradecraft import agents, context, evidence, settings, stage2, tools, validation
from tradecraft.harness import AgentResult, ScriptedModel, Tool, ToolRegistry, ToolUnavailable, run_agent
from tradecraft.storage import now
from tradecraft.workflow import StepFailed, Workflow
from tradecraft.workflow.state import StepContext
from conftest import guardrails, kinds

RID = "req_s2"
TODAY = now().date()


def side(low, high=None, measure="full-year EPS", period="fiscal 2026", basis="adjusted"):
    return {"measure": measure, "period": period, "basis": basis, "low": low, "high": high}


RAISED = {"now": side("$4.10", "$4.30"), "before": side("$3.90", "$4.10"), "compared_with": "earlier_guidance"}


def day(n):
    return (TODAY + dt.timedelta(days=n)).isoformat()


def reply(obj, **kw):
    return {"text": json.dumps(obj), **kw}


# ---- agent failures become stage stops, never a no-view --------------------------------

@pytest.mark.parametrize("status,message,cause,scope", [
    ("timed_out", "The Thesis agent timed out after 180 seconds.", "timed_out", None),
    ("spend_limit", "stopped: the daily spend limit of $10.00 has been reached.", "spend_limit", "day"),
    ("spend_limit", "stopped: the spend limit of $1.00 for this request has been reached.", "spend_limit", "request"),
    ("failed_validation", "failed validation", "agent_failed", None),
    ("model_error", "API error 500", "agent_failed", None),
    ("refused", "declined", "agent_failed", None),
])
def test_agent_status_maps_to_a_step_failure(status, message, cause, scope):
    with pytest.raises(StepFailed) as e:
        stage2.require_ok(AgentResult(status=status, agent="thesis", run_id="r", message=message))
    assert e.value.cause == cause and e.value.scope == scope and e.value.agent == "thesis"
    assert (e.value.resets_at is not None) == (scope == "day")


# ---- Evidence Retriever: the loop, one recovery, and ids that must exist ----------------

def test_retriever_recovers_from_a_failed_source_and_records_it_unavailable(store):
    reg = ToolRegistry()

    def estimates(ctx, symbol):
        raise ToolUnavailable("FMP analyst-estimates: HTTP 402")
    reg.register(Tool("get_analyst_estimates", "consensus", {"type": "object", "properties": {}}, estimates))
    reg.register(Tool("get_company_news", "news", {"type": "object", "properties": {}}, evidence.capturing(
        "get_company_news", lambda ctx, symbol: {"source": "FMP", "items": [
            {"published": day(-1), "publisher": "Wire", "title": "Results", "url": "u", "text": "t"}]})))
    for name in ("get_company_profile", "get_earnings", "get_dividends", "list_filings", "list_filing_sections",
                 "read_filing_section", "get_macro_calendar"):
        reg.register(Tool(name, name, {"type": "object", "properties": {}}, lambda ctx, **kw: {}))
    model = ScriptedModel([
        {"text": "Fetching the consensus and the news.", "tool_uses": [
            {"name": "get_analyst_estimates", "input": {"symbol": "NVDA"}},
            {"name": "get_company_news", "input": {"symbol": "NVDA"}}]},
        reply({"fetched": [{"what": "one news item", "evidence_ids": ["E1"]}],
               "unavailable": [{"input": "analyst consensus", "reason": "the source refused (HTTP 402)"}]})])
    cfg = agents.retriever(lambda: {i["id"] for i in store.evidence(RID)})
    r = run_agent(cfg, "Collect the evidence on NVDA.", model=model, registry=reg, store=store, request_id=RID)
    assert r.ok and r.tool_calls == 2
    assert r.unavailable_inputs[0]["tool"] == "get_analyst_estimates"            # recorded by the harness
    told = model.requests[1]["messages"][-1]["content"][0]["content"]
    assert "Not available" in told and "continue" in told                        # the agent is told to carry on
    assert r.output.unavailable[0].input == "analyst consensus"


def test_retriever_may_not_list_an_evidence_id_that_was_never_stored(store):
    model = ScriptedModel([reply({"fetched": [{"what": "a filing", "evidence_ids": ["E7"]}]}),
                           reply({"fetched": [], "unavailable": [{"input": "filings", "reason": "none fetched"}]})])
    r = run_agent(agents.retriever(lambda: set()), "Collect.", model=model, registry=tools.build_registry(),
                  store=store, request_id=RID)
    assert r.ok and r.model_calls == 2
    assert guardrails(store, r.run_id)[0]["guard"] == "evidence_ids_exist"


# ---- the analysts: one class, three configurations --------------------------------------

def test_three_analysts_share_one_output_class_and_differ_by_configuration():
    cfgs = [agents.analyst(n, lambda: set()) for n in ("fundamental_analyst", "regime_assessor", "technical_analyst")]
    assert {c.output_model for c in cfgs} == {agents.AnalystFindings}
    assert cfgs[0].tools == ["list_filings", "list_filing_sections", "read_filing_section"]
    assert cfgs[1].tools == ["get_macro_calendar"] and cfgs[2].tools == []
    assert len({c.fingerprint() for c in cfgs}) == 3


def test_fundamental_analyst_may_raise_only_flags_on_its_list_and_cite_only_stored_evidence(store):
    bad = {"findings": [{"finding": "Guidance was raised.", "evidence_ids": ["E9"], "bearing": "supports_bullish", "kind": "guidance_change", "guidance": RAISED}],
           "risk_flags": [{"flag": "insider_selling", "evidence_ids": ["E1"]}]}
    good = {"findings": [{"finding": "Guidance was raised.", "evidence_ids": ["E1"], "bearing": "supports_bullish", "kind": "guidance_change", "guidance": RAISED}],
            "risk_flags": [{"flag": "dilution", "evidence_ids": ["E1"]}]}
    model = ScriptedModel([reply(bad), reply(good)])
    r = run_agent(agents.analyst("fundamental_analyst", lambda: {"E1"}), "x", model=model,
                  registry=tools.build_registry(), store=store, request_id=RID)
    assert r.ok and r.model_calls == 2
    assert {g["guard"] for g in guardrails(store, r.run_id)} == {"cites_stored_evidence", "flags_on_the_list"}


def test_technical_analyst_describes_and_may_not_invent_a_level(store):
    base = {"price_description": "The close is above its averages.",
            "timeframes": {"daily": "Above.", "weekly": "Above.", "monthly": "Above."}}
    model = ScriptedModel([reply({**base, "levels": [{"label": "support", "level": 123.0}]}),
                           reply({**base, "levels": [{"label": "52-week high", "level": 150.25}]})])
    cfg = agents.analyst("technical_analyst", lambda: set(), lambda: {150.25, 98.1})
    r = run_agent(cfg, "x", model=model, store=store, request_id=RID)
    assert r.ok and r.model_calls == 2 and "never compute" in r.errors[0]
    model = ScriptedModel([reply({**base, "findings": [{"finding": "Likely to rise.", "evidence_ids": ["E1"],
                                                       "bearing": "supports_bullish"}]})] * 2)
    assert run_agent(cfg, "x", model=model, store=store, request_id=RID).status == "failed_validation"


# ---- the validation check ---------------------------------------------------------------

def finding(i, bearing, grade="strong", lead=True, primary=True, text="Guidance was raised to $65 billion.",
            kind="guidance_change"):
    lead = lead and bearing != "none"
    return {"id": i, "text": text, "evidence_ids": [], "bearing": bearing, "grade": grade, "lead": lead,
            "kind": kind if lead else "context",
            "primary_source": primary, "family": evidence.FUNDAMENTALS, "analyst": "fundamental_analyst",
            "date": day(-2)}


def record(*findings, flags=(), earnings_inside=()):
    facts = {"M1": {"id": "M1", "kind": "row", "text": "30-day row: base rate of a higher close 57.8%; typical realized move plus or minus 12.9%."},
             "M2": {"id": "M2", "kind": "event", "text": f"FOMC decision on {day(21)}, 21 days from today."},
             "M3": {"id": "M3", "kind": "price_move_since", "text": "the closing price has changed by +4.1%."}}
    return {"findings": {f["id"]: f for f in findings}, "facts": facts, "evidence": {}, "risk_flags": list(flags),
            "horizon": {"recommended_days": 30, "earnings_fact_ids_inside": list(earnings_inside)}}


def draft(**over):
    d = {
        "branches": [{"view": "bullish", "supporting": ["F1"], "opposing": ["R1"], "meets_precedence": True, "pruned_reason": None},
                     {"view": "bearish", "supporting": [], "opposing": ["F1"], "meets_precedence": False,
                      "pruned_reason": "No lead finding supports it."},
                     {"view": "no_view", "supporting": [], "opposing": [], "meets_precedence": False,
                      "pruned_reason": "A directional branch met the rules."}],
        "view": "bullish", "basis": "Guidance was raised.",
        "summary": {"text": "NVDA is likely to trade higher over 30 days because guidance was raised to $65 billion.", "cites": ["F1"]},
        "rationale": {"catalyst": {"text": "Management raised guidance.", "cites": ["F1"]},
                      "confirmation": {"text": "Nothing further confirms it yet.", "cites": ["F1"]},
                      "tempering": {"text": "One event; the price has already changed by 4.1% and the sector opposes.", "cites": ["F1", "M3", "R1"]}},
        "horizon_reasons": [{"text": "An FOMC decision falls 21 days in.", "cites": ["M2"]}],
        "resolution_criterion": "The close at the horizon is above the reference close.",
        "falsifiers": [{"finding_id": "F1", "type": "guidance_change", "trigger": "Guidance is cut.",
                        "reverses": "Reverses the catalyst", "action": "Close the position."}],
        "supporting": ["F1"], "opposing": ["R1"], "catalyst": {"dated": False},
    }
    d.update(over)
    return agents.ThesisDraft.model_validate(d)


F1 = finding("F1", "supports_bullish")
R1 = finding("R1", "supports_bearish", grade="weak", text="A weak item pointing the other way.")


def failed(d, rec):
    return " | ".join(validation.check(d, rec))


def test_a_sound_draft_passes():
    assert validation.check(draft(), record(F1, R1)) == []


def test_a_number_that_is_not_in_what_is_cited_fails():
    d = draft(summary={"text": "Guidance was raised to $70 billion.", "cites": ["F1"]})
    assert "numbers that are not in what it cites (70)" in failed(d, record(F1, R1))


def test_text_must_cite_and_only_ids_in_the_record():
    assert "cites nothing" in failed(draft(summary={"text": "Higher.", "cites": []}), record(F1, R1))
    assert "not in the record: F9" in failed(draft(summary={"text": "Higher.", "cites": ["F9"]}), record(F1, R1))


def test_a_view_needs_a_solid_lead_finding_and_qualifying_evidence_cannot_start_one():
    weak = finding("F1", "supports_bullish", grade="weak")
    assert "at least one finding that carries that direction" in failed(draft(), record(weak, R1))
    context = finding("F1", "supports_bullish", lead=False)          # context cannot start a view
    assert "at least one finding that carries that direction" in failed(draft(), record(context, R1))


def test_two_solid_findings_with_opposite_bearings_conflict_whatever_their_source():
    # Primary source is a grade check and nothing more (operator decision, 18 November 2026).
    departure = finding("F2", "supports_bearish", grade="moderate", primary=False, kind="new_event",
                        text="The chief executive left with no successor named.")
    rec = record(F1, departure)
    assert validation.precedence(rec)["conflict"] and validation.precedence(rec)["no_view_reason"] == "conflict"
    assert "carry both directions" in failed(draft(opposing=["F2"]), rec)


def test_context_never_conflicts_and_nothing_carrying_a_direction_is_its_own_reason():
    cash = finding("F2", "none", text="Free cash flow fell.")
    rec = record(F1, R1, cash)
    assert not validation.precedence(rec)["conflict"] and validation.check(draft(), rec) == []
    only_context = record(finding("F1", "none"), cash)
    assert validation.precedence(only_context)["no_view_reason"] == "nothing_carries_a_direction"
    assert validation.precedence(only_context)["carrying_a_direction"] == []


def test_a_view_on_the_earnings_result_alone_is_weakly_supported():
    result = finding("F1", "supports_bullish", grade="moderate", primary=False, kind="results_vs_estimates")
    assert validation.code_fields(draft(opposing=[]), record(result))["support"] == "weak"
    assert validation.code_fields(draft(opposing=[]), record(F1))["support"] == "normal"
    both = record(result, finding("F2", "supports_bullish"))
    assert validation.code_fields(draft(supporting=["F1", "F2"], opposing=[]), both)["support"] == "normal"


@pytest.mark.parametrize("direction,chosen,verdict", [
    ("bullish", ["F3"], "not_supported"),                 # context only
    ("bearish", ["F1"], "not_supported"),                 # chose the finding that points the other way
    ("bullish", ["F1"], "partly_supported"),              # F2 stands against it although not chosen
    ("bullish", ["F1", "F3"], "partly_supported"),
])
def test_how_a_thesis_the_user_entered_stands(direction, chosen, verdict):
    f = {x["id"]: x for x in (finding("F1", "supports_bullish"), finding("F2", "supports_bearish", kind="new_event"),
                              finding("F3", "none"))}
    v = validation.user_verdict(direction, chosen, f)
    assert v["verdict"] == verdict
    assert v["opposing"] == (["F2"] if direction == "bullish" else ["F1"])
    assert {r["kind"] for r in v["relied_on"]} <= {"anchored", "context"}


def test_a_user_thesis_is_well_supported_only_with_nothing_against_it():
    f = {x["id"]: x for x in (finding("F1", "supports_bullish"), finding("F3", "none"))}
    assert validation.user_verdict("bullish", ["F1"], f)["verdict"] == "well_supported"
    assert validation.user_verdict("bullish", ["F1", "F3"], f)["verdict"] == "partly_supported"


def test_solid_opposing_findings_must_be_listed_and_severe_flags_decline():
    assert validation.check(draft(opposing=[]), record(F1, R1)) == []      # a weak finding need not be listed
    rec = record(F1, R1, flags=[{"flag": "going_concern_or_liquidity_warning"}])
    assert "must be no_view, kind 'declined'" in failed(draft(), rec)


def test_invalidation_must_cover_each_supporting_finding_and_never_be_a_price_level():
    assert "none for: F1" in failed(draft(falsifiers=[]), record(F1, R1))
    price = [{"finding_id": "F1", "type": "other", "trigger": "The stock closes below $120.",
              "reverses": "x", "action": "y"}]
    assert "is a price condition" in failed(draft(falsifiers=price), record(F1, R1))


def test_price_derived_support_and_an_unflagged_earnings_date_fail():
    d = draft(summary={"text": "Higher, on strong momentum.", "cites": ["F1"]})
    assert "price-derived measure ('momentum')" in failed(d, record(F1, R1))
    assert "earnings report falls inside" in failed(draft(), record(F1, R1, earnings_inside=["M2x"]))


def test_branches_must_be_three_with_exactly_the_selected_one_unpruned():
    b = draft().model_dump()["branches"]
    b[1]["pruned_reason"] = None
    assert "Exactly one branch" in failed(draft(branches=b), record(F1, R1))


def test_no_view_needs_a_kind_and_a_reason_and_nothing_else():
    b = draft().model_dump()["branches"]
    b[0]["pruned_reason"], b[2]["pruned_reason"] = "The lead evidence is weak.", None
    d = agents.ThesisDraft.model_validate({"branches": b, "view": "no_view"})
    assert "needs no_view_kind" in failed(d, record(F1, R1))
    d = agents.ThesisDraft.model_validate({"branches": b, "view": "no_view", "no_view_kind": "nothing_found",
                                           "no_view_reason": "No branch met the rules."})
    assert validation.check(d, record(F1, R1)) == []


def test_a_single_family_is_recorded():
    assert validation.code_fields(draft(), record(F1, R1))["single_family"]


# ---- the Thesis step: one return in total ------------------------------------------------

def series():
    d0 = TODAY - dt.timedelta(days=400)
    return [(d0 + dt.timedelta(days=i), 100.0 + i * 0.05) for i in range(401)]


def state_for_thesis(store):
    eid = store.add_evidence(RID, "filing|x", {"kind": "earnings release (8-K)", "input": 2, "role": evidence.EVIDENCE,
                                               "family": evidence.FUNDAMENTALS, "source": "SEC EDGAR", "date": day(-2),
                                               "primary_source": True, "specific": True, "title": "8-K",
                                               "body": {"text": "Guidance was raised to $65 billion."}})
    rows = [{"days": d, "context_only": d == 180, "base_rate_pct": 57.8, "base_rate_basis": "blended",
             "typical_move_pct": 12.9, "crossed_below_pct": 18.0, "crossed_above_pct": 31.6} for d in (7, 14, 30, 60, 90, 180)]
    return {"request_id": RID, "symbol": "NVDA",
            "figures": {"measured": {"horizons": rows, "volatility": {"state": "active", "ratio": 1.41},
                                     "reference_close": 100.0},
                        "events": [{"kind": "fomc", "label": "FOMC decision", "date": day(21), "evidence_id": "E0"}],
                        "eligible_contracts": {7: 5, 14: 5, 30: 5, 60: 5, 90: 5}, "latest_earnings_report": day(-2)},
            "findings": {"fundamental_analyst": {"status": "ok", "output": {"findings": [
                {"id": "F1", "text": "Guidance was raised to $65 billion.", "evidence_ids": [eid], "bearing": "supports_bullish",
                 "kind": "guidance_change"}],
                "risk_flags": []}},
                "regime_assessor": {"status": "ok", "output": {"findings": [], "risk_flags": []}},
                "technical_analyst": {"status": "ok", "output": {"price_description": "Above its averages.",
                                                                 "timeframes": {}, "levels": []}}}}


def ctx_with(store, model):
    return StepContext(store=store, request_id=RID, cancel=threading.Event(), deadline=float("inf"),
                       extras={"model": model, "registry": ToolRegistry()})


@pytest.fixture
def prices(monkeypatch):
    monkeypatch.setattr(context, "fetch", lambda symbol, store=None: series())


def good_draft():
    d = draft(opposing=[], branches=[
        {"view": "bullish", "supporting": ["F1"], "opposing": [], "meets_precedence": True, "pruned_reason": None},
        {"view": "bearish", "supporting": [], "opposing": ["F1"], "meets_precedence": False, "pruned_reason": "No lead finding."},
        {"view": "no_view", "supporting": [], "opposing": [], "meets_precedence": False, "pruned_reason": "Bullish met the rules."}],
        rationale={"catalyst": {"text": "Management raised guidance.", "cites": ["F1"]},
                   "confirmation": {"text": "Nothing further confirms it yet.", "cites": ["F1"]},
                   "tempering": {"text": "The view rests on one event.", "cites": ["F1"]}},
        horizon_reasons=[{"text": "The 30-day row is the recommended horizon.", "cites": ["M3"]}])
    return d.model_dump()


def test_thesis_step_gives_a_view_with_the_base_rate_placed_by_code(store, prices):
    model = ScriptedModel([reply(good_draft())])
    t = stage2.thesis_step(state_for_thesis(store), ctx_with(store, model))
    assert t["view"] == "bullish" and t["validation"] == {"ok": True, "failed_checks": [], "returned_once": False, "in_harness": True}
    assert t["view_base_rate_pct"] == 57.8 and t["view_probability_pct"] is None
    assert t["recommended_horizon_days"] == 30 and t["findings"]["F1"]["grade"] == "strong" and t["findings"]["F1"]["lead"]
    assert t["risk_reference"] == {"level": 87.1, "usual_ranges_away": 1, "side": "below", "crossed_pct": 18.0}
    sent = model.requests[0]
    assert "tools" not in sent                                                  # the Thesis agent has no tools
    task = sent["messages"][0]["content"]
    assert "<untrusted_data" in task and "M1: 7-day row" in task               # findings wrapped as data
    assert not any(w in task.lower() for w in ("implied vol", "premium", "bid", "option price"))


def test_a_cut_off_reply_uses_the_one_return_and_a_failing_draft_is_then_shown_not_returned_again(store, prices):
    bad = good_draft()
    bad["summary"] = {"text": "NVDA has a 70% chance of closing higher.", "cites": ["F1"]}
    model = ScriptedModel([{"text": "{\"branches\": [", "stop_reason": "max_tokens"}, reply(bad), reply(good_draft())])
    t = stage2.thesis_step(state_for_thesis(store), ctx_with(store, model))
    assert len(model.requests) == 2 and len(model.replies) == 1                 # never asked a third time
    assert t["view"] == "bullish" and not t["validation"]["ok"] and t["validation"]["returned_once"]
    assert any("probability" in c for c in t["validation"]["failed_checks"])
    assert stage2.validate_step({"thesis": t}, None)["in_harness"]


def test_a_draft_that_fails_the_check_is_returned_once_and_then_passes(store, prices):
    bad = good_draft()
    bad["falsifiers"][0]["trigger"] = "The stock closes below $120."
    model = ScriptedModel([reply(bad), reply(good_draft())])
    t = stage2.thesis_step(state_for_thesis(store), ctx_with(store, model))
    assert t["validation"]["ok"] and t["validation"]["returned_once"]
    assert "price condition" in model.requests[1]["messages"][-1]["content"]
    run = t["run"]["run_id"]
    assert [p["ok"] for k, p in kinds(store, run) if k == "validation"] == [False, True]


def test_no_readable_draft_twice_is_an_agent_failure_not_a_no_view(store, prices):
    model = ScriptedModel([{"text": "not json"}, {"text": "still not json"}])
    with pytest.raises(StepFailed) as e:
        stage2.thesis_step(state_for_thesis(store), ctx_with(store, model))
    assert e.value.cause == "agent_failed"


def test_no_view_is_a_result_and_carries_the_branches(store, prices):
    b = good_draft()["branches"]
    b[0]["pruned_reason"], b[2]["pruned_reason"] = "The agent declined.", None
    model = ScriptedModel([reply({"branches": b, "view": "no_view", "no_view_kind": "nothing_found",
                                  "no_view_reason": "No branch met the rules."})])
    t = stage2.thesis_step(state_for_thesis(store), ctx_with(store, model))
    assert t["no_view"] and t["kind"] == "nothing_found" and len(t["branches"]) == 3 and t["validation"]["ok"]


def test_the_graph_does_not_return_a_draft_the_harness_already_returned(store):
    runs = []

    def thesis(state, ctx):
        runs.append(1)
        return {"view": "bullish", "validation": {"ok": False, "failed_checks": ["x"], "in_harness": True}}
    w = Workflow(store, steps={"thesis": thesis, "validate": stage2.validate_step})
    v = w.start("NVDA")
    v = w.resume(v["request_id"], "continue")
    assert len(runs) == 1 and v["pause"]["pause"] == "thesis"
    assert v["state"]["validation"]["final"] and not v["state"]["validation"]["ok"]


def test_range_rule_step_blocks_on_events_and_on_what_cannot_be_checked(store):
    s = state_for_thesis(store)
    s["thesis"] = {"no_view": True}
    s["figures"]["measured"]["volatility"]["state"] = "quiet"
    s["figures"]["events"] = [{"kind": "earnings", "label": "earnings report", "date": day(80)}]
    out = stage2.range_rule_step(s, None)
    assert out["rows_met"] == [7, 14] and out["horizon"]["recommended_days"] == 14
    s["figures"]["events"] = []
    assert "next earnings date" in stage2.range_rule_step(s, None)["reason"]
    s["thesis"] = {"view": "bullish"}
    assert not stage2.range_rule_step(s, None)["range_bound"]


def test_a_standing_disclosure_carries_no_bearing_whatever_the_analyst_reported(store):
    out = {"findings": [{"finding": "Guidance, unchanged since 2024, stays below consensus.", "evidence_ids": ["E1"],
                         "bearing": "supports_bearish", "standing_disclosure": True, "kind": "guidance_change",
                         "guidance": {**RAISED, "now": side("$4.10", "$4.30", measure="revenue")}},
                        {"finding": "Guidance was raised.", "evidence_ids": ["E1"], "bearing": "supports_bullish", "kind": "guidance_change", "guidance": RAISED}]}
    r = run_agent(agents.analyst("fundamental_analyst", lambda: {"E1"}), "x", model=ScriptedModel([reply(out)]),
                  registry=tools.build_registry(), store=store, request_id=RID)
    f = stage2._analyst_output(r, "F")["findings"]
    assert f[0]["bearing"] == "none" and f[0]["kind"] == "context" and f[0]["bearing_as_reported"] == "supports_bearish"
    assert f[1]["bearing"] == "supports_bullish" and f[1]["kind"] == "guidance_change"


def run_analyst(store, name, out, second=None, facts=None):
    model = ScriptedModel([reply(out)] + ([reply(second)] if second else []))
    r = run_agent(agents.analyst(name, lambda: {"E1", "E2", "E3"}, evidence_facts=facts), "x", model=model,
                  registry=tools.build_registry(), store=store, request_id=RID)
    return r, model


def test_a_direction_needs_a_stated_comparison(store):
    tone = {"findings": [{"finding": "Cloud revenue grew 30%.", "evidence_ids": ["E1"], "bearing": "supports_bullish"}]}
    no_figures = {"findings": [{"finding": "Guidance was raised.", "evidence_ids": ["E1"], "kind": "guidance_change",
                                "bearing": "supports_bullish"}]}
    r, _ = run_analyst(store, "fundamental_analyst", tone, no_figures)
    assert r.status == "failed_validation"
    errors = [g["detail"] for g in guardrails(store, r.run_id)]
    assert "is context, so its bearing must be 'none'" in errors[0] and "gives no figures" in errors[1]


def event(e, kind="ceo_or_cfo_departure_unplanned_or_no_permanent_successor"):
    return {"findings": [{"finding": "The chief executive left; no successor is named.", "evidence_ids": [e],
                          "kind": "new_event", "event_kind": kind, "bearing": "none"}]}


def test_an_event_takes_its_bearing_from_the_list_and_must_be_new(store):
    items = {"E1": {"date": day(-25), "kind": "company news"}, "E2": {"date": day(-40), "kind": "company news"}}
    r, _ = run_analyst(store, "fundamental_analyst", event("E1"))
    f = stage2._analyst_output(r, "F", items=items, latest=day(-10))["findings"][0]
    assert f["bearing"] == "supports_bearish" and f["kind"] == "new_event"      # set in code; 25 days old is recent
    r, _ = run_analyst(store, "fundamental_analyst", event("E2"))
    f = stage2._analyst_output(r, "F", items=items, latest=day(-10))["findings"][0]
    assert f["bearing"] == "none" and f["kind"] == "context" and f["context_reason"] == "not_recent"
    assert f["context_sentence"] == "Too old to count as new" and not r.returned  # reported as context, not refused
    r, _ = run_analyst(store, "fundamental_analyst", event("E1", "share_split"), event("E1", "buyback"))
    assert "not on the list" in guardrails(store, r.run_id)[0]["detail"]
    f = stage2._analyst_output(r, "F", items=items, latest=day(-10))["findings"][0]
    assert f["bearing"] == "none" and f["context_sentence"] == "Direction cannot be read from the event alone"


def test_every_context_finding_gets_its_reason_from_the_fixed_list(store):
    items = {"E1": {"date": day(-3), "kind": "earnings release (8-K)"}, "E2": {"date": day(-1), "kind": "macro calendar"},
             "E3": {"date": day(-1), "kind": "past earnings reactions"}}
    out = {"findings": [
        {"finding": "Free cash flow fell to $0.4B.", "evidence_ids": ["E1"], "context_reason": "no_estimate"},
        {"finding": "Management said demand is healthy.", "evidence_ids": ["E1"], "context_reason": "commentary"},
        {"finding": "The fourth-quarter revenue outlook is $2.4B.", "evidence_ids": ["E1"], "context_reason": "no_estimate"},
        {"finding": "The stock fell 3% after the last report.", "evidence_ids": ["E3"], "context_reason": "no_estimate"},
        {"finding": "Capital spending will rise.", "evidence_ids": ["E1"]}]}
    r, _ = run_analyst(store, "fundamental_analyst", out)
    got = [f["context_reason"] for f in stage2._analyst_output(r, "F", items=items)["findings"]]
    assert got == ["no_estimate", "commentary", "no_quarterly_consensus", "price_description", "other"]
    regime = {"findings": [{"finding": "The sector fund fell 11.7%.", "evidence_ids": ["E3"]},
                           {"finding": "An FOMC decision is due on 9 December.", "evidence_ids": ["E2"]}], "regime": "ok"}
    r, _ = run_analyst(store, "regime_assessor", regime)
    out = stage2._analyst_output(r, "R", items=items)
    # A scheduled release goes to the calendar and the flags, not to findings (ruling, 19 November 2026).
    assert [x["context_sentence"] for x in out["findings"]] == ["Price behaviour is description only"]
    assert out["calendar_findings_dropped"] == 1
    assert set(agents.CONTEXT_SENTENCE) == {"in_line", "mixed", "no_quarterly_consensus", "event_no_direction", "not_recent",
                                            "price_description", "no_macro_expectation", "no_estimate", "commentary", "other",
                                            "measure_no_direction", "worded_guidance", "reaffirmed", "guidance_mixed",
                                            "not_comparable"}


def test_results_in_line_or_mixed_carry_that_reason(store):
    f, _ = earnings(store, 1.045, 1.04, 2.26e9, 2.25e9)
    assert f["context_reason"] == "in_line" and f["context_sentence"] == "In line with estimates"
    f, _ = earnings(store, 1.12, 1.04, 2.10e9, 2.25e9, when=-1)
    assert f["context_reason"] == "mixed"
    f, _ = earnings(store, 1.12, 1.04, 2.31e9, 2.25e9, when=0)
    assert f["context_reason"] is None


def test_horizon_reasons_are_built_in_code_from_the_rule():
    from tradecraft import horizon
    events = [{"kind": "earnings", "label": "earnings report", "date": day(50)},
              {"kind": "fomc", "label": "FOMC decision", "date": day(21)}]
    rec = horizon.recommend(TODAY, events, {7: 5, 14: 5, 30: 5, 60: 0, 90: 5})
    r = stage2.horizon_reasons(rec, TODAY, events)
    assert r[0] == "Rows with eligible contracts: 7-day, 14-day, 30-day and 90-day."
    assert r[1] == "No eligible contracts: the 60-day row."
    assert r[2] == f"The 90-day row was set aside: it spans the earnings report on {day(50)}."
    assert r[3] == "The 30-day row is the one nearest 30 days of those left."
    assert r[4] == f"Known events inside it: FOMC decision on {day(21)} (day 21)."
    r = stage2.horizon_reasons(horizon.recommend(TODAY, [], None), TODAY, [])
    assert "provisional" in r[0] and r[-1] == "No known event falls inside it."
    r = stage2.horizon_reasons(horizon.recommend(TODAY, [{"kind": "earnings", "label": "earnings report", "date": day(1)}],
                                                 {d: 5 for d in (7, 14, 30, 60, 90)}), TODAY, [])
    assert any(x.startswith("Warning: Every horizon") for x in r)


def test_the_four_no_view_texts_are_fixed_wording_set_in_code():
    beat = finding("F1", "supports_bullish", grade="moderate", kind="results_vs_estimates", text="EPS above estimates.")
    left = finding("F2", "supports_bearish", kind="new_event", text="The chief executive left.")
    f = {"F1": beat, "F2": left}
    t = stage2.no_view_text("NVDA", "conflict", "nothing_found", f, [], [], None)
    assert t["headline"] == "The evidence that carries a direction points both ways"
    assert t["sentences"] == ["Pointing higher: EPS above estimates.", "Pointing lower: The chief executive left.",
                              "The system does not choose between two solid findings that disagree."]
    inline = {**finding("F1", "none"), "kind": "results_vs_estimates", "context_reason": "in_line"}
    t = stage2.no_view_text("KO", "nothing_carries_a_direction", "nothing_found", {"F1": inline, "F2": finding("F2", "none")}, [], [], None)
    assert t["headline"] == "Nothing found carries a direction"
    assert t["sentences"] == ["The system found 2 facts about KO. None comes with a comparison that gives it a direction.",
                              "The latest results were in line with estimates."]
    t = stage2.no_view_text("X", "declined", "declined", f, [{"flag": "going_concern_or_liquidity_warning"}], [], None)
    assert t["headline"] == "The system declined to take a view" and "going-concern" in t["sentences"][0]
    assert t["sentences"][1] == "A stock in this position trades on that outcome, not on its results."
    assert t["override_note"].startswith("This is an override.")
    t = stage2.no_view_text("X", "nothing_carries_a_direction", "insufficient_data", {}, [], ["earnings dates"], None)
    assert t["headline"] == "Not enough data to form a view" and t["sentences"] == ["Missing: earnings dates."]


def test_a_rejected_signal_reported_as_context_is_description_and_is_let_through(store):
    # Operator ruling, 19 November 2026: the check applies only to findings that carry a bearing.
    out = {"findings": [{"finding": "A 13F filing shows a hedge fund cut its stake.", "evidence_ids": ["E1"]}]}
    r, _ = run_analyst(store, "fundamental_analyst", out)
    assert r.ok and not r.returned
    assert stage2._analyst_output(r, "F")["findings"][0]["bearing"] == "none"


def test_sector_and_macro_findings_always_carry_no_bearing(store):
    out = {"findings": [{"finding": "The sector fund fell 11.7% over one month.", "evidence_ids": ["E1"]}], "regime": "hostile"}
    r, _ = run_analyst(store, "regime_assessor", out)
    f = stage2._analyst_output(r, "R")["findings"][0]
    assert f["bearing"] == "none" and f["kind"] == "context"


def earnings(store, eps, eps_est, rev, rev_est, when=-15):
    store.add_evidence(RID, f"earn|{when}", {"kind": "reported earnings (provider's figures)", "date": day(when),
                       "body": {"date": day(when), "eps_actual": eps, "eps_estimated": eps_est,
                                "revenue_actual": rev, "revenue_estimated": rev_est}})
    return stage2.results_finding(store, RID)


@pytest.mark.parametrize("eps,eps_est,rev,rev_est,bearing,how", [
    (1.12, 1.04, 2.31e9, 2.25e9, "supports_bullish", "above"),           # both above
    (1.12, 1.04, 2.26e9, 2.25e9, "supports_bullish", "above"),           # one above, the other within 1%
    (1.89, 1.97, 201.94e9, 202.22e9, "supports_bearish", "below"),       # AMZN: EPS below, revenue in line
    (1.12, 1.04, 2.10e9, 2.25e9, "none", "mixed"),                       # one above, one below
    (1.045, 1.04, 2.26e9, 2.25e9, "none", "in line"),                    # both within the tolerance
])
def test_the_results_finding_is_built_in_code_from_the_two_numbers(store, eps, eps_est, rev, rev_est, bearing, how):
    f, missing = earnings(store, eps, eps_est, rev, rev_est)
    assert missing is None and f["id"] == "F1" and f["kind"] == "results_vs_estimates" and f["set_by"] == "code"
    assert f["bearing"] == bearing and how in f["text"] and f["evidence_ids"] == ["E1"]


def test_the_results_finding_uses_the_latest_report_and_says_when_an_estimate_is_missing(store):
    earnings(store, 1.0, 2.0, 1e9, 2e9, when=-100)
    f, _ = earnings(store, 1.12, 1.04, 2.31e9, 2.25e9, when=-15)
    assert f["bearing"] == "supports_bullish" and day(-15) in f["text"] and "$2.31B" in f["text"]
    f, missing = earnings(store, 1.12, None, 2.31e9, 2.25e9, when=-1)
    assert f is None and "EPS estimate not available" in missing


def test_a_weak_finding_never_creates_a_conflict():
    weak_primary = finding("F2", "supports_bearish", grade="weak", kind="new_event", text="An old item.")
    rec = record(F1, R1, weak_primary)
    assert not validation.precedence(rec)["conflict"]
    assert validation.check(draft(), rec) == []          # listed or not, it does not cancel the view


# ---- "Take a view yourself" ----------------------------------------------------------------

def no_view_state(store):
    s = state_for_thesis(store)
    beat = finding("F1", "supports_bullish", grade="moderate", kind="results_vs_estimates", text="EPS above estimates.")
    left = {**finding("F2", "supports_bearish", kind="new_event", text="The chief executive left."),
            "event_kind": "ceo_or_cfo_departure_unplanned_or_no_permanent_successor"}
    cash = finding("F3", "none", text="Free cash flow fell.")
    s["thesis"] = {"no_view": True, "kind": "nothing_found", "no_view_reason_code": "conflict", "reason": "Both ways.",
                   "recommended_horizon_days": 30, "findings": {f["id"]: f for f in (beat, left, cash)}}
    return s


def test_the_conditions_the_system_can_name_follow_the_evidence_and_the_direction(store):
    f = no_view_state(store)["thesis"]["findings"]
    bull = [c["id"] for c in stage2.nameable_conditions(f, "bullish")]
    bear = stage2.nameable_conditions(f, "bearish")
    assert bull == ["earnings_result", "guidance_change"]
    assert [c["id"] for c in bear] == ["earnings_result", "guidance_change", "reverses_F2"]
    assert "permanent chief executive" in bear[2]["text"] and bear[2]["type"] in agents.FALSIFIER_TYPES
    assert all(c["type"] in agents.FALSIFIER_TYPES for c in bear)


def test_a_user_thesis_needs_a_direction_an_item_and_a_condition_and_gets_a_verdict(store):
    s = no_view_state(store)
    opts = stage2.own_view_options(s, s["thesis"])
    assert opts["horizons"] == [7, 14, 30, 60, 90] and opts["recommended_days"] == 30
    assert [(e["id"], e["kind"]) for e in opts["evidence"]] == [("F1", "anchored"), ("F2", "anchored"), ("F3", "context")]
    for entry, message in [({}, "Choose a direction"),
                           ({"direction": "bearish", "horizon_days": 45}, "Choose a horizon"),
                           ({"direction": "bearish"}, "at least one item"),
                           ({"direction": "bearish", "relied_on": ["F2"]}, "at least one condition"),
                           ({"direction": "bullish", "relied_on": ["F1"], "conditions": ["reverses_F2"]}, "at least one condition")]:
        with pytest.raises(ValueError, match=message):
            stage2.user_thesis_step({**s, "user_input": entry}, None)
    t = stage2.user_thesis_step({**s, "user_input": {"direction": "bearish", "horizon_days": 14, "relied_on": ["F2", "F3"],
                                                     "conditions": ["reverses_F2", "earnings_result"]}}, None)
    assert t["thesis_origin"] == "user" and t["view"] == "bearish" and t["primary_horizon_days"] == 14
    assert t["verdict"] == "partly_supported" and t["opposing"] == ["F1"]
    assert t["relied_on"] == [{"evidence_id": "F2", "kind": "anchored"}, {"evidence_id": "F3", "kind": "context"}]
    assert [f["type"] for f in t["falsifiers"]] == ["new_filing", "earnings_result"]
    assert t["view_base_rate_pct"] == 42.2 and t["entered_after_no_view"]["reason_code"] == "conflict"


# ---- operator rulings of 19 November 2026 ----------------------------------------------------

def guided(cmp, before, bearing, text="FY27 EPS guidance.", now=("$2.80", "$2.87"), measure="Adjusted EPS"):
    b = before if isinstance(before, tuple) else (before,)
    return {"finding": text, "evidence_ids": ["E1"], "kind": "guidance_change", "bearing": bearing,
            "guidance": {"now": side(*now, measure=measure, period="Fiscal 2027"),
                         "before": side(*b, measure=measure, period="Fiscal 2027"), "compared_with": cmp}}


def test_description_is_exempt_from_the_rejected_signal_check_but_a_bearing_is_not(store):
    trend = {"findings": [{"finding": "SPY closed 0.3% below its 200-day moving average.", "evidence_ids": ["E1"]}],
             "regime": "hostile"}
    r, _ = run_analyst(store, "regime_assessor", trend)
    assert r.ok and not r.returned                          # description: the design allows it
    r, _ = run_analyst(store, "fundamental_analyst", trend)
    assert r.ok and not r.returned                          # context from any analyst is exempt
    momentum = {"findings": [guided("consensus", "$2.70", "supports_bullish", "Guidance was raised on strong momentum.")]}
    r, _ = run_analyst(store, "fundamental_analyst", momentum, {"findings": []})
    assert "rests on a rejected signal" in guardrails(store, r.run_id)[0]["detail"]


def test_one_guidance_figure_yields_one_finding(store):
    twice = {"findings": [guided("earlier_guidance", ("$2.75", "$2.85"), "supports_bullish"),
                          guided("consensus", "$2.89", "supports_bearish")]}
    once = {"findings": [guided("consensus", "$2.89", "supports_bearish")]}
    r, _ = run_analyst(store, "fundamental_analyst", twice, once)
    assert r.ok and r.returned and "One guidance figure yields one finding" in r.errors[0]


def test_a_results_only_view_gets_the_fixed_invalidation_conditions_and_the_agents_are_added(store, prices):
    s = state_for_thesis(store)
    s["figures"]["events"].append({"kind": "earnings", "label": "earnings report", "date": day(70), "evidence_id": "E0"})
    s["findings"]["fundamental_analyst"]["output"]["findings"][0]["kind"] = "results_vs_estimates"
    t = stage2.thesis_step(s, ctx_with(store, ScriptedModel([reply(good_draft())])))
    assert t["support"] == "weak" and "reported 2 days ago" in t["support_note"]
    assert [(f["type"], f["set_by"]) for f in t["falsifiers"]] == [
        ("earnings_result", "code"), ("guidance_change", "code"), ("new_filing", "code"), ("guidance_change", "agent")]
    assert day(70) in t["falsifiers"][0]["trigger"] and "misses consensus" in t["falsifiers"][0]["trigger"]
    assert t["report_dates"] == {"latest_report": day(-2), "latest_report_days_ago": 2,
                                 "next_report": day(70), "next_report_days_from_today": 70}


def test_without_a_known_next_report_the_earnings_condition_is_left_out_and_bearish_wording_is_reversed():
    c = stage2.results_only_conditions("bearish", "F1", {"next_report": None})
    assert [f["type"] for f in c] == ["guidance_change", "new_filing"] and c[0]["trigger"] == "Guidance is raised"
    assert "beats consensus" in stage2.results_only_conditions("bearish", "F1", {"next_report": "2027-01-14"})[0]["trigger"]


def test_a_view_resting_on_more_than_the_result_keeps_the_agents_conditions_only(store, prices):
    t = stage2.thesis_step(state_for_thesis(store), ctx_with(store, ScriptedModel([reply(good_draft())])))
    assert t["support"] == "normal" and [f["set_by"] for f in t["falsifiers"]] == ["agent"]


def test_one_day_is_singular():
    assert stage2._days(1) == "1 day" and stage2._days(22) == "22 days" and stage2._days(0) == "0 days"


# ---- rulings of 19 November 2026 on the four faults of the 43-symbol run ----------------

def test_the_event_kind_check_is_the_fundamental_analysts_alone(store):
    macro = {"findings": [{"finding": "CPI is released on 10 December.", "evidence_ids": ["E2"], "kind": "new_event",
                           "event_kind": "macro_calendar"},
                          {"finding": "The sector fund fell 4%.", "evidence_ids": ["E3"], "kind": "new_event",
                           "event_kind": "sector_move", "bearing": "supports_bearish"}], "regime": "ok"}
    r, _ = run_analyst(store, "regime_assessor", macro)
    assert r.ok and not r.returned
    items = {"E2": {"kind": "macro calendar", "date": day(-1)}, "E3": {"kind": "sector context", "date": day(-1)}}
    out = stage2._analyst_output(r, "R", items=items)
    assert [(f["id"], f["kind"], f["bearing"]) for f in out["findings"]] == [("R1", "context", "none")]
    assert out["calendar_findings_dropped"] == 1
    assert settings.limits()["agents"]["regime_assessor"]["max_output_tokens"] == 2500


@pytest.mark.parametrize("text,hit", [
    ("Intel completed a $23 billion equity offering to support future growth.", False),
    ("Regulators met resistance from the industry; antibiotic resistance is rising.", False),
    ("Customer support costs rose.", False),
    ("The stock held its support level.", True),
    ("Support and resistance were tested twice.", True),
    ("Buyers found support at $182.", True),
    ("Resistance near 450 capped the move.", True),
])
def test_support_and_resistance_match_only_as_chart_terms(text, hit):
    assert (agents.rejected_signal(text) == "Support or resistance as a reason for direction") is hit


def test_a_defined_event_is_never_refused_as_a_rejected_signal(store):
    offering = {"finding": "The company sold shares; the stock is in a downtrend with momentum fading.",
                "evidence_ids": ["E1"], "kind": "new_event", "event_kind": "share_offering_or_shelf_registration"}
    r, _ = run_analyst(store, "fundamental_analyst", {"findings": [offering]})
    assert r.ok and not r.returned
    f = stage2._analyst_output(r, "F", items={"E1": {"date": day(-2), "kind": "company filing (8-K)"}}, latest=day(-10))
    assert f["findings"][0]["bearing"] == "supports_bearish"


@pytest.mark.parametrize("now,before,result", [
    ("$24.45 to $24.50", "24.48106 (consensus eps_avg)", "in_line"),                 # the range contains consensus
    ("$26.576 billion to $26.626 billion", "$26,606,442,238 (consensus revenue_avg)", "in_line"),
    ("$10.65 to $11.40", "consensus eps_avg 10.25079 (fiscal year ending 2027-01-31)", "above"),
    ("$2.80 to $2.87", "$2.89149 (consensus average)", "below"),
    ("$62.0 to $64.0 billion", "consensus revenue avg 63184256585 (FY2026)", "in_line"),   # one unit for both ends
    ("~$80,000 - $82,000", "$81,433 million consensus (revenue_avg)", "in_line"),          # units differ
    ("$11.05 to $11.15 (midpoint $11.10)", "consensus FY2026 eps_avg 11.11401", "in_line"),
    ("$8.530 - $8.534 billion", "8,529,296,383", "above"),                               # wholly above, however narrowly
    ("~$5.60", "$5.59173 (consensus avg)", "in_line"),                                    # single figure within 1%
    ("$0.90", "consensus 0.87384", "above"),
    ("$51.1B", "consensus revenue_avg 51124568330 (about $51.12B)", "in_line"),
    ("$3.00", "$3.10", "below"),
    ("higher than last year", "$3.10", "unreadable"),
    ("$3.00", "between $3.05 and $3.20", "unreadable"),
])
def test_guidance_against_consensus_is_set_in_code_from_the_two_figures(now, before, result):
    assert stage2.guidance_vs_consensus(now, before, 1.0)["result"] == result


def test_the_analysts_own_bearing_on_guidance_is_never_used(store):
    def one(now, before, said, cmp="consensus", **kw):
        r, _ = run_analyst(store, "fundamental_analyst", {"findings": [guided(cmp, before, said, now=now, **kw)]})
        return stage2._analyst_output(r, "F")["findings"][0]
    f = one(("$24.45", "$24.50"), "24.48", "supports_bearish")
    assert (f["bearing"], f["kind"], f["context_reason"], f["context_sentence"]) == (
        "none", "context", "in_line", "In line with estimates")
    assert f["bearing_as_reported"] == "supports_bearish" and f["comparison"]["set_by"] == "code"
    assert one(("$2.80", "$2.87"), "$2.70", "none")["bearing"] == "supports_bullish"
    assert one(("$2.80", "$2.87"), "$2.89", "supports_bullish")["bearing"] == "supports_bearish"
    # Against earlier guidance too: the analyst said bullish, the figures say lowered.
    f = one(("$2.80", "$2.87"), ("$2.85", "$2.95"), "supports_bullish", cmp="earlier_guidance")
    assert f["bearing"] == "supports_bearish" and f["comparison"]["result"] == "lowered"


def G(now, before, cmp="earlier_guidance", measure="EPS", b_measure=None, period="fiscal 2026", b_period=None,
      basis="adjusted", b_basis=None, passage=None):
    return {"now": side(*now, measure=measure, period=period, basis=basis),
            "before": None if before is None else side(*before, measure=b_measure or measure,
                                                       period=b_period or period, basis=b_basis or basis),
            "compared_with": cmp if before is not None else None, "passage": passage}


@pytest.mark.parametrize("g,result", [
    (G(("$4.10", "$4.30"), ("$3.90", "$4.10")), "raised"),                       # both ends higher
    (G(("$4.00", "$4.10"), ("$3.90", "$4.10")), "raised"),                       # one higher, one equal
    (G(("+6%",), ("+4%", "+6%"), measure="net revenue growth"), "raised"),
    (G(("+2.5%", "+3.5%"), ("+5%", "+7%"), measure="core EPS growth"), "lowered"),
    (G(("$3.90", "$4.00"), ("$3.90", "$4.10")), "lowered"),
    (G(("+1%", "+2%"), ("+4%", "+6%"), measure="core constant currency EPS growth"), "lowered"),   # a deep cut
    (G(("$1.00",), ("$4.00",)), "lowered"),
    (G(("$9B",), ("$7,500 million",), measure="revenue"), "raised"),                              # units differ
    (G(("$3.90", "$4.10"), ("$3.90", "$4.10")), "reaffirmed"),
    (G(("$3.95", "$4.05"), ("$3.90", "$4.10")), "mixed"),                        # narrowed
    (G(("$10.9B", "$11.0B"), ("$10.55B", "$10.75B"), measure="operating profit (adjusted)"), "raised"),
    (G(("$62.0", "$64.0 billion"), ("63184256585",), cmp="consensus", measure="revenue"), "in_line"),
    (G(("$2.80", "$2.87"), ("$2.89149",), cmp="consensus", measure="adjusted EPS", b_measure="EPS", b_basis="not stated"), "below"),
    # Only EPS, revenue or net sales, and operating income or margin can carry a bearing.
    (G(("$9.1B", "$9.4B"), ("$8.9B", "$9.2B"), measure="free cash flow"), "measure_no_direction"),
    (G(("$2.675", "$2.75 billion"), ("$2.675", "$2.775 billion"), measure="adjusted operating expenses"), "measure_no_direction"),
    (G(("$9B",), ("$7.5 billion",), measure="hyperscaler AI infrastructure revenue"), "measure_no_direction"),
    (G(("$23B", "$24B"), ("$22B",), measure="capital expenditure"), "measure_no_direction"),
    (G(("20%",), ("19%",), measure="effective tax rate"), "measure_no_direction"),
    # Measure, period and basis must match.
    (G(("$4.10", "$4.30"), ("$3.90", "$4.10"), b_period="fiscal 2025"), "not_comparable"),
    (G(("$4.10", "$4.30"), ("$3.90", "$4.10"), b_basis="GAAP"), "not_comparable"),
    (G(("$4.10", "$4.30"), ("$3.90", "$4.10"), b_measure="revenue"), "not_comparable"),
    (G(("+3%", "+4%"), ("$3.90", "$4.10")), "not_comparable"),                   # a growth rate against a level
    (G(("$4.10",), ("$3.90",), period="FY2026", b_period="fiscal year 2026"), "raised"),
    # Words, not figures.
    (G((None,), ("+15%",), measure="revenue growth", passage="high-teens growth"), "worded"),
    (G(("19%", "20%"), ("high-teens",), measure="adjusted revenue growth"), "worded"),
    (G(("$4.10", "$4.30"), None), "nothing_to_compare"),
])
def test_every_guidance_bearing_is_set_in_code_from_the_extracted_figures(g, result):
    assert stage2.guidance_comparison(g, 1.0)["result"] == result


def test_guidance_reasons_and_the_passage_are_kept_on_the_finding(store):
    worded = {"finding": "Revenue growth is expected in the high teens.", "evidence_ids": ["E1"], "kind": "guidance_change",
              "guidance": G((None,), None, measure="revenue growth", passage="we expect high-teens growth")}
    capex = {"finding": "Capital spending is guided to $23 to $24 billion.", "evidence_ids": ["E1"], "kind": "guidance_change",
             "guidance": G(("$23B", "$24B"), None, measure="capital expenditure")}
    same = {"finding": "EPS guidance was reaffirmed.", "evidence_ids": ["E1"], "kind": "guidance_change",
            "guidance": G(("$3.90", "$4.10"), ("$3.90", "$4.10"))}
    r, _ = run_analyst(store, "fundamental_analyst", {"findings": [worded, capex, same]})
    assert r.ok and not r.returned
    f = stage2._analyst_output(r, "F")["findings"]
    assert [(x["bearing"], x["context_sentence"]) for x in f] == [
        ("none", "Stated in words, not figures"), ("none", "Direction cannot be read from this measure"),
        ("none", "Reaffirmed: unchanged from earlier guidance")]
    assert f[0]["comparison"]["passage"] == "we expect high-teens growth"


def test_a_guidance_change_needs_figures_or_the_passage(store):
    empty = {"finding": "Guidance was raised.", "evidence_ids": ["E1"], "kind": "guidance_change",
             "guidance": G((None,), None)}
    r, _ = run_analyst(store, "fundamental_analyst", {"findings": [empty]}, {"findings": []})
    assert "gives no figures" in guardrails(store, r.run_id)[0]["detail"]


@pytest.mark.parametrize("trigger,price", [
    ("Full-year EPS guidance falls below consensus.", False),
    ("Revenue growth drops below the prior quarter's rate.", False),
    ("The company cuts guidance or reports a miss.", False),
    ("The stock closes below $120.", True),
    ("A close above the prior high.", True),
    ("The share price moves below its level before the report.", True),
    ("Shares trade under $50.", True),
    ("The share price falls sharply.", True),
    ("The stock breaks its 200-day moving average.", True),
])
def test_a_price_condition_needs_a_price_beside_above_or_below(trigger, price):
    assert bool(validation._PRICE_LEVEL.search(trigger)) is price


def test_the_fixed_conditions_written_by_code_never_reach_the_price_check():
    for view in ("bullish", "bearish"):
        for c in stage2.results_only_conditions(view, "F1", {"next_report": "2027-02-01"}):
            assert c["set_by"] == "code" and not validation._PRICE_LEVEL.search(c["trigger"])
