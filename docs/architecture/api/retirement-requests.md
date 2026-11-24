# Retirement requests

A user's request that a problem be retired. A `RetirementRequest` holds the
problem, a reason and the user's note.

- **A user asks for a retirement, and the author retires the problem by hand.**
  A problem is served to every user, so one user's reading of a statement does
  not remove the problem from another user's practice. `problems.md` gives
  who retires a problem.
- **The request names one of the two retirement reasons, `defective` or
  `copied`.** The author retires a problem under a reason, so a request naming
  the same reasons reads as the retirement it asks for.
- **The note is required, and at most 2000 characters.** The author judges the
  problem from the note, and a blank note gives nothing to judge.
- **A retired problem takes no request.** The problem is no longer served, so
  the request would ask for nothing.
- **The problem stays served while the request waits.** A request is evidence
  for the author, and a wrong request costs only the author's reading.
- **The author reads the requests on the inbox**, each beside
  whether its problem is still served, as
  `../web-app/pages/author/inbox/README.md` gives. `climb problem --retire`
  prints the problem's requests before asking to confirm.
- **A request is private to the user**, exported and erased with the rest of
  the log. The author reads it as the operator, as the author reads the rest
  of the store.
- **A user may send several requests on one problem.** Each one is append-only,
  and the page says a request was sent until the page is left.

Deferred, since only use answers each:

- A reply to the user once the author has read the request.
- A bound on how many requests one user sends.
