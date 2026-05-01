from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_readiness_files_exist() -> None:
    required = [
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "workflows" / "security.yml",
        ROOT / "docs" / "ARCHITECTURE.md",
        ROOT / "docs" / "ADAPTER_CONTRACT.md",
        ROOT / "docs" / "RELEASE_CHECKLIST.md",
        ROOT / "docs" / "INTEGRATIONS.md",
        ROOT / "docs" / "FIELD_LESSONS.md",
        ROOT / "scripts" / "privacy_check.sh",
        ROOT / "scripts" / "prepublish_check.sh",
        ROOT / "renovate.json5",
        ROOT / "uv.lock",
    ]

    for path in required:
        assert path.exists(), path


def test_security_workflow_runs_gitleaks() -> None:
    workflow = ROOT / ".github" / "workflows" / "security.yml"
    content = workflow.read_text(encoding="utf-8").lower()

    assert "gitleaks detect --no-git --source . --redact --no-banner" in content
    assert "pull_request" in content
    assert "push" in content
    assert "branches: [main]" in content
