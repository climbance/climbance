# Generation

`climb generate` writes the corpus: each problem, the test cases that decide
it, and the solutions written for it. A problem is written across six calls,
and the order matters because each step can reject what came before.

| File | Holds |
|---|---|
| [`problem.md`](problem.md) | The problem record: its target, its techniques, its statement |
| [`test-cases.md`](test-cases.md) | The test cases, where each came from, and the separating case |
| [`solutions.md`](solutions.md) | The canonical, the reference and the naive solution |
| [`verification-runs.md`](verification-runs.md) | A run of a solution against a problem's cases |
| [`site-outcomes.md`](site-outcomes.md) | What each call site left on one writing |
| [`states.md`](states.md) | The writing states a draft is stored at, and resuming a draft |
| [`speedup-search.md`](speedup-search.md) | Steps 7 to 9 and 11: the input generator, the naive solution, the search |
| [`mutation-loop.md`](mutation-loop.md) | Step 10: the mutants, the fuzz pass and the rounds |
| [`replay.md`](replay.md) | Replaying the answering sites over stored problems |
| [`enumeration.md`](enumeration.md) | Enumerating a problem's other solutions, deferred |

## Generating a problem

1. The target: a template, naming the form the problem must be solvable by, or
   a technique, naming only the skill. The technique target is deferred, as
   `problem.md` gives.
2. The statement, the canonical solution and the first test cases, from one
   call.
3. The canonical runs, and its outputs are read against the expected values
   the same call declared.
4. A judge reads the statement and the cases for an example, values or
   wording taken from a published problem, and rejects a copied draft.
5. The reference solution, from the statement alone.
6. The reference runs, and the two solutions' outputs are settled: they agree
   on every case, or the draft is rejected.
7. Code that builds an input of a given size and seed, from the statement
   alone.
8. A deliberately naive solution, from the statement and the form it may not
   use, on a template that claims a speedup.
9. The smallest input separating that solution from the canonical under the
   cap is searched for.
10. Mutants of the canonical run against the cases, then against inputs that
    code builds. A call asks for the cases that kill whichever mutant survived
    both, and the ones that killed are appended to the set.
11. The case at the separating size is appended after them.
12. All of it lands together, with the template match the generation asserts
    on its canonical.

## Every step

- **Problems for one template are written one at a time.** Each call is shown
  the statements the form already has, so two in flight would be shown the
  same list and could write the same problem twice. Concurrency saves minutes
  and costs the diversity the target exists to enforce.
- **The first problem written for a template is the standard problem its
  form is known by.** A learner meets the form first on the question it is
  usually taught with. Many learners have not met that question, and the
  later problems for the template train recognition. Each later problem asks a
  question the earlier ones do not, in any setting, the trigger's own
  included.
- **A draft lands only once every gate has passed.** A draft failing any step
  stops there, and only one that passed every gate becomes a problem. The
  draft is kept where it stopped rather than deleted, so a fixed step can
  resume from there. `states.md` gives the states.
- **A landed problem is never repaired.** A stored problem carries attempts
  and its cases are append-only, so every fix is a resumed draft. A step that
  has no answer therefore stops the writing rather than lowering what a
  landing requires.
- **Every step's verdict is recorded, not only reported.** A run prints each
  stage and the process then ends, so a rejected draft would leave only the
  calls it paid for. `site-outcomes.md` gives what a site's record carries.
- **A run ends on what it reached, and prints no statement.** Each problem
  the run stored is a line naming the id, and the author problems page reads
  one problem whole. Ten statements scroll the result out of the terminal.

## Steps 2 and 3: the canonical's own cases

- **Failing means two things on the cases written with the statement.** The
  first canonical is run before any expected value is settled, so it fails
  only by yielding no value on some case, and the draft is rejected. A later
  canonical is judged by the cases the problem carries, so it fails as any
  solution does, and nothing is rejected.
- **The generator's own expected values are a reading, not a gate.** The call
  that wrote the canonical also declared what each case returns, so the two
  share one reading of the statement, and a contradiction between them is that
  call's arithmetic. A landing case stores the reference's answer. The values
  were a gate once, as `misdeclared`: of ten writings on one template it
  rejected four, and the two checked by hand had the canonical right and the
  declared value wrong. So a mismatch is counted rather than rejected.
- **The count is filed on the generator's own record.** The count says how
  often a configuration's hand-computed value contradicts its own code, which
  is a fact about that site rather than about the problem.

## Step 4: the screen

- **The screen runs before the reference.** A copied draft then costs the
  screen's call alone, rather than the four calls after it.
- **The screen reads the statement and every declared case.** A published
  example reaches a draft as the worked example or as a case's arguments.
- **A retold question is not copied.** A question is free to reuse, and a
  published statement's text and example values are not. An easy problem
  applies a template's form unchanged, so its question is usually a published
  one. The screen rejects reused values and reused wording only.
- **The screen names the published problem it found**, in the site outcome's
  `detail`, so a reader can check the verdict. The record holds the name
  alone, never the published statement.
- **The screen answers from memory, and a miss passes silently.** A model that
  does not remember a published example lets it through. Which configuration
  recalls the most is unmeasured.
- **A copied draft is rejected, not held.** A second generator call writes
  new values, so nothing would re-run this one.
- **The generator is shown what the screen named on its template's earlier
  drafts.** A rejected draft is never stored, so without the list the next
  call receives the same prompt and reproduces the same published example.
  Each `copied` site outcome's `detail` for the template is listed as an
  example to avoid. On the greedy card, nine calls in a row reproduced the
  published examples of Jump Game II, Gas Station and Remove K Digits.
- **The problems already stored are screened by a replay**, `generate --replay
  --only screen`. They landed before the screen existed. A copy the replay
  names is retired by hand, as `copied`.

## Steps 5 and 6: the reference

- **The reference is written blind.** Shown the canonical, the reference would
  inherit that solution's reading of the statement. Agreement would then show
  only that one model is consistent. Blind, agreement is evidence that the
  statement has one reading, and disagreement on any case rejects the draft.
- **The blind reference rejects the draft.** The reference read the statement
  and nothing else, so a disagreement is evidence the prose admits two
  readings. The generator's declaration is evidence about one call.
- **A disagreement is the statement's fault, not either solution's.** Two
  correct-looking solutions returning different answers means the prose admits
  two readings. An in-place edit cannot repair that, since the cases would
  move with the wording.
- **Every run at generation is capped**, well above the drill loop's cap. The
  largest input the reference finishes at decides which cases carry its
  answer, and an uncapped run is a non-terminating reference hanging the run.
- **The scale case is tautological, and harmlessly so.** Correctness was
  established on the cases the reference computed, and the scale case exists
  for the cap rather than for the verdict. The scale case still catches a
  crash or a recursion limit at size. The scale case cannot catch a canonical
  correct small and wrong large.
- **An alternative canonical, where one exists, restores that independence.**
  The alternative canonical is a second efficient solution from a different
  form, so a scale case can be cross-checked between two canonicals rather
  than taken from one. Enumeration produces the alternative canonical, so the
  cross-check is available on a later pass rather than at landing.
