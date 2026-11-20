"""Each run limit in docs/build-plan.md section 4, shown stopping a run cleanly."""
import json
import sqlite3
import threading

import pytest
from pydantic import BaseModel

from tradecraft import net, settings
from tradecraft.harness import AgentConfig, ScriptedModel, Tool, ToolRegistry, ToolUnavailable, run_agent
from conftest import kinds


class Out(BaseModel):
    findings: list[str]


DONE = {"text": json.dumps({"findings": ["done"]})}


def registry(fn=None, name="lookup", untrusted=False):
    reg = ToolRegistry()
    reg.register(Tool(name=name, description="d", untrusted=untrusted,
                      input_schema={"type": "object", "properties": {"q": {"type": "string"}}},
                      fn=fn or (lambda ctx, q: f"result for {q}")))
    return reg


def cfg(name="regime_assessor", tools=("lookup",)):
    return AgentConfig(name=name, role=name, instructions="x", output_model=Out, tools=list(tools))


def limits_of(name):
    return settings.limits()["agents"][name]


def test_tool_call_limit_refuses_and_forces_an_answer(store):
    n = limits_of("regime_assessor")["max_tool_calls"]            # 6
    replies = [{"tool_uses": [{"name": "lookup", "input": {"q": str(i)}}]} for i in range(n + 1)] + [DONE]
    model = ScriptedModel(replies)
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store)
    assert r.ok and r.tool_calls == n
    assert "tool-call limit" in model.requests[n + 1]["messages"][-1]["content"][0]["content"]
    assert model.requests[n]["tool_choice"] == {"type": "none"}   # once the limit is hit, no more tools
    assert any(k == "limit" and p["limit"] == "max_tool_calls" for k, p in kinds(store, r.run_id))


def test_repeated_identical_call_is_refused(store):
    hits = []
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]},
                           {"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(lambda ctx, q: hits.append(q) or "x"), store=store)
    assert r.ok and hits == ["a"] and r.tool_calls == 1
    assert "already called" in model.requests[2]["messages"][-1]["content"][0]["content"]


def test_thesis_agent_is_offered_no_tools(store):
    model = ScriptedModel([DONE])
    r = run_agent(cfg("thesis"), "go", model=model, registry=registry(), store=store)
    assert r.ok and "tools" not in model.requests[0]


def test_time_limit_ends_the_run(store):
    t = {"now": 0.0}

    def slow(ctx, q):
        t["now"] += 100.0                                         # the tool takes 100 "seconds"
        return "x"
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(slow), store=store, clock=lambda: t["now"])
    assert r.status == "timed_out" and "90 seconds" in r.message
    assert len(model.requests) == 1


def test_spend_limit_stops_before_the_next_model_call(store):
    store.add_spend("req_s", "run_x", "x", "claude-opus-5-5", {}, 1.00)
    model = ScriptedModel([DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store, request_id="req_s")
    assert r.status == "spend_limit" and model.requests == []
    assert "$1.00" in r.message


def test_daily_spend_limit(store):
    store.add_spend("req_other", "run_x", "x", "claude-opus-5-5", {}, 10.00)
    model = ScriptedModel([DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store, request_id="req_new")
    assert r.status == "spend_limit" and "daily" in r.message


def test_tool_error_is_retried_once_then_recorded_unavailable(store):
    attempts = []

    def flaky(ctx, q):
        attempts.append(q)
        raise ConnectionError("source down")
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(flaky), store=store)
    assert r.ok and len(attempts) == 2                            # one retry
    assert r.unavailable_inputs[0]["tool"] == "lookup"
    assert "Not available" in model.requests[1]["messages"][-1]["content"][0]["content"]


def test_source_refusal_is_not_retried(store):
    attempts = []

    def refused(ctx, q):
        attempts.append(q)
        raise ToolUnavailable("FMP: not served for this symbol")
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(refused), store=store)
    assert r.ok and len(attempts) == 1 and "not served" in r.unavailable_inputs[0]["reason"]


def test_large_tool_result_is_truncated_with_a_note(store):
    big = "x" * 50_000
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(lambda ctx, q: big), store=store)
    sent = model.requests[1]["messages"][-1]["content"][0]["content"]
    assert len(sent) <= 8000 * 4 and "Truncated by the harness" in sent


def test_reply_cut_off_at_output_limit_is_returned_once(store):
    model = ScriptedModel([{"text": '{"findings": ["half', "stop_reason": "max_tokens"}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store)
    assert r.ok and r.model_calls == 2
    assert model.requests[0]["max_tokens"] == limits_of("regime_assessor")["max_output_tokens"]
    assert "cut off at the output limit" in model.requests[1]["messages"][-1]["content"]


def test_cancel_stops_the_run(store):
    stop = threading.Event()
    stop.set()
    model = ScriptedModel([DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store, cancel=stop)
    assert r.status == "cancelled" and model.requests == []


def test_every_step_is_traced_with_usage_and_cost(store):
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(model_name := "regime_assessor"), "go", model=model, registry=registry(), store=store)
    ks = [k for k, _ in kinds(store, r.run_id)]
    assert ks == ["run_start", "model_call", "tool_call", "tool_result", "model_call", "validation", "run_end"]
    calls = [p for k, p in kinds(store, r.run_id) if k == "model_call"]
    assert all(c["usage"]["input_tokens"] == 1000 and c["cost_usd"] > 0 for c in calls)


# ---- reach of tools, secrets, append-only records ---------------------------------

def test_network_allowlist():
    assert net.check_host("https://cdn.cboe.com/api/global/delayed_quotes/options/SPY.json") == "cdn.cboe.com"
    with pytest.raises(net.NotAllowed):
        net.check_host("https://example.com/anything")


def test_file_allowlist():
    assert net.writable("data/cache.bin")
    for p in ["scripts/tests/vrp_test_a.py", "vrp_out/TRIALS.log", "ops/snapshot_cron.sh", ".env"]:
        with pytest.raises(net.NotAllowed):
            net.writable(p)
    with pytest.raises(net.NotAllowed):
        net.readable(".env")
    assert net.readable("docs/research")


def test_secrets_never_reach_the_trace(store, monkeypatch):
    monkeypatch.setattr(settings, "_env", lambda: {"FMP_API_KEY": "sk-test-0123456789"})
    reg = registry(lambda ctx, q: "url?apikey=sk-test-0123456789 returned 403")
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=reg, store=store)
    dump = json.dumps(store.trace_rows(run_id=r.run_id))
    assert "sk-test-0123456789" not in dump and "<FMP_API_KEY>" in dump
    assert "sk-test-0123456789" not in json.dumps(model.requests)


def test_permanent_record_is_append_only_and_trace_cannot_be_edited(store):
    rid = store.open_request("NVDA")
    store.write_record(rid, "stage_1", "pass", "system", {"passing_contracts": 24})
    store.commit_request(rid)
    store.trace(rid, "run_a", "x", 1, "note", {})
    store.write_record(store.open_request("AMZN"), "stage_1", "pass", "system", {})   # stays pending
    with sqlite3.connect(store.path) as c:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            c.execute("UPDATE pending_records SET decision='x'")
        for sql in ["UPDATE decision_records SET decision='fail'", "DELETE FROM decision_records"]:
            with pytest.raises(sqlite3.IntegrityError, match="append-only"):
                c.execute(sql)
        with pytest.raises(sqlite3.IntegrityError, match="cannot be edited"):
            c.execute("UPDATE trace SET kind='x'")



def test_pending_log_commit_and_discard(store):
    a = store.open_request("NVDA")
    store.write_record(a, "stage_1", "pass", "system", {"n": 24})
    store.write_record(a, "stage_1", "continue", "user", {})
    assert store.records(a) == [] and len(store.pending(a)) == 2      # nothing permanent yet
    assert store.commit_request(a) == 2
    assert [r["decision"] for r in store.records(a)] == ["pass", "continue"] and store.pending(a) == []
    store.write_record(a, "stage_2", "accept", "user", {})            # after the commit point: direct
    assert len(store.records(a)) == 3
    with pytest.raises(ValueError):
        store.discard_request(a, "stopped")

    b = store.open_request("AMZN")
    store.write_record(b, "stage_1", "pass", "system", {})
    store.trace(b, "run_b", "thesis", 1, "run_end", {"status": "ok"})
    assert store.discard_request(b, "stopped_no_view") == 1
    assert store.records(b) == [] and store.pending(b) == []
    assert len(store.trace_rows(request_id=b)) == 1                   # the trace is kept
    assert store.request(b)["status"] == "stopped_no_view"


def test_old_traces_of_uncommitted_requests_are_purged_after_7_days(store):
    kept, dropped = store.open_request("NVDA"), store.open_request("AMZN")
    store.write_record(kept, "stage_1", "pass", "system", {})
    store.commit_request(kept)
    old = "2026-11-01T10:00:00-08:00"
    with sqlite3.connect(store.path) as c:
        for rid in (kept, dropped):
            c.execute("INSERT INTO trace (request_id, run_id, agent, step, kind, payload, created_at)"
                      " VALUES (?,?,?,?,?,?,?)", (rid, "r", "x", 1, "note", "{}", old))
    store.trace(dropped, "r2", "x", 1, "note", {})                    # recent: kept
    assert store.purge_old_traces() == 1
    assert len(store.trace_rows(request_id=kept)) == 1 and len(store.trace_rows(request_id=dropped)) == 1


# ---- added 18 November 2026 after the harness review --------------------------------

def test_api_errors_are_retried_by_the_harness_with_increasing_pauses(store):
    pauses = []
    model = ScriptedModel([{"error": "rate limited by the API", "retryable": True},
                           {"error": "API error 529", "retryable": True}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store, sleep=pauses.append)
    assert r.ok and len(model.requests) == 3
    assert pauses == [1.0, 2.0]


def test_api_retries_never_run_past_the_deadline(store):
    t = {"now": 0.0}

    def hang():
        t["now"] += 80.0                       # each failed call eats 80 of the 90 seconds
    model = ScriptedModel([{"error": "the model did not answer in time", "retryable": True, "before": hang},
                           {"error": "the model did not answer in time", "retryable": True, "before": hang},
                           DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store,
                  clock=lambda: t["now"], sleep=lambda s: None)
    assert r.status == "timed_out" and len(model.requests) == 2
    assert model.timeouts[1] <= 10.0           # the retry got only what was left


def test_non_retryable_api_error_stops_at_once(store):
    model = ScriptedModel([{"error": "the API rejected the request: bad schema"}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(), store=store, sleep=lambda s: None)
    assert r.status == "model_error" and len(model.requests) == 1


def test_a_stuck_tool_is_cut_off_at_the_deadline(store, monkeypatch):
    import time as _t
    monkeypatch.setitem(settings.limits()["agents"]["regime_assessor"], "time_seconds", 1)
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    t0 = _t.monotonic()
    r = run_agent(cfg(), "go", model=model, registry=registry(lambda ctx, q: _t.sleep(3) or "late"), store=store)
    assert _t.monotonic() - t0 < 2.0           # did not wait the full 3 seconds
    assert r.status == "timed_out"
    assert r.unavailable_inputs[0]["reason"].startswith("the source did not answer within")


def test_input_cap_shortens_results_and_forces_an_answer(store, monkeypatch):
    monkeypatch.setitem(settings.limits()["text"], "max_input_tokens_per_call", 3000)
    big = "y" * 20_000                         # about 5,000 tokens: over the cap of 3,000
    model = ScriptedModel([{"tool_uses": [{"name": "lookup", "input": {"q": "a"}}]}, DONE])
    r = run_agent(cfg(), "go", model=model, registry=registry(lambda ctx, q: big), store=store)
    assert r.ok
    sent = model.requests[1]["messages"][-1]["content"][0]["content"]
    assert "Input limit" in sent and len(sent) < 20_000
    assert model.requests[1]["tool_choice"] == {"type": "none"}
    assert any(k == "limit" and p["limit"] == "max_input_tokens_per_call" for k, p in kinds(store, r.run_id))


def test_oversized_task_is_not_started(store, monkeypatch):
    monkeypatch.setitem(settings.limits()["text"], "max_input_tokens_per_call", 1000)
    model = ScriptedModel([DONE])
    r = run_agent(cfg(), "z" * 10_000, model=model, registry=registry(), store=store)
    assert r.status == "input_limit" and model.requests == []


def test_fingerprint_identifies_the_prompt_version(store):
    a, b = cfg(), cfg()
    assert a.fingerprint() == b.fingerprint()
    b.instructions = "x, reworded"
    assert a.fingerprint() != b.fingerprint()
    r = run_agent(a, "go", model=ScriptedModel([DONE]), registry=registry(), store=store)
    start = [p for k, p in kinds(store, r.run_id) if k == "run_start"][0]
    assert start["config_fingerprint"] == a.fingerprint() == r.config_fingerprint
