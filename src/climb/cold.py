"""A cold sitting: an unseen problem with a score, served with nothing named
under a time limit. `api/rating.md` gives each rule."""

import random
from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict

from climb import mint
from climb.cases import CaseLog
from climb.log import AttemptLog, SittingStore
from climb.problems import ProblemStore
from climb.ratings import RatingLog, standing_ratings
from climb.schema import Attempt, CaseOutcome, Problem, ProblemDifficulty, Sitting
from climb.sitting import Refused, Submitted, get, lapsed, last_submitted, submit
from climb.solution_claims import load_problem
from climb.storage import Database

# `api/rating.md` gives why an hour
COLD_LIMIT_SEC = 3_600


class ColdFailure(BaseModel):
    """The first case a cold submission failed, by its number alone."""

    model_config = ConfigDict(frozen=True)

    number: int  # from 1, in the order the problem carries its cases
    outcome: CaseOutcome


class ColdSubmitted(BaseModel):
    model_config = ConfigDict(frozen=True)

    attempt: Attempt
    sitting: Sitting
    failure: ColdFailure | None  # none on a submission that passed every case


class Revealed(BaseModel):
    """What the page withheld while the sitting ran."""

    model_config = ConfigDict(frozen=True)

    title: str
    techniques: list[str]
    difficulty: ProblemDifficulty | None
    score: float | None


class ColdSeated(BaseModel):
    model_config = ConfigDict(frozen=True)

    statement: str
    signature: str | None
    sitting: Sitting
    elapsed_sec: float | None
    last: ColdSubmitted | None
    revealed: Revealed | None  # none while the sitting runs


def eligible(
    problems: Iterable[Problem],
    scored: set[str],
    sittings: Iterable[Sitting],
    attempts: Iterable[Attempt],
) -> list[str]:
    """The problems a cold sitting may serve one user: served, scored, and
    with no sitting or attempt of the user's on them."""
    seen = {one.problem_id for one in sittings} | {one.problem_id for one in attempts}
    return sorted(
        one.id for one in problems if one.served and one.id in scored and one.id not in seen
    )


def serve_cold(
    root: Database,
    *,
    user_id: str,
    device: str | None = None,
    now: datetime | None = None,
    draw: random.Random | None = None,
) -> ColdSeated:
    """The user's running cold sitting, or a new one on a problem drawn at
    random. One runs at a time, so a second press is no second loss."""
    at = now or datetime.now(UTC)
    store = SittingStore(root)
    mine = store.all(user_id)
    running = [one for one in mine if one.cold and one.ended_at is None and lapsed(one, at) is None]
    if running:
        return read(root, running[0].id, user_id=user_id, now=at)
    scored = set(standing_ratings(RatingLog(root).ratings()))
    candidates = eligible(
        ProblemStore(root).all(), scored, mine, AttemptLog(root).attempts(user_id)
    )
    if not candidates:
        raise Refused("no problem is left to serve cold")
    problem_id = (draw or random.Random()).choice(candidates)
    one = mint.sitting(user_id, problem_id, at, device, time_limit_sec=COLD_LIMIT_SEC)
    store.put(one)
    return read(root, one.id, user_id=user_id, now=at)


def read(
    root: Database, sitting_id: str, *, user_id: str, now: datetime | None = None
) -> ColdSeated:
    """A cold sitting with its statement, and what the page withheld once it
    has ended."""
    seated = get(ProblemStore(root), SittingStore(root), sitting_id, user_id=user_id, now=now)
    one = seated.sitting
    if not one.cold:
        raise Refused(f"sitting {sitting_id} is not cold")
    cases = CaseLog(root)
    last = last_submitted(AttemptLog(root), cases, one)
    return ColdSeated(
        statement=seated.statement,
        signature=seated.signature,
        sitting=one,
        elapsed_sec=seated.elapsed_sec,
        last=_numbered(last) if last else None,
        revealed=_revealed(root, one.problem_id) if one.ended_at else None,
    )


def submit_cold(
    root: Database, sitting_id: str, code: str, *, user_id: str, now: datetime | None = None
) -> ColdSubmitted:
    return _numbered(
        submit(
            SittingStore(root),
            CaseLog(root),
            AttemptLog(root),
            sitting_id,
            code,
            user_id=user_id,
            cold=True,
            now=now,
        )
    )


def _numbered(submitted: Submitted) -> ColdSubmitted:
    # a contest names the failing test and hides it: `api/rating.md`
    failed = next(
        (
            ColdFailure(number=number, outcome=result.outcome)
            for number, result in enumerate(submitted.verification.results, 1)
            if result.outcome is not CaseOutcome.PASSED
        ),
        None,
    )
    return ColdSubmitted(attempt=submitted.attempt, sitting=submitted.sitting, failure=failed)


def _revealed(root: Database, problem_id: str) -> Revealed:
    problem = load_problem(root, problem_id)
    if problem is None:
        raise ValueError(f"a cold sitting names no stored problem {problem_id}")
    stands = standing_ratings(RatingLog(root).for_problem(problem_id))
    return Revealed(
        title=problem.title,
        techniques=problem.techniques,
        difficulty=problem.difficulty,
        score=stands[problem_id].score if problem_id in stands else None,
    )
