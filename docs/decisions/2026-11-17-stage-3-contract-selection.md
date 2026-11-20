# Decision: stage 3 chooses contracts and ranks them by a chosen priority

*Retitled 17 November 2026. The first title, "recommends on trading cost", described the rule this record's amendment replaced.*

**Date:** 17 November 2026
**Decided by:** the operator
**Status:** in force, as amended later on 17 November 2026 (see "Amendment" below). Item 2 and the first line of "What it replaces" are superseded. Recorded in `docs/on-demand-mode-design.md`, "Stage 3 redesigned".

## The decision

1. **Stage 3 is re-centred on choosing contracts for a view.** It builds candidate structures by fixed rule and describes each on the same dimensions: payoff, base-rate chance of profit, structure-level cost, market-implied chance of profit, exposure, and event and assignment checks.
2. **The system recommends one candidate: the one with the lowest trading cost as a share of the amount at risk,** after removing candidates that fail liquidity, carry an event or assignment problem, or cannot fit the sizing rule.
3. **The recommendation is about efficiency. It is not a statement that the trade is worth taking.**
4. **The heavy valuation work is deferred:** event-volatility stripping, the volatility forecast, the surface fit and the richness residual.
5. Defined-risk structures only.

## Why

The original steps 4 to 8 assumed the operator brought the contract and asked whether it was fairly priced. Reviewed as a critic on 17 November 2026, they did not cover what is needed to choose one:

- The view's outcome was never translated into a structure's outcome.
- No payoff picture; no Greeks.
- Cost was measured per contract, not per structure.
- No rule linking horizon to expiry.
- No early-assignment check for single names.
- The valuation machinery informs single options and volatility trades, while the sizing rule pushes the operator into spreads; it also rests on a signal the spec grades weak, and two of its parts are blocked by missing data (earnings dates; implied-volatility history for single names).

A cost-based recommendation is defensible where a return-based one is not: a debit spread and a credit spread at the same strikes have nearly the same payoff, so choosing the cheaper is choosing between equivalents. That is the part of the problem the research found the system can do well.

## What it replaces

- "Candidates are never ranked." They are ranked on trading cost only. Ranking on gross richness remains prohibited.
- The probability pair of step 8 and its assumed drift.

## Open

- Earnings dates and ex-dividend dates have no data source; both checks show "not available" until they do.
- ~~Whether the base-rate chance of profit should be blended with the universe, as the base rate is.~~ **Decided 17 November 2026: yes.** Both history-based chance figures are blended with all single stocks, using the stage 2 weights, with moves scaled by each stock's usual range. Method in the design document.
- The strike distances are provisional.

## Amendment, 17 November 2026: single options, ranking by priority, expiry switching

Decided by the operator after reviewing the candidate set and the output layouts.

1. **Single bought options are candidates.** A long call for a bullish view and a long put for a bearish view, at the eligible strike nearest the price. The maximum loss is the premium, so they are defined risk. Not built: uncovered short options, cash-secured puts, covered calls, and structures across two expiries.
2. **Candidates are ranked by a priority the operator selects, not on trading cost alone.** Match the view (default): pays when the view is right. Larger payoff: what the candidate pays if the underlying moves one usual range in the view's direction, as a multiple of maximum loss (confirmed 17 November 2026, replacing maximum gain over maximum loss, under which a bought option always ranked first). Lowest cost: trading cost as a share of the amount at risk. Ties go to lower trading cost, then fewer legs. The first-ranked candidate is the recommendation.
3. **Trading cost still decides between the two constructions of one payoff shape,** because those are equivalent.
4. **Filters set candidates aside before ranking:** liquidity, a trading-cost cap, and events. (Sizing was a filter in the first draft of this amendment; see item 7.) Candidates set aside stay visible with the reason.
5. **The expiry defaults to the thesis horizon and the operator may switch** to an expiry serving another horizon of the research brief. Horizons leading to the same expiry are merged. A switch rebuilds the candidates and is recorded as an amendment to the horizon; the thesis record is not altered. An expiry more than twice the horizon away is marked a poor match.
6. **Output layout:** a ranked comparison in which the detail of one candidate expands in place.
7. **Sizing is an optional input on the output screen, not a filter.** Every candidate is shown for one contract. The operator may enter a maximum loss for the trade once prices are visible; contracts, loss, gain and cost are then restated to fit, as the figure is typed. Capital is not asked for. Reason: a loss figure requested before the contract prices are known would be a guess. Cost accepted: the limit of 0.217% of capital per position and the 4% cap across positions cannot be checked without a capital figure.
8. **Documentation marks what is a screen.** Each stage page labels every figure "application screen" or "explanation only". Stage 3 has one screen, the output.
9. **Chart levels are context in stage 3, and measured.** Support and resistance are drawn on each candidate's payoff chart and described in one sentence. They place no strike and do not affect filters or ranking. Each candidate's position relative to them is recorded so their value can be measured; they gain a role in strike placement only if that measurement supports it. The alternative, letting levels move the strikes, was considered and not adopted: nothing measured shows the levels hold, and their definition is arbitrary. The definition of a level is still open.

**Why.** The first version resolved only the choice between equivalent constructions and left the choice between different payoff shapes open. Those shapes are different trades, and the system has no evidence that one earns more, so a single fixed ordering would imply knowledge it does not have. Letting the operator state the priority keeps the ranking a fixed rule while making its basis explicit. "Match the view" is the default because the researched view states a direction and no size of move.

**Still open.** Whether stage 5 asks for capital, so that the limit across positions can run. **The poor-match mark is confirmed (17 November 2026) as a soft warning:** it removes nothing and does not affect ranking; the factor of two is a design choice; estimating value at the horizon is deferred. **The cost cap is confirmed (17 November 2026) as an adjustable control: default 5% of the amount at risk, range 2–10%.** The 5% is a design choice and will be reviewed against a count on stored chains. Earnings and dividend dates still have no source.

## Operator decisions for the build, 19 November 2026

Before stage 3 was built, the build session listed 22 gaps between this decision, `docs/product-shell.md` 6.3, the mock-up and the code already built. The operator ruled on all of them on 19 November 2026. The operator's six separate rulings were numbered 5 to 10; by their content they answer gaps 5, 8, 9, 11, 12 and 21 of the list, and they are recorded under those numbers here.

**Which contracts may form a leg**

1. **The DTE criterion is left out of leg eligibility,** as the stage 2 horizon rule already leaves it out. A leg must pass the other four stage 1 criteria in force and carry a valid quote. **The 7-day floor is kept:** no expiration under 7 DTE is offered (the gate considers 7 to 180 DTE). Reason: at the default 42 to 90 DTE the expiration serving a 30-day thesis has no eligible contract on any symbol.
2. **The strike-distance criterion is kept.** Where one typical move lies beyond it, the second strike moves to the nearest eligible strike, as the design words it, and the row states the distance used.
3. **A second strike that lands on the anchor, or does not exist on that side: the candidate is not built** and is listed with that reason.
4. **Strikes are placed where at least one construction is fully eligible.** If only one is, it is kept and the equivalent construction reads "not available: a leg fails the liquidity screen".
5. **There is no "Override and continue" in stage 3. This replaces the ruling of 18 November 2026** (product shell 6.3, third outcome). A stage 1 override carries forward without a second prompt. Legs still come only from passing contracts; if no leg can, the result is "no candidate built: no eligible contracts at your criteria". The stage 1 override panel adds: "The system only proposes contracts that pass the screen. If none pass at these criteria, no strategy will be built. Adjusting the criteria is the alternative."
6. **Market closed, symbol in the snapshot:** stage 3 runs on the snapshot with the gate screen's PROVISIONAL chip and source line. Continue stays allowed.

**Measures**

7. **Typical move for a DTE that is not one of the six rows:** NYSE sessions from today to the expiration are counted from `config/market_calendar.json`, and the typical move is measured for that many trading days.
8. **POP, market-implied:** the implied volatility of the eligible contract nearest the breakeven on its side; the at-the-money mean (call and put nearest spot) where that is missing. Risk-neutral, rate zero, the chance of finishing beyond the breakeven (between the two breakevens for a condor). **Labelled "approximate".** The implied move is as stage 4's check C5 defines it: at-the-money implied volatility scaled to the days to expiration.
9. **"Made money" in the two history-based figures** is payoff at expiration above zero with entry at mid; slippage is not deducted. **Both labels carry "before slippage".**
10. **Blend row when the DTE is midway between two rows:** the shorter row.
11. **Events are shown, not filtered.** The earnings date and the ex-dividend date are shown. Any row whose expiration falls after an earnings date, or after an ex-dividend date where it has a short leg, is marked. The filters line reads "Events: shown, not filtered". "None declared" for an ex-dividend date not yet declared; "not available" for symbols the data does not cover. Stage 4's event check carries the flag. **The control to include or exclude such candidates is deferred.** This replaces the events filter of amendment item 4 for the demo.
12. **Support and resistance are shown as the 60-day closing high and low that stage 2 computes:** drawn on the payoff chart and stated in the detail, labelled "60-day high" and "60-day low", context only. They are stored in the record with the name of the definition. They place no strike and do not affect ranking. (The definition of a level in general stays open, item 9 of the amendment.)
13. **Catalyst date:** the stage 2 record carries none, so "after the catalyst date" does not apply. On the after-the-demo list.

**Screen and record**

14. **Filtered-out candidates** use the same row layout below the "Filtered out" line: no rank, the reason in the grey line, Detail opens, not selectable.
15. **The outcomes of product shell 6.3 that the mock-up does not draw** are plain lines in the existing styles, as for 6.5.
16. **Bearish and range-bound row sentences mirror the bullish ones.** A long put's max profit is a dollar figure (the strike less the premium, the price falling to zero).
17. **Poor-match sentence:** "Poor match. Figures assume holding to expiration. Your thesis covers the first N days; closing then will give a different result."
18. **Header for a thesis the user entered:** "Your thesis, N-day horizon".
19. **Re-ranking and switching expiration reuse the chain already fetched.** It is fetched again only on Retry or "Return to contracts".
20. **The max-loss figure is recorded** when the field loses focus and at selection, not on every keystroke.
21. **A horizon amendment to an expiration that serves two horizons records the longer.**
22. **Range-bound:** iron condors are built and tested in the engine only, last, and dropped if time is short. (Its brief has no design, and it needs a quiet volatility state, which none of the 12 symbols measured on 18 November had.)

## As built on 19 November 2026, for the operator to correct

Choices the build made where the rulings above left room. None was put to the operator before it was built.

| Choice | As built |
|---|---|
| When an expiration counts as eligible | At least two eligible contracts on it, the gate's own minimum |
| A strike midway between two listed strikes | The lower strike |
| The two constructions land on different far strikes (one has an ineligible leg nearer the target) | The far strike nearest the target is used and the other construction reads "not available". On live chains this often keeps a construction built from in-the-money options, which costs more to trade (see `docs/build-log.md`) |
| The pooled history figure | The average across the pool's stocks of each stock's own share, as the stage 2 pool averages base rates |
| "The view's outcome" for a range-bound view | The underlying finishing within one typical move of where it started |
| A card that serves several horizons | Read against the thesis horizon where it serves it, otherwise the longest it serves |
| Where "before slippage" and "approximate" appear | In the three tiles of the detail and in one line under the table; the column heads are unchanged |
| The support and resistance sentence | States only whether each breakeven is above or below the 60-day low and the 60-day high |
| How a row is marked for an event | A sentence at the end of the row's grey line |
| The record's name for the first-ranked candidate | `best_fit_id` (the schema above says `recommended_id`) |
| While stage 3 computes | One line: "Opening the option chain and building the candidates." |
| Provisional line | "Snapshot of [date], [time] ET · market closed. Provisional: every figure is from the latest snapshot, not from live quotes." |
| Source failure | "The option data could not be retrieved." and "Source that failed: [source]." with the source's message |
| Market closed, no snapshot | "Contracts cannot be chosen until the market opens." and "This is consistent with what stage 1 showed: [SYMBOL] is not in the daily snapshot, so its liquidity could not be judged either." |
| Iron condors (ruling 22) | Built and tested in the engine. Not seen on a screen: no symbol is range-bound |

## The cost-cap control is on screen (operator decision, 19 November 2026)

Once stage 3 ran, the count the amendment asked for was made on live chains: at the 5% default, 35 of 72 candidates across 33 saved views were over the cap (54 at 2%, 15 at 10%), and two of the test symbols each lost a spread. The operator decided to build the on-screen control. The default stays 5% and the range 2% to 10%. As built: a slider in steps of 0.5, applied on release, for the current request only, recorded as a user decision, and kept on screen when every candidate is filtered out. The slider, its step and applying on release are the build's choices.

## Operator rulings on what the first runs showed (19 November 2026, afternoon)

1. **Expiration.** The default expiration for a horizon is the nearest eligible one on or after the horizon date, **or up to three trading sessions before it.** The gap is stated on the screen in either direction ("1 day before it", "27 days beyond it"). The poor-match rule is unchanged. *As built:* among the expirations allowed, the one nearest the horizon date in calendar days; a tie goes to the one on or after it. Reason: a 30-day horizon missed the monthly expiration by one day and was given one 57 days away.
2. **Leg criteria for a spread or an iron condor.** A valid two-sided quote, open interest and minimum premium on each leg; the bid-ask percentage criterion is judged on the structure through the cost cap, not on each leg. A single bought option keeps the per-leg criterion. A leg quoted wider than the user's setting carries a sentence in the detail. This amends rulings 1 to 4 of the build decisions above and is recorded as an amendment in `docs/decisions/2026-11-15-liquidity-controls.md`.
3. **The single option** is built at the nearest eligible strike and its row states the strike's distance from spot. No threshold.
4. **Stage 2 is not changed.**

**Confirmed by the operator as built (19 November 2026, afternoon).** Three points that the build had settled beside those rulings are now operator decisions:

- **The strike-distance criterion continues to apply to every leg,** of a spread, an iron condor and a single option alike.
- **Among the expirations allowed for a horizon, the one nearest the horizon date in calendar days is chosen; a tie goes to the one on or after it.**
- **The wide-leg sentence sits directly under that leg's row in "Legs and quotes".**

## The as-built table accepted, with three notes (operator decision, 19 November 2026, afternoon)

**Every row of "As built on 19 November 2026, for the operator to correct" is accepted** and is an operator decision from this date. Three notes for the record:

1. **An expiration is eligible with at least two eligible contracts, where "eligible" is stage 3's leg test for spreads:** a valid two-sided quote, open interest, minimum premium and strike distance. (Not the bid-ask criterion, and not the DTE criterion.)
2. **When the two constructions land on different far strikes, the pair nearest the target is used; on a tie, the one that costs less to trade.** The other construction reads "Not available at these strikes." This replaces the wording "not available: a leg fails the liquidity screen" of build decision 4.
3. **The pooled history figure is the average of each stock's own share,** as stage 2 pools its base rates. The design's wording ("the share of those scaled moves that finish beyond the break-even") could also be read as one share over all stocks' moves taken together; **it was read as the average of the stocks' own shares deliberately,** so that stages 2 and 3 pool in the same way and a stock with a longer history does not weigh more.

**The cost-cap control, as ruled:** a slider, 2% to 10%, steps of 0.5, default 5%, applied on release, **in the filters row in place of the static label.** It re-filters the candidates on screen without fetching the chain again. Each change is a decision record. (The first build had kept the static label and put the slider beside the row; the label is removed.)

**Demo symbols:** SPY and AMZN both stay. Shortlist for the recording, final choice on the day: TGT, CSCO, PYPL, AMZN, GOOGL, MSFT, NVDA, SPY. Figures for each are in `docs/build-log.md`.
