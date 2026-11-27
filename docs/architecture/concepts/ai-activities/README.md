# AI engineering activities

The `ai-eng` module teaches each pattern through questions. This folder names
the practice beyond the questions: the AI drills on the phone and the desk
tasks at the desk, per pattern. [`patterns.md`](patterns.md) lists every
activity with its activity kind, its check and its pattern, and marks the
spine. [`readiness-bar.md`](readiness-bar.md) gives the readiness bar the
spine's desk tasks build to. This file gives each activity kind, the rule
every check follows, and how simplicity is graded.

The record of a desk task, the hidden set and the harness's boundary with the
sandbox belong to `../ai-task-grading.md`. The record of each AI drill and
the witness run proving its key belong to `../../content-repo/ai-drills.md`.
This file fixes what each activity kind asks and how its answer is checked.

## The rule every check follows

- **A key is computed by running code, never taken from a model's word.** A
  model writes items and variants, and a model may be wrong about its own
  artefact. A key the engine cannot reproduce by execution teaches a wrong
  answer with the engine's authority.
- **Every key has a witness run stored with the activity.** The witness run
  shows the faulty artefact failing an input the clean one passes, or each
  option's measured score. An activity without a witness run does not land,
  as a problem without passing cases does not land.
- **A witness run that calls a model stores the model's responses.** An AI
  drill replays the stored responses, so its key does not move between two
  learners. A desk task calls a model live, and the grading design gives how
  its score is made to repeat.
- **A learner's answer is structured: a tap, a choice, a number or code.**
  Free text would need a model to grade it, and a model grader is the very
  judge this rule keeps out of the key.
- **A key resting on a model's behaviour is a claim re-verified on a
  schedule.** The witness run is repeated on the current model, and an
  activity whose key stopped holding is retired. The re-verification rule is
  in the authoring docs.

## AI drill kinds

- **Spot the flaw.** The learner reads one artefact: a prompt, a chunker, an
  eval script, a tool's definition, a grader's rubric. It is clean or carries
  one planted fault. The learner calls it clean or flawed, then taps the
  flawed line. Checked as judging a solution is: the witness run is the input
  on which the variant's output differs from the clean artefact's.
- **Estimate tokens, cost or latency.** The learner gives a number for a
  stated prompt and answer: tokens, cost at a stated price, or latency at a
  stated rate. The key is computed by the stated tokenizer and the stated
  arithmetic, so the item carries every rate it uses. Scored by the ratio to
  the key, within a factor the item states, since an engineer estimates to an
  order, never to the token.
- **Read an agent's trace.** The learner reads a stored trace of one agent
  run that failed, and taps the first wrong step. The trace comes from a run
  against a scripted environment with one planted fault. The witness run
  replays the trace with that step corrected, and the task then succeeds.
- **Pick the metric.** The learner reads a system's goal and two systems'
  outputs on a stated set, and picks the metric that should decide between
  them. The item computes every candidate metric on the outputs. The key is the
  candidate ranking the systems as the stated goal ranks them. A wrong pick is
  shown with the ranking it gave, such as accuracy ranking a majority-label
  baseline first on imbalanced labels.
- **Choose the fix.** The learner reads a failing output and its artefact,
  and picks one of several edits. Each edit is run on the item's input, and the
  key is the edit whose output passes. The strategy names this kind for the
  judging form, and it carries over.

## Desk task kinds

- **Build a component.** The learner writes a component to a stated
  interface: a retriever, an extractor, a router, an agent. The harness calls
  it on the hidden set and scores the stated metric against the bar.
- **Fix a planted fault.** The learner receives a working system holding one
  variant's fault, scoring under the bar. The harness scores the fixed system.
  The fault is known, so the slice the fault fails is named after grading.
- **Hit the bar under a budget.** A build or a fix with a cost budget in
  tokens per case. Every model call goes through the harness, which counts the
  tokens. A submission passes on the metric and the budget together.
- **Write the eval set that catches broken variants.** The learner writes
  cases and their expected answers, and the metric's threshold. The harness
  runs the eval on the clean component and on each stored variant. The score
  is the variants the eval fails, with the clean component passing. This is
  mutation testing turned on the learner's eval.
- **Defend an agent.** The learner adds guardrails to an agent holding tools.
  The harness runs an adversarial set and a benign set. An attack succeeds
  when the environment logs the action the attack aims at, such as a canary
  tool called. A benign case succeeds when the environment reaches its goal
  state. The environment's log gives the attack success rate and the false
  refusal rate, so no model's verdict enters either.

## Higher-level kinds

- **A runnable design decision.** The learner chooses between stated designs,
  such as reranking or none, or one chunk size or another, and predicts each
  design's score and cost. The harness has measured every design on the
  hidden set at landing. The key is the measured winner under the stated
  constraint. The predictions are scored by their error against the
  measurement.
- **A design review with planted flaws.** The learner reads a written design
  of a system and flags each flaw: the section and a flaw kind from a fixed
  list. Each planted flaw has a witness run: the system built from the design
  fails a named slice, and the corrected system passes it. The score is the
  flaws found and the flags on sound sections, counted apart, as spotting and
  over-calling are in judging.

## Simplicity is graded

- **A desk task's submission declares its stages.** The interface names the
  stages a component may hold, such as rewriting the query, retrieving,
  reranking and answering. The harness needs the stages named to remove one.
- **The harness removes each declared stage in turn and grades again.** Each
  removed stage is replaced by the identity the interface defines, such as
  passing the candidates through unchanged.
- **A stage earns its place when removing it drops the score or raises the
  cost beyond the noise.** The noise is the confidence interval of a paired
  comparison on the hidden set, as the `comparing-systems` subtopic teaches.
- **A stage that does not earn its place is named in the result, and the
  simplicity score counts those stages.** A pass on the metric stays a pass.
  The simplicity score is reported beside the metric, since a learner adding
  a reranker by habit has learned the habit, not the pattern.
- **Ablation costs a full grading per stage.** The budget a task states covers
  the learner's runs. The ablation runs are the engine's cost, and a task
  declares at most as many stages as its hidden set's size makes affordable.
  The count is deferred to the first retrieval task's measured cost.

## Deferred

- The factor an estimate is scored within, per quantity. The first items
  answered on real use set it.
- Whether a design review's flaw kinds are one list for the module or one per
  pattern. The first written reviews answer it.
