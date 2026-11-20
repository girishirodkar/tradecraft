# Strand 19 — Scheduled Macro and Geopolitical Events

**Date:** 12 November 2026
**Brief:** Does the earnings event-volatility decomposition transfer to scheduled macro and geopolitical events? Which events deserve a calendar? Is geopolitical risk an entry signal or a regime input?

**Headline:** The mechanism transfers. The *trade* does not — at the project's horizon. The decomposition is mechanically valid and now well-evidenced for FOMC, CPI and payrolls, and the direction of bias matches earnings (implied event variance exceeds realised). But the magnitude of a macro event's variance footprint at 42–90 DTE is roughly two orders of magnitude smaller than an earnings event's, and it fails the cost hurdle by a wide margin. Macro events belong in the project as **regime and calendar context**, not as a tradeable event-vol signal. Geopolitical risk is a **regime input only**, and even then the one direct out-of-sample test says it fails as a forecasting regressor.

---

## PART 1 — DOES THE DECOMPOSITION TRANSFER?

### CLAIM 1: The deterministic-event-jump framework can be calibrated to FOMC, CPI and payrolls from the option surface, and materially improves pricing fit — so the mechanism itself transfers.

- **SOURCE:** Tenghan Zhong (USC), "Non-Spanning Identification of Scheduled Event Risk in Option Pricing," arXiv:2606.12872v2 [q-fin.PR], 2026. https://arxiv.org/pdf/2606.12872 — **preprint, not peer-reviewed.**
- **EVIDENCE STRENGTH:** Moderate (method strong, venue unreviewed, sample short).
- **Detail:** Identifies the continuous no-event surface from expiries that *do not* span the event, then calibrates a deterministic-time jump from event-spanning quotes — the same logical structure as the project's two-maturity decomposition, but using non-spanning expiries as the control rather than a second spanning maturity. 101 events (39 CPI, 23 FOMC, 39 NFP), May 2022 – Aug 2025. Held-out SPX IV MAE falls 0.1080 → 0.0926 (mixture jump); median spread-normalised error 14.008 → 8.915. Gains concentrate in ATM straddles and 25-delta strangles, absent in risk reversals — i.e. it is a *variance* identification, not a directional one.
- **Fitted event jump standard deviations: CPI 0.91%, FOMC 0.81%, NFP 0.10%.**
- **IMPLICATION FOR THE BUILD:** The project's existing decomposition code can be pointed at macro dates with no new mathematics. Use non-spanning expiries as the control leg where available (daily/weekly SPX expiries make this possible for the index in a way it is not for single names). **Critically: these fitted jump sizes are the number that kills the trade — see Claim 4.**

### CLAIM 2: The implied event move extracted from 0DTE options is genuinely informative about the realised FOMC-window move — R² of 78–85% — but only for windows that actually contain the announcement.

- **SOURCE:** Yuhan Song (HEC Montréal), "Pre-FOMC Uncertainty Accumulation: Evidence from 0DTE Options," September 2026. https://afajof.org/management/viewp.php?n=260400 — **working paper, AFA submission, not yet peer-reviewed.**
- **EVIDENCE STRENGTH:** Moderate–Strong (high-frequency identification, large R², top-venue submission, unreviewed).
- **Detail:** Implied event uncertainty rises 0.60% (10:00 ET) → 0.78% (pre-14:00), collapses by more than half at the statement, rebuilds into the press conference, falls again. ~71% of priced event variance resolves at the statement, 29% at the press conference. Predictive regressions: R² ≈ 78–85% for announcement/press-conference windows; **essentially zero forecasting power for pre-14:00 windows.** Implied skewness averages −0.53, is stable into the release, and has no return predictability at almost any horizon — it is insurance demand, not a directional forecast.
- **IMPLICATION FOR THE BUILD:** This is the direct analogue of the earnings result (implied jump vol R² ≈ 28.5% against the realised announcement move) and it is *stronger* for FOMC — because the event is isolated in a 0DTE contract rather than diluted across a 40-day expiry. It confirms the implied event move is a legitimate *display* quantity. It also independently reconfirms the project's established finding that direction is worthless: skew carries no directional information even here.

### CLAIM 3: The event-day variance risk premium is positive and significant for the S&P 500 on both FOMC and employment-report days — implied event variance systematically exceeds realised, the same direction as earnings.

- **SOURCE:** Jonathan H. Wright (Johns Hopkins), "Event-Day Options," *Journal of Time Series Analysis*, 2025, DOI 10.1111/jtsa.12819; NBER WP 28306 (Dec 2020). https://www.nber.org/system/files/working_papers/w28306/w28306.pdf — **peer-reviewed.**
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, careful recursive out-of-sample construction, but modest event counts).
- **Detail:** Uses CME weekly options expiring on the event day on Treasury futures and S&P E-mini. Event-day VRP coefficients (γ on RV−IV regressions): **S&P 500 FOMC 0.248\*\*\*, S&P 500 employment report 0.204\*\*.** Treasuries: FOMC 5y 0.019 (n.s.), 10y 0.031\*\*, 30y 0.116\*\*\*; employment 5y 0.028\*\*\*, 10y 0.077\*\*\*, 30y 0.177\*\*\*. About half the FOMC implied-variance increase for 5y/10y Treasuries is risk premium, most of it for 30y. PIT tests reject at 5% for all four series on FOMC days; realised Treasury outcomes on FOMC days never landed in the top or bottom decile of the options-implied distribution — **the implied event distributions are too wide.** No R² reported; no option-return or P&L analysis. Samples: FOMC Jun 2017–Aug 2020; employment Jan 2011–Aug 2020.
- **IMPLICATION FOR THE BUILD:** This is the single best peer-reviewed support for transfer. The *sign* of the bias matches earnings (implied rich). The too-wide-distribution result is the macro analogue of the earnings ~7–11% relative bias high. But note the sample ends Aug 2020 and excludes the post-2020 regime — and Claim 6 shows the bias may not have survived.

### CLAIM 4 (DERIVED — the decisive build finding): A scheduled macro event's share of total variance in a 42–90 DTE expiry is ~0.7–0.9%, versus ~57% for an earnings day in a 40-day expiry. The decomposition is ~60–80× less informative at the project's horizon.

- **SOURCE:** My own arithmetic from Zhong (2026) fitted jump sizes. Not a published result — flagged as derived.
- **EVIDENCE STRENGTH:** Moderate (arithmetic is simple; inputs are from an unreviewed preprint).
- **Calculation:** FOMC jump σ = 0.81% → event variance 6.56e-5. A 60-day expiry at 20% annualised: total variance = 0.04 × 60/252 = 9.52e-3. **Event share = 0.69%.** CPI (0.91%): **0.87%.** NFP (0.10%): ~0.01%. A typical 60-day window containing 2 CPI prints, 1 FOMC and 3 payrolls reports: **combined ≈ 2.4% of total variance.**
- **Corroboration:** Adamski & Ślepaczuk (2026) find the FOMC IV elevation is strongest at 0 DTE, much weaker and later at 2 DTE, and **almost absent at 10 DTE.** Their ML impulse response gives ~20% IV shock for ATM 0DTE calls, shrinking with maturity.
- **IMPLICATION FOR THE BUILD:** **This is the answer to the index-vs-single-name question and to whether the macro calendar needs to feed single-name mode.** Even if implied macro event vol carried the full earnings-scale ~10% relative bias, the extractable edge is 10% of 0.7% ≈ **0.07% of straddle value** — against a 2% index cost hurdle at 42–48 DTE, that is ~30× short. Macro events do not clear the hurdle at 42–90 DTE in either index or single-name mode. For a single name, a macro event inside the expiry window is **second-order to third-order** next to the name's own earnings (0.9% vs 57% of variance). **Do not feed the macro calendar into single-name event-vol modelling. Display it as context only.**

### CLAIM 5: At 0DTE — the only horizon where macro event variance dominates — the evidence says release-day options are roughly *fairly* priced, not rich.

- **SOURCE:** "options-event-risk" (unaifmm), open-source project, SPY/SPX options around CPI, payrolls and FOMC, May 2022 – Nov 2026. https://github.com/unaifmm/options-event-risk — **practitioner / unreviewed, self-described hypothesis-generating.**
- **EVIDENCE STRENGTH:** Weak (n ≈ 35–51 per event type in the long sample, 9–11 with real option prices; VIX1D proxy with a fitted 0.94 bridge factor; cost scenarios not observed quotes; one split chosen after seeing the data, which the author flags).
- **Detail:** Realised/implied move ratios — **CPI 0.94 [0.71, 1.21]; payrolls 1.11 [0.89, 1.38]; FOMC 0.94 [0.71, 1.20]; normal days 0.89 [0.84, 0.94].** Only the normal-day ratio excludes 1. Release days charge ~27% more than normal days but the index moves ~43% more; rank test p = 0.19. Seller Sharpe: every day 0.23; **skip release days 0.52; release days only −0.49.** Real-straddle per-trade seller returns after retail costs: CPI +0.21%, FOMC +0.08%, payrolls −0.14%, normal +0.04% of index — most CIs include zero. One day (9 Apr 2025) cost a seller ~5.6% of index.
- **IMPLICATION FOR THE BUILD:** The short-vol premium the project could actually harvest at the index level lives on **ordinary days, not release days.** The release-days-only Sharpe of −0.49 is the practitioner mirror of the project's established "buying premium into a catalyst loses" finding — except here it says *selling* into a macro catalyst also fails, because the extra premium charged is roughly matched by the extra move. If anything this argues for **excluding macro release days** from short-premium entries rather than targeting them. Treat as weak, directionally useful, and tension-flagged against Wright (Claim 3).

### CLAIM 6: FOMC-day index straddle returns are genuinely contested across samples — one study finds them strongly positive, another strongly negative.

- **SOURCES:**
  - Garrett T. DeSimone, *Essays on Equity Option Behavior Surrounding Macroeconomic Announcements*, PhD dissertation, University of Delaware, 2017. https://udspace.udel.edu/items/a7715f6b-fc64-49e8-90b3-db9e4975df84 — **dissertation, examined but not journal peer-reviewed.**
  - Carl Windmar, "Risk Premium around Macroeconomic Announcements: Evidence from Delta-Neutral Straddles," master's thesis, Lund University, June 2025. http://lup.lub.lu.se/student-papers/record/9197108/file/9197117.pdf — **master's thesis, weakest tier.**
- **EVIDENCE STRENGTH:** Weak (both non-peer-reviewed; opposite signs on FOMC).
- **Detail:** DeSimone: announcement days account for **>77% of total negative annualised S&P straddle returns**; CPI, NFP, industrial production days average **−1.3% to −2.5%** vs **−0.1%** on non-announcement days; but **FOMC days show strongly *positive* straddle returns**, which he attributes to expected volatility declines from policy backstop. Also: on high-uncertainty announcement days a steeper IV curve predicts negative next-day index returns. Windmar (Jan 2024 – Apr 2025, **no transaction costs**): straddle *buyers* lose FOMC −5.6% [−1,1] (t≈−4.0), −12.9% [−3,3] (t≈−7.2); CPI −5.2% [−1,1] (t≈−5.1); **payrolls mixed and mostly insignificant** (+2.1% [−1,1], t≈1.3). He notes costs would materially worsen option strategies, citing Goyal & Saretto's 21.9% → 8.6% post-cost collapse.
- **IMPLICATION FOR THE BUILD:** Do not hard-code a directional view on FOMC vol richness. The most defensible reading across Wright (rich), DeSimone (FOMC cheap, CPI/NFP rich), Windmar (both rich, gross of costs) and the GitHub project (roughly fair) is: **the macro event premium is small, regime-dependent, and not reliably signed at retail cost levels.** DeSimone's CPI/NFP concentration result and the GitHub project's release-day Sharpe of −0.49 point in opposite directions on the same question, which is itself the finding.

---

## PART 2 — FOMC SPECIFICALLY

### CLAIM 7: The pre-FOMC announcement drift was large in the original sample, much weaker after 2011, and a structural break test places its death at March 2016.

- **SOURCES:**
  - Lucca & Moench, "The Pre-FOMC Announcement Drift," FRBNY Staff Report 512; published *Journal of Finance* 70(1), 2015. https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf — **peer-reviewed.**
  - Hu, Pan, Wang & Zhu, "Premium for Heightened Uncertainty: Solving the FOMC Puzzle," NBER WP 25817, 2019 (rev. Jul 2019). https://www.nber.org/system/files/working_papers/w25817/revisions/w25817.rev1.pdf — **working paper.** (Later published, *Journal of Financial Economics*.)
  - Song (2026), as above.
  - Kurov et al. / "The disappearing pre-FOMC announcement drift," *Finance Research Letters*, 2021, DOI via https://www.sciencedirect.com/science/article/abs/pii/S1544612320315956 — **peer-reviewed** (abstract not retrievable at fetch time; cited on title and venue only).
- **EVIDENCE STRENGTH:** Strong on the decline; Moderate on the exact break date.
- **Detail:** Hu et al.: pre-announcement window (prior 4pm close to 5 min before announcement) averages **+27.1 bp (t = 5.95)** vs **1.1 bp** on non-FOMC days; **post-2011 it is 8.9 bp and not significant.** Realised volatility on FOMC days is about normal. VIX builds ~0.60% (t = 2.60) over the six business days before FOMC, with ~no build-up on non-FOMC days; VIX falls on FOMC day, about half (−0.27%) *before* the announcement; it falls further after, but the average post-announcement return is ~zero. Song: 2016–2023 cumulative pre-announcement returns are insignificant across most windows; the only significant piece of the 24-hour window (~0.19%) sits in the **overnight gap, not the trading session**; structural break at the **March 2016 meeting — the first after Cboe listed Wednesday SPX expirations.** Knox et al. (below): over 1936–2024 FOMC days average ~12 bp excess return vs ~34 bp in the Lucca–Moench window, suggesting the original estimate partly captured unexpectedly good news.
- **IMPLICATION FOR THE BUILD:** **Do not build anything on the pre-FOMC drift.** It is dead, the surviving fragment is in the overnight gap (unreachable for a retail single-user tool with daily workflow), and 0.19% is far below the cost hurdle. The *volatility* pattern (VIX builds into FOMC, falls on the day, half of it pre-announcement) is robust and is legitimate regime context for a display.

### CLAIM 8: Option-implied FOMC uncertainty is real and FOMC is the most frequently priced event in the calendar — but option-based estimates of the FOMC premium are far smaller than realised-return studies imply.

- **SOURCE:** Ben Knox, Juan M. Londono, Mehrdad Samadi & Annette Vissing-Jorgensen, "Equity Premium Events," Federal Reserve Board working draft, March 2025. https://www.business.rutgers.edu/sites/default/files/documents/mehrdad-samadi.pdf — **central-bank working paper, not peer-reviewed.**
- **EVIDENCE STRENGTH:** Moderate (strong methodology and data, unreviewed).
- **Detail:** Builds forward per-day equity premium estimates from daily-expiry SPX options (Oct 2016 – Dec 2023) using forward SVIX, Chabi-Yo–Loudis LBR and Tetlock IEP, with median quantile regression on the forward term structure to define "abnormal" premia. FOMC is the most frequently priced event type — **13 meetings with significant abnormal forward premia; SVIX coefficient ~0.65 bp per forward period (t = 5.73); average FOMC forward premium 7.93 bp per period on IEP.** **FOMC, CPI and NFP together account for only ~23% of total expected daily returns.**
- **IMPLICATION FOR THE BUILD:** Confirms FOMC has the largest and most consistent option footprint of any scheduled macro event, which justifies putting it first on the calendar. The 23% figure is a second independent indication that scheduled macro events are a minority of priced risk — consistent with Claim 4.

### CLAIM 9: Option-implied *tail* measures around FOMC carry more return information than implied volatility does, but at R² ~12–13% over roughly a week.

- **SOURCE:** Kris Jacobs, Sai Ke & Xuhui (Nick) Pan, "Tail Risk Around FOMC Announcements," *Journal of Financial and Quantitative Analysis* 61(2), March 2026, 640–672. https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/tail-risk-around-fomc-announcements/567F3B47420074A6521C31755E7AE587 — **peer-reviewed.**
- **EVIDENCE STRENGTH:** Strong (top-tier journal, 207 meetings, 1996–2021).
- **Detail:** Bakshi–Kapadia–Madan model-free implied vol, skewness and kurtosis from OTM SPX at fixed 7-day maturity; "abnormal" = value 2 days pre-announcement minus trailing t−15..t−8 median. **Abnormal volatility predicts returns only weakly (0.078\*\* days 1–2; 0.122\*\* days 1–4; adj. R² ~2–4%) and loses significance once tail risk is controlled.** Abnormal skewness: negative relation, adj. R² up to ~13%. Abnormal kurtosis: positive relation (3.703\*\*\* days 1–4), adj. R² ~12%. Predictability lasts ~one week, stronger after expansionary shocks. Pre-FOMC abnormal volatility 0.423 vs full-sample 0.179 (~2.4×). (The paper reports skew/kurtosis percentage differences inconsistently between intro and body — 86%/81% and 52.5%/50%.)
- **IMPLICATION FOR THE BUILD:** Confirms the IV *level* around FOMC has little return content — reinforcing the project's "direction is near-worthless" conclusion. The tail-moment result is a one-week-horizon directional signal, which is outside the project's 42–90 DTE frame and would not survive the cost hurdle at retail. **Use as evidence against adding FOMC directional features, not for.**

---

## PART 3 — CPI, PAYROLLS AND OTHER RELEASES

### CLAIM 10: CPI and FOMC have the largest option-implied footprints among scheduled macro releases; GDP has essentially none; elections descriptively exceed all economic releases.

- **SOURCE:** Juan M. Londono & Mehrdad Samadi, "Which Days Matter for Global Equity Markets? Using Options to Price Events in the Global Calendar," FEDS Notes, Federal Reserve Board, 3 October 2025, DOI 10.17016/2380-7172.3908. https://www.federalreserve.gov/econres/notes/feds-notes/which-days-matter-for-global-equity-markets-using-options-to-price-events-in-the-global-calendar-20251003.html — **central-bank research note, not peer-reviewed.**
- **EVIDENCE STRENGTH:** Moderate–Strong (clean forward-premium identification on daily expiries; short sample Sep 2023 – Jul 2025; unreviewed).
- **Detail:** Forward premiums from differences in Gao–Martin LVIX between event-spanning and just-before-expiring options, averaged over the week before each event, regressed on event-type indicators with trade-date fixed effects. **US equity forward premium (annualised bp, t-stat): US employment 53 (8.8); US policy rate/FOMC 49 (4.7); US CPI 45 (10.4); euro-area CPI 18 (2.8); euro-area policy rate 5 (1.5, n.s.); US GDP 4 (0.5, n.s.); euro-area employment −1 (n.s.); euro-area GDP −11 (n.s.).** Authors conclude CPI and FOMC are the most relevant. **Elections are not in the regression but descriptively carry the largest event premiums, exceeding all economic releases.** Example calendar (5 Jul 2024): French runoff at the 99th percentile for Stoxx 50; US CPI at the 93rd percentile for SPX. Tariff-announcement days (Apr–May 2025) excluded as option-price noise. **The note does not compare implied pricing with realised moves and explicitly flags ex-post reaction as a limitation.**
- **IMPLICATION FOR THE BUILD:** This is the ranking backbone for the event calendar. It settles which events have an extractable footprint at all: **CPI, FOMC, payrolls — yes. GDP, Treasury auctions, most second-tier data — no.** It also establishes that elections are the largest single scheduled event by implied footprint, which is the one place where a macro event may approach earnings-scale variance share.

### CLAIM 11: The equity option market's response to CPI surprises changed materially after 2020 and became much weaker and less consistent.

- **SOURCE:** Ali Nejadmalayeri & William D. Campbell, "Inflation and Options: Volume 1, Through the Lens of SPX Options," Cboe research publication (Cboe 2023 MSCI Inflation Research Grant), data through Aug 2023. https://cdn.cboe.com/resources/education/research_publications/spxinflation.pdf — **exchange/vendor research, not peer-reviewed.**
- **EVIDENCE STRENGTH:** Weak–Moderate (good data, vendor venue, internally inconsistent sign reporting in the post-COVID section).
- **Detail:** Pre-COVID (2012–2019, median CPI <2%): per percentage point of positive CPI surprise, two-day call return ≈ **+1.48%**, put ≈ **−1.59%**; negative surprises: calls ≈ −1.23%, puts ≈ +1.43%. Call IVOL fell ~2.25% per pp positive surprise, rose ~1.95% on negative. Post-COVID (2020–2023, median CPI ~5%): reactions "markedly smaller," signs reversed for the same surprise direction, IV effects small and mostly insignificant. Pre-COVID, call volume dropped into larger-than-expected releases; bid-ask spreads narrowed into the release day and widened after.
- **IMPLICATION FOR THE BUILD:** The answer to "has the market's attention to CPI changed post-2021 in a way that shows up in the surface" is **yes, and it got weaker and less stable, not stronger** — despite CPI being more salient in the news. Any macro-event calibration must be estimated on a recent rolling window, not a long history. The spread-widening-after-release detail is a concrete cost warning: exiting right after a macro print is the worst moment for execution.

### CLAIM 12: No credible evidence was found that Treasury auctions have an extractable equity-option implied-volatility footprint.

- **SOURCE:** Searched specifically; found only practitioner auction previews (Newsquawk, VTMarkets) and CME educational material on Treasury options volatility (https://www.cmegroup.com/education/featured-reports/the-treasury-options-volatility-force-awakens.html — **vendor/educational**). Auctions do not appear in Londono & Samadi's significant event set, and US GDP — a far more prominent release — is already insignificant at 4 bp.
- **EVIDENCE STRENGTH:** No credible evidence found.
- **IMPLICATION FOR THE BUILD:** **Do not build a Treasury auction calendar.** If auctions matter they matter in rates volatility (where Wright does find a 30y FOMC/employment footprint), not in the equity surface the project trades.

### CLAIM 13: OPEC meetings have a weak and inconsistent implied-volatility footprint at 30-day maturity, and the largest oil-vol episodes were not near meetings.

- **SOURCE:** Brett Friedman / OptionMetrics, "Crude Oil and Trading OPEC," 16 Oct 2025 (rev. 30 Oct 2025). https://optionmetrics.com/blog/crude-oil-and-trading-opec/ — **vendor research.** Background: Horan, Peterson & Mahar, "Implied Volatility of Oil Futures Options Surrounding OPEC Meetings," *The Energy Journal* 25(3), 2004, 103–125. https://ideas.repec.org/a/sae/enejou/v25y2004i3p103-125.html — **peer-reviewed but 20+ years old.**
- **EVIDENCE STRENGTH:** Weak.
- **Detail:** OptionMetrics covers 57 scheduled and extraordinary OPEC meetings since Jan 2005 using WTI 30-day continuous futures and 30-day IV over 1/2/5/10-day windows. **IV declines on average into and around meetings, only slightly** — no run-up-and-collapse pattern at 30-day maturity. Average changes are small though larger than normal periods; min/max ranges are wide. **The largest IV swings (March–April 2020) did not occur near OPEC meetings.** No implied-vs-realised comparison.
- **IMPLICATION FOR THE BUILD:** **OPEC does not clear the bar for a calibrated event.** The project cannot even fit a reliable jump size at the 30-day-plus maturities it trades. Energy-sector sensitivity to OPEC is real in the underlying but is not an option-surface event the project can decompose. At most: flag OPEC dates as context when the user is looking at an energy name, with no implied-move number attached.

---

## PART 4 — ELECTIONS

### CLAIM 14: Options spanning elections and political summits are systematically more expensive than neighbouring non-spanning options, and the event-spanning variance risk premium is positive and larger than controls.

- **SOURCE:** Bryan Kelly, Ľuboš Pástor & Pietro Veronesi, "The Price of Political Uncertainty: Theory and Evidence from the Option Market," *Journal of Finance* 71(5), 2016, 2417–2480; NBER WP 19812 (2014, rev. 2015). https://www.nber.org/system/files/working_papers/w19812/w19812.pdf — **peer-reviewed, top-tier.**
- **EVIDENCE STRENGTH:** Strong (top journal, 20 countries, 271 events: 64 national elections + 216 summit observations; SPX back to 1990).
- **Detail:** Compares ATM options whose lives span the event with the average of two neighbouring non-spanning expiries (IVD). **Spanning an event raises ATM put prices ~5.1% on average (mean IVD 1.43 vol points on a 27.8% base, t = 4.43).** One-month puts 5% OTM cost **9.6%** more, 10% OTM **16.0%** more. **Mean variance-risk-premium difference 0.0107 (t = 2.61); VRP is 0.0465 for event-spanning options vs 0.0358 for controls** — i.e. event-spanning options are richer relative to realised than non-event options. Premia ~8% in weak economic conditions vs ~1% in strong. Higher election-poll uncertainty raises IVD and VRPD; the IV-slope result is not significant. Political uncertainty spills across countries, mainly in weak conditions. **The design deliberately sidesteps the term structure** (treatment and controls share maturities) and **does not directly test implied-vs-realised event-move bias or report option returns.**
- **IMPLICATION FOR THE BUILD:** This is the strongest peer-reviewed transfer evidence for *political* events, and the direction again matches earnings: event-spanning options are rich relative to realised. The 5.1% ATM / 16% deep-OTM gradient tells the project where the richness concentrates — **in the wings, not ATM** — which is a reason to prefer defined-risk short-wing structures over ATM straddles if ever acting on an election. The condition-dependence (8% weak vs 1% strong) is a usable regime modifier. **But: no option-return test, so the 5.1% is a price level, not a demonstrated edge, and the project's cost hurdle has not been applied to it by any author.**

### CLAIM 15: The 2026 midterms produced the classic pattern — a VIX term-structure bump priced in advance, a sharp post-event volatility collapse — immediately followed by a far larger *unscheduled* shock that dwarfed the election move.

- **SOURCES:** Bloomberg, "Options Are Pricing in Muted Moves for US Stocks on Midterm Vote," 28 Sep 2026 (https://www.bloomberg.com/news/articles/2026-09-28/options-are-pricing-in-muted-moves-for-us-stocks-on-midterm-vote); "VIX Curve 'Bump' Shows Stock-Market Anxiety Growing By Midterms," FA-Mag, 2026 (https://www.fa-mag.com/news/vix-curve--bump--shows-stock-market-anxiety-growing-by-midterms-88221.html); CNN, "Dow has best post-midterm elections day in 44 years," 4 Nov 2026 (https://www.cnn.com/2026/11/04/investing/us-markets-midterm-elections); Yahoo Finance, 5–6 Nov 2026 (https://finance.yahoo.com/markets/article/stocks-soared-on-the-democratic-sweep-less-than-24-hours-later-the-ai-trade-cracked-183312401.html) — **all financial press, not research.**
- **EVIDENCE STRENGTH:** Weak (press reporting; single event; no implied-vs-realised measurement).
- **Detail:** VIX futures rose from ~17.4 (September) to ~19.7 (November), a visible curve bump around the election — i.e. the term-structure kink the project would use for extraction was clearly present and observable weeks ahead. **3 Nov (election day):** futures slipped ~1% overnight. **4 Nov:** Democrats took both chambers; Dow +1,500+, S&P ~+2%, Nasdaq ~+1.4%, oil sharply lower, VIX dropped sharply as election uncertainty resolved. **5 Nov:** Dow −1,800+, **S&P −4.4%, Nasdaq −5.5%**, VIX spiked as much as **70%** — a move Cboe data puts at only eight occurrences since 1991 — driven by an AI/semis unwind and data-centre construction pauses (Goldman: governors covering ~45% of planned US data-centre capacity pledged to halt or pause). S&P had its worst week since June.
- **IMPLICATION FOR THE BUILD:** Two concrete lessons. (1) The election term-structure kink is **genuinely extractable and visible well in advance** — this is the one macro event where the project's two-maturity decomposition has enough signal-to-noise at a tradeable maturity. (2) The 4–5 November sequence is the perfect object lesson for why post-event short-vol into a *resolved* macro catalyst is dangerous: the event resolved benignly, vol collapsed, and an unrelated unscheduled shock then delivered a −4.4% day and a 70% VIX spike within 24 hours. **A "sell vol after the macro event resolves" rule — the macro analogue of the project's one positive single-name signal — would have been maximally short vol at exactly the wrong moment.** This belongs in the build as a hard warning, and it argues for defined-risk structures only.

---

## PART 5 — GEOPOLITICAL RISK

### CLAIM 16: Geopolitical risk shocks have large, persistent, measurable ex-post effects on equities, volatility and credit — and the IMF reports anticipation effects before conflicts.

- **SOURCES:** IMF, *Global Financial Stability Report*, April 2025, Chapter 2 Online Annex ("Geopolitical Risks: Implications for Asset Prices and Financial Stability"). https://www.imf.org/-/media/files/publications/gfsr/2025/april/english/ch2annex.pdf — **institutional research, internally reviewed, not peer-reviewed.** Underlying index: Dario Caldara & Matteo Iacoviello, "Measuring Geopolitical Risk," Fed Board IFDP 1222 (2018); published *American Economic Review* 112(4), 2022. https://www.federalreserve.gov/econres/ifdp/files/ifdp1222.pdf — **peer-reviewed, top-tier.**
- **EVIDENCE STRENGTH:** Strong on ex-post magnitudes; Moderate on anticipation.
- **Detail:** Firm level: a major home-country GPR event lowers monthly stock returns ~**0.7 pp** local currency, ~**1 pp** in excess USD terms (sample mean monthly excess return ~0.6%). Aggregate VAR: average country-specific GPR shock response peaks ~**−0.3%**; large shocks ~**−2%**; cited literature spans 0 to −6%. Home-country involvement in international military conflict: **>−4.5 pp** for EMDE firms, **not statistically significant for advanced-economy firms.** Trade-partner conflict at 10% trade weight: −0.4 pp (AE), −0.7 pp (EMDE). Revenue exposure (2σ): −0.2 pp; subsidiary exposure −0.5 pp. Russia/Ukraine: EMDE firms −1.1 pp cumulative over 7 days vs AEs; emerging Europe ~−9 pp. Sovereign CDS +16–27% after major domestic events (~44 bp AE, ~182 bp EME). **Option-implied volatility spikes after GPR shocks** (no magnitude given in the annex). Persistence: EME stock impact lasts ≥6 months; oil falls ~1% cumulatively, peaking months later. **Anticipation: AE firms' returns fell ~5 pp on average in the month before their country's military conflict; the GPR factor generally predicts one-month-ahead excess market returns.**
- **IMPLICATION FOR THE BUILD:** The effects are real and large enough to matter for sizing. But note what is actually actionable: the significant equity effects are concentrated in **emerging markets and in firms with direct exposure**, and the military-conflict effect is **not significant for advanced-economy firms** — which is where a US retail account lives. For a US-market tool, the usable content is narrower than the headline magnitudes suggest.

### CLAIM 17 (decisive on geopolitics): The Caldara–Iacoviello GPR index does **not** improve out-of-sample forecast accuracy when used as a regressor — but it does help when used as a *regime-monitoring* variable.

- **SOURCE:** Nima Nonejad, "An interesting finding about the ability of geopolitical risk to forecast aggregate equity return volatility out-of-sample," *Finance Research Letters* 47 (June 2022). https://www.sciencedirect.com/science/article/abs/pii/S154461232200037X — **peer-reviewed.**
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, directly out-of-sample, directly on the project's question).
- **Detail:** One-month-lagged log GPR **does not improve out-of-sample point forecast accuracy relative to the benchmark.** Combining GPR with economic variables also fails. **But** when GPR is used as the monitoring variable in the Zhu–Timmermann (2021) dynamic forecast-selection framework, it generates MSE gains — best with the dividend-yield model, **~3% at one month, rising to ~10% at longer horizons.**
- **IMPLICATION FOR THE BUILD:** This is the single cleanest answer to the brief's geopolitical question, and it says exactly what the brief suspected: **GPR is a regime switch, not a predictor.** Do not add GPR as a term in the volatility forecast — that is the failure mode the project already measured (macro-augmented GARCH-MIDAS 39% worse). Use it, if at all, to *select between or modulate* existing models and to gate position sizing. The 3–10% MSE gain as a monitoring variable is real but modest, and it is a forecast-accuracy gain, not a P&L.

### CLAIM 18: Unscheduled geopolitical shocks are not timeable, and the 2026 post-midterm episode is a live demonstration that the dominant volatility event in a window can be entirely absent from any calendar.

- **SOURCE:** Synthesis of Claim 15 (Nov 2026 press), Claim 16 (IMF) and Claim 17 (Nonejad).
- **EVIDENCE STRENGTH:** Moderate (reasoning from established findings plus one vivid instance).
- **IMPLICATION FOR THE BUILD:** The largest single-day volatility event of the project's recent window (5 Nov 2026, S&P −4.4%, VIX +70%) was not on any event calendar. Any event-driven mode that implicitly assumes calendared events dominate the variance will be miscalibrated. **Reserve variance for the uncalendared.** Concretely: never let an event-vol decomposition convince the position that the non-event residual is small.

---

## PART 6 — MACRO IN THE VOLATILITY FORECAST

### CLAIM 19: Kitchen-sink macro augmentation of long-horizon volatility forecasts is 19–39% worse out-of-sample; only a handful of variables survive selection, and the best single one is housing starts.

- **SOURCE:** Yue Fang, Tae-Hwy Lee & Wenjun Su, "Predicting the Long-term Stock Market Volatility: A GARCH-MIDAS Model with Variable Selection," *Journal of Empirical Finance* (accepted 2018/2019). https://faculty.ucr.edu/~taelee/paper/Fang%20Lee%20Su%20JAE%2020180925.pdf — **peer-reviewed.**
- **EVIDENCE STRENGTH:** Strong (peer-reviewed; directly replicates and explains the project's prior 39% finding).
- **Detail:** Adaptive-Lasso with GIC-selected λ = 13.0 retains **4 of 20** candidates: **unemployment level (θ = −16.34, 5%), housing starts (−20.38, 1%), PPI (−17.69, 1%), default spread (+0.57, 1%).** Real GDP and industrial production are dropped. Out-of-sample at 1–4 quarter horizons: the selected model beats most single-variable rivals (MSFE ratios >1, negative Giacomini-White signs against it). **Housing starts is the one variable that beats the selected benchmark at every horizon: MSFE ratios 0.980, 0.975, 0.967, 0.955.** CPI helps at 2 quarters, consumer sentiment at 4. **Kitchen sink (all variables, no selection): MSFE ratios 1.39, 1.32, 1.21, 1.19 — i.e. 19–39% worse — with negative GW statistics at every horizon.**
- **IMPLICATION FOR THE BUILD:** This is the source of the project's 39% figure and it vindicates the sceptical prior. **What survives, and is worth testing as a single additive term at 42–90 DTE: the default/credit spread and housing starts.** The credit-spread survival is notable because it is the one variable in the brief's candidate list (VIX term structure, MOVE, credit spreads, GPR) with peer-reviewed out-of-sample support at a horizon overlapping the project's. Caveat: the horizons are 1–4 quarters (≈63–252 trading days), so only the 1-quarter result straddles the project's 42–90 day window. Add **at most one** variable, test it against the existing two-component model with a Diebold-Mariano or Giacomini-White test, and keep it only if it wins.

### CLAIM 20: No credible evidence was found that the MOVE index improves equity volatility forecasts at 42–90 days beyond price history.

- **SOURCE:** Searched; no peer-reviewed study found testing MOVE as an incremental equity-RV predictor at this horizon. Adjacent evidence: Johnson, "Risk Premia and the VIX Term Structure," *JFQA* 2017 (https://www.travislakejohnson.com/pdfs/Johnson%20VIXTS%202017%20(JFQA).pdf) — **peer-reviewed** — concerns the VIX term structure as a *return*-premium state variable, not as an incremental RV forecast input.
- **EVIDENCE STRENGTH:** No credible evidence found.
- **IMPLICATION FOR THE BUILD:** Do not add MOVE. Rates volatility is where Wright's Treasury event footprint lives; there is no demonstrated equity-forecast transfer at the project's horizon.

### CLAIM 21: The implied volatility surface itself is forecastable around FOMC, and an FOMC date dummy adds small but real accuracy — concentrated on announcement days.

- **SOURCE:** Łukasz Adamski & Robert Ślepaczuk (University of Warsaw), "When the Fed Speaks: Dynamics and Forecasts of the Volatility Surface," arXiv:2608.10693v1 [q-fin.ST], August 2026. https://arxiv.org/pdf/2608.10693 — **preprint, not peer-reviewed.**
- **EVIDENCE STRENGTH:** Weak–Moderate (unreviewed; authors state results are untested in live trading; wing data quality limits conclusions).
- **Detail:** SPX IV rises before FOMC, peaks on announcement day before the 2pm press conference, declines during it. **Strongest at 0 DTE, fading with maturity; 2-day options much weaker and later; 10-day options show almost none.** Mann-Whitney tests show the IV distribution shifts up ~one day before the meeting, strongest near the money. IV leads realised volatility: IV rises beforehand while RV only rises once the conference starts (no formal IV−RV gap estimated). Convolutional 2D-LSTM on a fixed IV grid, with SVI surface construction best: **RMSE ~8% below random walk for calls, ~9% for puts at horizon 1,** not always significant. **Adding an FOMC date dummy gives small RMSE/MPE gains; Diebold-Mariano significance is mainly on announcement days.** Errors concentrate in short-maturity wings; the model mostly learns IV persistence and mean reversion and underestimates IV on announcement days without the dummy. No option returns or trading tests.
- **IMPLICATION FOR THE BUILD:** The "almost none at 10 DTE" result independently corroborates Claim 4 and is the clearest single statement of the project's horizon problem. The FOMC-dummy gain is real but confined to announcement days at short maturity — outside the project's frame. **Useful as: a reason to add an FOMC flag to any short-dated display, and a reason not to add one to the 42–90 DTE forecast.**

---

## TRANSFER VERDICT

**The framework transfers mechanically and directionally, but not economically at the project's horizon.**

**Where it transfers:**

1. **Mechanically — fully.** Zhong (2026) demonstrates that a deterministic-time event jump calibrated from the option surface materially improves SPX pricing fit for FOMC, CPI and NFP (IV MAE 0.1080 → 0.0926; median spread-normalised error 14.0 → 8.9). The project's existing decomposition needs no new mathematics, only an event calendar and, ideally, non-spanning expiries as the control leg.

2. **Informativeness — transfers, and is stronger than earnings at the right maturity.** Song (2026) finds implied FOMC event uncertainty from 0DTE options forecasts the realised announcement-window move with **R² 78–85%**, versus R² ≈ 28.5% for implied earnings jump vol against the realised earnings move. The macro number is higher precisely because a 0DTE contract isolates the event, whereas a 40-day earnings expiry dilutes it. **Crucially, Song finds zero forecasting power for pre-announcement windows** — the implied event move tells you about the event, not about the approach.

3. **Direction of bias — transfers.** Wright (*JTSA* 2025) finds significantly positive event-day variance risk premia for the S&P 500 on both FOMC (**0.248\*\*\***) and employment reports (**0.204\*\*\***), meaning implied event variance exceeds realised — the same sign as the earnings 8.22% implied vs 7.42% realised. His PIT tests reject at 5% for all four series on FOMC days, and realised Treasury outcomes on FOMC days never fell in the extreme deciles of the implied distribution: **the implied event distributions are too wide.** Kelly, Pástor & Veronesi (*JF* 2016) find the same for political events: event-spanning VRP 0.0465 vs 0.0358 for controls, and ATM puts 5.1% richer when spanning an event (16.0% for 10%-OTM).

**Where it does not transfer — and this is decisive:**

4. **Magnitude fails at 42–90 DTE.** Zhong's fitted event jump sizes are FOMC 0.81%, CPI 0.91%, NFP 0.10%. By my own arithmetic (derived, not published): a 0.81% one-day jump is **~0.69% of total variance in a 60-day, 20%-vol expiry**; CPI is ~0.87%; a whole 60-day window containing 2 CPI, 1 FOMC and 3 payrolls is **~2.4%**. An earnings day is **~57%** of a 40-day expiry. That is a 60–80× difference in how much of the contract the event explains. Adamski & Ślepaczuk corroborate directly and independently: FOMC IV elevation is strong at 0 DTE, weak at 2 DTE, and **almost absent at 10 DTE**.

5. **Therefore the cost hurdle is failed by roughly 30×.** Even granting macro events the full earnings-scale ~10% relative richness, the extractable edge at 60 DTE is ~10% of 0.7% ≈ **0.07% of straddle value**, against the project's measured **2% of premium** index cost at 42–48 DTE. There is no version of this that is viable. For single names the comparison is worse still (10.1% median cost, and the macro share is diluted further by idiosyncratic variance).

6. **And at the one horizon where the magnitude *is* dominant (0–1 DTE), the premium appears to be roughly fairly priced.** The open-source 2022–2026 study finds realised/implied move ratios of CPI 0.94, FOMC 0.94, payrolls 1.11 — **none statistically distinguishable from 1** — while normal days are 0.89 [0.84, 0.94], reliably below 1. Release days charge ~27% more and move ~43% more (rank test p = 0.19). Seller Sharpe: 0.52 skipping release days, **−0.49 on release days only.** This is weak evidence (n ≈ 35–51, VIX1D proxy, unreviewed) but it points the opposite way to a naive "sell macro event vol" read.

7. **The option-return literature is genuinely contradictory on FOMC.** DeSimone (2017) finds **>77% of the index's total negative annualised straddle return falls on announcement days**, with CPI/NFP days at −1.3% to −2.5% vs −0.1% elsewhere — but **FOMC days strongly positive** (vol cheap into FOMC). Windmar (2025) finds FOMC straddle buyers lose −5.6% [−1,1] and −12.9% [−3,3], and CPI −5.2%, but **excludes all transaction costs** and finds payrolls insignificant. Wright says rich. The GitHub study says fair. **Four sources, four signs. There is no reliable, signed, cost-surviving macro event premium.**

**Net:** implement the macro calendar as **display and regime context**. Show the implied event move where it is extractable (it is a legitimate, informative quantity — Song's R² proves that). Do **not** generate event-driven entries from it, and do **not** feed it into single-name event-vol modelling. The honest statement for the project's documentation: *the earnings decomposition works for macro events, and tells us that macro events are too small to trade at our horizon.* That is a real finding, not a failure.

**One exception worth building for: elections.** Londono & Samadi report that elections descriptively carry the largest event premiums of any calendar item, exceeding all economic releases; Kelly/Pástor/Veronesi price them at 5.1% ATM / 16% deep-OTM; and the 2026 midterm VIX futures bump (17.4 Sept → 19.7 Nov) was visible and extractable months ahead at tradeable maturities. Elections are the only macro event whose footprint plausibly approaches earnings scale at 42–90 DTE. Even there, no author has run an option-return test net of costs, so it is an **unverified candidate**, not a signal.

---

## EVENT CALENDAR PRIORITY

Ranked by whether the project should build for it. "Implied move extractable" = can the project fit a jump from its own surface at a maturity it trades. "Measured bias" = is there a credible implied-vs-realised result.

| # | Event type | Frequency | Implied move extractable at 42–90 DTE? | Measured implied-vs-realised bias | Actionable vs regime-only | Build verdict |
|---|---|---|---|---|---|---|
| 1 | **US elections** (presidential / midterm) | Every 2 yrs | **Yes** — visible term-structure kink months ahead (VIX fut 17.4→19.7, Sept→Nov 2026); largest event premium in the calendar (Londono & Samadi) | **Partial.** Event-spanning VRP 0.0465 vs 0.0358 control; ATM puts +5.1%, 10%-OTM +16.0% (Kelly/Pástor/Veronesi, *JF* 2016). No implied-vs-realised *move* test; no option-return test. | **Candidate actionable** — the only one. Unverified net of costs. | **Build the decomposition. Display it. Do not auto-trade it.** Richness is in the wings → defined-risk short-wing if ever acted on. Modulate by economic conditions (premium ~8% weak vs ~1% strong). |
| 2 | **FOMC** | 8/yr | **No** — strong at 0 DTE, almost absent at 10 DTE (Adamski & Ślepaczuk). Jump σ 0.81% ≈ 0.69% of 60-day variance. | **Yes but contested.** Wright: S&P event-day VRP +0.248\*\*\* (rich). DeSimone: FOMC straddles positive (cheap). Windmar: buyers −5.6% (rich, no costs). GitHub: ratio 0.94, CI spans 1 (fair). | **Regime-only.** | **Calendar flag + regime context.** Show the VIX build-into / collapse-on pattern (+0.60% over 6 days, falls on the day, half pre-announcement — Hu et al.). No entries. Do not use the dead pre-FOMC drift. |
| 3 | **US CPI** | 12/yr | **No** — jump σ 0.91% ≈ 0.87% of 60-day variance. Footprint 45 bp (t = 10.4) — the most statistically reliable of the three, but tiny in variance terms. | **Weak/mixed.** DeSimone: CPI days −1.3% to −2.5% straddle returns. GitHub: ratio 0.94, CI spans 1; 2022 ratio 1.48 vs 2023–26 0.78 (post-hoc split, flagged). Cboe: surface response weakened sharply post-2020. | **Regime-only.** | **Calendar flag.** Estimate anything CPI-related on a short rolling window — the pre-2020 relationships do not hold. Note spreads widen *after* the print: bad exit timing. |
| 4 | **US payrolls / NFP** | 12/yr | **No** — jump σ 0.10%, effectively nil; Zhong's fit often hits its lower bound. Largest regression footprint (53 bp, t = 8.8) yet smallest fitted jump — the two disagree. | **Weakest and possibly reversed.** GitHub: ratio **1.11** (p = 0.06) — the one event type where options may *under*price the move; real-trade seller return −0.14%. Windmar: payrolls insignificant/mixed. Wright: VRP +0.204\*\* (rich). | **Regime-only, with a caution flag.** | **Calendar flag only.** This is the one event where the thin evidence leans toward options being *cheap*, so do not treat it as a short-vol opportunity. |
| 5 | **Non-US macro (ECB, euro CPI)** | ~12–20/yr | No | Euro-area CPI 18 bp (t=2.8) for US equity; euro policy rate 5 bp (n.s.) | Regime-only, marginal | **Skip** for a US-market retail tool. |
| 6 | **OPEC / OPEC+** | ~2–6/yr scheduled | **No** — IV *declines* slightly into meetings at 30-day maturity; no run-up/collapse; largest oil-vol episodes were not near meetings (OptionMetrics, 57 meetings since 2005) | **No credible evidence.** | Regime-only at best | **Skip the decomposition.** Optionally surface OPEC dates as plain context on energy names, with no implied-move number. |
| 7 | **US GDP** | 4/yr | **No** — 4 bp, t = 0.5, insignificant | No | Neither | **Skip.** |
| 8 | **Treasury auctions** | ~weekly | **No** — no equity-surface footprint found; absent from every significant event set | **No credible evidence found.** | Neither | **Do not build.** Matters in rates vol (Wright: 30y FOMC 0.116\*\*\*, employment 0.177\*\*\*), not equity. |
| 9 | **Trade / tariff deadlines** | Irregular | **No.** Londono & Samadi *excluded* Apr–May 2025 tariff days as option-price noise rather than priced events | No | Regime-only | **Skip as a calendar event.** Treat as an unscheduled-shock regime, per the geopolitical verdict. |
| 10 | **Unscheduled geopolitical shocks** | Irregular | **N/A** — not knowable ex ante | Ex-post only | **Regime-only** | **Sizing gate, never an entry.** See below. |

---

## GEOPOLITICAL VERDICT

**Regime input only — and a weak one. Not an entry signal, and not a term in the volatility forecast.**

The one study that asks the project's exact question answers it cleanly. Nonejad (*Finance Research Letters* 47, 2022) finds the one-month-lagged log Caldara–Iacoviello GPR index **does not improve out-of-sample volatility forecast accuracy as a regressor**, and combining it with economic variables also fails. But used as the **monitoring variable** in a dynamic forecast-selection framework it produces MSE gains of ~3% at one month, rising to ~10% at longer horizons.

That is precisely the regime-versus-signal distinction the brief anticipated, confirmed in a peer-reviewed out-of-sample test. It also maps exactly onto the project's prior finding that macro-augmented GARCH-MIDAS with all variables was 39% worse: **GPR as a term degrades the forecast; GPR as a switch helps it slightly.**

The ex-post magnitudes are real — a major home-country GPR event costs ~0.7–1 pp of monthly return, large country-specific shocks ~−2%, military conflict >−4.5 pp for EMDE firms, EME effects persisting ≥6 months, option-implied vol spiking after shocks (IMF GFSR April 2025). But three things make them unusable as entries:

1. **The US-relevant effect is the weakest one.** The military-conflict effect is **not statistically significant for advanced-economy firms.** The large numbers are emerging-market and direct-exposure numbers. A US retail account sits in the part of the cross-section where the effect is smallest.
2. **Timing is unavailable.** The IMF notes anticipation effects (AE firms −5 pp in the month before their country's conflict), but those are identified *conditional on a conflict having occurred* — a researcher's hindsight window, not a signal a tool can act on prospectively.
3. **The 5 November 2026 episode is the practical refutation.** The largest single-day volatility event of the recent window — S&P −4.4%, Nasdaq −5.5%, VIX +70% (one of only eight such moves since 1991) — came from an AI/semis unwind and data-centre construction pauses, one day after a benign election resolution. It was on no event calendar and no geopolitical index would have flagged it.

**What to build.** A GPR level/percentile read used as a **sizing and structure gate**, not an input: at elevated GPR, size down and prefer defined-risk structures. Optionally use it to select between volatility models rather than as a model term, which is the one use with peer-reviewed out-of-sample support. Do not display it as a forecast driver, do not let it generate entries, and do not expect more than a few percent of forecast MSE from it.

---

## MACRO IN THE VOL FORECAST

**At 42–90 DTE, almost nothing survives. Add at most one variable, and test it against the incumbent.**

**Fails (do not add):**
- **All macro variables together.** Fang, Lee & Su (*JEF*): kitchen-sink GARCH-MIDAS MSFE ratios **1.39, 1.32, 1.21, 1.19** at 1–4 quarters, negative Giacomini-White at every horizon. This is the source and vindication of the project's prior 39% finding. Real GDP and industrial production are dropped by the Lasso outright.
- **Geopolitical risk index as a regressor.** Nonejad (*FRL* 2022): no out-of-sample improvement, alone or combined.
- **MOVE index.** No credible evidence found of incremental equity-RV forecast value at this horizon.
- **FOMC/CPI event dummies.** Adamski & Ślepaczuk: the FOMC dummy's Diebold-Mariano gains are significant **mainly on announcement days at short maturity**; 10-day options show almost no FOMC IV elevation at all. There is nothing for a 42–90 day forecast to capture.

**Worth one test each (the only survivors with peer-reviewed out-of-sample support):**
- **Default / credit spread.** Survives Adaptive-Lasso selection at 1% significance (θ = +0.57) in Fang/Lee/Su. The only variable in the brief's candidate list with peer-reviewed OOS support at an overlapping horizon.
- **Housing starts.** The single strongest predictor in that study, beating even the selected-variable benchmark at every horizon (MSFE ratios 0.980 / 0.975 / 0.967 / 0.955). Counter-intuitive for an options tool, which is itself a reason to trust the selection procedure over intuition.

**Caveats on both:** the horizons are 1–4 quarters (≈63–252 trading days), so only the 1-quarter result straddles 42–90 days. Gains are 2–5% in MSFE — real but small, and smaller than the variance in the project's own two-component estimate. **Protocol: add one variable at a time, compare against the existing two-component model with a Giacomini-White or Diebold-Mariano test on a genuine out-of-sample window, and keep it only if it wins. Default to not adding anything.** The evidence base's clearest message is that the simpler model is hard to beat and easy to wreck.

**VIX term structure:** no evidence found that its slope improves an RV *forecast* at 42–90 days. Johnson (*JFQA* 2017) establishes it as a *return*-premium state variable, which is a different question and one the project has already answered negatively (direction ~7 bp/month). Keep the VIX term structure as a **display and regime indicator** — the FOMC build-and-collapse pattern and the election kink are both legible in it — not as a forecast input.

---

## DISCONFIRMING EVIDENCE

1. **Macro event volatility appears efficiently priced at the horizon where it matters.** Realised/implied move ratios 2022–2026: CPI 0.94 [0.71, 1.21], FOMC 0.94 [0.71, 1.20], payrolls 1.11 [0.89, 1.38] — none distinguishable from 1 — while *normal* days are 0.89 [0.84, 0.94], reliably overpriced. Release days charge ~27% more and move ~43% more (p = 0.19). Short-vol Sharpe is **0.52 skipping release days and −0.49 on release days only.** (Practitioner, weak, n ≈ 35–51.) This directly contradicts a "macro events are rich like earnings" thesis.

2. **Payrolls may be *under*priced, not overpriced.** Ratio 1.11 with p = 0.06, real-trade seller return −0.14%, and overnight pricing of little extra risk for the 08:30 release while the move ran ~1.5× the priced amount. Zhong's fitted NFP jump of 0.10% frequently hits its lower bound. Yet Londono & Samadi give payrolls the *largest* regression footprint (53 bp, t = 8.8). These cannot both be right; the disagreement is unresolved.

3. **The pre-FOMC announcement drift is dead.** 27.1 bp (t = 5.95) pre-2011 → 8.9 bp and insignificant after; insignificant across most windows 2016–2023; structural break at the March 2016 meeting; the only surviving significant piece (~0.19%) is in the overnight gap. Over 1936–2024 FOMC days average ~12 bp vs ~34 bp in the original window, implying the original partly captured unexpectedly good news rather than a premium.

4. **Geopolitical indices have no tradeable forecast content as regressors.** Nonejad (peer-reviewed, OOS): lagged log GPR does not improve point forecast accuracy, alone or combined with economic variables.

5. **FOMC straddle returns have been found strongly *positive* in a careful study** — DeSimone (2017) attributes this to expected volatility declines, i.e. FOMC vol is *cheap* for buyers of the straddle, the exact opposite of Wright's +0.248 VRP and Windmar's −5.6%. Any confident sign on FOMC vol richness is unsupported.

6. **Tail moments beat volatility for FOMC return prediction, and volatility's own predictive power vanishes under controls.** Jacobs, Ke & Pan (*JFQA* 2026): abnormal pre-FOMC volatility predicts returns at adj. R² ~2–4% and **loses significance once tail risk is controlled.** Evidence against adding FOMC volatility features.

7. **The macro event IV footprint is nearly absent at the project's maturities.** Adamski & Ślepaczuk: strongest at 0 DTE, much weaker at 2 DTE, **almost none at 10 DTE.** The project trades 42–90 DTE. This is the most direct disconfirmation of the whole enterprise.

8. **OPEC shows no run-up/collapse pattern at all** — IV declines slightly into meetings, and the biggest oil-vol episodes (March–April 2020) were nowhere near a meeting.

9. **Kitchen-sink macro augmentation is 19–39% worse out-of-sample**, replicating the project's own prior finding in a peer-reviewed study, with real GDP and industrial production dropped by variable selection entirely.

10. **The dominant volatility event of the recent window was uncalendared.** 5 Nov 2026: S&P −4.4%, VIX +70%, one day after a benign election resolution. A post-event short-vol rule — the macro analogue of the project's one positive single-name signal — would have been maximally short at the worst moment.

11. **CPI's option-surface response weakened sharply after 2020** despite CPI becoming more salient. Pre-COVID: ~±1.5% two-day option returns per pp of surprise, IV responses ~2%. Post-COVID: "markedly smaller," signs reversed, mostly insignificant. Salience in the news is not salience in the surface.

12. **Londono & Samadi explicitly decline to compare implied event pricing with realised moves**, calling ex-post reaction a limitation for identifying which releases matter ex ante. The best event-ranking study in the literature does not establish a bias in either direction.

---

## OPEN QUESTIONS

1. **Nobody has run the earnings-style implied-vs-realised event-move test for macro events at 42–90 DTE.** Wright tests event-day VRP on event-day-expiring options; Song tests 0DTE; Zhong tests pricing fit only; Londono & Samadi explicitly decline. The exact Dubinsky/Johannes/Kaeck/Seeger comparison (implied event vol 8.22% vs realised 7.42%) has no macro counterpart at any maturity. **This is cheaply answerable from the project's own data** — two ATM maturities spanning an FOMC, versus the realised FOMC-day move, over 60–80 meetings — and would be a genuine contribution. Expect the answer to be "the estimate is too noisy to sign," given the ~0.7% variance share.

2. **"FOMC Event Risk" by Johannes, Kaeck & Seeger (SSRN 4484011) could not be retrieved** and is cited second-hand via Song as showing straddle losses over the FOMC statement window and no significant returns through the press conference. This is the single most important missing source — same authors, same method, macro event. **Worth one targeted retrieval attempt.**

3. **Payrolls: largest regression footprint (53 bp) but smallest fitted jump (0.10%) and a realised/implied ratio above 1.** Which is wrong? If payroll options are genuinely cheap, that inverts the whole thesis for one event type.

4. **Does the election term-structure kink survive a cost-adjusted option-return test?** No author has tried. Kelly/Pástor/Veronesi stop at prices; the 2026 evidence is press reporting. This is the one macro event where the test is worth running.

5. **What is the actual realised distribution of the non-event residual on days following a resolved macro catalyst?** The 5 November 2026 episode suggests post-event vol collapse is systematically followed by elevated gap risk, which would make "sell vol after the macro event" structurally worse than its earnings analogue. Testable on index data.

6. **Does the credit/default spread beat the project's two-component model at 42–90 days specifically?** Fang/Lee/Su test 1–4 quarters. The 42–90 day window is shorter than their shortest horizon.

7. **Is the 2022–2026 "release days are fairly priced" result an artefact of the post-2021 inflation regime?** Wright's rich-event-vol result ends Aug 2020; the fair-pricing result starts May 2022. The two samples do not overlap, so regime change and contradiction are indistinguishable.

8. **Does the 0DTE market's existence mechanically compress longer-dated macro event premia** by concentrating event trading in daily expiries? Song's March 2016 structural break (first Wednesday SPX expirations) hints at this. If so, the 42–90 DTE footprint may have been larger historically and the project's horizon problem is getting worse, not better.

---

## TOP 10 SOURCES

1. **Jonathan H. Wright, "Event-Day Options," *Journal of Time Series Analysis*, 2025** (DOI 10.1111/jtsa.12819; NBER WP 28306). *Peer-reviewed.* The only peer-reviewed measurement of event-day variance risk premia for macro events. S&P FOMC +0.248\*\*\*, employment +0.204\*\*\*; too-wide implied distributions via PIT tests. **The single most load-bearing source for the transfer verdict.** https://www.nber.org/system/files/working_papers/w28306/w28306.pdf

2. **Yuhan Song, "Pre-FOMC Uncertainty Accumulation: Evidence from 0DTE Options," 2026.** *Working paper, AFA submission.* Implied FOMC event vol forecasts the realised announcement-window move at R² 78–85%; 71%/29% statement/press-conference resolution split; dates the drift's death to March 2016; skew carries no directional content. **The informativeness half of the transfer answer.** https://afajof.org/management/viewp.php?n=260400

3. **Kelly, Pástor & Veronesi, "The Price of Political Uncertainty," *Journal of Finance* 71(5), 2016.** *Peer-reviewed, top-tier.* 271 political events, 20 countries. Event-spanning options +5.1% ATM / +16.0% at 10% OTM; VRP 0.0465 vs 0.0358 control; premia 8% weak vs 1% strong conditions. **The best evidence for the election case and the wing concentration.** https://www.nber.org/system/files/working_papers/w19812/w19812.pdf

4. **Tenghan Zhong, "Non-Spanning Identification of Scheduled Event Risk in Option Pricing," arXiv:2606.12872, 2026.** *Preprint.* Proves the decomposition is calibratable to FOMC/CPI/NFP and supplies the fitted jump sizes (0.81% / 0.91% / 0.10%) that drive the decisive variance-share calculation. **Supplies the numbers that kill the trade.** https://arxiv.org/pdf/2606.12872

5. **Fang, Lee & Su, "Predicting the Long-term Stock Market Volatility: A GARCH-MIDAS Model with Variable Selection," *Journal of Empirical Finance*.** *Peer-reviewed.* Kitchen sink 19–39% worse OOS; only unemployment, housing starts, PPI and default spread survive. **Explains and vindicates the project's prior 39% finding, and names the only candidates worth testing.** https://faculty.ucr.edu/~taelee/paper/Fang%20Lee%20Su%20JAE%2020180925.pdf

6. **Londono & Samadi, "Which Days Matter for Global Equity Markets?" FEDS Notes, Fed Board, 3 Oct 2025.** *Central-bank note.* The event ranking: US employment 53 bp, FOMC 49 bp, US CPI 45 bp, GDP 4 bp (n.s.); elections descriptively largest. **The calendar's backbone.** https://www.federalreserve.gov/econres/notes/feds-notes/which-days-matter-for-global-equity-markets-using-options-to-price-events-in-the-global-calendar-20251003.html

7. **Nonejad, "An interesting finding about the ability of geopolitical risk to forecast aggregate equity return volatility out-of-sample," *Finance Research Letters* 47, 2022.** *Peer-reviewed.* GPR fails as a regressor, works as a regime-monitoring variable (3–10% MSE gains). **Settles the geopolitical verdict.** https://www.sciencedirect.com/science/article/abs/pii/S154461232200037X

8. **Hu, Pan, Wang & Zhu, "Premium for Heightened Uncertainty: Solving the FOMC Puzzle," NBER WP 25817, 2019.** *Working paper (later *JFE*).* Pre-FOMC drift 27.1 bp → 8.9 bp insignificant post-2011; VIX +0.60% over six days into FOMC, falls on the day with half pre-announcement. **The FOMC volatility regime pattern worth displaying.** https://www.nber.org/system/files/working_papers/w25817/revisions/w25817.rev1.pdf

9. **Adamski & Ślepaczuk, "When the Fed Speaks: Dynamics and Forecasts of the Volatility Surface," arXiv:2608.10693, 2026.** *Preprint.* FOMC IV elevation strongest at 0 DTE, almost absent at 10 DTE; FOMC dummy gains confined to announcement days. **The clearest statement of the project's horizon problem.** https://arxiv.org/pdf/2608.10693

10. **Jacobs, Ke & Pan, "Tail Risk Around FOMC Announcements," *JFQA* 61(2), March 2026, 640–672.** *Peer-reviewed, top-tier.* 207 meetings, 1996–2021. Abnormal pre-FOMC volatility predicts returns at only 2–4% R² and loses significance under tail-risk controls; skew/kurtosis reach ~12–13%. **Evidence against adding FOMC directional or volatility-level features.** https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/tail-risk-around-fomc-announcements/567F3B47420074A6521C31755E7AE587

**Honourable mentions:** Knox, Londono, Samadi & Vissing-Jorgensen, "Equity Premium Events," Fed Board draft 2025 (FOMC the most frequently priced event; FOMC+CPI+NFP only ~23% of total expected daily returns); the open-source "options-event-risk" study (the fair-pricing null, weak but the only cost-aware test found); DeSimone (2017) dissertation (>77% of index negative straddle returns on announcement days, but FOMC positive); Caldara & Iacoviello, *AER* 112(4), 2022 (the GPR index itself); IMF GFSR April 2025 Ch. 2 (geopolitical magnitudes); Cboe/Nejadmalayeri & Campbell (CPI surface response weakened post-2020); OptionMetrics (OPEC null).
