# Invariants

Properties the system holds at all times.

- Attempts, attempt claims, self-labels and diagnoses are append-only: no
  record is ever revised or removed in place. Erasing one user's whole log is
  a different act, and `log-records.md` gives how it is taken.
- Every record keyed to an attempt carries an engine-minted `id`, its
  `attempt_id` and `created_at`.
- The user's own record stands over the machine's answer to the same question,
  whichever was written later: a attempt claim resolves user-first, and a
  diagnosis never supersedes a self-label. The machine's record is kept and
  scored, never deleted and never promoted.
- Every reference in an append-only record is engine-minted, so the log stays
  readable without anything outside the engine.
- Aggregates are derived views, never stored truth.
- Every problem is the product's own, written by the engine.
- A problem never lands without the test cases that decide it, a canonical
  solution that passed them, and a reference solution that agreed with the
  canonical on every case.
- The technique vocabulary and the cards are product-owned and global, and no
  user authors a technique or a card.
- Domain logic stays adapter-free and directly callable. The CLI is one
  adapter, the web app is the second, and the native app is the third. A
  sitting and the knowledge module's queues happen in either app, and the
  by-hand passes stay in the terminal.
- The knowledge module's domain in TypeScript lives in `packages/core`, the
  one copy of domain logic outside Python, imported by the web and the native
  app alike. Fixtures generated from the Python side hold the two copies to
  `../core-package/knowledge/`.
- No third-party problem statements or test cases in git, in any repo.
