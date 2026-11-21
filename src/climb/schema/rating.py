"""A judgement of a problem's contest-scale score, as `cli/difficulty/README.md`
gives."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from climb.schema.problem import ProblemDifficulty


class RatingSource(StrEnum):
    USER = "user"
    JUDGE = "judge"  # the corrected median of the judge's draws, named by `correction_id`


# Each label's lowest score, easy first; `cli/difficulty/README.md` gives how
# each cut was set
BANDS: tuple[tuple[float, ProblemDifficulty], ...] = (
    (float("-inf"), ProblemDifficulty.EASY),
    (1100.0, ProblemDifficulty.MEDIUM),
    (1900.0, ProblemDifficulty.HARD),
)


def band(score: float) -> ProblemDifficulty:
    return next(label for low, label in reversed(BANDS) if score >= low)


class DifficultyRating(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    problem_id: str = Field(min_length=1)
    score: float
    deviation: float | None = Field(default=None, gt=0)
    source: RatingSource
    correction_id: str | None = Field(default=None, min_length=1)
    draw_ids: list[str] = []  # the draws the median read, stored in `difficulty_rating_draws`

    @property
    def label(self) -> ProblemDifficulty:
        return band(self.score)

    @model_validator(mode="after")
    def _a_judge_names_its_correction(self) -> DifficultyRating:
        """A judge's rating names its correction, its deviation and its draws;
        a user's names none, its deviation being deferred."""
        judged = self.source is RatingSource.JUDGE
        named = (self.correction_id is not None, self.deviation is not None, bool(self.draw_ids))
        if any(one != judged for one in named):
            raise ValueError(
                f"a {self.source} rating names correction_id, deviation and draw_ids"
                " iff it is the judge's"
            )
        return self
