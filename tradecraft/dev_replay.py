"""Development only: the application with stage 2 replayed from saved outputs.

    .venv/bin/python -m uvicorn tradecraft.dev_replay:app --host 127.0.0.1 --port 8322

A build tool, not a product feature (operator decision, 19 November 2026). It
lets the stage 3 and 4 screens be checked without a model call: the gate and
stage 3 run for real, and each stage 2 step returns what a live run of
19 November saved in data/runs-2026-11-19/. In stage 4 both checklists, the
question, the fresh quotes and the readiness line run for real; the Evidence
Retriever and the Critic are served from what the first live run of that symbol
and candidate saved in data/stage4-saved/. Until one exists the Critic step
fails, and the challenge shows its stage-stopped screen. Nothing is asked of a model, and
records go to a separate database (data/replay.sqlite3), never the real one.
The saved theses predate some of stage 2's final rules; they are stand-ins for
checking later stages, not results.
"""
from __future__ import annotations

import json

from . import settings, stage2, stage3, stage4
from .stage1 import gate_step
from .storage import Store
from .workflow.state import StepFailed

RUNS = "runs-2026-11-19"
FOLDERS = ["run4", "run3", "run43"]        # newest first; the six-symbol run sits beside them


SWITCH = "replay_mode.txt"


def _mode() -> str:
    """A switch for states that cannot be had on demand, read on every call from
    data/replay_mode.txt: "closed" (the market is closed: the snapshot is used),
    "nosnap" (closed, and the snapshot does not hold the symbol), "fail" (the live
    chain cannot be fetched). For stage 4: "critic_fail" (the Critic times out),
    "critic_reject" (its output fails the output check twice), "nopassages"
    (nothing is retrieved). Anything else, or no file: as things are."""
    p = settings.data_dir() / SWITCH
    return p.read_text().strip().lower() if p.exists() else ""


def _install_switch() -> None:
    from .data import chain, session
    status, live, snapshot = session.status, chain.live, chain.snapshot

    def forced_status(when=None):
        s = status(when)
        return {**s, "open": False, "reason": "replay: forced closed"} if _mode() in ("closed", "nosnap") else s

    def forced_live(symbol, store=None):
        if _mode() == "fail":
            raise chain.ChainUnavailable("Cboe delayed quotes: replay switch set to fail")
        return live(symbol, store)

    def forced_snapshot(symbol):
        if _mode() == "nosnap":
            raise chain.ChainUnavailable(f"{symbol.upper()} is not in the daily snapshot")
        return snapshot(symbol)
    session.status, chain.live, chain.snapshot = forced_status, forced_live, forced_snapshot


def saved(symbol: str) -> dict:
    base = settings.data_dir() / RUNS
    for p in [base / f / f"{symbol}.json" for f in FOLDERS] + [base / f"live_stage2.py.{symbol}.json"]:
        if p.exists():
            return json.loads(p.read_text())
    raise StepFailed("error", f"Replay: no saved stage 2 output for {symbol}.")


def _part(key: str):
    def step(state, ctx):
        return saved(state["symbol"])[key]
    return step


def _analyst(name: str):
    def step(state, ctx):
        f = saved(state["symbol"])["findings"][name]
        if f.get("status") != "ok":
            raise StepFailed("agent_failed", f"Replay: the saved run has no output for the {name}.", agent=name)
        return f["output"]
    return step


def _thesis(state, ctx):
    """The saved thesis. Runs saved before "Take a view yourself" was wired lack what its
    screen offers; that part is code, so it is rebuilt here from the saved findings."""
    t = saved(state["symbol"])["thesis"]
    if t.get("no_view") and "own_view_options" not in t:
        t["own_view_options"] = stage2.own_view_options(state, t)
        t.setdefault("own_view_allowed", bool(t["own_view_options"]["evidence"]))
    return t


def _saved4(state) -> dict:
    p = stage4.saved_path(state)
    return json.loads(p.read_text()) if p.exists() else {}


def _passages(state, ctx):
    c = stage4.Case(state)
    topics = stage4.topics_for(c, state.get("question") or stage4.restate(c))
    kept = _saved4(state).get("passages")
    if _mode() == "nopassages" or not kept:
        return stage4.no_passages("replay: forced" if _mode() == "nopassages" else
                                  "replay: no live run of this symbol and candidate has been saved", topics=topics)
    return kept


def _critic(state, ctx):
    kept = _saved4(state).get("critic")
    if _mode() == "critic_fail":
        raise StepFailed("timed_out", "The Critic timed out after 180 seconds (replay switch).", agent="critic")
    if _mode() == "critic_reject":
        return {"rejected": True, "output": kept or {}, "model": "replay",
                "check": {"ok": False, "failed_checks": ["Objection 1 cites no grounds."], "returned_once": True,
                          "in_harness": True}}
    if not kept:
        raise StepFailed("agent_failed", f"Replay: no saved Critic output for {state['symbol']} and this candidate. "
                                         "The first live run of the pair saves one.", agent="critic")
    return kept


def replay_steps() -> dict:
    return {"gate": gate_step, "contracts": stage3.contracts_step, "user_thesis": stage2.user_thesis_step,
            **stage4.STEPS, "passages": _passages, "critic": _critic,
            "figures": _part("figures"), "retriever": _part("evidence"), "grades": _part("grades"),
            "fundamental_analyst": _analyst("fundamental_analyst"), "regime_assessor": _analyst("regime_assessor"),
            "technical_analyst": _analyst("technical_analyst"), "thesis": _thesis,
            "validate": lambda state, ctx: dict(state["thesis"]["validation"]),
            "range_rule": _part("range_rule")}


def __getattr__(name: str):
    if name == "app":
        global _app
        try:
            return _app
        except NameError:
            from .web.app import create_app
            _install_switch()
            from . import research
            research.ensure_current()
            _app = create_app(store=Store(settings.data_dir() / "replay.sqlite3"), steps=replay_steps())
            return _app
    raise AttributeError(name)
