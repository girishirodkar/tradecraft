"""The steps the application runs. Stages 1 to 4 are real."""
from __future__ import annotations

from . import stage2, stage3, stage4
from .stage1 import gate_step


def real_steps() -> dict:
    return {"gate": gate_step, **stage2.STEPS, "contracts": stage3.contracts_step, **stage4.STEPS}
