# Content repository

The private repository under `content/`, where the author writes the cards and
the knowledge modules. The seed stores both in Postgres, and the engine reads
them from there. The bullets on ingesting cards from files are still in
`../README.md` `## Boundaries`, under "Cards are ingested from files".

| File | Holds |
|---|---|
| [`cards.md`](cards.md) | What a card is, its ladder, its templates' speedup claims and cases |
| [`card-graph.md`](card-graph.md) | The requirements between cards, roots and depth |
| [`cards-and-subtopics.md`](cards-and-subtopics.md) | How a card and a subtopic of a module share a technique, and the algorithms module |
