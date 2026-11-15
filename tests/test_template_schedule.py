from datetime import UTC, datetime, timedelta

from fsrs import Rating
from helpers import make_problem

from climb.knowledge.schedule import Review
from climb.schema import (
    Attempt,
    CaseOutcome,
    CaseResult,
    Hint,
    ProblemStatus,
    RecallAttempt,
    RetirementReason,
)
from climb.template_schedule import check, due, recall_probability, reviews

T0 = datetime(2026, 1, 5, 9, tzinfo=UTC)
DAY = timedelta(days=1)


def recall(at: datetime, *, passed: bool = True, hints: tuple[Hint, ...] = ()) -> RecallAttempt:
    outcome = CaseOutcome.PASSED if passed else CaseOutcome.WRONG
    return RecallAttempt(
        id=f"r-{at.isoformat()}",
        created_at=at,
        user_id="u-4f9c2a",
        card_id="c1",
        template_id="t1",
        code="def solve(): ...",
        hints=list(hints),
        cap_ms=1000,
        runner="local",
        results=[CaseResult(case_id="k1", outcome=outcome, elapsed_ms=1)],
    )


def submitted(sitting: str, at: datetime, *, solved: bool, problem: str = "p1") -> Attempt:
    return Attempt(
        id=f"a-{sitting}-{at.isoformat()}",
        user_id="u-4f9c2a",
        problem_id=problem,
        sitting_id=sitting,
        finished_at=at,
        solved=solved,
    )


TARGETED = make_problem("p1", target_technique=None, target_template_id="t1")
PROBLEMS = {
    "p1": TARGETED,
    "p2": make_problem("p2"),
    "p3": make_problem(
        "p3",
        target_technique=None,
        target_template_id="t1",
        status=ProblemStatus.RETIRED,
        retired_reason=RetirementReason.DEFECTIVE,
    ),
}


def ratings(found: list[Review]) -> list[Rating]:
    return [r.rating for r in found]


def test_a_recall_rates_by_the_hints_taken():
    """Cold is Good, after the notes Hard, after the form or failed Again."""
    recalls = [
        recall(T0),
        recall(T0 + DAY, hints=(Hint.NOTES,)),
        recall(T0 + 2 * DAY, hints=(Hint.NOTES, Hint.FORM)),
        recall(T0 + 3 * DAY, passed=False),
    ]
    found = reviews(recalls, [], PROBLEMS)["t1"]
    assert ratings(found) == [Rating.Good, Rating.Hard, Rating.Again, Rating.Again]


def test_a_sitting_is_one_review_at_its_first_submission():
    """A solve after a failed submission rates Hard, timed at the failure."""
    attempts = [
        submitted("s1", T0 + timedelta(minutes=9), solved=True),
        submitted("s1", T0, solved=False),
    ]
    assert reviews([], attempts, PROBLEMS)["t1"] == [Review(T0, Rating.Hard)]


def test_a_sitting_rates_good_on_a_first_solve_and_again_unsolved():
    """A first-submission solve rates Good, and no solve at all Again."""
    attempts = [submitted("s1", T0, solved=True), submitted("s2", T0 + DAY, solved=False)]
    assert ratings(reviews([], attempts, PROBLEMS)["t1"]) == [Rating.Good, Rating.Again]


def test_only_a_sitting_on_a_live_problem_targeting_the_template_reviews_it():
    """A technique's, a defective and a sitting-less attempt add nothing."""
    attempts = [
        submitted("s1", T0, solved=True, problem="p2"),
        submitted("s2", T0, solved=True, problem="p3"),
        Attempt(id="a-x", user_id="u-4f9c2a", problem_id="p1", finished_at=T0, solved=True),
    ]
    assert reviews([], attempts, PROBLEMS) == {}


def test_the_check_opens_on_day_3_and_is_owed_on_day_5():
    """After one Good review, the band lands on the measured window."""
    window = check([Review(T0, Rating.Good)])
    assert window is not None
    assert (window.opens - T0, window.owed - T0) == (3 * DAY, 5 * DAY)


def test_the_check_never_opens_inside_the_floor():
    """A Hard review crosses the band on day 2, and the floor holds day 3."""
    window = check([Review(T0, Rating.Hard)])
    assert window is not None
    assert window.opens - T0 == 3 * DAY


def test_a_template_with_no_review_has_no_reading():
    """No review gives no recall probability, due time or check."""
    assert recall_probability([], T0) is None
    assert due([]) is None
    assert check([]) is None


def test_recall_probability_falls_with_time():
    """The probability read at the check is below the one read the day after."""
    found = [Review(T0, Rating.Good)]
    assert recall_probability(found, T0 + DAY) > recall_probability(found, T0 + 3 * DAY)
