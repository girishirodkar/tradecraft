# Research Strand 08: What Actually Predicts Equity Direction

**Date:** 10 November 2026
**Scope:** Cross-sectional equity return prediction — the literature on what predicts whether a stock goes up or down, assessed against the Options Contract Explorer's design constraints (1–6 month horizon, 20–50 name watchlist, EDGAR/free/WRDS data only, retail costs).

---

## EXECUTIVE ORIENTATION

The headline finding of this strand is uncomfortable and should be stated before any individual signal is discussed.

The best current estimate of what the published cross-sectional equity prediction literature is worth **in large, liquid stocks, after 2005** is approximately **7 basis points per month, with a median t-statistic of 0.45** (Chen & Welch 2026). That is the median across ~200 published anomalies. Net of realistic trading costs the same literature produces roughly **-1 to +4 bp/month**. Value and momentum — the two most famous directional factors in finance — are described in that paper as essentially dead in liquid names.

This is not an outlier result. It is consistent with Chen & Velikov (JFQA 2023), who find 8 bp/month equal-weighted and 4 bp/month value-weighted post-2005 under cost-optimised implementations, with only 11 of 120 anomalies clearing |t| > 2.

The counterweight is real but narrower than it first appears. Jensen, Kelly & Pedersen (JF 2023) find 82–85% of factors replicate — but they measure *CAPM alpha at one-month holding periods across 93 countries including nano-caps*, which is a different question from "does this produce tradeable directional alpha in US large caps today."

**The honest reading: the literature replicates as science and fails as a trading edge in the universe this product operates in.** A watchlist of 20–50 names is, almost by construction, liquid US large/mid caps — precisely the segment where Chen & Welch show predictability has been arbitraged away.

The one category that survives in that paper is **profitability**. That is the strand's main constructive finding.

---

## FINDINGS

### 1. Post-earnings announcement drift — the original effect

**CLAIM:** PEAD is the longest-surviving and best-documented directional anomaly; sorting on standardised unexpected earnings (SUE) historically produced roughly 2% abnormal return over the 60 trading days following an announcement, with drift persisting two to three quarters.
**SOURCE:** Ball & Brown (1968), *Journal of Accounting Research*; Bernard & Thomas (1989), *Journal of Accounting Research* 27, 1–36; reviewed in Josef Fink, "A Review of the Post-Earnings-Announcement Drift," University of Graz Working Paper 2020-04 (Nov 2020), https://static.uni-graz.at/fileadmin/sowi/Working_Paper/2020-04_Fink.pdf — **peer-reviewed originals, working-paper review**
**EVIDENCE STRENGTH:** Strong (for the historical effect)
**HORIZON:** Drift strongest in the first quarter after announcement; persists 2–3 quarters. Fink reports Bernard & Thomas at ~2% over 60 trading days, ~4% per quarter; early long/short estimates reach ~18% annualised.
**DECAY EVIDENCE:** See finding 2 — substantial.
**DATA OBTAINABILITY:** Excellent. SUE from a time-series model of quarterly EPS is computable **entirely from EDGAR XBRL** (`EarningsPerShareDiluted`, quarterly, 8+ quarters history). Analyst-based SUE needs IBES or a vendor. Fink notes analyst-forecast-based surprises produce *larger* drift than time-series surprises — so the free version is the weaker version.
**IMPLICATION FOR THE APP:** The 60-day drift window maps cleanly onto 60–90 DTE contracts. This is the single best horizon fit in the entire literature for this product. The problem is entirely whether it still exists.

---

### 2. PEAD decay — the critical question

**CLAIM:** PEAD hedge returns have declined steadily since the 1980s and are statistically indistinguishable from zero after 2017 in the most careful recent study.
**SOURCE:** Kettell, McInnis & Zhao, "Why Has PEAD Declined Over Time? The Role of Earnings News Persistence," University of Texas at Austin working paper, April 2022, https://business.columbia.edu/sites/default/files-efs/imce-uploads/CEASA/Events%20Page/PEAD_Declined_over_time.pdf — **working paper, not yet peer-reviewed**
**EVIDENCE STRENGTH:** Moderate-to-Strong (large sample, clean design; working-paper status and no published subperiod significance tests are the caveats)
**HORIZON:** Quarterly hedge return measured announcement to next announcement.
**DECAY EVIDENCE:** This *is* the decay evidence. 526,828 firm-quarters, 185 fiscal quarters, 1974–2020. Trend coefficient −0.020 (t = −3.06) on an intercept of 6.24%. Five-year moving average of hedge PEAD: ~5% in the 1980s–90s, ~4% in the 2000s–early 2010s, ≤3% in the late 2010s. The authors state hedge returns are indistinguishable from zero after 2017. Critically, the decline is **concentrated in the later window [+7 days, next announcement]** (−0.027, t = −4.68) while the **immediate window [+2, +6] has actually strengthened** (+0.006, t = 3.92). Decay is concentrated in **non-microcaps** (trend −0.031, t = −3.57); microcap trend is insignificant.
Their proposed mechanism is not arbitrage but **declining earnings persistence**: a firm in an extreme SUE decile is much less likely to stay there. Hedge SUE persistence falls from ~4.0 pre-mid-1980s to ~2.0 in the 2010s. Adding persistence to the regression drives the trend coefficient to insignificance (0.008, t = 1.08). "Stayers" earn 14.1% (t = 25.85) versus −1.8% for "movers," and the stayer share has fallen.
**DATA OBTAINABILITY:** N/A (this is evidence about the signal, not a signal).
**IMPLICATION FOR THE APP:** Three things follow, and they cut in opposite directions.
(a) The decay is **worst exactly where the app operates** — non-microcaps. Any instinct to say "this is a microcap effect that doesn't apply to me" is backwards; the microcap version is the one that survived.
(b) The surviving component is the **[+2, +6] day window**, which is unusable at 60–180 DTE. The part that died is the part this product would trade.
(c) The persistence mechanism is actionable: a filter for *repeat* positive-surprise firms (consecutive quarters in the same extreme decile) targets the "stayers" who earn 14.1%. This is computable from EDGAR XBRL. It is the most interesting single idea in this strand, and it is untested out of sample.

---

### 3. PEAD out of sample, 2023–2026

**CLAIM:** An independent out-of-sample test over 43,111 announcements from Jan 2023 to Oct 2026 finds PEAD still present in large caps but small and fading fast.
**SOURCE:** Gaurav Gupta, "Is Post-Earnings Drift Still Tradable? 43,000 Announcements, 2023–2026," https://guptagaurav.info/articles/earnings-drift — **practitioner blog post, not peer-reviewed; author discloses AI assistance in the analysis**
**EVIDENCE STRENGTH:** Weak (methodologically transparent but unrefereed, <4 years, one regime, self-disclosed probable survivorship bias)
**HORIZON:** Position formed at close of day +1, drift measured days +2 to +61 — i.e. ~3 months. Direct fit to 60–90 DTE.
**DECAY EVIDENCE:** Top-minus-bottom SUE quintile spread, all sizes: +1.7 pp over 60 days (t = 4.2). Large caps (>$10bn): +2.0 pp (t = 3.4). Mid: +1.4 pp (t = 2.9). Small: +1.1 pp (t = 2.1). **But the spread is +2.6 pp for 2023–24 announcements versus +0.5 pp for 2025–26.** The earnings-announcement-return (EAR) variant is weaker and insignificant: +1.3 pp (t = 1.4).
**Net of costs** (mid+large long-short book): gross 7.9%/yr, Sharpe 1.21; 6.0% at 10 bp one-way, 4.0% at 20 bp, 2.1% at 30 bp. Year-by-year at 10 bp: −1.3%, +13.6%, +2.2%, +7.9% — i.e. most of the return came from a single year (2024).
**DATA OBTAINABILITY:** The signal used is YoY change in quarterly EPS scaled by its own 4–8 quarter variability — **computable from EDGAR XBRL alone**, no IBES required.
**IMPLICATION FOR THE APP:** The one piece of evidence that PEAD still has a pulse in large caps at the right horizon. Treat it as a hypothesis to re-test, not a result. The 2025–26 collapse to +0.5 pp is the number to watch. Note the internal inconsistency flagged in the source (chart commentary describing a 4→5.4 point gap does not reconcile with the 1.7 pp headline), which is a reason for caution.

---

### 4. Analyst estimate revision momentum

**CLAIM:** Analyst earnings forecast revisions predict returns and are not subsumed by either price momentum or earnings surprise; the drift runs at least 90 days.
**SOURCE:** Chan, Jegadeesh & Lakonishok, "Momentum Strategies," *Journal of Finance* 51(5), 1996, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7836 — **peer-reviewed**. Also Kanyuan Huang, "The Value of Analyst Forecast Revisions: Evidence from Earnings Announcements," UCLA doctoral dissertation, 2022, https://escholarship.org/content/qt2r7980f3/ — **dissertation, not peer-reviewed**
**EVIDENCE STRENGTH:** Moderate for existence; Weak for post-2015 survival (nobody has published a clean recent test)
**HORIZON:** Chan/Jegadeesh/Lakonishok work at 6 and 12 months. Huang measures 90-day CARs (days +3 to +90) and does not test beyond 90 days. **The horizon fit to 1–6 months is good** — better than PEAD's surviving component.
**DECAY EVIDENCE:** Thin, and that is itself a finding. CJL document that price momentum and earnings momentum are mutually non-subsuming (regression coefficient on past return falls 5.7% → 2.9% when earnings surprise is added, remaining significant), and that ~41% of the first-six-month price momentum premium occurs around earnings announcement dates. Huang (1995–2019) finds a top-minus-bottom decile 90-day size/BM-adjusted CAR spread of **3.43%** for aggregated revisions, versus 2.18% for IBES-based earnings surprise and 1.78% for Compustat-based surprise — i.e. revisions beat SUE. Revisions stay significant at 1% controlling for SUE deciles, announcement CAR, and 12-month past return. **But R² is 0.001–0.003**, and Huang does not test whether the effect weakened over his sample. I found no peer-reviewed study isolating post-2015 revision-signal returns.
**DATA OBTAINABILITY:** **Moderate — this is the weak link.** WRDS IBES is the research standard and is unconfirmed for this user. Free/cheap alternatives exist but are materially worse:
- *Financial Modeling Prep (FMP)* — consensus estimates, price targets, grades/upgrades/downgrades via API; paid tiers. Vendor-documented; history depth and point-in-time integrity are **not** established.
- *Finnhub* — has an "Open Estimate" product and consensus estimates; free tier heavily rate-limited.
- *Nasdaq Data Link / Zacks* — Zacks revision data is the practitioner standard but is a paid commercial feed.
The fatal issue for all free sources is **point-in-time integrity**: a revision signal needs to know what consensus was on date *t* without look-ahead or restatement. Vendor APIs generally serve current consensus, not a clean historical snapshot. Building your own point-in-time series means capturing consensus daily going forward, which means no backtest.
**IMPLICATION FOR THE APP:** Good horizon fit and good evidence of incremental information, undermined by data. Recommendation: **capture consensus daily from a free API starting now, to build a forward point-in-time series, but do not deploy the signal until you have ≥12 months of self-captured history.** Treat any backtest on vendor-served current consensus as invalid.

---

### 5. Short interest, days-to-cover and borrow fee

**CLAIM:** Equity loan fee is the single strongest cross-sectional predictor among 102 standard anomalies; short interest is second or third; but both are one-month-horizon signals and the stronger one is not obtainable.
**SOURCE:** Engelberg, Evans, Leonard, Reed & Ringgenberg, "The Loan Fee Anomaly: A Short Seller's Best Ideas," SSRN working paper, Sept 2020, https://uncipc.org/wp-content/uploads/2021/05/The-Loan-Fee-Anomaly.pdf — **working paper**. Also Asquith, Pathak & Ritter, "Short Interest, Institutional Ownership, and Stock Returns," *Journal of Financial Economics* 78(2), 2005, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=525623 — **peer-reviewed**
**EVIDENCE STRENGTH:** Strong for loan fee; Moderate for short interest alone
**HORIZON:** **One month.** Engelberg et al. predict one-month-ahead returns. This is the central problem.
**DECAY EVIDENCE:** Engelberg et al.'s sample is 2006–2019 — already mostly post-crisis — and loan fee ranks first on average monthly long-short return, Sharpe, and share of positive months. Monthly long-short: 1.17% (decile) to 3.63% (top/bottom 1%); decile monthly Sharpe 0.40. **After subtracting borrowing costs the decile version still earns 0.48%/month**, versus ~−0.02% for the average anomaly in the same set. ~72% of the loan fee signal is *not* spanned by existing anomalies. Loan fee outperforms short interest by 0.49%–1.72%/month across cutoffs. Separately, 82% of top-decile loan-fee stocks remain top-decile a year later — unusual persistence that partially mitigates the one-month horizon.
Asquith/Pathak/Ritter (1988–2002): constrained stocks (high short interest **and** low institutional ownership) underperform by **215 bp/month equal-weighted but only 39 bp/month value-weighted, and the value-weighted figure is insignificant.** This is the small-cap concentration problem in its purest form.
**DATA OBTAINABILITY:** **Split.** FINRA Equity Short Interest is **free**, published bi-monthly (twice per settlement month), with a documented bulk download API (https://www.finra.org/finra-data/browse-catalog/equity-short-interest). Shares outstanding for the ratio and ADV for days-to-cover are free. **Borrow fee and utilisation are not free.** Engelberg et al. themselves note Markit's continuous loan fee measure is no longer distributed; they use Markit's 1–10 Daily Cost of Borrowing Score and impute fees from bucket means. Retail-visible proxies (IBKR's shortable-shares list, Fintel) are partial, not historical, and not licensable.
**IMPLICATION FOR THE APP:** The prior research finding that option-implied predictability is largely a borrow-fee proxy is **confirmed in direction but not rescued**. Borrow fee is indeed the underlying signal — and it is the one you cannot get. Short interest is the obtainable proxy for the proxy, and it is materially weaker, value-weighted-insignificant, and lives at a one-month horizon. **Verdict: use FINRA short interest as a risk filter (avoid heavily-shorted names on the long side), not as a direction signal.** Bi-monthly publication with a ~8 calendar day lag also makes it stale relative to a one-month horizon.

---

### 6. Accruals and earnings quality

**CLAIM:** The Sloan accrual anomaly is dead. Hedge returns decayed to the point of no longer being positive in US markets.
**SOURCE:** Green, Hand & Soliman, "Going, Going, Gone? The Apparent Demise of the US Accruals Anomaly," *Management Science* 57(5), May 2011, 797–816, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1501020 — **peer-reviewed**. Original: Sloan (1996), *The Accounting Review*
**EVIDENCE STRENGTH:** Strong (published in a top journal, explicitly a decay study)
**HORIZON:** Annual (accruals are measured from annual financials and held ~12 months) — **already a poor fit for 60–180 DTE.**
**DECAY EVIDENCE:** Green/Hand/Soliman attribute the demise to two things: a shrinking mispricing signal (accruals in extreme deciles compressed; relative persistence of cash flows vs accruals declined) and increased hedge fund capital deployed against it (AUM and trading volume in extreme-accrual-decile firms both rose). Later work — Mohanram et al., "Analysts' Cash Flow Forecasts and the Decline of the Accruals Anomaly," *Contemporary Accounting Research* — attributes part of the decline to analysts issuing cash flow forecasts, which teaches the market to distinguish accruals from cash. A 2023 working paper (Wakil, Lento & Sayed, "The Accrual Anomaly is Not Dead: Canadian Evidence," SSRN) revives it **in Canada**, which is not reassuring for a US large-cap watchlist.
**DATA OBTAINABILITY:** Excellent — the balance-sheet accrual measure is directly computable from EDGAR XBRL, and the cash-flow-statement version is too.
**IMPLICATION FOR THE APP:** **Exclude.** This is the cleanest "famous anomaly that died" in the strand. Its attractiveness is entirely that it is cheap to compute, which is not a reason to trade it. Horizon is wrong, published evidence says it is gone, and the revival evidence is in a different market.

---

### 7. Quality, profitability and value

**CLAIM:** Profitability is the only major directional factor category that survives in post-2005 liquid-stock samples; value and momentum do not.
**SOURCE:** Chen & Welch, "What Useful Alphas?," arXiv:2607.06502, July 2026, targeted at *Financial Analysts Journal*, https://arxiv.org/pdf/2607.06502 — **working paper by established authors (Chen is at the Federal Reserve Board; Welch at UCLA), not yet peer-reviewed**. Originals: Novy-Marx, "The Other Side of Value: The Gross Profitability Premium," *Journal of Financial Economics* 108(1), 2013; Asness, Frazzini & Pedersen, "Quality Minus Junk," *Review of Accounting Studies* 24, 2019
**EVIDENCE STRENGTH:** Moderate-to-Strong. Profitability's survival is independently corroborated by Feng, Giglio & Xiu, "Taming the Factor Zoo," *Journal of Finance* 75(3), 2020, https://stefanogiglio.org/papers/feng-giglio-xiu-jf-2020.pdf — **peer-reviewed** — which finds that of 15 factors introduced 2012–2016 tested against 135 pre-2012 controls and 750 test portfolios, only **5** have genuine incremental explanatory power, and **four of the five are profitability or investment**: RMW (t = 4.45), HXZ ROE (t = 3.37), HXZ IA (t = 2.11), QMJ (t = 2.03), plus the He/Kelly/Manela intermediary risk factor (t = 2.21). Ten of the fifteen are redundant.
**HORIZON:** Slow. Profitability is a *level* characteristic updated quarterly; it does not time entry. It persists over multi-year holding periods. **Fit to 60–180 DTE is poor in the sense that it gives no reason to buy a contract today rather than next quarter.**
**DECAY EVIDENCE:** Chen & Welch's survivor list is: cash-based operating profitability, R&D-adjusted operating profitability, gross profitability, net external financing, net equity financing, two seasonal momentum variants, and a realised-implied volatility spread. The profitability category has a post-2005 large-cap median of **~24 bp/month** — against a cross-anomaly median of 7 bp. Even so, their empirical-Bayes shrinkage (Var(t) ≈ 1.09 implying a shrinkage factor of ~0.08) cuts the best survivor's 66 bp raw return to **~6 bp**.
On value specifically: Arnott, Harvey, Kalesnik & Linnainmaa, "Reports of Value's Death May Be Greatly Exaggerated," *Financial Analysts Journal* 77(1), 2021, https://www.tandfonline.com/doi/full/10.1080/0015198X.2020.1842704 — **peer-reviewed** — argue the 2007–2020 value drawdown is mostly revaluation (value got cheaper) rather than a dead premium. This is a genuine disagreement. Chen & Welch call value dead; Arnott et al. call it cheap. Both can be right: the premium may exist at a decade horizon and be useless at a 3-month horizon.
**DATA OBTAINABILITY:** Excellent. Gross profitability = (Revenues − COGS) / Total Assets, all three from EDGAR XBRL (`Revenues`, `CostOfGoodsAndServicesSold`, `Assets`). Cash-based operating profitability needs working-capital adjustments, also in XBRL. Net equity financing from the cash flow statement. **This is the best data-cost-to-evidence ratio in the strand.**
**IMPLICATION FOR THE APP:** Include profitability, but **as a universe screen rather than a timing signal**. It tells you which names on the watchlist deserve directional bets at all; it does not tell you when. Its multi-year horizon is a feature for that use and a bug for any other.

---

### 8. Momentum, properly characterised

**CLAIM:** Cross-sectional momentum is well-documented historically, suffers severe crashes, and shows essentially no surviving return in post-2005 liquid US stocks.
**SOURCE:** Jegadeesh & Titman (1993), *Journal of Finance*; Daniel & Moskowitz, "Momentum Crashes," *Journal of Financial Economics* 122(2), 2016, https://www.kentdaniel.net/papers/published/mom12.pdf — **peer-reviewed**; Chen & Velikov, "Zeroing in on the Expected Returns of Anomalies," *Journal of Financial and Quantitative Analysis*, 2023 (FEDS WP 2020-039), https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf — **peer-reviewed**
**EVIDENCE STRENGTH:** Strong for the historical effect, Strong for the crash risk, Moderate-to-Strong for recent death in liquid names
**HORIZON:** Standard specification: 12-month formation skipping the most recent month (12-2 or 12-1), 1–6 month holding. **Horizon fit is genuinely good.**
**DECAY EVIDENCE:** Chen & Velikov report momentum post-2005 at **16 bp/month with a standard error of 30–60 bp** — i.e. indistinguishable from zero. Chen & Welch describe momentum as essentially dead in the top 90% of market cap. Daniel & Moskowitz document that momentum crashes occur in panic states following market declines when market volatility is high, and that the losses are severe and persistent enough to wipe out years of gains — crash risk that a 20–50 name book cannot diversify away.
**Variants:** Residual/idiosyncratic momentum (Blitz, Huij & Martens) and industry momentum (Moskowitz & Grinblatt) are the best-supported refinements, with idiosyncratic momentum generally showing better risk-adjusted performance and less crash exposure. George & Hwang's 52-week-high variant (below) dominates both in their tests.
**DATA OBTAINABILITY:** Trivially free — price history only.
**IMPLICATION FOR THE APP:** **This is where the small-universe problem bites hardest.** See the dedicated section below. Momentum is a pure relative-rank signal: "this stock rose more than other stocks." On a 20–50 name watchlist the top-ranked name may still be an absolute loser. The prior design note that momentum "cannot be used as a per-ticker absolute signal without reformulation as a relative rank" is correct, and reformulating it as a rank within 30 names does **not** recover the published effect — it recovers something untested.

---

### 9. Small-universe transferability — the structural constraint

**CLAIM:** Published cross-sectional evidence on small portfolios establishes that you can *hold* few stocks, not that you can *rank* few stocks; these are different claims and only the first is supported.
**SOURCE:** Siganos, "Can small investors exploit the momentum effect?," summarised at Quantpedia, https://quantpedia.com/strategies/momentum-effect-in-stocks-in-small-portfolios — **vendor summary of an academic paper**. Structural logic from Grinold's fundamental law of active management (IR ≈ IC × √breadth), Grinold & Kahn, *Active Portfolio Management*
**EVIDENCE STRENGTH:** Moderate (the distinction is logically forced; direct empirical tests of ranking within 20–50 names are absent from the literature)
**HORIZON:** N/A
**DECAY EVIDENCE:** Siganos's UK strategy (1988–2006) holds 10 long and 10 short, equal-weighted, ranked on 12-month returns, rebalanced yearly, net return 2.34%/month per Table 6 — **but the ranking universe is all UK-listed companies excluding the smallest 25%.** The small number is the holding count, not the ranking count. Quantpedia's own out-of-sample backtest shows "slightly negative performance." Combined winner/loser bid-ask spread in the source is 8.03%. Quantpedia also cites Piras (US data) reporting that portfolios under 10 stocks "show clear dependency on the given universe constituents."
The structural argument: the fundamental law says information ratio scales with √(number of independent bets). Going from 3,000 ranked names to 30 cuts √breadth by a factor of ten. An effect with a published information ratio of 0.5 on a full cross-section is an information ratio of ~0.05 on 30 names, before any decay haircut and before costs. Separately, decile sorts on 30 names put **three stocks per decile** — the top-decile return is then dominated by idiosyncratic variance, not the signal.
**DATA OBTAINABILITY:** N/A
**IMPLICATION FOR THE APP:** This is the most important constraint in the strand and it applies to **every** rank-based signal: momentum, 52-week high, short interest, revisions, accruals, PEAD-as-decile-sort. The practical consequences:
(a) **Prefer signals with an absolute interpretation over relative ranks.** SUE has one (earnings beat expectations by *k* standard deviations — meaningful without reference to other stocks). Gross profitability has one. Momentum does not. 52-week high nearness is intermediate — "price is 97% of its 52-week high" is absolute, which is why George & Hwang's signal is more transferable than Jegadeesh-Titman.
(b) **Where a rank is unavoidable, rank against a broad external universe and read off the watchlist name's percentile**, rather than ranking within the watchlist. This preserves the published construction. It also means the system must compute the signal for thousands of names even though it only trades 30 — which is a real engineering cost but is free data for price-based signals.
(c) **Expect the effective signal strength to be a fraction of the published number**, over and above the ~40% publication haircut.

---

### 10. 52-week high, idiosyncratic volatility and low beta

**CLAIM:** Nearness to the 52-week high predicts returns and dominates both individual-stock and industry momentum in joint tests; it has the useful property of being an absolute rather than relative measure.
**SOURCE:** George & Hwang, "The 52-Week High and Momentum Investing," *Journal of Finance* 59(5), Oct 2004, https://www.bauer.uh.edu/tgeorge/papers/gh4-paper.pdf — **peer-reviewed**
**EVIDENCE STRENGTH:** Moderate (strong original; no clean recent re-test found)
**HORIZON:** Six-month holding in the main (6,6) tests; robustness at (6,12), (12,6), (12,12). **Good fit.**
**DECAY EVIDENCE:** Weak evidence either way for recent periods. Original: winner-minus-loser 0.45%/month (t = 2.00) including January, 1.23% excluding it; Fama-MacBeth 0.65%/month with January, 1.06% without. Sample July 1963–Dec 2001. Notably, **no long-run reversal** — 52-week winners continue rising in year two, whereas Jegadeesh-Titman and Moskowitz-Grinblatt winners reverse. The January dependence is a concern: more than half the effect is non-January seasonality in the (6,6) test.
**DATA OBTAINABILITY:** Free — price history only. The ratio (current price / 52-week high) is trivially computable and, crucially, **interpretable per-ticker without a cross-section.**
**IMPLICATION FOR THE APP:** The best small-universe transferability of any momentum-family signal, because it is absolute. Worth including as a secondary signal. But recognise there is no published post-2015 test, and Chen & Welch's "momentum is dead" finding plausibly extends to it.

**On idiosyncratic volatility and betting-against-beta:** Both are in the IVOL/low-risk family and both are **volatility-related rather than directional** — they predict that low-IVOL and low-beta stocks outperform *on a risk-adjusted basis*, which is a portfolio-construction result, not a per-ticker "this will go up" signal. Novy-Marx & Velikov ("Betting Against Betting Against Beta," *Journal of Financial Economics*, 2022) show BAB's performance depends heavily on its non-standard construction — it uses a rank-based weighting scheme and leverages the long leg, and the alpha largely disappears under conventional construction, with much of what remains coming from microcaps. **EVIDENCE STRENGTH: Weak for directional use. Verdict: exclude.** These belong in the volatility strand, not here, and the system already has volatility coverage.

---

### 11. Replication and decay — where the balance of evidence sits

This is the most contested area and the brief rightly asks not to assume a single number. There are four positions and they are partly talking past each other.

**Position A — most of it fails (Hou/Xue/Zhang).**
**SOURCE:** Hou, Xue & Zhang, "Replicating Anomalies," *Review of Financial Studies* 33(5), 2020, https://global-q.org/uploads/1/2/2/6/122679606/houxuezhang2020rfs.pdf — **peer-reviewed**
**CLAIM:** Of 452 anomalies, ~65% fail to replicate at |t| ≥ 1.96 using value-weighted returns and NYSE breakpoints that suppress microcaps. **EVIDENCE STRENGTH: Strong but methodologically contested.**

**Position B — the replication crisis is an artefact of method (Jensen/Kelly/Pedersen).**
**SOURCE:** Jensen, Kelly & Pedersen, "Is There a Replication Crisis in Finance?," *Journal of Finance* 78(5), 2023, 2465–2518, https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13249 — **peer-reviewed**
**CLAIM:** 153 factors across 93 countries; Bayesian replication rate **84.9% globally**, 84.0% in the US on CAPM alphas, 77.3% under Benjamini-Yekutieli multiple-testing correction. They decompose the gap to HXZ: capped value weights +8.5 points, longer sample +4.3, one-month holding +4.0, added factors +2.4, other construction +2.7. Replication holds across size groups (mega 77.3%, large 81.5%, micro 81.5%, nano 71.4%) — **a direct rebuttal of "it's all microcaps."** Factors cluster into **13 themes**, 10 of which exceed 75% replication (exceptions: seasonality, leverage, size). Post-publication alpha falls from 0.45% to 0.31%/month, about one-third, which they argue is exactly what Bayesian shrinkage predicts. **EVIDENCE STRENGTH: Strong.**

**Position C — publication bias is small (Chen/Zimmermann).**
**SOURCE:** Chen & Zimmermann, "Publication Bias in Asset Pricing Research," arXiv:2209.13623, https://arxiv.org/html/2209.13623v3 — **working paper**; underlying data: Chen & Zimmermann, "Open Source Cross-Sectional Asset Pricing," *Critical Finance Review* 11, 2022
**CLAIM:** Of 207 published and replicated predictors, **183 (88%) have |t| ≥ 2.0**. Publication bias accounts for only **10–15%** of in-sample returns. False discovery rate estimates range 0.4%–6.3%. They argue HXZ's failures are misclassifications: only ~26% of HXZ's strategies were clearly significant in the original papers, and microcaps explain only about a third of the failures (failure rate falls 65% → 43.1% when microcaps are included). On Harvey/Liu/Zhu: the t ≈ 3.0 hurdle is highly conservative and mainly produces *insignificant* findings rather than *false* ones — they estimate ~81% of those screened-out predictors are nonetheless true. **EVIDENCE STRENGTH: Strong.**

**Position D — the decay is real and the survivors are near zero net of costs (McLean/Pontiff, Chen/Velikov, Chen/Welch).**
**SOURCES:** McLean & Pontiff, "Does Academic Research Destroy Stock Return Predictability?," *Journal of Finance* 71(1), 2016, https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf — **peer-reviewed**: 26% decay out of sample pre-publication, **58% decline post-publication**. Chen & Velikov (JFQA 2023): 120 anomalies, post-publication net **−3 bp/month** under academic implementations, **+13 bp** under cost-optimised ones; **post-2005: 8 bp (SE 4) equal-weighted, 4 bp (SE 3) value-weighted**; size/BM/momentum post-2005 at −26/+33/+16 bp with standard errors of 30–60 bp; **only 11 of 120 clear |t| > 2.** Chen & Welch (2026): post-2005 large-cap median 7 bp/month, t = 0.45; restricting to post-2005 cuts median return ~60%, restricting to top-90% market cap cuts it ~half, **together ~85%**. **EVIDENCE STRENGTH: Strong.**

**Where the balance actually sits.** Positions B/C and D are not in conflict once you separate two questions:
1. *Did the original authors find something real?* Balance of evidence: **yes, mostly.** The Jensen/Kelly/Pedersen and Chen/Zimmermann rebuttals of HXZ are convincing. 80–88% replication is the better estimate than 35%.
2. *Is there tradeable directional alpha left in liquid US stocks today?* Balance of evidence: **mostly no.** Chen/Velikov and Chen/Welch are not contradicted by B/C — JKP's 84.9% is a CAPM-alpha, one-month-holding, 93-country, all-size-groups number, and Chen/Zimmermann's 88% is an in-sample t-stat replication, not a statement about current net returns.

**The working haircut assumption of ~40% is too optimistic for this application.** It is roughly right for the published-to-first-out-of-sample transition (McLean/Pontiff's 26–58% bracket; JKP's one-third). It is far too small for published → post-2005 → large-cap → net of retail costs → 30-name universe. Chen & Welch's own stacking gives ~85% before costs and before the breadth penalty. **A haircut of 80–90% is the defensible assumption for this product's operating conditions.**

---

### 12. Signal combination

**CLAIM:** Combining multiple signals into a composite inflates test statistics severely, even when every input signal is pure noise; the required significance threshold is several times the conventional one.
**SOURCE:** Robert Novy-Marx, "Testing strategies based on multiple signals," University of Rochester working paper, March 2016, https://mysimon.rochester.edu/novy-marx/research/MSES.pdf — **working paper by a leading researcher**
**EVIDENCE STRENGTH:** Strong (simulation-based, mechanism is unambiguous)
**HORIZON:** N/A
**DECAY EVIDENCE:** Simulations on random signals over CRSP 1995–2014. Empirical 5% critical t-statistics for best-k-of-n composites: best 2-of-10 ≈ 3.5; best 3-of-20 > 4; best 4-of-40 ≈ 5. Some constructions require **t > 7** for 5% significance. Expressed as equivalent single-signal search: picking the best 3 of 20 equal-weighted signals is about as biased as picking the single best of ~1,780 signals; best 5 of 40 ≈ best of ~480,000. Equal-weighting inflates less than signal-weighting (which gives more freedom to overfit). His prescriptions: evaluate each signal's *marginal* contribution individually; apply Bonferroni over **every signal considered, not just those used**; with equal weights, the weaker half of candidates add little.
**DATA OBTAINABILITY:** N/A
**IMPLICATION FOR THE APP:** Decisive for design. **Do not build a composite score by searching over weightings or signal subsets.** Fix a small number of signals *a priori* on the basis of individual published evidence, equal-weight them, and never tune. If the system tries five direction signals and keeps three, the honest significance bar for the composite is around t = 4, not t = 2. This also means any in-app backtesting UI is actively dangerous: it invites exactly the search Novy-Marx shows is fatal.

**On how much independent information remains:** Feng/Giglio/Xiu (JF 2020) find only 5 of 15 recent factors add incremental explanatory power beyond 135 controls. Jensen/Kelly/Pedersen reduce 153 factors to **13 themes**, of which 10 get significantly positive weight in the ex-post tangency portfolio (exceptions: profitability, investment, size — note this is about *marginal tangency weight*, not about whether the factor is real). Stambaugh & Yuan's mispricing-factor work (*Review of Financial Studies* 30(4), 2017) compresses 11 anomalies into 2 composite mispricing factors. **The consistent message: the effective number of independent directional signals is in the single digits, probably 3–6.** A system using four signals is not meaningfully under-diversified relative to one using twenty; it is just honest about it.

---

## DIRECTION SIGNAL TABLE

| Signal | Evidence | Horizon fit (1–6mo) | Post-2015 survival | Small-universe (20–50) transferability | Data cost | Verdict |
|---|---|---|---|---|---|---|
| **PEAD / SUE (time-series, EDGAR)** | Strong historical, Moderate recent | **Excellent** (60–90d drift ↔ 60–90 DTE) | **Contested.** Zero after 2017 (Kettell et al.); +2.0pp/60d large caps 2023–26 but +0.5pp in 2025–26 (Gupta, unrefereed) | **Good** — SUE is absolute (σ units), no cross-section needed | **Free** (EDGAR XBRL) | **INCLUDE, small weight, monitored** |
| **PEAD "stayer" filter** (consecutive extreme-decile SUE) | Moderate, untested OOS | Excellent | Mechanism documented 1974–2020; stayers earn 14.1% | **Good** — absolute, per-ticker | **Free** (EDGAR XBRL) | **INCLUDE as refinement to PEAD** |
| **Analyst revision momentum** | Moderate | **Good** (90d+ documented) | **Unknown** — no clean post-2015 test published | Moderate — usable as z-score of revision magnitude, semi-absolute | **Problem.** IBES (WRDS, unconfirmed) or vendor with no point-in-time integrity | **DEFER** — capture forward, deploy later |
| **Gross / cash-based operating profitability** | **Strong** (FGX 2020; Chen & Welch survivor; ~24bp/mo post-2005 median) | **Poor as timing**, good as screen | **Yes** — the main survivor | **Good** — absolute ratio, per-ticker | **Free** (EDGAR XBRL) | **INCLUDE as universe screen** |
| **Net equity / external financing** | Moderate-Strong (Chen & Welch survivor) | Moderate (annual) | **Yes** | Good — absolute | **Free** (EDGAR XBRL) | **INCLUDE, small weight** |
| **52-week high nearness** | Moderate | **Good** (6-mo holding) | **Unknown**; momentum-family death likely extends | **Best of momentum family** — absolute ratio | **Free** (prices) | **INCLUDE, small weight** |
| **Cross-sectional price momentum (12-2)** | Strong historical | Good | **No** — 16bp/mo, SE 30–60bp post-2005 | **Poor** — pure relative rank; √breadth penalty ~10× | Free | **EXCLUDE** |
| **Residual / industry momentum** | Moderate | Good | Weak; no clean recent test | Poor — still a rank; industry momentum needs sector breadth the watchlist lacks | Free | **EXCLUDE** |
| **Short interest ratio / days-to-cover** | Moderate | **Poor** (1-month) | Plausibly; but value-weighted insignificant since 1988–2002 | Moderate — SI% is absolute | **Free** (FINRA, bi-monthly, ~8d lag) | **INCLUDE as risk filter only, not direction** |
| **Borrow fee / utilisation** | **Strong** (strongest single predictor found) | **Poor** (1-month) | Yes, 2006–2019 sample | Good — absolute | **Not obtainable** (Markit discontinued continuous measure) | **EXCLUDE — unobtainable** |
| **Accruals (Sloan)** | Strong that it **died** | Poor (annual) | **No** — Management Science 2011 demise | Good (absolute) but irrelevant | Free (EDGAR XBRL) | **EXCLUDE** |
| **Book-to-market / value** | Contested | Poor (multi-year) | **No** in liquid names (Chen & Welch); Arnott et al. dissent | Moderate | Free | **EXCLUDE** |
| **Idiosyncratic volatility** | Weak for direction | N/A | Contested | N/A | Free | **EXCLUDE — not directional** |
| **Betting-against-beta / low beta** | Weak (construction-dependent per Novy-Marx & Velikov) | N/A | Contested | N/A | Free | **EXCLUDE — not directional** |
| **EDGAR filing-language change ("Lazy Prices")** *(existing)* | Moderate | Good | — | Good (absolute) | Free | Retain — outside this strand |
| **Opportunistic insider trades** *(existing)* | Moderate, post-2017 decay noted | Good | Decaying | Good (absolute) | Free (Form 4) | Retain — outside this strand |

---

## RECOMMENDED DIRECTION STACK

Four signals, all free, all EDGAR or price-derived, all with an absolute per-ticker interpretation. Fixed weights, set in advance, never tuned.

**1. SUE with a persistence overlay (primary, weight ~0.40)**
Compute SUE as the YoY change in quarterly diluted EPS scaled by the standard deviation of that change over the prior 8 quarters, from EDGAR XBRL. Overlay the Kettell/McInnis/Zhao persistence insight: weight the signal up when the firm was also in the same extreme SUE region in the prior quarter ("stayer"), down when it has just moved there. Fire on announcements, hold to ~60–90 DTE expiry.
*Honest expectation:* The strongest published evidence says this is zero after 2017. The strongest recent evidence (unrefereed) says ~2pp over 60 days in large caps, decaying to 0.5pp. Build it with an explicit kill criterion: if the rolling four-quarter top-minus-bottom spread on your own tracked watchlist reaches zero, drop the weight to zero.

**2. Profitability screen (gating, not weighted)**
Gross profitability and cash-based operating profitability from EDGAR XBRL, computed across a broad external universe (Russell 1000 or similar) and read off as a percentile for each watchlist name. Use it to **gate** which names are eligible for long directional exposure rather than to score them. This is the only category Chen & Welch, Feng/Giglio/Xiu and the Novy-Marx original all agree survives.
*Honest expectation:* ~24 bp/month median post-2005 pre-shrinkage; ~6 bp after empirical-Bayes shrinkage. As a gate rather than a signal, its job is to avoid bad longs, not generate alpha.

**3. 52-week high nearness (secondary, weight ~0.30)**
Current price / trailing 252-day high. Absolute, free, no cross-section required, dominated momentum in the original joint tests, and — unusually — shows no long-run reversal.
*Honest expectation:* 45–65 bp/month in 1963–2001; unknown today; probably substantially less. Half the original effect is non-January seasonality, which is a warning sign.

**4. Net external/equity financing (tertiary, weight ~0.30)**
From the EDGAR cash flow statement. One of Chen & Welch's named survivors, independent of profitability and of PEAD, free, absolute.

**Risk filters (not signals, no weight):**
- FINRA short interest percentile — suppress long directional exposure on heavily shorted names. This is the obtainable shadow of the borrow-fee signal and should be used defensively, not offensively.
- Known earnings date within the contract's life — flag, since SUE-driven positions want the announcement inside the window and non-SUE positions generally do not.

**Explicitly excluded from the stack and why:** momentum (relative rank, dead post-2005), accruals (dead), value (dead at this horizon), IVOL/BAB (not directional), borrow fee (unobtainable), revision momentum (deferred pending self-captured point-in-time data).

**Expected combined strength, stated honestly.**
The published gross numbers for these four, naively combined, would suggest something in the region of 50–100 bp/month. That number should not be used. Stacking the documented haircuts:
- Post-2005 / liquid-universe restriction: **~85% reduction** (Chen & Welch's own decomposition)
- Breadth penalty from 3,000 → 30 names: a further factor of roughly **√100 = 10** on information ratio, though not a simple multiplier on return
- Novy-Marx composite inflation: the combined backtest will look better than the truth by a factor equivalent to searching hundreds of signals, unless weights are genuinely fixed in advance
- Retail options transaction costs: wide spreads on 60–180 DTE contracts, typically 2–5% of premium round-trip, which is an order of magnitude above the 10–30 bp equity costs in the Gupta analysis

**My honest estimate is that this stack produces an expected directional edge indistinguishable from zero at any sample size the developer will accumulate, and that the realistic best case is a modest improvement in the hit rate of trades selected for other reasons — perhaps shifting a 50% directional accuracy to 52–54%, which options transaction costs will consume.**

This should change how the direction module is positioned in the product. It is defensible as **a filter that removes obviously bad directional bets** (unprofitable firms, firms with deteriorating earnings persistence, heavily shorted names) and as **a structured way to make the user's own view explicit and falsifiable**. It is not defensible as an alpha engine, and the capstone write-up will be stronger for saying so than for claiming otherwise.

---

## DISCONFIRMING EVIDENCE

**1. The central finding of this strand is disconfirming.** Chen & Welch (2026) find the median published anomaly earns 7 bp/month with t = 0.45 in large-cap post-2005 samples, and that value and momentum are dead there. Chen & Velikov (JFQA 2023) find post-2005 cost-optimised net returns of 4–8 bp/month and only 11 of 120 anomalies clearing |t| > 2. If these are right, the entire premise that a direction stack can be assembled from published equity literature is wrong.

**2. PEAD — the strand's highest-priority candidate — may already be gone.** Kettell, McInnis & Zhao state hedge returns are indistinguishable from zero after 2017, and critically, the decay is concentrated in **non-microcaps** (t = −3.57) while the microcap trend is insignificant. The product's universe is the one where PEAD died. Worse, the surviving component is the [+2, +6] day window, which 60–180 DTE contracts cannot trade.

**3. Cross-sectional evidence does not establish small-universe transferability, and nobody has tested it.** Every decile-sort result in this literature ranks thousands of names. Siganos's "small portfolio" result holds 10 names but ranks the entire UK market. Quantpedia's own out-of-sample extension of it is slightly negative. Piras finds portfolios under 10 stocks show clear dependence on universe constituents. The fundamental law implies a √(3000/30) ≈ 10× information ratio penalty. **There is no published evidence that any of these signals works when the ranking universe is 30 names, and the structural argument says it should not.**

**4. Composite scoring is a trap with quantified severity.** Novy-Marx shows best-3-of-20 equal-weighted composites require t > 4 for genuine 5% significance, and are as biased as searching ~1,780 single signals. Any in-app signal-weighting or backtest-tuning feature makes the system's output worse while making it look better.

**5. Costs likely consume whatever remains at retail options scale.** The Gupta analysis finds PEAD net returns falling from 7.9% gross to 2.1% at 30 bp one-way *equity* costs. Options spreads on 60–180 DTE contracts for mid-cap names are routinely 2–5% of premium round-trip — 10–20× that. Chen & Velikov additionally note that short-sale costs (10–20 bp/month) and price impact are *excluded* from their already-near-zero figures and would likely consume the remainder.

**6. The strongest single predictor found is the one that cannot be obtained.** Engelberg et al. rank loan fee first of 102 anomalies on return, Sharpe, and hit rate, with 72% of its content unspanned by other anomalies. Markit's continuous measure is no longer distributed; even the academic authors resort to imputing from a 1–10 bucket score. The prior finding that option-implied predictability is a borrow-fee proxy is thereby confirmed *and* rendered unexploitable.

**7. The famous anomaly most attractive on data-cost grounds is dead.** Accruals is trivially computable from EDGAR XBRL and was killed in *Management Science* in 2011. The temptation to include cheap-to-compute signals regardless of evidence is exactly the failure mode this finding warns against.

**8. Short interest's directional content is a small-cap phenomenon.** Asquith, Pathak & Ritter: 215 bp/month equal-weighted versus 39 bp/month value-weighted and **insignificant**. On a liquid watchlist the signal is the insignificant one.

**9. Counter-disconfirming (for balance):** Jensen/Kelly/Pedersen (JF 2023, 84.9% Bayesian replication across 93 countries, holding across all size groups including mega-caps) and Chen/Zimmermann (88% of 207 predictors at |t| ≥ 2; publication bias only 10–15% of in-sample returns; FDR under 6%) are serious peer-reviewed evidence that the underlying effects are real. The reconciliation — effects are real but arbitraged out of liquid US stocks at tradeable net levels — is my reading, not a finding either paper makes.

---

## OPEN QUESTIONS

1. **Is the Gupta 2023–26 out-of-sample PEAD result reproducible?** It is the only recent large-cap evidence that PEAD lives, it is unrefereed, AI-assisted, self-declares probable survivorship bias, and contains an internal inconsistency between its headline 1.7 pp and its chart commentary. This is the single highest-value thing to replicate independently, and it is replicable from free EDGAR data.
2. **Does the "stayer" filter survive out of sample?** Kettell/McInnis/Zhao's 14.1% (t = 25.85) for consecutive-extreme-decile firms is in-sample over 1974–2020 and was not proposed as a trading strategy. No one has tested it post-2020. It is cheap to test and is the most interesting unexploited idea in the strand.
3. **Can a point-in-time analyst consensus series be built from free APIs going forward, and does it reproduce IBES?** Worth a direct comparison if WRDS IBES access is confirmed — capture FMP/Finnhub consensus daily for 90 days and compare against IBES snapshots for the same dates.
4. **What is the actual information-ratio penalty from a 30-name ranking universe?** The √breadth argument is theory. A direct simulation — compute a signal on the full Russell 1000, then evaluate it restricted to random 30-name subsets — would quantify it and is entirely free to run. This would be a genuinely novel contribution for a capstone.
5. **Does ranking watchlist names against a broad external universe recover published effects better than ranking within the watchlist?** Logically yes, but the magnitude is unknown and testable.
6. **Does profitability as a gate rather than a score actually improve outcomes?** The literature evaluates it as a long-short factor, not as an eligibility filter. The filter use is untested.
7. **Is there any direction signal in the 1–6 month band with an absolute per-ticker interpretation that this strand missed?** The absolute-vs-relative distinction is underexplored in the literature precisely because academic work always has a full cross-section available.
8. **Do the Chen & Welch survivors overlap with what the system already has?** Their list includes a realised-implied volatility spread, which touches the existing options-pricing strand — worth checking whether the system is already capturing one of the few survivors without labelling it as such.

---

## TOP 10 SOURCES, RANKED

1. **Chen, A. Y. & Welch, I. (2026). "What Useful Alphas?" arXiv:2607.06502.** https://arxiv.org/pdf/2607.06502 — *Working paper.* The most directly decision-relevant source found. Post-2005 large-cap median of 7 bp/month (t = 0.45) across ~200 anomalies; names the specific survivors (profitability, financing); quantifies the stacked haircut at ~85%. If you read one thing, read this.
2. **Chen, A. Y. & Velikov, M. (2023). "Zeroing in on the Expected Returns of Anomalies." *Journal of Financial and Quantitative Analysis*.** https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf — *Peer-reviewed.* 120 anomalies, net of costs, post-2005: 8 bp EW / 4 bp VW; 11 of 120 at |t| > 2. The cost-adjusted version of the same message, peer-reviewed.
3. **Kettell, L., McInnis, J. & Zhao, W. (2022). "Why Has PEAD Declined Over Time? The Role of Earnings News Persistence." UT Austin WP.** https://business.columbia.edu/sites/default/files-efs/imce-uploads/CEASA/Events%20Page/PEAD_Declined_over_time.pdf — *Working paper.* Zero after 2017; decay concentrated in non-microcaps; the persistence/"stayer" mechanism is the most actionable idea in the strand.
4. **Jensen, T. I., Kelly, B. & Pedersen, L. H. (2023). "Is There a Replication Crisis in Finance?" *Journal of Finance* 78(5), 2465–2518.** https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13249 — *Peer-reviewed.* The strongest case that the literature is sound: 84.9% Bayesian replication, 93 countries, holds across size groups, 13 themes. Essential counterweight to #1 and #2.
5. **Novy-Marx, R. (2016). "Testing strategies based on multiple signals." Rochester WP.** https://mysimon.rochester.edu/novy-marx/research/MSES.pdf — *Working paper.* Quantifies composite-scoring bias: best-3-of-20 needs t > 4. Directly constrains how the direction module may be built.
6. **Engelberg, J., Evans, R., Leonard, G., Reed, A. & Ringgenberg, M. (2020). "The Loan Fee Anomaly: A Short Seller's Best Ideas."** https://uncipc.org/wp-content/uploads/2021/05/The-Loan-Fee-Anomaly.pdf — *Working paper.* Loan fee ranks first of 102 anomalies, 72% unspanned, 48 bp/month net of borrow costs — and is unobtainable. Resolves the borrow-fee-proxy question definitively.
7. **Chen, A. Y. & Zimmermann, T. (2022/24). "Publication Bias in Asset Pricing Research." arXiv:2209.13623.** https://arxiv.org/html/2209.13623v3 — *Working paper.* 88% of 207 predictors at |t| ≥ 2; bias only 10–15%; dismantles both HXZ's failure count and HLZ's t = 3 hurdle. The best treatment of how much to haircut.
8. **Feng, G., Giglio, S. & Xiu, D. (2020). "Taming the Factor Zoo." *Journal of Finance* 75(3).** https://stefanogiglio.org/papers/feng-giglio-xiu-jf-2020.pdf — *Peer-reviewed.* Only 5 of 15 recent factors add incremental information, 4 of them profitability/investment. Independent corroboration of the one survivor category.
9. **Green, J., Hand, J. R. M. & Soliman, M. T. (2011). "Going, Going, Gone? The Apparent Demise of the US Accruals Anomaly." *Management Science* 57(5), 797–816.** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1501020 — *Peer-reviewed.* The model of how to report a dead anomaly, and directly removes an otherwise attractive EDGAR-computable candidate.
10. **George, T. J. & Hwang, C.-Y. (2004). "The 52-Week High and Momentum Investing." *Journal of Finance* 59(5).** https://www.bauer.uh.edu/tgeorge/papers/gh4-paper.pdf — *Peer-reviewed.* The one momentum-family signal with an absolute per-ticker interpretation, hence the only one plausibly transferable to a 30-name watchlist.

**Also consulted:** Fink (2020) PEAD review (Graz WP 2020-04); Gupta (2026) PEAD out-of-sample (practitioner blog); Chan/Jegadeesh/Lakonishok (1996) *JF*; Huang (2022) UCLA dissertation on revisions; Asquith/Pathak/Ritter (2005) *JFE*; Hou/Xue/Zhang (2020) *RFS*; McLean & Pontiff (2016) *JF*; Daniel & Moskowitz (2016) *JFE*; Arnott/Harvey/Kalesnik/Linnainmaa (2021) *FAJ*; Stambaugh & Yuan (2017) *RFS*; Novy-Marx & Velikov (2022) *JFE* on BAB; Siganos via Quantpedia (vendor); FINRA Equity Short Interest documentation.
