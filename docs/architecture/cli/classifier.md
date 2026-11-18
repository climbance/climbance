# Classifier

The classifier is the model call reading an attempt's or a solution's code for
the techniques it used. It writes the solution claims, and the machine attempt
claims where no user claimed. `../api/attempt-claims.md` gives the attempt
claim record and which claim stands.

## Solution claims

A solution claim names which techniques a solution used. It is
product-owned and global, as the solution is.

- **A solution claim is its own record, not an attempt claim.** A claim is
  testimony about the user's own attempt, and is private. A solution claim is
  a verdict about code the engine wrote, and ships with the corpus. One record
  type for both would also make the fallback a fold over records of the type it
  falls back for.
- **The candidates are the whole vocabulary**, where an attempt is classified
  against the problem's own techniques. A problem's techniques are derived
  from these claims, so constraining a solution claim by them is circular.
- **One classifier writes two records.** The prompt, the transport and the
  staleness rule are shared with the attempt classifier. Two prompts asking
  one question would drift, and neither score would compare with the other.
- **A solution claim is a machine record like any other**: provenance whole,
  staleness keyed on the prompt hash of what was sent, and re-derivable at any
  time. A claim carries one problem's criteria, and a solution claim carries
  the whole vocabulary's, so any criteria edit re-reads every canonical.
- **Two writers, and the user's stands first**, as a claim resolves. A user
  reading adjudicates rather than testifies: nobody sat for a canonical, so the
  user's reading is of code they did not produce. The user's solution claim
  stands all the same, and it is the reference a configuration is scored
  against.

## Attempt claims

- **The classifier is prompted, not trained.** Public corpora tag problems
  rather than solutions, so a model trained on them predicts the fallback
  instead of improving on it, and nobody has labelled what a given solution did
  because doing so means reading it. Reading a solution is semantic work:
  two-pointers and sliding-window differ in their invariant rather than their
  syntax, backtracking is depth-first search plus an undo, and greedy is a
  property of why a choice is correct rather than a construct. A scan of imports
  and keywords is weakest exactly where the claim is worth making.
- **Showing the classifier anything besides the code is deferred.** The code
  is the subject and stays. A measured comparison decides whether the problem's
  canonicals or the candidates' templates improve a machine claim.
- **A richer prompt can change the question rather than the answer.** Shown a
  problem's canonicals, a classifier can report which canonical the attempt
  resembles instead of which techniques its code used. Those are two different
  labels, and the user's claims were made against the second label. A
  configuration that moves the question is not comparable to one that answers
  it better.
- **A verdict naming no candidate is a machine claim, and is stored.** The
  verdict is evidence about the code rather than an absence of it, and an
  unstored verdict would be re-read by every later run. A reply cut short by the
  token cap also names nothing and is stored for the same reason, but that reply
  is a fact about the configuration instead. The call's `stop_reason` separates
  a decline from a cut-short reply, and the report counts them apart.
- **A machine claim on a hand-claimed attempt is scored, never a candidate.**
  Such a claim never stands and never reaches the board. It exists to be
  scored. Storing the machine claim makes an eval a dataset rather than a run,
  and a
  second configuration is then paid for only where it has not read. The
  classifier still skips such attempts, but only to save a call whose verdict
  could never stand.

## Scoring a configuration

- **A claim is scored against the user's own**, per technique rather than
  overall, by set equality rather than overlap. The board is per technique, so
  a classifier that over-claims one code skews the board, and a claim naming
  every candidate decides nothing while scoring well on a metric that only asks
  whether the right code appears. Set equality compounds a per-candidate
  error: a classifier right on 95% of candidates scores 87% over three.
- **How often a claim names every candidate is reported beside the score.**
  Claiming inclusively removes the reason to withhold a code, so a claim fails
  by naming all of them. A claim naming every candidate is the fallback, and it
  agrees with the user's claim whenever the fallback is right. Set equality
  cannot catch that.
- **One list of columns serves whichever renderer prints a score.** A metric
  added to one renderer and not the other prints a number that stopped being
  true.
- **The eval set holds one attempt per problem**, the latest attempt carrying
  code, since a retry asks the identical question and a repeat would measure
  one decision twice. The drill loop still asks about every attempt of a
  sitting, where the answer costs a keystroke.
- **A decline is scored all the same.** A decline asserts that none of these
  candidates apply, so a user claim naming one is a miss against every
  technique the user named. Unscored, declining would pay: each decline would
  leave a smaller denominator and a better share over it. Only an attempt
  nothing read stays unscored, and the count of declines prints beside the
  share.
