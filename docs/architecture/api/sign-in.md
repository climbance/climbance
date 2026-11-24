# Sign-in

The engine's user, whose id every private record carries, and the way a person
reaches it. Google and GitHub hold each identity and its login. A person signs
in through one of the two, and the engine stores no password. Password resets,
second factors and leaked credentials are the provider's to handle, so no
credential handling is the engine's own.

`app-tokens.md` gives how the native app signs in through the same flow.

## Providers and identities

- **The engine runs the sign-in flow itself, through Authlib, which checks the
  state, the nonce and PKCE.** A managed account provider is rejected: its
  login and its tokens live on its own domain, and the session cookie stays on
  the pages' origin.
- **An `identities` row links a provider's user id to a user id the engine
  mints at the first sign-in.** The log keys on the engine's id, so adding or
  replacing a provider rewrites no record.
- **A new account whose email matches another account's joins that account's
  user, so one person reaches one log through Google or GitHub.** The email
  counts only where the provider verified it. An address added and never
  verified would otherwise join the log of whoever holds that address.
- **Sign-in by email is deferred until a user needs it.** An emailed link, a
  managed provider or a company's own sign-in would each be one more provider
  an `identities` row names.

## Sign-up

- **Anyone may sign up, at a pace of 20 new users a day and up to 200 users
  in all.** The callback mints a user for a verified email no account holds
  while fewer than 20 users were minted in the last 24 hours and fewer than
  200 exist. A signed-in user's code runs on the engine, so the pace bounds
  how many strangers can reach the sandbox before its hardening is proven.
- **The limits gate only the minting of a user.** An existing user signs in
  past them, and so does a new identity joining an existing user by its
  email. Every user counts toward both limits, an invited one included.
- **Past either limit, the callback stores no user, identity or session, and
  the login page says today's places are taken.** A person refused comes back
  on a later day. A waitlist was rejected: letting a listed person in later
  needs an email to tell them, and the engine sends no email.
- **An email the `invitations` table holds is admitted past both limits.** An
  invitation is added, withdrawn and listed by `climb invite`. Withdrawing one
  no longer stops a sign-in, since an email with no invitation signs up too.
- **The author blocks an abusive account by deleting it with `climb log
  delete --user`.** The command runs the deletion the account menu runs, and
  asks for the user id typed back, as `climb log erase` does. A
  block that keeps the email from signing up again is deferred until one
  account needs it.
- **The two limits are constants in the sign-in code, raised by a commit.**
  The ceiling of 200 is the trigger for the sandbox's further isolation, as
  `../sandbox/README.md` gives. The dev login is never limited, since it
  answers on loopback alone.

## The author role

- **An invitation carries a `role`, `learner` by default or `author`.** The
  author pages are open to a user one of whose identities' emails holds an
  `author` invitation. The role is read from the invitation at each request,
  so a withdrawn invitation removes it at once.
  `../web-app/pages/author/README.md` gives the pages and how the role is set.
- **An author signs in as any user does, and keeps one log.** The author is
  also a learner, and the eval set and the by-hand passes read the author's
  own log. A separate account for authoring would split that log from the
  pages reading it, and would duplicate the sign-in.

## Sessions

- **The engine keeps each session in Postgres for 30 days, and sets the
  session's token in an `HttpOnly`, `SameSite=Lax` cookie.** A stored session
  can be revoked, where a signed token stands until it expires.
- **The table holds the hash of each token, and never the token.** A copy of
  the table then signs nobody in.
- **A request naming a user without a live session answers 401, and the pages
  send the browser to the login page.** The login page offers each configured
  provider and the dev login, and needs no session itself.
- **Signing out revokes the session and clears its cookie.** A copy of the
  cookie kept elsewhere then signs nobody in either.
- **A session records when it last signed a request in and the user agent it
  was opened by, as an app's token records its device.** Two browsers on one
  account then read apart in the list.
- **The account menu lists every signed-in device, each browser's session and
  each app's token, and revokes any one of them, on either client.** Signing
  out in the app revokes that app's token.

## The dev login

- **A dev login signs in with no provider, for local work, as the user
  `CLIMB_DEV_LOGIN` names.** Setting the variable enables the dev login, and
  two guards keep it off a deployed engine.
- **The app refuses to start with the flag beside a provider's client.** A
  deployed engine signs its users in through a provider, so it carries one.
- **The dev login answers only a request that arrived at a loopback address.**
  Another machine's request never does, however the server is bound. The app
  cannot check the bound address at start, since it is built before the server
  binds one.

## The hosted log

- **The hosted engine starts with an empty log, the author's included.** The
  author's account is linked to a user minted at its first sign-in, as every
  account is.
- **The records written before hosting stay in the local database**, under the
  ids the terminal and the local API wrote them under. The dev login signs in as
  the user `CLIMB_DEV_LOGIN` names, and the terminal reads that user's log
  by default.
- **No record is copied from the local log to the hosted one.** The local log
  held a handful of sittings and attempts when hosting was decided. Carrying
  them over would take a copy of the log and an account linked to an id the
  engine never minted, for records nothing reads.

## Deleting an account

- **Deleting the account erases the log, then deletes the user in the same
  transaction.** The user's identities, sessions, app codes and app tokens go
  with it, and so do the invitations of the identities' emails. The user asked
  to leave, so no email of theirs stays stored. Signing in again is a new
  sign-up under the pace, and mints a new user.
- **The engine deletes an account no session or app token has signed a
  request in for 12 months, as the user's own deletion does.** Open sign-up
  leaves accounts nobody returns to, each holding an email and a log. Short
  of that period the record is kept, since the board and the schedule read
  it. An account holding an invitation is never deleted this way. The privacy
  policy states this period, the backups' 30 days and the logs' 14 days.
- **The deletion asks for the account's name typed back, and the engine checks
  it.** The name is the one the account menu shows: the verified email, or the
  user id where no provider linked one. The client signs out after the
  deletion without sending its outbox, since the outbox belongs to the deleted
  log.
