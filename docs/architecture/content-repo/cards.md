# Cards

A card organises studying one technique: what to read, what to reproduce from
memory, and what to solve. A card is not the vocabulary itself, and not an
ability estimate. Mastery measures how well a user recognises and executes each
technique, and a card and a mastery estimate share no data.

## What a card holds

- **Product data, not code.** Cards live in the engine datastore, seeded from
  `content/`, which is gitignored like `data/`. One location, whatever the
  content turns out to be worth keeping private.
- **Granularity follows teaching, not estimation.** One technique can carry
  several cards. Mastery is estimated per technique, so cards are never the
  unit of estimation, and the attempt log never references a card.
- **A card carries no card state.** The card is global and each card state is
  one user's, so `../log.md` derives a user's card state from that user's log.
- **A card names no problem.** It carries a selector: a technique, and the
  filters that narrow it. The ladder is derived from the corpus. Ids are minted
  per engine, so a card holding problem ids would mean nothing in another
  store, where a selector ships anywhere.
- **The trigger is its own field**, apart from the prose it could sit in,
  because a drawn recall asks exactly that question: which form the trigger
  calls for. So the trigger is shown and withheld on its own, where the rest
  of what to read is one authored block the engine never parses. The pages
  cut that block at its headings for display alone, and no heading carries a
  meaning the engine reads. The trigger is
  carried at both levels, because recall is per template. The card's trigger
  says to reach for the technique, and a template's trigger says which of the
  technique's forms.
- **One template may sit outside the core set.** Templates are core by
  default, and at most one is marked optional. A card is covered without its
  optional template: the gap report skips it, and a rung covering it alone is
  optional. An optional template differs from a core one in nothing else.
- **Every template's code is hidden on a card's page until the user reveals
  it.** A form is worth deriving before it is read, and a card showing its
  code unasked removes that chance for every template alike. The card's
  trigger and brief stay visible, since they say when to reach for the
  technique rather than how the form is written.

## The ladder

The ladder is the problems a card has the user solve. The engine derives it
from the template matches and the card's selector, and stores none of it.

- **The ladder covers every core template.** Its rungs come from the
  template matches, at least one per template, and the selector fills the rest
  out to `size`. A match is a fact about a solution, so a rung is filled by the
  problem that solution answers. Drawn from the selector alone the ladder would
  exercise the technique and leave some forms untouched, since a technique says
  what a problem is about rather than which form solves it.
- **A ladder whose selector admits easy holds an easy rung** wherever the
  corpus holds an easy problem for the selector. The selector's fill takes an
  easy problem first when no covering rung is easy, one rung past `size` where
  the covering rungs already fill it. An empty difficulty list admits easy, as
  it admits every level. Ordered by attempts
  alone, `dp-1d-linear` filled eight rungs with medium problems while its easy
  problems waited. A learner starting the card then met no problem that
  applies the form unchanged.
- **Requiredness is derived from the templates a rung covers**, never stored.
  A rung covering a core template is required. A rung covering only the
  optional template is optional. A rung covering both is required, and the
  optional template is offered on that rung as the alternative approach.
- **A core template no solution displays is a reported gap**, not a quietly
  shorter ladder. The gap is the input to the next generation run: it names the
  template the next problem must be written for. The ladder never substitutes
  another problem, because a substitution hides the gap and the missing problem
  is then never written.
- **The ladder is derived on every read**, from the selector and the corpus as
  they stand. The selector is the truth and the ladder a derived view, so
  deriving the ladder again costs nothing. A started card is re-derived too.
  Ladder progress is a fold over attempts rather than a mark on a rung, so a
  solved problem stays solved.
- **A rung keeps its problem while the card's run is open.** The ladder ranks
  the problems least recently attempted first, counting only the attempts
  finished before the run began. Ranked by every attempt, each solve moved
  the solved problem to the back, another problem took its rung, and the
  card's count of solved rungs stayed at zero.
- **A retired problem fills no rung.** A defective problem was never a fair
  test. Re-deriving the ladder removes the retired problem, which is the other
  reason a started card is re-derived.
- **Probes are assigned when a card is started**, not at import, since a
  problem unseen at import need not still be unseen. Unseen first, then least
  recently attempted, and never drawn from the ladder. The ladder teaches the
  form, and a probe tests whether the form transfers to a problem it was not
  studied on.

## Speedups

- **A template states whether its form is a speedup** over the naive solution
  the technique replaces. Backtracking and exhaustive search are their own
  optimum, so no input separates them from a reference. Generation cannot tell
  such a form from a reference written cleverly by mistake, so the template
  says which of the two holds. A missing separation where a speedup was
  claimed is a defect in the run, and `../flows.md` names the three things that
  produce one.
- **The claim is asymptotic: the form beats the naive approach by at least a
  factor of log n.** The search separates by wall clock under the sitting's
  cap, on an input the ceiling holds, and that input carries some hundred
  thousand integers. A linear or linearithmic naive approach finishes such an
  input in milliseconds whatever the form does. So the search raises the
  case's repeat count where the walk reaches the ceiling, and times `solve`
  called that many times on one input. `../corpus.md` gives the repeat count.
- **The statement is written for the solver, not for the search.** One lookup
  in a sorted array is sublinear for the form and linear for the scan it
  replaces. The form and the scan both finish within the cap, so no input
  separates them. Asking for a batch of queries would make the scan quadratic,
  and the corpus would then carry a question nobody asks. The search instead
  separates the form with a repeated case: one lookup, called many times under
  one cap.
- **The claim still reaches the generator**, as the constraints are the
  statement's own. A statement admitting two thousand elements leaves no input
  on which a naive solution exceeds the cap, whatever the input generator
  builds.

## A template's cases

A template's cases let the recall trainer run what the user typed.

- **A template carries the cases its form is checked against.** The trainer
  runs what the user typed rather than comparing it with the stored code. Two
  correct reproductions of one form differ in their whitespace and in the names
  they choose, and neither difference is a recall failure.
- **A template's cases are checked against the form's own mutants.** `card
  check` runs every one-change mutant of the form against the cases, and a
  mutant every case passes is a case the template may lack. A survivor
  refuses nothing, since a mutant can be equivalent to the form, and only the
  author can tell which.
- **A survivor the author judged equivalent is named on the authored
  template**, in `equivalent`, and the check stops reporting it. The list is
  authoring alone, and the seed stores none. An entry no survivor matches any
  longer is reported as stale, since an edit to the form moves its lines.
- **The cases call `solve`**, as a problem's cases do. `../corpus.md` gives why
  that name is fixed: a function called `lower_bound` announces the form the
  recall is asking for.
- **A template whose answer is a set says so, and its cases are compared after
  the top level is sorted.** Every subset and every permutation of an input is
  one answer, and two correct reproductions emit that answer in different
  orders. The sort reaches the top level alone, so two permutations of one
  multiset stay two answers.
- **An answer that is neither unique nor a set carries no cases.** A
  topological order is one of many valid orders, and a sort compares multisets,
  so it would accept an invalid order as readily as a valid one. Such a form is
  read on the card until a case can carry a check rather than a value.
- **A template with no cases is read and never recalled.** The cases are an
  added field, so a card authored before it keeps working, and a template whose
  form no case checks is study material rather than a recall subject. A
  procedure template carries prose steps, which no case decides.
