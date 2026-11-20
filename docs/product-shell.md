# Tradecraft: product shell and screens

**Settled:** 18 November 2026, by the operator, after reviewing a clickable mock-up.
**Applies to:** the application's screens for on-demand mode, stages 1 to 4.
**Reference mock-up:** `docs/site/tradecraft-prototype.html` (open it in a browser and click through). **The build must match it: layout, wording, colours and behaviour.** Where this document and the mock-up disagree, the mock-up wins and this document is corrected.

**Exception: operator decisions dated after the mock-up was approved win over the mock-up.** During the build the operator settled states the mock-up does not draw and changed a few it does. Each is marked "operator decision" with its date in this document, and the application follows them. Do not "correct" the application back to the mock-up on these points. As of 18 November 2026 they are:

| Where | What differs from the mock-up |
|---|---|
| Section 2 | One open request at a time; the in-page "Leave this analysis?" confirmation; reload and second-tab behaviour |
| Section 5 | Search order within the first group; "Recent analyses" empty state; the mock-up's "NO VIEW · Stopped, nothing recorded" row is not built |
| 6.2 | Three thesis outcomes, the split evidence panel and "Take a view yourself" (drawn in the mock-up from 18 November, night); the results-against-estimates row reads "moderate" |
| 6.1 | Six screened-out tiles with "for this reason alone" (the mock-up draws four); the line above them; overlapping DTE buckets and the second wording; "Stop" on the pass screen; the FAIL state with "Override and continue" and a rationale; the market-closed, not-checked and live-fallback states |
| 6.3 | The outcomes when stage 3 cannot offer a selection; the build decisions of 19 November 2026 (events shown and not filtered, 60-day high and low, "before slippage" and "approximate" labels, filtered-out rows, PROVISIONAL, no override in stage 3) |
| 6.4 | The line shown when the Critic's output is rejected twice; the build decisions of 19 November 2026 (working panel, the "More detail" fold, how checks are counted, Not ready wording, the no-passages line, the end panel) |
| 6.5 | The buttons when a stage stops on a failure |

The mock-up file itself has not been redrawn to show these.

The mock-up uses a fictional underlying (EXMP) and illustrative figures. Its markup and styles are the starting point for the real front end; its hard-coded data is replaced by the engine's output.

## 1. What is settled and what is not

| Settled | Not designed yet (do not invent; show as disabled or leave out) |
|---|---|
| Navigation: a stage bar, one stage on screen at a time | Records page |
| Home screen | Settings page (saved defaults) |
| The four stage screens, as in the mock-up | Welcome screen or login (the operator has not chosen) |
| Trading wording on every screen (section 3) | Stage 5 (decision and record) and stage 6 screens |
| Direction label colours (section 4) | "View option chain" on the gate screen |
| Light and dark themes (Ledger, Night Desk) | |

## 2. Navigation

- **App bar:** product name (returns to Home), Home, Records, Settings, theme toggle.
- **Request header:** the underlying's symbol, the time the request opened, market status and quote delay. When the market is closed it reads "market closed · snapshot of [date]" in place of "market open · quotes delayed 15 minutes" (operator decision, 18 November 2026).
- **Stage bar:** four steps: Liquidity gate, Thesis, Contracts, Challenge. "Contracts" is the short label for stage 3, Market and contracts.

| Step state | Appearance | Behaviour |
|---|---|---|
| Complete | Green tick, green underline, "Complete" (the thesis shows "Frozen" and the time) | Clickable. Opens read-only |
| In progress | Filled blue number, blue underline | The current screen |
| Not reached | Grey number | Disabled |

- **One stage on screen at a time.** Moving forward replaces the screen; nothing scrolls into a long page.
- **Reviewing a completed stage:** a banner says the stage is read-only, with "Back to the current stage". Every control that changes state is disabled. Detail panels and collapsed lists may still be opened.
- **Return to contracts** (on the challenge) reopens stage 3 for a new selection. The Challenge step returns to "not reached" until the user continues, and stage 4 runs again for the new selection.
- **Stop** and **Reject and stop** return to Home.
- **After "Proceed to decision"** all four stages are complete and reviewable.

**One open request at a time (operator decision, 18 November 2026).** Strict: one open request, not just one running.

- **Leaving.** While a request is open, Home's search box is not reachable without leaving it. Clicking Home or the product name shows an in-page confirmation (not a browser dialog): "Leave this analysis? It will be stopped." with "Stay" and "Stop and leave". Stopping follows the existing rules: before the first view the pending log is discarded; after it, a decision record says where the request ended.
- **Reloading the page** restores the open request at its current stage, from the workflow state.
- **A second browser tab** that opens the app while a request is open shows that request, not Home.
- **If the engine restarts** while a request is open, the request is ended and recorded as "interrupted" under the same pending-log rule. It is not resumed.

## 3. Wording rule

Screens use the trading register below. The design documents keep their plainer wording as the explanation; the left column is what they say, the right column is what the screen says.

| Design documents | Screen |
|---|---|
| bid-ask gap | bid-ask spread |
| days to expiry; expiry | days to expiration (DTE); expiration |
| price (of the underlying) | spot |
| option price | premium (mid) |
| usual range | typical realized move |
| options imply a move of | implied move |
| volatility state | (not shown as a label; see 6.2, "Current volatility") |
| put credit spread; call debit spread | bull put spread (credit); bull call spread (debit) |
| call credit spread; put debit spread | bear call spread (credit); bear put spread (debit) |
| structure | strategy |
| trading cost | est. slippage |
| maximum gain; break-even | max profit; breakeven |
| pays when the view is right | profitable if thesis holds |
| base-rate chance of profit; market-implied chance | POP, historical base rate; POP, market-implied |
| exposure | Greeks |
| chart levels | support and resistance |
| other construction | equivalent construction |
| premium-selling structure | short-premium strategy |
| the strongest case for; against | bullish thesis: bull case, then bear case. Bearish thesis: bear case, then bull case. Range-bound thesis: case for, then case against. The case for the thesis always comes first |
| what would show the view to be wrong | invalidation criteria |
| narrow support | concentrated evidence |
| event inside the window | event risk inside the holding period |
| invalidation is not watched | invalidation not monitored |
| Federal Reserve decision | FOMC decision |
| qualifies; set aside | passes the liquidity screen; filtered out |
| recommended (first-ranked candidate) | best fit (never "recommended") |
| ranking: match the view; larger payoff; lowest cost | fit to thesis; reward-to-risk; lowest slippage |

Fixed lines that must appear: "No demonstrated predictive edge" on every system thesis; "The top-ranked candidate is the best fit on the chosen ranking, not a recommendation to trade" on stage 3; the same-model-family caution on stage 4 while the Critic shares a model family with the Thesis agent.

## 4. Direction labels

One label per thesis, used on the thesis screen, the stage 3 and 4 headers and the Home list. Tinted background, uppercase, monospace.

| Label | Colour | Light token | Dark token |
|---|---|---|---|
| BULLISH | green | `--good` #0a7d0a | #3fbf3f |
| BEARISH | red | `--crit` #c23232 | #e66767 |
| RANGE-BOUND | amber | `--warn` #8a5a00 | #e5b454 |
| NO VIEW | grey | `--ink-3` | `--ink-3` |

Status labels (PASS, FLAG, N/C, READY, STRONG, MODERATE, CONTRARY) keep their outline style without the tint, so that a direction is not mistaken for a status.

## 5. Home

- Heading "Which underlying do you want to research?", one search box, "Run analysis".
- **Symbol search with suggestions (requirement added 18 November 2026).** The box accepts a ticker symbol or a company name and shows matching listed symbols as the user types, as on charting and trading sites.

  | Aspect | Requirement |
  |---|---|
  | Coverage | Every US-listed stock and ETF, plus the index symbols the system supports (SPX, XSP). Not limited to the daily snapshot list or to the names the research data source covers |
  | Matching | Case-insensitive, on symbol and on company name. Updates on every keystroke, with no button press |
  | Order | Symbols that start with the text first; then names in which a word starts with it; then any other match. At most 8 rows. **Within the first group (operator decision, 18 November 2026):** names on the daily snapshot list (`universe.txt`) first, then an exact symbol match, then shorter symbols, then alphabetical. The daily list stands in for popularity, which no free source provides; it orders results and does not limit what can be searched |
  | Row | Symbol, company name, type (stock, ETF or index). The matched text is highlighted |
  | Keyboard | Up and down move the highlight, Enter selects, Escape closes. The first row is highlighted by default |
  | Selecting | Clicking or pressing Enter on a row fills the box with the symbol and name. "Run analysis" then starts the request |
  | Free text | "Run analysis" with text that was not selected takes the first match. With no match the request does not start and the screen says "No listed symbol matches" |
  | Speed | The list is held locally and searched in the browser or by the local engine, so suggestions appear without a network call per keystroke |
  | Data | A symbol directory (symbol, name, type) downloaded and stored locally, refreshed about weekly. **The source is chosen at build time and must be free.** Candidates to check from the Mac: the SEC's company ticker file and the Nasdaq Trader symbol directory. Neither was tested from the design session |
  | Not in the first version | Showing in the list whether a symbol has options or research data. The liquidity gate answers the first; "not available" on the brief answers the second |
- Status chips: market open or closed, quote delay, time of the latest snapshot. When the market is closed the first chip reads MARKET CLOSED (6.1, item 9).
- "Recent analyses": symbol, direction label, the strategy and where the request ended, and when. **Operator decision, 18 November 2026:** the panel and its heading are always shown. The list is built from the decision records only, newest first, at most ten rows; each row is as drawn (symbol, direction label, the strategy if one was selected, where the request ended, when). Rows are not clickable in the demo. With no records, one line in the small grey style: "No analyses yet. Search for a symbol above to run your first one." **Correction to the mock-up:** its row "NO VIEW · Stopped, nothing recorded" cannot occur, because Stop after a no-view result writes no record and so leaves no row. A NO VIEW row appears only when the user went on to supply a thesis, which is outside the demo. That example row is not built.

## 6. Stage screens

### 6.1 Liquidity gate

1. **Result line:** PASS or FAIL, "N contracts pass the liquidity screen", the source and time of the chain. Premiums are not shown at this stage.
2. **Screen criteria:** the five criteria with the value in use and its default; a chip reads "All at default" or "N changed from default"; changed values are shown in the accent colour.
3. **Adjust criteria** (button at the foot) opens a compact panel in place, the same width as the other sections:

| Criterion | Control | Range | Default |
|---|---|---|---|
| Max bid-ask spread | slider, step 0.5 | 2% to 10% | 5% |
| Min open interest | slider snapping to 10, 25, 50, 100, 250, 500, 1,000 | 10 to 1,000 | 100 |
| Days to expiration (DTE) | preset list (7 to 21, 22 to 41, 42 to 90, 91 to 180, 7 to 180, Custom) and two number boxes | 7 to 180 | 42 to 90 |
| Max strike distance from spot | slider, step 1 | 5% to 30% | 10% |
| Min premium (mid) | slider, step $0.05 | $0.05 to $1.00 | $0.20 |

   Each slider shows its minimum, default and maximum. Buttons: Reset, Cancel, "Apply and re-screen". Applying re-runs the gate and updates every figure on the screen. **A change applies to the current request only;** saved defaults belong to the Settings page, which is not designed.

   **Strike distance (operator decision, 18 November 2026):** the app measures it as a plain percentage, |strike / spot − 1| at most the setting, which matches the label. The daily census (`scripts/daily/chain_census.py`) uses a log measure, |log(strike / spot)|, so the two can differ by a few contracts at the boundary. The definition is written to the stage 1 decision record.
4. **Liquidity by expiration:** contracts passing the other four criteria in each DTE bucket (7 to 21, 22 to 41, 42 to 90, 91 to 180), the user's bucket highlighted, with the two explanatory lines from the mock-up. Every bucket the DTE setting overlaps, fully or partly, is highlighted; each bar still counts its whole bucket, with no split bars and no fifth bar. When the setting matches one bucket exactly the line reads "The highlighted bucket is your DTE setting, 42 to 90. The other buckets are shown for context."; otherwise "Your DTE setting, 30 to 60, falls across the highlighted buckets. Each bar counts its whole bucket, so the highlighted bars can include contracts outside your setting; the count at the top of the screen is for your setting exactly." (operator decision, 18 November 2026).
5. **Bid-ask spread:** median, tightest and widest spread of the passing contracts, with the fixed explanation of what the spread is and what tight (under about 2%) and wide (above 5%) mean. The 2% figure is display copy, not a control.
6. **Contracts screened out, by reason.** Six tiles, always shown in this order, including when a count is zero: Spread too wide; Open interest below minimum; Outside DTE range; Strike too far from spot; Premium below minimum; Invalid quote. A contract is counted under every criterion it fails, so the tiles overlap. Each tile shows its count and, beneath it in the small grey style, "N for this reason alone" (contracts failing only that criterion); the Invalid quote tile shows only its count. Above the tiles: "X of Y contracts screened out. A contract can fail more than one criterion, so the tiles add up to more than X." The figures recompute when criteria are applied (operator decision, 18 November 2026).
7. Sections 4 and 5 are the same height. Buttons on a pass, in order: "Adjust criteria", "View option chain" (disabled), "Stop", "Continue to thesis". **"Stop" was added to the pass screen on 18 November 2026 (operator decision; the mock-up does not draw it),** so that every stage can be ended from its own screen. It stops the request and returns to Home; nothing is recorded, since stage 1 is before the first view.
8. **On a FAIL (operator decision, 18 November 2026; the override confirmation was not drawn in the mock-up).** The same layout as the pass screen: the FAIL chip, the count and the reasons contracts were screened out. "Adjust criteria" stays. "Continue to thesis" is replaced by "Override and continue", which opens a one-line "Rationale" box and a confirm button; the rationale is required. On confirm, a decision record is written marked `decided_by: user, overruled: liquidity_gate`, with the rationale, and the request continues to the thesis. "Stop" is also shown. **The override panel also says (operator decision, 19 November 2026):** "The system only proposes contracts that pass the screen. If none pass at these criteria, no strategy will be built. Adjusting the criteria is the alternative." An invalid quote (no bid, no ask, or bid above ask) cannot be overridden. Existing mock-up styles only; nothing else is added to the screen. The screen says "override" and "rationale", as in `docs/site/THEME.md`.
9. **Market closed (operator decision, 18 November 2026).** "Market open" means regular hours on a trading day; until the NYSE holiday calendar is built, weekends and after-hours count as closed.
   - *Symbol in the daily snapshot.* The PASS or FAIL chip stays, with a second chip, PROVISIONAL, in the dashed style used for N/C. Headline unchanged: "N contracts pass the liquidity screen". Source line: "Snapshot of [date], [time] ET · market closed". One line under it: "Provisional: based on the latest snapshot. The screen is re-run on live quotes when the market opens." The rest of the screen is as drawn, computed from the snapshot. The snapshot keeps strikes outside the census's 10% band (flagged, not dropped), so the strike control works in full on snapshot data.
   - *Market open but the live chain cannot be fetched (operator decision, 18 November 2026).* The gate falls back to the snapshot. Same PROVISIONAL chip and provisional line; the source line reads "Snapshot of [date], [time] ET · live quotes unavailable". If neither source answers: one chip, NOT CHECKED; headline "Liquidity could not be checked."; line "The option chain could not be retrieved from the live feed or the daily snapshot. You may continue to the thesis; contracts cannot be chosen until a live screen has passed."; the same sections hidden and the same two buttons as below.
   - *Symbol not in the daily snapshot.* One chip, NOT CHECKED, in the dashed style. Headline: "Liquidity cannot be judged until the market opens." Line under it: "[SYMBOL] is not in the daily snapshot. You may continue to the thesis; contracts cannot be chosen until a live screen has passed." The liquidity by expiration, bid-ask spread and screened-out sections are hidden. "Continue to thesis" and "Stop" are shown; no override is needed.

### 6.2 Thesis

While the agents run, a panel lists each agent with its status (waiting, working, done); the three analysts are shown as a parallel group. Then the brief:

1. **Header:** direction label, "Directional thesis, N-day horizon", "No demonstrated predictive edge".
2. **Summary:** one sentence stating the view and its main reason.
3. **Three blocks:** "The catalyst", "The confirmation", "What tempers it". The third states the thesis's own weak points (for example one catalyst behind two findings, or a move already made since the catalyst).
4. **A line explaining the "no demonstrated predictive edge" label.**
5. **The evidence panel** beside **Invalidation criteria**, the same height. Invalidation criteria are numbered, each with what it reverses. **Revised 18 November 2026 (night):** the evidence panel has two parts on every brief. "Evidence that carries a direction": each row has its bearing label, the comparison, the kind, source, date and grade. "Context, with no direction": each row has the fact and why it has no direction, with sector and macro findings under a "Sector and macro backdrop" sub-heading.
6. **Historical statistics and horizon** (full width): the horizon table with the recommended row highlighted; beside it "Why an N-day horizon"; beneath, three definition boxes: "Base rate, higher close", "Typical realized move", "Current volatility".
7. Buttons: Reject and stop, Edit, "Accept and freeze the thesis".
8. **Reasoning view (added 18 November 2026, after the mock-up; not drawn in it).** In the brief's expandable detail: the three branches the Thesis agent considered (bullish, bearish, no view), the findings for and against each, whether each met the precedence rules, and why a branch was pruned. It adds no figure and no score. Where the symbol has been analysed before, the screen says so and links the earlier records.

**The three outcomes (operator decision, 18 November 2026, night; `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`, drawn in the mock-up under the "Thesis outcome" switch).**

| Outcome | The brief shows | Buttons |
|---|---|---|
| A view | As above, with **the age of the latest earnings report and the date of the next one shown prominently** (operator ruling, 19 November 2026; not drawn in the mock-up, layout to come from the operator). Where the view rests on the earnings result alone: the WEAKLY SUPPORTED chip, the sentence "This view rests on the earnings result alone, reported N days ago.", and the three blocks titled "The basis", "What is missing", "What tempers it" | Reject and stop, Edit, "Accept and freeze the thesis" |
| No view: the evidence that carries a direction points both ways | NO VIEW, the reason in a sentence, the findings on each side, the context, "What you can do", statistics | "Stop", "Take a view yourself" |
| No view: nothing carries a direction | NO VIEW, the reason, the context, "What you can do", statistics | "Stop", "Take a view yourself" |

**"Take a view yourself"** opens its own screen within the Thesis stage: direction and horizon; "What are you relying on?" (the evidence on the brief, each item marked as carrying a direction or as context); "What would prove you wrong?"; "How your thesis stands" (NOT SUPPORTED, PARTLY SUPPORTED, WELL SUPPORTED, computed in code); buttons "Back to the evidence", "Stop", "Freeze my thesis". Nothing from the option market is shown. The results-against-estimates row is labelled "data provider, [date] · moderate".

**As built on 19 November 2026 (operator decisions of that day; none is drawn in the mock-up, and each uses the mock-up's existing styles).**

- **Under the summary sentence,** one line in the small grey style: "Latest report: [date] ([N] days ago) · Next earnings report: [date or 'not available']".
- **A bearish view:** the statistics table's second column is "Base rate, lower close". When the figure is under 50%, the sentence "This view runs against the base rate: [SYMBOL] closed lower in [X]% of past [N]-day periods." is added.
- **"Flags and missing inputs"** between the evidence and the statistics: each risk flag as a row with the FLAG chip and its trigger; each unavailable input as a row with the N/A chip and the reason. Hidden when both are empty.
- **"How the system reasoned"** at the foot of the brief, collapsed: the three branches, each with the findings for it, the findings against it, whether it met the rules, and "Selected" or the reason it was pruned.
- **The horizon reasons are code-built.** The heading is "Why the [N]-day row is recommended". The Thesis agent's sentences are commentary, shown only on a view under "How the evidence fits this horizon". (Decision document, section 5.)
- **Context rows** carry a fixed sentence saying why the finding has no direction, and the four no-view results have fixed headlines; both lists are in the decision document, section 5.
- **Agents-working panel.** A "Stop" button in place of the mock-up's "Skip the wait". Besides WAITING, WORKING and DONE: **FAILED** (an error, or output that failed validation after its one retry) and **TIMED OUT** (the agent's time limit), both in the flag style; **NOT RUN** (the stage stopped before the agent started, or it was cancelled), in the dashed grey style. When the stage stops the panel stays on screen with each agent's final status, one plain sentence above it naming what stopped it, and the actions of 6.5 below.
- **Not designed, one plain line each:** the range-bound brief, and the brief when a draft fails validation twice. The "analysed before" line is not built.

**What this asks of the engine** (see the agent contract and the record schema):

- The Thesis agent returns `summary`, `rationale {catalyst, confirmation, tempering}` and `horizon_reasons[]` in addition to its existing output. Each sentence must rest on a finding already in the record; the validation check rejects a rationale that cites anything else. No figure is set by the agent.
- The three definition boxes are fixed templates in code, filled with the measured figures. "Current volatility" is chosen by the measured volatility state:
  - quiet: "{SYMBOL} has been moving less than it normally does. The figures above may overstate the swings over the next {N} days; quiet periods can end abruptly."
  - normal: "{SYMBOL} has been moving about as much as it normally does, so the figures above are a fair guide to the next {N} days. In a high-volatility period they would understate the swings."
  - elevated: "{SYMBOL} has been moving more than it normally does. The figures above are likely to understate the swings over the next {N} days."

**Evidence in three cards (operator decision, 19 November 2026; now drawn in the mock-up).** The evidence that carries a direction is one card, with a tally of bullish and bearish findings in its heading. "Context, with no direction" and "Sector and macro backdrop" are each a separate card that folds, with a count beside the heading. Context starts open with four rows or fewer and folded otherwise; the backdrop starts folded (proposed in the build; confirmed by the operator, 19 November 2026). **On a no view, "What you can do" sits in the view card and the evidence takes the full width (operator decision, 19 November 2026; drawn in the mock-up).**

### 6.3 Contracts (market and contracts)

The stage 3 output card as documented in `docs/site/market-contracts.html`, part 5, with the wording of section 3: header, expiration strip, "Rank by" and filters, "Max loss for this trade", ranked rows with the detail opening in place, the filtered-out line. The strategy whose detail is open is the selection; the button reads "Continue to the challenge with the …". With no detail open the top-ranked candidate is the selection.

**When stage 3 cannot offer a selection (operator decision, 18 November 2026; the third outcome replaced on 19 November 2026).** Four outcomes. In every case the thesis is already frozen and recorded, so "Stop" writes a decision record saying where and why the request ended. There is no way back into stage 1's criteria from here.

| Outcome | What it is | Screen | Buttons |
|---|---|---|---|
| Market closed and no snapshot covers the symbol | Expected, not a failure | "Contracts cannot be chosen until the market opens." It says this is consistent with what stage 1 showed | "Stop". No retry |
| No option data although the market is open, or the snapshot cannot be read | A failure | Shows which source failed | "Retry" (up to three; it is code and costs nothing), "Stop" |
| No leg can come from a passing contract (**operator decision, 19 November 2026, replacing the ruling of 18 November:** there is no "Override and continue" in stage 3; a stage 1 override carries forward without a second prompt) | A result, not styled as an error | "No candidate built: no eligible contracts at your criteria." The header and expiration strip stay | "Stop". Switching expiration rebuilds the candidates |
| No candidate built, or every candidate filtered out | A result, not styled as an error | The header and expiration strip stay. Each candidate is listed with the filter that removed it; its detail can still be opened | "Stop". Switching expiration rebuilds the candidates |

**Operator decisions for the build (19 November 2026).** The full list of 22 is in `docs/decisions/2026-11-17-stage-3-contract-selection.md`, "Operator decisions for the build". What they change on this screen:

- **Rulings of 19 November 2026 (afternoon), after the first runs.** An expiration may serve a horizon from up to three trading sessions before the horizon date, and the card states the gap either way ("1 day before it", "27 days beyond it"). The legs of a spread or an iron condor are not held to the bid-ask criterion one by one (the cost cap judges the structure); a leg quoted wider than the setting carries, under its row in "Legs and quotes": "This leg's quoted spread is [X]% of its premium, above your [Y]% setting. Cost is judged on the whole structure." A single option's row states its strike's distance from spot: "The strike, 46, is 1.4% above spot."
- **Legs:** the stage 1 criteria in force without the DTE criterion; no expiration under 7 DTE. A second strike that cannot be placed means the candidate is not built and is listed with the reason. Where only one construction can be built at the chosen strikes the detail reads "Equivalent construction. Not available at these strikes." (wording by operator decision, 19 November 2026).
- **Market closed, symbol in the snapshot:** the PROVISIONAL chip and the source line of 6.1, item 9. Continue stays allowed.
- **Labels:** "Profitable if thesis holds, before slippage"; "POP, historical base rate, before slippage"; "POP, market-implied, approximate".
- **Events are shown, not filtered.** The line under the expiration strip gives the next earnings date and the next ex-dividend date ("none declared" where no ex-dividend date is declared; "not available" where the data does not cover the symbol). A row whose expiration falls after the earnings date, or after the ex-dividend date where it has a short leg, is marked. The filters line reads "Events **shown, not filtered**". The control to include or exclude such candidates is deferred.
- **Support and resistance** are the 60-day closing high and low from stage 2, labelled "60-day high" and "60-day low", on the payoff chart and in the detail. Context only.
- **Filtered-out candidates:** the same row layout below the "Filtered out" line, with no rank, the reason in the grey line and Detail available. **In place of the rank the row carries a FILTERED label beside the strategy name (operator decision, 19 November 2026):** a dash read as a missing row number.
- **Bearish and range-bound sentences** mirror the bullish ones; a long put's max profit is a dollar figure.
- **Poor match:** "Poor match. Figures assume holding to expiration. Your thesis covers the first N days; closing then will give a different result."
- **A thesis the user entered:** the header reads "Your thesis, N-day horizon".
- **Ranking and expiration changes** reuse the chain already fetched; it is fetched again on Retry or "Return to contracts". The max-loss figure is recorded when the field loses focus and at selection.
- **Outcomes the mock-up does not draw** are plain lines in the existing styles, as in 6.5.

- **Filtered-out candidates are view-only in the demo** and cannot be selected. **Whether a filtered-out candidate may ever be selected is undecided.**
- **Cost cap: an on-screen control, in the filters row in place of the static "Cost cap" label (operator decisions, 19 November 2026,** after the count showed 35 of 72 candidates over the 5% cap; `docs/build-log.md`). A slider beside the filters, in the style of the stage 1 criteria: 2% to 10% in steps of 0.5, default 5% (`config/stage3.json`), showing its minimum, default and maximum. It is applied when the slider is released, rebuilds the ranking on the chain already fetched, applies to the current request only and is recorded as a user decision. It stays on screen when every candidate is filtered out, so the cap can be raised. Drawn in the mock-up. **The form (a slider, steps of 0.5, applied on release) was confirmed by the operator on 19 November 2026.**

### 6.4 Challenge

The challenge card as documented in `docs/site/challenge.html`, part 7 (layout B), with the wording of section 3: header with the selected strategy and contract count, readiness line, same-model caution, critic column (bull case, bear case, how this trade loses, objections with grounds), checks column (thesis, contract), and the three buttons stacked in the checks column. "N passed" opens the list of passed checks. Results use four states: flagged, could not be checked (N/C), not applicable (N/A), passed.

**When the Critic's output is rejected twice (operator decision, 18 November 2026).** The screen shows the two checklists and, in place of the Critic's column, one line: "The Critic's output was rejected by the output check: [the rule it failed]. It was returned once and failed again." The wording differs from the timeout case (6.5) so the two faults can be told apart. Readiness reads "Not ready" (the readiness table already lists a rejected Critic output as a not-ready condition). Buttons: "Proceed to decision", "Return to contracts", "Stop"; no manual retry, since the one return has been used. Proceeding past "Not ready" is recorded as such. The rejected output is not displayed; it is stored in the decision record and the trace with the check result.

**Operator decisions for the build (19 November 2026).** The full list of 18 is in `docs/decisions/2026-11-17-stage-4-challenge.md`, "Operator decisions for the build". What they change on this screen:

- **While the agents run:** stage 2's agents-working panel with three rows (Evidence Retriever, Critic, Output check) and "Stop". Drawn in the mock-up.
- **"More detail"** is one fold in the "N passed" style, under the two columns: each claim's standing, the priced-in reading (the figure set by code, the reading by the Critic), what is missing, and the research passages cited with source, section and evidence grade. Drawn in the mock-up. The user's original wording is not in it.
- **Counting.** Each box's header counts its checks by overall result. A line inside a check with a different result (an N/C line under a flagged event check) is its own row and is not counted. "Not applicable" and "passed with a note" sit in the fold with the passes, labelled; the header adds "n not applicable" only when there is one. This differs from the mock-up, which draws N/A as an open row.
- **Not ready:** the chip reads NOT READY in the flag style; the headline is "N blocking condition(s)."; the sentence gives each condition and its remedy. A stale thesis: "Start a new analysis to redraft the thesis." A moved price: "Return to contracts to select on current quotes."
- **No research passages:** one grey line under the same-model caution: "No research passages were retrieved: [reason]. The critic worked from the checklists and the thesis record alone." The retrieval method is recorded and not shown.
- **A thesis the user entered:** the header reads "Your thesis, N-day horizon · …".
- **Case names:** bullish, "Bull case" then "Bear case"; bearish, "Bear case" then "Bull case"; range-bound, "Case for" then "Case against".
- **After "Proceed to decision":** the mock-up's end panel without its "END OF THE PROTOTYPE" chip; the four stages stay reviewable from the stage bar until the user goes home.

### 6.5 When a stage stops on a failure (operator decision, 18 November 2026; not drawn in the mock-up)

The stage's screen shows a plain message naming what failed (an agent, a time limit or a spend limit), keeps any partial results, and offers these buttons in the mock-up's existing styles. Rules in `docs/on-demand-mode-design.md`, section 3a.

| Stage | Cause | Buttons |
|---|---|---|
| Thesis | Agent failure, timeout, stage time limit | "Retry", "Stop". After a second failure, "Stop" only |
| Thesis | Spend limit | "Stop" only |
| Challenge | Agent failure, timeout, stage time limit | "Retry" (once), "Continue with the checklists only", "Return to contracts", "Stop" |
| Challenge | Spend limit | "Continue with the checklists only", "Stop" |

For the daily spend limit the message says when it resets. "Continue with the checklists only" states that the Critic's output is not available and why, and the readiness line reads "Not ready". A failure is never shown as NO VIEW.

## 7. Themes

Ledger (light) and Night Desk (dark), tokens as in `docs/site/THEME.md` plus `--warn` (section 4). Section headers use the display typeface at about 17px with a rule beneath; sub-headings inside a section are 15px semibold.
