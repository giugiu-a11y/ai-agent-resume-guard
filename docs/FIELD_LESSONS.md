# Field Lessons

AI Agent Resume Guard comes from the kinds of continuity failures that are easy to wave away as "the model hallucinated".

The expensive reality is usually more mechanical.

## Lesson 1

Raw handoff text is dangerous when injected as if it were live intent.

The safe default is:

- a previous handoff exists;
- it is background metadata only;
- the new turn may inspect it only when the new user message explicitly asks to resume or inspect prior work.

## Lesson 2

The biggest session id is not always the freshest conversation.

Long-lived threads, child sessions, and restarts make lexicographic ordering a trap.

## Lesson 3

Operational transcripts should not dominate human recall.

Tool runs and cron jobs matter for debugging, but they should not crowd the default memory surface for normal conversation continuity.

## Lesson 4

Timeouts in summarization should degrade to raw preview, not to silence.

An empty summary often hurts more than a short imperfect preview.

## Lesson 5

Continuity rules are part of system safety, not just UX polish.

When continuity is dirty, the agent feels deceptive even when the base model is fine.
