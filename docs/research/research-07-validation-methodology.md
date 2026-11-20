# Research 07 — Validation, Backtesting and Calibration Methodology
### For a single-developer options contract explorer / ranker (CMU Agentic AI capstone)
Compiled 2026-11-10. All findings paraphrased. Wave-2 strand: *how does one person honestly test whether any of this works?*

---

## 0. The arithmetic that governs everything else

Before the findings, three numbers the developer should internalise, because every protocol decision below follows from them. I derived these from the published formulas (sources in §2) rather than taking them from a secondary source, so they are reproducible.

**(a) How much Sharpe you need to detect anything.** The t-statistic on an annualised Sharpe ratio grows roughly as `SR × √years`. So:

| True annual Sharpe | Years to reach t ≈ 2 | Years to reach Harvey's t ≈ 3 |
|---|---|---|
| 1.5 | 1.8 | 4.0 |
| 1.0 | 4.0 | 9.0 |
| 0.6 | 11.1 | 25.0 |
| 0.4 | 25.0 | 56.3 |

**(b) How many hypotheses you can afford.** Expected maximum in-sample Sharpe under *zero* skill ≈ `√(2 ln N) / √T` per period, where N is the number of configurations tried and T the number of return observations. With T = 60 months:

| Trials N | Zero-skill expected max Sharpe (annualised) |
|---|---|
| 2 | 0.52 |
| 5 | 0.79 |
| 12 | 1.00 |
| 45 | 1.23 |
| 200 | 1.46 |
| 1,000 | 1.65 |

Inverting: on 5 years of monthly data, **keeping the zero-skill bar below annualised Sharpe 0.5 permits fewer than two trials**; below 1.0 permits about twelve. This independently reproduces the Wave-1 figure (~45 trials → in-sample Sharpe ≈ 1 with no skill), which is reassuring about that figure's provenance.

**(c) Minimum backtest length.** Bailey & López de Prado's bound is approximately `MinBTL ≈ 2·ln(N) / SR²` years. For N = 100 trials and a target Sharpe of 1.0 that is ~9.2 years; for a Sharpe of 0.5 it is ~37 years.

**The inescapable conclusion, stated up front:** a solo developer with 5–10 years of monthly-horizon options data cannot statistically certify a moderate edge. Every protocol in §9 is therefore designed to produce *falsification and honest bounds*, not certification. This is not pessimism; it is what the published power arithmetic says, and the most rigorous recent empirical study of exactly this problem (§2, Hert 2026) reached the same conclusion with 0 of 5 strategies surviving despite all 5 being profitable out of sample.

---

## 1. Options backtesting construction

### CLAIM: Option prices must come from stored point-in-time chain snapshots; reconstructing them from a pricing model destroys the very implied-volatility information the strategy trades on.
**SOURCE:** OptionVisualizer, "Options Backtesting: Methods, Pitfalls & Assumptions" (practitioner documentation, 2026) — https://www.optionvisualizer.com/documentation/education/backtesting
**EVIDENCE STRENGTH:** Moderate (practitioner consensus, not a controlled study; corroborated independently by ORATS and EverFunded below)
**IMPLICATION:** The explorer must persist a nightly snapshot of the full chain (all strikes, all expiries, bid, ask, IV, Greeks, OI, volume) from day one, keyed by snapshot timestamp. A chain pulled today is not a substitute for the chain that existed on any earlier date — vendors reconstruct, re-stamp and backfill. **This is the single highest-value engineering action available and it is free: start logging now.** Every month of delay is a permanently lost month of validation sample.

### CLAIM: The contract-selection decision must use only data whose timestamp precedes the simulated trade; end-of-day Greeks cannot legitimately select a contract for an earlier-in-the-day trade.
**SOURCE:** EverFunded, "Option Backtesting: Chains, Fills, Assignment and Bias" (2026) — https://everfunded.com/blog/options-backtesting
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** If selection is "nearest 30-delta," the delta must be the one published at or before the decision timestamp, and the code must record which delta it used. Store the *decision-time* underlying price alongside the selection. Also align option and underlying timestamps, time zones and session calendars — half-day sessions produce fields labelled with a close time that actually reflect an earlier observation.

### CLAIM: Midpoint fills systematically overstate options P&L; the vendor-calibrated defensible assumption is to pay a large fraction of the quoted spread, decreasing with leg count.
**SOURCE:** ORATS, "Help, My Backtest Isn't Working!" (options data vendor, 2026) — https://orats.com/blog/help-my-backtest-isnt-working
**EVIDENCE STRENGTH:** Moderate for the direction; Weak for the exact numbers (vendor's own trading experience, explicitly not presented as a standard, and the vendor sells a backtester)
**IMPLICATION:** ORATS assumes slippage of **75% of the bid-ask width for a single leg, 66% for two legs, 56% for three, 53% for four**. For a single-leg contract explorer, 75% of quoted spread is the number to use as the base case. Note this is *more* punitive than the 25–50% fractions at which Wave 1's cited edges died — meaning a vendor who trades these instruments assumes worse execution than the fraction at which the academic edge already vanishes. That is a serious finding: **the academic sensitivity analyses may not go far enough.** Run the ladder at 25 / 50 / 75 / 100% and report all four; treat 75% as the headline.

### CLAIM: Academic delta-hedged option-return results are constructed on bid-ask *midpoints* with zero spread in the baseline, with fractional-spread sensitivity only as a robustness section.
**SOURCE:** Cao, Han, Zhan et al., "Option Return Predictability" (conference draft, 2016) — https://www.cicfconf.org/sites/default/files/paper_452.pdf
**EVIDENCE STRENGTH:** Strong (explicit in the paper's methodology)
**IMPLICATION:** Any headline number quoted from this literature is a *midpoint* number. The paper itself reports average quoted bid-ask of about **20% of premium (median ~15.6%)** for the at-the-money equity options it studies. One of their long-short spreads falls from 1.46% to 0.62% per month going from midpoint to 100% of quoted spread — a 58% haircut. The paper also contains an internal inconsistency (the introduction says buy-at-ask/sell-at-bid, Section 4 applies fractional effective spreads), which is worth noting as a reason not to over-trust any single reported cost-adjusted figure.

### CLAIM: Replicating the academic delta-hedged return requires a specific, daily-rebalanced discrete gain with an explicit financing term, and a documented scaling denominator.
**SOURCE:** Cao et al. (2016), Eq. 2–3, following Bakshi & Kapadia — https://www.cicfconf.org/sites/default/files/paper_452.pdf
**EVIDENCE STRENGTH:** Strong
**IMPLICATION:** The construction is: `Π = C(t+τ) − C(t) − Σₙ Δₙ[S(tₙ₊₁) − S(tₙ)] − Σₙ (αₙ·r/365)[C(tₙ) − Δₙ·S(tₙ)]`, rebalanced daily, where αₙ is calendar days between rebalances. Calls are scaled by `|Δ·S − C|`, puts by `|P − Δ·S|`. Three variants exist in the literature (one-month hold with no rebalance; hold to maturity ~50 days; daily rebalance compounded) and they are **not interchangeable** — choosing among them after seeing results is itself a trial that must be logged. Practical warning: this needs a daily underlying series *and* a daily option mark *and* a risk-free series, and daily re-hedging means daily equity transaction costs that the academic baseline charges at zero.

### CLAIM: The standard academic filter stack is restrictive enough that it changes what "the universe" means, and it excludes dividend-paying names entirely to justify European treatment.
**SOURCE:** Cao et al. (2016), sample construction — https://www.cicfconf.org/sites/default/files/paper_452.pdf
**EVIDENCE STRENGTH:** Strong
**IMPLICATION:** Their filters: CRSP share codes 10/11; prior-month close ≥ $5; one call and one put nearest ATM with shortest maturity > 1 month (final maturities 47–52 days); **exclude any option whose underlying pays a dividend during the option's remaining life**; positive volume; positive bid; bid < ask; midpoint ≥ $0.125; drop no-arbitrage violations (`S ≥ C ≥ max(0, S − Ke^(−rT))`); moneyness S/K in [0.8, 1.2]; drop off-cycle maturities; require both a call and a put to survive. Result: 159,902 option-months over 1996–2012. **No open-interest filter.** Two consequences for the build: (i) if the explorer's liquidity disqualifiers differ from this stack, the academic evidence does not transfer unmodified; (ii) the dividend exclusion is how the literature *avoids* the early-exercise problem rather than solving it — a build that includes dividend payers takes on an unmodelled risk the source papers deliberately excluded.

### CLAIM: Short American options can be assigned early regardless of other legs held, so a backtest must model assignment rather than assume an offsetting leg protects it.
**SOURCE:** EverFunded (2026), citing FINRA — https://everfunded.com/blog/options-backtesting ; corroborated by OptionVisualizer, "Corporate Actions & Options" — https://www.optionvisualizer.com/documentation/education/corporate-actions
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** Concrete rules to implement: do not delete a contract from the ledger because its date passed — exercise/assignment/settlement create cash flows and share positions. Model early exercise of deep-ITM short calls near ex-dividend dates (no source gives a threshold; the developer must pick and document one, e.g. assign when remaining extrinsic < dividend). Simulator defaults (the article names QuantConnect's) are assumptions to audit, not ground truth.

### CLAIM: Corporate actions change the deliverable, not just the strike, and adjusted contracts should be treated as separate illiquid instruments.
**SOURCE:** OptionVisualizer, "Corporate Actions & Options" (2026) — https://www.optionvisualizer.com/documentation/education/corporate-actions ; QuantMemo, "OCC Option Contract Adjustments, Explained" — https://quantmemo.com/concepts/occ-option-contract-adjustments
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** Rule set: whole-number forward split → multiply contract count, divide strike, multiplier stays 100. Fractional split (3:2) → count stays, strike divided, **deliverable becomes 150 shares**. Reverse split → strike multiplied, deliverable reduced, new symbol. Special dividend → strike reduced by the dividend, flagged non-standard; regular dividends get no adjustment. Cash merger → settle at deal price × multiplier. Stock-for-stock → deliverable becomes exchange-ratio × 100 acquirer shares. Spinoff → add spun shares to the deliverable. Target IV collapses between announcement and close, so do not carry pre-deal vol forward. **For this build the pragmatic answer is a hard disqualifier: exclude any name with an announced-but-uneffected split, special dividend or merger, and exclude non-standard deliverables outright.** That sidesteps most of this complexity and is honest if disclosed.

### CLAIM: Survivorship contamination in options backtests comes through the underlying — excluding delisted, bankrupt and acquired names inflates results.
**SOURCE:** OptionVisualizer backtesting documentation (2026); AnalystPrep CFA L2 study notes on backtesting biases — https://analystprep.com/study-notes/cfa-level-2/problems-in-backtesting/
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** The explorer's ticker universe must be a *point-in-time* membership list, not today's list. The most rigorous recent study on this (Hert 2026, §2) explicitly flags that using a current constituent list flatters active strategies — and notes this biased *against* their null result, making their failure conclusion conservative. A solo developer will probably use a current list; they must say so and note the direction of the bias.

### CLAIM: Multi-leg and fee accounting errors are large relative to per-trade edge, and must be charged per leg.
**SOURCE:** EverFunded (2026) — https://everfunded.com/blog/options-backtesting ; OptionVisualizer backtesting documentation
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** Worked example from EverFunded: four leg executions at $0.65 = $2.60, turning a nominal $50 gain into $47.40. OptionVisualizer puts commissions at $0.50–1.30 per contract per leg and total round-trip drag at $5–25 per trade. Engineering rules: specify whether a spread is priced as a combo or leg-by-leg; define behaviour on partial fills (one leg filled creates interim naked exposure); keep premium cash flows separate from mark-to-market changes; disclose the mark convention (midpoint vs liquidation). For a single-leg explorer this is simpler, but the mark convention still matters for reporting unrealised P&L.

### CLAIM: Limit-order fills carry a systematic adverse mid-price drift of roughly half a tick, approximately cancelling the spread capture that passive-fill backtests credit.
**SOURCE:** "The Negative Drift of a Limit Order Fill," arXiv 2407.16527 (2024) — https://arxiv.org/html/2407.16527v1
**EVIDENCE STRENGTH:** Moderate (clean mechanism, live data, but one instrument and one trading day; theory is a simple 3-state model)
**IMPLICATION:** Measured on 10-year Treasury futures: average post-fill mid drift ≈ −0.0065 for buy fills against a half-tick of 0.0078, i.e. essentially the whole half-spread. About **1/3 of 1,683 simulated resting orders never filled at all** because price moved away. The author reports a naive strategy's simulated profit going negative once realistic fill assumptions were used. For this build: (i) any "work the mid" or "limit at mid" assumption is close to self-deception; (ii) a backtest must model *non-fill*, not just fill price — a signal whose good trades are the ones that don't fill is worthless. This is the mechanism underneath the paper-trading optimism finding in §7.

### CLAIM: Sample-size bands for options backtest reliability are far above what a monthly signal produces in a few years.
**SOURCE:** OptionVisualizer backtesting documentation (2026) — https://www.optionvisualizer.com/documentation/education/backtesting
**EVIDENCE STRENGTH:** Weak (practitioner rules of thumb, no derivation)
**IMPLICATION:** Their bands: <30 trades unreliable; 30–100 directional only; 100–500 reasonably reliable; 500+ a strong foundation. They also require at least one significant market dislocation in sample and separate bull/bear/sideways reporting. **A monthly-rebalanced single-name signal over 5 years produces 60 rebalances.** Even picking a top-5 each month, those 300 "trades" are cross-sectionally correlated within month, so the independent count is nearer 60. By this vendor's own bands, the project sits in "directional only" at best. That is a usable honest framing.

---

## 2. Walk-forward and out-of-sample protocol

### CLAIM: Walk-forward backtesting tests only one historical path and its result depends on the data sequence; combinatorial purged CV replaces the point estimate with a distribution of Sharpe ratios.
**SOURCE:** Marcos López de Prado, "The 10 Reasons Most Machine Learning Funds Fail" (2018), reasons 8–10 — https://www.smallake.kr/wp-content/uploads/2018/07/SSRN-id3104816.pdf
**EVIDENCE STRENGTH:** Strong (the canonical statement; reason 9 is explicitly the walk-forward critique)
**IMPLICATION:** Three directly implementable items from this paper. (1) **Purging**: remove training observations whose label window overlaps any test label. (2) **Embargo**: additionally remove training observations immediately after the test period. (3) **CPCV**: partition into groups, test on combinations, reconstruct many backtest paths. For a monthly signal with a 1-month label, purging removes ~1 month either side of each test fold — cheap and non-negotiable. CPCV on 60 observations with, say, 6 groups and 2 test groups per split gives 15 splits and 5 reconstructed paths — enough to see dispersion, not enough to be a reliable distribution. Also from this paper, three items that directly bear on an LLM-assisted build: **about 20 iterations on the same data suffice to find a spuriously significant strategy at the 5% level**; overlapping labels make samples non-IID and require uniqueness weighting; and his blunt framing is that feature importance is the research tool and backtesting is not.

### CLAIM: Purging must follow each observation's actual label horizon, and embargo is specified as a fraction of the data rather than a fixed integer gap.
**SOURCE:** E. Lazarev, `purged-cross-validation` (open-source, scikit-learn-compatible; purging, embargo, CPCV, deflated Sharpe) — https://github.com/eslazarev/purged-cross-validation and paper at https://github.com/eslazarev/purged-cross-validation/blob/main/paper/paper.md ; background: Wikipedia, "Purged cross-validation" — https://en.wikipedia.org/wiki/Purged_cross-validation
**EVIDENCE STRENGTH:** Moderate (working implementation with property-based tests asserting the no-overlap invariant and an overlap-fraction diagnostic; the package does not state default embargo fractions or CPCV sizing guidance)
**IMPLICATION:** This is the tool to use rather than hand-rolling; it exposes `purge`, `apply_embargo`, `assert_embargo_respected`, `PurgedKFold`, `CombinatorialPurgedCV` with `reconstruct_paths`, `probabilistic_sharpe_ratio`, `deflated_sharpe_ratio`, `min_track_record_length`, and a `compute_overlap_fraction` diagnostic. Their own model-selection notebook used a DSR ≥ 0.95 threshold and **no model cleared it** — a useful calibration of expectations. Effort: ~half a day to wire in.

### CLAIM: The Deflated Sharpe Ratio raises the significance bar as a function of the number of trials and the dispersion of trial Sharpes, and is the published remedy for selection bias.
**SOURCE:** Bailey & López de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality," *Journal of Portfolio Management* / SSRN 2460551 (2014) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
**EVIDENCE STRENGTH:** Strong
**IMPLICATION:** DSR requires an honest N. It cannot be computed retrospectively from memory, which is precisely why §3's trial ledger is a hard prerequisite rather than good hygiene.

### CLAIM: The Probabilistic Sharpe Ratio and Minimum Track Record Length give an exact, computable answer to "how long must this run before it means anything," and non-normality lengthens it materially.
**SOURCE:** Bailey & López de Prado, "The Sharpe Ratio Efficient Frontier," *Journal of Risk* (2012) — https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf
**EVIDENCE STRENGTH:** Strong (closed-form, with worked numeric examples)
**IMPLICATION:** `PSR(SR*) = Z[ (SR̂ − SR*)·√(n−1) / √(1 − γ₃·SR̂ + ((γ₄−1)/4)·SR̂²) ]` and `MinTRL = 1 + (1 − γ₃·SR̂ + ((γ₄−1)/4)·SR̂²)·(z_α/(SR̂ − SR*))²`, with SR per observation. Their worked monthly non-normal case (annual SR̂ = 2 vs benchmark 1, skew −0.72, kurtosis 5.78) needs **59.9 months ≈ 5.0 years — 54% longer than the 3.24 years the same case needs under normality.** Options returns are strongly negatively skewed and fat-tailed, so the non-normality penalty is the relevant one, not the textbook one. Their two-year example with skew −2.45 and kurtosis 10.16 looks significant under normality and is not once higher moments are included. **Engineering action: never report a Sharpe for this system without its PSR and MinTRL alongside, computed with the realised skew and kurtosis.**

### CLAIM: Under a complete trial ledger and a structural no-look-ahead guardrail, every LLM-discovered trading strategy failed certification while passive premia passed — and out-of-sample profit by itself was shown to be no evidence of skill.
**SOURCE:** "What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery," arXiv 2608.27734 (2026) — https://arxiv.org/pdf/2608.27734
**EVIDENCE STRENGTH:** Strong — and this is the single most directly applicable source in this report, because it is an agentic LLM strategy-discovery system evaluated honestly, i.e. almost exactly this capstone
**IMPLICATION:** Their protocol, which this project should largely copy: (1) a constrained action surface where look-ahead features are *not expressible* by the agent, with registry-validated tools and structured errors for self-correction; (2) a deterministic audit layer enforcing publication delays on event data that *rejects* plans rather than repairing them; (3) signals from bars through day *t*, positions held from *t+1*; (4) costs including commissions, spreads, square-root impact and borrow; (5) point-in-time universe re-selected periodically; (6) a design window and a held-out window never visible to the search; (7) a **trial ledger** logging every distinct strategy evaluation, feeding N and Sharpe dispersion into DSR; (8) PBO via combinatorially symmetric CV over 16 blocks; (9) stationary-bootstrap CIs on evaluation-window Sharpe, with "certified" meaning the CI excludes zero; (10) an **evaporation curve** plotting best in-sample Sharpe against the rising deflation threshold for each prefix of the ledger.

Their numbers are the ones to quote in the capstone. A deliberately leaky strategy scored design Sharpe 34.7 and **DSR 1.00** — *statistical deflation does not catch leakage*, which is why the structural guardrail is necessary and not merely nice. Main LLM search (N=102): best design Sharpe 1.69, threshold 1.21, DSR 0.86 (below the 0.95 bar), evaluation Sharpe collapsing to 0.18 with CI [−0.80, +1.14] while buy-and-hold returned +40.8%. Five repeated runs were **all profitable out of sample and 0 of 5 survived deflation** (DSR 0.15–0.29). A random-weights null earned +23% out of sample with DSR 0.0008. Cross-model check with a Claude model: 80/100 proposals valid, best design Sharpe 0.44 → −0.33 out of sample. The author's own human production system scored design Sharpe 0.33 and evaluation −0.12. Their power note matches §0: a true Sharpe of 0.6 needs ~11 years for t ≈ 2, so four-year windows cannot certify moderate edges; and a 10⁴-candidate search faces a bar ~1.5× higher than a 100-candidate search.

### CLAIM: Look-ahead freedom can be formalised as a verifiable non-interference property and tested behaviourally rather than left to reviewer diligence.
**SOURCE:** "Look-Ahead-Freedom as Temporal Non-Interference," arXiv 2607.04958 (2026) — https://arxiv.org/pdf/2607.04958 ; "When Alpha Disappears: A One-Switch Benchmark for Decision-Time Leakage in Financial Backtests," arXiv 2605.23959 (2026) — https://arxiv.org/pdf/2605.23959 ; "HindsightBench: A Black-Box Behavioral Audit Protocol for Parametric Hindsight in Time-Indexed LLM Decision Tasks," arXiv 2607.18867 (2026) — https://arxiv.org/pdf/2607.18867
**EVIDENCE STRENGTH:** Moderate (recent, not yet widely replicated; I read titles/abstracts and the framing, not full texts)
**IMPLICATION:** Two concrete, cheap tests fall out of this literature and belong in the capstone's eval module. (1) **One-switch leakage test**: run the whole pipeline with a single switch that shifts decision time by one bar; if performance collapses, the original run was reading the future. (2) **Parametric hindsight audit**: the LLM components in this system have a training cutoff, so an LLM asked about a 2022 filing may "know" what happened next. HindsightBench's framing — black-box behavioural audit for hindsight in time-indexed LLM tasks — is the right shape. A practical version: present the agent with two dated contexts differing only in a post-cutoff outcome and check whether its judgment is invariant to information it should not have.

**Note on parametric hindsight: this is a leakage channel that does not exist in classical quant backtesting and that this project has by construction.** If the LLM summarises an EDGAR filing from 2019 and the model was trained on data through 2026, the summary can be contaminated by knowledge of the subsequent stock move. No amount of purged CV detects this. The only real mitigations are (i) restricting the LLM's context to the retrieved document and measuring faithfulness to it (§8), (ii) running the hindsight audit above, and (iii) honestly disclosing it as an unquantified bias. **This should be a named limitation in the capstone write-up.**

### Sample-size reality for a monthly-horizon signal
Concretely, for this project: a liquidity-qualified optionable universe is perhaps 200–500 names. A monthly rebalance over 5 years of stored chain snapshots gives **60 independent time-series observations**. Cross-sectionally there are thousands of name-months, which helps estimate a *cross-sectional* information coefficient, but the thing that determines whether the strategy makes money — the time series of portfolio returns — has N = 60. From §0, that supports roughly **12 logged trials before the zero-skill bar reaches Sharpe 1.0, and roughly 2 before it reaches 0.5.** Any realistic development process will blow through 12 trials in an afternoon. The honest response is not to pretend otherwise but to (a) pre-register a very small number of confirmatory tests, (b) log everything else as exploratory, (c) report the evaporation curve.

---

## 3. Multiple-testing discipline for one person

### CLAIM: A t-statistic of about 3.0 is the appropriate hurdle for a new factor; 2.0 is too low, and modelling unobserved tests pushes the hurdle to about 3.2–3.9.
**SOURCE:** Harvey, Liu & Zhu, "…and the Cross-Section of Expected Returns," *Review of Financial Studies* 29(1), 2016; NBER WP 20592 — https://www.nber.org/system/files/working_papers/w20592/w20592.pdf
**EVIDENCE STRENGTH:** Strong
**IMPLICATION:** Specific usable numbers: headline hurdle t ≈ 3.0 (p ≈ 0.27%); BHY at 5% FDR with a time-varying benchmark gives ≈ 2.8; modelling unpublished tests gives a minimum of **3.18**; the structural model with correlation gives FWER-5% ≈ 3.9 and FDR-1% ≈ 3.0. Bonferroni at 5% rose from 1.96 to 3.78 by 2012 and is projected near 4.00 by 2032; BHY at 1% stabilised near 3.39 after 2010. They estimate **1,300+ factors have been tried and about 71% of tried factors never appear in the published record.** They recommend BHY with the c(M) correction so it holds under arbitrary dependence, and believe average correlation among factor returns is near 0.20.

Combining with §0: **a t-hurdle of 3.0 on 5 years of monthly data requires an annualised Sharpe of about 1.34.** If the system's net Sharpe is below that, it cannot clear the published-factor bar on the available sample, full stop. That is the cleanest single statement of the project's statistical position.

### CLAIM: When the number of tests is unknown, the published set is a floor, not an estimate — and the only defensible move is to model or simulate the hidden tests.
**SOURCE:** Harvey, Liu & Zhu (2016), Appendix A and §5 — https://www.nber.org/system/files/working_papers/w20592/w20592.pdf
**EVIDENCE STRENGTH:** Strong for the framing; the authors themselves note ρ is weakly identified
**IMPLICATION:** The honest solo-developer analogue: the trial count cannot be reconstructed afterwards, so it must be recorded prospectively. If it was not recorded, the correct statement is "N is unknown and the reported Sharpe is therefore an upper bound on the true one," not a p-value.

### CLAIM: Solo-developer pre-registration with a sealed test set and a published trial ledger is being practised in public, and the honest outcome is usually zero promotions.
**SOURCE:** Public repositories implementing exactly this pattern: https://github.com/pedramebd/systematic-trading-research (point-in-time data, deterministic risk veto, deflated Sharpe, permutation tests; 4 trials, 4 honest FAILs); https://github.com/stanleys12/trading-bot (pre-registered experiments, sealed test set, 212 trials, 0 promoted); https://github.com/AllanHert/quant-research (pre-registered quant research with blind agent review). Related: "Preregistration for Experiments with AI Agents," arXiv 2606.11217 (2026) — https://arxiv.org/pdf/2606.11217
**EVIDENCE STRENGTH:** Weak as evidence of *efficacy* (these are self-published individual projects, not peer-reviewed); **Strong as evidence of feasibility** — the pattern is demonstrably executable by one person
**IMPLICATION:** This is the template, and it is also an excellent capstone deliverable in its own right. The minimum implementation:
- A `preregistration.md` committed to git **before** touching the holdout, stating: the universe, the disqualifier thresholds, the component panel and its weights/ordering, the exit rule, the cost assumption, the primary metric, the decision threshold, and the stopping rule.
- A machine-written `trials.jsonl` appended by the backtest harness itself on **every** run — config hash, git SHA, data snapshot ID, timestamp, and all metrics. Non-optional and not hand-maintained: if logging is a human discipline it will not survive contact with a debugging session.
- A sealed holdout period that the harness physically refuses to read unless a `--final` flag plus a one-line justification is supplied, with that invocation also logged.
- The evaporation curve regenerated from `trials.jsonl` as a build artefact.

Effort: **1–2 days**, and it is the highest-leverage 1–2 days in the whole project, because without it DSR, PBO and every p-value are uncomputable.

### CLAIM: Backtest overfitting calculators exist that take N trials and k free parameters and return the expected spurious Sharpe.
**SOURCE:** AuditZK, Backtest Overfitting Calculator (Bailey & López de Prado implementation) — https://www.auditzk.com/tools/backtest-overfitting
**EVIDENCE STRENGTH:** Weak (unattributed third-party implementation; its own page admits it does not show the formula behind its MinBTL output)
**IMPLICATION:** Useful for a sanity check, not as a citation. It gives selection bias ≈ √(2 ln N)/√T and parameter inflation ≈ √(k/T) — note the second term: **a composite score with 8 component weights carries √(8/60) ≈ 0.37 monthly ≈ 1.27 annualised of parameter inflation on its own.** This is an independent quantitative argument for Wave 1's conclusion that the 0–100 composite is not supportable: the free parameters alone manufacture a Sharpe of over 1.

---

## 4. Calibration measurement — the hard open question

### CLAIM: Optimising a single proper scoring rule such as Brier does **not** guarantee good decisions for an agent whose loss function you do not know; the correct object is U-calibration, the worst-case regret over all bounded proper scoring rules.
**SOURCE:** Kleinberg, Leme, Schneider & Teng, "U-Calibration: Forecasting for an Unknown Agent," COLT 2023; arXiv 2307.00168 — https://arxiv.org/pdf/2307.00168
**EVIDENCE STRENGTH:** Strong (theory with proofs and an explicit finite-sample computation)
**IMPLICATION:** **This is the direct answer to Wave 1's open question, and it is a better answer than I expected to find.** The setup is exactly the project's: a forecaster issues probabilities, and a downstream agent with an *unknown* utility function acts on them. Key results: each agent corresponds to a proper scoring rule, so agent regret equals scoring-rule regret; calibration error bounds agent regret for every bounded agent (`AgentReg ≤ 4·Cal`); sublinear U-calibration error is equivalent to sublinear regret for all agents; and the tractable relaxation **V-calibration** — maximising over V-shaped rules `ℓ_v(p) = −|p − v|` — is within a factor of 2 (`½·UCal ≤ VCal ≤ UCal`). Crucially for a builder, **V-regret has an explicit closed form that is piecewise linear in v with breakpoints at the observed predictions, so the supremum needs only finitely many evaluations** — it is computable from the developer's own trade journal in a few lines of code.

Practical recipe: for each predicted probability p_i and binary outcome y_i, compute `V-regret(v) = Σ[|p_i − v| − |y_i − v|]`-style terms over a grid of v values at the observed predictions, and report the maximum. The reportable statistic becomes "worst-case regret over all exit policies of this form," which is *more* defensible than a Brier score precisely because it does not assume one exit rule. Caveat: the O(√T) rates are guarantees for their algorithm's expected behaviour, and the finite-sample computation is a descriptive statistic on the observed sequence, so with 60–300 observations it is a diagnostic, not a hypothesis test.

### CLAIM: The Integrated Brier Score and concordance-index variants are **not** proper scoring rules for time-to-event outcomes, and most published survival metrics have no properness proof.
**SOURCE:** Yanagisawa, "Proper Scoring Rules for Survival Analysis," ICML 2023; arXiv 2305.00621 — https://arxiv.org/html/2305.00621v3 (citing Rindt et al. 2022, Blanche et al. 2018, Sonabend et al. 2022)
**EVIDENCE STRENGTH:** Strong (theorems, with prior results independently establishing the impropriety)
**IMPLICATION:** If the project frames "will this contract reach the target before expiry" as a time-to-event problem — which is the natural framing for a path-dependent outcome with a time limit — then the obvious metrics are wrong. Proper under correct censoring weights: Portnoy's estimator (Thm 4.5), Cen-log (4.6), Cen-Brier (4.7), Cen-RPS (4.8). **Only Cen-log-simple can be used as an evaluation metric without knowing the censoring weights** — that is the one to use. It needs a sufficiently large number of discretisation bins; their appendix suggests B > 16. For calibration specifically they recommend D-calibration or their KM-calibration (a KL divergence against the Kaplan-Meier estimate). Assumptions: right-censoring only, and event time independent of censoring time given features. Their experiments used 7,874–14,294 observations with 32–72% censoring — **two to three orders of magnitude more data than this project will have**, which is the binding constraint.

### CLAIM: Defining a mechanical exit rule converts the path-dependent outcome into a well-defined label, and this is the standard move — the triple-barrier method.
**SOURCE:** López de Prado, "The 10 Reasons Most Machine Learning Funds Fail" (2018), reason 5 — https://www.smallake.kr/wp-content/uploads/2018/07/SSRN-id3104816.pdf ; practitioner treatments: https://www.quantt.co.uk/resources/triple-barrier-method , https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/
**EVIDENCE STRENGTH:** Strong for the construction; Moderate for its efficacy
**IMPLICATION:** **This is the answer to "does defining a mechanical exit make the problem tractable?" — yes, and it is the only answer I found that actually works.** Label each contract by which of three barriers it touches first: profit target, stop loss, or time limit. The outcome becomes categorical and unambiguous, so Brier score and reliability diagrams become legitimate. Two essential consequences the sources insist on: (i) barriers should be scaled by volatility, not fixed in percent, or the labels encode nothing but realised vol; (ii) triple-barrier labels **overlap in time**, making samples non-IID — which is exactly why purging, embargo and uniqueness weighting (reasons 7–8 of the same paper) are mandatory companions, not optional extras. Also relevant: his reason 6, **meta-labelling** — a primary model picks direction and a secondary model decides whether to act. For this project the primary "model" is the component panel and the secondary question is "should the user take this trade at all," which maps cleanly and is a genuinely good capstone architecture.

### CLAIM: Broker-style probability-of-profit figures are expiry-based and diverge systematically from realised win rates under any real exit policy; the practical fix is bucketed predicted-vs-realised reporting from a trade journal with minimum-count suppression.
**SOURCE:** OptionScanner, "How Probability of Profit Is Computed and Checked" (2026) — https://optionscanner.ai/learn/probability-of-profit-methodology
**EVIDENCE STRENGTH:** Weak as evidence (a vendor describing its own product, no published validation); Moderate as a design pattern
**IMPLICATION:** The pattern is worth copying because it is the only consumer-facing calibration methodology I located, and it is cheap: compute POP as N(d₂) under a risk-neutral lognormal using the strike's own IV, with a smile-slope finite-difference correction; also report probability-of-touch (roughly 2× the terminal probability under zero drift) to approximate loss-triggered mid-hold exits; then maintain a standing calibration report that buckets trades by predicted probability and shows realised win rate next to predicted. Their operational thresholds: **no report until at least 30 labelled trades; suppress buckets with fewer than 10 rows; print the sample size beside every figure.** They explicitly attribute the predicted-realised gap to exit policy — their exits fire at 50% of max profit, at a loss multiple, or at 21 DTE, while the prediction assumes expiry. No Brier score or reliability diagram is mentioned, which is a gap the capstone can fill.

### CLAIM: Brier scores for entry-time option profit probabilities were found to be broadly stable across time-to-expiration on a large sample, with outcomes measured at expiration.
**SOURCE:** Option Alpha, "The 'Moment in Time' Problem for Option Profit Probabilities" (2026) — https://optionalpha.com/blog/moment-in-time-option-profit-probabilities
**EVIDENCE STRENGTH:** Weak (vendor blog, no peer review, no released data, and the central reasoning is weak — see below), but it is the **only large-sample Brier-scored options calibration study I located**
**IMPLICATION:** Sample sizes are notable: ~905k trades at ≤30 DTE scored at entry, plus ~11.2m probabilities recalculated every ~15 minutes for ~30k trades. Brier scores were "mostly stable" across DTE and mid-trade probabilities scored slightly better. **Treat the conclusion with real suspicion:** they measure outcomes at expiration, so they have assumed away exactly the path-dependence problem, and the article's reassurance that "a 60% trade still expires in profit 60% of the time regardless of the interim" is only true of the ex-ante distribution and says nothing about a holder who exits early. The useful takeaway is narrow and still valuable: **if you fix the exit at expiry, Brier scoring of option probabilities is empirically well-behaved and has been done at scale.** That is a real, if modest, foundation.

### CLAIM: Forecasting-tournament practice resolves the analogous problem by *defining away* ambiguity — questions are written with mechanical resolution criteria before forecasts are collected.
**SOURCE:** Mellers et al., "Identifying and Cultivating Superforecasters as a Method of Improving Probabilistic Predictions," *Perspectives on Psychological Science* (2015) — https://web.stanford.edu/~knutson/jdm/mellers15.pdf ; feasibility replication in public health: Recchia et al., PMC9023363 — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9023363/ ; practitioner summary of GJP evidence — https://forum.effectivealtruism.org/posts/W94KjunX3hXAtZvXJ/
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** The transferable lesson is methodological rather than statistical: **tournaments do not solve path-dependence, they prohibit it at the question-writing stage.** Every question has a resolution date and a mechanical source. The project's analogue is to commit, in pre-registration, to one canonical outcome definition — and the triple-barrier label is the natural choice. Any alternative exit the user actually takes is then *their* deviation from the scored forecast, which is an honest and explainable division of responsibility to put in the UI.

### CLAIM: Classifier calibration has a mature toolkit, but it assumes a fixed, well-defined binary or multiclass outcome.
**SOURCE:** Filho, Song, Perello-Nieto, Santos-Rodriguez, Kull & Flach, "Classifier Calibration: A survey on how to assess and improve predicted class probabilities," arXiv 2112.10327 — https://arxiv.org/pdf/2112.10327
**EVIDENCE STRENGTH:** Strong (comprehensive survey)
**IMPLICATION:** Once the triple-barrier label fixes the outcome, standard machinery applies: reliability diagrams, ECE (with the standard warning that ECE is binning-sensitive and not a proper scoring rule), Brier with its calibration/refinement decomposition, Platt scaling and isotonic regression for recalibration. The decomposition is the useful part for a capstone: it separates *calibration* error from *resolution* (discrimination), and a ranker with good calibration and zero resolution is useless — which is a distinction the project must be able to show it understands.

---

## 5. Evaluating an ordinal ranking rather than a cardinal score

### CLAIM: The standard significance test for a ranking signal is the information-coefficient t-statistic, `t = mean(IC)/std(IC) × √(number of periods)`.
**SOURCE:** Practitioner standard; see Mill Street Research via IBKR Campus on IC-based stock ranking — https://www.interactivebrokers.com/campus/traders-insight/securities/stocks/mill-street-research-maer-stock-ranking-model-do-you-see-what-ic/ ; "Factor Evaluation in Quantitative Portfolio Management" — https://www.r-bloggers.com/2015/03/factor-evaluation-in-quantitative-portfolio-management/ ; reference implementation: `fynance.metrics.factor` — https://fynance.readthedocs.io/en/latest/_modules/fynance/metrics/factor.html
**EVIDENCE STRENGTH:** Moderate (universally used, but no single canonical citation; the formula is elementary)
**IMPLICATION:** Compute monthly cross-sectional Spearman rank correlation between the ordinal panel ranking and realised forward delta-hedged return. Then the arithmetic: with 60 months and a typical monthly IC standard deviation of ~0.10, **t = 2 requires a mean IC of 0.026 and t = 3 requires 0.039.** Those are not implausible for a genuinely good signal — monthly ICs of 0.02–0.05 are the realistic range for equity factors — which makes **IC the most statistically tractable primary metric available to this project.** This is an important, actionable result: it is far easier to detect a signal in cross-sectional rank correlation over 60 months than to certify a Sharpe ratio over the same window, because the IC test uses the cross-section while the Sharpe test does not. **Recommend IC-IR as the primary pre-registered metric and Sharpe as secondary.**

### CLAIM: Decile analysis is under-powered in a liquidity-qualified options universe; quintiles or terciles are the honest choice.
**SOURCE:** Derived from the universe arithmetic plus standard quantile-portfolio practice (r-bloggers factor-evaluation reference above)
**EVIDENCE STRENGTH:** Weak (my derivation from source-reported practice, not a cited result)
**IMPLICATION:** A universe surviving hard liquidity disqualifiers is realistically 150–400 names. Deciles give 15–40 names per bucket, and the top bucket's monthly return has a standard error large enough to swamp a 1%/month spread. **Use terciles or quintiles, report bucket counts on every chart, and report the full monotonicity pattern rather than only the top-minus-bottom spread** — monotonicity across buckets is weak evidence that survives small samples better than a single spread t-test, because it is a shape claim rather than a magnitude claim.

### CLAIM: Top-N hit rates require sample sizes far beyond this project's reach to distinguish modest edges.
**SOURCE:** Standard two-proportion power calculation
**EVIDENCE STRENGTH:** Strong (elementary statistics)
**IMPLICATION:** `n = (z_{α/2} + z_β)²·p(1−p)/δ²`. Distinguishing a 55% hit rate from 50% at 80% power and 5% two-sided needs **≈ 785 independent observations.** A top-5 monthly selection over 5 years yields 300 nominal trades, and because the five picks in a given month share market and sector exposure the effective independent count is closer to 60–100. **Conclusion: top-N hit rate is a dashboard number and an honest-expectation-setting device, not evidence.** Say so explicitly rather than reporting it as a result.

---

## 6. Paper trading and forward testing

### CLAIM: The minimum forward-test duration is computable, and for realistic Sharpe levels it exceeds any plausible capstone timeline by an order of magnitude.
**SOURCE:** Bailey & López de Prado, "The Sharpe Ratio Efficient Frontier" (2012), MinTRL — https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf
**EVIDENCE STRENGTH:** Strong
**IMPLICATION:** Applying MinTRL against a zero benchmark with normal monthly returns: establishing an annualised Sharpe of 1.0 as non-zero at 95% needs **≈ 35 months**; Sharpe 0.5 needs **≈ 132 months (11 years)**. With realistic negative skew and excess kurtosis both numbers rise ~20–55%. A 9-week course module can therefore produce **zero** statistical evidence from forward testing. What a short forward test *can* do, and should be scoped to do, is detect implementation bugs, data-pipeline failures, cost misestimation, and gross divergence between simulated and live fills. That is a legitimate and valuable objective — just not a performance claim.

### CLAIM: Paper-trading fills are systematically optimistic because fills are conditionally adverse, and because non-fills are not modelled.
**SOURCE:** arXiv 2407.16527, "The Negative Drift of a Limit Order Fill" — https://arxiv.org/html/2407.16527v1 ; supporting market-simulation treatment: "Market Simulation under Adverse Selection," arXiv 2409.12721 — https://arxiv.org/pdf/2409.12721 ; practitioner corroboration: https://optionstradingiq.com/paper-trading/ , https://nexusfi.com/a/brokers/paper-trading-futures-simulators , https://blog.traderspost.io/article/traderspost-paper-trading-validation-guide
**EVIDENCE STRENGTH:** Moderate for the mechanism and magnitude; Weak for the practitioner-blog corroboration
**IMPLICATION:** The academic mechanism is the important part because it explains *why* rather than merely asserting. Two biases compound: (i) a resting order fills preferentially when the market is moving against it, so the post-fill mid drifts adversely by roughly a half-tick, cancelling the spread capture a simulator credits; (ii) **about a third of resting orders never fill**, and a simulator that fills everything silently awards the strategy the trades it would have missed. Options paper trading adds a third: broker simulators typically fill at or near the mid, which §1 already establishes as the dominant source of optimism. **Engineering guard: in paper trading, log the quoted bid/ask at decision time and the actual fill, and report the realised fraction-of-spread paid as a first-class metric.** That measurement is cheap, accumulates from trade one, and is the single most valuable thing a short forward test can produce — because Wave 1 established that costs, not signal, decide whether this system works at all.

---

## 7. Evaluation of LLM-based and agentic systems

### CLAIM: An outcome-only LLM judge can show high apparent recall on agent failures while having literally zero discriminative power, because its "detections" are its false-alarm rate.
**SOURCE:** Mohammadi, "trajectory-judge: What Outcome-Only LLM Judges Miss on Agent Trajectories," arXiv 2609.00038 (2026) — https://arxiv.org/pdf/2609.00038
**EVIDENCE STRENGTH:** Strong methodologically (deterministic environment, scripted oracle, 400 exactly-labelled trajectories with paired clean/faulty designs); limited externally (one environment, two local models, single-edit injected faults)
**IMPLICATION:** The headline result is the one to build on: on fault types that leave the final reply unchanged, the outcome-only judge showed 34–76% recall but **paired discrimination of exactly zero** — that recall was purely its false-alarm rate on clean runs. Overall it scored 0.613 recall with a 0.330 false-alarm rate and paired Δ of only +0.163. A **step judge** — the same model, instructed to check each step — flagged all four reply-unchanged fault types with **0 false alarms on 100 clean runs** (false-alarm upper bound 3.6%). Both the view and the instruction mattered: a reply-only judge told to check steps reached paired +0.69 against +1.00 for the step judge. An 8B judge flagged 397/400, making its recall meaningless. Majority voting at k=3 tripled cost with no measurable gain because errors were correlated across samples. Attribution is separately weak: the step judge detected 257/300 faults but misnamed the type 29% of the time.

Direct build actions: **(1) always score judges against paired clean controls, never recall alone; (2) check the judge on clean runs before trusting any number; (3) instruct judges to evaluate steps, not just the final numeric output; (4) evaluate detection and attribution separately; (5) do not pay for ensembles without first checking error independence.** Item (3) is critical for this project specifically, because the architecture is "LLM intermediate judgment → numeric ranking," and a wrong intermediate judgment that produces a plausible rank is exactly a reply-unchanged fault.

### CLAIM: LLM judges often *perceive* defects but file them under the wrong rubric axis, and the shipping gate then ignores them — a wiring failure rather than a perception failure.
**SOURCE:** "Catching One in Five: LLM-as-Judge Blind Spots in Production Multi-Turn Transaction Agents," arXiv 2606.10315 (2026) — https://arxiv.org/pdf/2606.10315
**EVIDENCE STRENGTH:** Moderate (real production agent, human-confirmed ground truth, but one agent on one tenant, sampled corpus, inter-annotator κ = 0.61)
**IMPLICATION:** The gate caught 2 of 9 human-confirmed patterns in one batch (22%, Wilson CI 6.3–54.7%) and **0 of 220 rounds overall**, while humans confirmed 23 defects. Pooled catch rate ≈ 18%. The mechanism is instructive: of 125 judge notes, 114 described state defects and **113 of those were filed under "brand voice"** because the rubric had no axis for state. 15 of 30 confirmed patterns fell in categories the rubric did not cover at all. Their prevalence arithmetic: a gate reporting 10% with recall ≈ 0.2 implies ~50% true prevalence, a 3–6× undercount; and a gate reporting zero cannot be corrected at all. Recommendations to adopt: treat automated judging as an always-on regression *floor*, not a substitute for reading transcripts; judge the arc rather than the final turn; add explicit rubric axes for every failure category you care about and wire them to the pass/fail verdict; and **report the judge's measured recall alongside any quality number.** The last is the cheapest credibility win in the whole eval module: a quality score without a judge-recall figure is uninterpretable.

### CLAIM: LLM judges exhibit measurable self-preference bias, apparently driven by familiarity (low perplexity) rather than self-authorship per se.
**SOURCE:** Wataoka, Takahashi & Ri, "Self-Preference Bias in LLM-as-a-Judge," arXiv 2410.21819 — https://arxiv.org/pdf/2410.21819 ; related 2026 work: "Self- and Other-Labels Induce Bidirectional Bias in LLM Judges," arXiv 2608.18091 — https://arxiv.org/pdf/2608.18091 ; "Who Judges Matters: Measuring Family-Conditioned Preference in LLM-as-Judge Panels," arXiv 2609.17857 — https://arxiv.org/pdf/2609.17857
**EVIDENCE STRENGTH:** Moderate (clear metric and measurements; the perplexity explanation is correlational, and the model set is now dated)
**IMPLICATION:** Under their equal-opportunity metric GPT-4 scored ≈ 0.520 (recalls 0.945 vs 0.425); under demographic parity, GPT-4 0.749, Vicuna-13b 0.382, GPT-3.5-turbo 0.191, with some smaller models showing reverse bias. Every evaluator showed lower average log-perplexity on its own outputs. Build actions: **use a different model family for judging than for generation; randomise presentation order; never let a model judge text it wrote.** The 2026 panel work suggests judge panels inherit family-conditioned preferences, so a panel of one family is not a fix.

### CLAIM: Generic prompt "improvements" can degrade application-level performance, so prompt and model changes require a held-out regression suite.
**SOURCE:** "When Generic Prompt Improvements Hurt: Evaluation-Driven Iteration for LLM Applications," arXiv 2601.22025 (2026) — https://arxiv.org/pdf/2601.22025
**EVIDENCE STRENGTH:** Moderate (I read the framing and abstract, not the full experimental detail)
**IMPLICATION:** Treat every prompt edit and model upgrade as a code change behind a test suite. Minimum viable: 30–60 frozen input cases with expected outputs or expected properties, run on every change, with results diffed and committed. For this project the natural cases are EDGAR filing excerpts with hand-labelled language-change judgments, and chain snapshots with hand-verified disqualifier outcomes. This also gives the capstone a demonstrable regression-testing story at low cost (~1 day to build, then minutes per change).

### CLAIM: RAG faithfulness should be measured by decomposing generated output into atomic claims and checking each against retrieved context, with retrieval and generation scored separately.
**SOURCE:** Kili Technology, "RAG Evaluation Methods: Separate Retrieval from Generation" — https://kili-technology.com/blog/rag-evaluation-guide-measuring-retrieval-and-generation-as-separate-problems ; "Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards," EMNLP 2025 Industry Track — https://aclanthology.org/2025.emnlp-industry.54.pdf ; 2026 practitioner surveys — https://futureagi.com/blog/evaluating-rag-faithfulness-deep-dive-2026/
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** For the EDGAR filing-language-change signal — Wave 1's best-evidenced LLM-dependent component — the pipeline needs: context precision and recall on retrieval, then claim-level faithfulness on generation, scored separately so a failure can be localised. Concretely: every assertion in a generated filing summary should carry a span pointer into the source filing, and any assertion without one is a faithfulness failure. This makes faithfulness mechanically checkable rather than judge-dependent, which given §7's judge findings is a significant advantage.

### CLAIM: Human faithfulness annotations are themselves not locally faithful, so aggregate faithfulness scores can mask claim-level errors.
**SOURCE:** "Averaging Bias: Human Faithfulness Annotations are not Locally Faithful," arXiv 2608.00205 (2026) — https://arxiv.org/pdf/2608.00205
**EVIDENCE STRENGTH:** Moderate
**IMPLICATION:** Report the *distribution* of claim-level faithfulness and the worst-case claim, not only the mean. For a financial summary, one unsupported claim about a filing can drive the whole ranking decision, so a 0.95 average is not reassuring.

### CLAIM: OpenTelemetry GenAI semantic conventions now provide a vendor-neutral standard for agent tracing, making per-step logging and replay a configuration task rather than a build.
**SOURCE:** OpenTelemetry GenAI semantic conventions, as covered in 2026 practitioner write-ups — https://dev.to/gabrielanhaia/opentelemetry-genai-semantic-conventions-your-llm-traces-should-look-like-this-in-2026-3ff6 , https://jacar.es/en/agent-observability-with-opentelemetry-genai-semconv-in-2026/ , https://www.morphllm.com/agent-tracing ; platform comparisons — https://www.marktechpost.com/2026/08/09/top-llm-observability-and-evaluation-platforms-in-2026-langfuse-langsmith-braintrust-arize-and-more-compared/ , https://www.confident-ai.com/knowledge-base/compare/10-llm-observability-tools-to-evaluate-and-monitor-ai-2026 ; Arize agent-observability guide — https://arize.com/ai-agents/agent-observability/
**EVIDENCE STRENGTH:** Moderate (consistent across independent 2026 sources; I did not read the spec itself, so treat specific attribute names as needing verification against the current spec)
**IMPLICATION:** Instrument with OTel GenAI semconv and export to a self-hostable backend — Langfuse and Arize Phoenix are both open-source and run locally, which suits a single-user project with no budget. Span per agent step, with model, prompt, token counts, latency, cost, tool calls and the retrieved context attached. **The capstone-relevant requirement beyond standard tracing is replay**: store the full input bundle (chain snapshot ID, retrieved documents, prompt, model version, seed/temperature) so any historical ranking can be regenerated bit-for-bit. Without replay, neither the regression suite nor the hindsight audit nor any post-hoc debugging of a bad recommendation is possible. This is a design requirement, not an add-on, and it is cheap if decided early and expensive if retrofitted.

---

## 8. VALIDATION PROTOCOL

Ordered and executable. Effort estimates assume a competent developer working part-time alongside the course. Steps 0–3 are mandatory; they are cheap and everything else depends on them. Steps 4–9 are the actual validation.

**Step 0 — Start the snapshot archive tonight. (2 hours, then automated)**
Nightly cron storing the full option chain for the candidate universe plus underlying OHLCV, dividends, and corporate-action notices, keyed by snapshot timestamp and never mutated. Also store the universe membership as of that date. *Sample requirement: none — this is the thing that creates sample.* Rationale: §1. Every day of delay is permanently lost evidence, and this is the only step with a hard deadline.

**Step 1 — Write and commit the pre-registration. (4 hours)**
`preregistration.md` in git, before any holdout contact, specifying: universe and liquidity disqualifier thresholds (spread % of premium, OI, volume, moneyness and maturity bands); the ordinal component panel and its ordering rule; **the canonical outcome definition — triple-barrier with volatility-scaled profit target, stop, and time limit** (§4); the cost assumption (base case 75% of quoted spread per §1, with a 25/50/75/100% ladder); the **primary metric: monthly cross-sectional IC with IC-IR t-statistic** (§5); the decision threshold (t ≥ 3.0 per Harvey/Liu/Zhu, §3); the number of confirmatory trials permitted (**say 3**, per §0); and the stopping rule. *Sample requirement: none.* This is the step that makes DSR computable later.

**Step 2 — Build the trial ledger and sealed holdout into the harness. (1 day)**
`trials.jsonl` appended automatically on every backtest invocation: config hash, git SHA, data snapshot ID, timestamp, all metrics. Harness refuses to read the sealed period without `--final` plus a logged justification string. *Sample requirement: none.* Per §3. Must be machine-enforced, not human discipline.

**Step 3 — Implement the structural no-look-ahead guardrail. (2 days)**
Following arXiv 2608.27734 (§2): signals computed from data through the decision timestamp, positions from the next bar; publication-delay enforcement on filing and fundamental data; an audit layer that **rejects** a configuration referencing future data rather than silently fixing it; no repainting indicators — any pivot/zigzag/fractal detector must be computed causally and unit-tested by confirming its historical values never change when new bars arrive. *Sample requirement: none.* Remember the finding that a deliberately leaky strategy scored DSR 1.00 — deflation does not catch leakage, only structure does.

**Step 4 — Run the three leakage and sanity oracles. (1 day)**
(a) **Leaky oracle**: deliberately feed a future-return feature and confirm the harness produces an absurd Sharpe — this validates that the harness can detect anything at all. (b) **One-switch test** (§2): shift decision time by one bar and confirm performance degrades gracefully rather than collapsing. (c) **Random-signal null**: replace the ordinal panel with random rankings, run the same pipeline, and record the resulting Sharpe and IC distribution over ~1,000 draws. *Sample requirement: the full available history.* Guard (c) is the most informative single diagnostic in the whole protocol: if the real signal's IC sits inside the random distribution, stop.

**Step 5 — Cost-ladder the signal on the design window. (2 days)**
Compute delta-hedged or simple contract returns per §1, with the Cao et al. construction if replicating academic results. Report net IC and net Sharpe at midpoint and at 25 / 50 / 75 / 100% of quoted spread. *Sample requirement: all design-window months; report monthly counts.* **Decision gate: if net IC at 75% of spread is not positive, the project has no tradeable signal and no further validation is informative.** State that gate in the pre-registration so passing it is not a post-hoc choice.

**Step 6 — Purged/embargoed CV and CPCV on the design window. (2 days)**
Use `purged-cross-validation` (§2). Purge one label-horizon either side; embargo a fixed fraction. Run CPCV with 6 groups and 2 test groups for 15 splits and 5 reconstructed paths. Report the **distribution** of Sharpe and IC, plus PBO. *Sample requirement: ≥ 60 monthly observations for this to be more than decorative; with fewer, report it as a diagnostic only.*

**Step 7 — Compute the honest statistics. (1 day)**
From `trials.jsonl`: N and Sharpe dispersion → **DSR**; realised skew and kurtosis → **PSR** and **MinTRL**; IC series → **IC-IR t-statistic** against the t = 3.0 hurdle; stationary-bootstrap CI on the evaluation-window Sharpe; and the **evaporation curve** over ledger prefixes. *Sample requirement: whatever exists — the point is that these quantities state their own insufficiency.*

**Step 8 — Single sealed-holdout evaluation, run exactly once. (half a day)**
Unseal, run the frozen configuration, report. No iteration. If it fails, the honest output is a documented negative result — which, per §3's public repositories and arXiv 2608.27734, is the normal outcome and a perfectly good capstone. *Sample requirement: ≥ 24 months of holdout to say anything at all; it will still be under-powered.*

**Step 9 — Forward test, scoped to engineering validation only. (ongoing, 2 hours/week)**
Log for every recommendation: decision-time bid/ask, the simulated fill, the actual fill, the realised fraction-of-spread paid, non-fills, and the triple-barrier outcome. Primary deliverable is **the realised cost distribution versus the assumed 75%**, not performance. Maintain a bucketed predicted-vs-realised calibration table with the OptionScanner thresholds — no report below 30 labelled trades, suppress buckets under 10 rows, print n beside every figure (§4). *Sample requirement: 30 trades for a first calibration table; ~35 months for any Sharpe inference.*

**Step 10 — Agent evaluation suite, in parallel. (3 days)**
(a) 30–60 frozen regression cases run on every prompt/model change (§7). (b) **Step-level** judge with paired clean controls, reporting measured judge recall alongside every quality score, using a different model family than the generator (§7). (c) Claim-level faithfulness with span pointers for EDGAR summaries, reporting the distribution and worst case. (d) OTel GenAI tracing with **full replay bundles**. (e) The parametric-hindsight audit (§2) — present dated contexts differing only in post-cutoff information and check judgment invariance.

**Total effort: roughly 15–18 working days of engineering, plus ongoing weekly forward-test logging.** That is genuinely achievable for a capstone. Steps 0 and 2 should happen this week.

---

## 9. TRAP CHECKLIST

Usable as an engineering checklist. Each entry: the lie, then the guard.

**Data and point-in-time integrity**
1. **Today's chain used for a past date.** → Snapshot archive keyed by timestamp, immutable; assert snapshot ID on every backtest row.
2. **Option prices reconstructed from a model.** → Use stored quotes; if a quote is missing, drop the observation and log the drop; never interpolate a price and then measure IV from it.
3. **Vendor backfill or re-stamping.** → Hash each nightly snapshot on receipt; alert on any change to a historical snapshot.
4. **Survivorship via the underlying.** → Point-in-time universe membership including delisted, bankrupt and acquired names; if using a current list, disclose it and state the bias direction.
5. **Stale, crossed, zero or missing quotes.** → Flag and *retain* excluded observations; report exclusion counts per month; a month with anomalous exclusions is a month to distrust.
6. **Timestamp and session misalignment.** → Align option, underlying and session calendars; special-case half-days, where fields labelled with a close time reflect earlier observations.

**Look-ahead**
7. **Day-t open fills on signals using day-t highs/lows** (Wave 1: ~22–26 Sharpe points). → Signal from bars through t, position from t+1; enforce structurally in the audit layer.
8. **Repainting pivot, zigzag or fractal detectors.** → Causal computation only; unit test that historical indicator values are immutable as new bars arrive.
9. **End-of-day Greeks selecting an earlier trade.** → Selection uses only decision-time-or-earlier Greeks; store which delta was used.
10. **Fundamental or filing data used before its publication date.** → Publication-delay enforcement; audit layer rejects rather than repairs.
11. **Parametric hindsight in the LLM** — unique to this build and undetectable by purged CV. → Restrict LLM context to retrieved documents; measure claim-level faithfulness; run the hindsight-invariance audit; **disclose as an unquantified limitation.**
12. **Leakage invisible to statistics.** → A deliberately leaky strategy scored DSR 1.00; only the structural guardrail catches this. Run the leaky oracle to prove the harness works.

**Costs and execution**
13. **Midpoint fills.** → Base case 75% of quoted spread for single-leg (ORATS); report the full 25/50/75/100% ladder; headline the 75% figure.
14. **Non-fills ignored.** → Model fill probability; roughly a third of resting orders never filled in the one study measuring it. A strategy whose winners don't fill is worthless.
15. **Spread capture credited to passive fills.** → Adverse post-fill drift ≈ half a tick approximately cancels it; do not credit spread capture.
16. **Commissions charged once, or per trade instead of per leg.** → Per leg, per side, at real broker rates ($0.50–1.30/contract/leg).
17. **Assignment and exercise fees omitted.** → $0–15 per occurrence.
18. **Quoted spread treated as the cost when premium is small.** → Express spread as % of premium (the Wave-1 disqualifier) — average ATM equity-option quoted spread is ~20% of premium, median ~15.6%.
19. **Daily delta-hedge rebalancing costed at zero.** → If replicating academic delta-hedged returns, charge equity transaction costs on every rebalance; the academic baseline does not.

**Contract lifecycle**
20. **Position deleted at expiry instead of settled.** → Model exercise/assignment/settlement cash flows and resulting share positions.
21. **Early assignment assumed away.** → Model early exercise of deep-ITM short calls near ex-dividend; document the threshold used. Note the academic literature avoids this by excluding dividend payers entirely.
22. **Non-standard deliverables assumed to be 100 shares.** → Read OCC adjustment memos; a 3:2 split leaves a 150-share deliverable. Simplest honest guard: hard-disqualify non-standard contracts.
23. **Pre-deal IV carried through a merger.** → Disqualify names with announced-but-uneffected mergers, splits or special dividends.
24. **Adjusted contracts traded at standard liquidity.** → Separate instruments, wider spreads, fill penalty, or excluded outright.

**Statistics**
25. **Unknown trial count.** → Machine-written `trials.jsonl`; N cannot be reconstructed afterwards, and without it DSR and PBO are uncomputable.
26. **Composite-score free parameters inflating Sharpe.** → Parameter inflation ≈ √(k/T); 8 weights on 60 months manufactures ~1.27 annualised Sharpe from nothing. Prefer a fixed ordinal panel with no fitted weights.
27. **Single walk-forward path treated as the answer.** → CPCV for a distribution; report dispersion, not the point estimate.
28. **Overlapping triple-barrier labels treated as IID.** → Purge, embargo, uniqueness-weight.
29. **Nominal Sharpe reported without deflation.** → DSR with honest N; 12 trials on 60 months already puts the zero-skill bar at Sharpe 1.0.
30. **t = 2 treated as significance.** → Harvey/Liu/Zhu hurdle t ≈ 3.0, rising to 3.18+ once unobserved tests are modelled.
31. **Normal-returns Sharpe inference on fat-tailed option returns.** → PSR with realised skew and kurtosis; non-normality lengthened one worked MinTRL case by 54%.
32. **Out-of-sample profit read as skill.** → A random-weights null earned +23% out of sample with DSR 0.0008. Always run the random-signal null.
33. **Decile analysis on 200 names.** → Terciles or quintiles; report bucket counts; prefer monotonicity over a single spread.
34. **Top-N hit rate reported as evidence.** → Needs ~785 independent observations for a 55%-vs-50% distinction; label it a dashboard metric.
35. **Published-signal decay ignored** (Wave 1: ~40–58%, contested). → Haircut any literature-derived expectation and state the haircut; do not treat an in-sample replication as confirmation of the published effect size.
36. **Holdout touched more than once.** → `--final` flag with logged justification; one shot.

**Agent and LLM evaluation**
37. **Outcome-only judging of a multi-step pipeline.** → Step-level judging; paired clean controls; zero paired discrimination can hide behind 76% recall.
38. **Quality score reported without judge recall.** → Report measured recall beside it; an 18% catch rate implies a 3–6× undercount.
39. **Rubric missing axes for the failure modes you care about.** → 113 of 125 state-defect notes were misfiled under "brand voice" because no axis existed; add axes and wire them to pass/fail.
40. **Model judging its own output.** → Different model family; randomise order; GPT-4 scored 0.749 on self-preference under demographic parity.
41. **Judge ensembles assumed to help.** → k=3 voting tripled cost with no gain because errors were correlated; test error independence first.
42. **Prompt or model change shipped without regression.** → 30–60 frozen cases on every change; generic prompt improvements can degrade application performance.
43. **Mean faithfulness masking a decisive bad claim.** → Report the claim-level distribution and the worst case, with span pointers.
44. **No replay capability.** → Store the full input bundle (snapshot ID, retrieved docs, prompt, model version, sampling params) per decision.

---

## 10. CALIBRATION VERDICT

**Partially tractable — and more tractable than Wave 1 concluded, provided the project accepts one constraint.**

The honest decomposition:

**What is genuinely unsolved.** There is no method for calibrating a probability attached to an outcome whose definition depends on a future free choice by the user. This is not a gap in the literature; it is ill-posed. "Probability this contract is profitable" has no truth value until an exit is specified, so no scoring rule can be applied to it. Any consumer-facing score that implies otherwise is not merely uncalibrated but uncalibratable. My searching found **no methodology for calibrating a consumer-facing options contract score under user-chosen exit**, confirming Wave 1's open question.

**What makes it tractable.** Three moves, in order of importance:

1. **Fix the exit mechanically — the triple-barrier label.** Volatility-scaled profit target, stop, and time limit, with the outcome being whichever barrier is touched first. This converts a path-dependent non-event into a well-defined categorical outcome, after which Brier score, reliability diagrams, the calibration/refinement decomposition, and isotonic or Platt recalibration all become legitimate. This is standard practice with a canonical source, and it is the single move that unlocks everything else. The cost is honest and must be stated in the UI: **the score is calibrated to a specific stated exit policy, and a user who exits differently is not covered by it.** That is a defensible contract with the user, and arguably a better product than a vague probability.

2. **Report U-calibration, or its V-calibration relaxation, as the robustness statistic.** This is the strongest finding in this strand. U-calibration is the worst-case regret over all bounded proper scoring rules, equivalently over all downstream agents with bounded utilities — which is precisely "all exit policies the user might adopt." It is theoretically the right object (sublinear U-calibration error is *equivalent* to sublinear regret for all agents), the V-shaped relaxation is within a factor of 2, and **V-regret has a closed form that is piecewise linear with breakpoints at the observed predictions, so it is computable from a modest trade journal in a few lines of code.** This lets the project say something genuinely strong: not "our probabilities are calibrated for one exit rule" but "worst-case regret across all exit policies of this family is bounded by X on our sample." For a capstone, deriving and implementing this is a distinctive contribution.

3. **Use the survival framing only if the data supports it, and avoid the obvious metrics.** If the project prefers "time until the target is reached," note that the Integrated Brier Score and all C-index variants are **not proper** scoring rules for time-to-event data. Of the proper alternatives, only Cen-log-simple is usable without knowing censoring weights, and it needs more than ~16 discretisation bins. The blocking problem is sample size: the validating experiments used 7,874–14,294 observations, versus the hundreds this project will have. **Recommendation: use triple-barrier categorical labels, not survival models.**

**Closest defensible substitute, concretely.** A **bucketed predicted-versus-realised calibration table against a pre-registered mechanical exit rule**, with sample counts printed on every row, buckets under 10 rows suppressed, no table published below 30 labelled trades, plus a V-calibration worst-case regret figure, plus an explicit UI statement of the exit policy the number is conditioned on. That is honest, cheap, implementable, and better than anything currently shipped by consumer options platforms — whose POP figures assume expiry while their own recommended exits fire at 50% of max profit or 21 DTE, a gap they acknowledge and do not correct.

**One supporting data point worth keeping.** Brier scoring of entry-time option profit probabilities has been done at genuine scale (~905k trades) with reasonably stable results — but with outcomes measured at expiration, i.e. having assumed the problem away. It establishes that the machinery works under a fixed exit, which is exactly the foundation move (1) relies on, and nothing more.

---

## 11. WHAT CLAIMS THE PROTOCOL LICENSES

**After Steps 0–7 (design-window validation), the developer can honestly say:**
- "I built a point-in-time options backtest with structurally enforced no-look-ahead, verified by a leakage oracle and a one-bar decision-time switch test."
- "The ranking's monthly cross-sectional information coefficient is X with an IC-IR t-statistic of Y, computed net of costs at 75% of quoted spread, against a pre-registered hurdle of t = 3.0."
- "I logged N trials. The deflated Sharpe ratio is Z. The expected maximum Sharpe under zero skill given N trials and my sample length is W." (If Z < 0.95, say so.)
- "The minimum track record length implied by my observed Sharpe, skew and kurtosis is M months. I have fewer than M, therefore I cannot reject zero skill."
- "Signal rank ordering is / is not monotone across terciles, with these bucket counts."
- "A random-signal null produces this distribution; my signal sits at this percentile of it."

**After Step 8 (sealed holdout), additionally:**
- "The frozen configuration produced this holdout result on a single unrepeated evaluation, with this bootstrap confidence interval." And, almost certainly: "the interval includes zero, so the result does not certify an edge."

**After Step 9 (forward test), additionally:**
- "Across K live decisions, the realised fraction of quoted spread paid was F, versus the 75% assumed. The cost model is / is not conservative." **This is the most valuable honest claim in the whole protocol**, because Wave 1 established costs decide the outcome.
- "Predicted versus realised outcome rates by bucket, against the pre-registered exit rule, with n per bucket."
- "Worst-case V-calibration regret across exit policies on this sample is R."

**After Step 10 (agent evaluation), additionally:**
- "Every LLM step is traced under OTel GenAI semconv with full replay bundles; any historical recommendation can be regenerated exactly."
- "The step-level judge has measured recall of R against paired clean controls and false-alarm rate of F on clean runs; quality scores are reported with that recall attached."
- "Claim-level faithfulness for filing summaries is distributed as D with worst case W, every assertion carrying a source span."
- "A frozen regression suite of N cases gates every prompt and model change."

**What the protocol never licenses, at this sample size:**
- That the system has positive expected net return.
- That the ranking is better than an alternative ranking with any stated confidence.
- Any Sharpe ratio stated without its deflation, N, and MinTRL.
- That live performance will resemble backtested performance.
- That the LLM components are free of hindsight contamination — this is structurally unmeasurable here.
- That the score is calibrated for any exit other than the pre-registered one.

**The capstone framing that is both honest and strong:** this is a correctly-instrumented falsification apparatus with a complete audit trail, which reports its own statistical insufficiency rather than concealing it. Per arXiv 2608.27734, under honest accounting passive premia were certified and every LLM-discovered strategy failed — **and the authors frame that as the system working.** A negative result with a trial ledger, an evaporation curve, and a correctly-computed DSR is a better capstone than a positive result without them, and it is also the more likely outcome.

---

## 12. DISCONFIRMING EVIDENCE

**1. Validation at this scale genuinely cannot certify a moderate edge, and the most rigorous study of this exact problem found nothing survived.** arXiv 2608.27734: five repeated LLM-discovery runs were **all profitable out of sample and 0 of 5 survived deflation** (DSR 0.15–0.29). The author's own human production trading system scored design Sharpe 0.33 and evaluation −0.12. Classic factors managed DSR ≤ 0.32 with PBO 0.83. The only thing certified was buy-and-hold. A solo developer should expect the same and plan for it.

**2. The power arithmetic is not a tuning problem, it is a wall.** A true Sharpe of 0.6 needs ~11 years for t ≈ 2 and ~25 years for Harvey's t = 3. MinTRL for Sharpe 0.5 against zero is ~132 months. No protocol, tool or cleverness changes this. If the system's true net Sharpe is in the 0.3–0.6 range — the plausible range for a retail options signal after 75%-of-spread costs — **it cannot be distinguished from zero within the developer's lifetime of available data.**

**3. The trial budget is smaller than any real development process.** On 60 monthly observations, the zero-skill bar reaches Sharpe 0.5 at **fewer than two trials** and 1.0 at about twelve. López de Prado puts spurious 5%-level discovery at roughly 20 iterations. Any genuine development process will exceed this before lunch on day one. Pre-registration limits *confirmatory* trials but cannot shrink the exploratory count, so the deflated statistics will be uncomfortable no matter how disciplined the developer is. This is not a reason to skip the ledger; it is a reason to expect the ledger to deliver bad news.

**4. Statistical deflation does not detect leakage, which undermines the natural assumption that rigorous statistics are the main defence.** A deliberately leaky strategy achieved design Sharpe 34.7 and **DSR 1.00** (arXiv 2608.27734). DSR, PBO and CPCV all assume the backtest is mechanically sound. If it is not, they certify the leak. Structural guardrails must come first, and they are engineering work, not statistics.

**5. CPCV and purged CV, though universally recommended, are near-decorative at this sample size.** On 60 monthly observations with a 1-month label, purging removes a meaningful fraction of each training fold and CPCV's reconstructed paths are heavily overlapping. The reference implementation's own model-selection notebook found **no model clearing DSR 0.95**. The library documents no default embargo fraction and no CPCV sizing guidance, so the developer is choosing hyperparameters for the validation procedure itself — which is another logged trial.

**6. Walk-forward's main critique applies to the fix as well.** López de Prado's objection is that walk-forward tests a single path. CPCV gives many paths — but all from the same 60 observations. The dispersion it reports is resampling variability, not independent evidence. It is honest about uncertainty and does not create information.

**7. The academic cost sensitivities may not be punitive enough, which undercuts the literature this build rests on.** Wave 1's edges died at 25–50% of quoted spread. The options data vendor that actually trades these instruments assumes **75% for a single leg**. If the vendor is right, the academic edges were already dead at the vendor's base case, and Wave 1's "costs dominate" conclusion is if anything understated.

**8. The "20% quoted spread" figure means the cost hurdle is enormous relative to any plausible monthly edge.** Cao et al. report average ATM equity-option quoted spreads around 20% of premium. At 75% of that, round-trip cost is roughly 15% of premium. Monthly long-short spreads in that literature are ~1.5% at midpoint. **The cost is an order of magnitude larger than the gross edge**, which is why the relevant question is whether a liquidity-qualified subuniverse has materially tighter spreads — a data question for the other agent, but a methodological warning here: a backtest on the *average* contract will not resemble a backtest on the *qualifying* contract, and the published evidence is about the former.

**9. The only consumer-facing calibration methodology located is a vendor's self-description, and the only large-sample options Brier study assumes away the hard part.** OptionScanner's bucketed report has no published validation. Option Alpha's ~905k-trade Brier analysis measures outcomes at expiration, and its central reassurance — that a 60% trade still expires profitably 60% of the time regardless of the interim — is true of the ex-ante distribution and irrelevant to a holder who exits early. **Neither constitutes evidence that a consumer options score can be calibrated.**

**10. Properness results for survival metrics depend on assumptions this project cannot verify.** The proper censored scoring rules require correct censoring weights, which must be estimated; the paper's properness theorems hold only when those weights are right. Their recovery is described as needing "a sufficient number of data points" with no threshold given, and the validating datasets were 7,874–14,294 observations. **At a few hundred observations the properness guarantees are not operative.**

**11. The LLM-evaluation literature it is natural to rely on is thin and barely external.** The trajectory-judge result comes from one synthetic environment with injected single-edit faults and two local models. The 18% judge catch rate comes from one agent on one tenant with sampled data and κ = 0.61 inter-annotator agreement. The self-preference bias numbers are on a model generation now several years old. These are the right *questions* and the right *methods*; the magnitudes should not be quoted as established.

**12. Parametric hindsight is a leakage channel with no available remedy.** The LLM components have a training cutoff well after the backtest period. An LLM asked to characterise a 2019 filing may be conditioning on the subsequent price move. No purging, embargo, CPCV or DSR touches this. Faithfulness measurement and invariance audits reduce but cannot eliminate it. **An LLM-assisted backtest over a period inside the model's training data is contaminated by construction, and this should be stated as a hard limitation rather than mitigated and forgotten.**

**13. OTel GenAI semantic conventions are described consistently by 2026 practitioner sources but I did not read the specification.** Specific attribute names and stability guarantees should be verified against the current spec before building against them; the conventions have been moving.

---

## 13. OPEN QUESTIONS

1. **Does the liquidity-qualified subuniverse have materially tighter spreads than the 20%-of-premium average in the literature?** This single number decides whether the project is viable, and it determines whether the academic evidence transfers at all. Measurable from the developer's own snapshot archive within weeks.
2. **What is the correct cost assumption for a retail single-leg options trade in 2026?** ORATS says 75% of width from experience; academic papers use midpoint; Wave 1's edges died at 25–50%. These are irreconcilable and the answer is empirical — which makes Step 9's realised-spread logging the highest-value measurement in the project.
3. **How should the hard-disqualifier stage be validated?** It is a filter, not a signal, so IC and Sharpe do not apply. Candidate approaches: measure realised execution cost inside versus outside the qualifying set; or treat disqualification as a classifier for "contract was tradeable at the assumed cost" and score it directly. I found no established methodology.
4. **Is V-calibration's closed form stable at 100–300 observations?** The theory is finite-sample computable, but its sampling distribution at this scale is not something I located. A bootstrap study on simulated data would settle it and is a tractable capstone contribution.
5. **What does an ordinal panel with no fitted weights do to the trial count?** Avoiding fitted weights removes the √(k/T) parameter inflation, but the *ordering* of components and the choice of which components to include are still choices. Is there a principled way to count them?
6. **Can parametric hindsight be bounded rather than merely disclosed?** Possible approach: compare agent judgments on pre-cutoff versus post-cutoff documents of matched type, treating any performance differential as an estimate of the contamination. I did not find this done.
7. **Does the published-signal decay figure (Wave 1: ~40–58%, contested) apply to delta-hedged option returns specifically, or only to equity anomalies?** The decay literature is overwhelmingly equity-based.
8. **What is the right embargo fraction and CPCV group count for a monthly signal on 60–120 observations?** No source gives guidance, and choosing them is itself a trial.
9. **Is there any published calibration study of a consumer-facing financial score under user-chosen action?** Adjacent domains — credit scoring, medical risk scores, sports betting models — may have solved an isomorphic problem. I did not search these and it may be the most promising remaining lead on the calibration question.
10. **Should the triple-barrier parameters be pre-registered as a single rule or as a small grid?** A single rule is statistically cleaner; a grid shows robustness but multiplies trials. The tradeoff is unresolved and matters for the pre-registration document.

---

## 14. TOP 10 SOURCES

1. **"What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery,"** arXiv 2608.27734 (2026) — https://arxiv.org/pdf/2608.27734 — *The single most applicable source. An agentic LLM strategy-discovery system evaluated honestly: constrained action surface, trial ledger, DSR, PBO, evaporation curve. DSR 1.00 on a deliberately leaky strategy; 0 of 5 profitable runs survived deflation. Copy the protocol and quote the numbers.*
2. **Bailey & López de Prado, "The Sharpe Ratio Efficient Frontier,"** *Journal of Risk* (2012) — https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf — *Exact PSR and MinTRL formulas with worked monthly non-normal examples. Answers "how long until this means anything" definitively.*
3. **Harvey, Liu & Zhu, "…and the Cross-Section of Expected Returns,"** *RFS* 29(1) 2016 / NBER WP 20592 — https://www.nber.org/system/files/working_papers/w20592/w20592.pdf — *The t ≈ 3.0 hurdle, 3.18+ with unobserved tests, BHY with the c(M) correction, and the estimate that 71% of tried factors never appear in print.*
4. **Kleinberg, Leme, Schneider & Teng, "U-Calibration: Forecasting for an Unknown Agent,"** COLT 2023, arXiv 2307.00168 — https://arxiv.org/pdf/2307.00168 — *The direct answer to the calibration open question. Worst-case regret over all downstream agents, with a computable V-shaped relaxation within a factor of 2.*
5. **López de Prado, "The 10 Reasons Most Machine Learning Funds Fail"** (2018) — https://www.smallake.kr/wp-content/uploads/2018/07/SSRN-id3104816.pdf — *Purging, embargo, CPCV, the walk-forward critique, triple-barrier labelling, meta-labelling, sample uniqueness, and the ~20-iterations-to-spurious-discovery figure, all in one short paper.*
6. **Cao, Han, Zhan et al., "Option Return Predictability"** (2016) — https://www.cicfconf.org/sites/default/files/paper_452.pdf — *The complete academic filter stack, the delta-hedged gain equation, and the midpoint-baseline plus fractional-spread ladder. What replication actually requires, and what the headline numbers assume.*
7. **ORATS, "Help, My Backtest Isn't Working!"** — https://orats.com/blog/help-my-backtest-isnt-working — *Slippage of 75/66/56/53% of bid-ask width by leg count, from a vendor that trades these instruments. The most concrete and most punitive defensible fill assumption located.*
8. **Mohammadi, "trajectory-judge: What Outcome-Only LLM Judges Miss on Agent Trajectories,"** arXiv 2609.00038 (2026) — https://arxiv.org/pdf/2609.00038 — *Paired clean controls reveal zero discrimination behind 34–76% apparent recall; step-level judging fixes it with 0 false alarms on 100 clean runs. Directly applicable to an LLM-judgment-feeds-numeric-output pipeline.*
9. **Yanagisawa, "Proper Scoring Rules for Survival Analysis,"** ICML 2023, arXiv 2305.00621 — https://arxiv.org/html/2305.00621v3 — *The Integrated Brier Score and C-index are not proper. Only Cen-log-simple is usable without censoring weights. Essential if the project considers a time-to-event framing.*
10. **"The Negative Drift of a Limit Order Fill,"** arXiv 2407.16527 (2024) — https://arxiv.org/html/2407.16527v1 — *The mechanism behind paper-trading optimism: adverse post-fill drift of ~half a tick cancels spread capture, and a third of resting orders never fill.*

**Also consulted and useful:** EverFunded options-backtesting guide — https://everfunded.com/blog/options-backtesting · OptionVisualizer backtesting and corporate-actions documentation — https://www.optionvisualizer.com/documentation/education/backtesting and https://www.optionvisualizer.com/documentation/education/corporate-actions · `purged-cross-validation` — https://github.com/eslazarev/purged-cross-validation · Bailey & López de Prado, Deflated Sharpe Ratio (SSRN 2460551) — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 · "Catching One in Five: LLM-as-Judge Blind Spots," arXiv 2606.10315 — https://arxiv.org/pdf/2606.10315 · Wataoka et al., "Self-Preference Bias in LLM-as-a-Judge," arXiv 2410.21819 — https://arxiv.org/pdf/2410.21819 · Filho et al., "Classifier Calibration" survey, arXiv 2112.10327 — https://arxiv.org/pdf/2112.10327 · OptionScanner POP methodology — https://optionscanner.ai/learn/probability-of-profit-methodology · Option Alpha "Moment in Time" — https://optionalpha.com/blog/moment-in-time-option-profit-probabilities · Mellers et al. on superforecasters — https://web.stanford.edu/~knutson/jdm/mellers15.pdf · solo pre-registration exemplars — https://github.com/pedramebd/systematic-trading-research , https://github.com/stanleys12/trading-bot · look-ahead-freedom formalisations — https://arxiv.org/pdf/2607.04958 , https://arxiv.org/pdf/2605.23959 , https://arxiv.org/pdf/2607.18867 · OTel GenAI semconv practitioner coverage — https://jacar.es/en/agent-observability-with-opentelemetry-genai-semconv-in-2026/ , https://dev.to/gabrielanhaia/opentelemetry-genai-semantic-conventions-your-llm-traces-should-look-like-this-in-2026-3ff6
