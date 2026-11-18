# The card graph

The cards form a directed acyclic graph. An edge from one card to another says
the first card requires the second. The graph orders study, so a new user
starts at the roots and an experienced user sees where a card sits.

- **A card names the cards it requires, as requirements on the card.** Each
  requirement names the required card's slug, a core template of that card,
  and the template on this card that uses the form. Kruskal's template on the
  `union-find` card uses the disjoint set, so that card requires the card
  teaching the disjoint set.
- **A requirement needs a template that uses another card's form.** An edge
  drawn because one topic is usually taught first carries no fact a reader can
  check. The named pair of templates is the fact, and a reviewer reads the
  two forms side by side to confirm it.
- **A requirement is not a parent.** A parent says one technique is a kind of
  another, between codes. A requirement says one card's form is used inside
  another card's, between cards. Kruskal is no kind of disjoint set, and a
  reader taking one relation for the other draws the wrong edges.
- **The graph is content, authored on the cards and seeded with them.** A
  requirement stores the required card's slug, held by a foreign key to the
  stored card, and the template's slug, resolved on each check. Editing the
  graph then needs no migration, and a re-seed refreshes the edges as it
  refreshes the templates.
- **The seed refuses a cycle, an unknown slug or a requirement naming an
  optional template.** A cycle locks every card on it for every user. An
  optional template is outside the study set, so a card requiring it would
  wait on a form the required card never asks for.
- **A root card requires nothing.** The roots teach the basic forms, such as
  hashing, two pointers and a prefix sum. The easy problems sit on the roots,
  since a basic form applied unchanged is easy by the criteria in
  `../corpus.md`.
- **A card's depth is the longest chain of requirements below the card.** The
  pages lay the graph out by depth, and the board orders the cards it offers by
  depth. Depth is derived from the graph on every read, never stored.
- **The graph gates card runs alone.** A locked card is read in full, and its
  problems are offered from the board as any technique's are. A sitting never
  waits on the graph, since the graph orders study rather than proving what
  the user may solve.
