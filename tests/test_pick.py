from datetime import UTC, datetime, timedelta

from fsrs import Rating
from helpers import make_problem

from climb.graduation import Next, NextKind
from climb.knowledge.schedule import Review
from climb.ladder import CardState, Rung
from climb.pick import Act, CardReading, Rank, offers, pick
from climb.schema import Attempt, Card, CardRun, Cause, FailureMode, Probe, Selector, Template

NOW = datetime(2026, 3, 1, 9, tzinfo=UTC)
DAY = timedelta(days=1)


def card(slug: str) -> Card:
    return Card(
        id=f"c-{slug}",
        slug=slug,
        technique="binary-search",
        module="algo",
        title=slug,
        trigger="a sorted range",
        brief="## Core idea\n\nHalve it.",
        templates=[Template(id=f"t-{slug}", slug="form", title="Form", trigger="t", code="...")],
        selector=Selector(technique="binary-search", size=5),
    )


def reading(slug: str, state: CardState, **fields) -> CardReading:
    return CardReading(
        card=card(slug),
        depth=fields.pop("depth", 0),
        locked=fields.pop("locked", False),
        run=fields.pop("run", None),
        rungs=fields.pop("rungs", []),
        state=state,
        next=fields.pop("next", None),
        execution=fields.pop("execution", None),
    )


def check(slug: str, opens: datetime, owed: datetime) -> Next:
    return Next(kind=NextKind.CHECK, template_id=f"t-{slug}", opens=opens, owed=owed)


def due(slug: str, at: datetime) -> Next:
    return Next(kind=NextKind.RECALL, template_id=f"t-{slug}", opens=at)


RUNG = make_problem("rung-1")
WRITTEN = make_problem("written-1", target_technique=None, target_template_id="t-kept")

OWED = reading("owed", CardState.CONSOLIDATING, next=check("owed", NOW - 6 * DAY, NOW - DAY))
OPEN = reading("open", CardState.LAPSED, next=check("open", NOW - DAY, NOW + DAY))
KEPT = reading("kept", CardState.GRADUATED, next=due("kept", NOW - DAY))
LEARNING = reading(
    "learning",
    CardState.ACQUIRING,
    rungs=[Rung(problem=RUNG, templates=[], required=True)],
)
FRESH = reading("fresh", CardState.NOT_STARTED)
PROBLEMS = [RUNG, WRITTEN]


def offered(readings, *, attempts=(), labels=None, reviews=None) -> list:
    return offers(readings, reviews or {}, PROBLEMS, list(attempts), labels or {}, NOW)


def test_each_rank_is_served_before_the_next():
    """Owed check, open check, due review, rung; no new card while owed."""
    found = offered([FRESH, LEARNING, KEPT, OPEN, OWED])
    assert [(one.rank, one.card_slug) for one in found] == [
        (Rank.OWED_CHECK, "owed"),
        (Rank.OPEN_CHECK, "open"),
        (Rank.DUE_REVIEW, "kept"),
        (Rank.RUNG, "learning"),
    ]


def test_a_check_is_served_as_a_recall():
    """Graduation reads a recall, so a check is never a sitting."""
    first = pick([OPEN], {}, PROBLEMS, [], {}, NOW)
    assert first is not None and (first.act, first.template_id) == (Act.RECALL, "t-open")


def test_a_due_review_is_a_sitting_on_an_unsolved_problem_written_for_it():
    """A problem the user has not seen comes before a recall."""
    first = pick([KEPT], {}, PROBLEMS, [], {}, NOW)
    assert first is not None and (first.act, first.problem_id) == (Act.SITTING, "written-1")


def test_a_due_review_with_no_unsolved_problem_is_a_recall():
    """A template whose problems are all solved falls back to its recall."""
    solved = Attempt(
        id="a1", user_id="u-4f9c2a", problem_id="written-1", finished_at=NOW - DAY, solved=True
    )
    first = pick([KEPT], {}, PROBLEMS, [solved], {}, NOW)
    assert first is not None and (first.act, first.problem_id) == (Act.RECALL, None)


def failed_sitting() -> tuple[Attempt, dict[str, list[Review]]]:
    attempt = Attempt(
        id="a1",
        user_id="u-4f9c2a",
        problem_id="written-1",
        sitting_id="s1",
        finished_at=NOW - DAY,
        solved=False,
    )
    return attempt, {
        "t-kept": [Review(NOW - 30 * DAY, Rating.Good), Review(attempt.finished_at, Rating.Again)]
    }


def test_a_failed_sitting_aims_a_recall_at_the_form_it_missed():
    """The next act on that template is its recall, before another problem."""
    attempt, found = failed_sitting()
    first = pick([KEPT], found, PROBLEMS, [attempt], {}, NOW)
    assert first is not None and first.act is Act.RECALL


def test_a_failure_labelled_syntax_aims_nothing():
    """The solver held the form, so the review stays a sitting."""
    attempt, found = failed_sitting()
    labels = {attempt.id: FailureMode.SYNTAX}
    first = pick([KEPT], found, PROBLEMS, [attempt], labels, NOW)
    assert first is not None and first.act is Act.SITTING


def test_a_form_and_a_slip_diagnosis_of_one_failure_pick_apart():
    """A measured `slip` keeps the review a sitting; `form` aims the recall."""
    attempt, found = failed_sitting()
    acts = [
        pick([KEPT], found, PROBLEMS, [attempt], {}, NOW, {attempt.id: cause})
        for cause in (Cause.FORM, Cause.SLIP)
    ]
    assert [one.act if one else None for one in acts] == [Act.RECALL, Act.SITTING]


def test_a_self_label_stands_over_the_diagnosis():
    """The user's `gap` aims the recall though the machine said `slip`."""
    attempt, found = failed_sitting()
    labels, diagnosed = {attempt.id: FailureMode.GAP}, {attempt.id: Cause.SLIP}
    first = pick([KEPT], found, PROBLEMS, [attempt], labels, NOW, diagnosed)
    assert first is not None and first.act is Act.RECALL


def test_two_cards_in_flight_hold_back_a_new_card():
    """An acquiring card and one with its check open fill the cap."""
    second = reading("second", CardState.CONSOLIDATING, next=check("second", NOW - DAY, NOW + DAY))
    assert Rank.NEW_CARD not in {one.rank for one in offered([LEARNING, second, FRESH])}


def test_a_card_waiting_for_its_check_holds_no_slot():
    """The waiting card is not counted, so a new card is offered."""
    waiting = reading(
        "waiting", CardState.CONSOLIDATING, next=check("waiting", NOW + DAY, NOW + 3 * DAY)
    )
    assert offered([LEARNING, waiting, FRESH])[-1].rank is Rank.NEW_CARD


def test_an_owed_check_freezes_new_cards():
    """Below the cap, a new card still waits while a check is owed."""
    assert Rank.NEW_CARD not in {one.rank for one in offered([OWED, FRESH])}


def test_an_overdue_review_freezes_nothing():
    """A review long past due still lets a new card in."""
    late = reading("late", CardState.GRADUATED, next=due("late", NOW - 40 * DAY))
    assert offered([late, FRESH])[-1].rank is Rank.NEW_CARD


def test_a_locked_card_is_never_offered():
    """Only an unlocked card not started is a new card."""
    assert offered([reading("shut", CardState.NOT_STARTED, locked=True)]) == []


def test_a_new_card_is_the_shallowest():
    """Depth orders the new cards, the roots first."""
    deep = reading("deep", CardState.NOT_STARTED, depth=2)
    root = reading("root", CardState.NOT_STARTED, depth=0)
    assert offered([deep, root])[0].card_slug == "root"


def test_a_consolidating_card_offers_its_probe_until_one_is_solved():
    """Graduation needs a solved probe, ranked with the rungs."""
    probe = make_problem("probe-1")
    run = CardRun(
        id="r1",
        user_id="u-4f9c2a",
        card_id="c-probing",
        started_at=NOW - 9 * DAY,
        probes=[Probe(problem_id="probe-1", assigned_at=NOW - 9 * DAY)],
    )
    probing = reading(
        "probing", CardState.CONSOLIDATING, run=run, next=check("probing", NOW + DAY, NOW + 3 * DAY)
    )
    found = offers([probing], {}, [probe], [], {}, NOW)
    assert [(one.rank, one.problem_id) for one in found] == [(Rank.RUNG, "probe-1")]
    solved = Attempt(
        id="a1", user_id="u-4f9c2a", problem_id="probe-1", finished_at=NOW - DAY, solved=True
    )
    assert offers([probing], {}, [probe], [solved], {}, NOW) == []


def test_a_tie_breaks_on_the_lowest_recall_probability():
    """Of two open checks, the form closer to being lost comes first."""
    fading = reading("fading", CardState.CONSOLIDATING, next=check("fading", NOW - DAY, NOW + DAY))
    fresh = reading(
        "fresh-check", CardState.CONSOLIDATING, next=check("fresh-check", NOW - DAY, NOW + DAY)
    )
    reviews = {
        "t-fading": [Review(NOW - 20 * DAY, Rating.Good)],
        "t-fresh-check": [Review(NOW - 2 * DAY, Rating.Good)],
    }
    assert offered([fresh, fading], reviews=reviews)[0].card_slug == "fading"


def test_a_tie_then_breaks_on_the_lowest_execution_reading():
    """At one depth the less practised technique comes first, unknown first."""
    strong = reading("strong", CardState.NOT_STARTED, execution=0.9)
    weak = reading("weak", CardState.NOT_STARTED, execution=0.2)
    unknown = reading("unknown", CardState.NOT_STARTED)
    assert [one.card_slug for one in offered([strong, weak, unknown])] == [
        "unknown",
        "weak",
        "strong",
    ]
