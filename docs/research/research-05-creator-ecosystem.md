# Strand 05 — The Creator, Educator, and Practitioner Ecosystem

**Research date:** 10 November 2026
**Scope:** What US retail options traders are *taught*, what they *expect* a tool to do, and what *vocabulary* they use.
**Framing constraint, stated up front and repeated throughout:** almost everything in this report is **evidence of market demand and user expectation, not evidence of efficacy.** A strategy being heavily marketed, or a term being widely used, says nothing about whether it makes money. Where independent or empirical evidence exists, it is labelled as such and it is mostly *unfavourable* to the marketed claims.

---

## METHOD AND EVIDENCE LIMITATIONS (read before the findings)

**1. I cannot watch video, and I did not read transcripts.** This is the single largest limitation. The retail options education ecosystem is overwhelmingly video-native (YouTube, tastylive's live daily programming, Discord voice rooms). My evidence about video creators comes from:
- channel and episode **titles** and show-level blurbs on tastylive.com (I fetched these; tastylive's episode pages contain titles and dates only, with no written summaries — I verified this on one episode page and found no text body);
- **course sales pages** (projectfinance/Teachable, SMB Training support pages, Unusual Whales pricing, Whop server listings);
- **third-party written reviews and directory listings** (FeedSpot, Benzinga, NexusFi, Medium, Trustpilot-adjacent pages);
- **Reddit and forum discussion** read through public mirrors (redlib/libreddit instances, r.datuan.dev, reddit.sentinel-team.org).

I did **not** read a single video transcript. Therefore: **I make no claims about what any educator says inside a video.** Where I describe a methodology, it is because the creator stated it in *writing* on a sales page, definitions page, or support article, or because a written third-party source attributed it to them. I flag each instance.

**2. Search budget was cut off.** The turn's shared web-search budget (200 calls across five parallel agents) was exhausted after ~24 of my planned 30–45 searches. I compensated with ~27 targeted page fetches against URLs already surfaced. Gaps this created are listed in OPEN QUESTIONS. Specifically unresearched: Market Rebellion / Najarian-style unusual-activity marketing scrutiny; the exact text of the December 2025 SEC alert on AI-sourced trade recommendations (I have it only second-hand); CFTC Rule 4.41 / SEC Rule 156 hypothetical-performance disclaimer norms as a primary source.

**3. The space is badly polluted by SEO and AI-generated content.** A large fraction of search results for every strategy term were thin affiliate or AI-written explainers on domains with no track record (fattail.ai, tradealgo.com, tradersagency.com, optionspilot.app, tapeboard.com, thetaloop.app, apexvol.com, dozens of `*.pages.dev` sites). **This is itself a finding** — see Finding 22. I did not treat any of these as evidence and have excluded them from sourcing except where noted as examples of the pollution.

---

## FINDINGS

### A. THE STRATEGY CANON BEING SOLD

---

**CLAIM:** The wheel (cash-secured puts → assignment → covered calls) is the single most-taught retail premium-selling strategy, and the community teaches it with a specific, numerically precise mechanical ruleset.
**SOURCE:** r/thetagang, "The Wheel Strategy — An In-Depth Overview," July 2024, read via libreddit mirror — https://lr.eu.psf.lt/r/thetagang/comments/1e6g9v2/the_wheel_strategy_an_indepth_overview
**EVIDENCE TYPE:** Demand signal
**EVIDENCE STRENGTH:** Strong (for the existence and shape of the demand; nothing about efficacy)
**DETAIL:** The canonical community ruleset, as written: open CSPs at 45–60 DTE (30 DTE acceptable); ~0.30 delta as the default strike, explicitly described in the post as "roughly a 30% chance of expiring in the money"; close at ~50% of credit collected; roll only for a net credit and not too far out in time; manage/roll around 21 DTE; covered calls only above cost basis; position sizing ≤20% of capital for small accounts, 5–10% per trade for large accounts; avoid selling through earnings as a beginner; only wheel stocks you actually want to own. Commenters supplied variants: one described 25 delta / 45 DTE / 50% take-profit / roll at 21 DTE; another proposed closing when the remaining premium's annualised decay rate falls below the trade's original return rate. Notably the post gives **no IV-rank guidance at all**, only a warning against chasing high-IV names for fat premium.
**IMPLICATION FOR THE APP:** This is the de facto spec for a "wheel candidate" feature. If the app's contract selector cannot express *delta target, DTE window, take-profit %, roll trigger DTE, and a "would I own this?" filter*, it will not feel native to this audience. The 0.30-delta default and the 45 DTE default are the strongest conventions in retail options; the app should expose them as presets. **But note the post itself equates 0.30 delta with "30% chance of expiring ITM" — that is the delta-as-probability error, embedded in the most-upvoted community explainer.** See Finding 14.

---

**CLAIM:** The wheel's marketed "triple income" framing has a documented accounting problem: practitioners publicly report collected premium while leaving assigned-stock losses unrealised, which inflates apparent performance.
**SOURCE:** Karsten Jeske (Early Retirement Now), "The Wheel Strategy Doesn't Work — Options Series Part 12," 17 September 2024 — https://earlyretirementnow.com/2024/09/17/the-wheel-strategy-doesnt-work-options-series-part-12/
**EVIDENCE TYPE:** Independent scrutiny
**EVIDENCE STRENGTH:** Moderate (reasoned critique with historical data; the author explicitly declines to run a formal wheel backtest, so it is not an empirical refutation)
**DETAIL:** The critique has five limbs: (1) the wheel's delta rises toward 1.0 as the underlying falls, so it is a *growing* long bet exactly when it hurts — fine in choppy V-shaped markets, bad in prolonged downtrends; (2) post-WW2 bear markets averaged ~1.3 years with ~3.6-year recoveries, and 2000–2013 was mostly underwater with little call premium to harvest, so the 2020/2022 fast recoveries that built the strategy's reputation are unrepresentative; (3) two identical investors can end with wildly different net deltas purely from assignment history, which the author calls logically inconsistent; (4) influencers can report $2,000 premium against $3,000 unrealised stock losses and claim a $2,000 profit — he compares this to Enron-style accounting; (5) the strategy quietly requires stock-picking skill, citing RIDE, PTON and ARKK as names that never came back. The same author separately argues premium selling is "nickels in front of a steamroller" rather than a benign income stream (https://earlyretirementnow.com/2019/09/11/ubs-another-option-strategy-failure/).
**IMPLICATION FOR THE APP:** **This is the most important single design constraint in this strand.** If the app scores a wheel/CSP contract 0–100 on premium yield and probability-of-expiring-OTM, it will reproduce exactly the accounting error this critique names. The app should compute and display **total position P&L including unrealised stock mark**, and should surface **current net delta of the whole wheel position**, not just the premium captured on the open leg. A scoring model that cannot see the assigned-shares drawdown is not measuring the thing the user cares about.

---

**CLAIM:** Premium-selling communities are themselves actively debating whether the wheel is inferior to defined-risk alternatives, and whether its returns beat simply holding the index.
**SOURCE:** r/thetagang front page and 12 January 2026 snapshot — https://r.datuan.dev/r/thetagang and https://reddit.sentinel-team.org/subreddits/thetagang/snapshots/2026-01-12T07%3A50%3A47.362601Z
**EVIDENCE TYPE:** Demand signal / community scrutiny
**EVIDENCE STRENGTH:** Moderate (community sentiment, not analysis)
**DETAIL:** Recurring January 2026 threads: "Question for Wheelers: Why Not Just Run Iron Condors?" plus a Part 2 — the argument being that condors cap downside and need far less collateral, and that the wheel's "at least you still own something" consolation fails after a large drop. A separate front-page thread argued wheel returns barely beat SPY. Another thread was from a self-described non-seller asking how active sellers *actually* manage risk — i.e. demand for a risk view the existing tools do not give them.
**IMPLICATION FOR THE APP:** The audience will accept, and may reward, a tool that compares a proposed structure against (a) the defined-risk alternative on the same underlying, and (b) buy-and-hold. A "versus just owning SPY" line on every income trade is a credibility feature, not a hostile one.

---

**CLAIM:** Credit spreads and iron condors are marketed as "high probability" income trades; the structurally negative skew (high win rate, large tail loss) is the standard critique.
**SOURCE:** Taleb distribution concept (https://en.wikipedia.org/wiki/Taleb_distribution); Early Retirement Now, "Another Option Strategy Failure," 11 September 2019 (https://earlyretirementnow.com/2019/09/11/ubs-another-option-strategy-failure/); Benzinga, "Picking Up Pennies In Front Of A Steamroller," April 2024 (https://benzinga.com/z/38086212)
**EVIDENCE TYPE:** Independent scrutiny
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION FOR THE APP:** A 0–100 score for a credit spread that is driven by win probability is actively misleading. Any score for a short-premium structure must be accompanied by **max loss, loss-to-credit ratio, and the number of consecutive wins needed to recover one max loss.** That last number is a single integer and it is the most honest thing the app can show a premium seller.

---

**CLAIM:** An independent 11-year backtest of a tastytrade-attributed credit-spread ruleset found a 61% win rate but negative total returns across all tested allocations.
**SOURCE:** SJ Options, "Tastytrade Credit Spreads, 11 Year Backtest," 7 February 2016 — https://www.sjoptions.com/tastytrade-credit-spreads-do-they-work/
**EVIDENCE TYPE:** Independent scrutiny (contested)
**EVIDENCE STRENGTH:** **Weak.** Material caveats: the author sells competing options education and software (OptionColors) and closes the post soliciting business, so there is a direct commercial conflict; the rules are attributed to tastytrade without citation and may not match its actual published methodology; only SPX and one ruleset were tested; no drawdown, trade count, average win/loss, annualised return or benchmark is reported; commissions/slippage treatment is undisclosed; and the post is from 2016 with no update.
**DETAIL (as reported, treat as unverified):** Rules tested — sell credit = 1/3 spread width, enter at 45 DTE, IV Rank 50–100, take profit at 50% of credit, stop at 2× credit. Result: 61% winners, 7 of 11 years losing, total 11-year returns of −7% / −19% / −56% / −93% at 5% / 10% / 25% / 50% capital allocation.
**IMPLICATION FOR THE APP:** Useful mainly as a *shape* result: a 61% win rate coexisting with negative returns is the exact failure mode a win-rate-weighted score produces. Do not cite this number to users as fact — it is one conflicted vendor's unreplicated test.

---

**CLAIM:** The "manage winners at 50% of max profit" rule — one of the most widely repeated mechanical rules in retail options — did not add value in an independent SPX short-strangle backtest.
**SOURCE:** SteadyOptions, "Does 'Managing Winners' Add Value to Short Strangles?" (author backtest, reader comments dated November 2020) — https://steadyoptions.com/articles/does-%E2%80%9Cmanaging-winners%E2%80%9D-add-value-to-short-strangles-r618/
**EVIDENCE TYPE:** Independent scrutiny / quasi-empirical
**EVIDENCE STRENGTH:** Moderate (real backtest, disclosed assumptions, but single underlying, end-of-day data, no slippage or commissions, and a competing-educator author)
**DETAIL:** 16-delta SPX short strangles, 2001 to May 2020, end-of-day data, no slippage/commissions. 45 DTE entry with 50%-of-credit-or-21-DTE exit: CAGR 4.44%, vol 8.62%, Sharpe 0.52. 30 DTE entry with 5-DTE exit (no profit target): CAGR 5.46%, vol 8.19%, Sharpe 0.67. A 25/16-delta bullish variant with 5-DTE exit: CAGR 6.30%, vol 9.93%, Sharpe 0.63. The author attributes divergence from educators' claims to data and methodology differences and does not name tastytrade — **the tastytrade attribution appears only in a reader comment and is unverified.**
**IMPLICATION FOR THE APP:** If the app ships a "take profit at 50%" default (and it probably should, because users expect it), it should be labelled as a **convention**, not an optimum. Offering the alternative (hold to a DTE-based exit) as a comparable preset is cheap and differentiating.

---

**CLAIM:** 0DTE is the dominant index-options flow and the fastest-growing retail strategy; retail traders lose money on it in aggregate.
**SOURCE (empirical):** Beckmeyer, Branger, Gayda et al., "Retail Traders Love 0DTE Options… But Should They?" — conference version at https://wp.lancs.ac.uk/fofi2024/files/2024/04/FoFI-2024-146-Leander-Gayda.pdf
**SOURCE (volume):** SpotGamma 0DTE hub, dated 18 August 2026 — https://spotgamma.com/0dte/
**EVIDENCE TYPE:** Empirical study (losses); vendor-reported market data (volume)
**EVIDENCE STRENGTH:** **Strong** for the loss finding; Moderate for the volume figures (vendor page, internally inconsistent dates)
**DETAIL (empirical):** Cboe transaction-level SPX option data, February 2021 – September 2023, retail identified via SLAN/MLAT price-improvement codes. 0DTE was >75% of retail SPX option volume for most of 2022 and all of 2023. Retail lost **>$125 million** in aggregate, of which **>$90 million was transaction costs**. Average ~$241k/day over the full sample, rising to ~$350k/day after daily expirations began 16 May 2022. Single-leg positions account for >$100m of the losses; multi-leg losses plateaued from early 2023. Median margin-adjusted returns: single puts ~−0.7%, single calls ~−0.8%; put spreads ~+3%, call spreads ~+3.3% median but with averages dragged negative by a few large losses. Retail actually gets *better* effective spreads than non-retail (≈6.0% vs 12.5% for calls; 5.0% vs 9.6% for puts) — costs still dominate. Figures exclude commissions and clearing fees, so the authors call them conservative. Conclusion as published: 0DTE options are on average not a lucrative vehicle for retail.
**DETAIL (volume, vendor):** SpotGamma reports 0DTE at ~20% of SPX volume in 2020, crossing 50% by 2024, and cites Cboe for approaching 63% of total SPX volume as of February 2026. The page is internally inconsistent (elsewhere says "mid-2026"), so treat the precise figure as soft.
**IMPLICATION FOR THE APP:** Three things. (1) **Single-leg 0DTE is the worst-performing retail behaviour in the strongest dataset available, and it is also the most-demanded.** If the app proposes 0DTE single legs it is steering users into the documented loss centre. (2) The median-vs-mean split for spreads is a design gift: the app can legitimately prefer defined-risk 0DTE structures over single legs on evidence, not vibes. (3) Transaction costs are >70% of the documented retail 0DTE loss — a scoring model that ignores bid-ask spread and slippage is omitting the dominant term. **Spread cost must be a first-class input to the 0–100 score, not a footnote.**

---

**CLAIM:** 0DTE is now taught with a dealer-gamma mental model (GEX, gamma walls, gamma flip, "pin or pop"), and vendors that teach it do state explicit risk caveats including that most retail 0DTE traders lose money.
**SOURCE:** SpotGamma, "0DTE Options: The Complete Guide," page dated 18 August 2026 — https://spotgamma.com/0dte/
**EVIDENCE TYPE:** Marketing claim (methodology) with vendor-stated caveats
**EVIDENCE STRENGTH:** Marketing claim only, for the efficacy of the setups
**DETAIL:** Taught setups: a "pin trade" (iron condor or butterfly around a gamma wall on positive-GEX days), a negative-gamma breakout (debit spreads after a confirmed level break), and a gamma-flip trade. A late-day framework decides by ~2:00–3:30pm ET whether it's a pin or a pop day. Stated risk rules: 1–2% of capital per trade, 2–3 trades/day max, stop after a 3–5% daily loss, exit by 3:30pm, don't average down, prefer defined risk, SPY has assignment risk while SPX is cash-settled. The page states plainly that most retail 0DTE traders lose money and that total loss within minutes is possible. It describes GEX as "a volatility-regime map, not a forecast of direction."
**IMPLICATION FOR THE APP:** The vocabulary is non-negotiable if the app touches 0DTE: **GEX, gamma wall, gamma flip, pin, positive/negative gamma regime.** The honest-vendor framing ("regime map, not a direction forecast") is a usable template for how the app should describe its own trend classifier. Note that the strongest-selling 0DTE vendors sell *context*, not picks — see Finding 25.

---

**CLAIM:** Earnings/IV-crush trading is a mainstream taught strategy, and the strongest empirical finding is that retail systematically overpays for options into high-expected-volatility earnings events.
**SOURCE:** de Silva, Smith & So, "Losing is Optional" — summarised by Quantpedia, "How Retail Loses Money in Option Trading" — https://quantpedia.com/how-retail-losses-money-in-option-trading/
**EVIDENCE TYPE:** Empirical study (read via a secondary summary; I did not read the paper itself)
**EVIDENCE STRENGTH:** Moderate-to-Strong finding, but **Moderate** confidence because my reading is second-hand and the summary did not state the sample period or firm count
**DETAIL:** Retail loses ~5–9% around earnings announcements on average and ~10–14% around high-expected-announcement-volatility (EAV) events. For high-EAV events, retail collectively loses roughly $60,000 per average event (~10% of the investment) over the following 10 days, before transaction costs. The summary estimates ~$1.5bn transferred from retail to other participants over the sample window. Mechanism: retail bids option prices *up* ahead of events where large moves are expected, and average spreads are ~20% of the option price and widen further pre-event. Retail also *holds* after the event despite no elevated post-event realised vol — consistent with a disposition effect. Market makers are the main counterparty and beneficiary. Retail demand concentrates in firms with prior media coverage.
**IMPLICATION FOR THE APP:** A news/sentiment feature that surfaces heavily-covered names into an earnings window is, on this evidence, pointing users at the single worst documented retail entry. If the app does earnings, it should display **implied move vs. historical realised move** and an explicit "options look expensive / cheap relative to history" read, and should default to warning rather than encouraging long premium into a high-IV event. The "Earnings Calendar By Implied Move" posts that recur on r/thetagang (seen on both the front page and the Jan 2026 snapshot) are direct evidence that this exact artefact is already in demand.

---

**CLAIM:** LEAPS and the poor man's covered call (PMCC / long-call diagonal) are an established capital-efficiency pitch aimed explicitly at small accounts.
**SOURCE:** r/thetagang discussion (both snapshots, PMCC and LEAPS recur); projectfinance course page (LEAPS Growth Strategy, "Hypergrowth" strategy, tradable in $2,500–$5,000 accounts) — https://optionsforbeginners.teachable.com/p/data-driven-options-strategies; SMB Training "The Rhino Options Strategy," a positive-theta course — https://support.smbtraining.com/support/solutions/articles/44000879018-what-training-programs-do-you-offer-
**EVIDENCE TYPE:** Demand signal / Marketing claim
**EVIDENCE STRENGTH:** Strong for demand; Marketing claim only for the edge
**IMPLICATION FOR THE APP:** PMCC is a two-legged, two-expiry structure. Supporting it means the app's contract selector must handle **a long LEAP and a short near-dated call as one position, with combined delta/theta and a breakeven that moves.** This is meaningfully harder than single-leg scoring and is a real scope decision.

---

**CLAIM:** "Unusual options activity" / "following the smart money" is a large commercial category sold at $50–$120/month retail, and the leading vendor's own pricing page makes no predictive claim.
**SOURCE:** Unusual Whales pricing page — https://unusualwhales.com/pricing
**EVIDENCE TYPE:** Demand signal / Marketing claim
**EVIDENCE STRENGTH:** Strong for the demand and the price points
**DETAIL:** Free tier gives delayed data (flow delayed 2 trading days, news 15 min, alerts 30 min) plus Discord. Retail Basic $50/mo (or $42/mo annually, $504/yr): real-time flow, GEX heatmap, SPX market-maker exposure at 10-minute updates, "Mr. Whale" AI with basic usage limits, politician trades, daily options and dark-pool data downloads, "Unusual Predictions," screener, 25 alerts, 5 watchlists, 5 dashboards, Greeks and volatility dashboards, profit calculator, institutional holder and insider data. Retail Pro $75/mo (most popular) unlocks unlimited alerts/watchlists/dashboards and 2× AI usage. Retail Max $120/mo adds 1-minute GEX Periscope and 1-minute SPX MM updates and 3× AI usage. Disclaimers are thin: "Not financial advice," "Results may vary; trading involves risk." **No scoring feature is advertised, and the page does not claim the flow data is predictive.**
**IMPLICATION FOR THE APP:** Two readings. (a) **Price anchor:** $50–$75/month is the established retail willingness-to-pay for an options data product, with $42/mo as the annual-discount floor. (b) **Whitespace:** the category leader sells *raw flow plus filters*, and explicitly does not score contracts. A 0–100 score is therefore differentiated — and also unvalidated by any incumbent, which cuts both ways. Note the tiering model (unlimited alerts as the main paid unlock) is worth copying.

---

**CLAIM:** The "tastytrade approach" — mechanical, high-occurrence, small-size premium selling — is publicly documented in its written definitions and concept pages, and those pages give concrete numeric thresholds.
**SOURCE:** tastylive, "What Is Implied Volatility (IV) Rank…" — https://www.tastylive.com/definitions/iv-rank-iv-percentile; tastylive, "How to Calculate Probability of Profit When Trading Options" — https://www.tastylive.com/concepts-strategies/probability-of-profit; tastytrade platform support, "Probability of Profit (POP & ePoP)" — https://tastyworks.freshdesk.com/support/solutions/articles/43000530527-probability-of-profit-pop-epop-
**EVIDENCE TYPE:** Marketing claim / publicly stated methodology
**EVIDENCE STRENGTH:** Strong that these are the stated thresholds; **Marketing claim only** for the claimed edge
**DETAIL — what is publicly stated in writing:** IV Rank compares current IV to the 52-week high/low on a 0–100 scale; IV Percentile is the share of the last 52 trading-day sessions with IV below current. Thresholds given: IVR >50 is elevated, ≥80 extreme, <20 may favour buying; IVP 0–30% suggests cheap options, ≥70% elevated. Guidance: IVR above 50 favours selling volatility, well below 50 favours buying, justified by IV mean reversion with the caveat that profit is not guaranteed. Low readings → defined-risk or long-option strategies; high readings → short premium or IV-contraction trades; buyers often look for IVR ≤20.
**DETAIL — what is paywalled or video-only:** The quantitative studies themselves. tastylive's research arm publishes episodes under *Market Measures*, *Options Jive*, *The Skinny on Options Math* and *From Theory to Practice* with highly specific titles — e.g. "Mega Strangle Study," "Premium: Why Selling It Works" (23 Oct 2014), "Mechanical Strategies: Trading A Strangle Portfolio" (25 May 2016), "Testing Probability of Touch," "How Is Probability of Profit Calculated" (10 Apr 2014), "Probability of Profit May Be Deceiving" (29 Oct 2024). **I fetched one of these episode pages and confirmed it contains only a title, a date, and a show-level blurb — no written methodology, no data tables, no sample description.** So the claims are *titled* as testable and are *not* testable from public written material.
**IMPLICATION FOR THE APP:** IV Rank with the 50 / 80 / 20 thresholds is the single most citable convention in retail options and the app should implement it exactly, with IV Percentile as an alternate. But the app should **not** cite tastytrade studies as evidence for anything, because their methodology is not in writing. If the app wants to claim an IV-rank-conditioned edge, it has to test it itself.

---

**CLAIM:** The industry-standard "Probability of Profit" metric that retail traders read off broker platforms is a thinly-documented model output, and the leading educator's own explainer of it contains no formula and no risk-neutral caveat.
**SOURCE:** tastylive concepts page and tastytrade platform support article (URLs above)
**EVIDENCE TYPE:** Independent scrutiny (my reading of their primary documents)
**EVIDENCE STRENGTH:** Strong (direct reading of the vendor's own pages)
**DETAIL:** The educational page defines POP as "the chance of making at least $0.01 on a trade" and then gives only heuristics: sold OTM/ATM strikes "better than 50%," debit spreads with breakeven near spot "around 50% or just a bit better," a covered call turns a "50/50 coin flip" into a higher-probability trade. **No formula, no model, no data source, and no statement that POP is a risk-neutral/model-implied quantity rather than a real-world probability.** The platform support article is more candid: POP and portfolio-level ePoP are built by generating a P&L graph and applying a distribution curve taken from the **beta-weighted symbol, defaulting to SPY**, and its volatility index; for mixed expirations it uses the longest-dated option's curve; the profit region's area under a unit-total curve gives the number. It does not name the statistical model. ePoP excludes futures and futures options.
**IMPLICATION FOR THE APP:** **Material.** If the app shows a POP-like number, it is showing a number whose own originators document loosely and whose default distribution is borrowed from SPY. The app has a real opportunity here: show POP *and* disclose the model, the volatility input, and the assumption. Saying "this is computed from implied volatility under a risk-neutral assumption and is not a forecast of real-world odds" is a two-line disclosure that no incumbent appears to make in its educational material, and it is the kind of thing that buys credibility with the sceptical half of this audience. See Finding 15.

---

### B. THE VOCABULARY AND ITS EMBEDDED ERRORS

---

**CLAIM:** Delta is near-universally used by retail as a probability of expiring in the money, including in the most-upvoted community explainers — and it is not one.
**SOURCE (usage):** r/thetagang wheel overview (0.30 delta = "roughly a 30% chance of expiring in the money") — https://lr.eu.psf.lt/r/thetagang/comments/1e6g9v2/the_wheel_strategy_an_indepth_overview ; tastylive episode titled "3 Ways To Use Delta Probability Approximation" (2 Oct 2025, title only — https://www.tastylive.com/shows/from-theory-to-practice/episodes/3-ways-to-use-delta-probability-approximation-10-02-2025); r/options wiki links a resource titled "Delta of Calls vs. Puts and Probability of Expiring In the Money" but contains no prose on it — https://r.datuan.dev/r/options/wiki/faq
**SOURCE (correction):** Freeport Logbook, "Options Implied Distributions are NOT Real-World Distributions" — https://freeportlogbook.substack.com/p/options-implied-distributions-are
**EVIDENCE TYPE:** Demand signal (usage) + technical correction
**EVIDENCE STRENGTH:** Strong
**DETAIL:** Delta is ∂V/∂S — a hedge ratio. It approximates the *risk-neutral* probability of finishing ITM, not the real-world one. The drift term μ drops out of option pricing entirely, so the option chain carries no direct information about expected return. Under the risk-neutral measure every asset is treated as drifting at the risk-free rate, which folds the risk premium into the probabilities; the practical effect is that risk-neutral probabilities **tilt toward bad outcomes and overstate downside** relative to real-world odds. The source notes the approximation is least bad over short horizons (e.g. around earnings) and worst over LEAPS horizons of 1–2 years.
**IMPLICATION FOR THE APP:** This is the central "mirror the error or correct it" decision. My recommendation: **mirror the vocabulary, correct the semantics in the tooltip.** Label the field "Delta (≈ chance of finishing ITM)" so it is findable and familiar, and put the one-sentence correction behind the hover: *delta approximates the market-implied chance, which embeds a risk premium and is not a real-world forecast; the approximation degrades at long horizons.* Do not rename the field — users will not find it. Do not silently repeat the error — the sceptical cohort will catch it and it is exactly the kind of thing that gets a tool dismissed on r/options.

---

**CLAIM:** The same risk-neutral-vs-real-world error propagates into "probability of profit," which retail reads as a real-world likelihood.
**SOURCE:** Freeport Logbook (above); tastylive's own episode title "Probability of Profit May Be Deceiving," 29 October 2024 (title only — https://www.tastylive.com/shows/options-jive/episodes/probability-of-profit-may-be-deceiving-10-29-2024)
**EVIDENCE TYPE:** Technical correction; the tastylive item is a title-only signal that the industry itself acknowledges the problem
**EVIDENCE STRENGTH:** Strong for the technical point; Weak for what tastylive actually says (I could not read it)
**IMPLICATION FOR THE APP:** If the app's 0–100 score is built on POP or on delta-derived probabilities, **the score inherits a systematic optimism/pessimism bias that is a function of the variance risk premium.** This is a modelling issue, not just a labelling one. At minimum, do not present the score as "probability of making money."

---

**CLAIM:** "Max pain" is in active retail use as a price-magnet theory; even vendors who publish the calculation state it is unproven.
**SOURCE:** Max-pain explainer served under SpotGamma's support domain — https://support.spotgamma.com/hc/en-us/articles/12772191681299-Max-Pain-Theory-Explained (note: the page content I received was a generic explainer and did not itself reference SpotGamma, so attribute cautiously); See It Market, "The Limitations of Max Pain Theory For Options Traders" — https://seeitmarket.com/?p=58883; r/GME, "The concept of max pain and why this is probably…," March 2021 — https://lr.eu.psf.lt/r/GME/comments/mejp0k/the_concept_of_max_pain_and_why_this_is_probably
**EVIDENCE TYPE:** Demand signal + vendor-stated caveat
**EVIDENCE STRENGTH:** Moderate for demand; the efficacy claim is **Marketing claim only** and is disclaimed even by its publishers
**DETAIL:** Calculation as published: for each strike, multiply intrinsic value by open interest for calls and puts and sum; the strike with the highest total is "max pain." The page states the theory is controversial, has not been shown to be consistently accurate, and that relying on it alone is difficult because prices are driven by many non-options factors.
**IMPLICATION FOR THE APP:** If the app uses open interest as a scoring input (it plans to), users will expect to see max pain and will interpret OI concentration as a price magnet. Show OI-by-strike because it is genuinely informative about liquidity and dealer positioning; if you show max pain, show it with the caveat. Do not let it carry weight in the score.

---

**CLAIM:** Options-specific slang is largely absent from the general meme-stock glossaries, which are a poor guide to the vocabulary this app needs.
**SOURCE:** r/wallstreetbets wiki glossary — https://lr.vern.cc/r/wallstreetbets/wiki/glossary
**EVIDENCE TYPE:** Demand signal (negative)
**EVIDENCE STRENGTH:** Moderate
**DETAIL:** The official WSB glossary has **no entries for any Greek, for implied volatility, for assignment, or for order flow.** It defines trading vs investing, binary events, PDUFA, "Farmers' Delight," bagholder, bullish/bearish, bid/ask and spread (bid-ask only — it does not mention that "spread" also means a multi-leg structure). Several definitions are loose: "binary event" is applied to earnings, whose outcomes are continuous; PDUFA dates are described as approval deadlines when they are FDA performance-goal dates that do not guarantee approval; bid/ask are described as maximum/minimum willingness rather than the best currently-posted quote.
**IMPLICATION FOR THE APP:** The real working vocabulary comes from r/options and r/thetagang, not r/wallstreetbets. WSB is an *audience-size* signal and a culture signal; it is not a vocabulary source. Also: the app's own glossary is a differentiator, because the community's canonical one is this bad.

---

**CLAIM:** The Pattern Day Trader rule — a core piece of retail vocabulary and a hard constraint on multi-leg trading in small accounts — was eliminated by SEC-approved FINRA rule changes in 2026.
**SOURCE:** Charles Schwab, "SEC Approves Scrapping $25,000 Day Trader Minimum" — https://www.schwab.com/learn/story/sec-approves-scrapping-25000-day-trader-minimum ; corroborated by Ridley Law Offices (https://ridleylawoffices.com/0dte-options/) and tastylive's pre-change commentary (https://www.tastylive.com/news-insights/finra-relaxing-regulations-pattern-day-trading)
**EVIDENCE TYPE:** Regulatory fact (secondary sources; **flag for the regulatory strand to verify against the FINRA rule filing and SEC approval order**)
**EVIDENCE STRENGTH:** Moderate-to-Strong (two independent brokerage/legal sources agree on the date and substance; I did not read the primary filing)
**DETAIL:** SEC approved 14 April 2026. The $25,000 minimum for frequent margin day trading is eliminated; the PDT designation is removed and day trades are no longer counted. Replacement: eligible margin accounts above $2,000 get intraday buying power set by each brokerage based on current positions and maintenance margin. Firms may monitor for margin shortfalls in real time or with a single end-of-day check; real-time monitors can block trades that would create an intraday deficit. Rules effective **4 June 2026**, with brokerages given until **20 October 2027** to implement. Schwab said it would stop counting day trades from 8 June 2026 and open no new PDT accounts from that date. **Critically for this app:** under the *old* regime each leg of a multi-leg options strategy counted as a separate day trade, so closing an iron condor same-day counted as four — which is why sub-$25k accounts could not trade condors or 0DTE spreads actively.
**IMPLICATION FOR THE APP:** (1) **Do not ship PDT-counting logic or PDT warnings based on the old rule — they are now wrong,** though brokers have an 18-month implementation window so behaviour will be inconsistent per broker until late 2027. (2) The constraint that made defined-risk multi-leg structures impractical for small accounts has been removed, which expands the addressable strategy set for the app's target user. (3) Expect a wave of small accounts newly able to trade 0DTE spreads — i.e. the app's audience just got larger and less experienced at the same time.

---

### C. MAJOR EDUCATORS: STATED VS PAYWALLED METHODOLOGY

---

**CLAIM:** The options-education YouTube audience is in the hundreds of thousands to low millions of subscribers per channel, with a clear top tier.
**SOURCE:** FeedSpot, "90 Options Trading YouTubers in 2026" — https://videos.feedspot.com/options_trading_youtube_channels ; Benzinga, "Best Options Trading YouTube Channels," 31 May 2023 — https://www.benzinga.com/money/best-options-trading-youtube-channels/
**EVIDENCE TYPE:** Demand signal
**EVIDENCE STRENGTH:** Moderate (directory aggregators; counts are self-reported or scraped, Benzinga's are three years stale and Benzinga ranks its own channel first and discloses affiliate relationships)
**DETAIL (FeedSpot, 2026, order is FeedSpot's own ranking not strictly by subscribers):** Adam Khoo 1.1M; Wealth Secret 1.1M; Pivot Call 596K; Invest with Henry 481K; projectfinance (Chris Butler) 483K; Theta Gainers 459K; InTheMoney 458K; Trading Fraternity 309K; Carmine Rosato 222K; Sasha the Options Coach 195K; Black Girl Stocks 196K; Max Options Trading 173K; The Daily Traders 160K; Trade and Travel 147K; Vincent Desiano 124K; MasiTrades 117K; Options Millionaire 114K; Options with Davis 64.9K; Matt Diamond 63.2K; BestStockStrategy 37.5K. Benzinga's 2023 counts for reference: Option Alpha 229K, tastytrade 232K, Sky View Trading 354K, InTheMoney 319K, Benzinga 92.3K. Note several top channels (Adam Khoo, Wealth Secret, Pivot Call, Theta Gainers, Option Trading Only, DD Nifty) appear to serve non-US or Indian audiences — **a US-market app should discount these in sizing its addressable market.**
**IMPLICATION FOR THE APP:** The US-relevant options-education audience reachable through creators is on the order of 2–3 million subscribers across the top ~15 channels, heavily overlapping. This is a real but not vast market, and it is a *creator-mediated* market — distribution through educators is likely more efficient than direct acquisition.

---

**CLAIM:** projectfinance (Chris Butler) markets a "data-proven / data-driven" methodology with specific simulated success-rate figures, and the methodology behind those figures is not disclosed on the sales page.
**SOURCE:** projectfinance / Chris Butler, "Data-Driven Options Strategies" course page on Teachable — https://optionsforbeginners.teachable.com/p/data-driven-options-strategies
**EVIDENCE TYPE:** **Marketing claim**
**EVIDENCE STRENGTH:** **Marketing claim only**
**DETAIL:** The page advertises a LEAPS Growth Strategy (with SPY results and entry-timing/strike-selection discussion) and a "Hypergrowth" options strategy pitched as limited risk / high profit potential, plus directional buying, market-neutral selling, trade management, income on long-term calls, and call spreads vs calls. Headline claims: a **historical 80% success rate of reaching 100% gains and a 53% success rate of reaching 200% gains**; "notable gains" versus investing the same funds in the S&P 500 "with a fraction of the market exposure"; tradable in $2,500–$5,000 accounts with some variants needing only a few hundred dollars; a positions-update video titled with a final P/L of +$198,905. The page carries a **hypothetical-performance disclaimer** stating results are computer-simulated, do not reflect actual trading, may not account for liquidity, slippage or commissions, and are "designed with the benefit of hindsight," plus educational-purposes-only and not-a-broker-dealer language and a total-loss warning. The page does not state the time period, trade count, or how "success" is defined. It was closed for enrolment when I read it and showed no price.
**IMPLICATION FOR THE APP:** Two lessons. (1) **This is the disclaimer template the market uses** — the hindsight-design language is the operative sentence and it is doing real legal work. If the app shows backtested or simulated contract scores, it needs substantively this language. (2) **This is also the standard the app will be compared against and can beat.** An 80%-success-rate claim with no period, no trade count and no definition of success is exactly what the sceptical cohort distrusts. Publishing period, n, and definition is cheap differentiation.

---

**CLAIM:** Option Alpha's public methodology is free education plus a paid screener, backtester and autotrading-bot platform; an independent reviewer who followed its trade alerts reported losses and a deteriorating win/loss size ratio.
**SOURCE:** "A Complete Review of Option Alpha Free, Pro & Elite Lifetime Membership," Medium, January 2021 — https://medium.com/@yolotrading/a-complete-review-of-option-alpha-free-pro-elite-lifetime-membership-d2a93e54558f ; Option Alpha PDT explainer — https://optionalpha.com/learn/day-trading-rules
**EVIDENCE TYPE:** Independent scrutiny (single reviewer, dated 2021 — treat as anecdote plus structure description)
**EVIDENCE STRENGTH:** **Weak** for the performance claims (n=1, five years old, self-reported); Moderate for the product structure
**DETAIL (as reported, 2021 pricing):** Free tier = courses, videos, PDFs, podcasts (the reviewer rated this the strongest part). Pro $100/mo = follow head trader's trades + member forum. Elite $300/mo = weekly Sunday strategy calls + monthly office hours + discounts. Elite Lifetime $2,000 one-time = everything plus software toolbox and research reports. Paid tools: a watchlist/screener over ~120 preselected liquid tickers filterable by IV Rank, earnings and ETFs (**the reviewer's favourite feature, which he said would be worth a $50 one-time fee**); an earnings calendar limited to the current week; a backtester/trade optimizer at $500 one-time which he called overpriced, with data only 2007–2016, no trade-by-trade export, no rolling/adjustment testing and no technical filters; research reports (Covered Calls, Profit Matrix, Signals) totalling >$600 if bought separately. Criticisms: he lost money following alerts and computed an implied expectancy under $30/trade by mid-2020 as losers grew to ~2.5× the size of winners; **the public performance page subsequently stopped showing average profit and loss**; consistently delta-neutral positioning with no stop losses and early profit-taking underperformed in a strong bull market; the forum was clunky and quiet versus Reddit.
**IMPLICATION FOR THE APP:** Three transferable lessons. (1) **A filtered liquid-universe screener keyed on IV Rank is the feature a paying user singled out as worth money.** That is close to the app's core. (2) A backtester without rolling/adjustment testing and without trade-level export was judged not worth $500 — if the app ships backtesting, those two features are table stakes. (3) **Removing a performance metric from a public page is read as evidence of bad performance.** If the app publishes any track record, it must keep publishing it through drawdowns or not start.

---

**CLAIM:** SMB Capital's options education is a high-touch, mentorship-and-cohort model with deliberately undisclosed pricing.
**SOURCE:** SMB Training support article, "What training programs do you offer?" — https://support.smbtraining.com/support/solutions/articles/44000879018-what-training-programs-do-you-offer- ; "What is included in the Options Tribe Trading Team?" — https://support.smbtraining.com/support/solutions/articles/44002792396-what-is-included-in-the-options-tribe-trading-team-
**EVIDENCE TYPE:** Marketing claim / stated product structure
**EVIDENCE STRENGTH:** Strong for structure; **prices are not published** — the page directs prospects to a sales chat
**DETAIL:** Options programs: Options Tribe Premium (monthly sub, new weekly webinar recording, library of 650+ hours of past sessions, 5% course discount); Options Tribe Trading Team (year-long mentoring, weekly coaching, a 1:1 annual trading plan session); Options Foundation (16 structured sessions, video series + weekly live Q&A); Options Breakthrough (10 strategies in depth); 1:1 mentoring by the hour or in packages; **The Rhino Options Strategy** (self-paced, a positive-theta strategy with management and adjustment guidance); Vertical Spread Advantage (directional verticals). Equities side includes an "SMB Inside Access" subscription with 18+ weekly desk sessions, an archive, a **"Trading Mentor AI" tool**, and Discord; plus 4-week bootcamps capped at 12 traders with prerequisites.
**IMPLICATION FOR THE APP:** Note what the high-end of this market sells: **adjustment and management guidance**, not entry picks. "The Rhino" is marketed specifically on how to manage and adjust a positive-theta position. The app's proposed output is a *proposed strategy* — the premium end of the education market says the money is in what you do *after* entry. A position-management layer (roll suggestions, adjustment triggers, when-to-close) is likely more valuable and more defensible than entry scoring. Also note SMB already ships an AI mentor tool, so AI-branded features are no longer novel in this space.

---

**CLAIM:** tastytrade's methodology is simultaneously the most-cited and the least independently verifiable, and the criticisms of it are mostly general rather than methodological.
**SOURCE:** SteadyOptions forum thread, "Another garbage study from Tasty Trade" — https://steadyoptions.com/forums/forum/topic/3108-another-garbage-study-from-tasty-trade/ ; EliteTrader, "Tastytrade Review + Criticism" thread — https://www.elitetrader.com/et/threads/tastytrade-review-criticism.291821/
**EVIDENCE TYPE:** Independent scrutiny (low quality — forum opinion)
**EVIDENCE STRENGTH:** **Weak.** These are named-pseudonym forum posts on a competing educator's site, with few specifics.
**DETAIL — the criticisms actually made:** that the studies have undisclosed deficiencies and leave out inherent limitations/assumptions; that the presentation is too black-and-white; that the claim "buying straddles before earnings doesn't work" rests on very specific parameters and ignores that pre-event IV is high for a reason; that the market measures are skewed to support selling when vol is overpriced; that the "high probability trades" framing and the 50%-of-max profit-taking rule are questionable; that **black swans and fat tails are never discussed, so tail risk is understated**; and that their own public trades show losers rolled for months. One commenter elsewhere speculated that tastytrade does not publish host P&L. **None of this is verified, and the "no host P&L" point is an unverified forum assertion that I am reporting as such, not endorsing.**
**IMPLICATION FOR THE APP:** The substantive and repeated criticism is **tail risk is absent from the pitch.** If the app's score for a short-premium contract does not have a tail-risk term, it has the same hole that the dominant methodology's critics have been pointing at for a decade. Conversely, a visible tail-risk term is a legible way for the app to signal that it is not just another premium-selling pitch.

---

**CLAIM:** The paid options Discord / alert economy is large in product count, tiny in per-product revenue, and makes unverified win-rate claims.
**SOURCE:** WhopTrends, "Stock Signals Group Revenue Rankings" — https://whoptrends.com/rankings/stock_signals_group ; Whop blog, "Top 20 best options trading Discord servers," November 2026 — https://whop.com/blog/options-trading-guide-discord-servers/
**EVIDENCE TYPE:** Demand signal (platform-reported, estimated bands) + Marketing claim (the win rates)
**EVIDENCE STRENGTH:** Moderate for the economics (one platform, estimated revenue bands, internally inconsistent product counts); **Marketing claim only** for every performance figure
**DETAIL (economics):** 468 products in the category (the page's own meta description says 120 — inconsistent). **Average revenue $1K–5K, median revenue under $1K, "success rate" 24.2%.** The top-25 products sit in $10K–50K estimated revenue bands with member counts from 3 to 900 and prices from free to $500/mo. Highest-priced entries: Shark Pro Trader $500/mo with 23 members; STUDNET $460/mo with 3 members; 4 Leaf Clover $250/mo with 44 members.
**DETAIL (pricing and claims across 20 servers):** monthly prices cluster $50–$200, with weekly options at $30–$79/week, annual at $470–$900, and lifetime tiers at $599–$4,000. Member counts are almost never disclosed (two of twenty). Performance claims found: one server advertises **a win rate over 82%**; another cites "tens of millions" in member profits; another promises results in a couple of hours a day and targets six or seven figures; another says most members expect to recoup the fee in a single trade. The Whop blog is the platform's own promotional content and provides no evidence for any of it.
**IMPLICATION FOR THE APP:** (1) **Willingness to pay is real but shallow and concentrated.** A median paid-signal product earns under $1,000 lifetime and ~76% fail. Do not model the app on signal-service economics. (2) The $50–$200/month band is where this audience already pays, consistent with the Unusual Whales anchor. (3) **Unverified win-rate claims like "82%" are the competitive noise floor.** The app cannot win a claims arms race and should not try; it can win by being the one that shows its working.

---

### D. SATURATION, POLLUTION, AND THE AI CREDIBILITY PROBLEM

---

**CLAIM:** r/options — the largest serious retail options community — has banned AI/LLM-authored content outright.
**SOURCE:** r/options front page, pinned moderator announcement "Effective Immediately: No AI/LLM Authored Content is allowed on this sub," read via redlib mirror — https://redlib.ssps.io/r/options
**EVIDENCE TYPE:** Demand signal (strongly negative)
**EVIDENCE STRENGTH:** Moderate-to-Strong (I read the pinned title and the mirror's summary of the rule, which allows exceptions for human-written posts *about* AI and for machine translation; I could not independently date the announcement or read the full rule text because search budget was exhausted — **this should be verified before being relied on**)
**CONTEXT:** The ban was reportedly prompted by an influx of low-effort posts. The same front page carried a thread asking "Is there a community that picks options trades for you?" — i.e. the demand for picks and the hostility to machine-generated content coexist in the same community on the same day.
**IMPLICATION FOR THE APP:** **This is the single hardest commercial fact in this strand.** The app's natural distribution channel has formally prohibited the kind of content the app produces. Practical consequences: (a) do not plan on organic Reddit distribution; (b) the app's output must be *verifiably not AI slop* — meaning it must show inputs, numbers and provenance, not prose; (c) an "AI-powered" badge is a liability with this audience, not an asset. Lead with the data and the method, not the model.

---

**CLAIM:** Retail traders' documented objection to AI pickers is specifically about signal generation and opacity, not about AI as a research aid.
**SOURCE:** AI Stock Picker App review site, quoting r/stocks and r/Daytrading users — https://aistockpickerapp.com/
**EVIDENCE TYPE:** Demand signal (second-hand quotation; the site discloses affiliate commissions and operates sister sites, so it has an interest in framing — but its *criticisms* cut against its own commercial interest, which makes them more credible)
**EVIDENCE STRENGTH:** Moderate
**DETAIL:** The two attributed sentiments: that LLMs are good research assistants and poor signal generators; and that AI stock-picker advertising overpromises relative to account outcomes. A third theme: too many alerts makes decisions harder, so tools that *reduce* noise are preferred to tools that multiply it. The review site praises one tool (Danelfin) specifically for **showing its factors rather than behaving as a black-box signal**, which the site presents as the differentiator — implying opacity is the category's main trust failure. The site claims a five-pillar "Alpha Score" checked against Reddit sentiment but publishes neither data nor formula, and promises "a track record you can check" without showing one.
**IMPLICATION FOR THE APP:** The design prescription is explicit and consistent across every trust source in this strand: **decompose the score.** A 0–100 number alone is the distrusted artefact. A 0–100 number that breaks into named, individually-inspectable factor contributions (liquidity, IV rank, spread cost, event proximity, flow, trend) with each factor's value and weight visible is the trusted artefact. Also: **fewer, better alerts beat more alerts** — the opposite of how the incumbent flow tools tier their pricing.

---

**CLAIM:** The SEC has publicly warned about fraudsters posing as experts in group chats recommending trades they attribute to AI.
**SOURCE:** Reported by Ridley Law Offices as an SEC investor alert of December 2025 — https://ridleylawoffices.com/0dte-options/
**EVIDENCE TYPE:** Regulatory fact, **second-hand** — I did not read the SEC alert
**EVIDENCE STRENGTH:** **Weak** as cited. Flag to the regulatory strand to locate and verify the primary alert.
**IMPLICATION FOR THE APP:** If confirmed, "AI-generated trade recommendations delivered through chat" is a pattern the SEC has specifically named in an investor alert. That is a reason for the app to be conspicuously unlike it: no chat-delivered picks, no implied performance, prominent educational framing, and no claim that an AI selected the trade.

---

**CLAIM:** The retail options education search space is saturated with low-quality, apparently AI-generated or affiliate-driven content, which raises the bar for a tool's credibility signals.
**SOURCE:** My own search results across ~24 queries. Representative examples of the pollution: fattail.ai, tradealgo.com / news.tradealgo.com, tradersagency.com, optionspilot.app, tapeboard.com, thetaloop.app, apexvol.com, finwiz.io, tradiecapital.com, advancedautotrades.com, and numerous `*.pages.dev` sites (options-simply.pages.dev, options-force.pages.dev, optionsnest-com.pages.dev, joinastre.pages.dev, protraderdashboard.pages.dev).
**EVIDENCE TYPE:** Observation / Independent scrutiny
**EVIDENCE STRENGTH:** Moderate (systematic observation across many queries, not a formal content audit)
**DETAIL:** For high-intent queries like "iron condor," "unusual options activity," "IV rank vs IV percentile," and "earnings IV crush," the first page was dominated by these domains rather than by brokers, exchanges, academics or established educators. Several of them published near-identical framings of the same concept.
**IMPLICATION FOR THE APP:** Users arriving at the app have likely just waded through this. The app's trust signals therefore need to be *structural* (visible data provenance, timestamps, named data sources, reproducible numbers) rather than *rhetorical* (claims of being data-driven, which every one of these sites also makes).

---

### E. MARKETED CLAIMS VS EVIDENCE: REGULATORY ACTIONS

> **All of the following are flagged for the regulatory strand.** I report documented actions and sourced reporting only, I attribute clearly, and I note where matters are allegations rather than findings. I name organisations and only those individuals already named in public regulatory filings or court opinions.

---

**CLAIM:** The FTC has repeatedly brought actions against trading educators over earnings claims, and the resulting orders establish a concrete substantiation standard.
**SOURCE:** FTC stipulated final order, *FTC v. Online Trading Academy*, C.D. Cal., 11 September 2020 — https://www.ftc.gov/system/files/documents/cases/x200032_online_trading_academy_-_final_order.pdf
**EVIDENCE TYPE:** Regulatory fact (primary document)
**EVIDENCE STRENGTH:** **Strong**
**DETAIL:** The order (i) requires that earnings claims be non-misleading, with a reasonable basis and **written substantiation in hand at the time the claim is made**, made available on request; (ii) prohibits misrepresenting the time, effort or capital typically needed to become proficient, prohibits claiming anyone can become proficient regardless of background, prohibits claiming significant returns from little capital or time, and prohibits claiming instructors are successful active traders unless true; (iii) bars calling commission-based salespeople "Education Counselors" and requires disclosure that reps are commission-paid; (iv) bars contract terms restricting communication with the FTC; (v) bars review-restricting or review-penalising contract terms and requires notifying past clients of their right to post honest reviews. A **$362 million** judgment was entered jointly and severally, mostly suspended on specified payments (Eyal Shachar $8.3M, Samuel Seiden $158,000, Darren Kimoto $736,300) plus surrender of vehicles and an aircraft, with the suspension voidable on material misstatement in the financial disclosures, and consumer-debt forgiveness for electing consumers.
**IMPLICATION FOR THE APP:** The substantiation standard is the operative constraint: **any performance or outcome claim the app makes must have written substantiation in the company's possession at the moment of the claim.** A 0–100 score is arguably an implicit outcome claim; a backtested score certainly is. Also note the review-suppression and commission-disclosure prohibitions — these shape what the app's own marketing and affiliate program may do.

---

**CLAIM:** The FTC and the State of Nevada have alleged that a large trading-education MLM made baseless earnings claims and kept no records of customer outcomes.
**SOURCE:** FTC press release, "FTC, State of Nevada Take Action Against IM Mastery Academy for Deceiving Consumers," May 2025 — https://www.ftc.gov/news-events/news/press-releases/2025/05/ftc-state-nevada-take-action-against-im-mastery-academy-deceiving-consumers
**EVIDENCE TYPE:** Regulatory fact — **these are allegations in a complaint; the court will decide**
**EVIDENCE STRENGTH:** Strong as to what was alleged; the allegations are unproven
**DETAIL:** Defendants are the company (IM Mastery Academy / IM Academy / iMarketsLive, now operating as IYOVIA), owners Chris and Isis Terry, and officers or top salespeople Jason Brown, Alex Morton, Matthew Rosa and Brandon Boyd. Programs reportedly cost up to **$400/month**; an MLM layer recruited customers to sell to others. The complaint alleges **more than $1.2 billion taken from consumers since 2018**. Alleged deceptions: false or baseless earnings claims used both to sell training and to recruit; **no records kept of whether purchasers succeeded**; marketing promising money "in minutes" and "in your sleep" and retirement in one's 20s; luxury-lifestyle displays by sales staff; social posts showing supposedly successful trades; targeting young people including via college social media pages; and "trainers"/"educators" who were allegedly salespeople without credentials or trading records. IML's own data allegedly shows **~60% of customers stopped paying within one month and ~90% dropped within six months**, and that very few MLM participants earned substantial money with many or most losing money. Counts: FTC Act, Telemarketing Sales Rule, ROSCA, plus Nevada law.
**IMPLICATION FOR THE APP:** The ~60%/~90% churn figures, if borne out, are the most direct available estimate of retention in paid retail trading products — and they are brutal. Any subscription model for this audience should assume severe early churn. Separately, "keeps no records of customer outcomes" is pleaded as an aggravating fact: **an app that *does* measure and report user outcomes is in a materially better position than one that does not.**

---

**CLAIM:** Multiple other enforcement actions against trading educators and signal services are documented, including one where a "live trading room" operator never actually traded.
**SOURCE:** Ridley Law Offices survey of enforcement, "0DTE Options, Trading Signals and Courses" — https://ridleylawoffices.com/0dte-options/ (a plaintiff-side securities law firm; it has a commercial interest in this framing, and I did not independently verify each action)
**EVIDENCE TYPE:** Regulatory fact, **second-hand**
**EVIDENCE STRENGTH:** Moderate (consistent with the primary documents I did read, but each item needs primary verification)
**DETAIL as reported:** **Raging Bull** — FTC alleged its "gurus" promised account growth while the company did not track customer results; paid **$2.425 million in 2022**; a separate case against one individual ended in a permanent injunction with no money for victims, attributed to the Supreme Court's 2021 *AMG Capital* decision limiting FTC Section 13(b) monetary relief. **CFTC v. a FuturesFX principal** — alleged a "live trading room" where the principal "never actually traded and only made hypothetical or simulated trades"; consent order of **$1.3 million restitution and a $450,000 penalty**. **FTC rulemaking** — an earnings-claims rule was proposed in January 2025 but was not final as of that review; the FTC's 2021 penalty-offence notices warn that false money-making claims can carry civil penalties; the Business Opportunity Rule mostly does not reach trading courses. The firm also notes separate FTC redress programs: >$10M in refunds in a real-estate investment training case (March 2024, https://search.ftc.gov/news-events/news/press-releases/2024/03/ftc-sends-more-10-million-refunds-consumers-harmed-real-estate-investment-training-scheme) and >$2M in a money-making/coaching case (June 2025, https://www.ftc.gov/news-events/news/press-releases/2025/06/ftc-sends-more-2-million-consumers-harmed-scammers-pitching-bogus-money-making-coaching-programs).
**IMPLICATION FOR THE APP:** The "simulated results presented as real" pattern is the recurring enforcement trigger. If the app ever shows a hypothetical or backtested result in the same visual frame as a live one, that is the exposure. Separate them unambiguously.

---

**CLAIM:** A federal appeals court has held that an indictment of social-media traders for pumping tickers to their followers states a securities-fraud offence, reviving a case that had been dismissed.
**SOURCE:** *United States v. Constantinescu*, No. 24-20143 (5th Cir., 2 October 2025) — https://caselaw.findlaw.com/court/us-5th-circuit/117795982.html ; procedural history at Dynamis LLP — https://www.dynamisllp.com/knowledge/atlas-trading-update ; contemporaneous reporting of the original charges: CNBC, 14 December 2022 — https://www.cnbc.com/2022/12/14/sec-charges-social-media-influencers-in-alleged-100-million-fraud-scheme.html ; NBC News — https://www.nbcnews.com/tech/tech-news/sec-says-social-media-influencers-used-twitter-discord-manipulate-stoc-rcna61673
**EVIDENCE TYPE:** Regulatory / judicial fact
**EVIDENCE STRENGTH:** **Strong** for the holding; the underlying conduct remains **alleged** — the court reviewed only the sufficiency of the indictment, not guilt
**DETAIL:** Eight defendants with large social-media followings held themselves out as skilled traders and frequently posted their trading activity. The indictment alleges they bought a security, inflated its price by posting false and misleading information, then secretly sold — **$114 million** alleged. Charges: conspiracy to commit securities fraud plus multiple substantive counts. One defendant (Knight) pleaded guilty; the others moved to dismiss and the district court (Judge Hanen, S.D. Tex., early 2024) dismissed for failure to allege deprivation of a traditional property interest. The Fifth Circuit (Engelhardt, with Higginson and Willett) reversed and remanded, holding the indictment sufficiently alleged a scheme and intent to defraud. Reasoning drew on *Kousisis* (2025) — a fraudulent-inducement theory is valid where material misstatements induce a victim to hand over money or property; the victim need not suffer net economic loss and a profit motive is no defence — distinguished from *Ciminelli* (2023), which bars convictions resting solely on deprivation of valuable economic information, because here the indictment alleged defendants induced followers to *buy securities*. **The opinion itself does not mention Twitter, Discord, tickers or "scalping," and announces no standard specific to social-media promoters** — contemporaneous reporting supplies the platform detail.
**IMPLICATION FOR THE APP:** Flagged for the regulatory strand. The relevant shape: liability attached to *inducing followers to transact on the basis of material misstatements while holding an undisclosed interest.* An app that (a) does not hold positions in what it surfaces, (b) does not misstate its method, and (c) discloses conflicts is structurally distant from this. But the holding does establish that "I was just posting my trades" is not a safe harbour.

---

**CLAIM:** FINRA's targeted review found ~70% of broker-affiliated influencer social-media communications substantively non-compliant, with specific failure modes.
**SOURCE:** FINRA Unscripted, "Finfluencers: New Marketing Strategies Meet Existing Compliance Obligations" (social media influencer targeted review) — https://www.finra.org/media-center/finra-unscripted/finfluencer-social-media-targeted-review
**EVIDENCE TYPE:** Regulatory fact (primary source)
**EVIDENCE STRENGTH:** **Strong**
**DETAIL:** 15 firms, >1,000 communications reviewed; ~70% non-compliant in some substantive way, concentrated in paid-influencer and referral-link programs. Failure rates: ~55% failed to disclose the post was a paid advertisement; **~38% omitted risk disclosure for products including margin, securities lending, crypto and *options***; ~30% contained promissory, unwarranted, misleading or exaggerated statements (a flagged example: that anyone starting an IRA in their 20s will become a millionaire by 60); ~27% omitted promotion terms and conditions. Two 2024 enforcement examples: a firm that paid ~1,700 influencers over **$2.75 million** producing >39,000 new accounts, whose influencers misstated that margin loans could be repaid at any time, with no pre-publication review, no retention and no written supervisory procedures; and a firm that paid 17 influencers a flat fee per funded account for ~775 accounts, using promissory language implying similar results, again without review or retention. Compliance expectations: a firm becomes responsible for third-party posts when it **adopts** them (liking, reposting, linking) or becomes **entangled** with them (paying for or helping create them) per Regulatory Notice 17-18; posts must identify paid advertisements and name the firm prominently per Rule 2210; content must be fair and balanced; firms should pre-review influencer content, keep written supervisory procedures, do influencer due diligence and train them; and communications including referral-program materials must be retained with dates of use.
**IMPLICATION FOR THE APP:** Directly operative if the app ever runs an affiliate or creator program. The adoption/entanglement doctrine means **resharing a creator's post about the app can make the app responsible for that post's content.** And note the 38% figure: options risk disclosure is the most commonly omitted element in this entire category, which tells you where regulators will look first.

---

**CLAIM:** The SEC's own Investor Advisory Committee has documented how heavily young retail investors rely on social media for investment information and how rarely finfluencers disclose.
**SOURCE:** SEC Investor Advisory Committee, Disclosure Subcommittee draft recommendations on finfluencers, 22 November 2024 (for the 10 December 2024 meeting) — https://www.sec.gov/files/sec-iac-finfluencer-recommendation-11222024.pdf
**EVIDENCE TYPE:** Regulatory fact / cited research
**EVIDENCE STRENGTH:** Strong (primary document; the figures are attributed to FINRA Investor Education Foundation and CFA Institute respectively)
**DETAIL:** Key data cited: **~60% of investors under 35 get investment information from social media** (FINRA Investor Education Foundation); investors of colour are more likely than white investors to rely on social media, mobile trading apps and online video for investment advice; **only ~20% of finfluencer content containing investment recommendations included any disclosure** of professional status or compensation (CFA Institute). Concerns raised: low barriers to entry make scammers and undisclosed conflicts hard for retail to distinguish from credible sources; finfluencers can move prices (2021 meme-stock episode, with a Federal Reserve warning on resulting risks); some give advice without the knowledge to support it and face engagement incentives toward exaggeration; existing law covers the worst conduct especially where a regulated firm is involved, but gaps remain, with uncertainty from pump-and-dump rulings and from whether social posts create Section 12 seller liability. Recommendations include an Advisers Act disclosure rule for finfluencers (conflicts, compensation, regulatory status and qualifications, and that advice is impersonal), a BrokerCheck-like public data source on finfluencer complaints, comprehensive guidance, investor education, FTC/IOSCO coordination, and a study of whether existing anti-fraud provisions suffice. See also IOSCO's 2024 finfluencer report — https://www.iosco.org/library/pubdocs/pdf/IOSCOPD775.pdf
**IMPLICATION FOR THE APP:** Two things. (1) **The 60%-under-35 figure is the app's market thesis in one number** — this audience exists and gets its information from exactly the channels the app would compete with. (2) The direction of regulatory travel is toward mandatory disclosure of status, compensation, qualifications and the impersonal nature of advice. An app that builds those four disclosures in from day one is ahead of a rule that is being actively recommended. Flagged for the regulatory strand.

---

### F. WHAT USERS ACTUALLY ASK FOR

---

**CLAIM:** Premium sellers are manually maintaining spreadsheets, cannot organise candidate contracts, and are explicitly asking what others use — an unmet workflow need, not an analytics need.
**SOURCE:** r/thetagang, 12 January 2026 snapshot — https://reddit.sentinel-team.org/subreddits/thetagang/snapshots/2026-01-12T07%3A50%3A47.362601Z ; r/thetagang front page — https://r.datuan.dev/r/thetagang
**EVIDENCE TYPE:** Demand signal
**EVIDENCE STRENGTH:** Moderate (community posts, not survey data)
**DETAIL:** Observed in the January 2026 snapshot: a thread titled "Tools to 'bookmark'/organize puts?" where users said tracking candidate contracts is cluttered and they copy data into spreadsheets by hand; a thread "2026 YTD Gains by Structure" where the user categorised trades by structure using **Quicken with pivot tables**; a user who built a proprietary tracking platform and stopped sharing his spreadsheet because of repeated requests; brokers in use spanning Robinhood, Webull, IBKR and Fidelity; recurring "Week N — $X in premium" posts (i.e. people want premium-captured tracking over time); recurring "Earnings Calendar By Implied Move" posts; and confusion about how premium affects buying power in cash vs margin accounts on a specific broker.
**IMPLICATION FOR THE APP:** **The most clearly articulated unmet need in this strand is not better picks — it is a candidate-contract shortlist and a position/premium tracker that works across brokers.** "Save this contract, compare these five, track what I actually captured by structure" is the workflow people are hand-rolling in Excel and Quicken. That is lower-risk to build, easier to validate, and does not require the app to be right about the market. It is also the natural wedge: the tracker earns trust, the scoring earns the upgrade.

---

**CLAIM:** At least one community member is already running an options screener that scores contracts on roughly the dimensions this app proposes — and it was shared, not sold.
**SOURCE:** r/thetagang, 12 January 2026 snapshot (as summarised from the thread set) — https://reddit.sentinel-team.org/subreddits/thetagang/snapshots/2026-01-12T07%3A50%3A47.362601Z
**EVIDENCE TYPE:** Demand signal / competitive signal
**EVIDENCE STRENGTH:** **Weak** (a single community post read via a mirror summary; I did not read the report itself)
**DETAIL:** The described screener report scores contracts on implied vs. historical volatility, a directional bias derived from RSI, moving averages and put/call skew, and an "efficiency" measure based on bid/ask slippage. Separately, another member described using a custom ML model combined with technical analysis to pick direction and magnitude for daily trades, and asked why it worked on RUT but not NDX. **Generative AI tools were not discussed in that snapshot.**
**IMPLICATION FOR THE APP:** The proposed feature set is not novel to this audience — individuals are already building it for themselves and giving it away. Three specific takeaways: (1) **IV vs. historical volatility is the comparison this audience finds meaningful**, more than IV alone; (2) **bid/ask slippage as an explicit "efficiency" score component** is already how a practitioner built it, and it matches the empirical finding that costs dominate retail losses; (3) a directional bias built from RSI + MAs + put/call skew is the expected composition — the app's trend classifier will be judged against that, so it should either match those inputs or justify departing from them.
**Cross-strand note:** the technical-analysis strand should check whether RSI/MA-based directional classification has any support; this finding is only that it is what users *expect*.

---

**CLAIM:** Demand for someone else to pick the trades is explicit and coexists with the AI-content ban in the same community.
**SOURCE:** r/options front page thread, "Is there a community that picks options trades for you?" — https://redlib.ssps.io/r/options
**EVIDENCE TYPE:** Demand signal
**EVIDENCE STRENGTH:** Weak (one thread title)
**IMPLICATION FOR THE APP:** The market wants picks and distrusts generated picks. The resolution most likely to work: **the app proposes a structure and shows why, as inspectable numbers, and never asserts an outcome.** "Here are the three contracts that best fit your stated constraints, and here is each one's liquidity, cost, IV context and loss profile" is a pick without being a prediction.

---

**CLAIM:** Users also want help with the unglamorous parts: taxes, buying power, roll mechanics, and P&L views their broker does not give them.
**SOURCE:** r/options front page (threads on ITM-call tax implications, setting up an LLC, "Anyone know a way to get my daily P&L into a calendar view?", "Best stock screeners") — https://redlib.ssps.io/r/options ; r/thetagang (buying-power confusion, "Paid $.40 to roll GOOG option," CSP collateral questions) — https://reddit.sentinel-team.org/subreddits/thetagang/snapshots/2026-01-12T07%3A50%3A47.362601Z
**EVIDENCE TYPE:** Demand signal
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION FOR THE APP:** A roll calculator (net credit/debit, delta change, new breakeven, new DTE) addresses a need that appears in both communities and that the premium education market charges for (SMB's adjustment-focused courses). Calendar-view P&L is a small, concrete, repeatedly-requested feature.

---

## STRATEGY DEMAND MAP

| Strategy | How heavily marketed | Audience-size signal | Should the app support it? | Do the marketed claims hold up? |
|---|---|---|---|---|
| **Wheel / CSP / covered calls** | **Very heavy.** The organising strategy of r/thetagang; taught free by every major channel; the core of Option Alpha's and projectfinance's beginner funnels | Entire r/thetagang; "Week N premium" posts are a weekly ritual; the canonical overview post is community-canonical with a detailed comment debate | **Yes — this is the core.** It is the most-demanded, best-specified and most mechanically expressible strategy. Support delta target, DTE window, take-profit %, roll trigger, and a "willing to own" filter | **No, as marketed.** The "triple income" framing has a documented accounting problem (unrealised assigned-stock losses excluded). Rising delta into drawdowns makes it a growing long bet in exactly the wrong regime. Even the community debates whether it beats SPY. *The app must show total position P&L including stock mark and net position delta, or it reproduces the error* |
| **Credit spreads / iron condors / "high probability" premium selling** | **Very heavy.** The dominant paid-course subject; Sky View Trading built an audience on condors; SMB sells multiple positive-theta courses | Large; growing because the PDT change removed the leg-counting barrier for small accounts | **Yes.** Defined risk, expressible, and empirically the better-behaved 0DTE structure (positive median returns for spreads vs negative for single legs) | **Partly, and not as framed.** High win rate with negative skew is the structural truth. One conflicted 11-year test found 61% winners and negative returns. *Score must show max loss, loss-to-credit ratio, and consecutive wins needed to recover one max loss* |
| **0DTE / same-day SPX** | **Very heavy and still accelerating.** Whole vendor categories (SpotGamma, Unusual Whales GEX tiers) and dozens of Discords built on it | >75% of retail SPX option volume in 2022–23; 0DTE ~50–63% of all SPX volume by 2025–26 | **Support defined-risk 0DTE structures; actively discourage single-leg 0DTE.** This is the one place the evidence supports a directional product opinion | **No.** Strongest dataset available: retail lost >$125m over Feb 2021–Sep 2023, ~$350k/day post-daily-expirations, >$90m of it transaction costs, >$100m concentrated in single-leg. Honest vendors say so on their own pages. *Spread cost must be a first-class scoring input* |
| **Earnings / IV crush / straddles & strangles around events** | **Heavy and seasonal.** "Earnings Calendar By Implied Move" is a recurring community artefact; every vendor publishes an earnings guide | Large and spiky four times a year | **Yes, but as a warning surface rather than an opportunity surface.** Show implied move vs historical realised move and an expensive/cheap read | **No, for the retail-typical long-premium version.** Retail loses ~5–9% around earnings and ~10–14% around high-expected-vol events, driven by bidding prices up pre-event and by ~20% spreads that widen further; retail then holds through the loss. *A news/sentiment feature that surfaces heavily-covered names into earnings points at the documented loss centre* |
| **LEAPS / poor man's covered call** | **Moderate-heavy**, pitched hard at small accounts ($2,500–$5,000) | Recurring in both communities; a named module in paid courses | **Phase 2.** Two legs across two expiries as one position is materially more work than single-leg scoring | **Unverified.** The headline claims I found (80% success rate to 100% gains; 53% to 200% gains) are computer-simulated with no disclosed period, trade count or definition of success, under a hindsight disclaimer. Also, the risk-neutral/real-world gap is *worst* at LEAPS horizons, so delta-as-probability is least reliable exactly here |
| **Unusual options activity / "following the smart money"** | **Heavy, and the most commercially mature category.** $50–$120/mo at the category leader | Unusual Whales' tiering and Discord; "flow bots" are a standard Discord feature; AI flow bots advertised by servers with 30,000+ members | **Yes, but as context, not signal.** Flow is directionally ambiguous without trade-side attribution — show it as positioning context alongside OI and GEX | **Unestablished either way.** I found **no independent scrutiny at all** — the entire first page of search results was vendor and affiliate content. Notably the category leader's own pricing page makes **no predictive claim**. Treat "smart money" framing as marketing. *This is the weakest-evidenced feature in the app's plan and should be labelled most cautiously* |
| **Delta/theta mechanical rules, "the tastytrade approach"** | **The most heavily marketed meta-methodology in retail options** | tastytrade ~232K YouTube subs (2023) plus daily live programming and an attached brokerage; its vocabulary (IV rank, POP, 45 DTE, manage winners at 50%) is the lingua franca | **Yes — adopt the vocabulary and the thresholds as presets.** IVR 50/80/20 and 45 DTE are the strongest conventions in the space | **Not verifiable.** The written definitions pages give thresholds but no studies; the studies exist only as video titles with no written methodology, sample or data. The recurring substantive criticism is that **tail risk is absent**. One independent backtest found the 50%-profit-target rule *reduced* CAGR and Sharpe versus a DTE-based exit. *Ship the conventions as conventions, not as validated edges; add a tail-risk term* |

---

## USER VOCABULARY GLOSSARY

Terms the UI should use, in the sense this audience uses them. **⚠ marks terms whose common retail usage encodes a technical error.** Recommendation throughout: **use the familiar label, correct the semantics in a tooltip.** Renaming loses discoverability; silently repeating the error loses the sceptical cohort, which is the cohort whose opinion propagates.

**Structure and mechanics**
- **DTE** — days to expiration. 0DTE, 1DTE, 2DTE, 21DTE, 45DTE, 60DTE all used as nouns and as filter values.
- **CSP** — cash-secured put. **CC** — covered call. **PMCC** — poor man's covered call (long-dated long call + short near-dated call). **The wheel** — CSP → assignment → CC → repeat.
- **Vertical / credit spread / debit spread / iron condor / iron fly / broken-wing iron fly / butterfly / strangle / straddle / diagonal / calendar / box spread.** Note "spread" means both bid-ask spread and multi-leg structure; disambiguate in UI copy.
- **Roll / roll for credit / roll out / roll down** — the single most-requested calculation after entry. **Assignment / exercise / cash-settled.**
- **Cost basis / effective cost basis** — the wheel's framing of premium as basis reduction.
- **Buying power / collateral / portfolio margin / Reg T** — a documented source of user confusion, especially cash vs margin account treatment of received premium.
- **Bagholder / bags / "holding bags"** — the community's own word for the wheel's failure mode. Using it signals fluency.

**Greeks and volatility**
- **⚠ Delta** — used as "probability of finishing ITM." It is a hedge ratio approximating a *risk-neutral* probability, which embeds a risk premium and tilts toward bad outcomes; the approximation is worst at long (LEAPS) horizons. Label as "Delta (≈ market-implied chance of finishing ITM)" with the correction on hover.
- **Theta / theta decay / "theta gang" / positive theta** — fine as used. "Theta gang" is a self-identification, not jargon to explain.
- **Gamma / gamma risk / gamma squeeze / GEX (gamma exposure) / gamma wall / gamma flip / positive and negative gamma regime** — now mainstream via 0DTE education. Best honest framing found, from a vendor: a volatility-regime map, not a direction forecast.
- **Vega / IV crush** — IV crush is correctly used and is one of the better-understood retail concepts.
- **IV (implied volatility); IV Rank (IVR); IV Percentile (IVP).** Conventions: IVR >50 elevated, ≥80 extreme, <20 favours buying; IVP 0–30% cheap, ≥70% elevated. Implement both; IVR is more commonly cited, IVP is more robust to single spikes.
- **IV vs HV** — implied versus historical volatility. A practitioner-built screener used this comparison as a primary score input; it is more meaningful to this audience than IV alone.
- **Expected move / implied move** — used heavily around earnings. Pair with *historical realised move* to make it useful.
- **⚠ POP (probability of profit)** — chance of making at least $0.01. A model output, not an observed frequency; the leading platform builds it from a distribution curve borrowed from the beta-weighted symbol (SPY by default) and does not name the model; the leading educator's own explainer gives no formula and no risk-neutral caveat. **ePoP** is the portfolio-level version. If shown, disclose the model and the volatility input.
- **⚠ Probability of touch** — roughly double probability of ITM for a given strike; a real and useful distinction that retail often conflates with POP. Worth surfacing precisely because it is the honest counterweight.
- **⚠ Max pain** — strike maximising ∑(intrinsic value × open interest). Even its publishers call it unproven and controversial. Show OI-by-strike (genuinely informative about liquidity and dealer positioning); if you show max pain, caveat it and give it no scoring weight.

**Flow and positioning**
- **Flow / options flow / unusual options activity (UOA) / sweeps / blocks / "whales" / "smart money" / dark pool prints / open interest (OI) / volume-to-OI ratio.** ⚠ "Smart money" is a marketing frame: aggregated flow is directionally ambiguous without trade-side attribution and includes hedging. Prefer "unusual activity" or "positioning," and state what the data can and cannot distinguish.

**Account and regulatory**
- **⚠ PDT / pattern day trader / "the $25k rule"** — **now obsolete.** SEC approved FINRA's elimination on 14 April 2026, effective 4 June 2026; PDT designation removed, day trades no longer counted, replaced by brokerage-set intraday buying power above a $2,000 account minimum; brokers have until 20 October 2027 to implement, so behaviour will vary by broker. Users will still use the term. The right UI move: recognise the term, explain the change, and do not implement day-trade counting.
- **Options approval levels** — brokers gate strategies by tier. Referenced obliquely in the sources; **under-researched and flagged** — the app probably needs to know a user's approval level before proposing a structure they cannot place.
- **Good-faith violation / free-riding** — cash-account settlement traps, listed in the r/options wiki.
- **Section 1256 / wash sale / covered call taxation / Section 475 election** — the r/options wiki has a whole tax section; ITM-call tax treatment appeared as a live front-page question.

**Culture (use sparingly; signals fluency, but is not analysis)**
- **Tendies, YOLO, diamond hands, apes, stonks, to the moon, lottos/lottery tickets, "farmers' delight."** Note the r/wallstreetbets official glossary contains **no** Greeks, no IV, no assignment and no flow terms — it is not a source for this app's vocabulary. r/options and r/thetagang are.

---

## TRUST AND CREDIBILITY FINDINGS

**What makes retail options traders distrust an automated scoring tool:**

1. **An undecomposed score.** The one tool praised in the AI-picker review material was praised specifically for showing its factors rather than acting as a black-box signal. Opacity is the category's defining trust failure.
2. **The "AI" label itself, when applied to signal generation.** The documented sentiment distinguishes sharply: LLMs as research assistants, acceptable; LLMs as signal generators, not. r/options has banned AI/LLM-authored content outright. SMB already ships a "Trading Mentor AI," so the label is no longer even novel — it is just unearned.
3. **Win-rate claims.** The noise floor includes an advertised "82% win rate" and "tens of millions in member profits," with no evidence. Any number in that register gets the app sorted into that bucket. Compounding this: the FTC has alleged, in two separate matters, that educators made growth claims **while keeping no records of customer outcomes.**
4. **Quietly removing a metric.** A reviewer noted that Option Alpha's public performance page stopped showing average profit and loss, and read that as evidence of poor performance. The rule follows: publish a metric only if you will keep publishing it through a drawdown.
5. **Simulated results framed as achieved results.** This is the recurring enforcement trigger (a CFTC consent order over a "live trading room" where the operator only made simulated trades; the FTC's substantiation standard in the Online Trading Academy order). It is also what the sceptical cohort checks for first.
6. **Alert volume.** More alerts is read as noise, not value — notable because it is exactly how the incumbent flow tools tier their pricing.
7. **Omitted risk disclosure.** FINRA found ~38% of broker-affiliated influencer posts omitted risk disclosure specifically for products including options. It is the most commonly missing element in the whole category, which means it is where scrutiny lands.

**What makes a tool trusted instead:**

1. **Decomposition.** A 0–100 score that expands into named factors, each with its value, its weight, and its direction of effect. This is the single highest-leverage trust feature and every trust source in this strand points at it.
2. **Showing the cost.** Bid-ask spread and slippage dominate documented retail losses (>$90m of >$125m in the 0DTE study; ~20% of option price around earnings). A practitioner's own home-built screener already includes an "efficiency" term for bid/ask slippage. Making cost visible and load-bearing in the score simultaneously improves the model and proves the model is honest.
3. **Showing the loss, not just the probability.** Max loss, loss-to-credit ratio, and consecutive wins needed to recover one max loss. This directly answers the standing criticism of the dominant methodology (that tail risk is absent) and the standing criticism of the wheel (that losses are hidden in unrealised stock).
4. **Benchmarking against the obvious alternative.** "Versus buying and holding the underlying" and "versus the defined-risk structure on the same name." The community is already asking these questions of itself.
5. **Correcting the vocabulary gently.** Keeping the familiar labels while disclosing in a tooltip that delta and POP are market-implied under a risk-neutral assumption, not real-world forecasts. No incumbent appears to do this in its educational material. It costs two sentences.
6. **Disclosing provenance.** Named data sources, timestamps, update frequency. The search-result pollution means users are primed to suspect generated content; structural provenance is the antidote, and rhetoric ("data-driven") is not — every content farm says that too.
7. **Measuring and reporting user outcomes.** The absence of outcome records is pleaded as an aggravating fact in FTC complaints. The inverse is both a compliance posture and a trust asset.
8. **Four disclosures, built in from day one:** that the tool is not registered as an adviser; what compensation and conflicts exist; what the method's limits are; and that output is impersonal and not individualised advice. These are precisely the four the SEC Investor Advisory Committee recommended making mandatory.

---

## DISCONFIRMING EVIDENCE

*Evidence against building this product, or against building it as specified.*

1. **The target community has formally banned the app's output format.** r/options, the largest serious retail options subreddit, has a pinned rule prohibiting AI/LLM-authored content. The app's natural organic distribution channel is closed. *(Moderate confidence — I read the pinned title and the mirror's rule summary but could not verify the full rule text or date before the search budget ran out.)*

2. **Willingness to pay is shallow and the failure rate is high.** On the largest creator-commerce platform for this category: 468 products, **median revenue under $1,000, average $1K–5K, 24.2% "success rate."** Roughly three in four paid trading-signal products fail commercially. The products at the top of the ranking have 23 to 900 members.

3. **Churn in paid retail trading products appears catastrophic.** The FTC alleges, citing the company's own data, that ~60% of customers of a $400/month trading-education product stopped paying within one month and ~90% within six. These are allegations about one company, but they are the only retention figures I found anywhere, and they are sourced to internal data.

4. **The category is saturated and its leader is cheap.** Unusual Whales sells real-time flow, GEX, market-maker exposure, Greeks dashboards, politician trades, insider data, an AI assistant, and a free delayed tier, from **$42/month annualised**. A new entrant must be better than that at a comparable price, or materially different.

5. **The incumbents deliberately do not score contracts — and that may be a considered choice, not an oversight.** The category leader's pricing page advertises no scoring feature and makes no predictive claim. A scored, ranked contract list is closer to a recommendation than anything the incumbents ship. That is a differentiator and a regulatory exposure at the same time, and the fact that a well-capitalised incumbent declined to build it is information.

6. **The empirical record for the app's three headline features is unfavourable or absent.** Trend classification from charts: not covered here, but see the technical-analysis strand. 0DTE and short-dated directional trading: retail loses, with costs as the dominant term. Earnings plays: retail loses 5–14% by systematically overpaying into events, and the loss concentrates in the heavily-covered names a news feature would surface. Unusual options activity: **I found no independent scrutiny whatsoever** — the entire visible literature is vendor and affiliate content. An app that scores contracts on these inputs is building on sand and should say so.

7. **Delta, POP and max pain — three likely scoring inputs — are each technically compromised.** Delta and POP are risk-neutral quantities systematically biased by the variance risk premium; the industry-standard POP implementation borrows its distribution from SPY by default and does not name its model; max pain is disclaimed as unproven by the vendors who publish it. A composite score built from these inherits all three problems and compounds them.

8. **Even the mechanical rules this audience most believes in do not survive independent testing.** The "manage winners at 50%" rule — among the most-repeated conventions in retail options — produced *lower* CAGR (4.44% vs 5.46%) and *lower* Sharpe (0.52 vs 0.67) than a passive DTE-based exit in an independent SPX short-strangle backtest. If the app's presets encode the conventions, the app encodes this too.

9. **The regulatory direction of travel is toward more constraint on exactly this product shape.** The SEC Investor Advisory Committee has recommended an Advisers Act disclosure rule for finfluencers; the FTC proposed an earnings-claims rule in January 2025; FINRA's adoption/entanglement doctrine makes a firm responsible for creator content it reshares; the Fifth Circuit has revived a securities-fraud indictment against social-media traders who induced followers to transact; and the SEC reportedly issued a December 2025 alert specifically about trade recommendations attributed to AI. Nothing here forbids the app, but the compliance surface is growing, not shrinking.

10. **The clearest articulated user need is not the app's core feature.** What users say they lack is a way to shortlist, bookmark and organise candidate contracts and to track premium captured by structure across brokers — things they are hand-rolling in Excel and Quicken. Nobody in the threads I read asked for a 0–100 score. The demand for "someone who picks trades for me" exists but is voiced alongside the AI-content ban in the same community.

11. **Practitioners are already building a near-identical tool and giving it away.** A community member's shared screener already scores contracts on implied-vs-historical volatility, a directional bias from RSI/MAs/put-call skew, and a bid-ask "efficiency" measure. Another is running a custom ML model for daily direction. The free alternative is a motivated hobbyist with a spreadsheet, and that competitor has credibility the app will have to earn.

---

## OPEN QUESTIONS

**Gaps created by the search-budget cutoff (highest priority):**
1. **Unusual-activity alert services have no independent scrutiny that I could find.** Market Rebellion / Najarian-style UOA marketing, and whether any independent party has evaluated whether UOA alerts predict anything, is unresearched. This matters most because it is the app's least-evidenced planned feature.
2. **The December 2025 SEC investor alert on AI-attributed trade recommendations** — I have it only second-hand from a plaintiff-side law firm. Locate and read the primary alert.
3. **Disclaimer norms as primary sources:** CFTC Rule 4.41 hypothetical-performance language, SEC Rule 156, and the FTC's proposed earnings-claims rule status as of November 2026. I have the *market practice* (the projectfinance hindsight disclaimer is a good template) but not the rules.
4. **Broker options-approval levels.** The app may need to know a user's tier before proposing a structure. Unresearched.

**Substantive questions for the product:**
5. **Mirror or correct?** My recommendation is mirror-the-label, correct-the-tooltip for delta and POP. But this needs a decision, and it needs to be consistent — half-correcting is worse than either.
6. **Does the app compute its own POP, or borrow one?** If it computes one, whose volatility surface and what model? The incumbent's default (SPY's distribution, beta-weighted) is defensible for portfolios and poor for single names.
7. **Is the wedge the tracker or the score?** The evidence points at the tracker: clearer demand, lower regulatory exposure, easier validation, and it generates the position data the scoring layer would later need. Worth testing.
8. **Can the app validate anything itself?** Every methodology in this space is either paywalled, video-only, or unreplicated. An app that published one honest, reproducible study — with period, n, and definitions — would be unusual enough to be a marketing asset in its own right.
9. **How much does the PDT elimination change the addressable market?** Small accounts can now trade multi-leg structures actively for the first time. Broker implementation runs to October 2027, so the transition is messy. Nobody has measured the behavioural effect yet.
10. **What is the actual tail-risk term?** Every substantive criticism of the dominant methodology is that tail risk is missing. I cannot tell from this strand what the right term is — that is a question for the pricing/flow strand.
11. **Creator distribution:** given the r/options ban, is creator partnership the viable channel? If so, FINRA's adoption/entanglement doctrine and the SEC IAC's proposed disclosure rule apply to how it is structured.
12. **Does the app hold or trade anything?** If not, say so prominently — it is the cleanest distinction from the conduct in the Fifth Circuit case.

---

## TOP 10 SOURCES, RANKED

1. **Beckmeyer, Branger, Gayda et al., "Retail Traders Love 0DTE Options… But Should They?"** — https://wp.lancs.ac.uk/fofi2024/files/2024/04/FoFI-2024-146-Leander-Gayda.pdf — The strongest empirical evidence in this strand. Cboe transaction-level data, Feb 2021–Sep 2023, retail identified by trade code. >$125m lost, >$90m of it transaction costs, >$100m in single-leg. Directly determines that spread cost must be a first-class scoring input and that single-leg 0DTE is the documented loss centre.
2. **FINRA, "Finfluencers: New Marketing Strategies Meet Existing Compliance Obligations"** — https://www.finra.org/media-center/finra-unscripted/finfluencer-social-media-targeted-review — Primary regulator findings with hard percentages (~70% non-compliant; ~38% omitted options risk disclosure) and the adoption/entanglement doctrine. Operative for any creator or affiliate program.
3. **FTC stipulated final order, FTC v. Online Trading Academy (C.D. Cal., 11 Sep 2020)** — https://www.ftc.gov/system/files/documents/cases/x200032_online_trading_academy_-_final_order.pdf — The clearest statement of the earnings-claim substantiation standard: written substantiation in hand at the time of the claim. $362m judgment, mostly suspended.
4. **SEC Investor Advisory Committee, finfluencer recommendations, 22 Nov 2024** — https://www.sec.gov/files/sec-iac-finfluencer-recommendation-11222024.pdf — Both the market thesis (~60% of under-35 investors use social media for investment information) and the regulatory direction (mandatory status, compensation, qualification and impersonal-advice disclosure).
5. **r/thetagang, "The Wheel Strategy — An In-Depth Overview" and its comment thread** — https://lr.eu.psf.lt/r/thetagang/comments/1e6g9v2/the_wheel_strategy_an_indepth_overview — The de facto spec for the app's core feature: exact delta, DTE, take-profit and roll conventions, plus the internal dissent. Also where the delta-as-probability error is visible in the community's own canonical text.
6. **Karsten Jeske (Early Retirement Now), "The Wheel Strategy Doesn't Work," 17 Sep 2024** — https://earlyretirementnow.com/2024/09/17/the-wheel-strategy-doesnt-work-options-series-part-12/ — The best-reasoned critique of the app's core strategy, and the source of the single most important design constraint: show total position P&L including unrealised stock, and show net position delta.
7. **tastytrade platform support, "Probability of Profit (POP & ePoP)"** — https://tastyworks.freshdesk.com/support/solutions/articles/43000530527-probability-of-profit-pop-epop- — plus the educational counterpart at https://www.tastylive.com/concepts-strategies/probability-of-profit and the IV Rank definitions at https://www.tastylive.com/definitions/iv-rank-iv-percentile — Together these give the exact thresholds the UI should adopt *and* document how thinly the industry's flagship probability metric is specified.
8. **Ridley Law Offices, "0DTE Options, Trading Signals and Courses"** — https://ridleylawoffices.com/0dte-options/ — A plaintiff-side survey with a commercial slant, but the densest single index of documented enforcement against trading educators (Online Trading Academy, Raging Bull, the CFTC live-trading-room consent order, the Atlas case, the Dec 2025 SEC AI alert) and the FINRA PDT change. Every item needs primary verification; several I was able to verify.
9. **r/options front page, incl. the pinned AI/LLM content ban, and r/thetagang's Jan 2026 snapshot** — https://redlib.ssps.io/r/options and https://reddit.sentinel-team.org/subreddits/thetagang/snapshots/2026-01-12T07%3A50%3A47.362601Z — The two most important demand-side documents: the AI-content ban (the hardest commercial fact here) and the articulated unmet need (shortlisting, bookmarking, cross-broker premium tracking, roll calculation).
10. **WhopTrends stock-signals revenue rankings** — https://whoptrends.com/rankings/stock_signals_group — plus Unusual Whales pricing — https://unusualwhales.com/pricing — The economics: median paid-signal product earns under $1,000, 24.2% succeed, and the category leader's price anchor is $42–$120/month.

*Also load-bearing but outside the top ten:* the Constantinescu Fifth Circuit opinion (https://caselaw.findlaw.com/court/us-5th-circuit/117795982.html); the FTC IM Mastery/IYOVIA complaint announcement with its churn figures (https://www.ftc.gov/news-events/news/press-releases/2025/05/ftc-state-nevada-take-action-against-im-mastery-academy-deceiving-consumers); Schwab on the PDT elimination (https://www.schwab.com/learn/story/sec-approves-scrapping-25000-day-trader-minimum); Quantpedia's summary of "Losing is Optional" on earnings losses (https://quantpedia.com/how-retail-losses-money-in-option-trading/); CXO Advisory on Bogousslavsky & Muravyev's linked-brokerage retail options data — 5,182 traders, ~2.1m trades, Jan 2020–Dec 2022, average option trade return −0.8% but uncovered option sales averaging +21% (https://www.cxoadvisory.com/individual-investing/actual-retail-option-trading-returns); the Freeport Logbook explainer on risk-neutral vs real-world distributions (https://freeportlogbook.substack.com/p/options-implied-distributions-are); SteadyOptions on managing winners (https://steadyoptions.com/articles/does-%E2%80%9Cmanaging-winners%E2%80%9D-add-value-to-short-strangles-r618/); FeedSpot's channel-size directory (https://videos.feedspot.com/options_trading_youtube_channels); the projectfinance course page as the disclaimer template (https://optionsforbeginners.teachable.com/p/data-driven-options-strategies); SMB Training's program list (https://support.smbtraining.com/support/solutions/articles/44000879018-what-training-programs-do-you-offer-); SpotGamma's 0DTE hub (https://spotgamma.com/0dte/); and the Whop options-Discord listing as the marketing-claims noise floor (https://whop.com/blog/options-trading-guide-discord-servers/).
