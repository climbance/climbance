from datetime import UTC, datetime

import pytest
from helpers import PROVENANCE
from matching import card, seeded
from sqlalchemy import func, select

from climb.calls import CallLog
from climb.cli.copy_corpus import copied
from climb.generation import Corpus, land
from climb.mint import site_outcome
from climb.outcomes import OutcomeLog
from climb.problems.table import problems
from climb.schema import (
    Call,
    CallSite,
    Draft,
    ExpectedSource,
    MachineProvenance,
    RetirementReason,
    SettledCase,
    WritingState,
)
from climb.solutions.table import solutions

CALL = Call(
    id="copy-call-1",
    created_at=datetime(2026, 1, 1, tzinfo=UTC),
    model="a-model",
    effort="high",
    prompt="a prompt",
    prompt_hash="0123456789ab",
    response="{}",
    pin="a-provider/bf16",
    provider="a-provider",
)


def drafted(writing: str) -> Draft:
    provenance = MachineProvenance.of(CALL)
    return Draft(
        id=writing,
        state=WritingState.HARDENED,
        title=f"Widest fair stretch {writing}",
        statement="Given a list of readings, return ...",
        canonical="def solve(xs):\n    return len(xs)\n",
        declared=[{"args": [[1, 2, 3]], "expected": 3}],
        difficulty="medium",
        reference="def solve(xs):\n    return sum(1 for _ in xs)\n",
        generator_provenance=provenance,
        blind_provenance=provenance,
        cases=[
            SettledCase(
                args=[[1, 2, 3]],
                expected=3,
                expected_from=ExpectedSource.REFERENCE,
                provenance=provenance,
            )
        ],
    )


@pytest.fixture
def local(database):
    CallLog(database).append(CALL)
    (seeded_card,) = seeded(database, card())
    return seeded_card.templates[0]


def landed(root, template, writing: str = "w1"):
    one = land(Corpus.at(root), template, drafted(writing))
    OutcomeLog(root).append(
        site_outcome(
            CallSite.GENERATOR, writing, target_template_id=template.id, provenance=PROVENANCE
        )
    )
    OutcomeLog(root).append(
        site_outcome(
            CallSite.BLIND,
            writing,
            target_template_id=template.id,
            problem_id=one.id,
            provenance=PROVENANCE,
        )
    )
    return one


def count(root, table) -> int:
    with root.connect() as conn:
        return conn.execute(select(func.count()).select_from(table)).scalar_one()


def test_a_problem_lands_with_its_records_under_the_targets_template(
    database, other_database, local
):
    """Each store's seed mints its own template ids, so a copied id would name
    no template there."""
    (theirs,) = seeded(other_database, card())
    problem = landed(database, local)

    copied(database, other_database, write=True)

    there = Corpus.at(other_database)
    assert [one.id for one in there.problems.all()] == [problem.id]
    assert there.problems.all()[0].target_template_id == theirs.templates[0].id
    assert len(there.cases.for_problem(problem.id)) == 1
    assert len(there.solutions.for_problem(problem.id)) == 2
    assert [one.template_id for one in there.matches.matches()] == [theirs.templates[0].id]
    assert [one.site for one in OutcomeLog(other_database).outcomes()] == [
        CallSite.GENERATOR,
        CallSite.BLIND,
    ]


def test_a_second_copy_writes_nothing(database, other_database, local):
    """A copy runs after every sweep, so copied rows are skipped."""
    seeded(other_database, card())
    landed(database, local)
    copied(database, other_database, write=True)

    again = copied(database, other_database, write=True)

    assert all(rows == [] for rows in again.rows.values())


def test_a_problem_the_target_holds_brings_none_of_its_records(database, other_database, local):
    """The deployed store writes claims and ratings of its own, under its own
    ids, so a record of a held problem could stand twice."""
    seeded(other_database, card())
    landed(database, local)
    copied(database, other_database, write=True)
    before = count(other_database, solutions)
    landed(database, local, "w2")

    plan = copied(database, other_database, write=True)

    assert len(plan.rows["problems"]) == 1
    assert len(plan.rows["solutions"]) == 2
    assert count(other_database, solutions) == before + 2


def test_a_target_without_the_card_is_refused_whole(database, other_database, local):
    """A problem whose template the target lacks would name none."""
    landed(database, local)

    plan = copied(database, other_database, write=True)

    assert plan.unseeded == [f"sliding-window/{local.slug}"]
    assert count(other_database, problems) == 0


def test_a_moved_status_is_reported_and_left(database, other_database, local):
    """A retirement is the author's act in one store; the copy only adds."""
    seeded(other_database, card())
    problem = landed(database, local)
    copied(database, other_database, write=True)
    Corpus.at(database).problems.retire(problem.id, RetirementReason.DEFECTIVE)

    plan = copied(database, other_database, write=True)

    assert plan.moved == [(problem.id, "retired", "created")]
    assert Corpus.at(other_database).problems.all()[0].status == "created"


def test_a_dry_run_writes_nothing(database, other_database, local):
    """The first run against prod is read before it writes."""
    seeded(other_database, card())
    landed(database, local)

    plan = copied(database, other_database, write=False)

    assert len(plan.rows["problems"]) == 1
    assert count(other_database, problems) == 0
