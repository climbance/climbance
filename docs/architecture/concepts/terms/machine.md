# Machine record terms

Words this project gives its own meaning for the records a model call writes.
Every file in `docs/architecture/` uses them without redefining them.

- **Machine record**: any record a model call wrote: a claim, a match, a
  solution, a case's arguments. It carries provenance whole. Content a Claude
  Code session writes is not one, as `../machine-records.md` gives.
- **Configuration**: model, effort, endpoint pin and temperature.
- **Provenance**: the configuration, the prompt hash of what was sent and the
  call that sent it.
- **Pin**: the endpoint a model id is fixed to, so one build answers.
- **Prompt hash**: the hash of the prompt a record was sent, `prompt_hash` on
  every machine record. Staleness keys on it.
- **Stale**: a record whose prompt hash differs from the one its site would send
  now. A re-run reads stale items and skips the rest.
- **Greedy** / **sampled**: temperature zero, or the provider's default. The
  answering sites are greedy. The generator and the naive site are sampled.
- **Call**: one request to a model and its response, domain-free. The call
  log holds every one.
- **Standing**: the record that answers a question when several were written
  about it. The user's stands over the machine's, and among the machine's the
  latest stands.
