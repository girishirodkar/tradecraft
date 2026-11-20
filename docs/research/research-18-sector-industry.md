# Research Strand 18 — Sector and Industry Level

Date: 2026-11-12. Scope: the middle layer between index and single name. Cost hurdle applied throughout: **~10% of premium round trip for single-name options, ~2–4% for liquid ETF options, ~1–3 bp for ETF shares.**

Labelling convention used below: **[PR]** peer-reviewed, **[WP]** working paper / conference paper, **[AM]** asset-manager or practitioner marketing, **[LIVE]** live market data snapshot.

---

## 1. INDUSTRY MOMENTUM

### CLAIM: The original Moskowitz–Grinblatt result is a ~0.43%/month raw, 0.20%/month risk-adjusted industry effect, and the paper itself warns it may not survive costs.
- **SOURCE:** Moskowitz & Grinblatt, "Do Industries Explain Momentum?", *Journal of Finance* 54(4), 1999. [PR] — http://www-stat.wharton.upenn.edu/~steele/Courses/956/Resource/Momentum/MoskowitzGrinblatt99.pdf
- **EVIDENCE STRENGTH:** Strong (for the in-sample 1963–1995 result)
- Details: 20 value-weighted two-digit-SIC industries, ~230 stocks each, Jul 1963–Jul 1995 (383 months). IM(6,6) raw 0.43%/mo; DGTW-adjusted 0.20%/mo (t=2.27). Individual-stock momentum size/BM-adjusted 0.29%/mo (t=3.34) but **industry-neutral individual momentum is 0.11%/mo, t=1.01 — insignificant**, and the excess-industry version is −0.07%/mo (t=−0.83). That is the subsumption claim.
- Breakeven one-way transaction costs: ~75 bp at ~200% annual turnover, ~150 bp at ~100%.
- The paper states that skipping one month eliminates IM(1,1) profitability and that high turnover means IM(1,1) profits likely do not survive costs.
- **HORIZON:** 1–6 month formation, 1–6 month holding, monthly rebalance.
- **DECAY EVIDENCE:** None in the original; sample ends 1995.
- **IMPLICATION FOR THE BUILD:** This is a cross-sectional long-short rank across ~20 industries with monthly rebalancing, not a per-sector absolute direction forecast. 0.20–0.43%/month on the *underlying* is an ETF-share-weight signal, not an options signal.

### CLAIM: The subsumption result does not hold once a one-month gap is inserted — industry momentum falls to insignificance.
- **SOURCE:** Grundy & Martin (2001), as reported in Hanauer/Windmüller-style review: "Momentum: what do we know 30 years after Jegadeesh and Titman's seminal paper?", *Financial Markets and Portfolio Management*, 2022. [PR] — https://link.springer.com/article/10.1007/s11408-022-00417-8
- **EVIDENCE STRENGTH:** Strong
- With a one-month gap between formation and holding, industry momentum profit falls to an insignificant 0.16%/month. Grundy & Martin's conclusion: too early to call industry momentum the main source of stock momentum.
- **IMPLICATION FOR THE BUILD:** A large part of the headline industry effect is one-month reversal/microstructure, i.e. exactly the component a retail account cannot capture. Any industry momentum signal in the build must be specified with a skip-month, which cuts the effect by roughly 60%.

### CLAIM: Industry momentum has since been shown to be subsumed by other effects — connected-firm momentum and factor momentum — leaving no independent alpha.
- **SOURCE:** Same review, citing Ali & Hirshleifer (2020), Arnott, Clements, Kalesnik & Linnainmaa (2021), Ehsani & Linnainmaa (2022). [PR review of PR papers] — https://link.springer.com/article/10.1007/s11408-022-00417-8
- **EVIDENCE STRENGTH:** Moderate-to-Strong
- Ali & Hirshleifer: after controlling for connected-firm momentum, industry momentum has **no significant four-factor alpha**. Arnott et al.: momentum in the three highest-eigenvalue principal components of industry-neutral factors subsumes *all* industry momentum. Ehsani & Linnainmaa: factor momentum explains all momentum in lower-eigenvalue PCs in the second half of 1973–2019.
- **DECAY EVIDENCE:** Ehsani–Linnainmaa's "all of it in the second half" is indirect decay evidence: the independent industry component shrinks over time.
- **IMPLICATION FOR THE BUILD:** The 1999 framing ("bet on industries, not stocks") has been substantially overturned. There is no residual industry-specific edge to build on.

### CLAIM: Within-industry momentum has predictive power beyond across-industry momentum — a direct contradiction of Moskowitz–Grinblatt.
- **SOURCE:** Asness, Porter & Stevens, "Predicting Stock Returns Using Industry-Relative Firm Characteristics", SSRN 213872, 2000. [WP] — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=213872
- **EVIDENCE STRENGTH:** Moderate (influential, long-unpublished working paper)
- **IMPLICATION FOR THE BUILD:** The literature is genuinely split on the central question. A split literature on a 20–40 bp/month gross effect is not a foundation for a product decision.

### CLAIM: Industry momentum is implementable in sector ETFs at 0.27–0.67%/month gross, with breakeven costs of ~65 bp per trade — but the only study ends in 2009.
- **SOURCE:** Andreu, Swinkels & Tjong-A-Tjoe, "Can exchange traded funds be used to exploit industry and country momentum?", *Financial Markets and Portfolio Management*, 2013. [PR] — summarised at https://agnosticinvesting.com/2023/12/agnostic-papers/agpa-73-country-and-industry-momentum/
- **EVIDENCE STRENGTH:** Moderate
- 9 S&P 500 sector ETFs, Dec 1998–Dec 2009, J=12/K=3: 0.27–0.67%/month. Theoretical (French 10-industry) version 0.40–0.63%/month, t>2, 1926–2009. FF3 alphas similar to raw returns; **no momentum factor control, so the paper cannot say industry momentum adds anything beyond single-stock momentum.** Breakeven cost 0.65% per trade for industry momentum (1.10% for country). ETF spreads fell sharply 2001–2009 and stayed below breakeven except in stress.
- **HORIZON:** 12-month formation, 3-month holding.
- **DECAY EVIDENCE:** None — data ends 2009. **There is no post-2009 published test of sector ETF industry momentum that I could locate.** That is itself a finding: the implementable version of this strategy has been un-tested for 17 years.
- **IMPLICATION FOR THE BUILD:** In ETF *shares*, this clears costs comfortably (65 bp breakeven vs 1–3 bp spreads). In sector ETF *options* at 2–4% round trip and monthly turnover, a 0.4%/month underlying signal does not clear unless you rely on option leverage to multiply it — which multiplies the variance identically. Conclusion: industry momentum is a share-allocation signal, not an options signal.

### CLAIM (DISCONFIRMING): Industry-level premiums add essentially nothing beyond stock-level premiums, and the one industry-momentum result with reliable alpha is destroyed by 500% annual turnover.
- **SOURCE:** Dimensional Fund Advisors, "Why the Benefits of Betting on Industries and Countries Are Few and Far Between". [AM — asset manager, but a research-grade test with a stated methodology] — https://www.dimensional.com/us-en/insights/why-the-benefits-of-betting-on-industries-and-countries-are-few-and-far-between
- **EVIDENCE STRENGTH:** Moderate
- US industries 1975–2021; other markets 1994–2021. Winning industries reliably beat losing industries in all markets (so the spread exists). But after testing for value *added over* stock-level premiums, only two candidates survived, and both then failed: developed-market country profitability is not robust to excluding Japan; **emerging-market industry momentum had reliable alpha but averaged 500% annualised one-way turnover at monthly rebalance, versus 15–35% for academic stock-level size/value/profitability portfolios. At semiannual or annual rebalance the alpha more than halved and became unreliable.**
- **IMPLICATION FOR THE BUILD:** Note the direction of this evidence: it is an asset manager arguing *against* a product it could easily sell. That makes it more credible than the reverse. The turnover number (500% vs 15–35%) is the cleanest single statistic in this strand.

### CLAIM: Full-sample industry momentum magnitudes remain large, but the sample is dominated by pre-1990 decades.
- **SOURCE:** Grobys & Kolari (2020), as reported in the FMPM 2022 review. [PR]
- Jul 1926–Feb 2018: three industry momentum strategies at 0.62%, 0.57%, 0.80%/month mean. Correlation of 0.14 between two of them suggests multiple partly independent forms. Volatility-managed version 1.16%/month unconstrained, 0.64–0.90% with leverage limits. Unmanaged skewness −0.47.
- **EVIDENCE STRENGTH:** Moderate. **DECAY EVIDENCE:** None — a 92-year average conceals any post-2005 subperiod.
- **IMPLICATION FOR THE BUILD:** Treat long-sample industry momentum magnitudes as uninformative about 2026. Apply the project's standing 80–90% haircut to published equity effects.

### CLAIM [AM]: The widely circulated practitioner version (top-3 of 10 sectors, 12-month lookback) reports Sharpe 0.54 with costs excluded.
- **SOURCE:** Faber, "Relative Strength Strategies for Investing", SSRN 1585517, via Quantpedia. [AM] — https://quantpedia.com/strategies/sector-momentum-rotational-system
- 1928–2009: 13.94%/yr, Sharpe 0.54, vol 18.38%, max drawdown −46.29%. **Transaction costs explicitly excluded**; turnover 100–400%; Quantpedia's own page notes unmodelled spreads, impact, fees and 50–150 bp estimated tax drag.
- **EVIDENCE STRENGTH:** Weak as evidence (backtest, in-sample, costs excluded, widely data-mined).
- **IMPLICATION FOR THE BUILD:** Sharpe 0.54 gross on a 98-year backtest with 100–400% turnover and a 46% drawdown is not a product. It is also the single most-copied sector strategy in retail finance, which is a reason to expect it to be arbitraged.

---

## 2. SECTOR ROTATION

### CLAIM (DISCONFIRMING, headline): Business-cycle sector rotation produces no systematic outperformance even with perfect ex-post knowledge of NBER turning points, and what little it produces vanishes under costs.
- **SOURCE:** Molchanov & Stangl, "The myth of business cycle sector rotation", *International Journal of Finance & Economics*, 2024. [PR] — https://onlinelibrary.wiley.com/doi/full/10.1002/ijfe.2882 ; working-paper version https://acfr.aut.ac.nz/__data/assets/pdf_file/0005/294287/The-Myth-of-Sector-Rotation-non-blind.pdf
- **EVIDENCE STRENGTH:** Strong
- Base case (Stovall-style rotation, 48 industries, 5 business-cycle stages, **perfect timing**): 1.00%/month vs 0.89% for the market — 11 bp/month gross — with higher volatility (5.02% vs 4.23%) and beta 1.04.
- Sharpe ratios: market 0.21, sector rotation **0.20**, naive market timing 0.26. Alternative groupings: 0.19 (10 sectors), 0.20 (23 industry groups). Alternative stage definitions: 0.18 (2 stages), 0.21 (4 stages), 0.14 (CFNAI).
- With 0.5–1.5% transaction costs, outperformance falls to 0.01–0.07%/month and is statistically indistinguishable from zero.
- Simply moving to cash in early recession beats sector rotation (≈0.15%/month) with 21 round trips instead of 53.
- Of all 1,022 two-stage/10-sector strategies, only 132 (12.9%) beat buy-and-hold and 35 (3.4%) beat market timing — attributed to data snooping. Of 2,160 cross-sector predictability t-statistics, 6% significantly positive and 5% significantly negative, i.e. chance.
- Industry alphas: four industries show significant Jensen's alpha; under FF3 and Carhart **none** show significant outperformance, only some significant underperformance.
- **HORIZON:** Business-cycle stages, months to quarters. **DECAY EVIDENCE:** n/a — it never worked.
- **IMPLICATION FOR THE BUILD:** Do not build business-cycle sector rotation. The study's design is maximally generous (perfect hindsight on recession dates, in-sample, no out-of-sample test) and it still fails. The project's standing conclusion that single-name direction is worthless extends to sector direction.
- **Note on the literature's shape:** Jacobsen, Stangl & Visaltanachoti's "Sector Rotation Across the Business Cycle" (SSRN 1467457) is the companion line of work. Against this there is an enormous volume of **[AM]** material — Fidelity-style business-cycle sector wheels, Quantpedia/Faber relative-strength rotation, numerous ETF-sponsor pieces. None of the **[AM]** material I surveyed deducted realistic costs. The peer-reviewed verdict and the marketing verdict are opposite, and the peer-reviewed verdict is the one with cost accounting in it.

---

## 3. SECTOR-LEVEL NEWS AND SENTIMENT

### CLAIM: News sentiment aggregated to industry level and propagated along supply-chain links produces a gross monthly cross-industry long-short IR of ~0.95, but the result is dictionary-fragile and reported gross of costs.
- **SOURCE:** Scognamiglio & de Zwart (APG), "Cross-Industry News Sentiment", Nomura Global Quantitative Equity Conference, 2012. [WP/AM — practitioner conference paper, not peer-reviewed] — https://www.nomura.com/events/global-quantitative-equity-conference/resources/upload/APG.pdf
- **EVIDENCE STRENGTH:** Weak-to-Moderate
- Method: count Harvard IV-4 negative words, aggregate to industry, then weight each industry's news by its goods-and-services flows to *customer* industries using input-output tables.
- Results, Apr 1989–Feb 2011, monthly rebalance: long-short 8.48%/yr, SD 8.95%, IR 0.95, t=4.44. FF3 alpha 0.67%/month (t=4.08), R² only 0.023. Barra style exposures do not explain it. Value-weighted 6.74% (IR 0.71, t=3.32).
- **Fragility:** switching from Harvard IV-4 to Loughran-McDonald — the dictionary the accounting literature regards as correct for finance — cuts the effect to 4.04%/yr, IR 0.55. A result that halves on a defensible change of word list is not robust.
- Correlation with cross-industry momentum long-short returns ≈ −1%, so it is a genuinely separate signal.
- No turnover, no transaction costs, no net-of-cost returns reported.
- **HORIZON:** Monthly; framed as a slow-reaction/supply-chain effect. **DECAY EVIDENCE:** None; sample ends Feb 2011 and I found no replication.
- **IMPLICATION FOR THE BUILD:** This is the one sector-level signal with a plausible mechanism (slow investor reaction along supply chains) that is *not* obviously repackaged beta. But it requires BEA input-output tables, a news corpus with industry tagging, and a dictionary choice that materially changes the answer; it is monthly cross-sectional across industries, not a per-sector trigger; and it is 15 years stale. Against the project's prior that single-name news sentiment reverses within a week and dies above ~10 bp, the relevant difference is horizon: this is a one-month effect, not a one-week reversal. Verdict: **interesting, not buildable at this scale.** Data obtainability is the binding constraint, not the evidence.
- Related, not obtained: Truong, "Does Industry Sentiment Explain Industry Returns?" (EFMA 2025) — robots-disallowed; https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2025-Greece/Does_Industry_Sentiment_Explain_Industry_Returns_Thi%20Thuy%20Trang%20Truong.pdf

---

## 4. PEER / INTRA-INDUSTRY INFORMATION TRANSFER

### CLAIM: A first announcer's earnings release moves its industry peers' implied volatilities, significantly and in the same direction — but the documented effect is contemporaneous, not predictive, and no trading strategy has been tested.
- **SOURCE:** Hann, Kim & Zheng, "Intra-industry information transfers: evidence from changes in implied volatility around earnings announcements", *Review of Accounting Studies* 24(3), 2019, 927–971. [PR] — https://link.springer.com/article/10.1007/s11142-019-9487-1 ; open version https://care-mendoza.nd.edu/assets/293764/hann_kim_zheng_rast_oct2018.pdf
- **EVIDENCE STRENGTH:** Moderate for the existence of second-moment transfer; **No credible evidence found** for tradeability
- Design: IV measured three trading days before vs three days after the first announcer's report. Significant positive association between the announcer's IV change and peers' IV changes, surviving controls for first-moment (return) transfer. Correlation between first- and second-moment transfer ≈0.25, so they are distinct.
- Stronger for: long-duration options, high-earnings-quality announcers, positive earnings news, bellwether firms, and periods of high macroeconomic uncertainty. ~60% of firms with an IV decrease also saw analyst forecast dispersion fall.
- The paper defines straddle-return variables (announcer and peers) in its appendix but **does not report strategy results**. No coefficient magnitudes or percentage IV changes were obtainable from the accessible text.
- **HORIZON:** [−3, +3] trading days around the announcer's report. **DECAY EVIDENCE:** None.
- **IMPLICATION FOR THE BUILD:** The mechanism is real: a bellwether's report resolves uncertainty about its peers, so peer IV should fall after a bellwether reports. Because the bellwether's date is known weeks ahead, this is a *scheduled* event, which is exactly the shape the project's event-driven mode wants. But nobody has shown the peer IV move is large enough to pay 10% of premium. See the SECTOR ETF hypothesis in §9.

### CLAIM: Peers' price reaction to a first announcer's earnings *overreacts* and partially reverses — but the magnitudes are 10–20 bp, far below the single-name options cost hurdle.
- **SOURCE:** Cheng, Fang, Huang & Zhong, "Overreaction or Underreaction to Intra-Industry Earnings Information Transfer: A Cross-Country Analysis", *Journal of International Accounting Research* 21(1), 2022, 1–21. [PR] — https://ira.lib.polyu.edu.hk/bitstream/10397/96101/1/Overreactior_UnderreactiIntra-Industry_Earnings.pdf
- **EVIDENCE STRENGTH:** Moderate (for the statistical effect), Weak (for usability)
- 91,442 firm-quarters, 33 countries, 1995–2015, **excluding the US**, excluding financials and utilities. Coefficient on the peer-news variable is −0.0537 (t=−3.97) raw and −0.0564 (t=−3.97) with full controls: late announcers' returns at their own report partially reverse the earlier peer-driven move. The underreaction coefficient is insignificant throughout (−0.0075, t=−1.30).
- Moderators: richer information environments → more underreaction (investor protection interaction 0.0325, t=2.85; transparency 0.0282, t=3.58); higher individualism → more overreaction (−0.052, t=−2.40).
- **Magnitudes:** average three-day [−1,+1] excess returns are 0.09% and −0.19%. **That is 9–19 bp.**
- No drift beyond the three-day window is examined; no portfolio test; no transaction costs.
- **HORIZON:** 3 days. **DECAY EVIDENCE:** None; and the US is excluded, so it does not even describe the project's market.
- **IMPLICATION FOR THE BUILD:** Dead on arrival. A 9–19 bp directional effect cannot pay 10% of premium, and the richer-information-environment moderator predicts the effect should be *weakest* in the US.

### CLAIM: Large-firm earnings announcements produce measurable market-wide spillovers to non-announcers, and announcers with high expected spillover earn large gross risk premia — all gross of costs.
- **SOURCE:** Ogneva, Xia & Ye, "Earnings News Spillovers and Risk Premium: Evidence from High-frequency Identification", working paper, March 2024. [WP] — https://ytgmyweb.s3.us-east-2.amazonaws.com/OXY_20240311.pdf
- **EVIDENCE STRENGTH:** Moderate
- 500 largest S&P 500 firms, 2004–2022, measured in 15-minute S&P 500 e-mini futures returns on a portfolio of non-announcing constituents. Absolute returns ~0.48 bp higher in announcement intervals vs non-announcement intervals, i.e. ~7% of the average absolute 15-minute return of 6.961 bp, and ~26% of the comparable macro-announcement effect. Excluding the ten largest firms gives 0.41 bp; excluding tech gives 0.42 bp.
- **Spillovers are persistent with no significant drift or reversal over the following seven hours** — i.e. the market prices them immediately.
- Past spillovers predict future spillovers (so the *magnitude* is forecastable even though the *direction* is not).
- Risk premia (gross): weekly FF5+MOM alpha ~0.30%/week for the largest 500 announcers (~16.7% annualised); ~0.23–0.25%/week for the largest 100. In the spillover-sorted test, value-weighted annualised alpha ~17.8% for high-expected-spillover announcers vs 5.3% for low.
- No transaction costs, net returns, or capacity analysis.
- **HORIZON:** Intraday for the spillover; weekly for the premium. **DECAY EVIDENCE:** None by subperiod.
- **IMPLICATION FOR THE BUILD:** The *second-moment* result is the usable one and it points the same way as Hann et al.: spillover magnitude is predictable, direction is not, and the move is instantaneous. That is a volatility statement, not a direction statement — which fits the project's existing conclusion that only vol/event modes survive. The "no drift or reversal over seven hours" finding specifically rules out a latency-based peer trade.

---

## 5. SECTOR ETF OPTIONS AS AN EXPRESSION VEHICLE

### CLAIM: Sector ETF options liquidity is extremely uneven — three or four are genuinely liquid and the rest are thinner than many large single names.
- **SOURCE:** Macroption, "Most Active ETFs by Options Volume", Cboe-group (CBOE/BATS/C2/EDGX) average daily options volume, 2026 YTD through 28 August 2026. [LIVE] — https://www.macroption.com/etf-options-volume/
- **EVIDENCE STRENGTH:** Strong (direct market data), though it is one venue group and volume is a proxy for, not a measure of, spread.

| Ticker | Rank | Avg daily options volume |
|---|---|---|
| SPY | 1 | 2,760,570 |
| QQQ | 2 | 1,534,038 |
| IWM | 3 | 419,827 |
| SMH (semis) | 11 | 59,799 |
| XLE (energy) | 17 | 41,237 |
| XLF (financials) | 19 | 37,241 |
| XLP (staples) | 31 | 14,180 |
| KRE (regional banks) | 32 | 13,977 |
| XLI (industrials) | 36 | 12,311 |
| XLB (materials) | 39 | 11,364 |
| XLU (utilities) | 43 | 9,648 |
| XBI (biotech) | 46 | 8,979 |
| XLK (technology) | 57 | 5,126 |
| XLY (cons. disc.) | 61 | 4,327 |
| XLV (health care) | 75 | 3,137 |
| XLRE, XLC | not in top 100 | — |

- Open interest, where visible: XLF carried roughly 6.0–6.1 million contracts of total open interest in early November 2026 on daily volumes of 160k–316k. [LIVE, news aggregator] — https://news.futunn.com/en/post/1003457880/
- **IMPLICATION FOR THE BUILD:** This is the single most actionable finding in the strand and it is a *negative* one for the naive version of the idea. "Use sector ETFs instead of single names" only works for **SMH, XLE, XLF, and arguably XLP/KRE/XLI/XLB/XLU/XBI**. XLK, XLY and XLV at 3–5k contracts/day are *less* liquid in options than dozens of single names, despite being the sectors a tech- or healthcare-oriented view would want. XLRE and XLC are not viable in options at all. **The build must whitelist specific sector ETFs by measured chain quality, not treat "sector ETF" as a liquidity category.**

### CLAIM (DISCONFIRMING of a hoped-for advantage): Sector ETF options carry **no** tax advantage over single-name options. They are equity options, not Section 1256 contracts.
- **SOURCE:** "Tax Rules for Options Trading: Section 1256 and Equity Options", Equicurious. [AM/reference] — https://equicurious.com/learn/investing-basics/taxes-and-regulations/tax-rules-for-options-trading-section-1256-and-equity-options ; corroborating: https://fedlaws.org/nonequity-options-as-section-1256-contracts-60-40-rule-and-form-6781/
- **EVIDENCE STRENGTH:** Strong (settled tax law, consistently reported)
- SPX qualifies as a Section 1256 contract: 60/40 long/short-term split regardless of holding period, mark-to-market, and **exempt from wash-sale rules**. **SPY and QQQ explicitly do not qualify**, and ETF options generally do not. Narrow-based index options and options on leveraged/inverse ETFs also do not qualify.
- Equity options: holding period depends on outcome; expired long options generally short-term losses; expired written options short-term gains; most active strategies produce fully-taxed short-term gains. Wash sales apply (including buying a call on a stock sold at a loss within 30 days, and reopening a substantially identical option). Section 1092 straddle rules can defer losses and suspend holding periods.
- **IMPLICATION FOR THE BUILD:** The tax ranking is **SPX/XSP/NDX/RUT ≫ sector ETFs = single names**. If tax treatment is a decision input, it argues for the index layer, not the sector layer. Moving a view from a single name to XLF changes cost and liquidity but not one cent of tax treatment.

### CLAIM: The structural reason some sector ETF options quote tightly is the Penny Interval Program, whose eligibility depends on both activity rank and underlying price under $200.
- **SOURCE:** Cboe, "Update — Penny Interval Program Annual Review and Rebalancing", 2022. [LIVE/exchange rule] — https://cdn.cboe.com/resources/product_update/2022/Update-Penny-Interval-Program-Annual-Review-and-Rebalancing.pdf
- **EVIDENCE STRENGTH:** Strong for the rule; **Weak for membership of any specific ticker** — the document names no tickers and points to separate lists.
- Rule: included series below $3.00 quote in $0.01 increments; series above $3.00 in $0.05. Classes removed from the program revert to $0.05 below $3.00 and $0.10 above. Each January, classes among the 300 most actively traded multiply-listed classes on securities priced below $200 (indexes below 200) are added; each April, classes outside the top 425 are removed.
- **IMPLICATION FOR THE BUILD:** Two consequences. (a) Penny status is the mechanical driver of "spread as % of premium" and it is *conditional on the underlying trading under $200* — so a sector ETF that appreciates past $200 can lose penny eligibility, which would widen its options spreads without any change in its popularity. (b) Membership changes annually, so the build should re-measure chain quality at least yearly rather than hard-coding a whitelist. **Do not assume any ticker's penny status; measure the quoted increments on the live chain.**

### CLAIM: No academic study of a sector-ETF variance risk premium was found, and a live snapshot shows the premium currently *negative* for XLF.
- **SOURCE:** [LIVE] OptionScout, XLF implied volatility page, 2026-11-12 — https://optionscout.ai/implied-volatility/xlf
- **EVIDENCE STRENGTH:** Weak (single snapshot, single name)
- On 2026-11-12, with XLF at $58.21: IV30 = 16%, HV30 = 18%, IV rank 27, IV percentile 35. IV minus HV = **−2 vol points**, i.e. options are pricing *less* movement than XLF has delivered.
- Searches for a sector/industry-ETF VRP study returned nothing on sector ETFs. The nearest adjacent results are on individual stocks and indices: González-Urteaga & Rubio, "The cross-sectional variation of volatility risk premia", *Journal of Financial Economics* 119(2), 2016, 353–370 [PR] (S&P 100 index options plus 181 stocks, Jan 1996–Feb 2011; VRP-beta-sorted stock portfolios range from about +10.3% to −3.4% annualised; index VRPs systematically more negative than individual-security VRPs; market VRP and especially the default premium price the cross-section, cross-sectional R² 0.514) — https://www.sciencedirect.com/science/article/abs/pii/S0304405X15001762 ; and Zhu, "Industry variance risk premium, cross-industry correlation, and expected returns", *Journal of Futures Markets*, 2023 [PR], which I could not retrieve (paywalled, fetch blocked) — https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22376. **That Zhu paper is the single most important unread source in this strand and should be obtained.**
- **IMPLICATION FOR THE BUILD:** The question "is the sector ETF VRP index-like or single-name-like?" has **no published answer**. The project's prior reasoning — index VRP is priced correlation risk, individual variance is unpriced — predicts a sector ETF should sit in between, with the premium rising in the number and diversity of its constituents. XLF (~70 holdings, high internal correlation) should look more index-like than XLE (~23 holdings, dominated by two names). This is directly measurable from the developer's own chain data and should be measured rather than assumed.

### CLAIM (DISCONFIRMING, and this undercuts a project premise): The S&P 500 variance risk premium has itself largely disappeared since about 2012.
- **SOURCE:** Dew-Becker & Giglio, "The decline of the S&P 500 variance risk premium", Federal Reserve Bank of Chicago working paper 2025-17 / dated 2 June 2026. [WP, Federal Reserve] — https://www.dew-becker.org/documents/option_decline.pdf ; https://www.chicagofed.org/-/media/publications/working-papers/2025/wp2025-17.pdf
- **EVIDENCE STRENGTH:** Strong
- Monthly returns Aug 1987–Aug 2025 (N=457), baseline break Aug 2012 (301 pre, 156 post). Before 2012, SPX option strategies had significantly negative mean returns and CAPM alphas; after 2012 the premia largely disappear. Straddle alpha change significant at 5%; a Hodges-Lehmann test dates the change to **2006–2010** for beta-adjusted returns.
- Straddle Sharpe ratios: Driessen & Maenhout report −0.21 for 1987–2001, the authors find −0.74 on the same sample; **after 2001 it is −0.09, and after 2012 it is +0.12 with the alpha turning positive.**
- VIX overstated realised volatility by ~25% in the high-premium era (18.7 implied vs 15 realised) but only ~10% in the most recent ten-year window (16.4 implied).
- The 95% put remains negative but is no longer statistically significant post-2012. The authors state a mean-variance investor would assign roughly zero weight to straddles. They note trading costs and basis risk have fallen, which they link to reduced dealer frictions, and are explicit that they are not forecasting future returns.
- **IMPLICATION FOR THE BUILD:** This is the most consequential disconfirming finding in the strand and it is not about sectors at all. The project's standing conclusion that "the index VRP is robust while the single-name VRP is not harvestable" needs revision: a 2026 Federal Reserve working paper finds the index VRP has not been statistically distinguishable from zero for roughly a decade. Any sector-ETF premium-harvesting design inherits this problem. **Before building sector-level premium harvesting, re-derive the index-level premium on post-2012 data only.**

---

## 6. IMPLIED CORRELATION AND DISPERSION AT SECTOR LEVEL

### CLAIM: No sector-level implied correlation index is published. Cboe's suite is S&P 500-only.
- **SOURCE:** Cboe, "Market Expectations About Future Diversification Benefits" (implied correlation index page). [LIVE/exchange] — https://cboe.com/us/indices/implied/ ; methodology https://cdn.cboe.com/resources/indices/documents/Implied_Correlation-WhitePaper.pdf
- **EVIDENCE STRENGTH:** Strong
- COR3M (and COR1M) measure average expected correlation among the **top 50 SPX stocks**, from ATM delta-relative constant-maturity SPX index and component option implied volatilities. Cboe also presents correlation skew- and term-structure views. **No sector-basket implied correlation index or ticker exists.** Cboe's own commentary notes that sector correlation could separate systematic market risk from industry-level risk — presented as research commentary, not as a product.
- **IMPLICATION FOR THE BUILD:** A sector implied correlation would have to be constructed from each sector ETF's IV plus every constituent's IV and weight. For XLF that is ~70 constituent IV surfaces refreshed daily. **Data obtainability: poor.** Given that the project already found market-level implied correlation usable only as a regime filter and *not* as a cross-sectional selector, building a worse-measured sector version to get a filter the market version already provides is not justified.

### CLAIM: The documented basket dispersion risk premium is in *style* baskets, not sectors, and is statistically insignificant for the S&P 500 itself.
- **SOURCE:** Gerchik, Ruffo, Schönleber & Vilkov, "Factor Dispersions", working paper, 15 March 2024 (Cboe research publication). [WP, exchange-hosted] — https://cdn.cboe.com/resources/education/research_publications/FactorDispersionWhitepaper.pdf
- **EVIDENCE STRENGTH:** Moderate for the measurement, **No credible evidence found** for sector dispersion tradeability
- Dispersion defined as weighted individual variances minus basket variance. Universe: SPX plus five smart-beta baskets (Value, Pure Value, Growth, Quality, Low Vol), using options on SPX and the ETFs IVE, IVW, RPV, SPHQ, SPLV. **No sector baskets.**
- The dispersion risk premium (realised minus implied) is positive and significant for most baskets, but the **S&P 500's is near zero and insignificant (−0.19, p=0.155)**. SPX realised dispersion 4.33 vs implied 4.54 vol points.
- Smart-beta baskets retain exposure to all factors, so even a "pure" factor dispersion loads on every factor's variance. For most baskets the systematic component explains only ~40% of realised dispersion; idiosyncratic variance drives the rest.
- Ex-ante dispersion and its premium carry signal about future systematic volatility and anomaly returns.
- The paper discusses dispersion swaps and basket options but **reports no Sharpe ratios, leg counts, or transaction cost assumptions for dispersion trades.** It notes that a block-diagonal covariance with per-industry equicorrelations (after Buss, Schönleber & Vilkov) is possible but does not build it.
- **IMPLICATION FOR THE BUILD:** Sector dispersion is genuinely untested — nobody has published it. And the sign pattern in the one adjacent study is the *opposite* of what the project assumed: the broad-index dispersion premium is insignificant while style-basket premiums are significant. Combined with the project's own prior (index dispersion needs ~21 legs monthly at 6–8% spreads, independent replications at Sharpe 0.34–0.40), a sector version with ~25–70 legs at single-name spreads of ~10% of premium is categorically worse. **Exclude.**
- Adjacent, not obtained: Bawa, "Has the Correlation Risk Premium Been Competed Away? Evidence from Implied and Realized Correlation, 2006–2026", SSRN 7361499 — fetch blocked, but the title suggests it bears directly on whether the correlation premium survives; worth retrieving.
- Foundational: Driessen, Maenhout & Vilkov, "Option-Implied Correlations and the Price of Correlation Risk" [PR] — https://pages.stern.nyu.edu/~rengle/Maenhout-S2005.pdf (the project already relies on this).

---

## 7. SECTOR-RELATIVE VALUATION AND FACTOR STRUCTURE

### CLAIM: Measuring firm characteristics relative to industry gives more precise estimates and each characteristic is reliably priced within-industry — but this is a cross-sectional factor-construction improvement, not a per-name signal.
- **SOURCE:** Asness, Porter & Stevens, "Predicting Stock Returns Using Industry-Relative Firm Characteristics", SSRN 213872, 2000. [WP] — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=213872
- **EVIDENCE STRENGTH:** Moderate (widely cited; magnitudes and t-statistics not obtainable from the accessible page)
- Each characteristic (size, book-to-market, cash-flow-to-price, employee growth, past returns) is split into a within-industry component (firm minus industry average) and an across-industry component (industry average). The within-industry measurement yields more precise estimates than the common raw form, and each variable is reliably priced within-industry. Within-industry momentum has predictive power beyond across-industry momentum. A significant one-month industry momentum effect persists among the most liquid firms.
- **HORIZON:** Monthly cross-sectional. **DECAY EVIDENCE:** None; the paper is 26 years old and the accessible version reports no subperiods.
- **IMPLICATION FOR THE BUILD:** Industry-adjustment is a *measurement* improvement for a cross-sectional long-short portfolio. The project has already established that single-name direction prediction is worth ~7 bp/month gross and −1 to +4 bp/month net. Making the characteristic cleaner improves the t-statistic of a portfolio effect; it does not turn 7 bp/month into something that pays 10% of premium. **Use sector-relative ranking as a screen/presentation refinement — "cheap for a utility" rather than "cheap" — and not as a signal.** This is a human-interface improvement, which connects to the project's existing interface strand.
- Related, not obtained: "Industry-adjusted book-to-market ratio and value premium", *Finance Research Letters*, 2025 — https://www.sciencedirect.com/science/article/abs/pii/S1544612325016010

---

## 8. SECTOR-LEVEL VOLATILITY AS AN ANCHOR FOR SINGLE-NAME VOL FORECASTS

### CLAIM: No study was found testing whether sector ETF implied volatility improves a single-name volatility forecast, but the mechanism is supported by the documented common factor in idiosyncratic volatility.
- **EVIDENCE STRENGTH:** **No credible evidence found** for the specific claim; Moderate for the mechanism
- **SOURCES (mechanism):**
  - Herskovic, Kelly, Lustig & Van Nieuwerburgh, "The Common Factor in Idiosyncratic Volatility", NBER WP 20076 / *Journal of Financial Economics*, 2016. [PR] — https://www.nber.org/system/files/working_papers/w20076/revisions/w20076.rev0.pdf. Establishes a strong *market-wide* common factor (CIV) in firm-level idiosyncratic volatility. This is the mechanism that would make any common vol anchor work, but it is a single market-wide factor, not a sector decomposition.
  - Kambouroudis, McMillan & Katsiampa, "Forecasting realized volatility: the role of implied volatility, leverage effect, overnight returns, and volatility of realized volatility", *Journal of Futures Markets*, 2021. [PR] — https://onlinelibrary.wiley.com/doi/full/10.1002/fut.22241. Establishes that implied volatility adds information to HAR-type realised volatility forecasts.
- **HORIZON:** Days to one month. **DECAY EVIDENCE:** n/a.
- **IMPLICATION FOR THE BUILD:** This is the **best risk-adjusted candidate in the whole strand**, precisely because it is a forecasting input rather than a trade. Sector ETF IV30 is free or near-free to obtain for the ~11 SPDR sectors plus SMH/XBI/KRE; adding it as a third component to the project's existing two-component volatility forecast costs nothing in execution and can be validated out-of-sample on data the developer already has. The evidence does not say it will work; it says the mechanism exists and nobody has tested it at sector granularity. **Build it as a measured experiment with a pre-registered out-of-sample criterion, not as an assumed improvement.** Note the honest caveat: if the CIV literature is right that the common factor is market-wide rather than sector-wide, the index VIX may capture most of the benefit and the sector layer may add nothing. Test sector IV *against* VIX as the control, not against the name's own history alone.

---

## 9. MANDATORY SECTIONS

### INDUSTRY VS INDIVIDUAL MOMENTUM VERDICT

**No. Momentum does not work better at sector level in any way that changes the product decision.**

The magnitudes:
- Original (Moskowitz–Grinblatt 1999, 1963–1995): industry momentum 0.43%/month raw, 0.20%/month DGTW-adjusted (t=2.27). Individual momentum 0.29%/month adjusted (t=3.34). **Comparable, not larger.** The famous result is not that industry momentum is *bigger* — it is that industry-neutralising individual momentum kills it (t=1.01).
- Sector ETF implementable version (Andreu/Swinkels/Tjong-A-Tjoe 2013, Dec 1998–Dec 2009): 0.27–0.67%/month, breakeven cost 65 bp/trade.
- Long sample (Grobys & Kolari 2020, 1926–2018): 0.57–0.80%/month, dominated by pre-1990 decades.

The decay and the demolition — four separate attacks, each sufficient on its own:
1. **The gap month.** Grundy & Martin: insert one month between formation and holding and industry momentum falls to an insignificant 0.16%/month. Roughly 60% of the headline effect is one-month reversal a retail account cannot trade.
2. **Connected firms.** Ali & Hirshleifer (2020): controlling for connected-firm momentum leaves industry momentum with no significant four-factor alpha.
3. **Factor momentum.** Arnott et al. (2021) and Ehsani & Linnainmaa (2022): momentum in the top principal components of industry-neutral factors subsumes *all* industry momentum, and does so completely in the second half of 1973–2019.
4. **Turnover.** Dimensional: the one industry momentum result with reliable alpha beyond stock-level premiums required 500% annualised one-way turnover (vs 15–35% for stock-level factor portfolios); slowing to semiannual or annual rebalance more than halved the alpha and made it unreliable.

And the literature is internally contradictory on the central claim: Asness, Porter & Stevens (2000) find within-industry momentum has power *beyond* across-industry momentum, directly against Moskowitz–Grinblatt.

**Cross-sectional or per-sector absolute?** Strictly cross-sectional. Every result above is a long-short rank across 10–48 industries, rebalanced monthly. I found **no credible evidence** for a per-sector absolute time-series momentum signal — the sector analogue of the project's existing finding that time-series momentum had 8 of 55 significant slopes and 45 of 55 negative out-of-sample R². There is no reason to expect the sector version to behave better; with 11 sectors instead of 55 names, there is less data to establish it.

**Against the cost hurdle.** 0.4%/month gross on the underlying, with a skip-month haircut to roughly 0.16%/month, and the project's standing 80–90% haircut on published equity effects, leaves 2–3 bp/month. In **ETF shares** at 1–3 bp spreads and 12 rebalances a year, that is break-even at best. In **sector ETF options** at 2–4% round trip monthly, it is nowhere close. Option leverage multiplies the signal and the variance by the same factor, so it does not rescue the Sharpe.

**Verdict for the build:** do not build a sector momentum signal. If a sector tilt is wanted for any other reason, express it in ETF shares, rebalance no more often than quarterly, and present it as a tilt rather than a forecast. The one defensible use of industry momentum in this project is as a **display context** — "energy is the strongest sector this quarter" alongside a name — which costs nothing and makes no claim.

### SECTOR ETF VS SINGLE NAME

| Dimension | Liquid sector ETF (SMH, XLE, XLF) | Mid-tier sector ETF (XLP, KRE, XLI, XLB, XLU, XBI) | Thin sector ETF (XLK, XLY, XLV, XLRE, XLC) | Liquid single name | Index (SPY/QQQ/IWM) | Index (SPX/XSP) |
|---|---|---|---|---|---|---|
| Options ADV (Cboe group, 2026 YTD) | 37k–60k | 9k–14k | 3k–5k, XLRE/XLC not in top 100 | highly variable | 420k–2.76M | n/a (separate venue) |
| Expected round-trip cost, % of premium | **not measured; expect between index ~2% and single-name ~10%** | expect worse than the liquid tier | expect single-name-like or worse | **median 10.1% measured; only 29.3% at or under 5%** | **~2% at 42–48 DTE measured** | ~2% |
| Strike/expiry grid | weeklies, dense strikes | monthlies plus some weeklies | sparse; verify per chain | variable; most names fail the project's ≥10-qualifying-contract test (36 of 103) | deepest available | deep, plus cash settlement |
| Qualifying-contract depth | unknown — **measure** | likely marginal | likely fails | median 7 of the project's 103 names | SPY+QQQ+IWM = 50.7% of all qualifying contracts | n/a |
| Premium harvestability (VRP) | **unknown — no published sector-ETF VRP study** | unknown | unknown | not harvestable (zero premium unrejectable for 108 of 135 names) | **index VRP itself insignificant post-2012** (Dew-Becker & Giglio) | same as SPY, plus cleaner |
| Tax | **equity options — no 1256** | equity options | equity options | equity options | **equity options — SPY/QQQ explicitly excluded from 1256** | **Section 1256, 60/40, no wash sales, mark-to-market** |
| Idiosyncratic exposure | diversified away | diversified away | diversified away | full | diversified away | diversified away |
| Event triggers available | sector-wide and bellwether earnings | same | same | the name's own earnings | macro only | macro only |

**Recommendation — when to express a view in the ETF instead of the single name:**

1. **When the view is sector-wide, always, and only in SMH/XLE/XLF (plus the mid-tier after measuring the chain).** The cost gradient is the whole argument. Single-name options cost ~10% of premium at the median and only 29.3% of in-band contracts come in under 5%; index options at 42–48 DTE run ~2%. Liquid sector ETF options must sit between those, and XLE/XLF/SMH trade at volumes an order of magnitude above XLK/XLY/XLV, so the gradient within the sector tier is as large as the gap to single names.
2. **Never for a name-specific view.** The ETF diversifies away exactly the idiosyncratic component a name-specific view is about. Trading XLF instead of JPM is not a cheaper JPM trade; it is a different trade.
3. **Never for tax reasons.** Sector ETF options are equity options. The tax ranking is SPX/XSP ≫ sector ETFs = single names = SPY/QQQ. If tax is a live input, that argues for the index layer.
4. **Not yet for premium harvesting.** Two unknowns compound: no published sector-ETF VRP estimate exists, and the index VRP that was the reference case has been statistically indistinguishable from zero since roughly 2012.
5. **The build must whitelist by measured chain quality, re-measured annually.** "Sector ETF" is not a liquidity category — XLV at 3,137 contracts/day is worse than many single names. Penny Interval Program membership turns over each January/April and is conditional on the underlying trading under $200, so a sector ETF can lose penny status purely by appreciating.

**What to measure next, on the developer's own chain data** (this is the cheapest high-value work in the strand): run the existing in-band cost measurement across all 14 sector ETFs and compare the distribution to the 103 single names and to SPY/QQQ/IWM. That single run would replace every "expect" in the table above with a number, and it uses tooling that already exists.

### PEER INFORMATION TRANSFER

**Is a peer's earnings a usable trigger? For direction, no. For volatility, unproven but the only live lead in this strand.**

The first-moment (direction) channel is dead against the cost hurdle. Cheng et al. (2022) measure average three-day peer excess returns of 0.09% and −0.19% — 9 to 19 bp. Single-name options cost ~10% of premium round trip. The effect is two orders of magnitude too small. It is also measured outside the US, and the paper's own moderators (richer information environments produce less overreaction) predict the effect is weakest in the US.

The second-moment (volatility) channel is real but has not been shown to be tradeable:
- Hann, Kim & Zheng (2019, *Review of Accounting Studies*) establish a significant positive association between a first announcer's IV change and its peers' IV changes, surviving controls for return transfer, and stronger for bellwether announcers, long-dated options, and high macro uncertainty. They define straddle-return variables and do not report results for them. No magnitudes were obtainable.
- Ogneva, Xia & Ye (2024) find spillover *magnitude* is predictable (past spillovers predict future spillovers) while finding **no drift or reversal over the following seven hours**. The market prices the spillover immediately.

Taken together: peer earnings move peer volatility, the size of the move is forecastable, the direction is not, and the repricing is instantaneous. That rules out a latency trade and points to a pure volatility-level trade.

**Trigger density.** Mechanically, peer transfer is a large multiplier. A sector with one bellwether and 20–70 members turns one earnings date into 20–70 dated events, and each of the ~11 sectors has 2–4 bellwethers per quarter. Against the project's measured liquidity reality — 36 of 103 names carried ≥10 qualifying contracts, median 7 — the constraint on event-mode density was never a shortage of *events*, it was a shortage of *tradeable chains*. **Peer transfer multiplies events in exactly the dimension that was not binding.** It does not help.

**The one hypothesis worth testing.** Because peer transfer is a sector-wide uncertainty resolution, its natural expression is the *sector ETF's* implied volatility around a bellwether report — XLF around JPM, SMH around NVDA, XLV around UNH. That trade pays 2–4% rather than 10%, uses one chain rather than 20, and is a volatility-level trade rather than a direction trade, which is the only mode the project's prior research leaves standing. **No study tests it: evidence strength, No credible evidence found.** It is cheap to measure from the developer's own data (sector ETF IV before and after each bellwether report, versus a matched non-event window), and it is the single most promising untested idea this strand produced. Treat it as a hypothesis to measure, not a feature to build.

### SECTOR SIGNAL TABLE

| Candidate | Evidence | Horizon | Decay evidence | Data obtainability | In the build? |
|---|---|---|---|---|---|
| Industry momentum, cross-sectional rank | Moderate original, **demolished** by gap-month, connected-firm, factor-momentum and turnover findings | 1–12m formation, monthly rebalance | Strong against: no post-2009 test of the ETF version; factor momentum absorbs it entirely in the later subsample | High (price data only) | **No.** Display context at most |
| Industry momentum, per-sector absolute (time-series) | **No credible evidence found** | — | — | High | **No** |
| Business-cycle sector rotation | **Strong against** (Molchanov & Stangl: Sharpe 0.20 vs market 0.21 with perfect foresight; 0.01–0.07%/mo after costs) | Quarters | n/a — never worked | High | **No** |
| Relative-strength sector rotation | Weak (Faber: Sharpe 0.54, costs excluded, 100–400% turnover, 46% drawdown) | Monthly | None published; heavily copied | High | **No** |
| Cross-industry news sentiment (supply-chain weighted) | Weak-to-Moderate (IR 0.95 gross, halves to 0.55 on dictionary change, no costs, sample ends 2011) | Monthly | None; 15 years stale, no replication found | **Poor** (BEA I-O tables + tagged news corpus) | **No** — data cost is the binding constraint |
| Peer earnings → peer *direction* | Moderate statistically, **Weak for use** (9–19 bp vs 10% hurdle, non-US sample) | 3 days | None | Moderate (earnings calendars + peer map) | **No** |
| Peer earnings → peer *implied volatility* | Moderate for existence, **No credible evidence** for tradeability | [−3,+3] days | None | Moderate | **No** — but see next row |
| Bellwether earnings → **sector ETF** IV | **No credible evidence found** (untested) | [−3,+3] days | — | **High** (one chain, known dates) | **Measure first.** Highest-value experiment in this strand |
| Sector ETF as cheaper vehicle for a sector-wide view | Strong on liquidity gradient (volume data), **unmeasured** on cost-as-%-of-premium | n/a — vehicle choice | Penny-program membership and $200 eligibility change annually | **High** (developer's own chain measurement) | **Yes, conditionally** — whitelist by measured chain quality, re-measure yearly |
| Sector ETF options tax advantage | **Strong against** — equity options, not 1256 | n/a | n/a | n/a | **No such advantage exists** |
| Sector ETF variance risk premium harvesting | **No credible evidence found**; and the index reference case is itself insignificant post-2012 | 30d | **Strong against at index level** (Dew-Becker & Giglio) | High (own chain data) | **No** until the index-level premium is re-derived on post-2012 data |
| Sector implied correlation as regime filter | **No credible evidence**; no index published; market version already exists and is filter-only | Weeks–months | n/a | **Poor** (all constituent IV surfaces) | **No** — market COR1M/COR3M already serves this |
| Sector dispersion trade | **No credible evidence** (untested); adjacent study finds the broad-index premium insignificant | Monthly | n/a | Poor | **No** — 25–70 legs at ~10% of premium |
| Sector-relative valuation / industry-adjusted characteristics | Moderate (Asness/Porter/Stevens: better measurement, reliably priced within-industry) | Monthly cross-sectional | None; 26 years old | **High** (sector classification + fundamentals) | **Yes, as a screen and display refinement**, never as a signal |
| Sector ETF IV as a third component in the volatility forecast | **No credible evidence** for the specific claim; Moderate for the mechanism (CIV; IV adds to HAR) | Days–1 month | n/a | **High** (free sector ETF IV) | **Yes, as a pre-registered out-of-sample experiment** with VIX as the control, not the name's own history |

### DISCONFIRMING EVIDENCE

1. **Sector effects are substantially repackaged factor exposure.** Arnott, Clements, Kalesnik & Linnainmaa (2021) show that momentum in the three highest-eigenvalue principal components of industry-neutral factors subsumes *all* industry momentum. Ehsani & Linnainmaa (2022) find factor momentum explains all momentum in lower-eigenvalue PCs in the second half of their 1973–2019 sample. Ali & Hirshleifer (2020) find industry momentum has no significant four-factor alpha once connected-firm momentum is controlled. Three independent subsumption results is not a robust anomaly.

2. **Industry-level premiums add nothing beyond stock-level premiums, per an asset manager with every commercial incentive to claim otherwise.** Dimensional tested US industries 1975–2021 and found that after requiring value *added over* stock-level premiums, nothing survived: emerging-market industry momentum had reliable alpha but at 500% annualised one-way turnover (vs 15–35% for stock-level factors), and slowing the rebalance more than halved the alpha and made it unreliable.

3. **Business-cycle sector rotation fails under maximally generous assumptions.** Molchanov & Stangl (*IJFE* 2024) grant the strategy perfect ex-post knowledge of NBER turning points, test in-sample only, and still find Sharpe 0.20 against 0.21 for the market and 0.26 for naive market timing. Of 1,022 strategy variants only 12.9% beat buy-and-hold; of 2,160 cross-sector predictability t-statistics, 6% were significantly positive and 5% significantly negative, which is chance. With 0.5–1.5% costs the 11 bp/month gross edge falls to 1–7 bp and becomes insignificant. Under FF3 and Carhart, no industry shows significant outperformance — only some show significant *under*performance.

4. **The raw sector-rotation edge is higher beta, not skill.** Molchanov & Stangl's base case runs volatility of 5.02% vs 4.23% for the market with beta 1.04, and the apparent outperformance largely disappears once Fama-French and Carhart factors are added. What remains resembles market timing (moving to cash in recessions) more than sector selection — and the cash version achieves more with 21 round trips instead of 53.

5. **The original industry momentum result depends on a one-month component that cannot be traded.** Moskowitz & Grinblatt themselves report that skipping one month eliminates IM(1,1) profitability and that high turnover means those profits likely do not survive costs. Grundy & Martin's gap-month version falls to an insignificant 0.16%/month.

6. **The literature contradicts itself on the headline claim.** Moskowitz & Grinblatt say industry momentum subsumes individual momentum; Asness, Porter & Stevens say within-industry momentum has power beyond across-industry momentum. Both are heavily cited. A 20–40 bp/month gross effect with a split literature is not a basis for a product decision.

7. **The implementable sector-ETF version has not been tested in 17 years.** Andreu, Swinkels & Tjong-A-Tjoe's sample ends December 2009. I found no published post-2009 test of sector ETF industry momentum. Their own FF3-alpha specification omits a momentum factor, so the paper cannot establish that industry momentum adds anything beyond single-stock momentum in the first place.

8. **The index variance risk premium — the project's reference case for "robust" — has itself largely disappeared.** Dew-Becker & Giglio (Chicago Fed WP 2025-17, dated June 2026) date the change to 2006–2010 and find straddle Sharpe of −0.74 pre-2001, −0.09 after 2001, and **+0.12 after 2012 with a positive alpha**. VIX overstated realised volatility by ~25% in the high-premium era and only ~10% in the last decade. They state a mean-variance investor would hold roughly zero weight in straddles. Any sector-level premium-harvesting design inherits this.

9. **The documented basket dispersion premium has the wrong sign pattern for this project's assumption.** Gerchik et al. find the dispersion risk premium positive and significant for style baskets but **near zero and insignificant for the S&P 500 itself** (−0.19, p=0.155). Systematic variance explains only ~40% of realised dispersion in most baskets, so a "sector dispersion" trade would be mostly idiosyncratic variance — the component the project already established is unpriced.

10. **The hoped-for tax advantage does not exist.** Sector ETF options are equity options. Only broad-based index options (SPX, XSP, NDX, RUT) receive Section 1256 60/40 treatment, mark-to-market and wash-sale exemption; SPY and QQQ are explicitly excluded, as are ETF options generally. Moving a position from a single name to a sector ETF changes nothing about its tax treatment.

11. **The one sector-level sentiment result halves on a defensible methodological change.** Scognamiglio & de Zwart's cross-industry news sentiment gives IR 0.95 with the Harvard IV-4 dictionary and IR 0.55 with Loughran-McDonald — the dictionary the finance literature regards as correct. No costs or turnover are reported, and the sample ends in 2011.

12. **Peer information transfer in the first moment is two orders of magnitude too small.** Average three-day peer excess returns of 9–19 bp against a ~10%-of-premium cost hurdle.

13. **Sector ETF options liquidity does not generalise.** XLV (3,137 contracts/day), XLY (4,327) and XLK (5,126) are thinner in options than many large single names; XLRE and XLC do not appear in the top 100 ETFs by options volume at all. The naive claim "sector ETFs are more liquid than single names" is false for 5 of the 11 SPDR sectors.

### OPEN QUESTIONS

1. **What is the actual in-band cost, as % of premium, of sector ETF options?** This is the pivotal unknown and it is measurable with tooling the developer already has. Until it is measured, the whole "cheaper vehicle" argument rests on an interpolation between 2% (index) and 10.1% (single name).
2. **Does the sector ETF variance risk premium behave like the index or like single names, and does it survive the post-2012 regime?** Hypothesis worth testing: the premium scales with constituent count and internal correlation, so XLF (~70 holdings) should look more index-like than XLE (~23, top-heavy). Requires the paywalled Zhu (2023, *Journal of Futures Markets*) on industry variance risk premium — **the most important unretrieved source in this strand.**
3. **Does a bellwether's earnings release produce a predictable, tradeable drop in its sector ETF's implied volatility?** Completely untested. Measurable from the developer's own chain data plus an earnings calendar.
4. **Has sector ETF industry momentum survived 2009–2026?** No published test exists. The developer could run it on free data in an afternoon, with a skip-month, quarterly rebalance, and realistic ETF-share costs — and should treat a null result as the expected outcome.
5. **Does sector ETF IV30 improve the project's two-component volatility forecast beyond what VIX already contributes?** The CIV literature suggests the common idiosyncratic-volatility factor may be market-wide, in which case VIX captures most of the benefit and the sector layer adds nothing. Must be tested with VIX as the control.
6. **Has the correlation risk premium been competed away?** Bawa's SSRN paper (abstract 7361499) covering 2006–2026 could not be retrieved and bears directly on whether the index VRP's decline extends to the correlation premium the project relies on as a regime filter.
7. **How stable is penny-increment status for the sector ETFs?** The $200 underlying-price eligibility condition means a successful sector ETF can lose tight quoting by appreciating. Worth checking historically for XLK.
8. **Does industry-relative ranking improve the *presentation* of candidates enough to matter?** This is a human-interface question, not a signal question, and it connects to the project's existing interface strand rather than to anything in this one.

### TOP 10 SOURCES, RANKED

1. **Dew-Becker & Giglio (2026), "The decline of the S&P 500 variance risk premium"**, Chicago Fed WP 2025-17 [WP, Federal Reserve] — https://www.dew-becker.org/documents/option_decline.pdf. Ranked first because it undercuts a premise the project treats as settled, with a clean break test and an explicit sub-period Sharpe series.
2. **Molchanov & Stangl (2024), "The myth of business cycle sector rotation"**, *International Journal of Finance & Economics* [PR] — https://onlinelibrary.wiley.com/doi/full/10.1002/ijfe.2882. Definitive peer-reviewed refutation of sector rotation, under perfect-foresight assumptions, with cost accounting.
3. **Moskowitz & Grinblatt (1999), "Do Industries Explain Momentum?"**, *Journal of Finance* [PR] — http://www-stat.wharton.upenn.edu/~steele/Courses/956/Resource/Momentum/MoskowitzGrinblatt99.pdf. The anchor, including its own cost warnings and breakeven estimates.
4. **Macroption, "Most Active ETFs by Options Volume"** (Cboe group, 2026 YTD to 28 Aug) [LIVE] — https://www.macroption.com/etf-options-volume/. The only hard liquidity data in this strand, and it overturns the naive sector-ETF story for 5 of 11 SPDR sectors.
5. **Dimensional, "Why the Benefits of Betting on Industries and Countries Are Few and Far Between"** [AM] — https://www.dimensional.com/us-en/insights/why-the-benefits-of-betting-on-industries-and-countries-are-few-and-far-between. Ranked high despite being asset-manager material because it argues against a product it could sell, and the 500%-vs-15–35% turnover figure is the cleanest statistic here.
6. **Hanauer-style review (2022), "Momentum: what do we know 30 years after Jegadeesh and Titman's seminal paper?"**, *Financial Markets and Portfolio Management* [PR] — https://link.springer.com/article/10.1007/s11408-022-00417-8. The efficient route to Grundy & Martin, Ali & Hirshleifer, Arnott et al. and Ehsani & Linnainmaa.
7. **Andreu, Swinkels & Tjong-A-Tjoe (2013), "Can ETFs be used to exploit industry and country momentum?"**, *Financial Markets and Portfolio Management* [PR] — summary https://agnosticinvesting.com/2023/12/agnostic-papers/agpa-73-country-and-industry-momentum/. The only study of the implementable sector-ETF version, with breakeven costs; sample ends 2009.
8. **Hann, Kim & Zheng (2019), "Intra-industry information transfers: evidence from changes in implied volatility around earnings announcements"**, *Review of Accounting Studies* 24(3) [PR] — https://care-mendoza.nd.edu/assets/293764/hann_kim_zheng_rast_oct2018.pdf. Establishes peer IV transfer and its bellwether conditioning; reports no strategy.
9. **Gerchik, Ruffo, Schönleber & Vilkov (2024), "Factor Dispersions"** [WP, Cboe-hosted] — https://cdn.cboe.com/resources/education/research_publications/FactorDispersionWhitepaper.pdf. Nearest thing to sector dispersion, and its insignificant SPX premium is a warning.
10. **Equicurious, "Tax Rules for Options Trading: Section 1256 and Equity Options"** [reference] — https://equicurious.com/learn/investing-basics/taxes-and-regulations/tax-rules-for-options-trading-section-1256-and-equity-options. Low-prestige source, high decision value: it closes the sector-ETF tax question definitively.

**Also cited above:** Asness, Porter & Stevens (2000) SSRN 213872; Cheng, Fang, Huang & Zhong (2022) *JIAR* 21(1); Ogneva, Xia & Ye (2024) WP; González-Urteaga & Rubio (2016) *JFE* 119(2); Herskovic, Kelly, Lustig & Van Nieuwerburgh (2016) *JFE*; Kambouroudis et al. (2021) *JFM*; Cboe implied correlation index page and Penny Interval Program update; OptionScout XLF snapshot 2026-11-12.

**Not retrieved, flagged for follow-up:** Zhu (2023) "Industry variance risk premium, cross-industry correlation, and expected returns", *Journal of Futures Markets* (paywalled); Truong (2025) "Does Industry Sentiment Explain Industry Returns?" (robots-disallowed); Bawa, "Has the Correlation Risk Premium Been Competed Away? 2006–2026", SSRN 7361499; Mamais (2025) "Explaining and Predicting Momentum Performance Shifts Across Time and Sectors", *Journal of Forecasting* (fetch blocked); "Industry-adjusted book-to-market ratio and value premium", *Finance Research Letters* 2025.
