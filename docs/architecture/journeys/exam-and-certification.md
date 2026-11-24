# A level exam and a certification

A user takes an exam on one level of the knowledge modules, or a
certification's exam once its other conditions hold, and reads the result.
This page follows the `exam-and-certification` journey in `../model.toml`. It
starts at the knowledge home naming a certification ready for its exam, or at
the home's Exam press. It ends at a certification earned, or at its conditions
read as not yet met.

`../core-package/knowledge/certifications.md` gives the rules of a
certification and an exam, and this page cites it rather than restating them.
Each component below is named by its id in `../model.toml`. Every rule in this
journey runs on the device, in `packages/core`, on the web and on the phone
alike.

## 1. The ways in

- **The knowledge home names a certification ready for its exam**, as a link
  above the focus. The link opens the certification's conditions.
  `knowledge-queue.md` gives the rest of the home.
- **The home's Exam press opens a level exam's choices**, at a lower weight
  than Continue. The web's page is `/knowledge/exam`, and the phone's is the
  Exam screen.
- **The home's header links the certifications page.** The web's page is
  `/knowledge/certifications`, and the phone reaches the Certifications
  screen from its top bar.
- **A certification focus on the home opens that certification's
  conditions.** The module's map also opens a certification's conditions, as
  `../core-package/screens.md` gives.

## 2. The certifications and their conditions

- **The certifications page reads each module as a grid of scopes by
  level.** A scope is one topic or the whole module. `knowledge-screens`
  computes what each cell says, and `certifications` decides each cell's
  state. `../web-app/pages/knowledge/certifications/README.md` gives the
  page.
- **Each cell reads as earned, lapsed, ready for its exam or not yet.** A
  legend above the grids names each cell's icon, on both clients.
- **A cell opens the certification's four conditions**, with the counts
  behind each: the prerequisites earned, every group covered, the questions
  retained, and the exam. The web opens the conditions in a dialog, and the
  phone in a sheet.
- **`gating` supplies the groups a certification covers**, and
  `knowledge-schedule` supplies which questions are retained. Retention reads
  each question's FSRS stability, as `../core-package/knowledge/schedule.md`
  gives.
- **A lapsed certification names the condition that fell short.** A lapsed
  certification still counts as earned for the certifications needing it.
- **A press in the conditions aims the focus at the certification.** The next
  queue then serves the certification's scope and every prerequisite group,
  unmet prerequisites first. `../core-package/knowledge/queues.md` gives the
  focus.
- **The focus panel then dates when the certification is earned.** The date
  waits for coverage and for retention, as
  `../core-package/knowledge/projections.md` gives.
- **The exam's press reads only once the other three conditions hold.** The
  press starts the certification's exam, and the web names the certification
  with `?cert=` on the exam's page.

## 3. A level exam's choices

- **A level exam samples every open group at one level**, and the choices
  name the module, the level and the size.
  `../web-app/pages/knowledge/exam/level-exam.md` draws them.
- **The choices open on the focus.** The module is the focus's module, and the
  level is a certification focus's level. Associate stands where no focus
  names a level. A focus aimed on the phone opens the same exam on the web.
- **The size field writes the exam size**, the `exam_size` setting, shortly
  after typing stops. The settings page writes the same setting, which
  `account.md` follows. The size stands for every later exam.
- **A paused module offers no level exam unless the user names it**, as
  `../core-package/knowledge/queues.md` gives under Module status.

## 4. Running the exam

- **`certifications` draws the exam's sample at its start.** The exam is a
  fixed sample from one scope at one level. An open question is never
  sampled, since its grade is the user's own report.
- **`answering` runs the exam one question at a time, with no feedback until
  the end.** The bar names the question count, and the page reads no verdict
  per question. `../web-app/pages/knowledge/queue/asking.md` draws the page.
- **The exam stores its answers together at its end.** An exam stopped before
  its last question is stored as not passed.
- **An exam in a closed tab or a killed app leaves no record.** A web reload
  returns to the exam's choices, since a second draw would be a different
  exam.
- **The exam's answers carry no measure, so the schedule reads them.** Each
  answer moves its question's state as a queue's answer does. A baseline
  test's answers differ, as `../core-package/knowledge/baseline-tests.md`
  gives.

## 5. The result

- **The summary names whether the exam passed**, and lists every answer. A
  certification's exam also names the certification it was for.
  `../web-app/pages/knowledge/queue/stopped.md` draws the summary.
- **A passed certification exam earns the certification.** The exam's press
  read only once the other three conditions held. The cell then reads as
  earned.
- **A failed certification exam leaves the cell ready for its exam.** The
  user may take the exam again from the conditions.
- **A level exam earns no certification.** A level exam's result is the
  summary and its stint.
- **A certification lapses later when coverage or retention falls short.**
  `certifications` derives the lapse from the log on every read.

## Where the web and the phone differ

`../core-package/screens.md` marks an exam and its results `by platform`, and
gives the reason.

- **The web runs an exam on its own page, and the phone on the quiz screen.**
  The web's exam page holds its sample in memory, so a reload returns to the
  choices without discarding a record. The phone has no reload, and its quiz
  screen runs every queue and exam.
- **The web opens a certification's conditions in a dialog, and the phone in
  a sheet.** The conditions and the presses are the same on both clients.

## What each step stores, and what reads it

`knowledge-sync` stores each line the client sends, as
`../api/knowledge-sync.md` gives. The engine translates each exam's session
name at its edge.

| Step | Stores | Read later by |
|---|---|---|
| The focus press | a focus, in `focuses` | the next queue; the exam's opening choices; the focus panel's date |
| The size field | a setting change, `exam_size` | every later exam's sample; the settings page |
| Each exam answer, at the end | an answer, in `answers` | `knowledge-schedule`, for the question's state; `certifications`, for coverage and retention; the queues |
| The exam's end | a stint of mode `exam`, at its level | the summary on the stop |
| A certification exam's end | a certification exam, in `certification_exams` | `certifications`, for the exam condition; the certifications page and the home |

## Open questions

- **Which score passes an exam?** `certifications.md` says an exam is passed
  and gives no share. The code's default is four fifths of the sample, with
  every question answered.
- **Does a lapsed certification need a new exam?** The doc says a lapse
  returns the certification to needing a refresh. No doc says whether
  restoring coverage and retention is enough, or whether a new exam is
  needed.
- **Does a level exam feed any later read?** A level exam stores a stint and
  earns no certification. No doc names a later read of that stint beyond the
  summary.
