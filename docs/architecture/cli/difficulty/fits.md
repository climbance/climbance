# Difficulty fits

A difficulty fit scores every problem it reads from the trials of a panel of
models, and links those scores to the contest scale through anchors.

## The panel

- **The scores come from models, and no user's attempt is needed.** A panel
  is a set of model configurations, each a member, chosen so that the members
  range from weak to strong. A trial is one member's solution to one problem,
  run against that problem's cases.
- **A fit is a difficulty-only item response model over the trials.** Each
  member has an ability and each problem a difficulty. A member solves a
  problem with the logistic chance of the ability minus the difficulty. A
  discrimination per problem is deferred until it lowers the log-loss below.
- **The members are chosen so that solve rates spread between 0 and 1** across
  the corpus. A problem every member solves, or none, carries no difficulty a
  fit can read. The pilot set the first panel: five members, from an 8B
  model with no reasoning to a 120B reasoning model at high effort, with 3
  trials each per problem.
- **Every anchor below 2200 had a mixed outcome in the pilot.** At least one
  of its 15 trials passed and one failed, over 24 anchors. Without the member
  with no reasoning, six easy anchors were solved by every member, and a fit
  reads nothing from them.
- **The panel reads nothing at 2200 and above.** On anchors rated 2200 and
  above the pilot's members solved almost nothing, so a fit could link no
  score in that range. A stronger member is deferred until the corpus needs
  scores there.

## Anchors

- **Anchors link the fit to the contest scale.** An anchor is an external
  problem whose contest rating was fitted from the contestants who solved it.
  The panel's trials on the anchors are fitted with the corpus. A linear
  mapping from the fitted difficulty to the contest rating, set on the
  anchors, then converts every problem's difficulty into a score.
- **An anchor is never served, never stored with the corpus and never in git.**
  It is a third-party problem, and `../../README.md` `## Invariants` keeps
  every third-party statement and case out of git. Each anchor's licence is
  recorded where the anchors are kept, outside this repository.
- **The anchor set is fixed before any trial runs, and named by its hash.**
  The fit record cites the hash, so a fit's scores are traceable to the anchors
  without naming one. A changed anchor set is a new hash, and the fits on the
  old one stay readable.
- **Some anchors are held out of the mapping.** The log-loss of the panel's
  trials on them is the fit's one metric. Each held-out anchor's contest rating
  is converted back to a fitted difficulty, and the chance each member solves
  it is read from the logistic curve. A change to the panel, the model or the
  mapping is kept only where it lowers that log-loss.

## The record

- **A `DifficultyFit` stores one fit.** It carries an engine-minted `id`,
  `created_at`, the members' configurations, the anchor set's hash, the
  mapping, each member's ability and the held-out log-loss. Each problem's
  score is a `DifficultyRating` naming the fit. Fits are product data, global
  and append-only.
- **The latest fit stands for every problem it read.** One fit scores the
  corpus at once, so its problems' ratings are mutually consistent. A rating
  from an earlier fit stays readable, and no reader mixes two fits' scores.

## The first fit

- **No fit is stored yet, so no problem has a `fit` rating.** The first fit,
  on 2026-11-17, did not beat its baseline on 42 held-out anchors below 2200.
  The baseline predicts each member's solve rate on the fitted anchors, at a
  log-loss of 0.491. The mapping as designed, from fitted difficulty to
  rating, scored 1.71.
- **The best variant's gain was within noise.** That variant fits the mapping
  from rating to difficulty on the anchors alone, and widens each predicted
  chance by the anchors' scatter around it. It scored 0.480. The 95%
  bootstrap interval of its gain over the baseline, resampling anchors, was
  −0.047 to +0.026.
- **The panel does not separate the easier anchors.** Its fitted difficulty
  ranks the 132 anchors at a Spearman correlation of 0.33 with their rating.
  Solve rates stay flat from 800 to 1500. The strongest member solves almost
  every anchor there, and the weaker members fail on edge cases about as often
  at 800 as at 1400. The contest scale is deferred until a panel lowers the
  held-out log-loss below the baseline's.
