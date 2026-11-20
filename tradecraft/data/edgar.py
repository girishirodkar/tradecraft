"""Company filings from SEC EDGAR, read by section and never whole.

Three steps, each a tool an agent can call:
1. `list_filings`: the company's recent 10-K, 10-Q and 8-K filings.
2. `list_sections`: what one filing contains. A 10-K or 10-Q is split into its
   Items; an 8-K lists its documents (the cover page and exhibits such as the
   earnings release).
3. `read_section`: the text of one section, held to the per-document limit.

Requests identify themselves with SEC_USER_AGENT from .env (added by the
network helper, never printed) and stay under 5 a second.
"""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser

from .. import net
from ..storage import Store, now

FORMS = ("10-K", "10-Q", "8-K")
ITEM_8K = {
    "1.01": "Entry into a material agreement", "2.02": "Results of operations and financial condition",
    "2.05": "Costs of exit or disposal", "2.06": "Material impairments", "4.02": "Non-reliance on prior statements",
    "5.02": "Departure or appointment of directors or officers", "7.01": "Regulation FD disclosure",
    "8.01": "Other events", "9.01": "Financial statements and exhibits",
}
_SKIP_DOC = re.compile(r"(^R\d+\.htm$|index|^Financial_Report|\.xsd$|\.xml$|\.json$|\.css$|\.js$|\.zip$|\.txt$|"
                       r"\.jpg$|\.gif$|\.png$)", re.IGNORECASE)
_ITEM = re.compile(r"^\s*item\s+(\d{1,2}[a-c]?)\s*[\.:\-–—]?\s*(.{0,120})$", re.IGNORECASE | re.MULTILINE)


class FilingUnavailable(Exception):
    pass


def _json(url: str, source: str, store: Store | None):
    try:
        return net.get_json(url, source=source, store=store)
    except net.FetchFailed as e:
        raise FilingUnavailable(f"SEC EDGAR: {str(e)[:160]}") from e


def cik_for(symbol: str, store: Store | None = None) -> str:
    table = _json("https://www.sec.gov/files/company_tickers.json", "sec.tickers", store)
    want = symbol.upper().replace(".", "-")
    for row in table.values():
        if row["ticker"].upper() == want:
            return f"{int(row['cik_str']):010d}"
    raise FilingUnavailable(f"SEC EDGAR: no company found for {symbol.upper()} (funds and indexes file differently)")


def list_filings(symbol: str, store: Store | None = None, forms: tuple[str, ...] = FORMS, limit: int = 12) -> dict:
    cik = cik_for(symbol, store)
    sub = _json(f"https://data.sec.gov/submissions/CIK{cik}.json", "sec.submissions", store)
    r = sub["filings"]["recent"]
    out = []
    for i, form in enumerate(r["form"]):
        if form not in forms:
            continue
        items = [x for x in (r.get("items", [""] * len(r["form"]))[i] or "").split(",") if x]
        out.append({"form": form, "filed": r["filingDate"][i], "period": r["reportDate"][i] or None,
                    "accession": r["accessionNumber"][i],
                    "items": [{"item": x, "about": ITEM_8K.get(x, "")} for x in items] or None})
        if len(out) >= limit:
            break
    return {"source": "SEC EDGAR submissions", "retrieved": now().isoformat(timespec="minutes"),
            "symbol": symbol.upper(), "company": sub.get("name"), "cik": cik, "filings": out}


# ---- reading one filing ---------------------------------------------------------------

class _Text(HTMLParser):
    BLOCK = {"p", "div", "tr", "br", "li", "h1", "h2", "h3", "h4", "h5", "table", "title"}
    HIDE = {"script", "style", "ix:header", "head"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.HIDE or dict(attrs).get("style", "").replace(" ", "").find("display:none") >= 0:
            self.hidden += 1 if tag in self.HIDE else 0
        if tag in self.BLOCK:
            self.parts.append("\n")
        if tag == "td":
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in self.HIDE and self.hidden:
            self.hidden -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def to_text(markup: str) -> str:
    p = _Text()
    p.feed(markup)
    text = html.unescape("".join(p.parts)).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _folder(cik: str, accession: str) -> str:
    if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession):
        raise FilingUnavailable("SEC EDGAR: the accession number must look like 0001045810-26-000088")
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}"


def _documents(cik: str, accession: str, store: Store | None) -> list[dict]:
    idx = _json(f"{_folder(cik, accession)}/index.json", "sec.index", store)
    docs = []
    for it in idx["directory"]["item"]:
        name = it["name"]
        if name.lower().endswith((".htm", ".html")) and not _SKIP_DOC.search(name):
            docs.append({"document": name, "bytes": int(it.get("size") or 0)})
    if not docs:
        raise FilingUnavailable("SEC EDGAR: no readable document in this filing")
    return docs


def _doc_text(cik: str, accession: str, document: str, store: Store | None) -> str:
    if not re.fullmatch(r"[\w\-.]+\.html?", document, re.IGNORECASE):
        raise FilingUnavailable("SEC EDGAR: not a document of this filing")
    try:
        raw = net.get(f"{_folder(cik, accession)}/{document}", source="sec.document", store=store)
    except net.FetchFailed as e:
        raise FilingUnavailable(f"SEC EDGAR: {str(e)[:160]}") from e
    return to_text(raw.decode("utf-8", "replace"))


def split_items(text: str) -> list[dict]:
    """Split a 10-K or 10-Q into its Items. A filing names each Item twice (the
    table of contents, then the section itself); the longer run of text is kept."""
    marks = list(_ITEM.finditer(text))
    best: dict[str, dict] = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        key = m.group(1).upper()
        body = text[m.start():end].strip()
        if key not in best or len(body) > len(best[key]["text"]):
            best[key] = {"section": f"Item {key}", "title": m.group(2).strip(" .:-")[:90], "text": body}
    return [v for v in best.values() if len(v["text"]) > 400]       # drop bare table-of-contents lines


def _est_tokens(text: str) -> int:
    return len(text) // 4 + 1


def list_sections(symbol: str, accession: str, store: Store | None = None) -> dict:
    cik = cik_for(symbol, store)
    docs = _documents(cik, accession, store)
    main = docs[0]["document"]
    items = split_items(_doc_text(cik, accession, main, store)) if len(docs) == 1 or docs[0]["bytes"] > 200_000 else []
    sections = [{"document": main, "section": s["section"], "title": s["title"], "approx_tokens": _est_tokens(s["text"])}
                for s in items]
    if not sections:                       # an 8-K: the cover page and its exhibits, each read whole
        sections = [{"document": d["document"], "section": "whole document", "title": "",
                     "approx_tokens": d["bytes"] // 20 + 1} for d in docs]
    return {"source": "SEC EDGAR", "symbol": symbol.upper(), "accession": accession, "sections": sections,
            "note": "Read one section at a time with read_filing_section."}


def read_section(symbol: str, accession: str, document: str, section: str = "whole document", part: int = 1,
                 store: Store | None = None, max_chars: int = 60_000) -> dict:
    cik = cik_for(symbol, store)
    if document not in {d["document"] for d in _documents(cik, accession, store)}:
        raise FilingUnavailable("SEC EDGAR: not a document of this filing; call list_filing_sections first")
    text = _doc_text(cik, accession, document, store)
    if section != "whole document":
        match = [s for s in split_items(text) if s["section"].lower() == section.lower()]
        if not match:
            raise FilingUnavailable(f"SEC EDGAR: {section} was not found in {document}; call list_filing_sections")
        text = match[0]["text"]
    parts = max(1, -(-len(text) // max_chars))
    part = max(1, min(int(part), parts))
    chunk = text[(part - 1) * max_chars: part * max_chars]
    return {"source": f"SEC EDGAR, {document}", "symbol": symbol.upper(), "accession": accession,
            "section": section, "part": part, "parts": parts,
            "note": (f"Part {part} of {parts}; ask for the next part only if you need it." if parts > 1 else None),
            "text": chunk}
