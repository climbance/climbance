from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RunKind(StrEnum):
    SUBMISSION = "submission"
    RECALL = "recall"


class RunFault(BaseModel):
    """A user's run the sandbox answered no result for: `log.md`, Run faults."""

    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    user_id: str = Field(min_length=1)
    kind: RunKind
    # the runner's own message, for the author
    detail: str = Field(max_length=2000)


__all__ = ["RunFault", "RunKind"]
