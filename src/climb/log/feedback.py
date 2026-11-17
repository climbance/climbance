from datetime import datetime

from climb.log.table import feedback
from climb.schema import Feedback
from climb.storage import Database, Log


class FeedbackLog(Log[Feedback]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, feedback, Feedback)

    def for_user(self, user_id: str, *, since: datetime | None = None) -> list[Feedback]:
        conditions = [feedback.c.user_id == user_id]
        if since is not None:
            conditions.append(feedback.c.created_at >= since)
        return self.where(*conditions)
