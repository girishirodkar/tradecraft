"""The request workflow as one LangGraph graph (docs/build-plan.md, section 3).

LangGraph decides which node runs next. What each node does is a "step": a
plain function `step(state, ctx) -> dict` supplied from outside, so the stubs of
the skeleton are replaced by real steps without touching the wiring. Agent steps
call the harness (`run_agent`), which decides what an agent may do.

Rules the wiring enforces:
- A pause is a real stop: the graph saves its state and waits for the user's
  action. Pause nodes do nothing before `interrupt()`, because LangGraph re-runs
  a paused node from its start when it resumes.
- A step never raises. A failure becomes `stage_stop`; later nodes of the stage
  pass through and the stage's "stopped" pause offers what the design allows.
  (LangGraph discards every result of a parallel step if one node raises.)
- A failure is never a "no view".
- Records go to the pending log until stage 2 returns a view; that is the commit
  point. A request ending earlier leaves nothing in the permanent record.
- LangGraph has no hard cancel and no time limit for ordinary nodes, so Stop and
  the stage time limits use the harness's cancel signal and deadlines.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .. import settings
from ..storage import Store, next_daily_reset
from .state import RequestState, StepContext, StepFailed
from .stubs import DEFAULT_STEPS

ANALYSTS = ["fundamental_analyst", "regime_assessor", "technical_analyst"]
LABEL = {
    "retriever": "Evidence Retriever", "fundamental_analyst": "Fundamental Analyst",
    "regime_assessor": "Regime Assessor", "technical_analyst": "Technical Analyst",
    "thesis": "Thesis agent", "critic": "Critic", "passages": "Evidence Retriever",
}
# Stage 2's panel: (agent in the trace, node in the graph, label, runs in the parallel group)
PANEL = [("evidence_retriever", "retriever", "Evidence Retriever", False),
         ("fundamental_analyst", "fundamental_analyst", "Fundamental Analyst", True),
         ("regime_assessor", "regime_assessor", "Regime Assessor", True),
         ("technical_analyst", "technical_analyst", "Technical Analyst", True),
         ("thesis", "thesis", "Thesis agent", False)]
# Stage 4's panel: (agent in the trace, its role, node in the graph, label)
PANEL4 = [("evidence_retriever", "evidence_retriever.research", "passages", "Evidence Retriever"),
          ("critic", "critic.challenge", "critic", "Critic")]
STAGE4_KEYS = ["checklists", "question", "passages", "critic", "critic_check", "critic_unavailable",
               "critic_rejected", "readiness", "stage_stop"]


class Busy(Exception):
    """A request is already open. Only one request may be open at a time."""

    def __init__(self, message: str, request_id: str | None = None):
        super().__init__(message)
        self.request_id = request_id


def _blocked(s: RequestState) -> bool:
    return bool(s.get("stage_stop") or s.get("cancelled"))


class Workflow:
    def __init__(self, store: Store, steps: dict[str, Callable] | None = None, checkpointer=None,
                 clock: Callable[[], float] = time.time,
                 symbol_ok: Callable[[str], bool] | None = None, extras: dict | None = None):
        self.store = store
        self.steps = {**DEFAULT_STEPS, **(steps or {})}
        self.clock = clock
        self.symbol_ok = symbol_ok
        self.extras = extras or {}
        self._cancel: dict[str, threading.Event] = {}
        self._errors: dict[str, str] = {}
        self.bg_wait = 1.5                      # seconds a caller waits before being told "still running"
        self._running = threading.Lock()
        self.graph = self._build().compile(checkpointer=checkpointer or InMemorySaver())

    # ---- helpers ----------------------------------------------------------------------

    def _ctx(self, s: RequestState) -> StepContext:
        rid = s["request_id"]
        return StepContext(store=self.store, request_id=rid,
                           cancel=self._cancel.setdefault(rid, threading.Event()),
                           deadline=s.get("stage_deadline", float("inf")), extras=self.extras)

    def _rec(self, s: RequestState, stage: str, decision: str, by: str, payload: dict) -> None:
        self.store.write_record(s["request_id"], stage, decision, by, payload)

    def _deadline(self, stage: str) -> float:
        return self.clock() + settings.limits()["stages"][f"{stage}_seconds"]

    def _precheck(self, s: RequestState, stage: str, node: str) -> dict | None:
        """Cancel and the stage time limit, checked before every step of stages 2 and 4."""
        if self._ctx(s).cancel.is_set():
            return {"cancelled": True}
        if self.clock() > s.get("stage_deadline", float("inf")):
            n = stage[-1]
            mins = settings.limits()["stages"][f"{stage}_seconds"] // 60
            return {"stage_stop": StepFailed("stage_time_limit",
                                             f"Stage {n} reached its time limit of {mins} minutes.").as_stop(stage, node)}
        return None

    def _run(self, name: str, s: RequestState, stage: str) -> tuple[dict | None, dict | None]:
        """Run a step. Returns (output, stop). Never raises."""
        try:
            return self.steps[name](s, self._ctx(s)), None
        except StepFailed as e:
            return None, e.as_stop(stage, name)
        except Exception as e:  # noqa: BLE001 - a step must never raise into the graph
            who = LABEL.get(name, name.replace("_", " "))
            return None, StepFailed("error", f"The {who} step failed unexpectedly ({type(e).__name__}).",
                                    agent=name if name in LABEL else None).as_stop(stage, name)

    def _step_node(self, name: str, key: str, stage: str, skip: Callable | None = None):
        def node(s: RequestState):
            if _blocked(s):
                return {"events": []}
            if s.get(key) is not None:
                return {"events": [f"{name}:kept"]}          # already in the record (a retry)
            if skip and skip(s):
                return {"events": [f"{name}:skipped"]}
            pre = self._precheck(s, stage, name)
            if pre:
                return {**pre, "events": [f"{name}:not_run"]}
            out, stop = self._run(name, s, stage)
            if stop and self._ctx(s).cancel.is_set():      # Stop was pressed while the step ran
                return {"cancelled": True, "events": [f"{name}:cancelled"]}
            if stop:
                return {"stage_stop": stop, "events": [f"{name}:failed"]}
            return {key: out, "events": [name]}
        node.__name__ = name
        return node

    # ---- stage 1 ----------------------------------------------------------------------

    def _gate(self, s: RequestState):
        try:
            g = self.steps["gate"](s, self._ctx(s))
        except Exception as e:  # noqa: BLE001
            g = {"status": "not_checked", "override_allowed": False,
                 "message": f"The liquidity screen could not be run ({type(e).__name__})."}
        self._rec(s, "stage_1", f"gate_{g['status']}", "system",
                  {"liquidity_screen": g, "settings": s.get("gate_settings")})
        return {"gate": g, "events": ["gate"]}

    def _gate_pause(self, s: RequestState) -> Command[Literal["gate", "figures", "stopped", "gate_pause"]]:
        g = s["gate"]
        if g["status"] == "pass":
            actions = ["continue", "adjust", "stop"]
        elif g["status"] == "fail":
            actions = (["override"] if g.get("override_allowed", True) else []) + ["adjust", "stop"]
        else:  # not_checked: market closed and the symbol is not in the snapshot
            actions = ["continue", "stop"]
        ans = self._ask(s, "gate", actions)
        a = ans.get("action")
        if a == "leave":
            return self._leave("gate")
        if a not in actions:
            return Command(update={"pause_error": f"'{a}' is not available here."}, goto="gate_pause")
        if a == "stop":
            return Command(update={"status": "stopped_at_gate", "pause_error": None}, goto="stopped")
        if a == "adjust":
            return Command(update={"gate_settings": ans.get("settings"), "gate": None, "pause_error": None},
                           goto="gate")
        if a == "override":
            rationale = (ans.get("rationale") or "").strip()
            if not rationale:
                return Command(update={"pause_error": "A rationale is required to override."}, goto="gate_pause")
            decision = {"action": "override", "overruled": "liquidity_gate", "rationale": rationale}
        else:
            decision = {"action": "continue"}
        self._rec(s, "stage_1", a, "user", decision)
        return Command(update={"gate_decision": decision, "pause_error": None,
                               "stage_deadline": self._deadline("stage_2")}, goto="figures")

    # ---- stage 2 ----------------------------------------------------------------------

    def _analyst_node(self, name: str):
        def node(s: RequestState):
            if _blocked(s):
                return {"events": []}
            prev = (s.get("findings") or {}).get(name)
            if prev and prev.get("status") == "ok":
                return {"events": [f"{name}:kept"]}
            # Analysts run in parallel: each writes only its own findings entry.
            pre = self._precheck(s, "stage_2", name)
            if pre and pre.get("cancelled"):
                return {"findings": {name: {"status": "cancelled"}}, "events": [f"{name}:not_run"]}
            if pre:
                return {"findings": {name: {"status": "failed", "stop": pre["stage_stop"]}},
                        "events": [f"{name}:not_run"]}
            out, stop = self._run(name, s, "stage_2")
            if stop and self._ctx(s).cancel.is_set():
                return {"findings": {name: {"status": "cancelled"}}, "events": [f"{name}:cancelled"]}
            if stop:
                return {"findings": {name: {"status": "failed", "stop": stop}}, "events": [f"{name}:failed"]}
            return {"findings": {name: {"status": "ok", "output": out}}, "events": [name]}
        node.__name__ = name
        return node

    def _analysts_done(self, s: RequestState):
        if _blocked(s):
            return {"events": []}
        f = s.get("findings") or {}
        if any(f.get(n, {}).get("status") == "cancelled" for n in ANALYSTS):
            return {"cancelled": True, "events": ["analysts_done"]}
        failed = [n for n in ANALYSTS if f.get(n, {}).get("status") != "ok"]
        if failed:
            stop = dict(f[failed[0]]["stop"])
            stop["failed_agents"] = failed
            stop["kept"] = [n for n in ANALYSTS if n not in failed]
            return {"stage_stop": stop, "events": ["analysts_done:failed"]}
        return {"events": ["analysts_done"]}

    def _validate(self, s: RequestState) -> Command[Literal["thesis", "range_rule"]]:
        if _blocked(s) or s.get("thesis") is None or (s.get("validation") or {}).get("final"):
            return Command(update={"events": []}, goto="range_rule")
        pre = self._precheck(s, "stage_2", "validate")
        if pre:
            return Command(update={**pre, "events": ["validate:not_run"]}, goto="range_rule")
        v, stop = self._run("validate", s, "stage_2")
        if stop:
            return Command(update={"stage_stop": stop, "events": ["validate:failed"]}, goto="range_rule")
        # One return to the Thesis agent with the failed checks; a no-view answer is not returned.
        # The real Thesis step runs the check on the harness, which has already used the one
        # return ("in_harness"): the draft is then never returned a second time from here.
        if not v["ok"] and s.get("thesis_returns", 0) < 1 and not s["thesis"].get("no_view") \
                and not v.get("in_harness"):
            return Command(update={"validation": v, "thesis": None, "thesis_returns": 1,
                                   "events": ["validate:returned"]}, goto="thesis")
        return Command(update={"validation": {**v, "final": True}, "events": ["validate"]}, goto="range_rule")

    def _brief(self, s: RequestState):
        if _blocked(s):
            return {"events": []}
        t = s["thesis"]
        view = None if t.get("no_view") else t.get("view")
        if view is None and (s.get("range_rule") or {}).get("range_bound"):
            view = "range_bound"                       # set by rule in code, never by the agent
        self._rec(s, "stage_2", "thesis_drafted", "system",
                  {"view": view or "no_view", "thesis": t, "validation": s.get("validation"),
                   "range_rule": s.get("range_rule")})
        upd: dict = {"view": view, "events": ["brief"]}
        if view and not s.get("committed"):
            self.store.commit_request(s["request_id"])  # the commit point: the first view
            upd["committed"] = True
        return upd

    @staticmethod
    def _after_stage2(s: RequestState) -> str:
        return "stopped" if s.get("cancelled") else "stage2_stopped" if s.get("stage_stop") else "thesis_pause"

    def _stage_stopped_actions(self, s: RequestState, stage: str) -> list[str]:
        stop = s["stage_stop"]
        spend = stop["cause"] == "spend_limit"
        retry = [] if spend or (s.get("retries_used") or {}).get(stage) else ["retry"]
        if stage == "stage_2":
            return retry + ["stop"]
        return retry + ["checklists_only"] + ([] if spend else ["return"]) + ["stop"]

    def _stage2_stopped(self, s: RequestState) -> Command[Literal["figures", "stopped", "stage2_stopped"]]:
        actions = self._stage_stopped_actions(s, "stage_2")
        ans = self._ask(s, "stage2_stopped", actions, {"stop": s["stage_stop"]})
        a = ans.get("action")
        if a == "leave":
            return self._leave("stage2_stopped")
        if a not in actions:
            return Command(update={"pause_error": f"'{a}' is not available here."}, goto="stage2_stopped")
        self._rec(s, "stage_2", f"stage_stopped_{a}", "user", {"stop": s["stage_stop"]})
        if a == "retry":   # re-runs what did not finish; nodes whose output is in the record are kept
            return Command(update={"stage_stop": None, "pause_error": None,
                                   "retries_used": {**(s.get("retries_used") or {}), "stage_2": 1},
                                   "stage_deadline": self._deadline("stage_2")}, goto="figures")
        return Command(update={"status": "stopped_stage_2_failure", "pause_error": None}, goto="stopped")

    def _thesis_pause(self, s: RequestState) -> Command[Literal["contracts", "stopped", "thesis_pause"]]:
        # After a no view: stop (nothing is recorded), or take a view yourself.
        own = (s.get("thesis") or {}).get("own_view_allowed", True)    # needs evidence to rely on
        actions = ["accept", "reject"] if s.get("view") else ["stop"] + (["own_view"] if own else [])
        ans = self._ask(s, "thesis", actions)
        a = ans.get("action")
        if a == "leave":
            return self._leave("thesis")
        if a not in actions:
            return Command(update={"pause_error": f"'{a}' is not available here."}, goto="thesis_pause")
        if a == "stop":    # after no view: nothing is recorded
            return Command(update={"status": "stopped_no_view", "pause_error": None}, goto="stopped")
        if a == "own_view":
            entry = {k: ans.get(k) for k in ("direction", "horizon_days", "relied_on", "conditions")}
            try:
                mine = self.steps["user_thesis"]({**s, "user_input": entry}, self._ctx(s))
            except ValueError as e:        # the entry is not complete: say what is missing and wait
                return Command(update={"pause_error": str(e)}, goto="thesis_pause")
            decision = {"action": "own_view", "view": mine["view"], "at": self.clock()}
            self._rec(s, "stage_2", "thesis_user_frozen", "user", {"view": mine["view"], "thesis": mine})
            self.store.commit_request(s["request_id"])   # the commit point, in place of "the first view"
            return Command(update={"user_thesis": mine, "view": mine["view"], "committed": True,
                                   "thesis_decision": decision, "pause_error": None}, goto="contracts")
        decision = {"action": a, "view": s["view"], "at": self.clock()}
        self._rec(s, "stage_2", "thesis_frozen" if a == "accept" else "thesis_rejected", "user", decision)
        if a == "reject":
            return Command(update={"thesis_decision": decision, "status": "rejected_thesis",
                                   "pause_error": None}, goto="stopped")
        return Command(update={"thesis_decision": decision, "pause_error": None}, goto="contracts")

    # ---- stage 3 ----------------------------------------------------------------------

    def _contracts(self, s: RequestState):
        """Stage 3 is code. Its step returns an `outcome`:
        ok | market_closed | source_failed | no_candidates.
        There is no override in stage 3 (operator decision, 19 November 2026): a stage 1
        override carries forward, and legs still come only from passing contracts."""
        if s.get("contracts") is not None:
            return {"events": ["contracts:kept"]}
        out, stop = self._run("contracts", s, "stage_3")
        if stop:
            out = {"outcome": "source_failed", "message": stop["message"], "candidates": []}
        out = {**out}
        out.setdefault("outcome", "ok" if out.get("candidates") else "no_candidates")
        self._rec(s, "stage_3", f"contracts_{out['outcome']}", "system",
                  {"contracts": out, "params": s.get("contracts_params")})
        return {"contracts": out, "events": ["contracts"]}

    @staticmethod
    def _refetch(s: RequestState) -> int:
        """Retry and "Return to contracts" fetch the chain again; re-ranking and switching
        expiration reuse the one already fetched."""
        return (s.get("chain_fetch") or 0) + 1

    def _contracts_pause(self, s: RequestState) -> Command[Literal["contracts", "checklists", "stopped", "contracts_pause"]]:
        c = s["contracts"]
        outcome = c["outcome"]
        tries = (s.get("retries_used") or {}).get("stage_3", 0)
        actions = {
            "ok": ["continue", "update", "stop"],
            "market_closed": ["stop"],                       # expected, not a failure: no retry
            "source_failed": (["retry"] if tries < 3 else []) + ["stop"],   # code, costs nothing
            "no_candidates": ["update", "stop"],             # a result; switching expiration rebuilds
        }[outcome]
        ans = self._ask(s, "contracts", actions, {"outcome": outcome})
        a = ans.get("action")
        if a == "leave":
            return self._leave("contracts")
        if a not in actions:
            return Command(update={"pause_error": f"'{a}' is not available here."}, goto="contracts_pause")
        if a == "stop":
            return Command(update={"status": "stopped_at_contracts", "stop_reason": outcome,
                                   "pause_error": None}, goto="stopped")
        if a == "retry":
            self._rec(s, "stage_3", "retry", "user", {"after": outcome, "failed_source": c.get("failed_source"),
                                                      "message": c.get("message"), "attempt": tries + 1})
            return Command(update={"contracts": None, "pause_error": None, "chain_fetch": self._refetch(s),
                                   "retries_used": {**(s.get("retries_used") or {}), "stage_3": tries + 1}},
                           goto="contracts")
        if a == "update":  # expiration, ranking or max loss changed: re-run stage 3 on the chain already fetched
            before, params = s.get("contracts_params") or {}, ans.get("params") or {}
            changed = {k: {"from": before.get(k), "to": v} for k, v in params.items() if before.get(k) != v}
            self._rec(s, "stage_3", "update", "user", {"changed": changed, "params": params})
            return Command(update={"contracts_params": params, "contracts": None,
                                   "pause_error": None}, goto="contracts")
        asked = ans.get("selection") or {}
        by_id = {x.get("id"): x for x in c["candidates"]}
        chosen = by_id.get(asked.get("id")) if asked.get("id") else c["candidates"][0]   # none open = the top-ranked
        if chosen is None:
            # A filtered-out candidate is view-only in the demo.
            return Command(update={"pause_error": "That candidate cannot be selected."}, goto="contracts_pause")
        selection = {"id": chosen.get("id"), "candidate": chosen,
                     "contracts_proposed": asked.get("contracts"), "max_loss_for_trade": c.get("max_loss_for_trade"),
                     "best_fit_id": c.get("best_fit_id", c["candidates"][0].get("id")),
                     "priority": c.get("priority"), "expiry": c.get("expiry_chosen"),
                     "horizon_amendment": c.get("horizon_amendment"),
                     "not_selected": [x.get("id") for x in c["candidates"] if x.get("id") != chosen.get("id")]}
        self._rec(s, "stage_3", "selection", "user", {"selection": selection})
        return Command(update={"selection": selection, "pause_error": None, "stage4_started": self.clock(),
                               "stage_deadline": self._deadline("stage_4")}, goto="checklists")

    # ---- stage 4 ----------------------------------------------------------------------

    def _critic_check(self, s: RequestState) -> Command[Literal["critic", "readiness"]]:
        if _blocked(s) or s.get("critic") is None or s.get("critic_unavailable") \
                or (s.get("critic_check") or {}).get("final"):
            return Command(update={"events": []}, goto="readiness")
        pre = self._precheck(s, "stage_4", "critic_check")
        if pre:
            return Command(update={**pre, "events": ["critic_check:not_run"]}, goto="readiness")
        v, stop = self._run("critic_check", s, "stage_4")
        if stop:
            return Command(update={"stage_stop": stop, "events": ["critic_check:failed"]}, goto="readiness")
        # The real Critic step runs the check on the harness, which has already used the one
        # return ("in_harness"): the answer is then never returned a second time from here.
        if not v["ok"] and s.get("critic_returns", 0) < 1 and not v.get("in_harness"):
            return Command(update={"critic_check": v, "critic": None, "critic_returns": 1,
                                   "events": ["critic_check:returned"]}, goto="critic")
        upd: dict = {"critic_check": {**v, "final": True}, "events": ["critic_check"]}
        if not v["ok"]:    # failed twice: the user sees the checklists alone
            rule = "; ".join(x.rstrip(". ") for x in v.get("failed_checks") or []) or "a rule of the output check"
            rejected = {"output": s["critic"], "check": v}
            upd["critic_rejected"] = rejected          # stored with the check result, never displayed
            upd["critic"] = None
            upd["critic_unavailable"] = {
                "kind": "rejected",
                "reason": f"The Critic's output was rejected by the output check: {rule}. "
                          "It was returned once and failed again."}
            self.store.trace(s["request_id"], "workflow", "critic", 0, "critic_rejected", rejected)
        return Command(update=upd, goto="readiness")

    def _readiness(self, s: RequestState):
        if _blocked(s):
            return {"events": []}
        out, stop = self._run("readiness", s, "stage_4")
        if stop:
            return {"stage_stop": stop, "events": ["readiness:failed"]}
        self._rec(s, "stage_4", "challenge", "system",
                  {"checklists": s.get("checklists"), "question": s.get("question"),
                   "passages": s.get("passages"), "critic": s.get("critic"),
                   "critic_output_check": s.get("critic_check"),
                   "critic_model": (s.get("critic") or (s.get("critic_rejected") or {}).get("output") or {}).get("model"),
                   "critic_unavailable": s.get("critic_unavailable"),
                   "critic_rejected": s.get("critic_rejected"), "readiness": out,
                   "selection_id": (s.get("selection") or {}).get("id")})
        return {"readiness": out, "events": ["readiness"]}

    @staticmethod
    def _after_stage4(s: RequestState) -> str:
        return "stopped" if s.get("cancelled") else "stage4_stopped" if s.get("stage_stop") else "challenge_pause"

    def _stage4_stopped(self, s: RequestState) -> Command[Literal["checklists", "contracts", "stopped", "stage4_stopped"]]:
        actions = self._stage_stopped_actions(s, "stage_4")
        ans = self._ask(s, "stage4_stopped", actions, {"stop": s["stage_stop"]})
        a = ans.get("action")
        if a == "leave":
            return self._leave("stage4_stopped")
        if a not in actions:
            return Command(update={"pause_error": f"'{a}' is not available here."}, goto="stage4_stopped")
        self._rec(s, "stage_4", f"stage_stopped_{a}", "user", {"stop": s["stage_stop"]})
        if a == "stop":
            return Command(update={"status": "stopped_stage_4_failure", "pause_error": None}, goto="stopped")
        if a == "return":
            # A new selection: the chain is fetched again and the candidates rebuilt.
            return Command(update={**{k: None for k in STAGE4_KEYS}, "selection": None, "critic_returns": 0,
                                   "contracts": None, "chain_fetch": self._refetch(s),
                                   "pause_error": None}, goto="contracts")
        upd: dict = {"stage_stop": None, "pause_error": None, "stage_deadline": self._deadline("stage_4"),
                     "readiness": None}
        if a == "retry":
            upd["retries_used"] = {**(s.get("retries_used") or {}), "stage_4": 1}
        else:              # checklists only: say the Critic's output is not available, and why
            upd["critic_unavailable"] = {"kind": "stopped", "reason": s["stage_stop"]["message"]}
            upd["critic"] = None
        return Command(update=upd, goto="checklists")

    def _challenge_pause(self, s: RequestState) -> Command[Literal["decision_next", "contracts", "stopped", "challenge_pause"]]:
        actions = ["proceed", "return", "stop"]
        ans = self._ask(s, "challenge", actions)
        a = ans.get("action")
        if a == "leave":
            return self._leave("challenge")
        if a not in actions:
            return Command(update={"pause_error": f"'{a}' is not available here."}, goto="challenge_pause")
        not_ready = (s.get("readiness") or {}).get("label") == "Not ready"
        self._rec(s, "stage_4", f"challenge_{a}", "user",
                  {"readiness": s.get("readiness"), "proceeded_past_not_ready": a == "proceed" and not_ready})
        if a == "stop":
            return Command(update={"status": "stopped_at_challenge", "pause_error": None}, goto="stopped")
        if a == "return":  # a new selection; stage 4 runs again for it
            # A new selection: the chain is fetched again and the candidates rebuilt.
            return Command(update={**{k: None for k in STAGE4_KEYS}, "selection": None, "critic_returns": 0,
                                   "contracts": None, "chain_fetch": self._refetch(s),
                                   "pause_error": None}, goto="contracts")
        return Command(update={"challenge_decision": {"action": "proceed"}, "pause_error": None},
                       goto="decision_next")

    # ---- endings ----------------------------------------------------------------------

    def _decision_next(self, s: RequestState):
        """Stage 5 (decision and record) is not designed. The request ends here."""
        self.store.end_request(s["request_id"], "proceeded_to_decision")
        return {"status": "proceeded_to_decision", "events": ["decision_next"]}

    def _stopped(self, s: RequestState):
        rid = s["request_id"]
        status = s.get("status") or ("stopped_while_running" if s.get("cancelled") else "stopped")
        if self.store.is_committed(rid):
            self._rec(s, "request", "stopped", "user", {"where": status, "why": s.get("stop_reason")})
            self.store.end_request(rid, status)
        else:              # before the commit point: nothing reaches the permanent record
            self.store.discard_request(rid, status)
        return {"status": status, "events": ["stopped"]}

    @staticmethod
    def _leave(where: str) -> Command:
        """"Stop and leave" from Home or the product name: allowed at every pause.
        The usual rules follow: discarded before the first view, recorded after it."""
        return Command(update={"status": f"left_at_{where}", "pause_error": None}, goto="stopped")

    def _ask(self, s: RequestState, name: str, actions: list[str], extra: dict | None = None) -> dict:
        ans = interrupt({"pause": name, "actions": actions, "error": s.get("pause_error"), **(extra or {})})
        return ans if isinstance(ans, dict) else {"action": ans}

    # ---- wiring -----------------------------------------------------------------------

    def _build(self) -> StateGraph:
        g = StateGraph(RequestState)
        no_critic = lambda s: bool(s.get("critic_unavailable"))  # noqa: E731

        g.add_node("gate", self._gate)
        g.add_node("gate_pause", self._gate_pause)
        g.add_node("figures", self._step_node("figures", "figures", "stage_2"))
        g.add_node("retriever", self._step_node("retriever", "evidence", "stage_2"))
        g.add_node("grades", self._step_node("grades", "grades", "stage_2"))
        for a in ANALYSTS:
            g.add_node(a, self._analyst_node(a))
        g.add_node("analysts_done", self._analysts_done)
        g.add_node("thesis", self._step_node("thesis", "thesis", "stage_2"))
        g.add_node("validate", self._validate)
        g.add_node("range_rule", self._step_node("range_rule", "range_rule", "stage_2"))
        g.add_node("brief", self._brief)
        g.add_node("stage2_stopped", self._stage2_stopped)
        g.add_node("thesis_pause", self._thesis_pause)
        g.add_node("contracts", self._contracts)
        g.add_node("contracts_pause", self._contracts_pause)
        g.add_node("checklists", self._step_node("checklists", "checklists", "stage_4"))
        g.add_node("question", self._step_node("question", "question", "stage_4"))
        g.add_node("passages", self._step_node("passages", "passages", "stage_4", skip=no_critic))
        g.add_node("critic", self._step_node("critic", "critic", "stage_4", skip=no_critic))
        g.add_node("critic_check", self._critic_check)
        g.add_node("readiness", self._readiness)
        g.add_node("stage4_stopped", self._stage4_stopped)
        g.add_node("challenge_pause", self._challenge_pause)
        g.add_node("decision_next", self._decision_next)
        g.add_node("stopped", self._stopped)

        g.add_edge(START, "gate")
        g.add_edge("gate", "gate_pause")
        # stage 2: retriever, then the three analysts in parallel, merged for the Thesis agent
        g.add_edge("figures", "retriever")
        g.add_edge("retriever", "grades")
        for a in ANALYSTS:
            g.add_edge("grades", a)
        g.add_edge(ANALYSTS, "analysts_done")
        g.add_edge("analysts_done", "thesis")
        g.add_edge("thesis", "validate")           # validate returns the draft once, or moves on
        g.add_edge("range_rule", "brief")
        g.add_conditional_edges("brief", self._after_stage2, ["thesis_pause", "stage2_stopped", "stopped"])
        # stage 3
        g.add_edge("contracts", "contracts_pause")
        # stage 4
        g.add_edge("checklists", "question")
        g.add_edge("question", "passages")
        g.add_edge("passages", "critic")
        g.add_edge("critic", "critic_check")       # critic_check returns the answer once, or moves on
        g.add_conditional_edges("readiness", self._after_stage4,
                                ["challenge_pause", "stage4_stopped", "stopped"])
        g.add_edge("decision_next", END)
        g.add_edge("stopped", END)
        return g

    # ---- running ----------------------------------------------------------------------

    def _cfg(self, request_id: str) -> dict:
        return {"configurable": {"thread_id": request_id}, "recursion_limit": 100}

    def _invoke_bg(self, request_id: str, payload, wait: float) -> dict:
        """Run to the next pause on a background thread. Returns after `wait`
        seconds at most: a quick step has finished by then and the view shows its
        pause; a long one (the agents) is still running and the view says so."""
        if self._running.locked():
            raise Busy("This request is still running.", request_id)

        def work():
            try:
                self._invoke(request_id, payload)
            except Busy:
                pass
            except Exception as e:  # noqa: BLE001 - reported on the next view, never lost
                self._errors[request_id] = f"The workflow stopped unexpectedly ({type(e).__name__})."
        t = threading.Thread(target=work, name=f"workflow-{request_id}", daemon=True)
        t.start()
        t.join(wait)
        return self.view(request_id)

    def resume_bg(self, request_id: str, action: str, **fields) -> dict:
        """`resume` without holding the caller while agents run."""
        return self._invoke_bg(request_id, Command(resume={"action": action, **fields}), self.bg_wait)

    def progress(self, request_id: str) -> list[dict]:
        """Stage 2's panel: each agent as waiting, working, done or failed, read
        from the trace (an agent's run has started, or ended) and the nodes run."""
        rows = self.store.trace_rows(request_id=request_id)
        values = self.graph.get_state(self._cfg(request_id)).values or {}
        events = values.get("events", [])
        # Once the stage has stopped, an agent that never started is "not run", not "waiting".
        halted = bool(values.get("stage_stop") or values.get("cancelled")) and not self._running.locked()
        idle = "not run" if halted else "waiting"
        last: dict[str, dict] = {}
        for r in rows:
            if r["kind"] in ("run_start", "run_end"):
                last[r["agent"]] = r
        out = []
        for agent, node, label, group in PANEL:
            r = last.get(agent)
            if r is None:
                status = "done" if node in events else "failed" if f"{node}:failed" in events else idle
            elif r["kind"] == "run_start":
                status = "working"
            else:
                end = r["payload"]["status"]
                shown = end == "ok" or (end == "failed_validation" and agent == "thesis" and "thesis" in events)
                status = ("done" if shown else "timed out" if end == "timed_out" else
                          "not run" if end == "cancelled" else "failed")
            out.append({"agent": agent, "label": label, "status": status, "parallel": group})
        thesis = next(x for x in out if x["agent"] == "thesis")["status"]
        out.append({"agent": "validation", "label": "Validation check", "parallel": False,
                    "status": "done" if thesis == "done" or "validate" in events else idle})
        return out

    def progress4(self, request_id: str, values: dict) -> list[dict]:
        """Stage 4's panel: the Evidence Retriever, the Critic and the output check,
        read from the trace of the runs started since this selection."""
        import datetime as dt
        since = values.get("stage4_started") or 0
        events = values.get("events", [])
        cut = len(events) - 1 - events[::-1].index("contracts") if "contracts" in events else 0
        events = events[cut:]
        halted = bool(values.get("stage_stop") or values.get("cancelled")) and not self._running.locked()
        idle = "not run" if halted else "waiting"
        role_of, last = {}, {}
        for r in self.store.trace_rows(request_id=request_id):
            if r["kind"] == "run_start":
                role_of[r["run_id"]] = r["payload"].get("role")
            if r["kind"] in ("run_start", "run_end") and \
                    dt.datetime.fromisoformat(r["created_at"]).timestamp() >= since - 1:
                last[role_of.get(r["run_id"])] = r
        out = []
        for agent, role, node, label in PANEL4:
            r = last.get(role)
            if r is None:
                status = ("done" if node in events else "failed" if f"{node}:failed" in events
                          else "not run" if f"{node}:skipped" in events else idle)
            elif r["kind"] == "run_start":
                status = "working"
            else:
                end = r["payload"]["status"]
                status = ("done" if end == "ok" else "timed out" if end == "timed_out" else
                          "not run" if end == "cancelled" else "failed")
            out.append({"agent": agent, "label": label, "status": status, "parallel": False})
        critic = out[-1]["status"]
        out.append({"agent": "output_check", "label": "Output check", "parallel": False,
                    "status": "done" if critic in ("done", "failed") and "critic" in events else
                    "not run" if critic == "not run" else idle})
        return out

    def _invoke(self, request_id: str, payload) -> dict:
        if not self._running.acquire(blocking=False):
            raise Busy("This request is still running.", request_id)
        try:
            self.graph.invoke(payload, self._cfg(request_id))
        finally:
            self._running.release()
        return self.view(request_id)

    def start(self, symbol: str, gate_settings: dict | None = None) -> dict:
        """Open a request and run it to its first pause."""
        if self.symbol_ok is not None and not self.symbol_ok(symbol):
            raise ValueError("No listed symbol matches")
        already = self.store.open_request_ids()
        if already:        # one open request at a time, running or waiting at a pause
            raise Busy("An analysis is already open. Stop it before starting another.", already[-1])
        rid = self.store.open_request(symbol)
        self._cancel[rid] = threading.Event()
        return self._invoke(rid, {"request_id": rid, "symbol": symbol, "gate_settings": gate_settings,
                                  "findings": {}, "events": []})

    def resume(self, request_id: str, action: str, **fields) -> dict:
        """Answer the current pause and run to the next one (or to the end)."""
        return self._invoke(request_id, Command(resume={"action": action, **fields}))

    def request_stop(self, request_id: str) -> None:
        """Stop pressed while agents are running: they stop at their next step."""
        self._cancel.setdefault(request_id, threading.Event()).set()

    def leave(self, request_id: str) -> dict | None:
        """"Stop and leave": at a pause the request stops now; while agents are
        running they are told to stop and the request ends at their next step."""
        if self._running.locked():
            self.request_stop(request_id)
            return None
        return self.resume(request_id, "leave")

    def open_view(self) -> dict | None:
        """The open request, if any: what a reload or a second tab is shown."""
        ids = self.store.open_request_ids()
        return self.view(ids[-1]) if ids else None

    def recover_interrupted(self) -> list[str]:
        """Called once when the engine starts. A request left open by a restart is
        ended as "interrupted" under the pending-log rule; it is not resumed."""
        ended = []
        for rid in self.store.open_request_ids():
            if self.store.is_committed(rid):
                self.store.write_record(rid, "request", "interrupted", "system",
                                        {"why": "the engine restarted while the request was open"})
                self.store.end_request(rid, "interrupted")
            else:
                self.store.discard_request(rid, "interrupted")
            ended.append(rid)
        return ended

    def view(self, request_id: str) -> dict:
        snap = self.graph.get_state(self._cfg(request_id))
        pauses = [i.value for t in snap.tasks for i in t.interrupts]
        running = self._running.locked() and not pauses and bool(snap.next)
        return {"request_id": request_id, "pause": pauses[0] if pauses else None,
                "done": not snap.next, "running": running, "error": self._errors.get(request_id),
                "progress": (self.progress4(request_id, snap.values) if snap.values.get("selection")
                             else self.progress(request_id) if snap.values.get("gate_decision") else None),
                "state": snap.values}

    def mermaid(self) -> str:
        return self.graph.get_graph().draw_mermaid()
