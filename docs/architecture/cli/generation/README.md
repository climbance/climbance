# Generation

`climb generate` writes the corpus: each problem, the test cases that decide
it, and the solutions written for it. The flow that writes them, site by site,
is still in `../../flows.md` `## Generating a problem`, until `split-flows-doc`
moves it here.

| File | Holds |
|---|---|
| [`problem.md`](problem.md) | The problem record: its target, its techniques, its statement |
| [`test-cases.md`](test-cases.md) | The test cases, where each came from, and the separating case |
| [`solutions.md`](solutions.md) | The canonical, the reference and the naive solution |
| [`site-outcomes.md`](site-outcomes.md) | What each call site left on one writing |
| [`verification-runs.md`](verification-runs.md) | A run of a solution against a problem's cases |
