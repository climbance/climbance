# Log records

The rules every record of a user's private log follows. The log holds the
user's attempts, the techniques each used, why each went the way it did, the
study a card run tracks, and the knowledge log. Every record of it is
append-only apart from the sitting, which is revised while the sitting runs.

## Every record keyed to an attempt

Claims, self-labels and diagnoses share a base: an engine-minted `id`, the
`attempt_id` they assert about, and `created_at`. One reader orders all three,
latest first, with append order breaking a tie. The `id` lets a record be
cited, by an eval naming the diagnosis it scored or by a user correcting a
claim.

Ordering does not decide which record stands. The shared reader answers "in
what order", and each record's own section says who wins.

## One user's log

- **One user's log is every sitting, attempt, attempt verification, attempt
  claim, self-label and diagnosis keyed to that user**, and the calls a model
  made about the user's code or for the user's request.
- **The knowledge log is part of it**: the user's answers, stints, module status
  changes, focuses, lesson marks, certification exams, setting changes,
  limit raises and module orders, as `../api/knowledge-log.md`
  gives them. An erasure removes them with the rest, and the user's
  signed-in devices stay as the sign-in does.
- **A reader given a user reads that user's records in its query.** No command
  loads every user's log to filter it, so the author's log, which every eval
  reads, never mixes with another user's.
- **`climb log export` prints one user's whole log as JSON.**

## Erasure

- **`climb log erase` deletes one user's whole log in one transaction.**
  The log belongs to its user, so a user leaving takes the log along. The
  user and its sign-in stay, and a new log starts at the next sitting.
- **A call is erased with the log only where no other record names it.** A
  problem's cases name the call that wrote them, and that call is product
  data.
- **The append-only tables let a delete through only while an erasure runs.**
  The erasing transaction sets a setting of its own, and the trigger refusing
  a delete reads that setting. An update is refused either way, so an erasure
  removes a log and revises no record.
- **The erasure asks for the user id typed back, and `--user` has no
  default.** An erasure cannot be undone, and a default would name the
  author's own log.
- **A user exports the record and deletes the account from the settings, on
  either client.** `climb log export` and `climb log erase` serve the
  operator, and an erasure keeps the account. A user acting without the
  operator needs both acts in the app.
- **The export is the JSON `climb log export` prints, saved as a file.** It
  holds every record an erasure deletes, the card runs and the recall attempts
  included.
