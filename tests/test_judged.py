from datetime import UTC, datetime

from climb.board.judged import JudgementRates, judgement_rates
from climb.schema import Card, CaseOutcome, Judgement, JudgementItem, Selector, Template

T0 = datetime(2026, 9, 1, 10, tzinfo=UTC)
CARD = Card(
    id="c1",
    slug="knapsack",
    technique="knapsack",
    module="algo",
    title="Knapsack",
    trigger="capacity",
    brief="## Core idea",
    templates=[Template(id="t1", slug="zero-one", title="0/1", trigger="once", code="pass")],
    selector=Selector(technique="knapsack", size=3),
)


def item(id: str, *, clean: bool) -> JudgementItem:
    flaw = (
        {}
        if clean
        else {
            "line": 2,
            "change": "<= for <",
            "case_args": [[1], 1],
            "case_expected": 1,
            "outcome": CaseOutcome.WRONG,
            "returned": 0,
        }
    )
    return JudgementItem(
        id=id,
        created_at=T0,
        template_id="t1",
        form_digest="d",
        code="pass\npass",
        clean=clean,
        **flaw,
    )


def answered(item_id: str, *, called_clean: bool) -> Judgement:
    return Judgement(
        id=f"j-{item_id}-{called_clean}",
        created_at=T0,
        user_id="u-4f9c2a",
        item_id=item_id,
        called_clean=called_clean,
        line=None if called_clean else 2,
    )


ITEMS = [item("flawed", clean=False), item("clean", clean=True)]


def test_both_rates_are_counted_apart():
    """Calling everything flawed finds every flaw; the second rate shows it."""
    answers = [answered("flawed", called_clean=False), answered("clean", called_clean=False)]
    rates = judgement_rates(answers, ITEMS, [CARD])["knapsack"]
    assert rates == JudgementRates(flaws_found=1, flawed=1, false_alarms=1, clean=1)


def test_an_answer_counts_toward_the_technique_s_parents():
    """Knapsack is a kind of dynamic programming, as a claim counts."""
    rates = judgement_rates([answered("clean", called_clean=True)], ITEMS, [CARD])
    assert rates["dynamic-programming"] == JudgementRates(clean=1)


def test_an_item_no_card_holds_counts_nowhere():
    """A template a re-seed dropped names no technique."""
    stray = JudgementItem(
        id="x", created_at=T0, template_id="gone", form_digest="d", code="p", clean=True
    )
    assert judgement_rates([answered("x", called_clean=True)], [stray], [CARD]) == {}
