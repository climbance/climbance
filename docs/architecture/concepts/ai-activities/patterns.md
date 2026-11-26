# AI engineering activities per pattern

Each pattern of the `ai-eng` topic map has its AI drills and its desk tasks
below. [`README.md`](README.md) gives each activity kind and its rule, and
the Kind column names each kind by the first words of its name there. A
check names the witness run proving the key. A row marked with a spine step
number belongs to the spine, and the spine's order is at the end.

Each activity opens with the subtopic it names. An activity naming no
subtopic opens with the pattern's last subtopic, which teaches the pattern's
eval.

## Tier 1

**Structured prompting and output** (`prompting`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| Tokens and cost of a stated prompt and answer (`tokens-context`) | Estimate | The stated tokenizer and price | 1 |
| Data pasted into the instructions without delimiters (`prompt-structure`) | Spot the flaw | A stored response following an instruction inside the data | 2 |
| An example copied into the answer (`few-shot`) | Spot the flaw | Stored responses repeating the example's value | |
| A parser accepting an answer outside the schema (`structured-output`) | Spot the flaw | The schema validator run on the stored answer | |
| An extractor reaching a schema-valid rate under a token budget (`structured-output`) | Hit the bar under a budget | The harness's validator and token count | 3 |

**Extraction and classification** (`extraction`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| A label set with no `other` label (`classification-prompts`) | Spot the flaw | Stored labels forcing an out-of-set input into a wrong label | |
| A stated self-confidence used as a threshold (`confidence`) | Choose the fix | Agreement across stored samples separating right from wrong | |
| Accuracy or F1 on imbalanced labels | Pick the metric | Both metrics computed on the two systems' outputs | |
| A field extractor answering absent fields as absent | Build a component | Per-field precision and recall on the hidden set | |

**Retrieval** (`retrieval`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| Vectors compared without normalisation, or from two models (`embeddings`) | Spot the flaw | The ranking computed both ways on the stored vectors | |
| A chunker with no overlap splitting the answer (`chunking`) | Fix a planted fault | Recall at k on the hidden set | 6 |
| A retriever clearing recall at k (`vector-index`) | Build a component | Recall at k and mean reciprocal rank on the hidden set | 7 |
| Rerank or not, at a stated cost per query (`reranking`) | A runnable design decision | Both designs measured on the hidden set at landing | 8 |
| An answer citing text it was not given (`grounded-answers`) | Spot the flaw | The cited span searched for in the retrieved text | |

**Chaining** (`chaining`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| End-to-end success from per-step error rates (`error-compounding`) | Estimate | The product of the stated rates | |
| A step whose output is read unchecked (`step-gates`) | Spot the flaw | A stored malformed output reaching the next step | |
| Per-step evals naming the failing step | Write the eval set | Each variant broken at one step, and the step the eval names | |

**Routing** (`routing`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| Cost saved by sending easy inputs to a smaller model (`model-routing`) | Estimate | The stated share of easy inputs and the two prices | |
| A fallback that never fires on a refusal (`fallbacks`) | Spot the flaw | A stored refusal passing the check | |
| A router reaching the quality bar under a budget | Hit the bar under a budget | Routing accuracy, end quality and the harness's token count | |

**Tool use** (`tool-use`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| Two tools whose descriptions overlap (`tool-definitions`) | Spot the flaw | Stored calls choosing the wrong tool | |
| A tool error raised instead of returned to the model (`tool-errors`) | Fix a planted fault | The loop finishing on the cases with a failing call | |
| Tool-selection and argument correctness | Write the eval set | Variants with a wrong description or a wrong schema | |

**Agents** (`agents`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| The first wrong step of a failed run (`agent-failures`) | Read an agent's trace | The trace replayed with the step corrected | 5 |
| A loop with no step budget (`agent-loop`) | Spot the flaw | A scripted environment the loop never leaves | |
| Success on every one of k tries or on any one | Pick the metric | Both rates computed on stored runs of two agents | |
| An agent finishing tasks in a scripted environment | Build a component | The environment's goal state on the hidden tasks | |

## Tier 2

**Evaluator and optimiser loops** (`refinement`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| A loop oscillating between two answers (`loop-stopping`) | Read an agent's trace | The stored rounds repeating a version | |
| One call or a refinement loop, at equal cost | A runnable design decision | Both designs measured on the hidden set | |

**Evals** (`evals`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| Cases needed for a stated margin of error (`eval-sets`) | Estimate | The binomial interval at the stated rate | |
| Exact match, a reference answer or a rubric, for a stated answer (`metrics`) | Pick the metric | Each metric computed on two systems' stored answers | 4 |
| A grader preferring the longer answer (`model-graders`) | Spot the flaw | Stored grades against human labels, split by length | |
| A test case copied into a prompt's examples (`leakage`) | Spot the flaw | The case's text found in the prompt | |
| An eval set catching a classifier's broken variants (`eval-sets`) | Write the eval set | The variants failed, with the clean component passing | 4 |
| A design review of an eval with planted flaws | A design review | Each flaw's witness run on the eval | |

**Guardrails** (`guardrails`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| An instruction inside a retrieved document (`prompt-injection`) | Spot the flaw | A stored run calling the canary tool | |
| An agent holding a tool it does not need (`least-privilege`) | A design review | The attack reaching that tool in the environment | |
| An agent defended against an adversarial set | Defend an agent | Attack success and false refusal, from the environment's log | |

**Caching and context management** (`context`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| A timestamp placed before the stable prefix (`prompt-caching`) | Spot the flaw | The prefixes of two requests compared | |
| Cost saved by a cache hit rate (`prompt-caching`) | Estimate | The stated rate and the two prices | |
| Retrieve or send the whole document (`long-context`) | A runnable design decision | Both designs measured on the hidden set | |

**Fine-tuning as a choice** (`fine-tuning`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| Tune, prompt or retrieve, for a stated need (`when-to-tune`) | A runnable design decision | The prompted and the retrieving designs measured; the tuned one from stored results | |
| A held-out split drawn after deduplication or before (`training-examples`) | Spot the flaw | The duplicates found across the split | |

**Monitoring in production** (`monitoring`).

| Activity | Kind | Check | Spine |
|---|---|---|---|
| The call that made a trace slow or costly (`tracing`) | Read an agent's trace | The stored per-call latency and tokens | |
| A model name with no pinned version (`drift`) | A design review | Two stored builds answering one case differently | |
| An online eval raising an alert on a planted regression | Write the eval set | The alert firing on the regressed traffic and not on the clean | |

## The spine

The first sittings open with eight activities, in this order. The spine
follows the needs in `graph.toml`: `prompting` first, then the eval thread,
which opens after `prompt-structure`, then retrieval. Retrieval is the first
desk task the engine generates, so the spine reaches it by step 6.

1. Estimate the tokens and cost of a prompt.
2. Spot data pasted into the instructions without delimiters.
3. Build an extractor to a schema-valid rate under a token budget.
4. Pick the metric for a stated answer, then write the eval set that catches
   a classifier's broken variants. The two activities share step 4, since the
   second applies the first.
5. Read an agent's trace for its first wrong step. The trace drill comes
   early because a trace is the evidence every later desk task's failure is
   read from.
6. Fix a chunker with no overlap.
7. Build a retriever to a recall bar.
8. Decide whether to rerank, with the reranker's stage graded for simplicity.

Step 5 reads a trace before the `agents` pattern opens. The trace drill names
only the step, so it needs `tool-call-loop` alone. The edge is deferred to
the first trace items, which show whether a learner without `agent-loop`
reads them.
