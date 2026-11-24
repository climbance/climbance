# A cold sitting and the rating

A user starts a cold sitting from the board, solves or fails an unseen
problem under a 60-minute limit, and reads the measured and the projected
rating the board's cold panel shows. This page follows the `cold-sitting`
journey in `../model.toml`. It starts at the board's cold panel. It ends at
the cold panel reading the measured and the projected rating.

A cold sitting is a sitting with what the drill loop shows withheld.
`sitting.md` gives the drill loop's sitting, and this page names only where a
cold sitting departs from it. `../api/rating.md` gives every rule of a cold
sitting and the reason for each. `../web-app/pages/practice/cold/README.md`
gives the page. Each component below is named by its id in `../model.toml`.

## 1. The cold panel

- **The board holds the cold panel below the short exercises**, at `/` on
  the web and on the Practice tab on the phone.
  `../web-app/pages/practice/board/board.md` draws the panel.
- **The panel says the sitting is unseen, names nothing, runs 60 minutes and
  does not pause.** The panel says so because a cold sitting measures the
  user, and nobody should start one expecting a drill.
- **The panel reads the measured rating once a cold sitting has ended**, as
  `Rating 1580 ± 210, from 3 sittings`. `rating` answers it at
  `GET /api/rating`. With no game the panel shows no rating line.
- **The panel reads the projected rating under the measured one**, as
  `Projected 1642 ± 180, from 4 techniques practised`. `projection` answers
  it at `GET /api/projection`. The projected line shows before any cold
  sitting, since practice sittings move the abilities it reads.
- **A refused rating read leaves its line out, and the press still works.**
  Each line is a reading beside the press.

## 2. Serving the cold problem

- **The panel's press serves a cold sitting, or returns to the one running.**
  A user has one cold sitting running at a time, so a double press or a
  second tab records no second loss.
- **`sitting` mints the cold sitting as the statement is served**, and the
  clock starts then. A drill-loop sitting waits for the first press, as
  `../api/sitting.md` gives. Minting at serving records a cold problem read
  and left.
- **The sitting stores `cold` and `time_limit_sec` at minting.** The rating
  rests on both fields, as `../api/rating.md` gives under `## The records`.
- **The problem is drawn at random** among the problems the user has no
  sitting and no attempt on, whose standing difficulty carries a score.
- **The web opens `/cold/:sitting_id`, and the phone the Cold screen.** The
  path names the sitting, since `/problems/:problem_id` draws the record line
  a cold sitting withholds.

## 3. The running sitting

- **The page shows the statement and the editor alone.** The bar reads
  `Cold problem` in the title's place, and no record line or
  `Report this problem` press sits above or under the statement.
  `../web-app/pages/practice/cold/running.md` draws the screen.
- **The clock counts down from 60 minutes and has no press.** A hidden page
  or a backgrounded app leaves the clock running, since a cold sitting does
  not pause.
- **The way back returns to the board, and the clock keeps running.** The
  panel's press then returns to the running sitting.
- **The unsent code is kept as the drill loop keeps it**, under the
  problem's id, so a reload keeps what was typed.

## 4. Submitting

- **A submission goes through the cold routes under `/api/cold-sittings`.**
  The drill loop's route through `submission` refuses a cold sitting, since
  that route answers the failing case whole.
- **`runner` runs the code against the problem's cases, and `attempt-log`
  appends the attempt** with its attempt verification, as for any sitting.
- **A failing submission reads its verdict and the number of the first case
  it failed**, such as `Not solved: case 8, wrong answer`. The arguments and
  the case strip are left out, as a contest shows neither.
- **A failed submission before the solve costs nothing.** The outcome reads
  only whether a submission passed every case within the limit.
- **A solve leaves the sitting running.** The bar says it is solved, and a
  line under the bar says End reveals the problem.

## 5. Ending the sitting

- **The sitting ends at End, at its time limit, or at the idle bound.** A
  submission after the limit is refused. Each end without a passing
  submission reads as not solved.
- **End asks to confirm while the sitting is not solved**, so one stray press
  does not record a loss.
- **At `0:00` the page reads the sitting again**, and the engine has ended it
  at its limit. The client and the engine then agree on the end.
- **The ended screen reveals what the running one withheld**: the title, and
  the record line with the difficulty, its score, the techniques and the
  cards. `../web-app/pages/practice/cold/ended.md` draws the screen.
- **The bar reads the outcome**: solved, with the time from serving, or not
  solved. The outcome is not stored, and is read on every read from the
  attempts, the clock's start and the limit.
- **The claim and the label are asked once the sitting ends, never at a
  solve.** The claim's candidates name techniques, which a running cold
  sitting withholds. `attempt-claims` and `self-labels` store the answers.
- **The code stays read-only**, and the verdict stays the number of the
  failed case. The way back names the board.

## 6. The rating on the board

- **`rating` replays the user's cold sittings by Glicko-1 on every read.**
  Each ended cold sitting is one game against an opponent rated at the
  problem's standing score. A running cold sitting is no game yet.
- **The day of the read counts as a period so far**, so the panel's measured
  line moves as soon as the sitting ends.
- **`mastery` counts the cold sitting for every technique its problem
  carries**, and for each technique's parents. The claim is not read, since
  the user claims after the techniques were revealed. `../api/mastery.md`
  gives the ability and the practice gap, which only cold sittings fit.
- **`projection` reads each technique's ability over a representative
  contest**, as `../api/projection.md` gives. A projected rating above the
  measured one says the user knows the material and loses time under the
  clock. A projected rating below it says the reverse.
- **The panel then reads both lines.** The engine stores no rating, since a
  recalibration of the problems' scores would leave a stored copy wrong.

## Where the web and the phone differ

`../core-package/screens.md` marks a cold sitting `same` on both clients.
`packages/core` computes the time left, the verdict line and the outcome for
both.

- **The phone has no path, so a reload has no sitting to name.** The Practice
  tab's press reopens the running sitting the way the web's reload does.
- **End's confirmation is a dialog on the web and a sheet on the phone.**
- **The phone shows the ended sitting's code as text in the Code tab.** The
  phone's editor has no read-only mode.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| Serving | the sitting, with `cold` and `time_limit_sec`, revised in place | `rating`, for each game; `mastery`, for the ability and the practice gap |
| Each submission | an attempt and its attempt verification | `rating` and `mastery`, for whether a submission passed within the limit |
| End, the limit or the idle bound | `ended_at` on the sitting | `rating`, which counts an ended sitting as a game |
| The claim and the label | an attempt claim and a self-label | the board's counts; `mastery` reads neither for the cold game |
| The retirement press on the ended screen | a retirement request | the author's inbox, in `author-review.md` |

## Open questions

- **How does the panel answer once no problem is left to serve cold?** A cold
  sitting needs an unseen problem with a score. No doc gives the panel's
  answer once every scored problem has a sitting or an attempt.
- **Is a cold sitting a review of its problem's target template?**
  `../api/template-schedule.md` counts a sitting served from a rung, a probe
  or the board. A cold sitting on a problem written for a template would rate
  Again when unsolved, and could lapse a graduated card.
- **Do the run caps apply to the cold submission route?**
  `../api/submission.md` gives the caps for the drill loop's route, and
  `../api/rating.md` gives the cold route without naming them.
- **Which reader uses a cold sitting's self-label?** The ended page asks for
  one. The game reads solved or not solved alone, and no doc names another
  reader of that label.
