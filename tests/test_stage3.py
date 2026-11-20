"""Stage 3: candidates, measures, filters, ranking and the workflow step. No model call anywhere."""
import datetime as dt
import json
import math
import random

import pytest

from tradecraft import stage3
from tradecraft.data import chain as chain_data
from tradecraft.data import fmp, prices, session
from tradecraft.workflow.state import StepContext

TODAY = dt.date(2026, 11, 18)
NO_EVENTS = {"earnings": {"date": None, "status": "not available"},
             "ex_dividend": {"date": None, "status": "none declared"}}


def con(kind, strike, bid, ask, dte=30, oi=500, spot=100.0, iv=0.30, **more):
    exp = (TODAY + dt.timedelta(days=dte)).isoformat()
    return {"occ": f"X{exp}{kind[0]}{strike}", "expiration": exp, "dte": dte, "strike": float(strike), "type": kind,
            "bid": bid, "ask": ask, "open_interest": oi, "spot": spot, "iv": iv,
            "delta": 0.5 if kind == "call" else -0.5, "theta": -0.05, "vega": 0.10, **more}


def synthetic_chain(spot=100.0, dtes=(30,), strikes=range(80, 121, 5), spread=0.02, source="live"):
    rows = []
    for dte in dtes:
        for k in strikes:
            tv = 2.5 * math.exp(-((k - spot) / 8.0) ** 2) * math.sqrt(dte / 30) + 0.3
            for kind in ("call", "put"):
                mid = tv + (max(spot - k, 0) if kind == "call" else max(k - spot, 0))
                rows.append(con(kind, k, round(mid * (1 - spread / 2), 2), round(mid * (1 + spread / 2), 2), dte, spot=spot))
    return {"symbol": "EXMP", "source": source, "as_of": TODAY.isoformat() + "T11:42-05:00", "spot": spot,
            "contracts": rows}


def walk(n=252 * 8, seed=1, vol=0.015):
    r, x, out = random.Random(seed), 100.0, []
    for _ in range(n):
        x *= math.exp(r.gauss(0.0003, vol))
        out.append(x)
    return out


class FlatHistory:
    """A stand-in for the price history: a 5% typical move and fixed figures."""
    move_pct = 5.0

    def figure(self, intervals, spot, within=(-math.inf, math.inf)):
        return {"pct": 50.0, "own_pct": 50.0, "pooled_pct": None, "own_weight": 1.0, "basis": "own history",
                "uncertainty_pts": 3.0}


def ctx_for(legs, view="bullish", events=NO_EVENTS):
    return {"spot": 100.0, "view": view, "history": FlatHistory(), "expiration": "2026-12-18", "dte": 30,
            "ok_exp": [], "events": events, "levels": {"high": 104.0, "low": 97.0}, "chart": (88.0, 112.0)}


def legs(*specs):
    return [stage3._leg(a, {**con(kind, k, bid, ask), "mid": (bid + ask) / 2}) for a, kind, k, bid, ask in specs]


# ---- the mock-up's example, reproduced ------------------------------------------------------

def test_the_mock_ups_bull_put_spread_figures():
    c = stage3.describe({"name": "Bull put spread (credit), 95 / 100",
                         "legs": legs(("sell", "put", 100, 2.35, 2.45), ("buy", "put", 95, 0.68, 0.72))},
                        {"id": "hold", "shape": "hold"}, ctx_for(None))
    assert (c["max_loss"], c["max_gain"], c["break_even"], c["net_price"], c["credit"]) == (330.0, 170.0, [98.3], -170.0, True)
    assert c["cost"]["dollars"] == 7.0 and round(c["cost"]["pct_of_risk"]) == 2
    assert c["payoff_at_one_move"]["per_dollar_at_risk"] == 0.52          # $170 on $330 at $105
    assert c["checks"]["has_short_leg"] and c["checks"]["short_leg_in_the_money"] is False
    assert c["levels"]["break_even_vs_support"] == ["above"] and c["levels"]["break_even_vs_resistance"] == ["below"]


def test_the_mock_ups_call_spread_and_long_call():
    spread = stage3.describe({"name": "Bull call spread (debit), 100 / 105",
                              "legs": legs(("buy", "call", 100, 2.35, 2.45), ("sell", "call", 105, 0.68, 0.72))},
                             {"id": "move", "shape": "move"}, ctx_for(None))
    assert (spread["max_loss"], spread["max_gain"], spread["break_even"]) == (170.0, 330.0, [101.7])
    assert spread["payoff_at_one_move"]["per_dollar_at_risk"] == 1.94
    call = stage3.describe({"name": "Long call, 100", "legs": legs(("buy", "call", 100, 2.35, 2.45))},
                           {"id": "single", "shape": "single"}, ctx_for(None))
    assert (call["max_loss"], call["max_gain"], call["break_even"]) == (240.0, None, [102.4])
    assert call["payoff_at_one_move"]["per_dollar_at_risk"] == 1.08 and call["payoff_at_one_move"]["keeps_growing"]
    assert call["cost"]["dollars"] == 5.0 and call["checks"]["has_short_leg"] is False


def test_a_long_puts_max_profit_is_a_dollar_figure():
    put = stage3.describe({"name": "Long put, 100", "legs": legs(("buy", "put", 100, 2.35, 2.45))},
                          {"id": "single", "shape": "single"}, ctx_for(None, "bearish"))
    assert put["max_gain"] == 9760.0 and put["break_even"] == [97.6]


# ---- eligibility and expirations -------------------------------------------------------------

def test_leg_eligibility_leaves_out_the_dte_criterion_and_keeps_the_7_day_floor():
    ch = {"contracts": [con("call", 100, 2.0, 2.04, dte=30), con("call", 100, 2.0, 2.04, dte=5),
                        con("call", 100, 2.0, 2.40, dte=30), con("call", 100, 2.0, 2.04, dte=30, oi=5),
                        con("call", 120, 2.0, 2.04, dte=30)]}
    ok = stage3.eligible(ch, None)                    # default DTE is 42 to 90: the 30-day contract still counts
    assert [(c["dte"], c["strike"], c["single_ok"]) for c in ok] == [(30, 100.0, True), (30, 100.0, False)]
    assert ok[1]["spread_pct"] == 18.2                # a wide quote: a spread leg may use it, a single option may not


def test_expirations_one_per_horizon_merged_with_the_thesis_default():
    ok = stage3.eligible(synthetic_chain(dtes=(5, 9, 32, 95)), None)
    opts = stage3.expiration_options(ok, 30)
    assert [(o["dte"], o["horizons_served"]) for o in opts] == [(9, [7]), (32, [14, 30]), (95, [60, 90])]
    mid = opts[1]
    assert mid["from_thesis"] and mid["selected"] and mid["serves_days"] == 30 and mid["days_beyond"] == 2
    assert not mid["poor_match"] and not opts[2]["poor_match"]
    switched = stage3.expiration_options(ok, 30, opts[2]["expiration"])
    assert [o["selected"] for o in switched] == [False, False, True] and switched[1]["from_thesis"]


def test_poor_match_when_the_expiration_is_more_than_twice_the_horizon_away():
    ok = stage3.eligible(synthetic_chain(dtes=(32,)), None)
    only = stage3.expiration_options(ok, 14)[0]
    assert only["horizons_served"] == [7, 14, 30] and only["serves_days"] == 14 and only["poor_match"]


def test_trading_days_skip_weekends_and_exchange_holidays():
    assert stage3.trading_days(dt.date(2026, 11, 20), dt.date(2026, 11, 23)) == 1          # over a weekend
    assert stage3.trading_days(dt.date(2026, 11, 25), dt.date(2026, 11, 27)) == 1          # Thanksgiving


# ---- candidates ------------------------------------------------------------------------------

def grids(chain):
    ok = stage3.eligible(chain, None)
    return ({c["strike"]: c for c in ok if c["type"] == "call"}, {c["strike"]: c for c in ok if c["type"] == "put"})


def names(built):
    return {e["id"]: [c["name"] for c in e["constructions"]] for e in built}


def test_a_bullish_view_builds_two_spread_shapes_and_a_long_call():
    built, missing = stage3.build_candidates("bullish", 100.0, 5.0, *grids(synthetic_chain()))
    assert missing == []
    assert names(built) == {"hold": ["Bull call spread (debit), 95 / 100", "Bull put spread (credit), 95 / 100"],
                            "move": ["Bull call spread (debit), 100 / 105", "Bull put spread (credit), 100 / 105"],
                            "single": ["Long call, 100"]}
    sold_first = built[0]["constructions"][1]["legs"]
    assert [(l["action"], l["strike"]) for l in sold_first] == [("sell", 100.0), ("buy", 95.0)]


def test_a_bearish_view_mirrors_it():
    built, _ = stage3.build_candidates("bearish", 100.0, 5.0, *grids(synthetic_chain()))
    assert names(built) == {"hold": ["Bear call spread (credit), 100 / 105", "Bear put spread (debit), 100 / 105"],
                            "move": ["Bear call spread (credit), 95 / 100", "Bear put spread (debit), 95 / 100"],
                            "single": ["Long put, 100"]}
    for e in built[:2]:
        for c in e["constructions"]:
            assert stage3.payoff(c["legs"], 80) > 0 > stage3.payoff(c["legs"], 120)


def test_the_second_strike_moves_to_the_nearest_eligible_one():
    calls, puts = grids(synthetic_chain())
    built, _ = stage3.build_candidates("bullish", 100.0, 14.0, calls, puts)     # the target, 114, is not listed
    move = next(e for e in built if e["id"] == "move")
    assert move["second"] == 110.0                  # 120 fails the 10% strike distance; 110 is the nearest left
    assert move["second_target"] == 114.0


def test_a_shape_with_no_strike_on_its_side_is_not_built_and_says_why():
    calls, puts = grids(synthetic_chain(strikes=[100, 105]))
    built, missing = stage3.build_candidates("bullish", 100.0, 5.0, calls, puts)
    assert set(names(built)) == {"move", "single"}
    assert missing == [{"id": "hold", "name": "Bull spread below spot",
                        "reason": "no eligible strike below the strike nearest spot, 100"}]


def test_one_construction_only_when_the_other_has_an_ineligible_leg():
    ch = synthetic_chain()
    for c in ch["contracts"]:
        if c["type"] == "put" and c["strike"] == 105:
            c["open_interest"] = 1                         # the in-the-money put fails the screen
    built, _ = stage3.build_candidates("bullish", 100.0, 5.0, *grids(ch))
    move = next(e for e in built if e["id"] == "move")
    assert [c["name"] for c in move["constructions"]] == ["Bull call spread (debit), 100 / 105"]
    assert move["one_construction_only"]


def test_nothing_eligible_builds_nothing():
    built, missing = stage3.build_candidates("bullish", 100.0, 5.0, {}, {})
    assert built == [] and {m["reason"] for m in missing} == {"no eligible contracts at your criteria"}


def test_a_range_bound_view_builds_iron_condors_with_defined_risk():
    built, missing = stage3.build_candidates("range_bound", 100.0, 5.0, *grids(synthetic_chain(strikes=range(85, 116, 5))))
    assert names(built)["condor"] == ["Iron condor, 90 / 95 / 105 / 110"]
    shape = stage3.payoff_shape(built[0]["constructions"][0]["legs"])
    assert shape["max_profit"] is not None and shape["max_loss"] > 0 and len(shape["breakevens"]) == 2
    assert stage3.payoff(built[0]["constructions"][0]["legs"], 100) > 0


# ---- the history-based figures and the implied ones ------------------------------------------------

def test_blend_weight_rules():
    closes = walk()
    w, basis = stage3.blend_weight("EXMP", 30, closes, 21)
    n = (len(closes) - 1) / 21
    assert basis == "blended" and w == pytest.approx(n / (n + 380))
    assert stage3.blend_weight("EXMP", 61, closes, 42) == (0.0, "pool average")            # beyond 60 days
    assert stage3.blend_weight("SPY", 30, closes, 21) == (1.0, "own history")              # a fund: unblended
    assert stage3.blend_weight("EXMP", 30, closes[:500], 21)[0] == 0.0                     # under five years
    assert stage3.blend_weight("EXMP", 22, closes, 15)[0] == pytest.approx((len(closes) - 1) / 15 / ((len(closes) - 1) / 15 + 570))
    assert stage3.blend_weight("EXMP", 45, closes, 31)[0] == pytest.approx((len(closes) - 1) / 31 / ((len(closes) - 1) / 31 + 380))


def test_history_figures_own_pooled_and_blended():
    closes = walk()
    pool = (tuple(sorted(x / 0.05 for x in stage3._moves(walk(seed=2), 21))),
            tuple(sorted(x / 0.05 for x in stage3._moves(walk(seed=3), 21))))
    h = stage3.History("EXMP", closes, 30, 21, pool)
    everything = h.figure([(0.0, math.inf)], 100.0)
    assert everything["pct"] == 100.0
    up = h.figure([(100.0, math.inf)], 100.0)                 # profits on any higher close
    assert 40 < up["own_pct"] < 70 and up["pooled_pct"] is not None
    assert up["pct"] == pytest.approx(h.weight * up["own_pct"] + (1 - h.weight) * up["pooled_pct"], abs=0.11)
    right = h.figure([(100.0, math.inf)], 100.0, (0.0, math.inf))
    assert right["pct"] == 100.0                             # among the periods that closed higher, all of them
    needs_move = h.figure([(104.0, math.inf)], 100.0, (0.0, math.inf))
    assert needs_move["pct"] < 100.0                         # right about direction, and still a loss
    fund = stage3.History("SPY", closes, 30, 21, pool).figure([(100.0, math.inf)], 100.0)
    assert fund["pooled_pct"] is None and fund["pct"] == fund["own_pct"] and fund["basis"] == "own history"


def test_implied_pop_reads_the_contract_nearest_the_breakeven_and_falls_back_to_at_the_money():
    ok = [{**con("call", 100, 2, 2.04, iv=0.30)}, {**con("put", 100, 2, 2.04, iv=0.30)},
          {**con("call", 105, 1, 1.02, iv=0.20)}]
    at = stage3.implied_pop([(100.0, math.inf)], 100.0, 30, ok)
    assert 45 < at["pct"] < 50 and at["iv_used"][0]["iv"] == 0.30 and "approximate" in at["method"]
    far = stage3.implied_pop([(104.9, math.inf)], 100.0, 30, ok)
    assert far["iv_used"][0] == {"breakeven": 104.9, "iv": 0.20, "from": "nearest the breakeven"}
    no_puts = stage3.implied_pop([(0.0, 96.0)], 100.0, 30, [ok[0]])
    assert no_puts["iv_used"][0]["from"] == "at the money"
    inside = stage3.implied_pop([(95.0, 105.0)], 100.0, 30, ok)
    assert 0 < inside["pct"] < 100
    assert stage3.implied_pop([(100.0, math.inf)], 100.0, 30, [])["pct"] is None
    assert stage3.implied_move_pct(ok, 100.0, 30) == round(100 * 0.30 * math.sqrt(30 / 365), 1)


# ---- the whole stage on one chain ------------------------------------------------------------

def run(view="bullish", days=30, params=None, chain=None, events=NO_EVENTS, settings=None):
    return stage3.select(chain or synthetic_chain(dtes=(9, 30, 95)), {"view": view, "horizon_days": days, "origin": "system"},
                         walk(), settings, params, events, pool=())


def test_select_ranks_by_the_chosen_priority_and_names_the_best_fit():
    out = run()
    assert out["outcome"] == "ok" and out["expiry_chosen"] == (TODAY + dt.timedelta(days=30)).isoformat()
    assert [c["id"] for c in out["candidates"]][0] == "hold" and out["best_fit_id"] == "hold"
    assert out["candidates"][0]["best_fit_reason"] == "profitable in every historical period in which the thesis held"
    by_cost = run(params={"priority": "cost"})["candidates"]
    assert [c["cost"]["pct_of_risk"] for c in by_cost] == sorted(c["cost"]["pct_of_risk"] for c in by_cost)
    by_payoff = run(params={"priority": "payoff"})["candidates"]
    ratios = [c["payoff_at_one_move"]["per_dollar_at_risk"] for c in by_payoff]
    assert ratios == sorted(ratios, reverse=True)
    assert out["labels"] == {"pays_when_view_right": "before slippage", "base_rate_profit": "before slippage",
                             "implied_profit": "approximate"}
    assert "recommend" not in json.dumps(out).lower() and "richness" not in json.dumps(out).lower()


def test_the_cheaper_construction_is_kept_and_the_other_is_shown_inside_it():
    c = run()["candidates"][0]
    assert c["other_construction"]["available"] and c["other_construction"]["cost"]["dollars"] >= c["cost"]["dollars"]


def test_the_cost_cap_filters_and_the_reason_is_stated():
    out = run(chain=synthetic_chain(dtes=(30,), spread=0.09), settings={"max_spread_pct": 10})
    assert out["filtered_out"] and all(c["removed_by"] == "cost_cap" for c in out["filtered_out"])
    assert "above the 5% cost cap" in out["filtered_out"][0]["removed_reason"]
    assert all(c["cost"]["pct_of_risk"] <= 5 for c in out["candidates"])
    assert {c["id"] for c in out["candidates"]}.isdisjoint(c["id"] for c in out["filtered_out"])


def test_no_eligible_contracts_is_a_result_with_its_reason():
    thin = synthetic_chain(dtes=(30,))
    for c in thin["contracts"]:
        c["open_interest"] = 5
    out = run(chain=thin)
    assert out["outcome"] == "no_candidates" and out["candidates"] == []
    assert out["message"] == "No candidate built: no eligible contracts at your criteria."


def test_switching_expiration_is_a_horizon_amendment_recording_the_longer_horizon():
    far = (TODAY + dt.timedelta(days=95)).isoformat()
    out = run(params={"expiration": far})
    assert out["expiry_chosen"] == far and out["horizon_amendment"] == {"from_days": 30, "to_days": 90, "expiration": far}
    assert run()["horizon_amendment"] is None
    assert out["dte"] == 95 and out["history"]["basis"] in ("own history (pool average not available)", "pool average")


def test_events_are_shown_and_marked_not_filtered():
    ev = {"earnings": {"date": (TODAY + dt.timedelta(days=10)).isoformat(), "status": "scheduled"},
          "ex_dividend": {"date": (TODAY + dt.timedelta(days=12)).isoformat(), "status": "declared"}}
    out = run(events=ev)
    assert out["outcome"] == "ok" and out["filters"]["events"] == "shown, not filtered"
    by = {c["id"]: c["checks"] for c in out["candidates"]}
    assert all(c["earnings_before_expiration"] for c in by.values())
    assert by["hold"]["ex_dividend_before_expiration_short_leg"] and not by["single"]["ex_dividend_before_expiration_short_leg"]


def test_levels_are_the_60_day_closing_high_and_low_and_change_nothing():
    closes = walk()
    out = run()
    assert out["levels"]["high"] == round(max(closes[-60:]), 2) and out["levels"]["low"] == round(min(closes[-60:]), 2)
    assert "60-day" in out["levels"]["definition"]


def test_ties_go_to_lower_slippage_then_fewer_legs():
    a = {"pays_when_view_right": {"pct": 80.0}, "cost": {"dollars": 9.0, "pct_of_risk": 2.0}, "legs": [1, 2], "id": "a"}
    b = {"pays_when_view_right": {"pct": 80.0}, "cost": {"dollars": 7.0, "pct_of_risk": 3.0}, "legs": [1, 2], "id": "b"}
    c = {"pays_when_view_right": {"pct": 80.0}, "cost": {"dollars": 7.0, "pct_of_risk": 3.0}, "legs": [1], "id": "c"}
    assert [x["id"] for x in stage3.rank([a, b, c], "match")] == ["c", "b", "a"]


# ---- the workflow step ---------------------------------------------------------------------------

@pytest.fixture
def step(monkeypatch, store):
    calls = {"live": 0}
    opened = {"open": True}

    def live(symbol, store_=None):
        calls["live"] += 1
        return synthetic_chain(dtes=(9, 30, 95))
    monkeypatch.setattr(chain_data, "live", live)
    monkeypatch.setattr(session, "status", lambda when=None: {"open": opened["open"], "reason": "test"})
    monkeypatch.setattr(prices, "closes", lambda symbol, store_=None: {"closes": [(None, c) for c in walk()]})
    monkeypatch.setattr(fmp, "dividends", lambda symbol, store_=None: {"next_ex_dividend_date": None})
    monkeypatch.setattr(stage3, "pool_scaled_moves", lambda h: ())
    stage3._CHAINS.clear()
    import threading
    ctx = StepContext(store=store, request_id="r1", cancel=threading.Event(), deadline=float("inf"))
    state = {"symbol": "EXMP", "view": "bullish", "thesis": {"primary_horizon_days": 30},
             "figures": {"events": [{"kind": "earnings", "date": "2027-02-24"}]}}
    return lambda **more: stage3.contracts_step({**state, **more}, ctx), calls, opened


def test_the_step_reuses_the_chain_until_a_new_fetch_is_asked_for(step):
    run_step, calls, _ = step
    out = run_step()
    assert out["outcome"] == "ok" and out["events"]["earnings"] == {"date": "2027-02-24", "status": "scheduled"}
    assert out["events"]["ex_dividend"] == {"date": None, "status": "none declared"}
    run_step(contracts_params={"priority": "cost"})
    assert calls["live"] == 1                       # re-ranking does not fetch again
    run_step(chain_fetch=1)
    assert calls["live"] == 2                       # Retry or "Return to contracts" does


def test_the_step_reads_a_user_thesis(step):
    run_step, _, _ = step
    out = run_step(view="bearish", user_thesis={"view": "bearish", "primary_horizon_days": 30})
    assert out["thesis_origin"] == "user" and out["candidates"][0]["structure"].startswith("Bear")


def test_market_open_and_no_live_chain_falls_back_to_the_snapshot(step, monkeypatch):
    """Operator decision, 20 November 2026: Cboe, Tradier, then the snapshot; no failure screen."""
    run_step, _, _ = step

    def down(symbol, store_=None):
        raise chain_data.ChainUnavailable("Cboe delayed quotes: HTTP 403; Tradier: timeout")
    monkeypatch.setattr(chain_data, "live", down)
    snap = synthetic_chain(dtes=(9, 30, 95))
    snap["source"] = "snapshot"
    monkeypatch.setattr(chain_data, "snapshot", lambda symbol: snap)
    out = run_step()
    assert out["outcome"] == "ok" and out["provisional"] and "HTTP 403" in out["live_failed"]


def test_market_open_and_no_source_at_all_is_a_failure_naming_the_sources(step, monkeypatch):
    run_step, _, _ = step

    def down(symbol, store_=None):
        raise chain_data.ChainUnavailable("Cboe delayed quotes: timeout")

    def none(symbol):
        raise chain_data.ChainUnavailable("EXMP is not in the daily snapshot")
    monkeypatch.setattr(chain_data, "live", down)
    monkeypatch.setattr(chain_data, "snapshot", none)
    out = run_step()
    assert out["outcome"] == "source_failed" and "Cboe" in out["failed_source"] and "snapshot" in out["failed_source"]


def test_the_live_chain_is_cboe_first_then_tradier(monkeypatch):
    cboe = {"source": "live", "provider": "Cboe", "contracts": [1]}
    tradier = {"source": "live", "provider": "Tradier", "contracts": [1]}
    monkeypatch.setattr(chain_data, "live_cboe", lambda s, st=None: cboe)
    monkeypatch.setattr(chain_data, "live_tradier", lambda s, st=None: (_ for _ in ()).throw(AssertionError("not asked")))
    assert chain_data.live("EXMP")["provider"] == "Cboe"                      # Tradier is not asked when Cboe answers

    def refused(s, st=None):
        raise chain_data.ChainUnavailable("Cboe delayed quotes: cboe.chain: HTTP 403")
    monkeypatch.setattr(chain_data, "live_cboe", refused)
    monkeypatch.setattr(chain_data, "live_tradier", lambda s, st=None: dict(tradier))
    got = chain_data.live("EXMP")
    assert got["provider"] == "Tradier" and "HTTP 403" in got["fell_back"]

    def also(s, st=None):
        raise chain_data.ChainUnavailable("Tradier: tradier.chain: HTTP 401")
    monkeypatch.setattr(chain_data, "live_tradier", also)
    with pytest.raises(chain_data.ChainUnavailable, match="HTTP 403.*HTTP 401"):
        chain_data.live("EXMP")


def test_a_tradier_chain_has_the_same_shape_as_a_cboe_chain(monkeypatch):
    import json as _json
    from tradecraft import net, settings
    exp = (dt.date.today() + dt.timedelta(days=30)).isoformat()
    far = (dt.date.today() + dt.timedelta(days=400)).isoformat()
    occ = "EXMP" + dt.date.fromisoformat(exp).strftime("%y%m%d") + "P00250000"
    asked = []

    def get(url, params=None, **kw):
        asked.append((url.rsplit("/", 1)[-1], dict(params or {}), kw.get("bearer")))
        if url.endswith("quotes"):
            return _json.dumps({"quotes": {"quote": {"symbol": "EXMP", "last": 251.18}}}).encode()
        if url.endswith("expirations"):
            return _json.dumps({"expirations": {"date": [exp, far]}}).encode()
        return _json.dumps({"options": {"option": [
            {"symbol": occ, "bid": 10.65, "ask": 10.95, "open_interest": 14701,
             "greeks": {"mid_iv": 0.4203, "delta": -0.4284, "theta": -0.2142, "vega": 0.2766}}]}}).encode()
    monkeypatch.setattr(net, "get", get)
    monkeypatch.setattr(settings, "secret", lambda name: "t" if name == "TRADIER_TOKEN" else None)
    monkeypatch.setattr(chain_data._census(), "standard_roots", lambda feed: {"EXMP"})
    got = chain_data.live_tradier("EXMP")
    assert got["source"] == "live" and got["provider"] == "Tradier" and got["spot"] == 251.18
    assert [a[0] for a in asked] == ["quotes", "expirations", "chains"]       # the far expiration is not fetched
    assert all(a[2] == "TRADIER_TOKEN" for a in asked)
    c = got["contracts"][0]
    assert (c["occ"], c["type"], c["strike"], c["bid"], c["ask"], c["open_interest"]) == (occ, "put", 250.0, 10.65, 10.95, 14701)
    assert (c["iv"], c["delta"], c["theta"], c["vega"]) == (0.4203, -0.4284, -0.2142, 0.2766) and c["dte"] == 30
    monkeypatch.setattr(settings, "secret", lambda name: None)
    with pytest.raises(chain_data.ChainUnavailable, match="TRADIER_TOKEN is not set"):
        chain_data.live_tradier("EXMP")



def test_market_closed_uses_the_snapshot_as_provisional_or_says_wait(step, monkeypatch):
    run_step, calls, opened = step
    opened["open"] = False
    monkeypatch.setattr(chain_data, "snapshot", lambda symbol: synthetic_chain(dtes=(30,), source="snapshot"))
    out = run_step()
    assert out["outcome"] == "ok" and out["provisional"] and calls["live"] == 0

    def none(symbol):
        raise chain_data.ChainUnavailable("EXMP is not in the daily snapshot")
    monkeypatch.setattr(chain_data, "snapshot", none)
    stage3._CHAINS.clear()
    out = run_step()
    assert out["outcome"] == "market_closed" and out["message"] == "Contracts cannot be chosen until the market opens."


def test_the_cost_cap_control_moves_candidates_in_and_out_and_is_held_to_its_range():
    wide = synthetic_chain(dtes=(30,), spread=0.09)
    at = lambda cap: run(chain=wide, settings={"max_spread_pct": 10}, params={"cost_cap_pct": cap})      # noqa: E731
    assert len(at(10)["candidates"]) > len(at(5)["candidates"]) >= len(at(2)["candidates"])
    assert at(10)["filters"]["cost_cap_pct"] == 10.0 and at(50)["filters"]["cost_cap_pct"] == 10.0
    assert at(0.1)["filters"]["cost_cap_pct"] == 2.0 and at(3.3)["filters"]["cost_cap_pct"] == 3.5
    assert at("x")["filters"]["cost_cap_pct"] == 5.0 and at(7)["filters"]["cost_cap_default_pct"] == 5.0
    assert "above the 2% cost cap" in at(2)["filtered_out"][0]["removed_reason"]


def test_a_spread_may_use_a_leg_with_a_wide_quote_and_says_so_and_a_single_option_may_not():
    ch = synthetic_chain()
    for c in ch["contracts"]:
        if c["type"] == "call" and c["strike"] in (100, 105):
            c["bid"], c["ask"] = round(c["bid"] * 0.94, 2), round(c["ask"] * 1.06, 2)      # about 14% wide
    calls, puts = grids(ch)
    built, _ = stage3.build_candidates("bullish", 100.0, 5.0, calls, puts)
    move = next(e for e in built if e["id"] == "move")
    call_spread = next(c for c in move["constructions"] if c["name"].startswith("Bull call"))
    assert all(l["spread_above_setting"] and l["spread_pct"] > 5 and l["spread_setting_pct"] == 5.0 for l in call_spread["legs"])
    single = next(e for e in built if e["id"] == "single")["constructions"][0]
    assert single["name"] == "Long call, 95" and not single["legs"][0]["spread_above_setting"]


def test_an_expiration_up_to_three_sessions_before_the_horizon_date_can_serve_it():
    ok = stage3.eligible(synthetic_chain(dtes=(29, 57)), None)       # 18 November + 30 days is Friday 18 December
    without = stage3.expiration_options(ok, 30)
    assert [o["dte"] for o in without if 30 in o["horizons_served"]] == [57]
    opts = stage3.expiration_options(ok, 30, None, TODAY)
    near = next(o for o in opts if 30 in o["horizons_served"])
    assert near["dte"] == 29 and near["days_beyond"] == -1 and near["from_thesis"] and not near["poor_match"]
    far = stage3.eligible(synthetic_chain(dtes=(23, 57)), None)      # five sessions before: too early
    assert [o["dte"] for o in stage3.expiration_options(far, 30, None, TODAY) if 30 in o["horizons_served"]] == [57]


def test_a_single_option_states_its_strikes_distance_from_spot():
    ch = synthetic_chain(spot=102.0)
    out = stage3.select(ch, {"view": "bullish", "horizon_days": 30, "origin": "system"}, walk(), None, None, NO_EVENTS, pool=())
    single = next(c for c in out["candidates"] + out["filtered_out"] if c["id"] == "single")
    assert single["strike_distance_pct"] == 2.0 and "The strike, 100, is 2% below spot." in single["need"]


# ---- developer-only test failures ------------------------------------------------------------------

def test_both_test_failure_switches_are_off_in_the_repository():
    from tradecraft import testfail
    cfg = testfail.read()
    assert cfg["option_chain_fail_once"] is False and cfg["stage2_source_fail_once"] is False
    assert testfail.active() == []


def test_the_option_chain_switch_fails_once_per_request_and_then_the_retry_succeeds(step, monkeypatch):
    from tradecraft import testfail
    run_step, calls, _ = step
    monkeypatch.setattr(testfail, "read", lambda: {"option_chain_fail_once": True})
    testfail._used.clear()
    first = run_step()
    assert first["outcome"] == "source_failed" and first["test_failure"] and "Cboe" in first["failed_source"]
    assert "test failure" in first["message"] and calls["live"] == 0
    second = run_step(chain_fetch=1)                     # Retry
    assert second["outcome"] == "ok" and calls["live"] == 1
    assert testfail.active() == ["option_chain_fail_once"]


def test_the_stage_2_switch_fails_the_named_tool_once_per_request(monkeypatch):
    from types import SimpleNamespace
    from tradecraft import testfail, tools
    monkeypatch.setattr(testfail, "read", lambda: {"stage2_source_fail_once": True, "stage2_source_tool": "list_filings"})
    testfail._used.clear()
    ctx = SimpleNamespace(request_id="r9")
    wrapped, other = tools._fail_once("list_filings", lambda ctx, **kw: "ok"), tools._fail_once("get_earnings", lambda ctx, **kw: "ok")
    assert other(ctx) == "ok"
    with pytest.raises(testfail.TestFailure):
        wrapped(ctx)
    assert wrapped(ctx) == "ok"                           # the harness's one retry gets the real answer
    monkeypatch.setattr(testfail, "read", lambda: {})
    testfail._used.clear()
    assert wrapped(ctx) == "ok" and testfail.active() == []


def test_differing_far_strikes_take_the_pair_nearest_the_target_and_a_tie_the_cheaper_one():
    ch = synthetic_chain(strikes=[95, 100, 104, 106])
    for c in ch["contracts"]:
        if (c["type"], c["strike"]) in (("call", 106.0), ("put", 104.0)):
            c["open_interest"] = 1                       # calls can reach 104 only, puts 106 only
        if c["type"] == "put":
            c["bid"], c["ask"] = round(c["bid"] - 0.05, 2), round(c["ask"] + 0.05, 2)       # puts cost more to trade
    built, _ = stage3.build_candidates("bullish", 100.0, 5.0, *grids(ch))                   # the target is 105: a tie
    move = next(e for e in built if e["id"] == "move")
    assert [c["name"] for c in move["constructions"]] == ["Bull call spread (debit), 100 / 104"] and move["one_construction_only"]
    built, _ = stage3.build_candidates("bullish", 100.0, 5.6, *grids(ch))                   # the target is 105.6: 106 is nearer
    assert [c["name"] for c in next(e for e in built if e["id"] == "move")["constructions"]] == ["Bull put spread (credit), 100 / 106"]
    out = stage3.select(ch, {"view": "bullish", "horizon_days": 30, "origin": "system"}, walk(), None, {"cost_cap_pct": 10}, NO_EVENTS, pool=())
    kept = next(c for c in out["candidates"] + out["filtered_out"] if c["id"] == "move")
    assert kept["other_construction"] == {"available": False, "reason": "not available at these strikes"}
