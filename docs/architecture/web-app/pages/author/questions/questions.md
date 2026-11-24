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
|                                                    ( Open all )        |
|                                                                        |
| Sorting . Merge sort                                         6         |
| > merge-split-trace   1 output choice  What does this print?   12 lines|
| v merge-stable-ties   2 output choice  Which order do the ...    4 lines|
|   +------------------------------------------------------------------+ |
|   | Which order do the equal keys come out in?                       | |
|   |   def ...                                                        | |
|   |   [ A  the input order ]   correct                               | |
|   |        Merge takes from the left run on a tie.                   | |
|   |   ( B  reversed )                                                | |
|   |        Believes merge takes from the right run on a tie.         | |
|   | Explanation  ...                                                 | |
|   | How it works  ...   Example  ...   Pitfalls  ...                 | |
|   +------------------------------------------------------------------+ |
|   Concept  merge-is-stable . level 2                                   |
|            Merge sort keeps equal keys in their input order.  source   |
|   Taught by  Merge sort, step by step                                  |
| > merge-count-calls   2 output short   How many calls does ...  7 lines|
|                                                                        |
| Searching . Binary search                                    4         |
| > ...                                                                  |
+------------------------------------------------------------------------+
```

- The author navigation sits left of the page, as `../navigation.md`
  draws it, and is left out here.
- The author bar names the three figure pages, then the four browser pages.
- The module chips pick one module, and the other filters' chips count what
  pressing each would leave.
- A closed row reads on one line. An opened row draws the queue's answered
  question in its panel, with every choice's reason and every detail open,
  then the concept and the lessons below the panel.
