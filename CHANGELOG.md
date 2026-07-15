# Changelog

All notable changes to AI Agent Resume Guard will be documented here.

## Unreleased

- Pinned every external GitHub Action to a verified full commit SHA and upgraded checkout and Gitleaks to their current major releases.
- Corrected the public clone directory and documentation URL so the quick start follows the default `main` branch.
- Added a dedicated GitHub Security workflow for automated Gitleaks scanning on pull requests, pushes to `main`, manual dispatches, and weekly scheduled runs.
- Hardened prepublish checks so release readiness fails if the security workflow or required Gitleaks command disappears.
- Added project-file tests that lock release-readiness and security workflow expectations.
- Added CI and Security status badges to README.

## 0.1.0 - Private Incubation

- Added the AI Agent Resume Guard CLI.
- Added safe handoff sanitization.
- Added activity-based session lineage selection.
- Added a local continuity doctor.
- Added policy, session manifest, and adapter export schemas.
- Added the `ai-agent-resume-guard.adapter-export/v1` integration contract.
- Added generic, Hermes-style, and OpenClaw-style adapter fixtures.
- Added CI, package build checks, prepublish checks, and privacy checks.
