# Research Strand 12: Volatility Forecasting, Surface Modelling, and Event-Vol Decomposition

**Date:** 11 November 2026
**Scope:** Realised vol estimation; volatility forecasting models and long-horizon accuracy; whether IV encompasses model forecasts; event-vol decomposition; surface fitting; surface relative value; regime conditioning; implementation.
**Context:** The system's one surviving pricing signal is IV minus a volatility forecast at 60–180 DTE on single-name US equities plus index. The spec currently uses trailing realised volatility as the comparison. If the forecast is the model, this strand determines how much of the signal is real.

**Headline:** The literature says three things at once, and they do not point the same way. (1) At the product's exact horizon, better forecasts cut RMSE against future realised vol by roughly 20–34% relative to trailing realised vol — a large, well-measured gain. (2) At index level and one-month horizon, option-implied volatility *statistically subsumes* HAR realised-vol components out of sample, which means the IV-minus-forecast spread may be premium, not mispricing. (3) The paper that established the IV-minus-trailing-RV signal found that repricing options with a cross-sectionally predicted IV made the long-short return insignificant. The build should therefore treat a better volatility forecast as a **contract-selection and sizing input and a richness display**, not as a licence to believe the spread is alpha.

---

## 1. REALISED VOLATILITY ESTIMATION

### CLAIM: Range-based estimators built from daily OHLC are 2.5–14x more efficient than close-to-close as estimators of daily variance, with Yang-Zhang the most efficient and the only one handling both drift and overnight gaps.
- **SOURCE:** Parkinson (1980) *Journal of Business* 53:61–65; Garman & Klass (1980) *Journal of Business* 53:67–78; Rogers & Satchell (1991) *Annals of Applied Probability* 1(4):504–512; Yang & Zhang (2000) *Journal of Business* 73:477–491. Efficiency figures collated in [Portfolio Optimizer, "Range-Based Volatility Estimators: Overview and Examples of Usage"](https://portfoliooptimizer.io/blog/range-based-volatility-estimators-overview-and-examples-of-usage/) (practitioner blog, citing Bennett).
- Theoretical max efficiency vs close-to-close: Parkinson ~5.2x, Garman-Klass ~7.4x, Rogers-Satchell ~6x, Yang-Zhang ~14x.
- **EVIDENCE STRENGTH:** Strong for the underlying estimator papers (all peer-reviewed, foundational). Moderate for the specific efficiency multiples, which are idealised-process figures, not realised gains on single-name equities.
- **IMPLICATION FOR THE BUILD:** Daily OHLC is enough to get most of the way to an intraday realised-variance estimate. Use Yang-Zhang as the primary daily variance estimator: it allows non-zero drift and explicitly incorporates the overnight gap, which matters enormously for single names where earnings and news gap the open. Compute it over a rolling window (YZ requires multi-day windows by construction — it is not a single-day estimator).

### CLAIM: Against intraday realised variance as benchmark, Parkinson and Garman-Klass cut estimation MSE by ~82–83% versus squared close-to-close returns, but all range estimators are biased ~8–18% low.
- **SOURCE:** Mouti, S., "Rough Volatility: Evidence from Range Volatility Estimators," UC Santa Barbara working paper, 2023. [arXiv:2312.01426](https://arxiv.org/pdf/2312.01426). S&P 500, Jan 2000–Apr 2015, Oxford-Man 5-min RV as benchmark.
- Table 1: MSE (×10⁻⁴) vs Oxford-Man RV — Parkinson 0.092, Garman-Klass 0.094, Rogers-Satchell 0.206, close-to-close 0.533. Proportional bias: Parkinson −0.085, GK −0.131, RS −0.176, close-to-close −0.128. Standard deviations: 0.0063 / 0.0058 / 0.0062 / 0.0092.
- Yang-Zhang was excluded from this comparison because it needs multi-day windows.
- **EVIDENCE STRENGTH:** Moderate (working paper, not peer-reviewed; single index; but the result is consistent with theory and with the estimator literature).
- **IMPLICATION FOR THE BUILD:** This is the single most useful number for the data budget question. **Switching from close-to-close to a range estimator buys roughly a 4–6x reduction in MSE of the daily variance estimate, from daily OHLC alone — no intraday data needed.** Correct for the downward bias with a multiplicative scalar estimated per name over history, or simply be aware that the level runs ~10% low. The remaining gap to true intraday RV is real but much smaller than the gap you just closed.

### CLAIM: Realised variance from intraday returns is best computed at ~5-minute sampling as a noise/efficiency compromise; sub-minute sampling requires noise-robust estimators (realised kernels, two-scale, pre-averaging).
- **SOURCE:** Hansen & Lunde, "Realized Variance and Market Microstructure Noise," *Journal of Business & Economic Statistics* 24(2), 2006 ([PDF](https://web-docs.stern.nyu.edu/salomon/docs/Hansen-Lunde.pdf)); Barndorff-Nielsen, Hansen, Lunde & Shephard, "Realized Kernels in Practice: Trades and Quotes," *The Econometrics Journal* 12, 2009 ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1368-423X.2008.00275.x)).
- **EVIDENCE STRENGTH:** Strong (both peer-reviewed, canonical).
- **IMPLICATION FOR THE BUILD:** **Do not buy intraday data for this.** The entire noise-robust estimator literature exists to solve a problem the developer does not have. Virtually every long-horizon forecasting result cited below uses 5-minute RV *as the target to be forecast*, not as a forecasting input that could not be substituted. At a 60–180 day horizon, the forecast is dominated by the persistent/long-run component, and the extra precision of intraday RV over a range-based daily estimator is second-order. If intraday data later becomes free, 5-minute RV plus the overnight return is the standard construction; realised kernels only matter below ~1 minute.

### CLAIM: A practitioner comparison on ETF data found jump-adjusted estimators gave no average forecasting improvement over close-to-close, and recommends averaging Parkinson, Garman-Klass and Rogers-Satchell rather than picking one.
- **SOURCE:** [Portfolio Optimizer blog](https://portfoliooptimizer.io/blog/range-based-volatility-estimators-overview-and-examples-of-usage/) (practitioner), reporting the Lyócsa-Plíhal-Výrost averaged estimator; also cites Shu & Zhang (2006) and Jacob & Vipul (2008) on drift-induced bias in Parkinson/GK.
- **EVIDENCE STRENGTH:** Weak (blog, monthly ETF horizon, not single-name daily).
- **IMPLICATION FOR THE BUILD:** Estimator choice is lower-leverage than estimator *use*. Compute an average of Parkinson, Garman-Klass and Rogers-Satchell alongside Yang-Zhang, and if they disagree materially on a name, treat that as a data-quality flag rather than a signal.

---

## 2. VOLATILITY FORECASTING MODELS AND LONG-HORIZON ACCURACY

### CLAIM (the most important quantitative result in this strand): At the 3–6 month horizon, the best available model cuts forecast RMSE against future realised volatility by ~33% relative to trailing historical volatility; HAR buys ~20–26%; GJR-GARCH buys ~19%.
- **SOURCE:** Conrad, C. & Engle, R. F., "Modelling Volatility Cycles: The MF2-GARCH Model," *Journal of Applied Econometrics*, 2025 ([Wiley, DOI 10.1002/jae.3118](https://onlinelibrary.wiley.com/doi/full/10.1002/jae.3118)); numbers below from the ECB Forecasting Techniques conference version, June 2021 ([PDF](https://www.ecb.europa.eu/press/conferences/shared/pdf/20210615_11th_cft/Conrad_Paper5.pdf)), Table 3. S&P 500, out-of-sample 01/2010–06/2020, monthly rolling re-estimation, target = 5-min realised variance plus overnight return.
- **All values are RMSE divided by the RMSE of a trailing historical-volatility forecast, so trailing HV = 1.000 by construction.** Lower is better.

| Model | Daily | Monthly | **Quarterly (~63d)** | **Semi-annual (~126d)** | Annual |
|---|---|---|---|---|---|
| Trailing historical vol (denominator) | 1.000 | 1.000 | **1.000** | **1.000** | 1.000 |
| Random Walk Type 1 | 0.907 | 1.278 | **1.520** | **1.730** | 1.761 |
| Random Walk Type 2 | 0.907 | 0.771 | **0.857** | **0.858** | 0.793 |
| GJR-GARCH | 0.782 | 0.788 | **0.806** | **0.810** | 0.771 |
| HAR | 0.771 | 0.711 | **0.759** | **0.800** | 0.875 |
| log-HAR | 0.760 | 0.687 | **0.740** | **0.781** | 0.846 |
| log-HAR + leverage | 0.756 | 0.713 | **0.729** | **0.784** | 1.123 |
| MF2-GARCH-rw-126 | 0.751 | 0.693 | **0.672** | **0.657** | 0.688 |
| MF2-GARCH-rw-21 | 0.734 | 0.684 | **0.703** | **0.701** | 0.715 |

- **EVIDENCE STRENGTH:** Strong (peer-reviewed in a top econometrics journal; the specific horizons match the product; the normalisation is exactly the comparison the brief asks for). **Caveat: S&P 500 index only, one out-of-sample decade.**
- **IMPLICATION FOR THE BUILD:** This is the answer to the brief's key question, at least for index options. Three concrete readings:
  1. **Trailing realised volatility is genuinely the weakest estimator, and the penalty is large and quantified.** Replacing it with a long-memory/component model at the quarterly-to-semi-annual horizon cuts RMSE by about a third.
  2. **HAR's advantage decays with horizon and reverses by one year.** HAR goes 0.771 → 0.711 → 0.759 → 0.800 → 0.875 as the horizon lengthens. Beyond six months, plain GJR-GARCH (0.771 at annual) beats HAR (0.875). HAR is a short-horizon tool being extrapolated.
  3. **The model class that wins at 60–180 days is explicitly two-component**: a short-run GARCH piece plus a slowly-varying long-run piece. The longer-window variant (rw-126) wins at quarterly and semi-annual; the shorter-window variant (rw-21) wins daily. Window length should be matched to horizon.

### CLAIM: HAR-Q's measurement-error correction buys 10–17% MSE at one day but only ~0.5–2.3% MSE for individual stocks at one month, and can be worse than plain HAR at monthly horizon.
- **SOURCE:** Bollerslev, T., Patton, A. J. & Quaedvlieg, R., "Exploiting the Errors: A Simple Approach for Improved Volatility Forecasting," *Journal of Econometrics* 192(1):1–18, 2016 ([Maastricht PDF](https://cris.maastrichtuniversity.edu/ws/files/12579554/1600566.pdf); [RePEc](https://econpapers.repec.org/RePEc:eee:econom:v:192:y:2016:i:1:p:1-18)).
- HARQ losses relative to HAR (rolling / increasing window), improvement = 1 − ratio:

| Horizon | S&P 500 MSE | S&P 500 QLIKE | Individual stocks MSE (avg) | Individual stocks QLIKE (avg) |
|---|---|---|---|---|
| h=1 | 0.827 / 0.894 | 0.946 / 0.881 | 0.935 / 0.953 | 0.990 / 0.949 |
| h=5 | 0.948 / 0.903 | 0.916 / 0.854 | 0.984 / 0.963 | 0.931 / 0.907 |
| h=22 | **1.071** / 0.967 | 0.981 / 0.937 | **0.995** / 0.977 | 0.949 / 0.937 |

- In-sample daily R² rises from 0.522 to 0.562 (S&P 500) and from 0.485 to 0.509 (stock average). The authors state gains diminish with horizon as forecasts smooth toward unconditional volatility. Measurement error attenuates the daily AR coefficient badly: 0.651 (OLS) vs 0.953 (instrumented) for the S&P 500.
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, top journal, individual-stock results reported separately).
- **IMPLICATION FOR THE BUILD:** **Do not build HAR-Q.** It needs realised quarticity from intraday data, and at monthly horizon it buys ~0.5% MSE on individual stocks and is actively worse than HAR on the index. The sophistication is in the wrong direction for a 60–180 day product. The useful transferable lesson is the opposite one: because *your* daily variance estimate is noisy, the fitted persistence of any autoregressive model will be biased low, so your forecasts will mean-revert too fast. Use a range-based (lower-noise) estimator as the model input to reduce this bias — this is the cheap version of HAR-Q's insight.

### CLAIM: At 50-day horizons, GARCH(1,1) forecasts can be *worse than the unconditional mean* (negative out-of-sample R²), while a regime-switching multifractal model stays positive.
- **SOURCE:** Calvet, L. E. & Fisher, A. J., "How to Forecast Long-Run Volatility: Regime Switching and the Estimation of Multifractal Processes," *Journal of Financial Econometrics* 2(1):49–83, 2004; working-paper version [NBER WP 9839](https://www.nber.org/system/files/working_papers/w9839/w9839.pdf), Tables 8–9.
- Restricted out-of-sample R², 20-day and 50-day horizons, four USD exchange rates:

| Pair | Horizon | MSM | GARCH(1,1)-t | MS-GARCH |
|---|---|---|---|---|
| DEM/USD | 20d | 0.135 | −0.147 | −0.180 |
| DEM/USD | 50d | 0.038 | **−0.761** | **−1.137** |
| JPY/USD | 50d | 0.213 | **−0.358** | **−0.569** |
| GBP/USD | 50d | 0.273 | −0.026 | 0.038 |
| CAD/USD | 50d | 0.111 | 0.070 | 0.036 |

- 20-day MSE ratios MSM/GARCH: ~0.75 (DEM), 0.78 (JPY), 0.92 (GBP), 0.98 (CAD). At one day the models are near-indistinguishable.
- **EVIDENCE STRENGTH:** Strong methodologically (peer-reviewed, JFEc). **Weak transferability: FX, not single-name equity. This is an extrapolation and should be flagged as such.**
- **IMPLICATION FOR THE BUILD:** The qualitative warning is the point and it corroborates Conrad-Engle. A single-component GARCH extrapolated to 2–6 months can be *actively harmful*: it reverts to a sample unconditional variance that is itself regime-dependent, and it can underperform doing nothing. Any long-horizon forecast needs an explicit, slowly-moving long-run level rather than a fixed unconditional variance.

### CLAIM: In a multi-horizon MSE comparison of 20+ daily-data models, EGARCH(1,1) was the sole Model-Confidence-Set survivor for the S&P 500 at 6-month, 1-year and 2-year horizons, while ARMA(1,1) and EWMA won at 1 day and 1 month.
- **SOURCE:** Vijn, S., "Volatility Forecasting Performance at Multiple Horizons," Erasmus University thesis, Table 7 ([PDF](https://thesis.eur.nl/pub/38972/Vijn-S.-454110-.pdf)). Target: 5-minute realised volatility.
- Best-model MSE: S&P 500 — 1 day ARMA(1,1) 3.107; 1 month EWMA 6.911; 6 months EGARCH-normal 8.864; 1 year EGARCH-normal 9.197; 2 years EGARCH-normal 10.161. GARCH(1,1)-GED blows up to 29.511 at two years.
- **EVIDENCE STRENGTH:** Weak (unpublished student thesis, no HAR, no implied vol). Reported only because it independently corroborates the direction.
- **IMPLICATION FOR THE BUILD:** Corroborates that (a) the horizon changes the winning model class, (b) asymmetric/leverage GARCH is the right GARCH variant at multi-month horizons, and (c) heavy-tailed error distributions can destabilise long-horizon GARCH extrapolation — fit with a normal or Student-t, not GED, and cap the forecast.

### CLAIM: GARCH-MIDAS models with macro variables beat a no-covariate long-run component at 1–4 quarter horizons, but the margins are small (2–5% MSFE) and shrink with horizon; housing starts was the single strongest predictor.
- **SOURCE:** Fang, T., Lee, T.-H. & Su, Z., "Predicting the Long-term Stock Market Volatility: A GARCH-MIDAS Model with Variable Selection," working paper Sept 2018 ([PDF](https://faculty.ucr.edu/~taelee/paper/Fang%20Lee%20Su%20JAE%2020180925.pdf)); published in *Journal of Empirical Finance*. Recursive out-of-sample 2012Q3–2018Q2, target 5-min RV.
- MSFE ratios vs the 4-variable benchmark: housing-starts-only 0.980 / 0.975 / 0.967 / 0.955 at 1–4 quarters; no-covariate model 1.067 / 1.061 / 1.051 / 1.044; all-20-variables 1.390 / 1.318 / 1.207 / 1.193 (overfitting).
- **EVIDENCE STRENGTH:** Moderate (peer-reviewed journal version exists; short out-of-sample window; single index).
- **IMPLICATION FOR THE BUILD:** Macro conditioning of the long-run component is real but small, and the all-variables result is a clean demonstration that adding predictors at quarterly horizon overfits fast. **Do not add macro predictors.** One or two at most, if any. The long-run component should be data-driven (a long rolling window) rather than regression-driven.

---

## 3. DOES IMPLIED VOLATILITY BEAT MODEL FORECASTS, AND DOES COMBINING HELP?

### CLAIM (central disconfirming finding): Out of sample at one-month horizon, option-implied volatility should be used *alone* to forecast realised volatility in stock, FX and bond markets — adding HAR daily/weekly/monthly realised components increases mean absolute forecast error.
- **SOURCE:** Busch, T., Christensen, B. J. & Nielsen, M. Ø., "The Role of Implied Volatility in Forecasting Future Realized Volatility and Jumps in Foreign Exchange, Stock, and Bond Markets," *Journal of Econometrics* 160(1):48–57, 2011 ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304407610000564); working paper [QED WP 1181](http://qed.econ.queensu.ca/working_papers/papers/qed_wp_1181.pdf)). S&P 500 futures, 30-year T-bond futures, $/DM.
- Findings: IV contains incremental information beyond past continuous and jump components in all three markets; IV is an *unbiased* forecast in FX and stock markets; in FX, IV "completely subsumes" the daily/weekly/monthly high-frequency realised measures; out of sample, IV alone is preferred for monthly RV in all three markets. IV also carries incremental information about future *jumps*.
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, *Journal of Econometrics*, explicit in-sample and out-of-sample encompassing tests). **Caveat: index/futures level, one-month horizon, pre-2011 sample, and IV here is a model-free/VIX-style measure.**
- **IMPLICATION FOR THE BUILD:** This is the most dangerous finding for the product thesis, and it must be stated plainly in the build's own documentation. At index level and one-month horizon, **IV minus an RV-model forecast is, statistically, IV minus noise**: the model forecast adds nothing that IV does not already contain, and adding it makes forecasts worse. Under this result the IV-vs-forecast spread is measuring the *variance risk premium*, not mispricing. Two consequences:
  1. **Do not present IV-minus-forecast as a "cheap/expensive" verdict** any more than IV rank should be. Present it as *premium being paid*, which is a different and defensible framing: a persistent premium can be worth collecting on a risk-compensation basis without being a mispricing claim.
  2. **The horizon and the universe are where the hope lies.** Busch et al. is one-month and index. The product is 60–180 days and single names, where option markets are far less informationally efficient, quotes are wider, and the forecast-encompassing result has not been established. This is an open question, not a settled one — flag it as such.

### CLAIM: Option-implied information added to HAR improves one-day forecasts by only ~4–6% on QLIKE and ~4–5% on RMSE; the richer the option extraction, the bigger the gain, but gains remain single-digit.
- **SOURCE:** "On Options-Driven Realized Volatility Forecasting: Information Gains via Rough Volatility Model," 2026 working paper, [arXiv:2604.02743](https://arxiv.org/pdf/2604.02743). SPX 5-min RV 2011–2021, OptionMetrics ~3.06m OTM contracts.
- 1-day out-of-sample: HAR-RV QLIKE 0.0428 → HAR-RV-VIX 0.0409 (−4.4%) → HAR-RV-SVCJ 0.0404 → HAR-RV-RoughHeston 0.0403 (−5.8%). MAE 0.2351 → 0.2205 → 0.2137. In-sample adj R²: 0.605 (HAR) → 0.627 (VIX) → 0.644 (rough Heston). Diebold-Mariano −3.12 for rough-Heston vs HAR. Multi-horizon results to 22 days are reported as a figure only; no quarterly results.
- **EVIDENCE STRENGTH:** Moderate (recent working paper, not peer-reviewed; index only; one-day headline results; internal date inconsistencies noted in the text).
- **IMPLICATION FOR THE BUILD:** Confirms direction of causality in the useful way: **options inform the RV forecast more than the RV forecast informs options.** For a retail single-user system, the cheap version is to put the option-implied level into the forecast (as a regressor or as a shrinkage target), not to pretend the forecast is independent evidence against the option. Rough-volatility spot-vol extraction is out of scope.

### CLAIM: Goyal & Saretto built the IV-minus-historical-vol signal on a 12-month plain close-to-close standard deviation, explicitly declined to use GARCH, never tested a better RV forecast — and found the long-short return became insignificant when options were repriced with a cross-sectionally predicted IV.
- **SOURCE:** Goyal, A. & Saretto, A., "Cross-section of Option Returns and Volatility," *Journal of Financial Economics* 94(2):310–326, 2009 ([working paper PDF](https://www.erim.eur.nl/fileadmin/erim_content/documents/10); [Purdue CIBER WP](https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1054&context=ciberwp)).
- Benchmark: annualised sample standard deviation of daily returns over the trailing 12 months. Options: one-month maturity only, moneyness 0.95–1.05. Gross 10−1 straddle ~21.9%/month (SR ~1.09); net 13.0% / 8.6% / 4.1% per month at 50% / 75% / 100% of quoted spread. Delta-hedged calls 2.3–2.5% gross → ~1.3% / 0.7% / 0.2% net. Illiquid options earn more. Fama-MacBeth regression of monthly Δlog IV on lagged IV, IV minus its 12-month average, and IV−RV: coefficients negative and significant, average R² 18.3%. **Section 6: repricing with cross-sectionally predicted IV renders the long-short return economically and statistically insignificant.** Authors frame the mechanism as mean reversion in the IV/RV gap and investor overreaction, and explicitly decline to claim true alpha.
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, *JFE*; the explicit statements about what was and was not tested are the valuable part).
- **IMPLICATION FOR THE BUILD:** Three things, and they are the most build-relevant items in this report.
  1. **The gap in the literature is exactly the developer's thesis, and it is genuinely unfilled.** Nobody in this lineage has substituted a proper volatility forecast for the 12-month close-to-close standard deviation. That is an honest research contribution for a capstone — but it is *untested*, so it must be framed as a hypothesis the system evaluates, not a finding the system assumes.
  2. **The signal is a 1-month-maturity result.** The product targets 60–180 DTE. The original evidence does not extend there.
  3. **The repricing result is a direct warning.** When the authors replaced raw IV with a *model-predicted* IV, the return vanished. That is the same mechanism as the Busch et al. encompassing result: much of what looks like an IV-vs-vol mispricing is cross-sectionally predictable IV structure. Any build that computes a better forecast must also check that the residual spread is not simply predictable IV.

### CLAIM: The classic finding that IV is a biased but informative forecast of future RV, with rationality-regression slopes below one, is robust; the measured slope rises toward unity once errors-in-variables and sample-overlap problems are handled.
- **SOURCE:** Christensen, B. J. & Prabhala, N. R., "The Relation Between Implied and Realized Volatility," *Journal of Financial Economics* 50(2):125–150, 1998 ([abstract](https://www.researchgate.net/publication/222305915_The_relation_between_implied_and_realized_volatility)); see also [Nielsen & Frederiksen's wavelet re-examination](https://arxiv.org/pdf/1208.4831).
- **EVIDENCE STRENGTH:** Strong for the peer-reviewed core result; Moderate for the magnitude of the bias correction, which is sample- and method-dependent.
- **IMPLICATION FOR THE BUILD:** The bias is the premium. If the slope is below one and the intercept positive, IV over-predicts future RV on average — the entire economic content of the surviving signal. Calibrate this per-name: regress realised 60–180 day forward vol on current same-horizon IV over history and store the intercept and slope. **The actionable spread is the residual from that regression, not raw IV minus a forecast.** This converts the signal from "IV looks high" to "IV is high relative to what IV at this level usually turns out to mean for this name," which is a much harder claim to fool yourself with.

---

## 4. EVENT VOLATILITY DECOMPOSITION (HIGH PRIORITY)

### CLAIM: Option-implied variance for a maturity containing a scheduled earnings date decomposes exactly as σ²(t,T) = σ²_diffusive + σ²_jump/T, which gives a closed-form two-maturity estimator for the implied earnings move.
- **SOURCE:** Dubinsky, A., Johannes, M., Kaeck, A. & Seeger, N. J., "Option Pricing of Earnings Announcement Risks," *The Review of Financial Studies* 32(2):646–687, 2019, DOI [10.1093/rfs/hhy060](https://doi.org/10.1093/rfs/hhy060) ([VU full text](https://research.vu.nl/ws/portalfiles/portal/108247883/Option_Pricing_of_Earnings_Announcement_Risks.pdf)). Earlier version: Dubinsky & Johannes (2006), [Columbia](https://business.columbia.edu/sites/default/files-efs/pubfiles/6051/DJ_2006.pdf).
- **Term-structure estimator (their Eq. 4, the authors' preferred method):** take two ATM maturities T₁ < T₂ that *both* span the announcement, then

  σ²_Q,term = ( σ²(t,T₁) − σ²(t,T₂) ) / ( 1/T₁ − 1/T₂ )

  The diffusive term cancels, isolating the jump variance.
- **Time-series estimator (Eq. 5):** σ²_Q,time ≈ T · ( σ²_before − σ²_after ), comparing IV the day before and the day after the announcement. Implicitly, a maturity that does *not* span the announcement has IV equal to the pure diffusive σ.
- The two estimators correlate ~93% across firms. Averages: term-structure 6.87%, time-series 6.04%.
- Data/method notes: OptionMetrics IvyDB, Jan 2000–Aug 2015, 50 most liquid firms per year (196 firms), 3,008 pooled term-structure observations; options with 3–365 days to maturity; call and put IVs averaged; announcement dates and before-open/after-close timing reconciled across at least two of Thomson Reuters, IBES and Compustat; excludes dividend yields above 2% and prices below $5.
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, *RFS*; explicit formulas; large sample).
- **IMPLICATION FOR THE BUILD:** This is the method. It is implementable with an end-of-day chain and nothing else, and it requires only two maturities. Build it. The data-hygiene requirement is non-trivial and is the real cost: **you need reliable earnings dates with before-open/after-close timing**, cross-checked across sources. Budget more effort for the earnings calendar than for the arithmetic.

### CLAIM: Implied earnings-move volatility systematically exceeds realised earnings-move volatility by ~56–80 bps, i.e. the implied event move is biased high — and one-day ATM straddles around earnings lose ~8% on average.
- **SOURCE:** Dubinsky, Johannes, Kaeck & Seeger (2019), *RFS* 32(2):646–687.
- Implied EAD volatility 8.22% vs realised close-to-close EAD-day volatility 7.42% (≈80 bp premium); on a close-to-open basis, implied 6.87% vs realised 6.31% (≈56 bp). Average one-day ATM straddle return around announcements −7.96%, median −10.24%, t ≈ −13.25. Non-EAD bootstrapped straddle returns are far less negative (1st percentile −2.17%). A simulation with a 1% P-vs-Q jump-vol wedge reproduces ≈−8.5% straddle returns. The authors attribute the premium partly to capital-constrained intermediaries and to the systematic (beta-correlated) component of earnings risk.
- **EVIDENCE STRENGTH:** Strong.
- **IMPLICATION FOR THE BUILD:** The implied event move is *rich but only modestly rich* — a ~7–11% relative premium on the jump-vol component. This corroborates the prior strand's retail-inflation finding (and the −8% announcement-day straddle return is strikingly consistent with the prior ~11% announcement-day loss figure). Two build consequences:
  1. The event component is the single richest part of a single-name chain, so **a 60–180 DTE contract containing 1–2 earnings dates will show an inflated IV that is not a diffusive-vol mispricing.** Comparing that IV to a diffusive-vol forecast produces a spurious "expensive" verdict. This is probably the most important single correction to make to the existing spec.
  2. The premium is a *level* effect on event variance, not a per-name signal. Do not rank names on it.

### CLAIM: Implied earnings-jump volatility has real forecasting power for the realised earnings move — R² ≈ 28.5% on the absolute announcement-day return — but less than diffusive IV has for ordinary volatility.
- **SOURCE:** Dubinsky, Johannes, Kaeck & Seeger (2019), *RFS*.
- Pooled univariate regression of |EAD return| on σ_Q: R² ≈ 28.5%, t = 11.42. Cross-sectional firm-level correlation between average implied and realised EAD volatility ≈ 85%; pooled absolute-return correlation ≈ 55%, rank correlation ≈ 53%. For one-month-ahead volatility, univariate R² ≈ 46% for jump vol vs ≈ 66% for diffusive IV. Earnings-jump vol varies with firm transparency; Apple's time-series standard deviation of implied jump vol is ~3%.
- **EVIDENCE STRENGTH:** Strong.
- **IMPLICATION FOR THE BUILD:** Use the implied jump vol as the *forecast* of the event component. There is no better available estimate. Do not attempt to forecast the event move from history alone; the market's number has R² ≈ 28.5% against the realised move, and nothing in the daily-OHLC toolkit will match that. The prior strand's finding that **filing file size predicts post-filing volatility** is the right complement here: it is a candidate *second* input to the event component, orthogonal to the option market's number, and worth testing as an add-on regressor against the implied jump vol. That is a genuinely novel and defensible model component.

### CLAIM: The practitioner method for a "clean" ex-earnings implied volatility is variance-additivity stripping across the term structure, solved iteratively for the event move that produces the smoothest residual curve.
- **SOURCE:** Moontower, ["How an Option Trader Extracts Earnings from a Vol Term Structure"](https://moontower.ai/blog/how-an-option-trader-extracts-earnings-from-a-vol-term-structure) (practitioner blog, Kris Abdelmessih).
- Identity: σ²_term · T = σ²_regular · (T−1) + σ²_event · 1. Worked example: 40 business days to expiry with earnings on day 35, assumed regular daily move 1.5% (≈24% annualised at √251 ≈ 16), observed term IV 36%. Then 0.36² × 40 = 5.184; regular variance 0.24² × 39 = 2.246; event variance = 2.938, so σ_event ≈ 171% annualised; daily sd = 171%/16 ≈ 10.7%; expected straddle move = 0.8 × 10.7% ≈ 8.6%. The event day carries ~57% of total variance while being 1 of 40 days.
- Clean-vol procedure: guess an earnings straddle S, convert σ_event ≈ (S/0.8) × 16, strip event variance from every expiry containing the event via base variance = (σ²_T·T − σ²_event)/(T−1), rebuild the forward-vol matrix, and choose S that yields the smoothest curve. Worked NVDA example: S = 6.5% gave a clean gently-upward-sloping curve; 5% made one expiry look rich and 8% made it look cheap. Strip the largest event first, then FOMC and calendar artifacts.
- **EVIDENCE STRENGTH:** Moderate as method (it is the same algebra as Dubinsky et al.'s identification, which is peer-reviewed), Weak as evidence (blog, no out-of-sample testing, the 0.8 straddle/sd factor is the normal-distribution MAD approximation and the 251-day annualisation is a convention).
- **IMPLICATION FOR THE BUILD:** Implement this as the operational layer on top of the Dubinsky estimator. The two-maturity closed form gives you an unbiased starting value; the iterative smoothness criterion is what you actually ship, because it generalises to chains with two events, FOMC weeks, and missing maturities. The "57% of variance in 1 of 40 days" observation is the headline number to show the user: **it explains at a glance why an uncorrected IV-vs-forecast comparison is meaningless on a single-name chain near earnings.**

### CLAIM: A commercial vendor reduces the whole single-name term structure to three parameters: 30-day ex-earnings constant-maturity IV, 2-year constant-maturity IV, and an implied earnings effect expressed as a multiple of normal vol.
- **SOURCE:** ORATS, ["Implied Volatility Term Structures: Three Parameters"](https://orats.com/blog/implied-volatility-term-structures-three-parameters) (vendor). Worked NVDA example 24 June 2019: 30-day ex-earnings IV 36.12%, 2-year IV 33.96%, implied earnings effect 277%.
- Method: take smoothed 50-delta IV per expiry; use √DTE as the time variable; identify the expiry containing the next earnings date; build a smooth "unadjusted" curve from the 30-day to the 2-year anchor; add the earnings effect only to expiries after the earnings date; solve jointly for the three parameters minimising squared deviation from the observed 50-delta vols. ORATS also mentions seasonality, short-term ATM slope, skew, kurtosis and wing parameters outside this core.
- **EVIDENCE STRENGTH:** Weak (vendor material, proprietary interpolation, no validation). Useful as an existence proof of a shippable parameterisation.
- **IMPLICATION FOR THE BUILD:** This is the right *shape* for a single-user system: a very low-dimensional, interpretable term-structure model with the event effect as one explicit parameter, fitted by least squares to the 50-delta vols. Three to four parameters on a 30–50 name watchlist is cheap, stable, and auditable. √DTE as the time variable is a sensible practical choice for the ATM term structure. Also note the separate ORATS pieces on [estimating post-earnings IV](https://orats.com/blog/how-to-calculate-expected-implied-volatility-after-earnings).

### CLAIM: Weekly option prices around earnings announcements show measurable efficiency, with the implied move being a price rather than an unbiased prediction.
- **SOURCE:** "The Efficiency of Weekly Option Prices Around Earnings Announcements," *Journal of Risk and Financial Management* 16(5):270, 2023 ([MDPI](https://www.mdpi.com/1911-8074/16/5/270)) (peer-reviewed, lower-tier). Also [MarketFragments, "The Implied Move Is a Price, Not a Prediction"](https://www.marketfragments.com/post/the-implied-move-is-a-price-not-a-prediction) (practitioner).
- **EVIDENCE STRENGTH:** Weak/Moderate.
- **IMPLICATION FOR THE BUILD:** Framing discipline. Display the implied event move as a market price with its historical premium attached (the Dubinsky ~7–11% figure), never as a forecast the user should bet against by default.

---

## 5. VOLATILITY SURFACE FITTING

### CLAIM: SVI can be parameterised to be provably free of static arbitrage via the SSVI (surface SVI) family, with explicit conditions on the parameters.
- **SOURCE:** Gatheral, J. & Jacquier, A., "Arbitrage-Free SVI Volatility Surfaces," *Quantitative Finance* 14(1):59–71, 2014 ([arXiv:1204.0646](https://arxiv.org/pdf/1204.0646); [Imperial PDF](https://www.ma.imperial.ac.uk/~ajacquie/index_files/GJ%20-%20NoArbSVI.pdf)); extended in "Generalised Arbitrage-Free SVI Volatility Surfaces," [arXiv:1210.7111](https://arxiv.org/pdf/1210.7111); see also [Gatheral's Baruch lecture notes](https://mfe.baruch.cuny.edu/wp-content/uploads/2015/06/VW3.pdf).
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, the canonical reference; the arbitrage conditions are mathematical results, not empirical claims).
- **IMPLICATION FOR THE BUILD:** If the system fits a surface, fit SSVI, not raw SVI slice-by-slice, and not a polynomial. SSVI ties slices together through a single ATM total-variance curve and a shape function, which (a) gives calendar-spread consistency for free and (b) drastically reduces the number of free parameters per name — which is exactly what you need on sparse single-name chains. A working open-source SSVI calibrator exists at [github.com/arkonique/ssvi](https://github.com/arkonique/ssvi) (unvetted).

### CLAIM: Practical surface construction requires explicit arbitrage checks, bid-ask- and vega-weighted calibration objectives, and controlled extrapolation; naive flat-vol or SABR extrapolation produces unrealistic tails.
- **SOURCE:** Homescu, C., "Implied Volatility Surface: Construction Methodologies and Characteristics," 2011 ([arXiv:1107.1834](https://arxiv.org/pdf/1107.1834)) — comprehensive survey, not peer-reviewed.
- Key points: Carr-Madan three-test arbitrage check (vertical spreads bounded in [0,1], non-negative butterflies, non-negative calendar spreads); adjust quotes starting from the nearest expiry, staying inside the bid-ask; weight calibration errors by inverse squared bid-ask spread *and* squared vega, with weights capped so deep OTM options cannot dominate; measure errors in implied vol rather than price so errors stay proportional to spreads; plain SVI "may not be arbitrage-free in all situations" so checks are still needed; interpolate linearly in total variance across maturities; flat-vol extrapolation gives unrealistically thin tails, reusing SABR beyond the core gives fat tails and moment explosions; Differential Evolution then a local optimiser for fitting.
- **EVIDENCE STRENGTH:** Moderate (survey; the recommendations are practitioner consensus rather than tested results).
- **IMPLICATION FOR THE BUILD:** This is the operational checklist. Three items matter most for the one-signal product:
  1. **Weight the fit by inverse squared spread and squared vega, capped.** This is the surface-fitting counterpart to the execution strand's spread findings, and it stops a single wide, illiquid strike from dragging the fitted ATM level — the number the entire signal depends on.
  2. **Run the three arbitrage checks on every fit, every night, and flag failures rather than silently fitting.** On a single-name chain a butterfly violation usually means a stale or one-sided quote, which is a data problem the user needs to see.
  3. **Interpolate in total variance in time, and do not extrapolate past the longest listed maturity.** The product's 60–180 DTE window is usually *inside* the listed range for liquid names, so extrapolation should simply be refused.

### CLAIM: A fitted surface is preferable to raw quoted IVs for comparison because raw mid-IVs on single names are contaminated by stale quotes, one-sided markets, strike granularity and discrete dividend/borrow effects — which is why vendors ship fitted surfaces.
- **SOURCE:** [OptionMetrics IvyDB US brochure](https://optionmetrics.com/wp-content/uploads/2024/03/OM_IvyDB-US_Flyer_WEB_REV.pdf) and [IvyDB US detail](https://optionmetrics.com/wp-content/uploads/2023/03/IvyDB-US-Brochure.pdf) (vendor); corroborated by the use of IvyDB's standardised surface in Dubinsky et al. (2019) and the options-driven forecasting paper above.
- **EVIDENCE STRENGTH:** Weak as direct evidence (vendor), Moderate indirectly (the entire empirical options literature relies on IvyDB's fitted standardised surface rather than raw quotes).
- **IMPLICATION FOR THE BUILD:** **If the developer has academic OptionMetrics/IvyDB access, use the standardised constant-maturity surface for all historical work** — model fitting, premium calibration, the per-name IV-to-future-RV regression. Rolling your own historical surface is weeks of work for a worse result. Reserve the self-built fit for *live* end-of-day chains, where IvyDB is not available in time. Be explicit in documentation that the historical calibration and the live computation come from different surface constructions, because that mismatch is a real and easily-overlooked source of spurious signal.

---

## 6. RELATIVE VALUE ON THE SURFACE

### CLAIM (directly adverse to the product's horizon): The implied-volatility term-structure slope predicts one-month straddle returns strongly but has no predictive power for 2–4 month straddle returns.
- **SOURCE:** Jones, C. S. & Wang, T., "The Term Structure of Equity Option Implied Volatility," USC Marshall working paper, Oct 2012 ([PDF](https://msbfile03.usc.edu/digitalmeasures/christoj/intellcont/jones_wang-1.pdf)). Marked preliminary; one section incomplete.
- Slope = long-maturity ATM IV − 1-month ATM IV. Mean slope rises with maturity: 0.0095 (2m), 0.0200 (3m), 0.0251 (4m). Determinants: past-month volatility coefficient −0.6014 (t = −27.89); volatility from t−12 to t−2 coefficient +0.2600 (t = 8.02); adj R² 7.4–17.1%.
- **Short-term (1-month) straddles:** slope coefficient 0.91 (t = 8.27) univariate, 0.84 (t = 7.94) with full controls; adj R² 0.24–1.90%. Quintile portfolios: lowest-slope −6.4%/month, highest +0.6%/month; long-short 7.0%/month (sd 12.2%, monthly SR 0.575, t = 7.72, annualised SR ≈ 2.0); Carhart + SPX-straddle alpha 8.3%/month (t = 7.84).
- **Long-term (2–4 month) straddles:** slope coefficient insignificant in three of four specifications (−0.01 t = −0.28; +0.01 t = 0.29; −0.03 t = −0.78; one specification −0.10 t = −2.82). Long-short quintile spread −0.3%/month (t = −0.84), alpha −0.3% (t = −0.59).
- The slope does *not* predict underlying stock returns. Time-series predictability of average slope for average straddle returns: nothing significant.
- **EVIDENCE STRENGTH:** Moderate (working paper, explicitly preliminary, and the incomplete section is the one controlling for expected realised volatility — which is exactly the control this build cares about). But the short-vs-long contrast is stark and internally consistent.
- **IMPLICATION FOR THE BUILD:** **Do not ship a term-structure-slope relative-value signal at 60–180 DTE.** The effect is a 1-month-maturity phenomenon that is statistically absent at the product's actual horizon. This mirrors the Goyal-Saretto maturity problem and should be treated as a general warning: **the option-returns literature is overwhelmingly a 1-month-maturity literature, and the product's horizon is outside it.** The slope remains useful as a *descriptive* input — specifically as the thing to look at after stripping earnings, to confirm the strip produced a sensible curve, per the Moontower method.

### CLAIM: Slope-sorted straddle long-shorts earn ~19.6%/month gross but only ~5.5%/month after quoted spreads, and become insignificant at 1.25x quoted spread.
- **SOURCE:** Vasquez, A., "Equity Volatility Term Structures and the Cross Section of Option Returns," *Journal of Financial and Quantitative Analysis* 52(6):2727–2754, 2017 ([Cambridge](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/equity-volatility-term-structures-and-the-cross-section-of-option-returns/F0A40E99FD2458367DD9A56A89783D38); summary at [Alpha Architect](https://alphaarchitect.com/2014/01/equity-term-structure-and-option-returns/)).
- Slope = long-dated ATM IV − short-dated ATM IV (short leg = average of 1-month ATM put and call IV, long leg at the same strike). OptionMetrics, Jan 1996–Jun 2007, ~386 stocks/month, decile long-short, one-month holding. Straddle long-short 19.6%/month gross → 5.5%/month after bid-ask (significant) → insignificant at 1.25× quoted spread. Naked-call long-short 24.1% gross → 4.8% net (insignificant). The author rules out volatility risk premia, jump risk, misreaction, known option anomalies, size, book-to-market and momentum as explanations.
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, *JFQA*).
- **IMPLICATION FOR THE BUILD:** The execution-cost fragility pattern is identical to the main signal's (8.8% → 4.1% → 1.4%). A 1.25× quoted-spread assumption kills it. Given the Jones-Wang finding that the effect is absent at long maturity anyway, this closes the question: **skew and slope belong in the system as richness/context displays, not as signals.** This is consistent with the prior strand's finding that skew's directional predictability is largely a borrow-fee proxy. Assessed strictly as relative value, slope fails the horizon test and the cost test independently.

### CLAIM: Volatility-of-volatility (VVIX) carries information about variance risk premia distinct from the VIX level.
- **SOURCE:** Park, Y.-H., "Volatility-of-Volatility and Tail Risk Hedging Returns," Federal Reserve Board FEDS 2013-54 ([Fed](https://www.federalreserve.gov/pubs/feds/2013/201354/201354pap.pdf)); also [a thesis on VIX/VVIX and volatility risk premia](https://nur.nu.edu.kz/bitstreams/856510d1-b7ad-44f7-85fc-4e594b27e768/download) (unpublished).
- **EVIDENCE STRENGTH:** Weak for build purposes (index-level, VIX-options-based, no single-name analogue, and no evidence it improves an IV-vs-forecast signal).
- **IMPLICATION FOR THE BUILD:** Skip. There is no cheap single-name vol-of-vol measure and no evidence of incremental value for this signal. VVIX is at most a regime label (see §7).

---

## 7. REGIME CONDITIONING OF VOLATILITY

### CLAIM: Equity variance risk premia are larger at longer maturities, and expected variance-swap returns are predictable with out-of-sample R² of ~0.04–0.12 (1-month horizon) rising to ~0.17–0.27 in-sample at 3–6 month horizons.
- **SOURCE:** Van Tassel, P., "Equity Volatility Term Premia," Federal Reserve Bank of New York Staff Report no. 867, Oct 2018, rev. Apr 2022 ([PDF](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr867.pdf?sc_lang=en)).
- Average variance-swap rate minus average realised variance widens with maturity: ≈5.75 points at 1 month (20.75 vs 15.00) to ≈8.2 points at 24 months (23.22 vs 15.00) — *computed from the paper's Table 1 means, not a reported premium*. The 12-month realised volatility term premium averaged 2.6% unconditionally, reaching 5–15% in the financial crisis. Return-predictability regressions: 1-month horizon in-sample adj R² 0.18 (1-month contract) falling to 0.10 (24-month), out-of-sample R² 0.12 → 0.04; 3-month horizon 0.27 → 0.17; 6-month horizon 0.34 → 0.27. Weekly premium changes correlate with VIX changes at 0.85 (1-month) and 0.55 (12-month). Premium loads negatively on realised variance, most strongly at short maturities. VIX futures basis averages ≈−0.49 points (cheap to model). Long-dated premia have risen relative to short-dated since the crisis.
- **EVIDENCE STRENGTH:** Moderate-to-Strong (Fed staff report, extensively revised, widely cited; not a journal publication).
- **IMPLICATION FOR THE BUILD:** Three useful things. (1) **The premium the product is harvesting is larger at 60–180 DTE than at 30 DTE** — this is an independent argument for the chosen horizon. (2) It is *predictable*, with usable out-of-sample R², and the predictors include the VIX level and the term-structure level/slope factors — so regime conditioning has genuine support. (3) The premium loads *negatively* on realised variance, which means the naive IV-minus-trailing-RV spread is partly mechanical: when trailing RV is high, the measured spread is small precisely when the premium is also compressed. **Conditioning the signal on the VIX level and the VIX term-structure slope is supported; conditioning it on trailing RV alone is partly circular.**

### CLAIM: Regime-switching volatility models improve realised-volatility forecasts, with the clearest gains at longer horizons.
- **SOURCE:** Ding, Y., Kambouroudis, D. S. & McMillan, D. G., "Forecasting Realised Volatility Using Regime-Switching Models" ([Stirling PDF](https://dspace.stir.ac.uk/retrieve/2df2464a-1aa8-4cba-b60e-4bda18a768eb/Forecasting%20realised%20volatility%20using%20regime-switching%20models.pdf); [SSRN 4415386](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4415386)); "Improving S&P 500 Volatility Forecasting through Regime-Switching Methods," [arXiv:2510.03236](https://arxiv.org/pdf/2510.03236); Calvet & Fisher (2004) above.
- **EVIDENCE STRENGTH:** Moderate for the general direction (multiple independent studies, mixed publication status). Weak for any specific regime-classification method.
- **IMPLICATION FOR THE BUILD:** The gain from "regime switching" at long horizon is largely the gain from *having a slowly-varying long-run level* — which Conrad-Engle's MF2-GARCH delivers more simply and with better-documented long-horizon numbers. **Prefer a two-component model to an explicit Markov-switching model.** If a regime label is wanted for display or for conditioning the premium, use a simple threshold rule on VIX level and VIX term-structure sign (contango vs backwardation): it is interpretable, has no estimation risk, and the Van Tassel results support those two variables specifically. Note that the VIX-term-structure-as-regime material in circulation is overwhelmingly practitioner (e.g. [SharkQuant](https://sharkquant.ai/insights/vix-term-structure-regimes), [Quantpedia](https://quantpedia.com/strategies/exploiting-term-structure-of-vix-futures)) — treat the specific thresholds as unvalidated.

### CLAIM: The VIX futures term structure violates the expectations hypothesis, so slope is primarily a risk-premium signal rather than a forecast of future volatility.
- **SOURCE:** Simon, D. P., "The VIX Futures Basis: Evidence and Trading Strategies," *Journal of Derivatives* 21(3):54, 2014 ([PDF](https://www.efmaefm.org/0efmameetings/efma%20annual%20meetings/2013-Reading/papers/VIX%20paper_EFMA.pdf)); "VIX Futures Term Structure and the Expectations Hypothesis," *Journal of Futures Markets* ([USF copy](https://repository.usfca.edu/cgi/viewcontent.cgi?article=1016&context=fe)).
- **EVIDENCE STRENGTH:** Moderate (peer-reviewed; index-level only).
- **IMPLICATION FOR THE BUILD:** Use the VIX term structure as a *regime label and premium conditioner*, not as a volatility forecast input. Backwardation signals a compressed or negative premium — exactly when an IV-looks-rich reading is least trustworthy. A simple gate ("suppress or downweight rich readings when the VIX curve is in backwardation") is defensible on this evidence.

---

## 8. PRACTICAL IMPLEMENTATION

### CLAIM: The `arch` Python package covers the GARCH family and HAR with a single API, is actively maintained, and is sufficient for everything this build needs on the time-series side.
- **SOURCE:** Sheppard, K. et al., `arch` ([GitHub](https://github.com/bashtage/arch), [PyPI](https://pypi.org/project/arch/)).
- Provides: ARCH, GARCH, TARCH/GJR, EGARCH, EWMA/RiskMetrics; mean models including constant, zero, AR and **Heterogeneous Autoregression (HAR)**, with or without exogenous regressors; Normal, Student-t and GED errors; analytic, simulation and bootstrap multi-step forecasting; IID/stationary/circular-block/moving-block bootstraps; unit-root and multiple-comparison (SPA/Reality Check) procedures. Python 3.9+, NumPy 1.19+, SciPy 1.5+, pandas 1.1+, statsmodels 0.12+.
- **EVIDENCE STRENGTH:** Strong (direct documentation).
- **IMPLICATION FOR THE BUILD:** `arch` gives HAR-with-exogenous-regressors and GJR/EGARCH out of the box, plus the multiple-comparison tests needed to claim one forecast beats another honestly. It does **not** ship range-based or realised estimators — write those yourself (they are a dozen lines each) or use a small package such as [`realized-library`](https://pypi.org/project/realized-library/) (unvetted, early-version). MF2-GARCH has no mainstream Python implementation; the practical substitute is an `arch` GJR/EGARCH whose long-run variance target is a long rolling average (see spec below) rather than the sample unconditional variance.
- **Cost:** Fitting a GJR-GARCH plus a HAR to ~2,500 daily observations takes well under a second per name. A 30–50 name nightly pipeline is seconds of compute. **Nothing in this strand is compute-constrained.** The constraints are data quality (earnings dates, chain snapshots) and the developer's time.

### Realistic nightly pipeline (30–50 names, daily OHLC + EOD chain)

1. Ingest daily OHLC; compute Yang-Zhang daily variance plus the Parkinson/GK/RS average as a cross-check; flag disagreement.
2. Update rolling realised-vol aggregates: 21d, 63d, 126d, 252d, 756d.
3. Fit the forecast model per name (see spec); produce a 60-, 90-, 120- and 180-day forward expected realised volatility.
4. Ingest the EOD chain; clean (drop zero-bid, zero-volume-and-zero-OI, crossed quotes, quotes wider than a threshold); compute mid-IVs.
5. Fit the low-dimensional ATM term structure with an explicit earnings-effect parameter; run the three Carr-Madan arbitrage checks; flag failures.
6. Strip event variance using the earnings calendar; emit both raw and clean constant-maturity IVs at 60/90/120/180 days.
7. Compute the spread: clean IV minus forecast, then the residual from the per-name historical IV-to-future-RV regression.
8. Attach context: VIX level, VIX term-structure sign, number of earnings dates in each expiry, spread/liquidity tercile from the execution strand, and data-quality flags.
9. Persist everything, including the inputs, so the forecast can be scored against realised outcomes later. **This step is the one that makes the project evaluable and is easiest to skip.**

---

## RECOMMENDED VOLATILITY FORECAST SPEC

**Target:** annualised realised volatility of the underlying over the next *h* calendar days, for h ∈ {60, 90, 120, 180}, measured at horizon end by the same estimator used as input (Yang-Zhang) so that forecast and outcome are commensurable.

**Inputs:** daily OHLC (minimum 5 years, 10 preferred); earnings calendar with before-open/after-close timing, cross-checked across at least two sources; EOD option chain; VIX level and VIX futures front/second settle.

**Step 1 — Daily variance estimate.** Yang-Zhang over a rolling window as the primary; average of Parkinson, Garman-Klass and Rogers-Satchell as a cross-check. Apply a per-name multiplicative bias correction estimated over history (range estimators run ~8–18% low per Mouti 2023). Rationale: ~4–6x MSE reduction versus close-to-close at zero data cost, and lower input noise reduces the persistence attenuation that Bollerslev-Patton-Quaedvlieg quantify.

**Step 2 — Diffusive-component forecast (the model).** A two-component specification, because every long-horizon result in §2 points the same way:

&nbsp;&nbsp;&nbsp;&nbsp;`forecast_h = w(h) · short_run + (1 − w(h)) · long_run`

- `long_run` = a slow average of the Yang-Zhang variance over a long window (use 126 trading days for h ≥ 60, matching Conrad-Engle's rw-126 which wins at quarterly and semi-annual), optionally shrunk toward a sector or market-wide average for thinly-traded names.
- `short_run` = an `arch` GJR-GARCH(1,1) or log-HAR fitted to the Yang-Zhang series, forecast forward *h* days.
- `w(h)` declines in *h*. Fit it per name by minimising out-of-sample QLIKE on the forward-*h* outcome, or set it from the model's own mean-reversion rate. At h = 120 the weight on the short-run component should be small; this is the whole lesson of the GARCH-goes-negative-R² result in Calvet-Fisher.
- Use log-variance throughout (log-HAR beats HAR at every horizon in Conrad-Engle's table), and cap the forecast at a historical percentile to prevent long-horizon extrapolation blow-ups.

**Step 3 — Event-component forecast.** For each candidate expiry, count scheduled earnings dates before expiry. For each, take the implied earnings-jump volatility from the Dubinsky et al. two-maturity term-structure estimator. Shrink it downward by ~7–11% (the measured implied-over-realised premium). Optionally test the prior strand's filing-file-size predictor as a second, orthogonal input to the event component — this is a genuine research contribution, not established.

**Step 4 — Reassemble.** Total expected variance over the expiry = diffusive forecast × (T − n_events)/T + Σ shrunk event variance / T. Convert to annualised volatility.

**Step 5 — The signal.** Fit per name, over history: forward realised *h*-day volatility regressed on same-horizon clean constant-maturity IV. Store intercept and slope (expect slope < 1). **The signal is the residual from this regression at the current IV**, not the raw difference. This is what makes the spread a statement about *unusual* premium rather than about the premium's existence, and it is the only version of the signal that survives the Busch et al. encompassing critique.

**Step 6 — Gate and context.** Suppress or heavily downweight when: the expiry's IV could not be cleanly stripped of event variance; the arbitrage checks failed; the VIX curve is in backwardation; the name is in the widest-spread or lowest-volume tercile (zero signal per the prior strands); or fewer than two maturities straddle the next earnings date.

**What NOT to build:** HAR-Q (needs intraday, buys ~0.5% at monthly horizon on stocks), realised kernels or any noise-robust estimator (solves a problem you don't have), explicit Markov-switching (the two-component model gets the same benefit more simply), macro-augmented GARCH-MIDAS (overfits at quarterly horizon), slope or skew as a signal (absent at this maturity, dies at 1.25× spread), vol-of-vol.

---

## FORECAST ACCURACY LADDER

**Part A — estimating today's volatility** (Mouti 2023, S&P 500, vs intraday 5-min RV; MSE ×10⁻⁴):

| Step | MSE | vs close-to-close | Data needed |
|---|---|---|---|
| Squared close-to-close return | 0.533 | — | Daily closes |
| Rogers-Satchell | 0.206 | −61% | Daily OHLC |
| Garman-Klass | 0.094 | −82% | Daily OHLC |
| Parkinson | 0.092 | −83% | Daily OHLC |
| Yang-Zhang | not in this test; theoretically most efficient (~14x vs c2c) and the only one handling overnight gaps | Daily OHLC, multi-day window |
| Intraday 5-min RV | benchmark | — | **Intraday data — not worth buying** |

**Part B — forecasting volatility 3–6 months ahead** (Conrad & Engle, *JAE* 2025, S&P 500, out-of-sample 2010–2020, RMSE relative to trailing historical volatility = 1.000):

| Step | Quarterly (~63d) | Semi-annual (~126d) | Gain vs trailing RV |
|---|---|---|---|
| **Trailing historical volatility (current spec)** | **1.000** | **1.000** | baseline |
| Random Walk Type 1 (last-period RV) | 1.520 | 1.730 | **worse — 52–73% worse** |
| GJR-GARCH | 0.806 | 0.810 | −19% |
| HAR | 0.759 | 0.800 | −20 to −24% |
| log-HAR | 0.740 | 0.781 | −22 to −26% |
| log-HAR + leverage | 0.729 | 0.784 | −22 to −27% |
| **MF2-GARCH (two-component)** | **0.672** | **0.657** | **−33 to −34%** |

**Part C — adding implied volatility.** Not quantifiable at 60–180 DTE from the available literature. What is known:
- At one-month horizon on the index, IV *subsumes* HAR realised components out of sample; adding them *raises* forecast error (Busch, Christensen & Nielsen, *J. Econometrics* 2011). Combination buys nothing — it loses.
- At one-day horizon on the index, adding option information to HAR buys 4–6% on QLIKE/MAE (arXiv 2604.02743).
- No study locates the crossover, and no study tests single-name 60–180 day forecast encompassing. **Flagged extrapolation: the entire Part-C row is an open empirical question, and it is the one the product most depends on.**

**Reading the ladder.** Three honest conclusions:
1. The two biggest, best-evidenced wins are both free: switch the estimator from close-to-close to range-based (~4–6x MSE reduction in the estimate) and switch the forecast from trailing RV to a two-component model (~33% RMSE reduction at the product's horizon). Both need only daily OHLC.
2. **The marginal value of each further step shrinks fast and the horizon works against sophistication.** HAR's advantage over GJR is ~5 percentage points at quarterly and ~1 at semi-annual, and reverses by one year. HAR-Q buys ~0.5% on stocks at monthly. The sophistication ladder flattens almost immediately past step two.
3. **A better forecast does not automatically mean a better signal.** A 33% RMSE reduction improves the forecast. Whether it improves the *tradeable spread* is unestablished, and the two most relevant pieces of evidence (Busch et al.'s encompassing result, Goyal-Saretto's repricing result) both point the other way. The build should measure this, not assume it.

---

## EVENT VOL HANDLING

**Method (implement in this order):**

1. **Build the earnings calendar first.** Date plus before-open/after-close timing, cross-checked across at least two sources. Dubinsky et al. reconciled across three plus news search. Without reliable timing the decomposition is wrong by one full event day, which on a 60-day expiry is roughly half the event variance. Flag and refuse names where timing is uncertain.
2. **Two-maturity closed-form estimate.** Pick two ATM maturities T₁ < T₂ that both span the next announcement: σ²_jump = (σ²(t,T₁) − σ²(t,T₂)) / (1/T₁ − 1/T₂). This is Dubinsky et al.'s Eq. 4 and needs nothing but two IVs and two maturities.
3. **Iterative term-structure strip.** Use the closed-form value as the starting guess, then apply the Moontower procedure across all expiries: for each expiry containing n events, base variance = (σ²_T · T − Σ σ²_event) / (T − n). Solve for the event size that minimises roughness of the resulting clean curve. Strip the largest event first; handle FOMC and other scheduled macro events on a second pass.
4. **Shrink the event size by ~7–11%** before using it in the forecast (implied EAD vol 8.22% vs realised 7.42%; 6.87% vs 6.31% close-to-open; Dubinsky et al.).
5. **Store both curves.** Raw and clean, at 60/90/120/180 constant maturity, every night, so the event effect's own time series is available.
6. **Validate quarterly.** Compare each name's stripped implied event move to its realised announcement-day move. If your strip systematically mis-sizes, the earnings calendar is the first suspect.

**How this changes contract selection:**

- **Count earnings dates per expiry and surface the count prominently.** At 60–180 DTE a single-name expiry contains one or two. The Moontower arithmetic shows an event day can hold ~57% of total variance while being 1 of 40 days. An uncorrected IV comparison on such a chain is not a weak signal, it is a *wrong* one.
- **Never compare a clean diffusive forecast to a raw IV from an event-spanning expiry.** This single error can manufacture an "expensive" verdict on every name approaching earnings. It is the most likely source of systematic false positives in the current spec.
- **Prefer expiries containing the same number of events when ranking names against each other**, or rank strictly on the clean IV residual. Otherwise the cross-sectional ranking is largely a ranking of earnings proximity.
- **Treat an event-spanning expiry's richness as two separate reads.** Clean IV rich relative to diffusive forecast is the signal the product is built on. Event component rich relative to the shrunk implied jump vol is a different, shorter-horizon, better-documented trade (the −7.96% announcement straddle return) that the prior strands' retail-inflation finding corroborates. Do not merge them into one number.
- **Prefer chains with at least two maturities straddling the next announcement.** Without them the decomposition is unidentified and the name should be excluded rather than approximated.
- Use the Dubinsky et al. universe filters as sanity bounds: price above $5, dividend yield below 2%, liquid names only. These exclusions exist because the estimator degrades outside them.

---

## DISCONFIRMING EVIDENCE

1. **Implied volatility statistically encompasses model-based realised-volatility forecasts.** Busch, Christensen & Nielsen (*Journal of Econometrics* 160(1):48–57, 2011) find that out of sample, for monthly realised volatility in stock, bond and FX markets, implied volatility should be used *alone* — mean absolute forecast error *rises* when HAR daily/weekly/monthly realised components are added. In FX, IV "completely subsumes" the realised measures. IV is also an unbiased forecast in the stock and FX markets in their sample. **If this transfers to single names at 60–180 DTE, then IV minus a model forecast is IV minus noise, and the surviving signal is measuring the variance risk premium, not mispricing.** This is the single most important adverse finding in the strand.

2. **When the originating paper replaced raw IV with a model-predicted IV, the signal died.** Goyal & Saretto (*JFE* 94(2):310–326, 2009), Section 6: repricing options using cross-sectionally predicted implied volatility rendered the long-short return economically and statistically insignificant. The authors frame the mechanism as mean reversion and investor overreaction, and explicitly decline to claim alpha. A better model does not obviously rescue the signal — in their own test, a better model *removed* it.

3. **Nothing reliably beats a simple HAR benchmark out of sample.** Pollok, "Predicting Realized Variance Out of Sample: Can Anything Beat The Benchmark?" ([arXiv:2506.07928](https://arxiv.org/pdf/2506.07928)), on 1,078 S&P 500 constituents 1993–2019: HAR has the best RMSE, MAE and QLIKE on the average firm (QLIKE 0.2591 vs LASSO 0.3448; RMSE 0.000519 vs 0.000549). Forecast averaging wins on Mincer-Zarnowitz R² (0.4866 vs 0.4692) but has roughly double the RMSE and 6x the QLIKE. The author's conclusion is that it is hard to unambiguously beat the benchmark, and that rankings flip with the loss function. Note the direct contradiction with Conrad-Engle: this paper tests only *one-day* horizons and no two-component model, which is why both can be right — but it means any claim that model X beats model Y must specify the horizon and the loss function or it is not a claim.

4. **Single-component GARCH extrapolated to long horizons can be worse than doing nothing.** Calvet & Fisher (*Journal of Financial Econometrics* 2(1):49–83, 2004): at 50-day horizons, GARCH(1,1)-t restricted out-of-sample R² is **negative** for three of four currency pairs (−0.761, −0.358, −0.026), and MS-GARCH is worse still (−1.137, −0.569). Negative R² means the forecast is worse than the unconditional mean. FX rather than equity, so transferability is uncertain — but it is a direct demonstration that long-horizon extrapolation of a short-horizon model can destroy value, not merely fail to add it.

5. **HAR's advantage over trailing-RV-class forecasts decays with horizon and reverses.** In Conrad & Engle's own table, HAR's relative RMSE goes 0.771 (daily) → 0.711 (monthly) → 0.759 (quarterly) → 0.800 (semi-annual) → 0.875 (annual), and log-HAR-with-leverage reaches **1.123** at annual horizon — worse than trailing historical volatility. HAR is a short-horizon model and the product's horizon is at the edge of where it helps.

6. **Measurement-error corrections buy almost nothing at the relevant horizon.** Bollerslev, Patton & Quaedvlieg (*Journal of Econometrics* 192(1):1–18, 2016): HARQ's MSE improvement over HAR for individual stocks falls from 6.5% (h=1) to 1.6% (h=5) to 0.5% (h=22), and HARQ is *worse* than HAR for the S&P 500 at h=22 under rolling windows (ratio 1.071). Sophistication does not scale to the product's horizon.

7. **The term-structure relative-value effect is absent at the product's maturity.** Jones & Wang (2012): the IV slope predicts 1-month straddle returns with t-statistics of 8+ and a long-short of 7.0%/month, but for 2–4 month straddles the slope coefficient is insignificant in three of four specifications and the long-short spread is −0.3%/month (t = −0.84). **The broader warning: the option-returns literature is almost entirely a 1-month-maturity literature, and the product's 60–180 DTE horizon sits outside it.** Both the slope signal and the originating IV-minus-RV signal were established on 1-month options.

8. **Range estimators may not forecast better even when they estimate better.** The Portfolio Optimizer tests found that jump-adjusted estimators gave no average forecasting improvement over close-to-close on ETF data, and that forecasts from all estimators had about the same predictive power, concluding there is no best range-based estimator. Weak evidence (blog, monthly horizon, ETFs), but it cautions against assuming the Part-A estimation gain flows through to the Part-B forecast gain.

9. **Macro-augmented long-horizon models overfit quickly.** Fang, Lee & Su: the GARCH-MIDAS with all 20 variables had MSFE ratios of 1.390 / 1.318 / 1.207 / 1.193 at 1–4 quarters — up to 39% *worse* than a 4-variable specification. At quarterly horizon there are very few effective observations, and adding predictors is actively harmful.

10. **The premium is partly mechanical in trailing RV.** Van Tassel (2018/2022) finds the variance term premium loads *negatively* on realised variance. The naive IV-minus-trailing-RV spread therefore narrows when trailing RV is high — at exactly the times the premium is also compressed. Part of what the current spec measures is an artefact of its own denominator.

---

## OPEN QUESTIONS

1. **Does IV encompass model forecasts for single names at 60–180 DTE?** The encompassing literature is index-level and one-month. This is the question the whole product rests on, and it is directly testable with the developer's data: regress forward 60/90/180-day realised vol on clean constant-maturity IV and on the two-component model forecast, jointly, per name and pooled, and test whether the model coefficient is non-zero. **This should be the capstone's central empirical exercise.**
2. **Does replacing Goyal-Saretto's 12-month close-to-close standard deviation with a proper forecast strengthen or weaken the sorted-portfolio result?** Nobody has run it. It is directly runnable on IvyDB. Note that both directions are informative: if the signal weakens, the signal was mean reversion in IV, not volatility mispricing.
3. **Is the Conrad-Engle quarterly/semi-annual result replicable on single names?** Their MF2-GARCH table is S&P 500 only. Single-name volatility has more idiosyncratic jumps and more event structure, and the two-component decomposition may work better (more regime variation) or worse (shorter clean histories, more earnings contamination).
4. **How much does the range-estimator gain in estimation (Part A) actually flow through to forecast accuracy at 60–180 days (Part B)?** No study connects them at this horizon, and the Portfolio Optimizer null result suggests the flow-through may be small.
5. **Does the filing-file-size predictor add to implied jump volatility for the event component?** Implied jump vol has R² ≈ 28.5% against the realised announcement move. Whether a fundamental text-based predictor adds incrementally is unknown and would be a genuine contribution.
6. **Is there a reliable single-name analogue of VIX-term-structure regime conditioning?** Van Tassel's predictors are index-level. Whether a name's own clean term-structure slope conditions its own premium is untested at this horizon (Jones & Wang's §5, which would have tested exactly this, was never completed).
7. **Does the Dubinsky two-maturity estimator remain stable when only one maturity straddles the announcement, or when weekly expiries are included?** Their sample used liquid monthlies; the modern chain has weeklies, which should improve identification but may add noise from thin quotes.
8. **What is the right loss function?** Pollok shows rankings flip between RMSE, MAE, QLIKE and MZ-R². For an options-pricing application QLIKE is the usual choice (proportional errors), but the economically relevant loss is P&L, which is neither. Pick one, state it, and do not switch after seeing results.
9. **Does conditioning the signal on the VIX curve sign actually improve realised outcomes, or merely reduce trade count?** Testable, and must be tested with the gate specified in advance.

---

## TOP 10 SOURCES (RANKED)

1. **Conrad, C. & Engle, R. F. (2025), "Modelling Volatility Cycles: The MF2-GARCH Model," *Journal of Applied Econometrics*** — [DOI 10.1002/jae.3118](https://onlinelibrary.wiley.com/doi/full/10.1002/jae.3118); [ECB conference version](https://www.ecb.europa.eu/press/conferences/shared/pdf/20210615_11th_cft/Conrad_Paper5.pdf). *Peer-reviewed.* The only source giving clean relative-RMSE numbers against a trailing-historical-volatility benchmark at exactly the product's 3–6 month horizon. Directly answers the brief's key question.
2. **Dubinsky, A., Johannes, M., Kaeck, A. & Seeger, N. J. (2019), "Option Pricing of Earnings Announcement Risks," *Review of Financial Studies* 32(2):646–687** — [DOI 10.1093/rfs/hhy060](https://doi.org/10.1093/rfs/hhy060); [full text](https://research.vu.nl/ws/portalfiles/portal/108247883/Option_Pricing_of_Earnings_Announcement_Risks.pdf). *Peer-reviewed.* The event-vol decomposition: closed-form two-maturity estimator, measured implied-vs-realised event premium, and the predictive R² of implied jump vol.
3. **Busch, T., Christensen, B. J. & Nielsen, M. Ø. (2011), "The Role of Implied Volatility in Forecasting Future Realized Volatility and Jumps," *Journal of Econometrics* 160(1):48–57** — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304407610000564). *Peer-reviewed.* The forecast-encompassing result, and the strand's most serious challenge to the product thesis.
4. **Goyal, A. & Saretto, A. (2009), "Cross-section of Option Returns and Volatility," *Journal of Financial Economics* 94(2):310–326** — [working paper](https://www.erim.eur.nl/fileadmin/erim_content/documents/10). *Peer-reviewed.* The origin of the signal. Documents exactly what was and was not tested, and the repricing result that killed it.
5. **Bollerslev, T., Patton, A. J. & Quaedvlieg, R. (2016), "Exploiting the Errors," *Journal of Econometrics* 192(1):1–18** — [PDF](https://cris.maastrichtuniversity.edu/ws/files/12579554/1600566.pdf). *Peer-reviewed.* Quantifies how little measurement-error sophistication buys at longer horizons, and why noisy volatility inputs bias persistence downward.
6. **Calvet, L. E. & Fisher, A. J. (2004), "How to Forecast Long-Run Volatility," *Journal of Financial Econometrics* 2(1):49–83** — [NBER WP 9839](https://www.nber.org/system/files/working_papers/w9839/w9839.pdf). *Peer-reviewed.* GARCH long-horizon R² goes negative; the case for an explicit long-run component. FX data — extrapolation flagged.
7. **Gatheral, J. & Jacquier, A. (2014), "Arbitrage-Free SVI Volatility Surfaces," *Quantitative Finance* 14(1):59–71** — [arXiv:1204.0646](https://arxiv.org/pdf/1204.0646). *Peer-reviewed.* The SSVI parameterisation and its arbitrage-free conditions; the right surface model for sparse single-name chains.
8. **Vasquez, A. (2017), "Equity Volatility Term Structures and the Cross Section of Option Returns," *JFQA* 52(6):2727–2754** — [Cambridge](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/equity-volatility-term-structures-and-the-cross-section-of-option-returns/F0A40E99FD2458367DD9A56A89783D38). *Peer-reviewed.* 19.6% → 5.5% → insignificant at 1.25× spread; the execution-fragility pattern repeating on a second signal.
9. **Van Tassel, P. (2018, rev. 2022), "Equity Volatility Term Premia," FRBNY Staff Report 867** — [PDF](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr867.pdf?sc_lang=en). *Fed staff report, not peer-reviewed.* Premium widens with maturity (supporting the 60–180 DTE choice), is predictable with out-of-sample R² up to ~0.27, loads negatively on realised variance.
10. **Mouti, S. (2023), "Rough Volatility: Evidence from Range Volatility Estimators," UCSB working paper** — [arXiv:2312.01426](https://arxiv.org/pdf/2312.01426). *Working paper, not peer-reviewed.* The only source quantifying range-estimator MSE against intraday realised variance (0.092–0.206 vs 0.533 ×10⁻⁴), which is the daily-vs-intraday data-budget answer.

**Also used:** Jones & Wang (2012) USC working paper (slope absent at 2–4 month maturity — important despite preliminary status); Pollok (2025) [arXiv:2506.07928](https://arxiv.org/pdf/2506.07928) (nothing beats the benchmark); Homescu (2011) [arXiv:1107.1834](https://arxiv.org/pdf/1107.1834) (surface construction checklist); Fang, Lee & Su (2018) (quarterly GARCH-MIDAS, overfitting); Christensen & Prabhala (1998) *JFE* (IV bias); Hansen & Lunde (2006) *JBES* and Barndorff-Nielsen et al. (2009) *Econometrics Journal* (noise-robust estimation — reason to skip intraday); Parkinson (1980), Garman & Klass (1980), Rogers & Satchell (1991), Yang & Zhang (2000) (estimators); [Moontower](https://moontower.ai/blog/how-an-option-trader-extracts-earnings-from-a-vol-term-structure) and [ORATS](https://orats.com/blog/implied-volatility-term-structures-three-parameters) (practitioner/vendor event-strip methods); [arXiv:2604.02743](https://arxiv.org/pdf/2604.02743) (options-driven RV forecasting); [`arch`](https://github.com/bashtage/arch) (implementation).
