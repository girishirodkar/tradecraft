# Decision: Haiku for the routine agents, Opus for the thesis and the critic

**Date:** 18 November 2026
**Decided by:** the operator
**Status:** in force. Settings in `config/models.json`.

## The decision

1. **Models are tiered by the job.** The Fundamental Analyst, Regime Assessor, Technical Analyst and Evidence Retriever run on Claude Haiku 5.5. The Thesis agent and the Critic run on Claude Opus 5.5.
2. **No open-source language model this week.** The operator proposed open-source models for the routine agents. The saving over Haiku was about one cent per run, against a second client library, weaker tool calling and half a day of build time before a Sunday deadline.
3. **An open-source embedding model, run locally, for the research index.** Claude offers no embedding model.
4. **The model for each agent is one line in `config/models.json`.**
5. **The Fundamental Analyst starts on Haiku and is checked by hand** against the filings for three tickers. If it misreads, it moves to Sonnet 5.5.
6. **A spend limit of $50** on the API account for the build and the demo.

## The estimate behind it (18 November 2026, published prices)

| Setup | Approximate cost of one run, stages 1 to 4 |
|---|---|
| Everything on Opus 5.5 | $0.70 |
| Routine agents on Haiku 5.5, thesis and critic on Opus 5.5 | $0.23 |
| Routine agents on a free local model, thesis and critic on Opus 5.5 | $0.22 |

- Assumes about 120,000 tokens read and 10,000 written per run. **An estimate, not a measurement.**
- With an allowance for retries, about $0.25 a run: $10 for 40 runs, $15 for 60, with a range of roughly $6 to $36.
- About 95% of a run's cost is the two Opus agents.

## Not models at all

Data collection, the measured figures, the validation check on a draft, both stage 4 checklists, the restated question, the readiness line, and all of stages 1 and 3 are code.

## Cost controls

- Trim each filing in code before a model reads it, and keep every Haiku prompt under 100,000 tokens (above that the rate is five times higher).
- Give the Critic the structured record and the cited passages, not whole documents.
- Extended reasoning on the Opus agents is billed as written tokens; turn it on deliberately.
- Record the token usage the API reports on every call, and replace the estimate with measured figures.

## After the demo

A second model family for the Critic, which the design already calls for. That is a quality reason for another model, and a stronger one than cost.
