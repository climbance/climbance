from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from climb.schema.authored import Text


class Client(StrEnum):
    WEB = "web"
    NATIVE = "native"


class Feedback(BaseModel):
    """One user's feedback on the engine: `api/feedback.md`."""

    model_config = ConfigDict(frozen=True)

    id: str
    created_at: datetime
    user_id: str = Field(min_length=1)
    client: Client
    # the path of the page it was sent from, which differs between the clients
    page: str = Field(min_length=1, max_length=200)
    note: Text = Field(max_length=2000)


__all__ = ["Client", "Feedback"]
