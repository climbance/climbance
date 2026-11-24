from datetime import datetime

from sqlalchemy import func, insert, select

from climb.calls.table import calls
from climb.schema import Call
from climb.storage import Database


class CallLog:
    """What was asked of a model and what returned. No index by hash: several
    calls can share one prompt."""

    def __init__(self, root: Database) -> None:
        self.root = root
        # what this instance appended, so a caller reads its own tail without
        # loading the log
        self.appended: list[Call] = []

    def append(self, record: Call) -> None:
        with self.root.begin() as conn:
            conn.execute(insert(calls).values(record.model_dump()))
        self.appended.append(record)

    def all(self) -> list[Call]:
        with self.root.connect() as conn:
            rows = conn.execute(select(calls).order_by(calls.c.appended)).mappings()
            return [Call.model_validate(dict(row)) for row in rows]

    def made_by(self, user_id: str, since: datetime) -> int:
        with self.root.connect() as conn:
            return conn.execute(
                select(func.count())
                .select_from(calls)
                .where(calls.c.user_id == user_id, calls.c.created_at >= since)
            ).scalar_one()
