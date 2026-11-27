# Content repository

The private repository under `content/`, where the author writes the cards and
the knowledge modules. The seed stores both in Postgres, and the engine reads
them from there.

| File | Holds |
|---|---|
| [`cards.md`](cards.md) | What a card is, its ladder, its templates' speedup claims and cases |
| [`card-graph.md`](card-graph.md) | The requirements between cards, roots and depth |
| [`cards-and-subtopics.md`](cards-and-subtopics.md) | How a card and a subtopic of a module share a technique, and the algorithms module |
| [`modules.md`](modules.md) | A module's topics, subtopics and levels, where its authoring rules live, its diagrams |
| [`questions.md`](questions.md) | A question's formats, its key and its grading |
| [`lessons.md`](lessons.md) | Lessons and their pretests |
| [`ai-drills.md`](ai-drills.md) | The AI drill items of the `ai-eng` module, their formats, and the witness run proving each key |

## Cards are ingested from files

Cards are ingested from files. They are authored in `content/` and seeded into
the datastore. `content/` is gitignored like `data/`, and is a private
repository of its own. The technique vocabulary is the exception: it ships with
the package, in git.

- **An authored card has its own shape.** `CardSeed`
  (`src/climb/schema/seed.py`) is the payload the stored card is built from,
  not the card, and it has no field for the identity the engine mints.
- **A card and each template are matched by their authored slug, which makes
  re-seeding refresh rather than duplicate.** A new slug is a new card: the
  runs and the recall history stay with the old card, so renaming is a title
  change.
