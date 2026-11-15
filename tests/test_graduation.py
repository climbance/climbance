from datetime import UTC, datetime, timedelta

from helpers import make_problem

from climb.graduation import NextKind, reading
from climb.ladder import CardState, Rung
from climb.schema import (
    Attempt,
    Card,
    CardRun,
    CaseOutcome,
    CaseResult,
    Probe,
    RecallAttempt,
    Selector,
    Template,
    TemplateCase,
)

T0 = datetime(2026, 1, 5, 9, tzinfo=UTC)
DAY = timedelta(days=1)
SOLVED = T0 + timedelta(hours=1)

CARD = Card(
    id="c1",
    slug="binary-search",
    technique="binary-search",
    module="algo",
    title="Binary search",
    trigger="a sorted range",
    brief="## Core idea\n\nHalve it.",
    templates=[
        Template(
            id="t1",
            slug="lower-bound",
            title="Lower bound",
            trigger="first index not below",
            code="def solve(): ...",
            cases=[TemplateCase(args=[], expected=0)],
        ),
        Template(id="t2", slug="read-only", title="Read", trigger="read", code="..."),
    ],
    selector=Selector(technique="binary-search", size=5),
)
RUNG = make_problem("p1", target_technique=None, target_template_id="t1")
PROBLEMS = {"p1": RUNG, "p9": make_problem("p9")}
RUNGS = [Rung(problem=RUNG, templates=["t1"], required=True, solved=True)]
RUN = CardRun(
    id="r1",
    user_id="u-4f9c2a",
    card_id="c1",
    started_at=T0,
    probes=[Probe(problem_id="p9", assigned_at=T0)],
)


def solve(problem: str, at: datetime, *, solved: bool = True) -> Attempt:
    return Attempt(
        id=f"a-{problem}-{at.isoformat()}",
        user_id="u-4f9c2a",
        problem_id=problem,
        sitting_id=f"s-{problem}-{at.isoformat()}",
        finished_at=at,
        solved=solved,
    )


def recall(at: datetime, *, passed: bool = True) -> RecallAttempt:
    outcome = CaseOutcome.PASSED if passed else CaseOutcome.WRONG
    return RecallAttempt(
        id=f"r-{at.isoformat()}",
        created_at=at,
        user_id="u-4f9c2a",
        card_id="c1",
        template_id="t1",
        code="def solve(): ...",
        cap_ms=1000,
        runner="local",
        results=[CaseResult(case_id="k1", outcome=outcome, elapsed_ms=1)],
    )


LADDER = [solve("p1", SOLVED)]
PROBED = [*LADDER, solve("p9", SOLVED + DAY)]
CHECKED = recall(SOLVED + 3 * DAY)


def test_a_solved_ladder_waits_for_the_spaced_check():
    """The check is read from the rung's solve: open day 3, owed day 5."""
    state, upcoming = reading(CARD, RUN, RUNGS, LADDER, PROBLEMS, [])
    assert state is CardState.CONSOLIDATING
    assert upcoming is not None and upcoming.kind is NextKind.CHECK
    assert (upcoming.opens - SOLVED, upcoming.owed) == (3 * DAY, SOLVED + 5 * DAY)


def test_the_check_and_a_probe_graduate_the_card():
    """A Good recall inside the check and a solved probe graduate it."""
    state, upcoming = reading(CARD, RUN, RUNGS, PROBED, PROBLEMS, [CHECKED])
    assert state is CardState.GRADUATED
    assert upcoming is not None and upcoming.kind is NextKind.RECALL
    assert upcoming.opens > CHECKED.created_at


def test_a_recall_before_the_check_opens_graduates_nothing():
    """A warm recall is a review: the card waits, and the check moves later."""
    warm = recall(SOLVED + DAY)
    state, upcoming = reading(CARD, RUN, RUNGS, PROBED, PROBLEMS, [warm])
    assert state is CardState.CONSOLIDATING
    assert upcoming is not None and upcoming.opens > warm.created_at + 3 * DAY


def test_no_probe_solved_holds_the_card_consolidating():
    """A passed check alone graduates nothing, and no check is left."""
    assert reading(CARD, RUN, RUNGS, LADDER, PROBLEMS, [CHECKED]) == (
        CardState.CONSOLIDATING,
        None,
    )


def test_a_failed_review_after_graduation_lapses_the_card():
    """The failed recall reopens a check, read from the failure."""
    failed = recall(SOLVED + 10 * DAY, passed=False)
    state, upcoming = reading(CARD, RUN, RUNGS, PROBED, PROBLEMS, [CHECKED, failed])
    assert state is CardState.LAPSED
    assert upcoming is not None and upcoming.kind is NextKind.CHECK
    assert upcoming.opens >= failed.created_at + 3 * DAY


def test_a_lapsed_card_graduates_again_on_a_spaced_recall():
    """No ladder and no probe again: a Good recall once the check opened."""
    failed = recall(SOLVED + 10 * DAY, passed=False)
    again = recall(SOLVED + 20 * DAY)
    state, _ = reading(CARD, RUN, RUNGS, PROBED, PROBLEMS, [CHECKED, failed, again])
    assert state is CardState.GRADUATED


def test_an_unstarted_or_acquiring_card_waits_for_nothing():
    """Before the ladder is solved, no check is read."""
    unsolved = [Rung(problem=RUNG, templates=["t1"], required=True)]
    assert reading(CARD, None, RUNGS, [], PROBLEMS, []) == (CardState.NOT_STARTED, None)
    assert reading(CARD, RUN, unsolved, [], PROBLEMS, []) == (CardState.ACQUIRING, None)
