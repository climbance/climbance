# The author pages

The pages the author reads the running engine from: how learners use the
product, how problem generation goes, and what waits for the author's hand.
The author is the person who generates and reviews the corpus, authors the
content and deploys the engine. These pages sit under no section, in an
author area of their own, on the web alone.

| URL | The author | File |
|---|---|---|
| `/author` | opens one of the pages below | this file |
| `/author/product` | reads how many learners use the product, how much and how long they stay | [`product`](product/README.md) |
| `/author/generation` | reads the drafts, the landing rate, the spend per landed problem and the corpus | [`generation`](generation/README.md) |
| `/author/workflow` | reads what waits in each by-hand pass and queue, the run faults and the spend by part | [`workflow`](workflow/README.md) |

The content browser's pages, which list the questions, the cards and the
problems, join this area under `/author` too.

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
  pages with no invitation to set.
- **Every author route answers 403 to a user without the role**, under
  `/api/author/`. The web app hides the account menu's Author entry from that
  user, and a learner typing an `/author` path reads the not-found page. The
  route's answer is the guard, and the hidden entry only keeps the menu
  accurate.
- **The author routes are reachable from the internet, guarded by the role
  alone.** One check guards every `/api/author/` route, and a test shows a
  learner answered 403 on each. A stronger boundary serves the author routes
  on loopback alone, reached through `just tunnel`, so a fault in the role
  check exposes nothing. The trigger for taking it is sign-in opening beyond
  invitations, when a stranger could hold a session.

## Where the figures come from

- **Each engine reads its own store.** The author pages at the hosted engine
  read prod's store, and the pages at `just app` read the local one. Each
  figure therefore needs no tunnel and no copy of the store.
- **The product page counts across users and lists no user.** Each user's log
  is private, and `../../../concepts/log-records.md` keeps each reader to one
  user's records. The product page's queries return counts grouped by day,
  and never a row of one user's log. Feedback and retirement requests are
  notes addressed to the author, so the workflow page lists them whole, as
  `climb feedback` does today.
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
| `climb feedback` | workflow | retired |
| `climb problem --requests` | workflow | retired |
| Ad hoc queries over run faults | workflow | gone |

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
- **`climb log export` stays.** The operator exports one user's log on that
  user's request, and the settings page already gives the user the same file.
