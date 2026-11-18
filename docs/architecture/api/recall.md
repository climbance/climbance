# Recall

A recall attempt is one template reproduced from memory, with the hints taken.
The recall runs what the user typed against the template's cases, and stores
the recall attempt.

- **A recall attempt is not an `Attempt`.** No problem and no submission. No
  field keys a recall attempt to an attempt, so it is its own record, keyed to
  a card and a template.
- **The unit is the template, not the card.** A card's forms are learned and
  lost separately, and a card-level number would average them together and show
  neither.
- **A hinted pass is not a pass.** Which hints were taken before succeeding is
  part of the record. Without that field, a decaying form scores the same as a
  fluent one.
- **Recall fluency is not solving fluency.** Reproducing a form cold is not
  recognising it unprompted, so recall fluency never stands in for mastery. The
  gap between recall fluency and solving fluency is the false fluency that
  blocked practice trains.
