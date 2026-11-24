# The phone offline

A user opens the phone with no connection, answers a knowledge queue from the
phone's own copy, and later reconnects. The answers then reach the engine and
the web. This page follows the `phone-offline` journey in `../model.toml`. It
starts at the phone's Home with no connection. It ends once the outbox is
sent and the web reads the same answers.

`../core-package/knowledge/store.md` gives the rules of the copy and the
outbox, and this page cites it rather than restating them. Each component
below is named by its id in `../model.toml`.

## 1. Opening the app with no connection

- **The phone starts with no connection, and the web does not.** The browser
  fetches the page's own files from the engine on each load. A service worker
  serving them offline is deferred, as `store.md` gives under Offline.
- **The app opens on the Practice tab.** The board's knowledge part serves from
  the phone's copy, so the first screen works offline.
  `../web-app/pages/practice/board/README.md` gives the landing.
- **The rest of the board and the Cards tab say there is no connection.** The
  phone reads the board and the cards from the engine and keeps no copy of
  them, as `../core-package/screens.md` gives under What the phone reads from
  the engine. Reading a card picks nothing, so the cards need no copy.
- **The Home screen reads the phone's copy.** `client-store` keeps the
  snapshot and the user's log in SQLite, keyed to the signed-in user. The
  launch reads the copy first, so the first question waits for no round trip.
- **The copy's snapshot stands while the connection is down.** `snapshot`
  revalidates the copy by its ETag at the next sync, as `../api/snapshot.md`
  gives.

## 2. Answering a queue offline

- **Continue starts the next queue from the copy, as with a connection.**
  `queues` picks each question on the phone, and `answering` runs the queue
  on the quiz screen. `knowledge-queue.md` follows the queue itself.
- **Each answer waits in the outbox**, which is part of the copy. A killed
  app keeps the outbox, so no answer is lost with the connection.
- **Every other record the user writes waits there too**: the queue's stint, a
  focus, a module's status, a raise, an order and a lesson mark.
- **The schedule reads the phone's own answers at once.** The phone's next
  pick reads the answer just given, before the engine has stored it.

## 3. The sync's state

- **The phone names the sync's state in Settings and in Home's footer**, with
  a press that syncs now. A failed sync reads as a sync error, and a press on
  it gives the details.
- **Pulling a list down syncs**, since a phone has no reload. A screen reading
  the engine reads it again after the pull.
- **A sync tried with no connection fails, and the outbox stays whole.** A
  record leaves the outbox only once the engine stored it, knew it already,
  or refused it.

## 4. Reconnecting

- **The phone syncs when the app becomes active**, and sends each new answer
  within ten seconds. Every other record is sent at once, since a focus, a
  status or a limit changes what another device serves.
- **`knowledge-sync` stores each sync line the upload carries.** A line naming
  content the store does not hold is refused alone, and the reply names it.
  `../api/knowledge-sync.md` gives the lines.
- **`knowledge-log` holds each stored line in one of nine append-only
  tables.** `../api/knowledge-log.md` gives the tables.
- **Every upload returns the records written since the phone's cursor.** The
  phone merges them into its copy by `client_id`, so a record another device
  wrote reaches the phone's schedule before its next pick.
- **A token the engine revoked keeps the copy.** The app returns to the login
  page, and the outbox waits for the same user's next sign-in.
  `../api/app-tokens.md` gives the token's lifetime: 90 days unused.

## 5. The web reads the same answers

- **The web syncs when its page becomes visible.** The upload returns every
  record since the web's cursor, the phone's answers included.
- **An answer given on the phone reaches an open web page at the page's next
  sync.** The web's schedule then replays the same answers the phone's did,
  through the same rules in `packages/core`.
- **The phone's records name the phone's device name, and the web's records
  name the device `web`.** A browser carries no stable device name. The
  journey ends here.

## Where the web and the phone differ

- **The phone starts a queue with no connection, and the web does not.** The
  web keeps serving a queue already running once the connection drops, as
  `store.md` gives.
- **The phone pulls a list down to sync, and the web syncs when the page
  becomes visible.** A phone has no reload.
- **The phone names the sync's state on Home's footer as well as in
  Settings.** The web names it on the settings page alone, as
  `../core-package/screens.md` gives.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| An answer given offline | an answer, in the phone's outbox | the phone's `queues` at once; `knowledge-sync` at the next sync |
| A queue stopped offline | a stint, in the outbox | the summary; `knowledge-sync` at the next sync |
| A focus, status, raise or order offline | its record, in the outbox | the phone's `queues` at once; every other device after the sync |
| The upload | each line, in `knowledge-log` | every device's next sync, which returns it |
| The reply | the records since the cursor, merged into the copy | the phone's next pick |
| A refused line | nothing, and the line leaves the outbox | the reply, which names it |

`knowledge-queue.md` gives which component reads each kind of record.

## Open questions

- **Does an offline phone's token expire on a long trip?** The token expires
  after 90 days unused, and each use extends it. An offline phone sends no
  request, so no doc says whether the outbox survives a token that lapsed
  before the phone reconnected.
- **Does the user learn that a line was refused?** The reply names each
  refused line, and the line leaves the outbox. No doc says whether the phone
  shows the refusal, so an answer to content a seed removed is lost silently.
- **In which order does the schedule replay answers given offline on two
  devices?** The copy merges records by `client_id`. No doc says whether FSRS
  replays them in the order given or in the order the engine stored them.
- **Which parts of the board serve offline?** The board's page file says its
  knowledge part serves from the copy. `screens.md` says the Practice tab
  says there is no connection, and no doc lists which rows of the tab stay.
