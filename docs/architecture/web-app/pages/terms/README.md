# The terms of use

The page at `/terms` and the phone's Terms screen, under no section and open
without a session. The terms carry no navigation and name the login as their
way back, as the privacy policy does in `../privacy/README.md`.

[`terms.md`](terms.md) draws the page at low fidelity.

- **The terms of use are one text in `packages/core`, read on both
  clients.** The web serves the terms at `/terms`, and a person signing in
  accepts them. The phone holds the terms as a screen, so they read before any
  sign-in and with no connection.
- **The terms link no page of the app.** The phone's prose renderer opens a
  link with the system, which cannot open a screen of the app. The terms
  name the privacy policy in words, and the login links both.
