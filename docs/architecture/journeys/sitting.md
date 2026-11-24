# A sitting

A user picks a problem, solves it in the editor against its own cases, and
says which techniques the code used and why the attempt went the way it did.
This page follows the `sitting` journey in `../model.toml`. It starts at the
board's pick, a technique's problems, or the problem listing. It ends at a
solved or ended sitting with its claim and its label answered.

`../flows/drill-loop.md` gives the rules of each step, and this page cites it
rather than restating them. Each component below is named by its id in
`../model.toml`, and its file under `../api/` or `../core-package/` gives its
rules.

## 1. Choosing a problem

- **The web offers a problem from three pages, and the phone from the same
  three screens.** The board at `/` is the Practice tab on the phone. A
  technique's page at `/techniques/:technique` is the Technique screen. The
  listing at `/problems` is the Problems tab.
  `../web-app/pages/practice/board/README.md` gives the board.
- **The board serves one pick above its lists.** The pick is the schedule's
  offer, read by `pick` from the three folds. `failure-diagnosed.md` follows
  how a failed sitting moves the next pick.
- **`practice-screens` in the shared core computes what each of the three
  pages says**, so both clients name the same rows in the same order.
- **Choosing stores nothing.** A candidate is listed without its statement, as
  the drill loop's step 2 gives.

## 2. Reading the statement

- **Opening a problem serves its statement and mints nothing.** The web's page
  is `/problems/:problem_id`, and the phone's is the Problem screen. `problems`
  reads the statement from the corpus. The line above the statement names the
  difficulty, the techniques, the user's counts on the problem and its cards.
- **A user may open any number of statements and leave.** No record says a
  problem was opened, as `../api/sitting.md` gives under Minting.
- **A query parameter on the web names where the user came from**, and the way
  back returns there. `../web-app/pages/problems/problem/README.md` gives
  `?technique=`, `?card=` and `?from=problems`.

## 3. The clock and the editor

- **The clock starts on the user's press, or at once where the clock
  preference is on.** The first press mints the sitting through `sitting`,
  and the web adds `?sitting=` to the address. `core-sitting` in the shared
  core sends the requests that mint the sitting and move its clock, on both
  clients.
- **A hidden page or a backgrounded app pauses a running clock**, and
  returning resumes only that pause. Each pause is stored on the sitting as an
  interval, and the elapsed time excludes every pause.
- **The editor proposes no standard-library name.** The phone's own keyboard
  offers the names the file already declares. `../flows/drill-loop.md` gives
  both rules under The editor.
- **The editor opens on the user's work in progress, and never on a solve.**
  A press offers to restore the last solve, and an attempt made after it
  carries `restored`, which mastery does not count as a solve.
- **A sitting nobody touches for 45 minutes ends where it is next read.**
  `../api/sitting.md` gives the idle bound.

## 4. Submitting

- **A submission goes to `submission`, which refuses it past the run caps.**
  The caps are 10 a minute and 60 an hour, and `run-faults` is counted beside
  the attempts. `../api/submission.md` gives the caps.
- **A submission with no clock started mints the sitting first.** An untimed
  sitting is a legitimate way to practise.
- **`runner` runs the code against the problem's cases**, through the broker
  and one sandbox container per run. `../api/runner.md` gives how each case is
  decided.
- **`attempt-log` appends the attempt and its attempt verification.** The
  attempt carries the sitting's id and the elapsed time the clock ran.
- **A failing submission shows the first case it failed, whole**: the
  arguments, the expected value and the value returned or the exception
  raised.
- **A sandbox that answers no result stores a run fault and no attempt.** The
  user is answered 503, and the fault still counts against the caps.
- **A solve leaves the sitting running.** The user may submit a better form in
  the same sitting, and the verdict is read through the first solve.
- **The End press ends the sitting**, and the ended sitting's code is
  read-only.

## 5. The claim and the label

- **At each solve and at the end, each attempt not yet asked is asked in
  turn.** The web asks in a dialog, and the phone in a sheet from the bottom.
- **The claim comes first: which techniques the code used.** The candidates
  are the problem's own techniques, the drilled one the default.
  `attempt-claims` stores the claim, and a decline is a claim too.
- **The label comes second: why the attempt went as it did**, as one failure
  mode. A solved attempt takes `speed` or `none`, and an unsolved one takes
  `gap`, `rust` or `syntax`. `self-labels` stores the label.
- **One press stores both.** A skipped label stores nothing, and a skipped
  claim leaves the fallback standing: the problem's own techniques.
- **A sitting opened from a card offers the card's next rung** beside the way
  back, once the sitting is solved or ended.

## 6. Asking for a retirement

- **A quiet press under the statement asks the author to retire the problem.**
  The web opens a dialog and the phone a sheet. The request names
  `defective` or `copied` and a required note.
- **`retirement-requests` stores the request, and the problem stays served.**
  The author reads it on the inbox and retires the problem by hand, in the
  `author-review` journey.

## Where the web and the phone differ

`../core-package/screens.md` marks a sitting `by platform`, and gives the
reasons.

- **The phone holds the statement and the editor as two tabs** under one bar
  holding the clock and End. The web holds them side by side on one page.
- **The phone reopens the sitting the problem has running**, since it has no
  address to carry `?sitting=`. An ended sitting is not reopened, so a claim
  the sheet left unanswered is not asked again. A web reload asks it again.
- **The phone's own keyboard types the code**, as `../native-app/README.md`
  gives.
- **Signing out on the phone deletes the unsent code** with the rest of the
  phone's copy. The web keeps the draft in the browser.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| The first clock press or submission | the sitting, revised in place | `mastery`, for which sittings were cold; `card-states`, for skipped rungs; `rating`, for cold sittings |
| Each submission | an attempt and its attempt verification | `mastery`, for execution; `template-schedule`, as a review where the problem was written for a template; `card-states`, for solved rungs; the diagnoser, for a failed attempt |
| A submission the sandbox did not answer | a run fault | `submission`, against the caps; the author's inbox |
| The claim | an attempt claim | `mastery`, crediting the techniques; the board's counts |
| The label | a self-label | `mastery`, for the failure mode; the diagnoser, scored against it |
| The retirement press | a retirement request | the author's inbox, through `author-reads` |

`failure-diagnosed.md` follows the stored attempt and label into the next
pick, and `cold-sitting.md` follows a cold sitting into the rating.

## Open questions

- **Which message does the user see after a run fault?** The engine answers
  503 and stores no attempt. No page file names the message either client
  shows.
- **Does a user ever learn what became of a retirement request?** The press
  says the author reads it. No record or screen tells the user the problem
  was retired or kept.
- **Is a sitting on the phone left without a claim counted the same as a
  skipped one?** The page file says its attempts count under the problem's own
  techniques. Mastery then credits the fallback with no signal that the user
  was never asked.
