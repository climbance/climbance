# The workflow page

The page at `/author/workflow`, in the author area: what waits for the
author's hand, what failed under learners, and what each part's model calls
cost. `../README.md` gives who reaches it.

[`workflow.md`](workflow.md) draws the page at low fidelity.

- **The by-hand passes read as what each would ask about now.** The page
  shows a count per pass and names the command that clears it, since every
  command that writes stays a command.
  - `claim --by-hand`: the signed-in author's attempts that carry no user
    claim. The pass reads the author's own log, so the page reads it too.
  - `match --by-hand`: the canonicals that carry no user template match.
  - `difficulty judge`: the served problems that carry no rating under the
    standing correction, which are the problems the command would rate. With
    no standing correction the command cannot run, and the row says so.
  - `judge build`: the templates whose judgement items are not served at the
    template's current code, which are the templates the build would rebuild.
  - `fill build`: the same count for the key-line items.
- **The retirement requests read newest first, waiting ones on top.** A
  request waits while its problem is still served. A row names the problem,
  the retirement reason and the note, and no user, since the author acts on
  the problem.
- **The feedback reads newest first**, each note with the client and the page
  it was sent from, as `climb feedback` prints it today. A note is addressed
  to the author, so the page shows it whole.
- **The run faults read as a count per day and run kind for the last 30
  days**, then the latest faults with their detail. A fault is private to its
  user, so a row names no user. The detail is the runner's own message,
  written for the author.
- **The spend reads by the part whose record cites the call**, for the last
  30 days. A call record names no domain, as `../../../../cli/calls.md` gives,
  so the part is read from the record citing its `call_id`: generation by
  site, difficulty, the classifier, the matcher and the diagnoser. A call no
  record cites, such as a failure, reads as `uncited`. The cost is the
  call's own `cost`, and the page names how many calls carry none.
