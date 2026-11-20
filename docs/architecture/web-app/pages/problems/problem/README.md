# A picked problem

The page at `/problems/:problem_id` and the phone's Problem screen: a
problem's record and statement, the sitting on it, the claim and the label
asked after a solve, and the request to retire it. The page sits under
Practice, as `../../shell/README.md` gives.

## The page and its path

- **The problem's page holds the statement and the sitting.** The path serves
  the statement and stays, since serving mints nothing, as
  `../../../../api/sitting.md` gives. A retired problem's path reads as its
  record and serves nothing.
- **The problem's page reads the difficulty, the techniques, the counts the
  user reached on the problem, and the cards** in one line above the
  statement, and the statement is the page's body.
- **A query parameter names where the user came from.** The picked problem is
  `/problems/:problem_id` whichever page offered it, since a card's ladder
  opens the same problem as a rung. `?technique=` names the technique the pick
  came from, `?card=` names the card, and `?from=problems` names the
  listing, which holds no record of its own to name. A listing filtered to one
  tag adds that tag as `?technique=`, since picking one tag is drilling for
  that technique as a pick from the board is. The problem's page keeps the
  technique and the card: the way back returns where the pick came from, and
  the claim answers for the card's own technique where a card offered the
  problem.
- **A sitting has no path of its own, and `?sitting=` names it on the
  problem's path.** Before the first clock press or submission no sitting
  exists, so the page's address cannot name one from its first load. The
  page adds the parameter once the sitting is minted, replacing the address
  rather than adding a history entry.
- **A reload reads the sitting `?sitting=` names, running or ended.** The End
  press or the idle bound ends a sitting, and the claim asked after the end
  would otherwise be lost to a reload. Without the parameter, a reload finds the
  sitting the problem has running, where one runs.
- **The phone's Problem screen reopens the sitting the problem has running.**
  The phone has no address to carry `?sitting=`, so opening the screen, or
  the app again after it was closed, reads the running sitting with the
  statement. Its own unsent code and its clock come back with it. An ended
  sitting is not reopened, so a claim the sheet left unanswered is not asked
  again, where a reload of the web's page asks it again. The attempts it
  leaves count under the problem's own techniques, as a skipped claim's do.

## The sitting

- **The sitting names its way back as a press, running or ended.** Leaving a
  sitting's page costs nothing: the clock is the user's to run, and the
  unsent code is kept. The press returns to the page the problem came from:
  the card, the technique, the listing or the board, and names that page. A
  solved or ended sitting stays on the page after the claim, and its press is
  the page's next act.
- **A solved or ended sitting opened from a card offers the card's next rung
  beside the way back.** The card is read again once the sitting is solved, so
  the solve just made counts. The rung offered is never the problem just sat.
  Without the press, a user working down a ladder returned to the card between
  every two rungs. The phone shows the press under the bar, since a rung's title
  does not fit beside the clock.
- **An ended sitting's code is read-only.** The code reads back as it was
  submitted, and the next sitting on the problem opens on the signature, as
  `../../../../flows.md` gives. A submission typed over the solve would be a
  solve read rather than recalled.
  A solved sitting still running stays editable. A later solve in it moves
  nothing, since the verdict is read through the first solve.
- **A reopened sitting reads back its last submission: the code and the
  verdict.** Reading the sitting returns them from the stored attempt and its
  verification. Kept in page state alone, both were lost to a reload, and an
  untimed sitting's draft names no sitting, so the editor opened on the
  signature. A draft of the sitting's own still comes first, since it holds
  what was typed after the submission.
- **The phone's sitting holds the statement and the editor as two tabs**,
  under one bar holding the clock, its press and End. The editor stays
  mounted under the statement, so a switch keeps what was typed. The first
  clock press or submission mints the sitting, named by the phone's device
  name, and an ended sitting's press returns to the page the problem came
  from. The phone keeps a problem's unsent code and the clock preference in
  its own copy, as the browser keeps them, and signing out deletes the code
  with the rest of the copy. The app going to the background pauses a
  running clock, and returning resumes only that pause, as a hidden page
  does on the web.
  At a solve and once the sitting ends, a sheet from the bottom asks the
  claim and the label of each attempt not yet asked, in turn, as the web's
  dialog does. A press under the editor restores the last solve, which the
  attempts then report. The
  sitting is `by platform` for its reopening alone, which the bullet on the
  Problem screen gives.

## The claim and the label

- **The claim is asked at each solve and at the end of the sitting**, of each
  attempt not yet asked. A solve leaves the sitting running, as
  `../../../../api/sitting.md` gives, and asking only at the end would ask
  about the solving attempt after the next form was typed over it.

## Retirement

- **A request to retire the problem is a quiet press under the statement**,
  on both clients. A reader judges a statement while reading it, so the press
  sits under the text being judged. Once sent, the press is replaced by a line
  saying the author reads the request, until the page is left. The problem
  stays served, and a later visit offers the press again, since a user may
  send several requests on one problem.
- **A retired page says so and serves nothing.** The serving call refuses a
  retired problem, so no statement is shown and no clock starts. The page
  reads as the record of what the user did on that problem.
