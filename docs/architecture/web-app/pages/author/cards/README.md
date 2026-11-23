# The cards page

The page at `/author/cards`, in the author area: every card at once, each
opened with its templates revealed. `../README.md` gives who reaches it, and
`## The content browser` there gives the rules this page shares with the other
browser pages. `../../../../content-repo/cards.md` gives the card.

[`cards.md`](cards.md) draws the page at low fidelity.

- **The cards are read from `/api/author/cards`**, over the seeded card tables
  and the corpus of the engine serving the page. The learner's card routes
  read one user's card state, and a card in review has no state.
- **The cards read in the card graph's order**: by depth, then by title. A
  card then reads after every card it requires.
- **The page filters by primary module and by depth**, as `?module=` and
  `?depth=`, combined as the problem listing's filters are. The URL carries
  both.
- **A row shows the card before it is opened**: its slug, its title, its
  technique, its primary module and its depth. Then it shows its templates by
  core and optional, its ladder's rungs against the selector's `size`, and its
  gaps. A gap is a core template no solution displays, so a row with a gap
  names the template the next generation run needs.
- **An opened row draws the card with the learner's card component**: the
  trigger, the brief, and every template with its trigger, its code shown and
  its notes. The author reviews every form at once, so no template waits for a
  reveal.
- **Each template names its counts**: its cases, its served judgement items
  and its served key-line items. A template with none of a kind is named, since
  `climb judge build` and `climb fill build` build them.
- **An opened row names the card's requirements and the cards requiring
  it.** Each edge names the required card, its template and the template that
  uses the form, as links to those cards' rows. The author then checks each
  edge against the two forms it joins.
- **An opened row lists the ladder as the corpus derives it now**, each rung
  with the templates it covers, its standing difficulty, and whether it is
  required. A rung links to the problem's row on the problems page. The
  ladder of a user's open run can differ, since a run keeps its rungs, and the
  page derives the ladder with no run.
