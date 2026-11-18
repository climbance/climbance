# Self-labels

The user's own verdict on why an attempt went the way it did. A self-label is
reported, not inferred. It is its own record rather than a field on the
attempt, for the same reason a claim is.

- **A self-label is only ever the user's.** A machine answering the same
  question produces a `Diagnosis`. Self-label and diagnosis are separate
  records because the eval scores one against the other, and a shared record
  read latest-first would let the machine supersede the evidence it is measured
  against.
- **One label per attempt**, and the latest wins on read.
- **The drill loop is the only writer.** The question is asked at the moment of
  solving, and nothing else is there to ask it.
- **A label cannot be given later, where a claim can.** The evidence for a
  claim is the code, which does not decay. The evidence for a label is recall,
  which does decay. A `Diagnosis` reads what survives months on: a timeout, a
  compile error. A label recalled that late is either invention or the
  classifier's own input handed back as evidence against it.

## What each mode selects

`FailureMode` is the vocabulary a self-label names a mode from. A mode says why
the attempt went the way it did. A diagnosis names a cause instead, as
`../cli/diagnoser.md` gives.

### The modes

- **`speed` is the time the solver took, and never the solution's
  complexity.** The solver reached the answer, and reached it more slowly than
  they judge they should have. No record holds the bar that judgement is made
  against, so the loop asks the solver for it.
- **A timeout is not labelled `speed`.** The attempt's verification stores
  `timed out` on each case the submission exceeded the cap on, so a label
  repeating that outcome answers a question the record already settled. A
  timeout is labelled by its cause, as any other failure is.
- **`gap` is a form the solver did not hold.** Reading the card would have
  supplied the form, and the solver had not read it or had not kept it.
- **`rust` is a form the solver held and did not reach.** The trigger went
  unrecognised, or the form came back in pieces. A solver who recognises the
  approach the moment they read a solution held the form.
- **The solver reports which of the two, and no record decides it.** The log
  holds the attempts made since the log began, and a solver learned techniques
  before that. A first sitting on a technique is therefore the same record
  whether the solver has practised the technique for years or has never met it.
- **The two modes name different remedies.** A solver who does not hold the
  form reads the card and solves its ladder. A solver who holds the form and
  did not reach it runs the recall trainer. One mode over both would leave the
  scheduler two remedies and no way to pick between them.
- **`syntax` is a slip in code the solver could have written correctly.** The
  form came and the approach was right, and the submission failed on how the
  code was typed: a name misspelled, a bound written the wrong way round, a
  method called with its arguments swapped.
- **A slip inside the form is `rust`.** A binary search whose bound moves the
  wrong way is the form coming back in pieces, where the same mistake in a loop
  the solver wrote from scratch is a slip. The solver reports which of the two
  the mistake sat in.
- **`none` is an attempt that went the way it should.** The form came, the code
  ran, and the solver reached the answer in the time they expected. `none` is a
  verdict the solver states rather than an absence of one.

### Which modes an attempt takes

- **A solved attempt takes `speed` or `none`, and an unsolved attempt takes
  `gap`, `rust` or `syntax`.** An attempt that returned no answer failed for a
  reason, and how long the solver took is not that reason. A submission that
  passed reached the form and carries no slip.
- **An attempt that crashed on every case is asked for no label.** The code
  reached no answer, so no mode is more than a guess, and the traceback each
  case result carries already names what raised. The loop asks about that
  attempt's claim and offers no mode.
- **A skipped label writes no record.** The solver who skips the question
  asserts nothing, so the attempt stays unlabelled and the board counts it
  under no mode.
- **A skip is never stored as `none`.** `none` asserts that the attempt went
  the way it should, and a board counting a skipped attempt under `none` would
  report a clean pass the solver never claimed.
- **A self-label needs no `declined`, where a claim carries one.** A claim
  declines against a list of candidate techniques, and that decline asserts
  that no candidate on the list applies. A mode names why the attempt went the
  way it did, and `none` already carries the verdict that nothing went wrong.
- **An attempt asked and skipped reads as an attempt the loop never asked**,
  and that cost is accepted. Every attempt written before 2026-09-21 carries no
  label, so a reader counting labels reads a denominator of labelled attempts
  rather than a rate of answers.
