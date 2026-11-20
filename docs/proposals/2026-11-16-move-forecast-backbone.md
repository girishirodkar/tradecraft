# Proposal: a move-forecast backbone for the thesis stage

**Date:** 16 November 2026
**Status:** NOT SUPPORTED. The test in section 8 was run on 16 November 2026 and failed (section 10). Nothing here is adopted.
**Affects:** Mode 3, step 2A (`docs/on-demand-mode-design.md`), and the thesis page (`docs/site/thesis-stage.html`).

---

## 1. Why this is on the table

Two measurements on 16 November 2026, on 20 years of daily prices for 105 names of the snapshot universe (`scripts/analysis/label_frequency.py`):

| Quantity | Result | Reading |
|---|---|---|
| Price trend (close against a moving average) | Shifts the chance of closing higher by −0.5 to −0.8 points in an uptrend and +0.6 to +1.1 in a downtrend. A name's effect in the first half of its history barely predicts its effect in the second (correlation 0.1 to 0.2) | Not usable. Stock-by-stock differences are noise, and the average has the wrong sign for a momentum reading |
| Volatility state (20-day realised against its one-year median) | A quiet state raises the chance of staying inside the usual range by about 6 points on the 7-, 14- and 30-day rows, in 99–100% of names. An active state lowers it by 6 to 8 points | Consistent across names. Fades beyond 60 days |

The thesis stage was built around direction, with move size added afterwards. The data supports the reverse. With trend removed, the present design returns no view on roughly 97 of 100 names today.

This agrees with what the specification already says: direction prediction is ranked near zero (§2), and volatility forecasting is described as "the core of any richness measure" (§6).

## 2. The proposal

**The thesis stage forecasts how far the underlying is likely to move. It does not issue a verdict on where it goes.** A view forms later, in step 8, when that forecast is set beside the move implied by option prices.

Every request then produces something usable, and "no view" stops being an empty result.

## 3. What the stage would produce

For each of the six horizons:

| Item | Source |
|---|---|
| **Usual range** | The band that held 68% of past moves of that length (replaces one standard deviation, which crisis periods distort) |
| **Forecast range** | The usual range scaled for today's volatility state, using the effect measured across the whole universe, not the name's own |
| **Event adjustment** | Where an earnings date falls inside the row, the range is widened using the name's own past earnings moves (input 6) and the row is marked |
| **Reading** | Quieter than usual, typical, or larger than usual |
| **Context, not a view** | Direction base rate, estimate-revision figure, risk flags, scheduled events, market regime |

Direction becomes an optional overlay supplied by the user. The system shows the base rate and the revision figure beside it and draws no directional label of its own.

## 4. Where the view forms

Step 8 already compares the system's figure with the market's. Under this proposal the comparison is forecast range against implied move:

| Comparison | Result |
|---|---|
| Implied move clearly above the forecast | Options look expensive for the expected move. Candidates: defined-risk premium-selling structures |
| Implied move clearly below the forecast | Options look inexpensive. Candidates: defined-risk long structures |
| No clear gap | No volatility view. If the user has supplied a direction, the system finds the cheapest way to express it; otherwise nothing is proposed |

The thesis stage still sees no option prices or implied volatility, so the comparison is not circular.

## 5. What stays and what changes

| Stays | Changes | Removed |
|---|---|---|
| Six horizons and the ladder layout | The central figure: a range, not a probability of closing higher | Trend as something that moves a probability |
| Volatility state definition | Range defined by the 68% band | The system's bullish and bearish labels |
| Risk flags, with no deductions | Universe-wide effects replace each name's own | The 4-point direction margin and the revision increments |
| Horizon recommendation rule (rule 4 reworded) | Revisions become a context line | The 50% condition |
| Limits, in the same spirit | The card leads with the range ladder | |
| Decision records, validation check, freeze | Step 8 compares ranges | |
| Five agents and thirteen inputs | Technical Analyst supplies levels and context only | |

Most of the design documented so far carries over.

## 6. What the existing research says

**In favour (specification sections):**
- §6: volatility is forecastable from daily prices; a two-component model beat trailing realised volatility by about a third on error, measured on the index.
- §6: the event decomposition is already specified, and one earnings day can hold over half the variance of a 40-day expiry.
- §4: the one positive single-name result is event-driven: implied volatility after an earnings announcement tends to be too high.
- §9b: technical levels are supported for strike and barrier placement, which a range forecast feeds directly.

**Against, or unresolved:**
- §6: implied volatility may already contain everything a model forecast knows. If so, the gap in section 4 is noise.
- §4: the single-name premium is unproven, and none of 24 delta-hedged single-name sorts was profitable after costs.
- §0b: rule-based index premium selling earned no excess return after May 2012.
- §6: for a row that spans earnings, the best estimate of the event move is the market's own, which this stage may not see. The stage would use past earnings moves, a weaker estimate, and step 6 would apply the market-based one.

**The proposal does not claim an edge.** It claims a better-founded forecast and an output on every request.

## 7. What it costs

- Rewriting the centre of the thesis page and step 2A. The three sample cards become one.
- One logged trial for the test below (the fourth of about twelve).
- The decisive question, whether the forecast beats the implied move, cannot be tested on free historical data. The snapshot archive has stored implied volatility only since 16 November 2026, so that test is forward-only.

## 8. The test proposed before adopting it

One pre-registered check on the cached prices, to be frozen in a script before it runs.

- **Question:** on data the rule has not seen, does scaling the usual range for the volatility state predict the actual range better than the usual range alone?
- **Method:** walk forward through each name's history. On each day, compute both ranges using only earlier data, with the state effect estimated across the universe from earlier data.
- **Measure:** how often the close lands inside each range, by state (target 68%), and a standard forecast-error score for the two ranges, on non-overlapping windows.
- **Rows:** 7, 14 and 30 days. The longer rows are reported but do not decide the result.
- **Pass:** the scaled range has the lower error on all three rows with a t-statistic above 2, and its hit rate is within 3 points of 68% in each state.
- **Fail:** the state adjustment is dropped and the stage reports the usual range only.

No variants would be run. A failure is recorded and stands.

## 9. Decision requested

1. Accept the direction of this proposal, subject to the test in section 8.
2. Or keep the present design with trend removed (the "research brief" option), without recentring the stage.
3. Or reject both and state what the thesis stage should do instead.

---

## 10. RESULT, 16 November 2026: Test R failed

Script `scripts/tests/range_test_r.py`, spec R-1, frozen and committed before its one run. 94 names (11 excluded for under 8 years of history). Scoring period January 2014 onward. Trial 4 of about 12 (`vrp_out/TRIALS.log`).

| Row | Windows | Error, usual range | Error, scaled range | Change | t | Hit rate, scaled (quiet / normal / active) | Hit rate, usual range (quiet / normal / active) |
|---|---|---|---|---|---|---|---|
| 7 days | 57,898 | 0.3032 | 0.3036 | −0.1% | −0.02 | 60.1 / 60.8 / 60.6 | 74.5 / 69.3 / 61.2 |
| 14 days | 28,867 | 0.2972 | 0.2975 | −0.1% | +0.03 | 60.4 / 60.4 / 61.3 | 72.9 / 67.2 / 59.1 |
| 30 days | 13,715 | 0.2872 | 0.2894 | −0.8% | −0.62 | 59.4 / 59.7 / 61.6 | 71.2 / 67.0 / 62.0 |
| 60 days (not decisive) | 6,748 | 0.2874 | 0.2908 | −1.2% | −1.72 | 59.2 / 61.7 / 62.5 | 67.5 / 66.8 / 62.8 |
| 90 days (not decisive) | 4,406 | 0.2726 | 0.2740 | −0.5% | +0.19 | 62.1 / 61.5 / 63.3 | 75.2 / 69.5 / 63.8 |

**Both pass conditions failed on all three decisive rows.** The scaled range was no more accurate than the usual range, and it contained the close about 60% of the time in every state against a target of 68%: it was too narrow throughout.

**Consequence, as pre-registered:** the state adjustment is dropped. The stage may report the usual range only. No variant of this test is to be run.

**What the result does and does not show.**
- The volatility state still carries information on unseen data: with the unscaled usual range, the close stayed inside it 71 to 75% of the time after a quiet state and 59 to 62% after an active one. That column was reported, not tested, and is not a pass.
- The scaling method did not turn that information into a better range. The multipliers were estimated from all earlier windows, and those under-stated how wide the range needed to be in the years scored. The synthetic self-test, where volatility regimes repeat, passed; real data, where they shift, did not.
- A different forecasting method (the one specified in §6 of the factor spec) would be a new configuration and a new trial. It was not run.

**Standing of this proposal:** the move-forecast backbone depends on a forecast that beats the usual range. That has not been shown. The proposal is not adopted.
