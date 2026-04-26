# AI Agent Resume Guard Rule For OpenClaw-Style Local Agent Stacks

Before worker continuation:

1. export a session manifest;
2. keep operational transcripts marked as `tool` or `cron`;
3. sanitize the raw handoff;
4. use activity-based lineage selection instead of session-id ordering.

Recommended commands:

```bash
agent-resume-guard ingest --adapter-export <exported-runtime-bundle.json>
agent-resume-guard pick-session --format json
agent-resume-guard doctor
```

Recommended local example:

```bash
agent-resume-guard ingest --adapter-export examples/openclaw-adapter-export.json
agent-resume-guard pick-session --format json
agent-resume-guard doctor
```
