# App tokens

How the native app signs in, and the token it holds afterwards. A native client
cannot carry the pages' cookie, so the provider flow `sign-in.md` gives ends in
a token for the app instead.

## The flow

- **The native app signs in through the same provider flow, opened in a browser
  sheet inside the app.** A native client cannot carry the pages' cookie, so
  the flow ends in a token for the app instead.
- **The app marks the flow as its own when it starts, and sends a PKCE
  challenge.** The callback then redirects to the app's own URL scheme with a
  one-time code, rather than setting the cookie.
- **The app exchanges that code and its PKCE verifier for the token.** Another
  app claiming the same URL scheme can receive the code, and without the
  verifier it cannot redeem it.
- **The providers see only the engine's own callback, as they do for the
  pages.** Supporting the app adds no redirect address to a provider's console.
- **The invitation gate, the email check and the linking of identities run
  unchanged, since the app's flow passes the same callback.**

## The token

- **An app token is stored as its hash, like a session.** A copy of the table
  then signs no app in.
- **An app token reaches every endpoint a session reaches, the account's
  included.** The engine is meant to work from the phone alone, with no web at
  all, so the app needs everything the pages need.
- **A token taken from a lost phone then reaches the whole account until it is
  revoked, and that is accepted.** The engine holds a user's practice records,
  and no money and no credential.
- **Scoping a token to some endpoints is deferred until the engine holds data
  worth scoping it for, such as a payment or access beyond invitations.** A
  scope is then one field on the token, checked where the token is read.
- **An app token expires after 90 days unused, and each use extends it.** The
  app works offline for days, and a fixed lifetime would sign it out on a trip.
- **The app sends its token in the `Authorization` header, never as a cookie.**
  A browser attaches no header to a request another site forges, so the token
  needs no guard against forgery.
- **The app keeps its token in the phone's secure storage, the Keystore on
  Android and the Keychain on iOS.**

## The dev build

- **The dev build of the app syncs with a local engine, never with a deployed
  one.** Its test answers would otherwise land in the author's own log.
- **The dev build has a URL scheme of its own, `climbancedev://`.** With one
  scheme for both builds, Android could hand the dev build's code to the
  release build on the same phone.
- **The dev build signs in through the dev login, which issues the same
  one-time code to the dev build's scheme.** The dev login still answers on
  loopback alone, and it issues no code to the release build.
