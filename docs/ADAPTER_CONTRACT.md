# Adapter Contract

AI Agent Resume Guard now has a preferred integration boundary:

a Hermes, OpenClaw, or custom runtime exports one versioned JSON bundle, and AI Agent Resume Guard ingests it locally.

## Preferred Contract

Current contract:

- `ai-agent-resume-guard.adapter-export/v1`

Minimal shape:

```json
{
  "adapter_contract": "ai-agent-resume-guard.adapter-export/v1",
  "runtime": {
    "kind": "generic",
    "adapter_name": "my-runtime-exporter",
    "adapter_version": "0.1.0"
  },
  "generated_at": "2026-04-26T15:00:00Z",
  "raw_handoff": "**Previous session**: ...",
  "session_manifest": {
    "sessions": [
      {
        "session_id": "root-001",
        "source": "human",
        "started_at": "2026-04-26T14:00:00Z",
        "last_activity_at": "2026-04-26T14:07:00Z"
      }
    ]
  }
}
```

Print the schema locally:

```bash
agent-resume-guard schema --kind adapter-export
```

## Exporter Responsibilities

The runtime adapter should:

1. emit a valid `adapter_contract`;
2. export the session lineage as `session_manifest`;
3. mark operational sessions with a source like `tool` or `cron`;
4. include `raw_handoff` only when there is an actual restart or worker handoff;
5. keep the export free of secrets, local absolute paths, and private notes.

## AI Agent Resume Guard Responsibilities

AI Agent Resume Guard should:

1. validate the bundle shape locally;
2. write a normalized local `session-manifest.json`;
3. sanitize `raw_handoff` into `SAFE_HANDOFF.md`;
4. pick the freshest visible lineage by actual activity;
5. warn when continuity is stale, risky, or polluted by operational noise.

## Why This Boundary Matters

It keeps the runtime-specific code small.

Hermes, OpenClaw, or any other stack only needs a thin exporter.

AI Agent Resume Guard owns the continuity rules.

## Runtime Examples

- generic multi-lineage fixture: [examples/multi-lineage-adapter-export.json](../examples/multi-lineage-adapter-export.json)
- Hermes-style fixture: [examples/hermes-adapter-export.json](../examples/hermes-adapter-export.json)
- OpenClaw-style fixture: [examples/openclaw-adapter-export.json](../examples/openclaw-adapter-export.json)
