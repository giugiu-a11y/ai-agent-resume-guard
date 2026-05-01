# AI Agent Resume Guard For Hermes, OpenClaw, And Multi-Agent Runtimes

[![CI](https://github.com/giugiu-a11y/ai-agent-resume-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/giugiu-a11y/ai-agent-resume-guard/actions/workflows/ci.yml)
[![Security](https://github.com/giugiu-a11y/ai-agent-resume-guard/actions/workflows/security.yml/badge.svg)](https://github.com/giugiu-a11y/ai-agent-resume-guard/actions/workflows/security.yml)
[![CodeQL](https://github.com/giugiu-a11y/ai-agent-resume-guard/actions/workflows/codeql.yml/badge.svg)](https://github.com/giugiu-a11y/ai-agent-resume-guard/actions/workflows/codeql.yml)

Stop AI agents from resuming stale work, trusting unsafe handoffs, or picking the wrong session after restarts.

AI Agent Resume Guard is a local safe-resume layer for Hermes-style orchestrators, OpenClaw-style local agent stacks, and any AI agent runtime that restarts, compacts, delegates, or resumes work across long threads.

It exists for one ugly failure:

an agent remembers the wrong thing, resumes the wrong work, or drags stale context into a fresh thread.

## The Problem

Agent systems often fail long before they fail on raw intelligence.

They fail because continuity is sloppy:

- a restart handoff gets injected like live instructions;
- the agent resumes old work even though the new message never asked for it;
- "newest session id" is not the same as most recent real activity;
- tool logs and cron transcripts pollute human recall;
- summarization stalls, returns empty, or quietly distorts the useful context.

That is not a memory feature problem.

It is a continuity safety problem.

## Who It Is For

- Hermes users who need restart handoffs to stay inert until the next task really asks to resume.
- OpenClaw users running local planners, workers, routes, or cron-driven agent loops.
- Codex, Claude Code, Cursor, OpenCode, Aider, Cline, or custom agent setups that pass work between sessions.
- Teams that need agent memory and recall without letting stale context hijack fresh work.

## What AI Agent Resume Guard Does

AI Agent Resume Guard gives you a small local toolkit to make continuity safer:

- sanitize raw handoffs into inert resume pointers;
- select the freshest session lineage by real latest activity;
- exclude operational noise like `tool` and `cron` from default human recall;
- detect risky handoffs and continuity drift with a local `doctor`;
- warn when the sanitized handoff is stale relative to the raw handoff;
- document a continuity policy that is inspectable and portable.

## What You Get

- a Python CLI with zero hosted dependencies;
- a default policy for safe resume and bounded recall;
- a manifest format for exported session metadata;
- a versioned adapter export contract for runtime integrations;
- integration templates for Hermes, OpenClaw, and other multi-agent systems;
- a doctor command that flags continuity risks before they become hallucinations.

## Current Status

AI Agent Resume Guard is a focused `0.1.0` public alpha.

The current goal is not breadth. It is a sharp, reviewable first cut around the real pain.

## Quick Start

Requires Python 3.10+.

```bash
cd agent-resume-guard
python3 -m pip install -e ".[dev]"
agent-resume-guard init
agent-resume-guard ingest --adapter-export examples/multi-lineage-adapter-export.json
agent-resume-guard pick-session --format json
agent-resume-guard doctor
```

## Commands

```bash
agent-resume-guard init
agent-resume-guard ingest --adapter-export path/to/runtime-export.json
agent-resume-guard ingest --manifest path/to/session-manifest.json
agent-resume-guard handoff-sanitize
agent-resume-guard pick-session
agent-resume-guard doctor
agent-resume-guard schema --kind policy
agent-resume-guard schema --kind session-manifest
agent-resume-guard schema --kind adapter-export
```

## Why This Fits With DoneProof And Multi-Agent Memory Isolation

- DoneProof: prove the work was actually done.
- Multi-Agent Memory Isolation: separate private notes from shared memory.
- AI Agent Resume Guard: make continuity and recall safe before the next turn starts.

They solve different failure modes in the same multi-agent reality.

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Adapter Contract](docs/ADAPTER_CONTRACT.md)
- [Integrations](docs/INTEGRATIONS.md)
- [Field Lessons](docs/FIELD_LESSONS.md)
- [Launch Copy](docs/LAUNCH_COPY.md)
- [Release Checklist](docs/RELEASE_CHECKLIST.md)
- [Roadmap](ROADMAP.md)
- [Support](SUPPORT.md)
