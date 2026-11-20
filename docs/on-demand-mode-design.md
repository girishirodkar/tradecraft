# On-Demand Mode — end-to-end design

**Date:** 16 November 2026 (step 2A rewritten as a research brief; system-drafted thesis added; now the build target; audit corrections 14 November; first issued 12 November 2026)
**Status:** stages 1 to 3 designed in full (stage 3 and stage 4 on 17 November 2026: "Stage 3 redesigned", "Stage 4 redesigned"); steps 10 onward are the earlier outline. Elicitation and critic sections filled from research strands 16 and 17.
**Depends on:** `docs/factor-spec.md` revision 12, especially §0a and §0b (measured), §5a–§5c (index instruments and structures), §3 (gate), §4 (single-name), §6 (volatility), §7 (execution), §8 (sizing).

> **Status, 15 November 2026: this is the mode being built.** Mode 1 (index overlay)
> is shelved — `docs/decisions/2026-11-15-mode-1-shelved.md`.

## Index instruments in this mode (added 15 November 2026)

SPY, SPX, QQQ, IWM and TLT are traded here, with any structure the operator
chooses. The 14 steps below apply unchanged. Three things are added when the
underlying is one of these:

1. **Instrument properties from spec §5a:** settlement style, ex-dividend dates
   and the early-exercise check on physically settled legs, and the 4% short-premium
   cap measured on beta-weighted exposure to SPY across all open index positions.
2. **Base-rate context from spec §0b**, shown at the base-rate step whenever the
   proposed structure is net short premium: rule-based index writing — at the
   money (BXM, PUT), 2% out of the money (BXY), 30-delta (BXMD) and the iron condor
   (CNDR) — earned no positive alpha after May 2012. The operator may proceed; the
   record stores that the context was shown.
3. **The tail design case:** a month in which realised volatility exceeds implied
   by 52 vol points (March 2020). Undefined-risk structures are displayed against
   it, with margin modelled (§5c).

The system does not originate index trades and does not rank index structures by
expected premium income.

---

## 1. What this mode is

The user names **one ticker**, or a specific contract on it, and asks for an assessment, outside any scheduled trigger. Expected to be the most-used mode.

**Scope, operator decision 17 November 2026: one ticker per request.** Handling a list of tickers is out of scope for now and is not designed. Screening many names belongs to the Mode 2 scan, which is built later and hands candidates to this pipeline one at a time.

**Since 15 November 2026 the system drafts the thesis by default** (operator decision, `docs/decisions/2026-11-15-system-drafted-thesis.md`). The user accepts, edits or rejects the draft, or skips it and supplies their own.

**The draft is a researched view with no demonstrated edge.** Direction prediction is worth ~7 bp/month at retail scale and the continuous single-name premium is not harvestable. That limits what may be claimed for the draft; it does not stop the system writing one. What the system contributes reliably is unchanged: cost analysis, probability honesty, base-rate confrontation, sizing discipline, and an immutable record — plus, now, a track record of its own theses that can be checked.

**It is a research assistant whose record you can audit, not an oracle.**

### The failure mode this design exists to prevent

The user brings an idea; the system, wanting to be useful, finds reasons to agree; the user acts with false confidence derived from their own prior reflected back with a number attached. That is worse than no tool.

The system-drafted path has its own version: the system writes a fluent thesis, a critic built on the same model agrees with it, and the user acts on two voices that were one. Step 2A and the critic rule in step 9 exist to prevent that.

---

## 2. Invariants

1. **Thesis is captured before any market data is displayed.**
2. **The thesis record is immutable once frozen.** Edits create a new record with a parent pointer.
3. **`thesis_origin` is recorded as `user`.** Measurement later splits information coefficient by origin, which is uncomputable retroactively.
4. **The liquidity gate retains full authority.**
5. **No cardinal score.** Ordinal panel with visible evidence grades.
6. **Both probabilities or neither.** Risk-neutral and estimated real-world side by side, gap labelled as the risk premium.
7. **Every assessed contract is shadow-labelled**, traded or not.
8. **The critic's objection is recorded even when overridden.**
9. **A falsifier emits a resting order ticket, never a notification.** (See §7.)

---

## 3. The sequence

### Step 0 — Invocation

| Input | System infers |
|---|---|
| Ticker only | proposes structures after thesis capture |
| Ticker + structure type | proposes strikes and expiries |
| Ticker + strike + expiry + side | assesses exactly that |

### Step 1 — Liquidity screen (cheap early exit)

*Revised 15 November 2026: live first, snapshot as history and fallback. The earlier version read only the daily snapshot, which limited the mode to names in `universe.txt` and ignored that one chain can be fetched in seconds.*

The question is the same either way: does this name carry at least two contracts that pass the gate (spec §3)? What differs is where the answer comes from.

| Situation | Source | What is shown |
|---|---|---|
| **Market open** | **Live chain fetch** for the named ticker, gate applied on the spot. Works for any optionable ticker, on the list or not | Pass or fail, qualifying-contract count, and — if the name is in `universe.txt` — its pass history from recent daily snapshots beside it |
| **Market closed**, name in `universe.txt` | Most recent mid-session snapshot | The same, **labelled with the snapshot date**, and marked provisional. Step 5 re-checks live before any order |
| **Market closed**, name not in `universe.txt` | None | "Liquidity cannot be judged until the market opens." The user may continue to the thesis; nothing downstream of step 4 runs until a live check has passed |

**Rules.**

- **"Market open" means regular hours on a trading day.** Quotes after the close are unusable (spec §0a: 35 names blocked on moneyness post-close against 4 intraday). The session check must know NYSE holidays and early closes; the census tool's `us_session()` does not, so the calendar is a build item for this step.
- **The live quote is 15 minutes delayed** on the free feed. That is fine for a screen and is stated on screen.
- **Where the live chain comes from (operator decision, 20 November 2026): Cboe, then Tradier, then the latest snapshot.** If Cboe does not answer, the chain is fetched from Tradier (real-time, on the operator's token) and the result is still live. If neither answers, the latest snapshot is used and the result is provisional, as in the market-closed row. The change is automatic, the screen names the source, and the same order applies wherever a later stage fetches the chain. Detail: `docs/decisions/2026-11-18-data-sources.md`.
- **A fail stops the request by default**, live or snapshot, with the reason (spread too wide, open interest too low, too few contracts). **The user can overrule it** — see below.
- **Snapshot history never overrides a live result.** A name that passed for a month and fails live today fails. History is context: it tells the user whether today's result is typical.
- **One ticker per request** (17 November 2026). Lists are out of scope for now.
- **The record stores** `liquidity_screen: {source: live | snapshot | none, as_of, passing_contracts, snapshot_history_days}`.

Measured on 12 Nov: only 36 of 103 liquid names carried ≥10 qualifying contracts; the median carried 7. Many requests end here, correctly, in a few seconds.

**The daily snapshot job** still supplies the history, the closed-market fallback, and the archive that cannot be rebuilt later. Since 15 November it also writes a spread ladder (`ladder_out/`): counts of tradeable contracts and names at ten bid-ask thresholds, by expiry.

#### The criteria are controls, not one fixed gate

Decided one at a time; full reasoning in `docs/decisions/2026-11-15-liquidity-controls.md`.

| Criterion | Status | Setting |
|---|---|---|
| Bid-ask gap | **Decided** | Default 5%, adjustable 2–10%. Strict for contracts the system proposes. A contract the user names may exceed it, with the cost shown and the override recorded. No bid, no ask, or bid above ask always fails |
| Open interest | **Decided** | Default 100, adjustable 10–1,000. Plus a size check: flag an order above 10% of the contract's open interest. Strict for the system's picks; overridable, and recorded, for a contract the user names |
| Expiry band | **Decided** | Adjustable 7–180 days; default 42–90, moved by the thesis horizon. The system never proposes under 7 days. A contract the user names may have any expiry, recorded. The daily snapshot stores 0–180 days from 16 Nov 2026 |
| Strike band | **Decided** | Default within 10% of the price, adjustable 5–30%. Strict for the system's picks; any strike for a contract the user names, recorded. To be expressed in delta later; the snapshot stores the feed's IV and Greeks from 16 Nov 2026 |
| Minimum price | **Decided** | Default $0.20, adjustable $0.05–$1.00. Strict for the system's picks; any price for a contract the user names, recorded. Under $1.00 the gap is also shown in dollars |

Where this section and the older sentence "the gate is not overridable" disagree, this section governs for Mode 3.

#### What the user sees at the end of step 1: a summary card (added 15 November 2026)

The gate does not present the list of passing contracts. A liquid ticker passes hundreds and there is no thesis yet to choose among them. It presents one screen:

- **Verdict line:** ticker, pass or fail, the number of contracts qualifying at the current settings, the source (live from Cboe, 15 minutes delayed; live from Tradier, real-time; or snapshot with its date) and the time.
- **Where the liquidity is:** qualifying-contract counts by expiry range and by calls and puts, with the user's current expiry setting marked and the ranges outside it shown for context.
- **Typical cost:** median, lowest and highest bid-ask gap of the passing contracts.
- **Why the rest failed:** counts by control.
- **One change away:** what a single setting change would unlock.
- **Recent history,** if the ticker is on the snapshot list.
- **Actions:** continue to thesis, adjust settings, view contracts (the full list, on request). On a fail, "overrule and continue" replaces "continue to thesis".

**No prices on the card:** no stock price, no option premiums, no implied volatility. It shows counts and trading costs only, so it does not anchor the user before step 2. Mock-up: `docs/site/liquidity-gate.html`.

*What step 1 passes to later steps is not specified here yet. It will be set out in a separate flow document covering the inputs and outputs of every stage.*

#### The user can overrule the gate (added 15 November 2026)

**The gate advises; the user decides.** When a ticker or a contract fails the gate, the request stops by default and the reason is shown. The user may overrule the result and send the ticker, or specific contracts, on to the next stage.

- **What can be overruled:** any of the five controls, the two-contract minimum, and a provisional or missing result when the market is closed.
- **What cannot:** a broken quote (no bid, no ask, or bid above ask). There is no price to carry forward, so there is nothing to overrule. *This exception is the designer's reading, not something the user stated; remove it if the user wants no exceptions.*
- **What the system does on an overrule:** shows the cost of the failing contract (the gap in percent and dollars, and the order size against open interest), asks for one line of reason, and writes a decision record marked `decided_by: user, overruled: liquidity_gate`.
- **What does not change:** the system still never proposes a failing contract on its own. An overrule moves contracts the user chose; it does not widen what the system will pick.
- **Step 5 still runs.** Overruled contracts are re-checked live before sizing, and the result is shown again. The user can overrule there too.

This supersedes "a fail ends the request" above and the older statement that the gate cannot be overridden.

### Step 2 — Thesis: two paths

**Path A, the default: the system drafts it (step 2A).**
**Path B: the user supplies it (step 2B).** Also the fallback when the Thesis agent returns `no_view` and the user still wants to proceed.

Both paths produce the same required fields and the same record.

### Step 2A — System-drafted thesis

**Revised 16 November 2026 (late): the stage produces a research brief.** It has two parts, kept apart on the card: **measured figures**, counted in code from price history, and **a researched view**, drafted by the agents. The Thesis agent emits `{view, basis, resolution_criterion, falsifiers[], evidence_grades{}, opposing_evidence[]}` or `{no_view: true, reason}`. **It does not emit a probability, and the system states none for a view.** Code places the base rate beside the view for reference. Decision record: `docs/decisions/2026-11-16-research-brief.md`.

**Inputs (operator decision, 16 November 2026).** Thirteen inputs feed the thesis. Sources marked *to confirm* depend on the provider probe (`scripts/analysis/probe_fmp.py`).

| # | Input | Source | Cost | How it is produced |
|---|---|---|---|---|
| 1 | Company filings (10-K, 10-Q, 8-K) | SEC EDGAR | Free | Retrieved, read by an agent |
| 2 | Earnings releases; call transcripts optional | EDGAR 8-K exhibits; transcripts from a paid provider | Free; transcripts paid | Retrieved, read by an agent |
| 3 | Company news | Paid provider's news feed, or the agent's web search | Paid, or model cost | Retrieved, read by an agent |
| 4 | Analyst estimates and recent revisions | Paid provider *(to confirm)* | Paid | Retrieved, read by an agent |
| 5 | Earnings date inside the horizon, with before-open or after-close timing | Paid provider *(to confirm)* | Paid | Retrieved |
| 6 | Reaction to past earnings reports | Earnings dates plus price history | — | Computed in code |
| 7 | Sector and industry context (spec §9c) | Sector ETF prices; company classification | With price data | Computed, read by an agent |
| 8 | Macro and geopolitical calendar and data (spec §9d) | FRED; Federal Reserve schedule | Free | Retrieved, read by an agent |
| 9 | Market regime: index trend, VIX level and term structure | Cboe index histories | Free | Computed, read by an agent |
| 10 | Trend and momentum on daily, weekly and monthly bars (spec §9b) | Daily price history | Paid | Computed in code |
| 11 | Support and resistance levels (spec §9b) | Daily price history | Paid | Computed in code |
| 12 | Relative strength against sector and market | Price history of stock, sector ETF and index | Paid | Computed in code |
| 13 | Historical volatility and the typical move over the horizon; base rate | Price history | Paid | Computed in code |

**Rules on the technical inputs (10–12).** Trend, momentum and relative strength are **description only** (revised 16 November 2026): they are shown on the brief and the chart, may not be cited in support of a direction, and move no figure. Support and resistance are description; in stage 3 they are shown beside each candidate as context and place no strike (revised 17 November 2026; they no longer set invalidation conditions). Timeframes are reported side by side, never combined into an agreement count. Chart patterns are shown with a weak grade; candlesticks, Fibonacci and Elliott wave are display only and do not feed the view. The chart is always drawn with the levels marked.

**Input 9 uses index-level VIX only.** It is a market-regime measure. The underlying's own option prices and implied volatility remain excluded from this stage (below).

**Input 13 supplies the probability, the usual range and the volatility state.** The method is set out below.

#### The research brief (operator decisions, 16 November 2026, late)

*This section replaces "Horizon, resolution criterion and probability" and "The range reading" as written earlier on 16 November. Those described a probability computed in four layers (base rate, trend, revision increments, limits), per-row labels set by a 4-point margin, and a range reading with a per-name volatility adjustment. All of that is withdrawn. The reasons are in the decision record and in `docs/proposals/2026-11-16-move-forecast-backbone.md`.*

**Measured on 16 November 2026** (20 years of daily closes, 105 names; `scripts/analysis/label_frequency.py`, `scripts/analysis/lean_frequency.py`, `scripts/tests/range_test_r.py`):

| Question | Finding | Consequence |
|---|---|---|
| Does price trend shift the chance of closing higher? | By 0.5 to 1.1 points, in the mean-reverting direction. A name's effect in the first half of its history barely predicts the second (correlation 0.1 to 0.2) | Trend is description only |
| Could estimate revisions alone carry a direction? | A bearish reading was reachable on about 13% of names. The frequency of revisions could not be measured (no data source) | No rule-based direction |
| Does scaling the range for the volatility state improve it? | **Test R, spec R-1, FAILED** on unseen data (trial 4 of ~12). No error improvement; hit rate about 60% against a 68% target | The usual range is reported unadjusted |
| Does the volatility state carry information? | With the unadjusted range, on unseen data the close stayed inside it 74.5 / 72.9 / 71.2% of the time after a quiet state (7 / 14 / 30 days), against 69.3 / 67.2 / 67.0% after a normal one and 61.2 / 59.1 / 62.0% after an active one. Observed, not a pre-registered pass | Range-bound view on the 7- and 14-day rows |

**Measured figures, in code, for six fixed horizons** (7, 14, 30 short; 60, 90 medium; 180 long, context only):

| Horizon | Independent windows in 20 years | Approximate uncertainty in one underlying's base rate |
|---|---|---|
| 7 days | ~1,040 | ±1.5 points |
| 14 days | ~520 | ±2 points |
| 30 days | ~240 | ±3 points |
| 60 days | ~120 | ±4.5 points |
| 90 days | ~80 | ±5.5 points |
| 180 days | ~40 | ±8 points |

1. **Base rate:** the share of past windows of the horizon's length in which the close finished above the starting close. Lookback up to 20 years, minimum 5. **Blended with the average of all single stocks (operator decision, 17 November 2026):**
   - *Measured:* across 105 names the spread of own base rates (2.5 / 3.3 / 4.5 / 5.9 / 6.6 / 8.3 points at 7 / 14 / 30 / 60 / 90 / 180 days) was only slightly wider than chance alone gives (1.8 / 2.5 / 3.7 / 5.1 / 6.2 / 8.5). The implied real difference between stocks is about 1.7 to 2.9 points on the 7- to 60-day rows and not detectable at 180 days.
   - *Formula, 7- to 60-day rows:* own weight = n / (n + k), where n is the number of independent windows in the stock's history (years × 252 / trading days in the row) and k = 900, 570, 380, 290 for the 7-, 14-, 30- and 60-day rows. That gives an own weight of 53 / 47 / 39 / 29% with 20 years, 36 / 31 / 24 / 17% with 10, and 22 / 18 / 14 / 9% with 5.
   - *90- and 180-day rows:* the average of all single stocks is used; the stock's own rate gets no weight.
   - *Two pools.* Single stocks are blended with single stocks. Index funds and ETFs use their own history, unblended. XSP uses SPX's history.
   - *Display:* the blended rate is the main figure; the stock's own rate is shown beside it. The stated range is that of the stock's own history (the wider of the two).
   - *Cautions:* the pool is made of today's large companies, so its average runs high and may flatter a weak recent listing; and because stocks move together the real differences are probably somewhat larger than measured, so k is provisional. Setting these weights scores no outcomes and spends no trial.
   - Displayed with its range. **Counted on split-adjusted closes, not dividend-adjusted,** because a view resolves on the actual closing price. (An earlier line said dividend-adjusted; that was inconsistent with the resolution criterion and is corrected.)
2. **Usual range:** the band either side of the starting close that held 68% of past moves of that length. This replaces one standard deviation, which crisis periods distort (one bank's 30-day figure was ±13.5% by standard deviation and ±9.1% by the band). **Not adjusted for the volatility state.**
3. **Volatility state:** 20-day realised volatility against its one-year median. Quiet below 80%, active above 120%, otherwise normal. One fixed definition, logged as a configuration.
4. **Trend:** close against a simple moving average (20, 50, 100, 200, 200, 200 days by row). **Description only.** No other indicator is to be searched for.

**The researched view, by the agents.**

- **View:** bullish, bearish, or `no_view`, for the primary horizon. It is the agents' reading of filings, earnings materials, estimates and revisions, news, and sector and macro context (inputs 1–4, 7, 8). It is a judgement, not a calculation.
- **What may not support a direction:** price trend, momentum and relative strength (10, 12); support and resistance (11); the underlying's option prices or implied volatility.
- **No probability is stated for a view (wording corrected 17 November 2026).** The brief shows the **base rate** of the view's outcome at the primary horizon, placed there in code, under the label "base rate" and never "probability". Bullish: the base rate of closing higher. Bearish: 100% minus it, which for most underlyings is under 50%; the brief says the view runs against the base rate. The view changes no figure.
- **Why:** whether an agent's reading of public information predicts direction cannot be backtested (the model may have seen the period). It is testable forward only.
- **How the view earns weight:** every view is logged and resolved. Once about 100 directional views have resolved, their hit rate is compared with the base rate. Only if they are right more often may a view carry a probability above the base rate, and then by the measured amount.
- **How the three analysts' findings are combined (operator decision, 17 November 2026): by precedence, not by weights.** Percentage weights would be invented numbers and would amount to a score.
  1. **Company evidence leads.** A directional view requires at least one company-specific finding from the Fundamental Analyst: a change in guidance, a revision to estimates, or a material filing or news item.
  2. **Sector and macro cannot start a view.** The Regime Assessor's findings may support or oppose a view that company evidence has established. Cost accepted: the system will not turn bearish on an underlying solely because its sector is deteriorating (consistent with spec §9c and §9d).
  3. **Conflicting company evidence means `no_view`.** The agent does not choose between, say, raised guidance and a newly filed offering.
  4. **Opposition from the backdrop is shown, not netted.** The view stands, the opposing evidence is listed, and the view is marked `contested`.
  5. **Every finding carries a grade, and a view needs solid evidence** (operator decision, 17 November 2026). A directional view requires at least one company-specific finding graded moderate or strong; for an index, one such finding from its lead evidence. "Thin" evidence means every company-specific finding is weak; "mixed" means the company evidence conflicts. Both give `no_view`.
     - **Grades are set by three checks, in code,** so the agents do not grade their own work. *Primary source:* a company filing, an earnings release or official data, not a report about them. *Recent:* dated within the last 30 days, or since the latest earnings report. *Specific:* concerns this company (for an index, the index itself), not the sector or market in general.
     - **All three passed: strong. Two: moderate. One or none: weak.**
     - A grade says how reliable a finding is. It makes no claim about predictive power and is not a measure of importance.
     - Grades define thin evidence and order the evidence on the brief. They are not summed, not turned into a score, and change no figure.
     - *The 30-day window is the designer's proposal.* Record schema: each evidence item gains `grade` and `checks{primary_source, recent, specific}`.
  - The Technical Analyst has no say on direction.

  **Stage 2 revised: anchored bearings and three outcomes (operator decision, 18 November 2026, night).** Decision record: `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`. Where it differs from the text above, it governs. The conflict rule and the grades are unchanged.

  - **What earns a bearing.** A finding carries a bearing only when the evidence states the comparison that gives it one. Three kinds can: **results against estimates** (reported EPS and revenue against consensus; the bearing is set in code from the two numbers, with 1% either side counting as in line, `config/stage2.json`); **a guidance change** (against the company's own earlier guidance for the same period, or the consensus for it; the analyst quotes both figures and code checks both are present); and **a new event** on the fixed list in section 3 of the decision, recent by the grades' test: dated within the last 30 days, or since the latest earnings report (amended by the operator on 19 November 2026; first written as "since the latest earnings report" only) (the analyst names the kind; code sets the bearing from the list and checks the date). **Everything else is context,** with bearing "none": it is kept, shown and may be quoted, and cannot start, support or cancel a view.
  - **The results-against-estimates finding always grades moderate:** recent and specific, not a primary source, because the comparison uses the data provider's reported and estimated figures.
  - **Mixed or in-line results** are one finding with bearing "none". Guidance raised on one measure and lowered on another is the same.
  - **Rejected signals** (`config/rejected_signals.json`) are not findings at all; the output check refuses them.
  - **Sector and macro findings carry bearing "none".** A sector fund's move is price action, and no source for macro expectations exists. They are shown as context under "Sector and macro backdrop". `contested` stays in the record and cannot be set until such a source exists. **For an index instrument this means lead evidence cannot carry a bearing: the request returns no view (nothing carries a direction) and offers "Take a view yourself".** Scheduled events still raise the existing risk flags and feed stage 4's event check.
  - **What is enough for a view.** Any one bearing-carrying finding graded moderate or strong can start a view, including results against estimates alone. A view resting on the earnings result alone is recorded `support: weak` and shown as "weakly supported", with the number of days since the report. The marking blocks nothing.
  - **Three outcomes.** A view; no view because the bearing-carrying findings conflict; no view because nothing carries a direction. Declined (a severe flag) and insufficient data are unchanged. A technical failure is never a no view.
  - **After a no view the user may "Take a view yourself"** (step 2B, structured form), or stop. Stop still records nothing.
  - **Stability test:** the Fundamental Analyst run twice on the same stored evidence must produce identical bearings.

  **Clarification of the precedence rules (operator, 18 November 2026, after the first live runs on NVDA and AMZN, which both returned no view).** The design was silent on these points. The rule on conflicting company evidence in "Five points settled for the build", point 1, is kept and is not otherwise changed.
  
  - **A conflict exists only between company-specific findings graded moderate or strong** (and, by point 1, from a primary source). A weak finding never creates a conflict.
  - **A weak finding against the view is listed as contrary evidence and does not cancel the view.**
  - **Superseded in part the same night (operator decision, 18 November 2026; `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`, section 4).** The primary-source limit on a conflict is withdrawn: **two bearing-carrying findings graded moderate or strong with opposite bearings give no view.** Primary source is one of the three grade checks and nothing more; it is not a separate condition for a conflict. The limit was a stopgap against opinion and tone creating conflicts, which the anchored-bearing standard below now prevents.
  - **A standing disclosure carries no bearing.** A long-standing risk factor, ongoing litigation or any other disclosure repeated from earlier filings, and not something new, is reported with bearing "none". The Fundamental Analyst marks such a finding as a standing disclosure and code sets its bearing to "none", so it can neither support a view nor conflict with one.

- **Index instruments: separate logic (operator decision, 17 November 2026).** An index has no company-specific evidence. Each instrument has *lead* evidence, which may start a view, and *qualifying* evidence, which may only support or oppose one.

  | Instrument | Lead evidence | Qualifying evidence |
  |---|---|---|
  | SPY, SPX, XSP | Aggregate earnings (index-level estimate revisions, earnings-season results); macro and policy (growth, inflation and employment data, the central bank's path) | Rates and credit conditions |
  | QQQ | Aggregate earnings, with results and guidance from its largest holdings; macro and policy | Rates |
  | IWM | Aggregate small-cap earnings and estimate revisions; macro and policy | Credit conditions |
  | TLT | Rates and policy (inflation trend, the central bank's path, Treasury supply) | Growth data |

  1. A directional view requires at least one finding from the lead evidence.
  2. Qualifying evidence cannot start a view.
  3. Conflicting lead evidence (for example aggregate earnings against macro and policy) means `no_view`. Neither takes precedence (confirmed by the operator, 17 November 2026).
  4. Opposition from qualifying evidence is shown, not netted; the view is marked `contested`.
  5. Index trend, breadth and VIX remain description and risk context.
  - **Macro and policy may start a view on the equity indices.** The operator chose this over "qualify only" so that index views are available outside earnings season. The designer recommended qualify-only; spec §9d found macro events the least reliable basis for direction and says to generate no entries from the macro calendar. The view claims no edge and is scored against the base rate, as for single names.
  - The Fundamental Analyst covers aggregate earnings and the largest holdings; the Regime Assessor leads on macro and policy for the equity indices and on rates and policy for TLT. No additional agent.
  - Measured figures, the base rate shown beside the view, the label, the scoring, the range-bound rule and the index flag list apply unchanged. Aggregate index estimates need a data source (unresolved).
- **Evidence families:** fundamentals and expectations; news and events; sector and macro. One supporting family marks the view weakly supported. Opposing evidence is listed beside supporting evidence.
- **Label on every draft:** "researched view: no demonstrated predictive edge."
- `no_view` is a first-class result.

**The range-bound view, by rule.** All four conditions: the agents returned no directional view; the volatility state is quiet; the row is the 7-day or 14-day row; no earnings date or flagged event falls inside the row.

- Stated as a measured tendency (about 75% and 73% inside the usual range, against 68%), labelled "measured tendency: not a trade signal".
- **Context far more often than a trade.** In the 16 November snapshot, 25 of 106 names had two eligible calls and two eligible puts expiring in 7 to 14 days at default settings (46 at a 10% spread limit; 44 and 95 at 22 to 41 days), and none of the three names then in a quiet state was among them. Where no eligible contracts exist at the horizon, the brief says so and offers a 22- to 41-day expiry closed early.
- Not evidence that options are overpriced. That comparison (the richness work of step 6) is deferred; stage 3 shows the market-implied move beside the usual range and nothing more. Spec §0b context is shown; defined-risk structures only.
- An active state creates no view; it is reported as a note.
- Every range-bound row is logged and scored; the rule is reviewed after about 100 have resolved.

**Invalidation and risk exit are separate (operator decision, 17 November 2026).**

| | Thesis invalidation | Risk exit |
|---|---|---|
| Question | Has the reason for the view gone? | Has the loss reached the limit set in advance? |
| Based on | Evidence | Price, or the value of the position |
| Set by | The agents: each finding the view rests on is paired with what would reverse it | Code, by a fixed rule |
| Example | Guidance is lowered; estimates are revised down by more than 2%; a flagged ruling goes against the company | A daily close one usual range against the view |
| Where set | Step 2A | Step 12 (barriers), once the structure is known |

- **Step 2A states evidence-based invalidation conditions** (`falsifiers[]`), one for every load-bearing finding. Risk flags may add others. **No invalidation condition is a price level.**
- **Step 2A also shows a risk reference:** the price one usual range against the view, with how often a level that far away has been crossed. Measured 17 November 2026 (median of 105 names, share of past periods in which a daily close reached the level): one usual range below, 21 / 23 / 23 / 22 / 23% on the 7 / 14 / 30 / 60 / 90-day rows; one usual range above, 24 / 27 / 30 / 33 / 34%; half a usual range below, 41 to 50%; one and a half below, about 10 to 11%. It is information only. The risk exit is set in step 12, on the position.
- **Range-bound views** are invalidated when the volatility state turns active or the company makes an unscheduled announcement.
- **Support and resistance are no longer used for invalidation.** A chart-level rule (nearest swing low within a distance band) was proposed and withdrawn on review: the definition is arbitrary, the distance band did the work and the level added only a story, a price move does not falsify an evidence-based view, and the 16 November measurement found these names slightly more likely to rise after falling. A price exit is discipline and loss control (spec §8a), not prediction. Chart levels remain as description, shown beside each candidate in stage 3 (see "Chart levels in stage 3").
- **Dependency:** evidence-based conditions need the Monitor agent to watch filings, estimates and flagged events while a position is open. Its detailed design is open.
- Record schema: `risk_reference{level, usual_ranges_away, crossed_pct}`; each `falsifiers[]` entry gains `finding_id` and, for stage 4 check 8, `type` (fixed list; see "Stage 4 redesigned").

**Resolution criteria.**

| View | Outcome that makes the view correct |
|---|---|
| Bullish | The underlying closes above the reference close at the horizon |
| Bearish | It closes below the reference close at the horizon |
| Range-bound | It closes within the usual range either side of the reference close at the horizon |

**Primary horizon: recommended by a fixed rule in code; the user may select any other row.** Chosen before any option price is shown.

1. Exclude the 180-day row.
2. Exclude rows without eligible contracts expiring on or after the horizon date (counts only).
3. Set aside rows that span an earnings date or a flagged binary event, preferring rows that end before it. If every remaining row spans the event, none is set aside and the recommendation carries a warning.
4. Recommend the remaining row nearest 30 days.

For a range-bound view only the 7- and 14-day rows are candidates. The rule takes no account of how strong any row looks. The recommendation and the user's selection are each a decision record. If no row has eligible contracts, no recommendation is made; when the market is closed and no snapshot covers the underlying, rule 2 is skipped and the recommendation is marked provisional. All six measured rows are logged and resolved whichever is primary.

**When there is no view (operator decision, 17 November 2026).** The brief is still produced. Three kinds: nothing found; declined (severe flag); insufficient data. **The user has two options and no others:**

1. **Stop.** The workflow ends and the user returns to the application's home page. **Nothing is written to the permanent record:** no decision records and no scoring entry. This is an exception to the rule that every request is logged and resolved. Cost accepted: the system cannot later report how often it returned no view or how the underlyings it passed on behaved.
2. **Supply a thesis.** The user enters a thesis as free text and the system evaluates it and reports on its credibility (step 2B, as revised below). After a declined result this is an override: the flag stays attached and a decision record is written.

The earlier "check again later" option is removed. The user may submit the same underlying on another day. The agents are not asked again for a different answer.

**What step 2 hands on (operator decision, 17 November 2026): a short brief, a complete record.** A longer write-up does not help the later steps, which work from fields, and makes a view read as stronger than the evidence warrants.

| Layer | For | Content |
|---|---|---|
| The brief | The user | The view, the measured figures and the main evidence, on one screen |
| Expandable detail | The user, on request | Every finding, with source, date, grade and bearing |
| The record | Steps 3 onward | Every field in structured form, with the complete evidence set |

- **Catalyst timing (new field).** Whether the view depends on a dated event, and when: `catalyst{dated: bool, date, finding_id, note}`. Set by the Thesis agent. A view that turns on a decision expected on day 12 calls for a different expiry from one resting on estimates that have already risen.
- **The complete evidence set travels with the record** (`evidence[]`, every finding with `id, source, date, family, grade, checks{}, bearing, shown_on_brief`; `family` added 17 November 2026 for stage 4), including findings not shown on the brief. The Critic in step 9 checks the evidence, not a summary.
- **Nothing about option prices is in the record.** Step 4 opens the chain for the first time.
- The validation check confirms the view is marked dated or undated.

**Record schema:** `horizons[]` (per row: `base_rate_pct`, `base_rate_range`, `usual_range_pct`, `event_inside`), `volatility_state`, `trend_state` (description), `view`, `view_origin` (`agents` | `rule` | `user`), `view_base_rate_pct`, `view_probability_pct` (null until the track record permits a figure above the base rate), `contested` (boolean), `primary_horizon_days`, `recommended_horizon_days`, `horizon_recommendation_reason`, `opposing_evidence[]`.

#### Five points settled for the build (operator decisions, 18 November 2026, night)

Raised as design gaps before stage 2 was built; the operator accepted the build session's recommendation on each. Where one differs from the text above, this section governs.

1. **What counts as conflicting company evidence (precedence rule 3).** *Superseded the same night: the primary-source limit is withdrawn; see "Stage 2 revised: anchored bearings" above.* Only **primary-source** company findings graded moderate or strong can conflict: a company filing or an earnings release pointing one way against another pointing the other. That gives `no_view`. An opposing company finding that is not from a primary source (company news, a provider's figures) does not conflict: it is listed as opposing evidence and the view is marked `contested`. *Why:* company news is now an input, and nearly every large company has a recent item on each side, so the strict reading would make `no_view` the result on almost every name. The design's own example (raised guidance against a newly filed offering) is two primary sources.
2. **The grade of a finding.** A finding takes the grade of its **best** cited evidence item. A data provider's copy of a company's reported figures (FMP's earnings actuals and surprises) is **not** a primary source; the company's own 8-K or earnings release is. The analyst consensus is not a primary source. A company profile has no date and so never passes "recent".
3. **Sources for inputs 7 and 9 (sector context and market regime).** Sector: the company's sector from the FMP profile, mapped to one of the eleven SPDR sector funds (`config/data_sources.json`, `sector_funds`), with price history from the Yahoo chart endpoint. Market regime: SPY's trend, and the VIX level and term structure from `^VIX` and `^VIX3M` on the same endpoint. If any of these cannot be fetched the input is "not available". Index-level VIX only, as before.
4. **What is computed for the Technical Analyst (inputs 10 to 12).** All in code, from daily closes; the agent describes them and computes nothing.
   - *Trend:* the close against its 50-day, 30-week and 10-month simple moving averages (daily, weekly and monthly bars).
   - *Momentum:* the percentage change over 1, 3 and 12 months (21, 63 and 252 trading days).
   - *Levels:* the highest and lowest close of the last 52 weeks and of the last 60 trading days. No swing detection.
   - *Relative strength:* the 3-month change minus the sector fund's, and minus SPY's.
   - These are description only, as before. They are definitions for display, not signals; none is tested or tuned.
5. **Primary-horizon rule 2, made exact.** A row has eligible contracts when at least two contracts pass the stage 1 criteria in force for the request, leaving out the DTE criterion, and expire **on or after the horizon date and no more than twice the horizon away** (the point at which stage 3 marks an expiry a poor match; stage 3 has no narrower window). Counts only; no price leaves the rule.

#### Risk flags: no deductions (operator decision, 16 November 2026)

Inputs 1, 2, 3, 7 and 8 are read for a defined list of flags. An agent decides whether a flag is present and cites the evidence. It may not invent a flag. If it believes something matters and no flag fits, it reports the item in the evidence list and the flag list is reviewed later.

**Single-name underlyings (core set, operator decision 16 November 2026):**

| Flag | Trigger | Effect |
|---|---|---|
| Going-concern or liquidity warning | Stated in the latest annual or quarterly report | `no_view` |
| Announced merger or takeover | The company is the target of an announced transaction | `no_view` |
| Pending binary event | A dated court ruling, regulatory decision or shareholder vote inside the horizon | Invalidation condition; reduce size |
| Dilution | A share offering or shelf registration filed in the last 90 days | Reduce size |
| Guidance reduction | Guidance lowered at the latest report | Reduce size |
| Material litigation or regulatory action | A new 8-K or a newly added risk factor, not standing disclosure | Reduce size; invalidation condition where a ruling date is known |
| Fed decision inside a short horizon | A scheduled Federal Reserve meeting inside a primary horizon of 14 days or less (narrowed 17 November 2026: inflation and employment releases removed for single names, since one falls inside almost every 14-day period) | Reduce size |
| Sector-wide move | The recent move matches the sector's, with no company-specific outperformance | Note on the card only |

**Index instruments (confirmed by the operator, 17 November 2026).** The filings, earnings and sector flags do not apply to SPY, SPX, XSP, QQQ, IWM or TLT. Macro and calendar flags take their place.

| Flag | Trigger | Applies to | Effect |
|---|---|---|---|
| Fed decision | A scheduled Federal Reserve meeting inside a primary horizon of 14 days or less | All | Reduce size; no range-bound view on that row |
| Inflation or employment release | CPI or the monthly employment report inside a primary horizon of 7 days | All | Reduce size; no range-bound view on that row |
| Heavy earnings period | Holdings making up at least 20% of the index report inside a primary horizon of 14 days or less | SPY, SPX, XSP, QQQ, IWM | Reduce size; no range-bound view on that row |
| Treasury refunding | The quarterly refunding announcement inside a primary horizon of 30 days or less | TLT | Reduce size |
| Fiscal deadline or national election | A funding or debt-ceiling deadline, or a national election, inside the primary horizon | All | Reduce size |

- **Triggers are set so that a flag is the exception.** A flag that is nearly always raised says nothing and would shrink every position. Inflation and employment reports are each monthly, so any 14-day period contains one. The designer proposed dropping them as flags; **the operator kept them, because a miss or beat on those figures moves the market and matters for short-dated contracts.** They are therefore flagged on the 7-day horizon, where they are present roughly half the time.
- **Every scheduled release is shown regardless of flags.** For an index the brief lists each Fed decision, inflation release and employment report inside the primary horizon, with its date and with the index's usual move on past release days beside its usual move on an ordinary day. Counted in code from price history and the release calendar (free sources).
- **Dropped:** monthly long-bond auctions (too frequent); index rebalance (affects holdings more than the index level).
- *The 7-, 14- and 30-day windows and the 20% earnings threshold are the designer's proposals.*

A stressed-market condition is not a flag: it is already carried by the market-regime input and must not reduce size twice.

**Two rules on size reduction.** Any number of size-reducing flags on one thesis produces a single reduction; they do not compound. A flag reduces size only where it works against the view or raises the likelihood of a large move in either direction (a guidance reduction counts against a bullish thesis, not a bearish one).

**A flag does three things and nothing else:** adds an invalidation condition; marks the thesis as carrying event risk, which reduces position size in step 11; or, when severe (going-concern warning, announced merger), produces `no_view`.

**A flag does not change the probability.** A scheme of 2 points per ordinary flag, 4 per major flag and an 8-point ceiling was proposed and rejected, because: the base rate already contains the average effect of such risks, so a deduction counts it twice; the information is public and largely priced; flags are common enough that routine deductions would lower every probability; the design would be asymmetric, raising by a few points and lowering by many, which understates bullish theses; and many flags concern the size of a move, not its direction, for which smaller size is the right response.

**Flags are measured.** Each is logged with the thesis. Once enough theses have resolved, flagged and unflagged theses are compared by flag type. A deduction is introduced only for a type shown to predict worse outcomes, at the measured size.

**Removed on review, 16 November 2026:** restatement (not expected to help); trading halt (relevant to OTC names, not to the liquid underlyings this system covers); insider selling cluster (not supported by this project's research); margin deterioration and revenue shortfall (already reflected in guidance and in estimate revisions); sector trend opposing the view (price-derived, already covered by the long-term trend row).

*The flag windows are provisional.* The record schema gains `risk_flags[{flag, input, evidence_id, effect}]`.

*(The price-only baseline is withdrawn with the trend layer, 16 November 2026. The base rate is the single baseline every view is scored against.)*

#### Safeguards on the inputs (revised 16 November 2026, late)

Thirteen inputs make a view better informed. They are not expected to make it better at predicting direction, and they make it read as more convincing than it is. Four rules contain that.

**1. Every input has a stated role, and the role limits what it can do.**

| Role | Inputs | What the input may do |
|---|---|---|
| Anchor | 13 (base rate, usual range, volatility state) | Supplies the probability. Is not adjusted by the view |
| Guard | 5, 6 (earnings date, past reactions) | Can force a change of horizon or a warning. Cannot change the probability |
| Levels | 11 (support and resistance) | Shown as description, and beside each candidate in stage 3 as context. Sets no direction, strike, invalidation condition or exit (revised 17 November 2026) |
| Risk context | 9 (market regime) | Feeds sizing and the regime note. Not an entry signal |
| Evidence and risk flags | 1, 2, 3, 4, 7, 8 (filings, earnings releases, news, estimates and revisions, sector, macro) | Support or oppose the researched view. Raise risk flags from a defined list. Cannot change the probability |
| Description only | 10, 12 (trend, momentum, relative strength) | Shown on the brief and the chart. May not support a direction or change the probability |

**2. The agents set no figures.** The base rate shown beside a view is counted in code.

**3. Opposing evidence is shown** beside supporting evidence, with the same grading. A brief that shows only support fails the validation check.

**4. The view is scored against the base rate.** If directional views are not right more often than the base rate once about 100 have resolved, the report says the views add no predictive value.

*Withdrawn: the "weak directional evidence" role, the price-only baseline, and the limits of ±5, ±3 and ±10 points. With no computed departure from the base rate there is nothing for them to bound.*

**What it may not see: option prices, implied volatility, or any market-implied probability.** Step 8 compares the thesis probability with the market-implied one. If the Thesis agent has seen the market's number, that comparison is circular.

**What it may not use:** anything on the dead list in spec §10. A user who wants a view built on those brings it through path B.

**Rules on the output:**

- `no_view` is a first-class result. A system that must produce a view on every ticker manufactures theses.
- Probability as integer percent. No cardinal score, no 0–100 rating.
- Every claim carries an evidence grade, and the draft is displayed under the label **"unvalidated: no demonstrated predictive edge."**
- The view may be range-bound, by the rule above. That is distinct from no view.

#### Agents in this stage (16 November 2026)

Five agents, in a fan-out and a merge. No debate between them.

| Agent | Inputs | Output |
|---|---|---|
| Evidence Retriever | Fetches 1–5 and 8; stores each item with source and time | The evidence set the others cite |
| Fundamental Analyst *(the Filing Analyst, widened)* | 1, 2, 3, 4, 5, 6 | Fundamental and expectations findings; risk flags |
| Regime Assessor | 7, 8, 9 | Sector, macro and market-regime findings |
| Technical Analyst *(new)* | 10, 11, 12 | A description of price behaviour and chart levels (not evidence for a direction, and not an exit) |
| Thesis agent | The three sets of findings | A bullish or bearish view with its basis, or `no_view`. No probability |

Inputs 6 and 10–13 are computed in code and handed to the agents as numbers. If the Fundamental Analyst's output proves shallow, the first split is a separate News Analyst.

#### Validation check, in code, before the user sees a draft (16 November 2026)

There is no critic agent in this stage. The Critic runs in stage 4 (on a different model family as the target; on the same family for the demo, see "Stage 4 redesigned"); a second one here would duplicate it and add assurance without adding accuracy. A deterministic check runs on every draft instead:

- every claim cites a stored piece of evidence;
- every number in the thesis matches the computed value it cites;
- the figure shown beside the view equals the base rate of its outcome at the primary horizon, and the draft states no other probability;
- a directional view cites at least one company-specific finding graded moderate or strong, or for an index one such finding from its lead evidence, and that evidence does not conflict with itself;
- every finding carries a grade set by the three checks;
- a resolution rule is present, and each finding the view rests on is paired with an evidence-based invalidation condition; none is a price level;
- an earnings date inside the horizon is flagged;
- no price-derived measure is cited in support of a direction;
- opposing evidence is listed, or the brief states that none was found;
- every risk flag raised is on the defined list and cites its evidence;
- a range-bound view meets all four of its conditions;
- the evidence families are listed, and a view supported by one family is marked weakly supported.

A draft that fails is returned to the Thesis agent once. If it fails again, the user is shown the draft with the failed checks. The result of the check is a decision record.

**How the check is carried out (operator decisions, 18 November 2026, night).**

- **Citations on the screen text.** `summary`, each of `rationale.catalyst`, `rationale.confirmation` and `rationale.tempering`, and each entry of `horizon_reasons` carries `cites[]`: ids of findings in the record or of measured facts that code supplies to the agent (base rates, typical moves, the volatility state, dated events with their day counts, the move in the price since a finding's date). The citations are not shown on the screen. A text with no citation, or one citing an id that is not in the record, fails the check.
- **Numbers.** Every number in those texts must equal a number in a cited finding, in the evidence that finding cites, or in a cited measured fact, at the precision written. Day counts and dates are computed in code and handed to the agent; it calculates nothing.
- **One return in total.** The check runs in one place, as the Thesis agent's output check on the harness, so the draft is returned at most once whatever the cause. A reply that is cut off at the output limit or does not match the format uses that one return; the content check cannot then return it again. If the second answer is a readable draft that still fails, the user is shown it with the failed checks. If there is no readable draft, the stage stops as an agent failure. A manual "Retry" after a stage stop is a fresh run with a fresh return.

**Accepting a draft is not approving a trade.** It fixes the thesis to be tested. The Critic's objections arrive in step 9, before any sizing or order.

**Then the user decides:** accept, edit, or reject. The record stores `thesis_origin` as `system`, `system_edited` or `user`, and keeps the untouched system draft alongside any edit.

**Anchoring, and the one mitigation available.** Reading the draft first anchors the user on it; the research behind step 2B shows warnings do not undo that. So before the draft is shown the user is offered one optional field: their own probability that the stock ends the horizon higher. If given, it is stored as `user_blind_probability` and never shown to the Thesis agent.

**Every draft is logged and resolved, traded or not** (step 14). This is how the system's own hit rate becomes measurable. It is forward-only: a model whose training data postdates a period cannot be tested on that period, so there is no backtest of the Thesis agent. No track-record statement is displayed before 100 resolved theses.

**Lists are out of scope for now** (operator decision, 17 November 2026). The mode takes one ticker per request. If lists are added later, the earlier rule stands as a starting point: one brief per ticker, shown in the order given, never ranked.

### Step 2B — User-supplied thesis

> **"Take a view yourself": the structured form, and the main road after a no view (operator decision, 18 November 2026, night; `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`, section 6).** Free-text entry with extraction by the Thesis agent, described below, stays in the design and is not built for the demo.
>
> 1. **Direction** (bullish or bearish) and **horizon** (a row of the measured table; the recommended row is preselected).
> 2. **What are you relying on?** The user ticks items from the evidence already on the brief, bearing-carrying or context. At least one.
> 3. **What would prove you wrong?** At least one invalidation condition, chosen from conditions the system can name, each with a `type` from the fixed list. None is a price level.
> 4. **How the thesis stands,** computed in code as the user chooses. *Not supported:* no chosen item carries a direction matching the view. *Partly supported:* at least one does, and either a chosen item is context or a finding with a direction points the other way. *Well supported:* every chosen item carries a matching direction and none points the other way. A finding that carries the opposite direction stands against the thesis whether or not it was ticked.
> 5. **Freeze my thesis** is enabled with at least one item and one condition. The verdict does not block.
>
> - **Recorded:** `thesis_origin: user`; direction and horizon; `relied_on[{evidence_id, kind}]` (anchored or context); the opposing findings; the invalidation conditions; `verdict`; and that it was entered after a no view, with the reason for the no view. **This is the commit point for the pending log, in place of "the first view".**
> - **Unchanged:** nothing from the option market is shown before the freeze; the agents are not asked again; stage 4's check 9 flags it; the Critic is not told who wrote it. Stop after a no view still records nothing.

> **Revised 17 November 2026 (operator decision): free text, then a credibility check.** The user types the thesis as free text. This replaces the fixed form described below as the way a thesis is *entered*; the research findings below still explain why the terms are confirmed in a structured step and why an invalidation condition is blocking.
>
> 1. **Read the text:** the system identifies the direction, the time frame and each factual claim.
> 2. **Check each claim** against the evidence already retrieved: supported, contradicted, or not found, citing the stored item.
> 3. **Check for rejected signals** (the dead list in spec §10; the same closed list as step 9b).
> 4. **Show what cuts against it:** opposing evidence, the base rate for the stated direction, and any risk flags.
> 5. **State a verdict in words:** well supported, partly supported, not supported, or rests on a rejected signal. No score.
>    **Verdict rule (operator decision, 17 November 2026), fixed in code and applied in order.** "Supported" means supported by evidence graded moderate or strong; weak evidence does not count.
>    1. *Rests on a rejected signal:* no claim is supported, and at least one claim is a rejected signal (`config/rejected_signals.json`).
>    2. *Not supported:* no claim is supported.
>    3. *Partly supported:* at least one claim is supported, and at least one other is contradicted, not found, or a rejected signal. One contradicted claim cannot be outvoted.
>    4. *Well supported:* every claim is supported.
> 6. **Confirm the terms:** the system extracts the direction, horizon and invalidation conditions and the user confirms or corrects them. **At least one invalidation condition (what would show the thesis to be wrong) is required before the freeze.** A user probability is optional.
>
> - **The verdict does not gate the workflow.** The user may proceed with a thesis the evidence does not support; the verdict and the decision are recorded.
> - **Guard against agreement:** claims are checked one at a time against stored evidence and opposing evidence is always shown. The Critic in step 9 follows as for any thesis.
> - The same path serves every user-supplied thesis, including one entered in place of a rejected system view.
> - *Designed by the designer from the operator's one-line instruction; the six steps and four verdict labels have not been reviewed in detail.*
> - **Display rule unchanged:** nothing from the market is on screen while the thesis is entered.

**Display rule: nothing from the market is on screen yet.** Not the price, not the chain, not implied volatility, not an analyst view, and above all not a market-implied probability.

Why the rule is this strict: an implied probability is a *consensus summary statistic on the same scale and dimension as the forecast being elicited*, which is the configuration where anchoring is strongest — and it is **robust to warnings and to accuracy incentives**. A cautionary banner has no empirical support. Only sequencing works. Measured: showing a running consensus cost 3 percentile points of accuracy at question level and up to 7 at domain level, while showing individual recent answers cost nothing. Separately, social information significantly *raised confidence with no accuracy gain*.

**One question per screen.** Question order and same-screen presentation both change anchoring magnitude, and anchoring survives careful design.

#### Required fields

| Field | Format | Why |
|---|---|---|
| `probability` | **integer percent, 1% steps** | Coarsening carries a measured Brier penalty: +11.8% at 3 bins, **+31.4% at 2 bins**, +562% for the strongest forecasters. A low/medium/high picker is the single most destructive available choice and destroys later scoreability |
| `resolution_criterion` | free text, **blocking** | A probability without a resolution rule cannot be scored |
| `horizon_days` | integer | ditto |
| `falsifiers[]` | **if-then, blocking** | Specific observable trigger plus an affirmatively-phrased action. Implementation-intention plans measure d=0.65 across 94 studies; negated then-parts may backfire |
| `stated_edge`, `edge_source` | free text | For the record and for the Critic. Written justification does **not** improve accuracy — Bayesian evidence *for* the null — though it does reduce stated confidence |
| `premortem_categories[]` | fixed tag set | Premortem reduced plan confidence (d=.81) and shifted the *distribution* of failure categories. Fixed tags, not free text. The widely-cited "30% more reasons" figure could not be verified and is not relied on |
| `claim_decomposition` | direction / magnitude / timing / vol, each scoreable | Record-keeping only. **Never recombine into a system-generated probability** — decomposition cut error on extreme-magnitude targets but *increased median error 458%* on non-extreme ones |

Falsifier fields are **blocking** because take-up, not design, is the binding constraint: an RCT found only 11% accepted commitment contracts and two thirds of signers still failed.

#### Structure over instruction

Field evidence sits almost entirely on the choice-architecture side; debiasing research is lab students, and the relevant review excludes decision-support software entirely. So: blocking fields, fixed sequence, immutable timestamped records, order tickets. Not coaching.

### Step 3 — Freeze

Write the immutable thesis record. This is the pre-registration moment. Context: **96% of hypotheses are supported in standard psychology versus 44% in Registered Reports.** A trading journal written after the outcome is the 96% literature.

### Stage 3 redesigned: choosing contracts (operator decision, 17 November 2026)

*This section governs steps 4 to 8 below. Those steps were written when the operator brought the contract and the system assessed it. The system now drafts the view and must propose contracts for it, so the stage is re-centred on choosing. Decision record: `docs/decisions/2026-11-17-stage-3-contract-selection.md`.*

**Amended for the build (operator decisions, 19 November 2026).** Stage 3 was built on 19 November 2026. Before and during the build the operator ruled on the gaps it showed; the full list, with what the build chose beside it, is in the decision record ("Operator decisions for the build", "As built", "Operator rulings on what the first runs showed"). Where the text below differs from this list, this list governs.

| Subject | Rule now in force |
|---|---|
| Which contracts may form a leg | The stage 1 criteria in force, **without the DTE criterion**; no expiration under 7 days. For a spread or an iron condor each leg needs a valid two-sided quote and must pass the open-interest, minimum-premium and strike-distance criteria; **the bid-ask criterion is judged on the whole structure, through the cost cap, not on each leg.** A single bought option keeps the per-leg bid-ask criterion. A leg quoted wider than the setting says so in the detail (amendment to `docs/decisions/2026-11-15-liquidity-controls.md`) |
| Override | **None in stage 3.** A stage 1 override carries forward. If no leg can come from a passing contract the result is "no candidate built: no eligible contracts at your criteria" |
| Expiry | The eligible expiry nearest the horizon date in calendar days, among those on or after it **or up to three trading sessions before it**; a tie goes to the one on or after. The gap is stated either way. The poor-match rule is unchanged |
| Strikes | Placed where at least one construction is fully eligible. Where the two constructions land on different far strikes: the pair nearest the target, and on a tie the one that costs less to trade; the other reads "not available at these strikes". A far strike that lands on the anchor, or has no eligible strike on its side, means the candidate is not built and is listed with the reason. The single option is at the nearest eligible strike and its row states the distance from the price |
| Usual range for the days to expiry | Measured for the number of NYSE sessions from today to the expiry |
| History-based chances | "Made money" is a payoff above zero at expiry, entered at mid: both figures are labelled "before slippage". Blend row when the days to expiry are midway between two rows: the shorter |
| Market-implied chance of profit | Risk-neutral, rate zero: the chance of finishing beyond the break-even (between the two for a condor), read with the implied volatility of the eligible contract nearest the break-even on its side, or the at-the-money mean where that is missing. Labelled "approximate" |
| Events | **Shown, not filtered.** Earnings and ex-dividend dates come from the data provider; a row whose expiry falls after an earnings date, or after an ex-dividend date where it has a short leg, is marked. A control to include or exclude such candidates is deferred |
| Trading-cost cap | **An on-screen control** (2% to 10%, default 5%), after a count on live chains: 35 of 72 candidates over the cap at 5% |
| Chart levels | For the demo: the 60-day closing high and low that stage 2 computes, labelled as such. Context only |
| Catalyst date | The stage 2 record carries none, so the rule does not apply; after the demo |
| Market closed | With the symbol in the snapshot, the stage runs on the snapshot, marked provisional, and the user may continue |
| On screen | The first-ranked candidate is the "best fit", never "recommended" (`docs/product-shell.md`, section 3). Filtered-out candidates are listed with a FILTERED label, can be opened and cannot be selected |

**What the earlier steps lacked.** They never translated the view's outcome into a structure's outcome (a bullish view is right above the reference close; a spread bought for $2 profits only above reference plus $2). They showed no payoff picture. They measured cost per contract, though two legs that each pass a 5% gate can form a spread whose cost is 20% of its price. They had no rule linking horizon to expiry, no Greeks, and no early-assignment check for single names. Their heaviest part (volatility forecast, surface fit, richness residual) mostly informs single options and volatility trades, while the sizing rule pushes the operator into spreads where that exposure largely cancels.

**Sequence.**

1. **Open the chain** (step 4): live when the market is open, the latest snapshot when closed, marked provisional.
2. **Re-run the liquidity gate** (step 5) on that chain, with the operator's settings. *Amended 19 November 2026:* the DTE criterion is left out, and for a spread or an iron condor the bid-ask criterion is judged on the structure, not on each leg (table above). There is no override at this step.
3. **Choose the expiry:** the nearest eligible expiry on or after the horizon date; after the catalyst date where the view is dated. If the expiry falls well after the horizon the brief says by how many days. *Amended 19 November 2026:* an expiry up to three trading sessions before the horizon date may also serve it; the nearest in calendar days is chosen. *Amended 17 November 2026:* this is the default. The same rule is applied to every horizon row of the research brief that has an eligible expiry, horizons that lead to the same expiry are merged, and the operator may switch (see "Expiry options and switching" below).
4. **Build candidates by fixed rule,** defined risk only, strikes from eligible contracts:

   | View | Payoff shape | Strikes | Two constructions, same payoff |
   |---|---|---|---|
   | Bullish | Requires a rise | The price, and one usual range above | Call debit spread; put credit spread |
   | Bullish | Requires no fall | One usual range below, and the price | Put credit spread; call debit spread |
   | Bearish | Requires a fall | The price, and one usual range below | Put debit spread; call credit spread |
   | Bearish | Requires no rise | One usual range above, and the price | Call credit spread; put debit spread |
   | Bullish | Single option | The price | Long call |
   | Bearish | Single option | The price | Long put |
   | Range-bound | At the usual range | Short strikes at the edges of the usual range; each long strike the next eligible strike beyond | Iron condor |
   | Range-bound | Wider | Short strikes at 1.25 usual ranges | Iron condor |

   *Corrected 17 November 2026.* The first version of this table said "call debit spread and put credit spread at the same strikes ... (for the credit version, below)", which described two different things at once. A spread above the price and a spread below it are **different payoffs**: the first needs a move and pays more, less often; the second needs only no adverse move and pays less, more often. Each of them can be built with calls or with puts **at the same strikes**, and those two constructions are equivalent. So each directional view has two shapes, each priced in two constructions. The narrower half-usual-range pair is dropped to keep the set small.

   - **Within a shape,** the system keeps the construction that costs less to trade. This is a choice between equivalents, so trading cost alone decides it.
   - **Between shapes,** the trades are not equivalent. *Resolved 17 November 2026:* the shapes and the single option are ranked together by a priority the operator selects (step 6).
   - **Single options (added 17 November 2026).** A bought call or put has a known maximum loss, the premium. It is built at the eligible strike nearest the price. **Not built:** uncovered short options (no fixed loss), cash-secured puts and covered calls (they commit the price of the shares), and structures across two expiries.

   The usual range is taken for the number of days to expiry.
5. **Describe each candidate on the same dimensions:**

   | Dimension | Content |
   |---|---|
   | Payoff | Net price at mid, maximum loss, maximum gain, break-even |
   | Base-rate chance of profit | The share of past periods of the same length in which this structure would have finished above break-even, from the underlying's own history of moves |
   | Structure-level cost | Cost of entering at market against mid, summed over the legs, in dollars and as a share of the amount at risk and of the net price |
   | Market-implied chance of profit | From the expiry's implied volatility. Shown beside the base-rate figure, labelled as context |
   | Exposure | Net delta, theta and vega, from the feed's Greeks |
   | Event and assignment checks | Earnings before expiry; a dividend before expiry on a short leg |
6. **Filter, then rank by a chosen priority** (amended 17 November 2026; the earlier rule recommended on trading cost alone).

   **Filters.** A candidate that fails is set aside, listed with the reason, and can still be opened.

   | Filter | Set aside when | Setting |
   |---|---|---|
   | Liquidity | Any leg fails the leg criteria on the chain just retrieved (*amended 19 November 2026:* in practice a candidate with a failing leg is not built, and is listed with the reason) | The operator's stage 1 controls, as the table above applies them |
   | Trading cost | Structure-level cost exceeds the cap | Share of the amount at risk. Default 5%, adjustable 2–10% (operator decision, 17 November 2026). The default is the designer's choice, not measured; to be reviewed after counting how many candidates each level sets aside on stored chains. *Counted 19 November 2026 on live chains and made an on-screen control* |
   | Events | *Amended 19 November 2026:* nothing is set aside. The dates are shown and the row is marked | Dates from the data provider; "none declared" for an ex-dividend date not yet declared; "not available" where the symbol is not covered |

   **Ranking.** The operator selects one priority; the system ranks on that measure alone.

   | Priority | Ranked by |
   |---|---|
   | Match the view (default) | Pays when the view is right, highest first |
   | Larger payoff | What the candidate pays if the underlying moves one usual range in the view's direction, as a multiple of its maximum loss, highest first. Range-bound: what it pays if the underlying finishes at the reference close (operator decision, 17 November 2026) |
   | Lowest cost | Trading cost as a share of the amount at risk, lowest first |

   *Why one usual range:* a bought option has no limit on its gain, so ranking on maximum gain would place it first every time. In the page's example (price $100, usual range ±5%) the call debit spread pays $1.94 per $1 at risk at $105, the long call $1.08 and the put credit spread $0.52. The long call keeps gaining beyond that point; the screen says so and the ranking does not reward it. Payoffs at expiry are intrinsic value only, so no Greeks enter these figures.

   Ties: lower trading cost, then fewer legs. The first-ranked candidate is the recommendation, with its reason in a sentence. If none is left, the screen says so and shows why each was set aside.

   **Pays when the view is right** (new measure): of the past periods of the same length in which the view's outcome occurred, the share in which the candidate would have made money. **Contracts and the maximum loss for the trade (operator decision, 17 November 2026, replacing the sizing filter).** Every candidate is shown for one contract by default. The output screen carries an optional field, "Maximum loss for this trade", entered once prices are visible; the operator pointed out that a figure asked for before stage 3 would be a guess. With a figure entered, each candidate shows the number of contracts that fit (figure ÷ maximum loss per contract, rounded down) and its maximum loss, maximum gain and trading-cost dollars are restated for that number, updating as the operator types. Ranking, break-even and the chance figures do not change. A candidate whose single contract exceeds the figure stays visible, shows no contracts and states what one contract risks. An order above 10% of a leg's open interest is flagged. The figure and each change to it are recorded. The contract count is a proposed size; step 11 confirms the final size. **Capital is not asked for.** The 0.217%-of-capital rule and the 4% aggregate short-premium cap (spec §8) therefore cannot run in this stage; whether step 11 asks for capital is open.
7. **The operator picks the recommended candidate, another, or none.** The expiry, the priority, the ranking, the reason and the choice are decision records.

**What the recommendation is and is not.** It is the candidate that best serves the priority the operator chose. **It is not a statement that the trade is worth taking.** Within a payoff shape the choice between the two constructions is still made on trading cost, because they are equivalent. Between shapes and the single option the trades differ and no evidence shows one earns more, which is why the operator states the priority. "Match the view" is the default because the researched view states a direction and no size of move. Ranking on gross richness remains prohibited (spec §3).

**Expiry options and switching (17 November 2026).**

- One expiry for each horizon row of the research brief that has an eligible expiry; horizons leading to the same expiry are merged into one option, labelled with the horizons it serves.
- The expiry for the thesis horizon is selected by default.
- The operator may switch. The candidates, strikes, usual range and history-based figures are rebuilt for the new period. **The switch is recorded as an amendment to the horizon; the thesis record is not altered.**
- Each expiry states how many days it falls after the horizon it serves.
- **Poor match: a soft warning (operator decision, 17 November 2026).** An expiry whose days to expiry exceed twice the horizon is marked a poor match: more than half of the option's life falls after the period the view covers. The mark removes nothing and does not affect ranking. The screen adds one sentence: the figures assume holding to expiry, the view covers only the first part of that, and closing at the horizon gives a different result. It arises mainly on the 7- and 14-day horizons. *The factor of two is the designer's choice.* **Deferred:** estimating the position's value at the horizon (needs a pricing model and a volatility assumption).
- Every leg of a candidate shares one expiry.

**Chart levels in stage 3: context, and measured (operator decision, 17 November 2026).** Two uses were considered: letting support and resistance move the strikes, or showing them beside each candidate. The operator chose the second.

- Support and resistance are drawn on each candidate's payoff chart, and one sentence in the detail states where the break-even and strikes sit relative to them. Labelled "description only".
- **They place no strike, set aside no candidate and do not affect ranking.** Strikes come from the usual range.
- Each candidate's position relative to the levels is saved in the record (`levels{support, resistance, break_even_vs_support, break_even_vs_resistance}`). Once enough trades have resolved, candidates with a level on their side are compared with the rest. Levels gain a role in placing strikes only if that comparison supports it.
- *Open:* the definition of a level in general. **For the demo (operator decision, 19 November 2026):** the 60-day closing high and low that stage 2 computes, labelled "60-day high" and "60-day low", stored in the record with the definition's name.
- This replaces earlier wording in step 2A and the agent architecture that chart levels are "a reference for strike selection".

**Output screen (17 November 2026).** One screen: header (view, horizon, price, quote time, implied move beside the usual range); expiry strip; priority selector and filter settings; the optional maximum-loss field; ranked comparison with one row per candidate (maximum loss, maximum gain, break-even, pays when the view is right, base-rate and market-implied chance, trading cost, contracts); the detail of a candidate expands in place beneath its row, one open at a time (payoff chart, legs and quotes, exposure, checks, the other construction); candidates set aside; Stop and Continue. Page: `docs/site/market-contracts.html`, parts 3 to 6. **This is the only screen of the stage.** The candidate explorer and expiry timeline on that page are explanation, not screens; every stage page marks each figure as "application screen" or "explanation only" and lists the stage's screens in its overview.

**Cautions.**

- **The base-rate chance of profit inherits the survivor bias of the price history** and will flatter bullish structures. It is shown without an expected-value figure for that reason. **Both history-based figures are blended (operator decision, 17 November 2026),** so that stages 2 and 3 rest on the same basis.
  - *Own figure:* counted from the underlying's own past moves over the days to expiry.
  - *Pooled figure:* counted from the past moves of all single stocks. Because stocks differ in how far they move, each move is first divided by that stock's usual range for the period, and the candidate's break-even is expressed the same way (for example, 0.34 usual ranges above the price). The pooled figure is the share of those scaled moves that finish beyond the break-even.
  - *Blend:* own weight n / (n + k), with the k of the stage 2 row nearest the days to expiry; pooled only beyond 60 days. Index funds and ETFs use their own history, unblended; XSP uses SPX.
  - The blended figure is shown; the own figure is kept in the record. "Pays when the view is right" is blended the same way, within the periods in which the view's outcome occurred.
  - *The scaling by usual range is the designer's method and has not been tested.* Blending reduces noise; it does not remove the survivor bias, which the pool shares.
- **With no edge claimed, a fairly priced structure loses its trading cost on average.** The screen says what the underlying must do for the trade to pay.
- **Credit spreads and condors sell premium.** The spec §0b context is shown, and the 4% aggregate cap applies in step 11.
- **Data gaps:** ~~earnings dates and ex-dividend dates have no source yet.~~ *Closed 18 November 2026:* both come from the data provider (`config/data_sources.json`). No time of day for earnings; a future ex-dividend date appears only once declared. Events are shown and not filtered (19 November 2026).
- *The strike distances (one and 1.25 usual ranges), are the designer's proposals. The cost cap is confirmed as an adjustable control and the poor-match mark as a soft warning.*

**Deferred, not dropped:** event-volatility stripping, the two-component forecast, the surface fit and the richness residual (step 6 and spec §6). They wait on an earnings-date source and on implied-volatility history, and they matter mainly for volatility trades. For index instruments the Cboe volatility indices give that history now. **The probability pair of step 8 is replaced** by the base-rate and market-implied chances of profit above; the "assumed drift" is withdrawn.

**Record schema** (*as built, 19 November 2026:* the first-ranked candidate is `best_fit_id` with `best_fit_reason` on the candidate, not `recommended_id`; the chance figures are objects carrying the blended figure, the own and pooled figures and the weight; each leg carries its quoted spread and whether it is above the setting; `filters` carries the cost cap in force; the selection record carries the candidate, the contracts proposed and the candidates not selected)**:** `candidates[{id, structure, legs[], expiry, net_price, max_loss, max_gain, break_even, base_rate_profit_pct, implied_profit_pct, cost{dollars, pct_of_risk, pct_of_price}, greeks{delta, theta, vega}, checks{earnings, dividend}, removed_reason}]`, `recommended_id`, `recommendation_reason`, `chosen_id`. *Added 17 November 2026:* per candidate `rank`, `pays_when_view_right_pct`, `contracts_allowed`, `other_construction{structure, cost}`; and `expiry_options[{expiry, days, horizons_served[], poor_match}]`, `expiry_chosen`, `horizon_amendment{from_days, to_days, at}`, `priority`, `filters{liquidity, cost_cap_pct, include_events}`, `max_loss_for_trade{amount, changes[]}`, `contracts_proposed`.

### Step 4 — Reveal market state

Now show spot, chain, gate status, richness context. The thesis is already frozen.

### Step 5 — Live re-gate

Pull live quotes. Re-check spread %, OI, moneyness band against the current quote, not the 11:30 batch. The batch is a candidate generator; the live quote is the authority.

### Step 6 — Valuation, with the event check that actually matters

**"Non-earnings window" describes today. What matters is whether a report date falls inside the expiry window.** At quarterly reporting, a 60-DTE contract has roughly a two-in-three chance of spanning an earnings event.

```
if earnings_date in (today, expiry):
    event-vol stripping REQUIRED
    Event Assessor ACTIVE
    clean_IV = strip(observed_IV, sigma2_jump)
else:
    clean_IV = observed_IV
```

Skipping this is how the system produces a false "expensive" verdict: one earnings day can hold ~57% of total variance in a 40-day expiry.

Then: Yang-Zhang realised vol → two-component forecast → richness residual as the **regression residual** of forward realised vol on same-horizon clean IV. Not a subtraction.

### Step 7 — Cost ladder

Tick size by premium level ($0.05 under $3.00, $0.10 above), tick count, placement, fill probability, expected net cost.

| Ticks | Placement | Fill | Net cost (× half-spread) |
|---|---|---|---|
| 2 | at mid | 62.8% | 0.42 |
| 3 | two ticks in | 90% | 0.43 |
| 3 | one tick in | 36% | 0.51 |
| 4 | interior | — | 0.42 vs 0.55 / 0.58 |
| ≥4 | flag as marginal | near zero | unreliable |

Display marketable and patient side by side, in dollars and as % of premium. Multi-leg: both legs quoted in the same instant or no net price is shown.

### Step 8 — Probability pair

Risk-neutral N(d₂) from live IV, and estimated real-world from the forecast plus an assumed drift. Gap labelled as the risk premium. Delta is never presented as a probability.

### Stage 4 redesigned: the challenge (17 November 2026)

*This section governs step 9 below, which was written when the operator brought the contract. Stage 3 now proposes the contract, so the challenge covers the choice of structure as well as the thesis. Page: `docs/site/challenge.html`. Settled one step at a time with the operator on 17 November 2026.*

**Built on 19 November 2026.** The operator ruled on 18 points before the build; they are in `docs/decisions/2026-11-17-stage-4-challenge.md`, "Operator decisions for the build", and win where this section differs. The main ones: the Critic's output check runs on the harness with one return in total; C11 uses stage 4's own fetch of the chain; "opposing" in check 4 is any finding carrying the opposite direction; the earnings line of check 6 and the dividend part of C8 now have a date source; check 9 is withheld from the Critic; each case is at most 90 words; retrieval is the Evidence Retriever's second configuration over a local chromadb index.

**Receives** the stage 3 hand-off: the selected candidate; the thesis record with its full evidence and any horizon amendment; the candidates not selected; how the choice was made.

**Steps.**

| # | Step | Done by | Purpose | Input | Output |
|---|---|---|---|---|---|
| 1 | Checklist on the thesis | Code | Catch the faults a rule can catch, the same way every time | Thesis record | Thesis checks, each with a result and the item cited |
| 2 | Checklist on the contract | Code | Challenge the choice of structure | Selected candidate, candidates not selected, expiry, priority, ranking | Contract checks, each with a result and the figure that triggered it |
| 3 | Restate the thesis as a question | Code | Stop the critic agreeing with a statement because it is asserted (9a) | Thesis claim and basis | The question the critic works on |
| 4 | Retrieve evidence | Evidence Retriever | Give the critic grounds from the research corpus, on both sides (9d) | The question; the thesis's signals | Supporting and opposing findings, or empty |
| 5 | Critique | Critic | Do the judgement rules cannot (9c) | The question, the findings, both checklists | Objections with basis and status; the strongest case for the thesis |
| 6 | Present and record | Code | Put the challenge before the operator ahead of sizing | Outputs of 1, 2 and 5 | The challenge screen; decision records |

Steps 1 and 2 run in parallel. **First version:** the challenge advises and does not block; the veto, the structured override and the planted-thesis evaluation (9e–9g, 12a, §6) are not built. **Decided 17 November 2026:** the Critic runs on the same model family for the demo, stated on the screen; the operator reads the challenge and decides, with no typed response.

**Every check returns one of four results:** passed, flagged, not applicable, could not be checked. A check never reports "passed" for want of data.

**Step 1, the thesis checklist: twelve checks.**

| # | Check | Flagged when | Status |
|---|---|---|---|
| 1 | Rejected signal | The basis or a cited finding matches `config/rejected_signals.json` | **Confirmed** |
| 2 | Narrow support | One supporting finding, or one evidence family | **Confirmed** |
| 3 | Strength of support | The best supporting finding is only moderate, or a weak finding is cited as support | **Confirmed** |
| 4 | Contested | Sector or macro evidence opposes the view | **Confirmed** |
| 5 | Against the base rate | The view's outcome occurred in fewer than half of past periods | **Confirmed** |
| 6 | Event inside the window | Earnings or a flagged event between today and the expiry; or a dated catalyst after the expiry | **Confirmed.** Earnings part "could not be checked" until a date source exists |
| 7 | Risk flags | Any risk flag was raised in step 2A | **Confirmed** |
| 8 | Invalidation cannot be watched | A condition has no data source; or nothing watches it; or a finding has no condition | **Confirmed.** Adds `type` to each `falsifiers[]` entry |
| 9 | Origin and edits | Edited after drafting; direction reversed; supplied and not fully supported; or entered after no view | **Confirmed,** with the verdict rule for a supplied thesis |
| 10 | Earlier overrides and gaps | Any override, or provisional data. Unavailable inputs are a note | **Confirmed** |
| 11 | Price moved since the freeze | The price has moved half a usual range or more since the freeze; or the thesis is more than one session old | **Confirmed;** both thresholds are the designer's |
| 12 | Volatility state | Active; or, for a range-bound view, no longer quiet | **Confirmed** |

Left out on purpose: checks that would be flagged on every request (for example "no demonstrated edge"), and repeated requests on one ticker, which cannot be detected because Stop records nothing.

**Check 1, rejected signal (confirmed).** Matches the wordings in `config/rejected_signals.json` against the basis and each cited finding. Output per match: the signal, the phrase matched, where it was found, the reason. A match is a flag. Whether the thesis depends on the signal, and rejected signals in other words, are for the Critic. False alarms are accepted (for example "support" in an ordinary sentence).

**Check 2, narrow support (confirmed).**

- Count supporting findings graded moderate or strong. Weak findings do not count.
- *Flagged, single finding:* one counts. *Flagged, single family:* two or more count, all from one family. *Passed:* at least two families.
- **Same event counts once:** supporting findings from the same family dated the same day count as one.
- **Each evidence item records its family** (`evidence[].family`), set in code from the input that produced it: inputs 1, 2, 4 fundamentals and expectations; 3, 5 news and events; 7, 8 sector and macro.
- **Supplied thesis:** a supported claim takes the family of the evidence item that supports it; claims not found or contradicted do not count.
- **Index instruments:** counts lead evidence; flagged when the view rests on one lead finding.
- Output: the result, the count by family, the findings counted. Agrees with step 2A's "weakly supported" mark and adds the single-finding case.

**Check 3, strength of support (confirmed).**

- *Flagged, moderate at best:* no supporting finding is graded strong. *Flagged, weak finding cited:* the basis cites a finding graded weak. Both can apply. *Passed:* at least one strong supporting finding and no weak finding cited.
- Output: the result, the best grade among supporting findings, and for each flagged finding which of the three grade tests it failed (primary source, recent, specific).
- A finding with no grade is treated as weak and reported as ungraded. In a supplied thesis a claim takes the grade of the evidence item that supports it.

**Check 4, contested (confirmed).**

- *Flagged, contested:* at least one opposing finding graded moderate or strong. *Passed with a note:* opposing findings exist, all weak; they are listed. *Passed:* none found, and sector and macro evidence was retrieved. *Could not be checked:* no sector or macro evidence was retrieved.
- Output: the result, each opposing finding with grade and source, and the best grade for beside the best grade against. **Shown, never netted.**
- Opposition here is always from sector, macro or (for an index) qualifying evidence; conflicting company evidence gives `no_view` in step 2A.
- **Supplied thesis:** also lists claims marked "contradicted" in step 2B, and flags if there is one.

**Check 5, against the base rate (confirmed).**

- *Flagged:* the outcome the view needs occurred in fewer than half of past periods of that length (bullish: the base rate of closing higher; bearish: 100% minus it). *Passed:* half or more. *Not applicable:* range-bound, or no directional view.
- **Plain threshold at 50%, no tolerance band** (operator decision). The output always shows the figure's uncertainty, so a marginal flag is visible. Most bearish views will be flagged; that is intended.
- Uses the horizon in force when stage 4 runs, including a horizon amended in stage 3, and says so. Under five years of history: the pooled figure, stated.
- Output: the result, the figure with its uncertainty, the horizon, and whether the figure is blended or pooled.

**Check 6, event inside the window (confirmed).**

- **The window runs from today to the expiry, not to the horizon:** the position is exposed until the option expires. The output says which side of the horizon each event falls on.
- Event types, each with its own result line: earnings date (single stocks; no source); a dated ruling, regulatory decision or vote (single stocks; from the step 2A risk flags); Federal Reserve decision (all); inflation and employment releases (index instruments); heavy earnings period (equity indices; no source); the thesis's own dated catalyst.
- *Flagged, event inside:* the event falls between today and the expiry. *Flagged, catalyst outside:* the thesis depends on a dated catalyst after the expiry. *Passed:* the date is known and outside the window, or the catalyst is inside it. *Could not be checked:* the date is unavailable. *Not applicable:* the type does not apply to the instrument.
- The check as a whole is flagged if any line is; "could not be checked" if none is flagged and any line could not be checked.
- Macro lines use the step 2A flag windows, so the stages cannot disagree. Stage 3's events filter decides whether a candidate is set aside; this check reports the exposure if the operator proceeds.
- Used by the Critic, the challenge screen (a short timeline against horizon and expiry) and step 11 (a flagged event reduces size).

**Check 7, risk flags (confirmed).**

- *Flagged:* at least one flag reduces size or adds an invalidation condition. *Flagged, severe flag overridden:* the system declined (going-concern warning or announced takeover) and the operator supplied a thesis anyway. *Passed with a note:* only a note-level flag (sector-wide move). *Passed:* none raised, and the filings were read. *Could not be checked:* the filings or calendar could not be read.
- Output per flag: its name, the trigger with source, its effect, and whether it works against the view (a flag reduces size only where it does, or where it raises the chance of a large move either way).
- Dated flags (a pending ruling, a Federal Reserve decision): check 6 owns the timing; this check lists the flag and points to check 6.
- Used by the Critic, the challenge screen and step 11 (one size reduction, however many flags).

**Check 8, invalidation cannot be watched (confirmed).**

- **Schema change to step 2A:** each `falsifiers[]` entry gains `type`, chosen by the Thesis agent from a fixed list. Code maps the type to a data source.

  | Type | Data source today |
  |---|---|
  | `guidance_change` | Company filings: available |
  | `new_filing` | Company filings: available |
  | `estimate_revision` | None |
  | `earnings_result` | Filing available after the event; the date is not |
  | `dated_event_outcome` | Partly: filings yes, news no |
  | `macro_release` | Available |
  | `volatility_state` | Price history: available |
  | `unscheduled_announcement` | Partly: filings yes, news no |
  | `other` | Treated as not watchable |
- *Flagged, cannot be watched:* at least one condition has no data source. *Flagged, not watched automatically:* every condition has a source but the Monitor is not built. *Flagged, no condition:* a finding the thesis rests on has no invalidation condition. *Passed:* every condition has a source and the Monitor is active.
- **Stays flagged while the Monitor is not built** (operator decision), as an exception to the rule against always-raised flags: the content differs per request, and it tells the operator that watching the conditions falls to them.
- Output per condition: type, source, status (watched, could be watched, cannot be watched) and, where not watched, where to look.
- Used by the challenge screen, by step 12 (a thesis whose conditions cannot be watched leans more on the price-based risk exit), and as the Monitor's work order when it is built.

**Check 9, origin and edits (confirmed).**

- *Passed:* system-drafted and accepted unchanged. *Flagged, edited:* each changed field listed with before and after (the untouched draft is kept). *Flagged, direction changed:* the edit reversed the direction; the evidence was gathered for the opposite view, so the thesis is treated as supplied. *Flagged, supplied and not fully supported:* the step 2B verdict is partly supported, not supported, or rests on a rejected signal. *Flagged, entered after no view:* with the reason for the no view. *Passed with a note:* supplied and well supported.
- Output: the origin, then the edits, or the counts of claims supported, contradicted and not found with the verdict.
- **The Critic is not told the origin** (corrected 17 November 2026; an earlier line said it was). Telling it who wrote the thesis restores the ownership cue that step 3 removes. The origin is shown to the operator and kept in the record.

**Check 10, earlier overrides and gaps (confirmed).**

- Collects, from the decision records: liquidity gate overruled (stage 1); recommended horizon not taken (stage 2); horizon amended by switching expiry (stage 3); maximum loss raised after the candidates were shown (stage 3); provisional data (market closed, snapshot used); inputs unavailable when the view was formed.
- *Flagged:* any override, or any figure resting on provisional data. *Passed with a note:* neither, but one or more inputs were unavailable; they are listed. *Passed:* none of these.
- **Unavailable inputs are a note, not a flag** (operator decision): they are missing on every request until a provider is chosen, and are already shown on the brief and in check 6. One setting promotes the note to a flag once gaps become the exception.
- **Schema addition to step 2A:** `inputs_unavailable[{input, reason: no_source | source_failed | not_applicable}]`.
- Output per item: the stage, what the system proposed, what the operator chose, and the reason given.

**Check 11, price moved since the freeze (confirmed).**

- The thesis resolves against its reference close; stage 3 builds contracts around the current price. The move between them is measured in usual ranges for the horizon.
- *Flagged, moved with the view:* half a usual range or more in the view's direction. *Flagged, moved against the view:* half a usual range or more against it. *Flagged, thesis is stale:* frozen more than one trading session ago, whatever the price has done; the screen offers to re-run stage 2. *Passed:* under half a usual range and from the current or previous session. *Could not be checked:* no current price.
- Range-bound view: any move of half a usual range is flagged.
- Output: reference price, current price, the move in percent and in usual ranges, its direction relative to the view, and the age of the thesis.
- *Half a usual range and one session are the designer's choices.* The check will fire often on the 7-day horizon, where half a usual range is an ordinary day's move; accepted.

**Check 12, volatility state (confirmed).**

- *Flagged, active:* the state is active (after an active state the close stayed inside the usual range 59–62% of the time, against the 68% it is built for; stage 3 places every strike by that range). *Flagged, no longer quiet:* a range-bound view and the state is now normal. *Flagged, invalidation met:* a range-bound view and the state is now active. *Passed with a note:* a directional view in a quiet state (moves have tended to be smaller). *Passed:* normal; or quiet with a range-bound view. *Could not be checked:* under one year of price history.
- Output: the state, the recent level as a percentage of the one-year typical level, whether it has changed since the freeze, and the observed figure for that state.
- **Reports and adjusts nothing.** The figures were observed on 16 November 2026, not confirmed by a pre-registered test, and Test R (adjusting the range for the state) failed.
- Used by the Critic, by the contract checklist (step 2) and by steps 11 and 12.

**All twelve thesis checks were confirmed by the operator on 17 November 2026.**

**Step 2, the contract checklist: eleven checks.** New with the stage 3 redesign: the original design never questioned a contract the system itself proposed. Same four results as the thesis checks. All eleven were confirmed by the operator on 17 November 2026.

| # | Check | Flagged when | Status |
|---|---|---|---|
| C1 | Can lose when the view is right | "Pays when the view is right" is below 100% | **Confirmed** |
| C2 | Volatility state against the structure | Active state and the structure collects premium; or quiet state and the structure needs a move | **Confirmed** |
| C3 | Poor-match expiry | The expiry is more than twice the horizon away | **Confirmed** |
| C4 | Chance gap | The base-rate chance of profit is below the market-implied chance by more than the base-rate figure's own uncertainty | **Confirmed** |
| C5 | Market expects a larger move | The implied move is at least 1.25 times the usual range (provisional) | **Confirmed;** threshold to be replaced by a measured one |
| C6 | Trading cost high | Trading cost is in the top fifth of the cost cap | **Confirmed** |
| C7 | Premium-selling structure | The structure collects premium | **Confirmed** |
| C8 | Early assignment | A short leg is in the money at entry, or a dividend falls before expiry on a short leg, where early exercise is possible | **Confirmed.** Dividend part "could not be checked" until a date source exists |
| C9 | Order size | The order exceeds 10% of open interest on any leg | **Confirmed** |
| C10 | Recommendation passed over | The operator selected a candidate other than the first-ranked one | **Confirmed** |
| C11 | Price moved since selection | The structure's price has moved by more than its trading cost since it was selected | **Confirmed** |

Left to the thesis checklist, to avoid repetition: events inside the window and a catalyst after the expiry (check 6); a switched expiry, a raised maximum loss and snapshot data (check 10).

- **C1 (confirmed).** The gap between being right about direction and making money. *Flagged:* `pays_when_view_right_pct` below 100. Output: the figure, the break-even, and the move needed in percent and in usual ranges. Pooled figure, stated, with under five years of history.
- **C2 (confirmed).** Uses thesis check 12. *Flagged:* the state is active and the structure is a net credit (larger moves hurt a premium seller); or the state is quiet and the structure needs a move (C1 flagged). *Could not be checked:* no state.
- **C3 (confirmed).** Reads the stage 3 poor-match mark. Output: days to expiry, the horizon, and that the figures assume holding to expiry.
- **C6 (confirmed).** *Flagged:* trading cost at or above 80% of the cost cap (4% at the default). Output: the cost in dollars and as a share of risk, the cheapest candidate's cost for comparison, and that closing before expiry costs about the same again.
- **C7 (confirmed).** *Flagged:* the structure is a net credit. A flag with context, not a prohibition: spec §0b (rule-based index premium selling earned no extra return after May 2012) for index instruments; for single names, that the premium is not harvestable at retail cost. Output: the credit and the maximum loss as a multiple of it.
- **C9 (confirmed).** *Flagged:* proposed contracts exceed 10% of open interest on any leg (the stage 1 rule). *Could not be checked:* open interest missing for a leg.
- **C10 (confirmed).** *Flagged:* `chosen_id` differs from `recommended_id`; the two are compared on the priority's measure. *Passed with a note:* the first-ranked candidate was chosen under a priority other than the default.

- **C4 (confirmed).** *Flagged:* `base_rate_profit_pct` is below `implied_profit_pct` by more than the uncertainty of the base-rate figure for that horizon (about ±3 points at 30 days, ±1.5 at 7). No invented threshold: the check fires only when history and the market disagree by more than history's own margin of error. History flatters bullish structures, so for a bullish trade a base-rate figure below the market's is the stronger warning. *Could not be checked:* implied volatility missing.
- **C5 (confirmed).** The implied move (from the expiry's at-the-money implied volatility, scaled to the days to expiry) against the usual range for the same period. Both describe about a 68% band. *Flagged:* the ratio is 1.25 or more. **Provisional:** option prices normally imply somewhat more movement than occurs, so the threshold must sit above that normal excess. To be replaced by the top fifth of the ratio measured across the snapshot names (implied volatility stored since 16 November 2026; a description of stored data, no trial spent). **Stands in for the missing earnings date:** a large implied move often means the market is pricing an event.
- **C8 (confirmed).** Reads `config/instruments.json` (exercise and settlement style; SPX and XSP are European and cash-settled, so not applicable; single stocks and ETFs can be assigned early). *Flagged:* a short leg is in the money at entry; or a dividend falls before expiry on a short leg. *Could not be checked:* the dividend part, until ex-dividend dates have a source.
- **C11 (confirmed).** Stage 4 fetches fresh quotes for the selected legs when it starts (one ticker). *Flagged:* the structure's net price has moved by more than its trading cost since selection, so the figures the choice rested on are out of date; the screen offers to return to stage 3. *Could not be checked:* the market is closed; the screen says the figures are from the last session. Replaces a fixed 30-minute rule.

**Step 3, restate the thesis as a question (confirmed 17 November 2026).**

- **A fixed template in code; no model.** The parts it needs were separated in stage 2: for a system view, the direction, horizon and each finding; for a supplied thesis, the direction, horizon and each claim extracted in step 2B. The template never uses the written basis or the operator's wording.
- Form: "Do the following support a close [above | below | within the usual range of] the reference price for [ticker] at [N] days?" followed by each finding or claim as a plain numbered statement linked to its evidence item.
- **Withheld from the Critic:** the original wording, the written basis, and who wrote the thesis. All three stay in the record and on the operator's screen.
- A short list of confidence words ("clearly", "obviously", "certain" and the like) is stripped from claims as a backstop.
- The contract is not restated; the Critic receives it as figures and checklist results.
- Output: `{question, direction, horizon_days, claims[{id, text, evidence_id}]}`, used by step 4 to search and by step 5 as the Critic's subject. Implements 9a below.

**Step 4, retrieve evidence (confirmed 17 November 2026).**

- **Two kinds of evidence.** Stage 2 evidence is about this company (filings, results, guidance) and travels in the thesis record. Step 4 evidence is about whether this kind of reasoning has worked, and comes from the research corpus. The Critic receives both.
- **Corpus: the project's research only** (the nineteen reports in `docs/research/`, the factor specification, the decision records). **No web search:** the research already records what was found and how strong it was, and a live search returns unvetted material on the topics where confident nonsense is commonest.
- One search topic per claim, plus one for the type of structure selected.
- **Each topic is searched both ways** (that the reasoning has worked; that it has not). Implements 9d: never one-sided.
- A relevance bar; nothing is better than something loosely related. **At most three passages per side per topic.**
- **One retry:** an empty search is reworded once, then reported as "nothing found".
- The retriever draws no conclusion.
- Output per topic: passages for and against, each with source report, section and evidence grade ("ungraded" where the report gives none).
- **Build-time choices, open:** the embedding model for the index (a local model needs no extra key; start there); how grades are attached to passages.

**Step 5, the critique: nine tasks (confirmed 17 November 2026).** The first five audit the thesis. The operator asked whether they were enough for a compelling counter-thesis; they were not, since nobody wrote the case against. Four were added.

| # | Task | What keeps it honest |
|---|---|---|
| 1 | Find what the thesis depends on: the claim whose removal leaves nothing | Cites the claim |
| 2 | Spot a rejected signal described in other words (what thesis check 1 missed) | Cites the claim and the list entry |
| 3 | Find claims that do not fit together | Cites the claims |
| 4 | Read the two checklists together: separate flags that are one problem | Cites the checks |
| 5 | Write the strongest case for the thesis | Required in every run |
| 6 | **Priced-in test:** for each claim the thesis depends on, has the market already reacted? | **Code supplies the price move since the date each finding became public** (`evidence[].price_move_since{pct, usual_ranges}`); the Critic interprets a figure and does not guess |
| 7 | **Write the strongest case against:** one short argument for the opposite outcome or for no move | Built only from recorded opposing evidence, the base rate, the checklist flags and retrieved passages. Same length limit as task 5; shown beside it |
| 8 | **How this trade loses:** two or three specific paths to a loss for the selected structure | Each path cites a check or a finding |
| 9 | **What is missing:** evidence that would be expected and is absent | Limited to what stage 2 recorded as unavailable or not found (`inputs_unavailable[]`, claims "not found"). The Critic may not invent a gap |

- The case for and the case against are symmetric and shown side by side: this is the balance rule (9d) applied to both, where the first draft required only the case for.
- **Limits that remain:** the Critic does no fresh research, so bad news stage 2 missed stays missed (the remedy is in stage 2, where opposing evidence must be listed); on the same model family as the Thesis agent the case against shares its blind spots; the output is not a verdict.
**The Critic's rules (confirmed 17 November 2026).**

1. **Every objection cites its grounds:** a checklist result, a claim or a retrieved passage. An objection with no citation is removed.
2. **A disposition for every claim:** holds, holds only in a narrower form, does not hold. No claim may be skipped. The count of each is recorded; a run of "narrower form" with no "holds" or "does not hold" is what going through the motions looks like (9e).
3. **At most five objections,** most serious first.
4. **No verdict, score or confidence figure, and no advice on whether to trade.**
5. **It may concede.** With clean checks and nothing found against, the right output is the two cases and few or no objections.

**Code check on the Critic's output, before the operator sees it:** every citation exists; every claim has a disposition; the case for and the case against are both present and within the length limit; the cap is respected. A failing output is returned once. If it fails again, the screen shows the two checklists and states that the Critic's output was rejected.

**Model (operator decision, 17 November 2026): the Critic runs on the same model family as the Thesis agent for the demo.** This departs from the 15 November rule in step 9 below (a different family whenever the thesis is system-drafted), which stays the target. The challenge screen and the report state the limitation. The checklists, which use no model, carry more of the weight meanwhile.

**The operator's response (operator decision, 17 November 2026): read and decide.** Proceed, return to stage 3, or stop. No typed response to objections is required. The structured override of 12a is not built in the first version.

**Step 6, present and record (confirmed 17 November 2026).**

- **One screen, in two columns** (layout B of four drawn; the operator chose it). Left: the Critic's judgement, namely the strongest case for, the strongest case against, how the trade loses, and the objections. Right: the fixed-rule checks, thesis then contract, with flagged and could-not-be-checked results open and passed ones collapsed to one line; the actions sit beneath them. The split keeps a model's argument and a rule's finding apart, which matters most while the Critic shares a model family with the Thesis agent.
- Header: ticker, view, horizon, the selected contract, and a line stating which model family the Critic ran on.
- **A readiness line, set by code** (operator decision). The Critic gives no go or no-go; the operator asked for guidance, and this supplies it without a verdict.

  | Readiness | When | The screen suggests |
  |---|---|---|
  | Not ready | The thesis is stale (thesis check 11); the contract's price has moved by more than its trading cost since selection (contract check C11); a range-bound view's invalidation condition is met (thesis check 12); or the Critic's output was rejected | The remedy: run stage 2 again, or return to stage 3 |
  | Ready, with items | None of those, and at least one check is flagged or could not be checked | "No blocking conditions", with the number of items for the operator's judgement |
  | Ready | None of those, and nothing flagged | "No blocking conditions" |

  It is about validity, not merit. Flags are not counted into a rating. It does not block: the operator may proceed past "not ready", and that is recorded.
- "Could not be checked" is shown with the flags, never with the passes.
- On request: each claim's disposition, the priced-in reading, what is missing, the passages cited, the operator's original wording.
- Actions: proceed to stage 5, return to stage 3, stop. Returning keeps this challenge on record and runs a new one on the newly selected candidate.
- **Recorded:** all twenty-three check results; the restated question; every passage retrieved and each topic that returned nothing; the Critic's full output; whether it passed the code check; the model it ran on; the readiness line and its conditions; the decision and its time, with proceeding past "not ready" marked.
- **Handed to stage 5:** the thesis and the selected contract, unchanged, with the flags and objections attached. Step 11 and step 12 use three directly: risk flags and events (size); invalidation that cannot be watched (the price-based exit matters more); the volatility state.
- Record schema: `challenge{thesis_checks[], contract_checks[], question, retrieved[], critic{...}, critic_output_check, critic_model, readiness{state, conditions[]}, decision, at}`.

**Stage 4 is designed in full as of 17 November 2026.** Page: `docs/site/challenge.html`, eight parts. Design canvas with the four screen layouts: "Stage 4 challenge screen layouts".

### Step 9 — Critic challenge

*Superseded in part on 17 November 2026 by "Stage 4 redesigned" above, which governs: for the demo the Critic runs on the same family, stated on screen, and the challenge never blocks.*

**Rule added 15 November 2026: when the thesis is system-drafted, the Critic must run on a different model family from the Thesis agent.** Models that are wrong agree on the same wrong answer at 0.42–0.60 against a chance baseline of 0.13–0.33, so a same-model critic shares the author's blind spots, and debate between instances of one model is on the dead list. If a second model family is unavailable, the user is the critic: the checklist results are shown and the LLM critic is skipped, not faked.

**The central research finding is negative: telling a model to be critical is mostly theatre.** Four independent measurements converge.

- Anti-sycophancy preambles *reduced* principled-choice accuracy on most models tested (one went 93.3% → 61.3%; a single preprint, flagged internally inconsistent).
- Suppressing sycophantic agreement by 20.9 points produced genuine-correction rates **below 0.6% in every condition** — refusal, hedging and non-commitment substituted for correction.
- Critical output tracks **surface cues, not substance**: confident rewrites of identical content were preferred 1.3×–7.0×, and one frontier model accepted 21.0% of high-confidence versions it had rejected in low-confidence form.
- Injected substantive flaws moved review scores by **−0.07 (not significant)**, sometimes *upward*, while inserting an explicit "strong reject" sentence moved them **−1.65**. The model responds to the stated verdict, not the reasoning.

Architecture: **deterministic checklist first, LLM second, veto gated structurally.**

#### 9a — Question reframe (preprocessing, before the LLM sees anything)

The strongest measured mitigation, and it is not a prompt. Strip epistemic markers, de-person, convert the assertion to a question. Latent sycophancy β **1.13** (control) → **0.51** (instructed) → **−0.55** (reframed). I-perspective framing scored β 0.88 and expressed conviction β 0.82 against −0.14 for a plain statement.

Roughly twice the effect of the instruction, and it composes with it.

#### 9b — Deterministic checklist (no model)

Near-100% recall, zero variance, probably the majority of real cases:

*17 November 2026:* the list is now a file, `config/rejected_signals.json` (14 signals, each with a reason and the wordings it is matched on). It holds the signals a thesis could cite; system-design prohibitions on the wider dead list are not in it. The same file serves the supplied-thesis check in step 2B, this checklist and the Critic. A match is a flag, not a block.

1. **Refuted-signal match.** Closed list: unusual options flow, IV rank as a verdict, Elliott wave, Fibonacci retracements, candlestick patterns, multi-timeframe confluence, social sentiment as direction, retail GEX, 13F, accruals, max pain, partial-notional risk reduction.
2. **Base-rate violation.** Structure, moneyness and tenor against the measured unconditional return for that class.
3. **Missing-grade gating.** Any load-bearing claim without a corpus evidence grade.
4. **Live gate failure**, already fatal upstream.

#### 9c — LLM critique, confined to what rules cannot do

- **Load-bearing-ness** — is the refuted signal decorative, or is the thesis resting on it? Highest-value contribution.
- **Paraphrase detection** — the same dead signal under a different name.
- **Composition errors** — individually defensible claims that do not compose.
- **Mandatory steelman** — the strongest version of the user's thesis.

#### 9d — Retrieval must be balanced, not asymmetric

The draft specified disconfirming-evidence-first retrieval. **That was wrong.** One-sided exposure drives model stance to endpoints (a 50-50 split going to 100%), and a single contradicting argument shifted 8 of 9 models by more than 50%. Worse, the human reader is *moved* by a one-sided critic rather than learning to discount it — roughly 16% polarity shift. That is a correctness problem, not a credibility one.

So: retrieve disconfirming evidence in a pass that **may not set the verdict**, pair it with the mandatory steelman, and let the verdict come from the structural checklist.

#### 9e — The anti-theatre instrument

A required `premise_disposition` per objection: **conceded / reformulated / upheld**. Static persona diversity lowered false-premise recovery to 35.8% from a 43.9% baseline, with **94% of responses reformulating the false premise against 2% conceding it.** Reformulation is what theatre looks like in the data, so make it countable.

#### 9f — Do not build debate or self-critique

- Intrinsic self-correction degrades: one model went 75.8 → 38.1, flipping 39.8% of correct answers while fixing 5.8%.
- Debate loses to plain majority voting at matched compute (83.0 vs 88.2).
- Round-two novelty median **0.068**; round-two confidence correlates +0.69 with round-one confidence and only **+0.10 with correctness**.
- Correlated errors: models that are wrong agree on the *same* wrong answer at 0.42–0.60 against a 0.13–0.33 chance baseline. Two instances of one model cannot find a blind spot they share.

#### 9g — Base model choice dominates

Confident-false-expert follow rates measured 4%, 11% and 80% across model generations — a ~20× spread that likely swamps every prompt-level mitigation. **Pick the model on this metric before tuning prompts.**

### Step 10 — Base-rate confrontation

| Structure | Mean return |
|---|---|
| 3% OTM weekly call | −59% per 8-day hold |
| 1% OTM weekly call | +12% |
| Retail option purchase, all | −3.95% per trade |
| Retail 0DTE | −4.6% per trade |

Show for the record and for friction, **not persuasion**: financial education explains 0.1% of variance in behaviour, negligible after 20 months, and engagement features have been measured to *increase* trade frequency and riskiness.

### Step 11 — Sizing

0.217% of capital per position on max loss, 4% aggregate short-premium cap, portfolio greek and correlation check, recovery arithmetic.

*Note, 17 November 2026:* stage 3 no longer asks for capital. It proposes a contract count from an optional maximum loss for the trade, entered on the output screen. This step confirms the final size. **Open:** whether this step asks for capital, without which the 0.217% rule and the 4% cap cannot be checked. The order-placement guidance of step 7 (the cost ladder) also moves here.

The rule binds: at $100k capital, a $2.50 naked long (max loss $250) is **zero contracts**. (The 0.217% is computed at an assumed p = 0.54; at $100k it admits only ~9% of gate-passing contracts as single-leg longs — spec §8.) This pushes toward narrow defined-risk spreads, agreeing with the 0DTE loss data and the complex-order finding by independent routes.

### Step 12 — Entry record and barriers

Triple-barrier levels, pre-registered invalidation conditions, the verbatim quote the panel was built from, assumed fill, fill-probability estimate, §1092(a)(2) identified-straddle timestamp.

### Step 12a — Veto mechanics

A clinical study measured an override rate of **0.68**; treat it as a prior and measure your own.

- **Never show a model confidence score.** Displayed confidence moves switch rates 40.5% → 69.6% with *no accuracy gain*, and users detect miscalibration only 26–29% of the time. Show corpus evidence grades instead.
- **Explanations do not help.** No significant reliance effect; 28.3% rated positively.
- **Use a cognitive forcing function.** Overreliance 0.64 → 0.48 (p=.003, d=.36). Prefer **assumption-surfacing** (63.0% overreliance) over a what-if variant (80.7%).
- **Rate-limit the veto.** Clinical alerts at 6.4 per 100 orders produced 56–63% inappropriate dismissal.
- Record the override and typed reason. **No credible evidence was found that typing a reason changes behaviour** — keep it for the record, not the effect.
- Trust and user preference were *negatively* correlated with performance. Do not optimise for the critic feeling helpful.

### Step 13 — Execution guidance

Limit price, native complex order never legged, the ≥4-tick stop, the $3-boundary patience asymmetry, avoid the first 90 minutes.

### Step 14 — Shadow label

Every assessed contract gets a triple-barrier label at resolution under the same fixed rule, traded or not.

---

## 3a. Decision records (design consideration added 15 November 2026)

**Every decision at every stage produces a decision record. If the contract is traded, the full chain of records is stored permanently in the system's memory, attached to that trade.**

A decision is anything that could have gone another way: the gate's pass or fail, a control the user changed, an overrule, the thesis the system drafted, the user's accept, edit or reject, the structure and contract chosen, the critic's objections and whether they were conceded, the size, the exit conditions.

| Field | Content |
|---|---|
| `stage`, `step` | where in the workflow the decision was made |
| `decision` | what was decided |
| `decided_by` | `system` or `user` |
| `inputs` | the data the decision rested on, with its source and time (live or snapshot, and the snapshot date) |
| `settings` | the control values in force, where relevant |
| `alternatives` | what else was on the table, where there was a choice |
| `reason` | the system's stated basis, or the user's one-line reason on an overrule |
| `overruled` | which check was overruled, if any |
| `at` | timestamp |

**Rules.**

- **Records are append-only.** A later decision adds a record; it never edits an earlier one.
- **Written as the workflow runs**, not reconstructed afterwards. A record written after the outcome is known is worth nothing.
- **Traded:** the chain is committed to long-term memory and linked to the trade, so the post-mortem can replay how the position came to exist and the system can retrieve similar past decisions later.
- **Not traded:** the chain is not committed to long-term memory. The thesis itself is still logged and resolved for scoring (step 14), as before. *The user's instruction covers traded contracts; whether to keep full chains for untraded requests is an open question.*
- **This is the same store as the thesis record** (§4): the thesis record becomes one record in the chain, not a separate system.

**Clarification, 18 November 2026 (operator decision): "append-only" applies to the permanent record, and the commit point is the first view.**

Two rules collided: every stage writes a record as the run proceeds, yet Stop after a no-view result must write nothing (step 2A). They are reconciled with a pending log.

- **Pending log.** Each request writes its decision records to a pending log as it runs. Within the request the pending log is append-only.
- **Commit point.** The pending log is committed to the permanent record at one point: **when stage 2 returns a view** (bullish, bearish or range-bound). From then on records are written directly to the permanent record, which is append-only and never deleted from.
- **Ending before the commit point.** The pending log is discarded: Stop on the gate screen, Stop after a no-view result, and Stop after a stage 2 failure. Nothing reaches the permanent record and no row appears in Recent analyses.
- **"Reject and stop" on a thesis that has a view** is after the commit point, so it is recorded and listed.
- **An engine restart** while a request is open ends it as "interrupted" under the same rule: discarded before the commit point, recorded after it. It is not resumed.
- **Agent traces are not decision records.** They are kept in a separate operational log, including for requests whose pending log was discarded, retained for 7 days, never used for scoring and never listed in Recent analyses. Traces of requests that reached the permanent record are kept with it.

**When a stage stops on a failure (operator decision, 18 November 2026).** A failed or timed-out agent, a stage time limit or a spend limit stops the stage with a plain message; partial results are kept.

- **Principle.** A retry is offered only when the user has not been shown that stage's answer. It re-runs the nodes that did not finish and skips nodes whose output is already in the record. At most one manual retry per stage per request.
- **Stage 2** (agent failure, timeout, stage time limit): "Retry" and "Stop". After a second failure, "Stop" only.
- **Stage 4**, same causes: "Retry", "Continue with the checklists only", "Return to contracts", "Stop".
- **Spend limit reached:** no retry. At stage 2, "Stop" only. At stage 4, "Continue with the checklists only" and "Stop", because the checklists and the readiness line are code and cost nothing. For the daily limit the screen shows when it resets.
- **Continuing with the checklists only** states that the Critic's output is not available and why, and sets readiness to "Not ready".
- **A failure is never shown or recorded as "no view".** They are different results with different rules.

---

## 4. Thesis record schema

**Added 18 November 2026, inside `thesis`:** `summary` (one sentence), `rationale` (`{catalyst, confirmation, tempering}`, each a short paragraph) and `horizon_reasons` (a list of sentences), and `branches` (the three branches the Thesis agent set out, bullish, bearish and no view, each with the findings for and against it, whether it meets the precedence rules and why it was pruned; `docs/build-plan.md`, section 4a). They are written by the Thesis agent for the thesis screen and checked by the validation check against the findings in the record. For a thesis the user supplies they are null. The screens are specified in `docs/product-shell.md` and drawn in `docs/site/tradecraft-prototype.html`; on the screens the stages use trading terms, mapped in section 3 of that document.

**Added 15 November 2026, top level:** `thesis_origin` (`system` | `system_edited` | `user` | `scan`), `system_draft` (the untouched Thesis agent output, or null), `user_blind_probability` (integer percent or null), `critic_model_family` (string or `"human"`). **Added 16 November 2026:** `baselines: {base_rate_pct, price_only_pct}`, `evidence_families[]`, `inputs_used[]`.

```json
{
  "record_id": "uuid",
  "parent_id": null,
  "created_at": "2026-11-12T13:51:04-0800",
  "thesis_origin": "user",
  "mode": "on_demand",

  "thesis": {
    "claim": "free text",
    "direction_or_vol": "long_vol | short_vol | long_delta | short_delta | none",
    "probability": 55,
    "resolution_criterion": "required, blocking",
    "horizon_days": 60,
    "falsifiers": [{"trigger": "observable", "action": "affirmative"}],
    "stated_edge": "free text",
    "edge_source": "free text",
    "premortem_categories": [],
    "claim_decomposition": {"direction": null, "magnitude": null, "timing": null, "vol": null}
  },

  "market_at_capture": null,

  "contract": {
    "occ_symbol": "...", "strike": 0, "expiry": "...", "side": "...",
    "bid": 0, "ask": 0, "bid_size": 0, "ask_size": 0, "mid": 0,
    "iv": 0, "quote_source": "...", "quote_delay_sec": 0,
    "quote_ts": "...", "recorded_ts": "..."
  },

  "assessment": {
    "gate_pass_live": true, "gate_reasons": [],
    "earnings_in_window": true,
    "clean_iv": 0, "vol_forecast": 0, "richness_residual": 0,
    "tick_count": 2, "recommended_limit": 0, "fill_probability": 0.628,
    "expected_cost_patient": 0, "expected_cost_marketable": 0,
    "prob_itm_risk_neutral": 0, "prob_itm_estimated_real": 0,
    "structure_base_rate": 0, "evidence_grades": {}
  },

  "critic": {
    "reframed_question": "assertion converted to question before the LLM saw it",
    "checklist_hits": [],
    "objections": [{"claim": "...", "premise_disposition": "conceded|reformulated|upheld"}],
    "steelman": "mandatory",
    "cited_findings": [],
    "veto": false,
    "veto_basis": "structural precondition, not model judgement",
    "overridden": false,
    "override_reason": null,
    "concession_on_good_thesis": null
  },

  "barriers": {
    "profit_target": 0, "stop": 0, "time_limit_days": 0,
    "invalidation_conditions": [],
    "resting_orders_placed": false
  },

  "sizing": {
    "max_loss_per_contract": 0, "contracts": 0,
    "pct_of_capital": 0.00217, "portfolio_check": "pass"
  },

  "execution": { "assumed_fill": 0, "actual_fill": null, "paid_spread_fraction": null },

  "outcome": { "barrier_hit": null, "resolved_at": null, "label": null, "traded": false }
}
```

`market_at_capture` is deliberately `null` — the record proves nothing from the market was shown before the thesis was frozen.

---

## 5. Agent activation

| Agent | On-demand | Note |
|---|---|---|
| Evidence Retriever | **Active** | balanced retrieval, not disconfirming-first |
| Regime Assessor | **Active** | unchanged |
| **Critic** | **Active — centrepiece** | checklist first, LLM confined to its nine tasks; **different model family from the Thesis agent** (demo exception: same family, stated on screen) |
| **Fundamental Analyst** (was Filing Analyst) | **Active on path A** | filings, earnings materials, news, estimates, earnings history |
| **Technical Analyst** | **Active on path A — new** | trend, momentum, levels, relative strength, from computed values |
| **Event Assessor** | **Active when expiry spans a report** | §3 step 6 |
| **Thesis agent** | **Active on path A (default)**; skipped on path B | never sees option prices or implied probabilities |
| Hedge Supervisor | Inactive | index only |
| Monitor | Active post-trade | **must emit order tickets, see §7** |
| Post-mortem | Active post-trade | no write path |
| Eval Judge | Active | step-level, κ not raw agreement |

**One new agent** (Technical Analyst, added 16 November 2026). The Critic is not duplicated in the thesis stage; a validation check in code runs there.

---

## 6. Evaluating the critic

**Primary metric is error-identification accuracy, not detection recall.** Models score match-F1 0.50–0.97 while error-*grading* lands at 5–75%, and the hardest class is **flawed reasoning that reaches a correct conclusion (7–24%)** — exactly this use case.

Protocol: **120 planted theses** — 40 resting on refuted signals, 20 right-for-wrong-reasons, 20 base-rate-violating, 20 out-of-corpus, 20 clean controls to catch false vetoes. Paired across configurations: ~30–35 items detects a 30pp difference, ~120 detects 15pp.

Judge **step-level, not outcome-level** (53.8–64.1 versus 35.1–43.9 for outcome-trained judges). Report **κ, not raw agreement** — "85% agreement" has been measured at κ 0.48, and high test–retest reliability coexists with severe position bias.

**Measure concession-on-good-theses as a first-class metric.** Anti-pressure training cut yielding by 32.9 points but cut *evidence-driven updating* by 53.7 points. A critic that never concedes is broken in the other direction.

### The case that the critic adds nothing

A full Planner→Executor→Critic team beat a single evolved agent by **+0.015 (p = 0.80)** at 1.79× the inference calls, and was *worse* on a second task. The critic fired 163 times, changed the action 41% of the time, never revised its own output, and **its prompt evolved to empty.**

Mitigation, adopted above: bind the veto to a structural precondition computed outside the model, and confine the LLM to what a rule cannot do.

---

## 7. Cross-cutting correction: reminders do not work

**This belongs in the main spec, not only here.**

Automated stop/take orders moved the disposition effect from +0.082 to **−0.106 (p=0.002)**, entirely by realising losses. A Reminder treatment — price limits that only notify — measured **0.088, i.e. no effect.** Stop-loss users were, on their *unstopped* trades, measurably *more* reluctant to realise losses.

The mechanism disciplines the trade, not the trader. A monitoring agent that sends notifications is reminder-class by construction; in the one laboratory experiment that tested reminders they had no measured effect on the disposition effect. Treat notifications as unproven and resting orders as the default.

**Therefore: a falsifier's output is a resting broker order ticket, and order-placement rate is recorded per trade as a first-class metric.**

---

## 8. What can and cannot be measured about the user

**Cannot: calibration.** At n=100 the 95% interval on one person's Brier score is 2–4× wider than the largest credible forecasting-training effect, and the standard Brier decomposition is biased at small n in the *flattering* direction. Thresholds: nothing under 30; gross miscalibration only at 30–100; an interval-bearing score at 100–300; a reliability curve above 300. **Never display "you are well calibrated."**

**Can, at n=1:** cost estimate versus realised, falsifier compliance rate, resting-order placement rate, divergence from market-implied, reference-class drift, premortem category hit rate.

---

## 9. Open questions

1. **Earnings-date sourcing** with before-open / after-close timing — the binding constraint on step 6, needed far more often than first assumed
2. **Does a typed override reason change behaviour** — no credible evidence found
3. **Do users learn to discount a one-sided critic** — no credible evidence found
4. **Does question-reframing survive multi-turn pushback** — no credible evidence found, and this matters because conversation is multi-turn by nature
5. **Base-rate display effect** — show for the record and friction, not persuasion
6. **Transfer** — every human-factors finding above comes from clinical, recidivism, writing or QA tasks, never financial theses. Nearly all 2026 sources are unreviewed preprints
