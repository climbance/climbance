# Generation terms

Words this project gives its own meaning for writing a problem: the call sites,
the writing states and the mutation loop. Every file in `docs/architecture/`
uses them without redefining them.

## Call sites

- **Site** (call site): one of the six model calls writing a problem, each
  at its own configuration: generator, screen, blind, inputs, naive and
  discrimination.
- **Generator**: the site writing the statement, the canonical and the first
  cases in one call.
- **Screen site**: the site judging whether a draft reuses the example, the
  values or the wording of a published problem. It answers from what the model
  remembers, since the engine holds no published problem to compare with.
- **Copied**: reusing a published problem's example, values or wording. The
  gate the screen site rejects a draft by, and the retirement reason of a
  problem it names. A published question retold in the engine's own words is
  not copied.
- **Blind site**: the site writing the reference from the statement alone.
- **Inputs site**: the site writing the input generator.
- **Input generator**: model-written code building an input of a given size and
  seed.
- **Bound**: the largest input the statement admits, as the input generator's
  `size` counts it. Stored as `largest` on the draft and the site outcome.
- **Naive site**: the site writing the naive solution.
- **Discrimination site**: the site asked for cases that kill the surviving
  mutants.
- **Bench**: the configuration of each site a run is aimed with, from the
  `--site` flags or the built-in default.

## Drafts and their states

- **Draft**: a problem being written, stored at every state so a failed step
  can resume. Cleared at landing.
- **Writing state**: how far a draft got: drafted, checked, screened,
  referenced, agreed, built, paced, searched, hardened, landed, or rejected.
- **Screened**: the writing state after the screen site found nothing copied.
- **Paced**: the writing state after a naive solution passed the cases. Named
  for the pacer, the runner who sets the time others are measured against.
  `unpaced` is the reason a draft has none.
- **Hardened**: the writing state after the mutation loop appended the cases it
  won. Named for hardening, making a thing resist attack.
- **Gate**: a check a draft must pass to advance. A failed gate rejects the
  draft or holds it, and is named on the site outcome.
- **Rejected**: a draft's terminal state. The gate names why: `no_value`,
  `copied`, `untested`, `disagreed` or `unexercised`.
- **Held**: a draft stopped at a state a resume can re-enter.
- **Landing**: the last step: the problem, its cases, its solutions, the
  verification runs of the canonical and the reference, and the generator's
  template match are stored together.
- **Resume**: `generate --resume`: re-entering every held draft at the first
  step whose configuration or prompt hash moved.

## The mutation loop

- **Mutant**: the canonical with one semantic change made on the parsed tree.
  A tree walk enumerates them, and no store holds them.
- **Kill**: a mutant failing at least one case, or answering a built input
  differently from the canonical.
- **Survivor**: a mutant no case and no built input killed.
- **Fuzz pass**: running the survivors against inputs the input generator
  builds. Costs no call.
- **Shrink**: reducing a kept fuzz input to the smallest list still killing
  the same mutants.
- **Kept input**: an input the fuzz pass built that killed a mutant, shrunk and
  stored as a case. `kept` on the draft.
- **Round**: one discrimination call, proposing cases for the survivors. At
  most two per draft.
- **Won case**: a round's proposal that killed a mutant, stored as a case.
  `won` on the draft and the site outcome.
- **Mutation loop**: the fuzz pass and the rounds together.

## The speedup search

- **Speedup search** (the search): finding the smallest input on which the
  naive solution exceeds the sitting's cap and the canonical does not. The
  walk is the sequence of sizes it tries.
- **Separating case**: the case stored at the size the search found.
  Appended after the loop, naming no round.
- **Ceiling**: 1 MiB, the most a stored case may weigh.

## Writings and runs

- **Writing**: one run of the generation flow over one target, from the
  generator's call to landing or rejection. An attempt is a different
  thing: the log's record of a user's solution.
- **Site outcome**: the record of what one site left on one writing: the gate,
  the counters and the configuration.
- **Writing id**: the id a run mints per writing. The draft and its site
  outcomes share it.
- **Replay**: running the five answering sites over stored problems at a new
  bench. It writes nothing to the corpus.
- **Sweep**: one `generate` run over every target, or over every held draft.
