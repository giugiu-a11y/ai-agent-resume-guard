# Architecture

AI Agent Resume Guard stays deliberately small.

## Core Idea

The tool does not try to become your memory store.

It acts as a continuity safety layer around artifacts you already have:

- a versioned adapter export bundle or equivalent runtime export;
- a handoff file;
- a session manifest export;
- a local continuity policy.

## Local Layout

```text
.agent-resume/
  policy.json
  session-manifest.json
  SESSION_HANDOFF.md
  SAFE_HANDOFF.md
  handoffs/
  templates/
```

## Commands

### `init`

Creates the local layout plus starter templates and policy.

### `handoff-sanitize`

Turns a raw restart handoff into an inert pointer:

- keeps useful metadata;
- keeps the last user message section when present;
- strips active-task style continuity that could hijack a fresh turn.

### `ingest`

Accepts either:

- a versioned adapter export bundle; or
- a session manifest plus an optional raw handoff.

The command normalizes the local continuity artifacts into `.agent-resume/`.

### `pick-session`

Selects the freshest visible session lineage by real latest activity instead of lexicographic session id.

Default hidden sources:

- `tool`
- `cron`

### `doctor`

Checks for:

- missing or invalid policy;
- missing or invalid session manifest;
- stale safe handoffs that no longer match the raw handoff;
- risky handoff sections;
- continuity mismatches where "largest session id" is not the freshest activity;
- hidden-source noise that should stay out of human recall.

## Why This Shape

It is portable.

Any runtime that can emit the adapter contract, or at least export session metadata and produce a handoff file, can use it without buying into a giant new framework.
