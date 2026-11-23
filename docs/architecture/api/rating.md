# Rating

A user's measured rating: one number on the contest scale, with its
deviation, read from the user's cold sittings. This file gives what a cold
sitting serves, how it is held, when it counts as solved, and the replay that
turns the outcomes into the rating.

## The conditions

- **A cold sitting is held under the conditions a problem's score was fitted
  under.** A score is the contest rating at which a contestant solves the
  problem half the time during a contest. The rating reads each cold sitting
  as one game against an opponent rated at the problem's score. A sitting
  easier than a contest therefore raises the rating above the one the user
  would reach in a contest.
- **Each rule below follows from that condition.** A cold sitting withholds
  any help the drill loop gives a solver beyond what a contest gives.

## The problem served

- **A cold sitting serves a problem the user has no sitting and no attempt
  on.** A problem the user has worked on is no longer unseen, and a contestant
  meets each problem for the first time.
- **The problem is served, and its standing difficulty carries a score.** A
  problem labelled by the generator alone has no score, so the rating has no
  opponent rating to read the game against.
- **A problem the user opened and left without a press may still be served
  cold.** No store records which problems were opened, as `sitting.md` gives.
  This case is accepted, since recording every opening was rejected there.
- **A user has one cold sitting running at a time.** A second press reaches
  the running cold sitting, so a double press or a second tab records no
  second loss.
- **The problem is drawn at random among the problems a cold sitting may
  serve.** Serving near the user's rating is deferred until a rating exists to
  serve near.

## The page

- **The page shows the statement and the editor alone.** It shows no title, no
  technique, no card and no difficulty. Some generated titles name the
  technique, and a contest shows no problem's rating during the contest.
- **A failing submission shows its verdict and the number of the first case it
  failed, and no case's input.** A contest shows the verdict on a hidden test.
  The drill loop shows the failing case whole, as `../flows/drill-loop.md`
  gives, and that help raises the chance to solve above the one the score
  describes.
- **A cold sitting offers no hint.** A hint is anything naming the approach.
  The drill loop offers none yet. A hint added to the drill loop later stays
  out of cold sittings, since no contestant behind a score was given one.
- **The engine does not guard against the solver reading a card in another
  tab.** `../README.md` gives why the engine does not guard a verdict against
  the solver.
- **Everything the page withheld is shown once the sitting ends**: the title,
  the techniques, the card and the difficulty.

## The clock

- **A cold sitting is minted as its statement is served, and its clock starts
  then.** A sitting in the drill loop is minted at the first press or
  submission, as `sitting.md` gives. Under that rule a cold problem read and
  left would leave no record. A user could then read problems and leave each
  hard one, and every loss would go unrecorded.
- **The time limit is 60 minutes.** A contest of about two hours holds five or
  six problems. The problem at a contestant's own rating is about the last one
  the contestant reaches, with about an hour left. The limit is checked
  against real contest results once users who compete are measured.
- **A cold sitting does not pause.** A contest's clock does not stop, and a
  pause is time to think off the clock. A hidden page leaves the clock
  running.
- **A cold sitting ends at its time limit**, and a submission after the limit
  is refused. The idle bound in `sitting.md` still applies, and ends an
  abandoned cold sitting at its `last_active_at`.

- **A cold sitting has routes of its own under `/api/cold-sittings`**: one
  serves it, one reads it and one takes a submission. Pressing End and the
  claim use the sitting's own routes.
- **The drill loop's submission route refuses a cold sitting.** That route
  answers the failing case whole.

## Solved

- **A cold sitting is solved when a submission passes every case within the
  time limit.** The elapsed time runs from serving, with no pause to exclude.
- **A failed submission before the solve does not count against it.** A
  problem's score is read from whether contestants solved it. A contest's
  penalty for a wrong submission moves the contestant's place, and leaves the
  problem solved.
- **A cold sitting with no passing submission within the limit is not
  solved.** This holds whether the sitting ended at the limit, by End or at
  the idle bound. Under any other rule a user would avoid every loss by leaving
  before the limit.
- **A submission after the solve leaves the outcome as it was.** The drill
  loop reads a sitting's verdict through its first solve, and a cold sitting
  follows the same rule.
- **The outcome is solved or not solved, with nothing between.** A fractional
  outcome, for a late solve or one passing most cases, is deferred until the
  binary outcome's log-loss is measured to compare it with.

## The records

- **The sitting stores `cold`, set at minting.** The page a sitting was served
  on is known only at serving, so no replay can rebuild the flag later.
- **The sitting stores its limit as `time_limit_sec`, set at minting.** A later
  change of the limit then leaves each earlier sitting read under the limit it
  ran under.
- **The outcome is not stored.** It is read on every read from the sitting's
  attempts, its clock start and its limit.
- **A refactor of the sitting store keeps `cold` and `time_limit_sec`.** The
  sitting store is revised in place, and `sitting.md` accepts that a refactor
  may lose the pauses. The rating rests on these two fields, so they are kept.
  A cold sitting with no submission has no attempt to carry them instead.

## The interface

- **The rating answers one question: the chance a user solves a problem at a
  moment.** The projection and the log-loss read this chance alone. The
  rating and its deviation are read beside it, for display.
- **The algorithm behind the chance is replaceable.** Glicko-1 answers first.
  A later method, such as Whole-History Rating, replaces it behind the same
  question, and it is kept only if it lowers the log-loss.

## The replay

- **The rating is replayed from the user's cold sittings on every read, and
  never stored.** The sittings and their attempts hold every outcome, so a
  stored rating would be a copy that a recalibration of the problems leaves
  wrong.
- **Each ended cold sitting is one game**, against an opponent rated at the
  problem's score, with the score's deviation as the opponent's. The outcome
  is 1 when solved and 0 when not. A cold sitting still running is no game
  yet, since its outcome is not decided.
- **One scale holds both.** Glicko-1's expected score is the logistic curve on
  the contest scale, so a problem's score is directly an opponent's rating.
- **A rating period is one UTC calendar day.** Glicko-1 updates every game of
  a period from the rating at the period's start. A user plays a few cold
  sittings a day, and a shorter period changes little.
- **A rating with no deviation is read as deviation zero.** A by-hand rating
  carries none, as `../cli/difficulty/README.md` gives, and its deviation is
  deferred there.
- **A new user starts at Glicko-1's defaults, 1500 with deviation 350.** The
  deviation grows by a constant per period without a game, so an unused
  rating widens again. The starting value of that constant lets a deviation
  of 50 return to 350 over a year of days. Each value is kept only if the
  log-loss does not rise without it.
- **The rating at a moment reads every cold sitting ended by that moment.**
  The moment's own day counts as a period so far, so a solve moves the
  rating the user reads at once.
- **`GET /api/rating` returns the rating, its deviation and the count of
  games.** The chance has no route yet, since the projection reads it inside
  the engine.
- **The chance combines both deviations**, by Glicko's predictive formula. The
  user's deviation is grown to the moment asked about. A wide deviation pulls
  the chance towards one half.

## Problem ratings as they stand now

- **A replay reads each problem's standing score now, not the score that
  stood when the sitting was held.** A problem is never edited, so a later
  rating of the same problem corrects an error in the earlier one. The game
  was played against the problem as it is, so the corrected score describes
  it better.
- **A recalibration therefore moves a user's past rating.** That cost is
  accepted. The rating is replayed on every read already, and the move is the
  correction reaching the user's rating.
- **A measurement that cites a rating names the ratings it read.** A log-loss
  written down names the correction each judge rating came from. Two
  measurements on different corrections are then not compared as one.

## Scoring the chance

- **The chance for each cold sitting is read from the replay up to the period
  before it**, by asking at the start of the sitting's day. The outcome of a
  sitting is then never in the rating that predicted it.
- **The metric is the log-loss of those chances over the user's cold
  sittings.** It is the metric the difficulty calibration uses on the
  anchors, so an improvement to either part is judged by one number.
