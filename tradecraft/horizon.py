"""Two fixed rules of stage 2, in code: the recommended horizon and the
range-bound view (docs/on-demand-mode-design.md, step 2A).

Neither takes account of how strong any row looks, and no price leaves this
module: the horizon rule uses counts of eligible contracts only.
"""
from __future__ import annotations

import datetime as dt

from . import gate
from .figures import VIEW_ROWS

TARGET_DAYS = 30
RANGE_ROWS = [7, 14]
MIN_ELIGIBLE = gate.MIN_PASSING
# Events that set a row aside in the horizon rule (rule 3).
SPANNING_KINDS = {"earnings", "binary_event"}


def eligible_counts(chain: dict, gate_settings: dict | None, rows: list[int] = VIEW_ROWS) -> dict[int, int]:
    """Per row: contracts that pass the stage 1 criteria in force, leaving out
    the DTE criterion, and expire on or after the horizon date and no more than
    twice the horizon away (operator decision, 18 November 2026)."""
    s = gate.clean_settings(gate_settings)
    ok = [c for c in (dict(c) for c in chain["contracts"]) if not (gate._fails(c, s) - {"dte"})]
    return {d: sum(1 for c in ok if d <= c["dte"] <= 2 * d) for d in rows}


def events_inside(events: list[dict], today: dt.date, days: int) -> list[dict]:
    """Events dated from today to the horizon date, both ends included. An
    earnings date has no time of day, so the report day counts as inside."""
    end = today + dt.timedelta(days=days)
    out = []
    for e in events:
        try:
            d = dt.date.fromisoformat(str(e.get("date"))[:10])
        except ValueError:
            continue
        if today <= d <= end:
            out.append({**e, "day": (d - today).days})
    return out


def recommend(today: dt.date, events: list[dict], eligible: dict[int, int] | None,
              range_bound: bool = False) -> dict:
    """The primary horizon, by the fixed rule.

    1. The 180-day row is never a candidate.
    2. Rows without eligible contracts are excluded (skipped, and the result
       marked provisional, when no option data is available: `eligible` None).
    3. Rows that span an earnings date or a flagged binary event are set aside,
       unless every remaining row spans one: then none is, with a warning.
    4. The remaining row nearest 30 days is recommended.
    For a range-bound view only the 7- and 14-day rows are candidates.
    """
    candidates = RANGE_ROWS if range_bound else VIEW_ROWS
    rows = []
    for d in candidates:
        spanning = [e for e in events_inside(events, today, d) if e.get("kind") in SPANNING_KINDS]
        n = None if eligible is None else eligible.get(d, 0)
        rows.append({"days": d, "eligible_contracts": n, "has_contracts": n is None or n >= MIN_ELIGIBLE,
                     "spans": spanning})
    with_contracts = [r for r in rows if r["has_contracts"]]
    clear = [r for r in with_contracts if not r["spans"]]
    warning = None
    if with_contracts and not clear:
        clear = with_contracts
        names = sorted({e.get("label") or e["kind"] for r in with_contracts for e in r["spans"]})
        warning = f"Every horizon with eligible contracts spans a known event: {', '.join(names)}."
    pick = min(clear, key=lambda r: (abs(r["days"] - TARGET_DAYS), r["days"]))["days"] if clear else None
    for r in rows:
        r["status"] = ("recommended" if r["days"] == pick else
                       "no eligible contracts" if not r["has_contracts"] else
                       "spans an event" if r["spans"] and not warning else "candidate")
    return {"recommended_days": pick, "provisional": eligible is None, "warning": warning, "rows": rows,
            "reason": ("No horizon has eligible contracts." if pick is None else
                       f"The {pick}-day row is the candidate nearest {TARGET_DAYS} days"
                       + (" (option data was not available, so contracts were not checked)."
                          if eligible is None else "."))}


def range_bound(view: str | None, volatility_state: str | None, today: dt.date, events: list[dict],
                unchecked: list[str] | None = None) -> dict:
    """The range-bound view, by rule. All four conditions: the agents returned
    no directional view; the volatility state is quiet; the row is the 7- or
    14-day row; no earnings date or flagged event falls inside the row.

    `events` are those that count for this instrument (earnings, flagged events
    and, where the flag list says so, scheduled releases), each optionally with
    `max_row_days`: the longest row on which it counts. A condition that could
    not be checked is never treated as met."""
    rows = []
    for d in RANGE_ROWS:
        inside = [e for e in events_inside(events, today, d) if d <= e.get("max_row_days", d)]
        rows.append({"days": d, "events_inside": inside, "met": False})
    no_view = view is None
    quiet = volatility_state == "quiet"
    for r in rows:
        r["met"] = no_view and quiet and not r["events_inside"] and not unchecked
    met = [r["days"] for r in rows if r["met"]]
    if not no_view:
        why = "Not applied: the agents returned a directional view."
    elif not quiet:
        why = f"Not met. The volatility state is {volatility_state or 'not available'}."
    elif unchecked:
        why = "Not met. Could not be checked: " + ", ".join(unchecked) + "."
    elif not met:
        why = "Not met. A known event falls inside both the 7- and 14-day rows."
    else:
        why = "Met on the " + " and ".join(f"{d}-day" for d in met) + (" rows." if len(met) > 1 else " row.")
    return {"range_bound": bool(met), "rows": rows, "rows_met": met, "reason": why,
            "conditions": {"no_directional_view": no_view, "quiet_volatility_state": quiet,
                           "unchecked": unchecked or []},
            "label": "measured tendency: not a trade signal"}
