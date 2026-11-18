# Matcher

The matcher is the model call reading a canonical beside its statement and
naming the card templates it displays. It writes template matches: which
solutions display which of a card's templates. A form is displayed by code, so
the subject is a solution rather than a problem. Matches are the engine's own
work: an author names no solution, so nothing is authored here either.

## The generator's match

- **The canonical a problem was generated with asserts its own match.** Its
  target was that template, so the pair is provenance rather than an
  inference,
  and the record names `generator` as its source. No call is paid to learn
  what the generator was told to write.
- **No other canonical asserts anything.** The rest are enumerated from the
  problem itself, and nobody named a form for them. So every template they
  display is the matcher's answer, and one generator's match per problem is
  the most there can be.
- **A generator's match carries no configuration**, as a user match
  carries none. The all-or-none rule is about machine matches, which are
  re-derivable
  and so must say by what. Re-deriving this pair would mean writing the
  solution again, and the solution already names the call that wrote it.
- **It is only ever positive.** The generator asserts the form its target
  named. Every other template the solution displays is the matcher's question,
  and a generator saying nothing about a template is not a negative on it.
- **The generator's match is stored only for a canonical that passed.** A
  solution that failed the cases demonstrates nothing about the form, so a
  failure is not a negative either.
- **A demonstration is free ground truth on a pair a matcher read.** It
  confirms a positive, and on a pair the matcher scored negative it is a caught
  false negative. It replaces no hand pass: the pairs it reaches are the ones a
  ladder wanted, which is a sample nobody drew at random.
- **The same fact sits on the problem and in a match.** `target_template_id`
  names the template the problem's target named, and the first canonical's match
  names the same one. They cannot drift, because generation writes both in one
  act. The canonicals of a problem written for a technique target still carry
  their own matches, once that target lands, as `../corpus.md` defers it.

## What the matcher answers

- **The matcher answers what generation cannot assert**: which templates a
  solution displays besides the one it was written for, and whether the
  generator's own claim holds. The first answer lets a rung cover a core
  template and an optional one at once. The second answer is the only check on
  a generator drifting from its target.
- **The candidates are scoped through the problem.** A solution is offered to
  the cards whose technique its problem carries, which bounds the pairs a call
  asks about and keeps a per-pair negative finite. The scoping survived the
  subject moving, because a solution answers exactly one problem.
- **The matcher's record is deferred** where that scoping
  does not reach: a solution displaying a form outside its problem's carded
  techniques is a pair nothing offers. Whether the record then becomes one
  naming the templates it found is the open question. Either shape must give
  staleness by configuration: a re-run reads the solutions not yet read at the
  current prompt hash, and nothing else.
- **Written after the solution lands, never before.** The template is minted
  at card import, and the solution when the problem lands. So a match cannot
  be authored against a seed file.
- **Procedure templates are excluded.** A framing procedure is displayed by
  every solution its technique reaches, so a per-solution verdict carries no
  information.
- **Re-derivation is the normal path, not an exception.** A attempt claim
  asks about one attempt, and the question never changes. A match asks about a
  template against a corpus of solutions that grows with every enumeration run.
- **An empty answer is negatives, not a decline.** A call naming no template
  asserts that each candidate it was given does not match. A claim naming
  nothing answers nothing, and the difference is in the record shape rather
  than in the model's behaviour. The stored form of an empty answer follows
  the deferred shape, and either way it is a verdict rather than a refusal to
  read.

## Which match stands

- **Three writers, ordered by what each of them knew.** A user match
  stands over both machine sources. A generator's match stands over a
  matcher's match on the same pair, because the generator knew and the
  matcher inferred.
- **A generator's match and a user match are one record per template and
  solution.**
  Each answers one pair, and pairs are independent: solutions arrive one at a
  time, and a set record would rewrite pairs already settled every time the
  corpus grew.
- **A card's relation to a problem is a fold over its canonicals**, never a
  record of its own. A rung is earned when some canonical of the problem
  displays some template of the card. No record asserts in one place that a
  problem belongs to a card, so no record is rewritten when one verdict
  changes.
- **A user record settles what stands, not what has been read.** The run path
  skips a solution only where the hand pass settled every pair the call would
  have asked about. So the record a skip needs follows the deferred shape. The
  eval reads pairs matched by hand on purpose, because reading them is the
  measurement.
- **A user match records the verdicts its author saw**, as a claim does. It is
  written on every pair the answer settles, negatives included, because the
  pairs the user saw are a fact about the sitting rather than about the
  verdict.

## Scoring a matcher

- **Agreement is per pair, grouped per template.** A call carrying six pairs
  saves requests, and is not a unit of truth. Grouping follows the ladder: a
  form the matcher over-matches fills its rung with problems that do not teach
  it, and one number over the card would average that away.
- **No score is taken over a set, and accuracy is not the metric.** A match
  asserts a pair, and a matcher that says yes to everything is already visible
  as a false positive on every template. Most pairs are negative, so a matcher
  naming nothing would score in the nineties and resolve an empty ladder. The
  score covers the positive verdicts, both directions: the templates the user
  named and the machine missed, and the templates the machine named and the
  user did not.
- **The first hand pass calibrates, a blind one measures.** Matching by hand
  draws the line between displaying a form and merely admitting it. A score
  taken over the pairs that drew that line measures agreement with itself. The
  eval set is matched by hand from the templates alone, and configurations are
  compared over the pairs both read. The rules `../log.md` gives for scoring an
  attempt claim apply here unchanged.
- **The matcher score is deferred until two matcher configurations are
  compared.** `climb score` scores attempt claims alone today, and no command
  scores a match.
