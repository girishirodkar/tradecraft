"""Tool registry. An agent can call only the tools its configuration names.

A tool is a plain function. It receives a `ToolContext` (the store, the request
and run ids, the limits) and the model's input. Tools that return text from an
outside source (filings, news, provider responses, the research corpus) are
marked `untrusted`; the harness wraps their results as data.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from .. import settings


@dataclass
class ToolContext:
    store: Any
    request_id: str | None
    run_id: str
    agent: str
    limits: dict
    deadline: float = float("inf")          # time.monotonic() value at which the agent's run ends

    def remaining(self) -> float:
        """Seconds left in the agent's run. Pass it as the timeout of any fetch."""
        import time
        return max(0.0, self.deadline - time.monotonic())

    def max_document_chars(self) -> int:
        t = self.limits["text"]
        return t["max_document_tokens"] * t["chars_per_token_estimate"]


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    fn: Callable[..., Any]
    untrusted: bool = False
    source: str = ""

    def schema(self) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema}


class ToolUnavailable(Exception):
    """The tool ran but its source could not supply the input. Not retried."""


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> Tool:
        if tool.name in self.tools:
            raise ValueError(f"tool {tool.name} registered twice")
        self.tools[tool.name] = tool
        return tool

    def get(self, name: str) -> Tool | None:
        return self.tools.get(name)

    def schemas(self, names: list[str]) -> list[dict]:
        missing = [n for n in names if n not in self.tools]
        if missing:
            raise ValueError(f"agent configuration names unknown tools: {missing}")
        return [self.tools[n].schema() for n in names]


def result_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str, ensure_ascii=False)


def truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    note = (f"\n[Truncated by the harness: this result was {len(text):,} characters; "
            f"the limit is {max_chars:,}. Ask for a narrower section if you need more.]")
    return text[: max_chars - len(note)] + note, True


def limit_document(text: str, ctx: ToolContext) -> tuple[str, bool]:
    """For tools that hand over a document: enforce the per-document limit."""
    return truncate(settings.redact(text), ctx.max_document_chars())
