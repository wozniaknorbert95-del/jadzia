"""Regression guard for the documented validation workflow."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
JADZIA_TEST_WORKFLOW = REPO_ROOT / ".agents" / "workflows" / "jadzia-test.md"


def test_jadzia_test_documents_the_canonical_ci_gate() -> None:
    workflow = JADZIA_TEST_WORKFLOW.read_text(encoding="utf-8")
    ci_workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "python -m pytest tests/" in workflow
    assert "--cov-report=xml:coverage.xml" in workflow
    assert "tests/integration" not in workflow
    assert "TestCommanderUiSmoke" in workflow
    assert "python -m pytest tests/" in ci_workflow
