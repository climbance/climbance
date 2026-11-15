from climb.log.table import predictions
from climb.schema import Prediction
from climb.storage import Database, Log


class PredictionLog(Log[Prediction]):
    def __init__(self, root: Database) -> None:
        super().__init__(root, predictions, Prediction)

    def for_user(self, user_id: str) -> list[Prediction]:
        return self.where(predictions.c.user_id == user_id)
