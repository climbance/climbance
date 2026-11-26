# The knowledge queue

A user answers the knowledge questions the schedule serves, one at a time,
and stops the queue. On the way, the user may aim the focus, start a filtered
queue on a module's groups, order or pause the modules, and read a lesson.
This page follows the `knowledge-queue` journey in `../model.toml`. It starts
at the knowledge home's Continue. It ends at the queue's stop and its summary.

`../core-package/knowledge/README.md` names the files giving the rules, and
this page cites them rather than restating them. Each component below is named
by its id in `../model.toml`. Every rule in this journey runs on the device,
in `packages/core`, on the web and on the phone alike.

## 1. The knowledge home

- **The web's home is `/knowledge`, and the phone's is the Home screen.**
  `knowledge-screens` computes what the home says, so both clients name the
  same counts and the same rows. `../web-app/pages/knowledge/home/README.md`
  gives the page.
- **Continue is the home's one act, and it starts the next queue.** The line
  under Continue counts the reviews due and the new questions left today. The
  press reads Start while the user's knowledge log holds no answer and no
  lesson mark.
- **The panel above Continue names the focus, with three presses.** The
  presses clear the focus, switch it between strict and relaxed, and raise
  today's limit by five. Clearing asks first. `queues` gives a strict focus
  and the raise, in `../core-package/knowledge/queues.md`.
- **A strict focus names the reviews waiting outside it.** A press on that
  count serves those reviews as a review queue.
- **The focus panel dates when the focus is reached**, at the daily limit and
  at the user's own pace. `projections` computes both dates, as
  `../core-package/knowledge/projections.md` gives.
- **The home names a lesson ready to read and a certification ready for its
  exam**, each as a link above the focus. `exam-and-certification.md` follows
  the certification's link.
- **The modules list below Continue, one row per module not archived.** A row
  names the group next up, which `gating` reads from the frontier. The row
  also names the reviews due, and opens the module's page.
- **The modules list in the user's order.** The web moves a row with up and
  down presses, and the phone drags it. The order changes no queue, as
  `../core-package/knowledge/queues.md` gives under Module order.
- **The reviews ahead close the home**: one column per learning day, for
  fourteen days. `projections` counts them, every review assumed to pass.

## 2. Answering the queue

- **The web's queue is `/knowledge/queue?mode=next`, and the phone's is the
  quiz screen.** `../web-app/pages/knowledge/queue/README.md` gives both.
- **`queues` picks each question when it is needed**, under the daily limit,
  the focus and the module status. `knowledge-schedule` replays FSRS over the
  user's answers for each question's state, as
  `../core-package/knowledge/schedule.md` gives.
- **`answering` runs the queue one question at a time.** An unanswered
  question asks for the reply. An answered one reads its verdict and its
  explanation, and Next is the act.
- **A `choice` question takes a digit or a press**, and a `short` question
  takes a typed reply. A `?` after a reply marks the reply a guess, which the
  schedule rates Hard when correct.
- **An open question reveals its key on a press**, and the user ticks the
  points recalled and the traps fallen into.
  `../content-repo/questions.md` gives the grade the ticks make.
- **A wrong choice names the misconception behind it**, and the answered
  question offers its detail on a press. The detail links the lessons
  teaching the question, and names each one already read.
- **`client-store` puts each answer in the outbox**, and sends it within ten
  seconds. `../core-package/knowledge/store.md` gives the outbox, and
  `phone-offline.md` follows a queue answered with no connection.
- **A queue offers a lesson as a stop**, where the queue would serve a new
  question whose lesson holds it back. The stop names the lesson, its
  reading time and why it is offered, with Read and Later.
  `../content-repo/lessons.md` gives when a lesson is offered.
- **Read opens the lesson over the running queue.** Closing the lesson
  returns to the queue, and so does Mark read. The web opens the lesson in a
  dialog, and the phone as a screen above the queue.
- **A queue may offer a baseline test or a delayed test as a stop.**
  `baseline-tests` samples the test, as
  `../core-package/knowledge/baseline-tests.md` gives. `first-run.md` follows
  the first baseline test.
- **A raise inside the queue adds five new questions today.** The raise is
  offered inside the next queue and the filtered queue, as on the home.

## 3. The stop and the summary

- **Stop ends the queue, and so does leaving through the navigation.** A
  queue also ends when nothing is left to serve.
- **Stopping stores a stint**: the queue's mode, the questions answered and
  the score. `client-store` sends the stint at once.
- **The summary lists every answer of the queue**, with Back to Knowledge and
  Continue again. `../web-app/pages/knowledge/queue/stopped.md` draws it.
- **A closed tab or a killed app stores no stint**, and the answers already
  given stay in the log. A web reload starts a queue of the same mode again.

## 4. The focus and the modules

- **The web's module page is `/knowledge/modules/:module`, and the phone's
  is the Module screen.** A topic reads as a panel of subtopics by level, and
  each group reads as covered, open, locked, holding no questions or not yet
  open.
  `../web-app/pages/knowledge/module/README.md` gives the page.
- **A press of its own aims the focus at the module, a topic or a
  subtopic.** The phone also aims at a subtopic from the module's map. A focus
  record is a line of the log, so the next queue on the other client serves
  the same focus.
- **A certification focus is aimed from the certification's conditions**,
  which `exam-and-certification.md` follows.
- **The home's focus opens what the focus covers.** A focus on a module, a
  topic or a subtopic opens the module's map, centred on the focus.
- **The status press pauses, resumes or archives the module.** Archiving asks
  first, since an archived module leaves the home. `account.md` follows the
  restore from the settings.
- **A paused module leaves the next queue, the review queue and the exams.**
  The filtered queue still offers it, as
  `../core-package/knowledge/queues.md` gives under Module status.

## 5. A filtered queue

- **A filtered queue starts from the start sheet on a module's page.** The
  press opening the sheet names the scope: a group's cell, a subtopic's name,
  or Start beside a topic or the module.
  `../web-app/pages/knowledge/module/start-sheet.md` draws the sheet.
- **The sheet narrows the scope by level, kind and due**, and its Start press
  counts what the choices leave. The phone also opens the sheet from a map
  node and a Stats cell.
- **Locks do not apply to a filtered queue**, so a locked cell opens the
  sheet too. `gating` still holds the next queue's new questions to the
  frontier.
- **Starting a filtered queue moves no focus.** The sheet's choices are
  stored nowhere. The web carries the choices in the queue's URL, which no
  other device reads.
- **A filtered queue then runs as step 2 gives, and stops as step 3 gives.**
  `knowledge-sync` stores its stint as the filtered queue, translating the
  wire's `drill`, as `../api/knowledge-sync.md` gives.

## 6. A topic's placement

- **Place beside a topic's heading starts the topic's placement** on the
  exam's screen, as `../core-package/knowledge/placement.md` gives. `gating`
  reads a placed group as done, so the next queue starts above it.

## 7. Lessons and subtopics outside a queue

- **The lessons page lists each module's lessons in order**, each row naming
  whether the lesson is locked, ready or read, and its minutes. The web's page
  is `/knowledge/lessons`, and the phone's is the Lessons screen.
- **A locked lesson opens too, and names what it needs.** Reading early skips
  nothing.
- **A lesson's page reads its text, and Mark read is the act.** Mark read
  returns to the page the lesson was opened from. A read lesson offers Mark
  unread, which stays on the page.
- **A subtopic's page reads one line per level, its lessons and its cards.**
  The page offers no Start and no Focus, since those presses sit on the
  module's page. `cards-and-recall.md` follows a card opened from it.

## Where the web and the phone differ

`../core-package/screens.md` marks two of this journey's acts `by platform`,
and gives the reasons.

- **The web orders the modules with up and down presses, and the phone with
  a drag.** A drag needs a long press, which a pointer does not hold well.
- **The phone types a `short` reply on a keyboard of the app's own.** The
  phone's system keyboard hides the symbols a reply needs, and its suggestion
  strip completes words.
- **The phone pulls a list down to sync**, since a phone has no reload. The
  web syncs when the page becomes visible.
- **The phone starts a queue with no connection, and the web does not.** The
  browser fetches the page's own files from the engine on each load.

## What each step stores, and what reads it

`knowledge-sync` stores each line `client-store` sends, and `knowledge-log`
holds it in one of nine append-only tables, as `../api/knowledge-log.md`
gives.

| Step | Stores | Read later by |
|---|---|---|
| Each answer | an answer, in `answers` | `knowledge-schedule`, for the question's state; `gating`, for passed groups; `queues`, for today's new questions; `projections`; `certifications`, for coverage and retention |
| A test answer | an answer carrying its measure | `baseline-tests`, for the learning gain; `placement`, for the placed groups; the schedule ignores it |
| The stop | a stint, in `stints` | the summary on the stop; a stopped test's stint, so the test is not offered again |
| A raise | a limit raise, in `limit_raises` | `queues`, for today's limit on every device |
| A focus press | a focus, in `focuses` | `queues`, for the next queue; `projections`, for the focus's dates; the exam's opening choices |
| A status press | a module status change | `queues`, which leaves a paused module out; the home's rows |
| An order press or drag | a module order, in `module_orders` | the home's rows on every device |
| Mark read or Mark unread | a lesson mark, in `lesson_marks` | `queues`, which releases the lesson's held questions; the lessons page |

The start sheet's choices are stored nowhere, as step 5 gives.

## Open questions

- **Does a web reload count as a new queue run?** A run offers one baseline
  test and each lesson at most once. A reload starts a queue of the same mode
  again, so a second test or the same lesson may be offered. No doc says
  which.
- **Does the daily limit cap a filtered queue's new questions?** The raise is
  offered inside the filtered queue, which implies the limit applies there.
  `queues.md` names the limit for new questions and does not name the
  filtered queue.
- **Which later read uses a practice stint's count and score?** The stop's
  summary reads them. No doc names a page or a component reading a stopped
  next queue's stint later.
