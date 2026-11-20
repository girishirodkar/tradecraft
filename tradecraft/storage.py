"""SQLite storage: decision records, the evidence store, traces, the spend ledger and the cache.

The permanent record (decision_records) is append-only: triggers in the
database refuse UPDATE and DELETE, so the guarantee does not depend on the
application code behaving.

A request's records start in a pending log. They are committed to the permanent
record at one point, when stage 2 returns a view (bullish, bearish or
range-bound); from then on records are written straight to the permanent
record. A request that ends before that point has its pending log discarded,
so nothing reaches the permanent record (docs/on-demand-mode-design.md, 3a).

The trace is a separate operational log. It cannot be edited. Traces of
requests that never reached the permanent record are kept for 7 days, are never
used for scoring and are never listed in Recent analyses.
"""
from __future__ import annotations

import datetime as dt
import json
import sqlite3
import threading
import uuid
from pathlib import Path
from zoneinfo import ZoneInfo

from . import settings

TZ = ZoneInfo("America/Los_Angeles")

SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    request_id   TEXT PRIMARY KEY,
    symbol       TEXT NOT NULL,
    opened_at    TEXT NOT NULL,
    committed_at TEXT,
    ended_at     TEXT,
    status       TEXT
);

CREATE TABLE IF NOT EXISTS pending_records (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id   TEXT NOT NULL UNIQUE,
    request_id  TEXT NOT NULL,
    stage       TEXT NOT NULL,
    decision    TEXT NOT NULL,
    decided_by  TEXT NOT NULL,
    payload     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS pending_records_no_update BEFORE UPDATE ON pending_records
BEGIN SELECT RAISE(ABORT, 'a pending log is append-only within its request'); END;

CREATE TABLE IF NOT EXISTS decision_records (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id   TEXT NOT NULL UNIQUE,
    request_id  TEXT NOT NULL,
    stage       TEXT NOT NULL,
    decision    TEXT NOT NULL,
    decided_by  TEXT NOT NULL,
    payload     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS decision_records_no_update BEFORE UPDATE ON decision_records
BEGIN SELECT RAISE(ABORT, 'decision records are append-only'); END;
CREATE TRIGGER IF NOT EXISTS decision_records_no_delete BEFORE DELETE ON decision_records
BEGIN SELECT RAISE(ABORT, 'decision records are append-only'); END;

CREATE TABLE IF NOT EXISTS trace (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id  TEXT,
    run_id      TEXT NOT NULL,
    agent       TEXT NOT NULL,
    step        INTEGER NOT NULL,
    kind        TEXT NOT NULL,
    payload     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS trace_no_update BEFORE UPDATE ON trace
BEGIN SELECT RAISE(ABORT, 'the trace cannot be edited'); END;

CREATE TABLE IF NOT EXISTS spend (
    seq           INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id    TEXT,
    run_id        TEXT NOT NULL,
    agent         TEXT NOT NULL,
    model         TEXT NOT NULL,
    input_tokens  INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cache_read_tokens  INTEGER NOT NULL,
    cache_write_tokens INTEGER NOT NULL,
    cost_usd      REAL NOT NULL,
    day           TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id  TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    item_key    TEXT NOT NULL,
    item        TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    UNIQUE (request_id, item_key)
);
CREATE TRIGGER IF NOT EXISTS evidence_no_update BEFORE UPDATE ON evidence
BEGIN SELECT RAISE(ABORT, 'stored evidence cannot be edited'); END;

CREATE TABLE IF NOT EXISTS cache (
    key        TEXT PRIMARY KEY,
    source     TEXT NOT NULL,
    day        TEXT NOT NULL,
    body       BLOB NOT NULL,
    created_at TEXT NOT NULL
);
"""


def now() -> dt.datetime:
    return dt.datetime.now(TZ)


def today() -> str:
    return now().date().isoformat()


def next_daily_reset() -> dt.datetime:
    """When the daily spend limit resets: the next midnight, Pacific time."""
    n = now()
    return (n + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def _strategy(selection: dict | None) -> str | None:
    """Home's list names the strategy without its strikes: "Bull put spread"."""
    c = (selection or {}).get("candidate") or selection or {}
    name = c.get("structure") or c.get("name")
    return name.split(" (")[0] if name else None


class Store:
    """One SQLite file. Safe to share across threads (one connection per call)."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else settings.data_dir() / "tradecraft.sqlite3"
        self._lock = threading.Lock()
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path, timeout=30)
        c.row_factory = sqlite3.Row
        return c

    # ---- requests, the pending log and the permanent record ---------------------------

    TRACE_RETENTION_DAYS = 7

    def open_request(self, symbol: str) -> str:
        rid = "req_" + uuid.uuid4().hex[:12]
        with self._lock, self._conn() as c:
            c.execute("INSERT INTO requests (request_id, symbol, opened_at) VALUES (?,?,?)",
                      (rid, symbol, now().isoformat()))
        return rid

    def request(self, request_id: str) -> dict | None:
        with self._conn() as c:
            r = c.execute("SELECT * FROM requests WHERE request_id=?", (request_id,)).fetchone()
        return dict(r) if r else None

    def open_request_ids(self) -> list[str]:
        """Requests that have not ended. There is at most one while the app runs."""
        with self._conn() as c:
            rows = c.execute("SELECT request_id FROM requests WHERE ended_at IS NULL ORDER BY opened_at").fetchall()
        return [r[0] for r in rows]

    def is_committed(self, request_id: str) -> bool:
        r = self.request(request_id)
        return bool(r and r["committed_at"])

    def write_record(self, request_id: str, stage: str, decision: str, decided_by: str,
                     payload: dict) -> str:
        """Write a decision record: to the pending log before the commit point,
        straight to the permanent record after it."""
        rec_id = "dr_" + uuid.uuid4().hex[:12]
        body = settings.redact(json.dumps(payload, default=str, sort_keys=True))
        table = "decision_records" if self.is_committed(request_id) else "pending_records"
        with self._lock, self._conn() as c:
            c.execute(
                f"INSERT INTO {table} (record_id, request_id, stage, decision, decided_by, payload, created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (rec_id, request_id, stage, decision, decided_by, body, now().isoformat()))
        return rec_id

    def commit_request(self, request_id: str) -> int:
        """The commit point: move the pending log to the permanent record, in order."""
        with self._lock, self._conn() as c:
            n = c.execute(
                "INSERT INTO decision_records (record_id, request_id, stage, decision, decided_by, payload, created_at)"
                " SELECT record_id, request_id, stage, decision, decided_by, payload, created_at"
                " FROM pending_records WHERE request_id=? ORDER BY seq", (request_id,)).rowcount
            c.execute("DELETE FROM pending_records WHERE request_id=?", (request_id,))
            c.execute("UPDATE requests SET committed_at=? WHERE request_id=? AND committed_at IS NULL",
                      (now().isoformat(), request_id))
        return n

    def discard_request(self, request_id: str, status: str) -> int:
        """A request that ended before the commit point: drop its pending log.
        Refused once committed. The trace is kept (operational log, 7 days)."""
        if self.is_committed(request_id):
            raise ValueError("a committed request cannot be discarded")
        with self._lock, self._conn() as c:
            n = c.execute("DELETE FROM pending_records WHERE request_id=?", (request_id,)).rowcount
            c.execute("UPDATE requests SET ended_at=?, status=? WHERE request_id=?",
                      (now().isoformat(), status, request_id))
        return n

    def end_request(self, request_id: str, status: str) -> None:
        with self._lock, self._conn() as c:
            c.execute("UPDATE requests SET ended_at=?, status=? WHERE request_id=?",
                      (now().isoformat(), status, request_id))

    def _rows(self, table: str, request_id: str | None) -> list[dict]:
        q, args = f"SELECT * FROM {table}", ()
        if request_id:
            q, args = q + " WHERE request_id = ?", (request_id,)
        with self._conn() as c:
            rows = c.execute(q + " ORDER BY seq", args).fetchall()
        return [dict(r) | {"payload": json.loads(r["payload"])} for r in rows]

    def records(self, request_id: str | None = None) -> list[dict]:
        """The permanent record."""
        return self._rows("decision_records", request_id)

    def pending(self, request_id: str | None = None) -> list[dict]:
        return self._rows("pending_records", request_id)

    def recent_analyses(self, limit: int = 10) -> list[dict]:
        """Home's list: requests that reached the permanent record, newest first.
        Built from decision records only; a discarded request never appears."""
        with self._conn() as c:
            reqs = c.execute("SELECT * FROM requests WHERE committed_at IS NOT NULL"
                             " ORDER BY opened_at DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for r in reqs:
            recs = self.records(r["request_id"])
            view = next((x["payload"].get("view") for x in recs if x["decision"] == "thesis_user_frozen"), None) \
                or next((x["payload"].get("view") for x in recs if x["decision"] == "thesis_drafted"), None)
            sel = [x["payload"].get("selection") for x in recs if x["decision"] == "selection"]
            out.append({"request_id": r["request_id"], "symbol": r["symbol"], "view": view,
                        "strategy": _strategy(sel[-1]) if sel else None,
                        "status": r["status"] or "open", "opened_at": r["opened_at"], "ended_at": r["ended_at"]})
        return out

    def purge_old_traces(self) -> int:
        """Delete traces older than the retention period for requests that never
        reached the permanent record. Traces of committed requests are kept."""
        cutoff = (now() - dt.timedelta(days=self.TRACE_RETENTION_DAYS)).isoformat()
        with self._lock, self._conn() as c:
            return c.execute(
                "DELETE FROM trace WHERE created_at < ? AND (request_id IS NULL OR request_id NOT IN"
                " (SELECT request_id FROM requests WHERE committed_at IS NOT NULL))", (cutoff,)).rowcount

    # ---- trace ------------------------------------------------------------------------

    def trace(self, request_id: str | None, run_id: str, agent: str, step: int, kind: str,
              payload: dict) -> None:
        body = settings.redact(json.dumps(payload, default=str))
        with self._lock, self._conn() as c:
            c.execute(
                "INSERT INTO trace (request_id, run_id, agent, step, kind, payload, created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (request_id, run_id, agent, step, kind, body, now().isoformat()))

    def trace_rows(self, run_id: str | None = None, request_id: str | None = None) -> list[dict]:
        q, args = "SELECT * FROM trace", []
        if run_id:
            q, args = q + " WHERE run_id = ?", [run_id]
        elif request_id:
            q, args = q + " WHERE request_id = ?", [request_id]
        with self._conn() as c:
            rows = c.execute(q + " ORDER BY seq", args).fetchall()
        return [dict(r) | {"payload": json.loads(r["payload"])} for r in rows]

    # ---- evidence store ---------------------------------------------------------------

    def add_evidence(self, request_id: str | None, item_key: str, item: dict) -> str:
        """Store one evidence item for a request and return its id (E1, E2, ...).
        The same item fetched again in the request keeps its first id."""
        rid = request_id or "adhoc"
        with self._lock, self._conn() as c:
            r = c.execute("SELECT evidence_id FROM evidence WHERE request_id=? AND item_key=?",
                          (rid, item_key)).fetchone()
            if r:
                return r[0]
            n = c.execute("SELECT COUNT(*) FROM evidence WHERE request_id=?", (rid,)).fetchone()[0]
            eid = f"E{n + 1}"
            body = settings.redact(json.dumps({**item, "id": eid}, default=str, ensure_ascii=False))
            c.execute("INSERT INTO evidence (request_id, evidence_id, item_key, item, created_at) VALUES (?,?,?,?,?)",
                      (rid, eid, item_key, body, now().isoformat()))
        return eid

    def evidence(self, request_id: str | None) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("SELECT item FROM evidence WHERE request_id=? ORDER BY seq",
                             (request_id or "adhoc",)).fetchall()
        return [json.loads(r[0]) for r in rows]

    # ---- spend ------------------------------------------------------------------------

    def add_spend(self, request_id: str | None, run_id: str, agent: str, model: str,
                  usage: dict, cost: float) -> None:
        with self._lock, self._conn() as c:
            c.execute(
                "INSERT INTO spend (request_id, run_id, agent, model, input_tokens, output_tokens,"
                " cache_read_tokens, cache_write_tokens, cost_usd, day, created_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (request_id, run_id, agent, model, usage.get("input_tokens", 0),
                 usage.get("output_tokens", 0), usage.get("cache_read_tokens", 0),
                 usage.get("cache_write_tokens", 0), cost, today(), now().isoformat()))

    def spent_request(self, request_id: str | None) -> float:
        if not request_id:
            return 0.0
        with self._conn() as c:
            return c.execute("SELECT COALESCE(SUM(cost_usd),0) FROM spend WHERE request_id=?",
                             (request_id,)).fetchone()[0]

    def spent_day(self, day: str | None = None) -> float:
        with self._conn() as c:
            return c.execute("SELECT COALESCE(SUM(cost_usd),0) FROM spend WHERE day=?",
                             (day or today(),)).fetchone()[0]

    # ---- cache ------------------------------------------------------------------------

    def cache_get(self, key: str) -> bytes | None:
        with self._conn() as c:
            r = c.execute("SELECT body FROM cache WHERE key=? AND day=?", (key, today())).fetchone()
        return r[0] if r else None

    def cache_put(self, key: str, source: str, body: bytes) -> None:
        with self._lock, self._conn() as c:
            c.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?,?,?)",
                      (key, source, today(), body, now().isoformat()))
