# The board

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- / --------------------------------------------------------------------+
| Climbance    [ Practice ]  Problems  Cards  Knowledge           ☀  ≡   |
+------------------------------------------------------------------------+
| Practice                                                               |
| Start or continue a card or a module, or pick a technique.             |
|                                                                        |
| Focus: Python . core                 [ Continue ]  12 due, 5 new       |
|                                                                        |
| Modules  2                                                             |
| +--------------------------------------------------------+             |
| | Python               level 1 . 40% retained            |             |
| | System design        level 0 . 12% retained            |             |
| +--------------------------------------------------------+             |
|                                                                        |
| Next                                                                   |
| +--------------------------------------------------------+             |
| | Recall: Lower bound           Binary search  [ Recall ]|             |
| +--------------------------------------------------------+             |
|                                                                        |
| Cards in progress  1                                                   |
| +--------------------------------------------------------+             |
| | Sliding window    sliding-window        2 days ago     |             |
| | started 09-28 . ladder 5/8, required 4/5               |             |
| | recall  ✓ ✓ ✗ · · -                                    |             |
| +--------------------------------------------------------+             |
|                                                                        |
| +--------------------------------------------------------+             |
| | Judge a solution                                       |             |
| | Read the solution. Is it correct, or is one line wrong?|             |
| | Fill the key line                                      |             |
| | One line of the form is blank. Pick the line that ...  |             |
| +--------------------------------------------------------+             |
|                                                                        |
| +--------------------------------------------------------+             |
| | Cold problem                           [ Start cold ]  |             |
| | An unseen problem with nothing named, 60 minutes, no   |             |
| | pause. It measures your rating.                        |             |
| +--------------------------------------------------------+             |
|                                                                        |
| Cards to start  3                                                      |
| +--------------------------------------------------------+             |
| | Two pointers      two-pointers          root           |             |
| +--------------------------------------------------------+             |
|                                                                        |
| Techniques not practised yet  12                                       |
| bit-manipulation   breadth-first-search   greedy                       |
| monotonic-stack   sliding-window   two-pointers ...                    |
|                                                                        |
| Techniques practised  2                                                |
| binary-search   12 attempts  9/12 solved  3 days ago  4/12 known       |
| monotonic-stack  4 attempts   2/4 solved  17 days ago                  |
|                                                                        |
| 3 attempts grouped nowhere . 2 on a defective problem                  |
+------------------------------------------------------------------------+
```

- The board is the landing page, so it opens under the navigation with no way
  back.
- The knowledge study reads first, from the device's copy: the focus with
  Continue, then the modules. The scheduler's pick follows under Next.
- "Cards in progress" reads next: the cards with a run open, the most recently
  active first, each the same row the cards list draws for it. A press opens
  the card, where the next rung is.
- A technique never practised ranks stalest, so the untouched techniques read
  first. Each is a name alone, since every count on such a row is zero.
- A name here is a link, not a chip. The listing's filters are chips, and a
  press there toggles rather than opens.
- A practised technique is a row: the attempts, the share solved, when it was
  last practised, and the questions passed of every subtopic naming it. A
  technique no subtopic names reads no knowledge, as `monotonic-stack` here.
- A technique practised only through its questions or judgements reads those
  counts alone. A row reading `never attempted` would contradict the section's
  heading, Techniques practised.
- The line under the two groups counts the attempts no row holds: the attempts
  no technique resolved, and the attempts on a retired problem.
- The scheduler's pick is served above the cards and the techniques, and every
  technique stays on offer below it. The pick then reads the open runs, so it
  can name a card's next rung beside the cards in progress.
- The two short exercises, judging and filling, follow the cards in progress.
  The cold sitting's panel follows them, and its press serves a cold sitting
  or returns to the one running.
  The unlocked cards not yet started follow them, five at most, without the
  card the pick names.
