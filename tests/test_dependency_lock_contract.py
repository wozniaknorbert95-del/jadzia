"""Regression contracts for the Python 3.11 dependency supply chain."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
REQUIREMENTS = REPO_ROOT / "requirements.txt"
LOCK = REPO_ROOT / "requirements.lock"
UV_LOCK = REPO_ROOT / "uv.lock"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _project_dependencies() -> list[str]:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    return project["dependencies"]


def test_python_runtime_is_locked_to_supported_311_series() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]

    assert project["requires-python"] == ">=3.11,<3.12"


def test_chromadb_is_excluded_until_a_fixed_release_exists() -> None:
    """PYSEC-2026-311 affects every currently published ChromaDB 1.x release."""
    declared = {
        requirement.split("[", 1)[0].split("=", 1)[0].lower()
        for requirement in _project_dependencies()
    }
    lock = LOCK.read_text(encoding="utf-8").lower()

    assert "chromadb" not in declared
    assert not re.search(r"^chromadb==", lock, flags=re.MULTILINE)


def test_pip_entry_point_cannot_bypass_the_generated_lock() -> None:
    assert REQUIREMENTS.read_text(encoding="utf-8").splitlines()[-1] == "-r requirements.lock"


def test_exported_lock_pins_every_declared_runtime_dependency() -> None:
    lock = LOCK.read_text(encoding="utf-8")
    pinned_names = {
        match.group(1).lower().replace("_", "-")
        for match in re.finditer(r"^([A-Za-z0-9_.-]+)==[^\s]+", lock, flags=re.MULTILINE)
    }

    for requirement in _project_dependencies():
        name = re.split(r"[<>=!~\[\s]", requirement, maxsplit=1)[0]
        assert name.lower().replace("_", "-") in pinned_names


def test_uv_lock_pins_all_declared_optional_dependencies() -> None:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    optional_dependencies = project["optional-dependencies"]
    locked_names = set(
        re.findall(
            r'^name = "([^"]+)"$',
            UV_LOCK.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    )

    for group in optional_dependencies.values():
        for requirement in group:
            name = re.split(r"[<>=!~\[\s]", requirement, maxsplit=1)[0]
            assert name.lower().replace("_", "-") in locked_names


def test_ci_blocks_dependency_and_secret_regressions() -> None:
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "pip-audit --strict -r requirements.lock" in workflow
    assert "gitleaks/gitleaks-action@v2" in workflow
    assert "GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}" in workflow


def test_uv_lock_is_version_controlled() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "!uv.lock" in gitignore
    assert UV_LOCK.is_file()
