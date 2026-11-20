# Tradecraft

A personal options research tool, and the capstone for an agentic-AI course. You name one US-listed underlying; Tradecraft screens its option chain for liquidity, drafts a researched thesis with a team of agents, proposes defined-risk option strategies by fixed rules, and then challenges both the thesis and the strategy before you decide.

**Tradecraft places no orders and gives no investment advice.** It cannot place an order. It states no probability for a view, labels every system thesis "no demonstrated predictive edge", and calls its first-ranked strategy the "best fit", never a recommendation. The research behind it (`docs/factor-spec.md`) concludes that predicting direction is close to worthless at retail scale and that trading costs dominate; the tool is built around cost, execution and honest evidence, not around a signal.

- **The manual:** read it at **[https://girishirodkar.github.io/tradecraft/site/manual.html](https://girishirodkar.github.io/tradecraft/site/manual.html)**. Four pages with one header: what Tradecraft is, the logic of each stage, the architecture at four levels of depth, and the four detailed stage manuals in full. Clicking `docs/site/manual.html` on GitHub shows its source code, not the page; use the link above, or clone the repository and open that file in a browser.
- **Elevator pitch video (1 min 22 s, narrated):** watch it at **[https://girishirodkar.github.io/tradecraft/media/tradecraft-pitch.mp4](https://girishirodkar.github.io/tradecraft/media/tradecraft-pitch.mp4)**. The file is [`docs/media/tradecraft-pitch.mp4`](docs/media/tradecraft-pitch.mp4).
- **Demo video:** *link to be added*
- **Demo data repository:** [https://github.com/girishirodkar/tradecraft-demo-data](https://github.com/girishirodkar/tradecraft-demo-data)

## Try it in five minutes, with no API key

The recorded demo runs all four stages in a browser on bundled data. Full notes: [`docs/recorded-demo.md`](docs/recorded-demo.md).

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/girishirodkar/tradecraft.git tradecraft && cd tradecraft
```

```bash
git clone https://github.com/girishirodkar/tradecraft-demo-data.git data/demo-bundle
```

```bash
uv sync
```

```bash
.venv/bin/python -m uvicorn tradecraft.demo:app --host 127.0.0.1 --port 8324
```

Open http://localhost:8324 and search for **AMZN** (a bearish thesis), **MSFT** (bullish) or **NVDA** (no view, then your own thesis).

In the demo, stages 1 and 3 and stage 4's checks run for real on a bundled option snapshot. The agents' outputs in stage 2 and the Critic's output in stage 4 are recordings of real runs made on 19 November 2026. Every page says RECORDED DEMO.

## Run the tests

```bash
.venv/bin/python -m pytest -q
```

376 tests. They need no key and no network: every agent runs on a scripted model. In a fresh clone four are skipped: three live checks, and one that reads the unpublished price archive.

## Run it live

A live run calls Claude and the data providers, costs about $0.20, and needs market hours for live quotes.

1. Copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY`, `FMP_API_KEY` (the paid plan), `FRED_API_KEY` and `SEC_USER_AGENT`. `TRADIER_TOKEN` is optional: it is the second source of option quotes, used when Cboe does not answer.
2. Build the research index once (it downloads a 79 MB local embedding model): `.venv/bin/python -m tradecraft.research build`
3. Start the app: `.venv/bin/python -m uvicorn tradecraft.web.app:app --host 127.0.0.1 --port 8321`

Option quotes come from Cboe, then Tradier, then the daily snapshot, automatically; the screen names the source. Without the project's daily option snapshot and price archive, which are not published, a run outside market hours stops at the liquidity gate.

## The four stages

| Stage | What it does | Who does it |
|---|---|---|
| 1. Liquidity gate | Screens the option chain on five adjustable criteria; the user may override a fail, and that is recorded | Code |
| 2. Thesis | Gathers evidence, grades it, and drafts a view (bullish, bearish or no view) with invalidation criteria. Measured figures come from code | Evidence Retriever, Fundamental Analyst, Regime Assessor, Technical Analyst, Thesis agent; a validation check in code |
| 3. Contracts | Builds defined-risk candidates by fixed rule, filters on liquidity and a cost cap, ranks by a priority the user picks | Code only, no agent |
| 4. Challenge | Twelve checks on the thesis and eleven on the contract; the thesis restated as a question; passages retrieved from the project's own research, both ways; the Critic's bull case, bear case, loss paths and objections, with no verdict; a readiness line | Code, Evidence Retriever, Critic; an output check in code |

Stages 5 and 6 (decision, sizing, monitoring) are not designed and not built.

## What the course grades, and where it is

| Requirement | Where to look |
|---|---|
| Tool calling | `tradecraft/tools.py` (nine data tools, each allowlisted per agent); `tradecraft/harness/tools.py`; stage 4's `search_research` tool in `tradecraft/stage4.py` |
| Reasoning loop with recovery (ReAct) | `tradecraft/harness/runner.py` (the reason, act, observe loop, one tool retry, one validation return); the Retriever and Fundamental Analyst in `tradecraft/agents.py`; `tests/test_stage2.py`, "recovers from a failed source" |
| Knowledge and memory | `tradecraft/research.py` (a local vector index over `docs/research/`, the factor specification and the decision records); the evidence store and the append-only decision records in `tradecraft/storage.py` |
| Further reasoning (Tree of Thought) | The Thesis agent's three branches, tested against precedence rules and pruned: `THESIS` in `tradecraft/agents.py`, re-checked in code by `tradecraft/validation.py`; shown on the thesis screen under "How the system reasoned" |
| Multi-agent coordination | `tradecraft/workflow/graph.py`: one LangGraph graph, three analysts in parallel merged for the Thesis agent, pauses for the user, stage stops and retries. Diagram: `docs/workflow-diagram.md` |
| Safety | Guardrails by agent: `docs/build-plan.md`, section 5; the statement of unintended actions: section 11; run limits in `config/limits.json`; `tests/test_guardrails.py` and `tests/test_limits.py` |
| Reuse | One harness runs every agent from a configuration (`AgentConfig`); the Evidence Retriever has two configurations (stage 2 and stage 4); the three analysts are one class |

## Safety, in brief

| Unintended action | What prevents it |
|---|---|
| Placing an order | No tool can place an order, and no agent has a tool that reaches a broker. The option-chain code reads market data from Tradier (a broker's service) when Cboe fails: prices and chains only |
| Following instructions hidden in a filing or a research passage | Fetched text is wrapped and labelled as data; tools are allowlisted, so an injected instruction has nothing to call |
| Spending without limit | Tool-call, time and spend limits per agent, stage, request and day |
| Presenting a guess as a fact | No agent sets a figure; every claim cites stored evidence; a draft that does not is returned once, then rejected |
| Presenting research as advice | No probability for a view; the Critic's output is refused if it gives a verdict, a score or advice |
| Acting on stale inputs | The readiness line; a check never reports "passed" for want of data |
| Leaking a key | Keys live only in `.env`, which is git-ignored, and are redacted from every trace |

The full table is in `docs/build-plan.md`, section 11.

## Where things are

| Path | Contents |
|---|---|
| `tradecraft/harness/` | The agent harness: one function runs any agent, with limits, guards and a trace |
| `tradecraft/agents.py`, `stage2.py`, `validation.py` | Stage 2's agents, steps and validation check |
| `tradecraft/stage1.py`, `gate.py`, `stage3.py` | Stages 1 and 3 (code only) |
| `tradecraft/stage4.py`, `research.py` | Stage 4 and the research index |
| `tradecraft/workflow/` | The LangGraph workflow |
| `tradecraft/web/` | The local web app (FastAPI and plain HTML, CSS and JavaScript) |
| `tradecraft/demo.py`, `dev_replay.py` | The recorded demo and the development replay |
| `config/` | Run limits, model per agent, rejected signals, stage settings |
| `tests/` | 376 tests |
| `docs/site/manual.html` | **The product manual:** what Tradecraft is, why each stage works as it does, and the architecture from a one-page overview down to the modules |
| `docs/` | The design: `on-demand-mode-design.md`, `product-shell.md`, `decisions/`, `build-plan.md`, `build-log.md`, the approved mock-up `site/tradecraft-prototype.html` (open it in a browser), and the research in `research/` and `factor-spec.md` |
| `scripts/`, `vrp_out/` | The liquidity census (`docs/liquidity-census.md`), the daily snapshot scripts and four frozen, pre-registered tests with their append-only trial log |
| `CLAUDE.md` | The build's working status, kept for the AI coding assistant that helped build it |

## Known limits

- **The Critic runs on the same model family as the Thesis agent** (both Claude). The screen says so. A different family is the aim.
- **No demonstrated predictive edge.** Three pre-registered tests of index option writing and one of a volatility adjustment failed and are recorded in `vrp_out/TRIALS.log`. Nothing here has been shown to predict direction.
- **Cboe refused the option chain on 20 November 2026** (HTTP 403, cause not known). Tradier was added that day as the second source; the daily snapshot job still uses Cboe alone.
- **Data gaps are shown, not hidden:** no time of day for earnings, no estimate revision history, annual consensus only. Affected checks read "not available" or "could not be checked".
- **Index instruments return no view by rule,** so SPY needs a thesis the user enters.
- **Not built:** editing a drafted thesis, the range-bound brief, the Records and Settings pages, a trace viewer, stages 5 and 6.

## What is left out of this repository

- API keys and the `.env` file.
- The daily option snapshots, the price archive and cached provider responses (third-party data).
- The scheduled job's machine-specific files and logs.
- The commit history: this is a single-commit copy of the working repository.

## Models and data sources

Claude Opus 5.5 (Thesis agent, Critic) and Claude Haiku 5.5 (the other agents), set in `config/models.json`. A local open-source embedding model (all-MiniLM-L6-v2) for the research index. Option quotes from Cboe's delayed feed, then Tradier if Cboe does not answer, then the daily snapshot; filings from SEC EDGAR; earnings, estimates, news and dividends from Financial Modeling Prep; calendars from the Federal Reserve and FRED; prices from Yahoo.
