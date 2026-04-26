from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_agent_resume_guard.sessions import validate_manifest_payload

ADAPTER_CONTRACT_V1 = "ai-agent-resume-guard.adapter-export/v1"


def load_adapter_export(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_adapter_export_payload(payload)


def validate_adapter_export_payload(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("adapter export must be a JSON object")

    contract = payload.get("adapter_contract")
    if contract != ADAPTER_CONTRACT_V1:
        raise ValueError(f"adapter export must declare adapter_contract={ADAPTER_CONTRACT_V1}")

    runtime = payload.get("runtime")
    if not isinstance(runtime, dict):
        raise ValueError("adapter export must include a runtime object")
    runtime_kind = runtime.get("kind")
    if not isinstance(runtime_kind, str) or not runtime_kind.strip():
        raise ValueError("adapter export runtime.kind must be a non-empty string")

    for key in ("adapter_name", "adapter_version"):
        value = runtime.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"adapter export runtime.{key} must be a non-empty string")

    generated_at = payload.get("generated_at")
    if generated_at is not None and not isinstance(generated_at, str):
        raise ValueError("adapter export generated_at must be a string when present")

    raw_handoff = payload.get("raw_handoff")
    if raw_handoff is not None and (not isinstance(raw_handoff, str) or not raw_handoff.strip()):
        raise ValueError("adapter export raw_handoff must be a non-empty string when present")

    session_manifest = validate_manifest_payload(
        payload.get("session_manifest"),
        location="adapter export session_manifest",
    )

    return {
        "adapter_contract": ADAPTER_CONTRACT_V1,
        "runtime": runtime,
        "generated_at": generated_at,
        "raw_handoff": raw_handoff,
        "session_manifest": session_manifest,
    }
