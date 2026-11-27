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
- **A call made for a user's request names the account in `user_id`.** The
  account is the one fact about the caller a call holds. The daily cap in
  `../api/README.md` counts it, and a user's erasure deletes the call with the
  log. A call `climb` makes leaves `user_id` empty.
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

- **One transport, one shape.** Every model reached over an API is reached as
  chat completions through a router, so adding a model is a string and adding
  a provider is a base URL. Two provider shapes
  maintained by hand would create pressure to adopt a library that reconciles
  them, and such a library can downgrade a schema into a prompt where the
  record cannot show it happened. The subscription backends below are the one
  exception, and each is a CLI the engine runs, not a second API shape.
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

## The subscription backends

Generation's sites run on the author's Claude and ChatGPT subscriptions, through
the `claude -p` and `codex exec` CLIs. On OpenRouter a landed problem cost about
$0.20 on 2026-11-27, so the 1,000-problem target would cost about $200. A
subscription charges nothing per call, so a problem is regenerated for free.

- **A pin names the CLI and its version, such as `claude-code 2.1.332` or
  `codex-cli 0.171.0`.** Each CLI wraps the prompt in instructions of its own,
  so an upgrade changes what the model is sent. A bench names the bare
  backend, `claude-code` or `codex-cli`, and `climb` resolves it to the
  installed version before the run. A call whose pin names another version
  than the one installed is refused.
- **The model is a full id, such as `claude-sonnet-5-5`, never an alias.** An
  alias moves to a newer model, and the record would name whichever one
  answered on the day.
- **A subscription pin is weaker than an endpoint pin, and that is accepted.**
  The vendor serves one build per model id and is the only host, so no
  quantization or provider choice is hidden. The vendor can still update the
  weights behind an id, and no record can show that.
- **Each call runs prompt-only, in an empty directory created for it.** Claude
  runs with no tools, with the site's prompt as its system prompt, and with no
  setting sources. The user's own `CLAUDE.md` and hooks therefore stay out of
  the prompt: with them, a two-word prompt sent 4,526 input tokens, and without
  them 678. Codex reads the site's prompt as its instructions file, in place
  of its own coding-agent prompt, with its environment context, its web search
  and every feature offering a tool turned off. With its shell tool on, the
  model ran a command in 2 of 29 generation calls on 2026-11-27. A developer
  message and about ten tool definitions stay, since no setting in
  `codex-cli 0.171.0` removes them: a two-word prompt sent 5,830 input tokens
  on 2026-11-27, against about 17,700 with Codex's own prompt. A Codex call
  whose events show any item other than a message or reasoning is still
  refused, since the model then read more than the prompt the hash names.
- **No API key reaches a CLI.** An `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
  in the environment wins over the subscription login, and `climb` loads
  `.env`, which holds one. On 2026-11-27 the first runs were billed to the API
  account this way, until its credit ran out. Each CLI therefore runs with
  every `ANTHROPIC_`, `OPENAI_` and `CLAUDE_CODE_` variable removed.
- **The schema is enforced by each CLI.** Claude takes it as `--json-schema`
  and Codex as `--output-schema`. A reply that does not parse fails the site's
  gate as it does on the router.
- **Codex writes the generator's and the naive site's answers, and Claude
  the other four.** The blind site runs on Sonnet, another model family than
  the canonical's, so a mistake both share is less likely. Haiku answers the
  screen, the inputs and the discrimination sites. On 2026-11-27 this bench
  landed 8 of 10 writings, and the bench with Claude on the generator and the
  naive site landed 1 of the same 10. Claude's naive solution finished at the
  bound or ran within a tenth of the canonical in 4 of them. All 4 landed once
  Codex wrote the naive solution.
- **The cost is recorded as 0, and the tokens as each CLI reports them.**
  Claude reports a notional `total_cost_usd`, which is not stored, since the
  spend page would count money never paid. Codex adds about 5,800 input
  tokens of its own to every prompt, so its token counts on a short prompt
  mostly measure the CLI.
- **No temperature is sent.** The two CLIs take none, so every site on this
  bench is sampled. `../concepts/machine-records.md` gives what that costs.
- **An effort of `default` sends no effort flag.** The CLI then answers at its
  own default, as a claim about a model as it answers by default needs.
- **Only `climb` reaches these backends.** The server holds no subscription
  login, and the API makes no model call, so a user's request never runs on
  the author's account.
