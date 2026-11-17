"""A fit and its ratings from the trials: `corpus.md`, Difficulty fits."""

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from climb.difficulty.fit import Outcome, chance, fit, link, log_loss
from climb.ids import new_id
from climb.schema import DifficultyFit, DifficultyRating, FitMember, RatingSource, Trial

type MemberKey = tuple[str, str, str]  # model, effort, pin
type ItemKey = tuple[bool, str]  # whether an anchor, and its id


@dataclass(frozen=True)
class Anchor:
    rating: float
    held_out: bool


def member_of(one: Trial) -> MemberKey:
    return (one.model or "", one.effort or "", one.pin or "")


def outcome(one: Trial, *, anchor: bool) -> Outcome[MemberKey, ItemKey]:
    return Outcome(member_of(one), (anchor, one.problem_id), one.solved)


def calibrate(
    corpus: Sequence[Trial],
    anchored: Sequence[Trial],
    anchors: dict[str, Anchor],
    *,
    anchor_set: str,
    order: Sequence[MemberKey] = (),
) -> tuple[DifficultyFit, list[DifficultyRating]]:
    """One fit over the corpus's trials and the fit anchors', linked on the
    fit anchors and scored on the held-out ones, which it never read."""
    held = [one for one in anchored if anchors[one.problem_id].held_out]
    outcomes = [outcome(one, anchor=False) for one in corpus]
    outcomes += [
        outcome(one, anchor=True) for one in anchored if not anchors[one.problem_id].held_out
    ]
    fitted = fit(outcomes)
    fitted_anchors = sorted(p for anchor, p in fitted.difficulty if anchor)
    line = link([(fitted.difficulty[True, p], anchors[p].rating) for p in fitted_anchors])
    if line.slope <= 0:
        raise ValueError("harder anchors fitted easier: no link to the contest scale")
    if not held:
        raise ValueError("no held-out anchor was tried, so the fit is scored on nothing")
    unknown = {member_of(one) for one in held} - set(fitted.ability)
    if unknown:
        raise ValueError(f"a held-out trial's member is in no fitted trial: {sorted(unknown)}")

    tried: dict[MemberKey, list[bool]] = defaultdict(list)
    for one in outcomes:
        tried[one.member].append(one.solved)
    predicted = [
        (
            chance(fitted.ability[member_of(one)], line.difficulty(anchors[one.problem_id].rating)),
            one.solved,
        )
        for one in held
    ]
    baseline = [
        (sum(tried[member_of(one)]) / len(tried[member_of(one)]), one.solved) for one in held
    ]

    ranked = {key: n for n, key in enumerate(order)}
    members = sorted(fitted.ability, key=lambda key: (ranked.get(key, len(ranked)), key))
    now = datetime.now(UTC)
    the_fit = DifficultyFit(
        id=new_id(),
        created_at=now,
        anchor_set=anchor_set,
        slope=line.slope,
        intercept=line.intercept,
        anchors_fitted=len(fitted_anchors),
        anchors_held_out=len({one.problem_id for one in held}),
        problems=sum(not anchor for anchor, _ in fitted.difficulty),
        held_out_log_loss=log_loss(predicted),
        baseline_log_loss=log_loss(baseline),
        members=[
            FitMember(
                model=m,
                effort=e,
                pin=p,
                ability=fitted.ability[m, e, p],
                trials=len(tried[m, e, p]),
            )
            for m, e, p in members
        ],
    )
    ratings = [
        DifficultyRating(
            id=new_id(),
            created_at=now,
            problem_id=problem,
            score=line.score(difficulty),
            deviation=line.slope * fitted.deviation[anchor, problem],
            source=RatingSource.FIT,
            fit_id=the_fit.id,
        )
        for (anchor, problem), difficulty in sorted(fitted.difficulty.items())
        if not anchor
    ]
    return the_fit, ratings
