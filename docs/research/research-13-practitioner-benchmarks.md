# Strand 13: Professional & Systematic Options Strategies, and the Benchmark Hurdle

Research date: 11 November 2026. All sources verified by web search/fetch, not memory.

**Source labelling convention used throughout:**
`[PEER]` peer-reviewed journal · `[WP]` academic working paper (not yet peer-reviewed) · `[INDEX]` index-provider / sponsored research · `[INDEP]` independent third-party analysis · `[PRACT]` practitioner commentary · `[MKTG]` fund marketing

---

## PART 1: THE BENCHMARK QUESTION

### 1.1 The CBOE option-strategy benchmark indices — actual long-run numbers

**CLAIM:** Over 1986–2018, CBOE option-writing benchmark indices delivered *slightly lower absolute returns* than the S&P 500 but materially lower volatility and shallower drawdowns, producing higher Sharpe ratios — all gross of transaction costs and taxes.

**SOURCE:** Wilshire Associates, "Options-Based Benchmark Indexes: Performance, Risk and Diversification Characteristics," commissioned/co-funded by Cboe, 2019. [INDEX] — https://cdn.cboe.com/resources/spx/wilshire-options-based-benchmark-indexes-2019.pdf

Period 30 Jun 1986 – 31 Dec 2018, monthly:

| Index | Ann. return | Ann. std dev | Sharpe | Sortino | Max drawdown |
|---|---|---|---|---|---|
| **BXM** (buy-write, ATM) | 8.50% | 10.6% | 0.51 | 0.40 | −35.8% |
| **BXMD** (buy-write, 30-delta OTM) | 10.22% | 12.8% | 0.55 | 0.49 | −42.7% |
| **PUT** (cash-secured put-write) | 9.54% | 9.9% | **0.64** | 0.43 | −35.5% |
| **CMBO** (combo) | 9.20% | 10.9% | 0.55 | 0.44 | −38.1% |
| **PPUT** (5% protective put) | 6.64% | 12.1% | 0.29 | 0.32 | −38.9% |
| **S&P 500** | 9.80% | 14.9% | 0.45 | 0.42 | −50.9% |
| US Agg Bond | 6.13% | 3.8% | 0.78 | 0.77 | −5.1% |

**EVIDENCE STRENGTH:** Moderate. The index data are reliable but this is Cboe-funded research; the study itself discloses the results are hypothetical backtests excluding transaction costs and taxes. The document reports *inconsistent Sharpe ratios for the same index across different exhibits* (S&P 500 appears as 0.45, 0.44 and 0.66 in Exhibits 8, 9c and 9b) with no explanation — a genuine quality flag.

**IMPLICATION FOR THE BUILD:** The honest long-run risk-adjusted hurdle from a passive rules-based option index is **Sharpe ≈ 0.64 with max drawdown ≈ −33% to −36%**, and that number is gross of costs. Note CLL (collar) and CNDR (condor) were absent from this study — I found no comparable long-run audited series for them, so no hurdle can be set from them.

---

**CLAIM:** The put-write index's apparent edge shrinks to nothing in the modern subsample.

**SOURCE:** Oleg Bondarenko (Univ. of Illinois Chicago), "Historical Performance of Put-Writing Strategies," Cboe-sponsored, 2019. [INDEX] — https://cdn.cboe.com/resources/education/research_publications/PutWriteCBOE19_v14_by_Prof_Oleg_Bondarenko_as_of_June_14.pdf

- 1986–2018: PUT 9.54% / 9.95% vol / Sharpe 0.65 / MDD −32.7%; S&P 500 9.80% / 14.93% / 0.49 / −50.9%.
- **2006–2018: PUT 5.97% vs S&P 500 7.59%. Sharpe 0.50 vs 0.51 — a dead heat.** WPUT (weekly put-write) 4.51%, Sharpe 0.40 — materially *worse* than the index.
- VRP evidence: 1990–2018 VIX averaged 19.3% vs S&P realized 15.1%, a 4.2 pp gap.

**EVIDENCE STRENGTH:** Moderate (sponsored, backtested, no costs — the paper explicitly concedes costs "could be significantly higher" for these strategies than for buy-and-hold).

**IMPLICATION FOR THE BUILD:** The famous "put-writing has a higher Sharpe than the index" result is **driven by 1986–2005**. Post-2006 it vanishes. Any benchmark set from the full 1986–2018 sample is set from a regime that no longer exists. Also note the *weekly* variant underperformed the monthly one — directly relevant since higher-frequency selling means more cost drag.

---

**CLAIM:** Since 2018 the buy-write index has lost badly, trailing the S&P 500 in every single year in which the S&P returned 10%+.

**SOURCE:** First Trust Portfolios, "An Update on Covered Call Returns," 11 Sep 2025. [PRACT/asset-manager, but raw index data] — https://www.ftportfolios.com/Commentary/MarketCommentary/2025/9/11/an-update-on-covered-call-returns

| Year | S&P 500 | BXM | Gap |
|---|---|---|---|
| 2025 YTD (to 9/9) | 11.73% | 1.15% | −10.58 pp |
| 2024 | 25.00% | 20.12% | −4.88 pp |
| 2023 | 26.26% | 11.82% | −14.44 pp |
| 2022 | −18.13% | −11.37% | **+6.76 pp** |
| 2021 | 28.71% | 20.47% | −8.24 pp |

Across the full history: the S&P had 13 years of 10%+ returns and **BXM trailed in all 13**. The S&P had three negative years (2008, 2018, 2022) and BXM beat it in two (in 2018 BXM actually lost slightly more: −4.77% vs −4.38%).

**EVIDENCE STRENGTH:** Strong on the data (verifiable index returns); the interpretive framing is from an asset manager that sells competing products.

**IMPLICATION FOR THE BUILD:** The option-writing benchmark is a *bull-market-lagging* benchmark. If the developer backtests over 2019–2026 and beats BXM, that proves nothing — holding SPY would also have beaten BXM by a wide margin. **BXM is the wrong benchmark. SPY/VOO is the benchmark.**

---

### 1.2 Does passive rules-based option selling beat active selection? — the decomposition result

**CLAIM:** A covered call is ~67% passive equity beta, ~26% uncompensated equity-timing risk, and only ~7% short volatility — and the short-vol sliver is the only part that is compensated.

**SOURCE:** Roni Israelov & Lars N. Nielsen (AQR), "Covered Calls Uncovered," *Financial Analysts Journal* 71(6), Nov/Dec 2015. [PEER] — https://www.aqr.com/Insights/Research/Journal-Article/Covered-Calls-Uncovered (PDF: https://abramofranchetti.github.io/FireSWR/covered_call/Covered%20Calls%20Uncovered.pdf)

Sample 25 Mar 1996 – 31 Dec 2014, ATM covered call, annualised excess returns:

| Component | Excess return | Volatility | Sharpe | Share of risk |
|---|---|---|---|---|
| Covered call (total) | 5.9% | 11.4% | 0.52 | 100% |
| Passive equity | 3.5% | 8.5% | 0.41 | 67% |
| **Short volatility** | **1.9%** | **1.9%** | **0.98** | **7%** |
| Equity timing | 0.5% | 4.8% | 0.10 (t = 0.4) | 26% |

Hedging away the timing component raised BXM's Sharpe from 0.37 to 0.52 and cut volatility from 11.4% to 9.2%; downside beta fell 0.85 → 0.60.

**EVIDENCE STRENGTH:** Strong. Peer-reviewed, top-tier journal, replicated decomposition logic, authors have no incentive to flatter covered calls.

**IMPLICATION FOR THE BUILD:** This is the most useful structural insight in the strand. **The compensated part of option selling has a Sharpe near 1.0 but carries only 7% of the risk.** Everything else is beta you could buy more cheaply, plus a quarter of your risk budget spent on a timing exposure with a t-statistic of 0.4. If the developer wants the VRP, the efficient expression is a *delta-hedged* short-vol position sized small — not a covered call. And a system that merely selects *which* covered call to write is tinkering with 7% of the risk.

---

**CLAIM:** Round-trip S&P 500 call selling has lost money on average since 1999, and lost more the higher the targeted yield.

**SOURCE:** Roni Israelov & Ndong, "A Devil's Bargain" (Oct 2023), reviewed by Larry Swedroe, Alpha Architect, Nov 2023. [WP, reviewed by INDEP] — https://alphaarchitect.com/covered-calls/

- Jan 1999 – Jun 2023: a 6% yield target lost 0.60%/yr; a 12% target lost 1.08%/yr.
- **2011 – mid-2023: the 6% target lost 3.1%/yr and the 12% target lost 4.7%/yr.**
- High-yield calls had equity beta ≈ 0.75 vs ≈ 1.0 for low-yield calls: extra VRP exposure did not offset the forgone equity premium.
- The authors attribute this to crowding in yield-enhancement strategies compressing call premiums, leaving calls *under*valued.

**EVIDENCE STRENGTH:** Strong on direction and mechanism; Moderate on precise magnitudes (working paper, backtested). Note the lead author is the same researcher as the 2015 FAJ paper, so this is not independent confirmation — it is the same team updating.

**IMPLICATION FOR THE BUILD:** Call selling as a yield source is now *negative alpha*, and getting worse over time. The crowding explanation matters: the developer's system would be entering a trade whose premium has been competed down by the exact ETF complex discussed below.

---

### 1.3 The option-income ETF complex — independent analysis

**CLAIM:** QYLD and XYLD sacrificed far more return than risk, producing clearly lower Sharpe ratios than their own benchmarks.

**SOURCE:** Swedroe / Alpha Architect, Nov 2023, citing fund data. [INDEP] — https://alphaarchitect.com/covered-calls/

| Comparison | Period | Ann. return | Std dev | Sharpe | Max DD |
|---|---|---|---|---|---|
| QYLD vs QQQ | Jan 2014–Sep 2023 | **6.4% vs 16.5%** | 11.8% vs 18.4% | **0.49 vs 0.86** | −22.7% vs −32.6% |
| XYLD vs VOO | Jul 2013–Sep 2023 | **6.6% vs 12.6%** | 12.1% vs 14.9% | **0.50 vs 0.77** | −23.4% vs −23.9% |

QYLD's return was ~61% below QQQ's while its volatility was only ~36% lower. XYLD's drawdown reduction versus VOO was negligible (0.5 pp). Both funds yielded 11.5–12.3% as of Nov 2023 while having lost ~5% over the prior three months — the clearest possible demonstration that yield ≠ return.

**EVIDENCE STRENGTH:** Strong (live fund total returns, not backtests).

---

**CLAIM:** Live total returns through November 2026 confirm the pattern: every option-income ETF trailed the plain index, and the long-history ones trailed by 6 pp/yr.

**SOURCE:** totalrealreturns.com, dividends-reinvested total return series, retrieved 11 Nov 2026. [INDEP] — https://totalrealreturns.com/n/SPY,SPYI,QQQI,JEPI,JEPQ,VOO and https://totalrealreturns.com/n/XYLD,JEPI,SPYI,JEPQ,QYLD,QQQI

Period 30 Jan 2024 – 11 Nov 2026 (dividends reinvested):

| Fund | CAGR | Max DD |
|---|---|---|
| **VOO** | **+18.44%** | −18.69% |
| **SPY** | **+18.37%** | −18.76% |
| QQQI | +16.71% | −20.00% |
| SPYI | +15.77% | −16.47% |
| JEPQ | +15.52% | −20.07% |
| QYLD | +12.58% | −19.06% |
| XYLD | +12.54% | −15.53% |
| JEPI | +9.63% | −13.26% |

Ten-year rolling to 11 Nov 2026: **SPY +15.18%/yr, VOO +15.26%/yr** vs **XYLD +8.40%/yr, QYLD +9.50%/yr**.

**EVIDENCE STRENGTH:** Strong. Live, dividend-adjusted, independent data source.

**IMPLICATION FOR THE BUILD:** Over the last decade the two longest-running covered-call ETFs delivered roughly **55–62% of the index's compound return**. The newer, better-designed entrants (SPYI, QQQI, JEPQ) have closed much of the gap but still trail on total return while barely reducing drawdown (SPYI −16.5% vs SPY −18.8%; JEPQ −20.1% vs SPY −18.8% — JEPQ had a *worse* drawdown than SPY). The upside-capture problem is real and quantified.

---

**CLAIM:** The investable put-write vehicle has delivered roughly 57% of SPY's five-year return.

**SOURCE:** PortfoliosLab, PUTW vs SPY comparison, retrieved Nov 2026. [INDEP] — https://portfolioslab.com/tools/stock-comparison/PUTW/SPY

| Metric | PUTW | SPY |
|---|---|---|
| 5-yr annualised | **8.99%** | **15.71%** |
| 3-yr annualised | 7.76% | 10.16% |
| 1-yr | 22.29% | 34.88% |
| Daily std dev | 9.03% | 12.18% |
| Max drawdown | −28.40% | −55.19% |

**EVIDENCE STRENGTH:** Moderate-to-Strong (live fund data; the two max-drawdown figures cover different histories — PUTW launched Feb 2016, so it never saw 2008 — so that comparison is not like-for-like).

**IMPLICATION FOR THE BUILD:** This is the *actually investable* version of the CBOE PUT index. The index showed 9.54%/yr with Sharpe 0.64; the fund tracking it returned 8.99%/yr over five years while SPY returned 15.71%. The gap between index backtest and live fund is the implementation cost the CBOE studies omit.

---

**CLAIM:** Serious practitioners argue these products carry equity-like risk with lower returns, and that a trivial 50/50 stock/T-bill blend has recently beaten the flagship products.

**SOURCE:** Kris Abdelmessih (former volatility trader, *Party at the Moontower*), "Derivative Income Bumhunting," citing QVR Advisors, former market-maker Mark Phillips, and Israelov & Ndong. [PRACT, high-credibility] — https://moontowermeta.com/derivative-income-bumhunting/

Key points: QVR characterise covered-call and put-write strategies as "equity-like risk with lower returns," argue the VRP is not persistently positive, and note that **a 50/50 S&P 500 / T-bill benchmark recently outperformed JHEQX and JEPI**. Phillips argues blind systematic option selling or buying is "almost certainly a performance drag," that there are real edges in options but that mechanical premium selling is not one of them, and that passive index investing is the actual edge available to an individual. QVR frame their own repeatable alpha as providing liquidity to *price-insensitive* derivative end-users — a service requiring balance sheet and infrastructure.

**EVIDENCE STRENGTH:** Moderate (practitioner commentary, but from people with verifiable vol-trading backgrounds, and the quantitative claims trace to the peer-reviewed/working-paper literature above). Abdelmessih discloses that his sources have commercial interests in the topic.

---

### 1.4 A hidden artifact in the benchmark data

**CLAIM:** The 135 bp/yr gap between the PUT and BXM indices is explained by an a.m.-settlement price bias, not by put-writing being a better strategy.

**SOURCE:** Guido Baltussen (Erasmus/Northern Trust), Julian Terstegge (CBS), Paul Whelan (CUHK), "The Derivative Payoff Bias," version Jan 2024. [WP] — https://afajof.org/management/viewp.php?n=98196

- SPX options settle a.m. on the third Friday via the Special Opening Quotation. The SOQ exceeds the prior close by ~18.5 bp on third Fridays (t > 4.5), an effect appearing only after ~2003.
- This transfers wealth from call writers to call buyers and from put buyers to put writers — estimated at ~$3.8bn/yr in SPX options (the paper reports $2.7bn, $3.8bn and ~$4bn in different sections).
- **The authors attribute the ~135 bp/yr BXM-vs-PUT gap to this settlement reversal.**
- Relative to counterfactual settlement, overnight returns were ~+34% for ATM calls and ~−20% for ATM puts.

**EVIDENCE STRENGTH:** Moderate. Statistically robust within sample (2003–2021), but a working paper, the mechanism is unidentified (the authors say the manipulation question "remains to be demonstrated"), and the dollar estimates are model-based and internally inconsistent.

**IMPLICATION FOR THE BUILD:** Do not treat "PUT beats BXM" as a strategy insight to replicate. It is substantially a settlement artifact. More broadly: this is a warning that *published option-index performance differences can be microstructure artifacts*, which is the recurring theme of Part 3.

---

## PART 2: WHAT SYSTEMATIC OPTIONS FUNDS AND PROP VOL TRADERS ACTUALLY TRADE

### 2.1 Volatility risk premium harvesting — and its documented decline

**CLAIM:** The alpha of delta-hedged index options has fallen to zero since roughly 2012; the VRP now compensates only for market beta.

**SOURCE:** Ian Dew-Becker (Northwestern) & Stefano Giglio (Yale), "The Decline of the Variance Risk Premium: Evidence from Traded and Synthetic Options," Federal Reserve Bank of Chicago Working Paper 2025-17, 4 Sep 2025. [WP, Fed-published] — https://www.chicagofed.org/-/media/publications/working-papers/2025/wp2025-17.pdf

- Structural break dated **May 2012**. Traded-option information ratio moved from about **−0.6 before the break to +0.09 after** it.
- The authors state the alpha of delta-hedged options has gone to zero.
- 1987–2005 (the classic sample): traded put information ratios as negative as −0.75, alphas significantly negative. Over the full post-1987 sample, alpha magnitudes were about half those of the classic sample.
- Traded put cumulative returns were **flat from March 2009 through December 2022**.
- Synthetic option alphas were near zero across 1926–2022 and never significantly negative in any rolling 10-year window.
- Mechanism: frictions once prevented most investors from selling options, so dealers bore large negative gamma and charged for it. Dealer net gamma went from consistently negative pre-2012 to near zero/slightly positive afterwards; trading costs and basis risk fell. Unhedgeable risk measures (jump variation, skewness) did *not* shrink, so they cannot explain the decline.
- The authors are careful: the VRP is **not** zero — but what remains is no larger than CAPM beta implies.

**EVIDENCE STRENGTH:** Strong. Fed working paper, two well-regarded asset-pricing researchers, century-long synthetic-option cross-check, explicit structural-break test, and a mechanism supported by dealer positioning data.

**IMPLICATION FOR THE BUILD:** **This is the most consequential finding in the strand.** The entire option-selling edifice — CBOE indices, VRP harvesting, and the delta-hedged option literature — rests on a premium that a Fed working paper dates as having disappeared in 2012. Every strong result cited in favour of option selling (Israelov's Sharpe-0.98 short-vol component ends 2014; Bondarenko's and Wilshire's good numbers come from 1986–2005; Zhan et al.'s sample is pre-2018) is estimated substantially *before or across* this break. The developer would be building a system to harvest a premium whose alpha the best recent evidence says is gone.

---

### 2.2 Dispersion trading

**CLAIM:** Dispersion trading shows strong backtested returns that survive modelled costs, but requires ~21 simultaneous option legs, has a −43% drawdown, and is rated "very complex."

**SOURCE:** Quantpedia strategy page summarising Buraschi, Trojani & Vedolin, "Equilibrium Index and Single-Stock Volatility Risk Premia," plus Schneider & Stübinger. [INDEP aggregator of PEER sources] — https://quantpedia.com/strategies/dispersion-trading

- Primary source (1996–2007): 15.39%/yr after transaction costs, 13.86% volatility, **Sharpe 0.82, max drawdown −43.49%** (Quantpedia's page is internally inconsistent about whether the drawdown figure is stated — treat with caution).
- Schneider & Stübinger (S&P 500 subsetting): 14.52% and 26.51%/yr after costs, but Sharpe only **0.40 and 0.34**.
- **Transaction costs are the crux:** average quoted bid-ask spreads of **6.23% for index options and 8.29% for single-stock options**. Executing at bid/ask cut the dispersion straddle from 19.9% to 11.5% monthly, and the dispersion put from 2.7% to 1.2% monthly.
- Structure: 20 single-stock options + 1 index option, rebalanced monthly. Quantpedia rates complexity "Very Complex" and warns it is "absolutely not a hedge" — a fat-tail strategy that loses heavily in crises when correlations spike.

**EVIDENCE STRENGTH:** Moderate. The underlying academic sources are peer-reviewed, but the sample ends 2007, the cost treatment is modelled rather than executed, and the two independent implementations produce Sharpe ratios half the headline figure.

**IMPLICATION FOR THE BUILD:** **Not retail-implementable.** Twenty-one legs rebalanced monthly, each crossing a 6–8% spread, is a cost structure no retail account survives. A retail trader also cannot access variance swaps or correlation swaps, which is how professionals actually express this cleanly. The strategy's loss profile (−43% drawdown, concentrated in correlation spikes) is precisely the risk a single-user account cannot ride out. Note also that whether the correlation risk premium still exists in 2026 is contested; I found only non-peer-reviewed SSRN work on that question and did not verify it.

**OVERLAP NOTE:** Spread magnitudes here belong to the execution-microstructure agent's lane; I report them only as the binding constraint on this strategy.

---

### 2.3 Relative-value vol: calendars, skew RV, surface arbitrage

**CLAIM:** No credible peer-reviewed evidence of a retail-implementable edge in calendar-spread term-structure dislocation, skew relative value, or vol-surface arbitrage.

**SOURCE:** Dedicated search returned only practitioner blogs and commercial content (flashalpha.com, optionsfunding.co, groww.in, dev.to, journalplus.co). No peer-reviewed or index-provider evidence located. Related academic work found (Samuelson effect in crude calendar spreads; Chinese index-futures calendar lead-lag) is not about equity-option RV strategies.

**EVIDENCE STRENGTH:** **No credible evidence found.** The absence of academic work on these strategies, contrasted with the dense literature on VRP and characteristic-based option returns, is itself informative: these are discretionary dealer activities, not documented systematic premia.

**IMPLICATION FOR THE BUILD:** Do not build a surface-arbitrage module. Professionals trade these off an inventory position, a funding advantage and a flow view — none of which the developer has. Any backtest the developer produces here would be unfalsifiable against the literature because there is no literature to falsify it against.

---

### 2.4 Gamma scalping and delta-hedged vol trading

**CLAIM:** No credible evidence found that gamma scalping is viable at retail transaction costs.

**SOURCE:** Dedicated search returned only commercial/educational content (incredmoney.com, arongroups.co, traderc.com, tradewink.com, daystoexpiry.com, coinswitch.co) plus genuine but non-applicable quantitative-finance papers on optimal hedging under small transaction costs (arXiv 1209.2555) and deep-RL gamma/vega hedging (arXiv 2205.05614). The one promising independent analysis (dependability.us) did not resolve to substantive content.

**EVIDENCE STRENGTH:** **No credible evidence found** for retail viability; the relevant academic work addresses institutional hedging-cost optimisation and is framed around *reducing* an unavoidable hedging cost, not earning a profit.

**IMPLICATION FOR THE BUILD:** Gamma scalping requires intraday rebalancing of a stock position against an option position. Combined with the Dew-Becker/Giglio finding that delta-hedged option alpha is now zero, the activity reduces to paying spreads and commissions to harvest a premium that no longer has alpha. Do not build it.

---

### 2.5 Tail hedging and convexity

**CLAIM:** Protective puts usually reduce risk-adjusted outcomes rather than improving them, and simply holding less equity dominates buying puts.

**SOURCE:** Roni Israelov, "Pathetic Protection: The Elusive Benefits of Protective Puts," *Journal of Alternative Investments*, Winter 2019 (dated 31 Dec 2018). [PEER] — https://www.aqr.com/Insights/Research/White-Papers/Pathetic-Protection-The-Elusive-Benefits-of-Protective-Puts

- Puts reduce drawdowns only in the unusual joint case where options carry no VRP *and* the drawdown coincides with the option's holding window.
- With a VRP present — which the author argues is almost always the case in index options — put protection can *increase* drawdowns and volatility per unit of expected return.
- Conclusion: because of path dependence and option expensiveness, puts "may do more harm than good."
- Preferred alternative: reduce equity exposure (a fixed equity/cash split), or diversify into liquid alternatives.

Corroborating data point: **PPUT (5% protective put index) returned 6.64%/yr with Sharpe 0.29 and a −38.9% max drawdown over 1986–2018 — it both underperformed the S&P 500 by 3.2 pp/yr and had a worse Sharpe than every option-writing index** (Wilshire 2019 [INDEX]). Bondarenko reports PPUT's *longest* drawdown at 80 months, versus 73 for the S&P 500 — the hedge lengthened the recovery.

**EVIDENCE STRENGTH:** Strong for the proposition that systematic put-buying is costly. The counter-case exists and is serious (see Disconfirming Evidence), and AQR has an institutional interest in trend-following as the alternative.

**IMPLICATION FOR THE BUILD:** A tail-hedge module is not a defensible use of effort. The cheapest convexity available to this developer is cash.

---

### 2.6 Carry and roll-down

**CLAIM:** Index put option carry showed the highest Sharpe ratio of any carry strategy across asset classes (1.80) — but carry strategies lose in exactly the states where you need them, and the put-carry strategy was the most extreme example.

**SOURCE:** Ralph Koijen (Chicago), Tobias Moskowitz (Yale), Lasse Pedersen (Copenhagen/AQR), Evert Vrugt, "Carry," working paper Nov 2013 (subsequently *Journal of Financial Economics* 2018). [PEER] — https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2014/06/Carry.pdf

- US equity index options, Jan 1996 – Dec 2011: **put option carry Sharpe 1.80 (highest of any asset class); call option carry Sharpe 0.37 (lowest).** Average across asset classes 0.74; diversified Global Carry Factor 1.10. Passive long exposures averaged 0.21.
- **Critical caveat:** during the Global Carry Factor's three largest drawdowns (all coinciding with global recessions), every carry strategy lost money and most did worse than passive exposure to the same market. **Index put options returned about +132%/yr passively during those periods while the put-carry strategy returned about −22%/yr.**
- The paper does **not** run a formal net-of-cost analysis. It notes carry faces larger transaction costs, funding and limits-to-arbitrage than passive strategies, and suggests the high Sharpe ratios may partly *be* compensation for those frictions.
- A footnote reports VIX futures carry predicts their returns, but the authors declined to build a strategy from it because the history is short and contracts illiquid.

**EVIDENCE STRENGTH:** Strong methodology and peer review; Weak on net-of-cost implementability, which the authors explicitly did not test. The options sample ends 2011 — before the Dew-Becker/Giglio break.

**IMPLICATION FOR THE BUILD:** Put carry's Sharpe 1.80 is the most seductive number in this strand and should be treated with the most suspicion: it is gross of costs, ends in 2011, and the same paper documents that the strategy returns −22%/yr precisely when the passive alternative returns +132%/yr. That is not a risk premium a single-user account with no outside capital can hold through. Volatility carry and roll-down are *the same economic exposure as VRP harvesting* expressed differently — they are not a diversifying third source of return.

---

## PART 3: DELTA-HEDGED OPTION RETURN HARVESTING AT RETAIL SCALE

This is the strand's second critical question, and the evidence is worse than expected.

### 3.1 The look-ahead bias result

**CLAIM:** When the firm-characteristic delta-hedged option strategy is rebuilt using only information available at the time of trading, its gross return falls from 2.27% to 0.10% per month — a ~96% reduction, before any transaction costs.

**SOURCE:** Jefferson Duarte (Rice), Christopher S. Jones (USC), Mehdi Khorram (Iowa State), Haitao Mo (Kansas), Junbo L. Wang (LSU), "Too Good to Be True: Look-Ahead Bias in Empirical Option Research," **forthcoming in the *Review of Financial Studies*** (accepted 2025; working version Oct 2023). [PEER, forthcoming] — https://sfs.org/rfs-forthcoming-paper-79/ · reviewed at https://cxoadvisory.com/equity-options/look-ahead-bias-in-option-trading-backtests and https://www.business.rice.edu/wisdom/when-research-promises-impossible-investors-pay-price

- The bias: studies used a contract's **average price over the full trading day** to select trades at the *start* of that same day. No trader can know the day's average until the close.
- **Stock-characteristic strategy (profitability example), Jan 2012 – Jun 2020: average gross monthly return fell from 2.27% to 0.10%** — a drop of 2.17 pp/month.
- Liquidity-provision strategy (calls), Jan 1996 – Apr 2016: gross monthly return fell from 1.52% to 0.19%.
- One influential study reporting >3% average *daily* returns produced "much smaller" returns with higher risk once corrected.
- The paper examines three influential empirical options papers.

**EVIDENCE STRENGTH:** Strong. Forthcoming in the *Review of Financial Studies* — the same journal that published Zhan, Han, Cao & Tong (2022). Five authors across five institutions. The correction is methodologically unambiguous.

**IMPLICATION FOR THE BUILD:** **This is the finding that answers the brief's highest-value question.** The "stock-characteristic delta-hedged option" strategy is precisely the Zhan/Han/Cao/Tong family. Corrected, it earns **0.10% per month gross** — roughly 1.2%/yr before spreads, commissions, and stock-side hedging costs. Against option bid-ask spreads of 6%+ and the need to rebalance a stock hedge, **0.10%/month is comfortably negative net.** I could not access the paywalled full text to confirm the paper tests Zhan et al. *by name*, so the precise mapping is an open question — but the strategy class, the characteristic used (profitability), the data source and the sample period all match.

---

### 3.2 The risk-adjustment result

**CLAIM:** Most firm-characteristic delta-hedged option-return predictability is explained as compensation for risk once dynamic characteristic-based betas are allowed, not as abnormal profit.

**SOURCE:** Amit Goyal (Lausanne) & Alessio Saretto (Dallas Fed), "Are Equity Option Returns Abnormal? IPCA Says No," Federal Reserve Bank of Dallas Working Paper 2214, Aug 2022. [WP, Fed-published] — https://www.dallasfed.org/-/media/documents/research/papers/2022/wp2214.pdf

- Delta-hedged calls, 1996–2020: 29 of 44 characteristics produce statistically significant average returns, some with t > 10.
- Under IPCA, alphas fall by **roughly 50% to 75%** depending on model and position. The RV−IV long-short strategy earns ~3.6%/month (t ≈ 20) raw but only ~1.0% alpha (t ≈ 9.4) under IPCA.
- After multiple-testing adjustment, IPCA leaves only **five** significant alphas among the long-short portfolios (IV ATM, IV slope, IV term, RV−IV, BM). Competing models leave 34, 30 and 14.
- For signal-weighted portfolios, only **1 of 23** strategies with significant returns retains a significant IPCA alpha.
- The paper **confirms Zhan et al.'s predictability** — profit margin, profitability, cash-to-assets and new issuance all have significant coefficients in the authors' own regressions — but **contradicts the interpretation**, concluding that "the extant evidence on option trading strategies presents no significant challenges to market efficiency."

**EVIDENCE STRENGTH:** Strong. Fed working paper, Goyal is a leading authority on predictability out-of-sample. Caveat: IPCA is a flexible latent-factor model and critics reasonably note that a sufficiently flexible risk model can absorb any anomaly; "explained by risk" is not the same as "not profitable."

**IMPLICATION FOR THE BUILD:** Notably, the five characteristics that *do* survive are all **option-implied** variables (IV level, IV slope, IV term structure, RV−IV) plus book-to-market — **not** the accounting fundamentals that make Zhan et al. attractive. If anything survives, it is implied-volatility structure, which belongs to the volatility-forecasting agent's lane.

---

### 3.3 The microstructure-artifact result

**CLAIM:** Delta-hedged option return premiums can be manufactured entirely by rebalancing frequency interacting with microstructure noise in the underlying.

**SOURCE:** Jelena Eberbach, Matthias Molnar, Philipp Schuster, Marliese Uhrig-Homburg (KIT/Stuttgart), "Asset Pricing Results in Options Markets: True, Spurious, or Overlooked?", Oct 2025. [WP] — https://www.fma.org/assets/docs/Derivatives2025/Molnar.pdf

Simulated (Black-Scholes base case):
- Mean call return bias ~**92 bp/month with 30-minute rebalancing** vs ~17–25 bp with end-of-day strategies. The "indirect mean return" (IMR) bias accounts for ~88 bp of that, ~96% of the total.
- **Spurious high-minus-low premium for high- vs low-spread underlyings: ~300 bp/month at 30-minute rebalancing, ~22 bp daily, ~2 bp static.** Fama-MacBeth slope on underlying bid-ask spread: 10.90 (30-min) vs 0.03 (bi-weekly).
- With a Leland (1985) hedging-cost premium embedded, the true premium is ~−83 bp (dealers net short) but the *measured* premium at 30-minute rebalancing is ~+226 bp — **the wrong sign**.
- Proposed fix (lagging delta one step) restores ~−81 bp and removes most spurious significance.

**EVIDENCE STRENGTH:** Moderate. Rigorous but entirely simulation-based; the authors concede magnitudes depend on calibrated noise/spread/frequency assumptions. It does not replicate published anomalies and does not test firm characteristics broadly (it focuses on underlying bid-ask spread and vol-elasticity).

**IMPLICATION FOR THE BUILD:** Two practical lessons. First, **the less frequently you hedge, the smaller the bias — and static hedging is nearly bias-free (~2 bp).** This is the key: a retail trader who cannot hedge frequently is also not exposed to the bias that inflates the literature's reported returns. Second, if the developer ever builds a delta-hedged backtest, hedge frequency must be a reported parameter and delta must be lagged, or the backtest will manufacture its own premium.

---

### 3.4 What delta-hedging actually costs at retail

I found **no** study that estimates retail-specific delta-hedging costs for a characteristic-sorted option portfolio. Reconstructing from the pieces above:

- The Zhan et al. strategy is a *cross-sectional* long-short across many names. The option legs sit in single-stock options, where the dispersion literature measures average quoted spreads of **8.29%** ([INDEP/PEER], §2.2).
- Each name requires a stock-side hedge rebalanced at least daily to approximate the published methodology. Commission-free equity trading removes commissions but not spread or the discrete-hedging error.
- Eberbach et al. show the premium's *measured* size scales with hedge frequency, and that the economically true premium under realistic dealer positioning may be **negative** (~−83 bp).
- The corrected gross return is **0.10%/month** (§3.1).

0.10%/month gross against an 8.29% round-trip option spread means the spread alone consumes **several years** of gross return per rebalance. There is no plausible arithmetic in which this is positive at retail.

**EVIDENCE STRENGTH:** Moderate (a synthesis I constructed from verified components, not a single cited estimate — flagged as such).

---

## PART 4: OVERLAY AND PORTFOLIO-LEVEL APPROACHES

**CLAIM:** The best-known study of option overlays on a 60/40 portfolio reports favourable results but excludes transaction costs entirely and prices every leg at mid.

**SOURCE:** Carlos Chujoy, Joy Seth, Satitpong Chantarajirawong (Employees Retirement System of Texas), "Use of Option Strategies to Improve Risk-Adjusted Returns on a 60/40 Investment Portfolio," July 2016; data supplied by CBOE. [WP, data-sponsored] — https://cdn.cboe.com/resources/education/research_publications/research-paper.pdf

- 11 overlays tested at 25% notional of portfolio assets, six downside-protection and five income-enhancement.
- All 11 had positive returns over the full 25 years to March 2015. Bull put spread, short put and short straddle were the best performers.
- During the Aug 2000 – Sep 2002 downturn, total risk ranged 8.24% (short risk reversal) to 14.06% (long iron condor); max drawdowns 11.66% to 20.45%.
- **Appendix B states no transaction costs were included and mid prices were used for both long and short transactions.** No Sharpe ratios are reported.

**EVIDENCE STRENGTH:** **Weak as evidence for implementation.** Mid-pricing a short straddle overlay for 25 years is not a cost assumption, it is the absence of one. For a 25%-notional overlay rebalanced monthly at 6%+ index-option spreads, the omitted cost is first-order.

---

**CLAIM:** No credible academic evidence located that cash-secured put ladders or systematic overlays improve risk-adjusted returns for an *individual* net of costs and taxes.

**SOURCE:** Dedicated search surfaced the CBOE-sponsored 60/40 study above, Neuberger Berman's put-writing marketing [MKTG], Ninepoint's "equity alternative" piece [MKTG], BNP Paribas AM equity-overlay material [MKTG], Allspring's options-based downside protection (explicitly labelled "Marketing Communication") [MKTG], and two ResearchGate entries on the cash-secured put-write strategy and the variance risk premium that I could not verify in full text.

**EVIDENCE STRENGTH:** **No credible independent evidence found.** The literature on this specific question is dominated by product marketing. This is itself a finding: the institutions that would benefit most from demonstrating overlay value have published marketing rather than peer-reviewed evidence.

**IMPLICATION FOR THE BUILD:** There is a *weaker but still defensible* argument for overlays that does not require an edge: a cash-secured put ladder on a name the developer wants to own anyway converts a limit order into a paid limit order, and a covered call on a holding they intend to trim converts a target price into a paid target price. Neither requires predictive skill; both are *execution* reframings of decisions already made. That is the only overlay use this evidence base supports — and critically, it is an argument for a **decision-support tool**, not a signal engine.

**IMPORTANT TAX CAVEAT (flagged, not researched):** US retail option-writing overlays generate short-term capital gains and, for in-the-money equity calls, can suspend the holding period for long-term treatment on the underlying. Swedroe flags "more tax realizations" as an explicit cost. This is outside my brief and is unresearched here, but it is a real drag that none of the index backtests include and it falls on no other agent's lane.

---

## PART 5: COMPETITION, CAPACITY, AND WHERE RETAIL EDGE MIGHT EXIST

### 5.1 Who is on the other side

**CLAIM:** Retail is now the majority of US options volume, and three wholesalers intermediate almost all of it.

**SOURCE:** Svetlana Bryzgalova, Anna Pavlova, Taisiya Sikorskaya (London Business School), "Retail Trading in Options and the Rise of the Big Three Wholesalers," Sep 2023, **forthcoming in the *Journal of Finance***. [PEER, forthcoming] — https://www.sikorskaya.net/files/Bryzgalova_Pavlova_Sikorskaya_2023.pdf

- Retail reached **over 60% of total options market volume** (62% estimated from Rule 606 data). Retail dollar volume rose ~101% from Jan 2020 to Jul 2021.
- Brokers received ~**$2.4bn** from options PFOF in 2021 vs ~$1.3bn from equities. **Citadel, Susquehanna and Wolverine took nearly 90% of options PFOF by Q2 2021.**
- **Price improvement is real and large:** quoted spreads on these trades average ~**13.7%** but effective spreads are ~**6.7%**.
- ~**50% of retail trades are in options expiring within a week**, where average quoted spread is 12.6%.
- Retail investors lost ~**$2.1bn** Nov 2019 – Jun 2021 (10-day holding assumption). **Indirect trading costs ~$6.4bn versus direct commissions of ~$900m.**
- Losses concentrate in **long** positions in short-dated options. **Investors who sold those contracts earned profits on average.**

**EVIDENCE STRENGTH:** Strong. Forthcoming in the *Journal of Finance*, regulatory (Rule 606) data, large sample.

---

**CLAIM:** Retail option trades lose ~0.9% each on average including all costs — but short option positions were the profitable exception.

**SOURCE:** Vincent Bogousslavsky (Boston College) & Dmitriy Muravyev (UIUC), "An Anatomy of Retail Option Trading," working paper 8 Feb 2025. [WP] — https://www.brettonwoodsskiconference.com/uploads/b/f9bfc8b0-0251-11ed-a646-3dea17112d2f/An%20Anatomy%20of%20Retail%20Option%20Trading.pdf

- Average option trade returns **−0.9%** including commissions, fees and spreads; stock trades near zero. Sample ~$15bn in trades.
- Per trader-month: option-only traders lose ~**$547**; stock-only traders earn ~$62 (not significant).
- **0DTE options lose ~4.7% per trade** univariately (2.3–3% worse than other options after controls).
- Index/ETF options ~−3% vs single-stock options ~**+0.15%**.
- **Option purchases lose ~4%. Naked option sales — only ~13% of option trades — earn ~20%.** Trader fixed effects do not explain the buyer/seller gap, so it is not a skill difference.
- **Trade size matters: traders averaging under $200/trade lose ~3.4% per option trade vs ~1.4% for those averaging over $5,000.**
- The average loss (−0.9%) is *smaller* than the typical quoted spread (3.7%), implying retail traders do get fills better than quoted — consistent with limit-order use and with the price improvement above.
- The authors note the sample is trade-journal users and may not represent all retail.

**EVIDENCE STRENGTH:** Moderate-to-Strong (large, granular, but a working paper with a self-selected sample the authors acknowledge).

**IMPLICATION FOR THE BUILD:** Two concrete, actionable asymmetries, both of which are *structural rather than predictive*:
1. **Short beats long, and it is not a skill effect.** +20% for naked sales vs −4% for purchases, with trader fixed effects ruling out selection. Both this paper and Bryzgalova et al. find the same thing independently.
2. **Size and tenor dominate everything.** Sub-$200 trades lose 2.4 pp more per trade than $5,000+ trades; 0DTE loses 2.3–3 pp more than other tenors; single-stock options beat index/ETF options by over 3 pp. These are larger effects than any direction signal in the research programme (~7 bp/month) and they require no forecasting at all.

**Caution on #1:** the +20% figure is a *per-trade* average on a position whose loss distribution is unbounded and whose sample (Nov 2019 – 2024) contains no sustained bear market. A 13%-frequency strategy earning +20% per trade in a period containing only the brief 2020 and 2022 drawdowns is exactly the pattern that precedes a large loss. Treat it as evidence about *cost structure* (sellers collect the spread rather than paying it), not as evidence of a 20% edge.

---

### 5.2 Where professionals say retail edge actually exists

**CLAIM:** Credible practitioners locate retail edge in not trading options systematically at all, or in flow-provision services retail cannot supply.

**SOURCE:** Abdelmessih / Moontower, citing Mark Phillips (former options market-maker) and QVR Advisors. [PRACT] — https://moontowermeta.com/derivative-income-bumhunting/

- Phillips: there are plenty of edges in options, but blind systematic option selling is not one, because there is "nothing particularly systematic" about it. He frames passive index investing as the individual's real edge, illustrating with an 80/20 stock/bond portfolio at $1,000/month over 40 years returning ~9.7%/yr to ~$5.3m.
- QVR: their repeatable alpha comes from **providing liquidity to price-insensitive derivative end-users** and from anticipating predictable fund rebalances — both requiring balance sheet, infrastructure and flow visibility.
- Abdelmessih: "nobody's job is to stand there and slurp risk for free."
- QVR note HFRX equity-hedge up-down capture of +31.6% through the GFC versus −8.7% after it — i.e. the hedged-equity complex stopped working post-crisis.

**EVIDENCE STRENGTH:** Moderate (practitioner, self-interested sources disclosed by the author, but quantitative claims trace to the literature).

---

**CLAIM:** No credible evidence found that a small options account has an exploitable capacity advantage in small or illiquid underlyings.

**SOURCE:** A dedicated search for small-account capacity advantage in options returned only the general equity size-premium literature (AQR "Fact, Fiction and the Size Effect"; OSAM; MSCI; Morningstar) — nothing about options in small or underfollowed names.

**EVIDENCE STRENGTH:** **No credible evidence found.** And there is a strong structural reason to expect none: options on small, underfollowed names have the *widest* spreads and thinnest open interest. The capacity advantage that is real in small-cap *equities* inverts in small-cap *options*, because the cost of accessing them scales with exactly the illiquidity that creates the opportunity. Bogousslavsky & Muravyev's finding that small trades lose more per trade is direct evidence against a small-size advantage in options.

**IMPLICATION FOR THE BUILD:** The retail structural advantages that are genuinely verified here are narrow and mostly *negative* (things to avoid): no forced selling, no benchmark pressure, the ability not to trade, and real price improvement on small orders (quoted 13.7% → effective 6.7%). The ability to be patient is real but it is an argument for *fewer* trades, which is an argument against building a signal engine.

---

## THE BENCHMARK HURDLE

The specification currently has no benchmark. Here is one, with numbers.

### The wrong benchmark

**Do not benchmark against BXM.** BXM returned 8.50%/yr over 1986–2018 and trailed the S&P 500 in all 13 years the index returned 10%+. Beating BXM over any recent window is achieved by holding SPY. Using an option-strategy index as the benchmark builds in a handicap that flatters the system.

### The primary hurdle: total return

**Passive alternative: VOO (Vanguard S&P 500 ETF), 0.03% expense ratio.**

- 10-year annualised to 11 Nov 2026: **+15.26%/yr** (SPY +15.18%/yr)
- 30 Jan 2024 – 11 Nov 2026: **+18.44%/yr**, max drawdown −18.69%

The system must beat **15.3%/yr net of all costs, commissions, spreads and taxes, over a decade-equivalent sample**, or it has destroyed value relative to a single ticker bought once.

### The secondary hurdle: risk-adjusted return

Three tiers, because the developer may legitimately prefer lower volatility:

1. **Best long-run rules-based option index (gross):** CBOE PUT — **Sharpe 0.64, 9.9% volatility, max drawdown −32.7% to −35.5%**. But note this collapses to **Sharpe 0.50 vs the S&P's 0.51 over 2006–2018**, so it is a hurdle from an expired regime.
2. **Best *investable* option-writing vehicle:** PUTW — **8.99%/yr over five years vs SPY's 15.71%**, max drawdown −28.4%. Or SPYI at **+15.77%/yr** (Jan 2024 – Nov 2026) with a −16.5% drawdown, versus SPY's +18.37% and −18.8%. SPYI is the strongest member of the complex and it still trails on total return while cutting drawdown by only 2.3 pp.
3. **The embarrassing hurdle:** a **50/50 S&P 500 / T-bill blend**, which QVR report recently outperformed both JEPI and JHEQX. This requires no options, no model, no maintenance and no tax friction. Any volatility-reduction objective the developer has should be tested against this first, because a static equity/cash split is Israelov's own recommended alternative to both protective puts and covered calls.

### The stated hurdle

> **The system must deliver ≥ 15.3% annualised net of all costs and taxes over a decade-equivalent out-of-sample window to beat VOO on return, OR a net Sharpe ratio > 0.64 with a maximum drawdown no worse than −33% to beat the best long-run rules-based option index. If the goal is risk reduction rather than return, it must beat a static 50/50 SPY/T-bill blend after tax. If it clears none of these, the correct action is to buy VOO (or SPYI if lower drawdown is genuinely worth 2.6 pp/yr) and stop.**

### Why the direction signal cannot clear this

The programme's established direction signal is **~7 bp/month, t = 0.45**, or roughly **0.84%/yr gross**, with net estimates of **−1 to +4 bp/month**. At the top of that net range the signal contributes **0.48%/yr**. Against a 15.3%/yr passive alternative, the direction signal is not a rounding error on the hurdle — it is roughly 3% of it. The hurdle is not close. It is not within an order of magnitude.

### The cost side of "worth building"

The hurdle is not purely financial. Building and maintaining a multi-agent options research system costs the developer hundreds of hours plus data subscriptions. A system that matched VOO exactly would represent a large negative return on that time. **For the build to be worth it on financial grounds alone, it must clear the hurdle by enough to pay for the effort** — which, for a personal account, essentially nothing in this evidence base supports. This is the strongest argument for repositioning the capstone's goal away from "generate returns" (see "What a professional would build instead").

---

## STRATEGY VIABILITY TABLE

| Strategy | Evidence strength | Retail implementable? | Capital required | Pursue? |
|---|---|---|---|---|
| **Passive index (VOO)** | Strong | Yes, trivially | Any | **Yes — this is the benchmark, and likely the answer** |
| Covered-call / buy-write overlay | Strong *against* (negative alpha 1999–2023; −3.1 to −4.7%/yr 2011–2023) | Yes | Any | **No** as a return strategy; only as paid-exit on holdings being trimmed |
| Cash-secured put-write (PUT-index style) | Moderate, regime-dependent (Sharpe 0.64 pre-2006 → 0.50 after) | Yes | ~$50k+ for diversified SPX laddering | **No** as alpha; defensible only as paid-entry on names wanted anyway |
| Protective puts / tail hedging | Strong *against* (PPUT Sharpe 0.29, longest drawdown 80 months) | Yes | Any | **No** — cash is cheaper convexity |
| VRP harvesting (delta-hedged short vol) | **Strong against post-2012** (alpha → 0, IR −0.6 → +0.09) | Partially; needs daily stock rebalancing | High | **No** |
| Delta-hedged characteristic signals (Zhan et al.) | **Weak after correction** (2.27% → 0.10%/mo; IPCA cuts 50–75%) | **No** — 8.29% single-stock option spreads | Very high | **No** — see verdict below |
| Dispersion / correlation trading | Moderate (Sharpe 0.82 gross, 1996–2007; independent reps 0.34–0.40) | **No** — 21 legs monthly, needs variance swaps | Institutional | **No** |
| Calendar / skew / surface relative value | **No credible evidence found** | No — requires dealer flow and inventory | Institutional | **No** |
| Gamma scalping | **No credible evidence found** for retail | **No** — intraday rebalancing | Institutional | **No** |
| Volatility carry / roll-down | Strong gross (put carry Sharpe 1.80, to 2011), untested net; −22%/yr in carry drawdowns | Partially | High | **No** — same exposure as VRP, worse timing |
| Collars | Weak; CLL absent from the long-run audited data | Yes | Any | **No** — no benchmark exists to evaluate against |
| **Avoiding structural cost sinks** (0DTE, sub-$200 trades, index/ETF vs single-stock, buying over selling) | Moderate-to-Strong, two independent papers | **Yes, fully** | Any | **Yes — this is the only options finding in the strand that is both evidenced and free to implement** |

---

## DELTA-HEDGING VERDICT

**The Zhan et al. signal family is not implementable at retail, and the more serious problem is that it may not be a real signal at all.**

Three independent lines of evidence, two of them in or forthcoming at the same tier of journal that published the original:

1. **Look-ahead bias (Duarte, Jones, Khorram, Mo & Wang, forthcoming *RFS* 2025):** the stock-characteristic delta-hedged strategy falls from **2.27% to 0.10% per month gross** when rebuilt with only pre-trade information. That is a ~96% reduction before a single cent of transaction cost.
2. **Risk adjustment (Goyal & Saretto, Dallas Fed 2022):** IPCA cuts option-strategy alphas by **50–75%**; only **1 of 23** signal-weighted strategies retains significance, and the five surviving long-short characteristics are **option-implied variables, not accounting fundamentals**.
3. **Regime (Dew-Becker & Giglio, Chicago Fed 2025):** the alpha of delta-hedged options went to **zero after May 2012**. Information ratio **−0.6 → +0.09**. Zhan et al.'s sample straddles this break.

On top of which, the implementation arithmetic is hopeless: **0.10%/month gross against ~8.29% average single-stock option quoted spreads**, requiring a daily-rebalanced stock hedge in every name. And Eberbach et al. (2025) show that the *measured* premium in such strategies scales with hedge frequency and may carry the wrong sign entirely — the true premium under realistic dealer positioning simulates at about **−83 bp**.

**Is there a partial substitute?** The brief asks whether a delta-neutral spread structure could capture part of the effect. Honestly: no, and for a reason worth stating. A static delta-neutral structure (straddle, strangle, delta-balanced vertical) does not replicate a dynamically delta-hedged position — it captures the *path-dependent* outcome rather than the volatility premium, which is exactly the "equity timing" exposure Israelov & Nielsen measured at **Sharpe 0.10, t = 0.4**. Substituting a static structure for dynamic hedging does not approximate the signal; it swaps a signal worth 0.10%/month for an uncompensated risk worth nothing.

There is one thin silver lining in Eberbach et al.: **static hedging produces almost no bias (~2 bp vs ~300 bp at 30-minute rebalancing).** The retail trader's inability to hedge frequently means they are also immune to the artifact that inflated the literature. But immunity to a measurement bias is not an edge.

**Verdict: the single strongest option-specific finding in nine research strands does not survive contact with (a) point-in-time data discipline, (b) risk adjustment, (c) the post-2012 regime, or (d) retail transaction costs. It should be removed from the specification as a tradable signal.**

---

## WHAT A PROFESSIONAL WOULD BUILD INSTEAD

A quant handed this evidence base — ~7 bp/month direction signal at t = 0.45, a characteristic signal that collapses to 0.10%/month under point-in-time discipline, a VRP whose alpha died in 2012, and a 15.3%/yr passive alternative — would not build a return-generating options system for a personal account. They would conclude the expected alpha is zero or negative and that the honest move is to hold the index.

But they would not necessarily build *nothing*. The evidence supports four things, in descending order of defensibility. Note that all four are **cost-and-decision tools, not signal engines** — which is the central repositioning this strand implies.

**1. A moneyness-and-tenor cost calculator (strongest support).**
The largest verified effects in the entire programme are structural, not predictive: 3%-OTM weeklies average −59% per 8-day hold vs +12% for 1%-OTM (prior strand); 0DTE loses 4.7%/trade and 2.3–3 pp more than other tenors; sub-$200 trades lose 2.4 pp more than $5,000+ trades; index/ETF options underperform single-stock by over 3 pp; buying loses ~4% while selling earns ~20%. **These dwarf every signal found and require no forecasting.** A tool that takes a contemplated trade and shows its expected cost and historical base rate by moneyness, tenor, size and side has a real, evidenced, falsifiable purpose: it prevents the losses that the two retail-anatomy papers document.

**2. An honest benchmark and attribution harness (the thing currently missing).**
Every trade or simulated strategy reported against: VOO total return, PUT/BXM, SPYI, and a 50/50 SPY/T-bill blend — all after costs and with a tax line. Plus Israelov-style decomposition of any option position into passive equity, equity timing and short volatility, so the developer can see that a covered call is 67% beta and 7% short vol. This makes the system falsifiable, which is the specification's core defect. It is also, usefully, the most academically defensible module and the easiest to demonstrate rigour on.

**3. A point-in-time data discipline layer.**
Given that the single most-cited finding in the programme loses 96% of its return to look-ahead bias, any backtest the developer builds needs: no intraday-average prices for same-day decisions, lagged deltas, hedge frequency as an explicit reported parameter, and conservative spread assumptions (effective ~6.7% for retail index/ETF orders, ~8.3% quoted for single-stock). **This is the most transferable skill in the whole project** — it is what distinguishes a quant from a backtester, and it generalises far beyond options.

**4. Decision support for positions already decided (weakest, but real).**
A cash-secured put on a name the developer wants to own is a paid limit order. A covered call on a holding they intend to trim is a paid target price. Neither needs predictive skill; both need correct strike/tenor selection and honest cost accounting — which modules 1 and 2 provide. The tax caveat in Part 4 applies.

**What a professional would explicitly not build:** a direction-prediction module, a delta-hedged characteristic signal engine, a dispersion module, a surface-arbitrage module, a tail-hedge module, or any backtest whose benchmark is an option-strategy index.

---

## DISCONFIRMING EVIDENCE

**1. The "just buy the index" case, at full strength.** This may simply be the right answer, and it is the single best-evidenced conclusion in the strand. VOO returned 15.26%/yr over ten years at a 0.03% expense ratio with zero maintenance, zero tax friction beyond dividends, and zero model risk. Over the same decade the two longest-running covered-call ETFs returned 8.40% and 9.50%/yr — roughly 55–62% of the index. PUTW returned 8.99%/yr over five years against SPY's 15.71%. A former options market-maker's advice to individuals is that passive index investing *is* the edge. A static 50/50 SPY/T-bill blend recently beat JEPI and JHEQX. If the developer's objective is financial, the evidence supports buying VOO, and — if lower drawdown is genuinely worth 2.6 pp/yr of return — SPYI as the best-in-class option-income alternative. **The capstone's defensible justification is pedagogical, not financial, and the specification should say so explicitly rather than implying an edge the evidence does not support.**

**2. The VRP's alpha is gone, which undercuts the pro-options case too.** Dew-Becker & Giglio (Chicago Fed 2025) date the break to May 2012 and find the delta-hedged option alpha has gone to zero. This cuts both ways and should be stated carefully: it demolishes the option-selling thesis, but it *also* means the market is more efficiently priced than when the favourable studies were run, so option *buying* is not symmetrically attractive either. There is no side of the trade with documented alpha. Note the authors are careful that the VRP itself is not zero — only its alpha beyond CAPM beta.

**3. Retail structural advantages are mostly illusory in options specifically.** The small-cap capacity advantage that is real in equities inverts in options: small, underfollowed names have the widest spreads and thinnest open interest. Bogousslavsky & Muravyev find directly that traders averaging under $200/trade lose 3.4% per option trade versus 1.4% for those over $5,000 — small size is a *disadvantage*. Searching specifically for evidence of small-account options capacity advantage returned nothing on point. The one genuine retail advantage I verified is price improvement (quoted 13.7% → effective 6.7%), and that is a reduction in a cost, not an edge — retail still pays 6.7%.

**4. The pro-option-selling counter-case, stated fairly.** Two independent papers find that retail option *sellers* made money: Bryzgalova et al. report that sellers of short-dated contracts earned profits on average, and Bogousslavsky & Muravyev measure ~+20% per trade on naked sales with trader fixed effects ruling out a skill explanation. The Carry paper's index put-option carry Sharpe of 1.80 is the highest of any carry strategy across asset classes. Israelov & Nielsen's short-vol component had Sharpe 0.98. **These are real findings and I have not dismissed them.** But: the +20% is per-trade on an unbounded loss distribution over a sample with no sustained bear market; put carry returned −22%/yr in exactly the drawdowns when passive puts returned +132%/yr; the Sharpe-0.98 component carried only 7% of risk; and the Carry options sample ends 2011, before the break. The consistent pattern is **short-vol strategies that look excellent until the state of the world in which they are supposed to pay.**

**5. The disconfirming evidence has its own weaknesses, and I should not overstate it.** Goyal & Saretto's IPCA is a flexible latent-factor model, and a sufficiently flexible risk model can absorb any anomaly — "explained by risk" is not "not profitable," and the authors' conclusion is partly a definitional choice. Eberbach et al. is pure simulation with no real option data and self-acknowledged calibration dependence. The Duarte et al. figures I report come from a secondary review (CXO Advisory) because the full text is paywalled, and I could not confirm the paper tests Zhan et al. *by name* — my mapping of "stock-characteristic strategy" to the Zhan family is an inference from the strategy class, characteristic, data source and sample period, and it should be verified before the specification is changed on its authority. The Baltussen settlement-bias paper reports three different wealth-transfer figures and concedes the mechanism is unidentified.

**6. The favourable benchmark data are conflicted and internally inconsistent.** The Wilshire and Bondarenko studies are both Cboe-funded, both exclude costs and taxes, and the Wilshire study reports *different Sharpe ratios for the same index in different exhibits* without explanation. The 60/40 overlay study priced 25 years of short straddles at mid with no transaction costs. If the pro-option-strategy literature is this methodologically soft, the hurdle I set from it (Sharpe 0.64) is probably *too generous* to the option strategies and the real hurdle is closer to the VOO total-return figure.

---

## OPEN QUESTIONS

1. **Does Duarte et al. (RFS 2025) test Zhan, Han, Cao & Tong by name?** The full text is paywalled. My inference is strong but unconfirmed, and it is load-bearing for the delta-hedging verdict. Worth resolving via a university library or the authors' working-paper version before amending the specification.
2. **Do Zhan et al.'s nine characteristics survive on post-2018 data?** Their sample predates the Dew-Becker/Giglio break's full effect. No out-of-sample test located.
3. **Has the correlation risk premium been competed away?** Only non-peer-reviewed SSRN work located; unverified. Relevant to whether dispersion is dead or merely inaccessible.
4. **What are CLL and CNDR's actual long-run numbers?** Absent from the long-run audited data; no hurdle can be set for collars or condors without them.
5. **What is the after-tax hurdle for a US taxable retail account?** All index backtests are pre-tax. Short-term gains treatment and holding-period suspension on in-the-money covered calls could plausibly cost 1–3 pp/yr. Unresearched here and on no other agent's lane.
6. **Does SPYI's structure (index options, tax-efficient distributions) genuinely beat JEPI/QYLD's, or is its 2024–26 outperformance a short sample?** Only ~2.8 years of live data.
7. **Is the retail short-option profitability finding robust to a sustained bear market?** Both papers' samples (2019–2024) lack one. This is the single most important unresolved empirical question for anyone contemplating premium selling.

---

## TOP 10 SOURCES, RANKED

1. **Dew-Becker & Giglio (2025), "The Decline of the Variance Risk Premium," Chicago Fed WP 2025-17** — https://www.chicagofed.org/-/media/publications/working-papers/2025/wp2025-17.pdf — The single most consequential source. Delta-hedged option alpha → 0 after May 2012; IR −0.6 → +0.09. Dates the death of the premium the entire specification implicitly assumes.
2. **Duarte, Jones, Khorram, Mo & Wang, "Too Good to Be True: Look-Ahead Bias in Empirical Option Research," forthcoming *RFS* (2025)** — https://sfs.org/rfs-forthcoming-paper-79/ — Stock-characteristic delta-hedged returns fall 2.27% → 0.10%/month. Directly addresses the strand's highest-value question.
3. **Israelov & Nielsen, "Covered Calls Uncovered," *Financial Analysts Journal* (2015)** — https://www.aqr.com/Insights/Research/Journal-Article/Covered-Calls-Uncovered — The decomposition: 67% beta, 26% uncompensated timing (t = 0.4), 7% short vol (Sharpe 0.98). The best structural insight available.
4. **Bryzgalova, Pavlova & Sikorskaya, "Retail Trading in Options and the Rise of the Big Three Wholesalers," forthcoming *JF* (2023)** — https://www.sikorskaya.net/files/Bryzgalova_Pavlova_Sikorskaya_2023.pdf — Retail is 62% of volume; Big Three take ~90% of PFOF; indirect costs $6.4bn vs $900m commissions; quoted 13.7% → effective 6.7%.
5. **Goyal & Saretto, "Are Equity Option Returns Abnormal? IPCA Says No," Dallas Fed WP 2214 (2022)** — https://www.dallasfed.org/-/media/documents/research/papers/2022/wp2214.pdf — IPCA cuts alphas 50–75%; only option-implied characteristics survive, not accounting fundamentals.
6. **Bogousslavsky & Muravyev, "An Anatomy of Retail Option Trading" (2025)** — https://www.brettonwoodsskiconference.com/uploads/b/f9bfc8b0-0251-11ed-a646-3dea17112d2f/An%20Anatomy%20of%20Retail%20Option%20Trading.pdf — The per-trade cost map: 0DTE −4.7%, buys −4%, naked sales +20%, small trades −3.4%. The evidence base for the one module worth building.
7. **Wilshire Associates for Cboe (2019), "Options-Based Benchmark Indexes"** — https://cdn.cboe.com/resources/spx/wilshire-options-based-benchmark-indexes-2019.pdf — The canonical BXM/BXMD/PUT/CMBO/PPUT long-run table. Essential for the hurdle; conflicted and internally inconsistent, so used with caveats.
8. **Swedroe / Alpha Architect (2023) reviewing Israelov & Ndong, "A Devil's Bargain"** — https://alphaarchitect.com/covered-calls/ — Call selling lost 3.1–4.7%/yr over 2011–2023; QYLD 6.4% vs QQQ 16.5%. The clearest independent demolition of the income-ETF case.
9. **Koijen, Moskowitz, Pedersen & Vrugt, "Carry" (JFE 2018; WP 2013)** — https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2014/06/Carry.pdf — Put carry Sharpe 1.80, the strand's most seductive number, alongside its own refutation: −22%/yr in carry drawdowns while passive puts returned +132%/yr.
10. **Israelov, "Pathetic Protection," *Journal of Alternative Investments* (Winter 2019)** — https://www.aqr.com/Insights/Research/White-Papers/Pathetic-Protection-The-Elusive-Benefits-of-Protective-Puts — Protective puts may do more harm than good; holding less equity dominates. Closes the tail-hedging question.

**Honourable mentions:** Bondarenko (2019) for the 2006–2018 subsample collapse — https://cdn.cboe.com/resources/education/research_publications/PutWriteCBOE19_v14_by_Prof_Oleg_Bondarenko_as_of_June_14.pdf · Abdelmessih / Moontower for the practitioner synthesis — https://moontowermeta.com/derivative-income-bumhunting/ · Eberbach, Molnar, Schuster & Uhrig-Homburg (2025) on hedge-frequency artifacts — https://www.fma.org/assets/docs/Derivatives2025/Molnar.pdf · Baltussen, Terstegge & Whelan (2024) on the BXM/PUT settlement artifact — https://afajof.org/management/viewp.php?n=98196 · totalrealreturns.com for live ETF total returns — https://totalrealreturns.com/n/SPY,SPYI,QQQI,JEPI,JEPQ,VOO

---

## NOTED OVERLAPS WITH OTHER AGENTS (not researched here)

- **Execution microstructure:** quoted vs effective spreads (13.7% → 6.7%), single-stock option spreads (8.29%), index option spreads (6.23%), PFOF mechanics, price-improvement auctions. I report these only as binding constraints on strategy viability.
- **Position sizing and risk:** the drawdown profiles of short-vol strategies, carry crash risk, and the −43% dispersion drawdown all have sizing implications I have not developed.
- **Volatility forecasting and surface modelling:** Goyal & Saretto's finding that the only surviving characteristics are **option-implied** (IV ATM, IV slope, IV term, RV−IV) hands that agent the most important lead in this report — if any signal survives risk adjustment, it is theirs, not the fundamental-characteristic family.
