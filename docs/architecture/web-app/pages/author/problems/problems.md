# The problems page

A wireframe of the page `README.md` specifies, drawn at low fidelity, with
no problem opened. [`opened.md`](opened.md) draws it with one opened.
`../../../README.md` gives how a wireframe is read.

```
+- /author/problems?landed=7d -------------------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Problems        Inbox 5                                                |
|                 Questions  Lessons  Cards  [ Problems ]                |
|                 Product  Generation  Spend                             |
|                                                                        |
| served ▾  technique ▾  target ▾  difficulty ▾  landed: 7d ▾            |
| ( Needs attention 3 )                        12 rows  sort: newest ▾   |
|                                                                        |
| Sliding Window Temperature Peaks  deque-window-max  1312 ± 265 medium  |
|   sliding-window . 13 cases                        ⚑ untagged titled   |
| Smallest Valid Cyclic Shift  deficit-reset-start    1109 ± 265 medium  |
|   greedy . 14 cases                                                    |
| Circular Circuit Power Run   deficit-reset-start    1109 ± 265 medium  |
|   greedy . 14 cases                                                    |
| Minimum Fiber-Optic Segments farthest-reach-levels  1211 ± 265 medium  |
|   greedy, intervals, shortest-path . 16 cases                          |
| …                                                                      |
+------------------------------------------------------------------------+
```

- The filters read on one line, each a menu naming its value, above the
  attention filter and the count of rows.
- A row reads on one line in a wide window. At this drawing's width it wraps
  to two: the title, the target and the difficulty, then the techniques, the
  cases and the flags.
- No row shows the id or the solutions by role. The panel shows both.
