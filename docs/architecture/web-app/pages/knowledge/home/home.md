# The knowledge home

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../../README.md` gives how a wireframe is read.

```
+- /knowledge -----------------------------------------------------------+
| Climbance    Practice  Problems  Cards  [ Knowledge ]           ☀  ≡   |
+------------------------------------------------------------------------+
| Knowledge                                                              |
| Answer the questions due, then the new ones.                           |
| Lessons . Certifications                                               |
|                                                                        |
| +--------------------------------------------------------+             |
| | Ready to read: Names and binding . ~6 min              |             |
| | Ready for exam: Python core, Associate                 |             |
| +--------------------------------------------------------+             |
| | Focus: Python . Core                                   |             |
| | [ Strict ]  [ 5 more new today ]  [ Clear ]            |             |
| | Reached: at 10 a day, by Thu 3 Dec . at your pace of   |             |
| | 4 a day, by Sat 9 Jan                                  |             |
| +--------------------------------------------------------+             |
|                                                                        |
|             [ Continue ]                                               |
|    12 reviews . 7 new left today . 2 waiting outside                   |
|                                                                        |
|   ( Exam )                                                             |
|                                                                        |
| Modules  2                                                             |
| +--------------------------------------------------------+             |
| | Python                                 12 due    ^ v   |             |
| | next up: Core . Names, Associate   4/9                 |             |
| +--------------------------------------------------------+             |
| | System design                          paused    ^ v   |             |
| | next up: Caching . Basics, Foundation  0/6             |             |
| +--------------------------------------------------------+             |
|                                                                        |
| Reviews ahead                                                          |
| +--------------------------------------------------------+             |
| | 31 over 14 days . 6 today                              |             |
| |  6                9                                    |             |
| |  #                #                                    |             |
| |  #  #     #    #  #     #           #                  |             |
| |  #  #  #  #    #  #  #  #     #     #     #            |             |
| | Today                                       Wed 25 Nov |             |
| | If every review passes. Questions not yet seen add     |             |
| | more.                                                  |             |
| +--------------------------------------------------------+             |
+------------------------------------------------------------------------+
```

- The home is the section's root, so it carries no way back.
- The line under the note links the lessons page and the certifications
  page. Each is a destination, so each reads as a link.
- Continue is the page's act, an ink pill. Exam is an outlined press below
  it, at a lower weight. A filtered queue starts from a module's page.
- The line under Continue counts the reviews due and the new questions left
  today. "waiting outside" reads only under a strict focus, and a press on it
  serves those reviews.
- The ready lesson and the ready certification read only where one exists.
  With neither and no focus, the panel above Continue is absent.
- `^` and `v` move a module row up or down. The first row's `^` and the last
  row's `v` are disabled.
- The focus panel reads "No focus" with a press to set one on a module's page
  where none is set. "5 more new today" raises today's limit.
- The daily limit is set on the settings page the account menu links.
- A module row opens the module's page. An archived module has no row.
- A column of the forecast names its day and its count on hover. Only today
  and the busiest day print their count.
