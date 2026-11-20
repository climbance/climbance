# Solutions

A solution the engine wrote for a problem, in one of three roles: canonical,
reference or naive.

## The three roles

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

## Several canonicals

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

## What a solution is not

- **A solution is never counted as an attempt**: no user and no sitting. A
  solution answers no board row and earns no progress, and a user who reads
  one has not solved the problem.
- **A canonical is sampled, not greedy, which is the exception
  `../../concepts/machine-records.md` names.** Generation produces the
  artifact rather than a verdict about one, so no verdict needs protecting
  from variance. Variance
  stops one model's habits becoming the whole corpus. The cost is a canonical
  that is re-runnable and never reproducible, which is also why nothing
  re-derives it.
- **A solution is immutable once written.** Whether a solution passes is a
  fact about a run, so nothing about how it ran is stored on the solution.
