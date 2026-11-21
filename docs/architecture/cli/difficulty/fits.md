# The panel and its fits

A difficulty fit read each problem's difficulty from the trials of a panel of
models, and linked it to the contest scale through anchors. The first fit
failed its metric, so the score comes from the difficulty judge instead, as
[`judge.md`](judge.md) gives. This file keeps the panel's design and the
measurement that set it aside, and says what the stored trials are for now.

## What the trials are for now

- **The trials stay in the store, and no score is read from them.** They are
  product data, append-only, and cost money to run again.
- **The trials are the one check of the judge on the corpus.** No corpus
  problem has a contest rating, so the judge's error there cannot be measured.
  A problem the panel's members solve less often should not be judged easier.
  The Spearman correlation between a problem's judged score and its pooled
  solve rate is that check, and it is reported beside the first judged
  ratings. The panel ranks the anchors weakly, so a low correlation on the
  corpus is weak evidence against the judge.
- **The panel's trials also find a problem no member solves.** Such a problem
  may be defective rather than hard. Reading them that way is deferred until a
  retirement review asks for it.
- **`climb difficulty trials` stays, and `climb difficulty fit` is removed
  with the `DifficultyFit` record.** No fit was stored, so the removal deletes
  no row. A fit that ever beats its baseline is designed again then, against
  the judge it would replace. The fitting code stays in `climb-lab`'s
  `research/`, where the first fit's variants ran.

## The panel

- **A fit read difficulty from models, and needed no user's attempt.** A panel
  is a set of model configurations, each a member, chosen so that the members
  range from weak to strong. A trial is one member's solution to one problem,
  run against that problem's cases.
- **A fit is a difficulty-only item response model over the trials.** Each
  member has an ability and each problem a difficulty. A member solves a
  problem with the logistic chance of the ability minus the difficulty.
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
  score in that range.

## The metric

- **The fit's one metric was the log-loss of the panel's trials on the
  held-out anchors.** Each held-out anchor's contest rating is converted back
  to a fitted difficulty, and the chance each member solves it is read from the
  logistic curve. A linear mapping, set on the fitted anchors, converts between
  fitted difficulty and contest rating. The anchors are the ones the judge's
  correction is fitted on, as [`README.md`](README.md) `## Anchors` gives.

## The first fit

- **No fit was stored, so no problem has a `fit` rating.** The first fit,
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
  at 800 as at 1400.
- **The members agree with each other on which anchors are hard**, at a
  Spearman correlation of 0.4 to 0.75 between two members' solve rates. That
  shared hardness does not follow the contest rating. More trials or more
  members of one model family would measure the same hardness again, so the
  panel search ended and the judge replaced the fit.
