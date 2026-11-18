# Predictions

What a pick expected, stored as the user takes it. A `Prediction` holds two
models' readings of one act, written before the act has an outcome.

- **A prediction is written when the user opens the pick's act**: the recall,
  the sitting or the card's start. A pick the board served and the user never
  opened predicts nothing an outcome can be read against.
- **A prediction is written once per act.** A second take before any outcome
  returns the first prediction, so a double press or a reload writes no
  second record.
- **A prediction is refused once the board's pick has moved.** The client
  names the pick it showed, and the engine stores nothing when the pick it
  computes now differs, since the prediction would concern an act the schedule
  did not choose.
- **The record holds the pick and both readings**: its rank, its act, its
  card, its template and problem where it names them, FSRS's recall
  probability for the template, and the technique's execution reading.
- **Each reading names the settings that made it**, as a hash of those
  settings: `fsrs_settings` for the template schedule, `execution_settings`
  for the execution scores and their evidence bound. A calibration then
  compares each prediction with the model that made it, after the settings
  move.
- **The outcome is not stored on the prediction.** The outcome is the act's
  next result after the prediction: the template's next review, an attempt on
  the problem, or the card's run. Reading it later keeps the record
  append-only and written blind to the result.
- **A prediction has an empty `arm` field**, for the policy that chose the
  pick. A comparison of the scheduler against a simpler policy would fill it.
  No such comparison is planned, since one user's techniques are too few to
  separate two policies, and the empty field costs nothing.
- **Predictions are private to the user**, exported and erased with the rest
  of the log.

Deferred, since only use answers each:

- How a calibration groups predictions, and how many it needs before a number
  is read.
