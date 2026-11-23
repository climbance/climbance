# Seed

The seed reads the authored files and writes the content tables. A re-seed
refreshes what the files still hold, and the log keeps every reference it
already made.

- **A seeded row a log record references is retired, never deleted.** This
  holds for a module, a topic, a subtopic, a question and a lesson. A deleted
  row would leave its answers and marks pointing at nothing.
- **A retired question is never served and never counted.** It leaves its
  group, its coverage and its certification, and its answers stay readable.
- **A question's slug names one question for good.** A fixed typo or a
  clearer wording keeps the slug, and the seed refreshes the row.
- **A question asking something new takes a new slug.** The old answers
  answered the old question, and a new slug keeps them from counting toward
  the new one. The old slug is retired.
- **A module whose files are removed is retired by `climb module retire`**,
  with every row it holds. The seed reads one module's directory, so a
  directory that is gone retires nothing. The module's questions are retired
  with it, so its files are never seeded again.
- **A retired slug is never reused.** A reused slug would attach the old
  answers to whatever question took it.
- **The author decides which of the two an edit is.** The seed sees changed
  text and cannot tell a clearer wording from a different question.
- **The seed stores each concept of a module written by concept**: its slug,
  its level, its claim and its source, in the `concepts` table. The content
  browser shows a question's concept beside it, and the hosted engine holds no
  copy of `content/` to read the concept from. The snapshot leaves the
  concepts out, since no learner reads one.
- **A re-seed replaces a module's concepts whole.** No log record references a
  concept, so a concept removed from the files has nothing left to keep.
