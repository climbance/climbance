# Mastery

How well a user knows one technique. The engine computes mastery from the log
each time it is asked, and never stores it. So the rules below are the whole
model of mastery.

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
- How a module outside the technique vocabulary, such as Python, enters
  mastery. Its questions carry no technique for a reading to be kept on.
