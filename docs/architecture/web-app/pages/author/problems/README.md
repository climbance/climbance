# The problems page

The page at `/author/problems`, in the author area: every problem in the
corpus, served or retired, each opened with its solutions and its cases.
`../README.md` gives who reaches it, and `## The content browser` there gives
the rules this page shares with the other browser pages.
`../../../../cli/generation/problem.md` gives the problem.

[`problems.md`](problems.md) draws the page at low fidelity.

## Where it reads from

- **The problems are read from `/api/author/problems`**, over the corpus of
  the engine serving the page. Problems are product data kept in the store,
  not in git, so the hosted engine's corpus is readable from this page alone.
- **An opened row reads `/api/author/problems/:id`**, one problem at a time. A
  case may weigh up to the ceiling, so the list carries no case and no
  solution's code.

## Filters

- **The page filters by technique, difficulty, status and target**, as
  `?technique=`, `?difficulty=`, `?status=` and `?template=`. A card's ladder
  links here with `?template=`, so every problem written for one form is one
  link.
- **The template filter offers only the template the URL names.** The corpus
  targets over a hundred templates, and a chip for each would push the rows
  below the fold. A card's ladder and its templates link to the filter.
- **The status filter reads `served` until the author picks another**, and
  offers `retired` and every retirement reason. A retired problem stays in the
  corpus, so the author can still read why it was retired.

## Rows

- **A row shows the problem before it is opened**: the first eight characters
  of its id, its title, its target and its standing difficulty. Then it shows
  its techniques, its count of cases and its solutions by role. A retired row
  names its reason. `climb problem --retire` takes the id's prefix, as the
  workflow page's requests give it.
- **The rows read newest first.** The author reads what the last generation
  run landed first. A problem record stores no time, so a row is
  dated by its first solution's `created_at`, which landing writes.
- **The row names how many retirement requests the problem carries.** An
  opened row links the count to the workflow page's requests. A link inside
  the closed row would nest one press inside the row's own press.

## An opened row

- **An opened row draws the statement with the sitting's own component**, as
  a learner is served it. The author reviews the exact text a solver reads.
- **Each solution reads by role: the canonical, the reference, then the
  naive**, with its code and its latest verification. A canonical names the
  templates it displays, from the standing template matches, and the
  techniques its standing solution claim names.
- **The cases read in the order they were appended**, each argument and the
  expected return cut to one line. A won case names the round that won it,
  and a case calling `solve` more than once names its repeat count. A press
  shows one case whole.
- **The difficulty reads as each rating's score and deviation, latest first**,
  with the standing one marked and the generator's label beside them. The
  author then sees how the served score was reached.
