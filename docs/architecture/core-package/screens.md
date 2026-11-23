# The two clients

Every screen either client holds, in one inventory, and the reasons the two
clients differ where they do. `README.md` gives the rule: a platform may
change how a thing looks and how it is used, and never what it offers. The
inventory is the list both clients build to. A page's own file under
`../web-app/pages/` gives what the page offers on both clients.

- **Each row is one screen or one act**, with where it lives on the web and
  on the phone. `none` marks a client that does not hold it.
- **A row's status is one of six.**
  - `same`: both clients offer it.
  - `by platform`: both offer it, and the interaction differs. The row
    gives its reason.
  - `web for now`: held on the web alone until a named trigger moves it to
    the phone too. The list under the tables names each trigger.
  - `web only` and `phone only`: held on one client for good, for a reason
    the list gives.
  - `to fix`: the clients offer different things, and the list under the
    tables names the change.
- **A planned screen counts as held.** A screen a page file gives and the web
  does not serve yet is listed on the web, so the phone is compared with what
  the web will offer.
- **`tests/test_pages_inventory.py` holds the screens table to the code.**
  Each web route and phone screen file names its row there, and a row's phone
  column reads `none` exactly where no phone screen holds it. A screen added
  without its row fails the suite.

## Screens

| Screen | Web | Phone | Status |
|---|---|---|---|
| The landing page | the board | the Practice tab | same |
| The board | `/` | the Practice tab | same |
| A technique's problems and cards | `/techniques/:technique` | Technique | same |
| The problem listing | `/problems` | the Problems tab | same |
| A picked problem's record and statement | `/problems/:problem_id` | Problem | same |
| A sitting | `/problems/:problem_id` | Problem, its Code tab | by platform |
| A cold sitting, running and ended | `/cold/:sitting_id` | Cold | same |
| The cards | `/cards` | the Cards tab | same |
| A card's trigger, brief and templates | `/cards/:slug` | Card | same |
| A card's ladder and probes | `/cards/:slug` | Card | same |
| The press starting a card's run | `/cards/:slug` | Card, its bottom bar | same |
| The required cards a locked card waits on, on that press | `/cards/:slug` | Card, its bottom bar | same |
| A recall | `/cards/:slug/recall/:template` | Recall, from Card | same |
| Judging a solution | `/judge` | Judge | same |
| Filling a key line | `/fill` | Fill | same |
| The knowledge home | `/knowledge` | Home | same |
| A module | `/knowledge/modules/:module` | Module | same |
| The start sheet | a dialog on the module page | a sheet on Module | same |
| A queue | `/knowledge/queue` | the quiz screen | same |
| A lesson a queue offers | a stop opening the lesson over the queue | a stop opening the lesson screen | same |
| A baseline test a queue offers | a stop, then the exam's screen in the queue's place | a stop, then the exam's screen in the quiz's place | same |
| A level exam's choices | `/knowledge/exam` | Exam | same |
| An exam and its results | `/knowledge/exam` | the quiz screen | by platform |
| The lessons | `/knowledge/lessons` | Lessons | same |
| A subtopic | `/knowledge/modules/:module/:sub` | Subtopic | same |
| A lesson | `/knowledge/lessons/:module/:lesson` | Lesson | same |
| The certifications | `/knowledge/certifications` | Certifications | same |
| A certification's conditions | a dialog on the certifications and the map | a sheet on Certifications and Map | same |
| The guide | `/start` | Guide | same |
| The settings | `/settings` | Settings | same |
| The signed-in devices | a dialog from the account menu | a screen from the account menu | same |
| The login | `/login` | Login | same |
| The privacy policy | `/privacy` | Privacy, from Login and Settings | same |
| The terms of use | `/terms` | Terms, from Login and Settings | same |
| The gallery | `/gallery`, in development | none | web only |
| The author pages | `/author` and the pages under it | none | web only |
| The error screen | in place of a page that threw | in place of a screen that threw | by platform |

## Acts

| Act | Web | Phone | Status |
|---|---|---|---|
| Continue | the home | Home | same |
| Review what a strict focus leaves out | the home's counts line | Home's counts line | same |
| Raise today's limit | the focus panel and a queue | the focus card and a queue | same |
| Clear the focus, or make it strict | the focus panel | the focus card | same |
| Aim the focus at a module | the module page | Module | same |
| Aim the focus at a topic | the module page | Module | same |
| Aim the focus at a subtopic | the module page | Module, its groups and its map | same |
| Aim the focus at a certification | a certification's conditions | a certification's sheet | same |
| Start a filtered queue on a group | a module page cell | a Module cell | same |
| Start a filtered queue on a subtopic | the module page | Module, its groups and its map | same |
| Start a filtered queue on a topic or a module | the module page | Module | same |
| Order the modules | up and down presses | a drag | by platform |
| Pause, resume or archive a module | the module page | Module | same |
| Restore an archived module | the settings page | Settings | same |
| Open a lesson ready to read, or a certification ready for its exam | the home | Home | same |
| Mark a lesson read or unread | the lesson page | Lesson | same |
| Open a subtopic naming a card's technique | the card page | Card | same |
| Open a card a lesson's subtopic pairs with | the lesson page | Lesson | same |
| Open a subtopic a template cites | the card page, in the template's panel | Card | same |
| Set the daily limit and the exam size | the settings page | Settings | same |
| Set the exam size for one exam | the exam page | Exam | same |
| Type a `short` reply | the browser's keyboard | the app's keyboard | by platform |
| Read the sync's state, and sync now | the settings page | Settings, and Home's footer | same |
| Sign out, naming unsent records | the account menu and the settings page | the account menu and Settings | same |
| Start a cold sitting, or return to the one running | the board's cold panel | the Practice tab's cold panel | same |
| End a cold sitting before it is solved, confirmed | a dialog from End | a sheet from End | same |
| Ask for a problem's retirement | a dialog from under the statement | a sheet from under the statement | same |
| Send feedback | a dialog from the settings page and the error screen | a sheet from Settings and the error screen | same |
| Revoke a signed-in device | the signed-in devices | the signed-in devices | same |
| Export the record as a file | the settings page, as a download | Settings, into a folder the user picks | by platform |
| Delete the account, its name typed back | the settings page | Settings | same |
| Choose the colour scheme | the switch in the navigation | Settings | by platform |
| Set the device name or the reminder hour | none | Settings | phone only |

## Where the clients differ

- **A sitting is `by platform` for its tabs and its reopening.** The phone
  holds the statement and the editor as two tabs, and reopens the sitting the
  problem has running. `../web-app/pages/problems/problem/README.md` gives
  both.
- **An exam runs on its own page on the web and on the quiz screen on the
  phone.** The web's exam page holds its sample in memory, so a reload
  returns to its choices without discarding a record. The phone has no
  reload, and its quiz screen runs every queue and exam.
- **Ordering by drag is the phone's, and up and down presses are the
  web's.** A drag needs a long press, which a pointer does not hold well.
- **A `short` reply is typed on the app's keyboard on the phone.** The web is
  read at a physical keyboard, which holds every symbol on its keys. The
  phone's system keyboard hides them, and its suggestion strip completes words.
- **The phone chooses its colour scheme in Settings, from System, Light and
  Dark.** System follows the phone's own setting, and is the default. The web
  holds a light and dark switch in its navigation, where a reader at a desk
  reaches it. The phone keeps the choice on the device and the web keeps it in
  the browser, since the choice is about the screen rather than the account.
- **The device name and the reminder hour are phone only.** Each one is
  about one phone.
- **The gallery is web only.** It is a tool for whoever styles the web.
- **The author pages are web only.** The author reads them at a desk, beside
  the terminal the commands that act on them run in.

## What the phone reads from the engine

- **The phone reads the board and the cards from the engine and keeps no
  copy.** With no connection the Practice tab, the Cards tab and each screen
  under them say so. The knowledge copy exists so a
  queue picks offline, and reading a card picks nothing.
- **Pulling a list down on the phone syncs.** The knowledge log is sent and
  received at once, and a screen reading the engine reads it again. A phone
  has no reload, and a reader pulls to see the records another device wrote.
- **Each build of the phone names the engine it syncs with, and no screen
  changes it.** The release build reads the address from `native/.env` when
  it is built. The dev build reaches the local engine at `localhost:8000`,
  which `just native-dev` forwards over USB. An address saved on the phone
  could go wrong, and a wrong one blocks the sign-in that would open
  Settings. The web reaches the engine it was served from.

## To fix

A row marked `to fix` is listed here with what holds now and the change it
needs. The audit of 2026-11-10 compared every knowledge row marked `same`
with the other client's code, and both clients were brought together on each
difference it found. No row is marked `to fix` today.
