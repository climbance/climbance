# A failure diagnosed and the next pick

A sitting ends unsolved, the engine reads why it failed, and the board's next
pick aims at the form the sitting missed. This page follows the
`failure-diagnosed` journey in `../model.toml`. It starts at a sitting ended
unsolved. It ends at the board serving a pick aimed at the form that failed.

`sitting.md` gives the sitting itself, from choosing the problem to the claim
and the label. This page starts where `sitting.md` ends. `../api/pick.md`
gives the rules of the aim, and this page cites it rather than restating
them. Each component below is named by its id in `../model.toml`.

## 1. The label on the unsolved sitting

- **The sitting ends unsolved at the End press or at the idle bound**, as
  `sitting.md` gives. The web asks the claim and the label in a dialog, and
  the phone in a sheet.
- **An unsolved attempt takes `gap`, `rust` or `syntax`.** `self-labels`
  stores the label. `../api/self-labels.md` gives what each mode means, and
  why `gap` and `rust` name different remedies.
- **An attempt that crashed on every case is asked for no label.** The
  attempt then carries a claim and no self-label, and step 2 is the only
  source of a cause for that attempt.
- **A skipped label stores nothing.** A label cannot be given later, as
  `../api/self-labels.md` gives, so a skipped label leaves the attempt to the
  diagnoser.
- **The pick reads the label on the sitting's last attempt.** A sitting may
  hold several failed attempts, and the last one ended the sitting.

## 2. The diagnosis, off the server

- **The diagnosis is written by `diagnoser`, in the command line the author
  runs off the server.** `climb diagnose attempts` reads every failed attempt
  with code, through the SSH tunnel to the store. `../cli/diagnoser.md`
  gives the call.
- **A failed attempt has no diagnosis until the author runs that command.**
  No schedule runs the command, and the engine on the server writes no
  diagnosis. A failure the user saw minutes ago therefore has none.
- **A diagnosis names a cause: `slip` or `form`.** `slip` is the fault a
  `syntax` label names, and `form` is the fault `gap` or `rust` names.
- **A refusal or a reply cut short writes no diagnosis.** The call log keeps
  the request, so the attempt stays undiagnosed until a later run.
- **No page of either client shows the user a diagnosis.** The author pages
  list `diagnose` among the commands that stay commands, as
  `../web-app/pages/author/README.md` gives.
- **The pick reads a diagnosis only from a measured configuration, at the
  baseline prompt.** `../api/pick.md` gives the measure, and records that the
  default configuration was measured on 2026-11-24.

## 3. The schedule reading the failure

- **`template-schedule` reads the unsolved sitting as a review rated
  Again**, at the moment of its first submission. The sitting reviews a
  template only where its problem's `target_template_id` names one, as
  `../api/template-schedule.md` gives. A problem written for a technique
  reviews no template, and the pick then has no form to aim at.
- **The Again enters FSRS whatever the label says.** The rating reads the
  attempts alone, so a `syntax` sitting lowers the template's stability as a
  `gap` sitting does.
- **`mastery` scores the sitting for execution.** An unsolved sitting scores
  0, or 0.25 where its last attempt is labelled `syntax`, as
  `../api/mastery.md` gives. The same score enters the technique's ability.
- **`card-states` reads the failure through the card.** An unsolved rung
  leaves an acquiring card acquiring. A review rated Again on a graduated
  card's template lapses the card, as `../api/card-states.md` gives.
- **Step 3 stores nothing.** The template's state, the execution reading and
  the card state are each derived from the log on every read.

## 4. The board's next pick

- **The user returns to the board, at `/` on the web and the Practice tab on
  the phone.** The board serves one pick above its lists, as
  `../web-app/pages/practice/board/README.md` gives.
- **`pick` reads the three folds**: the template's FSRS state from
  `template-schedule`, the card's state from `card-states`, and the
  technique's mastery from `mastery`.
- **A `gap` or `rust` label aims the pick at the target template.** A
  `syntax` or `speed` label aims nothing, since each label says the solver
  held the form.
- **With no label, the diagnosis decides.** A `slip` diagnosis aims nothing.
  A `form` diagnosis aims the pick, and so does no diagnosis at all. A later
  `slip` diagnosis can therefore only remove an aim the pick already served.
- **The aimed pick is the template's recall first**, once the relearning step
  has passed. A problem written for the template follows once the recall
  passes. `../api/pick.md` gives both under `## What a pick names`.
- **The board row names the act**, such as `Recall: Lower bound` with a
  Recall press, as `../web-app/pages/practice/board/board.md` draws it. The
  lists below the pick keep their order, so a user may decline the pick.
- **`predictions` stores what the pick expected once the user opens its
  act.** The record holds FSRS's recall probability and the execution
  reading, as `../api/predictions.md` gives. A pick the board served and the
  user never opened stores nothing.

## 5. The recall the pick serves

- **The recall opens at `/cards/:slug/recall/:template` on the web, and the
  Recall screen from Card on the phone.** `cards-and-recall.md` follows the
  recall itself, and `../flows/recalling-a-template.md` gives its rules.
- **The recall attempt is the template's next review.** `template-schedule`
  rates it Good, Hard or Again, and the next pick reads the new state.
- **A passed recall turns the aim to a problem written for the template**,
  one the user has not solved. That problem's sitting is the `sitting`
  journey again.

## Where the web and the phone differ

`../core-package/screens.md` marks the board and a recall `same` on both
clients.

- **The phone reads the board from the engine and keeps no copy.** With no
  connection the Practice tab says so, and no pick is served. The web needs a
  connection to the engine for the pick as well.
- **The phone does not ask a claim again once the sheet was left
  unanswered**, as `sitting.md` gives. An unsolved sitting on the phone is
  therefore more often left without a label, and the diagnosis decides its
  aim.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| The label | a self-label on each asked attempt | `pick`, for the aim; `mastery`, for the execution score; `diagnoser`, scored against it |
| `climb diagnose attempts` | a diagnosis per failed attempt, with its provenance | `pick`, where no label stands and the configuration is measured; `climb diagnose score` |
| Each diagnosis call | a call in the call log | the author's spend page |
| Opening the pick's act | a prediction | a later calibration against the act's outcome |
| The recall | a recall attempt | `template-schedule`, as the template's next review; `card-states`, for a check |

`cards-and-recall.md` follows the recall into a card's graduation.

## Open questions

- **Which card states does the aim apply to?** `../api/pick.md` states the aim
  for any failed sitting. Its offers are ordered by card state, and no doc
  says how a failed rung on an acquiring card turns into a recall rather than
  the same rung offered again.
- **When is the aimed recall served on a lapsed card?** `../api/pick.md`
  serves the recall once the relearning step has passed. A failed sitting on a
  graduated card's template lapses the card, and `../api/card-states.md` opens
  a lapsed card's check at least three days after the relearning step.
- **Does a measured diagnosis enter mastery?** `../api/mastery.md` says
  diagnoses count only after they are tested against the self-labels. The
  pick reads a measured diagnosis, and no doc says whether the execution
  score reads one where no label stands.
- **How often does the author run `climb diagnose attempts`?** No doc gives a
  cadence, and the author inbox names no undiagnosed attempts. Until the run,
  an unlabelled failure aims the pick as a `form` diagnosis would.
