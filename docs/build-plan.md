# Tradecraft: demo build plan

**Written:** 18 November 2026 (evening). Replaces `docs/build-plan-draft.md`.
**Status:** **confirmed by the operator, 18 November 2026,** including LangGraph, the run limits in section 4 and the stretch items in section 7.
**Deadline:** Sunday 22 November 2026, night: working system, recorded demo, report, presentation, upload, **and the code in a shareable git repository the evaluators can open** (section 12).
**Time available:** four days, Thursday to Sunday, 8 to 10 hours a day. No application code existed when this plan was written; **progress is recorded in section 6a.**

## 1. What changed since the draft

1. **The screens are settled.** The build matches `docs/site/tradecraft-prototype.html`, specified in `docs/product-shell.md`.
2. **The harness is built first.** The course asks that every agent has guardrails and a harness and that agents are reusable. One shared harness is built on day one; each agent is a configuration on top of it.
3. **Guardrails are made visible.** Four additions to the agent architecture (section 2a there), one table of guardrails by agent (section 5 here), and tests that show a guardrail firing.
4. **The schedule moved a day.** The draft had data tools being built on Wednesday.
5. **The capstone brief was re-read against the plan** (section 9). It names no framework, but asks for the course's tools and concepts, so **LangGraph runs the workflow**. It asks for a ReAct-style loop that recovers from missteps, for further reasoning such as Tree of Thought with the thought process shown, and for a written statement of unintended actions. Sections 4a and 11 answer those.
6. **Run limits were three numbers; they are now a table** (section 4).

## 2. Scope

On-demand mode, one underlying per request, stages 1 to 4, in the browser.

| In the demo | Left out, described in the report as designed next |
|---|---|
| Home with symbol search | Welcome screen or login; Records and Settings pages |
| Stage 1: liquidity gate, with adjustable criteria | "View option chain" |
| Stage 2: measured figures, five agents, validation check, research brief | Supplying your own thesis (step 2B), unless Saturday ends early |
| Stage 3: candidates, measures, filters, ranking, max loss (code, no agents) | Event-volatility work; value at the horizon |
| Stage 4: the two checklists, restated question, retrieval over the research corpus, the Critic, readiness line | The Critic's power to block; a second model family; the 120-thesis evaluation |
| Decision records written as the run proceeds | Stages 5 and 6; the Monitor |
| A trace of every agent step | The Eval Judge agent |

## 3. Technical choices (defaults; the build session may change one with a stated reason)

| Area | Choice | Why |
|---|---|---|
| Language | Python 3.11 or later | Existing scripts are Python |
| Workflow | **LangGraph.** One graph: stages as nodes; the three analysts as parallel nodes merged by the Thesis node; conditional edges for the validation retry, no view, Stop and "return to contracts" | The course teaches it, the brief asks for the course's tools, and it yields a workflow diagram for the report. Use the current LangGraph documentation, not memory, for its interface |
| Agents | **Our own harness with the Claude SDK, called inside each LangGraph node** | Tool allowlists, validation, limits and the trace stay under our control whatever the framework does |
| Models | `config/models.json`: Haiku for the Retriever and the three analysts, Opus for the Thesis agent and the Critic | Decided 18 November |
| Output formats | Pydantic models, one per agent | Validation and rejection come for free |
| Web | FastAPI serving the pages and a small JSON API on localhost | Light, and enough for a browser-first build |
| Front end | The mock-up's HTML, CSS and JavaScript, with the hard-coded data replaced by API calls. No build step | The mock-up is the approved design |
| Storage | SQLite: evidence store, decision records, traces | One file, no server |
| Research index | A local open-source embedding model and a local vector store (Chroma; plain arrays if installation is troublesome) | No extra key or cost |
| Secrets | `.env`, never printed or logged | Standing rule |

## 4. The harness (built first)

One function runs any agent from a configuration: instructions, model, allowed tools, output format, retrieval scope, limits.

| Part | What it does |
|---|---|
| Tool registry and allowlist | An agent can call only the tools its configuration names |
| The loop | Calls the model, runs requested tools, returns results, repeats until an answer or a limit |
| Output validation | Parses the answer into the agent's format; on failure returns it once with the error, then fails cleanly |
| Guardrail hooks | Checks before a call (inputs) and after it (outputs), listed in section 5 |
| Untrusted content | Text fetched from filings, data providers or the corpus is wrapped and labelled as data; instructions inside it are never followed |
| Run limits | The table below. Every value is a setting in configuration |
| Recovery | A failed source falls back (option quotes: Cboe, then Tradier, then the snapshot, by operator decision of 20 November 2026; missing input to "not available"); a failed agent stops the stage with a plain message |
| Trace | Every model call, tool call, validation result and guardrail result, stored and viewable. Each run also records a fingerprint of the agent's configuration (instructions, output format, checks, tools, model), so every output can be traced to the prompt version that produced it |

**Run limits (starting values, not measurements; adjust after the first real runs).**

| Limit | Value | On reaching it |
|---|---|---|
| Tool calls per agent run | Retriever 12; Fundamental Analyst 8; Regime Assessor 6; Technical Analyst 2; Thesis agent 0 (it reads findings only); Critic 4 | The agent must answer with what it has |
| Time per agent run | 90 seconds on Haiku agents; 180 seconds on the Thesis agent and the Critic | The run ends; the stage reports which agent timed out. Model calls, their retries and tool fetches all get only the time left, so a stuck source cannot hold a run past its limit |
| Time per stage | Stage 2: 5 minutes. Stage 4: 3 minutes | The stage stops with a plain message; partial results are kept |
| Output per model call | 1,500 tokens for the analysts and the Retriever; 2,500 for the Thesis agent and the Critic. **Operator decision, 18 November 2026:** thinking counts against these caps, so the build session may raise one after seeing a reply cut off, up to 4,000 for the Haiku agents and 8,000 for the Thesis agent, recording each change in `config/limits.json` and reporting it | The reply is cut off and fails validation, which triggers the one retry |
| Text handed to a model from one document | 15,000 tokens. Filings are read by section, never whole | The tool returns the section list and the agent chooses |
| Size of one tool result | 8,000 tokens | Truncated, with a note saying so |
| Text sent to the model in one call (added 18 November 2026 after the harness review) | 60,000 tokens, under Haiku 5.5's 100,000-token price step | The new tool results are shortened to fit and the agent must answer with what it has; a task already over the limit is not started |
| Validation retry | One, with the error returned to the agent. **One in total for the Thesis agent (operator decision, 18 November 2026):** a cut-off or badly formatted reply uses it, and a manual "Retry" after a stage stop is a fresh run | The user sees the draft with the failed checks (stage 2) or the checklists alone (stage 4) |
| API errors and rate limits | Two retries with an increasing pause, done by the harness inside the agent's time limit (the SDK's own retries are off, since each would get the full timeout again) | The stage stops with a plain message |
| Tool errors | One retry, then the fallback or "not available" | Recorded as an unavailable input |
| Repeated identical tool call | Refused the second time | The agent is told it already has that result |
| Spend | $1 a request and $10 a day, counted from token usage; the $50 account limit sits behind both | The request stops before the next model call |
| Outside services | At most 5 requests a second to the SEC; the free data key's daily cap is looked up and recorded on day one. Tradier, added 20 November 2026: 100 requests a minute | Requests wait; nothing is dropped silently |
| Cache | Filings, price history and provider responses are cached per symbol per day | A repeated run does not refetch |
| Reach of tools | Network: the data sources' domains only. Files: the application's data folder only | Refused and traced |
| Concurrency | **One open request at a time** (running or waiting at a pause; clarified 18 November 2026). Stop on screen cancels the running agents. Leaving, reloading, a second tab and an engine restart are specified in `docs/product-shell.md`, section 2 | A second request is refused and the open one is shown |

**Whenever a limit is reached** the run stops cleanly, what was completed is kept, the screen says what happened in plain words, and a decision record is written.

**Reuse shown in the demo.** The Evidence Retriever runs in stage 2 (company evidence) and stage 4 (research corpus) from two configurations of one agent. The three analysts are one class with three configurations. If step 2B is built, the Thesis agent and the Fundamental Analyst each take a second role.

## 4a. Reasoning the agents must visibly do

The brief grades the reasoning loop and "further reasoning", so these are requirements on the build, not style.

| Agent | Pattern | What it must do | What the demo shows |
|---|---|---|---|
| Evidence Retriever | **ReAct** (reason, act, observe, repeat) | Decide which sources to query for this underlying, call the tools, read the results and decide what to fetch next: list the filings, choose the sections, get the dates and estimates | The trace of its steps, including **one recovery**: a source refuses or returns nothing and the agent falls back or records the input as unavailable |
| Fundamental Analyst | ReAct | Read stored evidence, fetch a further filing section where a finding needs it, and stop when it has what it needs | The trace |
| Regime Assessor, Technical Analyst | Single pass | Interpret figures computed in code | The trace |
| Thesis agent | **Tree of Thought, one pass** | Set out three branches (bullish, bearish, no view). For each: the findings for it, the findings against it, and whether it meets the precedence rules. Prune the branches that fail, with the reason, and select what remains. Conflicting lead evidence selects no view | A "reasoning" view on the thesis screen's detail and in the trace, drawn as the three branches with the pruned ones marked |
| Critic | Single pass over nine tasks | As designed | The trace |

Limits on the Tree of Thought, from the existing design: it is one structured pass, not a debate and not self-critique; the agent is not asked again for a different answer; code re-checks the precedence test on the selected branch; no branch carries a probability or a score. Record: `thesis.branches[{view, supporting[], opposing[], meets_precedence, pruned_reason}]`. The reasoning view is an addition to the approved thesis screen, placed in its expandable detail.

**Memory, made visible:** when a symbol has been analysed before, Home and the thesis screen say so and link the earlier decision records.

## 5. Guardrails by agent

| Agent | Guardrail | Enforced by |
|---|---|---|
| All | Only allowlisted tools; run limits; untrusted content labelled; output must match its format; every step traced | Harness |
| All | No tool places an order or writes a setting | No such tool exists |
| Input (before any agent) | The symbol comes from the directory; one underlying per request | Code |
| Evidence Retriever | Returns evidence with source and date; draws no conclusion; grades are set in code | Format, code |
| Fundamental Analyst | Findings with a stated bearing; forms no view; raises only flags on the defined list | Format, code check |
| Regime Assessor | Sector and macro findings; cannot start a view on a single stock | Code (precedence rule) |
| Technical Analyst | Description only; computes no level; never receives option data | Tools withheld, format |
| Thesis agent | States no probability and sets no figure; never sees option prices or implied volatility; may return no view; every claim cites stored evidence; no price-derived support for a direction; invalidation is evidence-based | Tools withheld, validation check with one retry |
| Critic | Sees the restated question, not the original wording or the author; every objection cites its grounds; a disposition for every claim; at most five objections; no verdict, score or advice | Template in code, output check with one retry |
| Stage 3 | No agent at all: contracts are chosen by fixed rules | Design |
| Whole system | "No demonstrated predictive edge" on every thesis; "best fit", never "recommended"; rejected-signal list; the readiness line is set by code | Code |

**Guardrail tests for the demo (three, scripted):** a thesis draft that states a probability is rejected and returned; a filing excerpt containing an instruction is ignored; an agent that requests a tool outside its allowlist is refused.

## 6. Schedule

| Day | Work | Done when |
|---|---|---|
| **Wednesday evening** | The five items in section 8 | The local session is open on a clean repository |
| **Thursday** | Project skeleton, web server, storage. **The harness with its run limits, and the three guardrail tests.** The LangGraph workflow as a skeleton with stub nodes. Data tools with caching and rate limits: filings by section, earnings and dividend dates, consensus, macro calendar, price history, option chain (reusing `scripts/daily/chain_census.py`), symbol directory. Home with symbol search. Stage 1 with adjustable criteria | The harness passes its tests and the gate returns real results for a real symbol. The stage 1 screen may finish on Friday morning |
| **Friday** | Measured figures in code (reusing `scripts/analysis/label_frequency.py`): base rate, typical realized move, volatility state, recommended horizon. Evidence store and grades. Retriever and three analysts in parallel. Thesis agent with its three branches, summary, rationale and horizon reasons. Validation check. Thesis screen with the agents-working panel. Freeze. Decision records | Stages 1 and 2 run end to end on two demo symbols |
| **Saturday** | Morning: stage 3 (candidates, measures, filters, ranking, max loss, screen). Afternoon: research index; the two checklists; restated question; retrieval; Critic and its output check; readiness line; challenge screen | All four stages run end to end on one symbol |
| **Sunday** | Morning: full runs on every demo symbol, fixes, trace view, dark theme check. **Noon: code freeze.** Afternoon: the safety statement (section 11), record the demo, report, presentation, upload. **Last action: publish the repository for the evaluators (section 12) and put its link in the report and the presentation** | Uploaded, and the repository link opens from a browser that is not signed in as the operator (or as an invited evaluator, if private) |

## 6a. Progress

| Row | Status | Notes |
|---|---|---|
| Wednesday evening (section 8) | **Done, 18 November** | All five items; demo symbols and rate limits recorded in section 8 |
| Thursday | **Done, 18 November (a day early)** | Harness with run limits and the three guardrail tests; LangGraph workflow with stub steps; data tools (FMP, SEC filings by section, macro calendar, price history, option chain, symbol directory); web server; Home with symbol search; stage 1 on screen with real results from the 18 November snapshot. 122 tests pass. Branch `build/demo` |
| Friday | **Done, 19 November** | Built and tested: measured figures, horizon and range-bound rules, evidence store and grades, the five agents, the validation check, stage 2's workflow steps; run live step by step on six symbols. Stage 2 was revised the same night (`docs/decisions/2026-11-18-stage-2-anchored-bearings.md`). Stage 2 was wired into the app on 19 November (background run, agent status, Stop, "Take a view yourself") and run live through it; the six-symbol re-run under the revised rules was made once. The stage 2 screens were built on 19 November and checked live on TGT, MSFT and NVDA, including the freeze. **Row complete,** apart from two results with no design (range-bound; a draft that fails validation twice), which show one plain line. The four faults the 43-symbol run showed were fixed on the operator's rulings of 19 November, and C, PEP and T were then run once. Detail in `docs/build-log.md`. Every guidance bearing was then moved into code by operator decision (not yet run on a live model). 280 tests pass |
| Saturday | **Done, 19 November.** Stage 3 and stage 4 built; all four stages ran live end to end through the real app on AMZN ($0.20) | Stage 3 built on the operator's 22 rulings of 19 November: engine, workflow step, screen. Run live once each on MSFT, AMZN, NVDA, TGT and SPY ($0.37). **Saturday check made:** at the 5% cap, 35 of 72 candidates across 33 saved views are over it, and MSFT and AMZN each lose one; the operator had the on-screen cost-cap control built the same day (311 tests pass). Detail in `docs/build-log.md` |
| Sunday | Not started | |

**Still to verify from Thursday's row:** stage 1's fail, adjust-criteria and override states on live data. A live pass was seen on screen on 19 November (MSFT, 33 passing contracts); it showed a fault in the contract counts, fixed the same day.

**Changes to this plan made during the build,** each by operator decision on 18 November 2026: the FMP premium plan's company news and wider coverage (section 10); a limit on text sent to the model in one call, and retries and tool fetches held inside the agent's time limit (section 4); "one open request at a time" (section 4); the Saturday check on cost filtering (section 7); data-release dates from FRED in the macro calendar.

## 7. Cut lines

This is four stages in three build days. The cuts are decided now so that they are not argued on the day.

| When | If | Then |
|---|---|---|
| Thursday night | Stage 1 is not on a real screen | Friday starts with it; stage 2 screens use plainer markup until Saturday |
| **Friday night** | Stages 1 and 2 are not end to end | Saturday builds stage 3 only, and stage 4 as the two checklists and readiness line without the Critic |
| Saturday 3 pm | Stage 3 is not finished | Stage 4 is the two checklists only; the Critic is described in the report |
| Saturday night | The research index is not working | The Critic runs on the checklists and the thesis record alone; the screen says no research passages were retrieved |
| Sunday noon | Anything is unfinished | It is left out and the report says so |
| Sunday 6 pm | The repository is not yet published | Publishing takes priority over further polish of the report; the checks in section 12 are not skipped to save time |

Order of checklist work if time is short: the checks whose data exists first (thesis checks 1 to 5, 8, 9, 11, 12; contract checks C1, C3, C6, C7, C9, C10). The rest return "could not be checked", which the design allows.

**Saturday check (operator, 18 November 2026):** once stage 3 runs on the demo symbols, look at how often candidates are filtered out for cost. If it happens on the symbols to be recorded, the on-screen cost-cap control is worth the hour; if it never happens, leave it out. Raise the result with the operator.

**Stretch, only if Saturday ends early:** step 2B (supply your own thesis); a small evaluation of ten planted theses through the checklists and the Critic.

## 8. Before the build starts

1. Commit the documentation changes of 18 November.
2. Add `SEC_USER_AGENT` to `.env` (the operator does this; it contains a contact email and must never appear in a command, a file or a commit).
3. Set the $50 spend limit on the API account.
4. Choose three or four demo symbols from the 49 covered names in `config/data_sources.json`. **Chosen 18 November 2026 by the operator:** **NVDA, AMZN and SPY** run through all four stages; **ADBE** shows stage 1 only (FAIL at the default 42 to 90 DTE, then "Adjust criteria" and the override path). Basis, from the 18 November 11:00 snapshot at stage 1 defaults (plain-percentage strike distance) and FMP earnings dates: NVDA 24 passing contracts, median spread 1.9%, reported 17 November (beat), next report 24 February; AMZN 17 passing, 2.6%, reported 29 October (missed), next 4 February; SPY 399 passing, 0.8%; ADBE 0 passing at 42 to 90 DTE, 12 at 22 to 41. WMT avoided: it reports 19 November. One day's figures; live counts at the recorded demo will differ. ADBE's next earnings date is to be checked before it is relied on.
5. Look up the API account's rate limits. Three analysts run in parallel and a new account may be throttled; the harness retries, but the stage 2 time limit may need raising. **Looked up 18 November 2026:** 4,000 requests, 2,000,000 input tokens and 400,000 output tokens a minute for each of Opus 5.5, Sonnet 5.5 and Haiku 5.5 (`config/models.json`). Far above the demo's needs: the analysts run in parallel and the stage 2 limit stays at 5 minutes.

## 9. What the capstone grades, and where the demo shows it

| Requirement | Shown by |
|---|---|
| Tool calling | Agents fetch filings, dates, estimates, prices and the option chain through allowlisted tools |
| Reasoning loop with recovery (ReAct) | The Retriever's and Fundamental Analyst's reason, act, observe loops in the trace; a source failing over to a fallback; a draft failing validation and being returned once |
| Knowledge and memory | Retrieval over the research corpus in stage 4; the evidence store; decision records |
| Further reasoning (Tree of Thought) | The Thesis agent's three branches, tested against the precedence rules and pruned, shown in the reasoning view; the Critic's nine tasks |
| Multi-agent coordination | The LangGraph workflow: three specialised analysts in parallel merged by the Thesis agent; the Critic challenging a thesis it did not write |
| Safety | The statement of unintended actions and mitigations (section 11); the guardrails in section 5; the run limits; the three guardrail tests; no order execution |
| Reuse | One harness; the Retriever in two stages; the analysts as one class |

## 10. Standing rules for the build session

- Read `CLAUDE.md` first. Match the mock-up. Do not invent the parts marked "not designed".
- Never print or log anything from `.env`.
- Do not modify, re-run or vary the frozen tests in `scripts/tests/`, and do not edit `vrp_out/TRIALS.log`.
- Do not change the daily snapshot job or rename the repository folder.
- No new measurements and no design changes this week. A gap in the design is raised with the operator, not filled silently.
- Data sources: free sources plus the FMP premium plan's company news and wider coverage (amended 18 November 2026, evening; `config/data_sources.json`, `docs/decisions/2026-11-18-data-sources.md`). Where an input is missing, show "not available" or "could not be checked".

## 11. Safety statement (a report deliverable)

The brief asks for a "statement of potential unintended actions the system may execute and the steps taken to address this". The report carries this table, checked against the built system on Sunday.

| Unintended action | Steps taken |
|---|---|
| Placing or changing an order | No tool can place an order, and no agent has a tool that reaches a broker. The system outputs candidates; the user places orders. **Amended 20 November 2026:** the option-chain code (not an agent) now reads market data from Tradier, which is a broker, with the operator's token. It calls three market-data addresses (price, expirations, chain) and nothing else; no order or account address appears in the code. This rests on what the code calls: the network allowlist is by host, so it does not by itself separate Tradier's market data from its order addresses |
| Following instructions hidden in a filing or a web page | Retrieved text is labelled as data; tools are allowlisted, so an injected instruction has nothing to call. Tested |
| Running in a loop and spending without limit | Tool-call, time and spend limits per agent, stage, request and day; repeated calls refused |
| Presenting a guess as a fact or a figure | No agent sets a figure; every claim cites stored evidence; validation rejects a draft that does not. Tested |
| Presenting research as advice | No probability for a view; "no demonstrated predictive edge"; "best fit", never "recommended"; the Critic gives no verdict |
| Agreeing with the user or with itself | The thesis is restated as a question; balanced retrieval; fixed checklists before the Critic; same-model caution on screen |
| Using a signal already shown not to work | The rejected-signal list, checked in code |
| Acting on stale prices or a stale thesis | The readiness line; "could not be checked" is never shown as passed |
| Overloading a data source or breaking its terms | Rate limits, caching, a declared contact for the SEC |
| Leaking a key or personal detail | Secrets only in `.env`, never printed, logged or committed. The Tradier token (added 20 November 2026) belongs to a brokerage account: it is sent as a request header to Tradier's market-data address only, never to a host a redirect leads to, and no tool can reach an order or account address |
| Reaching beyond its job on the computer | Network and file allowlists; no shell tool; no agent can change a setting or the daily snapshot job |
| Failing silently | Every step traced; every limit reached and every unavailable input is shown and recorded |

## 12. Publishing the repository for the evaluators (Sunday, last action)

**Requirement (operator, 18 November 2026):** everything is uploaded to a shareable git repository that the evaluators can access.

**Decide by Saturday night:** public, or private with the evaluators invited. Private needs each evaluator's account name in advance; public needs none. Until now the repository has only existed on the Mac mini, so everything in it and in its history must be checked before it leaves.

**Checks before the first push. Each is a stop, not a warning.**

| Check | Why | How |
|---|---|---|
| No secret in any commit | `.env` is ignored, but a key committed once stays in history | Search the full history for the key names and for `.env`; if anything is found, do not push that history |
| The commit author's email | **Every commit carries the operator's email, and the operator keeps it private.** Publishing the history publishes it | Either publish a fresh copy with a single commit under the hosting service's private "no-reply" address, or keep the repository private. Do not push the existing history to a public repository |
| `SEC_USER_AGENT` | It contains the contact email | Confirm it exists only in `.env` and `.env.example` shows an empty placeholder |
| Licensed and third-party data | WRDS data is academic-use only and must not be published. The daily option snapshots, provider responses and cached filings came from third parties | Exclude WRDS-derived files, caches and provider responses. Decide whether the snapshot archive is included at all; the default is to leave it out and say so in the README |
| Personal paths and machine names | Documents and the scheduled job mention the home folder and the computer's name | Acceptable in a private repository; for a public one, review `ops/` and `CLAUDE.md` |
| Size | Price caches and snapshot archives are large | Confirm they are ignored |

**What the evaluators need to find.**

- A `README.md` at the top: what Tradecraft is, the six graded concepts and where each is in the code, how to install and run it, which keys are needed (`.env.example`), and what is left out.
- The design documents, the build plan, the safety statement and the mock-up.
- The recorded demo, or a link to it.
- A statement that the system places no orders and gives no investment advice.

**Then:** push, open the link from a browser that is not signed in as the operator (or as an invited evaluator), confirm it loads and the README renders, and put the link in the report and the presentation. The build session prepares the copy and runs the checks; **the operator creates the remote repository and does the push.**
