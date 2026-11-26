# AI task grading

An AI task is the record a desk task is served from: the AI engineering
counterpart of a problem. This file gives the AI task record, how the harness
grades a submission, why a regrade gives the same score, and where the
harness ends and the sandbox begins. The last section works the design
through on retrieval.

`ai-activities/README.md` gives the desk task kinds this record serves. The
flow that writes and lands an AI task is in `../flows/`, and the landing gate
is defined there. The model the sandbox reaches is chosen in
`../sandbox/README.md`. This file states what grading requires of both.

## The AI task record

An `AITask` is written by the engine and never edited. Only its status moves,
as a problem's does.

- **Its pattern, its desk task kind and its statement.** The statement is the
  prose a learner is served, and it carries the component interface.
- **The component interface**: the functions a submission defines, their
  signatures, and the declared stages with the identity of each. Ablation
  replaces a stage by its identity, as `ai-activities/README.md` gives.
- **The dataset**: the material the component works over, such as a document
  corpus, and the cases. Each case is an input, its expected answer and its
  slice. An `AITaskCase` stores one, and is appended to and never revised.
- **Each case is in the visible set or the hidden set, fixed at landing.** The
  learner reads and runs the visible set. The hidden set grades the
  submission, and no API response carries a hidden case's input or expected
  answer.
- **The metric**, named from the harness's fixed list with its parameters,
  such as recall at k with k = 5. A metric is code in the harness. A task
  cannot define a metric of its own, since a metric written with the task
  would be checked by nothing.
- **The bar**: the score the metric must reach on the whole hidden set.
- **The slices and each slice's floor.** A slice is a named group of cases
  testing one difficulty, such as a query sharing no keyword with its
  document. `typical` holds the cases testing none. Each slice has a floor:
  the score the metric must reach on that slice's cases alone.
- **The token budget**: the most tokens a submission may spend per case, and
  per indexing pass where the interface has one.
- **The reference component and the baseline component**, each with its
  grading on both sets. Each kind that plants a fault also stores its
  variants, as `terms/ai-engineering.md` defines them.
- **The model configuration** every model call in grading is answered by,
  stored whole as a machine record's configuration is.

## The reference component and the baseline component

- **The reference component clears the bar and every slice's floor on the
  hidden set, within the token budget.** It shows the task can be passed by
  a component written to the interface.
- **The baseline component fails the bar, and fails at least one slice's
  floor.** It is the approach a learner who has not learned the pattern
  writes. A task that the baseline passes measures nothing the pattern adds.
- **The bar and the floors are set between the two components' scores.** The
  margin each must keep from both scores is the landing gate's to set. A
  margin inside the hidden set's noise would let luck decide a pass.
- **The reference component is not served before the learner's final
  grading.** It is shown after, beside the learner's slice scores, as the
  separating case is shown after a judgement.

## Grading

- **The harness calls the component from outside it.** The component runs in
  the sandbox and answers the inputs it is sent. The harness computes the
  metric outside the sandbox from the answers and the expected answers.
- **The expected answers never enter the sandbox.** The runner keeps
  comparison outside itself for the same reason, as `../api/runner.md`
  gives. A component that could read the expected answers could return them.
- **An `AIAttempt` stores one submission**: its learner, its task, its
  sitting, its code and when it was submitted. It is private and
  append-only, as an attempt is.
- **An `AIGrading` stores one harness run of one AI attempt on one set**: the
  score on the whole set, each slice's score, the tokens per case, the
  ablation's result per declared stage, and the slices under their floors.
- **A submission passes when the hidden score reaches the bar, every slice
  reaches its floor, and no case exceeds the token budget.** A case over the
  budget is scored as a wrong answer, and the case's tokens are recorded.
- **A hidden grading names the slices under their floors, and no hidden
  case.** Per-case results on the hidden set would let a learner fit the
  hidden set by trial. The visible set reports each case's answer, expected
  answer and tokens.
- **Each sitting allows a stated number of hidden gradings.** A readiness
  sitting allows one, as `ai-activities/readiness-bar.md` gives. The number
  for a practice sitting is deferred to the first retrieval sittings.

## A regrade gives the same score

The same submission, graded twice on the same set, gets the same score to the
last digit. A score that moves between two gradings cannot decide a pass at
its bar.

- **Every model call in grading gets the same response to the same request.**
  The model access must give identical response bytes for identical request
  bytes. The sandbox's model access is chosen to meet that rule, and this
  file only states it.
- **The harness fixes every other source of variation.** The cases are sent
  in a fixed order. The interface passes the component a seed, and the
  harness sets `PYTHONHASHSEED`. The run holds one CPU, as every sandbox run
  does.
- **Time enters no score.** Tokens are counted, and wall clock is only a cap
  set far above the reference component's time. A latency measured under
  contention would differ between two gradings.
- **Landing grades the reference component and the baseline component twice
  each, and requires identical scores.** A task whose regrade differed does
  not land.
- **A change to the harness or to the model access regrades every landed
  task's reference component.** A stored score that the regrade does not
  reproduce marks the task for the author, and the claim re-verification rule
  in the authoring docs decides its retirement.

## The harness's boundary with the sandbox

- **The sandbox runs the learner's code and the driver.** The driver is the
  entry process of an AI task's run. It loads the component, passes it the
  dataset, then sends it each case's input in order and prints each answer.
- **One container holds the whole grading.** A component builds its index
  once and answers every case from it, so a child per case, as a problem's
  run forks, would rebuild the index per case. Caching across cases is
  allowed, since the cases share one dataset by design.
- **The AI task image is its own image, named by digest.** It carries the
  libraries the interface allows, such as a numeric library and a vector
  index, and no engine code. The broker starts it with the same fixed flags
  as the submission image.
- **The sandbox reaches one address: the model gateway.** The gateway runs
  outside the sandbox, answers every model call from the chosen model
  access, counts each case's tokens and refuses a call over the budget.
  Every other address stays unreachable, as for a problem's run.
- **The harness is a package of its own, importing no engine code.** The
  published grader is that package. A grader that imported the engine could
  not be published apart from it.
- **An AI grading is admitted by the broker as any run is.** A grading runs
  for minutes where a problem's run takes seconds. A queue of its own is
  deferred until the first gradings' durations are measured.

## Worked through on retrieval

A retrieval task asks for a retriever over a stated corpus of documents.

- **The interface is `index(documents, seed)` and `retrieve(query, k)`.**
  `retrieve` returns up to k document ids, best first. The declared stages
  are rewriting the query, retrieving and reranking. Rewriting's identity
  returns the query unchanged, and reranking's returns the candidates in
  their order.
- **The metric is recall at 5 over each query's relevant documents.** Mean
  reciprocal rank is reported beside it and decides nothing.
- **The slices are five.** `typical` holds the plain queries. A `paraphrase`
  query shares no keyword with its document. An `identifier` query names an
  exact code or name, which keyword search finds. A `distractor` case has a
  near-duplicate document holding a different fact. A `split` case has its
  answer spanning a chunk boundary.
- **The baseline component** chunks without overlap and searches by vector
  alone. It fails the `identifier` and `split` floors. **The reference
  component** chunks with overlap, merges keyword and vector rankings, and
  reranks. It clears every floor.
- **The token budget** counts the embedding tokens of indexing and the
  embedding and reranking tokens per query. A reranker run on a hundred
  candidates per query exceeds it, so the budget makes reranking a choice.
- **The hidden set's size is deferred.** A hidden set of 200 queries puts a
  recall near 0.8 within about ±0.06 at 95%, and a slice of 40 within about
  ±0.12. The first retrieval tasks' measured margins between the two
  components show whether those widths are narrow enough.
