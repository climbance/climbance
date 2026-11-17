import math
import random
from datetime import timedelta

import pytest
from helpers import PROVENANCE_FIELDS, T0, make_problem

from climb.difficulty import Anchor, calibrate
from climb.difficulty.fit import Link, Outcome, chance, fit, link, log_loss
from climb.problems import ProblemStore
from climb.ratings import FitLog, RatingLog
from climb.schema import CaseOutcome, Trial

ABILITY = {"weak": -1.5, "mid": 0.0, "strong": 1.5}


def simulated(difficulty: dict[str, float], tries: int = 40, seed: int = 7) -> list[Outcome]:
    rng = random.Random(seed)
    return [
        Outcome(member, problem, rng.random() < chance(theta, b))
        for member, theta in ABILITY.items()
        for problem, b in difficulty.items()
        for _ in range(tries)
    ]


def test_the_fit_orders_problems_and_members_as_they_were_drawn():
    drawn = {"a": -2.0, "b": -0.5, "c": 1.0, "d": 2.5}

    fitted = fit(simulated(drawn))

    assert sorted(fitted.difficulty, key=fitted.difficulty.__getitem__) == ["a", "b", "c", "d"]
    assert sorted(fitted.ability, key=fitted.ability.__getitem__) == ["weak", "mid", "strong"]


def test_a_problem_every_member_solved_stays_finite_and_uncertain():
    """The prior keeps it finite; its deviation is wider than a mixed one's."""
    outcomes = [Outcome(m, "easy", True) for m in ABILITY for _ in range(3)]
    outcomes += [Outcome(m, "mixed", m == "strong") for m in ABILITY for _ in range(3)]

    fitted = fit(outcomes)

    assert math.isfinite(fitted.difficulty["easy"])
    assert fitted.difficulty["easy"] < fitted.difficulty["mixed"]
    assert fitted.deviation["easy"] > fitted.deviation["mixed"]


def test_the_link_is_the_least_squares_line():
    line = link([(0.0, 1000.0), (1.0, 1200.0), (2.0, 1400.0)])

    assert (line.slope, line.intercept) == pytest.approx((200.0, 1000.0))
    assert line.difficulty(line.score(0.7)) == pytest.approx(0.7)


def test_a_link_needs_two_anchors_apart():
    with pytest.raises(ValueError, match="two anchors"):
        link([(1.0, 1000.0)])
    with pytest.raises(ValueError, match="one difficulty"):
        link([(1.0, 1000.0), (1.0, 1400.0)])


def test_log_loss_charges_a_confident_miss_most():
    assert log_loss([(0.9, True)]) < log_loss([(0.5, True)]) < log_loss([(0.1, True)])


def a_trial(problem: str, member: str, solved: bool, n: int) -> Trial:
    model, effort = member.split("/")
    return Trial(
        id=f"t-{problem}-{member}-{n}",
        created_at=T0 + timedelta(seconds=n),
        problem_id=problem,
        try_number=1,
        outcome=CaseOutcome.PASSED if solved else CaseOutcome.WRONG,
        cases_passed=3 if solved else 0,
        cases_run=3 if solved else 1,
        cap_ms=2000,
        runner="subprocess",
        **(PROVENANCE_FIELDS | {"model": model, "effort": effort}),
    )


def trials_for(difficulty: dict[str, float], seed: int = 3) -> list[Trial]:
    members = {"m/weak": -1.5, "m/mid": 0.0, "m/strong": 1.5}
    rng = random.Random(seed)
    return [
        a_trial(problem, member, rng.random() < chance(theta, b), n)
        for member, theta in members.items()
        for problem, b in difficulty.items()
        for n in range(20)
    ]


TRUE = Link(slope=300.0, intercept=1400.0)
ANCHORS = {f"x{n}": TRUE.score(b) for n, b in enumerate([-2.0, -1.0, 0.0, 1.0, 2.0, -0.5, 0.5])}
HELD = {"x5", "x6"}


def calibrated():
    anchors = {p: Anchor(rating=r, held_out=p in HELD) for p, r in ANCHORS.items()}
    anchored = trials_for({p: TRUE.difficulty(r) for p, r in ANCHORS.items()})
    corpus = trials_for({"p1": -1.0, "p2": 1.0}, seed=5)
    return calibrate(corpus, anchored, anchors, anchor_set="abc123")


def test_a_fit_scores_the_corpus_on_the_contest_scale():
    fit_, ratings = calibrated()
    scores = {one.problem_id: one.score for one in ratings}

    assert set(scores) == {"p1", "p2"}
    assert scores["p1"] < 1400 < scores["p2"]
    assert all(one.fit_id == fit_.id and one.deviation for one in ratings)


def test_a_fit_beats_a_constant_on_the_held_out_anchors_it_never_read():
    """The held-out anchors are 2 of 7, and the line is set on the other 5."""
    fit_, _ = calibrated()

    assert (fit_.anchors_fitted, fit_.anchors_held_out) == (5, 2)
    assert fit_.held_out_log_loss < fit_.baseline_log_loss


def test_a_fit_stores_with_its_ratings(database):
    for problem in ("p1", "p2"):
        ProblemStore(database).put(make_problem(problem))
    fit_, ratings = calibrated()

    FitLog(database).append(fit_, ratings)

    assert FitLog(database).fits() == [fit_]
    assert {one.problem_id for one in RatingLog(database).ratings()} == {"p1", "p2"}
