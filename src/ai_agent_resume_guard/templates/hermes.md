# AI Agent Resume Guard Rule For Hermes-Style Systems

Before resuming prior work:

1. sanitize the raw handoff;
2. pick the freshest session lineage by real latest activity;
3. do not continue prior work unless the new user message explicitly asked to resume, continue, or inspect it.

Recommended commands:

```bash
agent-resume-guard ingest --adapter-export <exported-runtime-bundle.json>
agent-resume-guard pick-session --format json
agent-resume-guard doctor
```

Recommended local example:

```bash
agent-resume-guard ingest --adapter-export examples/hermes-adapter-export.json
agent-resume-guard doctor
```
