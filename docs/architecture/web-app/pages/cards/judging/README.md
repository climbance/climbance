# Judging a solution

The page at `/judge` and the phone's Judge screen: the first short exercise,
served at a phone's width on both clients. `../../../../api/short-exercises.md`
gives the exercise and `../../../../cli/exercise-items.md` the items.

- **The page opens from the board and from a card.** The board's press serves
  the forms of the cards the user started first, as
  `../../../../api/short-exercises.md` gives. A card's press adds `?card=`,
  and the page serves that card's forms alone.
- **The item reads as its template's title, one of its cases and the code.**
  The header names the card under the title. A template's title names the
  form in words, since a new user reads it before the card.
  The case is the spec: `solve([3, 9, 4])` returns `9`. A statement would be a
  second text to read for a question the case already asks.
- **The item shows no depth.** A card's depth in the card graph orders the
  cards list, and beside one form it tells a new user nothing.
- **Each line of the code is numbered, and the whole line is the tap
  target.** A tap on a wrapped line lands on the line it wraps from.
- **The answer is two presses, Clean or Flawed.** Flawed then asks for the
  wrong line, and a tap and Submit send it. The page sends nothing before the
  user answers, so the item carries no answer the page could show early.
- **The engine decides the answer, and the page shows the decision.** The
  result reads as right, located, spotted on the wrong line, missed, or a
  false alarm. The flawed line is marked, and the separating case shows its
  arguments, the expected value and what the flawed code gave.
- **Next serves the following item**, drawn as
  `../../../../api/short-exercises.md` gives.
