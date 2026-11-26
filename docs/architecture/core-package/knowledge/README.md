# Knowledge rules

The rules a client applies to the knowledge modules: the schedule that spaces
the questions, the gates that open them, the queues that serve them, and what a
client keeps on the device. `packages/core` holds them in TypeScript, and both
clients import that package.

The rules were learn's, a personal study app merged into the engine on
2026-11-10. learn's native app became the engine's client. The server holds
FSRS replay and the question states in Python too. Shared fixtures hold
`packages/core` and the server to these files.

| File | Holds |
|---|---|
| [`schedule.md`](schedule.md) | FSRS replay, the ratings, the question states |
| [`gating.md`](gating.md) | Levels, the prerequisite graph, the frontier |
| [`queues.md`](queues.md) | The queues, the daily limit, settings, the focus, module status and order |
| [`certifications.md`](certifications.md) | Certifications and exams |
| [`baseline-tests.md`](baseline-tests.md) | The baseline and the delayed tests |
| [`placement.md`](placement.md) | Placing the groups a user already holds, highest level first |
| [`projections.md`](projections.md) | The review forecast and when the focus is reached |
| [`store.md`](store.md) | A client's copy of the content and the log, and its outbox |
