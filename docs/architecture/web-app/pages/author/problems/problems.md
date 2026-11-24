# The problems page

A wireframe of the page `README.md` specifies, drawn at low fidelity, with
no problem opened. [`opened.md`](opened.md) draws it with one opened.
`../../../README.md` gives how a wireframe is read.

```
+- /author/problems?landed=7d -------------------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Problems                                                               |
|                                                                        |
| served ▾  technique ▾  target ▾  difficulty ▾  landed: 7d ▾            |
| ( Needs attention 3 )                                     12 rows      |
|                                                                        |
| +--------------------------------------------------------------------+ |
| | Title               Target         Techniques  Score  Cases Flags  ▾ | |
| |--------------------------------------------------------------------| |
| | Sliding Window Tem… deque-window…  sliding-wi… 1312±265  13 untagged| |
| |▌Smallest Valid Cyc… deficit-rese…  greedy      1109±265  14         | |
| | Circular Circuit P… deficit-rese…  greedy      1109±265  14         | |
| | …                                                                  | |
| +--------------------------------------------------------------------+ |
+------------------------------------------------------------------------+
```

- The author navigation sits left of the page, as `../navigation.md`
  draws it, and is left out here.
- The filters read on one line, each a menu naming its value, above the
  attention filter and the count of rows.
- A row reads on one line. The landed column sits right of the flags, out of
  this drawing's width, and `▾` there marks it as the sort.
- No row shows the id or the solutions by role. The dialog shows both.
