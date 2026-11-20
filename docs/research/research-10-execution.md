# Research Strand 10: Execution Microstructure and Fill Quality for a Retail Options Trader

**Date:** 11 November 2026
**Scope:** US listed equity/index options, retail single account, execution-support tool.
**Framing premise inherited from prior strands:** selection edge is ~0; costs dominate; therefore paid-spread fraction is the largest controllable parameter in the system.

**Source labelling convention used throughout:** `[PEER-REVIEWED]`, `[REGULATORY]` (SEC/DERA/exchange rule filings/Form 606), `[WORKING PAPER]`, `[INDUSTRY/THINK-TANK]`, `[PRACTITIONER]`, `[BROKER MARKETING]`.

---

## HEADLINE RESULT

The central number for the whole product is now pinned by three independent sources that agree:

| Source | Measure | Marketable order | Patient/limit or auction | Ratio |
|---|---|---|---|---|
| SEC DERA 2025 (SPXW 0DTE) | net effective cost vs pre-trade mid, **including the cost of missed fills** | 1.00 of half-spread | 0.42 of half-spread | **2.4x** |
| Hendershott/Khan/Riordan, RFS 2026 | effective/quoted spread ratio (EQ) | 0.74 (continuous) | 0.38 (auction) | **1.9x** |
| SEC Roundtable data, Dec 2025 | median effective spread, within NBBO-width bin | electronic marketable | non-marketable in auction | **2.5–3.7x** |

**A retail options trader who uses marketable orders pays roughly 2–3.5x what the same trader pays using non-marketable limit orders with a disciplined fallback.** This is larger than any signal effect in strands 1–9, and it is measured net of non-execution cost in the DERA study. Execution is the edge.

---

## 1. LIMIT ORDER PLACEMENT AND FILL PROBABILITY

### CLAIM: In liquid short-dated index options, a midpoint-or-better customer limit order fills 63% of the time on a two-tick spread, and costs 42% of what a marketable order costs even after charging the full cost of every missed fill.
- **SOURCE:** Fu, Li, Musto & Pearson, "Hope at a Reasonable Price: Customer Use of Limit Orders in the 0DTE Market," SEC DERA Working Paper, March 2025. https://www.sec.gov/files/dera-hope-reasonable-prc-2503.pdf `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong.** Regulator-authored, full OPRA/exchange data, explicit counterfactual methodology, sequencing errors corrected.
- **The numbers (sub-$3 calls, bought, July 2023 period):**

| Quoted spread | Order placed | Fill rate | Net effective cost | Marketable cost | Paid fraction of half-spread |
|---|---|---|---|---|---|
| 2 ticks ($0.10) | at mid (only choice) | 62.8% | $0.021 | $0.050 | 0.42 |
| 3 ticks ($0.15) | 1 tick in (least aggressive) | 36% | $0.038 | $0.075 | 0.51 |
| 3 ticks ($0.15) | 2 ticks in (near mid) | 90% | $0.032 | $0.075 | 0.43 |
| 4 ticks ($0.20) | 1 tick in | — | $0.055 | $0.100 | 0.55 |
| 4 ticks ($0.20) | 2 ticks in | — | $0.042 | $0.100 | **0.42** |
| 4 ticks ($0.20) | 3 ticks in | — | $0.058 | $0.100 | 0.58 |

- **Methodology that makes this credible:** an unfilled limit order is replaced by a marketable order after **one second**, and the resulting worse price is charged against the limit-order strategy. So the 0.42 figure is net of non-execution cost under a near-worst-case replacement rule. The authors note this *understates* the benefit, because a real trader would be more selective about when to give up.
- **IMPLICATION FOR THE BUILD:** This is the app's primary coachable rule and its default cost assumption. Hard-code the default paid-spread fraction at **0.42 of the half-spread** for a patient-limit workflow in liquid names and **1.0 of the half-spread** for marketable, and let the user's own measured fill log override it (see MEASUREMENT SPEC).

### CLAIM: Fill probability is non-monotonic in aggressiveness — on wide (4-tick) spreads the *middle* aggressiveness level is cheapest, not the most aggressive.
- **SOURCE:** Fu, Li, Musto & Pearson, DERA 2025, as above. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Moderate.** One underlying (SPXW), one spread width, directionally clear but not replicated.
- **Interpretation:** the most aggressive level (3 ticks in on a 4-tick spread, i.e. 1 tick from the far side) fills often but captures little improvement; the least aggressive captures a lot but fills rarely and incurs replacement cost. The interior point dominates.
- **IMPLICATION FOR THE BUILD:** do not implement "always place at mid." Implement a placement ladder parameterised by spread width in ticks, defaulting to **mid on 2-tick spreads and one tick better than mid (toward your own side) on 3–4 tick spreads**, and expose the parameter for the user's own measurement to tune.

### CLAIM: When the quoted spread is four or more ticks, execution intensity for a resting order is near zero regardless of how aggressively it is priced.
- **SOURCE:** Cohen, Drake, Guo & Reisinger, "Liquidity Provision and Rebate Design in Option Markets," arXiv:2609.26606, 2026. https://arxiv.org/pdf/2609.26606 `[WORKING PAPER]`
- **EVIDENCE STRENGTH:** **Moderate.** Model calibrated to real SPXW Level-1 data, but it is a market-maker model and the claim is a calibration result, not a direct empirical fill-rate measurement.
- **IMPLICATION FOR THE BUILD:** a hard gate. If the spread is ≥4 ticks, a passive limit is unlikely to fill at all; the app should either (a) refuse to recommend the patient-limit workflow, (b) recommend a native complex order to access penny increments (see §3), or (c) recommend not trading that contract. Combined with the DERA 4-tick result, a 4-tick market is the boundary where patience stops working reliably.

### CLAIM: Retail limit orders fill ~65% of submitted quantity, with fill rate falling monotonically in distance from the quote, and retail limit orders beat marketable orders by ~9–10 bp of implementation shortfall *net of* opportunity cost.
- **SOURCE:** Anand, Samadi & Sokobin, "Retail Limit Orders," *Review of Finance* 30(2), 2026, pp. 459–. Working paper version: https://microstructure.exchange/papers/Retail%20Limit%20Orders%2004082025.pdf `[PEER-REVIEWED]`
- **EVIDENCE STRENGTH:** **Strong for equities, Weak as a direct options analogue.** 27M retail orders, 19 brokers, FINRA OATS. **But this is US equities, May 2020 only — not options.** Use the structure, not the levels.
- **The fill-probability ladder (equities):** inside the quote 83.0%; at the quote 76.2%; behind the quote within 5x spread 68.4%; behind beyond 5x spread 50.2%.
- **Opportunity cost of a missed fill:** ~15.9 bp average (13.6 bp large caps, 35.9 bp mid, 57.9 bp small), measured as the opposite-side quote at end of order life — which captures both adverse drift and the spread you then pay.
- **Net result:** limit-order IS ≈ −8.2 bp vs marketable +1.1 bp; advantage grows with spread width and volatility, and grows with passivity (beyond-5x-spread orders show IS 21 bp better than marketable).
- **Duration reality check:** retail limit orders live ~1,250 seconds on average vs ~6 s for marketable; 56% are cancelled within an hour.
- **IMPLICATION FOR THE BUILD:** three things. (1) The monotone fill-probability-vs-distance ladder is the right functional form to model. (2) The key cross-sectional result transfers and matters: **the passive-order advantage is largest exactly where spreads are widest and volatility highest** — which is where options live. (3) The DERA 1-second replacement rule is far more aggressive than real retail behaviour (1,250 s), which is why DERA's estimate is conservative.

### CLAIM: No credible evidence found for a published, calibrated fill-probability model specific to US options limit orders usable by a retail trader.
- **EVIDENCE STRENGTH:** **No credible evidence found.** The fill-probability modelling literature (Maglaras/Moallemi/Zheng deep-learning LOB fill probabilities, Cont et al., Moallemi queue-position valuation, Lo/MacKinlay/Zhang first-passage models) is all **equities/futures**, and depends on queue position and full depth data that OPRA does not give a retail trader. The options-specific work is either market-maker-side (Cohen et al. 2026) or empirical-tabulation (DERA 2025).
- **IMPLICATION FOR THE BUILD:** do not try to build a theoretical fill-probability model. Build an **empirical** one from the user's own fill log: a logistic regression of fill-within-T on (spread in ticks, placement in ticks from mid, minutes since open, option price bucket, underlying move since placement). This is the single highest-value piece of proprietary data the app can accumulate, and no public dataset substitutes for it.

### CLAIM: Adverse selection against patient options limit orders is small for cheap options but materially larger for options above $3.
- **SOURCE:** Fu, Li, Musto & Pearson, DERA 2025. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Moderate.**
- **Numbers:** for two-tick sub-$3 calls, a marketable order placed after a non-fill cost $0.057 vs $0.050 if sent immediately — a ~14% penalty. For options **above $3** with two-tick spreads, that post-non-fill cost rose from $0.10 to **$0.14** — a ~40% penalty. Separately, counterparty realised spreads on filled customer limit orders fell to **under one cent at the one-minute horizon** in the later period, i.e. market makers barely profit from filling these orders.
- **IMPLICATION FOR THE BUILD:** make the patience budget **price-dependent**. For options under ~$3 the cost of waiting is small and patience is nearly free. For options above $3, non-fill is penalised ~40%, so tighten the timeout and widen the initial placement toward marketable. Encode a threshold at the $3 tick-size boundary.

---

## 2. US OPTIONS MARKET STRUCTURE AND PRICE IMPROVEMENT MECHANISMS

### CLAIM: Price improvement auctions deliver about 67% of the quoted spread back as price improvement, cutting the effective/quoted ratio from 0.74 to 0.38.
- **SOURCE:** Hendershott, Khan & Riordan, "Option Auctions," *Review of Financial Studies* 39(3), March 2026, pp. 783–834, DOI 10.1093/rfs/hhaf043. Working paper: https://faculty.haas.berkeley.edu/hender/Option_Auctions.pdf `[PEER-REVIEWED]`
- **EVIDENCE STRENGTH:** **Strong.** Top-three finance journal, full market data.
- **Numbers (Table 5):**

| | Quoted spread | Effective spread | Price improvement | EQ ratio | MM revenue |
|---|---|---|---|---|---|
| Auction | 11.75c | **4.12c** | 7.62c | **0.38** | −0.59c |
| Continuous | 10.07c | 7.87c | 2.20c | 0.74 | +3.01c |
| PFOF auction | 13.62c | 4.69c | 8.93c | 0.37 | **−1.38c** |
| Non-PFOF auction | 9.56c | 3.47c | 6.09c | 0.38 | +0.34c |
| PFOF continuous | 11.16c | **10.19c** | 0.98c | **0.90** | +4.07c |
| Non-PFOF continuous | 9.74c | 7.17c | 2.57c | 0.69 | +2.69c |

- **Critical structural fact:** auctions are ~23% of single-leg option volume. PFOF-wholesaler auctions are 14.75% of total option volume. Market-maker revenue in PFOF auctions is **negative (−1.38c)** — wholesalers lose money on the trade itself and are compensated by the PFOF arrangement.
- **The worst place to be is a PFOF order in continuous trading: EQ of 0.90, i.e. you pay 90% of the quoted spread.** The best is any order in an auction: 0.37–0.38.
- **IMPLICATION FOR THE BUILD:** the app's single most valuable structural coaching point is **get the order into an auction rather than a continuous-book execution**. The ~2.4x difference (0.90 vs 0.37) between the worst and best cell in this table *is the product's value proposition*. Practically, auction participation is driven by order type: see the next claim.

### CLAIM: Non-marketable limit orders receive price improvement 80–99% of the time; marketable orders receive it 0–13% of the time on tight spreads.
- **SOURCE:** SEC Division of Trading and Markets, "Roundtable on Options Market Structure — Supporting Data," April 2026. https://www.sec.gov/files/roundtable-options-market-structure.pdf `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong.** SEC staff analysis of December 2025 OPRA + exchange data, Individual Customer capacity only — i.e. *exactly* the population the app serves.
- **Price improvement frequency, Individual Customers, December 2025, by NBBO width bin:**

| | nickel | dime | quarter | dollar | $5 | >$5 |
|---|---|---|---|---|---|---|
| **Marketable**, electronic (14.7M orders) | 0% | 0% | 1% | 4% | 5% | 13% |
| **Marketable**, single-leg auction (6.06M) | 22% | 53% | 51% | 83% | 89% | 83% |
| **Non-marketable**, electronic (27.5M) | **80%** | 83% | 90% | 96% | 98% | 99% |
| **Non-marketable**, auction (23.1M) | **96%** | 96% | 97% | 98% | 99% | 99% |
| Single-leg floor, marketable (9,894) | 0% | 0% | 0% | 0% | 0% | 0% |

- **Median effective spread, same data (dollars):**

| | nickel | dime | quarter | dollar | $5 | >$5 |
|---|---|---|---|---|---|---|
| Marketable, electronic | 0.01 | 0.05 | 0.10 | **0.37** | **1.73** | **6.68** |
| Marketable, auction | 0.02 | 0.05 | 0.10 | 0.17 | 0.82 | 2.98 |
| Non-marketable, electronic | 0.01 | 0.05 | 0.10 | 0.15 | 0.61 | 2.45 |
| Non-marketable, auction | 0.01 | 0.02 | 0.04 | **0.10** | **0.49** | **1.83** |

- **Within-bin ratios (the apples-to-apples comparison):** non-marketable-in-auction vs marketable-electronic is 0.27 in the dollar bin, 0.28 in the $5 bin, 0.27 in the >$5 bin. **A patient limit order that lands in an auction costs roughly 27% of what a marketable electronic order costs** in wide-spread options.
- **Caveat on reading the table:** these are bin medians, and the bin labels are NBBO-width buckets rather than exact widths, so the absolute figures cannot be converted to a fraction-of-quoted-spread directly. The *within-bin ratios* are the trustworthy quantity.
- **Structural shares:** non-marketable orders are **42.8–78.8% routed to auctions** depending on bin; marketable orders only 21–44%. Auction utilisation is 30–40% across most bins. Electronic is 39.7% of dollar volume, single-leg auctions 20%.
- **IMPLICATION FOR THE BUILD:** this is the strongest single piece of evidence in the strand and it is about *this exact population*. Two coachable facts: (1) **a marketable order on a tight-spread option gets price improvement essentially never (0–1%)**; (2) a non-marketable limit gets it 80–99% of the time. The app should treat "did you use a non-marketable limit?" as the primary execution-quality question and surface the expected cost difference inline at order-entry time.

### CLAIM: Exchange price improvement auctions in 2026 are AIM and SAM (Cboe C1/EDGX), SUM (Cboe automated pre-routing exposure), PRISM (Nasdaq), PIP (BOX), PRIME (MIAX), with auction exposure windows of ~100ms and response-processing tails of 100–900ms.
- **SOURCES:** Cboe, "Cboe Titanium U.S. Options Auction Process," v1.1.34, 14 Sept 2026, https://cdn.cboe.com/resources/techspec/technical-specifications-cboe-titanium-u-s-options-auction-process.pdf; Cboe, "Cboe Titanium U.S. Options Complex Book Process," v1.2.74, 2026, https://cdn.cboe.com/resources/techspec/technical-specifications-cboe-titanium-u-s-options-complex-book-process.pdf; MIAX PRIME specification, https://www.miaxglobal.com/miax_prime.pdf `[REGULATORY / exchange specification]`
- **EVIDENCE STRENGTH:** **Strong** for mechanics (primary exchange specs, current versions).
- **Verified 2026 mechanics:**
  - **AIM** (Cboe C1 and EDGX): a member broadcasts an agency order for price improvement; up to 10 contra parties; initiator can elect Auto-Match, Last Priority, or ISO. **A customer order resting at the final price fills ahead of the initiator's entitlement.**
  - **SAM**: AIM for orders ≥500 contracts; no Auto-Match or Last Priority; responses capped at NBBO.
  - **SUM**: system-generated exposure of marketable orders before routing/cancelling/posting. **Exposure cut from 50ms to 10ms, effective 4 Sept 2026 on C2/EDGX and 8 Sept 2026 on C1.** This is a 2026 change — training data on this is stale.
  - **COA** (complex order auction): 100ms Response Time Interval, plus up to 100ms (900ms on C1) tail for responses that arrived before the scheduled end. **On C1, only Customer and Pro-Customer capacities can initiate a COA.**
  - **QCC**: ≥1,000 contracts, limit within NBBO, immediate, no exposure. **Not retail-relevant.**
  - Auction data goes out on Cboe's PITCH and Auction feeds, **not OPRA** — so a retail data subscription cannot see auctions happening.
- **IMPLICATION FOR THE BUILD:** two actionable points. (1) The COA restriction to Customer/Pro-Customer capacity on C1 means **a retail complex order is privileged** — it can initiate an auction that a market maker cannot. This is a genuine structural advantage and the app should exploit it by preferring native complex orders. (2) Auctions resolve in ~100–200ms, so there is no human-timescale action to take once submitted; all the leverage is in the pre-submission decision. Do not build any "monitor the auction" feature.

### CLAIM: Options PFOF is roughly ten times equity PFOF for the same dollar invested, is ~two-thirds of all PFOF, and is paid at ~$0.26–0.69 per contract depending on broker and order type.
- **SOURCES:** Ernst & Spatt, "Payment for Order Flow," https://foster.uw.edu/wp-content/uploads/2022/07/4a-Ernst_Spatt-Payment-for-Order-Flow.pdf `[WORKING PAPER]`; SEC Roundtable Supporting Data, April 2026 `[REGULATORY]`; Committee on Capital Markets Regulation, "Retail Options Market Study," 17 June 2025, https://capmktsreg.org/wp-content/uploads/2025/06/CCMR-Staff-Report-Retail-Options-Market-Study-6.17.25.pdf `[INDUSTRY/THINK-TANK]`; Tastytrade Form 606, Q4 2024, https://cdn.finra.org/606/2024/277027_606_NMS_2024_Q4_V1.pdf `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong** on magnitude and concentration; **Moderate** on the causal link to execution quality.
- **Numbers:**
  - Options PFOF ≈ 40c per 100 shares (≈ per contract) vs 20c for equities; **$1,000 in a $5 option generates ~80c of PFOF vs ~8c for $1,000 in a $25 stock — ~10x** (Ernst & Spatt).
  - Options PFOF is **two-thirds of all PFOF**; top five recipients get >95%; **top three providers account for as much as 90% of options PFOF** (SEC 2026).
  - **CCMR 2025, six brokers, 2024 Form 606 averages:** PFOF per contract was **26.73c on market orders and 32.99c on non-marketable limit orders — ~23% higher for limit orders.** Order mix: market 7.45%, marketable limit 15.21%, **non-marketable limit 48.05%**, other 29.33%. Non-directed orders were 99.84–100% of all orders.
  - **Tastytrade Q4 2024 options routing: 100% to three wholesalers** — Dash/IMC 42.08%, Citadel 39.15%, Wolverine 17.11% — at a disclosed per-contract rate of $0.58–0.69, varying semi-monthly.
- **IMPLICATION FOR THE BUILD:** two implications, one of which is counterintuitive. (1) The wholesaler pays *more* for your non-marketable limit order than your market order, which is consistent with the Hendershott finding that wholesalers lose money on the trade and make it back on PFOF — the wholesaler's economics do not require you to get a bad fill on a limit order. (2) **Non-directed orders are ~100% of retail options flow.** Routing is effectively not something the retail trader exercises per-order; the lever is broker choice and order type, not per-order routing. Do not build a routing-selection feature.

### CLAIM: SEC Rule 605 does not cover listed options, so there is no mandated, standardised, comparable execution-quality disclosure for options at all. Rule 606 covers options routing and PFOF but not execution quality.
- **SOURCES:** Clear Street, "Rule 605 and Rule 606 Reporting," https://www.clearstreet.io/legal/rule-605-606-detail `[INDUSTRY]`; CCMR Staff Report, June 2025 `[INDUSTRY/THINK-TANK]`; SEC, "Disclosure of Order Execution Information," 89 FR (15 April 2024), https://www.federalregister.gov/documents/2024/04/15/2024-05556/disclosure-of-order-execution-information `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong.** Rule 605 applies to market centers in NMS *securities*; the 2024 amendments expanded the scope of reporting entities and added metrics but did **not** extend it to listed options. CCMR explicitly states options markets have no mandated execution-quality disclosures and recommends extending Rule 605 to options.
- **What Rule 606 for options does give you:** quarterly, per-venue, for non-directed options orders under $50,000 market value, broken out by market / marketable limit / non-marketable limit / other, plus material relationships and net payment received. That is **routing and PFOF, not price**.
- **IMPLICATION FOR THE BUILD:** **you cannot compare brokers' options execution quality from public disclosures. Full stop.** Any broker-comparison feature built on Rule 605 data would be wrong, because the data does not exist for options. Note that at least one popular broker-comparison site (stockbrokers.com) incorrectly points readers to Rule 605 for options comparison. The app must instead rely on (a) the two experimental studies in §7 and (b) the user's own measured fill log. This absence is itself the strongest argument for building the measurement module.

---

## 3. COMPLEX ORDERS VERSUS LEGGING

### CLAIM: Buying a vertical spread as a native complex order rather than two single-leg trades can save up to 83% of transaction costs.
- **SOURCES:** Li, Musto & Pearson, "Costs of Executing Complex Options Trades," SSRN 4389665, 2023, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4389665 `[WORKING PAPER]`; cited and relied upon in SEC DERA, "Simple Rules for Complex Options," March 2025, https://www.sec.gov/files/dera-simp-rule-complx-opt-2503.pdf `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Moderate-to-Strong.** The primary paper is a working paper and I could not retrieve its full text (SSRN blocked); however the 83% figure is reported and endorsed in an SEC DERA working paper, which is a meaningful validation. Treat the headline number as an upper bound ("up to") rather than a central estimate.
- **IMPLICATION FOR THE BUILD:** **This is the single largest cost effect found anywhere in this strand, larger even than the marketable-vs-patient effect.** Given that prior research established 58–76% of retail SPX open-position notional is multi-leg, the app's default must be **native complex orders, never legging**. If the app has one hard rule, this is it.

### CLAIM: Complex orders trade in $0.01 net increments even when the individual legs are restricted to $0.05 or $0.10 ticks — a strictly larger price grid than legging can reach.
- **SOURCE:** Cboe, "Cboe Titanium U.S. Options Complex Book Process," v1.2.74, 2026 (verified current). `[REGULATORY / exchange specification]`
- **EVIDENCE STRENGTH:** **Strong.** Primary exchange specification.
- **Verified detail:** net prices are **$0.01 on EDGX, C2 and BZX for any ratio**; on C1, $0.01 for most classes but **$0.05 for SPX/SPXW/SPXO** (box and roll spreads may use $0.01). **Leg execution prices print in $0.01 increments for complex orders of any ratio on all venues.**
- **This is almost certainly the mechanism behind the 83% figure.** On a 2-leg vertical where each leg has a $0.05 tick, legging forces you onto a $0.05 grid per leg; the complex book lets you name a net price on a $0.01 grid. On a $0.20-wide net market you can bid $0.01 better than the resting book instead of $0.05 better.
- **IMPLICATION FOR THE BUILD:** the order-entry module must compute and display the **net debit/credit** as the primary price, in $0.01 increments ($0.05 for SPX/SPXW on C1), and must never present the trade as two separate leg prices. Build the net-price ladder, not two leg ladders.

### CLAIM: Complex price improvement auctions deliver the best price improvement of any electronic complex protocol; legging a complex order through the single-leg books produces the *worst* effective spreads.
- **SOURCE:** SEC DERA, "Simple Rules for Complex Options," March 2025. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Moderate.** Directionally clear with order-characteristic controls, but DERA reports no effective-spread levels in cents or basis points for this comparison.
- **Ranking established:** C-PIA (best price improvement relative to the net NBBO implied by single-leg quotes) > C-LOB > execution via single-leg books (highest effective spreads).
- **Context:** complex volume rose from 26% to 38% of total options volume 2011–2019; exchanges offering complex protocols grew from 7 of 14 (2016) to 11 of 16 (Jan 2022). Complex-book quotes are **not disseminated through OPRA**.
- **IMPLICATION FOR THE BUILD:** because the complex book is invisible on OPRA, the app's displayed "net mid" computed by summing leg mids is a **synthetic** price that may be materially worse than the real complex market. Label it as synthetic. Coach the user that the true net market is usually tighter than the sum of the legs, and therefore that an order placed at the synthetic mid is often not aggressive — it may be well inside the real complex market and fill immediately, or well outside and never fill.

### CLAIM: Legging carries two distinct risks — paying the spread multiple times, and incomplete execution leaving a naked leg; and non-marketable legging additionally exposes the trader to being picked off.
- **SOURCE:** SEC DERA, "Simple Rules for Complex Options," March 2025. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Moderate** (reasoned regulatory analysis, no quantification of the naked-leg risk).
- **IMPLICATION FOR THE BUILD:** if the app ever supports legging (it should not, by default), it must model the unhedged-leg exposure explicitly. The risk is not just cost — it is an unintended directional position.

### CLAIM: Complex orders partially fill while preserving the leg ratio; and many common retail structures are specifically barred from legging into the single-leg books.
- **SOURCE:** Cboe Titanium Complex Book Process spec, 2026. `[REGULATORY / exchange specification]`
- **EVIDENCE STRENGTH:** **Strong.**
- **Verified mechanics:**
  - Ratio is reduced to lowest terms (a 2:2 must be sent as 1:1); the ratio is what allows partial execution in proportion. **A partial fill on a complex order leaves you with a smaller but still fully hedged position, not a naked leg.** This is the key risk-management difference from legging.
  - **Cannot leg in:** orders with ≥5 option legs; 3- or 4-leg orders where all legs are buys or all are sells; 2-leg orders where both legs are the same side and the same type (both calls or both puts) unless they are COA-eligible customer orders.
  - Books permit 2–16 legs. Complex orders with stock legs only on C1 and EDGX. Stock legs may print up to $0.25 outside the equity NBBO to achieve the package price.
  - Complex AIM executions may occur outside the synthetic NBBO but must be within the synthetic BBO.
- **IMPLICATION FOR THE BUILD:** the partial-fill-preserves-ratio property is a strong argument to present to the user, because the usual retail fear about complex orders ("I'll get half a spread") is **wrong on the exchanges' own rules**. Also: the "cannot leg in" list means a long call vertical (2 legs, same type, opposite sides) *can* leg, but a call calendar or a same-side structure cannot — the app should not promise legging behaviour it cannot predict.

### CLAIM: Multi-leg orders are heavily used by retail but the retail multi-leg *share* is not well documented in the sources I could reach.
- **EVIDENCE STRENGTH:** **Weak / partially no credible evidence found.** The SEC Roundtable data states multi-leg and complex orders were the second and fourth most common sale conditions for Individual Customers in December 2025 but **gives no percentage**. DERA's "Simple Rules" paper does not report the retail share of multi-leg volume. DERA's 0DTE paper found complex trades are a much smaller set than single-leg LOB trades in SPXW, and that among complex customer-interest trades the limit-order share *fell* from 59% to 37%.
- **IMPLICATION FOR THE BUILD:** the prior strands' 58–76% figure for retail SPX multi-leg *open-position notional* is not contradicted but is also not corroborated by these sources; note the distinction between notional and trade count. Do not over-claim.

---

## 4. TIME-OF-DAY AND CALENDAR EFFECTS

### CLAIM: Option percentage bid-ask spreads are L-shaped intraday: elevated at the open, dropping sharply, and stable after roughly the first 90 minutes.
- **SOURCE:** Chen, J., "Patterns and Determinants of the Intraday Bid-Ask Spread and Depth of CBOE Equity Options," M.Sc. thesis, University of Saskatchewan, 2017/2018, https://harvest.usask.ca/items/185eee73-6ce2-422e-9a11-c6fb47c0e9d0 `[WORKING PAPER / thesis]`
- **EVIDENCE STRENGTH:** **Moderate.** Quote-level OPRA data for CBOE equity options Jan–Mar 2010, thirteen 30-minute buckets. A master's thesis, and the data is 16 years old. It replicates Chan et al. (1995), which is the canonical reference.
- **Also found:** option depth is reverse-U-shaped; underlying stock spread is reverse-S-shaped; near the close market makers **maintain the spread but cut depth**.
- **IMPLICATION FOR THE BUILD:** avoid the first 90 minutes for non-urgent entries; prefer mid-session. Near the close, expect the quote to look normal but be thin — so size, not price, is the problem at the close.

### CLAIM: In SPX index options the intraday pattern is not a clean U — percentage spreads peak around 10:00, decline through the first hour, stay stable until 16:00, bounce at 16:00 and fall at 16:15.
- **SOURCE:** Cao, Jacobs & Ke, "Derivative Spreads: Evidence from SPX Options," AFA, https://afajof.org/management/viewp.php?n=12068 `[WORKING PAPER, AFA-presented]`
- **EVIDENCE STRENGTH:** **Moderate-to-Strong.** SPX options, Jan 2004–Dec 2020, 315,223 call and 496,307 put contract-days. But **the sample is 14–180 DTE and excludes weeklies**, so it says nothing about 0DTE.
- **Determinants quantified (first-differenced, contract fixed effects):** realised volatility coefficient on percentage spread 0.026 (calls) / 0.014 (puts), i.e. one SD of vol adds ~0.25% / 0.14% to the percentage spread; absolute end-user demand imbalance 0.049 / 0.080, strongest for OTM and fading near the close; absolute supply imbalance (depth) negative ~−2 and persistent; market-order imbalance 0.212 / 0.146. One SD of vol adds ~2.22c (calls) / 5.80c (puts) to the dollar spread.
- The authors explicitly contrast with Chan et al. (1995), who found the widest option spreads at the open — so the "avoid the open" rule is weaker for index options than for equity options.
- **IMPLICATION FOR THE BUILD:** the practical rule is **not** a fixed clock rule but a volatility-and-imbalance-conditioned one. The app should widen its expected-cost estimate when realised vol is high, and should flag that a spread that looks wide may be wide for a reason (vol/imbalance) rather than being a temporary dislocation worth waiting out.

### CLAIM: Option spreads widen at the open and close, and short-dated options are materially more expensive: mean effective spread is ~8.7–9.5% for 0DTE versus ~2% at 42–48 DTE.
- **SOURCE:** "Risky Intraday Order Flow and Option Liquidity," 23 May 2025 (authors not stated in the retrieved copy; hosted by Doshi, U. Houston), https://www.bauer.uh.edu/hdoshi/docs/DPS_May_2025.pdf `[WORKING PAPER]`
- **EVIDENCE STRENGTH:** **Moderate.** Recent, directly relevant maturity ladder; but I could not confirm the author list from the retrieved text.
- **Numbers:** mean effective spread 8.7% (0DTE calls), 9.5% (0DTE puts), 6.2%/6.3% (1–6 DTE), falling to ~2.0%/1.9% (42–48 DTE). Even liquid ATM short-dated options can show spreads up to ~10% of the option price. Intraday order-flow *volatility* predicts higher daily effective spreads (coefficient 0.020 for 0DTE calls, 0.023 for 0DTE puts), and the effect is about twice as strong for ultra-short maturities as for the longest. The sensitivity is highest at midday (0.020 at 12:00–13:00) and lowest late (0.005 at 15:00–16:00) for 0–6 day calls, and the relationship survives excluding the first and last 30 minutes.
- **IMPLICATION FOR THE BUILD:** **maturity choice is a cost decision of the same magnitude as execution tactics.** Moving from 0DTE to ~45 DTE cuts the effective spread by a factor of ~4.5. The app should display expected round-trip cost as a function of DTE at strategy-selection time, before execution tactics are even considered. This partially subsumes the execution question: the cheapest way to improve execution is often to trade a longer-dated contract.

### CLAIM: In SPXW, quoted spread width has compressed dramatically since 2020 and the near-money spread narrows as the day progresses.
- **SOURCE:** Fu, Li, Musto & Pearson, DERA 2025. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong.**
- **Numbers:** for ATM SPXW in July 2020, the BBO was one tick wide only **0.5%** of the time and ≥3 ticks wide **76%** of the time. By July 2023 it was one tick wide **64.7%** of the time and two ticks wide 35.3%. Intraday, July 2023 showed almost no wider BBOs **except at the end of the day**. In January 2023 data, mid-day calls $15–20 OTM reached the $0.05-tick range while just-OTM calls did not until the **last hour**.
- **IMPLICATION FOR THE BUILD:** two points. (1) Any cost model calibrated on pre-2021 options data is badly stale for index options — spreads compressed by roughly an order of magnitude in tick terms. (2) For near-money 0DTE specifically, the spread *narrows* into the last hour as the option price falls below the $3 tick boundary — which is the opposite of the general "avoid the close" rule. The app's time-of-day guidance must be conditional on option price relative to $3, not a blanket rule.

### CLAIM: No credible evidence found for a documented effect of OPEX, triple-witching or expiration day on options bid-ask spreads or retail execution quality.
- **EVIDENCE STRENGTH:** **No credible evidence found.** Searches returned only practitioner blogs (SpotGamma, Bookmap, gexmetrix, nexusfi, united-daytraders) covering gamma/pinning *price* effects, not spread or execution-quality effects. The academic pinning literature concerns underlying price behaviour, not option transaction costs.
- **IMPLICATION FOR THE BUILD:** do not implement OPEX-specific execution rules. If the user wants one, the app should say the evidence is absent and let their own fill log answer it — this is a good first use of the measurement module.

---

## 5. QUOTE QUALITY AND DATA HYGIENE

### CLAIM: Raw OPRA trade data is systematically out of sequence, making a naive comparison of trade price to prevailing quote wrong — 38% of trades in one sample appeared to execute inside the BBO, which is impossible.
- **SOURCE:** Fu, Li, Musto & Pearson, DERA 2025. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong.** This is the single most important data-hygiene finding in the strand.
- **Numbers:** in uncorrected OPRA data, **38% of trades in a July 2022 sample appeared to execute strictly inside the BBO**. After correction, **89.3% of trades were out of sequence in July 2020**; the in-sequence share rose to 37.8% by January 2023, then fell to 16.3% by September 2023.
- **IMPLICATION FOR THE BUILD:** **this invalidates the naive implementation-shortfall calculation.** If the app computes effective spread by matching its own fill timestamp against a quote snapshot pulled from a data feed, the sequencing error can swamp the signal — and it will do so in a *direction that flatters the trader* (apparent inside-the-spread fills). The app must snapshot the NBBO **at the moment of order submission, from its own local observation**, and store it immutably. Do not reconstruct the benchmark quote after the fact from historical data.

### CLAIM: Option prices are very noisy, and the bid-ask midpoint is a poor proxy for value — noise materially biases inferences drawn from option returns.
- **SOURCE:** Duarte, Jones & Wang, "Very Noisy Option Prices and Inference Regarding the Volatility Risk Premium" (earlier titled "...Inferences Regarding Option Returns"), 2022. Semantic Scholar record: https://www.semanticscholar.org/paper/14779bb77bcb156b7d6b03fa2e5a109acc080196 `[PEER-REVIEWED / working paper]`
- **EVIDENCE STRENGTH:** **Weak as reported here.** I could not retrieve the paper's full text or its specific filter list and noise magnitudes within budget (the hosting server was unreachable from this environment and the publisher page was off-allowlist). The existence and thrust of the result is well established; **the specific quantities should be verified before being used in the build.** Related: Goyenko & Zhang, "Price Pressures and Noise in Option Returns," https://ruslangoyenko.com/wp-content/uploads/2020/05/Option-Returns-MAY-24-2020.pdf `[WORKING PAPER]`.
- **IMPLICATION FOR THE BUILD:** treat any single-snapshot option mid as a noisy estimate. Flag this as an **OPEN QUESTION** requiring follow-up rather than coding a specific filter from it.

### CLAIM: Market makers maintain the quoted spread near the close while reducing depth, so a normal-looking quote can be non-actionable in size.
- **SOURCE:** Chen (2017/2018), U. Saskatchewan thesis. `[WORKING PAPER / thesis]`
- **EVIDENCE STRENGTH:** **Moderate.**
- **IMPLICATION FOR THE BUILD:** the actionability test must use **size at the quote, not just the quote**. A tight spread with one contract of depth is not a tight market for a ten-lot.

### CLAIM: Far-OTM options frequently have no bid at all and an offer pinned at the minimum tick, and customer interest in options more than 0.5% ITM is negligible.
- **SOURCE:** Fu, Li, Musto & Pearson, DERA 2025. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong** for SPXW.
- **Also:** peak customer presence at the bid moved from 1.0–1.5% OTM (July 2020) to 0.5–0.75% OTM (July 2023), and customer bid-side presence rose from ~40% to ~60% of the day.
- **IMPLICATION FOR THE BUILD:** a concrete non-actionable-quote test. If bid = 0, there is no mid and no two-sided market; the app must refuse to compute a mid and must not display a "spread". Define the tradable universe by liquidity, not by strike availability: for index options, roughly the 0.5%-OTM to ATM band is where customer liquidity actually is.

### CLAIM: OPRA quote traffic has grown ~90% in quote-to-trade terms since 2017, to ~131 billion messages per day, while the equity SIP ratio *fell*.
- **SOURCE:** SEC Roundtable Supporting Data, April 2026. `[REGULATORY]`
- **EVIDENCE STRENGTH:** **Strong.**
- **Numbers:** OPRA quote-to-trade ratio 9,133 (2017) → 17,398 (March 2025), +90%. Equity SIP ratio 17 → 13, −24%. Median daily OPRA messages ~9 billion (Jan 2017) → ~131 billion (Dec 2025). Exchange fragmentation: in 2025 no exchange exceeded 20% share and 18 venues each held over 1%, versus 2017 when the top three each held over 10%.
- **IMPLICATION FOR THE BUILD:** a quote you observed is stale within milliseconds, and the 17,398:1 quote-to-trade ratio means most quote updates are not tradable interest. Any app feature that depends on quote *stability* (e.g. "the mid is $1.23, place your order there") must re-check immediately before submission. Also: the app should not attempt to consolidate 18 venues; use the NBBO and accept it.

---

## 6. MEASURING YOUR OWN EXECUTION

### CLAIM: The correct benchmark for a retail options fill is the NBBO midpoint prevailing immediately before order submission, with unfilled orders charged the cost of the marketable order that replaces them.
- **SOURCE:** Methodology from Fu, Li, Musto & Pearson, DERA 2025 `[REGULATORY]`; implementation-shortfall framing from Anand, Samadi & Sokobin, *Review of Finance* 2026 `[PEER-REVIEWED]`.
- **EVIDENCE STRENGTH:** **Strong.** Both the regulatory and the peer-reviewed study converge on this design.
- **Why pre-submission mid and not fill-time mid:** using the fill-time mid lets the trader take credit for favourable drift during the order's life and conceals the cost of waiting. The DERA design — benchmark against the pre-submission BBO midpoint, and charge non-fills the replacement cost — is the only construction that makes patient and marketable strategies comparable.
- **IMPLICATION FOR THE BUILD:** see MEASUREMENT SPEC below. This is the module that turns the pivotal unknown parameter into a measured one.

### CLAIM: Effective spread, quoted spread, realised spread and price improvement are each separately computable from a retail fill log plus a submission-time quote snapshot, and their decomposition attributes slippage to its sources.
- **SOURCE:** Standard microstructure definitions as operationalised in Hendershott, Khan & Riordan (RFS 2026) `[PEER-REVIEWED]` and SEC Roundtable Supporting Data (2026) `[REGULATORY]`.
- **EVIDENCE STRENGTH:** **Strong** (definitional, with regulator and journal usage).
- **Note on realised spread:** DERA measured counterparty revenue at one second and one minute after the fill, finding MTO realised spreads *shrink* from 1s to 1min while PO realised spreads *grow*. A retail trader can compute the same quantity and it is the cleanest available test of whether they are being adversely selected.
- **IMPLICATION FOR THE BUILD:** compute all four, plus realised spread at 1s/1min/5min horizons. Realised spread is the diagnostic that distinguishes "I paid a wide spread" from "I was picked off."

---

## EXECUTION PLAYBOOK

Ordered, codeable rules. Each cites its evidence.

**Stage 0 — Before the trade exists: choose a cheaper contract.**

1. **Display expected round-trip cost as a function of DTE at strategy-selection time.** 0DTE ≈ 8.7–9.5% effective spread; 1–6 DTE ≈ 6.2–6.3%; 42–48 DTE ≈ 1.9–2.0%. *(Doshi et al. 2025.)* A ~4.5x cost reduction from maturity choice dominates every execution tactic below. Make this the first thing the user sees.
2. **Restrict the tradable universe by observed liquidity, not by strike availability.** For index options, customer liquidity concentrates roughly 0.5%-OTM to ATM; interest beyond 0.5% ITM is negligible, and far-OTM strikes often have no bid. *(DERA 2025.)* Gate: reject any contract where bid = 0, or where size at the touch is less than the intended order size.
3. **Compute and store `spread_ticks = round(quoted_spread / tick_size)`** where tick = $0.05 below $3 and $0.10 at/above $3. Every rule below branches on this. *(DERA 2025.)*

**Stage 1 — Order construction.**

4. **If the trade has more than one leg, always submit it as a native complex order. Never leg in.** Up to 83% cost saving vs two single-leg trades; legging through single-leg books produces the worst effective spreads of any complex protocol. *(Li/Musto/Pearson 2023; SEC DERA "Simple Rules" 2025.)*
5. **Price complex orders as a net debit/credit on a $0.01 grid** ($0.05 for SPX/SPXW/SPXO on C1). Never present a multi-leg trade as two leg prices. *(Cboe Titanium Complex Book spec, 2026.)* This penny grid is the mechanism by which native complex orders beat legging.
6. **Label the synthetic net mid (sum of leg mids) as synthetic, and warn that the real complex market is usually tighter.** Complex-book quotes are not on OPRA, so the app cannot see the real net market. *(SEC DERA 2025; Cboe spec.)*
7. **Tell the user that a partial fill on a complex order preserves the leg ratio** and cannot leave a naked leg. Exchange ratio rules guarantee this. *(Cboe Titanium Complex Book spec, 2026.)* This removes the main stated retail objection to complex orders.
8. **Always use a non-marketable limit order, never a market or marketable-limit order.** Non-marketable limits receive price improvement 80–99% of the time; marketable electronic orders receive it 0–1% on tight spreads. *(SEC Roundtable Supporting Data, Dec 2025.)*

**Stage 2 — Limit placement ladder (branch on `spread_ticks`).**

9. `spread_ticks == 1`: no interior price exists. Either take the offer or do not trade. Note that in July 2023 SPXW ATM was one tick wide 64.7% of the time *(DERA 2025)* — in the most liquid index options this is now the common case, and there is nothing to optimise.
10. `spread_ticks == 2`: **place at the midpoint** — the only interior choice. Expect ~63% fill and ~0.42 of the half-spread all-in. *(DERA 2025.)*
11. `spread_ticks == 3`: **place two ticks in from your side** (i.e. one tick past mid, toward the far side). Expect ~90% fill at ~0.43 of the half-spread, versus ~36% fill at ~0.51 for the one-tick placement. *(DERA 2025.)* The near-mid placement dominates on both fill rate and cost.
12. `spread_ticks == 4`: **place two ticks in — the middle aggressiveness level, not the most aggressive.** Cost 0.42 of half-spread at two ticks vs 0.55 at one tick and 0.58 at three ticks. *(DERA 2025.)* This interior optimum is counterintuitive and worth surfacing explicitly.
13. `spread_ticks >= 4` **and the contract is not index-liquid**: refuse the patient-limit workflow. Fill intensity for a resting order is near zero at ≥4 ticks regardless of aggressiveness. *(Cohen et al. 2026.)* Offer instead: trade a different strike/expiry, or use a native complex order to reach the penny grid, or do not trade.

**Stage 3 — Patience budget and fallback.**

14. **Set the timeout by option price, not by clock.** For options **under $3**, non-fill is penalised only ~14% (a post-non-fill marketable order cost $0.057 vs $0.050) — patience is nearly free, so allow a long timeout. For options **at/above $3**, the penalty is ~40% ($0.14 vs $0.10) — tighten the timeout sharply and start closer to marketable. *(DERA 2025.)*
15. **On timeout, convert to marketable and log the replacement cost against the patient strategy.** This is what makes the measured paid-spread fraction honest. *(DERA 2025 methodology.)*
16. **Do not build an auction-monitoring feature.** Auctions resolve in ~100ms exposure plus a ≤100–900ms response tail; Cboe's SUM exposure was cut to 10ms in September 2026. All leverage is pre-submission. *(Cboe Titanium Auction Process spec, Sept 2026.)*
17. **Re-check the NBBO immediately before submission.** OPRA quote-to-trade ratio is 17,398:1 and median daily messages ~131 billion; a quote observed even seconds earlier is stale. *(SEC Roundtable, 2026.)*

**Stage 4 — Timing.**

18. **Avoid the first 90 minutes for non-urgent entries** in equity options; spreads are L-shaped and stabilise after ~90 minutes. *(Chen 2017.)* For **index** options this rule is weaker — SPX percentage spreads peak near 10:00 and the open is not the worst point. *(Cao/Jacobs/Ke.)*
19. **Near the close, treat the quote as thin rather than wide.** Market makers maintain spread and cut depth. *(Chen 2017.)* Size down rather than repricing.
20. **Exception for near-money 0DTE: the spread narrows into the last hour** as the option price crosses below the $3 tick boundary. *(DERA 2025.)* Condition the time-of-day advice on option price relative to $3, not on the clock alone.
21. **Widen the expected-cost estimate when realised vol or order-flow imbalance is high.** One SD of realised vol adds ~0.25% (calls) / 0.14% (puts) to the SPX percentage spread and ~2.2c / 5.8c to the dollar spread; order-flow volatility predicts higher daily effective spreads with roughly twice the effect at ultra-short maturities. *(Cao/Jacobs/Ke; Doshi et al. 2025.)* A wide spread in high vol is wide for a reason and will not narrow by waiting.
22. **Implement no OPEX or triple-witching rule.** No credible evidence found for an expiration-day effect on options spreads or execution quality.

**Stage 5 — What not to build.**

23. **Do not build a per-order routing selector.** Non-directed orders are 99.84–100% of retail options flow. *(CCMR 2025.)* The lever is broker choice and order type.
24. **Do not build a broker execution-quality comparison from Rule 605.** Rule 605 does not cover listed options; there is no mandated options execution-quality disclosure. *(Clear Street; CCMR 2025; SEC 2024 Rule 605 release.)*
25. **Do not reconstruct benchmark quotes from historical data after the fact.** 38% of raw OPRA trades appear to execute inside the BBO because of sequencing errors, and the bias flatters the trader. *(DERA 2025.)* Snapshot at submission or do not measure.

---

## QUANTIFIED COST LADDER

Stated as the fraction of the **quoted spread** actually paid round-trip-equivalent (one side). To convert: a "half-spread paid" of 1.0 equals 0.50 of the quoted spread.

| Approach | Fraction of **half-spread** paid | Fraction of **quoted spread** paid | Evidence | Strength |
|---|---|---|---|---|
| **Market / marketable order, continuous book, PFOF broker** | ~1.8 | **~0.90** | Hendershott et al. EQ = 0.90 for PFOF continuous | Strong |
| **Market / marketable order, continuous book, average** | ~1.5 | **~0.74** | Hendershott et al. EQ = 0.74 continuous | Strong |
| **Market / marketable order, taking the quote (textbook)** | 1.0 | **0.50** | DERA: $0.05 on a $0.10 (2-tick) market | Strong |
| **Marketable order routed into an auction** | ~0.76 | **~0.38** | Hendershott et al. EQ = 0.38 auction; SEC Dec 2025 marketable-auction vs marketable-electronic ≈ 0.46x | Strong |
| **Patient limit at/near mid, 1-second fallback, liquid index option** | **0.42** | **0.21** | DERA 2025, net of all missed-fill cost, across 2/3/4-tick spreads | Strong |
| **Patient limit landing in an auction (the realistic best case)** | ~0.54 | **~0.27** | SEC Dec 2025, non-marketable-auction / marketable-electronic = 0.27 in the dollar, $5 and >$5 bins | Strong |
| **Native complex order vs legging the same structure** | — | **as low as ~0.17 of the legged cost** | Li/Musto/Pearson: up to 83% saving; penny net grid vs nickel leg grid | Moderate |
| **Legging a multi-leg structure with single-leg marketable orders** | ≥2.0 (you cross twice) | **≥1.00** plus naked-leg risk | SEC DERA "Simple Rules": highest effective spreads of any complex protocol | Moderate |

**The headline ladder for the build.** Against a marketable-order baseline of 1.00:
- marketable, PFOF continuous: **1.00** (worst realistic case)
- marketable, average: 0.82
- marketable into an auction: 0.42
- **patient limit with fallback: 0.23–0.30**
- **native complex vs legged: a further large multiple on top, for multi-leg trades**

**Default parameter for the product: assume you pay 0.21–0.27 of the quoted spread with the disciplined workflow, versus 0.74–0.90 with marketable orders — a 3x range.** Prior strands put the entire option-ranking edge at 8.8% gross collapsing to 1.4% and insignificant at full effective spread. A 3x cost reduction moves the trader from the "full effective spread" column back toward the "good execution" column, where the measured edge was 4.1%. **The execution improvement is worth more than the signal.**

**Important caveat on the ladder.** The DERA 0.42 figure is measured in SPXW 0DTE — the most liquid options in the world, in the period when their spreads compressed from ≥3 ticks (76% of the time, 2020) to 1 tick (64.7% of the time, 2023). It is an upper bound on what is achievable in single-name equity options, where prior strands report ATM spreads averaging ~20% of premium.

---

## MEASUREMENT SPEC

The pivotal unknown is *what fraction of the quoted spread do I actually pay*. Here is how to measure it.

### Fields to log, per order (not per fill)

Captured **at submission time**, from the app's own local observation, written immutably:

| Field | Type | Notes |
|---|---|---|
| `order_id` | string | app-generated |
| `submit_ts` | timestamp, ms, UTC | app's own clock |
| `symbol`, `expiry`, `strike`, `right` | — | per leg for complex |
| `is_complex`, `n_legs`, `leg_ratios` | — | |
| `strategy_label` | string | vertical, iron condor, etc. |
| `side` | buy/sell (net debit/credit for complex) | |
| `qty_submitted` | int | contracts, or packages for complex |
| **`nbbo_bid_at_submit`**, **`nbbo_ask_at_submit`** | decimal | **the benchmark. Snapshot before sending. Never reconstruct.** |
| `nbbo_bid_size_at_submit`, `nbbo_ask_size_at_submit` | int | for the actionability test |
| `is_synthetic_quote` | bool | true for complex (sum of leg mids) |
| `limit_price_submitted` | decimal | |
| `order_type` | enum | market / marketable_limit / non_marketable_limit |
| `tick_size` | decimal | 0.05 if price < 3 else 0.10 |
| `underlying_price_at_submit` | decimal | for the pick-off diagnostic |
| `dte` | int | |
| `minutes_since_open` | int | |

Captured **per fill**:

| Field | Notes |
|---|---|
| `fill_ts`, `fill_price`, `fill_qty` | one row per partial |
| `exchange` / `venue` if the broker reports it | often absent; log when present |
| `commission`, `exchange_fees`, `other_fees` | separately — do **not** fold into price |

Captured **on termination**:

| Field | Notes |
|---|---|
| `terminal_state` | filled / partial / cancelled / expired |
| `terminate_ts` | |
| `nbbo_bid_at_terminate`, `nbbo_ask_at_terminate` | for the opportunity-cost imputation |
| `replacement_order_id` | if converted to marketable — **this link is essential** |

Captured **post-fill**, for the adverse-selection diagnostic — snapshot the NBBO mid at `fill_ts + 1s`, `+60s`, `+300s`:

| Field |
|---|
| `mid_1s`, `mid_60s`, `mid_300s` |

### Derived quantities

Let `M0 = (nbbo_bid_at_submit + nbbo_ask_at_submit) / 2`, `QS = nbbo_ask_at_submit − nbbo_bid_at_submit`, and `D = +1` for buys, `−1` for sells.

```
# Per fill
signed_cost        = D * (fill_price - M0)              # dollars per contract, vs pre-submission mid
effective_spread   = 2 * signed_cost                    # full-spread convention
paid_half_frac     = signed_cost / (QS / 2)             # 1.0 = you paid the full half-spread
paid_quoted_frac   = signed_cost / QS                   # 0.50 = textbook marketable
price_improvement  = (QS / 2) - signed_cost             # dollars, vs taking the quote
spread_ticks       = round(QS / tick_size)

# Realised spread (adverse-selection diagnostic), per horizon h in {1s, 60s, 300s}
realised_spread_h  = 2 * D * (fill_price - mid_h)
# Large and positive => counterparty profited => you were picked off.
# DERA found counterparty revenue under 1 cent at 60s for customer limit orders.

# Opportunity cost of the unfilled remainder (Anand/Samadi/Sokobin convention)
# Impute the unfilled quantity at the opposite-side quote at termination:
impute_price       = nbbo_ask_at_terminate if D == +1 else nbbo_bid_at_terminate
opp_cost_per_ctr   = D * (impute_price - M0)

# Order-level implementation shortfall (the number that matters)
filled_qty         = sum(fill_qty)
unfilled_qty       = qty_submitted - filled_qty
IS_dollars         = sum(fill_qty * D * (fill_price - M0))
                     + unfilled_qty * opp_cost_per_ctr
                     + commission + exchange_fees + other_fees
IS_half_frac       = IS_dollars / (qty_submitted * QS / 2)
```

### The headline metric

```
PAID_SPREAD_FRACTION = sum over orders of IS_dollars
                     / sum over orders of (qty_submitted * QS / 2)
```

This is the single number the whole product turns on. **Benchmarks to compare against:** 1.00 ≈ marketable order taking the quote; **0.42 ≈ DERA's measured patient-limit result in liquid index options**; 0.74–0.90 (of half-spread: 1.48–1.80) ≈ Hendershott's continuous-trading EQ.

### Required stratifications

Report `PAID_SPREAD_FRACTION` and fill rate separately by:
`spread_ticks` (1/2/3/4/5+) × `order_type` × `is_complex` × option-price bucket (**<$3 vs ≥$3 — the tick boundary**) × `dte` bucket (0 / 1–6 / 7–30 / 31+) × time-of-day bucket (first 90 min / midday / last hour).

These are precisely the dimensions along which the literature finds the effect varies, so they are where the user's own data will either confirm or refute the defaults.

### The empirical fill-probability model

Once ~200+ orders are logged, fit:

```
P(fill within T) ~ logit(spread_ticks,
                         placement_ticks_from_mid,
                         minutes_since_open,
                         option_price_bucket,
                         abs(underlying_move_since_submit),
                         dte_bucket)
```

Then choose placement to minimise expected IS, not to maximise fill rate:

```
E[IS(placement)] = P(fill | placement) * cost_if_filled(placement)
                 + (1 - P(fill | placement)) * cost_of_marketable_fallback
```

This reproduces the DERA methodology on the user's own data and is the only way to get a fill-probability model that reflects their broker, their symbols and their sizes. **No public dataset substitutes for it** (see §1, final claim).

### Three measurement traps

1. **Never reconstruct `M0` after the fact.** 38% of raw OPRA trades appear to print inside the BBO from sequencing errors, and the bias flatters the trader. *(DERA 2025.)*
2. **Never benchmark against the fill-time mid.** That credits the trader with favourable drift and hides the cost of waiting.
3. **Keep commissions and fees as separate columns.** Prior strands note trading costs of $6.4bn against $0.9bn in commissions — a ~7:1 ratio. Mixing them makes the dominant term invisible. For a $0.65/contract commission on a $0.10-wide option, the commission is 13x the half-spread; on a $2.00-wide option it is 0.65x. The ratio flips completely across the book and must be visible.

---

## DISCONFIRMING EVIDENCE

**1. The headline broker-difference study has a published methodological critique.** Huang, Jorion & Schwarz ("Some Anonymous Options Trades Are More Equal than Others," SSRN 4951825) placed simultaneous market orders at six brokers (E*Trade, Fidelity, Schwab, TD Ameritrade, Vanguard, Robinhood) and found average round-trip execution cost ranging **0% to 7%** across brokers, with Robinhood worst (7% price improvement vs up to 52% for the best, and 25% auction routing vs 76%). But Hosty & Billings published a formal critique, "Evaluating Broker Execution Quality with a Trading Experiment: A Critique of..." (SSRN 5399225) — **I could not retrieve its content within budget, so the nature and force of the objections is unknown to me.** Separately, CCMR explicitly cautions that the Huang et al. result covers **market orders only, which are just 7.45% of retail options orders**, and that **over 90% of retail orders are excluded from that study** — so it does not reliably describe the retail options market. *Treat the broker-ranking result as contested.*

**2. Price improvement in options may be partly illusory because the bar is so low.** Ernst & Spatt argue the apparent generosity of options price improvement reflects wide spreads and $0.05–0.10 minimum ticks rather than genuine competition. More damagingly: in PIM auctions near the $3 tick boundary, trades above the cutoff get ~13.5 bp more price improvement **but also have higher realised spreads, so customers do not clearly benefit.** They also find that with a PFOF-paying DMM present, effective spreads are ~5% higher and quoted spreads ~10% higher. *The same mechanism that delivers the price improvement may be widening the benchmark it is measured against.* This is the most serious challenge to the whole thesis and the app should not treat quoted-spread-relative price improvement as unambiguously good.

**3. Auction competition is thin, which undercuts the "auctions are competitive" story.** Hendershott, Khan & Riordan find **fewer than 10% of auctions have multiple bidders at the winning price**, most multiple-bid auctions occur at the minimum improvement increment (usually 0 or 1 cent), and ~25% of auctions deliver **zero** price improvement. Requiring just one bid at non-minimal improvement would cover only ~55% of auctions. The initiating wholesaler is often the only real bidder. The 67%-of-quoted-spread average improvement coexists with a quarter of auctions giving nothing.

**4. The original "lower than you think" result was explicitly not for retail.** Muravyev & Pearson (RFS 2020) found an adjusted effective half-spread of ~1.3 cents for timed trades vs 6.2 cents conventional and 8.1 cents quoted — but the trades achieving this were **proprietary and institutional traders running quote-prediction algorithms** (40% of trades, rising to 54%). The authors warn such timing is **likely beyond many individual investors, who still bear large frictions**, and that market makers may widen spreads to offset timing — so **non-timing traders may be subsidising the timers.** The 2.4x headline in this strand's brief partly conflates an institutional algo result with a retail opportunity. The DERA 2025 result is the retail-relevant one and is weaker (0.42 vs ~0.16 of quoted).

**5. Patient limits do cost more in missed fills than they save — in one documented segment.** DERA's own data: for options **above $3** with two-tick spreads, the post-non-fill marketable cost rose from $0.10 to **$0.14**, a 40% penalty. And in the 4-tick case the *least* aggressive placement cost 0.55–0.58 of the half-spread versus 0.42 for the middle — i.e. excessive patience is measurably worse than moderate patience. Combined with Cohen et al.'s finding of near-zero fill intensity at ≥4 ticks, there is a well-defined region (wide spreads, higher-priced options, illiquid strikes) where patience loses.

**6. Retail cannot meaningfully influence routing.** CCMR's Form 606 data shows **non-directed orders are 99.84–100% of retail options orders**. Tastytrade routes **100%** of non-directed options flow to three wholesalers. Ernst & Spatt find options routing concentrated with Citadel ~42%, GEB ~28%, Wolverine ~14%, Morgan Stanley ~8%, Dash/IMC ~6%. The SEC's own April 2026 roundtable data says the consolidator model accounts for "virtually all retail options orders." **The app's leverage is order type and broker choice, not routing.** Any claim that a retail trader can steer individual orders to a better venue is unsupported.

**7. The best-documented cost reductions come from the most liquid options in the world and may not generalise.** DERA 2025 is SPXW 0DTE. Those options went from ≥3 ticks wide 76% of the time (July 2020) to 1 tick wide 64.7% of the time (July 2023). Prior strands put single-name ATM equity-option spreads at ~20% of premium. Extrapolating a 0.42 paid-half-spread fraction from SPXW to single-name equity options is unwarranted, and the app's defaults should be symbol-class-specific.

**8. Direct-exchange routing and midpoint-peg order types for options are far less available than they look.** IBKR offers Direct Routing for options and an IBUSOPT destination that supports Pegged-to-Midpoint, Pegged-to-Best and Relative/Pegged-to-Primary. But IBUSOPT is a **cross of IBKR's own SmartRouted client flow** — orders are undisplayed and **wait for an offsetting order from another IBKR client** before an exchange auction is initiated. IBKR's own page offers **no measured price-improvement statistics**, only claims `[BROKER MARKETING]`. IBKR's general order-types page does **not** confirm product eligibility for MidPrice, Pegged-to-Midpoint, Relative or Pegged-to-Stock in options, and lists Discretionary for stocks/ETFs only. stockbrokers.com lists direct market routing for **equities** only and says tastytrade does not offer it. **No credible evidence found** that midpoint-peg order types for retail options improve measured execution.

**9. Measured options effective spreads have *widened* outside the most liquid names.** SEC Roundtable data, 2012 → end-2025: median effective spreads fell for equity options overall (2.2% → 1.9%) and ETP options (1.9% → 1.4%) and for the top-10 liquid equities (1.3% → 0.9%; 3.0c → 2.3c). **But for the remaining equity underliers effective spreads rose by 0.5%, 1.3%, 1.5% and 0.4% across groupings (nominally +0.3c, +1.5c, +1.3c, +2.2c), and trade-weighted quoted spreads widened across nearly all non-top-10 bins.** The liquidity improvement is concentrated in a handful of names. A tool aimed at anything outside the top tier faces a worsening cost environment.

**10. The 83% complex-order saving is the weakest-sourced of the large numbers.** It originates in a working paper (Li, Musto & Pearson 2023) whose full text I could not retrieve; I have it only as reported in SEC DERA's "Simple Rules for Complex Options." It is stated as "up to 83%," which is an upper bound, and DERA reports **no effective-spread levels in cents or basis points** for its own complex-protocol comparison. Given that this is the playbook's single largest claimed effect, it deserves primary verification before being relied on.

---

## OPEN QUESTIONS

1. **What does the Hosty & Billings critique actually say?** It directly attacks the only controlled experiment on broker options execution quality. SSRN 5399225 was unreachable. This is the highest-priority follow-up.
2. **What is the central (not upper-bound) complex-order-versus-legging saving?** Retrieve Li, Musto & Pearson (SSRN 4389665) directly. The 83% figure anchors the playbook's biggest rule.
3. **What are Duarte/Jones/Wang's actual filters and noise magnitudes?** The quote-hygiene section is the weakest in the report because I could not retrieve this paper. Needed: the specific filter list and the measured midpoint noise, before coding any quote-validity test.
4. **Does the DERA 0.42 paid-half-spread result hold in single-name equity options?** Everything quantitative here is index options. The gap between SPXW (1 tick wide 65% of the time) and single names (~20% of premium) is enormous and unbridged.
5. **What is the fill rate and cost for native complex orders specifically?** The DERA 0DTE paper found complex customer-interest trades had a *falling* limit-order share (59% → 37%), which hints that patient limits work less well on complex orders. No data found on complex-order fill rates by placement. This matters because multi-leg is the common case.
6. **Do IBKR's IBUSOPT and Pegged-to-Midpoint for options actually improve measured execution?** No independent evidence found. The user could answer this directly with an A/B test logged through the measurement module.
7. **What did the SEC do after the April 2026 roundtable?** The roundtable contemplated recalibrating the five-lot specialist allocation rule, enhancing auction competition, and improving PFOF transparency. Comment letters were invited. If Rule 605 is extended to options, broker comparison becomes possible and the app's "you cannot compare brokers" stance would need revising.
8. **Is there an expiration-day or OPEX effect on options spreads?** No credible evidence found either way. A good first question for the user's own fill log.
9. **How do the SEC's December 2025 bin medians convert to fractions of quoted spread?** The bin labels are NBBO-width buckets, not exact widths, so only within-bin ratios are usable. The underlying distributions would allow a direct paid-fraction estimate for the exact retail population.
10. **How much of the measured patient-limit advantage survives at a broker other than the ones studied?** Hendershott's PFOF-continuous EQ of 0.90 versus non-PFOF-continuous 0.69 implies broker choice alone moves the paid fraction by ~30%, but no study maps this to named retail brokers for limit orders.

---

## TOP 10 SOURCES, RANKED

1. **Fu, Li, Musto & Pearson, "Hope at a Reasonable Price: Customer Use of Limit Orders in the 0DTE Market," SEC DERA Working Paper, March 2025.** https://www.sec.gov/files/dera-hope-reasonable-prc-2503.pdf `[REGULATORY]`
   *The single most useful source. Gives fill rates and net-of-missed-fill costs by spread width and aggressiveness, the correct measurement methodology, the OPRA sequencing warning, and the adverse-selection asymmetry at $3. Everything in the placement ladder comes from here.*

2. **SEC Division of Trading and Markets, "Roundtable on Options Market Structure — Supporting Data," April 2026.** https://www.sec.gov/files/roundtable-options-market-structure.pdf `[REGULATORY]`
   *December 2025 data on the Individual Customer population specifically: price improvement frequency and effective spreads by order type and NBBO bin. The 0% vs 80% price-improvement contrast between marketable and non-marketable orders is the most coachable fact in the strand. Also current, which matters.*

3. **Hendershott, Khan & Riordan, "Option Auctions," *Review of Financial Studies* 39(3), March 2026, 783–834.** DOI 10.1093/rfs/hhaf043; WP: https://faculty.haas.berkeley.edu/hender/Option_Auctions.pdf `[PEER-REVIEWED]`
   *The EQ decomposition (0.38 auction vs 0.74 continuous vs 0.90 PFOF-continuous) is the cleanest statement of the paid-spread fraction by execution channel. Also supplies disconfirming evidence on thin auction competition.*

4. **SEC DERA, "Simple Rules for Complex Options," March 2025.** https://www.sec.gov/files/dera-simp-rule-complx-opt-2503.pdf `[REGULATORY]`
   *The authoritative account of complex-order protocols and their cost ranking (C-PIA > C-LOB > legging via single-leg books), plus the endorsement of the 83% figure.*

5. **Cboe, "Cboe Titanium U.S. Options Complex Book Process," v1.2.74, 2026.** https://cdn.cboe.com/resources/techspec/technical-specifications-cboe-titanium-u-s-options-complex-book-process.pdf `[REGULATORY / exchange spec]`
   *Primary, current. The $0.01 net increment, the ratio/partial-fill rule, the COA mechanics and the Customer-only COA initiation on C1 are all codeable facts verified here, not recalled.*

6. **Anand, Samadi & Sokobin, "Retail Limit Orders," *Review of Finance* 30(2), 2026.** WP: https://microstructure.exchange/papers/Retail%20Limit%20Orders%2004082025.pdf `[PEER-REVIEWED]`
   *Equities, not options — but supplies the fill-probability-vs-aggressiveness ladder, the opportunity-cost imputation convention, and the finding that the passive advantage grows with spread width and volatility. The IS methodology in the measurement spec is theirs.*

7. **Committee on Capital Markets Regulation, "Retail Options Market Study," 17 June 2025.** https://capmktsreg.org/wp-content/uploads/2025/06/CCMR-Staff-Report-Retail-Options-Market-Study-6.17.25.pdf `[INDUSTRY/THINK-TANK]`
   *Establishes that non-marketable limits are ~48% of retail options orders, that non-directed is ~100%, that PFOF is higher on limit orders than market orders, and that options have no mandated execution-quality disclosure. Also the sharpest critique of the Huang et al. broker study.*

8. **Muravyev & Pearson, "Options Trading Costs Are Lower than You Think," *Review of Financial Studies* 33(11), 2020, 4973–5014.** Summary: https://www.cxoadvisory.com/equity-options/timing-option-trades-to-suppress-trading-frictions/ `[PEER-REVIEWED]`
   *The origin of the "costs are lower than quoted" thesis — and, read carefully, a source of disconfirming evidence, since the authors warn the timing advantage is beyond most individuals and may be subsidised by non-timers.*

9. **Ernst & Spatt, "Payment for Order Flow."** https://foster.uw.edu/wp-content/uploads/2022/07/4a-Ernst_Spatt-Payment-for-Order-Flow.pdf `[WORKING PAPER]`
   *The ~10x options-vs-equities PFOF result, the routing concentration figures, and the crucial disconfirming finding that price improvement near the $3 tick boundary comes with higher realised spreads, so customers may not benefit.*

10. **Cao, Jacobs & Ke, "Derivative Spreads: Evidence from SPX Options" (AFA)** https://afajof.org/management/viewp.php?n=12068 and **"Risky Intraday Order Flow and Option Liquidity," May 2025** https://www.bauer.uh.edu/hdoshi/docs/DPS_May_2025.pdf `[WORKING PAPERS]`
    *Jointly the best evidence on intraday and maturity effects. The 8.7–9.5% (0DTE) vs ~2% (42–48 DTE) effective-spread ladder is arguably the most actionable single number in the strand, because maturity choice dominates execution tactics.*

**Also used:** Cboe Titanium U.S. Options Auction Process spec v1.1.34, Sept 2026 `[REGULATORY]`; Chen, U. Saskatchewan thesis 2017 `[WORKING PAPER]`; Cohen, Drake, Guo & Reisinger, arXiv:2609.26606, 2026 `[WORKING PAPER]`; Huang, Jorion & Schwarz, SSRN 4951825 `[WORKING PAPER, contested]`; Tastytrade Form 606 Q4 2024 `[REGULATORY]`; Clear Street Rule 605/606 summary `[INDUSTRY]`; Sidley Austin roundtable summary, April 2026 `[INDUSTRY]`; MIAX PRIME specification `[REGULATORY]`; IBKR IBUSOPT page `[BROKER MARKETING]`; stockbrokers.com order-execution guide `[PRACTITIONER]`.
