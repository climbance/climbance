# The inbox

The page at `/author`, the author area's home: what waits for the author's
hand, and what learners reported or hit. `../README.md` gives who reaches it,
and the navigation that opens every other author page from it.

[`inbox.md`](inbox.md) draws the page at low fidelity.

## What waits

- **The page opens on what waits, one row per kind of work.** Each row counts
  the items waiting and names where the author clears them. The author reads
  the home page first, so the home page answers whether anything needs the
  author today.
- **The by-hand passes read as what each would ask about now.** A row names the
  command that clears it, since every command that writes stays a command. A
  press copies the command.
  - `claim --by-hand`: the signed-in author's attempts that carry no user
    claim. The pass reads the author's own log, so the page reads it too.
  - `match --by-hand`: the canonicals that carry no user template match.
  - `difficulty judge`: the served problems that carry no rating under the
    standing correction, which are the problems the command would rate. With
    no standing correction the command cannot run, and the row says so.
  - `judge build`: the templates whose judgement items are not served at the
    template's current code, which are the templates the build would rebuild.
  - `fill build`: the same count for the key-line items.
- **The problems needing attention read as one row**, counting the served
  problems that carry an attention flag. The row links to the problems page
  filtered by `?flag=any`, and `../problems/README.md` gives the flags.
- **The waiting retirement requests read as one row each**, newest first. A
  request waits while its problem is still served. A row names the problem by
  the first eight characters of its id and by its title, then the retirement
  reason and the note. The row links to the problem's row on the problems
  page, where the author reads the problem before retiring it. A row names no
  user, since the author acts on the problem.
- **A row counting nothing reads as clear**, and stays on the page. A row
  that vanished could equally mean a figure that failed to load.

## What learners reported

- **The feedback reads newest first**, each note with the client and the page
  it was sent from. A note is addressed to the author, so the page shows the
  note whole, and names no user. A note has no read state, since marking one
  read is a write this page does not make. The section counts the notes of
  the last 7 days.
- **The answered retirement requests read below the waiting ones**, newest
  first, each naming the status its problem holds now.
- **The run faults read as a count per day and run kind for the last 30
  days**, then the latest faults with their detail. A fault is private to its
  user, so a row names no user. The detail is the runner's own message,
  written for the author.

## The count in the navigation

- **The inbox's entry in the navigation reads the number of rows under
  `## What waits` that count something.** Every author page then shows
  whether work waits without opening the inbox. Rows are counted rather than
  items, since a by-hand pass of 14 attempts and one request each ask for one
  sitting at the terminal.
- **`/author/workflow` redirects to `/author`.** The workflow page held the
  by-hand passes, the requests, the feedback and the run faults before the
  inbox took them over. Its spend moved to `../spend/README.md`.
