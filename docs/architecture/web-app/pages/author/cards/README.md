# The cards page

The page at `/author/cards`, in the author area: every card at once, each
opened with its templates revealed. `../README.md` gives who reaches it, and
`../browser.md` gives the grid and the dialog this page shares with the other
browser pages. `../../../../content-repo/cards.md` gives the card.

[`cards.md`](cards.md) draws the page at low fidelity.

- **The rows are read from `/api/author/cards`, and an opened card from
  `/api/author/cards/:slug`**, over the seeded card tables and the corpus of
  the engine serving the page. A row carries the counts the grid shows, and
  no card text, template code or rung. The learner's card routes read one
  user's card state, and a card in review has no state.
- **The rows read in the card graph's order by default**: by depth, then by
  title. A card then reads after every card it requires.
- **The page filters by primary module and by depth**, as `?module=` and
  `?depth=`, combined as the problem listing's filters are. The URL carries
  both.
- **A row's columns are the card's slug, its title, its technique, its primary
  module, its depth, its templates by core and optional, its ladder's rungs
  against the selector's `size`, and its gaps.** A gap is a core template no
  solution displays, so a row with a gap names the template the next
  generation run needs. The depth, the rungs and the gaps sort on a press of
  their header.
- **The dialog draws the card with the learner's card component**: the
  trigger, the brief, and every template with its trigger, its code shown and
  its notes. The author reviews every form at once, so no template waits for a
  reveal.
  The template panel draws no recall press there, since a recall writes a
  log record and the browser only reads.
- **The dialog names the subtopics paired with the card**, as the card page
  does: every subtopic naming the card's technique, the primary module's
  first. The pairing is read from the snapshot, as
  `../../../../content-repo/cards-and-subtopics.md` gives it.
- **Each template names its counts**: its cases, its served judgement items
  and its served key-line items. A template with none of a kind is named, since
  `climb judge build` and `climb fill build` build them. Each template links to
  the problems page filtered to the problems written for it.
- **The dialog names the card's requirements and the cards requiring it.**
  Each edge names the required card, its template and the template that uses
  the form, as links to those cards' dialogs. The author then checks each edge
  against the two forms it joins.
- **The dialog lists the ladder as the corpus derives it now**, each rung
  with the templates it covers, its standing difficulty, and whether it is
  required. A rung links to the problem's dialog on the problems page. The
  ladder of a user's open run can differ, since a run keeps its rungs, and the
  page derives the ladder with no run.
