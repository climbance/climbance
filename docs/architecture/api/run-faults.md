# Run faults

A user's submission or recall the sandbox answered no result for. A
`RunFault` holds the user, the kind of run, the time and the runner's message.

- **A fault is stored because a solution can cause one.** A solution can kill
  its own entry process, or reach the container's process limit, and either
  ends the container before any case reports. The run held the broker all the
  same.
- **The caps count faults beside attempts.** A run of each kind counts once
  against its own caps, whether it stored an attempt or a fault. Without the
  count, a solution ending its sandbox would run past every cap.
- **A fault answers 503 and stores no attempt.** The sandbox gave no verdict,
  so nothing is judged, and the user reads that the run still counts.
- **A fault is private to the user**, exported and erased with the rest of
  the log. The author reads it as the operator.
