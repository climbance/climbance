# A card

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /cards/binary-search -------------------------------------------------+
| Climbance    Practice  Problems  [ Cards ]  Knowledge           ☀  ≡   |
+------------------------------------------------------------------------+
| < Cards                                                                |
| Binary search                                                          |
| binary-search                                                          |
|                                                                        |
| ( When to reach for it )( The brief )( Ladder )( Templates )   the bar |
|                                                                        |
| v When to reach for it                                                 |
| the trigger, one or two lines                                          |
|                                                                        |
| v The brief                                                            |
| ...........................................................            |
|                                                                        |
| v Templates                                             5 templates    |
| +--------------------------------------------------------+             |
| | Lower bound  [optional]              [ Reveal the form ] |           |
| | ------------------------------------------------------ |            |
| | trigger: ............................................  |             |
| | +----------------------------------------------------+ |            |
| | | The form is hidden . 14 lines                      | |            |
| | +----------------------------------------------------+ |            |
| +--------------------------------------------------------+             |
| +--------------------------------------------------------+             |
| | Upper bound                            [ Hide the form ] |           |
| | ------------------------------------------------------ |            |
| | trigger: ............................................  |             |
| | def upper(xs, target):   the form, coloured as the      |            |
| |     ...                  editor colours it             |             |
| | the notes, as prose                                    |             |
| +--------------------------------------------------------+             |
+------------------------------------------------------------------------+
```

- A bar names the page's sections and stays at the top while the page scrolls.
  The brief runs past a screen, and the ladder under it would otherwise be
  reached by scrolling through the whole of it.
- Every heading is the press that closes its own section, and a section is open
  until the reader closes it.
- The trigger and the brief read above the templates, and both stay visible.
- A template is a panel: its title, its badges and the press that reveals the
  form in the header, then its trigger.
- A template's form is hidden until the user reveals it. The hidden state names
  how many lines the form runs to, and shows nothing of the form itself. A
  reader decides whether to try recalling the form from that length.
- A revealed template shows its form and its notes, and the press then covers
  the form again.
