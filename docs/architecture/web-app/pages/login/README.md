# The login

The page at `/login` and the phone's Login screen, under no section and open
without a session. `../../../README.md` `## Boundaries` gives the sign-in flow.

- **The login page and the privacy policy carry no navigation.** The two pages
  open without a session, and every section behind the menu answers 401 to a
  request carrying none. The policy names the login as its way back, since the
  login is the page it is reached from.
- **A refused sign-in returns to the login page as a code.** The callback is a
  navigation from the provider's site, so a refusal answers with the page that
  explains it. `?refused=` carries a code rather than a sentence, since a
  sentence names the address that was refused and a URL is kept in the
  browser's history.
