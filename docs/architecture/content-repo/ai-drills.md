# AI drill items

The AI drills of the `ai-eng` module, as the module's queues serve them. A drill
item is one AI drill a user answers in a queue: an artefact, its key, and the
witness run proving the key. `../concepts/ai-activities/README.md` gives each
activity kind and the rule every check follows. This file gives each kind's
record, how its key is proven, and how its answer is stored.

## Where an item lives

- **A drill item is a question of the `ai-eng` module.** It is authored under
  `content/modules/ai-eng/drills/`, one file per subtopic, and names the
  concept it tests, as a question does. The queues then schedule, gate and
  count it as any question, and the phone serves it without a connection.
- **A drill item is not a `Judgement`.** The judging exercise is served online
  by the API from the cards a user started. A drill item is answered offline,
  in a queue, and its answer goes to the knowledge log.
- **The seed stores a drill item in the content tables as a question of its
  format.** The sync then accepts an answer naming it, since the sync refuses
  a line naming unknown content.
- **The snapshot carries the drill items under `drills`, beside a module's
  questions, left out where empty.** An installed app reads the formats it
  knows from `questions`. A drill format placed there would be served by a
  build that cannot draw it.
- **Retiring a concept retires its drill items**, as it retires its questions.
  A drill whose key stopped holding is retired as a concept is, under
  `[retired.<id>]` in `check.toml`.
- **A `judge` item's lines and a `trace` item's calls fit 60 characters**,
  the width the modules hold code to. A tap has to land on one line of a
  phone's screen, and a wider line wraps more than once there. A trace's
  message and an estimate's texts are prose, which a client wraps.

## The formats

Four formats are added to `choice`, `short` and `open`. Choose the fix is a
`choice` question whose correct option is computed. A pick-the-metric item is
a `metric` question, answered as a `choice` and stating its cases beside it.

| Format | Activity kind | The user's answer | Rating |
|---|---|---|---|
| `judge` | Spot the flaw | clean or flawed, then the flawed line | Good: right verdict and, if flawed, the right line. Hard: flawed called flawed, wrong line. Again: wrong verdict |
| `trace` | Read an agent's trace | the first wrong step | Good: the right step. Again: any other step |
| `estimate` | Estimate | a number | Good: within the item's factor of the key. Again: outside it |
| `metric` | Pick the metric | one candidate | as any `choice` question |
| `choice` | Choose the fix | one option | as any `choice` question |

- **A guess is marked on the new formats as on `choice`.** A correct
  guess rates Hard, since the fact is not yet held.
- **An `answers` row of a drill stores the raw answer beside `correct`**:
  `called_clean`, `tapped` and, on a flawed item, `located` for `judge`,
  `tapped` for `trace`, and `estimate` for `estimate`. Spotting and locating
  are counted apart, as in `../api/short-exercises.md`. A flawed item tapped
  anywhere is correct, and `located` false rates it Hard, since FSRS rates a
  record without reading its item. The factor an estimate is scored within is
  still to be set from real answers, and a stored `correct` alone could not
  be rescored.
- **A drill item may be asked in an exam.** Its verdict is computed from the
  user's tap or number, where an open question's grade is the user's own
  report.
- **After the answer, the item shows its witness**: the input, what the clean
  artefact gave and what the flawed one gave. The witness is the evidence the
  key is right, and reading it is the lesson.

## Spot the flaw

An artefact is a prompt, a function, an eval script, a tool's definition or a
grader's rubric. The author writes it clean, with up to three variants.

- **An artefact yields one clean item and one flawed item per variant.** At
  least a quarter of the items are then clean, so calling everything flawed
  is wrong a quarter of the time. The judgement items keep the same share for
  the same reason.
- **A variant differs from the clean artefact in one contiguous span of
  lines, and that span is the key.** A fault that is an absence, such as a
  missing `other` label or a missing step budget, is written on the line it
  changes: the label list without `other`, or `while True:` for the bounded
  loop. A variant that only deletes lines leaves no line to tap.
- **The record**: the artefact's `id`, `concept`, `prompt`, `lines`, `check`,
  `input`, `output` and `explain`, and a `[[drill.variant]]` table per variant
  with its `id`, `lines`, `span`, `output` and `explain`.
- **The reader expands an artefact into its items**, a variant's id being
  `<artefact>-<variant>`. A flawed item carries its `span`, the clean lines
  there as `fix`, and the clean `output`. The reader derives each span from
  the two texts, and refuses a stated span that differs.
- **The `check` defines `check(output)` on the output of the `input`**, a
  Python expression calling the artefact. The module check proves each key
  with it, as rule 34 in `docs/authoring/rules.md` gives.

## Read an agent's trace

A trace is one failed run of an agent in a scripted environment, a file in
`content/modules/ai-eng/environments/`.

- **An environment file defines `TOOLS`, the tools' names, and a class
  `Environment`** with a method per tool, the goal predicate `goal(answer)`,
  and `state()`, a line naming the end state. A run's final answer is its
  last step when that step is a message.
- **A trace is a list of steps, each the agent's message or a tool call**
  with its arguments and its result. A tap lands on a whole step. A result is
  the environment's, and cannot be the wrong step.
- **The record**: the item's `id`, `concept`, `prompt`, `environment`, `k`,
  `end_state`, `corrected_end_state` and `explain`, a `[[drill.step]]` per
  step of the failed run, and a `[[drill.corrected]]` per step of the
  corrected run from `k` on. The reader renders each call as `name(a=1)` and
  each result as its text, since a client runs no Python.
- **The module check replays both runs in the environment**, as rule 35 in
  `docs/authoring/rules.md` gives: the failed run misses the goal, and the
  corrected run reaches it.
- **The shared prefix makes the first wrong step unique.** Every step before
  `k` is a step of the corrected run, which reaches the goal, so none of them
  is wrong. The failed run's step `k` is the first step the runs differ at.
- **A trace's key is never re-verified**, since the steps are stored and the
  environment is code. A model that wrote a trace is named in its `model`.
- **After the answer, the item marks step `k` and shows the corrected run
  from `k` on**, then the end state of each run.

## Pick the metric and choose the fix

The correct option of both is computed, never authored.

- **A pick-the-metric item stores a goal, a set, two systems' outputs on it,
  and two to five candidate metrics.** The goal is stated in the prompt and as
  a `utility`, code scoring each system as the goal ranks them, such as a
  missed fraud costing a hundred false alarms. Each candidate names a metric
  from the module's metric library, `content/modules/ai-eng/metrics.py`, with
  its `label` and its `params`.
- **The record**: the item's `id` and `concept`, the cases' `expected`
  answers, `a` and `b` for the two systems' outputs, and `inputs` where a case
  needs one. It also holds the `candidates`, the `utility`, and the numbers the
  module check computed: `scores`, a pair per candidate, and `goal`. A set
  holds at most 12 cases, since a phone shows each case as a row.
- **The module check computes every candidate and the `utility` on both
  systems**, and refuses a stored number that differs, as rule 33 gives.
- **The seed refuses an item where other than one candidate ranks the
  systems as the goal does**, read from the stored numbers. A tie between the
  two systems decides nothing and agrees with no goal. Each client derives
  the correct option from the same numbers.
- **After the answer, the item shows each candidate's two scores** and the
  system it put first, in the order the options were shown, then the goal's.
  A wrong pick is shown with the ranking it gave.
- **A choose-the-fix item stores an artefact, its input, its failing output,
  three or four edits, and a `check`.** Each edit is applied to the artefact,
  and its output is computed or stored as in spot the flaw. Exactly one edit's
  output passes the `check`, and that edit is the correct option.
- **After the answer, the item shows each edit's output** on the input.

## Estimate

- **An estimate item states every number its key uses**: the prompt and the
  answer, the tokenizer by its name and version, the prices per million input
  and output tokens, and the rate in tokens per second. An item on another
  quantity, such as end-to-end success from per-step error rates, states its
  rates instead.
- **The record**: the item's `id` and `concept`, the texts `sent` and
  `received`, and each stated value in `given` with its `name` and `label`.
  It also holds the `compute` code, the `working` it prints, the key in
  `computed`, the `factor` and the `unit`. The module pins the tokenizer.
- **The module check runs `compute` and refuses a `computed` or a `working`
  that differs**, as rule 32 in `docs/authoring/rules.md` gives. The key is
  stored because no client holds a tokenizer.
- **A number is correct within the factor**: between the key divided by the
  factor and the key multiplied by it. An engineer estimates to an order, so
  a ratio is scored and a difference is not.
- **After the answer, the item shows the key and the arithmetic** from the
  stated numbers.

## A model-dependent key

A prompt artefact's flaw shows only in a model's answers. Its lines are a
prompt with `{input}` standing for the `input`, and its `check` reads one.

- **A prompt artefact states `share` and `samples`, and each variant its own
  `share`.** Each panel model gives `samples` answers per side. The clean
  lines' answers pass the `check` at or above the artefact's share, and a
  variant's fail it at or above the variant's. A model answers a prompt
  differently on repeated calls, so one answer proves nothing.
- **`climb module reverify` asks the panel in `check.toml` through the
  engine's calls**, so each answer is in the call log with its configuration.
  It rewrites `samples/<artefact>.toml` whole: a `[[sample]]` per answer with
  its `side`, `model`, `call`, `text` and `passed`, and a `[[checks]]` per run
  as a concept's are. A model's answers are written once, and a later run
  appends its check alone.
- **The module check runs the `check` on every stored answer**, as rule 36 in
  `docs/authoring/rules.md` gives. An item whose latest check on a panel model
  failed stops holding, and is retired.
- **A queue replays the stored answers**, so every learner meets the same key
  and the phone needs no model. An item's output is its side's first answer,
  one bearing out the key, with each model's counts under it.
- **A code artefact, a trace, a metric item and an estimate are never
  re-asked.** Their keys rest on code and stored data alone.

## Deferred

- The factor an estimate is scored within, per quantity. The first stored
  `estimate` answers set it.
- The shares and the sample count of a prompt open to injection. The first
  two prompts state 0.8 of 5, and each side came out 5 of 5 on both models.
- Whether a `judge` item is drawn in the order its subtopic's questions are,
  or after them. The first queue serving both answers it.
