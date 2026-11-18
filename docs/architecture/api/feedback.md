# Feedback

A user's note to the author about the engine. A `Feedback` record holds the
client it was sent from, the path of the page it was sent from, and the note.

- **The note is required, and at most 2000 characters.** A blank note passes a
  presence check while saying nothing.
- **The record names the client and the page.** The two clients' paths differ,
  so the path alone does not say which screen the note is about.
- **A user's feedback is capped as a run is**, at 10 a minute and 60 an hour.
  Each note is a row the author reads, and the cap is counted over the user's
  own records.
- **The author reads the feedback in the terminal.** `climb feedback` lists
  every note, newest first.
- **Feedback is private to the user**, exported and erased with the rest of
  the log. The author reads it as the operator, as the author reads the rest
  of the store.

Deferred, since only use answers it:

- A reply to the user once the author has read the note.
