"""The local web application: pages and a small JSON API on localhost.

    .venv/bin/python -m uvicorn tradecraft.web.app:app --host 127.0.0.1 --port 8321

The pages are the approved mock-up's markup and styles with its hard-coded data
replaced by calls to this API. There is no build step. The engine holds one
open request at a time; the browser shows whatever the workflow's state says.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .. import testfail
from ..data import chain, directory, session
from ..steps import real_steps
from ..storage import Store
from ..workflow import Busy, Workflow
from ..workflow.state import HIDDEN_FROM_SCREEN

STATIC = Path(__file__).parent / "static"
DEMO: dict | None = None      # set by tradecraft/demo.py: the recorded demo, and the date of its data


class StartBody(BaseModel):
    symbol: str


class ActionBody(BaseModel):
    action: str
    rationale: str | None = None
    settings: dict | None = None
    params: dict | None = None
    selection: dict | None = None
    # "Take a view yourself"
    direction: str | None = None
    horizon_days: int | None = None
    relied_on: list[str] | None = None
    conditions: list[str] | None = None


def screen_view(view: dict | None, store: Store) -> dict | None:
    """What a screen may see of a request: the record without its hidden parts."""
    if view is None:
        return None
    state = {k: v for k, v in view["state"].items() if k not in HIDDEN_FROM_SCREEN}
    req = store.request(view["request_id"]) or {}
    return {"request_id": view["request_id"], "symbol": state.get("symbol"), "opened_at": req.get("opened_at"),
            "pause": view["pause"], "done": view["done"], "running": view.get("running", False),
            "error": view.get("error"), "progress": view.get("progress"), "state": state,
            "test_failures": testfail.active(), "demo": DEMO}


def create_app(store: Store | None = None, steps: dict | None = None, symbols: dict | None = None) -> FastAPI:
    store = store or Store()
    listing = symbols if symbols is not None else directory.load(store)
    listed = {s[0] for s in listing["symbols"]}
    wf = Workflow(store, steps=steps if steps is not None else real_steps(), symbol_ok=lambda s: s in listed)
    wf.recover_interrupted()          # a request left open by a restart is ended, not resumed
    store.purge_old_traces()

    app = FastAPI(title="Tradecraft", docs_url=None, redoc_url=None)
    app.state.workflow, app.state.store = wf, store

    @app.get("/api/home")
    def home():
        return {"market": session.status(), "snapshot": chain.snapshot_info(),
                "recent": store.recent_analyses(10), "open": screen_view(wf.open_view(), store),
                "test_failures": testfail.active(), "demo": DEMO}

    @app.get("/api/symbols")
    def symbol_list():
        # no-store: the list is local and changes on the weekly refresh; a stale copy
        # in the browser would search an old list and an old ordering
        return JSONResponse(listing, headers={"Cache-Control": "no-store"})

    @app.post("/api/requests")
    def start(body: StartBody):
        symbol = body.symbol.strip().upper()
        try:
            return screen_view(wf.start(symbol), store)
        except ValueError as e:
            raise HTTPException(404, str(e)) from e
        except Busy as e:
            raise HTTPException(409, {"message": str(e), "request_id": e.request_id}) from e

    @app.get("/api/requests/open")
    def open_request():
        return screen_view(wf.open_view(), store)

    def _must_be_open(request_id: str):
        if request_id not in store.open_request_ids():
            raise HTTPException(404, "That request is not open.")

    @app.post("/api/requests/{request_id}/action")
    def act(request_id: str, body: ActionBody):
        _must_be_open(request_id)
        if body.action == "leave":
            raise HTTPException(400, "Use the leave endpoint.")
        fields = {k: v for k, v in body.model_dump().items() if k != "action" and v is not None}
        try:
            if body.action == "stop" and wf.view(request_id)["running"]:
                wf.request_stop(request_id)       # Stop on the working panel: the agents stop at their next step
                return screen_view(wf.view(request_id), store)
            # A quick step answers at once; while agents run the view says "running" and the page polls.
            return screen_view(wf.resume_bg(request_id, body.action, **fields), store)
        except Busy as e:
            raise HTTPException(409, {"message": str(e), "request_id": e.request_id}) from e

    @app.post("/api/requests/{request_id}/leave")
    def leave(request_id: str):
        _must_be_open(request_id)
        return {"left": True, "view": screen_view(wf.leave(request_id), store)}

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-store"})

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


def __getattr__(name: str):
    """`tradecraft.web.app:app` for uvicorn, created on first use so that importing
    this module (in tests) does not open the real database."""
    if name == "app":
        global _app
        try:
            return _app
        except NameError:
            from .. import research
            research.ensure_current()         # the research index matches the corpus before any request
            _app = create_app()
            return _app
    raise AttributeError(name)
