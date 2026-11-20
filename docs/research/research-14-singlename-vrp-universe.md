# Research Strand 14 — The Single-Name Variance Risk Premium and the Tradeable Universe

Date: 11 November 2026
Scope: whether a harvestable variance risk premium exists in individual US equity options; which name
characteristics predict where it is positive; whether the index-to-single-name vol relationship can be
used as a richness input; how many names a retail trader can realistically trade; weeklies vs monthlies;
the earnings cycle at 42–180 DTE; and assignment/dividend mechanics as a screening filter.

Cost hurdle applied throughout: ATM single-name option spreads of roughly 8–20% of premium at 42–180 DTE,
against roughly 2% for index options.

Label convention: **[PR]** peer-reviewed, **[WP]** working paper / unpublished, **[REG]** regulator or
exchange/clearing-house data, **[VEN]** vendor or practitioner material.

---

## PART 1 — IS THERE A HARVESTABLE VARIANCE RISK PREMIUM IN SINGLE NAMES AT ALL?

### 1.1 The small-sample baseline (the brief's starting point)

**CLAIM:** In the original 25-stock study the single-name implied-minus-realised volatility gap was
1.5 vol points against 3.3 for SPX, and fell to 1.07 points once dividend-affected options were removed;
14 of 25 stocks had negative average delta-hedged gains (7 significantly so at 99%) but 4 were
significantly positive.

**SOURCE:** Gurdip Bakshi & Nikunj Kapadia, "Volatility Risk Premiums Embedded in Individual Equity
Options: Some New Insights," *Journal of Derivatives*, Fall 2003. **[PR]**
https://people.umass.edu/~nkapadia/docs/Bakshi_Kapadia_JoD_Fall_2003.pdf

**Additional numbers recovered:** the average delta-hedging loss was 0.03% of the underlying for the
25 stocks against 0.07% for SPX — i.e. scaled by the underlying, the single-name premium is roughly
43% the size of the index premium. In the augmented regression, market volatility is significant
(coefficient −0.0233, p = 0.03) while firm-level volatility is not (−0.0042, p = 0.39); the panel
market-volatility premium estimate is −0.0263 (z = −2.55). The authors conclude idiosyncratic return
volatility is unpriced and that market volatility subsumes the firm's own volatility.

**EVIDENCE STRENGTH:** Strong for the stated numbers; Weak as a basis for a 2026 product (25 stocks,
early-1990s data, pre-decimalisation, pre-electronic-market-making).

**IMPLICATION FOR THE BUILD:** Confirms the brief. The headline single-name gap of 1.5 vol points is
less than half the index gap, and at the 1.07-point figure (dividend-clean) it is under a third. A
1–1.5 vol-point edge on a 90-day ATM option is worth roughly 0.4–0.6% of the underlying in premium
terms; against an 8–20%-of-premium round-trip spread on a premium that is itself ~5–6% of the
underlying, the spread costs 0.4–1.2% of the underlying. **The edge and the cost are the same order of
magnitude before any dispersion is considered.** That single arithmetic comparison is the governing
constraint of this entire strand.

---

### 1.2 The large-sample picture — and it is genuinely conflicting

**CLAIM:** Across roughly 6,000 underlying stocks over 1996–2009, the mean delta-hedged call gain held
to maturity (~50 days) was −1.13% of the initial position (median −1.29%), with 78% of stocks showing
negative average call returns, 32% significantly negative, and only about 1% significantly positive.

**SOURCE:** Jie Cao & Bing Han, "Cross section of option returns and idiosyncratic stock volatility,"
*Journal of Financial Economics*, 2013 (108: 231–249). **[PR]**
https://www-2.rotman.utoronto.ca/facbios/file/Han_JFE_published.pdf
Sample: OptionMetrics, Jan 1996 – Oct 2009; 6,141 call underlyings / 6,065 put underlyings; ~1,514
stocks per month; 213,640 call and 199,198 put observations.

**Cross-sectional dispersion (the central question of this strand), stock-level mean call gains:**

| Percentile | 10th | 25th | 50th | 75th | 90th |
|---|---|---|---|---|---|
| Mean delta-hedged call gain | −3.75% | −1.85% | −0.77% | −0.08% | +0.77% |

**EVIDENCE STRENGTH:** Strong. Largest sample in the literature, peer-reviewed in a top-three journal.

**IMPLICATION FOR THE BUILD:** This is the most important table in the strand. Read from the seller's
side, the median name hands a premium-seller +0.77% of the hedged position per ~50 days, the 25th
percentile name +1.85%, and the 10th percentile name +3.75%. **But the top quartile of names pay the
seller essentially nothing (+0.08%) and the top decile pay negative (−0.77%).** So: (a) a premium does
exist on average; (b) it is small at the median; (c) roughly a quarter of the optionable universe is
not worth selling at any cost level. Selection is not an optimisation, it is the whole strategy.

---

**CLAIM:** On a model-free implied-versus-realised basis across 135 individual stocks, average implied
volatility was 38.56% against realised 39.91% — i.e. a *negative* single-name variance risk premium of
about −1.35 vol points — and for 108 of 135 stocks a zero variance risk premium could not be rejected
at the 5% level; of the 27 rejections only 16 were significantly positive.

**SOURCE:** Joost Driessen, Pascal Maenhout & Grigory Vilkov, "The Price of Correlation Risk: Evidence
from Equity Options," *Journal of Finance*, 2009 (64: 1377–1406); working-paper version September 2005.
**[PR]** https://haas.berkeley.edu/wp-content/uploads/dmv_sept2005.pdf
Index comparison in the same paper: SPX implied 24.79% vs realised 21.02%, "very strongly rejected";
implied correlation 46.68% vs realised 28.68% (about 63% higher).

**EVIDENCE STRENGTH:** Strong. Peer-reviewed, *Journal of Finance*, model-free (whole smile) rather than
ATM-only.

**IMPLICATION FOR THE BUILD:** **This is the most serious piece of disconfirming evidence in the strand
and it must not be buried.** On the measure that matters for a vol-selling product — the full-surface
implied variance against subsequent realised variance — the average single name showed implied *below*
realised, and four-fifths of names showed no statistically distinguishable premium at all. The paper's
structural conclusion is sharper still: the entire index variance risk premium is attributable to priced
correlation risk, and individual variance risk is not priced. Note the apparent contradiction with
Cao & Han is partly reconcilable — DMV equal-weight 135 large stocks over a period containing the
dot-com volatility spike, use model-free rather than ATM implied vol, and measure variance rather than
delta-hedged P&L, which is convex and asymmetric. But the two cannot both be taken at face value, and
the product should be built as though DMV might be right.

---

**CLAIM:** The variance risk premium is negative (seller-favourable) for every Dow component studied,
and its idiosyncratic component accounts for about 80% of the total on average, ranging from 13% to 96%
across stocks.

**SOURCE:** Elise Gourier, "Pricing of Idiosyncratic Equity and Variance Risks," working paper,
January 2016, Queen Mary University of London. **[WP]**
https://www.elisegourier.com/uploads/3/7/9/6/37964671/singleauthorpaper.pdf
Sample: DJIA components (ex-Visa), daily, 1 March 2006 – end 2012; 2010–2012 out of sample.

**EVIDENCE STRENGTH:** Moderate. Careful structural estimation but only ~29 very large stocks, and a
working paper.

**IMPLICATION FOR THE BUILD:** **Directly contradicts the "idiosyncratic volatility is unpriced" claim
that the brief treats as established.** Gourier finds idiosyncratic variance risk is persistently
priced and is the dominant component. This matters enormously for the build's risk framing: if
idiosyncratic variance risk *is* priced, a short single-name vol position is compensated risk-taking
rather than an uncompensated gamble. If Bakshi–Kapadia and DMV are right, it is largely uncompensated.
**The build should treat this as an unresolved question and therefore size positions as though the
idiosyncratic exposure is uncompensated** — the conservative reading — while not asserting that it is.

---

### 1.3 Has it decayed? The decay evidence is index-only

**CLAIM:** The documented post-2012 collapse of the variance risk premium — VIX converging to realised
volatility from a ~3-point average gap, delta-hedged index option alpha going to zero, straddle Sharpe
ratios moving from −0.74 (1987–2001) to −0.09 (post-2001) to +0.12 (post-2012) — is established for
S&P 500 index options only. **Neither paper examines single-name options.**

**SOURCES:**
- Ian Dew-Becker & Stefano Giglio, "The decline of the S&P 500 variance risk premium," working paper,
  June 2026. **[WP]** https://www.dew-becker.org/documents/option_decline.pdf
  Baseline fixed break August 2012, chosen from the timing of the shift in dealer net gamma;
  Hodges–Lehmann dates the change to 2006–2010.
- Ian Dew-Becker & Stefano Giglio, "The Decline of the Variance Risk Premium: Evidence from Traded and
  Synthetic Options," Federal Reserve Bank of Chicago Working Paper 2025-17, 2025. **[WP/REG]**
  https://www.chicagofed.org/publications/working-papers/2025/2025-17
  Break "somewhere around 2010," split date 2012m5; traded put information ratios moved from about
  −0.75 (1987–2005) to +0.09; alpha magnitudes fell by about half when post-2005 data were included.

**EVIDENCE STRENGTH:** Strong for the index. **No credible evidence found** for an equivalent
documented decay in the single-name variance risk premium — no paper located that re-estimates the
single-name VRP on post-2012 data and reports a break.

**IMPLICATION FOR THE BUILD:** Two opposite readings are available and the honest position is that we
do not know which holds.
(a) The mechanism Dew-Becker & Giglio identify is a change in *dealer net gamma* — dealers moved from
systematically short gamma to roughly flat, driven by the growth of vol-selling ETFs and option-selling
funds. That supply-side change was concentrated in index products, which is where the retail and
institutional vol-selling flow went. Single names may have been less affected.
(b) Against that, the brief's own prior finding that delta-hedged equity-option alpha went to zero after
May 2012 and that the Zhan et al. characteristics collapsed to 0.10%/month is consistent with the same
decay having reached single names.
**Action for the build: the single-name VRP must be measured on recent data by the tool itself, not
assumed from the literature.** Any backtest using pre-2012 data is making an untested assumption. This
is the single largest open question in the strand.

---

### 1.4 Does it survive single-name transaction costs? — the decisive evidence

**CLAIM:** The canonical single-name volatility-spread strategy earns 21.9%/month on straddles and
2.3%/month delta-hedged at bid-ask midpoints, but falls to 4.1% and 0.2% respectively when the full
quoted spread is paid — and critically, **the effect is approximately zero in the widest-spread and
lowest-volume groups.**

**SOURCE:** Amit Goyal & Alessio Saretto, "Cross-Section of Option Returns and Volatility," *Journal of
Financial Economics*, 2009 (94: 310–326); working-paper version 2007/2008. **[PR]**
https://www.erim.eur.nl/fileadmin/erim_content/documents/10
Sample: OptionMetrics 1996–2005; one-month ATM options, moneyness 0.95–1.05; 120,028 monthly
observations across 3,885 stocks. Signal: log difference between 12-month realised volatility and
average ATM call/put implied volatility.

**Headline decile-spread (10−1) returns, monthly:**

| Strategy | Midpoint | 50% of quoted | 75% of quoted | 100% of quoted |
|---|---|---|---|---|
| Straddle | 21.9% | 13.0% | 8.6% | 4.1% |
| Delta-hedged calls | 2.3% | 1.3% | 0.7% | 0.2% (insignificant) |
| Delta-hedged puts | 2.6% | 1.6% | 1.2% | 0.7% |

**By option bid-ask spread tercile (straddle 10−1):**

| Tercile | Midpoint | 50% | 75% | 100% |
|---|---|---|---|---|
| Low spread (most liquid) | 18.0% | 12.7% | 10.3% | **8.2%** |
| Medium spread | 22.0% | 13.5% | 9.6% | 5.9% |
| High spread | 23.9% | 11.3% | 5.3% | **−0.8%** |

Delta-hedged calls, midpoint / 100% quoted: low spread 1.1% / **0.0%**, medium 2.6% / 0.7%,
high 2.9% / **0.1%**.
Delta-hedged puts, midpoint / 100% quoted: low 2.3% / 1.2%, medium 2.7% / 0.9%, high 2.6% / **0.0%**.

**By option trading volume tercile (straddle 10−1):**

| Tercile | Midpoint | 50% | 75% | 100% |
|---|---|---|---|---|
| Low volume | 23.3% | 12.4% | 7.0% | **1.5%** |
| Medium volume | 21.5% | 13.3% | 9.3% | 5.2% |
| High volume | 17.7% | 11.9% | 9.0% | 6.1% |

Delta-hedged calls, low volume: 2.8% midpoint / **0.2%** at full spread. Low-volume delta-hedged puts:
2.6% / **0.2%**.

**EVIDENCE STRENGTH:** Strong. Peer-reviewed, JFE, and the liquidity splits are reported directly
rather than inferred.

**IMPLICATION FOR THE BUILD:** **This table is the load-bearing evidence for the liquidity gate and it
fully vindicates treating the gate as exclusionary rather than as a score.** Note the structure
carefully: gross returns are *highest* in the illiquid terciles (23.9% high-spread vs 18.0% low-spread)
and net returns are *lowest* there (−0.8% vs +8.2%). Any screen that ranks on gross richness will
systematically select the names where the edge does not survive execution. The tool must therefore
apply the liquidity filter **before** computing any richness score, and must never allow a high
richness score to override a liquidity failure. Note also that straddles retain far more of the edge
than delta-hedged positions do (8.2% vs 1.2% in the liquid tercile) because the delta-hedging rebalances
pay the stock spread repeatedly — relevant to the other agent's overlay strand.

---

**CLAIM:** The best modern machine-learning cross-section of equity option returns earns 2.63%/month
gross but 1.33% at a 15% effective spread and 0.47% at 25%, and **long-dated options (over 90 days)
become insignificant or negative at a 25% effective spread while short-dated ones (≤90 days) survive.**

**SOURCE:** Turan G. Bali, Heiner Beckmeyer, Mathis Moerke & Florian Weigert, "Option Return
Predictability with Machine Learning and Big Data," *Review of Financial Studies*, 2023 (36: 3548–3602);
CFR Working Paper 21-08. **[PR]**
https://academic.oup.com/rfs/article/36/9/3548/7056660
Sample: OptionMetrics, Jan 1996 – Dec 2020; 4,932,372 options on 7,046 underlyings; 12,129,844
option-month observations; out-of-sample 2003–2020. Nonlinear ensemble H-L Sharpe 2.06 gross,
1.17 at 15%, 0.43 at 25%. At 25% the strategy is zero or slightly negative in 2016–2019. Short-term ATM
options have the highest risk-adjusted return (Sharpe 1.34) at 25%. Sample covers about 83% of total US
equity market capitalisation with an average size percentile of 72.

**EVIDENCE STRENGTH:** Strong. Peer-reviewed, RFS, largest and most recent sample with explicit cost
grids.

**IMPLICATION FOR THE BUILD:** Two consequences, both uncomfortable for the brief's stated horizon.
First, **the maturity evidence cuts against the long end of the 42–180 DTE target range.** The only
peer-reviewed study that splits option-return predictability by maturity and nets out costs finds the
over-90-day bucket does not survive a 25% effective spread. The 42–90 DTE sub-band is materially better
supported by evidence than 90–180 DTE, and the build should either concentrate there or explicitly
acknowledge that the 90–180 band is an evidence-free extrapolation. Second, the strategy was flat to
negative in 2016–2019 at 25% costs — the decay concern is live in single names even without a formal
break test.

---

**CLAIM:** Among S&P 500 constituents — the most liquid single names in the market — the average
relative *effective* bid-ask spread on at-the-money calls was 6.41% and on at-the-money puts 5.25%,
rising to 12.58% for OTM calls and 9.77% for OTM puts, against 0.09% for the underlying stocks.

**SOURCE:** Peter Christoffersen, Ruslan Goyenko, Kris Jacobs & Mehdi Karoui, "Illiquidity Premia in
the Equity Options Market," *Review of Financial Studies*, 2018 (31: 811–851). **[PR]**
https://ruslangoyenko.com/wp-content/uploads/2019/09/illiquidity-premia-in-the-equity-options-market.pdf
Sample: S&P 500 stocks, Jan 2004 – Dec 2012, intraday LiveVol trades and quotes. Illiquidity measured
as 2|trade price − midpoint| / midpoint. The long-short illiquid-minus-liquid delta-hedged portfolio
earns risk-adjusted daily spreads of 3.4% (ATM calls), 2.5% (ATM puts), 4.3% (OTM calls), 1.9%
(OTM puts).

**EVIDENCE STRENGTH:** Strong. Peer-reviewed, RFS, uses actual intraday trades rather than closing
quotes.

**IMPLICATION FOR THE BUILD:** This is the hard number the cost hurdle should be anchored to. **Even
inside the S&P 500, the average ATM option costs about 5–6.4% of premium to trade once, measured against
actual executions.** A round trip is therefore roughly 10–13% of premium, consistent with the brief's
8–20% range, and the brief's range should be read as a *round-trip* figure for liquid names and an
understatement for anything smaller. Equally important: the paper's own interpretation is that the
illiquidity premium is compensation to market makers for the risks of their net long inventory, and the
authors state explicitly that the alphas are not readily earned by investors who must pay the spread.
**A retail trader is on the paying side of this premium, not the receiving side.** Any apparent edge
that correlates with option illiquidity should be presumed to be this premium seen from the wrong side.

---

**CLAIM:** Delta-hedged equity-option returns computed from 4pm closing bid-ask midpoints are biased
upward by roughly 60 bp/month relative to 1pm midpoints and by over 100 bp/month relative to 10am
midpoints — a bias of the same order of magnitude as the entire measured single-name premium.

**SOURCE:** Ruslan Goyenko & Chengyu Zhang, "Option Returns: Closing Prices are not What You Pay,"
working paper, McGill University, 2019. **[WP]**
https://ruslangoyenko.com/wp-content/uploads/2019/11/Option-Returns-Nov-18-2019-FINAL.pdf
For S&P 500 constituents, delta-hedged returns from 1pm quotes are about 60 bp lower than from 4pm
quotes for both calls and puts (2004–2010). Equity call returns 2011–2017: +0.11% at 4pm vs −0.48% at
1pm (59 bp gap); the 10am gap is about 1.4%. The non-trading/trading return gap for equity calls falls
from −0.87% (4pm) to −0.31% (10am) in 2004–2010 and from −86 bp to −23 bp in 2011–2017. Using 10am
quotes, the differential pricing between equity and index call returns largely disappears.

**EVIDENCE STRENGTH:** Moderate (working paper, not peer-reviewed), but methodologically serious and
the direction of the bias is not in doubt.

**IMPLICATION FOR THE BUILD:** **Potentially the most damaging single finding in the strand.** Cao &
Han's headline single-name delta-hedged gain is −1.13% per ~50 days; Goyal & Saretto's delta-hedged
decile spreads are 2.3–2.6%/month at midpoints. A measurement artefact worth 60–140 bp/month is large
enough to account for a substantial fraction of both. Because every OptionMetrics-based study in this
strand (Cao–Han, Goyal–Saretto, Bali et al., Shafaati et al., Hu–Jacobs) uses 4pm closing midpoints,
**the entire literature's single-name VRP estimates share a common upward bias of unknown but material
size.** Practical consequence: the build must not calibrate expected edge from published figures. If it
records its own quotes it should timestamp them intraday, and it should treat any backtest built on
end-of-day marks as an upper bound rather than an estimate.

---

### 1.5 Where the cross-asset literature leaves single names

**CLAIM:** The most recent systematic cross-asset survey of variance risk premia covers 20 futures
markets and finds negative premia in 19 of them, but **does not estimate a single-name equity variance
premium at all** — its only equity evidence is the S&P 500.

**SOURCE:** Steven L. Heston & Karamfil Todorov, "Exploring the Variance Risk Premium Across Assets,"
SSRN 4373509; presented AFA 2024. **[WP]** https://afajof.org/management/viewp.php?n=41580
Data 2006–2020. S&P 500 mean hedged VIX² return −11.9%/month (Sharpe −0.23) full sample, −22.9%
(Sharpe −0.86, significant at 1%) pre-COVID. The paper notes the realised S&P 500 variance risk premium
was not significantly different from zero over the full sample.

**EVIDENCE STRENGTH:** Strong for what it covers; irrelevant to single names except as an absence.

**IMPLICATION FOR THE BUILD:** Worth noting that even the *index* premium is not significantly different
from zero over 2006–2020 once March 2020 is included. The single-name premium is smaller than the index
premium on every measure in this strand. If the index premium is marginal, the single-name premium net
of 10–13% round-trip costs is at best marginal and plausibly absent.

---

## PART 2 — WHICH NAME CHARACTERISTICS PREDICT WHERE THE PREMIUM IS POSITIVE?

This is the most product-relevant question in the brief. The literature gives a clear answer with an
uncomfortable twist: **the characteristics that predict a large premium are, with near-perfect overlap,
the characteristics that predict it cannot be captured.**

### 2.1 Idiosyncratic volatility — the strongest single predictor, pointing the wrong way

**CLAIM:** Delta-hedged equity option returns fall monotonically as idiosyncratic volatility rises; the
Fama–MacBeth coefficient on IVOL is −0.0405 (t ≈ −15.5), a one-standard-deviation rise in IVOL lowers
the average scaled call return by about 0.93%, and a move from the 10th to the 90th IVOL percentile
lowers it by about 2.14%. Systematic volatility carries the *opposite* sign (coefficient +0.016,
t ≈ 3.8).

**SOURCE:** Cao & Han, *JFE* 2013, as above. **[PR]**
Portfolio implementation: buying delta-hedged calls in the lowest IVOL quintile and selling those in the
highest earns about 1.40%/month equal-weighted (alpha 1.32% against common factors); value-weighted
returns are roughly half that; the effect reaches 1.63%/month in the smallest size quintile.
Cost grid: 1.40% at midpoint → 1.16% at 10% of quoted spread → 0.79% at 25% → **0.17%, insignificant,
at 50%.** The authors conclude only participants with relatively low trading costs can profit.

**EVIDENCE STRENGTH:** Strong (peer-reviewed, JFE, 6,000-stock sample, replicated in spirit by later
work).

**IMPLICATION FOR THE BUILD:** The single most actionable and most treacherous finding in the strand.
High-idiosyncratic-volatility names carry by far the richest options — a 2.14 percentage-point swing in
delta-hedged return from the 10th to the 90th IVOL percentile is roughly twice the entire average
premium. **But the value-weighting result (halves the effect) and the size result (strongest in the
smallest quintile) say plainly that the premium concentrates in small, high-IVOL names, which are
precisely the names with the widest option spreads.** Combined with Goyal–Saretto's liquidity terciles,
the conclusion is that the IVOL signal is strongest exactly where it cannot be harvested. The build
should use IVOL as a *within-liquid-universe* ranking variable only — rank on IVOL among names that have
already passed the spread and open-interest gate — and must not use it to justify widening the universe.
Note also the sign conflict with Bakshi–Kapadia: Cao–Han's IVOL effect is interpreted by the authors as
mispricing driven by limits to arbitrage and demand pressure, not as a risk premium, which is a further
reason to expect it to be unstable and to have decayed.

---

**CLAIM:** Of 130 firm- and option-level characteristics tested with LASSO and bootstrap post-selection
inference, only three survive as dominant determinants of delta-hedged equity option returns: the
realised-implied volatility spread, idiosyncratic volatility, and turnover.

**SOURCE:** Mobina Shafaati, Don M. Chance & Robert Brooks, "The cross-section of individual equity
option returns," *Journal of Empirical Finance*, 2026, vol. 88, article 101748.
DOI: 10.1016/j.jempfin.2026.101748 **[PR]**
The authors report that sparse models perform well out of sample with predictive slopes close to one;
the idiosyncratic-volatility effect intensifies when trading frictions and hedging costs are high; the
realised-implied spread works more strongly under greater information frictions, higher demand pressure
and lower liquidity; the turnover effect is largely insensitive to information and arbitrage-cost
proxies. The paper does not report transaction-cost-adjusted returns.

**EVIDENCE STRENGTH:** Strong for the variable-selection result (peer-reviewed, 2026, explicitly
designed to address selection uncertainty); Weak for tradeability, since no cost analysis is reported.

**IMPLICATION FOR THE BUILD:** The best available answer to "what should the richness score contain."
Three inputs, not nine or thirty: **(1) realised-minus-implied volatility spread, (2) idiosyncratic
volatility, (3) turnover.** Turnover is the most encouraging of the three for this product because it is
the only one whose effect is reported as insensitive to arbitrage-cost proxies — i.e. the only one that
does not appear to be a limits-to-arbitrage artefact. The other two intensify precisely where frictions
are high, which is the Cao–Han problem again. A defensible build weights turnover more heavily than its
raw predictive power would suggest, on robustness grounds.

---

### 2.2 Volatility level

**CLAIM:** There is a statistically significant negative relation between the level of volatility and
both call and put delta-hedged returns in individual equities; long straddle returns are lower for
high-volatility names, with a reported quintile spread of 5.4%/month equal-weighted (Newey–West t = 2.90)
and 6.3% volume-weighted.

**SOURCE:** Guanglian Hu & Kris Jacobs, "Volatility and Expected Option Returns," working paper
January 2016, University of Houston (subsequently *Journal of Financial and Quantitative Analysis*).
**[WP, later PR]** https://www.mcgill.ca/desautels/files/desautels/hj_jan29_2016.pdf
Sample: OptionMetrics, Jan 1996 – Jul 2013. Caveat recorded in the source: the quintile means (2.8% low
vol, 2.6% high vol) do not reconcile with the stated 5.4% spread, so the table should be checked against
the published version before use. The authors attribute much of the delta-hedged result to hedging error
and discretisation rather than a tradeable premium, and do not model transaction costs.

**EVIDENCE STRENGTH:** Moderate. Direction is consistent across studies; magnitudes in the working-paper
tables are internally inconsistent and the authors themselves caution against reading the delta-hedged
results as a tradeable premium.

**IMPLICATION FOR THE BUILD:** Points the same way as IVOL — high-volatility names are where options are
rich — and carries the same liquidity trap. The authors' own caution that the delta-hedged result is
largely hedging error and discretisation is an important warning: **a tool that computes expected
delta-hedged P&L from a model will inherit exactly that error.** Prefer measuring realised premium
outcomes over modelling them.

---

### 2.3 Size, index membership, analyst coverage, institutional ownership

**CLAIM:** Option return predictability is stronger among underlyings that are more illiquid, have lower
institutional ownership, and have lower analyst coverage — but these results are reported only in gross
R² terms, with no cost-adjusted returns by tier.

**SOURCE:** Bali, Beckmeyer, Moerke & Weigert, *RFS* 2023, as above. **[PR]**

**EVIDENCE STRENGTH:** Moderate for the gross pattern; **No credible evidence found** for the
net-of-cost version, which is the one the build needs.

**IMPLICATION FOR THE BUILD:** Same structure a third time. Every predictor of richness is a proxy for
informational friction or limits to arbitrage, and therefore a proxy for cost. **The honest statement
for the product is that the literature has not established a characteristic that predicts a positive
single-name premium among liquid, widely-covered, institutionally-held large caps** — which is exactly
the universe a retail trader can actually transact in. This is the deepest problem with the strand's
central question and should be stated as such in the build documentation.

**CLAIM:** On index membership specifically, the one located study of the S&P 500 inclusion effect in
the options market examines implied betas and comovement, not option liquidity, implied volatility
levels or option trading activity.

**SOURCE:** Jerry Coakley, George Dotsis, Apostolos Kourtis & Dimitris Psychoyios, "The S&P 500 index
inclusion effect: Evidence from the options market," *International Journal of Finance & Economics*,
2024, 29(1): 1157–1171. DOI: 10.1002/ijfe.2728 **[PR]**
Findings recovered: post-inclusion implied betas rise significantly less than historical or hybrid
betas; implied betas show no evidence of excess comovement after inclusion; added stocks change before
the announcement.

**EVIDENCE STRENGTH:** **No credible evidence found** on the question actually asked — whether index
membership predicts a positive or capturable option premium.

**IMPLICATION FOR THE BUILD:** Index membership should be used only as what it demonstrably is — a
cheap, stable, survivorship-resistant proxy for size, analyst coverage and option listing depth — and
not asserted to carry independent information about option richness. As a universe-construction device
it is defensible and cheap to implement. As a richness signal it is unsupported.

---

### 2.4 Does cross-sectional richness persist enough to trade?

**CLAIM:** Individual-stock implied volatility is cross-sectionally predictable and mean-reverting —
a Fama–MacBeth regression of the log change in ATM IV on its current level, its 12-month moving average
and 12-month average realised volatility achieves an average adjusted R² of 17.1% (up to 50% in some
months) — and trading on it earned 16.1% to expiration (~47 days) at midpoints, falling to 5.5% at an
assumed 75%-of-quoted effective spread.

**SOURCE:** Alessio Saretto, "Option Returns and the Cross-Sectional Predictability of Implied
Volatility," working paper, Purdue University, November 2005. **[WP]**
https://www.cis.upenn.edu/~mkearns/finread/CrossOptions.pdf
Sample: OptionMetrics, Jan 1996 – Jun 2005; 81,296 monthly observations across 4,249 stocks; 30–60 DTE
near-the-money. After costs by liquidity: low-spread tercile 7.2%, medium 8.6%, high 2.9%; by volume,
low tercile 1.4%, medium 8.8%, high 8.6%. The paper's introduction cites a headline (8.8% monthly,
Sharpe 0.271) that does not match its tables, and Table 4's top-decile straddle mean is 5.6%, so figures
should be verified against the published version.

**EVIDENCE STRENGTH:** Moderate. Working paper with internal inconsistencies, substantially superseded
by the published Goyal–Saretto. Important for the *persistence* question specifically.

**IMPLICATION FOR THE BUILD:** **The persistence answer is the opposite of what a watchlist product
wants.** The predictability documented here is *mean reversion*, not persistence: stocks whose IV is
below their own 12-month average and below the cross-sectional average tend to see IV rise. So a name
that looks rich today tends to become less rich, and a name that looks cheap tends to become less cheap.
There is a stable *stock-specific average* level of implied volatility (that is what the 12-month moving
average captures), but the deviation from it — the part that constitutes richness — is transient.
Practically: the tool should score richness as a deviation from the name's own trailing IV and realised
vol, refresh that score continuously, and **must not maintain a static "these names have rich options"
watchlist**, because the literature says that list is a list of names whose options are about to stop
being rich. The Table 11 result in the same paper — that when option prices are recomputed using the
cross-sectional volatility forecast the strategy's returns are no longer significant — reinforces this:
the apparent richness is largely the market pricing in information the naive signal ignores.

---

## PART 3 — THE INDEX-VERSUS-SINGLE-NAME VOLATILITY RELATIONSHIP AS A SELECTION INPUT

### 3.1 The mechanism and the official measures

**CLAIM:** The Cboe implied correlation indices compare SPX option implied variance with the implied
variance of an uncorrelated basket of the top 50 SPX components by float-adjusted market cap, dividing
the difference by the sum of pairwise weighted implied volatility products; they use ATM implied
volatilities defined at delta 0.5 and a Markowitz portfolio framework with no option pricing model.

**SOURCE:** Cboe Global Indices, "Cboe Implied Correlation Index" white paper, v1.0.5. **[VEN/REG]**
https://cdn.cboe.com/resources/indices/documents/Implied_Correlation-WhitePaper-v1.0.5.pdf
The white paper documents the 3-month index (COR3M) and states other maturities use the same methodology
with different IV tenors. Components 51–55 form a replacement pool. The white paper does **not** describe
a method for deriving a correlation for an individual stock. Tickers COR1M and COR3M are quoted publicly
(e.g. Yahoo Finance ^COR1M, ^COR3M).

**EVIDENCE STRENGTH:** Strong for the methodology (official exchange documentation).

**IMPLICATION FOR THE BUILD:** The index is computed top-down for the basket as a whole. **It yields a
single market-wide number, not a per-name richness measure**, and the official methodology gives no
decomposition to individual stocks. It can therefore serve as a *regime* input — is single-name vol rich
or cheap relative to index vol across the market right now — but not as a cross-sectional selector. A
regime input is still useful: it tells the tool whether this is a good month to be selling single-name
premium at all, which is a different and more defensible question than which name to sell.

---

**CLAIM:** Option-implied correlation substantially exceeds subsequently realised correlation —
46.68% implied against 28.68% realised, about 63% higher — and the entire index variance risk premium
is attributable to the price of correlation risk, with almost all of the correlation risk premium
orthogonal to the market (the systematic part is under 0.25% of the total).

**SOURCE:** Driessen, Maenhout & Vilkov, *Journal of Finance* 2009, as above. **[PR]**
Also recorded: individual puts show no evidence of a premium beyond the standard one-factor model; the
97.5% confidence bound on their one-factor excess returns is always positive, so that model cannot be
rejected for individual options; index puts have excess returns of roughly −7% to −39% per month
relative to individual puts.

**EVIDENCE STRENGTH:** Strong.

**IMPLICATION FOR THE BUILD:** This is the clean statement of the index-vs-single-name relationship and
it is bad news for the single-name seller. **The gap between index IV and the weighted average of
single-name IVs is not a single-name richness signal — it is the price of correlation risk, and it sits
in the index leg, not the single-name leg.** A retail trader selling single-name premium is on the wrong
side of the only part of the equity-vol complex that is clearly and robustly priced. The −7% to −39%
per month advantage of index puts over individual puts is the quantitative statement of how much is
given up by trading single names instead of the index. Given the brief's constraint that the tool must
work on individual tickers, this cost is accepted by assumption; the build should state it explicitly
rather than let the user discover it.

---

### 3.2 Can it be used as a per-name richness input?

**CLAIM:** No peer-reviewed work was located that uses the relationship between index implied volatility
and a single name's implied volatility — via that name's beta and historical correlation — as a
cross-sectional richness or selection signal for individual equity options.

**SOURCE:** Searches across the implied-correlation literature returned the Cboe methodology,
Driessen–Maenhout–Vilkov, and correlation-risk-premium work aimed at predicting *market* returns
(e.g. Buss & Schönleber, "Expected Correlation and Future Market Returns,"
https://www.aeaweb.org/conference/2019/preliminary/paper/H8b9eReG **[WP]**; Buss, "Measuring Equity Risk
with Option-Implied Correlations," https://www.gsefm.eu/fileadmin/user_upload/dateien_schuelermarketing/mimeo_2012_Buss.pdf
**[WP]**). All operate at index or market level. The only per-name "rich/cheap versus index" material
located is practitioner presentation material (R. Renicker, "Identifying Rich and Cheap Implied
Volatility — Equity Options," 2005, circulated via SlideShare **[VEN]**) and vendor screeners
(e.g. PowerOptions IV Rank screener **[VEN]**), neither of which contains validated out-of-sample
results.

**EVIDENCE STRENGTH:** **No credible evidence found.**

**IMPLICATION FOR THE BUILD:** A beta-and-correlation-adjusted "name IV versus index-implied name IV"
measure is constructible and intuitively appealing, and it has the attraction of being a *relative*
measure that partially neutralises market-wide vol regime. But it is unvalidated. If built, it should be
labelled in the product as an exploratory diagnostic, not an evidenced signal, and it should not be
allowed to override the three evidenced inputs (realised-implied spread, IVOL, turnover) or the
liquidity gate. The honest framing: this is a hypothesis the tool could help the user test, not a
finding the tool should act on.

---

## PART 4 — THE TRADEABLE UNIVERSE

### 4.1 The regulatory baseline

**CLAIM:** 8,439 unique underliers had at least one options contract trade during 2025, up 144% from
3,452 in 2012; by end-2025, 69.5% of 12,134 unique listed equity symbols had at least one option trade;
and 4,866,065 unique option series traded in 2025, up 719% from 594,488 in 2012.

**SOURCE:** SEC Staff of the Office of Analytics and Research, Division of Trading and Markets,
"Roundtable on Options Market Structure — Supporting Data," 9 April 2026. **[REG]**
https://www.sec.gov/files/roundtable-options-market-structure.pdf
(Staff research note; does not necessarily reflect Commission views.)

**EVIDENCE STRENGTH:** Strong. Regulator-compiled, current, counts actual trades.

**IMPLICATION FOR THE BUILD:** The gross universe is large but the metric is extremely weak — "at least
one contract traded in a year" is nowhere near tradeable. This is the ceiling, not the estimate.

---

### 4.2 The concentration evidence

**CLAIM:** The top 10 underliers accounted for 31.7% of total options volume at end-2025, up from 24.0%
in 2012; the top 10 ETP products accounted for 83.8% of ETP volume, up from 75.4%.

**SOURCE:** SEC staff note, April 2026, as above. **[REG]**
(The note's executive summary rounds the top-10 share to 31%. It provides volume-rank buckets — Top 10,
11th–50th, 51st–100th, 101st–250th, 251st+ — but no top-50 share figure.)

**CLAIM:** The 27 highly liquid underlyings eligible for Cboe's new pre-market session represent 53.4%
of market volume; single-stock options ADV was 32.7M contracts in Q3 2026 (about 46% of the 70.6M
market-wide ADV), ETF options 28.3M (~40%), index options 6.1M (~9%); 0DTE was a record 24.2M contracts,
about 36% of total volume.

**SOURCE:** Henry Schwartz, Cboe Global Markets, "State of the Options Industry Q3 2026: Volume Growth
Concentrated in Index and ETF Options," 19 October 2026. **[VEN/REG]**
https://www.cboe.com/insights/posts/state-of-the-options-industry-q-3-2026-volume-growth-concentrated-in-index-and-etf-options

**EVIDENCE STRENGTH:** Strong (exchange-published data, current).

**IMPLICATION FOR THE BUILD:** **The 27-names-equals-53.4%-of-volume figure is the single most useful
universe datapoint in the strand**, and it is consistent with the brief's prior finding that the top ten
underlyings were ~60% of retail option trades. It says the practically liquid core of the market is a
few dozen names, not a few hundred. Note also that 36% of all volume is 0DTE and is therefore entirely
irrelevant to a 42–180 DTE product — the volume statistics overstate liquidity at the maturities this
tool cares about, probably substantially, because 0DTE and near-dated weekly volume is concentrated in
the same handful of mega-cap names.

---

### 4.3 The liquidity-decay evidence — the universe is narrowing, not widening

**CLAIM:** Between 2012 and end-2025 the trade-weighted quoted NBBO spread for the top 10 equity
underliers was unchanged at 1.6%, while quoted spreads widened across every other equity bucket and
effective spreads rose by 0.5, 1.3, 1.5 and 0.4 percentage points (and nominally by 0.3¢, 1.5¢, 1.3¢
and 2.2¢) across the four non-top-10 buckets.

**SOURCE:** SEC staff note, April 2026, as above. **[REG]**
Other figures recorded: median equity-option effective spread fell market-wide from 2.2% to 1.9%; median
ETP effective spread from 1.9% to 1.4%; top-10 equity effective spread from 1.3% to 0.9% (3.0¢ to 2.3¢
nominal); top-10 ETP quoted spread flat at 1.7%. The note describes the widening outside the top 10 as
a potential sign of weaker displayed market quality. The note does not publish per-bucket volume shares
or maturity breakdowns in the extractable text.

**EVIDENCE STRENGTH:** Strong.

**IMPLICATION FOR THE BUILD:** Decisive for the universe question and it points one way. **Over thirteen
years of explosive growth in options trading, execution quality improved only in the top ten names and
deteriorated everywhere else.** The apparent democratisation of options is a concentration, not a
broadening. Any universe estimate built from older academic samples (Goyal–Saretto's 3,885 stocks,
Cao–Han's 6,000) will overstate what is tradeable today outside the mega-caps. Note the one important
caveat in the other direction: these are volume-weighted figures dominated by short-dated contracts, and
*percentage-of-premium* spreads mechanically improve with maturity because the premium in the denominator
grows faster than the nominal spread. A 90-DTE ATM option on a $100 stock at 30% vol carries roughly
$6.00 of premium, so a 10¢ nominal spread is 1.7% of premium where the same 10¢ on a $0.50 weekly is 20%.
**The 42–180 DTE horizon is therefore structurally advantaged on a percentage-of-premium basis relative
to what the volume-weighted statistics show** — this is the one genuinely favourable structural finding
for the brief's chosen horizon, and it partially offsets Bali et al.'s maturity result. It needs direct
measurement to confirm.

---

### 4.4 Vendor and practitioner counts

**CLAIM:** Vendor liquidity rankings of optionable US names extend to at least 1,208 symbols, ranked on
average option volume, average open interest and average tightest bid/ask spread, but publish no
numeric liquidity thresholds.

**SOURCE:** Tim's Stock Lists, "Liquid Options" ranking. **[VEN]**
https://timsstocklists.com/Options/LiquidOptions
(Page truncated at retrieval; visible range ran from rank 1 to rank 1,208. A "Liquidity Rating" column
exists but its construction is undocumented.)

**CLAIM:** Options liquidity is heavily concentrated in a small set of active underlyings; about 1.45
million individual index and equity option series traded in 2023; SPX ADV was 3.9M contracts (2.3M of
them 0DTE) and VIX 858,000 against a total of about 60.6M, i.e. SPX and VIX together roughly 7.8% of
total volume.

**SOURCE:** Exegy, "How Options Liquidity Impacts Your Market Data Needs," 24 March 2026, attributing
figures to Cboe and SIFMA. **[VEN]** https://www.exegy.com/market-structure-option-liquid-data/
(The post's Table 1 is titled "10 Most Liquid Options" but lists seven instruments with a 2019 header on
2025 data, so it is internally inconsistent and should not be cited for specifics.)

**EVIDENCE STRENGTH:** Weak. Vendor material, undocumented methodology, no thresholds.

**IMPLICATION FOR THE BUILD:** Useful only as an order-of-magnitude bracket: commercial providers think
roughly 1,000–1,200 names are worth ranking at all, which is consistent with a tradeable set one order
of magnitude below the 8,439 gross count and one order of magnitude above the mega-cap core.

---

### 4.5 No academic liquidity-tier census exists

**CLAIM:** No peer-reviewed study was located that counts how many US optionable names clear an absolute
quoted-spread threshold with specified open interest at a specified maturity band.

**SOURCE:** Searches across the option-liquidity literature returned relative-tercile and relative-quintile
splits (Goyal & Saretto 2009; Cao & Han 2013; Christoffersen et al. 2018) but no absolute-threshold census.
Academic samples report *relative* liquidity groupings within an OptionMetrics universe after arbitrage
and staleness filters, which is a different quantity.

**EVIDENCE STRENGTH:** **No credible evidence found.**

**IMPLICATION FOR THE BUILD:** The universe number must be derived, and the derivation must be shown and
flagged as an estimate. It also means **the tool should measure its own universe** — computing the count
of names clearing its gate each month is a cheap, genuinely novel, and directly decision-relevant output
that the literature does not provide. This is a real product opportunity rather than a gap to apologise for.

---

### 4.6 Derivation

| Step | Count | Basis |
|---|---|---|
| Listed US equity symbols | ~12,134 | SEC staff note, end-2025 **[REG]** |
| Had ≥1 option trade in 2025 | 8,439 (69.5%) | SEC staff note **[REG]** |
| Carry continuously listed multi-expiry chains | ~3,000–4,000 | Inferred: OptionMetrics-style studies average ~1,514 stocks/month passing arbitrage and staleness filters (Cao & Han) from a 6,000-stock pool; vendor rankings cover ~1,200 |
| Vendor-rankable on volume + OI + spread | ~1,000–1,200 | Tim's Stock Lists **[VEN]** |
| Clear a <5%-of-premium *quoted* spread with meaningful OI at 42–180 DTE | **~150–400, central estimate ~250** | Derived below |
| Practically liquid core (institutional-grade execution) | ~27–50 | Cboe: 27 names = 53.4% of market volume **[VEN/REG]**; SEC: top 10 = 31.7% **[REG]** |

**Reasoning for the 150–400 band.** Four independent anchors bracket it.

1. **From the S&P 500 effective-spread evidence.** Christoffersen et al. measure average relative
   effective spreads of 6.41% (ATM calls) and 5.25% (ATM puts) across S&P 500 constituents in 2004–2012.
   The *quoted* spread is wider than the effective spread. If the average S&P 500 name is at or above
   5% of premium on an effective basis at ATM, then a <5%-of-premium *quoted* threshold is binding
   *within* the S&P 500 — it does not merely exclude small caps. Taken alone this anchor would put the
   count well below 500, perhaps in the low hundreds. Two adjustments loosen it: spreads have tightened
   since 2012 in the liquid names (SEC: top-10 equity effective spread 1.3% → 0.9%), and the 42–180 DTE
   maturity band has a mechanically larger premium denominator than the volume-weighted average contract.
   Both push the count up, but neither is quantified in a located source.

2. **From concentration.** 27 names carry 53.4% of market volume and the top 10 carry 31.7%. Volume
   distributions of this shape typically have a long tail in which the 250th-ranked name has roughly two
   to three orders of magnitude less volume than the 1st. The SEC's own bucket structure stops at
   "251st and over," which is a reasonable signal that the agency's analysts regard rank ~250 as the
   boundary of the meaningfully active set.

3. **From the liquidity-decay evidence.** Spreads widened in every bucket outside the top 10 between
   2012 and 2025. Whatever the count was on 2012 data, it is lower now in the 11th–250th range. This
   argues for the lower half of the band and for re-measuring rather than trusting any static number.

4. **From the academic filters.** Cao & Han's monthly average of ~1,514 stocks passing basic arbitrage
   and staleness filters is an upper bound on names with usable quotes, and that is before any spread or
   open-interest threshold. Goyal & Saretto's most-liquid tercile of 3,885 stocks is ~1,295 names, but a
   relative tercile is not an absolute threshold and their own net results show the medium tercile
   already losing most of the edge at full quoted spread.

**Stated estimate: approximately 250 US single names, with a defensible range of 150–400,** clear a
quoted spread under 5% of premium with meaningful open interest in the 42–180 DTE band at any given time.
Of these, perhaps 30–60 are comfortable to trade in retail size with limit orders working inside the
spread, and the remainder require patience and partial fills.

**Uncertainty.** This is a derived estimate, not a measured one, and the uncertainty is large and
asymmetric. The downside risk is greater than the upside: three of the four anchors push toward the
low end, and the one that pushes high (the maturity/premium-denominator effect) is unquantified in any
located source. A plausible pessimistic case is 100–150 names. The estimate is also not stable over
time — it will contract in low-volatility regimes, when premiums shrink and percentage spreads widen
mechanically, and expand in high-volatility regimes. **The build should treat the universe size as a
measured monthly output, not a configuration constant.**

**Is 250 names enough to support a watchlist product?** Yes, with a caveat. 250 names is more than
enough for a single-user tool that holds a handful of positions at a time; diversification benefit
plateaus well before 250. The caveat is that the 250 are strongly tilted toward large-cap, low-IVOL,
high-institutional-ownership, heavily-covered names — precisely the segment where Part 2 found no
evidenced positive premium. **The universe is large enough; it is just not obviously the right universe.**

---

## PART 5 — WEEKLIES VERSUS MONTHLIES IN SINGLE NAMES

**CLAIM:** The number of single-name underlyings with listed weekly options could not be established
from primary sources.

**SOURCES ATTEMPTED:**
- Cboe "Available Weeklys" page: the equity and ETP sections render with headings but no rows; only 10
  unique index symbols were retrievable (DJX, VIX, SPXO, SPX, XSP, NANOS, OEX, XEO, RUT, SPEQX).
  https://www.cboe.com/available_weeklys **[VEN/REG]**
- Cboe Weeklys symbol directory: table headers present, no rows retrievable.
  https://www.cboe.com/us/options/symboldir/weeklys_options/ **[VEN/REG]**
- Options Industry Council FAQ: states each exchange may list weekly series on "a limited number of
  classes" and that exchanges typically select the most actively traded options for the extended weekly
  program, but gives no count and no formal eligibility criteria.
  https://www.optionseducation.org/referencelibrary/faq/weekly-options **[VEN]**
- OCC Weekly and Quarterly Options data page referenced but not retrievable in session.
- Direct CSV retrieval from cboe.com was blocked by the session's egress policy.

**EVIDENCE STRENGTH:** **No credible evidence found** for a count. Moderate evidence for the qualitative
selection rule (exchanges list weeklys on the most actively traded classes).

**IMPLICATION FOR THE BUILD:** The qualitative rule is actually the useful part. Because exchanges grant
weeklys to the most actively traded classes, **"has listed weeklys" is a free, exchange-curated liquidity
certification** — it encodes the exchanges' own judgement about which names sustain active option
trading. For a tool that needs a cheap first-pass liquidity gate, this is an excellent and almost
costless filter, and it is more defensible than any threshold the build could invent. The count itself
should be measured from the user's own data feed at build time.

**CLAIM:** No credible evidence was found on whether standard third-Friday monthly expiries are
materially more liquid than weekly expiries in single names at comparable maturities.

**EVIDENCE STRENGTH:** **No credible evidence found.** Searches returned only practitioner blog material
with no data. Two indirect considerations are recorded without supporting evidence: weekly open interest
expires every week (OIC), so standing open interest cannot accumulate in weekly series the way it does in
the quarterly third-Friday cycle; and LEAPS and quarterly cycles anchor on third Fridays, so hedging and
roll flow concentrates there.

**IMPLICATION FOR THE BUILD:** Constraining to standard third-Friday expiries is **weakly supported by
mechanism and not by evidence**, but it is close to costless. At 42–180 DTE there are always third-Friday
expiries available in the target band, and restricting to them reduces the search space, concentrates on
the series most likely to carry accumulated open interest, and avoids the thin weekly series at distant
maturities that exist only as skeleton listings. Recommend adopting it as a default with a documented
note that the evidence is mechanistic rather than empirical.

---

## PART 6 — EARNINGS-CYCLE STRUCTURE AT 42–180 DTE

### 6.1 The arithmetic

US issuers report quarterly, so the gap between announcements averages about 91 days. A 42-DTE holding
period spans one announcement with probability roughly 42/91 ≈ 46%; a 90-DTE period contains almost
exactly one announcement; a 180-DTE period contains two. **At the brief's horizon, earnings exposure is
not an edge case to be filtered — it is the dominant discrete risk in nearly every position**, and for
the upper half of the DTE range it is doubled. No source is required for this; it follows from the
reporting calendar. The practical implication is that position-level earnings exposure is unavoidable at
this horizon and must be priced rather than avoided, which makes the question of *where in the cycle to
enter* genuinely load-bearing.

### 6.2 The documented negative case (confirming prior strands)

**CLAIM:** Retail investors buy options into earnings announcements with high expected announcement
volatility, driving pre-announcement implied variance about 40% higher than for comparable announcements
with no retail buying; straddles on high-EAV announcements underperform low-EAV ones by about 11% on the
announcement day (t = 19.44) plus about 9% over the following 10 days; retail investors lose 5–9% of
option investments around earnings on average and 10–14% for high-EAV announcements, about $3bn in total
over the sample once spreads are included; and they pay roughly 9% in half-spreads before high-EAV
announcements.

**SOURCE:** Tim de Silva, Eric C. So & Kevin Smith, "Losing is Optional: Retail Option Trading and
Expected Announcement Volatility," working paper, draft 4 March 2024 (first draft January 2022).
**[WP]** https://ide.mit.edu/wp-content/uploads/2024/03/Retail_Options.pdf
Also recorded: retail dollar option volume rose from about $20bn in 2010 to about $240bn in 2020; market
makers absorb most of this demand; retail investors are slow to close losing positions, option prices
keep decaying, and the paper finds no reversal.

**EVIDENCE STRENGTH:** Strong. Large, recent, identifies retail flow directly, reports costs explicitly.

**IMPLICATION FOR THE BUILD:** Confirms the prior strands' finding that buying premium into an
announcement is the best-documented retail loss, and supplies the cleanest cost datapoint in the strand:
**a 9% half-spread means an 18% round trip before high-EAV announcements**, at the top of the brief's
8–20% range. Note the composition: the ~9% post-announcement underperformance of high-EAV straddles over
the following 10 days is where the post-earnings opportunity lives, and it is documented here as a
*continuation*, not a reversal.

### 6.3 The post-earnings window — positive evidence, in the opposite direction to the brief's hypothesis

**CLAIM:** Straddles bought *after* earnings announcements earn returns more negative than straddles in
firms with no nearby announcement; straddles bought *before* announcements earn about +5.1%; the
long-short portfolio earns about 14.4% over a one-month holding period; combining the announcement-timing
signal with the historical-minus-implied volatility spread raises the hedge return to 29.2% against 13.7%
for the volatility spread alone; and executed at the offer and sold at the bid the two-way strategy still
returns about 14.9% (HV-IV version) and about 9.4% (prior-month volatility version).

**SOURCE:** Sung Gon Chung & Henock Louis, "Earnings announcements and option returns," *Journal of
Empirical Finance*, 2017, 40: 220–235. DOI: 10.1016/j.jempfin.2016.07.010 **[PR]**
The authors attribute the pattern to traders underestimating volatility before announcements (especially
after calm periods) and overestimating it after announcements (especially after volatile periods), and
suggest recency bias as a mechanism. Their stated conclusion is that **post-announcement options appear
expensive** and pre-announcement options appear cheap. They also note single-factor strategies — the
volatility spread alone or announcement timing alone — shrink to small returns after costs.

**EVIDENCE STRENGTH:** Strong for the direction (peer-reviewed, explicit offer/bid execution);
Moderate for magnitude in a retail context, because the headline figures are long-short and the
cost-surviving versions are two-way strategies combining both legs.

**IMPLICATION FOR THE BUILD:** **This is the most important constructive finding in the strand, and it
inverts the brief's hypothesis.** The brief asked whether post-earnings implied volatility is
systematically *cheap* once the event premium has collapsed. The answer from the only peer-reviewed
study that tests it directly is **no — post-earnings options are systematically expensive**, and that is
precisely what a premium-selling tool wants. The post-announcement window is the best-evidenced *selling*
window in single-name options, not a buying window.

Three serious caveats must travel with this finding.
(a) Chung & Louis's +5.1% for pre-announcement straddle buyers contradicts the prior strands' conclusion
(and de Silva et al.'s evidence) that buying into announcements is the clearest retail loss. The conflict
is partly reconcilable — de Silva et al. condition on *high expected announcement volatility* and on
retail buying pressure, which is where overpricing concentrates, whereas Chung & Louis average across all
announcements — but it is not fully resolved. **The build should take only the short-after-announcement
leg and should not act on the long-before-announcement leg**, which is contradicted by better-identified
evidence and is in any case the documented retail loss pattern.
(b) The cost-surviving returns (14.9% / 9.4%) are for the *combined* two-way strategy. The isolated
short-after-announcement leg's net return is not separately reported, and the authors state that
single-factor versions shrink to small returns after costs. The honest expectation for a seller-only
implementation is therefore considerably below 14.9%.
(c) The mechanism is conditional: overestimation after announcements is strongest after *volatile*
periods. The build should condition the post-earnings sell signal on the pre-announcement realised-vol
environment rather than applying it uniformly.

---

**CLAIM:** ATM implied volatility rises from a mean of 49.3% at day −20 to a peak of 53.2% at day −1,
holds near 52.4% on announcement day, and falls to 49.1% on day +1 — i.e. the post-announcement collapse
returns implied volatility to approximately its pre-run-up baseline rather than below it.

**SOURCE:** Yuhang Xing & Xiaoyan Zhang, "Anticipating Uncertainty: Straddles Around Earnings
Announcements," working paper, 22 April 2013. **[WP]**
https://www.ruf.rice.edu/~yxing/straddle_201305_03.pdf
Also recorded: delta-neutral straddles lose 0.19%/day and 2.09%/week across all trading days
(equal-weighted); pre-announcement straddle buys earn 2.22% over [−5,0], 3.00% over [−3,0] and 2.30%
over [−1,0] with t-statistics above 15; straddles on low-IV firms (mean IV 29.8%) return 3.65% against
1.90% for high-IV firms (mean IV 75.0%), a 1.75% gap with t = −4.52; **the median relative bid-ask spread
is about 10%, rising to about 12% around announcements**; assuming realised spreads of 50% and 100% of
quoted, buy-and-hold straddles with 4–10 days to expiration earn 1.64%/day (t = 5.14) and 0.61%/day
(t = 2.08) respectively, while longer-maturity groups earn lower or negative returns.

**EVIDENCE STRENGTH:** Moderate (working paper) but the IV path is a clean descriptive fact and the
spread figures are directly useful.

**IMPLICATION FOR THE BUILD:** Two points. First, the IV path **rules out the "post-earnings IV is
unusually cheap" hypothesis on its own terms** — the crush restores the baseline, it does not undershoot
it. Combined with Chung & Louis, the correct picture is that post-earnings IV sits at its normal level
while remaining above subsequent realised volatility, which is a seller's condition. Second, the
~10% median relative bid-ask spread rising to ~12% around announcements independently corroborates the
brief's 8–20% cost hurdle and the Christoffersen et al. effective-spread figures. Third, the authors'
own finding that longer-maturity straddles earn lower or negative returns after costs is another
maturity warning consistent with Bali et al.

---

**CLAIM:** Weekly straddles around earnings have a mean return of 0.48% (not significantly different
from zero) and a median of −17.69%, and the only signal of five tested that predicts them is the gap
between a firm's average past earnings-day absolute move and its option-implied move.

**SOURCE:** Jonathan A. Milian, "The Efficiency of Weekly Option Prices around Earnings Announcements,"
*Journal of Risk and Financial Management*, 2023, 16(5): 270. DOI: 10.3390/jrfm16050270 **[PR]**
Sample: 2,690 quarterly announcements by firms with weekly options, Q1 2014 – Q1 2017 (13 quarters).
Quintile 1 of the AvgEA-Implied signal averages −5.42%/quarter (significant at 1%); quintile 5 averages
+8.78% (p = 0.106); hedge portfolio 14.20%/quarter (t = 2.72). Four other signals — historical
volatility, historical earnings-move volatility, implied volatility, and historical-minus-implied
volatility — show no significant predictive power. Returns use midpoint prices and are gross of costs;
mean quoted half-spread 7.4%, median 3.7%. The author notes straddles have large bid-ask spreads and
that transaction costs could erase profits.

**EVIDENCE STRENGTH:** Moderate. Peer-reviewed but a short 13-quarter sample, a low-impact journal, and
returns are gross of costs.

**IMPLICATION FOR THE BUILD:** Chiefly a negative result worth recording: of five candidate earnings
signals, the *historical-minus-implied volatility spread* — the Goyal–Saretto workhorse — had **no**
predictive power for earnings-window straddles. That is a specific warning against assuming the general
richness signal transfers to the earnings window. The one signal that did work compares the implied move
to the firm's own history of earnings-day moves, which is a straightforward and cheap computation and
worth including as a distinct earnings-specific input rather than folding earnings into the general
richness score. Note the median return of −17.69% against a mean of 0.48%: the distribution is violently
right-skewed, which is the characteristic signature of short-premium-style payoffs and a reminder that
mean returns in this space are driven by tails.

---

## PART 7 — ASSIGNMENT AND DIVIDEND MECHANICS AS A SELECTION FILTER

**CLAIM:** Early exercise of American equity options occurs at scale and is predominantly rational:
1.8 billion options were early-exercised with total exercise value of $36.3bn against intrinsic value of
$22.8bn; 66–84% of early-exercise decisions occur when the stock is above the model's optimal exercise
boundary (86–98% for market makers, with the most conservative assumptions explaining 98% of market
makers' exercises); and the cumulative 20-trading-day exercise probability is 20.7% when the stock is
above the boundary against 0.4% when below.

**SOURCE:** Mads Vestergaard Jensen & Lasse Heje Pedersen, "Early Option Exercise: Never Say Never,"
working paper versions March 2012 / October 2014; subsequently *Journal of Financial Economics*, 2016,
121(2): 278–299. **[WP, later PR]**
https://w4.stern.nyu.edu/facdir/lpederse/papers/NeverSayNever.pdf
The quoted figures are for *non-dividend-paying* stocks, deliberately chosen to isolate frictions-driven
violations of Merton's rule; the authors note that including dividend payers would increase the early-
exercise count. Their base-case model implies early exercise becomes optimal at 1.67× the strike a
quarter before expiry and 1.27× the strike 10 days before expiry. Period reported inconsistently in the
source (introduction says 2003–2010; data section says July 2001 – September 2008).

**EVIDENCE STRENGTH:** Strong for the scale and rationality of early exercise; the dividend case is
explicitly excluded from these numbers.

**IMPLICATION FOR THE BUILD:** Two directly usable facts. First, **early assignment is overwhelmingly a
deep-in-the-money phenomenon** — 20.7% over 20 days above the optimal boundary versus 0.4% below it. A
short option that stays out of the money or near the money carries negligible assignment risk, and the
boundary multiples (1.67× strike at a quarter out, 1.27× at 10 days) give a usable, if model-dependent,
threshold. Second, market makers exercise near-optimally (86–98%), so a retail short position faces a
sophisticated counterparty and should not rely on counterparty inattention. The useful screening rule is
therefore not about the name but about the position's moneyness and remaining time value.

---

**CLAIM:** Early assignment of a short call becomes likely when the call is in the money and the upcoming
dividend exceeds the call's remaining time value, with exercise typically occurring the day before the
ex-dividend date; the most at-risk profile is an in-the-money call with little remaining extrinsic value.

**SOURCE:** Fidelity Learning Center, "How dividends can increase options assignment risk."
**[VEN — broker educational material, not a formal result]**
https://www.fidelity.com/learning-center/investment-products/options/dividends-options-assignment-risk
The article's worked example involves a call $1 in the money with 10 days to expiration, and it warns that
assignment can occur earlier than the day before ex-dividend. Mitigations it lists: track dividend and
ex-dividend dates; avoid selling calls on dividend payers where the trade spans an ex-dividend date; or
use European-style options. No numeric threshold or maturity cutoff is given.

**EVIDENCE STRENGTH:** Weak as a source type (broker education), but the underlying rule — exercise when
the dividend exceeds remaining time value — is standard no-arbitrage option theory and is not in dispute.

**IMPLICATION FOR THE BUILD:** The rule is cheap to implement and should be implemented as a *position-
level* check rather than a name-level exclusion:
`assignment_flag = (option is ITM) AND (upcoming dividend > remaining extrinsic value) AND (ex-date falls
before expiry)`.
**Excluding high-dividend names wholesale is the wrong design.** At 42–180 DTE, remaining extrinsic value
is large relative to a single quarterly dividend for anything but deep-ITM strikes — a 90-DTE ATM option
on a $100 stock at 30% vol carries roughly $6 of extrinsic value against a typical quarterly dividend
well under $1 — so the condition rarely binds at this horizon and only becomes live as expiry approaches
or if the position moves deep in the money. A blanket high-dividend exclusion would therefore discard a
large and liquid slice of the investable universe (utilities, staples, financials, energy) to avoid a risk
that is mostly dormant at the target maturity. The correct design is a dated, position-level warning that
escalates as extrinsic value decays, plus a hard rule against holding short ITM calls through an ex-date
when the dividend exceeds extrinsic value. Note also that Bakshi & Kapadia's single-name IV−RV gap fell
from 1.5 to 1.07 vol points once dividend-affected options were removed, which is a reminder that
dividends contaminate measurement as well as creating assignment risk — the tool's richness computation
should handle discrete dividends explicitly rather than relying on continuous-yield approximations.

---

## SINGLE-NAME VRP VERDICT

**There is a small average variance risk premium in single-name equity options, it is roughly a third to
a half the size of the index premium, it is dwarfed by its own cross-sectional dispersion, and after
realistic single-name transaction costs it is approximately zero for the typical name and plausibly
negative for the names a richness screen would select.**

The magnitude, stated three ways from the three largest and best-identified studies:

| Measure | Single names | Index | Source |
|---|---|---|---|
| ATM IV − realised vol | +1.5 vol pts (25 stocks); +1.07 dividend-clean | +3.3 vol pts | Bakshi & Kapadia 2003 **[PR]** |
| Model-free IV − realised vol | **−1.35 vol pts** (38.56% vs 39.91%, 135 stocks) | +3.77 (24.79% vs 21.02%) | Driessen, Maenhout & Vilkov, *JF* 2009 **[PR]** |
| Delta-hedged call gain, ~50 days | −1.13% mean / −0.77% median of position (~6,000 stocks) | n/a | Cao & Han, *JFE* 2013 **[PR]** |
| Delta-hedging loss, % of underlying | 0.03% | 0.07% | Bakshi & Kapadia 2003 **[PR]** |

Two of the three say the premium is real but small; one — on the measure closest to what a vol seller
actually captures across the whole surface — says it is *negative on average* and statistically
indistinguishable from zero for 108 of 135 stocks. **That disagreement is not resolved in the literature
and should not be resolved by the build in its own favour.**

**Applying the cost hurdle.** Take the most favourable credible estimate: the median name's delta-hedged
gain of 0.77% of position per ~50 days, accruing to the seller. Against that:

- Average relative effective spread on ATM options among **S&P 500 constituents**: 6.41% calls / 5.25%
  puts (Christoffersen et al., *RFS* 2018). Round trip ≈ 10–13% of premium.
- Median relative bid-ask spread on single-name straddles: ~10%, ~12% around earnings (Xing & Zhang).
- Retail half-spread before high-EAV announcements: ~9%, i.e. ~18% round trip (de Silva, So & Smith).
- The brief's own figure: 8–20% of premium at 42–48 DTE.

A 90-DTE ATM option carries roughly 5–6% of the underlying in premium. A 10% round-trip spread therefore
costs about 0.5–0.6% of the underlying. The median name's premium, scaled comparably, is of the same
order. **The edge and the cost are the same size at the median name.** The only populations where the
net result is reliably positive are Goyal & Saretto's low-spread tercile (straddle 10−1 of 8.2% at full
quoted spread, delta-hedged puts 1.2%) — and those are the names where the gross premium is *smallest*
(18.0% gross versus 23.9% in the high-spread tercile).

**Three further discounts must be applied before believing any of it.**

1. **Measurement.** Every OptionMetrics-based estimate here uses 4pm closing midpoints, which Goyenko &
   Zhang show bias delta-hedged returns upward by 60 bp/month (1pm) to over 100 bp/month (10am) — the same
   order of magnitude as the entire measured premium.
2. **Decay.** The index premium collapsed around 2010–2012 and the brief's own prior work found
   delta-hedged equity option alpha went to zero after May 2012 and the Zhan et al. characteristics
   collapsed to 0.10%/month. No located study re-estimates the single-name VRP post-2012. Bali et al.
   find their strategy flat to negative in 2016–2019 at 25% costs.
3. **Maturity.** The one peer-reviewed study that splits by maturity and nets out costs finds options
   over 90 days do not survive a 25% effective spread, while those under 90 days do.

**In which names, then?** The literature's answer is high-idiosyncratic-volatility, small, illiquid,
low-coverage, low-institutional-ownership names (Cao & Han; Bali et al.; Shafaati et al.) — and
Goyal & Saretto show that is exactly the population where net returns go to zero or negative once the
spread is paid. **The intersection of "premium is positive" and "premium is capturable" is close to empty
in the published cross-section.**

**Verdict for the build.** Do not build a product whose thesis is "harvest the single-name variance risk
premium." The evidence does not support a positive expected net return from generic single-name premium
selling at retail costs. Build instead a product whose thesis is **cost-and-liquidity-first contract
selection within a narrow liquid universe**, where the richness score is a tie-breaker among contracts
that have already passed an exclusionary liquidity gate, and where the one differentiated, cost-surviving,
peer-reviewed edge — the post-announcement overpricing window — is the primary timing input. Expected net
edge should be presented to the user as "small, uncertain, and possibly zero," with the tool's main value
being the avoidance of documented losses (buying premium into announcements, trading illiquid contracts,
holding short ITM calls through ex-dates) rather than the capture of a premium.

---

## NAME-SELECTION CRITERIA

An ordered screen. Criteria 1–4 are **exclusionary gates** — a name that fails is removed from the
universe entirely and is never scored. Criteria 5–8 are **ranking inputs** applied only to survivors.

**GATE 1 — Quoted spread under 5% of premium on the target contract at 42–180 DTE.**
*Evidence:* Goyal & Saretto's high-spread tercile returns −0.8% (straddle) and 0.0–0.1% (delta-hedged) at
full quoted spread, against +8.2% and +1.2% in the low-spread tercile; gross returns are *higher* in the
illiquid tercile, so any gross-richness ranking actively selects failures. Christoffersen et al. show the
average S&P 500 ATM option is already at 5.25–6.41% effective, so this gate is binding inside the
large-cap universe and is not a formality. *Must be evaluated on the specific contract, not the name.*

**GATE 2 — Open interest and volume above an absolute floor in the specific series.**
*Evidence:* Goyal & Saretto's low-volume tercile nets 1.5% (straddle) and 0.2% (delta-hedged) at full
quoted spread. Note their split uses average daily dollar volume, not open interest; use both.

**GATE 3 — Has listed weekly options.**
*Evidence:* exchanges list weeklys on the most actively traded classes (Options Industry Council), making
this an exchange-curated liquidity certification obtained at zero cost. Weak evidence, zero cost,
strong mechanism. *Trade the monthlies; use weeklys existence only as the filter.*

**GATE 4 — Standard third-Friday expiry available in the 42–180 DTE window, and prefer it.**
*Evidence:* mechanistic rather than empirical — weekly open interest expires weekly (OIC) so standing
open interest accumulates in the monthly cycle, and quarterly/LEAPS flow anchors on third Fridays.
**No credible evidence found** for a measured liquidity advantage. Adopt as a near-costless default,
documented as unevidenced.

**GATE 5 — No short ITM call held through an ex-dividend date where the dividend exceeds remaining
extrinsic value.**
*Evidence:* standard no-arbitrage early-exercise condition (Fidelity **[VEN]**); Jensen & Pedersen show
20.7% 20-day exercise probability above the optimal boundary versus 0.4% below, and that market makers
exercise near-optimally (86–98%). **This is a position-level check, not a name-level exclusion** — at
42–180 DTE extrinsic value typically exceeds a quarterly dividend several times over, so excluding
dividend payers wholesale would discard a large liquid slice of the universe for a mostly dormant risk.

**RANK 6 — Realised-minus-implied volatility spread (name's own trailing realised vol versus current
implied).**
*Evidence:* the dominant predictor in Shafaati, Chance & Brooks (*JEF* 2026) and the Goyal–Saretto signal.
**Compute as a deviation from the name's own trailing level, refreshed continuously** — Saretto's
cross-sectional mean-reversion result says richness is transient, so a static watchlist is wrong by
construction. Caveat: Milian (*JRFM* 2023) finds this signal has **no** predictive power in the earnings
window specifically.

**RANK 7 — Turnover.**
*Evidence:* one of the three surviving predictors in Shafaati et al., and the only one whose effect is
reported as insensitive to information and arbitrage-cost proxies — i.e. the only one that does not look
like a limits-to-arbitrage artefact. **Weight it more heavily than its raw predictive power suggests, on
robustness grounds.**

**RANK 8 — Idiosyncratic volatility, applied *within* the gated universe only.**
*Evidence:* the strongest single predictor in the literature (Cao & Han: coefficient −0.0405, t = −15.5;
10th-to-90th percentile swing of 2.14 percentage points) but concentrated in small illiquid names
(effect halves when value-weighted; 1.63%/month in the smallest size quintile) and the authors interpret
it as mispricing from limits to arbitrage rather than a risk premium. Hu & Jacobs find the same direction
for total volatility level. **Never allow a high IVOL score to relax Gates 1–2** — that inverts the
strategy into Goyal & Saretto's loss-making tercile.

**RANK 9 — Position in the earnings cycle: prefer entries shortly after an announcement.**
*Evidence:* Chung & Louis (*JEF* 2017) — post-announcement options are expensive, long-short 14.4%/month,
and 14.9%/9.4% executed at offer/bid; de Silva, So & Smith — high-EAV straddles underperform by a further
~9% over the 10 days *after* the announcement with no reversal. Condition on the pre-announcement realised
vol environment, since overestimation after announcements is strongest following volatile periods.
**Take only the short-after leg; do not take the long-before leg** (contradicted by de Silva et al. and by
the brief's prior strands).

**RANK 10 — Earnings-move signal: the firm's average past earnings-day absolute move versus the current
option-implied move.**
*Evidence:* Milian (*JRFM* 2023) — the only one of five earnings signals with predictive power; hedge
portfolio 14.20%/quarter gross (t = 2.72). Gross of costs, 13-quarter sample, low-impact journal.
Treat as exploratory.

**CONTEXT INPUT (not a name criterion) — market-wide implied correlation (COR1M/COR3M) as a regime
filter.** *Evidence:* Cboe methodology is market-level only and provides no per-stock decomposition;
DMV show implied correlation runs ~63% above realised (46.68% vs 28.68%) and that the index VRP *is* the
correlation risk premium. Use to decide whether to be selling single-name premium at all this month;
**do not use as a cross-sectional selector**, for which **no credible evidence was found.**

**Deliberately excluded for lack of evidence:** index membership as a richness signal (Coakley et al.
2024 studies implied betas, not option richness — use membership only as a size/coverage proxy in
universe construction); analyst coverage and institutional ownership as richness signals (Bali et al.
report these gross only, and the sign favours *low* coverage, i.e. illiquid names); beta and systematic
share of variance (Bakshi & Kapadia find market vol priced and firm vol unpriced, but Gourier finds the
opposite with idiosyncratic variance at ~80% of the total — **unresolved, do not trade on it**).

---

## TRADEABLE UNIVERSE ESTIMATE

**Approximately 250 US single names, with a defensible range of 150–400.** These are names that at any
given time have at least one 42–180 DTE contract clearing a quoted spread under 5% of premium with
meaningful open interest. Of those, roughly 30–60 are comfortable to trade in retail size.

Derivation (full table in Part 4.6):

| Layer | Count | Basis |
|---|---|---|
| Listed US equity symbols | ~12,134 | SEC staff note, end-2025 **[REG]** |
| ≥1 option trade in 2025 | 8,439 (69.5%) | SEC staff note **[REG]** |
| Continuously listed multi-expiry chains | ~3,000–4,000 | Inferred from OptionMetrics filter yields |
| Vendor-rankable on volume + OI + spread | ~1,000–1,200 | Tim's Stock Lists **[VEN]** |
| **Clear <5% quoted spread with meaningful OI at 42–180 DTE** | **~250 (150–400)** | Derived |
| Institutional-grade execution core | ~27–50 | Cboe: 27 names = 53.4% of volume **[VEN/REG]** |

Four anchors, three of which push toward the low end:
1. Christoffersen et al.'s S&P 500 ATM effective spreads of 5.25–6.41% mean the 5% gate binds *within*
   the S&P 500, not merely below it.
2. 27 names carry 53.4% of volume and the top 10 carry 31.7%; the SEC's own bucket structure terminates at
   "251st and over," a reasonable signal that rank ~250 bounds the meaningfully active set.
3. Spreads widened in every bucket outside the top 10 between 2012 and 2025 (effective spreads up
   0.5–1.5 pp) — the count is lower now than on the academic samples.
4. Cao & Han's ~1,514 stocks per month passing basic filters is an upper bound on names with usable
   quotes, before any spread or OI threshold.

The one anchor pushing up is structural and favourable: **percentage-of-premium spreads improve
mechanically with maturity**, because the premium denominator grows faster than the nominal spread. A
90-DTE ATM option on a $100 stock at 30% vol carries ~$6.00 of premium, so a 10¢ nominal spread is 1.7%
of premium where the same 10¢ on a $0.50 weekly is 20%. Published volume-weighted spread statistics are
dominated by short-dated contracts (36% of all volume is 0DTE) and therefore understate the 42–180 DTE
band's quality. **No source quantifies this adjustment**, which is the largest single source of
uncertainty in the estimate and the first thing the build should measure.

**Uncertainty:** large and asymmetric to the downside. A pessimistic case is 100–150 names. The figure is
also regime-dependent — it contracts in low-volatility regimes as premiums shrink and percentage spreads
widen mechanically, and expands in high-volatility regimes. **The build should treat universe size as a
measured monthly output, not a configuration constant.** No peer-reviewed absolute-threshold census of
the optionable universe exists (**no credible evidence found**), so the tool computing this count each
month would be a genuinely novel and directly decision-relevant output.

**Is it enough for a watchlist product?** Yes in count — 250 names far exceeds what a single-user tool
holding a handful of positions needs, and diversification benefit plateaus long before 250. But the 250
are tilted toward large-cap, low-IVOL, heavily-covered, institutionally-held names, which is exactly the
segment where Part 2 found no evidenced positive premium. **The universe is large enough; the problem is
that it is not obviously the right universe.**

---

## POST-EARNINGS OPPORTUNITY

**Yes — there is genuine evidential support, but in the opposite direction to the brief's hypothesis, and
it favours selling rather than buying.**

The brief asked whether post-earnings implied volatility is systematically *cheap* once the event premium
has collapsed. Both relevant sources say it is not:

1. **Chung & Louis (*Journal of Empirical Finance* 2017, peer-reviewed):** straddles bought *after*
   announcements return *more negative* than straddles in firms with no nearby announcement. Their stated
   conclusion is that post-announcement options appear **expensive**. Long-short (buy before / sell after)
   = 14.4% over one month; combined with the HV-IV spread = 29.2% versus 13.7% for the spread alone; and
   executed at the offer and sold at the bid the two-way strategy still returns **14.9%** (HV-IV version)
   and **9.4%** (prior-month vol version). Mechanism: traders overestimate volatility after announcements,
   especially following volatile periods — recency bias.
2. **de Silva, So & Smith (working paper 2024):** high-EAV straddles underperform low-EAV straddles by
   ~11% on announcement day **plus a further ~9% over the following 10 days**, with option prices
   continuing to decay and **no reversal**. The post-announcement decay is documented as a continuation.
3. **Xing & Zhang (working paper 2013):** ATM IV runs 49.3% at day −20 → 53.2% at day −1 → 49.1% at day
   +1. The crush restores the baseline; it does not undershoot it. This independently **rules out the
   "post-earnings IV is cheap" hypothesis** while being consistent with post-earnings IV remaining above
   subsequent realised vol.

**Why this matters for the build.** It is the only cost-surviving, peer-reviewed, single-name-specific
edge located in this strand. Chung & Louis report returns at *full quoted* execution (offer to bid), which
is a far more demanding test than the midpoint figures that dominate this literature. And it is a timing
rule rather than a cross-sectional bet, so it does not require the richness persistence that Saretto's
mean-reversion result denies.

**Four caveats that must travel with it.**
1. **Only the short-after leg is usable.** Chung & Louis's +5.1% for pre-announcement straddle *buyers*
   contradicts de Silva et al. (who condition on high expected announcement volatility and retail buying
   pressure) and the brief's prior strands. The conflict is partly reconcilable — Chung & Louis average
   across all announcements whereas de Silva et al. isolate the overpriced subset — but it is unresolved.
   Take the sell-after leg only.
2. **The cost-surviving figures are for the two-way strategy.** The isolated short-after leg's net return
   is not separately reported, and the authors state that single-factor versions shrink to small returns
   after costs. Expect materially less than 14.9%.
3. **The effect is conditional.** Post-announcement overestimation is strongest after volatile periods.
   Condition the signal on the pre-announcement realised-vol environment rather than applying it uniformly.
4. **The general richness signal does not transfer.** Milian (*JRFM* 2023) finds the
   historical-minus-implied volatility spread has **no** predictive power in the earnings window. Use the
   earnings-specific signal (average past earnings-day move versus current implied move) instead of
   assuming the general score works there.

**Horizon fit.** At 42–180 DTE a position spans roughly one announcement at 90 DTE and two at 180 DTE, so
earnings exposure is unavoidable and must be priced rather than filtered. The practical rule that follows:
**enter shortly after an announcement, size so that the next announcement is survivable, and prefer the
42–90 DTE sub-band** — which both contains exactly one announcement cycle and is the maturity band Bali
et al. show surviving a 25% effective spread.

---

## DISCONFIRMING EVIDENCE

1. **The single-name variance premium may be negative, not positive.** Driessen, Maenhout & Vilkov
   (*JF* 2009) find average model-free implied volatility of 38.56% against realised 39.91% across 135
   stocks — implied *below* realised — and cannot reject a zero premium for **108 of 135 stocks** at the
   5% level. Of the 27 rejections only 16 are positive. This is the cleanest large-sample statement on the
   measure closest to what a vol seller captures, and it says there is nothing there for most names.

2. **The only clearly priced risk in the equity-vol complex sits in the index leg, and the retail
   single-name seller is on the wrong side of it.** DMV attribute the *entire* index variance risk premium
   to priced correlation risk and find individual variance risk unpriced; index puts earn roughly −7% to
   −39% per month *relative to* individual puts. A tool constrained to individual tickers is by
   construction trading the leg without the robust premium.

3. **A measurement artefact may account for much of the measured premium.** Goyenko & Zhang show
   delta-hedged equity-option returns from 4pm closing midpoints are biased upward by ~60 bp/month versus
   1pm and >100 bp/month versus 10am; using 10am quotes, the equity-versus-index call return differential
   largely disappears. Every OptionMetrics study cited here uses 4pm midpoints, so **the entire
   literature's single-name estimates share a common upward bias of the same order of magnitude as the
   premium itself.**

4. **Cross-sectional richness mean-reverts; it does not persist.** Saretto's predictability result is
   explicitly mean reversion — names with IV below their own 12-month average and the cross-sectional
   average see IV *rise*. A static "rich options" watchlist is a list of names about to stop being rich.
   His Table 11 shows that recomputing option prices with the cross-sectional volatility forecast makes
   the strategy's returns insignificant, i.e. the apparent richness largely reflects information the naive
   signal ignores.

5. **Every predictor of richness is also a predictor of uncapturability.** Cao & Han's IVOL effect halves
   when value-weighted and is strongest in the smallest size quintile; Shafaati et al. report the IVOL
   effect intensifies when trading frictions and hedging costs are high; Bali et al. find predictability
   strongest where the underlying is illiquid and coverage and institutional ownership are low. Goyal &
   Saretto show those are the names where net returns go to zero. **No characteristic has been shown to
   predict a positive premium among liquid large caps** — the only universe a retail account can transact.

6. **The liquidity gate is confirmed as fully exclusionary, and gross richness actively selects failures.**
   Goyal & Saretto at full quoted spread: high-spread tercile straddle 10−1 = **−0.8%**, delta-hedged calls
   **0.0–0.1%**, delta-hedged puts **0.0%**; low-volume tercile delta-hedged **0.2%**. Gross returns are
   *higher* in the illiquid terciles (23.9% vs 18.0%), so a screen that ranks on gross richness
   systematically picks the contracts where the edge does not survive execution.

7. **Costs are worse than the brief's lower bound even among the largest names.** Christoffersen et al.
   measure average relative *effective* spreads of 6.41% (ATM calls) and 5.25% (ATM puts) across **S&P 500
   constituents** — a 10–13% round trip. The authors' own reading is that the illiquidity premium
   compensates *market makers*, and they state the alphas are not readily earned by investors who must pay
   the spread. Xing & Zhang put the median single-name straddle relative spread at ~10% (~12% around
   earnings); de Silva et al. put retail half-spreads at ~9% before high-EAV announcements (~18% round trip).

8. **The long half of the target horizon is specifically unsupported.** Bali et al. (*RFS* 2023) find
   options over 90 days become insignificant or negative at a 25% effective spread while those ≤90 days
   survive. Xing & Zhang likewise find longer-maturity straddles earn lower or negative returns after
   costs. **The 90–180 DTE portion of the brief's horizon is an evidence-free extrapolation.**

9. **Decay is live in single names even without a formal break test.** Bali et al.'s strategy is zero or
   slightly negative in 2016–2019 at a 25% effective spread. The brief's own prior strands found
   delta-hedged equity-option alpha went to zero after May 2012 and the Zhan et al. characteristics
   collapsed from 2.27% to 0.10%/month on pre-trade information. Meanwhile **no located study re-estimates
   the single-name VRP on post-2012 data at all.**

10. **The tradeable universe is narrowing, not broadening.** Despite options volume roughly quadrupling,
    the SEC staff note shows trade-weighted quoted spreads widened across **every** equity bucket outside
    the top 10 between 2012 and 2025, with effective spreads up 0.5–1.5 pp. Top-10 concentration rose from
    24.0% to 31.7%, and 27 names now carry 53.4% of volume. Execution quality improved only where it was
    already best.

11. **The 'idiosyncratic vol is unpriced' premise the brief treats as settled is contested.** Gourier
    (2016) finds idiosyncratic variance risk *is* persistently priced and constitutes ~80% of the total
    single-name premium (range 13–96%), directly contradicting Bakshi & Kapadia and DMV. This cuts both
    ways — it is better news for risk compensation and worse news for the brief's stated evidence base —
    but either way **the risk-framing of a short single-name vol position rests on an unresolved question.**

12. **Even the index premium is not robustly significant on modern data.** Heston & Todorov report the
    realised S&P 500 variance risk premium as not significantly different from zero over 2006–2020 once
    March 2020 is included (−11.9%/month full sample versus −22.9% pre-COVID). If the index premium — three
    times the size of the single-name premium on every measure here — is marginal, the single-name premium
    net of a 10–13% round trip is at best marginal.

13. **A specific negative result on signal transfer.** Milian (*JRFM* 2023) finds the
    historical-minus-implied volatility spread, the workhorse signal of this literature, has **no**
    predictive power for earnings-window straddles. Signals do not travel across contexts for free.

---

## OPEN QUESTIONS

1. **Has the single-name variance risk premium decayed post-2012 the way the index premium has?** The most
   important unanswered question in the strand. Dew-Becker & Giglio establish the index break around
   2010–2012 and attribute it to a shift in dealer net gamma driven by vol-selling supply that was
   concentrated in index products. Whether single names were insulated or followed is untested.
   **Actionable:** measure directly on recent data before committing to the product thesis.

2. **How much of the measured single-name premium survives intraday-accurate pricing?** Goyenko & Zhang's
   60–140 bp/month closing-quote bias is of the same order as the premium. No study re-estimates the
   single-name VRP using intraday marks. **Actionable:** the build should timestamp its own quotes intraday
   and treat any end-of-day backtest as an upper bound.

3. **What is the actual distribution of percentage-of-premium spreads at 42–180 DTE, by underlying?** The
   largest source of uncertainty in the universe estimate. Published statistics are volume-weighted and
   dominated by 0DTE and weekly contracts; the maturity adjustment is structurally favourable but
   unquantified in any located source. **Actionable and cheap to measure — and genuinely novel.**

4. **Is idiosyncratic variance risk priced or not?** Bakshi & Kapadia and DMV say no; Gourier says yes and
   dominant. This determines whether short single-name vol is compensated risk-bearing or uncompensated
   exposure, and therefore how it should be sized. Unresolved in the literature.

5. **What is the isolated net return to the short-after-earnings leg alone?** Chung & Louis report
   cost-surviving returns only for the combined two-way strategy and note single-factor versions shrink
   substantially. The build needs the one-sided figure and the literature does not provide it.

6. **How many single names have listed weeklys, and are monthly expiries measurably more liquid at
   comparable maturities?** Primary sources were not retrievable in session (Cboe directory pages rendered
   without rows; direct CSV blocked by egress policy). Both are straightforward to resolve with a data
   feed at build time.

7. **Can a beta-and-correlation-adjusted "name IV versus index-implied name IV" measure add anything?**
   No validated academic work located. The construct is appealing because it partly neutralises market-wide
   vol regime, but it is unvalidated and should be built, if at all, as an exploratory diagnostic.

8. **Does the post-earnings overpricing effect survive on post-2017 data?** Chung & Louis's sample predates
   the retail options boom (retail dollar option volume went from ~$20bn in 2010 to ~$240bn in 2020 per
   de Silva et al.). That flow could have either amplified the effect (more retail overpricing) or
   competed it away. Untested.

9. **Does the richness signal work at all within the gated liquid universe?** Every cost-adjusted liquidity
   split in the literature is a *relative* tercile within a broad sample, not an absolute-threshold subset.
   Whether the realised-implied spread retains predictive power among only the ~250 names that pass an
   absolute gate is, as far as located, untested — and it is the question the product most depends on.

10. **How much does retail limit-order execution improve on quoted spreads?** Both Bali et al. and Milian
    cite Muravyev & Pearson (2020) to the effect that traders who time executions pay far less than quoted
    spreads imply — Bali et al. note effective costs about a quarter lower than conventional estimates. If
    a patient retail trader working inside the spread achieves 25–50% of quoted rather than 100%, the
    Goyal–Saretto grid becomes materially more favourable. **This is the single most consequential
    uncertainty that is under the user's own control**, and the one worth the most careful measurement.

---

## TOP 10 SOURCES, RANKED

1. **Amit Goyal & Alessio Saretto, "Cross-Section of Option Returns and Volatility," *Journal of Financial
   Economics* 2009, 94: 310–326.** **[PR]**
   https://www.erim.eur.nl/fileadmin/erim_content/documents/10
   *The load-bearing source.* The only study giving net returns by both spread tercile and volume tercile
   at four cost levels, which is exactly the table needed to justify an exclusionary liquidity gate — and
   which shows gross richness is highest where net returns are zero or negative.

2. **Jie Cao & Bing Han, "Cross section of option returns and idiosyncratic stock volatility," *Journal of
   Financial Economics* 2013, 108: 231–249.** **[PR]**
   https://www-2.rotman.utoronto.ca/facbios/file/Han_JFE_published.pdf
   The largest sample (~6,000 stocks) and the only published stock-level percentile distribution of
   delta-hedged gains, which is the direct answer to the brief's central question about heterogeneity.
   Also supplies the strongest cross-sectional predictor and its cost grid.

3. **Joost Driessen, Pascal Maenhout & Grigory Vilkov, "The Price of Correlation Risk: Evidence from Equity
   Options," *Journal of Finance* 2009, 64: 1377–1406.** **[PR]**
   https://haas.berkeley.edu/wp-content/uploads/dmv_sept2005.pdf
   The strongest disconfirming source: single-name implied *below* realised, zero premium unrejectable for
   108 of 135 stocks, and the structural result that the index VRP *is* the correlation risk premium.

4. **SEC Staff, Office of Analytics and Research, "Roundtable on Options Market Structure — Supporting
   Data," 9 April 2026.** **[REG]**
   https://www.sec.gov/files/roundtable-options-market-structure.pdf
   The authoritative current universe and concentration data: 8,439 underliers, top 10 = 31.7%, and the
   critical finding that spreads widened everywhere outside the top 10 from 2012 to 2025.

5. **Turan Bali, Heiner Beckmeyer, Mathis Moerke & Florian Weigert, "Option Return Predictability with
   Machine Learning and Big Data," *Review of Financial Studies* 2023, 36: 3548–3602.** **[PR]**
   https://academic.oup.com/rfs/article/36/9/3548/7056660
   Largest and most recent cost-adjusted cross-section (7,046 underlyings, 1996–2020), and the only source
   splitting survival by maturity — the finding that >90 DTE fails at 25% costs directly constrains the
   brief's horizon.

6. **Peter Christoffersen, Ruslan Goyenko, Kris Jacobs & Mehdi Karoui, "Illiquidity Premia in the Equity
   Options Market," *Review of Financial Studies* 2018, 31: 811–851.** **[PR]**
   https://ruslangoyenko.com/wp-content/uploads/2019/09/illiquidity-premia-in-the-equity-options-market.pdf
   The hard cost anchor, measured from actual intraday executions rather than quotes: 6.41% / 5.25%
   effective relative spreads on ATM calls/puts *among S&P 500 constituents*, plus the authors' explicit
   statement that the illiquidity premium is not earnable by those who pay the spread.

7. **Sung Gon Chung & Henock Louis, "Earnings announcements and option returns," *Journal of Empirical
   Finance* 2017, 40: 220–235.** **[PR]**
   https://doi.org/10.1016/j.jempfin.2016.07.010
   The only cost-surviving, peer-reviewed, single-name-specific constructive edge located: post-announcement
   options are expensive, with returns reported at full offer-to-bid execution.

8. **Ruslan Goyenko & Chengyu Zhang, "Option Returns: Closing Prices are not What You Pay," working paper,
   McGill 2019.** **[WP]**
   https://ruslangoyenko.com/wp-content/uploads/2019/11/Option-Returns-Nov-18-2019-FINAL.pdf
   Ranked this high despite being unpublished because it potentially invalidates the measurement basis of
   every other source in this list: a 60–140 bp/month upward bias in delta-hedged returns from 4pm marks.

9. **Gurdip Bakshi & Nikunj Kapadia, "Volatility Risk Premiums Embedded in Individual Equity Options,"
   *Journal of Derivatives* 2003.** **[PR]**
   https://people.umass.edu/~nkapadia/docs/Bakshi_Kapadia_JoD_Fall_2003.pdf
   The original benchmark — 1.5 vs 3.3 vol points, 14/25 negative, 4 significantly positive. Retained for
   the heterogeneity result and the 0.03%-vs-0.07%-of-underlying scaling, though superseded in sample size.

10. **Tim de Silva, Eric C. So & Kevin Smith, "Losing is Optional: Retail Option Trading and Expected
    Announcement Volatility," working paper 2024.** **[WP]**
    https://ide.mit.edu/wp-content/uploads/2024/03/Retail_Options.pdf
    The best identification of the retail earnings loss, the ~9% half-spread cost datapoint, and — most
    usefully — the ~9% *post*-announcement continued decay with no reversal, which corroborates the
    post-earnings selling window from an independent direction.

**Also cited, outside the top 10:** Mobina Shafaati, Don Chance & Robert Brooks (*Journal of Empirical
Finance* 2026, DOI 10.1016/j.jempfin.2026.101748) **[PR]** — the three surviving predictors from 130
candidates; Elise Gourier (WP 2016) **[WP]** — idiosyncratic variance *is* priced, ~80% of total;
Alessio Saretto (WP 2005) **[WP]** — cross-sectional IV mean reversion, the persistence result;
Yuhang Xing & Xiaoyan Zhang (WP 2013) **[WP]** — the IV path around announcements and the ~10% median
straddle spread; Jonathan Milian (*JRFM* 2023, DOI 10.3390/jrfm16050270) **[PR]** — the earnings-move
signal and the HV-IV non-transfer result; Mads Jensen & Lasse Pedersen (*JFE* 2016, 121: 278–299) **[WP/PR]**
— early-exercise rationality and the 20.7%-vs-0.4% boundary result; Guanglian Hu & Kris Jacobs (WP 2016,
later *JFQA*) **[WP/PR]** — volatility level and delta-hedged returns; Ian Dew-Becker & Stefano Giglio
(Chicago Fed WP 2025-17; WP 2026) **[WP/REG]** — the index VRP decline and its dealer-gamma mechanism;
Steven Heston & Karamfil Todorov (SSRN 4373509, AFA 2024) **[WP]** — cross-asset VRP, no single-name
estimates; Cboe Implied Correlation Index white paper v1.0.5 **[VEN/REG]**; Henry Schwartz / Cboe, "State
of the Options Industry Q3 2026" **[VEN/REG]** — the 27-names-equals-53.4% concentration figure; Jerry
Coakley et al. (*International Journal of Finance & Economics* 2024, 29: 1157–1171) **[PR]** — S&P 500
inclusion and implied betas; Fidelity Learning Center, dividend assignment risk **[VEN]**; Exegy, options
liquidity note March 2026 **[VEN]**; Tim's Stock Lists **[VEN]**; Options Industry Council weekly options
FAQ **[VEN]**.
