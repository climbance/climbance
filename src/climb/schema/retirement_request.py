from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from climb.schema.authored import Text
from climb.schema.problem import RetirementReason


class RetirementRequest(BaseModel):
    """One user's request that a problem be retired: `log.md`, Retirement
    requests."""

    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    user_id: str = Field(min_length=1)
    problem_id: str = Field(min_length=1)
    reason: RetirementReason
    # what the user found wrong, in their own words
    note: Text = Field(max_length=2000)


__all__ = ["RetirementRequest"]
