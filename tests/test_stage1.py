"""The symbol directory, the market calendar, the liquidity gate and the stage 1 step."""
import datetime as dt
from zoneinfo import ZoneInfo

import httpx
import pytest

from tradecraft import gate, net, stage1
from tradecraft.data import chain, directory, session

ET = ZoneInfo("America/New_York")

NASDAQ = """Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
NVDA|NVIDIA Corporation - Common Stock|Q|N|N|100|N|N
NVDL|GraniteShares 2x Long NVDA Daily ETF|G|N|N|100|Y|N
AMZN|Amazon.com, Inc. - Common Stock|Q|N|N|100|N|N
ZTEST|Test Company - Common Stock|Q|Y|N|100|N|N
ABCDW|ABCD Corp - Warrants|S|N|N|100|N|N
File Creation Time: 1118202621:31|||||||
"""
OTHER = """ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol
BAC|Bank of America Corporation Common Stock|N|BAC|N|100|N|BAC
BAC$B|Bank of America Corporation Depositary Shares, Series B Preferred|N|BACpB|N|100|N|BAC-B
SPY|SPDR S&P 500 ETF Trust|P|SPY|Y|100|N|SPY
BRK.B|Berkshire Hathaway Inc. Class B Common Stock|N|BRK.B|N|100|N|BRK.B
File Creation Time: 1118202621:31||||||
"""


@pytest.fixture
def listing():
    rows = directory._parse(NASDAQ, "nasdaq") + directory._parse(OTHER, "other") + directory.INDEXES
    return {"symbols": sorted(rows)}


# ---- directory ------------------------------------------------------------------------

def test_directory_keeps_stocks_and_etfs_and_drops_the_rest(listing):
    got = {s[0]: s for s in listing["symbols"]}
    assert set(got) == {"NVDA", "NVDL", "AMZN", "BAC", "SPY", "BRK.B", "SPX", "XSP"}
    assert got["NVDA"] == ("NVDA", "NVIDIA Corporation", "STOCK")       # "- Common Stock" removed
    assert got["BAC"][1] == "Bank of America Corporation"
    assert got["SPY"][2] == "ETF" and got["SPX"][2] == "INDEX"


def test_search_order_symbol_prefix_then_name_word_then_anywhere(listing):
    s = lambda q: [r[0] for r in directory.search(q, listing)]           # noqa: E731
    assert s("nvd") == ["NVDA", "NVDL"]                                 # symbols that start with the text
    assert s("amazon") == ["AMZN"]                                      # a name that starts with it
    assert s("america") == ["BAC"]                                      # a word inside a name
    assert s("sp") == ["SPX", "SPY", "XSP"]                             # XSP only contains it: last
    assert s("NVIDIA") == ["NVDA"] and s("  ") == [] and s("zzzz") == []
    assert len(directory.search("a", listing)) <= 8


def test_daily_list_names_come_first_among_symbols_that_start_with_the_text():
    rows = {"symbols": [["NVA", "Nova Minerals", "STOCK"], ["NVD", "GraniteShares 2x Short NVDA Daily ETF", "ETF"],
                        ["NVDA", "NVIDIA Corporation", "STOCK"], ["NVDL", "GraniteShares 2x Long NVDA Daily ETF", "ETF"]],
            "daily": ["NVDA"]}
    s = lambda q: [r[0] for r in directory.search(q, rows)]              # noqa: E731
    assert s("nv") == ["NVDA", "NVA", "NVD", "NVDL"]                     # daily list, then shorter, then alphabetical
    assert s("nvd") == ["NVDA", "NVD", "NVDL"]                           # daily list ahead of an exact match
    rows["daily"] = []
    assert s("nvd") == ["NVD", "NVDA", "NVDL"]                           # without it: exact match first


def test_daily_names_come_from_the_snapshot_list():
    names = directory.daily_names()
    assert "NVDA" in names and "SPY" in names and "SPX" in names and not any(n.startswith("_") for n in names)


# ---- market calendar ------------------------------------------------------------------

@pytest.mark.parametrize("when, is_open, reason", [
    ("2026-11-18 10:00", True, "regular session"),
    ("2026-11-18 09:29", False, "before the open"),
    ("2026-11-18 16:00", False, "after the close"),
    ("2026-11-21 11:00", False, "weekend"),
    ("2026-11-26 11:00", False, "holiday: Thanksgiving Day"),
    ("2026-11-27 12:59", True, "regular session"),          # early close at 13:00
    ("2026-11-27 13:00", False, "after the close"),
    ("2026-07-03 11:00", False, "holiday: Independence Day (observed)"),
])
def test_market_status(when, is_open, reason):
    st = session.status(dt.datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=ET))
    assert st["open"] is is_open and st["reason"] == reason


def test_market_status_converts_from_pacific_time():
    pt = dt.datetime(2026, 11, 18, 11, 30, tzinfo=ZoneInfo("America/Los_Angeles"))   # 14:30 ET
    assert session.status(pt)["open"]


# ---- the gate -------------------------------------------------------------------------

def c(dte=60, strike=100.0, bid=1.00, ask=1.04, oi=500, spot=100.0):
    return {"dte": dte, "strike": strike, "type": "call", "bid": bid, "ask": ask, "open_interest": oi, "spot": spot}


def test_a_contract_passes_only_when_it_meets_all_five_criteria():
    chain_ = {"contracts": [
        c(), c(strike=105),                         # two that pass
        c(bid=1.00, ask=1.10),                      # spread 9.5%
        c(oi=50),                                   # open interest
        c(dte=30),                                  # outside 42 to 90
        c(strike=115),                              # 15% from spot
        c(bid=0.10, ask=0.104),                     # premium 0.10
        c(bid=0, ask=1.0), c(bid=1.2, ask=1.0), c(bid=None, ask=1.0),   # invalid quotes
        c(dte=3), c(dte=200),                       # outside 7 to 180: not considered at all
    ]}
    r = gate.screen(chain_)
    assert r["status"] == "pass" and r["passing"] == 2
    assert r["considered"] == 10 and r["screened_out"] == 8
    by = r["screened_out_by_reason"]
    assert {k: v["count"] for k, v in by.items()} == {
        "spread": 1, "open_interest": 1, "dte": 1, "strike": 1, "premium": 1, "invalid_quote": 3}
    assert all(by[k]["alone"] == 1 for k in ["spread", "open_interest", "dte", "strike", "premium"])
    assert "alone" not in by["invalid_quote"]       # that tile shows only its count
    assert list(by) == ["spread", "open_interest", "dte", "strike", "premium", "invalid_quote"]


def test_a_contract_failing_two_criteria_counts_under_both_but_alone_under_neither():
    r = gate.screen({"contracts": [c(oi=50, strike=120), c(), c()]})
    by = r["screened_out_by_reason"]
    assert by["open_interest"] == {"count": 1, "alone": 0} and by["strike"] == {"count": 1, "alone": 0}
    assert r["screened_out"] == 1                   # the tiles add up to more than X


def test_fewer_than_two_passing_contracts_is_a_fail():
    assert gate.screen({"contracts": [c()]})["status"] == "fail"
    assert gate.screen({"contracts": [c(), c()]})["status"] == "pass"


def test_strike_distance_is_a_plain_percentage():
    # 110.5 is 10.5% above spot: inside the census's log band (log 1.105 = 0.0998) but outside 10% here.
    r = gate.screen({"contracts": [c(strike=110.0), c(strike=110.5), c(strike=90.0), c(strike=89.9)]})
    assert r["passing"] == 2 and "plain percentage" in r["strike_distance"]


def test_buckets_count_contracts_passing_the_other_four_and_highlight_the_overlap():
    chain_ = {"contracts": [c(dte=10), c(dte=30), c(dte=30), c(dte=60), c(dte=120), c(dte=30, oi=1)]}
    r = gate.screen(chain_)
    assert [(b["from"], b["to"], b["passing_other_four"]) for b in r["buckets"]] == [
        (7, 21, 1), (22, 41, 2), (42, 90, 1), (91, 180, 1)]
    assert [b["highlighted"] for b in r["buckets"]] == [False, False, True, False] and r["dte_matches_one_bucket"]
    r = gate.screen(chain_, {"dte_min": 30, "dte_max": 60})
    assert [b["highlighted"] for b in r["buckets"]] == [False, True, True, False]
    assert not r["dte_matches_one_bucket"] and r["passing"] == 3


def test_spread_figures_come_from_the_passing_contracts_only():
    r = gate.screen({"contracts": [c(bid=1.00, ask=1.01), c(bid=1.00, ask=1.03), c(bid=1.00, ask=1.05),
                                   c(bid=1.00, ask=1.50)]})
    assert r["spread"] == {"median": 3.0, "tightest": 1.0, "widest": 4.9}
    assert gate.screen({"contracts": [c(oi=1)]})["spread"] is None


def test_settings_are_held_inside_each_controls_range():
    s = gate.clean_settings({"max_spread_pct": 50, "min_open_interest": 80, "dte_min": 200, "dte_max": 1,
                             "max_strike_distance_pct": 2, "min_premium": 0.07, "unknown": 1})
    assert s == {"max_spread_pct": 10.0, "min_open_interest": 100, "dte_min": 7, "dte_max": 180,
                 "max_strike_distance_pct": 5.0, "min_premium": 0.05}
    assert gate.screen({"contracts": [c()]}, {"max_spread_pct": 7.5})["changed"] == ["max_spread_pct"]


def test_gate_result_carries_no_prices():
    r = gate.screen({"contracts": [c(), c()]})
    assert not any(k in r for k in ("contracts", "spot", "bid", "ask", "mid", "premium"))
    assert set(r["spread"]) == {"median", "tightest", "widest"}     # spreads in percent, never prices


def test_no_valid_quote_at_all_cannot_be_overridden():
    assert gate.screen({"contracts": [c(bid=0, ask=0), c(bid=None, ask=None)]})["override_allowed"] is False
    assert gate.screen({"contracts": [c(oi=1)]})["override_allowed"] is True


# ---- the stage 1 step -----------------------------------------------------------------

class Ctx:
    store = None


def patch(monkeypatch, is_open, live=None, snap=None):
    monkeypatch.setattr(session, "status", lambda when=None: {"open": is_open, "reason": "test"})

    def run(source, value):
        def f(symbol, *a):
            if isinstance(value, Exception):
                raise value
            return {"symbol": symbol, "source": source, "as_of": "2026-11-18T14:00-05:00", "file": "snap.csv.gz",
                    "contracts": value}
        return f
    monkeypatch.setattr(chain, "live", run("live", live))
    monkeypatch.setattr(chain, "snapshot", run("snapshot", snap))


def test_market_open_uses_the_live_chain(monkeypatch):
    patch(monkeypatch, True, live=[c(), c()], snap=[c()])
    r = stage1.gate_step({"symbol": "NVDA"}, Ctx)
    assert r["status"] == "pass" and r["source"] == "live" and r["provisional"] is False


def test_live_failure_falls_back_to_the_snapshot_and_says_so(monkeypatch):
    patch(monkeypatch, True, live=chain.ChainUnavailable("Cboe delayed quotes: HTTP 503"), snap=[c(), c()])
    r = stage1.gate_step({"symbol": "NVDA"}, Ctx)
    assert r["status"] == "pass" and r["source"] == "snapshot" and r["provisional"] is True
    assert "503" in r["live_failed"]


def test_market_closed_uses_the_snapshot_as_provisional(monkeypatch):
    patch(monkeypatch, False, live=[c(), c()], snap=[c()])
    r = stage1.gate_step({"symbol": "NVDA", "gate_settings": {"min_open_interest": 10}}, Ctx)
    assert r["source"] == "snapshot" and r["provisional"] is True and r["status"] == "fail"
    assert r["settings"]["min_open_interest"] == 10


def test_market_closed_and_not_in_the_snapshot_is_not_checked(monkeypatch):
    patch(monkeypatch, False, snap=chain.ChainUnavailable("ZZZZ is not in the daily snapshot"))
    r = stage1.gate_step({"symbol": "ZZZZ"}, Ctx)
    assert r["status"] == "not_checked" and r["reason"] == "not_in_snapshot" and r["override_allowed"] is False


# ---- redirects stay inside the allowlist ----------------------------------------------

def test_a_redirect_is_followed_only_to_an_allowlisted_host(monkeypatch, store):
    def handler(req):
        if req.url.host == "cdn.cboe.com" and req.url.path == "/ok":
            return httpx.Response(307, headers={"location": "https://cdn-api.cboe.com/ok"})
        if req.url.host == "cdn-api.cboe.com":
            return httpx.Response(200, content=b"chain")
        return httpx.Response(307, headers={"location": "https://evil.example.com/steal"})
    monkeypatch.setattr(net, "_client", httpx.Client(transport=httpx.MockTransport(handler)))
    assert net.get("https://cdn.cboe.com/ok", source="t", store=store, use_cache=False) == b"chain"
    with pytest.raises(net.NotAllowed, match="evil.example.com"):
        net.get("https://cdn.cboe.com/bad", source="t", store=store, use_cache=False)


# ---- the real gate inside the workflow ------------------------------------------------

def test_workflow_runs_the_real_gate_and_fail_leads_to_override(monkeypatch, store):
    from tradecraft.steps import real_steps
    from tradecraft.workflow import Workflow
    patch(monkeypatch, False, snap=[c(dte=30), c(dte=30), c(dte=30)])     # liquid only at 22 to 41 DTE
    w = Workflow(store, steps=real_steps(), symbol_ok=lambda s: s == "ADBE")
    v = w.start("ADBE")
    g = v["state"]["gate"]
    assert g["status"] == "fail" and g["provisional"] and v["pause"]["actions"] == ["override", "adjust", "stop"]
    v = w.resume(v["request_id"], "adjust", settings={"dte_min": 22, "dte_max": 41})
    g = v["state"]["gate"]
    assert g["status"] == "pass" and g["passing"] == 3 and g["changed"] == ["dte_min", "dte_max"]
    assert v["pause"]["actions"] == ["continue", "adjust", "stop"]
    pend = store.pending(v["request_id"])
    assert [r["decision"] for r in pend] == ["gate_fail", "gate_pass"]
    assert pend[0]["payload"]["liquidity_screen"]["strike_distance"].startswith("plain percentage")
