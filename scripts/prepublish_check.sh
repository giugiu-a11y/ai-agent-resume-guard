#!/usr/bin/env bash
set -euo pipefail

choose_python_bin() {
  local candidate
  for candidate in "${PYTHON_BIN:-}" python python3 python3.12 python3.11 python3.10; do
    if [[ -n "${candidate}" ]] && command -v "${candidate}" >/dev/null 2>&1; then
      if "${candidate}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
        command -v "${candidate}"
        return 0
      fi
    fi
  done
  return 1
}

PYTHON_BIN="$(choose_python_bin)"
UV_BIN="$(command -v uv || true)"
TMP_ROOT="$(mktemp -d /tmp/agent-resume-guard-prepublish.XXXXXX)"

run_ruff() {
  if [[ -n "${UV_BIN}" ]]; then
    "${UV_BIN}" run --extra dev --python "${PYTHON_BIN}" ruff check .
    "${UV_BIN}" run --extra dev --python "${PYTHON_BIN}" ruff format --check .
  else
    "${PYTHON_BIN}" -m ruff check .
    "${PYTHON_BIN}" -m ruff format --check .
  fi
}

run_pytest() {
  if [[ -n "${UV_BIN}" ]]; then
    "${UV_BIN}" run --extra dev --python "${PYTHON_BIN}" pytest
  else
    "${PYTHON_BIN}" -m pytest
  fi
}

run_python() {
  if [[ -n "${UV_BIN}" ]]; then
    "${UV_BIN}" run --extra dev --python "${PYTHON_BIN}" python "$@"
  else
    "${PYTHON_BIN}" "$@"
  fi
}

run_agent_resume_guard() {
  if [[ -n "${UV_BIN}" ]]; then
    "${UV_BIN}" run --extra dev --python "${PYTHON_BIN}" agent-resume-guard "$@"
  else
    "${PYTHON_BIN}" -m ai_agent_resume_guard "$@"
  fi
}

run_ruff
run_pytest
run_python -m compileall -q src tests
./scripts/privacy_check.sh
run_agent_resume_guard --version
run_agent_resume_guard --root "${TMP_ROOT}" init --force
run_agent_resume_guard --root "${TMP_ROOT}" ingest --adapter-export examples/multi-lineage-adapter-export.json
run_agent_resume_guard --root "${TMP_ROOT}" pick-session --format json >/tmp/agent-resume-guard-prepublish-selection.json
run_agent_resume_guard --root "${TMP_ROOT}" doctor
run_python -m build
run_python -m twine check dist/*

echo "AI Agent Resume Guard prepublish checks passed."
