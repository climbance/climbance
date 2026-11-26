# The readiness bar

The site promises AI engineering as a skill, so "learned" is a measured state.
The readiness bar is that state: five readiness sittings on the spine's desk
tasks, each passed, and each passed again four weeks or more later on a task
the learner has not seen. The bar is a state derived from the log. It is not
a certificate, and it names no job title.

[`patterns.md`](patterns.md) gives the spine and its steps. The task record,
the hidden set and the task's own bar, the threshold its metric must clear,
belong to `../ai-task-grading.md`. The readiness bar and a task's bar are two
different things, and this file names the first in full each time.

## The readiness sittings

| Spine step | Desk task | Passed when |
|---|---|---|
| 3 | Build an extractor to a schema-valid rate under a token budget | The task's bar on schema-valid rate and field F1, within the token budget |
| 4 | Write the eval set that catches a classifier's broken variants | All but at most one of the stored variants failed, and the clean component passing |
| 6 | Fix a planted fault in a chunker | The task's bar on recall at k, and the fault's slice passing |
| 7 | Build a retriever to a recall bar | The task's bar on recall at k, within the budget, every declared stage earning its place |
| 8 | Decide whether to rerank | The measured winner chosen, and every declared stage earning its place |

- **The bar holds whole tasks alone.** An AI drill is part-task practice, and
  passing one shows a part of the skill. The spine's drills prepare the
  readiness sittings and count toward nothing here.
- **Knowledge stays apart.** A certification measures the module's questions,
  as `../../core-package/knowledge/certifications.md` gives. A learner may
  hold the readiness bar without a certification, and the site states the two
  separately.
- **Simplicity is required on steps 7 and 8.** In practice a stage that earns
  no place is reported beside a pass, as [`README.md`](README.md) gives. On
  the readiness bar the same finding fails the sitting, since reaching for
  each stage only where it pays is the skill the bar asserts.
- **Each step's score is the task's own bar, never a number fixed here.** A
  task lands with its bar between its baseline's score and its reference's.
  A fixed number would mean a different difficulty on every generated task.
- **The eval set step allows one variant missed.** A task stores at least
  five variants. One variant may differ from the clean component on inputs no
  reasonable eval covers, and a learner should not fail on that variant.

## A readiness sitting

- **A readiness sitting serves a task the learner has never been served.** A
  task seen in practice could be passed from memory. Each readiness sitting
  draws a fresh landed task of its step's kind.
- **The task's pattern is named, and nothing else is offered.** The interface
  names the pattern, so withholding it is impossible. The sitting offers no
  hint, no lesson link and no worked reference.
- **The hidden set grades one final submission.** The learner runs the
  visible set as often as the budget allows. Grading the hidden set on every
  run would let a learner fit the hidden set by trial.
- **A readiness sitting runs under a time limit and no pause**, as a cold
  sitting does. The limit per step is deferred to the durations the first
  retrieval sittings measure.
- **A readiness sitting is opened by the learner**, from the bar's page. The
  pick never serves one unasked, since a readiness sitting spends a fresh
  task and the learner's attention under a clock.

## The retest

- **A step's retest comes due 28 days after its pass.** Twenty-eight days
  matches the delayed test, which measures knowledge kept over four weeks or
  more. A pass only days old shows the skill was reached, not that it lasts.
- **The retest is a readiness sitting of the same step on another fresh
  task.** The same task again would test memory of that task.
- **A step is held once its pass and a retest pass 28 days or more apart are
  in the log.** The bar is held once all five steps are held.
- **A failed retest reopens that step alone.** The step needs a new pass, then
  a new retest 28 days after that pass. The other held steps stand, since
  each step measures a different part of the skill.
- **A failed first sitting reopens nothing.** The learner practises the
  step's pattern and opens another readiness sitting when ready. The number
  of readiness sittings is not limited, and each one is in the log.
- **A held step does not expire.** The page states the date each step was
  held. An expiry period is deferred until learners who held the bar have
  been retested a second time.

## Versions of the bar

- **The readiness bar has a version, named by its list of steps.** The spine
  grows as further patterns gain desk tasks, and a step is added to the bar
  with them.
- **A held step carries over to a later version that keeps it.** The learner
  holds the later version once its new steps are held.
- **A learner is described by the version held.** A learner who held version
  1 is described by version 1's five steps, and never by a later version's.

## What the site may say

- **About the bar, the site states its steps and its retest.** The claim
  `ai-engineering-readiness-bar` in the site's claims is the one sentence.
- **About a learner who holds the bar, the site may say exactly this:** the
  learner holds the AI engineering readiness bar of the version named, on the
  date named. Each step is named with its pass and its retest.
- **The site never says a learner is an AI engineer, is certified, or is
  ready for a job.** The bar measures five tasks in three patterns. A job
  title asserts far more than five tasks measure.
- **The page a learner may share is deferred**, until a learner holds the
  bar.

## The state is derived

- **The readiness bar's state is derived from the log on every read, never
  stored.** Each readiness sitting is an attempt with a flag naming its step,
  and the pass is read from the attempt's grading. A stored state would
  drift from the attempts it summarises.
- **The records the bar reads are written by the AI desk tasks.** The record
  of a readiness sitting is designed with the AI task record in
  `../ai-task-grading.md`.
