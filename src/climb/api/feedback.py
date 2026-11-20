"""The routes a client reports to the author through: an error it met, and
the user's feedback."""

import json
import logging
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from climb.api.context import Root, UserId
from climb.caps import TooOften
from climb.feedback import sent
from climb.log import FeedbackLog
from climb.schema import Client, Feedback
from climb.schema.authored import Text

LOGGER = logging.getLogger(__name__)

router = APIRouter()

ERRORS_PER_MINUTE = 10

# per worker: a report is no record, so nothing stored counts a burst
_reported: dict[str, deque[datetime]] = defaultdict(deque)


class Sending(BaseModel):
    client: Client
    page: str = Field(min_length=1, max_length=200)
    note: Text = Field(max_length=2000)


@router.post("/feedback", status_code=201)
def feedback_sent(root: Root, user_id: UserId, body: Sending) -> Feedback:
    return sent(
        FeedbackLog(root),
        user_id=user_id,
        client=body.client,
        page=body.page,
        note=body.note,
        now=datetime.now(UTC),
    )


class ErrorReport(BaseModel):
    """An error a client met and did not handle. It carries no code the user
    typed."""

    client: Client
    version: str = Field(min_length=1, max_length=50)
    page: str = Field(min_length=1, max_length=200)
    message: str = Field(max_length=2000)
    stack: str | None = Field(default=None, max_length=8000)


@router.post("/errors", status_code=204)
def error_reported(user_id: UserId, body: ErrorReport) -> Response:
    """One line in the API's log, which the host keeps 14 days:
    `api/README.md`."""
    at = datetime.now(UTC)
    times = _reported[user_id]
    while times and at - times[0] > timedelta(minutes=1):
        times.popleft()
    if len(times) >= ERRORS_PER_MINUTE:
        raise TooOften(f"{ERRORS_PER_MINUTE} error reports a minute is the cap")
    times.append(at)
    LOGGER.warning("client error: %s", json.dumps({"user_id": user_id, **body.model_dump()}))
    return Response(status_code=204)
