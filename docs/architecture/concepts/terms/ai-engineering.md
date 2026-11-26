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
