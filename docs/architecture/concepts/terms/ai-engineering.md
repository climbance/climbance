# AI engineering terms

Words this project gives its own meaning for the practice of the AI
Engineering module beyond its questions. Every file in `docs/architecture/`
uses them without redefining them.

## Patterns and activities

- **Pattern**: one way of building a system on a fixed model, such as
  retrieval or tool use. Each pattern is one topic of the `ai-eng` module, and
  `content/modules/ai-eng/CLAUDE.md` lists the thirteen.
- **AI activity** (activity): one kind of practice on one pattern, of one
  activity kind, with its check. `../ai-activities/patterns.md` lists them.
- **Activity kind**: the shape an activity takes, such as spotting a flaw or
  fixing a planted fault. Named apart from a template's form, which is a
  different thing.
- **AI drill**: an activity answered in a minute or two on the phone, by a tap,
  a choice or a number, with no code typed.
- **Drill item**: one AI drill as a queue serves it: an artefact, clean or
  carrying one variant, its key and the witness run proving the key.
  `../../content-repo/ai-drills.md` gives each kind's record.
- **Scripted environment**: code offering an agent tools whose results depend
  only on their arguments and its state, and a goal predicate over the final
  state. A trace is replayed against one.
- **Desk task**: an activity answered with code or a dataset at the desk, and
  scored by the harness running it.
- **Harness**: the code that runs a learner's submission on a hidden set and
  scores it.
- **Variant**: a copy of a working component with one planted fault, written
  by the engine and stored with the activity.
- **Witness run**: the run proving an activity's key: the clean artefact and
  the faulty one on the same input, or each option measured on the same set.
- **Ablation**: rerunning a submission with one of its declared stages
  removed, to measure what the stage adds.
- **Spine**: the activities the first sittings open with, one path through the
  patterns a new learner meets first.

## The readiness bar

- **Readiness bar**: the measured state of having learned AI engineering:
  every step of its version held. `../ai-activities/readiness-bar.md` gives
  it. A task's bar is a different thing: the threshold one task's metric must
  clear.
- **Readiness sitting**: a desk task served fresh, under a time limit, for one
  step of the readiness bar, its hidden set grading one final submission.
- **Readiness retest**: a readiness sitting of a step already passed, due 28
  days after the pass, on another fresh task.
- **Held step**: a step of the readiness bar with a pass and a passed
  readiness retest 28 days or more apart.

## AI tasks and their grading

- **AI task**: the record a desk task is served from: its statement, its
  component interface, its dataset, its metric, its bar, its slices and its
  token budget. `../ai-task-grading.md` gives it.
- **Component interface**: the functions a desk task's submission defines,
  and its declared stages with the identity of each.
- **Visible set** / **hidden set**: an AI task's cases the learner runs, and
  the cases that grade the submission and are never served.
- **Bar**: the score an AI task's metric must reach on the hidden set.
  Distinct from the readiness bar.
- **Slice**: a named group of an AI task's cases testing one difficulty.
  Its **floor** is the score the metric must reach on its cases alone.
- **Token budget**: the most tokens a submission may spend per case.
- **Reference component**: the component written with an AI task that clears
  its bar and every floor. Distinct from a problem's reference solution.
- **Baseline component**: the component written with an AI task that fails
  its bar. Distinct from a baseline test.
- **AI attempt**: a learner's submission to an AI task. An **AI grading** is
  one harness run of an AI attempt on one set.
- **Driver**: the entry process of an AI task's run, which feeds the
  component its dataset and each case's input.
- **Model gateway**: the one address the sandbox reaches in an AI task's run.
  It answers each model call and counts its tokens.
