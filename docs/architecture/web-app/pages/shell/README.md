# The shell

The parts every signed-in page sits in: the navigation, the account menu, the
signed-in devices and the error screen that replaces a page that threw.

[`frame.md`](frame.md) draws the navigation and the header at low fidelity, and
[`readings.md`](readings.md) draws a page loading, failed and empty.

## The navigation

- **The navigation names four sections: Practice, Problems, Cards and
  Knowledge.** `../../README.md` `## The structure` gives the tree both
  clients hold. Practice holds the board, a technique's candidates, a picked
  problem and the sitting. Problems holds the listing of every problem. Cards
  holds the card list, one card, and the recall trainer. Knowledge holds the
  knowledge modules of `../../../core-package/knowledge/`: their queues, their
  lessons and their certifications.
- **The scheme switch and the account menu sit at the right of the
  navigation**, apart from the sections, since neither names a page.
- **At phone width the wordmark reads as its flame dot alone, and the
  sections scroll sideways.** Four sections need more width than a phone
  holds beside the switch and the menu. The row scrolls to the marked
  section, so the reader always sees where they are.
- **A section is marked while the user is on a page under it.** A technique and
  a picked problem are steps down from the board, so the board's own section
  stays marked on both.
- **Problems is marked on the listing alone.** A picked problem is a step down
  from the board, from a technique or from a card, so Practice stays marked on
  it and the way back names where the pick came from.

## The account menu

- **The account menu names who the session signs in as**, and holds the
  link to the settings, the signed-in devices and the sign-out. The address the
  provider verified names the user, with the engine's own id under it. A user
  no provider linked is named by that id instead, since the dev login mints
  no identity to carry an address.
- **The account menu links the guide**, on both clients, so a user can
  reread it once the board's panel is gone. `../practice/guide/README.md`
  gives the guide.

## The signed-in devices

- **Signed-in devices open from the account menu**, as a dialog on the web
  and a screen on the phone. The list names every browser and app signed in
  as the account, by its name and when it was last used, with a press to
  revoke it. A lost phone or a browser left signed in
  elsewhere is cut off there, where its own sign-out cannot reach.
- **The list names the device it is read on**, on both clients, and that row
  signs out rather than revoking. Signing out sends the outbox first, and a
  bare revoke would leave the outbox unsent.
- **A browser is named by its agent's browser and system**, such as Chrome
  on macOS. An app is named by the device name it signed in with.

## The error screen

- **A screen that throws is replaced by an error screen**, on both clients.
  The screen says the error was reported, and offers Reload and Send
  feedback. Without it a throw in one screen leaves a blank page, and the user
  cannot tell a fault from a page still loading.
