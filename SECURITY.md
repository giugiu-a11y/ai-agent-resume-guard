# Security Policy

## Supported Versions

Security fixes target the latest released version.

## Reporting a Vulnerability

Once the repository is public, report vulnerabilities through a private GitHub security advisory.

Do not include live secrets or private data in public issues.

## Scope

Security-sensitive areas include:

- unsafe parsing of session manifests or handoff files;
- path traversal in output locations;
- accidental inclusion of personal data in sanitized handoffs;
- continuity rules that allow hidden instructions back into a fresh turn;
- CI or release workflow changes.

## Local Checks

```bash
agent-resume-guard doctor
bash scripts/privacy_check.sh
gitleaks detect --source . --redact
```
