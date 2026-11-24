# The questions page

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /author/questions?module=algo&kind=output ----------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Questions                                                              |
|                                                                        |
| Module   [ algo ]  python  py                                          |
| Topic    sorting 14  searching 9  graphs 22                            |
| Level    0 12  1 18  2 11  3 4                                         |
| Kind     concept  [ output 45 ]  pattern  debug                        |
| Format   choice 38  short 7  open 0                     ( Clear )      |
|                                                                        |
| Algorithms                                                       45    |
| +--------------------------------------------------------------------+ |
| | Slug              Subtopic     Level▾ Kind   Format Prompt    Code | |
| |--------------------------------------------------------------------| |
| | merge-split-trace Merge sort   1      output choice What do…  12   | |
| |▌merge-stable-ties Merge sort   2      output choice Which o…   4   | |
| | merge-count-calls Merge sort   2      output short  How man…   7   | |
| | bisect-left-trace Binary sea…  1      output choice What do…   9   | |
| | …                                                                  | |
| +--------------------------------------------------------------------+ |
+------------------------------------------------------------------------+
```

A row pressed opens the question in the dialog:

```
+- /author/questions?module=algo&kind=output#merge-stable-ties ----------+
|      +-------------------------------------------------------------+   |
|      | ‹ › 2 of 45  merge-stable-ties                            ✕ |   |
|      | Merge sort . level 2 . output . choice                      |   |
|      |-------------------------------------------------------------|   |
|      | Which order do the equal keys come out in?                  |   |
|      |   def ...                                                   |   |
|      |   [ A  the input order ]   correct                          |   |
|      |        Merge takes from the left run on a tie.              |   |
|      |   ( B  reversed )                                           |   |
|      |        Believes merge takes from the right run on a tie.    |   |
|      | Explanation  ...                                            |   |
|      | How it works  ...   Example  ...   Pitfalls  ...            |   |
|      |                                                             |   |
|      | Concept  merge-is-stable . level 2                          |   |
|      |   Merge sort keeps equal keys in their input order.         |   |
|      |   source                                                    |   |
|      +-------------------------------------------------------------+   |
+------------------------------------------------------------------------+
```

- The author navigation sits left of the page, as `../navigation.md`
  draws it, and is left out here.
- The module chips pick one module, and the other filters' chips count what
  pressing each would leave.
- `▾` marks the column the rows are sorted by, and `▌` the row last opened.
- The dialog holds the reading column's width over the grid. `‹ ›` step as
  `j` and `k` do. The question reads as the queue draws it answered, then
  its concept.
