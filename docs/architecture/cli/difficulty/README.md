# Difficulty

A problem's difficulty is a score on the contest scale, with a deviation. The
label a problem is served with, easy, medium or hard, is derived from that
score. The difficulty judge, a model reading the statement alone, writes the
scores through `climb difficulty judge`. A `user` rating is written by hand.

| File | Holds |
|---|---|
| [`judge.md`](judge.md) | The difficulty judge: its draws, the correction to the contest scale, the records and the run |
| [`fits.md`](fits.md) | The panel, the anchors, the first fit's result, and what the trials are for now |
| [`trials.md`](trials.md) | A panel member's solution to one problem |
| [`criteria.md`](criteria.md) | What easy, medium and hard mean |
| [`easy-templates.md`](easy-templates.md) | The templates that admit an easy problem |

## The score and the label

- **A difficulty score reads on the contest scale.** The contest scale is the
  rating scale of the public programming contests. There a problem's rating is
  the contestant rating at which a solve is expected half the time. A score in
  those units says how hard a problem is to anyone who has entered a contest,
  where a label says it in three words.
- **A score carries its deviation**, one standard error on the contest scale.
  A rating method reports how sure it is, and a reader comparing a user with a
  problem needs that certainty as much as the score.
- **The label is the band the standing score falls in.** A band is a range of
  scores one label covers, and the three bands are a fixed table in the code.
  One number then answers both the score and the label, so the two never
  disagree.
- **A label reads on the scale of the public problem platforms.** Easy,
  medium and hard mean what the platforms' three levels mean, since a user
  compares a label with those. [`criteria.md`](criteria.md) gives the
  criteria for each level.
- **The bands' cuts are read from the judge's first scores of the corpus.** A
  cut is placed where the derived labels agree most often with the labels the
  generator wrote to the criteria, on the served problems. The criteria then
  keep the meaning a label had before scores existed.
- **Medium starts at 1100.** On the 133 served problems of the first judge run,
  a cut between the scores 1058 and 1109 agrees with the generator's label on
  97 problems, the most of any cut. The provisional cut at 1300 agreed on 85.
  Most scores lie within one deviation, about 265, of the cut, so one
  problem's label is uncertain even where the labels agree in aggregate.
- **Hard starts at 1900, a cut the corpus cannot set.** The generator wrote 3
  served problems as hard, and the judge scored them 1312 to 1414, among the
  medium ones. No corpus problem scored above 1567. Every hard cut therefore
  lowers agreement, and the cut keeps its provisional value. The cut is read
  again once the corpus holds problems the judge scores above 1600.
- **Whether a ladder requires an easy rung of a user who passed the recall is
  deferred** until real sittings show what the easy rung adds. A recall checks
  the user types the form, and an easy problem that the user sees it.
- **A problem's `difficulty` is the label the generator aimed at, and stays
  as written.** The generator is told a label by `generate --difficulty`, and
  writes to the criteria. A problem is never edited, so a score found
  later cannot overwrite that field.

## Anchors

- **Anchors link the scores to the contest scale.** An anchor is an external
  problem whose contest rating was fitted from the contestants who solved it.
  The judge's correction is fitted on them, as [`judge.md`](judge.md) gives.
- **An anchor is never served, never stored with the corpus and never in git.**
  It is a third-party problem, and `../../concepts/invariants.md` keeps
  every third-party statement and case out of git. Each anchor's licence is
  recorded where the anchors are kept, outside this repository.
- **The anchor set is fixed before any call reads it, and named by its hash.**
  A correction cites the hash, so a score is traceable to the anchors without
  naming one. A changed anchor set is a new hash, and the corrections on the
  old one stay readable.
- **Some anchors are held out of every fitted line.** Their residuals measure
  the error of a score on a problem the line did not see.

## Ratings

- **A `DifficultyRating` stores one judgement of one problem's score.** It
  carries an engine-minted `id`, the `problem_id`, the `score`, the
  `deviation`, its `source` and `created_at`. A rating with `source` `judge`
  names its correction by `correction_id`, and its draws, as
  [`judge.md`](judge.md) gives. A rating with `source` `user` names nothing
  more, and its deviation is deferred.
- **Ratings are product data, global and append-only.** A problem is served to
  every user, so its score is the same for every user. A rating replaced by a
  later one stays readable beside it.
- **The standing difficulty is read at every read and never stored.** The
  standing rating answers, by the standing rule. A `user` rating stands over a
  `judge` one, and among each source's ratings the latest stands. With no
  rating, the problem has no score, and its label is the generator's
  `difficulty`.
- **A problem landed after the latest judge run has no score until the next
  run rates it.** The judge rates each problem from its own statement, so the
  new score needs no other problem rated again.
- **The `fit` source is removed with the `DifficultyFit` record.** No fit was
  ever stored, so no rating names one, and the removal deletes no row.
  [`fits.md`](fits.md) gives why the panel's fit is not the score's source.
- **Every reader of a label reads the standing difficulty.** These readers are
  the badge, the listing's filter and a card's selector.
- **A loaded problem carries the label of its standing score in
  `difficulty`.** The loader folds the ratings in, as it folds the derived
  techniques in. The problem store alone returns the generator's label. A
  reader of the score reads the standing rating, since no record of the
  problem holds a score.
- **A `user` rating is written by hand, in the terminal, beside retirement.**
  It names a score on the contest scale. A learner's reading of a problem does
  not change the score another user is served.
- **The label ratings stored before scores existed are deleted** when the
  `score` field lands, after their labels have informed the bands' cuts. A
  rating carrying a label alone would be a second shape every reader branches
  on, as `../../concepts/repo-constraints.md` gives.
- **A difficulty estimated from users' attempts is deferred.** Whether an
  estimate is a rating with a source of its own is decided when it is planned.
