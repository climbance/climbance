# The account on the web and the phone

A user opens the account menu, changes the settings, sends feedback, manages
the signed-in devices, exports the record, and signs out or deletes the
account. This page follows the `account` journey in `../model.toml`. It
starts at the account menu. It ends signed out, or with the account deleted.

`../web-app/pages/settings/README.md` gives the settings, and
`../api/sign-in.md` gives the sessions and the deletion. This page cites them
rather than restating them. Each component below is named by its id in
`../model.toml`.

## 1. The account menu

- **The account menu sits at the right of the navigation on both clients.**
  The menu names who the session signs in as: the address the provider
  verified, with the engine's own id under it. A user the dev login reached is
  named by the id alone.
- **The menu links the settings, the signed-in devices, the sign-out and the
  guide.** `../web-app/pages/shell/README.md` gives the menu.
- **`core-account` in the shared core names what the menu and the settings
  offer**, so both clients name the same acts.

## 2. The settings

- **The web's settings are `/settings`, and the phone's are the Settings
  screen.** The two read in one order: the account, the study settings, the
  sync, the archived modules, feedback, then the record.
  `../web-app/pages/settings/settings.md` draws the page.
- **The account names every Google or GitHub account connected to the user,
  oldest first.** A connected account's address is shown only where it
  differs from the name above it.
- **The study settings are the daily limit on new questions and the exam
  size.** Each field names its range, 0 to 200 and 1 to 500. Save waits until
  both fields hold a value in range and one of them changed.
- **A saved study setting is a record of the user's log**, sent as a
  `setting` sync line through `knowledge-sync`. A value saved on one client
  then stands on the other.
- **The sync reads its state and offers Sync now.** The phone also names the
  state in Home's footer, as `phone-offline.md` follows.
- **The archived modules list with a Restore press each.** Restoring stores a
  module status change, and the module returns to the home with its answers,
  as `../core-package/knowledge/queues.md` gives under Module status.
- **The phone's Settings also hold the device name and the reminder hour**,
  which are about one phone. The signed-in devices name an app by the device
  name it signed in with.

## 3. The colour scheme

- **The web switches between light and dark from the navigation**, where a
  reader at a desk reaches the switch.
- **The phone chooses System, Light or Dark in Settings.** System follows the
  phone's own setting, and is the default.
- **The choice stays on the device or in the browser, and no record stores
  it.** The choice is about one screen rather than the account.

## 4. Feedback and the error screen

- **Send feedback opens a dialog on the web and a sheet on the phone**, from
  the settings and from the error screen. The note is required, and at most
  2000 characters.
- **`feedback` stores the note as a `Feedback` record**, naming the client and
  the page it was sent from. A user's notes are capped at 10 a minute and 60
  an hour. `../api/feedback.md` gives the record.
- **The author reads every note on the inbox**, which `author-review.md`
  follows. No reply reaches the user, since a reply is deferred.
- **A screen that throws is replaced by the error screen, on both clients.**
  The screen says the error was reported, and offers Reload and Send feedback.
- **The client reports the error to the API, which writes the report as one
  line of its log.** The report carries no code the user typed.
  `../api/README.md` gives the report under Client error reports.

## 5. The signed-in devices

- **The signed-in devices open from the account menu**: a dialog on the web,
  a screen on the phone. The list names every browser session and every app
  token signed in as the account, each with when it was last used.
- **A browser is named by its browser and its system, and an app by its
  device name.** Two browsers on one account then read apart in the list.
- **Revoke cuts off any other device in the list.** `sign-in` revokes a
  browser's session, and `app-tokens` revokes an app's token.
- **The row naming the device the list is read on signs out instead of
  revoking.** Signing out sends the outbox first, and a bare revoke would leave
  the outbox unsent.
- **A revoked phone keeps its copy and returns to the login page.** The outbox
  waits for the same user's next sign-in, as
  `../core-package/knowledge/store.md` gives.

## 6. Exporting the record

- **Export the record saves every record of the user's log as one JSON
  file.** The web downloads the file, and the phone saves it into a folder the
  user picks.
- **The export holds every record an erasure deletes**, the card runs, the
  recall attempts and the feedback included. `../concepts/log-records.md`
  gives the export.
- **Exporting stores nothing.**

## 7. Signing out

- **Sign out sits in the account menu and in the settings.** The client sends
  the outbox first, then deletes the device's copy of the content and the log.
- **An outbox that cannot be sent is named before the sign-out discards it**,
  so the user decides whether those records are lost.
- **The web's sign-out revokes the session and clears its cookie.** The
  phone's sign-out revokes the app's token.
- **The provider's own session stays in place.** The next sign-in shows the
  provider's account chooser, so the user may pick another account.

## 8. Deleting the account

- **Delete the account sits last on the settings**, since the deletion is the
  one act there that cannot be undone.
- **The deletion asks for the account's name typed back, and the engine checks
  it.** The name is the verified email, or the user id where no provider
  linked one.
- **`sign-in` erases the log, then deletes the user in the same transaction.**
  The identities, the sessions, the app codes, the app tokens and the
  invitations of the identities' emails go with the user.
- **The client signs out without sending the outbox**, since the outbox
  belongs to the deleted log.
- **Signing in again is a new sign-up under the pace**, and mints a new user,
  as `first-run.md` follows.
- **The engine also deletes an account no session or token has used for 12
  months.** `climb log prune` runs the deletion daily, and an account holding
  an invitation is never deleted this way.

## Where the web and the phone differ

`../core-package/screens.md` marks four of this journey's rows `by platform`
or `phone only`, and gives the reasons.

- **The export downloads on the web, and saves into a picked folder on the
  phone.**
- **The colour scheme is a switch in the web's navigation, and a choice of
  three in the phone's Settings.** Section 3 gives the reason.
- **The device name and the reminder hour are the phone's alone.** Each one
  is about one phone.
- **The error screen is marked `by platform`.** A screen that threw is
  replaced in place on both clients.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| Save on the study settings | a setting change, in `setting_changes` | `queues`, for the daily limit; the exam's size; every device after its sync |
| Restore | a module status change | `queues`; the home's rows |
| The colour scheme | nothing in the store, the choice on the device | that device's screens |
| Send feedback | a `Feedback` record | the author's inbox, through `author-reads`; the export; an erasure |
| A screen that threw | a line of the API's log | the operator, for the log's 14 days |
| Revoke | the session or the app token, revoked | the next request from that device, answered 401 |
| Sign out | the outbox sent; the session or the token, revoked | the engine's log, through `knowledge-sync`; the device's copy is deleted |
| Delete the account | nothing; the log and the user are deleted | the next sign-in, which mints a new user |

## Open questions

- **Which reminder does the reminder hour set, and how does it arrive?** No
  doc gives the reminder. `packages/core` computes the next review time and
  the next reminder at the hour. No doc says how the phone notifies the user.
- **Does a changed device name rename the app in the signed-in devices?** The
  list names an app by the device name it signed in with. No doc says whether
  a name set in Settings later reaches the token's row.
- **Why is the error screen `by platform`?** `screens.md` marks the row and
  gives no reason under Where the clients differ. The shell offers Reload on
  both clients, though a phone has no reload.
- **Which copy does a second phone keep after the account is deleted?** The
  deletion removes every app token, and a revoked token keeps the copy for the
  same user's next sign-in. A new sign-up mints a new user, so no doc says
  whether that copy is ever discarded.
