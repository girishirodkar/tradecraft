# Research Strand 01 — Competitive Landscape

**Scope:** Every product covering any slice of the four layers of the proposed app
(L1 background research · L2 technical pattern fitting · L3 contract selection · L4 pricing judgment + 0–100 score + strategy proposal).

**Date of research:** 10 November 2026.

## Methodological caveats (read first)

1. **The organic search layer for this category is polluted.** A majority of search
   results for every query ("best options flow scanner 2026", "Unusual Whales pricing",
   "TrendSpider pricing") returned recently-minted, thin affiliate/SEO sites —
   `tradingtools-directory.pages.dev`, `aitoolsatlas.ai`, `alphasignal-56o.pages.dev`,
   `chartinglens.pages.dev`, `toolradar.com`, `walnutinvest.com`, `purepowerpicks.com`,
   `findmymoat.com`, `optionscout.ai`, `profitbuilders.io`, `thedz.io`, `scanedge.ai`,
   `robinflow.io`, `gex-levels.com`, `tradeecho.com`, `skylit.ai`, `flashalpha.com`,
   `optionsanalysissuite.com`. Several of these are *vendors* writing "neutral"
   roundups about themselves. I treat all of them as vendor claims. This is itself a
   finding (see DISCONFIRMING EVIDENCE §D1).
2. **Where I could not verify, I say so.** Items I could not confirm are listed under
   "Not verified" and in OPEN QUESTIONS. I did not fill gaps from memory.
3. **Search budget exhausted.** The shared WebSearch budget for this turn ran out
   partway through the data-supplier and "new entrant" sweeps. Specifically unfinished:
   Barchart Premier pricing (page returned empty), AlphaSense, Finnhub, Alpha Vantage,
   CBOE DataShop, Quiver Quantitative pricing, TradeAlgo's regulatory/complaint history,
   Unusual Whales' funding/ownership. ~32 searches and ~38 page fetches were completed.
4. **Lane discipline.** Whether flow/pattern signals actually *work* belongs to the
   technical-analysis and options-flow strands. I note overlaps but do not research them.

---

# PART 1 — FEATURE COVERAGE MATRIX

Depth key: **—** none · **◔** shallow · **◑** moderate · **●** deep

## 1A. Options analytics / flow

| Product | L1 Research | L2 Patterns | L3 Contract selection | L4 Price judgment + score + strategy | Price (US$/mo) | Composite score? |
|---|---|---|---|---|---|---|
| Unusual Whales | ◑ (congress, dark pool, news; no EDGAR/social depth) | ◔ | ● flow, GEX/DEX/vanna, 0DTE, 50+ ATS | ◔ — "Mr. Whale" AI assistant; **explicitly does not rank which flow is actionable** | $48–50 retail; ~$99 Retail Pro; API $150/$375 | No |
| Market Chameleon | ◑ earnings/div/events/insider/news scanner | ◔ | ● IV rank, order-flow sentiment, OI dashboard, straddles | ◑ vertical/butterfly/condor/covered-call screeners + backtester | $99 Premium (free tier) | No |
| OptionStrat | ◔ news, congress, insider | — | ◑ live flow, volume overlay | ◑ builder, chance-of-profit, net Greeks, IV-per-expiry | $29.99 Live Tools / $89.99 Live Flow | No |
| Cheddar Flow | ◔ | — | ● flow, ISO sweeps, dark pool, GEX (Pro) | — **states it gives no "buy now" signals**; has "Cheddar AI" + AI Power Alerts | $85 Std / $99 Pro ($75 annual) | No |
| InsiderFinance | ◑ news sentiment, insider, congress | ◑ TradingView confluence indicator suite | ● flow, dark pool, GEX, OI levels | ◑ **"Heat Score" 0–100** conviction per options trade | $75 / $65 qtr / $55 annual | **Yes (0–100)** |
| Tradytics | ◑ AI news feed, congress, insider | ◑ | ● Algo/Net/Trady Flow, dark pool, GEX/DEX | ◑ AI confidence score per print; Bullseye (intraday) + Prophet (swing) ranked output; AI portfolios | $0 / $69 ($37 annual) / $199 Discord-owner | **Yes (AI confidence)** |
| SpotGamma | — | — | ● GEX, HIRO hedging-impact, TRACE (gamma/delta/charm pressure) | — | ~$89–$299; Institutional from $1,999 | No |
| MenthorQ | — | ◔ | ● gamma/blind-spot levels, futures conversions | — | Sold via TrendSpider store / Tickblaze / Quantower (B2B2C) | No |
| Options Analysis Suite | — | — | ● 17 Greeks, OI-derived dealer exposure, 23 screeners | **● 17-model pricing engine, model-divergence, FFT Scanner emitting Strong-Buy→Strong-Sell per contract, 45+ strategy builder, backtest to 2007, 46-tool MCP server** | Free tier; Pro/API prices not published | **Yes (7-level categorical)** |
| Quantcha | ◔ | — | ◑ liquidity rating 1–5, IV rating, Earnings Crush Rate | ◑ Option Search Engine models strategies vs. your price target; sorts by expected return | Not published | **Yes (3 "Option Ratings")** |
| Option Alpha | — | — | ◔ | ● bot automation (50 bots), unlimited backtester, paper trading | $99–$149, or **$0 with qualifying TradeStation/Tradier/tastytrade account** | No |
| BullFlow | ◔ | — | ● flow, dark pool, GEX/VEX heatmap + replay | ◔ **"SigScore"** unusualness score on prints | $39 Basic / $69 Premium | **Yes** |
| Quant Data | ◔ | — | ● blocks/splits/sweeps, dark pool, GEX/DEX/VEX/CHEX, "Net Drift" | ◔ | $74.99 ($62.50 annual) | Partial |
| Skylit (Flowseeker / Heatseeker) | ◔ | — | ● flow + GEX, plus Nexus/Tempest/Talon/Atlas modules | ◔ own **"Flow Score"** | Community $149 ($1,079/yr); Heatseeker $349 or $699 | **Yes** |
| TradeEcho | ◑ news | ◔ charting | ● flow, dark pool, DealerEdge | ◔ signed **"Flow Score"**, "Cortex" AI | $199 / $2,199 yr / $3,499 lifetime | **Yes** |
| FlowAlgo | ◔ | — | ● sweeps/blocks/dark pool, voice alerts | — | was $149 — **sign-ups paused pending new platform** | No |
| BlackBoxStocks | ◔ | ◔ | ● unusual stock+options activity, dark pool | ◔ "proprietary detection algorithms" | was $99.97 / $959 yr | No |
| Whomp AI | — | — | ◑ golden sweeps, unusual activity | ◔ "AI scoring" | from $20 | **Yes (claimed)** |
| ScanEdge AI | — | ◔ RSI gating | ◑ 7×/day institutional flow scan | ◑ structured entry/target/stop, post-open validation; self-reported 65% win rate | Free plan advertised | Partial |

## 1B. Charting / pattern recognition

| Product | L1 | L2 | L3 | L4 | Price | Score? |
|---|---|---|---|---|---|---|
| TrendSpider | ◑ **Sidekick AI summarizes SEC filings**, compares fundamentals | ● auto chart patterns, auto trendlines, multi-timeframe scan, ML Quant Lab (logit/random forest), NL alerts | ◔ chains + analysis; MenthorQ add-on | — | ~$54–$155 (4 tiers); 25 free AI msgs/mo | No |
| Trade Ideas | ◔ (news scored 1.00 in lab test) | ● 136 patterns (85 candle / 51 price-trend); lab-tested 95% accuracy; top of category at 4.62 | — | ◑ Holly AI equity strategies (not options); Brokerage Plus auto-trade | $89–$127 Std; $178–$254 Premium | No (signals, not scores) |
| Tickeron | ◔ | ◑ 64 patterns (25 candle / 39 price-trend), lab 3.43 | — | ◑ AI Robots (equities) with win rates, profit factors | $5 signals / $45 robots / $125 unlimited (promo; ~2× regular) | No |
| TradingView | ◔ | ◑–● auto chart patterns from Essential; **AI Screener with request quotas** | ◔ 3–25 options strategies by tier | — | $0 / $12.95 / $29.95 / $59.95 / $199.95 (annual) | No |
| thinkorswim (Schwab) | ◑ | ◑ accuracy 4.80 but depth 2.50; composite 3.63 | ● chains, options workflows | ◔ script-driven, AI score 1.50 | **$0 with Schwab account** | No |
| Finviz | ◑ | ◑ | ◔ | — | Free / Elite (price not verified) | No |
| Autochartist | — | ● B2B white-label pattern engine since 2004 | — | — | B2B; **acquired by oneZero Feb 2025** | No |
| Acuity Trading (AnalysisIQ) | ◑ sentiment | ● pattern recognition launched 2026, 128+ instruments | — | — | B2B white-label | No |
| Trading Central | ◑ | ● | ◑ **embedded in Firstrade's Options Builder** | ◔ | B2B | No |
| WaveBasis | — | ◑ automated Elliott wave, **metered wave counts** | — | — | Free tier + Trader plan (price not published) | No |
| MotiveWave | — | ◑ Auto Elliott Wave, **gated to Elliott Wave Tools Pack / Ultimate edition** | ◑ | ◔ | Tiered editions | No |
| Elliott Wave International | ◑ | ◑ EWAVES automated wave analysis | — | — | Newsletter/subscription | No |

## 1C. AI stock analysis / scoring

| Product | L1 | L2 | L3 | L4 | Price | Score? |
|---|---|---|---|---|---|---|
| Danelfin | ● ~150 fundamental + 150 sentiment indicators | ◑ ~600 technical indicators folded into score | — **no options** | ● **AI Score 1–10** + Fundamental / Technical / Sentiment / Low-Risk sub-scores; ~10,000 features/day; decision-tree ensemble; 252-day rolling training | Not published on methodology page | **Yes (1–10)** |
| Seeking Alpha Quant | ● 100+ metrics, analyst estimates | ◔ momentum factor only | — | ● **Quant Rating 1.0–5.0** + A+→F Value/Growth/Profitability/Momentum/EPS-Revisions grades | Premium (price not verified) | **Yes (1–5)** |
| Zacks Rank | ● earnings-estimate revisions | — | — | ● **Rank 1–5** | Zacks Premium (price not verified) | **Yes (1–5)** |
| Tickeron AI | ◔ | ◑ | — | ◑ | see 1B | No |
| Robinhood Cortex | ◑ Benzinga, TipRanks, MT Newswires, CoinDesk, Decrypt, The Block, analyst ratings, **aggregated customer trading activity**, CPI/GDP/unemployment | ◑ **published indicator list**: SMA/EMA 20/50/200, RSI-14, MACD 12/26/9, Bollinger 20/2σ, 5-yr beta | — **options and futures explicitly excluded from Digests** | ◔ conversational assistant; **cannot help with multi-leg options**; **does not use open-web browsing or social-media sentiment** | **$5/mo (Gold)** | No |
| Robinhood Agents | ◑ via "Agent Apps" from 11 third-party data companies | ◑ | ◑ | ● user-authored natural-language agents that monitor and auto-execute | Gold; Agent Apps pricing not disclosed | No |
| Public.com Alpha / AI Agents | ◑ | ◑ MA, RSI, MACD, Bollinger, VIX | ◑ | ● **single-leg and multi-leg options agents**, rolling single legs; assignment/expiration risk "coming soon" | Not disclosed | No |
| IBKR | ◑ | ◔ | ● Volatility Lab, OptionTrader, Risk Navigator | ● **Option Strategy Lab ranks strategies against your own price/vol estimate**; Probability Lab matches strategies to a user-drawn distribution; **"AI integration" lets Claude/ChatGPT query your account for options research** | **$0 with IBKR account** | Ranking, not a score |
| Perplexity Finance | ● SEC data, live transcripts, screening | ◔ | ◔ | ◔ | Free tier exists | No |
| stocknear | ◑ FMP + Benzinga + Intrinio + OPRA | ◑ | ● flow (Benzinga), dark pool (15-min delayed), GEX, OI | ◔ | Open-source origins; tiers not on FAQ | No |
| AlphaSense | **Not researched — search budget exhausted** | | | | | |

## 1D. Data suppliers (partners, not competitors)

| Supplier | Stated price | What it gives the app |
|---|---|---|
| Polygon.io / Massive | Starter $29 (15-min delayed); Developer $79; Advanced $199 (real-time) | Raw chains, ticks, WebSocket. You build analytics. |
| ORATS | Delayed API $199 · Live $299 · Live Intraday $599 · All-In $899; Tools add-ons $99–$299 | Greeks, **ORATS theoretical value ("theo")**, SMV-smoothed IV surface, skew/kurtosis, IV forecasts, EOD history to 2007, 1-min to Aug 2020, T&S to Sep 2022. *Underlying values are internal-use only.* |
| ThetaData | $40 / $80 / $160 | Raw tick trades+quotes, per-contract Greeks/IV. No aggregated GEX. |
| Intrinio | ~$1,000+/mo | Fundamentals + options chains |
| Tradier | $10/mo data, or free with brokerage account | Chain data + execution |
| SqueezeMetrics | $720/mo ($8,640/yr) | GEX + DIX dark-pool, 4,500+ securities, history to 2011, API included |
| SpotGamma | Institutional from $1,999/mo | GEX/HIRO/TRACE (not API-first) |
| Unusual Whales API | $150 Basic / $375 Advanced ($50/wk trial) | Flow, dark pool, congress; MCP server + LLM-oriented API |
| FlashAlpha | Free (5 req/day) · $63 · $239–299 · $1,199–1,499; commercial $2,500–$4,500 | Pre-computed GEX/DEX/VEX/CHEX, max pain, vol surfaces, VRP, MCP server |
| Benzinga / FMP / OPRA | Not verified | Real-time options flow (Benzinga), fundamentals (FMP), raw feed (OPRA) |
| Quiver Quantitative, Finnhub, Alpha Vantage, CBOE DataShop | **Not verified — search budget exhausted** | |

---

# PART 2 — FINDINGS

## A. Layer 4 (the app's claimed differentiator) is already shipped by at least seven products

**CLAIM:** A 0–100-style composite score over options contracts is not novel; InsiderFinance
("Heat Score" 0–100), Tradytics (AI confidence score), BullFlow ("SigScore"), Skylit and
TradeEcho ("Flow Score"), Whomp AI ("AI scoring") and Options Analysis Suite (7-level
Strong-Buy→Strong-Sell per contract) all emit one today.
**SOURCE:** InsiderFinance, `llms-full.txt`, 2026, https://www.insiderfinance.io/llms-full.txt ·
Trade Echo, "Best Options Flow Tools (2026), Compared", Sep–Oct 2026, https://tradeecho.com/best-options-flow-tools ·
Skylit, "Best Options Flow Tools, Scanners & Platforms", Apr/Sep 2026, https://www.skylit.ai/learn/best-options-flow-tools ·
Options Analysis Suite, "vs Unusual Whales", 2026, https://www.optionsanalysissuite.com/vs/unusualwhales ·
Product Hunt, "Whomp AI", Jan 2026, https://www.producthunt.com/products/whomp-ai/launches
**EVIDENCE STRENGTH:** Strong that the scores exist (two of these are vendor-neutral-ish
roundups plus one first-party doc); Marketing-claim-only as to whether any works.
**IMPLICATION:** The score itself is table stakes. Differentiation has to come from
*auditability* — publishing the formula, the per-component contribution, and a live,
timestamped outcome ledger. Nobody in this list does all three.

**CLAIM:** InsiderFinance is the closest named precedent: its Heat Score is documented as a
0–100 conviction rating over premium, size-relative-to-open-interest, sweep urgency and
expiration — four of the exact inputs the app proposes for L3/L4.
**SOURCE:** InsiderFinance `llms-full.txt`, 2026, https://www.insiderfinance.io/llms-full.txt
**EVIDENCE STRENGTH:** Strong (first-party, explicit).
**IMPLICATION:** Treat the Heat Score's input list as the floor, not the design. If the app's
score reduces to the same four variables, it is a reimplementation at $75/mo of something
that already exists at $55/mo.

**CLAIM:** Options Analysis Suite is the single most direct competitor to the app's
"is this contract appropriately priced" layer: it runs 17 pricing models and 17 Greeks,
extracts local volatility, and its FFT Scanner emits a per-contract signal by comparing
model-implied price against live bid/ask across calibrated models — plus a 46-tool MCP server.
**SOURCE:** Options Analysis Suite, "vs Unusual Whales" and "Gamma Exposure documentation",
2026, https://www.optionsanalysissuite.com/vs/unusualwhales and
https://www.optionsanalysissuite.com/documentation/gamma-exposure
**EVIDENCE STRENGTH:** Moderate — vendor-authored, but unusually specific and technically
coherent, and its public methodology page discloses real limitations rather than hiding them.
**IMPLICATION:** The app must either beat a 17-model calibration engine on rigor or compete on
something else entirely (narrative synthesis, onboarding, explanation quality). It should not
assume "fair-value vs market price" is an unclaimed position.

## B. Disclosed methodology is the exception, and the honest disclosures are damaging

**CLAIM:** Options Analysis Suite publicly states that the standard dealer-positioning
assumption (dealers long calls, short puts) is "a convention, not an observation"; that open
interest cannot reveal direction; that the consolidated tape does not identify counterparty
roles; that quote-rule heuristics misclassify a material share of prints — especially large,
cross, auction, floor and complex trades; and that GEX is most reliable only for index
products and the top 10–20 single names by options volume.
**SOURCE:** Options Analysis Suite, "Gamma Exposure & Greeks by Strike", 2026,
https://www.optionsanalysissuite.com/documentation/gamma-exposure
**EVIDENCE STRENGTH:** Moderate (vendor-authored, but self-damaging and internally consistent
with how OPRA data works).
**IMPLICATION:** The app's L3 inputs — "unusual options flow", GEX, dealer positioning — are
built on a side-classification heuristic that one of the few vendors willing to publish its
assumptions says fails materially on exactly the large prints retail treats as the signal.
Build the app so that flow is a *context* feature with an explicit confidence flag, not a
driver, and restrict GEX-derived levels to liquid index/mega-cap names.

**CLAIM:** SpotGamma names its three TRACE models (Gamma, Delta Pressure, Charm Pressure) and
describes HIRO conceptually, but does not publish the formulas, inputs or assumptions of its
"Options Inventory Model."
**SOURCE:** SpotGamma, `llms.txt`, 2026, https://spotgamma.com/llms.txt
**EVIDENCE STRENGTH:** Strong (first-party; absence is verifiable).
**IMPLICATION:** The category norm is "name the model, hide the math." A disclosed-methodology
posture is a genuine, if narrow, differentiator — and one that costs nothing but defensibility.

**CLAIM:** Danelfin publishes the most detailed public methodology of any consumer scoring
product — ~900 indicators, ~10,000 daily features, a decision-tree ensemble averaged into a
probability, rolling 252-day training, four named sub-scores, and the explicit statement that
the AI Score is *not* the average of its sub-scores — while still withholding the indicator
list, weights, tree parameters, out-of-sample protocol and backtest transaction costs.
**SOURCE:** Danelfin, "How It Works", 2026, https://danelfin.com/how-it-works
**EVIDENCE STRENGTH:** Strong (first-party).
**IMPLICATION:** This is the realistic ceiling for disclosure in a commercial product, and a
good template: disclose architecture and inputs by category, withhold weights. Note Danelfin's
framing — "probabilities, not certainties", "useful but not infallible", "backtested
performance is not an indicator of actual future results" — as model disclaimer language.

**CLAIM:** Seeking Alpha's public Quant Rating methodology page describes the rating as an
"objective evaluation ... based on data" over 100+ sector-relative metrics but discloses no
weights and — notably — carries **no** "this is not investment advice" caveat.
**SOURCE:** Seeking Alpha Help Center, "What Are Quant Ratings, and How Do I Use Them?", 2026,
https://help.seekingalpha.com/premium/what-are-quant-ratings-and-how-do-i-use-them
**EVIDENCE STRENGTH:** Strong (first-party; I checked for the caveat and it is absent on that page).
**IMPLICATION:** Do not copy this. A publisher with Seeking Alpha's regulatory footing and
exclusion posture can word things this way; a new B2C app proposing *options* strategies
cannot. See §D on FINRA.

**CLAIM:** Robinhood publishes a methodology page for Cortex Digests naming its exact
technical indicators and its six news vendors, and discloses that it uses *aggregated customer
trading activity* as an input.
**SOURCE:** Robinhood, "Cortex Digests methodology", 2026,
https://robinhood.com/us/en/support/articles/cortex-digests-methodology/
**EVIDENCE STRENGTH:** Strong (first-party).
**IMPLICATION:** The disclosure bar has been raised by the largest retail broker. An app whose
score is a black box now looks *less* transparent than Robinhood, not more sophisticated.

## C. The brokerages are giving away large parts of all four layers

**CLAIM:** Robinhood Cortex — a conversational AI research assistant with scheduled and
breaking-news digests — costs $5/month as part of Gold, and in 2026 Robinhood added
user-authored AI Agents that monitor markets and trade automatically, with premium data from
11 third-party "Agent App" partners.
**SOURCE:** Robinhood, "Robinhood Cortex", 2026, https://robinhood.com/us/en/support/articles/cortex/ ·
Robinhood, "HOOD Summit 2026 product announcements", 2026,
https://robinhood.com/us/en/support/articles/hood-summit-2026-product-announcements/
**EVIDENCE STRENGTH:** Strong (first-party).
**IMPLICATION:** The app cannot price as "AI research for stocks." Its price must be justified
by the options-specific layers (L3/L4) that Cortex explicitly does not cover.

**CLAIM:** Cortex has two documented holes that map exactly onto the app's thesis: it "can't
help with complex trades, including multi-leg options trades," and it "doesn't use open-web
browsing or social media sentiment data." Cortex Digests exclude options and futures entirely.
**SOURCE:** Robinhood, "Robinhood Cortex" and "Cortex Digests methodology", 2026 (URLs above).
**EVIDENCE STRENGTH:** Strong (first-party, explicit).
**IMPLICATION:** This is the single clearest positive signal in this strand. The defensible
wedge is *multi-leg options strategy construction* plus *social/alt-data sentiment* —
precisely the two things the incumbent with 20M+ funded accounts has declined to ship.

**CLAIM:** IBKR's Option Strategy Lab already ranks candidate option strategies against a
user's own price and volatility estimate, free to account holders, and IBKR now offers an
"AI integration" that lets external assistants such as Claude or ChatGPT query a live account
for options research.
**SOURCE:** Interactive Brokers, "Options Trading Tools", 2026,
https://www.interactivebrokers.com/en/trading/options-trading-tools.php
**EVIDENCE STRENGTH:** Strong (first-party); the free-to-holders inference is Moderate — the
page says "no platform fees" for options trading but does not price the tools individually.
**IMPLICATION:** The "propose an options strategy consistent with a directional view" function
is free at a major broker *and* now LLM-addressable. The app's L4 output must be better than
"a ranked strategy list", e.g. by carrying the research provenance and the catalyst timeline
into the recommendation.

**CLAIM:** Public.com launched AI investing agents on 31 March 2026 that already support
single-leg and multi-leg options plus rolling single legs, built from natural-language
strategy descriptions with user approval before activation.
**SOURCE:** AI News, "Public.com Launches AI Investing Agents", 31 Mar 2026,
https://www.ainews.com/p/public-com-launches-ai-investing-agents-bringing-agentic-trading-to-retail-investor
**EVIDENCE STRENGTH:** Moderate (trade press reporting a vendor launch; no independent test).
**IMPLICATION:** The multi-leg gap at Robinhood is already being filled by a competing
brokerage with execution attached. The app's window on "agentic multi-leg" is ~months, not years,
and it will never match execution integration. Compete on research depth and explanation.

**CLAIM:** thinkorswim is free with a Schwab account and tested at 4.80/5 for pattern accuracy
(though only 2.50 for pattern depth) and 1.50/5 for AI/algo capability.
**SOURCE:** Liberated Stock Trader, "thinkorswim Lab Test Review", 2026,
https://www.liberatedstocktrader.com/thinkorswim-lab-test-review/
**EVIDENCE STRENGTH:** Weak-to-Moderate — a single reviewer's proprietary rubric, affiliate-funded,
with several internal inconsistencies and some near-zero medians that inflate scores.
**IMPLICATION:** Free broker tools are weakest at AI/narrative and strongest at execution and
chain mechanics. Do not compete on chain mechanics.

## D. The regulatory framing constrains L4's wording more than vendors' current copy suggests

**CLAIM:** FINRA's 2026 Annual Regulatory Oversight Report states that retail communications
which mention AI tools must describe how the AI is used and must balance benefits against
risks, and that firms using GenAI to create customer communications must ensure compliance
with Rule 2210; FINRA Rule 2220 separately governs options communications. Findings cited
include mobile apps failing to disclose, or inaccurately disclosing, loss risk on certain
options transactions, and misleading promotions in social media and in-app "nudges."
**SOURCE:** FINRA, "2026 Annual Regulatory Oversight Report", Dec 2025,
https://www.finra.org/sites/default/files/2025-12/2026-annual-regulatory-oversight-report.pdf
(sections: Communications and Sales → Communications With the Public; Reg BI and Form CRS;
GenAI: Continuing and Emerging Trends [new for 2026])
**EVIDENCE STRENGTH:** Strong (primary regulator document).
**IMPLICATION:** Three concrete build requirements. (1) Any "AI-powered" marketing claim must
be accompanied by a plain description of what the AI does and its risks. (2) Loss-risk
disclosure must sit *with* each proposed options strategy, not in a footer. (3) The report
notes Reg BI "cannot be satisfied through disclosure alone" — so if the app ever routes
orders or partners with a broker-dealer, the score becomes a recommendation and the whole
architecture changes. Design now for the non-BD, publisher-exclusion posture.

**CLAIM:** FINRA's third-party-risk section tells firms to assess a vendor's own use of GenAI
during due diligence, and its "Emerging Trends in GenAI: Agents" subsection flags autonomy
without human validation, auditability and data sensitivity as named risks.
**SOURCE:** Same document, Firm Operations → Third-Party Risk Landscape; GenAI → Agents.
**EVIDENCE STRENGTH:** Strong.
**IMPLICATION:** If the app ever hopes to be licensed to or embedded by a broker, it needs an
audit trail per score from day one. Retrofitting provenance is far harder than logging it.

**CLAIM:** Vendors in this category converge on near-identical disclaimer constructions:
Market Chameleon ("informational and educational purposes only ... does not constitute
financial, investment, or trading advice"; "Options involve risk and are not suitable for all
investors"); InsiderFinance (not a registered investment adviser, educational purposes, no
warranty of completeness/timeliness/accuracy); TrendSpider (helps traders make their own
decisions, nothing is investment advice, tools "as-is", not a brokerage); Unusual Whales
(separate "Not financial advice" page, and an FAQ stating no flow tracker can guarantee
profits and that these are *information* rather than trading signals); Option Alpha
("Option Alpha is not a broker. We are a software service provider").
**SOURCE:** Market Chameleon Premium, https://marketchameleon.com/Premium ·
InsiderFinance `llms-full.txt` · TrendSpider `llm-info`, https://trendspider.com/llm-info/ ·
Unusual Whales LP, https://unusualwhales.com/lp/best-options-flow-tracker ·
Option Alpha pricing, https://optionalpha.com/pricing — all 2026.
**EVIDENCE STRENGTH:** Strong (first-party pages).
**IMPLICATION:** The standard pattern is: (a) "educational/informational only", (b) explicit
"not an investment adviser / not a broker", (c) "no guarantee of profit", (d) options-specific
risk language, (e) framing outputs as *information* and the tool as a *starting point* rather
than a signal. InsiderFinance's own copy calls its Top Tickers "a starting point, not a final
trade signal." Adopt that framing verbatim in spirit: the 0–100 score must be presented as a
screening/prioritization device, never as a recommendation or a probability of profit.

## E. Pattern recognition (L2) is a commodity, sold B2B, and is being given away

**CLAIM:** Chart pattern detection is explicitly described in trade press as having "long been
treated as a standard add-on rather than a differentiator"; Acuity Trading's 2026 launch into
pattern recognition is framed as a catch-up to Autochartist, which has supplied brokers since
2004 and was acquired by oneZero in February 2025.
**SOURCE:** Finance Magnates, "Acuity Catches Up to Autochartist as Chart Pattern Detection
Becomes Table Stakes for Brokers", 27 Apr 2026,
https://www.financemagnates.com/forex/products/acuity-catches-up-to-autochartist-as-chart-pattern-detection-becomes-table-stakes-for-brokers/
**EVIDENCE STRENGTH:** Strong (independent trade publication; names the acquisition, date and
integration partners).
**IMPLICATION:** L2 is not a moat; it is a procurement decision. Either license it
(Autochartist/oneZero, Acuity, Trading Central) or implement a minimal version and spend the
effort elsewhere. Building a bespoke pattern engine is the most likely way to waste the
build budget.

**CLAIM:** TradingView sells auto chart patterns from its $12.95/mo Essential tier and an
"AI Screener" metered by request count (100/150/250/500 by tier).
**SOURCE:** TradingView pricing, 2026, https://www.tradingview.com/pricing/
**EVIDENCE STRENGTH:** Strong (first-party).
**IMPLICATION:** L2 retails at ~$13/mo. Price anchoring for the whole app is set by this.

**CLAIM:** In one reviewer's standardized bench, pattern-library depth and tested accuracy
rank TrendSpider 4.88, Trade Ideas 4.62 (136 patterns, 95% accuracy), thinkorswim 3.63,
Tickeron 3.43 (64 patterns, 95% accuracy) against a 2.73 median.
**SOURCE:** Liberated Stock Trader, Tickeron / Trade Ideas / thinkorswim lab-test reviews, 2026,
https://www.liberatedstocktrader.com/tickeron-lab-test-review/ ·
https://www.liberatedstocktrader.com/trade-ideas-review/ ·
https://www.liberatedstocktrader.com/thinkorswim-lab-test-review/
**EVIDENCE STRENGTH:** Weak. The rubric is proprietary and unpublished, the "95% accuracy"
figure is never defined or shown, the pages carry affiliate codes and discount links, the
author is described as a "partner", and the Trade Ideas page contradicts itself on pricing
(two different tables) and on how many years Holly beat the market.
**IMPLICATION:** Useful only as a relative ordering of library breadth. **Do not cite any
"95% pattern accuracy" claim** — including in the app's own marketing — because the published
benchmark that produced it is not reproducible.

**CLAIM:** Automated Elliott wave is treated as an expensive, metered, upsell-gated feature
rather than a core one: WaveBasis limits "automatic wave counts" by plan and publishes no
prices, and MotiveWave's Auto Elliott Wave sits behind the Elliott Wave Tools Pack /
Advanced Elliott Wave Pack and is absent from the Community Edition.
**SOURCE:** WaveBasis pricing, 2026, https://app.wavebasis.com/pricing ·
MotiveWave forum thread "Auto Elliott wave is no longer on my Motivewave software", 
https://forum.motivewave.com/threads/auto-elliott-wave-is-no-longer-on-my-motivewave-software-it-has-suddenly-disappeared.1258
**EVIDENCE STRENGTH:** Moderate (first-party pricing page; forum thread is user-to-user with no
vendor reply, so the gating explanation is a member's inference).
**IMPLICATION:** Metering implies real compute cost per wave count and low enough demand that
it is never bundled. Elliott wave should be the *last* L2 component built, if at all, and
should probably be a post-MVP paid add-on rather than a default.

## F. Independent evidence on composite scores is weak-to-negative

**CLAIM:** An independent review of a 14.4-year Zacks-affiliated managed separate account
(Feb 1995 – Jun 2009) found the Zacks Rank Strategy compounded at 6.5%/yr net of fees versus
6.5% for SPY, beating SPY in 9 of 15 years, while the Zacks Market Neutral Fund returned
−13.1% from inception (Jul 2008) to Jan 2010.
**SOURCE:** CXO Advisory, "Are Zacks Rankings Exploitable?", Jan 2010,
https://www.cxoadvisory.com/fundamental-valuation/are-zacks-rankings-exploitable/
**EVIDENCE STRENGTH:** Moderate. It is genuinely independent and net-of-fee, which is rare, but
it rests on one representative account and one short-lived fund, both Zacks-affiliated, assessed
by a single analyst; and it is 16 years old.
**IMPLICATION:** The longest-running, best-marketed composite score in retail finance has
public net-of-fee evidence of *zero* outperformance. The same paper notes Zacks' own hypothetical
portfolios assume **zero transaction costs** — and the app's options-contract scores will face
far worse frictions (bid-ask on options, assignment, early exercise). Any backtest the app
publishes must include realistic options spreads or it is not evidence.

**CLAIM:** Danelfin's headline backtest (+191% vs +118% for the S&P 500, Jan 2017 – Aug 2023)
is published without transaction costs, rebalancing rules, or any statement of out-of-sample
protocol.
**SOURCE:** Danelfin, "How It Works", 2026, https://danelfin.com/how-it-works
**EVIDENCE STRENGTH:** Marketing claim only (vendor backtest; the absences are verifiable).
**IMPLICATION:** This is the standard of proof the market currently accepts. The app can
clear it trivially — which means clearing it proves nothing and buys no trust from a
sophisticated user.

**CLAIM:** Tradytics self-reports roughly an 80% win rate on Trady Flow signals at 25+ repeats,
and does not publish model training, backtest windows, or false-signal rates across regimes.
**SOURCE:** Pure Power Picks, "Tradytics Review (2026)", https://purepowerpicks.com/tradytics-review/
**EVIDENCE STRENGTH:** Marketing claim only — and the reviewing site runs Tradytics bots in
its own Discord and links to its signup page, so it is a commercially interested party. The
*absence* of methodology disclosure is the more reliable part of the report.
**IMPLICATION:** Expect any user who has shopped this category to discount a win-rate claim
to zero. Publish an outcome ledger instead of a win rate.

**CLAIM:** ScanEdge AI self-reports a 65% win rate over 40 trades in April 2026 and 86% for
RSI 55–65 setups across 98 live signals.
**SOURCE:** Product Hunt, ScanEdge AI forum, 2026, https://www.producthunt.com/p/scanedge-ai
**EVIDENCE STRENGTH:** Marketing claim only. Sample sizes of 40 and 98 cannot distinguish an
86% hit rate from chance at any useful confidence, and the selection of the RSI 55–65 bucket
after the fact is textbook subgroup mining.
**IMPLICATION:** Do not report win rates on sub-100-trade samples. If the app reports anything,
report distribution of returns with the full trade universe and the date the rule was frozen.

## G. User sentiment: community and education are what people actually pay for

**CLAIM:** Bullflow's Trustpilot profile shows 48 reviews at a 4.3 TrustScore with 90% five-star,
and the praise clusters on GEX levels, heat map, affordability, the Discord community, mentoring
and webinars; the 1-star complaints are about support, billing and Discord moderation — not
signal accuracy. Trustpilot itself notes it does not fact-check reviews and that the sample may
not be representative, and one reviewer alleges the reviews are fake.
**SOURCE:** Trustpilot, Bullflow reviews, 2026, https://trustpilot.com/review/bullflow.io
**EVIDENCE STRENGTH:** Weak as evidence about product quality; Moderate as evidence about what
users *talk about*.
**IMPLICATION:** Two readings, both actionable. (1) The retention asset in this category is the
community, not the analytics — which is a problem for a pure-software app. (2) Nobody is
evaluating these tools on realized outcomes, which is why an outcome ledger is an unoccupied
position.

**CLAIM:** An independent, explicitly non-affiliate review of Unusual Whales concludes that it
is "a data layer, not a signal service", that it "doesn't rank which flow is actionable", that
congressional disclosures lag up to 45 days, that flow may reflect hedging or spreads rather
than directional intent, and that Unusual Whales does not disclose its data feed provider. The
reviewer states academic research on unusual options activity is mixed and any edge is likely
modest.
**SOURCE:** DayTradingToolkit, "Unusual Whales Review 2026", https://daytradingtoolkit.com/reviews/unusual-whales-review
**EVIDENCE STRENGTH:** Moderate. The reviewer explicitly disclaims affiliate commission on this
product (the site carries affiliate links to others), and the criticisms are specific and
checkable. Still one reviewer, no data.
**IMPLICATION:** This states the market gap in one sentence: the category leader supplies data
and declines to rank it. That is the app's L4 opening — and also a warning, because the leader
with the most data has chosen not to make that claim, which may be a legal and epistemic
judgment rather than a product oversight.

**CLAIM:** Market Chameleon's deepest coverage is options analytics and event/volatility data;
its technical-analysis layer is thin, limited to screener filters such as relative volume and
distance from moving averages, and its data is 15 minutes delayed on Premium.
**SOURCE:** DAYTRADINGz, "Market Chameleon Review", 2026, https://daytradingz.com/market-chameleon-review/ ·
Market Chameleon Premium, https://marketchameleon.com/Premium
**EVIDENCE STRENGTH:** Moderate (affiliate-compensated review, corroborated by the vendor's own
feature list and delay disclosure).
**IMPLICATION:** The deepest options-analytics incumbent is weak at L2. The combination of
genuine L2 + genuine L3 in one product is less crowded than either layer alone.

## H. Corporate events: one public company in this exact business abandoned it

**CLAIM:** Blackboxstocks Inc. (BLBX) — a Nasdaq-listed retail options/equities flow analytics
platform — reported 2025 revenue of $2.43M (down 5.3% from $2.57M) with a net loss of $4.43M
(27.5% worse than 2024), and on 24 February 2026 was delisted and merged into REalloys Inc., a
rare-earth metals company, which began trading as ALOY on 25 February 2026. Legacy
Blackboxstocks assets were separated into a wholly owned subsidiary, Blackbox.io Inc., tied to
contingent value rights distributed to former shareholders.
**SOURCE:** StockAnalysis.com, BLBX profile, 2026, https://stockanalysis.com/stocks/blbx ·
Blackboxstocks Inc. Form 8-K exhibit 99.1, SEC EDGAR, Feb 2026,
https://www.sec.gov/Archives/edgar/data/1567900/000118518526000663/realloysex99-1.htm
**EVIDENCE STRENGTH:** Strong (SEC filing + market data). The characterization that the legacy
business was separated rather than retained is an inference from the CVR structure — the
release does not state it outright.
**IMPLICATION:** This is the hardest single datum in this strand. A company selling precisely
layers 1 and 3 to US retail, with public financials, topped out around **$2.4M of annual
revenue, shrinking, while losing $4.4M a year**, and its shareholders' best available outcome
was a reverse merger into rare-earth mining. Model the realistic TAM for a standalone retail
options-analytics subscription at single-digit millions, not tens of millions.

**CLAIM:** Autochartist was acquired by oneZero in February 2025; Trading Central's tools were
integrated into Firstrade's Options Builder.
**SOURCE:** Finance Magnates, 27 Apr 2026 (URL in §E).
**EVIDENCE STRENGTH:** Strong.
**IMPLICATION:** The successful exits in this space are B2B infrastructure sales to brokers and
platform vendors, not B2C subscription businesses. Keep a licensing/API path open in the
architecture.

**CLAIM:** FlowAlgo — for years one of the most-advertised options flow services at ~$149/mo —
has paused new sign-ups pending a new platform launch.
**SOURCE:** Trade Echo, "Best Options Flow Tools (2026), Compared", Sep–Oct 2026,
https://tradeecho.com/best-options-flow-tools
**EVIDENCE STRENGTH:** Weak-to-Moderate. The claim comes from a direct competitor's roundup;
I could not independently confirm it, and flowalgo.com still resolves. **Flagged for verification.**
**IMPLICATION:** If true, the second-most-recognized brand in the category stopped selling. Worth
confirming before using it in any pitch.

## I. Data licensing is a real, under-appreciated constraint

**CLAIM:** stocknear publicly discloses its full supplier stack (Financial Modeling Prep for
market data/fundamentals/technicals, Benzinga for real-time options flow and analyst data,
Intrinio for options chains, OPRA as the underlying feed) and states plainly that it does
**not** have redistribution rights to that data.
**SOURCE:** stocknear, "Data Disclaimer" and FAQ, 2026, https://stocknear.com/data-disclaimer ·
https://www.stocknear.com/faq
**EVIDENCE STRENGTH:** Strong (first-party).
**IMPLICATION:** The app's business model has a hard dependency on display/redistribution
licensing. ORATS, for example, restricts underlying values to internal use only; OptionStrat
withholds live data from registered advisers and FINRA/SEC registrants because of licensing
cost. Budget legal review of each supplier's display terms *before* designing the UI, and
expect to be barred from serving professional users on the cheap tiers.

**CLAIM:** Realistic monthly data cost for the app's four layers, assembled from stated
list prices: raw options chains + real-time ($79–$199 Polygon, or $40–$160 ThetaData), IV
surface + theoretical values ($199–$899 ORATS), computed dealer exposure ($63–$299 FlashAlpha,
or $720 SqueezeMetrics), flow ($150–$375 Unusual Whales API), fundamentals/news (Intrinio
~$1,000+, or FMP/Benzinga at unverified cost).
**SOURCE:** ORATS Data API, https://orats.com/data-api ·
FlashAlpha, "Options Data Pricing Compared", Jun 2026,
https://flashalpha.com/articles/options-data-pricing-comparison-flashalpha-thetadata-polygon-spotgamma-squeezemetrics ·
dev.to, "Best Options Data APIs 2026", Jun 2026,
https://dev.to/tomasz_dobrowolski_35d32c/best-options-data-apis-2026-7-compared-pricing-free-tiers-1lf5 ·
NexusFi, Unusual Whales listing, https://nexusfi.com/d/data-providers/unusual-whales/
**EVIDENCE STRENGTH:** Moderate. ORATS prices are first-party and Strong. The comparison tables
are both authored by FlashAlpha's founder, who discloses it; the Polygon, ThetaData, SpotGamma
and SqueezeMetrics figures in them are second-hand and were not confirmed at source (Polygon's
pricing page is not fetchable in this session). Treat as order-of-magnitude.
**IMPLICATION:** A credible build lands somewhere between **$300 and $1,500/month in data
alone** before any compute. At competitor price points of $39–$99/mo, that is roughly 5–40
paying subscribers just to cover data — before the LLM inference costs that the app's L1
narrative synthesis will incur, which no incumbent in this matrix carries.

## J. MCP servers have made the app's pipeline assemblable by its own users

**CLAIM:** Unusual Whales, Options Analysis Suite (46 tools) and FlashAlpha all ship MCP
servers; Unusual Whales additionally publishes AI "skills" documentation and describes its API
as designed for LLMs and AI agents; IBKR offers an AI integration for connecting Claude or
ChatGPT to a live account.
**SOURCE:** Unusual Whales LP, https://unusualwhales.com/lp/best-options-flow-tracker ·
Options Analysis Suite, https://www.optionsanalysissuite.com/vs/unusualwhales ·
FlashAlpha pricing comparison (URL in §I) · Interactive Brokers options tools (URL in §C).
**EVIDENCE STRENGTH:** Strong (multiple first-party sources).
**IMPLICATION:** This is the most serious structural threat to the app and it is new. A
competent user with a Claude or ChatGPT subscription can now connect flow, analytics and
broker tools and get most of L1–L4 without buying an app at all. The app's value therefore
cannot be "an LLM with access to options data." It has to be the opinionated, reproducible,
logged pipeline — the parts a user would not assemble correctly themselves: survivorship-free
backtests, frozen scoring rules, calibration tracking, and an honest confidence model.

---

# PART 3 — GAP ANALYSIS

## What nobody does well

1. **Nobody ranks flow for actionability.** The category leader is described — in a
   non-affiliate review — as "a data layer, not a signal service" that "doesn't rank which
   flow is actionable." Cheddar Flow states it gives no "buy now" signals. This is an open
   position, but note §K below: the best-informed players may be abstaining deliberately.
2. **Nobody publishes an auditable outcome ledger.** Every performance number found in this
   strand was a vendor backtest, a self-reported win rate, or an unreproducible reviewer
   rubric. No product publishes timestamped scores with frozen rules and subsequent realized
   outcomes including spread costs. This is the single clearest unoccupied, defensible position.
3. **L1 ↔ L4 provenance is broken everywhere.** Products either do research (Robinhood Cortex,
   Perplexity Finance, Seeking Alpha) or options analytics (SpotGamma, OAS, Market Chameleon).
   Nothing carries a specific EDGAR fact or catalyst date through to a specific contract
   recommendation with the chain of reasoning intact. Robinhood Cortex explicitly stops before
   multi-leg options; Market Chameleon explicitly thin on technicals; Danelfin has no options
   at all.
4. **Nobody combines deep L2 with deep L3.** TrendSpider and Trade Ideas own patterns and have
   almost no options depth. Market Chameleon, SpotGamma and OAS own options and have almost no
   pattern work. The app's L2+L3 combination is genuinely less crowded than either half.
5. **Sector-level and social/alt-data sentiment is absent from the serious tools.** Robinhood
   explicitly excludes social-media sentiment from Cortex. The flow tools do news headlines, not
   sector-relative or social analysis. (Depth here is the alternative-data strand's lane.)
6. **Calibration is never reported.** Scores are presented as magnitudes, never as calibrated
   probabilities with reliability curves. Danelfin comes closest by framing its score as a
   probability of beating the market but publishes no calibration plot.
7. **Nobody discloses how a composite score decomposes per instance.** Danelfin gives category
   sub-scores but says the AI Score is not their average; everyone else gives a bare number.
   Per-contract contribution attribution would be new.

## What has been tried and abandoned — which is evidence, not just history

| Thing tried | What happened | Reading |
|---|---|---|
| Standalone B2C options/equity flow analytics as a public company | Blackboxstocks: $2.43M revenue, −$4.43M net, delisted Feb 2026, reverse-merged into a rare-earth miner | The B2C subscription TAM for this is small and the unit economics are bad at scale |
| Bespoke chart-pattern engines as a differentiator | Became B2B table stakes (Autochartist since 2004, acquired by oneZero 2025; Acuity catching up in 2026; TradingView at $12.95/mo) | Do not build; license or minimize |
| Flow alerts as a premium standalone brand | FlowAlgo priced at $149/mo, now reportedly paused for new sign-ups *(unverified)* | Premium pricing for undifferentiated flow has eroded; the floor is now $39 (BullFlow) |
| Automated Elliott wave as a core feature | Metered by count (WaveBasis), gated to top editions (MotiveWave), never bundled anywhere | Compute cost high, demand low. Build last or never |
| Bare composite ratings on options (Quantcha's three Option Ratings, launched May 2018) | Still present but never became the product's identity; no methodology published in 8 years; no pricing published | A score with no disclosed method does not build a business |
| Options flow interpreted as directional intent | The one vendor that publishes its assumptions says the dealer-side convention is "a convention, not an observation" and that quote-rule heuristics misclassify a material share of large/cross/auction/floor/complex prints | The input the app wants for L3 is noisier than the category's marketing implies |
| Composite equity ranks sold on marketing-grade backtests | Zacks: independent net-of-fee evidence of 6.5% vs SPY 6.5% over 14 years | Backtests without costs predict nothing about subscriber outcomes |

## K. The uncomfortable structural read

Three facts sit together badly. (1) The most data-rich player declines to rank its own flow.
(2) The one vendor that publishes its dealer-positioning assumptions says the classification is
a convention that fails on large prints. (3) FINRA's 2026 report now requires AI-mentioning
retail communications to describe the AI's use and balance benefits against risks, and flags
agentic autonomy without human validation. The most parsimonious explanation for why nobody
occupies the "rank the contracts" position is not that nobody thought of it — InsiderFinance,
Tradytics, BullFlow, Skylit, TradeEcho and OAS all did — but that the ones with the best data
judged the claim indefensible on both epistemic and legal grounds, and the ones who shipped it
did so without evidence. The app should assume the position is open for a reason and plan to
hold it with disclosed method plus a live outcome ledger, or not at all.

---

# PART 4 — DISCONFIRMING EVIDENCE

**D1. The market is not just crowded; it is in SEO-farm saturation.** Searching this category
surfaces a continuous stream of 2026-vintage sites that are either affiliate farms or vendors
posing as reviewers: Tapeboard, FlashAlpha, ScanEdge AI, Robinflow, Profit Builders, thedz.io,
Skylit, TradeEcho, gex-levels.com, Options Analysis Suite, optionscout.ai, chartinglens,
aitoolsatlas, alphasignal, walnutinvest, purepowerpicks, journalplus, toolradar, findmymoat.
Product Hunt alone yielded a dozen 2026 launches in this exact space — Whomp AI (7 upvotes),
GammaRips, GammVault, ScanEdge AI, StockIQ, TradeSmartAI, stocknear, Stock Expert AI,
OptionSense, StockLens, Orbital Trade, Profit Builders. Whomp AI ships "options flow scanner
with AI scoring" at $20/month. Customer acquisition in this category is a knife fight against
both well-funded incumbents and an unlimited supply of indie clones.
*(Sources: the Product Hunt and roundup URLs cited throughout; Whomp AI launch Jan 2026.)*

**D2. A public company doing exactly this topped out at $2.4M revenue and reverse-merged into
rare earths.** Blackboxstocks, 2025 revenue $2.43M and falling, net loss $4.43M and widening,
delisted 24 Feb 2026 into REalloys/ALOY. This is the only audited revenue figure available for
a pure-play retail options analytics business, and it is bleak.

**D3. The composite score the app treats as its output is already a commodity with a
race-to-the-bottom price.** Heat Score (InsiderFinance, $55–75), SigScore (BullFlow, $39),
Flow Score (Skylit, TradeEcho), AI confidence (Tradytics, $37–69), AI scoring (Whomp, $20),
7-level model-divergence signal (OAS, free tier). Shipping a 0–100 score is not a product; it
is a checkbox.

**D4. The strongest independent evidence on any retail composite score is null.** Zacks Rank,
net of fees over 14.4 years in a real managed account: 6.5%/yr versus SPY's 6.5%/yr. The same
analysis notes Zacks' marketed backtests assume zero transaction costs. Options scores face
materially worse frictions than equity ranks.

**D5. Users do not buy these products for signal quality, and do not evaluate them on it.**
Bullflow's 48 Trustpilot reviews praise GEX visuals, affordability, Discord, mentoring and
webinars; the negative reviews are about billing and moderation. One reviewer alleges the
reviews are fake; Trustpilot states it does not fact-check and that the sample may be
unrepresentative. The retention asset is community, which a pure-software app does not have.

**D6. The foundational L3 input is self-admittedly unreliable.** Per Options Analysis Suite's
own public documentation: dealer long-call/short-put positioning is "a convention, not an
observation"; open interest reveals no direction; the consolidated tape identifies no
counterparty roles; quote-rule heuristics misclassify a material share of prints, worst on
large, cross, auction, floor and complex trades; GEX is reliable mainly for indices and the top
10–20 single names by options volume. An independent Unusual Whales review adds that flow often
reflects hedging or spreads rather than directional intent, and that congressional data lags up
to 45 days.

**D7. L2 is a solved, licensed commodity.** Finance Magnates, Apr 2026: pattern detection "has
long been treated as a standard add-on rather than a differentiator." TradingView sells it at
$12.95/mo. Autochartist has done it since 2004 and was bought by oneZero. Building this is
spending scarce budget on a free feature.

**D8. The brokerages are destroying the price floor from above.** Robinhood Cortex at $5/mo
with a published methodology; Robinhood AI Agents with 11 third-party data partners; Public.com
agentic brokerage with multi-leg options support since March 2026; IBKR Option Strategy Lab
ranking strategies free to account holders; thinkorswim free with Schwab; Option Alpha's full
bot platform free with a $5,000 tastytrade/Tradier account. Every one of these is attached to
execution, which the app never will be.

**D9. MCP has commoditized the app's architecture.** Unusual Whales, Options Analysis Suite
(46 tools) and FlashAlpha ship MCP servers; IBKR lets Claude/ChatGPT query a live account.
A technically literate user can now assemble L1–L4 themselves for the price of a data
subscription. The app is competing with its own users' tooling.

**D10. Unit economics are adverse at prevailing prices.** Data alone plausibly runs $300–$1,500/mo
(ORATS $199–$899 first-party; plus chains, flow and fundamentals), before LLM inference that no
incumbent in this matrix pays for. Competitors charge $20–$99/mo. stocknear's disclosure that it
holds no redistribution rights, ORATS' internal-use-only restriction on underlying values, and
OptionStrat's exclusion of registered advisers from live data all show that the licensing layer
also constrains who may legally be sold to.

**D11. Regulatory framing cuts against the app's most saleable output.** FINRA's 2026 report
requires retail communications mentioning AI tools to describe how the AI is used and balance
benefits with risks, flags mobile apps that under-disclosed options loss risk, flags misleading
in-app "nudges", flags agentic autonomy without human validation, and states Reg BI "cannot be
satisfied through disclosure alone." A ranked list of options contracts with a 0–100 score and a
proposed strategy is, functionally, the thing the rules are written about.

**D12. The one product doing the app's hardest layer properly is doing it better than an MVP
can.** Options Analysis Suite: 17 pricing models, 17 Greeks, local-volatility extraction,
model-divergence scanning, 23 screeners, 45+ strategies, backtesting to 2007, ~2,000
instruments, a Python SDK and a 46-tool MCP server — with a genuinely free tier.

---

# PART 5 — OPEN QUESTIONS

1. **Has FlowAlgo actually stopped selling?** The claim comes from a competitor's roundup and
   flowalgo.com still resolves. Needs direct verification.
2. **Unusual Whales' ownership, funding and revenue.** NexusFi lists a 14-person San Francisco
   team founded 2020; I found no funding, revenue or acquisition data. Is the category leader
   venture-backed or bootstrapped, and at what scale?
3. **Barchart Premier pricing and whether its unusual-activity screener emits a score.** The
   Barchart page returned empty content; unresolved.
4. **AlphaSense** — not researched at all (search budget). Relevant to L1 (filings/transcript
   search) and to pricing expectations for research-grade tooling.
5. **Finnhub, Alpha Vantage, CBOE DataShop, Quiver Quantitative pricing** — unresolved. These
   are the cheap-tier options that could change the unit-economics picture materially.
6. **TradeAlgo's regulatory and complaint history** — flagged for checking and not completed.
   Several roundup sites list it as a major options scanner; if it has consumer-protection
   problems, that matters for category reputation.
7. **Danelfin, Seeking Alpha Premium, Zacks Premium and Options Analysis Suite Pro prices** —
   none published on the pages fetched.
8. **Did OptionStrat raise prices ~50% in 2026?** A May 2026 roundup lists $19.99/$59.99 while
   the vendor's own membership page now shows $29.99/$89.99. If real, it is evidence of pricing
   power in the category — the one piece of good news for the app's economics. Needs confirmation.
9. **What exactly is IBKR's "AI integration"?** If it is an MCP server against a live brokerage
   account, it is the most important competitive fact in this report and deserves its own dive.
10. **Robinhood "Agent Apps" — who are the 11 data partners, and what do they cost?** If
    Robinhood is wholesaling flow and analytics into a $5/mo product, the standalone market
    shrinks further.
11. **Does any product anywhere publish a frozen-rule, timestamped outcome ledger?** I found
    none. Worth one more targeted sweep, because if one exists the main unoccupied position is
    occupied.
12. **Are there non-US products (EU/Asia) attacking this with different regulatory latitude?**
    Not searched.

---

# PART 6 — TOP 10 SOURCES, RANKED

1. **SEC EDGAR — Blackboxstocks Inc. Form 8-K exhibit 99.1 (Feb 2026)** +
   **StockAnalysis.com BLBX profile.** The only audited financial record of a pure-play retail
   options analytics business, and its delisting into a rare-earth miner. Primary, verifiable,
   decisive for TAM.
   https://www.sec.gov/Archives/edgar/data/1567900/000118518526000663/realloysex99-1.htm ·
   https://stockanalysis.com/stocks/blbx
2. **FINRA, 2026 Annual Regulatory Oversight Report (Dec 2025).** Primary regulator document;
   sets the binding constraints on how L4 may be worded and marketed, and on agentic autonomy.
   https://www.finra.org/sites/default/files/2025-12/2026-annual-regulatory-oversight-report.pdf
3. **Options Analysis Suite — Gamma Exposure documentation (2026).** The most candid public
   statement of what dealer-positioning and flow-classification data cannot support. Vendor-authored
   but self-damaging, which is the most trustworthy kind of vendor claim.
   https://www.optionsanalysissuite.com/documentation/gamma-exposure
4. **Robinhood — Cortex Digests methodology + Cortex help article + HOOD Summit 2026
   announcements.** First-party; establishes the $5/mo price anchor, the new disclosure bar, and
   the two explicit gaps (multi-leg options, social sentiment) that define the app's wedge.
   https://robinhood.com/us/en/support/articles/cortex-digests-methodology/ ·
   https://robinhood.com/us/en/support/articles/cortex/ ·
   https://robinhood.com/us/en/support/articles/hood-summit-2026-product-announcements/
5. **Finance Magnates — "Acuity Catches Up to Autochartist as Chart Pattern Detection Becomes
   Table Stakes for Brokers" (27 Apr 2026).** Independent trade press; establishes L2
   commoditization and the B2B exit path, with the oneZero acquisition dated.
   https://www.financemagnates.com/forex/products/acuity-catches-up-to-autochartist-as-chart-pattern-detection-becomes-table-stakes-for-brokers/
6. **CXO Advisory — "Are Zacks Rankings Exploitable?" (Jan 2010).** The only genuinely
   independent, net-of-fee evaluation of a major retail composite score found anywhere. Old and
   narrow, but nothing better exists.
   https://www.cxoadvisory.com/fundamental-valuation/are-zacks-rankings-exploitable/
7. **Danelfin — "How It Works" (2026).** The most detailed public methodology for a consumer AI
   score; simultaneously the template for disclosure and the exhibit for how weak the market's
   accepted standard of proof is.
   https://danelfin.com/how-it-works
8. **InsiderFinance — llms-full.txt (2026).** First-party documentation of the Heat Score's
   0–100 scale and its four inputs, plus pricing and disclaimer posture. The closest existing
   precedent for the app's L4.
   https://www.insiderfinance.io/llms-full.txt
9. **ORATS Data API pricing (2026)** + **Options Analysis Suite "vs Unusual Whales" (2026)**.
   The first gives hard first-party data costs including theoretical values and the
   internal-use-only restriction; the second is the most complete description of the direct
   competitor at L4.
   https://orats.com/data-api · https://www.optionsanalysissuite.com/vs/unusualwhales
10. **DayTradingToolkit — "Unusual Whales Review 2026"** (explicitly non-affiliate for this
    product) + **Trade Echo "Best Options Flow Tools (2026)"** (vendor-authored, read for
    competitor prices and the Flow-Score/SigScore inventory). Together they establish the
    "data layer, not a signal service" gap and the current price grid.
    https://daytradingtoolkit.com/reviews/unusual-whales-review · https://tradeecho.com/best-options-flow-tools

---

## Appendix — Explicit non-findings

I could not find, and therefore do not assert:
- Any product that publishes a frozen-rule, timestamped, outcome-tracked ledger of its scores.
- Any independent, peer-reviewed or audited evaluation of any options-flow or options-scoring
  product's live performance.
- Any product that carries a specific EDGAR or social-media finding through to a specific
  contract recommendation with the reasoning chain intact.
- Pricing for: Options Analysis Suite Pro/API, Danelfin, Seeking Alpha Premium, Zacks Premium,
  Quantcha, WaveBasis Trader, Barchart Premier, Skylit's named tiers, Robinhood Agent Apps.
- Any funding, acquisition or revenue data for Unusual Whales, Market Chameleon, Tradytics,
  Cheddar Flow, InsiderFinance, TrendSpider, Tickeron or SpotGamma.
- Any evidence about AlphaSense, Finnhub, Alpha Vantage, CBOE DataShop, Quiver Quantitative
  pricing, or TradeAlgo's regulatory history — the shared search budget ran out first.
