"""Stage 2's measured figures, the horizon rule and the range-bound rule. No network."""
import datetime as dt

import pytest

from tradecraft import context, figures, horizon

D0 = dt.date(2006, 1, 2)


def series(closes):
    return [(D0 + dt.timedelta(days=i), c) for i, c in enumerate(closes)]


def noisy(n, seed=1):
    import random
    rnd, out, c = random.Random(seed), [], 100.0
    for _ in range(n):
        c *= 1 + rnd.gauss(0.0004, 0.01)
        out.append(c)
    return out


def zigzag(n, up=1.01, down=0.995):
    out, c = [], 100.0
    for i in range(n):
        c *= up if i % 2 else down
        out.append(c)
    return out


def test_base_rate_counts_windows_that_closed_higher():
    closes = [1, 2, 3, 2, 1, 2]
    assert figures.base_rate(closes, 1) == (60.0, 5)
    assert figures.base_rate(closes, 2)[0] == 25.0          # 1>3? no; windows (1,3) up,(2,2) no,(3,1) no,(2,2) no


def test_typical_move_is_the_band_holding_68_percent_of_moves():
    closes = [100.0]
    for i in range(100):                                     # one-day moves of 1%..100% of a percent, in turn
        closes += [closes[-1] * (1 + (i + 1) / 10000)]
    assert figures.typical_move(closes, 1) == pytest.approx(0.68, abs=0.001)


def test_crossed_counts_a_daily_close_reaching_the_level_inside_the_window():
    closes = [100, 90, 100, 100, 100]
    below, above = figures.crossed(closes, 2, 5.0)
    assert below == pytest.approx(100 / 3)                   # only the window starting at 100 then 90
    assert above == pytest.approx(100 / 3)                   # only the window starting at 90


def test_volatility_state_quiet_normal_active_and_too_short():
    calm = zigzag(300, 1.002, 0.998)
    assert figures.volatility_state(calm)["state"] == "normal"
    assert figures.volatility_state(calm + zigzag(20, 1.03, 0.97))["state"] == "active"
    wild = zigzag(300, 1.03, 0.97)
    assert figures.volatility_state(wild + [wild[-1]] * 20)["state"] == "quiet"
    assert figures.volatility_state(calm[:100])["state"] is None


POOL = {"names": 94, "source": "test", "computed": "2026-11-18",
        "base_rate_pct": {"7": 50.0, "14": 50.0, "30": 50.0, "60": 50.0, "90": 50.0, "180": 50.0}}


def test_single_stock_is_blended_by_n_over_n_plus_k_and_long_rows_use_the_pool():
    m = figures.measure("NVDA", series(noisy(20 * 252 + 1)), POOL)
    rows = {r["days"]: r for r in m["horizons"]}
    assert [rows[d]["own_weight"] for d in (7, 14, 30, 60)] == [0.53, 0.47, 0.39, 0.29]   # the design's weights
    r = rows[30]
    assert r["base_rate_basis"] == "blended"
    assert r["base_rate_pct"] == pytest.approx(0.39 * r["own_base_rate_pct"] + 0.61 * 50.0, abs=0.3)
    assert rows[90]["base_rate_pct"] == 50.0 and rows[90]["base_rate_basis"] == "pool average"
    assert rows[180]["context_only"] and not rows[90]["context_only"]
    assert rows[7]["base_rate_uncertainty_pts"] == pytest.approx(1.5, abs=0.2)             # the design's table


def test_funds_use_their_own_history_and_short_histories_use_the_pool():
    m = figures.measure("SPY", series(zigzag(20 * 252 + 1)), None)
    assert all(r["base_rate_basis"] == "own history" and r["base_rate_pct"] == r["own_base_rate_pct"]
               for r in m["horizons"])
    young = figures.measure("NEWCO", series(zigzag(3 * 252)), POOL)
    assert young["short_history"]
    assert all(r["base_rate_pct"] == 50.0 and "under five years" in r["base_rate_basis"]
               for r in young["horizons"] if r["days"] <= 60)


def test_only_the_last_twenty_years_are_used():
    old = [100.0 - i * 0.001 for i in range(3000)]           # an early falling stretch that must be ignored
    m = figures.measure("SPY", series(old + zigzag(20 * 252 + 1)), None)
    assert m["years_of_history"] == 20.0


def test_real_pool_reads_only_single_stocks():
    import pytest
    from tradecraft import settings
    if not any((settings.ROOT / "label_out" / "prices").glob("*.json")):
        pytest.skip("the price archive (label_out/prices) is not published with the repository")
    p = figures.compute_pool()
    assert 80 <= p["names"] <= 96 and 50 < p["base_rate_pct"]["30"] < 65


# ---- the horizon rule ------------------------------------------------------------------

TODAY = dt.date(2026, 11, 18)


def ev(days, kind="earnings", **kw):
    return {"date": (TODAY + dt.timedelta(days=days)).isoformat(), "kind": kind, "label": kind, **kw}


ALL = {7: 5, 14: 5, 30: 5, 60: 5, 90: 5}


def test_recommends_the_row_nearest_30_days_and_never_180():
    r = horizon.recommend(TODAY, [], ALL)
    assert r["recommended_days"] == 30 and not r["provisional"] and r["warning"] is None
    assert 180 not in [x["days"] for x in r["rows"]]


def test_rows_without_eligible_contracts_are_excluded():
    r = horizon.recommend(TODAY, [], {**ALL, 30: 1, 14: 0})
    assert r["recommended_days"] == 7      # of 7, 60 and 90, the nearest to 30
    assert {x["days"]: x["status"] for x in r["rows"]}[30] == "no eligible contracts"


def test_rows_spanning_earnings_are_set_aside_in_favour_of_rows_ending_before():
    r = horizon.recommend(TODAY, [ev(20)], ALL)
    assert r["recommended_days"] == 14
    assert {x["days"]: x["status"] for x in r["rows"]}[30] == "spans an event"


def test_an_fomc_date_does_not_set_a_row_aside():
    assert horizon.recommend(TODAY, [ev(20, "fomc")], ALL)["recommended_days"] == 30


def test_when_every_row_spans_the_event_none_is_set_aside_and_a_warning_is_given():
    r = horizon.recommend(TODAY, [ev(3)], ALL)
    assert r["recommended_days"] == 30 and "spans a known event" in r["warning"]


def test_without_option_data_rule_two_is_skipped_and_the_result_is_provisional():
    r = horizon.recommend(TODAY, [], None)
    assert r["recommended_days"] == 30 and r["provisional"]


def test_no_row_with_contracts_means_no_recommendation():
    assert horizon.recommend(TODAY, [], {d: 0 for d in ALL})["recommended_days"] is None


def test_range_bound_candidates_are_the_7_and_14_day_rows():
    assert horizon.recommend(TODAY, [], ALL, range_bound=True)["recommended_days"] == 14


def contract(dte, spread_ok=True, strike=100.0, oi=500):
    return {"dte": dte, "strike": strike, "spot": 100.0, "bid": 2.0, "ask": 2.05 if spread_ok else 3.0,
            "open_interest": oi}


def test_eligible_counts_use_the_gate_criteria_without_dte_and_a_window_of_twice_the_horizon():
    chain = {"contracts": [contract(30), contract(45), contract(60), contract(61), contract(29),
                           contract(40, spread_ok=False), contract(40, strike=150.0), contract(40, oi=5)]}
    n = horizon.eligible_counts(chain, None)
    assert n[30] == 3                      # 30, 45, 60: default DTE of 42 to 90 is left out; 61 and 29 are outside
    assert n[14] == 0 and n[60] == 2       # 60 and 61
    assert horizon.eligible_counts(chain, {"max_spread_pct": 10, "min_open_interest": 10})[30] == 3


# ---- the range-bound rule --------------------------------------------------------------

def test_range_bound_needs_all_four_conditions():
    assert horizon.range_bound(None, "quiet", TODAY, [])["rows_met"] == [7, 14]
    assert not horizon.range_bound("bullish", "quiet", TODAY, [])["range_bound"]
    assert not horizon.range_bound(None, "normal", TODAY, [])["range_bound"]
    assert not horizon.range_bound(None, None, TODAY, [])["range_bound"]
    assert horizon.range_bound(None, "quiet", TODAY, [ev(10)])["rows_met"] == [7]
    assert not horizon.range_bound(None, "quiet", TODAY, [ev(2, "fomc")])["range_bound"]


def test_range_bound_event_that_counts_only_on_short_rows_and_unchecked_conditions():
    cpi = ev(5, "data_release", max_row_days=7)
    assert horizon.range_bound(None, "quiet", TODAY, [cpi])["rows_met"] == [14]
    r = horizon.range_bound(None, "quiet", TODAY, [], unchecked=["heavy earnings period"])
    assert not r["range_bound"] and "Could not be checked" in r["reason"]


# ---- numbers for the analysts ----------------------------------------------------------

def test_technical_inputs_are_the_agreed_definitions():
    s = series([100.0 + i * 0.1 for i in range(600)])
    t = context.technical(s, sector=series([100.0] * 600), market=None, sector_fund="XLK")
    assert t["trend"]["daily"]["close"] == "above" and t["trend"]["weekly"]["average"] == "30-week"
    assert t["momentum_pct"]["1 month"] == context.change(s, 21)
    assert t["levels"]["52 weeks"]["high_close"] == round(s[-1][1], 2) and t["levels"]["52 weeks"]["below_high_pct"] == 0
    assert t["relative_strength_3_months_pts"]["against_sector_fund"] == context.change(s, 63)
    assert t["relative_strength_3_months_pts"]["against_SPY"] is None
    assert "description only" in t["role"]


def test_earnings_reaction_spans_the_report_day_and_move_since_starts_before_the_item():
    s = series([100, 100, 110, 121, 121])
    day = s[2][0].isoformat()
    r = context.earnings_reactions(s, [day, "2030-01-01"])
    assert r[0]["move_pct"] == 21.0 and r[1]["move_pct"] is None
    assert context.move_since(s, day) == 21.0 and context.move_since(s, None) is None


def test_market_regime_and_sector_context_say_not_available():
    assert context.market_regime(None, None, None)["VIX"] == "not available"
    v = series([20.0] * 300)
    assert "normal" in context.market_regime(v, v, series([22.0] * 300))["VIX"]["term_structure"]
    assert context.sector_fund("Technology") == "XLK"
    assert not context.sector_context("X", "Unknown sector", v, None, None)["available"]
