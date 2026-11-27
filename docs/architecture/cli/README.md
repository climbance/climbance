# Command line

`climb`, run by the author off the server. It holds generation, the by-hand
passes, seeding, invitations, difficulty ratings and the corpus copy.

## Generation is a command

Content generation is a command of the engine, beside the classifier and the
matcher, and it writes the problems, their test cases and their solutions. The
command reuses one transport, one call log and one provenance base, rather than
standing a second copy of each somewhere else.

- **Extraction to a pipeline of its own stays possible and is not planned.**
  Such a pipeline would have to preserve the minted ids, since the attempt log
  references them.
- **Generation runs off the engine's server.** The mutation loop starts many
  subprocesses at a cap well above the sitting's, so a generation run beside a
  sitting moves the wall clock that sitting's verdict is read from. Generation
  writes the corpus rather than serving a page, so it runs wherever the author
  is.

## The corpus is copied to the deployed store

Generation runs against the author's local store. `climb copy-corpus --to
<url>` then copies the problems the deployed store lacks, and `just
copy-corpus` names the deployed store through the tunnel in
`../concepts/deployment.md`.

- **The local store keeps the drafts.** `generate --resume` reads them, and
  the deployed store serves no draft. A sweep then needs the tunnel only for
  the copy, not for the hours the sweep runs.
- **A problem is copied with every product record naming it.** These are its
  cases, its solutions with their verification runs, solution claims and
  template matches, the site outcomes of the writing that landed it, its
  difficulty draws and ratings, its trials, and the calls those records
  name. A writing that never landed stays local.
- **A problem the deployed store already holds brings nothing.** The deployed
  store writes solution claims and difficulty ratings of its own, under its own
  ids. A local copy of one of them would be a second record on the same
  question. The copy therefore only adds problems, and a second run copies
  nothing.
- **A template is matched by its card's slug and its own slug.** Each store's
  seed mints its own template ids, so the deployed store is seeded with a card
  before the problems written for it are copied. A copy naming a template the
  deployed store has not seeded is refused whole.
- **A status that differs between the stores is reported and left.** A
  retirement is the author's act in one store, and the copy writes no update.
- **A call a user's request made is never copied.** Such a call is private to
  that user, as `calls.md` gives. A copy naming one is refused whole.
- **The copy is one transaction on the deployed store.** A run that fails part
  way writes nothing, and `--dry-run` counts the rows without writing.
