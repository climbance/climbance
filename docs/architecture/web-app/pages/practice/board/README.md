# The board

The page at `/`, the root of Practice, and the phone's Practice tab. The board
is the overview of the user's practice, and serves the scheduler's pick.

[`before-the-first-act.md`](before-the-first-act.md) and [`board.md`](board.md)
draw the page's screens at low fidelity.

## Landing

- **A signed-in user lands on the board, on both clients.** Every sitting
  starts from a technique the user picks there, Continue starts the next
  queue there, and the scheduler's pick is served on the same page.
- **The phone opens on the Practice tab, as the web opens on the board.** The
  board's knowledge part serves from the phone's own copy, so the first page
  works without a connection.
- **The board opens with a panel linking the guide while the user's log
  holds no act**, on both clients. An act is an attempt, a sitting, a recall
  attempt, a card run, a judgement, a fill, an answer or a lesson marked
  read. The panel is derived from the log, and nothing stores a dismissal.
  The first act therefore removes the panel on every client the act's record
  reaches.

## The pick and the cards

- **The board serves the pick above its lists, on both clients.** The pick
  is one row under its own heading, naming the form, the problem or the card,
  and the act it opens. `../../../../api/pick.md` gives what it
  offers. A user who declines it picks from the lists below, which keep their
  order, and a technique with no template keeps the staleness order.
- **The board names the cards in progress before the techniques.** A card in
  progress is one
  acquiring or consolidating: a study the user declared and has not finished.
  Ranking techniques by staleness alone can bury such a card. A graduated card
  keeps its run open and is not in progress, since a graduated card is done.
  Each card in progress reads as its row on the cards list does, and opens the
  card.
- **The board then names the unlocked cards not yet started**, by depth, the
  shallowest first. A user with nothing in progress then reads the next study
  the card graph offers, rather than a list of every technique. It names five
  at most, and a link to the cards list counts the rest, so the board stays one
  glance with a dozen roots open.
  - The list leaves out the card the pick names. On a new account the pick
    offers the first card to start, and the board would otherwise name that
    card twice.

## The knowledge study

- **The board is the overview of the user's practice.** It reads the
  knowledge study first: the focus, Continue and the modules. The cards in
  progress and the techniques follow. A user reads every study they declared
  on one page before picking what to practise.
- **The knowledge part reads from the device's copy**, ahead of the engine's
  answer and without it. The board then works offline as the knowledge home
  does, and a phone opened on a train shows a page that works.
- **The board holds the focus as a reading, with Continue inside its
  panel.** The board names several studies, so a press in the page's bottom
  bar would not say which of them it continues. Continue serves the focus,
  so it sits in the focus's panel, or in a panel of its own where no focus
  is aimed. The panel leaves out the counts line the focus already reads.
- **The focus's other presses stay on the knowledge home**: Strict, Clear and
  the raise. The focus's panel on the board opens the home. Exam stays there
  too, as the home's second way in. A press living on two pages drifts
  apart.
- **Each module on the board reads as its row on the knowledge home**, and
  opens the module, whose way back then names the board. The board offers no
  order press, since ordering the modules belongs to the knowledge home.

## The techniques

- **The board's two technique lists close from their headings, on both
  clients**, as `../../../areas.md` gives for a section. A user who
  has practised many techniques closes the list of untouched ones to reach the
  practised ones.
- **A technique's row on the board reads its knowledge beside its attempts**,
  as the questions passed over the questions held, across every subtopic
  naming the technique or a code narrower than it. A row with no such question
  reads no knowledge. A technique whose questions the user answered is
  practised, though no sitting reached it. The count is read from the
  device's copy, as the board's knowledge part is.
- **Every technique on the board opens the technique's page, whatever number
  of cards teach the technique.** A row opening a card where one card teaches
  the technique would make one press land on two kinds of screen.
