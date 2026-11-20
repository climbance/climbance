# A queue, asking

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /knowledge/queue?mode=next -------------------------------------------+
| Climbance    Practice  Problems  Cards  [ Knowledge ]           ☀  ≡   |
+------------------------------------------------------------------------+
| Next                                          3 answered ( Stop )      |
| Python . Core . Names, Associate                         new           |
|                                                                        |
| What does `x is y` compare?                                            |
|                                                                        |
|   1  ( the values )                                                    |
|   2  ( the identities )                                                |
|   3  ( the types )                                                     |
|   4  ( the hashes )                                                    |
|                                                                        |
| Type ? after a reply to mark it a guess.        [ Submit ]             |
+------------------------------------------------------------------------+
```

- The queue carries no way back, since a press on Stop leaves the queue. The
  navigation still reads, and leaving through it stops the queue too.
- The bar names the queue's mode, the answers given and Stop. The line under
  it names the question's group and its state: new, due, weak or early.
- A digit picks an option, and Enter submits. A `short` question reads a text
  field in place of the options.
- The exam reads the same page with its question count in the bar, and no
  verdict until its end.
