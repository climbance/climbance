# Pick

The board serves one pick: the next act the schedule names for the user. The
user may take it or pick anything else the board offers. `predictions.md`
gives what each pick stores as the user takes it.

## What a pick names

- **The pick reads three folds**: each template's FSRS state, each card's
  state with its next spaced check or recall, and each technique's mastery.
  All three are derived on every read, so the pick is too, and nothing stores
  it but the prediction each pick makes.
- **A pick names a template and the act that reviews it.** The act is a
  recall of the template, or a sitting on a problem written for it.
- **A spaced check is served as a recall.** Graduation reads a recall rated
  Good, as `card-states.md` gives, so a check served as a sitting could never
  graduate the card.
- **A graduated template's due review is served as a sitting**, on a problem
  written for the template that the user has not solved. A sitting reviews the
  form in use on a statement the user has not seen, where a recall reviews
  reproducing it. A template with no such problem is served as a recall.
- **A failed sitting aims the pick at the form it missed.** The sitting's
  Again lowers the target template's stability, so FSRS brings the template
  due again soon. The pick then serves the template's recall once the
  relearning step has passed, and a problem written for it after the recall
  passes.
- **A failed sitting labelled `syntax` or `speed` aims nothing.** Each label
  says the solver held the form. The Again still enters FSRS, since the
  rating reads the attempts alone, as `template-schedule.md` gives.
- **A failed sitting with no self-label reads its diagnosis instead.** A
  diagnosis naming `slip` aims nothing, as a `syntax` label does not. A
  diagnosis naming `form`, or no diagnosis, aims the pick at the form. A
  self-label stands over a diagnosis of the same attempt, as a user record
  stands over a machine record.
- **The pick reads a diagnosis only from a measured configuration, at the
  baseline prompt.** A configuration is measured once its baseline column in
  `climb diagnose score` reads 10 verdicts on the `syntax` row or the slip
  mutants. `MEASURED` in `climb.diagnoser` names each measured configuration
  with the digest of the system prompt it was measured on. A pick acting on an
  unmeasured cause would aim practice on a guess. A tool's column is measured
  apart, so a verdict given a tool is not read.
- **On 2026-11-24 the default configuration was measured.** Its baseline named
  `slip` on 78% [63–89%] of 37 slip mutants, and `form` on 90% [84–94%] of 125
  labelled mutants, over the local store.
- **Ties break on the lowest recall probability, then the shallowest card,
  then the lowest execution reading, then the slug.** Recall probability ranks
  the form closest to being lost. Depth then serves a form other forms build
  on before the forms above it. An unknown execution reading comes before
  every number, since the technique has the least practice behind it.
- **The board offers everything beside the pick.** The cards in progress, the
  unlocked cards not started and every technique stay listed, as
  `../web-app/pages/practice/board/README.md` gives. The pick sits above them,
  so a user who declines it picks as before.
- **A technique with no template keeps the board's staleness order.** No
  template means no FSRS state, so the schedule has nothing to rank it by.

## The order of the offers

The pick offers by card state, in this order, and serves the first offer the
user's cards hold.

1. An owed spaced check, on a consolidating card or a lapsed one.
2. An open spaced check, on a consolidating card or a lapsed one.
3. A graduated template's due review, overdue or not.
4. An acquiring card's next rung, or a consolidating card's probe.
5. A new card, only below the cap and only while no check is owed.

- **An owed check comes first.** The check tests whether the form survived
  the gap after study, and each further day moves it toward a second
  acquisition. A check that is open but not owed can wait a day, so it comes
  second.
- **A lapsed card is offered again through its checks.** Each template rated
  Again since graduation waits for its own check, and the card graduates
  again on those recalls alone, as `card-states.md` gives.
- **A due review comes before a rung.** A graduated form decays while it
  waits, and a ladder picks up where it stopped.
- **An acquiring card offers its first unsolved rung**, required rungs before
  optional ones, in the ladder's order, a skipped rung after the rest. The
  ladder's opening easy rung counts as required in that order alone, so it is
  offered first while unsolved, and the card state still ignores it. The
  ladder follows the card's template order. `../flows/solving-a-rung.md`
  gives both.
- **A consolidating card with no probe solved offers its next unattempted
  probe**, ranked with the rungs. Graduation needs a solved probe, and a
  probe needs no wait.
- **A consolidating card waiting for its check offers nothing else.** Its
  rungs are solved, and its check has not opened.
- **A new card is the shallowest unlocked card not started**, as the board
  already lists them. The cap and an owed check both hold it back.
- **An owed check freezes new starts, and an overdue review does not.** An
  owed check is study left unfinished, and a new card would split the days
  that finish it. An overdue review is decay risk on a form already kept, so
  it ranks by its recall probability and holds nothing back.

## The in-flight cap

The in-flight cap bounds when the pick offers a new card.

- **The pick offers a new card only while fewer than two cards are in
  flight.** Two is the limit the author's earlier drill board held. Each card
  in flight needs work on the day it is open, and more than two split each day
  between too many forms.
- **A card is in flight while it is acquiring, or consolidating with its
  spaced check open or owed.** Each needs work now: a rung to solve, or a
  recall to make.
- **A consolidating card waiting for its check to open holds no slot.** Its
  next act is days away. Counting it would leave those days idle, and the next
  card's ladder fills them instead.
- **A graduated card and a lapsed card hold no slot.** A graduated card is
  done. A lapsed card needs recalls alone, which the pick offers beside a new
  card.
- **The cap is folded from the card states on every read**, and nothing stores
  it.
- **The cap bounds the pick, and a start by hand stays open.** The card's page
  starts a run whatever the cap reads, since the user chose that card.
