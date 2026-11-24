# The cards page

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /author/cards?module=algo --------------------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Cards                                                                  |
|                                                                        |
| Module   [ algo 18 ]                                                   |
| Depth    0 6  1 7  2 5                                   ( Clear )     |
|                                                                        |
| Cards                                                            18    |
| +--------------------------------------------------------------------+ |
| | Slug           Title          Technique    Depth Templates Rungs Gaps|
| |--------------------------------------------------------------------| |
| | binary-search  Binary search  binary-sea…  0     3 + 1     8/8      | |
| |▌two-pointers   Two pointers   two-pointers 0     2         5/6   1  | |
| | …                                                                  | |
| +--------------------------------------------------------------------+ |
+------------------------------------------------------------------------+
```

A row pressed opens the card in the dialog:

```
+- /author/cards?module=algo#two-pointers -------------------------------+
|      +-------------------------------------------------------------+   |
|      | ‹ › 2 of 18  Two pointers                                 ✕ |   |
|      | two-pointers . algo . depth 0 . 1 gap: opposite-ends        |   |
|      |-------------------------------------------------------------|   |
|      | Subtopics  Arrays . Two pointers                            |   |
|      | Trigger  A sorted array and a pair to find ...              |   |
|      | Brief    ...                                                |   |
|      | Template  same-direction   core                             |   |
|      |   def solve(...): ...                                       |   |
|      |   6 cases . 4 judgement items . 3 key-line items            |   |
|      | Template  opposite-ends    core                             |   |
|      |   def solve(...): ...                                       |   |
|      |   5 cases . no judgement item . no key-line item            |   |
|      | Required by  sliding-window, its fixed-width uses same-dir… |   |
|      | Ladder  3f9a2c71  Pair sums under a cap  same-direction req |   |
|      |         b04e18d2  Closest pair           same-direction req |   |
|      +-------------------------------------------------------------+   |
+------------------------------------------------------------------------+
```

- The author navigation sits left of the page, as `../navigation.md`
  draws it, and is left out here.
- `▌` marks the row last opened. The templates column reads core plus
  optional, and the rungs column the rungs against the selector's `size`.
- The dialog reads the card's text, each template with its code and counts,
  the requirements, then the ladder.
