# Projection

A user's projected contest rating: one number on the contest scale, with its
deviation, read from each technique's chance to solve. The measured rating in
`rating.md` reads the user's cold sittings alone. The projected rating reads
every sitting, through the abilities `mastery.md` gives, and predicts the
rating the user would reach in a contest. This file gives the contest the
projection is read over, the expected solves, and the conversion to a rating.

## The representative contest

- **The contest is every rated problem of one year of rated rounds on one
  public contest platform**, each with its contest rating and its tags. The
  rounds started from 2025-11-23 to 2026-11-22, and 593 of their problems
  carry a rating. The private research repository names the platform, the
  rounds counted, the fetch and the script.
- **Only an aggregate is stored**: `src/climb/contest.json` holds each rating
  and set of needed techniques, with the count of problems carrying them. No
  statement, title or problem identifier is stored. External data calibrates
  the engine and is never served.
- **The contest pools every division.** A user's division follows from the
  user's rating, so choosing one would read the projection back into the
  contest it is computed over. The count of problems per contest leaves the
  rating unchanged, since both sides of the conversion below scale by it.
- **A tag becomes a need when it names an engine technique.** The script's
  map sends `math`, `number theory`, `combinatorics` and the other counting
  tags to `math`. The tag for depth-first and breadth-first search becomes one
  need met by either technique.
- **A tag naming no engine technique is left out.** 77% of the problems
  carry such a tag, mostly `constructive algorithms`, `data structures`,
  `implementation`, `brute force`, `trees` and `graphs`. Reading each such tag
  at the start ability would make the start decide most problems, and the
  projection would then repeat the measured rating.
- **A problem with no need left is read at the start ability**, as a
  technique no sitting reached is. 8% of the problems are read so.

## The expected solves

- **A problem's ability is its weakest need's.** A need's ability is the
  ability of its strongest technique. This follows the chance to solve in
  `mastery.md`, where a problem's chance is its weakest technique's.
- **The expected solves are the sum of each problem's chance**, the logistic
  curve of `mastery.md` between the problem's ability and its rating. A solve
  counts 1 whatever the problem's rating. A contest's points and penalties
  rank contestants, and the problem's rating already carries its difficulty.

## The rating

- **The projected rating is the performance rating of the expected solves.**
  It is the rating at which a contestant equally able in every technique
  expects the same number of solves on the contest. A user whose abilities
  are all one value therefore projects that value.
- **The rating is read at each ability's mean.** The mean abilities give the
  chances, so each ability's deviation enters the projected rating's
  deviation alone.
- **The deviation is the projection's spread over 400 draws of the
  abilities.** Each draw takes every practised technique's ability from a
  normal curve at its rating and deviation. The deviation is the standard
  deviation of the 400 projected ratings.
- **Every technique no sitting reached shares one draw of the start.** The
  start is one prior, the measured rating, so its error moves every
  unpractised technique together. Independent draws narrowed a new user's
  deviation from 350 to 143, an assurance no sitting gave.
- **The draws are seeded**, so one log reads one deviation on every read.
- **The practised abilities are drawn independently.** Each starts at the
  measured rating, so their errors are correlated, and the deviation is
  narrower than the true one. A joint draw waits on users' sittings to fit
  the correlation.

## The interface

- **`GET /api/projection` returns the rating, its deviation and the count of
  techniques it read**: the techniques a sitting reached among those the
  contest needs. The board's cold panel shows the projected rating under the
  measured one, as `../web-app/pages/practice/cold/README.md` gives. A projection above the
  measured rating says the user knows the material and loses time under the
  clock, and a projection below it says the reverse.
- **The projection is replayed from the log on every read, and never
  stored.** The abilities are replayed on every read, so a stored projection
  would be a copy a recalibration leaves wrong.
- **No `Prediction` carries the projection.** The projection is scored against
  the measured rating once users who compete are measured. That score reads
  the log at the moment of each comparison, and needs no stored copy.

## Deferred

- Whether a `Prediction` carries the chance to solve, decided once the
  projection is scored.
- A contest per division, once a user's rating chooses the division.
- Reading an unmapped tag at the start ability, compared by the projection's
  error against the measured rating.
- A chance for the tags no engine technique names, such as `data
  structures`, once the vocabulary or the claims reach them.
