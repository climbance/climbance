# The lessons page

The page at `/author/lessons`, in the author area: one module's lessons,
each opened as a learner reads it. `../README.md` gives who reaches it, and
`../browser.md` gives the grid and the dialog this page shares with the other
browser pages.

[`lessons.md`](lessons.md) draws the page at low fidelity.

- **The lessons are read from the snapshot**, as the questions page reads its
  questions. The lessons page then draws each lesson with the component the
  learner's lesson page uses, from the same record. An opened lesson makes no
  request, since the snapshot already holds its text.
- **The page reads one module at a time**, named by `?module=`, and filters by
  topic and subtopic as `?topic=` and `?sub=`. A lesson teaches one or more
  groups, and the subtopic filter keeps a lesson teaching any group in that
  subtopic.
- **A lesson reads as one row**, whatever number of subtopics its groups sit
  in. A lesson listed once per subtopic read as two lessons where it was one.
- **A row's columns are the lesson's slug, its title, the groups it teaches,
  its reading time, its pretest, and how many questions those groups hold.**
  A lesson teaching many questions in few minutes reads as one to open first,
  and the reading time and the questions sort on a press of their header.
- **The rows read in the bank's order by default**: by the topic and the
  subtopic of the first group each lesson teaches, then the lesson's
  position.
- **The dialog names the lessons the opened one needs**, each a link to that
  lesson's dialog, and every lesson that needs it. The author then reads the
  order a learner meets the lessons in.
- **The dialog draws the lesson's text whole**, with its diagrams and its
  links. A press offers no Mark read, since a mark given in review records a
  reading the author did not do as a learner.
- **Under the lesson, the dialog lists the questions of the groups it
  teaches**, each a link to the question's dialog on the questions page. A
  question tests a concept on an example the lesson does not show, so the
  author checks the lesson against its questions here.
