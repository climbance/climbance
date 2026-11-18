"""One difficulty fit over the panel's trials: `cli/difficulty/fits.md`."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FitMember(BaseModel):
    model_config = ConfigDict(frozen=True)

    model: str = Field(min_length=1)
    effort: str = Field(min_length=1)
    pin: str = Field(min_length=1)
    ability: float  # on the fit's own logit scale
    trials: int = Field(ge=0)  # the member's trials the fit read


class DifficultyFit(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    anchor_set: str = Field(min_length=1)  # the hash of the anchor list, never an anchor's name
    slope: float = Field(gt=0)  # contest points per logit, set on the fit anchors
    intercept: float
    anchors_fitted: int = Field(ge=2)
    anchors_held_out: int = Field(ge=1)
    problems: int = Field(ge=0)  # corpus problems scored
    held_out_log_loss: float = Field(ge=0)
    baseline_log_loss: float = Field(ge=0)  # each member's solve rate, as a constant
    members: list[FitMember] = Field(min_length=2)
