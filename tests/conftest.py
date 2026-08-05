"""Shared pytest hooks for jadzia-core."""

from __future__ import annotations

import os

# Hermetic test env (8-01): several app modules call load_dotenv() at import
# time (core/services, api/app, agent/tools/*), so the suite inherits whatever
# .env the HOST has. On the VPS that is the production .env (JWT_SECRET,
# JADZIA_ENV=production, webhooks, marketing HITL...) which flipped tests into
# prod behavior (401/404/500) that local dev never sees. Contract: unit tests
# run dotenv-free. conftest loads before any app module, so stubbing
# dotenv.load_dotenv here neutralizes every later `from dotenv import
# load_dotenv`. Tests that need specific env set it via monkeypatch.
import dotenv

dotenv.load_dotenv = lambda *args, **kwargs: False  # type: ignore[assignment]

# Belt-and-braces flag honored by core/services.py (documents the contract).
os.environ["JADZIA_TEST_NO_DOTENV"] = "1"

# customer_agent binds `client` at import time; CI runs without .env.
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-ci-placeholder")

# --- S7: test suite must leave a clean git tree -------------------------------
# Demand OS writers resolve via state_paths (env override first). Without
# overrides, a local/prod run appends to TRACKED set-now files (CONTROL-AUDIT,
# MEMORY) — every suite run produced git drift. Contract: writes land in a
# per-test tmp dir; read-visible files (MEMORY, calendar) are seeded from the
# repo so reads still see SoT content. Test-local monkeypatch.setenv overrides
# win over this fixture (it runs first).
import shutil
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SET_NOW = _REPO_ROOT / "docs" / "ops" / "demand-os" / "set-now"

_STATE_ENV_FILES = {
    "DEMAND_OS_MEMORY": "MEMORY.json",
    "DEMAND_OS_AUDIT_LOG": "CONTROL-AUDIT.jsonl",
    "DEMAND_OS_AGENTS_HEARTBEAT": "AGENTS-HEARTBEAT.json",
    "DEMAND_OS_A2A_BUS": "A2A-HANDOFFS.jsonl",
    "DEMAND_OS_ENGAGE_LOG": "ENGAGE-LOG.jsonl",
    "DEMAND_OS_GROWTH_EVENTS": "GROWTH-EVENTS.jsonl",
    "DEMAND_OS_VALIDATOR_LOG": "VALIDATOR-LOG.csv",
    "DEMAND_OS_CONTENT_CALENDAR": "CONTENT-CALENDAR.json",
    "DEMAND_OS_BLOG_DRAFTS": "BLOG-DRAFTS",
}

# Read-visible SoT: seed the tmp copy from the tracked file so module reads
# keep working exactly as before the redirect.
_SEED_FROM_REPO = ("MEMORY.json", "CONTENT-CALENDAR.json")


@pytest.fixture(autouse=True)
def _demand_os_state_tmp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # Hermetic suite: prod sets DEMAND_OS_STALENESS_BLOCKING=1 (G1); tests
    # choose severity explicitly via monkeypatch, never via inherited env.
    monkeypatch.delenv("DEMAND_OS_STALENESS_BLOCKING", raising=False)
    for env_var, name in _STATE_ENV_FILES.items():
        target = tmp_path / name
        if name in _SEED_FROM_REPO:
            src = _SET_NOW / name
            if src.is_file():
                shutil.copy(src, target)
        elif name == "BLOG-DRAFTS":
            target.mkdir(exist_ok=True)
        monkeypatch.setenv(env_var, str(target))
    yield
