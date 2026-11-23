# The generation page

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /author/generation ---------------------------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Generation                          Product  [ Generation ]  Workflow  |
|                                                                        |
| Last 30 days                                                           |
| 42 writings . 17 landed . 40%       $0.31 a landed problem             |
|                                     3 site outcomes carry no cost      |
|                                                                        |
| Stopped by                                                writings     |
| screen . copied                                                 9      |
| blind . disagreed                                               8      |
| discrimination . unexercised                                    5      |
| held at paced                                                   3      |
|                                                                        |
| Drafts now                                   drafts     oldest         |
| checked                                         2       3 days         |
| paced                                           3       9 days         |
| rejected                                       22                      |
|                                                                        |
| Corpus                        easy   medium   hard   retired           |
| two-pointers / opposite ends     4        3      1         0           |
| two-pointers / same direction    2        1      0         1           |
| sliding-window / fixed size      0        0      0         -   gap     |
| ...                                                                    |
+------------------------------------------------------------------------+
```

- The bar under the title moves between the three author pages, since each
  is reached from `/author` and the author reads them in turn.
- The figures at the top read the period: the writings, the landed ones, the
  rate, then the spend per landed problem and the outcomes carrying no cost.
- `Stopped by` lists the period's writings that did not land, a row per site
  and gate, the most first. A held writing reads `held at` its state.
- `Drafts now` reads every draft as it stands, a row per writing state.
- `Corpus` reads a row per template, grouped by card in slug order. `gap`
  marks a core template no solution displays.
