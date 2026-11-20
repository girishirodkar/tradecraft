"""The symbol directory behind Home's search box.

Every US-listed stock and ETF, from the Nasdaq Trader symbol files (free, no
key), plus the index symbols the system supports. Stored locally in
data/symbols.json and refreshed about weekly. The browser loads the list once
and searches it locally, so there is no network call per keystroke.

Left out: test issues, and listings that are not stocks or funds (warrants,
rights, units, preferred shares and notes).
"""
from __future__ import annotations

import datetime as dt
import json
import re

from .. import net, settings
from ..storage import Store, now

SOURCES = {
    "nasdaq": "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
    "other": "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
}
INDEXES = [("SPX", "S&P 500 Index", "INDEX"), ("XSP", "Mini-SPX Index", "INDEX")]
REFRESH_DAYS = 7
PATH = "data/symbols.json"

_NOT_A_STOCK = re.compile(r"\b(warrants?|rights?|units?|preferred|depositary shares? representing .* preferred|"
                          r"notes? due|debentures?|subordinated)\b", re.IGNORECASE)
_SUFFIX = re.compile(r"\s*(-\s*)?(class [a-z] )?(common stock|ordinary shares?|common shares?|"
                     r"american depositary shares?.*|depositary shares?.*|shares of beneficial interest)\s*$",
                     re.IGNORECASE)


def _clean_name(name: str) -> str:
    name = name.strip()
    cleaned = _SUFFIX.sub("", name).strip(" -,")
    return cleaned or name


def _parse(text: str, kind: str) -> list[tuple[str, str, str]]:
    rows = []
    lines = text.splitlines()
    head = lines[0].split("|")
    sym_i = head.index("Symbol" if kind == "nasdaq" else "ACT Symbol")
    name_i, etf_i, test_i = head.index("Security Name"), head.index("ETF"), head.index("Test Issue")
    for line in lines[1:]:
        f = line.split("|")
        if len(f) != len(head) or line.startswith("File Creation Time"):
            continue
        sym, name = f[sym_i].strip(), f[name_i].strip()
        if f[test_i] == "Y" or not sym or not re.fullmatch(r"[A-Z]{1,5}(\.[A-Z])?", sym):
            continue                       # test issues; preferreds and others carry $ or other marks
        is_etf = f[etf_i] == "Y"
        if not is_etf and _NOT_A_STOCK.search(name):
            continue
        rows.append((sym, _clean_name(name), "ETF" if is_etf else "STOCK"))
    return rows


def refresh(store: Store | None = None) -> dict:
    """Download both files and write data/symbols.json. Returns the directory."""
    seen: dict[str, tuple[str, str, str]] = {}
    for kind, url in SOURCES.items():
        text = net.get(url, source=f"nasdaqtrader.{kind}", store=store).decode("utf-8", "replace")
        for row in _parse(text, kind):
            seen.setdefault(row[0], row)
    for row in INDEXES:
        seen[row[0]] = row
    out = {"updated": now().isoformat(timespec="seconds"),
           "source": "Nasdaq Trader symbol directory (nasdaqlisted.txt, otherlisted.txt)",
           "symbols": sorted(seen.values())}
    net.writable(PATH).parent.mkdir(exist_ok=True)
    net.writable(PATH).write_text(json.dumps(out, separators=(",", ":")))
    return out


def daily_names() -> list[str]:
    """Symbols on the daily snapshot list (universe.txt): the liquid, optionable
    names. Used only to order search results; it does not limit what can be searched."""
    try:
        lines = net.readable("universe.txt").read_text().splitlines()
    except (OSError, net.NotAllowed):
        return []
    out = []
    for line in lines:
        tok = line.split("#")[0].split()
        if tok:
            out.append(tok[0].lstrip("_").upper())
    return out


def load(store: Store | None = None, allow_refresh: bool = True) -> dict:
    """The directory from disk, refreshed if it is missing or older than a week.
    If a refresh fails and an older copy exists, the older copy is used.
    `daily` (names on the daily snapshot list) is attached on every load."""
    p = net.readable(PATH)
    current = json.loads(p.read_text()) if p.exists() else None
    stale = current is None or (now() - dt.datetime.fromisoformat(current["updated"])).days >= REFRESH_DAYS
    if stale and allow_refresh:
        try:
            current = refresh(store)
        except (net.FetchFailed, net.NotAllowed, OSError):
            if current is None:
                raise
    listed = {s[0] for s in current["symbols"]}
    current["daily"] = sorted(set(daily_names()) & listed)
    return current


def symbols(store: Store | None = None) -> set[str]:
    return {s[0] for s in load(store)["symbols"]}


def is_listed(symbol: str, store: Store | None = None) -> bool:
    return symbol.upper() in symbols(store)


def search(query: str, directory: dict, limit: int = 8) -> list[tuple[str, str, str]]:
    """The matching rule of docs/product-shell.md section 5, for the engine and the
    tests; the browser applies the same rule to the same list.
    Symbols that start with the text first; then names in which a word starts
    with it; then any other match. At most 8 rows.
    Within the first group (operator decision, 18 November 2026): names on the
    daily snapshot list first, then an exact symbol match, then shorter symbols,
    then alphabetical. The daily list stands in for popularity, which no free
    source provides."""
    q = (query or "").strip().lower()
    if not q:
        return []
    a, b, c = [], [], []
    for row in directory["symbols"]:
        sy, nm = row[0].lower(), row[1].lower()
        if sy.startswith(q):
            a.append(row)
        elif nm.startswith(q) or (" " + q) in nm:
            b.append(row)
        elif q in sy or q in nm:
            c.append(row)
    daily = set(directory.get("daily") or [])
    a.sort(key=lambda r: (r[0] not in daily, r[0].lower() != q, len(r[0]), r[0]))
    return [tuple(r) for r in (a + b + c)[:limit]]
