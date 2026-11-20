"""The macro calendar: scheduled FOMC decisions and major data releases.

FOMC decisions come from the Federal Reserve's own page. A two-day meeting's
decision is announced on its second day, so that is the date reported.

Data releases (which ones: config/data_sources.json) come from FRED's release
calendar, which needs FRED_API_KEY. FRED lists scheduled dates only a few weeks
ahead, so the result says how far its dates reach: beyond that a release is not
yet scheduled, which is not the same as no release.

The two halves fail separately. If one source is down the other is still
returned and the missing half is marked not available.
"""
from __future__ import annotations

import datetime as dt
import re

from .. import net, settings
from ..storage import Store, now

FRED = "https://api.stlouisfed.org/fred/release/dates"

URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
     "November", "December"], 1)}
_ABBR = {m[:3]: i for m, i in MONTHS.items()}


class MacroUnavailable(Exception):
    pass


def _month(name: str) -> int | None:
    return MONTHS.get(name) or _ABBR.get(name[:3])


def parse_fomc(html: str) -> list[dt.date]:
    """Decision dates (the last day of each meeting) from the calendar page."""
    out = []
    blocks = re.split(r"(\d{4}) FOMC Meetings", html)
    for year, body in zip(blocks[1::2], blocks[2::2]):
        for m in re.finditer(r"fomc-meeting__month[^>]*>\s*<strong>([^<]+)</strong>.*?fomc-meeting__date[^>]*>([^<]+)<",
                             body, re.DOTALL):
            months = [x.strip() for x in m.group(1).split("/")]       # "April/May" for a meeting across months
            days = re.findall(r"\d+", m.group(2))
            mon = _month(months[-1])
            if not days or not mon:
                continue
            try:
                out.append(dt.date(int(year), mon, int(days[-1])))
            except ValueError:
                continue
    return sorted(set(out))


def fomc_decisions(store: Store | None = None, days_ahead: int = 180) -> list[dict]:
    try:
        html = net.get(URL, source="fed.fomc", store=store).decode("utf-8", "replace")
    except net.FetchFailed as e:
        raise MacroUnavailable(f"Federal Reserve calendar: {str(e)[:160]}") from e
    all_dates = parse_fomc(html)
    if not all_dates:
        raise MacroUnavailable("Federal Reserve calendar: no meeting dates could be read from the page")
    today = now().date()
    return [{"date": d.isoformat(), "days_from_today": (d - today).days}
            for d in all_dates if today <= d <= today + dt.timedelta(days=days_ahead)]


def release_list() -> list[dict]:
    return settings.load_json("data_sources.json")["sources"]["macro_and_fed_calendar"]["releases"]


def data_releases(store: Store | None = None, days_ahead: int = 180) -> dict:
    """Scheduled dates of the configured releases, and how far FRED's schedule reaches."""
    today = now().date()
    out, reach = [], None
    for rel in release_list():
        try:
            j = net.get_json(FRED, {"file_type": "json", "release_id": rel["release_id"],
                                    "include_release_dates_with_no_data": "true",
                                    "realtime_start": today.isoformat(), "sort_order": "asc", "limit": 12},
                             source="fred.release_dates", store=store, secret_param=("api_key", "FRED_API_KEY"))
        except net.FetchFailed as e:
            raise MacroUnavailable(f"FRED release calendar: {str(e)[:160]}") from e
        dates = sorted(dt.date.fromisoformat(x["date"]) for x in j.get("release_dates", []))
        dates = [d for d in dates if d >= today]
        if dates:
            reach = max(reach, dates[-1]) if reach else dates[-1]
        out += [{"date": d.isoformat(), "release": rel["name"], "days_from_today": (d - today).days}
                for d in dates if d <= today + dt.timedelta(days=days_ahead)]
    return {"releases": sorted(out, key=lambda r: (r["date"], r["release"])),
            "scheduled_through": reach.isoformat() if reach else None}


def calendar(store: Store | None = None, days_ahead: int = 180) -> dict:
    """FOMC decisions and data releases together. Each half is reported as not
    available, with the reason, if its source fails; both failing is an error."""
    out: dict = {"retrieved": now().isoformat(timespec="minutes"), "window_days": days_ahead,
                 "sources": ["Federal Reserve, FOMC meeting calendars", "FRED release calendar"]}
    errors = []
    try:
        out["fomc_decisions"] = fomc_decisions(store, days_ahead)
    except MacroUnavailable as e:
        out["fomc_decisions"] = f"not available: {e}"
        errors.append(str(e))
    try:
        d = data_releases(store, days_ahead)
        out["data_releases"] = d["releases"]
        out["data_releases_tracked"] = [r["name"] for r in release_list()]
        out["data_releases_scheduled_through"] = d["scheduled_through"]
        out["data_releases_note"] = ("Release dates are published only a few weeks ahead. After "
                                     f"{d['scheduled_through']} a release is not yet scheduled; that is not "
                                     "the same as no release.") if d["scheduled_through"] else \
            "No release of the tracked list is scheduled yet."
    except MacroUnavailable as e:
        out["data_releases"] = f"not available: {e}"
        errors.append(str(e))
    if len(errors) == 2:
        raise MacroUnavailable("; ".join(errors))
    return out
