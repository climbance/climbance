# Eval set

The eval set is the reference the classifier is scored against. One writer's
blind claims cap at that writer's own consistency. The reference is therefore
a set two writers reached: the user's blind pass, a frontier model reading the
same attempts, and every divergence resolved by hand. `classifier.md` gives
the classifier the set scores.

## Adjudicating the eval set

1. The blind user claims stand as pass one. No claim is added to them while a
   machine claim is in view.
2. The frontier model reads those same attempts as a scored configuration. Its
   claims are machine claims, stored and never standing.
3. Each divergence is reviewed alone and resolved one of two ways: the
   criterion is edited, or the user's claim is.
4. A criteria edit changes the prompt hash of the attempts it reaches, and the
   frontier reads those again.
5. The steps repeat until the frontier disagrees with nothing, which is the
   stopping signal.
6. The set is frozen, and the cheap classifiers are scored against it.

- **The adjudicator is never the classifier.** Its number on this set is 100%
  by construction, since the gold is its own labels wherever the user did not
  overturn them. That number says adjudication finished, not that the model
  reads well.
- **The model is there for consistency.** The model applies the same rule at
  the sixtieth attempt as at the first, where a human drifts across one
  sitting. Consistency is not correctness, so every divergence is decided by
  hand rather than taken.
- **The blind pass keeps the reference independent.** Reviewing a proposed
  label is easier and more permissive than producing one. A claim made with a
  machine claim in view therefore records what it saw, and never stands in for
  pass one.
- **Which way the divergences went is the check on the process.** Mostly claim
  edits means the eval set is becoming a copy of one model's claims. A real
  share of criteria edits means the criteria are being corrected instead.
- **The set cannot show a classifier that is right where the frontier was
  wrong.** Such a case is recorded as an error, and the attempts both writers
  got wrong the same way are never detected. That cost of a fixed reference is
  accepted.
