from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from importlib import resources
from pathlib import Path
from typing import Any

from ai_agent_resume_guard import __version__
from ai_agent_resume_guard.adapter_exports import load_adapter_export
from ai_agent_resume_guard.handoff import sanitize_handoff
from ai_agent_resume_guard.scaffold import (
    base_dir,
    default_manifest_path,
    default_policy_path,
    default_raw_handoff_path,
    default_safe_handoff_path,
    init_project,
)
from ai_agent_resume_guard.sessions import choose_session_lineage, load_manifest
from ai_agent_resume_guard.validation import validate_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-resume-guard",
        description="Safe resume and handoff guard for multi-agent AI systems.",
    )
    parser.add_argument("--version", action="version", version=f"agent-resume-guard {__version__}")
    parser.add_argument(
        "--root",
        default=".",
        help="Project root. Defaults to the current directory.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create local AI Agent Resume Guard storage.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite starter files.")

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest an exported manifest and raw handoff into .agent-resume.",
    )
    ingest_source = ingest_parser.add_mutually_exclusive_group(required=True)
    ingest_source.add_argument("--manifest", help="Exported session manifest path.")
    ingest_source.add_argument(
        "--adapter-export",
        help="Versioned runtime export bundle path.",
    )
    ingest_parser.add_argument("--handoff", help="Exported raw handoff path.")
    ingest_parser.add_argument("--format", choices=["text", "json"], default="text")

    sanitize_parser = subparsers.add_parser(
        "handoff-sanitize",
        help="Turn a raw handoff into a safe continuity pointer.",
    )
    sanitize_parser.add_argument("--input", help="Raw handoff input path.")
    sanitize_parser.add_argument("--output", help="Safe handoff output path.")
    sanitize_parser.add_argument("--limit", type=int, help="Maximum output length.")
    sanitize_parser.add_argument("--format", choices=["text", "json"], default="text")

    pick_parser = subparsers.add_parser(
        "pick-session",
        help="Choose the freshest session lineage by real latest activity.",
    )
    pick_parser.add_argument("--manifest", help="Session manifest path.")
    pick_parser.add_argument("--current-session-id")
    pick_parser.add_argument("--include-hidden-sources", action="store_true")
    pick_parser.add_argument("--format", choices=["text", "json"], default="text")

    doctor_parser = subparsers.add_parser("doctor", help="Check continuity hygiene.")
    doctor_parser.add_argument("--policy", help="Policy path.")
    doctor_parser.add_argument("--manifest", help="Session manifest path.")
    doctor_parser.add_argument("--raw-handoff", help="Raw handoff path.")
    doctor_parser.add_argument("--handoff", help="Safe handoff path.")
    doctor_parser.add_argument("--format", choices=["text", "json"], default="text")

    schema_parser = subparsers.add_parser("schema", help="Print a AI Agent Resume Guard schema.")
    schema_parser.add_argument(
        "--kind",
        choices=["policy", "session-manifest", "adapter-export"],
        default="policy",
    )
    schema_parser.add_argument("--output", help="Write schema to a file.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    try:
        if args.command == "init":
            created = init_project(root, force=args.force)
            print(f"AI Agent Resume Guard initialized at {display_path(base_dir(root), root)}")
            print(f"created_or_verified={len(created)}")
            return 0

        if args.command == "ingest":
            adapter_payload: dict[str, Any] | None = None
            raw_handoff_text: str | None = None
            if args.adapter_export:
                if args.handoff:
                    raise ValueError(
                        "ingest does not accept --handoff together with --adapter-export"
                    )
                adapter_payload = load_adapter_export(Path(args.adapter_export))
                manifest_payload = adapter_payload["session_manifest"]
                raw_handoff_text = adapter_payload.get("raw_handoff")
            else:
                source_manifest_path = Path(args.manifest)
                manifest_payload = load_manifest(source_manifest_path)
                if args.handoff:
                    source_handoff_path = Path(args.handoff)
                    raw_handoff_text = source_handoff_path.read_text(encoding="utf-8")

            sanitized = None

            if raw_handoff_text is not None:
                sanitized = sanitize_handoff(
                    raw_handoff_text,
                    limit=_policy_limit(default_policy_path(root)),
                )

            init_project(root, force=False)
            target_manifest_path = default_manifest_path(root)
            target_manifest_path.write_text(
                json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            payload: dict[str, object] = {
                "manifest": display_path(target_manifest_path, root),
                "session_count": len(manifest_payload["sessions"]),
            }
            if args.adapter_export and adapter_payload:
                runtime = adapter_payload["runtime"]
                payload.update(
                    {
                        "adapter_contract": adapter_payload["adapter_contract"],
                        "runtime_kind": runtime["kind"],
                    }
                )
                adapter_name = runtime.get("adapter_name")
                if adapter_name:
                    payload["adapter_name"] = adapter_name

            if raw_handoff_text is not None and sanitized is not None:
                target_raw_handoff_path = default_raw_handoff_path(root)
                target_safe_handoff_path = default_safe_handoff_path(root)
                target_raw_handoff_path.write_text(raw_handoff_text, encoding="utf-8")
                target_safe_handoff_path.write_text(sanitized.content + "\n", encoding="utf-8")
                payload.update(
                    {
                        "raw_handoff": display_path(target_raw_handoff_path, root),
                        "safe_handoff": display_path(target_safe_handoff_path, root),
                        "handoff_risk_count": len(sanitized.risks),
                    }
                )

            emit_payload(
                payload,
                args.format,
                _ingest_text(payload),
            )
            return 0

        if args.command == "handoff-sanitize":
            input_path = Path(args.input) if args.input else default_raw_handoff_path(root)
            output_path = Path(args.output) if args.output else default_safe_handoff_path(root)
            policy_path = default_policy_path(root)
            limit = args.limit or _policy_limit(policy_path)
            raw_text = input_path.read_text(encoding="utf-8")
            sanitized = sanitize_handoff(raw_text, limit=limit)
            output_path.write_text(sanitized.content + "\n", encoding="utf-8")
            payload = {
                "input": display_path(input_path, root),
                "output": display_path(output_path, root),
                "risk_count": len(sanitized.risks),
                "risks": sanitized.risks,
            }
            emit_payload(
                payload,
                args.format,
                f"safe handoff written: {payload['output']}",
            )
            return 0

        if args.command == "pick-session":
            manifest_path = Path(args.manifest) if args.manifest else default_manifest_path(root)
            policy = _load_policy_or_default(default_policy_path(root))
            payload = load_manifest(manifest_path)
            selection = choose_session_lineage(
                payload["sessions"],
                hidden_sources=list(policy["hidden_sources"]),
                current_session_id=args.current_session_id,
                include_hidden_sources=args.include_hidden_sources,
            ).to_dict()
            emit_payload(
                selection,
                args.format,
                _selection_text(selection),
            )
            return 0 if selection["selected_root_session_id"] else 1

        if args.command == "doctor":
            result = validate_project(
                root=root,
                policy_path=args.policy,
                manifest_path=args.manifest,
                raw_handoff_path=args.raw_handoff,
                handoff_path=args.handoff,
            )
            payload = {
                "root": ".",
                "context_dir": display_path(base_dir(root), root),
                **result.to_dict(),
            }
            if args.format == "json":
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(
                    "AI Agent Resume Guard doctor: PASS"
                    if result.ok
                    else "AI Agent Resume Guard doctor: FAIL"
                )
                if result.selection:
                    print(
                        f"selected_root_session_id={result.selection['selected_root_session_id']}"
                    )
                for warning in result.warnings:
                    print(f"warning: {warning}")
                for error in result.errors:
                    print(f"error: {error}")
            return 0 if result.ok else 1

        if args.command == "schema":
            content = schema_text(args.kind)
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(content, encoding="utf-8")
                print(f"schema written: {display_path(output_path, root)}")
            else:
                print(content)
            return 0

    except Exception as exc:
        print(f"error: {safe_error_message(exc, root)}", file=sys.stderr)
        return 2

    parser.error("unknown command")
    return 2


def emit_payload(payload: dict[str, object], fmt: str, text: str) -> None:
    if fmt == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(text)


def schema_text(kind: str) -> str:
    name_by_kind = {
        "policy": "policy.schema.json",
        "session-manifest": "session-manifest.schema.json",
        "adapter-export": "adapter-export.schema.json",
    }
    name = name_by_kind[kind]
    return (
        resources.files("ai_agent_resume_guard")
        .joinpath("schemas", name)
        .read_text(encoding="utf-8")
    )


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        if path.is_absolute():
            return path.name
        return str(path)


def safe_error_message(exc: Exception, root: Path) -> str:
    message = str(exc)
    root_text = str(root)
    return message.replace(f"{root_text}/", "").replace(root_text, ".")


def _load_policy_or_default(path: Path) -> dict[str, object]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "hidden_sources": ["tool", "cron"],
        "max_handoff_chars": 1200,
    }


def _policy_limit(path: Path) -> int:
    payload = _load_policy_or_default(path)
    value = payload.get("max_handoff_chars", 1200)
    return value if isinstance(value, int) else 1200


def _selection_text(payload: dict[str, object]) -> str:
    selected_root = payload.get("selected_root_session_id")
    if not selected_root:
        return "no visible session lineage found"
    return (
        f"selected_root_session_id={selected_root}\n"
        f"selected_session_id={payload.get('selected_session_id')}\n"
        f"selected_last_activity_at={payload.get('selected_last_activity_at')}"
    )


def _ingest_text(payload: dict[str, object]) -> str:
    lines = [
        f"manifest ingested: {payload['manifest']}",
        f"session_count={payload['session_count']}",
    ]
    if "adapter_contract" in payload:
        lines.append(f"adapter_contract={payload['adapter_contract']}")
    if "runtime_kind" in payload:
        lines.append(f"runtime_kind={payload['runtime_kind']}")
    if "adapter_name" in payload:
        lines.append(f"adapter_name={payload['adapter_name']}")
    if "raw_handoff" in payload and "safe_handoff" in payload:
        lines.append(f"raw_handoff={payload['raw_handoff']}")
        lines.append(f"safe_handoff={payload['safe_handoff']}")
        lines.append(f"handoff_risk_count={payload['handoff_risk_count']}")
    return "\n".join(lines)
