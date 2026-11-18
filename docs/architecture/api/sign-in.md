# Sign-in

The engine's user, whose id every private record carries. The providers, the
identities, the sessions and the invitations are still in `../README.md` `##
Boundaries`, under "Google and GitHub hold each identity and its login", until
`split-readme-doc` moves them here.

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
  to leave, so no email of theirs stays stored. Signing in again needs a new
  invitation, and mints a new user.
- **The record and the account are kept until the user deletes the account.**
  The engine expires neither by itself, since the board and the schedule read
  the record. A rule deleting an account left unused is deferred until
  access is opened beyond invitations. The privacy policy states this period,
  the backups' 30 days and the logs' 14 days.
- **The deletion asks for the account's name typed back, and the engine checks
  it.** The name is the one the account menu shows: the verified email, or the
  user id where no provider linked one. The client signs out after the
  deletion without sending its outbox, since the outbox belongs to the deleted
  log.
