# Decision: the system drafts the thesis in Mode 3; Mode 2 becomes a scan in front of it

**Date:** 15 November 2026
**Decided by:** the operator
**Status:** in force. Recorded in `docs/factor-spec.md` revision 12.

## The decision

1. **In Mode 3 the system drafts the thesis by default.** The operator names a
   ticker or a list; the system researches it and proposes a view (bullish,
   bearish, neutral or no view), with a probability, a horizon, a resolution
   criterion and falsifiers. The operator accepts, edits or rejects it. Bringing
   your own thesis remains available as the alternative path.
2. **Mode 2 is not a separate build.** It will be added after Mode 3 as a scan:
   a scheduler and an event filter that surface candidates and hand each one to
   the Mode 3 pipeline. It still needs a reliable earnings-date source.

## Why

- The operator's stated goal from the start was a system that researches a ticker
  and forms the bullish, bearish or neutral view. Mode 3 as first designed left
  that to the operator.
- "The user brings the thesis" was a design choice, not a technical limit. It
  followed from the finding that direction prediction has almost no measurable
  edge at retail scale (about 7 bp a month, roughly zero after costs). That
  finding limits what may be **claimed** for a system thesis. It does not prevent
  drafting one.
- With a system-drafted thesis, Modes 2 and 3 share everything downstream of the
  thesis. The remaining difference is who picks the ticker and what kind of
  thesis is formed, which is a scheduler and a filter, not a second pipeline.

## Conditions attached, with the reason for each

| Condition | Reason |
|---|---|
| The thesis is labelled unvalidated; each claim carries an evidence grade; no 0–100 score | No evidence the thesis predicts returns. A score would imply precision that does not exist |
| The Thesis agent never sees option prices, implied volatility or market-implied probability | Otherwise the comparison of thesis probability with market-implied probability (step 8) is circular |
| The Critic runs on a different model family from the Thesis agent, or the operator is the critic | Models that are wrong agree on the same wrong answer far above chance; a same-model critic shares the author's blind spots |
| The Thesis agent may return `no_view` | Forcing a view on every ticker manufactures theses |
| Every drafted thesis is logged with its probability and resolved later, traded or not | Makes the system's own hit rate measurable. Forward-only: a model whose training postdates a period cannot be backtested on it |
| No track-record claim is displayed before 100 resolved theses | At smaller n the interval on a Brier score is wider than any plausible effect |
| Inputs are limited to what the spec supports: the seven TA roles (§9b), sector context (§9c), scheduled macro events (§9d), filings | The dead list in §10 stands |

## What does not change

The liquidity gate, cost ladder, sizing rule, veto mechanics, order tickets
instead of reminders, the immutable record, and no execution path.

## What this costs

- **Anchoring moves to the operator.** The original design had the operator state
  a view before seeing any market information. Reading a system draft first
  anchors the operator on it. Mitigation: an optional field to enter your own
  probability before the draft is shown; both are stored.
- **One more model dependency.** A second model family for the Critic.
