# Verification runs

A verification run is one execution of a solution against a problem's cases.
`../../api/runner.md` gives how the runner executes it and what a stored result
means.

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
