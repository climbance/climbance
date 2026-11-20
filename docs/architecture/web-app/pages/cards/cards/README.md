# The cards

The page at `/cards`, the root of Cards, and the phone's Cards tab: where each
card stands, read by its depth in the card graph.

[`cards.md`](cards.md) draws the page at low fidelity.

- **The cards list reads the card graph by depth.** The roots come first, and
  each depth is a section under its own heading. A row names its card's
  technique, its card state, and the required cards a locked card waits on. A
  reader then sees where to start and what each card opens.
- **A started card's row names the next spaced check or recall it waits
  for.** A consolidating or lapsed card names the earliest check of its
  templates, and a graduated card names its earliest due recall. The check is
  read against now, as opening, open or owed, so the row says when to come
  back.
- **The web draws the edges between the rows, and the phone names them on
  each row.** A drawn graph needs a page's width, and the phone's screen holds
  one column. The two clients read the same depths, the same rows and the
  same locks, as `../../../../core-package/screens.md` requires.
- **The web below 640px draws no edges either.** The edges' gutter would take
  a third of a row there. Each row names the required cards it waits on, as
  the phone's row does.
