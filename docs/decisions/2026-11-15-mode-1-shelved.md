# Decision: Mode 1 (scheduled index overlay) is shelved

**Date:** 15 November 2026
**Decided by:** the operator, on a recommendation made after Tests A, B and C
**Status:** in force. Recorded in `docs/factor-spec.md` revision 11.

## The decision

Mode 1 will not be built. Mode 3 (on-demand) is the build target, and the five
index instruments (SPY, SPX, QQQ, IWM, TLT) are available inside it. Mode 2
(single-name event positioning) is unchanged and still waits on earnings-date
sourcing. The daily snapshot job keeps running.

The mode numbers are not reused: Mode 1 stays "Mode 1, shelved" so older
documents and commits remain readable.

## Why

Mode 1 was the mode in which the **system** proposes index option trades on a
schedule. That requires evidence that some systematic index-writing programme
earns a return. Three pre-registered tests were run on 15 November 2026 on free
Cboe data, logged in `vrp_out/TRIALS.log`:

| Test | Question | Post-2012 result |
|---|---|---|
| A (`scripts/tests/vrp_test_a.py`) | Is the variance premium still in option prices? | Yes, gross: +3.7 vol points, same as 2001–2012. The worst 3 of 173 months take back 41% of it |
| B (`scripts/tests/vrp_test_b.py`) | Did at-the-money writing collect it? | No. BXM −1.38%/yr (t=−1.07), PUT −0.44%/yr (t=−0.37) |
| C (`scripts/tests/vrp_test_c.py`) | Did out-of-the-money or defined-risk writing collect it? | No. BXY −1.18 (t=−1.06), BXMD −1.14 (t=−1.13), CNDR −1.32 (t=−0.78). All three were positive and significant before May 2012 |

Five rule-based index-writing programmes show no positive alpha after 2012. None
of the post-2012 estimates is individually distinguishable from zero; the finding
is the absence of evidence for a return, plus a clear drop from the earlier
period. By the readings declared before each run, Mode 1 has no supported
premium-harvesting leg.

That leaves Mode 1 one honest function: reducing the equity risk of an existing
holding. The operator already holds index funds, does not want an overlay on them,
and wants to trade index options with structures of their own choosing. That is
Mode 3 with an index instrument.

## What is kept

- **§5a, §5b, §5c of the spec.** Instrument properties, assignment handling, the
  beta-weighted 4% cap and the structure evidence apply to index trades in Mode 3.
- **The test results as base-rate context.** When the operator proposes selling
  index premium in Mode 3, the system shows what rule-based versions of that trade
  earned after 2012.
- **The snapshot archive**, now including SPX, XSP and TLT.

## What is dropped

- The scheduled index trigger and any system-originated index proposal.
- The Hedge Supervisor agent (index-only; inactive until Mode 1 returns).
- Ranking of index candidates by expected premium income, anywhere.

## What would bring Mode 1 back

A pre-registered test showing positive alpha for 42–90 DTE index writing after
2012. No public index covers that horizon, so it needs purchased option data or
several years of the snapshot archive. **Running further variants of the Cboe
indices is not a route back**: three of roughly twelve trials are spent, and
searching variants until one works is the forking path §11 forbids.

## Limits of the evidence behind this decision

- Tests B and C are one-month programmes; Mode 1's intended 42–90 DTE programme
  was never tested directly.
- The three indices in Test C are highly correlated: one observation seen three
  ways.
- BXMD and CNDR may have back-calculated pre-2012 history (not checked).
- Test B's sample starts March 2004, so it says nothing about a break.
