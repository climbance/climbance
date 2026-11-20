# Repo constraints

Rules on how this repo is built, rather than properties of the running system.

- No concrete third-party problem-platform client ever enters this repo.
- Schema changes must be additive (new optional fields), never breaking. A
  change may tighten instead, by making a field required, removing a field or
  widening a validator. Tightening is allowed only while no stored record
  carries the loose shape, which in practice means deleting the records that
  do. Weigh what is deleted, not how many: the log has to stay readable by its
  own schema, and a field kept for a handful of disposable records is one every
  reader branches on forever.
- `data/` and `content/` are gitignored, and only the schema is public. The
  generated corpus could be published, since the product owns it, and is not:
  the database holding the corpus also holds the private log.
- An architecture doc holds at most 200 lines, fenced blocks not counted, and
  at most 12 top-level bullets under one heading. A session reads a whole file
  to use one bullet of it, so a small file costs less to read. A component
  over the limit becomes a folder, and a long section is grouped under
  subsections. `tests/test_doc_sizes.py` holds both limits.
- Prefer tools and functions over agents. Multi-agent is adopted once a
  pipeline needs it, never as the starting structure.

## Meta-rule

Ship thin on features, and design the record schema one phase ahead of them.
Component boundaries can be refactored. An append-only log cannot.

## The calibration corpus

The calibration corpus is the platform data the pivot to generated problems
left behind, under `data/old/`: a platform's problems, the attempts against
them, the claims and the calls. It is a corpus rather than a store: no store
points there, and nothing on the run path reads it.

- **The corpus is kept for one deferred measurement: how often a matcher names
  a form from a statement alone.** A corpus no generator wrote is the baseline
  for that rate. How the corpus is read is deferred to taking the measurement.
