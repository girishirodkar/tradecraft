"""Paths, configuration files and secrets.

Secrets are read from .env into memory only. Nothing in this module prints,
logs or returns a secret's value except `secret()`, whose callers pass it
straight to a client. `redact()` removes every known secret value from text
before it is traced or stored.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
DATA = ROOT / "data"
ENV_FILE = ROOT / ".env"

SECRET_KEYS = ("ANTHROPIC_API_KEY", "FMP_API_KEY", "FRED_API_KEY", "SEC_USER_AGENT", "TRADIER_TOKEN")


def load_json(name: str) -> dict:
    with open(CONFIG / name) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def limits() -> dict:
    return load_json("limits.json")


@lru_cache(maxsize=1)
def models() -> dict:
    return load_json("models.json")


@lru_cache(maxsize=1)
def _env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def secret(name: str) -> str | None:
    """The value of a secret from .env, for passing to a client. Never print it."""
    v = _env().get(name)
    return v or None


def has_secret(name: str) -> bool:
    return bool(_env().get(name))


def redact(text: str) -> str:
    """Replace every known secret value in `text` with a placeholder."""
    if not text:
        return text
    for k in SECRET_KEYS:
        v = _env().get(k)
        if v and len(v) >= 6 and v in text:
            text = text.replace(v, f"<{k}>")
    return text


def data_dir() -> Path:
    DATA.mkdir(exist_ok=True)
    return DATA
