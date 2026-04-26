# Integrations

AI Agent Resume Guard is runtime-agnostic by design.

It is meant for Hermes-style orchestrators, OpenClaw-style local agent stacks, and any multi-agent runtime that can export session metadata plus an optional restart handoff.

## Preferred Integration Boundary

Preferred flow:

1. export one versioned adapter bundle;
2. keep runtime-specific logic inside the exporter;
3. let AI Agent Resume Guard own continuity validation, sanitization, and lineage selection.

```bash
agent-resume-guard ingest --adapter-export <runtime-export.json>
agent-resume-guard pick-session --format json
agent-resume-guard doctor
```

Use `agent-resume-guard schema --kind adapter-export` to print the current contract.

## Hermes-Style Systems

Recommended flow:

1. export one `ai-agent-resume-guard.adapter-export/v1` bundle;
2. include the raw restart handoff only when there is an actual handoff to inspect;
3. run:

```bash
agent-resume-guard ingest --adapter-export <exported-runtime-bundle.json>
agent-resume-guard pick-session --format json
agent-resume-guard doctor
```

Use the sanitized handoff as the continuity pointer for fresh turns.

Do not inject the raw handoff as active instructions unless the user explicitly asked to resume prior work.

Example export shape:

```json
{
  "sessions": [
    {
      "session_id": "topic-root-001",
      "source": "human",
      "started_at": "2026-04-20T13:00:00Z",
      "last_activity_at": "2026-04-20T13:14:00Z",
      "title": "Main topic thread",
      "preview": "User asks why the agent resumed stale work"
    },
    {
      "session_id": "topic-child-002",
      "parent_session_id": "topic-root-001",
      "source": "human",
      "started_at": "2026-04-20T13:01:00Z",
      "last_activity_at": "2026-04-20T13:03:00Z",
      "title": "Short child branch",
      "preview": "Old detached branch"
    }
  ]
}
```

What AI Agent Resume Guard should enforce here:

- prefer `last_activity_at` over session-id ordering;
- keep raw continuity inert unless the new user message explicitly asks to resume;
- flag a stale `SAFE_HANDOFF.md` when the raw handoff changed after sanitization.

Useful local rehearsal:

```bash
agent-resume-guard ingest --adapter-export examples/hermes-adapter-export.json
agent-resume-guard doctor
```

## OpenClaw-Style Local Agent Stacks

Recommended flow:

1. export one bundle per route, planner, or worker family;
2. mark operational transcripts with a source like `tool` or `cron`;
3. let AI Agent Resume Guard filter those out of default human recall;
4. use `doctor` before long resumptions or worker handoffs.

Example worker manifest:

```json
{
  "sessions": [
    {
      "session_id": "planner-route-a",
      "source": "human",
      "started_at": "2026-04-20T12:00:00Z",
      "last_activity_at": "2026-04-20T12:05:00Z",
      "title": "Planner route"
    },
    {
      "session_id": "worker-build-1",
      "source": "tool",
      "started_at": "2026-04-20T12:06:00Z",
      "last_activity_at": "2026-04-20T12:16:00Z",
      "title": "Build worker transcript"
    },
    {
      "session_id": "watch-hourly-9",
      "source": "cron",
      "started_at": "2026-04-20T12:20:00Z",
      "last_activity_at": "2026-04-20T12:21:00Z",
      "title": "Watch job"
    }
  ]
}
```

What AI Agent Resume Guard should enforce here:

- `tool` and `cron` remain hidden from default human recall;
- only real human continuity should dominate default session selection;
- the worker handoff used for continuation should be the sanitized one, not the raw task dump.

Useful local rehearsal:

```bash
agent-resume-guard ingest --adapter-export examples/openclaw-adapter-export.json
agent-resume-guard pick-session --format json
agent-resume-guard doctor
```

## Fallback For Thin Exporters

If a runtime cannot emit the full bundle yet, AI Agent Resume Guard still accepts:

```bash
agent-resume-guard ingest --manifest <exported-manifest.json> --handoff <exported-handoff.md>
```

That fallback is useful during adoption, but the versioned bundle is the cleaner long-term boundary.

## Pairing With Multi-Agent Memory Isolation

Use AI Agent Resume Guard before the turn starts.

Use Multi-Agent Memory Isolation for shared memory during and after the turn.

```bash
agent-resume-guard doctor
agent-memory-isolation handoff --agent codex --task "<task>"
```

## Pairing With DoneProof

Use AI Agent Resume Guard to prevent dirty continuity.

Use DoneProof to prevent fake completion.

```bash
agent-resume-guard doctor
doneproof check
```

## Suggested Order In Real Agent Runs

For systems that use all three layers:

```bash
agent-resume-guard doctor
agent-memory-isolation handoff --agent <agent-name> --task "<task>"
doneproof check
```

That order keeps continuity clean before memory sharing starts, and keeps proof separate from continuity.
