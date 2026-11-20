# Test cases

The test cases decide whether a solution to a generated problem is correct.

## What a case is

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
- **A case carries its arguments literally, and weighs at most 1 MiB.** The
  ceiling covers the arguments and the expected value together. A separating
  input is the largest a case ever holds, and separating a quadratic solution
  from a linear one takes some ten to thirty thousand elements. A seed and a
  size would store less. Such a case would name how its input is built rather
  than what the input holds, and a run would build the input before judging
  it.
- **Every case is weighed before it joins the set.** A case the generator or
  a round proposed over the ceiling is dropped as it is settled, as the fuzz
  pass and the search drop theirs, so no stored case exceeds the ceiling.

## Where a case came from

- **Expected outputs come from the reference, never from the canonical.** A
  case the canonical produced passes by construction, and `verified` then
  means only that the solution agrees with itself. A reference that computed
  no case therefore rejects the draft. The generator's declared values are
  neither a source nor a gate, as `README.md` gives.
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

## What the set must decide

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
- **Consistent is not the same as statable.** A set fitting only "compute f,
  except return 7 on this input" is a function nobody can write a statement
  for. Such a problem does not land: the reference, written from the
  statement alone, disagrees with the set, and the `disagreed` gate rejects
  the draft.
- **Cases are appended, never revised.** An edge case, or a case that forces a
  timeout, is added. An addition leaves behind a canonical needing
  re-verification, and never a record that is now wrong.
- **The mutation loop that appends cases is in `mutation-loop.md`**: the fuzz
  pass, the shrink and the rounds.

## The separating case

- **A separating case may carry a repeat count**, and the cap covers the calls
  together. A form whose one application is sublinear separates on no input the
  ceiling holds, since a linear scan of the largest storable array takes two
  milliseconds. Repeating the call reaches the cap on an input a case can carry.
  Every other case carries one call.
- **The calls of one case are identical, and each runs on a fresh module.** A
  memo left in a global would otherwise answer the second call from the first.
  A submission that stores its answer outside the module still passes such a
  case, and `../../README.md` gives why the loop does not guard a verdict
  against that. The count separates the two solutions the engine wrote, and
  neither of them caches.
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
  `speedup-search.md` gives how a draft without that case is held and leaves.
