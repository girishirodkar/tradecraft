# Decision log: liquidity criteria as controls (Mode 3)

**Started:** 15 November 2026. One entry per criterion as each is decided.
**Applies to:** on-demand design, step 1 (liquidity screen) and step 5 (live re-gate).

The five gate criteria mixed three things: liquidity (bid-ask gap, open
interest), search scope (expiry band, strike band) and a data-quality guard
(minimum price). They are being reviewed one at a time to decide which are
adjustable controls and which stay fixed.

## 1. Bid-ask gap — DECIDED 15 November 2026

| | |
|---|---|
| Control | Maximum bid-ask gap as a percentage of the option's price |
| Default | **5%** |
| Adjustable range | **2% to 10%** |
| For contracts the system proposes | Strict: never proposes a contract above the current setting |
| For a contract the operator names | May exceed the setting, including above 10%. The cost is displayed and the override is written to the record |
| Hard stops no setting can pass | No bid, no ask, or bid above ask |

**Why adjustable:** a fixed 5% is arbitrary at the margin, excluded about half of
tradeable contracts at the monthly expiry, penalises cheap options mechanically,
and overstates cost when a limit order fills inside the gap.

**Why still strict for the system's own picks:** contracts with wide gaps tend to
look best before costs and worst after. A system that selects contracts under a
soft penalty keeps selecting them.

**Why 2–10%:** measured on the 13 Nov snapshot, 15 Jan monthly expiry, 103 names
(`scripts/daily/spread_ladder.py`): 27 names qualify at 2%, 84 at 5%, 98 at 7%, 102 at 10%, all
103 at 12%. Above 10% the setting adds almost nothing. One day, curated list.

## 2. Open interest — DECIDED 15 November 2026

| | |
|---|---|
| Control | Minimum open interest on the contract |
| Default | **100** |
| Adjustable range | **10 to 1,000** |
| Size check | Flag any order larger than **10% of the contract's open interest**. A proposed figure, not a measured one |
| For contracts the system proposes | Strict, and it will not propose a size that trips the size check |
| For a contract the operator names | May go below the floor or above the size check; shown and recorded |

**Why keep a floor at all:** it matters at weekly expiries. On the 13 Nov snapshot,
among contracts already inside a 5% bid-ask gap, the 31 Dec weekly went from 11
qualifying names with no floor to 5 at a floor of 100, and 34–46% of weekly
contracts had no trades that day against 4% at the monthly.

**Why it is not the main test:** at the 15 Jan monthly the floor changed nothing:
84 names qualify at any floor from 0 to 100 (83 at 250, 75 at 1,000). A tight
bid-ask gap there already implies open interest.

**Why add a size check:** open interest only means something relative to the
order. One contract against 100 is fine; twenty is a fifth of the market.

**Correction recorded:** an earlier reading in this session blamed open interest
for the weekly expiries failing the gate. Measured directly, few names have
tightly quoted weekly contracts at any open interest.
## 3. Expiry band — DECIDED 15 November 2026

| | |
|---|---|
| Control | Days to expiry the system will consider |
| Adjustable range | **7 to 180 days** |
| Default | 42 to 90 days, moved by the thesis horizon: the system proposes expiries that cover the horizon |
| Under 7 days | The system never proposes it |
| For a contract the operator names | Any expiry, including under 7 days; recorded |

**Why:** this is search scope, not liquidity. A fixed 42–90 ruled out the
short-dated trades the operator wants, and the right expiry depends on the
horizon of the thesis. The 42–90 figure was a default from the system-driven modes
and was already marked "to be tested".

**Why the system stops at 7 days:** very short-dated retail option trading lost
money on the positions themselves, not on costs (spec §5c).

**Batch job changed the same day.** The snapshot kept only 42–90 days and discarded
the rest, which cannot be recovered. From the 16 November run it keeps **0 to 180
days** (`store_min_dte`, `store_max_dte` in `scripts/daily/chain_census.py`). Contracts outside
42–90 are stored with the reason `dte_out_of_band`, not dropped. 0 rather than 7 so
that contracts the operator may name are in the archive too. **Snapshots dated
12 and 13 November hold 42–90 days only.** The spread ladder now lists every
stored expiry.
## 4. Strike band — DECIDED 15 November 2026

| | |
|---|---|
| Control | Maximum distance of the strike from the current price |
| Default | **within 10%** |
| Adjustable range | **5% to 30%** |
| For contracts the system proposes | Strict |
| For a contract the operator names | Any strike; recorded |
| Planned | Express the control in delta once enough snapshots carry it, since a fixed percentage means different things on a bond fund and a volatile stock |

**Why:** this is search scope, not liquidity, and the data shows no cliff at 10%.
On the 13 Nov snapshot, 15 Jan monthly, share of contracts passing the other
checks at their defaults: 55% for strikes 0–5% from the price, 37% at 5–10%, 34%
at 10–15%, 25% at 15–20%, 22% at 20–30%.

**Batch job changed the same day.** The quote feed supplies implied volatility,
delta, gamma, theta, vega, rho and a theoretical value for each contract, and the
job was discarding them. From the 16 November run they are stored as the last
seven columns of the snapshot. They are the vendor's model outputs, not
measurements. Earlier snapshots do not have them. The feed's field names were
taken from a code comment and could not be checked from the session that made the
change: `ops/verify_mode1_symbols.sh` prints them, and the first run should be
checked for non-empty values.
## 5. Minimum price — DECIDED 15 November 2026

| | |
|---|---|
| Control | Minimum option price (mid) |
| Default | **$0.20** |
| Adjustable range | **$0.05 to $1.00** |
| For contracts the system proposes | Strict |
| For a contract the operator names | Any price; recorded |
| Display rule | For any option under $1.00, show the bid-ask gap in dollars beside the percentage |

**Why keep it:** on a very cheap option a one- or two-cent gap is already a large
percentage, so the percentage stops being informative.

**Why it is mostly redundant:** on the 13 Nov snapshot, 15 Jan monthly, the median
bid-ask gap was 100% of the price for options under $0.05, 91% at $0.05–0.10, 73%
at $0.10–0.20, 42% at $0.20–0.50, 27% at $0.50–1.00 and 3.5% at $1.00 and above.
With the bid-ask control at 2–10%, almost nothing under $1.00 passes anyway.

## 6. The user can overrule the gate — DECIDED 15 November 2026

A gate failure stops the request by default, and the user may overrule it and
move the ticker or chosen contracts to the next stage. Any control, the
two-contract minimum and a closed-market result can be overruled. The system
shows the cost, takes a one-line reason and writes a decision record. It still
never proposes a failing contract itself. A broken quote cannot be overruled
because there is no price to carry forward (the designer's reading; open to
change). Full text: on-demand design, step 1.

## 7. Every decision is recorded — DECIDED 15 November 2026

Each decision at each stage produces an append-only decision record, written as
the workflow runs. If the contract is traded, the whole chain is stored
permanently in memory and linked to the trade. Full text: on-demand design, §3a.

## Summary of the five controls

| Criterion | Default | Range | Hard stops |
|---|---|---|---|
| Bid-ask gap | 5% | 2–10% | no bid, no ask, bid above ask |
| Open interest | 100 | 10–1,000 | — (plus a flag on orders above 10% of open interest) |
| Expiry | 42–90 days, moved by thesis horizon | 7–180 days | system never proposes under 7 days |
| Strike distance | within 10% | 5–30% | — |
| Minimum price | $0.20 | $0.05–$1.00 | — |

All five are strict for contracts the system proposes. A contract the operator
names may fall outside any of them except the quote hard stops; the system shows
the cost and writes the override to the record. A name still needs at least two
passing contracts to count as tradeable.

All figures above come from one intraday snapshot (13 November 2026) of a
hand-picked list of 103 liquid names. They should be re-read once a few weeks of
daily ladders exist.

## Amendment, 19 November 2026: the bid-ask criterion on the legs of a structure

Decided by the operator after stage 3 ran on live chains (`docs/build-log.md`, session of 19 November, afternoon).

- **For a spread or an iron condor built in stage 3, each leg must have a valid two-sided quote and pass the open-interest and minimum-premium criteria. The bid-ask percentage criterion is not applied to each leg.** It is applied to the structure, through stage 3's cost cap (est. slippage as a share of max loss).
- **A single bought option keeps the per-leg bid-ask criterion.**
- Where a leg's quoted spread is above the user's setting, the candidate's detail says so: "This leg's quoted spread is [X]% of its premium, above your [Y]% setting. Cost is judged on the whole structure."
- Stage 1's screen is unchanged: it still counts contracts against all five criteria.
- **Why.** Out-of-the-money options a typical move from the price are cheap, so a quote a few cents wide is more than 5% of the premium and the leg failed. The far strike was then pulled in, or only the construction built from in-the-money options was eligible, which costs more to trade. At the 5% cap, 35 of 72 candidates across 33 saved views were over it.
- **The strike-distance criterion continues to apply to every leg (confirmed by the operator, 19 November 2026).** Still as built, for the operator to correct: An expiration counts as eligible when it has at least two contracts passing these leg criteria.
