"""Placeholder steps for the workflow skeleton.

Every step here returns clearly marked placeholder data ("stub": True) so the
graph's paths can be run and tested before the real steps exist. Real steps
replace these one at a time: stage 1 on Thursday, stage 2 on Friday, stages 3
and 4 on Saturday. Nothing a stub returns is a measurement or a finding.
"""
from __future__ import annotations

STUB = {"stub": True, "note": "placeholder from the workflow skeleton, not real output"}


def gate(state, ctx):
    return {**STUB, "status": "pass", "passing": 0, "source": "stub", "override_allowed": True}


def figures(state, ctx):
    return {**STUB, "horizons": []}


def retriever(state, ctx):
    return {**STUB, "items": [], "unavailable": []}


def grades(state, ctx):
    return {**STUB, "grades": {}}


def analyst(name):
    def step(state, ctx):
        return {**STUB, "findings": []}
    step.__name__ = name
    return step


def thesis(state, ctx):
    return {**STUB, "view": "bullish", "summary": "placeholder", "branches": []}


def validate(state, ctx):
    return {**STUB, "ok": True, "failed_checks": []}


def range_rule(state, ctx):
    return {**STUB, "range_bound": False}


def contracts(state, ctx):
    return {**STUB, "candidates": [{"id": "stub-1"}], "filtered_out": []}


def checklists(state, ctx):
    return {**STUB, "thesis": [], "contract": []}


def question(state, ctx):
    return {**STUB, "text": "placeholder question"}


def passages(state, ctx):
    return {**STUB, "for": [], "against": []}


def critic(state, ctx):
    return {**STUB, "objections": []}


def critic_check(state, ctx):
    return {**STUB, "ok": True, "failed_checks": []}


def readiness(state, ctx):
    if state.get("critic_unavailable"):
        return {**STUB, "label": "Not ready", "reason": state["critic_unavailable"]["reason"]}
    return {**STUB, "label": "Ready"}


def user_thesis(state, ctx):
    entry = state.get("user_input") or {}
    if entry.get("direction") not in ("bullish", "bearish"):
        raise ValueError("Choose a direction: bullish or bearish.")
    return {**STUB, "thesis_origin": "user", "view": entry["direction"], "verdict": "not_supported"}


DEFAULT_STEPS = {
    "gate": gate, "user_thesis": user_thesis, "figures": figures, "retriever": retriever, "grades": grades,
    "fundamental_analyst": analyst("fundamental_analyst"),
    "regime_assessor": analyst("regime_assessor"),
    "technical_analyst": analyst("technical_analyst"),
    "thesis": thesis, "validate": validate, "range_rule": range_rule,
    "contracts": contracts, "checklists": checklists, "question": question,
    "passages": passages, "critic": critic, "critic_check": critic_check, "readiness": readiness,
}
