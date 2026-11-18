# Trials

A trial is one panel member's solution to one problem, with its verdict. A
difficulty fit reads the trials.

- **A `Trial` stores one member's solution to one problem and its verdict.**
  It carries an engine-minted `id`, the `problem_id`, the `try_number`, the
  `outcome`, `cases_passed`, `cases_run`, the `cap_ms` and `runner` the cases
  ran under, and `created_at`. The member's configuration, the prompt hash and
  the tokens are its provenance, read off its call as on any machine record.
- **A trial's `outcome` is its severest case outcome**, and `solved` is every
  case run passing. Code that ran no case has no outcome. Per-case results are
  not kept, since a fit reads only whether the member solved the problem.
- **A trial is distinct from an attempt.** An attempt is a user's solution in
  the user's private log. A trial is a model's solution, product data, global
  and append-only. A trial never enters the user's log, and no reader of
  mastery reads one.
- **A trial on a corpus problem is in the store.** Its verdict is read from
  the problem's own cases, by the runner a sitting uses.
- **A trial on an anchor is never in the store**, and neither is the call
  that wrote it. The call's prompt holds the anchor's statement, and no
  third-party statement is stored with the corpus. The trial and its call are
  kept beside the anchors, outside every repository. The trial keeps its own
  shape there, so one fit reads both kinds.
- **The code reading the anchors and running a trial on one lives outside
  this repository.** An anchor reads its input from standard input, where a
  corpus problem's cases call `solve`. That runner and the anchors' format
  belong with the anchors.
