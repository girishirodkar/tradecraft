# Proposal: what earns a finding its bearing

**Date:** 18 November 2026 (night)
**Status:** ACCEPTED by the operator on 18 November 2026 (night), with answers to its open questions. The decision is `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`, which governs where it differs from this text: results against estimates can start a view; a view resting on it alone is weakly supported; an officer departure is bearish when unplanned or with no permanent successor named; no bullish event other than raised guidance; the primary-source limit on a conflict is withdrawn.
**Affects:** Mode 3, step 2A: the Fundamental Analyst's findings and the precedence rules. The conflict rule itself is not changed.

---

## 1. The problem

The design gives every finding "a stated bearing" (supports bullish, supports bearish, none) and never says what earns one. As built, the Fundamental Analyst decides the bearing of each fact on its own.

Six symbols were run live on 18 November 2026 (NVDA, AMZN, TGT, WMT, JPM, MSFT). All six returned no view, because each had strong primary-source findings pointing both ways.

| Observation | Detail |
|---|---|
| Most bearings had no stated comparison | About 9 of roughly 39 directional findings compared a figure with an estimate or with earlier guidance. This is a hand count from the saved runs, not a code count |
| The rest were labelled by tone | Growth was bullish; a decline, a cost or a larger commitment was bearish. Examples: MSFT's devices revenue down 3%; AMZN's capital expenditure; JPM's dividend increase |
| Bearings were not stable | NVDA's Q4 revenue outlook was bearish on one run and bullish on the next |
| Items that are not evidence got a bearing | An investor trimming a stake (a 13F change, on the rejected-signal list); an outage story; a law firm soliciting plaintiffs |
| Grade compounded it | Grade measures the reliability of the source. Every line of the latest earnings release is strong, so one upbeat and one downbeat line "conflict" |

The factor specification already warns against this: most "negative" hits in filings are finance-neutral. A fact points somewhere only against an expectation, and the analyst was given none except the EPS and revenue estimates.

## 2. The proposed standard

**A finding carries a bearing only when the evidence states the comparison that gives it one. Otherwise its bearing is "none" and it is shown as context.**

Three kinds of finding can carry a bearing.

| Kind | The comparison | Bullish when | Bearish when | Who sets the bearing |
|---|---|---|---|---|
| Results against estimates | Reported EPS and revenue against the consensus estimate before the report | Both at or above; or one above and the other within the tolerance | Both below; or one below and the other within the tolerance | **Code,** from the two numbers |
| Guidance change | The company's guidance against its own earlier guidance for the same period, or against the consensus for that period | Raised, or above consensus | Lowered, or below consensus | The analyst, quoting both figures; code checks both are present |
| New event | A discrete event on the defined list (section 3), new since the last earnings report | As listed | As listed | The analyst names the event kind; code checks it is on the list and that the cited item is dated since the last report |

Everything else has bearing "none": segment detail, margins, cash flow, capital expenditure, inventory, buybacks and dividends, year-over-year changes with no estimate beside them, management commentary, and news that reports opinion or price action.

**Mixed results.** EPS above the estimate and revenue below it (or the reverse), each by more than the tolerance, is one finding with bearing "none".

**Open value: the tolerance.** A proposal of 1% either side of the estimate counts as in line. It is a display definition, not a tuned parameter.

## 3. The event list (the part most in need of the operator's edit)

The bearish events are mostly the existing risk-flag list. An event must be new: dated since the latest earnings report.

| Event | Bearing | How it is recognised |
|---|---|---|
| Share offering or shelf registration | Bearish | Existing flag: dilution |
| Guidance lowered outside an earnings report | Bearish | Existing flag: guidance reduction |
| New material litigation or regulatory action | Bearish | Existing flag. A new 8-K or a newly added risk factor; not a law firm's notice |
| Material impairment; exit or disposal costs; non-reliance on earlier statements | Bearish | 8-K items 2.06, 2.05, 4.02 |
| Unplanned departure of the chief executive or chief financial officer | Bearish | 8-K item 5.02. **Not on any list today.** NVDA's case on 18 November |
| Going-concern warning; announced takeover target | No view (unchanged) | Existing severe flags |
| Guidance raised outside an earnings report | Bullish | 8-K with a guidance statement |
| Material agreement, acquisition by the company, buyback, dividend change | None | Direction cannot be read from the event alone |

**Open question 1.** Is an officer departure a bearing-carrying event, a risk flag only, or neither?
**Open question 2.** Should any bullish event besides raised guidance be on the list?

## 4. What it would not do

- **It does not change the conflict rule.** Primary-source findings graded moderate or strong that point both ways still give no view.
- **It does not make a view likely.** A beat with lowered guidance is still a conflict.
- **It does not anchor quarterly guidance against consensus.** Only annual consensus is available, so a quarterly outlook can be compared only with the company's earlier guidance for that quarter, if it gave any. Otherwise it has bearing "none".
- **It does not restore estimate revisions.** No source serves revision history.

## 5. What I would expect on the six symbols

A reading of the saved findings, not a run. The classification of guidance in particular depends on figures I have not checked against the releases.

| Symbol | Bearing-carrying findings under the standard | Expected result |
|---|---|---|
| MSFT | EPS and revenue above estimates. No guidance in the release | Bullish, weakly supported (one finding) |
| JPM | EPS and revenue below estimates | Bearish, weakly supported |
| TGT | EPS and revenue above estimates; full-year guidance raised | Bullish. The $0.50 of tariff refunds in EPS would be listed as context under "What tempers it" |
| AMZN | EPS below the estimate by 4.1%, revenue below by 0.1% | Bearish, weakly supported |
| NVDA | EPS and revenue above estimates; chief executive's departure, if question 1 is answered "bearing-carrying" | No view if so; bullish if not |
| WMT | EPS and revenue above estimates; full-year guidance raised; the raised range still below consensus | No view |

## 6. Costs and risks

- **Fewer findings will carry a direction,** so more views will rest on a single finding and be marked weakly supported. That is an honest description of them.
- **"Results against estimates" becomes the commonest basis for a view.** The research behind this project finds post-earnings drift small and largely gone in liquid names. The label "no demonstrated predictive edge" already says the view claims nothing more; the stage 4 check on narrow support would flag it.
- **A view can sit beside substantial context that reads the other way** (TGT's refunds, AMZN's cash outflow). That context must be shown on the brief, and the Critic in stage 4 sees all of it.
- **The analyst still classifies guidance and events.** Code can check that the two figures or the dated item are present, not that the classification is right.

## 7. If accepted, what changes in the build

1. `Finding` gains `kind` (results against estimates, guidance change, new event, context) and, for a guidance change, the two figures compared.
2. Code builds the results-against-estimates finding itself from the earnings figures; the analyst no longer sets its bearing.
3. An output check: a bearing other than "none" is allowed only on the three kinds, with their required fields.
4. The Fundamental Analyst's instructions drop "which way that one fact points".
5. One re-run of the same six symbols, reported whatever the result (about $0.36).
