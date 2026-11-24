# Cards and recall

A user studies one technique through its card: reads the card, starts a run,
solves the ladder's rungs and a probe, and recalls each template from memory.
This page follows the `cards-and-recall` journey in `../model.toml`. It starts
at the Cards tab, the cards page at `/cards` on the web. It ends at a card
graduated.

`../flows/starting-a-card-run.md`, `../flows/solving-a-rung.md` and
`../flows/recalling-a-template.md` give the rules of each step, and this page
cites them rather than restating them. `../api/card-states.md` gives the five
card states. Each component below is named by its id in `../model.toml`.

## 1. The cards list

- **The cards list reads the card graph by depth.** The root cards come
  first, and each depth is a section under its own heading.
  `../web-app/pages/cards/cards/README.md` gives the page, and
  `../content-repo/card-graph.md` gives depth.
- **A row names its card's technique, its card state, and the required cards
  a locked card waits on.** `card-states` derives each card state and each
  lock from the log on every read, so the list reads no stored verdict.
- **A started card's row names the next spaced check or recall the card waits
  for**, read against now as opening, open or owed. The row tells the user
  when to come back.
- **A row carries one recall mark per template once any template was
  recalled.** The marks read recalled clean, passed with hints, failed, never
  recalled, or a template no case checks.
- **A locked row still opens its card**, since a locked card reads in full.
- **Opening the list stores nothing.**

## 2. Reading a card

- **The card page at `/cards/:slug` shows the trigger, the brief and the
  templates before any run opens.** The phone's Card screen shows the same.
  `../web-app/pages/cards/card/README.md` gives the page.
- **Each template's form is hidden until the user reveals it.** The hidden
  state names how many lines the form runs to, so the user decides whether to
  try recalling the form first.
- **The ladder is listed before the start, each rung naming the templates it
  covers.** The user decides whether to start on that list of problems. A
  core template no problem covers is named on the card as a gap.
- **The card links to every subtopic paired with its technique, the primary
  module's first.** A template's panel links each subtopic the template
  cites. `../content-repo/cards-and-subtopics.md` gives both links.
- **A lesson links back to every card its subtopic pairs with.** A user
  reaches a card from the `knowledge-queue.md` journey this way, and from a
  technique's page in the `sitting.md` journey.
- **Reading a card mints nothing.** A card read and never started stays not
  started.

## 3. Starting the run

- **The press starting the run sits in a panel at the top of the web's card,
  and in the bar at the bottom of the phone's Card.** The note beside the
  press says the ladder counts from the start.
- **On a locked card the press is disabled, and the note names the required
  cards not yet met.** A user who holds those forms starts each required card
  and solves its probe, which meets the required card, as
  `../api/card-states.md` gives under Locked cards.
- **The press mints a card run through `card-runs`, carrying when the run
  began.** A ladder problem solved before this moment counts for nothing.
- **`card-runs` draws the probes at the start and stores them on the run.**
  The draw reads the technique's problems, unseen first, and never takes a
  rung. `../flows/starting-a-card-run.md` gives the draw.
- **The card now reads acquiring.** The top panel shows the ladder's
  progress, each template's recall state and the probes, with presses for the
  recall trainer and the next rung.

## 4. Solving the rungs and the probes

- **The next-rung press opens the first unsolved required rung**, else the
  first unsolved rung. A rung and a probe each open the problem's page named
  by the card, and the sitting runs as `sitting.md` follows it.
- **A rung is solved by an attempt on its problem finished after the run
  began**, whichever page served that attempt. `card-states` folds the solve
  from the attempt log, and no mark is stored on the rung.
- **A sitting ended with no submission skips its rung.** The skipped rung is
  served after the others, as `../flows/solving-a-rung.md` gives.
- **A sitting on a problem written for a template is a review of that
  template.** `template-schedule` rates it from the sitting's attempts through
  the first solve. `../api/template-schedule.md` lists which sittings count.
- **The solve of the last required rung turns the card consolidating.** Each
  template's spaced check is then read from that template's reviews.
- **A solved probe counts toward graduation, before or after the ladder is
  finished.** A consolidating card with no probe solved offers its next
  unattempted probe on the board, as `../api/pick.md` gives.

## 5. Recalling a template

- **A recall opens from a template's press on the card, from the run's recall
  press, or from the board's pick.** The page is
  `/cards/:slug/recall/:template`, and the phone's Recall screen.
  `../web-app/pages/cards/recall/README.md` gives the page.
- **`core-recall` draws the template where the user named none**, never
  recalled first, then least recently recalled. A drawn recall shows the
  trigger and withholds the title.
- **The file is blank but for the signature the cases call.** The editor
  proposes no library name, on either client.
- **The hints are two, the notes and then the form.** `core-recall` offers
  them in that order, and the recall attempt records which were taken.
- **`recall` runs the file against the template's cases**, under the runner a
  submission uses, and stores the recall attempt. A recall needs no open card
  run.
- **The result names the template, and the form is revealed on a press.**
  `template-schedule` rates the recall attempt as a review: a clean pass
  rates Good, a pass after the notes Hard, and any other outcome Again.

## 6. Judging a solution and filling a key line

- **Judging opens at `/judge` and filling at `/fill`, from the board or from
  a card.** A card's press adds `?card=` and serves that card's forms alone.
  `../web-app/pages/cards/judging/README.md` and
  `../web-app/pages/cards/key-line/README.md` give the pages.
- **`core-exercises` serves the items one at a time and reads each answer
  back.** Judging asks clean or flawed, then the wrong line. Filling asks for
  the statement the blank holds.
- **`short-exercises` stores each judgement and each fill, and decides it
  right or wrong.** The result shows the separating case for a flawed line or
  a wrong choice.
- **A short exercise moves no card state and reviews no template.**
  `../api/template-schedule.md` gives the reason, so the exercises are
  practice beside the card's path to graduation.

## 7. From consolidating to graduated

- **The spaced check opens when a template's recall probability falls to
  0.89, and is owed at 0.84.** After one Good review these are day 3 and
  day 5. The check never opens within three days of the last review.
- **The board's pick serves an owed check first, as a recall.** An owed check
  also holds back any new card, as `../api/pick.md` gives.
- **A failed check is a review rated Again, and the card stays
  consolidating.** The window is then read again from the template's new
  state.
- **The card graduates once three facts hold**: the ladder is solved, a probe
  is solved, and every template carrying cases has a recall rated Good since
  its check opened. `../api/card-states.md` gives the rule under Graduating.
- **A graduated card's templates fall due at retention 0.9.** The pick serves
  each due review, and the cards list names the earliest due recall.
- **A review rated Again on a graduated card's template lapses the card.**
  The lapsed card graduates again on recalls alone, one rated Good per lapsed
  template once its check opened.

## Where the web and the phone differ

`../core-package/screens.md` marks every screen of this journey `same`. The
differences are in layout and input.

- **The web's cards list draws the edges of the card graph in a gutter.** The
  phone, and the web below 640px, name each card's required cards on the row
  instead, since one column has no room for the gutter.
- **The phone starts the run from a bar at the bottom of Card**, and the bar
  then holds the next rung. The web holds the press in a panel at the top.
- **The phone's Recall screen types the form on the app's own keyboard**, as
  `../native-app/README.md` gives. A menu switches between the card's
  templates on both clients.
- **The phone reads the cards from the engine and keeps no copy.** With no
  connection, the Cards tab and each screen under it say so, as the
  `phone-offline.md` journey follows.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| Opening the list, a card or a subtopic link | nothing | none |
| The start press | a card run, with when it began and its probes | `card-states`, for every state and for met; `pick`, for the next rung or probe; `short-exercises`, drawing from started cards first |
| A rung's or a probe's sitting | a sitting and its attempts, as `sitting.md` gives | `card-states`, for solved and skipped rungs and a solved probe; `template-schedule`, as a review of the problem's target template |
| A recall | a recall attempt, with its hints and its cases' outcome | `template-schedule`, as a review; `card-states`, for graduation and a lapse; `core-recall`, for the next draw; the cards list's recall marks |
| A judgement | a judgement | the board's two rates per technique; the next item's draw |
| A fill | a fill | the next item's draw |

`failure-diagnosed.md` follows a failed sitting into a recall the pick serves.

## Open questions

- **Does the cards list name graduated and lapsed yet?** The page file says
  a started card's row names its next check or due recall. The wireframe says
  graduated and lapsed appear only once the scheduler adds them.
- **Does the user learn that an early recall delays the spaced check?** A
  recall is a review, and the check never opens within three days of the last
  review. No page file says the card tells a user recalling daily that
  graduation moves away.
- **How does a card graduate once its probes all went unsolved?**
  Graduation needs a solved probe. `../flows/starting-a-card-run.md` defers
  how many probes a start draws and when a run is given another.
- **Which press on a card opens judging or filling?** The judging page says
  a card's press adds `?card=`. The card page file and its wireframes name no
  such press.
