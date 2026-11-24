# A client's store

The web app and the native app keep the knowledge log the same way. Each app
runs the rules from `packages/core`, and each keeps a copy of the content and
of the user's log on the device. A platform differs from the other only where
the platform itself cannot do the same.

## The copy

- **A client keeps the snapshot and the user's log between launches.** The
  native app keeps them in SQLite, and the web app keeps them in IndexedDB.
  A launch reads the copy first, so the first question waits for no round
  trip.
- **A launch then syncs from the copy's cursor.** A copy that is gone, after
  a cleared browser or a reinstalled app, syncs with no cursor and receives
  the whole log again. The engine's log is the truth, and a copy is only
  ever rebuilt from it.
- **The snapshot is revalidated by its ETag.** The content moves only at a
  seed, so an unchanged snapshot answers 304 and the copy stands.
- **The copy is keyed to the signed-in user.** A second account signed in on
  the same device would otherwise read the first account's log and upload
  its outbox under the wrong user. The native app marks each row with its
  owner. The web app keeps one IndexedDB database per user, named by the
  user's id, and the session names the user before the database opens.
- **The engine names the user when it issues a token and in every sync
  reply.** A copy kept before the owner was recorded is then claimed by the
  account whose token wrote it, at that account's next sync.
- **A token the engine revoked keeps the copy.** The app returns to the login
  page, and the outbox waits for the same user's next sign-in. Another
  account signing in reads only its own rows.
- **Signing out sends the outbox, then deletes the copy.** A copy left behind
  keeps a user's log readable on a shared device. An outbox that cannot be
  sent is named before sign-out discards it, so the user decides whether
  those answers are lost.
- **A web tab closes its copy when another tab deletes it, then reloads.**
  IndexedDB holds a deletion until every open connection closes. One more
  open tab of the same user would otherwise stall a sign-out or an account
  deletion before it revokes the session. The reloaded tab finds the session
  gone and shows the login page.

## The outbox

- **A record the engine has not acknowledged waits in the outbox.** The
  outbox is part of the copy, so a record survives a closed tab, a killed app
  and a lost connection.
- **An answer is sent within ten seconds of being given.** Answers given in
  quick succession then travel in one upload. Every other record is sent at
  once, since a focus, a status or a limit changes what another device
  serves.
- **A client also syncs when it returns to the foreground**: the app becoming
  active, or the page becoming visible. Records another device wrote in the
  meantime then reach the schedule before the next pick.
- **Every upload returns the records written since the cursor.** An answer
  given on the phone reaches an open web page at the page's next sync.
- **A record leaves the outbox once the engine stored it, knew it already
  or refused it.** A refused line names content the store does not hold, so
  sending the line again would be refused again.

## Offline

- **A queue keeps serving while the connection is down**, on both clients,
  since the rules and the copy are on the device.
- **The web app does not start without a connection, where the native app
  does.** The browser fetches the page's own files from the engine on each
  load. A service worker serving those files offline is deferred until a
  user practises on the web away from a connection.
- **The web app's records name the device `web`.** A browser carries no
  stable device name, and telling one browser from another would answer no
  question the schedule asks.
