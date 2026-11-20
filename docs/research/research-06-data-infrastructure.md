# Research 06 — Data Infrastructure and Feasibility for a Single User

**Scope:** Options chain/quote data, broker APIs, historical options for backtesting, EDGAR and fundamentals, free/cheap alternatives, build-vs-buy, running costs.
**Framing:** Personal, single-user, non-commercial tool. No redistribution, no other users.
**Date of research:** 10 November 2026. All prices verified on vendor pages unless marked otherwise.

**Important caveat on verification:** several vendor domains (polygon.io, alphavantage.co, eodhd.com, barchart.com, quiverquant.com, developer.schwab.com, unusualwhales.com, docs.claude.com) were not fetchable in this session. Where no credible vendor page could be reached, the finding is marked **Could not verify** rather than guessed. A large fraction of the search results for pricing queries are AI-generated SEO pages (qveris.ai, costbench.com, apicostcalc.com, multiples.vc, flashalpha.com comparison articles) and I have deliberately not used them as price sources.

---

## 1. THE CMU / WRDS QUESTION — THE HIGHEST-VALUE FINDING

**CLAIM:** Carnegie Mellon University Libraries subscribes to WRDS, and access requires only a CMU email address (plus Full VPN from off campus).
**SOURCE:** Carnegie Mellon University Libraries, "PPIA — Business" research guide, accessed 10 Nov 2026, https://guides.library.cmu.edu/PPIA/Business
**CONFIDENCE:** Verified on vendor page (CMU Libraries).
**IMPLICATION FOR THE BUILD:** The single largest cost line in this entire project — multi-year historical options data with Greeks and a volatility surface — is plausibly $0 for the duration of the course. This changes the economics more than any other finding in this report.

**CLAIM:** CMU's database A–Z list contains an entry, accessed through WRDS, for US options and their underlying securities including historical price, implied volatility and sensitivity information — which is the standard library description of OptionMetrics IvyDB US.
**SOURCE:** Carnegie Mellon University Libraries, A–Z database list, accessed 10 Nov 2026, https://guides.library.cmu.edu/az.php?q=options
**CONFIDENCE:** Verified on vendor page, but the entry's title was not captured; identification as OptionMetrics is by description, not by name. **Confirm by logging in.**
**IMPLICATION FOR THE BUILD:** If this is IvyDB US, the developer has 1996-onward daily option prices, IV, delta/gamma/vega/theta and a standardised constant-maturity volatility surface. That is precisely the dataset the Zhan et al. delta-hedged-return literature is built on, and it is the single dataset that makes a credible replication possible.

**CLAIM:** OptionMetrics IvyDB US on WRDS begins January 1996; IvyDB Europe begins January 2002.
**SOURCE:** WRDS, "OptionMetrics" data vendor page, accessed 10 Nov 2026, https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** 30 years of history. Enough for a properly sample-split study with a held-out period, which the other agent's strand will care about.

**CLAIM:** IvyDB US includes end-of-day bid/ask, volume, open interest, per-option implied volatility, delta/gamma/vega/theta, a daily standardised constant-maturity volatility surface interpolated across expiry and delta-moneyness, plus dividends, rates and corporate actions. Commercial licensing is annual-only and quote-only; a free sample exists.
**SOURCE:** Datarade listing for OptionMetrics IvyDB US, accessed 10 Nov 2026, https://datarade.ai/data-products/optionmetrics-ivydb-us-historical-option-prices-and-implied-optionmetrics
**CONFIDENCE:** Secondary source (vendor-supplied listing on a data marketplace). Price genuinely not published anywhere.
**IMPLICATION FOR THE BUILD:** The vol-surface-position component of the strategy ("where does this contract sit on the surface") is a solved problem on IvyDB and an unsolved one on almost every retail feed, none of which ship a fitted surface. Commercially this dataset is five figures per year; there is no retail route to it.

### The blocker hidden inside this good news

**CLAIM:** WRDS Terms of Use restrict the service to academic and non-commercial research, state that users may not use downloaded data for any non-academic or commercial endeavour, prohibit automated extraction from the site, prohibit credential sharing (including with co-authors), and require a citation in publications.
**SOURCE:** WRDS, "Terms of Use," accessed 10 Nov 2026, https://wrds-www.wharton.upenn.edu/users/tou/
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD — read this carefully:** This cleanly splits the project in two.
- **Research / backtest / capstone deliverable:** legitimate academic use. Running the Zhan et al. characteristic replication on IvyDB, writing it up, presenting it as coursework — this is exactly what the licence contemplates.
- **Live signal generation for the developer's own trading:** this is a non-academic endeavour. Using WRDS-derived data, or a model whose parameters were fitted on WRDS data and are then applied to real money, sits on the wrong side of that sentence.

The practical architecture that respects this: **fit and validate on WRDS; run live on independently-licensed data.** Keep the two data paths physically separate in the codebase. Do not let a WRDS-derived calibration file end up in the live scoring path without a conscious decision. Also note the institutional subscription may add further restrictions on top of the base ToU, and access presumably ends when enrolment ends.

**CLAIM:** CMU also provides S&P Capital IQ (Pittsburgh campus only) and Bloomberg Terminals in Hunt Library, Sorrells Library and the Tepper School.
**SOURCE:** CMU Libraries PPIA Business guide (as above).
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** Bloomberg terminals are a manual, no-API, no-bulk-export route. Useful for spot-checking a number, useless for a pipeline.

### Analyst forecast dispersion — the characteristic with no cheap source

**CLAIM:** I/B/E/S estimate analytics include mean, median, high, low and standard deviation across estimate periods, which is the dispersion measure the Zhan et al. specification needs.
**SOURCE:** LSEG, "I/B/E/S Estimates — Estimate Analytics" data catalogue page, accessed 10 Nov 2026, https://www.lseg.com/en/data-catalogue/company-data/ibes-estimates/estimate-analytics
**CONFIDENCE:** Verified on vendor page. Note the page states US and Rest-of-World coverage from 2012 for this particular analytics product; the classic IBES Summary history on WRDS goes back much further (not verified here). No price published.
**IMPLICATION FOR THE BUILD:** Dispersion is obtainable *if* CMU's WRDS subscription includes IBES. **This was not confirmed** — the CMU A–Z search surfaced only the options entry. This is the single most important thing to check on first login, because without IBES, one of the nine characteristics has no good source.

**CLAIM:** No free or near-free API was confirmed to publish the standard deviation or full distribution of analyst EPS estimates.
**SOURCE:** Attempted verification on Finnhub pricing and estimates pages (https://finnhub.io/pricing, https://finnhub.io/pricing-stock-estimates) and FMP's analyst estimates documentation (https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api), all accessed 10 Nov 2026; all three render pricing and response schemas client-side and returned no substantive content.
**CONFIDENCE:** Could not verify — this is an absence of confirmation, not a confirmed absence. FMP's own marketing copy elsewhere discusses measuring estimate dispersion, so a usable field may well exist on a paid tier.
**IMPLICATION FOR THE BUILD:** Treat analyst dispersion as the weakest leg of the nine-characteristic model. Two honest fallbacks: (a) proxy dispersion with high/low estimate range divided by |mean|, if a cheap source gives high/low and a count; (b) drop the characteristic from the live model and report in the capstone that it was available in the backtest but not in production — which is itself an interesting and honest finding about retail-obtainable signals.

### Where the other eight characteristics come from

Cash holdings, cash-flow variance, new share issuance, total external financing, profit margin and profitability are all derivable from **EDGAR XBRL companyfacts** at zero cost. Stock price is trivially available. Distress risk is a computed quantity (Altman-Z or Campbell-Hilscher-Szilagyi style) built from the same statements plus market data. **Eight of nine are free.** Only dispersion needs a vendor.

---

## 2. BROKER-PROVIDED DATA AND APIs

This section confirms the brief's hypothesis: broker data is the highest-leverage path for *live* data, and is almost worthless for *historical* options data.

### Interactive Brokers

**CLAIM:** IBKR charges non-professional accounts USD 1.50/month for OPRA (US Option Exchanges) Level 1, waived when monthly commissions reach USD 20; the US Equity and Options Add-On Streaming Bundle is USD 4.50/month; waivers are not cumulative and apply first to the highest-priced service.
**SOURCE:** Interactive Brokers, "Market Data Pricing," accessed 10 Nov 2026, https://www.interactivebrokers.com/en/pricing/market-data-pricing.php?menu=B
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** Real-time, exchange-sourced OPRA quotes for roughly the price of a coffee per month. Nothing else in this report comes close on a per-dollar basis for live quote quality — and quote quality is exactly what the liquidity gate depends on. This is the single best value line item available.

**CLAIM:** Every IBKR account starts with 100 concurrent market data lines; the allocation grows as the greater of (monthly commissions ÷ 8), (equity × 100 ÷ 1,000,000), or 100. Options Greeks require subscriptions to both the underlying and the derivative. Tick-by-tick requests are capped at about 5% of total lines.
**SOURCE:** IBKR Campus, "Market Data Subscriptions," accessed 10 Nov 2026, https://www.interactivebrokers.com/campus/ibkr-api-page/market-data-subscriptions/
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD — this is a real architectural constraint.** 100 lines means roughly 100 simultaneously-streaming contracts. A single liquid underlying's full chain can exceed that on its own. IBKR is therefore excellent for **deep monitoring of a short, already-selected shortlist** and structurally unsuited to **broad scanning across a watchlist**. Design accordingly: scan somewhere cheap and wide, then confirm on IBKR narrow and deep. Do not architect a scanner on IBKR and discover this at integration time.

**CLAIM:** IBKR historical data is unavailable for expired options, FOPs, warrants and structured products, and end-of-day data for options is also unavailable. Pacing limits: max 50 simultaneous open requests; identical requests within 15 seconds, six-plus requests for the same contract/exchange/tick-type within two seconds, or more than 60 requests in any ten-minute window all trigger violations for bars of 30 seconds or less; BID_ASK counts double; sub-30-second bars older than six months are unavailable.
**SOURCE:** Interactive Brokers, TWS API "Historical Data Limitations," accessed 10 Nov 2026, https://interactivebrokers.github.io/tws-api/historical_limitations.html
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** **IBKR cannot backtest options. At all.** Expired contracts are the entire substance of an options backtest and IBKR does not retain them. Anyone planning to "just pull history from IBKR" is going to lose a week discovering this. IBKR is a live-execution and live-quote venue only.

### Tastytrade

**CLAIM:** The Tastytrade API is open to funded account holders via OAuth, returns real-time quotes over REST with no delayed option, covers equity options and future options, supports a 100-symbol batch limit on REST market data, and exposes positions and balances including quantity, mark and cost basis. DXLink streaming requires a fully onboarded customer and quote tokens expire after 24 hours.
**SOURCE:** Tastytrade Developer, "Market Data" and docs index, accessed 10 Nov 2026, https://developer.tastytrade.com/docs/concepts/market-data/ and https://developer.tastytrade.com/docs/
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** A genuinely free, documented, modern API with real-time options quotes and position data, no separate market-data fee found. The docs explicitly describe building a small read-only personal app, so personal use is clearly contemplated.

**CLAIM:** The DXLink protocol defines a Greeks event type, but Tastytrade's documentation does not confirm that Greeks are delivered for option symbols, stating only that available event types depend on the feed and token.
**SOURCE:** Tastytrade Developer, "Streaming," accessed 10 Nov 2026, https://developer.tastytrade.com/docs/concepts/streaming/
**CONFIDENCE:** Verified on vendor page that the question is *unanswered* there.
**IMPLICATION FOR THE BUILD:** Do not assume Greeks. Verify empirically with a sandbox/production token before designing around them. If Greeks are absent, they must be computed locally — which is not hard (Black-Scholes plus a vol solve) but does mean owning the dividend and rate assumptions, and your delta will then differ from the broker's displayed delta.

**CLAIM:** Tastytrade's API Terms of Service were not retrievable; personal-vs-commercial terms are not stated in the docs.
**CONFIDENCE:** Could not verify.
**IMPLICATION FOR THE BUILD:** Read the linked ToS PDF before relying on it. Low risk for single-user read-only use, but unverified.

### Tradier

**CLAIM:** Tradier includes API access in all plans including the $0 Lite plan; Pro is $10/month and Pro Plus $35/month. Option chains include Greeks. A Tradier Brokerage account includes API access at no extra charge via a token, with no OAuth needed; without Partner status, API access is for personal use only. Sandbox is paper trading with 15-minute delayed data. Rate-limited requests return HTTP 400 with a Quota Violation body and X-Ratelimit headers.
**SOURCE:** Tradier, "Pricing" and Tradier Docs "Market Data," accessed 10 Nov 2026, https://tradier.com/individuals/pricing and https://docs.tradier.com/docs/market-data
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** The cheapest route to Greeks-included option chains with an explicit personal-use blessing. Note the terms are the right way round for this project: personal use is the *default*, and it is distribution that requires Partner status.

**CLAIM:** Tradier does not provide historical data for expired options.
**SOURCE:** Tradier Docs "Market Data" (as above).
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** Same blocker as IBKR. Live only.

### Alpaca

**CLAIM:** Alpaca's Basic plan is free and gives options an Indicative Pricing Feed, 200 WebSocket quote subscriptions, historical data limited to the latest 15 minutes, and 200 historical API calls/min. Algo Trader Plus is $99/month and gives the OPRA feed, 1,000 WebSocket subscriptions, unrestricted historical data and 10,000 calls/min.
**SOURCE:** Alpaca Docs, "About Market Data API," accessed 10 Nov 2026, https://docs.alpaca.markets/us/docs/about-market-data-api.md
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** The free tier's indicative feed and 15-minute historical window make it unusable for a liquidity gate — an indicative price is not an executable spread. The $99 tier is a credible real-time backbone with far more headroom than IBKR's 100 lines.

**CLAIM:** Alpaca's historical options data begins February 2024.
**SOURCE:** Alpaca Docs, "Historical Option Data," accessed 10 Nov 2026, https://docs.alpaca.markets/docs/historical-option-data
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** Under three years of history, covering an unusual market regime. Too short for a monthly-horizon strategy study: roughly 33 monthly observations, which is not enough to say anything with confidence about a signal of the size these papers report. Alpaca is a live feed, not a backtest source. Greeks and IV are not mentioned in the docs and should be assumed absent.

### Schwab / thinkorswim

**CLAIM:** Schwab's developer portal could not be reached, and no authoritative statement of individual-developer Market Data Production availability was obtained.
**SOURCE:** developer.schwab.com was not fetchable; schwab-py documentation was not fetchable. Searches returned only third-party SDKs (schwabr, schwab-go, schwab-sdk, @sudowealth/schwab-api), whose existence implies a working public API but does not establish its current approval terms.
**CONFIDENCE:** Could not verify.
**IMPLICATION FOR THE BUILD:** The post-TDA-migration Schwab API is the one broker question this research could not close. Given that Tradier and Tastytrade both work, are documented, and are free, **there is no reason to block on Schwab.** Note separately that Options Analysis Suite lists Schwab among its bring-your-own-key broker integrations, which is indirect evidence the API is live and usable by individuals.

### Robinhood

Not researched; the unofficial API carries account-termination risk under Robinhood's terms and offers nothing the licensed options above do not. **Recommendation: do not use.** There is no upside that justifies risking a funded account.

### Position and fill data for the outcome ledger

**CLAIM:** Tastytrade exposes positions and balances with quantity, mark and cost basis, and documents order lifecycle including partial fills; Tradier's brokerage API includes account event streaming.
**SOURCE:** Tastytrade and Tradier docs as cited above.
**CONFIDENCE:** Verified on vendor page for positions/balances; a dedicated fills/transactions endpoint was not confirmed in the pages read.
**IMPLICATION FOR THE BUILD:** The prior wave's conclusion that an outcome ledger and measured actual paid spread are essential is **satisfiable at zero marginal cost** on either Tastytrade or Tradier. This matters more than it sounds: the gap between modelled mid-price fills and actual fills is where most retail options backtests die, and here you can measure it directly on your own trades. IBKR additionally offers a Flex Web Service for scheduled report delivery (could not verify details — the page was not fetchable), which is the conventional route for IBKR execution history.

---

## 3. HISTORICAL OPTIONS DATA FOR BACKTESTING

The expensive requirement. Summary up front: **two genuinely affordable routes exist (ThetaData subscription, ORATS one-time purchase), plus one free academic route (WRDS/OptionMetrics) that cannot legally feed live trading.**

**CLAIM:** ThetaData's individual options tiers are Value $40/month (6 years history, 2 concurrent requests, low-latency snapshots, 1-minute intervals), Standard $80/month (10 years, 4 concurrent, tick-level data, option chain snapshots, every OPRA NBBO quote) and Pro $160/month (14 years, 8 concurrent, tick-level, option root snapshots, every option trade). The Individual tier is personal use only with no redistribution or business use; a separate Business licence covers commercial applications. There is no free tier, and Greeks/IV are not mentioned.
**SOURCE:** ThetaData, "Pricing," accessed 10 Nov 2026, https://thetadata.net/pricing
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** **The best licensing fit in this entire report.** ThetaData has explicitly built a personal-use tier, priced it for individuals, and permits exactly the use contemplated here — unlike WRDS, which forbids it. The Standard tier at $80/month with 10 years of every OPRA NBBO quote and chain snapshots is enough to backtest a monthly-horizon strategy properly *and* to measure realistic spread costs, which is the thing the liquidity gate exists to model. Greeks must be computed locally; with NBBO quotes and an underlying price this is straightforward.

**CLAIM:** ORATS offers individual non-professional pricing of $199/month for the Delayed Data API (20,000 requests/month), with a one-time historical download covering 2007 to present for $599 and recurring data at $99/month. Standard tiers are Delayed $199, Live $299, Live Intraday $599, All-In $899 per month, with Tools add-ons (Option Scanner $99, Backtest Finder $99, Intraday Backtester $299, Time & Sales $299). EOD history covers about 6,000 symbols from 2007; one-minute intraday from August 2020. Strikes data includes bid/ask quotes and Greeks. There is no free trial.
**SOURCE:** ORATS, "Data API" and the individual/non-professional pricing page, accessed 10 Nov 2026, https://orats.com/data-api and https://orats.com/reddit
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** **The $599 one-time purchase is the most interesting number in this section.** 19 years of EOD options data with Greeks already computed, under an individual non-professional licence, with no recurring obligation. For a capstone that needs one good backtest rather than a live data feed, a one-time $599 beats $80/month indefinitely, and it produces an artefact the developer keeps. It is also the only commercially-licensed dataset here that is directly comparable in structure to OptionMetrics — which means a WRDS-based backtest could be *reproduced* on ORATS data to prove the live model does not depend on academic-licensed data. That reproduction step is how you cleanly resolve the WRDS licensing problem.

**CLAIM:** Databento offers OPRA historical data from $0.04/GB with coverage from 2013 and over 1.6 million symbols, gives new users $125 in free credits, and explicitly does not provide pre-calculated IV or Greeks. A $199/month Standard subscription was introduced in June 2025, and usage-based *live* pricing ended at that time while usage-based *historical* pricing continues.
**SOURCE:** Databento, "Options data" and "Introducing new OPRA pricing plans" (3 June 2025), accessed 10 Nov 2026, https://databento.com/options and https://databento.com/blog/introducing-new-opra-pricing-plans
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** $0.04/GB sounds free until you remember OPRA is the highest-message-rate feed in US markets. Full tick OPRA runs to terabytes per year; at $0.04/GB a single year of full tick could still run into four figures. The usable play is the **CBBO-1m** (one-minute consolidated BBO) schema rather than raw ticks, which collapses the volume enormously. The $125 free credit is enough to size a real query before committing. No Greeks means local computation. Treat Databento as the precision instrument for a narrowly-scoped question, not the general backtest source.

**CLAIM:** CBOE DataShop's "Option Trades with Calculations" provides trade price/size, executing exchange, prevailing NBBO at time of trade, and point-in-time implied volatility and Greeks calculated at execution, from January 2012, purchasable by date range and symbol or as a daily subscription. No prices are displayed before making selections, and no non-professional tier is mentioned. A separate CGI licence for index values starts at $1,000/month.
**SOURCE:** CBOE DataShop, "Option Trades with Calculations," accessed 10 Nov 2026, https://datashop.cboe.com/option-trades-with-calculations
**CONFIDENCE:** Verified on vendor page that prices are not published; price itself **could not be verified**.
**IMPLICATION FOR THE BUILD:** Per-symbol, per-date-range purchasing is genuinely attractive for a narrow study (one watchlist, five years) and the IV/Greeks-at-execution field is high quality. But you cannot plan a budget against an unpublished price. Build the symbol/date selection in the cart and read the subtotal before committing. The absence of a non-professional tier is a mild warning sign on cost.

**CLAIM:** OptionMetrics does not publish pricing; only annual licences are offered, with no one-off, monthly or usage-based option.
**SOURCE:** Datarade OptionMetrics IvyDB US listing (as cited above).
**CONFIDENCE:** Secondary source.
**IMPLICATION FOR THE BUILD:** There is no retail route to OptionMetrics. The academic route via CMU is the only realistic access, with the licence constraint described in section 1.

**Nasdaq Data Link** was not researched in depth; its options offerings are largely resold third-party products and nothing suggested it undercuts ThetaData or ORATS. **Could not verify.**

### What a realistic multi-year equity-options backtest actually costs

- **$0** — WRDS/OptionMetrics, 1996–present, best-in-class, **academic use only, cannot feed live trading.**
- **$599 one-time** — ORATS full history 2007–present, EOD, Greeks included, individual non-pro licence, yours permanently.
- **$80/month ($960/yr)** — ThetaData Standard, 10 years, tick and NBBO quotes, personal-use licence, best spread realism.
- **$40/month ($480/yr)** — ThetaData Value, 6 years, 1-minute intervals. Adequate for a monthly-horizon study.
- **Low hundreds to low thousands, unpriced** — CBOE DataShop for a narrow symbol/date slice.
- **Variable, potentially large** — Databento at $0.04/GB, manageable only on aggregated schemas.

The honest headline: **a credible multi-year options backtest now costs between $0 and $960 for one person.** This was not true a few years ago and it substantially de-risks the project.

---

## 4. EDGAR AND FUNDAMENTALS

**CLAIM:** The SEC EDGAR data APIs require no authentication or API keys. They comprise the submissions API (data.sec.gov/submissions/CIK##########.json, with older filings split into linked files), and XBRL companyconcept, companyfacts and frames APIs. Bulk archives companyfacts.zip and submissions.zip are rebuilt nightly at approximately 3:00 a.m. ET.
**SOURCE:** SEC, "EDGAR Application Programming Interfaces," accessed 10 Nov 2026, https://www.sec.gov/search-filings/edgar-application-programming-interfaces
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** The entire fundamentals layer is free, keyless and bulk-downloadable. Pull companyfacts.zip once and work locally rather than hammering the API — this sidesteps rate limits entirely and makes the pipeline reproducible, which matters for a capstone.

**CLAIM:** SEC.gov's maximum automated access rate is 10 requests per second, and programmatic clients must declare a User-Agent header containing a company name and administrative contact email.
**SOURCE:** SEC, Webmaster FAQ (developers section), accessed 10 Nov 2026, https://www.sec.gov/os/webmaster-faq#developers
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** Hard-code a compliant User-Agent and a 10 rps limiter on day one. A generic or empty agent returns 403. Note a privacy point for a personal project: the SEC asks for a contact email, so use one you are content to have in server logs.

**CLAIM:** EDGAR full-text search runs at https://efts.sec.gov/LATEST/search-index with parameters q, forms, startdt, enddt, from and ciks; coverage begins in 2001; pagination is capped at 10,000 results; the endpoint is undocumented by the SEC; exceeding 10 rps reportedly causes roughly ten-minute IP blocks.
**SOURCE:** Orthogonal, "Reverse-Engineering SEC EDGAR's Full-Text Search API," accessed 10 Nov 2026, https://orthogonal.info/sec-edgar-full-text-search-api-efts-python/
**CONFIDENCE:** Secondary source (reverse-engineered, explicitly undocumented). The article contradicts itself on page size.
**IMPLICATION FOR THE BUILD:** Usable but unsupported — it can change without notice, so isolate it behind one adapter. More importantly, **the "Lazy Prices" filing-language-change signal does not need full-text search.** It needs consecutive filings' full text, which comes from the submissions API plus the Archives documents. Build it that way and the undocumented endpoint becomes optional.

**Sources for the nine Zhan et al. characteristics — honest assessment:**

| Characteristic | Source | Cost | Confidence |
|---|---|---|---|
| Cash holdings | EDGAR XBRL companyfacts | Free | High |
| Cash-flow variance | EDGAR XBRL, computed over history | Free | High |
| New share issuance | EDGAR XBRL | Free | High |
| Total external financing | EDGAR XBRL | Free | High |
| Profit margin | EDGAR XBRL | Free | High |
| Profitability | EDGAR XBRL | Free | High |
| Stock price | Any feed | Free | High |
| Distress risk | Computed from EDGAR + market data | Free | High (it is a formula, not a dataset) |
| **Analyst forecast dispersion** | **IBES via WRDS, or an unidentified paid API** | **$0 if CMU has IBES; otherwise unresolved** | **Low** |

**Eight of nine are free and reliable. One is a genuine open problem.**

---

## 5. FREE AND CHEAP ALTERNATIVES

**CLAIM:** The OpenBB Terminal was sunset because the team could not sustain a free open-source app with 500+ Python dependencies against vendors changing endpoints; the open-source Platform (Open Data Platform) continues and provides data through the user's own API keys. Workspace, the Snowflake Native App and Security are commercial.
**SOURCE:** OpenBB, "Sunsetting OpenBB Terminal: why, how, and what now," accessed 10 Nov 2026, https://openbb.co/blog/sunsetting-openbb-terminal-why-how-and-what-now/
**CONFIDENCE:** Verified on vendor page. Note the post is dated March 2024 and the product lineup is inferred from current site navigation.
**IMPLICATION FOR THE BUILD:** **OpenBB is an aggregation layer, not a data source.** It normalises access across providers you are already paying for. Its real value here is as insurance: if a vendor is dropped, the adapter changes rather than the pipeline. Its stated reason for sunsetting the Terminal is also the most useful warning in this report — maintaining many vendor integrations is the thing that kills personal finance-data projects. **Integrate as few vendors as possible.**

**CLAIM:** The current reliability status of yfinance could not be established from any authoritative source.
**SOURCE:** Searches returned only AI-generated comparison content and scraper-vendor marketing. No maintainer statement or issue tracker was reached.
**CONFIDENCE:** Could not verify.
**IMPLICATION FOR THE BUILD:** yfinance has a long history of intermittent breakage because it scrapes an undocumented endpoint, and the volume of "yfinance alternatives" marketing suggests continued instability. **Acceptable for exploratory notebooks; unacceptable in a pipeline that produces trading decisions,** and unacceptable for options chains where you need a trustworthy spread. Treat anything it returns as provisional.

**CLAIM:** Financial Modeling Prep and Finnhub pricing and response schemas could not be verified; both sites render these client-side.
**CONFIDENCE:** Could not verify.
**IMPLICATION FOR THE BUILD:** Both have free tiers and both are plausible homes for analyst estimate data. Worth 20 minutes of hands-on checking against the free tier rather than more desk research — a single API call will answer what the marketing pages will not.

**SEC Financial Statement Data Sets** (quarterly bulk extracts of all XBRL financial data) were not separately verified but are a free SEC product and a reasonable bulk alternative to companyfacts.zip. **Google Trends via pytrends** was not researched; it is unofficial, heavily rate-limited, and given that social scraping is being reconsidered anyway, it should be considered out of scope.

**News APIs:**

**CLAIM:** NewsAPI.org's Developer plan is free with 100 requests/day, 24-hour delayed articles, about one month of history, localhost-only CORS, and **no commercial use** — limited to development and testing, explicitly not staging or production including internal production. Business is $449/month with up to 5 years of history; Advanced is $1,749/month.
**SOURCE:** NewsAPI.org, "Pricing," accessed 10 Nov 2026, https://newsapi.org/pricing
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD — flagged terms issue:** The free tier forbids production use *including internal*. A personal tool that the developer runs daily on their own machine is arguably internal production, not development and testing. This is a genuine licensing ambiguity and the first terms problem in this report that the "it's just personal" framing does not clearly dissolve. Given 24-hour delay and one month of history make it nearly useless for this project anyway, **the clean answer is not to use it.**

**CLAIM:** Benzinga does not publish API pricing.
**SOURCE:** Benzinga, "Financial Data APIs," accessed 10 Nov 2026, https://www.benzinga.com/apis/
**CONFIDENCE:** Verified on vendor page that no price is published.
**IMPLICATION FOR THE BUILD:** Sales-gated pricing in this market reliably means institutional pricing. Deprioritise.

**Polygon.io news, Alpha Vantage NEWS_SENTIMENT:** **could not verify** — neither domain was fetchable.

**AlphaSense, Swaggy Stocks, Quiver Quantitative, Barchart Premier / OnDemand:** **could not verify.** Barchart and Quiver pages were not fetchable; Swaggy Stocks and AlphaSense were not reached within budget. Note that given the prior wave cut unusual options flow, the sentiment-adjacent products in this group (Swaggy Stocks, Quiver's WSB dataset) have lost most of their rationale and are not worth further budget.

---

## 6. COST TABLE

| Source | Cheapest usable tier | What you get | Limits | Personal-use terms |
|---|---|---|---|---|
| **CMU WRDS / OptionMetrics** | $0 (enrolment) | IvyDB US 1996+, EOD prices, IV, Greeks, vol surface | VPN off-campus; no automated site extraction | **Academic/non-commercial only — cannot feed live trading** |
| **IBKR OPRA L1** | $1.50/mo (waived at $20 commissions) | Real-time OPRA NBBO | 100 data lines; no expired-option history | Non-professional |
| **Tradier (Lite)** | $0 + brokerage acct | Option chains with Greeks, real-time | No expired-option history; 400 on quota | **Personal use is the default** |
| **Tradier Pro** | $10/mo | Above + $0 equity-option commissions | As above | Personal use default |
| **Tastytrade** | $0 + funded acct | Real-time REST quotes, positions, DXLink streaming | 100-symbol REST batch; Greeks unconfirmed | ToS not verified |
| **Alpaca Basic** | $0 | Indicative options feed | 15-min historical window; 200 WS subs | — |
| **Alpaca Algo Trader Plus** | $99/mo | OPRA feed, unrestricted historical | Options history only from Feb 2024 | — |
| **MarketData.app Free** | $0 | 24h-delayed chains **with IV and full Greeks**, 1 yr history | 100 credits/day | Internal use |
| **MarketData.app Starter** | $12/mo annual ($30 monthly) | 15-min delayed, 5 yr history, IV + Greeks | 10,000 credits/day | Internal use |
| **MarketData.app Trader** | $30/mo annual ($75 monthly) | **Real-time chains, IV + Greeks, unlimited history** | 100,000 credits/day | Internal use; real-time non-professional only |
| **ThetaData Value** | $40/mo | 6 yr history, 1-min intervals | 2 concurrent requests | **Individual = personal use only** |
| **ThetaData Standard** | $80/mo | 10 yr, tick data, chain snapshots, every OPRA NBBO quote | 4 concurrent | **Individual = personal use only** |
| **ORATS one-time** | **$599 once** | **2007–present EOD history with Greeks** | ~6,000 symbols | **Individual non-pro** |
| **ORATS recurring** | $99/mo | Ongoing historical data | — | Individual non-pro |
| **ORATS Delayed API** | $199/mo | EOD 2007+, strikes w/ Greeks, vol summaries, IV rank | 20,000 req/mo; no free trial | Individual non-pro |
| **Databento OPRA** | $0.04/GB + $125 credit | Tick/CBBO from 2013 | **No IV or Greeks** | Not stated |
| **CBOE DataShop** | Unpriced | Trades + NBBO + point-in-time IV/Greeks, 2012+ | Per-symbol/date purchase | No non-pro tier mentioned |
| **Intrinio Individual** | $150/mo | Core capital markets data incl. real-time options | — | Self-serve, instant |
| **SEC EDGAR** | $0 | Submissions, XBRL facts/frames, nightly bulk ZIPs | 10 rps; User-Agent required | No restriction |
| **EDGAR full-text search** | $0 | 2001+ full-text | 10,000-result pagination cap; **undocumented** | — |
| **OpenBB Platform** | $0 | Aggregation layer only | Bring your own keys | Open source |
| **NewsAPI.org Developer** | $0 | 24h-delayed news, 1 mo history | 100 req/day | **No commercial or production use — flagged** |
| **Options Analysis Suite Free** | $0 | 17 Greeks, chains, screeners, EOD index/ETF data, SEC/FINRA data, BYO-broker live | Not stated | Not stated |
| **Market Chameleon Premium** | $99/mo | Option trade/vol/earnings/chain downloads | **25 downloads per 24h; no API** | 7-day trial |
| **Unusual Whales** | $48/mo or $528/yr | Real-time flow, dark pool, GEX, REST API | WebSocket on a Pro tier, price unstated | Secondary source |
| **Polygon.io** | **Could not verify** | — | — | — |
| **Alpha Vantage / EODHD / Finnhub / FMP** | **Could not verify** | — | — | — |
| **Claude Haiku 5.5** | $0.10 / $0.50 per MTok | ≤100k-token prompts | Batch −50%; cache hit 0.01/MTok | — |
| **Claude Sonnet 5.5** | $2 / $10 per MTok | — | Batch −50%; cache hit $0.10/MTok | — |

---

## 7. THREE REFERENCE STACKS

### Stack A — Free / Minimal · **$0–12/month**

| Component | Choice | Cost |
|---|---|---|
| Fundamentals | SEC EDGAR bulk + XBRL | $0 |
| Filing-language change | EDGAR submissions + Archives | $0 |
| Options chains, Greeks, IV | MarketData.app Free (24h delayed) | $0 |
| Live chains + Greeks | Tradier Lite API (brokerage acct) | $0 |
| Positions / fills ledger | Tradier or Tastytrade | $0 |
| Backtest | **CMU WRDS / OptionMetrics** | $0 |
| Analytics / sanity-check | Options Analysis Suite Free | $0 |
| LLM | Claude Haiku 5.5 batched | ~$1–5 |
| Hosting | Local machine + cron | $0 |

**Can support:** the full capstone. Fundamentals, filing-change signal, a proper 1996+ delta-hedged-return backtest on OptionMetrics, live chain retrieval with Greeks, and a real outcome ledger from actual broker fills.

**Cannot support:** live trading informed by the WRDS-fitted model without crossing the academic-use line. Broad real-time scanning (Tradier Lite is fine for a short watchlist). Analyst dispersion if CMU lacks IBES. MarketData.app Free's 100 credits/day is roughly a handful of chains daily — enough to prototype, not to operate.

**Verdict: this is the right stack to start in, today, and it is the correct stack for the capstone deliverable.**

### Stack B — ~$100/month

| Component | Choice | Cost |
|---|---|---|
| Fundamentals + filings | SEC EDGAR | $0 |
| Real-time chains, IV, Greeks, history | **MarketData.app Trader** (annual billing) | $30 |
| Backtest data | **ThetaData Value** (6 yr) | $40 |
| Execution + OPRA quotes | IBKR OPRA L1 | $1.50 |
| Positions / fills | Tastytrade or Tradier | $0 |
| Tradier Pro (commission-free options) | optional | $10 |
| LLM | Claude Haiku 5.5 + Sonnet 5.5 for synthesis | ~$5–15 |
| Hosting | Small VPS | ~$6 |
| **Total** | | **~$93–103/month** |

**Can support:** everything in Stack A **plus a fully-licensed backtest that can legally inform live trading** — this is the key upgrade, not the extra data volume. MarketData.app Trader's 100,000 credits/day enables genuine scanning across a watchlist rather than spot checks, and IV and Greeks arrive pre-computed, removing a whole class of modelling error.

**Cannot support:** tick-level spread realism (ThetaData Value is 1-minute). Vol-surface fitting of OptionMetrics quality — you would fit your own surface from chains, which is a real piece of work. Intraday strategies.

**Alternative at the same price:** substitute **ORATS one-time $599** for the ThetaData subscription. After seven months the one-time purchase is cheaper, it includes Greeks already computed, it reaches back to 2007 rather than 2020, and you keep it forever. **For a project with a defined endpoint, the one-time purchase is the better buy.**

### Stack C — ~$500/month

| Component | Choice | Cost |
|---|---|---|
| Fundamentals + filings | SEC EDGAR | $0 |
| EOD history, Greeks, vol summaries, IV rank | **ORATS Delayed Data API** | $199 |
| Tick history + every OPRA NBBO quote | **ThetaData Standard** (10 yr) | $80 |
| Real-time chains with Greeks | MarketData.app Trader | $30 |
| Execution + OPRA | IBKR OPRA L1 | $1.50 |
| Broad real-time feed | Alpaca Algo Trader Plus | $99 |
| LLM | Sonnet 5.5, heavier use | ~$30–60 |
| Hosting | VPS + managed Postgres | ~$25 |
| **Total** | | **~$465–495/month** |

**Can support:** everything, including tick-accurate spread modelling, cross-vendor validation of the same signal on two independent datasets (which is genuinely valuable and is the main thing this tier buys), vol surface construction from ORATS SMV summaries, and a broad scanning universe.

**Cannot support:** OptionMetrics-grade surface quality. Any of this better than Stack B does for a single user on a monthly-horizon strategy.

**Honest verdict on Stack C: do not build it.** At ~$5,700/year it costs more than the expected edge on a personal account of plausible size, and it buys redundancy rather than capability. It is listed because the brief asked for it, not because it is recommended.

---

## 8. BUILD VS BUY VERDICT

**Recommendation: build, but build thin, and start by buying the free tier of something that already works.**

The reasoning:

**1. The things worth buying are mostly not for sale to you.** Unusual Whales ($48/mo, secondary source) sells options flow — which the prior wave already cut as non-viable in its retail form. Market Chameleon Premium at $99/month caps you at **25 downloads per rolling 24 hours and offers no API** (verified) — that is a human-browsing product, categorically unable to back a pipeline. Neither sells the thing this project is actually about: fundamental characteristics predicting delta-hedged option returns, ranked within a liquidity-qualified universe. **No commercial product implements the Zhan et al. signal family.** That is precisely why building is justified here, and it is a better justification than most build-vs-buy cases have.

**2. But one product is unusually well-positioned as a foundation.** Options Analysis Suite has a **genuinely free tier** including 17 Greeks, Black-Scholes pricing, options chain analysis, EOD data for major indexes and ETFs, options screeners, and SEC/FINRA/economic data — plus bring-your-own-broker-key live data via Tradier, Tastytrade, Public, Schwab or moomoo. Its **MCP server exposes 46 tools** (38 market/research/pricing, 6 synced-data, 2 platform-context) covering IV surfaces, dealer positioning, a 16-screen screener including IV rank and put skew, fundamentals, news, insider and institutional filings, and dark pool data. Critically, **the MCP server is not gated behind the separate API tier**, and it authenticates by OAuth with no separate key.
*Source: Options Analysis Suite, "MCP Server" and "Pricing," accessed 10 Nov 2026, https://www.optionsanalysissuite.com/developers/mcp and https://www.optionsanalysissuite.com/pricing. Pro and API tier prices are rendered client-side and **could not be verified**.*

**3. Therefore the recommended path is a hybrid, and the sequencing matters.**

- **Week 1:** Sign up for the Options Analysis Suite free tier and connect a Tradier or Tastytrade key. Before writing a line of code, use the MCP server interactively to find out what the data actually looks like, where the chains are thin, and what a realistic spread looks like on your candidate universe. This is the cheapest possible way to kill bad design assumptions.
- **Weeks 2–4:** Build the parts nobody sells — the EDGAR characteristic pipeline, the filing-language-change signal, the liquidity gate, the ranking logic, the outcome ledger. These are the capstone's intellectual content and they are all free to build.
- **Throughout:** Run the backtest on CMU's WRDS/OptionMetrics as academic work.
- **If and only if it goes live:** Buy ORATS' $599 one-time history, reproduce the backtest on it, and confirm the result survives the change of dataset. This simultaneously validates the signal and cleanly resolves the WRDS licensing constraint.

**4. What not to do.** Do not build a charting engine (TradingView and the broker platforms have solved this; the "visual layer" should be a thin rendering of your own computed levels, not a charting library project). Do not build a Greeks engine if MarketData.app ships them for $30/month. Do not integrate more than two or three vendors — OpenBB sunset its Terminal precisely because vendor-integration maintenance is unsustainable for a small team, and the developer is a team of one with a nine-week course and a day job's worth of other modules.

---

## 9. BLOCKERS

1. **WRDS cannot legally feed live trading.** The best dataset available is restricted to academic and non-commercial research. This does not block the capstone; it blocks the capstone becoming a trading system without a second, licensed dataset. **Mitigation: ORATS $599 one-time, reproduce and confirm.** Plan for this from the start rather than discovering it at the end.

2. **Analyst forecast dispersion has no confirmed cheap source.** It is available via IBES if CMU's WRDS subscription includes it (unconfirmed) and via LSEG commercially (quote-only). No free API was confirmed to carry it. **This is the one of nine characteristics that may simply not be obtainable** for live use. Mitigation: proxy by estimate range, or drop it and document the omission honestly — the latter is itself a legitimate capstone finding about the gap between academic and retail-obtainable signals.

3. **No broker provides historical options data.** IBKR, Tradier and Alpaca (pre-Feb 2024) all fail here, verified on vendor pages. Backtest data must be bought or obtained academically. This is the most common and most expensive wrong assumption in retail options projects.

4. **IBKR's 100 market-data-line default is a hard architectural constraint.** It scales only with account equity or commission volume, neither of which a student account will have. Any design that assumes broad real-time chain streaming on IBKR will fail at integration.

5. **Alpaca's options history begins February 2024** — roughly 33 monthly observations. Statistically insufficient for a monthly-horizon strategy, and drawn from a single unusual regime.

6. **Databento, ThetaData and Alpaca provide no computed Greeks or IV.** Local computation requires owning dividend and rate assumptions, and your Greeks will then differ from any broker's displayed Greeks — a reconciliation headache worth anticipating.

7. **The EDGAR full-text search endpoint is undocumented** and can change without notice. Isolate behind an adapter, or avoid by using the documented submissions API for the Lazy Prices signal.

8. **Schwab's current individual-developer API status is unresolved** — the developer portal was not reachable. Not a true blocker, since two free alternatives are verified working.

9. **NewsAPI.org's free tier forbids production use including internal use** — a flagged terms problem that the personal-use framing does not clearly resolve. Recommendation: do not use it.

10. **Polygon.io, Alpha Vantage, EODHD, Finnhub, FMP and Barchart pricing could not be verified.** Any of these might undercut the recommended stack; this report cannot say.

---

## 10. OPEN QUESTIONS

1. **Does CMU's WRDS subscription include IBES?** Highest-priority unknown. Check at first login. Determines whether analyst dispersion is obtainable at all.
2. **Does CMU's WRDS subscription include OptionMetrics by name?** Strongly implied by the A–Z description but not confirmed by title.
3. **Does Tastytrade's DXLink actually deliver the Greeks event for options?** Testable in minutes with a token; determines whether local Greeks computation is required.
4. **What does MarketData.app's "unlimited" historical options actually mean in practice** — what is the earliest retrievable chain date, and does the chain endpoint accept a historical date parameter? The docs page was not fetchable. This determines whether the $30/month Trader tier can *also* serve as the backtest source, which would collapse Stack B's cost substantially. **Highest-value remaining check.**
5. **What is CBOE DataShop's actual price** for, say, 30 symbols over five years with calculations?
6. **What does Options Analysis Suite Pro cost**, and does its backtesting tool handle the Zhan-style monthly rebalance?
7. **Does Schwab grant individual developers Market Data Production access** today?
8. **How large is a Databento OPRA CBBO-1m year** in GB for a 30-symbol universe? The $125 credit makes this free to answer.
9. **Does CMU WRDS access persist after enrolment ends?** Affects whether the capstone's backtest is reproducible later.
10. **Does the institutional subscription agreement add restrictions** beyond the base WRDS ToU?

---

## 11. RUNNING COSTS BEYOND DATA

**CLAIM:** Claude Haiku 5.5 is $0.10/MTok input and $0.50/MTok output for prompts up to 100,000 tokens, rising to $0.50/$2.50 above that threshold; Sonnet 5.5 is $2/$10; Opus 5.5 is $4/$20. The Batch API gives a 50% discount on both input and output. Cache hits cost 0.05x base input for Opus 5.5 and Sonnet 5.5, and 0.1x generally.
**SOURCE:** Anthropic, "Pricing," accessed 10 Nov 2026, https://platform.claude.com/docs/en/about-claude/pricing
**CONFIDENCE:** Verified on vendor page.
**IMPLICATION FOR THE BUILD:** Filing analysis is the LLM-heavy stage and it is far cheaper than intuition suggests. A 10-K runs roughly 100k–200k tokens. Processing a 30-name watchlist quarterly, at ~150k input and ~3k output per filing, is about 4.5M input and 90k output tokens per quarter. On **Haiku 5.5 with batching** that is roughly **$0.25 per quarter**. Even on Sonnet 5.5 batched it is about **$5 per quarter**. Prompt caching helps further if the same filing is queried repeatedly.

**Practical guidance:**
- **Use batching for everything that is not interactive.** Filing analysis is inherently asynchronous — nothing needs a filing summary within seconds. The 50% discount is free money here.
- **Route by stage, not uniformly.** Extraction and classification on Haiku; cross-filing synthesis and the final strategy rationale on Sonnet. Opus is not justified for this workload.
- **Watch the Haiku 100k threshold.** A full 10-K can cross it and quintuple the per-token price. Chunk filings below 100k tokens and the cheap tier applies — a meaningful optimisation that is easy to miss.

**Hosting:** Local machine with cron is genuinely sufficient for a single-user daily pipeline and costs $0. A small VPS ($5–10/month) buys reliability if the laptop sleeps. Managed Postgres (~$15–25/month) is worth it only once the outcome ledger matters enough to not lose. **Start local.**

**Local models as a substitute:** Realistic for the mechanical stages — document chunking, boilerplate stripping, section identification, and the text-similarity computation at the heart of the Lazy Prices signal, which needs an embedding model rather than a generative one and runs perfectly well locally for free. Not realistic for the judgement-dependent stages (synthesising a strategy rationale across filings, sector context and vol-surface position), where capability differences are large and the hosted cost is already measured in single-digit dollars. **The honest framing: local models save money on the stage that costs almost nothing, so the saving is not worth the operational complexity — except for embeddings, where local is simply the right answer.**

---

## 12. TOP 10 SOURCES

1. **CMU Libraries, PPIA Business research guide** — confirms WRDS access — https://guides.library.cmu.edu/PPIA/Business
2. **WRDS Terms of Use** — the academic/non-commercial restriction that shapes the whole architecture — https://wrds-www.wharton.upenn.edu/users/tou/
3. **Interactive Brokers, Market Data Pricing** — OPRA L1 at $1.50/mo non-professional — https://www.interactivebrokers.com/en/pricing/market-data-pricing.php?menu=B
4. **IBKR TWS API, Historical Data Limitations** — no expired-option history; the key disqualifier for broker-based backtesting — https://interactivebrokers.github.io/tws-api/historical_limitations.html
5. **ThetaData Pricing** — $40/$80/$160 individual tiers with explicit personal-use licensing — https://thetadata.net/pricing
6. **ORATS individual pricing** — the $599 one-time 2007-present history — https://orats.com/reddit
7. **MarketData.app Pricing** — free tier with Greeks and IV; $30/mo real-time Trader tier — https://www.marketdata.app/pricing/index.md
8. **SEC EDGAR Application Programming Interfaces** — free, keyless fundamentals — https://www.sec.gov/search-filings/edgar-application-programming-interfaces
9. **Options Analysis Suite MCP Server** — 46 tools, free tier, BYO-broker-key — https://www.optionsanalysissuite.com/developers/mcp
10. **Anthropic Pricing** — LLM cost basis for the filing-analysis stage — https://platform.claude.com/docs/en/about-claude/pricing

**Runners-up:** WRDS OptionMetrics vendor page (https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics); Tradier Docs Market Data (https://docs.tradier.com/docs/market-data); Alpaca About Market Data API (https://docs.alpaca.markets/us/docs/about-market-data-api.md); Databento Options (https://databento.com/options); Tastytrade Developer docs (https://developer.tastytrade.com/docs/).
