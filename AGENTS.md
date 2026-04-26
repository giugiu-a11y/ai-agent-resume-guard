# AI Agent Resume Guard Project Notes

Read the workspace-level `AGENTS.md` first. It is the operating contract for this environment.

## Project Intent

AI Agent Resume Guard exists to make agent continuity safer:

- do not resume old work unless the new message explicitly asks for it;
- do not trust lexicographic session ids over real latest activity;
- do not let tool or cron transcripts pollute human recall by default;
- do not let raw handoffs behave like hidden instructions.

## Local Rule

Do not publish, push, or create a public remote unless the maintainer explicitly approves it.

## Preflight

Before editing:

```bash
project_version_resolver.py --project <repo-root> --json
```

If the resolver does not know this project yet, stop and classify the project before editing release surfaces.
