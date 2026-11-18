"""A judgement of a problem's contest-scale score, as `cli/difficulty/README.md`
gives."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from climb.schema.problem import ProblemDifficulty


class RatingSource(StrEnum):
    USER = "user"
    FIT = "fit"  # a difficulty fit over the panel's trials, named by `fit_id`


# Each label's lowest score, easy first. Provisional: the first fit sets the
# cuts against the criteria's labels, as `cli/difficulty/README.md` gives
BANDS: tuple[tuple[float, ProblemDifficulty], ...] = (
    (float("-inf"), ProblemDifficulty.EASY),
    (1300.0, ProblemDifficulty.MEDIUM),
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
    fit_id: str | None = Field(default=None, min_length=1)

    @property
    def label(self) -> ProblemDifficulty:
        return band(self.score)

    @model_validator(mode="after")
    def _a_fit_names_itself(self) -> DifficultyRating:
        """A fit's rating names the fit and its deviation; a user's names
        neither, its deviation being deferred."""
        fitted = self.source is RatingSource.FIT
        if fitted != (self.fit_id is not None) or fitted != (self.deviation is not None):
            raise ValueError(f"a {self.source} rating names fit_id and deviation iff it is a fit")
        return self
