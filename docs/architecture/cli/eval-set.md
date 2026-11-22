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

## The shared scorer

The shared scorer is `climb.scorer`: the code scoring a model's verdicts against
labels, an item at a time and a category per row. The classifier's score runs
through it, an attempt per item and a technique per category. The diagnosis
call's score runs through it too, an attempt or a labelled mutant per item and
the implied cause per category. The matcher is to run through it next.

- **One scorer serves every model eval.** A score written per eval reports its
  own shares over its own denominators, and two such scores cannot be compared.
- **The scorer knows items, categories and labels, and no domain record.** It
  sits under every package it serves, so the diagnosis call can use it without
  importing the classifier's code.
- **Each row reports both directions.** `missed` counts a labelled category the
  model did not name, and `over` counts a category the model named without the
  label. A score reporting only misses cannot show a category the model names
  too readily.
- **Every share the scorer prints carries its 95% Wilson interval**, as
  `50% [9–91%]`. A share over a small denominator reads as a finding without
  one. The Wilson interval is used because the normal approximation collapses
  to a point at 0 of n and n of n.

## The spot check

A judge is a model call whose verdicts have no labels to be scored against,
such as a call naming each review finding `real` or `false`. The judge's
precision is measured by hand on a sample of its verdicts. `climb.scorer.spot`
draws the sample and reads the author's marks back.

- **`climb spot draw` reads a judge's verdicts as JSON lines and prints a
  sheet.** Each line names an id, a kind and a text. Taking a file keeps the
  spot check free of any domain record, so a judge outside the engine is
  checked by the same command.
- **A text of one line prints beside its mark, and a longer one prints
  indented below it.** A diagnosis's text is a statement and code, and code
  joined onto one line cannot be read. `climb spot read` reads only unindented
  lines, so a text line never counts as a mark or a heading.
- **The draw is per verdict kind, 20 of each by default.** A judge naming one
  kind thirteen times as often as the other would leave the rare kind a
  handful of lines in one pooled sample.
- **The seed is fixed and printed on the sheet.** The same seed draws the same
  lines from the same verdicts in any order, so a marked sheet can be checked
  against a fresh draw.
- **`climb spot read` reports each kind's precision over the marked lines.**
  An unmarked line is left out of the denominator and counted apart, and a mark
  other than `y` or `n` is refused. A typo counted as unmarked would shrink the
  denominator without notice.
- **Each kind's heading carries its population, the verdicts of that kind the
  sample was drawn from.** The share is an estimate for that population, and
  20 lines of 2,672 say less than 20 of 210.
