# Scripts

Reorganised on 18 November 2026. Every script used to sit at the project root.

| Folder | Scripts | What they are |
|---|---|---|
| `daily/` | `chain_census.py`, `spread_ladder.py` | Run by the scheduled job every weekday at 11:00 Pacific, through `ops/snapshot_cron.sh` (from 20 November 2026 with `--source auto`: Cboe, then Tradier). `chain_census.py` is also run every hour in market hours by `ops/latest_cron.sh`, which writes the rolling `snapshots/latest/` file |
| `tests/` | `vrp_test_a.py`, `vrp_test_b.py`, `vrp_test_c.py`, `range_test_r.py` | The four pre-registered tests. **Frozen** |
| `analysis/` | `label_frequency.py`, `lean_frequency.py`, `probe_fmp.py` | One-off measurements and the data-provider probe |

## Run everything from the project root

```
cd ~/options-explorer
python3 scripts/daily/chain_census.py --universe universe.txt --out ./snapshots --snapshot-only
python3 scripts/daily/spread_ladder.py
python3 scripts/analysis/label_frequency.py --selftest
```

The data folders did not move: `snapshots/`, `ladder_out/`, `logs/`, `label_out/`,
`vrp_out/` and `census_out/` are still at the project root.

- `chain_census.py` takes `--universe` and `--out` relative to the directory it is
  run from, so run it from the project root (the launcher does).
- `spread_ladder.py` and the three analysis scripts find the project root from
  their own location, so they work from any directory.

## The frozen tests

`tests/` holds the four trials recorded in `vrp_out/TRIALS.log`. **Do not re-run
them, change them or run variants** (factor specification, section 11).

They were moved without changing a character. One consequence: `range_test_r.py`
looks for the price cache and the results folder beside itself and imports
`label_frequency`, which is now in `analysis/`, so it will not run from here
without a path change. That is acceptable because it must not be re-run.

## Changing the daily job

The scheduler calls `ops/snapshot_cron.sh`, which calls the two scripts in
`daily/`. If a daily script is renamed or moved, edit that launcher. The launcher
checks that both files exist and writes a FATAL line to the day's log if not. The
scheduler itself (the launchd job in `ops/`, which is not published) points at the launcher
and does not need reinstalling when a script moves.
