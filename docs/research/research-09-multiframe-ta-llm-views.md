# Research Strand 09 — Multi-Timeframe Technical Analysis, Large-Scale Pattern Detection, and LLM View Formation

Date: 10 November 2026
Scope: Part A (multi-timeframe confluence — priority), Part B (automated pattern detection), Part C (LLM directional view formation).

A note on how this was researched: the brief asked me to look for supporting evidence first and with genuine effort. I ran four separately-worded searches aimed specifically at finding peer-reviewed support for timeframe confluence, and I deliberately sought out the steelman version (trend/regime filtering) before assessing anything. Where the evidence cuts against the conclusion I reached, I have said so.

---

## PART A — MULTI-TIMEFRAME CONFLUENCE

### A1. The absence of direct tests

**CLAIM:** There is no peer-reviewed empirical test of multi-timeframe confluence as practitioners specify it (agreement of chart patterns or levels across nested timeframes improving directional accuracy over the best single timeframe).

**SOURCE:** Negative result across four independently-worded searches: ("multi-timeframe technical analysis empirical test predictive accuracy"), ("multiple time frame analysis backtest higher timeframe trend filter lower timeframe entry"), ("timeframe confluence agreement signals improves accuracy academic"), ("hierarchical time scales combining signals different horizons"). Every returned result on the practitioner construct was a broker blog, trading-education site or vendor page — heygotrade, Axiory, VTMarkets, LiteFinance, Pepperstone, TradeFundrr, Colibri Trader, snappchart, tradealgo, Medium. Zero finance-journal, arXiv q-fin or SSRN hits on the construct itself.

**EVIDENCE STRENGTH:** No credible evidence found — and the search was adequate to establish this. Four distinct phrasings returning 100% practitioner sources is itself a finding: a construct this widely taught with this little academic footprint has not been tested, rather than having been tested and passed.

**IMPLICATION FOR THE APP:** The developer's hypothesis is genuinely untested, not refuted. That is a materially different position from candlestick patterns (tested, null). But untested is not evidence of efficacy, and the surrounding literature (A2–A5) is unfavourable.

---

### A2. The rigorous version — frequency decomposition — works, but supports scale SELECTION, not confluence

This is the strongest evidence in the developer's general direction, and it deserves careful reading.

**CLAIM:** Decomposing technical indicators into frequency bands substantially improves equity-premium forecasting, but the mechanism is isolating ONE predictive band and discarding the others — the opposite of requiring agreement across bands.

**SOURCE:** Tobias Stein, "Forecasting the equity premium with frequency-decomposed technical indicators", *International Journal of Forecasting*, 40(1), 6–28, 2024. DOI 10.1016/j.ijforecast.2022.12.001.

**EVIDENCE STRENGTH:** Strong (for the claim as stated). Peer-reviewed in a top forecasting journal; monthly US data Dec 1950–Dec 2017; 16 trend-following strategies; out-of-sample testing with holdout and elastic-net combination; economic value via mean-variance allocation; robust to transaction costs and replicated across 11 international indices (1980–2010).

Findings: predictive power concentrates in cycles of roughly 16–64 months. Out-of-sample R² rises from under 4% (raw indicators) to over 8% (filtered) during recessions. A mean-variance investor would pay roughly 100–150bp/year. High-frequency noise and slow trend components add little and removing them improves results. Predictability is concentrated in recessions and disappears after sharp rebounds. The best frequencies are identifiable in real time.

**IMPLICATION FOR THE APP:** This is the single most important nuance in this report. Stein does not show that multiple scales corroborating each other adds evidence. He shows that most scales are noise and one band carries the signal. Applied to the app, the lesson is "find the one horizon that predicts and ignore the rest", not "require five timeframes to agree". Three further mismatches: (i) the scales are 16–64 *months*, not daily/4h/1h/15m; (ii) the target is the aggregate equity premium (market timing), not single-name or option direction; (iii) the payoff is concentrated in recessions, so an always-on signal would not capture it.

---

### A3. The independence question — nested horizons are largely redundant, and this is now quantified

**CLAIM:** Trend signals computed at different lookback horizons on the same price series are heavily correlated, and removing an intermediate horizon can improve risk-adjusted performance — i.e. adjacent timeframes carry overlapping rather than independent information.

**SOURCE:** Alban Etienne, Jean-Jacques Ohana, Eric Benhamou, Béatrice Guez, Ethan Setrouk, Thomas Jacquot, "Revisiting the Structure of Trend Premia: When Diversification Hides Redundancy", arXiv:2510.23150 [q-fin.PR], v2 28 Oct 2025.

**EVIDENCE STRENGTH:** Moderate. Directly on point and quantitative, with realistic costs (2bp round-turn, 2–15bp roll, 50bp annual fee), rolling out-of-sample windows, and a futures universe across commodities, equities, fixed income and FX. Downgraded from Strong because: the reported correlations are between *sleeve returns* rather than raw signal values; Sharpe differences are small; no confidence intervals or significance tests are reported; and the stated backtest start dates are internally inconsistent (2009 vs 2013).

The numbers that matter for the independence question (2015–2025 sleeve-return correlations):
- Adjacent horizons: 20d–60d ≈ 83%, 60d–125d ≈ 81%, 125d–250d ≈ 84%, 250d–500d ≈ 90%
- Distant horizons: 20d–125d ≈ 59%, 20d–250d ≈ 59%, 20d–500d ≈ 44%

Leave-one-out ablation: removing the 125-day sleeve *improved* Sharpe (0.74 → 0.77 over 2005–2025) and return/max-drawdown while holding benchmark correlation roughly stable. The authors conclude the medium horizon largely overlaps its neighbours and a short+long "barbell" captures most of the performance.

**IMPLICATION FOR THE APP:** At 81–90% correlation, two adjacent timeframes agreeing is close to the same observation counted twice. A confluence score that adds confidence for each agreeing timeframe will be systematically overconfident, because it treats correlated evidence as independent. If the app keeps multiple timeframes at all, the defensible design is a barbell — one short and one long, widely separated — not a six-level ladder. Note also the honest counterpoint the paper itself contains: in one table the all-horizons composite (Sharpe 0.36) underperformed the single 500-day sleeve (0.47), which argues against multi-horizon combination even more strongly than the authors' own framing.

---

### A4. Multiple-testing cost — the hypothesis space the developer proposes is exactly the one that has been shown to produce false discoveries

**CLAIM:** When a large universe of technical rules is tested with proper false-discovery control, apparent outperformance does not survive realistic transaction costs, selected rules do not persist out of sample, and the identity of the "best" rule is unstable across periods.

**SOURCE:** Pierre Bajgrowicz and Olivier Scaillet, "Technical trading revisited: False discoveries, persistence tests, and transaction costs", *Journal of Financial Economics*, 106(3), 473–491, 2012.

**EVIDENCE STRENGTH:** Strong. Top-three finance journal; 7,846 rules from the Sullivan–Timmermann–White universe (filters, moving averages, support/resistance, channel breakouts, OBV); DJIA daily closes 1897–2011; FDR control via Barras–Scaillet–Wermers estimators, compared against White's bootstrap reality check and Romano–Wolf.

Findings: in-sample break-even one-way costs fall from 70bp (1939–62) to zero for 1962–2011, where performance is already nil before costs. Out-of-sample break-even costs are roughly 0–35bp. Fewer than 5% of rules survive the first monthly rebalancing. The authors conclude performance is completely offset by low transaction costs. Critically for timeframe selection: the best rule changes across periods *and across cost assumptions* — at zero cost the 1939–62 winner is a 2-day moving average; at 12.5bp it is a 75/250-day OBV rule.

**EVIDENCE STRENGTH caveat (reported for honesty):** the paper's text asserts out-of-sample performance is negative in recent periods, but its own Table 4 shows positive out-of-sample Sharpe ratios for the FDR portfolio in every period (0.47, 0.01, 0.55, 0.31, 0.34, 0.74). The table does not cleanly support the text. This cuts mildly *in favour* of selected technical rules having some residual value.

**IMPLICATION FOR THE APP:** Six timeframes × ten pattern types = 60 base hypotheses, and far more once each pattern has tunable swing-detection parameters. That is the Bajgrowicz–Scaillet setting in miniature. Without FDR control the app will find patterns that "work" and they will be false discoveries. Options add the specific aggravation that round-trip costs on a single-name option spread are far above the 0–35bp break-even that killed these rules on index futures.

---

### A5. Timeframe stability — direct evidence that the "right" horizon shifts

**CLAIM:** The optimal lookback/timeframe is not stable out of sample; it shifts with period and with cost assumptions, which is the signature of fitting rather than a real effect.

**SOURCE:** Bajgrowicz & Scaillet (2012), Table 3 (best rule varies by period and cost level); corroborated by Etienne et al. (2025), where the contribution of each horizon varies and the composite can be beaten by a single sleeve.

**EVIDENCE STRENGTH:** Moderate-to-Strong (two independent sources, one peer-reviewed in JFE).

**IMPLICATION FOR THE APP:** Any timeframe weighting the developer chooses by inspecting historical performance is a fitted parameter and must be validated on data not used to choose it. In practice this means the app cannot "tune" which timeframes matter without burning a holdout.

---

### A6. The one arXiv paper that claims multi-timeframe NN profitability does not support the claim

**CLAIM:** The only arXiv paper directly titled around multi-timeframe algorithmic trading contains no test of multi-timeframe benefit and has multiple methodological defects.

**SOURCE:** "Neural Network-Based Algorithmic Trading Systems: Multi-Timeframe Analysis and High-Frequency Execution in Cryptocurrency Markets", arXiv:2508.02356 (2025).

**EVIDENCE STRENGTH:** Weak / not usable. Specific defects: no single-timeframe baseline anywhere (the only comparison is CNN vs LSTM vs no-attention — removing attention is not a timeframe ablation); only metric reported is profit factor (1.15 best) with no period, Sharpe, drawdown or confidence intervals despite claims of statistical confidence; the chosen architecture is labelled "optimal" on the same numbers used to report it, indicating selection on the reported metric; inputs are unsynchronised (S&P 500 market hours, GDELT at 15-min, monthly MAs from daily bars) feeding minute-level decisions, so look-ahead cannot be excluded; costs stated as 0.05% with no slippage model and unclear whether Table 1 is net; no code or data.

**IMPLICATION FOR THE APP:** Do not cite this as support. It is the paper a search for supporting evidence surfaces first, and it does not survive inspection.

---

### A7. The steelman — trend/regime filtering — is the strongest practitioner-side case and it is weak

**CLAIM:** Adding an absolute trend filter to a momentum signal improved Sharpe in a commodity ETF study, but the test does not actually combine different timeframes and the methodology is not rigorous.

**SOURCE:** Cyril Dujava, "Dual vs. Single Momentum in Commodities: Enhancing Risk-Adjusted Returns through Absolute Trend Filtering", Quantpedia, 15 June 2026. **Label: vendor/sponsored blog, not peer-reviewed.** Builds on Jegadeesh & Titman (1993), Moskowitz–Ooi–Pedersen (2012), Antonacci (2014).

Results: 11 of 12 dual-momentum configurations beat the matched relative-momentum version on Sharpe; best dual config 0.63 vs benchmark 0.30; max drawdown improves from -63.9% to -30.1% in the best case.

**EVIDENCE STRENGTH:** Weak. The decisive problem: the SMA length is constrained to equal the momentum lookback, so both signals use the *same* horizon in two different ways. This is not a multi-timeframe test. Further: zero transaction costs, zero risk-free rate (which flatters the cash leg), four ETFs, ~19 years, full parameter grid reported with no out-of-sample period, an un-rebalanced benchmark, and sponsored content with promotional material. The author's language ("overwhelmingly supports", "universally outperformed") substantially overstates the evidence.

**IMPLICATION FOR THE APP:** Even the best practitioner-side case for "higher timeframe context improves lower timeframe trading" collapses on inspection into a single-horizon trend filter tested without costs. Much of its benefit plausibly comes from being out of the market during downtrends — a risk-management effect, not a directional-prediction effect.

---

### A8. Temporal aggregation — suggestive but not financial

**CLAIM:** Finer temporal granularity can inflate in-sample fit while worsening out-of-sample cumulative error.

**SOURCE:** Hugo Moreira (CIES, Iscte Lisbon), "The Granularity Paradox: How Temporal Disaggregation Inflates In-Sample Fit and Compounds Out-of-Sample Error", arXiv (2026).

**EVIDENCE STRENGTH:** Weak for this application. The data is Portuguese public-procurement IT contract values, not financial markets; the mechanism is error compounding in *recursive* multi-step forecasts (the author explicitly attributes the paradox to recursive feedback topology, not model complexity); non-recursive linear regression was stable across all six granularities. Illustrative numbers: daily persistence had training R² 0.78 but test R² -1.12.

**IMPLICATION FOR THE APP:** Only a loose warning. If the app does not do recursive multi-step forecasting, the specific mechanism does not apply. Cite it as a caution about granularity flattering in-sample diagnostics, not as evidence against multi-timeframe analysis.

---

## PART B — LARGE-SCALE AUTOMATED PATTERN DETECTION

### B1. Fibonacci retracements — RETRIEVED, and it is a clean null against the right control

**CLAIM:** Price behaviour around Fibonacci retracement zones is statistically indistinguishable from behaviour around non-Fibonacci zones.

**SOURCE:** Prodromos Tsinaslanidis and Nikolaos Voukelatos, "Automatic identification and evaluation of Fibonacci retracements: Empirical evidence from three equity markets", *Expert Systems with Applications*, vol. 391 (2021). DOI 10.1016/j.eswa.2021.115893. Published online 20 Sept 2021.

The paper's own stated highlights: an algorithmic scheme identifies Fibonacci retracements; retracements are evaluated by constructing zones around their levels; there is a positive relationship between zone width and the probability of price bounces; **price behaviour on Fibonacci and non-Fibonacci zones did not differ statistically.**

**EVIDENCE STRENGTH:** Strong for the null. This is the control test the question requires — Fibonacci levels versus other levels, not Fibonacci levels versus nothing. Three equity markets, automated (non-discretionary) identification. One residual uncertainty: I could not confirm from the retrieved record how the non-Fibonacci comparison zones were constructed (random placement versus systematic arbitrary ratios). The full text sits behind the Elsevier paywall; the bibliographic record and the authors' own highlights are the basis here.

**IMPLICATION FOR THE APP:** This is the decisive finding on Fibonacci. The "positive relationship between zones and bounce probability" result explains why Fibonacci appears to work to practitioners: wider zones catch more bounces, and price bounces near *any* prior level. The 0.382/0.5/0.618 ratios specifically contribute nothing. The developer should drop Fibonacci levels as a *distinct* evidence source. If round-number and prior-swing levels are wanted, implement those directly on the order-clustering mechanism the prior strand already identified — that at least has a microstructure story.

### B2. Elliott wave — the absence of any validation is confirmed

**CLAIM:** No inter-rater reliability study or algorithm-agreement study for Elliott wave labelling exists.

**SOURCE:** Confirmed by targeted search ("automated Elliott wave labelling algorithm validation inter-rater agreement reliability study"), which returned exclusively medical and engineering inter-rater work — EEG waveform reliability, pharmacovigilance label extraction, movement-related cortical potentials, decay-stage identification. Not one financial result. A second search on Elliott wave empirical testing returned: a retrospective review (ResearchGate), a currency-market study (D'Angelo & Grimaldi, semanticscholar), a Persian-language journal article, a medRxiv paper on whether *pandemics* obey the Elliott wave principle, and an MDPI *Applied Sciences* (14(24):11897) paper combining LLMs with Elliott wave — a low-barrier venue for this subject matter.

**EVIDENCE STRENGTH:** No credible evidence found. The prior strand's conclusion is **confirmed, not overturned.**

**IMPLICATION FOR THE APP:** This is the most serious problem in the developer's hypothesis. Elliott wave has no established construct validity: there is no demonstration that two competent analysts, or two implementations of a labelling algorithm, assign the same wave count to the same series. Without inter-rater reliability there is nothing to validate — a signal that cannot be reproduced cannot be backtested, and any backtest of one particular implementation measures that implementation, not the theory. Of everything in the developer's hypothesis, this is the component I would drop first.

### B3. CNNs on candlestick images — no methodological improvement

**CLAIM:** Recent CNN-on-chart-image work does not establish that chart images carry tradeable information, and the representative papers have the documented failure modes.

**SOURCE:** Duong, Hoang, Duong, Dinh, Le, Nguyen, Nguyen & Tran (FPT University Hanoi), "Investigating Market Strength Prediction with CNNs on Candlestick Chart Images", arXiv:2501.12239 (IEEE conference template, venue unnamed). Data: daily AAPL, EUR/USD, BTC, 2017–30 Oct 2023.

**EVIDENCE STRENGTH:** Weak. Defects: no backtest, no portfolio return, no Sharpe, no transaction costs — classification metrics only; the train/test split method and test period are not described, so chronological separation cannot be confirmed (and reported BTC accuracy of 0.792 is implausibly high for daily direction, consistent with a shuffled split); internal inconsistencies, with the text saying the pattern-augmented approach did not outperform while Table II shows BTC include-pattern 0.792 > non-pattern 0.765, and an abstract claiming performance "peaked at approximately 0.7" contradicting its own tables; the authors assert time-series data is superior without running the experiment that would show it. A replicated DCP model sat at chance (~0.5) for 20 epochs.

**IMPLICATION FOR THE APP:** No usable signal here. Treat high reported accuracies in this subfield as leakage until a chronological split and a cost-aware backtest are shown.

### B4. The best-quality recent evidence — VLMs reading candlesticks perform near chance

This is the closest published analogue to what the developer wants to build, and it is worth dwelling on.

**CLAIM:** Frontier vision-language models shown daily and weekly candlestick charts achieve near-chance directional accuracy, with several models posting negative information coefficients, and do not clearly beat XGBoost on numerical features.

**SOURCE:** Kaiqi Hu (University of Leeds), Linda Xiao, Shiyue Xu, Ziyi Tang (Sun Yat-sen University), Mingwen Liu (Likelihood Lab), "Do VLMs Truly 'Read' Candlesticks? A Multi-Scale Benchmark for Visual Stock Price Forecasting", arXiv:2604.12659v1 [cs.LG], 14 April 2026.

Design: paired daily and weekly candlestick charts for the same stock and cutoff date, up to 50 candles each with 5/20/90-period moving averages and a volume panel; HS300 and S&P 500 universes; 30-day forward return target; seven VLMs benchmarked against XGBoost.

Findings: HS300 accuracy ranges ~49–54%; best is Claude-Sonnet-4-5 (thinking) at 53.5%; Claude-Haiku-4-5, GPT-4o and GPT-5-mini post negative IC; models perform acceptably only in persistent trends and weakly in the more common mixed conditions; accuracy is higher in bear than bull markets; models show directional bias and limited sensitivity to the horizon stated in the prompt; XGBoost on numerical features is competitive with mean IC similar to several VLMs. A "peeping" check comparing two GPT-4o snapshots found no clear look-ahead, though the authors describe this as narrow.

**EVIDENCE STRENGTH:** Moderate. Recent, directly on point, with a real baseline and a contamination check. Downgraded from Strong by: no fine-tuning (which the authors note may limit performance); internal inconsistency where the confusion-matrix section calls Claude-Haiku-4-5 "best-performing" while Table 4 shows Claude-Sonnet-4-5 higher; and a "significantly higher" claim for 5-day over 30-day IC resting on 0.047 vs 0.042.

**The critical gap for Part A:** the paper pairs two scales but runs **no ablation** comparing daily-only, weekly-only and combined inputs. It describes cross-timeframe consistency as a goal but reports no quantified agreement result. So even the one benchmark built around multi-scale chart reading did not test whether multi-scale helps.

**IMPLICATION FOR THE APP:** This is close to a direct test of the app's core premise — an LLM looking at charts at two timeframes to form a directional view — and the answer is roughly coin-flip, with XGBoost on plain numbers matching it. The developer should treat this as the realistic performance ceiling for a chart-reading LLM component, not a floor to be improved on with better prompting.

### B5. Time-series foundation models are not alpha engines

**CLAIM:** Pretrained time-series foundation models produce small and sparse gains over a random walk on financial returns and have not been shown to generate tradeable alpha.

**SOURCE:** Miquel Noguer i Alonso and Rodolfo Pereira Franklin, "Pretrained Time-Series Foundation Models for Financial Return Forecasting", arXiv:2606.27100, 25 June 2026. Six TSFMs (TimeGPT/TimeGPT-LH, TimesFM-2.5, Moirai-2.0, Chronos, Chronos-2) vs five from-scratch neural models (NBEATS, NHITS, PatchTST, iTransformer, KAN); five US stocks; 512-day lookback; 20-business-day horizon; rolling-origin evaluation.

Findings: TSFMs won 8 of 10 task-level comparisons against from-scratch models, but gains against the random-walk benchmark are small and sparse, with Diebold–Mariano significance only for Chronos on AMZN and Moirai-2.0 on GOOG. Skill scores often near or below zero. The authors' own conclusion is that TSFMs are useful priors that reduce development cost but are not reliable alpha generators in realistic deployment. **No trading simulation and no transaction costs** — forecast-error metrics only.

**EVIDENCE STRENGTH:** Moderate for the negative claim; the five-stock universe is thin.

**IMPLICATION FOR THE APP:** There is no off-the-shelf foundation model that solves the directional problem. Nothing has improved on the Lo–Mamaysky–Wang (2000, *Journal of Finance* 55(4)) kernel-regression baseline in a cost-aware way that I could find; the 2020–2026 ML literature has added model complexity without adding methodological rigour.

---

## PART C — HOW LLM-DRIVEN PORTFOLIOS FORM DIRECTIONAL VIEWS

### C1. Lopez-Lira & Tang — the reference methodology, and it uses no price data at all

**CLAIM:** The best-documented LLM return-predictability result forms its directional view from news headlines alone, with no price or chart input, and its profitability does not survive realistic transaction costs.

**SOURCE:** Alejandro Lopez-Lira and Yuehua Tang (University of Florida), "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models", arXiv:2304.07619, first version April 2023, revised September 2024.

Method: the model receives a headline plus the company name — the prompt states the headline is the only information provided. It answers YES/NO/UNKNOWN on whether the news is good or bad for the short-term price, plus one sentence of reasoning, mapped to +1/-1/0. Temperature 0.

Results: daily-rebalanced long-short on GPT-4 scores earns ~38bp/day before costs, annualised Sharpe 3.28, max drawdown -17.4%, cumulative pre-cost return over 650% from Oct 2021 to Dec 2023. The short leg (29bp/day, Sharpe 2.12) dominates the long leg (9bp/day, Sharpe 0.90). **At 5bp round-trip, returns stay above 300%; at 20bp the strategy is unprofitable.** When the ChatGPT score is included, RavenPack's commercial sentiment score becomes statistically insignificant. Model-size monotonicity: GPT-1, GPT-2 and BERT show no predictability with negative Sharpes; GPT-3.5 reaches 1.79, DistilBart-MNLI 1.61, BART-large 1.24, BERT-large 1.12. Contamination handling: the sample starts October 2021, after the stated September 2021 cutoff of gpt-4-0314.

**EVIDENCE STRENGTH:** Moderate-to-Strong as evidence about news-sentiment extraction; **no evidence whatsoever about chart-based view formation.**

**IMPLICATION FOR THE APP:** Two things the developer should take from this. First, the one documented success case for LLM directional views is an event-reaction/sentiment strategy on text, not a pattern-recognition strategy on prices — and the alpha concentrates in the short leg, which is hard to implement. Second, the 20bp cost cliff is the key number: this strategy dies at a cost level far below what single-name option spreads cost to trade.

### C2. The Autopilot "Claude Portfolio" — a human makes the decisions, and nothing is disclosed

**CLAIM:** The Autopilot Claude-managed portfolio has a human in the decision loop, does not disclose its decision logic, reports no risk-adjusted metrics, and has a track record too short to be informative.

**SOURCE:** explainX.ai, "Claude Portfolio: Up 19% vs S&P, But Who Trades?", August 2026 (practitioner/journalistic analysis). The operator's own site claudeportfolio.com/p/autopilot returned a client error and could not be retrieved.

What IS known: the setup is reportedly a single prompt — "Beat the S&P 500" — to a Claude Code agent running Opus 4.6. The operator states that *they* wrote the risk parameters (position-size limits, turnover ceiling, a required falsifiable written thesis), and explicitly says "Every pick inside those rails is mine" — a human makes the final trade decisions. Claude's role is research: about 15 positions plus a watchlist, with news synthesis, bull/bear cases and scenario work, roughly twice weekly. Reported +19.04% since 3 March 2026 vs +12.24% for the S&P 500.

What is NOT known: the full parameters and decision rules are unpublished; no data sources are named; the prompt beyond the one-line screenshot is not public; **there is no disclosure of any use of technical analysis, chart patterns or price-based signals** — the described inputs are all news and fundamental narrative.

Caveats the source itself raises: ~5-month track record, too short to separate skill from noise in a rising market; no Sharpe, max drawdown or volatility reported; self-reported with no independent audit; the operator is pseudonymous; the return is the sales pitch for a copy-trading product with $27m following it; the same organiser runs several other AI-branded portfolios, so survivorship/spotlight bias applies; Anthropic did not build or endorse it.

**EVIDENCE STRENGTH:** Weak as evidence of efficacy. Strong as evidence about *what is disclosed*, which was the question asked.

**IMPLICATION FOR THE APP:** This cannot serve as a design template, because the thing that is actually working (if anything is) is an undisclosed human. More pointedly for this strand: the most visible LLM-driven portfolio forms directional views from news and narrative theses, with no disclosed technical-analysis component at all.

### C3. Look-ahead contamination — real, measurable, and smaller than feared in frontier models

This is the finding in Part C that most cuts against a sceptical prior, so I am reporting it prominently.

**CLAIM:** Temporal leakage in LLM backtesting cannot be identified from backtest scores alone and requires an external reference, but when measured properly most frontier models showed no leakage jump at their own training cutoffs.

**SOURCE:** Zeyu Zhang and Bradly C. Stadie (Northwestern University), "Temporal Leakage in LLM Backtesting: Measurement, Validation, and Adjusted Scores", arXiv:2608.02985v1, August 2026.

Findings: the standard pre/post-cutoff check is uninformative — the authors prove inflation is only bounded, not point-identified, from passive scores. Measurement needs either a known-cutoff regression discontinuity or a matched clean-control difference-in-differences. Validated on planted leakage (contrast ~+0.063 Brier units at highest dose; boundary estimate +0.052 overstated per-question inflation of ~+0.024) and on pretraining re-analysis (Hubble: accuracy inflation up to ~+0.403 at highest benchmark duplication). Applied to frontier models: naive pre/post gaps of +0.044 to +0.061 were attributed to **recency, not leakage**; after matched adjustment no significantly positive estimate appeared for the primary target; one boundary signature was detected for GPT-5.5 (+0.061, CI [+0.023, +0.093]), which the authors call a footprint rather than proof. Experiments are on forecasting and coding benchmarks, **not financial backtests specifically**.

Guidance: prefer forward evaluation on post-cutoff outcomes; never treat a flat pre/post profile as proof of cleanliness; use placebo cutoffs and covariate balance; use a crowd benchmark as a difficulty anchor; report power floors alongside nulls.

**EVIDENCE STRENGTH:** Moderate-to-Strong methodologically; indirect for finance.

**IMPLICATION FOR THE APP:** Good news and a constraint. The good news is that contamination may be a smaller problem than the folk wisdom holds. The constraint is that the developer cannot prove an LLM backtest is clean by showing flat performance either side of the cutoff — that test has no power. The only cheap, sound option for a single-user app is **forward evaluation on dates after the model's cutoff**, which is leakage-free by construction. That has a direct consequence for the test design in the next section.

---

## VERDICT ON MULTI-TIMEFRAME CONFLUENCE

**Direct answer: the hypothesis is untested in its own terms, and every adjacent body of rigorous evidence points against it. I would not build the app around it. But the developer is right that the prior strand did not test this, and the honest verdict is "unsupported and probably redundant", not "refuted".**

The three components of the hypothesis do not fare equally, and this distinction matters more than the overall verdict:

- **Elliott wave should be dropped.** No inter-rater reliability study exists (B2, confirmed). Without reproducibility there is no construct to test. This is the weakest link by a wide margin.
- **Fibonacci levels should be dropped as a distinct signal.** Tsinaslanidis & Voukelatos (2021) found Fibonacci zones statistically indistinguishable from non-Fibonacci zones (B1). This is the control test, and it is a clean null.
- **Multi-timeframe structure is the one part with a defensible residue** — but in the form of scale *selection* (Stein), and at most a two-point barbell rather than a six-level ladder (Etienne et al.).

**Strongest evidence FOR, laid out fairly:**
1. Stein (2024, IJF) is real, peer-reviewed, out-of-sample, cost-robust, internationally replicated: frequency decomposition more than doubles out-of-sample R² in recessions (under 4% → over 8%) and is worth 100–150bp/year. Scale genuinely matters.
2. Etienne et al. find distant horizons correlate only 44–59%, so a widely-separated short/long pair does carry partly distinct information.
3. Bajgrowicz & Scaillet's own Table 4 shows positive out-of-sample Sharpes in every period for the FDR-selected portfolio, which sits awkwardly with their negative text.
4. Trend/regime filtering has a long respectable lineage (Moskowitz–Ooi–Pedersen 2012 time-series momentum) and reliably improves drawdowns.
5. The construct has genuinely never been tested in its practitioner form. Absence of evidence here is weak evidence of absence, because nobody looked.

**Strongest evidence AGAINST:**
1. Stein's mechanism is the opposite of confluence — one band predicts, the rest are noise to be *removed*. Confluence requires the discarded bands to carry information.
2. Etienne et al.: adjacent horizons correlate 81–90%, and *removing* the medium horizon improved Sharpe. Confluence scoring double-counts correlated evidence and manufactures false confidence.
3. Bajgrowicz & Scaillet: 7,846 rules, FDR-corrected — performance completely offset by low transaction costs, under 5% of rules survive one rebalancing, best rule unstable across periods and cost assumptions. The developer's 6×10 grid is this setting.
4. Hu et al. (2026): the closest built analogue — a frontier VLM reading daily+weekly candlesticks — scores 49–54% accuracy with several negative ICs, matched by XGBoost on plain numbers.
5. The practitioner literature is uniformly promotional and uniformly innocent of baselines. Four searches, zero academic hits.
6. Fibonacci null (B1) and Elliott-wave non-validation (B2) remove two of the three claimed evidence sources outright.

**What would need to be true for it to work:**
1. Timeframes would need to carry *non-redundant* information. Measurable: the signals must have pairwise correlation materially below Etienne et al.'s 81–90% adjacent figure. If correlation is above ~0.8, agreement is one observation counted twice and the confluence score is miscalibrated by construction.
2. The joint signal must beat the *best single timeframe*, not buy-and-hold and not a no-signal baseline. No study in this report clears that bar; most never attempt it.
3. The edge must survive options-level transaction costs. Lopez-Lira dies at 20bp; Bajgrowicz–Scaillet dies at 0–35bp. Single-name option spreads cost multiples of that. This is the hardest constraint and the one most often ignored.
4. The chosen timeframe set must be stable out of sample, contradicting A5.
5. Pattern detection must be reproducible — which Elliott wave currently is not, at all.

Condition 3 alone is close to disqualifying for an options application, independent of whether the signal has any predictive content.

---

## A CHEAP DECISIVE TEST

The literature cannot settle this, because the practitioner construct has not been tested. It can be settled cheaply, and the test should be run **before** building the confluence engine, not after.

**Test 1 — the redundancy test (run this first; it is nearly free and may end the question).**
No labels or forward returns needed. Implement the swing-detection and pattern logic once. Run it across all six timeframes on ~100 liquid underlyings over 5+ years. Emit a daily signed signal per (symbol, timeframe). Then compute the pairwise correlation matrix of those signals and its principal components.
- Decision rule: if the first principal component explains more than ~70% of variance, or adjacent-timeframe correlations exceed ~0.8 (the Etienne et al. range), the six timeframes are effectively one-to-two signals. Stop. Reduce to a short/long barbell and do not build confluence scoring.
- Cost: one implementation pass, no labelling, hours of compute. This is the highest-information-per-unit-effort experiment available.

**Test 2 — the incremental-value test (only if Test 1 passes).**
Pre-register the pattern set, swing parameters, timeframes, holding period and cost assumption **before looking at returns**. Then compare three nested models on identical samples: (a) best single timeframe, (b) two-timeframe barbell, (c) full six-timeframe confluence. The baseline is (a), not buy-and-hold.

*Sample size.* The realistic effect is small. To detect a lift in directional accuracy from 52% to 55% at 80% power, α=0.05 two-sided, requires roughly 1,700–1,800 independent observations per arm. Because confluence signals fire rarely by design, the binding constraint is *confluence events*, not calendar days. Budget for **at least 2,000 non-overlapping confluence events**, and apply Bonferroni or Benjamini–Hochberg across the full hypothesis grid actually examined — with 60 base hypotheses, an uncorrected p=0.01 is unremarkable. Use non-overlapping holding periods, or block-bootstrap standard errors if overlap is unavoidable; overlapping windows will badly overstate significance. Across ~100 liquid underlyings, 2,000 events is realistically 3–5 years of history.

*Costs.* Evaluate at realistic options spreads, and report the break-even cost level explicitly, as Bajgrowicz & Scaillet do. A strategy whose break-even is under ~50bp round-trip is not tradeable in single-name options. Report this number even if the signal looks good — it is usually the number that kills the strategy.

**Test 3 — the LLM component, if one is used.**
Forward evaluation only, on dates after the model's training cutoff (Zhang & Stadie: pre/post-cutoff comparison has no power to establish cleanliness). Benchmark against XGBoost on plain numerical features, which Hu et al. found competitive with every VLM tested. If the LLM does not beat gradient boosting on numbers, the chart-reading component is not earning its cost or latency.

**A note on honest expectations:** Test 1 will most likely fail, and that is a good outcome — it costs very little and saves building a confluence engine whose arithmetic is wrong.

---

## PATTERN DETECTION STATE OF THE ART

Little has genuinely improved since Lo, Mamaysky & Wang (2000). The 2020–2026 literature has added architectural complexity without adding methodological discipline.

- **CNNs on chart images:** no cost-aware trading simulation in the representative papers; splits frequently undescribed; reported accuracies implausibly high where splits are unclear (B3).
- **VLMs on candlesticks:** the best-designed recent benchmark (Hu et al. 2026) finds near-chance accuracy, negative IC for several frontier models, and XGBoost competitive. Notably, no multi-scale ablation even in a paper built around multi-scale inputs (B4).
- **Time-series foundation models:** small, sparse gains over a random walk; no trading simulation; the authors themselves decline to claim alpha (B5).
- **Fibonacci:** automated identification now exists (Tsinaslanidis & Voukelatos 2021) and the result is a null against non-Fibonacci controls (B1).
- **Elliott wave:** automated labellers exist commercially but none has been validated against anything, and no inter-rater or algorithm-agreement study exists (B2).

**The pattern across this subfield:** papers that report a trading simulation with costs report near-null results; papers that report high accuracy omit the trading simulation. I found no exception.

---

## LLM VIEW FORMATION

What is actually known about how these systems decide direction:

1. **The documented methodology is text-driven, not price-driven.** Lopez-Lira & Tang give the model a headline and a company name and nothing else — explicitly no price data. The output is a ternary good/bad/unknown mapped to +1/-1/0.
2. **It works pre-cost and dies post-cost.** Sharpe 3.28 pre-cost, surviving 5bp, unprofitable at 20bp. The alpha is concentrated in the short leg.
3. **Capability scales with model size.** GPT-1/GPT-2/BERT show negative Sharpes; the effect emerges only in larger instruction-following models. This is consistent with genuine comprehension rather than keyword matching, and is the strongest argument that something real is happening.
4. **It subsumes commercial sentiment.** RavenPack's score becomes insignificant when the LLM score is included.
5. **The most visible LLM portfolio is not autonomous and is not disclosed.** The Autopilot Claude Portfolio has a human making final picks by the operator's own statement, a ~5-month record, no risk-adjusted metrics, self-reported returns, and an undisclosed ruleset — attached to a copy-trading product with $27m following it. No technical-analysis component is disclosed.
6. **Chart reading specifically does not work yet.** Hu et al.: frontier VLMs on candlestick images are at coin-flip, matched by XGBoost on numbers.
7. **Contamination is real but may be modest in frontier models**, and crucially cannot be ruled out by the pre/post-cutoff test most practitioners use.

**Synthesis for the app:** every documented case of an LLM adding directional value does so by *reading text about events* — not by reading charts. If the developer wants an LLM component with evidential support, the supported design is news and filing interpretation, not chart interpretation. That is a meaningful redirection of the capstone rather than an abandonment of it.

---

## DISCONFIRMING EVIDENCE

Evidence cutting against my own conclusion, which is sceptical of multi-timeframe confluence:

1. **Scale genuinely matters, and this is well established.** Stein (2024, IJF) is strong peer-reviewed evidence that frequency decomposition adds real, cost-robust, internationally-replicated economic value. My reading — that it supports selection rather than confluence — is my interpretation of his mechanism, not his stated claim. A reasonable person could argue that if different frequency bands carry different information content, a system that *weights* them is a legitimate implementation of that insight, and "confluence" is a crude but not absurd version of weighting.
2. **Bajgrowicz & Scaillet's own table contradicts their text.** Table 4 shows positive out-of-sample Sharpes for the FDR portfolio in every single period (0.47, 0.01, 0.55, 0.31, 0.34, 0.74). I have leaned on this paper as the strongest evidence against, and its own data is more favourable to technical rules than its prose. I flag this rather than quietly using the convenient half.
3. **Distant horizons are substantially less correlated than adjacent ones** — 44% for 20d vs 500d. A two-point barbell has a real statistical basis. The redundancy finding condemns a six-level ladder, not the general idea that horizon matters.
4. **Etienne et al.'s effects are small and untested for significance.** Sharpe 0.74 → 0.77 is within noise for a 20-year backtest, there are no confidence intervals, the correlations are between sleeve *returns* rather than raw signals, and the paper's stated backtest start dates are internally inconsistent. I have used it as the central independence evidence and it is weaker than I would like.
5. **Absence of academic testing is partly a sociological fact, not a verdict.** Multi-timeframe confluence is discretionary, hard to formalise and unattractive to publish on. Academic silence reflects what is publishable as much as what is true. The developer's point that this was never tested is correct and fair.
6. **Contamination fears may be overstated.** Zhang & Stadie found no leakage jump for most frontier models at their own cutoffs, attributing naive pre/post gaps to recency. This cuts against reflexive dismissal of LLM backtests.
7. **The Fibonacci null has a retrieval caveat.** I could not confirm from the available record how the non-Fibonacci control zones were constructed, and the full text is paywalled. The highlights are unambiguous, but I am relying on the authors' own summary rather than the methods section.
8. **Trend filters do reliably improve drawdowns**, across many studies. If the developer's real goal is risk management rather than directional prediction, a higher-timeframe filter is defensible on grounds this report does not refute.

---

## OPEN QUESTIONS

1. How were the non-Fibonacci control zones constructed in Tsinaslanidis & Voukelatos (2021)? Randomly placed, or systematic non-Fibonacci ratios? This determines how strong the null is. Requires paywalled full text.
2. What is the actual pairwise correlation of *pattern-detection* signals (as opposed to moving-average trend sleeves) across nested timeframes? Nobody has published this. Test 1 would produce it, and it is the single most decisive missing number.
3. Does Stein's frequency-decomposition result survive at intraday-to-daily scales, or is it specific to 16–64-month cycles? His own data cannot answer this.
4. Would a VLM with fine-tuning rather than prompting exceed chance on candlesticks? Hu et al. explicitly flag this as a limitation of their design.
5. Is there any Elliott wave implementation with published agreement statistics between two independent labellers? I found none, but commercial vendors may hold unpublished internal data.
6. What are realistic round-trip costs for the specific option structures the app would recommend? This is the binding constraint and is knowable from the developer's own broker data — it should be measured before any signal work.
7. Does the Autopilot Claude Portfolio use any price-based input? Not disclosed; the operator's own site was unreachable.
8. Does Bajgrowicz & Scaillet's positive out-of-sample Sharpe in Table 4 reflect a real residual effect, or a reporting artefact? Worth resolving, as it is the main crack in the strongest negative result.

---

## TOP 10 SOURCES, RANKED

1. **Tsinaslanidis & Voukelatos (2021)** — "Automatic identification and evaluation of Fibonacci retracements: Empirical evidence from three equity markets", *Expert Systems with Applications* 391. DOI 10.1016/j.eswa.2021.115893. *The target retrieval, obtained. Fibonacci zones statistically indistinguishable from non-Fibonacci zones — the control test, cleanly null.*
2. **Bajgrowicz & Scaillet (2012)** — "Technical trading revisited: False discoveries, persistence tests, and transaction costs", *Journal of Financial Economics* 106(3), 473–491. *7,846 rules, FDR-corrected, costs eliminate performance, best rule unstable. The multiple-testing precedent for a 6×10 grid.*
3. **Stein (2024)** — "Forecasting the equity premium with frequency-decomposed technical indicators", *International Journal of Forecasting* 40(1), 6–28. DOI 10.1016/j.ijforecast.2022.12.001. *The strongest evidence that scale matters — and that the mechanism is selection, not confluence.*
4. **Hu, Xiao, Xu, Tang & Liu (2026)** — "Do VLMs Truly 'Read' Candlesticks? A Multi-Scale Benchmark for Visual Stock Price Forecasting", arXiv:2604.12659v1. *Closest built analogue to the app. Near-chance accuracy; XGBoost competitive; no multi-scale ablation.*
5. **Etienne, Ohana, Benhamou, Guez, Setrouk & Jacquot (2025)** — "Revisiting the Structure of Trend Premia: When Diversification Hides Redundancy", arXiv:2510.23150. *The independence question, quantified: adjacent horizons 81–90% correlated; removing one improves Sharpe.*
6. **Lopez-Lira & Tang (2023/2024)** — "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models", arXiv:2304.07619. *The reference LLM methodology: headlines only, no price data, dies at 20bp.*
7. **Zhang & Stadie (2026)** — "Temporal Leakage in LLM Backtesting: Measurement, Validation, and Adjusted Scores", arXiv:2608.02985v1. *Pre/post-cutoff tests have no power; forward evaluation is the only cheap clean option.*
8. **Lo, Mamaysky & Wang (2000)** — "Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation", *Journal of Finance* 55(4). *Still the methodological benchmark; nothing since has improved on it cost-aware.*
9. **Noguer i Alonso & Pereira Franklin (2026)** — "Pretrained Time-Series Foundation Models for Financial Return Forecasting", arXiv:2606.27100. *No off-the-shelf foundation model solves this; authors decline to claim alpha.*
10. **Duong et al. (2025)** — "Investigating Market Strength Prediction with CNNs on Candlestick Chart Images", arXiv:2501.12239. *Included as a worked example of the subfield's failure modes: no backtest, undescribed splits, internally inconsistent tables.*

**Labelled non-peer-reviewed sources used:** Quantpedia/Dujava (sponsored vendor blog, A7); explainX.ai (journalistic, C2); arXiv:2508.02356 (preprint, assessed and rejected, A6); Moreira granularity-paradox preprint (A8, non-financial).
