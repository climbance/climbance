# The author's review

The author opens the author area, reads what waits for the author's hand, and
answers each waiting row with a command in the terminal. This page follows the
`author-review` journey in `../model.toml`. It starts at the author area's
inbox, at `/author`. It ends once each waiting row on the inbox is answered by
its command.

`../web-app/pages/author/README.md` gives the rules every author page shares,
and this page cites it rather than restating them. Each component below is
named by its id in `../model.toml`, and its file under `../api/` or `../cli/`
gives its rules.

## 1. Opening the author area

- **The author role on the invitation gates every author page.** Off
  loopback, a route also needs the user `CLIMB_AUTHOR_ID` names.
  `../web-app/pages/author/README.md` gives the checks under Who sees them.
- **The author reads prod's figures from a local engine, through `just
  app-prod`.** The local engine reads prod's Postgres over the database
  tunnel, and the dev login signs in as `PROD_AUTHOR_ID`. The hosted pages
  read the same figures for the pinned author.
- **`author-reads` answers every author page's figures under
  `/api/author`**, read from the store on each load. No figure is stored, so
  each page shows the store as it stands.
- **A column left of every page names the inbox, then `Content`, then
  `Figures`.** The inbox's entry counts the rows under What waits that count
  something. `../web-app/pages/author/navigation.md` draws the column.

## 2. The by-hand passes

- **The inbox opens on what waits, one row per kind of work.** Each row
  counts the items waiting and names the command that clears it. A press
  copies the command, and the author pastes it into the terminal.
  `../web-app/pages/author/inbox/README.md` gives each row's count.
- **`claim --by-hand` counts the author's own attempts with no user claim.**
  The pass appends an attempt claim with `source` `user`. Mastery and the
  eval set read the author's claims.
- **`match --by-hand` counts the canonicals with no user template match.**
  The pass appends a template match, and the ladder of each card is derived
  from the template matches.
- **`difficulty judge` counts the served problems with no rating under the
  standing correction.** `difficulty` draws each problem and stores a
  difficulty rating, as `../cli/difficulty/judge.md` gives under The run.
  With no standing correction, the row says to run `difficulty correct` first.
- **`judge build` and `fill build` count the templates whose items are not at
  the template's current code.** Each build appends judgement items or
  key-line items, as `../cli/exercise-items.md` gives.
- **A row counting nothing reads `clear`**, and stays on the page. A row that
  vanished could equally mean a figure that failed to load.

## 3. Problems and retirement requests

- **The `Needs attention` row counts the served problems carrying an
  attention flag.** The row links to `/author/problems?flag=any`.
  `../web-app/pages/author/problems/README.md` gives the five flags under
  Attention flags.
- **Each waiting retirement request reads as one row, newest first.**
  `retirement-requests` stored the request in the `sitting` journey, as
  `sitting.md` gives under step 6. A request waits while its problem is still
  served, and the row names no user.
- **A request's row links to the problem's row on the problems page.** The
  dialog there shows the statement, the solutions, the cases, the difficulty
  and the site outcomes. The author reads the problem before deciding.
- **The dialog's foot copies the commands acting on the problem**: retiring
  it as `defective`, retiring it as `copied`, and rating it by hand. Each
  command names the full id, so the command cannot match a second problem.
- **`climb problem --retire` prints the problem and its requests, then asks
  to confirm.** A retired problem is no longer served, and the request moves
  to the answered rows. `../api/problems.md` gives what a retirement changes.
- **`climb problem --rate` stores a `user` difficulty rating.** A `user`
  rating stores no deviation, and is read as deviation zero.

## 4. The learners' reports

- **The feedback reads newest first, each note whole**, with the client and
  the page it was sent from. `feedback` stored each note in the `account`
  journey, as `account.md` gives. A note has no read state, so no command
  answers a note.
- **The answered retirement requests read below the waiting ones**, each
  naming the status its problem holds now.
- **The run faults read as a count per day and run kind for the last 30
  days**, then the latest faults with the runner's message. `run-faults`
  stored each fault in the `sitting` journey, and no fault names its user.

## 5. Reviewing the content

- **The questions, the lessons, the cards and the problems pages list a whole
  bank at once.** Each item is drawn with the component a learner's page
  draws it with. `../web-app/pages/author/README.md` gives the content browser.
- **The browser only reads, and no press writes a log record.** A review
  therefore leaves the author's own schedule and board unchanged.
- **A change to a question, a lesson or a card is an edit in the content
  repository, then `climb seed`.** `seed` refreshes the content tables and
  retires each row a log record references, as `../cli/seed.md` gives.
- **The cards page names each core template no solution displays as a gap.**
  The gap names the template the next `climb generate` run needs.

## 6. Reading the figures

- **The product page counts learners, acts and retention across users**, and
  lists no user. The author's own log is left out of every figure.
  `../web-app/pages/author/product/README.md` gives each count.
- **The generation page reads the drafts per writing state, the landing rate,
  the spend per landed problem and the corpus by template.** A held state's
  row names its oldest draft's age.
- **`climb generate --resume` re-enters every held draft.** `generation`
  resumes each draft at the first step whose configuration or prompt hash
  moved, as `../cli/generation/states.md` gives.
- **`climb generate` writes new problems for a template.** Each landed
  problem then reads as `unrated` on the problems page until the next
  `difficulty judge` run rates the problem.
- **The spend page reads each part's model call cost for the last 30 days**,
  by the record citing each call. `../web-app/pages/author/spend/README.md`
  gives how a call is assigned to a part.

## 7. Diagnosing failed attempts

- **`climb diagnose attempts` reads every failed attempt with code.**
  `diagnoser` stores a diagnosis naming `slip` or `form`, as
  `../cli/diagnoser.md` gives. An attempt already read at the same
  configuration and prompt hash is skipped.
- **The pick reads a diagnosis where no self-label stands**, once the
  configuration that wrote the diagnosis is measured. `failure-diagnosed.md`
  follows a diagnosis into the next pick.
- **No author page lists the failed attempts awaiting a diagnosis.** The
  author runs the command without a row naming it.

## The phone

`../core-package/screens.md` marks the author pages `web only`. The author
reads the pages at a desk, beside the terminal in which the commands acting on
them run. The phone offers no author screen and no entry to one.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| Opening any author page | nothing | none |
| `claim --by-hand` | an attempt claim with `source` `user`, on the author's attempt | `mastery`, crediting the techniques; the eval set |
| `match --by-hand` | a template match with `source` `user` | the ladder, in `cards-and-recall.md` |
| `difficulty judge` | the draws and a difficulty rating per problem | the standing difficulty; `rating` and `mastery`, for the standing score; a cold sitting, in `cold-sitting.md` |
| `judge build`, `fill build` | judgement items, key-line items | `short-exercises`, in `cards-and-recall.md`; `diagnoser`, as labelled mutants |
| `climb problem --retire` | the problem's status and reason | `problems`, which stops serving it; `mastery`, which drops a defective problem's attempts; the inbox's answered requests |
| `climb problem --rate` | a difficulty rating with `source` `user` | the standing difficulty, as `difficulty judge` does |
| `climb seed` | the content tables and the concepts | `snapshot`, for both clients, in `knowledge-queue.md` and `first-run.md`; the questions page, for the concepts |
| `climb generate`, `--resume` | drafts, site outcomes, and each landed problem with its cases and solutions | the problem listing, in `sitting.md`; the generation and problems pages |
| `climb diagnose attempts` | a diagnosis per failed attempt | `pick`, in `failure-diagnosed.md` |

The learner journeys write the rows the inbox lists. `sitting.md` writes the
retirement requests and the run faults, and `account.md` writes the feedback.

## Open questions

- **Which component writes the by-hand passes' records?** The journey names
  `diagnoser`, `seed` and `generation`, which answer no inbox row. The record
  leaves out `classifier`, `matcher` and `exercise-items`, whose commands are
  four of the five by-hand rows.
- **Does any command answer a run fault?** The inbox lists the faults, and
  no doc names a command or a decision a fault asks of the author. The
  journey's end, each waiting row answered, reaches neither the faults nor
  the feedback.
- **Should the inbox count the failed attempts awaiting a diagnosis?** The
  pick reads diagnoses, and `climb diagnose attempts` is run with no row
  saying it is due. A by-hand pass of the same shape has a row.
- **Does a retirement answer every request on its problem?** A request waits
  while its problem is served, so a retirement answers all of them. A request
  the author decides to reject keeps its problem served, and stays waiting
  with no command to clear it.
