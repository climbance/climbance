# Architecture

Target state, across this file and the folders beside it. The code lags these
files. On any difference, the doc wins.

<!-- generated from model.toml by `just model-views`, never edited -->

## Views

A dashed arrow reads and leaves its target unchanged. A solid arrow writes,
or starts a run.

The engine's context: who uses it and what it reaches outside itself.

```mermaid
flowchart TB
    engine["Climbance<br/>Serves generated problems, judges each submission against the problem's own cases, and schedules what to practise next."]
    learner["Learner<br/>Solves problems, recalls templates and answers questions, on the web or the phone."]
    author["Author<br/>Generates and reviews the corpus, authors the content, invites users and deploys the engine."]
    identity_providers["Google and GitHub<br/>Hold each identity and its login; the engine stores no password."]
    model_router["Model router<br/>Reaches every model as chat completions, each request pinned to one endpoint."]
    content_repo["Content repository<br/>The private repository of authored cards and modules under content/, seeded into the store."]
    image_registry["Image registry<br/>Holds the engine's image, built on each push to main and pulled by digest."]
    offsite_dumps["Off-server dump storage<br/>Keeps the scheduled database dumps away from the storage the database lives on."]
    learner -->|"practises in a browser [a web browser]; practises on a phone [Android, iOS]"| engine
    author -->|"generates, reviews, seeds and invites [a terminal]"| engine
    author -->|"authors cards and modules [git]"| content_repo
    engine -.->|"runs the sign-in flow [OpenID Connect, OAuth]"| identity_providers
    engine -.->|"pulls the submission image by digest, through the host's daemon [docker pull]"| image_registry
    engine -.->|"sends every model call [chat completions]; sends each request, pinned to one endpoint"| model_router
    engine -.->|"seeds cards and modules from content/"| content_repo
    image_registry -->|"supplies the image the server deploys [docker pull by digest]"| engine
    engine -->|"is dumped on a schedule and copied off the server [pg_dump]"| offsite_dumps
```

The engine's containers: what runs on its own, and what each talks to.

```mermaid
flowchart TB
    learner["Learner<br/>Solves problems, recalls templates and answers questions, on the web or the phone."]
    author["Author<br/>Generates and reviews the corpus, authors the content, invites users and deploys the engine."]
    identity_providers["Google and GitHub<br/>Hold each identity and its login; the engine stores no password."]
    model_router["Model router<br/>Reaches every model as chat completions, each request pinned to one endpoint."]
    content_repo["Content repository<br/>The private repository of authored cards and modules under content/, seeded into the store."]
    image_registry["Image registry<br/>Holds the engine's image, built on each push to main and pulled by digest."]
    offsite_dumps["Off-server dump storage<br/>Keeps the scheduled database dumps away from the storage the database lives on."]
    subgraph engine["Climbance"]
        web_app["Web app<br/>Vite, React and TypeScript, built to static files; the pages a learner uses in a browser."]
        native_app["Native app<br/>The phone client for Android and iOS; schedules the knowledge queues offline and syncs."]
        core_package["Shared core<br/>packages/core: the knowledge module's rules, each screen's labels and acts, and each technique's knowledge reading from the device's copy of the log, imported by both clients."]
        shared_editor["Shared editor<br/>packages/editor: the CodeMirror setup for editing Python, imported by both clients."]
        proxy["Caddy<br/>Terminates TLS, keeps the certificates on a volume, and passes every request to the API."]
        api["API<br/>Python and FastAPI: answers JSON under /api, serves the web app's files, signs users in and records the log."]
        broker["Broker<br/>Holds the container runtime's socket, admits one submission at a time and starts its sandbox."]
        sandbox["Sandbox<br/>One container per run under gVisor, no network, read-only root; its entry process forks a child per case."]
        database["Postgres<br/>The one store: the corpus, the content, every user's log and the call log."]
        cli["Command line<br/>climb, run by the author off the server: generation, the by-hand passes, seeding, invitations and difficulty ratings; it runs each draft's solutions in a local subprocess, never through the broker."]
    end
    learner -->|"practises in a browser [a web browser]"| web_app
    learner -->|"practises on a phone [Android, iOS]"| native_app
    author -->|"generates, reviews, seeds and invites [a terminal]"| cli
    author -->|"authors cards and modules [git]"| content_repo
    web_app -.->|"imports the rules and screens [npm workspace]"| core_package
    native_app -.->|"imports the rules and screens [npm workspace]"| core_package
    web_app -.->|"imports the editor setup [npm workspace]"| shared_editor
    native_app -.->|"imports the editor setup, bundled into the editor's WebView page [npm workspace]"| shared_editor
    web_app -->|"sends JSON with the session cookie [HTTPS]"| proxy
    native_app -->|"syncs knowledge records and runs sittings, with an app token [HTTPS]"| proxy
    proxy -->|"passes every request [HTTP]"| api
    api -.->|"serves the built files [HTTP]"| web_app
    api -.->|"runs the sign-in flow [OpenID Connect, OAuth]"| identity_providers
    api -->|"reads and writes the store [SQLAlchemy Core]"| database
    api -->|"asks for one run: code, arguments, cap [HTTP, private network]"| broker
    broker -->|"starts one container per run, the run on standard input [docker run -i]"| sandbox
    broker -.->|"pulls the submission image by digest, through the host's daemon [docker pull]"| image_registry
    cli -.->|"sends every model call [chat completions]"| model_router
    cli -->|"writes the corpus and the by-hand records [SSH tunnel]"| database
    cli -.->|"seeds cards and modules from content/"| content_repo
    image_registry -->|"supplies the image the server deploys [docker pull by digest]"| api
    database -->|"is dumped on a schedule and copied off the server [pg_dump]"| offsite_dumps
    api -.->|"reads each failed sitting's measured diagnosis"| cli
```

The Web app's components, and what each reads and writes.

```mermaid
flowchart TB
    core_package["Shared core<br/>packages/core: the knowledge module's rules, each screen's labels and acts, and each technique's knowledge reading from the device's copy of the log, imported by both clients."]
    shared_editor["Shared editor<br/>packages/editor: the CodeMirror setup for editing Python, imported by both clients."]
    api["API<br/>Python and FastAPI: answers JSON under /api, serves the web app's files, signs users in and records the log."]
    subgraph web_app["Web app"]
        web_shell["Web shell<br/>The navigation, the account menu, the signed-in devices, the error screen, the settings and the pages under no section."]
        web_author["Web author pages<br/>The author area: the inbox, the content browser, and the product, generation and spend pages, for a user with the author role."]
        web_design_system["Web design system<br/>The tokens, the shadcn components and the shared shapes every web page is built from, shown in the gallery."]
        web_areas["Web page areas<br/>The header, the body, the act, the panels and the section bar a web page is laid out in."]
        web_practice["Web practice pages<br/>The board, a technique's problems, the guide and the problem listing."]
        web_cards["Web card pages<br/>The cards, a card's ladder and templates, a recall, and the judging and key-line exercises."]
        web_sitting["Web sitting<br/>A picked problem's page: its record, the statement, the editor, the clock, the verdict, the claim and the retirement request; and a cold sitting's page."]
        web_knowledge["Web knowledge pages<br/>The knowledge home, a module, a subtopic, a queue, an exam, the lessons and the certifications."]
        web_knowledge_store["Web knowledge store<br/>Keeps the browser's copy of the content and the user's log in IndexedDB, and runs the sync loop."]
    end
    web_author -.->|"reads each author page's figures"| api
    web_author -.->|"draws the author pages' labels"| core_package
    web_knowledge -.->|"draws what each knowledge screen says; runs a queue or an exam; draws the review forecast"| core_package
    web_knowledge -.->|"reads the copy and starts a sync"| web_knowledge_store
    web_knowledge_store -.->|"runs the sync over the browser's copy"| core_package
    web_practice -.->|"draws the board, the guide and the listing"| core_package
    web_cards -.->|"draws the cards and their ladders; runs a recall; runs a judging or a key-line exercise"| core_package
    web_cards -.->|"types a recall in the sitting's editor"| web_sitting
    web_sitting -.->|"runs the sitting's clock and submissions"| core_package
    web_sitting -.->|"imports the editor setup"| shared_editor
    web_shell -.->|"reads the devices, the export and the deletion"| core_package
    web_areas -.->|"reads a page's readings and its sections"| core_package
    web_design_system -.->|"reads how code wraps, and the shape of each table and diagram"| core_package
```

The Native app's components, and what each reads and writes.

```mermaid
flowchart TB
    core_package["Shared core<br/>packages/core: the knowledge module's rules, each screen's labels and acts, and each technique's knowledge reading from the device's copy of the log, imported by both clients."]
    shared_editor["Shared editor<br/>packages/editor: the CodeMirror setup for editing Python, imported by both clients."]
    subgraph native_app["Native app"]
        native_shell["Phone shell<br/>The account menu, the sign-in, the signed-in devices, the error screen, the settings and the reminder."]
        native_design_system["Phone design system<br/>The tokens and the shared shapes every phone screen is built from: rows, sheets, sections, tables, prose and diagrams."]
        native_editor["Phone editor<br/>The CodeMirror page in its WebView, and the app's own keyboard typing into it."]
        native_practice["Phone practice screens<br/>The Practice tab, a technique's problems, the guide and the Problems tab."]
        native_cards["Phone card screens<br/>The Cards tab, a card, a recall, and the judging and key-line exercises."]
        native_sitting["Phone sitting<br/>A picked problem's screen: the statement and the Code tab, the clock, the claim and the retirement request; and a cold sitting's screen."]
        native_knowledge["Phone knowledge screens<br/>The Knowledge tab, a module, a subtopic, the quiz screen, an exam, the lessons and the certifications."]
        native_knowledge_store["Phone knowledge store<br/>Keeps the phone's copy of the content and the user's log in SQLite, and syncs it in the background."]
    end
    native_knowledge -.->|"draws what each knowledge screen says; runs a queue or an exam; draws the review forecast"| core_package
    native_knowledge -.->|"reads the copy and starts a sync"| native_knowledge_store
    native_knowledge_store -.->|"runs the sync over the phone's copy"| core_package
    native_practice -.->|"draws the board, the guide and the listing"| core_package
    native_cards -.->|"draws the cards and their ladders; runs a recall; runs a judging or a key-line exercise"| core_package
    native_cards -.->|"types a recall"| native_editor
    native_sitting -.->|"runs the sitting's clock and submissions"| core_package
    native_sitting -.->|"types the sitting's code"| native_editor
    native_editor -.->|"bundles the editor setup into the WebView page"| shared_editor
    native_shell -.->|"reads the devices, the export and the deletion"| core_package
    native_design_system -.->|"reads a screen's readings and its sections; reads how code wraps, and the shape of each table and diagram"| core_package
```

The Shared core's components, and what each reads and writes.

```mermaid
flowchart TB
    web_app["Web app<br/>Vite, React and TypeScript, built to static files; the pages a learner uses in a browser."]
    native_app["Native app<br/>The phone client for Android and iOS; schedules the knowledge queues offline and syncs."]
    subgraph core_package["Shared core"]
        knowledge_schedule["Schedule<br/>Replays FSRS over a user's answers, rates each one, and reads each question's state."]
        gating["Gating<br/>Reads the levels, the groups and the prerequisite graph from the snapshot, and opens each group's new questions."]
        queues["Queues<br/>Picks each queue's next question under the daily limit, the focus, the settings and the module order."]
        certifications["Certifications<br/>Decides each certification's state, and samples a level exam or a certification's."]
        baseline_tests["Baseline tests<br/>Samples a topic's baseline test, and asks its questions again as the delayed test."]
        placement["Placement<br/>Asks a topic's subtopics highest level first, and reads which groups the user's answers placed."]
        projections["Projections<br/>Counts the reviews of the next fourteen learning days, and dates when the focus is reached."]
        client_store["Store and sync<br/>Names the records a client keeps, folds them into the learner, and syncs the outbox with the engine."]
        answering["Answering<br/>Runs a queue or an exam one question at a time: the reply, its grade, and the result each answer shows."]
        knowledge_screens["Knowledge screens<br/>Computes what the knowledge home, a module, its map, a subtopic, the lessons and the certifications say."]
        practice_screens["Practice screens<br/>Computes what the board, the cards, the listing and the guide say, each page's readings and sections, and the author pages' labels."]
        core_sitting["Sitting controller<br/>Drives a sitting: the requests minting it, moving its clock and submitting to it, then the claim and the label."]
        core_recall["Recall trainer<br/>Draws the template a recall reproduces, and offers its hints in order."]
        core_exercises["Exercise screens<br/>Serves the judging and the key-line items one at a time, and reads each answer back."]
        core_account["Account<br/>Names the signed-in devices, exports the record, deletes the account, sends feedback, and holds the privacy policy and the terms of use."]
        drawing["Code and diagrams<br/>Wraps code to a width, and shapes the tables and the diagrams authored prose holds."]
    end
    web_app -.->|"draws the author pages' labels; draws the board, the guide and the listing; draws the cards and their ladders; reads a page's readings and its sections"| practice_screens
    queues -.->|"reads each question's state"| knowledge_schedule
    queues -.->|"reads the open groups"| gating
    certifications -.->|"reads which questions are retained"| knowledge_schedule
    certifications -.->|"reads the groups a certification covers"| gating
    baseline_tests -.->|"samples the questions as an exam does"| certifications
    placement -.->|"samples the questions as an exam does"| certifications
    gating -.->|"reads which groups are placed"| placement
    answering -.->|"runs a placement"| placement
    projections -.->|"reads what the next queue serves"| queues
    projections -.->|"replays each question forward"| knowledge_schedule
    client_store -.->|"reads the focus, the settings and the order records"| queues
    answering -.->|"draws the next question"| queues
    answering -.->|"runs a baseline or a delayed test"| baseline_tests
    answering -.->|"runs an exam"| certifications
    answering -->|"appends each answer to the outbox"| client_store
    knowledge_screens -.->|"counts what each queue serves"| queues
    knowledge_screens -.->|"reads each certification's state"| certifications
    knowledge_screens -.->|"reads the groups and the prerequisite graph"| gating
    practice_screens -.->|"reads the account the navigation names"| core_account
    web_app -.->|"draws what each knowledge screen says"| knowledge_screens
    web_app -.->|"runs a queue or an exam"| answering
    web_app -.->|"draws the review forecast"| projections
    web_app -.->|"runs the sync over the browser's copy"| client_store
    web_app -.->|"runs a recall"| core_recall
    web_app -.->|"runs a judging or a key-line exercise"| core_exercises
    web_app -.->|"runs the sitting's clock and submissions"| core_sitting
    web_app -.->|"reads the devices, the export and the deletion"| core_account
    web_app -.->|"reads how code wraps, and the shape of each table and diagram"| drawing
    native_app -.->|"draws what each knowledge screen says"| knowledge_screens
    native_app -.->|"runs a queue or an exam"| answering
    native_app -.->|"draws the review forecast"| projections
    native_app -.->|"runs the sync over the phone's copy"| client_store
    native_app -.->|"draws the board, the guide and the listing; draws the cards and their ladders; reads a screen's readings and its sections"| practice_screens
    native_app -.->|"runs a recall"| core_recall
    native_app -.->|"runs a judging or a key-line exercise"| core_exercises
    native_app -.->|"runs the sitting's clock and submissions"| core_sitting
    native_app -.->|"reads the devices, the export and the deletion"| core_account
    native_app -.->|"reads how code wraps, and the shape of each table and diagram"| drawing
```

The API's components, and what each reads and writes.

```mermaid
flowchart TB
    identity_providers["Google and GitHub<br/>Hold each identity and its login; the engine stores no password."]
    web_app["Web app<br/>Vite, React and TypeScript, built to static files; the pages a learner uses in a browser."]
    native_app["Native app<br/>The phone client for Android and iOS; schedules the knowledge queues offline and syncs."]
    broker["Broker<br/>Holds the container runtime's socket, admits one submission at a time and starts its sandbox."]
    database["Postgres<br/>The one store: the corpus, the content, every user's log and the call log."]
    cli["Command line<br/>climb, run by the author off the server: generation, the by-hand passes, seeding, invitations and difficulty ratings; it runs each draft's solutions in a local subprocess, never through the broker."]
    subgraph api["API"]
        sitting["Sitting<br/>Times one session on one problem, minted at the first clock press or submission, and ended where next read."]
        submission["Submission<br/>Takes a user's code for a problem, refuses it past the run caps, and mints the attempt carrying the result."]
        runner["Runner<br/>Runs code against a problem's cases, through the broker or the local subprocess, and reads each case's outcome."]
        run_faults["Run faults<br/>Stores a run the sandbox answered no result for, so the run caps count it."]
        attempt_log["Attempt log<br/>Appends each attempt and its attempt verification; private to the user."]
        attempt_claims["Attempt claims<br/>Stores which techniques an attempt's code used, the user's claim standing over the classifier's."]
        self_labels["Self-labels<br/>Stores the user's verdict on why an attempt went the way it did, as a failure mode."]
        template_schedule["Template schedule<br/>Replays each template's FSRS state from its reviews: recall attempts and sittings on problems written for it."]
        card_states["Card states<br/>Derives each card's state, from not started to graduated or lapsed, from the log on every read."]
        mastery["Mastery<br/>Computes each technique's recognition, execution and chance to solve from the log on every read."]
        pick["Pick<br/>Names the next item: a template and the act that reviews it, read from the three folds."]
        rating["Rating<br/>Replays a user's cold sittings by Glicko-1 into the chance to solve a problem, and the rating with its deviation."]
        projection["Projection<br/>Projects a user's contest rating and its deviation from each technique's chance to solve over a representative contest."]
        predictions["Predictions<br/>Stores what each pick expected, from FSRS and from mastery, before the user acts on it."]
        snapshot["Snapshot<br/>Serves the seeded content to both clients as one document, revalidated by its ETag."]
        knowledge_sync["Knowledge sync<br/>Stores a client's sync lines, refusing each line that names unknown content, and returns the user's records since a cursor."]
        knowledge_log["Knowledge log<br/>The nine append-only tables of the user's knowledge log: answers, stints, focuses and the rest."]
        problems["Problems<br/>Reads a problem from the corpus: its statement, its templates and its test cases."]
        card_runs["Card runs<br/>Stores that a card was started, and the probes the start gave it."]
        recall["Recall<br/>Runs a template typed from memory against the template's cases, and stores the recall attempt."]
        short_exercises["Short exercises<br/>Serves the judgement and key-line items, and stores each judgement and fill."]
        retirement_requests["Retirement requests<br/>Stores a user's request that a problem be retired, for the author to read."]
        feedback["Feedback<br/>Stores a user's note to the author, naming the client and the page."]
        sign_in["Sign-in<br/>Runs the provider flow, admits a new user under the daily pace and the ceiling, and keeps each browser's session."]
        author_reads["Author reads<br/>Answers the author pages' figures under /api/author, read from the store, and refuses a user without the author role."]
        app_tokens["App tokens<br/>Ends the native app's provider flow in a one-time code, and exchanges it for the app's token."]
    end
    sign_in -.->|"runs the sign-in flow [OpenID Connect, OAuth]"| identity_providers
    web_app -->|"starts, pauses and ends the clock"| sitting
    web_app -->|"submits code for the problem"| submission
    submission -->|"mints the sitting where no clock started"| sitting
    submission -->|"runs the code against the problem's cases"| runner
    runner -->|"asks for one run: code, arguments, cap"| broker
    runner -->|"records a run that answered nothing"| run_faults
    submission -.->|"counts recent runs against the caps"| run_faults
    submission -->|"appends the attempt and its verification"| attempt_log
    web_app -->|"names the techniques the code used"| attempt_claims
    web_app -->|"says why the attempt went as it did"| self_labels
    template_schedule -.->|"replays each sitting's verdict as a review"| attempt_log
    card_states -.->|"reads which rungs are solved"| attempt_log
    card_states -.->|"reads the recall probability of a spaced check"| template_schedule
    mastery -.->|"scores execution per sitting"| attempt_log
    mastery -.->|"credits the techniques an attempt used"| attempt_claims
    mastery -.->|"reads the failure mode"| self_labels
    mastery -.->|"reads each problem's standing score"| problems
    mastery -.->|"reads which sittings were cold"| sitting
    mastery -.->|"starts each ability at the measured rating"| rating
    projection -.->|"reads each technique's ability and its deviation"| mastery
    web_app -->|"asks for the next item"| pick
    pick -.->|"reads each template's FSRS state"| template_schedule
    pick -.->|"reads each card's state and next check"| card_states
    pick -.->|"reads each technique's mastery"| mastery
    pick -.->|"reads each failed sitting's measured diagnosis"| cli
    pick -->|"stores what the pick expected"| predictions
    attempt_log -->|"appends to the user's log"| database
    sitting -->|"revises the sitting in place"| database
    predictions -->|"appends each prediction"| database
    attempt_claims -->|"appends each claim"| database
    self_labels -->|"appends each label"| database
    web_app -.->|"loads the content"| snapshot
    native_app -.->|"loads the content"| snapshot
    web_app -->|"syncs answers and sessions"| knowledge_sync
    native_app -->|"syncs answers and sessions"| knowledge_sync
    knowledge_sync -->|"appends each line"| knowledge_log
    knowledge_log -->|"appends to the user's knowledge log"| database
    snapshot -.->|"reads the seeded content"| database
    runner -.->|"reads the problem's cases"| problems
    problems -.->|"reads the corpus"| database
    web_app -->|"starts a card"| card_runs
    card_runs -->|"appends each card run"| database
    card_states -.->|"reads when each run began and its probes"| card_runs
    card_runs -.->|"draws the probes from the technique's problems"| problems
    card_runs -.->|"reads which problems the user attempted"| attempt_log
    web_app -.->|"reads a card's ladder and its state"| card_states
    card_states -.->|"reads which rungs a sitting skipped"| sitting
    web_app -->|"types a template from memory"| recall
    recall -->|"runs the typed form against the template's cases"| runner
    recall -->|"appends each recall attempt"| database
    template_schedule -.->|"replays each recall attempt as a review"| recall
    web_app -->|"judges a solution; fills a key line"| short_exercises
    short_exercises -->|"appends each judgement and fill"| database
    web_app -->|"asks for a problem's retirement"| retirement_requests
    retirement_requests -->|"appends each request"| database
    web_app -->|"sends a note to the author"| feedback
    feedback -->|"appends each note"| database
    web_app -.->|"reads each author page's figures"| author_reads
    author_reads -.->|"counts and lists the store's records"| database
    web_app -->|"signs in and out"| sign_in
    native_app -->|"signs in, exchanging a one-time code for a token"| app_tokens
    app_tokens -->|"passes the same provider callback"| sign_in
    sign_in -->|"stores the identities, the invitations and the sessions"| database
    app_tokens -->|"stores each one-time code and app token"| database
    rating -.->|"reads each cold sitting and its time limit"| sitting
    rating -.->|"reads whether a submission passed within the limit"| attempt_log
    rating -.->|"reads each problem's standing score"| problems
```

The Command line's components, and what each reads and writes.

```mermaid
flowchart TB
    model_router["Model router<br/>Reaches every model as chat completions, each request pinned to one endpoint."]
    content_repo["Content repository<br/>The private repository of authored cards and modules under content/, seeded into the store."]
    api["API<br/>Python and FastAPI: answers JSON under /api, serves the web app's files, signs users in and records the log."]
    database["Postgres<br/>The one store: the corpus, the content, every user's log and the call log."]
    subgraph cli["Command line"]
        classifier["Classifier<br/>Reads an attempt's code and claims the techniques it used, filling what no user claimed."]
        eval_set["Eval set<br/>Holds the hand-claimed attempts adjudicated against a frontier model, and scores each classifier configuration against them."]
        generation["Generation<br/>Writes each problem through its six call sites, and lands it with its cases and its solutions."]
        difficulty["Difficulty<br/>Judges each statement's rating, corrects it to the contest scale on the anchors, stores each problem's rating, and runs the panel's trials."]
        seed["Seed<br/>Reads the authored cards and modules from content/, and refreshes the content tables from them."]
        diagnoser["Diagnoser<br/>Reads a failed attempt or a labelled mutant and names the cause, scored against the self-labels."]
        matcher["Matcher<br/>Reads a canonical beside its statement and names the card templates it displays."]
        exercise_items["Exercise items<br/>Builds the judgement items and the key-line items from the seeded templates and their mutants."]
        calls["Calls<br/>Sends every model call through one transport, each pinned to one endpoint, and appends it to the call log."]
    end
    seed -.->|"seeds cards and modules from content/"| content_repo
    seed -->|"refreshes the content tables"| database
    api -.->|"reads each failed sitting's measured diagnosis"| diagnoser
    classifier -->|"asks which techniques the code used"| calls
    classifier -->|"appends a machine attempt claim"| database
    eval_set -->|"scores a configuration's claims against the set"| classifier
    eval_set -.->|"reads the blind claims and the frontier's claims"| database
    matcher -->|"asks which templates a solution displays"| calls
    matcher -->|"appends a machine template match"| database
    exercise_items -->|"reads the templates and appends the items"| database
    generation -->|"sends each call site's prompt"| calls
    generation -->|"revises the drafts and lands each problem"| database
    difficulty -->|"asks the judge for each draw, and each panel member for a solution"| calls
    difficulty -->|"appends the draws, the corrections, the ratings and the trials"| database
    diagnoser -->|"asks why an attempt failed"| calls
    seed -->|"asks each panel model for a claim's model witness"| calls
    diagnoser -->|"appends each diagnosis and mutant diagnosis"| database
    calls -.->|"sends each request, pinned to one endpoint"| model_router
    calls -->|"appends each call to the call log"| database
```

<!-- end of the generated views -->

## Shape

The engine is public and the content is private. Everything the practice loop
reads is local to the engine, which never contacts external platforms.

Consequence: no third-party dependency in the drill loop.

**Problems are the product's own, and the engine writes them.** A statement
scraped from a platform cannot ship, which forces the question of where
problems come from. The answer is a capability of the engine rather than a
licence fix.

**The engine is the platform.** It serves a generated problem, times the
sitting, runs the submission against the problem's own test cases, and records
the verdict. Python only: a canonical is Python, the test cases are
Python-shaped, and a second language is a runner rather than a record change.

**The engine is a learning platform, not a competitive one.** A verdict is
evidence about the user's own practice and ranks the user against nobody. A
solver who games a verdict misleads only their own board. So the drill loop
shows what helps a solver debug, and does not guard a verdict against the
solver.
## Where the rest lives

This file holds the views and the shape of the engine. The files beside it
specify everything else, in a folder per element of `model.toml`. A container
or a system with parts is a folder whose `README.md` holds its own boundary,
and each component is a file named by its id.

| Path | Holds |
|---|---|
| [`model.toml`](model.toml) | The engine's elements as one model: each element's stable id, its role, the doc that specifies it, the source files it owns, its relations, each flow as an ordered list of them, and each user journey. The views above, each flow's diagram in its page, and the journeys' table are generated from it |
| [`modules.md`](modules.md) | The engine's Python packages and the imports between them, grouped by the containers whose code reaches each package. Generated from `src/climb` and `model.toml` |
| [`client-modules.md`](client-modules.md) | The clients' TypeScript modules and the imports between them: the web app and the native app, then the shared packages per file, grouped by the clients that reach each file. Generated from the workspaces' sources |
| [`concepts/terms/`](concepts/terms/) | Every word this project gives its own meaning, a file per group |
| [`concepts/invariants.md`](concepts/invariants.md) | The properties the system holds at all times |
| [`concepts/repo-constraints.md`](concepts/repo-constraints.md) | How this repo is built, the meta-rule, and the calibration corpus |
| [`concepts/deployment.md`](concepts/deployment.md) | The one server: its storage, the dumps, the journal, the deploy, the secrets and the tunnel |
| [`concepts/machine-records.md`](concepts/machine-records.md) | What a model-written record carries, and content a session writes |
| [`concepts/log-records.md`](concepts/log-records.md) | What every log record carries, one user's log, export and erasure |
| [`concepts/techniques.md`](concepts/techniques.md) | The technique vocabulary and how a technique is claimed |
| [`concepts/ai-activities/`](concepts/ai-activities/README.md) | The AI engineering module's drills and desk tasks per pattern, how each key is proven by a run, simplicity graded by ablation, the spine, and the readiness bar a learner holds |
| [`concepts/ai-task-grading.md`](concepts/ai-task-grading.md) | The AI task record, how the harness grades a submission on the hidden set, why a regrade gives the same score, and the harness's boundary with the sandbox |
| [`journeys/`](journeys/README.md) | The user journeys: each one's start, end, screens, acts, flows and components, generated from `model.toml`, and the screens no journey reaches |
| [`flows/`](flows/) | The flows crossing containers, a page each with its generated sequence diagram: the drill loop, starting a card run, solving a rung, recalling a template |
| [`api/`](api/README.md) | One origin, JSON writes, client error reports, and a file per component: sign-in, app tokens, the sitting, the submission and its run caps, the runner, the pick and the rest |
| [`cli/`](cli/README.md) | Generation as a command run off the server, and a file or folder per component: generation and its states, difficulty, the classifier, the eval set, the matcher, the diagnoser, the exercise items, the seed and the calls |
| [`broker/`](broker/README.md) | Holding the container runtime's socket, and admitting one run at a time |
| [`sandbox/`](sandbox/README.md) | The container a run happens in, a child per case, and gVisor |
| [`database/`](database/README.md) | The one Postgres store, the data-class table as an index of every record, the tables and the migrations, and the schema graph of every table's foreign keys and owner, generated from the declared tables |
| [`proxy/`](proxy/README.md) | Caddy, its certificates and why it serves no files |
| [`content-repo/`](content-repo/README.md) | Cards, the card graph, how a card and a subtopic share a technique, modules, questions, lessons |
| [`core-package/`](core-package/README.md) | The three layers both clients share, the fixtures, every screen of both clients, and the knowledge module's rules |
| [`shared-editor/`](shared-editor/README.md) | The CodeMirror setup for editing Python that both clients import |
| [`web-app/`](web-app/README.md) | The structure of the pages, a folder per page with a wireframe per screen, a page's areas, the design system |
| [`native-app/`](native-app/README.md) | The phone client: offline practice, typing code, the editor's measurements |
