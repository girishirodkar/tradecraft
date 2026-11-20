"""Run any agent from its configuration.

One function, `run_agent`, does the whole job for every agent: it offers only
the allowlisted tools, runs the reason-act-observe loop, enforces the run
limits, wraps outside text as data, validates the answer against the agent's
output format and guards (returning it once on failure), and writes every
step to the trace. LangGraph decides which agent runs next; this decides what
an agent may do.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable

from pydantic import BaseModel, ValidationError

from .. import settings
from ..storage import Store
from . import spend
from .guards import UNTRUSTED_RULE, OutputGuard, find_injection, wrap_untrusted
from .model import Model, ModelError
from .tools import ToolContext, ToolRegistry, ToolUnavailable, result_text, truncate

DISPLAY = {
    "evidence_retriever": "Evidence Retriever",
    "fundamental_analyst": "Fundamental Analyst",
    "regime_assessor": "Regime Assessor",
    "technical_analyst": "Technical Analyst",
    "thesis": "Thesis agent",
    "critic": "Critic",
}


@dataclass
class AgentConfig:
    """One agent = one configuration on the shared harness."""
    name: str                      # key into config/limits.json and config/models.json
    role: str                      # which configuration, e.g. "evidence_retriever.company"
    instructions: str
    output_model: type[BaseModel]
    tools: list[str] = field(default_factory=list)
    output_guards: list[OutputGuard] = field(default_factory=list)
    model: str | None = None       # default: config/models.json
    effort: str | None = None      # low | medium | high | xhigh | max; None = model default

    def model_id(self) -> str:
        return self.model or settings.models()["agents"][self.name]["model"]

    def display(self) -> str:
        return DISPLAY.get(self.name, self.name)

    def fingerprint(self) -> str:
        """Identifies this exact configuration: instructions, output format, checks,
        tools, model and effort. Written to every run's trace, so each output can be
        traced to the prompt version that produced it (CLAUDE.md: log every
        configuration tried)."""
        parts = {
            "name": self.name, "role": self.role, "instructions": self.instructions.strip(),
            "output_schema": self.output_model.model_json_schema(),
            "output_guards": [g.__name__ for g in self.output_guards],
            "tools": sorted(self.tools), "model": self.model_id(), "effort": self.effort,
        }
        return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:12]


@dataclass
class AgentResult:
    status: str        # ok | failed_validation | timed_out | spend_limit | model_error | refused | cancelled | turn_limit
    agent: str
    run_id: str
    message: str
    output: BaseModel | None = None
    errors: list[str] = field(default_factory=list)
    unavailable_inputs: list[dict] = field(default_factory=list)
    tool_calls: int = 0
    model_calls: int = 0
    cost_usd: float = 0.0
    config_fingerprint: str = ""
    rejected_output: BaseModel | None = None   # a readable answer that failed its checks twice (never "ok")

    @property
    def returned(self) -> bool:
        """The answer was returned to the agent once (the one return was used)."""
        return bool(self.errors)

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def _parse_json(text: str) -> dict:
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end < start:
        raise ValueError("the answer contains no JSON object")
    return json.loads(t[start:end + 1])


def _answer_format(model: type[BaseModel]) -> str:
    schema = json.dumps(model.model_json_schema(), separators=(",", ":"))
    return ("When you have finished, answer with one JSON object and nothing else, "
            f"matching this JSON schema:\n{schema}")


def _tokens(obj, chars_per_token: int) -> int:
    """Rough token estimate from the size of the JSON text. Used only to keep a call
    under the input cap; the real count comes back in the reply's usage."""
    def plain(x):
        if hasattr(x, "model_dump"):
            return x.model_dump(mode="json", exclude_none=True)
        if isinstance(x, list):
            return [plain(v) for v in x]
        if isinstance(x, dict):
            return {k: plain(v) for k, v in x.items()}
        return x
    return len(json.dumps(plain(obj), default=str)) // chars_per_token + 1


def run_agent(config: AgentConfig, task: str, *, model: Model, registry: ToolRegistry | None = None,
              store: Store | None = None, request_id: str | None = None,
              cancel: threading.Event | None = None,
              clock: Callable[[], float] = time.monotonic,
              sleep: Callable[[float], None] = time.sleep) -> AgentResult:
    L = settings.limits()
    lim = L["agents"][config.name]
    cpt = L["text"]["chars_per_token_estimate"]
    input_cap = L["text"]["max_input_tokens_per_call"]
    registry = registry or ToolRegistry()
    store = store or Store()
    run_id = "run_" + uuid.uuid4().hex[:12]
    res = AgentResult(status="", agent=config.name, run_id=run_id, message="",
                      config_fingerprint=config.fingerprint())
    step = 0

    def tr(kind: str, payload: dict) -> None:
        store.trace(request_id, run_id, config.name, step, kind, payload)

    def end(status: str, message: str, output: BaseModel | None = None) -> AgentResult:
        res.status, res.message, res.output = status, message, output
        tr("run_end", {"status": status, "message": message, "tool_calls": res.tool_calls,
                       "model_calls": res.model_calls, "cost_usd": round(res.cost_usd, 6),
                       "unavailable_inputs": res.unavailable_inputs})
        return res

    max_tools = lim["max_tool_calls"]
    allowed = list(config.tools) if max_tools > 0 else []
    schemas = registry.schemas(allowed) if allowed else []
    tool_chars = L["text"]["max_tool_result_tokens"] * cpt

    system = "\n\n".join([config.instructions.strip(), UNTRUSTED_RULE, _answer_format(config.output_model)])
    base: dict = {"model": config.model_id(), "max_tokens": lim["max_output_tokens"], "system": system}
    if schemas:
        base["tools"] = schemas
    if config.effort:
        base["output_config"] = {"effort": config.effort}

    tr("run_start", {"role": config.role, "config_fingerprint": res.config_fingerprint,
                     "model": base["model"], "effort": config.effort, "tools": allowed, "limits": lim,
                     "input_cap_tokens": input_cap, "task": task[:4000]})

    deadline = clock() + lim["time_seconds"]
    # Tools run on the real clock: they get whatever time the run has left.
    tool_deadline = time.monotonic() + lim["time_seconds"]
    ctx = ToolContext(store=store, request_id=request_id, run_id=run_id, agent=config.name, limits=L,
                      deadline=tool_deadline)
    pool = cf.ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"tool-{config.name}")
    messages: list[dict] = [{"role": "user", "content": task}]
    seen: dict[str, int] = {}
    retries_left = L["retries"]["validation_retries"]
    api_retries = L["retries"]["api_retries"]
    force_answer = False
    max_turns = max_tools + retries_left + 4

    if _tokens([system, base.get("tools"), messages], cpt) > input_cap:
        return end("input_limit", f"The {config.display()} was not started: its input is larger than "
                                  f"the limit of {input_cap:,} tokens per call.")

    def call_tool(tool, args) -> tuple[object, str | None]:
        """Run a tool with one retry, never past the run's deadline."""
        reason = None
        for attempt in range(1 + L["retries"]["tool_retries"]):
            left = ctx.remaining()
            if left <= 0:
                return None, "the agent's time limit was reached before this input could be fetched"
            fut = pool.submit(tool.fn, ctx, **args)
            try:
                return fut.result(timeout=left), None
            except cf.TimeoutError:
                tr("limit", {"limit": "time_seconds", "tool": tool.name,
                             "outcome": "tool stopped waiting at the agent's deadline"})
                return None, "the source did not answer within the agent's time limit"
            except ToolUnavailable as e:
                return None, str(e)
            except Exception as e:  # noqa: BLE001 - any tool failure becomes "not available"
                reason = f"{type(e).__name__}: {settings.redact(str(e))[:300]}"
                tr("tool_error", {"tool": tool.name, "attempt": attempt + 1, "error": reason})
        return None, reason

    def run_tool(tu: dict) -> dict:
        nonlocal force_answer
        name, args = tu.get("name", ""), tu.get("input") or {}
        tr("tool_call", {"tool": name, "input": args})
        tool = registry.get(name)
        if name not in allowed or tool is None:
            tr("guardrail", {"guard": "tool_allowlist", "outcome": "refused", "tool": name,
                             "allowed": allowed})
            return {"type": "tool_result", "tool_use_id": tu["id"], "is_error": True,
                    "content": f"The tool '{name}' is not available to this agent. "
                               f"Available tools: {', '.join(allowed) or 'none'}."}
        key = name + json.dumps(args, sort_keys=True, default=str)
        if key in seen:
            tr("guardrail", {"guard": "repeated_call", "outcome": "refused", "tool": name,
                             "first_step": seen[key]})
            return {"type": "tool_result", "tool_use_id": tu["id"], "is_error": True,
                    "content": f"You already called {name} with this input (step {seen[key]}). "
                               "Use that result; it has not changed."}
        if res.tool_calls >= max_tools:
            force_answer = True
            tr("limit", {"limit": "max_tool_calls", "value": max_tools, "outcome": "refused; agent told to answer"})
            return {"type": "tool_result", "tool_use_id": tu["id"], "is_error": True,
                    "content": f"The tool-call limit for this agent ({max_tools}) has been reached. "
                               "Answer now with what you have."}
        res.tool_calls += 1
        seen[key] = step
        value, reason = call_tool(tool, args)
        if reason is not None:
            res.unavailable_inputs.append({"tool": name, "input": args, "reason": reason})
            tr("tool_result", {"tool": name, "available": False, "reason": reason})
            return {"type": "tool_result", "tool_use_id": tu["id"], "is_error": True,
                    "content": f"Not available: {reason}. Record this input as unavailable and continue."}
        text = settings.redact(result_text(value))
        text, cut = truncate(text, tool_chars)
        if cut:
            tr("limit", {"limit": "max_tool_result_tokens", "tool": name, "outcome": "truncated with a note"})
        if tool.untrusted:
            found = find_injection(text)
            if found:
                tr("guardrail", {"guard": "untrusted_text", "tool": name, "outcome": "labelled as data, not followed",
                                 "instruction_like_text": found})
            text = wrap_untrusted(text, tool.source or name)
        tr("tool_result", {"tool": name, "available": True, "truncated": cut, "untrusted": tool.untrusted,
                           "chars": len(text), "excerpt": text[:1500]})
        return {"type": "tool_result", "tool_use_id": tu["id"], "content": text}

    def fit_input_cap(results: list[dict], used: int) -> list[dict]:
        """Keep the next call under the input cap: shrink the new tool results to
        fit and tell the agent to answer with what it has."""
        nonlocal force_answer
        needed = _tokens(results, cpt)
        if used + needed <= input_cap:
            return results
        force_answer = True
        room = max(0, input_cap - used - 300 * len(results))
        share = (room * cpt) // max(1, len(results))
        note = (f"[Input limit: the next call would exceed {input_cap:,} tokens, so this result was "
                "shortened. Answer now with what you have.]")
        out = []
        for r in results:
            body = r["content"] if isinstance(r["content"], str) else json.dumps(r["content"])
            r = dict(r, content=(body[:share] + "\n" + note) if share > 200 else note)
            out.append(r)
        tr("limit", {"limit": "max_input_tokens_per_call", "value": input_cap, "estimated": used + needed,
                     "outcome": "tool results shortened; agent told to answer"})
        return out

    def call_model(params: dict) -> object:
        """One model call, retried on rate limits, server and connection errors,
        with an increasing pause, never past the deadline."""
        for attempt in range(1 + api_retries):
            remaining = deadline - clock()
            if remaining <= 0:
                raise ModelError("the time limit was reached while waiting for the model")
            try:
                return model.call(params, timeout=remaining)
            except ModelError as e:
                tr("error", {"error": str(e), "attempt": attempt + 1, "retryable": e.retryable})
                if not e.retryable or attempt == api_retries:
                    raise
                pause = min(2.0 ** attempt, max(0.0, deadline - clock() - 1.0))
                if pause <= 0:
                    raise
                sleep(pause)
        raise ModelError("unreachable")

    try:
        while True:
            step += 1
            if cancel is not None and cancel.is_set():
                return end("cancelled", f"The {config.display()} was stopped by the user.")
            if deadline - clock() <= 0:
                tr("limit", {"limit": "time_seconds", "value": lim["time_seconds"]})
                return end("timed_out", f"The {config.display()} timed out after {lim['time_seconds']} seconds.")
            why = spend.stop_reason(store, request_id)
            if why:
                tr("limit", {"limit": "spend", "detail": why})
                return end("spend_limit", f"The {config.display()} stopped before its next model call: {why}.")
            if res.model_calls >= max_turns:
                tr("limit", {"limit": "model_turns", "value": max_turns})
                return end("turn_limit", f"The {config.display()} used {max_turns} model turns without a valid answer.")

            params = dict(base, messages=messages)
            if schemas and (force_answer or res.tool_calls >= max_tools):
                params["tool_choice"] = {"type": "none"}
            t0 = time.monotonic()
            try:
                reply = call_model(params)
            except ModelError as e:
                if deadline - clock() <= 0:
                    tr("limit", {"limit": "time_seconds", "value": lim["time_seconds"]})
                    return end("timed_out", f"The {config.display()} timed out after {lim['time_seconds']} seconds.")
                return end("model_error", f"The {config.display()} could not complete: {e}.")
            res.model_calls += 1
            cost = spend.cost_usd(reply.model, reply.usage)
            res.cost_usd += cost
            store.add_spend(request_id, run_id, config.name, reply.model, reply.usage, cost)
            tr("model_call", {"model": reply.model, "stop_reason": reply.stop_reason, "usage": reply.usage,
                              "cost_usd": round(cost, 6), "seconds": round(time.monotonic() - t0, 2),
                              "text": reply.text()[:4000],
                              "tool_uses": [{"name": t["name"], "input": t.get("input")} for t in reply.tool_uses()]})

            if reply.stop_reason == "refusal":
                return end("refused", f"The {config.display()} declined the request.")
            messages.append({"role": "assistant", "content": reply.raw_content})
            u = reply.usage
            used = (u.get("input_tokens", 0) + u.get("cache_read_tokens", 0) + u.get("cache_write_tokens", 0)
                    + u.get("output_tokens", 0))

            if reply.stop_reason == "tool_use" and reply.tool_uses():
                results = [run_tool(tu) for tu in reply.tool_uses()]
                messages.append({"role": "user", "content": fit_input_cap(results, used)})
                continue

            # A final answer: validate it.
            errors: list[str] = []
            parsed: BaseModel | None = None
            if reply.stop_reason == "max_tokens":
                errors = [f"The answer was cut off at the output limit of {lim['max_output_tokens']} tokens. "
                          "Give a shorter answer."]
            else:
                try:
                    parsed = config.output_model.model_validate(_parse_json(reply.text()))
                except (ValueError, ValidationError) as e:
                    errors = [f"The answer does not match the required format: {str(e)[:1500]}"]
                if parsed is not None:
                    for g in config.output_guards:
                        for msg in g(parsed):
                            errors.append(msg)
                            tr("guardrail", {"guard": g.__name__, "outcome": "rejected", "detail": msg})
            if not errors:
                tr("validation", {"ok": True})
                return end("ok", f"The {config.display()} finished.", parsed)

            res.errors = errors
            tr("validation", {"ok": False, "errors": errors, "retry": retries_left > 0})
            if retries_left <= 0:
                res.rejected_output = parsed
                return end("failed_validation",
                           f"The {config.display()}'s answer failed validation after one return: {errors[0]}")
            retries_left -= 1
            force_answer = True
            messages.append({"role": "user", "content":
                             "Your answer was rejected by the validation check for these reasons:\n- "
                             + "\n- ".join(errors)
                             + "\nCorrect them and answer again with the JSON object only."})
    finally:
        # Do not wait for a tool still running past the deadline; its result is discarded.
        pool.shutdown(wait=False, cancel_futures=True)
