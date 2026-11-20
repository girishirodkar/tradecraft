# Decision: stage 4 challenges the thesis and the contract, and gives no verdict

**Date:** 17 November 2026
**Decided by:** the operator, one step at a time
**Status:** in force. Full rules in `docs/on-demand-mode-design.md`, "Stage 4 redesigned". Page: `docs/site/challenge.html`.

## The decision

1. **Stage 4 challenges the choice of contract as well as the thesis.** The original design questioned only the thesis, because the operator brought the contract. Stage 3 now proposes it.
2. **Six steps.** A checklist on the thesis and a checklist on the contract, in code and in parallel; the thesis restated as a question, in code; retrieval from the research corpus, by an agent; the critique, by the Critic; then one screen and the record.
3. **Twenty-three fixed checks:** twelve on the thesis, eleven on the contract. Each returns passed, flagged, not applicable or could not be checked. **A check never reports "passed" for want of data.**
4. **The thesis is restated by a fixed template.** The Critic is not shown the original wording and is not told who wrote the thesis.
5. **Retrieval uses the project's research only,** both ways for each claim, at most three passages a side, one retry. No web search.
6. **The Critic has nine tasks,** including the strongest case for, the strongest case against at the same length, a priced-in test on a figure supplied by code, how the trade loses, and what is missing.
7. **The Critic gives no verdict, score, confidence figure or trading advice.** Every objection cites its grounds; every claim gets a disposition; at most five objections; it may concede. Its output is checked in code before the operator sees it, with one retry.
8. **For the demo the Critic runs on the same model family as the Thesis agent,** stated on the screen and in the report. A different family remains the aim.
9. **One screen in two columns:** the Critic's judgement on the left, the fixed-rule checks on the right.
10. **A readiness line, set by code,** tells the operator whether anything the decision relies on has gone out of date. It is not a judgement of the trade and does not block.
11. **The operator reads and decides.** Proceed, return to stage 3, or stop. No typed response is required. The first version advises and never blocks.

## Why

- **Rules before the critic.** Instructing a model to be critical mostly produces the appearance of criticism. Whatever a rule can check is checked by a rule, and the Critic is confined to what rules cannot do.
- **Both sides.** A one-sided challenge moves the reader without informing them. The first draft required only the case for; the operator asked whether the Critic could build a compelling counter-thesis, and it could not. The case against, the priced-in test, the loss paths and the missing-evidence task were added, each tied to recorded evidence so that the counter-case is analysis and not persuasion.
- **No verdict from the Critic.** The system has no demonstrated ability to predict direction; a model's verdict follows surface cues; and on the same model family its agreement is partly the thesis agreeing with itself.
- **Readiness in its place.** The operator asked for go or no-go guidance. Readiness answers a narrower question that fixed rules can answer: are the inputs still valid? Flags are not counted into a rating, because which flags matter is a judgement.
- **Two columns.** The layout itself separates what a rule found from what a model argued.

## What it added to earlier stages

- `evidence[].family`, set in code from the input that produced the finding (thesis check 2).
- `falsifiers[].type`, chosen from a fixed list, so code can tell whether a condition can be watched (thesis check 8).
- `inputs_unavailable[]` with reasons (thesis check 10).
- `evidence[].price_move_since`, the stock's move since each finding became public (the priced-in test).
- **The verdict rule for a supplied thesis,** fixed in code, closing an open item.
- Two files: `config/rejected_signals.json` and `config/instruments.json`.

## What it departs from

- The rule of 15 November 2026 that the Critic runs on a different model family whenever the system drafts the thesis. Kept as the target; the demo is an exception.
- The veto, the structured override and the planted-thesis evaluation in the earlier design. Not built in the first version.

## Provisional values, the designer's choices

- Supporting findings from one family on the same day count as one (thesis check 2).
- Half a usual range, and one trading session, in thesis check 11.
- 1.25 times the usual range in contract check C5, to be replaced by a figure measured from the stored snapshots.

## Open

- Earnings dates and ex-dividend dates have no data source; thesis check 6 and contract check C8 report those parts as "could not be checked".
- The Monitor agent is not designed; thesis check 8 stays flagged until it is.
- The embedding model for the research index, and how evidence grades attach to passages, are build-time choices.

## Operator decisions for the build (19 November 2026)

Ruled one by one before stage 4 was built. Each is an operator decision of 19 November 2026.

| # | Subject | Decision |
|---|---|---|
| 1 | The Critic's one return | The output check runs on the harness, as the Critic's output check, and nowhere else: one return in total, as for the Thesis agent. The graph's `critic_check` node only reports it. A readable answer that fails twice is the "rejected" case (stored, never displayed). An answer that cannot be read twice is an agent failure, with the buttons of product-shell 6.5 |
| 2 | Limits | Critic output cap 4,000 tokens (was 2,500); stage 4 time limit 300 seconds (was 180); the Critic has no tools (was 4 tool calls). In `config/limits.json` |
| 3 | C11, fresh quotes | Stage 4 fetches the option chain once when it starts and compares the selected legs' net mid with the selected candidate's net price. Flagged when the change exceeds the candidate's slippage in dollars. Stage 3's stored chain is not replaced; "Return to contracts" fetches again as before. Market closed, a provisional selection or a failed fetch: could not be checked, never a stage stop. Not re-checked on Proceed. The same fetch gives thesis check 11 its current price |
| 4 | Rejected-signal patterns | Two patterns in `config/rejected_signals.json` are tightened: the day or week pattern must be followed by "average" or an average abbreviation; "61.8" must not sit inside a longer number. The file is shared with stage 2, where the change can only remove false refusals of guidance findings; the operator allowed it with stage 2 frozen. Before the change the patterns matched "over 30 days" in 19 saved thesis texts and "$61.82B" on CVX |
| 5 | A thesis the user entered | Check 1 reads the findings relied on. Checks 2 and 3 count only relied-on findings that carry the thesis's direction, graded moderate or strong. Check 7 adds "severe flag overridden" when the no view was a decline. Check 8 leaves out the "finding with no condition" test. Check 9 is always flagged "entered after no view", with the reason, and also when the verdict is partly or not supported. The verdict is the rule built on 18 November (not, partly or well supported). Every finding relied on, context included, becomes a claim in the question |
| 6 | The event check (thesis check 6) | The window is today to the expiration. Earnings gives a real result, by stage 3's own test (on or before the expiration). FOMC for every instrument. CPI and employment for index instruments; could not be checked where the expiration lies beyond the dates FRED lists. Heavy earnings period: always could not be checked. A dated ruling or vote from the pending-binary-event flag; the dated catalyst from the thesis record |
| 7 | Computed in stage 4, nothing added to stage 2 | The price move since each finding in usual ranges (stage 2 records the percentage); unavailable inputs are listed as stage 2 wrote them, without reason codes |
| 8 | Check 4, contested | "Opposing" means any finding that carries the opposite direction, since sector and macro findings carry none after the decision of 18 November |
| 9 | No supporting finding | Checks 2 and 3 are flagged "no finding carries this direction" |
| 10 | Retrieval | The Evidence Retriever's second configuration words both searches and the one reworded retry for each topic, marks each passage for or against, or drops it. Code checks the passage ids, applies the relevance bar and the cap of three a side. A passage's grade is its report's own "EVIDENCE STRENGTH" label, quoted as written; otherwise "ungraded". If the Retriever fails, the Critic runs with no passages and the screen says so. The whole factor specification is indexed as it is; superseded sections are a known limit |
| 11 | What the Critic is shown | Every check except thesis check 9 (origin and edits), which would tell it who wrote the thesis |
| 12 | Length | Each case at most 90 words; two or three loss paths |
| 13 | C6 | Measured against the cost cap in force on the slider, not the default |
| 14 | Working state | While the agents run the challenge shows stage 2's agents-working panel (Evidence Retriever, Critic, Output check) with Stop |
| 15 | "More detail on request" | One fold in the "N passed" style: each claim's standing, the priced-in reading, what is missing and the passages cited |
| 16 | Counting the checks | The header counts the checks by overall result. A line with a different result inside a check is its own row and is not counted. Not applicable and "passed with a note" sit in the fold with the passes, labelled; the header adds "n not applicable" only when there is one |
| 17 | Not ready, and the end | A stale thesis: text only, "Start a new analysis to redraft the thesis." C11: "Return to contracts". One grey line under the same-model caution when no research passages were retrieved; the retrieval method is recorded and not shown. After "Proceed to decision": the mock-up's end panel without its "END OF THE PROTOTYPE" chip. The readiness sentences are drafted in the build and listed below |
| 18 | Replay and test failures | The first live run of each symbol saves the two agents' outputs and the replay app serves them. `data/replay_mode.txt` gains "critic_reject", "critic_fail" and "nopassages", on the replay app only. `config/test_failures.json` gains `critic_fail_once`, shown as TEST FAILURE ON like the others |

**19. The index is brought up to date when the app starts (operator decision, 19 November 2026, evening).** On the AMZN run retrieval fell back to keyword search because the decision records, which are part of the corpus, had been edited after the index was built; nothing on screen said so. When the app starts it now compares the corpus with the index and rebuilds the index if they differ (about 11 seconds; nothing is done when they match). It never builds while serving a request, so an edit made while the app runs takes effect at the next start. If the build fails the app starts on keyword search, recorded as before.

### As built, for the operator to correct

Choices the build made beside the rulings (19 November 2026). **Accepted in full by the operator on 19 November 2026 (night),** after two rows were corrected: the Critic receives the other recorded findings as context for every thesis, not only one the user entered; and the passage count is that of the first build.

| Subject | As built |
|---|---|
| Relevance bar | chromadb: cosine similarity of 0.45 or more. Keyword search: 0.35 of the query's weighted terms. Set on five test topics: passages on the topic scored about 0.47 to 0.60 and unrelated ones under 0.40. In `config/stage4.json` |
| Passages | 1,406 from 30 files at the first build (1,411 after later edits to the decision records; the count follows the corpus). A claim block of a report (one "CLAIM" to the next) is one passage, kept whole up to 2,600 characters; other text is cut by paragraph at 1,600. 18 of the 19 reports carry "EVIDENCE STRENGTH" labels; the factor specification and the decision records carry none, so their passages are "ungraded" |
| Topics | One per claim (at most five) and one for the strategy type. One tool call searches a topic both ways; a topic may be searched twice, then the tool refuses |
| What the agents see of a passage | The first 700 characters (Retriever) or 1,400 (Critic) |
| Check 1 reads | The written basis and the text of each finding relied on. Not the summary or the rationale |
| Check 2 | Supporting findings with no date are counted separately |
| Check 6 | "Day N" counts calendar days from today. An event dated today counts as inside the window, as in stage 3. The horizon is counted from today, not from the freeze |
| Check 7 | "Could not be checked" only when no analyst finished and the record holds no finding |
| Check 8 | Each condition's type maps to "could be monitored", "in part" or "cannot be monitored". The row names the first place to watch |
| Check 10 | "Max loss raised" is read from stage 3's recorded updates: a later figure above an earlier one |
| Check 11 | The current price is the spot of stage 4's own fetch (15 minutes delayed), against the reference close of the thesis. Market closed: could not be checked. The thesis's age is counted in trading sessions from the freeze |
| Check 12 | The state is measured again from the price history when stage 4 starts; if that fails, the state at the freeze is used and the record says so |
| C1 | The move needed is measured from spot to the breakeven on the view's side |
| C8 | An ex-dividend date equal to today counts as before the expiration (stage 3's test). Seen on MSFT on 19 November, its ex-dividend day |
| C9 | One contract is assumed when no max loss was entered |
| C11 | A leg with no two-sided quote in the fresh fetch: could not be checked |
| No verdict or advice | A fixed list of phrases is refused in the Critic's output (for example "you should", "I would recommend", "worth taking", "7/10", "verdict"). The Critic may quote a percentage it was given. Its numbers are not checked against the record |
| Output check, further rules | A loss path must cite a check or a finding; "what is missing" may cite only recorded unavailable inputs; the claim the thesis depends on must be named; ids must exist |
| The Critic's instructions | It is told to aim for about 72 words a case, because the first live answer was returned for a 92-word case; and to keep ids out of its sentences |
| Readiness, "Not ready" | Also when the user continued with the checklists only (design document, section 3a). Headline: "N blocking condition(s)." |
| Readiness sentences | Ready: "The thesis is from this session and the contract's price has not moved by more than its slippage." C11 not checked: "The thesis is from this session. Whether the contract's price has moved since selection could not be checked: [reason]." |
| Context the Critic receives | For every thesis, the other recorded findings, as context with no direction (at most twelve) |
| After "Proceed to decision" | The end panel and the four read-only stages are held in the page only. The request has ended, so a reload shows Home |
| Stage-stopped screen | The working panel with each agent's final status and the buttons of 6.5. The checklists are kept and shown after "Continue with the checklists only" |
| No download at start | With no embedding model on disk (a fresh clone) the app does not download it when it starts: it starts on keyword search and prints the one command that downloads the model (79 MB) and builds the index. A download from inside the app would reach a host outside the app's network allowlist. **Confirmed by the operator, 19 November 2026: keep as built** |
| Saved outputs for replay | `data/stage4-saved/[SYMBOL].[candidate].json`, written by a live run; git-ignored |

### Seen on the build's runs, for the operator to rule on

1. **The Critic's cost.** One live run on MSFT: Evidence Retriever $0.005 (3 model calls, 4 searches, 11 seconds), Critic $0.226 (2 calls, 47 seconds; about 12,600 tokens read and 3,000 written per call). The Critic's first answer was returned once for a 92-word case against the 90-word limit, which doubled its cost. The build's estimate had been $0.10 to $0.15 for the stage. On the one full run through the real app (AMZN) the Critic passed on its first answer: $0.104, and $0.20 for all four stages.
2. **Active volatility is flagged on most names today** (MSFT 1.39, NVDA 1.34 times the one-year level), so thesis check 12 and contract check C2 fire together on every credit spread.
3. **The replay's saved Critic text quotes the figures of its own run** (for example a credit of $977.50), while the checks beside it are computed on today's quotes. A replay artefact, not a fault.
