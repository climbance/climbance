# The three readings before the content

A wireframe of the readings `../../areas.md` specifies, drawn at low fidelity.
`../../README.md` gives how a wireframe is read.

```
+- the three readings before the content --------------------------------+
| +--------------------------------------------------------+             |
| | Loading the board...                                   |             |
| +--------------------------------------------------------+             |
|                                                                        |
| +--------------------------------------------------------+             |
| | The board did not load: 503 from the API   [ Retry ]   |             |
| +--------------------------------------------------------+             |
|                                                                        |
| +--------------------------------------------------------+             |
| | No served problem carries a technique yet.             |             |
| +--------------------------------------------------------+             |
+------------------------------------------------------------------------+
```

- One component renders the three, so a page that is loading, failed or empty
  reads the same wherever the user stands.
- The failure names what failed and offers the request again.
