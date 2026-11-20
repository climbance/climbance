# The sitting

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

A served problem's page is the sitting's page. Opening `/problems/:problem_id`
serves the statement on the page drawn below, and the first clock press or
submission starts the sitting. A retired
problem's path reads as its record, as `README.md` gives.

```
+- /problems/p-91c2, solving --------------------------------------------+
| Climbance    [ Practice ]  Problems  Cards  Knowledge           ☀  ≡   |
+------------------------------------------------------------------------+
| Smallest feasible speed              12:04  [ Pause ]  [ End ]         |
+----------------------------------+-------------------------------------+
| medium . binary-search . 2 tried |                                     |
| . Cards: Binary search           | +----------------------------+      |
| the statement, as prose          | |                            |      |
|                                  | | def solve(piles, h) -> int:|      |
|                                  | |     |                      |      |
| ...........................      | |                            |      |
| ...........................      | |   the editor               |      |
| ...........................      | |                            |      |
| ( Report this problem )          | +----------------------------+      |
|                                  | [ Submit ]  Cmd+Enter . judged      |
|                                  |             against the problem's   |
|                                  |             own test cases          |
|                                  | +----------------------------+      |
|                                  | | Not solved: 7 of 11 cases  |      |
|                                  | | + + + + + + + x + ~ ~      |      |
|                                  | | Case 8: wrong answer       |      |
|                                  | |   Arguments  [1,4,1,1] 8   |      |
|                                  | |   Expected   3             |      |
|                                  | |   Returned   4             |      |
|                                  | +----------------------------+      |
+------------------------------------------------------------------------+
```

- A bar across the top carries the clock, its press and the end, and it stays
  at the top of the window while the statement scrolls. The clock is never
  scrolled out of sight.
- The clock reads `0:00` beside `[ Start ]` until the user starts it, or until
  the clock preference starts it on opening. Once running, the press reads
  `[ Pause ]`, and once paused, `[ Resume ]`.
- A clock the preference started carries a line under the bar saying so, and
  that pausing it turns the preference off. The line goes at the user's first
  press. The preference was set by a press the user may not remember.
- A sitting a submission minted with no clock reads `untimed` in the clock's
  place, since `0:00` reads as a time the sitting took.
- One line above the statement carries what the picked problem's page used to:
  the difficulty, the techniques, the attempts on this problem and the cards.
- The bar carries the problem's title, the page's only one, at the heading
  size. The statement column repeats none, since the bar keeps the title in view
  while the statement scrolls.
- The statement reads on the left and the editor takes the right, which is the
  one page in two columns.
- A quiet `Report this problem` press sits under the statement. It opens the
  dialog asking the author to retire the problem, and
  `README.md` gives the request.
- The editor opens on the signature every case calls, and the statement column
  does not repeat it. A second copy beside the editor's first line says the
  same thing twice.
- The verdict sits under the editor, so a failing case is read beside the code
  that failed it.
- The case strip carries one mark per case, in the order the problem carries its
  cases: `+` passed, `x` wrong, `~` timed out, `!` crashed.
- The failing case is drawn whole: the arguments, the expected value, and the
  value the submission returned.
- The submit press sits under the editor, beside the shortcut that fires it and
  the line saying what judges the submission.
- A quiet `Restore my last solve` press sits beside the submit press where the
  user has solved the problem before and the editor did not carry that code.
