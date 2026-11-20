# Tradecraft: the recorded demo (no keys needed)

For evaluators. It lets all four stages be clicked through in a browser with no API key, no network after installation, and no cost.

**Operator decision, 19 November 2026:** the main repository carries the code and the design; a second, small public repository carries the data for this demo. Neither holds a key or a secret.

## Run it

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
git clone <main repository URL> tradecraft && cd tradecraft
```

```bash
git clone <demo-data repository URL> data/demo-bundle
```

```bash
uv sync
```

```bash
.venv/bin/python -m uvicorn tradecraft.demo:app --host 127.0.0.1 --port 8324
```

Then open http://localhost:8324 and search for **AMZN**, **MSFT** or **NVDA**.

## What you will see

| Symbol | Path it shows |
|---|---|
| AMZN | A bearish thesis, three strategies, the challenge with the Critic's output for whichever strategy is selected |
| MSFT | A bullish thesis, three strategies, the challenge with the Critic's output |
| NVDA | "No view: the evidence points both ways", then "Take a view yourself", contracts, and the challenge on the fixed-rule checks alone |

Every page carries **RECORDED DEMO · DATA OF 19 NOVEMBER** and the stage screens carry **PROVISIONAL**.

## What is real and what is recorded

| Part | In the demo |
|---|---|
| Stage 1, the liquidity gate | Runs for real, on the bundled option snapshot. The criteria can be adjusted |
| Stage 2, the thesis | **Recorded.** The four Haiku agents' and the Thesis agent's outputs from a real run of 19 November 2026 |
| Stage 3, contracts | Runs for real: candidates, figures, the cost cap, ranking, switching expiration |
| Stage 4, both checklists, the question, the readiness line | Run for real |
| Stage 4, the Evidence Retriever and the Critic | **Recorded,** one real run for each of the three strategies of AMZN and MSFT at the default expiration and settings |

## Limits, stated plainly

- **The agents are not running.** A live run needs your own Anthropic, Financial Modeling Prep and FRED keys and an SEC contact string in `.env` (see `.env.example`), and market hours for live quotes. The recorded video and the traces are the evidence that the agents run.
- **"Today" is 19 November 2026** and the market is treated as closed. The two checks that need fresh quotes read "could not be checked".
- **Figures differ a little from a live run.** The other stocks' price histories (the pool) are not bundled, so the history-based figures use the stock's own history, and say so.
- **The Critic's output exists only for the six recorded selections.** Change the expiration, raise the cost cap so a different strategy appears, or use NVDA, and the challenge stops with "no saved Critic output"; choose "Continue with the checklists only".
- **The research index** uses keyword search until `.venv/bin/python -m tradecraft.research build` is run once (it downloads a 79 MB local embedding model). The demo does not need it: the retrieved passages are recorded.
- The demo writes to its own database, `data/demo.sqlite3`.

## For the operator: rebuilding the bundle

```bash
.venv/bin/python -m tradecraft.demo export AMZN MSFT NVDA
```

```bash
.venv/bin/python -m tradecraft.demo record AMZN MSFT
```

```bash
.venv/bin/python -m tradecraft.demo scan
```

`export` cuts the latest snapshot, the price histories and the saved thesis runs down to the named symbols. `record` is live: one Evidence Retriever and one Critic run per kept strategy, about $0.10 each. `scan` searches every file of the bundle, decompressed, for the value of each secret in `.env`, for a home-folder path and for an email address, and fails if it finds one. **Run `scan` before every push of the bundle.**
