# Research Strand 11 — Position Sizing, Risk Management, Capital Efficiency, and After-Tax Return

**Date:** 11 November 2026
**Scope:** Personal, single-user US options research tool. Retail account. No commercial deployment.
**Builds on:** Prior nine strands establishing that selection/direction edge is ~7 bp/month, t = 0.45, i.e. statistically indistinguishable from zero; and that margin enforcement turns short-premium Sharpe ratios negative (Santa-Clara & Saretto).

---

## HEADLINE CONCLUSION BEFORE THE DETAIL

Three findings dominate everything else in this strand:

1. **The sizing arithmetic, applied honestly to a t = 0.45 edge, returns a number very close to zero.** Crane's (2026) Theorem 38(i) gives a hard threshold: growth is positive only when the true edge exceeds α/2 of the estimated edge, where α is the Kelly fraction. A t-statistic of 0.45 means the 95% confidence interval on the edge spans zero, so the robust κ_min is effectively ≤ 0. The defensible Kelly fraction is 5–15%, and after the cost drag documented in the execution strand the Kelly stake on a 52%-accuracy direction signal is *negative*.

2. **The recovery arithmetic is the binding constraint, not the drawdown arithmetic.** With an annual edge of ~84 bp, recovering a 20% drawdown takes ln(1.25)/ln(1.0084) ≈ **27 years**. A 50% drawdown takes **83 years**. With near-zero drift, a drawdown is not a setback; it is permanent. This single calculation is the strongest argument in the entire specification for very small size.

3. **The tax choice is worth more than the signal.** The SPX-vs-SPY instrument decision is worth ~10.2 percentage points of gross P&L (26.8% vs 37.0% top marginal rate). At a 10% gross return on capital that is 102 bp/year — larger than the entire 84 bp/year measured gross directional edge. **The developer's highest-expected-value engineering hour is spent on the tax module, not the signal module.**

---

# SECTION 1 — KELLY AND FRACTIONAL KELLY FOR OPTIONS

### 1.1 Kelly with an estimated edge — the central result for this build

**CLAIM:** When the edge is overestimated by a factor 1/κ, a trader sizing at fraction α of Kelly achieves positive growth only if κ > α/2 — so full Kelly tolerates at most a 2× overestimate, half Kelly a 4× overestimate, and quarter Kelly an 8× overestimate.
**SOURCE:** Harry Crane, "The Kelly Criterion with an Estimated Edge," Researchers.One, September 2026. https://researchers.one/articles/26.09.00001.pdf — **working paper, pre-peer-review, mathematically explicit (Theorem 38)**
**EVIDENCE STRENGTH:** Strong (a theorem, not an empirical claim; the proof is self-contained)
**IMPLICATION FOR THE BUILD:** This is the single most important quantitative result in this strand. It converts "edge uncertainty" into a sizing cap. The developer's edge has t = 0.45; if the point estimate is 7 bp/month then SE ≈ 7/0.45 = 15.6 bp, and the 95% interval is roughly [−23.5, +37.5] bp. The implied range for κ = true/estimated is approximately [−3.4, +5.4]. Because the lower bound is negative, no α has a *guaranteed* positive growth rate. The honest reading is that the app must not present a Kelly number at all without the κ sensitivity beside it.

**CLAIM:** Crane's optimal fraction of Kelly is α̅ = 2 log(1−E) / (log(1−E) + log π) = 2/(1+θ_min), where E is the stop-loss as a fraction of bankroll and π the tolerated probability of hitting it; worked values are 46% Kelly (E=50%, π=0.10), 38% (E=50%, π=0.05), 30% (E=50%, π=0.02) and 14% (E=25%, π=0.02).
**SOURCE:** Crane 2026, Theorem 18 / eq. 21 and Example 22. **Working paper.**
**EVIDENCE STRENGTH:** Strong (derivation)
**IMPLICATION FOR THE BUILD:** This replaces the folklore "use half Kelly" with a formula the app can actually evaluate from two user inputs the developer can state honestly: how much he is willing to lose before stopping (E), and how unlucky he is prepared to be (π). Crane's own framing is that the familiar 10–50% Kelly range is a special case of this formula, not a universal constant. **Implement this as the sizing primitive.**

**CLAIM:** Crane's robust prescription is to scale the fraction by κ_min, giving ~15% of Kelly for κ_min = 0.5 and ~7.5% for κ_min = 0.25; he suggests 15–23% as prudent for κ_min between 1/2 and 3/4.
**SOURCE:** Crane 2026, Theorem 38(iv). **Working paper.**
**EVIDENCE STRENGTH:** Strong (derivation)
**IMPLICATION FOR THE BUILD:** Hard-code the ceiling at **15% of Kelly** and make it a constant the user cannot raise through the UI without a confirmation that states the κ assumption it implies.

**CLAIM:** Overestimating the edge degrades the *evidential* value of a stop-loss, not just the growth rate: at α̅ = 0.30, E = 50%, π = 0.02, an edge overestimated by one-third (κ = 0.75) raises the premature-stop probability from 2% to 6.4%, and at κ = 0.50 to 20.1% — so hitting the stop carries roughly 5-to-1 evidence against the assumed edge rather than 50-to-1.
**SOURCE:** Crane 2026, Theorem 38(iii). **Working paper.**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** This gives the app a principled *kill-switch* semantics. Crane's Lemma 5 shows that with no edge the stop-loss is hit with probability 1, and hitting it therefore has likelihood ratio at least 1/π against the assumed edge. So the app should log, at trade time, the π it sized for — and when the stop is hit, display the implied likelihood ratio against the edge hypothesis. That is a far better feedback mechanism than a P&L chart.

### 1.2 Shrinkage under parameter uncertainty — independent confirmation

**CLAIM:** Because Kelly treats an estimated win probability as if it were known, the stake should be shrunk in the presence of parameter uncertainty; simulation and tennis-betting data both show shrunken Kelly beats raw Kelly out of sample.
**SOURCE:** R.D. Baker & I.G. McHale, "Optimal Betting Under Parameter Uncertainty: Improving the Kelly Criterion," *Decision Analysis* (INFORMS) 10(3): 189–199, 2013. https://salford-repository.worktribe.com/output/1410355/ — **peer-reviewed**
**EVIDENCE STRENGTH:** Strong (peer-reviewed, with both simulation and empirical validation)
**IMPLICATION FOR THE BUILD:** Confirms Crane from an independent, peer-reviewed direction. Two sources from different literatures converging on "shrink the stake" is as good as this question gets. The app should treat the Kelly output as a *ceiling to shrink from*, never as a target.

### 1.3 Why full Kelly is specifically wrong for options — the skew asymmetry

**CLAIM:** Kelly's prescription is radically asymmetric in skew at identical expected return: a positively skewed bet (10% chance of 10-to-1, 90% total loss, +10% EV) gets **1% of bankroll**, while a negatively skewed bet with the same +10% EV (90% chance of +22.22%, 10% total loss) gets **nearly half the bankroll**.
**SOURCE:** Moontower, "Kelly Math Weirdness," https://moontowermeta.com/kelly-math-weirdness/ — **practitioner**
**EVIDENCE STRENGTH:** Moderate (the arithmetic is verifiable and correct; the source is a blog, but the computation is elementary)
**IMPLICATION FOR THE BUILD:** This is the crux of "why Kelly is wrong for options." Long options are the first case (tiny Kelly stake); short premium is the second (enormous Kelly stake). **A naive Kelly engine applied to a short-strangle recommendation will return a catastrophically large number**, because Kelly only sees the bounded-loss arithmetic of the modelled distribution and not the gap risk that makes the real left tail unbounded-in-practice. Mitigation the app must implement: compute Kelly against a *stressed* loss distribution (the realised worst case, not the modelled one), and apply a separate hard notional cap for short-premium structures that is not derived from Kelly at all.

**CLAIM:** A full-Kelly bettor has roughly a 1-in-3 chance of halving the bankroll before doubling it; half Kelly reduces this to 1-in-9, halving risk while giving up about a quarter of expected growth.
**SOURCE:** W. Poundstone, *Fortune's Formula* (2005), as relayed in Moontower above. **Popular/practitioner.**
**EVIDENCE STRENGTH:** Moderate (standard result, widely reproduced)
**IMPLICATION FOR THE BUILD:** Useful as the user-facing explanation of why the app refuses to size at full Kelly. Crane's Corollary 8 gives the sharper version: a full-Kelly bettor hits any stop-loss E with probability exactly 1−E, independent of payoff odds. Crane's Theorem 26 "cube law" gives half Kelly a premature-stop bound of (1−E)³ — for E = 50% that is 12.5%.

**CLAIM:** Euan Sinclair proposes an explicit downward adjustment to full Kelly for strongly negatively skewed option bets.
**SOURCE:** Referenced in Moontower above; primary source not retrieved. **Practitioner.**
**EVIDENCE STRENGTH:** Weak (existence verified, content not verified)
**IMPLICATION FOR THE BUILD:** Flag as an open item. Sinclair's *Volatility Trading* and *Positional Option Trading* are the practitioner canon here and should be read directly rather than relied on second-hand.

---

# SECTION 2 — RISK OF RUIN, DRAWDOWN, AND TIME TO RECOVERY

### 2.1 Expected maximum drawdown

**CLAIM:** Expected maximum drawdown can be related analytically to mean return and Sharpe ratio, and risk-adjusted measures like the Calmar ratio require scaling laws to compare track records of different lengths.
**SOURCE:** Malik Magdon-Ismail & Amir F. Atiya, "Maximum Drawdown," *Risk Magazine* 17(10): 99–102, October 2004. https://papers.ssrn.com/abstract=874069 — **practitioner journal, technically refereed**
**EVIDENCE STRENGTH:** Moderate (paper and scope verified; the closed-form expression itself was not retrieved — the SSRN landing page carries only the abstract)
**IMPLICATION FOR THE BUILD:** The important consequence, which follows from the standard Brownian-motion result rather than from the paper's specific algebra: **for a drifting process, expected MDD grows logarithmically in horizon, but for a zero-drift process it grows as σ√T — without bound.** A strategy with t = 0.45 is statistically a zero-drift process. The app therefore cannot offer a "maximum expected drawdown" figure that stabilises with more data; the honest display is a drawdown distribution that widens with horizon. **Do not display a single MDD number.**

### 2.2 The recovery asymmetry — the decisive arithmetic

**CLAIM:** Recovering a drawdown d requires a gain of d/(1−d), so 20% requires 25%, 50% requires 100%, and 80% requires 400%.
**SOURCE:** Elementary; widely reproduced, e.g. https://dev.to/pickuma/the-drawdown-recovery-math-why-a-50-loss-needs-a-100-gain-4i1j — **practitioner**
**EVIDENCE STRENGTH:** Strong (arithmetic identity)
**IMPLICATION FOR THE BUILD:** The identity is trivial. What is *not* trivial, and what the specification is missing, is combining it with the measured edge. Full arithmetic:

> Measured gross edge: 7 bp/month = 0.84%/year.
> Time to recover drawdown d at annual growth g: **t = ln(1/(1−d)) / ln(1+g)**
>
> | Drawdown | Gain needed | Years to recover at g = 0.84% | at g = 5% |
> |---|---|---|---|
> | 5% | 5.3% | 6.1 | 1.1 |
> | 10% | 11.1% | 12.6 | 2.2 |
> | 20% | 25.0% | **26.7** | 4.6 |
> | 35% | 53.8% | 51.4 | 8.8 |
> | 50% | 100.0% | **82.9** | 14.2 |
>
> At the *measured* edge, a 20% drawdown is a 27-year event and a 50% drawdown exceeds an investing lifetime.

This table should be rendered **inside the app**, on the sizing screen, parameterised by the user's own realised return. It is the most persuasive risk control the tool can offer, because it is arithmetic rather than opinion and it cannot be argued with.

### 2.3 Risk of ruin for a sequence of skewed bets

**CLAIM:** With no edge, any fixed stop-loss level is reached with probability 1 given enough bets.
**SOURCE:** Crane 2026, Lemma 5. **Working paper.**
**EVIDENCE STRENGTH:** Strong (standard random-walk recurrence result)
**IMPLICATION FOR THE BUILD:** Ruin is certain, not probable, for a zero-edge strategy trading indefinitely. The only two levers are (a) bet size, which sets *how long* it takes, and (b) a pre-committed stopping rule. **The app must therefore require the user to specify a total-capital stop before it will size a single trade**, and should state plainly that this stop will eventually be hit if the edge is truly zero.

**CLAIM:** Standard risk-of-ruin formulations for sequences of bets are available in practitioner literature but are built on i.i.d. assumptions that fail for option portfolios.
**SOURCE:** NexusFi risk-of-ruin reference, https://nexusfi.com/a/risk-management/risk-of-ruin; Options Trading IQ, https://optionstradingiq.com/risk-of-ruin/ — **practitioner**
**EVIDENCE STRENGTH:** Weak
**IMPLICATION FOR THE BUILD:** Do not implement a closed-form risk-of-ruin calculator. The i.i.d. assumption is violated precisely in the scenario that matters — the correlated multi-position loss. Use Monte Carlo over the *joint* position set with a correlation shock instead (see §4).

---

# SECTION 3 — VOLATILITY TARGETING AND POSITION SCALING

This is the sub-question where the prior research's suspicion (t-stat dropping 4.34 → 1.68 without vol scaling) is largely **vindicated**. The literature splits cleanly: vol targeting robustly reduces tail risk, but its Sharpe improvement is substantially a disguised momentum bet and does not survive out-of-sample portfolio construction.

**CLAIM:** Volatility scaling US equities to a 10% target (1927–2017) raised the Sharpe ratio from 0.40 to 0.48–0.51 and cut vol-of-vol from 4.6% to 1.8%; the improvement held in all 10 industry portfolios and in two of three 30-year subsamples, failing in 1957–1987.
**SOURCE:** Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert, "The Impact of Volatility Targeting," *Journal of Portfolio Management*, 2018. https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf — **peer-reviewed**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Vol targeting is real for equities and credit. But see the next claim before using it as a return enhancer.

**CLAIM:** The Sharpe improvement from vol targeting is driven by the leverage effect and is largely explained by momentum: one-month momentum explains 45% of cross-asset variation in Sharpe improvement at a 20-day half-life and 60% at a 90-day half-life; the leverage effect exists only in equities and credit, and in other assets vol scaling amounts to an inadvertent mean-reversion bet.
**SOURCE:** Harvey et al. 2018, as above. **Peer-reviewed.**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** **This directly answers the strand question.** Vol targeting is not a free improvement; it is a position-sizing rule that *embeds a momentum signal*. If the developer's direction module is anything other than momentum, vol scaling adds a second, undeclared bet. If it *is* momentum, vol scaling double-counts it. Either way the app must label vol scaling as a signal, not as risk management, in the return accounting — while separately crediting it for the tail-risk benefit below.

**CLAIM:** Volatility targeting reduced the likelihood of extreme returns across 60+ assets, materially improved left-tail mean shortfall, sharply reduced kurtosis, and lowered maximum drawdowns for equities and for balanced and risk-parity portfolios — even where it did nothing for the Sharpe ratio.
**SOURCE:** Harvey et al. 2018. **Peer-reviewed.**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** **This is the defensible use case.** Adopt vol targeting for tail-risk reduction and explicitly disclaim any Sharpe benefit. For a trader whose edge is zero, reducing kurtosis and MDD without expecting higher returns is exactly the right trade.

**CLAIM:** Volatility scaling *lowered* the Sharpe ratio for bonds over 1963–2017, and had negligible Sharpe effect for bonds, currencies and commodities generally.
**SOURCE:** Harvey et al. 2018. **Peer-reviewed.**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Do not generalise vol targeting beyond equity/equity-index underlyings in this tool.

**CLAIM:** Volatility-managed portfolios produce an annualised market alpha of 4.86% (s.e. 1.56) and large factor alphas (momentum 12.51%), with the market Sharpe up ~25%.
**SOURCE:** Alan Moreira & Tyler Muir, "Volatility-Managed Portfolios," NBER WP 22208 (2016), later *Journal of Finance* 2017. https://www.nber.org/system/files/working_papers/w22208/w22208.pdf — **peer-reviewed (JF version)**
**EVIDENCE STRENGTH:** Strong in-sample
**IMPLICATION FOR THE BUILD:** This is the headline result that makes vol-conditioning attractive. **It does not survive the next finding.** Note also the implementability caveats in the paper itself: baseline 99th-percentile weight of 6.4× (i.e. 6.4:1 leverage), alpha falling to 2.12% when exposure is capped at 1×, and average absolute monthly weight change of 0.73 versus 0.16 for capped versions.

**CLAIM:** Out of sample, with weights estimated from a real-time expanding window, volatility-managed portfolios *underperform*: in the base case the managed combination had a lower certainty-equivalent return than the original in **72 of 103 strategies**; for the market itself, out-of-sample Sharpe was 0.42 managed vs 0.46 unmanaged and CER 1.56% vs 1.75%. Only momentum and betting-against-beta survive robustly.
**SOURCE:** Cederburg, O'Doherty, Wang & Yan, "On the performance of volatility-managed portfolios," *Journal of Financial Economics* 138: 95–117, 2020. https://www.lehigh.edu/~xuy219/research/COWY.pdf — **peer-reviewed**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** **Decisive.** The authors' methodological point is the one that matters most for the developer: a positive spanning-regression alpha reflects the gain from an *ex-post optimal* combination of managed and unmanaged portfolios, and because the two are correlated 0.48–0.70, a managed portfolio can show positive alpha while having a *lower* Sharpe ratio. The developer must not validate any vol-scaling choice with an alpha regression. Only a real-time, expanding-window, out-of-sample CER comparison counts. They also attribute the failure to structural instability in the spanning regressions — i.e. the relationship is not stable enough to estimate.

---

# SECTION 4 — PORTFOLIO-LEVEL GREEKS

This is the thinnest area for peer-reviewed evidence; it is almost entirely practitioner craft. I label it accordingly.

**CLAIM:** Raw vega is not additive across expiries because a given change in the volatility *surface* does not shift all expiries equally; long-dated vega responds less to a short-term volatility shock, so brokers apply a term-adjustment (typically a √T-type scaling) before summing.
**SOURCE:** Interactive Brokers Risk Navigator documentation on VR(T) / term-adjusted vega (page redirected on fetch; concept confirmed in listing); Moontower, "Primer #11: Thoughts On Execution, Greeks, and Weights," https://moontower.substack.com/p/primer-11-thoughts-on-execution-greeks — **practitioner**
**EVIDENCE STRENGTH:** Weak-to-Moderate (the concept is standard and consistently described; I could not retrieve the exact IB formula — the documentation URL 302-redirected to a search page)
**IMPLICATION FOR THE BUILD:** **Do not display a single summed portfolio vega.** Display vega in expiry buckets (0–7d, 8–30d, 31–60d, 61–120d, 120d+) and, separately, a term-weighted total with the weighting scheme stated. A summed raw vega across a 7-day and a 2-year option is a meaningless number that will understate short-dated risk and overstate long-dated risk. **Open item: verify the exact IB term-adjustment formula from the current IB Risk Navigator documentation before implementing.**

**CLAIM:** Beta-weighted delta expresses positions in several underlyings as an equivalent exposure to a single index, which makes portfolio delta comparable but inherits every assumption of the beta estimate.
**SOURCE:** Practitioner standard; described in Moontower Primer #11 (above) and in broker risk tooling (thinkorswim, tastytrade). — **practitioner**
**EVIDENCE STRENGTH:** Weak (no peer-reviewed treatment located within budget)
**IMPLICATION FOR THE BUILD:** Known failure modes the app should surface rather than hide:
- Beta is estimated from a historical window and is unstable; the window length is a hidden parameter that changes the displayed risk.
- Beta rises toward 1 in crashes (see next claim), so beta-weighted delta *understates* exposure in exactly the scenario where it matters.
- It is linear, so it ignores gamma. A beta-weighted delta of zero across a book of short gamma is not flat.
- It is meaningless for an idiosyncratic event (earnings, M&A, biotech data), where the position's move has nothing to do with the index.
**Display beta-weighted delta alongside raw per-underlying delta and the beta window used — never alone.**

**CLAIM:** Realised equity correlations rise sharply in market stress, so a portfolio of positions that appears diversified under normal-period correlations collapses toward a single bet in a crash.
**SOURCE:** Well-established; within this search budget I located only practitioner restatements (e.g. Option Alpha, "Correlation research suggests diversification fails when you need it most," https://optionalpha.com/podcast/correlation-research-suggests-diversification-fails-when-you-need-it-most) and a technical treatment of correlation's effect on diversification (arXiv:0805.3397, https://arxiv.org/pdf/0805.3397). The canonical peer-reviewed sources (Longin & Solnik 2001, *JF*; Ang & Chen 2002, *JFE*) were not retrieved within budget. — **mixed**
**EVIDENCE STRENGTH:** Moderate (the phenomenon is uncontroversial in the literature; my specific citations here are weak and should be upgraded)
**IMPLICATION FOR THE BUILD:** The practical control is a **correlation-stressed concentration check**: before accepting a new position, recompute portfolio loss under a scenario where all equity correlations are set to 0.9 and all underlyings move down by the same stress percentage. If the stressed loss exceeds the portfolio limit, the position is rejected regardless of what the normal-correlation risk says. This is the only reliable defence against "accidentally holding one large correlated bet across several tickers," because the bet only reveals itself as one bet in the stress state.

**CLAIM:** Brokers impose explicit portfolio-level vega limits in their house margin logic — e.g. an alternative minimum requirement computed as worst-case net vega multiplied by a factor, with a default factor of 10.
**SOURCE:** tastytrade, "Portfolio Margin House Rules/Requirements," https://tastyworks.freshdesk.com/support/solutions/articles/43000595351 — **practitioner/primary (broker rulebook)**
**EVIDENCE STRENGTH:** Strong for what brokers actually do
**IMPLICATION FOR THE BUILD:** Useful calibration: a professional counterparty's own vega limit is "worst-case net vega × 10 must be covered by equity." The app can adopt the same shape, which has the advantage of matching the constraint the account will actually face.

---

# SECTION 5 — MARGIN REGIMES AND CAPITAL EFFICIENCY

### 5.1 Reg T (strategy-based) requirements — verified against Cboe

**CLAIM:** Cboe strategy-based minimums are: long options ≤9 months — full premium, no maintenance; long options >9 months — 75% of cost/market value; short uncovered equity options — 100% of proceeds + 20% of underlying value − OTM amount, with minimums of proceeds + 10% of underlying (calls) and 10% of the strike (puts); short uncovered **broad-based index** options — 100% of proceeds + **15%** of index value − OTM amount, same minimums; short strangles/straddles — the greater of the two single-leg requirements plus the other leg's market value.
**SOURCE:** Cboe, "Overview of Margin Requirements for Options" (Cboe Rule 10.3 minimums), https://www.cboe.com/us/options/strategy_based_margin — **primary (exchange rulebook)**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Implement these formulas directly; they are deterministic and the app can compute buying-power impact exactly for single legs and strangles. Note the exchange's own caveats: these are *minimums*, brokers may require more, and positions may be margined separately to obtain the lowest requirement. **The 15% vs 20% difference means a broad-based index short option consumes ~25% less margin than an economically similar equity short option — a capital-efficiency argument that stacks on top of the tax argument in §7.**

**CLAIM:** Cboe's rulebook page does not give a margin-account formula for vertical spreads; for cash accounts a debit spread requires the net debit in full and a credit spread requires cash equal to maximum risk less the net credit. Calendar spreads are not covered on that page.
**SOURCE:** Cboe, as above; the page refers readers to the Cboe Margin Manual (https://cdn.cboe.com/resources/membership/Margin_Manual.pdf) for spreads and combinations. — **primary**
**EVIDENCE STRENGTH:** Strong (for the gap itself)
**IMPLICATION FOR THE BUILD:** **Open item.** The app must read the Cboe Margin Manual for defined-risk spread and calendar treatment. The practical rule for a same-expiry vertical in a margin account is max-loss (width × multiplier − net credit), but this needs verification from the Manual and from the specific broker, because calendars and diagonals are where broker treatment diverges most.

### 5.2 Portfolio margin — eligibility and current requirements, verified

**CLAIM:** FINRA Rule 4210(g) interpretations (version valid from 4 June 2026) require members to set portfolio-margin minimum equity in filed Portfolio Margin Policies, and those policies may not go below: **$100,000** with full real-time intraday monitoring; **$150,000–$500,000** with partial monitoring; **$500,000** with no real-time monitoring; and **$5 million** for accounts permitted to hold unlisted derivatives.
**SOURCE:** FINRA, "Interpretations of Rule 4210 (valid from June 4, 2026)," Interpretation 4210(b)(4)/034. https://www.finra.org/rules-guidance/guidance/interps-4210-202606 — **primary (regulator), current version**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** $100,000 remains the regulatory floor and is unchanged as of the current interpretation. The app should treat $100,000 as the eligibility threshold but warn that the *broker's* number may be higher, since the regulator only sets a floor on what the broker's own policy may say.

**CLAIM:** Interactive Brokers requires **USD 110,000** net liquidation value to open/upgrade to portfolio margin and **USD 100,000** to maintain it; stress ranges are ±15% for stocks/equity options/narrow-based indices (8 intermediate points), +10%/−10% for US small caps and FINRA indices, **+6%/−8%** for broad-based and growth indices, implied-volatility shocks of ±75% for broad-based indices and ±150% for all other option classes, and a per-contract floor of **$0.375 × index**. Below $100,000 the account is restricted from margin-increasing trades and a surcharge progressively moves it toward Reg T levels.
**SOURCE:** Interactive Brokers, "Portfolio Margin," https://www.interactivebrokers.com/en/trading/marginRequirements/marginPortfolio.php — **primary (broker)**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Two things matter here. First, the asymmetry of the broad-index stress (+6%/−8%) means portfolio margin is *deliberately harsher on downside* for index positions — correct, and the app should mirror it. Second, and more important: **the progressive surcharge below $100,000 is a procyclical trap.** A portfolio-margin account that takes losses down through $100,000 does not merely stop at a limit; its margin requirement *increases toward Reg T* at the same moment its equity is falling. This is the Santa-Clara & Saretto mechanism rebuilt into the broker's rulebook, and it is the single most dangerous structural feature of portfolio margin for a retail trader near the threshold.

**CLAIM:** Broker house portfolio-margin rules add regime-dependent and idiosyncratic stress floors: equity indices at least −15%/+10% in low volatility and −20%/+15% in high volatility (low = VIX below 25 for five consecutive days or a close below 20; high = VIX above 25 for five consecutive days or a close above 30); individual equities at least ±20%; small-cap biotech at least −50%/+100%; stress tests extended by 50% in the ~3 days before earnings; a naked-option floor of 50% of deliverable value; a vega test at factor 10; and rejection of trades producing a cash balance of 15× net liquidation value or more.
**SOURCE:** tastytrade, "Portfolio Margin House Rules/Requirements," https://tastyworks.freshdesk.com/support/solutions/articles/43000595351 — **primary (broker)**
**EVIDENCE STRENGTH:** Strong (note: the page is undated and states rules are subject to change without notice — **re-verify before relying on it**)
**IMPLICATION FOR THE BUILD:** This gives the app a ready-made, professionally calibrated stress template, including something the academic literature does not: a **VIX-regime-conditioned margin requirement**. The app should replicate the regime definition exactly, because the user's buying power will change discontinuously when VIX crosses those thresholds — a predictable liquidity event the tool can and should forecast.

**CLAIM:** Portfolio margin reduces requirements for defined-risk and offsetting structures dramatically versus strategy-based margin. Cboe's own worked examples (AAPL, 19 Jan 2021, 100 contracts) show: short call $233,960 → $127,337; short put $255,660 → $135,359; short strangle $227,360 → **$75,999** (≈3.0×); long debit call spread $43,000 → $32,653; long calendar $45,000 → $18,539; **short calendar $300,460 → $7,500 (≈40×)**.
**SOURCE:** Cboe, "Margin Requirement Examples," https://cdn.cboe.com/resources/membership/Margin_Requirement_Examples.pdf — **primary (exchange)**
**EVIDENCE STRENGTH:** Strong (worked examples from the exchange)
**IMPLICATION FOR THE BUILD:** These are the real numbers, and they cut both ways. See DISCONFIRMING EVIDENCE: a 40× reduction in required capital for a short calendar is not a risk reduction, it is a 40× increase in permitted leverage for an identical economic position.

### 5.3 SPAN margin

**CLAIM:** SPAN (and CME's SPAN 2) is the futures-market portfolio risk margining framework, applying scenario-based scanning to futures and options on futures; it is relevant to a retail trader only if they trade futures options (e.g. /ES options) rather than securities options.
**SOURCE:** CME Group, "CME SPAN 2 Margin Framework," https://www.cmegroup.com/clearing/files/cme-span-2-margin-framework.pdf — **primary (clearing house)**
**EVIDENCE STRENGTH:** Moderate (framework confirmed; I did not retrieve a retail-specific capital-efficiency comparison within budget)
**IMPLICATION FOR THE BUILD:** **Largely not relevant, with one important exception.** For a securities-options trader, SPAN is out of scope. But SPAN-margined futures options are the *only* route to portfolio-style risk margining below the $100,000 securities portfolio-margin threshold, and futures options are Section 1256 contracts (§7). So for an account under $100k, /ES options offer both SPAN margining and 60/40 treatment where SPX options offer 60/40 but Reg T margining. **This is worth a dedicated comparison in the tool for small accounts, and is an open question I could not resolve within budget.** Caution: SPAN margin is lower, which again means more permitted leverage, and futures options carry their own assignment and roll mechanics.

### 5.4 PDT elimination — verified current status, and a correction to the brief

**CLAIM:** The SEC approved the FINRA Rule 4210 amendments on **15 April 2026** (the brief says 14 April), effective **4 June 2026**, eliminating the pattern-day-trader designation, the four-trades-in-five-days test, the $25,000 minimum equity requirement, day-trading buying power calculations and related special maintenance provisions, and replacing them with an intraday margin framework built on an Intraday Margin Level (IML) and Intraday Margin Deficit (IMD).
**SOURCE:** King & Spalding, "FINRA Adopts Sweeping Changes to Margin Requirements for Day Trading," https://www.kslaw.com/insights/articles/finra-adopts-sweeping-changes-to-margin-requirements-for-day-trading — **practitioner legal analysis**; FINRA Regulatory Notice 26-11, https://www.finra.org/sites/default/files/2026-05/Regulatory-Notice-26-11.pdf — **primary**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Confirmed. Note the corrected approval date.

**CLAIM:** The current minimum equity for leveraged (margin) trading is **$2,000**; accounts below that may still trade but only with available cash. Maintenance margin is 25% of long margin-eligible equity market value and must be met *throughout* the trading day, not only at the close. Firms may require more.
**SOURCE:** FINRA, "Understanding the New Intraday Margin Requirements," https://www.finra.org/investors/insights/intraday-margin-requirements — **primary (regulator)**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** The brief's framing of "broker-set intraday buying power above $2,000" is approximately right but the operative change is the *continuous* nature of the 25% test, not a new buying-power formula.

**CLAIM:** Deficits must be satisfied as promptly as possible and may remain outstanding up to 15 business days; a customer who as a practice fails to satisfy a deficit by the fifth business day must receive a 90-day freeze on new debit balances or short positions other than closing trades. Small deficits — the lesser of 5% of equity or $1,000 — have limited exceptions. FINRA guidance indicates a customer who satisfies all but three deficits in a rolling 12-month period within three business days would generally not be considered to have such a practice.
**SOURCE:** King & Spalding (above); FINRA Interpretations of Rule 4210 (from 4 June 2026), Interpretation 4210(d)(2). — **practitioner legal + primary**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** The app should track a rolling 12-month count of intraday margin deficits, because the third one in twelve months changes the user's regulatory standing. This is cheap to implement and nothing else will warn him.

**CLAIM:** Implementation is phased: firms needing more time have a transition period through **20 October 2027**. This is a phase-in for firm systems, not a sunset of the rule.
**SOURCE:** King & Spalding; FINRA investor insight (both above). — **primary + practitioner**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Confirms the brief's "runs to October 2027," with the correction that it is a phase-in, not an expiry. Broker behaviour will therefore be inconsistent until then and the app must not assume a uniform regime.

**CLAIM — IMPORTANT CORRECTION:** The new intraday margin layer applies to **stock** positions, not options. Options in a standard Reg T margin account continue under existing options margin rules with no additional intraday requirement. However, options expiring in the money on *deliverable* equities or ETFs (SPY, QQQ, single stocks) do count toward intraday margin or margin debit; cash-settled index options are unaffected. Broker support varies and some brokers did not implement immediately.
**SOURCE:** tastylive, "The PDT Rule Is Gone — Here's What Changes on June 4," https://www.tastylive.com/news-insights/the-pdt-rule-is-gone-here-s-what-changes-on-june-4 — **practitioner (broker-affiliated)**
**EVIDENCE STRENGTH:** Moderate (single broker-affiliated source; **re-verify with the developer's own broker**)
**IMPLICATION FOR THE BUILD:** **This materially deflates the brief's premise.** For an options-focused tool, PDT elimination changes very little directly. The one real consequence is the 0DTE deliverable-settlement interaction: a 0DTE SPY option that expires ITM creates a stock position and an intraday margin consequence, while an economically identical 0DTE XSP position does not. That is a third independent reason (alongside tax in §7 and the 15%-vs-20% Reg T difference in §5.1) to prefer cash-settled index options. **The app should surface this as a single combined "instrument choice" recommendation rather than three separate ones.**

---

# SECTION 6 — ASSIGNMENT, EXERCISE AND PIN RISK

**CLAIM:** OCC's exercise-by-exception ("Ex-by-Ex") threshold is **$0.01 per contract in the money**, for customer, firm and market-maker accounts alike. It is an administrative procedure between OCC and its clearing members, not a guarantee of automatic exercise for a customer.
**SOURCE:** OIC/OCC, "Options Exercise FAQ," https://www.optionseducation.org/referencelibrary/faq/options-exercise — **primary (OCC-affiliated investor education)**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Model $0.01 as the auto-exercise trigger, but display it as *the clearing default your broker may override*. The distinction matters: the customer's actual outcome is set by the broker's own threshold and cut-off, not OCC's.

**CLAIM:** The exchange cut-off for an exercise notice is **4:30 p.m. CT**, and brokers set earlier internal cut-offs for customer instructions.
**SOURCE:** OIC/OCC FAQ (above). — **primary**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** The app should hold a user-configured broker cut-off time and alert ahead of it on any expiration day with a position within, say, 2% of a strike. The broker cut-off, not the exchange cut-off, is the operative deadline.

**CLAIM:** Early exercise of an American call for dividend capture is optimal just before the ex-dividend date when the dividend exceeds the call's remaining time value: **D > C(S,K,T−t) − max(0, S−K)**, equivalently **D > K[1 − e^(−r(T−t))] + (value of the corresponding put)**.
**SOURCE:** Acadifi community reference, https://www.acadifi.com/community/early-exercise-american-call-dividend-decision — **practitioner, but the condition is the standard textbook result** (cf. Kwok, *Mathematical Models of Financial Derivatives*, ch. 5, https://www.math.hkust.edu.hk/~maykwok/courses/ma571/06_07/Kwok_Chap_5.pdf)
**EVIDENCE STRENGTH:** Strong (standard result, two independent confirmations)
**IMPLICATION FOR THE BUILD:** This is directly computable and is the highest-value assignment feature the app can build. For every short call in the book, on every day, compute extrinsic value and compare to the upcoming dividend. **Assignment risk is not random — it is predictable, and this inequality predicts it.** Flag any short call whose extrinsic value is below the dividend in the days before ex-div. The put-value form is the more accurate test and should be the one implemented, since the simple "extrinsic < dividend" heuristic ignores the interest term.

**CLAIM:** For a calendar spread where the short leg is assigned, a broker may exercise the long call to meet the resulting delivery obligation — but only if the customer has discussed this with the firm and given explicit exercise instructions for the long leg.
**SOURCE:** OIC/OCC FAQ (above). — **primary**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Critical and under-appreciated. A "defined-risk" spread is only defined-risk if the long leg actually gets exercised. If the short leg is assigned and the long leg is *not* exercised, the trader is left with a naked stock position overnight and a margin call that the spread's theoretical max loss never contemplated. **The app should display, for every spread, the overnight margin and loss exposure in the one-leg-assigned scenario — not just the theoretical max loss.** This is the single biggest gap between modelled and realised risk in spread trading.

**CLAIM:** Pin risk arises when the underlying settles at or near a short strike at expiry, leaving the trader uncertain whether assignment will occur and therefore uncertain of their Monday-morning position.
**SOURCE:** Concept is standard; the OCC FAQ did not address it. Practitioner descriptions: IBKR Traders' Insight, "Understanding Special Exercises and Pin Risk" (fetch returned a server error); Traders Agency, https://tradersagency.com/blog/options-pin-risk-expiration-assignment — **practitioner**
**EVIDENCE STRENGTH:** Weak (concept uncontroversial; I could not retrieve an authoritative treatment within budget)
**IMPLICATION FOR THE BUILD:** The practical rule is operational rather than analytical: **do not carry short options into expiration within a defined band of the strike.** Close or roll any short leg within ~1% of the underlying with less than one day to expiry. Cash-settled index options eliminate pin risk entirely, which is a fourth argument for the index-option preference. **Open item:** establish the band empirically from the user's own underlyings rather than adopting 1% by assertion.

---

# SECTION 7 — AFTER-TAX RETURN

**I am not a tax adviser and this is not tax advice.** What follows maps which rules a personal tool should model or flag and where a CPA is required. Every item marked "CPA" below should block the app from computing a number and should instead produce a flag.

### 7.1 Section 1256 and the 60/40 rule

**CLAIM:** Section 1256 contracts comprise regulated futures contracts, foreign currency contracts, nonequity options, dealer equity options and dealer securities futures contracts. Each is treated as sold at fair market value on the last business day of the tax year, and gain or loss is **40% short-term / 60% long-term regardless of holding period** (IRC §1256(a)(1)–(3)).
**SOURCE:** IRC §1256, https://www.customsmobile.com/uscode/26/1256 — **primary (statute)**; IRS Form 6781 instructions summary, https://www.teachmepersonalfinance.com/irs-form-6781-instructions — **practitioner summary of a primary form**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** The app can compute the 60/40 split mechanically. It cannot determine the user's actual bracket — that is a CPA/user input.

**CLAIM:** The statutory mechanism is that an "equity option" is one on stock or on a **narrow-based** security index (IRC §1256(g)(6)); because that definition excludes broad-based indices, options on broad-based indices fall outside the equity-option carve-out and are nonequity options receiving 1256 treatment. A "qualified board or exchange" includes any SEC-registered national securities exchange, any CFTC-designated contract market, and any other market the Secretary approves (§1256(g)(7)).
**SOURCE:** IRC §1256(g), as above. — **primary (statute)**
**EVIDENCE STRENGTH:** Strong for the mechanism; Moderate for its application to any specific ticker (see below)
**IMPLICATION FOR THE BUILD:** The app should encode the *test* (broad-based index, cash-settled, listed on a qualified board) rather than a hard-coded ticker list, and should flag rather than assert for anything outside a small verified set.

**CLAIM:** Cboe states that index options are 1256 contracts qualifying for 60/40 treatment, with SPX explicitly confirmed. Cboe's own page does **not** state the 1256 status of XSP, RUT, NDX or VIX options.
**SOURCE:** Cboe, "Index Options Benefits & Tax Treatment," https://www.cboe.com/tradable_products/index-options-benefits-tax-treatment/ — **primary (exchange)**
**EVIDENCE STRENGTH:** Strong for SPX; **No credible primary confirmation found for XSP, VIX, RUT or NDX within this search budget**
**IMPLICATION FOR THE BUILD:** **This is a correction to the brief's premise.** The brief asserts "SPX, XSP, VIX" qualify. I confirmed only SPX from a primary source. XSP and VIX options are very widely described as 1256 contracts in practitioner material, and the statutory logic in §1256(g)(6) plainly supports it (both are broad-based, cash-settled, and VIX options are options on a broad-based volatility index). But *widely described* is not *verified*, and VIX in particular has historically attracted commentary precisely because it is an option on an index of implied volatility rather than on a securities index. **The app must treat XSP, VIX, RUT and NDX as "likely 1256 — confirm with your CPA" and must not compute an after-tax number for them as though settled.** EY maintains a published Section 1256 qualified-board-or-exchange list (https://assets.ey.com/content/dam/ey-sites/ey-com/en_gl/topics/tax/tax-alerts-pdf/ey-updated-2019-section-1256-qualified-board-or-exchange-list.pdf) which should be consulted, and there is a 2026 revenue ruling in this area (IRS Rev. Rul. 26-16, https://www.irs.gov/pub/irs-drop/rr-26-16.pdf) that I did not have budget to read. **Flagged as a priority open question.**

**CLAIM:** Options on ETFs — including SPY and QQQ — are securities (equity) options, not Section 1256 contracts, and receive ordinary short-term/long-term capital treatment.
**SOURCE:** Green (GreenTraderTax), "Tax Treatment for Trading Options in 2026," https://greentradertax.com/tax-treatment-for-trading-options-in-2026-rules-pitfalls-and-planning-strategies/ — **practitioner (specialist trader-tax CPA)**; mechanism confirmed by IRC §1256(g)(6) — SPY and QQQ are stock of a trust/company, so options on them are options on stock.
**EVIDENCE STRENGTH:** Strong (the statutory mechanism is unambiguous)
**IMPLICATION FOR THE BUILD:** Safe to encode. SPY and QQQ options are 100% short-term for any realistic options holding period.

### 7.2 The SPX-vs-SPY after-tax arithmetic — the central finding of this section

**CLAIM:** The after-tax difference between economically equivalent SPX and SPY trades is approximately 10 percentage points of gross P&L at top marginal rates.
**SOURCE:** My arithmetic, from statutory rates. Cboe's own comparison uses assumptions of a 35% bracket, joint filing and a 20% LTCG rate (https://www.cboe.com/tradable_products/index-options-benefits-tax-treatment/) but presents the result only as an image.
**EVIDENCE STRENGTH:** Strong (arithmetic from statutory rates; the rates themselves require confirmation of the user's bracket)
**IMPLICATION FOR THE BUILD:** Full arithmetic:

> **Top bracket, ignoring NIIT:**
> SPX (1256): 0.60 × 20% + 0.40 × 37% = 12.0% + 14.8% = **26.8%**
> SPY (equity option, short-term): **37.0%**
> Difference: **10.2 percentage points**
>
> **Including the 3.8% net investment income tax:**
> SPX: 0.60 × 23.8% + 0.40 × 40.8% = 14.28% + 16.32% = **30.6%**
> SPY: **40.8%**
> Difference: **10.2 percentage points**
>
> **At the 35% bracket (Cboe's assumption), no NIIT:**
> SPX: 0.60 × 20% + 0.40 × 35% = **26.0%**; SPY: **35.0%**. Difference **9.0 pp**.
>
> **After-tax retention:** SPX keeps 73.2% of gross versus SPY's 63.0% — an uplift of 0.732/0.630 − 1 = **+16.2% more after-tax profit for identical gross P&L.**
>
> **Against the measured edge:** if gross return on deployed capital is 10%/year, the 10.2 pp rate difference is worth 1.02% of capital per year = **102 bp/year**, versus the measured gross directional edge of 7 bp/month = **84 bp/year**.

**The instrument choice is worth more than the signal.** And unlike the signal, it is certain, requires no forecasting ability, and has a t-statistic that does not apply because it is a rate, not an estimate. This should reorder the build priorities.

Stacking the other three reasons found in this strand, the preference for cash-settled broad-based index options over ETF options rests on four independent grounds:
1. **Tax:** ~10.2 pp of gross P&L (§7.2).
2. **Margin:** Reg T short-option requirement is 15% of index value vs 20% of underlying value (§5.1).
3. **Intraday margin:** no deliverable-settlement consequence for ITM 0DTE (§5.4).
4. **Pin/assignment:** cash settlement eliminates pin risk and early assignment entirely (§6).

### 7.3 Mark-to-market and the loss carryback

**CLAIM:** 1256 positions held at year end are deemed sold at FMV on the last business day; the wash-sale rules do not apply to them. A net Section 1256 loss may be **carried back 3 years** by election (Form 6781 Box D), limited to the smaller of (a) 1256 losses exceeding 1256 gains plus $3,000 ($1,500 MFS) or (b) total short- and long-term capital loss carryovers computed as if line 6 were zero; the amount carried to any prior year is capped by that year's 1256-only Schedule D line 16 gain and by its actual line 16 gain. Corporations, partnerships, estates and trusts cannot elect.
**SOURCE:** IRS Form 6781 and instructions, as summarised at https://www.teachmepersonalfinance.com/irs-form-6781-instructions — **practitioner summary of a primary form**; carryback mechanics corroborated by Thomson Reuters UltraTax guidance, https://www.thomsonreuters.com/en-us/help/ultratax-cs/1040/carrybacks-and-carrying-forward/carry-back-a-net-section-1256-contracts-loss
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Two distinct consequences. (a) **Modellable:** year-end MTM means the app can compute an unrealised-gain tax accrual on open 1256 positions and should display tax-adjusted rather than gross unrealised P&L. (b) **CPA:** the carryback election is genuinely valuable for a loss-making year — it converts a capital loss trapped behind the $3,000 annual limit into a refund of tax paid in up to three prior years — but the limitation stack is multi-layered and interacts with the user's whole return. **The app should flag "net 1256 loss this year — ask your CPA about the 3-year carryback election on Form 6781 Box D" and compute nothing.**

### 7.4 Straddle rules — directly relevant to a tool that recommends spreads

**CLAIM:** Under IRC §1092, positions are offsetting when holding one substantially reduces the risk of loss on another; a loss on one position is deductible only to the extent it exceeds unrecognised gain on the offsetting positions, and the disallowed loss carries forward to the next year subject to the same limit.
**SOURCE:** IRC §1092(a)(1) and (c)(2)(A), https://www.govinfo.gov/content/pkg/USCODE-2011-title26/pdf/USCODE-2011-title26-subtitleA-chap1-subchapO-partVII-sec1092.pdf — **primary (statute)**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** **This is the tax rule most directly threatened by the app's core function.** A tool that recommends spreads is a tool that recommends straddles in the §1092 sense. Vertical, horizontal (calendar) and diagonal spreads, iron condors and butterflies are all cited as examples attracting straddle treatment. The concrete consequence: close the losing leg in December and the loss may be deferred to the following year if the winning leg is still open with unrealised gain. A worked example in the practitioner literature: a $6,000 realised loss against a $10,000 unrealised gain in the offsetting leg defers the entire $6,000.
**SOURCE for the example:** GreenTraderTax 2026 (above). — **practitioner**

**CLAIM:** Positions are *presumed* offsetting if they are in the same property, in debt instruments of similar maturity, marketed as offsetting, or carry a combined margin requirement lower than the sum of the separate requirements — for most categories additionally requiring that the values tend to move inversely. The presumption is rebuttable.
**SOURCE:** IRC §1092(c)(3), as above. — **primary**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Note the chilling implication of the margin-offset presumption: **the very capital efficiency that makes portfolio margin and spread margining attractive (§5.2) is itself a statutory presumption that the positions are an offsetting straddle.** The app should detect this explicitly — if the broker charged less margin for the pair than for the two legs separately, flag a probable straddle.

**CLAIM:** Straddle rules can also require capitalising carrying costs such as margin interest rather than deducting them.
**SOURCE:** GreenTraderTax 2026 (above). — **practitioner**
**EVIDENCE STRENGTH:** Moderate (consistent with §263(g), which I did not read)
**IMPLICATION FOR THE BUILD:** CPA. Flag only.

**CLAIM:** The identified-straddle election (§1092(a)(2)) requires clear identification in the taxpayer's records by the close of the day the straddle is acquired; instead of deferring the loss, the loss is added to the basis of the offsetting positions, allocated by a ratio based on unrecognised gain. For identified straddles established after 21 October 2004, losses are not allowed at all — basis of the offsetting positions increases instead.
**SOURCE:** IRC §1092(a)(2), as above; Form 6781 Part II Section A instructions (above). — **primary**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** **Highest-value tax feature in the whole app, and purely a record-keeping problem.** The statute requires same-day identification. A trader who does not identify on day one cannot elect later. So the app should offer, at the moment a spread is opened, a one-click "record as identified straddle" that writes an immutable timestamped record with the legs, quantities and acquisition date. The app cannot decide whether to make the election — that is a CPA judgement — but it is the only system in a position to create the contemporaneous record that preserves the option. **This is a feature only the tool can provide, and it costs almost nothing to build.**

**CLAIM:** A mixed straddle is a straddle in which at least one but not all positions are 1256 contracts. Three elections exist: the §1256(d) mixed-straddle election (Box A, exempting the 1256 legs from MTM, requiring identification on the day the first 1256 contract is acquired, applying to all later years and irrevocable without IRS consent); straddle-by-straddle identification (Box B); and the mixed straddle account (Box C, established by the return's unextended due date).
**SOURCE:** Form 6781 instructions (above); IRC §1256(d). — **primary form / statute**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Highly relevant and dangerous: **hedging an SPX position with SPY options, or an SPX option with SPY stock, creates a mixed straddle.** The app should detect cross-instrument hedges spanning the 1256 boundary and flag them loudly, since the elections are irrevocable and date-constrained. CPA decision; app provides detection and the contemporaneous record only.

### 7.5 Wash sales

**CLAIM:** A loss is disallowed when a substantially identical position is acquired within 30 days before or after the sale; the disallowed loss is added to the basis of the replacement position. Applied to options, the rule reaches across expirations, across stock-and-option combinations, and across all of a taxpayer's accounts including IRAs. Form 1099-B generally reflects single-account activity and can therefore miss wash sales.
**SOURCE:** GreenTraderTax 2026 (above) — **practitioner (specialist)**; IRC §1091 is the governing provision.
**EVIDENCE STRENGTH:** Moderate (the practitioner source is a recognised specialist and the broad shape is uncontroversial; the "substantially identical" boundary for options across strikes and expirations is genuinely unsettled)
**IMPLICATION FOR THE BUILD:** What the app can compute: a conservative, over-inclusive wash-sale detector across the user's full position history, treating same-underlying same-direction options within 30 days as *candidates*. What it must not do: assert whether a different strike or expiration is "substantially identical." There is no bright-line rule, the practitioner literature is openly divided, and I found no revenue ruling settling it within budget. **CPA, with app-provided candidate detection.** Note the two useful interactions: (a) 1256 contracts are not subject to wash sales because of year-end MTM, so SPX trading sidesteps this entirely — a fifth argument for index options; (b) the cross-account reach, including IRAs, means a loss in the taxable account can be disallowed by a purchase in the IRA, which brokers will never report and only the user's own tool can catch.

### 7.6 Short-term versus long-term, and why options trading is almost all short-term

**CLAIM:** Equity options follow ordinary capital-gain rules requiring a holding period over one year for long-term treatment, so virtually all options trading produces short-term gains; 1256 contracts get 60% long-term regardless of holding period.
**SOURCE:** IRC §1256(a)(3) (above); GreenTraderTax 2026. — **primary + practitioner**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** This is *why* §7.2 matters so much. The 60/40 rule is not a modest rate preference; it is the only route to long-term treatment available to a short-horizon options trader. The app should state the comparison as "SPX gives you 60% long-term treatment on a 3-day trade; SPY cannot give you long-term treatment on any trade."

### 7.7 Qualified covered calls

**CLAIM:** A straddle consisting only of qualified covered call options and the optioned stock is not treated as a straddle, provided it is not part of a larger straddle. To qualify, the option must be exchange-traded, granted more than 30 days before expiration, not deep-in-the-money, not granted by an options dealer in dealing activity, and must not produce ordinary gain or loss (§1092(c)(4)).
**SOURCE:** IRC §1092(c)(4), https://www.govinfo.gov/content/pkg/USCODE-2011-title26/pdf/USCODE-2011-title26-subtitleA-chap1-subchapO-partVII-sec1092.pdf — **primary (statute)**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** Encode the qualification tests as a checklist. The >30-day test and the exchange-traded test are mechanical. The deep-ITM test is not (next claim).

**CLAIM:** Writing a non-qualified covered call against stock held less than one year **terminates** the stock's holding period. If stock and call are closed together the net result is short-term; if the call is closed first, a new holding period begins the day the call is closed. An in-the-money *qualified* covered call **suspends** the holding period while open; at- or out-of-the-money qualified calls do not affect it. Separately, if a call is closed at a loss in one year and the stock sold at a gain the next, the stock must be held at least 30 days from the call's disposition to avoid loss deferral.
**SOURCE:** Fidelity/Cboe, "Tax implications of covered calls," https://www.fidelity.com/learning-center/investment-products/options/tax-implications-covered-calls — **practitioner (note: the page is a 2013 Cboe article and states tax laws may change — re-verify)**
**EVIDENCE STRENGTH:** Moderate (consistent with the statute; the source is dated)
**IMPLICATION FOR THE BUILD:** **This is the trap the brief correctly anticipated.** A tool that recommends covered calls can silently destroy a long-term holding period worth 17 percentage points of tax rate (37% vs 20%) on an entire stock position — a cost that will dwarf the call premium collected. Concretely: on a $100,000 position with a $40,000 unrealised gain approaching the one-year mark, breaking the holding period costs 0.17 × $40,000 = **$6,800**. No realistic covered-call premium compensates for that. **The app must refuse to recommend a covered call on any lot with an unrealised gain and a holding period under 12 months without a blocking warning that quantifies the holding-period cost.** The "not deep in the money" test lacks a numeric definition in the sources I retrieved — the only guideline found is in-the-money by no more than one strike, and the governing detail is in Treas. Reg. §1.1092(c)-2 / §1.1092(c)-4 (https://www.law.cornell.edu/cfr/text/26/1.1092(c)-2), which I did not read within budget. **Open item; CPA for the boundary cases.**

### 7.8 Tax treatment on assignment and exercise

**CLAIM:** On exercise or assignment the option premium is folded into the basis or proceeds of the underlying rather than being a separate gain or loss, and the resulting holding period runs from the stock acquisition.
**SOURCE:** Standard treatment described in GreenTraderTax 2026 and Fidelity (both above). — **practitioner**
**EVIDENCE STRENGTH:** Moderate (uncontroversial, but I did not reach a primary citation within budget)
**IMPLICATION FOR THE BUILD:** The app must not treat an assignment as closing the option position for P&L purposes. Mechanically: an assigned short put reduces the stock's basis by the premium received; an exercised long call increases it. Modellable. Combined with §7.7, the app needs a **lot-level tax ledger**, not a trade-level one — the holding period and basis of specific share lots determine the tax outcome, and no broker statement will track the interaction with options correctly.

---

# SECTION 8 — REGIME CONDITIONING FOR RISK

**CLAIM:** Brokers already condition portfolio-margin stress tests on the VIX regime, defining low volatility as VIX below 25 for five consecutive days or a close below 20, and high volatility as VIX above 25 for five consecutive days or a close above 30, and widening equity-index stress from −15%/+10% to −20%/+15% in the high regime.
**SOURCE:** tastytrade house portfolio margin rules (above). — **primary (broker)**
**EVIDENCE STRENGTH:** Strong (for what brokers do)
**IMPLICATION FOR THE BUILD:** The most actionable regime finding in this strand, and notably it is *not* from the academic literature. Regime conditioning of risk is already happening to the user whether he models it or not, and it is procyclical: his buying power contracts exactly when volatility rises. The app should model the broker's own regime rule and warn when VIX approaches a threshold, because crossing it is a predictable margin event.

**CLAIM:** The VIX futures basis has predictive content for VIX futures returns and has been studied as a tradable signal.
**SOURCE:** D.P. Simon & J. Campasano, "The VIX Futures Basis: Evidence and Trading Strategies," *Journal of Derivatives* 21(3): 54–, Spring 2014 — **peer-reviewed**. URL robots-disallowed (https://www.pm-research.com/content/iijderiv:::21:::3:::54.full.pdf); secondary summary at Quantpedia, https://quantpedia.com/strategies/exploiting-term-structure-of-vix-futures
**EVIDENCE STRENGTH:** Weak as cited — **I could not retrieve the paper and therefore cannot report its magnitudes.** The existence and provenance of the paper are confirmed.
**IMPLICATION FOR THE BUILD:** Do not use. Flagged as an open item. Note also that this is a *signal* result, not a *sizing* result, and the strand brief correctly distinguishes them.

**CLAIM:** Conditioning exposure on volatility produces large in-sample alphas (market 4.86%/yr) that **do not survive real-time implementation**, underperforming in 72 of 103 strategies on certainty-equivalent return.
**SOURCE:** Moreira & Muir 2016/2017 and Cederburg, O'Doherty, Wang & Yan, *JFE* 2020 (both above). — **both peer-reviewed**
**EVIDENCE STRENGTH:** Strong
**IMPLICATION FOR THE BUILD:** **This is the answer to the strand's regime question.** There is good evidence that conditioning position size on regime reduces tail risk (Harvey et al.) and essentially no surviving out-of-sample evidence that it improves returns (Cederburg et al.). The honest design: use regime to **cut size in stress, never to add size in calm.** An asymmetric rule captures the documented tail benefit without relying on the return claim that failed replication. A symmetric rule — levering up in low volatility — relies entirely on the part of the literature that did not survive.

**CLAIM:** Realised correlation and credit spreads as risk-regime indicators.
**EVIDENCE STRENGTH:** **No credible evidence found** within this search budget that conditioning *position size* on realised correlation or credit spreads improves outcomes for an options trader. The searches returned practitioner commentary only.
**IMPLICATION FOR THE BUILD:** Do not implement as a sizing input. Realised correlation is still worth *displaying*, because it is the direct input to the correlation-stressed concentration check in §4, which is a limit rather than a forecast.

---

# SIZING RULE RECOMMENDATION

A concrete, defensible rule for a trader whose measured edge is indistinguishable from zero, with the arithmetic shown.

### Step 0 — Establish that Kelly returns a negative number, and say so

Binary framing of the direction module at its best realistic case. Let p = win probability, b = net payoff per unit risked after costs.

> **At p = 0.52, b = 1.0 (costless):** f\* = 2p − 1 = **+4.0%** of capital.
> **At p = 0.52, b = 0.90 (10% round-trip cost drag):**
> f\* = (p·b − q)/b = (0.52 × 0.90 − 0.48)/0.90 = (0.468 − 0.480)/0.90 = **−1.33%**
> **At p = 0.54, b = 0.90:**
> f\* = (0.486 − 0.460)/0.90 = **+2.89%**

**At 52% accuracy with a realistic cost drag the Kelly stake is negative — the correct size is zero.** The app should display this, not hide it. A positive Kelly stake requires accuracy at the top of the achievable range *and* costs at the bottom.

### Step 1 — Set the Crane fraction from stated risk tolerance

α̅ = 2 / (1 + θ_min), where θ_min = log π / log(1 − E).

Take E = 50% (willing to lose half the trading capital before stopping) and π = 0.02 (2% chance of hitting that stop even if the edge is real):
> θ_min = log(0.02)/log(0.50) = (−3.912)/(−0.693) = 5.644
> α̅ = 2/(1 + 5.644) = **0.301 → 30% of Kelly**

### Step 2 — Apply the robust κ_min scaling

Crane's robust rule scales by κ_min, the worst-case ratio of true to estimated edge. With t = 0.45, the lower confidence bound on the edge is negative, so a rigorous κ_min is ≤ 0 and the rigorous answer is zero size. Adopting the most generous defensible assumption, κ_min = 0.25 (the true edge is at least a quarter of the estimate):
> α = 0.301 × 0.25 = **0.075 → 7.5% of Kelly**

Sanity check against Theorem 38(i): growth is positive only when κ > α/2 = 0.0376. So this stake survives the true edge being as little as 3.8% of the estimate. At 30% of Kelly unscaled, it would require κ > 0.15 — six times less tolerance for error.

### Step 3 — Combine

> **At p = 0.54, b = 0.90:** 0.075 × 2.89% = **0.217% of capital at risk per position**
> **At p = 0.52:** Kelly is negative → **0% — no position**

### Step 4 — Translate into orders

For a **long option**, maximum loss is the premium, so premium paid per position ≤ 0.217% of capital. On a $100,000 account that is **$217 of premium per position** — roughly one or two contracts on a mid-priced name.

For a **defined-risk spread**, the risk quantum is max loss, not premium: (width × multiplier − net credit) ≤ 0.217% of capital.

For **short premium**, Kelly must not be used at all (§1.3 — Kelly returns near-half-bankroll for negatively skewed bets). Use the empirical margin-based cap instead: Santa-Clara & Saretto found average margin haircuts of $3.9 to $43.1 per $1 of premium received, implying a maximum sustainable short-option position of roughly **3.6%–4.4% of wealth** at CBOE parameters, and that shorting OTM puts becomes nearly impossible to sustain for individuals under retail-broker parameters. **Cap short-premium notional risk at 4% of capital in aggregate**, derived from that evidence rather than from Kelly.

### Step 5 — The sanity cross-check that should override everything

Expected annual growth at this size: 24 positions/year × 0.217% × (edge per position). With a 2-percentage-point accuracy edge the expected annual return is a fraction of a percent. **If the sizing rule produces an expected return not worth having, the correct conclusion is that the strategy is not worth trading at size — not that the sizing rule should be loosened.** The app should display expected annual return alongside the position size, so that the temptation to raise size is met immediately with the κ and drawdown-recovery consequences.

### Recommended default configuration

| Parameter | Value | Source |
|---|---|---|
| Kelly fraction ceiling | 15% (hard), 7.5% default | Crane 2026 Thm 38(iv) |
| Stop-loss E | 50% of trading capital | user input |
| Premature-stop tolerance π | 2% | user input |
| κ_min assumption | 0.25 | derived from t = 0.45 |
| Per-position risk (long/spread) | 0.20% of capital | arithmetic above |
| Aggregate short-premium risk | 4% of capital | Santa-Clara & Saretto |
| Vol targeting | yes, for tail control only; no Sharpe claim | Harvey et al. 2018 |
| Regime scaling | cut only, never add | Cederburg et al. 2020 |

---

# RISK LIMIT SET

Limits the app should enforce (block the trade) or display (warn). Thresholds are for a $100,000 account and scale linearly.

**Enforce — block the order:**

| # | Limit | Threshold | Basis |
|---|---|---|---|
| 1 | Per-position risk | ≤ 0.20% of capital (long/spread); ≤ 1% for any single short-premium structure | §Sizing |
| 2 | Aggregate short-premium risk | ≤ 4% of capital | Santa-Clara & Saretto |
| 3 | Correlation-stressed loss | all equity correlations → 0.9, all underlyings −15% (low-vol regime) or −20% (high-vol): loss ≤ 8% of capital | §4, tastytrade stress |
| 4 | Portfolio-margin buffer | reject any trade leaving net liq within 25% of the PM minimum ($125,000 against a $100,000 floor) | IBKR surcharge mechanics §5.2 |
| 5 | Net vega limit | worst-case net vega × 10 ≤ 10% of capital | tastytrade house rule |
| 6 | Short options into expiry | no short leg held with <1 DTE within 1% of the underlying | §6 pin risk |
| 7 | Short call before ex-div | block if extrinsic value < upcoming dividend + K[1−e^(−r(T−t))] | §6 early exercise |
| 8 | Covered call on short-term lot | block if underlying lot has unrealised gain and holding period < 12 months | §7.7 |
| 9 | Total-capital stop | pre-committed E (default 50%); on breach, all new risk blocked pending review | Crane Lemma 5 |

**Display — always visible:**

| # | Metric | Why |
|---|---|---|
| 10 | Vega by expiry bucket (0–7, 8–30, 31–60, 61–120, 120+ days), never a single summed vega | §4 — vega is not additive |
| 11 | Beta-weighted delta **plus** raw per-underlying delta **plus** the beta estimation window | §4 — failure modes |
| 12 | Net gamma, and the dollar P&L impact of a 1% underlying move computed through gamma, not delta alone | §4 |
| 13 | Drawdown-recovery table at the user's own realised return | §2.2 — the decisive arithmetic |
| 14 | Current drawdown, and years-to-recover at realised growth | §2.2 |
| 15 | κ sensitivity on the sizing recommendation: size and growth sign at κ = 1.0, 0.75, 0.50, 0.25 | Crane Thm 38 |
| 16 | Implied likelihood ratio against the edge hypothesis given realised performance versus the π sized for | Crane Lemma 5 |
| 17 | Distance to the VIX regime thresholds (20 / 25 / 30) and the margin consequence of crossing | tastytrade stress rules |
| 18 | Rolling 12-month count of intraday margin deficits (3 is the regulatory inflection) | FINRA Rule 4210(d)(2) |
| 19 | Overnight margin and loss exposure in the one-leg-assigned scenario for every spread | §6 — the real risk of "defined risk" |
| 20 | Tax-adjusted unrealised P&L on 1256 positions (year-end MTM accrual) | §7.3 |
| 21 | Number of concurrently open positions and the effective number of independent bets after correlation | §4 |

**Hard structural rules, not thresholds:**
- Never size short premium with Kelly.
- Never validate a sizing or regime choice with an alpha regression — only real-time expanding-window CER (Cederburg et al.).
- Never display a single expected-maximum-drawdown number for a zero-drift strategy.
- Prefer cash-settled broad-based index options for the four independent reasons in §7.2.

---

# TAX FLAGS THE APP SHOULD MODEL

| Rule | What the app can compute | What needs a CPA |
|---|---|---|
| **§1256 60/40** | The 60/40 split; after-tax P&L given a user-supplied bracket; the SPX-vs-SPY comparison for any proposed trade | The user's actual marginal rate, NIIT applicability, state tax |
| **§1256 eligibility** | Apply the statutory test (broad-based index, cash-settled, qualified board) and classify SPX as 1256 and SPY/QQQ as equity options | **XSP, VIX, RUT, NDX must be flagged "likely 1256 — confirm," not asserted.** Also Rev. Rul. 26-16 |
| **§1256 year-end MTM** | Deemed-sale gain/loss on open 1256 positions at year end; tax-adjusted unrealised P&L | Interaction with the rest of the return |
| **Net 1256 loss carryback** | Detect a net 1256 loss year and flag the Form 6781 Box D election | **The entire election.** Multi-layered limits and prior-year interaction. App computes nothing |
| **§1092 straddles** | Detect offsetting positions, including via the margin-offset presumption; flag every spread, condor and butterfly as a probable straddle; compute unrealised gain in the offsetting leg and the resulting loss-deferral exposure before a year-end close | Whether the presumption is rebuttable in a given case; carrying-cost capitalisation under §263(g) |
| **Identified straddle election** | **Create the same-day contemporaneous record** (legs, quantities, date, timestamp) at trade entry. This is the highest-value tax feature and only the tool can do it | Whether to make the election, and the basis-allocation computation |
| **Mixed straddles** | Detect any hedge spanning the 1256 boundary (e.g. SPX option hedged with SPY) and flag it before execution | All three elections (Form 6781 Boxes A/B/C). Irrevocable without IRS consent — never auto-elect |
| **Wash sales** | Over-inclusive candidate detection across the user's full history and **across all accounts including IRAs** — something no 1099-B will do | **Whether a different strike or expiration is "substantially identical."** No bright-line rule exists |
| **Short vs long term** | Holding period per lot; confirm that essentially all equity-option activity is short-term | Edge cases (LEAPS held >1 year) |
| **Qualified covered calls** | The >30-day test, exchange-traded test, and the holding-period cost of breaking a long-term lot, in dollars | **The "deep in the money" boundary** (Treas. Reg. §1.1092(c)-2/-4). Not numerically defined in sources retrieved |
| **Assignment/exercise** | Premium folded into basis or proceeds; lot-level basis and holding-period tracking | Complex multi-leg assignment chains |

**Standing requirements for the app:** every tax output carries "informational only, not tax advice, confirm with a CPA"; nothing is filed or elected automatically; the app's job is **detection, quantification and contemporaneous record-keeping**, never election. The record-keeping role is the one with the clearest return on effort, because several of these elections are forfeited by the passage of a single day.

---

# DISCONFIRMING EVIDENCE

**1. The headline vol-conditioning result fails out of sample.** Cederburg, O'Doherty, Wang & Yan (*JFE* 2020) found real-time volatility-managed combinations delivered a *lower* certainty-equivalent return than the unmanaged portfolio in **72 of 103 strategies**; for the market, out-of-sample Sharpe was 0.42 managed vs 0.46 unmanaged. Their methodological point is sharper than their empirical one: because managed and unmanaged versions correlate 0.48–0.70, **a managed portfolio can show a positive spanning alpha while having a lower Sharpe ratio**, so the alpha measures the value of an ex-post optimal combination that was unknowable in real time. Any backtest the developer runs that validates a sizing rule by regression alpha is measuring nothing.

**2. Volatility targeting's Sharpe benefit is a momentum bet, not risk management.** Harvey et al. (*JPM* 2018) found one-month momentum explains 45–60% of the cross-asset variation in Sharpe improvement from vol scaling, and that the mechanism — the leverage effect — exists only in equities and credit. In other assets vol scaling is an inadvertent mean-reversion bet. The prior strand's observation that the time-series-momentum t-statistic fell from 4.34 to 1.68 without vol scaling is therefore **confirmed as a real concern**: vol scaling was carrying part of the signal. Harvey et al. also found vol scaling *lowered* the bond Sharpe ratio over 1963–2017 and failed to improve equities in the 1957–1987 subsample.

**3. Portfolio margin increases risk for a retail trader.** Cboe's own worked examples show a short strangle requiring $227,360 under strategy-based margin and **$75,999** under portfolio margin, and a short calendar requiring $300,460 versus **$7,500** — a 40× reduction. The economic position is identical; only the permitted leverage changed. Worse, the capital relief is procyclical in a documented way: IBKR applies a margin surcharge below $100,000 net liq that progressively moves the account *toward Reg T requirements* as equity falls. A portfolio-margin account taking losses faces rising requirements at the moment of falling equity — mechanically the Santa-Clara & Saretto result, written into the broker's rulebook. **For an account near the threshold, portfolio margin converts a drawdown into a forced liquidation.** A third effect: §1092(c)(3) makes a lower combined margin requirement a statutory *presumption* that positions are an offsetting straddle, so the capital efficiency itself triggers adverse tax treatment.

**4. The sizing rule's own arithmetic says not to trade.** This is the most important disconfirming finding and it disconfirms the project, not a technique. At 52% accuracy with a realistic cost drag the Kelly stake is **−1.33%** — negative. A positive stake requires accuracy at the top of the achievable range. The recommended rule yields ~0.2% of capital per position; at that size the expected annual return from a 2-percentage-point accuracy edge is a fraction of a percent, before tax. **A correctly specified sizing module is likely to tell the developer that the strategy is not worth trading at any size that matters.** The app should be built to deliver that message clearly rather than to be configurable around it.

**5. Crane's own framing undercuts the folklore the build would otherwise adopt.** The familiar "use half Kelly" is not a principle but one point on a curve determined by stop-loss and ruin tolerance. Half Kelly tolerates only a 4× edge overestimate before growth goes negative. Given t = 0.45, a 4× overestimate is well inside the confidence interval. **Half Kelly is not conservative here; it is reckless.**

**6. PDT elimination changes much less than the brief assumes.** The new intraday margin layer applies to stock positions; options in a Reg T margin account continue under existing rules. The residual effect is narrow — 0DTE options expiring ITM on deliverable equities and ETFs create stock positions with intraday margin consequences, while cash-settled index options do not. The brief's framing of this as a material change in options buying power does not hold up.

**7. Risk-of-ruin formulas fail where it matters.** Closed-form risk-of-ruin calculations assume i.i.d. bets. An options portfolio's defining risk is the correlated multi-position loss, which violates the assumption precisely in the state that causes ruin. Implementing a closed-form calculator would produce a number that is reassuring and wrong.

**8. A caution on my own strongest source.** Crane (2026) is a working paper on Researchers.One, not peer-reviewed, and its quantitative treatment of estimation error covers only κ ≤ 1 — it does not formally treat edge *underestimation*, so its asymmetry argument is motivational rather than proven. Its results are theorems and I am confident in the mathematics, but the developer should know this strand's central quantitative recommendation rests on one unrefereed paper, corroborated in direction (not magnitude) by Baker & McHale (*Decision Analysis* 2013).

**9. Several claims here are weaker than their prominence suggests.** I could not verify Magdon-Ismail & Atiya's MDD formula (abstract only), could not retrieve Simon & Campasano's magnitudes (robots-disallowed), found no primary confirmation of 1256 status for XSP, VIX, RUT or NDX, found no numeric definition of "deep in the money," found no peer-reviewed treatment of beta-weighted delta or term-adjusted vega, and found **no credible evidence at all** that conditioning position size on realised correlation or credit spreads improves outcomes.

---

# WHAT A PROFESSIONAL RISK MANAGER WOULD REQUIRE

Concretely, before allowing a near-zero-measured-edge strategy to trade real capital:

1. **A statistically adequate track record, or an explicit admission that none exists.** Bailey & López de Prado's Minimum Track Record Length formalises how long a record must be before a Sharpe ratio is distinguishable from a benchmark at a stated confidence, and negative skewness *lengthens* the requirement. A t-statistic of 0.45 is far below any approval threshold; the implied MinTRL for significance is decades. **A risk manager would not approve this strategy. He would approve a paper-trading allocation.** (Sources: Bailey & López de Prado, "The Sharpe Ratio Efficient Frontier," *Journal of Risk*, 2012/13, https://www.risk.net/journal-risk/2223785/sharpe-ratio-efficient-frontier; implementation in R PerformanceAnalytics `MinTrackRecord`, https://search.r-project.org/CRAN/refmans/PerformanceAnalytics/html/MinTrackRecord.html — **peer-reviewed**.)

2. **A correlation-based approval test, not a standalone-performance test.** Bailey, López de Prado & del Pozo's Sharpe-ratio indifference curve shows a strategy's value depends jointly on its Sharpe ratio and its correlation to what is already held — and that a strategy with *negative* expected performance can improve a portfolio if its correlation is sufficiently negative (their worked threshold: average correlation −0.439). The correct question is not "does this strategy make money?" but "what does it add to the existing book?" (Source: https://www.davidhbailey.com/dhbpapers/sharpe-ratio.pdf, *Algorithmic Finance* — **peer-reviewed**.)

3. **A scaled allocation with pre-committed escalation gates.** Start at a fraction of the computed size; raise only on out-of-sample evidence, never on in-sample alpha.

4. **A hard capital stop, pre-committed in writing, and an acknowledgement that it will be hit if the edge is zero** (Crane Lemma 5).

5. **Stress limits binding independently of the P&L limit** — the correlation-stressed loss test in §4 — because a zero-edge strategy's realised outcome is determined by its worst correlated day.

6. **Out-of-sample validation methodology fixed before the first trade**, specifically excluding alpha regressions (Cederburg et al.).

7. **A declared and monitored capacity/cost assumption**, since Santa-Clara & Saretto found transaction costs of roughly 4% per month for the strategies they examined — enough to erase any edge of this magnitude many times over.

8. **Separation of the sizing decision from the signal decision**, so that vol scaling cannot smuggle in a momentum bet unaccounted for (Harvey et al.).

9. **A kill criterion expressed in evidence, not P&L** — Crane's likelihood-ratio framing, where hitting the stop carries at least 1/π evidence against the edge hypothesis.

10. **Explicit margin-regime risk sign-off**, given that enforcing margin turned the Santa-Clara & Saretto Sharpe ratios from +0.551 to −0.306 and from +0.352 to −0.239, and that the broker's own surcharge mechanics replicate the mechanism.

---

# OPEN QUESTIONS

1. **Is XSP/VIX/RUT/NDX definitively Section 1256?** Only SPX confirmed from a primary source. Check the EY qualified-board-or-exchange list and IRS Rev. Rul. 26-16 (https://www.irs.gov/pub/irs-drop/rr-26-16.pdf). **Highest-priority open item** — the whole after-tax case rests on it.
2. **What is the numeric "deep in the money" test for a qualified covered call?** Requires Treas. Reg. §1.1092(c)-2 and §1.1092(c)-4.
3. **Reg T margin treatment of verticals, calendars and diagonals.** Requires the Cboe Margin Manual; the strategy-based summary page omits them.
4. **Exact term-adjusted vega formula** used in production risk systems.
5. **Is the Magdon-Ismail & Atiya MDD expression usable for a near-zero-drift process,** or does it degenerate? Requires the *Risk* 2004 article.
6. **For an account under $100,000, do SPAN-margined futures options (/ES) dominate SPX options** on combined margin-plus-tax grounds? Both are 1256; SPAN is more efficient than Reg T. Unresolved and potentially significant.
7. **Does the user's specific broker apply the new intraday margin framework now or under the October 2027 phase-in?** Determines current behaviour.
8. **Does Euan Sinclair's negative-skew Kelly adjustment have a closed form,** and does it agree with Crane's κ scaling?
9. **Empirical basis for the pin-risk band.** The 1% figure is an assertion; it should be estimated from the user's own underlyings.
10. **Does any evidence support conditioning size on realised correlation or credit spreads?** None found. Possibly a genuine gap in the literature rather than a gap in my search.
11. **What is the strategy's actual MinTRL** given its skewness and kurtosis? Computable from the formula once realised moments exist, and would quantify how long before the edge could even in principle be validated.

---

# TOP 10 SOURCES, RANKED

1. **Harry Crane, "The Kelly Criterion with an Estimated Edge," Researchers.One, Sept 2026.** https://researchers.one/articles/26.09.00001.pdf — *Working paper, not peer-reviewed.* The single most important source. Theorem 38(i) (growth positive only if κ > α/2) and the robust κ_min scaling give the entire sizing recommendation its quantitative backbone. Caveat: unrefereed; covers only κ ≤ 1.

2. **Cederburg, O'Doherty, Wang & Yan, "On the performance of volatility-managed portfolios," *JFE* 138: 95–117, 2020.** https://www.lehigh.edu/~xuy219/research/COWY.pdf — *Peer-reviewed.* Kills the in-sample vol-conditioning result out of sample (72 of 103 strategies worse on CER) and supplies the methodological rule that no sizing choice may be validated by alpha regression.

3. **Santa-Clara & Saretto, "Option Strategies: Good Deals and Margin Calls," *Journal of Financial Markets* 12(3): 391–417, 2009.** https://escholarship.org/content/qt0499w44p/qt0499w44p_noSplash_a53c67820225e4ebff79454eb60c5447.pdf — *Peer-reviewed.* Confirms and enriches the brief: 10% OTM strangle Sharpe 0.551 → −0.306, 10% OTM put 0.352 → −0.239; margin haircuts of $3.9–$43.1 per $1 of premium capping positions at ~3.6–4.4% of wealth; transaction costs ~4%/month.

4. **Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert, "The Impact of Volatility Targeting," *JPM*, 2018.** https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf — *Peer-reviewed.* Equity Sharpe 0.40 → 0.48–0.51; momentum explains 45–60% of the improvement; robust tail-risk reduction across 60+ assets. Separates the defensible claim from the artefact.

5. **FINRA, Interpretations of Rule 4210 (valid from 4 June 2026) + Regulatory Notice 26-11 + intraday margin investor guidance.** https://www.finra.org/rules-guidance/guidance/interps-4210-202606 · https://www.finra.org/sites/default/files/2026-05/Regulatory-Notice-26-11.pdf · https://www.finra.org/investors/insights/intraday-margin-requirements — *Primary (regulator), current.* Portfolio-margin minimums ($100k/$150–500k/$500k/$5m by monitoring capability); $2,000 margin minimum; continuous 25% maintenance; PDT elimination; the 3-deficits-in-12-months inflection.

6. **IRC §1256 and §1092.** https://www.customsmobile.com/uscode/26/1256 · https://www.govinfo.gov/content/pkg/USCODE-2011-title26/pdf/USCODE-2011-title26-subtitleA-chap1-subchapO-partVII-sec1092.pdf — *Primary (statute).* The 60/40 rule, year-end MTM, the narrow-based-index mechanism that makes broad index options 1256, the straddle definition and offsetting-position presumptions, identified straddles, the qualified-covered-call exception.

7. **Cboe margin materials: "Overview of Margin Requirements for Options" and "Margin Requirement Examples."** https://www.cboe.com/us/options/strategy_based_margin · https://cdn.cboe.com/resources/membership/Margin_Requirement_Examples.pdf — *Primary (exchange).* Exact Reg T formulas (20% equity / 15% broad index) and the worked Reg-T-vs-PM comparisons that supply the strongest disconfirming evidence on portfolio margin (short calendar $300,460 → $7,500).

8. **Interactive Brokers Portfolio Margin + tastytrade Portfolio Margin House Rules.** https://www.interactivebrokers.com/en/trading/marginRequirements/marginPortfolio.php · https://tastyworks.freshdesk.com/support/solutions/articles/43000595351 — *Primary (brokers).* $110k open / $100k maintain; ±15% equity, +6%/−8% broad index, IV ±75%/±150%, $0.375 × index floor, procyclical surcharge below $100k; VIX-regime-conditioned stress, ±20% single names, −50%/+100% small-cap biotech, +50% pre-earnings, vega × 10, 15× cash rejection. *tastytrade page undated — re-verify.*

9. **Baker & McHale, "Optimal Betting Under Parameter Uncertainty: Improving the Kelly Criterion," *Decision Analysis* 10(3): 189–199, 2013.** https://salford-repository.worktribe.com/output/1410355/ — *Peer-reviewed.* Independent confirmation that Kelly stakes must be shrunk under parameter uncertainty, with simulation and empirical support. Magnitudes not retrieved.

10. **OIC/OCC Options Exercise FAQ + Bailey, López de Prado & del Pozo, "The Strategy Approval Decision."** https://www.optionseducation.org/referencelibrary/faq/options-exercise · https://www.davidhbailey.com/dhbpapers/sharpe-ratio.pdf — *Primary (OCC-affiliated) and peer-reviewed.* The $0.01 exercise-by-exception threshold, the 4:30 p.m. CT cut-off, and the critical warning that a long leg is only exercised against an assigned short leg with explicit instructions; plus the Sharpe-indifference-curve framework for how a professional would actually approve or reject this strategy.

**Honourable mentions:** Moreira & Muir (NBER WP 22208 / *JF* 2017) for the in-sample result that source 2 overturns; GreenTraderTax 2026 for specialist practitioner tax synthesis; IRS Form 6781 instructions for the carryback and mixed-straddle election mechanics; Moontower "Kelly Math Weirdness" for the skew asymmetry arithmetic (1% vs ~50% of bankroll at equal EV).
