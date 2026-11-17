# Corpus

The engine generates a problem, the test cases that decide it, and the
solutions written for it. This file specifies those records. Part of the
architecture, and `README.md` is the map.

## Problems

- **Generated, and that is the only origin.** The engine writes a statement,
  the test cases that decide it, a canonical solution and a reference
  solution.
- **A problem is written for a target: what it must be solvable by.** A
  template is the tightest kind, naming the exact form. A technique is a looser
  one, naming only the skill. Each kind produces a problem. A template target
  and a technique target differ in what the generator knew, and not in how the
  problem is judged.
- **The looser target reaches the rest of the vocabulary.** A paradigm and a
  problem class have no form to reproduce, so no template names them, and a
  corpus written from templates alone can never exercise them.
- **The technique target is deferred until a card's selector names a
  technique the template-aimed corpus cannot fill.** Generation writes for a
  template target alone today, and no writer sets `target_technique`.
- **The target is stored on the problem.** `target_template_id` or
  `target_technique` records what the generator was told rather than what a
  model inferred. The template arm makes the first template match provenance.
  No arm claims the problem exercises nothing else.
- **A technique target asserts no template match and no technique.** The
  generator was told no form, so the matcher alone says which forms the
  canonical displays. The target says what the generator was asked for, and
  only a solution claim says what the canonical used.
- **Provenance is required.** A problem names what produced it, as any machine
  record does.
- **A problem's techniques are the union of the standing solution claims of
  its canonicals**, a view rather than stored truth. Adding a canonical can
  widen the set, and re-deriving is legal and expected. The reference and the
  naive solution are excluded, or the approach a form replaces would be
  credited to the problem. A canonical that sorts before it searches used two
  techniques, and only a solution claim names the second.
- **Never derived from templates or from the target.** A paradigm and a
  problem class have no form to type out, so templates reach about half the
  vocabulary, and a set folded from them would be capped by which cards exist.
- **The statement is stored, because a solver is served it.** A matcher also
  reads the statement beside the canonical it classifies. Required and
  non-blank.
- **A created problem is served.** `created` means written and verified, and
  no later gate stands between that and serving. Retirement is the only status
  move.
- **Whether a statement gives its form away is not checked.** A statement can
  name its approach, or reuse the example its template's trigger names, and a
  solver who recognises the problem has not derived the form. A gate over the
  corpus for this is deferred. It needs
  a corpus to measure and a baseline no generator wrote, and a status the gate
  promotes to is an additive change when it comes.
- **A statement's example and cases are the engine's own.** The generator's
  prompt forbids reusing the example, the values or the wording of a published
  problem. A published question retold in the engine's own words is accepted.
  The screen site rejects a copy, and `flows.md` gives where it runs. The screen
  answers from the model's memory, since no repo may hold a published example
  to compare against.
- **A problem is never edited, and only its status moves.** A statement that
  says the wrong thing is retired `defective` and a new problem is written.
  The retired problem's attempts stay with the record they were made against,
  and no case moves under them. A generated statement passes every gate or is
  retired, so a write path for wording would buy nothing and could change what
  a verdict means.
- **A problem is retired by hand, in the terminal.** A problem is served to
  every user, so one user's reading of a statement may not remove the problem
  from another user's practice. A user asks for a retirement with a
  retirement request, which the author reads first. `log.md` gives the
  record.
- **Retirement names its reason.** `defective` is a statement that asked for
  something its cases do not decide. `copied` is a problem the screen site
  named a published source for, and its attempts stay in mastery: the solver
  solved what the problem asked.
- **A defective problem's attempts are excluded from mastery, both
  directions, at read time.** The failure was the problem's fault, and
  excluding only the failures would raise a solve rate because a problem was
  broken. The attempts stay readable, and the board stops counting them.

## Difficulty

A problem's difficulty is a score on the contest scale, with a deviation. The
label a problem is served with, easy, medium or hard, is derived from that
score.

- **A difficulty score reads on the contest scale.** The contest scale is the
  rating scale of the public programming contests. There a problem's rating is
  the contestant rating at which a solve is expected half the time. A score in
  those units says how hard a problem is to anyone who has entered a contest,
  where a label says it in three words.
- **A score carries its deviation**, one standard error on the contest scale.
  A rating method reports how sure it is, and a reader comparing a user with a
  problem needs that certainty as much as the score.
- **The label is the band the standing score falls in.** A band is a range of
  scores one label covers, and the three bands are a fixed table in the code.
  One number then answers both the score and the label, so the two never
  disagree.
- **A label reads on the scale of the public problem platforms.** Easy,
  medium and hard mean what the platforms' three levels mean, since a user
  compares a label with those. The criteria for each level are written below.
- **The bands' cuts are set when the first fit scores the corpus.** They are
  read so that the derived labels agree with the criteria below on the served
  problems as often as possible. The criteria then keep the meaning a label had
  before scores existed.
- **Whether a ladder requires an easy rung of a user who passed the recall is
  deferred** until real sittings show what the easy rung adds. A recall checks
  the user types the form, and an easy problem that the user sees it.
- **A problem's `difficulty` is the label the generator aimed at, and stays
  as written.** The generator is told a label by `generate --difficulty`, and
  writes to the criteria below. A problem is never edited, so a score found
  later cannot overwrite that field.
- **A `DifficultyRating` stores one judgement of one problem's score.** It
  carries an engine-minted `id`, the `problem_id`, the `score`, the
  `deviation`, its `source` and `created_at`. A rating with `source` `fit`
  names the difficulty fit that computed it, by `fit_id`. A rating with
  `source` `user` names nothing more.
- **Ratings are product data, global and append-only.** A problem is served to
  every user, so its score is the same for every user. A rating replaced by a
  later one stays readable beside it.
- **The standing difficulty is read at every read and never stored.** The
  standing rating answers, by the standing rule. A `user` rating stands over a
  `fit` one, and among each source's ratings the latest stands. With no
  rating, the problem has no score, and its label is the generator's
  `difficulty`.
- **A problem landed after the latest fit has no score until a fit reads it.**
  Whether a new problem is scored against the members' fitted abilities, or by
  fitting again, is deferred to the first problem landed after the first fit.
- **Every reader of a label reads the standing difficulty.** These readers are
  the badge, the listing's filter and a card's selector.
- **A loaded problem carries the label of its standing score in
  `difficulty`.** The loader folds the ratings in, as it folds the derived
  techniques in. The problem store alone returns the generator's label. A
  reader of the score reads the standing rating, since no record of the
  problem holds a score.
- **A `user` rating is written by hand, in the terminal, beside retirement.**
  It names a score on the contest scale. A learner's reading of a problem does
  not change the score another user is served.
- **The label ratings stored before scores existed are deleted** when the
  `score` field lands, after their labels have informed the bands' cuts. A
  rating carrying a label alone would be a second shape every reader branches
  on, as `README.md` `## Repo constraints` gives.
- **A difficulty estimated from users' attempts is deferred.** Whether an
  estimate is a rating with a source of its own is decided when it is planned.

### Difficulty fits

A difficulty fit scores every problem it reads from the trials of a panel of
models, and links those scores to the contest scale through anchors.

- **The scores come from models, and no user's attempt is needed.** A panel
  is a set of model configurations, each a member, chosen so that the members
  range from weak to strong. A trial is one member's solution to one problem,
  run against that problem's cases.
- **A fit is a difficulty-only item response model over the trials.** Each
  member has an ability and each problem a difficulty. A member solves a
  problem with the logistic chance of the ability minus the difficulty. A
  discrimination per problem is deferred until it lowers the log-loss below.
- **The members are chosen so that solve rates spread between 0 and 1** across
  the corpus. A problem every member solves, or none, carries no difficulty a
  fit can read. Which models, which efforts and how many trials each are
  deferred to the pilot on the anchors.
- **Anchors link the fit to the contest scale.** An anchor is an external
  problem whose contest rating was fitted from the contestants who solved it.
  The panel's trials on the anchors are fitted with the corpus. A linear
  mapping from the fitted difficulty to the contest rating, set on the
  anchors, then converts every problem's difficulty into a score.
- **An anchor is never served, never stored with the corpus and never in
  git.** It is a third-party problem, and `README.md` `## Invariants` keeps
  every third-party statement and case out of git. Each anchor's licence is
  recorded where the anchors are kept, outside this repository.
- **The anchor set is fixed before any trial runs, and named by its hash.**
  The fit record cites the hash, so a fit's scores are traceable to the anchors
  without naming one. A changed anchor set is a new hash, and the fits on the
  old one stay readable.
- **Some anchors are held out of the mapping.** The log-loss of the panel's
  trials on them is the fit's one metric. Each held-out anchor's contest rating
  is converted back to a fitted difficulty, and the chance each member solves
  it is read from the logistic curve. A change to the panel, the model or the
  mapping is kept only where it lowers that log-loss.
- **A `DifficultyFit` stores one fit.** It carries an engine-minted `id`,
  `created_at`, the members' configurations, the anchor set's hash, the
  mapping, each member's ability and the held-out log-loss. Each problem's
  score is a `DifficultyRating` naming the fit. Fits are product data, global
  and append-only.
- **The latest fit stands for every problem it read.** One fit scores the
  corpus at once, so its problems' ratings are mutually consistent. A rating
  from an earlier fit stays readable, and no reader mixes two fits' scores.

### Trials

- **A `Trial` stores one member's solution to one problem and its verdict.**
  It carries an engine-minted `id`, the `problem_id`, the `try_number`, the
  `outcome`, `cases_passed`, `cases_run`, the `cap_ms` and `runner` the cases
  ran under, and `created_at`. The member's configuration, the prompt hash and
  the tokens are its provenance, read off its call as on any machine record.
- **A trial's `outcome` is its severest case outcome**, and `solved` is every
  case run passing. Code that ran no case has no outcome. Per-case results are
  not kept, since a fit reads only whether the member solved the problem.
- **A trial is distinct from an attempt.** An attempt is a user's solution in
  the user's private log. A trial is a model's solution, product data, global
  and append-only. A trial never enters the user's log, and no reader of
  mastery reads one.
- **A trial on a corpus problem is in the store.** Its verdict is read from
  the problem's own cases, by the runner a sitting uses.
- **A trial on an anchor is never in the store**, and neither is the call
  that wrote it. The call's prompt holds the anchor's statement, and no
  third-party statement is stored with the corpus. The trial and its call are
  kept beside the anchors, outside every repository. The trial keeps its own
  shape there, so one fit reads both kinds.
- **The code reading the anchors and running a trial on one lives outside
  this repository.** An anchor reads its input from standard input, where a
  corpus problem's cases call `solve`. That runner and the anchors' format
  belong with the anchors.

### The criteria

The generator aims at a label by these criteria, and the bands' cuts are set
to reproduce them. A rater checks a problem against these in order, and the
first level that fits is the label. Each criterion counts the steps a solution
takes beyond one template's form, so two raters reading one statement reach
one label.

- **Easy: the solution is one basic form applied unchanged, or a direct
  approach that fits the limits.** The basic forms are the templates the table
  below names, most of them on the root cards of the card graph. The statement
  asks the form's own question about the input as given. A solver who holds
  the form types it and adapts only names and the return value.
- **Medium: one standard technique, plus one step the statement does not
  name.** The step transforms the input, chooses a state, or derives the
  predicate a search runs on. A search for the smallest feasible capacity is
  medium: the form is easy, and the feasibility check is the derived step.
- **Medium also covers a form that is itself a step past the basics**, applied
  directly: a monotonic stack, a disjoint set, a topological order, a knapsack,
  a backtracking search, and a choice per element under an adjacency ban.
- **Hard: a form few solvers hold, or two techniques combined, or a step the
  statement gives no hint of.** A sliding-window maximum on a deque and the
  largest rectangle in a histogram are each hard applied directly. So are
  counting the windows with exactly k distinct values by complement, placing n
  queens, and the longest cycle of a graph with one edge out of each node.

### The templates that admit an easy problem

A template admits an easy problem where its form, applied unchanged, answers a
question the platforms label easy. The sweeps write easy problems for these
templates alone.

| Card | Templates admitting easy |
|---|---|
| `binary-search` | `predicate-first-true`, `answer-space` |
| `sliding-window` | `fixed-window-match` |
| `dp-1d-linear` | `two-prev-pick-skip`, `running-aggregate` |
| `hashing` | `complement-lookup`, `count-then-query` |
| `two-pointers` | `compact-in-place`, `merge-sorted-heads`, `converge-sorted-pair` |
| `prefix-sum` | `range-sum-table` |
| `sorting` | `sort-then-sweep`, `composite-key` |
| `stack` | `match-nesting`, `collapse-adjacent`, `evaluate-postfix` |
| `linked-list` | `reverse-in-place`, `fast-slow-middle`, `merge-two-sorted` |
| `tree-traversal` | `inorder-stack`, `inorder-neighbours`, `level-order` |
| `breadth-first-search` | `unweighted-distance` |
| `depth-first-search` | `component-count`, `grid-flood-area` |
| `heap` | `top-k-bounded`, `combine-smallest-two` |
| `binary-search-tree` | `descend-floor-ceiling`, `range-sum-prune` |
| `greedy` | `smallest-sufficient-match` |

- **`converge-sorted-pair` admits easy only in its plainest uses**: a
  palindrome check, squaring a sorted array. A pair sum on a sorted array is
  medium on the platforms.
- **`answer-space` admits easy only where the predicate is given**, as in an
  integer square root. A predicate the solver has to derive makes the problem
  medium, by the criteria above.
- **`two-prev-pick-skip` and `running-aggregate` admit easy only in their
  plainest use**: counting the ways up a staircase, the cheapest climb, the best
  single buy and sell. The adjacency ban and the best contiguous sum are
  medium.
- **`monotonic-stack`, `union-find`, `topological-sort`, `dp-knapsack-01`,
  `dp-state-design` and `backtracking` admit none.** Each form is a step past
  the basics, so its direct use is medium already. These cards take no easy
  rung.

## Test cases

The test cases decide whether a solution to a generated problem is correct.

- **The first set is written with the problem, in the same call.** Cases
  written with the statement describe what the problem asks. Cases derived
  afterwards from a solution describe whatever that solution happens to do.
  Later additions append to the first set rather than replacing it.
- **A case is arguments and an expected return.** Parsing stdin would make a
  case describe how a solution was driven rather than what it must compute.
  The arguments are positional, so a canonical names its parameters whatever
  reads best.
- **The entry point is fixed rather than stored: one module-level `solve`.**
  A stored name lets a statement name one function and a canonical define
  another. A fixed name also stops the signature announcing the approach, as
  `longest_palindromic_substring` would.
- **The statement carries the signature, and one contradicting its canonical
  does not land.** Three prompts would otherwise infer the parameter order from
  prose apart. A reference took `solve(capacity, times, sizes)` where the
  canonical took `solve(times, sizes, capacity)`, and answered no case.
- **A problem needing more than one entry point is not expressible**, and that
  is accepted. A structure asked for by its operations has no single function.
  If one is ever wanted, `entrypoint` is an additive field whose absence means
  the convention.
- **Test cases make verification reachable.** The engine judges a submission
  itself rather than recording a verdict it did not produce.
- **The cases are owned, so the git invariant binds nothing the product
  ships.** The git invariant forbids third-party test cases in any repo, and
  the cases a generated problem carries are the product's own.
- **Expected outputs come from the reference, never from the canonical.** A
  case the canonical produced passes by construction, and `verified` then
  means only that the solution agrees with itself. A reference that computed
  no case therefore rejects the draft. The generator's declared values are
  neither a source nor a gate, as `flows.md` gives.
- **A case records where its expected output came from.** Beyond the largest
  input the reference finishes at generation time, only the canonical can
  compute an expected output, and such a case is evidence about the cap rather
  than about the verdict. Two cases in a set are not equally strong, and only
  the `expected_from` field says which is which.
- **A case names the call that proposed its arguments.** That call is not the
  problem's own wherever a mutation round or the speedup search won the case.
  Three sites write cases at three configurations, and a reader taking the
  problem's provenance would attribute a round's case to the generator.
- **A case names the round that won it, zero for the set the first round was
  run against.** Replaying the discrimination site needs that set as it stood,
  since the set decides which mutants survive and goes into the prompt. Zero
  covers the statement's cases and the fuzz pass's, which provenance tells
  apart.
- **The separating case names no round.** The separating case is appended
  after the loop, so it was never in the set the survivors were decided
  against. Zero would put the separating case in the set a replay rebuilds. An
  absent round keeps the case out without inventing a round nothing ran.
- **Cases that separate nothing are worse than none**, because they license the
  word `verified` on a canonical that is wrong. The mutation loop strengthens
  the set before landing, over at most two rounds, and appends every case it
  wins.
- **No survivor count blocks landing.** The survivors left after the rounds
  are counted on the discrimination site's outcome, and the problem lands
  with them. A bar refusing a problem on that count does not exist.
- **The cases define the problem, and the statement can disagree with them.**
  A finite set of arguments and returns describes some function. The statement
  is prose, so a mistake lands in the statement rather than in the cases.
- **A case set a deterministic canonical passes is already consistent.** Two
  cases with the same arguments and different returns fit no function, so no
  canonical can pass both. No separate check for consistency runs.
- **Cases are appended, never revised.** An edge case, or a case that forces a
  timeout, is added. An addition leaves behind a canonical needing
  re-verification, and never a record that is now wrong.
- **A case carries its arguments literally, and weighs at most 1 MiB.** The
  ceiling covers the arguments and the expected value together. A separating
  input is the largest a case ever holds, and separating a quadratic solution
  from a linear one takes some ten to thirty thousand elements. A seed and a
  size would store less. Such a case would name how its input is built rather
  than what the input holds, and a run would build the input before judging
  it.
- **A separating case may carry a repeat count**, and the cap covers the calls
  together. A form whose one application is sublinear separates on no input the
  ceiling holds, since a linear scan of the largest storable array takes two
  milliseconds. Repeating the call reaches the cap on an input a case can carry.
  Every other case carries one call.
- **The calls of one case are identical, and each runs on a fresh module.** A
  memo left in a global would otherwise answer the second call from the first.
  A submission that stores its answer outside the module still passes such a
  case, and `README.md` gives why the loop does not guard a verdict against
  that. The count separates the two solutions the engine wrote, and neither of
  them caches.
- **The canonical finishes within a tenth of the cap** at the size and count
  the case stores. A case the canonical only just answers fails a correct
  submission a few percent slower. The margin makes the case a test of the form
  rather than of the machine that ran it. The two solutions are within a
  constant factor when the naive solution is over the cap and the canonical
  over a tenth of it, and no count separates them.
- **The separating case is chosen against the sitting's cap**, and never
  against generation's. The separating size is the size at which a submission
  that did not use the form fails, so the cap a sitting judges under decides
  that size.
- **A separation at the smallest legal input is a whole verdict.** Eight of the
  first fifteen searches separated at one or two. The naive solution scans a
  range taken from the values the input carries, and a legal input carries
  values large enough at any size. The naive solution exceeds the cap on
  inputs smaller than the statement admits, so every legal input teaches the
  form.
- **A size is comparable only within one naive solution's cost.** A form whose
  naive solution is exponential in the size separates in the tens. A form
  whose naive cost the values drive separates at the smallest legal input,
  against the same bound of a hundred thousand. Two sizes drawn from two naive
  solutions say nothing about each other.
- **A problem whose template claims a speedup lands with the case that
  separates it, or it does not land.** A rung teaches the claimed speedup, and
  a problem the naive solution also solves does not exercise the form.
  `flows.md` gives how a draft without that case is held and leaves.
- **Consistent is not the same as statable.** A set fitting only "compute f,
  except return 7 on this input" is a function nobody can write a statement
  for. Such a problem does not land: the reference, written from the
  statement alone, disagrees with the set, and the `disagreed` gate rejects
  the draft.
- **The mutation loop that appends cases is in `flows.md`**: the fuzz pass,
  the shrink and the rounds.

## Solutions

A solution the engine wrote for a problem, in one of three roles.

- **The canonical displays the template's form**, and a rung teaches the
  canonical. It is exemplary rather than merely correct.
- **The reference is written from the statement alone**, and it computes the
  expected outputs. Independence is its whole purpose, so a solution
  displaying the form could not serve as a reference.
- **The speedup search times the naive solution.** The naive solution is the
  approach the card's form replaces, and the search measures the canonical
  against it. The reference once held both jobs, and the jobs conflict. The
  reference job needs a blind reading, and the naive job needs a solution that
  does not reach the form.
- **The naive solution is excluded from what a canonical answers for**, as the
  reference is: no solution claim, no template match, no rung. It is the
  approach the card exists to replace.
- **The naive solution is stored at landing, as the reference is.** A replay
  re-runs the search over the stored problem, and re-deriving the naive
  solution would re-pay the call that wrote it.
- **The role is stored, because all three roles are verified against the same
  cases.** Passing says nothing about which role a solution holds, and a
  reader taking a reference for a canonical would teach the approach the card
  exists to replace.
- **A template match is keyed to a solution.** A form is displayed by code, so
  which form is a question about the solution, and a statement only implies
  one. The matcher reads the canonical beside the statement, and the verdict
  is about the canonical.
- **A problem may carry several canonicals, and together they say what it
  teaches.** Two approaches to one problem is the ordinary case, and two
  canonicals let one rung cover a core template and an optional one. A
  problem carrying one canonical can teach one form.
- **A template is the origin of a problem, and never the origin of its later
  solutions.** The later canonicals are enumerated: a call over a landed
  problem proposes the approaches that solve it, and each proposal is
  generated as its own canonical. Asking for a solution by template would
  reach only forms someone authored, where enumeration reaches the techniques
  no card covers.
- **Enumeration is deferred until a ladder needs a second canonical for the
  matcher to read.** No code proposes further canonicals today, so each
  problem carries the canonical the generator wrote.
- **A later canonical carries less assurance than the first.** The case set
  was built to kill mutants of the first canonical, so a second approach
  passing those cases was never tested on its own failure modes. The later
  canonical is stored and it teaches. Re-running the mutation loop over the
  later canonical would close the gap.
- **A solution is never counted as an attempt**: no user and no sitting. A
  solution answers no board row and earns no progress, and a user who reads
  one has not solved the problem.
- **A canonical is sampled, not greedy, which is the exception `machine.md`
  names.** Generation produces the artifact rather than a verdict about one,
  so no verdict needs protecting from variance. Variance stops one model's
  habits becoming the whole corpus. The cost is a canonical that is
  re-runnable and never reproducible, which is also why nothing re-derives it.
- **A solution is immutable once written.** Whether a solution passes is a
  fact about a run, so nothing about how it ran is stored on the solution.

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

## Verification runs

A verification run is one execution of a solution against a problem's cases.

- **A verification is its own record, because the outcome is a fact about the
  run.** The cap and the machine decide a timeout, and a crash can come from
  the runner rather than the solution. A result stored on the solution would
  claim a permanence it does not have.
- **Re-running is legal and expected**, as re-deriving a solution claim is.
  Two runs of one solution are two records, and neither run supersedes the
  other.
- **The cap is stored beside the results.** The cap decided any timeout, and
  two runs under different caps are not comparable. No other field would show
  that the caps differ.
- **The runner and the interpreter are named, as one opaque string.** A local
  subprocess and a container under a CPU limit decide a timeout differently,
  and nothing else separates two runs that disagree. Full environment
  provenance is deferred, and subsumes this field rather than replacing it. A
  separating size is likewise a fact about the runner that found it.
- **The verification result is per case, and names how each case went**:
  passed, wrong, timed out or crashed. A share cannot say which input timed
  out, and the set of cases that passed cannot say why the rest did not. A
  failure mode is read from which case failed and how. An attempt's
  verification stores the same result.
- **A run covers the whole case set**, including the cases it answered
  before. A run answering only the cases added since the last run would fold
  to their outcome alone and say nothing about the rest. Executing code is
  cheap where a model call is not.
- **The outcome over the run is folded, never stored**, and it uses the four
  outcomes a case uses. A timeout is a fact about the run that surfaces at one
  case, so the level it is read at does not change what it means.
- **The most severe failure stands in that fold.** A solution that only ran
  slowly is otherwise correct, which is a different remedy from one returning
  a wrong answer. An empty set folds to nothing rather than to passed, or the
  fold would claim a verification that never ran.

## Execution

How a solution is run. The runner is a component and can be replaced. A
`Verification` is append-only and cannot. So the meaning of a stored result is
fixed here rather than by whatever executed it.

- **The cap is wall clock around the `solve` call, measured in the child.**
  Interpreter start is excluded, since it moves with the machine's load. Two
  runs storing one number would otherwise not be comparable.
- **A case is decided by JSON equality on the returned value**, encoded with
  sorted keys. A tuple and a list are one answer under that rule, and `True`
  and `1` are two.
- **A statement asks for a value that compares exactly**: integers, strings,
  booleans and lists of those. A floating-point answer is compared bit for bit,
  and two correct solutions computing a ratio in different orders disagree in
  the last bits. Such a draft is rejected as `disagreed` however sound the
  statement is. A ratio is asked for as a reduced numerator and denominator.
- **A problem admitting several correct returns does not land.** The
  alternative is a checker per problem, and every stored verdict would then
  depend on code the record does not name. The statement says how ties are
  broken, and a canonical and a reference disagreeing catches a statement
  that does not. The rule excludes a problem asking for any valid answer of
  many, and that cost is accepted until a core template needs one.
- **A return that JSON cannot encode is `CRASHED`.** The fault is the
  solution's rather than the case's. `WRONG` would file it beside an answer
  that was computed and is merely incorrect. The child does the encoding, so
  every runner uses the encoder `as_json` uses, or the same return would be
  decided differently by where it ran.
- **A solution defining no module-level `solve` fails every case as
  `CRASHED`.** Code that does not parse is rejected the same way. It is a
  verdict rather than an error, because a sitting reads this path for an
  attempt, and a submission with a syntax error is the ordinary case.
- **A crashed case carries what raised it**, as a traceback prints it over the
  solution's own lines. The runner's frames are left out, since they name no
  line the solver wrote. The solver reads which line raised, and a diagnosis
  reads a compile error the outcome alone would lose.
- **The error is stored on the case result**, not only shown. `log.md` has a
  diagnosis read a compile error months after the attempt, when only the record
  is left.
- **A wrong case stores the JSON it returned**, up to 64 KiB. A reopened
  sitting reads the failing case back from the record, and no rerun is spent
  on it. A larger return is not kept, since a 1 MiB case answered wrong on
  every submission would grow the log by that much each time. A case result
  written before the field existed keeps no return either, and the page says
  so.
- **No case observes another.** A solution memoising in a module global would
  otherwise answer one case from a cache built for a different one, and a wrong
  key would pass. Which mechanism gives that isolation is the runner's to
  choose.
- **A runner fault is raised, never recorded.** A subprocess that fails to
  start says nothing about the solution, and a stored `CRASHED` would reject a
  sound draft over the runner's own defect.
- **Comparison stays outside the runner.** A runner is handed code, the
  arguments and a cap, and returns what each call produced. The runner is
  never told what a case expects, so the rule deciding a case cannot vary by
  where the code ran.
- **A case yielding no value is read by the solution's role.** A canonical that
  crashed or timed out rejects the draft, since nothing establishes what the
  case returns. A reference that crashed or timed out is the ordinary path
  beyond its reach, and the case takes the canonical's answer, with
  `expected_from` naming the canonical.
- **The stored cap is the child's**, since that is the number the case was
  judged by. The parent runs a slack timer of its own, which the runner owns.
- **A child reporting nothing is read from how it died.** The parent's timer
  firing is `TIMEOUT`. A signal is `CRASHED`, and a segfault and a kill under
  memory pressure both land there. Anything else is the runner's own fault and
  is raised, since it says nothing about the solution.
- **A case result carries what the child measured.** The separating input a
  speedup search looks for is found from those numbers, and a result holding
  only the outcome would make every later search re-run the whole set.
