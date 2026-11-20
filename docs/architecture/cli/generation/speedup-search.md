# Speedup search

Steps 7 to 9 and 11 of `README.md` `## Generating a problem`. The input
generator is written for every problem. A naive solution is written when the
template claims a speedup. The search then finds the smallest input on which
the naive solution exceeds the sitting's cap and the canonical does not. The
case at that size is appended after the mutation loop.

## Step 7: the input generator

- **The input generator is written for every problem**, whatever the target
  named, and before the mutation loop. The fuzz pass kills mutants with the
  inputs the input generator builds, so a round is paid for the survivors
  alone, as `mutation-loop.md` gives.
- **The naive solution is written after the input generator.** The input
  generator is written for every problem, since the fuzz pass builds with it,
  and the naive solution only where a speedup is claimed.

## Step 8: the naive solution

- **The naive solution is written the opposite way**, and told the form it may
  not use. The naive solution settles no case and rejects no draft, so what
  the naive site is shown cannot reach a verdict.
- **The naive solution stands for the approach the form replaces, at that
  approach's cost.** One trying only the values the input carries has used the
  form's insight, and the search then separates nothing. One trying every
  subset where the statement describes a scan separates at a few dozen
  elements, and a submission of the wrong complexity passes inputs that small.
  The prompt states both ends, since a prompt naming one end produces the
  other fault.
- **A naive solution slower than the plain brute force separates too early.**
  The separating case then admits the brute force, which is slower than the
  form and faster than the naive solution. On 2026-11-16, 14 of the 89 served
  problems with a separating case in the local store had such a naive
  solution. Each of the 14 is cubic where the plain brute force is quadratic.
  The cause is a slice summed, a `min` or a `set` taken per pair, every edge
  scanned again per candidate, or a list searched in place of a set. The 14
  separate between n = 521 and n = 1497, under bounds of 100,000 to 200,000.
  A quadratic solution finishes there within the cap. The conveyor problem,
  `longest-valid-window`, separates at n = 907.
- **A naive solution enumerating every choice is the plain brute force**
  where the statement asks to choose, order or partition. The 11 problems
  separating between n = 10 and n = 65 enumerate subsets, permutations or
  unmemoised recursions, and none of the 11 counts in the 14.
- **The naive site is shown the technique's criterion beside the trigger.** A
  model told to avoid one form reaches the technique through a form no
  template names, as tabulation stands in for a memo.
- **The naive solution has to be correct on every case it answers**, and a
  naive solution that is not holds the draft. A case it does not finish is no
  failure, since being slow is its purpose. A naive solution that is wrong
  measures nothing, so a search against it would separate on a mistake rather
  than on the form.
- **A wrong naive solution rejects nothing all the same.** The naive solution
  is the solution the search times rather than a reading of the statement. A
  wrong naive solution establishes that this solution cannot serve, and
  nothing about the problem.

## Steps 9 and 11: the search and its case

- **The search runs before the loop and its case is appended after the
  loop.** The survivors are decided against the set as the statement left it,
  so the separating case may not join that set. Searching first catches a
  canonical wrong at scale before a round is paid for.
- **The walk bisects up to the ceiling first**, since a quadratic naive
  solution often separates within the last factor of two.
- **The input the search measured is the input the case stores.** The input
  generator is asked to build one input per size, and building the input
  again would be a second run of model-written code.
- **The separating case is settled as any other case.** The reference is
  measured well above the sitting's cap, so it usually computes the value the
  separating case stores. A disagreement on the separating case rejects the
  draft, and that disagreement catches a canonical correct on the small cases
  and wrong at scale.
- **A search that stored no case names its reason, and the reasons assert
  different things.** `Missing` in `speedup.py` holds each one.
  - `case_too_large`: a separating size was found and the case at it weighs
    over the ceiling. The speedup is established, and the run reports the
    size and both timings.
  - `naive_finished`: the naive solution finished at the statement's largest
    input. The search has established nothing.
  - `count_too_large`: the naive solution finished at the largest storable
    input, and the repeat count reaching the cap is over its bound. A
    separation may still sit above either bound.
  - `canonical_too_slow`: the canonical took over a tenth of the cap where
    the naive solution exceeded it. The two are within a constant factor, and
    no count separates them.
  - `naive_crashed`, `canonical_failed` and `disagreed`: a solution crashed,
    failed, or the two disagreed at a size the walk reached.
  - `input_too_large`: no storable input separated. Only drafts written
    before the repeat count carry it.

## A draft the search holds

- **A search that fails holds the draft, as one that separated nothing does.**
  The input generator's code can crash, which says nothing about the
  statement. The case a landing needs is missing, and the run reports what
  the search stopped at.
- **A call that wrote no input generator holds the draft too**, where a
  speedup is claimed. No search ran, so the claim is undemonstrated for the
  same reason, and a resume starts at the input generator rather than at the
  search. The missing input generator costs the fuzz pass besides.
- **A naive solution finishing at the largest legal input is a defect in the
  run, not in the problem.** The naive solution reached the form, the input
  generator built a shape the form does not beat, or the template claims a
  speedup it lacks. The run cannot tell the three apart.
- **Such a draft is held, not rejected.** The statement, the cases and every
  solution passed every gate that judges them. Rejecting would keep only the
  problems one model happened to be slow at.
- **A held draft leaves by one of four exits.** A resumed search separates it,
  a second naive draw is slow, the template's `speedup` is corrected and the
  search is skipped, or the draft is rejected by hand as `unexercised`. A
  naive solution writing the form it was told to avoid is the strongest
  evidence the problem does not exercise the form. `states.md` gives how a
  resume re-enters the search.
