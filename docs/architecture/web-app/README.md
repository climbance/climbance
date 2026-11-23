# Web app

The web app a user practises in: which pages it serves, how the user moves
between them, and the design system every page is built on. The native app
holds the same tree of pages, and `../core-package/screens.md` lists every
screen of both clients.

`../flows/` gives the steps of a flow and their order. The page files give
what the user sees at a step, and which page holds it. Beside each page's
`README.md`, a file per screen draws that screen at low fidelity, as
`## Wireframes` gives.

| File | Holds |
|---|---|
| [`areas.md`](areas.md) | A page's areas: the header, the body, the act, rows, panels and sections |
| [`design-system.md`](design-system.md) | The tokens, the colours, the type, code and tables |
| [`pages/shell/`](pages/shell/README.md) | The navigation, the account menu, the signed-in devices, the error screen |
| `pages/<section>/<page>/` | One page each, listed under `## The pages` |

## The structure

Both clients hold one tree of sections and pages. A platform draws the tree
its own way, and holds the same pages under the same sections.

```
Practice      the board, a technique, a picked problem, a sitting,
                a cold sitting
Problems      the listing, a picked problem
Cards         the list, a card, a recall
Knowledge     the home
                a module: its groups, its map, the start sheet
                  a subtopic
                a queue, an exam
                the lessons, a lesson
                the certifications, a certification's conditions
Account       the guide, the settings, the signed-in devices, the sign-out
Author        the product, the generation, the workflow, on the web alone
                the questions, the lessons, the cards, the problems
```

- **The four sections are the destinations both clients name.** The web
  names them in its top bar. The phone names them as bottom tabs, and shows a
  tab once the phone holds a page under it. The phone then holds a subset of
  the tree rather than a tree of its own.
- **Account sits apart from the sections on both clients.** The web opens it
  from the account menu, and the phone from its top bar. Account holds the
  guide, the settings, the signed-in devices and the sign-out, since none of
  the four is a place to practise.
- **The author area sits apart from the sections too, on the web alone.** The
  account menu opens it for a user with the author role, as
  `pages/author/README.md` gives.
- **A section's root is the only page the navigation reaches.** Every other
  page is a step down with one way back. A shortcut from the navigation to a
  page deeper in the tree would give that page two ways in, and the way back
  could name only one.
- **Each page names one way back: the page the user came from.** A rung of a
  ladder is a sitting reached from a card, and the same sitting is reached from
  the board, so the section a page sits in cannot say where the user came from.
- **The Knowledge home links its lessons and its certifications**, and a
  module row opens the module. The lessons, the certifications and every
  module are then steps down from the home on each client.
- **A module's page holds its groups and its map.** The groups read as a
  table of subtopics by level, and the map draws the prerequisite graph. The
  two are tabs of the page on both clients, since the map wants the page's
  whole width.
- **A module's focus, status and start sheet sit on the module's page.** The
  home's module row opens the module, and offers nothing else.
- **No page shows every module's groups at once.** The home names each
  module's next group and its reviews, and a module's page holds its groups.
  A page summing every module would be a second way to read the same groups.
- **The platform decides how the tree is drawn.**
  - Navigation: a top bar on the web, bottom tabs on the phone.
  - The way back: the browser's and the header's link on the web, the
    system's and the header's on the phone.
  - An overlay: a dialog on the web, a bottom sheet on the phone.
  - Two parts of one page: side by side in a wide window, stacked or tabbed in
    a narrow one.

## The pages

`../core-package/knowledge/` gives the rules each knowledge page applies, and
`packages/core` computes every label and count the knowledge pages show.

| URL | The user | Section | File |
|---|---|---|---|
| `/` | continues a card or picks a technique | Practice | [`practice/board`](pages/practice/board/README.md) |
| `/start` | reads what each kind of practice trains | none | [`practice/guide`](pages/practice/guide/README.md) |
| `/problems` | picks a problem across every technique | Problems | [`problems/listing`](pages/problems/listing/README.md) |
| `/techniques/:technique` | picks a problem | Practice | [`practice/technique`](pages/practice/technique/README.md) |
| `/problems/:problem_id` | reads the statement, solves, submits and claims, or reads a retired problem | Practice | [`problems/problem`](pages/problems/problem/README.md) |
| `/cold/:sitting_id` | solves an unseen problem with nothing named, under a time limit | Practice | [`practice/cold`](pages/practice/cold/README.md) |
| `/judge` | judges one solution at a time, clean or flawed, and taps the wrong line | Practice | [`cards/judging`](pages/cards/judging/README.md) |
| `/fill` | picks the line a form's blank needs, one form at a time | Practice | [`cards/key-line`](pages/cards/key-line/README.md) |
| `/cards` | reads where each card stands, and picks one | Cards | [`cards/cards`](pages/cards/cards/README.md) |
| `/cards/:slug` | reads a card and reveals its templates | Cards | [`cards/card`](pages/cards/card/README.md) |
| `/cards/:slug/recall` | opens the recall of the template the trainer draws | Cards | [`cards/recall`](pages/cards/recall/README.md) |
| `/cards/:slug/recall/:template` | reproduces one template from memory | Cards | [`cards/recall`](pages/cards/recall/README.md) |
| `/knowledge` | continues the next queue, or picks another way in | Knowledge | [`knowledge/home`](pages/knowledge/home/README.md) |
| `/knowledge/modules/:module` | reads where each group stands, aims the focus, and starts a filtered queue | Knowledge | [`knowledge/module`](pages/knowledge/module/README.md) |
| `/knowledge/modules/:module/:sub` | reads a subtopic's levels, its lessons and the cards it supports | Knowledge | [`knowledge/subtopic`](pages/knowledge/subtopic/README.md) |
| `/knowledge/queue` | answers one question at a time | Knowledge | [`knowledge/queue`](pages/knowledge/queue/README.md) |
| `/knowledge/exam` | picks a level exam or a certification's, and takes it | Knowledge | [`knowledge/exam`](pages/knowledge/exam/README.md) |
| `/knowledge/lessons` | picks a lesson | Knowledge | [`knowledge/lessons`](pages/knowledge/lessons/README.md) |
| `/knowledge/lessons/:module/:lesson` | reads a lesson and marks it read | Knowledge | [`knowledge/lesson`](pages/knowledge/lesson/README.md) |
| `/knowledge/certifications` | reads where each certification stands | Knowledge | [`knowledge/certifications`](pages/knowledge/certifications/README.md) |
| `/settings` | reads the account, sets the daily limit and the exam size, syncs, restores an archived module, sends feedback, exports the record and deletes the account | none | [`settings`](pages/settings/README.md) |
| `/login` | signs in | none | [`login`](pages/login/README.md) |
| `/privacy` | reads the privacy policy | none | [`privacy`](pages/privacy/README.md) |
| `/terms` | reads the terms of use | none | [`terms`](pages/terms/README.md) |
| any other path | reads that no page is there | none | [`not-found`](pages/not-found/README.md) |
| `/gallery` | reads the design system, in development alone | none | [`gallery`](pages/gallery/README.md) |
| `/author` | opens an author page, with the author role alone | none | [`author`](pages/author/README.md) |
| `/author/product` | reads the learners, the acts per day and the retention | none | [`author/product`](pages/author/product/README.md) |
| `/author/generation` | reads the drafts, the landing rate, the spend per landed problem and the corpus | none | [`author/generation`](pages/author/generation/README.md) |
| `/author/workflow` | reads the by-hand passes, the requests, the feedback, the run faults and the spend | none | [`author/workflow`](pages/author/workflow/README.md) |
| `/author/questions` | reads one module's questions at once, each as answered | none | [`author/questions`](pages/author/questions/README.md) |
| `/author/lessons` | reads one module's lessons, each whole | none | [`author/lessons`](pages/author/lessons/README.md) |
| `/author/cards` | reads every card, its templates revealed | none | [`author/cards`](pages/author/cards/README.md) |
| `/author/problems` | reads every problem, served or retired, with its solutions and cases | none | [`author/problems`](pages/author/problems/README.md) |

## Paths

- **A page's path names the record the page serves**, so a reload reaches the
  same page. `../api/README.md` gives how the server answers a path naming no
  file.
- **A page loads the record its path names.** The picked problem is read as its
  own record rather than found in the technique's candidates, since a page
  reached from two places would otherwise load a different list at each of
  them.

## What the browser keeps

- **A problem's unsent code, the clock preference and the chosen colour scheme
  are the state the browser keeps.** The code is stored under the problem's id
  with the moment it was typed, so a reload restores what the user typed, and
  the next sitting on the problem can carry it as `../flows/drill-loop.md`
  gives. The clock preference and the scheme are about how the user practises at
  this machine, and a store holding them would carry them between machines
  nobody asked it to join. Every other reading is fetched from the API at each
  load.
- **The unsent code is keyed to the signed-in user, and signing out deletes
  it.** A browser can be shared between two accounts. The code a user has not
  submitted is that user's own, and the next account to sign in must not open
  it. The phone keys its copy the same way.
- **The knowledge module keeps a copy of its content and of the user's log in
  the browser too**, in IndexedDB. `../core-package/knowledge/store.md` gives
  why the native app and the web app keep the same copy.

## Wireframes

A wireframe is a page's screen drawn at low fidelity, as text in a fenced
block. Each page's folder holds a file per screen beside its `README.md`, such
as `pages/problems/problem/paused.md` for the sitting with its clock paused.

- **A wireframe fixes what sits on a page and in what order.** The size of a
  box, the weight of a line and the wording of a label are the design system's
  to answer, and a wireframe fixing them would be redrawn at every restyle.
- **A wireframe is read against the page's `README.md`, never against the
  code.** The pages are rebuilt on these wireframes, so a wireframe copied from
  the pages as they stand would license the layout the rebuild exists to
  replace.

## Rules a page holds, specified elsewhere

- A candidate is offered without its statement, since opening the problem
  serves it (`../flows/drill-loop.md`).
- A template's code is hidden until the user reveals it
  (`../content-repo/cards.md`).
- The editor proposes no name from the standard library or from the code already
  typed (`../flows/drill-loop.md`).
- A failing submission shows its first failing case whole, at whatever size
  (`../flows/drill-loop.md`).
- A card is offered beside a problem, and no sitting requires reading it
  (`../flows/drill-loop.md`).
