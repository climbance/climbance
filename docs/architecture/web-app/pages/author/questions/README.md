# The questions page

The page at `/author/questions`, in the author area: one module's questions at
once, each drawn as a learner reads it once answered. `../README.md` gives who
reaches it, and `../browser.md` gives the grid and the dialog this page shares
with the lessons, the cards and the problems pages.

[`questions.md`](questions.md) draws the page at low fidelity.

## Where it reads from

- **The questions are read from the snapshot**, the document the web app
  already keeps for the knowledge pages. The snapshot is built from the seeded
  store of the engine serving the page, so the hosted engine shows prod's bank
  and `just app` shows the local one. A second read of the same questions in
  another shape would let the browser show a question the queue draws
  differently.
- **The snapshot holds the live questions alone.** A retired question is never
  served, so the browser shows the bank a learner can meet. Listing retired
  questions is deferred until the author asks for one the seed retired.
- **An opened question's concept is read from
  `/api/author/concepts/:module/:slug`**, one concept at a time. The seed
  stores each concept of a module written by concept, as
  `../../../../cli/seed.md` gives. The snapshot carries no concept, since no
  learner reads one, and a phone would download every claim for nothing.

## Filters

- **The page reads one module at a time**, named by `?module=`. With no
  module named, the page opens the first module in the snapshot's order. A
  module's bank is the unit the author reviews, and one module's questions
  already run to hundreds.
- **The filters narrow by topic, subtopic, level, kind and format**, as
  `?topic=`, `?sub=`, `?level=`, `?kind=` and `?format=`. The kinds offered are
  the module's own vocabulary, such as `output` in `algo`. Every `algo`
  `output` question is then one link: `?module=algo&kind=output`.
- **The URL carries every filter**, so a filtered bank is a link the author
  can keep and send. A filter naming content the snapshot does not hold
  degrades as a filtered queue's choice does: an unknown subtopic keeps its
  topic.

## The grid

- **A row's columns are the question's slug, its subtopic, its level, its
  kind, its format, the first line of its prompt, and the length of its code
  in lines** where it carries code. The author scans a bank for a broken rule,
  such as a long hand trace, and the code's column shows one without opening
  the question.
- **The rows read in the bank's order by default**: by topic, subtopic, level,
  then the question's position. The level, the kind, the format and the code's
  length sort on a press of their header.

## The dialog

- **The dialog draws the question with the queue's own component, as
  answered.** It shows the prompt, the code, every choice with the correct ones
  marked, each choice's reason, and each wrong choice's misconception. It then
  shows the explanation and the detail opened. The author then reviews the
  exact text and layout a learner reads.
- **An open question shows its key and its traps**, with each point's detail
  where the question carries one. A `short` question shows every accepted
  reply, and whether case counts.
- **Under the question, the dialog names its concept**: the concept's slug,
  claim, level and source. A question written from the concept tests the claim,
  so the author checks the two side by side. A question of a module not
  written by concept shows no concept.
- **The dialog names the lessons teaching the question**, each a link to that
  lesson's dialog on the lessons page.
