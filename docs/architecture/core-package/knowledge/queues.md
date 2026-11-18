# Queues

A queue picks each question at the moment it is needed, from what is servable
then. The user stops a queue at any time, and a queue ends when nothing is
left to serve.

## Order

- **A queue orders the questions it serves weak, due, unseen, learning,
  retained.** Ties break at random.
- **A step due within 20 minutes is served early** when nothing else is
  servable, so a one-minute step does not end the queue.
- **A client counts such steps apart from the due reviews**, and marks a
  question served early. A due count of zero then never sits beside a queue
  that keeps serving questions.

## The daily limit

- **New questions are limited per day, and reviews never are.** The limit
  counts questions first answered today across every device, ten by default.
  The day starts at 04:00 local time, when almost every user is asleep.
- **Each device reads the day in its own time zone.** Midnight UTC falls in a
  US evening, the hours a user practises in. Two devices in different time
  zones disagree on today's new questions and raises for a few hours, and
  that is accepted. A user's time zone as a record of the log is deferred
  until a user practises across time zones.
- **The user can raise today's limit, five at a time**, from Home or inside the
  next and filtered queues. The raise ends when the day does, and the daily
  setting stands again the next day.
- **The daily limit is a setting, and today's raise is a record of its
  own.** `## Settings` gives how a setting is stored. A limit kept per device
  would have the phone and the web offer different counts of new questions
  on the same day.
- **Today's raise is the sum of the raises given since the day began.** Two
  devices raising on one day then add up rather than overwrite each other.

## The three queues

- **The next queue serves the reviews, then the frontier's new questions.**
  Over every active module, the modules take turns.
- **The review queue serves the weak and due questions alone**, at every level,
  locked or not. It serves no new question.
- **The filtered queue serves chosen questions from one module**: by topic,
  subtopic, level, kind, weak alone, or weak and due alone. Locks do not
  apply. After the servable ones, it serves learning and retained questions
  it has not yet asked.
- **Stopping a queue stores a stint**: the queue's mode, how many questions
  were answered, and the score.
- **A filtered queue starts from a press on the module's groups.** The press
  names the module, the topic, the subtopic or one group, and the user adds
  the level, the kind and the due flag for that queue alone.
- **Starting a filtered queue moves no focus.** The focus aims the next
  queue, and one drill on a subtopic would otherwise retarget it.
- **A filtered queue's choices are stored nowhere.** Each narrows one queue,
  and a record of them would change at most starts. The web carries them in
  the queue's URL, which no other device reads.

## Exams

- **A level exam opens on the focus's module**, and on a certification
  focus's level. Associate stands where no focus names a level. The focus
  is a record of the log, so the phone and the web open the same exam.
- **The exam size is a setting**, as `## Settings` gives.

## Settings

- **A study setting is a name and a whole number**, and the latest record of
  each name stands across every device. A setting kept per device would
  have the phone and the web serve differently on the same day.
- **Two settings exist.** `new_per_day` is the daily limit on new
  questions, from 0 to 200, ten by default. `exam_size` counts the questions
  an exam samples, from 1 to 500, forty by default.
- **One table holds every setting.** A further setting that is a whole number
  adds a name and its range, and no table.
- **A setting outside its range is refused**, by the engine and by the
  database's own check. An exam sampling no question would be no exam.

## The focus

The user can aim the next queue at one module, one topic, one subtopic or one
certification.

- **The latest focus record stands**, across every device. A record naming no
  module clears the focus.
- **A relaxed focus serves every servable review first**, then the focus's new
  questions. A strict focus serves the focus's own reviews alone, and counts
  the rest as waiting outside it.
- **A focus degrades with the content.** An unknown module means no focus, an
  unknown topic keeps the module, and an unknown subtopic keeps the topic.
  A client degrades a stored focus as it reads it, once the content moved. A
  focus line naming content the store does not hold is refused at the sync,
  so no degraded focus is written to the log.
- **A certification focus covers its scope and every prerequisite group**, so
  the unmet prerequisites come first.

## Module status

- **A module is active, paused or archived**, by the user's latest status
  record. The status is the user's, never the module's.
- **A paused module leaves the next queue, the review queue and exams**,
  unless the user names it. The filtered queue still offers it.
- **An archived module is also hidden everywhere** but the module list. Its
  answers stay, and restoring it loses nothing.

## Module order

- **The user orders the modules, and the latest order record stands** across
  every device. An order kept per device would list the modules differently
  on the phone and the web.
- **A module the order does not name follows the named ones**, in the order
  the seed gives. A module seeded after the user ordered the rest still
  lists, at the end.
- **The order changes no queue.** The next queue's modules take turns
  whatever the order says.
