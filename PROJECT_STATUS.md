# Project Status

## AI Agent Resume Guard

- Status: public alpha
- Version: `0.1.0`
- Goal: turn safe resume, anti-contamination, and bounded recall into a small public-quality tool
- Audience: Hermes users, OpenClaw-style local agent stacks, and any agent runtime that exports session metadata plus handoffs

## Current Scope

- local CLI scaffold
- versioned adapter export contract
- safe handoff sanitizer
- latest-activity session picker
- continuity doctor
- policy, manifest, and adapter schemas
- realistic adapter export fixtures
- Hermes/OpenClaw integration docs
- release checklist, changelog, and privacy gate
- GitHub Actions CI for the public repo

## Not In Scope Yet

- hosted memory
- provider integrations
- live database adapters
- dashboards
- telemetry
- background sync

## Release Rule

Public releases require:

- the CLI scope is stable;
- docs match behavior;
- local checks pass;
- no private names, local paths, or internal system details remain in public-facing files.
