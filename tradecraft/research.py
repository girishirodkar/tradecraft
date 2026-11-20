"""The research index: the project's own research, cut into passages and searched locally.

Stage 4's retrieval reads nothing else (docs/on-demand-mode-design.md, "Stage 4
redesigned", step 4): the nineteen reports in docs/research/, the factor
specification and the decision records. No web search.

- A passage is a claim block of a report (from one "**CLAIM**" to the next), or
  a run of paragraphs under one heading. It keeps its source file, its section
  heading and its evidence grade.
- The grade is the report's own "EVIDENCE STRENGTH" label, quoted as written
  (operator decision, 19 November 2026). Where a passage has none it is
  "ungraded". Nothing is mapped onto stage 2's three grades.
- Two search methods over the same passages, in this order: chromadb with its
  built-in local embedding model (all-MiniLM-L6-v2, no key), then keyword
  search. Which one answered is recorded with every challenge.

The app checks the index once when it starts and rebuilds it if a corpus file has
changed (`ensure_current`); it never builds while serving a request, so an edit
made while the app runs takes effect at the next start. To build by hand, which
also downloads the embedding model the first time:

    .venv/bin/python -m tradecraft.research build
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from . import net, settings

SOURCES = ("docs/research", "docs/factor-spec.md", "docs/decisions")
INDEX_DIR = "research-index"
MODEL_DIR = "embedding-model"
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION = "research"
MAX_CHARS = 1600                 # a passage of running text
MAX_CLAIM_CHARS = 2600           # a claim block is kept whole up to this
UNGRADED = "ungraded"

_HEADING = re.compile(r"(?m)^(#{1,4})\s+(.*)$")
_CLAIM = re.compile(r"(?m)^\*\*CLAIMS?\b")
_GRADE = re.compile(r"\*\*EVIDENCE STRENGTH:?\*\*:?\s*(.+)")
_WORD = re.compile(r"[a-z][a-z0-9'-]+")
_STOP = set("""a an and are as at be been but by can did do does for from had has have how if in into is it its
not of on or over so than that the their then there these they this to under was were what when which while who
why will with would whether following after before about more most less much many such also may might could should
whose where both each other any all some no nor only own same very just being between during through against
above below up down out off again further once here most""".split())


def config() -> dict:
    return settings.load_json("stage4.json")["retrieval"]


# ---- passages ------------------------------------------------------------------------------

def _files() -> list[Path]:
    out: list[Path] = []
    for s in SOURCES:
        p = net.readable(s)
        out += sorted(p.glob("*.md")) if p.is_dir() else [p]
    return out


def _grade(text: str) -> str:
    m = _GRADE.search(text)
    if not m:
        return UNGRADED
    g = re.sub(r"[*_`]", "", m.group(1)).strip()
    return (g[:157].rstrip() + "...") if len(g) > 160 else g


def _pieces(text: str, limit: int) -> list[str]:
    """Paragraphs gathered into pieces of at most `limit` characters."""
    out, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        while len(para) > limit:                     # one very long paragraph (a table): cut at a line end
            cut = para.rfind("\n", 0, limit)
            cut = cut if cut > limit // 2 else limit
            if cur:
                out.append(cur)
                cur = ""
            out.append(para[:cut].strip())
            para = para[cut:].strip()
        if cur and len(cur) + len(para) + 2 > limit:
            out.append(cur)
            cur = para
        else:
            cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        out.append(cur)
    return out


def split_document(name: str, text: str) -> list[dict]:
    """One file as passages: {source, section, grade, text}. Pure; used by the tests."""
    out = []
    marks = list(_HEADING.finditer(text))
    title = marks[0].group(2).strip() if marks and marks[0].group(1) == "#" else name
    spans = [(None, 0, marks[0].start() if marks else len(text))]
    trail: dict[int, str] = {}
    for i, m in enumerate(marks):
        level = len(m.group(1))
        trail = {k: v for k, v in trail.items() if k < level}
        trail[level] = re.sub(r"[*_`]", "", m.group(2)).strip()
        heading = " > ".join(trail[k] for k in sorted(trail) if k > 1) or trail.get(1, title)
        spans.append((heading, m.end(), marks[i + 1].start() if i + 1 < len(marks) else len(text)))
    for heading, a, b in spans:
        body = text[a:b].strip()
        if len(body) < 80:
            continue
        starts = [m.start() for m in _CLAIM.finditer(body)]
        blocks = [body[:starts[0]]] if starts else [body]
        blocks += [body[s:e] for s, e in zip(starts, starts[1:] + [len(body)])]
        for k, block in enumerate(blocks):
            block = block.strip()
            if len(block) < 80:
                continue
            is_claim = bool(starts) and k > 0
            grade = _grade(block)
            parts = [block] if is_claim and len(block) <= MAX_CLAIM_CHARS else _pieces(block, MAX_CHARS)
            for part in parts:
                if len(part) < 80:
                    continue
                out.append({"source": name, "section": heading or title, "text": part,
                            "grade": grade if is_claim else _grade(part)})
    return out


def _short(name: str) -> str:
    m = re.match(r"research-(\d+)", name)
    if m:
        return f"R{m.group(1)}"
    if name.startswith("factor-spec"):
        return "SPEC"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.*)\.md", name)
    return "D" + m.group(2) + m.group(3) + "".join(w[0] for w in m.group(4).split("-"))[:4].upper() if m else "X"


@lru_cache(maxsize=1)
def corpus() -> tuple[tuple[dict, ...], str]:
    """Every passage of the corpus, each with a stable id, and a fingerprint of the files."""
    out, digest = [], hashlib.sha256()
    for p in _files():
        text = p.read_text(encoding="utf-8")
        digest.update(p.name.encode() + b"\0" + text.encode())
        for i, x in enumerate(split_document(p.name, text), 1):
            out.append({**x, "id": f"{_short(p.name)}-{i:03d}"})
    return tuple(out), digest.hexdigest()[:16]


# ---- keyword search (the fallback, and the tests' index) ------------------------------------

def _terms(text: str) -> list[str]:
    return [w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2]


class KeywordIndex:
    """Scores a passage by the share of the query's weight it contains: rarer words weigh more."""
    method = "keyword"

    def __init__(self, passages):
        self.passages = list(passages)
        self.sets = [set(_terms(p["text"] + " " + p["section"])) for p in self.passages]
        df = Counter(t for s in self.sets for t in s)
        n = max(len(self.passages), 1)
        self.idf = {t: math.log(1 + n / c) for t, c in df.items()}

    def search(self, query: str, n: int = 8) -> list[dict]:
        q = set(_terms(query))
        total = sum(self.idf.get(t, 0.0) for t in q)
        if not total:
            return []
        scored = []
        for p, s in zip(self.passages, self.sets):
            hit = sum(self.idf[t] for t in q & s)
            if hit:
                scored.append((hit / total, p))
        scored.sort(key=lambda x: (-x[0], x[1]["id"]))
        return [{**p, "score": round(sc, 3)} for sc, p in scored[:n]]

    def bar(self) -> float:
        return config()["relevance_bar"]["keyword"]


# ---- chromadb -----------------------------------------------------------------------------

def _embedder():
    from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

    class Local(ONNXMiniLM_L6_V2):
        # The model is kept under data/ (git-ignored), not in the home directory.
        DOWNLOAD_PATH = settings.data_dir() / MODEL_DIR / MODEL_NAME
    return Local()


def _client():
    import chromadb
    from chromadb.config import Settings
    return chromadb.PersistentClient(path=str(net.writable(settings.data_dir() / INDEX_DIR)),
                                     settings=Settings(anonymized_telemetry=False))


class ChromaIndex:
    """Passages embedded with chromadb's default local model; cosine similarity."""
    method = "chromadb (all-MiniLM-L6-v2, local)"

    def __init__(self, collection, passages):
        self.collection = collection
        self.by_id = {p["id"]: p for p in passages}

    def search(self, query: str, n: int = 8) -> list[dict]:
        r = self.collection.query(query_texts=[query], n_results=n)
        out = []
        for pid, dist in zip(r["ids"][0], r["distances"][0]):
            if pid in self.by_id:
                out.append({**self.by_id[pid], "score": round(1.0 - dist, 3)})
        return out

    def bar(self) -> float:
        return config()["relevance_bar"]["chromadb"]


def build(force: bool = False) -> dict:
    """Embed the corpus into data/research-index. Skipped when the files have not changed."""
    passages, stamp = corpus()
    client = _client()
    try:
        col = client.get_collection(COLLECTION, embedding_function=_embedder())
        if not force and (col.metadata or {}).get("corpus") == stamp and col.count() == len(passages):
            return {"built": False, "passages": len(passages), "corpus": stamp}
        client.delete_collection(COLLECTION)
    except Exception:  # noqa: BLE001 - no collection yet
        pass
    col = client.create_collection(COLLECTION, embedding_function=_embedder(),
                                   metadata={"hnsw:space": "cosine", "corpus": stamp})
    for i in range(0, len(passages), 200):
        chunk = passages[i:i + 200]
        col.add(ids=[p["id"] for p in chunk], documents=[f"{p['section']}\n{p['text']}" for p in chunk],
                metadatas=[{"source": p["source"], "section": p["section"], "grade": p["grade"]} for p in chunk])
    return {"built": True, "passages": len(passages), "corpus": stamp}


def model_present() -> bool:
    return (settings.data_dir() / MODEL_DIR / MODEL_NAME / "onnx" / "model.onnx").exists()


def ensure_current() -> dict:
    """Called once when the app starts, before it serves a request (operator decision,
    19 November 2026): if a corpus file has changed since the index was built, or there
    is no index, build it. About 11 seconds; nothing is done when the index is current.
    The embedding model is not downloaded here: with no model on disk the app starts on
    keyword search and says how to build. A failure never stops the app."""
    _OPENED.clear()
    try:
        if not model_present():
            out = {"built": False, "method": "keyword", "note": "the embedding model is not on disk; run "
                   "`.venv/bin/python -m tradecraft.research build` once to download it (79 MB) and build the index"}
        else:
            out = {**build(), "method": "chromadb", "note": None}
    except Exception as e:  # noqa: BLE001 - the app starts anyway, on keyword search
        out = {"built": False, "method": "keyword", "note": f"the index could not be built ({type(e).__name__})"}
    print("Research index: " + ("rebuilt, " if out.get("built") else "") + out["method"]
          + (f", {out['passages']:,} passages" if out.get("passages") else "")
          + (f". Note: {out['note']}" if out.get("note") else "."), flush=True)
    return out


_OPENED: dict = {}


def open_index():
    """The index a request searches: chromadb if its index is built and current,
    else keyword search over the same passages, else None (no passages).
    Returns (index, note); the note says why a method was passed over."""
    if "index" in _OPENED:
        return _OPENED["index"], _OPENED["note"]
    note = None
    try:
        passages, stamp = corpus()
    except Exception as e:  # noqa: BLE001 - the corpus cannot be read: no passages
        _OPENED.update(index=None, note=f"the research corpus could not be read ({type(e).__name__})")
        return None, _OPENED["note"]
    index = None
    try:
        col = _client().get_collection(COLLECTION, embedding_function=_embedder())
        if (col.metadata or {}).get("corpus") == stamp and col.count() == len(passages):
            index = ChromaIndex(col, passages)
        else:
            note = "the chromadb index is out of date (run: python -m tradecraft.research build)"
    except Exception as e:  # noqa: BLE001 - not installed, not built, or it cannot be opened
        note = f"the chromadb index could not be opened ({type(e).__name__})"
    if index is None:
        index = KeywordIndex(passages)
    _OPENED.update(index=index, note=note)
    return index, note


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["build"]:
        print(build(force="--force" in sys.argv))
    else:
        ix, why = open_index()
        print(ix.method if ix else None, why)
        for hit in (ix.search(" ".join(sys.argv[1:]), 6) if ix else []):
            print(hit["score"], hit["id"], "|", hit["source"], "|", hit["section"][:60], "|", hit["grade"][:40])
