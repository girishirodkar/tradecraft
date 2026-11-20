"""The evidence store and the grades set in code. No network."""
import datetime as dt

import pytest

from tradecraft import evidence, tools
from tradecraft.data import directory, edgar
from tradecraft.harness import ToolContext
from tradecraft.storage import now

RID = "req_test"


def day(offset):
    return (now().date() + dt.timedelta(days=offset)).isoformat()


@pytest.fixture(autouse=True)
def filings(monkeypatch):
    monkeypatch.setattr(edgar, "list_filings", lambda sym, store=None, **kw: {"filings": [
        {"form": "8-K", "filed": day(-3), "accession": "A-1", "items": [{"item": "2.02", "about": "results"}]},
        {"form": "10-K", "filed": day(-200), "accession": "A-2", "items": None}]})


def news(store, **kw):
    return evidence.capture("get_company_news", {"symbol": "NVDA"}, {"source": "FMP", "items": [
        {"published": day(-2) + " 10:00:00", "publisher": "Wire", "title": "Chip demand", "url": "u1", "text": "t"},
        {"published": day(-90), "publisher": "Wire", "title": "Old", "url": "u2", "text": "t"}]}, store, RID)


def test_each_news_item_is_stored_and_comes_back_with_its_id(store):
    out = news(store)
    assert [i["evidence_id"] for i in out["items"]] == ["E1", "E2"]
    saved = store.evidence(RID)
    assert saved[0]["family"] == evidence.NEWS and saved[0]["source"].startswith("Wire")
    assert not saved[0]["primary_source"] and saved[0]["specific"] and saved[0]["date"] == day(-2)


def test_the_same_item_fetched_again_keeps_its_id(store):
    news(store)
    assert [i["evidence_id"] for i in news(store)["items"]] == ["E1", "E2"]
    assert len(store.evidence(RID)) == 2


def test_stored_evidence_cannot_be_edited(store):
    news(store)
    with pytest.raises(Exception, match="cannot be edited"):
        with store._conn() as c:
            c.execute("UPDATE evidence SET item='{}'")


def test_grades_come_from_the_three_checks(store):
    news(store)                                                           # E1 recent, E2 old
    evidence.capture("read_filing_section", {"symbol": "NVDA", "accession": "A-1", "document": "ex99.htm"},
                     {"section": "whole document", "part": 1, "parts": 1, "text": "Guidance raised."}, store, RID)
    evidence.capture("read_filing_section", {"symbol": "NVDA", "accession": "A-2", "document": "10k.htm"},
                     {"section": "Item 1A", "part": 1, "parts": 1, "text": "Risk factors."}, store, RID)
    evidence.capture("get_macro_calendar", {}, {"fomc_decisions": []}, store, RID)
    evidence.capture("get_company_profile", {"symbol": "NVDA"}, {"name": "NVIDIA", "source": "FMP"}, store, RID)
    g = evidence.graded(store, RID)
    assert g["E1"]["grade"] == "moderate" and g["E1"]["checks"] == {"primary_source": False, "recent": True, "specific": True}
    assert g["E2"]["grade"] == "weak"                                     # specific only
    assert g["E3"]["grade"] == "strong" and g["E3"]["kind"] == "earnings release (8-K)" and g["E3"]["input"] == 2
    assert g["E4"]["grade"] == "moderate" and g["E4"]["kind"] == "company filing (10-K)"   # primary, specific, old
    assert g["E5"]["grade"] == "moderate" and g["E5"]["family"] == evidence.MACRO          # official, recent, general
    assert g["E6"]["grade"] == "weak"                                     # a profile has no date


def test_recent_also_means_since_the_latest_earnings_report(store):
    out = evidence.capture("get_earnings", {"symbol": "NVDA"}, {"source": "FMP", "next_report_date": day(80),
                           "past_reports": [{"date": day(-60), "eps_actual": 1.0}, {"date": day(-150), "eps_actual": 0.9}]},
                           store, RID)
    assert out["next_report_evidence_id"] == "E1" and [p["evidence_id"] for p in out["past_reports"]] == ["E2", "E3"]
    g = evidence.graded(store, RID)
    assert g["E2"]["checks"]["recent"] and not g["E3"]["checks"]["recent"]       # 60 days old, but the latest report
    assert not g["E2"]["primary_source"]                                         # a provider's copy of the figures
    assert g["E2"]["grade"] == "moderate" and g["E3"]["grade"] == "weak"


def test_a_finding_takes_the_grade_of_its_best_cited_item(store):
    news(store)
    g = evidence.graded(store, RID)
    assert evidence.finding_grade(["E2", "E1"], g) == ("moderate", [])
    assert evidence.finding_grade(["E2", "E9"], g) == ("weak", ["E9"])
    assert evidence.finding_grade([], g) == (None, [])


def test_computed_inputs_are_stored_with_their_role(store):
    eid = evidence.add_computed(store, RID, "technical", {"trend": {}}, "NVDA")
    item = evidence.graded(store, RID)[eid]
    assert item["role"] == evidence.DESCRIPTION and item["family"] == ""
    sector = evidence.add_computed(store, RID, "sector_context", {}, "NVDA")
    assert evidence.graded(store, RID)[sector]["family"] == evidence.MACRO


def test_registry_tools_store_what_they_return(store, monkeypatch):
    from tradecraft.data import fmp
    monkeypatch.setattr(directory, "is_listed", lambda s, store=None: True)
    monkeypatch.setattr(fmp, "analyst_estimates", lambda s, store=None: {"source": "FMP", "symbol": s, "fiscal_years": []})
    reg = tools.build_registry()
    ctx = ToolContext(store=store, request_id=RID, run_id="run", agent="evidence_retriever", limits={})
    out = reg.get("get_analyst_estimates").fn(ctx, symbol="NVDA")
    assert out["evidence_id"] == "E1" and store.evidence(RID)[0]["kind"] == "analyst consensus"
