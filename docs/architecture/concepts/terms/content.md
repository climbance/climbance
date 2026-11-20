# Content terms

Words this project gives its own meaning for techniques, cards, templates and
the card graph. Every file in `docs/architecture/` uses them without redefining
them.

## Techniques

- **Technique**: one entry in the vocabulary of skills the log references. A
  procedure, a structure, a paradigm or a problem class. Shipped as code.
- **Vocabulary**: every technique, each with the criterion for claiming it.
- **Parent**: a technique another technique is a kind of, named on the
  narrower one's entry. `dynamic-programming` is the parent of `knapsack`.

## Cards and templates

- **Card**: the study material for one technique: what to read, the
  templates to reproduce from memory, and a selector for problems to solve.
- **Primary module**: the module a card names in `module`, whose subtopics
  support the card. Another module's subtopic naming the card's technique
  adds to the card and leaves the support unchanged.
- **Template**: one form of a technique, authored on a card, that a user
  reproduces from memory. Core by default.
- **Trigger**: the field on a card or a template saying when to reach for the
  technique or the form. A drawn recall shows the trigger alone, and
  withholds the form's title.
- **Speedup**: a flag on a template saying its form is asymptotically faster
  than the naive approach the technique replaces, by at least a factor of
  log n.
- **Selector**: a technique plus filters, on a card. The ladder is derived
  from it.
- **Ladder**: the problems a card has the user solve, derived from template
  matches and the selector. Never stored.
- **Rung**: one problem on a ladder. Required when it covers a core template.
- **Probe**: a problem assigned when a card is started, testing whether the
  form transfers to a problem it was not studied on. Never drawn from the
  ladder.

## The card graph

- **Card graph**: the cards as a directed acyclic graph, each edge from a card
  to a card it requires. Orders study, and gates card runs alone.
- **Requirement**: an edge of the card graph, authored on the requiring card.
  It names the required card, a core template there, and the template here
  that uses that form.
- **Root card**: a card requiring no other card.
- **Depth**: the longest chain of requirements below a card. Zero on a root.
- **Met**: a required card whose ladder the user solved, or one of whose
  run's probes the user solved. Never stored.
- **Locked**: a card some required card of which the user has not met. Its
  run does not start.

## Template matches

- **Template match**: a record saying one solution displays one template.
  Written by the generator, the matcher or by hand.
- **Matcher**: the model call reading a canonical beside its statement and
  naming the templates it displays.
- **User record**: a claim or match written by the user rather than a model. Its
  `source` is `user`. It is written by hand: in the drill loop, or in a
  `--by-hand` pass over what the loop never asked. It stands over every
  machine record on the same question.
