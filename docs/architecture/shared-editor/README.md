# Shared editor

`packages/editor` holds the CodeMirror setup for editing Python, and both
clients import it. The web app builds its editor from the package directly.
The native app bundles the package into the page its one WebView shows, as
`../native-app/README.md` gives.

- **The package fixes how Python is edited: highlighting, indentation and
  paired brackets.** A client adds its own keymap and its own look. One setup
  keeps a sitting typed on the phone behaving as one typed on the web.
- **The editor proposes no name from the standard library.**
  `../flows/drill-loop.md` gives the reason.
- **The native app alone imports the keys, the names and the narrowing.** The
  keys and the names serve the app's own keyboard, and the narrowing fits a
  line to a phone's width. `../client-modules.md` draws which client reaches
  each file.
