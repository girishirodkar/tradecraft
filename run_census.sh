#!/bin/bash
# Run from macOS Terminal (not the sandboxed VM) so it has real internet.
#   cd ~/options-explorer && ./run_census.sh
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] && set -a && . ./.env && set +a
# Default source is Cboe free delayed quotes (no key). For --source tradier,
# put TRADIER_TOKEN in .env.
python3 scripts/daily/chain_census.py --universe universe.txt --out ./census_out "$@"
