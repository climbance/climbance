# First run and the baseline test

A new user signs in for the first time, reads the guide, opens the knowledge
home, is offered a placement, takes a topic's baseline test, and reads the
first lesson. This page
follows the `first-run` journey in `../model.toml`. It starts at the login
page. It ends once the first lesson is read and its first questions are
answered.

`../api/sign-in.md` gives the rules of signing in, and
`../core-package/knowledge/README.md` names the files giving the rules of the
knowledge module. This page cites them rather than restating them. Each
component below is named by its id in `../model.toml`.

## 1. The login page

- **The web's login is `/login`, and the phone's is the Login screen.** The
  page names the app in one line and offers Continue with Google and Continue
  with GitHub. `../web-app/pages/login/README.md` gives the page.
- **The login page links the privacy policy and the terms of use**, and the
  three pages open without a session and carry no navigation. The phone holds
  the policy and the terms as screens, so they read before any sign-in and
  with no connection.
- **Each press opens the provider's account chooser**, so a person holding two
  Google or GitHub accounts picks one. The engine stores no password.
- **The web signs in through `sign-in`, which ends the provider flow in a
  session cookie.** The phone opens the same flow in a browser sheet, and
  `app-tokens` ends the flow in a one-time code the app exchanges for its
  token. `../api/app-tokens.md` gives the exchange.
- **The phone's sign-in needs a connection.** With none, the Login screen says
  that the sign-in is read from the engine.

## 2. Signing up

- **Anyone may sign up, and no invitation is needed.** The callback mints a
  user for a verified email no account holds, under a pace of 20 new users a
  day and a ceiling of 200 users. `../api/sign-in.md` gives both limits under
  Sign-up.
- **An email the `invitations` table holds is admitted past both limits.**
  The author adds an invitation with `climb invite`.
- **An email another account already holds joins that account's user**, so
  one person reaches one log through Google or GitHub. The email counts only
  where the provider verified it.
- **A refused sign-in returns to the login page with a code**, and the page
  names the reason on a strip above the presses. Past either limit the strip
  says today's places are taken. An account with no verified email is refused
  too.
- **A refused sign-in stores no user, no identity and no session.** The person
  may come back on a later day, since the engine keeps no waitlist and sends no
  email.

## 3. The board and the guide

- **A signed-in user lands on the board**: `/` on the web, the Practice tab on
  the phone. `../web-app/pages/practice/board/README.md` gives the board.
- **The board opens with a panel linking the guide while the user's log holds
  no act.** The first act removes the panel on every client the act's record
  reaches, and nothing stores a dismissal.
- **The guide is `/start` on the web and the Guide screen on the phone.** The
  guide names each kind of practice, what it trains and where it is reached.
  Its two starts are the board's pick for the algorithms and a module's first
  lesson for the knowledge. `../web-app/pages/practice/guide/README.md` gives
  the page.
- **The account menu links the guide always**, so a user can reread the guide
  once the board's panel is gone.

## 4. The content reaches the device

- **`client-store` keeps a copy of the content and of the user's log on the
  device**: in IndexedDB on the web, in SQLite on the phone. The copy is keyed
  to the signed-in user. `../core-package/knowledge/store.md` gives the copy.
- **`snapshot` serves the whole content of every live module as one
  document.** A later launch revalidates the snapshot by its ETag, and an
  unchanged snapshot answers 304. `../api/snapshot.md` gives the format.
- **`knowledge-sync` returns the user's records since a cursor.** A new user's
  first sync carries no cursor and returns no record, since the log is empty.

## 5. The knowledge home

- **The web's home is `/knowledge`, and the phone's is the Home screen.** The
  home lists one row per module not archived. `knowledge-queue.md` follows the
  home in full.
- **The home's one act reads Start while the knowledge log holds no answer
  and no lesson mark.** Start runs the same queue Continue runs.
- **A module's row opens the module's page**, where each group reads as
  covered, open, locked, holding no questions or not yet open. `gating`
  opens level 0 of every subtopic at once, as
  `../core-package/knowledge/gating.md` gives.
- **The module's page opens the start sheet on a group, a subtopic, a topic or
  the module**, and the sheet starts a filtered queue.
  `../web-app/pages/knowledge/module/start-sheet.md` draws the sheet.

## 6. The placement

- **The queue offers a placement before the first new question of a module
  no answer and no stint names.** The placement covers that question's topic,
  as `../core-package/knowledge/placement.md` gives.
- **The placement opens as a stop naming the module beside the topic**, with
  Place me and Start from the beginning. Place me replaces the queue with the
  exam's screen on the web, and the quiz screen on the phone.
- **`placement` asks each subtopic from its highest written level down**, and
  shows no feedback until the end. Each answer carries the measure
  `placement`, and the schedule ignores it.
- **Done returns to the queue**, and `gating` reads every placed group as
  done. The queue's next new question then comes from above the placed
  levels.
- **Start from the beginning stores a placement stint that answered
  nothing**, and the queue offers no placement on the module again.

## 7. The baseline test

- **The queue offers a topic's baseline test before the topic's first new
  question.** `queues` picks the question, and `baseline-tests` samples the
  test: two `choice` or `short` questions per subtopic, at most twenty.
  `../core-package/knowledge/baseline-tests.md` gives the sample.
- **The test opens as a stop naming the module beside the topic**, as
  `Algorithms · Procedures`. A press then replaces the queue with the exam's
  screen on the web, and the quiz screen on the phone.
- **A queue run offers one baseline test.** Another topic's test waits for a
  later run, so a new user meets at most twenty test questions before any
  practice.
- **`answering` runs the test one question at a time, and shows no feedback
  until the end.** A shown key would teach the next question's answer.
- **The user may skip the test once.** The skip stores a baseline stint that
  answered nothing, and the topic then gets no delayed test.
- **Each test answer carries the measure `baseline`, and the schedule ignores
  it.** A question the test asked stays unseen, and the queues serve it last.

## 8. The first lesson and its questions

- **A taken test spends the pretest of every lesson teaching the topic.** The
  topic's next new question is then held back by its lesson, as
  `../content-repo/lessons.md` gives. A skipped test answered nothing, so it
  spends no pretest.
- **The queue offers the lesson as a stop, with Read and Later.** The stop
  names the lesson, its reading time and why it is offered.
- **Read opens the lesson over the running queue**: in a dialog on the web,
  as a screen above the queue on the phone. Mark read returns to the queue.
- **Mark read stores a lesson mark, and `queues` releases the lesson's held
  questions.** The next new question comes from the first frontier group,
  which `gating` reads.
- **Each answer goes into the outbox, and `client-store` sends it within ten
  seconds.** `knowledge-sync` stores each sync line. The journey ends here, and
  `knowledge-queue.md` follows every later queue.

## Where the web and the phone differ

`../core-package/screens.md` marks every screen of this journey `same`. The
differences lie in how each client signs in and starts.

- **The phone signs in through a browser sheet and keeps an app token** in the
  Keystore or the Keychain. The web keeps a session cookie. The two flows pass
  the same callback, so the pace and the email check run unchanged.
- **The phone reads the privacy policy and the terms with no connection**,
  since the app holds both texts. The web fetches every page from the engine.
- **The phone types a `short` reply on the app's own keyboard**, as
  `knowledge-queue.md` gives.

## What each step stores, and what reads it

| Step | Stores | Read later by |
|---|---|---|
| A first sign-in on the web | a user, an identity and a session | every later request; the signed-in devices; `climb log prune`, from the session's last use |
| A first sign-in on the phone | a user, an identity, a one-time code, then an app token | every later request; the signed-in devices; `climb log prune` |
| A sign-in refused past a limit | nothing | the login page, through `?refused=` alone |
| The device's first sync | the copy of the snapshot and the empty log | every queue on the device, which picks from the copy |
| A placement answer | an answer measuring `placement` | `placement`, which reads the placed groups; `gating`, which reads them as done |
| The placement's end, or its skip | a placement stint | `placement`, so the queue offers the module no placement again |
| A test answer | an answer measuring `baseline` | `baseline-tests`, for the delayed test and the learning gain; the lessons' pretests |
| The test's stop, or its skip | a baseline stint | `baseline-tests`, so the topic's test is not offered again |
| Mark read | a lesson mark | `queues`, which releases the held questions; the lessons page; the board's guide panel |
| A practice answer | an answer | `knowledge-schedule`, `gating`, `queues` and `certifications`, as `knowledge-queue.md` gives |

`exam-and-certification.md` follows the answers into a certification, and
`phone-offline.md` follows the outbox with no connection.

## Open questions

- **Does a filtered queue offer the baseline test?** The journey names the
  start sheet, which starts a filtered queue. `baseline-tests.md` names only
  the next and the focus queue as offering the test, so a new user starting
  from the sheet may skip the test unasked.
- **Which start does the guide name for the knowledge?** The guide's page file
  names a module's first lesson. The guide's wireframe names Continue on the
  board.
- **Which words does a refused person read past a limit?** The login
  wireframe says to come back tomorrow. The text in `packages/core` says to try
  again on a later day, and the pace counts the last 24 hours rather than the
  calendar day.
- **Does a test answer remove the board's guide panel?** The board counts an
  answer as an act. No doc says whether an answer the schedule ignores counts
  as one.
