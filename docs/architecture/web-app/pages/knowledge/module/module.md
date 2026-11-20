# A module

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /knowledge/modules/py ------------------------------------------------+
| Climbance    Practice  Problems  Cards  [ Knowledge ]           ☀  ≡   |
+------------------------------------------------------------------------+
| < Knowledge                                                            |
| Python                                                                 |
| 4 topics . 12 due . active     ( Start ) ( Focus here ) ( Pause )      |
|                                                                        |
| Foundation 18/20   Associate 9/24   Professional 0/30   Expert 0/12    |
|                                                                        |
| Core  3 subtopics                             ( Start ) ( Focus )      |
| +--------------------------------------------------------+             |
| |                  L0        L1        L2        L3      |             |
| | Names            covered   open      locked    locked  |             |
| | Types            covered   covered   open      locked  |             |
| | Mutability       open      locked    locked    -       |             |
| +--------------------------------------------------------+             |
|                                                                        |
| Functions  2 subtopics                        ( Start ) ( Focus )      |
| +--------------------------------------------------------+             |
| | ...                                                    |             |
| +--------------------------------------------------------+             |
+------------------------------------------------------------------------+
```

- The line under the title counts the topics and the reviews due, and names
  the module's status. The status press reads Pause on an active module, and
  Resume and Archive on a paused one.
- The counts per level are the phone's Stats line: the passed questions of
  each level over the questions the level holds.
- Each topic is a section with its heading and a panel of its subtopics. A
  cell is one group, and `-` is a group holding no questions.
- A press on a cell opens the start sheet on that group: the subtopic at
  the cell's level. A locked cell opens it too, since locks do not apply to
  the filtered queue. Start beside the module or a topic opens the sheet on
  that scope at every level.
- A subtopic's name opens the start sheet on the subtopic at every level. A
  Focus press on the subtopic's row aims the focus at it, and the Focus press
  beside a topic's heading aims at the topic.
