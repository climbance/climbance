from datetime import UTC, datetime, timedelta

import pytest
from helpers import PROVENANCE
from matching import canonical, card, problem, seeded, template

from climb.api.generation_figures import Stop, generation_figures
from climb.mint import draft, generator_match, site_outcome
from climb.schema import (
    CallSite,
    DraftCase,
    Gate,
    ProblemDifficulty,
    ProblemStatus,
    RetirementReason,
    WritingState,
)

NOW = datetime(2026, 11, 23, tzinfo=UTC)


def left(site, writing_id, *, days_ago=1, cost=0.1, **overrides):
    one = site_outcome(
        site, writing_id, provenance=PROVENANCE, target_technique="greedy", **overrides
    )
    return one.model_copy(update={"created_at": NOW - timedelta(days=days_ago), "cost": cost})


def drafted(writing_id, state, gate=None):
    one = draft(
        writing_id,
        title="t",
        statement="s",
        canonical="def solve(): pass",
        declared=[DraftCase(args=[1], expected=1)],
        difficulty=ProblemDifficulty.EASY,
        target_technique="greedy",
        provenance=PROVENANCE,
    )
    return one.model_copy(update={"state": state, "gate": gate})


def figures(outcomes=(), drafts=(), problems=(), solutions=(), matches=(), cards=()):
    return generation_figures(
        list(outcomes), list(drafts), list(problems), solutions, matches, cards, now=NOW
    )


def test_a_writing_lands_when_any_of_its_outcomes_names_a_problem():
    """A resume's records name the problem, and the first run's do not."""
    read = figures(
        [
            left(CallSite.GENERATOR, "w1", days_ago=3),
            left(CallSite.NAIVE, "w1", problem_id="p1"),
            left(CallSite.GENERATOR, "w2", gate=Gate.NO_VALUE),
        ]
    )

    assert (read.writings, read.landed) == (2, 1)


def test_a_replay_is_no_writing():
    """A replay runs the answering sites alone, over a landed problem."""
    read = figures([left(CallSite.BLIND, "r1", problem_id="p1")])

    assert (read.writings, read.landed, read.spend) == (0, 0, None)


def test_the_period_reads_a_writing_by_its_first_outcome():
    read = figures(
        [
            left(CallSite.GENERATOR, "w1", days_ago=31),
            left(CallSite.BLIND, "w1", days_ago=2, problem_id="p1"),
        ]
    )

    assert read.writings == 0


def test_a_rejected_writing_is_paid_for_by_the_landed_ones():
    """A cost over landed writings alone would understate a problem's."""
    read = figures(
        [
            left(CallSite.GENERATOR, "w1", cost=0.2, problem_id="p1"),
            left(CallSite.GENERATOR, "w2", cost=0.4, gate=Gate.NO_VALUE),
            left(CallSite.SCREEN, "w2", cost=None),
        ]
    )

    assert read.spend_per_landed == pytest.approx(0.6)
    assert read.uncosted == 1


def test_no_landed_writing_has_no_spend_per_problem():
    read = figures([left(CallSite.GENERATOR, "w1", gate=Gate.COPIED)])

    assert read.spend_per_landed is None
    assert read.spend == 0.1


def test_each_writing_left_unlanded_is_counted_where_it_stopped():
    """A site's gate, a gate the draft alone holds, or a held state."""
    read = figures(
        [
            left(CallSite.GENERATOR, "w1"),
            left(CallSite.SCREEN, "w1", gate=Gate.COPIED),
            left(CallSite.GENERATOR, "w2"),
            left(CallSite.SCREEN, "w2", gate=Gate.COPIED),
            left(CallSite.GENERATOR, "w3"),
            left(CallSite.GENERATOR, "w4"),
        ],
        drafts=[
            drafted("w1", WritingState.REJECTED, Gate.COPIED),
            drafted("w3", WritingState.REJECTED, Gate.UNEXERCISED),
            drafted("w4", WritingState.PACED),
        ],
    )

    assert read.stops == [
        Stop(site=CallSite.SCREEN, gate=Gate.COPIED, held_at=None, writings=2),
        Stop(site=None, gate=Gate.UNEXERCISED, held_at=None, writings=1),
        Stop(site=None, gate=None, held_at=WritingState.PACED, writings=1),
    ]


def test_a_held_state_names_its_oldest_draft_and_a_rejection_none():
    read = figures(
        [
            left(CallSite.GENERATOR, "w1", days_ago=9),
            left(CallSite.GENERATOR, "w2", days_ago=3),
            left(CallSite.GENERATOR, "w3", days_ago=5, gate=Gate.NO_VALUE),
        ],
        drafts=[
            drafted("w1", WritingState.PACED),
            drafted("w2", WritingState.PACED),
            drafted("w3", WritingState.REJECTED, Gate.NO_VALUE),
        ],
    )

    assert [(one.state, one.drafts, one.oldest_days) for one in read.drafts] == [
        (WritingState.PACED, 2, 9),
        (WritingState.REJECTED, 1, None),
    ]


def test_the_corpus_counts_each_template_by_band_and_retired_apart(database):
    """A retired problem is no longer served, so it sits outside the bands."""
    cards = seeded(
        database, card(templates=[template("fixed-window"), template("longest-valid-window")])
    )
    fixed = cards[0].templates[0].id

    def written(id, **update):
        one = problem(id, techniques=["sliding-window"])
        return one.model_copy(
            update={"target_template_id": fixed, "target_technique": None} | update
        )

    problems = [
        written("p1", difficulty=ProblemDifficulty.EASY),
        written("p2", difficulty=ProblemDifficulty.HARD),
        written("p3", difficulty=None),
        written(
            "p4",
            difficulty=ProblemDifficulty.EASY,
            status=ProblemStatus.RETIRED,
            retired_reason=RetirementReason.DEFECTIVE,
        ),
        problem("p5", techniques=["greedy"]),
    ]
    solution = canonical("p1")

    read = figures(
        problems=problems,
        solutions=[solution],
        matches=[generator_match(fixed, solution.id)],
        cards=cards,
    )

    rows = {one.template_slug: one for one in read.corpus}
    assert rows["fixed-window"].counts == {
        ProblemDifficulty.EASY: 1,
        ProblemDifficulty.MEDIUM: 0,
        ProblemDifficulty.HARD: 1,
    }
    assert (rows["fixed-window"].unlabelled, rows["fixed-window"].retired) == (1, 1)
    assert not rows["fixed-window"].gap
    assert rows["longest-valid-window"].gap
    assert read.untemplated == 1
