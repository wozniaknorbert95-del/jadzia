"""Shared pytest hooks for jadzia-core."""

from __future__ import annotations

import os

# customer_agent binds `client` at import time; CI runs without .env.
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-ci-placeholder")
