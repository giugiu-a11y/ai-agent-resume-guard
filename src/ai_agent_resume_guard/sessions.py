from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SessionSelection:
    selected_root_session_id: str | None
    selected_session_id: str | None
    selected_last_activity_at: str | None
    visible_lineages: int
    visible_sessions: int
    hidden_sessions: int
    lexicographic_latest_root_session_id: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_root_session_id": self.selected_root_session_id,
            "selected_session_id": self.selected_session_id,
            "selected_last_activity_at": self.selected_last_activity_at,
            "visible_lineages": self.visible_lineages,
            "visible_sessions": self.visible_sessions,
            "hidden_sessions": self.hidden_sessions,
            "lexicographic_latest_root_session_id": self.lexicographic_latest_root_session_id,
        }


def load_manifest(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_manifest_payload(payload)


def validate_manifest_payload(
    payload: object,
    location: str = "session manifest",
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{location} must be a JSON object")
    sessions = payload.get("sessions")
    if not isinstance(sessions, list):
        raise ValueError(f"{location} must contain a sessions list")
    for item in sessions:
        if not isinstance(item, dict):
            raise ValueError(f"each {location} entry must be an object")
        if not isinstance(item.get("session_id"), str) or not item["session_id"].strip():
            raise ValueError(f"each {location} entry must include a non-empty session_id")
        for key in ("parent_session_id", "source", "title", "preview"):
            value = item.get(key)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{location} field {key} must be a non-empty string when present")
        for key in ("started_at", "last_activity_at"):
            value = item.get(key)
            if value is not None and not isinstance(value, (str, int, float)):
                raise ValueError(f"{location} field {key} must be a string or number when present")
    return payload


def choose_session_lineage(
    sessions: list[dict[str, Any]],
    hidden_sources: list[str],
    current_session_id: str | None = None,
    include_hidden_sources: bool = False,
) -> SessionSelection:
    hidden_set = {source.strip() for source in hidden_sources if source.strip()}
    session_map = {item["session_id"]: dict(item) for item in sessions}
    hidden_sessions = 0
    visible_items: list[dict[str, Any]] = []

    for item in session_map.values():
        source = str(item.get("source") or "")
        if not include_hidden_sources and source in hidden_set:
            hidden_sessions += 1
            continue
        visible_items.append(item)

    if not visible_items:
        return SessionSelection(None, None, None, 0, 0, hidden_sessions, None)

    current_root = _root_session_id(current_session_id, session_map) if current_session_id else None
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in visible_items:
        root_id = _root_session_id(item["session_id"], session_map)
        if current_root and root_id == current_root:
            continue
        groups[root_id].append(item)

    if not groups:
        return SessionSelection(None, None, None, 0, len(visible_items), hidden_sessions, None)

    summaries = []
    for root_id, items in groups.items():
        best_session = max(items, key=lambda item: (_session_sort_key(item), item["session_id"]))
        summaries.append(
            (
                root_id,
                best_session["session_id"],
                _session_sort_key(best_session),
                _render_timestamp(best_session),
            )
        )

    selected_root_id, selected_session_id, _, selected_last_activity_at = max(
        summaries,
        key=lambda item: (item[2], item[0]),
    )
    lexicographic_latest_root = max(groups.keys())

    return SessionSelection(
        selected_root_session_id=selected_root_id,
        selected_session_id=selected_session_id,
        selected_last_activity_at=selected_last_activity_at,
        visible_lineages=len(groups),
        visible_sessions=len(visible_items),
        hidden_sessions=hidden_sessions,
        lexicographic_latest_root_session_id=lexicographic_latest_root,
    )


def _root_session_id(session_id: str | None, session_map: dict[str, dict[str, Any]]) -> str:
    if not session_id:
        return ""
    seen: set[str] = set()
    current = session_id
    while current and current not in seen:
        seen.add(current)
        parent = session_map.get(current, {}).get("parent_session_id")
        if isinstance(parent, str) and parent in session_map:
            current = parent
            continue
        return current
    return session_id


def _session_sort_key(item: dict[str, Any]) -> float:
    timestamp = item.get("last_activity_at") or item.get("started_at")
    parsed = _parse_timestamp(timestamp)
    return parsed.timestamp() if parsed else float("-inf")


def _render_timestamp(item: dict[str, Any]) -> str | None:
    value = item.get("last_activity_at") or item.get("started_at")
    if value is None:
        return None
    return str(value)


def _parse_timestamp(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        if cleaned.endswith("Z"):
            cleaned = cleaned[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(cleaned)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None
