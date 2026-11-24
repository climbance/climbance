# The author pages

The pages the author reads the running engine from: what waits for the
author's hand, every piece of content, how learners use the product, how
problem generation goes and what the model calls cost.
The author is the person who generates and reviews the corpus, authors the
content and deploys the engine. These pages sit under no section, in an
author area of their own, on the web alone.

| URL | The author | File |
|---|---|---|
| `/author` | reads what waits in each by-hand pass and queue, the feedback and the run faults | [`inbox`](inbox/README.md) |
| `/author/questions` | reads one module's questions at once, each as answered, with its concept | [`questions`](questions/README.md) |
| `/author/lessons` | reads one module's lessons, each whole, with the questions it teaches | [`lessons`](lessons/README.md) |
| `/author/cards` | reads every card with its templates revealed, its requirements and its ladder | [`cards`](cards/README.md) |
| `/author/problems` | reads every problem, served or retired, with its statement, solutions and cases | [`problems`](problems/README.md) |
| `/author/product` | reads how many learners use the product, how much and how long they stay | [`product`](product/README.md) |
| `/author/generation` | reads the drafts, the landing rate, the spend per landed problem and the corpus | [`generation`](generation/README.md) |
| `/author/spend` | reads what each part's model calls cost | [`spend`](spend/README.md) |

## The navigation

- **The author area's navigation names its pages in three groups.** The
  inbox is the first group. The content browser's four pages are the second.
  The product, the generation and the spend are the third. The groups follow
  what the author does on each page: act on what waits, review content, and
  read figures.
- **The inbox is the author area's home, at `/author`.** The author opens the
  area to learn whether anything needs the author's hand, and the inbox
  answers that first. `inbox/README.md` gives the count its entry carries.

## The content browser

The content browser is the four pages listing content: the questions, the
lessons, the cards and the problems. The author reads a whole bank there at
once, as a learner would see each item. A question is otherwise reviewed one
at a time in a queue, where a rule broken across a bank, such as long hand
traces, goes unseen.

- **The browser's pages are built in this order: the questions, the lessons,
  the cards, then the problems.** The questions are the largest bank and the
  one reviewed only in a queue today. The lessons read from the same snapshot,
  so the lessons page reuses the questions page's filters.
- **Each page reads the content of the engine serving it.** The questions and
  the lessons come from the snapshot, which the seed builds from the store.
  The cards and the problems come from `/api/author/`. `just app-prod` then
  shows prod's content and `just app` shows the local store's.
- **Each item is drawn with the component a learner's page draws it with.** A
  question uses the queue's answered question, a lesson the lesson page's, a
  card the card page's, and a statement the sitting's. A component of the
  browser's own could show an item differently from what a learner reads.
- **The browser only reads.** A change to a question, a lesson or a card is an
  edit in the content repository, then a seed. A problem is never edited and
  is retired with `climb problem --retire`. No press writes a log record,
  so a review leaves the author's own schedule and board unchanged.
- **A page lists every matching row in one scroll, each row closed.** A
  closed row reads on one or two lines. The author scans the closed rows for
  a pattern, then opens the rows that show one.
- **A press opens a row in place on the questions, the lessons and the cards
  pages.** An opened question, lesson or card reads in a screen or less, so
  several open rows read together.
- **The problems page opens a row in a panel beside the list.** An opened
  problem holds a statement, up to three solutions and its cases, and runs
  taller than a window. Opened in place, it would push the next row out of
  sight. Each opened problem is also a request of its own, so the problems
  page offers no Open all.
- **On every browser page, `j` and `k` move to the next and the previous row,
  and open it.** The anchor in the URL follows the opened row. A review then
  reads each row in turn without a pointer.
- **A row's anchor is its slug, or a problem's id prefix**, as `#<slug>`. A
  link to the anchor opens that row, so the pages link to each other's rows: a
  lesson to its questions, a card to its rungs.
- **The filters live in the URL, and each chip counts what pressing it would
  leave**, as on the problem listing. A filtered view is then a link the author
  keeps.

## Who sees them

- **An author role on the invitation gates every author page.** The
  `invitations` row of an email carries a `role`, `learner` by default or
  `author`. A request reaches an author page only when one of the signed-in
  user's identities has an email whose invitation reads `author`.
- **`climb invite add --author <email>` sets the role, and `climb invite add
  <email>` without the flag sets it back to `learner`.** The invitation is the
  record the engine already keys by email, and the author is invited like any
  user. Withdrawing the invitation removes the role at the next request,
  because the role is read from the invitation at each request rather than
  copied onto the user.
- **The dev login is an author.** The dev login answers on loopback alone, as
  `../../../api/sign-in.md` gives, so the local engine shows its own store's
  pages with no invitation to set. Off loopback the dev login's user is no
  author.
- **Every author route answers 403 to a user without the role**, under
  `/api/author/`. The web app hides the account menu's Author entry from that
  user, and a learner typing an `/author` path reads the not-found page. The
  route's answer is the guard, and the hidden entry only keeps the menu
  accurate.
- **Off loopback, an author route also needs the user `CLIMB_AUTHOR_ID`
  names.** The variable is set on the hosted engine alone. Open sign-up lets a
  stranger hold a session, and an author invitation set on a mistyped or lost
  email would otherwise open the pages to that address's holder. The pinned
  id is read from the server's environment, which no sign-in and no
  invitation writes. Unset, the hosted engine serves no author page.
- **A request that arrived at a loopback address needs the role alone.** The
  dev login answers there and is an author, and `just app-prod` signs in
  through it. One check guards every `/api/author/` route and `/api/me`'s
  author flag, and a test walks each route off loopback: answered with the
  role held and the id pinned, refused with either missing.
- **Inside the hosted `api` container, every request arrives off loopback.**
  Caddy's request arrives at the container's own address over the compose
  network, and so does one through the host's published port. The hosted
  engine therefore always applies the pinned id.

## Where the figures come from

- **The author reads prod's figures from a local engine over the database
  tunnel.** `just app-prod` runs `just app` with `DATABASE_URL` naming the
  local end of the deployment repo's `just tunnel`, which forwards prod's
  Postgres. The author signs in through the dev login, which answers on
  loopback alone and is an author. Each figure therefore needs no copy of the
  store. The hosted pages read the same figures for the pinned author.
- **The dev login signs in as the author's prod user, `PROD_AUTHOR_ID` in
  `.env`.** `just app-prod` refuses to start without it. The dev login
  otherwise mints a user named `local` in prod's store, and the product page
  would count that user as a learner.
- **The product page counts across users and lists no user.** Each user's log
  is private, and `../../../concepts/log-records.md` keeps each reader to one
  user's records. The product page's queries return counts grouped by day,
  and never a row of one user's log. Feedback and retirement requests are
  notes addressed to the author, so the inbox lists each one whole,
  naming no sender.
- **Every figure is computed from the store on each load, and none is stored.**
  The figures are counts and sums over append-only tables, and a stored copy
  would need a rule for when it goes stale.
- **A figure is a table before it is a chart.** Which figures earn a chart,
  and over which period, is deferred until the author has read the tables
  over real use.

## The reads each page replaces

| Read before the pages | Moves to | Then |
|---|---|---|
| Ad hoc queries over users, sittings, attempts and answers | product | gone |
| Ad hoc queries over drafts, site outcomes and the call log's cost | generation | gone |
| `climb gaps` | generation, as the corpus by template | retired |
| `climb feedback` | inbox | retired |
| `climb problem --requests` | inbox | retired |
| Ad hoc queries over run faults | inbox | gone |
| Ad hoc queries over the call log's cost by part | spend | gone |

## What stays a command

- **Every command that writes stays a command**: `generate`, `seed`, `claim`,
  `match`, `difficulty`, `diagnose`, `judge`, `fill`, `invite` and `log erase`.
  A page earns one of these actions only after the author has used the page
  that shows what the action would change.
- **A command that makes model calls to measure stays a command**: `score`.
  A page shows only what such a run stored. `movement` and `score --stored`
  stay commands too, because each reads one user's log, the author's own, for
  the eval set, and the product page reads no single user.
- **A command reading authored files rather than the store stays a
  command**: `module status`, `card`, `library` and `spot`. The hosted engine
  holds no copy of `content/` and no spot sheet, so a page there could not
  read them.
- **`climb problem`, apart from `--requests`, and `climb board` stay until
  another page covers them.** The content browser lists the problems, and the
  Practice section is the board.
- **A page names the command that acts on what it shows, and a press copies
  it.** The inbox copies each by-hand pass's command, and the problems page
  copies the commands retiring a problem and rating it by hand. The author
  then pastes a command naming the right id, never retypes it.
- **The first writes a page may earn are retiring a problem and rating it by
  hand**, both from the problems page's panel. The author reads the problem
  in the panel before running either command, and decides there.
  Each write is deferred until the author has used the copied commands, by
  the rule opening this section.
- **`climb log export` stays.** The operator exports one user's log on that
  user's request, and the settings page already gives the user the same file.
