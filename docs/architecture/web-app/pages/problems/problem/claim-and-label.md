# The claim and the label

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- the claim and the label, over the sitting ----------------------------+
| The claim                                                              |
| Your answer decides which techniques this attempt counts toward on     |
| your board. Each attempt of the sitting is asked in turn.              |
|                                                                        |
| Attempt 2 of 3 . not solved . 12:04                                    |
|                                                                        |
| Which techniques did this code use?                                    |
|   [x] binary-search        the drilled one, answered for               |
|   [ ] two-pointers                                                     |
|   [ ] None of these                                                    |
|                                                                        |
| How sure are you?   ( guess | leaning | sure )                         |
| A guess is a fine answer. The level is kept with the claim, so a       |
| guess is never read as sure.                                           |
|                                                                        |
| Why did it go that way?                                                |
|   ( ) gap      I did not hold the form                                 |
|   ( ) rust     I held the form and did not reach it                    |
|   ( ) syntax   I slipped writing code I know                           |
|                                                                        |
|                                         [ Save ]                       |
+------------------------------------------------------------------------+
```

- The claim and the label open together over the sitting, at a solve and at
  its end, and the two are asked in turn of each attempt not yet asked.
- The technique the problem was picked by is answered for already, since
  selection chose the problem for that technique.
- The label reads as a question about the solver rather than about the code,
  so it sits under the claim and the confidence.
- Each mode is drawn as its own word beside a gloss in the first person. A
  solver reading `rust` alone cannot tell which of the two failures it names.
- The modes are the ones the route sent, so the split by verdict lives in one
  place. An unsolved attempt is offered `gap`, `rust` and `syntax`, and a solved
  one is offered `speed` and `none`.
- An attempt that crashed on every case is offered no mode, and the overlay
  then asks for its claim alone. `../../../../api/self-labels.md` gives why
  the record answers that attempt already.
- One press stores both records. The claim and the label answer two questions
  about one attempt, and a press each would ask the solver to confirm twice.
- A press with no mode selected stores no label, and
  `../../../../api/self-labels.md` gives why a skip writes no record.
  Closing leaves the attempts to the problem's own techniques, and leaves them
  unlabelled.
