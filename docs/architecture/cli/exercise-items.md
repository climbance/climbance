# Exercise items

The judgement items and the key-line items, built by `climb judge` and `climb
fill` from the seeded templates and their mutants. The two kinds of item are
product data, which the short exercises serve. `../api/short-exercises.md`
gives the exercises and their answers.

## Judgement items

The solutions a judging exercise serves.

- **An item is one template's form, clean or carrying one mutant.** The
  question it answers is the one the template's cases ask, so the user knows
  what the code must do without a statement.
- **A flawed item's mutant fails at least one of the template's cases.** A
  mutant every case passes may be equivalent to the form, and calling it
  flawed would teach a fault that does not exist. `card check` already
  separates the two.
- **An item stores the code it shows, its mutant's line and change, and the
  separating case** with the value the mutant returned. The template's code
  can change after the item was built, and an answer has to stay readable
  against what the user saw.
- **An item is product data, minted when the items are built, and never
  edited.** A build appends items for templates not yet covered. A template
  whose code changed has its old items retired, as a problem is retired, so
  no answer loses its item.
- **About a quarter of the items are clean, and never fewer.** With no clean
  item, calling everything flawed would be right every time, and a false
  alarm could not be counted. A template with few flawed lines raises the
  clean share, as the bullet below gives.
- **An item shows the form without its comments and without its harness.** A
  comment can state the very invariant the flaw breaks. The harness is the
  code turning JSON into nodes and back, which a template names in `harness`,
  and a flaw there is no flaw in the form the user studies.
- **An item's lines fit 60 characters**, the width the modules hold code to.
  A phone fits some forty, so a longer line wraps once under its indent and
  never scrolls sideways where a tap has to land. A form wider than 60 yields
  no item.
- **A template yields one clean item and up to three flawed ones**, the flaws
  on different lines. Three flawed lines make the quarter of clean items. A
  template with one or two flawed lines still yields its items, a half or a
  third of them clean, since dropping the template would lose its practice.
- **A mutant on the harness never makes an item.** The user never sees the
  harness, so a flaw there could be neither read nor tapped.
- **A mutant that only slows the form never makes an item.** A timeout is a
  fact about the machine, and reading the code cannot find it.

## Key-line items

The forms the key-line exercise serves, each with one statement blanked. A
key-line item is built from the same mutants a judgement item is, under the
same rules for comments, the harness, the width and timeouts.

- **An item is one template's form with one statement blanked, and three or
  four choices for that statement.** One choice is the statement as the form
  writes it. Each other choice is the statement as one mutant writes it.
- **A blank covers a whole statement, every line of it.** A statement is one
  logical line of Python, so a long `if` condition wrapped over two lines is
  one statement. Blanking only the first of those lines makes every choice read
  as an unclosed bracket, such as `if (c in cols or r - c in diag1`. The
  mutants of either line are choices for the one blank.
- **An item blanking part of a statement is retired at the next build**, and
  its template is built again. Items built before blanks covered whole
  statements carry that shape.
- **Each choice is run against the template's cases when the item is built.**
  The form's own statement passes every case, and each other choice fails at
  least one. A mutant every case passes may be equivalent to the form, so a
  choice built from it could be a second right answer.
- **A wrong choice stores its separating case** and the value it returned
  there, as a flawed judgement item does. The case is the evidence shown after
  the fill.
- **A statement is blanked where at least two mutants that change one of its
  lines alone fail a case.** A statement with one such mutant gives a choice
  between two, which a guess answers half the time. Two mutants writing the
  same text are one choice.
- **The blanked statement is found by its mutants, and its role is not
  stored.** The lines that carry the invariant, the update and the edge case
  are the ones mutants of a condition, an index and a bound reach. A role read
  off the syntax tree is deferred until a fill shows that the mutants' lines
  miss the form's key line.
- **A template yields up to three items, each blanking a different
  statement**,
  spread over the form as the flawed judgement items are.
- **A choice shows the statement without the indent of its first line.** The
  blank keeps that indent, so the choices differ only in what the statement
  computes. A wrapped line keeps its indent relative to the first.
- **An item is product data, minted when the items are built, and never
  edited.** A template whose code changed has its old items retired, as a
  judgement item is.
