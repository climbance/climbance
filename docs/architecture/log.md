# The log

The user's private record: what was attempted, what it used, why it went the
way it did, the study a card run tracks, and the mastery derived from all of
it. Part of the architecture.
`README.md` is the map.

Every record here is append-only apart from the sitting, which is revised
while the sitting runs.

## Users

The engine's user, whose id every private record carries. `README.md` gives
how an account signing in is linked to a user.

- **The hosted engine starts with an empty log, the author's included.** The
  author's account is linked to a user minted at its first sign-in, as every
  account is.
- **The records written before hosting stay in the local database**, under the
  ids the terminal and the local API wrote them under. The dev login signs in as
  the user `CLIMB_DEV_LOGIN` names, and the terminal reads that user's log
  by default.
- **No record is copied from the local log to the hosted one.** The local log
  held a handful of sittings and attempts when hosting was decided. Carrying
  them over would take a copy of the log and an account linked to an id the
  engine never minted, for records nothing reads.
- **One user's log is every sitting, attempt, attempt verification, attempt
  claim, self-label and diagnosis keyed to that user**, and the calls a model
  made about the user's code.
- **The knowledge log is part of it**: the user's answers, stints, module status
  changes, focuses, lesson marks, certification exams, setting changes,
  limit raises and module orders, as `knowledge.md`
  gives them. An erasure removes them with the rest, and the user's
  signed-in devices stay as the sign-in does.
- **A reader given a user reads that user's records in its query.** No command
  loads every user's log to filter it, so the author's log, which every eval
  reads, never mixes with another user's.
- **`climb log export` prints one user's whole log as JSON.**
- **`climb log erase` deletes one user's whole log in one transaction.**
  The log belongs to its user, so a user leaving takes the log along. The
  user and its sign-in stay, and a new log starts at the next sitting.
- **A call is erased with the log only where no other record names it.** A
  problem's cases name the call that wrote them, and that call is product
  data.
- **The append-only tables let a delete through only while an erasure runs.**
  The erasing transaction sets a setting of its own, and the trigger refusing
  a delete reads that setting. An update is refused either way, so an erasure
  removes a log and revises no record.
- **The erasure asks for the user id typed back, and `--user` has no
  default.** An erasure cannot be undone, and a default would name the
  author's own log.

## Sittings

One session on one problem: when it began, when its clock started, when it
ended, and every pause between.

- **The engine mints the sitting at the first clock press or the first
  submission on the problem**, and every attempt of that sitting carries the
  sitting's id. The log is append-only, so an attempt written without the id
  can never be grouped with the sitting's others.
- **Serving the statement mints nothing.** A sitting minted at serving made
  every opened problem a record, and the author avoided opening problems
  because of it. A user reading a problem and leaving it has not practised it.
- **An untimed submission mints a sitting too.** Mastery counts execution per
  sitting, and an untimed attempt carrying no sitting would need a second
  grouping rule for its retries.
- **The alternative is grouping attempts by how close together they were
  written.** Such a grouping is a guess about a pause, and two readers reading
  one log would draw the sitting's boundary at different attempts.
- **The record is stored rather than held in the process that minted it.**
  One sitting reaches the engine as several calls, and a restart between them
  would lose the start the duration is measured from.
- **The store is revised in place, as the draft store is.** A sitting's state
  moves while the sitting runs, so the sitting store can be refactored where
  the append-only logs cannot.
- **The pauses live in that store alone, and a refactor of it can lose them.**
  No append-only record carries the pause history. That cost is accepted: a
  sitting is evidence about how practice ran rather than a record the board
  counts.
- **The record is kept after the sitting ends**, and `ended_at` closes it. How
  often practice is interrupted and how many sittings a day holds are readable
  in the sitting store alone.
- **No store records which problems were opened and abandoned.** A problem
  opened and left before any press or submission leaves no sitting, and
  nothing reads that count today.
- **A sitting records when its clock started**, as `clock_started_at`. The
  clock begins on the user's press, or as the statement is served where the
  clock preference `flows.md` gives is on. A sitting the first submission
  minted carries no clock start. Reading done before the press is not counted.
- **A sitting whose clock never started is untimed.** `clock_started_at` stays
  absent, and the sitting's attempts carry no `time_to_solve_sec`. Untimed
  practice is legitimate, and a time reconstructed afterwards would be a guess.
- **A running clock is paused and resumed, and the clock stops for a pause.**
  The user steps away from the problem, and a duration counting the hours away
  says nothing about solving it. A clock that never started has nothing to
  pause, so every pause falls after `clock_started_at`.
- **A pause is stored as its own interval**, `at` and `until`. A total of the
  time paused says how long and never how often, and a sitting paused once for
  two hours is different practice from a sitting paused nine times.
- **Only the last pause is open, and a sitting ends with none open.** An
  ended sitting holding an open pause would report an elapsed time that moved
  with the moment it was read.
- **The elapsed time runs from `clock_started_at` and excludes every pause**,
  and the attempt carries it as `time_to_solve_sec`.
- **A solving submission ends the sitting.** A user who solved and left the page
  then has nothing left open, and the next press or submission on the problem
  mints a new sitting.
- **The loop decides what starts and ends a pause**, not the record. A button,
  a hidden tab and an idle timer each leave the same interval.
- **A sitting records the device it was minted on**, as `device`, named as a
  knowledge record names its device: `web` on the web, the device name on the
  phone. A solve typed on a phone is slower than one typed at a keyboard, and
  execution reads the elapsed time, so the two have to read apart.
- **The minting device names the whole sitting.** A press from a second device
  reaches the running sitting, and that device is not recorded. The field is
  absent on every sitting stored before it.
- **A sitting records when it was last touched**, as `last_active_at`. Minting
  the sitting, serving its problem while it runs, a submission, a pause and a
  resume each set it. The record then
  says when practice stopped, without a reader joining the attempt log to it.
- **A sitting idle longer than 45 minutes is ended at its `last_active_at`.**
  Two of the first seven sittings were left running, and serving that problem
  again reached the old clock, which reports the hours away as time to solve.
  An open pause is closed at the same moment, so an ended sitting holds no open
  pause.
- **The ending happens where the sitting is next read**, and nothing runs in
  the background. An abandoned sitting therefore stays running in the store
  until the loop serves or reads it. The elapsed time it reports is the
  same whenever that happens, since the end is `last_active_at` rather than
  the moment of reading.
- **Serving the problem again shows no sitting** once the idle one is ended.
  The next press or submission mints a new sitting, so the clock the solver
  sees starts at zero.
- **A submission to a sitting idle past the bound ends it and is refused.**
  The elapsed time that attempt would carry counts the hours the user was
  away, and no attempt is worth more than the time it reports.
- **Pressing End does not touch `last_active_at`.** A sitting the user ended
  therefore carries an `ended_at` later than its last activity, and one the
  bound ended carries the two equal. No field states which happened, and the
  two timestamps say it.
- **The bound counts idleness, not elapsed time.** A solver thinking for an
  hour with the page open is practising, and the loop keeps that sitting
  touched. `flows.md` gives the loop's own steps, a hidden page among them.

## Attempts

- **The drill loop is the only source.** The engine served the problem and
  watched the sitting, so nothing else is in a position to assert an attempt.
- **An attempt records whether its sitting restored an earlier solve**, as
  `restored`. The page sends it with the submission, and the engine does not
  check it, for the reason `README.md` gives about guarding a verdict. Absent
  on every attempt written before the field, and absent means no restore.
- **A restored attempt is not counted as a solve by mastery.** Its verdict
  stands, and its sitting counts as a failure to solve independently.
- **The verification is its own record**, an `AttemptVerification` keyed by
  `attempt_id`, as a canonical's verification is keyed by `solution_id`.
  `solved` is the projection over the verification's results, and the raw
  result carries what the projection drops. A timeout and a wrong answer are
  both unsolved, and only the timeout is evidence of slowness.
- **An attempt's verification is a record type apart from a solution's**, as
  an attempt claim is apart from a solution claim. The results of the user's
  own code are private, and a solution's verification is product data. One
  type in both stores would leave privacy to whichever writer chose the file.
- **The two types share the fields a run is decided by**: the cap, the runner
  and the per-case results. `corpus.md` fixes what each of those means.
- **The elapsed time is cumulative, from the sitting's start to that
  submission.** A drill mints an attempt per submission, so the second attempt
  of a sitting carries the whole time since the statement was served, rather
  than the time since the first submission. `time_to_solve_sec` names the time
  to solve, and a per-segment number would report three minutes on the attempt
  that solved the problem.
- **The pauses are excluded already**, since the number is the sitting's
  elapsed time at the moment the attempt finished.
- **The time between two submissions is the difference of two attempts.** No
  field records that gap, and cumulative numbers lose nothing by leaving it
  derived.
- **Problem techniques are never denormalized onto an attempt.** Problem
  techniques are re-derivable and the log is not, so a copy taken when the
  attempt was written would drift with no way to tell which is right.

## Attempt claims

Which techniques an attempt used. Per-technique progress is measured from this.
A claim is open to revision, so it is its own record rather than a field on the
attempt.

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
- **The author's confidence on a claim is a level, not a float.** A judgement
  made in seconds carries no more resolution. The level is absent on every
  claim written before the loop asked for one, and a level nobody gave is not a
  low one.
- **One list of columns serves whichever renderer prints a score.** A metric
  added to one renderer and not the other prints a number that stopped being
  true.
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
- **The eval set holds one attempt per problem**, the latest attempt carrying
  code, since a retry asks the identical question and a repeat would measure
  one decision twice. The drill loop still asks about every attempt of a
  sitting, where the answer costs a keystroke.
- **One claim per attempt names every technique the attempt used**, since a
  solution can use several. A later claim replaces the whole set rather than
  rewriting the earlier one.
- **A verdict naming no candidate is a machine claim, and is stored.** The
  verdict is evidence about the code rather than an absence of it, and an
  unstored verdict would be re-read by every later run. A reply cut short by the
  token cap also names nothing and is stored for the same reason, but that reply
  is a fact about the configuration instead. The call's `stop_reason` separates
  a decline from a cut-short reply, and the report counts them apart.
- **An empty claim answers nothing, so the fallback stands.** The resolver
  reads a claim's *techniques* rather than its existence, so the problem's own
  techniques keep answering an attempt whose machine claim declined. A later
  decline
  supersedes an earlier claim as any machine claim does.
- **A decline is scored all the same.** A decline asserts that none of these
  candidates apply, so a user claim naming one is a miss against every
  technique the user named. Unscored, declining would pay: each decline would
  leave a smaller denominator and a better share over it. Only an attempt
  nothing read stays unscored, and the count of declines prints beside the
  share.
- **A decline is stated, never inferred from an empty set.** The user says so
  with `declined`, since the loop records nothing where they skip and emptiness
  would make a lost answer and a stated verdict one record. The classifier
  needs no flag: the classifier answers or fails, and a failure writes no
  claim. The eval set holds a correct decline, or the attempt could only leave
  the set by deletion.
- **A machine claim on a hand-claimed attempt is scored, never a candidate.**
  Such a claim never stands and never reaches the board. It exists to be
  scored. Storing the machine claim makes an eval a dataset rather than a run,
  and a
  second configuration is then paid for only where it has not read. The
  classifier still skips such attempts, but only to save a call whose verdict
  could never stand.
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

## Self-labels

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

### What each mode selects

`FailureMode` is the vocabulary a self-label and a diagnosis both name a mode
from. A mode says why the attempt went the way it did.

- **`speed` is the time the solver took, and never the solution's
  complexity.** The solver reached the answer, and reached it more slowly than
  they judge they should have. No record holds the bar that judgement is made
  against, so the loop asks the solver for it.
- **A timeout is not labelled `speed`.** The attempt's verification stores
  `timed out` on each case the submission exceeded the cap on, so a label
  repeating that outcome answers a question the record already settled. A
  timeout is labelled by its cause, as any other failure is.
- **A diagnosis never names `speed`.** The machine reads the record, and the
  record holds no bar to read a solver's own judgement from.
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
- **A diagnosis names either of the two.** The machine reads the code and the
  log, so it can propose which one the attempt shows, and the eval scores that
  proposal against the solver's own label.
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

## Diagnoses

Why an attempt failed, inferred rather than reported. Keyed to an attempt and
carrying provenance as any machine record does, so every attempt can be
re-diagnosed and compared.

- **A diagnosis is the machine counterpart of a self-label, never its
  replacement.** A diagnosis and a self-label never supersede each other, and
  agreement between them is the eval. A later diagnosis is a second verdict
  rather than a correction.

## What every record keyed to an attempt carries

Claims, self-labels and diagnoses share a base: an engine-minted `id`, the
`attempt_id` they assert about, and `created_at`. One reader orders all three,
latest first, with append order breaking a tie. The `id` lets a record be
cited, by an eval naming the diagnosis it scored or by a user correcting a
claim.

Ordering does not decide which record stands. The shared reader answers "in
what order", and each record's own section says who wins.

## Card runs

Studying a card is an explicit act, not a state the system infers.

- **Starting is explicit**, because the ladder is measured from the start. A
  ladder problem solved before the card began does not count toward the
  ladder. The card teaches the form, and having solved the problem once is not
  having studied the form.
- **The run holds what the start produced**: when the run began and the probes
  it was given. Later probes append rather than replacing the set, so what was
  offered and when stays readable.
- **Derived from the run, never stored**: ladder progress, recall state per
  template, and the card state `## Card states` gives.

## Card states

A card state says how far one user's study of one card has gone. Each card
stands in one of five: not started, acquiring, consolidating, graduated or
lapsed.

- **A card state is one user's.** The card is global and the log is private,
  so two users studying one card read two card states.
- **A card state is derived on every read and never stored.** The card run
  holds only the start and the probes, and ladder progress and recall state are
  folds already. A stored card state would copy those folds, and the copy
  drifts once the corpus moves under the ladder.
- **Not started: the user holds no card run for the card.** Reading a card
  mints nothing, as `flows.md` gives, so a card read and never started stays
  not started.
- **Acquiring: a run is open, and some required rung has no solve since the run
  began.** The ladder teaches the form with the card in view, and a solve from
  before the run counts for nothing, as `## Card runs` gives.
- **Consolidating: every required rung is solved since the run began, and the
  card has not graduated.** A solved ladder shows the form was reached with the
  card in view. It does not show the form is kept, so the card waits for a
  check spaced after the ladder.
- **The solve of the last required rung opens consolidating.** Each template's
  spaced check is then read from the template's reviews, which include the
  ladder's sittings.
- **Graduated: the graduation rule held, and the card has not lapsed since.**
  The rule reads the solved ladder, a recall rated Good of every template that
  carries cases once its spaced check opened, and a probe solved.
  `## The template schedule` gives the check. A card is done once it
  graduates.
- **Lapsed: a graduated card one of whose templates has had a review rated
  Again since graduation.** A form can be lost after the card graduated, and
  a card left graduated on a lost form is never offered again.
- **A probe graduates a card when one of the run's probes was solved since
  the run began.** The probe tests whether the form is recognised, and a
  failed submission before the solve still found the form. So a solve on any
  submission of the sitting counts.
- **A probe solved before the ladder was finished counts too.** The probe
  reads recognition, which the ladder does not change. The spaced check reads
  retention, so graduation still waits for the check.
- **A restored solve and a solve on a defective problem graduate nothing.** A
  restored solve retyped nothing, and a defective problem's verdict decides
  something other than the form.
- **A lapsed card graduates again on recalls alone.** Each template whose
  review was rated Again since the card last graduated needs a recall rated
  Good once its spaced check opened. The check is read from that template's
  reviews, so it opens at least three days after the relearning step.
- **Only a template that carries cases lapses a card.** A lapsed card
  graduates again on recalls alone, and a template no case checks is never
  recalled.
- **A lapse asks for no new ladder and no new probe.** The ladder and the
  probe held at graduation, and a lapse shows one form lost, which a recall
  tests. The run's probes are already seen, and `flows.md` defers when a run
  is given a further probe.
- **Before graduation, a card state reads the ladder as it stands now.** A
  re-derived ladder holding a required rung the user has not solved returns a
  consolidating card to acquiring. The ladder is the truth the card state is
  folded from, so the card state follows the ladder.
- **A graduated card no longer reads the ladder.** Graduation asserts that the
  forms are kept, and a later generation run adds problems to a ladder rather
  than forms. Only a lapse moves a graduated card.
- **A card state is not mastery.** Mastery is per technique and counts
  sittings and drills, as `## Mastery` gives. A graduated card raises no
  technique's reading, since `content.md` keeps cards and mastery apart.

Deferred, since only use answers each:

- Whether a probe solved after the sitting's clock passed a limit still
  graduates the card.
- A lapsed template rated Again again after its own passing recall, while
  another lapsed template still waits. The card graduates again without
  reading that second failure, and only a failure after the new graduation
  lapses the card.
- The card state of a started card whose ladder holds no required rung, every
  core template being a gap.
- A core template added by a re-seed to a card that already graduated.

## Locked cards

A card is locked for a user until every card it requires is met by that
user. `content.md` gives the card graph the rule reads.

- **A required card is met when its ladder was solved, or a probe of its run
  was solved since the run began.** The ladder shows the form was reached with
  the card in view. A solved probe shows a user who already held the form, who
  then skips the ladder rather than repeating study the user does not need.
- **A met card stays met through graduation and a lapse.** A lapse offers the
  lapsed card again and locks nothing above the lapsed card, since the forms
  above the lapsed card were studied and stay studied.
- **Met does not wait for graduation.** Graduation waits for a spaced check
  after the ladder, and a path gated on graduation would stall for days at
  every edge.
- **Locked and met are derived on every read, never stored.** Each is a fold
  over the card runs, the attempts and the current graph. An edited graph then
  moves no record and loses no progress.
- **A locked card's run does not start.** A user who holds the forms below the
  locked card starts each required card and solves its probe, which meets the
  required card at the cost of one problem.

Deferred, since only use answers each:

- Whether a locked card starts on an explicit press that names the cards it
  skips. A user holding many forms pays one probe per required card first.
- Whether a card stays met once a re-derived ladder returns it to acquiring.
  Met reads the ladder as it stands, and the ladder at an earlier read is not
  kept.

## Recall attempts

One template reproduced from memory, and how it went.

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

## The template schedule

Each template's memory, for one user, is FSRS-6, replayed from the template's
reviews. One curve then decides when a template's spaced check opens, when the
check is owed, and when a graduated template is due again.

- **A template's state is replayed from its reviews in time order**, as a
  question's is from its answers in `knowledge.md`. The state is derived on
  every read and never stored.
- **A review is a recall attempt of the template, or a sitting on a problem
  whose `target_template_id` names the template.** `flows.md` `## A
  template's reviews` lists which sittings count.
- **Each recall attempt becomes a rating.** A pass with no hint rates Good, a
  pass after the notes rates Hard, and a failed recall rates Again. A pass
  after the form hint rates Again too, since typing back a form just read
  recalls nothing.
- **Each sitting becomes a rating.** A solve on the first submission rates
  Good, a solve after a failed submission rates Hard, and an unsolved sitting
  rates Again. Easy is never used.
- **The ladder's sittings are reviews.** A rung solved with the card in view
  is a warm review, and FSRS gives a first review a short stability. The last
  review before the check is therefore the point the check is measured from.
- **Recall probability is FSRS's retrievability**: the chance, read from the
  replay, that the user still reproduces the form at a given moment. It
  counts whole days since the last review, as py-fsrs does, so it falls once
  a day.
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
  work and freezes new card starts, as `flows.md` gives the pick.
- **A failed check is a review rated Again.** FSRS relearning shortens the
  stability, and the window is read again from the new state. The card stays
  consolidating.
- **A graduated template is due at desired retention 0.9**, FSRS's own due
  time. An overdue template freezes nothing, and the pick serves the lowest
  recall probability first.
- **A review rated Again on a graduated card's template lapses the card.** A
  review rated Hard shortens the next interval and leaves the card graduated.
- **The settings are constants in code, and a change replays every
  template.** No state is stored, so new settings move every due time with no
  migration. Each stored prediction names the settings it was made under, so
  a calibration compares it with the model that made it.
- **The template settings stay on the engine.** The question settings reach
  both clients in the snapshot. The template schedule runs on the server
  alone, so changing it ships no snapshot and regenerates no fixture.
- **The settings start equal to the questions'**: the FSRS-6 default
  parameters, desired retention 0.9, learning steps of 1 and 10 minutes, a
  relearning step of 10 minutes, and fuzzing off. `knowledge.md` `## The
  schedule` gives the reason for each.

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

## Short exercises

A short exercise is a question about code that takes seconds to answer and
needs no typing. Judging a solution is the first kind. It suits the phone,
where a sitting's typing is slow.

- **Each kind of short exercise is a record kind of its own.** Each kind
  answers a different question, and its answer has a different shape. One
  shared record would carry fields every kind but one leaves empty.
- **A short exercise is not an `Attempt`.** No problem is served and nothing
  is submitted, so no field keys it to a sitting.
- **Mastery never counts a short exercise as execution.** Judging someone
  else's solution is reading code, and execution is writing a correct
  solution. A short exercise feeds no part of mastery, as `## Mastery`
  gives.
- **An answer is private and append-only**, keyed to its user and to the item
  it answered, as a recall attempt is.

### Judging a solution

The user reads one solution to a template's own question and says whether it
is correct. A flawed solution carries one mutant of the form, and the user
then taps the line that is wrong. `content.md` gives the items.

- **A `Judgement` stores one answer**: its `id`, `user_id`, `item_id`,
  `created_at`, whether the user called the solution clean, and the tapped
  line where the user called it flawed.
- **Correctness is derived from the item, never stored.** A clean item is
  answered right by calling it clean. A flawed item is spotted by calling it
  flawed, and located by tapping the mutant's line as well.
- **Spotting and locating are counted apart.** A user who senses a flaw and
  taps the wrong line reads code differently from one who finds the line, and
  one number would hide which.
- **After the answer, the item shows the separating case**: the arguments, the
  expected value and what the flawed solution returned. The case is the
  evidence the line is wrong, and reading it is the lesson.
- **Two rates per technique are derived for the board**: the flawed items
  spotted, and the clean items called flawed. A user calling everything flawed
  would score every flaw found, and the second rate exposes that.
- **The next item is picked unseen first, then by staleness**, until the
  scheduler picks it.

## Mastery

How well a user knows one technique. The engine computes mastery from the log
each time it is asked, and never stores it. So the rules below are the whole
model of mastery.

- **Mastery has three parts per technique: recognition, execution and
  knowledge.** Recognition means the user sees that a problem needs the
  technique when nobody told them. Execution means the user writes a correct
  solution once they know the technique. Knowledge means the user recalls the
  facts the technique rests on.
- **The three parts are kept separate.** A user who misses the technique needs
  recognition drills. A user who sees it and cannot write it needs the card's
  ladder and the recall trainer. A user who cannot state its facts needs the
  questions. A single score would hide which of the three the user needs.
- **Knowledge is counted from answers** to the questions the technique
  carries. `knowledge.md` gives the answer and the question state it is
  replayed into.
- **A question carries the techniques its subtopic names**, as `knowledge.md`
  `## Modules` gives. An answer counts toward each technique's parents as well,
  as a claim does, so an answer in `knapsack` counts toward
  `dynamic-programming`.
- **Knowledge never stands in for recognition.** An answer recalls a fact the
  question named, and recognition is spotting a technique nobody named. A
  question answered correctly therefore raises no recognition reading.
- **Execution is counted per sitting.** One sitting can hold several
  attempts, one per submission. Counting attempts would punish a user who
  submits often, though they solved the same problem.
- **A sitting with no submission counts for nothing.** A clock started and
  never submitted against records that the user worked on the problem, not
  that they tried a solution.
- **An untimed sitting counts by its verdict alone.** It says whether the user
  solved the problem and nothing about how long the solve took, so any reading
  of speed comes from timed sittings.
- **A sitting counts for every technique its attempts used.** Those
  techniques come from the standing attempt claim, or from the problem's own
  techniques when no claim stands. `## Attempt claims` gives that rule.
- **A sitting solved on the first submission counts more than one solved
  later.** After a failed submission the user sees the failing case, which
  helps them debug. The order of the attempts shows which submission passed.
- **The self-label on the sitting's last attempt adjusts the count.** `speed`
  marks a solve that took too long. `syntax` counts less as a failure, since
  the user knew the form. `gap` and `rust` mean the user did not write the
  form. An attempt without a label counts by its verdict alone.
- **Recognition is counted only from recognition drills.** The problem page
  lists the problem's techniques before the statement is served. So every
  sitting tells the user the technique, and no sitting tests recognition.
  Until the recognition drill is built, recognition has no evidence and reads
  as unknown.
- **A recognition drill counts for the techniques its problem carries.** The
  user describes the approach in words. The framing judge grades the
  description against the problem's canonicals, and that grade is the drill's
  result.
- **The judge's grades count only after the judge itself is tested** against
  drills graded by hand. A judge that accepts vague answers would raise
  recognition for exactly the techniques the user cannot spot. Grades written
  before that test are stored and ignored.
- **Sittings and drills on a defective problem do not count**, solved or not.
  `corpus.md` gives the reason for sittings. A drill on such a problem was
  graded against a statement that asks the wrong thing.
- **Recall attempts do not count toward mastery.** Typing a form from memory
  is neither spotting it in a problem nor solving a problem with it. The card
  shows recall progress on its own, as `## Recall attempts` gives.
- **Short exercises do not count toward mastery either.** A judgement item and
  a key line each come from a named template, so neither tests spotting the
  technique, and neither writes a solution. The board shows the judgement
  rates beside mastery instead, as `## Judging a solution` gives.
- **Diagnoses count only after they are tested** against the user's
  self-labels. An untested diagnosis would put a guess where the user's own
  answer belongs.
- **The formula is code, so changing it changes no record.** Mastery is
  recomputed on every read, so a new formula applies to every technique at
  once.
- **Each pick stores the prediction the formula made before the attempt.**
  That prediction is the only stored trace of mastery. It lets a later
  formula be compared with what an earlier one predicted.

- **Execution starts as the mean of a score per sitting.** A solve on the
  first submission scores 1, a solve after a failed submission 0.5, and an
  unsolved sitting 0. An unsolved sitting labelled `syntax` scores 0.25, and
  a sitting labelled `gap` or `rust` scores 0 whatever its verdict. These are
  starting values, and each moves only on what the stored predictions
  measure.
- **Execution reads unknown until a technique holds three sittings.** A mean
  over one or two sittings swings on a single solve, and a board showing it
  would rank techniques on noise.
- **Every sitting weighs the same, however old.** How old evidence fades is
  deferred, so the first reading counts the whole log.
- **A solve labelled `speed` counts as a full solve**, until the timed
  sittings say how slow a solve has to be to count less.

Deferred, since only use answers each:

- How old evidence fades.
- Whether the judgement rates enter mastery, once the stored predictions show
  whether a technique's judgement rates predict its execution.
- The scores and the evidence bound beyond their starting values.
- Whether a solve labelled `speed` counts less than a full solve.
- How a module outside the technique vocabulary, such as Python, enters
  mastery. Its questions carry no technique for a reading to be kept on.

## Predictions

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
