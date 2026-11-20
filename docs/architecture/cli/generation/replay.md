# Replaying a site

A replay runs the five answering sites over a stored problem, at a
configuration the corpus has not been read by. Generation writes a new problem
every call, so nothing there is ever asked twice and no two configurations
meet the same item.

1. The stored problems, minus the retired ones and any missing a solution in
   either role.
2. Per site, the prompt hash it would send now. A pair this configuration has
   answered at that prompt hash is skipped.
3. The screen site judges the statement for copied material.
4. The blind site writes a reference from the statement, settled against the
   cases the problem carries rather than against the canonical.
5. The discrimination site runs the mutation loop over the stored canonical,
   against the set as it stood before the rounds: the statement's cases and
   the kept fuzz inputs. No fuzz pass runs.
6. The inputs site builds an input generator, where the template claims a
   speedup, and the search measures it against the stored naive solution.
   The naive site then writes a naive solution, judged against the cases.
7. Each site's answer is recorded as its outcome, keyed to the problem.

- **`--only` narrows a replay to the sites it names.** Screening the corpus
  would otherwise pay every other site's call too.
- **A replay writes nothing to the corpus.** A case a round wins here is
  dropped, or the next configuration would be measured against a different
  problem.
- **The loop is replayed against the set as it stood.** A case a later round
  won and the separating case are excluded, since neither was there when the
  survivors were decided. Counting them changes the survivors and the prompt
  hash, and the generation run's own record would then answer for nothing.
- **The discrimination prompt hash is known only after the local kill pass.**
  The survivors are in the prompt, and killing costs subprocesses rather than
  a call, so the skip is decided after that pass and before the call.
- **A retired problem is not replayed.** A defective one was never a fair
  test, and a later corpus will not hold it.
- **The inputs site is asked only where a speedup is claimed**, where the
  landing path builds for every problem. A replay records the verdict a gate
  reached on an answer, and nothing here runs the code the call wrote unless
  a search does.
- **The naive site is asked there too**, where a speedup is claimed. The
  naive site's record carries the configuration and whether the solution it
  wrote answers the problem's cases, since a wrong naive solution rejects no
  draft and so names no gate.
- **The search stays measured against the stored naive solution**, not the
  one this run just wrote. Moving the input generator and the naive solution
  together would leave neither configuration readable from the verdict.
