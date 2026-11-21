# Corpus terms

Words this project gives its own meaning for problems, their cases, their
solutions and their difficulty. Every file in `docs/architecture/` uses them
without redefining them.

## Problems and solutions

- **Problem**: a statement, its test cases and its solutions, written by the
  engine. Never edited. Only its status moves.
- **Statement**: the prose a solver is served. It carries the signature of
  `solve`, the fixed name of the function every solution defines.
- **Test case** (case): positional arguments and an expected return. The
  case set is every case a problem carries, appended to and never revised.
- **Target**: what a problem is written for: a template, naming the form, or a
  technique, naming only the skill. The prompt a site is given is built from
  it. Stored as `target_template_id` or `target_technique` on the problem, the
  draft and the site outcome, one of the two.
- **Canonical solution**: an exemplary solution, written to display the
  approach rather than to pass.
- **Reference solution**: a solution written from the statement alone.
  Correct, and deliberately not exemplary. It computes the expected returns.
- **Naive solution**: the approach the template's form replaces, written told
  which form to avoid. The speedup search times the canonical against it.
- **Role**: which of the three a solution is: canonical, reference or naive.
  Stored, since all three pass the same cases.
- **Solution claim**: a claim about a solution the engine wrote. Product data,
  and what a problem's techniques are folded from.
- **Defective**: a retirement reason: the statement asks for something its
  cases do not decide.
- **Enumeration**: a pass over a landed problem proposing other approaches,
  each generated as a further canonical. Deferred, as
  `../../cli/generation/solutions.md` gives.

## Verification

- **Verification**: executing a solution against a problem's cases. A
  `Verification` record stores one run, with a case outcome per case: passed,
  wrong, timed out or crashed.
- **Cap**: the wall-clock limit on a case's `solve` calls, measured in the
  child process. Generation's cap sits well above the sitting's.
- **Repeat count**: how many times a case calls `solve` on its arguments, the
  cap covering the calls together. One on every case but a separating one the
  ceiling put out of reach.

## Difficulty

- **Difficulty score** (score): a problem's difficulty as one number on the
  contest scale.
- **Contest scale**: the rating scale of the public programming contests,
  where a problem's rating is the contestant rating at which a solve is
  expected half the time.
- **Deviation**: one standard error of a score, on the contest scale.
- **Band**: the range of scores one label covers: easy, medium or hard.
- **Difficulty rating**: one judgement of a problem's score and deviation,
  written after landing, by hand or by the difficulty judge. A
  `DifficultyRating` record stores one.
- **Standing difficulty**: the score a problem is served with, its standing
  rating's, and the label of the band it falls in. With no rating, the label
  is the generator's `difficulty` and there is no score.

## The difficulty judge

- **Difficulty judge** (judge): the model call reading one problem's
  statement alone and answering the contest rating it expects. Distinct from
  the framing judge, which grades a recognition drill.
- **Draw**: one difficulty judge call on one statement, and the rating it
  answered. A `DifficultyDraw` record stores one on a corpus problem.
- **Judged rating**: the median of one problem's draws, before the
  correction.
- **Correction**: the line from the judged rating to the contest scale,
  fitted on the anchors for one judge and one prompt. A `DifficultyCorrection`
  record stores one, with the deviation its held-out anchors measured.
- **Instructions hash**: the hash of the difficulty judge's prompt with the
  statement left out, named on a correction.
- **Anchor**: an external problem whose contest rating was fitted from the
  contestants who solved it. Never served, never stored with the corpus, and
  never in git.
- **Anchor set**: the fixed list of anchors a correction is fitted on, named
  by its hash. Some of its anchors are held out of the line.

## The panel

- **Panel**: the model configurations whose trials are stored, ranging from
  weak to strong. Each configuration is a **member**. The trials check the
  judge on the corpus, and no score is read from them.
- **Trial**: one member's solution to one problem, with its verdict. A `Trial`
  record stores one. An attempt is a different thing: a user's solution.
- **Difficulty fit** (fit): one item response fit over the panel's trials,
  linked to the contest scale on the anchors. The first fit failed its metric,
  so no fit is stored and no record holds one.

## The calibration corpus

- **Calibration corpus**: the platform problems and attempts under
  `data/old/`, kept for one deferred measurement: how often a matcher names a
  form from a statement alone.
