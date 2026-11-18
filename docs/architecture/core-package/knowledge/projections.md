# Projections

A projection reads the user's log forward: the practice the schedule will ask
for if the user keeps answering. A projection is derived on every read and
never stored, as a question state is.

## The review forecast

- **The review forecast counts the reviews each learning day will hold**, over
  the next fourteen days. A learning day starts at 04:00 local time, as the
  daily limit's day does.
- **Each review in the forecast is assumed to pass.** The forecast replays a
  question with a Good rating at each due time, and counts the due time that
  rating sets as well. Any other assumption needs a failure rate the log has
  not measured.
- **The forecast is therefore a lower bound on the load.** A failed review adds
  a relearning step and shortens the next interval, and the forecast counts
  neither.
- **An overdue review counts on the first day.** The review is owed now, and a
  forecast dropping it would show less than the review queue serves.
- **Only questions already seen are counted.** A new question enters the load
  on the day the user first answers it, and the user chooses that day. The
  page says so under the forecast.
- **The forecast reads the modules the review queue serves.** A paused module
  and an archived one add nothing.
- **The focus does not narrow the forecast.** A strict focus defers the
  reviews outside it and removes none, so those reviews still fall due.
- **A day counts 24 hours from its start.** A shift to or from summer time
  moves one boundary of the fourteen by an hour, and that is accepted.

## When the focus is reached

The focus panel names the day the focus is projected to be reached, at two
paces side by side.

- **A focus on a module, a topic or a subtopic is reached once every group in
  it is done.** A group is done at the module's pass ratio, as
  [`schedule.md`](schedule.md) gives.
- **A certification focus is reached once the certification is earned.** A
  lapsed certification still counts, as it does for the certifications that
  need it.
- **The route reads the same rule** to aim its next target.
- **The remaining work is the new questions the focus still needs answered.**
  Each group needs its pass ratio's share passed. A question seen and not yet
  passed is taken to pass on its next review, so it takes no new question's
  place.

### The two paces

- **The first pace is the daily limit**, the `new_per_day` setting. Today's
  room is today's limit less the new questions answered today.
- **The second pace is the user's own**: the new questions first answered per
  day over the last fourteen complete learning days. A day with no answer
  counts as zero. A log younger than fourteen days is read over the days it
  holds, and a log with no complete day yet has no pace.
- **The pace counts every module.** The next queue takes its new questions
  from the focus, so a pace measured before the focus was aimed still applies.
- **Two dates are shown, because they answer different questions.** The
  limit's date says what the setting allows. The pace's date says what the
  user's practice reaches. The gap between them says which of the two is
  holding the user back.

### The dates

- **A certification's date waits for retention too.** Every review is assumed
  to pass, as in the forecast, and the date is the day enough of its questions
  reach the rule's stability. A question not yet seen is taken to be first
  answered on the day coverage is reached. The exam is taken that day.
- **The date is a lower bound.** A failed review, the time spent reading a
  lesson and a failed exam each push it later, and the projection counts none
  of them.
- **A date more than three years away is not named.** No user plans by it.

Deferred, since only use answers each:

- The retention and the exams of a certification's prerequisite
  certifications. The date counts their coverage alone.
- A forecast per module, on the module's page.
