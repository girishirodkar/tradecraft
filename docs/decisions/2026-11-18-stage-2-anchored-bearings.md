# Stage 2 revised: anchored bearings, three outcomes, and the user's own view

> **FROZEN (operator decision, 19 November 2026).** Stage 2's rules are frozen as of 19 November 2026. The freeze covers what earns a bearing, the event list, what starts a view, the conflict rule, the grades and the recent test, and the four fault fixes and the guidance ruling of 19 November (all built). From now on, anything a run shows about stage 2 goes on the "After the demo" list in `docs/build-log.md` and is not changed, **unless it stops a run from finishing or makes a screen show something false.** A build session that thinks something meets that bar stops and asks the operator before changing it.

**Decided:** 18 November 2026 (night), by the operator.
**Status:** approved for the build. It adopts the proposal in `docs/proposals/2026-11-18-bearing-standard.md` with the operator's answers, and adds the path after a no view.
**Affects:** on-demand mode, step 2A (the Fundamental Analyst's findings, the precedence rules, the brief) and step 2B (the user's own thesis). The conflict rule and the grades are unchanged.
**Screens:** `docs/site/tradecraft-prototype.html`, thesis stage. The "Thesis outcome" switch in the prototype bar shows each outcome.

## 1. Why

Six symbols were run live on 18 November 2026 (NVDA, AMZN, TGT, WMT, JPM, MSFT). All six returned no view under the conflict rule. The cause was in the input to the rule, not the rule:

- The design gave every finding "a stated bearing" and never said what earns one. The Fundamental Analyst labelled facts by tone: growth bullish, a decline or a cost bearish.
- About 9 of roughly 39 directional findings stated a comparison (a hand count).
- Bearings were unstable: NVDA's revenue outlook was bearish on one run and bullish on the next.
- Items that are not evidence received a bearing, including a 13F holding change, which is on the rejected-signal list.
- Every line of an earnings release grades "strong", so one upbeat and one downbeat line produced a conflict.

A first clarification the same evening (weak findings and standing disclosures do not count towards a conflict) stays in force. Two wider changes were considered and rejected: weakening the conflict rule, and reducing every periodic report to its headline.

**This decision was made after seeing those six results.** No outcome was scored and no trial was spent. The six symbols are re-run once after the change and the result is accepted as it comes.

## 2. What earns a bearing

**A finding carries a bearing only when the evidence states the comparison that gives it one. Otherwise its bearing is "none" and it is shown as context.**

| Kind | The comparison | Bullish when | Bearish when | Who sets the bearing |
|---|---|---|---|---|
| Results against estimates | Reported EPS and revenue against the consensus estimate before the report | Both at or above; or one above and the other within the tolerance | Both below; or one below and the other within the tolerance | **Code,** from the two numbers |
| Guidance change | The company's guidance against the consensus for the same period or, where there is none, against its own earlier guidance for that period. EPS, revenue or net sales, and operating income or operating margin only | Raised, or above consensus | Lowered, or below consensus | **Code,** from the figures the analyst extracts (operator decision, 19 November 2026; see below) |
| New event | A discrete event on the list in section 3, dated since the last earnings report | As listed | As listed | The analyst names the kind; code checks the list and the date |

- **Everything else is context,** with bearing "none": segment detail, margins, cash flow, capital expenditure, inventory, buybacks and dividends, year-over-year changes with no estimate beside them, management commentary, and news that reports opinion or price action.
- **Context is kept and shown.** It may be quoted in the rationale, especially under "What tempers it". It cannot start, support or cancel a view.
- **Mixed results** (EPS above and revenue below, or the reverse, each by more than the tolerance) are one finding with bearing "none". Guidance is one finding per guided measure, each set in code (operator decision, 19 November 2026); a measure raised beside another lowered gives two findings that conflict.
- **The results-against-estimates finding always grades moderate:** recent and specific, not a primary source, because the comparison uses the data provider's reported and estimated figures. It can start a view and can conflict.
- **Tolerance:** within 1% of the estimate counts as in line. A display definition, held in configuration.
- **Quarterly guidance** can be compared only with the company's own earlier guidance for that quarter. Only annual consensus is available, so otherwise its bearing is "none" and the missing input is listed in `inputs_unavailable`.
- **Rejected signals** (`config/rejected_signals.json`) are not findings at all. **Ruling of 19 November 2026, after the re-run:** the check applies to findings that carry a bearing, and to the Thesis agent's text. Description from the Regime Assessor and the Technical Analyst, and any context finding, is exempt, including a trend against a moving average: it is description, which the design allows. (In the re-run the check had refused the Regime Assessor's description of SPY against its 200-day average on every symbol.) **The Thesis agent's text is tested by the validation check's own list of price-derived terms** (trend, momentum, relative strength, moving average, support level, resistance, breakout, overbought, oversold), not by the shared rejected-signal patterns (operator decision, 19 November 2026). The shared patterns would have refused "over 30 days" in three of the four views of the re-run; they stay as they are for stage 4, where a match is a flag.
- **One guidance figure yields one finding (ruling of 19 November 2026, decided after the re-run; it changes no result).** Where a consensus figure exists for the same period, the guidance is compared with consensus only; it is compared with the company's earlier guidance only when no consensus exists. In the re-run WMT's FY27 EPS guidance had been read two ways, raised against earlier guidance and below consensus. Under this rule it is one bearish finding (below consensus), which still conflicts with the results above estimates: **WMT remains no view.**
- **Guidance against consensus is set in code (operator decision, 19 November 2026, after the 43-symbol run).** The analyst quotes the two figures; code sets the bearing. A guided range that contains the consensus figure is in line: bearing "none", context reason `in_line`. A range wholly above consensus is above; wholly below is below. A single guided figure within 1% of consensus is in line. Extended the same day to all guidance: see the next point.
- **Every bearing in the system is set in code from figures or comes from a defined event; no bearing rests on a model's reading of wording (operator decision, 19 November 2026).** For guidance:
  - **The analyst extracts and classifies nothing.** For the new guidance, and for the earlier guidance or consensus, it extracts the measure, the period, the basis (for example adjusted or reported) and the low and high figures.
  - **Only three measures can carry a bearing:** EPS; revenue or net sales; operating income or operating margin. Any other guided measure, including capital expenditure, costs, tax rate and share count, is context with the reason "Direction cannot be read from this measure".
  - **A comparison is made only when measure, period and basis match;** otherwise the finding is context.
  - **Against earlier guidance:** raised when both ends are at or above the earlier ones and at least one is higher; lowered for the reverse; unchanged is "reaffirmed", bearing "none"; narrowed or moved both ways is "mixed", bearing "none".
  - **Against consensus:** as in the point above.
  - **Guidance stated in words,** with no figures to extract, is context with the reason "Stated in words, not figures" and the passage quoted.
  - **As built, for the operator to correct:** the measure is recognised in code from its name after removing words of basis and period; "operating profit" is read as operating income; EBIT, a segment's revenue and every cash-flow measure are context. The data provider does not state the basis of its consensus figures, so basis is matched against earlier guidance only. A growth rate is compared only with a growth rate. Three reasons were worded in the build: "Reaffirmed: unchanged from earlier guidance", "Mixed: the range narrowed or moved both ways", "Measure, period or basis does not match". The quoted passage is kept in the record; no screen shows it yet.
- **A finding whose kind is a defined event is never refused as a rejected signal (operator decision, 19 November 2026).** In the patterns file, "support" and "resistance" match only as chart terms ("support level", "support and resistance", "support at" a price), not as ordinary words.
- **The event-kind check applies to the Fundamental Analyst only (operator decision, 19 November 2026).** Every Regime Assessor finding is context, set in code. A scheduled macro release goes to the calendar and the risk flags, not to findings.
- **A price condition in an invalidation criterion (operator decision, 19 November 2026)** needs a price, a currency amount, or the words "close" or "share price" beside "above" or "below". The fixed conditions written by code are exempt from the check.
- **Stability test:** the analyst run twice on the same stored evidence must produce identical bearings.

## 3. The event list

An event must be new: dated since the latest earnings report.

**Amended 19 November 2026 (operator decision): "new" means recent by the grades' own test: dated within the last 30 days, or since the latest earnings report.** As first written, an event a few days before a report was not new: NVDA's chief executive resigned on 12 November and the company reported on 17 November, so the departure would have been context and NVDA a weakly supported bullish view. A resignation five days before a report is not something the results reflect. Found by the stability test, before the six-symbol re-run was made.

| Event | Bearing | How it is recognised |
|---|---|---|
| Share offering or shelf registration | Bearish | Existing flag: dilution |
| Guidance lowered outside an earnings report | Bearish | Existing flag: guidance reduction |
| New material litigation or regulatory action | Bearish | A new 8-K or a newly added risk factor; not a law firm's notice |
| Material impairment; exit or disposal costs; non-reliance on earlier statements | Bearish | 8-K items 2.06, 2.05, 4.02 |
| Departure of the chief executive or chief financial officer, unplanned or with no permanent successor named | Bearish | 8-K item 5.02 (operator decision) |
| A planned succession with the successor named | None | Context |
| Going-concern warning; announced takeover target | No view (unchanged) | Existing severe flags |
| Guidance raised outside an earnings report | Bullish | 8-K with a guidance statement |
| Material agreement, acquisition by the company, buyback, dividend change | None | Direction cannot be read from the event alone |

**No bullish event other than raised guidance** (operator decision). The list is mostly bearish; discrete good news usually arrives as guidance.

## 4. What is enough for a view

1. **Any one bearing-carrying finding graded moderate or strong can start a view, including results against estimates alone** (operator decision, 18 November 2026). The designer recommended that an earnings result should support a view and not start one, because most large companies beat consensus and the headline is quickly priced; the operator chose otherwise.
2a. **Invalidation conditions for a view resting on the results alone are set from a fixed set, in code (ruling of 19 November 2026):** guidance changed against the view; a defined event against the view; and the next earnings result going against it, when its date is known. A condition the agent writes may be added and may not stand alone.
2b. **No change to what counts as recent (ruling of 19 November 2026).** The brief shows the age of the latest report and the date of the next earnings report, prominently. Whether a results finding should stop counting as recent after a fixed number of days is deferred until after the demo.
2. **A view resting on the earnings result alone is marked "weakly supported".** The brief says so in a plain sentence and states how many days ago the report was. Stage 4 will flag it through the narrow-support check and the priced-in test. This marking is a description; it blocks nothing.
3. **The conflict rule is unchanged.** Bearing-carrying findings graded moderate or strong that point both ways give no view. Context never conflicts.
4. Sector and macro evidence still qualifies and cannot start a view on a single stock.
5. **Item 3 replaces the primary-source wording of commit 37dc892** ("only primary-source findings can conflict"). Primary source is one of the three grade checks and nothing more; it is not a separate condition for a conflict.
6. **Regime Assessor findings carry bearing "none"** and are shown as context under "Sector and macro backdrop": none of the three kinds fits them and no fourth is added. The `contested` field stays in the record and cannot be set until a source for macro expectations exists ("macro expectations: no source" is listed in `inputs_unavailable`). For index instruments this means lead evidence cannot carry a bearing, so an index request returns no view (nothing carries a direction) and offers "Take a view yourself".

## 5. The three outcomes of stage 2

| Outcome | When | The brief shows | The user can |
|---|---|---|---|
| **A view** | At least one bearing-carrying finding and none against it | Direction label, summary, the three blocks, the evidence that carries a direction, the context, invalidation criteria, statistics. "Weakly supported" where item 2 above applies | Accept and freeze; edit; reject and stop |
| **No view: conflict** | Bearing-carrying findings point both ways | NO VIEW, the reason in a sentence, the findings on each side, the context, statistics | Stop; take a view yourself |
| **No view: nothing carries a direction** | Only context was found, or the results were mixed or in line | NO VIEW, the reason, the context, statistics | Stop; take a view yourself |

The declined result (a severe flag) and insufficient data are unchanged. **A technical failure is never shown or recorded as a no view.**

**Additions of 19 November 2026 (operator decisions, made while the screens were built).**

*Why a context finding has no direction.* Each finding of kind "context" carries `context_reason` from a fixed list, and the row's small line is the sentence for that reason, then the source and date. The model writes none of the sentences.

| `context_reason` | Sentence on the row | Set by |
|---|---|---|
| `in_line` | In line with estimates | Code, from the results or guidance comparison |
| `mixed` | Mixed: one measure above, one below | Code, from the results or guidance comparison |
| `no_quarterly_consensus` | No quarterly consensus available | Code, for quarterly guidance without a consensus figure |
| `event_no_direction` | Direction cannot be read from the event alone | Code, from the event kind |
| `not_recent` | Too old to count as new | Code, when an event fails the recent test (it is then reported as context, not refused) |
| `price_description` | Price behaviour is description only | Code, for sector and index price behaviour from the Regime Assessor and the Technical Analyst |
| `no_macro_expectation` | No expected figure to compare with | Code, for macro releases and policy decisions |
| `no_estimate` | No estimate to compare with | The Fundamental Analyst |
| `commentary` | Commentary, not a comparison | The Fundamental Analyst |
| `other` | No stated comparison | Anything unset |
| `measure_no_direction` | Direction cannot be read from this measure | Code, for guidance on any measure but EPS, revenue or net sales, operating income or margin (19 November 2026) |
| `worded_guidance` | Stated in words, not figures | Code, for guidance with no figures to extract (19 November 2026) |
| `reaffirmed` | Reaffirmed: unchanged from earlier guidance | Code (19 November 2026; wording from the build) |
| `guidance_mixed` | Mixed: the range narrowed or moved both ways | Code (19 November 2026; wording from the build) |
| `not_comparable` | Measure, period or basis does not match | Code (19 November 2026; wording from the build) |

*The four no-view results.* All use the NO VIEW label and the layout drawn for the conflict case. The wording is fixed and set in code.

| Result | Headline | Under it | Actions |
|---|---|---|---|
| Conflict | The evidence that carries a direction points both ways | The findings on each side, named, then "The system does not choose between two solid findings that disagree." | Stop; Take a view yourself |
| Nothing carries a direction | Nothing found carries a direction | "The system found [N] facts about [SYMBOL]. None comes with a comparison that gives it a direction." A sentence is added when the results were in line with or mixed against estimates | Stop; Take a view yourself |
| Declined | The system declined to take a view | The flag by name, then "A stock in this position trades on that outcome, not on its results." | Stop; Take a view yourself, with "This is an override. The flag stays attached to your thesis and is recorded." beside the button |
| Insufficient data | Not enough data to form a view | What is missing | Stop. Take a view yourself only when at least one evidence item exists to rely on |

The "Evidence that carries a direction" section is kept in every case; when it is empty it shows one row with the NONE chip and "Nothing found carries a direction". A technical failure never uses these screens.

*The horizon reasons are built in code.* On every brief the heading is "Why the [N]-day row is recommended", and the reasons under it come from the rule that chose the row: which rows had eligible contracts; which were set aside and why, with the date; that the recommended row is the one nearest 30 days of those left; any known event inside it; and a warning or a provisional recommendation where one applies. On a view the Thesis agent's `horizon_reasons` are shown beneath, under "How the evidence fits this horizon": they are commentary and must not contradict the code-built reasons; with none, the sub-heading is omitted. On a no view only the code-built reasons are shown, with "The recommendation takes no account of direction. It is the row preselected if you take a view yourself." **This corrects the earlier design, in which the agent wrote the reasons for a choice made in code.**

**The evidence panel has two parts on every brief:** "Evidence that carries a direction" (each row: bearing label, the comparison, kind, source, date, grade) and "Context, with no direction" (each row: the fact and why it has no direction).

## 6. Take a view yourself

This is step 2B made the main road after a no view, in a structured form. Free-text entry with extraction by the Thesis agent stays in the design and is not built for the demo.

1. **Direction** (bullish or bearish) and **horizon** (a row of the measured table; the recommended row is preselected).
2. **What are you relying on?** The user ticks items from the evidence already on the brief, both kinds. At least one.
3. **What would prove you wrong?** At least one invalidation condition, chosen from conditions the system can name, each with a `type` from the fixed list. None is a price level.
4. **How the thesis stands,** computed in code and updated as the user chooses:

   | Verdict | When |
   |---|---|
   | Not supported | No chosen item carries a direction matching the view |
   | Partly supported | At least one chosen item carries a matching direction, and either a chosen item is context or a finding with a direction points the other way |
   | Well supported | Every chosen item carries a matching direction and none points the other way |

   A finding that carries the opposite direction stands against the thesis whether or not the user ticked it.
5. **Freeze my thesis.** Enabled with at least one item and one condition. The verdict does not block.

**Which conditions the system can name (as built, 19 November 2026).** The decision did not say how the list is made. The build session proposed a rule and the operator said to go ahead; it is recorded here so that it can be corrected. Two conditions are offered on every thesis: "The next earnings result goes against the view" (`earnings_result`) and "Guidance is changed against the view" (`guidance_change`). Each event finding on the brief whose direction matches the view adds the condition that would reverse it: for an officer departure, "A permanent chief executive or chief financial officer is named"; for a share offering, "The offering is withdrawn"; for new litigation or regulatory action, "The action is dismissed or settled". The other event kinds add none.

**Recorded:** `thesis_origin: user`; the direction and horizon; the items relied on, each as anchored or context; the opposing findings; the invalidation conditions; the verdict; and that it was entered after a no view, with the reason for the no view. This is the commit point for the pending log, in place of "the first view".

**Unchanged safeguards:** nothing from the option market is shown before the freeze; the agents are not asked again; stage 4's check 9 flags a thesis entered after a no view and one that is not fully supported; the Critic is not told who wrote it.

**Stop after a no view still records nothing.**

## 7. Changes to the build

1. `Finding` gains `kind` (results_vs_estimates, guidance_change, new_event, context) and, for a guidance change, the two figures compared.
2. Code builds the results-against-estimates finding from the earnings figures. The analyst does not set its bearing.
3. Output check: a bearing other than "none" is allowed only on the three kinds, with their required fields; a rejected signal is refused.
4. The Fundamental Analyst's instructions drop "which way that one fact points". It still reports what it finds on both sides.
5. The thesis record gains `support: weak | normal`, and for a user thesis `relied_on[{evidence_id, kind}]` and `verdict`.
6. The brief's evidence panel is split as in section 5. The no-view brief and the "Take a view yourself" screen are built as drawn in the prototype.
7. The stability test in section 2.
8. One re-run of the same six symbols, reported whatever the result. NVDA should remain no view (results above estimates against the chief executive's departure). Nothing is adjusted after that run.
9. Then one run of the other 43 covered symbols, reported as counts by outcome. Nothing is adjusted on those results either.
10. Added 19 November 2026: the four faults the 43-symbol run showed were ruled to be build faults or a gap in the rule, and are fixed (the four operator decisions of that date in section 2). The saved runs were recomputed in code; nine change outcome. The table is in `docs/build-log.md`.

## 8. What this does to the product

Stage 2 no longer promises a drafted view. It establishes what is known against expectations, takes a view when a bearing-carrying finding exists, and otherwise lays out both sides and leaves the direction to the user. With free data sources, "results against estimates" will be the commonest basis for a system view. The report should say so.
