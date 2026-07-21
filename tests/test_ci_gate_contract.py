"""Release-gate contract tests for the canonical GitHub Actions workflow."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
LEGACY_TESTS_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "tests.yml"


def test_ci_runs_full_suite_with_real_coverage_artifact() -> None:
    """A regression anywhere under tests/ must run in the blocking test job."""
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "python -m pytest tests/" in workflow
    assert "--cov-report=xml:coverage.xml" in workflow
    assert "uses: actions/upload-artifact@v4" in workflow
    assert "path: coverage.xml" in workflow
    assert "fail_ci_if_error: true" in workflow


def test_ci_has_single_full_test_gate_owner() -> None:
    """The legacy partial-suite workflow must not provide a misleading green check."""
    assert not LEGACY_TESTS_WORKFLOW.exists()
