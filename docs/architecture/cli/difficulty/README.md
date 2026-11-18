# Difficulty

A problem's difficulty is a score on the contest scale, with a deviation. The
label a problem is served with, easy, medium or hard, is derived from that
score. `climb difficulty` runs the panel's trials and fits the scores, and a
`user` rating is written by hand.

| File | Holds |
|---|---|
| [`fits.md`](fits.md) | The difficulty fit: the panel, the anchors, the first fit's result |
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
- **The bands' cuts are set when the first fit scores the corpus.** They are
  read so that the derived labels agree with the criteria on the served
  problems as often as possible. The criteria then keep the meaning a label had
  before scores existed.
- **Whether a ladder requires an easy rung of a user who passed the recall is
  deferred** until real sittings show what the easy rung adds. A recall checks
  the user types the form, and an easy problem that the user sees it.
- **A problem's `difficulty` is the label the generator aimed at, and stays
  as written.** The generator is told a label by `generate --difficulty`, and
  writes to the criteria. A problem is never edited, so a score found
  later cannot overwrite that field.

## Ratings

- **A `DifficultyRating` stores one judgement of one problem's score.** It
  carries an engine-minted `id`, the `problem_id`, the `score`, the
  `deviation`, its `source` and `created_at`. A rating with `source` `fit`
  names the difficulty fit that computed it, by `fit_id`. A rating with
  `source` `user` names nothing more.
- **Ratings are product data, global and append-only.** A problem is served to
  every user, so its score is the same for every user. A rating replaced by a
  later one stays readable beside it.
- **The standing difficulty is read at every read and never stored.** The
  standing rating answers, by the standing rule. A `user` rating stands over a
  `fit` one, and among each source's ratings the latest stands. With no
  rating, the problem has no score, and its label is the generator's
  `difficulty`.
- **A problem landed after the latest fit has no score until a fit reads it.**
  Whether a new problem is scored against the members' fitted abilities, or by
  fitting again, is deferred to the first problem landed after the first fit.
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
  on, as `../../README.md` `## Repo constraints` gives.
- **A difficulty estimated from users' attempts is deferred.** Whether an
  estimate is a rating with a source of its own is decided when it is planned.
