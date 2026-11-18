# Problems

The API reads a landed problem from the corpus and serves it: its statement,
its templates and its test cases. Generation writes the problem record, and
`../cli/generation/problem.md` gives it. This file gives what serving a problem
and retiring one hold to.

- **A created problem is served.** `created` means written and verified, and
  no later gate stands between that and serving. Retirement is the only status
  move.
- **A problem is never edited, and only its status moves.** A statement that
  says the wrong thing is retired `defective` and a new problem is written.
  The retired problem's attempts stay with the record they were made against,
  and no case moves under them. A generated statement passes every gate or is
  retired, so a write path for wording would buy nothing and could change what
  a verdict means.
- **A problem is retired by hand, in the terminal.** A problem is served to
  every user, so one user's reading of a statement may not remove the problem
  from another user's practice. A user asks for a retirement with a
  retirement request, which the author reads first. `../log.md` gives the
  record.
- **Retirement names its reason.** `defective` is a statement that asked for
  something its cases do not decide. `copied` is a problem the screen site
  named a published source for, and its attempts stay in mastery: the solver
  solved what the problem asked.
- **A defective problem's attempts are excluded from mastery, both
  directions, at read time.** The failure was the problem's fault, and
  excluding only the failures would raise a solve rate because a problem was
  broken. The attempts stay readable, and the board stops counting them.
