# Project conventions

AI coaching layer for deliberate practice of algorithmic problem-solving.
See `README.md` for what this is.

## Stack

- Python ≥3.15.2, `uv` for env/deps, pydantic v2, pytest.
- `textual` where a command is a screen rather than a scroll, driven in tests
  through its pilot.
- `uv sync` to set up; `uv run pytest` to test, always, whether one file or
  the whole suite. `addopts` spreads it over every core, 9s against 65s.
- `npm install` at the repository root installs the workspace: `packages/core`,
  the shared TypeScript core, `native/`, the native app, and `web/`, the
  frontend. `just native-test` runs the core's and the app's tests.
- `web/` is the frontend: Vite, React and TypeScript, built to static files.
  `npm run build` runs inside `web/`, and `just web-check` runs its type
  check, lint and tests.
- shadcn/ui over Radix, with Tailwind, for the components. `npx shadcn add
  <name>` inside `web/` copies one into `web/src/components/ui/`. Restyle
  through the theme tokens in `web/src/index.css`, not by editing a copied
  component, so the components stay consistent and an upgrade merges.
- Postgres is named by `DATABASE_URL` in `.env`. `just migrate` applies the
  migrations, and `just migration <name>` generates the next one.
- Signing in reads `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, their `_SECRET`
  pairs, `CLIMB_ORIGIN` and `CLIMB_SECRET` from `.env`. A provider
  with no client offers no route, and with none the sign-in routes are absent.
- Locally, `CLIMB_DEV_LOGIN=local` in `.env` and no provider client: the
  login page `just app` serves offers a dev login as `local`.
- The integration tests need a Postgres server named by `TEST_DATABASE_URL`.
  Its user needs the right to create databases and to set
  `session_replication_role`. Each xdist worker keeps a database of its own
  between runs, and recreates it when a migration file changes. A test taking
  the `database` fixture is marked `integration` and finds every table empty.
  `just test-unit` runs the rest, without a database.
- `just app` runs the API and the Vite dev server together, and Ctrl+C stops
  both. The page is at the address Vite prints.

@docs/architecture/README.md
@docs/architecture/concepts/terms/content.md
@docs/architecture/concepts/terms/corpus.md
@docs/architecture/concepts/terms/generation.md
@docs/architecture/concepts/terms/execution.md
@docs/architecture/concepts/terms/machine.md
@docs/architecture/concepts/terms/log.md
@docs/architecture/concepts/terms/knowledge.md
@docs/architecture/concepts/terms/clients.md

The other files in `docs/architecture/` are not loaded at start. Before
changing what one of them governs, read that file: the map in its README names
which folder holds what. A rule in `.claude/rules/` names the folder for the
code it covers.

## Where knowledge lives

- Docs matter more with an AI executor, and should be fewer: they are the only
  durable context, and they got cheap to write exactly when they got valuable.
- They carry intent, reasons, and the shape of the system — what a model
  cannot infer and would otherwise reinvent differently each session.
- Facts go where they can be enforced: tests, then hooks and types. Prose
  carries what nothing can execute.
- Implementation follows from tests and shape, and feeds back: what it
  discovers revises the doc.
- Divergence is checked on purpose. An unchecked doc describes a system that
  does not exist, and a model implements that description anyway.
- A measurement a design choice rests on is written beside that choice in
  `docs/architecture/`, since nothing re-derives it. How the work went is in
  the commits.
- The plan, what is still to do and in what order, is kept outside this
  repository.

## Sequencing

High-level design first, without detail; then small items one at a time.
Neither big batches nor detailed design up front.

A design pass settles boundaries, record shapes and what is irreversible, then
stops. A detail only real use can answer is named as deferred rather than
reasoned out. The schema is designed ahead of the features that write it.

## Writing

Docs, `README.md`, commits.

- Write for a reader who opens this file first and has not read the others.
  Prefer the explicit sentence over the short one. Two faults, tested
  separately:
  - A sentence is wordy if deleting it loses no fact. Delete it. This covers
    restating, hedging, and a reason given twice.
  - A sentence is dense if the reader needs another section to know what a
    noun refers to. Name the noun. This costs a few words, not a paragraph.
- **No aphorisms.** State the rule, then the reason, both literally. Don't
  compress an argument into a metaphor the reader has to unpack.
- **Name what every noun refers to.** A noun the doc has not defined — `the
  work`, `the point`, `the product`, `the unit` — means the sentence restates
  the previous one in more abstract words rather than adding a fact. Cut it,
  or name what it stands for.
- **Every word this project gives its own meaning is an entry in
  `docs/architecture/concepts/terms/`.** A file uses the word
  without redefining it. A word not there is defined in the sentence that
  introduces it, or added to the glossary. `the bench`, `the walk`, `the
  builder` are each defined in one file and used in four, so a reader of the
  fourth file cannot resolve them.
- **One name for one thing, and one thing per name.** A record, a state or a
  field has the same name in the docs, the code and the store. A name carries
  one meaning. `clock` beside `naive` was one thing under two names, and
  `brief` for both a card's reading and a run's target was two things under
  one. Either way a reader has to know which is meant, and a model guesses.
- **Repeat the noun instead of `one`, `it`, `that`, `the two`, `either`.** A
  pronoun two sentences after its noun is resolved by the writer and guessed
  by the reader.
- **No cleft sentences.** Not "What a site left is stored", not "The reference
  is what discards". Write the subject, the verb, the object: "Each site's
  outcome is stored", "The reference discards the problem".
- **Contrast is not the default form.** "X, never Y", "X rather than Y" and
  "as a claim does" each assume the reader knows Y. State X on its own first.
  Add the contrast only where Y is a mistake a reader would otherwise make,
  and name Y in full when you do.
- **A sentence does not open with `What`, `Where`, `Neither`, `Both` or
  `Nothing`.** Each of these fronts an abstraction and delays the subject to
  the end. Start with the concrete noun the sentence is about.
- **A bullet ends on its reason.** A closing clause that can be deleted
  without losing a fact is a summary. Check the last sentence of every bullet
  against that test.
- **No personification.** Records don't wear, ride, go quiet, or flatter. Say
  what the code does.
- **One idea per sentence.** Split at the em-dash and the semicolon instead
  of chaining. Target 25 words; nothing over 40.
- Precise technical terms are unaffected — `append-only`, `provenance`,
  `denominator`, `supersede`. Use the exact term.

Aphorism, before: "A blank string is the same absence wearing a value, so it
is rejected too."
After: "A blank string is rejected too. It passes a presence check while
carrying nothing."

Dense, before: "What a site left is stored rather than only printed. A run's
stage lines end with the process. The gate that rejected an answer, the
configuration behind it and the digest it was sent are readable nowhere else."
After: "Each site's outcome is stored, not only printed. The run prints one
line per stage, and that output is gone when the process ends. Without a
stored record, nobody can later see which gate rejected an answer, which
configuration produced it, or which prompt hash it was sent."

## Code style

- Match pydantic/pytest idiom. Keep slices thin: a feature is done when a pass
  through its flow runs on real data, not when it's feature-complete.
- **A docstring and its comments stay shorter than the code they sit on.** Over
  that, the reason belongs in `docs/architecture/` and the code cites it.
- **No docstring where the name and the signature already say it.**
  `candidates() -> list[str]` returning `sorted(codes())` needs none.
- **Never restate a reason `docs/architecture/` already gives.** Docs are the
  durable context; a copy in the code drifts from it. Point instead:
  `# sorted: the prompt hash is taken over this order`.
- **One comment carries one non-obvious fact** — the alternative rejected, the
  invariant that would break. Not the argument for it.
- The `## Writing` rules are for docs and commits. They do not license prose in
  a module.
- Tests are the exception to the budget. A test keeps a one-line docstring
  saying what it pins, since the body is two lines and the name cannot carry
  the reason.
- **A test module carries no docstring**, and one already there is deleted. The
  exception above is per test. A module-level one restates what the filename
  says or what `docs/architecture/` already carries, and a fact it holds alone
  belongs on the test that pins it.

## Git

- Conventional Commits, imperative subject ≤50 chars, English.
- Pre-commit + commit-msg hooks live in `.githooks/`
  (enable once: `git config core.hooksPath .githooks`).
  They enforce a vocabulary guard whose word list is `.githooks/words`. It is
  untracked, since it names exactly what must never be committed. Without the
  list the hooks fail rather than pass. A guard that silently allows everything
  when unconfigured is worse than no guard.
- Pre-commit runs the frontend's type check, lint and tests when `web/` is
  staged, and `just web-check` runs them by hand.
- Pre-commit runs the shared core's type check and tests when `packages/core/`
  is staged. Those tests include the check that fails on an import cycle.
- Pre-commit also runs ruff, pyright, vulture and `tests/test_architecture.py`
  when code is staged: the import contracts in `pyproject.toml`, the module size
  limit, and that a name is imported from where it is defined. The full suite is
  `just test`, by hand.
- `tests/schemas/` holds each stored record's JSON schema as last agreed, and
  `tests/test_schema_additive.py` refuses a change that is not additive. An
  intended tightening rewrites the snapshots in the same commit: `just
  schemas`.
