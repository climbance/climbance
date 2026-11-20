# Postgres

Storage is one Postgres database, named by `DATABASE_URL`, and every store
writes there. The schema is the contract, and the tables are declared against
it.

## Data classes

Every class of stored record, with who owns it and how it is written. Each
class links to the file that specifies the record.

| Class | Owner | Visibility | Write semantics | Source of truth |
|---|---|---|---|---|
| [Techniques](../concepts/techniques.md) | product | global | read-only at runtime | this repo, in git |
| [Cards](../content-repo/cards.md) | product | global | read-only at runtime | the store, seeded from `content/` |
| [Modules and questions](../content-repo/modules.md) | product | global | refreshed by the seed | the store, seeded from `content/` |
| [Drafts](../cli/generation/README.md) | product | global | revised in place | the store |
| [Problems](../cli/generation/problem.md) | product | global | created once; only its status moves | the store |
| [Test cases](../cli/generation/test-cases.md) | product | global | written with the problem | the store |
| [Solutions](../cli/generation/solutions.md) | product | global | append-only | the store |
| [Solution claims](../cli/classifier.md) | product | global | append-only | the store |
| [Difficulty ratings](../cli/difficulty/README.md) | product | global | append-only | the store |
| [Difficulty fits](../cli/difficulty/fits.md) | product | global | append-only | the store |
| [Trials](../cli/difficulty/trials.md) | product | global | append-only | the store, or beside the anchors for an anchor's trial |
| [Verification runs](../cli/generation/verification-runs.md) | product | global | append-only | the store |
| [Template matches](../cli/matcher.md) | product | global | append-only | the store |
| [Mutant diagnoses](../cli/diagnoser.md) | product | global | append-only | the store |
| [Judgement items](../cli/exercise-items.md) | product | global | created once; only its status moves | the store |
| [Key-line items](../cli/exercise-items.md) | product | global | created once; only its status moves | the store |
| [Site outcomes](../cli/generation/site-outcomes.md) | product | global | append-only | the store |
| [Sittings](../api/sitting.md) | user | private | revised in place | the store |
| [Card runs](../api/card-runs.md) | user | private | append-only | the store |
| [Recall attempts](../api/recall.md) | user | private | append-only | the store |
| [Judgements](../api/short-exercises.md) | user | private | append-only | the store |
| [Fills](../api/short-exercises.md) | user | private | append-only | the store |
| [Predictions](../api/predictions.md) | user | private | append-only | the store |
| [Retirement requests](../api/retirement-requests.md) | user | private | append-only | the store |
| [Feedback](../api/feedback.md) | user | private | append-only | the store |
| [Run faults](../api/run-faults.md) | user | private | append-only | the store |
| [Attempts](../api/attempt-log.md) | user | private | append-only | the store |
| [Attempt verifications](../api/attempt-log.md) | user | private | append-only | the store |
| [Attempt claims](../api/attempt-claims.md) | user | private | append-only | the store |
| [Calls](../cli/calls.md) | product, or user where only a user's record names the call | global, or private with that record | append-only | the store |
| [Users](../api/sign-in.md) | user | private | created once | the store |
| [Identities](../api/sign-in.md) | user | private | revised in place: the email at each sign-in | the store |
| [Sessions and app tokens](../api/sign-in.md) | user | private | revised in place: last use and revocation | the store |
| [App codes](../api/app-tokens.md) | user | private | revised in place: redeemed once | the store |
| [Invitations](../api/sign-in.md) | product | private | added and deleted by the author | the store |
| [Self-labels](../api/self-labels.md) | user | private | append-only | the store |
| [Diagnoses](../cli/diagnoser.md) | user | private | append-only | the store |
| [Answers, stints, module statuses, focuses, lesson marks, certification exams, setting changes, limit raises, module orders](../api/knowledge-log.md) | user | private | append-only | the store |

## Declaring the tables

- **The engine reaches Postgres through SQLAlchemy Core, and Alembic applies
  the migrations.** The tables are declared once in Python, so a field added to
  a record is one column and one generated migration, where hand-written SQL
  names the field again in every statement that lists columns.
- **The ORM is not used.** Core builds each statement explicitly, so a write
  the code does not name never happens, and the append-only logs stay visible
  as inserts alone.
- **A table holds a column per field, `NOT NULL` where the record requires the
  field.** The database then refuses a record the schema refuses, rather than
  storing whatever a writer sent.
- **A string enum is a Postgres enum type holding the member values, the
  strings a stored JSON record already carries.** A timestamp keeps its time
  zone.
- **A list of records is a child table keyed to its parent, with its position
  where the order matters: a sitting's pauses, a run's case results, a card's
  templates.** A list of strings is a `text[]` column.
- **JSONB holds a value only where the value is JSON of any shape by design, as
  a test case's arguments and its expected value are.**
- **A seeded content row may also hold its authored structure as JSONB: a
  question's format fields and detail, a module's graph and certification
  settings.** The seed validates each against a typed record before storing it,
  and no query reads inside it.
- **The exception covers content the seed refreshes, never the log.** A log
  record cannot be rewritten, so only its columns let the database refuse a bad
  record.
- **A machine record's table holds its `call_id`, a foreign key to `calls`, and
  none of the configuration.** `../concepts/machine-records.md` gives why the
  configuration is stored once.

## Migrations

- **The migrations live in `migrations/`, generated by Alembic from the
  declared tables and read before they are committed.** An enum type is created
  once, before every table using it, and dropped after them, since a column
  declaring its own type would create it twice.
- **A field added to a record is a nullable column added by a migration, which
  is the additive rule in `## Repo constraints`.** A test compares each table's
  columns with its record's fields, since the two are declared apart.
- **An append-only table refuses an `UPDATE` and a `DELETE` by a trigger, and
  so do the case results stored with a run.** A store with a bug in its write
  path is then refused by the database instead of rewriting the log. A
  migration creating an append-only table adds the trigger by hand, since
  Alembic generates none, and a test lists the tables that carry it.
