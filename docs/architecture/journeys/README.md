# Journeys

A journey is one path a user takes through both clients, from a screen where
the user starts to a state where the path ends. Each journey is a
`[[journey]]` record in `../model.toml`, and the table below is generated
from those records.

- **A journey names the screens and the acts it crosses**, by their rows in
  `../core-package/screens.md`. Each of those rows names what both clients
  offer, so a journey runs on the web and on the phone alike.
- **A journey names the flows it runs and the components that act in it**, by
  their ids in `../model.toml`. `../flows/` gives each flow's steps, and the
  component's own file gives its rules.
- **Every screen and every act sits in a journey or in the `apart` list.**
  `tools/model_views.py check` fails on a row in neither. A row added to
  `screens.md` then needs a journey that reaches it, or a decision that no
  user's path does.
- **The `apart` list names what no user's path reaches**, such as the
  gallery, built in development alone. The web's not-found page serves no row
  of `screens.md`, and reaches no journey either.
- **A journey's `doc` names this file until the journey has a page of its
  own** in this folder.

## The journeys

<!-- generated from model.toml by `just model-views`: the journeys -->

| Journey | Starts | Ends | Screens | Acts | Flows | Components |
|---|---|---|---|---|---|---|
| First run and the baseline test | The login page, with an invitation | The first lesson read and its first questions answered | The login; The privacy policy; The terms of use; The landing page; The guide; The knowledge home; A module; The start sheet; A baseline test a queue offers; A lesson a queue offers | Continue | none | `sign-in`; `app-tokens`; `snapshot`; `baseline-tests`; `gating`; `queues`; `answering`; `client-store`; `knowledge-sync` |
| The knowledge queue | The knowledge home's Continue | The queue's stop and its summary | The knowledge home; A queue; A module; A subtopic; The lessons; A lesson | Continue; Review what a strict focus leaves out; Raise today's limit; Clear the focus, or make it strict; Aim the focus at a module; Aim the focus at a topic; Aim the focus at a subtopic; Start a filtered queue on a group; Start a filtered queue on a subtopic; Start a filtered queue on a topic or a module; Order the modules; Pause, resume or archive a module; Open a lesson ready to read, or a certification ready for its exam; Mark a lesson read or unread; Type a `short` reply | none | `knowledge-schedule`; `gating`; `queues`; `answering`; `baseline-tests`; `projections`; `knowledge-screens`; `client-store`; `knowledge-sync`; `knowledge-log` |
| A sitting | The board's pick, a technique's problems, or the problem listing | A solved or ended sitting, its claim and its label answered | The board; A technique's problems and cards; The problem listing; A picked problem's record and statement; A sitting | Ask for a problem's retirement | `drill-loop` | `practice-screens`; `core-sitting`; `problems`; `sitting`; `submission`; `runner`; `run-faults`; `attempt-log`; `attempt-claims`; `self-labels`; `retirement-requests` |
| A failure diagnosed and the next pick | A sitting ended unsolved | The board serving a pick aimed at the form that failed | A sitting; The board; A recall | none | `drill-loop` | `self-labels`; `diagnoser`; `pick`; `predictions`; `template-schedule`; `card-states`; `mastery` |
| Cards and recall | The Cards tab | A card graduated | The cards; A card's trigger, brief and templates; A card's ladder and probes; The press starting a card's run; The required cards a locked card waits on, on that press; A sitting; A recall; Judging a solution; Filling a key line | Open a subtopic naming a card's technique; Open a card a lesson's subtopic pairs with; Open a subtopic a template cites | `starting-a-card-run`; `solving-a-rung`; `recalling-a-template` | `card-runs`; `card-states`; `recall`; `core-recall`; `template-schedule`; `short-exercises`; `core-exercises` |
| A cold sitting and the rating | The board's cold panel | The cold panel reading the measured and the projected rating | The board; A cold sitting, running and ended | Start a cold sitting, or return to the one running; End a cold sitting before it is solved, confirmed | none | `sitting`; `submission`; `runner`; `attempt-log`; `rating`; `projection`; `mastery` |
| A level exam and a certification | The knowledge home naming a certification ready for its exam, or its Exam press | A certification earned, or its conditions read as not yet met | The certifications; A certification's conditions; A level exam's choices; An exam and its results | Aim the focus at a certification; Set the exam size for one exam; Open a lesson ready to read, or a certification ready for its exam | none | `certifications`; `gating`; `knowledge-schedule`; `answering`; `knowledge-screens`; `knowledge-sync` |
| The phone offline | The phone's Home with no connection | The outbox sent, and the web reading the same answers | The knowledge home; A queue; The board; The cards | Read the sync's state, and sync now | none | `client-store`; `queues`; `answering`; `snapshot`; `knowledge-sync`; `knowledge-log` |
| The account on the web and the phone | The account menu | Signed out, or the account deleted | The settings; The signed-in devices; The error screen | Set the daily limit and the exam size; Restore an archived module; Read the sync's state, and sync now; Sign out, naming unsent records; Send feedback; Revoke a signed-in device; Export the record as a file; Delete the account, its name typed back; Choose the colour scheme; Set the device name or the reminder hour | none | `core-account`; `sign-in`; `app-tokens`; `feedback`; `knowledge-sync` |
| The author's review | The author area's inbox, at `/author` | Each waiting row answered by its command | The author pages | none | none | `author-reads`; `retirement-requests`; `feedback`; `run-faults`; `diagnoser`; `seed`; `generation`; `difficulty` |

The screens and acts in no journey: The gallery.

<!-- end of the generated journeys -->
