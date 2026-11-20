"""Cost of a model call from its token usage, and the spend stops."""
from __future__ import annotations

from .. import settings


def cost_usd(model: str, usage: dict) -> float:
    prices = settings.models()["prices_usd_per_million_tokens"]
    p = prices.get(model)
    if p is None:
        # Unknown model (for example the scripted test model): charge at the
        # highest listed rate so a spend stop can never be bypassed by a typo.
        p = max((v for k, v in prices.items() if isinstance(v, dict)), key=lambda v: v["output"])
    inp, out = p["input"], p["output"]
    if "long_prompt_over_tokens" in p and usage.get("input_tokens", 0) > p["long_prompt_over_tokens"]:
        inp, out = p["long_input"], p["long_output"]
    return (usage.get("input_tokens", 0) * inp
            + usage.get("output_tokens", 0) * out
            + usage.get("cache_read_tokens", 0) * p.get("cache_read", inp)
            + usage.get("cache_write_tokens", 0) * p.get("cache_write", inp)) / 1_000_000


def stop_reason(store, request_id: str | None) -> str | None:
    """A plain sentence if a spend limit has been reached, else None."""
    s = settings.limits()["spend"]
    if request_id and store.spent_request(request_id) >= s["per_request_usd"]:
        return f"the spend limit of ${s['per_request_usd']:.2f} for this request has been reached"
    if store.spent_day() >= s["per_day_usd"]:
        return f"the daily spend limit of ${s['per_day_usd']:.2f} has been reached"
    return None
