# Submission

Takes a user's code for a problem, refuses it past the run caps, and mints the
attempt carrying the result. `../flows.md` gives the steps of the drill loop
around it.

## The run caps

- **A user's submissions are capped at 10 a minute and 60 an hour, and a user's
  recalls are capped by the same bounds.** Each runs untrusted code on the
  server, and the broker admits one run at a time, so one user's burst is every
  other user's wait. Each cap is counted over the user's own records of its
  window, and a run past it is refused before any container starts.
- **A user's submissions and recalls are counted apart, each against the
  bounds.** A recall runs a template's few cases where a submission runs a
  problem's whole set, and one counter over both would refuse the cheaper run
  for the more expensive one's burst.
- **The hour's cap is needed beside the minute's.** A run of ten cases that all
  time out holds the broker about 20 seconds, so 10 runs a minute already keep
  the broker busy, and the minute's cap alone admits 600 an hour.
- **A run the sandbox answers no result for is stored as a run fault, and the
  caps count it.** A solution can end its own container, and the run held the
  broker as long as a judged one. `run-faults.md` gives the record.
- **A cap on the sandbox time a user takes in an hour is deferred until real
  use shows one user filling the broker's queue under the counted caps.** It
  would sum the case times each run already stores, a timed-out case counted at
  the cap, so it limits the resource the users share rather than a count.
- **A run's code is refused past 65,536 characters, before any container
  starts.** A solution is a few kilobytes, and the code reaches the broker and
  the container whole.
