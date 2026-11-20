# Every problem

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /problems?technique=binary-search&difficulty=medium ------------------+
| Climbance    Practice  [ Problems ]  Cards  Knowledge           ☀  ≡   |
+------------------------------------------------------------------------+
| Problems                                                               |
| Every problem the engine has written. A difficulty and a tag narrow    |
| the list, and a problem shows where it matches both.                   |
|                                                                        |
| ( easy 1 )( [medium 1] )( hard 0 )                                     |
|                                                                        |
| ( dynamic-programming 3 )( depth-first-search 2 )( backtracking 1 )    |
| ( [binary-search 1] )( sorting 1 )( greedy 1 ) ...                     |
|                                                                        |
| Matching your filters  1                        Clear all 2 filters    |
| Combined Frequency Rank   (medium)            never attempted          |
| binary-search . sorting                                                |
|                                                                        |
| [ Previous ]  Page 1 of 3  [ Next ]        with no tag picked          |
+------------------------------------------------------------------------+
```

- The navigation names the listing, and marks Problems on it alone. A picked
  problem is a step down from the board, from a technique or from a card.
- A tag is a technique the listing holds, with how many problems carry it. A
  picked tag is marked. The difficulties are the three a problem can carry,
  in the order a solver reads them.
- The tags keep the order the whole listing gives, and each count holds a fixed
  width, so picking a filter moves no row of the page.
- A problem is shown where it carries any tag the user picked and sits at any
  difficulty they asked for. Two techniques ask for the problems of either,
  where a technique and a difficulty ask for the problems of both.
- Each chip counts what pressing it would leave: the difficulties count what
  the tags left, and the tags count what the difficulties left.
- The tags picked are in the URL, so a filtered listing is a link the user can
  keep.
- A row names the problem's techniques under its title, since the counts take
  the right of the row. It carries no statement, as a candidate carries none.
- The listing is read in pages of twenty rows, and the page is in the URL
  beside the tags. Picking a tag returns the listing to its first page.
- The problem's page is the one a technique's candidates open, and the way back
  then names the listing.
