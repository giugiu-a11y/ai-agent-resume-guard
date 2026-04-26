# Release Checklist

Use this before opening the repository or publishing a package.

## Required Gates

```bash
make prepublish
bash scripts/prepublish_check.sh
bash scripts/privacy_check.sh
gitleaks detect --source . --redact
python -m build
python -m twine check dist/*
```

## Public Surface Review

- README explains the pain clearly in the first screen.
- GitHub description names the category: safe resume and handoff guard for Hermes, OpenClaw, and multi-agent AI systems.
- GitHub topics include `ai-agents`, `multi-agent`, `agent-memory`, `safe-resume`, `handoff`, `hermes`, `openclaw`, `agentops`, `continuity`, and `context-engineering`.
- Launch copy is reviewed in `docs/LAUNCH_COPY.md`.
- Docs match the current CLI behavior.
- Examples are synthetic and do not describe a private system.
- No local absolute paths appear in tracked files or package artifacts.
- No personal emails, secrets, tokens, credentials, or session data appear.
- No private project names, customer names, internal repo names, or private workflows appear.
- Security policy, contribution guide, code of conduct, changelog, and license are present.

## GitHub Release Steps

- Create the GitHub repository as private first.
- Push the local `main` branch.
- Confirm CI passes on GitHub.
- Enable secret scanning and push protection when available.
- Protect `main` with the CI check required.
- Create a signed or clearly authored `v0.1.0` tag.
- Draft release notes from `CHANGELOG.md`.
- Make the repository public only after the public surface review passes.

## Package Release Steps

- Build from a clean working tree.
- Run `twine check` against the generated artifacts.
- Inspect `sdist` and `wheel` contents before upload.
- Publish only after the GitHub release is green.
