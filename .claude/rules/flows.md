---
paths:
  - "src/climb/generation/**"
  - "src/climb/mutation/**"
  - "src/climb/drafts/**"
  - "src/climb/eval/**"
  - "src/climb/sitting.py"
  - "src/climb/recall.py"
  - "src/climb/runs.py"
---

Read the flow this code takes part in before changing it.
`docs/architecture/flows/` gives the drill loop, starting a card run, solving a
rung and recalling a template, a page each. `docs/architecture/cli/generation/`
gives generation, its writing states and replay, and
`docs/architecture/cli/eval-set.md` gives adjudication. They win over the code
on any difference.
