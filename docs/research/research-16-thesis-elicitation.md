# Research 16: Thesis Elicitation and Decision Hygiene

**Scope.** On-demand mode: the user brings their own thesis about an options contract, outside any scheduled event window, and the system evaluates it. The system has no independent directional view. Its honest contributions are cost analysis, probability honesty, sizing discipline, record-keeping and challenge. This strand covers **how to capture the thesis so it is scoreable, and how to avoid the capture process itself manufacturing the confidence it is meant to test.**

**Out of lane (other agent):** the design of the critic, adversarial challenge, "consider the opposite", devil's advocate / dialectical bootstrapping, LLM sycophancy. Noted as overlaps where relevant, not researched here.

**Date of research:** 12 November 2026. All effect sizes below are as reported by the cited source.

---

## PART 1 — FINDINGS

### 1. Elicitation formats that measurably improved calibration

---

**CLAIM:** A sub-one-hour probabilistic-reasoning training module improved forecast accuracy by 6–12% in standardised Brier score versus untrained controls, replicated across four independent tournament years.

**SOURCE:** Chang, W., Chen, E., Mellers, B., & Tetlock, P. — "Developing expert political judgment: The impact of training and practice on judgmental accuracy in geopolitical forecasting tournaments." *Judgment and Decision Making* 11(5), 2016, 509–526. https://www.sas.upenn.edu/~baron/journal/16/16511/jdm16511.pdf

**EVIDENCE STRENGTH:** Strong. Randomised assignment to training vs control, four replications.

Measured, mean standardised Brier (lower is better), trained vs control:

| Year | Trained n | Control n | Improvement | Test |
|---|---|---|---|---|
| 1 | 119 (prob) / 113 (scenario) | 152 | ~10% / ~11% | F(2,381)=12.1, p<.001 |
| 2 | 205 | 194 | ~12% | t(395)=5.95, p<.001 |
| 3 | 97 | 116 | ~6% | t(207)=2.32, p=.021 |
| 4 | 131 | 102 | ~7% | t(225)=2.20, p=.028 |

The authors describe these as likely lower bounds (training was brief; control forecasters were also self-selected and engaged).

**IMPLICATION FOR THE BUILD:** A one-hour training artifact is a legitimate, evidence-backed component — but the effect is ~6–12% on a Brier score, i.e. modest. It does not convert a non-predictor into a predictor. Given the project's own prior finding that direction prediction is worth ~7 bp/month gross, a 10% improvement on near-zero skill is still near-zero. **Do not position training as alpha.** The reason to build the elicitation structure is record-keeping and cost discipline, not calibration gains.

---

**CLAIM:** Within the training content, the single principle most strongly associated with accuracy was **comparison classes** (reference classes / base rates); the political-domain-knowledge principles were not associated with accuracy at all.

**SOURCE:** Chang et al. 2016, as above.

**EVIDENCE STRENGTH:** Moderate. This is a correlational analysis of self-reported rationales, not a randomised component dismantling. The authors explicitly caution that the principles were designed to work as a bundle.

- Comparison classes (C): ANOVA F=12.28, p<.001, positively associated with accuracy.
- Political "KNOW" principles: F=0.08, p=.78 — no association.
- Post-mortem (P) and other-perspectives (O) rationales were associated with **worse** scores. The authors partly attribute the P finding to post-mortems being written after inaccurate forecasts (reverse causation).

**IMPLICATION FOR THE BUILD:** Of all possible elicitation fields, the **reference class / base rate field has the best empirical warrant.** This is the one field to make mandatory and un-skippable. It also converges with Finding 8 (Flyvbjerg) and with the project's own unflattering known base rates.

Caution on the P finding: it is a warning against reading too much into a post-mortem field, not evidence that post-mortems hurt. But it does mean **do not score the user on the quality of their post-mortems.**

---

**CLAIM:** Forcing probability forecasts into coarser bins measurably degrades accuracy, and the degradation is severe for coarse verbal-style scales. Rounding to a 2-bin estimative-verb scale worsened Brier scores by 31% on average across all forecasters, and by 562% (mean) / 142% (median) for the best forecasters.

**SOURCE:** Friedman, J., Baker, J., Mellers, B., Tetlock, P., & Zeckhauser, R. — "The Value of Precision in Probability Assessment: Evidence from a Large-Scale Geopolitical Forecasting Tournament." *International Studies Quarterly* 62(2), 2018, 410–422. https://scholar.harvard.edu/sites/scholar.harvard.edu/files/rzeckhauser/files/value_of_precision.pdf

**EVIDENCE STRENGTH:** Strong. 888,328 forecasts, 1,832 individuals, 380 questions, 2011–2015. Post-hoc rounding of real forecasts, so it isolates the information lost by coarsening rather than confounding with elicitation mode.

| Rounding scheme | Mean Brier increase | Median |
|---|---|---|
| Words of estimative probability (2015 DNI version) | 0.7% | 0.9% |
| WEPs, 7 equal bins | 1.9% | 1.2% |
| Confidence levels, 3 bins | 11.8% | 7.3% |
| Estimative verbs, 2 bins | 31.4% | 22.1% |

Superforecasters at 3 bins: +236% mean. Untrained individuals at 2 bins: +15% mean — i.e. the better the forecaster, the more coarsening destroys.

**IMPLICATION FOR THE BUILD:** **Capture probability as a number, in fine increments (1% steps), never as a verbal label and never as a 3- or 5-point confidence picker.** A "low / medium / high conviction" selector is not a lossy convenience; it is the single most destructive elicitation choice available. If the UI offers a slider, the numeric value must be editable as text and must not snap to 5% or 10% increments. Note that this finding is about *information carried by the number*, so it applies even if the user's underlying skill is zero: coarse capture also destroys the ability to score them later.

---

**CLAIM:** Requiring a written justification of the judgment process did **not** improve accuracy and did not change the strategy people used; it only lowered their stated confidence.

**SOURCE:** Hoffmann, J. A., Gaissmaier, W., & von Helversen, B. — "Justifying the judgment process affects neither judgment accuracy nor strategy use." *Judgment and Decision Making* 12(6), 2017, 627–641. https://dlab.sauder.ubc.ca/sjdm/journal/17/17411/jdm17411.html

**EVIDENCE STRENGTH:** Moderate-to-strong for the null. Two experiments, n=144 and n=110, Bayesian analysis giving positive evidence *for* the null (BF 0.18 and 0.09 against an accuracy benefit), not merely a failure to reject.

Exp 2 test error: 6.2 RMSD with justification vs 5.8 control — directionally worse. Strategy shares were unchanged (BF=0.027 and 0.056 for a shift). Confidence was significantly lower on justification trials (BF=140.9 for the interaction in Exp 2).

**IMPLICATION FOR THE BUILD:** A free-text "why do you believe this?" box will not make the user's forecast better. It is still worth capturing — for the record, for later scoring, and because it reduces confidence — but **the system must not tell the user that writing a rationale improves their judgment.** This is a genuine disconfirming result against the most intuitively appealing elicitation field.

---

**CLAIM:** Decomposing a judgment into sub-estimates helps substantially when the target is highly uncertain and extreme in magnitude, and **hurts** when it is not. In the authors' own experiment, decomposition cut median error ~20-fold on extreme targets but increased median error by 458% on non-extreme targets.

**SOURCE:** MacGregor, D. G., & Armstrong, J. S. — "Judgmental Decomposition: When Does It Work?" *International Journal of Forecasting*, 1994. https://marketing.wharton.upenn.edu/wp-content/uploads/2022/02/140-JSA-Judgmental-Decomposition-When-Does-It-Work.pdf

**EVIDENCE STRENGTH:** Moderate. 280 subjects, 1,078 estimates, 10 problems, randomised to global vs decomposed, plus reanalysis of 15 problems from two earlier studies. Problems are general-knowledge quantity estimates, not financial forecasts — transfer to options is **assumed, not demonstrated.**

- Extreme/high-uncertainty targets: improved on 5 of 6; median error reduction ~19.8× (p<.001 one-tailed).
- Non-extreme targets: median error +458% (p<.05 two-tailed), worse on 3 of 4.
- Decomposition reduced overconfidence slightly: the gap between stated and actual probability of being within 10% of truth fell from 28.0 to 23.6 points — i.e. **it barely helped overconfidence and both conditions were grossly overconfident.**
- Authors' rule: only decompose when the components are genuinely easier to estimate than the target.

**CLAIM (counter):** The evidence that decomposing a *binary probability question* into a chain of conditional probabilities improves accuracy is essentially absent; the supporting literature is about time-series and causal-structure decomposition.

**SOURCE:** "The Evidence for Question Decomposition is Weak," LessWrong, reviewing Lawrence et al. (2006) *International Journal of Forecasting* 22(3) and Goodwin & Wright (1993). https://www.greaterwrong.com/posts/YjZ8sJmkGJQhNcjHj/the-evidence-for-question-decomposition-is-weak

**EVIDENCE STRENGTH:** Weak as evidence of a positive effect; the *absence* is reasonably well-established. Cited studies (Edmundson 1990; Webby, O'Connor & Edmundson 2005; Armstrong & Collopy 1993) report no effect sizes and concern series decomposition. Goodwin & Wright note decomposition can reduce accuracy when the sub-judgments are less familiar than the whole. A commenter raises the effort confound: decomposing makes people think longer, so apparent gains may be effort rather than structure.

**IMPLICATION FOR THE BUILD:** **Do not require a multiplicative probability chain** ("P(earnings beat) × P(stock moves >5% | beat) × P(it happens before expiry)"). There is no credible evidence this improves a binary probability and some evidence it makes it worse when sub-judgments are harder than the whole. What decomposition *is* legitimately for here is **separating the claims so each can be scored separately later** — direction, magnitude, timing, and realised-vs-implied volatility are four distinct falsifiable claims and a thesis that conflates them cannot be scored. Frame the decomposition as a record-keeping requirement, not a reasoning aid, and do not recombine the parts into a system-generated composite probability.

---

### 2. Anchoring and display order

---

**CLAIM:** Showing people a running consensus before eliciting their own estimate measurably reduced accuracy, by about 3 percentile points at the question level and up to ~7 points at the domain level; showing recent or high-confidence individual answers did not.

**SOURCE:** Simoiu, C., Sumanth, C., Mysore, A., & Goel, S. — "Studying the 'Wisdom of Crowds' at Scale." AAAI (HCOMP), 2019. https://5harad.com/papers/wisdom-of-crowds.pdf

**EVIDENCE STRENGTH:** Strong for the consensus effect. Randomised four-arm design at scale; accuracy measured as the crowd's percentile rank among individual responses.

Mean crowd percentile rank:

| Condition | Q-level open-ended | Q-level categorical | Domain open-ended | Domain categorical |
|---|---|---|---|---|
| Control (no social info) | 66 | 60 | 86 | 87 |
| Most recent 3 | 69 | 60 | 88 | 85 |
| Most confident 3 | 67 | 59 | 81 | 83 |
| **Consensus (running median)** | **63** | **57** | **81** | **80** |

Crowds that began inaccurate did not recover under the consensus condition but did recover in the other two social conditions. The authors attribute the penalty to anchoring on the displayed consensus.

**IMPLICATION FOR THE BUILD:** This is the strongest direct evidence for the display-order rule. A market-implied probability is exactly a consensus summary statistic. **Do not display implied probability, implied move, IV rank, or any aggregate before the user's probability is committed.** The pattern that inaccurate starters never recover under consensus display is the mechanism by which the tool would launder priors: a user who sees 30% and then "decides" 32% has recorded nothing, and the system then has no independent datum to challenge.

---

**CLAIM:** Giving people others' estimates sharply reduced the diversity of estimates and significantly **increased confidence**, while collective accuracy did not improve.

**SOURCE:** Lorenz, J., Rauhut, H., Schweitzer, F., & Helbing, D. — "How social influence can undermine the wisdom of crowd effect." *PNAS* 108(22), 2011, 9020–9025. https://pmc.ncbi.nlm.nih.gov/articles/PMC3107299

**EVIDENCE STRENGTH:** Strong. 144 subjects, 12 sessions, six factual estimation questions, five rounds each, three randomised information conditions, accuracy-incentivised payments (CHF 1.40 / 0.70 / 0.35 for within 10/20/40%).

- Diversity: strongly reduced under both social conditions; control showed almost no change.
- The range-reduction (wisdom-of-crowd) indicator fell ~1 unit under social influence, significant for all questions, larger in the *aggregated-mean* condition than the full-information condition.
- Collective error: changed little, declined only marginally — not a meaningful accuracy gain.
- **Confidence rose significantly in both information conditions versus control, with no accuracy improvement.**

**IMPLICATION FOR THE BUILD:** This is the exact failure mode named in the brief, measured. Showing the user the market's number before capture produces **more confidence without more accuracy** — manufactured false confidence, which is the thing the product is supposed to prevent. Note also that the *aggregated mean* was worse than *full information*: a single summary number anchors harder than a distribution. If anything must be shown pre-capture, a distribution or a range anchors less than a point estimate — but the safe rule is to show nothing.

---

**CLAIM:** Anchoring on an irrelevant number is robust to warnings, to incentives for accuracy, and to extreme anchor values; it is strongest when the anchor is on the same response scale and dimension as the target, and weaker when the formats differ.

**SOURCE:** Chapman, G. B., & Johnson, E. J. — "Incorporating the Irrelevant: Anchors in Judgments of Belief and Value," in Gilovich, Griffin & Kahneman (eds.), *Heuristics and Biases*, Cambridge University Press, 2002. https://core.ac.uk/download/357527311.pdf

**EVIDENCE STRENGTH:** Moderate (narrative review of experimental literature, not a single measured study). Illustrative: Kahneman & Knetsch (1993) found mean estimates of $14 under a low anchor vs $36 under a high anchor when the response was a dollar amount, but 24% vs 29% — no reliable effect — when the response was a percentage.

Two mitigations with cited support: prompting the respondent to generate reasons *against* the anchor reduced anchoring; presenting another person's thoughts also reduced it.

**IMPLICATION FOR THE BUILD:** Three concrete rules follow.
1. **Scale matching is the danger condition.** Showing a market-implied *probability* (a percentage) immediately before asking for the user's *probability* (a percentage) is the maximum-anchoring configuration. Showing an option *price* before asking for a probability is a format mismatch and anchors less — but it is still a same-dimension number for the sizing question, so it must be withheld before the sizing step.
2. **Warning the user does not work.** A banner saying "don't let the market price anchor you" has no support here. Sequence the form; don't caption it.
3. The "generate reasons against" mitigation is the other agent's territory (the critic), but it is *also* the mechanism by which the pre-mortem field earns its place — see Finding 6.

---

**CLAIM:** Anchoring and carryover from earlier questions persists in subjective-probability elicitation even with careful questionnaire design, and the amount of bias depends on question order and on whether questions appear on the same or separate screens.

**SOURCE:** Prava, V. R., Clemen, R. T., Hobbs, B. F., & Kenney, M. A. — "Partition Dependence and Carryover Biases in Subjective Probability Assessment Surveys for Continuous Variables: Model-Based Estimation and Correction." *Decision Analysis* 13(1), 2016, 51–67. DOI 10.1287/deca.2015.0323

**EVIDENCE STRENGTH:** Moderate. Model-based estimation applied to two expert-elicitation datasets; the specific magnitudes are in the full text, which I did not obtain. The qualitative findings (order matters; same-screen vs separate-screen matters; anchoring survives careful design) are stated in the abstract.

**IMPLICATION FOR THE BUILD:** **One question per screen.** Do not render the thesis form as a single long page: a later field's answer is contaminated by a visible earlier field, and by any number visible anywhere on the page. This also means the committed probability should be hidden (or at least not re-rendered) once the user moves on to the magnitude and timing fields, and the user's own earlier numeric answers carry over as anchors just as the market's do.

**CLAIM (partition dependence, same literature):** Carving the outcome space into buckets biases the elicited probabilities toward uniformity across whatever buckets are offered.

**EVIDENCE STRENGTH:** Moderate for the general phenomenon; I did not obtain a measured magnitude in this pass.

**IMPLICATION FOR THE BUILD:** Do not offer the user a pre-built menu of strike buckets or outcome ranges and ask them to distribute probability across it. The chosen partition will shape the answer. Ask for a threshold the user names themselves ("what price, by what date") and then a single probability.

---

**CLAIM:** Anchoring in financial forecasting is documented but the directly relevant experimental literature on whether showing current price anchors a forecaster is thinner than the general anchoring literature.

**SOURCE:** Representative: Kudryavtsev & Cohen, and the analyst-anchoring literature (e.g. "Anchoring effect and long-horizon analysts' forecast errors," *Cogent Economics & Finance*, 2025, https://www.tandfonline.com/doi/full/10.1080/23322039.2025.2598189). The most-cited controlled experiment, Ceschi/Costantini-style "Can anchoring explain biased forecasts? Experimental evidence" (*Journal of Behavioral and Experimental Finance*, 2016), was not retrievable in this pass.

**EVIDENCE STRENGTH:** Weak-to-moderate. Archival analyst studies are observational and cannot separate anchoring from rational information use. **I found no single clean experiment showing that displaying the current underlying price before eliciting a price forecast shifts the forecast by a measured amount.**

**IMPLICATION FOR THE BUILD:** The display-order rules in this brief rest on the *consensus-display* evidence (Simoiu; Lorenz) and the *general* anchoring evidence (Chapman & Johnson), not on a financial-forecasting-specific experiment. Record that honestly. The practical consequence is unchanged — hiding the market's number before capture is cheap and the downside is nil — but do not claim a finance-specific effect size.

---

### 3. Pre-mortem and prospective hindsight

---

**CLAIM:** A pre-mortem reduced participants' confidence in a plan significantly more than a "pro-mortem" (imagining success) or a filler control, with a large effect size (d=0.81).

**SOURCE:** Keysor, E., Wojtyna, A., & Veinott, E. S. — "Premortem: Evaluating two structured analytic techniques for group brainstorming," Michigan Technological University, poster, Society for Judgment and Decision Making (2020). https://dlab.sauder.ubc.ca/sjdm/presentations/2020-Poster-Elizabeth-premortem-confidence-brainstorming.pdf

**EVIDENCE STRENGTH:** Moderate. Experiment 1: n=53, three randomised conditions, pre/post confidence and understanding on 0–100 scales. F(2,51)=4.02, p=.024, **d=.81** for confidence reduction. Understanding showed the same pattern but only marginally: F(2,51)=2.8, p=.077. Experiment 2 (n=43): no difference between individual and group pre-mortems (F(1,42)=0.85, p=.772). Conference poster, small samples, student subjects, hypothetical plans.

**IMPLICATION FOR THE BUILD:** This is the best measured number available for the pre-mortem, and note carefully **what it measures: confidence reduction, not failure-mode discovery, not decision quality.** For this product that is arguably the right outcome — the central risk is manufactured confidence, and a pre-mortem demonstrably reduces confidence. It is *not* evidence that the user will identify the failure mode that actually kills the trade. The Experiment 2 null is also useful: a single-user tool loses nothing by not having a group.

---

**CLAIM:** In three controlled studies, the pre-mortem's advantage over comparison techniques was partial and inconsistent — it reduced fixation and errors in a field setting and produced more reasons in one lab study, but produced no more reasons or solutions than a worst-case-scenario method in another.

**SOURCE:** Peabody, M. — "Improving Planning: Quantitative Evaluation of the Premortem Technique in Field and Laboratory Settings." MSc thesis, Michigan Technological University, 2017. https://digitalcommons.mtu.edu/etdr/374

**EVIDENCE STRENGTH:** Moderate for the mixed result; the thesis abstract reports no effect sizes, test statistics or p-values.

- Exp 1 (field): 52 Army cadets in teams, six time-constrained planning exercises, pre-mortem vs standard military plan evaluation. Fewer "fouls," less fixation, no increase in planning time.
- Exp 2: 72 participants, pre-mortem vs worst-case-scenario method. **No significant difference in number of reasons or solutions generated.** The *distribution* of reasons across categories differed significantly.
- Exp 3: 82 participants. Pre-mortem generated more reasons than worst-case scenario; groups more solutions than individuals.

**IMPLICATION FOR THE BUILD:** The pre-mortem's measured advantage is over *doing nothing*, not over any other structured prompt. A plain "what would make this wrong?" prompt may do nearly as well. Choose the pre-mortem framing because it is cheap and the confidence-reduction result (Finding above) is the one you want, **not** because it is uniquely good at finding failure modes — Exp 2 says it is not. The consistent finding across all three studies is that the pre-mortem changes *which categories* of failure people think about, which is a real benefit for a form that then stores those categories as structured fields.

---

**CLAIM (unverified):** The foundational prospective-hindsight result — that framing an outcome as already having happened produces ~30% more reasons than framing it as something that might happen — is widely cited but I could not verify the primary figure.

**SOURCE:** Mitchell, D. J., Russo, J. E., & Pennington, N. — "Back to the future: Temporal perspective in the explanation of events." *Journal of Behavioral Decision Making* 2(1), 1989, 25–38. DOI 10.1002/bdm.3960020103

**EVIDENCE STRENGTH:** No credible verification obtained in this pass. The citation is real and the paper exists; the "30%" figure circulates widely in secondary sources (including Klein's own writing) but I could not reach the primary text or a quantitative secondary report of it. **Treat the 30% number as unconfirmed.**

**IMPLICATION FOR THE BUILD:** Use the "it is three weeks from now and this trade lost money; write down why" framing — the mechanism is plausible and the framing costs nothing — but do not cite 30% in any user-facing copy or internal justification until verified.

---

### 4. Reference-class forecasting and base rates

---

**CLAIM:** Reference-class forecasting — replacing a bottom-up estimate with the distribution of outcomes from a class of comparable past cases — was adopted as official practice by the UK Department for Transport and the Treasury's Green Book after Flyvbjerg's work on systematic optimism bias in project forecasts.

**SOURCE:** Flyvbjerg, B. — "From Nobel Prize to Project Management: Getting Risks Right," *Project Management Journal* 37(3), 2006; and "Policy and Planning for Large Infrastructure Projects: Problems, Causes, Cures," https://arxiv.org/pdf/1303.7400

**EVIDENCE STRENGTH:** Moderate. The descriptive evidence of forecast bias is strong and large-sample (cost overruns in hundreds of projects). The evidence that *applying* reference-class forecasting improved subsequent outcomes is weaker — it is largely before/after and advocacy-adjacent, and the method has been criticised as hard to apply when the reference class is ill-defined (see e.g. the APM webinar framed as "useful method or random number generator?" https://www.slideshare.net/APMDonotuse/reference-class-forecasting-useful-method-or-random-number-generator-webinar).

**IMPLICATION FOR THE BUILD:** Reference-class forecasting is unusually well-suited to this product because the hard part — defining the reference class and obtaining its distribution — is *already solved*. The project's prior research supplies the classes and their outcomes (retail option purchases averaging −3.95% per trade; a 3%-OTM weekly call averaging −59% over an 8-day hold). The system can therefore do the thing Flyvbjerg's method needs and that users cannot do for themselves: match the proposed trade to a reference class and show its empirical distribution. Converges with the Chang et al. finding that comparison classes were the single most accuracy-associated principle.

---

**CLAIM:** Showing a base rate does not reliably change behaviour. The best-evidenced disclosure-style interventions in retail finance explain almost no variance in subsequent behaviour, and effects decay to negligible within about 20 months.

**SOURCE:** Fernandes, D., Lynch, J. G., & Netemeyer, R. G. — "Financial Literacy, Financial Education, and Downstream Financial Behaviors." *Management Science* 60(8), 2014, 1861–1883. https://papers.ssrn.com/abstract=2333898

**EVIDENCE STRENGTH:** Strong. Meta-analysis of 168 papers reporting 201 prior studies.

- Financial education interventions explained **0.1% of the variance** in the financial behaviours studied.
- Effects were weaker in low-income samples.
- Even interventions with many hours of instruction had **negligible effects on behaviour 20 months or more** later.

**IMPLICATION FOR THE BUILD:** This is the single most important disconfirming finding in this brief. **A base-rate display is informational, and information does not change retail financial behaviour.** The base rate must therefore not be the mechanism relied on. It must be (a) captured as a required acknowledgement so it is in the record, and (b) backed by a *structural* mechanism — see Findings 14–15 on choice architecture and automated limits — that acts on the trade whether or not the user's beliefs changed.

---

**CLAIM:** Regulator-mandated standardised risk warnings for leveraged retail products were introduced on the basis that the loss base rate is severe, but I found no credible evidence that the warning itself changed retail behaviour.

**SOURCE:** ESMA product intervention notices (ESMA35-43-1135, ESMA35-43-1912); FCA PS19/18, https://www.fca.org.uk/publication/policy/ps19-18.pdf. FCA Occasional Paper 66, "Digital engagement practices and investment outcomes," April 2025, https://www.fca.org.uk/publication/occasional-papers/op66-digital-engagement-practices-investment-outcomes.pdf

**EVIDENCE STRENGTH:** No credible evidence found for an effect of the warning. OP66 contains no RCT of risk warnings or loss-statistic displays and reports no effect sizes for them. Its own main analysis is observational, and it notes that as of December 2022 none of the firms studied had tested the causal impact of their engagement practices on outcomes.

What OP66 *does* report, as cited evidence, runs the other way: Gathergood et al. (2024), an online experiment with ~9,000 consumers, found push notifications and points/prize-draw mechanics **increased** trade frequency and riskiness, with leaderboards and flashing prices increasing frequency more among the less financially literate. Hayes et al. (2022), a survey of ~3,000 trading-app users across five firms, found 3.75% met at-risk-of-problem-gambling criteria.

**IMPLICATION FOR THE BUILD:** Two things. First, the asymmetry is instructive: the measured effects in retail trading UX are from *engagement* features that increase trading, not from *warning* features that reduce it. A tool that simply refrains from gamification may do more good than one that adds warnings. Second, since the warning literature is empty, a base-rate display should be justified as **record-keeping and friction**, not as persuasion. OP66 does cite friction (Farghly et al. 2022; Gilchrist et al. 2022) as beneficial before high-risk investments, though without effect sizes — weak support, reported as weak.

---

### 5. Falsifier pre-registration and pre-commitment

---

**CLAIM:** Pre-registration substantially changes what gets reported: 96% of hypotheses were supported in the standard psychology literature versus 44% in published Registered Reports.

**SOURCE:** Scheel, A. M., Schijen, M. R. M. J., & Lakens, D. — "An Excess of Positive Results: Comparing the Standard Psychology Literature With Registered Reports." *Advances in Methods and Practices in Psychological Science*, 2021 (preprint 2020). https://psyarxiv.com/p6e9c/ — DOI 10.1177/25152459211007467

**EVIDENCE STRENGTH:** Strong for the comparison. N=152 standard hypothesis-testing studies vs N=71 published Registered Reports (as of November 2018). Excluding direct replications: 96% vs 50%. It is an observational comparison of literatures, not a randomised trial of pre-registration, so selection into Registered Reports is a confound the authors acknowledge.

**IMPLICATION FOR THE BUILD:** The analogy to a trading journal is direct and this is the sharpest argument for the design. A trading record written *after* the outcome is the 96% literature: the thesis is reconstructed to fit what happened, and the user learns nothing. A thesis committed *before* entry, with its falsifier, is the 44% literature. **This is the strongest single justification for making the record immutable and timestamped at entry, with amendments appended rather than overwritten.** The honest contribution of the tool is converting the user's own history from the first regime to the second.

---

**CLAIM:** If-then plans ("implementation intentions") that specify in advance what will trigger an action have a medium-to-large effect on goal attainment, d=0.65 across 94 studies and over 8,000 participants, over and above goal intentions alone.

**SOURCE:** Gollwitzer, P. M., & Sheeran, P. — "Implementation intentions and goal achievement: A meta-analysis of effects and processes." *Advances in Experimental Social Psychology* 38, 2006, 69–119. Summarised with the failure conditions in Gollwitzer & Oettingen, "Planning and Goal Striving," https://www.socmot.uni-konstanz.de/sites/default/files/Gollwitzer_Oettingen_11_Planning_Goal_Striving.pdf

**EVIDENCE STRENGTH:** Strong for the main effect. Mostly health and academic behaviours; **transfer to trading exits is assumed, not demonstrated.** The meta-analysis is also old enough to predate current publication-bias correction norms.

Documented failure conditions, all directly relevant:
- Weak commitment to the superordinate goal, or the goal not being active at the moment of the trigger.
- Doubt about the plan: participants primed as "flexible" showed weaker effects than those primed as plan-stickers.
- Strong competing habits can outrun a weak plan.
- Low self-efficacy weakens the effect.
- A then-part phrased as the *negation* of the habitual behaviour may backfire by strengthening the habit (the authors flag this without systematic evidence).
- **On disengagement specifically:** Henderson et al. (2007) found implementation intentions can reduce escalation of commitment to failing courses of action, with the if-part specifying receipt of negative feedback and the then-part specifying a switch to an available alternative.

**IMPLICATION FOR THE BUILD:** The falsifier field should be written as an **if-then plan with an observable trigger and a specific action**, not as a description. "If IV drops below 28 or the stock closes below 142, I sell" is an implementation intention. "I'll get out if the thesis breaks" is not, and has no support. The negation warning is actionable: phrase the then-part as "I close the position," not "I do not hold on."

---

**CLAIM:** Voluntary commitment devices work for the minority who adopt them and are declined by the large majority. A smoking-cessation commitment contract raised quit rates by 3.3–5.8 percentage points against a base of 8.9–14.7% (>35% relative), but only ~11% of those offered signed up, and ~66% of signers still failed.

**SOURCE:** Giné, X., Karlan, D., & Zinman, J. — "Put Your Money Where Your Butt Is: A Commitment Contract for Smoking Cessation." *American Economic Journal: Applied Economics* 2(4), 2010, 213–235. https://www.povertyactionlab.org/evaluation/cares-commitment-savings-smoking-cessation-philippines

**EVIDENCE STRENGTH:** Strong. RCT, 2,000 smokers, biochemically verified outcomes (urine nicotine test) at 6 and 12 months.

**IMPLICATION FOR THE BUILD:** Pre-commitment is real but **take-up is the binding constraint, not efficacy.** An optional falsifier field will be left blank by most users most of the time; the 11% take-up figure is the realistic prior. Therefore the falsifier must be a **required field that blocks the record from being saved**, not an invitation. And since a third of adopters succeeded, the system should expect its own exit plans to be broken routinely and should record breaks rather than assume compliance.

---

### 6. Scoring one person's forecasts at small N

---

**CLAIM:** At the sample sizes this project will reach, a single user's Brier score is dominated by sampling noise, and per-bucket calibration is uninterpretable.

**SOURCE:** Own computation (binomial Wilson intervals; Monte Carlo of per-item Brier variance for a calibrated forecaster with probabilities drawn uniform(0.05, 0.95), 4,000 replications per n). Method standard; the arithmetic is mine and reproducible.

**EVIDENCE STRENGTH:** Strong (it is arithmetic, not an empirical claim).

95% CI on the realised frequency in a calibration bucket where the user stated 70%:

| n in bucket | 95% CI | half-width |
|---|---|---|
| 10 | [0.40, 0.89] | ±24.8 pp |
| 20 | [0.48, 0.86] | ±18.7 pp |
| 30 | [0.52, 0.83] | ±15.6 pp |
| 50 | [0.56, 0.81] | ±12.3 pp |
| 100 | [0.60, 0.78] | ±8.8 pp |
| 200 | [0.63, 0.76] | ±6.3 pp |

95% CI width on the *overall* Brier score for a perfectly calibrated forecaster:

| n (total forecasts) | mean Brier | SE | 95% CI width |
|---|---|---|---|
| 25 | 0.182 | 0.039 | 0.153 |
| 50 | 0.183 | 0.028 | 0.109 |
| 100 | 0.182 | 0.020 | 0.077 |
| 200 | 0.182 | 0.014 | 0.055 |

For context: the entire *trained-vs-untrained* difference in the Good Judgment Project was 6–12% of a Brier score — on a base around 0.18 that is roughly 0.011 to 0.022. At n=100 the 95% CI on a single person's Brier score is ±0.038, i.e. **two to four times wider than the whole effect of the best-evidenced forecasting training in existence.**

**IMPLICATION FOR THE BUILD:** See SMALL-N VERDICT below.

---

**CLAIM:** The standard Brier decomposition into reliability, resolution and uncertainty is biased at small samples: it overestimates reliability, underestimates uncertainty, and may bias resolution in either direction. A fully unbiased decomposition is unattainable.

**SOURCE:** Ferro, C. A. T., & Fricker, T. E. — "A bias-corrected decomposition of the Brier score." *Quarterly Journal of the Royal Meteorological Society*, 2012. https://ore.exeter.ac.uk/repository/handle/10871/8503

**EVIDENCE STRENGTH:** Moderate for the claim as stated (from the abstract); I did not obtain the magnitude formulas as a function of n and bin count.

**IMPLICATION FOR THE BUILD:** Do not display a calibration/resolution/uncertainty breakdown. The bias runs in the flattering direction — it **overestimates reliability**, i.e. it will make the user look better calibrated than they are, at exactly the sample sizes this project will have. If a decomposition is ever shown, it must use a bias-corrected estimator and still carry an interval.

---

**CLAIM:** Spiegelhalter's Z is a binning-free test of calibration whose normal approximation is verified at n=1,000 but not at smaller n.

**SOURCE:** Spiegelhalter, D. J. (1986), *Statistics in Medicine* 5(5), 421–433, as implemented and documented in the `calzone` package: https://calzone-docs.readthedocs.io/en/stable/notebooks/spiegelhalter_z.html

Z = Σ(xᵢ − pᵢ)(1 − 2pᵢ) / Σ(1 − 2pᵢ)²pᵢ(1 − pᵢ), approximately standard normal under the null of calibration. The documentation reports empirical size 0.049 at α=0.05 with n=1,000 over 10,000 simulations, is explicit that small-sample behaviour is untested there, and notes the test is weak against prevalence shift.

**EVIDENCE STRENGTH:** Moderate. The test is well-established; its small-n properties are not documented in the source I obtained.

**IMPLICATION FOR THE BUILD:** If a calibration statistic is computed at all, Spiegelhalter's Z is the right choice because it needs no binning (binning is what destroys small samples — see the Open Phil bucket counts below). But its p-value should be treated as indicative only below a few hundred observations, and the test is weakest against exactly the failure mode a bullish options trader would have: a systematic shift in base rate.

---

**CLAIM:** A well-resourced organisation with 743 resolved predictions treated its own calibration conclusions as exploratory, and its most interesting finding rested on 8 observations.

**SOURCE:** Open Philanthropy — "How accurate are our predictions?" (2022). https://www.openphilanthropy.org/research/how-accurate-are-our-predictions

**EVIDENCE STRENGTH:** Strong as an illustration. 2,850 predictions made, 743 resolved and scored (382 true / 361 false). Bucket-level uncertainty shown with 90% credible intervals from Beta(T+1, F+1). Every bucket had ≥40 resolved predictions except 90–100%, which had 8. The claimed overconfidence at 90%+ rests on those 8. The 70–80% finding is described only as "possibly" miscalibration. They note calibration varies greatly across individual predictors, so personal conclusions need each forecaster's own curve.

**IMPLICATION FOR THE BUILD:** This is the realistic ceiling comparison. At 743 resolved forecasts — far beyond what this project will reach — the sophisticated conclusion was still "exploratory," and the most-confident bucket was unusable. A user with 60 resolved theses should be shown counts and intervals, never a verdict.

---

### 7. Disposition effect and exit discipline

---

**CLAIM:** Automated stop-loss and take-gain orders eliminated and reversed the disposition effect in a controlled experiment (DE fell from +0.082 to −0.106, about a 0.19 reduction); **a reminder-only version of the same device had no significant effect** (−0.040, ns).

**SOURCE:** Fischbacher, U., Hoffmann, G., & Schudy, S. — "The Causal Effect of Stop-Loss and Take-Gain Orders on the Disposition Effect." *Review of Financial Studies* 30(6), 2017, 2110–2129. Working paper: https://www.twi-kreuzlingen.ch/wp-content/uploads/2017/12/twi-rps-089-fischbacher-hoffmann-schudy.pdf

**EVIDENCE STRENGTH:** Strong design, modest power. Lab trading experiment, University of Konstanz 2015, six assets, 34 rounds, three between-subjects treatments (No limit / Limit / Reminder), with Limit and No-limit subjects facing identical random price paths. 72 participants, 22 per treatment with computable DE; 24 independent price developments in the regressions.

| Measure | No limit | Limit | Reminder |
|---|---|---|---|
| Disposition effect | 0.082 | **−0.106** | 0.088 |
| Proportion of losses realized | 0.059 | **0.252** | 0.050 |
| Proportion of gains realized | 0.141 | 0.146 | 0.138 |

- Limit vs No-limit: KS p=0.002, Wilcoxon p=0.008. Regression coefficient −0.221*** (no controls), −0.224* (full controls).
- Mechanism: the entire effect runs through realizing losses (PLR +0.19, coefficient 0.185***). Gains realization unchanged.
- Take-up: of 22 Limit subjects, 13 set both limits, 2 set only an upper limit, 0 set only a lower limit, **7 set none.**
- Both-limit setters: DE = −0.124 vs 0.082 control, p=0.036. No-limit setters within the Limit treatment: DE = −0.078, p=0.218 (not different from control).

**IMPLICATION FOR THE BUILD:** This is the most directly actionable finding in the brief, and it is bad news for the tool's natural design. **The device that worked was automatic execution. The device that only reminded the investor did nothing.** A personal research tool cannot execute. Therefore the honest framing is: the tool's falsifier field is a *reminder-class* intervention, and the measured effect of reminder-class interventions on the disposition effect is zero. If exit discipline is actually a goal, the falsifier must be converted into a **resting order placed at the broker at the time of entry** — the tool's output should be an order ticket, not a note. Record whether the user placed it. Note also 7 of 22 set no limits even when offered: voluntary is not enough.

---

**CLAIM:** In brokerage data on 4,328 investors and 65,096 round trips, stop-loss users showed a smaller disposition effect overall — but when their stop-loss-closed trades were excluded, they were *more* reluctant to sell losses than non-users.

**SOURCE:** Richards, D. W., Rutterford, J., Kodwani, D., & Fenton-O'Creevy, M. — "Stock market investors' use of stop losses and the disposition effect." *European Journal of Finance* 23(2), 2017, 130–152. https://core.ac.uk/download/82981049.pdf

**EVIDENCE STRENGTH:** Strong data, observational design. UK online/telephone brokerage, July 2006 – December 2009, 169,608 trades in UK stocks. Survival analysis with hazard ratios.

- Investor level: HR for selling at a gain 0.7443 (−25.6%); HR for selling at a loss 1.1427 (+14.3%).
- Stop-loss-closed trades specifically: losses HR 1.1854, gains HR 0.9246 — bias reversed.
- **Stop-loss users' other (non-stop-loss) trades:** losses HR 0.9555 (p<.05) — *more* reluctant to sell losers; gains HR 0.8419. The authors call this only partial support for their hypothesis.
- The paper does not test the effect of stop-loss use on returns.

**IMPLICATION FOR THE BUILD:** Converges exactly with Fischbacher: **the mechanism does the work, not the person.** Being the kind of investor who uses stop-losses did not confer discipline on trades without one — if anything the opposite. So per-trade coverage matters: a thesis record with a falsifier and no resting order is a trade in the undisciplined bucket, even for a user who "uses stops." The tool should track the *rate* of trades entered with a live resting order, as a per-trade compliance statistic, rather than treating discipline as a user attribute.

---

### 8. Does any of this transfer? (see also DISCONFIRMING EVIDENCE)

---

**CLAIM:** The bias-mitigation evidence base is predominantly laboratory-based for training-type interventions and predominantly field-based for structural (choice-architecture) interventions, with no head-to-head comparison and almost no evidence on durability in organizations.

**SOURCE:** Fasolo, B., Heard, C., & Scopelliti, I. — "Mitigating Cognitive Bias to Improve Organizational Decisions: An Integrative Review, Framework, and Research Agenda." *Journal of Management* 51(6), 2025, 2182–2211. https://openaccess.city.ac.uk/id/eprint/33831/

**EVIDENCE STRENGTH:** Strong as a characterisation of the literature. 100 experimental studies from 62 articles, 1986–2022: 32 debiasing, 62 choice architecture, 6 dual.

- Setting: 50% lab, 29% field, 21% online. **Debiasing: 23 of 32 studies were lab-based.** Choice architecture: 22 of 62 were field studies.
- Mean sample size: debiasing 232; choice architecture 2,254.
- Only 2 studies targeted group decisions.
- **No study compared debiasing against choice architecture head to head.**
- Durability: limited evidence. Morewedge et al. (2015) up to three months. **No choice-architecture study examined persistence in organizations.**
- Transfer: debiasing training in thinking strategies showed some cross-domain transfer; choice-architecture effects are highly context-specific with low spillover.
- The review excludes accountability-type motivational strategies and excludes decision-support systems — i.e. it excludes the category this product falls into.

**IMPLICATION FOR THE BUILD:** Two conclusions. (1) **Favour structure over instruction.** The field evidence, the large samples, and the real-decision settings are all on the choice-architecture side; the training side is lab students. A required form with blocking fields and a fixed sequence is choice architecture. A tutorial is training. (2) The review explicitly excludes decision-support software, so **there is no review-level evidence that a tool like this one works.** Build it, but do not claim the literature supports it; the literature supports the ingredients, in other settings.

---

**CLAIM:** A single training intervention reduced measured bias by ~19% (video) to ~32% (interactive game) immediately, with ~19–24% retained at a follow-up of at least two months.

**SOURCE:** Morewedge, C. K., Yoon, H., Scopelliti, I., Symborski, C. W., Korris, J. H., & Kassam, K. S. — "Debiasing Decisions: Improved Decision Making With A Single Training Intervention." *Policy Insights from the Behavioral and Brain Sciences* 2(1), 2015, 129–140. DOI 10.1177/2372732215600886. https://openaccess.city.ac.uk/id/eprint/12324

**EVIDENCE STRENGTH:** Moderate. Two experiments; targeted biases were bias blind spot, confirmation bias and fundamental attribution error (Exp 1), and **anchoring**, representativeness and social projection (Exp 2). Outcomes were measured on bias-elicitation test instruments, not real decisions. Sample sizes not stated on the record I obtained.

| Intervention | Immediate | ≥2-month follow-up |
|---|---|---|
| Interactive game | ≥ −31.94% | ≥ −23.57% |
| Video | ≥ −18.60% | ≥ −19.20% |

**IMPLICATION FOR THE BUILD:** This is the best pro-debiasing evidence and it includes anchoring specifically, which matters for the display-order rules — it suggests anchoring is partially trainable. But the outcome is performance on bias tests, so **transfer to a real options decision with real money is assumed, not demonstrated.** Do not let this finding substitute for the structural rules.

---

## PART 2 — MANDATORY SECTIONS

### ELICITATION PROTOCOL

Design constraints this sequence is built from:
- One question per screen (Prava et al.: same-screen vs separate-screen changes bias magnitude; earlier answers carry over as anchors).
- No consensus or market statistic visible before the user's probability is committed (Simoiu et al.: −3 to −7 percentile points; Lorenz et al.: confidence up, accuracy flat).
- Probability captured as a fine-grained number, never a verbal band (Friedman et al.: +31% Brier at 2 bins, +562% for good forecasters).
- Reference class presented, because it is the most accuracy-associated principle (Chang et al., F=12.28) — but *after* capture, and not relied on to change behaviour (Fernandes et al.: 0.1% of variance).
- Falsifier as a required if-then plan with an observable trigger (Gollwitzer & Sheeran d=0.65; failure modes noted).
- Commitment before outcome, immutably (Scheel et al.: 96% vs 44%).

---

**STEP 0 — Contract identification.**
*Ask:* underlying, expiry, strike, side (long/short), structure (single leg / spread).
*UI may display:* the contract's static identifiers only — ticker, expiry date, strike, multiplier, exercise style, whether the expiry straddles a known earnings date (a calendar fact, not a forecast).
*UI may NOT display:* premium, bid/ask, mid, last, IV, IV rank, delta, implied move, probability of touch, probability ITM, open interest, volume, the underlying's current price, any chart, any analyst target, any news feed.

Rationale: the underlying price is the same-dimension anchor for Step 2 and the premium is the same-dimension anchor for Step 5. Chapman & Johnson: same-scale, same-dimension anchors are the strongest, and warnings do not neutralise them.

Implementation note: contract selection normally *requires* seeing a price. Resolve this by letting the user paste or type the contract identifier, or by showing a strike ladder with strikes and expiries but all price, greek and volume columns blanked until Step 4 is complete.

---

**STEP 1 — Free-text thesis, before any structure.**
*Ask:* in your own words, what do you expect to happen and why? (required, min ~120 characters)
*UI may display:* nothing new.
*Rationale:* captured first so it is uncontaminated by the structured fields that follow. Hoffmann et al. is explicit that this does **not** improve the forecast — so the UI must not claim it does. Its value is the record and a measured reduction in stated confidence.

---

**STEP 2 — The falsifiable claim, decomposed into separately scoreable parts.**
One screen each:

2a. *Direction:* does the underlying go up or down? (binary)
2b. *Threshold:* what price must it reach or exceed? (free numeric — **do not** offer a menu of strike-derived buckets; partition dependence)
2c. *Deadline:* by what date? (free date, defaulting to nothing)
2d. *Volatility claim:* do you expect realised volatility over the holding period to be higher or lower than what is currently priced? (three options: higher / lower / no view — "no view" must be available and must not be penalised)

*UI may display:* nothing new. In particular 2b must be asked with no strike ladder, no current price and no standard-deviation cone visible.
*Rationale:* four claims, four separate later resolutions. A thesis that conflates them cannot be scored, and the scoring is the product. This is decomposition as a record-keeping requirement, which is the only use MacGregor & Armstrong's evidence supports; **the system must not multiply these into a composite probability** (no credible evidence that a conditional-probability chain beats a holistic binary estimate, and some evidence it is worse).

---

**STEP 3 — Probability, as a number.**
*Ask:* what is the probability that the claim in Step 2 (direction AND threshold BY deadline) is true? Enter a whole-number percentage.
*UI constraints:* free numeric text input, 1–99, 1% increments. If a slider is offered it must be accompanied by the editable number and must not snap to 5s or 10s. **No verbal labels anywhere on this screen** — no "unlikely/likely," no "low/medium/high conviction," no 1–5 stars, no emoji scale.
*UI may NOT display:* implied probability, probability ITM, delta, breakeven, the market's implied move, or the user's own answer to any prior step re-rendered on this screen.
*Rationale:* Friedman et al. — coarsening costs 12% of Brier at 3 bins and 31% at 2 bins, and is worst for the most informative forecasters. This is also the measurement that everything downstream is scored against; coarse capture permanently destroys the record.

---

**STEP 4 — COMMIT. Write the record. Timestamp it. Make it immutable.**

Nothing after this point can alter Steps 0–3. Later changes are appended as amendments with their own timestamps, never overwrites. This is the pre-registration boundary (Scheel et al.) and it is the single most important line in the protocol: everything before it is the user's own view, everything after it is informed by the market and by the system.

---

**STEP 5 — Reveal. Now show everything.**

*UI now displays, in this order:*
1. **The market's implied probability** for the user's exact claim, and the gap. Framed as a divergence to be explained, not a correction: "you said 42%, the market prices approximately 28%; your edge claim is 14 points."
2. **Full cost decomposition** — bid/ask spread as a fraction of premium, commission, assignment and exercise fees, expected slippage, and the breakeven move required including all of it. This is the part the project's prior research says is worth 2–3.5× every signal combined, and it is the system's actual contribution.
3. **The reference class and its empirical distribution** — matched on moneyness, days to expiry, side, and whether an earnings event is inside the window. Show the mean and the full distribution, not just the mean: for a 3%-OTM weekly call, −59% over an 8-day hold. Show the count of historical cases and the time period.
4. **The breakeven probability** implied by the cost structure, next to the user's stated probability.

*Rationale for the order:* implied probability first because it is the sharpest challenge; costs second because they are the system's genuine contribution; reference class third because it is the most accuracy-associated principle in the training literature. All of it after commit, because shown before commit it is an anchor (Simoiu, Lorenz) and after commit it is evidence.

---

**STEP 6 — Pre-mortem, as a required field.**

*Ask, in prospective-hindsight framing:* it is [deadline date]. This position lost money. Write down what happened.
*Required:* at least two distinct causes, each tagged with a category from a fixed list — **direction wrong / move too small / move too late / IV crush / cost and slippage / assignment or early exercise / liquidity (could not exit at a reasonable price) / position sizing / something I have not thought of.**

*Rationale:* the measured pre-mortem effect is on confidence (d=0.81, Keysor et al.), not on failure-mode discovery — Peabody's Exp 2 found no advantage over a worst-case prompt in number of reasons generated, but all three of her studies found the *distribution of categories* shifted. So force the categories: that is the part that reliably changes. Requiring two causes is arbitrary but costless. The prospective-hindsight framing ("it lost money, why") rather than the conditional framing ("what might go wrong") follows Mitchell/Russo/Pennington — whose magnitude I could not verify, so do not cite a number for it.

Note the Chang et al. warning: post-mortem-style reasoning was *negatively* associated with accuracy in the GJP data (probably reverse causation). So **never score the user on pre-mortem quality** and never feed it into a system-generated probability.

---

**STEP 7 — Falsifier, as a required if-then plan.**

*Ask:* complete this sentence. "If [observable trigger] then I [specific action]."
*Required:* at least one invalidation trigger with (a) an observable, machine-checkable condition where possible — a price level, an IV level, a date, a realised-loss percentage — and (b) a specific action, phrased affirmatively.
*UI must reject:* triggers without a number or a date ("if the thesis breaks"), and actions phrased as negations ("I don't hold on") — Gollwitzer & Oettingen flag negation then-parts as potentially counterproductive.
*Also required:* a time-based falsifier, separate from the price-based one. The deadline from Step 2c is the natural default.

*Then, immediately:* "Place this as a resting order at your broker now?" with the order parameters pre-filled, and a required yes/no answer that is recorded.

*Rationale:* this is where the brief's prior finding about holding losers too long is addressed, and the evidence is uncomfortable. Fischbacher et al.: automatic limits moved the disposition effect from +0.082 to −0.106; **reminder-only limits moved it to 0.088, i.e. nowhere.** Richards et al.: stop-loss users were, if anything, *worse* on their trades without a stop. A note in a journal is a reminder. The only thing with measured effect is a resting order. The system cannot place it, so it must produce the ticket and record whether the user did. Expect low compliance — 7 of 22 subjects set no limits when offered; 11% took up the smoking commitment contract — which is why the *rate* of orders actually placed is the metric worth tracking.

---

**STEP 8 — Sizing, after costs and base rate are visible.**

*Ask:* position size, as a percentage of account.
*UI displays:* the reference-class mean outcome applied to the proposed size in currency; the full-loss amount; and the user's own last N realised outcomes on comparable trades, if any.
*Rationale:* sizing is asked last because premium and reference class are same-dimension anchors for it, and because by this point the user has seen the cost structure and the base rate. This ordering is a judgment call, not an evidence-backed one — flagged as such.

---

**STEP 9 — Resolution, automatic, at the deadline.**

Score each of the four Step-2 claims separately against what actually happened. Score the Step-3 probability with a proper scoring rule. Record whether the Step-7 falsifier triggered, whether a resting order existed, and whether the user acted. Record realised cost versus estimated cost.

*The user is never asked to self-report the outcome and never asked to re-describe the thesis afterward.* That is the 96%-positive-results regime.

---

### REQUIRED FIELDS

Minimum set for a thesis record to be scoreable later. Each must be captured before commit unless marked.

| Field | Why it is required |
|---|---|
| Contract identifier (underlying, expiry, strike, side, structure) | Without it the outcome cannot be reconstructed. |
| Entry timestamp, to the second | The pre-registration boundary. An untimestamped record cannot be distinguished from a retrofitted one. |
| Free-text thesis | The only field that captures reasoning. Does not improve accuracy (Hoffmann et al.) but is the record and reduces confidence. |
| Direction claim (binary) | Separately resolvable. Conflated claims cannot be scored. |
| Price threshold (free numeric) | Makes the claim falsifiable. Free-entry, not bucketed (partition dependence). |
| Deadline (date) | Without a horizon no claim is falsifiable and no claim ever resolves. A thesis with no deadline is unscoreable by construction. |
| Volatility claim (higher / lower / no view) | The dominant P&L driver for most option positions and the one most often absent from a directional thesis. "No view" must be allowed — forcing a view manufactures one. |
| Probability, 1–99, integer | The scoreable quantity. Fine-grained because coarsening costs 12–31% of Brier (Friedman et al.). |
| Resolution rule, stated explicitly | Which price source, which timestamp, how a gap or halt resolves. Without it, resolution is contestable after the fact, which reintroduces the retrofitting the record exists to prevent. No direct effect-size evidence for this field; it is a logical requirement, not an empirical one. |
| Pre-mortem: ≥2 causes, each category-tagged | Measured effect is confidence reduction (d=0.81). The category tags are what reliably changes (Peabody, all three studies). Tags make failure modes aggregatable across the user's history. |
| Falsifier: ≥1 if-then with observable trigger + affirmative action | Implementation-intention format, d=0.65 for goal attainment. Observable so the system can check it; affirmative because negation then-parts may backfire. |
| Time-based falsifier, separate | Price-based stops do not catch theta decay or a thesis that simply never plays out. |
| Resting order placed? (yes/no, recorded at entry) | The *only* exit intervention with a measured effect was automatic execution; reminders measured zero (Fischbacher et al.). This field distinguishes a real pre-commitment from a note. |
| Estimated all-in cost at entry (spread + commissions + fees + expected slippage) | So realised cost can be compared to estimate. This is the system's actual contribution and the thing most worth improving. |
| Breakeven probability implied by cost | The honest comparator for the user's stated probability. |
| Reference class assigned + its historical distribution + n + period | So the base rate shown is auditable and the class assignment can be revisited. |
| Position size, % of account, and currency amount | Needed to compute realised outcomes and to detect size creep after losses. |
| Market-implied probability at entry | The benchmark the user's probability is scored against. Must be snapshotted at commit, not recomputed later. |
| *(At resolution)* outcome of each of the four claims, separately | Four claims, four resolutions. |
| *(At resolution)* realised P&L, realised cost, exit reason, whether falsifier triggered, whether user acted | Exit discipline is the measurable behaviour. Compliance rate is the statistic. |
| *(Appended)* amendments, each timestamped, originals preserved | Pre-registration without immutability is not pre-registration. |

Deliberately **not** required: a system-generated composite probability from the decomposed parts (no evidential support, some counter-evidence); a conviction rating (verbal bands destroy the record); a self-assessed calibration score (uninterpretable at this n).

---

### DISPLAY ORDER RULES

**Hidden until after commit (Step 4):**

| Hidden item | Why |
|---|---|
| Market-implied probability, probability ITM, probability of touch, delta | The strongest possible anchor: a consensus summary statistic, on the same scale and dimension as the target quantity. Simoiu et al.: consensus display cost 3–7 percentile points of accuracy and inaccurate starters never recovered. Lorenz et al.: a single aggregate anchored *harder* than a full distribution. |
| Premium, bid, ask, mid, last | Same-dimension anchor for the sizing step; also an implicit probability (premium/width for a spread is a probability estimate the user can read off). |
| Underlying's current price, charts, 52-week range | Same-dimension anchor for the Step-2b threshold. The archival anchoring evidence in finance is observational, so this rule rests on the general anchoring literature (Chapman & Johnson), not a finance-specific experiment. Stated honestly: cheap precaution, weaker direct evidence. |
| IV, IV rank, IV percentile, term structure, skew | Anchor for the Step-2d volatility claim, which is otherwise the least-anchored and most informative thing the user says. |
| Implied move, expected-move cone, standard-deviation bands | A pre-packaged answer to Step 2b. |
| Analyst targets, consensus estimates, news sentiment, social sentiment | Consensus summary statistics — the exact category Simoiu et al. measured as harmful. |
| The reference-class base rate and its distribution | Counterintuitive but necessary. Shown before capture it anchors the probability toward the base rate, which looks like calibration but is not the user's own view, and destroys the ability to detect divergence. Shown after commit it is evidence and it is the material for challenge. Note Fernandes et al. (0.1% of variance): showing it will probably not change the decision anyway — so there is nothing to lose by showing it late and much to lose by showing it early. |
| The user's own prior answers, re-rendered on later screens | Carryover bias (Prava et al.): earlier answers anchor later ones, and same-screen presentation changes the bias magnitude. One question per screen. |
| The system's own cost analysis and verdict | Shown before capture it converts the tool into the thing the brief warns against in reverse — the user writes a thesis to match the system's framing. |

**Shown before commit:**
Static contract identifiers; calendar facts (expiry date, whether a known earnings date falls inside the window, days to expiry, exercise style, multiplier); and the fact that costs and base rates will be shown after commit. That last item is important: the user should know the reveal is coming, so the sequence reads as a protocol rather than as the tool withholding information.

**Two engineering consequences:**
1. The pre-commit screens must not load market data at all, rather than loading it and hiding it with CSS. A number that can be revealed by inspecting the DOM, by a flash of unstyled content, or by a browser tab title is not hidden.
2. Contract selection is the hard case, since picking a strike normally requires seeing prices. Either accept a typed/pasted identifier, or render a strike ladder with the price, greek and volume columns blanked.

**Not justified by evidence:** a warning banner telling the user not to anchor. Chapman & Johnson report that warnings and accuracy incentives do little to reduce anchoring. Sequence the form instead of captioning it.

---

### SMALL-N VERDICT

**Short answer: no. A single user's forecast calibration cannot be meaningfully assessed at the scale this project will reach, and the system should not attempt it.**

The arithmetic (my own computation, standard method, reproducible):

- For a calibration bucket where the user stated 70%, the 95% CI on the realised frequency is ±25 pp at n=10, ±19 pp at n=20, ±12 pp at n=50, and still ±9 pp at n=100 **in that bucket alone**. A user with 100 total forecasts spread over 5 buckets has ~20 per bucket, i.e. ±19 pp — which cannot distinguish a well-calibrated 70% from a badly overconfident one.
- The 95% CI on an *overall* Brier score for a perfectly calibrated forecaster is 0.153 wide at n=25, 0.109 at n=50, 0.077 at n=100, 0.055 at n=200.
- For scale: the entire trained-vs-untrained effect in the Good Judgment Project was 6–12% of a Brier score — roughly 0.011 to 0.022 on a base near 0.18. **At n=100, the 95% CI on one person's Brier score is two to four times wider than the largest forecasting-training effect ever credibly measured.**

Corroborating evidence that this is not an overly strict standard:
- Open Philanthropy, with 743 resolved predictions, called its own calibration findings exploratory, and its headline overconfidence claim rested on 8 observations in one bucket.
- The standard Brier decomposition is biased at small n in the *flattering* direction — it overestimates reliability (Ferro & Fricker 2012) — so a naive calibration/resolution display would systematically tell the user they are better calibrated than they are, at exactly these sample sizes. A fully unbiased decomposition is, per those authors, unattainable.
- Spiegelhalter's Z avoids binning, which is the right structural choice, but its normal approximation is documented at n=1,000 and not below, and it is weakest against prevalence shift — which is precisely the miscalibration a persistently bullish option buyer would exhibit.

**Thresholds, stated as honestly as the evidence allows:**

| n (resolved forecasts) | What can be said |
|---|---|
| < 30 | Nothing. Show counts and outcomes only. No score, no curve, no adjective. |
| 30–100 | Gross miscalibration only, and only if extreme — e.g. every forecast above 70% and a realised hit rate under 35%. Report as "consistent with overconfidence," with the interval, never as a calibration verdict. |
| 100–300 | An overall Brier score with a ±0.04 to ±0.08 interval. Enough to notice a large systematic bias. Not enough to say "well calibrated," and not enough to detect change over time. |
| > 300 | A bucketed calibration curve becomes worth plotting, with per-bucket intervals, and still only as a weak signal. |
| Never | "Your forecasts are well calibrated." Demonstrating calibration requires ruling out miscalibration, which requires power this sample size does not have. Absence of detected miscalibration is not calibration. |

**What to do instead.** Score the things that are measurable at small n because they are near-deterministic rather than probabilistic:

- **Cost accuracy:** estimated all-in cost vs realised, per trade. n=1 is informative. This is the system's real contribution and the thing the prior research says is worth 2–3.5× every signal.
- **Falsifier compliance rate:** proportion of trades where the trigger fired and the user acted. A rate, not an inference about skill.
- **Resting-order placement rate:** proportion of trades entered with a live resting order. Directly tied to the only exit intervention with a measured effect.
- **Divergence from implied:** the distribution of (user probability − market-implied probability). This does not need calibration to be informative — a user whose probabilities are systematically 15 points above implied is making a describable claim about their own edge, and can be shown the realised P&L of that claim.
- **Reference-class drift:** whether the user's trades are migrating toward worse reference classes (further OTM, shorter dated) over time, and whether that correlates with recent losses.
- **Pre-mortem category hit rate:** when a trade lost, had the user named that category in the pre-mortem? A simple proportion, interpretable at modest n, and it tells the user something true about their blind spots without claiming anything about calibration.

Every number displayed should carry its n and its interval. The honest framing for the user: *"this is your record, not your score."*

---

### DISCONFIRMING EVIDENCE

1. **Financial education explains 0.1% of the variance in financial behaviour, and large interventions have negligible effects after 20 months.** Fernandes, Lynch & Netemeyer, *Management Science* 60(8), 2014 — meta-analysis of 168 papers / 201 studies. This is the central counter-evidence to the whole informational layer of the product. Showing a user the base rate, the cost decomposition and the implied probability is information provision, and information provision does not change retail financial behaviour at a measurable scale. The only defensible response is to rely on structure (blocking fields, fixed sequence, immutable records, order tickets) rather than on the user updating.

2. **Requiring written justification did not improve accuracy and did not change reasoning strategy — with positive Bayesian evidence for the null.** Hoffmann, Gaissmaier & von Helversen, *JDM* 12(6), 2017, n=144 and n=110, BF 0.18 and 0.09 against an accuracy benefit; test error directionally *worse* with justification (6.2 vs 5.8 RMSD). The most intuitive field in the whole form — "explain your reasoning" — has no measured accuracy benefit. Keep it for the record; do not claim it sharpens thinking.

3. **Reminder-only exit devices measured exactly zero effect on the disposition effect.** Fischbacher, Hoffmann & Schudy, *RFS* 30(6), 2017: automated limits moved DE from +0.082 to −0.106; the Reminder treatment moved it to 0.088 (coefficient −0.040, ns). A research tool is a reminder-class intervention by construction. This is the sharpest disconfirming finding for the product's exit-discipline ambitions: the falsifier field, however well designed, is in the arm of the experiment that did nothing.

4. **Stop-loss users were *more* reluctant to realise losses on their trades without a stop.** Richards et al., *European Journal of Finance* 23(2), 2017: 4,328 investors, HR 0.9555 (p<.05) for selling at a loss on non-stop-loss trades. Discipline does not generalise from the person to their other trades. So a user who completes the thesis form faithfully on some trades should not be assumed to be more disciplined on the trades where they skip it — possibly the reverse.

5. **Voluntary pre-commitment has ~11% take-up, and two thirds of those who take it up still fail.** Giné, Karlan & Zinman, *AEJ: Applied* 2(4), 2010, RCT n=2,000. Also: 7 of 22 subjects in the Fischbacher Limit treatment set no limits at all even though limits were the entire point of their condition. The binding constraint on any pre-commitment feature is adoption, not design.

6. **The evidence that decomposing a binary probability question improves it is essentially absent, and decomposition measurably hurt non-extreme targets by 458% median error.** MacGregor & Armstrong 1994 (n=280, 1,078 estimates); Lawrence et al. 2006 as reviewed in "The Evidence for Question Decomposition is Weak." A multiplicative probability chain is a plausible mechanism with no supporting measurement and a documented failure condition.

7. **The debiasing literature is predominantly laboratory-based, with almost no durability evidence and no head-to-head comparison against structural interventions; and the review excludes decision-support systems entirely.** Fasolo, Heard & Scopelliti, *Journal of Management* 51(6), 2025: 100 studies, 23 of 32 debiasing studies lab-based, mean debiasing n=232 vs 2,254 for choice architecture, durability evidence limited to Morewedge et al.'s three months, no choice-architecture study examined persistence in organizations. There is **no review-level evidence that software of this kind improves decisions.**

8. **Anchoring is robust to warnings and to accuracy incentives.** Chapman & Johnson 2002. Any design that relies on telling the user to be careful about the market price will not work. Also note the Kahneman & Knetsch asymmetry they report ($14 vs $36 under dollar response, 24% vs 29% under percentage response): anchoring is not uniform across response formats, so the display-order rules are more certain for same-format pairings than for cross-format ones. The rules in this brief are deliberately conservative past what the evidence strictly requires.

9. **Decomposition barely dented overconfidence even where it massively improved accuracy.** MacGregor & Armstrong: the stated-vs-actual gap for "probability of being within 10% of truth" fell only from 28.0 to 23.6 points, with both conditions grossly overconfident (38.9% stated vs 10.9% actual; 32.6% vs 9.0%). Structural interventions can improve the *answer* without touching the *confidence*. For a tool whose central risk is manufactured confidence, this is a warning that improving the thesis is not the same as calming the user.

10. **The headline prospective-hindsight figure is unverified.** Mitchell, Russo & Pennington 1989 is widely cited for a ~30% increase in reasons generated, and I could not reach the primary result. The pre-mortem's verified numbers are d=0.81 for *confidence reduction* (Keysor et al., conference poster, n=53) and a mixed picture for failure-mode generation (Peabody 2017, with Exp 2 finding no advantage over a worst-case prompt). The pre-mortem's reputation outruns its measured evidence.

11. **Post-mortem-style reasoning was negatively associated with accuracy in the Good Judgment Project data** (Chang et al. 2016). Probably reverse causation — people write post-mortems after being wrong — but it is a direct caution against treating reflective fields as a quality signal, and against scoring the user on them.

12. **Pre-registration's documented effect is on the published literature, not on individual judgment.** Scheel et al. 2021 compares two bodies of literature with self-selection into Registered Reports; it is not a randomised test of whether pre-committing improves an individual's decisions. I found **no credible evidence** that an individual trader who pre-commits a falsifier achieves better exit discipline than one who does not, absent an automated mechanism — and finding 3 above suggests they do not.

---

### OPEN QUESTIONS

1. **Does showing the underlying's current price measurably anchor a price-target forecast?** I found no clean experiment. The archival analyst-anchoring literature is observational and cannot separate anchoring from rational information use. This is the one display-order rule resting on general rather than domain-specific evidence. Testable by the developer at n≈40 over a year as a within-subject A/B, though the power would be poor.

2. **Does a market-implied probability anchor *harder* than an unframed option price?** Chapman & Johnson's scale-matching argument predicts yes, and Lorenz et al.'s aggregated-vs-full-information result predicts yes, but the specific comparison is untested. It matters because it determines whether the strike-ladder blanking needs to cover prices or only derived probabilities.

3. **What is the magnitude of partition dependence in a strike-ladder UI?** Prava et al. establish that order and screen layout change the bias; I did not obtain magnitudes. A strike ladder is a partition, and the industry-standard UI may be systematically biasing every retail probability estimate.

4. **Does a self-produced order ticket close the gap between reminder-class and automation-class interventions?** Fischbacher et al. show the gap is total (0.19 vs 0.00). An order ticket the user must still place is intermediate. No evidence found. This is the most consequential unknown in the build — it decides whether the exit-discipline feature does anything.

5. **Does an immutable pre-registered record change behaviour, or only the quality of the record?** Scheel et al. establish the latter. The former is unestablished and, given Fernandes et al., should not be assumed.

6. **Is there a proper scoring rule better suited to n<100 than Brier?** Log score is more sensitive to confident errors and has worse small-sample behaviour; Brier is bounded and better-behaved. A Bayesian posterior over a calibration parameter with an informative prior might be more honest than any point score, since it degrades gracefully toward the prior at small n. Not researched in this pass.

7. **Does the reference-class assignment itself bias the user?** Showing a user that their trade belongs to the "3%-OTM weekly call" class with a −59% mean may cause them to adjust to a marginally different strike to escape the class rather than to reconsider the trade. Gaming of base-rate classification is not addressed in the Flyvbjerg literature, which concerns institutions with no incentive to escape the class.

8. **Does the cost-estimate-vs-realised feedback loop improve execution?** This is the project's own thesis and the one feedback signal measurable at small n. I found no literature on cost-feedback interventions for retail traders. Worth treating as the product's primary hypothesis precisely because it is the one the developer can test.

9. **Overlap with the other agent:** whether post-commit challenge should come from the system, from a reference class, or from the user's own pre-mortem categories. Chapman & Johnson's finding that "generate reasons against the anchor" and "present another person's thoughts" both reduced anchoring is relevant to the critic's design, and is left to that strand.

---

### TOP 10 SOURCES, RANKED

1. **Friedman, Baker, Mellers, Tetlock & Zeckhauser (2018)** — "The Value of Precision in Probability Assessment," *International Studies Quarterly* 62(2), 410–422. 888,328 forecasts. The single most directly implementable finding: capture probability as a fine-grained number, never a verbal band. +31% Brier at 2 bins, +562% for the best forecasters. https://scholar.harvard.edu/sites/scholar.harvard.edu/files/rzeckhauser/files/value_of_precision.pdf

2. **Fischbacher, Hoffmann & Schudy (2017)** — "The Causal Effect of Stop-Loss and Take-Gain Orders on the Disposition Effect," *Review of Financial Studies* 30(6), 2110–2129. Automated limits reversed the disposition effect (+0.082 → −0.106); reminders did nothing (0.088). The most consequential finding for the exit-discipline feature, and the most unwelcome. https://www.twi-kreuzlingen.ch/wp-content/uploads/2017/12/twi-rps-089-fischbacher-hoffmann-schudy.pdf

3. **Fernandes, Lynch & Netemeyer (2014)** — "Financial Literacy, Financial Education, and Downstream Financial Behaviors," *Management Science* 60(8), 1861–1883. 0.1% of variance; negligible after 20 months. The ceiling on everything informational the product does. https://papers.ssrn.com/abstract=2333898

4. **Simoiu, Sumanth, Mysore & Goel (2019)** — "Studying the 'Wisdom of Crowds' at Scale," AAAI/HCOMP. Randomised: consensus display cost 3–7 percentile points; recent and most-confident displays did not. The direct warrant for hiding implied probability pre-commit. https://5harad.com/papers/wisdom-of-crowds.pdf

5. **Chang, Chen, Mellers & Tetlock (2016)** — "Developing expert political judgment," *Judgment and Decision Making* 11(5), 509–526. Four-year randomised replication, 6–12% Brier improvement; comparison classes the most accuracy-associated principle (F=12.28); political knowledge not associated at all (F=0.08). https://www.sas.upenn.edu/~baron/journal/16/16511/jdm16511.pdf

6. **Lorenz, Rauhut, Schweitzer & Helbing (2011)** — "How social influence can undermine the wisdom of crowd effect," *PNAS* 108(22), 9020–9025. Social information reduced diversity and *raised confidence* without raising accuracy, under accuracy incentives. The mechanism of manufactured confidence, measured. https://pmc.ncbi.nlm.nih.gov/articles/PMC3107299

7. **Scheel, Schijen & Lakens (2021)** — "An Excess of Positive Results," *AMPPS*. 96% vs 44% supported hypotheses (N=152 vs 71). The argument for immutable pre-commitment, by close analogy. https://psyarxiv.com/p6e9c/

8. **Fasolo, Heard & Scopelliti (2025)** — "Mitigating Cognitive Bias to Improve Organizational Decisions," *Journal of Management* 51(6), 2182–2211. 100 studies: debiasing is lab-based and small-n; choice architecture is field-based and large-n; decision-support systems excluded entirely. Favour structure over instruction, and claim nothing about tools. https://openaccess.city.ac.uk/id/eprint/33831/

9. **Richards, Rutterford, Kodwani & Fenton-O'Creevy (2017)** — "Stock market investors' use of stop losses and the disposition effect," *European Journal of Finance* 23(2), 130–152. 4,328 investors, 65,096 round trips: the mechanism disciplines the trade, not the trader; stop-loss users were worse on their unstopped trades. https://core.ac.uk/download/82981049.pdf

10. **Gollwitzer & Sheeran (2006)** — "Implementation intentions and goal achievement," *Advances in Experimental Social Psychology* 38, 69–119. d=0.65, 94 studies, >8,000 participants, plus a documented list of failure conditions (weak commitment, strong competing habits, negation-phrased then-parts). The format specification for the falsifier field. https://www.socmot.uni-konstanz.de/sites/default/files/Gollwitzer_Oettingen_11_Planning_Goal_Striving.pdf

*Just outside:* Chapman & Johnson (2002) on anchoring's resistance to warnings and incentives; MacGregor & Armstrong (1994) on when decomposition hurts; Hoffmann, Gaissmaier & von Helversen (2017) on the null effect of required justification; Giné, Karlan & Zinman (2010) on commitment-device take-up; Open Philanthropy (2022) as the realistic small-N benchmark; Ferro & Fricker (2012) on the flattering direction of small-sample Brier decomposition bias.
