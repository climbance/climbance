# Template schedule

Each template's memory, for one user, is FSRS-6, replayed from the template's
reviews. One curve then decides when a template's spaced check opens, when the
check is owed, and when a graduated template is due again.

## Reviews

- **A template's state is replayed from its reviews in time order**, as a
  question's is from its answers in `../core-package/knowledge/schedule.md`. The
  state is derived on every read and never stored.
- **A review is a recall attempt of the template, or a sitting on a problem
  whose `target_template_id` names the template.** `../flows.md` `## A
  template's reviews` lists which sittings count.
- **Each recall attempt becomes a rating.** A pass with no hint rates Good, a
  pass after the notes rates Hard, and a failed recall rates Again. A pass
  after the form hint rates Again too, since typing back a form just read
  recalls nothing.
- **Each sitting becomes a rating.** A solve on the first submission rates
  Good, a solve after a failed submission rates Hard, and an unsolved sitting
  rates Again. Easy is never used. The rating reads the attempts through the
  first solve.
- **The ladder's sittings are reviews.** A rung solved with the card in view
  is a warm review, and FSRS gives a first review a short stability. The last
  review before the check is therefore the point the check is measured from.
- **Recall probability is FSRS's retrievability**: the chance, read from the
  replay, that the user still reproduces the form at a given moment. It
  counts whole days since the last review, as py-fsrs does, so it falls once
  a day.

## The spaced check

- **The spaced check opens when a template's recall probability falls to
  0.89, and is owed once it falls to 0.84.** At the default parameters, after
  one Good review, these are day 3 and day 5. The check tests whether the form
  survived, so it sits later than the due time a maintaining review reads.
- **The check never opens within three days of the template's last review.**
  A Hard review leaves a stability of 1.3 days, and the band alone would open
  the check on day 1.7. Recall probability does not model how warm a form
  still is the day after practice.
- **A check passed after it was owed still counts.** A pass at lower recall
  probability is stronger evidence that the form was kept. Owed orders the
  work and freezes new card starts, as `../flows.md` gives the pick.
- **A failed check is a review rated Again.** FSRS relearning shortens the
  stability, and the window is read again from the new state. The card stays
  consolidating.
- **A graduated template is due at desired retention 0.9**, FSRS's own due
  time. An overdue template freezes nothing, and the pick serves the lowest
  recall probability first.
- **A review rated Again on a graduated card's template lapses the card.** A
  review rated Hard shortens the next interval and leaves the card graduated.

## Settings

- **The settings are constants in code, and a change replays every
  template.** No state is stored, so new settings move every due time with no
  migration. Each stored prediction names the settings it was made under, so
  a calibration compares it with the model that made it.
- **The template settings stay on the engine.** The question settings reach
  both clients in the snapshot. The template schedule runs on the server
  alone, so changing it ships no snapshot and regenerates no fixture.
- **The settings start equal to the questions'**: the FSRS-6 default
  parameters, desired retention 0.9, learning steps of 1 and 10 minutes, a
  relearning step of 10 minutes, and fuzzing off.
  `../core-package/knowledge/schedule.md` gives the reason for each.

Deferred, since only use answers each:

- The band and the floor beyond their starting values. They move on what the
  stored predictions measure against the outcomes.
- A desired retention for templates apart from questions. The default
  parameters were fitted on flashcards, and after three Good reviews their
  intervals reach 14, 57 and 196 days.
- Parameters fitted per user, once one user's log holds enough reviews.
- How a sitting's elapsed time enters its rating.
- The check of a recallable template no review has reached when its card
  turns consolidating.
