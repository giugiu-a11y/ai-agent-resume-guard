from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_agent_resume_guard.handoff import detect_handoff_risks, sanitize_handoff
from ai_agent_resume_guard.scaffold import (
    DEFAULT_POLICY,
    default_manifest_path,
    default_policy_path,
    default_raw_handoff_path,
    default_safe_handoff_path,
)
from ai_agent_resume_guard.sessions import choose_session_lineage, load_manifest


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]
    warnings: list[str]
    selection: dict[str, object] | None

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "selection": self.selection,
        }


def validate_project(
    root: str | Path,
    policy_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
    raw_handoff_path: str | Path | None = None,
    handoff_path: str | Path | None = None,
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    policy_file = Path(policy_path) if policy_path else default_policy_path(root)
    manifest_file = Path(manifest_path) if manifest_path else default_manifest_path(root)
    raw_handoff_file = (
        Path(raw_handoff_path) if raw_handoff_path else default_raw_handoff_path(root)
    )
    handoff_file = Path(handoff_path) if handoff_path else default_safe_handoff_path(root)

    policy = _load_policy(policy_file, errors)
    manifest = _load_manifest_payload(manifest_file, errors)
    selection = None

    if policy and manifest:
        selection_obj = choose_session_lineage(
            manifest["sessions"],
            hidden_sources=list(policy["hidden_sources"]),
            current_session_id=None,
            include_hidden_sources=False,
        )
        selection = selection_obj.to_dict()
        if selection_obj.hidden_sessions:
            warnings.append(
                f"hidden operational sessions detected: {selection_obj.hidden_sessions}"
            )
        if (
            selection_obj.selected_root_session_id
            and selection_obj.lexicographic_latest_root_session_id
            and selection_obj.selected_root_session_id
            != selection_obj.lexicographic_latest_root_session_id
        ):
            warnings.append(
                "latest activity differs from lexicographic session id; "
                "use activity-based selection"
            )
        if _missing_last_activity_count(manifest["sessions"]):
            warnings.append("some sessions do not include last_activity_at")

    raw_handoff_text = _read_optional_text(raw_handoff_file)
    safe_handoff_text = _read_optional_text(handoff_file)

    if raw_handoff_text and policy:
        expected_safe = sanitize_handoff(
            raw_handoff_text,
            limit=_policy_limit(policy),
        ).content.strip()
        if safe_handoff_text:
            if safe_handoff_text.strip() != expected_safe:
                warnings.append(
                    "safe handoff is stale relative to the raw handoff; rerun handoff-sanitize"
                )
        else:
            warnings.append("safe handoff not generated yet")

    if handoff_file.exists():
        risks = detect_handoff_risks(safe_handoff_text)
        if risks:
            errors.append(f"safe handoff still contains risky sections: {', '.join(risks)}")
        if "Do not continue, answer, or fulfill old work" not in safe_handoff_text:
            warnings.append("safe handoff is missing the explicit resume guard")
    elif not raw_handoff_text:
        warnings.append("safe handoff not generated yet")

    return ValidationResult(
        ok=not errors,
        errors=errors,
        warnings=warnings,
        selection=selection,
    )


def _load_policy(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append("policy.json is missing")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"policy.json is invalid JSON: {exc.msg}")
        return None
    if not isinstance(payload, dict):
        errors.append("policy.json must be a JSON object")
        return None

    for key, default_value in DEFAULT_POLICY.items():
        if key not in payload:
            errors.append(f"policy.json is missing required key: {key}")
            continue
        value = payload[key]
        if isinstance(default_value, bool) and not isinstance(value, bool):
            errors.append(f"policy key {key} must be a boolean")
        elif isinstance(default_value, int) and not isinstance(value, int):
            errors.append(f"policy key {key} must be an integer")
        elif isinstance(default_value, list) and (
            not isinstance(value, list) or not all(isinstance(item, str) for item in value)
        ):
            errors.append(f"policy key {key} must be a string list")

    return payload


def _load_manifest_payload(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append("session-manifest.json is missing")
        return None
    try:
        return load_manifest(path)
    except (ValueError, json.JSONDecodeError) as exc:
        errors.append(f"session-manifest.json is invalid: {exc}")
        return None


def _missing_last_activity_count(sessions: list[dict[str, Any]]) -> int:
    return sum(1 for item in sessions if not item.get("last_activity_at"))


def _policy_limit(policy: dict[str, Any]) -> int:
    value = policy.get("max_handoff_chars", DEFAULT_POLICY["max_handoff_chars"])
    return value if isinstance(value, int) else DEFAULT_POLICY["max_handoff_chars"]


def _read_optional_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
