# Research Strand 15 — Retail Implementation of the Overlay Return Decomposition

**Date:** 11 November 2026
**Scope:** Can a retail trader isolate the compensated short-volatility component of a covered call and strip the uncompensated equity-timing component? Index products and single names.
**Out of scope (flagged only):** tax. Covered by another strand: single-name variance risk premium magnitude, tradeable universe.

---

## 0. The size of the prize (framing arithmetic)

Before anything else, it is worth fixing how much money is actually at stake, because every cost estimate below has to be measured against it.

Israelov & Nielsen's hedged BXM delivers 5.1% excess return at 9.2% volatility. Their "passive equity" component delivers 3.5% at 8.5% volatility. Scaling passive equity up to 9.2% volatility gives 3.79%. So the entire economic value of the overlay — the compensated short-volatility sleeve — is worth about **130 bps per year, gross, at full BXM notional** (one ATM monthly call per unit of equity held). Equivalently, a Sharpe gain from 0.41 to about 0.55.

*(Own arithmetic from Israelov & Nielsen 2015 Tables 1 and 6. Labelled as such.)*

That is the ceiling. Retail option spreads, futures spreads, commissions and granularity error all come out of 130 bps. Any proposal whose frictions exceed roughly 60–70 bps/yr at full notional is not worth doing.

---

## 1. Israelov's own body of work and its follow-ups

### CLAIM 1.1 — The anchor decomposition is peer-reviewed, and the hedged improvement is specifically a *risk-reduction* result, not a return result.
- **SOURCE:** Roni Israelov & Lars N. Nielsen, "Covered Calls Uncovered," *Financial Analysts Journal* 71(6), 2015, pp. 44–57. DOI 10.2469/faj.v71.n6.1. PDF mirrors: [AQR](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/Covered-Calls-Uncovered.pdf), [alternate](https://abramofranchetti.github.io/FireSWR/covered_call/Covered%20Calls%20Uncovered.pdf). Journal page: [CFA Institute RPC](https://rpc.cfainstitute.org/research/financial-analysts-financial-analysts-journal/2015/covered-calls-uncovered).
- **EVIDENCE STRENGTH:** Strong (peer-reviewed, 19-year sample, replicated internationally — see 1.4).
- **DETAIL:** Table 6 (BXM, 25 Mar 1996 – 31 Dec 2014): excess return 4.9% unhedged → **5.1% hedged** (only +20 bps of return); volatility 11.4% → 9.2%; Sharpe 0.37 → 0.52; downside beta 0.85 → 0.60; upside beta 0.46 → 0.49. BXY (2% OTM): Sharpe 0.41 → 0.46, volatility 13.3% → 12.4%, downside beta 0.89 → 0.78.
- **IMPLICATION FOR THE BUILD:** The headline 0.37 → 0.52 is **four-fifths volatility reduction and one-fifth return**. An investor who merely wants less volatility can get it by holding less equity, for free. The hedge is only worth paying for because it removes volatility *without* giving up the short-vol premium. The build must therefore present the hedged overlay against a correctly-scaled passive-equity benchmark, not against the raw index, or it will flatter itself exactly the way the overlay-marketing literature does.

### CLAIM 1.2 — The methodology is daily Black–Scholes delta, hedged with index futures, against a *constant* target delta (not zero).
- **SOURCE:** Israelov & Nielsen 2015, methodology section and Table 6 notes.
- **EVIDENCE STRENGTH:** Strong (explicit in the paper).
- **DETAIL:** Each day they compute the written call's Black–Scholes delta at an assumed 18% implied volatility. "Active exposure" = today's delta minus the *expected delta on rebalance dates* — 0.5 for ATM, 0.3 for the 2% OTM variant. The active exposure is offset with S&P 500 futures. Worked example (30 Sep 2014): BXM short a 2020-strike call expiring 17 Oct with delta 0.15 versus an expected 0.5, hedged with a short futures position of **35% of NAV**. Mean absolute active exposure across the sample is **0.21**. The authors say equity exposure is easily hedged with futures or ETFs.
- **IMPLICATION FOR THE BUILD:** The target is not delta-neutrality. The build must hold a *constant* equity delta (0.5 for ATM writing, 0.7 for 2%-OTM writing) and trade only the deviation. The hedge is **short futures when the market has fallen** (call delta down, portfolio delta up) and **long futures when the market has risen**. Average hedge size is ~21% of the written notional, peaking around 35–45%.

### CLAIM 1.3 — The timing risk is concentrated at the end of the option's life, which is the single most actionable fact in the strand.
- **SOURCE:** Israelov & Nielsen 2015.
- **EVIDENCE STRENGTH:** Strong.
- **DETAIL:** Delta starts tightly clustered at 0.5 and disperses toward 0 or 1 as expiry approaches. Timing exposure is smallest immediately after writing and largest just before expiry; **on the day before expiration the timing position carries nearly the same risk as the passive-equity component.** Timing's share of total risk was stable across sub-periods (23%, 28%, 24%).
- **IMPLICATION FOR THE BUILD:** Closing or rolling the written option before the final stretch of its life removes a disproportionate share of timing risk for the cost of one extra option trade — no futures account needed. This is the cheapest single lever available to retail. See the Implementation Ladder for a quantified (own-arithmetic) estimate.

### CLAIM 1.4 — The decomposition replicates out-of-sample across 11 countries, and that replication is the only place the hedged result has been costed.
- **SOURCE:** Roni Israelov, Matthew Klein & Harsha Tummala, "Covering the World: Global Evidence on Covered Calls," *Journal of Risk*, 2017 (working-paper version June 2017). [Journal of Risk](https://www.risk.net/journal-of-risk/5943741/covering-the-world-global-evidence-on-covered-calls); [AQR working paper page](https://www.aqr.com/Insights/Research/Working-Paper/Covering-the-World-Global-Evidence-on-Covered-Calls); summary: [CXO Advisory](https://www.cxoadvisory.com/equity-options/covered-equity-index-calls-worldwide/).
- **EVIDENCE STRENGTH:** Strong for the replication; Moderate for the cost figures (reported via a reliable secondary summary; the AQR PDF is robots-blocked).
- **DETAIL:** 11 global equity indices, options data to Sep 2015, common start Jan 2006. Average component statistics: equity 3.6% / 11.5% vol / 0.31 Sharpe; **short volatility 1.9% / 2.7% vol / 0.74 Sharpe**; **equity timing −0.3% / 5.6% vol** (negative return, pure cost). Risk-managed version hedges deviations of dynamic exposure from 0.5 using index futures, daily.
  **The cost accounting — the most important numbers in this strand:**
  - Monthly index-call selling frictions ≈ **0.28%/yr**, which lowers the basic covered-call Sharpe from **0.35 → 0.33** (underlying index 0.32).
  - Daily futures hedge adjustment costs lower the risk-managed Sharpe from **0.51 → 0.46**.
  - Cap-weighted risk-managed variant: 0.57 gross.
  - So **net of institutional costs: hedged 0.46 vs unhedged 0.33, a +0.13 Sharpe gain, versus a +0.16 gross gain. About 81% of the improvement survives costs.** The daily hedge itself costs ~0.05 of Sharpe ≈ 46 bps/yr at 9.2% volatility.
- **IMPLICATION FOR THE BUILD:** This is the benchmark to beat. An institution pays ~46 bps/yr to run the daily futures hedge. Section 3 shows retail micro-futures costs are *an order of magnitude lower* than this, because institutions move size and pay market impact; a single retail account moving one or two MES contracts pays only spread plus commission. The hedged overlay therefore looks *more* attractive at retail scale than at institutional scale, which is a genuinely surprising and build-relevant conclusion.

### CLAIM 1.5 — Israelov's earlier paper supplies the exact static equivalence that bounds every "static approximation" idea.
- **SOURCE:** Roni Israelov & Lars N. Nielsen, "Covered Call Strategies: One Fact and Eight Myths," *Financial Analysts Journal* 70(6), 2014, pp. 23–31. [AQR PDF](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/FAJ-Covered-Call-Strategies-One-Fact-and-Eight-Myths.pdf); [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2014/covered-call-strategies-one-fact-and-eight-myths).
- **EVIDENCE STRENGTH:** Strong.
- **DETAIL:** The one fact: a covered call is long equity plus short volatility. Key quantitative content: an ATM call has delta ~0.49, so the covered call is ~50% index exposure; **with zero volatility premium, writing an ATM covered call is exactly equivalent to cutting the index position by 51%.** In their stylised example (index 100, one month, 18% implied vs 16% realised), the ATM call sells for 2.07% and only **~11% of that premium is volatility compensation** — the other ~89% is the equity premium being handed back. A 104-strike call yields 6.65% annualised, of which 2.05% is volatility premium and 4.60% is equity premium. They also state that **delta-hedging the short straddle substantially increases its Sharpe ratio**, and that selling a basket of options across strikes may diversify idiosyncratic option risk. Their simulated covered call (Apr 1996 – Dec 2013): 5.0% excess return = 3.3% equity + 1.8% short straddle; 14.1% vol = 9.9% equity + 6.7% straddle at 0.42 correlation; beta 0.64; Sharpe 0.36.
- **IMPLICATION FOR THE BUILD:** Two things. (a) Roughly **nine-tenths of the premium a covered-call writer collects is not compensation** — it is the equity premium on the delta sold. The build should display, for every candidate write, the split between vol-premium and equity-premium portions of the premium, because the quoted "yield" is almost entirely the latter. (b) Since the investor **already holds index funds**, a covered call is a disguised and expensive way of reducing their index position. If they want 50% equity they should hold 50% equity. The only reason to write the call is the ~11%-of-premium vol compensation, and the only way to get it cleanly is to neutralise the delta.

### CLAIM 1.6 — Israelov's later (QVR) work is substantially *negative* on call-writing and specifically negative on the post-2011 index call premium.
- **SOURCE:** Roni Israelov & David Ndong, "A Devil's Bargain: When Generating Income Undermines Investment Returns," QVR Advisors working paper, Oct 2023 (later *Journal of Alternative Investments*). Summaries: [CXO Advisory](https://cxoadvisory.com/equity-options/beat-the-market-with-covered-calls); [Larry Swedroe, Alpha Architect](https://alphaarchitect.com/covered-calls/); [Moontower](https://moontowermeta.com/derivative-income-bumhunting/); press: [BNN Bloomberg](https://www.bnnbloomberg.ca/chasing-options-income-risks-grave-error-former-aqr-quant-warns-1.1993662).
- **EVIDENCE STRENGTH:** Moderate (asset-manager research, later peer-reviewed; read through secondary summaries).
- **DETAIL:** Jan 1999 – Jun 2023. Each month they sell the SPX call expiring the following third Friday with premium closest to a target monthly yield (0.10% to 1.5%, i.e. ~1.2% to ~18% annualised), held to expiry. Results: **the strategy beat the index by only ~0.2%/yr gross, and only at target yields of about 1.2%–2.4% annualised.** At higher yields it trailed. Raw option P&L: at a 6% annualised target the calls settled at 0.54% of index versus an average sale price of 0.49%, a loss of ~0.60%/yr; at 12% target, ~1.08%/yr. **In the 2011 – mid-2023 sub-period the 6% target lost ~3.1%/yr and the 12% target ~4.7%/yr.** High-yield (near-ATM) writes had equity beta ~0.75 versus ~1.0 for low-yield writes. The authors suggest crowding in yield-enhancement has compressed premiums.
- **IMPORTANT RECONCILIATION (own analysis):** "Selling calls lost money" is *not* the same as "there is no volatility premium," because the raw option P&L embeds the short delta's share of the equity risk premium. For the 2011–2023 6%-target case, a call with delta ~0.25 against an equity excess return of roughly 12%/yr implies a delta-attributable loss of about 3%/yr — essentially the whole −3.1%. For the 12%-target case (delta ~0.5), delta-implied loss ≈ 6%/yr against an actual −4.7%, implying a residual *positive* vol premium of ~1.3%/yr. So the paper is strong evidence that **unhedged** call-writing has been a losing proposition post-2011, and is *ambiguous* on whether the delta-hedged premium has disappeared. This ambiguity is the central unresolved risk in the strand.
- **IMPLICATION FOR THE BUILD:** Israelov's own later conclusion is that investors should stop treating premium as income and should allocate to equity and volatility premia deliberately and separately. That is precisely the architecture recommended in §7. Also: the build should default to **small target yields** (1–3% annualised), not the 8–12% the retail covered-call world chases.

### CLAIM 1.7 — Israelov has quantified "rebalance timing luck" in option overlays, which bears directly on the laddering question.
- **SOURCE:** Roni Israelov, "Rebalance Timing Luck in Option Overlays" (presentation), CQF Institute, 23 Mar 2023. [PDF](https://www.cqfinstitute.org/sites/default/files/8%20-%20Roni%20Israelov_230323.pdf).
- **EVIDENCE STRENGTH:** Moderate (practitioner presentation, gross of all costs; structure is a put-spread collar, not a plain covered call).
- **DETAIL:** 2008–2022, quarterly put-spread collars (long SPX TR, long 5% OTM put, short 20% OTM put, short self-financing OTM call), run as three staggered tranches (DMJS / JAJO / FMAN). Sharpe 0.54 / 0.54 / 0.42 versus SPX 0.51; betas 0.47–0.53. Decomposition is into **passive equity (average delta), timing (de-meaned delta), and delta-neutral/convexity** — the same architecture as the 2015 paper. Delta drift example: April 2017 expiry went from 0.49 at launch to **0.07** the day before expiry. On 14 Feb 2019 the three tranches were simultaneously ~100%, ~45% and <10% equity-exposed. **Cross-tranche portfolio-delta correlation ≈ 0.27.** Rebalance timing luck is **~40% of the strategy's volatility**; the spread across tranches was 1.0% in excess return, 1.4% in alpha, 1.1% in volatility, 0.12 in Sharpe, and 9% in worst drawdown, with a near-40% difference in terminal wealth over 15 years. Diversifying across tranches does little to reduce volatility or drawdown but removes the risk of holding the worst tranche, which trailed the median by 15%. Timing and delta-neutral alphas are small and statistically insignificant.
- **IMPLICATION FOR THE BUILD:** (a) Laddering expiries is *mandatory risk hygiene*, not an alpha source — it removes a 0.12-Sharpe / 15%-terminal-wealth lottery. (b) The 0.27 cross-tranche delta correlation implies (own arithmetic) that averaging three tranches cuts the *variance* of the timing exposure by roughly half: var of the mean of 3 with pairwise ρ=0.27 is (1/3)(1+2×0.27)=0.51 of a single tranche's. So laddering is a genuine partial substitute for delta hedging, at near-zero extra cost. Caveat: this correlation was measured on *quarterly* collars; monthly calls laddered weekly would be more correlated and the benefit smaller.

### CLAIM 1.8 — No independent academic replication or formal critique of the Israelov–Nielsen decomposition was found; the only replication is by the same lead author.
- **SOURCE:** Repeated targeted searches (Google Scholar-style queries via web search) for critiques, failed replications, and independent decompositions. Nothing found.
- **EVIDENCE STRENGTH:** No credible evidence found (of a critique). The decomposition is therefore *unchallenged* but also *unaudited by outsiders* — all three decomposition studies have Israelov as an author.
- **IMPLICATION FOR THE BUILD:** Treat the 0.21 average active exposure and the 26% timing risk share as model-dependent inputs, not facts. Israelov himself notes the decomposition is sensitive to the delta model (they used Black–Scholes at an assumed flat 18% IV); a different delta model shifts return between the three components. The build should compute its own deltas from live implied volatilities and show sensitivity, not hard-code the paper's numbers.

---

## 2. What stripping the equity-timing component actually requires operationally

### CLAIM 2.1 — The required hedge is small, mechanical, and fully specified ex ante.
- **SOURCE:** Israelov & Nielsen 2015; Israelov, Klein & Tummala 2017.
- **EVIDENCE STRENGTH:** Strong.
- **DETAIL:** Daily recomputation of the written option's delta; hedge the deviation from a constant target (0.5 ATM / 0.3 for 2% OTM calls, i.e. 0.7 portfolio delta); instrument = index futures or ETFs; mean absolute hedge ≈ 21% of written notional; example peak 35%. No forecasting, no discretion, no optimisation. The exposure is "known ex ante."
- **IMPLICATION FOR THE BUILD:** This is a deterministic function of (spot, strike, DTE, IV, rate, dividend yield). It is a ~30-line calculation. The build should emit a daily target hedge notional and a suggested contract count, with a tolerance band.

### CLAIM 2.2 — Daily is what the literature tests; the limited evidence on lower frequency suggests weekly is not worse, and may be better net of costs.
- **SOURCE:** (a) Israelov & Nielsen 2015 (daily only). (b) A. Tilgenkamp-style master's thesis: "Confronting the Volatility Risk Premium on the S&P 500 Index," Copenhagen Business School, [PDF](https://research-api.cbs.dk/ws/portalfiles/portal/60757092/307507_Confronting_the_volatility_risk_premium_on_the_S_P500_index.pdf). (c) James O'Donovan & Gloria Yang Yu, "A Transaction Cost Perspective on Option Anomalies," SSRN 4806038, Apr 2024, rev. Dec 2025. [SSRN](https://papers.ssrn.com/abstract=4806038).
- **EVIDENCE STRENGTH:** Weak for (b) — unpublished thesis, short sample, idiosyncratic statistics. Moderate for (c) — SSRN working paper, large cross-section.
- **DETAIL:** The CBS thesis compares **weekly versus daily** delta hedging of short SPX straddles and strangles and finds weekly superior on return and risk-adjusted measures: mean monthly return 0.47% (straddle) / 0.49% (strangle) weekly versus 0.19% / 0.30% daily; cumulative 66%/75% versus 23%/41%. Daily had lower volatility (2.04%/1.90% vs 2.93%/2.31% monthly) and generally lower VaR/expected shortfall. The thesis attributes part of daily's shortfall to higher trading costs and part of weekly's gain to a few lucky hedges during large moves — so this is **not clean evidence**. It also concludes that **delta neutrality is required** to obtain the volatility-premium factor exposure at all, and that the **short delta-hedged strangle** was the most profitable route. Separately, O'Donovan & Yu find that **hedging frequency has a first-order effect on transaction costs**, that 17 of 24 delta-hedged option sorts are significantly profitable gross, and that **none survive trading costs** without an explicit cost-mitigation overlay (which restores 7).
- **IMPLICATION FOR THE BUILD:** Daily is the literature default but is not demonstrably necessary. Build the hedge as **banded**: recompute daily, trade only when the deviation exceeds a tolerance (see §3 for the size-driven floor on that band). Expect to trade a few times a month, not daily. Make the band a tunable parameter and show the user the cost/tracking trade-off.

### CLAIM 2.3 — Static approximations: only *strike widening* and *early rolling* and *laddering* actually change the risk mix; partial notional does not.
- **SOURCE:** Israelov & Nielsen 2015 (Tables 1, 3, 6); Israelov CQF 2023; own arithmetic.
- **EVIDENCE STRENGTH:** Strong for strike widening (direct from Tables 3 and 6); Moderate for laddering; Weak/own-arithmetic for early rolling; Strong (logical) for the partial-notional null result.
- **DETAIL:**
  - **Partial notional is a null.** Writing X% of the holding scales all three components — equity, short-vol, timing — linearly by X. The *share* of risk from timing is unchanged, so the Sharpe of the overlay sleeve is unchanged. Partial notional is a **sizing** decision, not a risk-mix improvement. This is important because retail commentary routinely presents partial coverage as a risk-management fix; it is not.
  - **Strike widening is a real, free improvement.** Timing's share of risk falls from **26% (ATM, BXM) to 12% (2% OTM, BXY)**, and unhedged Sharpe rises 0.37 → 0.41. Against the full hedged-ATM result of 0.52, moving ATM → 2%-OTM captures about **27% of the available gross improvement at zero incremental cost**. Hedging the 2%-OTM write then gets to 0.46, i.e. **~60% of the way**. (Caveat: BXM and BXY have different equity betas, so the Sharpes are not perfectly comparable at matched beta.)
  - **Early rolling.** Israelov establishes that timing risk rises monotonically through the option's life and is near-passive-equity magnitude on the final day. Own arithmetic: modelling active exposure as ≈0.4·√(t/(T−t)) truncated at ±0.5, closing the write with one-third of its life remaining removes roughly **35–50% of the timing variance**, for the cost of one additional option trade per cycle (the buy-back). Wide uncertainty; **no paper quantifies this.** Supporting but non-quantitative practitioner evidence: tastylive's study of selling 45-day options and managing at 21 days reports significantly reduced risk and a tighter return distribution, with no figures published ([recapio digest](https://recapio.com/digest/gamma-risk-why-early-management-wins-study-by-tastylive)).
  - **Laddering.** See Claim 1.7: cross-tranche delta correlation 0.27 implies ~49% reduction in timing-exposure variance from three staggered tranches (own arithmetic), at near-zero incremental cost, plus removal of the 0.12-Sharpe tranche lottery.
  - **Deep-OTM ultra-short writing eliminates timing structurally.** A live retail practitioner selling 0DTE/1DTE SPX options reports mean absolute deltas of **0.004–0.009** at inception ([Early Retirement Now, Options Trading Series Part 13](https://earlyretirementnow.com/2025/01/14/options-trading-series-part-13-year-2024-review/)). At those deltas the active-exposure term is numerically irrelevant, so the timing component is ~zero by construction, with no hedging at all. The cost is that you are selling jump/tail risk rather than ATM variance: his 0DTE put premium-capture rate was only 32.2%, and he regards portfolio margin as "essential". This is a different risk premium with a much worse tail.
- **IMPLICATION FOR THE BUILD:** The default recommendation for a retail user without a futures account is **2%-OTM strikes + three staggered tranches + roll at ~1/3 life remaining**. Own arithmetic suggests that stack plausibly captures **50–65% of the gross Sharpe improvement at near-zero incremental cost**, versus ~100% for a daily futures hedge. That is an excellent trade.

### CLAIM 2.4 — Hedging with shares is cheaper than futures but touches the holding; hedging with an offsetting option is unquantified.
- **SOURCE:** Own arithmetic from published spreads; Dörries, Korn & Power 2021 (3 bp underlying hedge spread assumption).
- **EVIDENCE STRENGTH:** Moderate (cost arithmetic); No credible evidence found (offsetting-option hedge).
- **DETAIL:** SPY at ~$755 (S&P ~7,550) trades with a $0.01 spread, i.e. a half-spread of **0.07 bps of notional**, at zero commission at most US retail brokers — roughly **half the cost of MES** and with **50× finer granularity** ($755 per increment versus $37,750). The decisive drawback is that trading shares in the holding realises gains in appreciated lots and triggers wash-sale and holding-period issues. Hedging by adjusting the short option (e.g. converting the short call into a call spread, so that delta drift is bounded by the strike separation) caps drift at high index levels but not between strikes; **no study quantifies this** and it adds a long-option premium cost.
- **IMPLICATION FOR THE BUILD:** Support two hedge instruments: **MES/MNQ** (default for a taxable account with appreciated lots) and **SPY/QQQ shares** (default for an IRA or for a freshly-established position, where it is cheaper and far more granular). The build should let the user pick and should show the granularity error for each.

---

## 3. Can micro futures make retail delta-hedging viable? — Yes, on cost; the binding constraint is granularity, not cost

### CLAIM 3.1 — Micro E-mini contract specifications (verified).
- **SOURCE:** CME Group, "Frequently Asked Questions: Micro E-mini Equity Index Futures," [cmegroup.com](https://www.cmegroup.com/articles/faqs/micro-e-mini-equity-index-futures-frequently-asked-questions.html).
- **EVIDENCE STRENGTH:** Strong (exchange primary source).
- **DETAIL:** **MES** multiplier **$5 × S&P 500**; outright tick 0.25 index points = **$1.25**; calendar-spread tick 0.05 pts = $0.25. **MNQ** multiplier **$2 × Nasdaq-100**; outright tick 0.25 pts = **$0.50**. March quarterly cycle (Mar/Jun/Sep/Dec), five contract months listed, cash-settled against the Special Opening Quotation on the third Friday. CME Globex hours Sun 18:00 ET – Fri 17:00 ET with a daily 16:15–16:30 ET halt. Launched May 2019. CME does not publish spread statistics on that page.
- **At S&P 500 ≈ 7,550 (Nov 2026 — index closed at 7,549.94 in a recent session, [report](https://www.ad-hoc-news.de/boerse/news/marktberichte/s-p-500-closes-at-7-549-94-after-2-35-rally/70483327)), one MES ≈ $37,750 notional; one ES ≈ $377,500.**

### CLAIM 3.2 — MES margin is roughly 4–5% of notional; this is not a constraint for an overlay.
- **SOURCE:** CME directs to SPAN margin tables and publishes no fixed figure. Broker/secondary: MetroTrade knowledge base, [MES contract specifications](https://help.metrotrade.com/kb/micro-e-mini-sp-500-futures-mes-contract-specifications) — initial ~**$1,700–1,900**, maintenance ~**$1,550–1,750**, varying with volatility. Webull's guide gives a general 3–12%-of-notional range ([Webull](https://www.webull.com/blog/334-Micro-E-Mini-Futures-A-Complete-Guide-to-Contract-Specs-Margins-and-Trading)). Optimus Futures lists a **$50 day-trade margin** for MES, with full initial margin applying to positions held past 16:45 ET ([Optimus](https://optimusfutures.com/Futures-Trading-Margins.php)).
- **EVIDENCE STRENGTH:** Moderate. CME's own page gives no dollar figure, and broker pages are undated. **Verify in the broker's live margin table before sizing.**
- **DETAIL:** $1,700–1,900 initial on ~$37,750 notional ≈ 4.5–5.0%. A typical overlay hedge of ~21% of a $500k sleeve is ~$105k of delta ≈ 2.8 MES ≈ **$5,000–5,300 of initial margin**, about 1% of the sleeve. Peak hedges of 45% would need ~6 contracts ≈ $11,000.
- **IMPLICATION FOR THE BUILD:** Margin is a non-issue. Reserve ~3% of the sleeve as futures margin buffer and the hedge will never be force-liquidated under plausible moves. Note that **day-trade margin does not apply** — this is an overnight hedge, so budget full initial margin.

### CLAIM 3.3 — The all-in cost of a daily MES delta hedge is of the order of **5–10 bps/yr of hedged notional** — roughly one-fifth of what the institutional study paid.
- **SOURCE:** Own arithmetic, from CME tick specs (Claim 3.1), typical retail futures commissions, and Black–Scholes gamma. Cross-check: Dörries, Korn & Power (2021) assume a **3 bp quoted spread** on the underlying hedge instrument, [PDF](https://www.fernuni-hagen.de/bwlbuf/docs/how_to_harvest_variance_risk_premiums_for_the_long-term_investor_.pdf).
- **EVIDENCE STRENGTH:** Moderate (transparent arithmetic from verified specs; not from a published study).
- **DETAIL (own calculation, stated so the user can check it):**
  - *Cost per trade.* MES half-spread = 0.125 index points / 7,550 = **0.17 bps** of notional. Commission at ~$0.50–0.85 per contract per side on $37,750 = **0.13–0.23 bps**. Total **≈0.30–0.40 bps per side**.
  - *Turnover.* For an ATM 35-DTE SPX call at 15% implied volatility, gamma ≈ 0.00114 per index point, so delta moves ≈0.086 per 1% index move. With an expected absolute daily move of ~0.75%, mean daily delta change ≈ **0.065**, i.e. ~6.5% of written notional per day, or **≈16× notional per year** if rebalanced every day.
  - *Annual cost.* 16 × 0.35 bps ≈ **5.6 bps/yr**; call it **5–10 bps** allowing for commission variation and roll.
  - *Roll.* Four quarterly rolls per year, each a calendar spread at a 0.05-point tick ($0.25): negligible, well under 1 bp/yr.
  - *Comparison.* Israelov, Klein & Tummala's daily hedge cost ~0.05 of Sharpe ≈ **46 bps/yr** at 9.2% volatility — about 6–9× the retail arithmetic. The difference is market impact on institutional size, which a one-to-six-contract retail hedge does not pay.
- **IMPLICATION FOR THE BUILD:** **Cost is not the obstacle to retail delta hedging of an index overlay.** Against a gross prize of ~130 bps/yr, a 5–10 bps hedge is trivially affordable. This is the key enabling fact of the strand. The build should state this number explicitly to the user, because the intuition ("delta hedging is for institutions") is wrong for index futures and right only for single-name options.

### CLAIM 3.4 — Granularity, not cost, sets the minimum account size, and it is roughly $300–500k for the written sleeve.
- **SOURCE:** Own arithmetic from Claim 3.1 notional and Claim 1.2 mean active exposure.
- **EVIDENCE STRENGTH:** Moderate (arithmetic).
- **DETAIL:** One MES is an indivisible $37,750 step. With a ±½-contract tolerance band, residual mean absolute unhedged exposure ≈ one-quarter of a contract's share of the sleeve. Against a mean active exposure to be removed of 0.21:

| Written sleeve | 1 MES as % of sleeve | Residual mean exposure | Share of active exposure removed |
|---|---|---|---|
| $1,000,000 | 3.8% | ~0.9% | ~96% |
| $500,000 | 7.6% | ~1.9% | ~91% |
| $250,000 | 15.1% | ~3.8% | ~82% |
| $150,000 | 25.2% | ~6.3% | ~70% |
| $100,000 | 37.8% | ~9.4% | ~55% |
| $50,000 | 75.5% | ~18.9% | ~10% |

- **IMPLICATION FOR THE BUILD:** Hard-code a size check. Below roughly **$150,000 of written notional**, MES granularity destroys most of the hedge and the user should fall back to the static ladder (strike widening + tranches + early roll) or to SPY-share hedging in a tax-advantaged account. The build should display this table and the user's position on it.

### CLAIM 3.5 — Practical frictions: basis, dividends, roll, and the fact that the hedge instrument may not match the holding.
- **SOURCE:** CME contract specs (Claim 3.1); general futures mechanics.
- **EVIDENCE STRENGTH:** Moderate.
- **DETAIL:** (a) **Basis.** MES prices the forward, embedding financing less expected dividends; the hedge therefore carries a small financing exposure and the basis moves with rate and dividend expectations. Over a one-month hedging interval this is small, but it is not zero and it is a systematic drag/benefit depending on which side you are on. (b) **Roll.** Four quarterly rolls, each a calendar spread; operationally simple but must be automated or it will be forgotten. (c) **Overnight margin and mark-to-market.** Futures settle daily in cash, so the hedge consumes and releases cash daily; the account needs a cash buffer independent of the margin requirement. (d) **Instrument mismatch.** If the user writes calls on an S&P 500 holding, MES matches well. If they write on QQQ, MNQ matches. If they write on a sector or a non-US holding, there is no micro contract that matches and the hedge becomes a basis trade. (e) **Tax.** Futures are §1256 contracts with 60/40 long/short-term treatment and year-end mark-to-market; hedging an appreciated equity position with an offsetting futures position also raises §1092 straddle-rule questions that can suspend holding periods and defer losses. **Tax is explicitly out of this brief — flagged and left to the tax strand.**
- **IMPLICATION FOR THE BUILD:** The build must verify that a micro contract exists for the user's underlying before offering the hedged route, and must schedule the quarterly roll.

---

## 4. Does the decomposition hold for single names?

### CLAIM 4.1 — **No decomposition of single-name covered-call or buy-write returns into equity / short-vol / timing components was found.** This is the strongest result in the programme and it is index-only.
- **SOURCE:** Repeated targeted searches. All three decomposition papers (Israelov & Nielsen 2014, 2015; Israelov, Klein & Tummala 2017) use indices exclusively. The 2014 paper's single-stock content is purely illustrative, with **no quantitative single-stock comparison**. The 2017 paper covers 11 *indices*, not stocks. Independent searches for single-name decompositions returned nothing.
- **EVIDENCE STRENGTH:** No credible evidence found.
- **IMPLICATION FOR THE BUILD:** The build must not represent the Israelov improvement as applying to single-name covered calls. It should say so in the UI. Everything the programme has established about the hedged overlay is an index result.

### CLAIM 4.2 — The one systematic single-name buy-write benchmark shows materially worse risk reduction and ~5× the trading cost of index-level writing, with no Sharpe improvement.
- **SOURCE:** S&P Dow Jones Indices, "The S&P 500 Stock Covered Call Index: Why, When and How It Works" (SPXCC, Bloomberg ticker SPXCC). [PDF](https://www.spice-indices.com/idpfiles/spice-assets/resources/public/documents/research-sp-500-stock-covered-call-index-why-when-and-how-it-works.pdf).
- **EVIDENCE STRENGTH:** Moderate (index-provider research on a hypothetical backtest; not peer-reviewed; sample ends 2013).
- **DETAIL:** SPXCC writes **monthly OTM calls on individual S&P 500 constituents**, strike set at 0.75 × each stock's implied volatility above its opening price on the roll day. Nine-year figures (16 Jan 2004 – 31 May 2013), annualised: S&P 500 **6.45% / 21.18% vol**; BXM **4.58% / 15.28%**; SPXCC **5.47% / 18.60%**. Max drawdown: S&P 500 **−55.25%**, BXM **−40.14%**, SPXCC **−49.75%**. Trading cost is stated at about **150 bps per year**. Monthly averages: gross option premium 0.93%, dividend 0.17%, net "income distribution" only **0.37%** after exercise and trading costs. Premium is strongly state-dependent: average monthly income 0.76% in down markets, 0.31% when the market rose 0–2%, and **0.06%** when it rose more than 2%. No decomposition is provided.
- **OWN ARITHMETIC:** at a ~1.5% risk-free rate over that period, Sharpe ratios are approximately S&P 500 0.23, BXM 0.20, SPXCC 0.21 — i.e. **single-name covered-call writing produced no risk-adjusted improvement over simply holding the index** in this sample, while BXM was slightly worse. (Rough; the sample straddles the GFC and is short.)
- **IMPLICATION FOR THE BUILD:** Two decisive numbers. (a) **150 bps/yr of trading cost** for monthly single-name call writing, versus **28 bps/yr** for index-level monthly writing (Claim 1.4) — a **5.4× cost multiple**, consistent with the programme's earlier finding of 8–20% of premium for single names versus ~2% for index options. (b) The entire gross prize at index level was ~130 bps/yr. **At single-name level the trading cost alone (150 bps) exceeds the whole index-level prize before any premium is even collected.** Combined with the thinner single-name variance risk premium (~1.5 vol points versus 3.3 for SPX, per the programme's prior finding) and the apparently unpriced idiosyncratic volatility, the arithmetic for single-name overlay harvesting is negative.

### CLAIM 4.3 — Delta-hedged single-name option strategies are the specific case where transaction costs are documented to destroy *all* gross profitability.
- **SOURCE:** O'Donovan & Yu, "A Transaction Cost Perspective on Option Anomalies," SSRN 4806038, 2024/2025. [SSRN](https://papers.ssrn.com/abstract=4806038).
- **EVIDENCE STRENGTH:** Moderate-to-Strong (large cross-section, recent, explicit cost treatment; working paper).
- **DETAIL:** Across 24 sorting variables on long-short portfolios of **delta-hedged equity option returns**, 17 produce positive and statistically significant *gross* returns, and **none remain profitable after trading costs**. The authors' own cost-mitigation technique restores 7. Delta-hedging frequency has a first-order effect on costs.
- **IMPLICATION FOR THE BUILD:** This is the decisive argument against single-name delta-hedged writing at retail. If institutional-grade cost-mitigation is required to salvage 7 of 24 strategies, a retail account paying full single-name option spreads has no edge. **Do not build a single-name delta-hedged module.**

---

## 5. Put-writing versus covered calls

### CLAIM 5.1 — Cash-secured put-writing has historically shown slightly better risk-adjusted returns than the index and comparable-or-better statistics than buy-writing, but all published figures are gross.
- **SOURCE:** Oleg Bondarenko, "An Analysis of Index Option Writing with Monthly and Weekly Rollover," Jan 2016 (Cboe-sponsored). Summary: [CXO Advisory](https://www.cxoadvisory.com/equity-options/performance-of-cboe-putwrite-indexes). Also [Cboe benchmark index commentary](https://www.cboe.com/insights/posts/key-cboe-benchmark-indexes-using-spx-options-offer-strong-risk-adjusted-returns/).
- **EVIDENCE STRENGTH:** Moderate (sponsored research; gross of costs; pre-launch history is backfilled).
- **DETAIL:** Feb 2006 – Dec 2015: PUT 6.6% return / 11.5% vol / **Sharpe 0.52**; WPUT 5.6% / 9.8% / 0.50; S&P 500 TR 7.1% / 15.1% / 0.46. Max drawdowns −33% / −24% / −51%. Longer sample Jul 1986 – Dec 2015: PUT 10.1% versus S&P 9.8%, **Sharpe 0.67 vs 0.47**. All gross; the summary notes option trading frictions are high and PUT/WPUT turnover far exceeds the index's. It also notes that **exchange-traded products tracking BXM substantially underperform the BXM index itself** — the standing warning about index-to-product slippage.
- **IMPLICATION FOR THE BUILD:** By put–call parity an ATM cash-secured put write is economically the same position as an ATM covered call, so it has the **same equity-timing contamination** — a short put's delta also drifts between 0 and 1. Put-writing is therefore **not a cleaner way to isolate the short-vol component**; it is the same exposure with different plumbing.
- **The real differences, which do matter for the build:** (a) It never touches the appreciated share lot, so the in-the-money-call holding-period trap does not arise (tax out of scope, flagged). (b) Collateral is cash or T-bills rather than the equity holding, which means it **does not reduce the user's existing index exposure** — relevant because they already hold index funds and may not want their beta cut. (c) Puts are on the rich side of the equity skew, so the vol premium per unit of delta is generally larger than for calls. (d) Assignment on a short put delivers shares, which an index-fund holder may not want.

### CLAIM 5.2 — No study comparing put-writing and covered calls *net of realistic costs*, with the timing component separated, was found.
- **SOURCE:** Searches across Cboe, CXO, academic sources. Bondarenko reports no BXM comparison; the CXO summary explicitly notes none.
- **EVIDENCE STRENGTH:** No credible evidence found.
- **IMPLICATION FOR THE BUILD:** Treat covered call and cash-secured put as the same underlying bet and choose between them on plumbing (collateral, assignment, tax), not on expected return.

---

## 6. Alternative routes to the volatility premium with less timing contamination

### CLAIM 6.1 — Among retail-reachable structures, a **delta-hedged short strangle** and a **variance-swap-like structure** rank highest; the delta hedge is necessary, not optional, for the premium to show up.
- **SOURCE:** Julian Dörries, Olaf Korn & Gabriel J. Power, "How to Harvest Variance Risk Premiums for the Long-Term Investor," Aug 2021. [PDF](https://www.fernuni-hagen.de/bwlbuf/docs/how_to_harvest_variance_risk_premiums_for_the_long-term_investor_.pdf). Secondary support: CBS thesis (Claim 2.2).
- **EVIDENCE STRENGTH:** Moderate (working paper, explicit cost treatment, but the Sharpe units are not clearly defined in the paper).
- **DETAIL:** They compare straddle, strangle, butterfly, condor strangle, delta-hedged call, delta-hedged put and variance swap on one-month SPX options. Cost assumptions: effective spread **25% of the quoted bid-ask** (sensitivities at 0% and 50%), long options at the ask and short at the bid, **3 bp quoted spread on the underlying hedge**, options held to expiry and cash settled. Reported risk-adjusted figures (interpretable as monthly, so multiply by ~3.46 for annual): variance swap 0.152 / 0.232 (max-exposure / equal-exposure), straddle 0.133 / 0.120, delta-hedged call 0.127 / 0.121, delta-hedged put 0.120 / 0.115, butterfly 0.121 / 0.097, strangle 0.098 / 0.118, condor 0.111 / 0.065. The **variance swap and delta-hedged put are highlighted as most promising**; the variance swap has the highest equal-exposure return and lowest downside risk. Crucially, **the delta hedge is set at initiation and not readjusted until maturity** — a fully static, one-shot hedge — and the results are still positive net of their cost assumptions. The CBS thesis independently concludes that **delta neutrality is required to gain the volatility-premium factor exposure** and that the short delta-hedged strangle was its most profitable route.
- **IMPLICATION FOR THE BUILD:** A **set-and-forget initial delta hedge** is a legitimate, costed, published implementation — it is the cheapest rung on the ladder above doing nothing, and it needs one futures trade per option cycle rather than a daily routine. Build it as the default hedged mode, with daily banded hedging as an opt-in upgrade.

### CLAIM 6.2 — Retail cannot access variance swaps; the listed proxies are poor.
- **SOURCE:** Dörries, Korn & Power 2021 (variance swap is their best performer but is an OTC instrument); general market structure. Cboe variance futures have had intermittent listings and thin liquidity.
- **EVIDENCE STRENGTH:** Moderate.
- **IMPLICATION FOR THE BUILD:** The best-performing structure in the literature is the one retail cannot buy. The closest accessible approximation is a **delta-hedged strangle laddered across strikes** — Israelov & Nielsen 2014 note that selling a basket of options across strikes may diversify idiosyncratic option risk, which is directionally what a variance swap does.

### CLAIM 6.3 — Short-volatility ETPs are not a premium harvest and have a documented catastrophic failure mode.
- **SOURCE:** Patrick Augustin, Ing-Haw Cheng & Ludovic Van den Bergen, "Volmageddon and the Failure of Short Volatility Products," *Financial Analysts Journal*, Q3 2021. [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2021/volmageddon-failure-short-volatility-products).
- **EVIDENCE STRENGTH:** Strong (peer-reviewed).
- **DETAIL:** On 5 February 2018 XIV and SVXY — inverse trackers of the S&P 500 VIX Short-Term Futures Index — lost **more than 90% of value in one day**; investors lost roughly 90%. Mechanism: as volatility rose, fund assets fell while short VIX-futures exposure grew, forcing large VIX futures purchases to restore neutrality, which pushed futures higher, shrinking assets further — a self-reinforcing loop amplified by leveraged ETPs' large share of VIX futures open interest.
- **IMPLICATION FOR THE BUILD:** Exclude short-vol ETPs entirely. They are leveraged, path-dependent, and structurally reflexive.

### CLAIM 6.4 — VIX-based approaches harvest a different premium and are not a clean variance-premium harvest.
- **SOURCE:** Dörries, Korn & Power 2021 literature review, which notes VIX-based strategies earn a **term-structure (roll) premium rather than the variance risk premium**.
- **EVIDENCE STRENGTH:** Moderate.
- **IMPLICATION FOR THE BUILD:** Do not substitute VIX futures for SPX option writing and claim it is the same exposure. The build should not offer VIX products.

### CLAIM 6.5 — Ultra-short deep-OTM writing eliminates equity timing but substitutes jump risk and depends on portfolio margin.
- **SOURCE:** Karsten Jeske, "Options Trading Series Part 13: Year 2024 Review," Early Retirement Now, Jan 2025. [Link](https://earlyretirementnow.com/2025/01/14/options-trading-series-part-13-year-2024-review/).
- **EVIDENCE STRENGTH:** Weak as evidence of a premium (single account, no risk-adjusted benchmark comparable to the literature); **Strong as evidence of retail operational reality**.
- **DETAIL:** Sells 1DTE SPX puts daily plus 0DTE puts and calls. Mean absolute deltas in 2024: **0.004 (1DTE puts), 0.007 (0DTE puts), 0.009 (calls)** — so no delta management at all is required. 2024 net profit $95,861 on $124k+ gross premium, a 77.3% premium-capture rate overall but only **32.2% for 0DTE puts**; options added 4.8 percentage points to a 23.9% total return. He reports an information ratio of 10.62 for 2024 and ~3.0 over ~10 years, on 0.4% annualised risk for 2024 — figures that are not comparable to annual Sharpe ratios and should not be read as such. He uses **portfolio margin, which he calls essential**, no futures, and no delta hedging. He explicitly cites the Israelov & Nielsen decomposition and argues the short-vol component is worth holding while the timing component is not. Commenters report IBKR per-contract commissions around $1.20 and "exposure fees" that can consume a large share of income.
- **IMPLICATION FOR THE BUILD:** This is the only live retail evidence found of someone deliberately structuring around the Israelov decomposition. His solution — options so short-dated and far out of the money that delta is numerically negligible — is the only zero-infrastructure way to eliminate the timing component. The build can offer it as a mode, but must label it honestly: it is selling tail risk, not ATM variance, it needs portfolio margin, and the 32% capture rate on 0DTE puts shows how much of the premium is genuine expected loss.

---

## 7. Sizing an overlay against an existing holding

### CLAIM 7.1 — An ATM covered call is approximately a 51% reduction in the index position, so an investor who already holds index funds should size the overlay by how much beta they are willing to give up.
- **SOURCE:** Israelov & Nielsen 2014 (Claim 1.5).
- **EVIDENCE STRENGTH:** Strong.
- **DETAIL:** With zero volatility premium, writing a full-notional ATM covered call is identical to cutting the index position by 51%. ATM delta ~0.49. 2%-OTM calls have delta ~0.3, so a full-notional 2%-OTM write cuts effective exposure by ~30%.
- **IMPLICATION FOR THE BUILD:** The sizing input should be **"how much index beta are you willing to convert into short volatility?"**, not "what yield do you want?". For a user who wants to keep full equity exposure, the answer is to write at partial notional **and restore the lost delta with long futures** — which is exactly the hedged structure, run with a target delta of 1.0 rather than 0.5.

### CLAIM 7.2 — High target yields mechanically destroy return; the evidence supports very small overlays.
- **SOURCE:** Israelov & Ndong 2023 (Claim 1.6); Morningstar data cited in [Alpha Architect / Swan](https://alphaarchitect.com/covered-calls/) showing 6–8% distribution strategies had the best total returns while double-digit distributions were associated with weaker total returns.
- **EVIDENCE STRENGTH:** Moderate.
- **DETAIL:** Only 1.2–2.4% annualised target yields beat the index (by 0.2%/yr gross). Derivative-income assets grew from under $5bn to $74bn in a decade and products from 35 to 120, consistent with the crowding explanation.
- **IMPLICATION FOR THE BUILD:** Cap the default target yield at roughly 2–3% annualised. Warn above that. Do not offer a "high income" preset.

### CLAIM 7.3 — Partial notional does not improve the overlay's risk mix (restated for the sizing section).
- See Claim 2.3. Partial notional scales all three components linearly; it is a dial on exposure, not a risk-quality improvement. The build's UI should make this explicit, because it contradicts standard retail framing.

### CLAIM 7.4 — Tax trap: flagged and deferred.
In-the-money calls written against appreciated long-term lots can suspend the holding period (qualified-covered-call rules), and futures hedges against an appreciated equity position raise §1092 straddle-rule issues alongside §1256 60/40 treatment. **Out of this brief.** The build must surface a warning and route the question to the tax strand before any ITM write against an appreciated lot.

---

## RETAIL FEASIBILITY VERDICT

**Yes for index products, and more cheaply than the institutional literature implies. No for single names.**

For index products:
- The hedge is fully specified, deterministic, and small: offset the written call's delta deviation from a constant target (0.5 for ATM writing), averaging ~21% of written notional, peaking around 35–45%.
- Micro E-mini S&P (MES, $5 × index, 0.25-point tick = $1.25, ~$37,750 notional at S&P 7,550) can do this. **Own arithmetic puts the all-in cost of a daily hedge at 5–10 bps/yr of hedged notional** — a 0.17 bp half-spread plus 0.13–0.23 bp commission per side, against ~16× notional of annual turnover. The published institutional cost of the same hedge was ~46 bps/yr of Sharpe-equivalent, i.e. 6–9× higher, because institutions pay market impact that a one-to-six-contract hedge does not.
- Margin is ~4.5–5% of notional (~$1,700–1,900 initial per MES), so a $500k sleeve's hedge consumes ~1% of the sleeve. Not a constraint. **Verify in the live broker margin table — CME publishes no fixed figure.**
- **The binding constraint is contract granularity, not cost.** One MES is an indivisible $37,750 step. Below roughly **$150,000 of written notional** the rounding error swamps the exposure being hedged (see the table in Claim 3.4); below ~$50,000 the hedge is useless. Minimum comfortable sleeve: **$300–500k**.
- **The whole prize is ~130 bps/yr gross at full notional** (own arithmetic from Israelov & Nielsen Table 6 versus a volatility-matched passive-equity benchmark). Retail option frictions on monthly index calls, at the programme's established ~2%-of-premium figure, run roughly **30–45 bps/yr** depending on tenor; the futures hedge adds **5–10 bps**. So **the net prize is of the order of 75–95 bps/yr** — real, but not large, and critically dependent on the volatility premium still being positive (see Disconfirming Evidence).

For single names: **no.** Single-name monthly call writing carries ~150 bps/yr of trading cost (S&P's own SPXCC index documentation) — more than the entire index-level gross prize — against a variance premium the programme has already established is ~1.5 vol points versus 3.3 for SPX. And the one paper that costs delta-hedged *single-name* option strategies properly finds that **none of 24 gross-profitable sorts survives trading costs**. There is also no published decomposition of single-name covered calls at all, so the Israelov improvement has never been shown to exist there.

---

## IMPLEMENTATION LADDER

Share-of-improvement figures are relative to the **gross +0.15 Sharpe gain** Israelov & Nielsen measured for BXM (0.37 → 0.52). Entries marked *own arithmetic* are my estimates, not published results, and should be treated as order-of-magnitude.

| # | Approach | Mechanism | Est. share of the Sharpe improvement captured | Incremental cost | Evidence |
|---|---|---|---|---|---|
| 0 | Plain full-notional ATM monthly covered call, held to expiry | baseline | 0% | ~45 bps/yr option frictions (retail, ~2% of premium × 12 rolls) | Strong (Israelov & Nielsen 2015) |
| 1 | **Widen the strike to ~2% OTM** | cuts timing's risk share from 26% to 12% | **~27%** (0.37 → 0.41) | **Zero** — fewer-dollar premium, same trade count | **Strong** — direct from Israelov & Nielsen Tables 3 & 6 |
| 2 | **Ladder 3 staggered tranches** | averages uncorrelated delta paths (cross-tranche ρ ≈ 0.27 ⇒ ~49% of timing variance removed) | **~40–50%** *(own arithmetic)*; also removes a 0.12-Sharpe tranche lottery and a 15% worst-vs-median terminal gap | ~0 bps (same total notional, 3× trade count at 1/3 size; slightly worse per-ticket spread) | Moderate (Israelov CQF 2023 — measured on quarterly collars, not monthly calls) |
| 3 | **Roll out at ~1/3 of life remaining** instead of holding to expiry | truncates the window where timing risk peaks at near-passive-equity magnitude | **~35–50% of timing variance** *(own arithmetic)*; no published figure | +1 option trade per cycle ≈ +15–20 bps/yr retail | Weak–Moderate (mechanism is Strong from Israelov & Nielsen; magnitude is unquantified; tastylive's 45-day/21-day study is directional only) |
| 4 | **Stack 1+2+3** (recommended no-futures default) | | **~50–65%** *(own arithmetic; the three overlap, so not additive)* | ~+15–20 bps/yr | Moderate |
| 5 | **Static initial delta hedge, one futures trade per cycle, never readjusted** | sets portfolio delta to target at inception | Not separately measured; Dörries et al. show this structure is net-profitable on their cost assumptions | ~1–2 bps/yr in MES; requires futures account + quarterly roll | Moderate (Dörries, Korn & Power 2021) |
| 6 | **Banded daily hedge** — recompute daily, trade when deviation exceeds ±½ contract | the practical retail implementation | **~70–96% depending on sleeve size** (Claim 3.4 table) | ~3–8 bps/yr in MES | Moderate (own arithmetic on Israelov's method) |
| 7 | **Weekly hedge** | | Not measured against daily in a clean study; the one comparison found favours weekly on return and Sharpe but is a master's thesis with a short sample and acknowledged luck | ~2–4 bps/yr | **Weak** (CBS thesis) |
| 8 | **Full daily delta hedge with index futures** (Israelov's method as published) | | **100%** by definition (0.37 → 0.52 gross) | ~5–10 bps/yr at retail in MES; **~46 bps/yr at institutional size** | **Strong** gross (Israelov & Nielsen 2015); **Moderate** net (Israelov, Klein & Tummala 2017: 0.51 → 0.46 net, and 0.35 → 0.33 for the unhedged version, so **+0.13 of a +0.16 gross gain survives, ~81%**) |
| 9 | **Deep-OTM 0–1DTE writing, no hedge at all** | delta ≈ 0.004–0.009, so the timing term vanishes structurally | Not comparable — removes ~100% of timing but changes the premium being harvested from ATM variance to jump/tail risk | Needs portfolio margin; ~$1.20/contract commissions; 0DTE put premium capture only 32.2% | Weak as premium evidence, Strong as operational evidence (Early Retirement Now) |
| X | Partial notional (write on only part of the holding) | **scales all three components linearly** | **0%** — risk shares unchanged | n/a | Strong (logical consequence of the decomposition) |
| X | Short-vol ETPs (SVXY and successors) | | **Negative** — reflexive, leveraged | >90% one-day loss precedent | Strong (Augustin, Cheng & Van den Bergen, FAJ 2021) |
| X | VIX futures / VIX options | harvests the **term-structure premium**, not the variance premium | Not applicable | n/a | Moderate (Dörries et al. literature review) |

**The headline of this ladder:** rungs 1–3 cost essentially nothing, need no futures account, no daily routine and no minimum account size, and plausibly capture half to two-thirds of the benefit. Rung 8 costs 5–10 bps at retail scale and captures all of it, but only above ~$150–300k of written notional. There is no rung at which cost is the obstacle for *index* products.

---

## SINGLE-NAME VALIDITY

**The decomposition has never been measured on single names. Treat the strongest result in the programme as index-only.**

1. **No decomposition exists.** All three Israelov decomposition papers use indices (one index, then eleven indices). Independent searches for a single-name equivalent found nothing. *No credible evidence found.*
2. **What little systematic single-name buy-write evidence exists is unflattering.** S&P's SPXCC index (monthly OTM calls on individual S&P 500 constituents, strike at 0.75 × stock implied volatility above the open) delivered 5.47% at 18.60% volatility over 2004–2013, versus S&P 500 6.45% / 21.18% and BXM 4.58% / 15.28%. Own arithmetic puts all three Sharpes within 0.03 of each other (~0.20–0.23) — **no risk-adjusted improvement**. Max drawdown −49.75% versus BXM's −40.14%: the single-name version gives up most of the downside benefit, consistent with idiosyncratic volatility being diversified away in the premium but not in the delta.
3. **The cost arithmetic is fatal.** SPXCC's documented trading cost is **~150 bps/yr**, versus **~28 bps/yr** for index-level monthly writing. The entire index-level gross prize is ~130 bps/yr. Single-name writing costs more than the prize before any premium is collected. Note also that SPXCC's *net* income distribution was 0.37% monthly against 0.93% gross option premium — 60% of the premium was consumed by exercise and trading costs.
4. **Delta-hedging single names is specifically documented to fail on costs.** O'Donovan & Yu: 17 of 24 delta-hedged option sorts significantly profitable gross, **none net of costs**.
5. **The theoretical reason this is expected.** The timing component for a single name is timing of that single name — an idiosyncratic bet with no reason to be compensated — while the short-vol component is the single-name variance premium, which the programme has already established at ~1.5 vol points versus 3.3 for SPX, with idiosyncratic volatility apparently unpriced. The numerator shrinks by more than half while the denominator (cost) rises ~5×.

**Verdict: index-only. The build should not offer a hedged single-name overlay. If the user wants to write on individual tickers, the build should present it honestly as a beta-reduction and premium-capture exercise with no documented Sharpe benefit, and should display the 150 bps/yr cost estimate.**

---

## RECOMMENDED STRUCTURE

### (a) Index products — build this

**Architecture: separate the two sleeves. Do not write covered calls against the index fund.**

The user already holds index funds. A covered call on that holding is, per Israelov & Nielsen's own equivalence, a 51%-expensive way of cutting an index position they chose deliberately, and it entangles the equity decision with the volatility decision. Build instead:

1. **Equity sleeve:** the existing index funds, untouched, at the user's chosen beta. No calls written against appreciated lots. This also sidesteps the ITM-call holding-period trap entirely.

2. **Short-volatility sleeve (the overlay):** a **laddered, delta-hedged short strangle or short call position on a cash-settled index option (SPX or XSP), carried in a separate sub-account with its own cash collateral.**
   - **Instrument:** SPX for sleeves above ~$500k; **XSP** (1/10th size) below that, for the same reason MES granularity bites — XSP gives 10× finer notional granularity. Cash-settled, so no assignment of shares.
   - **Tenor:** 30–45 DTE at initiation, which matches the programme's established ~2%-of-premium index cost at 42–48 DTE.
   - **Strike:** 2% OTM or wider, not ATM. Target total annualised premium yield of **2–3%, not 8–12%** (Israelov & Ndong: only 1.2–2.4% targets beat the index).
   - **Ladder:** three tranches, staggered ~10–15 days apart, each 1/3 of the sleeve notional. Mandatory — it removes a 0.12-Sharpe / 15%-terminal-wealth lottery for free.
   - **Roll:** close and rewrite at ~1/3 of life remaining (≈12–15 DTE), not at expiry. This truncates the window in which timing risk approaches passive-equity magnitude.
   - **Delta hedge:** target a **constant** portfolio delta for the sleeve (zero if the sleeve is meant to be pure short-vol; the equity sleeve already supplies the beta). Recompute delta daily from live implied volatility. Trade **MES** when the deviation exceeds ±½ contract. Expect a handful of trades a month, ~5–10 bps/yr all in. Automate the quarterly MES roll.
   - **Fallback when the sleeve is under ~$150k:** skip the futures hedge, run rungs 1–3 only (2% OTM + three tranches + early roll), and tell the user explicitly that they are capturing roughly half to two-thirds of the available improvement.
   - **Sizing:** express the sleeve size as "percentage of portfolio beta converted into short volatility," and cap it. At full BXM notional the gross prize is ~130 bps/yr on the whole portfolio; at a 25% sleeve it is ~33 bps/yr gross, maybe ~20 bps net. Below that the whole exercise is not worth the operational burden, which is itself a finding worth telling the user.

3. **What the build must display, every time:**
   - The split of the quoted premium into **volatility-premium** and **equity-premium** portions (Israelov & Nielsen 2014: only ~11% of an ATM premium is compensation). This single number is the most useful thing the tool can show.
   - The sleeve's performance against a **volatility-matched passive-equity benchmark**, not against the raw index.
   - The user's position on the MES granularity table.
   - Current realised-versus-implied spread, so the user can see whether the premium is still there.

### (b) Single names — build a warning, not a strategy

Offer single-ticker covered-call analysis as a **premium-decomposition and beta-reduction calculator** only, with:
- the ~150 bps/yr trading-cost estimate from SPXCC,
- the ~1.5-vs-3.3 vol-point variance-premium comparison,
- the explicit statement that **no decomposition study exists for single names** and that the hedged improvement is an index result,
- and no delta-hedging module. Hedging a single-name call's delta means trading the stock itself (realising gains) or an unhedgeable basis, and O'Donovan & Yu show delta-hedged single-name option strategies do not survive costs.

If the user insists on single-name writing, the least-bad version is the same static ladder — well OTM, laddered, rolled early — accepted as a beta-reduction exercise with no claimed risk-adjusted benefit.

---

## DISCONFIRMING EVIDENCE

1. **Israelov's own later work is largely negative on call-writing, and the post-2011 evidence is the worst of it.** Israelov & Ndong (2023) find that over Jan 1999 – Jun 2023 monthly SPX call-writing beat the index only at 1.2–2.4% target yields and only by 0.2%/yr gross; in **2011 – mid-2023 a 6% target yield lost ~3.1%/yr and a 12% target ~4.7%/yr**. My reconciliation above suggests most of that is the short delta rather than a vanished vol premium — but it is a reconciliation, not a measurement, and the 12%-target residual implies a vol premium of only ~1.3%/yr, consistent with heavy compression.

2. **QVR — Israelov's own firm — has stated that the volatility risk premium is not persistently positive or attractive**, as reported in [Moontower's coverage](https://moontowermeta.com/derivative-income-bumhunting/) of the Devil's Bargain discussion. The author of the paper this entire strand rests on has, a decade later, publicly discouraged the premise. That is the most serious disconfirming fact available.

3. **The prior strand's QVR finding that a static 50/50 SPY/T-bill blend beat both JEPI and JHEQX** is the cleanest possible refutation of overlay complexity: if the simplest possible static allocation beats two professionally-run multi-billion-dollar overlay products, a retail overlay has a very high bar.

4. **The hedged improvement is mostly volatility reduction, not return.** Excess return goes 4.9% → 5.1%; volatility goes 11.4% → 9.2%. Almost all of the 0.37 → 0.52 is the denominator. Holding less equity achieves the same volatility reduction for nothing. The genuine incremental value is ~130 bps/yr, and a user who misreads the Sharpe gain as a return gain will badly oversize the overlay.

5. **The only net-of-cost accounting of the hedged result shows the hedge eats ~31% of its own gross benefit even at institutional scale.** Israelov, Klein & Tummala: risk-managed Sharpe 0.51 gross → **0.46 net** of daily hedge costs, against unhedged 0.35 → 0.33. The gain shrinks from +0.16 to +0.13.

6. **Delta-hedged option strategies have been shown not to survive transaction costs in the cross-section.** O'Donovan & Yu: of 24 sorts, 17 significant gross, **zero net**. Their result is on single-name options, so it does not directly refute the index case — but it is the only paper that carefully costs delta hedging, and its answer is negative.

7. **The decomposition has never been independently replicated or audited.** Every study that performs it has Israelov as an author. Israelov himself notes the attribution is sensitive to the delta model (Black–Scholes at a flat assumed 18% implied volatility), and that a different model shifts return between the three components. The 26% timing risk share and the 0.21 average active exposure are model outputs.

8. **The two decomposition tables in the anchor paper do not agree on the unhedged Sharpe** — Table 1 reports 0.52 for the simulated covered call while Table 6 reports 0.37 for the actual BXM index. The difference is simulated-versus-actual and simple-versus-compounded returns, but it means the headline "0.37 → 0.52" compares two different things in two different tables, and the number quoted as the improvement is partly an artefact of that.

9. **Laddering expiries — one of the cheapest rungs — was found by Israelov himself to do little for volatility or drawdown.** His RTL presentation says tranche diversification "does little to reduce volatility or drawdowns"; its benefit is avoiding the worst tranche. My ~40–50% estimate for rung 2 rests on extrapolating a 0.27 delta correlation measured on *quarterly put-spread collars* to *monthly calls*, where the correlation would be higher and the benefit smaller.

10. **Index-tracking reality check: products tracking BXM have substantially underperformed the BXM index itself** (noted in the CXO summary of the PutWrite study). Every number in this report is an index or a simulation. The gap between a published option-index backtest and a live account has historically been large.

11. **The one comparison of hedging frequencies found that *more* hedging produced *worse* returns** (CBS thesis: weekly beat daily on return and Sharpe for both straddles and strangles). It is weak evidence, but it is evidence against the proposition that the daily hedge in the anchor paper is the right frequency.

12. **The honest case for not attempting this at all:** the net prize is ~75–95 bps/yr at *full* BXM notional, which for a realistically sized sleeve (say 25% of portfolio) is ~20 bps/yr — against daily monitoring, a futures account, quarterly rolls, a ladder of three option positions, assignment and pin risk, basis risk, §1256 and §1092 complexity, and a premium whose continued existence the paper's own author doubts. A static reduction in equity exposure achieves the same volatility profile with none of it.

---

## OPEN QUESTIONS

1. **Is the index variance risk premium still positive net of costs post-2011?** Israelov & Ndong's raw option P&L is confounded by the short delta; nobody has published the *delta-hedged* SPX short-vol component's return for 2015–2026. This is the single question that determines whether the whole structure is worth building. It is also answerable from data the build will already have.
2. **What fraction of the timing variance does early rolling actually remove?** The mechanism is firmly established (timing risk peaks at expiry) but the magnitude is unpublished. A backtest rolling BXM-style writes at 1/3, 1/2 and 2/3 of life, with and without a futures hedge, would settle rung 3 of the ladder. This is the highest-value piece of original work available.
3. **What is the right rebalancing band?** No study varies the tolerance band. The build could grid-search band width against tracking error and cost directly.
4. **Does the decomposition transfer to single names at all?** Nobody has measured it. Running the Israelov decomposition on a handful of liquid single names would be a genuinely novel result, and would resolve whether the answer is "thinner but present" or "absent."
5. **Does XSP liquidity support a laddered 2%-OTM write at 30–45 DTE?** XSP solves the granularity problem for small sleeves, but its bid-ask spreads relative to SPX need measuring; the programme's ~2%-of-premium figure was established for index options generally, not XSP specifically.
6. **How much of the hedged improvement survives when the hedge instrument is MES rather than full-size ES?** The granularity table in Claim 3.4 is arithmetic, not simulation. A backtest hedging with integer MES contracts under a tolerance band would give the real number.
7. **Is the short-put version of the sleeve better net of skew?** Puts sit on the rich side of the equity skew, which should mean more vol premium per unit of delta, but no study separates skew from level in a put-write-versus-call-write comparison net of costs.
8. **Does the quarterly MES basis create a systematic drag on a persistently short hedge?** The hedge is short futures more often than long (it is short when the market has fallen, and markets rise more often than they fall), so there may be a persistent carry sign. Unquantified.

---

## TOP 10 SOURCES, RANKED

1. **Israelov, R. & Nielsen, L. N. (2015), "Covered Calls Uncovered," *Financial Analysts Journal* 71(6), 44–57.** DOI 10.2469/faj.v71.n6.1. The anchor. Peer-reviewed. Supplies the decomposition, the hedging methodology (daily BS delta, index futures, constant 0.5 target), the 0.21 mean active exposure, the 0.37 → 0.52 result, and the crucial fact that timing risk peaks at expiry. Gross of costs. [PDF](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/Covered-Calls-Uncovered.pdf)
2. **Israelov, R., Klein, M. & Tummala, H. (2017), "Covering the World: Global Evidence on Covered Calls," *Journal of Risk*.** The only out-of-sample replication *and* the only place the hedged result has been costed: 0.51 → 0.46 net of daily hedge costs, 0.35 → 0.33 net of option costs, 0.28%/yr option frictions. Peer-reviewed; AQR-authored. [Journal of Risk](https://www.risk.net/journal-of-risk/5943741/covering-the-world-global-evidence-on-covered-calls) · [summary](https://www.cxoadvisory.com/equity-options/covered-equity-index-calls-worldwide/)
3. **Israelov, R. & Nielsen, L. N. (2014), "Covered Call Strategies: One Fact and Eight Myths," *Financial Analysts Journal* 70(6), 23–31.** Peer-reviewed. Supplies the 51%-position-reduction equivalence and the finding that only ~11% of an ATM premium is volatility compensation — the two facts that should drive the build's UI. [PDF](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/FAJ-Covered-Call-Strategies-One-Fact-and-Eight-Myths.pdf)
4. **Israelov, R. & Ndong, D. (2023), "A Devil's Bargain: When Generating Income Undermines Investment Returns," QVR Advisors (later *Journal of Alternative Investments*).** Asset-manager research by the anchor paper's own author, reaching a largely negative conclusion. The 2011–2023 numbers are the strongest disconfirming evidence in the strand. [CXO summary](https://cxoadvisory.com/equity-options/beat-the-market-with-covered-calls) · [Swedroe summary](https://alphaarchitect.com/covered-calls/)
5. **O'Donovan, J. & Yu, G. Y. (2024/2025), "A Transaction Cost Perspective on Option Anomalies," SSRN 4806038.** Working paper. The decisive evidence against single-name delta-hedged option strategies at retail: 17 of 24 sorts significant gross, none net. Establishes that hedging frequency is first-order for costs. [SSRN](https://papers.ssrn.com/abstract=4806038)
6. **CME Group, "Frequently Asked Questions: Micro E-mini Equity Index Futures."** Exchange primary source for MES/MNQ multipliers, ticks, cycle, settlement and hours — the specs underpinning the retail-feasibility verdict. [cmegroup.com](https://www.cmegroup.com/articles/faqs/micro-e-mini-equity-index-futures-frequently-asked-questions.html)
7. **S&P Dow Jones Indices, "The S&P 500 Stock Covered Call Index: Why, When and How It Works."** Index-provider research (not peer-reviewed). The only systematic single-name buy-write benchmark found, and the source of the ~150 bps/yr single-name trading-cost figure that kills the single-name case. [PDF](https://www.spice-indices.com/idpfiles/spice-assets/resources/public/documents/research-sp-500-stock-covered-call-index-why-when-and-how-it-works.pdf)
8. **Dörries, J., Korn, O. & Power, G. J. (2021), "How to Harvest Variance Risk Premiums for the Long-Term Investor."** Academic working paper with explicit, documented cost assumptions (25% of quoted spread, 3 bp underlying hedge). Shows a **static initial-delta-only hedge** is net-profitable and ranks the retail-reachable structures. [PDF](https://www.fernuni-hagen.de/bwlbuf/docs/how_to_harvest_variance_risk_premiums_for_the_long-term_investor_.pdf)
9. **Israelov, R. (2023), "Rebalance Timing Luck in Option Overlays," CQF Institute presentation.** Practitioner research, gross of costs. Quantifies tranche-timing luck at ~40% of strategy volatility and gives the 0.27 cross-tranche delta correlation that underpins the laddering rung. [PDF](https://www.cqfinstitute.org/sites/default/files/8%20-%20Roni%20Israelov_230323.pdf)
10. **Augustin, P., Cheng, I.-H. & Van den Bergen, L. (2021), "Volmageddon and the Failure of Short Volatility Products," *Financial Analysts Journal* Q3 2021.** Peer-reviewed. Settles the short-vol-ETP question definitively: >90% one-day loss, reflexive rebalancing loop. [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2021/volmageddon-failure-short-volatility-products)

*Honourable mentions, used above:* Bondarenko (2016) on PUT/WPUT, via [CXO Advisory](https://www.cxoadvisory.com/equity-options/performance-of-cboe-putwrite-indexes); the Copenhagen Business School thesis on [daily versus weekly hedging](https://research-api.cbs.dk/ws/portalfiles/portal/60757092/307507_Confronting_the_volatility_risk_premium_on_the_S_P500_index.pdf) (weak but the only frequency comparison found); [Early Retirement Now Part 13](https://earlyretirementnow.com/2025/01/14/options-trading-series-part-13-year-2024-review/) as the only live retail account found that is explicitly structured around this decomposition.

### Labelling note
- **Peer-reviewed:** Israelov & Nielsen 2014 & 2015 (FAJ); Israelov, Klein & Tummala 2017 (Journal of Risk); Augustin, Cheng & Van den Bergen 2021 (FAJ).
- **Asset-manager research (AQR/QVR), not marketing but not independent:** all of the above were AQR-authored while Israelov was there; Israelov & Ndong 2023 and the CQF presentation are QVR-era.
- **Asset-manager marketing, excluded from the evidence base:** Swan Global Investments' "Escaping the Devil's Bargain" (Advisor Perspectives, 2024) is a promotional piece for its own product and contains no decomposition, no costs and no performance figures for the strategy it promotes; Vontobel's and Global X's covered-call pieces likewise. Cboe's benchmark-index commentary and S&P's SPXCC paper are index-provider research with a commercial interest in the indices they describe.
- **Working papers / theses, treated as weaker:** O'Donovan & Yu; Dörries, Korn & Power; the CBS thesis.
- **Own arithmetic, clearly flagged in the text:** the ~130 bps/yr prize; the 5–10 bps/yr MES hedging cost; the granularity table; the ~35–50% early-roll estimate; the ~49% laddering variance reduction; the SPXCC Sharpe ratios; the delta-reconciliation of the Devil's Bargain numbers.
