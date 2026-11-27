# Baseline and delayed tests

The baseline test measures what a user holds of a topic before studying it.
The delayed test asks the same questions four weeks or more later. The
difference between the two scores is the learning gain the strategy claims.
A lesson's pretest is a different thing, as
`../../content-repo/lessons.md` gives.

## The baseline test

- **A topic gets one baseline test, offered before its first new question.**
  When the next or the focus queue would serve the first new question of a
  topic the user has answered nothing in, it offers the baseline test first.
  The test samples the topic's subtopics at that question's level. On a
  module no answer and no stint names, a placement is offered first, as
  `placement.md` gives. A lesson is offered only once its pretest is spent,
  so a test waiting for the first lesson would follow practice answers. A
  taken test then spends that pretest, as `../../content-repo/lessons.md`
  gives.
- **A queue run offers one baseline test.** Once a run has offered one, the
  new questions of every other untested topic wait for a later run, which
  offers that topic's test. Two modules' tests in a row asked a new user 28
  questions before any practice. A withheld topic keeps no answer from this
  run, so its test is still offered later.
- **One test per topic, rather than per subtopic or per module.** A test per
  subtopic would interrupt every lesson, and a test per module would ask
  about topics the user may never open.
- **The test samples two questions per subtopic, at most twenty.** Only
  `choice` and `short` questions are sampled, since an open question's grade
  is the user's own report, as an exam excludes it too.
- **The test's stop and its summary name the module beside the topic**, as
  `Algorithms · Procedures`. The stop interrupts a queue that may span
  several modules, and a topic's title alone does not say which module it
  belongs to.
- **The test gives no feedback until the end**, as an exam does. A shown key
  would teach the next question's answer.
- **The user may skip the baseline test once.** A skip stores a baseline
  stint that answered nothing, so the test is not offered again. A skipped
  topic gets no delayed test.

## The delayed test

- **The delayed test asks the baseline test's questions again**, in a new
  order. The two tests then ask items of the same difficulty, so the gain is
  read question by question. A user remembering a baseline question counts
  toward what the product taught.
- **The delayed test is offered from four weeks after the baseline test.** It
  is a stop at the start of the next queue, like a lesson offered there, and
  stays offered until it is taken. Four weeks is the delay the strategy's
  claim names.
- **Later passes the delayed test's stop for the run alone.** The test stores
  nothing until it is taken, so the next run offers it again. A skip would
  lose the topic's gain for good, so the delayed test has none.

## The answers

- **A test answer carries the test it was given in**: `baseline` or
  `delayed`, as the answer's `measure`. A practice answer carries none.
- **The schedule ignores every answer carrying a measure.** FSRS replay, the
  question states, passed and the daily new-question limit all skip it.
  Most baseline answers are wrong, on questions the user has not studied. As
  ordinary answers they would make those questions weak, and the review
  queue would serve them before their lesson is read.
- **A placement answer carries the measure `placement`**, and the schedule
  ignores it as well. The baseline test samples none of the questions a
  placement asked, as `placement.md` gives.
- **The rule exists in Python and in `packages/core`**, held together by the
  shared fixtures, as `../README.md` gives for the schedule.
- **The queues order the tested questions last.** A question the test asked
  stays unseen, and a queue serves it as new only once its group has no
  other new question left, as `queues.md` gives.
- **The baseline's questions are read from its answers**, never stored as a
  list. A topic has one baseline test, so the answers measuring `baseline` on
  that topic's questions are the test.
- **The gain is derived from the answers on every read**, per topic and per
  user, and never stored. Reading it over every user belongs to the
  retention report.

Deferred, since only use answers each:

- A baseline test at each further level of a topic.
- Whether a delayed test still offered after some months stops being
  offered.
- A baseline test for a card's techniques. These tests cover the knowledge
  modules alone.
