# Certifications and exams

A certification is one scope, a topic or a whole module, at one level. A user
earns it on coverage, retention, an exam and its prerequisites.

- **A certification is a scope at a level**: one topic, or the whole module.
  Every scope at every level is one. A module's certification file holds the
  defaults and the exceptions, never the list.
- **Certifications form a graph derived from the prerequisite graph**, never
  stored. A topic's level needs its level below and every topic its subtopics
  need. The module's level needs every topic at that level.
- **A certification is earned on four conditions**: its prerequisites are
  earned, every subtopic's group is covered, enough questions are retained,
  and its exam was passed.
- **Coverage is the passed share of each group.** Retention is the share of
  the scope's questions at that level whose stability reaches a set number of
  days.
- **A certification lapses back to needing a refresh** when coverage or
  retention falls short after its exam. A lapsed certification still counts
  as earned for the ones that need it, so one lapse does not cascade.
- **An exam is a fixed sample from a scope at one level**, with no feedback
  until the end. A level exam samples every open group at one level instead.
  Each exam answer is stored as an answer, and the exam as a stint.
- **An exam is offered only once everything else in its certification
  holds.** A certification exam passed is stored as its own record.
