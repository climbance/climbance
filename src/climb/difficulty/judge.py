"""The difficulty judge and its correction: `cli/difficulty/judge.md`."""

import re
import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from operator import attrgetter

from climb.calls import CallLog, Transport, ask, prompt_hash
from climb.ids import new_id
from climb.schema import (
    Call,
    Configuration,
    DifficultyCorrection,
    DifficultyDraw,
    DifficultyRating,
    MachineProvenance,
    RatingSource,
)

JUDGE = Configuration(model="openai/gpt-oss-120b", effort="medium", pin="coreweave/fp4")
MAX_TOKENS = 40_000
DRAWS = 6
# the probe's `blind` arm, which ranked the anchors best: `judge.md`
SYSTEM = (
    "You estimate the difficulty rating of a competitive programming problem on the contest scale,"
    " where 800 is the easiest and 3500 the hardest, and a rating is the contestant rating at which"
    " a solve is expected half the time. Reply with the rating alone, an integer, on the last line."
)
INSTRUCTIONS_HASH = prompt_hash(SYSTEM, "")
NUMBER = re.compile(r"\d{3,4}")
LOWEST, HIGHEST = 400, 4000  # a number outside is a misread, not a rating


@dataclass(frozen=True)
class Anchor:
    rating: float
    held_out: bool


def judged(text: str | None) -> int | None:
    """The last number on the reply's last line, where it reads as a rating."""
    lines = (text or "").strip().splitlines()
    found = NUMBER.findall(lines[-1]) if lines else []
    rating = int(found[-1]) if found else None
    return rating if rating is not None and LOWEST <= rating <= HIGHEST else None


def draw(
    problem_id: str, statement: str, *, transport: Transport, calls: CallLog
) -> tuple[Call, DifficultyDraw | None]:
    """One judge call, and its draw: none where the reply holds no rating."""
    call, text = ask(
        transport,
        calls,
        system=SYSTEM,
        content=statement,
        configuration=JUDGE,
        max_tokens=MAX_TOKENS,
    )
    rating = judged(text)
    if rating is None:
        return call, None
    return call, DifficultyDraw(
        id=new_id(),
        created_at=datetime.now(UTC),
        problem_id=problem_id,
        judged=rating,
        **MachineProvenance.of(call).model_dump(),
    )


def current(draw: DifficultyDraw, statement: str) -> bool:
    return draw.at_configuration(JUDGE, prompt_hash(SYSTEM, statement))


def matches(correction: DifficultyCorrection) -> bool:
    """Whether the code's judge would send what the correction was fitted to."""
    return (
        correction.model,
        correction.effort,
        correction.pin,
        correction.temperature,
        correction.instructions_hash,
        correction.draws,
    ) == (JUDGE.model, JUDGE.effort, JUDGE.pin, JUDGE.temperature, INSTRUCTIONS_HASH, DRAWS)


def standing_correction(corrections: Sequence[DifficultyCorrection]) -> DifficultyCorrection | None:
    return max(
        (one for one in corrections if matches(one)), key=attrgetter("created_at"), default=None
    )


def medians(draws: Sequence[DifficultyDraw], count: int) -> dict[str, list[DifficultyDraw]]:
    """Each problem's first `count` draws, where it holds that many."""
    by_problem: dict[str, list[DifficultyDraw]] = {}
    for one in draws:
        by_problem.setdefault(one.problem_id, []).append(one)
    return {p: held[:count] for p, held in by_problem.items() if len(held) >= count}


def median(draws: Sequence[DifficultyDraw]) -> float:
    return statistics.median(one.judged for one in draws)


def correct(
    draws: Sequence[DifficultyDraw], anchors: dict[str, Anchor], *, anchor_set: str
) -> DifficultyCorrection:
    """The least-squares line on the fitted anchors' medians, scored on the
    held-out ones, which it never read."""
    read = medians([one for one in draws if one.problem_id in anchors], DRAWS)
    fitted = sorted(p for p in read if not anchors[p].held_out)
    held = sorted(p for p in read if anchors[p].held_out)
    if len(fitted) < 2 or len(held) < 2:
        raise ValueError(
            f"{len(fitted)} fitted and {len(held)} held-out anchor(s) hold {DRAWS} draws:"
            " a line needs two of each"
        )
    xs = [median(read[p]) for p in fitted]
    ys = [anchors[p].rating for p in fitted]
    slope, intercept = statistics.linear_regression(xs, ys)
    if slope <= 0:
        raise ValueError("harder anchors judged easier: no line to the contest scale")
    scored = [intercept + slope * median(read[p]) for p in held]
    truth = [anchors[p].rating for p in held]
    residuals = [t - s for t, s in zip(truth, scored, strict=True)]
    return DifficultyCorrection(
        id=new_id(),
        created_at=datetime.now(UTC),
        anchor_set=anchor_set,
        model=JUDGE.model,
        effort=JUDGE.effort,
        pin=JUDGE.pin,
        temperature=JUDGE.temperature,
        instructions_hash=INSTRUCTIONS_HASH,
        draws=DRAWS,
        intercept=intercept,
        slope=slope,
        anchors_fitted=len(fitted),
        anchors_held_out=len(held),
        held_out_spearman=spearman(scored, truth),
        held_out_mean_error=statistics.fmean(abs(r) for r in residuals),
        deviation=statistics.stdev(residuals),
    )


def rating(
    problem_id: str, draws: Sequence[DifficultyDraw], correction: DifficultyCorrection
) -> DifficultyRating:
    if len(draws) != correction.draws:
        raise ValueError(f"a rating reads {correction.draws} draws, not {len(draws)}")
    return DifficultyRating(
        id=new_id(),
        created_at=datetime.now(UTC),
        problem_id=problem_id,
        score=correction.score(median(draws)),
        deviation=correction.deviation,
        source=RatingSource.JUDGE,
        correction_id=correction.id,
        draw_ids=[one.id for one in draws],
    )


def spearman(xs: Sequence[float], ys: Sequence[float]) -> float:
    return statistics.correlation(xs, ys, method="ranked")
