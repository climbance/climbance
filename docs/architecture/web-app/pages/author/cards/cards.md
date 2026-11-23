# The cards page

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /author/cards?module=algo --------------------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Cards              Product  Generation  Workflow                       |
|                    Questions  Lessons  [ Cards ]  Problems             |
|                                                                        |
| Module   [ algo 18 ]                                                   |
| Depth    0 6  1 7  2 5                                   ( Clear )     |
|                                                                        |
| > binary-search   Binary search   binary-search . algo . depth 0        |
|                   3 core + 1 optional . 8 of 8 rungs . no gap          |
| v two-pointers    Two pointers    two-pointers . algo . depth 0         |
|                   2 core . 5 of 6 rungs . 1 gap: opposite-ends         |
|   Trigger  A sorted array and a pair to find ...                       |
|   Brief    ...                                                         |
|   Template  same-direction   core                                      |
|     def solve(...): ...                                                |
|     6 cases . 4 judgement items . 3 key-line items                     |
|   Template  opposite-ends    core                                      |
|     def solve(...): ...                                                |
|     5 cases . no judgement item . no key-line item                     |
|   Required by  sliding-window, its fixed-width uses same-direction     |
|   Ladder   3f9a2c71  Pair sums under a cap   same-direction  easy  req |
|            b04e18d2  Closest pair            same-direction  1240  req |
+------------------------------------------------------------------------+
```

- A closed row reads on two lines: the card, then its templates, rungs and
  gaps.
- An opened row reads the card's text, each template with its code and counts,
  the requirements, then the ladder.
