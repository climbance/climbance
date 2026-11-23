# The problems page

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /author/problems?technique=two-pointers ------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Problems           Product  Generation  Workflow                       |
|                    Questions  Lessons  Cards  [ Problems ]             |
|                                                                        |
| Technique  [ two-pointers 9 ]  sorting 3                               |
| Difficulty easy 3  medium 5  hard 1                                    |
| Status     [ served 9 ]  retired 1                       ( Clear )     |
|                                                                        |
| > 3f9a2c71  Pair sums under a cap  same-direction  easy  14 cases  CRN |
| v b04e18d2  Closest pair           same-direction  1240 medium         |
|             two-pointers . 22 cases . CRN . 1 request                  |
|   +------------------------------------------------------------------+ |
|   | Closest pair                                                     | |
|   | Given a sorted list ...                                          | |
|   +------------------------------------------------------------------+ |
|   Canonical   displays same-direction . claims two-pointers  passed    |
|     def solve(...): ...                                                |
|   Reference   passed                                                   |
|     def solve(...): ...                                                |
|   Naive       passed                                                   |
|     def solve(...): ...                                                |
|   Cases   1  ([1, 4, 9], 10)          -> 1                             |
|           17 ([3, 3, 8, ...], 6)       -> 0      round 1               |
|           22 ([0, 1, 2, ...], 99)      -> 98     repeats 40            |
|   Difficulty  1240 ± 90  standing . 1310 ± 140 . generator medium      |
+------------------------------------------------------------------------+
```

- `CRN` names the solutions by role: canonical, reference and naive.
- A closed row reads on one line where it fits, and on two otherwise.
- An opened row reads the statement as served, the solutions by role, the
  cases, then the difficulty.
