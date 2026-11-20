# Decision: the thesis stage produces a research brief with a researched view

**Date:** 16 November 2026
**Decided by:** the operator
**Status:** in force. Recorded in `docs/on-demand-mode-design.md`, step 2A.
**Relation to earlier decisions:** this keeps the decision of 15 November 2026 that the system drafts the thesis in Mode 3 (`2026-11-15-system-drafted-thesis.md`). It changes how the draft is formed and what it may claim.

## The decision

1. **The stage produces a research brief in two parts.** Measured figures, counted in code from price history: for six horizons the base rate of closing higher and the usual range, plus the volatility state. And a researched view, drafted by the agents.
2. **The agents draft the direction.** Bullish, bearish or no view, from filings, earnings materials, estimates and revisions, news, and sector and macro context.
3. **The system states no probability for a view. The brief shows the base rate beside it, counted in code, and the view changes no figure.** Every draft is labelled "researched view: no demonstrated predictive edge".
4. **Price trend is description only.** It supports no view and moves no figure.
5. **A range-bound view is set by rule** on the 7- and 14-day rows only: no directional view, a quiet volatility state, and no scheduled event inside the row. It is presented as a measured tendency and as context.
6. **Every view is logged and scored.** After about 100 resolved directional views, a view may carry a probability above the base rate only if the views have been right more often than the base rate, and then by the measured amount.

7. **Findings are combined by precedence, not weights (added 17 November 2026).** Company-specific evidence from the Fundamental Analyst decides whether there is a view and which way; sector and macro findings may support or oppose it but may not start one; conflicting company evidence gives no view; opposition from the backdrop is shown and the view is marked contested; the Technical Analyst has no say on direction.
8. **Index instruments have their own logic (added 17 November 2026).** Each has lead evidence that may start a view and qualifying evidence that may only support or oppose one. For SPY, SPX, XSP, QQQ and IWM the lead evidence is aggregate earnings and macro and policy; for TLT it is rates and policy. **The operator chose to let macro and policy start a view on the equity indices,** against the designer's recommendation of qualify-only, so that index views are available outside earnings season. Spec §9d found macro the least reliable basis for direction; the view claims no edge and is scored against the base rate.

## What it replaces

Earlier on 16 November the stage was specified as a probability computed in four layers: a base rate, a trend-conditional adjustment, fixed increments for estimate revisions, and limits; with per-row labels set by a 4-point margin and a 50% condition; and a range reading adjusted for the volatility state of each name. All of that is withdrawn.

## Why

Four measurements on 16 November 2026, on 20 years of daily closes for 105 names of the snapshot universe.

| Measurement | Script | Result |
|---|---|---|
| Label frequency under the four-layer design | `scripts/analysis/label_frequency.py` | 71% of names no view with revisions flat. Trend shifted the chance of closing higher by 0.5 to 1.1 points in the mean-reverting direction; split-half correlation of a name's trend effect 0.1 to 0.2. The directional labels were produced by noise |
| Revision-only "leans" at a 2-point margin | `scripts/analysis/lean_frequency.py` | A bearish lean was reachable on about 13% of names. Revision frequency could not be measured: the data source refused the requests |
| Volatility-adjusted range, out of sample | `scripts/tests/range_test_r.py`, spec R-1 | **FAIL.** Trial 4 of about 12. No error improvement on the 7-, 14- and 30-day rows; hit rate about 60% against 68% |
| Short-dated liquidity | 16 November snapshot | 25 of 106 names had two eligible calls and two eligible puts at 7 to 14 days to expiry at default settings; none of the three names in a quiet state did |

The move-forecast backbone proposed in `docs/proposals/2026-11-16-move-forecast-backbone.md` depended on the third measurement and is not adopted.

None of these measured whether an agent's reading of fundamentals and news predicts direction. That cannot be tested on past data, because the model may have seen the period. It is tested forward by the track record, which is why the view is drafted but carries no claimed edge.

## What was considered and rejected

- **A research brief with no system view.** Honest, but it abandons the operator's stated aim and learns nothing about the agents' views.
- **Rule-based leans from revisions.** Nearly bullish-only, resting on one unvalidated input, and the label would restate a figure already on the card.
- **Keeping the four-layer design.** It would have issued confident-looking labels that the data shows to be noise, including bullish labels on names below their moving average.
- **Searching for a better trend indicator, or re-running Test R with a different method.** Each would spend trial budget on a question chosen after seeing a failure.

## Risks accepted

- A well-written view reads as more convincing than it deserves. Mitigations: the probability is not the agents' to set; opposing evidence is shown; the Critic runs on a different model family in step 9; the operator may record a blind estimate first; position size is bounded by the sizing rule.
- Most bearish views will carry a stated probability under 50%.
- The range-bound view will usually be context, not a trade.

## Open

- Next steps after no view (proposed in the design document, not reviewed in detail).
- (Base-rate blending weights and the index flag list were settled on 17 November 2026; see the design document.) (Handling a list of tickers was taken out of scope on 17 November 2026: one ticker per request.)
- A volatility forecast by the method in spec §6, as a separately pre-registered experiment. Not scheduled.
