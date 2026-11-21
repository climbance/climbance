"""The difficulty judge's draws and corrections: `cli/difficulty/judge.md`."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from climb.schema.provenance import MachineProvenance


class DifficultyDraw(MachineProvenance):
    id: str
    created_at: datetime
    problem_id: str = Field(min_length=1)
    judged: int  # the contest rating the call answered, uncorrected

    @model_validator(mode="after")
    def _a_draw_names_its_call(self) -> DifficultyDraw:
        self.check_provenance(True)
        return self


class DifficultyCorrection(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    anchor_set: str = Field(min_length=1)  # the hash of the anchor list, never an anchor's name
    model: str = Field(min_length=1)
    effort: str = Field(min_length=1)
    pin: str
    temperature: float | None = None  # absent is the provider's default: the judge is sampled
    instructions_hash: str = Field(min_length=1)
    draws: int = Field(ge=1)  # per statement, the median's count
    intercept: float
    slope: float = Field(gt=0)
    anchors_fitted: int = Field(ge=2)
    anchors_held_out: int = Field(ge=2)
    held_out_spearman: float = Field(ge=-1, le=1)
    held_out_mean_error: float = Field(ge=0)
    deviation: float = Field(gt=0)

    def score(self, judged: float) -> float:
        return self.intercept + self.slope * judged
