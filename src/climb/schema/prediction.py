"""What a pick predicted, stored as the user takes it: `api/predictions.md`."""

from datetime import datetime
from enum import IntEnum, StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Rank(IntEnum):
    """The order the pick offers in: `flows.md`, The pick."""

    OWED_CHECK = 1
    OPEN_CHECK = 2
    DUE_REVIEW = 3
    RUNG = 4
    NEW_CARD = 5


class Act(StrEnum):
    RECALL = "recall"
    SITTING = "sitting"
    START = "start"


class Arm(StrEnum):
    """Which policy chose the pick, were a comparison to assign one."""

    SCHEDULER = "scheduler"
    BASELINE = "baseline"


class Prediction(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime  # when the user took the pick, before any outcome
    user_id: str = Field(min_length=1)
    rank: Rank
    act: Act
    card_id: str = Field(min_length=1)
    template_id: str | None = None  # absent on a rung, a probe and a new card
    problem_id: str | None = None  # a sitting's alone
    probe: bool = False
    # FSRS's chance the template's form is recalled, absent with no template
    recall_probability: float | None = Field(default=None, ge=0, le=1)
    fsrs_settings: str = Field(min_length=1)  # the hash of the settings it read
    # the technique's execution reading, absent while it reads unknown
    execution: float | None = Field(default=None, ge=0, le=1)
    execution_settings: str = Field(min_length=1)
    arm: Arm | None = None  # absent while no comparison assigns arms

    @model_validator(mode="after")
    def _the_act_names_its_subject(self) -> Prediction:
        if self.act is Act.RECALL and self.template_id is None:
            raise ValueError("a recall names its template")
        if self.act is Act.SITTING and self.problem_id is None:
            raise ValueError("a sitting names its problem")
        if self.act is Act.START and (self.template_id or self.problem_id):
            raise ValueError("a new card names neither a template nor a problem")
        return self


__all__ = ["Act", "Arm", "Prediction", "Rank"]
