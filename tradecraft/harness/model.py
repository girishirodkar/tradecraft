"""Model clients the harness can call.

`AnthropicModel` calls the Claude API through the official SDK. `ScriptedModel`
returns prepared replies, so the guardrail tests run without spending money and
give the same result every time.

Both return a `ModelReply`: content blocks as plain dicts (for the harness to
read), the raw content (to send back unchanged in the next turn, which keeps
thinking blocks valid), the stop reason and the token usage.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Protocol

from .. import settings


@dataclass
class ModelReply:
    blocks: list[dict]
    raw_content: Any
    stop_reason: str
    usage: dict
    model: str

    def text(self) -> str:
        return "".join(b.get("text", "") for b in self.blocks if b.get("type") == "text")

    def tool_uses(self) -> list[dict]:
        return [b for b in self.blocks if b.get("type") == "tool_use"]


class ModelError(Exception):
    """A model call failed. `retryable` errors (rate limit, server error,
    connection, timeout) are retried by the harness inside the run's deadline."""

    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class Model(Protocol):
    def call(self, params: dict, timeout: float) -> ModelReply: ...


def _usage(u: Any) -> dict:
    get = (lambda k: getattr(u, k, 0) or 0) if not isinstance(u, dict) else (lambda k: u.get(k, 0) or 0)
    return {
        "input_tokens": get("input_tokens"),
        "output_tokens": get("output_tokens"),
        "cache_read_tokens": get("cache_read_input_tokens"),
        "cache_write_tokens": get("cache_creation_input_tokens"),
    }


class AnthropicModel:
    """The Claude API. The SDK's own retries are switched off: each retry would
    get the full timeout again and could overrun the agent's time limit. The
    harness retries instead, inside the deadline (config/limits.json)."""

    def __init__(self):
        import anthropic  # imported here so the tests need no key

        key = settings.secret("ANTHROPIC_API_KEY")
        if not key:
            raise ModelError("ANTHROPIC_API_KEY is not set in .env")
        self._anthropic = anthropic
        self._client = anthropic.Anthropic(api_key=key, max_retries=0)

    def call(self, params: dict, timeout: float) -> ModelReply:
        a = self._anthropic
        try:
            r = self._client.with_options(timeout=max(timeout, 1.0)).messages.create(**params)
        except a.APITimeoutError as e:
            raise ModelError("the model did not answer in time", retryable=True) from e
        except a.RateLimitError as e:
            raise ModelError("rate limited by the API", retryable=True) from e
        except a.BadRequestError as e:
            raise ModelError(f"the API rejected the request: {settings.redact(str(e.message))}") from e
        except a.APIStatusError as e:
            raise ModelError(f"API error {e.status_code}", retryable=e.status_code >= 500) from e
        except a.APIConnectionError as e:
            raise ModelError("could not reach the API", retryable=True) from e
        blocks = [b.model_dump(mode="json", exclude_none=True) for b in r.content]
        return ModelReply(blocks=blocks, raw_content=r.content, stop_reason=r.stop_reason or "",
                          usage=_usage(r.usage), model=r.model)


@dataclass
class ScriptedModel:
    """Replies from a list, in order. Each reply is a dict:
    {"text": "..."} for a final answer, or {"tool_uses": [{"name":..., "input":{...}}]},
    optionally with "stop_reason" and "usage"; or {"error": "...", "retryable": True}
    to fail the call. "before" may hold a function run first (e.g. to move a test
    clock). Records every request it receives, and the timeout it was given."""

    replies: list[dict]
    model: str = "scripted"
    requests: list[dict] = field(default_factory=list)
    timeouts: list[float] = field(default_factory=list)

    def call(self, params: dict, timeout: float) -> ModelReply:
        self.requests.append(copy.deepcopy(params))  # as sent; the harness keeps appending
        self.timeouts.append(timeout)
        if not self.replies:
            raise ModelError("scripted model has no replies left")
        r = self.replies.pop(0)
        if r.get("before"):
            r["before"]()
        if r.get("error"):
            raise ModelError(r["error"], retryable=r.get("retryable", False))
        blocks: list[dict] = []
        if r.get("text") is not None:
            blocks.append({"type": "text", "text": r["text"]})
        for i, tu in enumerate(r.get("tool_uses", [])):
            blocks.append({"type": "tool_use", "id": f"toolu_{len(self.requests)}_{i}",
                           "name": tu["name"], "input": tu.get("input", {})})
        stop = r.get("stop_reason") or ("tool_use" if r.get("tool_uses") else "end_turn")
        usage = r.get("usage", {"input_tokens": 1000, "output_tokens": 200})
        return ModelReply(blocks=blocks, raw_content=blocks, stop_reason=stop,
                          usage=_usage(usage), model=params.get("model", self.model))
