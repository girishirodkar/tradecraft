# Tradecraft (formerly Options Contract Explorer)

> **Product name: Tradecraft** (operator decision, 18 November 2026). It covers
> options now and stock strategies later; modules can be named "Tradecraft
> Options", "Tradecraft Stocks". Use it in the application's title, window and
> screens, and in the report. **Do not rename the repository folder:** it stays
> `~/options-explorer`, because the scheduled job depends on that path. The
> course's weekly submissions keep the earlier title.

> **SCREENS: BUILD THEM TO MATCH THE MOCK-UP (operator decision, 18 November 2026).**
> `docs/site/tradecraft-prototype.html` is a clickable mock-up the operator
> reviewed and approved. `docs/product-shell.md` is its written specification.
> - **Layout, wording, colours and behaviour must match the mock-up.** Start the
>   front end from its markup and styles and replace the hard-coded data.
> - **Navigation:** a stage bar, one stage on screen at a time; completed stages
>   reopen read-only.
> - **Screens use trading terms** (bid-ask spread, DTE, spot, premium, breakeven,
>   POP, slippage, bull case and bear case). The design documents keep plainer
>   wording; the mapping is in `docs/product-shell.md`, section 3. The first-ranked
>   candidate is "best fit", never "recommended".
> - **The Thesis agent now also returns** `summary`, `rationale {catalyst,
>   confirmation, tempering}` and `horizon_reasons[]`; the validation check tests
>   them against the findings in the record.
> - **Not designed, do not invent:** welcome screen or login, the Records and
>   Settings pages, stage 5 and 6 screens. Show them disabled or leave them out.

> **BUILD STATUS (updated Thursday 19 November 2026, night PT). Read this before
> doing anything; update it at the end of every working session.**
> **`docs/build-log.md` has the detail: what is built, what is next, every decision of
> the session, and the questions waiting for the operator. Read it next.**
>
> **Where the build is.** The plan's "Thursday", "Friday" and "Saturday" rows are built:
> stages 1 to 3 run live end to end on their own screens, and **stage 4 (the challenge) was
> built on 19 November.** Stage 4 is tested, was checked on the replay app, and **ran live
> once through the real app, all four stages, on AMZN ($0.20; after the close, so on the
> snapshot).** Application code is in
> `tradecraft/`, tests in `tests/` (373 pass), on the branch **`build/demo`**. `master`
> is the approved design, untouched. Progress by day is in `docs/build-plan.md`, section
> 6a. Commit locally at each working milestone; **never push** (the operator publishes on
> Sunday, plan section 12).
>
> **STAGE 2'S RULES ARE FROZEN (operator decision, 19 November 2026).** The freeze covers
> what earns a bearing, the event list, what starts a view, the conflict rule, the grades
> and the recent test, and the four fault fixes and the guidance ruling of 19 November.
> Anything a run shows about stage 2 goes on the "After the demo" list in
> `docs/build-log.md` and is not changed, unless it stops a run from finishing or makes a
> screen show something false. If you think something meets that bar, **stop and ask
> before changing it.** Recorded at the top of
> `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`.
>
> **Stage 2 was revised on 18 November (night):
> `docs/decisions/2026-11-18-stage-2-anchored-bearings.md`.** A finding carries a bearing
> only as results against estimates (built in code), a guidance change quoting both
> figures, or a new event on a fixed list; everything else is context. Three outcomes: a
> view, no view because findings conflict, no view because nothing carries a direction.
> After a no view the user may "Take a view yourself". Section 7 of that decision is the
> work list; items 1 to 5 and 7 are built.
>
> **The six-symbol re-run (item 8) was made once on 19 November:** NVDA and WMT no view
> (conflict); TGT bullish; MSFT bullish, AMZN and JPM bearish, all three weakly supported.
> **Nothing in stage 2's rules is adjusted on a run's results without an operator
> ruling.** The operator ruled on seven things seen in this run and on four faults seen in
> the 43-symbol run; the rulings are in `docs/build-log.md`. Do not re-run the six.
>
> **How to run.**
> - Tests: `.venv/bin/python -m pytest -q`
> - The app: `.venv/bin/python -m uvicorn tradecraft.web.app:app --host 127.0.0.1 --port 8321`
>   (or the `tradecraft` entry in `.claude/launch.json`), then http://localhost:8321
> - Packages: `UV_CACHE_DIR="$PWD/.uv-cache" ~/.local/bin/uv add <name>`. The app runs on
>   `.venv` (Python 3.12); the daily snapshot job keeps the system Python 3.9.
> - Live model checks: `TRADECRAFT_LIVE=1 .venv/bin/python -m pytest -q tests/test_live.py -s`.
>   **These must run outside the sandbox:** inside it the Anthropic SDK fails TLS
>   verification. That is a sandbox artefact, not a bug. A full stage 2 run costs about
>   $0.06; tell the operator the cost of each live run.
>
> **What is real.**
> - `tradecraft/harness/`: `run_agent` runs any agent from an `AgentConfig`. Run
>   limits in `config/limits.json`, prices in `config/models.json`.
> - `tradecraft/workflow/`: the LangGraph graph for stages 1 to 4 (`graph.py`).
>   Diagram: `docs/workflow-diagram.md` (generated; do not edit).
> - `tradecraft/storage.py`: SQLite in `data/` (git-ignored): decision records, the
>   evidence store, traces, spend, cache.
> - Stage 1 end to end, on screen.
> - Stage 2 engine: `figures.py` (measured figures), `horizon.py` (horizon and
>   range-bound rules), `context.py` (numbers for the analysts), `evidence.py` (evidence
>   store and grades), `agents.py` (five `AgentConfig`s), `validation.py` (the validation
>   check, the precedence rules, the verdict for a user thesis), `stage2.py` (the
>   workflow steps, `STEPS`).
> - `tradecraft/tools.py`: nine data tools; each result is stored as evidence and
>   returned with evidence ids.
>
> **Stage 3 (built 19 November).** `tradecraft/stage3.py`: the engine and the workflow
> step; settings in `config/stage3.json`. The operator's 22 rulings, and the choices the
> build made beside them ("As built, for the operator to correct"), are in
> `docs/decisions/2026-11-17-stage-3-contract-selection.md`. Legs leave out the DTE
> criterion; **there is no override in stage 3**; events are shown, not filtered; the
> first-ranked candidate is `best_fit_id`. **The cost cap is an on-screen slider** (2% to
> 10%, default 5%; operator decision, 19 November, after 35 of 72 candidates across 33
> saved views were over the cap). **Ruled on 19 November (afternoon):** an expiration may serve a horizon from up to three
> sessions before the horizon date; the legs of a spread or condor are not held to the
> bid-ask criterion one by one (the cost cap judges the structure; a single option keeps
> it); a single option's row states its distance from spot; filtered-out rows carry a
> FILTERED label. Re-run on the six tested symbols: 3 built, 3 kept, none over the cap,
> each; see `docs/build-log.md`.
>
> **Stage 4 (built 19 November).** `tradecraft/stage4.py`: both checklists (12 and 11
> checks), the question, retrieval, the Critic and its output check, readiness; settings in
> `config/stage4.json`. `tradecraft/research.py`: the research index (chromadb with its
> local default model; keyword search over the same passages as the fallback; the method is
> recorded in every challenge). The operator's 19 rulings and the build's own choices ("As
> built", **accepted in full on 19 November**) are in `docs/decisions/2026-11-17-stage-4-challenge.md`.
> **The Critic's output check runs on the harness and nowhere else** (one return in total);
> the graph's `critic_check` node only reports it. Thesis check 9 is withheld from the
> Critic. C11 uses stage 4's own fetch of the chain. **After the corpus changes, rebuild the
> index:** `.venv/bin/python -m tradecraft.research build` (the index and the model live
> under `data/`, git-ignored; a fresh clone must build it, or stage 4 uses keyword search).
> The Critic costs about $0.11 a call, double when its answer is returned once. **The app
> rebuilds the index when it starts if a corpus file (`docs/research/`, `docs/decisions/`,
> `docs/factor-spec.md`) has changed; an edit made while it runs takes effect at the next
> start. It does not download the embedding model: on a fresh clone run the build command
> once, or stage 4 uses keyword search.**
>
> **Developer-only test failures.** `config/test_failures.json` holds three switches, all
> false by default: `option_chain_fail_once` (stage 3's Retry),
> `stage2_source_fail_once` (the Retriever's one recovery, on `list_filings`) and
> `critic_fail_once` (stage 4's Retry). Each fires
> once per request and is read on every use. While any is true every page shows
> TEST FAILURE ON in its header, and a test fails. **Leave all false** except while
> showing a recovery; `docs/build-log.md` says what each was seen to do.
>
> **Recorded demo for evaluators (operator decision, 19 November).** `tradecraft/demo.py`
> (`tradecraft.demo:app`, port 8324) runs all four stages with no keys and no network from
> `data/demo-bundle/` (3.1 MB: AMZN, MSFT, NVDA; to be published as its own public
> repository). Instructions: `docs/recorded-demo.md`. Rebuild with
> `python -m tradecraft.demo export|record|scan`; **run `scan` before every push of the
> bundle.** `README.md` is the evaluators' README (two link placeholders to fill).
> **`python -m tradecraft.publish`** writes the clean, no-history copy to
> `data/publish/tradecraft/` and runs section 12's checks; re-run it after any commit. The
> operator creates the remotes, commits under a no-reply address and pushes.
>
> **The product manual** (19 November; part 1 added 20 November) is four pages with one
> shared header: `docs/site/manual.html` (what Tradecraft is), `manual-logic.html` (the
> logic of each stage), `manual-architecture.html` (four levels, written from the code as
> built) and `manual-stages.html` (the four stage pages shown in full). The header is
> repeated in the four files: change it in all four. When the code
> changes, check the manual's tables (agents and limits, module map, state keys) against it.
>
> **Videos (19 November, night; all under `data/video/`, git-ignored).** The pitch
> (`pitch/tradecraft-pitch.mp4`, 1 min 22 s; a copy is tracked at `docs/media/tradecraft-pitch.mp4` and linked from the README: copy it again after a rebuild) and the
> demo are narrated by the macOS voice Nathan (Enhanced); `imageio-ffmpeg` is a development
> dependency for this. **`data/video/demo/make_demo_motion.py dry|live`** records the demo
> as live screen action in headless Chrome and writes the narrated video, a silent copy and
> `transcript.md`; `make_demo.py` is the still-frame fallback. `live` uses its own database
> (`data/demo-recording.sqlite3`), costs about $1, and turns two developer switches on for a
> few seconds each, restoring `config/test_failures.json` exactly: check that file after any
> run. It was run live once (after hours: 18 of 19 passages, $0.75). **Two one-off scheduled
> tasks run it on 20 November, 07:30 PT (rehearsal) and 10:00 PT (the take).** The operator
> records the presentation separately; 10 minutes in total. Detail in `docs/build-log.md`.
>
> **Development-only replay.** `tradecraft/dev_replay.py` (the `tradecraft-replay` entry
> in `.claude/launch.json`) serves the stage 2 outputs saved on 19 November, makes no
> model call and writes to `data/replay.sqlite3`. Use it to check stage 3 and 4 screens.
> In stage 4 the code runs for real and the two agents are served from
> `data/stage4-saved/[SYMBOL].[candidate].json`, which the first live run of that pair
> writes (MSFT with the bull put spread is saved); without one the challenge shows its
> stage-stopped screen. `data/replay_mode.txt` also takes "critic_fail", "critic_reject"
> and "nopassages". A build tool by operator decision, not a product feature.
>
> **What is a stub.** Nothing in stages 1 to 4: all are real (`steps.real_steps()`).
> `tradecraft/workflow/stubs.py` remains for the wiring tests. Stage 5 is not designed;
> after "Proceed to decision" the app shows one plain panel.
> **Tests must not call `real_steps()` past the gate** (stage 2 would call live models);
> see `steps()` in `tests/test_web.py`. A long stage runs in the background: actions
> return `running: true` and the page polls `/api/requests/open`; `Workflow.progress`
> gives each agent's status from the trace. `tradecraft/web/static/tradecraft.css` is the
> mock-up's stylesheet copied whole: change the mock-up first, then copy.
>
> **The 43-symbol run (item 9) was made once on 19 November:** 27 views, 13 no views, 3
> that did not finish. It showed four faults. **The operator ruled on them the same morning
> and all four are fixed**: the event-kind check is the Fundamental
> Analyst's alone; "support" and "resistance" match only as chart terms and a defined event
> is never refused as a rejected signal; guidance against consensus is set in code (a range
> containing consensus is in line); a price condition needs a price beside "above" or
> "below". Recomputed in code, nine of the 49 saved runs change outcome (table in
> `docs/build-log.md`); they were not re-run. C, PEP and T were run once and finished.
> **Every guidance bearing is now set in code (operator decision, 19 November):** the
> analyst extracts measure, period, basis and figures and classifies nothing; only EPS,
> revenue and operating income or margin can carry a bearing. No bearing rests on a model's
> reading of wording. 280 tests pass; the new analyst format was checked live on PEP only
> (no view, conflict; guidance against consensus not yet seen live). Recomputed in code, 15 of the 49 change outcome and 30 of 34 views rest on
> the earnings result alone (`docs/build-log.md`). Do not re-run the 43 or the six.
>
> **Screen changes of 19 November (operator decisions, in the mock-up and `docs/product-shell.md`
> 6.2):** the brief's evidence is three cards (context and backdrop fold, with counts); on a
> no view "What you can do" sits in the view card and the evidence takes the full width;
> "Flags and missing inputs" folds. **The browser caches `app.js` and the stylesheet:** hard
> refresh after changing them, or a check shows the old page.
>
> **The saved outputs of the 49 runs and the recompute scripts** are in
> `data/runs-2026-11-19/` (git-ignored). The build log's tables come from them.
>
> **Demo shortlist (operator, 19 November):** TGT, CSCO, PYPL, AMZN, GOOGL, MSFT, NVDA, SPY;
> final choice on the day; SPY and AMZN stay. Gate and stage 3 figures for each are in
> `docs/build-log.md` (CSCO is fragile; NVDA, SPY and probably PYPL need a user thesis).
> The stage 3 as-built table is accepted in full.
>
> **Next, in the operator's order:** the Sunday row. Still to see with the market open:
> stage 4's C11 and check 11 on live quotes through the real app. Stage 3's
> market-closed, provisional, source-failure, override-panel and dark-theme states were
> seen on 19 November through the replay app's switch (`data/replay_mode.txt`: "closed",
> "nosnap", "fail"; delete the file afterwards). Still to
> check: stage 1's fail, adjust-criteria and override states on live data (a pass was seen
> on MSFT on 19 November). **Raise before the demo:** the demo symbols (SPY returns no view
> by rule; AMZN is bearish on the result alone). Designs still to come from the
> operator: the range-bound brief, the brief when a draft fails validation twice, the
> "analysed before" line. **Do not design them.**
>
> **Mock-up versus operator decisions.** Decisions the operator made during the
> build win over the mock-up where they differ; the list is at the top of
> `docs/product-shell.md`. Do not "correct" the application back to the mock-up.
>
> **Carry these forward (they exist nowhere else).**
> 1. **One draft return in total for the Thesis agent.** The validation check runs as
>    the Thesis agent's output check on the harness and nowhere else; the graph's
>    `validate` node only reports it (`in_harness`). Keep it that way.
> 2. **Output caps.** Retriever and Fundamental Analyst are at 4,000 tokens after
>    cut-offs; the Thesis agent is at 4,000 by operator ruling (it had used up to 2,341
>    of 2,500). The Regime Assessor is at 2,500 by operator ruling (19 November), after empty second answers at 1,500. Changes are recorded
>    in `config/limits.json`.
> 3. **Live checks through the app write to the permanent record** once a view exists
>    (it is append-only). `data/tradecraft.sqlite3` holds such rows from 19 November
>    (five more from the stage 3 checks);
>    the operator may want a clean database before recording the demo.
> 4. **Agent failures become `StepFailed`** through `stage2.require_ok`, never a no-view.
> 5. **Stage 1 on live data has been seen on screen for a pass only** (MSFT, 19 November,
>    which showed a fault in the counts, now fixed). Fail, adjust criteria and the override
>    have been seen on snapshot data only.
> 6. **The cost-filter count was reported on 19 November** (build log) and the operator
>    had the on-screen cost-cap control built the same day. Stage 3's outcomes are in product-shell 6.3.
> 7. **Ask, do not fill.** Every design gap raised so far was settled by the operator
>    and is recorded as a dated "operator decision" in the document it belongs to;
>    `docs/build-log.md` lists them. Stop and ask when a decision conflicts with the
>    build or leaves a gap.
> 8. **Index instruments return no view** by the 18 November decision (sector and macro
>    findings carry no bearing). SPY was to run all four stages; raise it.

> **BUILD PLAN: `docs/build-plan.md`** (confirmed by the operator, 18 November
> 2026). Follow it.
> - **The agent harness is built first;** every agent is a configuration on it.
>   **LangGraph runs the workflow** and the harness runs inside each node. Read the
>   current LangGraph documentation; do not write its interface from memory.
> - **Run limits** (plan, section 4) are settings: tool calls, time, output and
>   document size, retries, spend, rate limits, caching, network and file allowlists.
> - **Reasoning the capstone grades** (plan, section 4a): the Retriever and the
>   Fundamental Analyst run a ReAct loop with tools and one recovery is shown; the
>   Thesis agent sets out three branches, prunes by the precedence rules and the
>   tree is shown.
> - **Guardrails by agent** are in section 5; the **safety statement** for the
>   report is section 11. Cut lines are fixed in section 7.
> - **Last action on Sunday: publish the repository for the evaluators** (plan,
>   section 12). Do not push the existing history to a public repository: every
>   commit carries the operator's private email. Run the checks in section 12
>   first. The operator creates the remote and does the push.

> **DATA SOURCES FOR THE BUILD (settled for the demo, 18 November 2026).** The
> operator's reminder was raised and answered. See `config/data_sources.json` and
> `docs/decisions/2026-11-18-data-sources.md`.
> - **Free sources, plus the FMP premium plan (amended 18 November 2026, evening).**
>   Filings from SEC EDGAR (`SEC_USER_AGENT` is in `.env`, set by the operator;
>   never put the email in a command, a file you write, or a commit).
> - **The FMP key (`FMP_API_KEY` in `.env`) is now premium** (750 calls a minute,
>   50 GB per rolling 30 days) and serves 105 of the 106 names (not BRK.B):
>   earnings dates (still no time of day), past earnings, ex-dividend dates, the
>   current annual analyst consensus, company profile, and **company news, which
>   the demo now uses.** Quarterly estimates and the `limit` parameter are served
>   but not adopted for the demo. Use httpx, not urllib: urllib had large FMP
>   responses cut off.
> - **Macro calendar:** FOMC decision dates from the Federal Reserve's page, and
>   the dates of four data releases (CPI, Employment Situation, GDP, Personal
>   Income and Outlays) from FRED, using `FRED_API_KEY` in `.env` (added by the
>   operator, 18 November 2026). FRED lists dates only a few weeks ahead.
> - **Demo symbols: NVDA, AMZN, SPY (all four stages), ADBE (stage 1 FAIL path).**
>   Where an input is not served, show "not available" or "could not be checked".
> - **Still to raise with the operator after the demo:** the time of day of
>   earnings, estimate revision history, aggregate index earnings.

Personal, single-user options research tool. Also the capstone for a CMU
agentic-AI course. US market, retail account, no commercial deployment.

## Read this first

`docs/factor-spec.md` is the operating spec (revision 13, 15 November 2026).
**Sections 0a and 0b hold measured data and outrank every literature estimate
elsewhere in the document.** It is the output of
nineteen research strands across seven waves and it supersedes intuition. Read it
before proposing any signal or feature.

The headline conclusions, so you don't rediscover them:

- **Direction prediction is near-worthless** at retail scale: ~7 bp/month,
  median t=0.45 in liquid names post-2005; −1 to +4 bp/month net of costs.
- **Costs dominate.** ATM single-name spreads run ~6.4% effective, 10–13% round
  trip. Index options at 42–48 DTE are ~2%. Cost is an order of magnitude larger
  than gross edge.
- **The system is a cost / execution / event-timing tool**, not an alpha engine.
- **Mode 3 (on-demand) is the build target.** The operator names a ticker or a
  list; **the system drafts the thesis by default** (operator may accept, edit,
  reject, or bring their own), then prices, sizes, challenges and records it.
  Index instruments (SPY, SPX, QQQ, IWM, TLT) are traded here. Hard rules for the
  draft: labelled unvalidated, no score, the Thesis agent never sees option prices
  or implied probabilities, the Critic is a different model family (demo exception: same family, stated on screen), `no_view` is
  allowed, every draft is logged and resolved. See
  `docs/decisions/2026-11-15-system-drafted-thesis.md`.
- **The user can overrule the liquidity gate** and send a ticker or contracts on
  to the next stage; the system shows the cost and records the overrule. The
  system still never proposes a failing contract itself.
- **Every decision at every stage writes an append-only decision record.** If
  the contract is traded, the full chain goes to long-term memory, linked to the
  trade (on-demand design §3a). Build this in from the first stage.
- **Mode 1 (scheduled index overlay) is SHELVED, 15 Nov 2026. Do not build it.**
  Three pre-registered tests found no index-writing programme with positive alpha
  after 2012. Never present index option writing as an income source. Read
  `docs/decisions/2026-11-15-mode-1-shelved.md` before reopening this.
- **Mode 2 (single-name event positioning)** is built later as a scan that feeds
  the Mode 3 pipeline, not as a separate pipeline. Blocked on earnings-date
  sourcing.
- **Trial budget: 4 of ~12 spent** (`vrp_out/TRIALS.log`, append-only). The
  specs in `scripts/tests/vrp_test_a/b/c.py` are frozen. Do not re-run them with changes and
  do not test further Cboe index variants.
  Trial 4 (16 Nov 2026) was Test R, `scripts/tests/range_test_r.py`, spec R-1: the
  volatility-state range adjustment FAILED out of sample. Frozen; do not re-run
  or run variants. See `docs/proposals/2026-11-16-move-forecast-backbone.md`.
- **Thesis stage (Mode 3, step 2A), decided 16 Nov 2026:** a research brief.
  Measured figures in code (base rate, usual range as the 68% band, volatility
  state); a researched view drafted by the agents (bullish, bearish, no view)
  whose probability is the base rate and is NOT moved by the view; price trend
  is description only; a range-bound view by rule on the 7- and 14-day rows.
  The four-layer probability, trend layer, increments and limits are withdrawn.
  See `docs/decisions/2026-11-16-research-brief.md`. Do not reintroduce a
  computed direction or search for another trend indicator.
- **Stage 3, market and contracts (Mode 3), decided 17 Nov 2026:** deterministic
  code, no agents. Candidates by fixed rule (two spread shapes per directional
  view, a single bought option, iron condors for range-bound); defined risk
  only. Filters: liquidity, a cost cap (default 5% of risk, 2-10%), events.
  Ranked by a priority the user picks: Match the view (default), Larger payoff
  (payoff at one usual range per dollar at risk), Lowest cost. Expiry defaults
  to the thesis horizon; switching is an amendment; a poor match is a soft
  warning. Sizing is an optional maximum loss for the trade on the output
  screen; capital is not asked for. Ranking on gross richness stays prohibited.
  See `docs/decisions/2026-11-17-stage-3-contract-selection.md` and
  `docs/site/market-contracts.html`.
- **Stage 4, the challenge (Mode 3), decided 17 Nov 2026:** two checklists in
  code (12 checks on the thesis, 11 on the contract; each returns passed,
  flagged, not applicable or could not be checked, never "passed" for want of
  data); the thesis restated as a question by a fixed template; balanced
  retrieval from `docs/research/` only (no web); the Critic with nine tasks
  (case for, case against, priced-in test, how the trade loses) and NO verdict,
  score or trading advice; its output is checked in code. One screen, critic
  left and checks right, with a readiness line set by code. Advises, never
  blocks. For the demo the Critic runs on the same model family as the Thesis
  agent, stated on screen. Reads `config/rejected_signals.json` and
  `config/instruments.json`. See
  `docs/decisions/2026-11-17-stage-4-challenge.md` and
  `docs/site/challenge.html`.
- **Stage 2 record additions from stage 4:** `evidence[].family`,
  `evidence[].price_move_since`, `falsifiers[].type`, `inputs_unavailable[]`,
  and a fixed verdict rule for a supplied thesis.
- **Design status:** stages 1 to 4 designed; stages 5 and 6 not designed.
  **Build status is at the top of this file** (application code exists from 18 Nov
  2026; `ANTHROPIC_API_KEY`, `FMP_API_KEY`, `FRED_API_KEY` and `SEC_USER_AGENT` are
  in `.env`). Deadline Sunday 22 Nov 2026 (`docs/build-plan.md`).
- **Documentation pages** tag every figure APPLICATION SCREEN or EXPLANATION
  ONLY and list each stage's screens (`docs/site/THEME.md`).
- **Model tiers, decided 18 Nov 2026:** Haiku 5.5 for the Fundamental Analyst,
  Regime Assessor, Technical Analyst and Evidence Retriever; Opus 5.5 for the
  Thesis agent and the Critic; a local open-source embedding model for the
  research index. One line per agent in `config/models.json`. No open-source
  language model this week. Spend limit $50. Log the token usage of every call.
  See `docs/decisions/2026-11-18-model-tiers.md`.
- **Delivery, decided 18 Nov 2026:** browser first (Python engine serving local
  web pages); a desktop window wrapping the same pages once stages 1 to 4 run end
  to end; a double-click app after that. Build the screens so the wrap needs no
  rework.
- **Scripts were reorganised on 18 Nov 2026** into `scripts/daily/` (run by the
  scheduled job), `scripts/tests/` (the four frozen trials, moved unchanged) and
  `scripts/analysis/` (one-off measurements). Run them from the project root.
  Data folders did not move. `ops/snapshot_cron.sh` calls the daily scripts by
  their new paths; the launchd plist is unchanged. See `scripts/README.md`.
  Application code for the build goes in its own folder, not under `scripts/`.
- **The liquidity gate excludes; it never penalises.** Gross returns are *higher*
  in illiquid terciles (23.9% vs 18.0%) while net goes +8.2% → −0.8%. Any ranking
  on gross richness selects contracts whose edge dies in execution.
- **Dead, do not rebuild:** unusual options flow, IV rank as a verdict, Elliott
  wave, Fibonacci retracements, candlestick patterns, multi-timeframe confluence
  scoring, social sentiment as direction, retail GEX, 13F, accruals, a cardinal
  0–100 score, single-name overlays, the nine Zhan et al. delta-hedged
  characteristics.

## Current state

- `scripts/daily/chain_census.py` — liquidity census + point-in-time snapshot logger. Stdlib
  only, no pip install needed. Cboe delayed-quote fetcher is the default source.
  **Run against live data 12 Nov 2026; results in spec §0a.**
- `universe.txt` — 103 starter tickers, hand-picked for liquidity. **Replace
  with real S&P 500 + Nasdaq 100 constituents** — the curated list cannot
  answer the universe-size question.
- `run_census.sh` — wrapper, loads `.env`.
- `ops/` — launchd daily snapshot job, installed and verified (rc=0, 32,524
  rows, ~91 seconds for 103 names). First scheduled run 11:30 PT.

**The project lives at `~/options-explorer`, NOT under `~/Documents`.** macOS
TCC blocks launchd agents from Documents, Desktop and Downloads with a silent
`Operation not permitted`. See `ops/README.md`. Do not move it back.

## What the first live census established

Measurements, in spec §0a. The three that change design decisions:

- **5.2% of contracts qualify** (1,684 of 32,524) even among the most liquid
  US names. The gate does its work at the contract level, not the name level.
- **Median in-band spread is 10.1% of premium**; only 29.3% are at or under 5%.
  This confirms the published 10–13% round-trip figure from live data.
- **Depth, not name count, is binding.** 36 names carried ≥10 qualifying
  contracts, 15 carried ≥20, and **zero single names reached ≥50**. SPY+QQQ+IWM
  alone hold 50.7% of all qualifying contracts. Consequence: single-name mode is
  **event-driven**, not a ranking sweep — the post-earnings trade needs one
  contract on one name, which the median name's 7 can supply.

The 87-of-103 name pass rate is **not** evidence about universe size: the list
was selected for liquidity, so that is selection on the dependent variable.

## Immediate next steps

1. **Fix the after-hours spot-price anomaly.** The 20:38 PT run blocked 35 names
   on `moneyness_out_of_band` versus 4 intraday. Moneyness cannot change
   overnight, so spot extraction is picking up something stale. Resolve before
   the daily job accumulates much data.
2. **Broad-universe census:** real S&P 500 + Nasdaq 100 constituents, pass
   threshold raised to ≥5 qualifying contracts (make it a config flag), VIX
   stamped on every run. ~8 minutes at current throughput. This answers the
   open universe-size question.
3. **Stamp every run with VIX.** Spread width is volatility-dependent, so
   universe size is regime-dependent and the series is uninterpretable without
   it. Treat universe size as a measured monthly output, never a constant.

## Background: how the census got here

Run the real census. **No API key is required for this** — delayed quotes are
adequate, because spread width and open interest do not change meaningfully in
15 minutes. Real-time data only matters once trading starts.

Preferred, no signup: Cboe publishes free delayed option chains as public JSON,
no auth, e.g.

    https://cdn.cboe.com/api/global/delayed_quotes/options/SPY.json

`cdn.cboe.com` is already in the sandbox allowlist. **Verify the response shape
before writing against it** — fetch one ticker, inspect the JSON, confirm the
bid/ask/open-interest/volume field names, then add a `fetch_chain_cboe()`
alongside the existing Tradier fetcher. The fetch layer is already isolated in
`tradier_get` / `fetch_chain`, so this is a small, contained change. Keep the
Tradier path; do not delete it.

Note Cboe's endpoint covers listed US equity and index options but confirm
coverage for the whole universe rather than assuming it.

Fallback, if Cboe does not work out: a free Tradier Lite token in `.env`:

    cp .env.example .env    # paste TRADIER_TOKEN
    ./run_census.sh

Research predicts ~250 names clear the gate (range 150–400, pessimistic
100–150). Nobody has published this number, so it is a novel output. The answer
feeds back into the spec: universe size changes the breadth penalty and whether
single-name mode is viable.

Then start the daily snapshot. Point-in-time chains cannot be reconstructed
later, so every session not logged is permanently lost:

    ./run_census.sh --snapshot-only

**Run it intraday at 11:30 PT (14:30 ET), not after the close.** Three reasons:

1. After-hours quotes are unusable. Measured on the same gate and universe:
   87 names passed at 12:14 PT, 50 at 20:38 PT.
2. A snapshot is a record of what was *tradeable* at a decision moment. Only a
   live quote answers that.
3. 4pm closing marks are a documented source of bias — they inflate measured
   delta-hedged option returns by 60–140 bp/month. Snapshotting at the close
   would bake that bias into our own data.

What this costs, and why it is acceptable: open interest will be the prior
session's, because OI only updates via overnight OCC reconciliation — fine,
since OI is used purely as a liquidity screen, not a signal. Volume will be
partial-day — also fine, `min_volume` is 0 and volume-as-signal was rejected.

**Use the same time every day.** The series of universe sizes and spread
distributions is only comparable if the sampling time is held constant.

This belongs in launchd on this machine, not in a chat session.

## Hard constraints

- **Never build an in-app backtest-tuning feature.** Best-3-of-20 composites
  need t > 4 for genuine significance and are as biased as searching ~1,780
  signals. A tuning UI makes the system worse while making it look better.
- **Log every configuration tried, from the first commit.** ~12 trials on 60
  monthly observations puts the zero-skill Sharpe bar at 1.0. The count cannot be
  reconstructed afterward.
- **Store raw bid/ask verbatim.** ~38% of raw OPRA prints appear inside the BBO
  from sequencing errors, biased to flatter the trader. Flag pathologies
  (crossed, locked, one-sided); never correct them in place.
- **Primary metric is cross-sectional IC with an IC-IR t-statistic**, not Sharpe.
- **WRDS data is academic-use only** — it can validate the capstone but cannot
  fit a model that trades live.
- **No execution path.** The system produces candidates and cost estimates; the
  human places orders.

## Open items, ranked

1. §1256 eligibility for XSP, VIX, RUT, NDX — only SPX verified; 10.2 pp of P&L
   rests on it
2. Run the spread-gate census for real
3. Does the one-legged short-after-earnings trade survive costs?
4. Reliable earnings dates with before/after-close timing
5. Does a model vol forecast beat clean constant-maturity IV at 42–90 DTE? This
   is the right capstone experiment; both outcomes are publishable.

## Two corrections that override what the spec's older sections say

1. **The 10.1% median single-name spread is an expiry-mix artefact.** 75% of
   in-band contracts in the 12 Nov run sat in two weekly expiries with almost no
   open interest. Restricted to the 15 January monthly: median 5.0%, half at or
   under 5%, 92% with OI >= 100. **Report census output by expiry, never pooled.**
2. **Mode, instrument and structure are three orthogonal dimensions** (spec §1).
   The index instruments are SPY, SPX, QQQ, IWM, TLT (§5a). Mode 3 has no
   structure menu; §5c is the evidence shown beside an index structure. Do not
   infer a structure restriction from a mode.

## Git in this folder

A cloud Claude session cannot delete files here, and git deletes its own locks, so
a commit made from one leaves `.git/HEAD.lock` and the next git command fails with
`File exists`. Clear it with `rm -f .git/*.lock`. Commits from a local session here
are unaffected.

## What each snapshot contains changed on 16 Nov 2026

- **12 and 13 Nov:** contracts 42–90 days from expiry only; 103 names.
- **From 16 Nov:** contracts **0–180 days** from expiry; `_SPX`, `_XSP` and `TLT`
  added. Rows outside 42–90 days carry `dte_out_of_band` in `gate_reasons` and
  `gate_pass` False. Do not compare row counts or pass counts across that date
  without filtering to a common expiry range.
- **From 16 Nov** the last seven columns are the feed's `iv`, `delta`, `gamma`,
  `theta`, `vega`, `rho`, `theo`. Vendor model outputs, not measurements. Empty
  in earlier snapshots.
- Each run also writes `ladder_out/spread_ladder_<stamp>.csv` (ten bid-ask
  thresholds, by expiry).
- The liquidity criteria are adjustable controls in Mode 3:
  `docs/decisions/2026-11-15-liquidity-controls.md`.

## Snapshots taken on NYSE holidays and early-close days are in the archive

The job runs every weekday with no holiday guard, by deliberate decision
(14 Nov 2026) — roughly 9-10 full closures and ~3 early closes a year, about 5%
of files, which is immaterial to the archive's purpose. **But they are not
labelled.** Filter them at read time, never trust them:

- A full closure writes a file with stale quotes and an unchanged spot.
- An early close (10:00 local) writes a file ~1h post-close, which reproduces the
  moneyness pathology that corrupted the 12 Nov run: 35 names blocked on
  moneyness post-close versus 4 intraday.

Cheapest filter: drop any `asof` date where spot is identical to the prior
snapshot across most symbols. A holiday calendar is more precise if you have one.
