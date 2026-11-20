# Short exercises

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
  solution. A short exercise feeds no part of mastery, as
  [`mastery.md`](mastery.md) gives.
- **An answer is private and append-only**, keyed to its user and to the item
  it answered, as a recall attempt is.

## Judging a solution

The user reads one solution to a template's own question and says whether it
is correct. A flawed solution carries one mutant of the form, and the user
then taps the line that is wrong. `../cli/exercise-items.md` gives the items.

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
- **The next item is drawn from the cards the user started first**, unseen
  before stale. A user practises the forms of the cards being studied, and a
  form from a card never opened tests what nobody taught. On a new account the
  first item came from `backtracking`, a card locked behind another.
- **With no item left on a started card, the next item comes from the cards not
  started**, unseen before stale, the shallowest card first, then by slug. The
  pick offers a new card in that order, as `pick.md` gives. A page asking for
  one card's items draws from that card alone.
- **The scheduler picking the next item is deferred** until the pick serves
  short exercises.

## Filling a key line

The user reads a template's form with one statement blanked and picks the
statement that belongs there. `../cli/exercise-items.md` gives the items.

- **A `Fill` stores one answer**: its `id`, `user_id`, `item_id`,
  `created_at`, and the choice the user picked, by its position in the item.
- **Correctness is derived from the item, never stored.** The fill is right
  when the picked choice is the form's own line.
- **After the fill, the item shows the form's line and, for a wrong choice,
  its separating case**: the arguments, the expected value and what the code
  with that line returned.
- **The next item is drawn as judging draws its items**: from the cards the
  user started first, unseen before stale.
- **A rate per technique on the board is deferred** until enough fills exist
  to show whether the fill rate differs from the judgement rates.
