from climb.log.table import fills
from climb.schema import Fill
from climb.storage import Database, Log


class FillLog(Log[Fill]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, fills, Fill)

    def for_user(self, user_id: str) -> list[Fill]:
        return self.where(fills.c.user_id == user_id)
