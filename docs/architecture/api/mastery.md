# Mastery

How well a user knows one technique, and the chance the user solves a problem
in it under test conditions. The engine computes mastery from the log each
time it is asked, and never stores it. So the rules below are the whole model
of mastery.

## The three parts

- **Mastery has three parts per technique: recognition, execution and
  knowledge.** Recognition means the user sees that a problem needs the
  technique when nobody told them. Execution means the user writes a correct
  solution once they know the technique. Knowledge means the user recalls the
  facts the technique rests on.
- **The three parts are kept separate.** A user who misses the technique needs
  recognition drills. A user who sees it and cannot write it needs the card's
  ladder and the recall trainer. A user who cannot state its facts needs the
  questions. A single score would hide which of the three the user needs.
- **The formula is code, so changing it changes no record.** Mastery is
  recomputed on every read, so a new formula applies to every technique at
  once.
- **Each pick stores the prediction the formula made before the attempt.**
  That prediction is the only stored trace of mastery. It lets a later
  formula be compared with what an earlier one predicted.

## Knowledge

- **Knowledge is counted from answers** to the questions the technique carries.
  `../core-package/knowledge/schedule.md` gives the answer and the question
  state it is replayed into.
- **A question carries the techniques its subtopic names**, as
  `../content-repo/modules.md` `## Techniques` gives. An answer counts toward
  each technique's parents as well, as a claim does, so an answer in `knapsack`
  counts toward `dynamic-programming`.
- **Knowledge never stands in for recognition.** An answer recalls a fact the
  question named, and recognition is spotting a technique nobody named. A
  question answered correctly therefore raises no recognition reading.

## Execution

- **Execution is counted per sitting.** One sitting can hold several
  attempts, one per submission. Counting attempts would punish a user who
  submits often, though they solved the same problem.
- **A sitting with no submission counts for nothing.** A clock started and
  never submitted against records that the user worked on the problem, not
  that they tried a solution.
- **An untimed sitting counts by its verdict alone.** It says whether the user
  solved the problem and nothing about how long the solve took, so any reading
  of speed comes from timed sittings.
- **A sitting counts for every technique its attempts used.** Those techniques
  come from the standing attempt claim, or from the problem's own techniques
  when no claim stands. [`attempt-claims.md`](attempt-claims.md) gives that
  rule.
- **A sitting solved on the first submission counts more than one solved
  later.** After a failed submission the user sees the failing case, which
  helps them debug. The order of the attempts shows which submission passed.
- **The self-label on the sitting's last attempt adjusts the count.** `speed`
  marks a solve that took too long. `syntax` counts less as a failure, since
  the user knew the form. `gap` and `rust` mean the user did not write the
  form. An attempt without a label counts by its verdict alone.
- **Execution starts as the mean of a score per sitting.** A solve on the first
  submission scores 1, a solve after a failed submission 0.5, and an unsolved
  sitting 0. The score reads the attempts through the first solve. An unsolved
  sitting labelled `syntax` scores 0.25, and a sitting labelled `gap` or `rust`
  scores 0 whatever its verdict. These are starting values, and each moves only
  on what the stored predictions measure.
- **Execution reads unknown until a technique holds three sittings.** A mean
  over one or two sittings swings on a single solve, and a board showing it
  would rank techniques on noise.
- **Every sitting weighs the same, however old.** How old evidence fades is
  deferred, so the first reading counts the whole log.
- **A solve labelled `speed` counts as a full solve**, until the timed
  sittings say how slow a solve has to be to count less.

## The chance to solve

- **Mastery gives, per technique, the chance to solve a problem of a given
  score under the conditions of a cold sitting.** The contest projection is
  built from these chances, one per technique and score.
  `rating.md` gives the conditions.
- **The chance is a logistic curve on the contest scale.** The chance is
  `1 / (1 + 10^((score - ability) / 400))`, where `ability` is the user's
  ability in the technique on the contest scale. The measured rating reads a
  cold sitting on the same curve, so the two readings share one scale.
- **Each ability carries a deviation on the contest scale**, as a problem's
  score does. A reader of the chance needs to know how sure it is, and a
  technique with two sittings is far less sure than one with forty.
- **The ability is replayed from the log on every read, and never stored.**
  The replay is Glicko-1 over the technique's sittings, a rating period per
  UTC day as `rating.md` gives for the measured rating. Each sitting is a game
  against an opponent rated at its problem's standing score. Execution is
  replayed the same way, so a new formula changes no record.
- **A practice sitting scores as execution scores it.** It scores 1, 0.5,
  0.25 or 0 by the rules under `## Execution`. Glicko accepts a fractional
  game result, so the self-label and the failed submissions reach the ability.
- **A sitting on a problem with no score counts for no ability.** A game
  needs an opponent rating, and a problem labelled by the generator alone has
  none. Execution still counts the sitting.
- **A cold sitting counts for every technique its problem carries**, and for
  each technique's parents. Its result is solved or not solved, as `rating.md`
  gives. The user's claim is not read, since the user claims after the
  sitting ends and has then seen the techniques.
- **An ability starts at the user's measured rating, with deviation 350.**
  A user's skill in an unpractised technique is better guessed from the
  user's general rating than from nothing. With no cold sitting, the start is
  Glicko-1's default of 1500. The cold sittings then count twice, once in the
  start and once as the technique's games. The wide deviation keeps the start
  a weak prior.
- **A problem's chance is the chance of its weakest technique.** A solver
  missing one technique a problem needs fails the problem. The product of the
  chances, which treats each technique as a separate hurdle, is the
  alternative the log-loss compares.
- **The chance combines the ability's deviation with the score's**, by
  Glicko's predictive formula, as the measured rating's chance does. The
  engine returns the chance, the ability, its deviation and the count of
  games behind it.
- **Recalls and short exercises do not enter the ability**, for the reasons
  under `## What counts for nothing`. Whether a template's recall probability
  adds to the chance is measured by the pick's predictions, as
  [`predictions.md`](predictions.md) gives.

## The practice gap

- **A practice sitting is easier than a cold sitting.** The page names the
  technique before the statement, so recognition is given for free. A failed
  submission shows the failing case whole, and the clock pauses. Each of these
  raises the chance to solve above the chance a contest gives.
- **The practice gap is a number of points on the contest scale.** A practice
  sitting is read as a game against an opponent rated at the problem's score
  minus the gap. A cold sitting is read against the score itself. The
  ability is then the ability under cold conditions, learned from both kinds
  of sitting.
- **The gap is fitted on cold sittings alone.** For each cold sitting, the
  replay computes the chance from the log before the sitting began, at a
  candidate gap. The gap kept is the one with the lowest log-loss over every
  cold sitting. Practice sittings cannot measure the gap, since every one of
  them carries it.
- **The gap is one number for every user and every technique at first.** One
  user's cold sittings are a few a week, spread over many techniques. A gap per
  user or per technique would be fitted on a handful of games each.
- **The gap starts at 200 points and moves only on the cold sittings'
  log-loss.** The candidates run from 0 to 500 in steps of 50, and a tie
  keeps the candidate nearest 200. The value 200 is a starting guess, since no
  cold sitting existed to fit it.
- **The chance's log-loss is read held out**, in nats, by `climb
  chance-loss`. Each cold sitting is scored at the gap fitted on the other
  cold sittings. A score read on the sittings the gap was fitted to would
  understate the error.
- **Measured on 2026-11-23: no score, over 0 cold sittings.** The local
  store and the server's store held no cold sitting yet.
- **No record stores a chance.** The score replays each chance from the log
  before its cold sitting. Whether a `Prediction` carries the chance waits
  on scoring the projection, as [`projection.md`](projection.md) gives.

## Recognition

- **Recognition is counted only from recognition drills.** The problem page
  lists the problem's techniques before the statement is served. So every
  sitting tells the user the technique, and no sitting tests recognition.
  Until the recognition drill is built, recognition has no evidence and reads
  as unknown.
- **A recognition drill counts for the techniques its problem carries.** The
  user describes the approach in words. The framing judge grades the
  description against the problem's canonicals, and that grade is the drill's
  result.
- **The judge's grades count only after the judge itself is tested** against
  drills graded by hand. A judge that accepts vague answers would raise
  recognition for exactly the techniques the user cannot spot. Grades written
  before that test are stored and ignored.

## What counts for nothing

- **Sittings and drills on a defective problem do not count**, solved or not.
  `problems.md` gives the reason for sittings. A drill on such a problem was
  graded against a statement that asks the wrong thing.
- **Recall attempts do not count toward mastery.** Typing a form from memory
  is neither spotting it in a problem nor solving a problem with it. The card
  shows recall progress on its own, as [`recall.md`](recall.md) gives.
- **Short exercises do not count toward mastery either.** A judgement item and
  a key line each come from a named template, so neither tests spotting the
  technique, and neither writes a solution. The board shows the judgement
  rates beside mastery instead, as [`short-exercises.md`](short-exercises.md)
  gives.
- **Diagnoses count only after they are tested** against the user's
  self-labels. An untested diagnosis would put a guess where the user's own
  answer belongs.

Deferred, since only use answers each:

- How old evidence fades.
- Whether the judgement rates enter mastery, once the stored predictions show
  whether a technique's judgement rates predict its execution.
- The scores and the evidence bound beyond their starting values.
- Whether a solve labelled `speed` counts less than a full solve.
- A gap per user, per technique, or per practice condition such as an
  untimed sitting, once the cold sittings are enough to fit each one.
- Whether recognition drills narrow the gap for the techniques they test.
- How a module outside the technique vocabulary, such as Python, enters
  mastery. Its questions carry no technique for a reading to be kept on.
