# Shared core

The web and the native app import one TypeScript package, `packages/core`, and
each keeps a look of its own. The two apps are ways into one learner model, and
each feature sits on the platforms where it works.

## Three layers

- **Three layers divide the code.** The rules live in the core, as one copy. A
  screen's labels, counts and offered acts live in the core too, tested once.
  The look and the interaction belong to each platform.
- **A platform may change how a thing looks and how it is used, and never what
  it computes, says or offers.** A difference in what two platforms say is a
  bug, and a difference in how they look is a choice.
- **The knowledge queues are scheduled on the device by the core, on the web
  and the phone alike.** The phone must work offline, and one user practising
  on both has to see one behaviour.
- **The server schedules what depends on the server already: the pick of a
  sitting or a recall, mastery, the stored predictions and any reminder sent
  while the app is closed.** FSRS replay and the question states therefore
  exist in TypeScript and in Python, held together by the shared fixtures.

## The fixtures

- **The Python side generates the fixtures, and both suites check them.** A
  fixture is regenerated from the Python side, never edited by hand, so a rule
  changed in one copy fails the other copy's tests.
- **`just fixtures` generates the cases of the rules Python holds: FSRS replay
  and the question states.** A rule only TypeScript holds, such as gating or a
  queue, keeps the cases generated before the merge until a server feature
  reads that rule.
- **A rule changes in `knowledge/` first, then in both copies.**
  The doc is the contract the fixtures are generated against.

## Rejected

- **The web app wrapped in a WebView, as Capacitor ships one, was rejected.**
  Every screen would then scroll, type and navigate through a WebView, where a
  native screen gets the platform's own lists, sheets and back gesture.
- **A native rewrite in Kotlin and Swift was rejected.** Every rule and every
  screen would exist three times, and each copy would need testing on a device.
