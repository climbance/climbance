# A queue

The page at `/knowledge/queue` and the phone's quiz screen: one question at a
time, from the next queue, the review queue or a filtered queue.
`../../../../core-package/knowledge/queues.md` gives the queues.

## The path and a reload

- **The queue's path is `/knowledge/queue`, and `?mode=` names the queue**:
  next, review or filtered. A filtered queue's URL carries the sheet's
  choices too: `?module=`, `&topic=`, `&sub=`, `&level=`, `&kind=` and
  `&due=`.
- **A reload starts a queue of the same mode again**, a filtered queue on the
  choices its URL carries. The answers given before the reload are in the
  log already, so the next pick reads them. The web then holds one reload
  rule for its three queues.
- **A filtered queue's URL is a link to that drill.** It writes no record,
  so the choices reach no other device.
- **A choice naming content the store no longer holds degrades**, as a focus
  does. An unknown topic keeps the module, an unknown subtopic keeps the
  topic, and an unknown module returns to the home.
- **A reload loses the count and the score of the queue it ended.** The phone
  holds a running queue in memory alone, so a killed app loses the same. A
  copy of the running queue kept in the browser would make one client keep
  what the other loses.

## Answering

- **The queue serves one question at a time, and the page asks for one act at
  a time.** An unanswered question asks for the answer. An answered one reads
  its verdict and the explanation, and Next is the act.
- **A wrong choice the user picked names the misconception it embodies**, in
  the verdict, on both clients. The misconception is the belief that leads to
  the choice, so the user can check it against their own reasoning without
  opening the detail.
- **An answered question offers its detail on a press**: how it works, the
  example, the pitfalls, the version notes and the diagram, each where the
  question carries one.
- **An open question reveals its key on a press.** The user then ticks the
  points recalled, the traps fallen into, and whether they said anything else
  wrong. `../../../../content-repo/questions.md` gives the grade the ticks
  make.
- **A keyboard answers the queue.** A digit picks an option, and Enter submits
  or moves to the next question. A reader at a keyboard answers faster than by
  pointer.
- **The phone types a `short` reply on a keyboard of the app's own, and the
  system keyboard never opens.** Two rows of symbols sit above the digits and
  the letters, so a reply needs no layer. A layer holds the rare symbols and
  `True`, `False` and `None`, behind a key that names it.
- **Stop ends the queue and stores its stint**, and the page reads a summary
  of the answers given. Leaving the queue through the navigation stops it the
  same way. A closed tab stores no stint, and the answers given stay.

## Lessons inside the queue

- **The detail links the lessons teaching the question, and names each one
  already read.** A reader then knows before opening a lesson whether it is
  new. A lesson is marked read only on the lesson itself, since a mark given
  from a link records a reading that never happened.
- **A lesson the queue offers is a stop in the queue**, on both clients: the
  lesson's title, its reading time, why it is offered, and Read and Later as
  its presses. The reading time lets the reader choose between Read and Later
  before opening the lesson. Read
  opens the lesson over the running queue, with its minutes, Mark read and
  its links to other lessons. Closing the lesson returns to the queue, and
  so does Mark read.
- **Reading a lesson ends no queue.** The web opens the lesson in a dialog
  over the queue, and the phone opens it as a screen above the queue. A
  lesson an answer's detail links to opens the same way, so a reader never
  loses a running queue to a link.
