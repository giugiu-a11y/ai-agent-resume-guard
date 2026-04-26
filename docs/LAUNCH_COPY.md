# AI Agent Resume Guard Messaging Notes

Use this when publishing the repository, writing release notes, posting on social platforms, or replying to early users.

## Core Position

AI Agent Resume Guard is for people running AI agents that restart, compact, hand off, or resume work across long sessions.

It prevents the next run from trusting stale handoffs, picking the wrong session, or letting tool and cron transcripts dominate human recall.

## GitHub Description

```text
Safe resume and handoff guard for Hermes, OpenClaw, and multi-agent AI systems, so agents do not continue stale work.
```

## GitHub Topics

```text
ai-agents, multi-agent, agent-memory, safe-resume, handoff, hermes, openclaw, agentops, continuity, context-engineering
```

## Main Hook

```text
The dangerous part of agent memory is not forgetting. It is resuming the wrong thing with confidence.
```

## Short Launch Post

```text
If you run Hermes, OpenClaw, or any multi-agent AI setup, watch for this:

the agent resumes stale work because an old handoff still sounds true.

AI Agent Resume Guard is a small local guard for that.
It keeps raw handoffs inert, picks sessions by real activity, and warns before dirty continuity becomes the next task.
```

## Recommendation-Style Post

```text
Most agent failures I care about now are not "the model is dumb."

They are stale handoffs, wrong session resumes, and tool logs getting treated like human context.

AI Agent Resume Guard is a useful local guard for that, especially in Hermes/OpenClaw-style agent stacks.
```

## Release Blurb

```text
AI Agent Resume Guard v0.1.0 adds a local safe-resume guard for multi-agent systems: handoff sanitization, real-activity session selection, hidden-source filtering, continuity doctor checks, and adapter fixtures for Hermes-style and OpenClaw-style runtimes.
```

## Tone Rules

- Lead with stale resume and dirty continuity, not generic AI memory.
- Say Hermes and OpenClaw for discovery, but avoid implying official endorsement.
- Keep the claim concrete: safer handoffs, session selection, and continuity checks.
- Avoid promising correctness, truth, or hallucination prevention.
