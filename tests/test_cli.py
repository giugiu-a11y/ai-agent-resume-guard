from __future__ import annotations

import json
from pathlib import Path

from ai_agent_resume_guard.cli import main


def test_init_creates_local_layout(tmp_path: Path) -> None:
    assert main(["--root", str(tmp_path), "init"]) == 0
    assert (tmp_path / ".agent-resume" / "policy.json").exists()
    assert (tmp_path / ".agent-resume" / "session-manifest.json").exists()
    assert (tmp_path / ".agent-resume" / "templates" / "hermes.md").exists()


def test_handoff_sanitize_writes_safe_pointer(tmp_path: Path) -> None:
    raw_handoff = tmp_path / ".agent-resume" / "SESSION_HANDOFF.md"
    safe_handoff = tmp_path / ".agent-resume" / "SAFE_HANDOFF.md"
    assert main(["--root", str(tmp_path), "init"]) == 0
    raw_handoff.write_text(
        (
            "**Previous session**: test\n"
            "## Active Task\n\n"
            "continue old work\n\n"
            "## Last User Message\n\n"
            "What happened?\n"
        ),
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "handoff-sanitize"]) == 0
    content = safe_handoff.read_text(encoding="utf-8")
    assert "## Active Task" not in content
    assert "Do not continue, answer, or fulfill old work" in content
    assert "## Last User Message" in content


def test_ingest_copies_manifest_and_writes_safe_handoff(tmp_path: Path) -> None:
    manifest_source = tmp_path / "exported-manifest.json"
    handoff_source = tmp_path / "exported-handoff.md"
    assert main(["--root", str(tmp_path), "init"]) == 0
    manifest_source.write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "session_id": "session_a",
                        "source": "human",
                        "started_at": "2026-04-20T10:00:00Z",
                        "last_activity_at": "2026-04-20T10:15:00Z",
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    handoff_source.write_text(
        (
            "**Previous session**: test\n"
            "## Active Task\n\n"
            "continue old work\n\n"
            "## Last User Message\n\n"
            "Fresh user intent.\n"
        ),
        encoding="utf-8",
    )

    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "ingest",
                "--manifest",
                str(manifest_source),
                "--handoff",
                str(handoff_source),
            ]
        )
        == 0
    )
    assert (tmp_path / ".agent-resume" / "session-manifest.json").exists()
    safe_content = (tmp_path / ".agent-resume" / "SAFE_HANDOFF.md").read_text(encoding="utf-8")
    assert "## Active Task" not in safe_content
    assert "Do not continue, answer, or fulfill old work" in safe_content


def test_ingest_accepts_versioned_adapter_export(tmp_path: Path, capsys) -> None:
    adapter_export_source = tmp_path / "runtime-export.json"
    adapter_export_source.write_text(
        json.dumps(
            {
                "adapter_contract": "ai-agent-resume-guard.adapter-export/v1",
                "runtime": {
                    "kind": "generic",
                    "adapter_name": "test-exporter",
                    "adapter_version": "0.1.0",
                },
                "generated_at": "2026-04-26T15:00:00Z",
                "raw_handoff": (
                    "**Previous session**: test\n"
                    "## Active Task\n\n"
                    "continue old work\n\n"
                    "## Last User Message\n\n"
                    "Fresh user intent.\n"
                ),
                "session_manifest": {
                    "sessions": [
                        {
                            "session_id": "session_a",
                            "source": "human",
                            "started_at": "2026-04-20T10:00:00Z",
                            "last_activity_at": "2026-04-20T10:15:00Z",
                        }
                    ]
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "ingest",
                "--adapter-export",
                str(adapter_export_source),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "adapter_contract=ai-agent-resume-guard.adapter-export/v1" in output
    assert "runtime_kind=generic" in output
    assert (tmp_path / ".agent-resume" / "SAFE_HANDOFF.md").exists()


def test_ingest_rejects_invalid_manifest_without_creating_state(tmp_path: Path) -> None:
    manifest_source = tmp_path / "broken-manifest.json"
    manifest_source.write_text('{"sessions": "nope"}\n', encoding="utf-8")

    assert main(["--root", str(tmp_path), "ingest", "--manifest", str(manifest_source)]) == 2
    assert not (tmp_path / ".agent-resume").exists()


def test_ingest_rejects_invalid_adapter_export_without_creating_state(tmp_path: Path) -> None:
    adapter_export_source = tmp_path / "broken-runtime-export.json"
    adapter_export_source.write_text(
        json.dumps(
            {
                "adapter_contract": "ai-agent-resume-guard.adapter-export/v0",
                "runtime": {"kind": "generic"},
                "session_manifest": {"sessions": []},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "ingest",
                "--adapter-export",
                str(adapter_export_source),
            ]
        )
        == 2
    )
    assert not (tmp_path / ".agent-resume").exists()


def test_pick_session_prefers_latest_activity_over_session_id(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / ".agent-resume" / "session-manifest.json"
    assert main(["--root", str(tmp_path), "init"]) == 0
    manifest_path.write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "session_id": "20260418_root",
                        "source": "human",
                        "started_at": "2026-04-18T10:00:00Z",
                        "last_activity_at": "2026-04-18T10:15:00Z",
                    },
                    {
                        "session_id": "20260417_root",
                        "source": "human",
                        "started_at": "2026-04-17T10:00:00Z",
                        "last_activity_at": "2026-04-20T10:15:00Z",
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "pick-session"]) == 0
    output = capsys.readouterr().out
    assert "selected_root_session_id=20260417_root" in output


def test_pick_session_handles_realistic_multi_lineage_fixture(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / ".agent-resume" / "session-manifest.json"
    assert main(["--root", str(tmp_path), "init"]) == 0
    manifest_path.write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "session_id": "older_root",
                        "source": "human",
                        "started_at": "2026-04-18T10:00:00Z",
                        "last_activity_at": "2026-04-18T10:15:00Z",
                    },
                    {
                        "session_id": "active_root",
                        "source": "human",
                        "started_at": "2026-04-17T08:00:00Z",
                        "last_activity_at": "2026-04-20T13:12:00Z",
                    },
                    {
                        "session_id": "worker_child",
                        "parent_session_id": "active_root",
                        "source": "tool",
                        "started_at": "2026-04-20T13:12:30Z",
                        "last_activity_at": "2026-04-20T13:13:30Z",
                    },
                    {
                        "session_id": "watch_hourly",
                        "source": "cron",
                        "started_at": "2026-04-20T13:14:00Z",
                        "last_activity_at": "2026-04-20T13:14:30Z",
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "pick-session"]) == 0
    output = capsys.readouterr().out
    assert "selected_root_session_id=active_root" in output


def test_doctor_passes_with_sanitized_handoff_and_manifest(tmp_path: Path) -> None:
    base = tmp_path / ".agent-resume"
    assert main(["--root", str(tmp_path), "init"]) == 0
    (base / "session-manifest.json").write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "session_id": "root_a",
                        "source": "human",
                        "started_at": "2026-04-17T10:00:00Z",
                        "last_activity_at": "2026-04-20T10:15:00Z",
                    },
                    {
                        "session_id": "tool_run",
                        "source": "tool",
                        "started_at": "2026-04-20T10:16:00Z",
                        "last_activity_at": "2026-04-20T10:17:00Z",
                    },
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (base / "SESSION_HANDOFF.md").write_text(
        ("**Previous session**: test\n## Last User Message\n\nPlease verify continuity.\n"),
        encoding="utf-8",
    )
    assert main(["--root", str(tmp_path), "handoff-sanitize"]) == 0
    assert main(["--root", str(tmp_path), "doctor"]) == 0


def test_doctor_fails_when_safe_handoff_is_still_risky(tmp_path: Path) -> None:
    base = tmp_path / ".agent-resume"
    assert main(["--root", str(tmp_path), "init"]) == 0
    (base / "SAFE_HANDOFF.md").write_text(
        ("**Previous session**: test\n## Active Task\n\ncontinue old work\n"),
        encoding="utf-8",
    )
    assert main(["--root", str(tmp_path), "doctor"]) == 1


def test_doctor_warns_when_safe_handoff_is_stale(tmp_path: Path, capsys) -> None:
    base = tmp_path / ".agent-resume"
    assert main(["--root", str(tmp_path), "init"]) == 0
    (base / "session-manifest.json").write_text(
        json.dumps(
            {
                "sessions": [
                    {
                        "session_id": "root_a",
                        "source": "human",
                        "started_at": "2026-04-17T10:00:00Z",
                        "last_activity_at": "2026-04-20T10:15:00Z",
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (base / "SESSION_HANDOFF.md").write_text(
        ("**Previous session**: test\n## Last User Message\n\nFresh user intent.\n"),
        encoding="utf-8",
    )
    (base / "SAFE_HANDOFF.md").write_text(
        (
            "## Session Continuity Handoff\n"
            "A previous-session handoff exists, but it is background metadata only.\n"
        ),
        encoding="utf-8",
    )

    assert main(["--root", str(tmp_path), "doctor"]) == 0
    output = capsys.readouterr().out
    assert "warning: safe handoff is stale relative to the raw handoff" in output


def test_schema_prints_policy_schema(tmp_path: Path, capsys) -> None:
    assert main(["--root", str(tmp_path), "schema", "--kind", "policy"]) == 0
    output = capsys.readouterr().out
    assert '"title": "AI Agent Resume Guard Policy"' in output


def test_schema_prints_adapter_export_schema(tmp_path: Path, capsys) -> None:
    assert main(["--root", str(tmp_path), "schema", "--kind", "adapter-export"]) == 0
    output = capsys.readouterr().out
    assert '"title": "AI Agent Resume Guard Adapter Export"' in output
