"""A user's remark on the engine, read by the author: `api/feedback.md`."""

from datetime import datetime

from climb.caps import capped
from climb.ids import new_id
from climb.log import FeedbackLog
from climb.schema import Client, Feedback


def sent(
    log: FeedbackLog, *, user_id: str, client: Client, page: str, note: str, now: datetime
) -> Feedback:
    capped(lambda since: len(log.for_user(user_id, since=since)), now, "notes of feedback")
    one = Feedback(
        id=new_id(), created_at=now, user_id=user_id, client=client, page=page, note=note
    )
    log.append(one)
    return one
