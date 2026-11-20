"""The recorded demo: all four stages on bundled data, with no keys and no network.

    .venv/bin/python -m uvicorn tradecraft.demo:app --host 127.0.0.1 --port 8324

For evaluators (operator decision, 19 November 2026). It is the development
replay app (tradecraft/dev_replay.py) fed only from a small bundle of files in
data/demo-bundle/, which is published as its own repository:

- stages 1 and 3 and stage 4's checklists, question and readiness line run for
  real, on the bundled option snapshot and price histories;
- stage 2's agents, the Evidence Retriever of stage 4 and the Critic return what
  real runs saved. Nothing is asked of a model, so no key is needed;
- "today" is the date of the bundled snapshot and the market is treated as
  closed, so every screen is marked PROVISIONAL and RECORDED DEMO and nothing
  drifts as the calendar moves on;
- no source on the network is asked for anything.

Figures differ a little from a live run: the pool of other stocks' histories is
not bundled, so the history-based figures use the stock's own history and say so.

Building the bundle (the operator's machine only; needs the saved runs):

    .venv/bin/python -m tradecraft.demo export AMZN MSFT NVDA
    .venv/bin/python -m tradecraft.demo record AMZN MSFT      # live: one Critic run per candidate
    .venv/bin/python -m tradecraft.demo scan                  # no secret, no personal path
"""
from __future__ import annotations

import csv
import datetime as dt
import gzip
import io
import json
import os
import re
import shutil
import sys
from pathlib import Path

from . import settings

BUNDLE = "demo-bundle"
DB = "demo.sqlite3"


def bundle_dir() -> Path:
    return Path(os.environ.get("TRADECRAFT_DEMO_DIR") or settings.data_dir() / BUNDLE)


def manifest() -> dict:
    p = bundle_dir() / "manifest.json"
    if not p.exists():
        raise SystemExit(f"The demo bundle is not at {bundle_dir()}. Clone the demo-data repository into "
                         "data/demo-bundle (README.md, 'Recorded demo').")
    return json.loads(p.read_text())


def install() -> dict:
    """Point every source at the bundle. Nothing reaches the network after this."""
    from . import dev_replay, stage3, stage4
    from .data import chain, fmp, prices, session
    from .workflow.state import StepFailed
    m, root = manifest(), bundle_dir()
    as_of = dt.datetime.fromisoformat(m["as_of"])
    real_status = session.status

    def status(when=None):
        return {**real_status(when), "open": False, "reason": "recorded demo: data of " + m["as_of"][:10]}

    def no_live(symbol, store=None):
        raise chain.ChainUnavailable("the recorded demo uses the bundled snapshot only")

    def closes(symbol, store=None):
        p = root / "prices" / f"{symbol.upper()}.json"
        if not p.exists():
            raise prices.PricesUnavailable(f"no bundled price history for {symbol}")
        return {"symbol": symbol.upper(), "source": "bundled price history (recorded demo)", "stale": True,
                "closes": [(d, c) for d, c in prices._parse(p.read_bytes()) if d <= as_of.date()]}

    events = json.loads((root / "events.json").read_text()) if (root / "events.json").exists() else {}

    def dividends(symbol, store=None):
        if symbol.upper() not in events:
            raise fmp.NotServed(f"no bundled dividend dates for {symbol}")
        return events[symbol.upper()]

    def saved(symbol):
        p = root / "stage2" / f"{symbol.upper()}.json"
        if not p.exists():
            raise StepFailed("error", f"Recorded demo: no saved thesis run for {symbol}.")
        return json.loads(p.read_text())

    def saved4(state):
        cand = ((state.get("selection") or {}).get("id")) or "none"
        return root / "stage4" / f"{state['symbol'].upper()}.{cand}.json"

    session.status = status
    chain.live = no_live
    chain.latest_snapshot_path = lambda: root / "snapshot" / m["snapshot"]
    prices.closes = closes
    fmp.dividends = dividends
    dev_replay.saved = saved
    dev_replay._mode = lambda: ""                      # the build's replay switch has no effect here
    stage4.saved_path = saved4
    stage4.now = lambda: as_of                          # "today" is the day of the bundled data
    stage3.pool_scaled_moves = lambda h: ()             # the pool's price histories are not bundled
    return m


def create():
    from . import dev_replay, research
    from .storage import Store
    from .web import app as web
    m = install()
    research.ensure_current()
    listing = json.loads((bundle_dir() / "symbols.json").read_text())
    web.DEMO = {"as_of": m["as_of"], "symbols": m["symbols"]}
    return web.create_app(store=Store(settings.data_dir() / DB), steps=dev_replay.replay_steps(), symbols=listing)


def __getattr__(name: str):
    if name == "app":
        global _app
        try:
            return _app
        except NameError:
            _app = create()
            return _app
    raise AttributeError(name)


# ---- building the bundle (the operator's machine) --------------------------------------------

README = """# Tradecraft: recorded demo data

Data for the keyless demo of Tradecraft. Clone this repository into the main
repository's `data/demo-bundle/` folder, then follow "Recorded demo" in the main
README. It lets all four stages be clicked through with no API key, no network
and no cost.

Everything here is a recording made on {day}. It is not live data and not
investment advice. Tradecraft places no orders.

| Folder | What it is | Source |
|---|---|---|
| `snapshot/` | One option-chain snapshot, cut down to {symbols} | Cboe delayed quotes, as logged by the project's daily job |
| `prices/` | Daily closing prices for the same symbols | Yahoo chart endpoint |
| `stage2/` | What the thesis stage's agents returned on a real run, with the evidence they cited | SEC EDGAR filings, Financial Modeling Prep, the Federal Reserve and FRED calendars; model output from Claude |
| `stage4/` | What the Evidence Retriever and the Critic returned on a real run, per selected strategy | The project's own research; model output from Claude |
| `events.json`, `symbols.json`, `manifest.json` | Dividend dates, the symbol list for the search box, the date of the data | Financial Modeling Prep; public listing files |

The third-party data is a small sample kept so that the software can be evaluated.
It is not licensed for reuse; take it from its source if you need it.
"""


def _feed(symbol: str) -> str:
    from .data import chain
    return chain.feed_symbol(symbol)


def export(symbols: list[str]) -> dict:
    """Write the bundle from this machine's snapshot, price files and saved runs."""
    from . import dev_replay
    from .data import chain, directory, fmp
    from .storage import Store
    root = bundle_dir()
    for d in ("snapshot", "prices", "stage2", "stage4"):
        (root / d).mkdir(parents=True, exist_ok=True)
    symbols = [s.upper() for s in symbols]
    src = chain.latest_snapshot_path()
    feeds = {_feed(s) for s in symbols}
    kept, as_of = 0, None
    out = io.StringIO()
    with gzip.open(src, "rt") as f:
        r = csv.DictReader(f)
        w = csv.DictWriter(out, fieldnames=r.fieldnames)
        w.writeheader()
        for row in r:
            if row["symbol"] in feeds:
                w.writerow(row)
                kept += 1
                as_of = as_of or row["asof"]
    for old in (root / "snapshot").glob("*.csv.gz"):
        old.unlink()
    with gzip.open(root / "snapshot" / src.name, "wt") as f:
        f.write(out.getvalue())
    when = dt.datetime.fromisoformat(as_of).replace(tzinfo=chain.PT)
    report = {"snapshot_rows": kept, "prices": [], "stage2": [], "events": [], "missing": []}
    from . import figures
    for s in symbols:
        name = figures.HISTORY_OF.get(s, s)
        p = settings.ROOT / "label_out" / "prices" / f"{name}.json"
        if p.exists():
            shutil.copyfile(p, root / "prices" / f"{s}.json")
            report["prices"].append(s)
        else:
            report["missing"].append(f"price history for {s}")
        try:
            run = dev_replay.saved(s)
            for item in (run.get("evidence") or {}).get("items") or []:
                item.pop("body", None)                 # the fetched text itself is not needed by any screen
            (root / "stage2" / f"{s}.json").write_text(json.dumps(run, default=str))
            report["stage2"].append(s)
        except Exception as e:  # noqa: BLE001
            report["missing"].append(f"saved thesis run for {s} ({getattr(e, 'message', e)})")
    events = {}
    store = Store(settings.data_dir() / DB)
    for s in symbols:
        try:
            d = fmp.dividends(s, store)
            events[s] = {k: d.get(k) for k in ("symbol", "pays_dividend", "next_ex_dividend_date", "next_ex_dividend_note")}
            report["events"].append(s)
        except Exception:  # noqa: BLE001 - not served: the screen says "not available"
            pass
    (root / "events.json").write_text(json.dumps(events, indent=1))
    listing = directory.load(store, allow_refresh=False)
    rows = [x for x in listing["symbols"] if x[0] in symbols]
    (root / "symbols.json").write_text(json.dumps({"updated": listing.get("updated"), "symbols": rows,
                                                   "daily": [s for s in listing.get("daily", []) if s in symbols]}))
    (root / "manifest.json").write_text(json.dumps({
        "as_of": when.isoformat(timespec="seconds"), "snapshot": src.name, "symbols": symbols,
        "note": "A recording for the keyless demo. Not live data."}, indent=1))
    (root / "README.md").write_text(README.format(day=f"{when.day} {when:%B %Y}", symbols=", ".join(symbols)))
    return report


def record(symbols: list[str]) -> list[dict]:
    """Live, on the operator's key: for each symbol and each candidate stage 3 keeps on the
    bundled data, run the Evidence Retriever and the Critic once and save their outputs into
    the bundle. About $0.11 a candidate. A symbol that returns no view is skipped."""
    from . import dev_replay, stage4
    from .storage import Store
    from .workflow import Workflow
    install()
    steps = {**dev_replay.replay_steps(), "passages": stage4.passages_step, "critic": stage4.critic_step}
    store = Store(settings.data_dir() / DB)
    out = []
    for s in [x.upper() for x in symbols]:
        w = Workflow(store, steps=steps)
        w.recover_interrupted()                        # a request left open by an earlier, broken recording
        v = w.start(s)
        rid = v["request_id"]
        v = w.resume(rid, "continue")
        if not v["state"].get("view"):
            out.append({"symbol": s, "skipped": "no view: the user enters a thesis, so no Critic output can be saved"})
            w.resume(rid, "stop")
            continue
        v = w.resume(rid, "accept")
        ids = [c["id"] for c in (v["state"].get("contracts") or {}).get("candidates") or []]
        for i, cid in enumerate(ids):
            v = w.resume(rid, "continue", selection={"id": cid, "contracts": 1})
            k, st = v["state"].get("critic"), v["state"]
            out.append({"symbol": s, "candidate": cid, "pause": v["pause"]["pause"],
                        "critic": k and {"cost": k["run"]["cost_usd"], "returned_once": k["check"]["returned_once"],
                                         "objections": len(k["objections"])},
                        "retriever_cost": ((st.get("passages") or {}).get("run") or {}).get("cost_usd"),
                        "method": (st.get("passages") or {}).get("method"),
                        "stop": (v["pause"].get("stop") or {}).get("message"),
                        "unavailable": st.get("critic_unavailable")})
            if v["pause"]["pause"] == "stage4_stopped":
                v = w.resume(rid, "return")
            elif i + 1 < len(ids):
                v = w.resume(rid, "return")
        if v["pause"] and "stop" in v["pause"]["actions"]:
            w.resume(rid, "stop")
    return out


_PERSONAL = re.compile(r"/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_ALLOWED_MAIL = re.compile(r"@(sec\.gov|noreply\.github\.com|example\.(com|org)|domain\.com|anthropic\.com)$|^noreply@", re.I)


def scan(root: Path | None = None) -> list[str]:
    """Every file of the bundle, decompressed, searched for the value of each secret in .env,
    for a home-folder path and for an email address. Returns what was found; empty means clean.
    The values themselves are never printed."""
    root = root or bundle_dir()
    secrets = {k: v for k, v in settings._env().items() if v and len(v) >= 6}
    user = Path.home().name
    found = []
    for p in sorted(x for x in root.rglob("*") if x.is_file() and ".git" not in x.parts):
        raw = p.read_bytes()
        try:
            text = gzip.decompress(raw).decode("utf-8", "replace") if p.suffix == ".gz" else raw.decode("utf-8", "replace")
        except OSError:
            text = raw.decode("utf-8", "replace")
        rel = p.relative_to(root)
        for k, v in secrets.items():
            if v in text:
                found.append(f"{rel}: holds the value of {k}")
            for part in re.split(r"[\s()<>,;]+", v):                # e.g. the email inside SEC_USER_AGENT
                if "@" in part and part in text:
                    found.append(f"{rel}: holds the contact address from {k}")
        if user and len(user) >= 4 and user.lower() in text.lower():
            found.append(f"{rel}: holds this machine's user name")
        for m in _PERSONAL.finditer(text):
            hit = m.group(0)
            if "@" in hit:
                if not _ALLOWED_MAIL.search(hit) and not re.search(r"@\d|\.(png|jpg|gif|htm|html|xml|json)$", hit, re.I):
                    found.append(f"{rel}: holds an email address (…@{hit.split('@')[1]})")
            else:
                found.append(f"{rel}: holds a home-folder path")
    return sorted(set(found))


if __name__ == "__main__":
    cmd, args = (sys.argv[1:2] or [""])[0], sys.argv[2:]
    if cmd == "export":
        print(json.dumps(export(args), indent=1))
    elif cmd == "record":
        for row in record(args):
            print(json.dumps(row))
    elif cmd == "scan":
        hits = scan()
        print("\n".join(hits) if hits else f"Clean: no secret, no home-folder path, no email address in {bundle_dir()}.")
        sys.exit(1 if hits else 0)
    else:
        print(__doc__)
