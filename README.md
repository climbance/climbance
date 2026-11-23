# Climbance

Climbance is a platform for the deliberate practice of algorithmic problem
solving. It is built for engineers who were once fluent and want their speed,
their recognition of techniques and their missing knowledge back. It covers
three kinds of practice as one system:

- **Learn**: knowledge modules of short questions, reviewed on a spaced
  schedule.
- **Drill**: short exercises and templates recalled from memory, sized for a
  phone.
- **Solve**: timed sittings on problems, judged by running the code.

The engine writes every problem it serves. Each problem carries the test cases
that decide it, and the engine runs each submission against those cases in a
sandbox. The engine contacts no external problem platform, so every verdict is
the engine's own.

The engine runs as a web app and a phone app over one learner model. Access is
by invitation.

## The method

### Practice targets techniques, not problems

A **technique** is one entry in a fixed vocabulary of skills, such as
`monotonic-stack` or `knapsack`. Each technique carries a written criterion for
when code uses it. Progress, mastery and scheduling are kept per technique,
since a problem is solved once and a technique is used across hundreds.

A **card** is the study material for one technique:

- **Trigger**: when to reach for the technique.
- **Brief**: what to read before solving.
- **Templates**: the forms of the technique, each reproduced from memory.
- **Selector**: the technique and the filters the card's problems are drawn
  by.

A card names no problem. Its **ladder** of problems is derived from the
selector and from which templates each stored solution displays. Every core
template gets a rung, so the ladder exercises every form the card teaches. A
core template no solution displays is reported as a gap.

Cards form a directed acyclic graph. A card requires another card when one of
its templates builds on a form the other card teaches. A card stays locked
until each card it requires is met.

### Mastery has three parts

The engine computes each technique's mastery from the user's log on every read
and stores none of it. Mastery has three parts, kept apart because each one
calls for a different kind of practice:

- **Recognition**: seeing that a problem needs the technique when nobody named
  it. A user weak here gets recognition drills.
- **Execution**: writing a correct solution once the technique is known. A user
  weak here gets the card's ladder and the recall trainer.
- **Knowledge**: recalling the facts the technique rests on. A user weak here
  gets the module's questions.

Execution is read as an **ability** on the contest scale, the rating scale of
public programming contests. From the ability and a problem's difficulty score,
the engine reads the user's chance to solve that problem.

### Reviews are scheduled per template

The unit of recall is the template, not the card. A card's forms are learned
and forgotten separately, and a card-level number would average them together.

FSRS, a spaced-repetition scheduler, replays each template's reviews into its
recall probability. A recall attempt is a review, and so is a sitting on a
problem written for the template. The board serves one **pick**, the next act
the schedule names:

- A recall of the template closest to being forgotten.
- A sitting on an unseen problem written for a template already learned.
- After a failed sitting, the recall of the form it missed, and then a new
  problem for that form.

Each pick stores what it expected from FSRS and from mastery before the user
acts. A later formula can therefore be scored against what an earlier formula
predicted.

### A card moves through states

A started card is **acquiring** until each required rung is solved. It is then
**consolidating** until a spaced check passes, a recall of its templates served
when their recall probability has fallen. A card that passes is **graduated**.
A graduated card **lapses** when one of its templates is later rated Again.

Reproducing a form on cue is not recognising it unprompted. Each card run
therefore assigns **probes**: unseen problems, solved with no card in view.

### Knowledge is learned by retrieval

A knowledge module holds topics and subtopics, each subtopic at four levels from
Foundation to Expert. Its questions are multiple choice, short answer, or open.
An open question is graded by the user, who ticks the points of its key they
recalled. FSRS schedules every question.

- **Gating** opens a subtopic's questions at a level once the lower levels and
  the prerequisite subtopics are done.
- **Lessons** are short texts read before a group's new questions. A pretest
  lets a few questions be met before the lesson.
- **Certifications** cover a topic or a whole module at one level. Each is
  earned on coverage, on retention over weeks and on an exam.
- **A baseline test** samples a topic's questions before its first lesson. The
  same questions come back as a delayed test four weeks or more later. The
  difference in score is the measured learning gain.

The scheduling rules live in one TypeScript package that both apps import. The
phone app therefore runs its queues offline and syncs later.

### Short exercises train the parts of a solve

- **Judging**: a template's code, clean or carrying one change that fails a
  case. The user says whether it is correct, then taps the flawed line.
- **Key line**: a template with one line blanked, and a choice between the
  form's own line and mutants of it that fail a case.

Each mutant is checked by execution before it is served, so a flawed item is
known to fail.

### Ratings are read from cold sittings

A **cold sitting** serves an unseen problem with no title, technique, card or
difficulty shown, under a time limit and with no pause. Those are the
conditions a problem's difficulty score assumes. The engine replays the user's
cold sittings with Glicko-1 into a measured rating and its deviation.

A **projected rating** reads every sitting instead, through each technique's
ability. It predicts the rating the user would reach on a contest made of one
year of rated public contest problems. Only that contest's aggregate is stored:
each problem's rating and needed techniques, and no statement.

## How a problem is written

`climb generate` writes a problem for one template across six model calls. Each
step can reject what the steps before it wrote, and a problem lands only when
every gate has passed.

1. One call writes the statement, a canonical solution and the first test
   cases. The canonical must reproduce the outputs that call declared.
2. A screen rejects a draft reusing the example, the values or the wording of a
   published problem.
3. A reference solution is written from the statement alone. The reference
   computes each case's expected return, and it must agree with the canonical
   on every case. A reference shown the canonical would inherit its reading of
   the statement. Written blind, agreement shows the statement has one
   reading.
4. A call writes code that builds an input of any size. For a template that is
   faster than the naive approach, another call writes that naive solution.
   The engine then searches for the smallest input on which the naive solution
   runs over the time cap and the canonical does not, and stores it as a case.
5. Mutants of the canonical, each one semantic change on its syntax tree, run
   against the cases and then against built inputs. A last call is asked for
   cases that kill the mutants still surviving. Only a case that killed a
   mutant is kept.

No model is asked whether the cases are good enough, since a model asked that
about its own cases says yes. The mutants measure it instead. A draft that
stops on a missing answer is held and resumes at the first step whose prompt
or model changed.

After landing, a difficulty judge reads each statement and answers the
contest rating it expects. A line fitted on external anchor problems corrects
that answer onto the contest scale. The anchors are never served, and never
stored with the corpus or in git.

## Where models sit, and the rules over them

Models write problems, read which techniques a solution used, match solutions
to card templates, judge difficulty and name why a failed solution failed. No
model is trained or fine-tuned anywhere in the engine.

- **The user's record stands over the machine's**, whichever was written
  later. A machine reading of an attempt the user already claimed is kept and
  scored, and never replaces the user's claim.
- **Every machine record carries its provenance**: the model, the effort, the
  endpoint it was pinned to, the temperature, the hash of the exact prompt and
  the call that sent it. A record whose prompt hash differs from the current
  prompt is stale and is asked again.
- **Every call is logged whole**, with its prompt, its response, its tokens
  and its timings. The call log is domain-free, so a new kind of reading
  reuses it unchanged.
- **Each reader is scored against a hand-made reference.** The classifier is
  scored against hand-claimed attempts, the matcher against a hand pass, and
  the diagnosis call against labelled mutants. Configurations are compared
  over the items every one of them read.

## Architecture

| Part | What it does |
|---|---|
| API | Python and FastAPI: serves JSON under `/api` and the web app's files, signs users in and records the log |
| Web app | Vite, React and TypeScript, built to static files |
| Phone app | React Native for Android and iOS, offline-first for the knowledge queues |
| Shared core | `packages/core`: the rules and each screen's data, imported by both apps |
| Broker | Holds the container runtime's socket and admits one run at a time |
| Sandbox | One container per run under gVisor, with no network and a read-only root |
| Postgres | The one store: the corpus, the content, every user's log and the call log |
| Command line | `climb`, run off the server: generation, the hand passes, seeding and invitations |

Sign-in goes through Google or GitHub, and the engine stores no password.
[`docs/architecture/`](docs/architecture/README.md) holds the design: each
part's boundary, the records, the invariants and the reasons behind each
choice. On any difference between the docs and the code, the docs describe the
target.

The invariants the rest depends on:

- **The log is append-only.** A user's attempts, claims, labels and answers
  are never revised in place. Erasing a user's whole log is a separate act.
- **Every reference in the log is minted by the engine**, so the log stays
  readable without anything outside the engine.
- **Aggregates are derived on read**: the board, a card's ladder and state,
  mastery and both ratings.
- **No third-party problem statement or test case is in git**, in any
  repository.

## Your data

The code and the record schema are public. Each user's log lives in Postgres
and is private to that user, who can export it or erase it. The authored cards
and knowledge modules live under `content/`, a private repository of their own
that this repository ignores.

## Running it

Requires Python 3.15, `uv`, Node with npm, `just` and a Postgres server.

```
uv sync
npm install
just migrate
just app
```

`.env` names the database in `DATABASE_URL`. For a local login without a
sign-in provider, set `CLIMB_DEV_LOGIN=local`. `just app` runs the API and the
Vite dev server together, and the page is at the address Vite prints.

```
uv run pytest      # the Python suite, integration tests need TEST_DATABASE_URL
just web-check     # the web app's type check, lint and tests
just native-test   # the shared core's and the phone app's tests
uv run climb --help
```

[`CLAUDE.md`](CLAUDE.md) holds the conventions. Enable the git hooks once with
`git config core.hooksPath .githooks`.

## Where things are

```
src/climb/         the engine: the API, the command line, generation, the log
packages/core/     the rules and screen data both apps share
packages/editor/   the code editor setup both apps share
web/               the web app
native/            the phone app
migrations/        the store's migrations
deploy/            the image's compose file and its proxy
docs/architecture/ the design
content/           the authored cards and modules, a private repository
```

## Licence

Apache-2.0, in [`LICENSE`](LICENSE).
