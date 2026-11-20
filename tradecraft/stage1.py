"""Stage 1 as a workflow step: fetch the chain, apply the gate, say where it came from.

Market open: the live chain (15 minutes delayed). If it cannot be fetched the
step falls back to the latest daily snapshot and marks the result provisional.
Market closed: the latest daily snapshot, provisional; a symbol the snapshot
does not hold is "not checked" (docs/product-shell.md 6.1, item 9).
"""
from __future__ import annotations

from . import gate
from .data import chain, session


def gate_step(state, ctx) -> dict:
    symbol = state["symbol"]
    market = session.status()
    fell_back = None
    data = None
    if market["open"]:
        try:
            data = chain.live(symbol, ctx.store)
        except chain.ChainUnavailable as e:
            fell_back = str(e)                     # recovery: live chain to snapshot
    if data is None:
        try:
            data = chain.snapshot(symbol)
        except chain.ChainUnavailable as e:
            return {"status": "not_checked", "symbol": symbol, "market": market, "source": "none",
                    "override_allowed": False, "live_failed": fell_back,
                    "reason": "not_in_snapshot" if not market["open"] else "no_source", "detail": str(e)}
    result = gate.screen(data, state.get("gate_settings"))
    result.update({"symbol": symbol, "market": market, "source": data["source"], "as_of": data["as_of"],
                   "provisional": data["source"] == "snapshot", "live_failed": fell_back,
                   "snapshot_file": data.get("file"), "contracts_in_chain": len(data["contracts"])})
    return result
