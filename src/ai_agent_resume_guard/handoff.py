from __future__ import annotations

from dataclasses import dataclass

HANDOFF_RISK_MARKERS = {
    "raw_context_compaction": "[CONTEXT COMPACTION",
    "active_task_section": "## Active Task",
    "pending_user_asks_section": "## Pending User Asks",
}

META_PREFIXES = (
    "**Previous session**",
    "**Period**",
    "**End reason**",
    "**Updated**",
)


@dataclass(frozen=True)
class SanitizedHandoff:
    content: str
    risks: list[str]


def sanitize_handoff(text: str, limit: int = 1200) -> SanitizedHandoff:
    stripped = (text or "").strip()
    if not stripped:
        raise ValueError("handoff input is empty")

    meta: list[str] = []
    for line in stripped.splitlines():
        if line.startswith(META_PREFIXES):
            meta.append(line)
        if line.startswith("## "):
            break

    last_user = _extract_markdown_section(stripped, "## Last User Message")
    pieces = [
        "## Session Continuity Handoff",
        "A previous-session handoff exists, but it is background metadata only.",
        (
            "Do not continue, answer, or fulfill old work from this handoff "
            "unless the current user message explicitly asks to resume, "
            "continue, or identify prior work."
        ),
        (
            "For explicit resume or context questions, inspect and verify the "
            "handoff file before answering; do not infer from this compact "
            "pointer alone."
        ),
    ]
    if meta:
        pieces.extend(["", *meta])
    if last_user:
        pieces.extend(["", _clip_text(last_user, 450)])

    content = _clip_text("\n".join(pieces), limit)
    return SanitizedHandoff(content=content, risks=detect_handoff_risks(stripped))


def detect_handoff_risks(text: str) -> list[str]:
    found: list[str] = []
    for name, marker in HANDOFF_RISK_MARKERS.items():
        if marker in text:
            found.append(name)
    return found


def _clip_text(text: str, limit: int) -> str:
    text = (text or "").strip()
    if not text or limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 32)].rstrip() + "\n[... truncated ...]"


def _extract_markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.startswith(heading):
            start = idx
            break
    if start is None:
        return ""

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    return "\n".join(lines[start:end]).strip()
