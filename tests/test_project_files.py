from __future__ import annotations

import re
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
        ROOT / ".github" / "dependabot.yml",
        ROOT / "uv.lock",
    ]

    for path in required:
        assert path.exists(), path


def test_security_workflow_runs_history_complete_pinned_gitleaks() -> None:
    workflow = ROOT / ".github" / "workflows" / "security.yml"
    content = workflow.read_text(encoding="utf-8").lower()

    assert "gitleaks" in content
    assert "pull_request" in content
    assert "push" in content
    assert "branches: [main]" in content
    assert "fetch-depth: 0" in content
    assert "gitleaks/gitleaks-action@e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e" in content


def test_external_github_actions_are_pinned_to_full_commit_shas() -> None:
    workflows = (ROOT / ".github" / "workflows").glob("*.yml")
    external_uses: list[tuple[Path, str]] = []
    for workflow in workflows:
        content = workflow.read_text(encoding="utf-8")
        for action in re.findall(r"^\s*-?\s*uses:\s*([^\s#]+)", content, flags=re.MULTILINE):
            if not action.startswith("./"):
                external_uses.append((workflow, action))

    assert external_uses
    for workflow, action in external_uses:
        assert "@" in action, (workflow, action)
        reference = action.rsplit("@", 1)[1]
        assert re.fullmatch(r"[0-9a-f]{40}", reference), (workflow, action)
