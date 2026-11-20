# The cards

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /cards ---------------------------------------------------------------+
| Climbance    Practice  Problems  [ Cards ]  Knowledge           ☀  ≡   |
+------------------------------------------------------------------------+
| Cards                                                                  |
| One card teaches one technique: when to reach for it, and the forms to |
| reproduce from memory. A card opens once its required cards are met.   |
|                                                                        |
| Depth 0, roots                                          3 cards        |
|      +----------------------------------------------------+            |
| o----| Hashing            hashing            met          |            |
| |    | started 11-02 . ladder 6/6, required 3/3           |            |
| |    | recall  ✓ ✓ ·                                      |            |
| |    +----------------------------------------------------+            |
| |o---| Two pointers       two-pointers       2 days ago   |            |
| ||   | started 11-10 . ladder 3/6, required 2/3           |            |
| ||   | recall  ✓ ✗ · ·                                    |            |
| ||   +----------------------------------------------------+            |
| ||o--| Stack and queue    stack              met          |            |
| |||  | started 11-04 . ladder 2/6, required 1/3           |            |
| |||  | recall  ✓ ✓ ✓                                      |            |
| |||                                                                    |
| Depth 1                                                 2 cards        |
| |||  +----------------------------------------------------+            |
| **|o-| Sliding window     sliding-window     locked       |            |
|   || | waits on Two pointers                              |            |
|   || +----------------------------------------------------+            |
| o-*+-| Monotonic stack    monotonic-stack    not started  |            |
| |  | | For each element, the next greater ...             |            |
| |  |                                                                   |
| Depth 2                                                 1 card         |
| |  | +----------------------------------------------------+            |
| *--*-| Monotonic deque    sliding-window     locked       |            |
|      | waits on Sliding window, Monotonic stack           |            |
+------------------------------------------------------------------------+
```

- The page reads the card graph by depth, as
  `README.md` gives: the roots first, then each depth
  under its own heading with its count. Within a depth, the cards read in the
  order their slugs sort.
- The gutter at the left draws the edges. An edge leaves a required card's
  row at `o` and enters each card requiring it at `*`. Hovering a row
  brightens its own edges and dims the rest, since a graph of twenty cards
  draws more edges than a reader can follow at once.
- Every card reads one row, wherever it stands. A started card's row reads
  its progress where an unstarted card's reads its trigger, so the cards
  being studied are not listed twice. The board names those cards in
  progress first.
- A row names its card state at the right: `met`, `locked`, `not started`,
  or when a started card was last active. A met card lets the cards requiring
  it start, as `../../../../api/card-states.md` gives.
- A locked row reads `waits on` and the required cards not yet met, in place
  of the trigger. The row still opens the card, since a locked card is read in
  full.
- A row carries the recall state of its templates once one of them was
  recalled. It reads one mark per template in the card's order: `✓` recalled
  clean, `◐` passed with hints, `✗` failed, `·` never recalled, and `-` a
  template no case checks. Before the first recall every mark would read `·`
  and tell nothing, so the row carries no recall line.
- A gap reads on the row as `n forms uncovered`, as the card's own page
  reports it.
- The phone reads the same sections and rows with no gutter. Each row of a
  card that requires others names them on a line of its own: `needs Hashing ✓,
  Two pointers`, a tick on each one met.
- Graduated and lapsed read in the state's place once the scheduler adds them,
  and a due date beside them.
