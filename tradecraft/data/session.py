"""Is the market open? Regular hours on a trading day (NYSE calendar).

Quotes after the close are unusable for the liquidity screen, so "open" means
the regular session only: 9:30 to 16:00 Eastern, 13:00 on early-close days,
never on a weekend or an exchange holiday (config/market_calendar.json).
"""
from __future__ import annotations

import datetime as dt
from functools import lru_cache
from zoneinfo import ZoneInfo

from .. import settings


@lru_cache(maxsize=1)
def calendar() -> dict:
    return settings.load_json("market_calendar.json")


def _et(when: dt.datetime | None) -> dt.datetime:
    tz = ZoneInfo(calendar()["timezone"])
    return (when or dt.datetime.now(tz)).astimezone(tz)


def _hm(text: str) -> dt.time:
    h, m = text.split(":")
    return dt.time(int(h), int(m))


def status(when: dt.datetime | None = None) -> dict:
    """{"open": bool, "reason": ..., "as_of": ET time, "closes_at"/"day": ...}"""
    cal, t = calendar(), _et(when)
    day = t.date().isoformat()
    out = {"open": False, "as_of": t.isoformat(timespec="minutes"), "day": day}
    if t.weekday() >= 5:
        return {**out, "reason": "weekend"}
    if day in cal["holidays"]:
        return {**out, "reason": f"holiday: {cal['holidays'][day]}"}
    close = _hm(cal["early_close"] if day in cal["early_closes"] else cal["regular_session"]["close"])
    if t.time() < _hm(cal["regular_session"]["open"]):
        return {**out, "reason": "before the open"}
    if t.time() >= close:
        return {**out, "reason": "after the close"}
    return {**out, "open": True, "reason": "regular session", "closes_at": close.strftime("%H:%M"),
            "early_close": day in cal["early_closes"]}


def is_open(when: dt.datetime | None = None) -> bool:
    return status(when)["open"]
