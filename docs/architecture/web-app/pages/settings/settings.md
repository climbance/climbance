# The settings

A wireframe of the page `README.md` specifies, drawn at low fidelity.
`../../README.md` gives how a wireframe is read.

```
+- /settings ------------------------------------------------------------+
| Climbance    Practice  Problems  Cards  Knowledge               ☀  ≡   |
+------------------------------------------------------------------------+
| Settings                                                               |
| The study settings hold on every device you sign in on.                |
|                                                                        |
| Account                                                                |
| you@example.invalid              ( Signed-in devices ) ( Sign out )    |
| u-4f9c2a                                                               |
|                                                                        |
| Study                                                                  |
| New questions per day                           [ 10 ]  0 to 200       |
| Exam size                                       [ 40 ]  1 to 500       |
|                                                                        |
| [ Save ]  Saved.                                                       |
|                                                                        |
| Sync                                                                   |
| Synced 2 minutes ago                                  ( Sync now )     |
|                                                                        |
| Archived modules  1                                                    |
| System design                                         ( Restore )      |
|                                                                        |
| Feedback                                                               |
| ( Send feedback )                                                      |
|                                                                        |
| Your record                                                            |
| Every record of your practice, as one JSON file.                       |
| ( Export the record )                         ( Delete the account )   |
+------------------------------------------------------------------------+
```

- The account menu links the page. It carries no way back, since the
  navigation reaches every section from it.
- The page reads as the phone's Settings screen does: Account, Study, the
  sync, the archived modules, Feedback, then the record. The phone adds the
  device name and the reminder hour, which are about one phone.
- The record's export and the account's deletion come last, since the
  deletion is the one act on the page that cannot be undone.
- The daily limit and the exam size are settings of the log, so a value
  saved here stands on the phone. Each field names its range, and Save waits
  until both fields hold a value in range and one of them changed.
