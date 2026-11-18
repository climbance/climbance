# Problem

A problem is a statement, its test cases and its solutions, written by the
engine. This file gives the problem record as generation writes it at landing.
`../../api/problems.md` gives how a landed problem is served and retired.

## The target

- **Generated, and that is the only origin.** The engine writes a statement,
  the test cases that decide it, a canonical solution and a reference
  solution.
- **A problem is written for a target: what it must be solvable by.** A
  template is the tightest kind, naming the exact form. A technique is a looser
  one, naming only the skill. Each kind produces a problem. A template target
  and a technique target differ in what the generator knew, and not in how the
  problem is judged.
- **The looser target reaches the rest of the vocabulary.** A paradigm and a
  problem class have no form to reproduce, so no template names them, and a
  corpus written from templates alone can never exercise them.
- **The technique target is deferred until a card's selector names a
  technique the template-aimed corpus cannot fill.** Generation writes for a
  template target alone today, and no writer sets `target_technique`.
- **The target is stored on the problem.** `target_template_id` or
  `target_technique` records what the generator was told rather than what a
  model inferred. The template arm makes the first template match provenance.
  No arm claims the problem exercises nothing else.
- **A technique target asserts no template match and no technique.** The
  generator was told no form, so the matcher alone says which forms the
  canonical displays. The target says what the generator was asked for, and
  only a solution claim says what the canonical used.

## The record

- **Provenance is required.** A problem names what produced it, as any machine
  record does.
- **A problem's techniques are the union of the standing solution claims of
  its canonicals**, a view rather than stored truth. Adding a canonical can
  widen the set, and re-deriving is legal and expected. The reference and the
  naive solution are excluded, or the approach a form replaces would be
  credited to the problem. A canonical that sorts before it searches used two
  techniques, and only a solution claim names the second.
- **Never derived from templates or from the target.** A paradigm and a
  problem class have no form to type out, so templates reach about half the
  vocabulary, and a set folded from them would be capped by which cards exist.
- **The statement is stored, because a solver is served it.** A matcher also
  reads the statement beside the canonical it classifies. Required and
  non-blank.
- **Whether a statement gives its form away is not checked.** A statement can
  name its approach, or reuse the example its template's trigger names, and a
  solver who recognises the problem has not derived the form. A gate over the
  corpus for this is deferred. It needs
  a corpus to measure and a baseline no generator wrote, and a status the gate
  promotes to is an additive change when it comes.
- **A statement's example and cases are the engine's own.** The generator's
  prompt forbids reusing the example, the values or the wording of a published
  problem. A published question retold in the engine's own words is accepted.
  The screen site rejects a copy, and `../../flows.md` gives where it runs. The
  screen answers from the model's memory, since no repo may hold a published
  example to compare against.
