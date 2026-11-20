# Sitting

One session on one problem: when it began, when its clock started, when it
ended, and every pause between.

## Minting

- **The engine mints the sitting at the first clock press or the first
  submission on the problem**, and every attempt of that sitting carries the
  sitting's id. The log is append-only, so an attempt written without the id
  can never be grouped with the sitting's others.
- **Serving the statement mints nothing.** A sitting minted at serving made
  every opened problem a record, and the author avoided opening problems
  because of it. A user reading a problem and leaving it has not practised it.
- **An untimed submission mints a sitting too.** Mastery counts execution per
  sitting, and an untimed attempt carrying no sitting would need a second
  grouping rule for its retries.
- **The alternative is grouping attempts by how close together they were
  written.** Such a grouping is a guess about a pause, and two readers reading
  one log would draw the sitting's boundary at different attempts.
- **No store records which problems were opened and abandoned.** A problem
  opened and left before any press or submission leaves no sitting, and
  nothing reads that count today.

## The record

- **The record is stored rather than held in the process that minted it.**
  One sitting reaches the engine as several calls, and a restart between them
  would lose the start the duration is measured from.
- **The store is revised in place, as the draft store is.** A sitting's state
  moves while the sitting runs, so the sitting store can be refactored where
  the append-only logs cannot.
- **The pauses live in that store alone, and a refactor of it can lose them.**
  No append-only record carries the pause history. That cost is accepted: a
  sitting is evidence about how practice ran rather than a record the board
  counts.
- **The record is kept after the sitting ends**, and `ended_at` closes it. How
  often practice is interrupted and how many sittings a day holds are readable
  in the sitting store alone.
- **A sitting records the device it was minted on**, as `device`, named as a
  knowledge record names its device: `web` on the web, the device name on the
  phone. A solve typed on a phone is slower than one typed at a keyboard, and
  execution reads the elapsed time, so the two have to read apart.
- **The minting device names the whole sitting.** A press from a second device
  reaches the running sitting, and that device is not recorded. The field is
  absent on every sitting stored before it.
- **A sitting records when it was last touched**, as `last_active_at`. Minting
  the sitting, serving its problem while it runs, a submission, a pause and a
  resume each set it. The record then
  says when practice stopped, without a reader joining the attempt log to it.

## The clock

- **A sitting records when its clock started**, as `clock_started_at`. The clock
  begins on the user's press, or as the statement is served where the clock
  preference `../flows/drill-loop.md` gives is on. A sitting the first
  submission minted carries no clock start. Reading done before the press is not
  counted.
- **A sitting whose clock never started is untimed.** `clock_started_at` stays
  absent, and the sitting's attempts carry no `time_to_solve_sec`. Untimed
  practice is legitimate, and a time reconstructed afterwards would be a guess.
- **A running clock is paused and resumed, and the clock stops for a pause.**
  The user steps away from the problem, and a duration counting the hours away
  says nothing about solving it. A clock that never started has nothing to
  pause, so every pause falls after `clock_started_at`.
- **A pause is stored as its own interval**, `at` and `until`. A total of the
  time paused says how long and never how often, and a sitting paused once for
  two hours is different practice from a sitting paused nine times.
- **Only the last pause is open, and a sitting ends with none open.** An
  ended sitting holding an open pause would report an elapsed time that moved
  with the moment it was read.
- **The elapsed time runs from `clock_started_at` and excludes every pause**,
  and the attempt carries it as `time_to_solve_sec`.
- **A solving submission leaves the sitting running.** A further submission,
  such as the better form after a brute force, joins the sitting and carries its
  id. A user who solved and left the page leaves the sitting to the idle bound,
  which ends it at the solve's `last_active_at`. `../flows/drill-loop.md` gives
  why.
- **The loop decides what starts and ends a pause**, not the record. A button,
  a hidden tab and an idle timer each leave the same interval.

## The idle bound

- **A sitting idle longer than 45 minutes is ended at its `last_active_at`.**
  Two of the first seven sittings were left running, and serving that problem
  again reached the old clock, which reports the hours away as time to solve.
  An open pause is closed at the same moment, so an ended sitting holds no open
  pause.
- **The ending happens where the sitting is next read**, and nothing runs in
  the background. An abandoned sitting therefore stays running in the store
  until the loop serves or reads it. The elapsed time it reports is the
  same whenever that happens, since the end is `last_active_at` rather than
  the moment of reading.
- **Serving the problem again shows no sitting** once the idle one is ended.
  The next press or submission mints a new sitting, so the clock the solver
  sees starts at zero.
- **A submission to a sitting idle past the bound ends it and is refused.**
  The elapsed time that attempt would carry counts the hours the user was
  away, and no attempt is worth more than the time it reports.
- **Pressing End does not touch `last_active_at`.** A sitting the user ended
  therefore carries an `ended_at` later than its last activity, and one the
  bound ended carries the two equal. No field states which happened, and the
  two timestamps say it.
- **The bound counts idleness, not elapsed time.** A solver thinking for an
  hour with the page open is practising, and the loop keeps that sitting
  touched. `../flows/drill-loop.md` gives the loop's own steps, a hidden page
  among them.
