# Enumerating a problem's other solutions

Deferred until a ladder needs a second canonical for the matcher to read, as
`solutions.md` gives. No code runs the steps below yet.

A landed problem carries one canonical, written for what its target named.
Every other way to solve it is found afterwards, over the stored problem.

1. The statement, the cases it carries and the canonical it already has.
2. A call proposes the approaches that solve it, each as a name and a one-line
   idea.
3. A canonical is generated per approach, one call each.
4. Each runs against the cases the problem already carries, and one that fails
   is not stored.
5. Each stored canonical is read for its techniques and for the templates it
   displays.

- **Enumeration runs over the corpus, never in the landing path.** A proposal
  nobody could write says nothing about the statement, so enumeration cannot
  gate a problem. The list needs no gate of its own either: its length tracks
  the model's verbosity, and a wrong proposal costs one call and lands
  nothing.
- **One call per approach, never one reply carrying all of them.** A single
  bad entry would otherwise fail the whole batch, where each canonical is
  judged on its own.
- **The proposing call sees the first canonical.** Independence is the
  reference's purpose rather than this call's. This call is asked for
  approaches that differ from what is stored, and that needs the stored
  canonical in view.
- **A canonical enumeration produced is not a reference.** The enumerated
  canonical saw the statement, the cases and another solution, so it is no
  independent reading. The enumerated canonical cannot reject a draft, and
  its failure says nothing about the statement.
- **Execution cannot catch duplicates.** Top-down and bottom-up dynamic
  programming pass the same cases, and only a template match separates them.
  The handling of two canonicals of one form is deferred until a corpus shows
  how often it happens.
