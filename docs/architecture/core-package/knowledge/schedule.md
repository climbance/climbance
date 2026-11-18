# The schedule

Each question's memory is FSRS-6, replayed from the user's answers.

- **Each answer becomes a rating.** An open question grades `k` to Good, `p` to
  Hard and `n` to Again. On `choice` and `short`, a correct reply that is not
  a guess rates Good, a correct guess Hard, and a wrong reply Again. Easy is
  never used.
- **An answer counts as a pass when it rates Good.**
- **A question's state is replayed from its answers in time order**, each at
  the moment it was given, starting from a new card in FSRS's sense. The
  state is stability, difficulty and the next due time. It is derived on
  every read and never stored.
- **The settings are py-fsrs's defaults**, each kept for its own reason:
  - The FSRS-6 default parameters. No user's log holds enough answers to fit
    parameters of its own, and both clients replay with the one set the
    snapshot publishes.
  - Desired retention 0.9. The default parameters were fitted against it,
    and the spaced check's band in `../../api/template-schedule.md` is read
    against it.
  - Learning steps of 1 and 10 minutes, and a relearning step of 10 minutes.
    A failed answer then comes back inside the same session, while the
    answer just read is still fresh.
  - A maximum interval of 36500 days. The cap is a hundred years, so FSRS
    alone sets every interval.
- **Retained means a stability of 21 days.** The bar is a convention, the
  interval Anki calls mature, and no measurement here set it. It is the
  setting most likely to move once the stored predictions are read.
- **Fuzzing is off.** The state is replayed on every read and on every device,
  and unseeded fuzz would give each replay a different due time.
- **Elapsed time between answers is counted in whole days.** Under a day,
  FSRS's short-term stability applies.
- **A question's state at a moment is one of five.**
  - unseen: no answer yet.
  - weak: the last answer was not a pass, however long ago.
  - due: the due time has passed.
  - retained: stability is at least 21 days.
  - learning: any other seen question, including one waiting on a step.
- **A question is servable when it is unseen or its due time has passed.** A
  weak question inside its step waits for the step. A queue serves servable
  questions first, and [`queues.md`](queues.md) names the two exceptions after
  them.
- **A question is passed once any of its answers was a pass**, and stays
  passed. A group is done when its passed share reaches the module's pass
  ratio.
