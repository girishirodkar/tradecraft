# Decision: free data sources for the demo; a paid provider decided afterwards

**Date:** 18 November 2026
**Decided by:** the operator, after two probes
**Status:** in force for the demo, **as amended the same evening (below).** Settings in `config/data_sources.json`.

## Amendment, 18 November 2026 (evening): FMP premium plan; news and wider coverage adopted

The operator upgraded the FMP key to the premium plan (750 calls a minute, 50 GB per rolling 30 days) and, after the probes were re-run, **decided that the demo uses two premium features: company news and the wider symbol coverage.** Points 1 to 3 of the decision below are superseded to that extent; point 4 stands.

| Need | Premium FMP key, measured 18 November 2026 (evening) |
|---|---|
| Symbols | **105 of 106** universe names served; BRK.B refused as a special symbol |
| Company news | **Served** (`/stable/news/stock`) |
| Quarterly estimates; the `limit` parameter | Served; **not adopted for the demo** |
| Time of day for earnings | **Still not served,** in either the per-symbol or the market-wide calendar |
| Estimate revision history | Not tested; no endpoint identified |
| Aggregate index earnings | Not tested |

What this changes:

- **Input 3, company news, becomes available** to the Evidence Retriever and the Fundamental Analyst. News items are untrusted text: wrapped and labelled as data, like filings.
- **Demo tickers are no longer limited to the 49 free-plan names.** The chosen four (NVDA, AMZN, SPY, ADBE) are unchanged. The "not available" path remains for BRK.B and for any input FMP does not serve.
- **Unchanged:** no time of day for earnings, so the report day still counts as inside any window that contains it, and the Event Assessor stays inactive; estimate revisions still have a current figure and no history.
- **Measurement note:** the probe scripts' standard-library HTTP client had large responses cut off (`IncompleteRead`), which first looked like 55 refusals; the same requests through httpx all completed. Application code uses httpx with retries.

Still open after the demo: earnings time of day, estimate revision history (or saving the consensus daily), aggregate index earnings, and whether quarterly estimates add anything.

## The decision (as first taken, 18 November 2026)

1. **The demo runs on free sources.** Prices and option chains as before; filings from SEC EDGAR; macro data from FRED and the Federal Reserve schedule; and, new, **earnings dates, past earnings, dividends, analyst estimates and company profile from the free Financial Modeling Prep key.**
2. **The free FMP key covers 49 of the 106 universe names.** Demo tickers are chosen from those 49. For a name outside them, the affected inputs and checks report "not available" or "could not be checked", as designed.
3. **No paid data plan before the demo.** Which provider to pay for is decided afterwards, on evidence.
4. **Application data is fetched by code with a key, not through a Claude connector.** A connector serves Claude in the chat, costs tokens for every fetch and puts a model between the source and the record.

## What was measured (18 November 2026)

| Need | Free FMP key |
|---|---|
| Earnings dates | Served. 48 of 48 covered companies returned a future report date |
| Time of day for earnings | **Not served.** No such field |
| Past earnings, actual against expected | Served, many years back |
| Ex-dividend dates | Served. 17 of 20 sampled; the other three pay no dividend |
| Analyst estimates | Served as the current annual consensus. No revision history |
| Company profile and sector | Served |
| Company news | **Refused** on the free plan |
| Symbols | 49 served, 57 refused, including every fund except SPY and both index symbols |

The free plan also refuses the `limit` parameter and quarterly estimates.

## What this changes in the design

- **Thesis check 6 and the stage 3 events filter** work for the 49 names. With no time of day, the report day itself counts as inside any window that contains it.
- **Contract check C8** (early assignment) can use ex-dividend dates. A future ex-date appears only once declared; before that it is estimated from the payment frequency and labelled an estimate.
- **Input 6, reaction to past earnings,** becomes computable.
- **Input 4, estimate revisions,** has a current figure and no history. The history can be built by saving the consensus each day.
- **Input 3, company news,** stays unavailable.
- **Index instruments** get nothing from this key except SPY's dividends.

## Also considered

- **Alpha Vantage.** Its documentation lists an earnings calendar, dividends, estimates, news, transcripts and options. The operator's free key was refused for what was needed. Not paid for: its coverage of the two details that matter most (time of day, estimate history) was unconfirmed. Its support page says verified educational projects may get free access.
- **A sample Alpha Vantage "Trading Analysis Report"** on AAPL (17 November 2026, produced by a third-party multi-agent program on a Gemini model). Not used. It ends in a BUY verdict reached by agent debate, rests direction on moving averages, RSI, MACD and sentiment, cites no sources, and contradicts itself on several figures. Useful only as a contrast for the capstone report.
- **Connectors in the Claude directory** (FMP, Alpha Vantage, Twelve Data, Financial Datasets, Bigdata.com and others). Useful for evaluating a provider from a chat; not the route for the application's data.

## Still open, for after the demo

- A paid provider that covers all 106 names, gives the time of day for earnings, estimate revision history and company news, and aggregate index earnings.
- Whether to save the FMP consensus daily from now, so that revision history starts accumulating.
