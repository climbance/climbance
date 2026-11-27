# Questions

A question asks about one fact, and a user answers it from memory.
`../core-package/knowledge/schedule.md` gives how the answers are scheduled.

- **A question carries a prompt, a kind and a format.** The kind is the
  module's own vocabulary, such as concept, output, pattern or debug. A module
  names which kinds carry a code snippet.
- **A question is answered in one of three formats.**
  - `choice`: three to eight options, one or more correct. The options are
    shuffled on every display, so a position carries no answer.
  - `short`: a typed reply, matched against the accepted replies after
    whitespace is removed throughout, and quotes and backticks at either
    end. Case is ignored unless the question says otherwise.
  - `open`: the user answers in their own head, reveals the key, and ticks the
    points recalled, the traps fallen into, and anything else said wrong.
- **The AI drill items add three formats**: `judge`, `trace` and `estimate`,
  as [`ai-drills.md`](ai-drills.md) gives.
- **An open question's key is two to six points.** Each point is one fact the
  answer has to contain. A trap is a known wrong claim, and a question carries
  up to three.
- **An open question is graded from the ticks.** Every point recalled with no
  trap and nothing else wrong grades `k`. Every point with a trap or something
  else wrong grades `p`, and so does some but not all of the points. No point
  recalled grades `n`.
- **A reply ending in `?` is a guess**, on `choice` and `short` alone. A guess
  is stored apart from whether the reply was correct, since a correct guess
  shows the fact is not yet held.
- **A question carries its explanation and its detail**: how the mechanism
  works, an example, pitfalls, version notes and a diagram, each optional but
  the mechanism. The detail is shown on request after an answer.
- **An open question's explanation and detail are optional, the mechanism
  included.** The key already carries the points an answer has to contain.
- **A wrong choice of a module written by concept names its misconception.**
  The seed resolves each one to the misconception's text, as
  `misconception_text`, since no client holds the concepts.
- **An open question is excluded from exams.** Its grade is the user's own
  report, and an exam reads a verdict the user did not give.
