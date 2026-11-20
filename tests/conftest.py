import pytest

from tradecraft.storage import Store


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "test.sqlite3")


def kinds(store, run_id):
    return [(r["kind"], r["payload"]) for r in store.trace_rows(run_id=run_id)]


def guardrails(store, run_id):
    return [p for k, p in kinds(store, run_id) if k == "guardrail"]
