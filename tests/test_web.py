"""The JSON API the pages use, with the real gate on a canned chain."""
import pytest
from fastapi.testclient import TestClient

from tradecraft.data import chain, session
from tradecraft.steps import real_steps
from tradecraft.web.app import create_app
from test_stage1 import c, patch

def steps(**more):
    """The real gate, with stage 2 replaced by a stand-in: these tests make no model calls."""
    return {"gate": real_steps()["gate"],
            "thesis": lambda s, c: {"no_view": True, "kind": "nothing_found", "reason": "test"}, **more}


SYMBOLS = {"updated": "2026-11-18T20:00:00-08:00",
           "symbols": [["ADBE", "Adobe Inc.", "STOCK"], ["NVDA", "NVIDIA Corporation", "STOCK"]]}


@pytest.fixture
def client(store, monkeypatch):
    patch(monkeypatch, False, snap=[c(), c(), c(dte=30)])
    monkeypatch.setattr(chain, "snapshot_info", lambda: {"file": "x", "taken_et": "2026-11-18T14:00-05:00"})
    return TestClient(create_app(store, steps(), SYMBOLS))


def test_home_reports_market_snapshot_recent_and_no_open_request(client):
    h = client.get("/api/home").json()
    assert h["market"]["open"] is False and h["snapshot"]["taken_et"].startswith("2026-11-18T14:00")
    assert h["recent"] == [] and h["open"] is None
    r = client.get("/api/symbols")
    assert r.json()["symbols"][1][0] == "NVDA" and r.headers["cache-control"] == "no-store"


def test_pages_are_served(client):
    page = client.get("/")
    assert page.status_code == 200 and "Which underlying do you want to research?" in page.text
    assert "Copied verbatim" in client.get("/static/tradecraft.css").text
    assert client.get("/static/app.js").status_code == 200


def test_start_runs_the_gate_and_the_view_has_no_prices(client):
    v = client.post("/api/requests", json={"symbol": "nvda"}).json()
    g = v["state"]["gate"]
    assert v["symbol"] == "NVDA" and v["pause"]["pause"] == "gate" and v["opened_at"]
    assert g["status"] == "pass" and g["passing"] == 2 and g["provisional"] is True
    assert "contracts" not in g and "spot" not in g
    assert client.get("/api/requests/open").json()["request_id"] == v["request_id"]     # a reload restores it


def test_unlisted_symbol_and_second_request_are_refused(client):
    assert client.post("/api/requests", json={"symbol": "ZZZZ"}).status_code == 404
    first = client.post("/api/requests", json={"symbol": "NVDA"}).json()
    r = client.post("/api/requests", json={"symbol": "ADBE"})
    assert r.status_code == 409 and r.json()["detail"]["request_id"] == first["request_id"]


def test_adjust_override_and_stop_through_the_api(client, monkeypatch, store):
    patch(monkeypatch, False, snap=[c(dte=30), c(dte=30)])
    v = client.post("/api/requests", json={"symbol": "ADBE"}).json()
    rid = v["request_id"]
    assert v["state"]["gate"]["status"] == "fail" and v["pause"]["actions"] == ["override", "adjust", "stop"]
    v = client.post(f"/api/requests/{rid}/action", json={"action": "override", "rationale": " "}).json()
    assert "rationale is required" in v["pause"]["error"]
    v = client.post(f"/api/requests/{rid}/action", json={"action": "adjust", "settings": {"dte_min": 22, "dte_max": 41}}).json()
    assert v["state"]["gate"]["status"] == "pass" and v["state"]["gate"]["changed"] == ["dte_min", "dte_max"]
    v = client.post(f"/api/requests/{rid}/action", json={"action": "continue"}).json()
    assert v["pause"]["pause"] == "thesis" and v["pause"]["actions"] == ["stop", "own_view"]   # a no view
    assert v["running"] is False and [p["status"] for p in v["progress"]][-1] == "done"
    v = client.post(f"/api/requests/{rid}/action", json={"action": "stop"}).json()
    assert v["done"] is True
    assert store.records(rid) == [] and client.get("/api/home").json()["recent"] == []   # nothing recorded


def test_leave_stops_the_open_request(client):
    rid = client.post("/api/requests", json={"symbol": "NVDA"}).json()["request_id"]
    assert client.post(f"/api/requests/{rid}/leave", json={}).json()["left"] is True
    assert client.get("/api/requests/open").json() is None
    assert client.post(f"/api/requests/{rid}/action", json={"action": "continue"}).status_code == 404


def test_engine_restart_ends_the_open_request(store, monkeypatch):
    patch(monkeypatch, False, snap=[c(), c()])
    a = TestClient(create_app(store, steps(), SYMBOLS))
    rid = a.post("/api/requests", json={"symbol": "NVDA"}).json()["request_id"]
    b = TestClient(create_app(store, steps(), SYMBOLS))                              # the engine restarts
    assert b.get("/api/requests/open").json() is None
    assert store.request(rid)["status"] == "interrupted"


def test_hidden_parts_of_the_record_never_reach_a_screen(store):
    from tradecraft.web.app import screen_view
    rid = store.open_request("NVDA")
    v = screen_view({"request_id": rid, "pause": None, "done": False,
                     "state": {"symbol": "NVDA", "critic_rejected": {"output": {"verdict": "buy"}}}}, store)
    assert "critic_rejected" not in v["state"]


def test_real_steps_are_stage_1_and_stage_2_and_the_not_built_placeholder_is_gone():
    from tradecraft import stage2, steps as app_steps
    real = real_steps()
    assert real["thesis"] is stage2.thesis_step and real["user_thesis"] is stage2.user_thesis_step
    assert not hasattr(app_steps, "thesis_not_built")


def slow_app(store, monkeypatch):
    """An app whose Thesis step waits until released, as a model call would."""
    import threading
    patch(monkeypatch, False, snap=[c(), c(), c(dte=30)])
    monkeypatch.setattr(chain, "snapshot_info", lambda: {"file": "x", "taken_et": "2026-11-18T14:00-05:00"})
    release, started = threading.Event(), threading.Event()

    def thesis(state, ctx):
        ctx.store.trace(ctx.request_id, "run_t", "thesis", 0, "run_start", {})
        started.set()
        while not release.is_set() and not ctx.cancel.is_set():
            release.wait(0.02)
        if ctx.cancel.is_set():
            raise RuntimeError("stopped")
        ctx.store.trace(ctx.request_id, "run_t", "thesis", 1, "run_end", {"status": "ok"})
        return {"view": "bullish"}
    app = create_app(store, steps(thesis=thesis), SYMBOLS)
    app.state.workflow.bg_wait = 0.05                                 # do not hold the test for 1.5 seconds
    return TestClient(app), release, started


def wait_for(fn, seconds=3.0):
    import time
    end = time.time() + seconds
    while time.time() < end:
        v = fn()
        if v:
            return v
        time.sleep(0.02)
    raise AssertionError("timed out waiting")


def test_a_long_stage_runs_in_the_background_and_the_view_reports_each_agent(store, monkeypatch):
    client, release, started = slow_app(store, monkeypatch)
    rid = client.post("/api/requests", json={"symbol": "NVDA"}).json()["request_id"]
    v = client.post(f"/api/requests/{rid}/action", json={"action": "continue"}).json()
    started.wait(2)
    v = client.get("/api/requests/open").json()
    assert v["running"] is True and v["pause"] is None and v["done"] is False
    status = {p["agent"]: p["status"] for p in v["progress"]}
    assert status["evidence_retriever"] == "done" and status["thesis"] == "working" and status["validation"] == "waiting"
    assert [p["agent"] for p in v["progress"] if p["parallel"]] == ["fundamental_analyst", "regime_assessor", "technical_analyst"]
    assert client.post(f"/api/requests/{rid}/action", json={"action": "accept"}).status_code == 409   # still running
    release.set()
    v = wait_for(lambda: (lambda x: x if x["pause"] else None)(client.get("/api/requests/open").json()))
    assert v["pause"]["pause"] == "thesis" and v["running"] is False
    assert {p["status"] for p in v["progress"]} == {"done"}


def test_stop_while_the_agents_run_cancels_them_and_discards_the_pending_log(store, monkeypatch):
    client, release, started = slow_app(store, monkeypatch)
    rid = client.post("/api/requests", json={"symbol": "NVDA"}).json()["request_id"]
    client.post(f"/api/requests/{rid}/action", json={"action": "continue"})
    started.wait(2)
    client.post(f"/api/requests/{rid}/action", json={"action": "stop"})
    wait_for(lambda: client.get("/api/requests/open").json() is None)
    assert store.records(rid) == [] and store.pending(rid) == []
    assert store.request(rid)["status"] == "stopped_while_running"
    assert client.get("/api/home").json()["recent"] == []


def test_take_a_view_yourself_through_the_api_is_the_commit_point(client, store):
    rid = client.post("/api/requests", json={"symbol": "NVDA"}).json()["request_id"]
    client.post(f"/api/requests/{rid}/action", json={"action": "continue"})
    v = client.post(f"/api/requests/{rid}/action", json={"action": "own_view"}).json()
    assert "Choose a direction" in v["pause"]["error"] and not store.is_committed(rid)
    v = client.post(f"/api/requests/{rid}/action", json={"action": "own_view", "direction": "bearish"}).json()
    assert v["pause"]["pause"] == "contracts" and v["state"]["view"] == "bearish"
    assert v["state"]["user_thesis"]["thesis_origin"] == "user"
    assert [r["decision"] for r in store.records(rid)][-2:] == ["thesis_user_frozen", "contracts_ok"]
    assert store.records(rid)[0]["decision"] == "gate_pass"                    # the pending log was committed
    assert client.get("/api/home").json()["open"]["state"]["view"] == "bearish"
