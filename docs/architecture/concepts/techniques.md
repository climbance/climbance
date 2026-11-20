# Techniques

The technique vocabulary: every technique the append-only log references, each
with the criterion for claiming it. The vocabulary ships with the package, and
every container reads it: the classifier's prompt, the board, mastery, the
cards and the knowledge modules.

## Claiming a code

- **A code carries the criterion for claiming it**, not only its name: its
  kind, what earns it, and the near miss it is confused with. The near miss
  decides cases, because disputes are about boundaries rather than definitions.
  The codes are four kinds of thing, and one question is answered differently
  for each.
  - A procedure counts when the solution performs it.
  - A structure counts when its properties carry the correctness or the
    complexity.
  - A paradigm counts when the paradigm is the reason the solution is correct.
  - A problem class counts when the problem asks for that class.
- **A kind reaches both readers as its test, never as its name.** The label
  helps only a reader who already knows what the kind selects. A reader who
  does not will judge a structure on whether the structure was performed. The
  four tests live with the kind, so the entries state them once.
- **A code is claimed beside the narrower ones, never instead of them.** A
  solution's approach is true at several levels: a backtracking search
  descends, and a search tree is a binary tree. An exclusive rule would need a
  containment order over the codes, and nothing generates one. Such an order
  could only be written by hand pair by pair, then disagreed with case by case.
  Exceptions are per code and stated in the entry: `recursion` names a
  language mechanism rather than an approach, so a row counting every
  self-call would name no skill.
- **Only incidental use disqualifies a code.** Another
  candidate covering the code does not. The near miss states that line in
  full: a sorted lookup beside a linear pass that dominates, a map standing in
  for an array. A reader taking the near miss for precedence drops codes the
  user claimed.
- **Inclusive claiming keeps a row coherent.** The fallback is the problem's
  own techniques, and those nest already. Under an exclusive rule a claimed
  attempt and an unclaimed one on the same problem would be counted
  differently, so board numbers would move as classification progressed while
  the practice behind them did not.
- **The criteria are the prompt.** They reach the classifier beside the
  candidates and the reader beside the code, so one set of criteria answers
  both. Editing an entry changes machine claims, but only for the attempts
  carrying that candidate.

## Parents

- **A code may name its parents, each a code it is a kind of.** Interval DP
  is a kind of DP, so `interval-dp` names `dynamic-programming`. A code with
  a parent is defined as a narrowing of that parent, so the parent is part of
  the definition rather than a judgement made pair by pair. Containment
  between codes defined apart stays unwritten, since nothing generates it.
- **A parent is added wherever codes are grouped**, and never written into a
  claim. A claim keeps the codes its writer named. The board, mastery and a
  problem's techniques count a claim naming `knapsack` toward
  `dynamic-programming` as well.
- **A parent means only "is a kind of".** A code that always uses another, as
  a bitmask DP uses bit operations, does not name it as a parent. Whether one
  code always uses another is a judgement per pair, and the classifier makes
  it from the criteria as it makes any claim.

## The vocabulary as code

- **Versioned as code, not stored as data.** A file shipped with the package,
  not a datastore the engine writes.
- **A code is never deleted**, because records carrying it outlive it.
  Retirement means an entry in an alias map, applied when grouping. The map is
  deferred until a code is first retired, since none has been.
- **The vocabulary is read-only once loaded.** Its entries reach a prompt and
  a reader unchanged. An entry edited in memory would be a criterion the file
  does not carry, and nothing could re-derive the machine claims that entry
  produced.
- **Membership is checked on the write path only.** A model that validated
  codes on read would make the log unreadable by its own schema the moment a
  code was retired.
