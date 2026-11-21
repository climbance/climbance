# The difficulty judge

The difficulty judge is the model call that reads one problem's statement and
answers the contest rating it expects the problem to have. A problem's score
is the median of several of those answers, corrected by a line fitted on the
anchors. `climb difficulty judge` writes the scores.

## The judge

- **The judge is `gpt-oss-120b` at medium effort, pinned, and it reads the
  statement alone.** It sees no solution, no case, no title and no rated
  example. On the 42 held-out anchors this prompt ranked best of the six
  tried, at a Spearman correlation of 0.83 against 0.73 with 25 rated anchors
  in the prompt. Over all 132 anchors and two prompts, its expected Spearman
  correlation is about 0.75.
- **The judge's knowledge cutoff, June 2024, predates every anchor's
  contest.** A judge trained after the anchors' contests may remember their
  ratings, and its score on the anchors then measures memory as well as
  judgement. A stronger judge with a later cutoff is not chosen on a score the
  anchors cannot check.
- **A draw is one judge call on one statement, and the rating it answered.**
  The judge is sampled at the endpoint's default temperature, unlike the
  greedy answering sites in `../../concepts/machine-records.md`. Draws of one
  statement then differ, and their median is the verdict. A greedy judge would
  answer the same number on every draw, and the median would carry no more than
  one call.
- **A problem's judged rating is the median of its draws.** The median
  ignores a draw that misread the statement, where a mean moves with it. The
  draws of one statement agree within about 76 points, far less than the
  judge's error against the true rating. So the count of draws is set by the
  correction, not raised to buy precision.
- **A draw whose answer holds no rating is not stored.** Its call stays in the
  call log. A problem with fewer readable draws than the correction's count
  gets no rating, and the run reports how many problems it left unrated.

## The correction

- **A correction is the line from the judged rating to the contest scale.**
  The judge rates easy anchors too high: anchors rated 800 to 1200 are judged
  about 1315 on average. The line, `score = intercept + slope × judged`, is
  fitted by least squares on the fitted anchors' medians.
- **A correction is fitted for one judge and one prompt.** It names the
  judge's configuration, the instructions hash and the count of draws its
  medians took. The instructions hash is the hash of the judge's prompt with
  the statement left out. Every draw's own prompt hash differs, since each
  draw carries a different statement. A change to the model, the effort, the
  pin, the prompt or the count needs a new correction, since the line was
  fitted to that judge's habits.
- **A correction names the anchor set by its hash, and names no anchor.** The
  anchors' draws and their calls are kept beside the anchors, outside every
  repository, as `trials.md` gives for the anchors' trials. Their prompts hold
  third-party statements. The command fitting a correction reads those draws
  from a file named on the command line.
- **A correction's deviation is the standard deviation of the held-out
  anchors' residuals**, each the anchor's contest rating minus its corrected
  score. The held-out anchors play no part in the line, so their residuals
  measure the error a new problem's score carries. The probe measured about
  270 points.
- **Every rating under one correction carries the correction's deviation.**
  The spread between one statement's draws is small beside the judgement's
  error, so a per-problem deviation would add little. A deviation that varies
  per problem is deferred until the residuals show some problems judged
  worse than others.
- **The correction also stores the held-out Spearman correlation and the
  held-out mean absolute error.** These are the judge's measured quality on
  that anchor set. The Spearman correlation is the one metric a change to the
  judge or its prompt is kept by. The probe's held-out Spearman was about
  0.75.
- **The transfer from anchors to the corpus is not measured.** An anchor reads
  standard input, and a corpus problem's statement carries the signature of
  `solve`. No corpus problem has a contest rating. `fits.md` gives the one
  check the store can make on the corpus.

## The records

- **A `DifficultyCorrection` stores one correction.** It carries an
  engine-minted `id`, `created_at`, the `anchor_set` hash, the judge's `model`,
  `effort`, `pin` and `temperature`, the `instructions_hash`, the `draws`
  count, the `intercept` and `slope`, `anchors_fitted`, `anchors_held_out`,
  `held_out_spearman`, `held_out_mean_error` and the `deviation`. Corrections
  are product data, global and append-only.
- **A `DifficultyDraw` stores one draw on a corpus problem.** It carries an
  engine-minted `id`, `created_at`, the `problem_id`, the `judged` rating the
  call answered, and the call's provenance whole, as on every machine record.
  Draws are product data, global and append-only.
- **A `DifficultyRating` whose `source` is `judge` names its
  `correction_id` and its draws.** A link table, `difficulty_rating_draws`,
  holds one row per draw the median read. The rating's `score` is the corrected
  median, and its `deviation` is the correction's. The rating and its links
  are stored in one transaction.
- **A draw is stored apart from the rating that reads it.** A new correction
  for the same judge, prompt and count, fitted on a new anchor set, re-reads
  the stored draws and writes new ratings without a call.
- **The latest correction matching the code's judge stands.** A `judge` run
  refuses to start when no stored correction matches the configuration, the
  instructions hash and the count the code would send.

## The run

- **`climb difficulty correct` fits and stores a correction.** It reads the
  anchor list, the anchors' draws and their split, and prints the line and the
  held-out metrics. It stores the correction under `--write`.
- **`climb difficulty judge` rates every served problem with no `judge`
  rating under the standing correction.** It draws each
  problem the correction's count of times, within a `--budget`, and stores
  each rating with its draws under `--write`. A retired problem is not rated.
- **A problem landed after a run is rated by the next run.** Each score
  depends on its own statement and the shared correction alone, so one
  problem's score does not move when another is added. Rating a problem at
  landing, inside generation, is deferred until the corpus grows between
  judge runs.
