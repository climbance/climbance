# Machine records

The fields every record written by a model carries. Claims, template matches,
solution claims, canonical solutions, trials and the arguments of a test case
are written by a model. Each of them carries the same fields to stay
comparable, and those fields are stated here once. `../cli/calls.md` gives the
call log the records cite.

## What a machine record carries

### Provenance

- **Provenance is the configuration**: model, effort, the endpoint the model was
  pinned to, the prompt hash of what that record was sent, and the call that
  sent it. All of them or none, since a record whose configuration is partly
  unknown compares with nothing. Temperature is recorded beside them, outside
  that rule, as `### Temperature` gives.
- **A model asked for no effort, or a model that rejects the parameter,
  records `default`** rather than an empty field. The parameter is not sent,
  so the level the model ran at is the endpoint's own and is not read back.
- **A configuration is per call site, not per run.** Writing a problem takes
  six calls, and each asks for a different thing. The generator writes a
  statement and a solution. The screen site judges whether the draft copied a
  published problem. The blind site writes an independent reading of
  that statement. The discrimination site writes the inputs that catch a wrong
  solution. The inputs site writes code that builds an input of a given size.
  The naive site writes the approach the form replaces, and the speedup search
  measures the canonical against it. One configuration over all six sites
  makes the cheapest site pay the price of the hardest.
- **A run mixing models stays readable, because each record names its own
  call.** The problem names the call that wrote it, its
  reference names the call written blind, and a case won by a round names the
  call that proposed it. No record reads a run-wide configuration, so there is
  none to be wrong.
- **A pin is part of the record, not a note about routing.** A model id
  resolves to as many builds as there are endpoints serving it, and
  quantization changes the weights. Unpinned, the router chooses per request,
  so the records under one key are a mixture no later run can separate.
- **Who served a call is recorded and never compared.** The router reports a
  company rather than an endpoint, and one company serves several builds. The
  company name confirms that a pin held, without identifying the build. The
  name is also not known until the response arrives, so a run deciding what
  it has already read cannot key on it.
- **A machine record's price is recorded and never compared.** A price says
  when a record was written rather than which model wrote it, so two records
  compare
  whether or not each carries a price. The price sits outside the all-or-none
  rule, as the temperature does: a record stored before the field existed
  carries none, and so does a record a provider priced at nothing.

### Temperature

- **A machine record is greedy, and says so.** Sampling turns a verdict the
  model holds at 0.9 into one it gives four times in five. An eval absorbs that
  variance by being repeated. A sweep cannot be repeated: it writes into an
  append-only log the board reads forever. Temperature identifies a record for
  the same reason the pin does: the pin says which weights answered, and the
  temperature says how they were sampled. A temperature nobody set is the
  provider's own default. It is recorded absent, and equal only to itself, which
  keeps records taken before the parameter existed scorable rather than
  excluded.
- **The generator and the naive site are sampled**, for the reason
  `../cli/generation/solutions.md` gives: each produces an artifact rather
  than a verdict about one. The generator's variance buys diversity across a
  corpus of statements, and the naive site's variance buys a second draw where
  the first draw wrote the form.
- **The difficulty judge is sampled**, for the reason
  `../cli/difficulty/judge.md` gives: a problem's judged rating is the median
  of several draws, and greedy draws would all answer one number.
- **The other four sites are greedy.** Greedy answers make two configurations
  of one site comparable over the same item. Those sites answer about a
  statement that already exists, and each answer decides something.
- **Whether a site can be greedy is the endpoint's answer.** A request naming
  a parameter its endpoint does not advertise is refused rather than served, so
  a temperature sent where none is offered fails the call instead of running
  greedy. Some endpoints serving a model at an effort advertise no temperature
  and others carry both, so pinning a site to `0` costs the effort in one place
  and nothing in another.

### Storage and staleness

- **Staleness keys on the prompt hash of what was sent**, never on a version
  over the vocabulary. A criterion travels with its candidate, so editing one
  entry re-derives what that entry reached and leaves the rest. An author can
  forget to bump a version while the text moves. A prompt hash moves with the
  text. The cost is that a reflowed sentence re-derives what it reaches, and
  that the criteria are cited as a prompt hash rather than as "prompt 3".
  Editing one criteria entry re-derived 7 of 31 attempts' claims, where a
  version bump would have re-derived all 31.
- **The configuration is stored once, on the call, and a record references
  the call.** A record carries its provenance whole when it is read, and the
  store fills the fields from the call the record names. One call writes many
  records, as a generation call writes a problem's cases, so a copy on each
  record would be a second place for the configuration to disagree.
- **The JSON stores copied the configuration onto every record.** Loading the
  call log to learn which model wrote a record was a megabyte-scale read on
  every command. On Postgres the call is one indexed row away, and every
  stored copy matched its call when the stores moved.
- **A call is never deleted while a record references it.** The call log is
  append-only already. Generation's calls are product data, and only the
  classifier's calls on a user's attempts are that user's.

### Reading the records

- **The precedence is a reader, not a write path.** Preferring the user's
  record on read makes overwriting the evidence unrepresentable, where a write
  path that skips what the user answered depends on every writer remembering
  to.
- **Each configuration is scored over what it read**, and the denominator is
  printed rather than assumed. Scoring over the intersection alone charges
  every column for the records one column failed on. A share prints as
  `92/98`, so two columns over different samples cannot be read as one rate.
  Whoever reads the table still supplies the judgement that the harder sample
  reads as the worse model.

## Content written by a session

A question, a concept, a lesson or a card written by a Claude Code session is
content, not a machine record. The stored record carries no writer and no
provenance.

- **A session leaves nothing provenance could hold.** It makes no call through
  the engine's transport, so no call id exists. It reads files as it goes,
  so no single prompt has a hash. It names a model by an alias such as
  `opus`, which resolves to no pinned build. Provenance is all or none, so a
  partial one would compare with nothing.
- **Content needs no provenance to be judged.** A machine record keeps its
  configuration so that configurations can be scored against each other and a
  stale record re-run. Content is checked by the module check or `card check`,
  reviewed, and revised in place by the seed. A question stands on its witness
  and its review, whichever model wrote it.
- **The content repository's history records the writer.** `run.py` in the
  `concept-author` skill writes each role's model into the body of the commit
  it makes, and the subtopic's digest records the rounds. A session run by
  hand, as a card is written today, leaves its commit alone.
- **A writer field joins the stored record once a query reads it**, such as a
  defect rate per writer model. The field is then additive, and the commits
  supply it for content written before.
