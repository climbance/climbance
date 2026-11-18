# Attempt log

An attempt is a user's solution to a problem, successful or failed, with its
attempt verification. The log appends both, and they are private to the user.

- **The drill loop is the only source.** The engine served the problem and
  watched the sitting, so nothing else is in a position to assert an attempt.
- **An attempt records whether its sitting restored an earlier solve**, as
  `restored`. The page sends it with the submission, and the engine does not
  check it, for the reason `README.md` gives about guarding a verdict. Absent
  on every attempt written before the field, and absent means no restore.
- **A restored attempt is not counted as a solve by mastery.** Its verdict
  stands, and its sitting counts as a failure to solve independently.
- **The verification is its own record**, an `AttemptVerification` keyed by
  `attempt_id`, as a canonical's verification is keyed by `solution_id`.
  `solved` is the projection over the verification's results, and the raw
  result carries what the projection drops. A timeout and a wrong answer are
  both unsolved, and only the timeout is evidence of slowness.
- **An attempt's verification is a record type apart from a solution's**, as
  an attempt claim is apart from a solution claim. The results of the user's
  own code are private, and a solution's verification is product data. One
  type in both stores would leave privacy to whichever writer chose the file.
- **The two types share the fields a run is decided by**: the cap, the runner
  and the per-case results. `runner.md` fixes what each of those means.
- **The elapsed time is cumulative, from the clock's start to that
  submission.** A drill mints an attempt per submission, so the second attempt
  of a sitting carries the whole time since `clock_started_at`, rather than
  the time since the first submission. Reading the statement before the first
  press is not counted. `time_to_solve_sec` names the time
  to solve, and a per-segment number would report three minutes on the attempt
  that solved the problem.
- **The pauses are excluded already**, since the number is the sitting's
  elapsed time at the moment the attempt finished.
- **The time between two submissions is the difference of two attempts.** No
  field records that gap, and cumulative numbers lose nothing by leaving it
  derived.
- **Problem techniques are never denormalized onto an attempt.** Problem
  techniques are re-derivable and the log is not, so a copy taken when the
  attempt was written would drift with no way to tell which is right.
