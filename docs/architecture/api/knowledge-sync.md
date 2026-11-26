# Knowledge sync

Both clients read the snapshot and write sync lines through
`packages/core`. The wire keeps some names the store does not use, and the
engine translates them at its edge, so the store keeps this project's names.

- **A client syncs sync lines**: `attempt`, `session`, `status`, `focus`,
  `lesson` and `cert`. Each line carries a `client_id` and names its content
  by slug.
- **Three line kinds are the engine's own**: `setting`, `raise` and `order`.
  The settings, the raise and the module order were kept on the device before
  the engine synced them, so format 6 has no line for any of the three.
- **A `setting` line carries the name and the value**, as `name` and `n`.
- **An `order` line names every module by slug, as `courses`.** A line naming
  a module the store does not hold is refused, as any line naming unknown
  content is.
- **Four names change at the edge.** The wire's `card` format is stored as
  an open question, and its `drill` queue as the filtered queue. Its
  `exam-L<n>` session is stored as an `exam` stint at level `n`. Its
  `cert-<id>` session is stored as an `exam` stint at the certification's
  level, naming the certification. A line read
  back carries the wire's names again.
- **A test's lines carry its topic.** A `session` line whose mode is
  `baseline` or `delayed` names its `course`, its `topic` and its `level`. A
  `session` line whose mode is `placement` names its `course` and its
  `topic`. An `attempt` line given in a test carries its `measure`.
- **A line naming content the store does not hold is refused alone.** The
  rest of the upload is stored, and the reply names each refused line.
- **A sync returns the user's records since a cursor**, one append order per
  table. A client merges them into its copy by `client_id`.
