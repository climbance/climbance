# Log terms

Words this project gives its own meaning for one user's log: attempts,
sittings, claims, labels, card runs, recalls and mastery. Every file in
`docs/architecture/` uses them without redefining them.

## Sittings and attempts

- **Attempt**: a user's solution to a problem, successful or failed.
- **Attempt verification**: executing an attempt's code against its problem's
  cases. An `AttemptVerification` record stores one run, and is private to the
  user where a solution's `Verification` is product data.
- **Sitting**: one session on one problem in the drill loop, timed or not,
  from the first clock press or submission. It may mint several attempts, and
  each of them carries the sitting's id. The record is revised while the
  sitting runs and kept after the sitting ends.
- **Pause**: an interval a sitting's clock is stopped for. The elapsed time a
  sitting reports excludes every pause.
- **Clock preference**: whether a sitting's clock starts by itself when the
  statement is served. The user's last press on a clock sets it, and the
  browser keeps it.
- **Drill loop**: the practice flow: pick a technique and a problem, read the
  card, solve, then answer the claim and the label.
- **Run fault**: a user's run the sandbox answered no result for, stored so
  the run caps count it.
- **Retirement request**: a user's request that a problem be retired, naming
  a retirement reason and a note. The author reads it and retires the problem
  by hand.
- **Feedback**: a user's note to the author about the engine, naming the
  client and the page it was sent from. The author reads it with `climb
  feedback`.

## Claims

- **Claim**: a record naming the techniques a piece of code used, by a named
  writer. Latest wins, and the user's stands over the classifier's.
- **Attempt claim**: a claim about the user's own attempt. Private, and what
  the board counts.
- **Classifier**: the model call reading an attempt's or a solution's code for
  the techniques it used. As a `source` value on any record, `classifier` means
  a model wrote it, whichever call.
- **Decline**: a claim stating that none of the candidates apply. Distinct
  from an empty claim, which answers nothing.
- **Fallback**: the problem's own techniques, answering an attempt no claim
  covers.
- **Eval set**: the hand-claimed attempts a classifier configuration is
  scored against.
- **Adjudication**: resolving each divergence between the user's blind claims
  and a frontier model's claims, by editing the criterion or the claim.

## Labels and diagnoses

- **Labelled mutant**: a mutant of a template's form, read from a flawed
  judgement item or a key-line item's wrong choice, labelled `rust` and named
  by its operator. The diagnosis call is scored against the labelled mutants.
- **Self-label**: the user's own verdict on why an attempt went the way it
  did.
- **Diagnosis**: the machine's verdict on why an attempt failed, naming a
  cause. A `Diagnosis` record stores it.
- **Diagnosis call**: the model call reading a failed attempt or a labelled
  mutant and naming its cause.
- **Tool**: a piece of evidence the diagnosis call is given beyond its
  baseline, such as the first case the solution failed. Each is scored by the
  difference it makes.
- **Mutant diagnosis**: the diagnosis call's verdict on a labelled mutant. A
  `MutantDiagnosis` record stores it, keyed to the mutant.
- **Cause**: where a diagnosis places the fault: `slip`, outside the form the
  solver held, or `form`, in the form itself.
- **Failure mode**: why an attempt went the way it did, as one of five words a
  self-label names. `speed` is the time the solver took,
  and `rust` a form the solver held and did not reach. `gap` is a form the
  solver did not hold, `syntax` a slip in code the solver could have written
  correctly, and `none` an attempt that went the way it should.

## Card runs and the pick

- **Card run**: the record that a card was started, and the probes it was
  given.
- **Pick**: the one problem or recall the board serves, read from FSRS,
  mastery and the cards' states.
- **Prediction**: what a pick expected as the user took it, from FSRS and from
  mastery, each with the settings that made it. A `Prediction` record stores
  one.
- **In flight**: a card acquiring, or consolidating with its spaced check open
  or owed. The pick offers a new card only while fewer than two are in flight.
- **Card state**: how far one user's study of one card has gone: not started,
  acquiring, consolidating, graduated or lapsed. Derived from the log, never
  stored.
- **Acquiring**: the card state of a started card with a required rung not
  solved since the run began.
- **Consolidating**: the card state once every required rung is solved, until
  the card graduates.
- **Graduated**: the card state once the graduation rule held, until a lapse.
  A graduated card is done.
- **Lapsed**: the card state of a graduated card one of whose templates has
  since had a review rated Again.

## Recall and short exercises

- **Recall attempt**: one template reproduced from memory, with the hints
  taken.
- **Recall probability**: FSRS's retrievability of one template for one user
  at a moment, read from the replay of its reviews.
- **Spaced check**: the recall a consolidating card's template waits for. It
  opens and falls owed at two recall probabilities, as
  `../../api/template-schedule.md` gives.
- **Short exercise**: a question about code answered in seconds with no
  typing, such as judging a solution. Each kind is a record kind of its own.
- **Judgement item**: a template's form, clean or carrying one mutant that
  fails a case, served by the judging exercise. Product data.
- **Judgement**: one user's answer to a judgement item: clean or flawed, and
  the tapped line where flawed.
- **Key-line item**: a template's form with one line blanked, and the choices
  for that line: the form's own line and mutants of it that fail a case,
  served by the key-line exercise. Product data.
- **Fill**: one user's answer to a key-line item: the choice the user picked.
- **Review**: one check that a user still holds a template's form or a
  question's fact. An answer to a seen question is a review of it, and so is
  a template's recall attempt or a sitting written for the template.

## Mastery

- **Board**: the per-technique view of progress, derived from attempts and
  claims. Never stored.
- **Mastery**: how well a user knows one technique, in three parts:
  recognition, execution and knowledge. Computed from the log on every read,
  never stored.
- **Recognition**: seeing that a problem needs a technique when nobody named
  it. Counted from recognition drills alone.
- **Execution**: writing a correct solution once the technique is known.
  Counted from sittings.
- **Knowledge**: recalling the facts a technique rests on. Counted from
  answers to the questions the technique carries.
- **Recognition drill**: a problem shown without its technique, where the user
  describes the approach in words and runs no code.
- **Framing judge**: the model call grading a recognition drill's description
  against the problem's canonicals.
