# The problems page, a problem opened

A wireframe of the page `README.md` specifies, drawn at low fidelity, with
one problem opened in the panel. `../../../README.md` gives how a wireframe
is read.

```
+- /author/problems?landed=7d#b853101e ----------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Problems        Inbox 5                                                |
|                 Questions  Lessons  Cards  [ Problems ]                |
|                 Product  Generation  Spend                             |
|                                                                        |
| served ▾  technique ▾  target ▾  difficulty ▾  landed: 7d ▾            |
| ( Needs attention 3 )                        12 rows  sort: newest ▾   |
|                                                                        |
|   Sliding Window Tem… ⚑2  │ Smallest Valid Cyclic Shift                |
| > Smallest Valid Cycl…    │ b853101e ⧉  served                         |
|   Circular Circuit Po…    │ deficit-reset-start . greedy               |
|   Minimum Fiber-Optic…    │ 1109 ± 265 medium . 14 cases               |
|   Baseline Temperatu… ⚑1  │                                            |
|   Largest Contiguous…     │ +- statement, as a learner reads it -+     |
|   …                       │ | Given a list of gains and costs …  |     |
|                           │ +------------------------------------+     |
|                           │ Canonical  displays deficit-reset-start    |
|                           │   def solve(...): ...          passed      |
|                           │ Reference                      passed      |
|                           │   def solve(...): ...                      |
|                           │ Cases  1  ([1, 2], [2, 1])   -> 0          |
|                           │        14 ([5, 1, …], …)     -> 3  round 1 |
|                           │ Difficulty  1109 ± 265  standing           |
|                           │             generator medium               |
|                           │ ⧉ retire defective  ⧉ retire copied        |
|                           │ ⧉ rate by hand                             |
+------------------------------------------------------------------------+
```

- The list narrows to each row's title and its count of flags while the
  panel is open, and `>` marks the opened row.
- The panel reads the head, the statement as served, the solutions by role,
  the cases, the difficulty, then the commands.
- `⧉` copies: the id in the head, each command in the foot.
