# Card states

A card state says how far one user's study of one card has gone. Each card
stands in one of five: not started, acquiring, consolidating, graduated or
lapsed.

## The five states

- **A card state is one user's.** The card is global and the log is private,
  so two users studying one card read two card states.
- **A card state is derived on every read and never stored.** The card run
  holds only the start and the probes, and ladder progress and recall state are
  folds already. A stored card state would copy those folds, and the copy
  drifts once the corpus moves under the ladder.
- **Not started: the user holds no card run for the card.** Reading a card
  mints nothing, as `../flows.md` gives, so a card read and never started stays
  not started.
- **Acquiring: a run is open, and some required rung has no solve since the run
  began.** The ladder teaches the form with the card in view, and a solve from
  before the run counts for nothing, as [`card-runs.md`](card-runs.md) gives.
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
  [`template-schedule.md`](template-schedule.md) gives the check. A card is
  done once it graduates.
- **Lapsed: a graduated card one of whose templates has had a review rated
  Again since graduation.** A form can be lost after the card graduated, and
  a card left graduated on a lost form is never offered again.

## Graduating

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
  tests. The run's probes are already seen, and `../flows.md` defers when a run
  is given a further probe.

## The ladder under a card state

- **Before graduation, a card state reads the ladder as it stands now.** A
  re-derived ladder holding a required rung the user has not solved returns a
  consolidating card to acquiring. The ladder is the truth the card state is
  folded from, so the card state follows the ladder.
- **A graduated card no longer reads the ladder.** Graduation asserts that the
  forms are kept, and a later generation run adds problems to a ladder rather
  than forms. Only a lapse moves a graduated card.
- **A rung carries when it joined the ladder**: the first template match
  placing it, which the generator writes at landing. No ladder is stored, so
  a card graduated under the rungs that joined before its graduation, and a
  required rung joining after it is left out of the card state.
- **A card state is not mastery.** Mastery is per technique and counts sittings
  and drills, as [`mastery.md`](mastery.md) gives. A graduated card raises no
  technique's reading, since `../content-repo/cards.md` keeps cards and mastery
  apart.

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
user. `../content-repo/card-graph.md` gives the card graph the rule reads.

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
