# Cards and subtopics

A card and a subtopic of the algorithms module teach one technique together.
The card says when to reach for the technique and how its forms are written.
The subtopic says why the forms are correct and what they cost.

## The pairing

- **A card and a subtopic are paired by technique code alone.** A card names
  one code, and a subtopic names any number, as `../knowledge.md` `## Modules`
  gives. A card is paired with every subtopic naming its code. The board's
  three readings key on the same code, so a pairing needs no field of its own.
- **A card names its primary module, in `module`.** The primary module's
  subtopics support the card: they hold the facts the card's forms rest on. An
  algorithms card names `algo`, the algorithms module, and a card on a
  language's idioms would name that language's module. A card names a module
  by slug, the module's directory name, and the pages show the module's title.
  The card seed refuses a card whose `module` names no seeded module, so a
  module is seeded before the cards naming it. Such a card would be paired
  with no subtopic.
- **Another module's subtopic adds to a card and never supports it.** Its
  answers still count toward the technique's knowledge reading, and its link
  still shows on the card's page. A `py` subtopic naming `heap` would
  otherwise hide the gap where the algorithms module has no heap subtopic.
- **Every card's technique gets a subtopic in the card's primary module, and a
  subtopic may have no card.** Amortized analysis and recursion are facts with
  no ladder of their own, so the module holds subtopics naming no card's
  technique. Two cards teaching
  one technique are each paired with every subtopic naming it, and one
  technique's facts may span several subtopics: `dp-1d-linear` and
  `dp-state-design` both name `dynamic-programming`.
- **`module check` lists each card naming the module as primary whose
  technique none of the module's subtopics names.** The list reports work
  still to write and refuses nothing, since a card is studied in full without
  its subtopic.
- **A card and its subtopic gate each other in nothing.** A card run never
  waits on a subtopic, and a subtopic's questions never wait on a met card.
  Mastery reads knowledge and execution apart, so a gate between the two
  would hold one reading back until the other moved.
- **A card's page links to every subtopic paired with the card, the primary
  module's first, and each lesson of a subtopic links to every card paired
  with the subtopic.** The primary module's subtopics support the card, and
  the rest add to it.
- **A template may cite subtopics of another module, in `cites`.** Each entry
  names a subtopic as `<module>/<topic>/<subtopic>`, such as
  `py/stdlib/collections`, and the card's page links each one. A citation
  gates nothing, since gating runs inside one module. The seed refuses a
  citation naming no seeded subtopic, so a module is seeded before the cards
  citing it.

## What each one holds

- **The card holds the trigger, the brief's core idea and decision axes, the
  templates and the ladder.** A solver reads these before a sitting and
  during one.
- **The subtopic holds the facts: invariants, complexity, pitfalls and edge
  cases.** Each fact is a concept with a witness, as
  `docs/authoring/concepts.md` gives. A fact lives in one place, so a brief
  and a lesson never restate each other.
- **A brief loses its `## Complexity`, `## Pitfalls` and `## Key insights`
  sections once a subtopic of the card's primary module names its technique.**
  The three sections move to the module's `sources/<technique>.md`, which the
  subtopic's stage 1 writer is given, and their facts become the subtopic's
  concepts. A new card is written without the three sections, and its facts
  wait for the subtopic. `card check` reads the modules in `content/modules/`
  and refuses a brief keeping one of the three sections after that. Another
  module's subtopic holds none of the card's facts, so it leaves the brief
  alone. The check runs in `card check` and not in the seed, since the engine
  reads no heading of a brief.
- **A brief keeps `## Mental model`, `## Out of scope` and `## Open`.** The
  mental model says what each name in the templates means, which a reader
  needs while reading the templates. The other two say what the card's
  templates leave out.

## The two graphs

The card graph orders cards, and a module's prerequisite graph orders
subtopics.

- **A requirement draws no prerequisite.** A requirement says one card's
  template uses another card's form, and the card graph orders study by it. A
  prerequisite says one subtopic's facts rest on another subtopic's facts, and
  the prerequisite graph gates new questions by it. Kruskal's template sorts
  its edges, and no fact about union-find's cost rests on a fact about
  sorting.
- **The card graph and the prerequisite graph never order two techniques
  opposite ways.** `module check` reads the cards in `content/cards/`,
  projects both graphs onto techniques and refuses a cycle in their union. A
  requirement draws an edge between the two cards' techniques. A
  prerequisite draws an edge from each technique of the needing subtopic to
  each technique of the needed one, through any subtopic naming none. An
  edge from a technique to itself is dropped. A cycle would have the user
  study one technique's form first and the other technique's facts first.

## The algorithms module

- **The module's code is Python, at levels 0 and 1 of `py`'s `core` and
  `stdlib`.** The module's `CLAUDE.md` lists that baseline. A Python API such
  as `heapq` is taught in `py`, and a template using the API cites that
  subtopic. The algorithms module teaches what the structure guarantees.
- **The module has levels 0 and 1, and its own level table** in its
  `CLAUDE.md`. `py`'s table measures how far into Python a learner is, which
  says nothing about algorithms.
- **The module's topics are the vocabulary's kinds**: procedures, structures,
  paradigms and problem classes, with `analysis` for a subtopic naming no
  technique. A topic orders the listing and gates nothing, so the grouping
  reuses the vocabulary's classification.
- **A claim about cost is witnessed by counting steps**, as
  `docs/authoring/concepts.md` `## Claims about cost` gives.
