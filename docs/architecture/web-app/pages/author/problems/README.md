# The problems page

The page at `/author/problems`, in the author area: every problem in the
corpus, served or retired, each opened with its solutions and its cases.
`../README.md` gives who reaches it, and `## The content browser` there gives
the rules this page shares with the other browser pages.
`../../../../cli/generation/problem.md` gives the problem.

[`problems.md`](problems.md) draws the page at low fidelity.

The author comes to this page to review problems: the batch the last
generation run landed, the problems an attention flag names, and the
problems a learner asked to retire. The layout serves that review. The rows
read one line each so a window holds about 25, and an opened problem reads in
a dialog over them.

## Where it reads from

- **The problems are read from `/api/author/problems`**, over the corpus of
  the engine serving the page. Problems are product data kept in the store,
  not in git, so the hosted engine's corpus is readable from this page alone.
  Each listed problem carries its attention flags, computed on the server.
- **An opened problem reads `/api/author/problems/:id`**, one problem at a
  time. A case may weigh up to the ceiling, so the list carries no case and no
  solution's code.
- **The opened problem carries each case cut on the server.** Each case's
  arguments and expected return are sent as one line of compact JSON, cut at
  120 characters, with the case's full size in bytes. One local problem
  weighed 411 KB for 13 whole cases, and the cut keeps a response under 50 KB.
  A case of 1 KB or more names its size in its row.
- **A pressed case reads `/api/author/problems/:id/cases/:case`**, the case
  whole. Only the case the author asked for is sent at full weight.

## Filters

- **The filters sit on one line above the rows**: status, technique, target,
  difficulty, landed, and the attention flags. A filter reads as a menu
  naming its current value. Chips for 29 techniques took a third of the
  window, above the first row.
- **Each filter is in the URL**: `?status=`, `?reason=`, `?technique=`,
  `?template=`, `?difficulty=`, `?landed=`, `?flag=` and `?sort=`. A card's
  ladder links here with `?template=`, so every problem written for one form
  is one link.
- **Each menu option counts the rows picking it would leave.** An option
  leaving no row reads greyed and stays in the menu. `hard` reads greyed on
  today's corpus: no judge score lies above 1567, and the hard band starts at
  1900, as `../../../../cli/difficulty/README.md` gives.
- **The technique and the target menus carry a search field.** The corpus
  targets over a hundred templates, and the search reaches any of them
  without a row of chips.
- **The status reads `served` until the author picks `retired`.** The
  retirement reasons, `defective` and `copied`, are offered as `?reason=`
  only once `retired` is picked. A reason divides the retired problems, so
  offering it beside `served` read as a third status.
- **The landed filter reads `any`, `1d`, `7d` or `30d`.** After a generation
  run, `1d` lists the batch it landed. A problem record stores no time, so a
  problem is dated by its first solution's `created_at`, which landing
  writes.
- **`Needs attention` sets `?flag=any`**, and names how many rows carry a
  flag. A single flag's name narrows the rows to that flag.
- **The rows read newest first by default.** `?sort=score` and `?sort=cases`
  order them by the standing score or the count of cases, highest first.

## Attention flags

A flag names a property of a problem worth a look before a learner meets
it. A flag is computed on every read and never stored. A flag only points:
the author decides, and no flag retires a problem.

- **`untagged`**: the problem's techniques are empty. The board credits an
  attempt on it to no technique when no claim covers the attempt.
- **`titled`**: the title holds a technique's name, its slug's words in order
  with case ignored, such as `Sliding Window` for `sliding-window`. The
  listing shows the title, so the title names the approach before the
  statement does.
- **`unrated`**: the problem's standing difficulty carries no score. A cold
  sitting cannot serve it, as `../../../../api/rating.md` gives.
- **`off-band`**: the standing score lies more than its deviation outside the
  band of the generator's `difficulty`. A `user` rating stores no deviation,
  and is read as deviation zero. The generator aimed at one label and the
  judge read another, so the statement or the label is wrong.
- **`requested`**: a retirement request waits on the problem.

## Rows

- **A closed row reads on one line**: the title, the target, the techniques,
  the standing score with its deviation and its label, the count of cases, and
  the flags. A retired row names its reason in place of the flags. In a narrow
  window a row wraps to two lines.
- **The title leads the row, and the id is read in the dialog.** The author
  scans titles and flags. The id's prefix is needed only for a command.
- **The solutions by role read in the dialog alone.** A problem written for a
  template with no speedup lands with no naive solution, as
  `../../../../cli/generation/states.md` gives, so the roles differ by target
  and not by fault.

## The dialog

- **A press on a row opens the problem in a dialog over the list.** The
  dialog leaves a margin of 1.5rem around it in a wide window, and fills a
  window under 64rem. The list underneath keeps its full rows and its
  scroll. A panel beside the list, tried first, narrowed the list to titles
  cut at 20 characters and left the panel 38rem, too narrow to set the
  statement beside a solution.
- **One problem is opened at a time, and the anchor names it.** The page's
  anchor is then a link to exactly the problem in view, and a reload or a
  pasted link opens the same dialog.
- **The dialog reads in two columns in a window of 64rem or more.** The
  statement reads on the left. The solutions, the cases, the difficulty and
  the site outcomes read on the right, each column scrolling on its own. The
  author checks the canonical against the statement, so the two read side by
  side. A narrower window stacks the columns, as `../../../README.md` gives
  for two parts of one page.
- **`j` and `k` step the dialog to the next and the previous row, and the
  head reads the position, such as `5 of 133`.** The dialog stays open, and
  the anchor in the URL follows. Reviewing a batch of 20 problems is then 20
  presses of one key. Two buttons in the head step the same way.
- **Escape, the close button or a press outside closes the dialog**, and
  clears the anchor. The list then shows the row last opened, marked, so the
  author resumes the scan from it.

## The opened problem

The dialog reads the head, then the statement in the left column, then
the solutions, the cases, the difficulty and the site outcomes in the right
one, then the foot.

- **The dialog's head names the problem**: its title, the first eight
  characters of its id, its status and its flags. A press on the id copies
  it.
- **The head names the configuration that wrote the problem**: the model,
  the effort, the temperature, the prompt hash and the pin. A temperature
  nobody set reads `default`. A resume compares the configuration and the
  prompt hash, so the author can see which bench wrote a problem judged weak.
- **The dialog draws the statement with the sitting's own component**, as a
  learner is served it. The author reviews the exact text a solver reads.
- **Each solution reads by role: the canonical, the reference, then the
  naive**, with its code, its latest verification and the configuration that
  wrote it, read as the head reads the problem's. A canonical names the
  templates it displays, from the standing template matches, and the
  techniques its standing solution claim names.
- **The cases read in the order they were appended**, each argument and the
  expected return cut to one line. A won case names the round that won it,
  and a case calling `solve` more than once names its repeat count. A press
  shows one case whole.
- **The difficulty reads as each rating's score and deviation, latest first**,
  with the standing one marked and the generator's label beside them. The
  author then sees how the served score was reached.
- **The site outcomes read after the difficulty, in the order written**: each
  site's name and model, the gate and its detail where one rejected the
  site's answer, and each counter that is not zero. The separating size reads
  with its repeat count, and the bound beside it. A separating size read
  without the bound says nothing about how far the search had left to look.
  A resumed step writes a second outcome, so a site can read twice. A problem
  landed before site outcomes were stored reads `no site outcome`.
- **The dialog names the retirement requests the problem carries**, each with
  its reason and note, and links them to the inbox.
- **The dialog's foot copies the commands acting on the problem**: retiring it
  as `defective`, retiring it as `copied`, and rating it by hand, each as
  `climb problem` takes it. The page writes nothing, as `../README.md` gives.
  Each command names the full id, so it cannot match a second problem. The
  rating command ends in the standing score, rounded, for the author to edit
  before running it, and an unrated problem's command ends where the score is
  typed. A retired problem's foot offers the rating alone, since `climb
  problem --retire` refuses a problem already retired.
