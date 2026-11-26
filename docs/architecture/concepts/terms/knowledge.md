# Knowledge terms

Words this project gives its own meaning for the knowledge modules, their
questions and their queues. Every file in `docs/architecture/` uses them
without redefining them.

## Modules and questions

- **Module**: one subject of declarative knowledge, such as Python or system
  design. A module holds topics, and a topic holds subtopics.
- **Level**: how deep a question goes, one of four: 0 Foundation, 1 Associate,
  2 Professional and 3 Expert. A problem's difficulty is a different field.
- **Group**: one subtopic at one level, the unit gating and coverage count.
- **Mapped**: a subtopic the module's course lists while no level of it holds
  a question. It reads Not yet open, offers no press, and counts toward
  nothing.
- **Question**: one fact asked about, in one of three formats: `choice`,
  `short` or `open`.
- **Open question**: a question the user answers in their own head, then
  grades by ticking the points of its key they recalled.
- **Concept**: one claim about a module's subject, with its source, its
  witness and the wrong beliefs about it. A lesson section teaches it and a
  question tests it. `docs/authoring/concepts.md` gives the record.
- **Witness**: code whose output shows a concept's claim holds, run on every
  supported build by the module check.
- **Key**: the two to six points an open question's answer has to contain.
- **Trap**: a known wrong claim, listed on an open question.
- **Lesson**: a short text teaching one or more groups, read before their new
  questions.
- **Pretest**: how many of a lesson's questions a user may meet before reading
  the lesson.

## Answers and their states

- **Answer**: one reply to a question, by one user. Distinct from an attempt,
  which is a user's solution to a problem.
- **Question state**: unseen, weak, due, learning or retained, replayed from
  the user's answers on every read.
- **Retained**: the question state once FSRS stability reaches 21 days.
  Distinct from mastery, which is per technique.
- **Servable**: a question a queue may serve now: unseen, or past its due
  time.
- **Gating**: the rule opening a group's new questions once the lower levels
  and the prerequisite subtopics are done.
- **Frontier**: the open groups that are not done, where new questions come
  from.

## Queues and tests

- **Queue**: a sequence of questions picked one at a time from what is servable:
  the next queue, the review queue or the filtered queue.
- **Filtered queue**: the queue serving questions the user chose by topic,
  subtopic, level or kind, locked or not.
- **Stint**: the record of one queue or one exam, stored when it stops.
- **Baseline test**: a sample of a topic's questions, asked before its first
  lesson, whose answers the schedule ignores. Distinct from a lesson's pretest.
- **Delayed test**: the baseline test's questions asked again four weeks or
  more later. The difference in score is the learning gain.
- **Measure**: the test an answer was given in: `baseline`, `delayed` or
  `placement`.
- **Placement**: the test of one topic's subtopics that places the groups a
  user already holds. Each subtopic is asked first at its highest level
  holding a `choice` or a `short` question, and one such level lower after
  each miss.
- **Placement step**: one placement's questions on one group, at most three.
  It passes when every answer is correct and none is a guess.
- **Placed**: a group a placement step passed, or a lower group of the same
  subtopic. Gating reads a placed group as done.
- **Focus**: the module, topic, subtopic or certification the next queue is
  aimed at.
- **Module status**: active, paused or archived, set by the user.
- **Certification**: one scope, a topic or a whole module, at one level. Earned
  on coverage, retention, an exam and its prerequisites.

## Projections and sync

- **Projection**: a reading of the user's knowledge log forward, derived on
  every read and never stored.
- **Review forecast**: the projection counting the reviews each of the next
  fourteen learning days will hold, every review assumed to pass.
- **Snapshot**: the whole content of every live module as one JSON document,
  at snapshot format 6, which both clients load.
- **Sync line**: one knowledge record as a client writes it and the sync
  carries it, named by its kind and its `client_id`.
- **Outbox**: the knowledge records a client holds that the engine has not
  acknowledged, kept in the client's copy of the user's log.
