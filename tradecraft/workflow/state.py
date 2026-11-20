"""The request record that flows through the graph, and how a step reports failure."""
from __future__ import annotations

import operator
import threading
from dataclasses import dataclass, field
from typing import Annotated, Any

from typing_extensions import TypedDict

from ..harness.guards import wrap_untrusted


class RequestState(TypedDict, total=False):
    request_id: str
    symbol: str
    # stage 1
    gate_settings: dict | None
    gate: dict | None
    gate_decision: dict
    # stage 2
    figures: dict | None
    evidence: dict | None
    grades: dict | None
    findings: Annotated[dict, operator.or_]     # one entry per analyst, written in parallel
    thesis: dict | None
    validation: dict | None
    thesis_returns: int
    range_rule: dict | None
    view: str | None                            # bullish | bearish | range_bound | None (no view)
    committed: bool                             # the pending log has been committed (first view)
    thesis_decision: dict
    user_thesis: dict | None                    # entered by the user after a no view ("Take a view yourself")
    # stage 3
    contracts_params: dict | None
    chain_fetch: int                            # raised to fetch the option chain again (Retry, Return to contracts)
    contracts: dict | None
    selection: dict | None
    # stage 4
    checklists: dict | None
    question: dict | None
    passages: dict | None
    critic: dict | None
    critic_check: dict | None
    critic_returns: int
    critic_unavailable: dict | None
    critic_rejected: dict | None                # the rejected output and its check: stored, never displayed
    readiness: dict | None
    stage4_started: float                       # when this selection was made (stage 4's panel)
    challenge_decision: dict
    # control
    stage_deadline: float                       # time.time() at which the current stage's limit ends
    stage_stop: dict | None                     # set when a stage stops on a failure or a limit
    retries_used: dict                          # manual retries used, per stage
    cancelled: bool
    pause_error: str | None
    stop_reason: str | None
    status: str
    events: Annotated[list, operator.add]       # which nodes ran, in order (panel and tests)


# Parts of the record that are stored but must never be sent to a screen.
HIDDEN_FROM_SCREEN = {"critic_rejected"}


class StepFailed(Exception):
    """A step could not finish. `cause` is one of: agent_failed, timed_out,
    stage_time_limit, spend_limit, error. A failure is never a 'no view'."""

    def __init__(self, cause: str, message: str, agent: str | None = None, scope: str | None = None,
                 resets_at: str | None = None):
        super().__init__(message)
        self.cause, self.message, self.agent = cause, message, agent
        self.scope, self.resets_at = scope, resets_at     # spend_limit: "request" or "day"

    def as_stop(self, stage: str, node: str) -> dict:
        return {"stage": stage, "node": node, "cause": self.cause, "message": self.message,
                "agent": self.agent, "scope": self.scope, "resets_at": self.resets_at}


@dataclass
class StepContext:
    """What a step may use besides the request record."""
    store: Any
    request_id: str
    cancel: threading.Event
    deadline: float                             # the stage deadline, as time.time()
    extras: dict = field(default_factory=dict)  # registry, model clients, ... (set by the app)


def findings_for_thesis(findings: dict) -> str:
    """The analysts' findings as handed to the Thesis agent: wrapped as data.

    Analysts read filings and news, and their findings can quote that text, so a
    planted instruction could travel second-hand. The Thesis agent receives the
    findings labelled as data, the same way a filing is (harness review, item 4).
    Failed analysts are left out; the workflow never reaches the Thesis agent
    with one missing."""
    import json
    parts = []
    for name in sorted(findings):
        f = findings[name]
        if f.get("status") == "ok":
            parts.append(wrap_untrusted(json.dumps(f.get("output"), default=str, ensure_ascii=False),
                                        f"findings of the {name.replace('_', ' ')}"))
    return "\n\n".join(parts)
