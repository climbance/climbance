"""The problems a card has the user solve, derived from the template matches
and the card's selector. A view, never stored: `content-repo/cards.md` gives
why.

Starting a card is here too, since the start draws the probes the ladder is
not allowed to hold.
"""

from collections.abc import Iterable, Sequence, Set
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel

from climb.board import candidates
from climb.log import CardRunLog
from climb.matches import coverage
from climb.mint import card_run
from climb.schema import (
    Attempt,
    Card,
    CardRun,
    MatchHead,
    Problem,
    ProblemDifficulty,
    Sitting,
    Solution,
    SolutionHead,
    TemplateMatch,
)
from climb.sitting import over

# how many probes a start draws. One until use says otherwise, which
# `flows/starting-a-card-run.md` names as deferred
PROBES = 1


class Rung(BaseModel):
    """One problem on a ladder, with the templates its canonicals display.

    A rung the selector filled covers none. `required` is derived from what the
    rung covers rather than stored, and a rung covering the optional template
    beside a core one offers that form as the alternative approach.
    """

    problem: Problem
    templates: list[str]  # template ids, in the order the card authored them
    required: bool
    # folded from the attempts made since the run began, never marked on the
    # rung: a ladder re-derived under a moved corpus keeps what was solved
    solved: bool = False
    # its last sitting since the run began ended with no submission:
    # `flows/solving-a-rung.md`
    skipped: bool = False
    # when the first match placing it was written, so graduation can leave out
    # a rung a later problem added: `api/card-states.md`. None on a fill rung
    joined: datetime | None = None


class Gap(BaseModel):
    """A core template no solution displays, named as the card names it.

    The card claims to teach the form, so the ladder reports the gap rather
    than substituting another problem for the rung. The next generation run is
    aimed at what this names.
    """

    template_id: str
    slug: str
    title: str


class Ladder(BaseModel):
    """What studying one card has the user solve."""

    card_slug: str
    rungs: list[Rung]
    gaps: list[Gap]


class CardState(StrEnum):
    """How far one user's study of one card has gone, derived on every read:
    `api/card-states.md`."""

    NOT_STARTED = "not_started"
    ACQUIRING = "acquiring"
    CONSOLIDATING = "consolidating"
    # reached by the graduation and lapse rules, neither written yet
    GRADUATED = "graduated"
    LAPSED = "lapsed"


def card_state(started: bool, rungs: Iterable[Rung]) -> CardState:
    if not started:
        return CardState.NOT_STARTED
    required = [rung for rung in rungs if rung.required]
    # a ladder holding no required rung is deferred in `api/card-states.md`, and
    # stays acquiring rather than claiming a ladder nobody solved
    if required and all(rung.solved for rung in required):
        return CardState.CONSOLIDATING
    return CardState.ACQUIRING


def met(run: CardRun | None, rungs: Iterable[Rung], attempts: Iterable[Attempt]) -> bool:
    """Whether a required card is met: `api/card-states.md`."""
    if run is None:
        return False
    if card_state(True, rungs) is not CardState.ACQUIRING:
        return True
    done = _solved(attempts, run.started_at)
    return any(one.problem_id in done for one in run.probes)


class Locked(Exception):
    """A start refused: `api/card-states.md`."""

    def __init__(self, waiting: list[Card]) -> None:
        super().__init__(f"locked until met: {', '.join(one.title for one in waiting)}")
        self.waiting = waiting


def locked_by(
    card: Card,
    cards: Iterable[Card],
    runs: CardRunLog,
    problems: Iterable[Problem],
    solutions: Iterable[Solution | SolutionHead],
    matches: Iterable[TemplateMatch | MatchHead],
    attempts: Iterable[Attempt],
    *,
    user_id: str,
) -> list[Card]:
    """The required cards the user has not met, in the order `card` names."""
    by_slug = {one.slug: one for one in cards}
    problems, solutions = list(problems), list(solutions)
    matches, attempts = list(matches), list(attempts)
    found: set[str] = set()
    for slug in dict.fromkeys(one.card for one in card.requires):
        required = by_slug[slug]  # the seed refused a requirement on no card
        run = runs.started(user_id, required.id)
        since = run.started_at if run else None
        rungs = ladder(required, problems, solutions, matches, attempts, since=since).rungs
        if met(run, rungs, attempts):
            found.add(slug)
    return [by_slug[slug] for slug in unmet(card, found)]


def unmet(card: Card, met: Set[str]) -> list[str]:
    """The required cards not yet met, by slug: locked while one is left."""
    return list(dict.fromkeys(one.card for one in card.requires if one.card not in met))


def ladder(
    card: Card,
    problems: Iterable[Problem],
    solutions: Iterable[Solution | SolutionHead],
    matches: Iterable[TemplateMatch | MatchHead],
    attempts: Iterable[Attempt],
    *,
    since: datetime | None = None,
    sittings: Iterable[Sitting] = (),
    now: datetime | None = None,
) -> Ladder:
    """A rung per template the corpus covers, then the selector's fill.

    The covering rungs come first, in the order the card authored its
    templates, and the fill follows least recently attempted before the run
    began. A retired
    problem fills no rung, here and in `coverage`. `since` is when the card's
    run began, and a rung is solved by an attempt finished after it: having
    solved the problem once is not having studied the form.
    """
    problems = list(problems)
    attempts = list(attempts)
    solutions = list(solutions)
    matches = list(matches)
    done = _solved(attempts, since)
    skipped = _skipped(sittings, attempts, since, now or datetime.now(UTC)) - done
    answers = {solution.id: solution.problem_id for solution in solutions}
    # ranked as at the start: `content-repo/cards.md`, a rung keeps its problem
    ranking = attempts if since is None else [one for one in attempts if one.finished_at < since]
    offered = _offered(card, problems, ranking)
    rank = {problem.id: place for place, problem in enumerate(offered)}
    by_id = {problem.id: problem for problem in problems if problem.served}

    covering: dict[str, list[str]] = {}
    gaps: list[Gap] = []
    titles = {template.id: template.title for template in card.templates}
    core = {template.id for template in card.templates if not template.optional}
    for covered in coverage([card], problems, solutions, matches):
        filling = sorted(
            {answers[one] for one in covered.solution_ids if answers.get(one) in by_id},
            key=lambda id: (id in skipped, rank.get(id, len(rank)), id),
        )
        if not filling:
            if covered.gap:
                gaps.append(
                    Gap(
                        template_id=covered.template_id,
                        slug=covered.template_slug,
                        title=titles[covered.template_id],
                    )
                )
            continue
        covering.setdefault(filling[0], []).append(covered.template_id)

    # the first record saying so, whichever writer stands now: a hand pass
    # confirming a rung later does not move when it joined
    placed: dict[tuple[str, str], datetime] = {}
    for match in matches:
        if match.matched and match.solution_id in answers:
            key = (match.template_id, answers[match.solution_id])
            placed[key] = min(placed.get(key, match.created_at), match.created_at)
    rungs = [
        Rung(
            problem=by_id[id],
            templates=templates,
            required=bool(core & set(templates)),
            solved=id in done,
            joined=min(
                (placed[(one, id)] for one in templates if (one, id) in placed), default=None
            ),
        )
        for id, templates in covering.items()
    ]
    # out to `size`, and never past a core template the corpus does not cover
    fill = [one for one in offered if one.id not in covering]
    # a skipped problem gives way to the selector's next
    fill = sorted(fill, key=lambda one: one.id in skipped)
    room = max(0, card.selector.size - len(rungs))
    # empty admits the whole range, easy included
    admits = not card.selector.difficulty or ProblemDifficulty.EASY in card.selector.difficulty
    if admits and not any(rung.problem.difficulty == ProblemDifficulty.EASY for rung in rungs):
        # `content-repo/cards.md`: a ladder whose selector admits easy holds an
        # easy rung, past `size` where the covering rungs already fill it
        easy = [one for one in fill if one.difficulty == ProblemDifficulty.EASY]
        fill = easy[:1] + [one for one in fill if one not in easy[:1]]
        room = max(room, len(easy[:1]))
    rungs += [
        Rung(problem=one, templates=[], required=False, solved=one.id in done)
        for one in fill[:room]
    ]
    rungs = [one.model_copy(update={"skipped": one.problem.id in skipped}) for one in rungs]
    # `content-repo/cards.md`: the ladder opens on its first easy rung
    easy = next((one for one in rungs if one.problem.difficulty == ProblemDifficulty.EASY), None)
    rungs.sort(key=lambda one: one is not easy)
    # served after the rungs not skipped, each part in the ladder's order
    rungs.sort(key=lambda one: one.skipped)
    return Ladder(card_slug=card.slug, rungs=rungs, gaps=gaps)


def next_rung(rungs: Sequence[Rung]) -> Rung | None:
    """The rung a card offers next: `api/pick.md`."""
    opening = _opening(rungs)
    open_ = [one for one in rungs if not one.solved]
    return min(
        open_, key=lambda one: (one.skipped, one is not opening and not one.required), default=None
    )


def _opening(rungs: Sequence[Rung]) -> Rung | None:
    """The ladder's first rung where it is easy: offered before the required."""
    return rungs[0] if rungs and rungs[0].problem.difficulty == ProblemDifficulty.EASY else None


def _solved(attempts: Iterable[Attempt], since: datetime | None) -> set[str]:
    """The problems solved since the run began. No run measures nothing, since
    the ladder is measured from the start."""
    if since is None:
        return set()
    return {
        attempt.problem_id
        for attempt in attempts
        if attempt.solved_unaided and attempt.finished_at >= since
    }


def _skipped(
    sittings: Iterable[Sitting], attempts: Iterable[Attempt], since: datetime | None, now: datetime
) -> set[str]:
    """The problems whose last sitting since the run began ended with no
    submission. No run skips nothing, as it solves nothing."""
    if since is None:
        return set()
    submitted = {attempt.sitting_id for attempt in attempts}
    last: dict[str, Sitting] = {}
    for one in sorted(sittings, key=lambda one: one.started_at):
        if one.started_at >= since:
            last[one.problem_id] = one
    return {id for id, one in last.items() if over(one, now) and one.id not in submitted}


def _offered(card: Card, problems: Iterable[Problem], attempts: Iterable[Attempt]) -> list[Problem]:
    """The selector's problems, least recently attempted first, as a
    technique's candidates are ordered."""
    wanted = set(card.selector.difficulty)
    return [
        row.problem
        for row in candidates(card.selector.technique, problems, attempts)
        if not wanted or row.problem.difficulty in wanted
    ]


def start(
    runs: CardRunLog,
    card: Card,
    cards: Iterable[Card],
    problems: Iterable[Problem],
    solutions: Iterable[Solution | SolutionHead],
    matches: Iterable[TemplateMatch | MatchHead],
    attempts: Iterable[Attempt],
    *,
    user_id: str,
) -> CardRun:
    """The run a start mints, with the probes drawn in the same act.

    The ladder is measured from the start, so a run reaches the store carrying
    what the start drew. A card already started is returned rather than started
    again: `flows/starting-a-card-run.md` leaves a second run deferred. A locked
    card raises `Locked`.
    """
    open_already = runs.started(user_id, card.id)
    if open_already is not None:
        return open_already
    problems, solutions = list(problems), list(solutions)
    matches, attempts = list(matches), list(attempts)
    waiting = locked_by(card, cards, runs, problems, solutions, matches, attempts, user_id=user_id)
    if waiting:
        raise Locked(waiting)
    resolved = ladder(card, problems, solutions, matches, attempts)
    run = card_run(user_id, card.id, probes(card, resolved, problems, attempts))
    runs.append(run)
    return run


def probes(
    card: Card,
    resolved: Ladder,
    problems: Iterable[Problem],
    attempts: Iterable[Attempt],
    count: int = PROBES,
) -> list[str]:
    """The problems a start offers as probes: the card's technique, unseen
    first, then least recently attempted, and never one the ladder holds.

    The whole technique rather than the selector's own filters. The filters
    narrow what the ladder teaches, and a probe asks whether the technique is
    recognised at all.
    """
    attempts = list(attempts)
    taught = {rung.problem.id for rung in resolved.rungs}
    seen = {attempt.problem_id for attempt in attempts}
    offered = [
        row.problem.id
        for row in candidates(card.selector.technique, problems, attempts)
        if row.problem.id not in taught
    ]
    return sorted(offered, key=lambda id: id in seen)[:count]
