# Strand 3 — Options Pricing, Mispricing, and Flow
### Research report for a retail-facing options contract scoring application
**Date:** 10 November 2026
**Scope:** What "appropriately priced" can defensibly mean; option return predictability; order flow and "unusual options activity"; microstructure realities for retail; Greeks-based screening; dealer gamma (GEX); composite scoring; 0DTE.

---

## 0. How to read this report

Every source is labelled by evidence class:

- **[PEER]** — published in a peer-reviewed journal.
- **[WP]** — working paper / preprint, not yet peer-reviewed.
- **[VENDOR]** — produced by a firm selling a related product, or an exchange with a commercial interest.
- **[BLOG]** — practitioner commentary with no methodology disclosure.

A methodological note on this session: the web-search quota for this research run was exhausted part way through (it is shared across five parallel agents), so the last third of the work was done by fetching URLs already surfaced. Two specific gaps are flagged explicitly in **Open Questions**: the Grauer–Schuster–Uhrig-Homburg option trade classification accuracy figures, and Carr & Wu (2009) primary verification. Nothing in the report's conclusions depends on an unverified number without being marked as such.

---

## 1. WHAT "APPROPRIATELY PRICED" CAN DEFENSIBLY MEAN

### 1.1 The variance risk premium exists, but it is smaller and more fragile than the folklore

**CLAIM:** Individual equity options embed a negative volatility risk premium, but it is roughly half the size of the index-option premium, and idiosyncratic volatility does not appear to be priced.
**SOURCE:** Gurdip Bakshi & Nikunj Kapadia, "Volatility Risk Premiums Embedded in Individual Equity Options: Some New Insights," *Journal of Derivatives*, Fall 2003. https://people.umass.edu/~nkapadia/docs/Bakshi_Kapadia_JoD_Fall_2003.pdf **[PEER]**
**EVIDENCE STRENGTH:** Moderate (small sample: 25 stocks).
**Details:** Average implied-minus-realized volatility gap of 1.5 vol points for the 25 single stocks versus 3.3 points for SPX. Delta-hedged gains were negative on average for 14 of 25 stocks; 7 significantly negative at the 99% level, 4 significantly positive. Panel slope on market volatility −0.0263 (z = −2.55).
**IMPLICATION FOR THE APP:** The structural short-premium edge in single-name equity options is roughly 1.5 vol points on average — thin relative to the bid-ask spreads documented in §4. And it is a *market*-volatility premium: an app that tells the user "IV is above RV on this ticker, so the option is rich" is partly measuring an unpriced idiosyncratic component for which no premium is owed.

**CLAIM:** The equity-index variance risk premium is not robust to sample choice: the S&P 500 realised VRP is statistically indistinguishable from zero once March 2020 is included.
**SOURCE:** Steven L. Heston & Karamfil Todorov, "Exploring the Variance Risk Premium Across Assets," SSRN 4373509, c. 2023 (presented AFA 2024). https://afajof.org/management/viewp.php?n=41580 **[WP]**
**EVIDENCE STRENGTH:** Strong (model-free tradable replication across 20 futures markets; median correlation with realized variance >99%).
**Details:** S&P 500 variance-portfolio mean return −11.9%/month full sample but −22.9%/month pre-COVID; annualized Sharpe −0.23 full sample. A single March 2020 observation above +2000%/month drives much of the result. 10-year Treasuries (−25.8%/month) and agricultural commodities show far larger premiums than equities (Sharpes ≈ −1.4 to −3.0). Only the Swiss franc has a positive premium. Systematic risk explains little; kurtosis and VIX level matter cross-sectionally.
**IMPLICATION FOR THE APP:** This is the single most important caveat in the whole VRP literature for a retail product. The VRP is real but is a *left-tail-financing* premium: it pays a little most of the time and loses enormously rarely. An app whose score rewards "sell premium because IV > RV" is selling that tail to the user without the user seeing the tail. If the app surfaces short-premium strategies, the honest display is not an expected return but an expected-return-plus-tail-loss pair.

**CLAIM:** Long out-of-the-money index calls have large negative average returns — not just puts.
**SOURCE:** Gurdip Bakshi, John Crosby & Xiaohui Gao, "Dark Matter in (Volatility and) Equity Option Risk Premiums," *Operations Research*, Dec 2022 (arXiv:2303.16371). https://arxiv.org/pdf/2303.16371 **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details (average holding-period returns, computed at ask prices):** Weeklies (~8 days): 3% OTM call **−59%**, 1% OTM call **+12%**, 3% OTM put **−61%**, ATM straddle −10%. 28-day SPX: 5% OTM call −31%, 3% OTM call −10%, 1% OTM call +4%, ATM straddle −19%. 88-day SPX futures options: 12% OTM call −66%, ATM straddle −20%. Straddles were profitable in only 40% of positions. Results qualitatively survive recomputation at midpoint.
**IMPLICATION FOR THE APP:** This is the most load-bearing single result for a product that converts a bullish chart pattern into a long call recommendation. The unconditional expected return on a short-dated 3%-OTM call is roughly **−59% per 8-day holding period**. A score of 0–100 placed on such a contract is scoring positions whose unconditional mean is catastrophic. Note the nuance the app can use honestly: the 1%-OTM weekly call had a *positive* +12% mean. Moneyness is doing enormous work; "buy calls" and "buy OTM calls" are economically different products.

### 1.2 IV rank and IV percentile: no peer-reviewed support found

**CLAIM:** No peer-reviewed study was found testing IV rank or IV percentile as a predictor of option returns, implied-volatility change, or realized volatility.
**SOURCE:** Searched across Google Scholar-indexed results, SSRN, arXiv q-fin, and journal sites. All substantive results were vendor or practitioner material: tastylive *Market Measures* episodes (e.g. "IVR and IVP: The Numbers," 30 Aug 2016; "IV Rank Various Time Periods," 31 Jul 2015; "IV Rank Strategy Selection," 6 Jan 2017) https://tastylive.com/shows/market-measures/episodes/ivr-and-ivp-the-numbers-08-30-2016 **[VENDOR]**; Option Samurai blog backtest series https://optionsamurai.com/blog/implied-volatility-backtest-pt-3-iv-and-rv/ **[VENDOR]**.
**EVIDENCE STRENGTH:** **No credible evidence found.**
**Details on the vendor material:** The Option Samurai backtest reports that after SPY IV exceeded its 90th percentile, realized volatility *rose* 11.43% over the next week and 15.78% over two weeks relative to normal, declining only over the following month and 45 days. No sample period, no observation count, no standard errors, no out-of-sample split. The tastylive episodes are video segments with no published methodology, no significance tests, and no replication package.
**IMPLICATION FOR THE APP:** IV rank is the most widely marketed "is this option expensive?" heuristic in retail options software, and it has no peer-reviewed empirical foundation that this research could locate. Worse, the one vendor backtest that looked at the honest question (does high IV rank precede low realized vol?) found the *opposite* at one- and two-week horizons. IV rank is a legitimate **descriptive** statistic — "this ticker's IV is high relative to its own past year" is a true statement — and it is not a legitimate **predictive** one. The app can display it as context. The app should not weight it in a score that is presented as predicting anything, and should not use it as the basis for a "cheap/expensive" verdict.

### 1.3 The academic cousin of IV rank — IV minus historical vol — does work, but barely survives execution

**CLAIM:** Sorting on the spread between implied and historical volatility generates large gross straddle returns that are mostly consumed by trading costs, with the residual concentrated in medium-liquidity options.
**SOURCES:**
- Amit Goyal & Alessio Saretto, "Cross-Section of Option Returns and Volatility," *Journal of Financial Economics* 94(2), 2009 (SSRN working version "Option Returns and Volatility Mispricing," SSRN 889947). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=889947 **[PEER]**
- Alessio Saretto, "Option Returns and the Cross-Sectional Predictability of Implied Volatility," Purdue WP, Nov 2005. https://www.cis.upenn.edu/~mkearns/finread/CrossOptions.pdf **[WP]**
- Dmitriy Muravyev & Neil D. Pearson, "Options Trading Costs Are Lower than You Think," *Review of Financial Studies* 33(11), 2020, pp. 4973–5014, Internet Appendix. https://www.dmurav.com/MuravyevPearson.OptionsTradingCosts.InternetAppendix.pdf **[PEER]**
**EVIDENCE STRENGTH:** Strong for the gross effect; Strong for the cost erosion.
**Details:** Saretto's long–short straddle strategy on forecast IV change returns **16.1% gross** to expiration (~47 days) at midpoint and **5.5% net** assuming an effective spread of 75% of quoted. Split by liquidity, the net long–short is 8.6% in the medium bid-ask tercile (significant), **2.9% and insignificant (t = 0.91) in the widest-spread tercile**, and 1.4% and insignificant in the lowest-volume tercile. Muravyev & Pearson re-examine the implied-minus-historical straddle sort directly: **8.8% gross → 4.1% (t ≈ 2.9) using their "algo" half-spread (the cost faced by a trader who times execution) → 1.4% and insignificant using the conventional effective half-spread.** They also measure effective-to-quoted half-spread ratios of ~0.73–0.81 (non-S&P names: 9.7% effective vs 12.8% quoted half-spread), with an algo half-spread of 5.4% average (8.0% for OTM, 2.8% for ITM); about 37% of trades show execution timing.
**IMPLICATION FOR THE APP:** This is the honest version of the IV-rank idea, and it tells you three things. (1) The effect exists. (2) It is roughly **halved by paying good prices and eliminated by paying the spread**. (3) It survives only in options that are *liquid enough* — in the widest-spread tercile it is statistically zero. A liquidity screen is therefore not a hygiene filter sitting beside the score; it is a precondition for the score meaning anything. Any contract failing the liquidity screen should be excluded from scoring entirely, not scored and penalised.

### 1.4 Term structure and skew as richness measures

**CLAIM:** The slope of a firm's implied volatility term structure predicts the cross-section of straddle returns.
**SOURCE:** Aurelio Vasquez, "Equity Volatility Term Structures and the Cross Section of Option Returns," *Journal of Financial and Quantitative Analysis* 52(6), 2017, pp. 2727–2754. https://econpapers.repec.org/article/cupjfinqa/v_3a52_3ay_3a2017_3ai_3a06_3ap_3a2727-2754_5f00.htm **[PEER]**
**EVIDENCE STRENGTH:** Moderate (abstract-level verification only; magnitudes and net-of-cost results not obtained in this session). Straddles on steep-slope firms outperform flat-slope firms by an amount the author describes as economically and statistically significant, not explained by traditional, higher-moment, or jump factors.
**IMPLICATION FOR THE APP:** Term-structure slope is a defensible *relative* richness measure with peer-reviewed support, and it is computable from a standard option chain. Treat it as a candidate input with moderate weight, flagged as unverified on net-of-cost survival.

**CLAIM:** The volatility smirk (steepness of the strike-dimension IV curve) predicted equity returns strongly in the 1996–2005 era.
**SOURCE:** Yuhang Xing, Xiaoyan Zhang & Rui Zhao, "What Does the Individual Option Volatility Smirk Tell Us About Future Equity Returns?" *JFQA* 45(3), 2010, pp. 641–662. **[PEER]**
**EVIDENCE STRENGTH:** Strong in sample. Steepest-smirk stocks underperformed flattest-smirk stocks by **10.9% per year** risk-adjusted, persisting at least six months; steepest-smirk firms also had the worst subsequent earnings shocks.
**IMPLICATION FOR THE APP:** Skew is a legitimate *measure* and was once a legitimate *signal*. See §3.4 for what happened to it.

---

## 2. OPTIONS RETURN PREDICTABILITY LITERATURE

**CLAIM:** Nine stock-level characteristics predict delta-hedged equity option returns with portfolio Sharpe ratios above 2 annualised, and the authors report the strategies remain profitable after transaction costs.
**SOURCE:** Xintong Zhan, Bing Han, Jie Cao & Qing Tong, "Option Return Predictability," *Review of Financial Studies* 35(3), 2022, pp. 1394–1442. https://academic.oup.com/rfs/article-abstract/35/3/1394/6294944 **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details:** Negatively related to delta-hedged call-writing returns: stock price, profit margin, profitability. Positively related: cash holdings, cash-flow variance, new share issuance, total external financing, distress risk, analyst forecast dispersion. Two option factors explain the profits; equity risk factors do not. Authors describe the predictability as still puzzling.
**IMPLICATION FOR THE APP:** These are *fundamental* inputs to an *options* score — cash holdings, issuance, distress, analyst dispersion. They are obtainable from EDGAR and standard data feeds, which fits the app's existing ingestion pipeline, and they have the strongest cost-survival claim of any option-return predictor family found. If the score is to have one academically grounded pillar, this is the most defensible candidate.

**CLAIM:** Nonlinear machine learning predicts delta-hedged option returns out of sample, but the net profitability collapses as the fraction of quoted spread paid rises, failing entirely at 50%.
**SOURCE:** Turan G. Bali, Heiner Beckmeyer, Mathis Moerke & Florian Weigert, "Option Return Predictability with Machine Learning and Big Data," CFR WP 21-08, 2021. https://www.cfr-cologne.de/download/workingpaper/cfr-21-08.pdf **[WP]** (subsequently published; this session verified the working-paper version.)
**EVIDENCE STRENGTH:** Strong.
**Details:** Out-of-sample R² 2003–2020: linear models not significantly positive; best nonlinear models (GBR, DART) ≈ 2.6–2.7%. Nonlinear ensemble decile 10−1 earns **2.63%/month, monthly Sharpe 2.06 gross**. Net: **1.33%/month (SR 1.17) at 15% of quoted spread; 0.47%/month (SR 0.43) at 25%; fails at 50%.** At 25%, rolling one-year returns were zero or negative in 2016–2019; long-dated options become insignificant or negative while short-dated survive. Option-based characteristics dominate (R² 1.77% alone vs 0.26% for stock characteristics alone); position on the implied-volatility surface — moneyness, maturity, IV — ranks highest. Authors report predictability "stable over time and does not vanish" to end of sample. Overfitting controls: separate validation year, 512-trial random search with successive halving, early stopping, 8-model ensembles, elastic-net/ridge/lasso/dropout/subsampling. **No multiple-testing correction mentioned.**
**IMPLICATION FOR THE APP:** 25% of quoted spread is the breakeven zone, and a retail user clicking "buy" in a consumer app is not realistically paying 15%. Also note the composition result: the most important predictors are *where the contract sits on the vol surface*, not exotic signals. That is a cheap, obtainable, defensible score backbone.

**CLAIM:** Most documented delta-hedged equity-option anomalies are absorbed by a conditional latent-factor model, implying they are largely not independent mispricings.
**SOURCE:** Alessio Saretto (with possible co-authors not listed on the landing page), "Can Equity Option Returns Be Explained by a Factor Model? IPCA Says Yes," *Review of Financial Studies* 38(6), 2025, pp. 1783–1821. DOI 10.1093/rfs/hhae087 **[PEER]**
**EVIDENCE STRENGTH:** Moderate (abstract and figure-caption level verification only). IPCA alphas are reported as "close to zero for almost all strategies."
**IMPLICATION FOR THE APP:** Strong caution against building a score by summing many option anomalies. If a common factor structure explains almost all of them, then adding the twelfth anomaly to a composite adds correlated noise rather than independent information, and the composite's apparent diversification is an illusion. See §7.

**CLAIM:** End-to-end deep learning on delta-neutral straddles produces a 1.33 gross Sharpe that degrades steeply with costs.
**SOURCE:** Wee Ling Tan, Stephen Roberts & Stefan Zohren, "Deep Learning for Options Trading: An End-To-End Approach," arXiv:2407.21791, 2024. https://arxiv.org/pdf/2407.21791 **[WP]**
**EVIDENCE STRENGTH:** Moderate.
**Details:** S&P 100 one-month ATM delta-neutral straddles, OptionMetrics, 2010–2023, expanding window. LSTM Sharpe 1.329 at 0 bps → 0.952 at 20 bps → 0.388 at 50 bps; beats the best rules benchmark only up to 20 bps. Turnover regularization helps at 10–50 bps (1.045 at 20 bps, 0.689 at 50 bps). Mean-reversion beats momentum in this market.
**IMPLICATION FOR THE APP:** Even on the *most liquid* 100 US names in the most standardized structure, ML edge is a 20-basis-point phenomenon. A consumer app cannot assume its users trade at 20 bps.

**CLAIM:** Cao & Han establish that delta-hedged option returns decrease in the underlying's idiosyncratic volatility.
**SOURCE:** Jie Cao & Bing Han, "Cross-section of option returns and idiosyncratic stock volatility," *Journal of Financial Economics*, 2013. https://www-2.rotman.utoronto.ca/facbios/file/Han_JFE_published.pdf **[PEER]**
**EVIDENCE STRENGTH:** Citation verified; magnitudes **not** verified in this session (search budget exhausted before fetch). Flagged in Open Questions.

---

## 3. ORDER FLOW AND "UNUSUAL OPTIONS ACTIVITY"

This is where the product thesis is most exposed. The findings below are, in aggregate, the strongest negative result in this report.

### 3.1 The foundational flow result required data retail cannot buy — and the publicly inferable version did not work

**CLAIM:** Pan & Poteshman's option-volume predictability came specifically from *proprietarily identified, open-position, customer-class* volume; predictability computed from publicly observable Lee-Ready-classified volume was weak, reversed within a day, and disappeared once open-buy volume was controlled for.
**SOURCE:** Jun Pan & Allen M. Poteshman, "The Information in Option Volume for Future Stock Prices," *Review of Financial Studies* 19(3), 2006. https://www.mit.edu/~junpan/volume.pdf **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details:** Full-sample daily slope on the open-buy put-call ratio ≈ 53 bps; low-minus-high quintile ≈ 42 bps/day risk-adjusted; predictability persists about a week (first five days sum >1%), near zero by three weeks. By trader class (next-day, Table 7): **full-service customers ≈ 44 bps (t ≈ 37); discount customers ≈ 35 bps; other public customers ≈ 29 bps; firm proprietary traders ≈ 1.5 bps (t ≈ 0.75)** — the authors suggest proprietary traders use listed options mainly for hedging. Open-buy is most informative; open-sell ≈ 20 bps (t = 12.4); close-sell ≈ 27 bps; close-buy ≈ 0.9 bps, insignificant.
**IMPLICATION FOR THE APP:** Read this carefully, because the retail flow industry has it backwards twice over.

1. **The signal lives in open-position volume, labelled by trader class.** It requires the CBOE/ISE proprietary open-close dataset. It is *not* in the public tape.
2. **The authors explicitly tested the publicly inferable version and it failed.** Lee-Ready-classified public volume gave weak predictability that reversed after one day and vanished under controls. That is the exact data a consumer app has.
3. **Firm proprietary traders — the large, aggressive, multi-exchange sweeps that retail flow products label "smart money" or "whale flow" — had essentially zero predictive power, and the authors attribute this to hedging.** The informative flow came from *full-service brokerage customers*, which on a public tape looks like ordinary mid-size activity.

A flow feature built on the public tape is therefore not a weakened version of Pan–Poteshman. It is the version Pan–Poteshman reported as not working, applied to the trader class they reported as uninformative.

### 3.2 The put-call parity deviation signal is substantially a stock-borrow-fee proxy

**CLAIM:** Return predictability from the option-implied volatility spread and skew falls by at least two-thirds when high-borrow-fee stocks are excluded; the predictability is consistent with implied volatilities mechanically reflecting stock borrow fees, which independently predict returns.
**SOURCE:** Dmitriy Muravyev, Neil D. Pearson & Joshua M. Pollet, "Why does options market information predict stock returns?" *Journal of Financial Economics* 172(C), 2025. DOI 10.1016/j.jfineco.2025.104153. https://ideas.repec.org/a/eee/jfinec/v172y2025ics0304405x25001618.html **[PEER]**
**EVIDENCE STRENGTH:** Strong — and it directly overturns the mechanism claimed by the original paper.
**Original:** K. J. Martijn Cremers & David Weinbaum, "Deviations from Put-Call Parity and Stock Return Predictability," *JFQA* 45(2), 2010, pp. 335–367. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=968237 **[PEER]** — 51 bps/week spread between relatively-expensive-call and relatively-expensive-put stocks; the authors argued using lending rebate rates that hard-to-borrow stocks did **not** drive it; and they themselves reported that **"the degree of predictability decreases over the sample period."**
**IMPLICATION FOR THE APP:** Three compounding problems for a put-call-parity-deviation input.
1. The original authors already documented in-sample decay.
2. A 2025 JFE paper derives a formula linking the volatility spread to the borrow fee and shows ≥2/3 of the predictability disappears outside high-fee stocks — contradicting the original paper's own rebate-rate robustness check.
3. The residual tradable signal lives in **expensive-to-borrow stocks**, where the implied trade is a short, and where a retail user cannot realistically borrow or will pay the fee that *is* the signal.

A "put-call parity deviation" line item in a retail score is, on the current best evidence, mostly a hard-to-borrow indicator wearing an options costume.

### 3.3 The O/S ratio works because of embedded leverage — and the mechanism requires signed, open/close data

**CLAIM:** The option-to-stock volume ratio predicts stock returns primarily because of embedded leverage, not short-sale constraints, and the predictive content is concentrated in *opening call purchases*.
**SOURCES:** Travis L. Johnson & Eric C. So, "The option to stock volume ratio and future returns," *JFE* 106(2), 2012, pp. 262–286 **[PEER]**; Li Ge, Tse-Chun Lin & Neil D. Pearson, "Why does the option to stock volume ratio predict stock returns?" *JFE* 120(3), 2016, pp. 601–622. https://www.sciencedirect.com/science/article/abs/pii/S0304405X16000167 **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details:** Ge/Lin/Pearson use ISE signed public-customer volume. Synthetic-short trades are *not* more informative than synthetic-long trades, contradicting Johnson & So's short-sale-constraint mechanism. **Call purchases that open new positions predict most strongly**; call sales that close prior purchases are second. Higher-leverage OTM options show stronger predictability. The paper reconciles Pan–Poteshman with Johnson–So.
**IMPLICATION FOR THE APP:** The unsigned O/S ratio *is* computable from public data, which is its one advantage. But the 2016 paper shows the unsigned version obscures the components that actually carry the signal: you need open-vs-close and buy-vs-sell labels to isolate "opening call purchases." Unsigned O/S is therefore a diluted proxy of a diluted proxy.

**CLAIM:** Unsigned put-call volume ratios do predict returns at short horizons without proprietary data, but the effect is very short-lived.
**SOURCE:** Benjamin M. Blau, Nga Nguyen & Ryan J. Whitby, "The information content of option ratios," *Journal of Banking & Finance* 43, 2014, pp. 179–187. **[PEER]**
**EVIDENCE STRENGTH:** Moderate.
**Details:** P/C ratio beats O/S at the daily horizon by at least 40%; O/S beats P/C at the weekly horizon (sometimes by >200%) and is the only one significant monthly; P/C predictability is significant daily, weaker weekly, then fades. Neither measure uses open interest — both are volume ratios.
**IMPLICATION FOR THE APP:** The honest version of a public-data flow signal is a **one-day-horizon** signal. A product that surfaces an options contract to hold for weeks cannot use it. The horizon mismatch is fatal to most of the use case.

### 3.4 Decay: the direct evidence

**CLAIM:** Across 97 published stock-return predictors, long-short returns fall ~26% from in-sample to out-of-sample-pre-publication and ~58% post-publication; decay is larger for predictors with higher in-sample returns and smaller for those concentrated in costly-to-arbitrage stocks.
**SOURCE:** R. David McLean & Jeffrey Pontiff, "Does Academic Research Destroy Stock Return Predictability?" *Journal of Finance*, 2016. https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details:** In-sample mean 58.2 bps/month → 40.2 bps out-of-sample pre-publication (−15.0 bps) → 26.4 bps post-publication (−33.7 bps). Statistical bias estimated ~26% (upper bound); publication effect ~32%. Excluding 12 low-t predictors: −18.0 and −38.7 bps. With time fixed effects, post-publication decline ~53%. Post-publication rises in volume, dollar volume, relative short interest; correlations migrate toward published predictors.
**IMPLICATION FOR THE APP:** Every flow and skew signal in §3 is published, widely published, and in several cases sold as a retail product. The base-rate expectation is that it delivers **roughly 40% of its published magnitude**, before the app's users pay retail spreads. Applying a 0.4 haircut to every literature-derived effect size before it enters a score is not pessimism; it is the measured average.

**CLAIM:** The volatility smirk signal has weakened to insignificance in the most recent regime, with signs of sign reversal at longer horizons.
**SOURCE:** Baichuan Li & Mengxiao Wang, "Option-Implied Signals and Crash Risk: Predictability and Machine-Learning Evidence from U.S. Equity Options, 2015–2026," arXiv:2608.26115, 2026. https://arxiv.org/pdf/2608.26115 **[WP]**
**EVIDENCE STRENGTH:** **Weak.** This preprint is internally inconsistent and should not be leaned on. Its text and tables disagree on whether the smirk retains multivariate significance; its replication recovers about half the original Xing et al. magnitude (−4.91% vs −10.9% annualized); regressions use a random 1.5M-row subsample of ~12M firm-days; there are no CRSP/Compustat controls; a key retail-trading claim cites "Anonymous (2026)"; robustness checks are deferred to a follow-up.
**Reported figures (treat as indicative only):** 21-day smirk coefficient −0.023 (t = −5.5) in 2015–2019, −0.015 (t = −4.2) in 2020–2022, −0.006 (t = −1.5, insignificant) in 2023–2026; +0.016 (t = +2.1) at 63 days in 2023–2026. IV spread and a risk-neutral-skewness proxy retain |t| > 4 in all regimes. Crash-classification AUC (5-day) 0.706 XGBoost / 0.670 logit in 2015–2019, ~0.56/0.53 in 2020–2022, ~0.665/0.652 in 2023–2026. No trading strategy, no costs, no portfolio returns.
**IMPLICATION FOR THE APP:** The *direction* of this evidence matches the McLean–Pontiff prior, which is why it is worth reporting, but the quality does not support a weighting decision. Treat skew decay as plausible-and-unproven and verify with a proper source before relying on it.

### 3.5 Open interest signals: thin and low-quality evidence

**CLAIM:** Open-interest-based directional trading on 30 stocks over six months in 1999 produced large reported returns, but the study has no significance tests and assumed zero stock trading costs.
**SOURCE:** Rafiqul Bhuyan & Mo Chaudhury, "Trading on the information content of open interest: Evidence from the US equity options market," *Journal of Derivatives Use, Trading & Regulation* 11(1), pp. 16–36, c. 2005. https://www.mcgill.ca/desautels/files/desautels/TradingOn05.pdf **[PEER — low-tier]**
**EVIDENCE STRENGTH:** **Weak.** 30 large US stocks, Feb–Jul 1999 only; stock-only active strategy averaged 9.05% per holding period vs 1.00% buy-and-hold and 1.53% S&P 500; stock-plus-options 11.20%. "Up" calls correct ~65% of the time, "down" ~58%. Options costed at $30 one-way; **stock trading costed at zero.** No formal significance tests, no annualization, no risk adjustment beyond a cross-sectional standard-deviation proxy. Results sensitive to single news events (one example fell from 0.86% to 0.39% when one news stock was dropped).
**IMPLICATION FOR THE APP:** Do not cite this as support for an open-interest signal.

**CLAIM:** Price- and probability-weighted call-put ratios built from open interest or volume in short-dated OTM options predict next-day returns, with the gains concentrated in the short leg and the signal attributed to retail call buying.
**SOURCE:** Jitka Hilliard, Jimmy E. Hilliard & Yi Wu, "Do short-lived options reveal information asymmetry? Evidence from open interest and volume signals," *Review of Quantitative Finance and Accounting*, accepted May 2025. DOI 10.1007/s11156-025-01427-z **[PEER]**
**EVIDENCE STRENGTH:** Moderate (recent, peer-reviewed, but a three-year window and some internal inconsistencies).
**Details:** 458 NYSE-listed optionable stocks, 31 Aug 2020 – 31 Aug 2023 (755 days, >20M observations), 7–45 day OTM options. Daily long-short before borrow costs: CPIR ≈ 19.0 bp, CPIRA ≈ 20.7 bp, CPVR ≈ 18.8 bp, CPVRA ≈ 19.5 bp, all significant at 1%. Returns computed **at bid/ask** (open at prior ask, close at current bid). FF5+momentum alphas ≈ 0.18–0.19%/day; **bottom-decile alphas significantly negative, top-decile near zero — the short leg drives the result.** After an estimated short-sale cost adjustment the CPIR long-short falls to ≈13.4 bp/day (t ≈ 2.10). Adjusted R² is low (0.12–0.15). The authors use risk-neutral probabilities as a proxy for physical probabilities (their own stated limitation), the Markit short-cost database stopped updating after 2020, and some figures differ between text and tables (annualized CPIR reported as both 61.34% and 54.25%).
**IMPLICATION FOR THE APP:** This is the best recent evidence that an OI/volume-based option signal has content in a modern sample using publicly available chain data, which is genuinely encouraging. But the economics are hostile to the product: a **daily**-horizon signal whose profits sit in the **short** leg, requiring **daily rebalancing** and **short selling**, with an explicit acknowledgment that risk-neutral probabilities are standing in for real ones. A retail long-only options app can capture approximately none of it.

### 3.6 Can retail-visible flow distinguish opening from closing, hedge from bet, dealer from customer? — No.

This is the question the task flagged as central, and the answer is unambiguous across four independent lines of evidence.

**CLAIM (a):** The public OPRA tape records price, size, exchange and timestamp but **not** whether a trade opened or closed a position, and open interest is published only after overnight OCC reconciliation.
**SOURCE:** GEX Metrix, "The Intraday Open Interest Problem: Why Real-Time OI Does Not Exist." https://www.gexmetrix.com/blog/intraday-oi-problem **[VENDOR]** (a competitor in the same space, so self-interested, and its numbers are unsourced).
**EVIDENCE STRENGTH:** Strong for the structural facts (independently corroborated by the academic sources below); Weak for the quantitative claims.
**Details as claimed:** OI changes only when both counterparties open or both close; mixed trades leave it unchanged and are common in liquid markets. Vendors reconstruct intraday OI by starting from the prior night's OCC figure, classifying each print as opening or closing with a tick/quote/Lee-Ready rule, accumulating net opening volume, and recalibrating nightly. Claimed mid-session drift of 10–20% on active days, worsening when intraday volume exceeds about half of overnight OI; error sources include spreads, rolls, FLEX, early exercise and the 0DTE closing rush. Claimed data costs: full OPRA feed $10k–30k/month, dealer-position data >$30k/month, against consumer dashboards at $250–720/month.

**CLAIM (b):** The quote rule — the standard way to infer trade direction from public data — **misclassifies about 42% of Cboe customer SLIM option trades**, and this misclassification materially changes published conclusions about retail profitability.
**SOURCE:** Diego Amaya, Pedro A. Garcia-Ares, Neil D. Pearson & Aurelio Vasquez, "New Evidence on the Performance of Customer Options Trades," April 2025. https://cdn.cboe.com/resources/education/research_publications/Retail_Profitability.pdf **[WP / VENDOR-FUNDED** — data research grant from The Options Institute, Cboe's educational division, which also supplied the data; Cboe operates the exchanges studied.**]**
**EVIDENCE STRENGTH:** Strong on the misclassification rate (validated against exchange data carrying true direction and open/close flags).
**IMPLICATION:** A 42% error rate on a binary label is close to coin-flipping. Any app feature of the form "large call buying detected" built on a quote-rule classification of the public tape is reporting a label that is wrong roughly two times in five.

**CLAIM (c):** Even the exchange cannot identify end users, and the majority of retail SPX activity is multi-leg — so individual legs on the tape are not individual bets.
**SOURCE:** Selina Han (Economist, Public Policy, Cboe Global Markets), "Unveiling the Sophistication: Understanding Retail Investors' Trading Behavior in the U.S. Options Market," 17 May 2024. https://cdn.cboe.com/resources/government_relations/Understanding-Retail-Investors-Dynamic-Trading-Behavior-in-the-US-Options-Market_2024.pdf **[VENDOR]**
**EVIDENCE STRENGTH:** Moderate (exchange-authored, disputes prior academic work, offers no P&L).
**Details:** Retail share of C1 notional rose from 18% (Q4 2019) to 31% (Q4 2023). **Complex (multi-leg) orders were ~58–76% of retail open-position notional.** Put vertical spreads most common, then call verticals. Aggregated retail complex positions are **net short**; simple orders are net long. Retail net credits from complex strategies peaked at $10.3bn in Q3 2022. >50% of retail SPX 0DTE volume through Q1 2024 was identifiable multi-leg (disputing Beckmeyer et al. 2023's 60–80% single-leg figure, attributing the gap to data source). Options with ≤1 week to expiry were >90% of retail notional in Q4 2023, up from <70% in Q4 2019. The paper states Cboe **"cannot identify end-user investors,"** that the "customer" group may include professionals and funds, and that legged-in strategies are likely undercounted.
**IMPLICATION:** Three things follow. A big put print may be the short leg of a put vertical — a *bullish* position. Retail aggregate complex positioning is net short premium, the opposite of the "retail buys lottery tickets" caricature and the opposite of what GEX conventions assume. And "customer" on exchange data is not "retail."

**CLAIM (d):** Dedicated option-trade-classification research exists and proposes new rules (depth rule, trade-size rule) precisely because the standard rules perform poorly on options.
**SOURCE:** Caroline Grauer, Philipp Schuster & Marliese Uhrig-Homburg, "Option Trade Classification," SSRN 4098475, 2023 — identified via the `tclf` reference library (https://github.com/KarelZe/tclf). **[WP]**
**EVIDENCE STRENGTH:** **Existence confirmed; accuracy figures NOT obtained** — the SSRN DOI was not fetchable in this session and the search budget was exhausted. Flagged in Open Questions as the highest-priority follow-up.

**Synthesis of §3.6 for the product:** A flow signal built on retail-obtainable data cannot reliably tell an opening trade from a closing one, a bought option from a sold one (~42% error), a single-leg bet from one leg of a spread (most retail SPX notional is multi-leg), a hedge from a directional position (Pan–Poteshman attribute proprietary-trader flow to hedging and find it uninformative), or a market maker from a customer (the exchange itself says it cannot identify end users). The task framing asked whether a flow signal that cannot tell a hedge from a bet is near-worthless. On this evidence: **yes, and the one paper that tested the publicly inferable version directly found it weak, one-day-reversing, and subsumed.**

---

## 4. MARKET MICROSTRUCTURE REALITIES FOR RETAIL

**CLAIM:** Retail accounts for the majority of US options volume; its gross buy-minus-sell performance is positive but its net performance is negative, with indirect trading costs an order of magnitude larger than commissions.
**SOURCE:** Svetlana Bryzgalova, Anna Pavlova & Taisiya Sikorskaya, "Retail Trading in Options and the Rise of the Big Three Wholesalers," *Journal of Finance*, 2023. https://www.sikorskaya.net/files/Bryzgalova_Pavlova_Sikorskaya_2023.pdf **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details:** Retail ≈ **62.6%** of total options volume (from Rule 606 PFOF disclosures). SLIM (single-leg non-ISO price-improvement-auction trades) captures ~30% of inferred retail volume, ~18% of market volume; SLIM dollar volume +101% Jan 2020–Jul 2021. **Gross buy-minus-sell performance +$10.4–12.9M/day; net −$5.0M to −$1.6M/day.** At a 10-day holding assumption, retail lost ≈**$2.1bn** Nov 2019–Jun 2021. **Trading costs ≈$6.4bn vs commissions ≈$0.9bn.** Losses concentrated in **long positions in short-dated (weekly) options**; retail *sellers* of these were profitable — two distinct populations. **Average quoted bid-ask spread on weekly options: 12.6%.**
**IMPLICATION FOR THE APP:** The sign of retail P&L flips between gross and net. This is the mathematical statement of "edge measured at midpoint vanishes at executable prices," measured at the population level on $6.4bn of real costs. Any score the app computes from midpoint-derived quantities (IV, Greeks, theoretical value) is computing a number from a price no user can transact at. A score that does not model the spread is not a conservative score; it is a score of a different, better instrument than the one the user will buy.

**CLAIM:** Retail option traders lose 5–9% of their option investment around earnings on average, and 10–14% for high-expected-announcement-volatility events, with aggregate losses ≈$3bn.
**SOURCE:** Tim de Silva, Eric C. So & Kevin Smith, "Losing is Optional: Retail Option Trading and Expected Announcement Volatility," *Review of Finance* 30, 2026, pp. 489–535 (online Oct 2025). https://www.timdesilva.me/files/papers/losing_optional.pdf **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details:** Nasdaq and PHLX clientele-split trade data matched to 32,758 US quarterly announcements, 2010–2021. Retail buys ATM calls in the days before high-EAV announcements; media coverage appears to drive the attention. Market makers absorb the demand; retail purchases raise option-implied variances by **~40%** for top-quintile retail buying. Three loss channels: (1) options overpriced relative to subsequent realized vol — straddles underperform by **~11%** on high-EAV announcement days vs low-EAV and a further **~9%** over the next 10 days, with no reversal; (2) wide pre-announcement spreads costing **~9%** extra on a half-spread assumption; (3) slow closing of losers consistent with the disposition effect. Retail option dollar volume rose from ~$20bn (2010) to ~$240bn (2020). The authors attribute the behaviour to behavioural error rather than hedging, lottery preference, or private information. Transaction-cost estimates assume hold-to-maturity and half-spread, so they are **lower bounds**.
**IMPLICATION FOR THE APP:** Devastating and specific. "News catalyst" is one of the app's four named selection inputs, and the single best-documented systematic retail loss in the options literature is *buying options into a known catalyst*. Retail demand itself inflates the IV by ~40%, and the loss is three-part: overpricing, spread, and failure to exit. If the app ranks contracts higher because an earnings catalyst is approaching, it is mechanically steering users into the configuration with the largest measured retail loss in the literature. The defensible version of a catalyst input is **negative-signed for long premium** and accompanied by an IV-crush warning.

**CLAIM:** Retail option trades average −0.9% per trade, option purchases −3.95%, 0DTE trades −4.6%, with median maturity collapsing from four days to one day between 2020 and 2022.
**SOURCE:** Vincent Bogousslavsky & Dmitriy Muravyev, "An Anatomy of Retail Option Trading," 29 Aug 2024. https://www.lsu.edu/business/files/event-files/2025-finance-mardi-gras/retail_option_trading_v2.pdf **[WP]**
**EVIDENCE STRENGTH:** Moderate (sample of ~5,182 traders using a trading journal — likely more active and sophisticated than typical retail, which the authors note).
**Details:** Average option trade −0.9% (t = −3.57) including commissions and spread; purchases −3.95%; **naked option sales +20%**; stock trades roughly flat (+0.11%). Small traders lose most per option trade (−3.4%); multi-day traders −0.9%. 0DTE ≈ 23% of option trades, −4.6% average. SPY and SPX ≈ 26% of retail option trades; top ten underlyings ≈ 60%. Median moneyness ~0.97–0.98 (ATM to slightly OTM). The authors note typical option spreads of 5–10%+ while observed losses are much smaller, inferring substantial limit-order use.
**IMPLICATION FOR THE APP:** The asymmetry between purchases (−3.95%) and naked sales (+20%) in the same sample is the clearest statement of the structural headwind on long premium. It also confirms the Bakshi–Crosby–Gao direction with real retail trades rather than synthetic portfolios.

**CLAIM:** Customers in the 0DTE SPX market are at the best bid more than half the time and achieve net effective spreads well below marketable-order costs — so the "spread kills you" claim is weaker in the most liquid product than elsewhere.
**SOURCE:** Lin Fu, Sida Li, David K. Musto & Neil D. Pearson, "Hope at a Reasonable Price: Customer Use of Limit Orders in the 0DTE Market," SEC DERA Working Paper, March 2025. https://www.sec.gov/files/dera-hope-reasonable-prc-2503.pdf **[WP — SEC staff, preliminary, not Commission views]**
**EVIDENCE STRENGTH:** Moderate-to-Strong on costs; the paper explicitly does **not** measure customer P&L.
**Details:** Customer presence at the bid in heavily traded slightly-OTM SPXW options peaked near 60% of the day in July 2023 (up from ~40% in July 2020). ~25% of 0DTE trades are filled customer market-turning or pick-off orders; **66% of MTO trades and 68% of PO trades are one contract**, another ~23%/21% are two to five. On two-tick spreads for calls under $3 in the later period, 62.8% of MTOs filled with a net effective spread of **$0.021 vs $0.05 for a marketable order**. For three-tick spreads, one-tick MTOs filled 22–36% with net effective spreads falling from 5.5 to 3.8 cents vs 7.5 cents marketable. Realized spreads for MTOs were generally under half the quoted spread. The authors conclude retail "may be losing money on these trades but they are not losing it to transactions costs" — a qualitative assertion, not a measured result.
**IMPLICATION FOR THE APP:** Important counterweight, and it points to a genuine product feature. In SPX/SPY-class liquidity, a user who posts a limit order pays a small fraction of the quoted spread. The app can add real value by (a) restricting to instruments where this is achievable and (b) coaching limit-order placement with an explicit fill-probability estimate — a feature grounded in a government-authored study rather than folklore.

**CLAIM:** Apparent Sharpe ratios on short-option strategies collapse, and several turn negative, once margin requirements are enforced.
**SOURCE:** Pedro Santa-Clara & Alessio Saretto, "Option Strategies: Good Deals and Margin Calls," UCLA Anderson WP, Nov 2004 (later published in *Journal of Financial Markets*). https://www.anderson.ucla.edu/documents/areas/fac/finance/santa_clara_option.pdf **[WP]**
**EVIDENCE STRENGTH:** Strong.
**Details, transaction costs (mid → bid/ask):** near-maturity 10% OTM put SR 0.555 → 0.425; near ATM straddle 0.533 → 0.351 (mean return −4.9 points); near 10% OTM strangle 1.232 → 0.970; far ATM straddle **0.126 → −0.137**. **Margin calls (costs excluded):** near 5% OTM strangle SR 0.474 → **−0.311** (mean monthly 2.7% → −1.0%); near 10% OTM strangle 0.551 → **−0.306**; near 10% OTM put 0.352 → **−0.239**; near ATM straddle 0.301 → 0.128. Best combined portfolio (long market, short near ATM straddle) margin-adjusted SR 0.128; after the ~4.9% straddle cost ≈0.03, versus ~0.19 for the market itself.
**IMPLICATION FOR THE APP:** Margin calls force exits at the worst moment. Any short-premium strategy the app proposes must be sized against the user's account and margin regime, and the score must not present an unlevered expected return as if it were achievable. On these numbers, the best short-premium portfolio underperformed simply owning the index once costs and margin were applied.

---

## 5. GREEKS-BASED SCREENING AND THE PROBABILITY ERROR

**CLAIM:** The option-implied (risk-neutral) density blends beliefs with risk preferences and is not the real-world probability distribution; recovering the physical density requires additional assumptions that are contested.
**SOURCE:** Stephen Figlewski, "Risk Neutral Densities: A Review," NYU Stern, Nov 2017. https://pages.stern.nyu.edu/~sfiglews/documents/RND%20Review%20ver4.pdf **[WP — authoritative review]**; foundational: Yacine Aït-Sahalia & Andrew W. Lo, "Nonparametric estimation of state-price densities implicit in financial asset prices," and "Nonparametric risk management and implied risk aversion," *Journal of Econometrics* 94, 2000, pp. 9–51. **[PEER]**
**EVIDENCE STRENGTH:** Strong (this is settled theory, not a contested empirical claim).
**Details:** Q and P densities are linked pointwise by the pricing kernel, g(S_T) = k(S_T)·f(S_T), where k embeds risk preferences. Implied volatility is a Q-density forecast, not the market's best P-density forecast: in rationality regressions the slope on IV is commonly **0.7 to 0.9, significantly below 1.0**. Bliss & Panigirtzoglou's best-fitting CRRA risk aversion for the S&P 500 was ~3.53 with strong period-to-period variation. Ross's recovery theorem has been challenged — Jackwerth & Menner found the recovered P-density a poor predictor of future returns.
**IMPLICATION FOR THE APP:** This is a correctness issue, not a tuning issue, and it is the easiest thing in the entire product to get legally and ethically wrong.

- **Delta is not the probability of finishing in the money.** It approximates the *risk-neutral* probability (for a European call, N(d₂) is the risk-neutral ITM probability; delta is N(d₁)). Presenting either as "chance of profit" conflates three distinct things: delta, risk-neutral probability, and real-world probability.
- **"Probability of profit" and "probability of touch," as computed by every retail platform, are risk-neutral quantities**, computed under a measure that prices in a volatility risk premium and the market's risk aversion. Because the equity VRP is negative, risk-neutral downside probabilities are systematically *higher* than physical ones, and risk-neutral upside drift is the risk-free rate rather than the equity risk premium.
- The slope-on-IV result (0.7–0.9) means option-implied vol is a biased-high forecast of realized vol by a measurable amount. The app can state this.

**Concrete recommendation:** label every probability the app displays as "market-implied (risk-neutral)" and state in plain words that it is not a forecast of what will happen. If the app wants a real-world probability, it must estimate P separately — e.g. from a conditional volatility model with an assumed drift — and present the Q and P numbers side by side, with the gap labelled as the risk premium. The side-by-side gap is itself a genuinely novel and honest consumer feature, and it is the only version of "appropriately priced" that is both measurable and truthful.

**CLAIM:** The most predictive characteristics for option returns are simply the contract's position on the implied volatility surface — moneyness, maturity, implied volatility — together with illiquidity and risk measures.
**SOURCE:** Bali, Beckmeyer, Moerke & Weigert (2021), as above. **[WP]**
**EVIDENCE STRENGTH:** Strong.
**IMPLICATION FOR THE APP:** The defensible Greeks-based screen is boring and that is the point: moneyness band, maturity band, liquidity, and vega/theta exposure relative to the user's thesis. There is no evidence for elaborate Greeks-ratio heuristics, and the one well-evidenced result says the simple surface coordinates carry most of the information.

---

## 6. DEALER POSITIONING AND GAMMA EXPOSURE (GEX)

This is the one marketed signal where the peer-reviewed evidence is *better* than expected — and where the retail implementation is nonetheless probably backwards.

**CLAIM:** Intraday market momentum in the S&P 500 appears only when option market makers are net short gamma, consistent with a delta-hedging feedback channel.
**SOURCE:** Guido Baltussen, Zhi Da, Sten Lammers & Martin Martens, "Hedging demand and market intraday momentum," *Journal of Financial Economics* 142, 2021, pp. 377–403. https://academicweb.nd.edu/~zda/intramom.pdf **[PEER]**
**EVIDENCE STRENGTH:** Strong for the conditional effect; the positioning *measure* rests on strong assumptions.
**Details:** Net gamma exposure (NGE) proxy from OptionMetrics and SqueezeMetrics, 1996–May 2020. When lagged NGE is negative, the slope of last-half-hour return on rest-of-day return is **6.63 (t = 4.78), R² 3.58%**; when NGE is positive, **0.82 (t = 1.03), insignificant**. Continuous interaction NGE × rROD = **−123.04 (t = −3.42)**. 2,930 negative-NGE days, 3,158 positive-NGE days. **The NGE measure assumes all listed options are delta-hedged by market makers, that calls are sold by investors, and that puts are bought by investors; OTC positions are omitted.**
**IMPLICATION FOR THE APP:** There is real peer-reviewed support for a dealer-gamma effect on index intraday dynamics. It is conditional (only in the short-gamma state), index-level, intraday, and dependent on a sign convention that the next finding contradicts.

**CLAIM:** For SPX 0DTE, option market makers hold **positive** net gamma in about 88% of intervals, because customers are typically **short** at-the-money straddles — the opposite of the standard retail GEX sign convention.
**SOURCE:** Greg Adams, Chukwuma Dim, Bjorn Eraker, Jean-Sébastien Fontaine, Chayawat Ornthanalai & Grigory Vilkov, "Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs," draft 15 July 2026 (SSRN 5641974). https://www.jean-sebastienfontaine.com/papers/0dte-options-volatility.pdf **[WP]**
**EVIDENCE STRENGTH:** Strong (identified off calendar variation in Tuesday/Thursday expirations 2018–May 2022, plus a diff-in-diff around the 2022 introduction of daily expirations).
**Details:** 0DTE presence **lowers** 10-minute realized volatility by ~**61 annualized bps**, ~7% of the 9.10% sample mean; the gap disappears once 0DTEs trade every business day. Expiration days raise total MM net gamma ~15 bps (0DTE component +27.5 bps, non-0DTE −14 bps). Most of the 0DTE increase (~25 bps) comes from **stale positions opened in longer-dated options before expiration day**; newly opened 0DTE positions add only ~3 bps and are insignificant. Net delta shows no significant change. Two-stage estimate: 1 bp more net gamma ≈ 4 bp lower annualized realized vol. Intraday, a one-SD rise in 0DTE net gamma predicts ~23 bps lower volatility over the next 10 minutes; cumulative ~−55 bps over the first hour. Higher net gamma strengthens order-flow reversal in E-mini futures and weakens intraday momentum (Q4−Q1 momentum gap ≈ −1 to −3 bps over 30 min to 2 h). Despite ~1M daily 0DTE contracts, end-of-day net order imbalance in ATM 0DTEs is **under 5,000 contracts**. 0DTEs were nearly half of SPX options volume in 2024. The authors caution they cannot link E-mini orders to specific option market makers.
**IMPLICATION FOR THE APP:** Two product-critical consequences. First, **the sign convention embedded in retail GEX is empirically wrong for the most important segment of the most important options market.** SqueezeMetrics-style GEX assumes customers buy puts and sell calls; Adams et al. find customers short ATM straddles and dealers long gamma 88% of the time, and Cboe's own data show retail complex positions net short. A "negative gamma, expect momentum" alert that was derived under the opposite assumption is not a weak signal, it is a possibly-inverted one. Second, most of the gamma that matters comes from *stale, previously opened longer-dated positions*, which an intraday-volume-based estimator cannot see at all.

**CLAIM:** Dealer gamma imbalance is associated with intraday momentum vs reversal, strongest in illiquid underlyings.
**SOURCE:** Andrea Barbon & Andrea Buraschi, "Gamma Fragility," SSRN 3725454, 2020 (rev. Mar 2021). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3725454 **[WP — 48-page preprint, not peer-reviewed]**
**EVIDENCE STRENGTH:** Weak-to-Moderate. Negative ex-ante gamma imbalance → momentum; positive → reversal; effect "stronger for the least liquid underlying securities"; related to flash-crash frequency and magnitude. **No effect sizes, coefficients, or identification strategy were obtainable from the landing page.**

**CLAIM:** Critiques of GEX's directional assumptions come from competitors, not from peer review.
**SOURCE:** Jason DeLorenzo (Wizard of Ops / Volland), "Why Not GEX." https://www.wizofops.com/articles/why-not-gex **[BLOG — direct competitor promoting its own product]**
**EVIDENCE STRENGTH:** **No credible evidence found** for the blog's claims as stated; however its central objection coincides with the peer-reviewed/working-paper evidence above.
**Details:** Argues the 2017 SqueezeMetrics assumptions (investors sell calls, investors buy puts) were defensible then and are wrong now that volume has more than tripled; that GEX vendors retain them knowingly; that the "magnet" effect attributed to high-gamma strikes is actually vanna. Volland instead infers direction from which side of the spread a trade executes on, assuming dealers get the better price — i.e. **a quote-rule-class inference, which Amaya et al. measured as 42% wrong.** The article offers no independent evidence.

**Net verdict on GEX:** The *phenomenon* has genuine peer-reviewed support (Baltussen et al., JFE 2021; Adams et al. 2026 working paper). The *retail measure* rests on a positioning assumption that the best recent evidence contradicts, is built on trade-direction inference that is ~42% wrong, cannot observe the stale longer-dated positions that supply most of the gamma, and is sold with intraday open-interest estimates that its own vendors describe as probabilistic with 10–20% drift. Supporting studies and critiques both point the same way: **the effect is real at the index level and the retail proxy of it is not trustworthy.**

---

## 7. SCORING AND COMPOSITE MODELS

**CLAIM:** Strategies should be evaluated on net-of-cost return at each risk level, and several machine-learning portfolio constructions that look excellent gross are catastrophic net.
**SOURCE:** Lasse Heje Pedersen, "Machine Learning and the Implementable Efficient Frontier," *Review of Financial Studies* 39(10), 2026, pp. 3035–3078. DOI 10.1093/rfs/hhag022. https://academic.oup.com/rfs/article/39/10/3035/8524346 **[PEER]**
**EVIDENCE STRENGTH:** Strong.
**Details (1981–2020 out-of-sample, $10bn investor, risk aversion 10):**

| Method | Gross SR | Net SR | Net utility |
|---|---|---|---|
| Portfolio-ML | 1.38 | **1.33** | 0.086 |
| Static-ML* (tuned) | 1.15 | 0.81 | 0.030 |
| Multiperiod-ML* (tuned) | 1.10 | 0.83 | 0.020 |
| Static-ML | 0.95 | 0.79 | −0.165 |
| Multiperiod-ML | 1.15 | **0.26** | −0.453 |
| Markowitz-ML | **2.06** | n/r (turnover 79.36; non-implementable) | n/r |
| Factor-ML | 0.84 | **−18.09** | −2.487 |
| Rank-ML | 1.16 | **−16.73** | −1.210 |

Uses 115 characteristics. The paper's central mechanism: **standard ML favours fleeting, small-stock, high-turnover signals such as one-month reversal**; blending predictability across horizons instead favours persistent signals (value and quality earn the highest feature importance). Larger investors face strictly worse frontiers and tilt away from predictive-but-costly signals.
**IMPLICATION FOR THE APP:** The highest gross Sharpe (Markowitz-ML, 2.06) was non-implementable, and two methods with respectable gross Sharpes had net Sharpes around −17 to −18. This is the canonical failure mode of a composite score: **optimising a composite on gross signal strength selects for the signals that are most expensive to trade.** For an options app where spreads are 5–12% rather than a few basis points, the distortion is far larger. Practical consequence: the composite must be fitted, or at minimum validated, on net-of-spread outcomes, and should deliberately down-weight short-horizon and illiquid-contract signals even where they look strongest gross.

**CLAIM:** Signal correlation and redundancy are substantial among option predictors, and option anomalies are largely absorbed by a conditional factor model.
**SOURCES:** Saretto, RFS 2025 (IPCA), as above **[PEER]**; Bali et al. 2021 **[WP]**, whose own predictor list contains several mechanically overlapping volume measures (so, lso, dso, ldso, modso are variants of the same option-to-stock volume comparison; log versions are mechanically related to their originals) and several overlapping illiquidity measures, and which reports **no multiple-testing correction**.
**EVIDENCE STRENGTH:** Moderate-to-Strong.
**IMPLICATION FOR THE APP:** A 0–100 composite built by averaging IV rank, skew, flow, OI change, put/call ratio and GEX is not averaging six independent opinions. Several are transformations of the same two or three underlying quantities (the vol surface, and option volume relative to stock volume). The resulting score will look more confident than it is — the classic overconfidence failure of naive signal averaging — and will be most wrong precisely in regimes where the common factor moves.

**CLAIM:** Published predictors decay by roughly 58% post-publication, with decay largest for the strongest in-sample effects.
**SOURCE:** McLean & Pontiff, *JF* 2016, as in §3.4. **[PEER]**
**IMPLICATION FOR THE APP:** Build the decay haircut into the model as an explicit parameter rather than discovering it in production.

**On calibration of composite scores:** no literature specific to calibrating retail-facing options composite scores was located. The general forecast-combination and signal-calibration literature (Timmermann on forecast combination; Rapach–Strauss–Zhou on out-of-sample combination; Green–Hand–Zhang on the supraview of return predictive signals; Harvey–Liu–Zhu on multiple-testing-adjusted t-statistic hurdles) is relevant and well known, but **I was unable to verify any of it in this session after the search quota was exhausted, so I am not citing specific findings from it.** Treat these as leads, listed in Open Questions. What *can* be said from the sources actually verified here: (a) composite scores should be fitted on net-of-cost outcomes (Pedersen); (b) the component signals are correlated and largely factor-explained (Saretto; Bali et al.); (c) published effect sizes should be haircut ~40–58% (McLean & Pontiff); (d) no multiple-testing correction is standard even in the best option-ML papers, so the literature's own effect sizes are upper bounds.

**A specific, honest design consequence:** a 0–100 score implies a cardinal, calibrated quantity. Nothing in the verified literature supports cardinal calibration of such a score for an individual options contract. What *is* supportable is an **ordinal screen with explicit disqualifiers** — rank contracts within a liquidity-qualified universe, show the components separately, and never collapse them into a single number that invites the user to read 82 as meaningfully better than 74.

---

## 8. 0DTE AND CURRENT MARKET STRUCTURE

**CLAIM:** 0DTE options reached roughly half of SPX options volume by 2024, and options with ≤1 week to expiry are >90% of retail notional on Cboe's C1.
**SOURCES:** Adams et al. 2026 **[WP]**; Han (Cboe) 2024 **[VENDOR]**; Bogousslavsky & Muravyev 2024 **[WP]** (median retail option maturity fell from four days in 2020 to one day in 2022).
**EVIDENCE STRENGTH:** Strong.

**CLAIM:** 0DTE presence dampens rather than amplifies intraday index volatility.
**SOURCE:** Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov, 2026, as in §6; secondary summary at Quantpedia, 2 Feb 2026 https://quantpedia.com/do-sp500-0dtes-options-increase-market-volatility/ **[BLOG summary]**; corroborating practitioner reporting of Vilkov's earlier work at EQDerivatives, 6 Mar 2024 **[BLOG, paywalled]**.
**EVIDENCE STRENGTH:** Strong for the paper; the secondary sources add nothing independent.
**Note on the competing paper:** Jonathan Brogaard, Jaehee Han & Peter Y. Won, "Does 0DTE Options Trading Increase Volatility?" SSRN 4426358 **[WP]** — identified but **not fetchable in this session**; its findings are unverified here and may or may not agree. Flagged in Open Questions.

**CLAIM:** Retail 0DTE trades average −4.6% per trade.
**SOURCE:** Bogousslavsky & Muravyev 2024. **[WP]**
**EVIDENCE STRENGTH:** Moderate (self-selected journal-using sample).

**CLAIM:** Customers achieve good execution in 0DTE SPX via limit orders, so 0DTE losses are not primarily a transaction-cost story.
**SOURCE:** Fu, Li, Musto & Pearson, SEC DERA 2025, as in §4. **[WP]**
**IMPLICATION FOR THE APP:** 0DTE is where the users are and where the losses are. The combination of findings is unusually clear: execution costs in SPX 0DTE are manageable, so the average −4.6% is coming from the *positions*, not the frictions. There is no version of a 0DTE recommendation engine that this research supports. If the app covers 0DTE at all, the defensible posture is risk display (position-level loss distribution, time decay per hour, probability of touch labelled as risk-neutral) rather than selection or scoring.

---

## DEFENSIBLE DEFINITION OF "APPROPRIATELY PRICED"

**What the app can honestly claim to measure.** Three things, all relative and all stated as such:

1. **Relative richness within the ticker's own history and surface.** "This contract's implied volatility sits in the Nth percentile of this underlying's trailing one-year IV, and the IV-minus-trailing-realized-volatility spread is X vol points." This is an arithmetic fact. It is the one measure with a genuine academic cousin that survives costs in liquid contracts (Goyal–Saretto; Saretto 2005; Muravyev–Pearson 2020: 8.8% gross → 4.1% with good execution → 1.4% and insignificant at full effective spread).
2. **Relative richness across the surface.** Term-structure slope (Vasquez, JFQA 2017) and strike-dimension skew versus the underlying's own history — both computable from a chain, both peer-reviewed as measures.
3. **Expected cost of trading it.** Quoted spread as a percentage of premium, open interest, volume, and an estimated fill price. On the verified evidence this is the single most decision-relevant number on the screen, because it is what flips population retail P&L from positive to negative (Bryzgalova et al.: +$10.4–12.9M/day gross → −$5.0 to −$1.6M/day net; costs $6.4bn vs commissions $0.9bn).

**The honest framing sentence:** *"We do not know whether this option is mispriced. We can tell you how its implied volatility compares with its own history, with its realized volatility, and with the rest of its surface — and what it will cost you to trade."*

**What the app cannot honestly claim.**

- **It cannot claim a contract is cheap or expensive in an absolute sense.** That requires knowing the physical distribution of the underlying's future returns, which is unobservable; option prices give only the risk-neutral distribution (Figlewski; Aït-Sahalia & Lo).
- **It cannot present implied probabilities as real probabilities.** Delta is not P(ITM); risk-neutral P(ITM) is not real-world P(ITM); "probability of profit" and "probability of touch" as computed by retail platforms are risk-neutral. IV is a biased-high forecast of realized vol (rationality-regression slope 0.7–0.9).
- **It cannot claim that high IV rank means an option is overpriced.** No peer-reviewed evidence was found for IV rank as a predictor of anything, and the one vendor backtest found realized volatility *rising* after high-IV-percentile readings at one- and two-week horizons.
- **It cannot claim to detect informed or "smart money" flow.** The publicly inferable version of the flow signal was tested and found weak and one-day-reversing (Pan & Poteshman); trade direction inference from public data is ~42% wrong (Amaya et al.); most retail SPX notional is multi-leg so single legs are not bets (Han/Cboe); the exchange itself cannot identify end users; and the aggressive proprietary flow retail products call "smart money" had t ≈ 0.75.
- **It cannot present a long-premium position's expected return as neutral.** The unconditional mean return on a short-dated 3%-OTM index call is about −59% per 8-day holding period (Bakshi, Crosby & Gao, *Operations Research* 2022); retail option purchases average −3.95% per trade and 0DTE trades −4.6% (Bogousslavsky & Muravyev).
- **It cannot present a 0–100 score as calibrated.** Nothing verified here supports cardinal calibration of a composite options score.
- **It cannot treat an approaching catalyst as a reason to buy premium.** Retail buying into high-expected-announcement-volatility events inflates implied variance ~40% and produces the best-documented systematic retail loss in the literature — ~11% straddle underperformance on the announcement day plus ~9% over the following 10 days, with no reversal, plus ~9% in spread (de Silva, So & Smith, *Review of Finance* 2026).

**Recommended product architecture.** Replace the composite score with a two-stage design:

- **Stage 1 — hard disqualifiers (no score, excluded).** Spread above a threshold as a percentage of premium; open interest and volume below thresholds; maturity/moneyness outside bands where the literature finds any signal. Justification: the IV-vs-HV effect is statistically zero in the widest-spread tercile and the lowest-volume tercile (Saretto 2005), and the ML effect dies at 50% of quoted spread (Bali et al.).
- **Stage 2 — a transparent component panel, ordinally ranked, not summed.** Show each measure separately with its own evidence grade visible to the user, alongside the expected trading cost and an explicit expected-return context line for the structure type. Users should be able to see *why* a contract ranks where it does, which is also the only defensible answer when the ranking is wrong.

---

## SIGNAL VIABILITY TABLE

| Signal | Evidence quality | Likely decay | Retail data obtainability | Belongs in the score? |
|---|---|---|---|---|
| **IV rank / IV percentile** | **None peer-reviewed.** Vendor backtests only, one of which points the wrong way | N/A — never established | Trivial (chain + 1y history) | **No.** Display as descriptive context only, never as a cheap/expensive verdict |
| **IV minus trailing RV spread** | **Strong** (Goyal–Saretto JFE 2009; Saretto 2005; Muravyev–Pearson RFS 2020) | Moderate. Published 2009, heavily traded; apply ~40–58% haircut | Easy | **Yes, with a hard liquidity gate.** 8.8% gross → 4.1% good execution → 1.4% insignificant at full spread; zero in widest-spread tercile |
| **Term-structure slope** | **Moderate** (Vasquez JFQA 2017; magnitudes and net-of-cost unverified) | Moderate-to-high | Easy (chain) | **Yes, small weight,** flagged as unverified on cost survival |
| **Skew / volatility smirk** | **Was Strong** (Xing–Zhang–Zhao JFQA 2010, 10.9%/yr). Now compromised: ≥2/3 of IV-spread and skew predictability is borrow fees (Muravyev–Pearson–Pollet JFE 2025); weak preprint evidence of recent insignificance | **High** | Easy | **As a descriptive measure yes; as a predictive input no** unless the app can condition on borrow fees — and the residual signal requires shorting |
| **Put-call parity deviation / vol spread** | **Was Strong** (Cremers–Weinbaum JFQA 2010, 51 bps/wk) but the authors themselves reported in-sample decay, and JFE 2025 shows it is largely a borrow-fee proxy | **High** | Easy (matched call/put IVs) | **No.** It is mostly a hard-to-borrow indicator; the tradable residual is in stocks retail cannot short |
| **"Unusual options activity" / flow** | **Weak to none for retail-obtainable versions.** Pan–Poteshman (RFS 2006) tested the publicly inferable version and found it weak, one-day-reversing, subsumed; informative class was full-service customers (44 bps), proprietary traders 1.5 bps (t = 0.75); quote-rule direction ~42% wrong (Amaya et al. 2025); majority of retail SPX notional is multi-leg (Cboe 2024) | **High**, and the starting point is near zero | **Signal-grade data not obtainable.** Requires exchange open-close + clientele data | **No.** This is the clearest negative finding in the report |
| **Open interest change** | **Weak** for the classic studies (Bhuyan–Chaudhury: 30 stocks, 6 months, no significance tests, zero stock costs). **Moderate** for Hilliard–Hilliard–Wu (RQFA 2025): 19 bp/day long-short, 13.4 bp after borrow costs, but short-leg-driven, daily horizon, 3-year window | Moderate-to-high | **Partial.** EOD OI is reliable; intraday OI does not exist in public data (vendors estimate with 10–20% claimed drift) | **Marginal.** Only as a next-day signal, which does not match the product's horizon. Use EOD OI for *liquidity screening*, which is its genuinely valuable role |
| **Put/call ratio** | **Moderate but horizon-limited** (Blau–Nguyen–Whitby JBF 2014: P/C beats O/S daily, fades weekly, insignificant monthly) | High (published 2006–2014, widely traded) | Easy | **No for a multi-day product.** The effect lives at a one-day horizon |
| **Option/stock volume ratio (O/S)** | **Moderate** (Johnson–So JFE 2012; Ge–Lin–Pearson JFE 2016 show the signal is in *opening call purchases*, which unsigned O/S cannot isolate) | High | Easy for unsigned; signed version not obtainable | **Marginal, small weight.** The unsigned version is a diluted proxy of the real mechanism |
| **GEX / dealer gamma** | **Moderate-to-Strong for the phenomenon** (Baltussen et al. JFE 2021: 6.63 vs 0.82 slope conditional on NGE sign). **Weak-to-negative for the retail measure** — Adams et al. 2026 find MM net gamma positive in 88% of SPX 0DTE intervals with customers short ATM straddles, contradicting the standard sign convention; most gamma comes from stale longer-dated positions an intraday estimator cannot see | Unknown; the phenomenon is structural so may persist | **Poor.** Requires inferred positioning with a ~42%-error direction rule and estimated intraday OI | **No for single names. No as a signed directional signal.** Possibly as index-level *volatility-regime context* with the sign convention empirically re-derived, not assumed |
| **Greeks filters (delta/gamma/theta/vega bands)** | **Strong, indirectly** — Bali et al. find position on the vol surface (moneyness, maturity, IV) is the most predictive characteristic family | Low (these are constraints, not alpha) | Trivial | **Yes — as the structural backbone,** matching contract to thesis and risk tolerance. Not as alpha |
| **"Probability of profit" / probability of touch** | **Strong theory that these are risk-neutral, not real-world** (Figlewski; Aït-Sahalia & Lo; IV rationality slope 0.7–0.9) | N/A | Trivial to compute | **Yes to display, with mandatory relabelling** as market-implied. Never as a forecast. Side-by-side Q vs estimated P is the honest and differentiating version |
| **Fundamental / EDGAR characteristics** | **Strong** (Zhan–Han–Cao–Tong RFS 2022: nine characteristics, Sharpe > 2, reported to survive costs) | Moderate (published 2022) | Easy — and already in the app's pipeline | **Yes. This is the strongest-evidenced pillar available** for an app with an EDGAR ingestion stage |
| **News catalyst proximity (long premium)** | **Strong — and negative** (de Silva–So–Smith RoF 2026: retail buying inflates implied variance ~40%; −11% announcement-day straddle underperformance, −9% over next 10 days, no reversal, +~9% spread; ~$3bn aggregate retail loss) | Low — behavioural and persistent | Easy | **Yes, with negative sign for long premium.** Must carry an IV-crush warning. Inverting this is the most expensive single mistake the app could make |
| **Trading-cost estimate (spread % of premium, fill estimate)** | **Strong** (Bryzgalova et al. JF 2023; Muravyev–Pearson RFS 2020; Fu et al. SEC DERA 2025) | None — it is a measurement | Easy | **Yes — as a gate and as a headline number.** This is what flips retail P&L sign |

---

## DISCONFIRMING EVIDENCE

Evidence that cuts against the product thesis, against conclusions elsewhere in this report, or against the consensus narrative:

1. **The equity-index variance risk premium may not be statistically significant.** Heston & Todorov find the realized S&P 500 variance premium is not significantly different from zero over the full sample once March 2020 is included (−11.9%/month full sample vs −22.9% pre-COVID; Sharpe −0.23), driven by one >+2000% monthly observation. The premium is far larger in Treasuries and agricultural commodities than in equities. The entire "options are structurally overpriced" story rests on a thinner statistical foundation than practitioners assume.

2. **Retail options traders may not actually lose money.** Amaya, Garcia-Ares, Pearson & Vasquez (2025), using Cboe data with *true* direction and open/close flags, find net performance of Cboe customer SLIM trades held to expiration is positive but insignificant: +$0.34M/day (t = 0.29) for 2020–2023 and +$2.07M/day (t = 1.19) for 2020–2021. They state their results provide no evidence that these trades are unprofitable. The divergence from Bryzgalova et al. (JF 2023) traces to two methodological choices: BPS value expiring options at the quote midpoint rather than exercise value, and infer direction with a quote rule that misclassifies ~42% of trades. Switching to exercise values moves BPS's held-to-expiry estimate from −$1.75M/day to +$0.36M/day. Caveat: the study was funded by a Cboe division and used Cboe-supplied data on Cboe-operated exchanges. Still, it is a serious, specific methodological challenge to the headline retail-loss result, and it means the app should not state as settled fact that retail options traders lose money.

3. **Not all long calls have negative expected returns.** Bakshi, Crosby & Gao report +12% for 1%-OTM weekly calls and +4% for 1%-OTM 28-day calls, alongside −59% and −31% for the 3% and 5% OTM equivalents. The "long premium is a losing proposition" rule is really a statement about *deep* OTM short-dated options. Moneyness is the variable, not direction.

4. **0DTE options appear to reduce, not increase, index volatility.** Adams et al. find ~61 annualized bps *lower* 10-minute realized volatility on 0DTE expiration days (~7% of the sample mean), identified off calendar variation. This contradicts the widely circulated retail narrative that 0DTE gamma destabilizes the market — a narrative the app would be tempted to reproduce.

5. **The standard retail GEX sign convention is contradicted by the best recent data.** GEX assumes customers buy puts and sell calls, implying dealers are typically short gamma. Adams et al. find SPX option market makers net *long* gamma in ~88% of intervals, with customers typically short ATM straddles. Cboe's own data show aggregated retail complex positions are net short. A positioning signal built on the opposite assumption may be inverted.

6. **Transaction costs in options are lower than the quoted spread implies, and retail does use limit orders.** Muravyev & Pearson find effective-to-quoted half-spread ratios of 0.73–0.81 and an "algo" half-spread of ~5.4% (vs 12.8% quoted) for execution timers, who are ~37% of trades. The SEC DERA study finds customers at the best bid >50% of the day in heavily traded 0DTE SPX options, with net effective spreads of 2.1 cents versus 5 cents for marketable orders, and concludes retail "may be losing money on these trades but they are not losing it to transactions costs." The pessimistic cost story in §4 is therefore an upper bound, and the app can legitimately help users land in the better part of that distribution.

7. **Option return predictability may not have decayed.** Bali, Beckmeyer, Moerke & Weigert report that option return predictability is "stable over time and does not vanish towards the end of our sample period," with short-term ATM and OTM options profitable in every month. This cuts directly against the McLean–Pontiff decay prior for the option-specific anomalies, and against my own recommendation to haircut effect sizes. Counter-caveat: at 25% of quoted spread, their own rolling one-year returns were zero or negative in 2016–2019.

8. **Cremers & Weinbaum explicitly tested and rejected the borrow-fee explanation that JFE 2025 later established.** The 2010 paper used stock lending rebate rates and concluded hard-to-borrow stocks did not drive the result. Muravyev, Pearson & Pollet (2025) derive the formula and find ≥2/3 of the effect disappears outside high-fee stocks. Two peer-reviewed papers in good journals reach opposite conclusions on the same mechanism. This should lower confidence in *any* single-paper justification for a score component, including the ones I have graded Strong.

9. **A composite can be worse than its components.** Pedersen's Factor-ML and Rank-ML had gross Sharpes of 0.84 and 1.16 and net Sharpes of −18.09 and −16.73. Combining signals is not a conservative act.

10. **The IV-rank evidence that exists points the wrong way.** The one vendor backtest that tested the economically meaningful question found that after SPY IV exceeded its 90th percentile, realized volatility *rose* 11.43% in the following week and 15.78% over two weeks relative to normal. It is low-quality evidence, but it is the only directly on-point evidence located, and it does not support the heuristic.

---

## OPEN QUESTIONS

1. **Grauer, Schuster & Uhrig-Homburg, "Option Trade Classification" (SSRN 4098475).** Highest-priority gap. This is the dedicated study of how accurately each classification rule signs option trades, and it proposes the depth and trade-size rules used in the `tclf` library. The DOI was not fetchable in this session. Needed: per-rule accuracy percentages on options, and whether any rule reaches usable accuracy. If the answer is "no rule exceeds ~70%," the flow-feature question is settled definitively.
2. **Carr & Wu, "Variance Risk Premiums," *RFS* 22(3), 2009.** Cited throughout the VRP literature; verified only via secondary mentions here. Needed: the variance-swap-rate-minus-realized-variance magnitudes and the five-index results.
3. **Cao & Han, *JFE* 2013, idiosyncratic volatility and delta-hedged option returns.** Citation verified, magnitudes not. Needed for the Greeks/characteristics screen.
4. **Brogaard, Han & Won, "Does 0DTE Options Trading Increase Volatility?" (SSRN 4426358).** Not fetchable. May disagree with Adams et al.; the disagreement itself would be informative about how settled the 0DTE question is.
5. **Vasquez (JFQA 2017) magnitudes and net-of-cost results.** Only abstract-level verification obtained. The term-structure input's weight should not be set until the net numbers are known.
6. **Does the IV-minus-RV effect survive 2010–2026?** Goyal–Saretto's sample ends in the 2000s. Bali et al. imply stability to 2020. A direct post-2010 replication of the straddle sort, net of realistic retail costs, is the single most valuable empirical test the developer could run before shipping.
7. **Is there any public-data flow construction with demonstrated out-of-sample value?** Pan & Poteshman's negative result on Lee-Ready-classified public volume is twenty years old. Whether a modern construction (sweep detection, multi-exchange aggregation, size filters, combined with EOD OI confirmation) does better is, as far as this research found, untested in peer review. This is an answerable research question and the honest basis for a product claim if it works.
8. **Calibration methodology for a consumer-facing composite score.** No literature located. Leads not verified in this session: Timmermann on forecast combination; Rapach–Strauss–Zhou on out-of-sample combination; Green–Hand–Zhang on the supraview of return predictive signals; Harvey–Liu–Zhu on multiple-testing t-hurdles. Needed: whether a Brier-score or reliability-diagram framework can be applied to options contract scores at all, given that outcomes are path-dependent and the user chooses the exit.
9. **How much of the quoted spread does a typical retail app user actually pay?** This is the pivotal unknown parameter for the whole product. Bali et al.'s 15%/25%/50% breakpoints bracket it, and the answer determines whether anything in §2 is usable. Measurable from the app's own fill data once live, and worth instrumenting from day one.
10. **Does the Hilliard et al. (2025) CPIR signal have a long-only, multi-day, cost-surviving variant?** Their result is daily, short-leg-driven, and shorting-dependent. Whether anything remains for a long-only multi-day app is unknown.
11. **What is the correct sign of dealer gamma in single names?** Adams et al. establish customer short-straddle positioning for SPX 0DTE. Nobody located has done the equivalent for single-name equity options, which is what the app would actually score.

---

## TOP 10 SOURCES, RANKED

1. **Bryzgalova, Pavlova & Sikorskaya (2023), "Retail Trading in Options and the Rise of the Big Three Wholesalers," *Journal of Finance*.** https://www.sikorskaya.net/files/Bryzgalova_Pavlova_Sikorskaya_2023.pdf — Retail is 62.6% of options volume; gross P&L positive, net negative; $6.4bn in trading costs vs $0.9bn commissions; losses concentrated in long short-dated options with 12.6% average quoted spreads. The single most important paper for understanding what the app's users will actually experience.
2. **Muravyev & Pearson (2020), "Options Trading Costs Are Lower than You Think," *RFS* 33(11).** https://www.dmurav.com/MuravyevPearson.OptionsTradingCosts.InternetAppendix.pdf — The IV-vs-HV straddle sort at 8.8% gross, 4.1% with execution timing, 1.4% and insignificant at full effective spread. The precise accounting of where the edge goes, and the basis for a defensible cost model.
3. **de Silva, So & Smith (2026), "Losing is Optional: Retail Option Trading and Expected Announcement Volatility," *Review of Finance* 30.** https://www.timdesilva.me/files/papers/losing_optional.pdf — Retail buying into catalysts inflates implied variance ~40%; −11% announcement-day straddle underperformance plus −9% over 10 days with no reversal plus ~9% spread; ~$3bn aggregate loss. Directly indicts the app's "news catalyst" input as currently conceived.
4. **Pan & Poteshman (2006), "The Information in Option Volume for Future Stock Prices," *RFS* 19(3).** https://www.mit.edu/~junpan/volume.pdf — The foundational flow paper, and the one that tested the publicly inferable version and found it weak and one-day-reversing. Full-service customers 44 bps; firm proprietary traders 1.5 bps (t = 0.75). The reason the "unusual options activity" feature cannot work on retail data.
5. **Muravyev, Pearson & Pollet (2025), "Why does options market information predict stock returns?" *JFE* 172.** https://ideas.repec.org/a/eee/jfinec/v172y2025ics0304405x25001618.html — ≥2/3 of IV-spread and skew predictability disappears outside high-borrow-fee stocks. Dismantles the two most popular option-implied directional signals in one paper.
6. **Adams, Dim, Eraker, Fontaine, Ornthanalai & Vilkov (2026), "Do S&P 500 Options Increase Market Volatility? Evidence from 0DTEs."** https://www.jean-sebastienfontaine.com/papers/0dte-options-volatility.pdf — 0DTE dampens volatility by ~61 annualized bps; market makers net long gamma in ~88% of intervals; customers short ATM straddles. The best current evidence on 0DTE and the strongest challenge to retail GEX conventions. [Working paper.]
7. **Bakshi, Crosby & Gao (2022), "Dark Matter in (Volatility and) Equity Option Risk Premiums," *Operations Research*.** https://arxiv.org/pdf/2303.16371 — 3%-OTM weekly calls average −59% per 8-day holding period; 1%-OTM weeklies +12%. The expected-return numbers that any long-premium recommendation must be displayed against, with the moneyness nuance intact.
8. **Bali, Beckmeyer, Moerke & Weigert (2021), "Option Return Predictability with Machine Learning and Big Data," CFR WP 21-08.** https://www.cfr-cologne.de/download/workingpaper/cfr-21-08.pdf — Gross Sharpe 2.06 → 1.17 at 15% of spread → 0.43 at 25% → fails at 50%; vol-surface position is the dominant predictor family. The clearest map of how much edge survives which execution quality.
9. **Baltussen, Da, Lammers & Martens (2021), "Hedging demand and market intraday momentum," *JFE* 142.** https://academicweb.nd.edu/~zda/intramom.pdf — Intraday momentum slope 6.63 (t = 4.78) when dealers are short gamma vs 0.82 (insignificant) when long. The peer-reviewed foundation for dealer-gamma effects, with the positioning-assumption caveat stated by the authors themselves.
10. **Figlewski (2017), "Risk Neutral Densities: A Review," NYU Stern.** https://pages.stern.nyu.edu/~sfiglews/documents/RND%20Review%20ver4.pdf — The authoritative statement that option-implied densities blend beliefs with risk preferences, that IV is a biased forecast of realized vol (rationality slope 0.7–0.9), and that physical-density recovery is contested. The source that keeps the app's probability displays honest.

**Honourable mentions:** McLean & Pontiff (*JF* 2016) on 58% post-publication decay; Pedersen (*RFS* 2026) on net-of-cost composites and the −18 net Sharpe cautionary tale; Zhan, Han, Cao & Tong (*RFS* 2022) on the nine fundamental characteristics that are the app's best-evidenced pillar; Heston & Todorov (2023) on the fragility of the equity VRP; Amaya, Garcia-Ares, Pearson & Vasquez (2025) for the 42% quote-rule misclassification rate and the strongest challenge to the retail-loss consensus; Fu, Li, Musto & Pearson (SEC DERA 2025) on retail limit-order execution in 0DTE; Hilliard, Hilliard & Wu (*RQFA* 2025) as the best recent peer-reviewed OI/volume signal study; Ge, Lin & Pearson (*JFE* 2016) on why O/S works and why the unsigned version cannot capture it; Santa-Clara & Saretto (2004) on margin calls turning short-premium Sharpes negative.
