# The product page

The page at `/author/product`, in the author area: how many learners use the
product, how much they practise, and how many come back. `../README.md` gives
who reaches it, and why the page counts across users and lists none.

[`product.md`](product.md) draws the page at low fidelity.

- **An act is one record a learner's practice writes**: a sitting, an
  attempt, an answer, a recall attempt, a judgement or a fill. Each figure on
  the page counts acts or the users behind them. A sign-in and a settings
  change are not acts, since neither is practice.
- **A user with the author role is left out of every figure.** The author's
  own log is the eval set's, and it would otherwise count as the most active
  learner.
- **The users read as three counts**: invitations held, users who signed in
  at least once, and active learners. An active learner is a user with an
  act in the last 7 days.
- **The days read as one row per day for the last 30 days**: the sittings,
  the attempts and the answers that day, and the users with an act that day.
  A day with no act still reads a row of zeros, so a gap reads as a gap.
- **Retention at 7 days is the share of users who acted again 7 days or more
  after their first act**, counted over the users whose first act is at
  least 7 days old. Retention at 30 days reads the same at 30. Each reads as
  `m of n` beside the share, since a share over a handful of users means
  little without its denominator.
- **Each count is one grouped query in the store**, and returns no user id
  to the page. `../README.md` gives why.
