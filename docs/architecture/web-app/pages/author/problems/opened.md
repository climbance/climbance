# The problems page, a problem opened

A wireframe of the page `README.md` specifies, drawn at low fidelity, with
one problem opened in the dialog. `../../../README.md` gives how a wireframe
is read.

```
+- /author/problems?landed=7d#b853101e ----------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
|  +-------------------------------------------------------------------+ |
|  | ‹ › 2 of 12  Smallest Valid Cyclic Shift                       ✕  | |
|  | b853101e ⧉  served  deficit-reset-start . greedy                  | |
|  | 1109 ± 265 medium . 14 cases                                      | |
|  | a-model, medium @default, 3f2a… @ pin                             | |
|  |-------------------------------------------------------------------| |
|  | +- statement, as a ----+  Canonical  displays deficit-reset-start | |
|  | | learner reads it     |    a-model, medium @default, 9c1e… @ pin | |
|  | |                      |    def solve(...): ...           passed  | |
|  | | Given a list of      |  Reference                       passed  | |
|  | | gains and costs …    |    def solve(...): ...                   | |
|  | |                      |  Cases  1  ([1, 2], [2, 1])  -> 0        | |
|  | | Example …            |        14 ([5, 1, …], …)    -> 3 round 1 | |
|  | |                      |  Difficulty  1109 ± 265  standing        | |
|  | | def solve(gains,     |              generator medium            | |
|  | |   costs): ...        |  Sites  generator  a-model  killed 9     | |
|  | +----------------------+         naive  a-model  separating 4096 | |
|  |-------------------------------------------------------------------| |
|  | ⧉ retire defective  ⧉ retire copied  ⧉ rate by hand               | |
|  +-------------------------------------------------------------------+ |
+------------------------------------------------------------------------+
```

- The dialog covers the page with a margin, and the list reads full rows
  underneath it. The author navigation sits under the dialog too.
- The head reads the position among the rows, `‹ ›` stepping as `j` and `k`
  do, then the problem's id, status, target, techniques, score and
  configuration.
- The statement reads as served in the left column. The solutions by role,
  the cases, the difficulty and the site outcomes read in the right one.
- `⧉` copies: the id in the head, each command in the foot.
