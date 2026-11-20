# Factor Specification — Options Contract Explorer
### What works, what does not, and what the system should actually do
**Date:** 15 November 2026 — **revision 13**: liquidity controls, user overrule and decision records (§3, on-demand design); revision 12, same day: system-drafted thesis in Mode 3, Mode 2 becomes a scan (§1, §12); revision 11, same day: Mode 1 shelved after Tests A, B and C (§0b, §1); revision 10, 14 November 2026: index instrument set (§5a, §5b, §5c); revision 9 audit corrections (revision 8, 12 November 2026, added sector/industry and macro-event strands 18, 19)
**Sources:** nineteen research strands across seven waves, plus own measurements (§0a census, §0b Tests A–C)
**Companions:** `docs/on-demand-mode-design.md` (mode 3 implementation), `docs/agent-architecture.md` (agent contracts and harness) — both updated 15 November 2026 to match
**Status:** operating spec. Supersedes all prior synthesis documents where they disagree.
**Measurements in §0a and §0b outrank literature estimates elsewhere in this document.**
**Revision 13 changes (15 November 2026, operator decisions for Mode 3):** (1) the liquidity criteria are adjustable controls, not fixed cutoffs (`docs/decisions/2026-11-15-liquidity-controls.md`); (2) **the user can overrule the liquidity gate** and move a ticker or chosen contracts to the next stage, with the cost shown and the overrule recorded; (3) **every decision at every stage produces a decision record, and when a contract is traded the full chain is stored permanently in memory** (on-demand design §3a). §3 below describes the gate as first specified; where it says the gate is non-overridable, these decisions govern for Mode 3.

**Revision 12 changes:** operator decision, 15 November 2026 — in Mode 3 the system drafts the thesis by default and the operator accepts, edits or rejects it; Mode 2 will be built after Mode 3 as a scan that feeds the same pipeline. Conditions and reasons in `docs/decisions/2026-11-15-system-drafted-thesis.md`. No research finding changed: the draft is labelled unvalidated and carries no score.

**Revision 11 changes:** three pre-registered tests run 15 November 2026 (§0b). The gross variance premium is intact; no tested index-writing programme earned alpha after 2012. **Mode 1 is shelved by operator decision; Mode 3 is the build target, with the index instruments available inside it.** Reasoning in `docs/decisions/2026-11-15-mode-1-shelved.md`. §5–§5c are kept as reference for index trades in Mode 3. §12 and §13 rewritten to match.

**Revision 10 changes:** Mode 1 instrument set widened to SPY, SPX, QQQ, IWM, TLT by operator decision — §5a (properties, hedge map, per-instrument minimum sleeve, assignment handling, correlation cap), §5b (criteria for adding further instruments), §5c (structure menu, short-dated distinction, regime-conditional selection). §1 now states that mode, instrument and structure are three orthogonal dimensions; collapsing them was a drafting error in revisions 5–10.

**Revision 9 changes:** corrections from the audit of revision 8 (`Claude outputs/spec-audit-rev8-v2.md`, 38 findings). No new research. Passages marked *(unverified)* rest on papers not read directly.

---

## 0. What changed in revision 5 (carried forward)

| Change | Was | Now |
|---|---|---|
| **Default horizon** | 42–180 DTE | **42–90 DTE** — options >90 DTE are insignificant or negative at 25% costs (one study's maturity split for one signal; treat the band as a default to be tested, and report census results for 30–120 DTE alongside — the band also determines the §0a depth result) |
| **Single-name premium** | Primary pricing signal | **Not a thesis.** Zero premium was unrejectable for 108 of 135 stocks on the model-free measure |
| **Post-earnings timing** | Untested hypothesis (IV might be cheap) | **Reversed and confirmed: IV is expensive after announcements.** First positive signal whose direction is supported offer-to-bid (what is and is not cost-tested: §4) |
| **Overlay / Israelov** | Strongest result in the programme | **Index-only, and smaller than it looked** — 4/5 of the Sharpe gain is volatility reduction, not return |
| **Tradeable universe** | Unspecified | **~250 names** (estimate, still untested — §0a, §3), measured monthly as a product output |
| **Liquidity gate** | Precondition | **Fully exclusionary and non-overridable** — gross returns are *higher* in illiquid terciles |
| **Product shape** | One pipeline | **Two modes** with different signals, instruments and benchmarks (three since revision 6 — §1) |

---

## 0b. MEASURED 15 November 2026: the variance premium did not vanish

**Test A has been run. It does not support the vanishing claim.** Per this spec's
precedence rule, a measurement outranks a literature estimate, so this subsection
governs and the literature discussion below it is now context rather than premise.

`scripts/tests/vrp_test_a.py` spec A-1, Cboe VIX and SPX closes, 441 non-overlapping monthly
windows, 1990-01 to 2026-10. Break date taken from the paper, not chosen here.

| Period | n | Mean VRP (vol pts) | Mean VRP (variance) | t | Months + | Short-var Sharpe | Detectable |
|---|---|---|---|---|---|---|---|
| pre-2001 | 132 | **+5.179** | +0.016921 | +9.34 | 90.2% | +2.82 | >0.60 |
| 2001–2012 | 136 | **+3.687** | +0.009587 | +1.94 | 80.1% | +0.58 | >0.59 |
| **post-2012** | 173 | **+3.725** | +0.007734 | +1.71 | **83.2%** | +0.45 | >0.53 |
| full sample | 441 | +4.148 | +0.011055 | +4.60 | 84.4% | +0.76 | >0.33 |

**The post-2012 premium is indistinguishable from the 2001–2012 premium.** +3.725
against +3.687 vol points; cumulative variance +1.3380 against +1.3038. Months
positive are *higher* post-2012 (83.2% against 80.1%).

**The break in this data is 2001, not 2012.** Both post-2001 periods resemble each
other and differ from the 1990s. Mean VIX fell 18.98 → 21.97 → 17.84 while mean
realised vol went 13.81 → 18.28 → 14.12: post-2012 realised vol is close to the
1990s while VIX is *lower*, which is where the compression came from.

**The t-statistics are a power statement, not a premium statement.** 2001–2012
also fails significance (t=1.94). The premium has been statistically invisible at
monthly frequency since 2001 because the standard deviation of monthly VRP rose
from 4.36 to ~7 vol points. The full sample is significant at t=4.60. A premium
that needs 441 months to show up is real and hard to harvest; it is not absent.

**What actually dominates: the tail, and it is stable.** The worst three months of
173 destroy **41%** of post-2012 cumulative premium (+1.3380 total, −0.9298 in the
worst three). The same figure for 2001–2012 is 40%. Worst single months: March
2020 −52.41 vol pts (VIX 40.11, realised 92.52), October 2008 −39.85, September
2008 −33.67, April 2025 −25.38.

### What Test A does not settle, and why Test B is now the decisive test

1. **This is gross.** No bid-ask, no commission, no slippage. §0a puts index
   options at ~2% of premium.
2. **A variance swap premium is not a straddle return.** It integrates the whole
   surface; an ATM straddle does not. **Both results can be true at once** if the
   premium migrated to the wings as skew steepened post-2008 — the surface-wide
   premium holds while an ATM straddle sale stops paying. That is a hypothesis
   here, not a finding.
3. **Dew-Becker & Giglio's straddle measurement is closer to tradeable than this
   one.** Do not treat Test A as refuting them. On the risk-adjusted decline both
   agree: Sharpe 2.82 → 0.45 here is an 84% fall.
4. **Not harvestable as measured.** Retail cannot trade a variance swap.

**The pre-registered gate CLEARED** (post-2012 positive and ≥ half of 2001–2012;
it came in at 101% in vol points, 81% in variance). Test B — Cboe BXM/PUT against
real executed option prices — is justified and is now what decides Mode 1.

### Test B is pre-registered (`scripts/tests/vrp_test_b.py`, spec B-1, frozen 15 November 2026)

Monthly CAPM alpha of Cboe BXM and PUT against the S&P 500 **total return** index,
net of the 13-week T-bill, same periods and break date as Test A. Both indices are
reported; neither is picked afterwards. The script stops rather than fall back to
the price index, because the dividend mismatch (~1.5–2%/yr) is the size of the
effect. Reading declared in advance: both post-2012 alphas positive with one
significant = survived; both positive, neither significant = point estimate only,
size against costs decides; mixed = unresolved; both ≤ 0 = defined-risk only.
Known bias, stated before the result: CAPM alpha is biased **upward** for a concave
payoff, so a small positive alpha is weaker evidence than it looks.

### Test B RESULT, 15 November 2026: no alpha from at-the-money index writing

239 monthly returns, 2004-03 to 2026-11. Cboe's free history files start later than
the indices themselves, so **there is no usable pre-2001 period and only 65 months
before the break** — this test cannot say anything about a 2012 break. It speaks to
the post-2012 period on its own.

| Period | n | BXM alpha | 95% CI | t | PUT alpha | 95% CI | t |
|---|---|---|---|---|---|---|---|
| 2004–2012 | 65 | +0.76%/yr | −4.56, +6.07 | +0.28 | +3.97%/yr | −2.56, +10.51 | +1.19 |
| **post-2012** | 174 | **−1.38%/yr** | −3.93, +1.16 | −1.07 | **−0.44%/yr** | −2.82, +1.93 | −0.37 |
| full | 239 | −1.49%/yr | −3.92, +0.94 | −1.20 | −0.23%/yr | −2.90, +2.45 | −0.17 |

**Pre-registered reading: DID NOT SURVIVE in tradeable form.** Both post-2012 alphas
are negative. Neither is distinguishable from zero, and the intervals admit up to
about +1.2%/yr (BXM) and +1.9%/yr (PUT) — but the known bias of this alpha for a
concave payoff is upward, so the true figure is if anything lower.

**What writing at-the-money did deliver post-2012:** beta 0.57 and volatility 9.3%
against the market's 13.9%, for 6.2%/yr excess return against 13.2%. That is the
risk and return of holding a bit over half the equity position, minus a small
drag. It is de-risking, not income.

**Tests A and B together.** The surface-wide variance premium is intact (+3.7 vol
points gross); one-month at-the-money writing earned nothing for it. This agrees
with Dew-Becker & Giglio's straddle result and is what the wings hypothesis
predicts, but Test B does not test the wings — it only shows the premium is not
collected at the money, monthly, after costs of implementation.

**Defect, left unfixed on purpose:** the last window is a partial month
(2026-10-30 to 2026-11-13). It is 1 of 174 observations. Fixing and re-running
would be a new trial for no change in the reading.

**Not tested, and where Mode 1's own programme sits:** out-of-the-money and
42–90 DTE writing. Cboe publishes BXMD (30-delta buy-write) and CNDR (iron condor).
A Test C on those would be trial 3 against the §11 budget and must be
pre-registered before it is run.

### Test C is pre-registered (`scripts/tests/vrp_test_c.py`, spec C-1, frozen 15 November 2026)

Trial 3. Same method as Test B on three Cboe indices fixed in advance: BXY (2% OTM
buy-write), BXMD (30-delta buy-write) and CNDR (iron condor). OTM overwriting
returns to the Mode 1 menu only if **both** buy-write alphas are positive post-2012
and at least one has t > 2. CNDR positive and significant = evidenced edge;
positive, not significant = permitted structure with no edge claim; zero or
negative = Mode 1 has no supported premium-harvesting leg. An unavailable index
makes its branch incomplete and changes nothing.

### Test C RESULT, 15 November 2026: no alpha out of the money or in the condor either

| Index | Pre-2012 alpha (n≈290) | t | Post-2012 alpha (n=173) | 95% CI | t | Beta post |
|---|---|---|---|---|---|---|
| BXY, 2% OTM buy-write | +2.10%/yr | +2.35 | **−1.18%/yr** | −3.37, +1.01 | −1.06 | 0.73 |
| BXMD, 30-delta buy-write | +2.44%/yr | +3.07 | **−1.14%/yr** | −3.12, +0.83 | −1.13 | 0.75 |
| CNDR, iron condor | +3.81%/yr | +2.87 | **−1.32%/yr** | −4.61, +1.97 | −0.78 | 0.03 |

**Pre-registered reading: no alpha out of the money; no evidenced edge in the
defined-risk structure. Mode 1 has no supported premium-harvesting leg.**

**Unlike Test B, this one does show a break.** All three were positive and
significant before May 2012 and all three are negative after. From the reported
figures the pre-to-post differences are about 3.3, 3.6 and 5.1 points a year, each
roughly 2.3–2.8 standard errors. *Those difference figures are arithmetic on the
output, not a pre-registered test, and the three indices are highly correlated, so
this is one observation seen three ways, not three confirmations.* The split is at
2012 only; this does not say whether the change came in 2001 or 2012.

**A caveat that cuts toward the same conclusion:** BXMD and CNDR were, as far as is
known here (not checked), launched around 2015 with back-calculated history. If so,
their pre-2012 alphas are hypothetical and may flatter the design. The post-2012
figures are the more trustworthy ones.

**The post-2012 condor lost money outright:** −0.88%/yr against T-bills at 6.2%
volatility and a −7.35% worst month, with beta 0.03. Defined risk bounded the
loss; it did not create a return.

**Five rule-based index-writing programmes, at the money, out of the money and
defined-risk, show no positive alpha after 2012.** Test A's +3.7 vol-point gross
premium was not collected by any of them.

**Still untested, and not testable for free:** 42–90 DTE writing. No public index
exists. It needs purchased option data or several years of the snapshot archive.
**Do not run further index variants looking for one that works** — three trials
are spent and that search is the forking path §11 exists to prevent.

### Consequences for Mode 1

- **Systematic at-the-money monthly writing has no evidenced alpha after 2012.**
  The system must not present a covered call or put-write on an index as an
  income source. It may present it as a way to hold less equity risk.
- **Mode 1 has no supported premium-harvesting leg.** The system must not
  recommend any systematic index-writing programme as a source of return, and
  must not rank Mode 1 candidates by expected premium income.
- **What Mode 1 can still honestly do:** show the cost of a structure, its tail
  (design case: a −52 vol-point month), and what it does to the portfolio's equity
  exposure. It is a de-risking and execution tool.
- **Mode 3 is unaffected.** An operator-chosen index trade is the operator's
  thesis; the system prices it, sizes it and records it without claiming an edge.
- **The binding constraint is the tail, not the premium.** 41% of cumulative
  premium sitting in 3 of 173 months is a sizing-and-structure fact. It supports
  the 4% beta-weighted cap (§5a) and defined-risk structures (§5c) on evidence,
  rather than on caution.
- **A −52 vol point month is the design case**, not a stress scenario.

---

## 0b-context. The literature claim this replaced as premise


**This is the most consequential finding in strands 18–19 and it attacks the mode
this spec treats as defensible.**

Dew-Becker & Giglio (Chicago Fed WP 2025-17, Sept 2025; revised June 2026) find the **S&P 500 variance risk
premium has declined to statistical insignificance since ~2012**:

| Period | Straddle Sharpe |
|---|---|
| Pre-2001 | **−0.74** (strongly profitable to sell) |
| Post-2001 | −0.09 |
| **Post-2012** | **+0.12, with positive alpha** |

VIX overstated realised volatility by ~25% in the high-premium era against **~10%
in the last decade.**

*The Sharpe and VIX figures are from the June 2026 revision and have not been
independently checked. The September 2025 version reports an information ratio of
about −0.6 → +0.09 around a May 2012 break. The authors caution that their results
do not show the premium is zero — a smaller premium, not an absent one.*

§1 of this spec previously described the index VRP as "+3.3 vol pts, robust." **That
characterisation rests on pre-2012 data.** The Israelov decomposition sample is
1996–2014 and so straddles the break; its 7% compensated short-vol sliver may be
substantially a pre-2012 artefact.

This is the same paper already used in §10 (alpha zero after May 2012, cited there
from its 2025 version). It is one source, not independent corroboration.

**Test A was pre-registered against this section and has now been run** (result above) (`scripts/tests/vrp_test_a.py`, spec A-1,
frozen 15 November 2026). It measures `VIX² − realised variance` on
non-overlapping monthly windows, 1990–2026, split at the paper's own May 2012
break, using free VIX and SPX closes — no WRDS, so no academic-use bind on the
result. The specification is in the script header and must not be edited
silently; every run appends to `vrp_out/TRIALS.log`.

**What Test A can and cannot settle.** `VIX² − RV` is the *variance swap*
premium, which integrates across strikes; a straddle return does not. Adjacent
object, not the same one. With ~174 non-overlapping months post-2012 the sample
can only detect an annualised Sharpe above about 0.5, so the paper's +0.12 sits
inside the noise: **a failure to reject zero here is not evidence the premium is
zero.** The decision therefore rests on the size of the point estimate against
costs, not on significance.

**A pre-registered gate governs what happens next.** Test B (Cboe BXM/PUT
against real executed option prices) runs only if post-2012 mean VRP is positive
and at least half the 2001–2012 value. Declared before the first run so the
sequence is not a forking path.

**And the reframe that shrinks this blocker.** §0b blocks *undefined-risk*
short premium, not Mode 1. A defined-risk structure (§5c: credit spreads,
condors) bounds the loss whether or not the premium exists; it is the
unbounded left tail that requires the premium to be real. Mode 1's
defined-risk branch can be built before this resolves.

**Against:** §9d's 0DTE study finds ordinary-day implied volatility about 11% above
realised in 2022–2026 — weak (small sample, unreviewed), but the only post-2012
measurement in this spec, and it points to a positive premium.

**Required before any premium-harvesting is built, index or otherwise: re-derive
the VRP on post-2012 data only.** If it is near zero post-2012, the overlay's ~20
bps/yr net prize is not merely small — it may not exist. This is now open item 1.

---

## 0a. Measured results — first live census, 12 November 2026

Run at 12:14 PT (regular session) against Cboe delayed quotes. Gate: spread ≤5% of
premium, OI ≥100, DTE 42–90, |log(K/S)| ≤0.10, mid ≥$0.20.

**These are measurements, not estimates. Where they conflict with a literature
figure elsewhere in this spec, these win.**

### What the run does NOT tell us

The universe was 103 hand-picked liquid names, so the 87/103 name-level pass rate
is **selection on the dependent variable and carries no information** about the
~250 estimate, which concerned the full ~8,439-name optionable universe. That run
has not been done.

### Contract-level yield: 5.2%

**1,684 of 32,524 contracts qualified.** Among the most liquid names in the US
market, 95% of the chain fails (17.7% of the 9,502 in-band contracts qualify; 71%
of the chain is outside the moneyness band by construction). The gate does its work at the *contract* level,
not the name level — which is the opposite of how a watchlist-shaped product
naturally thinks.

### Depth collapses fast

| Min. qualifying contracts | Names | Excluding ETFs |
|---|---|---|
| ≥2 | 87 | 80 |
| ≥5 | 66 | 60 |
| **≥10** | **36** | **32** |
| ≥20 | 15 | 12 |
| ≥50 | 3 | **0** |

Median passing name: **7 qualifying contracts**. A "≥2" pass threshold is too
generous to be meaningful — with two contracts there is no choice of strike or
expiry. **Use ≥5 as the minimum defensible bar and ≥10 for a name you would
screen on.**

**These counts are not stable.** Two later snapshots give 27 names with ≥10
(23 single) at 13:05 PT the same day and 28 (22 single) on 13 Nov, after the
24 Dec expiry fell below the 42-day floor. Quote depth as **22–32 single names
with ≥10 contracts**. 91% of single-name passes sat in the one monthly expiry
(15 Jan), and the result is steep in the threshold: at a 7.5% spread limit 49
single names carry ≥10, at 10% 61.

### Concentration

**SPY + QQQ + IWM alone hold 50.7% of all qualifying contracts** across 103 names
(SPY 443, QQQ 316, IWM 95). Seven ETFs hold 52.6%. The median single name holds 7.
This independently reproduces the published concentration figure (27 names =
53.4% of market volume).

### The cost distribution — the headline measurement

Across 9,439 in-band contracts with two-sided quotes:

| Percentile | Spread as % of premium |
|---|---|
| p25 | 4.1% |
| **p50** | **10.1%** |
| p75 | 21.0% |
| p90 | 45.4% |
| p95 | 79.3% |

Only **29.3%** are at or under 5%; 49.8% at or under 10%.

**The 10.1% median is an expiry-mix figure, not the cost of a contract you would
trade.** 75% of these contracts sit in two weekly expiries with almost no open
interest:

| Expiry | Contracts | Median spread | Share ≤5% | Share with OI ≥100 |
|---|---|---|---|---|
| 24 Dec (weekly) | 3,531 | 11.5% | 18% | 10% |
| 31 Dec (weekly) | 3,554 | 16.8% | 20% | 15% |
| **15 Jan (monthly)** | **1,818** | **5.0%** | **50%** | **92%** |
| 29 Jan | 536 | 1.0% | 95% | 35% |

**Headline: the median in-band contract in the monthly expiry costs 5.0% of premium
at quoted** (5.2% for single names; 3.7% across all in-band contracts with OI ≥100).
This does not confirm the published "10–13% round trip" — see §4 on whether that
figure is doubled.

### The gate binds inside the S&P 100

Sixteen names failed: MCD, NKE, UPS, LMT, HON, TMO, UNP, DE, LIN, SO, DUK, CSCO,
MRK, RTX, DASH, SMCI — median in-band spreads **13–43%**. Fourteen are S&P 100
members (DASH and SMCI are not — membership to be confirmed), so the gate does bind
inside the S&P 100. Seven of the sixteen had exactly one qualifying contract and
fail only on the ≥2 rule; at the ≥5 bar, 37 names fail. The OI figures in the
census output (NKE 29,564; DE 543) are maximum in-band OI, all above the 100
floor; the per-name failure label is the most frequent per-contract reason, not a
statement that the name lacks open interest.

### Session timing confirmed as material

Same gate, same universe: **50 names passed after hours (20:38 PT), 87 during the
session (12:14 PT).** After-hours quotes are not usable for this measurement.

**Open data-quality issue:** the after-hours run's top blocker was
`moneyness_out_of_band` on 35 names versus 4 intraday. This is probably not a
spot-price fault: spot differs between the two runs by a median 0.9% (max 5.2%),
and the label is a per-name modal reason that defaults to moneyness whenever a
name fails. What changed is the 31 Dec expiry (1,928 listed contracts after hours,
7,078 next day) and two-sided in-band quotes (6,613 against 9,439). **Explain the
difference before relying on any after-hours run** — bad point-in-time data is
worse than none.

**Snapshot timing decision: intraday at 11:30 PT, not at or after the close.**
The 50-vs-87 result above makes after-hours quotes unusable, a snapshot must
record what was *tradeable* at a decision moment, and 4pm closing marks are a
known bias source (they inflate measured delta-hedged returns by 60–140
bp/month — see §4). Cost: OI is the prior session's and volume is partial-day,
both acceptable because OI serves only as a liquidity screen here and volume is
unused. Hold the sampling time constant so the series stays comparable.

---

## 1. The three modes

> **Status, 15 November 2026: Mode 1 is shelved.** The scheduled index overlay
> will not be built. Tests A–C (§0b) found no index-writing programme with
> positive alpha after 2012, which leaves the system nothing to base its own index
> proposals on. Index trades are made in Mode 3, where the operator brings the
> thesis. Mode 2 is unchanged. Decision record:
> `docs/decisions/2026-11-15-mode-1-shelved.md`. The mode numbers are not reused.

### Three orthogonal dimensions, not one

A persistent drafting error in revisions 5–10 was collapsing these into "mode."
They are independent:

| Dimension | Defined by | Values |
|---|---|---|
| **Mode** | trigger + thesis origin | ~~index overlay~~ (shelved), single-name event, on-demand |
| **Instrument** | what you trade | SPY, SPX, QQQ, IWM, TLT (§5a) |
| **Structure** | the option position | **unrestricted in Mode 3**; §5c supplies the evidence shown beside an index structure |
| *Cardinality* | one name or a list | orthogonal to all three — a list is a batch, not a mode |

**Mode is the only one of these that is about who formed the thesis.** Instrument
and structure are choices made inside a mode. The consequence that matters:
**Mode 1 needs an evidenced structure menu because the system picks; Mode 3 needs
none because the operator picks.** A restriction on Mode 1's menu is a restriction
on what the system will claim to have decided, not on what the operator may trade.

The instrument classes have inverted properties. The system should branch, not parameterise.

**Mode 3 — on demand.** The user names a ticker, a list or a contract outside any
scheduled trigger. **Since revision 12 the system drafts the thesis by default**
(bullish, bearish, neutral or no view, with a probability, horizon and falsifiers);
the user accepts, edits or rejects it, or supplies their own. **Expected to be the
most-used mode.** It adds no new agents. The draft has no demonstrated predictive
edge and is labelled so; it is never given a score, never sees option prices, is
challenged by a critic on a different model family, and is logged and resolved so
the system's own hit rate can be measured. What the system contributes reliably is
unchanged: cost analysis, probability honesty, base-rate confrontation, sizing
discipline and an immutable record. Full design in `docs/on-demand-mode-design.md`.

**Mode 2 — single-name events — is now a scan, not a pipeline.** It will be built
after Mode 3 as a scheduler and an event filter that surface candidates and hand
each to the Mode 3 pipeline with a volatility-pricing thesis. §4 still governs
what the scan may look for.

Two constraints from that mode generalise and are recorded here because they
change the main design: §8a (reminders do not work) and §11 (what cannot be
measured about the user).

The two instrument classes. *The index column described Mode 1 and is kept for the
instrument properties, which apply to index trades in Mode 3.*

| | **Index mode** (SPX/XSP) | **Single-name mode** |
|---|---|---|
| Spread at 42–48 DTE | ~2% of premium | **~6.4% effective; round trip 5–6.4% or 10–13% depending on the source's definition (unverified — §4)** |
| Variance risk premium | Gross +3.7 vol pts post-2012, **not collected by any tested writing programme** (§0b) | **+1.5 or −1.35 depending on measure; unrejectable zero for 108/135 names** |
| Tax | §1256, 26.8% | All short-term, 37% |
| Settlement | Cash, no assignment | Physical, early exercise, pin risk |
| Cross-sectional signals | None | The only place any exist |
| Earnings events | None | **The core opportunity** |
| Liquidity gate | Passes trivially | Excludes most names; depth is the real constraint (§0a) |
| **Primary purpose** | ~~Overlay~~ **shelved 15 Nov 2026.** Index trades are operator-originated, in Mode 3 | **Scheduled-event positioning** — earnings is the best-evidenced instance, not the only one (§4a) |
| **Benchmark** | Volatility-matched passive equity | That name's own realised post-earnings moves |

---

## 2. Ranked levers

| Lever | Effect | Certainty |
|---|---|---|
| **Maturity choice** (0DTE vs 42–48 DTE) | Spread 8.7–9.5% → ~2% of premium | Measured (one working paper; the index end agrees with the 12 Nov census) |
| **Instrument choice** (SPX vs SPY) | **10.2 pp of gross P&L** via §1256 | Statutory |
| **Liquidity gate** | Straddle 10−1: +8.2% low-spread tercile vs −0.8% high | Strong |
| **Native complex orders** | Up to **83%** vs legging | Strong |
| **Limit vs marketable** | **2–3.5×** cost reduction, net of missed fills | Strong for SPXW 0DTE (3 sources); transfer to 42–90 DTE assumed |
| **Post-earnings short premium** | 14.9% / 9.4% **offer-to-bid** for the two-way, two-signal strategy | Strong for direction; net return of the leg actually built is unmeasured and expected small |
| **Event-vol stripping** | Removes false positive on every earnings name | Strong |
| **Volatility forecast quality** | ~33% RMSE vs trailing RV | Measured, index only |
| **Overlay timing-strip** | ~130 bps/yr gross at full notional; ~20 bps at 25% sleeve | Moderate, unreplicated (conditional on §0b) |
| **Sizing** | Prevents ruin; creates no return | Strong |
| *Direction prediction* | ~7 bp/month, t=0.45 | **Near zero** |
| *Contract richness ranking* | ML sort: 0.47%/mo at 25% of quoted spread, fails at 50%. HV−IV straddle sort: +8.2%/mo at full quoted spread in the liquid tercile (1996–2006; removed by the authors' own repricing test — §6) | **Weak and cost-dependent, not zero** |

Build in this order. Everything above the italics requires no forecasting.

---

## 3. The liquidity gate — now the most important mechanism in the system

Goyal & Saretto (*JFE* 2009), straddle 10−1 at full quoted spread:

| Tercile | Net return |
|---|---|
| Low spread | **+8.2%** |
| High spread | **−0.8%** |

Delta-hedged calls: 0.0% low, 0.1% high. Low-volume tercile delta-hedged: 0.2%.

**The trap: gross returns are *higher* in the illiquid terciles — 23.9% versus 18.0%.** Any ranking built on gross richness systematically selects contracts whose edge dies in execution. This is not a tuning problem; it is a selection-mechanism failure.

**Therefore the gate runs before scoring, excludes rather than penalises, and must never be overridable by any signal strength.**

### The gate

1. **Quoted spread < 5% of premium on the specific contract** — not the name's average
2. **Absolute open-interest and volume floors**
3. **Has listed weeklys** — an exchange-curated liquidity certification, free
4. **Prefer third-Friday expiries** (measured 12 Nov: median in-band spread 5.0% in the monthly expiry against 11.5–16.8% in the two weeklies — §0a)
5. **No short ITM call through an ex-date where dividend > extrinsic value** — position-level, not a name exclusion; at 42–90 DTE extrinsic value typically exceeds a quarterly dividend several times over

### The universe

| Stage | Count |
|---|---|
| Listed equity symbols | 12,134 |
| ≥1 option trade in 2025 | 8,439 |
| Continuous chains | ~3,000–4,000 |
| Vendor-rankable | ~1,000–1,200 |
| **Clear <5% spread with meaningful OI** | **~250** (range 150–400; pessimistic 100–150) — **untested** |
| Institutional-grade | ~27–50 |

For scale: 27 names are 53.4% of market volume; the top 10 are 31.7%.

**Measured (§0a), on a curated liquid universe only:** depth, not name count, is
the binding constraint. 36 names carried ≥10 qualifying contracts and 15 carried
≥20, of which **zero single names reached ≥50** (12 Nov 12:14 PT; 27–28 names
carried ≥10 on two later snapshots — §0a). Half of all qualifying contracts
sat in three ETFs. Whatever the broad-universe count turns out to be, the number
of names with enough depth to *choose* a trade is an order of magnitude smaller.

**Composition is a second problem.** (Revision 5 said here that count is ample; §0a supersedes that — depth is the constraint.) The survivors tilt to large-cap, low-IVOL, heavily-covered names — precisely where no positive premium is evidenced.

**Treat universe size as a measured monthly output, not a constant.** No peer-reviewed absolute-threshold census exists, so this is a genuinely novel product output and worth surfacing.

---

## 4. Single-name mode

### The premium thesis is unproven

| Measure | Single names | Index |
|---|---|---|
| ATM IV − realised (Bakshi & Kapadia, 25 stocks) | +1.5 vol pts (+1.07 dividend-clean) | +3.3 |
| **Model-free IV − realised** (Driessen-Maenhout-Vilkov, 135 stocks) | **−1.35 vol pts** | +3.77 |
| Delta-hedged call gain ~50d (Cao & Han, ~6,000 stocks) | −1.13% mean, −0.77% median | — |

All three samples are believed to end before 2012 (periods to be checked against the papers and added to the table). If so, the single-name null is as dated as the index premium that §0b discounts.

**DMV is the serious disconfirming source.** On the full-surface measure, implied sat *below* realised on average, and **zero premium was unrejectable for 108 of 135 stocks.** Their structural result — the entire index VRP is priced *correlation* risk and individual variance risk is unpriced — means a ticker-level tool trades the leg without the robust premium.

**Cao & Han's percentiles show how wide the cross-section is:** mean delta-hedged call gain runs −3.75% (10th pct), −1.85% (25th), −0.77% (median), −0.08% (75th), **+0.77% (90th)**. From the seller's side, a quarter of names paid nothing on average and a tenth paid negative. These are unconditional percentiles; they do not show which names a richness screen selects.

**Cost arithmetic.** Effective relative spreads among S&P 500 constituents: **6.41% ATM calls, 5.25% ATM puts** (2004–2012). **Round trip is unverified:** strand 14 records the measure as 2|trade − mid|/mid, which is already a round trip, making it 5–6.4% and not the 10–13% earlier revisions stated. Check the definition in Christoffersen et al. (*RFS* 2018) before relying on either. A 90-DTE ATM option is ~5–6% of the underlying in premium, so the round trip costs ~0.3% of the underlying at 5–6.4% (~0.5–0.6% at 10%) — **in either case a large share of the median name's entire premium.**

**Three further discounts:**
- 4pm closing marks bias delta-hedged returns up **60–140 bp/month** — the same order as the premium, and every OptionMetrics-based study here uses them
- The index premium broke around 2010–2012, and **no located study re-estimates the single-name VRP post-2012**
- Options **>90 DTE are insignificant or negative at 25% costs** while ≤90 DTE survive

**Contested premise:** Gourier (2016) finds idiosyncratic variance risk *is* persistently priced, at ~80% of the total premium (range 13–96%) — the opposite of DMV. Unresolved. **Size as though uncompensated; do not assert it either way.**

### The post-earnings signal — the one positive result

**Post-announcement implied vol is expensive, not cheap.** This reverses the hypothesis and favours a seller.

- Chung & Louis (*JEF* 2017): straddles bought *after* announcements return **more negative** than non-earnings straddles. Long-short 14.4%/month, and **14.9% / 9.4% executed offer-to-bid** — a far more demanding test than the midpoint figures dominating this literature.
- de Silva, So & Smith: high-expected-announcement-volatility straddles underperform ~11% on announcement day **plus ~9% over the next 10 days with no reversal.**
- Xing & Zhang's IV path (49.3% → 53.2% → 49.1%) shows the crush **restores baseline without undershooting** — ruling out the cheap-IV hypothesis directly.

**Implementation constraints:**
- **Take only the short-after leg.** The long-before leg contradicts de Silva et al. and three prior strands.
- Cost-surviving figures are for the combined two-way strategy, further sorted on a volatility spread. The authors reportedly find single-factor versions shrink to small returns after costs (strand 14; paper not read directly). **The short-after leg alone is unmeasured and should be expected to be small.** The source also uses one-month options, not 42–90 DTE.
- **Condition on pre-announcement realised vol** — overestimation is strongest after volatile periods.
- **Use an earnings-specific signal.** Milian (2023) finds the HV−IV spread has **no** power inside the earnings window.

### Single-name ranking, survivors of the gate only

| Input | Role |
|---|---|
| Realised-minus-implied, as deviation from the name's **own trailing level** | Tie-breaker, not primary |
| **Turnover** | Weight **above** its raw power — the only one of three surviving predictors insensitive to arbitrage-cost proxies |
| IVOL | **Within the gated universe only** |
| Post-announcement entry | **Primary timing input** |
| Past earnings move vs implied move | Event richness |

**Implied correlation (COR1M/COR3M) is market-level only** — usable as a regime filter, **not** a cross-sectional selector. No credible evidence found for per-name use.

### 4a. The event framework is general, not earnings-specific

Earlier revisions described this mode as post-earnings short premium. **That was an
unforced narrowing.** The σ²_jump decomposition works on *any scheduled event with
a known date* — FOMC, CPI, elections, OPEC, trade deadlines, FDA decisions, court
rulings, product launches. Same formula, same implied-versus-realised comparison,
same shrink factor. It is a wider event calendar, not a new module.

Earnings remains the best-*evidenced* instance (implied jump vol R² ≈ 28.5% against
the realised move; ~9–11% relative bias high). Whether the framework transfers
quantitatively to macro events is under research — see open items.

Trend and TA enter this mode as structure, placement and sizing inputs per §9b, not
as entry direction.

### Single-name mode is event-driven, not a screen

The measured depth distribution (§0a) rules out single-name mode as a
screen-across-many-names product: only 22–32 single names carry ≥10 qualifying
contracts across three snapshots and the median carries 7.

**But the post-earnings short-premium trade does not need depth.** It needs one
suitable contract, on one name, in the window after that name reports. Seven
qualifying contracts is sufficient for that. So single-name mode is an
**event-driven, few-names-at-a-time** product, triggered by the earnings
calendar rather than by a periodic ranking sweep.

This also resolves the breadth-penalty problem: an event-triggered system is not
ranking a small cross-section against itself, so the √(N/n) information-ratio
penalty does not apply in the same way. The small-sample problem does not disappear:
it moves to the time series (roughly 130 earnings events a year across ~32 names).

### Single-name overlays are dead

S&P's SPXCC index (monthly OTM calls on individual constituents): 5.47% return / 18.60% vol, against the S&P's 6.45% / 21.18% and BXM's 4.58% / 15.28%. All three Sharpes within 0.03 — **no risk-adjusted improvement**, and drawdown worse than BXM's. Trading cost **~150 bps/yr versus 28 bps at index level** — more than the entire index prize before any premium is collected. Separately, 17 of 24 delta-hedged single-name option sorts were profitable gross and **none net of costs.**

**Do not build a single-name overlay or hedged module.**

---

## 5. Index mode — the overlay (SHELVED 15 November 2026)

> **This mode is not being built.** §5 is kept as the record of the overlay design
> and its literature basis. §5a (instruments), §5b (adding instruments) and §5c
> (structures) remain in force as reference for index trades made in Mode 3.
> Where §5 describes a return to be harvested, §0b's measurements override it.

### The decomposition

Israelov & Nielsen (*FAJ* 2015), simulated ATM covered call (their Table 1, arithmetic returns), 1996–2014:

| Component | Excess return | Vol | Sharpe | Risk share |
|---|---|---|---|---|
| Covered call (total) | 5.9% | 11.4% | 0.52 | 100% |
| Passive equity | 3.5% | 8.5% | 0.41 | 67% |
| **Short volatility** | **1.9%** | **1.9%** | **0.98** | **7%** |
| Equity timing | 0.5% | 4.8% | 0.10 (t = 0.4) | 26% |

Of the option-related risk, only the 7% short-vol sliver is compensated. On the actual BXM index (their Table 6, compounded returns), hedging away timing took Sharpe 0.37 → 0.52, vol 11.4% → 9.2%, downside beta 0.85 → 0.60.

### Three corrections to how this is usually read

1. **The gain is four-fifths volatility reduction, one-fifth return.** Excess return moves only 4.9% → 5.1%. Anyone reading it as added return will oversize badly.
2. **The whole prize is ~130 bps/yr gross at full BXM notional**, volatility-matched. At a realistic 25% sleeve, the net prize is **~20 bps/yr** — against daily monitoring, a futures account, quarterly rolls and §1256/§1092 complexity. A static equity reduction gets the same volatility profile free.
3. **Partial notional is a null.** It scales all three components linearly; risk shares are unchanged. The common retail framing of "write fewer contracts to reduce risk" reduces size, not the uncompensated share.

### Methodology

Daily Black-Scholes delta, hedge the deviation from a **constant** target delta (0.5 ATM, 0.3 at 2% OTM) with index futures. Mean absolute hedge ≈ **21% of written notional**, peak ~35%. **Timing risk rises monotonically through the option's life** and on the day before expiry is nearly as large as the passive-equity component.

Costed once, in *Covering the World* (Journal of Risk 2017): option frictions 0.28%/yr take unhedged Sharpe 0.35 → 0.33; daily futures hedging takes risk-managed 0.51 → **0.46**. So **+0.13 of a +0.16 gross gain survives institutional costs (~81%)**; the hedge costs ~0.05 Sharpe ≈ 46 bps/yr.

### Micro futures: cost is not the obstacle — granularity is

CME-verified: MES = $5 × index, 0.25-pt tick = $1.25, quarterly, cash-settled, §1256. At S&P ~7,550 that is ~$37,750 notional; initial margin ~$1,700–1,900 (broker source, undated — **verify live**).

Cost: half-spread 0.17 bps + commission 0.13–0.23 bps per side; ATM 35-DTE gamma implies ~6.5% notional daily delta drift ≈ 16× notional/yr turnover → **5–10 bps/yr all-in for a daily hedge**, 6–9× cheaper than institutional because a 1–6 contract hedge pays no market impact.

**Granularity is binding:**

| Sleeve | Active exposure removable |
|---|---|
| $1m | ~96% |
| $500k | ~91% |
| $250k | ~82% |
| $100k | ~55% |
| $50k | ~10% |

**Minimum comfortable sleeve $300–500k. Below ~$150k, use static approximations only.** SPY shares are cheaper (0.07 bps) and 50× more granular but touch the appreciated lot — a tax problem, not an execution one.

### The free wins — no futures account needed

- **Strike widening.** Timing's risk share falls 26% → 12% going ATM → 2% OTM; Sharpe 0.37 → 0.41. **~27% of the gross improvement, zero cost.**
- **Three-tranche laddering** staggered 10–15 days. Cross-tranche delta correlation 0.27 implies ~49% of timing variance removed, and it eliminates a 0.12-Sharpe / 15%-terminal-wealth single-expiry lottery.
- **Roll at ~1/3 life remaining** — ~35–50% of timing variance (unquantified in the literature).
- **Static initial-delta-only hedge** — one futures trade per cycle, net-profitable under documented cost assumptions (25% of quoted spread, 3 bp underlying).

**Stacked: ~50–65% of the improvement at near-zero cost.**

### 5a. The instrument set — operator decision, 14 November 2026

**Mode 1 trades SPY, SPX, QQQ, IWM and TLT.** The operator has explicitly accepted
the §1256 give-up (~10.2 pp of gross P&L, ~102 bp/yr at a 10% gross return, against
an overlay net prize of ~20 bp/yr). Recorded here so the trade-off is not
re-litigated: **the tax treatment is worth more than the strategy's edge**, and the
decision was to take liquidity and simplicity instead.

#### What this set gets right

**Depth.** The 12 Nov census found the three deepest chains in the whole 103-name
universe were **SPY (443 qualifying contracts), QQQ (316), IWM (95)** — together
50.7% of all qualifying contracts. SPX and XSP were not in that universe file and
remain unmeasured. On the dimension this spec says dominates everything, these are
the best-measured instruments available. *(Counts are from the 12:14 PT run; §0a
records that depth counts are not stable across snapshots.)*

**TLT may carry a larger premium than equities, and it is a different premium.**
Heston & Todorov, across 20 futures markets: the S&P 500 variance portfolio
returned −11.9%/month at an annualised Sharpe of **−0.23**; **10-year Treasuries
returned −25.8%/month at Sharpes of −1.4 to −3.0.** Negative means selling variance
wins, so the bond premium is roughly twice the magnitude at five to thirteen times
the Sharpe.

**Why that matters:** §0b blocks index mode on whether the *equity* VRP survived
post-2012. The bond premium is a separate question, so TLT gives Mode 1 a path that
does not wait on that resolution.

**The inference gap, stated plainly.** That measurement is on **10-year Treasury
futures variance**. TLT is a 20+ year bond ETF and its options are a different
instrument at a different point on the curve. No TLT-options VRP estimate was
located. *(Unverified — the transfer is assumed, not demonstrated. Treat as a
hypothesis to measure, not a finding.)*

#### Per-instrument properties

| | Settlement | §1256 | Distributions | Hedge | Hedge notional |
|---|---|---|---|---|---|
| **SPX** | Cash, European | **Yes** | None | MES | ~$37,750 |
| **SPY** | Physical, American | No | Quarterly | MES | ~$37,750 |
| **QQQ** | Physical, American | No | Quarterly | MNQ | ~$50,000 |
| **IWM** | Physical, American | No | Quarterly | M2K | ~$12,500 |
| **TLT** | Physical, American | No | **Monthly** | **None (micro)** | shares, or ZB/UB ~$100k+ |

*Hedge notionals are index level × multiplier at mid-November 2026 levels; recompute
at runtime, not from this table.*

#### Minimum sleeve per instrument

The §5 granularity table is MES-specific. Removable exposure scales with
sleeve ÷ hedge notional, so the minimum sleeve differs by instrument *(own
arithmetic, scaled from the MES figures — not independently derived)*:

| Hedge | Notional | Approx. minimum sleeve |
|---|---|---|
| TLT shares (100-lot ≈ $8,800) | finest | **~$70–115k** |
| M2K | ~$12,500 | **~$100–165k** |
| MES | ~$37,750 | **~$300–500k** |
| MNQ | ~$50,000 | **~$400–650k** |

Two consequences. **IWM is the most granular futures-hedged instrument**, not SPY.
And **TLT shares give the finest granularity of anything here** — the earlier
characterisation of TLT hedging as "awkward" was wrong; it is capital-expensive and
not §1256, but it is the most precise hedge in the set.

#### Assignment handling — now load-bearing, not theoretical

Four of five instruments are physically settled American options. For a short-
premium overlay rolling tranches continuously this is a recurring operational cost,
and §3's gate item 5 moves from a precaution to a hard requirement.

**Required:**

1. **An ex-dividend calendar per instrument.** TLT distributes **monthly**, making
   it the worst case by a wide margin.
2. **An early-exercise predictor on short calls.** Assignment is likely when
   `D > K[1 − e^(−r(T−t))] + put value`. Evaluate before every ex-date, not at entry.
3. **Recognise that a spread's defined risk is not defined through assignment.** If
   one leg is assigned you hold overnight share exposure at full notional. Size and
   margin must survive that state, not just the intended one.
4. **No short ITM call carried through an ex-date** where the distribution exceeds
   remaining extrinsic value. Position-level, blocking.

SPX alone needs none of this, which is the non-tax reason it remains in the set.

#### Correlation — the real risk in this instrument set

**SPY, QQQ and IWM are all US equity beta.** Writing strangles across all three is
not three positions; it is **one position at roughly 3× size.** Daily-return
correlations among them typically run 0.85–0.95.

**Therefore the 4% aggregate short-premium cap in §8 must be measured on
beta-weighted net exposure to a single reference (SPY), never per instrument.**
A per-instrument reading of that cap would permit roughly three times the intended
risk.

**TLT is the only candidate diversifier, and do not assume it diversifies.**
Stock–bond correlation is regime-dependent and was positive through 2022. Compute
realised correlation on a rolling window rather than assuming the historical sign.

#### Structure note

The audit's two open inconsistencies in the recommended structure below (the 30–45
DTE band sitting outside the 42–90 gate, and the 2–3% premium target lacking a
denominator) apply unchanged to this instrument set and are not resolved by it.

---

### 5b. Criteria for adding an instrument to Mode 1

Apply in order. An instrument qualifies only if it clears **every** gate and
satisfies **at least one** of the two evidence conditions.

**Gates — all required:**

1. **Measure the chain first.** Run the census on it: spread as % of premium and
   qualifying-contract count at the intended DTE and moneyness. Report by expiry,
   not pooled — §0a's expiry-mix finding shows a pooled median is dominated by
   untradeable weeklies. **No instrument enters on reputation.**
2. **A hedge instrument exists at workable granularity.** Compute the minimum sleeve
   from its notional. If the minimum exceeds the sleeve, the instrument is out
   regardless of how good its chain looks.
3. **Settlement and distribution schedule are known**, and if physically settled,
   the ex-date calendar and early-exercise test are in place before the first trade.
4. **It clears the liquidity gate** on its own merits. Index instruments are not
   exempt.

**Evidence — at least one required:**

5. **Measured VRP evidence for that asset class**, with the instrument it was
   measured in stated. A futures-variance result does not transfer to an ETF option
   without an argument.
6. **Or genuine diversification**, demonstrated by realised beta-weighted
   correlation to the existing sleeve on a rolling window — not by asset-class label.

**Record for each instrument:** §1256 status, hedge instrument and notional,
minimum sleeve, distribution frequency, measured spread by expiry, and correlation
to the sleeve.

#### Candidates worth considering, with what is known

| Candidate | Case for | Case against |
|---|---|---|
| **GLD** | Genuine diversifier; liquid options. Commodity variance premia were measured large *(ags, Sharpes −1.4 to −3.0 — **not gold specifically**)* | No gold-options VRP estimate located |
| **HYG / LQD** | Credit; the credit spread survived variable selection in the vol-forecast work | That was as a *forecast input*, not a premium claim. Thin option chains — measure first |
| **EEM / EFA** | International equity | Correlated to SPY; adds size, not diversification |
| **USO** and energy | Commodity premium | Contango/roll structure contaminates the ETF; measure before assuming |
| **FXE / FXY** | Currency diversification | Heston & Todorov found the Swiss franc was the **one market with a positive premium** — currency VRP is inconsistent in sign. Caution |
| **VIX options** | — | **No.** Different instrument class, and short-vol ETPs are excluded outright (Volmageddon, >90% one-day loss) |

**Best next candidate on the evidence: GLD**, conditional on measuring its chain and
locating a gold-options premium estimate. It is the only one that plausibly
satisfies the diversification condition rather than just adding equity beta.

---

### 5c. The structure dimension

§5's evidence is covered-call-shaped because the Israelov decomposition is about
covered calls. **That is the shape of the evidence, not a limit on the mode.** Mode
1 may run any structure below; what differs is how much the system is entitled to
claim about it.

#### Structure menu for Mode 1

| Structure | Evidence | Verdict |
|---|---|---|
| Short calls / covered calls | Israelov decomposition (§5); ~20 bps/yr net at a 25% sleeve. **Test B (§0b): BXM alpha −1.38%/yr post-2012, t=−1.07** | **No alpha at the money. De-risking only** |
| Put-writing | Same bet by put-call parity — differs on plumbing (cash collateral, no ITM-call holding-period trap, richer skew side), not expected return. **Test B (§0b): PUT alpha −0.44%/yr post-2012, t=−0.37** | **No alpha at the money. De-risking only** |
| Short strangles | **Margin calls turn Sharpes negative:** near-10%-OTM strangle 0.551 → **−0.306**, 10% OTM put 0.352 → −0.239, near-ATM straddle 0.301 → 0.128, all with margin enforced | **Only with margin modelled against the actual account** |
| Credit spreads / iron condors | High win rate, negative skew. One 11-year test reported 61% winners with negative returns across all allocations *(competing-educator source, weak)* | **Allowed, with no edge claim.** Test C (§0b): CNDR alpha −1.32%/yr post-2012, t=−0.78. Must display max loss, loss-to-credit ratio, and consecutive wins needed to recover one max loss |
| Calendar spreads | **No credible evidence found** — only commercial blogs. The absence of literature beside the dense VRP literature is itself the finding | **Not systematically** |
| Systematic long premium | Pays the variance risk premium by construction | **No** |
| Systematic tail hedge | PPUT 6.64%/yr, Sharpe 0.29, drawdown **longer** than the S&P (80 vs 73 months) | **Poorly evidenced** |
| Ratio / broken-wing | Unresearched | **Measure before building** |

#### Short-dated structures: edge-blocked, not cost-blocked

The 42–90 DTE default was derived largely from **single-name** economics and does
not transfer cleanly to index instruments.

**On cost, short-dated index is defensible.** SPX 0DTE customers were at the best
bid more than half the day, achieving net effective spreads of **2.1¢ against 5¢**
for marketable orders. That is the opposite of the single-name picture, where the
measured median in-band spread was 10.1% of premium (§0a — and itself an
expiry-mix figure).

**On edge, it is not.** Retail 0DTE averaged **−4.6% per trade**, and the research
concluded the losses came from *the positions, not the frictions.* Of a >$125m
retail 0DTE loss, **>$100m sat in single legs** while spreads had positive *median*
returns.

**Consequences:**

1. Short-dated index is a **different problem** from short-dated single-name — a
   missing edge rather than a prohibitive cost. Do not cite the single-name cost
   argument against it.
2. **If short-dated runs at all, run it defined-risk.** That is the one thing the
   0DTE data supports directly.
3. The audit's note on the 42–90 band applies here: treat it as a default to test,
   and report 30–120 DTE alongside in census output.

#### Structure selection should be regime-conditional, not fixed

The Regime Assessor (§9a, `docs/agent-architecture.md` §3.2) exists for this. A
systematic mode that always writes the same structure is making an unconditional
bet that the structure's edge is unconditional — which nothing here supports.

Indicative mapping, to be tested rather than trusted:

| Regime signal | Structure bias |
|---|---|
| VIX curve in contango, realised vol low | Undefined-risk short premium permissible, **margin modelled** |
| VIX curve in backwardation | Defined-risk only, or skip the tranche |
| Elevated geopolitical risk | Size down and prefer defined risk (§9d — regime input only, never an entry) |
| Higher-timeframe trend against the short side | Size down (§9b role 4) |

**Every one of these is a sizing-and-structure response, never an entry signal.**

#### What this does not change

- The liquidity gate applies to every structure (§3).
- The 4% aggregate short-premium cap is measured on **beta-weighted** net exposure
  (§5a), and a multi-leg structure contributes its net short-premium exposure, not
  its leg count.
- Assignment handling applies per leg on physically settled instruments (§5a).
- A spread's defined risk is **not** defined through assignment.

#### And the restriction that does not exist

**Mode 3 has no structure menu.** The operator brings the thesis and the structure;
the system contributes the cost ladder, the probability pair, base-rate context,
sizing and an immutable record. A discretionary short-dated put because the operator
has a view this week is **Mode 3 with an index instrument** — supported today, no
structure evidence required, because the system is not claiming to have chosen it.

---

### Recommended index structure

Keep the index funds untouched. Run a **separate** sleeve across the §5a instrument set: laddered short strangles or calls, **30–45 DTE, 2% OTM or wider**, targeting **2–3% annualised premium, not 8–12%**, three tranches staggered 10–15 days, rolled at ~12–15 DTE, delta-hedged to a constant target on a ±½-contract band using each instrument's own hedge (§5a). Aggregate short-premium risk is capped on **beta-weighted** net exposure, not per instrument.

**Two unresolved inconsistencies in this structure:** (1) 30–45 DTE rolled at 12–15 DTE lies almost wholly outside the 42–90 DTE default horizon and gate; either move it into the band or record why index mode differs. (2) The 2–3% premium target has no stated denominator. A 2% OTM one-month call at 18% volatility is worth ~1.2% of the index, ~14–15% annualised; 2–3% at full notional needs a strike near 7% OTM (delta ~0.1). The numbers reconcile only if 2–3% is measured on the whole portfolio with a ~20–25% sleeve.

Display the **volatility-premium-versus-equity-premium split of every quoted premium** — only ~11% of an ATM premium is compensation. Benchmark against volatility-matched passive equity.

### Serious disconfirming evidence

- **Israelov's own later work undercuts it.** *A Devil's Bargain* (QVR): monthly SPX call-writing beat the index only at 1.2–2.4% target yields and by 0.2%/yr gross, with **2011–2023 losses of 3.1%/yr at a 6% target and 4.7%/yr at 12%.** QVR has publicly stated the VRP is not persistently positive or attractive.
- **The decomposition has never been independently replicated** — every paper performing it has Israelov as an author, and he notes it is delta-model-dependent.
- **The anchor paper's two tables use different conventions** — Table 1 is the simulated covered call on arithmetic returns (0.52), Table 6 is BXM on compounded returns (0.37 unhedged). The 0.37 → 0.52 improvement is within Table 6 and is like-for-like *(reconstructed from reported figures; tables not read directly)*.
- Laddering, per Israelov's own later work, "does little to reduce volatility or drawdowns."
- Short-vol ETPs excluded outright (Volmageddon, >90% one-day loss).

### Put-writing vs covered calls

Economically the same bet by put-call parity — a short put's delta drifts identically, so it is **not** a cleaner isolation of short vol. Choose on plumbing: cash collateral leaves existing index beta intact, no ITM-call holding-period trap, richer skew side. PUT index 0.52 Sharpe vs S&P 0.46 (2006–15), gross.

---

## 6. Volatility forecasting

Unchanged from revision 4 and still the core of any richness measure.

| Model | ~63 days | ~126 days |
|---|---|---|
| Trailing historical vol | 1.000 | 1.000 |
| GJR-GARCH | 0.806 | 0.810 |
| HAR | 0.759 | 0.800 |
| **Two-component (MF2-GARCH)** | **0.672** | **0.657** |

A two-component model in log-variance beats trailing RV by ~33% RMSE. **HAR decays and reverses with horizon** — 0.759 quarterly → 0.875 annual, with log-HAR-plus-leverage at 1.123 at one year, *worse* than trailing RV.

**Estimation is nearly free.** MSE vs intraday 5-min RV: close-to-close 0.533, Garman-Klass 0.094, **Parkinson 0.092** — 4–6× reduction from daily OHLC. Range estimators run 8–18% biased low; Yang-Zhang handles overnight gaps, which matters for single names. **Do not buy intraday data.**

### Event-vol decomposition

**One earnings day can hold ~57% of total variance in a 40-day expiry.** Comparing raw event-spanning IV to a diffusive forecast manufactures a false "expensive" verdict on every name near earnings.

```
σ²_jump = (σ²(t,T₁) − σ²(t,T₂)) / (1/T₁ − 1/T₂)
```

Computable from an EOD chain alone. Implied event vol 8.22% vs realised 7.42% — **~9–11% relative bias high.** Implied jump vol has **R² ≈ 28.5%** against the realised announcement move; nothing in the daily-OHLC toolkit matches that, so use the market's implied event move shrunk 9–11%, then strip it via variance additivity.

**The hard part is reliable earnings dates with before-open/after-close timing.** Budget real effort.

### The signal, correctly specified

**The residual from a per-name regression of forward realised vol on same-horizon *clean* IV** (expect slope < 1) — not the raw difference. Gate on VIX-curve backwardation and exclude the zero-signal terciles.

### Disconfirming

IV may encompass model forecasts entirely (Busch et al.: forecast error *rises* when HAR components are added). Goyal-Saretto's own repricing test killed their signal — a better IV model *removed* the effect. GARCH(1,1) out-of-sample R² goes **negative at 50 days.** The option-returns literature is a 1-month literature being extrapolated.

**Build:** Yang-Zhang, Parkinson, two-component log-variance forecast, SSVI surface weighted by inverse-squared spread × squared vega, nightly Carr-Madan arbitrage checks with flagging, event-vol stripping. `arch` provides HARX/GJR/EGARCH with SPA tests. 30–50 names is seconds of compute.

**Do not build:** HAR-Q, realised kernels, Markov switching, GARCH-MIDAS, slope or skew as signals, vol-of-vol.

---

## 7. Execution

Marketable orders cost **2–3.5×** disciplined non-marketable limits, and the 0.42-of-half-spread figure is already net of missed-fill cost under a one-second fallback.

**Scope:** the placement figures in rules 2, 3 and 5 are measured or calibrated on SPXW 0DTE options under $3 with $0.05 ticks (July 2023). Transfer to 42–90 DTE single names is assumed, not measured. On 12 Nov only 9% of single-name contracts passing the §3 gate were ≤2 ticks wide, the width at which 0.42 was measured; the median was 8 ticks.

1. **Always non-marketable limits.** Price improvement received 80–99% of the time, versus **0–1%** for marketable electronic orders on tight spreads.
2. **Interior placement, not most aggressive.** 4-tick: 0.55 / **0.42** / 0.58. 3-tick: two ticks in fills 90% at 0.43; one tick in fills 36% at 0.51.
3. **At ≥4 ticks, drop the patient-limit workflow** — fill intensity near zero regardless of aggressiveness (a market-maker model calibrated to SPXW; unreviewed). This is a workflow switch, not a contract exclusion: 82% of single-name contracts passing the §3 gate are ≥4 ticks wide, so as an exclusion it would empty the universe. Use a native complex order or accept a marketable fill, and measure own fill rates.
4. **Native complex orders, never leg in.** Up to 83% saving; complex orders price on a **$0.01 net grid** even when legs are on $0.05/$0.10 ticks. **Partial fills preserve the leg ratio.** On C1, only Customer/Pro-Customer capacity can initiate a complex-order auction.
5. **Adverse selection is asymmetric at the $3 boundary** — non-fill penalty ~14% below, **~40% above.**
6. **Avoid the first 90 minutes** for equity options; SPX spreads peak ~10:00.

**Do not build:** a routing selector (99.84–100% of retail options flow is non-directed), or anything from Rule 605 (**605 does not cover listed options**).

**Data hygiene:** ~**38% of raw OPRA trades appear to print inside the BBO** from sequencing errors, biased to flatter the trader.

---

## 8. Sizing and risk

Growth is positive only when true edge exceeds α/2 of estimated edge. **With t = 0.45 the 95% interval on true/estimated edge spans [−3.4, +5.4] — the lower bound is negative, so no Kelly fraction has guaranteed positive growth.** At p = 0.52 with 10% round-trip drag, Kelly is **−1.33%.**

**Rule: ≈0.2% of capital per long or spread position (0.217%, computed at an assumed p = 0.54 and κ_min = 0.25; at the measured p ≈ 0.52 the same rule returns zero); 4% aggregate short-premium cap.** At $100k this admits only ~9% of gate-passing contracts as single-leg longs (147 of 1,684 on 12 Nov, mostly low-priced names). **The cap's unit is undefined:** strand 11 words it as notional risk, under which a 25% index sleeve breaches it sixfold; under premium received it does not. Define it before build, and add a per-position limit for short premium — at present one undefined-risk short may be 18× the largest permitted long. Kelly must never size short premium — it prescribes near-half-bankroll for negatively skewed bets at identical expected value.

**Recovery is the binding constraint:** at 84 bp/yr, **26.7 years to recover 20%, 82.9 years to recover 50%.** Expected max drawdown for a zero-drift process grows as σ√T without bound — **never display a single MDD figure.**

**Vol targeting is substantially a backtest artefact** — lower certainty-equivalent return in 72 of 103 strategies in real time; momentum explains 45–60% of the apparent Sharpe gain. Tail-risk reduction is robust. **Cut size in stress, never add in calm.**

**Portfolio margin increases risk:** short strangle $227,360 → $75,999 (3×); **short calendar $300,460 → $7,500 (40×)** for identical economics. IBKR's sub-$100k surcharge moves requirements *toward* Reg T as equity falls. Lower combined margin is a statutory presumption of an offsetting straddle under §1092(c)(3).

**PDT:** approved 14 April 2026, effective 4 June, phase-in to 20 Oct 2027. **The intraday margin layer applies to stock, not options** — minimal effect on an options tool.

### 8a. Reminders do not work. Resting orders do.

Automated stop/take orders moved the disposition effect from +0.082 to **−0.106
(p=0.002)**, entirely by realising losses. A Reminder treatment — price limits that
only notify — measured **0.088, i.e. no effect at all.** Stop-loss users were, on
their *unstopped* trades, measurably **more** reluctant to realise losses
(HR 0.9555, p<.05).

The mechanism disciplines the trade, not the trader.

**Therefore a monitoring agent that sends notifications has no measured effect on
the disposition effect in the one experiment that tested it** (a laboratory study;
transfer to a single operator is assumed). Treat notifications as unproven and
resting orders as the default. An invalidation condition's output is a **resting broker order ticket**,
and order-placement rate is recorded per trade as a first-class metric. This
supersedes any earlier description of monitoring as alerting.

---

## 9. Tax

| Rule | App can do | Needs a CPA |
|---|---|---|
| **§1256 60/40** | Flag instrument class; compute differential | Partly resolved (strand 18): **XSP, NDX and RUT do get 60/40; SPY and QQQ are explicitly excluded.** Sector ETF options are equity options, not §1256. VIX still unverified |
| **§1092(a)(2) identified straddle** | **Immutable timestamped record at entry** — election requires *same-day* identification | Whether to elect |
| Straddle loss deferral | Flag offsetting positions | Application |
| Wash sales on options | Flag substantially identical repurchases | Edge cases |
| **Qualified covered calls** | **Blocking warning on ITM calls against short-term or appreciated long-term lots** | Confirmation |
| Year-end M2M on 1256 | Compute | Filing |

A futures delta-hedge adds §1256 and §1092 interactions to the overlay. Not researched — flag it.

The identified-straddle record is the highest-value, lowest-cost tax feature: a few lines of code preserving an irreversible dated option.

---

## 9a. Architecture constraints with evidence behind them

These are design prohibitions, not preferences. **The evidence behind the
model-behaviour and human-factors items is out-of-domain and largely unreviewed
(`agent-architecture.md` §8); treat the figures as priors, not measurements.**

- **The liquidity gate is deterministic code, upstream, non-overridable.** Gross
  returns are *higher* in illiquid terciles, so anything permitted to reason about
  exceptions will request them and be wrong.
- **Telling a model to be critical is mostly theatre.** Anti-sycophancy preambles
  *reduced* accuracy on most models tested (one preprint, flagged internally
  inconsistent); suppressing sycophantic agreement by 20.9
  points produced genuine-correction rates **below 0.6%**. Injected substantive
  flaws moved review scores −0.07 (ns) while an explicit "strong reject" sentence
  moved them −1.65 — the model tracks the stated verdict, not the reasoning.
  **Checklist first, LLM confined to what rules cannot do, veto gated
  structurally.**
- **Question reframing beats instruction by ~2×.** Converting the user's assertion
  to a question before the model sees it: latent sycophancy β 1.13 → 0.51
  (instructed) → **−0.55** (reframed). Preprocessing, not a prompt.
- **Base model choice dominates prompt-level mitigation.** Confident-false-expert
  follow rates measured 4%, 11% and 80% across generations — a ~20× spread.
- **Do not build debate or self-critique.** Intrinsic self-correction degrades
  (75.8 → 38.1, flipping 39.8% of correct answers to fix 5.8%); debate loses to
  plain majority voting at matched compute; and models that are wrong agree on the
  *same* wrong answer at 0.42–0.60 against a 0.13–0.33 chance baseline. Two
  instances of one model cannot find a blind spot they share.
- **Retrieval must be balanced, not disconfirming-first.** One-sided exposure drives
  model stance to endpoints, and the human reader is *moved* by a one-sided critic
  rather than discounting it (~16% polarity shift). Correctness problem, not a
  credibility one.
- **Never show a model confidence score.** Displayed confidence moves switch rates
  40.5% → 69.6% with no accuracy gain; users detect miscalibration 26–29% of the
  time. Show corpus evidence grades instead.
- **No agent writes to parameters.** ~45 trials on 60 monthly observations (Bailey et al.; ~12 on their conservative bound) before
  the zero-skill Sharpe bar reaches 1.0. A self-tuning loop spends that invisibly.
- **The post-mortem narrative has no write path** and is labelled unreliable.
- **Judge step-level, report κ.** Step-level judging scored 53.8–64.1 against
  35.1–43.9 for outcome-trained judges, and "85% agreement" has been measured at
  κ 0.48.

---

## 9b. Technical analysis: where it belongs

Earlier revisions said "render everything, score nothing," which **under-used the
evidence.** TA constructs have several roles the research supports, and they were
not implemented. This section corrects that.

### The reframe that resolves most of the tension

**There is no composite score in this system** (§11). The output is a transparent
ordinal panel with per-signal evidence grades visible. So "should TA be in the
scoring" is the wrong question — nothing is weighted into a number. **TA
constructs appear in the panel with their honest grades, like every other
component.** The user sees them and can act on them; the system has not laundered
them into a false precision.

### Roles the evidence supports

**1. Strike selection — a hypothesis, testable on the snapshot series.**
Support and resistance has a genuine microstructure mechanism: stop-loss and
take-profit order clustering at round numbers, with an asymmetry that explains both
reversal at levels and acceleration through them (Osler, *JF* 2003, FX order-book
data). This is **not a prediction task.** The step from FX order clustering to listed-option
strikes is untested: no strand shows option liquidity clustering at the underlying's
levels. One day of census data (15 Jan expiry, single names ≥$100) shows $10-multiple
strikes with higher median OI (1,133 against 832) but the same median spread (5.3%
against 5.4%) and pass rate. Test on the snapshot series before relying on it. Feed identified levels into strike choice within
the moneyness band.

**2. Barrier and resting-order placement.**
§8a requires invalidation conditions to emit **resting broker orders**, not
notifications. Where you place a resting order matters: a stop at a clustered level
sits where other orders are. Triple-barrier levels should be volatility-scaled
*and* snapped toward identified levels, rather than pure σ multiples. Same
mechanism as above, different application.

**3. Structure selection.**
Given a volatility view, trend direction picks put-spread versus call-spread, which
side to sell, and how far OTM. This is not alpha generation — it is expressing a
view with the right instrument. Moneyness dominates direction anyway (3% OTM weekly call −59% versus 1% OTM +12% — index weeklies bought at the ask), so getting structure right is worth more than
getting direction right.

**4. Risk filter and sizing — explicitly survived the research.**
Higher-timeframe trend filters **reliably improve drawdowns.** This was in the
findings and was not implemented. Consistent with §8's rule to cut size in stress
and never add in calm: size down against the higher-timeframe trend. The goal is
drawdown control, not prediction, and the evidence supports it in that role.

**5. Regime input.**
Higher-timeframe trend state feeds the Regime Assessor alongside VIX term structure.

**6. Event-window context.**
Where price sits relative to identified levels going into a scheduled event is
context the user wants and the system should show.

**7. Rendering, always.**
Users will not trust a chart tool without these drawings, and that is a legitimate
product requirement independent of predictive content.

### Honest grades for the panel

| Construct | Mechanism | Predictive | Panel grade |
|---|---|---|---|
| Support / resistance | **Moderate** — order clustering documented | Weak — automated levels fail to beat buy-and-hold | Moderate for placement, Weak for direction |
| Trend / momentum | Moderate | Weak per-ticker absolute; **Moderate for drawdown control** | Weak for entry, Moderate for sizing |
| Chart patterns | Weak | Weak — both cost-aware head-and-shoulders tests lost money | Weak |
| Candlestick patterns | — | **Strong null** — 22 of 28 rules significant on zero stocks across 83,220 observations | Display only |
| Fibonacci retracements | — | **Refuted in the one controlled study** (read at abstract level; control construction unconfirmed) — Fibonacci and non-Fibonacci zones did not differ statistically; bounce probability tracks zone *width* | Display only, labelled |
| Elliott wave | — | **No evidence, and no inter-rater reliability study in any literature** | Display only, labelled |

Showing a weak grade is not the same as excluding the construct. The panel's job is
to let the operator see what the evidence says and decide.

### The one real limit

**Correlated constructs are not independent confirmation.** Fibonacci levels,
support/resistance, pattern necklines and Elliott pivots are all computed from the
same swing extrema. "Five of six agree" mostly reports that one swing detector
fired five times. Adjacent trend horizons correlate **81–90%** (20d–60d ≈ 83%,
250d–500d ≈ 90%), and in one ablation **removing a horizon improved Sharpe
0.74 → 0.77**. Distant horizons are genuinely different (20d–500d ≈ 44%), which
supports a **two-point barbell** rather than a six-level ladder.

So: display each construct separately, never aggregate them into an agreement
count.

### The cheap test that settles multi-timeframe on your own data

Nearly free, no labels needed. Emit daily signed signals per (symbol, timeframe)
across ~100 underlyings, compute the correlation matrix, run PCA. **If PC1 exceeds
~70% of variance or adjacent correlations exceed 0.8, the timeframes are one or two
signals** — reduce to a barbell. If they are genuinely independent, that is a real
finding and the ladder is justified.

Run this before building confluence logic either way.

### Implementation non-negotiables

- **Confirmation lag on every pivot-derived construct.** ZigZag and fractal
  detectors structurally repaint. Without a lag the backtest reads the future; with
  one, production levels will visibly differ from the hindsight-perfect lines on a
  charting site. Decide which the product shows and say so.
- **Never assume a day-*t* open fill on a signal using day-*t* highs or lows** —
  measured at ~22–26 Sharpe points of inflation.
- **Fix the indicator warm-up window in config** so values are comparable across
  tickers.

---

## 9c. Sector and industry level — strand 18

**Verdict: the sector layer rescues nothing.** It is mostly a worse version of
problems already identified, with two useful exceptions.

### Industry momentum does not beat individual momentum

The source does claim industry momentum is the more profitable; its adjusted figures do not bear that out. Moskowitz & Grinblatt (*JF*
1999) measured industry momentum at 0.43%/mo raw and **0.20%/mo adjusted (t=2.27)**,
against 0.29%/mo adjusted for individual momentum — **comparable, not larger.**
Their actual claim was that industry-neutralising individual momentum kills it
(t=1.01). That has since been dismantled four independent ways:

- **Gap month.** Insert one month and it falls to an insignificant 0.16%/mo —
  roughly 60% of the headline was untradeable one-month reversal. The original
  authors themselves warn profits likely do not survive costs (break-even 75bp
  one-way at 200% turnover).
- **Connected-firm momentum** leaves no significant 4-factor alpha.
- **Factor momentum** in the top three PCs of industry-neutral factors subsumes
  *all* industry momentum, completely so in the later subsample.
- **Turnover.** The one industry-momentum result adding value over stock-level
  premiums needed **500% annualised one-way turnover** against 15–35% for stock
  factors; slowing the rebalance more than halved the alpha and killed
  significance.

The literature also contradicts itself — Asness, Porter & Stevens find *within*-
industry momentum has power beyond across-industry, directly against the 1999
claim.

**Cost arithmetic:** 0.4%/mo gross → ~0.16%/mo with a skip month → **2–3bp after
the project's 80–90% haircut.** Break-even in ETF *shares*; nowhere close in sector
ETF *options*. Strictly a cross-sectional rank, never per-sector absolute — no
evidence was found for a sector time-series momentum signal. The only implementable
study ends December 2009 with **no published post-2009 test.**

### Sector rotation is refuted

Granted **perfect ex-post NBER business-cycle timing**, in-sample only: Sharpe
**0.20 against the market's 0.21** and 0.26 for a naive move-to-cash. Costs of
0.5–1.5% cut an 11bp/mo gross edge to 1–7bp, insignificant. Of 1,022 variants,
12.9% beat buy-and-hold; of 2,160 predictability t-statistics, 6% positive and 5%
negative — chance. Under FF3/Carhart no industry outperforms. The raw edge is beta
1.04 and higher volatility.

Against this sits a large volume of asset-manager marketing with **no cost
accounting anywhere** (one widely-cited relative-strength result reports Sharpe
0.54 with costs excluded, 100–400% turnover and a −46% drawdown).

### "Sector ETF" is not a liquidity category

The actionable negative. Cboe-group option ADV, 2026 YTD:

| Liquid | ADV | Thin | ADV |
|---|---|---|---|
| SMH | 59.8k | XLK | 5.1k |
| XLE | 41.2k | XLY | 4.3k |
| XLF | 37.2k | XLV | **3.1k** |
| | | XLRE, XLC | not in top 100 |

**Five of eleven SPDR sectors are thinner in options than many large single names.**
Treat sector ETFs as individually measured instruments, with a chain-measured
whitelist — SMH, XLE, XLF plus any mid-tier that measures well — **re-measured
annually** (the 12 Nov census already measured three: XLF 9, XLE 6 and XLK 2
qualifying contracts at 42–90 DTE, all under the ≥10 screening bar), because Penny Interval Program membership turns over each January and
April and is conditional on the underlying trading under $200.

### One definitive negative and one gap on the ETF-substitution idea

- **No tax advantage.** Sector ETF options are equity options, **not §1256.**
  Moving a view from a single name to XLF changes nothing on tax.
- **No published sector-ETF VRP estimate exists.** A live XLF snapshot
  (12 Nov 2026) showed IV30 16 against HV30 18, but that is not evidence either
  way: HV30 contained the 5 Nov shock, and §6 rules out the raw comparison.

### Peer information transfer: volatility yes, direction no

- **Direction channel is dead.** Peer 3-day excess returns measured 0.09% and
  −0.19% — 9–19bp against a ~10%-of-premium hurdle, two orders of magnitude short,
  and in a non-US sample whose own moderators predict the US effect is weakest.
- **Volatility channel is real but untested as a strategy.** Peer implied vol
  transfers significantly around a first announcer's report, stronger for
  bellwethers and long-dated options — but it is **contemporaneous**, with spillover
  *magnitude* predictable and direction not, and **no drift or reversal over the
  following seven hours.** That rules out a latency trade.
- **Trigger density does not help.** Peer transfer multiplies event count 20–70×,
  but the binding constraint was never events — it was **tradeable chains** (36 of
  103 names carried ≥10 qualifying contracts).

### The one thing worth building from this strand

**Sector ETF IV30 as a third component in the volatility forecast.** Best
risk-adjusted candidate here because it is a *forecasting input, not a trade.*
Mechanism is supported (common idiosyncratic volatility; implied vol in HAR), the
specific claim is untested. **Must use VIX as the control, not the name's own
history** — if the common factor is market-wide, the sector layer adds nothing.

### Also dead or absent

No sector implied-correlation index exists (only SPX-based COR1M/COR3M). Sector
dispersion is untested, and the **SPX** dispersion premium is itself insignificant
(−0.19, p=0.155) while style baskets are significant — the opposite sign pattern to
what was assumed. Sector-relative valuation is a measurement improvement for
cross-sectional portfolios: use as a screen and display refinement, never a signal.

---

## 9d. Scheduled macro and geopolitical events — strand 19

**Verdict: the mechanism transfers; the trade does not, at this horizon.** The
decomposition works for macro events and tells us macro is too small to trade here.

### What transfers

- **Mechanically, fully.** Event jumps calibrate to FOMC/CPI/NFP from the SPX
  surface, cutting held-out IV error 0.1080 → 0.0926. **No new mathematics needed.**
- **Informativeness transfers, and beats earnings.** Implied FOMC event vol from
  0DTE options forecasts the realised announcement move at **R² 78–85%**, against
  ~28.5% for earnings — with zero power for pre-announcement windows, and skew
  carrying no directional content.
- **Bias direction is contested.** Event-day variance risk premia are significantly
  positive (S&P FOMC **+0.248\*\*\***, employment **+0.204\*\***); implied event
  distributions are measurably **too wide.**

### What kills it

Fitted jumps: **FOMC 0.81%, CPI 0.91%, NFP 0.10%.** A 0.81% jump is ~**0.69% of
total variance in a 60-day expiry**; a full 60-day window containing 2 CPI, 1 FOMC
and 3 payrolls is ~2.4%. **An earnings day can be 20–55% of the expiry's variance depending on base
volatility — roughly 30–80× a macro event** (57% is a worked example at 24% base
and 36% term volatility over 40 days). Corroborated independently: FOMC IV elevation is strong at 0 DTE,
weak at 2 DTE, **almost absent at 10 DTE.**

**Cost hurdle failed by ~30–60×:** granting macro the full earnings-scale ~10%
richness yields ~0.07% of variance (~0.035% of straddle value) against the measured 2% index cost at
42–48 DTE.

### And at 0 DTE, where the event does dominate, it is fairly priced

Realised/implied ratios: CPI 0.94, FOMC 0.94, payrolls 1.11 — **none
distinguishable from 1** — while **normal days run 0.89 [0.84, 0.94], reliably
rich.** Seller Sharpe **0.52 skipping release days, −0.49 on release days only.**

You are paid for selling volatility on boring days and charged for selling it on
event days. On FOMC specifically, four sources give four different signs.

### The one exception: elections

Largest event premium in the calendar — priced at **+5.1% ATM and +16.0% at 10%
OTM** — and the 2026 midterm VIX futures bump (17.4 September → 19.7 November) was
extractable months ahead **at tradeable maturities.** Richness concentrated in the
**wings**, which argues for defined-risk short-wing structures if ever acted on.

No cost-adjusted return test has been published. **Unverified candidate, not a
signal.**

### Cautionary episode, 5 November 2026

The S&P fell **4.4% with VIX up 70%**, one day after a benign election resolution.
An uncalendared shock that would have caught a "sell vol post-event" rule maximally
short. That is the tail the variance risk premium pays for, arriving in-sample.

### Geopolitical: regime input only, and weak

Lagged geopolitical risk **does not improve out-of-sample volatility forecasts as a
regressor**, alone or combined — but as a *regime-monitoring* variable it yields
~3% MSE gain at one month and ~10% longer. Effects are concentrated in emerging
markets and directly-exposed firms; the military-conflict effect is **not
significant for advanced-economy firms.** Sizing and structure gate, never an entry.

### Macro in the volatility forecast: almost nothing survives

Kitchen-sink augmentation gives MSFE ratios of **1.39 / 1.32 / 1.21 / 1.19** at
1–4 quarters — worse at every horizon. Only 4 of 20 variables survive Lasso.

Worth **one test each**: **credit/default spread** (survives at 1%) and **housing
starts** (beats even the selected benchmark at every horizon, MSFE 0.980 → 0.955).
**Reject:** MOVE, geopolitical risk as a regressor, event dummies, all-variable
augmentation. VIX term structure stays a display and regime indicator, not a
forecast input.

### And the pre-FOMC drift is dead

27.1bp decaying to **8.9bp and insignificant**, with a structural break in March
2016.

### Build consequence

**Macro calendar = display and regime context.** Show the implied event move; it is
legitimate and informative. Generate no entries from it. **Do not feed the macro
calendar into single-name event-vol modelling** — at 0.9% versus 20–55% of variance it
is third-order next to the name's own earnings.

---

## 10. What is dead

**Removed in revision 5:** single-name VRP harvesting as a thesis; single-name overlays and hedged modules; the 90–180 DTE band; the cheap-post-earnings-IV hypothesis; implied correlation as a per-name selector.

**Removed in revision 4:** the nine Zhan et al. delta-hedged characteristics (2.27% → **0.10%/month** on pre-trade-only information; alpha zero after May 2012; only 1 of 23 signal-weighted strategies survives IPCA, and the survivors are option-implied not fundamental); dynamic delta-hedging of single names at retail.

**Still dead:** unusual options flow (~42% direction error; intraday OI does not exist publicly). Fibonacci retracements (**refuted in the one controlled study, read at abstract level** — Fibonacci and non-Fibonacci zones did not differ statistically; bounce probability tracks zone *width*). Candlestick patterns (22 of 28 rules significant on zero stocks across 83,220 observations). Social sentiment as direction. Put/call ratio, put-call parity deviation, skew as direction. Retail GEX (market makers net *long* gamma ~88% of SPX 0DTE intervals). 13F. Accruals. Partial-notional risk reduction. Short-vol ETPs. A cardinal 0–100 score.

**No credible evidence found:** calendar/skew/surface relative value; gamma scalping; IV rank as a verdict (no peer-reviewed test in either direction); max pain (unproven); Elliott wave (no evidence, no inter-rater study in any literature); multi-timeframe confluence scoring (never tested in its practitioner form; adjacent horizons correlate 81–90% and removing one *improved* Sharpe — run the §9b test before building). Dispersion trading is real but not retail (21 legs monthly at 6–8% spreads; independent replications Sharpe 0.34–0.40).

---

## 11. Ranking and measurement

**No cardinal score.** Hard disqualifiers that **exclude**, then a transparent ordinal panel with evidence grades visible.

- **Primary metric, single-name event mode: mean net return per event with a t-statistic over events** — §4 removes the cross-section an IC needs. **For any ranking that survives: cross-sectional IC with IC-IR t-statistic**, not Sharpe. At 60 months with IC std ≈ 0.10, t=3 needs mean IC of 0.039; 0.10 presumes ~100 names, and at 22–36 names it is ~0.17–0.21, needing 0.065–0.08. Snapshots began 12 Nov 2026, so a 60-month verdict is not possible before late 2031.
- **Hurdle t > 3.0**; **t > 4** for any composite selected from a candidate set.
- **Trial budget ~45** (Bailey et al.; ~12 if their conservative upper bound is used deliberately) on 60 monthly observations before the zero-skill bar reaches Sharpe 1.0. Log every configuration from the first commit.
- **Evaluate the shadow portfolio** — every ranked contract labelled at resolution, traded or not.
- **Never build an in-app backtest-tuning feature.**
- **Benchmark per mode:** index overlay against volatility-matched passive equity; single-name events against that name's own realised post-earnings moves.
- **Haircut published equity effects 80–90%.** Breadth penalty for ranking the gated universe (size unmeasured; ≤36 names with depth on 12 Nov) instead of 3,000 is material — prefer absolute per-ticker readings over relative ranks.

### What cannot be measured about the operator

**Calibration, at any sample size this project will reach.** At n=100 the 95%
interval on one person's Brier score is **2–4× wider than the largest credible
forecasting-training effect**, and the standard Brier decomposition is biased at
small n in the *flattering* direction. Thresholds: nothing under 30; gross
miscalibration only at 30–100; an interval-bearing score at 100–300; a reliability
curve above 300. **Never display "you are well calibrated."**

Measurable at n=1, and these replace it: cost estimate versus realised, falsifier
compliance rate, resting-order placement rate, divergence from market-implied,
reference-class drift, premortem category hit rate.

### Elicitation constraints that bind the UI

- **Probability is captured as an integer percent in 1% steps.** Coarsening carries
  a measured Brier penalty of +11.8% at 3 bins and **+31.4% at 2 bins**. A
  low/medium/high conviction picker is the most destructive available choice.
- **No market data may be displayed before a thesis is frozen.** An implied
  probability is a consensus statistic on the same scale as the forecast — the
  configuration where anchoring is strongest, and it is robust to warnings and to
  accuracy incentives. Sequencing is the only defence; a banner is not.

---

## 12. What the system is

**A cost, execution and event-timing tool with two live modes and a thin, honestly-graded signal layer.**

**Index mode: shelved 15 November 2026.** No tested index-writing programme earned alpha after 2012 (§0b), so the system does not originate index trades. Index instruments are traded in on-demand mode, where the system shows cost, tail and the post-2012 base rate beside the operator's own structure.

**Single-name mode (built later, as a scan feeding on-demand mode):** gate hard on liquidity, treat richness as a tie-breaker only, and time entries to short premium after scheduled events — earnings being the best-evidenced instance (§4a) and the one signal in seven waves whose direction is supported offer-to-bid.

**On-demand mode:** you name the ticker; the system researches it and drafts a
thesis you can accept, edit or reject, then contributes cost analysis, probability
honesty, base-rate confrontation, sizing discipline and an immutable record. A
research assistant whose track record can be audited, not an oracle. The draft is
labelled unvalidated until that record says otherwise. See `docs/on-demand-mode-design.md`.

**Both live modes:** cut what you pay to trade by a measurable factor, strip event vol so you stop buying false "expensive" readings, route to the tax-advantaged instrument, size so a drawdown is not permanent, preserve the straddle election, and report honestly what the passive alternative returned.

Honest framing: *we cannot tell you which way the stock will go, and the premium in single names is not reliably positive. We can tell you what a contract will cost you, what the market is charging for the next earnings event versus what that event has historically delivered, where your own thesis is weak, and what you would have earned doing nothing.*

---

## 13. Open items, ranked

1. ~~Re-derive the index VRP on post-2012 data only~~ — **done 15 Nov** (§0b, Tests A–C). Outcome: Mode 1 shelved.
1a. **Build Mode 3** (`docs/on-demand-mode-design.md`), with the system-drafted thesis path. Unblocked; the build target. Needs a second model family for the Critic.
1b. **Test 42–90 DTE index writing** — the only route back for Mode 1. Needs purchased option data or several years of the snapshot archive. Not urgent. Do not substitute further Cboe index variants.
2. **§1256 eligibility for VIX** — XSP, NDX and RUT now confirmed as 60/40 (strand 18); SPY and QQQ explicitly excluded; sector ETFs are not §1256
3. **Measure sector ETF chain costs** for the ETFs not yet in the census (XLF, XLE, XLK already measured — §9c) — replaces every estimate in §9c with a number, and five of eleven SPDR sectors are thinner than large single names
4. **Test sector ETF IV30 as a third volatility-forecast component**, with VIX as the control — the one build-worthy item from strand 18
5. **Run the census against a real broad universe** (S&P 500 + Nasdaq 100 constituents). The 12 Nov run used a curated liquid list, so the ~250 question is still open. Raise the pass threshold to ≥5 contracts and make it a config flag.
6. **Explain the after-hours difference** (§0a) — spot prices agree within ~1%; new-expiry listing and quote withdrawal are the candidates
7. **Stamp every census run with the VIX level** — spread width is volatility-dependent, so universe size is regime-dependent and the series is uninterpretable without it
8. **Does the one-legged short-after-earnings trade survive costs?** Published cost-surviving figures are for the two-way strategy
9. **Reliable earnings dates with before/after-close timing** — binding constraint on event-vol stripping
10. **Confirm the Duarte et al. mapping** to the Zhan family before finalising its removal
11. **Does the model forecast add information beyond clean constant-maturity IV** at 42–90 DTE? Directly testable; both outcomes publishable. **The right capstone experiment.**
12. ~~Live MES margin~~ — only needed by the shelved overlay's hedge
13. **Post-2012 single-name VRP re-estimation** — nobody has done it
14. **Your own paid-spread fraction**, from a fill log, corrected for the 38% inside-BBO artefact
15. ~~Start daily chain snapshots~~ — **done 12 Nov**, launchd verified (rc=0, 32,524 rows). First scheduled run completed 11:35 PT 13 Nov (26,184 rows)
