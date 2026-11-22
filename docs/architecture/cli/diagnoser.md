# Diagnoser

Why an attempt failed, inferred rather than reported. Keyed to an attempt and
carrying provenance as any machine record does, so every attempt can be
re-diagnosed and compared.

## The cause

- **A diagnosis is the machine counterpart of a self-label, never its
  replacement.** A diagnosis and a self-label never supersede each other, and
  agreement between them is the eval. A later diagnosis is a second verdict
  rather than a correction.
- **A diagnosis names a cause, one of two: `slip` or `form`.** `slip` is a
  fault outside the form the solver held, the fault a self-label calls
  `syntax`. `form` is a fault in the form itself, the fault a self-label calls
  `gap` or `rust`.
- **A diagnosis names no failure mode, since the code cannot decide four of
  them.** Whether the solver held the form separates `gap` from `rust`, and no
  record holds that, as `../api/self-labels.md`
  `## What each mode selects` gives. `speed` and `none`
  name no fault in the code.
- **The two causes are the split mastery and the pick already read.** An
  unsolved sitting labelled `syntax` scores 0.25 and aims no pick. One
  labelled `gap` or `rust` scores 0 and aims the pick at the form. A third
  cause would name a difference no reader acts on.
- **A slip inside the form is `form`, not `slip`.** A binary search whose bound
  moves the wrong way is the form coming back in pieces, which a self-label
  calls `rust`. The call is told the problem's target template, so it can
  judge whether the fault sits inside that template's form.

## The call

- **The diagnosis call reads the failed attempt's code, its problem's
  statement and the target template's title and trigger.** A problem written
  for a technique names no template, so its call reads no form.
- **The call is shown no template's code.** A labelled mutant is the form with
  one change, so the clean form beside it would show the call the answer. Beside
  an attempt, the form's code is a diff by another name. Each is a tool, scored
  by what it adds.
- **The call reads no case either.** The first case an attempt fails is a tool
  of its own, and a call already reading it would leave that tool nothing to
  add.
- **The call is greedy, and a refusal or a reply cut short writes no
  diagnosis.** The call log keeps the request, so the cost stays readable.
- **An attempt read at the same configuration and prompt hash is not read
  again**, as a claim is not. `climb diagnose attempts` reads every failed
  attempt with code, and `--fresh` reads them all.

## Tools

- **A tool is one piece of evidence added to the call's prompt, and the
  baseline is the call with none.** The divergence tool shows the first case
  the solution failed: its arguments, the expected return, and the value
  returned, the timeout, or the error a crash raised.
- **The form-code tool shows the target template's code beside an attempt, and
  reads no labelled mutant.** A mutant is that code with one change, so the
  call would find the fault by comparing the two. Its column's mutant rows
  read `unread`, and its share is read from the self-labels alone.
- **A score column is a configuration plus a tool set.** Each verdict is
  matched on the prompt hash its item would be sent under that tool set, so a
  tool's verdicts never stand in the baseline's column. The prompt hash
  already records which tools a verdict saw, so no record names them.
- **`climb diagnose score --tool divergence` prints the baseline beside the
  tool.** The tool's gain is its column's share less the baseline's.

## Scoring

- **A diagnosis is scored through the cause each label implies.** `syntax`
  implies `slip`, and `gap`, `rust` and every labelled mutant imply `form`.
  `speed` and `none` imply no cause, so a self-label naming either scores no
  diagnosis.
- **`climb diagnose score` prints one row per label mode and no overall
  share.** The rows are `syntax`, `gap`, `rust` and the labelled mutants, and
  each `--model` is a column. A call that always says `form` would score well
  on a pool of form faults, and one share over the pool would hide that.
- **A share counts one configuration's latest verdict on each item of the
  row**, and the fraction naming the implied cause. A row the configuration
  has not read prints `unread`, so it is never mistaken for 0%.
- **Each row is scored by the shared scorer of `eval-set.md`**, and its share
  prints with its interval, as `70% [40–89%] of 10`. The per-mode rows and the
  classifier's rows then report a share the same way.
- **A row under 10 verdicts prints its count and no share.** One `syntax`
  self-label would read as 0% or 100%.
- **`climb diagnose verdicts` prints each diagnosis no self-label scores, for
  the spot check of `eval-set.md`.** It prints one JSON line per attempt: the
  attempt id, the cause as the kind, and the statement and the fenced code
  as the text. It reads one configuration's latest verdict at one tool set, as a
  score column does. An attempt labelled `speed` or `none` stays in, since
  neither mode implies a cause.
- **The labelled mutants are a row apart from the self-labels, split by
  operator.** A call can catch a reversed comparison and miss a shifted
  constant, and one mutant row would hide that.

## Labelled mutants

The diagnosis call is also scored against failures whose cause is known
before the call reads them. A labelled mutant is one such failure.

- **A labelled mutant is read from the stored items, and is itself never
  stored.** Each flawed judgement item and each wrong choice of a key-line item
  carries one mutant of a template's form and the case it fails. The items are
  never edited, so the labelled mutants re-derive the same on every read.
- **Every labelled mutant is labelled `rust`, and so implies the cause
  `form`.** A one-change mutant of a template's form is the form coming back in
  pieces, as `../api/self-labels.md` `## What each mode selects` gives for a
  slip inside the form.
- **Each labelled mutant also names the operator that wrote the change**:
  boundary, negation, arithmetic, connector, condition, constant, extremum or
  control. An item stores the change and not the operator. The change's text
  names one operator alone, and a test holds the two to each other.
- **A mutant both exercises serve is one labelled mutant.** Counting it twice
  would weigh a mistake by how many exercises show it.
- **A retired item yields no labelled mutant.** Its form is one the template
  no longer holds, so a diagnosis reading the template now would read a
  different form.
- **A labelled mutant's verdict is a `MutantDiagnosis`, keyed to the mutant.**
  A `Diagnosis` is keyed to an attempt, and a mutant is none. The record names
  the template, the form digest and the hash of the mutant's code, with the
  call that wrote it. A second configuration then pays only for the mutants it
  has not read.
- **The call reads a labelled mutant as an attempt on its template.** The task
  is the template's title, and the form is named as for an attempt.
- **`climb diagnose mutants` reads the first 20 labelled mutants of each
  operator**, and `--all` reads every one. The same mutants then answer for
  every configuration, and constant shifts, over half of the set, do not
  crowd out the other operators.
- **The labelled mutants imply `form` alone.** A score over them alone would
  reward a call that always says `form`. So the score per mode also reads the
  self-labels, and the `syntax` self-labels alone imply `slip`. On 2026-11-17
  the deployed store held one `syntax` self-label, so the `slip` side waits on
  use.
- **A labelled mutant is a template's form run against the template's cases,
  not an attempt on a problem.** The call reads a template in place of a
  statement, so a score over the labelled mutants carries over to attempts
  only in part.
- **On 2026-11-17 the local store's items gave 821 labelled mutants over 109
  templates.** 481 of them are constant shifts, 137 arithmetic, 105 negations
  and 43 boundaries, with 55 spread over the other four operators.
