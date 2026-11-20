# Client terms

Words this project gives its own meaning for the two clients and their pages.
Every file in `docs/architecture/` uses them without redefining them.

## The native app

- **Native app**: the engine's client on a phone, built from one codebase for
  Android and iOS. It runs the knowledge module's rules from `packages/core`,
  as the web app does, and starts without a connection, which the web app
  cannot.

## The pages

- **Section**: one of the four destinations both clients' navigation names:
  Practice, Problems, Cards and Knowledge. Every page sits under one of them
  or under neither.
- **Guide**: the page saying what each kind of practice trains and where a
  new user starts, linked from the board while the user's log holds no act.
- **Gallery**: the page showing every design token and every component the
  pages use, built in development alone.
