# Calls

One request to a model and what came back. A layer below the claims. A claim
cites a call and reads its own meaning into the response, and the call record
holds nothing about what the answer was for.
`../concepts/machine-records.md` gives what a record citing a call carries.

## The record

- **Domain-free on purpose.** A call names no attempt, no techniques and no
  vocabulary. It holds only what was asked, of whom, and what returned. That
  absence lets a second domain reuse the log without being taught anything, and
  keeps the run loop's decisions in the domain where they belong.
- **The prompt is stored whole, beside its prompt hash.** The record therefore
  hashes to its own key, and a renderer that changes later cannot make an old
  record unreadable. The prompt is inline rather than deduplicated into a store
  of its own: one append cannot half-succeed, where a file plus a log line can
  leave a call naming a prompt that is not there.
- **A call holds what a claim structurally cannot**: the tokens a run cost, the
  reasoning behind a verdict, and the calls that produced no claim at all. A
  decline names no candidate and a failure names nothing, so neither of them
  reaches a claim at all. Without the call record, a decline and a failure are
  counters that print once.
- **The reasoning field holds what the call produced, not what was asked
  for.** A model that decides a question needs no thought returns none, and the
  empty field is a fact about the call rather than a gap in the record.
- **A call is timed at two levels**: what the caller waited and how many
  requests that took, beside what the last request took alone. The difference
  between the two is the endpoint's backoff, and without it a run held behind a
  per-minute cap reads as a slow model.
- **The run path never reads the call log back.** Whether to ask again is
  decided from the claims, which carry the configuration already. The table is
  written by every run and read only to analyse one.

## The transport

- **One transport, one shape.** Every model is reached as chat completions
  through a router, so adding a model is a string and adding a provider is a
  base URL. Two provider shapes maintained by hand would create pressure to
  adopt a library that reconciles them, and such a library can downgrade a
  schema into a prompt where the record cannot show it happened.
- **Every request names one endpoint.** A provider that cannot honour the
  response schema is never chosen, and a request fails rather than falling back
  to a backend the record would not name.
- **A strict schema can hold a reply in whitespace.** A grammar that permits
  whitespace between tokens lets a model emit nothing else until the token cap.
  On 2026-11-14 the matcher on `deepinfra/bf16` did this on 50 of 362 calls,
  and a retry of the same prompt answered once in 38. `dekallm/bf16` stuck on 5
  of 10 of those prompts, and `groq` on none, so the matcher is pinned to
  `groq`.
- **A choice reply is capped at 8,000 tokens**, about twice the longest one
  measured. A reply stuck in whitespace on any endpoint then costs a quarter
  of the transport's own cap of 32,000.

## Retries

- **A rate cap and a gateway failure are absorbed here, never reported
  upward.** Each is a fact about the endpoint rather than about the
  configuration, and a run's abort exists to catch a broken configuration. The
  four waits are 5, 15, 30 and 60 seconds, 110 seconds in all. The last alone
  covers a minute, since that is the window a per-minute cap is stated in.
  The endpoint's own reset time is not read: where it is carried varies by
  provider, and a wrong parse would sleep for hours.
- **A 404 naming no endpoints is asked once more, at the shortest wait.** The
  router's list of endpoints serving a model moves under a pinned request, so
  the answer is state rather than a rejected request. The retry decides whether
  the list moved, not whether a cap window passed.
- **A model id that does not exist answers the same way**, and pays one extra
  request before it fails. The error message does not separate a missing model
  from a list that moved, and one request is cheaper than a wrong pin failing a
  whole backlog.
- **Every other failure is raised on the first request.** A rejected schema and
  an unset key are answered the same way twice, so retrying them spends the
  abort count slowly instead of at once.
