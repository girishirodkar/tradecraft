"""Developer-only test failures (operator decision, 19 November 2026).

Three switches in config/test_failures.json, all off by default, each making one
source fail ONCE per request so that the recovery can be seen:

- option_chain_fail_once: stage 3's first fetch of the option chain fails. The
  stage 3 screen names the source and offers Retry; the retry succeeds.
- stage2_source_fail_once: the first call to one stage 2 data tool (named by
  stage2_source_tool) fails. The harness retries a failing tool once, so the
  Evidence Retriever recovers and the trace shows the failure and the retry.

- critic_fail_once: the Critic's first run in a request fails (stage 4). The
  challenge shows the stage-stopped screen with Retry; the retry runs the Critic.

Nothing here changes a rule or a result. The file is read on every use, so a
switch can be turned on and off without a restart, and while any is on every
page shows "TEST FAILURE ON" in its header.
"""
from __future__ import annotations

import json

from . import settings

FILE = "test_failures.json"
SWITCHES = ("option_chain_fail_once", "stage2_source_fail_once", "critic_fail_once")
_used: set[tuple[str, str]] = set()


class TestFailure(Exception):
    """A failure made on purpose by a switch in config/test_failures.json."""
    __test__ = False


def read() -> dict:
    try:
        return json.loads((settings.CONFIG / FILE).read_text())
    except (OSError, ValueError):
        return {}


def active() -> list[str]:
    """The switches that are on, for the marker in the page header."""
    cfg = read()
    return [s for s in SWITCHES if cfg.get(s) is True]


def tool() -> str | None:
    return read().get("stage2_source_tool")


def take(switch: str, request_id: str | None) -> bool:
    """True the first time this switch is asked about in this request, if it is on."""
    key = (switch, request_id or "")
    if switch not in active() or key in _used:
        return False
    _used.add(key)
    return True
