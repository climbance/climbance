# Attempt claims

Which techniques an attempt used. Per-technique progress is measured from this.
A claim is open to revision, so it is its own record rather than a field on the
attempt.

`../cli/classifier.md` gives how the classifier writes its claims and how a
configuration is scored against the user's.

- **Attribution is resolved, not required.** An attempt's techniques are the
  claim that stands, if one exists, and otherwise the problem's techniques.
  Resolution happens on read and is never stored, so re-deriving a problem's
  techniques reaches every unclaimed attempt.
- **The fallback answers a different question.** A problem's techniques say
  what solving the problem can take. A claim says what one solution did. The
  fallback over-credits techniques a canonical used incidentally, which skews
  scheduling away from the weakest ones.
- **A claim has two writers, and the user's stands first.** The drill loop
  asks at the moment of solving, and a hand pass reaches attempts no loop
  touched. A classifier fills the rest, and a later user claim corrects it.
- **The author's confidence on a claim is a level, not a float.** A judgement
  made in seconds carries no more resolution. The level is absent on every
  claim written before the loop asked for one, and a level nobody gave is not a
  low one.
- **The user's claims are an eval set and a correction path**, never training
  data. The engine trains nothing.
- **A label is invalidated by which classifier informed it, not by the fact
  that one did.** A claim made with the scored configuration's claim in view
  measures that configuration against itself. A claim adjudicated against a
  classifier that is never scored measures no configuration against itself. That
  adjudication draws the boundary. So `informed_by` names the machine claims its
  author saw, one by one, and a set of claims can be read back for either
  question: which claims a scored classifier informed, and which claims any
  classifier
  informed.
- **One claim per attempt names every technique the attempt used**, since a
  solution can use several. A later claim replaces the whole set rather than
  rewriting the earlier one.
- **An empty claim answers nothing, so the fallback stands.** The resolver
  reads a claim's *techniques* rather than its existence, so the problem's own
  techniques keep answering an attempt whose machine claim declined. A later
  decline
  supersedes an earlier claim as any machine claim does.
- **A decline is stated, never inferred from an empty set.** The user says so
  with `declined`, since the loop records nothing where they skip and emptiness
  would make a lost answer and a stated verdict one record. The classifier
  needs no flag: the classifier answers or fails, and a failure writes no
  claim. The eval set holds a correct decline, or the attempt could only leave
  the set by deletion.
- **One record for both writers, not two.** Splitting would mirror `SelfLabel`
  and `Diagnosis`, but claims already written stay in the log forever, so a
  reader carries the old shape regardless. A third record written only by the
  eval is worse: the same verdict would land in one record or the other
  depending on
  what else was claimed.
- **Every claim records its source.** A user's claim carries no provenance,
  because nothing re-derives a user's claim. A machine claim carries all of its
  provenance, and a re-derivation reads that provenance to find the stale
  claims and leave the rest. A user's claim and a machine claim count the same
  toward progress.
