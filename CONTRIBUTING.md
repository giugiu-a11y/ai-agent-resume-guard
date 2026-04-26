# Contributing

Thanks for helping improve AI Agent Resume Guard.

## Local Setup

```bash
python3 -m pip install -e ".[dev]"
make prepublish
```

## Pull Request Standard

Before opening a PR:

- explain the continuity failure or safety gap;
- keep the change small;
- add or update tests;
- update docs when behavior changes;
- run `make prepublish`;
- do not include secrets, personal data, private paths, or internal project details.

## Design Standard

AI Agent Resume Guard should stay small.

Prefer:

- local files;
- inspectable manifests;
- deterministic checks;
- continuity rules that can be audited;
- adapters that do not assume one runtime owns every environment.

Avoid:

- hosted dependencies by default;
- telemetry;
- hidden state;
- memory features that silently reintroduce contamination;
- broad claims that AI Agent Resume Guard can solve every agent memory problem.
