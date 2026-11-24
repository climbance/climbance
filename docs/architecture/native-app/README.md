# Native app

The native app schedules the knowledge queues offline. It runs the knowledge
module's rules from `packages/core`, and syncs with the engine through the API.

- **The app answers questions with no network.** A queue picks each question at
  the moment it is needed, so a round trip per pick would stall practice on a
  train or a plane.
- **The app served the knowledge modules first, and the rest of the engine
  followed feature by feature.** The phone now holds every page but the
  gallery, and `../core-package/screens.md` lists what each client holds.
- **The app runs on Android first, and iOS follows from the same code.** It is
  installed directly from a build signed by a key kept out of git. A store
  release is deferred until someone other than the author installs it.
- **A tab out of view is frozen, and renders the store's latest value when it
  is back in view.** Every record rebuilt the board on every mounted screen,
  so only the tab in view renders. React drops a context change made while
  the tab is frozen. `ui/frozen.tsx` therefore provides the store again below
  the freeze, from a value read outside it. Without that, the Practice tab
  kept a focus set on a module's page. Continue then served every module
  instead of the focus, as the prod rehearsal of 2026-11-24 found.

## Typing code

- **A sitting and a recall are typed on both clients.** The phone types them
  through a keyboard of the app's own, since the system keyboard hides the
  symbols code is made of and completes words. `../core-package/screens.md`
  lists what each client holds.
- **The phone's code editor is the one WebView, inside a native screen:
  CodeMirror, typed through the app's own keyboard.** One editor setup then
  serves both clients. The system keyboard is the part of a WebView that
  handles worst, and the app's keyboard replaces it.
- **A key reaches CodeMirror as typed input, after a forced parse.** CodeMirror
  reindents `else:` only on a transaction marked `input.type`, and reads a
  syntax tree its parser fills in idle time. Without both, `else:` kept the
  indentation of the line above it.
- **Enter after `else:` indents to the level of `else` rather than of its
  body.** Node reproduces it with the same packages, so the web's editor does
  the same, and the dedent and indent keys correct it on the phone.

## The editor's measurements

- **A key reached the painted editor in 23 ms at the median.** On 2026-11-11 a
  nine-line binary search was typed through the app's keys on a Redmi Note 13
  Pro 5G at 120 Hz. Over 126 keys, the time from the press to the second
  animation frame after CodeMirror applied the key was 23 ms at p50, 27 ms at
  p90 and 48 ms at most. The message across the bridge took 6 ms of it.
- **The editor scrolled as a native list does.** Over the same flings and
  drags, the editor and the native Problems list each missed one frame deadline
  in about 4,000 frames. The editor's frames took longer: 11 ms against 9 ms at
  p50, and 19 ms against 14 ms at p99.
