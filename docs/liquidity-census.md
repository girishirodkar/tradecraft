> The liquidity census the project began with (November 2026). It still runs daily and feeds Tradecraft's stage 1 and its snapshot. The project's README is at the top of the repository.

# Liquidity census + snapshot logger

**Product name: Tradecraft** (since 18 November 2026). "Options Contract Explorer" was the working title. The folder name is unchanged.

`scripts/daily/chain_census.py` does two jobs in one pass over the chain data:

1. **Census** — how many optionable names actually clear a tradeable liquidity gate.
2. **Snapshot** — writes the raw quoted chain to disk, point-in-time.

The snapshot is the one that can't wait. Point-in-time chains cannot be
reconstructed from a pricing model later, so every night not logged is permanently
lost. The census falls out of doing it anyway.

## Status

**Logic verified on synthetic chains. Not yet run on real data** — this session has
no market-data network access, so the real census is one command away but needs a
token.

## Running it for real

```bash
# free Tradier Lite account; personal use is the default term
export TRADIER_TOKEN=...

# build a universe file, one ticker per line (S&P 500 + Nasdaq 100 is a fine start —
# the gate binds INSIDE the S&P 500, so a broad-index list loses little)
python3 scripts/daily/chain_census.py --universe universe.txt --out ./census_out
```

Nightly snapshot, no census aggregation:

```bash
python3 scripts/daily/chain_census.py --universe universe.txt --out ./snapshots --snapshot-only
```

Verify the logic with no token and no network:

```bash
python3 scripts/daily/chain_census.py --synthetic --out ./census_out
```

## What the gate is

Straight from the factor spec, revision 5:

| Criterion | Default | Why |
|---|---|---|
| Spread as % of premium | ≤ 5% | On the **specific contract**, never a name average |
| Open interest | ≥ 100 | A tight spread on a contract nobody holds is not liquidity |
| DTE | 42–90 | >90 DTE insignificant or negative at 25% costs; <42 spreads widen |
| \|log(K/S)\| | ≤ 0.10 | Moneyness dominates direction |
| Mid premium | ≥ $0.20 | Below this, tick granularity makes spread-% meaningless |

A name qualifies only if **at least two** contracts pass. One lucky strike is not a
trade-able name.

**The gate excludes; it does not penalise.** Gross returns are *higher* in illiquid
terciles (23.9% vs 18.0%) while net returns go from +8.2% to −0.8%. Any ranking on
gross richness selects for contracts whose edge dies in execution. This is why the
gate runs before scoring and must never be overridable.

## Synthetic-mode sensitivity

Run on 600 generated names with a roughly market-shaped liquidity distribution
(~1% mega-liquid, ~10% good, ~30% thin, rest dead). **These numbers describe the
synthetic distribution, not the real market** — they are here to show how much the
answer moves with the threshold, which is the point worth internalising before
reading any real result.

| Spread gate | OI ≥ 100 | OI ≥ 500 |
|---|---|---|
| ≤ 2% | 67 (11.2%) | 63 (10.5%) |
| ≤ 3% | 70 (11.7%) | 66 (11.0%) |
| ≤ 5% | 70 (11.7%) | 66 (11.0%) |
| ≤ 8% | 151 (25.2%) | 66 (11.0%) |
| ≤ 12% | 239 (39.8%) | 66 (11.0%) |

Two things to take from this:

- **Between 2% and 5% the answer is stable; past 8% it explodes.** Loosening the
  spread gate from 5% to 12% more than triples the universe — and every name added
  sits in the tercile where the research says net edge is negative. The gate is
  doing real work exactly where it is set.
- **An OI floor of 500 makes the spread gate almost irrelevant.** At OI ≥ 500 the
  count is flat at 66 across every spread threshold, because open interest is the
  binding constraint. If the real data behaves the same way, OI is the cheaper and
  more robust screen and the spread gate becomes a contract-level refinement rather
  than a name-level one.

DTE band barely moves it (70 at 42–90, 70 at 30–60, 76 at 21–180), which is
expected: maturity affects *which* contracts qualify, not *which names* have liquid
chains at all.

## Known limitation in synthetic mode

Every synthetic name reports `has_weeklys = True`. That's an artefact of generating
expirations at 7-day multiples from today, which mostly miss third Fridays. The
third-Friday detection itself is correct; it just has nothing realistic to detect.
On real data this field becomes meaningful — Wave 5 found "has listed weeklys" is a
free exchange-curated liquidity certification worth using as a gate.

## Output

- `chain_snapshot_<stamp>.csv.gz` — every contract row, raw bid/ask stored verbatim
- `census_<stamp>.json` — aggregate report, gate config, passing names
- `census_<stamp>_by_symbol.csv` — per-name detail, sorted by contracts passing

Raw quotes are stored untouched and pathologies (crossed, locked, one-sided,
zero-bid) are **flagged, not corrected**. A mid computed from a one-sided quote is
fiction, and ~38% of raw OPRA trades appear to print inside the BBO from sequencing
errors — biased in the direction that flatters the trader. Downstream analysis needs
the unmodified quote to handle that.

## What to look at first in a real run

1. **The headline count.** Research says ~250 (range 150–400, pessimistic 100–150).
   If yours is near the bottom of that, the watchlist design and breadth penalty
   both change.
2. **`top_blocking_reason_by_name`.** If it's `oi_too_low`, your universe is
   genuinely thin. If it's `spread_too_wide`, there's liquidity but you're paying
   for it. Different problems, different responses.
3. **The OI-vs-spread interaction above.** Find out which screen actually binds on
   real data before tuning either.
4. **Composition, not just count.** The surviving names are expected to tilt
   large-cap, low-IVOL, heavily-covered — exactly where Wave 5 found no positive
   single-name premium is evidenced. A count of 250 that is all mega-caps is a
   different product than 250 spread across the cap spectrum.
