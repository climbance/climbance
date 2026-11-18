# Lessons

A lesson is a short text teaching one or more groups, read before their new
questions.

- **A lesson names the groups it teaches and what it needs**: a group done, or
  another lesson read. A lesson unlocks once its needs hold and every group
  it teaches is open.
- **A lesson is read or not, by the user's latest mark.** A mark can reset a
  read lesson.
- **A lesson holds its new questions back once its pretest is spent.** The
  pretest counts the lesson's questions a user may meet before reading it,
  two by default. The lesson's unseen questions then wait until it is read.
- **A taken baseline test spends the pretest of every lesson teaching its
  topic.** The baseline test already asks the user about the topic before any
  teaching, and a pretest serves that purpose alone. Without this rule, a
  topic whose subtopic has two lessons served four new questions after the
  test before its first lesson. A skipped test answered nothing, so it spends
  no pretest.
- **A question names its lesson, or takes the lessons teaching its group.** A
  question with several lessons waits while any one holds it.
- **A queue offers a lesson where it would serve a new question**, after the
  reviews, and each lesson at most once per queue. Once today's new questions
  are spent, no lesson is offered, since no new question could follow it.
- **A question comes between two lessons wherever one is left to serve.** Two
  lesson stops in a row break the queue's flow. A queue with nothing but
  lessons left still offers them one after another.
