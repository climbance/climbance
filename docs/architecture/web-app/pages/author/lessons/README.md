# The lessons page

The page at `/author/lessons`, in the author area: one module's lessons,
each opened as a learner reads it. `../README.md` gives who reaches it, and
`## The content browser` there gives the rules this page shares with the other
browser pages.

[`lessons.md`](lessons.md) draws the page at low fidelity.

- **The lessons are read from the snapshot**, as the questions page reads its
  questions. The lessons page then draws each lesson with the component the
  learner's lesson page uses, from the same record.
- **The page reads one module at a time**, named by `?module=`, and filters by
  topic and subtopic as `?topic=` and `?sub=`. A lesson teaches one or more
  groups, so a lesson is listed under each subtopic a group it teaches sits in.
- **A row shows the lesson before it is opened**: its slug, its title, its
  reading time, its pretest, the groups it teaches, and how many questions
  those groups hold. A lesson teaching many questions in few minutes reads as
  one to open first.
- **A row names the lessons it needs**, each a link to that lesson's row, and
  every lesson that needs it. The author then reads the order a learner meets
  the lessons in.
- **An opened row draws the lesson's text whole**, with its diagrams and its
  links. A press offers no Mark read, since a mark given in review records a
  reading the author did not do as a learner.
- **Under the lesson, the row lists the questions of the groups it teaches**,
  each a link to the question's row on the questions page. A question tests a
  concept on an example the lesson does not show, so the author checks the
  lesson against its questions here.
