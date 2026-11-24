# The lessons page

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /author/lessons?module=py --------------------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Lessons                                                                |
|                                                                        |
| Module   algo  python  [ py ]                                          |
| Topic    core 9  data 6                                  ( Clear )     |
|                                                                        |
| Python                                                           15    |
| +--------------------------------------------------------------------+ |
| | Slug               Title              Teaches        Min  Pre  Qs  | |
| |--------------------------------------------------------------------| |
| | functions-calls    Calling a function Functions 0, 1   6    2  24  | |
| |▌functions-defaults Default arguments  Functions 1      4    1  11  | |
| | …                                                                  | |
| +--------------------------------------------------------------------+ |
+------------------------------------------------------------------------+
```

A row pressed opens the lesson in the dialog:

```
+- /author/lessons?module=py#functions-defaults -------------------------+
|      +-------------------------------------------------------------+   |
|      | ‹ › 2 of 15  Default arguments                            ✕ |   |
|      | functions-defaults . teaches Functions 1 . 4 min            |   |
|      | needs functions-calls . needed by functions-closures        |   |
|      |-------------------------------------------------------------|   |
|      | A default is evaluated once, when `def` runs ...            |   |
|      | ...                                                         |   |
|      |                                                             |   |
|      | Questions  defaults-shared-list  defaults-none-sentinel ... |   |
|      +-------------------------------------------------------------+   |
+------------------------------------------------------------------------+
```

- The author navigation sits left of the page, as `../navigation.md`
  draws it, and is left out here.
- `▌` marks the row last opened.
- The dialog's head names the lessons the opened one needs and those needing
  it. The body draws the lesson whole, then lists its groups' questions as
  links.
