# A technique

The page at `/techniques/:technique` and the phone's Technique screen: a
technique's cards and the problems a user picks from. The board opens it, as
`../board/README.md` gives.

- **A technique's page lists its cards, then its problems, on both clients.**
  The cards are those teaching the technique or a narrower one, each as its
  row on the cards list reads. A row carries the card's progress and its
  recall, where a link carries the title alone.
- **A technique no card teaches lists its problems alone.** The board lists
  every technique a served problem carries, and a technique can carry
  problems before any card teaches it.
- **A problem's row on the Technique screen opens the phone's Problem
  screen.** The screen reads the problem's record: its title, difficulty,
  techniques, the counts the user reached on it, and its cards, then the
  statement. Serving the statement mints nothing, so the phone reads a problem
  as the web does.
