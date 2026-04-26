from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

DEFAULT_POLICY = {
    "explicit_resume_required": True,
    "hidden_sources": ["tool", "cron"],
    "prefer_latest_activity": True,
    "max_handoff_chars": 1200,
    "summary_timeout_seconds": 12,
    "summary_total_timeout_seconds": 14,
    "summary_budget_seconds": 16,
}


def base_dir(root: str | Path) -> Path:
    return Path(root).resolve() / ".agent-resume"


def default_policy_path(root: str | Path) -> Path:
    return base_dir(root) / "policy.json"


def default_manifest_path(root: str | Path) -> Path:
    return base_dir(root) / "session-manifest.json"


def default_raw_handoff_path(root: str | Path) -> Path:
    return base_dir(root) / "SESSION_HANDOFF.md"


def default_safe_handoff_path(root: str | Path) -> Path:
    return base_dir(root) / "SAFE_HANDOFF.md"


def init_project(root: str | Path, force: bool = False) -> list[Path]:
    base = base_dir(root)
    templates_dir = base / "templates"
    handoffs_dir = base / "handoffs"
    created: list[Path] = []

    for directory in (base, templates_dir, handoffs_dir):
        directory.mkdir(parents=True, exist_ok=True)
        created.append(directory)

    created.extend(_write_json_file(default_policy_path(root), DEFAULT_POLICY, force=force))
    created.extend(_write_json_file(default_manifest_path(root), {"sessions": []}, force=force))
    created.extend(
        _write_text_file(
            default_raw_handoff_path(root),
            "",
            force=force,
        )
    )

    for name in ("hermes.md", "openclaw.md"):
        template_text = (
            resources.files("ai_agent_resume_guard")
            .joinpath("templates", name)
            .read_text(encoding="utf-8")
        )
        created.extend(_write_text_file(templates_dir / name, template_text, force=force))

    return created


def _write_json_file(path: Path, payload: dict[str, object], force: bool) -> list[Path]:
    if path.exists() and not force:
        return [path]
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return [path]


def _write_text_file(path: Path, content: str, force: bool) -> list[Path]:
    if path.exists() and not force:
        return [path]
    path.write_text(content, encoding="utf-8")
    return [path]
