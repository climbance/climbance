# Placement

A placement asks a user about a topic's subtopics, highest level first, and
places each group the user already holds. Gating counts a placed group as
done, so an experienced user skips the groups below the level they start
studying at. The modules are sequential, and without placement an engineer
answers every Foundation question before reaching the level they need.

## The placement steps

- **A placement covers one topic, and asks about each of its subtopics in
  listing order.** A placement over a whole module would ask about topics the
  user may never open. The baseline test is scoped to one topic for the same
  reason, as `baseline-tests.md` gives.
- **A subtopic's placement starts at its highest written level.** A level is
  written when its group holds a `choice` or a `short` question. An open
  question's grade is the user's own report, so a placement excludes it, as an
  exam does.
- **A placement step asks three questions of one group, sampled at random.** A
  group holding fewer asks every one it holds.
- **A placement step passes when every answer is correct and none is marked a
  guess.** A blind guess on three four-way choices passes once in 64 placement
  steps.
- **The first wrong or guessed answer misses the placement step, and the
  placement moves down one written level.** The rest of the missed placement
  step is not asked. A strong user answers three questions per subtopic, and a
  user who holds nothing of a subtopic answers one per written level.
- **A pass ends the subtopic's placement.** The user then studies the subtopic
  from the level above the pass. A miss at level 0 ends it too, and places
  nothing.
- **A placement ignores the gates.** A placement step asks about a locked
  group, since each answer is evidence of what the user already holds.
- **A placement gives no feedback until the end**, as an exam does. A question
  a placement asked stays unseen, and a shown key would answer it before the
  user studies it. The summary names, per subtopic, the level placed through.
- **The user may stop a placement at any time.** A stopped placement step
  resumes at the next placement of the topic, sampling from the questions it
  has not asked.

## Where a placement starts

- **A Place press beside a topic's heading on the module's page starts its
  placement**, on both clients, while the topic has a question left to ask.
  A topic every subtopic of which a placement ended offers no press.
- **The placement runs on the exam's screen**: `/knowledge/exam` on the web,
  the quiz screen on the phone. Its title counts the questions asked, since
  the number left depends on the answers. Its Done returns to the module.

## What a pass places

- **A pass at a level places the subtopic's group at that level and at every
  level below.** A level measures the depth of a question, so a user answering
  the deeper questions is taken to hold the shallower ones. The lower levels
  are not asked, which keeps a strong user's placement to three questions per
  subtopic.
- **Every rule reading a group as done reads a placed group as done.** In
  `gating.md` these are the level order, the prerequisite graph, the frontier
  and next up. A lesson's needs in `../../content-repo/lessons.md` and the
  date the focus is reached in `projections.md` read it too. The next queue
  then serves no new question from a placed group. The filtered queue still
  serves a placed group's questions.
- **A placed group reads placed on the module's page**, until its passed
  share reaches the pass ratio and it reads covered.
- **A placed group is not covered.** A certification's coverage is the passed
  share of each group, as `certifications.md` gives, and a placement passes no
  question. A certification rests on retention measured over weeks, and three
  answers in one sitting measure none.
- **Each group is placed once.** A missed placement step is not asked again,
  and the user reaches the group by studying the level below. A repeated
  placement step would let a guess place a group on a later try.

## The answers

- **A placement answer carries the measure `placement`.** The schedule ignores
  every answer carrying a measure, as `baseline-tests.md` gives. A missed
  placement question would otherwise read as weak, and the review queue would
  serve it before its lesson is read.
- **The placement is derived from the answers on every read**, never stored as
  a state. A group has one placement step, so the answers measuring
  `placement` on a group's questions are that placement step. This follows
  `gating.md`, under which an unlock is never stored.
- **Stopping a placement stores a stint** of mode `placement`, naming its
  module and its topic. The stint records the score and the count, as every
  stint does.
- **A question a placement asked is served as new after the rest of its
  group's new questions**, as a question a baseline test asked is in
  `queues.md`.

## The baseline test

- **The baseline test's answers do not serve as a placement step.** The
  baseline samples one level, the level of the topic's first new question, at
  two questions per subtopic. A placement starts at the highest written level,
  so a baseline answer could only ever serve its last placement step. Two
  questions per subtopic is also fewer than a placement step asks.
- **A placement answer does not serve as a baseline answer.** The baseline
  test measures the topic at one level for every user, and the delayed test
  reads its gain question by question. Adaptive answers at several levels
  would give each user a different test under the same measure.
- **Each sample excludes the questions the other asked.** A question already
  asked would be answered from that first sight, and the baseline would
  measure the placement rather than the user's prior knowledge.
- **A placement answer does not prevent the baseline test.** The baseline test
  is offered before the topic's first new question, at that question's level.
  After a placement that level is the one the user starts studying at, so the
  delayed test reads the gain where the product teaches.

Deferred, since only use answers each:

- Whether three questions per placement step misplace users often enough to
  need a fourth. The stored placement answers and the later answers on placed
  groups answer it.
- Whether a user may undo a placement and walk a subtopic from level 0.
- Offering a placement in a module's first run, before its first lesson.
